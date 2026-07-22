"""Example wiring for config-driven scope filtering.

Two layers:

* ``create_scope_pipeline`` -- SPINE layer. Derives the scope sets from the
  modelling spine ONCE (the only ``distinct()`` / explode), persisted for reuse.
* ``create_staging_pipeline`` -- STAGING layer. Reduces each raw table with its
  OWN strategy via ``scoped_stage``, then runs a pure transform. Different tables
  use different scoping -- that per-node choice is the ``functools.partial`` config.

Downstream primary / intermediate / feature pipelines read staged outputs only,
so they carry no scope wiring at all.

Register in ``pipeline_registry.py``::

    from src.collections_spine.pipelines.scope_example import (
        create_scope_pipeline, create_staging_pipeline,
    )

    def register_pipelines():
        scope, staging = create_scope_pipeline(), create_staging_pipeline()
        return {"scope": scope, "staging": staging,
                "__default__": scope + staging}
"""

from functools import partial

from kedro.pipeline import Pipeline, node, pipeline

from src.collections_spine.scope import (
    add_window_bounds,
    build_grid,
    build_scope_ids,
    scoped_stage,
)

# --- example modelling config (move to conf/base/parameters.yml in real use) --
ID = "entity_id"
ANCHOR = "anchor_date"
LOOKBACK, LOOKAHEAD = 60, 1
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


# --------------------------------------------------------------------------- #
# SPINE layer -- build each scope set ONCE from the modelling spine.
# --------------------------------------------------------------------------- #
def create_scope_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=partial(build_scope_ids, id_cols=ID),
                inputs="modelling_spine",
                outputs="scope_ids",
                name="build_scope_ids",
            ),
            node(
                func=partial(
                    add_window_bounds,
                    id_cols=ID,
                    anchor_col=ANCHOR,
                    lookback_months=LOOKBACK,
                    lookahead_months=LOOKAHEAD,
                ),
                inputs="modelling_spine",
                outputs="scope_windows",
                name="build_scope_windows",
            ),
            node(
                func=partial(
                    build_grid,
                    id_cols=ID,
                    anchor_col=ANCHOR,
                    lookback_months=LOOKBACK,
                    lookahead_months=LOOKAHEAD,
                    grain="month",
                ),
                inputs="modelling_spine",
                outputs="scope_grid",
                name="build_scope_grid",
            ),
        ],
        tags="scope",
    )


# --------------------------------------------------------------------------- #
# STAGING layer -- each node picks its own scope. Same factory, per-node config.
# --------------------------------------------------------------------------- #
def create_staging_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            # range: date filter via per-anchor windows; coarse-prune the load col
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_txns,
                    on=ID,
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
            # grid: exact (id, month) equi-join -- this table IS month-partitioned
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_events,
                    on=ID,
                    strategy="grid",
                    date_col="event_date",
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
            # id_only: small dimension, no date reduction
            node(
                func=partial(
                    scoped_stage,
                    transform=stage_dim,
                    on=ID,
                    strategy="id_only",
                ),
                inputs={"raw": "raw_dim", "scope_ids": "scope_ids"},
                outputs="dim_staged",
                name="stage_dim",
            ),
        ],
        tags="staging",
    )
