"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Three evidence groups feed the classifier (``classify.py``):

* income    — payroll months, latest WM salary (if still current), bureau salary;
* liquidity — CASA balance (recent vs prior quarter), payments to external cards,
              CASA in/outflow activity;
* distress  — bounced cheques (plus optional sources not yet materialised in PROD).

Every builder takes the observation base ``(account_id, observation_date, cif_id)`` and
returns one row per base row that has evidence; the classifier left-joins them.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    pit_latest,
    require_columns,
    window_agg,
)

# WM salary snapshot rows are weekly; one older than this means the feed stopped.
_SALARY_SNAPSHOT_MAX_AGE_D = 35
# A salary credited longer ago than this is not current income.
_SALARY_MAX_AGE_D = 90
_CASA_BAL_COL = "ft_avg_eod_balance_in_last_0_2_months_avg"  # trailing 3-month average
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


# ── Income ────────────────────────────────────────────────────────────────────


def _payroll_months(obs: DataFrame, feat_payroll: DataFrame) -> DataFrame:
    """Months with a payroll credit in the last 3 complete months."""
    require_columns(
        feat_payroll,
        ["cif_id", "month_number", "payroll_flag"],
        "feat_payroll_indicator",
    )
    src = feat_payroll.select(
        "cif_id", parse_yyyymmdd("month_number").alias("month"), "payroll_flag"
    )
    return window_agg(
        obs,
        src,
        date_col="month",
        months=3,
        aggs=[
            F.sum((F.col("payroll_flag") == 1).cast("int")).alias("salary_months_h2")
        ],
    )


def _wm_salary(obs: DataFrame, wm_salary: DataFrame) -> DataFrame:
    """Latest WM salary amount, only while the salary itself is recent.

    The weekly snapshot carries the last salary ever seen;
    ``ft_days_since_salary_transaction`` says how old it was on the snapshot date. Both
    ages are bounded.
    """
    days_col = "ft_days_since_salary_transaction"
    require_columns(
        wm_salary,
        ["cif_id", "week_number", "ft_last_salary_amount", days_col],
        "wm_fea_salary_days_since_increment",
    )
    src = wm_salary.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        F.col("ft_last_salary_amount").cast("double").alias("_amt"),
        F.col(days_col).cast("int").alias("_days_since"),
    )
    latest = pit_latest(
        obs,
        src,
        date_col="week",
        value_cols=["_amt", "_days_since", "week"],
        max_age_days=_SALARY_SNAPSHOT_MAX_AGE_D,
    )
    age = F.col("_days_since") + F.datediff(F.col("observation_date"), F.col("week"))
    return latest.select(
        *GRAIN, F.when(age <= _SALARY_MAX_AGE_D, F.col("_amt")).alias("salary_amt_last")
    )


def _bureau_salary(
    obs: DataFrame, salary_hist: DataFrame, cif_bridge: DataFrame
) -> DataFrame:
    """Bureau salary credits in the last 6 months: presence and latest amount."""
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
    src = salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt")
        .cast("double")
        .alias("bureau_salary_amt_last"),
    )
    latest = pit_latest(
        obs,
        src,
        date_col="month",
        value_cols=["bureau_salary_amt_last"],
        max_age_days=183,
    )
    return latest.withColumn("bureau_salary_present_6m_flag", F.lit(1))


def build_income_signals(
    obs_base: DataFrame,
    feat_payroll: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
) -> DataFrame:
    """Payroll months, current WM salary and bureau salary per observation."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _payroll_months(obs, feat_payroll),
            _wm_salary(obs, wm_salary),
            _bureau_salary(obs, salary_hist, bureau_cif_bridge),
        ],
    )


# ── Liquidity ─────────────────────────────────────────────────────────────────


def _casa_quarters(obs: DataFrame, feat_casa_bal: DataFrame) -> DataFrame:
    """Trailing-3-month CASA balance at the latest month-end of each of the last two
    quarters (``casa_recent3m_avg``, ``casa_prior3m_avg``)."""
    require_columns(
        feat_casa_bal,
        ["cif_id", "month_end_date", _CASA_BAL_COL],
        "feat_casa_eod_balance",
    )
    src = feat_casa_bal.select(
        "cif_id",
        F.col("month_end_date").cast("date").alias("month_end"),
        F.col(_CASA_BAL_COL).cast("double").alias("_bal"),
    )
    obs_date = F.col("observation_date")
    recent = pit_latest(
        obs, src, date_col="month_end", value_cols=["_bal"], max_age_days=90
    )
    prior = pit_latest(
        obs,
        src,
        date_col="month_end",
        value_cols=["_bal"],
        anchor=F.date_sub(obs_date, 90),
        max_age_days=90,
    )
    return recent.withColumnRenamed("_bal", "casa_recent3m_avg").join(
        prior.withColumnRenamed("_bal", "casa_prior3m_avg"), on=list(GRAIN), how="outer"
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame
) -> DataFrame:
    """CASA payments to the customer's registered external credit cards, last 90 days.

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
            (F.col("tran_date") >= F.lit(lookback_floor(obs, 90)))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id",
            F.col("tran_date").cast("date").alias("tran_date"),
            F.col("tran_amt").cast("double"),
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        days=90,
        aggs=[
            F.sum("tran_amt").alias("ext_cc_payment_amt_h2"),
            # weeks with a payment
            F.countDistinct(F.date_trunc("week", "tran_date")).alias(
                "ext_cc_payment_cnt_h2"
            ),
        ],
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame) -> DataFrame:
    """Weeks with any CASA inflow / outflow in the last 90 days."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        _CASA_IN_COL,
        _CASA_OUT_COL,
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        days=90,
        aggs=[
            F.sum((F.col(_CASA_IN_COL) > 0).cast("int")).alias("casa_inflow_cnt_h2"),
            F.sum((F.col(_CASA_OUT_COL) > 0).cast("int")).alias("casa_outflow_cnt_h2"),
        ],
    )


def build_liquidity_signals(
    obs_base: DataFrame,
    feat_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
) -> DataFrame:
    """CASA balance by quarter, external card payments and CASA activity."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _casa_quarters(obs, feat_casa_bal),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards),
            _casa_activity(obs, wm_casa_flow),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a bounced cheque (or, once materialised, a returned payment order)
    reported in the last 90 days.

    ``payment_order`` (prm_bureau_payment_order) does not exist in PROD yet; wire it in
    the pipeline when it does.
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
    hits = window_agg(
        obs,
        events,
        date_col="event_date",
        days=90,
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])
