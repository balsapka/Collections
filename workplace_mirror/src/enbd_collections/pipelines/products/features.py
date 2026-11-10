"""Product feature pipeline: the customer's other products with us per month.

feat_product_holding, bo_rr_portf_actv_acct_mthly,
card balances, WM assets ────────────────────────────► feat_cif_cross_product_monthly

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
                    # TODO(sonnet): the card balances and WM asset datasets the round-3
                    # snippet loaded for F4.
                    "card_balances": "prm_balance",
                    "wm_assets": "wm_fea_aum_balance",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:casa_features.history_months",
                },
                outputs="feat_cif_cross_product_monthly",
                name="build_feat_cif_cross_product_monthly",
                tags=["products", "features"],
            )
        ]
    )
