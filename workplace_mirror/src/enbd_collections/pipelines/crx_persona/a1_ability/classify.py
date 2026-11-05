"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque / DDS return, new bureau bounce) lowers the state one level;
  0 points, no distress and no customer-initiated CASA movement → unknown
  (no CASA with us, or a dormant one).

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (spec §3, S2–S12): the workbook's starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
CASA_MIN_MONTHS = {3: 2, 6: 3}  # S7: months of the window the CASA must be at its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
INCOME_FLOOR = 3000.0  # S2: salary floor (internal and bureau), AED
INCOME_ANCHOR_MULT = 2.0  # S2: income must also cover this multiple of the anchor
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
CASA_FLOOR = 3000.0  # S7
CASA_ANCHOR_MULT = 1.0  # S7
CASA_MAX_FALL = 0.50  # S7
CARD_PAYMENT_FLOOR = 500.0  # S8
CARD_PAYMENT_ANCHOR_MULT = 1.0  # S8
MIN_EVIDENCE_AMT = 1000.0  # smallest amount that counts as evidence (Weak, S5-S8)
INCOME_POINTS = {"stable": 2, "weak": 1}
LIQUIDITY_POINTS = {"adequate": 2, "weak": 1}

SCORECARD = Scorecard(
    prefix="a1",
    dimensions=(
        Dimension("income", "a1_income_level", INCOME_POINTS),
        Dimension("liquidity", "a1_liquidity_level", LIQUIDITY_POINTS),
    ),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    labels={s: s for s in ("high", "moderate", "low", "unknown")},
    high_from=4,
    moderate_from=2,
)
DISPLAY_NAMES = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "unknown": "Unknown",
}


def _window(w: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Month indices of the window (m1–mW) and of the prior window (m(W+1)–m(2W))."""
    return tuple(range(1, w + 1)), tuple(range(w + 1, 2 * w + 1))


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(INCOME_FLOOR), INCOME_ANCHOR_MULT * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (spec S7, S8)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(CASA_FLOOR), CASA_ANCHOR_MULT * anchor)
    casa_ok = (
        _count_at_least(last, casa_floor) >= CASA_MIN_MONTHS[w]
    ) & _not_weakening("casa", CASA_MAX_FALL, missing_is_zero=False, w=w)
    adequate = casa_ok | (
        payment
        >= F.greatest(F.lit(CARD_PAYMENT_FLOOR), CARD_PAYMENT_ANCHOR_MULT * anchor)
    )
    weak = (_count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0) | (
        payment >= MIN_EVIDENCE_AMT
    )
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    eosb: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Points: S2–S12; the unknown gate: S11; distress lowers the state one rung (S9).

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``. Diagnostics, which change
    nothing: ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the prior
    window, none in the window).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, eosb, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    df = (
        df.withColumn("a1_income_level", income_level(amt, w))
        .withColumn("a1_liquidity_level", liquidity_level(amt, w))
        .withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    )
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0  # S11
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    internal_w = _shows_evidence("internal_salary_w")
    bureau_w = _shows_evidence("bureau_salary_w")
    internal_prior = _shows_evidence("internal_salary_prior")
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        F.when(internal_w & bureau_w, "both")
        .when(internal_w, "internal")
        .when(bureau_w, "bureau")
        .otherwise("none")
        .alias("a1_income_source"),
        (internal_prior & ~internal_w).cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
