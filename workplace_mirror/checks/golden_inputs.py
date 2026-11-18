"""Synthetic inputs of the behaviour oracle (``refactor_golden.py``).

One builder per area; each returns ``{dataset name: DataFrame}`` (cached, built once).

* A1: the cases of ``a1_engine_spec.py`` (its feature frames, built through the real
  CASA / bureau feature builders), plus a few obs-base rows and RL loan snapshots.
* A2: the cases of ``a2_engine_spec.py`` (captured from its ``main``) and four
  location x reachability pairs no case has.
* A4: one journey per state and per history rule (run 1's cases).
* A3: ``A3_CASES``, one account per rule branch, turned into the raw Way4 extracts
  (CC, through ``crx_cc_raw_extract``), the loan snapshots (RL) and the DCORE tables.
* Products and bureau: raw rows for ``product_primary`` + ``product_features`` and
  ``bureau_salary_bounces``.

``install_workplace_stubs()`` must run before any persona module is imported: the DCORE
helpers, Way4's ``prm_cc`` derivations and one ``config`` constant are not mirrored.
The stand-ins are simple and deterministic; the oracle checks our code, not theirs.
"""

# pylint: disable=too-many-lines
import contextlib
import datetime as dt
import functools
import io
import pathlib
import sys
import types

from pyspark.sql import DataFrame, SparkSession
from pyspark.sql import functions as F

HERE = pathlib.Path(__file__).resolve().parent
D = dt.date


def spark() -> SparkSession:
    return SparkSession.builder.getOrCreate()


def df(rows, schema: str) -> DataFrame:
    return spark().createDataFrame(rows, schema)


# ── Stand-ins for workplace modules the mirror does not hold ──────────────────

# raw_stg_account_group ids of the stand-in prm_cc derivations (sign flipped as Way4)
ACCOUNT_GROUPS = {1: "MIN_DUE", 2: "STMT_BAL", 3: "TOTAL_DUE"} | {
    10 + k: f"OVD_{k:02d}" for k in range(1, 9)
}


def _pivot_balance(
    balance: DataFrame, account_group: DataFrame, codes: dict
) -> DataFrame:
    """Per ``(contract_idt, banking_date)``: ``-sum(balance)`` of each type code, 0 when
    absent (Way4 writes an empty bucket as 0)."""
    rows = balance.join(account_group, "account_group_id").withColumn(
        "contract_idt", F.col("contract_idt").cast("long")
    )
    out = rows.groupBy("contract_idt", "banking_date").agg(
        *[
            F.coalesce(
                -F.sum(F.when(F.col("type_code") == code, F.col("balance"))), F.lit(0.0)
            ).alias(name)
            for code, name in codes.items()
        ]
    )
    return out


def _derive_billing_amounts(balance: DataFrame, account_group: DataFrame) -> DataFrame:
    return _pivot_balance(
        balance,
        account_group,
        {
            "MIN_DUE": "minimum_due",
            "STMT_BAL": "stmt_balance",
            "TOTAL_DUE": "total_due",
        },
    )


def _derive_overdue_buckets(balance: DataFrame, account_group: DataFrame) -> DataFrame:
    codes = {f"OVD_{k:02d}": f"overdue_ovd_{k:02d}" for k in range(1, 9)}
    return _pivot_balance(balance, account_group, codes)


def _null_cancelled_instalment_fields(frame: DataFrame, status: str) -> DataFrame:
    """DCORE's rule as the A3 spec test stubs it: a cancelled instalment loses its dates
    and amounts."""
    cancelled = F.col("instalment_status") == status
    for c in ("due_date", "due_amount", "payment_amount"):
        frame = frame.withColumn(c, F.when(cancelled, None).otherwise(F.col(c)))
    return frame


def install_workplace_stubs() -> list[str]:
    """Register the stand-ins; returns what was stubbed (for the coverage report)."""

    def module(name: str, **attrs) -> None:
        mod = types.ModuleType(name)
        mod.__path__ = []
        mod.__dict__.update(attrs)
        sys.modules[name] = mod

    module("enbd_collections.nodes.features.dcore")
    module(
        "enbd_collections.nodes.features.dcore._feat_dcore_utils",
        null_cancelled_instalment_fields=_null_cancelled_instalment_fields,
    )
    module(
        "enbd_collections.nodes.utils.config_dcore",
        PTP_INSTALMENT_STATUS_CANCELLED="C",
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED="C",
    )
    module("enbd_collections.nodes.primary.cc_way4")
    module(
        "enbd_collections.nodes.primary.cc_way4.prm_cc",
        derive_billing_amounts=_derive_billing_amounts,
        derive_overdue_buckets=_derive_overdue_buckets,
    )
    stubbed = [
        "nodes.features.dcore._feat_dcore_utils.null_cancelled_instalment_fields"
        " (status C nulls the instalment)",
        "nodes.utils.config_dcore (cancelled status = C)",
        "nodes.primary.cc_way4.prm_cc.derive_billing_amounts / derive_overdue_buckets"
        " (pivot of -balance by account-group type code)",
    ]
    from enbd_collections.nodes.utils import config  # pylint: disable=C0415

    if not hasattr(config, "EDP_LOAD_DATE_BUFFER_MONTHS"):  # mirror copy predates it
        config.EDP_LOAD_DATE_BUFFER_MONTHS = 12
        stubbed.append(
            "nodes.utils.config.EDP_LOAD_DATE_BUFFER_MONTHS = 12 (missing from the"
            " mirror's config.py; 12 per cc_raw_extract's docstrings)"
        )
    return stubbed


# ── A1: the spec test's cases ─────────────────────────────────────────────────


@functools.cache
def _a1_spec() -> dict:
    """The namespace of ``a1_engine_spec.py`` after a run (its frames and case rows)."""
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
    return ns


A1_PERSONA = {"persona_start_date": "2026-07-01", "persona_end_date": "2026-07-31"}


@functools.cache
def a1_inputs() -> tuple[dict, dict]:
    """CC and RL inputs of the A1 spec cases (persona ``A1_PERSONA``), plus obs-base
    rows: two billing dates in one month with different CIFs, a row without a CIF and
    one before the persona months; and two customers no case has: G6 (the "High"
    case's salary and balance plus a large deposit: three strong families) and GN
    (money in below the "some" floor: level none)."""
    ns = _a1_spec()
    obs = ns["OBS"]
    high = next(int(a[1:]) + 1000 for a, e in ns["expect"].items() if e[0] == "High")
    g6, gn = 9006, 9007
    extra = [
        ("Z1", D(2026, 7, 3), 5000),
        ("Z1", D(2026, 7, 28), 5001),
        ("Z2", obs, None),
        ("Z3", D(2026, 5, 31), 5003),
        ("G6", obs, g6),
        ("GN", obs, gn),
    ]
    spine = ns["rows"]["spine"] + extra

    def clone(frame: DataFrame) -> DataFrame:
        """``frame`` plus the "High" customer's rows as customer G6."""
        kind = dict(frame.dtypes)["cif_id"]
        mine = F.col("cif_id").cast("long") == high
        return frame.unionByName(
            frame.filter(mine).withColumn("cif_id", F.lit(g6).cast(kind))
        )

    products = ns["products"].unionByName(
        df(
            [(str(g6), obs, "ITD", "deposit", 20000.0, None, None, None)],
            ns["products"].schema.simpleString()[7:-1].replace(":", " "),
        )
    )
    flows = ns["flows"].unionByName(
        df(
            [(str(gn), obs, "third_party_in", 1, 200.0, None, 200.0)],
            ns["flows"].schema.simpleString()[7:-1].replace(":", " "),
        )
    )
    shared = {
        "feat_cif_internal_salary_monthly": clone(ns["internal_salary"]),
        "feat_cif_bureau_salary_monthly": ns["bureau_salary"],
        "feat_cif_casa_balance_monthly": clone(ns["casa_balance"]),
        "feat_cif_casa_flows_monthly": flows,
        "feat_cif_cross_product_monthly": products,
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
    rl = {
        **shared,
        "rl_spine": df(
            [r for r in spine if r[1] == obs],
            "account_id string, observation_date date, cif_id long",
        ),
        "int_loan_master": df(
            [("A0", obs, 2000.0), ("A1", obs, 0.0), ("A2", D(2026, 6, 30), 1500.0)]
            + [("A6", obs, 3000.0)],
            "account_id string, observation_date date, installment_due_amount double",
        ),
    }
    assert ns["PERSONA"] == A1_PERSONA, ns["PERSONA"]
    return cc, rl


# ── A2: the spec test's cases ─────────────────────────────────────────────────

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
    import a2_engine_spec  # pylint: disable=import-outside-toplevel

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
    # location x reachability pairs no case has: one case's customer, another's calls
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


def month_end(index: int) -> dt.date:
    """Month ``index`` from 2024-01 as a month-end date."""
    year, month = 2024 + index // 12, index % 12 + 1
    return D(year + (month == 12), month % 12 + 1, 1) - dt.timedelta(1)


END = 29
JOURNEYS = {  # account: (first month, buckets, what it exercises)
    0: (-8, [1] * 38, "clean all along: not classified; earliest source month"),
    1: (24, [1, 1, 2, 3, 4, 5], "early_payment_default"),
    2: (
        12,
        [1, 1, None, 1, 1, 1, 1, 1, 2, 3, 4, 5, 5, 5, 5, 5, 5, 5],
        "stabilized; gap",
    ),
    3: (10, [1] * 6 + [2, 3] + [1] * 4 + [2, 3, 4, 5, 6, 7, 7, 7], "repeat_delinquent"),
    4: (8, [1] * 16 + [2, 3, 4, None, 6, 7], "straight_roller_seasoned; roll gap"),
    5: (18, [1] * 6 + [2, 3, 4, 5, 6, 7], "straight_roller_early_life"),
    6: (16, [1] * 6 + [2, 2, 3, 3, 4, 5, 6, 7], "slow_roller"),
    7: (-3, [3, 4, 5, 6, 7, 8] + [9] * 27, "unknown: history before the CC floor"),
    8: (20, [5] * 10, "Q0 stabilized: CC opened delinquent (restructure blind spot)"),
    9: (
        14,
        [1, 1, 1, 4, 1, 1, 2, 3, 3, 5, 6, None, 4, 5, 6, 7],
        "glitch, +2 jump, gap",
    ),
    10: (
        10,
        [1] * 5 + [None] * 4 + [4, 5, 6, 7, 8, 9, 9, 9, 9, 9, 9],
        "unresolvable gap",
    ),
}
SPINE_MONTHS = {2: [27], 7: [1], 5: [17], 1: [31]}  # extra rows: earlier / outside
A4_PERSONA = {
    "persona_start_date": "2026-01-01",
    "persona_end_date": str(month_end(END)),
}
A4_ALT = {  # every dpd_journey switch flipped
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
    ).withColumn("billing_date", F.col("billing_date").cast("timestamp"))
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

    journeys = {f"L{a}": (first, rl(b)) for a, (first, b, _) in JOURNEYS.items()}
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
            "cif_id string, account_id string, observation_date date, dpd_bucket int,"
            " emi_coverage_ratio double, outstanding_balance double,"
            " is_restructured int,"
            " loan_type string, account_status string",
        ),
        "rl_spine": df(
            spine, "account_id string, observation_date date, cif_id string"
        ),
        "int_loan_restructure_link": df(
            link,
            "account_id string, orig_account_id string, restr_flagged_date date,"
            " orig_close_date date, match_type string, candidate_count int",
        ),
        "feature_retail_loans": df(
            [(a, month_end(END), int(a in flagged)) for a in on_spine],
            "account_id string, observation_date date, has_restructured_loan_flag int",
        ),
    }


# ── A3: one account per rule branch ───────────────────────────────────────────
# Observation month Aug 2026. CC statements on the 5th (Jan 2025 .. Aug 2026; the last
# has no next statement, so no cycle); one month's due 100 unless ``due`` says
# otherwise (CC: overdue bucket 03; RL: the EMI). RL rows are the CC case on the loan
# scale: one month-end snapshot per month, the month's payments as ``total_paid``.
# Episode = the first month of the current delinquency (A4), Apr 2026 unless set.

A3_PERSONA = {"persona_start_date": "2026-08-01", "persona_end_date": "2026-08-31"}
STATEMENTS = tuple(D(2025 + i // 12, i % 12 + 1, 5) for i in range(20))
EP = D(2026, 4, 1)


def monthly(amount: float, first: dt.date, last: dt.date, day: int = 20) -> tuple:
    """A payment of ``amount`` on ``day`` of every month from ``first`` to ``last``."""
    out, y, m = [], first.year, first.month
    while (y, m) <= (last.year, last.month):
        out.append((D(y, m, day), amount))
        y, m = y + (m == 12), m % 12 + 1
    return tuple(out)


PAID_2025 = monthly(100.0, D(2025, 1, 1), D(2025, 12, 1))
A3_CASES: dict[int, dict] = {}


def a3_case(  # pylint: disable=too-many-arguments
    what: str,
    *,
    episode: dt.date | None = EP,
    a4: str = "scored",
    pays: tuple = (),
    followups: tuple = (),
    plans: tuple = (),
    due: dict | None = None,
    min_due: dict | None = None,
    statements: tuple = STATEMENTS,
    stagnated_from: dt.date | None = None,
) -> int:
    """Add an account. ``a4``: scored / censored (cropped and delinquent from its first
    kept month) / uncropped (delinquent from its first month, not cropped) / stale (A4
    row in July only) / none. ``followups``: (day, result_name[, action_code[,
    category]]). ``plans``: (ptp | settlement, start, cancelled, [(due_date, due, paid,
    status)]). ``due`` / ``min_due``: statement -> amount. ``stagnated_from``: from this
    statement bucket 08 holds money and buckets 01..07 none (CC; the minimum due is 0
    unless ``min_due`` sets it) and the EMI is missing (RL)."""
    account = 101 + len(A3_CASES)
    A3_CASES[account] = {
        "what": what,
        "episode": episode,
        "a4": a4,
        "pays": pays,
        "followups": followups,
        "plans": plans,
        "due": due or {},
        "min_due": min_due or {},
        "statements": statements,
        "stagnated_from": stagnated_from,
    }
    return account


PTP, SAL, RTP = "PROMISE TO PAY", "WILL PAY AT SALARY", "REFUSE TO PAY"
JUL1 = dt.datetime(2026, 7, 1, 10)
# ── Dimension A: promise events ──
K = a3_case(
    "kept (2 promises paid by the next statement) + regular + clean -> High",
    pays=PAID_2025 + monthly(100.0, D(2026, 1, 1), D(2026, 8, 1)),
    followups=((D(2026, 5, 10), PTP), (D(2026, 6, 10), SAL)),
)
a3_case(
    "kept + regular, unpaid before the episode (not clean): 4 points -> High",
    pays=monthly(100.0, D(2026, 1, 1), D(2026, 8, 1)),
    followups=((D(2026, 5, 10), PTP), (D(2026, 6, 10), SAL)),
)
a3_case(
    "broken by rate: a follow-up run paid, a matched plan partly paid, a settlement in"
    " the window unpaid, one outside it, a promise not concluded (31-day fallback)",
    pays=PAID_2025 + ((D(2026, 6, 30), 120.0), (D(2026, 7, 20), 150.0)),
    due={D(2026, 7, 5): 300.0},
    followups=(
        (D(2026, 6, 20), PTP),
        (D(2026, 6, 24), "PROMISE TO PAY SCHEDULED"),
        (D(2026, 7, 14), "CODE25 WILL PAY AT SALARY"),
        (D(2026, 7, 25), "SOFTPTP"),
        (D(2026, 8, 20), PTP),
    ),
    plans=(
        ("ptp", D(2026, 7, 10), 0, [(D(2026, 7, 30), 100.0, None, "B")]),
        ("settlement", D(2026, 2, 1), 0, [(D(2026, 2, 28), 1000.0, None, "B")]),
        ("settlement", D(2025, 8, 1), 0, [(D(2025, 8, 30), 1000.0, None, "B")]),
    ),
)
a3_case(
    "partly kept: one promise paid; some; not clean -> Moderate",
    pays=((D(2026, 7, 20), 100.0),),
    followups=((D(2026, 7, 10), PTP),),
)
a3_case(
    "promised: one promise unpaid; a cancelled plan and a cancelled instalment drop out",
    followups=((D(2026, 7, 10), PTP),),
    plans=(
        ("ptp", D(2026, 6, 1), 1, [(D(2026, 6, 20), 100.0, None, "B")]),
        ("ptp", D(2026, 5, 1), 0, [(D(2026, 5, 20), 100.0, None, "C")]),
    ),
)
a3_case(
    "broken by streak: three promises unpaid",
    followups=((D(2026, 5, 10), PTP), (D(2026, 6, 10), PTP), (D(2026, 7, 10), PTP)),
)
a3_case(
    "D-A3-29: 07-07 is after the 07-05 deadline of the 07-02 run, so it starts a new"
    " event (60-180 CC); with a month-end deadline the three are one event",
    followups=((D(2026, 7, 2), PTP), (D(2026, 7, 7), SAL), (D(2026, 7, 9), PTP)),
)
a3_case(
    "a plan takes the nearer of two follow-up runs (06-14), 06-05 stays alone",
    followups=((D(2026, 6, 5), PTP), (D(2026, 6, 14), PTP)),
    plans=(("ptp", D(2026, 6, 10), 0, [(D(2026, 6, 30), 100.0, None, "B")]),),
)
a3_case(
    "paid after the next statement, within 30 days: none (promised); partly kept at"
    " 30 days",
    pays=((D(2026, 5, 10), 200.0),),
    followups=((D(2026, 5, 3), PTP),),
)
a3_case(
    "settlement plan paid by its deadline (table_only, paid)",
    pays=((D(2026, 6, 20), 100.0),),
    plans=(("settlement", D(2026, 6, 1), 0, [(D(2026, 6, 25), 100.0, 100.0, "F")]),),
)
# ── Dimensions B and C ──
a3_case(
    "some: one cycle with 150 against a due of 300; not clean",
    pays=((D(2026, 7, 20), 150.0),),
    due={s: 300.0 for s in STATEMENTS if s >= D(2026, 6, 5)},
)
a3_case(
    "payments under 100 AED: none; not clean",
    pays=monthly(60.0, D(2025, 1, 1), D(2026, 8, 1)),
)
a3_case(
    "bucket 08 open from May with a minimum due of 5000: the due is the average ladder"
    " due before it; regular",
    pays=((D(2026, 6, 20), 150.0), (D(2026, 7, 20), 150.0)),
    min_due={
        s: 5000.0 if s >= D(2026, 5, 5) else 100.0 if s.month % 2 else 140.0
        for s in STATEMENTS
    },
    stagnated_from=D(2026, 5, 5),
)
a3_case(
    "missing statements: the 90-day cycle is dropped",
    pays=PAID_2025 + monthly(100.0, D(2026, 1, 1), D(2026, 8, 1)),
    statements=tuple(s for s in STATEMENTS if s not in (D(2026, 2, 5), D(2026, 3, 5))),
)
a3_case(
    "few statements before the episode: no record",
    pays=monthly(100.0, D(2026, 2, 1), D(2026, 8, 1)),
    statements=tuple(s for s in STATEMENTS if s >= D(2026, 2, 5)),
)
a3_case(
    "episode censored: windows from the lookback, C no record (censored)",
    a4="censored",
    pays=PAID_2025 + monthly(100.0, D(2026, 1, 1), D(2026, 8, 1)),
)
a3_case(
    "delinquent from the first month of an uncropped history: a true onset",
    a4="uncropped",
    pays=PAID_2025,
)
a3_case(
    "earlier episode (Jan 2026): longer B window, C up to Dec 2025",
    episode=D(2026, 1, 1),
    pays=PAID_2025 + monthly(100.0, D(2026, 3, 1), D(2026, 8, 1)),
)
# ── Unknown ──
a3_case(
    "no A4 row: Unknown (no_episode)", a4="none", followups=((D(2026, 7, 10), PTP),)
)
a3_case("A4 row only in July: Unknown (no_episode)", a4="stale")
# ── Contacts ──
a3_case(
    "refusal, nothing after: refusal flag demotes Moderate (regular + clean) to Low",
    pays=PAID_2025 + monthly(100.0, D(2026, 1, 1), D(2026, 6, 1)),
    followups=((JUL1, RTP, "OC", "SUC"),),
)
a3_case(
    "refusal, then 60 AED in two cycles: still a refusal",
    pays=((D(2026, 7, 10), 60.0), (D(2026, 8, 10), 60.0)),
    followups=((JUL1, RTP, "OC", "SUC"),),
)
a3_case(
    "refusal, then 150 AED in one cycle: not a refusal",
    pays=((D(2026, 7, 10), 150.0),),
    followups=((JUL1, RTP, "OC", "SUC"),),
)
a3_case(
    "refusal and a promise later the same day: the latest contact is the promise",
    followups=((JUL1, RTP, "OC", "SUC"), (JUL1.replace(hour=11), PTP, "OC", "SUC")),
)
a3_case(
    "refusal, then a plan starts: not a refusal",
    followups=((JUL1, RTP, "OC", "SUC"),),
    plans=(("ptp", D(2026, 7, 15), 0, [(D(2026, 7, 30), 100.0, None, "B")]),),
)
a3_case("dispute", followups=((JUL1, "DISPUTE", "OC", "SUC"),))
RINGING = tuple(
    (dt.datetime(2026, 7, d, 10), "RINGING NO REPLY", "OC", "UNS") for d in range(2, 8)
)
a3_case(
    "hung up, then 3 ringing days: no pickup at 60-180 only",
    followups=((JUL1, "CUSTOMER HUNG UP", "OC", "SUC"), *RINGING[:3]),
)
a3_case(
    "hung up, then 6 ringing days: no pickup in both segments",
    followups=((JUL1, "CUSTOMER HUNG UP", "OC", "SUC"), *RINGING),
)
a3_case(
    "hung up, ringing days, then a dead line: no pickup is false",
    followups=(
        (JUL1, "CUSTOMER HUNG UP", "OC", "SUC"),
        *RINGING,
        (dt.datetime(2026, 7, 20, 10), "CUSTOMER NOT CONTACTABLE", "OC", "UNS"),
    ),
)
a3_case("payment reported", followups=((JUL1, "PARTIALLY PAID", "OC", "SUC"),))
a3_case(
    "right-party contact (inbound); a refusal before the episode and one 30 months"
    " back are outside the window",
    followups=(
        (JUL1, "APPRECIATIONS", "IC", "SUC"),
        (dt.datetime(2026, 3, 1, 10), RTP, "OC", "SUC"),
        (dt.datetime(2024, 2, 1, 10), RTP, "OC", "SUC"),
    ),
)
a3_case(
    "refusal and a plain contact later the same day: the refusal counts (D-A3-32)"
    " and demotes Moderate to Low",
    pays=PAID_2025 + monthly(100.0, D(2026, 1, 1), D(2026, 6, 1)),
    followups=(
        (JUL1, RTP, "OC", "SUC"),
        (JUL1.replace(hour=11), "APPRECIATIONS", "OC", "SUC"),
    ),
)


def _due(case: dict, statement: dt.date) -> float | None:
    if case["stagnated_from"] and statement >= case["stagnated_from"]:
        return None
    return case["due"].get(statement, 100.0)


def _a4_row(account, case: dict, day: dt.date) -> tuple | None:
    """A4 output row: the episode start is ``history_months - 1 - months_before_spell``
    months before the row's month."""
    if case["a4"] == "none":
        return None
    ep = case["episode"]
    back = (day.year * 12 + day.month) - (ep.year * 12 + ep.month)
    left = case["a4"] in ("censored", "uncropped")
    cropped = case["a4"] == "censored"
    if case["a4"] == "stale":
        day = D(2026, 7, 31)
    return (account, day, 24 - 1 - back, 24, left, cropped)


A4_SCHEMA = (
    "account_id string, observation_date date, months_before_spell int,"
    " history_months int, left_censored boolean, history_cropped boolean"
)


@functools.cache
def a3_dcore() -> dict:
    """The DCORE tables of ``A3_CASES`` (agreement = 9000 + account), plus an agreement
    and a plan of an account outside the base."""
    agreements, followup, ptp, ptp_rows, sett, sett_rows = [], [], [], [], [], []
    seq = 0
    for account, case in [*A3_CASES.items(), (999, {"followups": (), "plans": ()})]:
        agreement = 9000 + account
        agreements.append((str(account), agreement))
        for day, name, *rest in case["followups"]:
            code, category = rest if rest else ("OC", "PTP")
            when = (
                day
                if isinstance(day, dt.datetime)
                else dt.datetime(*day.timetuple()[:3], 10)
            )
            followup.append((str(agreement), when, code, category, name))
        for kind, start, cancelled, rows in case["plans"]:
            seq += 1
            if kind == "ptp":
                ptp.append((agreement, seq, start, start, cancelled))
                ptp_rows += [(seq, *r) for r in rows]
            else:
                sett.append((agreement, seq, start, cancelled))
                sett_rows += [(seq, *r) for r in rows]
    ptp.append(
        (9999, 999, D(2026, 6, 1), D(2026, 6, 1), 0)
    )  # account 999: not in the base
    ptp_rows.append((999, D(2026, 6, 20), 100.0, None, "B"))
    rows = (
        "due_date date, due_amount double, payment_amount double,"
        " instalment_status string"
    )
    return {
        "prm_dcore_account_agreements": df(
            agreements, "account_id string, agreement_id long"
        ),
        "dcore_prm_followup_outcomes": df(
            followup,
            "agreement_id string, action_ts timestamp, action_code string,"
            " result_category string, result_name string",
        ),
        "dcore_int_ptp": df(
            ptp,
            "agreement_id long, promise_seqno long, promise_start date,"
            " event_date date,"
            " is_cancelled int",
        ),
        "dcore_prm_promise_instalments": df(ptp_rows, f"promise_seqno long, {rows}"),
        "dcore_int_settlement": df(
            sett, "agreement_id long, rps_seqno long, event_date date, is_cancelled int"
        ),
        "dcore_prm_settlement_schedule_instalments": df(
            sett_rows, f"rps_seqno long, {rows}"
        ),
    }


def _cc_raw_rows(account: int, case: dict) -> tuple[list, list, list]:
    """raw_stg_billing, raw_stg_balance and raw_transaction rows of one CC account."""
    billing, balance, txn = [], [], []
    for s in case["statements"]:
        due = _due(case, s)
        billing.append(
            (
                float(account),
                dt.datetime(*s.timetuple()[:3]),
                s + dt.timedelta(1),
                s + dt.timedelta(25),
                "BS_PMT_CYCLE_DUE=3",
            )
        )
        min_due = case["min_due"].get(s, 0.0 if due is None else 100.0)
        groups = {1: min_due, 2: 500.0, 3: due or 5000.0}
        if due is not None and due != 100.0:
            groups[13] = due  # OVD_03: the oldest open bucket
        if due is None:
            groups[18] = 5000.0  # OVD_08 open, buckets 01..07 empty
        balance += [(float(account), s, s, g, -v) for g, v in groups.items()]
    for day, amount in case["pays"]:
        txn.append(
            (
                1,
                100,
                float(account),
                day,
                day,
                amount,
                1,
                "018",
                "PAYMENT",
                "DOMESTIC=Y",
                0,
                day,
                1,
                "T",
            )
        )
    return billing, balance, txn


@functools.cache
def cc_a3_inputs() -> dict:
    """Free inputs of ``crx_cc_obs_base`` + ``crx_cc_raw_extract`` + the CC A3 axis."""
    spine, a4, billing, balance, txn = [], [], [], [], []
    for account, case in A3_CASES.items():
        spine.append((account, D(2026, 8, 5), 50000 + account))
        if (row := _a4_row(str(account), case, D(2026, 8, 5))) is not None:
            a4.append(row)
        b, bal, t = _cc_raw_rows(account, case)
        billing, balance, txn = billing + b, balance + bal, txn + t
    spine.append((K, D(2026, 7, 5), 50000 + K))  # before the persona months
    noise = [  # on account K: dropped by the quality filters or not a payment
        (
            1,
            200,
            float(K),
            D(2026, 7, 21),
            D(2026, 7, 21),
            999.0,
            1,
            "018",
            "X",
            "",
            0,
            D(2026, 7, 21),
            1,
            "T",
        ),
        (
            0,
            100,
            float(K),
            D(2026, 7, 22),
            D(2026, 7, 22),
            999.0,
            1,
            "018",
            "X",
            "",
            0,
            D(2026, 7, 22),
            1,
            "T",
        ),
        (
            1,
            100,
            float(K),
            D(2026, 7, 23),
            D(2026, 7, 23),
            999.0,
            0,
            "036",
            "SHOP",
            "DOMESTIC=N",
            5411,
            D(2026, 7, 23),
            1,
            "T",
        ),
        (
            1,
            100,
            float(K),
            D(2026, 7, 24),
            D(2026, 7, 24),
            0.0,
            1,
            "018",
            "FEE",
            "",
            0,
            D(2100, 1, 1),
            0,
            "I",
        ),
        txn[0],  # an exact duplicate row counts once
    ]
    groups = [(g, code) for g, code in ACCOUNT_GROUPS.items()]
    return {
        **a3_dcore(),
        "cc_spine": df(spine, "contract_id long, observation_date date, cif_id long"),
        "crx_cc_a4_deterioration": df(a4, A4_SCHEMA),
        "raw_stg_billing": df(
            billing,
            "contract_idt double, billing_date timestamp, edp_load_date date,"
            " due_date date, add_info string",
        ),
        "raw_stg_balance": df(
            balance,
            "contract_idt double, banking_date date, edp_load_date date,"
            " account_group_id int, balance double",
        ),
        "raw_stg_account_group": df(groups, "account_group_id int, type_code string"),
        "raw_transaction": df(
            txn + noise,
            "primary_entry_idt int, org int, contract_idt double, banking_date date,"
            " edp_load_date date, settl_amount double, direction int, txn_code string,"
            " txn_description string, add_info string, trans_mcc int, trans_date date,"
            " card_idt int, service_class string",
        ),
        "crx_cc_spell_table": df(
            [(K, D(2026, 4, 10), 0), (K + 1, D(2026, 4, 10), 1)],
            "account_id long, t0 date, t0_censored_flag int",
        ),
        "raw_stg_limit": df(
            [
                (float(K), D(2026, 3, 1), "FIN_LIMIT", 10000.0),
                (float(K), D(2026, 3, 1), "AVAILABLE", 2000.0),
                (float(K), D(2026, 3, 1), "ADD_LIMIT", 500.0),
                (float(K), D(2024, 1, 1), "FIN_LIMIT", 9000.0),
                (float(K + 1), D(2026, 3, 1), "FIN_LIMIT", 7000.0),
            ],
            "contract_idt double, banking_date date, type_code string, amount double",
        ),
    }


@functools.cache
def rl_a3_inputs() -> dict:
    """Free inputs of ``crx_rl_obs_base`` + the RL A3 axis: one month-end snapshot of
    each case per month (EMI = the month's due, ``total_paid`` = its payments), an
    earlier snapshot in August for K (the month end wins) and a loan outside the base.
    """
    spine, a4, master = [], [], []
    for account, case in A3_CASES.items():
        spine.append((str(account), D(2026, 8, 31), 50000 + account))
        if (row := _a4_row(str(account), case, D(2026, 8, 31))) is not None:
            a4.append(row)
        for s in case["statements"]:
            month_end_day = D(
                s.year + s.month // 12, s.month % 12 + 1, 1
            ) - dt.timedelta(1)
            paid = float(
                sum(
                    a for d, a in case["pays"] if (d.year, d.month) == (s.year, s.month)
                )
            )
            master.append((str(account), month_end_day, _due(case, s), paid))
    master += [
        (str(K), D(2026, 8, 15), 999.0, 999.0),
        ("999", D(2026, 7, 31), 100.0, 100.0),
    ]
    return {
        **a3_dcore(),
        "rl_spine": df(spine, "account_id string, observation_date date, cif_id long"),
        "crx_rl_a4_deterioration": df(a4, A4_SCHEMA),
        "int_loan_master": df(
            master,
            "account_id string, observation_date date, monthly_emi_due double,"
            " total_paid double",
        ),
    }


# ── Products: product_primary + product_features ──────────────────────────────
# Persona from Jul 2026, 12 months of history: floor Aug 2025, load-date bound Jun 2025.

PRODUCTS_PARAMS = {
    "crx_persona": {
        "persona_start_date": "2026-07-01",
        "persona_end_date": "2026-07-31",
    },
    "products": {"history_months": 12},
}


@functools.cache
def product_inputs() -> dict:
    """Customer 1: card 11 linked to card 10 (both kept), card 12 overdue, card 13 with no
    balance snapshot in the month's last days (minimum due NULL), two billing rows in a
    month (the latest counts), one before the floor, one loaded too early. Customer 2:
    a current loan, an overdue one, a written-off one, a snapshot before the floor, an
    account number with spaces. WM: deposits (last week of the month counts),
    investments of 0 (no holding), a negative deposit, AUM, a week before the floor.
    Contract 30's client is unknown."""
    billing = [  # (contract, billing day, load day, level)
        (11, D(2026, 6, 5), D(2026, 6, 6), 1),
        (11, D(2026, 6, 20), D(2026, 6, 21), 2),
        (11, D(2026, 7, 5), D(2026, 7, 6), 1),
        (10, D(2026, 7, 5), D(2026, 7, 6), 1),
        (12, D(2026, 7, 5), D(2026, 7, 6), 4),
        (13, D(2026, 7, 5), D(2026, 7, 6), 1),
        (11, D(2025, 7, 5), D(2025, 7, 6), 1),
        (12, D(2025, 9, 5), D(2025, 5, 1), 1),
        (30, D(2026, 7, 5), D(2026, 7, 6), 1),
    ]
    balance = [  # (contract, banking day, load day, group, balance)
        (11, D(2026, 6, 28), D(2026, 6, 29), 1, -150.0),
        (11, D(2026, 7, 27), D(2026, 7, 28), 1, -120.0),
        (11, D(2026, 7, 30), D(2026, 7, 31), 1, -130.0),
        (12, D(2026, 7, 30), D(2026, 7, 31), 1, -800.0),
        (13, D(2026, 7, 10), D(2026, 7, 11), 1, -50.0),
    ]
    loans = [  # (cust, acct, snapshot, bucket, overdue days, instalment, write-off)
        (2, "L1 ", D(2026, 7, 31), 0, 0.0, 2500.0, None),
        (2, "L2", D(2026, 7, 31), 2, 45.0, 1800.0, None),
        (2, "L3", D(2026, 7, 31), 0, 0.0, 900.0, D(2026, 5, 1)),
        (2, "L1 ", D(2025, 6, 30), 0, 0.0, 2500.0, None),
        (3, "L4", D(2026, 6, 30), 0, None, 700.0, None),
    ]
    wm = [  # (cif, WM week yyyyMM0W, deposits, investments)
        (1, 20260701, 5000.0, 0.0),
        (1, 20260704, 6000.0, 0.0),
        (2, 20260704, -10.0, 3000.0),
        (1, 20250604, 9999.0, 9999.0),
    ]
    return {
        "raw_stg_client": df(
            [(1, " 1"), (2, "2"), (2, "2")], "client_idt long, ident_number string"
        ),
        "raw_stg_contract": df(
            [
                (10.0, 1, None),
                (11.0, 1, 10.0),
                (12.0, 1, None),
                (13.0, 1, None),
                (30.0, 9, None),
            ],
            "contract_idt double, client_idt long, parent_contract_idt double",
        ),
        "raw_stg_billing": df(
            [
                (
                    float(c),
                    dt.datetime(*b.timetuple()[:3]),
                    ld,
                    f"BS_PMT_CYCLE_DUE={lv}",
                )
                for c, b, ld, lv in billing
            ],
            "contract_idt double, billing_date timestamp, edp_load_date date,"
            " add_info string",
        ),
        "raw_stg_balance": df(
            [(float(c), d, ld, g, v) for c, d, ld, g, v in balance],
            "contract_idt double, banking_date date, edp_load_date date,"
            " account_group_id int, balance double",
        ),
        "raw_stg_account_group": df(
            list(ACCOUNT_GROUPS.items()), "account_group_id int, type_code string"
        ),
        "bo_rr_portf_actv_acct_mthly": df(
            loans,
            "cust_num long, acct_num string, ss_dt date, ra_delq_bkt int,"
            " ra_ovd_days double, ra_instl_due_amt double, ra_woff_dt date",
        ),
        "wm_fea_casa_eod_avg_balance": df(
            wm,
            "cif_id long, week_number int, avg_itd_eod_balance double,"
            " avg_inv_eod_balance double",
        ),
        "wm_fea_wealth_holdings_by_cif": df(
            [(1, 20260704, 20000.0), (2, 20260704, 0.0)],
            "cif_id long, week_number int, etw_total_market_value_aed double",
        ),
    }


# ── Bureau: bureau_salary_bounces ─────────────────────────────────────────────


@functools.cache
def bureau_inputs() -> dict:
    """The A1 spec's bureau rows, plus a NULL CIF, a NULL salary, a padded CIF and a
    mid-month date (salary); a NULL return date, a 0 amount, two cheques returned on
    one day and a return repeated in a later pull (bounces)."""
    rows = _a1_spec()["rows"]
    unified = rows["unified"] + [
        (None, D(2026, 7, 28), 5000.0, "alert"),
        (7, D(2026, 7, 28), None, "alert"),
        (8, D(2026, 6, 14), 4000.0, "salary_credit"),
    ]
    alerts = rows["alert"] + [
        (9, "CC", "BOUNCED CHEQUE", D(2026, 7, 5), 700.0, 99, None, None),
        (9, "CC", "BOUNCED CHEQUE", D(2026, 7, 5), 0.0, 99, None, D(2026, 7, 2)),
        (9, "CC", "BOUNCED CHEQUE", D(2026, 7, 5), 300.0, 99, None, D(2026, 7, 3)),
        (9, "CC", "BOUNCED CHEQUE", D(2026, 7, 5), 800.0, 99, None, D(2026, 7, 3)),
        (9, "CC", "BOUNCED CHEQUE", D(2026, 8, 5), 800.0, 99, None, D(2026, 7, 3)),
    ]
    return {
        "feat_bureau_salary_unified": df(
            unified,
            "cif_id long, salary_month_end date, monthly_salary double,"
            " salary_source string",
        ),
        "prm_bureau_alert_enriched": df(
            alerts,
            "cif_id long, contract_type string, alert_description string,"
            " extract_date date, bounced_cheque_amount double, alert_type_number int,"
            " salary_credit_amount double, dt_of_return date",
        ),
    }
