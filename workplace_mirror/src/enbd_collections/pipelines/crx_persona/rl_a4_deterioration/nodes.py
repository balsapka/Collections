"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_dpd_sequences    crx_rl_full_history  -> crx_rl_dpd_sequences
Node 2 build_rl_a4_deterioration crx_rl_dpd_sequences -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import RL, build_deterioration, build_dpd_sequences, journey_params


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (1 if the loan was restructured in any month) +
    ecl_gap_blind_spot_flag (1 if the loan was disbursed before the ECL/DPL union seam
    AND its product_code falls outside the set the pre-cutoff ECL historical extract is
    structurally winnowed to — see _dpd_journey.spark.build_dpd_sequences).
    """
    history = crx_rl_full_history.select(
        "account_id",
        F.col("month_end_date").alias("obs_date"),
        "dlq_bucket",
        "restructure_flag",
        "disbursement_date",
        "product_code",
    )
    return build_dpd_sequences(history, RL, journey_params(crx_persona, RL, model_id))


def build_rl_a4_deterioration(
    crx_rl_dpd_sequences: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here."""
    spine = rl_spine.select("account_id", "observation_date")
    return build_deterioration(
        crx_rl_dpd_sequences, RL, journey_params(crx_persona, RL, model_id), spine
    )
