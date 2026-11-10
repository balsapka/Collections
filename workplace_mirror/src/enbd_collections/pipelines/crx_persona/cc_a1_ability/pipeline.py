"""Kedro pipeline: CC A1 ability axis on the shared ``a1_ability`` engine; the anchor is
the amount in the oldest overdue bucket (``nodes.py``).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_cc_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.check import create_a1_check_pipeline
from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_cc_liquidity_anchor

_ANCHOR = node(
    func=build_cc_liquidity_anchor,
    inputs={
        "obs_base": "crx_cc_obs_base",
        "prm_balance": "prm_balance",
        "model_id": "params:model_id",
    },
    outputs="crx_cc_a1_liquidity_anchor",
    name="build_crx_cc_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a1_ability", **kwargs
) -> Pipeline:
    """The CC A1 axis written to ``output``."""
    return create_a1_pipeline("cc", output, _ANCHOR)


def create_check_pipeline() -> Pipeline:
    """TEMPORARY (A1 bundle 21): the new rule against the persisted ``crx_cc_a1_ability``;
    removed by the bundle's cleanup."""
    return create_a1_check_pipeline("cc", _ANCHOR)
