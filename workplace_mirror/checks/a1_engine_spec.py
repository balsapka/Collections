"""Local spec test for the A1 engine (``a1_ability``) against specs/A1_ability_spec.md.

    python workplace_mirror/checks/a1_engine_spec.py      (needs pyspark + Java 17)

Each case is one customer at one observation date, built from source-shaped rows that go
through the real primary and feature builders, with the level / state the spec
prescribes. Prints a table and exits non-zero on a mismatch.
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

from enbd_collections.nodes.features.bureau import (  # noqa: E402
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)
from enbd_collections.nodes.features.casa import feat_cif_casa as fc  # noqa: E402
from enbd_collections.nodes.primary.casa import prm_casa  # noqa: E402
from enbd_collections.pipelines.crx_persona import _common  # noqa: E402
from enbd_collections.pipelines.crx_persona.a1_ability import (  # noqa: E402
    build_a1_ability,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
    build_liquidity_signals,
)
from enbd_collections.pipelines.crx_persona.cc_a1_ability.nodes import (  # noqa: E402
    build_cc_liquidity_anchor,
)
from enbd_collections.pipelines.crx_persona.rl_a1_ability.nodes import (  # noqa: E402
    build_rl_liquidity_anchor,
)

OBS = date(2026, 7, 31)  # m1 = Jul, m2 = Jun, m3 = May; prior = Apr, Mar, Feb
PERSONA = {"persona_start_date": "2026-07-01", "persona_end_date": "2026-07-31"}


def m(k, day=20):
    """A date in month m_k (m1 = the observation month, m0 = the month after)."""
    y, mo = OBS.year, OBS.month - k + 1
    while mo <= 0:
        mo, y = mo + 12, y - 1
    return date(y, mo, day)


def week(d):
    """WM ``week_number``: yyyyMM0W, week 01-04 of the month."""
    return int(f"{d:%Y%m}0{min((d.day - 1) // 7 + 1, 4)}")


LEG = {  # active= : (tran_type, reason, code, narration)
    "economic": ("INWARD REMITTANCE", None, "101", "SALARY FROM X"),
    "card": ("POS TRANSACTIONS", None, "447", "POS"),
    "own_loan": ("MISCELLANEOUS", None, None, "INSTL_RECOVERY-PL-AC 123"),
    "wash": ("INTERNAL TRANSFER - SELF", "INTERNAL TRANSFER - SELF", "458", "OWN"),
    "fee": ("CHARGES", "CHARGES", "418", "VAT"),
    "dds": ("OUTWARD REMITTANCE", "DDS Rejects/Reversal", "445", "DDR-1"),
}
rows = {
    k: []
    for k in "spine wmsal bal casa flow txn bene alert ret ftr dcore agr".split()
}
expect = {}


def case(name, *, salary=(), bureau=(), casa=(), payments=(), bounces=(), active="economic",
         buckets=None, internal=None, eosb=None, model="cc_60_180", **want):
    """salary: [(k, amount)]; bureau: [(k, amount[, alert type[, pull day]])]; casa:
    [(k, balance)]; payments: [(k, amount)];
    bounces: [(k, bureau bounced amount on that pull)]; active: a CASA leg lane in m2 (None:
    no leg); buckets: overdue_bucket_01..08 on the latest snapshot; eosb: k of a DCORE
    EOSB result."""
    i = len(expect)
    acct, cif = f"A{i}", 1000 + i
    rows["spine"].append((acct, OBS, cif))
    for k, amt in salary:  # a week-2 snapshot of the salary month; days from its 1st
        snap = m(k, 10)
        rows["wmsal"].append((cif, week(snap), float(amt), (snap - m(k, 1)).days))
    for k, amt, *rest in bureau:
        alert_type = rest[0] if rest else 31
        day = rest[1] if len(rest) > 1 else 5
        rows["alert"].append((cif, "CC", "SALARY", m(k, day), 0.0, alert_type, float(amt)))
    for k, bal in casa:
        rows["casa"].append((cif, week(m(k, 22)), float(bal)))
    for k, amt in payments:
        rows["bene"].append((f"CARD{i}", "CARD_NUMBER", "OTHER BANK"))
        rows["txn"].append((cif, "outflow", "CASA", m(k), float(amt), f"CARD{i}"))
    for k, amt in bounces:
        rows["alert"].append((cif, "CC", "BOUNCED CHEQUE", m(k, 5), float(amt), 99, None))
    if internal is not None:  # (k, reason_for_excluding)
        k, reason = internal
        rows["ret"].append((cif, f"T{i}", m(k), reason))
    if active is not None:
        t, reason, code, narration = LEG[active]
        rows["ftr"].append((cif, m(2), "D", t, reason, code, narration, 100.0))
        rows["flow"].append((cif, week(m(2, 8)), 100.0, 0.0))
    if eosb is not None:
        rows["agr"].append((acct, f"AG{i}", str(cif)))
        rows["dcore"].append((f"AG{i}", m(eosb), "EXPECTING EOSB"))
    b = buckets or [0.0] * 8
    rows["bal"].append((acct, OBS - timedelta(days=5), *[float(x) for x in b]))
    expect[acct] = (name, want, model)


# ── Income (spec S2–S6, S12 window total) ──
case("stable: window total >= 2 x 3000", salary=[(1, 5000), (2, 5000)], income="stable")
case("weak: window total < 2 x 3000", salary=[(1, 4000), (3, 1200)], income="weak")
case("weak: below the total, >= 1000", salary=[(1, 1500), (2, 1500), (3, 1500)], income="weak")
case("S12: three months of 2000 reach 2 floors", salary=[(1, 2000), (2, 2000), (3, 2000)],
     income="stable")
case("S12: early pay — two salaries in m2, none in m1", salary=[(2, 10000)], income="stable")
case("none: < 1000", salary=[(1, 800)], income="none")
case("stable needs 2 x (2 x anchor): overdue 3000 -> 12000", salary=[(1, 5000), (2, 5000)],
     buckets=[500, 1000, 3000, 0, 0, 0, 0, 0], income="weak")
case("weakening > 25% breaks stable", salary=[(1, 4000), (2, 4000), (3, 4000), (4, 9000), (5, 9000), (6, 9000)],
     income="weak")
case("bureau salary counts", bureau=[(1, 4000), (2, 4000)], income="stable")
case("salary after the observation month ignored", salary=[(0, 9000), (1, 4000)], income="weak")
case("bureau older than W + the carry ignored", bureau=[(5, 9000), (6, 9000)], income="none")
# AECB salary (S14): the pull's month and the next, never before the pull
case("AECB: pull in the first month of W gives 2 months", bureau=[(3, 3000)], income="stable",
     source="bureau")
case("AECB: pull in the middle month gives 2 months", bureau=[(2, 3000)], income="stable")
case("AECB: pull in the observation month gives 1 month", bureau=[(1, 3000)], income="weak")
case("AECB: one month of 6000 reaches the total", bureau=[(1, 6000)], income="stable")
case("AECB: a pull before W carries into W", bureau=[(4, 3000)], income="weak")
case("AECB: pulls every 2 months fill W", bureau=[(3, 2000), (1, 2000)], income="stable")
case("AECB: the carry goes 1 month only", bureau=[(4, 9000)], income="stable")
case("AECB: the month's latest pull wins, not the sum", bureau=[(2, 9000, 31, 5), (2, 2000, 31, 25)],
     income="weak")
case("AECB: type 32 counts", bureau=[(3, 3000, 32)], income="stable")
case("AECB: other alert types do not count", bureau=[(3, 9000, 77)], income="none")
case("AECB: a closure ends the carry", bureau=[(3, 3000), (2, 0, 43)], income="weak")
case("AECB: a closure on the same pull wins", bureau=[(2, 9000), (2, 0, 43)], income="none")
case("AECB + internal: the larger per month, not the sum", salary=[(2, 2000)], bureau=[(2, 2500)],
     income="weak", source="both")
case("internal salary stopped, one AECB pull at the same level -> Weak",
     salary=[(4, 10000), (5, 10000), (6, 10000)], bureau=[(2, 10000)], income="weak",
     source="bureau", stopped=1)
case("AECB in W with internal salary in W: not stopped",
     salary=[(1, 5000), (2, 5000), (4, 5000)], income="stable", source="internal", stopped=0)
# ── Liquidity (S7, S8) ──
case("casa adequate 2 of 3 >= 3000", casa=[(1, 3500), (2, 3500), (3, 100)], liquidity="adequate")
case("casa drop > 50% -> not adequate", casa=[(1, 3500), (2, 3500), (3, 3500), (4, 9000), (5, 9000), (6, 9000)],
     liquidity="weak")
case("single payment >= 500 adequate", payments=[(2, 600)], liquidity="adequate")
case("payments summed do not count", payments=[(1, 300), (2, 300)], liquidity="none")
case("payment must cover the anchor", payments=[(2, 600)], buckets=[100, 2000, 0, 0, 0, 0, 0, 0],
     liquidity="none")
case("casa >= 1000 once -> weak", casa=[(2, 1500)], liquidity="weak")
# ── Anchor (S1) ──
case("anchor = oldest bucket in OVD_01..06", buckets=[100, 200, 300, 400, 0, 0, 0, 0], anchor=400.0)
case("OVD_07/08 never anchor", buckets=[100, 0, 0, 0, 0, 0, 7000, 9000], anchor=100.0)
case("no overdue -> flat floors", buckets=[0] * 8, anchor=None)
# ── State map ──
case("High", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)], state="high")
case("High + bureau bounce -> Moderate", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     bounces=[(2, 500)], state="moderate")
case("Stable + None -> Moderate", salary=[(1, 5000), (2, 5000)], state="moderate")
case("Stable + Weak + bounce -> Low", salary=[(1, 5000), (2, 5000)], casa=[(1, 1500)], bounces=[(1, 500)],
     state="low")
case("Weak + None -> Low", salary=[(1, 1500)], state="low")
case("High + internal cheque return -> Moderate", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], internal=(2, "CHEQUE RETURNS"), state="moderate")
case("internal DDS return counts", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     internal=(1, "DDS Rejects/Reversal"), state="moderate")
case("RETURNS (POS refunds) ignored", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     internal=(1, "RETURNS"), state="high")
case("bounce older than 3 months ignored", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     bounces=[(4, 500)], state="high")
case("bureau bounce repeated unchanged -> not new", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(4, 500), (2, 500)], state="high")
case("bureau bounce amount changed -> new", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(4, 500), (2, 900)], state="moderate")
case("EOSB result is a diagnostic only", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     eosb=2, state="high", eosb_flag=1)
# ── Activity gate (S11) ──
case("0 points, a third-party credit -> Low", active="economic", state="low")
case("0 points, card spend -> Low", active="card", state="low")
case("0 points, only own-loan recovery -> Unknown (dormant)", active="own_loan", state="unknown",
     reason="dormant_casa")
case("0 points, only own-account transfers -> Unknown (dormant)", active="wash", state="unknown",
     reason="dormant_casa")
case("0 points, only fees, small balance -> Unknown (dormant)", active="fee", casa=[(8, 200)],
     state="unknown", reason="dormant_casa")
case("0 points, no CASA leg, zero balance -> Unknown (no CASA)", active=None, casa=[(2, 0)],
     state="unknown", reason="no_casa")
case("0 points, only a DDS reject -> distress -> Low", active="dds", internal=(2, "DDS Rejects/Reversal"),
     state="low")
# ── 180+: 6-month window, 3 floors, no anchor ──
P180 = dict(model="cc_180_plus")
case("180+: stable, 15000 >= 3 x 3000", salary=[(1, 5000), (4, 5000), (6, 5000)], income="stable", **P180)
case("180+: 8000 < 9000 is weak", salary=[(1, 4000), (5, 4000)], income="weak", **P180)
case("180+: weakening vs the prior 6", salary=[(k, 4000) for k in range(1, 7)] + [(k, 9000) for k in range(7, 13)],
     income="weak", **P180)
case("180+: casa adequate 3 of 6", casa=[(2, 3500), (4, 3500), (6, 3500)], liquidity="adequate", **P180)
case("180+: bounce in month 5 counts", salary=[(1, 5000), (2, 5000), (3, 5000)], bounces=[(5, 500)],
     state="low", **P180)
case("180+: overdue buckets give no anchor", buckets=[100, 200, 0, 0, 0, 0, 0, 0], anchor=None, **P180)

df = spark.createDataFrame
# a return of another CIF in the 180+ window's first month: the returns feature starts
# early enough (build_distress_signals checks it)
COVER = [(-1, "TC", m(6), "CHARGES")]
ret_schema = "cif_id long, tran_id string, tran_date date, reason_for_excluding string"
ftr_schema = ("cif_id long, tran_date date, tran_dc string, tran_type string, reason_for_excluding string,"
              " tran_particular_code string, tran_narration_1 string, actual_tran_amt_aed double")

internal_salary = fc.build_internal_salary(df(
    rows["wmsal"], "cif_id long, week_number int, ft_last_salary_amount double, ft_days_since_salary_transaction int"))
alert_schema = ("cif_id long, contract_type string, alert_description string, extract_date date,"
                " bounced_cheque_amount double, alert_type_number int, salary_credit_amount double")
bureau_salary = feat_cif_bureau_salary_monthly.build(df(rows["alert"], alert_schema))
casa_balance = fc.build_casa_balance(
    df(rows["casa"], "cif_id long, week_number int, ft_avg_casa_eod_balance_in_last_0_3_weeks_avg double"),
    df(rows["flow"], "cif_id long, week_number int, ft_inflow_casa_amt_in_last_0_0_weeks_sum double,"
                     " ft_outflow_casa_amt_in_last_0_0_weeks_sum double"),
    PERSONA["persona_start_date"], 12,
)
payments = fc.build_ext_card_payments(
    df(rows["txn"], "cif_id long, in_out_flow string, product_category string, tran_date date, tran_amt double,"
                    " transaction_acid string"),
    prm_casa.build_beneficiary_cards(
        df(rows["bene"], "instrument_number string, instrument_type string, institution_name string")),
    PERSONA["persona_start_date"], 12,
)
activity = fc.build_casa_activity(df(rows["ftr"], ftr_schema))
returns = fc.build_returns(df(rows["ret"] + COVER, ret_schema))
bounces = feat_cif_bureau_bounces_monthly.build(df(rows["alert"], alert_schema))
followup = df(rows["dcore"], "agreement_id string, action_ts date, result_name string")
agreements = df(rows["agr"], "account_id string, agreement_id string, cif_id string")

spine_schema = "contract_id string, observation_date date, cif_id long"
obs = _common.build_cc_obs_base(df(rows["spine"], spine_schema), PERSONA)
bcols = ", ".join(f"overdue_bucket_{i:02d} double" for i in range(1, 9))
balance = df(rows["bal"], f"contract_id string, observation_date date, {bcols}")


def run(model_id):
    o = obs.filter(F.col("account_id").isin([a for a, e in expect.items() if e[2] == model_id]))
    return build_a1_ability(
        o,
        build_income_signals(o, internal_salary, bureau_salary, model_id),
        build_liquidity_signals(o, casa_balance, payments, activity, model_id),
        build_distress_signals(o, returns, bounces, model_id),
        build_eosb_signals(o, followup, agreements, model_id),
        build_cc_liquidity_anchor(o, balance, model_id),
        model_id,
        PERSONA["persona_end_date"],
    ).collect()


got = {r["account_id"]: r for r in run("cc_60_180") + run("cc_180_plus")}
fails = 0
for acct, (name, want, _) in expect.items():
    r = got[acct]
    actual = {"income": r["a1_income_level"], "liquidity": r["a1_liquidity_level"],
              "state": r["a1_state"], "anchor": r["liquidity_anchor_amt"],
              "reason": r["a1_unknown_reason"], "eosb_flag": r["a1_eosb_flag"],
              "source": r["a1_income_source"], "stopped": r["a1_salary_stopped"]}
    ok = all(actual[k] == v for k, v in want.items())
    fails += not ok
    print(f"{'ok  ' if ok else 'FAIL'} {name:<58} want={want} got={ {k: actual[k] for k in want} }")

# salary month: a week-1 snapshot of the next month dates the credit to the right month
# (the earlier engine parsed yyyyMM0W as a date and put every salary a month early)
snap = m(0, 3)
probe = fc.build_internal_salary(df([(1, week(snap), 5000.0, (snap - m(1, 1)).days)],
                                    "cif_id long, week_number int, ft_last_salary_amount double,"
                                    " ft_days_since_salary_transaction int")).first()
assert probe["month_end"] == date(2026, 7, 31), probe
# the lanes of the FTR reference: card payments survive the SELF reason, DDS beats SELF
lanes = {r["lane"] for r in fc.build_casa_activity(df(
    [(1, m(1), "D", "CREDIT CARD PAYMENTS", "INTERNAL TRANSFER - SELF", "405", "CC", 1.0),
     (2, m(1), "D", "INTERNAL TRANSFER - SELF", "DDS Rejects/Reversal", "445", "DDR", 1.0),
     (3, m(1), "C", "POS TRANSACTIONS", "RETURNS", "948", "REF", 1.0),
     (4, m(1), "C", "INWARD REMITTANCE", "SUBSIDIARIES EXCLUSION", "101", "X", 1.0)],
    ftr_schema)).collect()}
assert lanes == {"card_payment", "signal", "refund", "group_internal"}, lanes
# 180+ has no anchor; a balance snapshot from before the observation month gives none
assert build_cc_liquidity_anchor(obs, balance, "cc_180_plus").filter(
    F.col("liquidity_anchor_amt").isNotNull()).count() == 0
stale = df([("A0", date(2026, 6, 30), *[100.0] * 8)], f"contract_id string, observation_date date, {bcols}")
assert build_cc_liquidity_anchor(obs, stale, "cc_60_180").count() == 0
# the debit and credit legs of one return count once
legs = df([(1, "T", m(1), "CHEQUE RETURNS")] * 2 + COVER, ret_schema)
assert fc.build_returns(legs).filter(F.col("cif_id") == "1").first()["events"] == 1
# a returns feature that starts after the first observation window stops the run
try:
    build_distress_signals(obs, fc.build_returns(df(rows["ret"], ret_schema)), bounces, "cc_180_plus")
    raise AssertionError("returns coverage guard did not fire")
except ValueError as e:
    assert "persona_start_date" in str(e)
# RL anchor: one EMI on the observation month's int_loan_master snapshot
loan_schema = "account_id string, observation_date date, installment_due_amount double"
emi = {r["account_id"]: r["liquidity_anchor_amt"] for r in build_rl_liquidity_anchor(
    obs, df([("A0", OBS, 2000.0), ("A1", OBS, 0.0), ("A2", date(2026, 6, 30), 1500.0)],
            loan_schema)).collect()}
assert emi == {"A0": 2000.0, "A1": None}, emi  # 0 EMI → no anchor; a June snapshot is stale
# RL: the loan's latest-pull bureau salary is income in its pull month and the next, PIT
frl_schema = "account_id string, observation_date date, aecb_bureau_pull_date date, aecb_last_salary_credit_amount double"
frl = df([("A0", OBS, m(2, 10), 6000.0), ("A1", OBS, m(0, 5), 7000.0)], frl_schema)
inc = {r["account_id"]: r for r in build_income_signals(
    obs.filter(F.col("account_id").isin("A0", "A1")), internal_salary, bureau_salary, "cc_60_180",
    loan_features=frl,
).collect()}
assert inc["A0"]["income_m2"] == 6000.0 == inc["A0"]["income_m1"], inc["A0"]
assert inc["A0"]["income_m3"] is None and inc["A0"]["bureau_salary_w"] == 6000.0, inc["A0"]
# a pull after the observation month never counts
assert 7000.0 not in [inc["A1"][f"income_m{i}"] for i in range(1, 7)], inc["A1"]
print(f"\n{len(expect) - fails}/{len(expect)} cases pass (+ dating, lanes, anchor, returns and loan salary checks)")
sys.exit(1 if fails else 0)
