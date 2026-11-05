"""Kedro pipeline: crx_rl_full_history, the monthly DPD history of the RL spine."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_full_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [rl_spine, int_loan_master] → crx_rl_full_history.

    int_loan_master provides the monthly delinquency history. rl_spine
    (model_id-namespaced) scopes it to the target population via leftsemi join. No
    date window is applied: the history is used in full.

    Must run after the spine pipeline for the relevant model_id
    (rl_60_180.spine or rl_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_rl_full_history
    """
    return Pipeline(
        [
            node(
                func=build_rl_full_history,
                inputs={
                    "rl_spine": "rl_spine",
                    "int_loan_master": "int_loan_master",
                    "crx_persona": "params:crx_persona",
                },
                outputs="crx_rl_full_history",
                name="build_crx_rl_full_history",
                tags=["crx", "rl", "rl_b1"],
            ),
        ],
        tags=["crx_persona"],
    )
