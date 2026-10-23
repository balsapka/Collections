"""
Staging layer: stg_rr_portf -> Monthly loan portfolio snapshots (active + closed).

Grain: acct_num × ss_dt (monthly account snapshots)
Sources:
  - bo_rr_portf_actv_acct_mthly  (active accounts, 2025-12 onwards)
  - bo_rr_portf_clsd_acct_mthly  (closed accounts, 2025-12 onwards)
  - ecl_bo_rr_portfolio_mthly_hist (active + closed, pre-2025-12, split by ra_ln_stat_nm)

Purpose: Full portfolio history for model training (active + closed, monthly grain).
All column names normalised to the monthly bo schema (4 ECL fields renamed to add _mtd suffix).
"""

from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import DateType
from pyspark.sql.window import Window

_SELECT_COLS = [
    # Identifiers
    "ra_org_app_id",  # Application ID (links to acquisition)
    "acct_num",  # Loan account ID (primary key)
    "cust_num",  # Customer ID
    "ss_dt",  # Snapshot date (month-end)
    # Product classification
    "prod_cd",  # Product code
    "ra_prod_typ_nm",  # Product type (Personal/Auto/Home)
    "ra_prod_sub_typ_nm",  # Product sub-type
    "ra_prod_cat_nm",  # Product category
    # Amounts
    "ra_disb_amt_ocy",  # Disbursement amount (original currency)
    "ra_appr_ln_amt",  # Approved loan amount
    "ra_enr_amt",  # Expected Net Receivable (current outstanding)
    "ra_prev_enr_amt",  # Previous outstanding (for delta)
    "ra_ovd_tot_amt",  # Total overdue amount
    "ra_ovd_princ_amt",  # Overdue principal
    "ra_ovd_int_amt",  # Overdue interest
    # Delinquency
    "ra_delq_bkt",  # DPD bucket (0-7)
    "ra_ovd_days",  # Current overdue days (numeric DPD)
    "ra_prev_ovd_days",  # Previous overdue days (for velocity)
    "ra_risk_grd",  # Risk grade (7 categories)
    "ra_prev_risk_grd",  # Previous risk grade (for migration)
    # EMI
    "ra_instl_due_amt",  # Monthly installment due (95.7% populated)
    "ra_bill_cycl_dy",  # Billing cycle day
    # Dates
    "ra_disb_dt",  # Disbursement date
    "ra_maturity_dt",  # Maturity date (0.02% null)
    "ra_lst_pymt_dt_mtd",  # Last payment date MTD (48% null)
    # Restructuring
    "ra_rewrt_flg",  # Rewrite flag (0.5% populated)
    "ra_rewrt_dt",  # Rewrite date (99.5% null)
    "ra_rewrt_typ",  # Rewrite type (2 distinct values)
    # Status
    "ra_ln_stat_nm",  # Loan status name (0% null)
    # Metadata
    "edp_load_date",  # EDP timestamp
    # Payment behaviour
    "ra_frst_pymt_dflt_flg",  # First EMI ever defaulted flag (0/1)
    "ra_sec_pymt_dflt_flg",  # Second EMI ever defaulted flag (0/1)
    "ra_repymt_amt_mtd",  # Repayment amount month-to-date
    "ra_repymt_flg_mtd",  # Whether repayment made this month (0/1)
    "ra_pymt_amt_mtd",  # Payment amount month-to-date (distinct from repayment)
    # Risk / affordability
    "ra_dbr",  # Debt-to-Burden Ratio (3% null) — KEY risk signal
    "ra_eff_int_rate",  # Effective interest rate (0% null)
    # Outstanding amounts
    "ra_fee_os_amt",  # Total fees outstanding (0% null)
    "ra_tot_os_amt",  # Total overdue fees (?)
    # Loan characteristics
    "ra_num_of_instl",  # Remaining installments after prepayments (≠ ra_tnr when prepaid)
    "ra_int_typ_nm",  # Interest type: F-FIXED / M-FLOATING (3.8% null)
    "ra_ln_acct_opn_dt",  # Account open date (0% null; differs from ra_disb_dt in 6.2% of cases)
    "ra_ln_stat_dt",  # Loan status change date (0% null)
    "ra_woff_dt",  # Write-off date (81% null but needed for both models)
    # Categoricals
    "ra_cust_seg",  # Customer segment (PRB/PSB/etc)
    "ra_ln_nat_nm",  # Loan nature: NEW/TOPUP/TAKEOVER
    "ra_pymt_mod",  # Payment mode: A OR E-AUTO-DEBIT / N-DDS
    "ra_cust_nat_cat_nm",  # Nationality category: LOCAL/EXPAT
    # Demographics
    "ra_cust_age",  # Customer age (27% null)
    "ra_cust_annl_inc",  # Annual income (46% null)
    # Loan term tracking
    "ra_tnr",  # Original loan tenure in months (0% null; complements ra_num_of_instl)
    # Prepayment signals (ra_num_of_instl < ra_tnr iff prepaid)
    "ra_prepymt_flg",  # Prepayment flag (0/1; 4.7% = 1)
    "ra_prepymt_amt",  # Prepayment amount in AED (95.3% null; populated when ra_prepymt_flg=1)
    "ra_prepymt_dt",  # Prepayment date (95.3% null; populated when ra_prepymt_flg=1)
    # Fee breakdown
    "ra_ovd_fee_amt",  # Overdue fee amount (~92% >0 in sample)
    "ra_late_fee_amt",  # Late fee amount (~34% >0 in sample)
    "ra_tot_fee_amt",  # Total fee amount (0% null)
    # Recovery (Model 2 signal — DLQ 7 scope: 94K/11.9M rows >0 in PROD)
    "ra_tot_rcvr_amt",  # Total recovery amount (~0.8% non-zero at DLQ 7)
]

# ECL historical uses base field names; monthly bo tables use _mtd suffix variants.
_ECL_RENAMES = {
    "ra_lst_pymt_dt": "ra_lst_pymt_dt_mtd",
    "ra_repymt_amt": "ra_repymt_amt_mtd",
    "ra_repymt_flg": "ra_repymt_flg_mtd",
    "ra_pymt_amt": "ra_pymt_amt_mtd",
}

# ECL historical table stops at 2025-11 (monthly bo tables cover 2025-12 onwards).
ECL_CUTOFF_DATE = "2025-12-01"

# `ecl_bo_rr_portfolio_mthly_hist`'s catalog entry resolves to the raw Hive table
# `group_ecl.bo_rr_portfolio_mthly_hist_winnow_ncl_grr` -- a server-side extract
# winnowed to these prod_cd values only (confirmed by the business). A loan whose
# product_code falls outside this set is genuinely, structurally absent from the
# pre-cutoff ECL historical leg of union_raw(), independent of its disbursement_date.
ECL_WINNOWED_PRODUCT_CODES = frozenset({"20", "30", "50", "60"})


def union_raw(  # pylint: disable=too-many-locals
    raw_actv: DataFrame,
    raw_clsd: DataFrame,
    raw_hist: DataFrame,
    incremental_from_date: Optional[str] = None,
) -> DataFrame:
    """Union and normalise the three portfolio sources. No scope applied.

    Args:
        raw_actv: Raw bo_rr_portf_actv_acct_mthly DataFrame.
        raw_clsd: Raw bo_rr_portf_clsd_acct_mthly DataFrame.
        raw_hist: Raw ecl_bo_rr_portfolio_mthly_hist DataFrame.
        incremental_from_date: If set (e.g. "2026-08-01"), restrict DPL to that
            month only and skip ECL historical entirely. Combined with
            partitionOverwriteMode=dynamic in the catalog, only the new ss_dt
            partition is written; all prior HDFS partitions are preserved.
            None (default) = full reprocess (training).

    Returns:
        Unscoped union DataFrame ready for dedup and select in build().
    """
    # Incremental mode: restrict DPL to new months, skip ECL historical entirely.
    # ECL historical is all pre-2025-12 — new data is never added there post-cutoff.
    # partitionOverwriteMode=dynamic means only these ss_dt partitions are written;
    # existing HDFS partitions are untouched.
    if incremental_from_date is not None:
        raw_actv = raw_actv.filter(
            F.col("edp_load_date") >= F.lit(incremental_from_date)
        )
        raw_clsd = raw_clsd.filter(
            F.col("edp_load_date") >= F.lit(incremental_from_date)
        )
        raw_hist = raw_hist.filter(F.lit(False))  # empty DataFrame, same schema

    # 1. Restrict ECL historical to pre-2025-12 (avoids overlap with monthly bo)
    raw_hist = raw_hist.filter(F.col("edp_load_date") < F.lit(ECL_CUTOFF_DATE))

    # 1b. Restrict DPL tables from 2025-11
    raw_actv = raw_actv.filter(F.col("edp_load_date") >= F.lit(ECL_CUTOFF_DATE))
    raw_clsd = raw_clsd.filter(F.col("edp_load_date") >= F.lit(ECL_CUTOFF_DATE))

    # 2. Normalise ECL field names to match monthly bo schema (4 payment/date fields)
    for old, new in _ECL_RENAMES.items():
        raw_hist = raw_hist.withColumnRenamed(old, new)

    # 3. Apply casts
    raw_actv = _apply_casts(raw_actv)
    raw_clsd = _apply_casts(raw_clsd)
    raw_hist = _apply_casts(raw_hist)

    # 4a. Define "effectively closed" condition
    is_closed_cond = (F.col("ra_enr_amt").isNotNull() & (F.col("ra_enr_amt") <= 0)) | (
        F.upper(F.col("ra_ln_stat_nm")) == F.lit("CLOSED")
    )

    # 4b. Split raw_hist — ECL historical mixes both statuses
    hist_active = raw_hist.filter(~is_closed_cond)

    # 4c. Closed-side filter: only include the month in which the account closed.
    #     ra_ln_stat_dt must fall within the calendar month of ss_dt.
    #     (ra_ln_stat_dt is 0% null per staging doc; isNotNull() is defensive.)
    month_start = F.trunc(F.col("ss_dt"), "month")
    closed_month_filter = (
        F.col("ra_ln_stat_dt").isNotNull()
        & (F.col("ra_ln_stat_dt") >= month_start)
        & (F.col("ra_ln_stat_dt") <= F.col("ss_dt"))
    )

    raw_clsd_filtered = raw_clsd.filter(closed_month_filter)
    hist_clsd_filtered = raw_hist.filter(is_closed_cond).filter(closed_month_filter)

    # 4d. Union all four partitions (hist_active and hist_clsd_filtered are disjoint)
    combined = raw_actv.unionByName(raw_clsd_filtered, allowMissingColumns=True)
    combined = combined.unionByName(hist_active, allowMissingColumns=True)
    combined = combined.unionByName(hist_clsd_filtered, allowMissingColumns=True)

    # 5. Dedup: bo_rr_portf_clsd_acct_mthly can produce a duplicate
    #    (ra_org_app_id, edp_load_date) row when an account also appears
    #    in the active table. Keep the non-CLOSED record.
    _is_closed_priority = F.when(
        (F.col("ra_enr_amt").isNotNull() & (F.col("ra_enr_amt") <= 0))
        | (F.upper(F.col("ra_ln_stat_nm")) == F.lit("CLOSED")),
        1,
    ).otherwise(0)
    _dedup_window = Window.partitionBy("ra_org_app_id", "edp_load_date").orderBy(
        _is_closed_priority.asc()
    )
    result = (
        combined.withColumn("_rn", F.row_number().over(_dedup_window))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )
    return result.localCheckpoint()


def build(df: DataFrame, scope_cifs: Optional[DataFrame] = None) -> DataFrame:
    """Scope to in-scope CIFs (if provided) and select staging columns.

    Args:
        df: Output of union_raw() — full portfolio union.
        scope_cifs: Optional DataFrame with a cif_id column. When provided,
            filters df to rows whose cust_num appears in scope_cifs.

    Returns:
        Staging DataFrame with 58 selected columns.
    """
    if scope_cifs is not None:
        cif_ids = scope_cifs.withColumnRenamed("cif_id", "cust_num")
        df = df.join(F.broadcast(cif_ids), "cust_num", "leftsemi")
    return df.select(*_SELECT_COLS)


def _apply_casts(df: DataFrame) -> DataFrame:
    """Apply type casts to normalise source types.

    Timestamps → DateType (strip time component).
    ra_bill_cycl_dy: string → int in source.
    DPD/count/flag columns: source stores as double — normalise to int.
    edp_load_date: kept as defensive cast; ECL hist source type unconfirmed.
    Amount columns (already double in source) are not cast.
    """
    return (
        # Timestamps → date
        df.withColumn("ss_dt", F.col("ss_dt").cast(DateType()))
        .withColumn("edp_load_date", F.col("edp_load_date").cast(DateType()))
        .withColumn("ra_disb_dt", F.col("ra_disb_dt").cast(DateType()))
        .withColumn("ra_maturity_dt", F.col("ra_maturity_dt").cast(DateType()))
        .withColumn("ra_lst_pymt_dt_mtd", F.col("ra_lst_pymt_dt_mtd").cast(DateType()))
        .withColumn("ra_rewrt_dt", F.col("ra_rewrt_dt").cast(DateType()))
        .withColumn("ra_ln_acct_opn_dt", F.col("ra_ln_acct_opn_dt").cast(DateType()))
        .withColumn("ra_ln_stat_dt", F.col("ra_ln_stat_dt").cast(DateType()))
        .withColumn("ra_woff_dt", F.col("ra_woff_dt").cast(DateType()))
        .withColumn("ra_prepymt_dt", F.col("ra_prepymt_dt").cast(DateType()))
        # String → int
        .withColumn("ra_bill_cycl_dy", F.col("ra_bill_cycl_dy").cast("int"))
        # Double → int (DPD, counts, flags, tenure)
        .withColumn("ra_delq_bkt", F.col("ra_delq_bkt").cast("int"))
        .withColumn("ra_ovd_days", F.col("ra_ovd_days").cast("int"))
        .withColumn("ra_prev_ovd_days", F.col("ra_prev_ovd_days").cast("int"))
        .withColumn("ra_frst_pymt_dflt_flg", F.col("ra_frst_pymt_dflt_flg").cast("int"))
        .withColumn("ra_sec_pymt_dflt_flg", F.col("ra_sec_pymt_dflt_flg").cast("int"))
        .withColumn("ra_repymt_flg_mtd", F.col("ra_repymt_flg_mtd").cast("int"))
        .withColumn("ra_num_of_instl", F.col("ra_num_of_instl").cast("int"))
        .withColumn("ra_cust_age", F.col("ra_cust_age").cast("int"))
        .withColumn("ra_tnr", F.col("ra_tnr").cast("int"))
        .withColumn("ra_prepymt_flg", F.col("ra_prepymt_flg").cast("int"))
    )
