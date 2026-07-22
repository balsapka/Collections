"""Tests for collections_spine.scope.filters.

Focus on the ways scope filtering typically breaks: fan-out when a raw row falls
in several anchor windows (must survive exactly once), the three strategies, and
the coarse partition prune. `date_modified`-style dedup is out of scope here --
scope is pure reduction.

Run: pytest -q   (requires pyspark; tests skip cleanly if it is not installed)
"""

from __future__ import annotations

import datetime as dt

import pytest

pyspark = pytest.importorskip("pyspark")

from collections_spine.scope import (  # noqa: E402
    add_window_bounds,
    apply_scope,
    build_grid,
    build_scope_ids,
)

# `spark` fixture is provided by the repo-root conftest.py (session-scoped).


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def _spine(spark):
    # entity A has TWO anchors whose 1-month-back / 1-month-ahead windows overlap
    # around 2025-03; entity B one anchor; entity C is out of scope entirely.
    rows = [("A", "2025-03-01"), ("A", "2025-04-01"), ("B", "2025-01-01")]
    df = spark.createDataFrame(rows, ["entity_id", "anchor_date"])
    return df.withColumn("anchor_date", df["anchor_date"].cast("date"))


def _raw(spark):
    rows = [
        ("A", "2025-03-15", "load1"),  # in BOTH of A's windows (overlap) -> once
        ("A", "2025-06-01", "load1"),  # outside A's windows
        ("B", "2025-01-10", "load1"),  # in B's window
        ("C", "2025-01-10", "load1"),  # entity not in scope
    ]
    df = spark.createDataFrame(rows, ["entity_id", "event_date", "load_col"])
    return df.withColumn("event_date", df["event_date"].cast("date"))


# --------------------------------------------------------------------------- #
# range strategy
# --------------------------------------------------------------------------- #
def test_range_no_fanout_and_scopes(spark):
    spine = _spine(spark)
    scope_ids = build_scope_ids(spine, "entity_id")
    windows = add_window_bounds(spine, "entity_id", "anchor_date", 1, 1)

    out = apply_scope(
        _raw(spark),
        on="entity_id",
        strategy="range",
        scope_ids=scope_ids,
        windows=windows,
        date_col="event_date",
    ).collect()

    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    # A's 2025-03-15 row appears ONCE despite matching two overlapping windows;
    # A's June row and entity C are dropped.
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    assert len(out) == 2  # explicit: no fan-out duplication


def test_range_coarse_prune_is_correct(spark):
    spine = _spine(spark)
    windows = add_window_bounds(spine, "entity_id", "anchor_date", 1, 1)
    # prune_col == event_date here; bounds cover all in-window rows.
    out = apply_scope(
        _raw(spark),
        on="entity_id",
        strategy="range",
        windows=windows,
        date_col="event_date",
        prune_col="event_date",
        prune_bounds=("2025-01-01", "2025-05-31"),
    ).collect()
    assert sorted(r["entity_id"] for r in out) == ["A", "B"]


# --------------------------------------------------------------------------- #
# grid strategy
# --------------------------------------------------------------------------- #
def test_grid_month_equi(spark):
    spine = _spine(spark)
    scope_ids = build_scope_ids(spine, "entity_id")
    grid = build_grid(spine, "entity_id", "anchor_date", 1, 1, grain="month")

    out = apply_scope(
        _raw(spark),
        on="entity_id",
        strategy="grid",
        scope_ids=scope_ids,
        grid=grid,
        date_col="event_date",
        grain="month",
    ).collect()

    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    # helper column must not leak into the payload
    assert "_obs_grain" not in out[0].asDict()


# --------------------------------------------------------------------------- #
# id_only strategy
# --------------------------------------------------------------------------- #
def test_id_only_keeps_all_dates_for_scoped_ids(spark):
    spine = _spine(spark)
    scope_ids = build_scope_ids(spine, "entity_id")

    out = apply_scope(
        _raw(spark), on="entity_id", strategy="id_only", scope_ids=scope_ids
    ).collect()

    # every row for A and B survives (no date filter); C is dropped.
    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    assert got == [("A", "2025-03-15"), ("A", "2025-06-01"), ("B", "2025-01-10")]


# --------------------------------------------------------------------------- #
# guardrails
# --------------------------------------------------------------------------- #
def test_missing_inputs_raise(spark):
    with pytest.raises(ValueError):
        apply_scope(_raw(spark), on="entity_id", strategy="range", date_col="event_date")
    with pytest.raises(ValueError):
        apply_scope(_raw(spark), on="entity_id", strategy="bogus")
