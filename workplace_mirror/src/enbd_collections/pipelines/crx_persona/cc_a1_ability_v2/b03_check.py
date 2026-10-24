"""TEMPORARY (mirror bundle 03): old vs new CC A1 states, run in PROD.

Two log blocks, aggregates only:

* ``compare_a1_outputs`` (``B03 OUTPUT``): the bundle 02 engine output
  (``crx_cc_a1_ability_b01_check``, billing-date observations) against the new month-end
  output (``crx_cc_a1_ability_b03_check``). An old row is matched to the new row of the
  same account and month (the month's latest old observation).
* ``compare_income_rules`` (``B03 INCOME``): what the 2 × anchor income bar and the
  income-weakening check do, against a flat AED 3,000 floor and no weakening check.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import window_months
from ..a1_ability.classify import (
    _LADDER,
    D_INC,
    DEMIN,
    F_INC,
    K_INC,
    MIN_MONTHS,
    _count_at_least,
    _months,
    _not_weakening,
    _window,
)
from ..scoring_engine import points_from_level

LOG = logging.getLogger(__name__)


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state crosstab, new levels and the latest month's state distribution."""
    latest_in_month = Window.partitionBy("account_id", "month").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.withColumn("month", F.trunc("observation_date", "month"))
        .withColumn("_rn", F.row_number().over(latest_in_month))
        .filter(F.col("_rn") == 1)
        .select("account_id", "month", F.col("a1_state").alias("old_state"))
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
        )
        .join(old_m, ["account_id", "month"], "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    last = new.agg(F.max("observation_date")).first()[0]
    latest = new.filter(F.col("observation_date") == F.lit(last))
    lines = [
        f"model_id={model_id} rows={n} changed={changed} "
        f"({100.0 * changed / max(n, 1):.2f}%)",
        f"  distress flag: {_counts(both, 'a1_distress_flag')}",
        f"  latest month {last}: {_counts(latest, 'a1_state')}",
        "  income level x liquidity level:",
        *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
        "  old state x new state:",
        *_crosstab(both, "old_state", "new_state"),
    ]
    _log("OUTPUT", lines)
    both.unpersist()


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B03 {name} START ===", *lines, f"=== B03 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def _income_level(floor: Column, weakening: bool, w: int) -> Column:
    """classify.income_level with the threshold and the weakening check as inputs."""
    last = _months("income", _window(w)[0])
    stable = _count_at_least(last, floor) >= MIN_MONTHS[w]
    if weakening:
        stable = stable & _not_weakening("income", D_INC, True, w)
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _state(income_level: str) -> Column:
    """The A1 state with ``income_level`` in place of the engine's income level (the
    unknown gate only holds while the points stay 0)."""
    points = points_from_level(
        F.col(income_level), {"stable": 2, "weak": 1}
    ) + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    unknown = (F.col("a1_state") == _LADDER.unknown) & (points == 0)
    return _LADDER.state(points, F.col("a1_distress_flag") == 1, unknown)


def compare_income_rules(income: DataFrame, a1: DataFrame, model_id: str) -> None:
    """How often 2 × anchor raises the income bar above the flat floor, how often the
    weakening check fires, and the levels and states without each of them."""
    w = window_months(model_id)
    last = _window(w)[0]
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    bar = F.greatest(F.lit(F_INC), K_INC * anchor)
    flat = F.lit(F_INC)
    df = (
        a1.join(income, ["account_id", "observation_date"])
        .withColumn("bar", bar)
        .withColumn("raised", bar > flat)
        .withColumn("lvl_engine", _income_level(bar, True, w))
        .withColumn("lvl_flat", _income_level(flat, True, w))
        .withColumn("lvl_no_weak", _income_level(bar, False, w))
        .withColumn("lvl_flat_no_weak", _income_level(flat, False, w))
        .withColumn(
            "qual_bar", _count_at_least(_months("income", last), bar) >= MIN_MONTHS[w]
        )
        .withColumn(
            "qual_flat", _count_at_least(_months("income", last), flat) >= MIN_MONTHS[w]
        )
        .withColumn("weak_ok", _not_weakening("income", D_INC, True, w))
        .withColumn("st_flat", _state("lvl_flat"))
        .withColumn("st_no_weak", _state("lvl_no_weak"))
        .withColumn("st_flat_no_weak", _state("lvl_flat_no_weak"))
        .cache()
    )
    n = df.count()
    raised = (
        df.filter("raised")
        .agg(
            F.count("*").alias("n"),
            F.expr("percentile_approx(bar, array(0.5, 0.9, 0.99))").alias("q"),
        )
        .first()
    )
    mismatch = df.filter(F.col("lvl_engine") != F.col("a1_income_level")).count()
    lines = [
        f"model_id={model_id} rows={n} engine-level mismatches={mismatch} (must be 0)",
        f"  bar raised above {F_INC:.0f}: {raised['n']} ({100.0 * raised['n'] / max(n, 1):.2f}%)"
        f"  bar p50/p90/p99 where raised: {raised['q']}",
        f"  {MIN_MONTHS[w]} of {w} months reach the bar: {df.filter('qual_bar').count()}"
        f"  reach the flat floor: {df.filter('qual_flat').count()}",
        f"  {MIN_MONTHS[w]} of {w} reach the bar but weakening fails: "
        f"{df.filter(F.col('qual_bar') & ~F.col('weak_ok')).count()}"
        f"  (flat floor: {df.filter(F.col('qual_flat') & ~F.col('weak_ok')).count()})",
    ]
    for name, lvl, st in [
        ("flat floor", "lvl_flat", "st_flat"),
        ("no weakening check", "lvl_no_weak", "st_no_weak"),
        ("flat floor + no weakening check", "lvl_flat_no_weak", "st_flat_no_weak"),
    ]:
        lines += [
            f"  -- {name}: income level engine x variant",
            *_crosstab(df, "a1_income_level", lvl),
            f"  -- {name}: state engine x variant",
            *_crosstab(df, "a1_state", st),
        ]
    _log("INCOME", lines)
    df.unpersist()
