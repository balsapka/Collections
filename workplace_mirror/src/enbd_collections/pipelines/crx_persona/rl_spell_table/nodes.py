"""RL-B2 — T0 anchor table for Retail Loan persona pipeline.

Build function: build_rl_spell_table(crx_rl_full_history, rl_spine) -> DataFrame

Output grain: one row per (account_id, spell_id).

A spell is a contiguous run of months where dlq_bucket >= 1.  Episode
boundaries are detected via a cumulative-sum of spell-start flags ordered by
month_end_date per account (mirrors cc_spell/nodes.py, adapted for RL threshold
dlq_bucket >= 1 vs CC dlq_bucket >= 2).

T0 = min(month_end_date) where dlq_bucket >= 1 within the spell.
spell_end = first clean (dlq_bucket == 0) month_end_date strictly after the
last delinquent row of the spell; NULL for the active spell.

t0_censored_flag = 1 for spell_id = 1 when the account's very first history row
is already delinquent (T0 predates the data window).

For the ~0% of accounts with no DLQ >= 1 in history (censored with no episodes),
a single stub row is synthesised with spell_id = 1, t0 = min(rl_spine
.observation_date), t0_censored_flag = 1.

Key behavioural columns derived per spell:
- restructure_blind_spot_flag: 1 if account was ever restructured in history (R13)
- pre_t0_months: count of history rows with month_end_date < t0
- prior_spell_cnt_12m: distinct prior DLQ-1+ episodes in 12m before T0
- w_pre_clean_m: consecutive DLQ-0 months immediately preceding T0

Inputs: crx_rl_full_history (RL-B1 output), rl_spine (model-namespaced spine, requires cif_id)
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_rl_spell_table(  # pylint: disable=too-many-locals
    crx_rl_full_history: DataFrame,
    rl_spine: DataFrame,
) -> DataFrame:
    """Build the T0 anchor table for RL accounts.

    Args:
        crx_rl_full_history: Full monthly history for RL spine accounts.
            Required columns: account_id (string), month_end_date (date),
            dlq_bucket (int), restructure_flag (int).
        rl_spine: Model-namespaced spine. Required columns:
            account_id (string), observation_date (date), cif_id (string).

    Returns:
        DataFrame at grain (account_id, spell_id) with schema:
            account_id                  string
            cif_id                      string
            spell_id                    int     (1-indexed per account)
            t0                          date    (start of delinquency episode)
            t0_censored_flag            int     (1 if T0 before data window)
            restructure_blind_spot_flag int     (1 if ever restructured — R13)
            pre_t0_months               int     (months of history before T0)
            prior_spell_cnt_12m         int     (prior DLQ-1+ episodes in 12m before T0)
            w_pre_clean_m               int     (consecutive DLQ-0 months before T0)
            spell_end                   date    (NULL for active spell)
            computed_at                 timestamp
    """
    hist = crx_rl_full_history

    # -- Step 1: spine_anchor — first spine observation and cif_id per account --
    spine_anchor = (
        rl_spine.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("cif_id").cast("string"),
        )
        .groupBy("account_id")
        .agg(
            F.min("observation_date").alias("anchor_date"),
            F.first("cif_id").alias("cif_id"),
        )
    )

    # -- Step 2: scope history to spine accounts only -------------------------
    hist_scoped = hist.join(
        spine_anchor.select("account_id"), on="account_id", how="inner"
    )

    # -- Step 3: detect spell starts via lag and assign spell_id (cumsum) -----
    # Spell starts when dlq_bucket >= 1 and previous month was dlq_bucket == 0
    # (or no previous row). coalesce(lag, 0) treats first row as "clean before".
    w_acct = Window.partitionBy("account_id").orderBy("month_end_date")
    w_acct_unbounded = (
        Window.partitionBy("account_id")
        .orderBy("month_end_date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    labeled = (
        hist_scoped.withColumn(
            "_prev_dlq",
            F.coalesce(F.lag("dlq_bucket").over(w_acct), F.lit(0)),
        )
        .withColumn(
            "_spell_start",
            F.when(
                (F.col("dlq_bucket") >= 1) & (F.col("_prev_dlq") == 0),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "spell_id",
            F.sum("_spell_start").over(w_acct_unbounded).cast("int"),
        )
    )

    # -- Step 4: censored detection — first history row already delinquent ----
    # Only spell_id = 1 can be censored (T0 before data window).
    censored_accts = (
        labeled.withColumn("_rn", F.row_number().over(w_acct))
        .filter((F.col("_rn") == 1) & (F.col("dlq_bucket") >= 1))
        .select("account_id")
        .distinct()
    )

    # -- Step 5: per-spell aggregation (delinquent rows only) -----------------
    in_spell = labeled.filter(F.col("dlq_bucket") >= 1)

    spell_agg = in_spell.groupBy("account_id", "spell_id").agg(
        F.min("month_end_date").alias("t0"),
        F.max("month_end_date").alias("_spell_max_obs"),
    )

    # -- Step 6: spell_end detection — first clean month after last DLQ row ---
    clean_rows = hist_scoped.filter(F.col("dlq_bucket") == 0).select(
        F.col("account_id"),
        F.col("month_end_date").alias("_clean_date"),
    )

    cure_dates = (
        spell_agg.select("account_id", "spell_id", "_spell_max_obs")
        .join(clean_rows, on="account_id", how="left")
        .filter(F.col("_clean_date") > F.col("_spell_max_obs"))
        .groupBy("account_id", "spell_id")
        .agg(F.min("_clean_date").alias("spell_end"))
    )

    spell_agg = spell_agg.join(cure_dates, on=["account_id", "spell_id"], how="left")

    # -- Step 7: t0_censored_flag and T0 fallback ------------------------------
    spell_agg = (
        spell_agg.join(
            censored_accts.withColumn("_is_censored", F.lit(1)),
            on="account_id",
            how="left",
        )
        .withColumn(
            "t0_censored_flag",
            F.when(
                (F.col("spell_id") == 1) & (F.col("_is_censored") == 1),
                F.lit(1),
            )
            .otherwise(F.lit(0))
            .cast("int"),
        )
        .drop("_is_censored")
    )

    # -- Step 8: stub rows for ~0% accounts with no DLQ in history -----------
    # These have no rows in spell_agg; synthesise spell_id=1, t0=anchor_date.
    no_spell_accts = spine_anchor.select("account_id", "anchor_date").join(
        spell_agg.select("account_id").distinct(),
        on="account_id",
        how="left_anti",
    )

    stubs = (
        no_spell_accts.withColumn("spell_id", F.lit(1).cast("int"))
        .withColumnRenamed("anchor_date", "t0")
        .withColumn("_spell_max_obs", F.lit(None).cast("date"))
        .withColumn("spell_end", F.lit(None).cast("date"))
        .withColumn("t0_censored_flag", F.lit(1).cast("int"))
    )

    spell_agg = spell_agg.unionByName(stubs, allowMissingColumns=True)

    # -- Step 9: join cif_id and restructure_blind_spot_flag ------------------
    restructure = hist_scoped.groupBy("account_id").agg(
        F.max("restructure_flag").cast("int").alias("restructure_blind_spot_flag")
    )

    spell_agg = (
        spell_agg.join(
            spine_anchor.select("account_id", "cif_id"), on="account_id", how="left"
        )
        .join(restructure, on="account_id", how="left")
        .withColumn(
            "restructure_blind_spot_flag",
            F.coalesce(F.col("restructure_blind_spot_flag"), F.lit(0)).cast("int"),
        )
    )

    # -- Step 10: per-spell ancillary metrics ---------------------------------
    # pre_t0_months, prior_spell_cnt_12m, w_pre_clean_m are per (account_id, spell_id).
    spell_t0s = spell_agg.select("account_id", "spell_id", "t0")

    pre_t0_cnt = _compute_pre_t0_months(hist_scoped, spell_t0s)
    prior_spells = _compute_prior_spells(labeled, spell_t0s)
    w_clean_tbl = _compute_w_clean_m(hist_scoped, spell_t0s)

    # -- Step 11: assemble and finalize ----------------------------------------
    result = (
        spell_agg.select(
            "account_id",
            "cif_id",
            "spell_id",
            "t0",
            "t0_censored_flag",
            "restructure_blind_spot_flag",
            "spell_end",
        )
        .join(pre_t0_cnt, on=["account_id", "spell_id"], how="left")
        .join(prior_spells, on=["account_id", "spell_id"], how="left")
        .join(w_clean_tbl, on=["account_id", "spell_id"], how="left")
        .withColumn("computed_at", F.current_timestamp())
        .withColumn(
            "pre_t0_months", F.coalesce(F.col("pre_t0_months"), F.lit(0)).cast("int")
        )
        .withColumn(
            "prior_spell_cnt_12m",
            F.coalesce(F.col("prior_spell_cnt_12m"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "w_pre_clean_m",
            F.coalesce(F.col("w_pre_clean_m"), F.lit(0)).cast("int"),
        )
        .select(
            F.col("account_id").cast("string"),
            F.col("cif_id").cast("string"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("t0_censored_flag"),
            F.col("restructure_blind_spot_flag"),
            F.col("pre_t0_months"),
            F.col("prior_spell_cnt_12m"),
            F.col("w_pre_clean_m"),
            F.col("spell_end"),
            F.col("computed_at"),
        )
    )

    # -- Step 12: log stats --------------------------------------------------------
    _log_stats(result)
    return result


def _compute_pre_t0_months(
    hist_scoped: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count history rows with month_end_date < T0 per (account_id, spell_id)."""
    return (
        spell_t0s.join(
            hist_scoped.select("account_id", "month_end_date"),
            on="account_id",
            how="left",
        )
        .filter(F.col("month_end_date") < F.col("t0"))
        .groupBy("account_id", "spell_id")
        .agg(F.count("*").cast("int").alias("pre_t0_months"))
    )


def _compute_prior_spells(
    labeled: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count distinct prior DLQ-1+ episodes in the 12m window before each spell's T0."""
    # labeled carries spell_id (the episode each row belongs to).
    # For target spell N, count distinct prior spell_ids where rows fall in [T0-12m, T0).
    hist_dlq = labeled.filter(F.col("dlq_bucket") >= 1).select(
        F.col("account_id"),
        F.col("month_end_date"),
        F.col("spell_id").alias("_hist_spell_id"),
    )

    return (
        spell_t0s.withColumnRenamed("spell_id", "_target_spell_id")
        .join(hist_dlq, on="account_id", how="left")
        .filter(
            (F.col("month_end_date") < F.col("t0"))
            & (F.col("month_end_date") >= F.add_months(F.col("t0"), -12))
            & (F.col("_hist_spell_id") != F.col("_target_spell_id"))
        )
        .groupBy("account_id", "_target_spell_id")
        .agg(F.countDistinct("_hist_spell_id").cast("int").alias("prior_spell_cnt_12m"))
        .withColumnRenamed("_target_spell_id", "spell_id")
    )


def _compute_w_clean_m(
    hist_scoped: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count consecutive DLQ-0 months immediately before each spell's T0."""
    pre_t0 = spell_t0s.join(
        hist_scoped.select("account_id", "month_end_date", "dlq_bucket"),
        on="account_id",
        how="left",
    ).filter(F.col("month_end_date") < F.col("t0"))

    pre_t0_cnt = pre_t0.groupBy("account_id", "spell_id").agg(
        F.count("*").cast("int").alias("_pre_t0_cnt")
    )

    w_desc = Window.partitionBy("account_id", "spell_id").orderBy(
        F.desc("month_end_date")
    )

    first_nc = (
        pre_t0.withColumn("_rn_desc", F.row_number().over(w_desc))
        .filter(F.col("dlq_bucket") > 0)
        .groupBy("account_id", "spell_id")
        .agg(F.min("_rn_desc").alias("_first_nc_rn"))
    )

    return (
        pre_t0_cnt.join(first_nc, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "w_pre_clean_m",
            F.when(F.col("_first_nc_rn").isNull(), F.col("_pre_t0_cnt")).otherwise(
                (F.col("_first_nc_rn") - 1).cast("int")
            ),
        )
        .select("account_id", "spell_id", "w_pre_clean_m")
    )


def _log_stats(df: DataFrame) -> None:
    """Log spell count, censored%, and restructure_blind_spot%."""
    try:
        row_count = df.count()
        acct_count = df.select("account_id").distinct().count()
        agg_row = df.agg(
            F.sum("t0_censored_flag").alias("censored_cnt"),
            F.sum("restructure_blind_spot_flag").alias("restructure_cnt"),
        ).collect()[0]
        active_cnt = df.filter(F.col("spell_end").isNull()).count()
        censored_pct = (
            agg_row["censored_cnt"] / row_count * 100 if row_count > 0 else 0.0
        )
        restructure_pct = (
            agg_row["restructure_cnt"] / acct_count * 100 if acct_count > 0 else 0.0
        )
        LOG.info(
            "crx_rl_spell_table built: %d spells across %d accounts | "
            "active (spell_end NULL)=%d | censored=%.2f%% | restructure_blind_spot=%.2f%%",
            row_count,
            acct_count,
            active_cnt,
            censored_pct,
            restructure_pct,
        )
    except Exception as e:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute rl_spell_table stats: %s (lazy eval context)", str(e)
        )
