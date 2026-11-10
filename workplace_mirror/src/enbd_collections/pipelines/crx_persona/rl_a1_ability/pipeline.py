"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``) and the loan's latest bureau pull adds a salary source.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.check import create_a1_check_pipeline
from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_rl_liquidity_anchor

_ANCHOR = node(
    func=build_rl_liquidity_anchor,
    inputs={"obs_base": "crx_rl_obs_base", "int_loan_master": "int_loan_master"},
    outputs="crx_rl_a1_liquidity_anchor",
    name="build_crx_rl_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability", **kwargs
) -> Pipeline:
    """The RL A1 axis written to ``output``."""
    return create_a1_pipeline("rl", output, _ANCHOR)


def create_check_pipeline() -> Pipeline:
    """TEMPORARY (A1 bundle 21): the new rule against the persisted ``crx_rl_a1_ability``;
    removed by the bundle's cleanup."""
    return create_a1_check_pipeline("rl", _ANCHOR)
