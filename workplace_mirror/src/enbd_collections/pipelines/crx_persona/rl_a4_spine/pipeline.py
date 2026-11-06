"""Kedro pipeline: RL A4 Spine — structural spine/spell window projection.

Replaces rl_a4_class's Node 2 (build_rl_a4_spine_projection), which broadcast a
now-superseded CASA/EMI classification onto the spine. crx_rl_a4_spine is now
a pure structural join — (account_id, cif_id, observation_date, spell_id, t0),
decoupled from any A4 classifier, scoped by crx_rl_a4_deterioration instead.

Run with:
    kedro run --pipeline=crx_rl_a4_spine

TEMPORARY (refactor bundle R-A): ``create_ra_check_pipeline`` rebuilds the spine into
``crx_rl_a4_spine_ra_check`` and compares it with ``crx_rl_a4_spine``; removed by the
bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_depart_spine
from .ra_check import compare_rl_a4_spine

_TAGS = ["crx", "rl", "rl_a4_spine"]


def _spine_node(output: str) -> node:
    return node(
        func=build_rl_depart_spine,
        inputs=[
            "rl_spine",
            "crx_rl_spell_table",
            "params:crx_persona",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=_TAGS,
    )


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """One-node pipeline: rl_spine + crx_rl_spell_table -> crx_rl_a4_spine."""
    return Pipeline([_spine_node("crx_rl_a4_spine")], tags=["crx_persona"])


def create_ra_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the spine into crx_rl_a4_spine_ra_check, then old vs new (bundle R-A)."""
    return Pipeline(
        [
            _spine_node("crx_rl_a4_spine_ra_check"),
            node(
                func=compare_rl_a4_spine,
                inputs={
                    "old": "crx_rl_a4_spine",
                    "new": "crx_rl_a4_spine_ra_check",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name="compare_crx_rl_a4_spine_ra",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
