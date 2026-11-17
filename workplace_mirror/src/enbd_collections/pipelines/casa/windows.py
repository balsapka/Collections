"""CASA window pipeline: 1 / 3 / 6 / 12 month CASA flow and salary per customer, one table.

    wm_fea_casa_cc_inflow_outflow --------------------------------> flow --+
    feat_cif_internal_salary_monthly (``casa_features``),                  +-> join
    feat_cif_bureau_salary_monthly (``bureau_salary_bounces``,             |
        from prm_bureau_alert_enriched only) -----------------------> salary -+
                                                  feat_cif_inflow_outflow_salary_monthly <-+

``flow`` and ``salary`` are in-memory intermediates; all history. The salary node needs both salary
tables for the model_id first.

    kedro run --pipeline=casa_windows
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_windows


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The windowed monthly CASA flow and salary table."""
    tags = ["casa", "features"]
    return Pipeline(
        [
            node(
                func=feat_cif_windows.build_casa_flow,
                inputs={"wm_casa_flow": "wm_fea_casa_cc_inflow_outflow"},
                outputs="casa_flow_windows",
                name="build_casa_flow_windows",
                tags=tags,
            ),
            node(
                func=feat_cif_windows.build_salary_windows,
                inputs={
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                },
                outputs="casa_salary_windows",
                name="build_casa_salary_windows",
                tags=tags,
            ),
            node(
                func=feat_cif_windows.join_windows,
                inputs={
                    "flow": "casa_flow_windows",
                    "salary": "casa_salary_windows",
                },
                outputs="feat_cif_inflow_outflow_salary_monthly",
                name="build_feat_cif_inflow_outflow_salary_monthly",
                tags=tags,
            ),
        ]
    )
