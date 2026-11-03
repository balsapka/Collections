"""A3 Payment Credibility – node functions, in pipeline.py order.

Spec: logs/A3_credibility_shared.xlsx, sheet "A3 framework" (validated against the
12-account "Tester" fixture, test_a3_v2_scoring.py). Three scored dimensions sum to
a3_points_total (0-5); a strong negative demotes the state one level; zero evidence
gives Unknown:
    A. Commitments kept          Broken / Kept(2) / Partly kept(1) / Thin  (DCORE PTP + settlement)
    B. Payments in delinquency   Regular(2) / Some(1) / None(0)  (Way4 billing + transactions)
    C. Record before delinquency Clean(1) / Not clean / No record  (Way4 billing + transactions)
    State: payment_credibility_{high, moderate, low, unknown}.

Nodes (output dataset = function name with "build_" -> "crx_cc_"):
    1. build_a3_commitment_signals          Dimension A: level, points, broken streak
    2. build_a3_strong_negative_signals     strong-negative evidence (rules run in node 9)
    3. build_a3_payment_cycles              shared cycle/payment/due ledger for B and C
    4-6. build_a3_dlq_payment_signals_*     Dimension B: payment_sum_waterfall (shadow),
                                            single_payment_cycle_count (default),
                                            dpd_bucket_movement (shadow)
    7-8. build_a3_pre_dlq_payment_signals_* Dimension C: single_payment_cycle_count
                                            (default), dpd_bucket_movement (shadow)
    9. build_a3_payment_credibility         combiner -> a3_state_v1

Every method of B and C is always computed (per-method columns in the output for
cross-checking); params:a3_dlq_payment_evidence_method and
params:a3_pre_dlq_payment_evidence_method independently pick the shipped one.
RL (rl_a3_payment_credibility) wraps these functions.

Notes:
  - Grain: (account_id, observation_date) from cc_spine; Dimension C is
    (account_id, spell_id) and joins on (account_id, t0).
  - Right-party classification uses result_name allowlists from
    cc_a3_payment_credibility.constants (result_category is unreliable: "SUC" contains
    refusals) and considers all action codes, IA included; only contact_dates_n is
    limited to call-type codes (OC/CB/IC).
  - due_amount_m (_signals_common.resolve_due_amount_m) is the highest-impact
    assumption in Dimensions B and C.
"""

# pylint: disable=too-many-lines, duplicate-code

# pylint: disable=too-many-lines, duplicate-code
import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._common import log_latest_month
from enbd_collections.pipelines.crx_persona._spine_utils import join_spine_to_spell
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility._signals_common import (
    attribute_payments_to_billing_cycles,
    filter_payment_cycles,
    resolve_dpd_bucket_movement_history,
    resolve_dlq_payment_window,
    resolve_bucket08_fallback_due,
    resolve_due_amount_m,
    resolve_pre_dlq_spell_window,
    resolve_dlq_waterfall_qualifying_months_cleared,
    aggregate_dlq_window,
    aggregate_pre_dlq_window,
    payment_meets_floor,
    flag_followups_after_refusal,
    flag_plans_on_record,
    pooled_trailing_broken_streak,
)
from enbd_collections.pipelines.crx_persona._dcore_codes import (
    CALL_CODES,
    PAYMENT_CONFIRMED,
    PROMISE_TO_PAY,
    REFUSING,
    RETAIN_PTP,
    RIGHT_PARTY_CONTACT,
)
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _CONF_HIGH,
    _CONF_LOW,
    _CONF_MODERATE,
    _CONF_UNKNOWN,
    _DLQ_LEVEL_SATURATED,
    _METHOD_DPD_BUCKET_MOVEMENT,
    _METHOD_PAYMENT_SUM_WATERFALL,
    _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    _SB_PRIORITY,
    _TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M,
    _TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP,
    _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
    _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180,
    _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS,
    _TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE,
    _TAU_A3V2_PRE_DLQ_CLEAN_SHARE,
    _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    _TAU_A3V2_COMMITMENTS_BROKEN_RATE,
    _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
    _TAU_A3V2_COMMITMENTS_KEPT_RATE,
    _TAU_A3V2_COMMITMENTS_MIN_CONCLUDED,
    _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS,
    _TAU_A3V2_HIGH_FROM_POINTS,
    _TAU_A3V2_MODERATE_FROM_POINTS,
    _TAU_MIN_CONTACT_DATES,
)

LOG = logging.getLogger(__name__)

# ── Required columns for schema guards ────────────────────────────────────

# Dimension A reads the 12-month instalment counts; each guard nulls only its own columns.
_PTP_COUNT_COLS = [
    "agreement_id",
    "observation_date",
    "ptp_instalment_due_cnt_12m",  # Dimension A concluded count
    "ptp_instalment_paid_cnt_12m",  # Dimension A kept count
]
_SETTLEMENT_COUNT_COLS = [
    "agreement_id",
    "observation_date",
    "settlement_instalment_due_cnt_12m",  # Dimension A concluded count
    "settlement_instalment_paid_cnt_12m",  # Dimension A kept count
]

# Canonical right-party disposition labels (last_rpc_disposition)
_DISP_PAID = "paid"
_DISP_PTP = "ptp"
_DISP_RTP = "rtp"
_DISP_SUCCESS = "success"


# ── Shared: spine → spell → DCORE agreement bridge ───────────────────────


def _build_agreement_bridge(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    caller: str,
) -> DataFrame:
    """(account_id, observation_date, iagreementseqno, cif_id, t0) for every spine row.

    cc_spine joined to the spell active at the observation date (t0), then to
    dcore_observation_spine for the DCORE agreement id. Used by nodes 1 and 2.

    Args:
        cc_spine: contract_id (= account_id), observation_date, cif_id (authoritative).
        spell_table: account_id, spell_id, t0, spell_end.
        observation_spine: account_id, observation_date, agreement_id, cif_id.
        caller: node name, for error and log messages.
    """
    _SPINE_REQUIRED = {"account_id", "observation_date", "agreement_id", "cif_id"}
    if not _SPINE_REQUIRED.issubset(set(observation_spine.columns)):
        missing = _SPINE_REQUIRED - set(observation_spine.columns)
        raise ValueError(
            f"{caller}: dcore_observation_spine missing columns {missing}."
        )

    # (account_id, observation_date, spell_id, t0) – shared equality-join pattern.
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    # cc_spine.cif_id is authoritative; observation_spine.cif_id is excluded below.
    spine_base = spine_with_spell.join(
        cc_spine.select(
            F.col("contract_id").alias("account_id"), "observation_date", "cif_id"
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    agreement_scope = observation_spine.select(
        "account_id",
        "observation_date",
        F.col("agreement_id").alias("iagreementseqno"),
    )
    # spell_id dropped – A3 grain is (account_id, observation_date)
    agreement_bridge = spine_base.join(
        agreement_scope, on=["account_id", "observation_date"], how="left"
    ).select("account_id", "observation_date", "iagreementseqno", "cif_id", "t0")

    n_rows = spine_base.count()
    n_with_agreement = agreement_bridge.filter(
        F.col("iagreementseqno").isNotNull()
    ).count()
    LOG.info(
        "%s: %d rows | agreement bridge: %d (%.1f%%)",
        caller,
        n_rows,
        n_with_agreement,
        100.0 * n_with_agreement / max(n_rows, 1),
    )
    return agreement_bridge


def _guarded_feat(feat: DataFrame, required_cols: list, name: str, caller: str):
    """feat if it has every required column and at least one row, else None (warned)."""
    present = set(feat.columns)
    if all(c in present for c in required_cols) and feat.limit(1).count() > 0:
        return feat
    LOG.warning(
        "%s: %s schema guard fired (missing=%s or empty) – its columns will be NULL.",
        caller,
        name,
        [c for c in required_cols if c not in present],
    )
    return None


# ── Node 1 – Dimension A: build_a3_commitment_signals ─────────────────────


def derive_commitments_level(df: DataFrame) -> DataFrame:
    """Dimension A: instalment counts and streak -> level and points.

    Concluded / kept are PTP + settlement instalments due / paid in the last 12 months
    (instalment level, not plan level – a plan-level bar of 2 whole plans left 79% of
    the population Thin). [CONFIRM] a deviation from the business "Tester" sheet, which
    was built on plan-level inputs.

    Level, checked in this order: Broken (last 3 concluded all broken, or >= 2
    concluded and kept-rate < 40%), Kept (>= 2 concluded, kept-rate >= 80%), Partly
    kept (>= 1 kept), else Thin. Pending instalments earn nothing (spec window rule).

    Needs ptp_/settlement_instalment_{due,paid}_cnt_12m and commitments_broken_streak
    (NULL counts as 0). Adds commitments_concluded / _kept / _kept_rate, the coalesced
    commitments_broken_streak, a3_commitments_level and a3_commitments_points
    (Kept 2, Partly kept 1, else 0).
    """
    kept = F.coalesce(F.col("ptp_instalment_paid_cnt_12m"), F.lit(0)) + F.coalesce(
        F.col("settlement_instalment_paid_cnt_12m"), F.lit(0)
    )
    concluded = F.coalesce(F.col("ptp_instalment_due_cnt_12m"), F.lit(0)) + F.coalesce(
        F.col("settlement_instalment_due_cnt_12m"), F.lit(0)
    )
    df = (
        df.withColumn("commitments_concluded", concluded)
        .withColumn("commitments_kept", kept)
        .withColumn(
            "commitments_kept_rate",
            F.when(concluded > 0, kept.cast("double") / concluded.cast("double")),
        )
        .withColumn(
            "commitments_broken_streak",
            F.coalesce(F.col("commitments_broken_streak"), F.lit(0)),
        )
    )
    rate = F.col("commitments_kept_rate")
    df = df.withColumn(
        "a3_commitments_level",
        F.when(
            (
                F.col("commitments_broken_streak")
                >= _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N
            )
            | (
                (F.col("commitments_concluded") >= 2)
                & rate.isNotNull()
                & (rate < _TAU_A3V2_COMMITMENTS_BROKEN_RATE)
            ),
            F.lit("broken"),
        )
        .when(
            (F.col("commitments_concluded") >= _TAU_A3V2_COMMITMENTS_MIN_CONCLUDED)
            & rate.isNotNull()
            & (rate >= _TAU_A3V2_COMMITMENTS_KEPT_RATE),
            F.lit("kept"),
        )
        .when(F.col("commitments_kept") >= 1, F.lit("partly_kept"))
        .otherwise(F.lit("thin")),
    )
    return df.withColumn(
        "a3_commitments_points",
        F.when(F.col("a3_commitments_level") == "kept", F.lit(2))
        .when(F.col("a3_commitments_level") == "partly_kept", F.lit(1))
        .otherwise(F.lit(0)),
    )


def build_a3_commitment_signals(  # pylint: disable=too-many-positional-arguments,too-many-locals
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    feat_ptp: DataFrame,
    feat_settlement: DataFrame,
    int_ptp: DataFrame = None,
    ptp_instalments: DataFrame = None,
    int_settlement: DataFrame = None,
    settlement_instalments: DataFrame = None,
) -> DataFrame:
    """Dimension A (commitments kept) per (account_id, observation_date).

    Steps: agreement bridge; 12-month PTP and settlement instalment counts from
    dcore_feat_ptp / dcore_feat_settlement (each guarded: missing columns or empty ->
    NULL counts); broken streak from the raw instalment tables
    (_signals_common.pooled_trailing_broken_streak, NULL when any is None); then
    derive_commitments_level.

    Args:
        cc_spine: master grain (account_id, observation_date, cif_id).
        spell_table: crx_cc_spell_table – t0 per spell.
        observation_spine: dcore_observation_spine – account -> agreement.
        feat_ptp / feat_settlement: dcore_feat_ptp / dcore_feat_settlement.
        int_ptp / ptp_instalments / int_settlement / settlement_instalments:
            dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments.

    Returns:
        (account_id, observation_date, iagreementseqno, t0, commitments_concluded,
        commitments_kept, commitments_kept_rate, commitments_broken_streak,
        a3_commitments_level, a3_commitments_points).
    """
    caller = "build_a3_commitment_signals"
    bridge = _build_agreement_bridge(cc_spine, spell_table, observation_spine, caller)
    keys = ["iagreementseqno", "observation_date"]

    result = bridge.select("account_id", "observation_date", "iagreementseqno", "t0")

    ptp = _guarded_feat(feat_ptp, _PTP_COUNT_COLS, "dcore_feat_ptp", caller)
    if ptp is None:
        result = result.withColumn(
            "ptp_instalment_due_cnt_12m", F.lit(None).cast("int")
        ).withColumn("ptp_instalment_paid_cnt_12m", F.lit(None).cast("int"))
    else:
        # AS-OF: one row per (agreement_id, obs_date).
        result = result.join(
            ptp.select(
                F.col("agreement_id").alias("iagreementseqno"),
                "observation_date",
                "ptp_instalment_due_cnt_12m",
                "ptp_instalment_paid_cnt_12m",
            ),
            on=keys,
            how="left",
        )

    settlement = _guarded_feat(
        feat_settlement, _SETTLEMENT_COUNT_COLS, "dcore_feat_settlement", caller
    )
    if settlement is None:
        result = result.withColumn(
            "settlement_instalment_due_cnt_12m", F.lit(None).cast("int")
        ).withColumn("settlement_instalment_paid_cnt_12m", F.lit(None).cast("int"))
    else:
        result = result.join(
            settlement.select(
                F.col("agreement_id").alias("iagreementseqno"),
                "observation_date",
                "settlement_instalment_due_cnt_12m",
                "settlement_instalment_paid_cnt_12m",
            ),
            on=keys,
            how="left",
        )

    # Built from the raw instalment tables, not dcore_feat_*: those carry only
    # plan-level / windowed aggregates, not the order of the latest instalments.
    if any(
        df is None
        for df in (int_ptp, ptp_instalments, int_settlement, settlement_instalments)
    ):
        LOG.warning(
            "%s: instalment tables not supplied – commitments_broken_streak is NULL.",
            caller,
        )
        result = result.withColumn("commitments_broken_streak", F.lit(None).cast("int"))
    else:
        streak = pooled_trailing_broken_streak(
            result, int_ptp, ptp_instalments, int_settlement, settlement_instalments
        )
        result = result.join(streak, on=keys, how="left")

    return derive_commitments_level(result).select(
        "account_id",
        "observation_date",
        "iagreementseqno",
        "t0",
        "commitments_concluded",
        "commitments_kept",
        "commitments_kept_rate",
        "commitments_broken_streak",
        "a3_commitments_level",
        "a3_commitments_points",
    )


# ── Node 2 – Strong negatives: build_a3_strong_negative_signals ──────────


def build_a3_strong_negative_signals(  # pylint: disable=too-many-positional-arguments,too-many-locals
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
    transactions: DataFrame = None,
) -> DataFrame:
    """Evidence for the strong negatives per (account_id, observation_date).

    Evidence only; the rules (broken commitments / refusal / no response) run in
    build_a3_payment_credibility, which holds Dimension A's level and Dimension B's
    any-payment flag.

    Steps: agreement bridge; contact evidence from dcore_prm_followup_outcomes
    (_aggregate_disposition); PTP / settlement on record since T0
    (_signals_common.flag_plans_on_record); what followed the latest refusal
    (_signals_common.flag_followups_after_refusal).

    Args:
        cc_spine / spell_table / observation_spine: as build_a3_commitment_signals.
        followup_outcomes: dcore_prm_followup_outcomes (agreement_id, action_ts,
            action_code, result_category, result_name).
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
        transactions: crx_cc_transactions. None (RL) -> the Refusal rule falls back to
            Dimension B's any-payment flag.

    Returns:
        (account_id, observation_date, contact_dates_n, rpc_confirmed, ptp_on_record_flag,
        arrangement_on_record_flag, last_rpc_disposition, refusal_followed_by_commitment,
        refusal_followed_by_payment, refusal_followed_by_payment_min_amount,
        payment_evidence_available).
    """
    caller = "build_a3_strong_negative_signals"
    bridge = _build_agreement_bridge(cc_spine, spell_table, observation_spine, caller)

    # ── Pass B: DCORE disposition signals ─────────────────────────────────
    _REQUIRED_FOLLOWUP_COLS = {
        "agreement_id",  # was iagreementseqno
        "action_ts",  # was szactiondate
        "action_code",  # OC/CB/IC/IA – used to restrict to call-type events
        "result_category",  # was szcategorycode
        "result_name",  # was szresultname – now carried directly, no join needed
    }

    followup_cols = set(followup_outcomes.columns)
    if not _REQUIRED_FOLLOWUP_COLS.issubset(followup_cols):
        missing = _REQUIRED_FOLLOWUP_COLS - followup_cols
        LOG.warning(
            "%s: dcore_prm_followup_outcomes missing columns %s – disposition signals "
            "will be all-NULL / zero.",
            caller,
            missing,
        )
        result = _null_disposition(bridge)
    elif followup_outcomes.limit(1).count() == 0:
        LOG.warning(
            "%s: dcore_prm_followup_outcomes is empty – disposition signals will be "
            "all-NULL / zero.",
            caller,
        )
        result = _null_disposition(bridge)
    else:
        result = _aggregate_disposition(bridge, followup_outcomes)

    # ── Pass C: PTP / settlement on record since T0 ───────────────────────
    result = flag_plans_on_record(result, int_ptp, int_settlement)

    # ── Pass D: what followed the latest right-party refusal ──────────────
    result = flag_followups_after_refusal(result, int_ptp, int_settlement, transactions)
    return result.drop("iagreementseqno", "cif_id", "t0", "last_rpc_date")


# ── helpers for node 2 ─────


def _null_disposition(base: DataFrame) -> DataFrame:
    """Return base with all disposition signal columns as NULL/zero."""
    return base.select(
        "account_id",
        "observation_date",
        "iagreementseqno",
        "t0",
        F.lit(None).cast("int").alias("contact_dates_n"),
        F.lit(0).cast("int").alias("rpc_confirmed"),
        F.lit(None).cast("string").alias("last_rpc_disposition"),
        F.lit(None).cast("date").alias("last_rpc_date"),
    )


def _aggregate_disposition(
    agreement_bridge: DataFrame, followup: DataFrame
) -> DataFrame:
    """Contact evidence per (account_id, observation_date) for the strong negatives.

    Window: [t0, observation_date); falls back to (-inf, observation_date)
    when t0 is NULL (no active spell) so real followup history still
    surfaces – see inline comment above the filter. result_name is carried
    directly on dcore_prm_followup_outcomes (no join required); allowlists from
    cc_a3_payment_credibility.constants are matched against result_name (upper-stripped).

    Outputs (added to the bridge columns):
        contact_dates_n      – distinct dates with a call-type action (OC outbound
                               call, CB callback, IC inbound call). 3 calls on one
                               day are weaker evidence than 3 separate days. No-response.
        rpc_confirmed        – 1 if any event matched RIGHT_PARTY_CONTACT
                               (result_category is not used: "SUC" is unreliable, it
                               contains refusals). No-response.
        last_rpc_disposition / last_rpc_date – the latest right-party event
                               (paid / rtp / ptp / success); Refusal.

    Right-party classification considers ALL action codes, including IA (internal
    action): confirmed payments and RETAIN PTP are frequently logged administratively
    rather than against a live call.

    Disposition waterfall (first match wins – order is load-bearing):
        _DISP_PAID    – PAYMENT_CONFIRMED (confirmed completed payment)
        _DISP_RTP     – REFUSING (explicit refusal/hang-up/dispute)
        _DISP_PTP     – PROMISE_TO_PAY | RETAIN_PTP
        _DISP_SUCCESS – RIGHT_PARTY_CONTACT (cooperative contact not
                        already claimed above)
    Anything else (unreachable, ringing, unclassified) is not a right-party event.
    """

    # Window [t0, observation_date). A NULL t0 (no active spell) is an unbounded lower
    # bound: comparing against NULL would drop every event and turn "window unknown"
    # into a false "no contact".
    window_events = (
        followup.select(
            F.col("agreement_id").alias("iagreementseqno"),
            F.col("action_ts").cast("date").alias("szactiondate"),
            F.col("action_code"),
            F.col("result_category").alias("szcategorycode"),
            "result_name",
        )
        .join(
            agreement_bridge.select(
                "account_id", "observation_date", "t0", "iagreementseqno"
            ),
            on="iagreementseqno",
            how="inner",
        )
        .filter(
            (F.col("t0").isNull() | (F.col("szactiondate") >= F.col("t0")))
            & (F.col("szactiondate") < F.col("observation_date"))
        )
        .withColumn("_result_name_upper", F.upper(F.trim(F.col("result_name"))))
        # Tags call-type events for the attempt-volume counters only
        # (contact_attempts_n / contact_dates_n) – disposition classification
        # below is intentionally NOT restricted by this flag.
        .withColumn("_is_call_code", F.col("action_code").isin(*CALL_CODES))
    )

    # Classify each event; a NULL _disp is not a right-party contact. Order is
    # load-bearing: PAID first, RTP next so refusals inside _RIGHT_PARTY_CONTACT are
    # not mis-classified as SUCCESS, PTP before SUCCESS for the same reason.
    window_with_disp = window_events.withColumn(
        "_disp",
        F.when(
            F.col("_result_name_upper").isin(*PAYMENT_CONFIRMED),
            F.lit(_DISP_PAID),
        )
        .when(F.col("_result_name_upper").isin(*REFUSING), F.lit(_DISP_RTP))
        .when(
            F.col("_result_name_upper").isin(*PROMISE_TO_PAY)
            | F.col("_result_name_upper").isin(*RETAIN_PTP),
            F.lit(_DISP_PTP),
        )
        .when(
            F.col("_result_name_upper").isin(*RIGHT_PARTY_CONTACT),
            F.lit(_DISP_SUCCESS),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    # Latest right-party contact. On the same date a non-refusal ranks as later: a
    # same-day promise followed the refusal.
    last_rpc = (
        window_with_disp.filter(F.col("_disp").isNotNull())
        .withColumn(
            "_rpc_rn",
            F.row_number().over(
                Window.partitionBy("account_id", "observation_date").orderBy(
                    F.col("szactiondate").desc(),
                    F.when(F.col("_disp") == _DISP_RTP, 1).otherwise(0),
                )
            ),
        )
        .filter(F.col("_rpc_rn") == 1)
        .select(
            "account_id",
            "observation_date",
            F.col("_disp").alias("last_rpc_disposition"),
            F.col("szactiondate").alias("last_rpc_date"),
        )
    )

    agg = window_with_disp.groupBy("account_id", "observation_date").agg(
        F.countDistinct(F.when(F.col("_is_call_code"), F.col("szactiondate")))
        .cast("int")
        .alias("contact_dates_n"),
        F.max(
            F.when(
                F.col("_result_name_upper").isin(*RIGHT_PARTY_CONTACT),
                F.lit(1),
            ).otherwise(F.lit(0))
        )
        .cast("int")
        .alias("rpc_confirmed"),
    )

    return (
        agreement_bridge.join(agg, on=["account_id", "observation_date"], how="left")
        .join(last_rpc, on=["account_id", "observation_date"], how="left")
        .fillna({"contact_dates_n": 0, "rpc_confirmed": 0})
        # fillna turned "no DCORE agreement at all" into 0 contact dates; restore NULL to
        # tell it apart from "agreement found but no call-type event in the window"
        # (the no_response rule requires a non-NULL contact_dates_n).
        .withColumn(
            "contact_dates_n",
            F.when(
                F.col("iagreementseqno").isNull(), F.lit(None).cast("int")
            ).otherwise(F.col("contact_dates_n")),
        )
    )


# ── Node 3 – build_a3_payment_cycles (shared by Dimensions B and C) ──────


def build_a3_payment_cycles(
    crx_cc_billing: DataFrame,
    crx_cc_balance: DataFrame,
    crx_cc_transactions: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Billing-cycle payment attribution and due-amount resolution, run once for B and C.

    A cycle runs to the next existing statement, so cycles spanning missing statements
    (e.g. the 2021-2023 billing gap) are dropped: those starting more than 35 days before
    history_floor_date and those longer than 62 days
    (_signals_common.filter_payment_cycles).

    Args:
        crx_cc_billing: billing_date, due_date, next_billing_date.
        crx_cc_balance: minimum_due, overdue_bucket_01..08, total_due.
        crx_cc_transactions: payment transactions (txn_category, is_post_block_x_fee).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, billing_date) with due_date, next_billing_date,
        payment_sum_in_cycle, on_time_payment_sum_in_cycle
        (resolve_due_amount_m), due_amount_fallback_m (the account's frozen baseline on
        statements where only overdue_bucket_08 is left, else NULL;
        resolve_bucket08_fallback_due; read only by the Dimension B default method) and
        waterfall_qualifying_months_cleared_m (Dimension B's lumpsum-aware count,
        resolve_dlq_waterfall_qualifying_months_cleared).
    """
    cycles_raw = filter_payment_cycles(
        attribute_payments_to_billing_cycles(crx_cc_billing, crx_cc_transactions),
        history_floor_date,
    )
    cycles = cycles_raw.withColumnRenamed("contract_id", "account_id")

    balance_due = resolve_due_amount_m(crx_cc_balance)
    qualifying_months = resolve_dlq_waterfall_qualifying_months_cleared(
        crx_cc_balance,
        cycles_raw,
        _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
        bucket08_baseline_lookback_m=_TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M,
        bucket08_max_split=_TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP,
    )

    return (
        cycles.join(balance_due, on=["account_id", "billing_date"], how="left")
        .join(
            resolve_bucket08_fallback_due(crx_cc_balance),
            on=["account_id", "billing_date"],
            how="left",
        )
        .join(qualifying_months, on=["account_id", "billing_date"], how="left")
    )


# ── Nodes 4-6 – Dimension B: payments in delinquency ─────────────────────


def _dlq_payment_level_and_points(agg: DataFrame) -> DataFrame:
    """Dimension B ladder shared by the methods: regular / some / none, points 2 / 1 / 0."""
    result = agg.withColumn(
        "dlq_payment_level",
        F.when(
            (
                (
                    F.col("dlq_payment_window_months")
                    == _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS
                )
            )
            | (
                (
                    F.col("dlq_payment_window_months")
                    != _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180
                )
            ),
            F.lit("regular"),
        )
        .when(F.col("dlq_payment_any_flag") == 1, F.lit("some"))
        .otherwise(F.lit("none")),
    )
    return result.withColumn(
        "dlq_payment_points",
        F.when(F.col("dlq_payment_level") == "regular", F.lit(2))
        .when(F.col("dlq_payment_level") == "some", F.lit(1))
        .otherwise(F.lit(0)),
    )


def _dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Typed output select shared by the three Dimension B methods."""
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


def build_a3_dlq_payment_signals_payment_sum_waterfall(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, payment_sum_waterfall method (shadow): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    A lumpsum that clears several overdue buckets credits several months
    (waterfall_qualifying_months_cleared_m). Amount-only, no due-date check.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    agg = aggregate_dlq_window(
        spine_with_window,
        crx_cc_a3_payment_cycles.filter(F.col("next_billing_date").isNotNull()),
        "next_billing_date",
        # 180+ (_min_payment_aed = 100): a cycle credits months only if its payment is
        # at least 100 AED; 61-180 has no floor.
        F.when(
            payment_meets_floor(F.col("c.payment_sum_in_cycle")),
            F.coalesce(F.col("c.waterfall_qualifying_months_cleared_m"), F.lit(0)),
        ).otherwise(F.lit(0)),
        (F.col("c.payment_sum_in_cycle") > 0)
        & payment_meets_floor(F.col("c.payment_sum_in_cycle")),
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


def build_a3_dlq_payment_signals_single_payment_cycle_count(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, single_payment_cycle_count method (default): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    Each cycle is judged on its own: qualifying when payment_sum_in_cycle >=
    max(due x share, minimum payment); no multi-month credit from one lumpsum.
    Rule: 2+ qualifying months of 3 (61-180), 3+ of 6 (180+). The due is due_amount_m, or
    for a statement where only overdue_bucket_08 is left the account's frozen baseline
    (due_amount_fallback_m); NULL when neither exists, and the cycle cannot qualify.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    cycles_with_evidence = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    )
    if "due_amount_fallback_m" not in cycles_with_evidence.columns:
        cycles_with_evidence = cycles_with_evidence.withColumn(
            "due_amount_fallback_m", F.lit(None).cast("double")
        )

    # Due = due_amount_m, else the frozen bucket-08 baseline.
    _due = F.coalesce(F.col("c.due_amount_m"), F.col("c.due_amount_fallback_m"))
    # Required payment = max(100% of the due, the 180+ minimum payment): at 180+ a tiny
    # due cannot be cleared by a token payment (_min_payment_aed = 0 at 61-180).
    _required_payment = F.greatest(
        _due * F.lit(_TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE),
        F.col("s._min_payment_aed"),
    )
    _is_qualifying_cycle = F.when(
        _due.isNotNull() & (_due > 0),
        F.col("c.payment_sum_in_cycle") >= _required_payment,
    ).otherwise(F.lit(False))

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "next_billing_date",
        _is_qualifying_cycle.cast("int"),
        (F.col("c.payment_sum_in_cycle") > 0)
        & payment_meets_floor(F.col("c.payment_sum_in_cycle")),
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


def build_a3_dlq_payment_signals_dpd_bucket_movement(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_full_history: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, dpd_bucket_movement method (shadow): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    Infers payment from month-over-month DLQ bucket movement. Per statement, the bucket
    (crx_cc_full_history via resolve_dpd_bucket_movement_history) already reflects cash
    received since the previous statement, so it is compared with the previous row:
        no previous cycle                  -> 0
        improved (level < prev)            -> prev - level, +1 unless fully cured (level 0)
        flat, nonzero, below the cap       -> 1
        flat at zero                       -> 0 (cannot tell dormant from paying on time)
        flat at the cap (9)                -> ambiguous; the waterfall count for that cycle
        worsened                           -> 0
    The +1 offsets the bucket index being net of the cycle's own new unpaid minimum due.
    Bucket credits carry no amount, so the 100 AED floor applies only to the cap fallback.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_full_history: account_id, billing_date, dlq_bucket.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    qualifying_months_by_evidence_date = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    ).select(
        "account_id",
        F.col("next_billing_date").alias("billing_date"),
        "waterfall_qualifying_months_cleared_m",
        F.col("payment_sum_in_cycle").alias("_cycle_payment_sum"),
    )
    dlq_bucket_history = resolve_dpd_bucket_movement_history(
        crx_cc_full_history, history_floor_date
    ).join(
        qualifying_months_by_evidence_date,
        on=["account_id", "billing_date"],
        how="left",
    )

    _dlq_levels_improved = F.col("dlq_level_prev_m") - F.col("dlq_level_m")
    # +1 unless this row is fully cured (see docstring).
    _improved_credit = F.when(
        F.col("dlq_level_m") == 0, _dlq_levels_improved
    ).otherwise(_dlq_levels_improved + 1)
    cycles_with_evidence = dlq_bucket_history.withColumn(
        "_qualifying_months_m",
        F.when(F.col("dlq_level_prev_m").isNull(), F.lit(0))
        .when(_dlq_levels_improved > 0, _improved_credit)
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") < _DLQ_LEVEL_SATURATED)
            & (F.col("dlq_level_m") != 0),
            F.lit(1),
        )
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") == _DLQ_LEVEL_SATURATED),
            F.coalesce(F.col("waterfall_qualifying_months_cleared_m"), F.lit(0)),
        )
        .otherwise(F.lit(0)),
    ).withColumn(
        "_is_cap_fallback",
        (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
        & (F.col("dlq_level_m") == _DLQ_LEVEL_SATURATED),
    )

    # Bucket-movement credits carry no amount, so the 180+ minimum payment (100 AED)
    # applies only to the amount-based fallback at the bucket cap.
    _months = F.when(
        F.col("c._is_cap_fallback")
        & ~payment_meets_floor(F.coalesce(F.col("c._cycle_payment_sum"), F.lit(0.0))),
        F.lit(0),
    ).otherwise(F.col("c._qualifying_months_m"))

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "billing_date",
        _months,
        _months >= 1,
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


# ── Nodes 7-8 – Dimension C: record before delinquency ───────────────────


def _pre_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Typed output select shared by the two Dimension C methods."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("pre_dlq_months_due_n").cast("int"),
        F.col("pre_dlq_months_paid_as_billed_n").cast("int"),
        F.col("pre_dlq_paid_as_billed_share").cast("double"),
    )


def build_a3_pre_dlq_payment_signals_single_payment_cycle_count(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension C, single_payment_cycle_count method (default): did they pay as billed
    before delinquency started?

    Window: the 12 months strictly before t0, never mixed with post-onset months. "Paid as
    billed" = payment_sum_in_cycle >= _TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE (strict 100%) x
    due_amount_m. Cycles are keyed on next_billing_date (the statement that shows the
    result); cycles without one are excluded.

    [TEMPORARY, 2026-10-21] The check ignores the due date (whole-cycle payment, not
    on_time_payment_sum_in_cycle) so both Dimension C methods answer the same question;
    the due-date-sensitive version disagreed with dpd_bucket_movement on 39% of rows.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: population filter only – drops spells not in the current model_id
            population; the window itself is purely t0-anchored.
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, spell_id): t0, pre_dlq_months_due_n, pre_dlq_months_paid_as_billed_n,
        pre_dlq_paid_as_billed_share (NULL below _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, the
        "No record" condition).
    """
    spells = resolve_pre_dlq_spell_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    cycles_with_due = (
        crx_cc_a3_payment_cycles.filter(F.col("next_billing_date").isNotNull())
        .withColumn(
            "_has_due",
            F.col("due_amount_m").isNotNull() & (F.col("due_amount_m") > 0),
        )
        .withColumn(
            "_paid_on_time",
            F.when(
                F.col("_has_due"),
                # Strict 100% of due; ignores the due date (see docstring).
                F.col("payment_sum_in_cycle")
                >= F.col("due_amount_m") * F.lit(_TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE),
            ).otherwise(F.lit(False)),
        )
    )

    result = aggregate_pre_dlq_window(spells, cycles_with_due, "_paid_on_time")

    return _pre_dlq_payment_signals_output(result)


def build_a3_pre_dlq_payment_signals_dpd_bucket_movement(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_full_history: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension C, dpd_bucket_movement method (shadow): did they pay as billed before
    delinquency started?

    Same window and months_due denominator as the single_payment_cycle_count method. A
    cycle is "paid as billed" when the resulting statement's dlq_bucket
    (crx_cc_full_history at next_billing_date, the row that shows the result) is <= 1,
    i.e. the account did not fall into an overdue bucket. Level-only, so there is no
    flat-bucket ambiguity.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_full_history: account_id, billing_date, dlq_bucket.
        crx_cc_spell_table: t0 per spell.
        cc_spine: population filter only – drops spells not in the current model_id
            population; the window itself is purely t0-anchored.
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, spell_id): t0, pre_dlq_months_due_n, pre_dlq_months_paid_as_billed_n,
        pre_dlq_paid_as_billed_share (NULL below _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, the
        "No record" condition).
    """
    spells = resolve_pre_dlq_spell_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    resulting_dlq_bucket = crx_cc_full_history.select(
        F.col("account_id").alias("_evidence_account_id"),
        F.col("billing_date").alias("_evidence_date"),
        F.col("dlq_bucket").alias("_resulting_dlq_bucket"),
    )
    base = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    ).withColumn(
        "_has_due",
        F.col("due_amount_m").isNotNull() & (F.col("due_amount_m") > 0),
    )
    cycles_with_evidence = base.join(
        resulting_dlq_bucket,
        (base["account_id"] == resulting_dlq_bucket["_evidence_account_id"])
        & (base["next_billing_date"] == resulting_dlq_bucket["_evidence_date"]),
        "left",
    ).withColumn(
        "_paid_as_billed",
        F.col("_resulting_dlq_bucket").isNotNull()
        & (F.col("_resulting_dlq_bucket") <= 1),
    )

    result = aggregate_pre_dlq_window(spells, cycles_with_evidence, "_paid_as_billed")

    return _pre_dlq_payment_signals_output(result)


# ── Node 9 – build_a3_payment_credibility (combiner) ─────────────────────

_DLQ_PAIR_COLUMNS = {
    "dlq_payment_window_months": "int",
    "dlq_payment_any_window_months": "int",
    "dlq_payment_qualifying_month_cnt": "int",
    "dlq_payment_any_flag": "int",
    "dlq_payment_level": "string",
    "dlq_payment_points": "int",
}
_PRE_DLQ_PAIR_COLUMNS = {
    "pre_dlq_months_due_n": "int",
    "pre_dlq_months_paid_as_billed_n": "int",
    "pre_dlq_paid_as_billed_share": "double",
}
_STATE_HIGH = "payment_credibility_high"
_STATE_MODERATE = "payment_credibility_moderate"
_STATE_LOW = "payment_credibility_low"
_STATE_UNKNOWN = "payment_credibility_unknown"


def _join_signals_pair(
    df: DataFrame, pair: DataFrame, join_keys: list, columns: dict, approach: str
) -> DataFrame:
    """Left-join one approach's signals onto df, suffixing each column with the approach.

    A None pair, or a column the pair lacks, becomes a typed NULL so the column set
    is the same whichever pairs were supplied.
    """
    renamed = [
        (
            F.col(name)
            if pair is not None and name in pair.columns
            else F.lit(None).cast(dtype)
        ).alias(f"{name}_{approach}")
        for name, dtype in columns.items()
    ]
    if pair is None:
        return df.select("*", *renamed)
    return df.join(pair.select(*join_keys, *renamed), on=join_keys, how="left")


def _validate_method_pairs(
    dlq_pairs: dict,
    pre_dlq_pairs: dict,
    dlq_payment_evidence_method: str,
    pre_dlq_payment_evidence_method: str,
) -> None:
    """Reject unknown method names and a shipped method whose signals were not supplied.

    A missing shipped pair would otherwise be NULL-filled and silently ship as level
    "none" / "no_record" for every row. Shadow pairs stay optional.
    """
    checks = (
        (
            "dlq_payment_evidence_method",
            dlq_payment_evidence_method,
            dlq_pairs,
            "dlq_payment_signals_*",
        ),
        (
            "pre_dlq_payment_evidence_method",
            pre_dlq_payment_evidence_method,
            pre_dlq_pairs,
            "pre_dlq_payment_signals_*",
        ),
    )
    for param, method, pairs, _ in checks:
        if method not in pairs:
            raise ValueError(
                f"build_a3_payment_credibility: {param} must be one of "
                f"{list(pairs)}, got {method!r}."
            )
    for param, method, pairs, inputs in checks:
        if pairs[method] is None:
            raise ValueError(
                f"build_a3_payment_credibility: {param}={method!r} selects an "
                f"approach whose {inputs} input was not supplied."
            )


def _score_dimension_b(df: DataFrame, approaches) -> DataFrame:
    """Per-approach Dimension B level (NULL -> "none"), points (NULL -> 0) and count."""
    for approach in approaches:
        df = (
            df.withColumn(
                f"a3_dlq_payment_level_{approach}",
                F.coalesce(F.col(f"dlq_payment_level_{approach}"), F.lit("none")),
            )
            .withColumn(
                f"a3_dlq_payment_points_{approach}",
                F.coalesce(F.col(f"dlq_payment_points_{approach}"), F.lit(0)),
            )
            .withColumn(
                f"a3_dlq_payment_qualifying_month_cnt_{approach}",
                F.col(f"dlq_payment_qualifying_month_cnt_{approach}"),
            )
        )
    return df


def _pre_dlq_payment_level_col(months_due_col: Column, share_col: Column) -> Column:
    """Dimension C ladder: no_record (too few billed months) / clean / not_clean."""
    return (
        F.when(
            months_due_col.isNull()
            | (months_due_col < _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE),
            F.lit("no_record"),
        )
        .when(share_col >= _TAU_A3V2_PRE_DLQ_CLEAN_SHARE, F.lit("clean"))
        .otherwise(F.lit("not_clean"))
    )


def _score_dimension_c(df: DataFrame, approaches) -> DataFrame:
    """Per-approach Dimension C level, points (Clean 1, else 0) and months due."""
    for approach in approaches:
        df = (
            df.withColumn(
                f"a3_pre_dlq_payment_level_{approach}",
                _pre_dlq_payment_level_col(
                    F.col(f"pre_dlq_months_due_n_{approach}"),
                    F.col(f"pre_dlq_paid_as_billed_share_{approach}"),
                ),
            )
            .withColumn(
                f"a3_pre_dlq_payment_points_{approach}",
                F.when(
                    F.col(f"a3_pre_dlq_payment_level_{approach}") == "clean", F.lit(1)
                ).otherwise(F.lit(0)),
            )
            .withColumn(
                f"a3_pre_dlq_months_due_n_{approach}",
                F.col(f"pre_dlq_months_due_n_{approach}"),
            )
        )
    return df


def _select_shipped_methods(
    df: DataFrame, dlq_method: str, pre_dlq_method: str
) -> DataFrame:
    """Unsuffixed shipped Dimension B / C columns plus a3_points_total."""
    b, c = dlq_method, pre_dlq_method
    return (
        df.withColumn("a3_dlq_payment_level", F.col(f"a3_dlq_payment_level_{b}"))
        .withColumn("a3_dlq_payment_points", F.col(f"a3_dlq_payment_points_{b}"))
        .withColumn(
            "a3_dlq_payment_qualifying_month_cnt",
            F.col(f"a3_dlq_payment_qualifying_month_cnt_{b}"),
        )
        .withColumn(
            "a3_dlq_payment_window_months", F.col(f"dlq_payment_window_months_{b}")
        )
        .withColumn(
            "a3_dlq_payment_any_window_months",
            F.col(f"dlq_payment_any_window_months_{b}"),
        )
        .withColumn("a3_pre_dlq_payment_level", F.col(f"a3_pre_dlq_payment_level_{c}"))
        .withColumn(
            "a3_pre_dlq_payment_points", F.col(f"a3_pre_dlq_payment_points_{c}")
        )
        .withColumn("a3_pre_dlq_months_due_n", F.col(f"a3_pre_dlq_months_due_n_{c}"))
        .withColumn(
            "a3_points_total",
            F.col("a3_commitments_points")
            + F.col("a3_dlq_payment_points")
            + F.col("a3_pre_dlq_payment_points"),
        )
    )


def _strong_negative_reason(dlq_payment_evidence_method: str) -> Column:
    """Strong-negative reason per row, or NULL (framework block 3; one reason, no stacking).

    broken_commitments: Dimension A is Broken. refusal: the latest right-party contact
    was a refusal and nothing followed it. no_response: 3+ contact dates without
    reaching the customer, no promise / arrangement, no payment in the window. When
    several fire, _SB_PRIORITY picks the reason. Needs a3_commitments_level and
    commitments_concluded (Dimension A), the strong-negative evidence columns and
    Dimension B's shipped any-payment flag / window.
    """
    # No-response uses Dimension B's shipped any-payment flag (3 months at 61-180, 12 at
    # 180+).
    _dlq_any_flag_shipped = F.col(f"dlq_payment_any_flag_{dlq_payment_evidence_method}")
    _sn_broken_commitments = F.col("a3_commitments_level") == "broken"
    # Refusal: latest right-party contact was a refusal, with no later promise or
    # arrangement and no later payment (100 AED floor at 180+). Without card
    # transactions (RL) the payment test is Dimension B's any-payment flag.
    _is_180_plus = (
        F.col(f"dlq_payment_any_window_months_{dlq_payment_evidence_method}")
        == _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS
    )
    _payment_followed_refusal = F.when(
        F.coalesce(F.col("payment_evidence_available"), F.lit(0)) == 1,
        F.when(
            _is_180_plus,
            F.coalesce(F.col("refusal_followed_by_payment_min_amount"), F.lit(0)) == 1,
        ).otherwise(F.coalesce(F.col("refusal_followed_by_payment"), F.lit(0)) == 1),
    ).otherwise(F.coalesce(_dlq_any_flag_shipped, F.lit(0)) == 1)
    _sn_refusal = (
        (F.col("last_rpc_disposition") == _DISP_RTP)
        & (F.coalesce(F.col("refusal_followed_by_commitment"), F.lit(0)) == 0)
        & ~_payment_followed_refusal
    )
    _sn_no_response = (
        F.col("contact_dates_n").isNotNull()
        & (F.col("contact_dates_n") >= _TAU_MIN_CONTACT_DATES)
        & (F.coalesce(F.col("rpc_confirmed"), F.lit(0)) == 0)
        & (F.col("commitments_concluded") == 0)
        & (F.coalesce(F.col("ptp_on_record_flag"), F.lit(0)) == 0)
        & (F.coalesce(F.col("arrangement_on_record_flag"), F.lit(0)) == 0)
        & (F.coalesce(_dlq_any_flag_shipped, F.lit(0)) == 0)
    )

    # Priority order (for the rare case more than one fires) is driven by
    # _SB_PRIORITY – the single source of truth, instead of duplicating the
    # order here.
    _sn_conditions = {
        "broken_commitments": _sn_broken_commitments,
        "refusal": _sn_refusal,
        "no_response": _sn_no_response,
    }
    _sn_reason_expr = F.lit(None).cast("string")
    for _reason in reversed(_SB_PRIORITY):
        _sn_reason_expr = F.when(_sn_conditions[_reason], F.lit(_reason)).otherwise(
            _sn_reason_expr
        )
    _sn_reason_expr = F.lit(None).cast("string")
    for _reason in reversed(_SB_PRIORITY):
        _sn_reason_expr = F.when(_sn_conditions[_reason], F.lit(_reason)).otherwise(
            _sn_reason_expr
        )
    return _sn_reason_expr


def _a3_state_col(
    level_a: Column,
    level_b: Column,
    level_c: Column,
    points_total: Column,
    has_strong_negative: Column,
) -> Column:
    """State ladder, checked in order: Unknown, High, Moderate, else Low.

    Unknown: A thin, B none, C no_record and no strong negative (zero evidence, distinct
    from Low – evidence exists and it is bad; a pending PTP alone is still Thin).
    High: points >= HIGH and no strong negative. Moderate: points >= MODERATE and no
    strong negative, or points >= HIGH knocked down one level by a strong negative.
    """
    no_sn = ~has_strong_negative
    is_unknown = (
        (level_a == "thin") & (level_b == "none") & (level_c == "no_record") & no_sn
    )
    return (
        F.when(is_unknown, F.lit(_STATE_UNKNOWN))
        .when((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & no_sn, F.lit(_STATE_HIGH))
        .when(
            ((points_total >= _TAU_A3V2_MODERATE_FROM_POINTS) & no_sn)
            | ((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & has_strong_negative),
            F.lit(_STATE_MODERATE),
        )
        .otherwise(F.lit(_STATE_LOW))
    )


def _a3_output(df: DataFrame, dlq_method: str, pre_dlq_method: str) -> DataFrame:
    """State, path, confidence, provenance and the typed output select."""
    df = df.withColumn(
        "a3_state_v1",
        _a3_state_col(
            F.col("a3_commitments_level"),
            F.col("a3_dlq_payment_level"),
            F.col("a3_pre_dlq_payment_level"),
            F.col("a3_points_total"),
            F.col("_has_strong_negative"),
        ),
    )
    df = df.withColumn(
        "a3_path",
        F.concat_ws(
            "|",
            F.col("a3_commitments_level"),
            F.col("a3_dlq_payment_level"),
            F.col("a3_pre_dlq_payment_level"),
            F.coalesce(F.col("a3_strong_negative_reason"), F.lit("none")),
        ),
    )
    df = df.withColumn(
        "a3_confidence",
        F.when(F.col("a3_state_v1") == _STATE_HIGH, F.lit(_CONF_HIGH))
        .when(F.col("a3_state_v1") == _STATE_MODERATE, F.lit(_CONF_MODERATE))
        .when(F.col("a3_state_v1") == _STATE_LOW, F.lit(_CONF_LOW))
        .otherwise(F.lit(_CONF_UNKNOWN)),
    )
    # Every non-Unknown state rests on concrete points or a strong negative (observed
    # behaviour). [CONFIRM: simplified]
    df = df.withColumn(
        "a3_provenance",
        F.when(F.col("a3_state_v1") == _STATE_UNKNOWN, F.lit("unknown")).otherwise(
            F.lit("observed")
        ),
    )
    return df.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("t0").cast("date"),
        F.col("a3_state_v1").cast("string"),
        F.col("a3_path").cast("string"),
        F.col("a3_confidence").cast("double"),
        F.col("a3_provenance").cast("string"),
        # Dimension breakdown
        F.col("a3_commitments_level").cast("string"),
        F.col("a3_dlq_payment_level").cast("string"),
        F.col("a3_pre_dlq_payment_level").cast("string"),
        F.col("a3_commitments_points").cast("int"),
        F.col("a3_dlq_payment_points").cast("int"),
        F.col("a3_pre_dlq_payment_points").cast("int"),
        F.col("a3_points_total").cast("int"),
        F.col("a3_strong_negative_reason").cast("string"),
        F.col("a3_dlq_payment_window_months").cast("int"),
        F.col("a3_dlq_payment_any_window_months").cast("int"),
        # Track the shipped methods; the per-method columns below are method-pinned.
        F.col("a3_dlq_payment_qualifying_month_cnt").cast("int"),
        F.col("a3_pre_dlq_months_due_n").cast("int"),
        # Per-method correlation columns (all methods are always computed).
        F.lit(pre_dlq_method).alias("a3_pre_dlq_payment_evidence_method"),
        F.lit(dlq_method).alias("a3_dlq_payment_evidence_method"),
        F.col("a3_dlq_payment_level_single_payment_cycle_count").cast("string"),
        F.col("a3_dlq_payment_qualifying_month_cnt_single_payment_cycle_count").cast(
            "int"
        ),
        F.col("a3_dlq_payment_level_payment_sum_waterfall").cast("string"),
        F.col("a3_dlq_payment_level_dpd_bucket_movement").cast("string"),
        F.col("a3_pre_dlq_payment_level_single_payment_cycle_count").cast("string"),
        F.col("a3_pre_dlq_payment_level_dpd_bucket_movement").cast("string"),
        F.col("a3_dlq_payment_qualifying_month_cnt_payment_sum_waterfall").cast("int"),
        F.col("a3_dlq_payment_qualifying_month_cnt_dpd_bucket_movement").cast("int"),
        F.col("a3_pre_dlq_months_due_n_single_payment_cycle_count").cast("int"),
        F.col("a3_pre_dlq_months_due_n_dpd_bucket_movement").cast("int"),
        # Strong-negative evidence
        F.col("contact_dates_n").cast("int"),
        F.col("rpc_confirmed").cast("int"),
        F.col("last_rpc_disposition").cast("string"),
        F.col("refusal_followed_by_commitment").cast("int"),
        F.col("ptp_on_record_flag").cast("int"),
        F.col("arrangement_on_record_flag").cast("int"),
        F.col("commitments_broken_streak").cast("int"),
        F.current_timestamp().cast("string").alias("computed_at"),
    )


def build_a3_payment_credibility(  # pylint: disable=too-many-positional-arguments,too-many-arguments,too-many-locals
    commitment_signals: DataFrame,
    negative_signals: DataFrame,
    dlq_payment_signals_payment_sum_waterfall: DataFrame = None,
    dlq_payment_signals_single_payment_cycle_count: DataFrame = None,
    dlq_payment_signals_dpd_bucket_movement: DataFrame = None,
    pre_dlq_payment_signals_single_payment_cycle_count: DataFrame = None,
    pre_dlq_payment_signals_dpd_bucket_movement: DataFrame = None,
    dlq_payment_evidence_method: str = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    pre_dlq_payment_evidence_method: str = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    model_id: str = None,
    persona_end_date: str = None,
) -> DataFrame:
    """Combine Dimensions A, B, C and the strong negatives into a3_state_v1.

    Dimension A's level and points come from commitment_signals; B and C from their
    per-method signal tables. Each method of B (3) and C (2) is scored into suffixed
    columns for cross-checking; dlq_payment_evidence_method and
    pre_dlq_payment_evidence_method (independent switches) pick the shipped one. The
    strong-negative rules (_strong_negative_reason) read Dimension B's shipped
    any-payment flag. [CONFIRM: simplification – acceptable for the shadow columns,
    not independently recomputed per method]

    State (see _a3_state_col): Unknown / High / Moderate / Low. The old waterfall's
    pre-rule guards (window too short, no DCORE data) are deliberately gone; Unknown is
    the single "insufficient evidence" gate.

    Signal inputs default to None for domains without that source; the SELECTED
    approach's input must be supplied (ValueError otherwise). Keep the defaults:
    rl_a3_payment_credibility passes its own pairs.

    Args:
        commitment_signals: crx_cc_a3_commitment_signals – (account_id,
            observation_date) Dimension A level, points and streak.
        negative_signals: crx_cc_a3_strong_negative_signals – same grain; the
            strong-negative evidence.
        dlq_payment_signals_payment_sum_waterfall / _single_payment_cycle_count /
        _dpd_bucket_movement: Dimension B methods, (account_id, observation_date).
        pre_dlq_payment_signals_single_payment_cycle_count / _dpd_bucket_movement:
            Dimension C methods, (account_id, spell_id), joined on (account_id, t0).
        dlq_payment_evidence_method: "single_payment_cycle_count" (default),
            "payment_sum_waterfall" or "dpd_bucket_movement".
        pre_dlq_payment_evidence_method: "single_payment_cycle_count" (default) or
            "dpd_bucket_movement".
        model_id / persona_end_date: when both are given, log the latest month's
            a3_state_v1 distribution.

    Returns:
        (account_id, observation_date) typed A3 output; a3_state_v1 in
        payment_credibility_{high, moderate, low, unknown}.
    """
    dlq_pairs = {
        _METHOD_PAYMENT_SUM_WATERFALL: dlq_payment_signals_payment_sum_waterfall,
        _METHOD_SINGLE_PAYMENT_CYCLE_COUNT: (
            dlq_payment_signals_single_payment_cycle_count
        ),
        _METHOD_DPD_BUCKET_MOVEMENT: dlq_payment_signals_dpd_bucket_movement,
    }
    pre_dlq_pairs = {
        _METHOD_SINGLE_PAYMENT_CYCLE_COUNT: (
            pre_dlq_payment_signals_single_payment_cycle_count
        ),
        _METHOD_DPD_BUCKET_MOVEMENT: pre_dlq_payment_signals_dpd_bucket_movement,
    }
    _validate_method_pairs(
        dlq_pairs,
        pre_dlq_pairs,
        dlq_payment_evidence_method,
        pre_dlq_payment_evidence_method,
    )

    df = commitment_signals.join(
        negative_signals, on=["account_id", "observation_date"], how="left"
    )
    for approach, pair in dlq_pairs.items():
        df = _join_signals_pair(
            df, pair, ["account_id", "observation_date"], _DLQ_PAIR_COLUMNS, approach
        )
    for approach, pair in pre_dlq_pairs.items():
        df = _join_signals_pair(
            df, pair, ["account_id", "t0"], _PRE_DLQ_PAIR_COLUMNS, approach
        )

    df = _score_dimension_b(df, dlq_pairs)
    df = _score_dimension_c(df, pre_dlq_pairs)
    df = _select_shipped_methods(
        df, dlq_payment_evidence_method, pre_dlq_payment_evidence_method
    )
    df = df.withColumn(
        "a3_strong_negative_reason",
        _strong_negative_reason(dlq_payment_evidence_method),
    ).withColumn("_has_strong_negative", F.col("a3_strong_negative_reason").isNotNull())

    output = _a3_output(
        df, dlq_payment_evidence_method, pre_dlq_payment_evidence_method
    )

    _log_a3_stats(output)
    if model_id and persona_end_date:
        log_latest_month(
            output,
            "a3_state_v1",
            f"a3_payment_credibility [{model_id}]",
            persona_end_date,
        )
    return output


def _log_a3_stats(df: DataFrame) -> None:
    """Log state distribution for post-run monitoring."""
    try:
        n_total = df.count()
        state_dist = df.groupBy("a3_state_v1").count().collect()
        path_dist = df.groupBy("a3_path").count().collect()

        LOG.info("build_a3_payment_credibility: total rows = %d", n_total)
        for row in state_dist:
            pct = 100.0 * row["count"] / max(n_total, 1)
            LOG.info(
                "  a3_state_v1=%-35s n=%7d  (%.1f%%)",
                str(row["a3_state_v1"]),
                row["count"],
                pct,
            )
        LOG.info("  path breakdown:")
        for row in path_dist:
            LOG.info("  %-30s n=%d", str(row["a3_path"]), row["count"])
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("_log_a3_stats: stats collection failed – %s", exc)
