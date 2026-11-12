"""Product feature pipeline: the customer's other products with us per month.

feat_product_holding, bo_rr_portf_actv_acct_mthly,
wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif,
raw_stg_client / contract / billing / balance / account_group
                                    ─────────────→ feat_cif_cross_product_monthly

kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline(
        [
            node(
                func=feat_cif_cross_product.build,
                inputs={
                    "product_holding": "feat_product_holding",
                    "loan_portfolio": "bo_rr_portf_actv_acct_mthly",
                    "wm_balances": "wm_fea_casa_eod_avg_balance",
                    "wm_holdings": "wm_fea_wealth_holdings_by_cif",
                    "card_client": "raw_stg_client",
                    "card_contract": "raw_stg_contract",
                    "card_billing": "raw_stg_billing",
                    "card_balance": "raw_stg_balance",
                    "card_account_group": "raw_stg_account_group",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:casa_features.history_months",
                },
                outputs="feat_cif_cross_product_monthly",
                name="build_feat_cif_cross_product_monthly",
                tags=["products", "features"],
            ),
        ]
    )
