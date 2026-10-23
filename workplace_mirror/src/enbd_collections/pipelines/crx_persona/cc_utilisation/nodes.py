"""T05 — CC Utilisation, Spend & Liquidity Features.

# pylint: disable=too-many-locals, too-many-statements
# Rationale: two-pass feature builder (Pass A: monthly utilisation from crx_cc_limits;
# Pass B: transaction-level spend/CA features). Each pass is self-contained.
# Splitting further would obscure the T0-anchored window logic shared across passes.

Build function: build_cc_utilisation_features(crx_cc_limits, crx_cc_transactions,
                                              crx_cc_spell_table,
                                              crx_cc_payment_trajectory)

Output grain: (account_id, spell_id) — one row per delinquency spell.
All lookback windows reuse w_pre_start / w_pre_clean_m from T04b output.

Window design (same as T04b)::

    M0      = trunc(t0, 'month')              — onset month (excluded)
    W_pre   = [w_pre_start, M0)               — clean pre-delinquency window (≤12 months)
    H2      = [M0-3m, M0)       → m_from_m0 1..3  — recent behaviour
    H1      = [w_pre_start, M0-3m) → m_from_m0 ≥ 4  — baseline behaviour

T0 leakage guard: all joins use strict ``obs_date < M0``
(M0 = trunc(t0, 'month')). Onset month excluded; m_from_m0 = 0 never appears.

Truncation columns are read directly from crx_cc_payment_trajectory (T04b output).
No re-derivation of retention floor or account-open-date cuts.

Null rules:
    util_slope       : NULL if < 4 non-null util months in W_pre
    util_accel       : NULL if < 3 non-null util months in W_pre
    util_t0          : NULL if no util snapshot at m_from_m0 == 1
    H2 util features : NULL if w_pre_clean_m < 3 (no H2 months)
    txn_cnt_slope    : NULL if < 4 months with ≥1 transaction
    H2 txn features  : NULL if w_pre_clean_m < 3

Cash-advance detection (R17: replicates feat_transaction.py lines 301-309):
    is_cash_adv = upper(coalesce(txn_description,'')) RLIKE 'CASH ADVANCE|CASH DISBURSEMENT'
    Source column: txn_description (CreditCardTransaction schema).

util_ratio computation:
    util_ratio = (credit_limit - available_limit) / credit_limit * 100
    NULL when credit_limit <= 0 or either column is NULL.
    Source: CreditCardLimit schema (prm_limit catalog key).

Amount convention:
    txn_amount_aed is negative for outflows (debits). Use F.abs() for spend sums.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_cc_utilisation_features(
    crx_cc_limits: DataFrame,
    crx_cc_transactions: DataFrame,
    crx_cc_spell_table: DataFrame,
    crx_cc_payment_trajectory: DataFrame,
) -> DataFrame:
    """Build CC utilisation, spend & liquidity features anchored to T0 per spell.

    Args:
        crx_cc_limits:              T04c intermediate — T0-scoped CC limit snapshots.
                                    Replaces prm_limit.
                                    Required cols: contract_id, observation_date,
                                    credit_limit, available_limit.
        crx_cc_transactions:        T04c intermediate — T0-scoped CC transactions.
                                    Replaces prm_transaction.
                                    Required cols: contract_id, observation_date,
                                    direction, txn_amount_aed, txn_description.
        crx_cc_spell_table:         T03b output at (account_id, spell_id) grain.
        crx_cc_payment_trajectory:  T04b output — carries w_pre truncation columns.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id, spell_id, t0,
            util_mean_h1, util_mean_h2, util_t0,
            util_slope, util_accel,
            cash_adv_ramp, cash_adv_amt_share_h2,
            spend_taper_ratio, spend_cliff_flag,
            spend_active_days_share_h2, txn_cnt_slope,
            w_pre_start, w_pre_clean_m,
            w_pre_contaminated_flag, w_pre_truncation_reason,
            computed_at
    """
    # ── Step 0: spell base + truncation columns from T04b ──────────────────────
    # Excludes both censored subtypes (data_depth + restructured_entry) — see
    # cc_payment_trajectory/nodes.py Step 0 comment for rationale.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id", "spell_id", "t0"
    )

    trunc = crx_cc_payment_trajectory.select(
        "account_id",
        "spell_id",
        "w_pre_start",
        "w_pre_clean_m",
        "w_pre_contaminated_flag",
        "w_pre_truncation_reason",
    )

    # Inner join: any spell absent from T04b output is excluded (should not happen
    # for non-censored spells; inner join surfaces unexpected mismatches via row count).
    spell_w = spell.join(trunc, on=["account_id", "spell_id"], how="inner")

    # ── Pass A: monthly utilisation (from crx_cc_limits) ───────────────────────
    pass_a = _build_pass_a(crx_cc_limits, spell_w)

    # ── Pass B: spend & cash-advance features (from crx_cc_transactions) ──────
    pass_b1, pass_b2 = _build_pass_b(crx_cc_transactions, spell_w)

    # ── Combine: left-join passes onto spell base ──────────────────────────────
    result = (
        spell_w.join(pass_a, on=["account_id", "spell_id"], how="left")
        .join(pass_b1, on=["account_id", "spell_id"], how="left")
        .join(pass_b2, on=["account_id", "spell_id"], how="left")
        .withColumn("computed_at", F.current_timestamp())
    )

    _log_utilisation_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("util_mean_h1").cast("double"),
        F.col("util_mean_h2").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("util_slope").cast("double"),
        F.col("util_accel").cast("double"),
        F.col("cash_adv_ramp").cast("double"),
        F.col("cash_adv_amt_share_h2").cast("double"),
        F.col("spend_taper_ratio").cast("double"),
        F.col("spend_cliff_flag").cast("int"),
        F.col("spend_active_days_share_h2").cast("double"),
        F.col("txn_cnt_slope").cast("double"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("computed_at"),
    )


# ── Private: Pass A ────────────────────────────────────────────────────────────


def _build_pass_a(prm_limit: DataFrame, spell: DataFrame) -> DataFrame:
    """Monthly utilisation features from prm_limit snapshots.

    spell carries w_pre_start and w_pre_clean_m from T04b output.
    Returns one row per (account_id, spell_id).
    Spells with no limit snapshots in W_pre have NULL for all Pass A features.

    Features::

        util_mean_h1    : mean util_ratio over H1 months (m_from_m0 >= 4)
        util_mean_h2    : mean util_ratio over H2 months (m_from_m0 1..3)
        util_t0         : util_ratio at m_from_m0 == 1 (month immediately before T0)
        util_slope      : OLS slope of util_ratio vs m_from_m0 over W_pre
                          (NULL if < 4 non-null months)
        util_accel      : mean second-difference of util_ratio chronologically
                          (NULL if < 3 non-null months)
    """
    scope = spell.select("account_id").distinct()

    limit = (
        prm_limit.select(
            F.col("contract_id"),
            F.col("observation_date").alias("obs_date"),
            F.col("credit_limit"),
            F.col("available_limit"),
        )
        .join(
            F.broadcast(scope),
            prm_limit["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .withColumn(
            "util_ratio",
            F.when(
                F.col("credit_limit").isNotNull() & (F.col("credit_limit") > 0),
                (F.col("credit_limit") - F.col("available_limit"))
                / F.col("credit_limit")
                * 100.0,
            ).otherwise(F.lit(None).cast("double")),
        )
        .select("contract_id", "obs_date", "util_ratio")
    )

    # Join to spell and filter to W_pre window
    util_w = (
        limit.join(
            spell,
            on=limit["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("obs_date"),
            F.col("util_ratio"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        # One snapshot per month — take the trunc(obs_date,'month') month
        # W_pre: [w_pre_start, M0); M0 = trunc(t0,'month') excluded
        .filter(
            (F.trunc(F.col("obs_date"), "month") >= F.col("w_pre_start"))
            & (F.trunc(F.col("obs_date"), "month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("obs_date"), "month"),
                )
            ).cast("int"),
        )
        # One record per (account_id, spell_id, m_from_m0) — take max util if duplicates
        .groupBy("account_id", "spell_id", "m_from_m0")
        .agg(F.first("util_ratio").alias("util_ratio"))
    )

    # ── Rank rows for util_accel boundary accumulators ─────────────────────────
    # rank_oldest: 1 = oldest month (highest m_from_m0, farthest from T0)
    # rank_newest: 1 = newest month (lowest m_from_m0, closest to T0)
    w_oldest = Window.partitionBy("account_id", "spell_id").orderBy(F.desc("m_from_m0"))
    w_newest = Window.partitionBy("account_id", "spell_id").orderBy("m_from_m0")

    util_w = (
        util_w.filter(F.col("util_ratio").isNotNull())
        .withColumn("_rank_oldest", F.row_number().over(w_oldest))
        .withColumn("_rank_newest", F.row_number().over(w_newest))
    )

    # ── Spell-level aggregation ────────────────────────────────────────────────
    agg = util_w.groupBy("account_id", "spell_id").agg(
        # H1 / H2 means
        F.avg(F.when(F.col("m_from_m0") >= 4, F.col("util_ratio"))).alias(
            "util_mean_h1"
        ),
        F.avg(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("util_ratio"),
            )
        ).alias("util_mean_h2"),
        # util_t0: value at m_from_m0 == 1 (month immediately before T0)
        F.first(
            F.when(F.col("m_from_m0") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("util_t0"),
        # Non-null count for null guards
        F.count(F.lit(1)).alias("_n_util"),
        # OLS accumulators for util_slope (x = m_from_m0)
        F.sum(F.col("m_from_m0").cast("double")).alias("_sx"),
        F.sum(F.col("util_ratio")).alias("_sy"),
        F.sum(F.col("m_from_m0").cast("double") * F.col("util_ratio")).alias("_sxy"),
        F.sum(
            F.col("m_from_m0").cast("double") * F.col("m_from_m0").cast("double")
        ).alias("_sx2"),
        # util_accel boundary accumulators (telescoping second-difference)
        # u_first = util at oldest rank (highest m_from_m0)
        # u_second = util at second oldest
        # u_penultimate = util at second newest
        # u_last = util at newest (lowest m_from_m0)
        F.first(
            F.when(F.col("_rank_oldest") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_first"),
        F.first(
            F.when(F.col("_rank_oldest") == 2, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_second"),
        F.first(
            F.when(F.col("_rank_newest") == 2, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_penultimate"),
        F.first(
            F.when(F.col("_rank_newest") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_last"),
    )

    # ── Derive slope + accel with null guards ──────────────────────────────────
    _denom = F.col("_n_util").cast("double") * F.col("_sx2") - F.col("_sx") * F.col(
        "_sx"
    )

    agg = agg.withColumn(
        "util_slope",
        F.when(
            (F.col("_n_util") >= 4) & (_denom != 0.0),
            (
                F.col("_n_util").cast("double") * F.col("_sxy")
                - F.col("_sx") * F.col("_sy")
            )
            / _denom,
        ).otherwise(F.lit(None).cast("double")),
    ).withColumn(
        "util_accel",
        # mean second-difference = (u_last - u_penultimate - u_second + u_first) / (n - 2)
        F.when(
            (F.col("_n_util") >= 3)
            & F.col("_u_first").isNotNull()
            & F.col("_u_second").isNotNull()
            & F.col("_u_penultimate").isNotNull()
            & F.col("_u_last").isNotNull(),
            (
                F.col("_u_last")
                - F.col("_u_penultimate")
                - F.col("_u_second")
                + F.col("_u_first")
            )
            / (F.col("_n_util").cast("double") - 2.0),
        ).otherwise(F.lit(None).cast("double")),
    )

    return agg.select(
        "account_id",
        "spell_id",
        "util_mean_h1",
        "util_mean_h2",
        "util_t0",
        "util_slope",
        "util_accel",
    )


# ── Private: Pass B ────────────────────────────────────────────────────────────


def _build_pass_b(
    prm_transaction: DataFrame,
    spell: DataFrame,
) -> tuple:
    """Spend and cash-advance features from outflow transactions.

    Returns two DataFrames:
        pass_b1 : (account_id, spell_id) with spend_active_days_share_h2
        pass_b2 : (account_id, spell_id) with cash_adv_ramp, cash_adv_amt_share_h2,
                  spend_taper_ratio, spend_cliff_flag, txn_cnt_slope

    spell carries w_pre_start and w_pre_clean_m from T04b.

    Cash-advance detection (replicates feat_transaction.py lines 301-309)::

        is_cash_adv = upper(coalesce(txn_description,'')) RLIKE 'CASH ADVANCE|CASH DISBURSEMENT'

    Amount convention: txn_amount_aed is negative for outflows (debits). F.abs() used
    for spend sums to yield positive AED amounts.
    """
    scope = spell.select("account_id").distinct()

    # Outflows only (direction == -1)
    txn_out = (
        prm_transaction.filter(F.col("direction") == -1)
        .select(
            F.col("contract_id"),
            F.col("observation_date").alias("txn_date"),
            F.abs(F.col("txn_amount_aed")).alias("txn_amount_aed"),
            F.col("txn_description"),
        )
        .join(
            F.broadcast(scope),
            prm_transaction["contract_id"] == scope["account_id"],
            "leftsemi",
        )
    )

    # Cash-advance flag (replicates feat_transaction.py logic)
    is_cash_adv = F.upper(F.coalesce(F.col("txn_description"), F.lit(""))).rlike(
        "CASH ADVANCE|CASH DISBURSEMENT"
    )

    txn_out = txn_out.withColumn(
        "is_cash_adv", F.when(is_cash_adv, F.lit(1)).otherwise(0)
    )

    # Join spell and filter to W_pre window
    txn_w = (
        txn_out.join(
            spell,
            on=txn_out["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("is_cash_adv"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
    )

    # ── Sub-pass B1: active days share in H2 (transaction-level groupBy) ───────
    # calendar_days_h2 = number of days in the 3-month H2 window [M0-3m, M0)
    # = datediff(trunc(t0,'month'), add_months(trunc(t0,'month'), -3))
    pass_b1 = (
        txn_w.groupBy("account_id", "spell_id", "t0", "w_pre_clean_m")
        .agg(
            F.countDistinct(
                F.when(F.col("m_from_m0") <= 3, F.to_date(F.col("txn_date")))
            ).alias("_active_days_h2")
        )
        .withColumn(
            "_calendar_days_h2",
            F.datediff(
                F.trunc(F.col("t0"), "month"),
                F.add_months(F.trunc(F.col("t0"), "month"), -3),
            ).cast("double"),
        )
        .withColumn(
            "spend_active_days_share_h2",
            F.when(
                (F.col("w_pre_clean_m") >= 3) & (F.col("_calendar_days_h2") > 0),
                F.col("_active_days_h2").cast("double") / F.col("_calendar_days_h2"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .select("account_id", "spell_id", "spend_active_days_share_h2")
    )

    # ── Sub-pass B2: monthly aggregate → spell aggregate ───────────────────────
    monthly = txn_w.groupBy("account_id", "spell_id", "m_from_m0").agg(
        F.sum("txn_amount_aed").alias("spend_m"),
        F.sum(F.when(F.col("is_cash_adv") == 1, F.lit(1)).otherwise(0)).alias(
            "ca_count_m"
        ),
        F.sum(F.when(F.col("is_cash_adv") == 1, F.col("txn_amount_aed"))).alias(
            "ca_amt_m"
        ),
        F.count("*").alias("txn_count_m"),
    )

    m = F.col("m_from_m0")

    feats_b2 = monthly.groupBy("account_id", "spell_id").agg(
        # H1/H2 spend means for taper ratio
        F.avg(F.when(m <= 3, F.col("spend_m"))).alias("_spend_h2_avg"),
        F.avg(F.when(m >= 4, F.col("spend_m"))).alias("_spend_h1_avg"),
        # M0-1 and M0-2 spend for cliff flag
        F.sum(F.when(m == 1, F.col("spend_m")).otherwise(0)).alias("_spend_m1"),
        F.sum(F.when(m == 2, F.col("spend_m")).otherwise(0)).alias("_spend_m2"),
        # Cash-advance ramp: (sum CA count H2 + 1) / (avg CA count H1 + 1)
        F.sum(F.when(m <= 3, F.col("ca_count_m")).otherwise(0)).alias("_ca_cnt_h2"),
        F.avg(F.when(m >= 4, F.col("ca_count_m"))).alias("_ca_cnt_h1_avg"),
        # Cash-advance amount share in H2
        F.sum(F.when(m <= 3, F.col("ca_amt_m")).otherwise(0)).alias("_ca_amt_h2"),
        F.sum(F.when(m <= 3, F.col("spend_m")).otherwise(0)).alias("_spend_h2_sum"),
        # OLS accumulators for txn_cnt_slope (x = -m_from_m0 → positive = increasing toward T0)
        F.count("*").alias("_ols_n"),
        F.sum((-m).cast("double")).alias("_ols_sx"),
        F.sum(F.pow(-m, 2)).alias("_ols_sx2"),
        F.sum(F.col("txn_count_m").cast("double")).alias("_ols_sy"),
        F.sum((-m).cast("double") * F.col("txn_count_m").cast("double")).alias(
            "_ols_sxy"
        ),
    )

    # ── Post-aggregate derived features ────────────────────────────────────────
    _ols_denom = F.col("_ols_n").cast("double") * F.col("_ols_sx2") - F.col(
        "_ols_sx"
    ) * F.col("_ols_sx")

    feats_b2 = (
        feats_b2
        # spend_taper_ratio: avg(H2 spend) / avg(H1 spend) — NULL if either is NULL
        .withColumn(
            "spend_taper_ratio",
            F.when(
                F.col("_spend_h2_avg").isNotNull()
                & F.col("_spend_h1_avg").isNotNull()
                & (F.col("_spend_h1_avg") > 0),
                F.col("_spend_h2_avg") / F.col("_spend_h1_avg"),
            ).otherwise(F.lit(None).cast("double")),
        )
        # spend_cliff_flag: M0-1 spend < 20% of H1 avg AND M0-2 spend >= 80% of H1 avg
        .withColumn(
            "spend_cliff_flag",
            F.when(
                F.col("_spend_h1_avg").isNotNull() & (F.col("_spend_h1_avg") > 0),
                F.when(
                    (F.col("_spend_m1") < 0.2 * F.col("_spend_h1_avg"))
                    & (F.col("_spend_m2") >= 0.8 * F.col("_spend_h1_avg")),
                    F.lit(1),
                ).otherwise(F.lit(0)),
            ).otherwise(F.lit(0)),
        )
        # cash_adv_ramp: (sum CA count H2 + 1) / (avg CA count H1 + 1)
        .withColumn(
            "cash_adv_ramp",
            (F.col("_ca_cnt_h2").cast("double") + 1.0)
            / (F.coalesce(F.col("_ca_cnt_h1_avg"), F.lit(0.0)) + 1.0),
        )
        # cash_adv_amt_share_h2: total CA amt H2 / total spend H2
        .withColumn(
            "cash_adv_amt_share_h2",
            F.when(
                (F.col("_spend_h2_sum").isNotNull()) & (F.col("_spend_h2_sum") != 0),
                F.col("_ca_amt_h2") / F.col("_spend_h2_sum"),
            ).otherwise(F.lit(None).cast("double")),
        )
        # txn_cnt_slope: OLS slope, NULL if < 4 months
        .withColumn(
            "txn_cnt_slope",
            F.when(
                (F.col("_ols_n") >= 4) & (_ols_denom != 0.0),
                (
                    F.col("_ols_n").cast("double") * F.col("_ols_sxy")
                    - F.col("_ols_sx") * F.col("_ols_sy")
                )
                / _ols_denom,
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    pass_b2 = feats_b2.select(
        "account_id",
        "spell_id",
        "spend_taper_ratio",
        "spend_cliff_flag",
        "cash_adv_ramp",
        "cash_adv_amt_share_h2",
        "txn_cnt_slope",
    )

    return pass_b1, pass_b2


# ── Private: logging ───────────────────────────────────────────────────────────


def _log_utilisation_stats(result: DataFrame) -> None:
    """Log coverage summary for the built utilisation table."""
    try:
        total = result.count()
        cov_util = result.filter(F.col("util_mean_h2").isNotNull()).count()
        cov_spend = result.filter(F.col("spend_taper_ratio").isNotNull()).count()
        cov_cliff = result.filter(F.col("spend_cliff_flag").isNotNull()).count()
        LOG.info(
            "CC utilisation features built: %d spells | "
            "util_mean_h2: %.1f%% | spend_taper_ratio: %.1f%% | spend_cliff_flag: %.1f%%",
            total,
            100.0 * cov_util / total if total > 0 else 0.0,
            100.0 * cov_spend / total if total > 0 else 0.0,
            100.0 * cov_cliff / total if total > 0 else 0.0,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute utilisation stats: %s (lazy eval context)", str(exc)
        )
