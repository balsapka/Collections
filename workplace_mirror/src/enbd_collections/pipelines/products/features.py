"""Product feature pipeline: the customer's other products with us per month.

    prm_card_contracts, prm_card_month_end, prm_loan_month_end,
    wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif ► feat_cif_cross_product_monthly

Needs ``product_primary`` for the model_id first.

    kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline([_cross_product_node("feat_cif_cross_product_monthly")])


def _cross_product_node(output: str):
    return node(
        func=feat_cif_cross_product.build,
        inputs={
            "card_contracts": "prm_card_contracts",
            "card_month_end": "prm_card_month_end",
            "loan_month_end": "prm_loan_month_end",
            "wm_balances": "wm_fea_casa_eod_avg_balance",
            "wm_holdings": "wm_fea_wealth_holdings_by_cif",
            "persona_start_date": "params:crx_persona.persona_start_date",
            "history_months": "params:products.history_months",
        },
        outputs=output,
        name=f"build_{output}",
        tags=["products", "features"],
    )


def create_b24_check_pipeline() -> Pipeline:
    """TEMPORARY (bundle 24): the table rebuilt from the product primaries against the
    persisted one; removed by the bundle's cleanup."""
    from . import check  # pylint: disable=import-outside-toplevel

    return Pipeline(
        [
            _cross_product_node("feat_cif_cross_product_monthly_b24_new"),
            node(
                func=check.compare,
                inputs={
                    "old": "feat_cif_cross_product_monthly",
                    "new": "feat_cif_cross_product_monthly_b24_new",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name="b24_check_compare",
                tags=["products", "b24_check"],
            ),
        ]
    )
