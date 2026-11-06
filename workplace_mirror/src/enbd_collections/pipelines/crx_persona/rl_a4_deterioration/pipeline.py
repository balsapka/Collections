"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

4-node pipeline:
    Node 1  build_rl_full_history_linked -> crx_rl_full_history_linked,
                                            crx_rl_restructure_chains
    Node 2  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 3  build_rl_linked_dpd_sequences -> crx_rl_dpd_sequences_linked
    Node 4  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
    build_rl_linked_dpd_sequences,
)


def _linked_node() -> node:
    return node(
        func=build_rl_full_history_linked,
        inputs=[
            "crx_rl_full_history",
            "int_loan_master",
            "int_loan_restructure_link",
        ],
        outputs=["crx_rl_full_history_linked", "crx_rl_restructure_chains"],
        name="build_crx_rl_full_history_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _sequences_node(output: str) -> node:
    return node(
        func=build_rl_dpd_sequences,
        inputs=[
            "crx_rl_full_history",
            "feature_retail_loans",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _linked_sequences_node() -> node:
    return node(
        func=build_rl_linked_dpd_sequences,
        inputs=[
            "crx_rl_full_history_linked",
            "crx_rl_restructure_chains",
            "feature_retail_loans",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs="crx_rl_dpd_sequences_linked",
        name="build_crx_rl_dpd_sequences_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _state_node(own: str, output: str) -> node:
    return node(
        func=build_rl_a4_deterioration,
        inputs=[
            own,
            "crx_rl_dpd_sequences_linked",
            "crx_rl_restructure_chains",
            "rl_spine",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Link the restructured loans, build both sequences, classify deterioration state."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_dpd_sequences"),
            _linked_sequences_node(),
            _state_node("crx_rl_dpd_sequences", "crx_rl_a4_deterioration"),
        ],
        tags=["crx_persona"],
    )
