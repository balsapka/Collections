"""T26 — A1 Ability enrichment helpers.

Helper functions for building A1 ability signals:
  - _enrich_salary_months_h2: payroll_indicator → salary_months_h2
  - _enrich_casa_eod_bal_h2: casa_eod_balance → casa_eod_bal_h2
  - _enrich_salary_pit: salary_days_since_increment → salary signals
  - _enrich_recurring_inflow_h2: casa_weekly_repeated_inflow → recurring signals
  - _enrich_payment_trajectory: T04b → payment trajectory
  - _enrich_utilisation: T05 → utilisation
  - _enrich_prm_balance: prm_balance → cc_total_outstanding
  - enrich_salary_stop_month: payroll_indicator → salary_stop_month
    (RL-A1-19 — timing-anchored salary arm high_arm3)
  - enrich_ext_loan_payments_h2: wm_fea_external_loan_payments →
    ext_loan_payment_amt_h2, ext_loan_payment_cnt_h2 (RL-A1-23 — High Arm 6b)

All functions return None (with warning) if required columns are absent.
"""

# pylint: disable=too-many-lines

import logging
from typing import NamedTuple, Optional, Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


class RequiredJoin(NamedTuple):
    """One declared enrichment signal: a label (for the error message) and
    the already-computed signal DataFrame (None if the enricher's required
    source columns were absent)."""

    label: str
    signal_df: Optional[DataFrame]


def join_required_signals(
    base: DataFrame, grain_key: tuple, joins: Sequence[RequiredJoin]
) -> DataFrame:
    """Left-join every declared signal onto base.

    Raises RuntimeError if any enricher returned None instead of
    null-stubbing it — upstream schema drift is a defect to surface at
    build time, not degrade through silently.
    """
    result = base
    for rj in joins:
        if rj.signal_df is None:
            raise RuntimeError(
                f"{rj.label}: enricher returned None — required source "
                "columns are missing. Fix the source or the enricher; do "
                "not silently null the signal."
            )
        result = result.join(rj.signal_df, on=list(grain_key), how="left")
    return result


# ── CASA EOD balance column name in feat_casa_eod_balance ─────────────────────
# 3-month rolling avg relative to record date: covers ≈ [T0-3m, T0) at PIT.
_CASA_BAL_COL = "ft_avg_eod_balance_in_last_0_2_months_avg"


def enrich_salary_months_h2(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Count H2 months with payroll_flag=1 from feat_payroll_indicator.

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_months_h2).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
            "enrich_salary_months_h2: feat_payroll_indicator missing 'payroll_flag'"
            " — salary_months_h2 will be NULL for all rows"
        )
        return None

    fp_dated = feat_payroll.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_month_date", "payroll_flag")

    h2_salary = (
        cif_base.join(fp_dated, on="cif_id", how="inner")
        .filter(
            (
                F.col("_month_date")
                >= F.add_months(F.trunc(F.col(anchor_col), "month"), -3)
            )
            & (F.col("_month_date") < F.trunc(F.col(anchor_col), "month"))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col("payroll_flag") == 1, 1).otherwise(0))
            .cast("int")
            .alias("salary_months_h2")
        )
    )

    return h2_salary


def enrich_salary_months_h4_h6(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Count H4-H6 months with payroll_flag=1 from feat_payroll_indicator.

    Window shifted 3 months earlier than enrich_salary_months_h2's H2 window:
    [anchor-6m, anchor-3m) instead of [anchor-3m, anchor). Used (RL-A1-9) to
    detect whether payroll was present before the most recent 3-month window,
    feeding the salary_stopped_flag_recent derivation.

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_months_h4_h6).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
            "enrich_salary_months_h4_h6: feat_payroll_indicator missing 'payroll_flag'"
            " — salary_months_h4_h6 will be NULL for all rows"
        )
        return None

    fp_dated = feat_payroll.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_month_date", "payroll_flag")

    h4_h6_salary = (
        cif_base.join(fp_dated, on="cif_id", how="inner")
        .filter(
            (
                F.col("_month_date")
                >= F.add_months(F.trunc(F.col(anchor_col), "month"), -6)
            )
            & (
                F.col("_month_date")
                < F.add_months(F.trunc(F.col(anchor_col), "month"), -3)
            )
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col("payroll_flag") == 1, 1).otherwise(0))
            .cast("int")
            .alias("salary_months_h4_h6")
        )
    )

    return h4_h6_salary


def enrich_salary_stop_month(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Latest H4-H6 month with payroll_flag=1 from feat_payroll_indicator (RL-A1-19).

    Same window as enrich_salary_months_h4_h6 ([anchor-6m, anchor-3m)), but
    returns the latest calendar month payroll was present instead of a count —
    the timing-anchored high_arm3 (RL-A1-19) compares this against the bureau
    pull date, not just a presence count. Rows with no payroll_flag=1 month in
    the window get NULL (there is no "stop month" to report, not 0).

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_stop_month).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
# <<MIRROR GAP: enrichers.py line 176 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 177 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 178 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 179 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 180 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 181 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 182 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 183 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 184 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 185 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 186 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 187 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 188 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 189 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 190 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 191 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 192 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 193 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 194 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 195 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 196 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 197 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 198 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 199 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 200 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 201 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 202 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 203 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 204 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 205 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 206 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 207 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 208 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 209 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 210 not photographed (IMG_8260 missing)>>
# <<MIRROR GAP: enrichers.py line 211 not photographed (IMG_8260 missing)>>
_CASA_EOD_BAL_SOURCE_COLS = {
    "ca": {
        "spot": "ft_avg_ca_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_ca_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_ca_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_ca_eod_balance_in_last_0_11_weeks_max",
    },
    "casa": {
        "spot": "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_casa_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_casa_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_casa_eod_balance_in_last_0_11_weeks_max",
    },
    "all": {
        "spot": "ft_avg_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_eod_balance_in_last_0_11_weeks_max",
    },
}


def enrich_casa_eod_avg_balance(
    cif_base: DataFrame,
    wm_casa_avg_bal: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT CASA EOD avg balance — 3 scope prefixes x 2 windows x 2 aggs — from
    wm_fea_casa_eod_avg_balance (WM).

    RL-A1-20: casa (CA+SA) is the primary balance-vs-EMI gate; ca (current-
    account-only) and all (CASA+investments+FDs) are passthrough/diagnostic
    only (never wired into a gate). casa ⊇ ca by construction — a
    savings-only customer with no current account still shows a non-null
    casa figure even when their ca figure is null. _max variants are
    diagnostic-only (never wired into a gate).

    PIT join: filters wm_casa_avg_bal to week_date <= anchor_col per row, then
    window-dedups to the freshest week_number per grain_key (same row_number
    pattern as enrich_salary_pit / enrich_casa_inflow_h2's PIT joins).

    week_number, not adv_load_date, is the real per-row time dimension
    (RL-A1-14/RL-A1-9 Leg B, confirmed in PROD 2026-10-05): a direct column
    probe showed adv_load_date is a load-time constant (single value across
    all sampled rows, e.g. 2026-06-02), while week_number varies per row from
    2022-01 onward — the catalog entry being unpinned on adv_load_date made
    adv_load_date a genuine loaded column, but not a genuine per-row date.
    This mirrors the sibling table wm_fea_casa_cc_inflow_outflow
    (enrich_casa_inflow_h2), which already keys off week_number correctly.
    week_number parses the same way: F.to_date(..., "yyyyMMdd").

    Each avg_3m / avg_3m_max output coalesces the 3m-window column to its
    same-prefix spot column (2-level coalesce only — the 6m candidate column
    has no corroborated name, see RESULTS_RL.md 2026-10-02).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_eod_spot_ca, casa_eod_spot_ca_max,
    casa_eod_avg_3m_ca, casa_eod_avg_3m_ca_max, casa_eod_spot_casa,
    casa_eod_spot_casa_max, casa_eod_avg_3m_casa, casa_eod_avg_3m_casa_max,
    casa_eod_spot_all, casa_eod_spot_all_max, casa_eod_avg_3m_all,
    casa_eod_avg_3m_all_max).
    """
    _required = ["week_number"] + [
        c for grp in _CASA_EOD_BAL_SOURCE_COLS.values() for c in grp.values()
    ]
    missing = [c for c in _required if c not in wm_casa_avg_bal.columns]
    if missing:
        LOG.warning(
            "enrich_casa_eod_avg_balance: wm_fea_casa_eod_avg_balance missing %s"
            " — all casa_eod_* columns will be NULL",
            missing,
        )
        return None

    _src_select = [
        F.col(col).cast("double").alias(f"_{prefix}_{window}")
        for prefix, cols in _CASA_EOD_BAL_SOURCE_COLS.items()
        for window, col in cols.items()
    ]
    bal_dated = wm_casa_avg_bal.select(
        "cif_id",
        F.to_date(F.col("week_number").cast("string"), "yyyyMMdd").alias("_snap_date"),
        *_src_select,
    )

    joined = cif_base.join(bal_dated, on="cif_id", how="inner").filter(
        F.col("_snap_date") <= F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_snap_date").desc())
    _out_select = [*grain_key]
    for prefix in _CASA_EOD_BAL_SOURCE_COLS:
        _out_select.append(F.col(f"_{prefix}_spot").alias(f"casa_eod_spot_{prefix}"))
        _out_select.append(
            F.col(f"_{prefix}_spot_max").alias(f"casa_eod_spot_{prefix}_max")
        )
        _out_select.append(
            F.coalesce(F.col(f"_{prefix}_avg_3m"), F.col(f"_{prefix}_spot")).alias(
                f"casa_eod_avg_3m_{prefix}"
            )
        )
        _out_select.append(
            F.coalesce(
                F.col(f"_{prefix}_avg_3m_max"), F.col(f"_{prefix}_spot_max")
            ).alias(f"casa_eod_avg_3m_{prefix}_max")
        )

    pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(*_out_select)
    )

    return pit


def enrich_casa_eod_bal_h2(
    cif_base: DataFrame,
    feat_casa_bal: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT CASA EOD balance from feat_casa_eod_balance (retail.feature_space).

    PIT approach: latest record with month_end_date < T0, per row — the catalog
    entry (feat_casa_eod_balance) is pinned to one adv_load_date snapshot, so
    `adv_load_date` is not a column in this DataFrame at all; the real per-record
    PIT date is `month_end_date`, which is used directly below.
    Balance column: ft_avg_eod_balance_in_last_0_2_months_avg
        — 3-month rolling average relative to the record date, covering
          months 0, 1, 2 back from that date ≈ [T0-3m, T0) at PIT.

    ⚠ IMPORTANT — previous bugs fixed here:
        1. Date column was 'month_number' (yyyyMMdd int) — WRONG.
           Correct column is 'month_end_date' (YYYY-MM-dd string), cast directly.
        2. Balance column was 'avg_casa_eod_balance' — WRONG (not in schema).
           Correct column is 'ft_avg_eod_balance_in_last_0_2_months_avg'.
        3. Filtering/selecting on 'adv_load_date' — WRONG. The catalog entry is
           pinned (`.../adv_load_date=${globals:snapshot_adv_load_date}`), so Spark
           reads directly from that leaf partition and the column does not exist
           in the schema — raises UNRESOLVED_COLUMN, not a silent no-op.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, casa_eod_bal_h2).
    """
    for col in ("month_end_date", _CASA_BAL_COL):
        if col not in feat_casa_bal.columns:
            LOG.warning(
                "enrich_casa_eod_bal_h2: feat_casa_eod_balance missing '%s'"
                " — casa_eod_bal_h2 will be NULL",
                col,
            )
            return None

    cb_dated = feat_casa_bal.withColumn(
        "_month_date", F.col("month_end_date").cast("date")
    ).select("cif_id", "_month_date", _CASA_BAL_COL)

    joined = cif_base.join(cb_dated, on="cif_id", how="inner").filter(
        F.col("_month_date") < F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    casa_pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col(_CASA_BAL_COL).cast("double").alias("casa_eod_bal_h2"),
        )
    )

    return casa_pit


def enrich_salary_pit(
    cif_base: DataFrame,
    wm_salary: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT salary signals from wm_fea_salary_days_since_increment.

    PIT = last week_number strictly before T0, per row — the catalog entry is
    pinned to one adv_load_date snapshot, so `adv_load_date` is not a column in
    this DataFrame at all; the real per-record PIT date is `week_number`, used
    directly below.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, salary_amt_last, salary_change_pct).
    """
    _required = [
        "ft_last_salary_amount",
        "ft_percent_monthly_salary_change",
    ]
    missing = [c for c in _required if c not in wm_salary.columns]
    if missing:
        LOG.warning(
            "enrich_salary_pit: wm_fea_salary_days_since_increment missing %s"
            " — salary PIT signals will be NULL",
            missing,
        )
        return None

    ws_dated = wm_salary.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", *_required)

    joined = cif_base.join(ws_dated, on="cif_id", how="inner").filter(
        F.col("_week_date") < F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_week_date").desc())
    sal_pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col("ft_last_salary_amount").cast("double").alias("salary_amt_last"),
            F.col("ft_percent_monthly_salary_change")
            .cast("double")
            .alias("salary_change_pct"),
        )
    )

    return sal_pit


def enrich_recurring_inflow_h2(
    cif_base: DataFrame,
    wm_recurring: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 recurring non-salary CASA inflow from wm_fea_casa_weekly_repeated_inflow.

    H2 = weeks with week_date in [T0 - 90 days, T0).

    Source schema: (cif_id, week_number, ft_repeated_inflow).
    get_continuous_weekly_fill_from_month renames repeated_inflow_month_amt →
    ft_repeated_inflow and drops repeated_inflow_month_count (not forwarded).
    recurring_inflow_cnt_h2 is derived as count of H2 weeks with ft_repeated_inflow > 0.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, recurring_inflow_amt_h2,
                            recurring_inflow_cnt_h2).
    """
    _required = ["ft_repeated_inflow"]
    missing = [c for c in _required if c not in wm_recurring.columns]
    if missing:
        LOG.warning(
            "enrich_recurring_inflow_h2: wm_fea_casa_weekly_repeated_inflow"
            " missing %s — recurring inflow signals will be NULL",
            missing,
        )
        return None

    wr_dated = wm_recurring.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", "ft_repeated_inflow")

    rec_h2 = (
        cif_base.join(wr_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("ft_repeated_inflow").cast("double").alias("recurring_inflow_amt_h2"),
            F.sum(F.when(F.col("ft_repeated_inflow") > 0, F.lit(1)).otherwise(F.lit(0)))
            .cast("int")
            .alias("recurring_inflow_cnt_h2"),
        )
    )

    return rec_h2


def enrich_casa_inflow_h2(
    cif_base: DataFrame,
    wm_casa_inflow: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 generic CASA inflow from wm_fea_casa_cc_inflow_outflow.

    H2 = weeks with week_date in [T0 - 90 days, T0).

    Captures ALL CASA credit types — salary, family transfers, rental,
    business payments — broader than payroll_present_h2 (ENBD payroll only)
    and recurring_inflow_cnt_h2 (same-counterparty recurring only).

    Source schema: (cif_id, week_number, ft_inflow_casa_amt_in_last_0_0_weeks_sum, ...).
    ft_inflow_casa_amt_in_last_0_0_weeks_sum is the 0:0 window (spot week amount).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, casa_inflow_amt_h2,
                            casa_inflow_cnt_h2).
    """
    _required = ["ft_inflow_casa_amt_in_last_0_0_weeks_sum"]
    missing = [c for c in _required if c not in wm_casa_inflow.columns]
    if missing:
        LOG.warning(
            "enrich_casa_inflow_h2: wm_fea_casa_cc_inflow_outflow"
            " missing %s — generic CASA inflow signals will be NULL",
            missing,
        )
        return None

    ci_dated = wm_casa_inflow.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", "ft_inflow_casa_amt_in_last_0_0_weeks_sum")

    inflow_h2 = (
        cif_base.join(ci_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("ft_inflow_casa_amt_in_last_0_0_weeks_sum")
            .cast("double")
            .alias("casa_inflow_amt_h2"),
            F.sum(
                F.when(
                    F.col("ft_inflow_casa_amt_in_last_0_0_weeks_sum") > 0, F.lit(1)
                ).otherwise(F.lit(0))
            )
            .cast("int")
            .alias("casa_inflow_cnt_h2"),
        )
    )

    return inflow_h2


def enrich_ext_cc_payments_h2(
    cif_base: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 CASA payments to external credit cards from WM primary + BENEFICIARY table.

    H2 = transactions with tran_date in [anchor - 90 days, anchor).

    Source: pri_labelled_transactions_indicators_by_week (WM primary layer) joined
    to AI_TDV_OMB_UAE_EBI.BENEFICIARY on transaction_acid == instrument_number.
    Only CARD_NUMBER instrument types (external CC numbers registered by customers)
    are matched — this captures genuine CC obligation servicing at other banks,
    not generic self-transfers.

    ⚠ [CONFIRM] beneficiary_cards is a live snapshot (edp_activeind='Y'); no
    historical partitioning means mild look-ahead bias if beneficiaries changed
    after T0.  Acceptable for v1 — refine at Leg B if coverage data warrants.

    Required columns:
        wm_labelled_transactions: cif_id, in_out_flow, product_category,
                                  tran_date, tran_amt, transaction_acid
        beneficiary_cards:        instrument_number, instrument_type

    Returns DataFrame(account_id, spell_id, ext_cc_payment_amt_h2,
                      ext_cc_payment_cnt_h2) or None if required columns absent.
    """
    _required_txn = [
        "cif_id",
        "in_out_flow",
        "product_category",
        "tran_date",
        "tran_amt",
        "transaction_acid",
    ]
    _required_bene = ["instrument_number", "instrument_type"]

    missing_txn = [
        c for c in _required_txn if c not in wm_labelled_transactions.columns
    ]
    if missing_txn:
        LOG.warning(
            "enrich_ext_cc_payments_h2: wm_pri_labelled_transactions missing %s"
            " — ext_cc_payment signals will be NULL",
            missing_txn,
        )
        return None

    missing_bene = [c for c in _required_bene if c not in beneficiary_cards.columns]
    if missing_bene:
        LOG.warning(
            "enrich_ext_cc_payments_h2: raw_beneficiary_cards missing %s"
            " — ext_cc_payment signals will be NULL",
            missing_bene,
        )
        return None

    # Distinct set of external CC numbers (may already be filtered to CARD_NUMBER
    # via catalog query, but guard here in case catalog query is broadened later)
    cc_numbers = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("_cc_number"))
        .distinct()
    )

    # CASA outflow transactions at transaction grain
    casa_outflow = wm_labelled_transactions.filter(
        (F.col("in_out_flow") == "outflow") & (F.col("product_category") == "CASA")
    ).select(
        F.col("cif_id").cast("string"),
        F.col("tran_date").cast("date").alias("_tran_date"),
        F.col("tran_amt").cast("double"),
        F.col("transaction_acid"),
    )

    # Keep only transactions where the destination matches a registered external CC
    cc_payments = casa_outflow.join(
        cc_numbers,
        on=casa_outflow["transaction_acid"] == cc_numbers["_cc_number"],
        how="inner",
    ).drop("_cc_number")

    # Bridge to spell grain via cif_base and apply H2 window
    result = (
        cif_base.join(cc_payments, on="cif_id", how="inner")
        .filter(
            (F.col("_tran_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_tran_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("tran_amt").cast("double").alias("ext_cc_payment_amt_h2"),
            # Count distinct ISO weeks with ≥1 payment (consistent with H2 cnt signals)
            F.countDistinct(F.date_format(F.col("_tran_date"), "yyyyww"))
            .cast("int")
            .alias("ext_cc_payment_cnt_h2"),
        )
    )

    return result


# ── External loan payments column names (wm_fea_external_loan_payments, WM) ──
# Weekly PIT-joinable series (week_number is the real per-row date, same
# confirmed pattern as the sibling wm_fea_casa_eod_avg_balance — see
# docs/context/reference/sibling_repo_partitions.md). No R2 look-ahead flag
# (unlike RL-A1-22's single-pinned-snapshot income dataset).
_EXT_LOAN_AMT_COL = "ft_external_loan_payment_amt_in_last_0_3_weeks_sum"
_EXT_LOAN_CNT_COL = "ft_external_loan_payment_cnt_in_last_0_3_weeks_sum"


def enrich_ext_loan_payments_h2(
    cif_base: DataFrame,
    wm_ext_loan_payments: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT external-bank loan payment amount/count from wm_fea_external_loan_payments.

    RL-A1-23 (High Arm 6b): "servicing another bank's loan from this CASA
    account" is the same evidentiary logic as the existing high_arm6
    ("servicing another bank's credit card") — this enricher mirrors
    enrich_ext_cc_payments_h2's output shape (amt + cnt pair), but the join
    mechanics mirror enrich_casa_eod_avg_balance's PIT pattern instead: the
    source table is already a pre-aggregated weekly trailing-window feature
    (0:3-week sum), not raw transactions, so there is no H2-window
    aggregation to do here — just a PIT pick of the freshest weekly snapshot.

    PIT join: filters wm_ext_loan_payments to week_date <= anchor_col per row,
    then window-dedups to the freshest week_number per grain_key (same
    row_number pattern as enrich_casa_eod_avg_balance).

    week_number, not adv_load_date, is the real per-row time dimension —
    confirmed PROD precedent for this table (RL-A1-23 Leg B,
    trl_a1_23_ext_loan_payment_probe.py chk1), same confirmed pattern as the
    sibling wm_fea_casa_eod_avg_balance.

    Required columns: cif_id, week_number, ft_external_loan_payment_amt_in_
        last_0_3_weeks_sum, ft_external_loan_payment_cnt_in_last_0_3_weeks_sum.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., ext_loan_payment_amt_h2,
    ext_loan_payment_cnt_h2).
    """
    _required = ["cif_id", "week_number", _EXT_LOAN_AMT_COL, _EXT_LOAN_CNT_COL]
    missing = [c for c in _required if c not in wm_ext_loan_payments.columns]
    if missing:
        LOG.warning(
            "enrich_ext_loan_payments_h2: wm_fea_external_loan_payments missing %s"
            " — ext_loan_payment_amt_h2/cnt_h2 will be NULL",
            missing,
        )
        return None

    ext_dated = wm_ext_loan_payments.select(
        "cif_id",
        F.to_date(F.col("week_number").cast("string"), "yyyyMMdd").alias("_snap_date"),
        F.col(_EXT_LOAN_AMT_COL).cast("double").alias("_amt_sum"),
        F.col(_EXT_LOAN_CNT_COL).cast("double").alias("_cnt_sum"),
    )

    joined = cif_base.join(ext_dated, on="cif_id", how="inner").filter(
        F.col("_snap_date") <= F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_snap_date").desc())
    pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col("_amt_sum").alias("ext_loan_payment_amt_h2"),
            F.col("_cnt_sum").alias("ext_loan_payment_cnt_h2"),
        )
    )

    return pit


def enrich_payment_trajectory(
    base: DataFrame,
    payment_traj: DataFrame,
) -> DataFrame | None:
    """Join T04b payment trajectory features at (account_id, spell_id) grain.

    No CIF bridge required — T04b is already at spell grain.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, pay_ratio_slope,
                            pay_ratio_mean_h1, pay_ratio_mean_h2).
    """
    _required = ["pay_ratio_slope", "pay_ratio_mean_h1", "pay_ratio_mean_h2"]
    missing = [c for c in _required if c not in payment_traj.columns]
    if missing:
        LOG.warning(
            "enrich_payment_trajectory: crx_cc_payment_trajectory missing %s"
            " — trajectory signals will be NULL",
            missing,
        )
        return None

    result = (
        base.select("account_id", "spell_id")
        .join(
            payment_traj.select("account_id", "spell_id", *_required),
            on=["account_id", "spell_id"],
            how="inner",
        )
        .select(
            "account_id",
            "spell_id",
            F.col("pay_ratio_slope").cast("double"),
            F.col("pay_ratio_mean_h1").cast("double"),
            F.col("pay_ratio_mean_h2").cast("double"),
        )
    )

    return result


def enrich_utilisation(
    base: DataFrame,
    util_features: DataFrame,
) -> DataFrame | None:
    """Join T05 utilisation features at (account_id, spell_id) grain.

    No CIF bridge required — T05 is already at spell grain.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, util_t0, util_slope,
                            spend_cliff_flag).
    """
    _required = ["util_t0", "util_slope", "spend_cliff_flag"]
    missing = [c for c in _required if c not in util_features.columns]
    if missing:
        LOG.warning(
            "enrich_utilisation: crx_cc_utilisation_features missing %s"
            " — utilisation signals will be NULL",
            missing,
        )
        return None

    result = (
        base.select("account_id", "spell_id")
        .join(
            util_features.select("account_id", "spell_id", *_required),
            on=["account_id", "spell_id"],
            how="inner",
        )
        .select(
            "account_id",
            "spell_id",
            F.col("util_t0").cast("double"),
            F.col("util_slope").cast("double"),
            F.col("spend_cliff_flag").cast("int"),
        )
    )

    return result


def enrich_prm_balance(
    base: DataFrame,
    prm_balance: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT join prm_balance for cc_total_outstanding at T0 or observation_date.

    anchor_col controls the PIT cutoff column from base:
      - "t0" (default): latest balance ≤ T0 per (account_id, spell_id)
        → output column named cc_total_outstanding
      - "observation_date": latest balance ≤ observation_date per grain_key
        → output column named cc_total_outstanding_recent

    account_id == contract_id in the CC domain (confirmed by CIF bridge pattern).
    total_outstanding = full current + overdue CC balance at anchor point.

    Note: prm_balance renames banking_date → observation_date in the primary layer
    (_BALANCE_RENAMES in prm_cc.py).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., cc_total_outstanding[_recent]).
    """
    _required = ["contract_id", "observation_date", "total_outstanding"]
    missing = [c for c in _required if c not in prm_balance.columns]
    if missing:
        LOG.warning(
            "enrich_prm_balance: prm_balance missing %s"
            " — cc_total_outstanding will be NULL",
            missing,
        )
        return None

    out_col = (
        "cc_total_outstanding" if anchor_col == "t0" else "cc_total_outstanding_recent"
    )
    _grain_cols = list(grain_key)

    # Alias balance observation_date to avoid collision with base.observation_date
    bal = prm_balance.select(
        F.col("contract_id"),
        F.col("observation_date").cast("date").alias("_bal_obs_date"),
        F.col("total_outstanding").cast("double"),
    )

    # Select grain cols + anchor aliased to _anchor to handle name collisions
    if anchor_col in _grain_cols:
        # anchor is already a grain key column (e.g. observation_date); copy it
        base_sel = base.select(*_grain_cols).withColumn("_anchor", F.col(anchor_col))
    else:
        base_sel = base.select(*_grain_cols, F.col(anchor_col).alias("_anchor"))

    joined = (
        base_sel.join(
            bal,
            on=(base_sel["account_id"] == bal["contract_id"]),
            how="left",
        )
        .filter(
            F.col("_bal_obs_date").isNotNull()
            & (F.col("_bal_obs_date") <= F.col("_anchor"))
        )
        .drop("contract_id", "_anchor")
    )

    w = Window.partitionBy(*_grain_cols).orderBy(F.col("_bal_obs_date").desc())
    result = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *_grain_cols,
            F.col("total_outstanding").alias(out_col),
        )
    )

    return result


# ── Bureau salary column names (stg_aecb_salary_history) ─────────────────────
# Source: ai_dpl_uae_operations.sa_ops_aecb_sub_sal_cr_hist (110M rows)
# Grain: subj_salcr_hist_hdr_file_id × subj_salcr_hist_ref_mnth × EDP_LOAD_DATE
# No direct cif_id — requires prm_bureau_cif_bridge (bureau_file_id → cif_id).
_AECB_SAL_FILE_COL = "subj_salcr_hist_hdr_file_id"  # bureau file UUID (join key)
_AECB_SAL_DATE_COL = "subj_salcr_hist_ref_mnth"  # reference month of salary credit
_AECB_SAL_AMT_COL = "subj_salcr_hist_tot_sal_amt"  # total salary amount credited

# ── Bureau alert column names (prm_bureau_alert_enriched) ────────────────────
# Source: stg_aecb_alert → prm_bureau_alert_enriched (primary layer renames applied)
# EXTRACT_DT renamed to extract_date; ALERT_DESC normalized to alert_type_flag.
_BUREAU_ALERT_CIF_COL = "cif_id"  # PRVDR_SUBJ_NUM cast to long in primary layer
_BUREAU_ALERT_DATE_COL = "extract_date"  # renamed from EXTRACT_DT in _ALERT_RENAMES
_BUREAU_ALERT_TYPE_COL = "alert_type_flag"  # lower(trim(no-spaces(ALERT_DESC)))

# ── Bureau alert type filter values ──────────────────────────────────────────
# alert_type_flag = lower(trim(regexp_replace(ALERT_DESC, r"\s+", "")))
# e.g. "Salary Account Added" → "salaryaccountadded"
# Confirmed from T26a EDA (2026-09-17) on prm_bureau_alert_enriched.
_ALERT_NEW_SALARY_ACCT = "salaryaccountadded"  # confirmed: 32,780 rows

# Off-us paying: no single value exists.  The signal is the "positive alerts"
# family — any alert where a competitor facility recovered from delinquency
# (e.g. "positivealerts30dpdtoactive-creditcards").  Matched via startswith
# prefix rather than equality; covers all DPD bands and product types.
_ALERT_OFFUS_PAYING_PREFIX = "positivealerts"  # confirmed from T26a EDA


def enrich_bureau_salary(  # pylint: disable=too-many-locals
    cif_base: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Bureau salary history from stg_aecb_salary_history (bureau-file-grain).

    stg_aecb_salary_history has no direct cif_id — it is keyed on bureau file
    UUIDs.  prm_bureau_cif_bridge maps subj_salcr_hist_hdr_file_id → cif_id.

    Window: [T0 - 6 months, T0) — covers H1 and H2.
    Derives:
        bureau_salary_present_6m_flag  int 0/1  — any salary credit in window
        bureau_salary_amt_last         double   — most recent salary credit amount

    ⚠ eosb_post_salary_flag is derived in build_a1_classify (not here) because
      it requires eosb_like_flag from Group A, which is unavailable here.

    ⚠ [LEG B] T0 anchor used for v1.  Upgrade to scoring-month reference after
      observation_date is available in spell table.

    Schema guard: required columns absent → returns None (warning logged).
    Required columns:
        stg_aecb_salary_history: _AECB_SAL_FILE_COL, _AECB_SAL_DATE_COL,
                                 _AECB_SAL_AMT_COL
        prm_bureau_cif_bridge:   bureau_file_id, cif_id

    Returns DataFrame with (account_id, spell_id, bureau_salary_present_6m_flag,
                           bureau_salary_amt_last) or None.
    """
    _required_sal = [_AECB_SAL_FILE_COL, _AECB_SAL_DATE_COL, _AECB_SAL_AMT_COL]
    missing_sal = [c for c in _required_sal if c not in stg_salary_hist.columns]
    if missing_sal:
        LOG.warning(
            "enrich_bureau_salary: stg_aecb_salary_history missing %s"
            " — bureau salary signals will be NULL",
            missing_sal,
        )
        return None

    _required_bridge = ["bureau_file_id", "cif_id"]
    missing_bridge = [
        c for c in _required_bridge if c not in prm_bureau_cif_bridge.columns
    ]
    if missing_bridge:
        LOG.warning(
            "enrich_bureau_salary: prm_bureau_cif_bridge missing %s"
            " — bureau salary signals will be NULL",
            missing_bridge,
        )
        return None

    # Deduplicate CIF bridge: keep one cif_id per bureau_file_id (any snapshot)
    cif_bridge = prm_bureau_cif_bridge.select(
        "bureau_file_id", "cif_id"
    ).dropDuplicates(["bureau_file_id"])

    # Bridge salary history to cif_id via bureau_file_id
    # subj_salcr_hist_ref_mnth is stored as "MMYYYY" string — must specify format
    sal_with_cif = stg_salary_hist.join(
        cif_bridge,
        on=stg_salary_hist[_AECB_SAL_FILE_COL] == cif_bridge["bureau_file_id"],
        how="inner",
    ).select(
        F.col("cif_id").cast("string"),
        F.to_date(F.col(_AECB_SAL_DATE_COL), "MMyyyy").alias("_sal_date"),
        F.col(_AECB_SAL_AMT_COL).cast("double").alias("_sal_amt"),
    )

    n_bridge = sal_with_cif.count()
    LOG.info("enrich_bureau_salary: %d rows after bridge join", n_bridge)
    if n_bridge == 0:
        LOG.warning(
            "enrich_bureau_salary: bureau_file_id join produced 0 rows"
            " — prm_bureau_cif_bridge may not cover stg_aecb_salary_history"
        )
        return None

    # 6-month window join [T0-6m, T0)
    joined = cif_base.join(sal_with_cif, on="cif_id", how="inner").filter(
        (F.col("_sal_date") >= F.add_months(F.col(anchor_col), -6))
        & (F.col("_sal_date") < F.col(anchor_col))
    )

    # PIT: most recent salary record within window
    w_pit = Window.partitionBy(*grain_key).orderBy(F.col("_sal_date").desc())
    pit = (
        joined.withColumn("_rn", F.row_number().over(w_pit))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.lit(1).cast("int").alias("bureau_salary_present_6m_flag"),
            F.col("_sal_amt").cast("double").alias("bureau_salary_amt_last"),
        )
    )

    # Note: bureau_salary_present_6m_flag is always NULL (no bureau record) or 1
    # (salary credit found in window). It is never 0 — analysts querying = 0 find no rows.
    return pit


def enrich_bureau_alerts(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Bureau alert signals from prm_bureau_alert_enriched (CIF-grain).

    Window: [T0 - 90 days, T0) — pre-T0 to avoid leakage.
    Derives:
        a1_new_salary_acct_flag  int 0/1 — new salary account alert in window
        a1_offus_paying_flag     int 0/1 — positive off-us delinquency in window

    Column names in prm_bureau_alert_enriched (primary layer renames applied):
        cif_id          — PRVDR_SUBJ_NUM cast to long
        extract_date    — EXTRACT_DT renamed in _ALERT_RENAMES
        alert_type_flag — lower(trim(no-spaces(ALERT_DESC))) derived column

    Filter values (alert_type_flag):
        new salary acct:  _ALERT_NEW_SALARY_ACCT = "salaryaccountadded" (exact match)
        off-us paying:    _ALERT_OFFUS_PAYING_PREFIX = "positivealerts" (startswith)
                          Covers all DPD bands and product types, e.g.:
                            positivealerts30dpdtoactive-creditcards
                            positivealerts60dpdtoactive-installments
                          Confirmed from T26a EDA (2026-09-17).

    Schema guard: required columns absent → returns None (warning logged).
    Required columns: _BUREAU_ALERT_CIF_COL, _BUREAU_ALERT_DATE_COL,
                      _BUREAU_ALERT_TYPE_COL

    Returns DataFrame with (account_id, spell_id, a1_new_salary_acct_flag,
                           a1_offus_paying_flag) or None.
    """
    _required = [_BUREAU_ALERT_CIF_COL, _BUREAU_ALERT_DATE_COL, _BUREAU_ALERT_TYPE_COL]
    missing = [c for c in _required if c not in prm_bureau_alert.columns]
    if missing:
        LOG.warning(
            "enrich_bureau_alerts: prm_bureau_alert_enriched missing %s"
            " — bureau alert signals will be NULL",
            missing,
        )
        return None

    alerts_dated = prm_bureau_alert.withColumn(
        "_alert_date", F.to_date(F.col(_BUREAU_ALERT_DATE_COL))
    ).select(
        F.col(_BUREAU_ALERT_CIF_COL).alias("_bur_cif_id"),
        "_alert_date",
        F.col(_BUREAU_ALERT_TYPE_COL).alias("_alert_type"),
    )

    # 90-day pre-T0 window
    joined = (
        cif_base.join(
            alerts_dated,
            on=cif_base["cif_id"] == alerts_dated["_bur_cif_id"],
            how="inner",
        )
        .filter(
            (F.col("_alert_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_alert_date") < F.col(anchor_col))
        )
        .drop("_bur_cif_id")
    )

    result = joined.groupBy(*grain_key).agg(
        F.max(
            F.when(F.col("_alert_type") == _ALERT_NEW_SALARY_ACCT, F.lit(1)).otherwise(
                F.lit(0)
            )
        )
        .cast("int")
        .alias("a1_new_salary_acct_flag"),
        F.max(
            F.when(
                F.col("_alert_type").startswith(_ALERT_OFFUS_PAYING_PREFIX), F.lit(1)
            ).otherwise(F.lit(0))
        )
        .cast("int")
        .alias("a1_offus_paying_flag"),
    )

    return result


def enrich_fea_bureau_alerts(
    cif_base: DataFrame,
    fea_aecb_alerts: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Salary-account signal from the retail.feature_space pre-engineered alert table.

    Second source for a1_new_salary_acct_flag — used alongside enrich_bureau_alerts
    (prm_bureau_alert_enriched) so that either source firing is sufficient.

    Source: fea_monthly_aecb_alerts (retail.feature_space).
    Grain: cif_id × month_number (last day of month, YYYY-MM-DD).
    Signal: ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum
        — 3-month rolling sum of salary-account-added-or-closed alerts.
          Non-zero → at least one salary account event in the 3-month window.

    Note: the feature space combines add + close into one flag.  We accept this
    as a corroborating signal; the primary source (prm_bureau_alert_enriched) is
    add-only and more precise.

    PIT join: latest month_number strictly before the calendar month of T0.
    This ensures the rolling window uses only complete months that precede T0,
    matching the ≈90-day pre-T0 window used by enrich_bureau_alerts.

    Schema guard: required columns absent → returns None (warning logged).
    Required columns: cif_id, month_number,
                      ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum

    Returns DataFrame with (account_id, spell_id, fea_salary_acct_flag: int 0/1)
    or None.
    """
    _FEA_SAL_COL = (
        "ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum"
    )
    _required = ["cif_id", "month_number", _FEA_SAL_COL]
    missing = [c for c in _required if c not in fea_aecb_alerts.columns]
    if missing:
        LOG.warning(
            "enrich_fea_bureau_alerts: fea_monthly_aecb_alerts missing %s"
            " — fea_salary_acct_flag will be NULL",
            missing,
        )
        return None

    fea_dated = fea_aecb_alerts.select(
        F.col("cif_id"),
        F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
            "_month_date"
        ),
        F.col(_FEA_SAL_COL).cast("double").alias("_sal_sum"),
    )

    # PIT: latest complete month strictly before the calendar month of T0
    joined = cif_base.join(fea_dated, on="cif_id", how="inner").filter(
        F.col("_month_date") < F.trunc(F.col(anchor_col), "month")
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    result = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.when(F.col("_sal_sum") > 0, F.lit(1))
            .otherwise(F.lit(0))
            .cast("int")
            .alias("fea_salary_acct_flag"),
        )
    )

    return result


def log_a1_stats(df: DataFrame) -> None:
    """Log state distribution for A1 ability axis."""
    state_counts = df.groupBy("a1_state").count().orderBy("a1_state").collect()
    total = sum(r["count"] for r in state_counts)
    LOG.info("build_a1_ability — state distribution (n=%d):", total)
    for row in state_counts:
        pct = 100.0 * row["count"] / max(total, 1)
        LOG.info(
            "  a1_state=%-25s  %6d  (%5.1f%%)",
            row["a1_state"],
            row["count"],
            pct,
        )
