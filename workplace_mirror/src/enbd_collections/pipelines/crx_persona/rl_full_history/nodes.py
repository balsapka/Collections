"""RL full monthly history: ``int_loan_master`` scoped to the run's ``rl_spine``.

Output ``crx_rl_full_history`` at grain (account_id, month_end_date). Run:
``kedro run --pipeline=crx_rl_full_history`` (needs the spine of the model_id).

* the spine key is cast to string safely: a double/decimal account_id goes through
  long first (double -> string gives "1.23456789E8" and silently empties the left-semi
  join);
* the spine keys are broadcast: they are tiny, and without the hint Spark may shuffle
  the whole int_loan_master (all RL accounts x all months);
* the stats log is opt-in (params dpd_journey.log_stats): it runs extra jobs over the
  whole output.
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns, string_key

LOG = logging.getLogger(__name__)


def build_rl_full_history(
    rl_spine: DataFrame, int_loan_master: DataFrame, crx_persona: dict
) -> DataFrame:
    """Full monthly history of the run's RL spine.

    Args:
        rl_spine: model-namespaced RL spine (~31k accounts). Column: account_id.
        int_loan_master: monthly snapshots for all RL accounts. Columns: account_id (string),
            observation_date (date), dpd_bucket (int: 0 = 0 DPD, 1 = 1-30, ..., 7 = 180+),
            emi_coverage_ratio, outstanding_balance, is_restructured, loan_type.
        crx_persona: params dict (only dpd_journey.log_stats is read).

    Returns:
        DataFrame at grain (account_id, month_end_date): account_id string, month_end_date
        date, dlq_bucket int, emi_coverage_ratio double, outstanding_balance double,
        restructure_flag int, loan_type string, computed_at timestamp.
    """
    require_columns(rl_spine, ["account_id"], "rl_spine")
    require_columns(
        int_loan_master,
        [
            "account_id",
            "cif_id",
            "observation_date",
            "dpd_bucket",
            "emi_coverage_ratio",
            "outstanding_balance",
            "is_restructured",
            "loan_type",
        ],
        "int_loan_master",
    )
    # -- Step 1: scope to the spine (broadcast: the spine is model-sized) ----------
    spine_keys = rl_spine.select(string_key(rl_spine).alias("account_id")).distinct()
    df = int_loan_master.join(F.broadcast(spine_keys), on="account_id", how="leftsemi")

    # -- Step 2: select + alias + cast to the output schema ----------------------------
    result = df.select(
        F.col("cif_id").cast("string"),
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date").alias("month_end_date"),
        F.col("dpd_bucket").cast("int").alias("dlq_bucket"),
        F.col("emi_coverage_ratio").cast("double"),
        F.col("outstanding_balance").cast("double"),
        F.col("is_restructured").cast("int").alias("restructure_flag"),
        F.col("loan_type").cast("string"),
        F.current_timestamp().alias("computed_at"),
    )

    # -- Step 3 (opt-in): one aggregate job — rows, date range, null rates, spine match ---
    if (crx_persona.get("dpd_journey") or {}).get("log_stats"):
        result = result.persist()
        _log_stats(result, spine_keys)
    return result


def _log_stats(df: DataFrame, spine_keys: DataFrame) -> None:
    r = (
        df.agg(
            F.count("*").alias("rows"),
            F.countDistinct("account_id").alias("accounts"),
            F.min("month_end_date").alias("first_month"),
            F.max("month_end_date").alias("last_month"),
            *[
                F.avg(F.col(c).isNull().cast("double")).alias(f"null_{c}")
                for c in ("dlq_bucket", "month_end_date", "restructure_flag")
            ],
        )
        .first()
        .asDict()
    )
    r["spine_accounts"] = spine_keys.count()
    LOG.info(
        "build_rl_full_history: %s (spine accounts found: %s of %s)",
        r,
        r["accounts"],
        r["spine_accounts"],
    )
