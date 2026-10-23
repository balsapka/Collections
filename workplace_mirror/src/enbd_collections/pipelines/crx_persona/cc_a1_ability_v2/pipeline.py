"""Kedro pipeline: T31 — A1 Ability axis v2 (GRR MECE points redesign).

Five-node pipeline, additive beside T26's cc_a1_ability (R18 — that
pipeline's nodes/enrichers/catalog entries are never modified). Emits a new
persona axis table, ``crx_cc_a1_ability_v2``, carrying ``a1_state_v2``.

Architecture:
    build_a1v2_cif_base           -> crx_cc_a1v2_cif_base          [Node 1]
    build_a1v2_income_signals     -> crx_cc_a1v2_income_signals    [Node 2] ┐
    build_a1v2_liquidity_signals -> crx_cc_a1v2_liquidity_signals [Node 3] ┤ parallel
    build_a1v2_distress_signals   -> crx_cc_a1v2_distress_signals  [Node 4] ┘
    build_a1v2_classify           -> crx_cc_a1_ability_v2          [Node 5]

prm_bureau_payment_order / feature_retail_loans are NOT wired into Node 4
here — both PATH_NOT_FOUND in PROD as of T31 Leg A (2026-10-22), not yet
materialized (see cc_a1_ability_v2/nodes.py module docstring). Node 4's
function signature already accepts them as optional parameters; wiring them
in once the tables land is a 2-line addition to this file's inputs list, no
change to the distress logic itself.

Run with:
    kedro run --pipeline=crx_cc_a1_ability_v2
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a1v2_cif_base,
    build_a1v2_classify,
    build_a1v2_distress_signals,
    build_a1v2_income_signals,
    build_a1v2_liquidity_signals,
)

_TAGS = ["crx", "a1", "ability", "a1_v2", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 5-node A1 Ability v2 pipeline."""
    return Pipeline(
        [
            node(
                func=build_a1v2_cif_base,
                inputs=["cc_spine", "prm_contract", "prm_client"],
                outputs="crx_cc_a1v2_cif_base",
                name="build_crx_a1v2_cif_base",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_income_signals,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "feat_payroll_indicator",
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                ],
                outputs="crx_cc_a1v2_income_signals",
                name="build_crx_a1v2_income_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_liquidity_signals,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "prm_balance",
                    "feat_casa_eod_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1v2_liquidity_signals",
                name="build_crx_a1v2_liquidity_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_distress_signals,
                inputs=["crx_cc_a1v2_cif_base", "prm_bureau_alert_enriched"],
                outputs="crx_cc_a1v2_distress_signals",
                name="build_crx_a1v2_distress_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_classify,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "crx_cc_a1v2_income_signals",
                    "crx_cc_a1v2_liquidity_signals",
                    "crx_cc_a1v2_distress_signals",
                ],
                outputs="crx_cc_a1_ability_v2",
                name="build_crx_a1v2_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
