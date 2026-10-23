# pylint: disable=W0511
"""
Configuration for data engineering pipelines.

Way4 CC: tdv_way4_standard_group_way4_standard
AECB Bureau: dpl_uae_operations

Environment prefix (ai_ for sandpit, empty for prod) is resolved via
conf globals — see conf/dev/globals_dev.yml and conf/prod/globals_prod.yml.
"""

import calendar
from datetime import date

# Base schema name (without environment prefix)
WAY4_SCHEMA_BASE = "tdv_way4_standard_group_way4_standard"

# DDI archive schema — 3-5 year history (replaces TDV T-1 snapshots for 6 of 9 tables)
WAY4_DDI_SCHEMA_BASE = "ddi_tdv_way4_standard_group_way4_standard"

# Mapping from TDV table names to DDI equivalents (DDI drops stg_ prefix).
# All 9 base Way4 tables now in DDI (TBL024-026 ingested).
DDI_TABLE_MAP = {
    "stg_contract": "contract",
    "stg_client": "client",
    "stg_contract_attribute": "contract_attribute",
    "stg_balance": "balance",
    "stg_account_group": "account_group",
    "stg_product_config": "product_config",
    # TBL024-026: previously TDV-only, now ingested into DDI
    "stg_limit": "limit",
    "stg_card": "card",
    "transaction": "transaction",
    # New DDI tables (10 tables from schema-to-model)
    "stg_billing": "billing",
    "stg_last_operation": "last_operation",
    "stg_summary_balance": "summary_balance",
    "stg_instalment": "instalment",
    "stg_tariff": "tariff",
    "stg_card_event": "card_event",
    "stg_card_attribute": "card_attribute",
    "stg_calc_fields_dump": "calc_fields_dump",
    "stg_contract_ext": "contract_ext",
}

# Org code → entity mapping (from Rahul's logic files)
ORG_ENTITY_MAP = {
    "100": "AE",
    "101": "AE",
    "010": "AE",
    "011": "AE",
    "012": "AE",
    "033": "AE",
    "017": "EI",
    "016": "SA",
    "034": "EG",
}

# CIF length by org (from Rahul's logic: 8 for EI, 9 for others)
CIF_LENGTH = {"017": 8}
CIF_LENGTH_DEFAULT = 9

# SCD2 sentinel value for current active records
SCD2_CURRENT_DATE = "2100-01-01"

# Post-Block X sentinel date — system-generated fee accruals after permanent
# card cancellation use trans_date=2100-01-01 with card_idt=0, settl_amount=0,
# service_class=I. V2 sample: 99.8% of transactions are this pattern (DLQ 5-9).
POST_BLOCK_X_SENTINEL_DATE = "2100-01-01"

# Transaction code groupings (from DPL logics Query 3 — production-authoritative).
# Source: EC_CREDIT_CARD_TRANSACTIONS aggregation logic used in production DPL pipeline.
# fee code 500 = "BILLED FINANCE CHARGES" — dominant post-Block X fee accrual type
# (99.8% of V2 transactions). All post-Block X txns are service_class=I with
# sentinel trans_date=2100-01-01.
TXN_CATEGORIES = {
    # Retail purchases (CC_ACCT_RETL_AMT_MTH in DPL logics Query 3).
    # Includes domestic, international, and return codes (041 = retail return
    # summed with purchases in DPL). Way4 code 092 retained (not in DPL; Way4-only).
    "purchase": [
        "036",
        "037",
        "038",
        "039",
        "040",
        "041",
        "046",
        "047",
        "092",
        "150",
        "151",
        "340",
        "341",
    ],
    # Cash advances (CC_ACCT_CASH_AMT_MTH in DPL logics Query 3).
    "cash": ["030", "031", "032", "130", "131", "132"],
    # Payments received (CC_ACCT_PYMT in DPL logics Query 3).
    "payment": [
        "018",
        "020",
        "021",
        "025",
        "028",
        "073",
        "074",
        "075",
        "076",
        "077",
        "078",
        "079",
        "080",
        "081",
        "083",
        "085",
        "086",
        "205",
        "392",
    ],
    # Annual / membership fees (CC_ACCT_ANNL_FEES in DPL logics Query 3).
    "annual_fee": ["204", "252", "253", "505", "675"],
    # Cash advance fees (CC_ACCT_CASH_ADV_FEES in DPL logics Query 3).
    "cash_advance_fee": ["014", "015", "050", "051", "060", "061"],
    # Late payment fees (CC_ACCT_LATE_FEES_MTH in DPL logics Query 3).
    "late_fee": ["254", "255", "504", "519"],
    # Overlimit fees (CC_ACCT_OVLM_FEES_MTH in DPL logics Query 3).
    "overlimit_fee": ["256", "257", "503"],
    # Finance charges / billed interest (not explicitly categorised in DPL Query 3;
    # 500 appears in DPL CC_ACCT_REV revenue total).
    "fee": ["500", "485"],
    # Instalment plan splits (IPP/EPP).
    "ipp": ["721", "722", "723"],
    # Write-off codes (CC_ACCT_PRINC_WOFF=699, CC_ACCT_INT_FEE_WOFF=700,
    # CC_ACCT_WOFF_AMT=701 in DPL logics Query 3).
    "writeoff": ["699", "700", "701"],
    # Rewards / loyalty redemptions.
    "rewards": ["520"],
}

# Contract status codes
CONTRACT_STATUS = {
    924: "Normal",
    974: "Decline & Pickup General",  # Block X
    730: "Active",
    1101: "Closed",
    938: "Decline",
    2440: "Decline - ENBD",
}

# ---------------------------------------------------------------------------
# Model 1 spine / target constants
# ---------------------------------------------------------------------------

# DLQ buckets comprising M1 population (61-180 DPD)
M1_DLQ_BUCKETS = [4, 5, 6, 7]

# DLQ threshold for cure — account exits M1 range (drops below DLQ 4)
CURE_DLQ_THRESHOLD = 4

# Primary target for Model 1 (confirmed May 1, 2026 by Architha)
# 1 = stable/improved (success), 0 = rolled forward (failure)
DEFAULT_PRIMARY_TARGET = "target"

# Feature lookback windows (months, suffix) — used across all domains (CC, loans, CASA, FTR)
LOOKBACK_WINDOWS = [
    (1, "_1m"),
    (3, "_3m"),
    (6, "_6m"),
    (12, "_12m"),
]

# Balance currency filter (AED = currency code 784, dominant at 86% in profile)
BASE_CURRENCY_CODE = "784"

# Contract attribute type_code patterns (from Rahul's cif_block_code.txt Query 2).
# type_code is the key field — NOT attr_id.
# Block codes are org-specific (e.g., BLOCK_CODE_ACC2_100), so use SQL LIKE patterns.
CONTRACT_ATTR_TYPES = {
    "dlq_level": "DLQ_LEVEL",
    "activity_status": "ACTIVITY_STATUS",
    "collateral_code": "COLLATERAL_CODE",
    "manual_wo": "MANUAL_WO",
    "block_code_1": "BLOCK_CODE_ACC1_%",  # LIKE pattern (org-specific)
    "block_code_2": "BLOCK_CODE_ACC2_%",  # LIKE pattern (org-specific)
    # Hardship / concession flags (from DPL logics Query 2)
    "interest_waiver": "FINANCE_CHG_WAIVER",
    "late_fee_waiver": "LATE_FEE_WAIVER",
    "overlimit_waiver": "OVERLIMIT_FEE_WAIVER",
    "full_payment_flag": "PETRA_FULL_PAYMENT",
    "rewrite_indicator": "REWRITE_INDICATOR",
    "amf_waiver": "AMF_WAIVER",
    # Direct debit enrollment (63.7% of contracts have this attribute)
    "direct_debit_raw": "DIRECT_DEBIT",
}

# Contract attribute types where attr_date_from is the value of interest.
# Used to capture the date a specific event/code was applied to the account.
CONTRACT_ATTR_DATE_TYPES = {
    "block_code_2_date": "BLOCK_CODE_ACC2_%",  # LIKE pattern (org-specific)
}

# Write-off code prefixes (from Rahul's cif_collat_writeoff.txt)
# stg_contract_attribute.code starting with these = write-off/skip
WRITEOFF_CODE_PREFIXES = ["WO", "SK"]

# Write-off account prefix (from Rahul's cif_collat_writeoff.txt)
# personal_account starting with '0009' = written-off account convention
WRITEOFF_ACCOUNT_PREFIX = "0009"

# Balance type codes for sub-components extracted from stg_account_group.
# All three are stored POSITIVE in Way4 (no sign inversion needed).
BALANCE_TYPE_INTEREST_FREE = "INTEREST_FREE"
BALANCE_TYPE_ACCRUED_INT = "ACCRUED_INT"
BALANCE_TYPE_CASH = "CASH"

# Overdue bucket balance types in stg_account_group (from Rahul's cif_block_code.txt)
OVERDUE_BUCKETS = [f"OVD_{i:02d}" for i in range(1, 9)]

# ---------------------------------------------------------------------------
# DLQ_HIST translation: Way4 encoding → numeric DLQ values (0-9).
# Source: Moustafa's DCORE logic (proc_stg_dcore_intrmediate lines 92-97).
# Encoding: '8'=DLQ9, '7'=DLQ8, ..., '1'=DLQ2, '+'=DLQ1, 'E'=DLQ0, '_'=missing.
# Used by BOTH Way4 and DPL pipelines — cc_acct_dlq_hist uses the same encoding.
# ---------------------------------------------------------------------------
DLQ_HIST_FROM = "87654321+E_"
DLQ_HIST_TO = "9876543210 "

# DLQ_LEVEL attribute values (stg_contract_attribute) → DPD bucket labels.
# Production-verified (INV-8, 20.8M rows): values are strings '0'-'9',
# NOT 'CD00'-'CD09' and NOT integers. Python type is str.
# Formula: dlq_level = max(overdue_bucket_with_positive_amount) + 1
# 0 = current (no due), 1 = due but NOT overdue (no OVD buckets),
# 2-9 = overdue buckets 1-8.  DPD labels supported by AMBS naming
# (Moustafa's DCORE SQL: OVD_01=AMBS_PMT_PAST_DUE, OVD_02=AMBS_PMT_30DAYS,
# etc.).  VAL-2 cross-tab couldn't run (0 joined rows — date freshness
# mismatch).  Labels validated via DPL sample cross-validation (H3 100%).
# 9 is the highest overdue bucket, NOT necessarily write-off (is_writeoff
# is a separate flag).
# Frequency from production data: 0 dominates (6.7M), 9 is the
# second-largest bucket (1.2M) — consistent with 60+ DPD portfolio skew.
DLQ_LEVEL_MAP = {
    "0": "current",
    "1": "due_not_overdue",  # was "1-30_dpd" — VERIFIED WRONG from data
    "2": "1-30_dpd",  # Supported by AMBS naming (AMBS_PMT_30DAYS)
    "3": "31-60_dpd",  # Supported by AMBS naming (AMBS_PMT_60DAYS)
    "4": "61-90_dpd",  # Supported by AMBS naming (AMBS_PMT_90DAYS)
    "5": "91-120_dpd",  # Supported by AMBS naming (AMBS_PMT_120DAYS)
    "6": "121-150_dpd",  # Supported by AMBS naming (AMBS_PMT_150DAYS)
    "7": "151-180_dpd",  # Supported by AMBS naming (AMBS_PMT_180DAYS)
    "8": "181-210_dpd",  # Supported by AMBS naming (AMBS_PMT_210DAYS)
    "9": "211+_dpd",  # was "writeoff" — highest OVD bucket
}

# Billing amount type_codes in stg_account_group.
# Source: cluster diagnostic (billing_type_codes.xlsx, April 2026).
# Production-validated: April 2026 (INV-3, INV-7 against 4.7M rows).
#
# Previous config used ENBD_DUE + ENBD_TOTAL_DUE, which share the same 3
# account_group_ids — causing minimum_due == total_due after pivot.
#
# DATA QUALITY per type_code (production-verified):
#
# STMT_BALANCE (161 ag_ids): Known-contaminated — 0% exclusive ag_ids (INV-3).
#   Every ag_id also maps to other type_codes (AMOUNT_AVAILABLE, TOTAL_BALANCE,
#   etc.). Despite contamination, produces usable values for DLQ 1-9 (~100%
#   coverage) because for deeply delinquent accounts stmt_balance ≈
#   total_outstanding. Meaningful for pre-delinquency history where billing
#   cycles are still active.
#
# TOTAL_DUE (41 ag_ids): 0% exclusive ag_ids but ~100% coverage for DLQ 1-9.
#   Accumulated payment obligation (≈ ENBD_TOTAL_DUE).
#
# ENBD_DUE (3 ag_ids): Minimum payment. COVERAGE GAP for high-DLQ accounts
#   (INV-7): 99.9% at DLQ 1, 34% at DLQ 2, down to 9.5% at DLQ 9. Mostly
#   NULL for our 60+ DPD target population. Useful for pre-delinquency
#   features only.
BILLING_TYPE_CODES = {
    "minimum_due": "ENBD_DUE",
    "stmt_balance": "STMT_BALANCE",
    "total_due": "TOTAL_DUE",
}

# Balance decomposition type_codes — billed-not-paid breakdown.
# Useful for feature engineering: principal vs interest vs insurance split.
BNP_TYPE_CODES = {
    "bnp_outstand": "BNP_OUTSTAND",
    "bnp_principal": "BNP_PRINCIPAL",
    "bnp_interest": "BNP_INTEREST",
    "ins_total": "INS_TOTAL",
}

# Legacy CONTRACT_ATTR_IDS — replaced by CONTRACT_ATTR_TYPES above.
# Kept for backward compat; not used by build_pivoted() anymore.
CONTRACT_ATTR_IDS: dict[str, int] = {}

# ---------------------------------------------------------------------------
# DT01 Demographics (Finacle) — sa_customer_kyc, sa_customer_relationship,
# sa_customer_kyc_financial
# ---------------------------------------------------------------------------

# SCD2 active indicator (edp_activeind values: Y/N/D)
FINACLE_SCD2_ACTIVE = "Y"

# customer_grouping_xref: entity dedup priority (ENBD first = highest priority)
ENTITY_PRIORITY = ["ENBD", "EIB", "KSA", "EGY", "IND", "LON", "SGP"]

# customer_grouping_xref: DOB sentinel cleanup bounds
DOB_MIN_YEAR = 1900
DOB_MAX_YEAR = 2026

# Customer segment codes (sa_customer_relationship.cust_seg_cd, 7 values)
SEGMENT_CODES = {
    "PSB": "Personal & Smart Banking",
    "Liv.": "Liv. (Digital Banking)",
    "BB": "Beyond Banking",
    "PRB": "Priority Banking",
    "WB": "Wealth Banking",
    "PB": "Private Banking",
    "OTHER": "Other",
}

# KYC risk rating groups (sa_customer_kyc.KYC_RISK_RATING, 11 observed values)
# Pattern: SSD* = Standard Due Diligence, EDD* = Enhanced Due Diligence
# Categorical grouping for feature engineering
KYC_RISK_RATING_GROUPS = {
    "standard_low": ["SSDL"],
    "standard_medium": ["SSDM"],
    "standard_high": ["SSDH"],  # Not yet observed in data
    "enhanced_standard": ["EDDS"],
    "enhanced_level_1": ["EDD1"],
    "enhanced_level_2": ["EDD2"],
    "enhanced_level_3": ["EDD3"],
    "enhanced_high": ["EDDH"],
    "enhanced_full": ["EDDF"],
    "high_risk": ["H"],
    "special": ["S"],
}

# KYC risk rating ordinal mapping — assumed hierarchy for modeling
# NOTE: This ordinal hierarchy is ASSUMED and needs verification with business
# TODO: Verify with stakeholders - is this the correct risk ordering?  # NOSONAR
KYC_RISK_RATING_ORDINAL = {
    "SSDL": 0,  # Standard DD Low (assumed lowest risk)
    "SSDM": 1,  # Standard DD Medium
    "SSDH": 2,  # Standard DD High (not observed in data)
    "EDDS": 3,  # Enhanced DD Standard
    "EDD1": 4,  # Enhanced DD Level 1
    "EDD2": 5,  # Enhanced DD Level 2
    "EDD3": 6,  # Enhanced DD Level 3
    "EDDH": 7,  # Enhanced DD High
    "EDDF": 8,  # Enhanced DD Full
    "H": 9,  # High Risk (mapping unclear - verify with business)
    "S": 10,  # Special (mapping unclear - verify with business)
}

# ---------------------------------------------------------------------------
# AECB Bureau configurations (DPL_UAE_OPERATIONS schema)
# ---------------------------------------------------------------------------

AECB_SCHEMA_BASE = "dpl_uae_operations"

# System/audit columns present in every AECB table — always dropped in staging.
AECB_METADATA_DROP_COLS = [
    "entity_cd",
    "create_dt_time",
    "update_dt_time",
    "create_user_nm",
    "update_user_nm",
    "delete_flg",
]

# Zero-information columns present in most AECB tables (constant 1.0).
AECB_CONSTANT_DROP_COLS = [
    "res_hdr_chunk_id",
]

# Contract type codes from cntr_sumry_cntrct_typ_cd / cntr_hist_cntrct_typ_cd
AECB_CONTRACT_TYPES = {
    "CreditCards": "credit_card",
    "Installments": "installment_loan",
    "NotInstallments": "non_installment_loan",
    "Services": "service",
    "Utilities": "utility",
}

# Holder/guarantor classification from cntr_sumry_holdr_guar_cd
AECB_HOLDER_GUARANTOR = {"Holder": "holder", "Guarantor": "guarantor"}

# --- Business rule mappings (populated from ref_ops_aecb, Apr 17 2026) ---

# cntr_hist_cntrct_sta_cd / cntr_dtl_worst_sta_cd — 17 codes
AECB_CONTRACT_STATUS: dict[str, str] = {
    "A": "arrangement",
    "B": "bankrupt",
    "C": "credit_settlement",
    "D": "deceased",
    "E": "extended_loan",
    "F": "default",
    "G": "guarantor_paying",
    "L": "left_country",
    "M": "suspended_unused",
    "N": "nddsf",
    "O": "disconnected_renounced",
    "P": "court_enforced_payments",
    "S": "suspended",
    "T": "dewan_settlement",
    "U": "up_to_date",
    "W": "write_off",
    "X": "disconnected_service",
}

# cntr_hist_pymnt_behvr — 9 codes (credit card / loan payment behaviour)
AECB_PAYMENT_BEHAVIOR: dict[str, str] = {
    "0": "ok_no_delay",
    "1": "minimum_payment",
    "2": "delay_6_29d",
    "3": "delay_30_59d",
    "4": "delay_60_89d",
    "5": "delay_90_119d",
    "6": "delay_120_149d",
    "7": "delay_150_179d",
    "8": "delay_180d_plus",
}

# cntr_hist_pymnt_dly_dy_cnt — 8 codes (all contract types EXCEPT services)
AECB_PAYMENT_DELAY: dict[str, str] = {
    "0": "current_0_5d",
    "1": "delay_6_29d",
    "2": "delay_30_59d",
    "3": "delay_60_89d",
    "4": "delay_90_119d",
    "5": "delay_120_149d",
    "6": "delay_150_179d",
    "7": "delay_180d_plus",
}

# cntr_hist_pymnt_dly_dy_cnt for services (telecom/utility) — 6 codes
AECB_PAYMENT_DELAY_SERVICES: dict[str, str] = {
    "0": "no_barring",
    "1": "barred_to_29d",
    "2": "delay_30_59d",
    "3": "delay_60_89d",
    "4": "delay_90_149d",
    "5": "delay_150d_plus",
}

# subj_crd_score_range — 23 codes across 3 score types:
#   SCORE_RANGE_CONSUMER (A-M), CNSMR_NOHIT (1-5), ALTDATA (A1-A5)
AECB_SCORE_RANGES: dict[str, str] = {
    # Consumer score (letter grades)
    "A": "very_high_risk",
    "B": "very_high_risk",
    "C": "high_risk",
    "D": "high_risk",
    "E": "medium_risk",
    "F": "medium_risk",
    "G": "medium_risk",
    "H": "low_risk",
    "I": "low_risk",
    "J": "low_risk",
    "K": "very_low_risk",
    "L": "very_low_risk",
    "M": "very_low_risk",
    # No-hit consumer (thin file, numeric grades)
    "1": "very_high_risk",
    "2": "high_risk",
    "3": "medium_risk",
    "4": "low_risk",
    "5": "very_low_risk",
    # Alternative data score
    "A1": "very_high_risk",
    "A2": "high_risk",
    "A3": "medium_risk",
    "A4": "low_risk",
    "A5": "very_low_risk",
}

# subj_crt_case_cat_cd — 5 codes
AECB_COURT_CASE_CATEGORIES: dict[str, str] = {
    "1": "rental",
    "2": "civil",
    "3": "labor",
    "4": "commercial",
    "5": "personal",
}

# subj_crt_case_status_cd — 3 codes
AECB_COURT_CASE_STATUSES: dict[str, str] = {
    "55": "active",
    "70": "on_hold",
    "90": "closed",
}

# subj_pymnt_ord_sev_cd — 3 codes (bounced cheque severity)
AECB_CHEQUE_SEVERITY: dict[str, str] = {
    "1": "single",
    "2": "multiple",
    "3": "reported",
}

# ALERT_CTG — 7 codes
AECB_ALERT_CATEGORIES: dict[str, str] = {
    "1": "contracts_applications_cheques",
    "2": "individual_data",
    "3": "individuals_companies_contacts",
    "4": "commercial_data",
    "5": "income_data",
    "6": "utilities_data",
    "7": "courts_data",
}


# ---------------------------------------------------------------------------
# Observation → data window expansion
# ---------------------------------------------------------------------------

# Default data-window lookahead (months) — 1 calendar month matches target_horizon_months: 1
DEFAULT_DATA_WINDOW_HORIZON_MONTHS = 1


def _subtract_months(d: date, months: int) -> date:
    """Subtract exact calendar months from a date, clamping to month-end."""
    y, m_idx = divmod(d.month - months - 1, 12)
    target_year = d.year + y
    target_month = m_idx + 1
    return date(
        target_year,
        target_month,
        min(d.day, calendar.monthrange(target_year, target_month)[1]),
    )


def _add_months(d: date, months: int, end_of_month: bool = False) -> date:
    """Add exact calendar months to a date, clamping to month-end."""
    y, m_idx = divmod(d.month + months - 1, 12)
    target_year = d.year + y
    target_month = m_idx + 1
    day = (
        calendar.monthrange(target_year, target_month)[1]
        if end_of_month
        else min(d.day, calendar.monthrange(target_year, target_month)[1])
    )
    return date(target_year, target_month, day)


def compute_data_window(modelling: dict | None) -> tuple[str | None, str | None]:
    """Expand observation window to data loading window.

    Adds max feature lookback before start_date and target_horizon_months
    after end_date so that every observation row in the window has
    sufficient data for features and targets.
    """
    if not modelling:
        return None, None
    start = modelling.get("start_date") or modelling.get("inference_date")
    end = modelling.get("end_date") or modelling.get("inference_date")
    horizon_months = modelling.get(
        "target_horizon_months", DEFAULT_DATA_WINDOW_HORIZON_MONTHS
    )
    lookback_months = max(m for m, _ in LOOKBACK_WINDOWS)
    data_start = (
        str(_subtract_months(date.fromisoformat(start), lookback_months))
        if start
        else None
    )
    data_end = (
        str(_add_months(date.fromisoformat(end), horizon_months, end_of_month=True))
        if end
        else None
    )
    return data_start, data_end


# ---------------------------------------------------------------------------
# EDP load date scope filtering
# ---------------------------------------------------------------------------


def filter_edp_load_date(df, start_date=None, end_date=None):
    """Filter DataFrame on ``edp_load_date`` column.

    No-op when both *start_date* and *end_date* are ``None``.
    Spark pushes the predicate down for Hive partition pruning.
    """
    if start_date is not None:
        df = df.filter(df["edp_load_date"] >= start_date)
    if end_date is not None:
        df = df.filter(df["edp_load_date"] <= end_date)
    return df


def filter_observation_date(df, start_date=None, end_date=None):
    """Filter DataFrame on ``observation_date`` column.

    No-op when both *start_date* and *end_date* are ``None``.
    Spark pushes the predicate down for Hive partition pruning.
    """
    if start_date is not None:
        df = df.filter(df["observation_date"] >= start_date)
    if end_date is not None:
        df = df.filter(df["observation_date"] <= end_date)
    return df


def scope_to_data_window(df, modelling=None):
    """Filter df by expanded data window. No-op when modelling is None.

    Optionally limits rows when modelling.row_limit is set.
    """
    if not modelling:
        return df
    data_start, data_end = compute_data_window(modelling)
    df = filter_edp_load_date(df, data_start, data_end)

    # Apply row limiting if specified (for fast schema validation)
    row_limit = modelling.get("row_limit")
    if row_limit is not None and row_limit > 0:
        df = df.limit(row_limit)

    return df
