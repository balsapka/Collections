"""Local check for bundle 01: pre-refactor CC A1 v2 vs the shared ``_a1`` engine.

    python workplace_mirror/checks/a1_engine_vs_v2.py      (needs pyspark + Java 17)

Builds synthetic sources with scenario flags (no CIF, stale WM salary, stale balance
snapshots, external card payments early in the window). Rows without a flag must keep
their state; flagged rows may change because of the fixes. Prints the snippet's
old-vs-new crosstab at the end. The old v2 code is read from git (commit 0c45e6e).
"""
import os
import pathlib
import random
import subprocess
import sys
import tempfile
from datetime import date, timedelta

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE.parent / "docs" / "context" / "snippets"))
_old_dir = tempfile.mkdtemp()
pathlib.Path(_old_dir, "old_v2_nodes.py").write_text(
    subprocess.run(
        ["git", "-C", str(HERE), "show",
         "0c45e6e:workplace_mirror/src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py"],
        capture_output=True, text=True, check=True,
    ).stdout
)
sys.path.insert(0, _old_dir)

from pyspark.sql import SparkSession, functions as F  # noqa: E402

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .config("spark.sql.legacy.timeParserPolicy", "LEGACY")  # old code uses "yyyyww"
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

import old_v2_nodes as old  # noqa: E402
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

rnd = random.Random(7)
OBS = [date(2026, 3, 31), date(2026, 5, 31), date(2026, 7, 31)]
PERSONA_START = "2026-01-01"


def ymd(d):
    return int(d.strftime("%Y%m%d"))


def month_ends(end, n):
    out, d = [], end.replace(day=1) - timedelta(days=1)
    for _ in range(n):
        out.append(d)
        d = d.replace(day=1) - timedelta(days=1)
    return out


rows = {k: [] for k in "spine contract client payroll wmsal salhist bridge bal casa flow txn bene alert".split()}
scen = []
for i in range(400):
    acct, cif, client = f"A{i}", 1000 + i, f"C{i}"
    has_cif = rnd.random() > 0.05
    stale_salary = rnd.random() < 0.15  # salary last credited long ago (O36)
    stale_balance = rnd.random() < 0.10  # balance snapshots stopped (O24)
    early_payer = rnd.random() < 0.15  # ext card payments early in the year (O37)
    rows["contract"].append((acct, client))
    if has_cif:
        rows["client"].append((client, cif))
    for obs in OBS:
        rows["spine"].append((acct, obs))
        scen.append((acct, obs, has_cif, stale_salary, stale_balance, early_payer))
    # payroll: monthly flags over the year
    p_rate = rnd.choice([0, 0.3, 0.9])
    for m in month_ends(date(2026, 8, 31), 12):
        rows["payroll"].append((cif, ymd(m), int(rnd.random() < p_rate)))
    # WM salary weekly snapshots
    amt = rnd.choice([None, 800.0, 2500.0, 6000.0])
    if amt:
        wk = date(2025, 9, 1)
        while wk < date(2026, 8, 31):
            ds = 400 + (wk - date(2025, 9, 1)).days if stale_salary else rnd.randint(1, 30)
            rows["wmsal"].append((cif, ymd(wk), amt, ds, 0.0))
            wk += timedelta(days=7)
    # bureau salary
    if rnd.random() < 0.4:
        fid = f"F{i}"
        rows["bridge"].append((fid, cif))
        for m in month_ends(date(2026, 8, 31), rnd.choice([2, 10])):
            rows["salhist"].append((fid, m.strftime("%m%Y"), rnd.choice([2000.0, 5000.0])))
    # balance snapshots with overdue buckets
    last = date(2026, 1, 31) if stale_balance else date(2026, 8, 31)
    for m in month_ends(last + timedelta(days=1), 10):
        b = [rnd.choice([0.0, 0.0, 400.0, 2500.0, 9000.0]) for _ in range(8)]
        rows["bal"].append((acct, m, *b))
    # CASA balance month-ends
    lvl = rnd.choice([None, 500.0, 2000.0, 8000.0])
    if lvl is not None:
        drop = rnd.random() < 0.3
        for m in month_ends(date(2026, 8, 31), 12):
            v = lvl * (0.3 if drop and m > date(2026, 4, 1) else 1.0)
            rows["casa"].append((cif, m, v))
    # CASA weekly flows
    if rnd.random() < 0.6:
        wk = date(2025, 9, 1)
        while wk < date(2026, 8, 31):
            rows["flow"].append((cif, ymd(wk), float(rnd.random() < 0.5) * 100, float(rnd.random() < 0.5) * 50))
            wk += timedelta(days=7)
    # external card payments
    card = f"CARD{i}"
    if early_payer or rnd.random() < 0.2:
        rows["bene"].append((card, "CARD_NUMBER"))
        start = date(2025, 12, 1) if early_payer else date(2026, 1, 15)
        for k in range(rnd.randint(1, 6)):
            d = start + timedelta(days=rnd.randint(0, 220))
            rows["txn"].append((cif, "outflow", "CASA", d, rnd.choice([300.0, 1500.0, 9000.0]), card))
    # bounced cheques
    if rnd.random() < 0.1:
        rows["alert"].append((cif, date(2026, rnd.randint(1, 7), 15), 1200.0))

df = spark.createDataFrame
cc_spine = df(rows["spine"], "contract_id string, observation_date date")
contract = df(rows["contract"], "contract_id string, client_id string")
client = df(rows["client"], "client_id string, cif_id long")
payroll = df(rows["payroll"], "cif_id long, month_number int, payroll_flag int")
wmsal = df(rows["wmsal"], "cif_id long, week_number int, ft_last_salary_amount double, ft_days_since_salary_transaction int, ft_percent_monthly_salary_change double")
salhist = df(rows["salhist"], "subj_salcr_hist_hdr_file_id string, subj_salcr_hist_ref_mnth string, subj_salcr_hist_tot_sal_amt double")
bridge = df(rows["bridge"], "bureau_file_id string, cif_id long")
bcols = ", ".join(f"overdue_bucket_{i:02d} double" for i in range(1, 9))
bal = df(rows["bal"], f"contract_id string, observation_date date, {bcols}")
casa = df(rows["casa"], "cif_id long, month_end_date date, ft_avg_eod_balance_in_last_0_2_months_avg double")
flow = df(rows["flow"], "cif_id long, week_number int, ft_inflow_casa_amt_in_last_0_0_weeks_sum double, ft_outflow_casa_amt_in_last_0_0_weeks_sum double")
txn = df(rows["txn"], "cif_id long, in_out_flow string, product_category string, tran_date date, tran_amt double, transaction_acid string")
bene = df(rows["bene"], "instrument_number string, instrument_type string")
alert = df(rows["alert"], "cif_id long, extract_date date, bounced_cheque_amount double")

# ── old v2 ──
cif_base = old.build_a1v2_cif_base(cc_spine, contract, client)
o_inc = old.build_a1v2_income_signals(cif_base, payroll, wmsal, salhist, bridge)
o_liq = old.build_a1v2_liquidity_signals(cif_base, bal, casa, flow, txn, bene, {"persona_start_date": PERSONA_START})
o_dis = old.build_a1v2_distress_signals(cif_base, alert)
o_out = old.build_a1v2_classify(cif_base, o_inc, o_liq, o_dis).select(
    "account_id", "observation_date", F.col("a1_state_v2").alias("old_state")
)

# ── new engine ──
obs = _common.build_cc_obs_base(cc_spine, contract, client)
n_out = build_a1_ability(
    obs,
    build_income_signals(obs, payroll, wmsal, salhist, bridge),
    build_liquidity_signals(obs, casa, flow, txn, bene),
    build_distress_signals(obs, alert),
    build_cc_liquidity_anchor(obs, bal),
    log_stats=True,
).select("account_id", "observation_date", F.col("a1_state").alias("new_state"))

sc = df(scen, "account_id string, observation_date date, has_cif boolean, stale_salary boolean, stale_balance boolean, early_payer boolean")
cmp = n_out.join(o_out, ["account_id", "observation_date"], "left").join(sc, ["account_id", "observation_date"])
cmp.cache()
total = cmp.count()
changed = cmp.filter(~F.col("new_state").eqNullSafe(F.col("old_state")))
explained = F.col("stale_salary") | F.col("stale_balance") | F.col("early_payer") | ~F.col("has_cif")
unexplained = changed.filter(~explained)
print(f"rows={total}  old_rows={o_out.count()}  changed={changed.count()}  unexplained={unexplained.count()}")
print("changed by scenario:")
changed.groupBy("has_cif", "stale_salary", "stale_balance", "early_payer", "old_state", "new_state").count().orderBy(F.desc("count")).show(40, False)
print("clean rows that changed (must be 0):")
unexplained.show(20, False)
print("no-CIF rows (old: missing, new: present):")
cmp.filter(~F.col("has_cif")).groupBy("old_state", "new_state").count().show()
assert total == cc_spine.count(), "new output must keep every spine row"
assert unexplained.count() == 0, "a row without a fix scenario changed state"


# ── snippet dry run ──
import b01_a1_engine_check as snip
class Cat:
    def __init__(s, d): s.d = d
    def load(s, k): return s.d[k]
    def save(s, k, v): s.d[k] = v.cache(); v.count()
cat = Cat({"params:model_id": "cc_60_180",
           "crx_cc_a1_ability_v2": old.build_a1v2_classify(cif_base, o_inc, o_liq, o_dis)})
snip.main(cat, step="snapshot")
cat.d["crx_cc_a1_ability_v2"] = build_a1_ability(obs, build_income_signals(obs, payroll, wmsal, salhist, bridge), build_liquidity_signals(obs, casa, flow, txn, bene), build_distress_signals(obs, alert), build_cc_liquidity_anchor(obs, bal))
res = snip.main(cat, step="compare", out_dir=tempfile.mkdtemp())
