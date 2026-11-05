"""CC full billing history: ``raw_stg_billing`` scoped to the run's ``cc_spine``.

Output ``crx_cc_full_history`` at grain (account_id long, billing_date date) with
``dlq_bucket`` int and ``cif_id`` from the spine. Run:
``kedro run --pipeline=crx_cc_full_history`` (needs the spine of the model_id).

* a bucket that cannot be parsed from ``add_info`` is NULL, never "" cast to int (an
  error under ANSI mode, the default from Spark 4);
* the same-date duplicate takes the worst (max) non-null bucket, so reruns agree;
* no history floor here: ``build_cc_dpd_sequences`` applies it, so it can tell a
  floor-cropped account from a new one.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns

# add_info carries "BS_PMT_CYCLE_DUE=<bucket>".
_DPD_BUCKET_REGEX = r"BS_PMT_CYCLE_DUE=(\d+)"


def build_cc_full_history(raw_stg_billing: DataFrame, cc_spine: DataFrame) -> DataFrame:
    """Full billing history of the run's CC spine.

    Args:
        raw_stg_billing: raw billing table, all CC accounts. Columns: contract_idt (double,
            whole-number account id), billing_date (timestamp), add_info (string carrying
            BS_PMT_CYCLE_DUE=<bucket>).
        cc_spine: model-namespaced spine of the run (cc_60_180 or cc_180_plus). Columns:
            contract_id, cif_id.

    Returns:
        DataFrame at grain (account_id, billing_date): account_id long, billing_date date,
        dlq_bucket int (NULL when add_info carries no bucket), cif_id (from the spine).
    """
    require_columns(
        raw_stg_billing, ["contract_idt", "billing_date", "add_info"], "raw_stg_billing"
    )
    require_columns(cc_spine, ["contract_id", "cif_id"], "cc_spine")
    # -- Step 1: scope to the spine, distinct leftsemi on the native contract id ----
    # Join BEFORE any cast to string (double "939877870.0" vs "939877870" zeroes the join).
    spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()
    raw_bucket = F.regexp_extract(F.col("add_info"), _DPD_BUCKET_REGEX, 1)
    df = raw_stg_billing.join(
        F.broadcast(spine_keys), "contract_idt", "leftsemi"
    ).select(
        # contract_idt is a whole-number double at the raw boundary -- cast to long (never
        # string), same convention as the rest of crx_persona.
        F.col("contract_idt").cast("long").alias("account_id"),
        F.col("billing_date").cast("date").alias("billing_date"),
        # regexp_extract returns "" when there is no match: NULL, not a failing cast
        F.when(raw_bucket != "", raw_bucket.cast("int")).alias("dlq_bucket"),
    )

    # -- Step 2: one row per (account_id, billing_date), deterministic: worst bucket -------
    history = df.groupBy("account_id", "billing_date").agg(
        F.max("dlq_bucket").alias("dlq_bucket")
    )

    # -- Step 3: attach cif_id from the spine, same bridge convention as build_account_cif_map
    account_cif_map = cc_spine.select(
        F.col("contract_id").cast("long").alias("account_id"), "cif_id"
    ).dropDuplicates(["account_id"])
    return history.join(F.broadcast(account_cif_map), "account_id", "left")
