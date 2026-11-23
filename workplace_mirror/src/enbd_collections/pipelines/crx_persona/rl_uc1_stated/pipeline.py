"""Kedro pipeline: RL UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``, ``crx_rl_a1_ability``,
``crx_rl_a3_promise_events``.

    kedro run --pipeline=crx_rl_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_uc1_stated", **kwargs
) -> Pipeline:
    """The RL UC1 stated block written to ``output``."""
    return create_uc1_pipeline("rl", output)
