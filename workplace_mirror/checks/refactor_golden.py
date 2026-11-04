"""Golden outputs of the live crx_persona pipelines (refactor gate 4, PLAN §5 Phase 0).

    JAVA_HOME=/opt/homebrew/opt/openjdk@17 \
        python workplace_mirror/checks/refactor_golden.py [--record]

Runs every tier-L pipeline (obs bases, A1, A2, full histories + A4; CC and RL) through
Kedro's SequentialRunner on small synthetic inputs, once per model_id, and checks every
dataset the pipelines write:

* ``--record`` saves ``refactor_review/00_baseline/golden/<run>/<dataset>.parquet``
  (gitignored), ``manifest.json`` (rows, schema, order-independent hash per dataset) and
  ``harness_coverage.md`` (which states and rule branches the inputs reach);
* the default compares schema and rows (``exceptAll`` both ways) with the parquet, or
  with the manifest hash when the parquet is absent, and exits 1 naming the dataset
  and example rows.

Inputs: A1 = the cases of ``a1_engine_spec.py`` (executed for its feature frames);
A2 = the cases of ``a2_engine_spec.py`` (captured from its ``main``); A4 = the journeys
below, one per state and per history rule. ``computed_at`` (the run clock) is ignored.
Three guard runs must fail: a mid-month RL spine, a missing required column, an unknown
dpd_journey key.
"""

import contextlib
import datetime as dt
import functools
import hashlib
import io
import json
import logging
import os
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

from kedro.io import DataCatalog, MemoryDataset  # noqa: E402
from kedro.runner import SequentialRunner  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .config("spark.ui.showConsoleProgress", "false")
    .config("spark.sql.session.timeZone", "UTC")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("kedro").setLevel(logging.CRITICAL)  # the guard runs log their errors

from enbd_collections.pipelines.crx_persona import (  # noqa: E402
    cc_a1_ability,
    cc_a2_locatability,
    obs_base,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a4_deterioration,
    rl_full_history,
)
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration import (  # noqa: E402
    pipeline as cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona.cc_full_history import (  # noqa: E402
    pipeline as cc_full_history,
)

import a2_engine_spec  # noqa: E402
from a4_chain_spec import month_end  # noqa: E402

OUT = HERE.parent / "refactor_review" / "00_baseline"
GOLDEN = OUT / "golden"
IGNORED = ["computed_at"]
CC_MODELS, RL_MODELS = ("cc_60_180", "cc_180_plus"), ("rl_60_180", "rl_180_plus")
df = spark.createDataFrame


# ── A1 and A2: the spec tests' cases ──────────────────────────────────────────


@functools.cache
def a1_inputs() -> tuple[dict, dict, dict]:
    """CC inputs, RL inputs and the persona dates of the A1 spec cases, plus a few
    obs-base rows: two billing dates in one month with different CIFs, a row without a
    CIF and one before the persona months."""
    ns: dict = {
        "__name__": "a1_engine_spec",
        "__file__": str(HERE / "a1_engine_spec.py"),
    }
    code = compile((HERE / "a1_engine_spec.py").read_text(), ns["__file__"], "exec")
    # the spec gate reports a failure; the frames are built before its asserts
    with contextlib.redirect_stdout(io.StringIO()), contextlib.suppress(
        SystemExit, AssertionError
    ):
        exec(code, ns)  # pylint: disable=exec-used
    obs = ns["OBS"]
    extra = [
        ("Z1", dt.date(2026, 7, 3), 5000),
        ("Z1", dt.date(2026, 7, 28), 5001),
        ("Z2", obs, None),
        ("Z3", dt.date(2026, 5, 31), 5003),
    ]
    spine = ns["rows"]["spine"] + extra
    shared = {
        "feat_cif_internal_salary_monthly": ns["internal_salary"],
        "feat_cif_bureau_salary_monthly": ns["bureau_salary"],
        "feat_cif_casa_balance_monthly": ns["casa_balance"],
        "feat_cif_ext_card_payment_monthly": ns["payments"],
        "feat_cif_casa_activity_monthly": ns["activity"],
        "feat_cif_returns_monthly": ns["returns"],
        "feat_cif_bureau_bounces_monthly": ns["bounces"],
        "dcore_prm_followup_outcomes": ns["followup"],
        "prm_dcore_account_agreements": ns["agreements"],
    }
    cc = {
        **shared,
        "cc_spine": df(spine, "contract_id string, observation_date date, cif_id long"),
        "prm_balance": ns["balance"],
    }
    june = dt.date(2026, 6, 30)
    rl = {
        **shared,
        "rl_spine": df(
            [r for r in spine if r[1] == obs],
            "account_id string, observation_date date, cif_id long",
        ),
        "int_loan_master": df(
            [
                ("A0", obs, 2000.0),
                ("A1", obs, 0.0),
                ("A2", june, 1500.0),
                ("A6", obs, 3000.0),
            ],
            "account_id string, observation_date date, installment_due_amount double",
        ),
        "feature_retail_loans": df(
            [
                ("A0", obs, ns["m"](2, 10), 6000.0),
                ("A1", obs, ns["m"](0, 5), 7000.0),
                ("A5", obs, ns["m"](1, 10), 2500.0),
            ],
            "account_id string, observation_date date, aecb_bureau_pull_date date,"
            " aecb_last_salary_credit_amount double",
        ),
    }
    return cc, rl, ns["PERSONA"]


COMBOS = {
    "AX1": ("01", "R7"),
    "AX2": ("02", "R1"),
    "AX3": ("01", "R1"),
    "AX4": ("02", "R7"),
}


@functools.cache
def a2_inputs() -> tuple[dict, dict]:
    """CC and RL inputs of the A2 spec cases (``main`` runs once with the signal
    builders wrapped to keep their first inputs), plus the ``COMBOS`` accounts."""
    seen: dict = {}

    def keep(name):
        real = getattr(a2_engine_spec, name)

        def wrapper(*args):
            seen.setdefault(name, args)
            return real(*args)

        setattr(a2_engine_spec, name, wrapper)

    for name in (
        "build_location_signals",
        "build_dcore_signals",
        "build_way4_deceased",
        "build_demographics_deceased",
    ):
        keep(name)
    with contextlib.redirect_stdout(io.StringIO()):
        a2_engine_spec.main()
    base, features, _ = seen["build_location_signals"]
    _, followup, agreements, _ = seen["build_dcore_signals"]
    _, contracts, clients = seen["build_way4_deceased"]
    # location × reachability pairs no case has: one case's customer, another's calls
    for account, (place, calls) in COMBOS.items():
        base = base.unionByName(
            base.filter(F.col("account_id") == f"A{place}").withColumn(
                "account_id", F.lit(account)
            )
        )
        agreements = agreements.unionByName(
            agreements.filter(F.col("account_id") == f"A{calls}").withColumn(
                "account_id", F.lit(account)
            )
        )
    shared = {
        "feat_cif_location_monthly": features,
        "dcore_prm_followup_outcomes": followup,
        "prm_dcore_account_agreements": agreements,
        "prm_contract": contracts,
        "prm_client": clients,
        "feat_demographics_cif": seen["build_demographics_deceased"][1],
    }
    spine = base.select("account_id", "observation_date", "cif_id")
    return (
        {**shared, "cc_spine": spine.withColumnRenamed("account_id", "contract_id")},
        {**shared, "rl_spine": spine},
    )


# ── A4: one journey per state and per history rule ────────────────────────────
# Month i = month_end(i) (0 = Jan 2024); the persona ends in month 29 (Jun 2026).
# Buckets are CC native (canonical); None = no row that month. RL uses canonical - 1.
END = 29
JOURNEYS = {  # account: (first month, buckets, what it exercises)
    0: (-8, [1] * 38, "clean all along: not classified; earliest source month"),
    1: (24, [1, 1, 2, 3, 4, 5], "early_payment_default"),
    2: (
        12,
        [1, 1, None, 1, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5],
        "stabilized; gap filled",
    ),
    3: (10, [1] * 6 + [2, 3] + [1] * 4 + [2, 3, 4, 5, 6, 7, 7, 7], "repeat_delinquent"),
    4: (
        8,
        [1] * 16 + [2, 3, 4, None, 6, 7],
        "straight_roller_seasoned; straight-roll gap",
    ),
    5: (18, [1] * 6 + [2, 3, 4, 5, 6, 7], "straight_roller_early_life"),
    6: (16, [1] * 6 + [2, 2, 3, 3, 4, 5, 6, 7], "slow_roller"),
    7: (
        -3,
        [3, 4, 5, 6, 7, 8] + [9] * 27,
        "unknown: history before the CC floor (cropped)",
    ),
    8: (20, [5] * 10, "Q0 stabilized: CC opened delinquent (restructure blind spot)"),
    9: (
        14,
        [1, 1, 1, 4, 1, 1, 2, 3, 3, 5, 6, None, 4, 5, 6, 7],
        "glitch, +2 jump (repaired on CC), inferred gap",
    ),
    10: (
        10,
        [1] * 5 + [None] * 4 + [4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9],
        "unresolvable gap: truncated, or dropped (alt run)",
    ),
}
SPINE_MONTHS = {
    2: [27],
    7: [1],
    5: [17],
    1: [31],
}  # extra rows: earlier / outside history
A4_PERSONA = {
    "persona_start_date": "2026-01-01",
    "persona_end_date": str(month_end(END)),
}
ALT = {  # every dpd_journey switch flipped
    "cc_history_floor_date": None,
    "rl_history_floor_date": "2024-01-01",
    "on_unresolvable_gap": "drop",
    "fill_straight_roll_gaps": False,
    "repair_cycle_shift": False,
    "max_inferred_gap_months": 0,
    "log_stats": True,
}


def _months(first, buckets):
    for i, b in enumerate(buckets):
        if b is not None:
            yield first + i, b


@functools.cache
def cc_a4_inputs() -> dict:
    """raw_stg_billing + cc_spine (mid-month billing dates). Beyond JOURNEYS: account 11
    has a cycle shift (two bills in a month next to an empty one) and two bills in a
    month with both neighbours present; 12 has no valid bucket (none, out of range,
    NULL); 13 has rows only before the floor; 99 is not on the spine; 4 has two rows on
    one date."""
    rows = [
        (a, month_end(i).replace(day=15), f"X;BS_PMT_CYCLE_DUE={b}")
        for a, (first, buckets, _) in JOURNEYS.items()
        for i, b in _months(first, buckets)
    ]
    shift = [1] * 4 + [None, 1] + [1] * 4 + [2, 3, 4, 5]  # months 16..29, 20 empty
    rows += [
        (11, month_end(i).replace(day=15), f"BS_PMT_CYCLE_DUE={b}")
        for i, b in _months(16, shift)
    ]
    rows += [
        (11, month_end(21).replace(day=1), "BS_PMT_CYCLE_DUE=1"),  # moves to month 20
        (11, month_end(25).replace(day=2), "BS_PMT_CYCLE_DUE=1"),  # duplicate month
        (12, month_end(25).replace(day=15), "NO_BUCKET"),
        (13, month_end(-6).replace(day=15), "BS_PMT_CYCLE_DUE=4"),
        (99, month_end(28).replace(day=15), "BS_PMT_CYCLE_DUE=5"),
        (12, month_end(22).replace(day=15), "BS_PMT_CYCLE_DUE=12"),  # out of range
        (12, month_end(23).replace(day=15), None),
        (4, month_end(9).replace(day=15), "BS_PMT_CYCLE_DUE=0"),  # same date as a 1
    ]
    billing = df(
        [(float(a), d, info) for a, d, info in rows],
        "contract_idt double, billing_date date, add_info string",
    ).withColumn(
        "billing_date", F.col("billing_date").cast("timestamp")
    )  # UTC midnight
    accounts = [*JOURNEYS, 11, 12, 13]
    spine = [(a, month_end(END).replace(day=12), f"C{a}") for a in accounts]
    spine += [(a, month_end(i), f"C{a}") for a, ms in SPINE_MONTHS.items() for i in ms]
    return {
        "raw_stg_billing": billing,
        "cc_spine": df(spine, "contract_id long, observation_date date, cif_id string"),
    }


@functools.cache
def rl_a4_inputs() -> dict:
    """int_loan_master, rl_spine, int_loan_restructure_link, feature_retail_loans.
    JOURNEYS on the RL scale (canonical 9 caps at RL 7; L7 starts in the source's first
    month, so it is the cropped one), plus the chain cases of a4_chain_spec: L20 linked,
    L21 linked late (the row before the link reads its own history), L22 restructured
    with no original (blind), L23 raw flag only, L24 a chain of two originals."""

    def rl(buckets):
        return [None if b is None else min(max(b - 1, 0), 7) for b in buckets]

    journeys = {
        f"L{a}": (first, rl(buckets)) for a, (first, buckets, _) in JOURNEYS.items()
    }
    journeys["L7"] = (-12, rl([3] * 9 + JOURNEYS[7][1]))  # the earliest source month
    journeys |= {
        "L20": (26, [0, 1, 2, 3]),
        "L21": (26, [0, 1, 2, 3]),
        "L22": (25, [2, 2, 2, 2, 3]),
        "L23": (26, [0, 1, 2, 3]),
        "L24": (27, [1, 2, 3]),
        "O20": (10, [0] * 15 + [1, 2, 3]),
        "O21": (10, [0] * 15 + [1, 2, 3]),
        "O24a": (14, [0] * 10 + [1, 2]),
        "O24b": (8, [0] * 6 + [1, 1, 0]),
    }
    closed = {("O20", 28), ("O21", 28), ("O24a", 27)}
    master = [
        (
            f"C{a}",
            a,
            month_end(i),
            b,
            1.0,
            1000.0,
            int(a == "L23"),
            "Personal",
            "ACTIVE",
        )
        for a, (first, buckets) in journeys.items()
        for i, b in _months(first, buckets)
    ] + [
        (f"C{a}", a, month_end(i), 0, 1.0, 0.0, 0, "Personal", "CLOSED")
        for a, i in closed
    ]
    on_spine = [a for a in journeys if a.startswith("L")]
    spine = [(a, month_end(END), f"C{a}") for a in on_spine]
    spine += [
        (f"L{a}", month_end(i), f"CL{a}") for a, ms in SPINE_MONTHS.items() for i in ms
    ]
    spine += [("L21", month_end(28), "CL21")]
    link = [
        ("L20", "O20", month_end(28), month_end(28), "one_to_one", 1),
        ("L21", "O21", month_end(29), month_end(28), "one_to_one", 1),
        ("L22", None, month_end(29), None, None, 0),
        ("L24", "O24a", month_end(27), month_end(27), "one_to_one", 1),
        ("O24a", "O24b", month_end(17), month_end(16), "many_to_one", 3),
    ]
    flagged = {"L8", "L20", "L21", "L22", "L24"}
    return {
        "int_loan_master": df(
            master,
            "cif_id string, account_id string, observation_date date,"
            " dpd_bucket int, emi_coverage_ratio double, outstanding_balance"
            " double, is_restructured int, loan_type string,"
            " account_status string",
        ),
        "rl_spine": df(
            spine, "account_id string, observation_date date, cif_id string"
        ),
        "int_loan_restructure_link": df(
            link,
            "account_id string, orig_account_id string,"
            " restr_flagged_date date, orig_close_date date,"
            " match_type string, candidate_count int",
        ),
        "feature_retail_loans": df(
            [(a, month_end(END), int(a in flagged)) for a in on_spine],
            "account_id string, observation_date date,"
            " has_restructured_loan_flag int",
        ),
    }


# ── Runs ──────────────────────────────────────────────────────────────────────


PRODUCTS = {  # models, obs base, A1, A2, full history, A4
    "cc": (CC_MODELS, obs_base.create_cc_pipeline, cc_a1_ability, cc_a2_locatability,
           cc_full_history, cc_a4_deterioration),
    "rl": (RL_MODELS, obs_base.create_rl_pipeline, rl_a1_ability, rl_a2_locatability,
           rl_full_history, rl_a4_deterioration),
}  # fmt: skip


def runs() -> list[tuple[str, object, str, dict, dict]]:
    """(run name, pipeline, model_id, crx_persona, inputs): each product's A1, A2 and A4
    per model_id, and A4 once more with ``ALT``."""
    a1_cc, a1_rl, persona = a1_inputs()
    a2_cc, a2_rl = a2_inputs()
    inputs = {
        "cc": (a1_cc, a2_cc, cc_a4_inputs()),
        "rl": (a1_rl, a2_rl, rl_a4_inputs()),
    }
    out = []
    for product, (models, obs, a1, a2, history, a4) in PRODUCTS.items():
        in_a1, in_a2, in_a4 = inputs[product]
        journey = history.create_pipeline() + a4.create_pipeline()
        for m in models:
            out += [
                (f"crx_{product}_a1_ability.{m}", obs() + a1.create_pipeline(), m,
                 persona, in_a1),
                (f"crx_{product}_a2_locatability.{m}", obs() + a2.create_pipeline(), m,
                 persona, in_a2),
                (f"crx_{product}_a4_deterioration.{m}", journey, m, A4_PERSONA, in_a4),
            ]  # fmt: skip
        alt = {**A4_PERSONA, "dpd_journey": ALT}
        out.append(
            (f"crx_{product}_a4_deterioration.{models[0]}_alt", journey, models[0], alt,
             in_a4)
        )  # fmt: skip
    return out


def guards(persona: dict, a1_cc: dict) -> list[tuple[str, object, str, dict, dict]]:
    """Runs that must raise."""
    bad_spine = df(
        [("X", dt.date(2026, 7, 15), 1)],
        "account_id string, observation_date date, cif_id long",
    )
    no_bucket = {**a1_cc, "prm_balance": a1_cc["prm_balance"].drop("overdue_bucket_06")}
    stale_key = {**A4_PERSONA, "dpd_journey": {"det_option": 1}}
    cc_journey = (
        cc_full_history.create_pipeline() + cc_a4_deterioration.create_pipeline()
    )
    return [
        ("mid-month RL spine", obs_base.create_rl_pipeline(), "rl_60_180", persona,
         {"rl_spine": bad_spine}),
        ("prm_balance without overdue_bucket_06", obs_base.create_cc_pipeline()
         + cc_a1_ability.create_pipeline(), "cc_60_180", persona, no_bucket),
        ("unknown dpd_journey key", cc_journey, "cc_60_180", stale_key, cc_a4_inputs()),
    ]  # fmt: skip


class _Kept(MemoryDataset):
    """A MemoryDataset the runner cannot release, so intermediates can be read after."""

    def _release(self) -> None:
        pass


def run_pipeline(pipeline, model_id: str, persona: dict, inputs: dict) -> dict:
    """Every dataset ``pipeline`` writes, run on MemoryDatasets."""
    params = {"model_id": model_id, "crx_persona": persona}
    data = {}
    for name in pipeline.datasets():
        if name.startswith("params:"):
            value = params
            for part in name[len("params:") :].split("."):
                value = value[part]
            data[name] = value
        elif name in pipeline.inputs():
            data[name] = inputs[name]
    datasets = {n: MemoryDataset(v, copy_mode="assign") for n, v in data.items()}
    datasets |= {n: _Kept(copy_mode="assign") for n in pipeline.all_outputs()}
    catalog = DataCatalog(datasets)
    SequentialRunner().run(pipeline, catalog)
    return {n: catalog.load(n).drop(*IGNORED) for n in sorted(pipeline.all_outputs())}


# ── Record / compare ──────────────────────────────────────────────────────────


def schema(frame) -> list[list[str]]:
    return [[f.name, f.dataType.simpleString()] for f in frame.schema.fields]


def content_hash(frame) -> str:
    return hashlib.sha256(
        "\n".join(sorted(frame.toJSON().collect())).encode()
    ).hexdigest()


def compare(
    name: str, frame, golden_path: pathlib.Path, entry: dict | None
) -> list[str]:
    """Differences between ``frame`` and its golden copy, as report lines."""
    if entry is None:
        return [f"{name}: not in the manifest"]
    if schema(frame) != entry["schema"]:
        return [f"{name}: schema {schema(frame)} != golden {entry['schema']}"]
    if not golden_path.exists():
        same = content_hash(frame) == entry["hash"]
        return [] if same else [f"{name}: content hash differs (no parquet to diff)"]
    golden = spark.read.parquet(str(golden_path)).select(*frame.columns)
    golden = golden.select([F.col(c).cast(t) for c, t in entry["schema"]])
    lines = []
    for label, a, b in (("new only", frame, golden), ("golden only", golden, frame)):
        extra = a.exceptAll(b)
        n = extra.count()
        if n:
            lines.append(f"{name}: {n} {label} rows, e.g.")
            lines += [f"    {r.asDict()}" for r in extra.limit(3).collect()]
    return lines


# Columns whose values show which rule branches the inputs reach.
STATE_COLUMNS = {
    "a1_ability": {
        "a1_state": ["high", "moderate", "low", "unknown"],
        "a1_income_level": ["stable", "weak", "none"],
        "a1_liquidity_level": ["adequate", "weak", "none"],
        "a1_unknown_reason": ["no_casa", "dormant_casa"],
        "a1_income_source": ["internal", "bureau", "both", "none"],
        "a1_points_total": [0, 1, 2, 3, 4],
        "a1_distress_flag": [0, 1],
        "a1_eosb_flag": [0, 1],
        "a1_salary_stopped": [0, 1],
    },
    "a1_distress_signals": {
        "distress_cheque": [0, 1],
        "distress_dds": [0, 1],
        "distress_bureau": [0, 1],
    },
    "a1_liquidity_anchor": {"liquidity_anchor_amt": ["NULL", "value"]},
    "a2_locatability": {
        "location_rule": ["L1", "L2", "L3", "L4"],
        "location_unknown_reason": ["no_evidence", "domestic_before_window"],
        "reachability_state": ["reachable", "non_reachable", "unknown"],
        "reachability_unknown_reason": ["no_dcore_record", "no_contact_in_window"],
        "deceased_source": ["dcore", "way4", "demographics"],
        "a2_state": ["deceased"]
        + [
            f"{loc}__{r}"
            for loc in ("skip", "in_country", "unknown")
            for r in ("reachable", "non_reachable", "unknown")
        ],
    },
    "dpd_sequences": {
        "build_status": [
            "ok",
            "no_valid_rows",
            "no_rows_in_window",
            "dropped_unresolvable_gap",
        ],
        "history_cropped": [True, False],
        "restructure_blind_spot_flag": [0, 1],
        "legacy_drop": [True, False],
    },
    "a4_deterioration": {
        "det_state": [
            "unknown",
            "early_payment_default",
            "stabilized",
            "repeat_delinquent",
            "straight_roller_seasoned",
            "straight_roller_early_life",
            "slow_roller",
        ],
        "restructure_blind_spot_flag": [0, 1],
        "chain_stitched_flag": [0, 1],
    },
    "restructure_chains": {"chain_n_originals": [1, 2]},
}
# Counters of a history rule: covered when some row is above 0.
RULE_COUNTERS = {
    "dpd_sequences": [
        "n_gap_months_filled",
        "n_gap_months_rolled",
        "n_gap_months_inferred",
        "n_cycle_shift_moves",
        "n_months_truncated",
        "n_dup_month_rows",
        "n_invalid_rows",
    ],
    "a4_deterioration": [
        "n_glitches",
        "n_jumps_repaired",
        "n_jumps_left",
        "n_blips",
        "n_prior_episodes",
    ],
}


def coverage(name: str, frame) -> dict[str, set]:
    """Values the state columns of dataset ``name`` take, and counters above 0."""
    kind = name.split("_", 2)[-1]
    seen = {}
    for col in [c for c in STATE_COLUMNS.get(kind, {}) if c in frame.columns]:
        values = {r[0] for r in frame.select(col).distinct().collect()}
        if col == "liquidity_anchor_amt":
            values = {"NULL" if v is None else "value" for v in values}
        if col == "deceased_source":
            values = {s for v in values if v for s in v.split(",")}
        seen[col] = values
    for col in RULE_COUNTERS.get(kind, []):
        if frame.filter(F.col(col).cast("int") > 0).limit(1).count():
            seen.setdefault("rule counters > 0", set()).add(col)
    return seen


# Branches the outputs above cannot show.
NOT_COVERED = [
    "A1 `build_distress_signals(payment_order=...)`: the optional"
    " prm_bureau_payment_order source is not wired in any pipeline (not in PROD).",
    "`dpd_journey.cc_history_floor_date_180_plus` set apart from the 60-180 floor (same"
    " default; the alt run changes only the shared keys).",
    "`log_stats` / `log_latest_month` / `_log_state_stats`: logging only, run but not"
    " checked; `_ship_by_value` pickling matters on real executors only.",
    "Guards (must raise, checked by exception type only): mid-month RL spine, a missing"
    " required column, an unknown dpd_journey key; the returns-coverage guard of"
    " `build_distress_signals` is checked by a1_engine_spec.py.",
]


def write_coverage(seen: dict) -> None:
    """``harness_coverage.md``: values reached per dataset kind, and what is not."""
    lines = [
        "# Golden harness coverage",
        "",
        "Generated by `checks/refactor_golden.py --record`. Per output kind (CC and",
        "RL, all model_ids together): the values each state column reaches, then the",
        "ones it does not.",
        "",
    ]
    for kind in sorted(seen):
        lines.append(f"## {kind}")
        lines.append("")
        expected = {**STATE_COLUMNS.get(kind, {})}
        if kind in RULE_COUNTERS:
            expected["rule counters > 0"] = RULE_COUNTERS[kind]
        for col, values in expected.items():
            got = seen[kind].get(col, set())
            missing = [v for v in values if v not in got]
            note = (
                f" — **not reached: {', '.join(map(str, missing))}**" if missing else ""
            )
            lines.append(
                f"- `{col}`: {', '.join(str(v) for v in values if v in got)}{note}"
            )
        lines.append("")
    lines += ["## Not covered by the outputs", "", *[f"- {n}" for n in NOT_COVERED], ""]
    (OUT / "harness_coverage.md").write_text("\n".join(lines))


def main() -> int:
    record = "--record" in sys.argv
    manifest_path = OUT / "manifest.json"
    manifest = {} if record else json.loads(manifest_path.read_text())
    problems, seen = [], {}
    for run, pipeline, model_id, persona, inputs in runs():
        start = time.perf_counter()
        outputs = run_pipeline(pipeline, model_id, persona, inputs)
        for name, frame in outputs.items():
            frame = frame.persist()
            path = GOLDEN / run / f"{name}.parquet"
            kind = name.split("_", 2)[-1]
            for col, values in coverage(name, frame).items():
                seen.setdefault(kind, {}).setdefault(col, set()).update(values)
            if record:
                frame.coalesce(1).write.mode("overwrite").parquet(str(path))
                manifest.setdefault(run, {})[name] = {
                    "rows": frame.count(),
                    "schema": schema(frame),
                    "hash": content_hash(frame),
                }
            else:
                problems += compare(
                    f"{run}/{name}", frame, path, manifest.get(run, {}).get(name)
                )
            frame.unpersist()
        print(
            f"{run:<45} {len(outputs):>2} datasets  {time.perf_counter() - start:5.1f}s"
        )
    a1_cc, _, persona = a1_inputs()
    for label, pipeline, model_id, params, inputs in guards(persona, a1_cc):
        try:
            run_pipeline(pipeline, model_id, params, inputs)
            problems.append(f"guard did not fire: {label}")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"guard ok: {label} ({type(exc).__name__})")
    if record:
        manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
        write_coverage(seen)
        print(f"recorded {sum(map(len, manifest.values()))} datasets to {GOLDEN}")
    for line in problems:
        print(f"DIFF {line}")
    print("golden: " + ("FAIL" if problems else "pass"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
