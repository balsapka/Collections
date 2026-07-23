"""Scope filtering for wide raw tables (PySpark) -- staging side.

Three small, composable filters instead of one strategy-enum mega-function. Each
keeps the raw rows that match a pre-built scope set and takes ONLY the arguments
its join shape needs:

* :func:`filter_ids`     -- id in scope                 (leftsemi on the id set)
* :func:`filter_windows` -- id + date in an anchor window (leftsemi, equi id +
  ``BETWEEN`` residual)
* :func:`filter_pairs`   -- exact (id, date) pair in scope (leftsemi, equi on BOTH
  id and date -- always both, no grain truncation)

Compose them in a per-table staging function; per-table facts (column names,
which filters apply) live THERE, not in shared machinery::

    def stage_txns(raw, scope_ids, windows):
        df = filter_ids(raw, scope_ids, id_col="contract_idt",
                        scope_id_col="customer_id")
        df = filter_windows(df, windows, id_col="contract_idt",
                            date_col="txn_date", scope_id_col="customer_id")
        ...  # real staging logic
        return df

Column-name mapping, not dataset copies
---------------------------------------
Raw tables and scope sets rarely share column names. Every filter takes optional
``scope_*_col`` names and aliases the SMALL side internally -- an alias is a
projection in the Spark plan, so nothing is materialised. Never create a renamed
copy of a scope/spine dataset just to match a raw table.

Scope sets are inputs, not built here
-------------------------------------
Scope sets are produced upstream, persisted, and passed in as catalog inputs.
There are many of them -- one per id TYPE (customer, account, ...). These
functions never call ``.distinct()``: recomputing the id set per staging node
would shuffle the same result N times.

Broadcasting
------------
``filter_ids`` force-broadcasts by default (one row per id -- reliably small).
``filter_windows`` / ``filter_pairs`` do NOT: their sets are one row per
(id, anchor) / (id, date) and can be millions of rows; a forced broadcast
collects them to the driver and OOMs. Unhinted, the window join runs as a
sort-merge join on the equi id key with ``BETWEEN`` as a residual filter (never a
cartesian), and Spark still auto-broadcasts a side that is genuinely under
``autoBroadcastJoinThreshold``.

Every filter is a ``leftsemi``: a raw row covered by several anchors/windows
survives exactly once -- no fan-out, no dedup. Scope is reduction only; grain /
as-of / point-in-time logic (e.g. SCD2 collapse via ``stage_scd2_table``) belongs
downstream.
"""

from __future__ import annotations

from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def filter_ids(
    df: DataFrame,
    scope_ids: DataFrame,
    *,
    id_col: str,
    scope_id_col: Optional[str] = None,
    broadcast: bool = True,
) -> DataFrame:
    """Keep raw rows whose id is in ``scope_ids``.

    Args:
        df: Raw table.
        scope_ids: Pre-built distinct id set for this id type.
        id_col: Id column in ``df``.
        scope_id_col: Id column in ``scope_ids`` if named differently (aliased
            internally -- no copy).
        broadcast: Force-broadcast the id set. Default on; disable only if the id
            universe itself is too large to broadcast.
    """
    ids = scope_ids.select(F.col(scope_id_col or id_col).alias(id_col))
    return df.join(F.broadcast(ids) if broadcast else ids, id_col, "leftsemi")


def filter_windows(
    df: DataFrame,
    windows: DataFrame,
    *,
    id_col: str,
    date_col: str,
    scope_id_col: Optional[str] = None,
    start_col: str = "win_start",
    end_col: str = "win_end",
) -> DataFrame:
    """Keep raw rows whose date falls inside ANY of the id's anchor windows.

    ``windows`` is one row per (id, anchor): ``(id, start, end)``. The join has an
    equi id key plus a ``BETWEEN`` residual, so Spark runs a sort-merge join --
    never a cartesian -- and auto-broadcasts a genuinely small side on its own
    (no forced broadcast here: windows can be millions of rows).

    Args:
        df: Raw table.
        windows: Pre-built per-anchor window set for this id type.
        id_col: Id column in ``df``.
        date_col: Observation-date column in ``df``.
        scope_id_col: Id column in ``windows`` if named differently.
        start_col / end_col: Window bound columns in ``windows``.
    """
    w = windows.select(
        F.col(scope_id_col or id_col).alias("_w_id"),
        F.col(start_col).alias("_w_start"),
        F.col(end_col).alias("_w_end"),
    )
    cond = (df[id_col] == w["_w_id"]) & df[date_col].between(w["_w_start"], w["_w_end"])
    return df.join(w, cond, "leftsemi")


def filter_pairs(
    df: DataFrame,
    pairs: DataFrame,
    *,
    id_col: str,
    date_col: str,
    scope_id_col: Optional[str] = None,
    scope_date_col: Optional[str] = None,
) -> DataFrame:
    """Keep raw rows whose exact ``(id, date)`` pair is in ``pairs``.

    Always an equi ``leftsemi`` on BOTH id and date -- no grain truncation. The
    pair set's date grain must already match the raw table's (build it that way
    upstream). Use this over :func:`filter_windows` only when the raw table is
    physically partitioned on the date grain, where the equi key enables dynamic
    partition pruning.

    Args:
        df: Raw table.
        pairs: Pre-built ``(id, date)`` set (e.g. your ``data_scope_ids``).
        id_col: Id column in ``df``.
        date_col: Date column in ``df``.
        scope_id_col / scope_date_col: Column names in ``pairs`` if they differ
            (aliased internally -- no copy).
    """
    p = pairs.select(
        F.col(scope_id_col or id_col).alias(id_col),
        F.col(scope_date_col or date_col).alias(date_col),
    )
    return df.join(p, [id_col, date_col], "leftsemi")
