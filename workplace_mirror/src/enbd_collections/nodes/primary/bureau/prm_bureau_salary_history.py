"""Primary dataset: AECB salary history (``prm_bureau_salary_history``).

One row per bureau file, salary month, reporting provider and load: the monthly salary
total each provider reported to the bureau. It carries no ``cif_id``; features join the
CIF bridge on ``bureau_file_id``.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_RENAMES = {
    "subj_salcr_hist_hdr_file_id": "bureau_file_id",
    "subj_salcr_hist_ref_mnth": "reference_month",
    "subj_salcrdt_prvdr_no": "provider_no",
    "EDP_LOAD_DATE": "edp_load_date",
    "subj_salcr_hist_tot_sal_amt": "total_salary_amount",
    "subj_salcr_hist_trnsfr_cnt": "transfer_count",
}
_GRAIN = ["bureau_file_id", "reference_month", "provider_no", "edp_load_date"]


def build(stg_salary_history: DataFrame) -> DataFrame:
    """``stg_aecb_salary_history`` typed and renamed: ``reference_month`` is the first day
    of the salary month (the source holds ``MMyyyy``, e.g. ``072023``), amounts are
    doubles. Exact duplicates of a grain row keep one (the largest amount)."""
    missing = sorted(set(_RENAMES) - set(stg_salary_history.columns))
    if missing:
        raise ValueError(f"stg_aecb_salary_history is missing columns: {missing}")
    df = stg_salary_history.select(
        F.col("subj_salcr_hist_hdr_file_id").cast("string").alias("bureau_file_id"),
        F.to_date(
            F.lpad(F.col("subj_salcr_hist_ref_mnth").cast("string"), 6, "0"), "MMyyyy"
        ).alias("reference_month"),
        F.col("subj_salcrdt_prvdr_no").cast("string").alias("provider_no"),
        F.col("EDP_LOAD_DATE").cast("date").alias("edp_load_date"),
        F.col("subj_salcr_hist_tot_sal_amt")
        .cast("double")
        .alias("total_salary_amount"),
        F.col("subj_salcr_hist_trnsfr_cnt").cast("double").alias("transfer_count"),
    ).filter(F.col("bureau_file_id").isNotNull() & F.col("reference_month").isNotNull())
    first = Window.partitionBy(*_GRAIN).orderBy(
        F.col("total_salary_amount").desc_nulls_last()
    )
    return (
        df.withColumn("_rn", F.row_number().over(first))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )
