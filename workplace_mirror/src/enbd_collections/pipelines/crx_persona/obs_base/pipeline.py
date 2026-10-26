"""Kedro pipelines building the observation base every persona axis reads: the spine's
month-end rows from ``crx_persona.persona_start_date`` to ``persona_end_date``.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_cc_obs_base from cc_spine."""
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs=["cc_spine", "params:crx_persona"],
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_rl_obs_base from rl_spine."""
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs=["rl_spine", "params:crx_persona"],
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )
