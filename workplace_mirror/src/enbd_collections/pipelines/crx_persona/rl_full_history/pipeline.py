"""Kedro pipeline: RL-B1 — Full pre-delinquency monthly history."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_full_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [rl_spine, int_loan_master] → crx_rl_full_history.

    int_loan_master provides the full monthly-grain delinquency history. rl_spine
    (model_id-namespaced) scopes scan to target population via leftsemi join. No
    date window applied — full history required for T0 identification (RL-B2) and
    pre-T0 A4 lookback (RL-A4-2).

    Must run after the spine pipeline for the relevant model_id
    (rl_60_180.spine or rl_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_rl_full_history
    """
    return Pipeline(
        [
            node(
                func=build_rl_full_history,
                inputs=["rl_spine", "int_loan_master", "params:crx_persona"],
                outputs="crx_rl_full_history",
                name="build_crx_rl_full_history",
                tags=["crx", "rl", "rl_b1"],
            ),
        ],
        tags=["crx_persona"],
    )
