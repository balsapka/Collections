"""CASA primary pipeline.

kedro run --pipeline=casa_primary   (per model_id)
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import (
    build_card_transactions,
    build_return_events,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events and prm_casa_card_transactions from
    comp_financial_tran_repos_dly."""
    return Pipeline(
        [
            node(
                func=build_return_events,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:casa_primary.return_reasons",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.history_months",
                ],
                outputs="prm_casa_return_events",
                name="build_prm_casa_return_events",
                tags=["casa", "primary"],
            ),
            node(
                func=build_card_transactions,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.card_history_months",
                ],
                outputs="prm_casa_card_transactions",
                name="build_prm_casa_card_transactions",
                tags=["casa", "primary"],
            ),
        ],
    )
