"""Kedro pipeline: RL-A3-1 – A3 Payment Credibility axis for Retail Loans.

Nine nodes mirroring cc_a3_payment_credibility: Dimension A reuses CC nodes
through a thin wrapper; Dimension B has three approaches and
Dimension C two, all always computed and named like CC's
(dimension prefix + approach: payment_sum_waterfall / single_payment_cycle_count
/ dpd_bucket_movement); the last node wraps CC's domain-agnostic combiner and
ships the approach chosen by params:rl_a3_dlq_payment_evidence_method /
params:rl_a3_pre_dlq_payment_evidence_method (default single_payment_cycle_count
for both dimensions, CC's defaults). See
nodes.py's module docstring for what each approach computes and the timing
convention (RL's cash and bucket for a month sit on the same month-end row).

Architecture (output dataset = function name, "build_" -> "crx_" prefix):
    build_rl_a3_commitment_signals                                 [Dimension A]
    build_rl_a3_strong_negative_signals                            [strong-negative evidence]
    build_rl_a3_dlq_cycles                                         [shared B/C input]
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall          [Dimension B]
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count     [Dimension B, shipped]
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement            [Dimension B]
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count [Dimension C, shipped]
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement        [Dimension C]
    build_rl_a3_payment_credibility                                [combiner A+B+C, shipped]

Dimension A: crx_rl_a4_spine already carries (account_id, observation_date,
spell_id, t0, cif_id) – reshaped into the CC (cc_spine, spell_table) shim
pair via rl_spine_as_cc_shim so build_a3_commitment_signals runs
unchanged. Strong negatives (build_rl_a3_strong_negative_signals) use the same
shim and apply a 24m partition floor on dcore_prm_followup_outcomes
(performance guard per TASKS_RL.md).

The five Dimension B/C nodes depend only on build_rl_a3_dlq_cycles' output and
crx_rl_a4_spine (which carries spell_id/t0 directly), so they run in parallel
once it completes.

Run with:
    kedro run --pipeline=crx_rl_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a3_commitment_signals,
    build_rl_a3_dlq_cycles,
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement,
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall,
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count,
    build_rl_a3_payment_credibility,
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement,
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count,
    build_rl_a3_strong_negative_signals,
)

_TAGS = ["crx", "a3", "payment_credibility", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node RL A3 Payment Credibility pipeline."""
    return Pipeline(
        [
            # ── Dimension A: commitments kept (DCORE PTP / settlement signals,
            # 24m partition floor, RL-D5 spine) ────────────────────────────────
            node(
                func=build_rl_a3_commitment_signals,
                inputs=[
                    "crx_rl_a4_spine",
                    "dcore_observation_spine",
                    "dcore_feat_ptp",
                    "dcore_feat_settlement",
                    "dcore_int_ptp",
                    "dcore_prm_promise_instalments",
                    "dcore_int_settlement",
                    "dcore_prm_settlement_schedule_instalments",
                ],
                outputs="crx_rl_a3_commitment_signals",
                name="build_rl_a3_commitment_signals",
                tags=_TAGS,
            ),
            # ── Strong negatives: evidence only (24m follow-up floor); the rules
            # run in the combiner ───────────────────────────────────────────────
            node(
                func=build_rl_a3_strong_negative_signals,
                inputs=[
                    "crx_rl_a4_spine",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "params:crx_persona",
                    "dcore_int_ptp",
                    "dcore_int_settlement",
                ],
                outputs="crx_rl_a3_strong_negative_signals",
                name="build_rl_a3_strong_negative_signals",
                tags=_TAGS,
            ),
            # ── Shared input for Dimensions B and C: monthly bucket + lag +
            # monthly_emi_due + total_paid ──────────────────────────────────────
            node(
                func=build_rl_a3_dlq_cycles,
                inputs=["crx_rl_full_history", "int_loan_master", "rl_spine"],
                outputs="crx_rl_a3_dlq_cycles",
                name="build_rl_a3_dlq_cycles",
                tags=_TAGS,
            ),
            # ── Dimension B (dlq): payments in delinquency – three approaches,
            # all always computed; shipped one chosen by
            # params:rl_a3_dlq_payment_evidence_method ──────────────────────────
            node(
                func=build_rl_a3_dlq_payment_signals_payment_sum_waterfall,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                name="build_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_dlq_payment_signals_single_payment_cycle_count,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                name="build_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_dlq_payment_signals_dpd_bucket_movement,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                name="build_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Dimension C (pre_dlq): record before delinquency – two approaches,
            # all always computed; shipped one chosen by
            # params:rl_a3_pre_dlq_payment_evidence_method ──────────────────────
            node(
                func=build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                name="build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                name="build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Combiner: Dimensions A + B + C -> a3_state_v1 (CC's
            # build_a3_payment_credibility, wrapped) ────────────────────────────
            node(
                func=build_rl_a3_payment_credibility,
                inputs=[
                    "crx_rl_a3_commitment_signals",
                    "crx_rl_a3_strong_negative_signals",
                    "crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                    "crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                    "crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                    "crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                    "crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                    "params:rl_a3_dlq_payment_evidence_method",
                    "params:rl_a3_pre_dlq_payment_evidence_method",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs="crx_rl_a3_payment_credibility",
                name="build_rl_a3_payment_credibility",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
