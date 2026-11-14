"""A1 ability state — evidence families.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md``.

    F1 income        stable 2 / weak 0 (evidence) / none
    F2 money in/held strong 2 / some 0 (evidence) / none   (inflow, or a CASA balance)
    F3 money out     strong 2 / some 0 (evidence) / none
    F4 cross-product strong 2 / some 0 (evidence) / none
    = points         4+ high (two strong families), 2 moderate, else low
  distress (cheque / DDS return, new bureau bounce) lowers the state one rung;
  no evidence in any family and no counted CASA leg in the window → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (family rule §2; income: spec S2–S12): starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
MIN_MONTHS = {3: 2, 6: 3}  # months of the window a flow / balance must reach its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
# Income, money in, money out, the balance and assets are strong from one amount:
# max(floor, mult x anchor) (S2; one threshold for every family, user 2026-11-14).
STRONG_FLOOR = 3000.0  # AED
STRONG_ANCHOR_MULT = 2.0
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
FLOW_SOME = 1000.0  # F2 / F3 some: any month with this much money in / out
BALANCE_MAX_FALL = 0.50  # F2 balance strong: at most this share below the prior window
INSTALMENT_FLOOR = 1000.0  # F4 strong: a current credit product's instalment reaches
INSTALMENT_ANCHOR_MULT = 1.0  # max(floor, mult x anchor)
MIN_EVIDENCE_AMT = 1000.0  # smallest salary that counts as evidence (income weak)
INCOME_POINTS = {"stable": 2}  # weak is evidence (Low), not points
FAMILY_POINTS = {"strong": 2}  # some is evidence (Low), not points
HIGH_FROM, MODERATE_FROM = 4, 2  # two strong families / one

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
    """The ``{prefix}_m{i}`` columns of month indices ``months``."""
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    """The number of ``cols`` reaching ``floor`` (NULL counts as 0)."""
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


def _strong_amount(anchor: Column) -> Column:
    """The amount a family is strong from: max(``STRONG_FLOOR``, ``STRONG_ANCHOR_MULT``
    x anchor); the floor alone without an anchor."""
    return F.greatest(F.lit(STRONG_FLOOR), STRONG_ANCHOR_MULT * anchor)


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    floor = _strong_amount(anchor)
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


def _strong_months(prefix: str, floor: Column, w: int) -> Column:
    """At least ``MIN_MONTHS[w]`` months of the window reach ``floor``."""
    return _count_at_least(_months(prefix, _window(w)[0]), floor) >= MIN_MONTHS[w]


def balance_strong(anchor: Column, w: int) -> Column:
    """The CASA balance holds the strong amount in ``MIN_MONTHS`` months of the window
    and is not more than ``BALANCE_MAX_FALL`` below the prior window (money held)."""
    return _strong_months("casa", _strong_amount(anchor), w) & _not_weakening(
        "casa", BALANCE_MAX_FALL, missing_is_zero=False, w=w
    )


def _flow_level(prefix: str, anchor: Column, w: int) -> Column:
    """strong / some / none / NULL (no flow in the window) of a monthly flow."""
    last = _months(prefix, _window(w)[0])
    has_data = F.greatest(*[c.isNotNull() for c in last])
    return (
        F.when(_strong_months(prefix, _strong_amount(anchor), w), "strong")
        .when(_count_at_least(last, F.lit(FLOW_SOME)) > 0, "some")
        .when(has_data, "none")
    )


def money_in_level(anchor: Column, w: int) -> Column:
    """F2: strong when money in or the balance held is strong; some on money in only (a
    balance below strong is not evidence)."""
    inflow = _flow_level("in", anchor, w)
    return F.when(balance_strong(anchor, w), "strong").otherwise(inflow)


def money_out_level(anchor: Column, w: int) -> Column:
    """F3: chosen spend and transfers to the customer's own accounts elsewhere."""
    return _flow_level("out", anchor, w)


def cross_product_level(anchor: Column, _w: int) -> Column:
    """F4 at the observation month end: strong on assets of the strong amount or a
    current credit product whose instalment reaches max(floor, anchor); some on any
    other current credit product or any asset."""
    assets = F.coalesce(F.col("xp_assets_aed"), F.lit(0.0))
    instalment = F.coalesce(F.col("xp_instalment_max"), F.lit(0.0))
    strong = (assets >= _strong_amount(anchor)) | (
        (F.col("xp_current") == 1)
        & (
            instalment
            >= F.greatest(F.lit(INSTALMENT_FLOOR), INSTALMENT_ANCHOR_MULT * anchor)
        )
    )
    some = (F.col("xp_current") == 1) | (F.col("xp_holding") == 1)
    return F.when(strong, "strong").when(some, "some").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (money_in_level, Dimension("money_in", "a1_money_in_level", FAMILY_POINTS)),
    (money_out_level, Dimension("money_out", "a1_money_out_level", FAMILY_POINTS)),
    (
        cross_product_level,
        Dimension("cross_product", "a1_cross_product_level", FAMILY_POINTS),
    ),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={state: state for state in DISPLAY_NAMES},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def _income_source() -> Column:
    """Who shows ``MIN_EVIDENCE_AMT`` or more in the window: both, internal, bureau or
    none."""
    internal = _shows_evidence("internal_salary_w")
    bureau = _shows_evidence("bureau_salary_w")
    return (
        F.when(internal & bureau, "both")
        .when(internal, "internal")
        .when(bureau, "bureau")
        .otherwise("none")
    )


def _salary_stopped() -> Column:
    """Internal salary in the prior window and none in the window."""
    return _shows_evidence("internal_salary_prior") & ~_shows_evidence(
        "internal_salary_w"
    )


def build_a1_ability(
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Families and points: family rule §2–§4; distress lowers the state one rung (S9).

    ``signals`` (income, CASA, cross-product, distress, EOSB: ``GRAIN`` + columns) and
    ``anchor`` (``GRAIN + liquidity_anchor_amt``, from the product wrapper) are
    left-joined in that order. ``a1_unknown_reason`` says why a row is unknown:
    ``no_casa`` (no CASA leg or positive balance with us in 12 months) or
    ``dormant_casa``; ``a1_reason`` is the strongest family (or ``distress``).
    Diagnostics, which change nothing: ``a1_sweepable_balance_flag`` (the CASA balance
    is strong: money above the floor the bank could still sweep), ``a1_eosb_flag`` (a
    DCORE end-of-service result in the window), ``a1_income_source`` (who shows AED
    1,000 or more in the window: ``internal``, ``bureau``, ``both`` or ``none``),
    ``a1_salary_stopped`` (internal salary in the prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
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
        "a1_reason",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        balance_strong(amt, w).cast("int").alias("a1_sweepable_balance_flag"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        _income_source().alias("a1_income_source"),
        _salary_stopped().cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
