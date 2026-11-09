"""Kedro pipeline: RL A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (the month's EMI) and the payments (the month's cash).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``crx_rl_a4_deterioration``, ``int_loan_master`` and the DCORE tables.

    kedro run --pipeline=crx_rl_a3_payment_credibility

TEMPORARY (A3 bundle 20): ``create_check_pipeline`` (``a3_credibility/check.py``);
removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a3_credibility.check import create_a3_check_pipeline
from ..a3_credibility.pipeline import TAGS, create_a3_pipeline
from .nodes import build_rl_a3_dues, build_rl_a3_payments

_SOURCES = {"int_loan_master": "int_loan_master", "obs_base": "crx_rl_obs_base"}
DUES = node(
    func=build_rl_a3_dues,
    inputs=_SOURCES,
    outputs="crx_rl_a3_dues",
    name="build_crx_rl_a3_dues",
    tags=TAGS,
)
PAYMENTS = node(
    func=build_rl_a3_payments,
    inputs=_SOURCES,
    outputs="crx_rl_a3_payments",
    name="build_crx_rl_a3_payments",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a3_payment_credibility", **kwargs
) -> Pipeline:
    """The RL A3 axis written to ``output``."""
    return create_a3_pipeline("rl", output, DUES, PAYMENTS)


def create_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the A3 bundle 20 check for RL."""
    return create_a3_check_pipeline("rl", DUES, PAYMENTS)
