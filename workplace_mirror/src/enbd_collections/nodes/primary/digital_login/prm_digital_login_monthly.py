"""Primary node: monthly OMB digital login aggregation.

Aggregates stg_digital_login event-grain to (cif_id × month_number) grain.

month_number: last day of login month in yyyyMMdd format — consistent with
retail.feature_space fea_customer_digital_engagement and fea_monthly_aecb_alerts.

Schema:
    cif_id                  (str)        — bank CIF number
    month_number            (str)        — yyyyMMdd, last day of month
    last_login_date         (date)       — most recent login_date in month
    last_login_foreign_flag (int 0/1)    — is_foreign_login for most recent login
    last_login_country      (str, null)  — countrylocation of most recent login
    last_login_countrycode  (str, null)  — countrycode of most recent login
    any_foreign_login_flag  (int 0/1)    — 1 if any login in month was foreign
    foreign_login_cnt       (int)        — count of foreign logins in month
    total_login_cnt         (int)        — total successful logins in month
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(stg_digital_login: DataFrame) -> DataFrame:
    """Aggregate login events to (cif_id × month_number) grain.

    Args:
        stg_digital_login: Output of stg_digital_login node.
                           Required cols: cif_id, login_date, is_foreign_login,
                           countrylocation, countrycode.

    Returns:
        DataFrame at grain (cif_id, month_number).
    """
    # ── Derive month_number: last day of login month (yyyyMMdd) ──────────────
    df = stg_digital_login.withColumn(
        "month_number",
        F.date_format(F.last_day(F.col("login_date")), "yyyyMMdd"),
    )

    # ── Window for most-recent login per (cif_id, month_number) ──────────────
    w_last = Window.partitionBy("cif_id", "month_number").orderBy(
        F.col("login_date").desc()
    )
    df_ranked = df.withColumn("_rn", F.row_number().over(w_last))

    # Extract last-login attributes (rank 1 row)
    last_login_details = df_ranked.filter(F.col("_rn") == 1).select(
        "cif_id",
        "month_number",
        F.col("login_date").alias("last_login_date"),
        F.col("is_foreign_login").cast("int").alias("last_login_foreign_flag"),
        F.col("countrylocation").cast("string").alias("last_login_country"),
        F.col("countrycode").cast("string").alias("last_login_countrycode"),
    )

    # ── Monthly aggregation ───────────────────────────────────────────────────
    agg = df.groupBy("cif_id", "month_number").agg(
        F.sum(F.col("is_foreign_login").cast("int"))
        .cast("int")
        .alias("foreign_login_cnt"),
        F.count("*").cast("int").alias("total_login_cnt"),
        F.max(F.col("is_foreign_login").cast("int"))
        .cast("int")
        .alias("any_foreign_login_flag"),
    )

    # ── Join last-login details onto aggregation ──────────────────────────────
    result = agg.join(last_login_details, on=["cif_id", "month_number"], how="left")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("month_number").cast("string"),
        F.col("last_login_date").cast("date"),
        F.col("last_login_foreign_flag").cast("int"),
        F.col("last_login_country").cast("string"),
        F.col("last_login_countrycode").cast("string"),
        F.col("any_foreign_login_flag").cast("int"),
        F.col("foreign_login_cnt").cast("int"),
        F.col("total_login_cnt").cast("int"),
    )
