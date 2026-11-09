"""A3 source nodes shared by both products: the episode anchor, the cycle ledger, the
DCORE plans and the promise events."""

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import GRAIN, dcore_account_events, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start
from .constants import (
    DEADLINES,
    FOLLOWUP_RUN_DAYS,
    MATCH_DAYS,
    MIN_PAYMENT_AED,
    STATEMENT_FALLBACK_D,
)

DUES = ["account_id", "cycle_start", "cycle_end", "due_amount", "billed_amount"]
PAYMENTS = ["account_id", "pay_from", "pay_date", "amount"]


def build_a3_episode(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for every base row (D-A3-2).

    ``episode_start`` is the first day of the month the current delinquency episode
    began, from A4 as of the observation date; NULL when A4 did not score the row (A3
    then reads Unknown, reason ``no_episode``, Q-12).
    """
    return obs_base.select(*GRAIN, "cif_id").join(
        episode_start(obs_base, deterioration), on=list(GRAIN), how="left"
    )


def build_cycle_ledger(dues: DataFrame, payments: DataFrame) -> DataFrame:
    """One row per account cycle: ``DUES`` + ``paid_amount``, the payments with
    ``cycle_start < pay_date <= cycle_end`` (paid before the next statement, D-A3-8).

    ``dues`` and ``payments`` follow the product contracts ``DUES`` / ``PAYMENTS``
    (CC: statement cycles and card payments; RL: months and the month's cash).
    """
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    paid = (
        dues.select("account_id", "cycle_start", "cycle_end")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(
            (F.col("pay_date") > F.col("cycle_start"))
            & (F.col("pay_date") <= F.col("cycle_end"))
        )
        .groupBy("account_id", "cycle_end")
        .agg(F.sum("amount").alias("paid_amount"))
    )
    return (
        dues.select(*DUES)
        .join(paid, on=["account_id", "cycle_end"], how="left")
        .withColumn("paid_amount", F.coalesce(F.col("paid_amount"), F.lit(0.0)))
    )


def build_instalments(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> DataFrame:
    """PTP and settlement instalments of the base's accounts (D-A3-7, D-A3-9).

    One row per instalment of a non-cancelled plan: ``account_id``, ``plan_id``,
    ``plan_type``, ``plan_start`` (PTP: promise start, else event date; settlement: event
    date, the only date DCORE keeps), ``due_date``, ``due_amount``, ``payment_amount``
    (DCORE's). Cancelled instalments are nulled by DCORE's own rule and dropped.
    """
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    require_columns(
        int_ptp,
        [
            "agreement_id",
            "promise_seqno",
            "promise_start",
            "event_date",
            "is_cancelled",
        ],
        "dcore_int_ptp",
    )
    require_columns(
        int_settlement,
        ["agreement_id", "rps_seqno", "event_date", "is_cancelled"],
        "dcore_int_settlement",
    )
    cols = ["due_date", "due_amount", "payment_amount", "instalment_status"]
    require_columns(
        ptp_instalments, ["promise_seqno", *cols], "dcore_prm_promise_instalments"
    )
    require_columns(
        settlement_instalments,
        ["rps_seqno", *cols],
        "dcore_prm_settlement_schedule_instalments",
    )
    links = scoped(
        agreements.select(
            string_key(agreements).alias("account_id"),
            F.col("agreement_id").cast("string").alias("agreement_id"),
        ),
        obs_base,
        "account_id",
    )

    def plans(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        plan: DataFrame, seq: str, start, kind: str, rows: DataFrame, cancelled
    ) -> DataFrame:
        live = plan.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            seq,
            F.concat_ws(":", F.lit(kind), F.col(seq).cast("string")).alias("plan_id"),
            F.lit(kind).alias("plan_type"),
            start.cast("date").alias("plan_start"),
        )
        return null_cancelled_instalment_fields(
            live.join(rows.select(seq, *cols), on=seq), cancelled
        ).drop(seq)

    ptp = plans(
        int_ptp,
        "promise_seqno",
        F.coalesce(F.col("promise_start"), F.col("event_date")),
        "ptp",
        ptp_instalments,
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = plans(
        int_settlement,
        "rps_seqno",
        F.col("event_date"),
        "settlement",
        settlement_instalments,
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    return (
        ptp.unionByName(settlement)
        .join(F.broadcast(links), on="agreement_id")
        .where(F.col("due_date").isNotNull())
        .select(
            "account_id",
            "plan_id",
            "plan_type",
            "plan_start",
            F.col("due_date").cast("date").alias("due_date"),
            F.col("due_amount").cast("double").alias("due_amount"),
            F.col("payment_amount").cast("double").alias("payment_amount"),
        )
    )


# ── Promise events (D-A3-25) ──────────────────────────────────────────────────

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


def _followup_promises(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Follow-up promise runs per account: rows less than 8 days after the previous one
    belong to the same run, dated (and named) at its first row."""
    rows = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select("account_id", "day", "name")
        .distinct()
    )
    order = Window.partitionBy("account_id").orderBy("day", "name")
    gap = F.datediff("day", F.lag("day").over(order))
    new_run = F.when(gap.isNull() | (gap > FOLLOWUP_RUN_DAYS), 1).otherwise(0)
    first = F.min(F.struct("day", "name"))
    return (
        rows.withColumn(
            "_run", F.sum(new_run).over(order.rowsBetween(Window.unboundedPreceding, 0))
        )
        .groupBy("account_id", "_run")
        .agg(first["day"].alias("fu_date"), first["name"].alias("event_name"))
        .drop("_run")
    )


def _consolidate(plans: DataFrame, promises: DataFrame) -> DataFrame:
    """One event per DCORE plan and per follow-up promise no plan claims. A plan takes
    its nearest follow-up promise within 7 days (each promise at most once): the event
    keeps the plan's date and the promise's name (``matched``)."""
    pairs = (
        plans.select("account_id", "plan_id", "event_date")
        .join(promises, on="account_id")
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
    )
    return table.unionByName(alone)


def _cutoff(events: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``events`` + ``promise_cutoff``: the last day a payment still counts."""
    day = F.col("event_date")
    fixed = {
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


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    deadline: str,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment (D-A3-25). ``EVENTS``.

    Events: every non-cancelled PTP and settlement plan (dated at its start) and every
    follow-up promise run (``_dcore_codes.PROMISE_EVENT``) no plan claims
    (``event_kind`` matched / table_only / followup_only). Judged once: the payments
    after the event day up to ``promise_cutoff`` (``deadline``, ``PROMISE_DEADLINE``)
    against ``promise_amount``, the due of the cycle open on the event day (the last
    known one, at least 100 AED). Paid: they reach it; partial: 100 AED or more; else
    none. RL cash is dated at the month end, so the event month's cash counts in full.
    """
    plans = instalments.select(
        "account_id", "plan_id", "plan_type", F.col("plan_start").alias("event_date")
    ).distinct()
    events = _cutoff(
        _consolidate(plans, _followup_promises(obs_base, followup, agreements)),
        dues,
        deadline,
    )
    keys = ["account_id", "event_date"]
    due = (
        events.select(*keys)
        .distinct()
        .join(dues.select("account_id", "cycle_start", "due_amount"), on="account_id")
        .where(F.col("cycle_start") <= F.col("event_date"))
        .groupBy(*keys)
        .agg(F.max(F.struct("cycle_start", "due_amount"))["due_amount"].alias("_due"))
    )
    after = (F.col("pay_date") > F.col("event_date")) | (
        (F.col("pay_date") == F.col("event_date"))
        & (F.col("pay_from") < F.col("pay_date"))
    )
    paid = (
        events.select(*keys, "promise_cutoff")
        .distinct()
        .join(
            payments.select("account_id", "pay_from", "pay_date", "amount"),
            "account_id",
        )
        .where(after & (F.col("pay_date") <= F.col("promise_cutoff")))
        .groupBy(*keys, "promise_cutoff")
        .agg(F.sum("amount").alias("promise_paid_amount"))
    )
    amount = F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(MIN_PAYMENT_AED)))
    got = F.coalesce("promise_paid_amount", F.lit(0.0))
    return (
        events.join(due, on=keys, how="left")
        .join(paid, on=[*keys, "promise_cutoff"], how="left")
        .withColumn("promise_amount", amount)
        .withColumn("promise_paid_amount", got)
        .withColumn(
            "promise_outcome",
            F.when(got >= F.col("promise_amount"), "paid")
            .when(got >= MIN_PAYMENT_AED, "partial")
            .otherwise("none"),
        )
        .select(*EVENTS)
    )
