"""Bureau salary and bounce inputs of the persona axes (per model_id).

    prm_bureau_alert_enriched ─┬─► feat_cif_bureau_salary_monthly
                               └─► feat_cif_bureau_bounces_monthly

Needs ``bureau_staging`` and ``bureau_primary`` (the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
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
