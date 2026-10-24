"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from datetime import date
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


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def build_return_events(
    tran_repos: DataFrame,
    return_reasons: Sequence[str],
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Returned CASA transactions (every ``return_reasons`` value, both debit and credit
    legs) for all CIFs, one row per transaction key, partitioned by ``event_month``.

    Covers the last ``history_months`` calendar months up to and including the persona
    start month, and everything after it; each run rebuilds the whole table. A reload of
    the same transaction in a later ``edp_load_date`` keeps the latest load.
    """
    missing = sorted(set(_RETURN_EVENT_COLUMNS) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
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
