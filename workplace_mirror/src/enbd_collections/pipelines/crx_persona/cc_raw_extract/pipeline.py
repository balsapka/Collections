"""Kedro pipeline: the CC raw extract for A3.

``build_cc_acct_windows`` reads the obs base and A4 (the episode anchor), so this runs
after ``crx_cc_a4_deterioration`` and before ``crx_cc_a3_payment_credibility``. The
transactions, balance and billing extracts read its windows.

    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from ..cc_a3_payment_credibility.nodes import build_cc_acct_windows
from .nodes import (
    build_cc_balance,
    build_cc_billing,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The account windows and the three extracts."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs={
                    "obs_base": "crx_cc_obs_base",
                    "deterioration": "crx_cc_a4_deterioration",
                    "history_floor_date": "params:cc_a3_history_floor_date",
                },
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs={
                    "raw_transaction": "raw_transaction",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs={
                    "raw_stg_balance": "raw_stg_balance",
                    "raw_stg_account_group": "raw_stg_account_group",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs={
                    "raw_stg_billing": "raw_stg_billing",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
