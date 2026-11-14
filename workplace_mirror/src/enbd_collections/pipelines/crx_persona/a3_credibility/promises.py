"""A3 promise events (D-A3-25, -29): DCORE plans and follow-up promises grouped into
events, each judged by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    DEADLINES,
    MIN_PAYMENT_AED,
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


def _event_step(live: Column, day: Column) -> Column:
    """Fold one promise day into ``live``, the event alive so far (D-A3-29). The day
    joins it while its deadline has not passed and the payments before the day have not
    reached its promised amount; otherwise the day starts a new event. ``starts``: the
    event start of every day so far."""
    paid_before = day["_paid_before"] - live["paid_at_start"]
    joins = (
        live["start"].isNotNull()
        & (day["event_date"] <= live["cutoff"])
        & (paid_before < live["amount"])
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


def _event_starts(days: DataFrame) -> DataFrame:
    """``account_id``, ``event_date``, ``event_start``: the event each promise day
    belongs to (``_event_step`` over the account's days in date order)."""
    ordered = F.array_sort(
        F.collect_list(
            F.struct(
                "event_date",
                "promise_cutoff",
                "promise_amount",
                "_paid_before",
                "_paid_by",
            )
        )
    )
    return (
        days.groupBy("account_id")
        .agg(ordered.alias("_days"))
        .withColumn("_starts", F.aggregate("_days", _no_event(), _event_step)["starts"])
        .select("account_id", F.explode(F.arrays_zip("_days", "_starts")).alias("_d"))
        .select(
            "account_id",
            F.col("_d._days.event_date").alias("event_date"),
            F.col("_d._starts").alias("event_start"),
        )
    )


def _events(rows: DataFrame, starts: DataFrame) -> DataFrame:
    """One event per ``event_start``: its first plan (``plan_id``, ``event_source``) and
    first follow-up promise (``event_name``); ``event_kind`` matched (both), table_only
    or followup_only."""
    is_plan = F.col("plan_id").isNotNull()
    plan = F.min(F.when(is_plan, F.struct("event_date", "plan_id", "event_source")))
    call = F.min(F.when(~is_plan, F.struct("event_date", "event_name")))
    return (
        rows.join(starts, on=["account_id", "event_date"])
        .groupBy("account_id", "event_start")
        .agg(plan.alias("_plan"), call.alias("_call"))
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
        )
    )


def _cutoff(events: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``events`` + ``promise_cutoff``, the last day a payment still counts, by
    ``deadline`` (``DEADLINES``). ``next_statement``: the first cycle end after the
    event day, at most ``STATEMENT_FALLBACK_D`` days after it (no statement on record
    by then: that day)."""
    day = F.col("event_date")
    fixed = {
        "month_end": F.last_day(day),
        "next_month_end": F.last_day(F.add_months(day, 1)),
        "30_days": F.date_add(day, 30),
        "30_days_month_end": F.last_day(F.date_add(day, 30)),
    }
    if deadline in fixed:
        return events.withColumn("promise_cutoff", fixed[deadline])
    if deadline != "next_statement":
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    nxt = (
        events.select("account_id", "event_date")
        .distinct()
        .join(dues.select("account_id", "cycle_end"), on="account_id")
        .where(F.col("cycle_end") > day)
        .groupBy("account_id", "event_date")
        .agg(F.min("cycle_end").alias("promise_cutoff"))
    )
    fallback = F.date_add(day, STATEMENT_FALLBACK_D)
    return events.join(nxt, on=["account_id", "event_date"], how="left").withColumn(
        "promise_cutoff", F.least(F.coalesce("promise_cutoff", fallback), fallback)
    )


def _with_due(events: DataFrame, dues: DataFrame) -> DataFrame:
    """``events`` + ``_due``: the latest known due on the event day (the latest cycle
    starting on or before it that has a due amount)."""
    cycles = dues.where(F.col("due_amount").isNotNull()).select(
        F.col("account_id").alias("_c_account"), "cycle_start", "due_amount"
    )
    return (
        events.join(
            cycles,
            (F.col("account_id") == F.col("_c_account"))
            & (F.col("cycle_start") <= F.col("event_date")),
            "left",
        )
        .groupBy(*events.columns)
        .agg(F.max(F.struct("cycle_start", "due_amount"))["due_amount"].alias("_due"))
    )


def _after(day: Column) -> Column:
    """A payment counted as made after ``day``: dated later, or dated that day when its
    period started earlier (RL cash is dated at the month end)."""
    return (F.col("pay_date") > day) | (
        (F.col("pay_date") == day) & (F.col("pay_from") < F.col("pay_date"))
    )


def _with_paid_by(days: DataFrame, payments: DataFrame) -> DataFrame:
    """``days`` + ``_paid_before``, the payments dated before the day, and ``_paid_by``,
    the payments not after it (``_after``): what an event starting that day never
    counts."""
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
            (F.col("account_id") == F.col("_p_account")) & (F.col("pay_date") <= day),
            "left",
        )
        .groupBy(*days.columns)
        .agg(
            total(F.col("pay_date") < day).alias("_paid_before"),
            total(~_after(day)).alias("_paid_by"),
        )
    )


def _with_paid(events: DataFrame, payments: DataFrame) -> DataFrame:
    """``events`` + ``promise_paid_amount``: the payments after the event day up to its
    ``promise_cutoff`` (a payment on the event day counts when it started earlier)."""
    day = F.col("event_date")
    pays = payments.select(
        F.col("account_id").alias("_p_account"),
        "pay_from",
        "pay_date",
        F.col("amount").alias("_amount"),
    )
    return (
        events.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & _after(day)
            & (F.col("pay_date") <= F.col("promise_cutoff")),
            "left",
        )
        .groupBy(*events.columns)
        .agg(F.sum("_amount").alias("promise_paid_amount"))
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
    """Promise events of the base's accounts, judged by payment (D-A3-25). ``EVENTS``.

    A promise is a non-cancelled PTP or settlement plan (dated at its start) or a
    follow-up promise. An event starts with the first promise and stays alive until its
    deadline passes or the payments reach the promised amount; every promise meanwhile
    belongs to it, the first one after it starts a new event (D-A3-29). ``event_kind``:
    matched (plans and follow-up promises), table_only, followup_only.

    Judged once: the payments after the event day up to ``promise_cutoff``
    (``deadline``, by default ``promise_deadline(product, model_id)``) against
    ``promise_amount``, the latest known due on the event day (at least 100 AED). Paid:
    they reach it; partial: 100 AED or more; else none. RL cash is dated at the month
    end, so the event month's cash counts in full and never ends an event mid-month.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    rows = _promise_rows(obs_base, followup, agreements, instalments)
    days = _with_due(
        _cutoff(rows.select("account_id", "event_date").distinct(), dues, deadline),
        dues,
    ).select(
        "account_id",
        "event_date",
        "promise_cutoff",
        F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(MIN_PAYMENT_AED))).alias(
            "promise_amount"
        ),
    )
    starts = _event_starts(_with_paid_by(days, payments))
    judged = _with_paid(
        _events(rows, starts).join(days, on=["account_id", "event_date"]), payments
    )
    got = F.coalesce("promise_paid_amount", F.lit(0.0))
    return (
        judged.withColumn("promise_paid_amount", got)
        .withColumn(
            "promise_outcome",
            F.when(got >= F.col("promise_amount"), "paid")
            .when(got >= MIN_PAYMENT_AED, "partial")
            .otherwise("none"),
        )
        .select(*EVENTS)
    )
