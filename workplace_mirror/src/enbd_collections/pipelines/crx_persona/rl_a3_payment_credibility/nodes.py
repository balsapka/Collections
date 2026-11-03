"""RL A3 Payment Credibility axis – RL-specific adapter nodes (RL-A3-1).

Nine-node pipeline that mirrors cc_a3_payment_credibility's structure (same
approach names, same shipped defaults, same window semantics), reusing CC logic
where possible and rebuilding only what is hardcoded to CC's statement ladder:

    build_rl_a3_commitment_signals                                 [Dim A]
    build_rl_a3_strong_negative_signals                            [strong-negative evidence]
    build_rl_a3_dlq_cycles                                         [shared monthly ledger rows]
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall          [Dim B]
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count     [Dim B, shipped]
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement            [Dim B]
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count [Dim C, shipped]
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement        [Dim C]
    build_rl_a3_payment_credibility                                [CC combiner, wrapped]

Naming: "dlq" = Dimension B (payments while delinquent), "pre_dlq" = Dimension
C (record before delinquency); the suffix is the approach.
  - payment_sum_waterfall (Dim B): floor(sum of the window's cash / EMI) – one
    large payment can credit several months, RL has no bucket ladder to walk,
    so this is a division rather than CC's waterfall walk; the tag is kept so
    the shared combiner's shadow columns line up with CC's.
  - single_payment_cycle_count: each month judged on its own (Dim B: cash >=
    100% of EMI, Dim B and Dim C), counting qualifying months.
  - dpd_bucket_movement: payment inferred from month-over-month bucket movement.

Each node's output dataset is the function name with "build_" replaced by
"crx_" (see pipeline.py).

Timing: RL's total_paid is the cash received during the month and the bucket is
the month-end state, so a month's cash and bucket result sit on the same row.
Dimension B uses result months (window_start, observation_date]; Dimension C
uses months [window_start, t0).

Node 1 difference from CC: crx_rl_a4_spine already carries (account_id,
observation_date, spell_id, t0, cif_id) resolved by RL-A4-2, so no separate
spell-table lookup is needed. rl_spine_as_cc_shim() reshapes it into the
(cc_spine, spell_table) contract build_a3_commitment_signals and
build_a3_strong_negative_signals expect, so the CC functions run unchanged (R14). The
strong-negative node also applies a 24-month partition floor to
dcore_prm_followup_outcomes (performance guard, not a logic change).

The last node wraps CC's build_a3_payment_credibility (never modified) and pins
both shipped approaches to single_payment_cycle_count, CC's defaults.
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.crx_persona._spine_utils import rl_spine_as_cc_shim
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.nodes import (
    build_a3_commitment_signals,
    build_a3_payment_credibility,
    build_a3_strong_negative_signals,
)
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility._signals_common import (
    aggregate_dlq_window,
    aggregate_pre_dlq_window,
    payment_meets_floor,
    resolve_pre_dlq_spell_window,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility._signals_common import (
    resolve_rl_dlq_payment_window,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility.constants import (
    _DLQ_LEVEL_SATURATED_RL,
    _DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    _PRE_DLQ_NOT_DELINQUENT_MAX_RL,
    _PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    _TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
    _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP,
    _TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE,
    _TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
)

LOG = logging.getLogger(__name__)

__all__ = [
    "build_rl_a3_commitment_signals",
    "build_rl_a3_strong_negative_signals",
    "build_rl_a3_dlq_cycles",
    "build_rl_a3_dlq_payment_signals_payment_sum_waterfall",
    "build_rl_a3_dlq_payment_signals_single_payment_cycle_count",
    "build_rl_a3_dlq_payment_signals_dpd_bucket_movement",
    "build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
    "build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
    "build_rl_a3_payment_credibility",
]


# ── Node 1: build_rl_a3_commitment_signals ───────────────────────────────


def build_rl_a3_commitment_signals(  # pylint: disable=too-many-positional-arguments
    crx_rl_a4_spine: DataFrame,
    dcore_observation_spine: DataFrame,
    feat_ptp: DataFrame,
    feat_settlement: DataFrame,
    int_ptp: DataFrame = None,
    ptp_instalments: DataFrame = None,
    int_settlement: DataFrame = None,
    settlement_instalments: DataFrame = None,
) -> DataFrame:
    """Dimension A (commitments kept) for RL. Thin wrapper over CC's node.

    Reshapes crx_rl_a4_spine into the (cc_spine, spell_table) shim pair via
    rl_spine_as_cc_shim() and delegates to build_a3_commitment_signals (R14 reuse) –
    identical PTP / settlement counts, pooled broken streak and level / points as CC.

    Args:
        crx_rl_a4_spine: RL spine at (account_id, observation_date) grain,
            already windowed to the persona date range and carrying
            spell_id / t0 / cif_id (RL-A4-2 Node 2 output).
        dcore_observation_spine: RL-scoped DCORE account→agreement mapping
            (RL-D5). Required cols: account_id, observation_date, agreement_id,
            cif_id.
        feat_ptp: dcore_feat_ptp – PTP history per agreement.
        feat_settlement: dcore_feat_settlement – settlement/arrangement
            history per agreement.
        int_ptp / ptp_instalments / int_settlement / settlement_instalments:
            dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments – Dimension A broken streak.

    Returns:
        crx_rl_a3_commitment_signals – same schema as
        crx_cc_a3_commitment_signals.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    return build_a3_commitment_signals(
        cc_spine=cc_spine_shim,
        spell_table=spell_table_shim,
        observation_spine=dcore_observation_spine,
        feat_ptp=feat_ptp,
        feat_settlement=feat_settlement,
        int_ptp=int_ptp,
        ptp_instalments=ptp_instalments,
        int_settlement=int_settlement,
        settlement_instalments=settlement_instalments,
    )


# ── Node 1b: build_rl_a3_strong_negative_signals ─────────────────────────


def build_rl_a3_strong_negative_signals(  # pylint: disable=too-many-positional-arguments
    crx_rl_a4_spine: DataFrame,
    dcore_observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    crx_persona: dict,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
) -> DataFrame:
    """Strong-negative evidence for RL. Thin wrapper with a 24m partition floor.

    Same shim as build_rl_a3_commitment_signals, delegating to CC's
    build_a3_strong_negative_signals. RL has no card transactions, so the Refusal rule
    keeps Dimension B's any-payment flag as its payment test.

    Args:
        crx_rl_a4_spine / dcore_observation_spine / int_ptp / int_settlement: as
            build_rl_a3_commitment_signals.
        followup_outcomes: dcore_prm_followup_outcomes – DCORE contact attempt
            log. Required cols: agreement_id, action_ts, action_code,
            result_category, result_name.
        crx_persona: Persona param dict with persona_start_date /
            persona_end_date.

    Returns:
        crx_rl_a3_strong_negative_signals – same schema as
        crx_cc_a3_strong_negative_signals.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)

    persona_start_date = crx_persona["persona_start_date"]
    dcore_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=24)
    ).isoformat()
    followup_filtered = followup_outcomes.filter(
        F.col("action_ts").cast("date") >= F.lit(dcore_floor)
    )
    LOG.info(
        "build_rl_a3_strong_negative_signals [%s → %s]: "
        "dcore_prm_followup_outcomes floored at %s",
        persona_start_date,
        crx_persona["persona_end_date"],
        dcore_floor,
    )

    return build_a3_strong_negative_signals(
        cc_spine=cc_spine_shim,
        spell_table=spell_table_shim,
        observation_spine=dcore_observation_spine,
        followup_outcomes=followup_filtered,
        int_ptp=int_ptp,
        int_settlement=int_settlement,
    )


# ── Node 2: build_rl_a3_dlq_cycles ───────────────────────────────────────


def _rl_string_key(df: DataFrame, col: str = "account_id"):
    """Double/decimal-safe account_id -> string cast, replicated locally
    rather than importing rl_full_history.nodes' private _string_key helper
    (a double/decimal account_id cast straight to string gives
    "1.23456789E8" and silently zeroes a leftsemi join – the same trap
    build_rl_full_history already guards against)."""
    dtype = df.schema[col].dataType
    c = F.col(col)
    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
        c = c.cast("long")
    return F.trim(c.cast("string"))


def build_rl_a3_dlq_cycles(
    crx_rl_full_history: DataFrame,
    int_loan_master: DataFrame,
    rl_spine: DataFrame,
) -> DataFrame:
    """Per-month ledger rows shared by every RL Dimension B/C approach – the
    RL counterpart of CC's build_a3_payment_cycles (bucket history + EMI due
    + cash received), without a billing-cycle ladder (RL has none).

    One row per account per month-end. The month-end row M carries both the
    month's cash (total_paid = payment_amount_mtd, cash received during M) and
    the month-end bucket, so bucket(M-1) -> bucket(M) is explained by the
    cash in M: payment and bucket result sit on the SAME row. (CC needs a
    result-statement re-key because its payment belongs to the cycle that
    OPENS at the statement; RL does not.) [CONFIRM] – see the validation
    snippet's cash-explains-bucket-change check.

    dlq_level_m is read straight from crx_rl_full_history.dlq_bucket (0-7).
    dlq_level_prev_m is the previous month's bucket, computed over the FULL
    unwindowed history so the first in-scope month still has a real previous
    month (same reason CC sources its lag from crx_cc_full_history).

    monthly_emi_due and total_paid come from int_loan_master (scoped to
    rl_spine through a broadcast leftsemi, with a double/decimal-safe
    account_id cast – see _rl_string_key). monthly_emi_asof is monthly_emi_due
    forward-filled to the latest non-null value up to that month – the EMI a
    month's payment is judged against when its own row is NULL, and robust to
    the rare EMI change on restructure.

    Args:
        crx_rl_full_history: RL-B1 – (account_id, month_end_date, dlq_bucket,
            ...), full unwindowed history, already scoped to rl_spine.
        int_loan_master: monthly loan snapshots – account_id, observation_date,
            monthly_emi_due, total_paid.
        rl_spine: model-namespaced RL spine – used only to scope
            int_loan_master the same way build_rl_full_history already scopes
            crx_rl_full_history itself.

    Returns:
        DataFrame at grain (account_id, billing_date) with: dlq_level_m (int),
        dlq_level_prev_m (int, NULL on an account's first month),
        monthly_emi_due (double, nullable), monthly_emi_asof (double,
        nullable), total_paid (double, nullable).
    """
    spine_keys = rl_spine.select(
        _rl_string_key(rl_spine).alias("account_id")
    ).distinct()
    emi = int_loan_master.join(
        F.broadcast(spine_keys), on="account_id", how="leftsemi"
    ).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("monthly_emi_due").cast("double"),
        F.col("total_paid").cast("double"),
    )

    history = crx_rl_full_history.select(
        F.col("account_id").cast("string"),
        F.col("month_end_date").alias("billing_date"),
        F.col("dlq_bucket").cast("int").alias("dlq_level_m"),
    )

    _w_account_history = Window.partitionBy("account_id").orderBy("billing_date")
    with_lag = history.withColumn(
        "dlq_level_prev_m", F.lag("dlq_level_m").over(_w_account_history)
    )

    joined = (
        with_lag.alias("h")
        .join(
            emi.alias("e"),
            (F.col("h.account_id") == F.col("e.account_id"))
            & (F.col("h.billing_date") == F.col("e.observation_date")),
            "left",
        )
        .select(
            F.col("h.account_id").alias("account_id"),
            F.col("h.billing_date").alias("billing_date"),
            F.col("h.dlq_level_m").alias("dlq_level_m"),
            F.col("h.dlq_level_prev_m").alias("dlq_level_prev_m"),
            F.col("e.monthly_emi_due").alias("monthly_emi_due"),
            F.col("e.total_paid").alias("total_paid"),
        )
    )

    _w_asof = (
        Window.partitionBy("account_id")
        .orderBy("billing_date")
        .rowsBetween(Window.unboundedPreceding, 0)
    )
    return joined.withColumn(
        "monthly_emi_asof",
        F.last(F.col("monthly_emi_due"), ignorenulls=True).over(_w_asof),
    )


# ── Dimension B shared helpers ───────────────────────────────────────────


def _rl_dlq_payment_level_and_points(agg: DataFrame) -> DataFrame:
    """Add dlq_payment_level (regular/some/none) + dlq_payment_points (2/1/0)
    – shared ladder for ALL Dimension B approaches (payment_sum_waterfall,
    single_payment_cycle_count, dpd_bucket_movement),
    mirroring CC's _dlq_payment_level_and_points (cc_a3_payment_credibility
    .nodes) which CC itself factored out for the identical reason: both of
    its methods need the same window-length-dependent "regular" thresholds,
    only the per-cycle "did they pay" primitive differs. Expects agg to
    already have dlq_payment_window_months, dlq_payment_qualifying_month_cnt,
    dlq_payment_any_flag."""
    result = agg.withColumn(
        "dlq_payment_level",
        F.when(
            (
                (
                    F.col("dlq_payment_window_months")
                    == _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP
                )
            )
            | (
                (
                    F.col("dlq_payment_window_months")
                    != _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID
                )
            ),
            F.lit("regular"),
        )
        .when(F.col("dlq_payment_any_flag") == 1, F.lit("some"))
        .otherwise(F.lit("none"))
    )
    return result.withColumn(
        "dlq_payment_points",
        F.when(F.col("dlq_payment_level") == "regular", F.lit(2))
        .when(F.col("dlq_payment_level") == "some", F.lit(1))
        .otherwise(F.lit(0)),
    )


def _rl_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Final select/cast shared by all three Dimension B approaches –
    identical output contract by design (each feeds the matching
    dlq_payment_signals_<approach> argument of
    build_rl_a3_payment_credibility)."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("t0").cast("date"),
        F.col("dlq_payment_window_months").cast("int"),
        F.col("dlq_payment_any_window_months").cast("int"),
        F.col("dlq_payment_qualifying_month_cnt").cast("int"),
        F.col("dlq_payment_any_flag").cast("int"),
        F.col("dlq_payment_level").cast("string"),
        F.col("dlq_payment_points").cast("int"),
    )


# ── Dimension B approaches ───────────────────────────────────────────────
# All three use the same window – result months (window_start, observation_date]
# on the month-end row – because RL's cash and bucket for month M sit on row M.
# The month at t0 is excluded (the cash that failed to stop onset); the
# observation month is included (known at the observation).


def build_rl_a3_dlq_payment_signals_payment_sum_waterfall(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, payment_sum_waterfall approach – is money coming in now?

    RL's counterpart of CC's build_a3_dlq_payment_signals_payment_sum_waterfall
    (same tag, so the shared combiner's columns line up). RL has no bucket
    ladder to walk: monthly_emi_due is a FIXED contractual amount, so "how
    many EMI-months did the payments cover" reduces to division:

        dlq_payment_qualifying_month_cnt = floor(sum(total_paid over window) / emi)

    emi is the account's monthly_emi_asof at observation_date (forward-filled,
    resolved before any groupBy – an F.last() inside a groupBy is not
    deterministic). Like CC's waterfall, one large payment can credit several
    months. any_flag = any cash in the "any payment" window (12 months in the
    deep band, otherwise the regular window).

    Window: months in (window_start, observation_date], window length from
    resolve_rl_dlq_payment_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        CC's Dimension B builders: t0, dlq_payment_window_months,
        dlq_payment_qualifying_month_cnt, dlq_payment_any_flag,
        dlq_payment_level (regular/some/none), dlq_payment_points (2/1/0).
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    emi_at_obs = crx_rl_a3_dlq_cycles.select(
        F.col("account_id"),
        F.col("billing_date").alias("observation_date"),
        F.col("monthly_emi_asof").alias("_emi_amount"),
    )

    joined = spine_with_window.alias("s").join(
        crx_rl_a3_dlq_cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col("c.billing_date") > F.col("s._any_window_start"))
        & (F.col("c.billing_date") <= F.col("s.observation_date")),
        "left",
    )

    # One join over the wider "any payment" window; the EMI-month count only sums the
    # "Regular" window (billing_date > _window_start). In the deep band, months with cash
    # below the minimum (100 AED) are ignored in both sums.
    _counted_cash = payment_meets_floor(F.col("c.total_paid"))
    agg = joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.observation_date").alias("observation_date"),
        F.col("s.t0").alias("t0"),
        F.col("s._window_months").alias("dlq_payment_window_months"),
        F.col("s._any_window_months").alias("dlq_payment_any_window_months"),
    ).agg(
        F.coalesce(
            F.sum(
                F.when(
                    (F.col("c.billing_date") > F.col("s._window_start"))
                    & _counted_cash,
                    F.col("c.total_paid"),
                )
            ),
            F.lit(0.0),
        ).alias("_window_payment_sum"),
        F.coalesce(
            F.sum(F.when(_counted_cash, F.col("c.total_paid"))), F.lit(0.0)
        ).alias("_any_window_payment_sum"),
    )

    agg = agg.join(emi_at_obs, on=["account_id", "observation_date"], how="left")

    agg = agg.withColumn(
        "dlq_payment_qualifying_month_cnt",
        F.when(
            F.col("_emi_amount").isNotNull() & (F.col("_emi_amount") > 0),
            F.floor(F.col("_window_payment_sum") / F.col("_emi_amount")),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    ).withColumn(
        "dlq_payment_any_flag",
        (F.col("_any_window_payment_sum") > 0).cast("int"),
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


def build_rl_a3_dlq_payment_signals_single_payment_cycle_count(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, single_payment_cycle_count approach (RL default).

    RL counterpart of CC's build_a3_dlq_payment_signals_single_payment_cycle_count:
    each month is judged on its own – total_paid >= 100% of that month's EMI
    (_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE x monthly_emi_asof) – and the
    window count is the number of qualifying months. No partial credit and no
    multi-month credit from one large payment (unlike payment_sum_waterfall).
    Note total_paid is the month's cash total, not one transaction. any_flag =
    any cash in the "any payment" window (12 months in the deep band). A month with no
    EMI cannot qualify.

    Window: months in (window_start, observation_date]; the window join and
    aggregation are CC's shared aggregate_dlq_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        build_rl_a3_dlq_payment_signals_payment_sum_waterfall.
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    # Required cash = max(100% of the month's EMI, the deep-band minimum of 100 AED).
    _required_cash = F.greatest(
        F.col("c.monthly_emi_asof") * F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE),
        F.col("s._min_payment_aed"),
    )
    _is_qualifying_cycle = F.when(
        F.col("c.monthly_emi_asof").isNotNull() & (F.col("c.monthly_emi_asof") > 0),
        F.coalesce(F.col("c.total_paid"), F.lit(0.0)) >= _required_cash,
    ).otherwise(F.lit(False))

    agg = aggregate_dlq_window(
        spine_with_window,
        crx_rl_a3_dlq_cycles,
        "billing_date",
        _is_qualifying_cycle.cast("int"),
        (F.col("c.total_paid") > 0) & payment_meets_floor(F.col("c.total_paid")),
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


def build_rl_a3_dlq_payment_signals_dpd_bucket_movement(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, dpd_bucket_movement approach – RL counterpart of CC's
    build_a3_dlq_payment_signals_dpd_bucket_movement.

    Infers payment from month-over-month bucket movement. For month M, the
    month-end bucket already reflects the cash received in M, so M's bucket is
    compared with the PREVIOUS month's (dlq_level_prev_m, a lag):
        no previous month                                   -> 0
        bucket improved (level < prev)                      -> prev - level (raw delta)
        flat, nonzero, below the cap                        -> 1
        flat at zero                                        -> 0 (nothing delinquent)
        flat at the cap (_DLQ_LEVEL_SATURATED_RL = 7)       -> 0 (no RL ladder to
            fall back on; ~all arrivals at RL bucket 7 coincide with
            charge-off/write-off, after which no real payments occur)
        worsened                                            -> 0
    RL credits the RAW delta on an improvement (no CC-style "+1 unless cured")
    – [CONFIRM], see constants.py. Window and aggregation are the same as the
    other Dimension B approaches.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        build_rl_a3_dlq_payment_signals_payment_sum_waterfall.
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    _dlq_levels_improved = F.col("dlq_level_prev_m") - F.col("dlq_level_m")
    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_qualifying_months_m",
        F.when(F.col("dlq_level_prev_m").isNull(), F.lit(0))
        .when(_dlq_levels_improved > 0, _dlq_levels_improved)
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") < _DLQ_LEVEL_SATURATED_RL)
            & (F.col("dlq_level_m") != 0),
            F.lit(1),
        )
        .otherwise(F.lit(0)),
    )

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "billing_date",
        F.col("c._qualifying_months_m"),
        F.col("c._qualifying_months_m") >= 1,
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


# ── Dimension C approaches ───────────────────────────────────────────────
# Window: the 12 months strictly before t0 (CC's resolve_pre_dlq_spell_window,
# reused through rl_spine_as_cc_shim). Month M's cash and bucket sit on row M,
# so both approaches judge row M: cash vs EMI, or bucket(M) back at zero.


def _rl_pre_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Final select/cast shared by both Dimension C approaches (identical
    output contract by design)."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("pre_dlq_months_due_n").cast("int"),
        F.col("pre_dlq_months_paid_as_billed_n").cast("int"),
        F.col("pre_dlq_paid_as_billed_share").cast("double"),
    )


def build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension C, single_payment_cycle_count approach (RL default) –
    record before delinquency.

    RL counterpart of CC's
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count: a month is
    "paid as billed" when total_paid >= _TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE
    (100%) of monthly_emi_due; a month "has due" when monthly_emi_due is not
    null and > 0. Window: months in [window_start, t0). The window join and
    share derivation are CC's shared aggregate_pre_dlq_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine – resolves spell_id/t0 and limits the
            spells to the current population.

    Returns:
        DataFrame at grain (account_id, spell_id): t0, pre_dlq_months_due_n,
        pre_dlq_months_paid_as_billed_n, pre_dlq_paid_as_billed_share (NULL
        when pre_dlq_months_due_n is below _TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE –
        the "no_record" condition).
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spells = resolve_pre_dlq_spell_window(cc_spine_shim, spell_table_shim)

    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_has_due",
        F.col("monthly_emi_due").isNotNull() & (F.col("monthly_emi_due") > 0),
    ).withColumn(
        "_paid_as_billed",
        F.col("total_paid").isNotNull()
        & (
            F.col("total_paid")
            >= F.col("monthly_emi_due") * F.lit(_TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE)
        ),
    )

    result = aggregate_pre_dlq_window(
        spells,
        cycles_with_evidence,
        "_paid_as_billed",
        evidence_date_col="billing_date",
        min_months_due=_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    )
    return _rl_pre_dlq_payment_signals_output(result)


def build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension C, dpd_bucket_movement approach – RL counterpart of CC's
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement.

    "Paid as billed" = the month's own bucket is back to / still at
    <= _PRE_DLQ_NOT_DELINQUENT_MAX_RL (0 – RL bucket 1 is already real
    delinquency, so the threshold is 0, not CC's 1). The month's own
    (month-end) bucket is used, not the next month's: it already reflects
    that month's cash, and using the next month's would count the onset
    transition (always delinquent by definition of t0) as an unpaid month in
    every spell. "Has due" and the window are the same as the
    single_payment_cycle_count approach.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine – resolves spell_id/t0 and limits the
            spells to the current population.

    Returns:
        DataFrame at grain (account_id, spell_id) – same contract as
        build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spells = resolve_pre_dlq_spell_window(cc_spine_shim, spell_table_shim)

    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_has_due",
        F.col("monthly_emi_due").isNotNull() & (F.col("monthly_emi_due") > 0),
    ).withColumn(
        "_paid_as_billed",
        F.col("dlq_level_m").isNotNull()
        & (F.col("dlq_level_m") <= _PRE_DLQ_NOT_DELINQUENT_MAX_RL),
    )

    result = aggregate_pre_dlq_window(
        spells,
        cycles_with_evidence,
        "_paid_as_billed",
        evidence_date_col="billing_date",
        min_months_due=_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    )
    return _rl_pre_dlq_payment_signals_output(result)


# ── Node: build_rl_a3_payment_credibility ────────────────────────────────


def build_rl_a3_payment_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    commitment_signals: DataFrame,
    negative_signals: DataFrame,
    dlq_payment_signals_payment_sum_waterfall: DataFrame,
    dlq_payment_signals_single_payment_cycle_count: DataFrame,
    dlq_payment_signals_dpd_bucket_movement: DataFrame,
    pre_dlq_payment_signals_single_payment_cycle_count: DataFrame,
    pre_dlq_payment_signals_dpd_bucket_movement: DataFrame,
    dlq_payment_evidence_method: str = _DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    pre_dlq_payment_evidence_method: str = _PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    model_id: str = None,
    persona_end_date: str = None,
) -> DataFrame:
    """Thin wrapper over CC's build_a3_payment_credibility (imported
    unchanged, R14): feeds it all three Dimension B approaches and both
    Dimension C approaches. The shipped approach per dimension is switchable
    from RL's own config keys (params:rl_a3_dlq_payment_evidence_method /
    params:rl_a3_pre_dlq_payment_evidence_method, default
    single_payment_cycle_count – the same default CC ships), deliberately
    separate from CC's a3_* keys so a CC config change never moves RL. The
    other approaches stay in the output as per-approach shadow columns. CC's
    combiner rejects unknown method names and raises if the selected
    approach's signals are missing, so a misconfiguration cannot silently
    ship level "none".

    Args:
        commitment_signals: crx_rl_a3_commitment_signals (Dimension A).
        negative_signals: crx_rl_a3_strong_negative_signals (strong-negative evidence).
        dlq_payment_signals_payment_sum_waterfall:
            crx_rl_a3_dlq_payment_signals_payment_sum_waterfall (Dimension B).
        dlq_payment_signals_single_payment_cycle_count:
            crx_rl_a3_dlq_payment_signals_single_payment_cycle_count
            (Dimension B, shipped).
        dlq_payment_signals_dpd_bucket_movement:
            crx_rl_a3_dlq_payment_signals_dpd_bucket_movement (Dimension B).
        pre_dlq_payment_signals_single_payment_cycle_count:
            crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count
            (Dimension C, shipped).
        pre_dlq_payment_signals_dpd_bucket_movement:
            crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement (Dimension C).
        dlq_payment_evidence_method: shipped Dimension B approach –
            "single_payment_cycle_count" (default), "payment_sum_waterfall" or
            "dpd_bucket_movement" (params:rl_a3_dlq_payment_evidence_method).
        pre_dlq_payment_evidence_method: shipped Dimension C approach –
            "single_payment_cycle_count" (default) or "dpd_bucket_movement"
            (params:rl_a3_pre_dlq_payment_evidence_method).
        model_id: optional – with persona_end_date, logs the latest-month
            a3_state_v1 distribution.
        persona_end_date: optional – paired with model_id.

    Returns:
        crx_rl_a3_payment_credibility – same schema as
        crx_cc_a3_payment_credibility.
    """
    signals = {
        "dlq_payment_signals_payment_sum_waterfall": (
            dlq_payment_signals_payment_sum_waterfall
        ),
        "dlq_payment_signals_single_payment_cycle_count": (
            dlq_payment_signals_single_payment_cycle_count
        ),
        "dlq_payment_signals_dpd_bucket_movement": (
            dlq_payment_signals_dpd_bucket_movement
        ),
        "pre_dlq_payment_signals_single_payment_cycle_count": (
            pre_dlq_payment_signals_single_payment_cycle_count
        ),
        "pre_dlq_payment_signals_dpd_bucket_movement": (
            pre_dlq_payment_signals_dpd_bucket_movement
        ),
    }
    return build_a3_payment_credibility(
        commitment_signals,
        negative_signals,
        **signals,
        dlq_payment_evidence_method=dlq_payment_evidence_method,
        pre_dlq_payment_evidence_method=pre_dlq_payment_evidence_method,
        model_id=model_id,
        persona_end_date=persona_end_date,
    )
