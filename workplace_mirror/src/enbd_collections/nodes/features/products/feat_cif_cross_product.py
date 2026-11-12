"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets: deposits, investments, WM; NULL for
  credit products, and for a term-deposit holder without a balance snapshot);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 id for cards, ``acct_num`` for loans), so the A1 engine
can leave out the scored account itself. The asset sources are per customer, not per
account: their rows carry the fixed ids ``ASSET_IDS`` (they never equal a spine account).
Supplementary cards post to their contract and never appear as a product of their own;
a card that a newer card replaced (``parent_contract_idt``) is left out, so the scored
card's predecessor is not "another card". CASA balances are never a product here (they
are A1's money held, ``feat_cif_casa_balance_monthly``).

Sources (the ones the round-3 F4 builder loaded): ``wm_fea_casa_eod_avg_balance``
(``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the CASA columns are never read),
``wm_fea_wealth_holdings_by_cif`` (``etw_total_market_value_aed``),
``feat_product_holding`` (term-deposit holders), ``bo_rr_portf_actv_acct_mthly`` (loans)
and the raw Way4 client / contract / billing / balance / account-group tables (cards:
``derive_billing_amounts`` is the repo's own minimum-due derivation).
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    _cif,
    _require,
    _wm_month,
    months_back,
)
from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts

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
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (CC code: 1 = not overdue)
BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _wm_last_week(df: DataFrame, columns: list[str], floor) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the month's
    last week, from the month of ``floor`` on."""
    return (
        df.filter(_wm_month() >= F.lit(floor))
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(
            *[
                F.max(
                    F.struct(
                        F.col("week_number").cast("string").alias("w"),
                        F.col(c).cast("double").alias("v"),
                    )
                )["v"].alias(c)
                for c in columns
            ]
        )
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series; a
    balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    none = F.lit(None)
    return (
        series.filter(F.col(column) > 0)
        .select(
            "cif_id",
            "month_end",
            F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
            F.lit(product_type).alias("product_type"),
            F.col(column).alias("balance_aed"),
            none.cast("int").alias("is_current"),
            none.cast("double").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def _wm_assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    _require(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    _require(
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


def _term_deposit_holders(product_holding: DataFrame, floor) -> DataFrame:
    """``deposit`` rows without a balance for the months ``feat_product_holding`` counts a
    term deposit (``month_number`` = ``yyyyMMdd``): the holding is known, the amount is
    not."""
    _require(
        product_holding,
        ["cif_id", "month_number", "term_deposits_total_active_accounts"],
        "feat_product_holding",
    )
    month_end = F.last_day(F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"))
    holders = (
        product_holding.filter(F.col("term_deposits_total_active_accounts") > 0)
        .select(_cif(), month_end.alias("month_end"))
        .filter(F.col("month_end") >= F.lit(floor))
        .distinct()
    )
    none = F.lit(None)
    return holders.select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS["deposit"]).alias("product_account_id"),
        F.lit("deposit").alias("product_type"),
        none.cast("double").alias("balance_aed"),
        none.cast("int").alias("is_current"),
        none.cast("double").alias("instalment_aed"),
    )


def _loans(loan_portfolio: DataFrame, floor) -> DataFrame:
    """``loan`` rows: every retail loan in the monthly portfolio snapshot; current = bucket
    0, no overdue days and not written off, the instalment is the one due."""
    columns = [
        "cust_num",
        "acct_num",
        "ss_dt",
        "ra_delq_bkt",
        "ra_ovd_days",
        "ra_instl_due_amt",
        "ra_woff_dt",
    ]
    _require(loan_portfolio, columns, "bo_rr_portf_actv_acct_mthly")
    overdue = F.coalesce(F.col("ra_ovd_days").cast("double"), F.lit(0.0))
    current = (
        (F.col("ra_delq_bkt").cast("int") == 0)
        & (overdue <= 0)
        & F.col("ra_woff_dt").isNull()
    )
    return (
        loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor))
        .select(
            F.col("cust_num").cast("string").alias("cif_id"),
            F.last_day(F.to_date("ss_dt")).alias("month_end"),
            F.trim(F.col("acct_num").cast("string")).alias("product_account_id"),
            F.lit("loan").alias("product_type"),
            F.lit(None).cast("double").alias("balance_aed"),
            current.cast("int").alias("is_current"),
            F.col("ra_instl_due_amt").cast("double").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def _card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id, contract_id, parent_id`` of every card contract (``ident_number`` is the
    CIF); a contract that a newer one replaced is left out."""
    _require(client, ["client_idt", "ident_number"], "raw_stg_client")
    _require(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", F.trim(F.col("ident_number").cast("string")).alias("cif_id")
    ).distinct()
    contracts = (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_id"),
        )
        .distinct()
    )
    replaced = contracts.select(F.col("parent_id").alias("contract_id")).distinct()
    return contracts.join(replaced, "contract_id", "left_anti")


def _card_levels(billing: DataFrame, contracts: DataFrame, lo) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    _require(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = (
        billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_id", F.col("contract_idt").cast("long"))
        .join(F.broadcast(contracts.select("contract_id")), "contract_id", "left_semi")
        .select(
            "contract_id",
            F.col("billing_date").cast(DateType()).alias("bdate"),
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
            .cast("int")
            .alias("level"),
        )
        .withColumn("month_end", F.last_day("bdate"))
    )
    latest = Window.partitionBy("contract_id", "month_end").orderBy(
        F.col("bdate").desc()
    )
    return (
        rows.withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .select("contract_id", "month_end", "level")
    )


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, contracts: DataFrame, lo
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot in
    the last ``BALANCE_TAIL_DAYS`` days of the month."""
    _require(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(
            F.broadcast(contracts.select(F.col("contract_id").alias("contract_idt"))),
            "contract_idt",
            "left_semi",
        )
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    latest = Window.partitionBy("contract_idt", F.last_day("banking_date")).orderBy(
        F.col("banking_date").desc()
    )
    return (
        amounts.withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("contract_idt").alias("contract_id"),
            F.last_day("banking_date").alias("month_end"),
            F.col("minimum_due").cast("double").alias("min_due"),
        )
    )


def _cards(
    client: DataFrame,
    contract: DataFrame,
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    floor,
) -> DataFrame:
    """``card`` rows: a contract with a billing row in the month; current = billing level
    at most ``CARD_CURRENT_MAX_LEVEL``; the instalment is the month's minimum due."""
    lo = floor - datetime.timedelta(days=LOAD_LAG_DAYS)
    contracts = _card_contracts(client, contract)
    month = _card_levels(billing, contracts, lo).join(
        _card_minimum_due(balance, account_group, contracts, lo),
        ["contract_id", "month_end"],
        "left",
    )
    return (
        month.filter(F.col("month_end") >= F.lit(floor))
        .join(contracts.select("cif_id", "contract_id"), "contract_id")
        .select(
            "cif_id",
            "month_end",
            F.col("contract_id").cast("string").alias("product_account_id"),
            F.lit("card").alias("product_type"),
            F.lit(None).cast("double").alias("balance_aed"),
            (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
            F.col("min_due").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def build(
    product_holding: DataFrame,
    loan_portfolio: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    card_client: DataFrame,
    card_contract: DataFrame,
    card_billing: DataFrame,
    card_balance: DataFrame,
    card_account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the first of the last ``history_months`` months up to the persona
    start month on, for all customers (the persona scope is applied by the A1 engine's
    join on the observation base).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = months_back(persona_start_date, history_months - 1)
    deposits, investments, wm = _wm_assets(wm_balances, wm_holdings, floor)
    holders = _term_deposit_holders(product_holding, floor).join(
        deposits.select("cif_id", "month_end"), ["cif_id", "month_end"], "left_anti"
    )
    cards = _cards(
        card_client,
        card_contract,
        card_billing,
        card_balance,
        card_account_group,
        floor,
    )
    parts = [deposits, investments, wm, holders, _loans(loan_portfolio, floor), cards]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
