"""Kedro pipeline: T27 – A3 Payment Credibility axis.

# pylint: disable=line-too-long

Nine-node pipeline that derives the A3 payment-credibility axis and emits
the shipped persona column ``a3_state_v1`` at (account_id, observation_date) grain.

Architecture:
    build_a3_commitment_signals          → crx_cc_a3_commitment_signals      (Dimension A: level, points, broken streak)
    build_a3_strong_negative_signals     → crx_cc_a3_strong_negative_signals (strong-negative evidence; rules run in the combiner)
    build_a3_payment_cycles              → crx_cc_a3_payment_cycles          (shared by Dimension B/C)
    build_a3_dlq_payment_signals_payment_sum_waterfall      → crx_cc_a3_dlq_payment_signals_payment_sum_waterfall      (Dimension B, payment_sum_waterfall – shadow)
    build_a3_dlq_payment_signals_single_payment_cycle_count → crx_cc_a3_dlq_payment_signals_single_payment_cycle_count (Dimension B, single_payment_cycle_count – default)
    build_a3_dlq_payment_signals_dpd_bucket_movement        → crx_cc_a3_dlq_payment_signals_dpd_bucket_movement        (Dimension B, dpd_bucket_movement – shadow)
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count → crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count (Dimension C, single_payment_cycle_count – default)
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement        → crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement        (Dimension C, dpd_bucket_movement – shadow)
    build_a3_payment_credibility         → crx_cc_a3_payment_credibility     ← shipped axis

params:cc_a3_history_floor_date (default 2024-01-01, null = off) is the earliest billing
date Dimension B and C read; it is passed to the five Dimension B/C nodes and to
cc_raw_extract's build_cc_acct_windows. crx_cc_spell_table / crx_cc_full_history stay
unfloored (other pipelines read them).

Dimension B and C have INDEPENDENT evidence-method switches (decoupled
2026-10-26 – see build_a3_payment_credibility's docstring, "Why decoupled"):
params:a3_dlq_payment_evidence_method ("single_payment_cycle_count" default,
Dimension B only, 3-way) and params:a3_pre_dlq_payment_evidence_method
("single_payment_cycle_count" default, Dimension C only, 2-way, unchanged). All pairs of
nodes above always run regardless of either switch, so every method's output
can be correlated directly off crx_cc_a3_payment_credibility's per-method
columns (a3_dlq_payment_level_single_payment_cycle_count / _payment_sum_waterfall /
_dpd_bucket_movement for Dimension B; a3_pre_dlq_payment_level_single_payment_cycle_count /
_dpd_bucket_movement for Dimension C).

build_a3_payment_cycles combines the billing-cycle payment attribution and
due-amount resolution once, so build_a3_dlq_payment_signals_payment_sum_waterfall and
build_a3_pre_dlq_payment_signals_single_payment_cycle_count both consume its output instead of each
re-deriving it independently from crx_cc_billing/crx_cc_balance/
crx_cc_transactions. The two dimension nodes have no dependency on each other
and run independently; both feed the final combiner. Both also take cc_spine
as an input – for build_a3_dlq_payment_signals_payment_sum_waterfall it drives the window-length
choice (3mo/6mo); for build_a3_pre_dlq_payment_signals_single_payment_cycle_count it is a population
filter only (scopes crx_cc_spell_table down to spells actually represented in
the current model_id population, avoiding wasted per-spell joins for accounts
with many historical cured spells no longer in scope) – its window is still
purely t0-anchored.

Inputs:
    cc_spine                    Model-id-scoped spine – master grain (account_id, observation_date, cif_id)
    crx_cc_spell_table          T03 – lookup for t0 per spell (joined on account_id + date range)
    dcore_observation_spine     account+agreement mapping (contract_id, observation_date, agreement_id, cif_id)
    dcore_prm_followup_outcomes DCORE contact attempt log (strong negatives)
    dcore_feat_ptp              Aggregated PTP history per agreement
    dcore_feat_settlement       Arrangement / settlement status per agreement
    dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
    dcore_prm_settlement_schedule_instalments
                                Dimension A broken streak (latest concluded instalments);
                                dcore_int_ptp / dcore_int_settlement also feed the strong-negative
                                plan-on-record and Refusal evidence
    crx_cc_transactions         Refusal strong negative (payment after the refusal)
    crx_cc_billing              T04c – billing_date, due_date, next_billing_date
    crx_cc_balance              T04c – minimum_due, overdue_bucket_01..08, total_due
    crx_cc_transactions         T04c – payment transactions, txn_category, is_post_block_x_fee
    crx_cc_full_history         Full, floor-free (account_id, billing_date) → dlq_bucket
                                history – feeds both DPD-bucket-method nodes
                                (build_a3_dlq_payment_signals_dpd_bucket_movement /
                                build_a3_pre_dlq_payment_signals_dpd_bucket_movement) via
                                _signals_common.resolve_dpd_bucket_movement_history

Output:
    crx_cc_a3_payment_credibility – A3 axis for every (account_id, observation_date)
    pair; a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
    payment_credibility_low, payment_credibility_unknown}.

Run with:
    kedro run --pipeline=crx_cc_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a3_commitment_signals,
    build_a3_strong_negative_signals,
    build_a3_dlq_payment_signals_payment_sum_waterfall,
    build_a3_dlq_payment_signals_single_payment_cycle_count,
    build_a3_dlq_payment_signals_dpd_bucket_movement,
    build_a3_payment_credibility,
    build_a3_payment_cycles,
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count,
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
)

_TAGS = ["crx", "a3", "payment_credibility", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node A3 Payment Credibility pipeline."""
    return Pipeline(
        [
            # ── Dimension A: commitments kept (DCORE PTP / settlement signals) ──
            node(
                func=build_a3_commitment_signals,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "dcore_observation_spine",
                    "dcore_feat_ptp",
                    "dcore_feat_settlement",
                    "dcore_int_ptp",
                    "dcore_prm_promise_instalments",
                    "dcore_int_settlement",
                    "dcore_prm_settlement_schedule_instalments",
                ],
                outputs="crx_cc_a3_commitment_signals",
                name="build_a3_commitment_signals",
                tags=_TAGS,
            ),
            # ── Strong negatives: evidence only; the rules run in the combiner ──
            node(
                func=build_a3_strong_negative_signals,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "dcore_int_ptp",
                    "dcore_int_settlement",
                    "crx_cc_transactions",
                ],
                outputs="crx_cc_a3_strong_negative_signals",
                name="build_a3_strong_negative_signals",
                tags=_TAGS,
            ),
            # ── Shared input for Dimensions B and C: per-cycle payments, due amount
            # and waterfall months ──────────────────────────────────────────────
            node(
                func=build_a3_payment_cycles,
                inputs=[
                    "crx_cc_billing",
                    "crx_cc_balance",
                    "crx_cc_transactions",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_payment_cycles",
                name="build_a3_payment_cycles",
                tags=_TAGS,
            ),
            # ── Dimension B (dlq): payments in delinquency – three approaches, all
            # always computed for cross-checking; the shipped one is chosen by
            # params:a3_dlq_payment_evidence_method (default single_payment_cycle_count).
            node(
                func=build_a3_dlq_payment_signals_payment_sum_waterfall,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
                name="build_a3_dlq_payment_signals_payment_sum_waterfall",
                tags=_TAGS,
            ),
            node(
                func=build_a3_dlq_payment_signals_single_payment_cycle_count,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
                name="build_a3_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_a3_dlq_payment_signals_dpd_bucket_movement,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_full_history",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
                name="build_a3_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Dimension C (pre_dlq): record before delinquency – two approaches,
            # all always computed; the shipped one is chosen by
            # params:a3_pre_dlq_payment_evidence_method (default single_payment_cycle_count).
            node(
                func=build_a3_pre_dlq_payment_signals_single_payment_cycle_count,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                name="build_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_full_history",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                name="build_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Combiner: Dimensions A + B + C -> a3_state_v1 ──────────────────
            node(
                func=build_a3_payment_credibility,
                inputs=[
                    "crx_cc_a3_commitment_signals",
                    "crx_cc_a3_strong_negative_signals",
                    "crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
                    "crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
                    "crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
                    "crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                    "crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                    "params:a3_dlq_payment_evidence_method",
                    "params:a3_pre_dlq_payment_evidence_method",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs="crx_cc_a3_payment_credibility",
                name="build_a3_payment_credibility",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
