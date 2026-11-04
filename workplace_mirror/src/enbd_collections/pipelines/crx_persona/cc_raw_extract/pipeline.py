"""Kedro pipeline: T04c — CRX CC raw DDI extract (5 intermediate datasets).

Promotes the T0-scoped raw extracts (formerly private helpers inside T04b) to
persisted intermediate catalog datasets so that T04b, T05, T06 and A3 Dimension
B/C all consume the same pre-scoped, pre-enriched tables instead of re-reading
prm_* or raw_* directly.

build_cc_acct_windows computes the shared per-account [acct_start, acct_end]
window once; build_cc_transactions, build_cc_balance and build_cc_billing all
consume its output (crx_cc_acct_windows) instead of each independently
recomputing the same crx_cc_spell_table/cc_spine aggregation. The window's
forward edge is cc_spine-anchored (not just T0) — needed by A3 Dimension B,
which looks at payment behaviour after onset. build_cc_billing is new,
providing the billing-cycle header (billing_date, due_date, next_billing_date)
A3 Dimension B/C's payment-attribution helper is built on. build_cc_limits
keeps its own self-contained T0-only window (see nodes.py docstring) and does
not consume crx_cc_acct_windows.

build_cc_acct_windows also takes params:cc_a3_history_floor_date: spine accounts
without a non-censored spell get a window starting no earlier than it, so A3 has
payment cycles for them (the other consumers are unaffected, see nodes.py).

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
                    "crx_cc_spell_table",
                    "cc_spine",
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
