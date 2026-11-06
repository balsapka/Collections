"""Spec test: the RL restructure chains (bundles 11, 13), i.e. resolve_chains and the
linked A4 nodes; then the episode anchor A3 reads (episode_start), window_agg(start=).

JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a4_chain_spec.py
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from enbd_collections.pipelines.crx_persona._common import window_agg  # noqa: E402
from enbd_collections.pipelines.crx_persona._dpd_journey import episode_start  # noqa
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration import (  # noqa: E402
    create_pipeline,
)
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.chains import (  # noqa: E402
    Edge,
    resolve_chains,
)
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.nodes import (  # noqa: E402
    _LINK_ACCOUNT,
    _LINK_ORIGINAL,
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
    build_rl_linked_dpd_sequences,
)
from pyspark.sql import DataFrame, SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402


def month_end(index: int) -> dt.date:
    """Month ``index`` from 2024-01 as a month-end date."""
    year, month = 2024 + index // 12, index % 12 + 1
    return dt.date(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(1)


def check_chains() -> None:
    day = dt.date(2026, 1, 1)
    later = dt.date(2026, 5, 1)
    edges = [
        Edge("R", "C1", day, "one_to_one", 1),
        Edge("C1", "C2", later, "many_to_one", 3),
        Edge("X", "Y", day, "one_to_one", 1),
        Edge("Y", "X", day, "one_to_one", 1),  # a cycle must end
    ]
    chains, members = resolve_chains(edges, ["R", "X", "alone"])
    by = {c.account: c for c in chains}
    assert set(by) == {"R", "X"}
    assert by["R"].known == later and by["R"].n_originals == 2
    assert by["R"].match_type == "many_to_one" and by["R"].candidates == 3
    assert [m.original for m in members if m.account == "R"] == ["C1", "C2"]
    assert by["X"].n_originals == 1


def check_anchor(spark: SparkSession, a4: DataFrame) -> None:
    """episode_start on the A4 output and on long-keyed, billing-dated rows (CC); the
    left-censored pair; window_agg(start=), both bounds inclusive."""
    d = dt.date
    base = spark.createDataFrame(
        [("plain", month_end(33)), ("101", d(2025, 5, 31)), ("101", d(2025, 6, 30))]
        + [(k, d(2025, 6, 30)) for k in ("102", "103", "104")],
        "account_id string, observation_date date",
    )
    a4_rows = [  # clean Jan-Mar 2025, delinquent from April
        (101, d(2025, 5, 15), 3, 5, False, False),
        (101, d(2025, 6, 15), 3, 6, False, False),
        (102, d(2025, 6, 15), 0, 4, True, True),  # cropped: onset unknown
        (103, d(2025, 6, 15), 0, 4, True, False),  # uncropped: true onset
        (104, d(2025, 5, 15), 3, 5, False, False),  # last month's row: none
    ]
    cc = spark.createDataFrame(
        a4_rows,
        "account_id long, observation_date date, months_before_spell int, "
        "history_months int, left_censored boolean, history_cropped boolean",
    )
    got = {
        (r["account_id"], r["observation_date"]): (r[2], r[3])
        for src in (a4, cc)
        for r in episode_start(base, src).collect()
    }
    assert got == {
        ("plain", month_end(33)): (d(2026, 7, 1), False),
        ("101", d(2025, 5, 31)): (d(2025, 4, 1), False),
        ("101", d(2025, 6, 30)): (d(2025, 4, 1), False),
        ("102", d(2025, 6, 30)): (d(2025, 3, 1), True),
        ("103", d(2025, 6, 30)): (d(2025, 3, 1), False),
    }, got
    obs = d(2025, 6, 30)  # window_start(3) = 2025-04-01
    starts = spark.createDataFrame(
        [("a", obs, d(2025, 5, 10)), ("b", obs, d(2025, 1, 1))],
        "account_id string, observation_date date, start date",
    )
    days = [("a", d(2025, 5, k)) for k in (9, 10)] + [("a", obs), ("a", d(2025, 7, 1))]
    days += [("b", d(2025, 3, 31)), ("b", d(2025, 4, 1)), ("b", obs)]
    events = spark.createDataFrame(days, "account_id string, day date")
    aggs = [F.min("day").alias("first"), F.count("day").alias("n")]
    kw = {"date_col": "day", "months": 3, "key": "account_id", "start": "start"}
    agg = window_agg(starts, events, aggs=aggs, **kw)
    assert {r[0]: (r["first"], r["n"]) for r in agg.collect()} == {
        "a": (d(2025, 5, 10), 2),  # start after the window start bounds it
        "b": (d(2025, 4, 1), 2),  # start before it: the window start bounds it
    }


def check_nodes(spark: SparkSession) -> DataFrame:
    obs_index, close, late = 33, 28, 33
    own = {
        "plain": (28, [0, 0, 1, 2, 3, 3], 0),
        "linked": (29, [0, 0, 1, 2, 3], 1),  # known at 28: stitched at obs
        "late": (29, [0, 0, 1, 2, 3], 1),  # known at 33: stitched from 33 on
        "unlinked": (29, [3, 3, 3, 3, 4], 1),  # stays blind
        "no_feature": (29, [0, 0, 1, 2, 3], 0),  # raw flag set, feature not
    }
    history = spark.createDataFrame(
        [
            (k, month_end(start + i), bucket, 1)  # the raw flag is never read
            for k, (start, buckets, _) in own.items()
            for i, bucket in enumerate(buckets)
        ],
        ["account_id", "month_end_date", "dlq_bucket", "restructure_flag"],
    )
    master_rows = []
    for name in ("c_linked", "c_late"):
        master_rows += [
            (name, month_end(10 + i), bucket, "ACTIVE")
            for i, bucket in enumerate([0] * 15 + [1, 2, 3])
        ]
        master_rows.append((name, month_end(close), 0, "CLOSED"))
    master = spark.createDataFrame(
        master_rows,
        [
            "account_id",
            "observation_date",
            "dpd_bucket",
            "account_status",
        ],
    )
    link_rows = [
        ("linked", "c_linked", month_end(28), month_end(28), "one_to_one", 2),
        ("late", "c_late", month_end(late), month_end(28), "one_to_one", 1),
        ("unlinked", None, month_end(29), None, None, 0),
    ]
    link = spark.createDataFrame(
        link_rows,
        [
            _LINK_ACCOUNT,
            _LINK_ORIGINAL,
            "restr_flagged_date",
            "orig_close_date",
            "match_type",
            "candidate_count",
        ],
    )
    linked, chains = build_rl_full_history_linked(history, master, link)
    rows = {r["account_id"]: r for r in chains.collect()}
    assert set(rows) == {"linked", "late"}
    assert rows["linked"]["chain_months_added"] == 18
    assert (
        linked.filter("dlq_bucket = 0 and month_end_date = '2026-05-31'")
        .filter("account_id = 'linked'")
        .count()
        == 0
    ), "the CLOSED month must not be stitched"

    persona = {"persona_end_date": str(month_end(obs_index))}
    feature = spark.createDataFrame(
        [(k, month_end(33), flag) for k, (_, _, flag) in own.items()],
        ["account_id", "observation_date", "has_restructured_loan_flag"],
    )
    seq_own = build_rl_dpd_sequences(history, feature, persona, "rl_60_180")
    seq_linked = build_rl_linked_dpd_sequences(
        linked, chains, feature, persona, "rl_60_180"
    )
    spine = spark.createDataFrame(
        [(k, month_end(33)) for k in own] + [("late", month_end(32))],
        ["account_id", "observation_date"],
    )
    out = build_rl_a4_deterioration(
        seq_own, seq_linked, chains, spine, persona, "rl_60_180"
    )
    got = {(r["account_id"], r["observation_date"]): r for r in out.collect()}
    assert len(got) == 6
    obs = month_end(33)
    assert got[("linked", obs)]["chain_stitched_flag"] == 1
    assert got[("linked", obs)]["restructure_blind_spot_flag"] == 0
    assert got[("linked", obs)]["history_months"] > 20
    assert got[("late", obs)]["chain_stitched_flag"] == 1
    early = got[("late", month_end(32))]
    assert (
        early["chain_stitched_flag"] == 0 and early["history_months"] == 4
    ), "before the chain is known the account reads its own history"
    assert got[("no_feature", obs)]["restructure_blind_spot_flag"] == 0
    assert got[("unlinked", obs)]["restructure_blind_spot_flag"] == 1
    assert got[("unlinked", obs)]["chain_stitched_flag"] == 0
    assert got[("unlinked", obs)]["det_state"] in ("unknown", "stabilized")
    assert got[("plain", obs)]["chain_stitched_flag"] == 0
    return out


def main() -> None:
    check_chains()
    assert len(create_pipeline().nodes) == 4
    spark = (
        SparkSession.builder.master("local[2]")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.shuffle.partitions", "4")
        .getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    check_anchor(spark, check_nodes(spark))
    print("a4 chain spec: all checks pass")


if __name__ == "__main__":
    main()
