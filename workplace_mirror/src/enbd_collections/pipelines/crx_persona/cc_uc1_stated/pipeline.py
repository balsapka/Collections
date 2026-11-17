"""Kedro pipeline: CC UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``.

    kedro run --pipeline=crx_cc_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_uc1_stated", **kwargs
) -> Pipeline:
    """The CC UC1 stated block written to ``output``."""
    return create_uc1_pipeline("cc", output)
