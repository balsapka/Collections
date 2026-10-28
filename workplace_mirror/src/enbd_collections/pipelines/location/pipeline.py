"""Location inputs of the A2 locatability axis (per model_id).

    dcore_observation_spine ─► prm_dcore_account_agreements ─┐
    prm_digital_login_monthly, prm_casa_card_transactions,    ├─► feat_cif_location_monthly
    prm_transaction, prm_contract, prm_client,                │
    dcore_prm_followup_outcomes ──────────────────────────────┘

Needs ``digital_login`` and ``casa_primary`` for the model_id first.

    kedro run --pipeline=location_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.location import feat_cif_location_monthly
from enbd_collections.nodes.primary.dcore import prm_dcore_account_agreements


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_dcore_account_agreements and feat_cif_location_monthly."""
    return Pipeline(
        [
            node(
                func=prm_dcore_account_agreements.build,
                inputs="dcore_observation_spine",
                outputs="prm_dcore_account_agreements",
                name="build_prm_dcore_account_agreements",
                tags=["dcore", "primary"],
            ),
            node(
                func=feat_cif_location_monthly.build,
                inputs={
                    "logins": "prm_digital_login_monthly",
                    "casa_cards": "prm_casa_card_transactions",
                    "transactions": "prm_transaction",
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:location_features.history_months",
                },
                outputs="feat_cif_location_monthly",
                name="build_feat_cif_location_monthly",
                tags=["location", "features"],
            ),
        ]
    )
