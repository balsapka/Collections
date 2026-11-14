"""A3 promise events (D-A3-25): DCORE plans and follow-up promise runs, each judged
by payment by its deadline (``PROMISE_DEADLINE``)."""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import dcore_account_events, require_columns
from .constants import (
    DEADLINES,
    FOLLOWUP_RUN_DAYS,
    MATCH_DAYS,
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


def _run_step(run: Column, row: Column) -> Column:
    """Fold one follow-up row into ``run`` (``firsts``: the first row of every run so
    far with its cutoff, ``prev``: the previous row's date, ``cutoff``: the current
    run's deadline)."""
    starts = (
        run["prev"].isNull()
        | (F.datediff(row["event_date"], run["prev"]) > FOLLOWUP_RUN_DAYS)
        | (row["event_date"] > run["cutoff"])
    )
    first = F.struct(row["event_date"], row["name"], row["promise_cutoff"])
    return F.struct(
        F.when(starts, F.concat(run["firsts"], F.array(first)))
        .otherwise(run["firsts"])
        .alias("firsts"),
        row["event_date"].alias("prev"),
        F.when(starts, row["promise_cutoff"]).otherwise(run["cutoff"]).alias("cutoff"),
    )


def _no_runs() -> Column:
    """The empty ``_run_step`` accumulator."""
    return F.struct(
        F.array()
        .cast("array<struct<event_date:date,name:string,promise_cutoff:date>>")
        .alias("firsts"),
        F.lit(None).cast("date").alias("prev"),
        F.lit(None).cast("date").alias("cutoff"),
    )


def _followup_promises(
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    dues: DataFrame,
    deadline: str,
) -> DataFrame:
    """Follow-up promise runs per account, dated (and named) at their first row, with
    its ``promise_cutoff`` (the run's deadline). A row starts a new run when it is more
    than 7 days after the previous row or after the run's deadline (D-A3-29)."""
    rows = _cutoff(
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select("account_id", F.col("day").alias("event_date"), "name")
        .distinct(),
        dues,
        deadline,
    )
    ordered = F.array_sort(
        F.collect_list(F.struct("event_date", "name", "promise_cutoff"))
    )
    return (
        rows.groupBy("account_id")
        .agg(F.aggregate(ordered, _no_runs(), _run_step)["firsts"].alias("_firsts"))
        .select("account_id", F.explode("_firsts").alias("_first"))
        .select(
            "account_id",
            F.col("_first.event_date").alias("fu_date"),
            F.col("_first.name").alias("event_name"),
            F.col("_first.promise_cutoff").alias("promise_cutoff"),
        )
    )


def _consolidate(plans: DataFrame, promises: DataFrame) -> DataFrame:
    """One event per DCORE plan and per follow-up promise no plan claims. A plan takes
    its nearest follow-up promise within 7 days (each promise at most once): the event
    keeps the plan's date and cutoff and the promise's name (``matched``)."""
    pairs = (
        plans.select("account_id", "plan_id", "event_date")
        .join(promises.drop("promise_cutoff"), on="account_id")
        .withColumn("_dist", F.abs(F.datediff("fu_date", "event_date")))
        .where(F.col("_dist") <= MATCH_DAYS)
    )
    for key, tie in ((["plan_id"], "fu_date"), (["fu_date"], "plan_id")):
        nearest = Window.partitionBy("account_id", *key).orderBy("_dist", tie)
        pairs = pairs.withColumn("_r", F.row_number().over(nearest)).where("_r = 1")
    table = plans.join(
        pairs.select("account_id", "plan_id", "event_name"),
        on=["account_id", "plan_id"],
        how="left",
    ).select(
        "account_id",
        "event_date",
        F.when(F.col("event_name").isNotNull(), "matched")
        .otherwise("table_only")
        .alias("event_kind"),
        F.col("plan_type").alias("event_source"),
        "event_name",
        "plan_id",
        "promise_cutoff",
    )
    alone = promises.join(
        pairs.select("account_id", "fu_date"), on=["account_id", "fu_date"], how="anti"
    ).select(
        "account_id",
        F.col("fu_date").alias("event_date"),
        F.lit("followup_only").alias("event_kind"),
        F.lit("followup").alias("event_source"),
        "event_name",
        F.lit(None).cast("string").alias("plan_id"),
        "promise_cutoff",
    )
    return table.unionByName(alone)


def _cutoff(events: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``events`` + ``promise_cutoff``: the last day a payment still counts."""
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
    return events.join(nxt, on=["account_id", "event_date"], how="left").withColumn(
        "promise_cutoff",
        F.coalesce("promise_cutoff", F.date_add(day, STATEMENT_FALLBACK_D)),
    )


def _with_due(events: DataFrame, dues: DataFrame) -> DataFrame:
    """``events`` + ``_due``: the due of the cycle open on the event day (the latest
    cycle starting on or before it)."""
    cycles = dues.select(
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
    after = (F.col("pay_date") > day) | (
        (F.col("pay_date") == day) & (F.col("pay_from") < F.col("pay_date"))
    )
    return (
        events.join(
            pays,
            (F.col("account_id") == F.col("_p_account"))
            & after
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

    Events: every non-cancelled PTP and settlement plan (dated at its start) and every
    follow-up promise run (``_dcore_codes.PROMISE_EVENT``; a follow-up after the run's
    deadline starts a new run) no plan claims
    (``event_kind`` matched / table_only / followup_only). Judged once: the payments
    after the event day up to ``promise_cutoff`` (``deadline``, by default
    ``promise_deadline(product, model_id)``) against ``promise_amount``, the due of the
    cycle open on the event day (the last known one, at least 100 AED). Paid: they reach
    it; partial: 100 AED or more; else none. RL cash is dated at the month end, so the
    event month's cash counts in full.
    """
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    deadline = promise_deadline(product, model_id, deadline)
    plans = _cutoff(
        instalments.select(
            "account_id",
            "plan_id",
            "plan_type",
            F.col("plan_start").alias("event_date"),
        ).distinct(),
        dues,
        deadline,
    )
    promises = _followup_promises(obs_base, followup, agreements, dues, deadline)
    judged = _with_paid(_with_due(_consolidate(plans, promises), dues), payments)
    amount = F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(MIN_PAYMENT_AED)))
    got = F.coalesce("promise_paid_amount", F.lit(0.0))
    return (
        judged.withColumn("promise_amount", amount)
        .withColumn("promise_paid_amount", got)
        .withColumn(
            "promise_outcome",
            F.when(got >= F.col("promise_amount"), "paid")
            .when(got >= MIN_PAYMENT_AED, "partial")
            .otherwise("none"),
        )
        .select(*EVENTS)
    )
