"""Spark tests for the crx_persona deterioration nodes — synthetic data, no catalog, no PROD.

Workplace location: src/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py.
Run: python -m pytest src/tests/nodes/crx_persona   (needs Java + pyspark >= 3.3)

Builds raw tables the way the sources look (CC billing with add_info, RL monthly loan
master) with their known noise — same-day duplicates, unparseable add_info, billing-cycle
shifts, months missing between equal neighbours, unresolvable gaps, history before the CC
floor, double spine keys — runs the node functions end to end, and checks every account
against the per-account engine (itself covered by test_dpd_journey.py).
"""
from __future__ import annotations

import datetime as dt
import random

import pytest
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona import _dpd_journey as J
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.nodes import (
    build_cc_a4_deterioration, build_cc_dpd_sequences)
from enbd_collections.pipelines.crx_persona.cc_full_history.nodes import build_cc_full_history
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.nodes import (
    build_rl_a4_deterioration, build_rl_dpd_sequences)
from enbd_collections.pipelines.crx_persona.rl_full_history.nodes import build_rl_full_history

SNAP = dt.date(2026, 8, 31)
SNAP_IDX = SNAP.year * 12 + SNAP.month - 1
FLOOR_IDX = 2024 * 12                      # 2024-01, the CC history floor default
N = 600


def _journey(rng: random.Random) -> list[int]:
    """One CC journey, oldest -> newest, ending in the 60-180 or 180+ segment."""
    b = [0] * rng.randint(0, 60)
    if rng.random() < 0.25:                                    # an earlier cured spell
        b += [2, 3][: rng.randint(1, 2)] + [0] * rng.randint(1, 20)
    level = 2
    b.append(level)
    target = rng.choice([4, 5, 6, 7, 7, 9])
    while level < target:
        u = rng.random()
        if u < 0.7:
            level += 1                                         # roll
        elif u < 0.9 or level < 4:
            pass                                               # hold
        else:
            level -= 1                                         # pay two months
        b.append(level)
    for _ in range(rng.randint(0, 14)):                        # life in the segment
        u = rng.random()
        if target == 9 or u < 0.5:
            pass
        elif u < 0.8 and level < 7:
            level += 1
        elif level > 4:
            level -= 1
        b.append(level)
    if rng.random() < 0.05:
        b = [rng.choice([4, 5, 9])] * rng.randint(3, 10)       # history starts delinquent
    return b


def _month(idx: int, day: int) -> dt.datetime:
    y, m = divmod(idx, 12)
    return dt.datetime(y, m + 1, day)


@pytest.fixture(scope="module")
def journeys():
    rng = random.Random(11)
    return [_journey(rng) for _ in range(N)]


def _cc_raw(journeys):
    """raw_stg_billing rows and the expected (kept history, cropped) per account."""
    rng = random.Random(5)
    rows, expected = [], {}
    for k, b in enumerate(journeys):
        acc = 900_000_000 + k
        start = SNAP_IDX - len(b) + 1
        months = {start + t: v for t, v in enumerate(b)}
        bills = [(m, 15, v) for m, v in months.items()]
        first_kept = max(start, FLOOR_IDX)
        interior = [m for m in months if first_kept + 1 < m < SNAP_IDX - 4]
        u = rng.random()
        if u < 0.10 and len(interior) > 2:                     # billing-cycle shift
            m = rng.choice(interior)
            bills = [x for x in bills if x[0] != m] + [(m + 1, 1, months[m])]
        elif u < 0.20 and len(interior) > 2:                   # gap between equal neighbours
            cand = [m for m in interior if months[m - 1] == months[m] == months[m + 1]]
            if cand:
                bills = [x for x in bills if x[0] != rng.choice(cand)]
        elif u < 0.25 and len(interior) > 6:                   # unresolvable 3-month gap
            m = interior[len(interior) // 2 - 3]
            cl, cr = max(months[m - 1], 1), max(months[m + 3], 1)
            if cl != cr and cr - cl != 4:
                bills = [x for x in bills if not m <= x[0] <= m + 2]
                first_kept = max(first_kept, m + 3)
        for m, day, v in bills:
            rows.append((float(acc), _month(m, day), f"A=1;BS_PMT_CYCLE_DUE={v};B=2"))
            if rng.random() < 0.03:
                rows.append((float(acc), _month(m, day), f"A=1;BS_PMT_CYCLE_DUE={v};B=2"))
            if rng.random() < 0.03:
                rows.append((float(acc), _month(m, day), "A=1;NO_BUCKET"))
        kept = [months[m] for m in range(first_kept, SNAP_IDX + 1)]
        expected[acc] = (kept, first_kept > start)
    return rows, expected


@pytest.fixture(scope="module")
def cc(spark, journeys):
    rows, expected = _cc_raw(journeys)
    raw = spark.createDataFrame(rows, "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(float(a),) for a in expected], "contract_id double")
    spells = spark.createDataFrame(
        [(a, "restructured_entry" if a % 37 == 0 else "none") for a in expected],
        "account_id long, censored_subtype string")
    return raw, spine, spells, expected


@pytest.mark.parametrize("segment", ["60_180", "180_plus"])
def test_cc_end_to_end(cc, segment):
    raw, spine, spells, expected = cc
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"segment": segment}}
    seq = build_cc_dpd_sequences(build_cc_full_history(raw, spine), spells, params)
    got = {r.account_id: r for r in build_cc_a4_deterioration(seq, params).collect()}
    want = {a: J.classify(k, c, 0, 9)
            for a, (k, c) in expected.items() if max(k[-1], 1) in J.SEGMENTS[segment]}
    assert set(got) == set(want), "every account in the segment is classified, no others"
    for a, w in want.items():
        assert got[a].det_state == w["det_state"], (a, expected[a])
        assert got[a].history_cropped == expected[a][1], a
        assert got[a].det_state_label == J.DISPLAY_NAMES[w["det_state"]]
    assert {r.det_state for r in got.values()} <= set(J.STATES)
    if segment == "180_plus":
        assert "stabilized" not in {r.det_state for r in got.values()}
    statuses = {r.build_status for r in seq.select("build_status").distinct().collect()}
    assert statuses == {"ok"}, "no account dropped"


def test_cc_audit_columns(cc):
    raw, spine, spells, _ = cc
    params = {"persona_end_date": str(SNAP)}
    seq = build_cc_dpd_sequences(build_cc_full_history(raw, spine), spells, params)
    r = seq.agg(*[F.sum(c).alias(c) for c in ("n_cycle_shift_moves", "n_gap_months_filled",
                                              "n_months_truncated", "restructure_blind_spot_flag")],
                F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop")).first()
    assert r.n_cycle_shift_moves > 0 and r.n_gap_months_filled > 0 and r.n_months_truncated > 0
    assert r.legacy_drop > 0, "the old rule would have dropped some of these accounts"
    assert r.restructure_blind_spot_flag == len([a for a in cc[3] if a % 37 == 0])


def test_cc_full_history_dedupe_and_bad_rows(spark):
    raw = spark.createDataFrame([
        (1.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=3"),
        (1.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=4"),     # same date: worst wins
        (1.0, dt.datetime(2025, 2, 15), "NO_BUCKET"),               # unparseable: NULL, no error
        (2.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=2"),      # not in the spine
    ], "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(1.0,)], "contract_id double")
    out = {(r.billing_date.month, r.dlq_bucket) for r in build_cc_full_history(raw, spine).collect()}
    assert out == {(1, 4), (2, None)}


@pytest.mark.parametrize("segment", ["60_180", "180_plus"])
def test_rl_end_to_end(spark, journeys, segment):
    rows, want = [], {}
    rl = {f"L{k:07d}": [min(max(x, 1), 8) - 1 for x in b] for k, b in enumerate(journeys)}
    global_min = min(SNAP_IDX - len(b) + 1 for b in rl.values())
    for acc, b in rl.items():
        start = SNAP_IDX - len(b) + 1
        rows += [(acc, _month(start + t, 28).date(), v, 1.0, 100.0, 0, "PL") for t, v in enumerate(b)]
        if max(b[-1] + 1, 1) in J.SEGMENTS[segment]:
            want[acc] = J.classify(b, start <= global_min, 1, 8)["det_state"]
    master = spark.createDataFrame(rows, "account_id string, observation_date date, dpd_bucket int, "
                                         "emi_coverage_ratio double, outstanding_balance double, "
                                         "is_restructured int, loan_type string")
    spine = spark.createDataFrame([(a,) for a in rl], "account_id string")
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"segment": segment}}
    seq = build_rl_dpd_sequences(build_rl_full_history(spine, master, params), params)
    got = {r.account_id: r for r in build_rl_a4_deterioration(seq, params).collect()}
    assert {a: r.det_state for a, r in got.items()} == want
    allowed = set(J.RL.native_buckets(J.SEGMENTS[segment]))
    assert {r.current_bucket for r in got.values()} <= allowed
    if segment == "180_plus":
        assert "stabilized" not in set(want.values())


def test_rl_double_spine_key_matches_string_master(spark):
    master = spark.createDataFrame(
        [(str(123456789 + k), dt.date(2026, 8, 31), 3, 1.0, 1.0, 0, "PL") for k in range(20)],
        "account_id string, observation_date date, dpd_bucket int, emi_coverage_ratio double, "
        "outstanding_balance double, is_restructured int, loan_type string")
    spine = spark.createDataFrame([(float(123456789 + k),) for k in range(20)], "account_id double")
    assert build_rl_full_history(spine, master).select("account_id").distinct().count() == 20
