"""Kedro pipeline: CC A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (statement cycles) and the payments (card payments).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``crx_cc_a4_deterioration``, ``crx_cc_raw_extract`` (billing, balance, transactions)
and the DCORE tables.

    kedro run --pipeline=crx_cc_a3_payment_credibility

TEMPORARY (A3 bundle 23): ``create_check_pipeline`` (``a3_credibility/check.py``);
removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a3_credibility.check import create_a3_check_pipeline
from ..a3_credibility.pipeline import TAGS, create_a3_pipeline
from .nodes import build_cc_a3_dues, build_cc_a3_payments

DUES = node(
    func=build_cc_a3_dues,
    inputs={
        "billing": "crx_cc_billing",
        "balance": "crx_cc_balance",
        "history_floor_date": "params:cc_a3_history_floor_date",
    },
    outputs="crx_cc_a3_dues",
    name="build_crx_cc_a3_dues",
    tags=TAGS,
)
PAYMENTS = node(
    func=build_cc_a3_payments,
    inputs={"transactions": "crx_cc_transactions"},
    outputs="crx_cc_a3_payments",
    name="build_crx_cc_a3_payments",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a3_payment_credibility", **kwargs
) -> Pipeline:
    """The CC A3 axis written to ``output``."""
    return create_a3_pipeline("cc", output, DUES, PAYMENTS)


def create_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the A3 bundle 23 check for CC."""
    return create_a3_check_pipeline("cc", DUES, PAYMENTS)
