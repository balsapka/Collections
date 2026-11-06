"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    instalment_amount_flags,
)

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CC_GRACE_FALLBACK_D,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_BY,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _grace_cutoff(instalments: DataFrame, dues: DataFrame, grace: str) -> DataFrame:
    """``instalments`` + ``cutoff``: the last day a payment still keeps the instalment."""
    if grace == "next_month_end":
        return instalments.withColumn("cutoff", F.last_day(F.add_months("due_date", 1)))
    statements = dues.select("account_id", F.col("cycle_end").alias("_stmt")).distinct()
    first = (
        instalments.select("account_id", "due_date")
        .distinct()
        .join(statements, on="account_id")
        .filter(F.col("_stmt") >= F.col("due_date"))
        .groupBy("account_id", "due_date")
        .agg(F.min("_stmt").alias("cutoff"))
    )
    return instalments.join(
        first, on=["account_id", "due_date"], how="left"
    ).withColumn(
        "cutoff", F.coalesce("cutoff", F.date_add("due_date", CC_GRACE_FALLBACK_D))
    )


def _covered(instalments: DataFrame, payments: DataFrame) -> DataFrame:
    """``instalments`` + ``covered_date``: the day payments since the plan start first
    reach the plan's cumulative due up to and including the instalment (V1c rule)."""
    plan = Window.partitionBy("plan_id").orderBy("due_date", "due_amount")
    inst = instalments.withColumn("_n", F.row_number().over(plan)).withColumn(
        "cum_due",
        F.sum(F.coalesce("due_amount", F.lit(0.0))).over(
            plan.rowsBetween(Window.unboundedPreceding, 0)
        ),
    )
    running = (
        Window.partitionBy("plan_id", "_n")
        .orderBy("pay_date")
        .rangeBetween(Window.unboundedPreceding, 0)
    )
    hit = (
        inst.select("account_id", "plan_id", "_n", "plan_start", "cum_due")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(F.col("pay_date") >= F.col("plan_start"))
        .withColumn("_paid", F.sum("amount").over(running))
        .filter(F.col("_paid") >= F.col("cum_due"))
        .groupBy("plan_id", "_n")
        .agg(F.min("pay_date").alias("covered_date"))
    )
    return inst.join(hit, on=["plan_id", "_n"], how="left")


def build_commitment_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    episode: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    kept_by: str,
    grace: str,
) -> DataFrame:
    """Dimension A: kept / partly kept / thin / broken (D-A3-9, D-A3-11).

    Instalments due in ``[max(episode start, last 12 months), observation date]``.
    ``kept_by="payments"``: kept when payments reach the cumulative due by the grace
    cutoff; concluded once kept or past the cutoff. ``kept_by="dcore"``: DCORE's own
    paid / overdue flags. Broken: the last 3 concluded all broken (a broken instalment
    ranks first on a shared due date), or at least 2 concluded and under 40% kept.
    """
    if kept_by not in KEPT_BY:
        raise ValueError(f"a3_kept_by must be one of {KEPT_BY}, got {kept_by!r}")
    if kept_by == "payments":
        instalments = _covered(_grace_cutoff(instalments, dues, grace), payments)
    base = _base(episode)
    lower = F.greatest(window_start(COMMITMENT_MONTHS), F.col("_anchor"))
    rows = base.join(instalments, on="account_id").filter(
        (F.col("due_date") >= lower) & (F.col("due_date") <= F.col("observation_date"))
    )
    if kept_by == "payments":
        obs = F.col("observation_date")
        kept = F.col("covered_date") <= F.least("cutoff", obs)
        concluded = kept | (F.col("cutoff") <= obs)
    else:
        is_paid, _, is_overdue = instalment_amount_flags()
        kept, concluded = is_paid, is_paid | is_overdue
    rows = rows.withColumn("_kept", F.coalesce(kept, F.lit(False))).withColumn(
        "_concluded", F.coalesce(concluded, F.lit(False))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct("due_date", (~F.col("_kept")).cast("int").alias("broken")),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    agg = rows.groupBy(*GRAIN).agg(
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum((F.col("_concluded") & F.col("_kept")).cast("int")).alias(
            "commitments_kept"
        ),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when(
            (F.col("commitments_last_broken_n") >= BROKEN_STREAK)
            | ((done >= MIN_CONCLUDED) & (rate < BROKEN_RATE)),
            "broken",
        )
        .when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .otherwise("thin")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(
            0,
            ["commitments_concluded", "commitments_kept", "commitments_last_broken_n"],
        )
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_concluded",
            "commitments_kept",
            rate.alias("commitments_kept_rate"),
            "commitments_last_broken_n",
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_CONFIRMED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


def _disposition(name: Column) -> Column:
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid after the
    refusal day, up to the observation date (Q-29)."""
    cycles = dues.select("account_id", "cycle_start", "cycle_end")
    pays = (
        payments.alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_from") > F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
    max_months: int | None = DCORE_MAX_MONTHS,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on the same day a non-refusal counts as later
    (a same-day promise followed the refusal); a remaining tie takes the largest
    disposition (Q-28). ``a3_refusal_flag``: it was a refusal and no plan started and no
    cycle / month with 100 AED or more paid followed. Diagnostics (not in the state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    base = _base(episode)
    lower = window_start(max_months) if max_months else None
    lower = F.col("_anchor") if lower is None else F.greatest(lower, F.col("_anchor"))
    events = (
        base.join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct(
                "day", (F.col("_disp") != "refusal").cast("int").alias("later"), "_disp"
            ),
        )
    )
    summary = events.groupBy(*GRAIN).agg(
        latest["day"].alias("last_rpc_date"),
        latest["_disp"].alias("last_rpc_disposition"),
        F.countDistinct(
            F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
        ).alias("contact_dates_n"),
    )
    after = events.join(summary.select(*GRAIN, "last_rpc_date"), on=list(GRAIN)).filter(
        F.col("day") > F.col("last_rpc_date")
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    quiet = after.groupBy(*GRAIN).agg(
        F.countDistinct(F.when(no_pickup, F.col("day"))).alias("no_pickup_days_n"),
        F.max(F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")).alias(
            "_dead"
        ),
    )
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") > F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        base.select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(quiet, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
