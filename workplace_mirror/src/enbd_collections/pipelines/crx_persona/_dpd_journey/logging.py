"""Stage telemetry — state-distribution log is always-on; sequence stats are opt-in,
one extra aggregate job per node when log_stats=True."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import Window
from pyspark.sql import functions as F

from ._dates import _month_col, _month_idx, _month_label
from .constants import BucketScheme
from .params import JourneyParams

LOG = logging.getLogger(__name__)


def _log_sequence_stats(
    seq: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> None:
    r = (
        seq.agg(
            F.count("*").alias("accounts"),
            *[
                F.sum((F.col("build_status") == s).cast("int")).alias(s)
                for s in (
                    "ok",
                    "no_rows_in_window",
                    "no_valid_rows",
                    "dropped_unresolvable_gap",
                )
            ],
            F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
            F.sum((F.col("n_months_truncated") > 0).cast("int")).alias(
                "truncated_accounts"
            ),
            F.sum("n_gap_months_filled").alias("gap_months_filled"),
            F.sum("n_gap_months_rolled").alias("gap_months_rolled"),
            F.sum("n_gap_months_inferred").alias("gap_months_inferred"),
            F.sum("n_cycle_shift_moves").alias("cycle_shift_moves"),
            F.sum(F.col("legacy_drop").cast("int")).alias("legacy_rule_would_drop"),
            F.sum("n_dup_month_rows").alias("dup_month_rows"),
            F.sum("n_invalid_rows").alias("invalid_rows"),
            F.min("first_month").alias("first_month"),
            F.max("last_month").alias("last_month"),
        )
        .first()
        .asDict()
    )
    LOG.info(
        "build_%s_dpd_sequences [end %s, floor %s, gaps %s]: %s",
        scheme.name,
        params.end_date,
        params.floor_date,
        params.on_unresolvable_gap,
        r,
    )


def _log_state_stats(
    out: DataFrame, end_date: str, scheme: BucketScheme, params: JourneyParams
) -> None:
    """det_state distribution for the latest month of the crx modelling date range
    (persona_end_date's calendar month, matched via `_month_col` — NOT an exact-day
    filter: CC billing dates land on a different day per account within the month, so
    `observation_date == persona_end_date` keeps almost none of the population). `out`
    is point-in-time (one row per spine row, not one row per account), so an
    unrestricted groupBy would also mix every historical month together — restrict to
    the target month, then keep the latest row per account within it (in case an
    account has more than one observation that month). Same always-on logging
    convention and format as cc_a2_locatability_v2/cc_a3_payment_credibility's own
    _log_a2_v2_stats/_log_a3_stats."""
    try:
        end_idx = _month_idx(end_date)
        same_month = out.where(_month_col(F.col("observation_date")) == F.lit(end_idx))
        w = Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
        snap = (
            same_month.withColumn("_rn", F.row_number().over(w))
            .where(F.col("_rn") == 1)
            .drop("_rn")
        )
        rows = snap.groupBy("det_state").agg(F.count("*").alias("n")).collect()
        n_total = sum(r["n"] for r in rows)
        LOG.info(
            "build_%s_deterioration [%s]: total accounts (%s) = %d",
            scheme.name,
            params.segment,
            _month_label(end_date),
            n_total,
        )
        for r in sorted(rows, key=lambda r: -r["n"]):
            pct = 100.0 * r["n"] / max(n_total, 1)
            LOG.info(
                "  det_state=%-28s n=%7d  (%.1f%%)", str(r["det_state"]), r["n"], pct
            )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "build_%s_deterioration: stats logging failed: %s", scheme.name, exc
        )
