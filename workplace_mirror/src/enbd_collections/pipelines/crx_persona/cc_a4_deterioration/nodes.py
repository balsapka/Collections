"""CC-A4 — DPD-journey deterioration state for credit cards (thin wrappers on _dpd_journey).

Node 1 build_cc_dpd_sequences    crx_cc_full_history -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration crx_cc_dpd_sequences                    -> crx_cc_a4_deterioration

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210, 9 = 210+.
History before params dpd_journey.cc_history_floor_date (default 2024-01-01, known data-
quality issue, temporary) is not used; accounts with older history are flagged cropped.
cc_180_plus reads its own dpd_journey.cc_history_floor_date_180_plus (same default) instead
-- T43's 2026-10-20 PROD run found the shared floor leaves 99.07% of the gt2y chargeoff-age
vintage "unknown" (their journey start predates the floor by construction); override this
key alone to relax/remove the floor for 180_plus without touching the 60_180 run.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

# Mirrors cc_spell/nodes.py's _RESTRUCTURE_DLQ_THRESHOLD: an account whose earliest
# billing observation is already at this dlq_bucket or above was opened mid-delinquency
# as part of a restructure (R13), not merely data-depth censored.
_RESTRUCTURE_DLQ_THRESHOLD = 4


def build_cc_dpd_sequences(
    crx_cc_full_history: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One row per CC account: gap-filled monthly bucket array (from the history floor to
    persona_end_date) + audit columns + restructure_blind_spot_flag (R13: 1 if the
    account's earliest billing observation already has dlq_bucket >= _RESTRUCTURE_DLQ_THRESHOLD).
    Derived directly from crx_cc_full_history — no spell-table dependency.
    See _dpd_journey.build_dpd_sequences.
    """
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket"
    )

    # Earliest dated row per account; F.max is the deterministic tie-break on
    # same-date conflicting rows (more deterministic than the old spell table's
    # row_number() tie-break — a deliberate improvement, not a regression).
    history_dated = history.filter(F.col("dlq_bucket").isNotNull())
    earliest_date = history_dated.groupBy("account_id").agg(
        F.min("obs_date").alias("_first_date")
    )
    restructure = (
        history_dated.join(earliest_date, on="account_id")
        .filter(F.col("obs_date") == F.col("_first_date"))
        .groupBy("account_id")
        .agg(F.max("dlq_bucket").alias("_first_dlq_bucket"))
        .select(
            "account_id",
            (F.col("_first_dlq_bucket") >= F.lit(_RESTRUCTURE_DLQ_THRESHOLD))
            .cast("int")
            .alias("restructure_blind_spot_flag"),
        )
    )
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
    build_cc_dpd_sequences. cc_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here. See _dpd_journey.build_deterioration.
    """
    spine = cc_spine.select(
        F.col("contract_id").alias("account_id"), "observation_date"
    )
    return build_deterioration(
        crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC, model_id), spine
    )
