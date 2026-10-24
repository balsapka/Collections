"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_KEY = ["tran_id", "part_tran_srl_num", "tran_date"]
_RETURN_EVENT_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "reason_for_excluding",
    "tran_dc",
    "main_tran_type",
    "tran_type",
    "tran_sub_type",
    "channel_tran_type",
    "tran_particular_code",
    "tran_amt",
    "tran_amt_aed",
    "edp_load_date",
]


def build_return_events(
    tran_repos: DataFrame,
    return_reasons: Sequence[str],
    rebuild_from: str | date | None,
) -> DataFrame:
    """Returned CASA transactions (every ``return_reasons`` value, both debit and credit
    legs) for all CIFs, one row per transaction key, partitioned by ``event_month``.

    Incremental: only event months from ``rebuild_from`` (a date, taken at its month
    start) are rebuilt, and the catalog overwrites just those partitions. Without it, the
    run rebuilds the previous and the current month. A reload of the same transaction in
    a later ``edp_load_date`` keeps the latest load.
    """
    missing = sorted(set(_RETURN_EVENT_COLUMNS) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    if rebuild_from:
        floor = date.fromisoformat(str(rebuild_from)).replace(day=1)
    else:  # the previous month's start
        floor = (date.today().replace(day=1) - timedelta(days=1)).replace(day=1)
    latest_load = Window.partitionBy(*_KEY).orderBy(F.col("edp_load_date").desc())
    return (
        tran_repos.filter(
            (F.col("edp_load_date") >= F.lit(floor))
            & (F.col("tran_date") >= F.lit(floor))
            & F.col("reason_for_excluding").isin(*return_reasons)
        )
        .select(*_RETURN_EVENT_COLUMNS)
        .withColumn("_rn", F.row_number().over(latest_load))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
        .withColumn(
            "event_month", F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd")
        )
    )
