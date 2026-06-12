"""Tests for collections_spine.

Covers the cases where SCD2 / spine logic typically breaks: interval boundaries,
the 2100-01-01 open-end sentinel, restatement (date_modified) dedup, future-
restatement leakage, and exact vs as-of daily matching.

Run: pytest -q   (requires pyspark; tests skip cleanly if it is not installed)
"""

from __future__ import annotations

import datetime as dt

import pytest

pyspark = pytest.importorskip("pyspark")

from pyspark.sql import SparkSession  # noqa: E402

from collections_spine import (  # noqa: E402
    OPEN_END_SENTINEL,
    Scd2Schema,
    active_as_of,
    build_spine,
    prefilter_daily,
    prefilter_scd2,
)


@pytest.fixture(scope="module")
def spark():
    ss = (
        SparkSession.builder.master("local[2]")
        .appName("collections_spine-tests")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.enabled", "false")
        .getOrCreate()
    )
    yield ss
    ss.stop()


def _d(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


SCD2_COLS = ["account_id", "effective_start_date", "effective_end_date", "date_modified", "limit"]


def _scd2(spark, rows):
    df = spark.createDataFrame(rows, SCD2_COLS)
    for c in ("effective_start_date", "effective_end_date", "date_modified"):
        df = df.withColumn(c, df[c].cast("date"))
    return df


# --------------------------------------------------------------------------- #
# active_as_of
# --------------------------------------------------------------------------- #
def test_active_as_of_picks_covering_interval(spark):
    df = _scd2(spark, [
        ("A", "2025-01-01", "2025-06-01", "2025-01-01", 100),
        ("A", "2025-06-01", OPEN_END_SENTINEL, "2025-06-01", 200),  # open record
    ])
    out = {r["account_id"]: r["limit"] for r in active_as_of(df, "2025-07-15").collect()}
    assert out == {"A": 200}


def test_half_open_boundary_is_exclusive_on_end(spark):
    # obs == end_date must NOT match a half-open [start, end) interval.
    df = _scd2(spark, [("A", "2025-01-01", "2025-06-01", "2025-01-01", 100)])
    assert active_as_of(df, "2025-06-01").count() == 0
    assert active_as_of(df, "2025-05-31").count() == 1


def test_end_inclusive_includes_end_day(spark):
    df = _scd2(spark, [("A", "2025-01-01", "2025-06-01", "2025-01-01", 100)])
    schema = Scd2Schema(end_inclusive=True)
    assert active_as_of(df, "2025-06-01", schema).count() == 1


def test_restatement_latest_modified_wins(spark):
    df = _scd2(spark, [
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-01-01", 100),
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-03-01", 150),  # later correction
    ])
    out = active_as_of(df, "2025-04-01").collect()
    assert len(out) == 1 and out[0]["limit"] == 150


def test_knowledge_date_blocks_future_restatement(spark):
    # A correction booked after the observation date must not leak in.
    df = _scd2(spark, [
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-01-01", 100),
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-09-01", 999),  # future correction
    ])
    out = active_as_of(df, "2025-04-01", knowledge_date="2025-04-01").collect()
    assert len(out) == 1 and out[0]["limit"] == 100


# --------------------------------------------------------------------------- #
# prefilter_scd2
# --------------------------------------------------------------------------- #
def test_prefilter_scd2_grid_and_population_filter(spark):
    df = _scd2(spark, [
        ("A", "2025-01-01", "2025-06-01", "2025-01-01", 100),
        ("A", "2025-06-01", OPEN_END_SENTINEL, "2025-06-01", 200),
        ("Z", "2025-01-01", OPEN_END_SENTINEL, "2025-01-01", 777),  # not in spine pop
    ])
    spine = build_spine(
        spark.createDataFrame([("A",)], ["account_id"]),
        ["2025-03-31", "2025-07-31"],
    )
    out = {(r["account_id"], str(r["observation_date"])): r["limit"]
           for r in prefilter_scd2(df, spine).collect()}
    assert out == {
        ("A", "2025-03-31"): 100,
        ("A", "2025-07-31"): 200,
    }


def test_prefilter_scd2_respects_knowledge_time(spark):
    df = _scd2(spark, [
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-01-01", 100),
        ("A", "2025-01-01", OPEN_END_SENTINEL, "2025-08-01", 999),  # booked after obs
    ])
    spine = build_spine(spark.createDataFrame([("A",)], ["account_id"]), ["2025-03-31"])
    rows = prefilter_scd2(df, spine, respect_knowledge_time=True).collect()
    assert len(rows) == 1 and rows[0]["limit"] == 100


# --------------------------------------------------------------------------- #
# prefilter_daily
# --------------------------------------------------------------------------- #
def _daily(spark, rows):
    df = spark.createDataFrame(rows, ["account_id", "snapshot_date", "bal"])
    return df.withColumn("snapshot_date", df["snapshot_date"].cast("date"))


def test_prefilter_daily_exact_match(spark):
    df = _daily(spark, [
        ("A", "2025-03-31", 10),
        ("A", "2025-03-30", 9),   # off by a day -> excluded in exact mode
        ("B", "2025-03-31", 20),  # B not in spine
    ])
    spine = build_spine(spark.createDataFrame([("A",)], ["account_id"]), ["2025-03-31"])
    out = prefilter_daily(df, spine).collect()
    assert len(out) == 1 and out[0]["bal"] == 10 and out[0]["account_id"] == "A"


def test_prefilter_daily_asof_latest_before(spark):
    df = _daily(spark, [
        ("A", "2025-03-10", 1),
        ("A", "2025-03-28", 2),   # latest on/before 03-31
        ("A", "2025-04-02", 3),   # after obs -> excluded
    ])
    spine = build_spine(spark.createDataFrame([("A",)], ["account_id"]), ["2025-03-31"])
    out = prefilter_daily(df, spine, asof=True, lookback_days=45).collect()
    assert len(out) == 1 and out[0]["bal"] == 2
