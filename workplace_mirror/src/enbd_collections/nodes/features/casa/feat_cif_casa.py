"""Feature nodes: monthly CASA features per customer, all customers.

Each table has one row per ``(cif_id, month_end)`` (plus ``lane`` / ``reason`` where
named) with any data; customers are CIFs, so every CASA account of the customer counts.
The FTR-based tables keep only legs on current and savings accounts (``prm_casa_accounts``):
the transaction table also holds the loan account itself. Values are raw: which lanes,
reasons or amounts count is decided by the consumers.

* ``feat_cif_internal_salary_monthly``  - salary credited with us per month (WM);
* ``feat_cif_casa_balance_monthly``     - CASA average balance and any flow per month (WM);
* ``feat_cif_casa_activity_monthly``    - transaction legs per month and lane (FTR);
* ``feat_cif_ext_card_payment_monthly`` - payments to registered external cards (WM);
* ``feat_cif_returns_monthly``          - returned-transaction events per reason (FTR);
* ``prm_casa_flow_legs``                - the classified CASA legs, saved so the flows node
  starts from them (FTR + WM labels);
* ``feat_cif_casa_flows_monthly``       - CASA money in / out per month and flow class from
  those legs (A1 evidence: ``FLOW_CLASSES``).

WM weekly tables carry ``week_number`` as ``yyyyMM0W`` (week 01-04 of the month).
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

_CASA_BALANCE = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"

# Transaction lanes (FTR row-handling reference), assigned in this order: a leg takes the
# first lane it matches.
SIGNAL_REASONS = ("DDS Rejects/Reversal", "CHEQUE RETURNS")
_FEE_TYPES = ("CHARGES", "FEES", "INTEREST PAID", "INTEREST COLLECTION")
_NOISE_REASONS = ("CHARGES", "FEES", "REVERSAL", "CANCELLED")
_GROUP_REASONS = ("SUBSIDIARIES EXCLUSION", "INTERNAL TRANSFER - LIV")
_AUTO_SAVE_CODES = ("LV95", "LV3")
_AMBIGUOUS_TYPES = ("MISCELLANEOUS", "MC/DD", "MC/DD-ISSUE", "STANDING INSTRUCTIONS")
_ECONOMIC_TYPES = (
    "INWARD REMITTANCE",
    "OUTWARD REMITTANCE",
    "INTERNAL TRANSFER - OTHERS",
    "CASH DEPOSIT",
    "CASH WITHDRAWALS",
    "INWARD CLEARING",
    "OUTWARD CLEARING",
    "BILL PAYMENTS",
)
LANES = (
    "signal",  # DDS rejects, cheque returns
    "refund",  # POS refunds (reason RETURNS)
    "card_spend",  # POS debits
    "card_payment",  # payments to the customer's own credit card
    "wash",  # transfers between the customer's own accounts, auto-save
    "fee_interest",
    "reversal",  # reversals, cancellations
    "group_internal",  # group subsidiaries, Liv
    "own_loan",  # the bank recovering the customer's own loan instalment
    "ambiguous",  # the rest of MISCELLANEOUS and the tiny instruction types
    "economic",  # remittances, transfers to others, cash, clearing, bill payments
    "unclassified",
)


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def _wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def _wm_week_date(week_number: str = "week_number") -> Column:
    """The middle of week W of the month (day 4, 11, 18 or 25): within 4 days of any
    day of that week."""
    week = F.substring(F.col(week_number).cast("string"), 7, 2).cast("int")
    return F.date_add(_wm_month(week_number), 7 * week - 4)


def _cif() -> Column:
    return F.col("cif_id").cast("string").alias("cif_id")


def build_internal_salary(wm_salary: DataFrame) -> DataFrame:
    """``salary``: the month's total of salary-flagged credits with us, recovered from
    every weekly snapshot of ``wm_fea_salary_days_since_increment`` (all history).

    Each snapshot carries the latest salary month's total and the days from the first of
    that month to the snapshot; the snapshot's week date minus those days lands within a
    few days of the first of the salary month, so it is rounded to the nearest first.
    Snapshots that see the same month collapse to its largest total.
    """
    _require(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credited = F.date_sub(
        _wm_week_date(), F.col("ft_days_since_salary_transaction").cast("int")
    )
    month = F.trunc(F.date_add(credited, 15), "month")  # nearest first of a month
    return (
        wm_salary.filter(
            (F.col("ft_last_salary_amount") > 0)
            & F.col("ft_days_since_salary_transaction").isNotNull()
        )
        .groupBy(_cif(), F.last_day(month).alias("month_end"))
        .agg(F.max(F.col("ft_last_salary_amount").cast("double")).alias("salary"))
    )


def build_casa_balance(
    wm_casa_balance: DataFrame,
    wm_casa_flow: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``casa_balance``: the 4-week CASA (current + savings) average at the month's last
    weekly snapshot; ``casa_flow``: 1 when any week of the month has an inflow or outflow.
    From the first of the last ``history_months`` months up to the persona start month on.
    """
    _require(
        wm_casa_balance,
        ["cif_id", "week_number", _CASA_BALANCE],
        "wm_fea_casa_eod_avg_balance",
    )
    _require(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN, _CASA_OUT],
        "wm_fea_casa_cc_inflow_outflow",
    )
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    last_week = F.max(
        F.struct(
            F.col("week_number").cast("string").alias("w"),
            F.col(_CASA_BALANCE).cast("double").alias("v"),
        )
    )
    balance = (
        wm_casa_balance.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(last_week.alias("_last"))
        .select("cif_id", "month_end", F.col("_last.v").alias("casa_balance"))
    )
    moved = (F.col(_CASA_IN) > 0) | (F.col(_CASA_OUT) > 0)
    flow = (
        wm_casa_flow.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(F.max(moved.cast("int")).alias("casa_flow"))
    )
    return balance.join(flow, on=["cif_id", "month_end"], how="full")


def transaction_lane() -> Column:
    """The lane of a ``prm_casa_transactions`` leg (``LANES``).

    Signal rows first; card rows before the reason rules, because the bank's reason flag
    also marks own-card payments; then noise, own-loan recovery, ambiguous and economic
    types. Types are compared exactly, after upper-casing and collapsing spaces.
    """
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    reason = F.trim("reason_for_excluding")
    debit = F.col("tran_dc") == "D"
    narration = F.upper(F.trim("tran_narration_1"))
    noise_reason = F.coalesce(reason.isin(*_NOISE_REASONS), F.lit(False))
    return (
        F.when(reason.isin(*SIGNAL_REASONS) | (t == "CHEQUE RETURNS"), "signal")
        .when(reason == "RETURNS", "refund")
        .when((t == "POS TRANSACTIONS") & debit & ~noise_reason, "card_spend")
        .when(t == "CREDIT CARD PAYMENTS", "card_payment")
        .when(
            (t == "INTERNAL TRANSFER - SELF")
            | F.col("tran_particular_code").isin(*_AUTO_SAVE_CODES)
            | (reason == "INTERNAL TRANSFER - SELF"),
            "wash",
        )
        .when(reason.isin("CHARGES", "FEES") | t.isin(*_FEE_TYPES), "fee_interest")
        .when(reason.isin("REVERSAL", "CANCELLED") | (t == "REVERSAL"), "reversal")
        .when(
            reason.isin(*_GROUP_REASONS) | t.endswith("- SUBSIDIARIES"),
            "group_internal",
        )
        .when(
            (t == "MISCELLANEOUS") & narration.startswith("INSTL_RECOVERY"), "own_loan"
        )
        .when(t.isin(*_AMBIGUOUS_TYPES), "ambiguous")
        .when(t.isin(*_ECONOMIC_TYPES), "economic")
        .otherwise("unclassified")
    )


def _on_casa_accounts(legs: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """The legs whose ``foracid`` is a current or savings account."""
    _require(casa_accounts, ["foracid"], "prm_casa_accounts")
    accounts = casa_accounts.select("foracid").distinct()
    return legs.withColumn("foracid", F.trim(F.col("foracid").cast("string"))).join(
        accounts, on="foracid", how="leftsemi"
    )


def build_casa_activity(transactions: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, lane)``: ``legs`` and the credit / debit AED of the
    ``prm_casa_transactions`` legs on CASA accounts (its whole history)."""
    _require(
        transactions,
        [
            "cif_id",
            "foracid",
            "tran_date",
            "tran_dc",
            "tran_type",
            "reason_for_excluding",
            "tran_particular_code",
            "tran_narration_1",
            "actual_tran_amt_aed",
        ],
        "prm_casa_transactions",
    )
    amount = F.col("actual_tran_amt_aed").cast("double")
    return (
        _on_casa_accounts(transactions, casa_accounts)
        .withColumn("lane", transaction_lane())
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"), "lane")
        .agg(
            F.count(F.lit(1)).alias("legs"),
            F.sum(F.when(F.col("tran_dc") == "C", amount)).alias("credit_aed"),
            F.sum(F.when(F.col("tran_dc") == "D", amount)).alias("debit_aed"),
        )
    )


def build_ext_card_payments(
    labelled: DataFrame,
    beneficiary_cards: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``max_payment`` / ``payments``: CASA payments to a card registered as a payment
    beneficiary (``prm_beneficiary_cards``; an external card) per month, from
    ``wm_pri_labelled_transactions``.

    The beneficiary list is a current snapshot: a card registered later still counts
    (a mild look-ahead, accepted).
    """
    _require(
        labelled,
        [
            "cif_id",
            "in_out_flow",
            "product_category",
            "tran_date",
            "tran_amt",
            "transaction_acid",
        ],
        "wm_pri_labelled_transactions",
    )
    _require(beneficiary_cards, ["card_number"], "prm_beneficiary_cards")
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    cards = beneficiary_cards.select(F.col("card_number").alias("transaction_acid"))
    return (
        labelled.filter(
            (F.to_date("tran_date") >= floor)
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"))
        .agg(
            F.max(F.col("tran_amt").cast("double")).alias("max_payment"),
            F.count(F.lit(1)).alias("payments"),
        )
    )


def build_returns(return_events: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """``events``: returned transactions on CASA accounts per ``(cif_id, month_end,
    reason)`` from ``prm_casa_return_events`` - one event per ``(tran_id, tran_date)``, so
    the debit and credit legs of a return count once."""
    _require(
        return_events,
        ["cif_id", "foracid", "tran_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    one_event = Window.partitionBy("cif_id", "tran_id", "tran_date")
    return (
        _on_casa_accounts(return_events, casa_accounts)
        .select(
            _cif(),
            "tran_id",
            F.to_date("tran_date").alias("tran_date"),
            F.trim("reason_for_excluding").alias("reason"),
        )
        .withColumn("_rn", F.row_number().over(one_event.orderBy("reason")))
        .filter(F.col("_rn") == 1)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "reason")
        .agg(F.count(F.lit(1)).alias("events"))
    )


def _flag(column: str) -> Column:
    """A WM 0 / 1 flag column as an int, 0 when NULL."""
    return F.coalesce(F.col(column).cast("int"), F.lit(0))


# — Flow classes (A1 money in / out, specs/A1_ability_family_rule.md §3) ──────────
# A leg counts as evidence only in a class that is positively identified; every other
# leg is a class that does not count. Assigned in this order: a leg takes the first
# class it matches.
FLOW_CLASSES = (
    "salary",  # salary-flagged credit (WM): income (F1), not money in
    "reversal_return",  # reversals, returned cheques / DDS, refunds, cheque presentments
    "own_in_external",  # credit from the customer's own account at another bank
    "own_out_external",  # debit to the customer's own account at another bank
    "own_transfer",  # between the customer's accounts with us, auto-save, group
    "bank_initiated",  # fees, interest
    "debt_to_us",  # paying their own card / loan with us (A3)
    "cash_in",  # cash deposits
    "third_party_in",  # transfers, remittances, clearing credits from others
    "chosen_spend",  # POS, ATM, bills, transfers to others
    "unplaced",  # meaning not established (the rest of MISCELLANEOUS, …)
)
MONEY_IN_CLASSES = ("third_party_in", "cash_in", "own_in_external")
MONEY_OUT_CLASSES = ("chosen_spend", "own_out_external")
# Narration stems of cheque returns and the presentments they undo (both legs, round 3:
# 100% mirrored the same day).
_CHEQUE_STEMS = ("CHQ RTN", "CHQ NO")
# WM's label for a transfer between the customer and their own account at another bank:
# ``self_transfer_flag`` = 1 on ``wm_pri_labelled_transactions`` (round-3 ``wm_labels``).
WM_SELF_COLUMN = "self_transfer_flag"
WM_SELF_VALUE = 1
# The other WM flags of the flow dictionary: a fee / charge, a loan payment, and a bank
# counterparty (``bank_transfer`` / ``local_`` / ``international_bank_transfer``).
WM_FEE_COLUMN, WM_LOAN_COLUMN = "fees_charges", "loan_payment_flag"
WM_BANK_COLUMNS = (
    "bank_transfer",
    "local_bank_transfer",
    "international_bank_transfer",
)
WM_LABEL_FLAGS = (WM_FEE_COLUMN, WM_LOAN_COLUMN, *WM_BANK_COLUMNS)
NET_DAYS = 3  # a counted leg mirrored within this many days by a non-evidence leg …
NET_TOLERANCE = 0.01  # … of the same amount (±1%) is dropped (bounce, reversal, sweep)


def flow_class() -> Column:
    """The ``FLOW_CLASSES`` class of a leg carrying ``lane`` (``transaction_lane``) and the
    WM labels ``wm_salary``, ``wm_self``, ``wm_fee``, ``wm_loan`` and ``wm_bank`` (false
    when unlabelled).

    The self label decides ``own_in_external`` / ``own_out_external`` outside the wash lane
    only; on it the lane's ``own_transfer`` stands (round-3 dictionary, lane first).

    Debits only, as in the round-3 flow dictionary: a fee label is ``bank_initiated``; a
    loan-payment label with no other-bank counterparty is ``unplaced`` (the instalment may
    be our own loan)."""
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    narration = F.upper(F.trim("tran_narration_1"))
    credit = F.col("tran_dc") == "C"
    debit = F.col("tran_dc") == "D"
    lane = F.col("lane")
    on_wash_lane = (
        lane == "wash"
    )  # the lane decides first: DDS returns carry the self label
    cheque = F.lit(False)
    for stem in _CHEQUE_STEMS:
        cheque |= F.coalesce(narration.startswith(stem), F.lit(False))
    return (
        F.when(lane.isin("signal", "refund", "reversal") | cheque, "reversal_return")
        .when(credit & F.col("wm_salary"), "salary")
        .when(F.col("wm_self") & credit & ~on_wash_lane, "own_in_external")
        .when(F.col("wm_self") & ~on_wash_lane, "own_out_external")
        .when(lane.isin("wash", "group_internal"), "own_transfer")
        .when(lane == "fee_interest", "bank_initiated")
        .when(lane.isin("card_payment", "own_loan"), "debt_to_us")
        .when(debit & F.col("wm_fee") & ~F.col("wm_salary"), "bank_initiated")
        .when(debit & F.col("wm_loan") & ~F.col("wm_bank"), "unplaced")
        .when(lane == "card_spend", "chosen_spend")
        .when((lane == "economic") & credit & (t == "CASH DEPOSIT"), "cash_in")
        .when((lane == "economic") & credit, "third_party_in")
        .when(lane == "economic", "chosen_spend")
        .otherwise("unplaced")
    )


def _net_mirrored(legs: DataFrame) -> DataFrame:
    """``legs`` without the counted legs (money in / out classes) that an opposite leg of
    a class that does not count mirrors: the same amount within ``NET_TOLERANCE``,
    0-``NET_DAYS`` days apart, on any account of the customer.

    Each non-counted leg is spread over the days it can mirror, so the match is an
    equi-join on customer, day and direction (never all legs of a customer against all).
    """
    counted = F.col("flow_class").isin(*MONEY_IN_CLASSES, *MONEY_OUT_CLASSES)
    days = F.sequence(
        F.date_sub("tran_date", NET_DAYS), F.date_add("tran_date", NET_DAYS)
    )
    mirrors = legs.filter(~counted & (F.col("flow_class") != "salary")).select(
        F.col("cif_id").alias("_cif"),
        F.explode(days).alias("_day"),
        F.when(F.col("tran_dc") == "C", "D")
        .when(F.col("tran_dc") == "D", "C")
        .alias("_dc"),
        F.col("amount").alias("_amt"),
    )
    hit = (
        (F.col("cif_id") == F.col("_cif"))
        & (F.col("tran_date") == F.col("_day"))
        & (F.col("tran_dc") == F.col("_dc"))
        & (F.abs(F.col("_amt") - F.col("amount")) <= NET_TOLERANCE * F.col("amount"))
    )
    mirrored = (
        legs.filter(counted)
        .join(mirrors, hit, "leftsemi")
        .select("cif_id", "tran_id", "tran_date", "tran_dc")
    )
    return legs.join(
        mirrored, on=["cif_id", "tran_id", "tran_date", "tran_dc"], how="left_anti"
    )


_TRANSACTION_COLUMNS = (
    "cif_id",
    "foracid",
    "tran_id",
    "tran_date",
    "tran_dc",
    "tran_type",
    "reason_for_excluding",
    "tran_particular_code",
    "tran_narration_1",
    "actual_tran_amt_aed",
)
_LABEL_KEYS = ["cif_id", "tran_id", "tran_date", "tran_dc"]
_LABEL_COLUMNS = ("_sal", "_self", "_fee", "_loan", "_bank")


def _usable_key(*columns: str) -> Column:
    """True when every column is neither NULL nor blank (NULL when a column is NULL)."""
    usable = F.lit(True)
    for column in columns:
        usable &= F.length(F.trim(F.col(column).cast("string"))) > 0
    return usable


def _flow_labels(labelled: DataFrame, floor_day: date) -> DataFrame:
    """One row per ``(cif_id, tran_id, tran_date, tran_dc)`` of ``wm_pri_labelled_transactions``
    that carries a label the flow classes read, with ``_sal``, ``_self``, ``_fee``,
    ``_loan`` and ``_bank``.

    The table is partitioned by ``week_number`` (``yyyyMM0W``), so a bound on it lets Spark
    skip old partitions (one month of margin: a week can start in the month before its
    ``tran_date``; ``tran_date`` stays the exact filter). Only the key and flag columns are
    read. A row with every flag 0 / NULL would end up unlabelled anyway, so it is dropped
    before the aggregate; so is a group with no salary, self, fee or loan label (a bank
    flag alone changes nothing: it is read only together with the loan label)."""
    direction = F.when(F.lower(F.trim("in_out_flow")) == "inflow", "C").when(
        F.lower(F.trim("in_out_flow")) == "outflow", "D"
    )
    flags = ("salary_txn_flag", WM_SELF_COLUMN, *WM_LABEL_FLAGS)
    keep = ["cif_id", "tran_id", "tran_date", "in_out_flow", *flags]
    has_week = "week_number" in labelled.columns
    labelled = labelled.select(*keep, *(["week_number"] if has_week else []))
    if has_week:
        week_bound = int(months_back(floor_day, 1).strftime("%Y%m")) * 100 + 1
        labelled = labelled.filter(F.col("week_number") >= week_bound)
    carries_label = F.lit(False)
    for column in flags:
        carries_label |= _flag(column) != 0
    carries_label_we_use = (F.col("_sal") == 1) | (F.col("_self") == 1)
    carries_label_we_use |= (F.col("_fee") == 1) | (F.col("_loan") == 1)
    return (
        labelled.filter((F.to_date("tran_date") >= F.lit(floor_day)) & carries_label)
        .groupBy(
            _cif(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            direction.alias("tran_dc"),
        )
        .agg(
            F.max(F.coalesce(F.col("salary_txn_flag").cast("int"), F.lit(0))).alias(
                "_sal"
            ),
            F.max(
                F.coalesce(
                    (F.col(WM_SELF_COLUMN).cast("int") == WM_SELF_VALUE).cast("int"),
                    F.lit(0),
                )
            ).alias("_self"),
            F.max(_flag(WM_FEE_COLUMN)).alias("_fee"),
            F.max(_flag(WM_LOAN_COLUMN)).alias("_loan"),
            F.max(F.greatest(*[_flag(c) for c in WM_BANK_COLUMNS])).alias("_bank"),
        )
        .filter(carries_label_we_use)
    )


def build_casa_flow_legs(
    transactions: DataFrame,
    casa_accounts: DataFrame,
    labelled: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """One row per classified ``prm_casa_transactions`` leg on CASA accounts, from the
    first of the last ``history_months`` months up to the persona start month on:
    ``cif_id``, ``tran_id``, ``tran_date``, ``tran_dc``, ``amount``, ``flow_class`` and
    ``event_month`` (the first of the leg's month, the partition).

    Salary and WM's own-account-elsewhere label come from ``wm_pri_labelled_transactions``
    joined on ``(cif_id, tran_id, tran_date)`` and the direction (``in_out_flow``), as in
    round 3. Saved on its own so the heavy join / classification is read once and a failed
    run restarts from here (``build_casa_flows`` nets and aggregates it)."""
    _require(
        transactions,
        [
            "cif_id",
            "foracid",
            "tran_id",
            "tran_date",
            "tran_dc",
            "tran_type",
            "reason_for_excluding",
            "tran_particular_code",
            "tran_narration_1",
            "actual_tran_amt_aed",
        ],
        "prm_casa_transactions",
    )
    _require(
        labelled,
        [
            "cif_id",
            "tran_id",
            "tran_date",
            "in_out_flow",
            "salary_txn_flag",
            WM_SELF_COLUMN,
            *WM_LABEL_FLAGS,
        ],
        "wm_pri_labelled_transactions",
    )
    floor_day = months_back(persona_start_date, history_months - 1)
    floor = F.lit(floor_day)
    labels = _flow_labels(labelled, floor_day)
    legs = (
        _on_casa_accounts(transactions.select(*_TRANSACTION_COLUMNS), casa_accounts)
        .filter(F.to_date("tran_date") >= floor)
        .withColumn("lane", transaction_lane())
        .select(
            _cif(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            "tran_dc",
            "tran_type",
            "tran_narration_1",
            "lane",
            F.col("actual_tran_amt_aed").cast("double").alias("amount"),
        )
    )
    # A leg without a usable key can never match a label; in the join they would all hash
    # to one partition, so they skip it (every label column NULL = unlabelled).
    usable = _usable_key("cif_id", "tran_id", "tran_dc", "tran_date")
    unkeyed = legs.filter(~F.coalesce(usable, F.lit(False)))
    keyed = legs.filter(F.coalesce(usable, F.lit(False))).join(
        labels, on=_LABEL_KEYS, how="left"
    )
    unkeyed = unkeyed.select(
        *legs.columns,
        *[F.lit(None).cast("int").alias(c) for c in _LABEL_COLUMNS],
    )
    legs = (
        keyed.unionByName(unkeyed)
        .withColumn("wm_salary", F.coalesce(F.col("_sal"), F.lit(0)) == 1)
        .withColumn("wm_self", F.coalesce(F.col("_self"), F.lit(0)) == 1)
        .withColumn("wm_fee", F.coalesce(F.col("_fee"), F.lit(0)) == 1)
        .withColumn("wm_loan", F.coalesce(F.col("_loan"), F.lit(0)) == 1)
        .withColumn("wm_bank", F.coalesce(F.col("_bank"), F.lit(0)) == 1)
        .withColumn("flow_class", flow_class())
    )
    # One shuffle by ``event_month`` so each month folder gets one file, not one per
    # shuffle partition (the partitioned overwrite commits a rename per task file).
    return legs.select(
        "cif_id",
        "tran_id",
        "tran_date",
        "tran_dc",
        "amount",
        "flow_class",
        F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd").alias("event_month"),
    ).repartition("event_month")


def build_casa_flows(legs: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, flow_class)``: ``legs``, ``credit_aed``, ``debit_aed``
    and ``max_leg_aed`` of the classified legs (``build_casa_flow_legs``). Counted legs
    mirrored by a leg that does not count are dropped (``_net_mirrored``)."""
    _require(
        legs,
        ["cif_id", "tran_id", "tran_date", "tran_dc", "amount", "flow_class"],
        "prm_casa_flow_legs",
    )
    return (
        _net_mirrored(legs)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "flow_class")
        .agg(
            F.count(F.lit(1)).alias("legs"),
            F.sum(F.when(F.col("tran_dc") == "C", F.col("amount"))).alias("credit_aed"),
            F.sum(F.when(F.col("tran_dc") == "D", F.col("amount"))).alias("debit_aed"),
            F.max("amount").alias("max_leg_aed"),
        )
    )
