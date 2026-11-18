"""UC1 stated block at (account_id, observation_date), shared by CC and RL.

UC1's customer table ``timelines/simple_signal_aggregation`` is read as it is: one level
per signal per customer, the most frequent over all of the customer's extracted
conversations (UC1's rule; no date, confidence or count). This module maps levels to
states and adds the conversation counts of ``signals.py``:

* ``a5_state``, stated ability, from ``payment_capacity``: able / partly_able / unable;
* ``a6_state``, stated intent, from ``payment_intent``: pays_in_full / partly_or_later
  (partial or with delay) / refuses;
* ``not_stated``: the customer has a current-format extracted conversation before the
  observation date, and the signal was not detected;
* ``no_evidence``: no such conversation; ``uc1_evidence`` says why (no_cif /
  no_conversation / not_extracted / legacy_only).

Support: the conversations before the observation date that detected the signal, and
how many of them detected the published level (``a5_agree_n``, ``a6_agree_n``).
``uc1_after_obs_flag`` = 1 when the published level may rest on a conversation dated on
or after the observation date. Only the month of ``crx_persona.persona_end_date`` is
scored; the other months' rows carry NULL in every UC1 column.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month, require_columns, string_key
from .signals import CAPACITY_LEVELS, INTENT_LEVELS, latest_month

NOT_DETECTED = "NA"
LEVELS = {
    "payment_capacity": CAPACITY_LEVELS,
    "payment_intent": INTENT_LEVELS,
    "delinquency_reason": (
        "lost_employment",
        "reduced_employment",
        "has_employment",
        "increased_obligations",
    ),
    "payment_period": ("salary_cycle_dependent", "weeks", "months_or_longer"),
    "dispute": ("system_problem", "customer_scammed", "other"),
    "request": ("detected",),
}
ABILITY_STATES = {"full": "able", "partial": "partly_able", "none": "unable"}
INTENT_STATES = {
    "payback_full": "pays_in_full",
    "partial": "partly_or_later",
    "with_delay": "partly_or_later",
    "no_payment": "refuses",
}
_COUNTS = [
    "uc1_conversations_n",
    "uc1_extracted_n",
    "uc1_current_n",
    "uc1_after_obs_flag",
    "amount_named_flag",
    "date_named_flag",
    *[f"capacity_{level}_n" for level in CAPACITY_LEVELS],
    *[f"intent_{level}_n" for level in INTENT_LEVELS],
]
_OUTPUT = [
    "uc1_evidence",
    "a5_state",
    "a5_reason",
    "a5_conversations_n",
    "a5_agree_n",
    "a6_state",
    "a6_intent_level",
    "a6_period",
    "a6_amount_named_flag",
    "a6_date_named_flag",
    "a6_conversations_n",
    "a6_agree_n",
    "stated_dispute",
    "stated_request_flag",
    "uc1_conversations_n",
    "uc1_extracted_n",
    "uc1_last_conversation_date",
    "uc1_last_extracted_date",
    "uc1_after_obs_flag",
]


def _levels(aggregation: DataFrame) -> DataFrame:
    """``cif_id`` and the published level of each signal in ``LEVELS`` (NULL = not
    detected), checked: an unknown level or a missing signal stops the run."""
    require_columns(
        aggregation, ["cif_id", "signals_json"], "UC1 simple_signal_aggregation"
    )
    js = F.col("signals_json")
    levels = aggregation.select(
        string_key(aggregation, "cif_id").alias("cif_id"),
        *[F.get_json_object(js, f"$.{s}").alias(f"_raw_{s}") for s in LEVELS],
        *[F.get_json_object(js, f"$.{s}.level").alias(s) for s in LEVELS],
    )
    unknown = None
    for signal, allowed in LEVELS.items():
        raw = F.col(f"_raw_{signal}")
        known = (raw == NOT_DETECTED) | F.coalesce(
            F.col(signal).isin(*allowed), F.lit(False)
        )
        rows = levels.filter(raw.isNull() | ~known).select(
            F.lit(signal).alias("signal"), raw.alias("value")
        )
        unknown = rows if unknown is None else unknown.unionByName(rows)
    found = unknown.distinct().limit(20).collect()
    if found:
        values = sorted(f"{r['signal']}={r['value']}" for r in found)
        raise ValueError(f"UC1 simple_signal_aggregation has unknown values: {values}")
    return levels.select("cif_id", *LEVELS)


def _mapped(col: str, mapping: dict[str, str]) -> Column:
    pairs = [F.lit(x) for item in mapping.items() for x in item]
    return F.create_map(*pairs)[F.col(col)]


def _support(
    signal: str, prefix: str, levels: tuple[str, ...]
) -> tuple[Column, Column]:
    """Conversations that detected ``signal``, and those that detected its published
    level."""
    total = sum((F.col(f"{prefix}_{level}_n") for level in levels), F.lit(0))
    agree = F.coalesce(
        *[
            F.when(F.col(signal) == level, F.col(f"{prefix}_{level}_n"))
            for level in levels
        ],
        F.lit(0),
    )
    return total, agree


def _evidence() -> Column:
    return (
        F.when(F.col("cif_id").isNull(), "no_cif")
        .when(F.col("uc1_conversations_n") == 0, "no_conversation")
        .when(F.col("uc1_extracted_n") == 0, "not_extracted")
        .when(F.col("uc1_current_n") == 0, "legacy_only")
        .otherwise("extracted")
    )


def _stated_columns() -> dict[str, Column]:
    """The stated columns, read after ``uc1_evidence``: NULL details and
    ``no_evidence`` states unless the evidence is ``extracted``."""
    stated = F.col("uc1_evidence") == "extracted"

    def when_stated(col: Column) -> Column:
        return F.when(stated, col)

    def state(signal: str, mapping: dict[str, str]) -> Column:
        value = F.coalesce(_mapped(signal, mapping), F.lit("not_stated"))
        return F.when(stated, value).otherwise("no_evidence")

    a5_total, a5_agree = _support("payment_capacity", "capacity", CAPACITY_LEVELS)
    a6_total, a6_agree = _support("payment_intent", "intent", INTENT_LEVELS)
    request = F.coalesce(F.col("request") == "detected", F.lit(False)).cast("int")
    return {
        "a5_state": state("payment_capacity", ABILITY_STATES),
        "a5_reason": when_stated(F.col("delinquency_reason")),
        "a5_conversations_n": when_stated(a5_total),
        "a5_agree_n": when_stated(a5_agree),
        "a6_state": state("payment_intent", INTENT_STATES),
        "a6_intent_level": when_stated(F.col("payment_intent")),
        "a6_period": when_stated(F.col("payment_period")),
        "a6_amount_named_flag": when_stated(F.col("amount_named_flag")),
        "a6_date_named_flag": when_stated(F.col("date_named_flag")),
        "a6_conversations_n": when_stated(a6_total),
        "a6_agree_n": when_stated(a6_agree),
        "stated_dispute": when_stated(F.coalesce(F.col("dispute"), F.lit("none"))),
        "stated_request_flag": when_stated(request),
    }


def build_uc1_stated(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    aggregation: DataFrame,
    conversations: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation: the evidence status, both stated axes with their
    support and details, the dispute and request flags and the conversation counts."""
    scored = (
        latest_month(obs_base, persona_end_date)
        .join(_levels(aggregation), "cif_id", "left")
        .join(conversations, list(GRAIN), "left")
        .fillna(0, subset=_COUNTS)
        .withColumn("uc1_evidence", _evidence())
    )
    scored = scored.select(
        *scored.columns,
        *[col.alias(name) for name, col in _stated_columns().items()],
    )
    out = obs_base.select(*GRAIN).join(
        scored.select(*GRAIN, *_OUTPUT), list(GRAIN), "left"
    )
    name = f"uc1_stated [{model_id}]"
    for col in ("uc1_evidence", "a5_state", "a6_state"):
        log_latest_month(out, col, name, persona_end_date)
    return out
