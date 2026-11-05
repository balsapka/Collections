"""Kedro pipeline: RL A4 deterioration state (retail loans).

4-node pipeline:
    Node 1  build_rl_full_history_linked -> crx_rl_full_history_linked,
                                            crx_rl_restructure_chains
    Node 2  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 3  build_rl_linked_dpd_sequences -> crx_rl_dpd_sequences_linked
    Node 4  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration

TEMPORARY: create_b13_check_pipeline writes the new state to temporary entries and logs
old vs new; removed by its cleanup prompt.
"""

from kedro.pipeline import Pipeline, node

from .b13_check import compare_rl_a4_outputs
from .nodes import (
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
    build_rl_linked_dpd_sequences,
)


def _linked_node() -> node:
    return node(
        func=build_rl_full_history_linked,
        inputs={
            "crx_rl_full_history": "crx_rl_full_history",
            "int_loan_master": "int_loan_master",
            "int_loan_restructure_link": "int_loan_restructure_link",
        },
        outputs=["crx_rl_full_history_linked", "crx_rl_restructure_chains"],
        name="build_crx_rl_full_history_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _sequences_node(output: str) -> node:
    return node(
        func=build_rl_dpd_sequences,
        inputs={
            "crx_rl_full_history": "crx_rl_full_history",
            "feature_retail_loans": "feature_retail_loans",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
        outputs=output,
        name=f"build_{output}",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _linked_sequences_node() -> node:
    return node(
        func=build_rl_linked_dpd_sequences,
        inputs={
            "crx_rl_full_history_linked": "crx_rl_full_history_linked",
            "crx_rl_restructure_chains": "crx_rl_restructure_chains",
            "feature_retail_loans": "feature_retail_loans",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
        outputs="crx_rl_dpd_sequences_linked",
        name="build_crx_rl_dpd_sequences_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _state_node(own: str, output: str) -> node:
    return node(
        func=build_rl_a4_deterioration,
        inputs={
            "crx_rl_dpd_sequences": own,
            "crx_rl_dpd_sequences_linked": "crx_rl_dpd_sequences_linked",
            "crx_rl_restructure_chains": "crx_rl_restructure_chains",
            "rl_spine": "rl_spine",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
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


def create_b13_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the new RL A4 into temporary entries, then old vs new."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_dpd_sequences_b13_check"),
            _linked_sequences_node(),
            _state_node(
                "crx_rl_dpd_sequences_b13_check", "crx_rl_a4_deterioration_b13_check"
            ),
            node(
                func=compare_rl_a4_outputs,
                inputs=[
                    "crx_rl_a4_deterioration",
                    "crx_rl_a4_deterioration_b13_check",
                    "feature_retail_loans",
                    "rl_spine",
                    "params:model_id",
                ],
                outputs=None,
                name="compare_rl_a4_outputs",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
