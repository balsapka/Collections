"""Kedro pipeline: T04b — CC payment & balance trajectory features (re-anchored).

Input wiring note:
    crx_cc_transactions and crx_cc_balance replace the raw/primary-layer inputs.
    Both are T04c intermediates built by crx_cc_raw_extract — T0-scoped per-account
    windows already extracted from the DDI-backed raw tables.

    prm_contract is used to derive account_open_month via the open_date column
    (Way4 monthly contract snapshots, one row per contract per observation month).

Run with:
    kedro run --pipeline=crx_cc_payment_trajectory
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_payment_trajectory


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: build CC payment trajectory from T04c intermediates + spells."""
    return Pipeline(
        [
            node(
                func=build_cc_payment_trajectory,
                inputs=[
                    "crx_cc_transactions",
                    "crx_cc_balance",
                    "crx_cc_spell_table",
                    "prm_contract",
                ],
                outputs="crx_cc_payment_trajectory",
                name="build_crx_cc_payment_trajectory",
                tags=["crx", "payment_trajectory", "t04b"],
            ),
        ],
        tags=["crx_persona"],
    )
