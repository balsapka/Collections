"""Kedro pipeline: CC A2 locatability axis on the shared ``a2_locatability`` engine.

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``digital_login``, ``casa_primary`` and ``location_features``.

    kedro run --pipeline=crx_cc_a2_locatability
"""

from kedro.pipeline import Pipeline

from ..a2_locatability.pipeline import create_a2_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a2_locatability", **kwargs
) -> Pipeline:
    """The CC A2 axis written to ``output``."""
    return create_a2_pipeline("cc", output)
