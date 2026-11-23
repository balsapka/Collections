"""UC1 stated block at (account_id, observation_date), shared by CC and RL.

UC1's customer table ``customer_signal_export`` is read as it is: one row per customer
and signal, ``estimated_value`` = UC1's final level (call transcripts and agent remarks,
recent evidence weighted higher), with its confidence, the latest transcript value and
the latest agent-remark value. Tied levels arrive joined by ``|``. This module maps the
levels to states and adds two flags:

* ``a5_state``, stated ability, from ``payment_capacity``: able / partly_able / unable;
* ``a6_state``, stated intent, from ``payment_intent``: pays_in_full / partly_or_later
  (partial or with delay) / refuses; a tie takes the more cautious level;
* ``not_stated``: the customer is in UC1's table and the signal is ``not-detected``;
* ``no_evidence``: not in UC1's table; ``uc1_evidence`` says why (no_cif /
  no_conversation / not_extracted);
* ``stated_promise_unlogged_flag``: pays in full or partly / later, an amount or a date
  mentioned, and no A3 promise event near the last call (``signals.py``); NULL when
  that holds but there is no dated call;
* ``verify_stated_ability_flag``: able, or pays in full, while ``a1_state`` is low.

UC1's table carries no date per level, so only one month is scored
(``signals.scored_month``); every other month's row carries NULL in every UC1 column.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month, require_columns, string_key
from .signals import latest_month, scored_month

NOT_DETECTED = "not-detected"
NO_VALUE = (NOT_DETECTED, "N/A", "")
TIE = "|"
# Levels in cautious-first order (a tie keeps the first of its levels in this order).
LEVELS = {
    "payment_capacity": ("none", "partial", "full"),
    "payment_intent": ("no_payment", "with_delay", "partial", "payback_full"),
    "delinquency_reason": (
        "lost_employment",
        "reduced_employment",
        "increased_obligations",
        "has_employment",
    ),
    "payment_period": ("months_or_longer", "salary_cycle_dependent", "weeks"),
    "dispute": ("customer_scammed", "system_problem", "other"),
    "request": ("detected",),
    "fraudulent_customer": ("detected",),
}
REPAYMENT = {
    "amount": "repayment_specifics:amount_mentioned",
    "date": "repayment_specifics:date_specific",
    "plan": "repayment_specifics:plan_structure_mentioned",
}
EXPORT = [
    "cif_id",
    "signal",
    "estimated_value",
    "confidence",
    "latest_value",
    "agent_remark_value",
    "supporting_data",
    "snapshot_date",
]
ABILITY_STATES = {"full": "able", "partial": "partly_able", "none": "unable"}
INTENT_STATES = {
    "payback_full": "pays_in_full",
    "partial": "partly_or_later",
    "with_delay": "partly_or_later",
    "no_payment": "refuses",
}
PAYING = ("pays_in_full", "partly_or_later")
_OUTPUT = [
    "uc1_evidence",
    "uc1_snapshot_date",
    "a5_state",
    "a5_capacity_level",
    "a5_confidence",
    "a5_latest_value",
    "a5_remark_value",
    "a5_supporting_data",
    "a5_reason",
    "a5_reason_confidence",
    "a6_state",
    "a6_intent_level",
    "a6_confidence",
    "a6_latest_value",
    "a6_remark_value",
    "a6_period",
    "a6_amount_named_flag",
    "a6_date_named_flag",
    "a6_plan_named_flag",
    "stated_dispute",
    "stated_request_flag",
    "stated_fraud_flag",
    "stated_promise_unlogged_flag",
    "verify_stated_ability_flag",
    "uc1_conversations_n",
    "uc1_last_conversation_date",
]


def _check_levels(export: DataFrame) -> None:
    """Stop the run on a level UC1's table holds outside ``LEVELS`` (a schema change
    on their side, to be looked at, not guessed)."""
    allowed = F.create_map(
        *[
            x
            for signal, levels in LEVELS.items()
            for x in (F.lit(signal), F.array(*[F.lit(v) for v in levels]))
        ]
    )
    parts = export.filter(F.col("signal").isin(*LEVELS)).select(
        "signal",
        F.explode(F.split("estimated_value", f"\\{TIE}")).alias("level"),
    )
    found = (
        parts.filter(
            F.col("level").isNull()
            | (
                (F.col("level") != NOT_DETECTED)
                & ~F.array_contains(allowed[F.col("signal")], F.col("level"))
            )
        )
        .select("signal", "level")
        .distinct()
        .limit(20)
        .collect()
    )
    if found:
        values = sorted(f"{r['signal']}={r['level']}" for r in found)
        raise ValueError(f"UC1 customer_signal_export has unknown values: {values}")


def _level(col: str, signal: str) -> Column:
    """The level of ``col`` (NULL = not detected); a tie keeps its most cautious level."""
    parts = F.split(F.col(col), f"\\{TIE}")
    cautious = F.coalesce(
        *[F.when(F.array_contains(parts, v), F.lit(v)) for v in LEVELS[signal]]
    )
    return F.when(F.col(col).isin(*NO_VALUE) | F.col(col).isNull(), None).otherwise(
        F.when(F.col(col).contains(TIE), cautious).otherwise(F.col(col))
    )


def _wide(export: DataFrame) -> DataFrame:
    """One row per customer: per signal its estimate and details, the repayment slots'
    mentioned flags, and the snapshot date."""
    require_columns(export, EXPORT, "UC1 customer_signal_export")
    _check_levels(export)
    signal = F.col("signal")

    def pick(name: str, col: str) -> Column:
        return F.max(F.when(signal == name, F.col(col)))

    def mentioned(slot: str) -> Column:
        values = [F.col(c) for c in ("latest_value", "agent_remark_value")]
        named = [(v.isNotNull() & ~v.isin(*NO_VALUE)) for v in values]
        return F.max(F.when((signal == slot) & (named[0] | named[1]), 1).otherwise(0))

    return export.groupBy(string_key(export, "cif_id").alias("cif_id")).agg(
        F.max(F.to_date("snapshot_date")).alias("uc1_snapshot_date"),
        *[pick(s, "estimated_value").alias(f"_est_{s}") for s in LEVELS],
        *[
            pick(s, c).alias(f"_{c}_{s}")
            for s in ("payment_capacity", "payment_intent")
            for c in ("confidence", "latest_value", "agent_remark_value")
        ],
        pick("payment_capacity", "supporting_data").alias("_supporting"),
        pick("delinquency_reason", "confidence").alias("_reason_confidence"),
        *[mentioned(slot).alias(f"_{key}_named") for key, slot in REPAYMENT.items()],
    )


def _mapped(level: Column, mapping: dict[str, str]) -> Column:
    pairs = [F.lit(x) for item in mapping.items() for x in item]
    return F.create_map(*pairs)[level]


def _evidence() -> Column:
    return (
        F.when(F.col("cif_id").isNull(), "no_cif")
        .when(F.col("uc1_snapshot_date").isNotNull(), "extracted")
        .when(F.coalesce(F.col("uc1_conversations_n"), F.lit(0)) > 0, "not_extracted")
        .otherwise("no_conversation")
    )


def _stated_columns() -> dict[str, Column]:
    """The stated columns, read after ``uc1_evidence``: NULL details and
    ``no_evidence`` states unless the evidence is ``extracted``."""
    stated = F.col("uc1_evidence") == "extracted"

    def when_stated(col: Column) -> Column:
        return F.when(stated, col)

    def state(level: Column, mapping: dict[str, str]) -> Column:
        value = F.coalesce(_mapped(level, mapping), F.lit("not_stated"))
        return F.when(stated, value).otherwise("no_evidence")

    capacity = _level("_est_payment_capacity", "payment_capacity")
    intent = _level("_est_payment_intent", "payment_intent")
    a5, a6 = state(capacity, ABILITY_STATES), state(intent, INTENT_STATES)
    named = (F.col("_amount_named") == 1) | (F.col("_date_named") == 1)
    near = F.col("dcore_promise_near_call_flag")
    promise = F.when(a6.isin(*PAYING) & named, 1 - near).otherwise(0)
    verify = (F.col("a1_state") == "low") & ((a5 == "able") | (a6 == "pays_in_full"))

    def detected(signal: str) -> Column:
        level = _level(f"_est_{signal}", signal)
        return F.coalesce(level == "detected", F.lit(False)).cast("int")

    return {
        "a5_state": a5,
        "a5_capacity_level": when_stated(F.col("_est_payment_capacity")),
        "a5_confidence": when_stated(F.col("_confidence_payment_capacity")),
        "a5_latest_value": when_stated(F.col("_latest_value_payment_capacity")),
        "a5_remark_value": when_stated(F.col("_agent_remark_value_payment_capacity")),
        "a5_supporting_data": when_stated(F.col("_supporting")),
        "a5_reason": when_stated(
            _level("_est_delinquency_reason", "delinquency_reason")
        ),
        "a5_reason_confidence": when_stated(F.col("_reason_confidence")),
        "a6_state": a6,
        "a6_intent_level": when_stated(F.col("_est_payment_intent")),
        "a6_confidence": when_stated(F.col("_confidence_payment_intent")),
        "a6_latest_value": when_stated(F.col("_latest_value_payment_intent")),
        "a6_remark_value": when_stated(F.col("_agent_remark_value_payment_intent")),
        "a6_period": when_stated(_level("_est_payment_period", "payment_period")),
        "a6_amount_named_flag": when_stated(F.col("_amount_named")),
        "a6_date_named_flag": when_stated(F.col("_date_named")),
        "a6_plan_named_flag": when_stated(F.col("_plan_named")),
        "stated_dispute": when_stated(
            F.coalesce(_level("_est_dispute", "dispute"), F.lit("none"))
        ),
        "stated_request_flag": when_stated(detected("request")),
        "stated_fraud_flag": when_stated(detected("fraudulent_customer")),
        "stated_promise_unlogged_flag": when_stated(promise),
        "verify_stated_ability_flag": when_stated(verify.cast("int")),
    }


def build_uc1_stated(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    export: DataFrame,
    conversations: DataFrame,
    a1_ability: DataFrame,
    model_id: str,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> DataFrame:
    """One row per observation: the evidence status, both stated axes with UC1's
    confidence and values, the reason, period, repayment, dispute, request and fraud
    details, the two flags and the conversation count."""
    require_columns(a1_ability, [*GRAIN, "a1_state"], "A1 ability")
    month = scored_month(persona_end_date, uc1_month_end)
    scored = (
        latest_month(obs_base, month)
        .join(_wide(export), "cif_id", "left")
        .join(conversations, list(GRAIN), "left")
        .join(a1_ability.select(*GRAIN, "a1_state"), list(GRAIN), "left")
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
    for col in ("uc1_evidence", "a5_state", "a6_state", "stated_promise_unlogged_flag"):
        log_latest_month(out, col, name, month)
    return out
