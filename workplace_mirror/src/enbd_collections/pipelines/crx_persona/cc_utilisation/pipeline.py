"""Kedro pipeline: T05 — CC utilisation, spend & liquidity features.

Input wiring note:
    crx_cc_limits (catalog key) replaces prm_limit.
    crx_cc_transactions replaces prm_transaction.
    Both are T04c intermediates (T0-scoped DDI raw extracts) with full history
    needed for cc_180_plus accounts where T0 may be 18-24+ months before
    observation_date.

    crx_cc_payment_trajectory is the 4th input — provides w_pre truncation
    columns (w_pre_start, w_pre_clean_m, w_pre_contaminated_flag,
    w_pre_truncation_reason) computed in T04b, avoiding re-derivation here.

Run with:
    kedro run --pipeline=crx_cc_utilisation_features
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_utilisation_features


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: build CC utilisation features."""
    return Pipeline(
        [
            node(
                func=build_cc_utilisation_features,
                inputs=[
                    "crx_cc_limits",
                    "crx_cc_transactions",
                    "crx_cc_spell_table",
                    "crx_cc_payment_trajectory",
                ],
                outputs="crx_cc_utilisation_features",
                name="build_crx_cc_utilisation_features",
                tags=["crx", "utilisation", "t05"],
            ),
        ],
        tags=["crx_persona"],
    )
