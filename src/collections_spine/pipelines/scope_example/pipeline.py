"""Example STAGING pipeline for scope filtering.

Each raw table has its own small staging function that COMPOSES the scope filters
it needs (``filter_ids`` / ``filter_windows`` / ``filter_pairs``) and then runs the
real staging logic. Per-table facts -- column names, which filters apply, coarse
prune -- live in that function, where they are local and readable. There is no
strategy enum, no factory, no wrapper.

Column-name differences between a raw table and a scope set are handled by the
filters' ``scope_*_col`` arguments (internal alias on the small side) -- never by
materialising a renamed copy of a scope dataset.

Multiple id types: each id TYPE (customer, account, ...) has its own scope sets,
produced upstream. A staging node simply names the ones matching its table's
grain in its Kedro inputs.

SCD2 / interval tables do NOT use these filters -- they need the interval ->
point-in-time collapse to one active row per (id, observation_date), which is
``stage_scd2_table`` (see the last node).

Register in ``pipeline_registry.py``::

    from src.collections_spine.pipelines.scope_example import create_staging_pipeline

    def register_pipelines():
        staging = create_staging_pipeline()
        return {"staging": staging, "__default__": staging}
"""

from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from src.collections_spine import Scd2Schema, stage_scd2_table
from src.collections_spine.scope import filter_ids, filter_pairs, filter_windows

# SCD2 column contract for the example interval table (override per table).
_CONTRACT_SCD2 = Scd2Schema(key="customer_id")


# --------------------------------------------------------------------------- #
# per-table staging functions -- compose the filters this table needs
# --------------------------------------------------------------------------- #
def stage_txns(raw: DataFrame, scope_ids: DataFrame, windows: DataFrame) -> DataFrame:
    """Customer-grain transactions: id prune -> window filter -> staging logic.

    The raw table calls the id ``contract_idt`` while the customer scope sets use
    ``customer_id`` -- mapped via ``scope_id_col``, no renamed dataset copies.
    """
    # coarse prune on the load partition: plain where, bounds from the modelling
    # window extent (move to params in real use).
    df = raw.where(F.col("load_date").between("2019-01-01", "2026-07-31"))
    df = filter_ids(df, scope_ids, id_col="contract_idt", scope_id_col="customer_id")
    df = filter_windows(
        df, windows,
        id_col="contract_idt", date_col="txn_date", scope_id_col="customer_id",
    )
    # TODO(you): real staging logic
    return df


def stage_positions(raw: DataFrame, scope_ids: DataFrame, pairs: DataFrame) -> DataFrame:
    """Account-grain positions: month-partitioned, so exact (id, date) pairs."""
    df = filter_ids(raw, scope_ids, id_col="account_id")
    df = filter_pairs(
        df, pairs,
        id_col="account_id", date_col="position_date", scope_date_col="obs_date",
    )
    # TODO(you): real staging logic
    return df


def stage_customer_dim(raw: DataFrame, scope_ids: DataFrame) -> DataFrame:
    """Customer dimension: small table, id prune only."""
    df = filter_ids(raw, scope_ids, id_col="customer_id")
    # TODO(you): real staging logic
    return df


def create_staging_pipeline(**kwargs) -> Pipeline:
    return pipeline(
        [
            node(
                func=stage_txns,
                inputs={
                    "raw": "raw_txns",
                    "scope_ids": "customer_scope_ids",
                    "windows": "customer_windows",
                },
                outputs="txns_staged",
                name="stage_txns",
            ),
            node(
                func=stage_positions,
                inputs={
                    "raw": "raw_positions",
                    "scope_ids": "account_scope_ids",
                    "pairs": "account_pairs",
                },
                outputs="positions_staged",
                name="stage_positions",
            ),
            node(
                func=stage_customer_dim,
                inputs={"raw": "raw_customer_dim", "scope_ids": "customer_scope_ids"},
                outputs="customer_dim_staged",
                name="stage_customer_dim",
            ),
            # SCD2 interval table: reduce AND collapse to one active row per
            # (customer_id, observation_date). Takes the pre-built scope_ids as
            # `accounts` (no per-node distinct) and the (id, observation_date)
            # pairs as `spine`.
            node(
                func=partial(
                    stage_scd2_table,
                    schema=_CONTRACT_SCD2,
                    broadcast_accounts=True,
                ),
                inputs={
                    "raw_df": "raw_customer_scd2",
                    "spine": "customer_pairs",
                    "accounts": "customer_scope_ids",
                },
                outputs="customer_scd2_staged",
                name="stage_customer_scd2",
            ),
        ],
        tags="staging",
    )
