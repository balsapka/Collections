"""Local spec test for the UC1 stated block (``crx_persona/uc1_stated``).

    python workplace_mirror/checks/uc1_stated_spec.py      (needs pyspark + Java 17)

UC1-shaped rows (metadata, extraction ledger, per-conversation grid, customer table, as
in ``bundle_helpers/uc1/uc1_timelines_handoff.md``) go through both nodes for
cc_60_180, scored month 2026-08. Each case is one customer with the evidence status,
states, support and flags the review's decisions D1-D5 prescribe. Also checks that an
unknown level stops the run and that every dataset the pipelines name is in
``catalog_crx.yml``. Prints a table, exits non-zero on a mismatch.
"""

import json
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
from enbd_collections.pipelines.crx_persona import (
    cc_uc1_stated,
    rl_uc1_stated,
)
from enbd_collections.pipelines.crx_persona.uc1_stated import (
    build_uc1_conversation_signals,
    build_uc1_stated,
)

END = "2026-08-31"
OBS = date(2026, 8, 31)
SIGNALS = (
    "delinquency_reason",
    "dispute",
    "fraudulent_customer",
    "payment_capacity",
    "payment_intent",
    "payment_period",
    "repayment_specifics",
    "request",
)
SLOTS = {
    "delinquency_reason": [
        "has_employment",
        "increased_obligations",
        "lost_employment",
        "reduced_employment",
    ],
    "dispute": ["customer_scammed", "other", "system_problem"],
    "request": ["detected"],
    "payment_intent": ["no_payment", "partial", "payback_full", "with_delay"],
    "payment_capacity": ["full", "none", "partial"],
    "payment_period": ["months_or_longer", "salary_cycle_dependent", "weeks"],
    "fraudulent_customer": ["detected"],
    "repayment_specifics": [
        "amount_mentioned",
        "date_specific",
        "plan_structure_mentioned",
    ],
}

# conversations: (cif, conversationid, start, ledger: None / "gemma" / "legacy", detected);
# a legacy-only conversation is dropped (A3: no conversation left; A3b: one unextracted)
# detected = {signal: value}; a repayment_specifics value is the encoded string.
CONVERSATIONS = [
    (
        "10000001",
        "c1a",
        "2026-07-01",
        "gemma",
        {
            "payment_capacity": "full",
            "payment_intent": "payback_full",
            "repayment_specifics": "amount_mentioned:2,000",
        },
    ),
    ("10000002", "c2a", "2026-06-01", "gemma", {}),
    ("10000003", "c3a", "2026-05-10", "legacy", {}),
    ("10000013", "c13a", "2026-05-10", "legacy", {}),
    ("10000013", "c13b", "2026-06-10", None, {}),
    ("10000004", "c4a", "2026-04-02", None, {}),
    ("10000007", "c7a", "2026-09-05", "gemma", {"payment_capacity": "none"}),
    (
        "10000008",
        "c8a",
        "2026-06-01",
        "gemma",
        {
            "payment_capacity": "partial",
            "payment_intent": "with_delay",
            "repayment_specifics": "date_specific:2026-06-25",
        },
    ),
    ("10000008", "c8b", "2026-07-01", "gemma", {"payment_capacity": "full"}),
    ("10000008", "c8c", "2026-09-02", "gemma", {"payment_capacity": "partial"}),
    (
        "10000009",
        "c9a",
        "2026-08-30",
        "gemma",
        {"payment_capacity": "none", "payment_intent": "no_payment"},
    ),
    ("10000010", "c10a", "2026-08-31", "gemma", {"payment_capacity": "full"}),
]
# the customer table as UC1 publishes it (signals not listed are "NA")
AGGREGATION = {
    "10000001": {
        "payment_capacity": "full",
        "payment_intent": "payback_full",
        "delinquency_reason": "has_employment",
        "payment_period": "weeks",
        "dispute": "system_problem",
        "request": "detected",
        "repayment_specifics": "amount_mentioned:2,000",
    },
    "10000002": {},
    "10000003": {},
    "10000007": {"payment_capacity": "none"},
    "10000008": {
        "payment_capacity": "partial",
        "payment_intent": "with_delay",
        "repayment_specifics": "date_specific:2026-06-25",
    },
    "10000009": {
        "payment_capacity": "none",
        "payment_intent": "no_payment",
        "delinquency_reason": "lost_employment",
    },
    "10000010": {"payment_capacity": "full"},
}
# obs base: (account_id, observation_date, cif_id)
OBS_BASE = [
    ("A1", OBS, "10000001"),
    ("A1b", OBS, "10000001"),
    ("A1", date(2026, 7, 31), "10000001"),
    ("A2", OBS, "10000002"),
    ("A3", OBS, "10000003"),
    ("A3b", OBS, "10000013"),
    ("A4", OBS, "10000004"),
    ("A5", OBS, "10000005"),
    ("A6", OBS, None),
    ("A7", OBS, "10000007"),
    ("A8", OBS, "10000008"),
    ("A9", OBS, "10000009"),
    ("A10", OBS, "10000010"),
]

# expected: account -> {column: value}
EXPECTED = {
    "A1": {
        "uc1_evidence": "extracted",
        "a5_state": "able",
        "a5_reason": "has_employment",
        "a5_conversations_n": 1,
        "a5_agree_n": 1,
        "a6_state": "pays_in_full",
        "a6_intent_level": "payback_full",
        "a6_period": "weeks",
        "a6_amount_named_flag": 1,
        "a6_date_named_flag": 0,
        "stated_dispute": "system_problem",
        "stated_request_flag": 1,
        "uc1_conversations_n": 1,
        "uc1_after_obs_flag": 0,
    },
    "A1b": {
        "uc1_evidence": "extracted",
        "a5_state": "able",
        "a6_state": "pays_in_full",
    },
    "A2": {
        "uc1_evidence": "extracted",
        "a5_state": "not_stated",
        "a6_state": "not_stated",
        "a5_conversations_n": 0,
        "stated_dispute": "none",
        "stated_request_flag": 0,
    },
    "A3": {
        "uc1_evidence": "no_conversation",
        "a5_state": "no_evidence",
        "a6_state": "no_evidence",
        "stated_dispute": None,
        "uc1_conversations_n": 0,
        "uc1_extracted_n": 0,
    },
    "A3b": {
        "uc1_evidence": "not_extracted",
        "a5_state": "no_evidence",
        "uc1_conversations_n": 1,
        "uc1_extracted_n": 0,
    },
    "A4": {
        "uc1_evidence": "not_extracted",
        "a5_state": "no_evidence",
        "uc1_conversations_n": 1,
        "uc1_extracted_n": 0,
    },
    "A5": {
        "uc1_evidence": "no_conversation",
        "a5_state": "no_evidence",
        "uc1_conversations_n": 0,
        "uc1_after_obs_flag": 0,
    },
    "A6": {"uc1_evidence": "no_cif", "a5_state": "no_evidence"},
    "A7": {
        "uc1_evidence": "no_conversation",
        "a5_state": "no_evidence",
        "uc1_after_obs_flag": 1,
    },
    "A8": {
        "uc1_evidence": "extracted",
        "a5_state": "partly_able",
        "a5_conversations_n": 2,
        "a5_agree_n": 1,
        "a6_state": "partly_or_later",
        "a6_intent_level": "with_delay",
        "a6_date_named_flag": 1,
        "a6_amount_named_flag": 0,
        "uc1_conversations_n": 2,
        "uc1_last_conversation_date": date(2026, 7, 1),
        "uc1_after_obs_flag": 1,
    },
    "A9": {
        "uc1_evidence": "extracted",
        "a5_state": "unable",
        "a6_state": "refuses",
        "a5_reason": "lost_employment",
    },
    "A10": {
        "uc1_evidence": "no_conversation",
        "a5_state": "no_evidence",
        "uc1_after_obs_flag": 1,
    },
}


def _frames(aggregation=None):
    meta = spark.createDataFrame(
        [(cid, cif, datetime.fromisoformat(d)) for cif, cid, d, _, _ in CONVERSATIONS],
        "conversationid string, cif_id string, conversationstart timestamp",
    )
    ledger = spark.createDataFrame(
        [
            (cid, "legacy" if v == "legacy" else "gemma-4-31b-bedrock")
            for _, cid, _, v, _ in CONVERSATIONS
            if v
        ],
        "conversationid string, model_version string",
    )
    grid_rows = []
    for cif, cid, _, version, det in CONVERSATIONS:
        if not version:
            continue
        for signal, slots in SLOTS.items():
            for slot in slots:
                value = det.get(signal)
                hit = value is not None and value.split(":")[0] == slot
                grid_rows.append(
                    (
                        cif,
                        cid,
                        signal,
                        value if hit else slot,
                        "detected" if hit else "not-detected",
                        None,
                    )
                )
    grid = spark.createDataFrame(
        grid_rows,
        "cif_id string, conversationid string, signal string, value string, "
        "observation string, conflicting_signals string",
    )
    agg = aggregation or AGGREGATION
    agg_df = spark.createDataFrame(
        [
            (
                cif,
                f"c{cif}",
                json.dumps(
                    {s: ({"level": lv[s]} if s in lv else "NA") for s in SIGNALS}
                ),
            )
            for cif, lv in agg.items()
        ],
        "cif_id string, conversationid string, signals_json string",
    )
    base = spark.createDataFrame(
        OBS_BASE, "account_id string, observation_date date, cif_id string"
    )
    return base, meta, ledger, grid, agg_df


def _run(aggregation=None):
    base, meta, ledger, grid, agg = _frames(aggregation)
    conv = build_uc1_conversation_signals(base, meta, ledger, grid, END)
    return build_uc1_stated(base, agg, conv, "cc_60_180", END)


def main() -> int:
    out = {
        (r["account_id"], r["observation_date"]): r.asDict() for r in _run().collect()
    }
    failures = 0
    print(f"{'case':6} {'column':28} {'expected':18} {'got':18}")
    for account, cols in EXPECTED.items():
        row = out[(account, OBS)]
        for col, want in cols.items():
            got = row[col]
            mark = "" if got == want else "  <-- MISMATCH"
            failures += bool(mark)
            print(f"{account:6} {col:28} {want!s:18} {got!s:18}{mark}")
    july = out[("A1", date(2026, 7, 31))]
    unscored = [
        c
        for c, v in july.items()
        if c not in ("account_id", "observation_date") and v is not None
    ]
    print(f"A1 2026-07 unscored month, non-NULL columns: {unscored or 'none'}")
    failures += bool(unscored)
    print(f"rows out = {len(out)} (obs base {len(OBS_BASE)})")
    failures += len(out) != len(OBS_BASE)

    bad = dict(AGGREGATION, **{"10000002": {"payment_capacity": "maybe"}})
    try:
        _run(bad).count()
        print("unknown level: NOT raised  <-- MISMATCH")
        failures += 1
    except ValueError as exc:
        print(f"unknown level: raised ({exc})")

    catalog = yaml.safe_load(
        (HERE.parent / "conf/base/catalog/catalog_crx.yml").read_text()
    )
    for module in (cc_uc1_stated, rl_uc1_stated):
        names = module.create_pipeline().datasets()
        missing = sorted(
            n for n in names if not n.startswith("params:") and n not in catalog
        )
        print(
            f"{module.__name__.split('.')[-1]}: datasets not in catalog_crx: "
            f"{missing or 'none'}"
        )
        failures += bool(missing)
    print("PASSED" if not failures else f"FAILED ({failures})")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
