"""Config-driven scope filtering for wide raw tables (PySpark).

The problem this solves
-----------------------
A modelling *spine* of ``(entity_id, anchor_date)`` pairs defines the population.
Every raw table must be reduced to just the rows in scope before feature logic
runs. Two facts vary *per raw table*, so they are configuration, not code:

* the id / date column names,
* the reduction *strategy* -- ``id_only`` / ``range`` / ``grid``.

The one rule that makes this cheap
----------------------------------
The distinct id set (and the window / grid sets) are computed ONCE in the spine
layer and persisted. ``apply_scope`` never calls ``.distinct()`` -- it only
*joins* pre-built sets. Recomputing ``spine.select(id).distinct()`` inside every
staging node would shuffle the same set N times; that is the mistake this module
is shaped to avoid.

Strategies
----------
* ``id_only`` -- keep raw rows whose id is in scope. Broadcast ``leftsemi`` on the
  distinct id set. For small dimensions / tables with no date reduction.
* ``range``   -- keep raw rows whose date falls in ANY anchor's window
  ``[anchor - lookback, anchor + lookahead]``. Broadcast ``leftsemi`` against the
  per-anchor ``(id, win_start, win_end)`` set. Window variation lives in two
  columns, so nothing is materialised at row grain. Works regardless of how the
  raw table is physically partitioned.
* ``grid``    -- keep raw rows whose ``(id, month)`` is in the exploded
  ``(id, obs_grain)`` set. A pure equi ``leftsemi``. Prefer this ONLY when the raw
  table is physically partitioned on that grain (it enables dynamic partition
  pruning); otherwise ``range`` is cheaper.

The precise match is always a ``leftsemi`` so a raw row covered by several anchors
survives exactly once (no fan-out, no dedup). Scope is reduction only; grain /
as-of logic belongs in the downstream transform.
"""

from __future__ import annotations

import operator
from functools import reduce
from typing import Callable, Optional, Sequence, Union

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

Keys = Union[str, Sequence[str]]


def _as_list(cols: Keys) -> list[str]:
    return [cols] if isinstance(cols, str) else list(cols)


# --------------------------------------------------------------------------- #
# Spine-layer builders -- each runs ONCE, output persisted, reused everywhere.
# --------------------------------------------------------------------------- #
def build_scope_ids(spine: DataFrame, id_cols: Keys) -> DataFrame:
    """Distinct in-scope id key(s). The single ``distinct()`` for the id-prune."""
    return spine.select(*_as_list(id_cols)).distinct()


def add_window_bounds(
    spine: DataFrame,
    id_cols: Keys,
    anchor_col: str,
    lookback_months: int,
    lookahead_months: int,
) -> DataFrame:
    """Per-anchor ``(id.., win_start, win_end)`` for the ``range`` strategy."""
    keys = _as_list(id_cols)
    a = F.col(anchor_col)
    return (
        spine.select(*keys, anchor_col)
        .withColumn("win_start", F.add_months(a, -lookback_months))
        .withColumn("win_end", F.add_months(a, lookahead_months))
        .select(*keys, "win_start", "win_end")
        .distinct()
    )


def build_grid(
    spine: DataFrame,
    id_cols: Keys,
    anchor_col: str,
    lookback_months: int,
    lookahead_months: int,
    grain: str = "month",
) -> DataFrame:
    """Exploded ``(id.., obs_grain)`` for the ``grid`` strategy (monthly explode).

    Each anchor fans out to the month-starts its window covers; ``distinct`` then
    collapses overlapping windows across an id's anchors. Daily grids should come
    from *enumeration* (a spine that already lists exact ``(id, date)`` pairs), not
    from exploding a window -- a daily explode of a 60-month window is huge.
    """
    keys = _as_list(id_cols)
    a = F.col(anchor_col)
    bounded = (
        spine.select(*keys, anchor_col)
        .withColumn("win_start", F.add_months(a, -lookback_months))
        .withColumn("win_end", F.add_months(a, lookahead_months))
    )
    months = F.expr("sequence(win_start, win_end, interval 1 month)")
    return (
        bounded.withColumn("_d", F.explode(months))
        .select(*keys, F.trunc("_d", grain).alias("obs_grain"))
        .distinct()
    )


# --------------------------------------------------------------------------- #
# Staging-layer application -- joins only, never distinct.
# --------------------------------------------------------------------------- #
def apply_scope(
    df: DataFrame,
    *,
    on: Keys,
    strategy: str,
    scope_ids: Optional[DataFrame] = None,
    windows: Optional[DataFrame] = None,
    grid: Optional[DataFrame] = None,
    date_col: Optional[str] = None,
    grain: str = "month",
    prune_col: Optional[str] = None,
    prune_bounds: Optional[tuple[str, str]] = None,
    broadcast_ids: bool = True,
    broadcast_scope: bool = False,
) -> DataFrame:
    """Reduce ``df`` to the modelling scope. Pre-built sets in, joined never distinct.

    Args:
        on: Entity key column(s). NOT the date column.
        strategy: ``id_only`` | ``range`` | ``grid``.
        scope_ids: Distinct id set for the cheap broadcast id-prune (and the whole
            reduction for ``id_only``). From :func:`build_scope_ids`.
        windows: ``(id.., win_start, win_end)`` for ``range``. From
            :func:`add_window_bounds`.
        grid: ``(id.., obs_grain)`` for ``grid``. From :func:`build_grid` (or an
            enumerated spine).
        date_col: Raw observation-date column (``range`` / ``grid``).
        grain: Truncation grain matching the ``grid`` set (``grid`` only).
        prune_col: Partition/clustered column for a coarse file prune. Often NOT
            ``date_col`` (e.g. an ``edp_load_date`` load partition). Harmless row
            filter when it prunes nothing (single-partition history table).
        prune_bounds: ``(lo, hi)`` literal extent for ``prune_col`` -- the global
            window extent, computed once by the caller (no agg here).
        broadcast_ids: Force-broadcast the distinct ``scope_ids`` set (one row per
            id -- reliably small). Set ``False`` if the id universe itself is too
            large to broadcast.
        broadcast_scope: Force-broadcast ``windows`` / ``grid``. Default ``False``:
            these are one row per (id, anchor) / (id, month) and can be MILLIONS of
            rows -- forcing a broadcast collects them to the driver and OOMs. Left
            off, the range join runs as a sort-merge join on the equi ``id`` key
            with the ``BETWEEN`` as a residual filter (not a cartesian), and the
            grid join as a normal equi join; Spark still auto-broadcasts either side
            if it is genuinely under ``autoBroadcastJoinThreshold``. Set ``True``
            only when you know the set is small (e.g. a single-anchor population).

    Returns:
        Raw rows in scope, each at most once (``leftsemi`` precise match).
    """
    keys = _as_list(on)
    _ident = lambda x: x  # noqa: E731
    bc_ids = F.broadcast if broadcast_ids else _ident
    bc_scope = F.broadcast if broadcast_scope else _ident

    # coarse partition/file prune -- enables pruning where the layout allows it,
    # a harmless row filter otherwise. Bounds are literal: no action triggered.
    if prune_col and prune_bounds:
        lo, hi = prune_bounds
        df = df.where(F.col(prune_col).between(F.lit(lo), F.lit(hi)))

    # cheap broadcast id-prune: shrink the scan before the precise match.
    if scope_ids is not None:
        df = df.join(bc_ids(scope_ids), keys, "leftsemi")

    if strategy == "id_only":
        return df

    if strategy == "range":
        if date_col is None or windows is None:
            raise ValueError("range strategy requires date_col and windows")
        d, w = df.alias("d"), windows.alias("w")
        cond = reduce(operator.and_, (F.col(f"d.{k}") == F.col(f"w.{k}") for k in keys))
        cond = cond & F.col(f"d.{date_col}").between(F.col("w.win_start"), F.col("w.win_end"))
        # Equi key `id` present -> sort-merge join with the BETWEEN as a residual
        # filter (NOT a cartesian). leftsemi -> each raw row survives once even if
        # several windows cover it. windows unhinted by default (can be millions).
        return d.join(bc_scope(w), cond, "leftsemi")

    if strategy == "grid":
        if date_col is None or grid is None:
            raise ValueError("grid strategy requires date_col and grid")
        obs = F.trunc(F.col(date_col), grain) if grain else F.col(date_col)
        d = df.withColumn("_obs_grain", obs)
        g = grid.withColumnRenamed("obs_grain", "_obs_grain")
        return d.join(bc_scope(g), keys + ["_obs_grain"], "leftsemi").drop("_obs_grain")

    raise ValueError(f"unknown strategy: {strategy!r}")


def scoped_stage(
    raw: DataFrame,
    scope_ids: Optional[DataFrame] = None,
    windows: Optional[DataFrame] = None,
    grid: Optional[DataFrame] = None,
    *,
    transform: Callable[[DataFrame], DataFrame],
    on: Keys,
    strategy: str,
    date_col: Optional[str] = None,
    grain: str = "month",
    prune_col: Optional[str] = None,
    prune_bounds: Optional[tuple[str, str]] = None,
    broadcast_ids: bool = True,
    broadcast_scope: bool = False,
) -> DataFrame:
    """One staging node: apply the chosen scope, then run the pure ``transform``.

    Bind the config (``transform``, ``on``, ``strategy``, ...) with
    ``functools.partial`` in the pipeline; the DataFrame inputs (``raw`` +
    whichever scope sets the strategy needs) stay as node inputs. ``transform`` is
    a plain ``DataFrame -> DataFrame`` reused as-is by the spine layer on
    unscoped slim raw. ``broadcast_scope`` defaults off -- see :func:`apply_scope`.
    """
    scoped = apply_scope(
        raw,
        on=on,
        strategy=strategy,
        scope_ids=scope_ids,
        windows=windows,
        grid=grid,
        date_col=date_col,
        grain=grain,
        prune_col=prune_col,
        prune_bounds=prune_bounds,
        broadcast_ids=broadcast_ids,
        broadcast_scope=broadcast_scope,
    )
    return transform(scoped)
