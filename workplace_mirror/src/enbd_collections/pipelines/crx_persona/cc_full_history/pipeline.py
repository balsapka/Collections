"""Kedro pipeline: crx_cc_full_history — full billing history (ad hoc, mirrors RL-B1)."""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_full_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [raw_stg_billing, cc_spine] → crx_cc_full_history.

    raw_stg_billing provides the full billing history for all CC accounts.
    cc_spine (model_id-namespaced) scopes the scan to the target population
    via leftsemi join. Must run after the spine pipeline for the relevant
    model_id (cc_60_180.spine or cc_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_cc_full_history
    """
    return Pipeline(
        [
            node(
                func=build_cc_full_history,
                inputs=["raw_stg_billing", "cc_spine"],
                outputs="crx_cc_full_history",
                name="build_crx_cc_full_history",
                tags=["crx", "cc", "full_history"],
            ),
        ],
        tags=["crx_persona"],
    )
