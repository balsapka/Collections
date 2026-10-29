"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly (+ RL loans)
                      ├─ liquidity signals ─┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_ext_card_payment_monthly,
                      │                     │   feat_cif_casa_activity_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``bureau_salary_bounces`` and ``location_features`` (``prm_dcore_account_agreements``).

TEMPORARY (mirror bundle 08): ``create_b08_check_pipeline`` runs the observation base and
the same nodes, writes the axis to ``crx_<p>_a1_ability_b08_check`` and logs the report
tables (``b08_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b08_check import (
    compare_a1_outputs,
    describe_a1_report,
    describe_a1_sources,
    explain_a1_changes,
)
from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
    build_liquidity_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    income_inputs = {
        "obs_base": obs,
        "internal_salary": "feat_cif_internal_salary_monthly",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        income_inputs["loan_features"] = "feature_retail_loans"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs=income_inputs,
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_liquidity_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "ext_card_payments": "feat_cif_ext_card_payment_monthly",
                    "casa_activity": "feat_cif_casa_activity_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_liquidity_signals",
                name=f"build_{prefix}_liquidity_signals",
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
                    "liquidity": f"{prefix}_liquidity_signals",
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


def create_b08_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_<p>_a1_ability_b08_check + the log-only report nodes.
    Remove with b08_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    check = f"{prefix}_ability_b08_check"
    signals = {
        "income": f"{prefix}_income_signals",
        "liquidity": f"{prefix}_liquidity_signals",
        "distress": f"{prefix}_distress_signals",
    }
    products = "rl_spine" if product == "rl" else obs
    changes = {
        "obs_base": obs,
        "old": f"{prefix}_ability_v2",
        "new": check,
        **signals,
        "anchor": f"{prefix}_liquidity_anchor",
        "wm_salary": "wm_fea_salary_days_since_increment",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "casa_balance": "feat_cif_casa_balance_monthly",
        "bureau_bounces": "feat_cif_bureau_bounces_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        changes["loan_features"] = "feature_retail_loans"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a1_outputs,
            inputs={
                "old": f"{prefix}_ability_v2",
                "new": check,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"compare_{prefix}_b08",
            tags=tags,
        ),
        node(
            func=describe_a1_report,
            inputs={
                "obs_base": obs,
                "new": check,
                **signals,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b08_report",
            tags=tags,
        ),
        node(
            func=describe_a1_sources,
            inputs={
                "obs_base": obs,
                "new": check,
                "internal_salary": "feat_cif_internal_salary_monthly",
                "bureau_salary": "feat_cif_bureau_salary_monthly",
                "casa_balance": "feat_cif_casa_balance_monthly",
                "casa_activity": "feat_cif_casa_activity_monthly",
                "transactions": "prm_casa_transactions",
                "alerts": "prm_bureau_alert_enriched",
                "cif_bridge": "prm_bureau_cif_bridge",
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b08_sources",
            tags=tags,
        ),
        node(
            func=explain_a1_changes,
            inputs=changes,
            outputs=None,
            name=f"explain_{prefix}_b08_changes",
            tags=tags,
        ),
    ]
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_a1_pipeline(product, output=check, anchor=anchor)
        + Pipeline(checks)
    )
