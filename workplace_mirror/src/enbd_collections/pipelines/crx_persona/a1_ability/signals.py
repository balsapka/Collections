"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders return the amounts the
classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the window (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the window.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
    window_agg,
    window_months,
)

# reason_for_excluding values that count as distress. prm_casa_return_events also carries
# "RETURNS", which is POS reversals (checked in PROD, Sonnet v01).
DISTRESS_RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m{months}`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots.

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    This is the only internal salary source. ``feat_payroll_indicator`` is not used: it is
    stamped the month after the credit and flags a subset of these months.
    """
    require_columns(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credit_date = F.date_sub(
        parse_yyyymmdd("week_number"),
        F.col("ft_days_since_salary_transaction").cast("int"),
    )
    return wm_salary.select(
        "cif_id",
        F.trunc(credit_date, "month").alias("month"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _bureau_salary(salary_hist: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Bureau-reported salary by month."""
    require_columns(
        salary_hist,
        [
            "subj_salcr_hist_hdr_file_id",
            "subj_salcr_hist_ref_mnth",
            "subj_salcr_hist_tot_sal_amt",
        ],
        "stg_aecb_salary_history",
    )
    require_columns(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    bridge = cif_bridge.select(
        F.col("bureau_file_id").alias("subj_salcr_hist_hdr_file_id"), "cif_id"
    ).distinct()
    return salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt").cast("double").alias("amount"),
    )


def build_income_signals(
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    monthly = (
        _internal_salary(wm_salary)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    months = 2 * window_months(model_id)
    return left_join_all(
        obs_base, [_by_month(obs, monthly, "amount", "income", months)]
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame) -> DataFrame:
    """CASA (current + savings) average balance per month: the 4-week average at the
    month's last weekly snapshot."""
    require_columns(
        wm_casa_bal,
        ["cif_id", "week_number", _CASA_MONTH_COL],
        "wm_fea_casa_eod_avg_balance",
    )
    week = parse_yyyymmdd("week_number")
    last_in_month = F.max(
        F.struct(week.alias("w"), F.col(_CASA_MONTH_COL).cast("double").alias("v"))
    )
    return (
        wm_casa_bal.groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame, months: int
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the window.

    ``raw_beneficiary_cards`` is a live snapshot: a card registered after the
    observation date still counts (mild look-ahead, accepted).
    """
    require_columns(
        labelled_txn,
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
    require_columns(
        beneficiary_cards,
        ["instrument_number", "instrument_type"],
        "raw_beneficiary_cards",
    )
    cards = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("transaction_acid"))
        .distinct()
    )
    src = (
        labelled_txn.filter(
            (F.col("tran_date") >= F.lit(lookback_floor(obs, months)))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        aggs=[F.max("tran_amt").alias("ext_card_payment_max")],
        months=months,
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame, months: int) -> DataFrame:
    """Any CASA credit or debit in the window."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active")],
        months=months,
    )


def build_liquidity_signals(
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}``, ``ext_card_payment_max``, ``casa_active``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    return left_join_all(
        obs_base,
        [
            _by_month(obs, _casa_by_month(wm_casa_bal), "balance", "casa", 2 * w),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards, w),
            _casa_activity(obs, wm_casa_flow, w),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
    internal_returns: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the window,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet;
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    require_columns(
        bureau_alert,
        ["cif_id", "extract_date", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    events = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                "cif_id", F.to_date("return_date").alias("event_date")
            )
        )
    if internal_returns is not None:
        require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
        events = events.unionByName(
            internal_returns.select(
                "cif_id", F.to_date("event_date").alias("event_date")
            )
        )
    hits = window_agg(
        obs,
        events,
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=window_months(model_id),
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(
    obs_base: DataFrame, return_events: DataFrame, model_id: str
) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    return (
        return_events.filter(
            (
                F.col("tran_date")
                >= F.lit(lookback_floor(obs_base, window_months(model_id)))
            )
            & F.col("reason_for_excluding").isin(*DISTRESS_RETURN_REASONS)
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
        .distinct()
    )
