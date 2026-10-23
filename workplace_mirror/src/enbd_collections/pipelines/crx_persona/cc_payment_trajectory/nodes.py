"""T04b — CC Payment & Balance Trajectory Features (re-anchored).

# pylint: disable=too-many-locals, too-many-statements
# Rationale: two-pass feature builder (Pass A: transaction DOM/gap features;
# Pass B: monthly pay-ratio features). Each pass is self-contained; splitting
# further would obscure the T0-anchored window logic.

Build function: build_cc_payment_trajectory(crx_cc_transactions, crx_cc_balance,
                                            crx_cc_spell_table, prm_contract)

Business context:
    At 61+ DPD, credit cards receive Block X (permanent cancellation). All
    transaction activity stops — no utilization, no payment signals from that
    point. Features must be derived entirely from pre-delinquency history.
    This pipeline extracts that history anchored to T0 (spell onset), not to
    the model's observation_date. For cc_180_plus accounts T0 may be 18-24+
    months before observation_date; anchoring to observation_date would produce
    zero months of usable history.

    Output grain: one row per (account_id, spell_id). An account that cured and
    re-defaulted gets a separate spell — and separate features — for each episode.

Feature interpretation:
    Pass A (DOM/gap features) → payment discipline axis:
        A habitual payer with low pay_dom_std / high pay_dom_window_share who hit
        a sudden shock looks different from a chronically erratic payer. A large
        pay_dom_drift means payments were drifting later each month before onset.
        pay_gap_last_d measures the elapsed silence before T0.

    Pass B (ratio features) → payment capacity axis:
        pay_ratio_m = P_m / D_m per month (capped at 2.0). The contrast
        pay_ratio_mean_h2 vs pay_ratio_mean_h1 — whether recent repayment
        deteriorated relative to baseline — is a strong default predictor.
        pay_ratio_slope captures the direction of the trend over W_pre.

Window design (T04b — month-based, per 2026-08-19 decision)::

    M0          = trunc(t0, 'month')            — onset month (excluded from all windows)
    W_pre       = [w_pre_start, M0)             — clean pre-delinquency window (≤12 months)
    w_pre_start = max(M0−12m, prior_spell_cut, account_open_month, retention_floor)
    H2          = [M0−3m, M0)       → month_idx 1..3  — recent behaviour
    H1          = [w_pre_start, M0−3m) → month_idx ≥4  — baseline behaviour

T0 leakage guard: all transaction joins use strict ``txn_date < M0``
(M0 = trunc(t0, 'month')). The onset month is excluded; month_idx = 0
never appears.

Censored spells (t0_censored_flag=1) are excluded from feature computation;
they receive NULL for all features via left-join null-propagation.

Truncation columns (new in T04b):
    w_pre_start             : date — effective W_pre start (month-start date)
    w_pre_clean_m           : int — months in [w_pre_start, M0)
    w_pre_contaminated_flag : int — 1 if w_pre_start > M0−12m
    w_pre_truncation_reason : string — none | prior_spell | tenure | retention

FILL-IN blockers (T01 flagged, surfaced here per R17):
    min_pay_share_w12        : blocked by <<FILL-IN: prm_billing column for min_due_amount>>
    months_since_full_pay_t0 : blocked by <<FILL-IN: full-pay condition or source table>>

Day arithmetic note:
    pay_dom_* and pay_gap_*_d use actual day-of-month / datediff values.
    Month boundary changes affect WHICH transactions are included, but the
    gap/DOM calculations themselves remain day-based.

OLS slope implementation note:
    ``compute_ols_slope()`` from utils/ols.py is designed for pre-bucketed
    wide monthly data (dict of month_index → Column expression). For
    transaction-level OLS (pay_dom_drift) and monthly aggregate OLS
    (pay_ratio_slope), inline aggregation statistics are used instead —
    same mathematical formula, no pivot step required. This avoids a
    separate pivot shuffle for 12 columns on a large transactions table.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)

# Minimum number of non-null H1 months required before pay_ratio_mean_h1 is
# considered reliable.  H1 spans [w_pre_start, M0-3) — nominally 9 months.
# Fewer than 3 months of pre-delinquency payment history is not a credible
# baseline; the mean would rest on noise (one unusual month can shift it ±1.0).
_MIN_H1_MONTHS = 3


def build_cc_payment_trajectory(
    crx_cc_transactions: DataFrame,
    crx_cc_balance: DataFrame,
    crx_cc_spell_table: DataFrame,
    prm_contract: DataFrame,
) -> DataFrame:
    """Build CC payment & balance trajectory features anchored to T0 per spell.

    Args:
        crx_cc_transactions:  T04c intermediate — T0-scoped CC transaction history.
            direction=1 rows are credit/inflow (payments). Replaces raw_transaction.
            Required cols: contract_id, observation_date, direction, txn_amount_aed.
        crx_cc_balance:       T04c intermediate — T0-scoped total_due billing history.
            Replaces raw_stg_balance + raw_stg_account_group.
            Required cols: contract_id, observation_date, total_due.
        crx_cc_spell_table: T03b output at (account_id, spell_id) grain.
            Already scoped to the active cc_spine population.
        prm_contract:         Way4 monthly contract snapshots. Used to derive
            account_open_month via open_date per account.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id, spell_id, t0,
            w_pre_start, w_pre_clean_m, w_pre_contaminated_flag, w_pre_truncation_reason,
            pay_dom_std, pay_dom_window_share, pay_dom_drift,
            pay_gap_max_d, pay_gap_last_d,
            pay_ratio_mean_h1, pay_ratio_mean_h2, pay_ratio_slope,
            min_pay_share_w12       (NULL — FILL-IN blocker),
            months_since_full_pay_t0 (NULL — FILL-IN blocker),
            computed_at
    """
    # ── Step 0: spell base — exclude censored spells, carry prior_spell_end ──
    # t0_censored_flag=1 covers two subtypes (see cc_spell/nodes.py):
    #   data_depth        — T0 outside the billing window; may become scorable later.
    #   restructured_entry — new account ID opened mid-delinquency; T0-anchored features
    #                        cannot be computed from this account alone; needs T18/T19.
    # Both are correctly excluded here.  The distinction matters for T03c / coverage
    # reporting but not for feature computation — neither subtype can have a valid W_pre.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id", "spell_id", "t0", "prior_spell_end"
    )

    # ── Step -1: T0-scoped intermediates (pre-built by crx_cc_raw_extract T04c) ─
    # crx_cc_transactions and crx_cc_balance are already scoped to the T0 window;
    # no further raw extraction required here.
    txn = crx_cc_transactions
    balance = crx_cc_balance

    # ── Compute per-spell W_pre truncation boundaries ──────────────────────────
    w_pre = _compute_w_pre_truncation(txn, prm_contract, spell)
    spell_with_w = spell.join(w_pre, on=["account_id", "spell_id"], how="left")

    # ── Pass A: transaction-level features (DOM consistency, payment gaps) ──
    pass_a = _build_pass_a(txn, spell_with_w)

    # ── Pass B: monthly billing features (payment ratio vs total due) ─────────
    pass_b = _build_pass_b(txn, balance, spell_with_w)

    # ── Combine onto spell base ─────────────────────────────────────────────────
    # Left join: spells with zero payments in W_pre receive NULL for all features.
    result = spell_with_w.join(pass_a, on=["account_id", "spell_id"], how="left").join(
        pass_b, on=["account_id", "spell_id"], how="left"
    )

    # ── FILL-IN blocked features (NULL until column sources are confirmed) ────
    result = (
        result
        # <<FILL-IN: prm_billing column for min_due_amount>>
        # Once resolved: share of W_pre months where P_m ∈ [0.9×min_due, 1.1×min_due]
        .withColumn("min_pay_share_w12", F.lit(None).cast("double"))
        # <<FILL-IN: full-pay condition or source table>>
        # Once resolved: months since last month where P_m >= total_due (full statement pay)
        .withColumn("months_since_full_pay_t0", F.lit(None).cast("double")).withColumn(
            "computed_at", F.current_timestamp()
        )
    )

    _log_trajectory_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("pay_dom_std").cast("double"),
        F.col("pay_dom_window_share").cast("double"),
        F.col("pay_dom_drift").cast("double"),
        F.col("pay_gap_max_d").cast("int"),
        F.col("pay_gap_last_d").cast("int"),
        F.col("pay_ratio_mean_h1").cast("double"),
        F.col("pay_ratio_mean_h2").cast("double"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("min_pay_share_w12").cast("double"),
        F.col("months_since_full_pay_t0").cast("double"),
        F.col("computed_at"),
    )


# ── Private: W_pre truncation ──────────────────────────────────────────────────


def _compute_w_pre_truncation(
    prm_transaction: DataFrame,
    prm_contract: DataFrame,
    spell: DataFrame,
) -> DataFrame:
    """Compute per-spell W_pre window boundaries and truncation diagnostics.

    Three cut points (all scoped via inner-join to spell population — no
    unscoped scan of large tables):

    1. Retention floor: earliest transaction month in the raw data — hard limit
       of available history; no fabricating coverage that doesn't exist.
    2. Account open month: open_date from prm_contract — window cannot precede
       account existence.
    3. Prior spell cut: month after prior_spell_end — the previous delinquency
       episode is "dirty"; crossing into it would contaminate features with
       in-spell behavior from a different episode.

    w_pre_start = max(M0−12m, prior_spell_cut, account_open_month, retention_floor)
    where M0 = trunc(t0, 'month').

    Args:
        prm_transaction: used for retention floor (earliest txn month per account).
        prm_contract:    used for account open month (min obs_date per account).
        spell:           (account_id, spell_id, t0, prior_spell_end) — non-censored.

    Returns:
        DataFrame at (account_id, spell_id) grain with:
            w_pre_start             : date — effective W_pre start (month-start date)
            w_pre_clean_m           : int — months in [w_pre_start, M0)
            w_pre_contaminated_flag : int — 1 if w_pre_start > M0−12m
            w_pre_truncation_reason : string — none | prior_spell | tenure | retention
    """
    scope = spell.select("account_id").distinct()

    # ── Cut point 1: retention floor — earliest transaction month per account ──
    acct_retention = (
        prm_transaction.select(
            F.col("contract_id").alias("account_id"),
            F.col("observation_date").alias("txn_date"),
        )
        .join(scope, on="account_id", how="inner")
        .groupBy("account_id")
        .agg(F.trunc(F.min("txn_date"), "month").alias("retention_floor_month"))
    )

    # ── Cut point 2: account open month — open_date from prm_contract ────────────
    acct_open = (
        prm_contract.select(
            F.col("contract_id").alias("account_id"),
            F.col("open_date").alias("obs_date"),
        )
        .join(scope, on="account_id", how="inner")
        .groupBy("account_id")
        .agg(F.trunc(F.min("obs_date"), "month").alias("account_open_month"))
    )

    # ── Join per-account cut points onto the spell table ─────────────────────────
    spell_w = spell.join(acct_retention, on="account_id", how="left").join(
        acct_open, on="account_id", how="left"
    )

    # ── Per-spell truncation expressions ─────────────────────────────────────────
    m0 = F.trunc(F.col("t0"), "month")
    nominal = F.add_months(m0, -12)  # 12-month lookback — binding when no cut is later

    # Prior spell cut: month after cure month (cure month is partly delinquent)
    prior_cut = F.when(
        F.col("prior_spell_end").isNotNull(),
        F.add_months(F.trunc(F.col("prior_spell_end"), "month"), 1),
    )

    w_pre_start_expr = F.greatest(
        nominal,
        F.coalesce(prior_cut, nominal),
        F.coalesce(F.col("account_open_month"), nominal),
        F.coalesce(F.col("retention_floor_month"), nominal),
    )

    spell_w = (
        spell_w.withColumn("_m0", m0)
        .withColumn("_nominal", nominal)
        .withColumn("_prior_cut", prior_cut)
        .withColumn("w_pre_start", w_pre_start_expr)
        .withColumn(
            "w_pre_clean_m",
            F.floor(F.months_between(F.col("_m0"), F.col("w_pre_start"))).cast("int"),
        )
        .withColumn(
            "w_pre_contaminated_flag",
            F.when(F.col("w_pre_start") > F.col("_nominal"), 1).otherwise(0),
        )
        .withColumn(
            "w_pre_truncation_reason",
            # Priority: prior_spell > tenure > retention > none
            F.when(F.col("w_pre_contaminated_flag") == 0, "none")
            .when(
                F.col("_prior_cut").isNotNull()
                & (F.col("w_pre_start") == F.col("_prior_cut")),
                "prior_spell",
            )
            .when(
                F.col("account_open_month").isNotNull()
                & (F.col("w_pre_start") == F.col("account_open_month")),
                "tenure",
            )
            .when(
                F.col("retention_floor_month").isNotNull()
                & (F.col("w_pre_start") == F.col("retention_floor_month")),
                "retention",
            )
            .otherwise("none"),
        )
    )

    # Clamp negative w_pre_clean_m (retention_floor > T0).
    # Must override reason BEFORE clamping so the negative signal is not lost.
    spell_w = spell_w.withColumn(
        "w_pre_truncation_reason",
        F.when(F.col("w_pre_clean_m") < 0, F.lit("negative_window")).otherwise(
            F.col("w_pre_truncation_reason")
        ),
    ).withColumn(
        "w_pre_clean_m",
        F.greatest(F.col("w_pre_clean_m"), F.lit(0)),
    )

    return spell_w.select(
        "account_id",
        "spell_id",
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
    )


# ── Private: Pass A ────────────────────────────────────────────────────────────


def _build_pass_a(prm_transaction: DataFrame, spell: DataFrame) -> DataFrame:
    """Transaction-level payment features: DOM consistency and payment gaps.

    spell carries w_pre_start (date) and w_pre_clean_m (int) from
    _compute_w_pre_truncation, already joined onto spell_with_w.

    Returns one row per (account_id, spell_id) that has ≥1 payment in W_pre.
    Spells with no payments are absent; they become NULLs via left join.

    Window: [w_pre_start, M0) where M0 = trunc(t0, 'month').
    month_idx: M0−1 → 1, M0−2 → 2, …, M0−12 → 12.  M0 (idx=0) is excluded.

    Features computed::

        pay_dom_std         : stddev of dayofmonth across W_pre payments (NULL if <3).
                              Low = disciplined habitual payer; high = erratic timing.
        pay_dom_window_share: share of w_pre_clean_m months with ≥1 payment within
                              ±2 DOM of modal DOM (NULL if <3 payments).
                              Measures payment habit consistency.
        pay_dom_drift       : OLS slope of dayofmonth vs month_idx over W_pre
                              (NULL if <3 payments). Positive slope = payments were
                              drifting to later dates each month approaching onset.
        pay_gap_max_d       : max gap (days) between consecutive payments in W_pre
                              (NULL if <2 payments). Captures whether the customer
                              ever went a very long time without paying.
        pay_gap_last_d      : datediff(t0, most_recent_payment) (NULL if 0 payments).
                              Uses actual t0, not M0. A short gap suggests a sudden
                              shock; a long gap suggests slow drift into delinquency.
    """
    # Filter to payment transactions
    # direction == 1 = credit (inflow / payment reduces outstanding balance)
    # <<FILL-IN: any additional payment exclusion conditions>>
    txn_pay = prm_transaction.filter(F.col("direction") == 1).select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
    )

    # Join to spell table: one txn can match multiple spells when W_pre windows
    # of consecutive spells overlap the same calendar period. This is correct —
    # payment history before T0 is a valid feature for any spell anchored after it.
    payments = (
        txn_pay.join(
            spell,
            on=txn_pay["contract_id"] == spell["account_id"],
            how="inner",
        ).select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        # W_pre window: [w_pre_start, M0). M0 = trunc(t0,'month') is excluded.
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
    )

    payments = payments.withColumn("dom", F.dayofmonth("txn_date"))

    # month_idx: whole months before M0 (both endpoints truncated to month-start
    # to avoid partial-month bias when t0 falls mid-month).
    # M0-1 → 1,  M0-2 → 2, ...,  M0-12 → 12
    payments = payments.withColumn(
        "month_idx",
        F.floor(
            F.months_between(
                F.trunc(F.col("t0"), "month"), F.trunc(F.col("txn_date"), "month")
            )
        ).cast("int"),
    )

    # Lagged payment date for consecutive-gap computation within each spell
    w_pay = Window.partitionBy("account_id", "spell_id").orderBy("txn_date")
    payments = payments.withColumn("_prev_txn", F.lag("txn_date").over(w_pay))
    payments = payments.withColumn(
        "_gap_days",
        F.when(
            F.col("_prev_txn").isNotNull(),
            F.datediff(F.col("txn_date"), F.col("_prev_txn")),
        ),
    )

    # ── Step 1: spell-level aggregation ────────────────────────────────────────
    spell_agg = payments.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_n_pay"),
        F.first("t0").alias("t0"),
        F.first("w_pre_clean_m").alias(
            "_w_pre_clean_m"
        ),  # denominator for window_share
        # DOM stats
        F.stddev_samp("dom").alias("_dom_std_raw"),
        F.percentile_approx("dom", 0.5).alias("_modal_dom"),
        # Payment gap
        F.max("_gap_days").alias("_gap_max_raw"),
        F.max("txn_date").alias("_last_txn"),
        # OLS accumulators for pay_dom_drift (transaction-level inline OLS)
        F.sum(F.col("month_idx").cast("double")).alias("_dom_sx"),
        F.sum(F.col("dom").cast("double")).alias("_dom_sy"),
        F.sum(F.col("month_idx").cast("double") * F.col("dom").cast("double")).alias(
            "_dom_sxy"
        ),
        F.sum(
            F.col("month_idx").cast("double") * F.col("month_idx").cast("double")
        ).alias("_dom_sx2"),
    )

    # ── Step 2: pay_dom_window_share (requires modal DOM from Step 1) ──────────
    # Count calendar months in W_pre where ≥1 payment falls within ±2 days of
    # modal DOM.
    near_modal = (
        payments.join(
            spell_agg.select("account_id", "spell_id", "_modal_dom"),
            on=["account_id", "spell_id"],
        )
        .filter(F.abs(F.col("dom") - F.col("_modal_dom")) <= 2)
        .withColumn("_cal_month", F.trunc(F.col("txn_date"), "MM"))
        .groupBy("account_id", "spell_id")
        .agg(F.countDistinct("_cal_month").alias("_near_modal_months"))
    )

    spell_agg = spell_agg.join(near_modal, on=["account_id", "spell_id"], how="left")

    # ── Step 3: apply null guards and derive final feature columns ─────────────

    # pay_dom_std: NULL if < 3 payments
    spell_agg = spell_agg.withColumn(
        "pay_dom_std",
        F.when(F.col("_n_pay") >= 3, F.col("_dom_std_raw")).otherwise(
            F.lit(None).cast("double")
        ),
    )

    # pay_dom_window_share: NULL if < 3 payments; denominator = w_pre_clean_m
    # (actual clean months available per spell, not a fixed 12)
    spell_agg = spell_agg.withColumn(
        "pay_dom_window_share",
        F.when(
            (F.col("_n_pay") >= 3) & (F.col("_w_pre_clean_m") > 0),
            F.coalesce(F.col("_near_modal_months"), F.lit(0)).cast("double")
            / F.col("_w_pre_clean_m").cast("double"),
        ).otherwise(F.lit(None).cast("double")),
    )

    # pay_dom_drift: OLS slope of dayofmonth vs month_idx; NULL if < 3 payments
    _dom_denom = F.col("_n_pay").cast("double") * F.col("_dom_sx2") - F.col(
        "_dom_sx"
    ) * F.col("_dom_sx")
    spell_agg = spell_agg.withColumn(
        "pay_dom_drift",
        F.when(
            (F.col("_n_pay") >= 3) & (_dom_denom != 0.0),
            (
                F.col("_n_pay").cast("double") * F.col("_dom_sxy")
                - F.col("_dom_sx") * F.col("_dom_sy")
            )
            / _dom_denom,
        ).otherwise(F.lit(None).cast("double")),
    )

    # pay_gap_max_d: NULL if < 2 payments (no consecutive pair exists)
    spell_agg = spell_agg.withColumn(
        "pay_gap_max_d",
        F.when(F.col("_n_pay") >= 2, F.col("_gap_max_raw")).otherwise(
            F.lit(None).cast("int")
        ),
    )

    # pay_gap_last_d: days from most-recent W_pre payment to T0; NULL if no payments.
    # Uses actual t0 (not M0) — measures elapsed days to delinquency onset.
    # Always >= 0: guaranteed by txn_date < M0 ≤ t0 (onset month not yet started).
    spell_agg = spell_agg.withColumn(
        "pay_gap_last_d",
        F.when(
            F.col("_n_pay") > 0,
            F.datediff(F.col("t0"), F.col("_last_txn")),
        ).otherwise(F.lit(None).cast("int")),
    )

    return spell_agg.select(
        "account_id",
        "spell_id",
        "pay_dom_std",
        "pay_dom_window_share",
        "pay_dom_drift",
        "pay_gap_max_d",
        "pay_gap_last_d",
    )


# ── Private: Pass B ────────────────────────────────────────────────────────────


def _build_pass_b(
    prm_transaction: DataFrame,
    prm_billing: DataFrame,
    spell: DataFrame,
) -> DataFrame:
    """Monthly billing features: payment ratio relative to total due (D_m).

    spell carries w_pre_start (date) from _compute_w_pre_truncation, already
    joined onto spell_with_w.

    Window: [w_pre_start, M0). month_idx: M0−1 → 1, ..., M0−12 → 12.
    H2 = month_idx 1..3  (recent 3 months).
    H1 = month_idx ≥ 4   (older months beyond 3).

    pay_ratio_m = P_m / D_m per billing month (capped at 2.0 to limit outlier
    distortion). 1.0 = paid exactly what was due; < 1.0 = partial payment;
    0.0 = no payment. Undefined (NULL) when D_m = 0 or NULL.

    Features::

        pay_ratio_mean_h1 : mean(P_m / D_m) over H1 months (month_idx ≥ 4).
                            Baseline repayment behaviour in the older lookback.
                            NULL if fewer than _MIN_H1_MONTHS (3) non-null H1
                            months exist — one or two months is not a credible
                            baseline; a single outlier month would dominate.
        pay_ratio_mean_h2 : mean(P_m / D_m) over H2 months (month_idx 1..3).
                            Recent repayment in the 3 months just before onset.
                            The contrast h2 vs h1 — whether behaviour deteriorated
                            in the final quarter — is a strong default predictor.
        pay_ratio_slope   : OLS slope of pay_ratio_m vs month_idx over W_pre
                            (NULL if < 4 non-null months). Negative slope =
                            ratio was declining toward onset (worsening capacity).
        min_pay_share_w12 : NULL — <<FILL-IN: min_due_amount source>>
        months_since_full_pay_t0 : NULL — <<FILL-IN: full-pay condition or source>>
    """
    # ── Monthly payment totals P_m ─────────────────────────────────────────────
    txn_pay = prm_transaction.filter(F.col("direction") == 1).select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("txn_amount_aed"),
    )

    monthly_p = (
        txn_pay.join(
            spell,
            on=txn_pay["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))  # T0 leakage guard
        )
        .withColumn(
            "month_idx",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"), F.trunc(F.col("txn_date"), "month")
                )
            ).cast("int"),
        )
        .groupBy("account_id", "spell_id", "month_idx")
        .agg(F.sum("txn_amount_aed").alias("p_m"))
    )

    # ── Monthly billing D_m from prm_balance (wired as prm_billing) ────────────
    # <<FILL-IN: prm_billing column for total_due_amount (D_m)>>
    # Using CreditCardBalance.total_due (100% coverage) pending confirmation.
    billing = prm_billing.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("total_due").alias("d_m"),
    )

    monthly_d = (
        billing.join(
            spell,
            on=billing["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("billing_date"),
            F.col("d_m"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("billing_date") >= F.col("w_pre_start"))
            & (F.col("billing_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "month_idx",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("billing_date"), "month"),
                )
            ).cast("int"),
        )
        # One billing record per (account, spell, month) — take first if duplicates
        .groupBy("account_id", "spell_id", "month_idx")
        .agg(F.first("d_m").alias("d_m"))
    )

    # ── Join P_m and D_m; compute monthly pay_ratio ────────────────────────────
    # Left join from monthly_d: billing record defines the eligible months.
    # Months where billing exists but no payment was made → P_m defaults to 0.
    # Months where D_m = 0 or NULL → pay_ratio_m = NULL (undefined).
    monthly = (
        monthly_d.join(
            monthly_p, on=["account_id", "spell_id", "month_idx"], how="left"
        )
        .withColumn("p_m", F.coalesce(F.col("p_m"), F.lit(0.0)))
        .withColumn(
            "pay_ratio_m",
            F.when(
                F.col("d_m").isNotNull() & (F.col("d_m") > 0),
                F.least(F.col("p_m") / F.col("d_m"), F.lit(2.0)),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    # ── Aggregate per spell ─────────────────────────────────────────────────────
    result = monthly.groupBy("account_id", "spell_id").agg(
        # H1 = older half: month_idx >= 4 (months M0-4 through end of W_pre)
        F.avg(
            F.when(
                (F.col("month_idx") >= 4) & F.col("pay_ratio_m").isNotNull(),
                F.col("pay_ratio_m"),
            )
        ).alias("pay_ratio_mean_h1"),
        # Count of non-null H1 months — used to enforce _MIN_H1_MONTHS floor below
        F.count(
            F.when(
                (F.col("month_idx") >= 4) & F.col("pay_ratio_m").isNotNull(),
                F.lit(1),
            )
        ).alias("_h1_n"),
        # H2 = recent half: month_idx 1..3 (months M0-1, M0-2, M0-3)
        F.avg(
            F.when(
                (F.col("month_idx") >= 1)
                & (F.col("month_idx") <= 3)
                & F.col("pay_ratio_m").isNotNull(),
                F.col("pay_ratio_m"),
            )
        ).alias("pay_ratio_mean_h2"),
        # OLS accumulators for pay_ratio_slope (inline OLS; no pivot required)
        F.count(F.when(F.col("pay_ratio_m").isNotNull(), F.lit(1))).alias("_pr_n"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sx"),
        F.sum(
            F.when(F.col("pay_ratio_m").isNotNull(), F.col("pay_ratio_m")).otherwise(
                F.lit(0.0)
            )
        ).alias("_pr_sy"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double") * F.col("pay_ratio_m"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sxy"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double") * F.col("month_idx").cast("double"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sx2"),
    )

    # OLS slope for pay_ratio_slope: NULL if < 4 non-null months
    _pr_denom = F.col("_pr_n").cast("double") * F.col("_pr_sx2") - F.col(
        "_pr_sx"
    ) * F.col("_pr_sx")
    result = result.withColumn(
        "pay_ratio_slope",
        F.when(
            (F.col("_pr_n") >= 4) & (_pr_denom != 0.0),
            (
                F.col("_pr_n").cast("double") * F.col("_pr_sxy")
                - F.col("_pr_sx") * F.col("_pr_sy")
            )
            / _pr_denom,
        ).otherwise(F.lit(None).cast("double")),
    )

    # Enforce minimum H1 month floor: pay_ratio_mean_h1 requires at least
    # _MIN_H1_MONTHS non-null H1 months to be considered a reliable baseline.
    # Fewer months → NULL; downstream c_shock_2 condition then fails cleanly.
    result = result.withColumn(
        "pay_ratio_mean_h1",
        F.when(F.col("_h1_n") >= _MIN_H1_MONTHS, F.col("pay_ratio_mean_h1")).otherwise(
            F.lit(None).cast("double")
        ),
    )

    # FILL-IN blocked features — return NULL until column sources confirmed
    result = result.withColumn(
        "min_pay_share_w12",
        F.lit(None).cast(
            "double"
        ),  # <<FILL-IN: prm_billing column for min_due_amount>>
    ).withColumn(
        "months_since_full_pay_t0",
        F.lit(None).cast("double"),  # <<FILL-IN: full-pay condition or source table>>
    )

    return result.select(
        "account_id",
        "spell_id",
        "pay_ratio_mean_h1",
        "pay_ratio_mean_h2",
        "pay_ratio_slope",
        "min_pay_share_w12",
        "months_since_full_pay_t0",
    )


# ── Private: logging ───────────────────────────────────────────────────────────


def _log_trajectory_stats(result: DataFrame) -> None:
    """Log coverage summary for the built trajectory table."""
    try:
        total = result.count()
        cov_gap = result.filter(F.col("pay_gap_last_d").isNotNull()).count()
        cov_dom = result.filter(F.col("pay_dom_std").isNotNull()).count()
        cov_ratio = result.filter(F.col("pay_ratio_mean_h2").isNotNull()).count()
        LOG.info(
            "CC payment trajectory built: %d spells | "
            "pay_gap_last_d: %.1f%% | pay_dom_std: %.1f%% | pay_ratio_mean_h2: %.1f%%",
            total,
            100.0 * cov_gap / total if total > 0 else 0.0,
            100.0 * cov_dom / total if total > 0 else 0.0,
            100.0 * cov_ratio / total if total > 0 else 0.0,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute trajectory stats: %s (lazy eval context)", str(exc)
        )
