"""Kedro pipeline: T03 — CC delinquency-spell table (raw_stg_billing → crx_cc_spell_table)."""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_spell_table


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [raw_stg_billing, cc_spine] → crx_cc_spell_table.

    raw_stg_billing provides full DLQ history (all levels 0-9, all dates) for
    all accounts. cc_spine (model_id-namespaced) scopes the scan to the target
    population via leftsemi join. Must run after the spine pipeline for the
    relevant model_id (cc_60_180.spine or cc_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_cc_spell_table
    """
    return Pipeline(
        [
            node(
                func=build_cc_spell_table,
                inputs=["raw_stg_billing", "cc_spine"],
                outputs="crx_cc_spell_table",
                name="build_crx_cc_spell_table",
                tags=["crx", "spell", "t03"],
            ),
        ],
        tags=["crx_persona"],
    )
