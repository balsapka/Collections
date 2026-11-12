"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly
                      ├─ CASA signals ──────┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_casa_flows_monthly
                      ├─ cross-product ─────┤   feat_cif_cross_product_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``product_features``, ``bureau_salary_bounces`` and ``location_features``
(``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_casa_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "casa_flows": "feat_cif_casa_flows_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_casa_signals",
                name=f"build_{prefix}_casa_signals",
                tags=TAGS,
            ),
            node(
                func=build_cross_product_signals,
                inputs={
                    "obs_base": obs,
                    "products": "feat_cif_cross_product_monthly",
                },
                outputs=f"{prefix}_cross_product_signals",
                name=f"build_{prefix}_cross_product_signals",
                tags=TAGS,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": obs,
                    "returns": "feat_cif_returns_monthly",
                    "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_distress_signals",
                name=f"build_{prefix}_distress_signals",
                tags=TAGS,
            ),
            node(
                func=build_eosb_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_eosb_signals",
                name=f"build_{prefix}_eosb_signals",
                tags=TAGS,
            ),
            anchor,
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_signals",
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_ability",
                tags=TAGS,
            ),
        ],
    )
