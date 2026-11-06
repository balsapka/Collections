"""CC A3 sources: statement cycles with one month's due, and card payments."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, string_key
from ..a3_credibility.constants import (
    BUCKET08_BASELINE_MONTHS,
    CYCLE_MAX_DAYS,
    FLOOR_LOOKBACK_DAYS,
)

_LADDER = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]


def _nonzero(col: str):
    """Way4 writes an empty bucket as 0, not NULL."""
    return F.col(col).isNotNull() & (F.col(col) != 0.0)


def _balance_dues(balance: DataFrame) -> DataFrame:
    """``(account_id, cycle_start, billed_amount, due_amount)`` per statement.

    One month's due: the oldest open bucket 07..01, else the minimum due (bucket 08 is
    Way4's accumulator, not one month). Once only bucket 08 holds money, ``due_amount``
    is the average positive minimum due of the 12 months before that point (D-A3-12);
    ``billed_amount`` (Dimension C) has no such fallback.
    """
    rows = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("cycle_start"),
        "minimum_due",
        F.coalesce(*[F.when(_nonzero(c), F.col(c)) for c in _LADDER]).alias(
            "billed_amount"
        ),
        (
            ~F.coalesce(
                *[F.when(_nonzero(c), F.lit(True)) for c in _LADDER], F.lit(False)
            )
            & _nonzero("overdue_bucket_08")
        ).alias("_stagnated"),
    )
    since = (
        rows.where("_stagnated")
        .groupBy("account_id")
        .agg(F.min("cycle_start").alias("_since"))
    )
    recent = Window.partitionBy("account_id").orderBy(F.col("_month").desc())
    baseline = (
        rows.join(since, "account_id")
        .where(_nonzero("minimum_due") & (F.col("cycle_start") < F.col("_since")))
        .groupBy("account_id", F.trunc("cycle_start", "month").alias("_month"))
        .agg(F.avg("minimum_due").alias("_m"))
        .withColumn("_r", F.row_number().over(recent))
        .where(F.col("_r") <= BUCKET08_BASELINE_MONTHS)
        .groupBy("account_id")
        .agg(F.avg("_m").alias("_baseline"))
    )
    return rows.join(baseline, "account_id", "left").select(
        "account_id",
        "cycle_start",
        "billed_amount",
        F.coalesce(
            "billed_amount", F.when(F.col("_stagnated"), F.col("_baseline"))
        ).alias("due_amount"),
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
    start, end = F.col("observation_date").cast("date"), F.col(
        "next_billing_date"
    ).cast("date")
    floor = F.date_sub(F.lit(str(history_floor_date)).cast("date"), FLOOR_LOOKBACK_DAYS)
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
