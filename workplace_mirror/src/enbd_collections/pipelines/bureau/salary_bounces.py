"""Bureau salary and bounce inputs of the persona axes (per model_id).

    stg_aecb_salary_history ─► prm_bureau_salary_history ─┐
                                 prm_bureau_cif_bridge ───┴─► feat_cif_bureau_salary_monthly
    prm_bureau_alert_enriched ──────────────────────────────► feat_cif_bureau_bounces_monthly

Needs ``bureau_staging`` and ``bureau_primary`` (the bridge and the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)
from enbd_collections.nodes.primary.bureau import prm_bureau_salary_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_bureau_salary_history and the two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=prm_bureau_salary_history.build,
                inputs={"stg_salary_history": "stg_aecb_salary_history"},
                outputs="prm_bureau_salary_history",
                name="build_prm_bureau_salary_history",
                tags=["bureau", "primary"],
            ),
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={
                    "salary_history": "prm_bureau_salary_history",
                    "cif_bridge": "prm_bureau_cif_bridge",
                },
                outputs="feat_cif_bureau_salary_monthly",
                name="build_feat_cif_bureau_salary_monthly",
                tags=["bureau", "features"],
            ),
            node(
                func=feat_cif_bureau_bounces_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_bounces_monthly",
                name="build_feat_cif_bureau_bounces_monthly",
                tags=["bureau", "features"],
            ),
        ]
    )
