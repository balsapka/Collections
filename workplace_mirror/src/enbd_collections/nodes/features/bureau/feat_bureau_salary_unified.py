"""
Feature layer: one monthly salary per CIF, unified across the three bureau salary sources.

Sources (precedence, highest first):
    1. int_bureau_alert_salary_monthly   -- salary alerts (alert_salary_amount)
    2. int_bureau_salary_credit_monthly  -- bank salary credit history (monthly_salary_credit)
    3. int_bureau_salary_monthly         -- AECB reported salary spread (monthly_salary)
Grain:  cif_id × salary_month_end

All sources are unioned and reduced to one row per (cif_id, salary_month_end). A usable
amount is non-null and non-zero; the best usable amount by source precedence wins, so a
0/null in a higher source is filled from the next source that has a value. If no source has a
usable amount the month keeps 0 when any source reports 0, otherwise null. Inside one source
the latest load date wins (alerts: extract date; salary spread: EDP_LOAD_DATE), then the
larger amount. Rows without a cif_id cannot be deduplicated and are dropped. When scope
filtering is on, output is restricted to the spine CIFs in scope_cifs (per model_id).
"""

from typing import Optional

import pyspark.sql.functions as F
from pyspark.sql import DataFrame, Window

from enbd_collections.nodes.model_input.scope_extractor import resolve_cif_scope


SOURCE_ALERT = "alert"
SOURCE_CREDIT = "salary_credit"
SOURCE_BUREAU = "bureau_salary"

_OUT = [
    "cif_id",
    "salary_month_end",
    "salary_amount",
    "salary_source",
    "is_closure",
    "_rank",
    "_load_date",
]


def build(
    int_bureau_alert_salary_monthly: DataFrame,
    int_bureau_salary_credit_monthly: DataFrame,
    int_bureau_salary_monthly: DataFrame,
    scope_cifs: Optional[DataFrame] = None,
    modelling: dict | None = None,
) -> DataFrame:
    """Union the three salary sources and keep one amount per (cif_id, salary_month_end).

    Returns:
        DataFrame at grain (cif_id, salary_month_end) with monthly_salary (double) and
        salary_source ("alert" / "salary_credit" / "bureau_salary"), kept for debugging, and
        is_closure (boolean): true only when the winning row is a salaryaccountclosed alert with
        a positive amount. Such a month counts in its own month; forward filling downstream must
        not carry it into the next month.
    """
    alert = int_bureau_alert_salary_monthly.select(
        "cif_id",
        "salary_month_end",
        F.col("alert_salary_amount").cast("double").alias("salary_amount"),
        F.lit(SOURCE_ALERT).alias("salary_source"),
        F.coalesce(F.col("is_closure"), F.lit(False)).alias("is_closure"),
        F.lit(1).alias("_rank"),
        F.col("alert_extract_date").cast("date").alias("_load_date"),
    )
    credit = int_bureau_salary_credit_monthly.select(
        "cif_id",
        "salary_month_end",
        F.col("monthly_salary_credit").cast("double").alias("salary_amount"),
        F.lit(SOURCE_CREDIT).alias("salary_source"),
        F.lit(False).alias("is_closure"),
        F.lit(2).alias("_rank"),
        F.lit(None).cast("date").alias("_load_date"),
    )
    bureau = int_bureau_salary_monthly.select(
        "cif_id",
        "salary_month_end",
        F.col("monthly_salary").cast("double").alias("salary_amount"),
        F.lit(SOURCE_BUREAU).alias("salary_source"),
        F.lit(False).alias("is_closure"),
        F.lit(3).alias("_rank"),
        F.col("EDP_LOAD_DATE").cast("date").alias("_load_date"),
    )
    unioned = (
        alert.select(*_OUT)
        .unionByName(credit.select(*_OUT))
        .unionByName(bureau.select(*_OUT))
        .where(F.col("cif_id").isNotNull() & F.col("salary_month_end").isNotNull())
    )
    amount = F.col("salary_amount")
    best = Window.partitionBy("cif_id", "salary_month_end").orderBy(
        (amount.isNotNull() & (amount != 0)).desc(),  # usable (non-null, non-zero) first
        amount.isNotNull().desc(),  # then 0 over null
        F.col("_rank").asc(),  # source precedence
        F.col("_load_date").desc_nulls_last(),  # latest load inside a source
        amount.desc_nulls_last(),
    )
    scope = resolve_cif_scope(scope_cifs, modelling)
    if scope is not None:
        # Staging scopes at bureau-file level (a superset); enforce exact CIF scope here.
        unioned = unioned.join(
            F.broadcast(scope.select(F.col("cif_id").cast("long").alias("cif_id")).distinct()),
            on="cif_id",
            how="left_semi",
        )
    return (
        unioned.withColumn("_rn", F.row_number().over(best))
        .where(F.col("_rn") == 1)
        .select(
            "cif_id",
            "salary_month_end",
            amount.alias("monthly_salary"),
            "salary_source",
            "is_closure",
        )
    )
