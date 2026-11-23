"""UC1 conversations and DCORE promises at the UC1 month, shared by CC and RL.

Per observation of the scored month (``scored_month``): the customer's UC1 conversations
(``crx_uc1_metadata``, every account of the ``cif_id``) dated strictly before the
observation date, the date of the last one, and ``dcore_promise_near_call_flag``: 1 when
an A3 promise event of any of the customer's accounts in the base is alive within
``NEAR_CALL_DAYS`` days of that call (it starts on or before the call + 7 days and its
cutoff is on or after the call - 7 days), 0 when none is, NULL without a call. Events
dated after the observation date are not used.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, require_columns, scoped, string_key

NEAR_CALL_DAYS = 7


def scored_month(persona_end_date: str, uc1_month_end: str | None) -> str:
    """The month UC1 is scored at: ``uc1_month_end`` when set, else the persona end
    date."""
    return str(uc1_month_end or persona_end_date)


def latest_month(obs_base: DataFrame, month_date: str) -> DataFrame:
    """The ``obs_base`` rows of the month of ``month_date``, with a string ``cif_id``
    join key."""
    month = F.trunc(F.lit(str(month_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month).select(
        *GRAIN, string_key(obs_base, "cif_id").alias("cif_id")
    )


def build_uc1_conversation_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    metadata: DataFrame,
    promise_events: DataFrame,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> DataFrame:
    """``GRAIN`` of the scored month's observations whose customer had a UC1
    conversation before the observation date: ``uc1_conversations_n``,
    ``uc1_last_conversation_date`` and ``dcore_promise_near_call_flag``."""
    require_columns(
        metadata, ["conversationid", "cif_id", "conversationstart"], "UC1 metadata"
    )
    require_columns(
        promise_events,
        ["account_id", "event_date", "promise_cutoff"],
        "A3 promise events",
    )
    base = latest_month(obs_base, scored_month(persona_end_date, uc1_month_end))
    meta = scoped(
        metadata.select(
            string_key(metadata, "cif_id").alias("cif_id"),
            F.to_date("conversationstart").alias("_conv_date"),
        ),
        base,
        "cif_id",
    )
    calls = (
        base.join(meta, "cif_id")
        .filter(F.col("_conv_date") < F.col("observation_date"))
        .groupBy(*GRAIN, "cif_id")
        .agg(
            F.count(F.lit(1)).alias("uc1_conversations_n"),
            F.max("_conv_date").alias("uc1_last_conversation_date"),
        )
    )
    events = (
        base.select("cif_id", F.col("account_id").alias("_event_account"))
        .distinct()
        .join(
            promise_events.select(
                F.col("account_id").alias("_event_account"),
                F.to_date("event_date").alias("_event_date"),
                F.to_date(F.coalesce("promise_cutoff", "event_date")).alias("_cutoff"),
            ),
            "_event_account",
        )
        .select("cif_id", "_event_date", "_cutoff")
    )
    last = F.col("uc1_last_conversation_date")
    near = (
        (F.col("_event_date") <= F.date_add(last, NEAR_CALL_DAYS))
        & (F.col("_cutoff") >= F.date_sub(last, NEAR_CALL_DAYS))
        & (F.col("_event_date") <= F.col("observation_date"))
    )
    return (
        calls.join(events, "cif_id", "left")
        .groupBy(*GRAIN, "uc1_conversations_n", "uc1_last_conversation_date")
        .agg(F.max(F.when(near, 1).otherwise(0)).alias("dcore_promise_near_call_flag"))
    )
