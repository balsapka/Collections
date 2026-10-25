"""Staging node: OMB digital login events.

Unions two raw OMB login tables, filters to successful logins, derives is_foreign_login,
and resolves partyid → cif_id via the PDM users table.

Output grain: one row per login session (deduplicated on sessionid — the tables are
partitioned by edp_load_date and the same session can appear in multiple partitions).

Schema:
    cif_id          (str)        — bank CIF number
    login_date      (date)       — date of login
    is_foreign_login (int 0/1)   — 1 if login originated outside UAE
    countrylocation (str, null)  — country name from login record
    countrycode     (str, null)  — ISO country code from login record
    login_interface (str, null)  — login channel (channel column)
"""

import logging
from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(
    raw_digital_login_data: DataFrame,
    raw_digital_login_data_history: DataFrame,
    raw_digital_user_data: DataFrame,
) -> DataFrame:
    """Stage OMB login events: union, dedup, CIF resolve, country flag.

    Args:
        raw_digital_login_data:         Current OMB login table
                                        (CL_OMB_GROUP_REPORTS.LOGIN_DATA_EBI).
                                        Cols used: partyid, status, createdon,
                                        countrylocation, countrycode, channel,
                                        sessionid.
        raw_digital_login_data_history: Historical OMB login table
                                        (tdv_omb_uae_ebi.loginlog).
                                        May lack countrycode — handled via
                                        allowMissingColumns union.
        raw_digital_user_data:          PDM users table (tdv_pdm_uae_ebi.users).
                                        Maps partyid → cif_id.
                                        Cols used: id (= partyid), cif.

    Returns:
        Session-grain DataFrame with stable schema (NULL-padded for missing columns).
    """
    # ── CIF lookup: PDM users id → cif ────────────────────────────────────────
    # 'id' in the users table is the partyid (Firebase ID); 'cif' is the bank CIF.
    # Dedup on (cif_id, _party_id) — matches retail.feature_space convention.
    # raw_digital_user_data is SCD2 (has edp_activeind, edp_effectivestartdate,
    # edp_effectiveenddate). Filter to 'Y' so superseded historical versions of a
    # user record are excluded from the CIF map.
    user_cols_lower = {c.lower() for c in raw_digital_user_data.columns}
    if "id" not in user_cols_lower or "cif" not in user_cols_lower:
        LOG.warning(
            "stg_digital_login: raw_digital_user_data missing 'id' or 'cif' column "
            "— emitting empty staging output"
        )
        return _empty_schema()

    active_users = raw_digital_user_data
    if "edp_activeind" in user_cols_lower:
        active_users = active_users.filter(F.col("edp_activeind") == F.lit("Y"))

    cif_map = (
        active_users.filter(F.col("cif").isNotNull())
        .select(
            F.col("id").cast("string").alias("_party_id"),
            F.col("cif").cast("string").alias("cif_id"),
        )
        .dropDuplicates(["cif_id", "_party_id"])
    )

    # ── Normalise each source to common columns before union ─────────────────
    current = _normalise_source(raw_digital_login_data, source_label="current")
    history = _normalise_source(raw_digital_login_data_history, source_label="history")

    if current is None and history is None:
        LOG.warning("stg_digital_login: both login tables missing required columns")
        return _empty_schema()

    if current is None:
        combined = history
    elif history is None:
        combined = current
    else:
        combined = current.unionByName(history, allowMissingColumns=True)

    # ── Filter to successful logins ───────────────────────────────────────────
    # Include "pre_login" per retail.feature_space convention — partial logins
    # still carry a valid country signal for the departure feature.
    logins = combined.filter(F.lower(F.col("status")).isin(["success", "pre_login"]))

    # ── Dedup on sessionid ────────────────────────────────────────────────────
    # Both tables are partitioned by edp_load_date; the same sessionid can appear
    # in multiple partitions. Drop to one row per session before deriving features.
    if "sessionid" in {c.lower() for c in logins.columns}:
        logins = logins.dropDuplicates(["sessionid"])

    # ── Derive is_foreign_login ───────────────────────────────────────────────
    # UAE match: UPPER(REGEXP_REPLACE(countrylocation, whitespace, '')) = 'UNITEDARABEMIRATES'
    # OR UPPER(countrycode) = 'AE'.  Each guarded by null-check.
    uae_by_name = F.col("countrylocation").isNotNull() & (
        F.upper(F.regexp_replace(F.col("countrylocation"), r"\s+", ""))
        == F.lit("UNITEDARABEMIRATES")
    )
    uae_by_code = F.col("countrycode").isNotNull() & (
        F.upper(F.col("countrycode")) == F.lit("AE")
    )
    uae_cond = uae_by_name | uae_by_code

    logins = logins.withColumn(
        "is_foreign_login",
        F.when(uae_cond, F.lit(0)).otherwise(F.lit(1)).cast("int"),
    )

    # ── Resolve partyid → cif_id via PDM users (inner join drops unresolved) ──
    result = logins.join(cif_map, logins["partyid"] == cif_map["_party_id"], "inner")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("login_date").cast("date"),
        F.col("is_foreign_login").cast("int"),
        F.col("countrylocation").cast("string"),
        F.col("countrycode").cast("string"),
        F.col("login_interface").cast("string"),
    )


# ── Private helpers ───────────────────────────────────────────────────────────


def _normalise_source(df: DataFrame, source_label: str) -> Optional[DataFrame]:
    """Normalise a raw login source to common columns.

    Required: partyid, status, createdon.
    Optional: countrylocation, countrycode, channel, sessionid.
    Returns None if required columns are absent.
    """
    cols_lower = {c.lower() for c in df.columns}
    required = ["partyid", "status", "createdon"]
    missing = [c for c in required if c not in cols_lower]
    if missing:
        LOG.warning(
            "stg_digital_login [%s]: missing required columns %s — skipping source",
            source_label,
            missing,
        )
        return None

    # SCD2 tables carry edp_activeind (Y/N). Filter to active records only so that
    # historical partition rows (edp_activeind='N') are not counted as login events.
    # The current table (raw_digital_login_data) has no edp_activeind — guard prevents
    # errors on that source.
    if "edp_activeind" in cols_lower:
        df = df.filter(F.col("edp_activeind") == F.lit("Y"))

    # createdon is a TIMESTAMP in both tables — to_date() truncates to date directly.
    login_date_expr = F.to_date(F.col("createdon"))

    # Optional columns — emit NULL if absent
    def _opt(col_name: str, dtype: str) -> F.Column:
        return (
            F.col(col_name).cast(dtype)
            if col_name in cols_lower
            else F.lit(None).cast(dtype)
        )

    return df.select(
        F.col("partyid").cast("string").alias("partyid"),
        F.col("status").cast("string").alias("status"),
        login_date_expr.alias("login_date"),
        _opt("countrylocation", "string").alias("countrylocation"),
        _opt("countrycode", "string").alias("countrycode"),
        _opt("channel", "string").alias("login_interface"),
        _opt("sessionid", "string").alias("sessionid"),
    )


def _empty_schema() -> DataFrame:
    """Return an empty DataFrame with the stable output schema.

    Used when required columns are missing to preserve schema contract.
    """
    from pyspark.sql import SparkSession  # pylint: disable=import-outside-toplevel
    from pyspark.sql.types import (  # pylint: disable=import-outside-toplevel
        DateType,
        IntegerType,
        StringType,
        StructField,
        StructType,
    )

    spark = SparkSession.builder.getOrCreate()
    schema = StructType(
        [
            StructField("cif_id", StringType(), True),
            StructField("login_date", DateType(), True),
            StructField("is_foreign_login", IntegerType(), True),
            StructField("countrylocation", StringType(), True),
            StructField("countrycode", StringType(), True),
            StructField("login_interface", StringType(), True),
        ]
    )
    return spark.createDataFrame([], schema)
