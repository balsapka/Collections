"""CC A3 sources: the history window of the raw extract, statement cycles with one
month's due, and card payments."""

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, string_key
from .._dpd_journey.anchor import episode_start
from ..a3_credibility.constants import HISTORY_MONTHS

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of ladder due averaged (D-A3-12, -31)
_LADDER = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]


def _history_floor(history_floor_date: str) -> Column:
    """The first statement day kept: ``history_floor_date`` less ``FLOOR_LOOKBACK_DAYS``
    (the statement just before the floor)."""
    return F.date_sub(F.lit(str(history_floor_date)).cast("date"), FLOOR_LOOKBACK_DAYS)


def build_cc_acct_windows(
    obs_base: DataFrame, deterioration: DataFrame, history_floor_date: str
) -> DataFrame:
    """``account_id``, ``acct_start``, ``acct_end``: the raw history the CC A3 extracts
    read per account (``crx_cc_raw_extract``).

    ``acct_start``: ``HISTORY_MONTHS`` before the earlier of the account's earliest
    episode start (A4) and its first observation month, never before the history floor;
    ``acct_end``: its last observation date.
    """
    episodes = episode_start(obs_base, deterioration)
    first = (
        obs_base.join(episodes, on=["account_id", "observation_date"], how="left")
        .groupBy("account_id")
        .agg(
            F.least(
                F.min("episode_start"), F.trunc(F.min("observation_date"), "month")
            ).alias("_first"),
            F.max("observation_date").alias("acct_end"),
        )
    )
    return first.select(
        "account_id",
        F.greatest(
            F.add_months(F.col("_first"), -HISTORY_MONTHS),
            _history_floor(history_floor_date),
        ).alias("acct_start"),
        "acct_end",
    )


def _nonzero(col: str) -> Column:
    """Way4 writes an empty bucket as 0, not NULL."""
    return F.col(col).isNotNull() & (F.col(col) != 0.0)


def _balance_dues(balance: DataFrame) -> DataFrame:
    """``(account_id, cycle_start, billed_amount, due_amount)`` per statement.

    ``billed_amount`` (the ladder value): the oldest open bucket 07..01, else the
    minimum due. ``due_amount`` (one month's due) is the ladder value while bucket 08
    (Way4's accumulator, not one month) is empty. On a statement with bucket 08 open it
    is the baseline: the average ladder value of the 12 months before bucket 08 first
    held money, or NULL when there is none (D-A3-12, -31). ``billed_amount``
    (Dimension C) keeps the ladder value.
    """
    billed = F.coalesce(*[F.when(_nonzero(c), F.col(c)) for c in _LADDER])
    rows = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("cycle_start"),
        billed.alias("billed_amount"),
        _nonzero("overdue_bucket_08").alias("_accumulating"),
    )
    rows = rows.withColumn(
        "_since",
        F.min(F.when(F.col("_accumulating"), F.col("cycle_start"))).over(
            Window.partitionBy("account_id")
        ),
    )
    recent = Window.partitionBy("account_id").orderBy(F.col("_month").desc())
    baseline = (
        rows.where(
            F.col("billed_amount").isNotNull()
            & (F.col("cycle_start") < F.col("_since"))
        )
        .groupBy("account_id", F.trunc("cycle_start", "month").alias("_month"))
        .agg(F.avg("billed_amount").alias("_m"))
        .withColumn("_r", F.row_number().over(recent))
        .where(F.col("_r") <= BUCKET08_BASELINE_MONTHS)
        .groupBy("account_id")
        .agg(F.avg("_m").alias("_baseline"))
    )
    return rows.join(baseline, "account_id", "left").select(
        "account_id",
        "cycle_start",
        "billed_amount",
        F.when(F.col("_accumulating"), F.col("_baseline"))
        .otherwise(F.col("billed_amount"))
        .alias("due_amount"),
    )


def build_cc_a3_dues(
    billing: DataFrame, balance: DataFrame, history_floor_date: str
) -> DataFrame:
    """A3 dues contract per statement cycle (D-A3-15): ``cycle_start`` = the statement,
    ``cycle_end`` = the next one. A cycle longer than 62 days spans missing statements
    and is dropped, as is one starting more than 35 days before the history floor; the
    latest cycle (no next statement yet) has no result and is left out."""
    require_columns(
        billing,
        ["contract_id", "observation_date", "next_billing_date"],
        "crx_cc_billing",
    )
    require_columns(
        balance,
        ["contract_id", "observation_date", "overdue_bucket_08", *_LADDER],
        "crx_cc_balance",
    )
    start = F.col("observation_date").cast("date")
    end = F.col("next_billing_date").cast("date")
    floor = _history_floor(history_floor_date)
    cycles = (
        billing.where(
            end.isNotNull()
            & (F.datediff(end, start) <= CYCLE_MAX_DAYS)
            & (start >= floor)
        )
        .select(
            string_key(billing, "contract_id").alias("account_id"),
            start.alias("cycle_start"),
            end.alias("cycle_end"),
        )
        .distinct()
    )
    return cycles.join(
        _balance_dues(balance), on=["account_id", "cycle_start"], how="left"
    )


def build_cc_a3_payments(transactions: DataFrame) -> DataFrame:
    """A3 payments contract: card payments (category ``payment``, no post-block fee
    artefacts), dated by banking date."""
    require_columns(
        transactions,
        [
            "contract_id",
            "observation_date",
            "txn_amount_aed",
            "txn_category",
            "is_post_block_x_fee",
        ],
        "crx_cc_transactions",
    )
    day = F.col("observation_date").cast("date")
    return transactions.where(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        string_key(transactions, "contract_id").alias("account_id"),
        day.alias("pay_from"),
        day.alias("pay_date"),
        F.col("txn_amount_aed").cast("double").alias("amount"),
    )
