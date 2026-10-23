"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared engine in ``_a1``.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns

_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 9)]
# A balance snapshot older than this means the card stopped reporting; no anchor then.
_BALANCE_MAX_AGE_D = 31


def build_cc_liquidity_anchor(obs_base: DataFrame, prm_balance: DataFrame) -> DataFrame:
    """Oldest unpaid overdue bucket on the latest balance snapshot at or before the
    observation date.

    Buckets fill from 01 upward as the account ages, so the highest non-zero bucket is
    the longest-aged unpaid amount — what the customer must find to stop the roll.
    """
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_days=_BALANCE_MAX_AGE_D,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
