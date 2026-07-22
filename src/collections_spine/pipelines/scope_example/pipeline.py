"""Example STAGING pipeline for config-driven scope filtering.

Each staging node reduces one raw table with its OWN strategy AND its OWN scope
sets via ``scoped_stage``, then runs a pure transform. Different tables use
different scoping -- that per-node choice is the ``functools.partial`` config, so
nothing is duplicated.

Multiple id types
-----------------
There is no single global scope. Each id TYPE (customer, account, ...) has its own
``scope_ids`` and (for ``range``) its own ``windows`` / ``grid``, all produced
UPSTREAM by your own builders. A staging node picks the ``id_col`` and the scope
datasets that match the grain of its raw table -- see how ``stage_txns`` uses the
customer scope while ``stage_positions`` uses the account scope below.

Downstream primary / intermediate / feature pipelines read staged outputs only, so
they carry no scope wiring at all.

Register in ``pipeline_registry.py``::

    from src.collections_spine.pipelines.scope_example import create_staging_pipeline

    def register_pipelines():
        staging = create_staging_pipeline()
        return {"staging": staging, "__default__": staging}
"""

from functools import partial

from kedro.pipeline import Pipeline, node, pipeline

from src.collections_spine.scope import scoped_stage

# --- example config (move to conf/base/parameters.yml in real use) -----------
# global window extent for the coarse partition prune, computed once from the
# modelling window: [start - lookback, end + lookahead].
PRUNE_BOUNDS = ("2019-01-01", "2026-07-31")


# --------------------------------------------------------------------------- #
# pure transforms (DataFrame -> DataFrame). Reused unscoped by the spine layer.
# --------------------------------------------------------------------------- #
def stage_txns(df):
    # TODO(you): real staging logic
    return df


def stage_positions(df):
    # TODO(you): real staging logic
    return df


def stage_customer_dim(df):
    # TODO(you): real staging logic
    return df


def create_staging_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # CUSTOMER-grain, range: date filter via the customer windows; coarse-
            # prune the load col. Uses the CUSTOMER scope sets.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_txns,
                    id_col="customer_id",
                    strategy="range",
                    date_col="txn_date",
                    prune_col="load_date",
                    prune_bounds=PRUNE_BOUNDS,
                ),
                inputs={
                    "raw": "raw_txns",
                    "scope_ids": "customer_scope_ids",
                    "windows": "customer_windows",
                },
                outputs="txns_staged",
                name="stage_txns",
            ),
            # ACCOUNT-grain, grid: exact (account, month) equi-join -- this table is
            # month-partitioned. Uses a DIFFERENT id type and the ACCOUNT scope sets.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_positions,
                    id_col="account_id",
                    strategy="grid",
                    date_col="position_date",
                    grid_col="obs_month",
                    grain="month",
                ),
                inputs={
                    "raw": "raw_positions",
                    "scope_ids": "account_scope_ids",
                    "grid": "account_grid",
                },
                outputs="positions_staged",
                name="stage_positions",
            ),
            # CUSTOMER-grain, id_only: small dimension, no date reduction.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_customer_dim,
                    id_col="customer_id",
                    strategy="id_only",
                ),
                inputs={"raw": "raw_customer_dim", "scope_ids": "customer_scope_ids"},
                outputs="customer_dim_staged",
                name="stage_customer_dim",
            ),
        ],
        tags="staging",
    )
