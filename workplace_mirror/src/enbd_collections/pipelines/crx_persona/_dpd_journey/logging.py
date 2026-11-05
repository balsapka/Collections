"""Stage telemetry — the state-distribution log is always on (``_common``'s format,
shared with every axis); sequence stats are opt-in, one extra aggregate job per node
when log_stats=True."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import log_latest_month
from .constants import BucketScheme
from .params import JourneyParams

LOG = logging.getLogger(__name__)


# Logs the build_status counts and the gap, cycle-shift and invalid-row totals of
# ``seq``: one extra aggregate job, run only when ``log_stats`` is set.
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


def log_state_stats(
    out: DataFrame, end_date: str, scheme: BucketScheme, params: JourneyParams
) -> None:
    """det_state distribution of persona_end_date's month, one row per account."""
    log_latest_month(
        out,
        "det_state",
        f"a4_deterioration [{scheme.name}_{params.segment}]",
        end_date,
        latest_per_account=True,
    )
