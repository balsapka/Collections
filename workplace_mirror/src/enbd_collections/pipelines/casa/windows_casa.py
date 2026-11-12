"""CASA window pipeline, CASA schemes only: inflow, outflow, net flow and salary per customer.

    wm_pri_labelled_transactions --+ (legs on current / savings accounts only)
    prm_casa_accounts -------------+--------> flow ------------------+
    feat_cif_internal_salary_monthly (``casa_features``),            +-> join
    feat_cif_bureau_salary_monthly (``bureau_salary_bounces``) --> salary -+
                                      feat_cif_casa_inflow_outflow_salary_monthly <-+

Same columns as ``casa_windows`` (``feat_cif_inflow_outflow_salary_monthly``), but the
flows exclude loan and other non-CASA accounts. ``flow`` and ``salary`` are in-memory
intermediates; all history. Needs ``casa_primary`` (``prm_casa_accounts``), ``casa_features``
and ``bureau_salary_bounces`` for the model_id first.

    kedro run --pipeline=casa_windows_casa
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_casa_flow, feat_cif_windows


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The CASA-scheme inflow / outflow / net flow and salary table."""
    tags = ["casa", "features"]
    return Pipeline(
        [
            node(
                func=feat_cif_casa_flow.build_casa_scheme_flow,
                inputs={
                    "wm_labelled": "wm_pri_labelled_transactions",
                    "casa_accounts": "prm_casa_accounts",
                },
                outputs="casa_scheme_flow_windows",
                name="build_casa_scheme_flow_windows",
                tags=tags,
            ),
            node(
                func=feat_cif_windows.build_salary_windows,
                inputs={
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                },
                outputs="casa_scheme_salary_windows",
                name="build_casa_scheme_salary_windows",
                tags=tags,
            ),
            node(
                func=feat_cif_windows.join_windows,
                inputs={
                    "flow": "casa_scheme_flow_windows",
                    "salary": "casa_scheme_salary_windows",
                },
                outputs="feat_cif_casa_inflow_outflow_salary_monthly",
                name="build_feat_cif_casa_inflow_outflow_salary_monthly",
                tags=tags,
            ),
        ]
    )
