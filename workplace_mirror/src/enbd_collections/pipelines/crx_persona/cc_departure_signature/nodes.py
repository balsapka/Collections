"""T06 — CC Departure Signature & History Shape Features.

Public nodes (15):
    build_departure_spell_base, build_departure_contract_cif,
    build_departure_pass_a, build_departure_pass_b, build_departure_pass_c,
    build_departure_pass_d, build_departure_pass_e, build_departure_pass_f,
    build_departure_pass_g, build_departure_pass_h, build_departure_pass_h2,
    build_departure_pass_i, build_departure_pass_j, build_departure_pass_k,
    build_departure_final

Output grain: (account_id, spell_id) — joins seamlessly with T04b/T05 outputs.

Window design (same convention as T04b/T05)::

    M0      = trunc(t0, 'month')                  — onset month (excluded)
    W_pre   = [w_pre_start, M0)                   — clean pre-delinquency window (≤12 months)
    H2      = [M0-3m, M0) → m_from_m0 1..3        — recent behaviour (T0-anchored)
    H1      = [w_pre_start, M0-3m) → m_from_m0 ≥ 4  — baseline
    H2_blk  = [block_date-3m, block_date) → m_from_block 1..3 — block-anchored (Pass A travel)

T0 leakage guard: all joins enforce strict obs_date < M0.

Pass A  — CC departure + fee signals from prm_transaction (travel_mcc_flag_h2,
          foreign_txn_share_h2, last_txn_foreign_flag; internal _fee_amt_h2)
Pass B  — CASA inflow signals from comp_financial_tran_repos_dly [COND: schema guard]
          (casa_inflow_stop_gap_d, eosb_like_flag)
Pass C  — History shape self-window from crx_cc_spell_table (prior_spell_cnt_24m,
          months_since_prior_spell, roll_speed_30_d, roll_speed_60_d)
Pass D  — Tenure + lifetime fees from prm_contract + prm_turnovers
          (tenure_at_t0_m, fee_rate_life, fee_accel_h2)
Pass E  — AECB leverage slope from int_bureau_pull_monthly (aecb_leverage_slope)
          [T21 DROP candidate — 0.11% bureau coverage on CC 60+ DPD book; code retained]
Pass F  — Relationship breadth from feat_product_holding (relationship_breadth)
Pass G  — AECB alert signals from fea_monthly_aecb_alerts (REUSE — retail.feature_space)
          (aecb_new_enquiry_3m, aecb_credit_opened_3m, aecb_total_alerts_3m)
Pass H  — Cross-border CASA outflow from feat_fx_leakage [COND: schema guard]
          (cross_border_outflow_amt_h2, cross_border_outflow_cnt_h2)
Pass H2 — Retail.feature_space CC travel+tours MCC from feat_cc_txns_rfs [COND: schema guard]
          (retail_travel_mcc_amt_h2, retail_travel_mcc_cnt_h2)
Pass I  — Payroll indicator from feat_payroll_indicator [COND: schema guard]
          (payroll_present_h2, payroll_stopped_flag)
Pass J  — Foreign login detection from prm_digital_login_monthly (OMB login logs)
          (foreign_login_flag, last_login_country_h2)
Pass K  — Bust-out / fraudster utilisation signals (crx_cc_transactions + prm_contract reuse)
          (limit_util_first_7d_flag, ever_paid_flag, max_7d_spend_ratio)
Nulls   — Always-NULL placeholders: cross_prod_t0_gap_d, simultaneous_default_flag

FILL-IN items (resolve before or during PROD run):
  FI-1: _SALARY_CODES — RESOLVED 2026-08-21 (sourced from WM income.py ENBD params)
  FI-2: _TRAN_DC_CREDIT — RESOLVED 2026-08-21 ('C' confirmed from WM ENBD entity config)
  FI-4: _CONTRACT_CIF_COL — confirmed 'client_id' from prm_contract schema
  FI-5: _CONTRACT_OPEN_DATE_COL — prm_contract column for account open date
  FI-6: _TURNOVERS_SNAPSHOT_COL — prm_turnovers snapshot date column name
  FI-7: _FEE_CATEGORY — exact value of CC fee tag in prm_transaction.txn_category
  FI-8: _PAYMENT_CATEGORY — exact value of CC payment tag in crx_cc_transactions.txn_category
"""

# pylint: disable=too-many-lines  # 13 private pass helpers (~1700 lines) + 15 thin public wrappers

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)

# ── Travel MCC codes (R14 — departure proxy, no protected attributes) ────────
# Source: ISO 18245 Merchant Category Codes (Visa/Mastercard published mapping).
# Scope: booking or using international travel services — strong departure proxy.
#   Airlines (brand codes):        3000-3299
#   Airlines (generic):            4511
#   Travel agencies/tour ops:      4722
#   Cruise / steamship lines:      4411  — added: clear departure signal
# Deliberately excluded (domestic-ambiguous; captured by is_international instead):
#   Hotels/lodging:                3501-3999, 7011
#   Car rentals:                   3351-3441, 7512, 7513
_TRAVEL_MCCS = list(set(range(3000, 3300)) | {4411, 4511, 4722})

# ── Travel keyword regex for txn_description fallback (Pass A) ───────────────
# Catches transactions where MCC is absent or miscoded (R14).
# Covers UAE-headquartered airlines and generic booking keywords.
# Case-insensitive via (?i); word-boundary anchors minimise false positives.
_TRAVEL_KEYWORDS_RE = (
    r"(?i)\b(AIRLINE|AIRWAYS|AIR TICKET|FLIGHT|AIRPORT|DEPARTURE|"
    r"EMIRATES AIR|ETIHAD|FLYDUBAI|AIR ARABIA|WIZZ AIR|BOARDING PASS)\b"
)

# ── FILL-IN constants ─────────────────────────────────────────────────────────
# FI-1: salary tran_particular_code values — sourced from
#   wealth_management/conf/enbd/parameters/parameters.yml → particular_codes_unique
#   (ENBD entity, confirmed 2026-08-21).  These are the codes that, when seen on a credit
#   transaction, positively identify a salary credit.
_SALARY_CODES = [
    "505",
    "506",
    "507",
    "503",
    "585",
    "586",
    "587",
    "588",
    "085",
    "086",
    "087",
    "088",
    "328",
    "828",
]
# Codes to EXCLUDE even if the narrative matches salary regex — from WM particular_codes_not_in
_SALARY_EXCLUDE_CODES = ["947", "LV3", "LV4"]

# FI-2: credit indicator in tran_dc column — confirmed 'C' from WM sal_casa_txns_part_tran_type
_TRAN_DC_CREDIT = "C"  # confirmed: matches wealth_management ENBD entity config


# FI-5: prm_contract column name for account open date
# 'open_date' confirmed from PROD schema (error: record_date_to unresolved;
# suggested columns include open_date, close_date, writeoff_date)
_CONTRACT_OPEN_DATE_COL = "open_date"  # confirmed from prm_contract schema

# FI-6: prm_turnovers snapshot date column — confirmed 'observation_date' from primary layer
_TURNOVERS_SNAPSHOT_COL = "observation_date"  # confirmed from prm_cc.py rename mapping

# FI-7: CC fee tag in prm_transaction.txn_category (exact string value)
_FEE_CATEGORY = "fee"  # <<FILL-IN: verify exact value in PROD>>

# FI-8: CC payment category tag in crx_cc_transactions.txn_category
_PAYMENT_CATEGORY = "payment"  # <<FILL-IN: verify exact value in PROD>>

# ── Pass H column names ───────────────────────────────────────────────────────
# Source: feat_fx_leakage = fea_monthly_agg_fx_leakage (retail.feature_space).
# Pre-rolled 3-month sum; covers H2 = [M0-3m, M0) at the last H2 month.
# T06d (2026-08-26): feat_casa_txns had no cross-border columns — correct source is
# fea_monthly_agg_fx_leakage which derives is_cross_border_outflow_txn from
# counter_party_bank_cntry in raw FTR transactions.
_FX_CB_AMT_COL = "ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum"
# No pre-rolled count equivalent in fea_monthly_agg_fx_leakage — cross_border_outflow_cnt_h2
# emits NULL. T21 candidate for formal dropping.
_FX_CB_CNT_COL: str | None = None  # absent — T21 candidate

# ── Pass H2 column names (PROD schema probe required — T06d) ─────────────────
# Source: feat_cc_txns_rfs = fea_cc_inflow_outflow_txns_monthly
# The ft_ prefix and window suffix are added downstream; bare column at source grain.
_CC_TRAVEL_AMT_COL = "outflow_cc_mcc_travel_and_tours_amt"
_CC_TRAVEL_CNT_COL = "outflow_cc_mcc_travel_and_tours_count"

# ── Pass I column names ───────────────────────────────────────────────────────
# Source: feat_payroll_indicator = pri_monthly_payroll_indicator
# T06d (2026-08-26): confirmed actual column name is "payroll_flag" (0/1 per month row).
_PAYROLL_HAS_COL = "payroll_flag"  # confirmed via t06d 2026-08-26


# ── Public nodes ──────────────────────────────────────────────────────────────


def build_departure_spell_base(
    crx_cc_spell_table: DataFrame,
    crx_cc_payment_trajectory: DataFrame,
    cc_spine: DataFrame,
) -> DataFrame:
    """Build spell base with T04b truncation columns (Node 1 of 15).

    Filters crx_cc_spell_table to non-censored spells and inner-joins
    the W_pre truncation columns from crx_cc_payment_trajectory.
    Also derives block_date (t0 + days_to_dpd60) and spine_obs_date for
    downstream passes that anchor windows on card-block or observation date.

    Args:
        crx_cc_spell_table:        T03b spell table (all spells including censored).
        crx_cc_payment_trajectory: T04b output carrying w_pre truncation columns.
        cc_spine:                  Spine table with observation_date per contract.

    Returns:
        DataFrame at grain (account_id, spell_id) with t0, prior_spell_end,
        days_to_dpd30/60, all w_pre_* columns, block_date, and spine_obs_date.
    """
    # Excludes both censored subtypes (data_depth + restructured_entry) — see
    # cc_payment_trajectory/nodes.py Step 0 comment for rationale.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id",
        "spell_id",
        "t0",
        "prior_spell_end",
        "days_to_dpd30",
        "days_to_dpd60",
    )
    trunc = crx_cc_payment_trajectory.select(
        "account_id",
        "spell_id",
        "w_pre_start",
        "w_pre_clean_m",
        "w_pre_contaminated_flag",
        "w_pre_truncation_reason",
    )
    # Derive block_date: t0 + days_to_dpd60 (NULL-safe fallback to M0)
    result = spell.join(trunc, on=["account_id", "spell_id"], how="inner").withColumn(
        "block_date",
        F.when(
            F.col("days_to_dpd60").isNotNull(),
            F.expr("date_add(t0, cast(days_to_dpd60 as int))"),
        ).otherwise(F.trunc(F.col("t0"), "month")),
    )

    # Join cc_spine for spine_obs_date (latest obs_date per account — typically one row)
    spine_obs = cc_spine.groupBy("contract_id").agg(
        F.max("observation_date").alias("spine_obs_date")
    )
    return result.join(
        spine_obs.withColumnRenamed("contract_id", "_spine_ctr"),
        result["account_id"] == F.col("_spine_ctr"),
        how="left",
    ).drop("_spine_ctr")


def build_departure_contract_cif(
    prm_contract: DataFrame,
    prm_client: DataFrame,
) -> DataFrame:
    """Build contract_id → cif_id bridge (Node 2 of 15).

    Maps Way4 client_idt (prm_contract.client_id) → bank CIF (prm_client.cif_id).
    Pattern mirrors spine_builders.py::finalize_contract_spine().

    Both prm_contract and prm_client expose 'client_id' after primary-layer renaming
    (client_idt → client_id in both). Aliasing to '_way4_cid' is defensive PySpark
    practice (prevents ambiguity if column sets shift) and signals semantic intent:
    this is the Way4 system ID, NOT the bank CIF.

    Args:
        prm_contract:  Primary CC contracts. Required cols: contract_id, client_id.
        prm_client:    Primary client dimension. Required cols: client_id, cif_id.

    Returns:
        DataFrame at grain contract_id with columns (contract_id, cif_id).
    """
    return (
        prm_contract.select("contract_id", F.col("client_id").alias("_way4_cid"))
        .join(
            prm_client.select(F.col("client_id").alias("_way4_cid"), "cif_id"),
            on="_way4_cid",
            how="left",
        )
        .select("contract_id", "cif_id")
        .dropDuplicates(["contract_id"])
    )


def build_departure_pass_a(
    crx_cc_transactions: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """CC departure signals + H2 fee amount (Node 3 of 15).

    Wraps _build_pass_a. Returns full output including _fee_amt_h2 — this
    intermediate column is consumed by build_departure_pass_d and dropped
    in build_departure_final before the final join.

    Args:
        crx_cc_transactions:    T04c intermediate — T0-scoped CC transactions.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with travel_mcc_flag_h2,
        foreign_txn_share_h2, last_txn_foreign_flag, _fee_amt_h2.

        Anchor semantics (T06 anchor-change):
            travel_mcc_flag_h2 / foreign_txn_share_h2 — H2 anchored on block_date
                (card-block date = t0 + days_to_dpd60), window [block-3m, block).
            last_txn_foreign_flag — most recent transaction before spine_obs_date
                (extends W_pre right boundary to obs_date, covering the T0→block gap).
            _fee_amt_h2 — still T0-anchored [M0-3m, M0) (unchanged; used by Pass D).
    """
    return _build_pass_a(crx_cc_transactions, spell_w)


def build_departure_pass_b(
    comp_financial_tran_repos_dly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """CASA inflow stop signals (Node 4 of 15).

    Wraps _build_pass_b. Schema guard emits NULL if required columns absent.

    Args:
        comp_financial_tran_repos_dly:  Raw CASA transactions (2.4B rows, R20).
        contract_cif:                   crx_cc_departure_contract_cif output.
        spell_w:                        crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with casa_inflow_stop_gap_d,
        eosb_like_flag.
    """
    return _build_pass_b(comp_financial_tran_repos_dly, contract_cif, spell_w)


def build_departure_pass_c(
    crx_cc_spell_table: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """History shape from spell table self-window (Node 5 of 15).

    Wraps _build_pass_c. Needs original spell table (including censored spells)
    for the 24-month prior-spell lookback.

    Args:
        crx_cc_spell_table: T03b spell table (all spells, unfiltered).
        spell_w:            crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with prior_spell_cnt_24m,
        months_since_prior_spell, roll_speed_30_d, roll_speed_60_d.
    """
    return _build_pass_c(crx_cc_spell_table, spell_w)


def build_departure_pass_d(
    prm_contract: DataFrame,
    prm_turnovers: DataFrame,
    spell_w: DataFrame,
    pass_a_df: DataFrame,
) -> DataFrame:
    """Tenure and lifetime fee velocity features (Node 6 of 15).

    Extracts _fee_amt_h2 from pass_a_df and passes it to _build_pass_d.

    Args:
        prm_contract:   Primary CC contracts (SCD2 via observation_date).
        prm_turnovers:  Primary CC lifetime turnover snapshots.
        spell_w:        crx_cc_departure_spell_base output.
        pass_a_df:      crx_cc_departure_pass_a output (includes _fee_amt_h2).

    Returns:
        DataFrame at (account_id, spell_id) with tenure_at_t0_m,
        fee_rate_life, fee_accel_h2.
    """
    fee_feats = pass_a_df.select("account_id", "spell_id", "_fee_amt_h2")
    return _build_pass_d(prm_contract, prm_turnovers, spell_w, fee_feats)


def build_departure_pass_e(
    int_bureau_pull_monthly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """AECB leverage slope via OLS (Node 7 of 15).

    Wraps _build_pass_e. T21 DROP confirmed — all values NULL in production.

    Args:
        int_bureau_pull_monthly:  AECB monthly pull snapshots.
        contract_cif:             crx_cc_departure_contract_cif output.
        spell_w:                  crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with aecb_leverage_slope.
    """
    return _build_pass_e(int_bureau_pull_monthly, contract_cif, spell_w)


def build_departure_pass_f(
    feat_product_holding: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Relationship breadth from feat_product_holding (Node 8 of 15).

    Inlines the cif_id → account_id and month_number → observation_date
    normalisation before calling _build_pass_f (original lines 318–327).

    Args:
        feat_product_holding:   fea_timeseries_based_product_holding.
                                Grain cif_id × month_number (yyyyMMdd); normalised
                                to account_id × observation_date before _build_pass_f.
        contract_cif:           crx_cc_departure_contract_cif output.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with relationship_breadth.
    """
    _ph_cols = {c.lower() for c in feat_product_holding.columns}
    if "cif_id" in _ph_cols and "account_id" not in _ph_cols:
        _cif_map = contract_cif.withColumnRenamed("contract_id", "account_id")
        feat_product_holding = feat_product_holding.join(
            _cif_map, on="cif_id", how="inner"
        )
    if "month_number" in _ph_cols and "observation_date" not in _ph_cols:
        feat_product_holding = feat_product_holding.withColumn(
            "observation_date", F.to_date(F.col("month_number"), "yyyyMMdd")
        )
    return _build_pass_f(feat_product_holding, spell_w)


def build_departure_pass_g(
    fea_monthly_aecb_alerts: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """AECB alert signals — REUSE from retail.feature_space (Node 9 of 15).

    Wraps _build_pass_g. Schema guard emits NULL if required columns absent.

    Args:
        fea_monthly_aecb_alerts:  AECB alert feature table (retail.feature_space).
        contract_cif:             crx_cc_departure_contract_cif output.
        spell_w:                  crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with aecb_new_enquiry_3m,
        aecb_credit_opened_3m, aecb_total_alerts_3m.
    """
    return _build_pass_g(fea_monthly_aecb_alerts, contract_cif, spell_w)


def build_departure_pass_h(
    feat_fx_leakage: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Cross-border CASA outflow signals (Node 10 of 15).

    Wraps _build_pass_h. Schema guard emits NULL if required columns absent.

    Args:
        feat_fx_leakage:  fea_monthly_agg_fx_leakage (retail.feature_space).
        contract_cif:     crx_cc_departure_contract_cif output.
        spell_w:          crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with cross_border_outflow_amt_h2,
        cross_border_outflow_cnt_h2.
    """
    return _build_pass_h(feat_fx_leakage, contract_cif, spell_w)


def build_departure_pass_h2(
    feat_cc_txns_rfs: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Retail.feature_space CC travel+tours MCC signals (Node 11 of 15).

    Wraps _build_pass_h2. Schema guard emits NULL if required columns absent.

    Args:
        feat_cc_txns_rfs:  fea_cc_inflow_outflow_txns_monthly (retail.feature_space).
        contract_cif:      crx_cc_departure_contract_cif output.
        spell_w:           crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with retail_travel_mcc_amt_h2,
        retail_travel_mcc_cnt_h2.
    """
    return _build_pass_h2(feat_cc_txns_rfs, contract_cif, spell_w)


def build_departure_pass_i(
    feat_payroll_indicator: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Payroll presence and stop signals (Node 12 of 15).

    Wraps _build_pass_i. Schema guard emits NULL if required columns absent.

    Args:
        feat_payroll_indicator: pri_monthly_payroll_indicator (retail.feature_space).
        contract_cif:           crx_cc_departure_contract_cif output.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with payroll_present_h2,
        payroll_stopped_flag.
    """
    return _build_pass_i(feat_payroll_indicator, contract_cif, spell_w)


def build_departure_pass_j(
    prm_digital_login_monthly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Foreign login detection from OMB login logs (Node 13 of 15).

    Wraps _build_pass_j. Schema guard emits NULL if required columns absent.

    Args:
        prm_digital_login_monthly:  Monthly OMB login aggregation.
        contract_cif:               crx_cc_departure_contract_cif output.
        spell_w:                    crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with foreign_login_flag,
        last_login_country_h2.

        Anchor semantics (T06 anchor-change):
            foreign_login_flag — most recent login before spine_obs_date (not [T0-3m, T0)).
            Login can occur post-card-block (digital channel stays active), so obs_date
            is the correct ceiling; fallback to M0 if spine_obs_date is NULL.
    """
    return _build_pass_j(prm_digital_login_monthly, contract_cif, spell_w)


def build_departure_pass_k(
    crx_cc_transactions: DataFrame,
    prm_contract: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Bust-out / fraudster utilisation signals (Node 14 of 15).

    Wraps _build_pass_k. Reuses crx_cc_transactions (Pass A source) and
    prm_contract (Pass D source); no new inputs.

    Args:
        crx_cc_transactions:    T04c intermediate — T0-scoped CC transactions.
        prm_contract:           Primary CC contracts.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with ever_paid_flag,
        limit_util_first_7d_flag, max_7d_spend_ratio.
    """
    return _build_pass_k(crx_cc_transactions, prm_contract, spell_w)


def build_departure_final(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    spell_w: DataFrame,
    pass_a: DataFrame,
    pass_b: DataFrame,
    pass_c: DataFrame,
    pass_d: DataFrame,
    pass_e: DataFrame,
    pass_f: DataFrame,
    pass_g: DataFrame,
    pass_h: DataFrame,
    pass_h2: DataFrame,
    pass_i: DataFrame,
    pass_j: DataFrame,
    pass_k: DataFrame,
) -> DataFrame:
    """Assemble all pass outputs into the final departure signature (Node 15 of 15).

    Left-joins all pass outputs onto spell_w. Drops _fee_amt_h2 from pass_a
    before joining (internal column consumed by Pass D; not in final schema).
    Adds always-NULL placeholder columns. Calls _log_departure_stats.
    Applies final typed .select() to enforce schema contract.

    Args:
        spell_w:    crx_cc_departure_spell_base — the grain anchor.
        pass_a:     crx_cc_departure_pass_a (includes _fee_amt_h2 — dropped here).
        pass_b..k:  crx_cc_departure_pass_b through crx_cc_departure_pass_k.

    Returns:
        DataFrame at (account_id, spell_id) — 36-column typed departure signature.
        Schema is identical to the pre-refactor build_cc_departure_signature output.
    """
    result = (
        spell_w.join(
            pass_a.drop("_fee_amt_h2"), on=["account_id", "spell_id"], how="left"
        )
        .join(pass_b, on=["account_id", "spell_id"], how="left")
        .join(pass_c, on=["account_id", "spell_id"], how="left")
        .join(pass_d, on=["account_id", "spell_id"], how="left")
        .join(pass_e, on=["account_id", "spell_id"], how="left")
        .join(pass_f, on=["account_id", "spell_id"], how="left")
        .join(pass_g, on=["account_id", "spell_id"], how="left")
        .join(pass_h, on=["account_id", "spell_id"], how="left")
        .join(pass_h2, on=["account_id", "spell_id"], how="left")
        .join(pass_i, on=["account_id", "spell_id"], how="left")
        .join(pass_j, on=["account_id", "spell_id"], how="left")
        .join(pass_k, on=["account_id", "spell_id"], how="left")
        # Always-NULL placeholders (confirmed absent from all repos in T01 reuse map)
        .withColumn("cross_prod_t0_gap_d", F.lit(None).cast("double"))
        .withColumn("simultaneous_default_flag", F.lit(None).cast("int"))
        .withColumn("computed_at", F.current_timestamp())
    )

    _log_departure_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
        F.col("foreign_txn_share_h2").cast("double"),
        F.col("last_txn_foreign_flag").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
        F.col("eosb_like_flag").cast("int"),
        F.col("foreign_login_flag").cast("int"),
        F.col("last_login_country_h2").cast("string"),
        F.col("fee_rate_life").cast("double"),
        F.col("fee_accel_h2").cast("double"),
        F.col("tenure_at_t0_m").cast("int"),
        F.col("prior_spell_cnt_24m").cast("int"),
        F.col("months_since_prior_spell").cast("int"),
        F.col("roll_speed_30_d").cast("int"),
        F.col("roll_speed_60_d").cast("int"),
        F.col("cross_prod_t0_gap_d").cast("double"),
        F.col("simultaneous_default_flag").cast("int"),
        F.col("aecb_leverage_slope").cast("double"),
        F.col("relationship_breadth").cast("int"),
        F.col("aecb_new_enquiry_3m").cast("int"),
        F.col("aecb_credit_opened_3m").cast("int"),
        F.col("aecb_total_alerts_3m").cast("int"),
        F.col("cross_border_outflow_amt_h2").cast("double"),
        F.col("cross_border_outflow_cnt_h2").cast("int"),
        F.col("retail_travel_mcc_amt_h2").cast("double"),
        F.col("retail_travel_mcc_cnt_h2").cast("int"),
        F.col("payroll_present_h2").cast("int"),
        F.col("payroll_stopped_flag").cast("int"),
        F.col("limit_util_first_7d_flag").cast("int"),
        F.col("ever_paid_flag").cast("int"),
        F.col("max_7d_spend_ratio").cast("double"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("computed_at"),
    )


# ── Private: Pass A ───────────────────────────────────────────────────────────


def _build_pass_a(prm_transaction: DataFrame, spell_w: DataFrame) -> DataFrame:
    """CC departure signals and H2 fee amount from crx_cc_transactions.

    Business purpose: captures intent to leave UAE before the delinquency onset (T0).
    At 61+ DPD accounts go Block-X (no new transactions), so departure signals must
    come from the pre-delinquency window.  A customer booking flights or making
    foreign transactions in the 3 months before T0 is a strong flight-risk indicator.

    Window terminology (same as module header):
        M0      = trunc(t0, 'month')                  — onset month (excluded from all windows)
        H2      = [M0-3m, M0) → m_from_m0 in [1, 3]   — T0-anchored (fee signals only)
        H1      = [w_pre_start, M0-3m) → m_from_m0 >= 4 — baseline
        W_pre   = [w_pre_start, obs_ceil)             — extended to spine_obs_date (covers T0→block gap)
        H2_blk  = [block-3m, block) → m_from_block in [1, 3] — block-anchored (travel signals)
        block   = t0 + days_to_dpd60                  — card-block date

    Detection strategy (Sub-pass A1):
        Primary — MCC-based: travel MCCs (ISO 18245: airlines 3000–3299/4511,
            cruise 4411, travel agencies 4722) identify explicit travel bookings.
        Fallback — txn_description keyword: catches transactions where the MCC is
            absent or miscoded (common for aggregated/wallet payments).  Mirrors the
            dual particular-code + narration pattern used for salary in Pass B.
        Combined: is_travel = is_travel_mcc | is_travel_desc

    Sub-pass A1 — departure:
        travel_mcc_flag_h2          : 1 if any H2_blk txn matches travel MCC or keyword;
                                      0 if H2_blk txns exist but none match;
                                      NULL if no H2_blk txns (left-join result — treat as 0
                                      downstream; do NOT coalesce to 0 here to distinguish
                                      "no travel" from "no data").
                                      Anchored on block_date (not T0) — captures bookings in
                                      the T0→block window that T0-anchoring missed.
        foreign_txn_share_h2        : mean(is_international) over H2_blk txns;
                                      NULL if no H2_blk txns (avg of empty set).
                                      Anchored on block_date for same reason as above.
        last_txn_foreign_flag       : is_international of the last transaction before
                                      spine_obs_date (extended from old M0 ceiling);
                                      NULL if no W_pre transactions at all.

    Sub-pass A2 — fee velocity intermediate:
        _fee_amt_h2                 : sum(abs(txn_amount_aed)) for H2 fee transactions;
                                      0.0 if H2 transactions exist but none are fee-type
                                      (coalesced in aggregation, never NULL).
                                      Still T0-anchored [M0-3m, M0) — unchanged; used by
                                      Pass D to compute fee_accel_h2.
    """
    scope = spell_w.select("account_id").distinct()

    txn = prm_transaction.select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("merchant_category_code"),
        F.col("is_international"),
        F.col("txn_amount_aed"),
        F.col("txn_category"),
        F.col("txn_description"),
    ).join(
        F.broadcast(scope),
        prm_transaction["contract_id"] == scope["account_id"],
        "leftsemi",
    )

    # Join to spell and filter to W_pre: [w_pre_start, _obs_ceil)
    # _obs_ceil extends the right boundary to spine_obs_date (fallback: block_date)
    # so transactions in the T0→card-block gap are captured for last_txn_foreign_flag
    # and the block-anchored travel window.
    txn_w = (
        txn.join(spell_w, on=(txn["contract_id"] == spell_w["account_id"]), how="inner")
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("merchant_category_code"),
            F.col("is_international"),
            F.col("txn_amount_aed"),
            F.col("txn_category"),
            F.col("txn_description"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
            F.col("block_date"),
            F.coalesce(F.col("spine_obs_date"), F.col("block_date")).alias("_obs_ceil"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.col("_obs_ceil"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
        .withColumn(
            "m_from_block",
            F.floor(
                F.months_between(
                    F.trunc(F.col("block_date"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
    )

    # Travel detection: MCC-based (primary) OR txn_description keyword fallback.
    # The narration fallback mirrors the salary narration pattern in Pass B,
    # covering cases where the MCC is absent or miscoded.
    mcc_int_col = F.col("merchant_category_code").cast("int")
    is_travel = (mcc_int_col.isNotNull() & mcc_int_col.isin(_TRAVEL_MCCS)) | F.upper(
        F.coalesce(F.col("txn_description"), F.lit(""))
    ).rlike(_TRAVEL_KEYWORDS_RE)

    # h2: T0-anchored — used only for _fee_amt_h2 (fee velocity; unchanged)
    # h2_block: block_date-anchored — used for travel features
    h2 = (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3)
    h2_block = (F.col("m_from_block") >= 1) & (F.col("m_from_block") <= 3)

    # Fee detection: exact category first, narration fallback (FI-7)
    fee_cond = (F.col("txn_category") == F.lit(_FEE_CATEGORY)) | F.upper(
        F.coalesce(F.col("txn_description"), F.lit(""))
    ).rlike(r"(?i)\bFEE\b|\bCHARGE\b|\bANNUAL\b")

    # Window to identify last transaction per spell (for last_txn_foreign_flag)
    txn_ranked = txn_w.withColumn(
        "_last_rank",
        F.row_number().over(
            Window.partitionBy("account_id", "spell_id").orderBy(
                F.col("txn_date").desc()
            )
        ),
    )

    agg = txn_ranked.groupBy("account_id", "spell_id").agg(
        # A1 — departure signals (block_date-anchored for travel; obs_date ceiling for last-txn)
        F.max(F.when(h2_block & is_travel, F.lit(1)).otherwise(F.lit(0))).alias(
            "travel_mcc_flag_h2"
        ),
        F.avg(F.when(h2_block, F.col("is_international").cast("double"))).alias(
            "foreign_txn_share_h2"
        ),
        F.first(
            F.when(F.col("_last_rank") == 1, F.col("is_international").cast("int")),
            ignorenulls=True,
        ).alias("last_txn_foreign_flag"),
        # A2 — H2 fee amount (internal; used by Pass D)
        F.sum(
            F.when(h2 & fee_cond, F.abs(F.col("txn_amount_aed"))).otherwise(F.lit(0.0))
        ).alias("_fee_amt_h2"),
    )

    return agg.select(
        "account_id",
        "spell_id",
        "travel_mcc_flag_h2",
        "foreign_txn_share_h2",
        "last_txn_foreign_flag",
        "_fee_amt_h2",
    )


# ── Private: Pass B ───────────────────────────────────────────────────────────


def _build_pass_b(  # pylint: disable=too-many-locals
    comp_financial_tran_repos_dly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """CASA inflow stop signals from raw transaction table (conditional).

    Business purpose: captures salary disruption and End-of-Service Benefit (EOSB)
    patterns in the customer's CASA account before T0.  A salary stopping or a large
    terminal credit (EOSB payout) shortly before delinquency onset is a strong
    indicator of job loss / departure — directly correlated with cure probability.

    Detection strategy: dual-signal salary identification mirrors WM income.py ENBD
    entity logic (FI-1 resolved 2026-08-21).  A transaction is salary if:
      (1) credit side (tran_dc == 'C') AND not an excluded code AND
      (2) either a known salary particular_code OR tran_narration_1 matches a
          salary keyword regex (SALARY|PAYROLL|INCENTIVE|BONUS|OVERTIME|COMMISSION …).
    This two-path approach handles both structured SWIFT credits (code present) and
    direct/payroll credits that arrive with no structured code but a descriptive narration.

    R20 compliance: CIF-level leftsemi scope applied *before* any date filter
    to limit the 2.4B-row scan.

    Schema guard: if required CASA columns are absent, emits NULL for both
    features and logs a warning.

    Features::

        casa_inflow_stop_gap_d  : days between last salary-like credit and M0;
                                  NULL if no salary-like inflow found in [M0-24, M0).
        eosb_like_flag          : 1 if any single salary credit in [M0-6, M0)
                                  exceeds 3× the monthly median over [M0-24, M0-6)
                                  AND casa_inflow_stop_gap_d <= 90 days;
                                  0 if data present but condition not met;
                                  NULL if monthly_salary_median cannot be computed
                                  (i.e. fewer than one salary month in the baseline window).
    """
    _CASA_REQUIRED = [
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ]
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    missing = [c for c in _CASA_REQUIRED if c not in casa_cols_lower]

    if missing:
        LOG.warning(
            "Pass B [CASA]: missing columns %s in comp_financial_tran_repos_dly "
            "— emitting NULL for casa_inflow_stop_gap_d and eosb_like_flag",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("casa_inflow_stop_gap_d", F.lit(None).cast("double"))
            .withColumn("eosb_like_flag", F.lit(None).cast("int"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select("cif_id").distinct()

    # R20 — scope CASA via CIF IDs before any other filter
    casa_scoped = comp_financial_tran_repos_dly.select(
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # Salary detection — mirrors WM income.py ENBD entity logic (FI-1 resolved 2026-08-21):
    # credit transaction AND NOT an excluded code AND (positive code OR narrative match)
    is_salary = (
        (F.col("tran_dc") == _TRAN_DC_CREDIT)
        & ~F.col("tran_particular_code").isin(_SALARY_EXCLUDE_CODES)
        & (
            F.col("tran_particular_code").isin(_SALARY_CODES)
            | F.upper(F.coalesce(F.col("tran_narration_1"), F.lit(""))).rlike(
                r"SALARY|PAYROLL|SALAR|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK"
            )
        )
    )

    # Join to spell_cif to get (account_id, spell_id, t0) per transaction
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.withColumnRenamed("_ctr_id", "account_id"),
        on="account_id",
        how="left",
    )

    casa_w = (
        casa_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("tran_dc") == _TRAN_DC_CREDIT)
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn("is_salary", is_salary)
    )

    # ── Gap feature: last salary credit date ──────────────────────────────────
    last_sal = (
        casa_w.filter(F.col("is_salary"))
        .groupBy("account_id", "spell_id", "t0")
        .agg(F.max("tran_date").alias("last_sal_date"))
        .withColumn(
            "casa_inflow_stop_gap_d",
            F.datediff(F.trunc(F.col("t0"), "month"), F.col("last_sal_date")).cast(
                "double"
            ),
        )
        .select("account_id", "spell_id", "casa_inflow_stop_gap_d")
    )

    # ── EOSB flag: monthly salary median [M0-24, M0-6) vs large credit in [M0-6, M0)
    monthly_sal = (
        casa_w.filter(F.col("is_salary"))
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("tran_date"), "month"),
                )
            ).cast("int"),
        )
        .groupBy("account_id", "spell_id", "m_from_m0")
        .agg(F.sum("tran_amt_aed").alias("monthly_sal_total"))
    )

    # Baseline median: m_from_m0 in [7, 24] → months [M0-24m, M0-6m)
    sal_median = (
        monthly_sal.filter((F.col("m_from_m0") >= 7) & (F.col("m_from_m0") <= 24))
        .groupBy("account_id", "spell_id")
        .agg(
            F.percentile_approx("monthly_sal_total", 0.5).alias("monthly_salary_median")
        )
    )

    # Max single salary credit in recent window: m_from_m0 in [1, 6] → [M0-6m, M0)
    recent_max = (
        casa_w.filter(
            F.col("is_salary")
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -6))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.max("tran_amt_aed").alias("max_sal_recent"))
    )

    eosb = (
        spell_w.select("account_id", "spell_id")
        .join(last_sal, on=["account_id", "spell_id"], how="left")
        .join(sal_median, on=["account_id", "spell_id"], how="left")
        .join(recent_max, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "eosb_like_flag",
            F.when(
                # Cannot evaluate if no baseline median
                F.col("monthly_salary_median").isNull(),
                F.lit(None).cast("int"),
            )
            .when(
                # Condition met: single large credit + salary stopped recently
                F.col("max_sal_recent").isNotNull()
                & (F.col("monthly_salary_median") > 0)
                & (F.col("max_sal_recent") > 3.0 * F.col("monthly_salary_median"))
                & F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= 90.0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "spell_id", "casa_inflow_stop_gap_d", "eosb_like_flag")
    )

    return eosb


# ── Private: Pass C ───────────────────────────────────────────────────────────


def _build_pass_c(crx_cc_spell_table: DataFrame, spell_w: DataFrame) -> DataFrame:
    """History shape features from crx_cc_spell_table self-window.

    Business purpose: characterises the delinquency history pattern of the account.
    Repeat delinquency within 24 months signals systemic financial stress rather than
    a one-off event; rapid roll speed (days to reach 30/60 DPD) predicts trajectory
    toward 180+ DPD.  These features are available without any new data sources —
    pure self-joins on the already-built spell table.

    Detection strategy: self-join on crx_cc_spell_table using (account_id, spell_id)
    to find prior spells.  prior_spell_cnt_24m counts by spell_id < current and t0
    within the 24-month lookback.  roll_speed_* are direct pass-throughs computed
    by T03b (days from first missed payment to each DPD threshold).

    All features are free reads from the existing spell table — no new data sources.

    Features::

        prior_spell_cnt_24m     : count of prior spells (same account_id, lower
                                  spell_id) whose t0 falls in [t0_current-24m, t0_current);
                                  0 if no qualifying prior spells (never NULL — coalesced).
        months_since_prior_spell: floor(months_between(t0, prior_spell_end));
                                  NULL for first spell (prior_spell_end is NULL in T03b).
        roll_speed_30_d         : days_to_dpd30 pass-through from spell table;
                                  NULL if the account never reached 30 DPD in this spell.
        roll_speed_60_d         : days_to_dpd60 pass-through from spell table;
                                  NULL if the account never reached 60 DPD in this spell.
    """
    # All spells (including censored) — used only for prior-spell counting
    prior_candidates = crx_cc_spell_table.select(
        F.col("account_id"),
        F.col("spell_id").alias("prior_spell_id"),
        F.col("t0").alias("prior_t0"),
    )

    current = spell_w.select("account_id", "spell_id", "t0")

    prior_cnt = (
        current.join(prior_candidates, on="account_id", how="left")
        .filter(
            (F.col("prior_spell_id") < F.col("spell_id"))
            & (F.col("prior_t0") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("prior_t0") < F.col("t0"))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.count("prior_spell_id").alias("prior_spell_cnt_24m"))
    )

    result = (
        spell_w.select(
            "account_id",
            "spell_id",
            "t0",
            "prior_spell_end",
            "days_to_dpd30",
            "days_to_dpd60",
        )
        .join(prior_cnt, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "prior_spell_cnt_24m",
            # 0 for first spells or accounts with no recent prior spells
            F.coalesce(F.col("prior_spell_cnt_24m"), F.lit(0)),
        )
        .withColumn(
            "months_since_prior_spell",
            F.when(
                F.col("prior_spell_end").isNotNull(),
                F.floor(F.months_between(F.col("t0"), F.col("prior_spell_end"))).cast(
                    "int"
                ),
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumnRenamed("days_to_dpd30", "roll_speed_30_d")
        .withColumnRenamed("days_to_dpd60", "roll_speed_60_d")
    )

    return result.select(
        "account_id",
        "spell_id",
        "prior_spell_cnt_24m",
        "months_since_prior_spell",
        "roll_speed_30_d",
        "roll_speed_60_d",
    )


# ── Private: Pass D ───────────────────────────────────────────────────────────


def _build_pass_d(
    prm_contract: DataFrame,
    prm_turnovers: DataFrame,
    spell_w: DataFrame,
    fee_feats: DataFrame,
) -> DataFrame:
    """Tenure and lifetime fee velocity features.

    Business purpose: captures whether the customer has a history of incurring
    late/overlimit fees relative to their account lifetime.  A high fee_rate_life
    signals chronic near-limit behaviour; fee_accel_h2 > 1 means fees
    accelerated in the 3 months before T0, an early stress indicator.  Tenure
    contextualises risk: short-tenure accounts with high fees are higher risk than
    long-tenure accounts with the same absolute fee amount.

    PIT join pattern:
        prm_contract  : take row with latest observation_date <= t0 per account
        prm_turnovers : take row with latest observation_date <= t0 per account

    fee_feats is (account_id, spell_id, _fee_amt_h2) from Pass A.

    Features::

        tenure_at_t0_m          : floor(months_between(M0, account_open_date));
                                  NULL if account_open_date is NULL in prm_contract.
        fee_rate_life           : (ltd_late_fee_amount + ltd_overlimit_fee_amount)
                                  / max(tenure_at_t0_m, 1);
                                  0.0 if both fee columns are NULL (coalesced to 0);
                                  NULL if no prm_contract snapshot on or before t0.
        fee_accel_h2            : (H2 fees / H2 months) / fee_rate_life;
                                  H2 months = min(w_pre_clean_m, 3) to avoid
                                  over-denominating short windows;
                                  NULL if fee_rate_life is NULL or zero, or if
                                  _fee_amt_h2 is NULL, or if _h2_months is 0.
    """
    spell_base = spell_w.select(
        F.col("account_id"),
        F.col("spell_id"),
        F.col("t0"),
        F.col("w_pre_clean_m"),
    )

    scope = spell_base.select("account_id").distinct()

    # ── Tenure: PIT join prm_contract (snapshot via observation_date) ─────────
    # prm_contract uses observation_date (renamed from banking_date in primary layer).
    # Take latest snapshot on or before t0 per account.
    contract_scoped = prm_contract.select(
        F.col("contract_id").alias("_ctr_id"),
        F.col(_CONTRACT_OPEN_DATE_COL).alias("account_open_date"),
        F.col("observation_date").alias("_eff_start"),
    ).join(
        F.broadcast(scope),
        F.col("_ctr_id") == F.col("account_id"),
        "leftsemi",
    )

    contract_pit = (
        spell_base.join(
            contract_scoped,
            on=(spell_base["account_id"] == contract_scoped["_ctr_id"]),
            how="left",
        )
        .filter(F.col("_eff_start") <= F.col("t0"))
        .withColumn(
            "_rn_ctr",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_eff_start").desc()
                )
            ),
        )
        .filter(F.col("_rn_ctr") == 1)
        .withColumn(
            "tenure_at_t0_m",
            F.when(
                F.col("account_open_date").isNotNull(),
                F.floor(
                    F.months_between(
                        F.trunc(F.col("t0"), "month"),
                        F.trunc(F.col("account_open_date"), "month"),
                    )
                ).cast("int"),
            ).otherwise(F.lit(None).cast("int")),
        )
        .select("account_id", "spell_id", "tenure_at_t0_m")
    )

    # ── Lifetime fees: PIT join prm_turnovers ─────────────────────────────────
    # prm_turnovers exposes the two fee-type columns; no pre-computed total exists.
    # Both are stored positive in the primary layer (Way4 sign=-1 absorbed upstream).
    turnovers_scoped = prm_turnovers.select(
        F.col("contract_id").alias("_tov_id"),
        F.col(_TURNOVERS_SNAPSHOT_COL).alias("_snap_date"),
        F.col("ltd_late_fee_amount"),
        F.col("ltd_overlimit_fee_amount"),
    ).join(
        F.broadcast(scope),
        F.col("_tov_id") == F.col("account_id"),
        "leftsemi",
    )

    turnovers_pit = (
        spell_base.join(
            turnovers_scoped,
            on=(spell_base["account_id"] == turnovers_scoped["_tov_id"]),
            how="left",
        )
        .filter(F.col("_snap_date") <= F.col("t0"))
        .withColumn(
            "_rn_tov",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_snap_date").desc()
                )
            ),
        )
        .filter(F.col("_rn_tov") == 1)
        .withColumn(
            "_ltd_fees_charged",
            F.coalesce(F.col("ltd_late_fee_amount"), F.lit(0.0))
            + F.coalesce(F.col("ltd_overlimit_fee_amount"), F.lit(0.0)),
        )
        .select("account_id", "spell_id", "_ltd_fees_charged")
    )

    # ── Combine and derive velocity features ──────────────────────────────────
    result = (
        spell_base.join(contract_pit, on=["account_id", "spell_id"], how="left")
        .join(turnovers_pit, on=["account_id", "spell_id"], how="left")
        .join(fee_feats, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "fee_rate_life",
            # _ltd_fees_charged is always non-null (coalesced); 0 for no-fee accounts
            F.col("_ltd_fees_charged")
            / F.greatest(F.col("tenure_at_t0_m").cast("double"), F.lit(1.0)),
        )
        # H2 denominator: actual clean months in H2 (≤ 3); avoids over-denominating
        .withColumn(
            "_h2_months",
            F.when(
                F.col("w_pre_clean_m") < 3, F.col("w_pre_clean_m").cast("double")
            ).otherwise(F.lit(3.0)),
        )
        .withColumn(
            "fee_accel_h2",
            F.when(
                F.col("fee_rate_life").isNotNull()
                & (F.col("fee_rate_life") > 0.0)
                & F.col("_fee_amt_h2").isNotNull()
                & (F.col("_h2_months") > 0.0),
                (F.col("_fee_amt_h2") / F.col("_h2_months")) / F.col("fee_rate_life"),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    return result.select(
        "account_id",
        "spell_id",
        "tenure_at_t0_m",
        "fee_rate_life",
        "fee_accel_h2",
    )


# ── Private: Pass E ───────────────────────────────────────────────────────────


def _build_pass_e(
    int_bureau_pull_monthly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """AECB leverage slope via OLS of bureau_total_balance vs months before T0.

    Business purpose: detects whether the customer's total bureau-reported liabilities
    were growing or shrinking in the 24 months before T0.  An upward slope (leverage
    accumulation) correlates with inability to cure; a downward slope (deleveraging)
    may indicate active debt management.

    T21 DROP — CONFIRMED. Coverage: 0.11% cc_180_plus, 0.46% cc_60_180 (T06b 2026-08-24).
    Genuine data absence; not fixable by bridge repair. Code retained solely for output
    schema stability. All values are NULL in production. Remove at T21.

    Detection strategy: OLS computed via Spark accumulators (_n, _sx, _sy, _sxy, _sx2)
    to avoid collecting data to the driver.  x-variable = m_from_m0 (positive integer,
    ≥ 1; larger = further from T0).  Same pattern as T05 util_slope.
    Positive slope = balance was growing toward T0 (increasing leverage).
    Negative slope = balance was shrinking toward T0 (deleveraging).

    Features::

        aecb_leverage_slope     : OLS β₁ of bureau_total_balance on m_from_m0;
                                  NULL if fewer than 2 non-null pulls in [M0-24m, M0)
                                  or if the OLS denominator is zero (all pulls same month).

    One pull per (account_id, spell_id, m_from_m0) — deduped to latest in month.
    """
    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select("cif_id").distinct()

    # Scope bureau via CIF IDs (leftsemi before date filter)
    bureau_scoped = int_bureau_pull_monthly.select(
        "cif_id", "pull_date", "bureau_total_balance"
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # Join spell_cif to get (account_id, spell_id, t0) per pull
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.withColumnRenamed("_ctr_id", "account_id"),
        on="account_id",
        how="left",
    )

    bureau_w = (
        bureau_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pull_date") < F.trunc(F.col("t0"), "month"))
            & (F.col("pull_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & F.col("bureau_total_balance").isNotNull()
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("pull_date"), "month"),
                )
            ).cast("int"),
        )
        # Dedup to one pull per (account_id, spell_id, month) — take latest pull
        .withColumn(
            "_rn_bur",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id", "m_from_m0").orderBy(
                    F.col("pull_date").desc()
                )
            ),
        )
        .filter(F.col("_rn_bur") == 1)
    )

    # OLS accumulators (x = m_from_m0)
    agg = bureau_w.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_n"),
        F.sum(F.col("m_from_m0").cast("double")).alias("_sx"),
        F.sum(F.col("bureau_total_balance")).alias("_sy"),
        F.sum(F.col("m_from_m0").cast("double") * F.col("bureau_total_balance")).alias(
            "_sxy"
        ),
        F.sum(
            F.col("m_from_m0").cast("double") * F.col("m_from_m0").cast("double")
        ).alias("_sx2"),
    )

    _denom = F.col("_n").cast("double") * F.col("_sx2") - F.col("_sx") * F.col("_sx")

    slope = agg.withColumn(
        "aecb_leverage_slope",
        F.when(
            (F.col("_n") >= 2) & (_denom != 0.0),
            (F.col("_n").cast("double") * F.col("_sxy") - F.col("_sx") * F.col("_sy"))
            / _denom,
        ).otherwise(F.lit(None).cast("double")),
    ).select("account_id", "spell_id", "aecb_leverage_slope")

    # Left join to emit NULL for spells with no bureau pulls
    return spell_w.select("account_id", "spell_id").join(
        slope, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass F ───────────────────────────────────────────────────────────


def _build_pass_f(feat_product_holding: DataFrame, spell_w: DataFrame) -> DataFrame:
    """Relationship breadth from feat_product_holding.

    Business purpose: captures the customer's product footprint at the bank at T0.
    Customers with a deeper relationship (multiple products: mortgage, personal loan,
    auto, CASA) are less likely to default strategically — they have more to lose and
    may respond better to in-house collection.  Single-product (CC-only) customers
    with no other bank ties are higher flight risk.

    Schema guard: if total_products column or a recognised join key / observation
    date column is absent, emits NULL and logs a warning.

    PIT join: latest obs_date <= t0 per (account_id, spell_id).

    Feature::

        relationship_breadth    : total_products cast to int at T0;
                                  NULL if no snapshot on or before T0, or if the
                                  required column / join key is absent (schema guard).
    """
    ph_cols_lower = {c.lower() for c in feat_product_holding.columns}

    # Schema guard: total_products required
    if "total_products" not in ph_cols_lower:
        LOG.warning(
            "Pass F: feat_product_holding missing 'total_products' column "
            "— relationship_breadth = NULL (<<FILL-IN: verify catalog key>>)"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    # Resolve join key
    ph_key = None
    for candidate in ("account_id", "contract_id"):
        if candidate in ph_cols_lower:
            ph_key = candidate
            break

    if ph_key is None:
        LOG.warning(
            "Pass F: feat_product_holding missing account_id/contract_id key "
            "— relationship_breadth = NULL"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    # Resolve observation date column
    ph_obs = None
    for candidate in ("obs_date", "observation_date", "snapshot_date", "edp_load_date"):
        if candidate in ph_cols_lower:
            ph_obs = candidate
            break

    if ph_obs is None:
        LOG.warning(
            "Pass F: feat_product_holding missing observation date column "
            "— relationship_breadth = NULL"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    scope = spell_w.select("account_id").distinct()

    ph_scoped = feat_product_holding.select(
        F.col(ph_key).alias("_ph_key"),
        F.col(ph_obs).alias("_ph_obs"),
        F.col("total_products").cast("int").alias("_total_products"),
    ).join(
        F.broadcast(scope),
        F.col("_ph_key") == F.col("account_id"),
        "leftsemi",
    )

    spell_dates = spell_w.select("account_id", "spell_id", "t0")

    ph_pit = (
        ph_scoped.join(
            spell_dates,
            on=(ph_scoped["_ph_key"] == spell_dates["account_id"]),
            how="inner",
        )
        .filter(F.col("_ph_obs") <= F.col("t0"))
        .withColumn(
            "_rn_ph",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_ph_obs").desc()
                )
            ),
        )
        .filter(F.col("_rn_ph") == 1)
        .select(
            "account_id",
            "spell_id",
            F.col("_total_products").alias("relationship_breadth"),
        )
    )

    return spell_w.select("account_id", "spell_id").join(
        ph_pit, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass G ───────────────────────────────────────────────────────────

# Column names in fea_monthly_aecb_alerts (from retail.feature_space aecb_alert pipeline)
_ALERT_NEW_ENQUIRY_COL = "aecb_alert_new_inquiry_alert_flag"
_ALERT_CREDIT_OPENED_COL = "aecb_credit_facility_opened_alert_flag"
_ALERT_TOTAL_COL = "aecb_total_alerts_flag"


def _build_pass_g(  # pylint: disable=too-many-locals
    fea_monthly_aecb_alerts: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """AECB alert-based signals from fea_monthly_aecb_alerts (REUSE — retail.feature_space).

    Business purpose: captures external credit-market activity (new enquiries, new
    facilities) in the 3 months before T0.  A spike in new credit enquiries or newly
    opened facilities just before delinquency onset suggests the customer was seeking
    alternative credit — either to service existing debt or in anticipation of financial
    stress.  These are bureau-derived, unbiased by internal bank behaviour, making them
    strong early-warning signals independent of transactional history.

    R2 PASS: month_number is the last day of each calendar month (yyyyMMdd).
    Filter ``F.to_date(month_number,'yyyyMMdd') < F.trunc(t0,'month')`` is strict <
    T0 month, so no post-T0 leakage is possible.
    R7 PASS: source is sa_ops_aecb_alert (prvdr_subj_num, alert_desc, contract_type,
    extract_dt). No nationality, visa, residency, iqama, or expat inputs.
    Coverage: 92.99% (T06c, cc_60_180).

    Window: 3 calendar months immediately before T0 — [M0-3m, M0).
    cif_id type: fea_monthly_aecb_alerts stores cif_id as IntegerType; normalised to
    string for the join to match prm_client.cif_id convention.

    Schema guard: if cif_id, month_number, or aecb_total_alerts_flag are absent,
    emits NULL for all three features and logs a warning.

    Features::

        aecb_new_enquiry_3m     : count of new-enquiry alerts in [M0-3m, M0);
                                  NULL if no alert rows in window or column absent;
                                  note: individual month values are coalesced(flag, 0)
                                  before summing, so only fully absent data produces NULL.
        aecb_credit_opened_3m   : count of credit-facility-opened alerts in [M0-3m, M0);
                                  NULL if no alert rows in window or column absent.
        aecb_total_alerts_3m    : total alert count in [M0-3m, M0);
                                  NULL if no alert rows in window (left-join result).
    """
    _ALERT_REQUIRED = ["cif_id", "month_number", _ALERT_TOTAL_COL]
    alert_cols_lower = {c.lower() for c in fea_monthly_aecb_alerts.columns}
    missing = [c for c in _ALERT_REQUIRED if c not in alert_cols_lower]

    if missing:
        LOG.warning(
            "Pass G [AECB alerts]: missing columns %s in fea_monthly_aecb_alerts "
            "— emitting NULL for aecb_new_enquiry_3m, aecb_credit_opened_3m, "
            "aecb_total_alerts_3m",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("aecb_new_enquiry_3m", F.lit(None).cast("int"))
            .withColumn("aecb_credit_opened_3m", F.lit(None).cast("int"))
            .withColumn("aecb_total_alerts_3m", F.lit(None).cast("int"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    # cif_id in fea_monthly_aecb_alerts is IntegerType — cast to string to match prm_client
    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    # Optional alert columns — coalesce to 0 if column exists but value is NULL;
    # emit NULL feature if the column is entirely absent (pivot may not produce it)
    has_new_enq = _ALERT_NEW_ENQUIRY_COL in alert_cols_lower
    has_cred_open = _ALERT_CREDIT_OPENED_COL in alert_cols_lower

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("alert_month"),
        (
            F.coalesce(F.col(_ALERT_NEW_ENQUIRY_COL), F.lit(0)).alias("_new_enq")
            if has_new_enq
            else F.lit(None).cast("int").alias("_new_enq")
        ),
        (
            F.coalesce(F.col(_ALERT_CREDIT_OPENED_COL), F.lit(0)).alias("_cred_open")
            if has_cred_open
            else F.lit(None).cast("int").alias("_cred_open")
        ),
        F.coalesce(F.col(_ALERT_TOTAL_COL), F.lit(0)).alias("_total"),
    ]

    alerts_scoped = fea_monthly_aecb_alerts.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # spell_cif: (account_id, spell_id, t0) per CIF
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # R2: 3-month window strictly before T0
    alerts_w = alerts_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        (F.col("alert_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("alert_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    agg = alerts_w.groupBy("account_id", "spell_id").agg(
        F.sum("_new_enq").alias("aecb_new_enquiry_3m"),
        F.sum("_cred_open").alias("aecb_credit_opened_3m"),
        F.sum("_total").alias("aecb_total_alerts_3m"),
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass H ───────────────────────────────────────────────────────────


def _build_pass_h(
    feat_fx_leakage: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Cross-border CASA outflow signals from fea_monthly_agg_fx_leakage.

    Business purpose: captures fund outflows to foreign accounts in the 3 months
    before T0.  Cross-border transfers are a direct capital-flight signal — a customer
    remitting large amounts abroad while accumulating card debt is a strong flight risk.
    LGBM importance 156.5, IV 0.035 (existing model, 12-month window).  This pass uses
    the H2 (3-month) window for tighter T0 proximity.

    Source: feat_fx_leakage = fea_monthly_agg_fx_leakage (retail.feature_space).
    The table carries pre-rolled features; _FX_CB_AMT_COL is a 3-month rolling sum
    (in_last_0_2_months), which equals the H2 = [M0-3m, M0) window when read at the
    last H2 month (most recent month_number strictly before M0).

    Approach: point-in-time join — find the row with the latest month_number in H2
    for each (spell, cif) and read the pre-rolled 3-month sum directly.  No re-aggregation
    needed (unlike raw-monthly sources).

    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Features::

        cross_border_outflow_amt_h2  (double) — pre-rolled 3m AED cross-border outflow;
                                                NULL if no H2 row or column absent.
        cross_border_outflow_cnt_h2  (int)    — always NULL; no count equivalent in
                                                fea_monthly_agg_fx_leakage (T21 candidate).
    """
    _REQUIRED = ["cif_id", "month_number"]
    fx_cols_lower = {c.lower() for c in feat_fx_leakage.columns}
    missing_base = [c for c in _REQUIRED if c not in fx_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass H [cross-border FX leakage]: missing base columns %s in feat_fx_leakage "
            "— emitting NULL for cross_border_outflow_amt_h2, cross_border_outflow_cnt_h2",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("cross_border_outflow_amt_h2", F.lit(None).cast("double"))
            .withColumn("cross_border_outflow_cnt_h2", F.lit(None).cast("int"))
        )

    has_amt = _FX_CB_AMT_COL in fx_cols_lower
    if not has_amt:
        LOG.warning(
            "Pass H [cross-border FX leakage]: column '%s' absent from feat_fx_leakage "
            "— cross_border_outflow_amt_h2 = NULL",
            _FX_CB_AMT_COL,
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    # cif_id in retail.feature_space tables is IntegerType — cast to string to match prm_client
    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    fx_scoped = feat_fx_leakage.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("fx_month"),
        (
            F.col(_FX_CB_AMT_COL).cast("double").alias("_cb_amt")
            if has_amt
            else F.lit(None).cast("double").alias("_cb_amt")
        ),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # Point-in-time: most recent H2 row per (spell, cif).
    # H2 = [M0-3m, M0); the pre-rolled _FX_CB_AMT_COL at that row already covers 3m.
    h2_w = spell_cif.join(fx_scoped, on="cif_id", how="inner").filter(
        (F.col("fx_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("fx_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    pit_w = Window.partitionBy("account_id", "spell_id").orderBy(
        F.col("fx_month").desc()
    )
    agg = (
        h2_w.withColumn("_rn", F.row_number().over(pit_w))
        .filter(F.col("_rn") == 1)
        .groupBy("account_id", "spell_id")
        .agg(F.first("_cb_amt").alias("cross_border_outflow_amt_h2"))
        .withColumn("cross_border_outflow_cnt_h2", F.lit(None).cast("int"))
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass H2 ──────────────────────────────────────────────────────────


def _build_pass_h2(  # pylint: disable=too-many-locals
    feat_cc_txns_rfs: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Retail.feature_space CC travel+tours MCC signals from fea_cc_inflow_outflow_txns_monthly.

    Business purpose: retail.feature_space uses a 24-category MCC taxonomy including
    a 'travel_and_tours' category that partially overlaps but is NOT identical to the
    ISO 18245 airline/cruise/agency codes used in Pass A.  Both signals together cover
    more MCCs than either alone — Pass A catches explicit booking MCCs; this pass catches
    the retail.feature_space categorisation which may include different merchant types.
    Recreation and Car Fuel from this same table are already STRONG_SIGNAL features in
    the existing model (LGBM importance 721/452), confirming the table's signal quality.

    Source: feat_cc_txns_rfs = fea_cc_inflow_outflow_txns_monthly (retail.feature_space).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: H2 = [M0-3m, M0) — 3 months immediately before T0.
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if _CC_TRAVEL_AMT_COL or _CC_TRAVEL_CNT_COL are absent, emits NULL
    and logs a warning.  Run t06d_schema_probes.py in PROD to confirm column names.

    Features::

        retail_travel_mcc_amt_h2  (double) — AED sum of travel+tours CC spend in H2;
                                             NULL if no rows in H2 or column absent.
        retail_travel_mcc_cnt_h2  (int)    — count of travel+tours CC transaction months
                                             in H2; NULL if no rows or column absent.
    """
    _REQUIRED = ["cif_id", "month_number"]
    cc_cols_lower = {c.lower() for c in feat_cc_txns_rfs.columns}
    missing_base = [c for c in _REQUIRED if c not in cc_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass H2 [CC travel MCC]: missing base columns %s in feat_cc_txns_rfs "
            "— emitting NULL for retail_travel_mcc_amt_h2, retail_travel_mcc_cnt_h2",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("retail_travel_mcc_amt_h2", F.lit(None).cast("double"))
            .withColumn("retail_travel_mcc_cnt_h2", F.lit(None).cast("int"))
        )

    has_amt = _CC_TRAVEL_AMT_COL in cc_cols_lower
    has_cnt = _CC_TRAVEL_CNT_COL in cc_cols_lower

    if not has_amt:
        LOG.warning(
            "Pass H2 [CC travel MCC]: column '%s' absent — retail_travel_mcc_amt_h2 = NULL "
            "(run t06d_schema_probes.py to confirm name)",
            _CC_TRAVEL_AMT_COL,
        )
    if not has_cnt:
        LOG.warning(
            "Pass H2 [CC travel MCC]: column '%s' absent — retail_travel_mcc_cnt_h2 = NULL "
            "(run t06d_schema_probes.py to confirm name)",
            _CC_TRAVEL_CNT_COL,
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("cc_month"),
        (
            F.col(_CC_TRAVEL_AMT_COL).cast("double").alias("_travel_amt")
            if has_amt
            else F.lit(None).cast("double").alias("_travel_amt")
        ),
        (
            F.col(_CC_TRAVEL_CNT_COL).cast("int").alias("_travel_cnt")
            if has_cnt
            else F.lit(None).cast("int").alias("_travel_cnt")
        ),
    ]

    cc_scoped = feat_cc_txns_rfs.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    cc_w = cc_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        (F.col("cc_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("cc_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    agg = cc_w.groupBy("account_id", "spell_id").agg(
        F.sum("_travel_amt").alias("retail_travel_mcc_amt_h2"),
        F.sum("_travel_cnt").alias("retail_travel_mcc_cnt_h2"),
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass I ───────────────────────────────────────────────────────────


def _build_pass_i(
    feat_payroll_indicator: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Payroll presence and stop signals from pri_monthly_payroll_indicator.

    Business purpose: a salary stopping just before T0 is a strong cure-negative signal.
    `payroll_present_h2` confirms whether any payroll credit landed in the 3 months before
    T0.  `payroll_stopped_flag` is 1 if payroll was present in the baseline window (H1:
    m_from_m0 >= 4) but absent in H2 — the single strongest cure predictor (stopping salary
    ≈ job loss ≈ no cure).

    This complements Pass B (which detects EOSB/stop from raw 2.4B-row CASA table) with a
    pre-computed primary-layer signal:
      - Pass B: raw CASA, 2.4B rows, detects stop + EOSB lump sum.
      - Pass I: pre-computed, cheaper join, confirms consistency of payroll receipt.
    LGBM importance in existing model: has_payroll_credit_1m=53.6, payroll_consistency_3m=28.8.

    Source: feat_payroll_indicator = pri_monthly_payroll_indicator (retail.feature_space).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: H2 = [M0-3m, M0) for payroll_present_h2; H1 = [w_pre_start, M0-3m) for baseline.
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if _PAYROLL_HAS_COL is absent, emits NULL for both features.
    Run t06d_schema_probes.py in PROD to confirm exact column name.

    Features::

        payroll_present_h2   (int 0/1) — 1 if any H2 month shows a payroll credit;
                                         0 if H2 rows exist but no payroll found;
                                         NULL if no H2 rows in window or column absent.
        payroll_stopped_flag (int 0/1) — 1 if payroll present in H1 (m_from_m0 >= 4)
                                         but absent in H2 (m_from_m0 in [1, 3]);
                                         0 if payroll present in both or absent in both;
                                         NULL if no H1 rows (cannot assess baseline).
    """
    _REQUIRED = ["cif_id", "month_number"]
    pay_cols_lower = {c.lower() for c in feat_payroll_indicator.columns}
    missing_base = [c for c in _REQUIRED if c not in pay_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass I [payroll]: missing base columns %s in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    if _PAYROLL_HAS_COL not in pay_cols_lower:
        LOG.warning(
            "Pass I [payroll]: column '%s' absent in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            _PAYROLL_HAS_COL,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    pay_scoped = feat_payroll_indicator.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("pay_month"),
        F.col(_PAYROLL_HAS_COL).cast("int").alias("_has_payroll"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    spell_cif = spell_w.select("account_id", "spell_id", "t0", "w_pre_start").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # Full pre-delinquency window [w_pre_start, M0)
    pay_w = (
        pay_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pay_month") >= F.trunc(F.col("w_pre_start"), "month"))
            & (F.col("pay_month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.col("pay_month"),
                )
            ).cast("int"),
        )
    )

    agg = pay_w.groupBy("account_id", "spell_id").agg(
        # H2: m_from_m0 in [1, 3] — recent 3 months
        F.max(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("_has_payroll"),
            )
        ).alias("_h2_max"),
        # H1: m_from_m0 >= 4 — baseline
        F.max(F.when(F.col("m_from_m0") >= 4, F.col("_has_payroll"))).alias("_h1_max"),
        F.count(F.when(F.col("m_from_m0") >= 4, F.lit(1))).alias("_h1_row_count"),
    )

    result = (
        agg.withColumn(
            "payroll_present_h2",
            F.when(
                F.col("_h2_max").isNotNull(), F.col("_h2_max").cast("int")
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumn(
            "payroll_stopped_flag",
            F.when(
                # No H1 data — cannot assess whether payroll stopped
                F.col("_h1_row_count").isNull() | (F.col("_h1_row_count") == 0),
                F.lit(None).cast("int"),
            )
            .when(
                # Payroll present in H1 but absent/zero in H2 → stopped
                (F.col("_h1_max") == 1) & (F.coalesce(F.col("_h2_max"), F.lit(0)) == 0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "spell_id", "payroll_present_h2", "payroll_stopped_flag")
    )

    return spell_w.select("account_id", "spell_id").join(
        result, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass J ───────────────────────────────────────────────────────────


def _build_pass_j(  # pylint: disable=too-many-locals
    prm_digital_login_monthly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """Foreign login detection from prm_digital_login_monthly (OMB login logs).

    Business purpose: a customer logging in from outside UAE before the spine observation
    date is a departure-intent proxy — digital access from a foreign IP indicates
    continued presence abroad or imminent relocation.  Unlike transactions (blocked at
    61+ DPD), login can occur after card block, so the window extends to spine_obs_date
    (fallback: M0 if spine_obs_date is NULL).

    Source: prm_digital_login_monthly (digital_login pipeline output).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: all months before spine_obs_date — most recent login picked (no lower bound).
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if cif_id, month_number, or last_login_foreign_flag are absent,
    emits NULL for both features and logs a warning.

    Features::

        foreign_login_flag    (int 0/1) — is_foreign_login of the most recent login
                                          before spine_obs_date;
                                          1 = latest login was from outside UAE;
                                          0 = latest login was from within UAE;
                                          NULL if no logins found before obs_date.
        last_login_country_h2 (str)     — countrylocation of most recent pre-obs login;
                                          NULL if no logins or country data absent.
                                          Not encoded — consumers (T07 class rules,
                                          segment inspection) decide encoding strategy.
    """
    _REQUIRED = ["cif_id", "month_number", "last_login_foreign_flag"]
    login_cols_lower = {c.lower() for c in prm_digital_login_monthly.columns}
    missing = [c for c in _REQUIRED if c not in login_cols_lower]

    if missing:
        LOG.warning(
            "Pass J [foreign login]: missing columns %s in prm_digital_login_monthly "
            "— emitting NULL for foreign_login_flag, last_login_country_h2",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("foreign_login_flag", F.lit(None).cast("int"))
            .withColumn("last_login_country_h2", F.lit(None).cast("string"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    has_country = "last_login_country" in login_cols_lower

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("login_month"),
        F.col("last_login_foreign_flag").cast("int").alias("_foreign_flag"),
        (
            F.col("last_login_country").cast("string").alias("_login_country")
            if has_country
            else F.lit(None).cast("string").alias("_login_country")
        ),
    ]

    login_scoped = prm_digital_login_monthly.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # spell_cif: (account_id, spell_id, t0, spine_obs_date) per CIF
    spell_cif = spell_w.select("account_id", "spell_id", "t0", "spine_obs_date").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # All pre-obs months — no lower bound; pick most recent login before spine_obs_date.
    # Login can occur post-card-block (digital channel stays active after Block-X).
    # NULL-safe fallback to M0 if spine_obs_date is absent.
    _obs_ceil_j = F.coalesce(
        F.trunc(F.col("spine_obs_date"), "month"),
        F.trunc(F.col("t0"), "month"),
    )
    login_w = login_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        F.col("login_month") < _obs_ceil_j
    )

    # Most recent H2 login month per (account_id, spell_id)
    w_recent = Window.partitionBy("account_id", "spell_id").orderBy(
        F.col("login_month").desc()
    )
    most_recent = (
        login_w.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(
            "account_id",
            "spell_id",
            F.col("_foreign_flag").alias("foreign_login_flag"),
            F.col("_login_country").alias("last_login_country_h2"),
        )
    )

    return spell_w.select("account_id", "spell_id").join(
        most_recent, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass K ───────────────────────────────────────────────────────────


def _build_pass_k(  # pylint: disable=too-many-locals
    crx_cc_transactions: DataFrame,
    prm_contract: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Bust-out / fraudster utilisation signals from crx_cc_transactions + prm_contract.

    Business purpose: identifies accounts fraudulently opened and immediately exhausted
    (bust-out pattern).  Cure probability ≈ 0% for these accounts.  The 2022–2023
    origination spike included a material population: limit consumed in 1–2 days or
    concentrated in a single week, followed by zero repayment.  Identifying them prevents
    waste of collection effort and removes a confounding population from the cure model.

    Detection strategy:
    - ever_paid_flag: was any payment made in W_pre?  0 = never paid.
    - limit_util_first_7d_flag: did the account consume 80%+ of its lifetime peak
      spend within the first 7 days of opening?  (Total W_pre abs spend used as a
      proxy for limit — prm_limit may post-date the bust-out period.)
    - max_7d_spend_ratio: peak rolling 7-day spend / total W_pre spend.  Captures
      concentration of spend into a short burst window regardless of account age.

    Sign convention: txn_amount_aed > 0 = purchase (increases balance);
    txn_amount_aed < 0 = payment (reduces balance). Confirmed FI-2: Way4 CC convention.

    PIT join: prm_contract observation_date PIT join for open_date — same pattern as Pass D.
    Sources reused: crx_cc_transactions (Pass A) + prm_contract (Pass D); no new inputs.

    Features::

        ever_paid_flag           (int 0/1) — 1 if any payment in W_pre (txn_amount_aed < 0
                                             or txn_category == payment); 0 if W_pre txns
                                             exist but none are payments; NULL if no W_pre txns.
        limit_util_first_7d_flag (int 0/1) — 1 if cumulative spend in first 7 days after
                                             open_date > 80% of total W_pre spend;
                                             0 if open_date available but condition not met;
                                             NULL if open_date is NULL or no W_pre txns.
        max_7d_spend_ratio       (double)  — max rolling 7-day purchase sum / total W_pre
                                             purchase sum; NULL if no purchase transactions.
    """
    scope = spell_w.select("account_id").distinct()
    spell_base = spell_w.select("account_id", "spell_id", "t0", "w_pre_start")

    # Scope CC transactions to in-scope accounts (leftsemi before window filter)
    txn = crx_cc_transactions.select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("txn_amount_aed"),
        F.col("txn_category"),
    ).join(
        F.broadcast(scope),
        crx_cc_transactions["contract_id"] == scope["account_id"],
        "leftsemi",
    )

    # Join to spell_w and filter to W_pre: [w_pre_start, M0)
    txn_w = (
        txn.join(spell_w, on=(txn["contract_id"] == spell_w["account_id"]), how="inner")
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("txn_category"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
    )

    # Payment detection: negative amount (Way4 CC sign convention, FI-2) OR payment category
    is_payment = (F.col("txn_amount_aed") < 0) | (
        F.col("txn_category") == F.lit(_PAYMENT_CATEGORY)
    )

    # ever_paid_flag aggregation
    ever_paid_agg = txn_w.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_row_count"),
        F.max(F.when(is_payment, F.lit(1)).otherwise(F.lit(0))).alias("_any_payment"),
    )

    # Purchase transactions (positive amounts = spend on card)
    purchase_txns = txn_w.filter(
        F.col("txn_amount_aed").isNotNull() & (F.col("txn_amount_aed") > 0)
    ).withColumn(
        "_epoch_day",
        F.datediff(F.col("txn_date"), F.to_date(F.lit("1970-01-01"))).cast("long"),
    )

    # Total W_pre purchase spend per spell
    total_spend = purchase_txns.groupBy("account_id", "spell_id").agg(
        F.sum("txn_amount_aed").alias("_total_spend"),
    )

    # Max rolling 7-day spend: rangeBetween(-6, 0) on epoch-day ordered window
    w_7d = (
        Window.partitionBy("account_id", "spell_id")
        .orderBy("_epoch_day")
        .rangeBetween(-6, 0)
    )
    max_7d_spend = (
        purchase_txns.withColumn("_rolling_7d", F.sum("txn_amount_aed").over(w_7d))
        .groupBy("account_id", "spell_id")
        .agg(F.max("_rolling_7d").alias("_max_7d_spend"))
    )

    # PIT join prm_contract for account open_date (same pattern as Pass D)
    contract_scoped = prm_contract.select(
        F.col("contract_id").alias("_ctr_id"),
        F.col(_CONTRACT_OPEN_DATE_COL).alias("account_open_date"),
        F.col("observation_date").alias("_eff_start"),
    ).join(F.broadcast(scope), F.col("_ctr_id") == F.col("account_id"), "leftsemi")

    contract_open = (
        spell_base.join(
            contract_scoped,
            on=(spell_base["account_id"] == contract_scoped["_ctr_id"]),
            how="left",
        )
        .filter(F.col("_eff_start") <= F.col("t0"))
        .withColumn(
            "_rn_ctr",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_eff_start").desc()
                )
            ),
        )
        .filter(F.col("_rn_ctr") == 1)
        .select("account_id", "spell_id", "account_open_date")
    )

    # First-7-day spend: purchases on or within 6 days after open_date
    first7d_spend = (
        purchase_txns.join(contract_open, on=["account_id", "spell_id"], how="left")
        .filter(
            F.col("account_open_date").isNotNull()
            & (F.col("txn_date") >= F.col("account_open_date"))
            & (F.col("txn_date") <= F.date_add(F.col("account_open_date"), 6))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.sum("txn_amount_aed").alias("_first_7d_spend"))
    )

    # Combine all aggregations and compute final features
    result = (
        spell_w.select("account_id", "spell_id")
        .join(ever_paid_agg, on=["account_id", "spell_id"], how="left")
        .join(total_spend, on=["account_id", "spell_id"], how="left")
        .join(max_7d_spend, on=["account_id", "spell_id"], how="left")
        .join(first7d_spend, on=["account_id", "spell_id"], how="left")
        .join(contract_open, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "ever_paid_flag",
            F.when(F.col("_row_count").isNull(), F.lit(None).cast("int"))
            .when(F.col("_any_payment") == 1, F.lit(1))
            .otherwise(F.lit(0)),
        )
        .withColumn(
            "limit_util_first_7d_flag",
            F.when(
                F.col("account_open_date").isNull() | F.col("_total_spend").isNull(),
                F.lit(None).cast("int"),
            )
            .when(
                F.col("_first_7d_spend").isNull(),
                F.lit(0),  # no spend in first 7d → not bust-out
            )
            .when(
                (F.col("_total_spend") > 0)
                & (F.col("_first_7d_spend") / F.col("_total_spend") > 0.80),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .withColumn(
            "max_7d_spend_ratio",
            F.when(
                F.col("_total_spend").isNotNull() & (F.col("_total_spend") > 0),
                F.col("_max_7d_spend") / F.col("_total_spend"),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    return result.select(
        "account_id",
        "spell_id",
        "ever_paid_flag",
        "limit_util_first_7d_flag",
        "max_7d_spend_ratio",
    )


# ── Private: logging ──────────────────────────────────────────────────────────


def _log_departure_stats(result: DataFrame) -> None:
    """Log null-rate summary for the built departure signature table."""
    try:
        total = result.count()
        if total == 0:
            LOG.warning("CC departure signature: 0 rows produced — check spell filter")
            return
        cov_travel = result.filter(F.col("travel_mcc_flag_h2").isNotNull()).count()
        cov_casa = result.filter(F.col("casa_inflow_stop_gap_d").isNotNull()).count()
        cov_bureau = result.filter(F.col("aecb_leverage_slope").isNotNull()).count()
        cov_breadth = result.filter(F.col("relationship_breadth").isNotNull()).count()
        cov_alerts = result.filter(F.col("aecb_total_alerts_3m").isNotNull()).count()
        cov_cb_outflow = result.filter(
            F.col("cross_border_outflow_amt_h2").isNotNull()
        ).count()
        cov_retail_travel = result.filter(
            F.col("retail_travel_mcc_amt_h2").isNotNull()
        ).count()
        cov_payroll = result.filter(F.col("payroll_present_h2").isNotNull()).count()
        cov_ever_paid = result.filter(F.col("ever_paid_flag").isNotNull()).count()
        cov_foreign_login = result.filter(
            F.col("foreign_login_flag").isNotNull()
        ).count()
        LOG.info(
            "CC departure signature built: %d spells | "
            "travel_mcc_flag_h2: %.1f%% | "
            "casa_inflow_stop_gap_d: %.1f%% | "
            "aecb_leverage_slope: %.1f%% (T21 DROP — all NULL expected) | "
            "relationship_breadth: %.1f%% | "
            "aecb_total_alerts_3m: %.1f%% | "
            "cross_border_outflow_amt_h2: %.1f%% | "
            "retail_travel_mcc_amt_h2: %.1f%% | "
            "payroll_present_h2: %.1f%% | "
            "ever_paid_flag: %.1f%% | "
            "foreign_login_flag: %.1f%%",
            total,
            100.0 * cov_travel / total,
            100.0 * cov_casa / total,
            100.0 * cov_bureau / total,
            100.0 * cov_breadth / total,
            100.0 * cov_alerts / total,
            100.0 * cov_cb_outflow / total,
            100.0 * cov_retail_travel / total,
            100.0 * cov_payroll / total,
            100.0 * cov_ever_paid / total,
            100.0 * cov_foreign_login / total,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute departure signature stats: %s (lazy eval context)",
            str(exc),
        )
