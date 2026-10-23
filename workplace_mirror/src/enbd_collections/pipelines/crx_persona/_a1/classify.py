"""A1 ability state: GRR MECE points.

Blueprint: ``data/input/A1_ability_framework_1008_blueprint.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           ≥ 4 high, ≥ 2 moderate, else low
  distress (bounced cheque / returned payment order) demotes one rung;
  no evidence at all → unknown.

Liquidity is judged against ``liquidity_anchor_amt`` — the amount the customer would
need to find now (CC: oldest overdue bucket; RL: one instalment). Thresholds are the
blueprint's starting values, not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_distribution
from ..scoring_engine import StateLadder, points_from_level

_MIN_PAYROLL_MONTHS = 2  # of the last 3
_INCOME_FLOOR = 3000.0  # AED, flat (k_inc = 0)
_CASA_FLOOR = 3000.0
_PAY_FLOOR = 500.0
_EVIDENCE_MIN = 1000.0  # smallest amount that counts as any evidence
_K_CASA = 1.0  # CASA floor = max(_CASA_FLOOR, _K_CASA * anchor)
_K_PAY = 1.0
_CASA_DROP = 0.5  # recent quarter below half the prior one = weakening

_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=4,
    moderate_from_points=2,
)


def _zero(col: str) -> Column:
    return F.coalesce(F.col(col), F.lit(0))


def income_level() -> Column:
    amount = F.coalesce("salary_amt_last", "bureau_salary_amt_last")
    stable = (_zero("salary_months_h2") >= _MIN_PAYROLL_MONTHS) & (
        amount >= _INCOME_FLOOR
    )
    weak = (
        (_zero("salary_months_h2") >= 1)
        | (_zero("bureau_salary_present_6m_flag") == 1)
        | (amount >= _EVIDENCE_MIN)
    )
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level() -> Column:
    anchor = _zero("liquidity_anchor_amt")
    casa, prior = F.col("casa_recent3m_avg"), F.col("casa_prior3m_avg")
    pay_weeks, pay_amt = _zero("ext_cc_payment_cnt_h2"), _zero("ext_cc_payment_amt_h2")
    weakening = casa < prior * (
        1 - _CASA_DROP
    )  # NULL (→ not weakening) if either is missing
    adequate = (
        (casa >= F.greatest(F.lit(_CASA_FLOOR), _K_CASA * anchor))
        & ~F.coalesce(weakening, F.lit(False))
    ) | ((pay_weeks >= 1) & (pay_amt >= F.greatest(F.lit(_PAY_FLOOR), _K_PAY * anchor)))
    weak = (casa >= _EVIDENCE_MIN) | ((pay_weeks >= 1) & (pay_amt >= _EVIDENCE_MIN))
    return (
        F.when(F.coalesce(adequate, F.lit(False)), "adequate")
        .when(F.coalesce(weak, F.lit(False)), "weak")
        .otherwise("none")
    )


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
    df = (
        df.withColumn("a1_income_level", income_level())
        .withColumn("a1_liquidity_level", liquidity_level())
        .withColumn("a1_distress_flag", _zero("distress_flag") == 1)
    )
    df = df.withColumn(
        "a1_points_total",
        points_from_level(F.col("a1_income_level"), {"stable": 2, "weak": 1})
        + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1}),
    )
    casa_active = (_zero("casa_inflow_cnt_h2") > 0) | (_zero("casa_outflow_cnt_h2") > 0)
    unknown = (
        (F.col("a1_points_total") == 0) & ~F.col("a1_distress_flag") & ~casa_active
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
        F.current_date().alias("computed_at"),
    )
    log_distribution(out, "a1_state", "a1_ability", log_stats)
    return out
