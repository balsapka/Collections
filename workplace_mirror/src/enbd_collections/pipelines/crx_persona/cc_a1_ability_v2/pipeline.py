"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ────────────────────┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first.
prm_bureau_payment_order joins the distress node once it exists in PROD.

    kedro run --pipeline=crx_cc_a1_ability_v2

TEMPORARY (mirror bundle 03): ``create_b03_check_pipeline`` runs the same nodes but
writes the axis to the temporary dataset ``crx_cc_a1_ability_b03_check`` (the existing
``crx_cc_a1_ability_v2`` is not overwritten) and logs the old-vs-new comparison
(``b03_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from .b03_check import compare_a1_outputs
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,  # pylint: disable=unused-argument
) -> Pipeline:
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                ],
                "crx_cc_a1_income_signals",
                name="build_crx_cc_a1_income_signals",
            ),
            node(
                build_liquidity_signals,
                [
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_internal_returns,
                [_OBS, "prm_casa_return_events"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
                },
                "crx_cc_a1_distress_signals",
                name="build_crx_cc_a1_distress_signals",
            ),
            node(
                build_cc_liquidity_anchor,
                [_OBS, "prm_balance", "params:model_id"],
                "crx_cc_a1_liquidity_anchor",
                name="build_crx_cc_a1_liquidity_anchor",
            ),
            node(
                build_a1_ability,
                [
                    _OBS,
                    "crx_cc_a1_income_signals",
                    "crx_cc_a1_liquidity_signals",
                    "crx_cc_a1_distress_signals",
                    "crx_cc_a1_liquidity_anchor",
                    "params:crx_log_stats",
                ],
                output,
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )


def create_b03_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_cc_a1_ability_b03_check + the log-only comparison node.
    Remove with b03_check.py and the catalog entries."""
    return (
        create_cc_obs_pipeline()
        + create_pipeline(output="crx_cc_a1_ability_b03_check")
        + Pipeline(
            [
                node(
                    compare_a1_outputs,
                    [
                        "crx_cc_a1_ability_b01_check",
                        "crx_cc_a1_ability_b03_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b03",
                ),
            ],
            tags=["crx_persona"],
        )
    )
