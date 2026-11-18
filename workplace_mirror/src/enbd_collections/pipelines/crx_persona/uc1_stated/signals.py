"""UC1 conversation evidence at (account_id, observation_date), shared by CC and RL.

UC1 is another team's signal extraction from call transcripts. Its outputs are read as
they are, from the shared file store: ``metadata`` (every conversation), the extraction
ledger ``extracted_signals`` (only ``model_version``) and the per-conversation grid
``timelines/signal_level_conflicts`` (the level each conversation detected).

Conversations UC1 extracted only in the ``legacy`` format are dropped everywhere (UC1
reads no level from them). Per customer (``cif_id``, all accounts) this counts the
remaining conversations dated strictly before the observation date: all of them, the
extracted ones, and those that detected each capacity and intent level or named an
amount or a date. Only the month of
``crx_persona.persona_end_date`` is scored: UC1's customer table has no date, so earlier
months cannot be read point in time.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, require_columns, scoped, string_key

CAPACITY_LEVELS = ("none", "partial", "full")
INTENT_LEVELS = ("no_payment", "with_delay", "partial", "payback_full")
LEGACY_MODEL_VERSION = "legacy"


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The ``obs_base`` rows of the month of ``persona_end_date``, with a string
    ``cif_id`` join key."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month).select(
        *GRAIN, string_key(obs_base, "cif_id").alias("cif_id")
    )


def _conversations(
    base: DataFrame, metadata: DataFrame, extracted: DataFrame, grid: DataFrame
) -> DataFrame:
    """One row per conversation of the base's customers, legacy-only extractions
    dropped: ``cif_id``, its date, ``_extracted`` (1 = extracted in the current format,
    NULL = not extracted) and what it detected (``_capacity``, ``_intent``, ``_amount``,
    ``_date``)."""
    meta = scoped(
        metadata.select(
            string_key(metadata, "cif_id").alias("cif_id"),
            "conversationid",
            F.to_date("conversationstart").alias("_conv_date"),
        ),
        base,
        "cif_id",
    )
    is_current = F.coalesce(F.col("model_version") != LEGACY_MODEL_VERSION, F.lit(True))
    ledger = extracted.groupBy("conversationid").agg(
        F.max(is_current.cast("int")).alias("_current")
    )
    signal, value = F.col("signal"), F.col("value")
    slot = F.split(value, ":").getItem(0)
    specifics = signal == "repayment_specifics"
    detected = (
        grid.filter(F.col("observation") == "detected")
        .groupBy("conversationid")
        .agg(
            F.max(F.when(signal == "payment_capacity", value)).alias("_capacity"),
            F.max(F.when(signal == "payment_intent", value)).alias("_intent"),
            F.max(F.when(specifics & (slot == "amount_mentioned"), 1)).alias("_amount"),
            F.max(F.when(specifics & (slot == "date_specific"), 1)).alias("_date"),
        )
    )
    return (
        meta.join(ledger, "conversationid", "left")
        .filter(F.coalesce(F.col("_current"), F.lit(1)) == 1)
        .withColumnRenamed("_current", "_extracted")
        .join(detected, "conversationid", "left")
    )


def build_uc1_conversation_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    metadata: DataFrame,
    extracted_signals: DataFrame,
    signal_level_conflicts: DataFrame,
    persona_end_date: str,
) -> DataFrame:
    """Conversation counts per latest-month observation whose customer has any UC1
    conversation (earlier or later): ``uc1_conversations_n``, ``uc1_extracted_n``,
    the last conversation / extracted dates, ``uc1_after_obs_flag``
    (an extracted conversation on or after the observation date), ``amount_named_flag``,
    ``date_named_flag`` and one ``capacity_<level>_n`` / ``intent_<level>_n`` per level.
    """
    require_columns(
        metadata, ["conversationid", "cif_id", "conversationstart"], "UC1 metadata"
    )
    require_columns(
        extracted_signals, ["conversationid", "model_version"], "UC1 extracted_signals"
    )
    require_columns(
        signal_level_conflicts,
        ["conversationid", "signal", "value", "observation"],
        "UC1 signal_level_conflicts",
    )
    base = latest_month(obs_base, persona_end_date)
    conversations = _conversations(
        base, metadata, extracted_signals, signal_level_conflicts
    )

    before = F.col("_conv_date") < F.col("observation_date")
    extracted = F.col("_extracted").isNotNull()

    def count(cond: Column) -> Column:
        return F.sum(F.when(before & cond, 1).otherwise(0))

    def flag(col: str) -> Column:
        return F.coalesce(F.max(F.when(before, F.col(col))), F.lit(0))

    return (
        base.join(conversations, on="cif_id")
        .groupBy(*GRAIN)
        .agg(
            count(F.lit(True)).alias("uc1_conversations_n"),
            count(extracted).alias("uc1_extracted_n"),
            F.max(F.when(before, F.col("_conv_date"))).alias(
                "uc1_last_conversation_date"
            ),
            F.max(F.when(before & extracted, F.col("_conv_date"))).alias(
                "uc1_last_extracted_date"
            ),
            F.max(F.when(~before & extracted, 1).otherwise(0)).alias(
                "uc1_after_obs_flag"
            ),
            flag("_amount").alias("amount_named_flag"),
            flag("_date").alias("date_named_flag"),
            *[
                count(F.col("_capacity") == level).alias(f"capacity_{level}_n")
                for level in CAPACITY_LEVELS
            ],
            *[
                count(F.col("_intent") == level).alias(f"intent_{level}_n")
                for level in INTENT_LEVELS
            ],
        )
    )
