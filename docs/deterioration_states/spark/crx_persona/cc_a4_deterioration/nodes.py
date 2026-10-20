"""CC-A4 — DPD-journey deterioration state for credit cards (thin wrappers on _dpd_journey).

Node 1 build_cc_dpd_sequences   crx_cc_full_history + crx_cc_spell_table -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration crx_cc_dpd_sequences                     -> crx_cc_a4_deterioration

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210, 9 = 210+.
History before params dpd_journey.cc_history_floor_date (default 2024-01-01, known data-
quality issue, temporary) is not used; accounts with older history are flagged cropped.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

_RESTRUCTURED_ENTRY = "restructured_entry"


def build_cc_dpd_sequences(crx_cc_full_history: DataFrame, crx_cc_spell_table: DataFrame,
                           crx_persona: dict) -> DataFrame:
    """One row per CC account: gap-filled monthly bucket array (from the history floor to
    persona_end_date) + audit columns + restructure_blind_spot_flag (R13: 1 if ANY spell of
    the account is censored_subtype == 'restructured_entry'). See _dpd_journey.build_dpd_sequences.
    """
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket")
    restructure = crx_cc_spell_table.groupBy("account_id").agg(
        F.max((F.col("censored_subtype") == _RESTRUCTURED_ENTRY).cast("int"))
        .alias("restructure_blind_spot_flag"))
    return build_dpd_sequences(history, CC, journey_params(crx_persona, CC), restructure=restructure)


def build_cc_a4_deterioration(crx_cc_dpd_sequences: DataFrame, crx_persona: dict) -> DataFrame:
    """One state per CC account whose latest bucket is in the run's segment (params
    dpd_journey.segment: 60_180 -> buckets 4-7, 180_plus -> 8-9). See _dpd_journey.build_deterioration.
    """
    return build_deterioration(crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC))
