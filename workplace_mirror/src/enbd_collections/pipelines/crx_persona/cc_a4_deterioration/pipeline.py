"""Kedro pipeline: CC A4 deterioration state (credit cards).

2-node pipeline:
    Node 1  build_cc_dpd_sequences       -> crx_cc_dpd_sequences
    Node 2  build_cc_a4_deterioration    -> crx_cc_a4_deterioration

Requires crx_cc_full_history to already be materialized.

Run with:
    kedro run --pipeline=crx_cc_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_a4_deterioration, build_cc_dpd_sequences

TAGS = ["crx_persona", "crx", "a4", "deterioration", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Build per-account DPD sequences, then classify the deterioration state."""
    return Pipeline(
        [
            node(
                func=build_cc_dpd_sequences,
                inputs={
                    "crx_cc_full_history": "crx_cc_full_history",
                    "crx_persona": "params:crx_persona",
                    "model_id": "params:model_id",
                },
                outputs="crx_cc_dpd_sequences",
                name="build_crx_cc_dpd_sequences",
                tags=TAGS,
            ),
            node(
                func=build_cc_a4_deterioration,
                inputs={
                    "crx_cc_dpd_sequences": "crx_cc_dpd_sequences",
                    "cc_spine": "cc_spine",
                    "crx_persona": "params:crx_persona",
                    "model_id": "params:model_id",
                },
                outputs="crx_cc_a4_deterioration",
                name="build_crx_cc_a4_deterioration",
                tags=TAGS,
            ),
        ],
    )
