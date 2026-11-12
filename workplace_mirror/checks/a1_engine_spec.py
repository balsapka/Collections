"""Local spec test for the A1 engine (``a1_ability``) against specs/A1_ability_family_rule.md
(income: specs/A1_ability_spec.md).

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
    build_casa_signals,
    build_cross_product_signals,
    build_income_signals,
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


LEG = {  # active= / flows kind: (tran_type, reason, code, narration)
    "economic": ("INWARD REMITTANCE", None, "101", "TRANSFER FROM X"),
    "cash": ("CASH DEPOSIT", None, "102", "CASH"),
    "remit_out": ("OUTWARD REMITTANCE", None, "120", "TO OTHER BANK"),
    "chq_rtn": ("MISCELLANEOUS", None, None, "CHQ RTN INSUFFICIENT 123"),
    "misc": ("MISCELLANEOUS", None, None, "ADJUSTMENT"),
    "card": ("POS TRANSACTIONS", None, "447", "POS"),
    "own_loan": ("MISCELLANEOUS", None, None, "INSTL_RECOVERY-PL-AC 123"),
    "wash": ("INTERNAL TRANSFER - SELF", "INTERNAL TRANSFER - SELF", "458", "OWN"),
    "fee": ("CHARGES", "CHARGES", "418", "VAT"),
    "dds": ("OUTWARD REMITTANCE", "DDS Rejects/Reversal", "445", "DDR-1"),
}
rows = {
    k: []
    for k in "spine wmsal bal casa flow alert unified ret ftr lab prod dcore agr".split()
}
expect = {}


def case(name, *, salary=(), bureau=(), casa=(), flows=(), products=(), bounces=(),
         active="economic", on_loan=False, buckets=None, internal=None, eosb=None,
         model="cc_60_180", **want):
    """salary: [(k, amount)]; bureau: [(k, amount[, unified salary_source[, day]])]; casa:
    [(k, balance)]; flows: [(k, "C"/"D", LEG kind, amount[, day[, wm label]])] where the
    label is "salary" or "self"; products: [(type, balance, is_current, instalment[,
    own account])];
    bounces: [(k, bureau bounced amount on that pull[, k of its return date, None: none])]; active: a CASA leg lane in m2 (None:
    no leg); on_loan: that leg is on the loan account, not a CASA; buckets: overdue_bucket_01..08 on the latest snapshot; eosb: k of a DCORE
    EOSB result."""
    i = len(expect)
    acct, cif = f"A{i}", 1000 + i
    rows["spine"].append((acct, OBS, cif))
    for k, amt in salary:  # a week-2 snapshot of the salary month; days from its 1st
        snap = m(k, 10)
        rows["wmsal"].append((cif, week(snap), float(amt), (snap - m(k, 1)).days))
    for k, amt, *rest in bureau:  # a feat_bureau_salary_unified row
        source = rest[0] if rest else "alert"
        day = rest[1] if len(rest) > 1 else 28
        rows["unified"].append((cif, m(k, day), float(amt), source))
    for k, bal in casa:
        rows["casa"].append((cif, week(m(k, 22)), float(bal)))
    for j, (k, dc, kind, amt, *rest) in enumerate(flows):
        day = rest[0] if rest else 20
        t, reason, code, narration = LEG[kind]
        tid = f"F{i}_{j}"
        rows["ftr"].append((cif, f"CASA{cif}", tid, m(k, day), dc, t, reason, code, narration,
                            float(amt)))
        if len(rest) > 1:
            label = rest[1]
            rows["lab"].append((cif, tid, m(k, day), "inflow" if dc == "C" else "outflow",
                                int(label == "salary"), int(label == "self"), 0, 0, 0, 0, 0))
    for ptype, bal, current, inst, *own in products:
        pacct = acct if own and own[0] else f"P{i}_{ptype}"
        rows["prod"].append((str(cif), OBS, pacct, ptype, bal, current, inst))
    for k, amt, *ret in bounces:
        back = ret[0] if ret else k  # the return date's month (None: no return date)
        returned = None if back is None else m(back, 3)
        rows["alert"].append((cif, "CC", "BOUNCED CHEQUE", m(k, 5), float(amt), 99, None, returned))
    if internal is not None:  # (k, reason_for_excluding)
        k, reason = internal
        rows["ret"].append((cif, f"CASA{cif}", f"T{i}", m(k), reason))
    if active is not None:
        t, reason, code, narration = LEG[active]
        account = f"LOAN{cif}" if on_loan else f"CASA{cif}"
        rows["ftr"].append((cif, account, f"A{i}", m(2), "D", t, reason, code, narration, 100.0))
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
case("AECB: a bulk-pull month counts like an alert", bureau=[(3, 3000, "bureau_salary")],
     income="stable")
case("AECB: a mid-month date counts in its month", bureau=[(3, 3000, "salary_credit", 10)],
     income="stable")
case("AECB level check: fewer alerts at the same level -> Stable",
     bureau=[(6, 7000), (4, 7000), (1, 7000)], income="stable")
case("AECB level check: a real fall -> Weak", bureau=[(6, 8000), (4, 8000), (2, 3500)],
     income="weak")
case("AECB level check: a fall within 25% -> Stable", bureau=[(6, 8000), (4, 8000), (2, 6500)],
     income="stable")
case("level check off: internal salary in the prior window", salary=[(4, 7000), (5, 7000), (6, 7000)],
     bureau=[(1, 7000)], income="weak", stopped=1)
case("level check off: internal salary in the window", salary=[(1, 1000)],
     bureau=[(6, 7000), (4, 7000), (1, 7000)], income="weak")
case("level check: internal under AED 1,000 does not count", salary=[(1, 800)],
     bureau=[(6, 7000), (4, 7000), (1, 7000)], income="stable")
case("AECB: a 0 row ends the carry", bureau=[(3, 3000), (2, 0)], income="weak")
case("AECB + internal: the larger per month, not the sum", salary=[(2, 2000)], bureau=[(2, 2500)],
     income="weak", source="both")
case("internal salary stopped, one AECB pull at the same level -> Weak",
     salary=[(4, 10000), (5, 10000), (6, 10000)], bureau=[(2, 10000)], income="weak",
     source="bureau", stopped=1)
case("AECB in W with internal salary in W: not stopped",
     salary=[(1, 5000), (2, 5000), (4, 5000)], income="stable", source="internal", stopped=0)
# ── Liquidity (S7, S8) ──
# ── F2 money in or held, F3 money out (family rule §2–§3) ──
case("F2 strong: money in >= 1000 in 2 of 3", flows=[(1, "C", "economic", 1500), (2, "C", "economic", 1500)],
     money_in="strong")
case("F2 some: one month of money in", flows=[(1, "C", "economic", 1500)], money_in="some")
case("F2 strong must cover the anchor", flows=[(1, "C", "economic", 1500), (2, "C", "economic", 1500)],
     buckets=[100, 2000, 0, 0, 0, 0, 0, 0], money_in="some")
case("F2: cash deposits count", flows=[(1, "C", "cash", 2000), (3, "C", "cash", 2000)], money_in="strong")
case("F2: returned-cheque credits never count", flows=[(1, "C", "chq_rtn", 9000), (2, "C", "chq_rtn", 9000)],
     money_in=None)
case("F2: ambiguous MISCELLANEOUS credits never count", flows=[(1, "C", "misc", 9000), (2, "C", "misc", 9000)],
     money_in=None)
case("F2: salary-flagged credits are income, not money in",
     flows=[(1, "C", "economic", 5000, 20, "salary"), (2, "C", "economic", 5000, 20, "salary")], money_in=None)
case("F2: own account at another bank (WM self) counts",
     flows=[(1, "C", "economic", 2000, 20, "self"), (2, "C", "economic", 2000, 20, "self")], money_in="strong")
case("F2: a credit mirrored by a non-evidence debit is netted",
     flows=[(1, "C", "economic", 2000, 10), (1, "D", "misc", 2000, 12), (2, "C", "economic", 2000)],
     money_in="some")
case("F2: a mirror 5 days later is not netted",
     flows=[(1, "C", "economic", 2000, 5), (1, "D", "misc", 2000, 10), (2, "C", "economic", 2000)],
     money_in="strong")
case("F2 strong: CASA balance held 2 of 3 >= 3000", casa=[(1, 3500), (2, 3500), (3, 100)],
     money_in="strong", sweepable=1)
case("F2: balance drop > 50% is not strong", casa=[(1, 3500), (2, 3500), (3, 3500), (4, 9000), (5, 9000), (6, 9000)],
     money_in=None, sweepable=0)
case("F2: a balance below strong is not evidence", active=None, casa=[(2, 1500)], money_in=None,
     state="unknown", reason="dormant_casa")
case("F3 strong: spend >= 1000 in 2 of 3", active=None,
     flows=[(1, "D", "card", 1200), (2, "D", "remit_out", 1200)], money_out="strong")
case("F3 some: one month >= 500", active=None, flows=[(1, "D", "card", 600)], money_out="some")
case("F3: transfers to own accounts elsewhere count", active=None,
     flows=[(1, "D", "remit_out", 3000, 20, "self"), (2, "D", "remit_out", 3000, 20, "self")],
     money_out="strong")
case("F3: own-account transfers with us never count", active=None,
     flows=[(1, "D", "wash", 3000), (2, "D", "wash", 3000)], money_out=None, state="unknown")
# ── F4 cross-product ──
case("F4 strong: deposits >= 10000", products=[("deposit", 12000.0, None, None)], cross_product="strong")
case("F4 some: a small deposit", products=[("deposit", 500.0, None, None)], cross_product="some")
case("F4 strong: a current loan with instalment >= anchor", buckets=[100, 2000, 0, 0, 0, 0, 0, 0],
     products=[("loan", None, 1, 2500.0)], cross_product="strong")
case("F4 some: a current card with a small minimum due", buckets=[100, 2000, 0, 0, 0, 0, 0, 0],
     products=[("card", None, 1, 300.0)], cross_product="some")
case("F4: an overdue loan is not evidence", products=[("loan", None, 0, 5000.0)], cross_product="none")
case("F4: the scored account itself never counts", products=[("card", None, 1, 5000.0, True)],
     cross_product="none")
case("F4: assets must reach 3 x anchor", buckets=[100, 5000, 0, 0, 0, 0, 0, 0],
     products=[("wm", 12000.0, None, None)], cross_product="some")
# ── Anchor (S1) ──
case("anchor = oldest bucket in OVD_01..06", buckets=[100, 200, 300, 400, 0, 0, 0, 0], anchor=400.0)
case("OVD_07/08 never anchor", buckets=[100, 0, 0, 0, 0, 0, 7000, 9000], anchor=100.0)
case("no overdue -> flat floors", buckets=[0] * 8, anchor=None)
# ── State map ──
case("High", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)], state="high")
case("High + bureau bounce -> Moderate", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     bounces=[(2, 500)], state="moderate")
case("one strong family (income) -> Moderate", salary=[(1, 5000), (2, 5000)], state="moderate")
case("one strong family + bounce -> Low", salary=[(1, 5000), (2, 5000)], casa=[(1, 1500)], bounces=[(1, 500)],
     state="low")
case("income weak only -> Low", salary=[(1, 1500)], state="low")
case("High: money out + cross-product", active=None, flows=[(1, "D", "card", 1200), (2, "D", "card", 1200)],
     products=[("deposit", 20000.0, None, None)], state="high", why="money_out")
case("High: money in + money out", flows=[(1, "C", "economic", 1500), (2, "C", "economic", 1500),
     (1, "D", "card", 1200), (2, "D", "card", 1200)], state="high")
case("some levels score nothing: Moderate stays Moderate", salary=[(1, 5000), (2, 5000)],
     flows=[(1, "C", "economic", 1500), (1, "D", "card", 600)], products=[("deposit", 500.0, None, None)],
     state="moderate", why="income")
case("cross-product some alone -> Low (evidence)", active=None, products=[("card", None, 1, 100.0)],
     state="low")
case("High + internal cheque return -> Moderate", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], internal=(2, "CHEQUE RETURNS"), state="moderate")
case("internal DDS return counts", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     internal=(1, "DDS Rejects/Reversal"), state="moderate")
case("RETURNS (POS refunds) ignored", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     internal=(1, "RETURNS"), state="high")
case("bounce older than 3 months ignored", salary=[(1, 5000), (2, 5000)], casa=[(1, 4000), (2, 4000)],
     bounces=[(4, 500)], state="high")
case("bureau bounce repeated in a later pull -> its return date", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(4, 500), (2, 900, 4)], state="high")
case("bureau bounce, same amount, new return date -> counts", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(4, 500), (2, 500)], state="moderate")
case("bureau bounce pulled in W, returned before W -> ignored", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(2, 500, 5)], state="high")
case("bureau bounce without a return date -> not counted", salary=[(1, 5000), (2, 5000)],
     casa=[(1, 4000), (2, 4000)], bounces=[(2, 500, None)], state="high")
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
case("0 points, a leg on the loan account only -> Unknown (no CASA)", active="economic", on_loan=True,
     state="unknown", reason="no_casa")
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
case("180+: balance held 3 of 6", casa=[(2, 3500), (4, 3500), (6, 3500)], money_in="strong", **P180)
case("180+: money in 3 of 6", flows=[(1, "C", "economic", 1000), (3, "C", "economic", 1000),
     (6, "C", "economic", 1000)], money_in="strong", **P180)
case("180+: bounce in month 5 counts", salary=[(1, 5000), (2, 5000), (3, 5000)], bounces=[(5, 500)],
     state="low", **P180)
case("180+: overdue buckets give no anchor", buckets=[100, 200, 0, 0, 0, 0, 0, 0], anchor=None, **P180)

df = spark.createDataFrame
# a return of another CIF in the 180+ window's first month: the returns feature starts
# early enough (build_distress_signals checks it)
COVER = [(-1, "CASA-1", "TC", m(6), "CHARGES")]
ret_schema = "cif_id long, foracid string, tran_id string, tran_date date, reason_for_excluding string"
ftr_schema = ("cif_id long, foracid string, tran_id string, tran_date date, tran_dc string, tran_type string,"
              " reason_for_excluding string,"
              " tran_particular_code string, tran_narration_1 string, actual_tran_amt_aed double")

internal_salary = fc.build_internal_salary(df(
    rows["wmsal"], "cif_id long, week_number int, ft_last_salary_amount double, ft_days_since_salary_transaction int"))
alert_schema = ("cif_id long, contract_type string, alert_description string, extract_date date,"
                " bounced_cheque_amount double, alert_type_number int, salary_credit_amount double,"
                " dt_of_return date")
bureau_salary = feat_cif_bureau_salary_monthly.build(df(
    rows["unified"], "cif_id long, salary_month_end date, monthly_salary double, salary_source string"))
casa_balance = fc.build_casa_balance(
    df(rows["casa"], "cif_id long, week_number int, ft_avg_casa_eod_balance_in_last_0_3_weeks_avg double"),
    df(rows["flow"], "cif_id long, week_number int, ft_inflow_casa_amt_in_last_0_0_weeks_sum double,"
                     " ft_outflow_casa_amt_in_last_0_0_weeks_sum double"),
    PERSONA["persona_start_date"], 12,
)
# every customer has a current account (scheme 101) and a loan account (scheme LAA)
gam = [(c, f"CASA{c}", "101") for c in range(-1, 1000 + len(expect))]
gam += [(c, f"LOAN{c}", "LAA") for c in range(1000, 1000 + len(expect))] + [(1, "CASA1", "101")]
CA, SA = ["101", "110"], ["021"]
accounts = prm_casa.build_casa_accounts(df(gam, "cif_id long, foracid string, schm_code string"), CA, SA)
assert {r["schm_code"] for r in accounts.collect()} == {"101"}  # the loan scheme is not CASA
lab_schema = ("cif_id long, tran_id string, tran_date date, in_out_flow string, salary_txn_flag int,"
              " self_transfer_flag int, fees_charges int, loan_payment_flag int, bank_transfer int,"
              " local_bank_transfer int, international_bank_transfer int")
legs = fc.build_casa_flow_legs(df(rows["ftr"], ftr_schema), accounts, df(rows["lab"], lab_schema),
                               PERSONA["persona_start_date"], 12)
flows = fc.build_casa_flows(legs)
prod_schema = ("cif_id string, month_end date, product_account_id string, product_type string,"
               " balance_aed double, is_current int, instalment_aed double")
products = df(rows["prod"], prod_schema)
returns = fc.build_returns(df(rows["ret"] + COVER, ret_schema), accounts)
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
        build_cc_liquidity_anchor(o, balance, model_id),
        model_id,
        PERSONA["persona_end_date"],
        income=build_income_signals(o, internal_salary, bureau_salary, model_id),
        casa=build_casa_signals(o, casa_balance, flows, model_id, crx_persona=PERSONA),
        cross_product=build_cross_product_signals(o, products),
        distress=build_distress_signals(o, returns, bounces, model_id),
        eosb=build_eosb_signals(o, followup, agreements, model_id),
    ).collect()


got = {r["account_id"]: r for r in run("cc_60_180") + run("cc_180_plus")}
fails = 0
for acct, (name, want, _) in expect.items():
    r = got[acct]
    actual = {"income": r["a1_income_level"], "money_in": r["a1_money_in_level"],
              "money_out": r["a1_money_out_level"], "cross_product": r["a1_cross_product_level"],
              "sweepable": r["a1_sweepable_balance_flag"], "why": r["a1_reason"],
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
    [(1, "CASA1", "L1", m(1), "D", "CREDIT CARD PAYMENTS", "INTERNAL TRANSFER - SELF", "405", "CC", 1.0),
     (1, "CASA1", "L2", m(1), "D", "INTERNAL TRANSFER - SELF", "DDS Rejects/Reversal", "445", "DDR", 1.0),
     (1, "CASA1", "L3", m(1), "C", "POS TRANSACTIONS", "RETURNS", "948", "REF", 1.0),
     (1, "CASA1", "L4", m(1), "C", "INWARD REMITTANCE", "SUBSIDIARIES EXCLUSION", "101", "X", 1.0)],
    ftr_schema), accounts).collect()}
assert lanes == {"card_payment", "signal", "refund", "group_internal"}, lanes
# 180+ has no anchor; a balance snapshot from before the observation month gives none
assert build_cc_liquidity_anchor(obs, balance, "cc_180_plus").filter(
    F.col("liquidity_anchor_amt").isNotNull()).count() == 0
stale = df([("A0", date(2026, 6, 30), *[100.0] * 8)], f"contract_id string, observation_date date, {bcols}")
assert build_cc_liquidity_anchor(obs, stale, "cc_60_180").count() == 0
# the debit and credit legs of one return count once
legs = df([(1, "CASA1", "T", m(1), "CHEQUE RETURNS")] * 2 + COVER, ret_schema)
assert fc.build_returns(legs, accounts).filter(F.col("cif_id") == "1").first()["events"] == 1
# a return on a loan account is not a CASA return
loan_return = df([(1, "LOAN1", "T", m(1), "CHEQUE RETURNS")], ret_schema)
assert fc.build_returns(loan_return, accounts).count() == 0
# a returns feature that starts after the first observation window stops the run
try:
    build_distress_signals(obs, fc.build_returns(df(rows["ret"], ret_schema), accounts), bounces,
                           "cc_180_plus")
    raise AssertionError("returns coverage guard did not fire")
except ValueError as e:
    assert "persona_start_date" in str(e)
# RL anchor: one EMI on the observation month's int_loan_master snapshot
loan_schema = "account_id string, observation_date date, installment_due_amount double"
emi = {r["account_id"]: r["liquidity_anchor_amt"] for r in build_rl_liquidity_anchor(
    obs, df([("A0", OBS, 2000.0), ("A1", OBS, 0.0), ("A2", date(2026, 6, 30), 1500.0)],
            loan_schema)).collect()}
assert emi == {"A0": 2000.0, "A1": None}, emi  # 0 EMI → no anchor; a June snapshot is stale
# Scorecard: each override mode, the High gate, a NULL flag, override order, Unknown
from enbd_collections.pipelines.crx_persona import scoring_engine as se  # noqa: E402

DIMS = (se.Dimension("a", "a_level", {"x": 4, "y": 2}), se.Dimension("b", "b_level", {"x": 2}))
LABELS = {r: r for r in (*se.RUNGS, "unknown")}


def card(*overrides, **gate):
    return se.Scorecard("t", DIMS, LABELS, 4, 2, overrides, **gate)


demote, refuse = se.Override("d", "f1"), se.Override("r", "f2", se.FORCE, "high")
sc_rows = [  # (a_level, b_level, f1, f2, scorecard, state, override, reason)
    ("x", "none", False, False, card(demote), "high", None, "a"),
    ("x", "none", True, False, card(demote), "moderate", "d", "d"),  # DEMOTE
    ("y", "none", True, False, card(demote), "low", "d", "d"),
    ("x", "none", True, False, card(se.Override("c", "f1", se.CAP, "moderate")), "moderate", "c", "c"),
    ("y", "none", True, False, card(se.Override("c", "f1", se.CAP, "moderate")), "moderate", "c", "c"),
    ("none", "none", False, True, card(demote, refuse), "high", "r", "r"),  # FORCE
    ("x", "none", True, True, card(demote, refuse), "moderate", "d", "d"),  # first wins
    ("x", "none", None, False, card(demote), "high", None, "a"),  # NULL flag: no fire
    ("x", "none", False, False, card(high_min_dimensions=2), "moderate", None, "a"),
    ("y", "x", False, False, card(high_min_dimensions=2), "high", None, "a"),  # tie: a first
    ("y", "x", False, False, card(high_current=("b",)), "high", None, "a"),
    ("x", "none", False, False, card(high_current=("b",)), "moderate", None, "a"),
    ("none", None, False, False, card(demote), "unknown", None, None),
    ("none", "none", True, False, card(demote), "low", "d", "d"),
]
sc_df = spark.createDataFrame([r[:4] for r in sc_rows], "a_level string, b_level string, f1 boolean, f2 boolean")
for i, (*_, sc, state, override, reason) in enumerate(sc_rows):
    got = sc.score(sc_df).collect()[i]
    assert (got["t_state"], got["t_override"], got["t_reason"]) == (state, override, reason), (i, got)
try:  # a mistyped override mode raises instead of acting as FORCE
    card(se.Override("m", "f1", "forse", "high")).score(sc_df)
    raise AssertionError("mistyped override mode did not raise")
except KeyError:
    pass
print(f"\n{len(expect) - fails}/{len(expect)} cases pass (+ dating, lanes, anchor, returns and Scorecard checks)")
sys.exit(1 if fails else 0)
