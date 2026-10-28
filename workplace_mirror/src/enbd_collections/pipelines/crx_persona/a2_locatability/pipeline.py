"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` runs the observation base,
``location_features`` and the same nodes, writes the axis to
``crx_<p>_a2_locatability_b06_check`` and logs the comparison with the old A2
(``b06_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.location.pipeline import (
    create_pipeline as create_location_pipeline,
)

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b06_check import (
    compare_a2_outputs,
    describe_a2_rules,
    describe_debit_evidence,
    split_by_product,
)
from .classify import build_a2_locatability
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)


def create_a2_pipeline(product: str, output: str) -> Pipeline:
    """Signal nodes and the state node of ``product``'s A2 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a2"
    tags = ["crx_persona", "crx", "a2", "locatability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_location_signals,
                inputs={
                    "obs_base": obs,
                    "location_features": "feat_cif_location_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_location_signals",
                name=f"build_{prefix}_location_signals",
                tags=tags,
            ),
            node(
                func=build_dcore_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_dcore_signals",
                name=f"build_{prefix}_dcore_signals",
                tags=tags,
            ),
            node(
                func=build_way4_deceased,
                inputs={
                    "obs_base": obs,
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                },
                outputs=f"{prefix}_way4_deceased",
                name=f"build_{prefix}_way4_deceased",
                tags=tags,
            ),
            node(
                func=build_demographics_deceased,
                inputs={"obs_base": obs, "demographics": "feat_demographics_cif"},
                outputs=f"{prefix}_demographics_deceased",
                name=f"build_{prefix}_demographics_deceased",
                tags=tags,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "obs_base": obs,
                    "location": f"{prefix}_location_signals",
                    "dcore": f"{prefix}_dcore_signals",
                    "way4_deceased": f"{prefix}_way4_deceased",
                    "demographics_deceased": f"{prefix}_demographics_deceased",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_locatability",
                tags=tags,
            ),
        ],
    )


def create_b06_check_pipeline(product: str) -> Pipeline:
    """TEMPORARY: observation base + location inputs + the A2 pipeline writing to
    crx_<p>_a2_locatability_b06_check + the log-only comparison nodes.
    Remove with b06_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    check = f"crx_{product}_a2_locatability_b06_check"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a2_outputs,
            inputs=[f"crx_{product}_a2_locatability", check, "params:model_id"],
            outputs=None,
            name=f"compare_crx_{product}_a2_b06",
            tags=tags,
        ),
        node(
            func=describe_a2_rules,
            inputs=[check, "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_rules",
            tags=tags,
        ),
        node(
            func=describe_debit_evidence,
            inputs=[obs, "prm_casa_card_transactions", "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_debit",
            tags=tags,
        ),
    ]
    if product == "rl":
        checks.append(
            node(
                func=split_by_product,
                inputs=[check, "rl_spine", "params:model_id"],
                outputs=None,
                name="split_crx_rl_a2_b06_product",
                tags=tags,
            )
        )
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_location_pipeline()
        + create_a2_pipeline(product, output=check)
        + Pipeline(checks)
    )
