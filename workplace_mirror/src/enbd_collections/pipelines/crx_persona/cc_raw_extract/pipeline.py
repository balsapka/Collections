"""Kedro pipeline: T04c — CRX CC raw DDI extract (3 intermediate datasets).

Promotes the T0-scoped raw extracts (formerly private helpers inside T04b) to
persisted intermediate catalog datasets so that T04b, T05, and T06 all consume
the same pre-scoped, pre-enriched tables instead of re-reading prm_* or raw_*
directly.

Run with:
    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_balance, build_cc_limits, build_cc_transactions


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Three-node pipeline: build T0-scoped CC raw extract intermediates."""
    return Pipeline(
        [
            node(
                func=build_cc_transactions,
                inputs=["raw_transaction", "crx_cc_spell_table"],
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs=["raw_stg_limit", "crx_cc_spell_table"],
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs=[
                    "raw_stg_balance",
                    "raw_stg_account_group",
                    "crx_cc_spell_table",
                ],
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
