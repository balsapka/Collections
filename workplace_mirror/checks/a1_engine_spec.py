"""Local spec test for the A1 engine (``_a1``) against specs/A1_ability_spec.md.

    python workplace_mirror/checks/a1_engine_spec.py      (needs pyspark + Java 17)

Each case is one customer at one observation date, built from raw-shaped source rows, with
the level / state the workbook prescribes. Prints a table and exits non-zero on a mismatch.
"""

import os
import pathlib
import sys
from datetime import date, timedelta

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path.insert(0, str(HERE.parent / "src"))

from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

from enbd_collections.pipelines.crx_persona import _common  # noqa: E402
from enbd_collections.pipelines.crx_persona._a1 import (  # noqa: E402
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)
from enbd_collections.pipelines.crx_persona.cc_a1_ability_v2.nodes import (  # noqa: E402
    build_cc_liquidity_anchor,
)

OBS = date(2026, 7, 15)  # m1 = Jun, m2 = May, m3 = Apr; prior = Mar, Feb, Jan


def m(k, day=20):
    """A date in month m_k before OBS."""
    y, mo = OBS.year, OBS.month - k
    while mo <= 0:
        mo, y = mo + 12, y - 1
    return date(y, mo, day)


def yyyymmdd(d):
    return int(d.strftime("%Y%m%d"))


rows = {k: [] for k in "spine contract client wmsal salhist bridge bal casa flow txn bene alert".split()}
expect = {}


def case(name, *, salary=(), bureau=(), casa=(), payments=(), bounce=None, active=True,
         buckets=None, **want):
    """salary / bureau: [(k, amount)]; casa: [(k, balance)]; payments: [(k, amount)];
    buckets: overdue_bucket_01..08 on the latest snapshot."""
    i = len(expect)
    acct, cif = f"A{i}", 1000 + i
    rows["spine"].append((acct, OBS))
    rows["contract"].append((acct, f"C{i}"))
    rows["client"].append((f"C{i}", cif))
    for k, amt in salary:  # one weekly snapshot a few days after each credit
        credit = m(k, 25)
        snap = credit + timedelta(days=3)
        rows["wmsal"].append((cif, yyyymmdd(snap), float(amt), 3))
    for k, amt in bureau:
        rows["bridge"].append((f"F{i}", cif))
        rows["salhist"].append((f"F{i}", m(k).strftime("%m%Y"), float(amt)))
    for k, bal in casa:
        rows["casa"].append((cif, yyyymmdd(m(k, 22)), float(bal)))
    for k, amt in payments:
        rows["bene"].append((f"CARD{i}", "CARD_NUMBER"))
        rows["txn"].append((cif, "outflow", "CASA", m(k), float(amt), f"CARD{i}"))
    if bounce is not None:
        rows["alert"].append((cif, m(bounce), 500.0))
    if active:
        rows["flow"].append((cif, yyyymmdd(m(1, 8)), 100.0, 0.0))
    b = buckets or [0.0] * 8
    rows["bal"].append((acct, OBS - timedelta(days=5), *[float(x) for x in b]))
    expect[acct] = (name, want)


A = [0, 0, 0, 0, 0, 0, 0, 0]
# ── Income (workbook rows 14-16) ──
case("stable: salary 2 of 3 >= 3000", salary=[(1, 5000), (2, 5000)], income="stable")
case("weak: only 1 month >= 3000", salary=[(1, 5000), (3, 1200)], income="weak")
case("weak: below 3000, >= 1000", salary=[(1, 2000), (2, 2000), (3, 2000)], income="weak")
case("none: < 1000", salary=[(1, 800)], income="none")
case("stable needs 2x anchor: 2 x 3000 overdue = 6000", salary=[(1, 5000), (2, 5000)],
     buckets=[500, 1000, 3000, 0, 0, 0, 0, 0], income="weak")
case("weakening > 25% breaks stable", salary=[(1, 4000), (2, 4000), (3, 4000), (4, 9000), (5, 9000), (6, 9000)],
     income="weak")
case("bureau salary counts", bureau=[(1, 4000), (2, 4000)], income="stable")
case("bureau older than 3 months ignored", bureau=[(4, 4000), (5, 4000)], income="none")
# ── Liquidity (rows 17-19) ──
case("casa adequate 2 of 3 >= 3000", casa=[(1, 3500), (2, 3500), (3, 100)], liquidity="adequate")
case("casa drop > 50% -> not adequate", casa=[(1, 3500), (2, 3500), (3, 3500), (4, 9000), (5, 9000), (6, 9000)],
     liquidity="weak")
case("single payment >= 500 adequate", payments=[(2, 600)], liquidity="adequate")
case("payments summed do not count", payments=[(1, 300), (2, 300)], liquidity="none")
case("payment must cover the anchor", payments=[(2, 600)], buckets=[100, 2000, 0, 0, 0, 0, 0, 0],
     liquidity="none")
case("casa >= 1000 once -> weak", casa=[(2, 1500)], liquidity="weak")
# ── Anchor ──
case("anchor = oldest bucket in OVD_01..06", buckets=[100, 200, 300, 400, 0, 0, 0, 0], anchor=400.0)
case("OVD_07/08 never anchor", buckets=[100, 0, 0, 0, 0, 0, 7000, 9000], anchor=100.0)
case("no overdue -> flat floors", buckets=[0] * 8, anchor=None)
# ── State map (section 3) ──
case("High", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)], state="ability_high")
case("High + bounce -> Moderate", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)], bounce=2,
     state="ability_moderate")
case("Stable + None -> Moderate", salary=[(1, 5000), (2, 5000)], state="ability_moderate")
case("Stable + Weak + bounce -> Limited", salary=[(1, 5000), (2, 5000)], casa=[(1, 1500)], bounce=1,
     state="ability_low")
case("Weak + None -> Limited", salary=[(1, 1500)], state="ability_low")
case("None + None, CASA active -> Limited", active=True, state="ability_low")
case("None + None, no CASA activity -> Unknown", active=False, state="ability_unknown")
case("bounce older than 3 months ignored", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     bounce=4, state="ability_high")

df = spark.createDataFrame
obs = _common.build_cc_obs_base(
    df(rows["spine"], "contract_id string, observation_date date"),
    df(rows["contract"], "contract_id string, client_id string"),
    df(rows["client"], "client_id string, cif_id long"),
)
bcols = ", ".join(f"overdue_bucket_{i:02d} double" for i in range(1, 9))
out = build_a1_ability(
    obs,
    build_income_signals(
        obs,
        df(rows["wmsal"], "cif_id long, week_number int, ft_last_salary_amount double, ft_days_since_salary_transaction int"),
        df(rows["salhist"] or [("X", "012000", 0.0)], "subj_salcr_hist_hdr_file_id string, subj_salcr_hist_ref_mnth string, subj_salcr_hist_tot_sal_amt double"),
        df(rows["bridge"] or [("Y", 0)], "bureau_file_id string, cif_id long"),
    ),
    build_liquidity_signals(
        obs,
        df(rows["casa"], "cif_id long, week_number int, ft_avg_casa_eod_balance_in_last_0_3_weeks_avg double"),
        df(rows["flow"], "cif_id long, week_number int, ft_inflow_casa_amt_in_last_0_0_weeks_sum double, ft_outflow_casa_amt_in_last_0_0_weeks_sum double"),
        df(rows["txn"], "cif_id long, in_out_flow string, product_category string, tran_date date, tran_amt double, transaction_acid string"),
        df(rows["bene"], "instrument_number string, instrument_type string"),
    ),
    build_distress_signals(obs, df(rows["alert"], "cif_id long, extract_date date, bounced_cheque_amount double")),
    build_cc_liquidity_anchor(obs, df(rows["bal"], f"contract_id string, observation_date date, {bcols}"), "cc_60_180"),
).collect()

got = {r["account_id"]: r for r in out}
fails = 0
for acct, (name, want) in expect.items():
    r = got[acct]
    actual = {"income": r["a1_income_level"], "liquidity": r["a1_liquidity_level"],
              "state": r["a1_state"], "anchor": r["liquidity_anchor_amt"]}
    ok = all(actual[k] == v for k, v in want.items())
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name:<50} want={want} got={ {k: actual[k] for k in want} }")

# 180+ has no anchor
assert build_cc_liquidity_anchor(obs, df(rows["bal"], f"contract_id string, observation_date date, {bcols}"),
                                 "cc_180_plus").filter(F.col("liquidity_anchor_amt").isNotNull()).count() == 0
print(f"\n{len(expect) - fails}/{len(expect)} cases pass")
sys.exit(1 if fails else 0)
