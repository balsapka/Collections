"""A3 engine spec test: hand-built cases for every rule, and a Kedro run of both products.

    JAVA_HOME=/opt/homebrew/opt/openjdk@17 python workplace_mirror/checks/a3_engine_spec.py

DCORE's helpers are not mirrored; the cancelled-instalment rule is stubbed (status C:
cancelled).
"""

# pylint: disable=wrong-import-position,import-outside-toplevel
import datetime as dt
import sys
import types
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402


def _stub_dcore() -> None:
    def module(name: str) -> types.ModuleType:
        mod = sys.modules.get(name) or types.ModuleType(name)
        mod.__path__ = []
        sys.modules[name] = mod
        return mod

    for name in [
        "enbd_collections.nodes",
        "enbd_collections.nodes.features",
        "enbd_collections.nodes.features.dcore",
        "enbd_collections.nodes.utils",
    ]:
        module(name)
    utils = module("enbd_collections.nodes.features.dcore._feat_dcore_utils")

    def null_cancelled_instalment_fields(df, status):
        cancelled = F.col("instalment_status") == status
        for c in ("due_date", "due_amount", "payment_amount"):
            df = df.withColumn(c, F.when(cancelled, None).otherwise(F.col(c)))
        return df

    utils.null_cancelled_instalment_fields = null_cancelled_instalment_fields
    cfg = module("enbd_collections.nodes.utils.config_dcore")
    cfg.PTP_INSTALMENT_STATUS_CANCELLED = cfg.SETTLEMENT_INSTALMENT_STATUS_CANCELLED = (
        "C"
    )


_stub_dcore()
from enbd_collections.pipelines.crx_persona.a3_credibility import (  # noqa: E402
    build_a3_credibility,
    build_commitment_signals,
    build_contact_signals,
    build_cycle_ledger,
    build_dlq_payment_signals,
    build_instalments,
    build_pre_dlq_payment_signals,
    build_promise_events,
)
from enbd_collections.pipelines.crx_persona.a3_credibility.constants import (  # noqa: E402
    SCORECARD,
)

D = dt.date
OBS = D(2026, 8, 31)
spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.ui.enabled", "false")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.driver.memory", "2g")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
FAILS = []


def check(name: str, got, want) -> None:
    if got != want:
        FAILS.append(f"{name}: got {got!r}, want {want!r}")


def df(rows, schema):
    return spark.createDataFrame(rows, schema)


def episode(rows):
    """(account, episode_start, censored) at OBS."""
    return df(
        [(a, OBS, f"C{a}", s, c) for a, s, c in rows],
        "account_id string, observation_date date, cif_id string, "
        "episode_start date, episode_left_censored boolean",
    )


def by_account(frame, col):
    return {r["account_id"]: r[col] for r in frame.collect()}


# ── 1. The map: Scorecard against the reference rule (72 cells) ───────────────
LEVELS_A = {"kept": 2, "partly_kept": 1, "thin": 0, "broken": -1}
LEVELS_B = {"regular": 2, "some": 1, "none": 0}
LEVELS_C = {"clean": 1, "not_clean": 0, "no_record": 0}


def reference(a, b, c, refusal):
    if (a, b, c, refusal) == ("thin", "none", "no_record", False):
        return "unknown"
    pts = LEVELS_A[a] + LEVELS_B[b] + LEVELS_C[c]
    rungs = ["low", "moderate", "high"]
    rung = 2 if pts >= 4 else 1 if pts >= 2 else 0  # Moderate from 2 (D-A3-24)
    return rungs[max(rung - refusal, 0)]


combos = [
    (a, b, c, r)
    for a in LEVELS_A
    for b in LEVELS_B
    for c in LEVELS_C
    for r in (False, True)
]
cells = df(
    combos,
    "a3_commitments_level string, a3_dlq_payment_level string, "
    "a3_pre_dlq_payment_level string, a3_refusal_flag boolean",
)
for r in SCORECARD.score(cells).collect():
    key = (
        r["a3_commitments_level"],
        r["a3_dlq_payment_level"],
        r["a3_pre_dlq_payment_level"],
        r["a3_refusal_flag"],
    )
    check(f"map {key}", r["a3_state"], f"payment_credibility_{reference(*key)}")

# ── 2. Dimension A: promise events judged by payment, deadlines, window ────────
# CC statements on the 5th; cycle (5th, next 5th], one month's due 100 (A: 300 in the cycle
# from 07-05). A: follow-up promises 06-20 + 06-24 (one run, no plan) paid 120 on 06-30
# by the 07-05 statement -> paid; PTP plan 07-10 + a salary promise on 07-14 (matched),
# 150 paid on 07-20 against 300 -> partial; promise 08-20 not concluded (statement 09-05);
# SOFTPTP is no event; a settlement from 02-01, before the 04-01 episode, is in the window
# (D-A3-26), unpaid -> 3 concluded, 1 kept -> broken; one from 2025-08-01 is outside. B: promise 05-03, paid
# 200 on 05-10, after the 05-05 statement -> none (GRR), paid within 30 days. K: two
# promises, each paid by its statement -> kept. M: plan 06-10 takes the nearer of two
# promise runs (06-14), 06-05 stays alone; neither is paid -> broken (2 concluded, 0
# kept).
# Bk: three promises never paid -> broken (streak).
stmts = [D(2026, m, 5) for m in range(1, 10)]


def fu(rows):
    return df(
        [(a, f"{d} 10:00:00", "OC", "PTP", n) for a, d, n in rows],
        "agreement_id string, action_ts string, action_code string, "
        "result_category string, result_name string",
    ).withColumn("action_ts", F.to_timestamp("action_ts"))


def plan_rows(rows):
    return df(
        [(a, pid, pid.split(":")[0], d, d, 100.0, None) for a, pid, d in rows],
        "account_id string, plan_id string, plan_type string, plan_start date, "
        "due_date date, due_amount double, payment_amount double",
    )


A_ACCTS = ["A", "B", "K", "M", "Bk"]
dues = df(
    [
        (a, s, n, 300.0 if (a, s) == ("A", D(2026, 7, 5)) else 100.0, 100.0)
        for a in A_ACCTS
        for s, n in zip(stmts, stmts[1:])
    ],
    "account_id string, cycle_start date, cycle_end date, due_amount double, "
    "billed_amount double",
)
pays = df(
    [
        ("A", D(2026, 6, 30), D(2026, 6, 30), 120.0),
        ("A", D(2026, 7, 20), D(2026, 7, 20), 150.0),
        ("B", D(2026, 5, 10), D(2026, 5, 10), 200.0),
        ("K", D(2026, 5, 20), D(2026, 5, 20), 150.0),
        ("K", D(2026, 6, 20), D(2026, 6, 20), 150.0),
    ],
    "account_id string, pay_from date, pay_date date, amount double",
)
a_followup = fu(
    [
        ("A", "2026-06-20", "PROMISE TO PAY"),
        ("A", "2026-06-24", "PROMISE TO PAY SCHEDULED"),
        ("A", "2026-07-14", "CODE25 WILL PAY AT SALARY"),
        ("A", "2026-07-25", "SOFTPTP"),
        ("A", "2026-08-20", "PROMISE TO PAY"),
        ("B", "2026-05-03", "PROMISE TO PAY"),
        ("K", "2026-05-10", "PROMISE TO PAY"),
        ("K", "2026-06-10", "WILL PAY AT SALARY"),
        ("M", "2026-06-05", "PROMISE TO PAY"),
        ("M", "2026-06-14", "PROMISE TO PAY"),
        ("Bk", "2026-05-10", "PROMISE TO PAY"),
        ("Bk", "2026-06-10", "PROMISE TO PAY"),
        ("Bk", "2026-07-10", "PROMISE TO PAY"),
    ]
)
a_agreements = df([(a, a) for a in A_ACCTS], "account_id string, agreement_id string")
inst = plan_rows(
    [
        ("A", "ptp:1", D(2026, 7, 10)),
        ("A", "settlement:2", D(2026, 2, 1)),
        ("A", "settlement:0", D(2025, 8, 1)),
        ("M", "ptp:5", D(2026, 6, 10)),
    ]
)
ep = episode([(a, D(2026, 4, 1), False) for a in A_ACCTS])
obs_a = ep.select("account_id", "observation_date", "cif_id")


def events_for(deadline):
    return build_promise_events(
        obs_a, a_followup, a_agreements, inst, dues, pays, deadline
    )


ev = events_for("next_statement")
check(
    "events A",
    sorted(
        (str(r["event_date"]), r["event_kind"], r["event_name"], r["promise_outcome"])
        for r in ev.where("account_id = 'A'").collect()
    ),
    [
        ("2025-08-01", "table_only", None, "none"),
        ("2026-02-01", "table_only", None, "none"),
        ("2026-06-20", "followup_only", "PROMISE TO PAY", "paid"),
        ("2026-07-10", "matched", "CODE25 WILL PAY AT SALARY", "partial"),
        ("2026-08-20", "followup_only", "PROMISE TO PAY", "none"),
    ],
)
check(
    "events M",
    sorted(
        (str(r["event_date"]), r["event_kind"])
        for r in ev.where("account_id = 'M'").collect()
    ),
    [("2026-06-05", "followup_only"), ("2026-06-10", "matched")],
)
check(
    "cutoff A 07-10",
    [
        str(r["promise_cutoff"])
        for r in ev.where("account_id = 'A' AND event_date = '2026-07-10'").collect()
    ],
    ["2026-08-05"],
)
sig = build_commitment_signals(ep, ev)
check(
    "A counts",
    [
        (r["commitments_concluded"], r["commitments_kept"], r["commitments_partial"])
        for r in sig.where("account_id = 'A'").collect()
    ],
    [(3, 1, 1)],
)
check(
    "A levels (next statement)",
    by_account(sig, "a3_commitments_level"),
    {"A": "broken", "B": "thin", "K": "kept", "M": "broken", "Bk": "broken"},
)
sig30 = build_commitment_signals(ep, events_for("30_days"))
check(
    "B level (30 days)", by_account(sig30, "a3_commitments_level")["B"], "partly_kept"
)
# RL, end of the next month: cash dated at the month end. R: promise 06-15, July cash ->
# paid; S: only August cash -> none; T: June cash counts (same month); U: promise on
# 06-30, June cash dated 06-30 counts.
rl_accts = ["R", "S", "T", "U"]
rl_dues = df(
    [
        (
            a,
            D(2026, m, 1) - dt.timedelta(days=1),
            D(2026, m + 1, 1) - dt.timedelta(days=1),
            1000.0,
            1000.0,
        )
        for a in rl_accts
        for m in range(1, 9)
    ],
    "account_id string, cycle_start date, cycle_end date, due_amount double, "
    "billed_amount double",
)
rl_pays = df(
    [
        ("R", D(2026, 7, 1), D(2026, 7, 31), 1000.0),
        ("S", D(2026, 8, 1), D(2026, 8, 31), 1000.0),
        ("T", D(2026, 6, 1), D(2026, 6, 30), 1000.0),
        ("U", D(2026, 6, 1), D(2026, 6, 30), 1000.0),
    ],
    "account_id string, pay_from date, pay_date date, amount double",
)
rl_ev = build_promise_events(
    episode([(a, D(2026, 4, 1), False) for a in rl_accts]).select(
        "account_id", "observation_date", "cif_id"
    ),
    fu(
        [
            ("R", "2026-06-15", "PROMISE TO PAY"),
            ("S", "2026-06-15", "PROMISE TO PAY"),
            ("T", "2026-06-15", "PROMISE TO PAY"),
            ("U", "2026-06-30", "PROMISE TO PAY"),
        ]
    ),
    df([(a, a) for a in rl_accts], "account_id string, agreement_id string"),
    plan_rows([]),
    rl_dues,
    rl_pays,
    "next_month_end",
)
check(
    "RL outcomes",
    by_account(rl_ev, "promise_outcome"),
    {"R": "paid", "S": "none", "T": "paid", "U": "paid"},
)

# ── 3-4. Dimensions B and C on the ledger ─────────────────────────────────────
# Months (result statement = month end). X: episode 2026-05; cycles ending 06..08 paid in
# full -> regular; X pre-episode 2025-05..2026-04: 12 months due, 10 paid -> clean (83%).
# Y: 60 AED payments only -> none (below 100 AED). Z: one 150 AED payment in 07 -> some.
# W: censored -> windows from the lookback, C no record.
months = [D(2025, m, 28) for m in range(1, 13)] + [D(2026, m, 28) for m in range(1, 9)]
led_rows = []
for acct, paid in [
    ("X", lambda e: 0.0 if e in (D(2025, 7, 28), D(2025, 9, 28)) else 100.0),
    ("Y", lambda e: 60.0),
    ("Z", lambda e: 150.0 if e == D(2026, 7, 28) else 0.0),
    ("W", lambda e: 100.0),
]:
    for s, e in zip(months, months[1:]):
        led_rows.append((acct, s, e, 100.0, 100.0, paid(e)))
ledger = df(
    led_rows,
    "account_id string, cycle_start date, cycle_end date, due_amount double, "
    "billed_amount double, paid_amount double",
)
ep_bc = episode(
    [
        ("X", D(2026, 5, 1), False),
        ("Y", D(2026, 5, 1), False),
        ("Z", D(2026, 5, 1), False),
        ("W", D(2026, 5, 1), True),
    ]
)
b_lv = by_account(
    build_dlq_payment_signals(ep_bc, ledger, "cc_60_180"), "a3_dlq_payment_level"
)
check("B levels", b_lv, {"X": "regular", "Y": "none", "Z": "some", "W": "regular"})
c = build_pre_dlq_payment_signals(ep_bc, ledger)
check(
    "C levels",
    by_account(c, "a3_pre_dlq_payment_level"),
    {"X": "clean", "Y": "not_clean", "Z": "not_clean", "W": "no_record"},
)
check(
    "C X counts",
    [
        (r["pre_dlq_months_due_n"], r["pre_dlq_months_paid_as_billed_n"])
        for r in c.collect()
        if r["account_id"] == "X"
    ],
    [(12, 10)],
)
check("C W reason", by_account(c, "pre_dlq_reason")["W"], "censored")
# Ledger: payments land in (cycle_start, cycle_end].
lg = build_cycle_ledger(dues, pays)
check(
    "ledger A 07-05..08-05",
    [
        r["paid_amount"]
        for r in lg.collect()
        if r["cycle_end"] == D(2026, 8, 5) and r["account_id"] == "A"
    ],
    [150.0],
)

# ── 5. Contacts ───────────────────────────────────────────────────────────────
# agreement = account id. R1 refuses on 07-01, nothing after -> refusal. R2 refuses, then
# two 60 AED payments in two cycles -> still refusal (no cycle with 100). R3 refuses, then
# 150 in one cycle -> not. R4 refuses and promises the same day -> latest is the promise.
# R5 refuses, then a plan starts -> not. D1 disputes. H1 hangs up, then 3 ringing days.
fu_rows = []
for a in ("R1", "R2", "R3", "R5"):
    fu_rows.append((a, "2026-07-01 10:00:00", "OC", "SUC", "REFUSE TO PAY"))
fu_rows += [
    ("R4", "2026-07-01 10:00:00", "OC", "SUC", "REFUSE TO PAY"),
    ("R4", "2026-07-01 11:00:00", "OC", "SUC", "PROMISE TO PAY"),
    ("D1", "2026-07-01 10:00:00", "OC", "SUC", "DISPUTE"),
    ("H1", "2026-07-01 10:00:00", "OC", "SUC", "CUSTOMER HUNG UP"),
    ("P1", "2026-07-01 10:00:00", "OC", "SUC", "PARTIALLY PAID"),
]
fu_rows += [
    ("H1", f"2026-07-{d:02d} 10:00:00", "OC", "UNS", "RINGING NO REPLY")
    for d in (2, 3, 4)
]
followup = df(
    fu_rows,
    "agreement_id string, action_ts string, action_code string, "
    "result_category string, result_name string",
).withColumn("action_ts", F.to_timestamp("action_ts"))
accts = ["R1", "R2", "R3", "R4", "R5", "D1", "H1", "P1"]
agreements = df([(a, a) for a in accts], "account_id string, agreement_id string")
ep_ct = episode([(a, D(2026, 4, 1), False) for a in accts])
c_dues = df(
    [(a, s, n, 100.0, 100.0) for a in accts for s, n in zip(stmts, stmts[1:])],
    "account_id string, cycle_start date, cycle_end date, due_amount double, "
    "billed_amount double",
)
c_pays = df(
    [
        ("R2", D(2026, 7, 10), D(2026, 7, 10), 60.0),
        ("R2", D(2026, 8, 10), D(2026, 8, 10), 60.0),
        ("R3", D(2026, 7, 10), D(2026, 7, 10), 150.0),
    ],
    "account_id string, pay_from date, pay_date date, amount double",
)
c_inst = df(
    [("R5", "ptp:9", "ptp", D(2026, 7, 15), D(2026, 7, 30), 100.0, None)],
    "account_id string, plan_id string, plan_type string, plan_start date, "
    "due_date date, due_amount double, payment_amount double",
)
ct = build_contact_signals(
    ep_ct, followup, agreements, c_inst, c_pays, c_dues, "cc_60_180"
)
check(
    "refusal",
    by_account(ct, "a3_refusal_flag"),
    {
        "R1": True,
        "R2": True,
        "R3": False,
        "R4": False,
        "R5": False,
        "D1": False,
        "H1": False,
        "P1": False,
    },
)
check("R4 latest", by_account(ct, "last_rpc_disposition")["R4"], "ptp")
check("P1 latest", by_account(ct, "last_rpc_disposition")["P1"], "paid")
check("dispute", by_account(ct, "a3_dispute_flag")["D1"], True)
check(
    "hung up / no pickup",
    (
        by_account(ct, "a3_hung_up_last")["H1"],
        by_account(ct, "a3_no_pickup_after_contact")["H1"],
    ),
    (True, True),
)

# ── 6. State: Moderate from 2, a refusal demotes, no episode is Unknown ────────
ep_s = episode(
    [("K", D(2026, 4, 1), False), ("A", D(2026, 4, 1), False), ("N", None, None)]
)
st = build_a3_credibility(
    ep_s,
    build_commitment_signals(ep_s, ev),
    build_dlq_payment_signals(ep_s, ledger, "cc_60_180"),
    build_pre_dlq_payment_signals(ep_s, ledger),
    build_contact_signals(ep_s, followup, agreements, inst, pays, dues, "cc_60_180"),
    "next_statement",
    "2026-08-31",
)
check("state N", by_account(st, "a3_unknown_reason")["N"], "no_episode")
check(
    "state K / A",
    (by_account(st, "a3_state")["K"], by_account(st, "a3_state")["A"]),
    ("payment_credibility_moderate", "payment_credibility_low"),
)  # kept 2 / partly kept 1, no B or C
check("deadline column", by_account(st, "a3_promise_deadline")["K"], "next_statement")

# ── 7. Instalments: cancelled plans and instalments drop out ──────────────────
obs_i = df(
    [("A", OBS, "CA")], "account_id string, observation_date date, cif_id string"
)
built = build_instalments(
    obs_i,
    df([("A", 7)], "account_id string, agreement_id long"),
    df(
        [(7, 1, D(2026, 7, 1), D(2026, 7, 2), 0), (7, 2, None, D(2026, 7, 3), 1)],
        "agreement_id long, promise_seqno long, promise_start date, event_date date, is_cancelled int",
    ),
    df(
        [(1, D(2026, 7, 20), 500.0, None, "B"), (2, D(2026, 7, 21), 50.0, None, "B")],
        "promise_seqno long, due_date date, due_amount double, payment_amount double, "
        "instalment_status string",
    ),
    df(
        [(7, 5, D(2026, 6, 1), 0)],
        "agreement_id long, rps_seqno long, event_date date, is_cancelled int",
    ),
    df(
        [(5, D(2026, 6, 10), 300.0, 300.0, "F"), (5, D(2026, 7, 10), 300.0, None, "C")],
        "rps_seqno long, due_date date, due_amount double, payment_amount double, instalment_status string",
    ),
)
check(
    "instalments",
    sorted((r["plan_id"], str(r["due_date"])) for r in built.collect()),
    [("ptp:1", "2026-07-20"), ("settlement:5", "2026-06-10")],
)

# ── 8. Kedro: both product pipelines end to end ──────────────────
from kedro.io import DataCatalog, MemoryDataset  # noqa: E402
from kedro.runner import SequentialRunner  # noqa: E402

from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility import (  # noqa: E402
    create_pipeline as cc_pipeline,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility import (  # noqa: E402
    create_pipeline as rl_pipeline,
)

obs = df(
    [("A", OBS, "CA"), ("N", OBS, "CN")],
    "account_id string, observation_date date, cif_id string",
)
a4 = df(
    [("A", OBS, 6, 10, False, False)],  # episode 2026-05
    "account_id string, observation_date date, months_before_spell int, history_months int, "
    "left_censored boolean, history_cropped boolean",
)
shared = {
    "prm_dcore_account_agreements": df(
        [("A", 7)], "account_id string, agreement_id long"
    ),
    "dcore_int_ptp": df(
        [(7, 1, D(2026, 7, 1), D(2026, 7, 2), 0)],
        "agreement_id long, promise_seqno long, promise_start date, "
        "event_date date, is_cancelled int",
    ),
    "dcore_prm_promise_instalments": df(
        [(1, D(2026, 7, 20), 500.0, 500.0, "F")],
        "promise_seqno long, due_date date, due_amount double, "
        "payment_amount double, instalment_status string",
    ),
    "dcore_int_settlement": df(
        [], "agreement_id long, rps_seqno long, event_date date, is_cancelled int"
    ),
    "dcore_prm_settlement_schedule_instalments": df(
        [],
        "rps_seqno long, due_date date, due_amount double, payment_amount double, "
        "instalment_status string",
    ),
    "dcore_prm_followup_outcomes": followup.where("agreement_id = 'R1'").withColumn(
        "agreement_id", F.lit("7")
    ),
    "params:crx_persona.persona_end_date": "2026-08-31",
    "params:cc_a3_history_floor_date": "2024-01-01",
}
cc_in = {
    "crx_cc_obs_base": obs,
    "crx_cc_a4_deterioration": a4,
    "crx_cc_billing": df(
        [("A", s, n) for s, n in zip(stmts, stmts[1:])],
        "contract_id string, observation_date date, next_billing_date date",
    ),
    "crx_cc_balance": df(
        [("A", s, 100.0, *[0.0] * 8) for s in stmts],
        "contract_id string, observation_date date, minimum_due double, "
        + ", ".join(f"overdue_bucket_0{i} double" for i in range(1, 9)),
    ),
    "crx_cc_transactions": df(
        [("A", D(2026, 7, 30), 500.0, "payment", 0)],
        "contract_id string, observation_date date, txn_amount_aed double, "
        "txn_category string, is_post_block_x_fee int",
    ),
}
rl_in = {
    "crx_rl_obs_base": obs,
    "crx_rl_a4_deterioration": a4,
    "int_loan_master": df(
        [("A", D(2026, m, 28 if m == 2 else 30), 500.0, 500.0) for m in range(1, 9)],
        "account_id string, observation_date date, monthly_emi_due double, "
        "total_paid double",
    ),
}
for product, make, inputs, model in [
    ("cc", cc_pipeline, cc_in, "cc_60_180"),
    ("rl", rl_pipeline, rl_in, "rl_60_180"),
]:
    pipe = make()
    data = {**shared, **inputs, "params:model_id": model}
    cat = DataCatalog(
        {n: MemoryDataset(v, copy_mode="assign") for n, v in data.items()}
        | {n: MemoryDataset(copy_mode="assign") for n in pipe.all_outputs()}
    )
    SequentialRunner().run(pipe, cat)
    out = cat.load(f"crx_{product}_a3_payment_credibility")
    got = {
        r["account_id"]: (r["a3_state"], r["a3_refusal_flag"], r["a3_promise_deadline"])
        for r in out.collect()
    }
    check(f"kedro {product} rows", sorted(got), ["A", "N"])
    check(f"kedro {product} N", got["N"][0], "payment_credibility_unknown")
    check(f"kedro {product} A refusal (paid after)", got["A"][1], False)
    check(
        f"kedro {product} deadline",
        got["A"][2],
        {"cc": "next_statement", "rl": "next_month_end"}[product],
    )
    check(
        f"kedro {product} promises concluded",
        by_account(out, "commitments_concluded")["A"],
        1,
    )

# ── 9. TEMPORARY (A3 bundle 20): the check pipelines run and log every block ──
import logging  # noqa: E402

from enbd_collections.pipelines.crx_persona.a3_credibility import (  # noqa: E402
    check as a3_check,
)
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility import (  # noqa: E402
    create_check_pipeline as cc_check,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility import (  # noqa: E402
    create_check_pipeline as rl_check,
)

logged = []
handler = logging.Handler()
handler.emit = lambda record: logged.append(record.getMessage())
logging.getLogger(a3_check.__name__).addHandler(handler)
logging.getLogger(a3_check.__name__).setLevel(logging.INFO)
old_out = df(
    [
        ("A", OBS, "payment_credibility_moderate", 1, False, "broken", 2, "ptp"),
        ("N", OBS, "payment_credibility_unknown", 0, False, "thin", 0, None),
    ],
    "account_id string, observation_date date, a3_state string, a3_points_total int, "
    "a3_refusal_flag boolean, a3_commitments_level string, "
    "commitments_concluded int, last_rpc_disposition string",
)
for product, make, inputs, model in [
    ("cc", cc_check, cc_in, "cc_60_180"),
    ("rl", rl_check, rl_in, "rl_60_180"),
]:
    pipe = make()
    data = {
        **shared,
        **inputs,
        "params:model_id": model,
        f"crx_{product}_a3_payment_credibility": old_out,
    }
    cat = DataCatalog(
        {
            n: MemoryDataset(v, copy_mode="assign")
            for n, v in data.items()
            if n in pipe.inputs()
        }
        | {n: MemoryDataset(copy_mode="assign") for n in pipe.all_outputs()}
    )
    SequentialRunner().run(pipe, cat)
    spark.catalog.clearCache()  # one long session: free the CC run first
blocks = [m.split("===")[1].strip() for m in logged]
check(
    "check blocks",
    sorted(set(blocks)),
    sorted(
        f"{b} START" for b in ["A3 OUTPUT", "A3 PROMISES", "A3 LEVELS", "A3 CONTACTS"]
    ),
)
check("check old Moderate from 2", "state old_m2:\n  low: 1 (50.0%)" in logged[0], True)
check("check GRR vs 30 days", "low | moderate: 1" in logged[0], True)
check(
    "check steps",
    [
        w in logged[0]
        for w in ("(whole bundle)", "(promise events)", "(12-month window)")
    ]
    + ["before the episode start" in logged[1]],
    [True] * 4,
)
print("\n\n".join(logged[:4]))

print("\n".join(FAILS) if FAILS else "a3 engine spec: all checks pass")
sys.exit(1 if FAILS else 0)
