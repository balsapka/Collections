"""Kedro pipeline: RL A4 Spine — structural spine/spell window projection.

Replaces rl_a4_class's Node 2 (build_rl_a4_spine_projection), which broadcast a
now-superseded CASA/EMI classification onto the spine. crx_rl_a4_spine is now
a pure structural join — (account_id, cif_id, observation_date, spell_id, t0),
decoupled from any A4 classifier, scoped by crx_rl_a4_deterioration instead.

Reuses rl_departure_signature's build_rl_depart_spine (R14 — identical logic,
already exercised by that pipeline) rather than re-deriving the same join.

Run with:
    kedro run --pipeline=crx_rl_a4_spine
"""

from kedro.pipeline import Pipeline, node

from ..rl_departure_signature.nodes import build_rl_depart_spine

_TAGS = ["crx", "rl", "rl_a4_spine"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """One-node pipeline: rl_spine + crx_rl_spell_table -> crx_rl_a4_spine."""
    return Pipeline(
        [
            node(
                func=build_rl_depart_spine,
                inputs=[
                    "rl_spine",
                    "crx_rl_spell_table",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a4_spine",
                name="build_crx_rl_a4_spine",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
