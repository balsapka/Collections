"""Product primary pipeline: every customer's card contracts, card month ends and loan
month ends (per model_id).

    raw_stg_client, raw_stg_contract ─────────────────────► prm_card_contracts
    raw_stg_billing, raw_stg_balance, raw_stg_account_group ► prm_card_month_end
    bo_rr_portf_actv_acct_mthly ──────────────────────────► prm_loan_month_end

    kedro run --pipeline=product_primary
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.products import prm_products


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The three product primaries read by ``product_features``."""
    tags = ["products", "primary"]
    window = {
        "persona_start_date": "params:crx_persona.persona_start_date",
        "history_months": "params:products.history_months",
    }
    return Pipeline(
        [
            node(
                func=prm_products.build_card_contracts,
                inputs={"client": "raw_stg_client", "contract": "raw_stg_contract"},
                outputs="prm_card_contracts",
                name="build_prm_card_contracts",
                tags=tags,
            ),
            node(
                func=prm_products.build_card_month_end,
                inputs={
                    "billing": "raw_stg_billing",
                    "balance": "raw_stg_balance",
                    "account_group": "raw_stg_account_group",
                    **window,
                },
                outputs="prm_card_month_end",
                name="build_prm_card_month_end",
                tags=tags,
            ),
            node(
                func=prm_products.build_loan_month_end,
                inputs={"loan_portfolio": "bo_rr_portf_actv_acct_mthly", **window},
                outputs="prm_loan_month_end",
                name="build_prm_loan_month_end",
                tags=tags,
            ),
        ]
    )
