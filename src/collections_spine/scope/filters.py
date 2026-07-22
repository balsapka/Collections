"""Config-driven scope filtering for wide raw tables (PySpark) -- staging side.

A modelling *spine* of ``(id, anchor_date)`` pairs defines the population. Every
raw table must be reduced to just the rows in scope before feature logic runs.
Two facts vary *per raw table*, so they are configuration, not code:

* the id / date column names,
* the reduction *strategy* -- ``id_only`` / ``range`` / ``grid``.

Scope sets are inputs, not built here
-------------------------------------
``scope_ids`` (distinct ids), ``windows`` (``id, win_start, win_end``) and
``grid`` (``id, <grain>``) are produced UPSTREAM -- by the spine layer or your own
builders -- persisted, and passed to these nodes as catalog inputs. This module
only *applies* them; it never calls ``.distinct()`` (recomputing it per staging
node would shuffle the same set N times).

There is no single global scope: there are many scope sets, one per id TYPE
(customer, account, ...). ``id_col`` and the scope DataFrames are per-node
arguments, so different staging nodes reduce against different scopes -- e.g. a
customer-grain table against ``customer_scope_ids`` / ``customer_windows`` and an
account-grain table against ``account_scope_ids`` / ``account_grid``.

Strategies
----------
* ``id_only`` -- keep raw rows whose id is in scope. ``leftsemi`` on ``scope_ids``.
  For small dimensions / tables with no date reduction.
* ``range``   -- keep raw rows whose date falls in ANY anchor's window
  ``[anchor - lookback, anchor + lookahead]``. ``leftsemi`` against ``windows``.
  Window variation lives in two columns, nothing materialised at row grain. Works
  regardless of how the raw table is physically partitioned.
* ``grid``    -- keep raw rows whose ``(id, grain)`` is in ``grid``. A pure equi
  ``leftsemi``. Prefer this ONLY when the raw table is physically partitioned on
  that grain (it enables dynamic partition pruning); otherwise ``range`` is cheaper.

The precise match is always a ``leftsemi`` so a raw row covered by several anchors
survives exactly once (no fan-out, no dedup). Scope is reduction only; grain /
as-of logic belongs in the downstream transform.

Join strategy / broadcasting
----------------------------
Only ``scope_ids`` (one row per id) is force-broadcast, for the cheap id-prune.
``windows`` / ``grid`` are one row per (id, anchor) / (id, grain) and can be
millions of rows, so they are NOT force-broadcast (that would collect them to the
driver and OOM). The ``range`` join carries an equi key (``id``), so Spark runs it
as a sort-merge join with the ``BETWEEN`` as a residual filter -- never a
cartesian -- and still auto-broadcasts a genuinely small side on its own. See
``broadcast_ids`` / ``broadcast_scope``.
"""

from __future__ import annotations

from typing import Callable, Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def apply_scope(
    df: DataFrame,
    *,
    id_col: str,
    strategy: str,
    scope_ids: Optional[DataFrame] = None,
    windows: Optional[DataFrame] = None,
    grid: Optional[DataFrame] = None,
    date_col: Optional[str] = None,
    grid_col: str = "obs_month",
    grain: Optional[str] = "month",
    prune_col: Optional[str] = None,
    prune_bounds: Optional[tuple[str, str]] = None,
    broadcast_ids: bool = True,
    broadcast_scope: bool = False,
) -> DataFrame:
    """Reduce ``df`` to the modelling scope. Pre-built sets in, joined never distinct.

    Args:
        id_col: Entity key column (present in ``df`` and every scope set).
        strategy: ``id_only`` | ``range`` | ``grid``.
        scope_ids: Distinct id set for the cheap broadcast id-prune (and the whole
            reduction for ``id_only``).
        windows: ``(id, win_start, win_end)`` for ``range``.
        grid: ``(id, <grid_col>)`` for ``grid``.
        date_col: Raw observation-date column (``range`` / ``grid``).
        grid_col: Name of the grain column in ``grid`` (``grid`` only).
        grain: Truncation applied to ``date_col`` to match ``grid_col``
            (``"month"``, ``"week"``, ...). ``None`` = exact match, e.g. a daily
            enumerated grid (``grid`` only).
        prune_col: Partition/clustered column for a coarse file prune. Often NOT
            ``date_col`` (e.g. an ``edp_load_date`` load partition). Harmless row
            filter when it prunes nothing (single-partition history table).
        prune_bounds: ``(lo, hi)`` literal extent for ``prune_col`` -- the global
            window extent, computed once by the caller (no agg here).
        broadcast_ids: Force-broadcast ``scope_ids`` (reliably small). Set ``False``
            only if the id universe itself is too large to broadcast.
        broadcast_scope: Force-broadcast ``windows`` / ``grid``. Default ``False``:
            these can be MILLIONS of rows and a forced broadcast OOMs the driver.
            Left off, ``range`` is a sort-merge join (equi ``id`` + ``BETWEEN``
            residual) and ``grid`` a normal equi join; Spark still auto-broadcasts a
            side under ``autoBroadcastJoinThreshold``. Set ``True`` only for a known
            small set (e.g. a single-anchor population).

    Returns:
        Raw rows in scope, each at most once (``leftsemi`` precise match).
    """
    ident = lambda x: x  # noqa: E731
    bc_ids = F.broadcast if broadcast_ids else ident
    bc_scope = F.broadcast if broadcast_scope else ident

    # coarse partition/file prune -- prunes where the layout allows, a harmless row
    # filter otherwise. Bounds are literal: no action triggered.
    if prune_col and prune_bounds:
        lo, hi = prune_bounds
        df = df.where(F.col(prune_col).between(F.lit(lo), F.lit(hi)))

    # cheap broadcast id-prune: shrink the scan before the precise match.
    if scope_ids is not None:
        df = df.join(bc_ids(scope_ids), id_col, "leftsemi")

    if strategy == "id_only":
        return df

    if strategy == "range":
        if date_col is None or windows is None:
            raise ValueError("range strategy requires date_col and windows")
        d, w = df.alias("d"), windows.alias("w")
        cond = (F.col(f"d.{id_col}") == F.col(f"w.{id_col}")) & F.col(
            f"d.{date_col}"
        ).between(F.col("w.win_start"), F.col("w.win_end"))
        # equi key `id` -> sort-merge join, BETWEEN as residual (never cartesian);
        # leftsemi -> each raw row survives once even if several windows cover it.
        return d.join(bc_scope(w), cond, "leftsemi")

    if strategy == "grid":
        if date_col is None or grid is None:
            raise ValueError("grid strategy requires date_col and grid")
        d, g = df.alias("d"), grid.alias("g")
        obs = F.trunc(F.col(f"d.{date_col}"), grain) if grain else F.col(f"d.{date_col}")
        cond = (F.col(f"d.{id_col}") == F.col(f"g.{id_col}")) & (obs == F.col(f"g.{grid_col}"))
        return d.join(bc_scope(g), cond, "leftsemi")

    raise ValueError(f"unknown strategy: {strategy!r}")


def scoped_stage(
    raw: DataFrame,
    scope_ids: Optional[DataFrame] = None,
    windows: Optional[DataFrame] = None,
    grid: Optional[DataFrame] = None,
    *,
    transform: Callable[[DataFrame], DataFrame],
    id_col: str,
    strategy: str,
    date_col: Optional[str] = None,
    grid_col: str = "obs_month",
    grain: Optional[str] = "month",
    prune_col: Optional[str] = None,
    prune_bounds: Optional[tuple[str, str]] = None,
    broadcast_ids: bool = True,
    broadcast_scope: bool = False,
) -> DataFrame:
    """One staging node: apply the chosen scope, then run the pure ``transform``.

    Bind the config (``transform``, ``id_col``, ``strategy``, ...) with
    ``functools.partial`` in the pipeline; the DataFrame inputs (``raw`` +
    whichever scope sets the strategy needs) stay as node inputs. ``transform`` is a
    plain ``DataFrame -> DataFrame`` reused as-is by the spine layer on unscoped
    slim raw. ``broadcast_scope`` defaults off -- see :func:`apply_scope`.
    """
    scoped = apply_scope(
        raw,
        id_col=id_col,
        strategy=strategy,
        scope_ids=scope_ids,
        windows=windows,
        grid=grid,
        date_col=date_col,
        grid_col=grid_col,
        grain=grain,
        prune_col=prune_col,
        prune_bounds=prune_bounds,
        broadcast_ids=broadcast_ids,
        broadcast_scope=broadcast_scope,
    )
    return transform(scoped)
