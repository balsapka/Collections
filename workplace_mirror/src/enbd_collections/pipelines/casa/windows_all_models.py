"""All-models pipeline: one inflow / outflow / salary table for the customers of all four models.

    feat_cif_inflow_outflow_salary_monthly_<model_id> (x4, hardcoded model ids)
        --> union_models --> feat_cif_inflow_outflow_salary_monthly_all_models

Each per-model table comes from ``casa_windows`` run once per ``model_id``. They are stacked,
cut at ``persona_end_date`` and reduced to one row per ``(cif_id, month_end)``; the active
``model_id`` does not matter here.

    kedro run --pipeline=casa_windows_all_models
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_windows

TABLE = "feat_cif_inflow_outflow_salary_monthly"


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Union and de-duplicate the four per-model tables."""
    return Pipeline(
        [
            node(
                func=feat_cif_windows.union_models,
                inputs={
                    "persona_end_date": "params:crx_persona.persona_end_date",
                    **{m: f"{TABLE}_{m}" for m in feat_cif_windows.MODEL_IDS},
                },
                outputs=f"{TABLE}_all_models",
                name=f"union_{TABLE}",
                tags=["casa", "features"],
            ),
        ]
    )
