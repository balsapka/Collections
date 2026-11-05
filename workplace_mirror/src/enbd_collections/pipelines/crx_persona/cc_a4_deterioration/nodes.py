"""CC A4 — deterioration state for credit cards (wrappers on ``_dpd_journey``).

Node 1 build_cc_dpd_sequences     crx_cc_full_history -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration  crx_cc_dpd_sequences + cc_spine
                                  -> crx_cc_a4_deterioration
Run: ``kedro run --pipeline=crx_cc_a4_deterioration`` (needs crx_cc_full_history).

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210,
9 = 210+. History before ``dpd_journey.cc_history_floor_date`` (default 2024-01-01:
the billing history is unreliable before it, temporary) is not used; accounts with
older history are flagged cropped. ``cc_180_plus`` reads
``cc_history_floor_date_180_plus`` (same default) instead, because the journey of most
long charged-off accounts starts before the shared floor and leaves them "unknown";
override that key alone to relax the floor at 180+ (conformance D5).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns
from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

# Same value as cc_spell's _RESTRUCTURE_DLQ_THRESHOLD: an account whose earliest
# billing row is already at this dlq_bucket or above was opened mid-delinquency by a
# restructure, not merely cut off by the data depth (conformance D2).
_RESTRUCTURE_DLQ_THRESHOLD = 4


def _restructure_blind_spot(history: DataFrame) -> DataFrame:
    """``account_id``, ``restructure_blind_spot_flag``: 1 when the account's earliest
    dated row is already at ``_RESTRUCTURE_DLQ_THRESHOLD`` or worse."""
    # Earliest dated row; on a same-date tie the worst bucket wins, because the bucket
    # is negated so the smallest struct is that row.
    first = F.min(F.struct("obs_date", (-F.col("dlq_bucket")).alias("neg_bucket")))
    return (
        history.filter(F.col("dlq_bucket").isNotNull())
        .groupBy("account_id")
        .agg(first.alias("_first"))
        .select(
            "account_id",
            (-F.col("_first.neg_bucket") >= _RESTRUCTURE_DLQ_THRESHOLD)
            .cast("int")
            .alias("restructure_blind_spot_flag"),
        )
    )


def build_cc_dpd_sequences(
    crx_cc_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per CC account: gap-filled monthly bucket array (from the history floor
    to persona_end_date) + audit columns + restructure_blind_spot_flag (1 if the
    account's earliest billing row already has dlq_bucket >=
    _RESTRUCTURE_DLQ_THRESHOLD).
    See _dpd_journey.build_dpd_sequences.
    """
    require_columns(
        crx_cc_full_history,
        ["account_id", "billing_date", "dlq_bucket"],
        "crx_cc_full_history",
    )
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket"
    )

    restructure = _restructure_blind_spot(history)
    return build_dpd_sequences(
        history, CC, journey_params(crx_persona, CC, model_id), restructure=restructure
    )


def build_cc_a4_deterioration(
    crx_cc_dpd_sequences: DataFrame,
    cc_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, cc_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_cc_dpd_sequences. cc_spine is already scoped to the model_id's DLQ band, so no
    segment filter is applied here. See _dpd_journey.build_deterioration.
    """
    require_columns(cc_spine, ["contract_id", "observation_date"], "cc_spine")
    spine = cc_spine.select(
        F.col("contract_id").alias("account_id"), "observation_date"
    )
    return build_deterioration(
        crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC, model_id), spine
    )
