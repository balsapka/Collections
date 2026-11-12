"""CASA feature pipeline: monthly CASA features per customer (per model_id).

    wm_fea_salary_days_since_increment ──────────────────► feat_cif_internal_salary_monthly
    wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow ► feat_cif_casa_balance_monthly
    prm_casa_transactions, prm_casa_accounts ────────────► feat_cif_casa_activity_monthly
    wm_pri_labelled_transactions, prm_beneficiary_cards ─► feat_cif_ext_card_payment_monthly
    prm_casa_return_events, prm_casa_accounts ───────────► feat_cif_returns_monthly
    prm_casa_transactions, prm_casa_accounts,
    wm_pri_labelled_transactions ────────────────────────► prm_casa_flow_legs (HDFS)
    prm_casa_flow_legs ──────────────────────────────────► feat_cif_casa_flows_monthly

Needs ``casa_primary`` for the model_id first.

    kedro run --pipeline=casa_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_casa


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The six monthly CASA feature tables (the flows one via the saved classified legs)."""
    tags = ["casa", "features"]
    window = {
        "persona_start_date": "params:crx_persona.persona_start_date",
        "history_months": "params:casa_features.history_months",
    }
    return Pipeline(
        [
            node(
                func=feat_cif_casa.build_internal_salary,
                inputs={"wm_salary": "wm_fea_salary_days_since_increment"},
                outputs="feat_cif_internal_salary_monthly",
                name="build_feat_cif_internal_salary_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_balance,
                inputs={
                    "wm_casa_balance": "wm_fea_casa_eod_avg_balance",
                    "wm_casa_flow": "wm_fea_casa_cc_inflow_outflow",
                    **window,
                },
                outputs="feat_cif_casa_balance_monthly",
                name="build_feat_cif_casa_balance_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_activity,
                inputs={
                    "transactions": "prm_casa_transactions",
                    "casa_accounts": "prm_casa_accounts",
                },
                outputs="feat_cif_casa_activity_monthly",
                name="build_feat_cif_casa_activity_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_ext_card_payments,
                inputs={
                    "labelled": "wm_pri_labelled_transactions",
                    "beneficiary_cards": "prm_beneficiary_cards",
                    **window,
                },
                outputs="feat_cif_ext_card_payment_monthly",
                name="build_feat_cif_ext_card_payment_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_returns,
                inputs={
                    "return_events": "prm_casa_return_events",
                    "casa_accounts": "prm_casa_accounts",
                },
                outputs="feat_cif_returns_monthly",
                name="build_feat_cif_returns_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_flow_legs,
                inputs={
                    "transactions": "prm_casa_transactions",
                    "casa_accounts": "prm_casa_accounts",
                    "labelled": "wm_pri_labelled_transactions",
                    **window,
                },
                outputs="prm_casa_flow_legs",
                name="build_prm_casa_flow_legs",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_flows,
                inputs={"legs": "prm_casa_flow_legs"},
                outputs="feat_cif_casa_flows_monthly",
                name="build_feat_cif_casa_flows_monthly",
                tags=tags,
            ),
        ]
    )
