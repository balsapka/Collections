"""Spec test for the RL restructure chains (bundles 11, 13): resolve_chains and the linked A4 nodes.

JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a4_chain_spec.py
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pyspark.sql import SparkSession  # noqa: E402

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


def check_nodes(spark: SparkSession) -> None:
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
    check_nodes(spark)
    print("a4 chain spec: all checks pass")


if __name__ == "__main__":
    main()
