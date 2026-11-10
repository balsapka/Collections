# Mirror bundle 22 — A3: Unknown = no episode only (D-A3-27)

apply_bundle version: 7 · built 2026-11-10 from `17be2bf..7449f05` · source: 0 added, 2 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/22_a3_unknown_no_episode_only.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '22_a3_unknown_no_episode_only.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/22_a3_unknown_no_episode_only.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet: update the A3 tests to the new rule. A row inside an episode with thin promises, no payment while delinquent and no record before is `payment_credibility_low`, not Unknown, and `a3_unknown_reason` is NULL for it; a row with no episode stays Unknown with `no_episode`. The mirror's spec test (`workplace_mirror/checks/a3_engine_spec.py`, section 1 map) has the reference rule. Then check `grep -rn "no_evidence" src/enbd_collections/pipelines/crx_persona/a3_credibility` prints nothing.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A3: Unknown = no episode only; no payment while delinquent is evidence (D-A3-27)" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/22_a3_unknown_no_episode_only.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

No check pipeline: the change is reviewed in code. Write the real A3 output for **all four model_ids** (`cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus`; set `model_id` in `conf/dev/globals_dev.yml`):

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

The pipeline logs the latest month's state counts: paste them back for each model_id. Expected: Unknown falls to the `no_episode` rows only (loans 61–180 near 0), Low rises by the same count, High and Moderate unchanged.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Narrows A3 payment credibility's Unknown state to rows with no delinquency episode. Apply after bundle 20 (and its cleanup); it touches only A3 files, so its order against bundle 21 doesn't matter.

**What changes in the logic** (spec `specs/A3_credibility_spec.md`, D-A3-27):
- No payment while delinquent (Dimension B `none`) is evidence that scores 0 points. It is no longer a "silent" level.
- So a row with an observed episode and no points in any dimension (thin promises, no payment, no record before delinquency) is **Low**, not Unknown. These are mostly early payment defaults.
- Unknown stays only for rows with no episode anchor (`a3_unknown_reason = 'no_episode'`); the `no_evidence` reason no longer occurs.
- High and Moderate don't move; nothing else in the scoring changes.

**Code:** `a3_credibility/constants.py` (Dimension B has no silent level) and `a3_credibility/classify.py` (the `no_evidence` branch and docstring). No new datasets, no catalog or registry change, no temporary check.

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
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` |

## Files

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py`
action: replace · base sha256 `3bb4768508c4a274d4dda012b1bdae864d0ac953d54a974652794b3d8a3b91c2` · base trailing newline: yes · new sha256 `3dc6ee8cc85538d7f506d1800ff85a720d140e77c39a08456aac4ef5147fcf96` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    deadline: str,
    persona_end_date: str,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off. Unknown:
    no evidence in any dimension and no refusal, or no episode anchor (Q-12,
    ``a3_unknown_reason``).
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn("a3_promise_deadline", F.lit(deadline))
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason",
        F.when(no_episode, "no_episode").when(
            F.col("a3_state") == unknown, "no_evidence"
        ),
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", "A3 credibility", persona_end_date)
    return out
`````

New:

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    deadline: str,
    persona_end_date: str,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24, -27).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off. Unknown:
    no episode anchor only (``a3_unknown_reason`` = ``no_episode``); an episode with no
    evidence scores 0 points and is Low.
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn("a3_promise_deadline", F.lit(deadline))
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason", F.when(no_episode, "no_episode")
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", "A3 credibility", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py`
action: replace · base sha256 `53ffe52e1e082a62f5646c29641e84910e4a5edbc20f22bca6ae9517cea9ec62` · base trailing newline: yes · new sha256 `c3c26a1575e672d1ad29a362aa916db860bced579ec54bc5dd8e78850355dc24` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
FOLLOWUP_RUN_DAYS = 7  # follow-up promises less than 8 days apart are one event
MATCH_DAYS = 7  # a follow-up promise within 7 days of a DCORE plan is that plan
# The deadline a promise is judged by (GRR): CC the next statement after the promise
# day, however close; RL the end of the next month (RL cash is known by month only).
# The alternative is 30 days from the promise ("30_days"; RL "30_days_month_end").
DEADLINES = ("next_statement", "next_month_end", "30_days", "30_days_month_end")
PROMISE_DEADLINE = {"cc": "next_statement", "rl": "next_month_end"}
STATEMENT_FALLBACK_D = 31  # no statement after the promise day yet: 31 days

# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20; Q-28, Q-29, Q-30) ─────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of positive minimum due averaged (D-A3-12)

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, ("thin",)),
        Dimension(
            "dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ("none",)
        ),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

New:

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
FOLLOWUP_RUN_DAYS = 7  # follow-up promises less than 8 days apart are one event
MATCH_DAYS = 7  # a follow-up promise within 7 days of a DCORE plan is that plan
# The deadline a promise is judged by (GRR): CC the next statement after the promise
# day, however close; RL the end of the next month (RL cash is known by month only).
# The alternative is 30 days from the promise ("30_days"; RL "30_days_month_end").
DEADLINES = ("next_statement", "next_month_end", "30_days", "30_days_month_end")
PROMISE_DEADLINE = {"cc": "next_statement", "rl": "next_month_end"}
STATEMENT_FALLBACK_D = 31  # no statement after the promise day yet: 31 days

# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20; Q-28, Q-29, Q-30) ─────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of positive minimum due averaged (D-A3-12)

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, ("thin",)),
        # no silent level: no payment while delinquent is evidence (0 points), so an
        # episode row is never Unknown (D-A3-27)
        Dimension("dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ()),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
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
Clean up after mirror bundle 22_a3_unknown_no_episode_only.md, on the bundle's branch.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
