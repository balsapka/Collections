"""Kedro pipeline: CC-A4 — DPD-journey deterioration state for Credit Cards.

2-node pipeline:
    Node 1  build_cc_dpd_sequences      -> crx_cc_dpd_sequences
    Node 2  build_cc_a4_deterioration   -> crx_cc_a4_deterioration

Requires crx_cc_full_history and crx_cc_spell_table to already be materialized.

Run with:
    kedro run --pipeline=crx_cc_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_a4_deterioration, build_cc_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_cc_dpd_sequences,
                inputs=["crx_cc_full_history", "crx_cc_spell_table", "params:crx_persona"],
                outputs="crx_cc_dpd_sequences",
                name="build_crx_cc_dpd_sequences",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
            node(
                func=build_cc_a4_deterioration,
                inputs=["crx_cc_dpd_sequences", "params:crx_persona"],
                outputs="crx_cc_a4_deterioration",
                name="build_crx_cc_a4_deterioration",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
