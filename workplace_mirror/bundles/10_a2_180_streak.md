# Mirror bundle 10 — A2: 6 failed call days at 180+ (GRR)

apply_bundle version: 7 · built 2026-10-30 from `da7aa67..584d5b2` · source: 0 added, 1 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/a2_180_streak
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/10_a2_180_streak.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '10_a2_180_streak.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/10_a2_180_streak.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Workbook (UAT Sonnet).** Give the UAT Sonnet the prompt in
`workplace_mirror/bundle_helpers/b10_a2/sonnet_a2_workbook_180_streak_prompt.md` (GitHub, raw). It
updates your copy of `a2_locatability_reference.xlsx`, keeping your edits and results.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Mirror bundle 10: A2: 6 failed call days at 180+ (GRR)" && git push -u origin feature/a2_180_streak
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/10_a2_180_streak.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/a2_180_streak && git pull
```

No PROD check for this bundle: the only change is at 180+, and no 180+ A2 output exists yet. The
60–180 runs need nothing new. The 180+ model_ids pick up the 6-day streak on their first A2 run.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

GRR accepted the A2 logic with one change: at 180+ the failed-call-day streak for Non-Reachable is 6,
not 3 (D-A2-20). `GONE_DARK_DAYS` is now per segment (3 at 60–180, 6 at 180+), read through
`gone_dark_days(model_id)`; `build_dcore_signals` uses it. Nothing
changes at 60–180: `cc_60_180` and `rl_60_180` outputs stay as they are, so bundle 06 step 8 and
the RL product and v04 snippets are unaffected. `b06_check.py` is not in this bundle: the bundle 06 cleanup
already removed it. `apply_bundle.py` v7 no longer crashes on a file missing here.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. A `MERGED` file differed from the copy
   this bundle was built from; show the user its `git diff` before committing.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py`
action: replace · base sha256 `7d32d2bf2f4cef3771ac80f5a95f7a9e45083dbb1ec8717e38c5d36b0f449f3b` · base trailing newline: yes · new sha256 `ceb4de3b20175bdef9e0400726af052224b9522e9c8ce001d43a0b2aef6f8c4d` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history (no T0);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, require_columns, window_months
from .codes import (
    CALL_CODES,
    DECEASED,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SKIP_TRACE,
    SUCCESS_CATEGORY,
)

# Travel rule (L2): the latest UAE evidence at most this many months after the last
# ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
# Non-Reachable: the last this-many call days all failed.
GONE_DARK_DAYS = 3
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _window_start(months: int) -> Column:
    """First day of the observation's W-month window."""
    return F.add_months(F.trunc(F.col("observation_date"), "month"), 1 - months)


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
    L3 in_country  the latest UAE evidence is in W
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    latest = (
        obs.join(location_features, on="cif_id")
        .filter(F.col("month_end") <= F.col("observation_date"))
        .groupBy(*GRAIN)
        .agg(
            _latest("last_uae_date", "last_uae_source").alias("_uae"),
            _latest("last_foreign_date", "last_foreign_source").alias("_foreign"),
            F.max("last_travel_date").alias("last_travel_date"),
        )
        .select(
            *GRAIN,
            F.col("_uae.last_uae_date").alias("last_uae_date"),
            F.col("_uae.last_uae_source").alias("last_uae_source"),
            F.col("_foreign.last_foreign_date").alias("last_foreign_date"),
            F.col("_foreign.last_foreign_source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )
    uae, foreign, travel = (
        F.col("last_uae_date"),
        F.col("last_foreign_date"),
        F.col("last_travel_date"),
    )
    obs_date = F.col("observation_date")
    rule = (
        F.when(foreign.isNotNull() & (uae.isNull() | (foreign >= uae)), "L1")
        .when(
            travel.isNotNull()
            & (
                uae.isNull()
                | (
                    (uae <= F.add_months(travel, TRAVEL_GAP_MONTHS))
                    & (uae <= F.add_months(obs_date, -TRAVEL_SILENCE_MONTHS))
                )
            ),
            "L2",
        )
        .when(uae >= _window_start(window_months(model_id)), "L3")
        .otherwise("L4")
    )
    return (
        left_join_all(obs_base, [latest])
        .withColumn("location_rule", rule)
        .withColumn(
            "location_state",
            F.when(F.col("location_rule").isin("L1", "L2"), "skip")
            .when(F.col("location_rule") == "L3", "in_country")
            .otherwise("unknown"),
        )
        .withColumn(
            "location_unknown_reason",
            F.when(F.col("location_rule") != "L4", None)
            .when(uae.isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Each observation row's DCORE events dated on or before it: ``day``,
    ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when missing)."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    events = followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
    return (
        obs_base.select(*GRAIN)
        .join(events, on="account_id")
        .filter(F.col("day") <= F.col("observation_date"))
    )


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``codes.FAILED_CALL``) and no contact was confirmed. A contact is an
    inbound call, an outbound call in category SUC, or a right-party result.

    non_reachable  the last GONE_DARK_DAYS call days all failed, the oldest in W, and no
                   contact since
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = _window_start(window_months(model_id))
    events = _dcore_events(obs_base, followup, agreements)
    name = F.col("name")
    code = F.col("action_code")
    calls = events.filter(
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = code.isin(*OUTBOUND_CODES)
    contact = (
        code.isin(*INBOUND_CODES)
        | (outbound & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    days = (
        calls.groupBy(*GRAIN, "day")
        .agg(
            F.max(outbound.cast("int")).alias("_attempt"),
            F.max(contact.cast("int")).alias("_contact"),
            F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
                "_all_failed"
            ),
        )
        .withColumn(
            "_failed",
            ((F.col("_contact") == 0) & (F.col("_all_failed") == 1)).cast("int"),
        )
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last_days = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= GONE_DARK_DAYS)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n_last"),
            F.sum("_failed").alias("_failed_last"),
            F.min("day").alias("_oldest_last"),
        )
    )
    day = F.col("day")
    calls_summary = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact") == 1, day)).alias("last_contact_date"),
        F.max(F.when(F.col("_attempt") == 1, day)).alias("last_attempt_date"),
        F.count(F.when((F.col("_attempt") == 1) & (day >= w_start), day)).alias(
            "attempt_days_in_window"
        ),
    )
    records = events.groupBy(*GRAIN).agg(
        F.max(F.when(name.isin(*DECEASED), day)).alias("dcore_deceased_date"),
        F.max(F.when(name.isin(*SKIP_TRACE), day)).alias("last_skip_trace_date"),
        F.lit(1).alias("_dcore_record"),
    )
    last_contact = F.col("last_contact_date")
    gone_dark = (
        (F.col("_n_last") == GONE_DARK_DAYS)
        & (F.col("_failed_last") == GONE_DARK_DAYS)
        & (F.col("_oldest_last") >= w_start)
        & (last_contact.isNull() | (last_contact < F.col("_oldest_last")))
    )
    return (
        left_join_all(obs_base, [records, calls_summary, last_days])
        .withColumn(
            "reachability_state",
            F.when(gone_dark, "non_reachable")
            .when(last_contact >= w_start, "reachable")
            .otherwise("unknown"),
        )
        .withColumn(
            "reachability_unknown_reason",
            F.when(F.col("reachability_state") != "unknown", None)
            .when(F.col("_dcore_record").isNull(), "no_dcore_record")
            .otherwise("no_contact_in_window"),
        )
        .withColumn(
            "attempt_days_in_window", F.coalesce("attempt_days_in_window", F.lit(0))
        )
        .drop("_dcore_record", "_n_last", "_failed_last", "_oldest_last")
    )


# ── Deceased (Way4, demographics) ─────────────────────────────────────────────


def build_way4_deceased(
    obs_base: DataFrame, contracts: DataFrame, clients: DataFrame
) -> DataFrame:
    """``way4_deceased_flag``: block code 2 = D on the latest ``prm_contract`` snapshot on
    or before the observation date, on any of the customer's cards. Rows with a card
    only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    cifs = obs.select("cif_id").distinct()
    snapshots = contracts.select(
        F.col("contract_id").cast("string").alias("contract_id"),
        "client_id",
        F.to_date("observation_date").alias("snapshot_date"),
        F.upper(F.trim("block_code_2")).alias("block_code_2"),
    )
    cards = (
        snapshots.select("contract_id", "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select("contract_id", "cif_id")
    )
    deceased = F.coalesce(F.col("block_code_2") == WAY4_DECEASED_BLOCK, F.lit(False))
    latest = Window.partitionBy(*GRAIN, "contract_id").orderBy(
        F.col("snapshot_date").desc(), deceased.desc()
    )
    return (
        obs.join(cards, on="cif_id")
        .join(snapshots.drop("client_id"), on="contract_id")
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .groupBy(*GRAIN)
        .agg(F.max(deceased.cast("int")).alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag``: ``ft_deceased_flag`` of the customer (a death is
    permanent: the largest value per CIF, no date). Rows with a demographics record
    only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    flags = demographics.groupBy(F.col("cif_id").cast("string").alias("cif_id")).agg(
        F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
            "demographics_deceased_flag"
        )
    )
    return (
        obs_base.filter(F.col("cif_id").isNotNull())
        .select(*GRAIN, "cif_id")
        .join(flags, on="cif_id")
        .select(*GRAIN, "demographics_deceased_flag")
    )
`````

New:

`````python
"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history (no T0);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, require_columns, window_months
from .._dpd_journey.constants import MODEL_ID_SEGMENT
from .codes import (
    CALL_CODES,
    DECEASED,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SKIP_TRACE,
    SUCCESS_CATEGORY,
)

# Travel rule (L2): the latest UAE evidence at most this many months after the last
# ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
# Non-Reachable: the last this-many call days all failed, per segment.
GONE_DARK_DAYS = {"60_180": 3, "180_plus": 6}
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _window_start(months: int) -> Column:
    """First day of the observation's W-month window."""
    return F.add_months(F.trunc(F.col("observation_date"), "month"), 1 - months)


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
    L3 in_country  the latest UAE evidence is in W
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    latest = (
        obs.join(location_features, on="cif_id")
        .filter(F.col("month_end") <= F.col("observation_date"))
        .groupBy(*GRAIN)
        .agg(
            _latest("last_uae_date", "last_uae_source").alias("_uae"),
            _latest("last_foreign_date", "last_foreign_source").alias("_foreign"),
            F.max("last_travel_date").alias("last_travel_date"),
        )
        .select(
            *GRAIN,
            F.col("_uae.last_uae_date").alias("last_uae_date"),
            F.col("_uae.last_uae_source").alias("last_uae_source"),
            F.col("_foreign.last_foreign_date").alias("last_foreign_date"),
            F.col("_foreign.last_foreign_source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )
    uae, foreign, travel = (
        F.col("last_uae_date"),
        F.col("last_foreign_date"),
        F.col("last_travel_date"),
    )
    obs_date = F.col("observation_date")
    rule = (
        F.when(foreign.isNotNull() & (uae.isNull() | (foreign >= uae)), "L1")
        .when(
            travel.isNotNull()
            & (
                uae.isNull()
                | (
                    (uae <= F.add_months(travel, TRAVEL_GAP_MONTHS))
                    & (uae <= F.add_months(obs_date, -TRAVEL_SILENCE_MONTHS))
                )
            ),
            "L2",
        )
        .when(uae >= _window_start(window_months(model_id)), "L3")
        .otherwise("L4")
    )
    return (
        left_join_all(obs_base, [latest])
        .withColumn("location_rule", rule)
        .withColumn(
            "location_state",
            F.when(F.col("location_rule").isin("L1", "L2"), "skip")
            .when(F.col("location_rule") == "L3", "in_country")
            .otherwise("unknown"),
        )
        .withColumn(
            "location_unknown_reason",
            F.when(F.col("location_rule") != "L4", None)
            .when(uae.isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Each observation row's DCORE events dated on or before it: ``day``,
    ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when missing)."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    events = followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
    return (
        obs_base.select(*GRAIN)
        .join(events, on="account_id")
        .filter(F.col("day") <= F.col("observation_date"))
    )


def gone_dark_days(model_id: str) -> int:
    """The failed-call-day streak that makes ``model_id``'s segment Non-Reachable."""
    return GONE_DARK_DAYS[MODEL_ID_SEGMENT[model_id]]


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``codes.FAILED_CALL``) and no contact was confirmed. A contact is an
    inbound call, an outbound call in category SUC, or a right-party result.

    non_reachable  the last ``gone_dark_days`` call days all failed, the oldest in W,
                   and no contact since
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = _window_start(window_months(model_id))
    streak = gone_dark_days(model_id)
    events = _dcore_events(obs_base, followup, agreements)
    name = F.col("name")
    code = F.col("action_code")
    calls = events.filter(
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = code.isin(*OUTBOUND_CODES)
    contact = (
        code.isin(*INBOUND_CODES)
        | (outbound & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    days = (
        calls.groupBy(*GRAIN, "day")
        .agg(
            F.max(outbound.cast("int")).alias("_attempt"),
            F.max(contact.cast("int")).alias("_contact"),
            F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
                "_all_failed"
            ),
        )
        .withColumn(
            "_failed",
            ((F.col("_contact") == 0) & (F.col("_all_failed") == 1)).cast("int"),
        )
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last_days = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= streak)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n_last"),
            F.sum("_failed").alias("_failed_last"),
            F.min("day").alias("_oldest_last"),
        )
    )
    day = F.col("day")
    calls_summary = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact") == 1, day)).alias("last_contact_date"),
        F.max(F.when(F.col("_attempt") == 1, day)).alias("last_attempt_date"),
        F.count(F.when((F.col("_attempt") == 1) & (day >= w_start), day)).alias(
            "attempt_days_in_window"
        ),
    )
    records = events.groupBy(*GRAIN).agg(
        F.max(F.when(name.isin(*DECEASED), day)).alias("dcore_deceased_date"),
        F.max(F.when(name.isin(*SKIP_TRACE), day)).alias("last_skip_trace_date"),
        F.lit(1).alias("_dcore_record"),
    )
    last_contact = F.col("last_contact_date")
    gone_dark = (
        (F.col("_n_last") == streak)
        & (F.col("_failed_last") == streak)
        & (F.col("_oldest_last") >= w_start)
        & (last_contact.isNull() | (last_contact < F.col("_oldest_last")))
    )
    return (
        left_join_all(obs_base, [records, calls_summary, last_days])
        .withColumn(
            "reachability_state",
            F.when(gone_dark, "non_reachable")
            .when(last_contact >= w_start, "reachable")
            .otherwise("unknown"),
        )
        .withColumn(
            "reachability_unknown_reason",
            F.when(F.col("reachability_state") != "unknown", None)
            .when(F.col("_dcore_record").isNull(), "no_dcore_record")
            .otherwise("no_contact_in_window"),
        )
        .withColumn(
            "attempt_days_in_window", F.coalesce("attempt_days_in_window", F.lit(0))
        )
        .drop("_dcore_record", "_n_last", "_failed_last", "_oldest_last")
    )


# ── Deceased (Way4, demographics) ─────────────────────────────────────────────


def build_way4_deceased(
    obs_base: DataFrame, contracts: DataFrame, clients: DataFrame
) -> DataFrame:
    """``way4_deceased_flag``: block code 2 = D on the latest ``prm_contract`` snapshot on
    or before the observation date, on any of the customer's cards. Rows with a card
    only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    cifs = obs.select("cif_id").distinct()
    snapshots = contracts.select(
        F.col("contract_id").cast("string").alias("contract_id"),
        "client_id",
        F.to_date("observation_date").alias("snapshot_date"),
        F.upper(F.trim("block_code_2")).alias("block_code_2"),
    )
    cards = (
        snapshots.select("contract_id", "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select("contract_id", "cif_id")
    )
    deceased = F.coalesce(F.col("block_code_2") == WAY4_DECEASED_BLOCK, F.lit(False))
    latest = Window.partitionBy(*GRAIN, "contract_id").orderBy(
        F.col("snapshot_date").desc(), deceased.desc()
    )
    return (
        obs.join(cards, on="cif_id")
        .join(snapshots.drop("client_id"), on="contract_id")
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .groupBy(*GRAIN)
        .agg(F.max(deceased.cast("int")).alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag``: ``ft_deceased_flag`` of the customer (a death is
    permanent: the largest value per CIF, no date). Rows with a demographics record
    only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    flags = demographics.groupBy(F.col("cif_id").cast("string").alias("cif_id")).agg(
        F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
            "demographics_deceased_flag"
        )
    )
    return (
        obs_base.filter(F.col("cif_id").isNotNull())
        .select(*GRAIN, "cif_id")
        .join(flags, on="cif_id")
        .select(*GRAIN, "demographics_deceased_flag")
    )
`````

## Apply script

Written to `data/input/mirror_bundles/apply_bundle.py` by step 3.

`````python
"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

When a repo file differs from the copy the bundle was built from (an edit made at work, a
lint fix, a photo slip), the bundle still applies — it never stops on a difference:
  * replace: three-way merge (git merge-file) of this repo's file, the bundle's base copy and
    the bundle's new version. Edits made here survive wherever the bundle did not change the
    same lines; where both changed the same lines, the bundle's version wins.
  * delete: the file is deleted (git history keeps it).
  * add over an existing file: the bundle's version is written.
Each such file is listed as MERGED; review it with `git diff <path>` before committing.

Safety rules:
  * refuses to write on main/master, or when a touched file has uncommitted changes, so
    `git diff` shows exactly what the bundle did and --revert restores HEAD.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
"""

from __future__ import annotations

import argparse
import ast
import difflib
import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

APPLY_VERSION = 7
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


# Separator lines in comments (``# ── Node 1 ─────``, ``#######``) are transcribed from
# photos, where their exact length cannot be read. Runs of 4+ identical separator
# characters therefore compare equal whatever their length; so do trailing spaces.
_RULE_RUN = re.compile(r"([─━═=\-#*~_])\1{3,}")


def _loose(text: str) -> str:
    return "\n".join(
        _RULE_RUN.sub(r"\1\1\1\1", line.rstrip()) for line in _norm(text).split("\n")
    )


def _strip_docstrings(tree):
    for node in ast.walk(tree):
        body = getattr(node, "body", None)
        if (
            isinstance(body, list)
            and body
            and isinstance(body[0], ast.Expr)
            and isinstance(getattr(body[0], "value", None), ast.Constant)
            and isinstance(body[0].value.value, str)
        ):
            node.body = body[1:] or [ast.Pass()]
    return tree


def _same_code(path: str, a: str, b: str) -> bool:
    """Same Python code (comments and docstrings aside) or the same YAML content."""
    try:
        if path.endswith(".py"):
            return ast.dump(_strip_docstrings(ast.parse(a))) == ast.dump(
                _strip_docstrings(ast.parse(b))
            )
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(
        e["path"], current, e["new"]
    )


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml  # pylint: disable=import-outside-toplevel  # optional

            return yaml.safe_dump(yaml.safe_load(text), sort_keys=True)
    except Exception:  # pylint: disable=broad-except
        pass
    return _loose(text)


def _matches_base(current: str | None, e: dict) -> bool:
    """The repo file is the version the bundle was built from: identical up to
    separator lengths and trailing spaces, or — since comments and docstrings are
    transcribed from photos — the same code / YAML content."""
    if current is None:
        return False
    if _loose(current) == _loose(e["base"]):
        return True
    return _same_code(e["path"], current, e["base"])


def _rebase(new: str, base: str, current: str) -> str:
    """``new`` with every line the bundle did not change taken from ``current``.

    ``current`` matches ``base`` line by line up to separator lengths (``_matches_base``),
    so the repo's own separators survive and ``git diff`` shows only real changes.
    """
    base_l, new_l, cur_l = (_norm(t).split("\n") for t in (base, new, current))
    if len(cur_l) != len(base_l):  # comments wrapped differently: no line alignment
        return new
    out: list[str] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(
        None, base_l, new_l, autojunk=False
    ).get_opcodes():
        out += cur_l[i1:i2] if tag == "equal" else new_l[j1:j2]
    return "\n".join(out)


def _merge3(current: str, base: str, new: str) -> str:
    """Three-way merge: this repo's edits on top of the bundle's change (git merge-file;
    on overlapping lines the bundle's version wins). Without git: the bundle's version.
    """
    with tempfile.TemporaryDirectory() as tmp:
        paths = []
        for name, text in (("current", current), ("base", base), ("new", new)):
            f = pathlib.Path(tmp) / name
            f.write_text(_norm(text), encoding="utf-8")
            paths.append(str(f))
        try:
            out = subprocess.run(
                ["git", "merge-file", "-p", "--theirs", *paths],
                capture_output=True,
                check=False,
            )
        except OSError:
            return new
    return out.stdout.decode("utf-8") if out.returncode >= 0 else new


def _sha(text: str) -> str:
    return hashlib.sha256(_norm(text).encode("utf-8")).hexdigest()


def _read(path: pathlib.Path) -> str | None:
    if not path.is_file():
        return None
    return path.read_bytes().decode("utf-8")


# ── Parsing ──────────────────────────────────────────────────────────────────


def parse_bundle(md: str) -> list[dict]:
    """Return one dict per file: path, action, base/new sha and text."""
    lines = _norm(md).split("\n")
    entries, i = [], 0
    while i < len(lines):
        m = re.match(r"^### FILE: `([^`]+)`\s*$", lines[i])
        if not m:
            i += 1
            continue
        meta = lines[i + 1]
        entry = {
            "path": m.group(1),
            "action": re.search(r"action: (add|replace|delete)", meta).group(1),
            "base_sha": None,
            "new_sha": None,
            "base": None,
            "new": None,
        }
        for kind in ("base", "new"):
            sm = re.search(kind + r" sha256 `([0-9a-f]{64})`", meta)
            if sm:
                entry[kind + "_sha"] = sm.group(1)
        j = i + 2
        for kind in ("base", "new"):
            if entry[kind + "_sha"] is None:
                continue
            while not FENCE.match(lines[j]):
                j += 1
            fence = FENCE.match(lines[j]).group(1)
            k = j + 1
            while lines[k] != fence:
                k += 1
            body = "\n".join(lines[j + 1 : k])
            if re.search(kind + r" trailing newline: yes", meta) and body:
                body += "\n"
            entry[kind] = body
            j = k + 1
        entries.append(entry)
        i = j
    return entries


def verify_bundle(entries: list[dict]) -> list[str]:
    """Blocks whose content no longer matches the checksum (a damaged copy)."""
    errors = []
    for e in entries:
        for kind in ("base", "new"):
            if e[kind + "_sha"] and _sha(e[kind]) != e[kind + "_sha"]:
                errors.append(f"{e['path']}: {kind} block does not match its checksum")
    return errors


# ── Git guards ───────────────────────────────────────────────────────────────


def _git(*args: str) -> str | None:
    try:
        return subprocess.run(
            ["git", *args], capture_output=True, text=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None


def _head_version(path: str) -> str | None:
    """The committed (HEAD) content of a file, byte-exact, or None."""
    try:
        out = subprocess.run(
            ["git", "show", f"HEAD:{path}"], capture_output=True, check=True
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return out.decode("utf-8")


def git_problems(entries: list[dict]) -> list[str]:
    """Reasons to refuse: a protected branch, or uncommitted edits in a touched file."""
    problems = []
    branch = _git("rev-parse", "--abbrev-ref", "HEAD")
    if branch is not None:
        branch = branch.strip()
    if branch is None:
        print("note: not a git repository (or git missing) — branch checks skipped")
        return problems
    if branch in PROTECTED_BRANCHES:
        problems.append(
            f"you are on '{branch}' — create a branch first: git checkout -b <name>"
        )
    # Files already in their final state may be uncommitted (applied, not yet committed).
    pending = [e["path"] for e in entries if file_status(e) != "done"]
    dirty = _git("status", "--porcelain", "--", *pending) if pending else ""
    for line in (dirty or "").splitlines():
        if line[:2] != "??":  # untracked files are compared by content below
            problems.append(f"uncommitted change in a touched file: {line[3:]}")
    return problems


# ── Status ───────────────────────────────────────────────────────────────────


def file_status(e: dict) -> str:  # pylint: disable=too-many-return-statements
    """One of: todo, done, merge (the repo file differs from the bundle's base copy)."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "merge"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "merge"
    # delete
    if current is None:
        return "done"
    return "todo" if _matches_base(current, e) else "merge"


def explain_merge(e: dict) -> None:
    """One line on what happened to a file that differed from the bundle's copy."""
    what = {
        "replace": "merged with this repo's own edits",
        "delete": "deleted, although it had edits the bundle's copy lacks (git keeps them)",
        "add": "already existed with other content; replaced by the bundle's version",
    }[e["action"]]
    print(f"MERGED {e['path']}: {what} — review: git diff -- {e['path']}")


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    """One line per bundle file: its action and status."""
    word = {
        "todo": "will apply",
        "done": "already applied",
        "merge": "will apply — MERGED (differs from the bundle's copy)",
    }
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        note = ""
        if s == "todo" and _comment_only(e):
            note = "  (comments differ from the bundle's copy — fine)"
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}{note}")


# ── Post-apply checks ────────────────────────────────────────────────────────


def _module_name(path: str) -> str | None:
    p = pathlib.PurePosixPath(path)
    if p.suffix != ".py" or p.parts[0] != "src":
        return None
    parts = list(p.with_suffix("").parts[1:])
    if parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def compile_and_import(entries: list[dict], do_import: bool) -> list[str]:
    """Compile every touched .py file and import its module (plus the registry)."""
    failures = []
    existing = [
        e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")
    ]
    for e in existing:
        try:
            compile(_read(pathlib.Path(e["path"])), e["path"], "exec")
        except SyntaxError as exc:
            failures.append(f"compile: {e['path']}: {exc}")
    if not do_import or failures:
        return failures
    modules = [m for m in (_module_name(e["path"]) for e in existing) if m]
    if pathlib.Path("src/enbd_collections/pipeline_registry.py").is_file():
        modules.append("enbd_collections.pipeline_registry")
    env = dict(os.environ)
    env["PYTHONPATH"] = "src" + os.pathsep + env.get("PYTHONPATH", "")
    for mod in dict.fromkeys(modules):
        r = subprocess.run(
            [sys.executable, "-c", f"import {mod}"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    """Dry run: what --apply would do; False only when git refuses."""
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for p in problems:
        print("REFUSED: " + p)
    print(
        f"\n{statuses.count('todo') + statuses.count('merge')} to apply "
        f"({statuses.count('merge')} merged), {statuses.count('done')} already applied"
    )
    print("CHECK FAILED — nothing was written" if problems else "CHECK PASSED")
    return not problems


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    """Write every file (merging where this repo differs), then verify and import."""
    if not cmd_check(entries):
        return False
    merged = []
    for e in entries:
        status = file_status(e)
        if status == "done":
            continue
        path = pathlib.Path(e["path"])
        if status == "merge":
            merged.append(e)
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
            continue
        new = e["new"]
        if e["action"] == "replace":
            current = _read(path)
            if status == "todo":
                new = _rebase(new, e["base"], current)
            elif current is not None:  # a file missing here gets the bundle's version
                new = _merge3(current, e["base"], new)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(new.encode("utf-8"))
    print()
    for e in merged:
        explain_merge(e)
    # a merged file keeps this repo's own edits, so it need not equal the bundle's version
    merged_paths = {e["path"] for e in merged if e["action"] == "replace"}
    bad = [
        e["path"]
        for e in entries
        if e["path"] not in merged_paths and file_status(e) != "done"
    ]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(
        f"{len(entries)} files in their new state, compile OK"
        + (", imports OK" if do_import else " (imports skipped)")
    )
    print(
        "APPLY PASSED — review with `git status` / `git diff`"
        + (f" (look closely at the {len(merged)} MERGED files)" if merged else "")
    )
    return True


def cmd_revert(entries: list[dict]) -> bool:
    """Put every touched file back to HEAD (apply refuses to run over uncommitted changes,
    so HEAD is the state before --apply); files the bundle added are removed."""
    for e in entries:
        path = pathlib.Path(e["path"])
        committed = _head_version(e["path"])
        if committed is not None:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(committed.encode("utf-8"))
        elif path.exists():
            path.unlink()
            _prune_empty_dirs(path.parent)
    print("REVERT DONE — `git status` should show none of the bundle's files")
    return True


def main() -> int:
    """Parse the arguments, verify the bundle's checksums and run the chosen mode."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--revert", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    args = ap.parse_args()

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(
            f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
            f"{APPLY_VERSION}. Redo step 3 of the bundle."
        )
        return 1
    entries = parse_bundle(md)
    if not entries:
        print("No files found — was the raw markdown copied (not the rendered page)?")
        return 1
    errors = verify_bundle(entries)
    if errors:
        for err in errors:
            print("DAMAGED: " + err)
        print("The bundle copy is damaged — recopy the RAW file. Nothing was written.")
        return 1
    if not pathlib.Path("src").is_dir():
        print("Run this from the workplace repo root (no src/ folder here).")
        return 1
    print(f"{len(entries)} files in bundle, all checksums OK\n")
    if args.check:
        ok = cmd_check(entries)
    elif args.apply:
        ok = cmd_apply(entries, do_import=not args.no_import)
    else:
        ok = cmd_revert(entries)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
`````

## Cleanup prompt

Copy this to the workplace assistant in UAT once the bundle's PROD checks are done:

````text
Clean up after mirror bundle 10_a2_180_streak.md, on the bundle's branch.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
