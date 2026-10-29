"""RL-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, lookback_floor, pit_latest, require_columns

# int_loan_master is a month-end snapshot; none in the observation month means no anchor.
_LOAN_MAX_AGE_M = 1


def build_rl_liquidity_anchor(
    obs_base: DataFrame, int_loan_master: DataFrame
) -> DataFrame:
    """One EMI — ``installment_due_amount`` on the loan's snapshot in the observation
    month. NULL (flat floors) when the snapshot is missing or the EMI is not positive.
    """
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "installment_due_amount"],
        "int_loan_master",
    )
    since = lookback_floor(obs_base, _LOAN_MAX_AGE_M)
    src = int_loan_master.filter(F.col("observation_date") >= F.lit(since)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("installment_due_amount").cast("double").alias("emi"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["emi"],
        inclusive=True,
        max_age_months=_LOAN_MAX_AGE_M,
    )
    return latest.select(
        *GRAIN, F.when(F.col("emi") > 0, F.col("emi")).alias("liquidity_anchor_amt")
    )
