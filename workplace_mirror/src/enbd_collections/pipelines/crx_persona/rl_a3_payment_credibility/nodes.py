"""RL A3 sources: months with the EMI, and the month's cash (``int_loan_master``)."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, scoped, string_key


def _months(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """The latest snapshot of each month for the base's loans."""
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "monthly_emi_due", "total_paid"],
        "int_loan_master",
    )
    rows = int_loan_master.select(
        string_key(int_loan_master).alias("account_id"),
        F.col("observation_date").cast("date").alias("_d"),
        F.col("monthly_emi_due").cast("double").alias("emi"),
        F.col("total_paid").cast("double").alias("paid"),
    )
    latest = F.max(F.struct("_d", "emi", "paid"))
    return (
        scoped(rows, obs_base, "account_id")
        .groupBy("account_id", F.last_day("_d").alias("month_end"))
        .agg(latest["emi"].alias("emi"), latest["paid"].alias("paid"))
    )


def build_rl_a3_dues(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """A3 dues contract per month: the due and the billed amount are the month's EMI,
    else the last known one (D-A3-13)."""
    asof = (
        Window.partitionBy("account_id")
        .orderBy("month_end")
        .rowsBetween(Window.unboundedPreceding, 0)
    )
    emi = F.last("emi", ignorenulls=True).over(asof)
    return _months(int_loan_master, obs_base).select(
        "account_id",
        F.last_day(F.add_months("month_end", -1)).alias("cycle_start"),
        F.col("month_end").alias("cycle_end"),
        emi.alias("due_amount"),
        emi.alias("billed_amount"),
    )


def build_rl_a3_payments(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """A3 payments contract: the month's cash (``total_paid``), known only to the month:
    it arrived some day between the first and the last day of the month."""
    return (
        _months(int_loan_master, obs_base)
        .where(F.col("paid") > 0)
        .select(
            "account_id",
            F.trunc("month_end", "month").alias("pay_from"),
            F.col("month_end").alias("pay_date"),
            F.col("paid").alias("amount"),
        )
    )
