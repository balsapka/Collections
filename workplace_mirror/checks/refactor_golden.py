"""Behaviour oracle of the persona pipelines (refactor gate 4, PLAN §5 / §6).

    JAVA_HOME=/opt/homebrew/opt/openjdk@17 \
        python workplace_mirror/checks/refactor_golden.py [--record] [--only SUBSTR]

Runs the pipelines on the synthetic inputs of ``golden_inputs.py`` through Kedro's
SequentialRunner (MemoryDatasets, Spark local, one job at a time), once per model_id,
and checks every dataset they write:

* tier L: A1 and A3 (CC and RL, both segments; A3 also with the other promise
  deadlines), ``product_primary`` + ``product_features``, ``bureau_salary_bounces``;
* tier K: ``crx_cc_raw_extract`` (in the CC A3 runs);
* regression guard (tier S is editable): the obs bases, A2, the full histories + A4.

``--record`` saves ``refactor_review/00_baseline/golden/<run>/<dataset>.parquet``
(gitignored), ``manifest.json`` (rows, schema, order-independent hash per dataset) and
``harness_coverage.md`` (the values the state columns reach, and what is not covered).
The default compares schema and rows (``exceptAll`` both ways) with the parquet, or with
the manifest hash when the parquet is absent, and exits 1 naming the dataset and example
rows. ``computed_at`` (the run clock) is ignored. Guard runs must raise.
"""

# pylint: disable=wrong-import-position
import datetime as dt
import hashlib
import json
import logging
import os
import pathlib
import sys
import time
import warnings

HERE = pathlib.Path(__file__).resolve().parent
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
os.environ["TZ"] = "UTC"  # naive datetimes in the inputs are UTC, as the session
time.tzset()
sys.path[:0] = [str(HERE.parent / "src"), str(HERE)]

from kedro.io import DataCatalog, MemoryDataset  # noqa: E402
from kedro.runner import SequentialRunner  # noqa: E402
from pyspark.sql import SparkSession  # noqa: E402
from pyspark.sql import functions as F  # noqa: E402

spark = (
    SparkSession.builder.master("local[2]")
    .config("spark.driver.memory", "2g")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.ui.enabled", "false")
    .config("spark.ui.showConsoleProgress", "false")
    .config("spark.sql.session.timeZone", "UTC")
    .config("spark.driver.extraJavaOptions", "-Duser.timezone=UTC")
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")
logging.getLogger().setLevel(logging.WARNING)
logging.getLogger("kedro").setLevel(logging.CRITICAL)  # the guard runs log their errors
warnings.filterwarnings("ignore", message=".*'partial' function.*")

import golden_inputs as gi  # noqa: E402

STUBBED = gi.install_workplace_stubs()

from enbd_collections.pipelines.bureau import salary_bounces  # noqa: E402
from enbd_collections.pipelines.crx_persona import (  # noqa: E402
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_raw_extract,
    obs_base,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
    rl_full_history,
)
from enbd_collections.pipelines.crx_persona.a3_credibility import (  # noqa: E402
    create_a3_pipeline,
)
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration import (  # noqa: E402
    pipeline as cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona.cc_full_history import (  # noqa: E402
    pipeline as cc_full_history,
)
from enbd_collections.pipelines.products import features as product_features  # noqa
from enbd_collections.pipelines.products import primary as product_primary  # noqa

OUT = HERE.parent / "refactor_review" / "00_baseline"
GOLDEN = OUT / "golden"
IGNORED = ["computed_at"]
MODELS = {"cc": ("cc_60_180", "cc_180_plus"), "rl": ("rl_60_180", "rl_180_plus")}
A3_FLOOR = "2024-01-01"  # params:cc_a3_history_floor_date (conf/base)


# ── Runs ──────────────────────────────────────────────────────────────────────


def _a3(product: str, deadline: str | None = None):
    """The product's A3 pipeline; CC also builds its raw extract first."""
    wrapper = {"cc": cc_a3_payment_credibility, "rl": rl_a3_payment_credibility}
    module = wrapper[product]
    if deadline is None:
        a3 = module.create_pipeline()
    else:  # the extension point: another promise deadline, same nodes
        a3 = create_a3_pipeline(
            product,
            f"crx_{product}_a3_payment_credibility",
            module.pipeline.DUES,
            module.pipeline.PAYMENTS,
            deadline,
        )
    return cc_raw_extract.create_pipeline() + a3 if product == "cc" else a3


def runs() -> list[tuple[str, object, str, dict, object]]:
    """(run name, pipeline, model_id, params, inputs builder)."""
    a1 = {"cc": cc_a1_ability, "rl": rl_a1_ability}
    a2 = {"cc": cc_a2_locatability, "rl": rl_a2_locatability}
    a4 = {
        "cc": cc_full_history.create_pipeline() + cc_a4_deterioration.create_pipeline(),
        "rl": rl_full_history.create_pipeline() + rl_a4_deterioration.create_pipeline(),
    }
    obs = {"cc": obs_base.create_cc_pipeline, "rl": obs_base.create_rl_pipeline}
    built = {  # product: (A1, A2, A4, A3 inputs), each a builder (cached)
        "cc": (lambda: gi.a1_inputs()[0], lambda: gi.a2_inputs()[0], gi.cc_a4_inputs,
               gi.cc_a3_inputs),
        "rl": (lambda: gi.a1_inputs()[1], lambda: gi.a2_inputs()[1], gi.rl_a4_inputs,
               gi.rl_a3_inputs),
    }  # fmt: skip
    a1_persona = {"crx_persona": gi.A1_PERSONA}
    a3_params = {"crx_persona": gi.A3_PERSONA, "cc_a3_history_floor_date": A3_FLOOR}
    out = []
    for p, models in MODELS.items():
        in_a1, in_a2, in_a4, in_a3 = built[p]
        for m in models:
            out += [
                (f"crx_{p}_a1_ability.{m}", obs[p]() + a1[p].create_pipeline(), m,
                 a1_persona, in_a1),
                (f"crx_{p}_a3_payment_credibility.{m}", obs[p]() + _a3(p), m,
                 a3_params, in_a3),
                (f"crx_{p}_a2_locatability.{m}", obs[p]() + a2[p].create_pipeline(), m,
                 a1_persona, in_a2),
                (f"crx_{p}_a4_deterioration.{m}", a4[p], m,
                 {"crx_persona": gi.A4_PERSONA}, in_a4),
            ]  # fmt: skip
        m = models[0]
        alt = {"crx_persona": {**gi.A4_PERSONA, "dpd_journey": gi.A4_ALT}}
        out.append((f"crx_{p}_a4_deterioration.{m}_alt", a4[p], m, alt, in_a4))
    # the other promise deadlines; the CC run also moves the history floor past
    # the first statements
    for p, deadline, floor in (
        ("cc", "30_days", "2025-06-01"),
        ("rl", "next_month_end", A3_FLOOR),
        ("rl", "30_days_month_end", A3_FLOOR),
    ):
        params = {**a3_params, "cc_a3_history_floor_date": floor}
        out.append(
            (f"crx_{p}_a3_payment_credibility.{MODELS[p][0]}_{deadline}",
             obs[p]() + _a3(p, deadline), MODELS[p][0], params, built[p][3])
        )  # fmt: skip
    products = product_primary.create_pipeline() + product_features.create_pipeline()
    out += [
        ("product_primary+product_features", products, "cc_60_180",
         gi.PRODUCTS_PARAMS, gi.product_inputs),
        ("bureau_salary_bounces", salary_bounces.create_pipeline(), "cc_60_180", {},
         gi.bureau_inputs),
    ]  # fmt: skip
    return out


def guards() -> list[tuple[str, object, str, dict, dict]]:
    """Runs that must raise."""
    a1_cc, persona = gi.a1_inputs()[0], gi.A1_PERSONA
    bad_spine = gi.df(
        [("X", dt.date(2026, 7, 15), 1)],
        "account_id string, observation_date date, cif_id long",
    )
    no_bucket = {**a1_cc, "prm_balance": a1_cc["prm_balance"].drop("overdue_bucket_06")}
    stale_key = {"crx_persona": {**gi.A4_PERSONA, "dpd_journey": {"det_option": 1}}}
    cc_journey = (
        cc_full_history.create_pipeline() + cc_a4_deterioration.create_pipeline()
    )
    rl_a3 = gi.rl_a3_inputs()
    no_paid = {**rl_a3, "int_loan_master": rl_a3["int_loan_master"].drop("total_paid")}
    a3_params = {"crx_persona": gi.A3_PERSONA}
    bureau = gi.bureau_inputs()
    no_source = {
        **bureau,
        "feat_bureau_salary_unified": bureau["feat_bureau_salary_unified"].drop(
            "salary_source"
        ),
    }
    products = gi.product_inputs()
    no_woff = {
        **products,
        "bo_rr_portf_actv_acct_mthly": products["bo_rr_portf_actv_acct_mthly"].drop(
            "ra_woff_dt"
        ),
    }
    rl_obs = obs_base.create_rl_pipeline()
    return [
        ("mid-month RL spine", rl_obs, "rl_60_180", {"crx_persona": persona},
         {"rl_spine": bad_spine}),
        ("prm_balance without overdue_bucket_06", obs_base.create_cc_pipeline()
         + cc_a1_ability.create_pipeline(), "cc_60_180", {"crx_persona": persona},
         no_bucket),
        ("unknown dpd_journey key", cc_journey, "cc_60_180", stale_key,
         gi.cc_a4_inputs()),
        ("unknown promise deadline", rl_obs + _a3("rl", "tomorrow"), "rl_60_180",
         a3_params, rl_a3),
        ("int_loan_master without total_paid (RL A3)", rl_obs + _a3("rl"),
         "rl_60_180", a3_params, no_paid),
        ("feat_bureau_salary_unified without salary_source",
         salary_bounces.create_pipeline(), "cc_60_180", {}, no_source),
        ("loan portfolio without ra_woff_dt", product_primary.create_pipeline(),
         "cc_60_180", gi.PRODUCTS_PARAMS, no_woff),
    ]  # fmt: skip


class _Kept(MemoryDataset):
    """A MemoryDataset the runner cannot release, so intermediates can be read after.
    A saved DataFrame is checkpointed (computed once, lineage cut), as a persisted
    catalog dataset would be: without it the last node's plan holds the whole
    pipeline and the 2 GB driver spends its time in garbage collection."""

    def save(self, data) -> None:
        if hasattr(data, "localCheckpoint"):
            data = data.localCheckpoint(eager=True)
        super().save(data)

    def _release(self) -> None:
        pass


def run_pipeline(pipeline, model_id: str, params: dict, inputs: dict) -> dict:
    """Every dataset ``pipeline`` writes, run on MemoryDatasets."""
    params = {"model_id": model_id, **params}
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


# ── Coverage ──────────────────────────────────────────────────────────────────
# Per output kind (the dataset name without the crx_<product>_ prefix): the values a
# column should reach; "NULL" stands for a missing value.
STATE_COLUMNS = {
    "a1_ability": {
        "a1_state": ["high", "moderate", "low", "unknown"],
        "a1_reason": ["income", "money_in", "money_out", "cross_product", "distress"],
        "a1_unknown_reason": ["no_casa", "dormant_casa"],
        "a1_income_level": ["stable", "weak", "none"],
        "a1_money_in_level": ["strong", "some", "none", "NULL"],
        "a1_money_out_level": ["strong", "some", "none", "NULL"],
        "a1_cross_product_level": ["strong", "some", "none"],
        "a1_points_total": [0, 2, 4, 6],
        "a1_distress_flag": [0, 1],
        "a1_sweepable_balance_flag": [0, 1],
        "a1_eosb_flag": [0, 1],
        "a1_income_source": ["internal", "bureau", "both", "none"],
        "a1_salary_stopped": [0, 1],
        "liquidity_anchor_amt": ["NULL", "value"],
    },
    "a1_liquidity_anchor": {"liquidity_anchor_amt": ["NULL", "value"]},
    "a3_payment_credibility": {
        "a3_state": [f"payment_credibility_{s}" for s in ("high", "moderate", "low",
                                                          "unknown")],
        "a3_commitments_level": ["kept", "partly_kept", "thin", "broken"],
        "a3_dlq_payment_level": ["regular", "some", "none"],
        "a3_pre_dlq_payment_level": ["clean", "not_clean", "no_record"],
        "pre_dlq_reason": ["no_episode", "censored", "NULL"],
        "a3_unknown_reason": ["no_episode", "NULL"],
        "a3_override": ["refusal", "NULL"],
        "a3_promise_deadline": ["next_statement", "month_end", "next_month_end",
                                "30_days", "30_days_month_end"],
        "last_rpc_disposition": ["paid", "refusal", "dispute", "hung_up", "ptp",
                                 "success", "NULL"],
        "a3_refusal_flag": [True, False],
        "refusal_followed_by_plan": [True, False],
        "refusal_followed_by_payment": [True, False],
        "a3_dispute_flag": [True, False],
        "a3_hung_up_last": [True, False],
        "a3_no_pickup_after_contact": [True, False],
        "episode_left_censored": [True, False, "NULL"],
        "a3_points_total": [-1, 0, 1, 2, 3, 4, 5],
    },
    "a3_promise_events": {
        "event_kind": ["matched", "table_only", "followup_only"],
        "event_source": ["ptp", "settlement", "followup"],
        "promise_outcome": ["paid", "partial", "none"],
    },
    "cross_product_monthly": {
        "product_type": ["deposit", "investment", "wm", "card", "loan"],
        "is_current": [0, 1, "NULL"],
    },
    "card_month_end": {"minimum_due": ["NULL", "value"]},
    "bureau_salary_monthly": {
        "salary_source": ["alert", "salary_credit", "bureau_salary"]
    },
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
        "build_status": ["ok", "no_valid_rows", "no_rows_in_window",
                         "dropped_unresolvable_gap"],
        "history_cropped": [True, False],
        "restructure_blind_spot_flag": [0, 1],
        "legacy_drop": [True, False],
    },
    "a4_deterioration": {
        "det_state": ["unknown", "early_payment_default", "stabilized",
                      "repeat_delinquent", "straight_roller_seasoned",
                      "straight_roller_early_life", "slow_roller"],
        "restructure_blind_spot_flag": [0, 1],
        "chain_stitched_flag": [0, 1],
    },
    "restructure_chains": {"chain_n_originals": [1, 2]},
}  # fmt: skip
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


def _probe_two_runs(frame) -> bool:
    """D-A3-29: two follow-up events of one account less than 8 days apart (only a
    deadline between them splits a run)."""
    fu = frame.where("event_kind = 'followup_only'").select("account_id", "event_date")
    pairs = fu.alias("a").join(fu.alias("b"), "account_id")
    gap = F.datediff("b.event_date", "a.event_date")
    return bool(pairs.where((gap > 0) & (gap <= 7)).limit(1).count())


# Branches the state columns cannot show: (kind, label, test on the frame).
PROBES = [
    ("a3_promise_events",
     "D-A3-29: a follow-up after the run's deadline starts an event",
     _probe_two_runs),
    ("a3_promise_events", "next-statement fallback: no statement after the promise"
     " (cutoff = day + 31)",
     lambda f: bool(f.where(F.datediff("promise_cutoff", "event_date") == 31)
                    .limit(1).count())),
    ("a3_promise_events", "event outside the 12-month window (not counted)",
     lambda f: bool(f.where("event_date < '2025-09-01'").limit(1).count())),
    ("a3_payment_credibility", "refusal demotes a rung (points >= 2, Low or Moderate)",
     lambda f: bool(f.where("a3_override = 'refusal' AND a3_points_total >= 2")
                    .limit(1).count())),
    ("a3_payment_cycles", "bucket-08 due: due from the minimum-due baseline",
     lambda f: bool(f.where("billed_amount IS NULL AND due_amount IS NOT NULL")
                    .limit(1).count())),
    ("a3_dlq_cycles", "RL EMI missing: the last known EMI carries",
     lambda f: bool(f.where("cycle_end >= '2026-05-31'").groupBy("account_id")
                    .agg(F.countDistinct("due_amount").alias("n"))
                    .where("n = 1").limit(1).count())),
    ("transactions", "post-block fee row flagged",
     lambda f: bool(f.where("is_post_block_x_fee = 1").limit(1).count())),
    ("billing", "latest cycle has no next statement",
     lambda f: bool(f.where("next_billing_date IS NULL").limit(1).count())),
    ("limits", "limits pivoted from non-censored spells",
     lambda f: bool(f.limit(1).count())),
    ("bureau_bounces_monthly", "two cheques on one day count once",
     lambda f: bool(f.where("cif_id = '9' AND bounce_events = 1"
                            " AND max_bounce_amount = 800").limit(1).count())),
]  # fmt: skip


def _kind(name: str) -> str:
    """``crx_cc_a1_ability`` -> ``a1_ability``; ``feat_cif_x`` -> ``x``."""
    for prefix in ("crx_cc_", "crx_rl_", "feat_cif_", "prm_"):
        if name.startswith(prefix):
            return name[len(prefix) :]
    return name


def coverage(name: str, frame) -> dict[str, set]:
    """Values the state columns of dataset ``name`` take, counters above 0, probes."""
    kind = _kind(name)
    seen: dict[str, set] = {}
    for col in [c for c in STATE_COLUMNS.get(kind, {}) if c in frame.columns]:
        values = {r[0] for r in frame.select(col).distinct().collect()}
        if col in ("liquidity_anchor_amt", "minimum_due"):
            values = {"NULL" if v is None else "value" for v in values}
        elif col == "deceased_source":
            values = {s for v in values if v for s in v.split(",")}
        seen[col] = {"NULL" if v is None else v for v in values}
    for col in RULE_COUNTERS.get(kind, []):
        if frame.filter(F.col(col).cast("int") > 0).limit(1).count():
            seen.setdefault("rule counters > 0", set()).add(col)
    for probe_kind, label, test in PROBES:
        if probe_kind == kind and test(frame):
            seen.setdefault("probes", set()).add(label)
    return seen


NOT_COVERED = [
    "`feat_cif_casa.py` lines 438-487 are not photographed, so `casa_features` is not"
    " run: A1 reads synthetic feature tables built by the spec test's calls to the CASA"
    " builders (`build_casa_balance`, `build_casa_flow_legs`, `build_casa_flows`,"
    " `build_returns`, `build_internal_salary`). Tier A is reviewed only, never"
    " edited.",
    "Stand-ins for workplace modules the mirror lacks (simple, deterministic; the"
    " oracle"
    " checks our code around them): " + "; ".join(STUBBED) + ".",
    "`casa_primary`, `location_features`, `digital_login`: not run (A2 reads the spec"
    " test's `feat_cif_location_monthly`; tier X).",
    "A1 `build_distress_signals(payment_order=...)` and other optional sources not"
    " wired in any pipeline.",
    "`dpd_journey.cc_history_floor_date_180_plus` set apart from the 60-180 floor (same"
    " default; the alt run changes only the shared keys).",
    "`log_latest_month` / `log_stats` / `_log_state_stats`: logging only, run but not"
    " checked.",
    "Guards are checked by exception only (the run must raise); the returns-coverage"
    " guard of `build_distress_signals` is checked by a1_engine_spec.py.",
    "Options no pipeline passes: `build_contact_signals(max_months=None)`, the"
    " `next_statement` deadline for RL, the alternative deadlines at 180+ (they run at"
    " 60-180 only), `create_pipeline(output=...)` names other than the default.",
    "`product_features`' card minimum due and `crx_cc_balance` come through the"
    " `prm_cc` stand-in: the oracle fixes what our code does with them, not Way4's"
    " derivation.",
    "Dead candidates (`cc_spell`, `rl_spell_table`, `rl_a4_spine`, `_spine_utils`) are"
    " not run; `crx_cc_limits` (no reader) is run from a synthetic spell table.",
]


def write_coverage(seen: dict, timings: dict) -> None:
    """``harness_coverage.md``: values reached per dataset kind, and what is not."""
    lines = [
        "# Behaviour oracle coverage",
        "",
        "Generated by `checks/refactor_golden.py --record` (do not edit by hand). Per",
        "output kind (CC and RL, every model_id together): the values each state",
        "column reaches; **not reached** marks a gap. Then the probes (branches a",
        "column cannot show) and what the oracle does not cover.",
        "",
        "## Runs",
        "",
        "| Run | Datasets | Seconds |",
        "|---|---|---|",
        *[f"| `{r}` | {n} | {s:.1f} |" for r, (n, s) in timings.items()],
        "",
    ]
    for kind in sorted(STATE_COLUMNS.keys() | RULE_COUNTERS.keys()):
        lines += [f"## {kind}", ""]
        expected = {**STATE_COLUMNS.get(kind, {})}
        if kind in RULE_COUNTERS:
            expected["rule counters > 0"] = RULE_COUNTERS[kind]
        got_kind = seen.get(kind, {})
        for col, values in expected.items():
            got = got_kind.get(col, set())
            missing = [v for v in values if v not in got]
            note = (
                f" — **not reached: {', '.join(map(str, missing))}**" if missing else ""
            )
            reached = ", ".join(str(v) for v in values if v in got) or "(none)"
            lines.append(f"- `{col}`: {reached}{note}")
        lines.append("")
    lines += ["## Probes", ""]
    for kind, label, _ in PROBES:
        hit = label in seen.get(kind, {}).get("probes", set())
        lines.append(f"- {'reached' if hit else '**not reached**'}: `{kind}` — {label}")
    lines += ["", "## Not covered", "", *[f"- {n}" for n in NOT_COVERED], ""]
    (OUT / "harness_coverage.md").write_text("\n".join(lines))


def main() -> int:  # pylint: disable=too-many-locals
    record = "--record" in sys.argv
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else ""
    manifest_path = OUT / "manifest.json"
    manifest = {} if record else json.loads(manifest_path.read_text())
    problems, seen, timings = [], {}, {}
    start_all = time.perf_counter()
    for run, pipeline, model_id, params, inputs in runs():
        if only not in run:
            continue
        start = time.perf_counter()
        outputs = run_pipeline(pipeline, model_id, params, inputs())
        for name, frame in outputs.items():
            frame = frame.persist()
            path = GOLDEN / run / f"{name}.parquet"
            for col, values in coverage(name, frame).items():
                seen.setdefault(_kind(name), {}).setdefault(col, set()).update(values)
            if record:
                frame.coalesce(1).write.mode("overwrite").parquet(str(path))
                manifest.setdefault(run, {})[name] = {
                    "rows": frame.count(),
                    "schema": schema(frame),
                    "hash": content_hash(frame),
                }
            else:
                entry = manifest.get(run, {}).get(name)
                problems += compare(f"{run}/{name}", frame, path, entry)
            frame.unpersist()
        spark.catalog.clearCache()
        timings[run] = (len(outputs), time.perf_counter() - start)
        print(f"{run:<55} {len(outputs):>2} datasets  {timings[run][1]:5.1f}s")
    if not only:
        for label, pipeline, model_id, params, inputs in guards():
            try:
                run_pipeline(pipeline, model_id, params, inputs)
                problems.append(f"guard did not fire: {label}")
            except Exception as exc:  # pylint: disable=broad-except
                print(f"guard ok: {label} ({type(exc).__name__})")
    if record:
        manifest_path.write_text(json.dumps(manifest, indent=1, sort_keys=True) + "\n")
        write_coverage(seen, timings)
        print(f"recorded {sum(map(len, manifest.values()))} datasets to {GOLDEN}")
    for line in problems:
        print(f"DIFF {line}")
    total = sum(n for n, _ in timings.values())
    print(f"golden: {'FAIL' if problems else 'pass'} ({total} datasets,"
          f" {time.perf_counter() - start_all:.0f}s)")  # fmt: skip
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
