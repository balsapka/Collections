"""Kedro pipeline: CC A1 ability axis on the shared ``a1_ability`` engine; the anchor is
the amount in the oldest overdue bucket (``nodes.py``).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_cc_a1_ability

TEMPORARY (mirror bundle 08): ``create_b08_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b08_check_pipeline as _b08_check
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


def create_b08_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the CC A1 check (bundle 08)."""
    return _b08_check("cc", _ANCHOR)
