"""TEMPORARY (mirror bundle 03): old vs new CC A1 states, run in PROD.

``compare_a1_outputs`` logs the ``B03 OUTPUT`` block (aggregates only): the bundle 02
engine output (``crx_cc_a1_ability_b01_check``, billing-date observations) against the
new month-end output (``crx_cc_a1_ability_b03_check``). An old row is matched to the new
row of the same account and month (the month's latest old observation).

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

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
    LOG.info(
        "\n%s",
        "\n".join(["=== B03 OUTPUT START ===", *lines, "=== B03 OUTPUT END ==="]),
    )
    both.unpersist()
