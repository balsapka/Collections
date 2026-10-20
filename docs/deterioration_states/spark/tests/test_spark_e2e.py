"""End to end on local Spark: synthetic raw tables -> the Kedro node functions -> states,
compared account by account with the (parity-tested) per-account core.

    python docs/deterioration_states/spark/tests/test_spark_e2e.py [n_accounts]

The raw tables carry the noise the real ones have: same-day duplicates, NULL / unparseable
add_info, billing-cycle shifts (two bills in one month, none in the next), months missing
between equal neighbours, history before the CC floor, and a few unresolvable gaps. The
node code is imported as a package that the Spark workers CANNOT import — so this also
proves the pickle-by-value shipping works without the project installed on executors.
"""
from __future__ import annotations

import datetime as dt
import os
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))                       # crx_persona package
sys.path.insert(0, str(HERE.parents[2]))                       # reference generators
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
os.environ["PYSPARK_PYTHON"] = sys.executable

from pyspark.sql import SparkSession                           # noqa: E402
from pyspark.sql import functions as F                         # noqa: E402

from crx_persona import _dpd_journey as J                      # noqa: E402
from crx_persona.cc_a4_deterioration.nodes import build_cc_a4_deterioration, build_cc_dpd_sequences  # noqa: E402
from crx_persona.cc_full_history.nodes import build_cc_full_history  # noqa: E402
from crx_persona.rl_a4_deterioration.nodes import build_rl_a4_deterioration, build_rl_dpd_sequences  # noqa: E402
from crx_persona.rl_full_history.nodes import build_rl_full_history  # noqa: E402
from dpd_states import segment_180, synth                      # noqa: E402

SNAP = dt.date(2026, 8, 31)
SNAP_IDX = SNAP.year * 12 + SNAP.month - 1
FLOOR_IDX = 2024 * 12 + 0


def _month_date(idx: int, day: int) -> dt.datetime:
    y, m = divmod(idx, 12)
    return dt.datetime(y, m + 1, day)


def _accounts(n: int) -> list[list[int]]:
    """CC journeys oldest -> newest, all ending in the snapshot month."""
    synth.calibrate(n=4000, iters=3)
    spine = [[int(c) for c in reversed(s)] for s in synth.generate(n).dpd_string]
    s180 = [[int(c) for c in reversed(s)] for s in segment_180.generate_180(n // 4).dpd_string]
    return spine + s180


def _cc_raw(journeys, rng):
    """raw_stg_billing rows + the expected (kept history, cropped) per account."""
    rows, expected = [], {}
    for k, b in enumerate(journeys):
        acc = 900_000_000 + k
        start = SNAP_IDX - len(b) + 1
        noise = rng.random()
        months = {start + t: v for t, v in enumerate(b)}
        bills = [(m, 15, v) for m, v in months.items()]
        trunc_from = None
        interior = [m for m in months if max(start, FLOOR_IDX) + 1 < m < SNAP_IDX - 1]
        if noise < 0.05 and len(interior) > 2:                      # cycle shift
            m = rng.choice(interior[:-1])
            bills = [x for x in bills if x[0] != m] + [(m + 1, 1, months[m])]
        elif noise < 0.10 and len(interior) > 2:                    # gap between equal neighbours
            cand = [m for m in interior if months[m - 1] == months[m] == months[m + 1]]
            if cand:
                drop = rng.choice(cand)
                bills = [x for x in bills if x[0] != drop]
        elif noise < 0.12 and len(interior) > 6:                    # unresolvable 3-month gap
            m = interior[len(interior) // 2 - 3]
            cl, cr = max(months[m - 1], 1), max(months[m + 3], 1)
            if cl != cr and cr - cl != 4:
                bills = [x for x in bills if not m <= x[0] <= m + 2]
                trunc_from = m + 3
        for m, day, v in bills:
            ts = _month_date(m, day)
            rows.append((float(acc), ts, f"X=1;BS_PMT_CYCLE_DUE={v};Y=2"))
            if rng.random() < 0.02:                                 # same-day duplicate
                rows.append((float(acc), ts, f"X=1;BS_PMT_CYCLE_DUE={v};Y=2"))
            if rng.random() < 0.02:                                 # unparseable row same day
                rows.append((float(acc), ts, "X=1;NO_BUCKET"))
        first_kept = max(start, FLOOR_IDX)
        if trunc_from is not None and trunc_from > first_kept:
            first_kept = trunc_from
        kept = [months[m] for m in range(first_kept, SNAP_IDX + 1)]
        expected[acc] = (kept, first_kept > start)
    return rows, expected


def main(n: int = 4000) -> int:
    t0 = time.time()
    rng = random.Random(3)
    spark = (SparkSession.builder.master("local[4]").appName("dpd_journey_e2e")
             .config("spark.sql.shuffle.partitions", "8").config("spark.ui.enabled", "false")
             .config("spark.sql.ansi.enabled", "true")               # Spark 4 default
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    journeys = _accounts(n)
    bad = 0

    # ---------------- CC ----------------
    rows, expected = _cc_raw(journeys, rng)
    raw = spark.createDataFrame(rows, "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(float(a),) for a in expected], "contract_id double")
    spells = spark.createDataFrame([(a, "restructured_entry" if a % 50 == 0 else "none") for a in expected],
                                   "account_id long, censored_subtype string")
    for segment in ("60_180", "180_plus"):
        params = {"persona_start_date": "2024-01-01", "persona_end_date": str(SNAP),
                  "dpd_journey": {"segment": segment, "log_stats": True}}
        full = build_cc_full_history(raw, spine)
        seq = build_cc_dpd_sequences(full, spells, params)
        out = build_cc_a4_deterioration(seq, params)
        got = {r.account_id: r for r in out.collect()}
        seg = J.SEGMENTS[segment]
        want = {a: J.classify(k, c, 0, 9, segment, "B_balanced_6") for a, (k, c) in expected.items()
                if max(k[-1], 1) in seg}
        miss = set(want) ^ set(got)
        wrong = [a for a in want if a in got and (got[a].det_state != want[a]["det_state"]
                                                  or got[a].history_cropped != expected[a][1])]
        bad += len(miss) + len(wrong)
        for a in wrong[:5]:
            print("  CC WRONG", a, got[a].det_state, want[a]["det_state"], expected[a])
        st = seq.groupBy("build_status").count().collect()
        print(f"CC {segment}: {len(got):,} classified of {len(want):,} expected; "
              f"{len(miss)} missing/extra, {len(wrong)} wrong; build_status {[tuple(r) for r in st]}")
        if segment == "60_180":
            counts = seq.agg(*[F.sum(c).alias(c) for c in ("n_cycle_shift_moves", "n_gap_months_filled",
                                                          "n_months_truncated", "n_dup_month_rows", "n_invalid_rows")],
                             F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop"),
                             F.sum("restructure_blind_spot_flag").alias("restructured")).first()
            print("   audit:", counts.asDict())

    # ---------------- RL ----------------
    rl_rows, rl_expected = [], {}
    for k, b in enumerate(journeys[: len(journeys) // 2]):
        acc = f"L{k:07d}"
        rlb = [min(max(x, 1), 8) - 1 for x in b]
        start = SNAP_IDX - len(rlb) + 1
        for t, v in enumerate(rlb):
            rl_rows.append((acc, _month_date(start + t, 28).date(), v, 1.0, 1000.0, int(k % 40 == 0), "PL"))
        rl_expected[acc] = rlb
    global_min = min(SNAP_IDX - len(b) + 1 for b in rl_expected.values())
    master = spark.createDataFrame(rl_rows, "account_id string, observation_date date, dpd_bucket int, "
                                            "emi_coverage_ratio double, outstanding_balance double, "
                                            "is_restructured int, loan_type string")
    rl_spine = spark.createDataFrame([(a,) for a in rl_expected], "account_id string")
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"log_stats": True}}
    full = build_rl_full_history(rl_spine, master, params)
    seq = build_rl_dpd_sequences(full, params)
    out = build_rl_a4_deterioration(seq, params)
    got = {r.account_id: r for r in out.collect()}
    want = {}
    for a, rlb in rl_expected.items():
        if max(rlb[-1] + 1, 1) in J.SEGMENTS["60_180"]:
            cropped = SNAP_IDX - len(rlb) + 1 <= global_min
            want[a] = J.classify(rlb, cropped, 1, 8, "60_180", "B_balanced_6")
    miss = set(want) ^ set(got)
    wrong = [a for a in want if a in got and got[a].det_state != want[a]["det_state"]]
    bad += len(miss) + len(wrong)
    cur = sorted({r.current_bucket for r in got.values()})
    print(f"RL 60_180: {len(got):,} classified of {len(want):,} expected; {len(miss)} missing/extra, "
          f"{len(wrong)} wrong; current RL buckets {cur}")

    # numeric-key trap: a double spine key must still match a string master key
    num_master = master.withColumn(
        "account_id", F.regexp_replace("account_id", "L", "").cast("long").cast("string"))
    num_spine = spark.createDataFrame([(float(a[1:]),) for a in list(rl_expected)[:100]], "account_id double")
    matched = build_rl_full_history(num_spine, num_master).select("account_id").distinct().count()
    print(f"RL double spine key -> string master key: {matched}/100 matched")
    bad += 100 - matched

    spark.stop()
    print(f"{'SPARK E2E PASSED' if not bad else f'SPARK E2E FAILED ({bad})'} in {time.time() - t0:.0f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 4000))
