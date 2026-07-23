"""Tests for collections_spine.scope.filters (composable staging filters).

Focus on the ways scope filtering typically breaks: fan-out when a raw row falls
in several anchor windows (must survive exactly once), column-name mapping via
scope_*_col (no renamed dataset copies), and exact-pair matching. Scope sets are
built inline here -- in production they come from upstream nodes.

Run: pytest -q   (requires pyspark; tests skip cleanly if it is not installed)
"""

from __future__ import annotations

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import functions as F  # noqa: E402

from collections_spine.scope import filter_ids, filter_pairs, filter_windows  # noqa: E402

# `spark` fixture is provided by the repo-root conftest.py (session-scoped).


def _raw(spark):
    # raw table uses contract_idt / txn_date -- names differ from the scope sets.
    rows = [
        ("A", "2025-03-15", 10),  # in BOTH of A's windows (overlap) -> once
        ("A", "2025-06-01", 20),  # outside A's windows
        ("B", "2025-01-10", 30),  # in B's window
        ("C", "2025-01-10", 40),  # entity not in scope
    ]
    df = spark.createDataFrame(rows, ["contract_idt", "txn_date", "amount"])
    return df.withColumn("txn_date", df["txn_date"].cast("date"))


def _scope_ids(spark):
    # scope set uses customer_id -- mapped via scope_id_col.
    return spark.createDataFrame([("A",), ("B",)], ["customer_id"])


def _windows(spark):
    # A has TWO anchors whose windows overlap around 2025-03; B one.
    rows = [
        ("A", "2025-02-01", "2025-04-01"),
        ("A", "2025-03-01", "2025-05-01"),
        ("B", "2024-12-01", "2025-02-01"),
    ]
    df = spark.createDataFrame(rows, ["customer_id", "win_start", "win_end"])
    return df.withColumn("win_start", F.col("win_start").cast("date")).withColumn(
        "win_end", F.col("win_end").cast("date")
    )


def _pairs(spark):
    # exact (id, date) pairs at the raw table's (daily) grain, own column names.
    rows = [("A", "2025-03-15"), ("B", "2025-01-10")]
    df = spark.createDataFrame(rows, ["customer_id", "obs_date"])
    return df.withColumn("obs_date", F.col("obs_date").cast("date"))


# --------------------------------------------------------------------------- #
# filter_ids
# --------------------------------------------------------------------------- #
def test_filter_ids_maps_column_names(spark):
    out = filter_ids(
        _raw(spark), _scope_ids(spark),
        id_col="contract_idt", scope_id_col="customer_id",
    ).collect()
    got = sorted((r["contract_idt"], r["txn_date"].isoformat()) for r in out)
    assert got == [
        ("A", "2025-03-15"), ("A", "2025-06-01"), ("B", "2025-01-10"),
    ]  # all dates kept; C dropped
    # payload untouched -- no scope columns leak in
    assert set(out[0].asDict()) == {"contract_idt", "txn_date", "amount"}


# --------------------------------------------------------------------------- #
# filter_windows
# --------------------------------------------------------------------------- #
def test_filter_windows_no_fanout(spark):
    out = filter_windows(
        _raw(spark), _windows(spark),
        id_col="contract_idt", date_col="txn_date", scope_id_col="customer_id",
    ).collect()
    got = sorted((r["contract_idt"], r["txn_date"].isoformat()) for r in out)
    # A's 2025-03-15 appears ONCE despite matching two overlapping windows;
    # A's June row and entity C are dropped.
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    assert len(out) == 2  # explicit: no fan-out duplication
    assert set(out[0].asDict()) == {"contract_idt", "txn_date", "amount"}


def test_filter_windows_custom_bound_cols(spark):
    w = _windows(spark).withColumnRenamed("win_start", "s").withColumnRenamed("win_end", "e")
    out = filter_windows(
        _raw(spark), w,
        id_col="contract_idt", date_col="txn_date", scope_id_col="customer_id",
        start_col="s", end_col="e",
    ).collect()
    assert sorted(r["contract_idt"] for r in out) == ["A", "B"]


# --------------------------------------------------------------------------- #
# filter_pairs
# --------------------------------------------------------------------------- #
def test_filter_pairs_exact_match_and_mapping(spark):
    out = filter_pairs(
        _raw(spark), _pairs(spark),
        id_col="contract_idt", date_col="txn_date",
        scope_id_col="customer_id", scope_date_col="obs_date",
    ).collect()
    got = sorted((r["contract_idt"], r["txn_date"].isoformat()) for r in out)
    # exact pairs only: A's June row has no pair, C not in scope.
    assert got == [("A", "2025-03-15"), ("B", "2025-01-10")]
    assert set(out[0].asDict()) == {"contract_idt", "txn_date", "amount"}
