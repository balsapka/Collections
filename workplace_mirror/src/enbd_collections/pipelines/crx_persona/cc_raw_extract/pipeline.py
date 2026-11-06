"""Kedro pipeline: CRX CC raw DDI extract (5 intermediate datasets) for A3.

build_cc_acct_windows reads the obs base and A4 (the episode anchor), so this runs
after crx_cc_a4_deterioration and before crx_cc_a3_payment_credibility. The three A3
extracts (transactions, balance, billing) read its window; build_cc_limits keeps its own
spell-table window.

Run with:
    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_cc_acct_windows,
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Five-node pipeline: build window-scoped CC raw extract intermediates."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs=[
                    "crx_cc_obs_base",
                    "crx_cc_a4_deterioration",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs=["raw_transaction", "crx_cc_acct_windows"],
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
                    "crx_cc_acct_windows",
                ],
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs=["raw_stg_billing", "crx_cc_acct_windows"],
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
