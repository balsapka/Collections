"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per card contract and span ``[valid_from,
  valid_to)`` over which its client and that client's CIF held (point in time: a
  contract that moved client, or whose client's CIF changed, has one row per owner;
  NULL ``valid_from`` = from the first record, NULL ``valid_to`` = still current), with
  ``parent_contract_id`` (Way4's linked contract, which stays live beside it; NULL for
  none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row
  in the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 =
  not overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off
  date.

All customers, from ``history_floor(persona_start_date, history_months)`` on; values as
in the source (which level or bucket is "current" is decided by the consumers). The
spine-scoped ``prm_contract`` / ``prm_balance`` hold only the model's own accounts, so
they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from functools import reduce

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import (
    history_floor,
    require_columns,
    string_key,
)

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _load_bound(floor: datetime.date) -> datetime.date:
    """The ``edp_load_date`` bound that covers the month of ``floor`` (load lag)."""
    return floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str, value: str) -> DataFrame:
    """``key``, ``month_end`` (the month end of ``day``) and ``value`` of each ``key``'s
    latest ``day`` row per month; two rows on that day: the larger ``value``."""
    return (
        df.groupBy(key, F.last_day(day).alias("month_end"))
        .agg(F.max(F.struct(day, value)).alias("_latest"))
        .select(key, "month_end", F.col(f"_latest.{value}").alias(value))
    )


def _versions(df: DataFrame, key: str, start: str, values: list[str]) -> DataFrame:
    """``key``, ``values``, ``valid_from``, ``valid_to``: one row per change of
    ``values`` in a Way4 change log, ordered by ``start`` (the version's valid-from day;
    on one day the latest ``edp_modifiedts`` wins). The first version is open at the start
    (``valid_from`` NULL), the last at the end (``valid_to`` NULL)."""
    latest = (
        df.groupBy(key, F.col(start).cast(DateType()).alias("_from"))
        .agg(F.max(F.struct("edp_modifiedts", *values)).alias("_v"))
        .select(key, "_from", *(F.col(f"_v.{c}").alias(c) for c in values))
    )
    order = Window.partitionBy(key).orderBy("_from")
    first = F.row_number().over(order) == 1
    same = reduce(
        lambda x, y: x & y, (F.lag(c).over(order).eqNullSafe(F.col(c)) for c in values)
    )
    return (
        latest.withColumn("_change", first | ~same)
        .filter("_change")
        .select(
            key,
            *values,
            F.when(~first, F.col("_from")).alias("valid_from"),
            F.lead("_from").over(order).alias("valid_to"),
        )
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id``, ``valid_from``, ``valid_to``
    of every card contract whose client is known (``ident_number`` is the CIF), point
    in time: the contract's client from the contract log (``record_date_from``), that
    client's CIF from the client log (``edp_effectivestartdate``); each row is a span
    where both held."""
    require_columns(
        client,
        ["client_idt", "ident_number", "edp_effectivestartdate", "edp_modifiedts"],
        "raw_stg_client",
    )
    require_columns(
        contract,
        [
            "contract_idt",
            "client_idt",
            "parent_contract_idt",
            "record_date_from",
            "edp_modifiedts",
        ],
        "raw_stg_contract",
    )
    owner = _versions(
        contract,
        "contract_idt",
        "record_date_from",
        ["client_idt", "parent_contract_idt"],
    ).alias("o")
    cif = _versions(
        client.withColumn("cif_id", string_key(client, "ident_number")),
        "client_idt",
        "edp_effectivestartdate",
        ["cif_id"],
    ).alias("c")

    def before(start: str, end: str) -> Column:
        """``start`` < ``end``, a NULL bound being open."""
        return F.col(start).isNull() | F.col(end).isNull() | (F.col(start) < F.col(end))

    overlaps = before("o.valid_from", "c.valid_to") & before(
        "c.valid_from", "o.valid_to"
    )
    return owner.join(
        cif, (F.col("o.client_idt") == F.col("c.client_idt")) & overlaps
    ).select(
        "c.cif_id",
        F.col("o.contract_idt").cast("long").alias("contract_id"),
        F.col("o.parent_contract_idt").cast("long").alias("parent_contract_id"),
        F.greatest("o.valid_from", "c.valid_from").alias("valid_from"),
        F.least("o.valid_to", "c.valid_to").alias("valid_to"),
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
    return _latest_in_month(rows, "contract_id", "billing_date", "level")


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot
    in the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the
    repo's own minimum-due derivation)."""
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
    return (
        _latest_in_month(amounts, "contract_idt", "banking_date", "minimum_due")
        .withColumnRenamed("contract_idt", "contract_id")
        .withColumn("minimum_due", F.col("minimum_due").cast("double"))
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card
    contract with a billing row in the month."""
    floor = history_floor(persona_start_date, history_months)
    lo = _load_bound(floor)
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
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``,
    ``overdue_days``, ``instalment_due_aed`` and ``write_off_date`` of every monthly
    loan snapshot."""
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
    floor = history_floor(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        string_key(loan_portfolio, "cust_num").alias("cif_id"),
        string_key(loan_portfolio, "acct_num").alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
