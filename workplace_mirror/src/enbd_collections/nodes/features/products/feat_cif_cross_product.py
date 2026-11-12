"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1 engine
can leave out the scored account itself. The WM asset sources are per customer, not per
account: their rows carry the fixed ids ``ASSET_IDS`` (they never equal a spine account).
Supplementary cards post to their contract and never appear as a product of their own; a
card that a newer card replaced is left out, so the scored card's predecessor is not
"another card". CASA balances are never a product here (they are A1's money held,
``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    months_back,
    require_columns,
    wm_month,
)

PRODUCT_TYPES = ("deposit", "investment", "wm", "card", "loan")
COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the month's
    last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series; a
    balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: a live contract (not replaced by a newer one) with a billing row in
    the month; current = billing level at most ``CARD_CURRENT_MAX_LEVEL``; the instalment
    is the month's minimum due."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    replaced = card_contracts.select(
        F.col("parent_contract_id").alias("contract_id")
    ).distinct()
    live = card_contracts.join(replaced, "contract_id", "left_anti")
    return card_month_end.join(
        live.select("cif_id", "contract_id"), "contract_id"
    ).select(
        "cif_id",
        "month_end",
        F.col("contract_id").cast("string").alias("product_account_id"),
        F.lit("card").alias("product_type"),
        _null("double").alias("balance_aed"),
        (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
        F.col("minimum_due").alias("instalment_aed"),
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days and
    not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the first of the last ``history_months`` months up to the persona
    start month on, for all customers (the persona scope is applied by the A1 engine's
    join on the observation base). The primaries are already bounded to that window by
    ``product_primary`` (same parameter).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = months_back(persona_start_date, history_months - 1)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
