"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    require_columns,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)
from .promises import EVENTS
from .sources import CYCLE_LEDGER, DUES, EPISODE, INSTALMENTS, PAYMENTS


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    """``GRAIN`` and ``_anchor`` of every base row."""
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _commitment_counts(base: DataFrame, events: DataFrame, lower: Column) -> DataFrame:
    """Per base row with an event in ``[lower, observation date]``: the concluded, kept
    and partly kept counts and ``commitments_last_broken_n``, the not-kept events among
    the last ``BROKEN_STREAK`` concluded."""
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct(
                        "event_date", (~F.col("_kept")).cast("int").alias("broken")
                    ),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    return rows.groupBy(*GRAIN).agg(
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / thin / broken (D-A3-9, -25, -26).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only); concluded once their cutoff is on or before the observation date.
    An event is kept when paid; partial counts as not kept. Broken: the last 3 concluded
    all not kept (a broken event ranks first on a shared day), or at least 2 concluded
    and under 40% kept. Kept: at least 2 concluded and 80% kept. Partly kept: any
    kept event. Else thin.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(events, EVENTS, "A3 promise events")
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    agg = _commitment_counts(base, events, lower)
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
    counts = [
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
        "commitments_last_broken_n",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
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
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
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
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(ledger, CYCLE_LEDGER, "A3 cycle ledger")
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
    ("paid", codes.PAYMENT_REPORTED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


# Contacts on the same day: the one later in this order counts as the latest (Q-28: a
# refusal never outranks another contact of its day).
_SAME_DAY_ORDER = ("refusal", "dispute", "hung_up", "paid", "ptp", "success")


def _disposition(name: Column) -> Column:
    """The ``_DISPOSITIONS`` label of a DCORE result name (NULL: not a contact)."""
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid on or after
    the refusal day, up to the observation date (Q-29). A payment that may have come
    after the refusal lifts it: one dated the refusal day, and on RL the refusal
    month's cash (known only to the month)."""
    accounts = F.broadcast(refusals.select("account_id").distinct())
    cycles = dues.select("account_id", "cycle_start", "cycle_end").join(
        accounts, on="account_id", how="left_semi"
    )
    pays = (
        payments.join(accounts, on="account_id", how="left_semi")
        .alias("p")
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
            (F.col("pay_date") >= F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def _contact_events(
    episode: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """The account's DCORE events in ``[max(episode start, last DCORE_MAX_MONTHS
    months), observation date]`` with their ``_disp`` disposition (NULL: not a
    contact)."""
    lower = F.greatest(window_start(DCORE_MAX_MONTHS), F.col("_anchor"))
    return (
        _base(episode)
        .join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )


def _contact_summary(events: DataFrame) -> DataFrame:
    """Per base row: the latest right-party contact (``last_rpc_date``,
    ``last_rpc_disposition``; on one day, the latest by ``_SAME_DAY_ORDER``), the call
    days (``contact_dates_n``), the days with no pickup after the contact
    (``no_pickup_days_n``) and ``_dead``, 1 when a dead-line result came after it."""
    same_day_rank = F.lit(None).cast("int")
    for rank, label in enumerate(_SAME_DAY_ORDER):
        same_day_rank = F.when(F.col("_disp") == label, rank).otherwise(same_day_rank)
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct("day", same_day_rank.alias("same_day_rank"), "_disp"),
        )
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    last_day = F.col("_last")["day"]
    after = F.col("day") > last_day
    return (
        events.withColumn("_last", latest.over(Window.partitionBy(*GRAIN)))
        .groupBy(*GRAIN)
        .agg(
            F.max("_last")["day"].alias("last_rpc_date"),
            F.max("_last")["_disp"].alias("last_rpc_disposition"),
            F.size(
                F.collect_set(
                    F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
                )
            )
            .cast("long")
            .alias("contact_dates_n"),
            F.size(F.collect_set(F.when(after & no_pickup, F.col("day"))))
            .cast("long")
            .alias("no_pickup_days_n"),
            F.max(
                F.when(
                    after, F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")
                )
            ).alias("_dead"),
        )
    )


def _plan_after_refusal(refusals: DataFrame, instalments: DataFrame) -> DataFrame:
    """Rows whose plan started after the refusal day, by the observation date."""
    return (
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


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on the same day a non-refusal counts as later
    (a same-day promise followed the refusal); a remaining tie takes the largest
    disposition (Q-28). ``a3_refusal_flag``: it was a refusal and no plan started and no
    cycle / month with 100 AED or more paid followed. Diagnostics (not in the state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    require_columns(episode, EPISODE, "A3 episode")
    require_columns(instalments, INSTALMENTS, "A3 instalments")
    require_columns(payments, PAYMENTS, "A3 payments")
    require_columns(dues, DUES, "A3 dues")
    events = _contact_events(episode, followup, agreements)
    summary = _contact_summary(events)
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = _plan_after_refusal(refusals, instalments)
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        _base(episode)
        .select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
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
