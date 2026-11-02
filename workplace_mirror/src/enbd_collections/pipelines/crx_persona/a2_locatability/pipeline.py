"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node

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
