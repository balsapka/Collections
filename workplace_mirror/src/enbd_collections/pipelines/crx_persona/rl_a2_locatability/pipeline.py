"""Kedro pipeline: RL A2 locatability axis on the shared ``a2_locatability`` engine.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``digital_login``, ``casa_primary`` and ``location_features``.

    kedro run --pipeline=crx_rl_a2_locatability

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` — see
``a2_locatability/pipeline.py``.
"""

from kedro.pipeline import Pipeline

from ..a2_locatability.pipeline import create_a2_pipeline
from ..a2_locatability.pipeline import create_b06_check_pipeline as _b06_check


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a2_locatability", **kwargs
) -> Pipeline:
    """The RL A2 axis written to ``output``."""
    return create_a2_pipeline("rl", output)


def create_b06_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the RL A2 check (bundle 06)."""
    return _b06_check("rl")
