"""TEMPORARY (mirror bundle 13): RL A4 on ``has_restructured_loan_flag``, old vs new, in PROD.

The old output (``crx_rl_a4_deterioration``) is bundle 11's, which read ``is_restructured``.
Log blocks, aggregates only, latest observation month:

* ``B13 OUTPUT``: states old × new, and new states by ``loan_type``.
* ``B13 RESTRUCTURE``: the feature flag by ``loan_type``, stitched and still blind, old vs
  new blind spot, states of the blind rows, stitched accounts the flag does not mark.
* ``B13 UNKNOWN``: what is left in Unknown, by route and ``loan_type``.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_KEY = ["account_id", "observation_date"]


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B13 {name} START === [{model_id}]",
        *lines,
        f"=== B13 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<28}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _keyed(df: DataFrame, *cols: str) -> DataFrame:
    return df.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        *cols,
    )


def compare_rl_a4_outputs(
    old: DataFrame,
    new: DataFrame,
    feature_retail_loans: DataFrame,
    rl_spine: DataFrame,
    model_id: str,
) -> None:
    """Log the B13 blocks; the baseline is bundle 11's output (step 8 done)."""
    products = _keyed(rl_spine, "loan_type").dropDuplicates(_KEY)
    flags = _keyed(
        feature_retail_loans,
        F.col("has_restructured_loan_flag").cast("int").alias("feature_flag"),
    ).dropDuplicates(_KEY)
    frame = (
        _keyed(
            new,
            "det_state",
            "history_cropped",
            "n_months_truncated",
            F.col("restructure_blind_spot_flag").alias("blind"),
            F.col("chain_stitched_flag").alias("stitched"),
        )
        .join(
            _keyed(
                old,
                F.col("det_state").alias("old_state"),
                F.col("restructure_blind_spot_flag").alias("old_blind"),
            ),
            on=_KEY,
            how="left",
        )
        .join(products, on=_KEY, how="left")
        .join(flags, on=_KEY, how="left")
    )
    latest = _latest_month(frame).cache()

    _log(
        "OUTPUT",
        model_id,
        [
            f"accounts {latest.count()}",
            "old x new",
            *_table(latest, "old_state", "det_state"),
            "loan_type x new",
            *_table(latest, "loan_type", "det_state"),
        ],
    )

    restructured = latest.filter(F.col("feature_flag") == 1)
    blind = latest.filter(F.col("blind") == 1)
    unflagged = latest.filter(
        (F.col("stitched") == 1) & ~F.coalesce(F.col("feature_flag") == 1, F.lit(False))
    )
    _log(
        "RESTRUCTURE",
        model_id,
        [
            f"flag set {restructured.count()}",
            "loan_type x stitched x blind (flag set)",
            *_table(restructured, "loan_type", "stitched", "blind"),
            "old_blind x blind",
            *_table(latest, "old_blind", "blind"),
            "blind: old x new",
            *_table(blind, "old_state", "det_state"),
            f"stitched without the flag: {unflagged.count()}",
        ],
    )

    unknown = latest.filter(F.col("det_state") == "unknown").withColumn(
        "route",
        F.when(F.col("blind") == 1, "restructured")
        .when(F.col("n_months_truncated") > 0, "cropped_gap")
        .when(F.col("history_cropped"), "cropped_source_start")
        .otherwise("other"),
    )
    _log(
        "UNKNOWN",
        model_id,
        [
            f"unknown {unknown.count()}",
            "route x loan_type",
            *_table(unknown, "route", "loan_type"),
        ],
    )
    latest.unpersist()
