"""Kedro pipeline: RL-B2 — T0 anchor table for Retail Loan persona pipeline."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_spell_table


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [crx_rl_full_history, rl_spine] → crx_rl_spell_table.

    crx_rl_full_history (RL-B1) provides the full monthly history from which
    T0 (first DLQ >= 1 onset) is derived. rl_spine (model_id-namespaced) provides
    the censored fallback for the ~0% of accounts with no DLQ >= 1 in history.

    No date filter applied — full history required to find true first delinquency
    onset. Date filtering is applied downstream in crx_rl_a4_spine.

    Run with:
        kedro run --pipeline=crx_rl_spell_table
    """
    return Pipeline(
        [
            node(
                func=build_rl_spell_table,
                inputs=["crx_rl_full_history", "rl_spine"],
                outputs="crx_rl_spell_table",
                name="build_crx_rl_spell_table",
                tags=["crx", "rl", "rl_b2"],
            ),
        ],
        tags=["crx_persona"],
    )
