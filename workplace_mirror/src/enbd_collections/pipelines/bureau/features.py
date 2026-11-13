"""Kedro pipeline: AECB bureau feature layer.

Feature sets:
- feat_bureau_alert: rolling window alert features (Tier A, ~93 features)
- feat_bureau_pull: rolling window bureau pull features (Tier B, ~54 features)
- feat_bureau_snapshot: latest-pull-before-observation snapshot (8 features)
- feat_bureau_salary_unified: one monthly salary per CIF unified across 3 salary sources
"""

from pyspark.sql import DataFrame
from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_bureau_alert,
    feat_bureau_pull,
    feat_bureau_salary_unified,
    feat_bureau_snapshot,
)


def _join_bureau_features(
    alert_features: DataFrame,
    pull_features: DataFrame,
    snapshot_features: DataFrame,
) -> DataFrame:
    """Join bureau alert, pull, and snapshot features on [cif_id, observation_date]."""
    return alert_features.join(
        pull_features, on=["cif_id", "observation_date"], how="outer"
    ).join(snapshot_features, on=["cif_id", "observation_date"], how="outer")


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Feature layer pipeline: rolling window bureau alert + pull features."""
    return Pipeline(
        [
            # --- Tier A: Alert features ---
            node(
                func=feat_bureau_alert.build,
                inputs=[
                    "int_bureau_alert_monthly",
                    "observation_dates_bureau",
                ],
                outputs="feat_bureau_alert",
                name="build_feat_bureau_alert",
            ),
            # --- Tier B: Bureau pull features ---
            node(
                func=feat_bureau_pull.build,
                inputs=[
                    "int_bureau_pull_monthly",
                    "observation_dates_bureau",
                ],
                outputs="feat_bureau_pull",
                name="build_feat_bureau_pull",
            ),
            # --- Tier C: Bureau snapshot (latest pull before observation) ---
            node(
                func=feat_bureau_snapshot.build,
                inputs=[
                    "int_bureau_pull_monthly",
                    "observation_dates_bureau",
                ],
                outputs="feat_bureau_snapshot",
                name="build_feat_bureau_snapshot",
            ),
            # --- Unified monthly salary per CIF: alert > salary credit > bureau salary ---
            node(
                func=feat_bureau_salary_unified.build,
                inputs=[
                    "int_bureau_alert_salary_monthly",
                    "int_bureau_salary_credit_monthly",
                    "int_bureau_salary_monthly",
                    "scope_cifs",
                    "params:modelling",
                ],
                outputs="feat_bureau_salary_unified",
                name="build_feat_bureau_salary_unified",
            ),
            node(
                func=_join_bureau_features,
                inputs=[
                    "feat_bureau_alert",
                    "feat_bureau_pull",
                    "feat_bureau_snapshot",
                ],
                outputs="feat_bureau",
                name="join_bureau_features",
                tags=["aecb", "features"],
            ),
        ],
        tags=["aecb", "features"],
    )
