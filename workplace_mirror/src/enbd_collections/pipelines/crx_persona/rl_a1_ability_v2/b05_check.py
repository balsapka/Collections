"""TEMPORARY (mirror bundle 05): RL waterfall vs RL A1 on the engine, run in PROD.

Two log blocks, aggregates only:

* ``compare_rl_a1_outputs`` (``B05 OUTPUT``): the RL waterfall output (``crx_rl_a1_ability``)
  against the engine output (``crx_rl_a1_ability_b05_check``), over the engine output's
  months (the persona months). An old row is matched to the new row of the same account
  and month (the month's latest old observation).
* ``compare_income_sources`` (``B05 INCOME``): what the ``feature_retail_loans`` bureau
  salary adds — income levels and states with and without it.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, window_months
from ..a1_ability import build_income_signals
from ..a1_ability.classify import _LADDER, income_level
from ..a1_ability.signals import _loan_bureau_salary
from ..scoring_engine import points_from_level

LOG = logging.getLogger(__name__)


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B05 {name} START ===", *lines, f"=== B05 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def compare_rl_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state crosstab, new levels, the anchor's coverage and the latest
    month's state distribution."""
    first, last = new.agg(F.min("observation_date"), F.max("observation_date")).first()
    latest_in_month = Window.partitionBy("account_id", "month").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.withColumn("month", F.trunc("observation_date", "month"))
        .filter(F.col("month").between(F.trunc(F.lit(first), "month"), F.lit(last)))
        .withColumn("_rn", F.row_number().over(latest_in_month))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string").alias("account_id"),
            "month",
            # waterfall names: ability_high … ability_unknown
            F.regexp_replace("a1_state", "^ability_", "").alias("old_state"),
        )
    )
    both = (
        new.withColumn("month", F.trunc("observation_date", "month"))
        .select(
            "account_id",
            "month",
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
            F.col("liquidity_anchor_amt").isNotNull().alias("has_anchor"),
        )
        .join(old_m, ["account_id", "month"], "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    latest = new.filter(F.col("observation_date") == F.lit(last))
    anchor_q = new.agg(
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))")
    ).first()[0]
    lines = [
        (
            f"model_id={model_id} months {first}..{last} rows={n} changed={changed} "
            f"({100.0 * changed / max(n, 1):.2f}%)"
        ),
        f"  distress flag: {_counts(both, 'a1_distress_flag')}",
        f"  EMI anchor present: {_counts(both, 'has_anchor')}  p10/p50/p90: {anchor_q}",
        f"  latest month {last}: {_counts(latest, 'a1_state')}",
        "  income level x liquidity level:",
        *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
        "  old state x new state:",
        *_crosstab(both, "old_state", "new_state"),
    ]
    _log("OUTPUT", lines)
    both.unpersist()


def _state(income_col: str) -> Column:
    """The A1 state with ``income_col`` in place of the engine's income level (the
    unknown gate only holds while the points stay 0)."""
    points = points_from_level(
        F.col(income_col), {"stable": 2, "weak": 1}
    ) + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    unknown = (F.col("a1_state") == _LADDER.unknown) & (points == 0)
    return _LADDER.state(points, F.col("a1_distress_flag") == 1, unknown)


def compare_income_sources(  # pylint: disable=too-many-arguments
    *,
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
    loan_features: DataFrame,
    a1: DataFrame,
    model_id: str,
) -> None:
    """How often the loan bureau salary lands in the window, and the income levels and
    states without it."""
    w = window_months(model_id)
    without = build_income_signals(
        obs_base, wm_salary, salary_hist, bureau_cif_bridge, model_id
    )
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    df = (
        a1.join(without, list(GRAIN))
        .withColumn("lvl_without", income_level(anchor, w))
        .withColumn("st_without", _state("lvl_without"))
        .cache()
    )
    pulls = _loan_bureau_salary(obs_base, loan_features)
    in_window = (
        obs_base.select(*GRAIN, "cif_id")
        .join(pulls, "cif_id")
        .filter(
            (F.col("month") <= F.col("observation_date"))
            & (
                F.col("month")
                >= F.add_months(F.trunc("observation_date", "month"), 1 - w)
            )
        )
        .select(*GRAIN)
        .distinct()
        .count()
    )
    lines = [
        (
            f"model_id={model_id} rows={df.count()} rows with a loan bureau salary in "
            f"the {w}-month window: {in_window}"
        ),
        "  -- without feature_retail_loans: income level engine x variant",
        *_crosstab(df, "a1_income_level", "lvl_without"),
        "  -- without feature_retail_loans: state engine x variant",
        *_crosstab(df, "a1_state", "st_without"),
    ]
    _log("INCOME", lines)
    df.unpersist()
