"""T03 — Delinquency-spell table for Credit Cards.

Build function: build_cc_spell_table(raw_stg_billing, cc_spine) -> DataFrame

Output grain: (account_id, spell_id) — one row per delinquency episode.
T0 is the spell anchor for every A4 feature. Every A4 lookback window is
relative to T0, not to the calendar or observation date.

Shared dependency (R18 cleanup, A4 pipeline retirement): this table now carries
only the columns its surviving consumers (cc_a1_ability, cc_a2_locatability,
cc_a3_payment_credibility, cc_departure_signature, cc_payment_trajectory,
cc_utilisation, cc_raw_extract) actually read — account_id, spell_id, t0,
spell_end, t0_censored_flag, prior_spell_end, days_to_dpd30, days_to_dpd60.
The superseded cc_a4_class pipeline and its spine-table consumers are removed;
crx_cc_a4_deterioration derives its own restructure signal directly from
crx_cc_full_history instead of this table's former censored_subtype column.

Population scoping:
- cc_spine (model_id-namespaced) defines the target population for the current
  run (e.g. cc_60_180 or cc_180_plus). Only accounts appearing in cc_spine are
  processed. All their DLQ history rows are retained — not just M1 observations
  — because spell start/end detection requires the full temporal sequence
  including DLQ=0 rows.

Known limitations (by design, not bugs):
- 24-month horizon / censoring: t0_censored_flag = 1 is emitted for spell_id = 1
  on any account whose earliest recorded observation is already delinquent
  (delinquency_bucket >= _CC_DELINQ_MIN, i.e. ≥ 2 on CC) — T0 genuinely fell
  outside the data window, or (R13) the account was opened mid-delinquency as
  part of a restructure. Cure is a return to code < _CC_DELINQ_MIN (≤ 1 on CC).
  Code 1 = 'due but not overdue' is ordinary revolver behaviour and is outside
  spells.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

LOG = logging.getLogger(__name__)

# DPD30 and DPD60 entry thresholds (DLQ = max_ovd_bucket + 1):
# DLQ >= 3 → account has entered 31-60 DPD range (OVD_02 has balance)
# DLQ >= 4 → account has entered 61+ DPD range (M1 entry)
_DPD30_ENTRY_THRESHOLD = 3
_DPD60_ENTRY_THRESHOLD = 4

# CC delinquency threshold: code 1 = "due but not overdue" (normal revolver behaviour).
# Delinquency starts at code 2 (0-30 DPD).  Retail loans use 1 — hence per-unit constant.
_CC_DELINQ_MIN = 2


def build_cc_spell_table(raw_stg_billing: DataFrame, cc_spine: DataFrame) -> DataFrame:
    """Build the delinquency-spell table for CC accounts.

    One row per (account_id, spell_id). A spell is a continuous run of
    monthly observations with delinquency_bucket >= _CC_DELINQ_MIN (code ≥ 2
    on CC: code 1 = 'due but not overdue', delinquency starts at code 2).
    T0 = first such observation in the run. Cure = first observation with
    delinquency_bucket < _CC_DELINQ_MIN (≤ 1 on CC).

    Args:
        raw_stg_billing: Raw billing staging table — full history, all DLQ
            levels (0-9), no date or DLQ filter applied. Required columns:
            contract_idt (Long), billing_date (Date), add_info (string —
            contains BS_PMT_CYCLE_DUE=<N> from which delinquency_bucket is
            extracted via regex).
        cc_spine: Model-namespace spine (produced by the spine pipeline for the
            current model_id). Used to scope raw_stg_billing to the target
            population via leftsemi join. Required column: contract_id (Long).

    Returns:
        DataFrame at grain (account_id, spell_id) with schema:
            account_id          long
            spell_id            int     (1-indexed, per account, no gaps)
            t0                  date    (first DLQ>=DELINQ_MIN observation in the spell)
            spell_end           date    (nullable — first DLQ<DELINQ_MIN after spell, or NULL)
            prior_spell_end     date    (nullable — previous spell's cure date; NULL for spell_id=1)
            t0_censored_flag    int     (1 if T0 is outside the data window)
            days_to_dpd30       int     (nullable — datediff from t0 to first DLQ>=3)
            days_to_dpd60       int     (nullable — datediff from t0 to first DLQ>=4)
    """
    # -- Step 0: scope to target population + extract full DLQ history ---------
    # raw_stg_billing carries all DLQ levels (0-9) and all history — no date or
    # DLQ filter applied. leftsemi join on cc_spine limits the scan to accounts
    # in the current model_id population. Column name difference: billing uses
    # contract_idt (Long), cc_spine uses contract_id (Long).
    _spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()

    df = (
        raw_stg_billing.join(F.broadcast(_spine_keys), "contract_idt", "leftsemi")
        .select(
            F.col("contract_idt").alias("account_id"),
            F.col("billing_date").cast(DateType()).alias("observation_date"),
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
            .cast("int")
            .alias("delinquency_bucket"),
        )
        .distinct()
    )

    # -- Step 2: detect spell starts -----------------------------------------
    w_acct = Window.partitionBy("account_id").orderBy("observation_date")

    df = df.withColumn("_prev_dlq", F.lag("delinquency_bucket").over(w_acct))

    df = df.withColumn(
        "_spell_start",
        F.when(
            (F.col("delinquency_bucket") >= _CC_DELINQ_MIN)
            & ((F.col("_prev_dlq") < _CC_DELINQ_MIN) | F.col("_prev_dlq").isNull()),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )

    # -- Step 3: assign spell_id (cumulative sum of _spell_start) ----------
    w_acct_unbounded = (
        Window.partitionBy("account_id")
        .orderBy("observation_date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
    df = df.withColumn("spell_id", F.sum("_spell_start").over(w_acct_unbounded))

    # -- Step 4: detect censored accounts ----------------------------------
    # An account is censored if its very first observation already has
    # dlq >= _CC_DELINQ_MIN. This means T0 fell outside the data window.
    # Only spell_id = 1 is flagged (the only one whose T0 might be unknown).
    w_first = Window.partitionBy("account_id").orderBy("observation_date")
    censored_accounts = (
        df.withColumn("_rn", F.row_number().over(w_first))
        .filter(F.col("_rn") == 1)
        .filter(F.col("delinquency_bucket") >= _CC_DELINQ_MIN)
        .select("account_id")
        .distinct()
        .withColumn("_is_censored", F.lit(1))
    )

    # -- Step 5: aggregate spell-level metrics (in-spell rows only) --------
    in_spell = df.filter(F.col("delinquency_bucket") >= _CC_DELINQ_MIN)

    spell_agg = in_spell.groupBy("account_id", "spell_id").agg(
        F.min("observation_date").alias("t0"),
        F.max("observation_date").alias("_spell_max_obs"),
        F.min(
            F.when(
                F.col("delinquency_bucket") >= _DPD30_ENTRY_THRESHOLD,
                F.col("observation_date"),
            )
        ).alias("_date_dlq3"),
        F.min(
            F.when(
                F.col("delinquency_bucket") >= _DPD60_ENTRY_THRESHOLD,
                F.col("observation_date"),
            )
        ).alias("_date_dlq4"),
    )

    # -- Step 6: roll speed metrics ------------------------------------------
    spell_agg = spell_agg.withColumn(
        "days_to_dpd30",
        F.datediff(F.col("_date_dlq3"), F.col("t0")),
    ).withColumn(
        "days_to_dpd60",
        F.datediff(F.col("_date_dlq4"), F.col("t0")),
    )

    # -- Step 7: cure date detection (self-join on account_id) ------------
    # For each spell, find the first DLQ<_CC_DELINQ_MIN observation strictly after
    # the spell's last DLQ>=_CC_DELINQ_MIN snapshot (_spell_max_obs).
    cure_candidates = df.filter(F.col("delinquency_bucket") < _CC_DELINQ_MIN).select(
        F.col("account_id"),
        F.col("observation_date").alias("_cure_obs"),
    )

    cure_dates = (
        spell_agg.select("account_id", "spell_id", "_spell_max_obs")
        .join(cure_candidates, on="account_id", how="left")
        .filter(F.col("_cure_obs") > F.col("_spell_max_obs"))
        .groupBy("account_id", "spell_id")
        .agg(F.min("_cure_obs").alias("_cure_date"))
    )

    spell_agg = spell_agg.join(cure_dates, on=["account_id", "spell_id"], how="left")

    # spell_end: cure_date if known; NULL for active (no cure yet)
    spell_agg = spell_agg.withColumn(
        "spell_end",
        F.when(F.col("_cure_date").isNotNull(), F.col("_cure_date")).otherwise(
            F.lit(None).cast("date")
        ),
    )

    # prior_spell_end: previous spell's cure date — NULL for spell_id=1.
    # T04b uses it to truncate W_pre at the prior spell boundary (§3.0b).
    _w_prev_spell = Window.partitionBy("account_id").orderBy("spell_id")
    spell_agg = spell_agg.withColumn(
        "prior_spell_end", F.lag("spell_end").over(_w_prev_spell)
    )

    # -- Step 8: t0_censored_flag --------------------------------------------
    spell_agg = spell_agg.join(
        censored_accounts, on="account_id", how="left"
    ).withColumn(
        "t0_censored_flag",
        F.when(
            (F.col("spell_id") == 1) & (F.col("_is_censored") == 1),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )

    # -- Step 9: final select in schema order --------------------------------
    result = spell_agg.select(
        F.col("account_id").cast("long"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("spell_end").cast("date"),
        F.col("prior_spell_end").cast("date"),
        F.col("t0_censored_flag").cast("int"),
        F.col("days_to_dpd30").cast("int"),
        F.col("days_to_dpd60").cast("int"),
    )

    _log_spell_stats(result)
    return result


def _log_spell_stats(result: DataFrame) -> None:
    """Log basic spell table statistics."""
    try:
        total_spells = result.count()
        LOG.info(
            "CC spell table built: %d spells",  # total_accounts omitted: Filtering_Sensitive_Logs
            total_spells,
        )
    except Exception as e:  # pylint: disable=broad-except
        LOG.warning("Could not compute spell stats: %s (lazy eval context)", str(e))
