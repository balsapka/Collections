"""Wiring of the CC / RL deterioration pipelines — no Spark, no data.

Workplace location: src/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py.
Run: python -m pytest src/tests/pipelines/crx_persona
"""
import pytest

from enbd_collections.pipelines.crx_persona import _dpd_journey as J
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration import nodes as cc_nodes
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import (
    create_pipeline as create_cc_pipeline)
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration import nodes as rl_nodes
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import (
    create_pipeline as create_rl_pipeline)

EXPECTED = {
    "cc": (create_cc_pipeline, [
        ("build_crx_cc_dpd_sequences", cc_nodes.build_cc_dpd_sequences,
         ["crx_cc_full_history", "crx_cc_spell_table", "params:crx_persona"], ["crx_cc_dpd_sequences"]),
        ("build_crx_cc_a4_deterioration", cc_nodes.build_cc_a4_deterioration,
         ["crx_cc_dpd_sequences", "params:crx_persona"], ["crx_cc_a4_deterioration"]),
    ]),
    "rl": (create_rl_pipeline, [
        ("build_crx_rl_dpd_sequences", rl_nodes.build_rl_dpd_sequences,
         ["crx_rl_full_history", "params:crx_persona"], ["crx_rl_dpd_sequences"]),
        ("build_crx_rl_a4_deterioration", rl_nodes.build_rl_a4_deterioration,
         ["crx_rl_dpd_sequences", "params:crx_persona"], ["crx_rl_a4_deterioration"]),
    ]),
}


@pytest.mark.parametrize("product", sorted(EXPECTED))
def test_pipeline_wiring(product):
    create, spec = EXPECTED[product]
    pipe = create()
    by_name = {n.name.split(".")[-1]: n for n in pipe.nodes}     # namespaced names end in the node name
    assert set(by_name) == {name for name, *_ in spec}
    for name, func, inputs, outputs in spec:
        n = by_name[name]
        assert n.func is func
        assert n.inputs == inputs
        assert n.outputs == outputs
        assert {"crx", product, "crx_persona"} <= set(n.tags)


@pytest.mark.parametrize("product", sorted(EXPECTED))
def test_sequences_run_before_classification(product):
    pipe = EXPECTED[product][0]()
    order = [n.name.split(".")[-1] for n in pipe.nodes]          # Kedro returns topological order
    assert order.index(f"build_crx_{product}_dpd_sequences") < order.index(f"build_crx_{product}_a4_deterioration")


def test_params_defaults_are_valid():
    """The params the nodes read: defaults resolve, and a bad value fails loudly."""
    p = J.journey_params({"persona_end_date": "2026-08-31"}, J.CC)
    assert p.floor_date == "2024-01-01" and p.segment == "60_180"
    assert J.journey_params({"persona_end_date": "2026-08-31"}, J.RL).floor_date is None
    with pytest.raises(ValueError):
        J.journey_params({"persona_end_date": "2026-08-31", "dpd_journey": {"segment": "90_plus"}}, J.CC)
    with pytest.raises(ValueError):    # stale key from the old A/B/C options must not pass silently
        J.journey_params({"persona_end_date": "2026-08-31", "dpd_journey": {"det_option": "B_balanced_6"}}, J.CC)
