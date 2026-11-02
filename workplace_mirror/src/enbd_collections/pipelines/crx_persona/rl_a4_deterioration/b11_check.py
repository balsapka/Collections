"""TEMPORARY (mirror bundle 11): RL A4 without the ECL gap rule, old vs new, in PROD.

The old output (``crx_rl_a4_deterioration``) still carries ``ecl_gap_blind_spot_flag``
until step 8 rewrites it. Log blocks, aggregates only, latest observation month:

* ``B11 OUTPUT``: states old × new, and new states by ``loan_type``.
* ``B11 ECL``: the accounts the rule flagged, by ``loan_type`` and whether their history
  now starts before the old table's end (2025-12), then their new states.
* ``B11 CHAIN``: restructured accounts stitched or not, by ``loan_type``; match type,
  ambiguous links, months added, old × new on the stitched rows.
* ``B11 UNKNOWN``: what is left in Unknown, by route and ``loan_type``.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_KEY = ["account_id", "observation_date"]
_SEAM = "2025-12-01"


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B11 {name} START === [{model_id}]",
        *lines,
        f"=== B11 {name} END ===",
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
    sequences: DataFrame,
    rl_spine: DataFrame,
    model_id: str,
) -> None:
    """Log the B11 blocks; the baseline must carry ``ecl_gap_blind_spot_flag``."""
    start = sequences.select(
        F.col("account_id").cast("string").alias("account_id"), "first_month"
    )
    products = _keyed(rl_spine, "loan_type").dropDuplicates(_KEY)
    frame = (
        _keyed(
            new,
            "det_state",
            "starts_delinquent",
            "history_cropped",
            "n_months_truncated",
            "restructure_blind_spot_flag",
            "history_months",
            "chain_stitched_flag",
            "chain_match_type",
            "chain_candidate_count",
            "chain_months_added",
        )
        .join(
            _keyed(
                old,
                F.col("det_state").alias("old_state"),
                F.col("ecl_gap_blind_spot_flag").alias("ecl_flag"),
            ),
            on=_KEY,
            how="left",
        )
        .join(products, on=_KEY, how="left")
        .join(start, on="account_id", how="left")
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

    flagged = latest.filter(F.col("ecl_flag") == 1).withColumn(
        "history_from",
        F.when(
            F.col("first_month") < F.lit(_SEAM).cast("date"), "before_2025_12"
        ).otherwise("2025_12_or_later"),
    )
    _log(
        "ECL",
        model_id,
        [
            f"flagged {flagged.count()}",
            "loan_type x history_from",
            *_table(flagged, "loan_type", "history_from"),
            "history_from x old x new",
            *_table(flagged, "history_from", "old_state", "det_state"),
            "history_from: history_months min / median / max",
            *[
                f"  {r['history_from']}: {r['q']}"
                for r in flagged.groupBy("history_from")
                .agg(
                    F.expr("percentile_approx(history_months, array(0, 0.5, 1))").alias(
                        "q"
                    )
                )
                .collect()
            ],
        ],
    )

    stitched = latest.filter(F.col("chain_stitched_flag") == 1)
    restructured = latest.filter(
        (F.col("chain_stitched_flag") == 1)
        | (F.col("restructure_blind_spot_flag") == 1)
    )
    months = stitched.agg(
        F.expr("percentile_approx(chain_months_added, array(0, 0.5, 1))").alias("q")
    ).first()["q"]
    _log(
        "CHAIN",
        model_id,
        [
            f"restructured {restructured.count()}, stitched {stitched.count()}",
            "loan_type x stitched x still blind",
            *_table(
                restructured,
                "loan_type",
                "chain_stitched_flag",
                "restructure_blind_spot_flag",
            ),
            "match_type",
            *_table(stitched, "chain_match_type"),
            f"ambiguous (candidate_count > 1) "
            f"{stitched.filter(F.col('chain_candidate_count') > 1).count()}",
            f"months added min / median / max {months}",
            "stitched: old x new",
            *_table(stitched, "old_state", "det_state"),
        ],
    )

    unknown = latest.filter(F.col("det_state") == "unknown").withColumn(
        "route",
        F.when(F.col("restructure_blind_spot_flag") == 1, "restructured")
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
