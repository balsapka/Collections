"""Example STAGING pipeline for config-driven scope filtering.

Each staging node reduces one raw table with its OWN strategy via ``scoped_stage``,
then runs a pure transform. Different tables use different scoping -- that per-node
choice is the ``functools.partial`` config, so nothing is duplicated.

The scope sets (``scope_ids`` / ``scope_windows`` / ``scope_grid``) are produced
UPSTREAM -- by the spine layer or your own builders -- and referenced here purely
as catalog inputs. Downstream primary / intermediate / feature pipelines read
staged outputs only, so they carry no scope wiring at all.

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
ID = "entity_id"
# global window extent for the coarse partition prune, computed once from the
# modelling window: [start - lookback, end + lookahead].
PRUNE_BOUNDS = ("2019-01-01", "2026-07-31")


# --------------------------------------------------------------------------- #
# pure transforms (DataFrame -> DataFrame). Reused unscoped by the spine layer.
# --------------------------------------------------------------------------- #
def stage_txns(df):
    # TODO(you): real staging logic
    return df


def stage_events(df):
    # TODO(you): real staging logic
    return df


def stage_dim(df):
    # TODO(you): real staging logic
    return df


def create_staging_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # range: date filter via per-anchor windows; coarse-prune the load col.
            # `windows` (entity_id, win_start, win_end) is built upstream.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_txns,
                    id_col=ID,
                    strategy="range",
                    date_col="txn_date",
                    prune_col="load_date",
                    prune_bounds=PRUNE_BOUNDS,
                ),
                inputs={
                    "raw": "raw_txns",
                    "scope_ids": "scope_ids",
                    "windows": "scope_windows",
                },
                outputs="txns_staged",
                name="stage_txns",
            ),
            # grid: exact (id, month) equi-join -- this table IS month-partitioned.
            # `scope_grid` (entity_id, obs_month) is YOUR own data_scope_ids output.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_events,
                    id_col=ID,
                    strategy="grid",
                    date_col="event_date",
                    grid_col="obs_month",
                    grain="month",
                ),
                inputs={
                    "raw": "raw_events",
                    "scope_ids": "scope_ids",
                    "grid": "scope_grid",
                },
                outputs="events_staged",
                name="stage_events",
            ),
            # id_only: small dimension, no date reduction.
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_dim,
                    id_col=ID,
                    strategy="id_only",
                ),
                inputs={"raw": "raw_dim", "scope_ids": "scope_ids"},
                outputs="dim_staged",
                name="stage_dim",
            ),
        ],
        tags="staging",
    )
