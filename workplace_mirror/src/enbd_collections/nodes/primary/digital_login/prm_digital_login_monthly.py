"""Primary node: monthly OMB digital login aggregation.

Aggregates stg_digital_login event-grain to (cif_id × month_number) grain.

month_number: last day of login month in yyyyMMdd format — consistent with
retail.feature_space fea_customer_digital_engagement and fea_monthly_aecb_alerts.

Schema:
    cif_id                     (str)        — bank CIF number
    month_number               (str)        — yyyyMMdd, last day of month
    last_login_date            (date)       — most recent login_date in month
    last_login_foreign_flag    (int 0/1)    — is_foreign_login for most recent login
                                              (NULL: no country)
    last_login_country         (str, null)  — countrylocation of most recent login
    last_login_countrycode     (str, null)  — countrycode of most recent login
    any_foreign_login_flag     (int 0/1)    — 1 if any login in month was foreign
    foreign_login_cnt          (int)        — count of foreign logins in month
    total_login_cnt            (int)        — total successful logins in month
    last_uae_login_date        (date, null) — latest login from the UAE in month
    last_foreign_login_date    (date, null) — latest login from abroad in month
    unknown_country_login_cnt  (int)        — logins in month without a country

Logins are dated by day, so several can share the month's last login day: the most
recent login is then a foreign one if any (foreign evidence wins a same-day tie),
otherwise a UAE one, otherwise one without a country.
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
    df = stg_digital_login.withColumn(
        "month_number",
        F.date_format(F.last_day(F.col("login_date")), "yyyyMMdd"),
    )
    foreign = F.col("is_foreign_login").cast("int")

    # ── Most recent login per (cif_id, month_number); same day: foreign first ─
    w_last = Window.partitionBy("cif_id", "month_number").orderBy(
        F.col("login_date").desc(),
        foreign.desc_nulls_last(),
        F.col("countrylocation").desc_nulls_last(),
        F.col("countrycode").desc_nulls_last(),
    )
    last_login_details = (
        df.withColumn("_rn", F.row_number().over(w_last))
        .filter(F.col("_rn") == 1)
        .select(
            "cif_id",
            "month_number",
            F.col("login_date").alias("last_login_date"),
            foreign.alias("last_login_foreign_flag"),
            F.col("countrylocation").cast("string").alias("last_login_country"),
            F.col("countrycode").cast("string").alias("last_login_countrycode"),
        )
    )

    # ── Monthly aggregation ───────────────────────────────────────────────────
    agg = df.groupBy("cif_id", "month_number").agg(
        F.coalesce(F.sum(foreign), F.lit(0)).cast("int").alias("foreign_login_cnt"),
        F.count("*").cast("int").alias("total_login_cnt"),
        F.coalesce(F.max(foreign), F.lit(0))
        .cast("int")
        .alias("any_foreign_login_flag"),
        F.max(F.when(foreign == 0, F.col("login_date"))).alias("last_uae_login_date"),
        F.max(F.when(foreign == 1, F.col("login_date"))).alias(
            "last_foreign_login_date"
        ),
        F.sum(F.when(foreign.isNull(), 1).otherwise(0))
        .cast("int")
        .alias("unknown_country_login_cnt"),
    )

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
        F.col("last_uae_login_date").cast("date"),
        F.col("last_foreign_login_date").cast("date"),
        F.col("unknown_country_login_cnt").cast("int"),
    )
