"""Local spec test for the point-in-time CIF of card contracts (``prm_card_contracts``)
and the F4 card rows built on it (``feat_cif_cross_product`` ``_cards``).

    python workplace_mirror/checks/card_cif_spec.py      (needs pyspark + Java 17)

Rule (user, 2026-11-18; summary ``bundle_helpers/a1_final/card_cif_summary_cc_60_180.md``):
a card counts for the CIF that held its contract at the month end. The contract's client
comes from the contract log (``record_date_from``), that client's CIF from the client log
(``edp_effectivestartdate``); on one day the latest ``edp_modifiedts`` wins.
"""

import os
import pathlib
import sys
from datetime import date, datetime

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path.insert(0, str(HERE.parent / "src"))
sys.path.insert(0, str(HERE))

import golden_inputs as gi  # noqa: E402

gi.install_workplace_stubs()

from pyspark.sql import SparkSession  # noqa: E402

from enbd_collections.nodes.features.products.feat_cif_cross_product import (  # noqa: E402
    _cards,
)
from enbd_collections.nodes.primary.products.prm_products import (  # noqa: E402
    build_card_contracts,
)

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
D, T = date, datetime
FAILS = []


def check(name, got, want):
    ok = got == want
    print(f"{'ok  ' if ok else 'FAIL'} {name}: {got}" + ("" if ok else f" != {want}"))
    if not ok:
        FAILS.append(name)


# Clients: 1 -> CIF 100 throughout (two log rows, no change); 2 -> CIF 200, then 201 from
# 2023-03-10; 3 -> CIF 300; 4: two rows on one day, the later edp_modifiedts (CIF 401) wins.
client = spark.createDataFrame(
    [
        (1, "100", T(2019, 1, 1), T(2019, 1, 1, 9)),
        (1, "100", T(2021, 5, 1), T(2021, 5, 1, 9)),
        (2, "200", T(2019, 1, 1), T(2019, 1, 1, 9)),
        (2, " 201", T(2023, 3, 10), T(2023, 3, 10, 9)),
        (3, "300", T(2019, 1, 1), T(2019, 1, 1, 9)),
        (4, "400", T(2020, 1, 1), T(2020, 1, 1, 9)),
        (4, "401", T(2020, 1, 1), T(2020, 1, 1, 11)),
    ],
    "client_idt long, ident_number string, edp_effectivestartdate timestamp,"
    " edp_modifiedts timestamp",
)
# Contracts: 10 stays with client 1; 20 with client 2 (its CIF changes); 30 moves from
# client 1 to 3 on 2024-06-15 and back to 1 on 2024-09-01; 40 with client 4, child of 10;
# 50 has no known client.
contract = spark.createDataFrame(
    [
        (10.0, 1, None, T(2019, 2, 1), T(2019, 2, 1, 9)),
        (10.0, 1, None, T(2022, 2, 1), T(2022, 2, 1, 9)),
        (20.0, 2, None, T(2019, 2, 1), T(2019, 2, 1, 9)),
        (30.0, 1, None, T(2019, 2, 1), T(2019, 2, 1, 9)),
        (30.0, 3, None, T(2024, 6, 15), T(2024, 6, 15, 9)),
        (30.0, 1, None, T(2024, 9, 1), T(2024, 9, 1, 9)),
        (40.0, 4, 10.0, T(2020, 2, 1), T(2020, 2, 1, 9)),
        (50.0, 9, None, T(2020, 2, 1), T(2020, 2, 1, 9)),
    ],
    "contract_idt double, client_idt long, parent_contract_idt double,"
    " record_date_from timestamp, edp_modifiedts timestamp",
)
spans = build_card_contracts(client, contract)
check(
    "spans",
    sorted(  # by contract, CIF and start (NULL start = from the first record)
        [(r["contract_id"], r["cif_id"], r["parent_contract_id"], r["valid_from"],
          r["valid_to"]) for r in spans.collect()],
        key=lambda t: (t[0], t[1], t[3] or D.min),
    ),
    [
        (10, "100", None, None, None),
        (20, "200", None, None, D(2023, 3, 10)),
        (20, "201", None, D(2023, 3, 10), None),
        (30, "100", None, None, D(2024, 6, 15)),
        (30, "100", None, D(2024, 9, 1), None),
        (30, "300", None, D(2024, 6, 15), D(2024, 9, 1)),
        (40, "401", 10, None, None),
    ],
)  # fmt: skip

month_end = spark.createDataFrame(
    [
        (20, D(2023, 2, 28), 1, 50.0),
        (20, D(2023, 3, 31), 1, 50.0),
        (30, D(2024, 5, 31), 1, 70.0),
        (30, D(2024, 6, 30), 1, 70.0),
        (30, D(2024, 8, 31), 1, 70.0),
        (30, D(2024, 9, 30), 1, 70.0),
        (40, D(2026, 7, 31), 1, 90.0),
        (50, D(2026, 7, 31), 1, 90.0),
    ],
    "contract_id long, month_end date, level int, minimum_due double",
)
check(
    "cards: one CIF per contract and month end",
    sorted(
        (r["product_account_id"], r["month_end"], r["cif_id"], r["linked_account_id"])
        for r in _cards(spans, month_end).collect()
    ),
    [
        ("20", D(2023, 2, 28), "200", None),
        ("20", D(2023, 3, 31), "201", None),
        ("30", D(2024, 5, 31), "100", None),
        ("30", D(2024, 6, 30), "300", None),
        ("30", D(2024, 8, 31), "300", None),
        ("30", D(2024, 9, 30), "100", None),
        ("40", D(2026, 7, 31), "401", "10"),
    ],
)

print("card cif spec:", "FAIL " + ", ".join(FAILS) if FAILS else "all checks pass")
sys.exit(1 if FAILS else 0)
