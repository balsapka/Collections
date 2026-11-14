"""A3 promise events (D-A3-25, -28, -29): DCORE plans and follow-up promises grouped
into events, each judged by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    PROMISE_DAYS,
    PROMISE_MIN_AED,
    STATEMENT_FALLBACK_D,
    promise_deadline,
)
from .sources import DUES, INSTALMENTS, PAYMENTS

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]
# What a promise day decides for an event that starts on it (D-A3-29).
_TERMS = ("promise_cutoff", "promise_amount", "promise_paid_amount")
_DAY_TERMS = ("event_date", *_TERMS)


def _next_statement(day: Column, next_cycle_end: Column) -> Column:
    """The first cycle end after ``day``, at most ``STATEMENT_FALLBACK_D`` days after
    it (no statement on record by then: that day)."""
    fallback = F.date_add(day, STATEMENT_FALLBACK_D)
    return F.least(F.coalesce(next_cycle_end, fallback), fallback)


# ``promise_cutoff``, the last day a payment still counts, per deadline option
# (D-A3-28), from the promise day and the first cycle end after it.
CUTOFFS = {
    "next_statement": _next_statement,
    "month_end": lambda day, _: F.last_day(day),
    "next_month_end": lambda day, _: F.last_day(F.add_months(day, 1)),
    "30_days": lambda day, _: F.date_add(day, PROMISE_DAYS),
    "30_days_month_end": lambda day, _: F.last_day(F.date_add(day, PROMISE_DAYS)),
}
DEADLINES = tuple(CUTOFFS)


def _promise_rows(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
) -> DataFrame:
    """Every promise of the base's accounts, one row each: a DCORE plan dated at its
    start, a follow-up promise (``_dcore_codes.PROMISE_EVENT``) at its call day."""
    calls = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select(
            "account_id",
            F.col("day").alias("event_date"),
            F.col("name").alias("event_name"),
            F.lit(None).cast("string").alias("plan_id"),
            F.lit("followup").alias("event_source"),
        )
        .distinct()
    )
    plans = instalments.select(
        "account_id",
        F.col("plan_start").alias("event_date"),
        F.lit(None).cast("string").alias("event_name"),
        "plan_id",
        F.col("plan_type").alias("event_source"),
    ).distinct()
    return plans.unionByName(calls)


def _with_terms(days: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``days`` (``account_id``, ``event_date``) + ``promise_cutoff`` (``CUTOFFS``) and
    ``promise_amount``: the latest due on or before the day (cycles without a due amount
    skipped), at least ``PROMISE_MIN_AED``. One pass over the account's cycles."""
    day = F.col("event_date")
    known_due = F.col("due_amount").isNotNull() & (F.col("cycle_start") <= day)
    cycles = (
        days.join(
            dues.select("account_id", "cycle_start", "cycle_end", "due_amount"),
            on="account_id",
            how="left",
        )
        .groupBy("account_id", "event_date")
        .agg(
            F.min(F.when(F.col("cycle_end") > day, F.col("cycle_end"))).alias("_next"),
            F.max(F.when(known_due, F.struct("cycle_start", "due_amount")))[
                "due_amount"
            ].alias("_due"),
        )
    )
    return cycles.select(
        "account_id",
        "event_date",
        CUTOFFS[deadline](day, F.col("_next")).alias("promise_cutoff"),
        F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(PROMISE_MIN_AED))).alias(
            "promise_amount"
        ),
    )


def _after(day: Column) -> Column:
    """A payment counted as made after ``day``: dated later, or dated that day when its
    period started earlier (RL cash is dated at the month end)."""
    return (F.col("pay_date") > day) | (
        (F.col("pay_date") == day) & (F.col("pay_from") < F.col("pay_date"))
    )


def _with_payments(days: DataFrame, payments: DataFrame) -> DataFrame:
    """``days`` + three sums from one pass over the payments up to the day's
    ``promise_cutoff``: ``_paid_before`` (dated before the day) and ``_paid_by`` (not
    after it, ``_after``), which an event starting that day never counts, and
    ``promise_paid_amount`` (after the day; NULL: none), which it does."""
    day = F.col("event_date")
    pays = payments.select(
        F.col("account_id").alias("_p_account"),
        "pay_from",
        "pay_date",
        F.col("amount").alias("_amount"),
    )

    def total(counted: Column) -> Column:
        return F.coalesce(F.sum(F.when(counted, F.col("_amount"))), F.lit(0.0))

    return (
        days.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & (F.col("pay_date") <= F.col("promise_cutoff")),
            "left",
        )
        .groupBy(*days.columns)
        .agg(
            total(F.col("pay_date") < day).alias("_paid_before"),
            total(~_after(day)).alias("_paid_by"),
            F.sum(F.when(_after(day), F.col("_amount"))).alias("promise_paid_amount"),
        )
    )


def _event_step(live: Column, day: Column) -> Column:
    """Fold one promise day into ``live``, the event alive so far (D-A3-29). The day
    joins it while its deadline has not passed and the payments since the event day,
    before this day, have not reached its promised amount; otherwise the day starts a
    new event. ``starts``: the event start of every day so far."""
    paid_since_start = day["_paid_before"] - live["paid_at_start"]
    joins = (
        live["start"].isNotNull()
        & (day["event_date"] <= live["cutoff"])
        & (paid_since_start < live["amount"])
    )

    def keep(old: str, new: str) -> Column:
        return F.when(joins, live[old]).otherwise(day[new]).alias(old)

    start = keep("start", "event_date")
    return F.struct(
        F.concat(live["starts"], F.array(start)).alias("starts"),
        start,
        keep("cutoff", "promise_cutoff"),
        keep("amount", "promise_amount"),
        keep("paid_at_start", "_paid_by"),
    )


def _no_event() -> Column:
    """The empty ``_event_step`` accumulator."""
    return F.struct(
        F.array().cast("array<date>").alias("starts"),
        F.lit(None).cast("date").alias("start"),
        F.lit(None).cast("date").alias("cutoff"),
        F.lit(None).cast("double").alias("amount"),
        F.lit(None).cast("double").alias("paid_at_start"),
    )


def _with_event_start(days: DataFrame) -> DataFrame:
    """``account_id``, ``_DAY_TERMS`` and ``event_start``, the event each promise day
    belongs to (``_event_step`` over the account's days in date order)."""
    ordered = F.array_sort(
        F.collect_list(F.struct(*_DAY_TERMS, "_paid_before", "_paid_by"))
    )
    return (
        days.groupBy("account_id")
        .agg(ordered.alias("_days"))
        .withColumn("_starts", F.aggregate("_days", _no_event(), _event_step)["starts"])
        .select("account_id", F.explode(F.arrays_zip("_days", "_starts")).alias("_d"))
        .select(
            "account_id",
            *[F.col(f"_d._days.{c}").alias(c) for c in _DAY_TERMS],
            F.col("_d._starts").alias("event_start"),
        )
    )


def _events(promises: DataFrame, days: DataFrame) -> DataFrame:
    """One event per ``event_start``: its first plan (``plan_id``, ``event_source``) and
    first follow-up promise (``event_name``); ``event_kind`` matched (both), table_only
    or followup_only; the start day's cutoff, promised amount and paid amount."""
    is_plan = F.col("plan_id").isNotNull()
    plan = F.min(F.when(is_plan, F.struct("event_date", "plan_id", "event_source")))
    call = F.min(F.when(~is_plan, F.struct("event_date", "event_name")))
    start_day = F.max(
        F.when(F.col("event_date") == F.col("event_start"), F.struct(*_TERMS))
    )
    return (
        promises.join(days, on=["account_id", "event_date"])
        .groupBy("account_id", "event_start")
        .agg(plan.alias("_plan"), call.alias("_call"), start_day.alias("_start"))
        .select(
            "account_id",
            F.col("event_start").alias("event_date"),
            F.when(F.col("_plan").isNull(), "followup_only")
            .when(F.col("_call").isNull(), "table_only")
            .otherwise("matched")
            .alias("event_kind"),
            F.coalesce("_plan.event_source", F.lit("followup")).alias("event_source"),
            F.col("_call.event_name").alias("event_name"),
            F.col("_plan.plan_id").alias("plan_id"),
            "_start.*",
        )
    )


def _judged(events: DataFrame) -> DataFrame:
    """``EVENTS``: ``promise_outcome`` paid when the payments reach the promised amount,
    partial from ``PROMISE_MIN_AED``, else none."""
    paid = F.coalesce("promise_paid_amount", F.lit(0.0))
    outcome = (
        F.when(paid >= F.col("promise_amount"), "paid")
        .when(paid >= PROMISE_MIN_AED, "partial")
        .otherwise("none")
    )
    return (
        events.withColumn("promise_paid_amount", paid)
        .withColumn("promise_outcome", outcome)
        .select(*EVENTS)
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    model_id: str,
    product: str,
    deadline: str | None = None,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment. ``EVENTS``.

    A promise is a non-cancelled PTP or settlement plan (dated at its start) or a
    follow-up promise. An event starts with the first promise and stays alive until its
    deadline passes or the payments since its day reach the promised amount; every
    promise meanwhile belongs to it, the first one after it starts a new event
    (D-A3-29). ``event_kind``: matched (plans and follow-up promises), table_only,
    followup_only.

    The event day sets the terms: ``promise_cutoff`` by ``deadline`` (default
    ``promise_deadline(product, model_id)``, D-A3-28) and ``promise_amount``, the latest
    due on or before that day (at least ``PROMISE_MIN_AED``). Judged once on the
    payments after the event day up to the cutoff: paid when they reach the amount,
    partial from ``PROMISE_MIN_AED``, else none. RL cash is dated at the month end, so
    the event month's cash counts in full and never ends an event mid-month.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    if deadline not in CUTOFFS:
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    promises = _promise_rows(obs_base, followup, agreements, instalments)
    days = promises.select("account_id", "event_date").distinct()
    days = _with_payments(_with_terms(days, dues, deadline), payments)
    return _judged(_events(promises, _with_event_start(days)))
