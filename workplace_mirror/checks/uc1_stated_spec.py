"""Local spec test for the UC1 stated block (``crx_persona/uc1_stated``).

    python workplace_mirror/checks/uc1_stated_spec.py      (needs pyspark + Java 17)

UC1-shaped rows (call metadata, the customer table ``customer_signal_export`` as in
``bundle_helpers/uc1/uc1_signal_export_datasets.md``), A3 promise events and A1 states go
through both nodes for cc_60_180, UC1 month 2026-07-31. Each case is one customer with
the evidence status, states, details and flags the rules prescribe. Also checks that the
other months stay NULL, that ``uc1_month_end`` = null falls back to the persona end date,
that an unknown level stops the run, and that every dataset the pipelines name is in
``catalog_crx.yml``. Prints a table, exits non-zero on a mismatch.
"""

import os
import pathlib
import sys
from datetime import date, datetime

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path.insert(0, str(HERE.parent / "src"))

import yaml
from pyspark.sql import SparkSession

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# pylint: disable=wrong-import-position
from enbd_collections.pipelines.crx_persona import cc_uc1_stated, rl_uc1_stated
from enbd_collections.pipelines.crx_persona.uc1_stated import (
    build_uc1_conversation_signals,
    build_uc1_stated,
)

END, UC1_MONTH = "2026-08-31", "2026-07-31"
OBS = date(2026, 7, 31)
CATEGORICAL = (
    "payment_capacity",
    "payment_intent",
    "delinquency_reason",
    "payment_period",
    "dispute",
    "request",
    "fraudulent_customer",
)
REPAYMENT = (
    "repayment_specifics:amount_mentioned",
    "repayment_specifics:date_specific",
    "repayment_specifics:plan_structure_mentioned",
)


def export_rows(cif: str, **levels) -> list[tuple]:
    """The customer's 10 export rows; ``levels`` sets ``estimated_value`` per signal
    (repayment slots: ``latest_value``), everything else not detected."""
    rows = []
    for signal in CATEGORICAL:
        value = levels.get(signal, "not-detected")
        conf = "N/A" if value == "not-detected" else "LOW"
        rows.append((cif, signal, value, conf, value, "not-detected", "N/A"))
    for slot in REPAYMENT:
        key = slot.split(":")[1]
        rows.append(
            (
                cif,
                slot,
                "N/A",
                "N/A",
                levels.get(key, "not-detected"),
                "not-detected",
                "N/A",
            )
        )
    return [(*r, "2026-10-31") for r in rows]


# customer: (account, cif, a1_state, conversations [dates], promise events [(start, cutoff)], export levels)
CASES = {
    "no_cif": ("A01", None, "unknown", [], [], None),
    "no_conversation": ("A02", "C02", "unknown", [], [], None),
    "not_extracted": ("A03", "C03", "unknown", ["2026-07-01"], [], None),
    "call_after_obs_only": ("A04", "C04", "unknown", ["2026-08-05"], [], None),
    "able_pays_unlogged_low": (
        "A05",
        "C05",
        "low",
        ["2026-07-10"],
        [("2026-06-01", "2026-06-20")],
        {
            "payment_capacity": "full",
            "payment_intent": "payback_full",
            "amount_mentioned": "2,400",
        },
    ),
    "partly_logged": (
        "A06",
        "C06",
        "moderate",
        ["2026-07-10"],
        [("2026-07-12", "2026-07-30")],
        {"payment_intent": "partial", "date_specific": "2026-07-20"},
    ),
    "ties_cautious": (
        "A07",
        "C07",
        "high",
        ["2026-07-01"],
        [],
        {"payment_capacity": "full|none", "payment_intent": "partial|payback_full"},
    ),
    "all_not_detected": ("A08", "C08", "low", ["2026-07-01"], [], {}),
    "remark_only_no_call": (
        "A09",
        "C09",
        "unknown",
        [],
        [],
        {"payment_intent": "payback_full", "amount_mentioned": "1,000"},
    ),
    "details": (
        "A10",
        "C10",
        "unknown",
        ["2026-06-15"],
        [],
        {
            "delinquency_reason": "lost_employment",
            "payment_period": "weeks",
            "dispute": "system_problem",
            "request": "detected",
            "fraudulent_customer": "detected",
            "plan_structure_mentioned": "detected",
        },
    ),
    "event_after_obs_ignored": (
        "A11",
        "C11",
        "unknown",
        ["2026-07-28"],
        [("2026-08-02", "2026-08-20")],
        {"payment_intent": "with_delay", "amount_mentioned": "500"},
    ),
}
EXPECTED = {  # uc1_evidence, a5, a6, promise flag, verify flag
    "no_cif": ("no_cif", "no_evidence", "no_evidence", None, None),
    "no_conversation": ("no_conversation", "no_evidence", "no_evidence", None, None),
    "not_extracted": ("not_extracted", "no_evidence", "no_evidence", None, None),
    "call_after_obs_only": (
        "no_conversation",
        "no_evidence",
        "no_evidence",
        None,
        None,
    ),
    "able_pays_unlogged_low": ("extracted", "able", "pays_in_full", 1, 1),
    "partly_logged": ("extracted", "not_stated", "partly_or_later", 0, 0),
    "ties_cautious": ("extracted", "unable", "partly_or_later", 0, 0),
    "all_not_detected": ("extracted", "not_stated", "not_stated", 0, 0),
    "remark_only_no_call": ("extracted", "not_stated", "pays_in_full", None, 0),
    "details": ("extracted", "not_stated", "not_stated", 0, 0),
    "event_after_obs_ignored": ("extracted", "not_stated", "partly_or_later", 1, 0),
}
DETAILS = {  # extra columns checked on one case
    "details": {
        "a5_reason": "lost_employment",
        "a6_period": "weeks",
        "stated_dispute": "system_problem",
        "stated_request_flag": 1,
        "stated_fraud_flag": 1,
        "a6_plan_named_flag": 1,
        "a6_amount_named_flag": 0,
        "uc1_conversations_n": 1,
    },
    "ties_cautious": {
        "a6_intent_level": "partial|payback_full",
        "a5_capacity_level": "full|none",
    },
    "all_not_detected": {"stated_dispute": "none", "stated_request_flag": 0},
    "remark_only_no_call": {"uc1_conversations_n": None, "a6_amount_named_flag": 1},
}


def frames(cases: dict):
    obs, meta, events, a1, export = [], [], [], [], []
    for i, (acct, cif, a1_state, calls, evs, levels) in enumerate(cases.values()):
        for month_end in (date(2026, 7, 31), date(2026, 8, 31)):
            obs.append((acct, month_end, cif))
            a1.append((acct, month_end, a1_state))
        meta += [
            (f"conv{i}_{j}", cif, datetime.fromisoformat(d))
            for j, d in enumerate(calls)
        ]
        events += [(acct, date.fromisoformat(s), date.fromisoformat(c)) for s, c in evs]
        if levels is not None:
            export += export_rows(cif, **levels)
    return (
        spark.createDataFrame(
            obs, "account_id string, observation_date date, cif_id string"
        ),
        spark.createDataFrame(
            meta, "conversationid string, cif_id string, conversationstart timestamp"
        ),
        spark.createDataFrame(
            events, "account_id string, event_date date, promise_cutoff date"
        ),
        spark.createDataFrame(
            a1, "account_id string, observation_date date, a1_state string"
        ),
        spark.createDataFrame(
            export,
            "cif_id string, signal string, estimated_value string, confidence string, "
            "latest_value string, agent_remark_value string, supporting_data string, "
            "snapshot_date string",
        ),
    )


def run(cases: dict, month_end):
    obs, meta, events, a1, export = frames(cases)
    conv = build_uc1_conversation_signals(obs, meta, events, END, month_end)
    return build_uc1_stated(obs, export, conv, a1, "cc_60_180", END, month_end)


failures = []
out = run(CASES, UC1_MONTH)
rows = {r["account_id"]: r for r in out.filter(f"observation_date = '{OBS}'").collect()}
print(f"{'case':26} {'evidence':16} {'a5':12} {'a6':16} promise verify  ok")
for case, (acct, *_rest) in CASES.items():
    r = rows[acct]
    got = (
        r["uc1_evidence"],
        r["a5_state"],
        r["a6_state"],
        r["stated_promise_unlogged_flag"],
        r["verify_stated_ability_flag"],
    )
    ok = got == EXPECTED[case]
    for col, want in DETAILS.get(case, {}).items():
        if r[col] != want:
            ok = False
            print(f"  {case}: {col} = {r[col]!r}, want {want!r}")
    if not ok:
        failures.append(case)
    print(
        f"{case:26} {got[0]:16} {got[1]:12} {got[2]:16} {got[3]!s:7} {got[4]!s:6} {'ok' if ok else 'FAIL'}"
    )

other = (
    out.filter("observation_date <> '2026-07-31'")
    .filter("uc1_evidence is not null")
    .count()
)
if other:
    failures.append("other months not NULL")
print(f"other months with a UC1 value: {other}")

fallback = run(CASES, None)
aug = fallback.filter(
    "observation_date = '2026-08-31' and uc1_evidence is not null"
).count()
if aug != len(CASES):
    failures.append("uc1_month_end null does not fall back to persona_end_date")
print(f"uc1_month_end null -> scored rows at {END}: {aug} of {len(CASES)}")

bad = dict(CASES)
bad["unknown_level"] = ("A99", "C99", "low", [], [], {"payment_capacity": "plenty"})
try:
    run(bad, UC1_MONTH).count()
    failures.append("unknown level did not stop the run")
    print("unknown level: not stopped (FAIL)")
except ValueError as err:
    print(f"unknown level stops the run: {err}")

catalog = yaml.safe_load(
    (HERE.parent / "conf/base/catalog/catalog_crx.yml").read_text()
)
named = set()
for module in (cc_uc1_stated, rl_uc1_stated):
    pipe = module.create_pipeline()
    named |= {d for d in pipe.datasets() if not d.startswith("params:")}
missing = sorted(d for d in named if d not in catalog)
if missing:
    failures.append(f"not in catalog_crx.yml: {missing}")
print(
    f"datasets named by the pipelines, missing from catalog_crx.yml: {missing or 'none'}"
)

print("FAIL: " + ", ".join(failures) if failures else "all checks pass")
sys.exit(1 if failures else 0)
