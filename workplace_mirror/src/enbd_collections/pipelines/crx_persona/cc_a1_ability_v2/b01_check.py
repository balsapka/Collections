"""TEMPORARY (mirror bundle 01): checks for the CC A1 rebuild, run in PROD.

The last nodes of the ``crx_cc_a1_ability_b01_check`` pipeline (aggregates only):

* ``compare_a1_outputs`` — the untouched ``crx_cc_a1_ability_v2`` against the new
  ``crx_cc_a1_ability_b01_check``; logs the ``B01 OUTPUT`` block;
* ``compare_salary_months`` — salary months recovered from the WM snapshots against
  ``feat_payroll_indicator``; logs the ``B01 SALARY`` block.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_GRAIN = ["account_id", "observation_date"]


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Log old vs new state crosstab, level distributions and anchor coverage."""
    both = (
        new.select(
            *_GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "liquidity_anchor_amt",
        )
        .join(
            old.select(*_GRAIN, F.col("a1_state_v2").alias("old_state")), _GRAIN, "full"
        )
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    anchor = both.agg(
        F.avg(F.col("liquidity_anchor_amt").isNotNull().cast("double")).alias("share"),
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))").alias(
            "q"
        ),
    ).first()
    lines = [
        "=== B01 OUTPUT START ===",
        f"model_id={model_id} rows={n} changed={changed} "
        f"({100.0 * changed / max(n, 1):.2f}%)",
        f"  income levels:    {_counts(both, 'a1_income_level')}",
        f"  liquidity levels: {_counts(both, 'a1_liquidity_level')}",
        f"  anchor present: {anchor['share'] or 0.0:.4f}  p10/p50/p90: {anchor['q']}",
    ]
    for r in (
        both.groupBy("old_state", "new_state")
        .count()
        .orderBy("old_state", "new_state")
        .collect()
    ):
        lines.append(f"  {r['old_state']:<18} -> {r['new_state']:<18} {r['count']:>9}")
    lines.append("=== B01 OUTPUT END ===")
    LOG.info("\n%s", "\n".join(lines))
    both.unpersist()


def compare_salary_months(
    obs_base: DataFrame, income: DataFrame, payroll: DataFrame
) -> None:
    """Log recovered salary months (income_m1..m3 > 0) against feat_payroll_indicator."""
    months = (
        income.join(obs_base.select(*_GRAIN, "cif_id"), _GRAIN)
        .select(
            "cif_id",
            F.explode(
                F.array(
                    *[
                        F.struct(
                            F.trunc(
                                F.add_months("observation_date", -k), "month"
                            ).alias("month"),
                            (F.coalesce(F.col(f"income_m{k}"), F.lit(0.0)) > 0).alias(
                                "recovered"
                            ),
                        )
                        for k in (1, 2, 3)
                    ]
                )
            ).alias("m"),
        )
        .select("cif_id", "m.month", "m.recovered")
        .filter(F.col("cif_id").isNotNull())
    )
    flags = (
        payroll.select(
            "cif_id",
            F.trunc(
                F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"), "month"
            ).alias("month"),
            (F.col("payroll_flag") == 1).alias("payroll"),
        )
        .groupBy("cif_id", "month")
        .agg(F.max("payroll").alias("payroll"))
    )
    rows = (
        months.join(flags, ["cif_id", "month"], "left")
        .fillna({"payroll": False})
        .groupBy("recovered", "payroll")
        .count()
        .orderBy("recovered", "payroll")
        .collect()
    )
    lines = ["=== B01 SALARY START ===", "  recovered  payroll_flag      count"]
    lines += [
        f"  {r['recovered']!s:<10} {r['payroll']!s:<13} {r['count']:>9}" for r in rows
    ]
    lines.append("=== B01 SALARY END ===")
    LOG.info("\n%s", "\n".join(lines))
