"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from enbd_collections.nodes.utils.location import is_travel
from pyspark.sql import Column, DataFrame, Window
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
_CARD_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "value_date",
    "edp_load_date",
    "tran_dc",
    "channel_desc",
    "merchant_type_desc",
    "tran_particular_code_desc",
    "reason_for_excluding",
    "merchant_category",
    "merchant_name",
    "merchant_country",
    "counter_party_bank_cntry",
    "tran_narration_1",
    "actual_tran_amt_aed",
]

POS, ATM = "Point of Sale", "ATM Transactions"
# Card-present POS rows (Offline until ~2025-08, Machine since); Online = e-commerce.
IN_PERSON_POS_TYPES = ("Machine", "Offline")
# ATM cash withdrawals; the other ATM rows are fees, balance enquiries and mePay.
_ATM_WITHDRAWAL_CODES = ("DR ATM TRANSACTION", "UAE SWITCH WDL")
# The NI POS settlement sink: not a customer (millions of POS rows a month).
_NON_CUSTOMER_CIFS = ("13339117",)


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _scoped(
    tran_repos: DataFrame,
    columns: Sequence[str],
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``columns`` of the rows loaded and dated from the first day of the last
    ``history_months`` months up to the persona start month."""
    missing = sorted(set(columns) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
    return tran_repos.filter(
        (F.col("edp_load_date") >= F.lit(floor)) & (F.col("tran_date") >= F.lit(floor))
    ).select(*columns)


def _latest_load(df: DataFrame) -> DataFrame:
    """One row per transaction key (the latest ``edp_load_date``), partitioned by
    ``event_month`` (the month of ``tran_date``)."""
    latest_load = Window.partitionBy(*_KEY).orderBy(F.col("edp_load_date").desc())
    return (
        df.withColumn("_rn", F.row_number().over(latest_load))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
        .withColumn(
            "event_month", F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd")
        )
    )


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
    rows = _scoped(
        tran_repos, _RETURN_EVENT_COLUMNS, persona_start_date, history_months
    )
    return _latest_load(
        rows.filter(F.col("reason_for_excluding").isin(*return_reasons))
    )


def _narration_country() -> Column:
    """The two-letter country code an ATM narration ends with (``…:AE#`` or ``… AE``)."""
    narration = F.upper(F.trim(F.col("tran_narration_1")))
    tagged = F.regexp_extract(narration, r":([A-Z]{2})#", 1)
    trailing = F.regexp_extract(narration, r"\s([A-Z]{2})$", 1)
    return F.when(tagged != "", tagged).when(trailing != "", trailing)


def build_card_transactions(
    tran_repos: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """Debit-card rows that can place a customer, for all CIFs, one row per transaction
    key, partitioned by ``event_month``:

    * in-person candidates — POS debits of a card-present type (``merchant_type_desc``
      Machine / Offline) and ATM cash withdrawals;
    * travel purchases — POS debits with a travel MCC or travel keyword, any type
      (online bookings included).

    ``place_country`` is where the row happened: ``merchant_country`` for POS; for ATM
    the narration's country code, else ``counter_party_bank_cntry``. ``place_source``
    names the column used. Which rows count as evidence (reasons, remote MCCs, UAE or
    abroad) is decided downstream; values are kept as they are. Same history and reload
    rule as ``build_return_events``; the NI POS sink CIF is dropped.
    """
    rows = _scoped(tran_repos, _CARD_COLUMNS, persona_start_date, history_months)
    channel = F.col("channel_desc")
    in_person = (
        (channel == POS) & F.col("merchant_type_desc").isin(*IN_PERSON_POS_TYPES)
    ) | (
        (channel == ATM)
        & F.col("tran_particular_code_desc").isin(*_ATM_WITHDRAWAL_CODES)
    )
    travel = is_travel(
        F.col("merchant_category"), F.col("merchant_name"), F.col("tran_narration_1")
    )
    cards = rows.filter(
        (F.col("tran_dc") == "D")
        & (in_person | ((channel == POS) & travel))
        & ~F.col("cif_id").cast("string").isin(*_NON_CUSTOMER_CIFS)
    )
    code = _narration_country()
    bank = F.col("counter_party_bank_cntry")
    return _latest_load(cards).select(
        "*",
        F.when(channel == POS, F.col("merchant_country"))
        .otherwise(F.coalesce(code, bank))
        .alias("place_country"),
        F.when(
            (channel == POS) & F.col("merchant_country").isNotNull(), "merchant_country"
        )
        .when((channel == ATM) & code.isNotNull(), "narration")
        .when((channel == ATM) & bank.isNotNull(), "counter_party_bank")
        .alias("place_source"),
    )
