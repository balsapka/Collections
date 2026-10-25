"""Kedro pipeline: OMB digital login staging + primary aggregation.

Wiring:
    raw_digital_login_data         }
    raw_digital_login_data_history } → stg_digital_login → prm_digital_login_monthly
    raw_digital_user_data          }

Run with:
    kedro run --pipeline=digital_login
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.staging.digital_login import stg_digital_login
from enbd_collections.nodes.primary.digital_login import prm_digital_login_monthly


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Two-node pipeline: stage OMB login events then aggregate to monthly grain."""
    return Pipeline(
        [
            node(
                func=stg_digital_login.build,
                inputs=[
                    "raw_digital_login_data",
                    "raw_digital_login_data_history",
                    "raw_digital_user_data",
                ],
                outputs="stg_digital_login",
                name="build_stg_digital_login",
                tags=["digital_login", "staging"],
            ),
            node(
                func=prm_digital_login_monthly.build,
                inputs=["stg_digital_login"],
                outputs="prm_digital_login_monthly",
                name="build_prm_digital_login_monthly",
                tags=["digital_login", "primary"],
            ),
        ]
    )
