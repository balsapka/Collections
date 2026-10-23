"""TEMPORARY (mirror bundle 01): checks for the CC A1 rebuild, run in PROD.

The last nodes of the ``crx_cc_a1_ability_b01_check`` pipeline (aggregates only):

* ``compare_a1_outputs`` — the untouched ``crx_cc_a1_ability_v2`` against the new
  ``crx_cc_a1_ability_b01_check``, plus income × liquidity levels; ``B01 OUTPUT`` block;
* ``compare_salary_months`` — salary months recovered from the WM snapshots against
  ``feat_payroll_indicator`` in the same month and one month either side; ``B01 SALARY``;
* ``compare_distress_sources`` — bureau vs internal returns, and each internal
  ``reason_for_excluding`` value; ``B01 DISTRESS`` block.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_GRAIN = ["account_id", "observation_date"]


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B01 {name} START ===", *lines, f"=== B01 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def _in_last_3_months(date_col: str) -> Column:
    k = F.months_between(
        F.trunc("observation_date", "month"), F.trunc(F.col(date_col), "month")
    )
    return k.between(1, 3)


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state, level distributions and crosstab, anchor coverage."""
    both = (
        new.select(
            *_GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
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
    _log(
        "OUTPUT",
        [
            f"model_id={model_id} rows={n} changed={changed} "
            f"({100.0 * changed / max(n, 1):.2f}%)",
            f"  distress flag: {_counts(both, 'a1_distress_flag')}",
            f"  anchor present: {anchor['share'] or 0.0:.4f}  p10/p50/p90: {anchor['q']}",
            "  income level x liquidity level:",
            *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
            "  old state x new state:",
            *_crosstab(both, "old_state", "new_state"),
        ],
    )
    both.unpersist()


def compare_salary_months(
    obs_base: DataFrame, income: DataFrame, payroll: DataFrame
) -> None:
    """Recovered salary months (income_m1..m3 > 0) against payroll_flag in the same
    month, the month before and the month after."""
    month = lambda k: F.trunc(F.add_months("observation_date", -k), "month")  # noqa: E731
    credits = (
        income.join(obs_base.select(*_GRAIN, "cif_id"), _GRAIN)
        .filter(F.col("cif_id").isNotNull())
        .select(
            "cif_id",
            F.explode(
                F.array(
                    *[
                        F.struct(
                            month(k).alias("month"),
                            F.col(f"income_m{k}").alias("amount"),
                        )
                        for k in (1, 2, 3)
                    ]
                )
            ).alias("m"),
        )
        .select(
            "cif_id",
            "m.month",
            "m.amount",
            (F.coalesce(F.col("m.amount"), F.lit(0.0)) > 0).alias("recovered"),
        )
    )
    flags = (
        payroll.select(
            "cif_id",
            F.trunc(
                F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"), "month"
            ).alias("pmonth"),
            (F.col("payroll_flag") == 1).cast("int").alias("payroll"),
        )
        .groupBy("cif_id", "pmonth")
        .agg(F.max("payroll").alias("payroll"))
    )
    # payroll_prev: flag in the month before the credit month; payroll_next: the month after
    for shift, name in ((-1, "prev"), (0, "same"), (1, "next")):
        f = flags.select(
            "cif_id",
            F.add_months("pmonth", -shift).alias("month"),
            F.col("payroll").alias(f"payroll_{name}"),
        )
        credits = credits.join(f, ["cif_id", "month"], "left")
    credits = credits.fillna(
        0, ["payroll_prev", "payroll_same", "payroll_next"]
    ).cache()
    amounts = (
        credits.filter("recovered")
        .groupBy("payroll_same")
        .agg(
            F.expr("percentile_approx(amount, array(0.1, 0.5, 0.9))").alias("q"),
            F.avg((F.col("amount") >= 3000).cast("double")).alias("ge3000"),
        )
        .orderBy("payroll_same")
        .collect()
    )
    lines = []
    for name in ("same", "prev", "next"):
        lines += [f"  recovered x payroll flag ({name} month):"]
        lines += _crosstab(credits, "recovered", f"payroll_{name}")
    lines += ["  recovered credit amount by payroll flag (same month):"]
    lines += [
        f"  payroll={r['payroll_same']} p10/p50/p90={r['q']} "
        f"share>=3000={r['ge3000']:.3f}"
        for r in amounts
    ]
    _log("SALARY", lines)
    credits.unpersist()


def compare_distress_sources(
    obs_base: DataFrame, bureau_alert: DataFrame, internal_returns: DataFrame
) -> None:
    """Rows flagged by bureau bounces vs internal returns (last 3 complete months), and
    events / rows flagged per internal reason."""
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*_GRAIN, "cif_id")
    bureau = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    internal = (
        obs.join(internal_returns, "cif_id")
        .filter(_in_last_3_months("event_date"))
        .cache()
    )
    hit = lambda df, name: (  # noqa: E731
        df.select(*_GRAIN).distinct().withColumn(name, F.lit(1))
    )
    flags = (
        obs.join(
            hit(
                obs.join(bureau, "cif_id").filter(_in_last_3_months("event_date")),
                "bureau",
            ),
            _GRAIN,
            "left",
        )
        .join(hit(internal, "internal"), _GRAIN, "left")
        .fillna(0, ["bureau", "internal"])
    )
    per_reason = (
        internal.groupBy("reason")
        .agg(
            F.count(F.lit(1)).alias("events"),
            F.countDistinct(*_GRAIN).alias("rows"),
        )
        .orderBy("reason")
        .collect()
    )
    lines = [f"  rows with a CIF: {obs.count()}", "  bureau x internal:"]
    lines += _crosstab(flags, "bureau", "internal")
    lines += ["  internal reason: events in window / rows flagged"]
    lines += [
        f"  {r['reason']:<24} {r['events']:>9} {r['rows']:>9}" for r in per_reason
    ]
    _log("DISTRESS", lines)
    internal.unpersist()
