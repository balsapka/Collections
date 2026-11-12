"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per ``(cif_id, contract_id)``: every Way4 card contract
  of a client, with ``parent_contract_id`` (the contract a newer one replaced; NULL for
  none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row in
  the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 = not
  overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off date.

All customers, from the first of the last ``history_months`` months up to the persona
start month on; values as in the source (which level or bucket is "current" is decided
by the consumers). The spine-scoped ``prm_contract`` / ``prm_balance`` hold only the
model's own accounts, so they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import months_back, require_columns

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _window(persona_start_date: str, history_months: int) -> tuple:
    """The first month kept and the ``edp_load_date`` bound that covers it."""
    floor = months_back(persona_start_date, history_months - 1)
    return floor, floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str) -> DataFrame:
    """``df`` with ``month_end`` = the month end of ``day``, keeping each ``key``'s latest
    ``day`` row per month."""
    month_end = F.last_day(day)
    latest = Window.partitionBy(key, month_end).orderBy(F.col(day).desc())
    return (
        df.withColumn("month_end", month_end)
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id`` of every card contract whose
    client is known (``ident_number`` is the CIF)."""
    require_columns(client, ["client_idt", "ident_number"], "raw_stg_client")
    require_columns(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", F.trim(F.col("ident_number").cast("string")).alias("cif_id")
    ).distinct()
    return (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_contract_id"),
        )
        .distinct()
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date").select(
        "contract_id", "month_end", "level"
    )


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot in
    the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the repo's
    own minimum-due derivation)."""
    require_columns(
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
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return _latest_in_month(amounts, "contract_idt", "banking_date").select(
        F.col("contract_idt").alias("contract_id"),
        "month_end",
        F.col("minimum_due").cast("double").alias("minimum_due"),
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card contract
    with a billing row in the month."""
    floor, lo = _window(persona_start_date, history_months)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``, ``overdue_days``,
    ``instalment_due_aed`` and ``write_off_date`` of every monthly loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor, _ = _window(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        F.col("cust_num").cast("string").alias("cif_id"),
        F.trim(F.col("acct_num").cast("string")).alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
