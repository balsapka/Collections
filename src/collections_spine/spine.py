"""Point-in-time master-table staging for big retail-credit tables (PySpark).

The team maintains a ``(account_id, observation_date)`` *spine* and needs every
source table reduced to exactly those pairs before any feature logic runs, so
Kedro nodes never transform the full universe (billions of rows per table).

Two table archetypes are supported:

* **Daily grain** ``(account_id, snapshot_date, ...)`` -- matched to the spine
  either by exact ``snapshot_date == observation_date`` or as-of (latest
  snapshot on/before the observation date).
* **SCD2 / effective-dated** ``(account_id, effective_start_date,
  effective_end_date, date_modified, ...)`` -- the active record at an
  observation date is the one whose half-open interval ``[start, end)`` contains
  it. Selection is always point-in-time-correct: ``date_modified`` corrections
  booked after the observation date are ignored, and the latest remaining version
  wins (no future-restatement leakage).

All SCD2 tables in this estate share the same date columns and use a sentinel
``effective_end_date`` of ``2100-01-01`` for still-open records, so those
semantics are baked into :class:`Scd2Schema`'s defaults.

The reduction pipeline (cheap step feeds the next):

    0. account semi-join     -> drop accounts outside the modeling population
    1. date-overlap prune    -> enables partition pruning on date-partitioned tables
    2. grid join to distinct  -> broadcast the tiny set of observation dates,
       observation dates          turning an interval/theta join into a bounded explode
    3. restatement dedup     -> one row per (account_id, observation_date)
    4. equi-join to spine    -> exact pairs only

See ``README.md`` in this package for the Kedro catalog/pipeline wiring.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Optional, Union

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

#: Effective_end_date value used for still-open SCD2 records across the estate.
OPEN_END_SENTINEL = "2100-01-01"

DateLike = Union[str, Column]


@dataclass(frozen=True)
class Scd2Schema:
    """Column names + interval semantics for an effective-dated (SCD2) table.

    Defaults match the shared schema used by every SCD2 table in this estate;
    override only ``key`` (or ``tiebreak``) if a particular table differs.

    Attributes:
        key: Business/entity key, deduped to one active row per value.
        eff_start: Interval start column (inclusive lower bound).
        eff_end: Interval end column. With ``end_inclusive=False`` (default) the
            interval is half-open ``[start, end)``.
        modified: Restatement / knowledge timestamp. The latest value wins when
            several versions are valid at the same observation date.
        end_inclusive: Treat ``eff_end`` as the last valid day (``<=``) rather
            than the next record's start (``<``). Default ``False``.
        open_end_sentinel: Value of ``eff_end`` for still-open records. Compares
            correctly as a normal future date; kept here for clarity and helpers.
        null_end_is_open: Also treat a NULL ``eff_end`` as still-open (defensive;
            the estate uses the sentinel, but upstream loads occasionally null it).
        tiebreak: Extra columns (desc) appended to the dedup ordering for fully
            deterministic selection when ``modified`` ties.
    """

    key: str = "account_id"
    eff_start: str = "effective_start_date"
    eff_end: str = "effective_end_date"
    modified: str = "date_modified"
    end_inclusive: bool = False
    open_end_sentinel: str = OPEN_END_SENTINEL
    null_end_is_open: bool = True
    tiebreak: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------- #
# Internal column helpers
# --------------------------------------------------------------------------- #
def _as_date(value: DateLike) -> Column:
    """Coerce a ``'yyyy-MM-dd'`` string (or pass through a Column) to a date."""
    return value if isinstance(value, Column) else F.to_date(F.lit(value))


def _end_after(end: Column, point: Column, s: Scd2Schema) -> Column:
    """Upper-bound validity: ``end`` is after ``point`` (interval still active)."""
    cond = (end >= point) if s.end_inclusive else (end > point)
    if s.null_end_is_open:
        cond = cond | end.isNull()
    return cond


def _dedup_order(s: Scd2Schema) -> list[Column]:
    """Deterministic ordering: latest restatement, then latest start, then ties."""
    return [
        F.col(s.modified).desc_nulls_last(),
        F.col(s.eff_start).desc(),
        *[F.col(c).desc() for c in s.tiebreak],
    ]


# --------------------------------------------------------------------------- #
# Task 1 -- active-record selection at a single observation date
# --------------------------------------------------------------------------- #
def active_as_of(
    df: DataFrame,
    observation_date: DateLike,
    schema: Scd2Schema = Scd2Schema(),
) -> DataFrame:
    """Return exactly one active row per key, valid at ``observation_date``.

    Point-in-time-correct and leakage-free by construction:

    Validity (default half-open):  ``eff_start <= obs < eff_end``.
    Knowledge cutoff (always on):  ``date_modified <= obs`` -- corrections booked
                                   after the observation date are never seen.
    Restatement:                   among the remaining rows per key, keep the
                                   latest ``date_modified``.

    Args:
        df: A single SCD2 source table.
        observation_date: ``'yyyy-MM-dd'`` string, or a Column.
        schema: Column/interval contract; estate defaults usually suffice.

    Returns:
        One row per ``schema.key`` (keys with no covering interval are absent).
    """
    obs = _as_date(observation_date)
    start, end = F.col(schema.eff_start), F.col(schema.eff_end)

    # Valid at obs AND only corrections known by then (no future leakage).
    candidates = df.where(
        (start <= obs) & _end_after(end, obs, schema) & (F.col(schema.modified) <= obs)
    )

    w = Window.partitionBy(schema.key).orderBy(*_dedup_order(schema))
    return (
        candidates.withColumn("_rn", F.row_number().over(w))
        .where(F.col("_rn") == 1)
        .drop("_rn")
    )


# --------------------------------------------------------------------------- #
# Task 2 -- pre-filter big tables against the spine
# --------------------------------------------------------------------------- #
def prefilter_scd2(
    df: DataFrame,
    spine: DataFrame,
    schema: Scd2Schema = Scd2Schema(),
    obs_col: str = "observation_date",
    broadcast_dates: bool = True,
    broadcast_accounts: bool = False,
) -> DataFrame:
    """Reduce a billion-row SCD2 table to one active row per spine pair.

    Selection is always point-in-time-correct: corrections booked after the
    observation date (``date_modified > observation_date``) are never used, so
    staged rows are leakage-free.

    Args:
        df: SCD2 source table.
        spine: ``(account_id, observation_date)`` DataFrame (column names per
            ``schema.key`` and ``obs_col``).
        schema: Column/interval contract.
        obs_col: Observation-date column name in ``spine``.
        broadcast_dates: Broadcast the tiny distinct-observation-date set (the
            key to turning the interval join into a bounded explode). Leave on.
        broadcast_accounts: Broadcast the distinct-account set in the step-0
            semi-join. Enable only if that set fits comfortably in memory;
            otherwise rely on bucketing / dynamic partition pruning.

    Returns:
        One row per ``(account_id, observation_date)`` present in the spine and
        covered by an interval, carrying the full SCD2 payload.
    """
    start, end = F.col(schema.eff_start), F.col(schema.eff_end)

    # 0. account semi-join: drop everything outside the modeling population.
    accounts = spine.select(schema.key).distinct()
    df = df.join(F.broadcast(accounts) if broadcast_accounts else accounts, schema.key, "leftsemi")

    # 1. date-overlap prune (interval must touch [lo, hi]) -> partition pruning.
    lo, hi = spine.agg(F.min(obs_col).alias("lo"), F.max(obs_col).alias("hi")).first()
    df = df.where((start <= F.lit(hi)) & _end_after(end, F.lit(lo), schema))

    # 2. grid join to the tiny distinct-date set: each row fans out only to the
    #    observation dates its interval actually covers (broadcast theta join).
    obs_dates = spine.select(obs_col).distinct()
    od = F.broadcast(obs_dates) if broadcast_dates else obs_dates
    obs = F.col(obs_col)
    paired = df.join(od, (start <= obs) & _end_after(end, obs, schema), "inner")
    # Always drop corrections booked after the observation date (no leakage).
    paired = paired.where(F.col(schema.modified) <= obs)

    # 3. restatement dedup -> one row per (key, observation_date).
    w = Window.partitionBy(schema.key, obs_col).orderBy(*_dedup_order(schema))
    point_in_time = (
        paired.withColumn("_rn", F.row_number().over(w))
        .where(F.col("_rn") == 1)
        .drop("_rn")
    )

    # 4. equi-join to the spine -> exact pairs only.
    return point_in_time.join(spine, [schema.key, obs_col], "inner")


def prefilter_daily(
    df: DataFrame,
    spine: DataFrame,
    key: str = "account_id",
    snapshot_col: str = "snapshot_date",
    obs_col: str = "observation_date",
    asof: bool = False,
    lookback_days: Optional[int] = None,
) -> DataFrame:
    """Reduce a daily-grain table to the spine.

    Args:
        df: Daily-grain source table.
        spine: ``(account_id, observation_date)`` DataFrame.
        key: Entity key, present in both ``df`` and ``spine``.
        snapshot_col: Daily snapshot-date column in ``df``.
        obs_col: Observation-date column in ``spine``.
        asof: If ``False`` (default), match exactly
            ``snapshot_date == observation_date``. If ``True``, pick the latest
            snapshot on/before each observation date.
        lookback_days: Bounds the as-of search window (snapshots within
            ``[obs - lookback_days, obs]``). Strongly recommended when
            ``asof=True`` to keep the range join cheap; ignored when ``asof`` is
            ``False``.

    Returns:
        One row per matched ``(account_id, observation_date)`` with the snapshot
        payload and an ``observation_date`` column.
    """
    lo, hi = spine.agg(F.min(obs_col).alias("lo"), F.max(obs_col).alias("hi")).first()
    floor = F.date_sub(F.lit(lo), lookback_days) if (asof and lookback_days) else F.lit(lo)
    df = df.where(F.col(snapshot_col).between(floor, F.lit(hi)))  # partition pruning

    sp = spine.select(F.col(key).alias("_k"), F.col(obs_col).alias("_obs"))

    if not asof:  # exact snapshot == observation
        cond = (df[key] == sp["_k"]) & (df[snapshot_col] == sp["_obs"])
        return df.join(sp, cond, "inner").drop("_k").withColumnRenamed("_obs", obs_col)

    # as-of: latest snapshot on/before the observation date
    cond = (df[key] == sp["_k"]) & (df[snapshot_col] <= sp["_obs"])
    if lookback_days:
        cond = cond & (df[snapshot_col] >= F.date_sub(sp["_obs"], lookback_days))
    w = Window.partitionBy("_k", "_obs").orderBy(F.col(snapshot_col).desc())
    return (
        df.join(sp, cond, "inner")
        .withColumn("_rn", F.row_number().over(w))
        .where(F.col("_rn") == 1)
        .drop("_rn", "_k")
        .withColumnRenamed("_obs", obs_col)
    )


# --------------------------------------------------------------------------- #
# Kedro node wrappers
# --------------------------------------------------------------------------- #
def build_spine(
    accounts: DataFrame,
    observation_dates: Union[Iterable[str], DataFrame],
    key: str = "account_id",
    obs_col: str = "observation_date",
) -> DataFrame:
    """Build the ``(account_id, observation_date)`` spine.

    Args:
        accounts: DataFrame containing the modeling population's ``key`` column
            (deduped internally).
        observation_dates: Either a list of ``'yyyy-MM-dd'`` strings (e.g.
            month-ends from params) or a DataFrame with an ``obs_col`` column.
        key: Account key column name.
        obs_col: Observation-date column name to emit.

    Returns:
        The cross product of distinct accounts and observation dates.
    """
    if isinstance(observation_dates, DataFrame):
        dates = observation_dates.select(F.to_date(F.col(obs_col)).alias(obs_col)).distinct()
    else:
        spark = accounts.sparkSession
        rows = [(d,) for d in observation_dates]
        dates = spark.createDataFrame(rows, [obs_col]).select(
            F.to_date(F.col(obs_col)).alias(obs_col)
        )

    return accounts.select(key).distinct().crossJoin(F.broadcast(dates))


def stage_scd2_table(
    raw_df: DataFrame,
    spine: DataFrame,
    schema: Optional[Scd2Schema] = None,
    obs_col: str = "observation_date",
    broadcast_accounts: bool = False,
) -> DataFrame:
    """Kedro node: stage one SCD2 source table against the spine.

    Repartitions by ``observation_date`` so the persisted staging output is laid
    out for cheap, partition-pruned reads by downstream feature nodes.
    """
    schema = schema or Scd2Schema()
    out = prefilter_scd2(
        raw_df,
        spine,
        schema=schema,
        obs_col=obs_col,
        broadcast_accounts=broadcast_accounts,
    )
    return out.repartition(F.col(obs_col))


def stage_daily_table(
    raw_df: DataFrame,
    spine: DataFrame,
    key: str = "account_id",
    snapshot_col: str = "snapshot_date",
    obs_col: str = "observation_date",
    asof: bool = False,
    lookback_days: Optional[int] = None,
) -> DataFrame:
    """Kedro node: stage one daily-grain source table against the spine.

    Repartitions by ``observation_date`` to match the SCD2 staging layout, so all
    staged tables join cheaply on ``(account_id, observation_date)`` downstream.
    """
    out = prefilter_daily(
        raw_df,
        spine,
        key=key,
        snapshot_col=snapshot_col,
        obs_col=obs_col,
        asof=asof,
        lookback_days=lookback_days,
    )
    return out.repartition(F.col(obs_col))
