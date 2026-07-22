"""Tests for collections_spine.scope.filters (staging application).

Focus on the ways scope filtering typically breaks: fan-out when a raw row falls
in several anchor windows (must survive exactly once), the three strategies, and
the coarse partition prune. Scope sets are built inline here -- in production they
come from upstream nodes, not from this module.

Run: pytest -q   (requires pyspark; tests skip cleanly if it is not installed)
"""

from __future__ import annotations

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import functions as F  # noqa: E402

from collections_spine.scope import apply_scope  # noqa: E402

# `spark` fixture is provided by the repo-root conftest.py (session-scoped).


def _raw(spark):
    rows = [
        ("A", "2025-03-15", "load1"),  # in BOTH of A's windows (overlap) -> once
        ("A", "2025-06-01", "load1"),  # outside A's windows
        ("B", "2025-01-10", "load1"),  # in B's window
        ("C", "2025-01-10", "load1"),  # entity not in scope
    ]
    df = spark.createDataFrame(rows, ["entity_id", "event_date", "load_col"])
    return df.withColumn("event_date", df["event_date"].cast("date"))


def _scope_ids(spark):
    return spark.createDataFrame([("A",), ("B",)], ["entity_id"])


def _windows(spark):
    # A has TWO anchors whose +/-1-month windows overlap around 2025-03; B one.
    rows = [
        ("A", "2025-02-01", "2025-04-01"),
        ("A", "2025-03-01", "2025-05-01"),
        ("B", "2024-12-01", "2025-02-01"),
    ]
    df = spark.createDataFrame(rows, ["entity_id", "win_start", "win_end"])
    return df.withColumn("win_start", F.col("win_start").cast("date")).withColumn(
        "win_end", F.col("win_end").cast("date")
    )


def _grid(spark):
    # (entity_id, obs_month) enumerated at month grain
    rows = [("A", "2025-03-01"), ("B", "2025-01-01")]
    df = spark.createDataFrame(rows, ["entity_id", "obs_month"])
    return df.withColumn("obs_month", F.col("obs_month").cast("date"))


# --------------------------------------------------------------------------- #
# range
# --------------------------------------------------------------------------- #
def test_range_no_fanout_and_scopes(spark):
    out = apply_scope(
        _raw(spark),
        id_col="entity_id",
        strategy="range",
        scope_ids=_scope_ids(spark),
        windows=_windows(spark),
        date_col="event_date",
    ).collect()

    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    # A's 2025-03-15 appears ONCE despite matching two overlapping windows;
    # A's June row and entity C are dropped.
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    assert len(out) == 2  # explicit: no fan-out duplication


def test_range_coarse_prune_is_correct(spark):
    out = apply_scope(
        _raw(spark),
        id_col="entity_id",
        strategy="range",
        windows=_windows(spark),
        date_col="event_date",
        prune_col="event_date",
        prune_bounds=("2025-01-01", "2025-05-31"),
    ).collect()
    assert sorted(r["entity_id"] for r in out) == ["A", "B"]


# --------------------------------------------------------------------------- #
# grid
# --------------------------------------------------------------------------- #
def test_grid_month_equi(spark):
    out = apply_scope(
        _raw(spark),
        id_col="entity_id",
        strategy="grid",
        scope_ids=_scope_ids(spark),
        grid=_grid(spark),
        date_col="event_date",
        grid_col="obs_month",
        grain="month",
    ).collect()

    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    # no helper column leaks into the payload
    assert set(out[0].asDict()) == {"entity_id", "event_date", "load_col"}


# --------------------------------------------------------------------------- #
# id_only
# --------------------------------------------------------------------------- #
def test_id_only_keeps_all_dates_for_scoped_ids(spark):
    out = apply_scope(
        _raw(spark),
        id_col="entity_id",
        strategy="id_only",
        scope_ids=_scope_ids(spark),
    ).collect()

    got = sorted((r["entity_id"], r["event_date"].isoformat()) for r in out)
    assert got == [("A", "2025-03-15"), ("A", "2025-06-01"), ("B", "2025-01-10")]


# --------------------------------------------------------------------------- #
# guardrails
# --------------------------------------------------------------------------- #
def test_missing_inputs_raise(spark):
    with pytest.raises(ValueError):
        apply_scope(_raw(spark), id_col="entity_id", strategy="range", date_col="event_date")
    with pytest.raises(ValueError):
        apply_scope(_raw(spark), id_col="entity_id", strategy="bogus")
