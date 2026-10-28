"""Local spec test for the A2 engine against specs/A2_locatability_spec.md.

    python workplace_mirror/checks/a2_engine_spec.py      (needs pyspark + Java 17)

Raw-shaped rows go through the whole chain: login staging + monthly primary, the CASA card
primary, the DCORE agreement primary, the location feature, the signals and the state.
Each case is one account / customer at one observation date (cc_60_180, W = 3 months)
with the rule and states the spec prescribes. Prints a table, exits non-zero on a mismatch.
"""

import os
import pathlib
import sys
from datetime import date, datetime

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path.insert(0, str(HERE.parent / "src"))

from pyspark.sql import SparkSession  # noqa: E402

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

from enbd_collections.nodes.features.location import (  # noqa: E402
    feat_cif_location_monthly,
)
from enbd_collections.nodes.primary.casa.prm_casa import (  # noqa: E402
    build_card_transactions,
)
from enbd_collections.nodes.primary.dcore import (  # noqa: E402
    prm_dcore_account_agreements,
)
from enbd_collections.nodes.primary.digital_login import (  # noqa: E402
    prm_digital_login_monthly,
)
from enbd_collections.nodes.staging.digital_login import (  # noqa: E402
    stg_digital_login,
)
from enbd_collections.pipelines.crx_persona.a2_locatability import (  # noqa: E402
    build_a2_locatability,
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)

MODEL = "cc_60_180"
OBS = date(2026, 7, 31)  # W = May, Jun, Jul
START = "2026-01-01"
UAE, GB = "United Arab Emirates", "United Kingdom"

# ── Expected results: case → (location_rule, reachability_state, deceased_source) ──
CASES = {
    "01": ("L3", "unknown", None),  # UAE login in W
    "02": ("L1", "unknown", None),  # foreign login after a UAE login
    "03": ("L1", "unknown", None),  # same day: UAE login, foreign shop payment
    "04": ("L4", "unknown", None),  # UAE login before W (domestic_before_window)
    "05": ("L4", "unknown", None),  # nothing
    "06": ("L2", "unknown", None),  # ticket, UAE 1 month later, silent since
    "07": ("L3", "unknown", None),  # UAE evidence > 3 months after the ticket
    "08": ("L3", "unknown", None),  # ticket, UAE evidence within the last month
    "09": ("L1", "unknown", None),  # ATM abroad (narration) after a UAE grocery
    "10": ("L3", "unknown", None),  # online foreign purchase is no evidence
    "11": ("L4", "unknown", None),  # remote MCC abroad is no evidence
    "12": ("L4", "unknown", None),  # charges row abroad is no evidence
    "13": (
        "L1",
        "unknown",
        None,
    ),  # credit online abroad ignored, credit grocery abroad
    "14": ("L1", "unknown", None),  # departure note after a UAE login
    "15": ("L4", "unknown", None),  # login without a country
    "16": ("L4", "unknown", None),  # evidence after the observation date
    "17": ("L3", "unknown", None),  # same session loaded twice, NULL sessions kept
    "R1": ("L4", "non_reachable", None),  # 3 failed days, contact before
    "R2": ("L4", "reachable", None),  # failed days, then the customer called
    "R3": ("L4", "unknown", None),  # failed days older than W
    "R5": ("L4", "reachable", None),  # a neutral call breaks the failed run
    "R6": ("L4", "non_reachable", None),  # admin entries are ignored
    "R7": ("L4", "reachable", None),  # outbound SUC in W
    "R8": ("L4", "unknown", None),  # only 2 failed days, contact before W
    "D1": ("L4", "unknown", "dcore"),  # relative's claim (admin note)
    "D2": ("L4", "unknown", "way4"),  # block D on the latest snapshot
    "D3": ("L4", "unknown", None),  # block D removed on a later snapshot
    "D4": ("L4", "unknown", "demographics"),
}
UNKNOWN_REASON = {
    "04": "domestic_before_window",
    "05": "no_evidence",
    "15": "no_evidence",
}
REACH_REASON = {"R3": "no_contact_in_window", "05": "no_dcore_record"}


def ts(y, mo, d):
    return datetime(y, mo, d, 10, 0)


# ── Logins: (case, day, countrylocation, countrycode, sessionid) ──
LOGINS = [
    ("01", ts(2026, 7, 10), UAE, "AE", "s01"),
    ("02", ts(2026, 6, 1), UAE, "AE", "s02a"),
    ("02", ts(2026, 7, 10), GB, "GB", "s02b"),
    ("03", ts(2026, 7, 12), UAE, "AE", "s03"),
    ("04", ts(2026, 3, 1), UAE, "AE", "s04"),
    ("06", ts(2026, 5, 20), UAE, "AE", "s06"),
    ("07", ts(2026, 7, 20), UAE, "AE", "s07"),
    ("08", ts(2026, 7, 15), UAE, "AE", "s08"),
    ("10", ts(2026, 6, 15), UAE, "AE", "s10"),
    ("14", ts(2026, 5, 1), UAE, "AE", "s14"),
    ("15", ts(2026, 7, 1), None, None, "s15"),
    ("16", ts(2026, 8, 5), UAE, "AE", "s16"),
    ("17", ts(2026, 6, 2), UAE, "AE", "s17"),
    ("17", ts(2026, 6, 2), UAE, "AE", "s17"),
    ("17", ts(2026, 6, 3), None, None, None),
    ("17", ts(2026, 6, 4), UAE, "AE", None),
]

# ── Debit-card rows: (case, day, channel, type, code_desc, reason, mcc, country, narration)
POS, ATM = "Point of Sale", "ATM Transactions"
DEBIT = [
    ("03", date(2026, 7, 12), POS, "Machine", "POS-PURCHASE", None, "5411", GB, "SHOP"),
    ("09", date(2026, 6, 1), ATM, None, "DR ATM TRANSACTION", None, "6011", None,
     "ATM WDL LONDON:GB#"),
    ("10", date(2026, 7, 2), POS, "Online", "POS-PURCHASE", None, "5999", GB, "SHOP"),
    ("11", date(2026, 7, 2), POS, "Machine", "POS-PURCHASE", None, "5815", GB, "APP"),
    ("12", date(2026, 7, 2), POS, "Machine", "POS-PURCHASE", "CHARGES", "5411", GB, "FEE"),
]  # fmt: skip

# ── Credit-card rows: (case, day, direction, category, mcc, international, description)
CREDIT = [
    ("06", date(2026, 4, 15), -1, "purchase", "4511", 0, "EMIRATES TICKET"),
    ("07", date(2026, 3, 1), -1, "purchase", "4511", 0, "TICKET"),
    ("08", date(2026, 7, 1), -1, "purchase", "4722", 1, "TRAVEL AGENT"),
    ("09", date(2026, 5, 1), -1, "purchase", "5411", 0, "GROCERY"),
    ("13", date(2026, 7, 5), -1, "purchase", "5999", 1, "AMAZON"),
    ("13", date(2026, 6, 5), -1, "purchase", "5411", 1, "SUPERMARKET"),
    ("13", date(2026, 6, 1), 1, "payment", None, 1, "PAYMENT"),
]

# ── DCORE events: (case, day, action_code, category, result_name) ──
RING = "RINGING NO REPLY"
DCORE = [
    ("14", ts(2026, 6, 1), "IA", "", "LEFT THE COUNTRY"),
    *[("R1", ts(2026, 7, d), "OC", "UNS", RING) for d in (5, 10, 15)],
    ("R1", ts(2026, 6, 1), "OC", "SUC", "PROMISE TO PAY"),
    *[("R2", ts(2026, 7, d), "OC", "UNS", "LEFT_MSG") for d in (5, 10, 15)],
    ("R2", ts(2026, 7, 20), "IC", "INT", "OTHER"),
    *[("R3", ts(2026, 4, d), "OC", "UNS", "WRONG NUMBER") for d in (1, 5, 10)],
    *[("R5", ts(2026, 7, d), "OC", "UNS", RING) for d in (5, 10, 15)],
    ("R5", ts(2026, 7, 10), "OC", "INT", "CALL CONNECTED"),
    ("R5", ts(2026, 6, 1), "IC", "INT", "OTHER"),
    *[("R6", ts(2026, 7, d), "OC", "UNS", RING) for d in (5, 10, 15)],
    ("R6", ts(2026, 7, 20), "OC", "ADM", "Follow up"),
    ("R6", ts(2026, 7, 21), "OC", "ADM", "RPO case 12"),
    ("R7", ts(2026, 6, 10), "OC", "SUC", "OTHER"),
    *[("R8", ts(2026, 7, d), "OC", "UNS", RING) for d in (5, 10)],
    ("R8", ts(2026, 3, 1), "IC", "INT", "OTHER"),
    ("D1", ts(2026, 5, 1), "IA", "", "DECEASED CLAIMED"),
]

# ── Way4 snapshots: (case, snapshot day, block_code_2) ──
WAY4 = [
    ("D2", date(2026, 5, 9), "W"),
    ("D2", date(2026, 7, 9), "D"),
    ("D3", date(2026, 5, 9), "D"),
    ("D3", date(2026, 7, 9), "W"),
    ("D2", date(2026, 8, 9), "W"),  # after the observation date
]


def cif(case):
    return f"C{case}"


def main() -> int:
    obs_base = spark.createDataFrame(
        [(f"A{c}", OBS, cif(c)) for c in CASES],
        "account_id string, observation_date date, cif_id string",
    )
    raw_login = spark.createDataFrame(
        [(f"P{c}", "success", t, loc, code, "MOB", s) for c, t, loc, code, s in LOGINS],
        "partyid string, status string, createdon timestamp, countrylocation string,"
        " countrycode string, channel string, sessionid string",
    )
    raw_history = spark.createDataFrame(
        [], "partyid string, status string, createdon timestamp, countrylocation string"
    )
    users = spark.createDataFrame(
        [(f"P{c}", cif(c), "Y") for c in CASES],
        "id string, cif string, edp_activeind string",
    )
    logins = prm_digital_login_monthly.build(
        stg_digital_login.build(raw_login, raw_history, users)
    )

    comp = spark.createDataFrame(
        [
            (f"T{i}", "1", d, cif(c), f"F{c}", d, d, "D", ch, typ, desc, reason, mcc,
             "MERCHANT", country, None, narr, 100.0)
            for i, (c, d, ch, typ, desc, reason, mcc, country, narr) in enumerate(DEBIT)
        ],
        "tran_id string, part_tran_srl_num string, tran_date date, cif_id string,"
        " foracid string, value_date date, edp_load_date date, tran_dc string,"
        " channel_desc string, merchant_type_desc string, tran_particular_code_desc string,"
        " reason_for_excluding string, merchant_category string, merchant_name string,"
        " merchant_country string, counter_party_bank_cntry string,"
        " tran_narration_1 string, actual_tran_amt_aed double",
    )  # fmt: skip
    cards = build_card_transactions(comp, START, 36)

    transactions = spark.createDataFrame(
        [
            (f"K{c}", d, di, cat, mcc, intl, desc)
            for c, d, di, cat, mcc, intl, desc in CREDIT
        ],
        "contract_id string, observation_date date, direction int, txn_category string,"
        " merchant_category_code string, is_international int, txn_description string",
    )
    contract_rows = [(f"K{c}", f"L{c}", date(2026, 7, 9), None) for c in CASES]
    contract_rows += [(f"K{c}", f"L{c}", d, b) for c, d, b in WAY4]
    contracts = spark.createDataFrame(
        contract_rows,
        "contract_id string, client_id string, observation_date date, block_code_2 string",
    )
    clients = spark.createDataFrame(
        [(f"L{c}", cif(c)) for c in CASES], "client_id string, cif_id string"
    )
    spine = spark.createDataFrame(
        [(int(i), 9000 + i, cif(c), date(2026, 7, 9)) for i, c in enumerate(CASES)],
        "account_id long, agreement_id long, cif_id string, observation_date date",
    )
    # the spine's account ids are the obs base's: A<case> ↔ i
    index = {c: i for i, c in enumerate(CASES)}
    spine = spine.selectExpr(
        "agreement_id", "cif_id", "observation_date",
        "concat('A', element_at(array(" + ",".join(f"'{c}'" for c in CASES)
        + "), int(account_id) + 1)) as account_id",
    )  # fmt: skip
    agreements = prm_dcore_account_agreements.build(spine)
    followup = spark.createDataFrame(
        [(9000 + index[c], t, code, cat, name) for c, t, code, cat, name in DCORE],
        "agreement_id long, action_ts timestamp, action_code string,"
        " result_category string, result_name string",
    )
    demographics = spark.createDataFrame(
        [(cif(c), 1 if c == "D4" else 0) for c in CASES],
        "cif_id string, ft_deceased_flag int",
    )

    feature = feat_cif_location_monthly.build(
        logins, cards, transactions, contracts, clients, followup, agreements, START, 36
    )
    out = build_a2_locatability(
        obs_base,
        build_location_signals(obs_base, feature, MODEL),
        build_dcore_signals(obs_base, followup, agreements, MODEL),
        build_way4_deceased(obs_base, contracts, clients),
        build_demographics_deceased(obs_base, demographics),
        MODEL,
        str(OBS),
    )
    rows = {r["account_id"][1:]: r for r in out.collect()}

    bad = 0
    for case, (rule, reach, deceased) in CASES.items():
        r = rows[case]
        got = (r["location_rule"], r["reachability_state"], r["deceased_source"])
        ok = got == (rule, reach, deceased)
        ok &= r["location_unknown_reason"] == UNKNOWN_REASON.get(
            case, r["location_unknown_reason"]
        )
        ok &= r["reachability_unknown_reason"] == REACH_REASON.get(
            case, r["reachability_unknown_reason"]
        )
        bad += not ok
        print(
            f"{'ok ' if ok else 'BAD'} {case}  {r['a2_state']:<28} {r['location_rule']}"
            f"  uae={r['last_uae_date']} ({r['last_uae_source']})"
            f"  foreign={r['last_foreign_date']} ({r['last_foreign_source']})"
            f"  travel={r['last_travel_date']}  reach={r['reachability_unknown_reason']}"
            f"  deceased={r['deceased_source']}  label={r['a2_state_label']}"
        )
    print(f"\n{len(CASES) - bad}/{len(CASES)} cases pass")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
