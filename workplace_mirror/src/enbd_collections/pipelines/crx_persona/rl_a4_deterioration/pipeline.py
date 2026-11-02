"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

2-node pipeline:
    Node 1  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 2  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration

TEMPORARY (mirror bundle 11): create_b11_check_pipeline writes the new state to temporary
entries and logs old vs new; removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .b11_check import compare_rl_a4_outputs
from .nodes import build_rl_a4_deterioration, build_rl_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=[
                    "crx_rl_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_dpd_sequences",
                name="build_crx_rl_dpd_sequences",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=[
                    "crx_rl_dpd_sequences",
                    "rl_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_a4_deterioration",
                name="build_crx_rl_a4_deterioration",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )


def create_b11_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the new RL A4 into temporary entries, then old vs new (bundle 11)."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=[
                    "crx_rl_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_dpd_sequences_b11_check",
                name="build_crx_rl_dpd_sequences_b11_check",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=[
                    "crx_rl_dpd_sequences_b11_check",
                    "rl_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_a4_deterioration_b11_check",
                name="build_crx_rl_a4_deterioration_b11_check",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=compare_rl_a4_outputs,
                inputs=[
                    "crx_rl_a4_deterioration",
                    "crx_rl_a4_deterioration_b11_check",
                    "crx_rl_dpd_sequences_b11_check",
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
