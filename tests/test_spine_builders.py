"""Tests for the contract_pit point-in-time selection in spine_builders.

Focus on the branches that are easy to get wrong on this latest-record_date_from
-wins / sentinel-end table:

* exact-match fast path (record_date_from == observation_date)
* future-restatement fallback (a same-start version booked after obs must not leak)
* anchor-prune boundary (the deep historical tail is dropped, the anchor kept)
* a pair with no active contract version is dropped

Skips cleanly when pyspark is unavailable. `spark` comes from conftest.py.
"""

from __future__ import annotations

import pytest

pytest.importorskip("pyspark")

from src.collections_spine.nodes.spine_builders import contract_pit  # noqa: E402

SENTINEL = "2100-01-01"

CS_COLS = [
    "contract_idt", "record_date_from", "record_date_to",
    "edp_modifiedts", "dlq_hist", "product_id", "client_idt",
]


def _cs(spark, rows):
    """Build a contract_slim-shaped DataFrame (date columns cast to date)."""
    df = spark.createDataFrame(rows, CS_COLS)
    for c in ("record_date_from", "record_date_to", "edp_modifiedts"):
        df = df.withColumn(c, df[c].cast("date"))
    return df


def _spine(spark, rows):
    df = spark.createDataFrame(rows, ["contract_idt", "observation_date"])
    return df.withColumn("observation_date", df["observation_date"].cast("date"))


def _by_pair(df):
    return {
        (r["contract_idt"], str(r["observation_date"])): r
        for r in df.collect()
    }


def test_exact_start_equals_observation(spark):
    # The version whose start == obs wins over an earlier open version.
    cs = _cs(spark, [
        ("A", "2025-01-01", SENTINEL, "2025-01-01", 4, "P1", "C1"),
        ("A", "2025-03-31", SENTINEL, "2025-03-31", 5, "P1", "C1"),
    ])
    out = _by_pair(contract_pit(cs, _spine(spark, [("A", "2025-03-31")]),
                                {"start_date": "2025-01-01"}))
    r = out[("A", "2025-03-31")]
    assert r["dlq_hist"] == 5
    assert str(r["record_date_from"]) == "2025-03-31"
    # carried-through columns survive PIT
    assert r["product_id"] == "P1" and r["client_idt"] == "C1"


def test_future_restatement_falls_back(spark):
    # The start==obs version was booked AFTER obs (edp_modifiedts > obs); it must
    # not leak, so selection falls back to the latest version known by obs.
    cs = _cs(spark, [
        ("A", "2025-01-01", SENTINEL, "2025-01-01", 4, "P1", "C1"),
        ("A", "2025-03-31", SENTINEL, "2025-09-01", 7, "P1", "C1"),  # future correction
    ])
    out = _by_pair(contract_pit(cs, _spine(spark, [("A", "2025-03-31")]),
                                {"start_date": "2025-01-01"}))
    r = out[("A", "2025-03-31")]
    assert r["dlq_hist"] == 4 and str(r["record_date_from"]) == "2025-01-01"


def test_anchor_prune_boundary(spark):
    # The deep 2020 tail is superseded; the 2023-12-01 anchor (latest start on or
    # before start_date) must remain selectable at the window's first observation.
    cs = _cs(spark, [
        ("A", "2020-01-01", SENTINEL, "2020-01-01", 9, "P1", "C1"),  # must never win
        ("A", "2023-12-01", SENTINEL, "2023-12-01", 4, "P1", "C1"),  # anchor
        ("A", "2024-06-01", SENTINEL, "2024-06-01", 5, "P1", "C1"),  # within window
    ])
    spine = _spine(spark, [("A", "2024-01-31"), ("A", "2024-07-31")])
    out = _by_pair(contract_pit(cs, spine, {"start_date": "2024-01-01"}))
    assert out[("A", "2024-01-31")]["dlq_hist"] == 4
    assert out[("A", "2024-07-31")]["dlq_hist"] == 5
    assert 9 not in {r["dlq_hist"] for r in out.values()}


def test_pair_with_no_active_version_is_dropped(spark):
    # Observation precedes the contract's first start -> no active version -> no row.
    cs = _cs(spark, [
        ("A", "2024-06-01", SENTINEL, "2024-06-01", 5, "P1", "C1"),
    ])
    out = contract_pit(cs, _spine(spark, [("A", "2024-03-31")]),
                       {"start_date": "2024-01-01"}).collect()
    assert out == []
