"""Kedro pipeline: RL A1 ability axis.

    crx_rl_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_rl_a1_ability_v2
                     └─ liquidity anchor (EMI) ──────────────┘

Needs crx_rl_obs_base (``kedro run --pipeline=crx_rl_obs_base``) and
prm_casa_return_events for the RL model_id (``kedro run --pipeline=casa_primary``) first.

    kedro run --pipeline=crx_rl_a1_ability_v2

TEMPORARY (mirror bundle 05): ``create_b05_check_pipeline`` runs the same nodes but
writes the axis to ``crx_rl_a1_ability_b05_check`` and logs the comparison with the RL
waterfall (``b05_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b05_check import compare_income_sources, compare_rl_a1_outputs
from .nodes import build_rl_liquidity_anchor

_OBS = "crx_rl_obs_base"


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability_v2",
    **kwargs,
) -> Pipeline:
    """The RL A1 axis: signal tables, the EMI anchor and the state, written to
    ``output``."""
    tags = ["crx_persona", "crx", "a1", "ability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": _OBS,
                    "wm_salary": "wm_fea_salary_days_since_increment",
                    "salary_hist": "stg_aecb_salary_history",
                    "bureau_cif_bridge": "prm_bureau_cif_bridge",
                    "model_id": "params:model_id",
                    "loan_features": "feature_retail_loans",
                },
                outputs="crx_rl_a1_income_signals",
                name="build_crx_rl_a1_income_signals",
                tags=tags,
            ),
            node(
                func=build_liquidity_signals,
                inputs=[
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:model_id",
                ],
                outputs="crx_rl_a1_liquidity_signals",
                name="build_crx_rl_a1_liquidity_signals",
                tags=tags,
            ),
            node(
                func=build_internal_returns,
                inputs=[_OBS, "prm_casa_return_events", "params:model_id"],
                outputs="crx_rl_a1_internal_returns",
                name="build_crx_rl_a1_internal_returns",
                tags=tags,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_rl_a1_internal_returns",
                    "model_id": "params:model_id",
                },
                outputs="crx_rl_a1_distress_signals",
                name="build_crx_rl_a1_distress_signals",
                tags=tags,
            ),
            node(
                func=build_rl_liquidity_anchor,
                inputs=[_OBS, "int_loan_master"],
                outputs="crx_rl_a1_liquidity_anchor",
                name="build_crx_rl_a1_liquidity_anchor",
                tags=tags,
            ),
            node(
                func=build_a1_ability,
                inputs=[
                    _OBS,
                    "crx_rl_a1_income_signals",
                    "crx_rl_a1_liquidity_signals",
                    "crx_rl_a1_distress_signals",
                    "crx_rl_a1_liquidity_anchor",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs=output,
                name="build_crx_rl_a1_ability",
                tags=tags,
            ),
        ],
    )


def create_b05_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the RL A1 pipeline writing to
    crx_rl_a1_ability_b05_check + the log-only comparison nodes.
    Remove with b05_check.py and the catalog entry."""
    tags = ["crx_persona"]
    return (
        create_rl_obs_pipeline()
        + create_pipeline(output="crx_rl_a1_ability_b05_check")
        + Pipeline(
            [
                node(
                    func=compare_rl_a1_outputs,
                    inputs=[
                        "crx_rl_a1_ability",
                        "crx_rl_a1_ability_b05_check",
                        "params:model_id",
                    ],
                    outputs=None,
                    name="compare_crx_rl_a1_b05",
                    tags=tags,
                ),
                node(
                    func=compare_income_sources,
                    inputs={
                        "obs_base": _OBS,
                        "wm_salary": "wm_fea_salary_days_since_increment",
                        "salary_hist": "stg_aecb_salary_history",
                        "bureau_cif_bridge": "prm_bureau_cif_bridge",
                        "loan_features": "feature_retail_loans",
                        "a1": "crx_rl_a1_ability_b05_check",
                        "model_id": "params:model_id",
                    },
                    outputs=None,
                    name="compare_crx_rl_a1_b05_income",
                    tags=tags,
                ),
            ],
        )
    )
