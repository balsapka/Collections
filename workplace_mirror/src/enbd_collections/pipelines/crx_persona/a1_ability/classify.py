"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque bounce / DDS return) lowers the state one level;
  no income, no liquidity, no distress and no CASA transaction → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_distribution
from ..scoring_engine import StateLadder, points_from_level

N3 = 2  # months of the last 3 that must qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
D_INC = 0.25  # stable income may fall at most this share vs the prior 3 months
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=4,
    moderate_from_points=2,
)
_LAST3, _PRIOR3 = (1, 2, 3), (4, 5, 6)


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(prefix: str, max_drop: float, missing_is_zero: bool) -> Column:
    """The last-3-month average is not more than ``max_drop`` below the prior 3 months
    (true when there is no prior quarter to compare with)."""
    recent = _mean(_months(prefix, _LAST3), missing_is_zero)
    prior = _mean(_months(prefix, _PRIOR3), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column) -> Column:
    last3 = _months("income", _LAST3)
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last3, floor) >= N3) & _not_weakening(
        "income", D_INC, True
    )
    weak = _count_at_least(last3, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column) -> Column:
    last3 = _months("casa", _LAST3)
    payment = F.coalesce(F.col("ext_card_payment_max_3m"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last3, casa_floor) >= N3) & _not_weakening(
        "casa", D_CASA, False
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last3, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    log_stats: bool = False,
) -> DataFrame:
    """One A1 state per observation-base row.

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    df = (
        df.withColumn("a1_income_level", income_level(amt))
        .withColumn("a1_liquidity_level", liquidity_level(amt))
        .withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    )
    df = df.withColumn(
        "a1_points_total",
        points_from_level(F.col("a1_income_level"), {"stable": 2, "weak": 1})
        + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1}),
    )
    unknown = (
        (F.col("a1_points_total") == 0)
        & ~F.col("a1_distress_flag")
        & (F.coalesce(F.col("casa_active_3m"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    out = df.select(
        *GRAIN,
        "a1_state",
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.current_date().alias("computed_at"),
    )
    log_distribution(out, "a1_state", "a1_ability", log_stats)
    return out
