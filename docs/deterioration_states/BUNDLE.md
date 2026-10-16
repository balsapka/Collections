# Deterioration states — full source bundle

## Run this (from the repo root)

```bash
# 1. recreate every file and verify checksums  -> "N files OK, 0 mismatched"
python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md

# 2. self-test on synthetic data              -> "SELFTEST PASSED"  (~1 min)
python docs/deterioration_states/run.py selftest

# 3. optional: rebuild the synthetic method-validation report
python docs/deterioration_states/run.py synthetic
```

Step 1 needs `extract_bundle.py` — create it from the **Extractor** section below the first
time. Then fill in `dpd_states/config.py` and the `<<FILL-IN>>` in
`snippets/dpd_states_validate.py` (PROMPTS.md P1) and, in a Kedro notebook:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
from dpd_states_validate import main
main(catalog, check_only=True)   # dry run: schema, counts, example strings
result = main(catalog)           # full validation -> results/ (aggregates only)
```

---

Generated 2026-10-16 by `dpd_states/bundle.py`. 18 files, 3,756 lines.
This one markdown file contains **every source file** of `docs/deterioration_states/`, for
environments where `.py` files cannot be opened. Regenerate it after any change with
`python docs/deterioration_states/run.py bundle`.

## Instructions for the assistant recreating the files (read first)

1. **Do not retype the code.** Long files retyped by hand (or by a model) pick up small
   errors. Instead:
   - save this whole file, unchanged, as `docs/deterioration_states/BUNDLE.md` in the
     workplace repository (copy the **raw** markdown — e.g. GitHub's "Copy raw file"
     button — not the rendered page, which drops the code fences);
   - create `docs/deterioration_states/extract_bundle.py` with the extractor below;
   - run `python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md`.
2. The extractor writes every file and checks its SHA-256. It must end with
   **"N files OK, 0 mismatched"**. A mismatch means the copy of this markdown was altered
   (line endings, smart quotes, a rendered instead of raw copy) — recopy the raw file;
   do not hand-fix the code.
3. Then run the self-test — from any folder, e.g. the repo root:
   `python docs/deterioration_states/run.py selftest` → must print **SELFTEST PASSED**
   (needs pandas, numpy, scikit-learn; ~1 minute). Do not use `python -m dpd_states...`
   from the repo root: the package sits inside `docs/deterioration_states/`, so Python
   will not find it there.
4. Only after that, follow `PROMPTS.md` (P0 → P1 → P2). The only files to edit are
   `dpd_states/config.py` and the marked `<<FILL-IN>>` spot in
   `snippets/dpd_states_validate.py`.
5. Fallback, only if no script can be run: create each file below verbatim from its code
   block (the text between the fence lines, nothing else), then run the extractor's
   checksum part to confirm.

## Extractor

`````python
"""Recreate docs/deterioration_states/ from BUNDLE.md and verify every file.

Run from the repo root, in this order:

    1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
         -> must end with "N files OK, 0 mismatched"
    2. python docs/deterioration_states/run.py selftest
         -> must end with "SELFTEST PASSED" (~1 minute; needs pandas, numpy, scikit-learn)
    3. Fill in docs/deterioration_states/dpd_states/config.py and the <<FILL-IN>> in
       snippets/dpd_states_validate.py (PROMPTS.md P1), then in a Kedro notebook:
         main(catalog, check_only=True)   # dry run
         main(catalog)                    # full validation

Optional second argument writes somewhere else: extract_bundle.py BUNDLE.md <folder>
"""
import hashlib
import pathlib
import re
import sys

src = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.resolve().parent
lines = src.read_text(encoding="utf-8").split("\n")
ok = bad = 0
i = 0
while i < len(lines):
    m = re.match(r"^### FILE: `([^`]+)`\s*$", lines[i])
    if not m:
        i += 1
        continue
    rel = m.group(1)
    meta = lines[i + 1]
    sha = re.search(r"sha256 `([0-9a-f]{64})`", meta).group(1)
    trailing = "trailing newline: yes" in meta
    j = i + 2
    while not lines[j].startswith("`````"):
        j += 1
    fence = re.match(r"^(`+)", lines[j]).group(1)
    k = j + 1
    while lines[k] != fence:
        k += 1
    body = "\n".join(lines[j + 1:k])
    if body and trailing:
        body += "\n"
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body.encode("utf-8"))
    good = hashlib.sha256(body.encode("utf-8")).hexdigest() == sha
    ok += good
    bad += not good
    print(("OK       " if good else "MISMATCH ") + rel)
    i = k + 1
for d in re.findall(r"^- empty folder: `([^`]+)`", "\n".join(lines), flags=re.M):
    (root / d).mkdir(parents=True, exist_ok=True)
    (root / d / ".gitkeep").touch()
print(f"\n{ok} files OK, {bad} mismatched -> {root}")
if not bad:
    print("Next: python docs/deterioration_states/run.py selftest   (from the repo root)")
sys.exit(1 if bad else 0)
`````

## Folder structure

```
docs/deterioration_states/
├── README.md
├── run.py
├── METHODOLOGY.md
├── REVIEW.md
├── PROMPTS.md
├── dpd_states/__init__.py
├── dpd_states/config.py
├── dpd_states/features.py
├── dpd_states/states.py
├── dpd_states/analysis.py
├── dpd_states/expectations.py
├── dpd_states/file_mode.py
├── dpd_states/discover.py
├── dpd_states/synth.py
├── dpd_states/run_synthetic.py
├── dpd_states/selftest.py
├── dpd_states/bundle.py
├── snippets/dpd_states_validate.py
├── results/
├── validation/
```

- empty folder: `results`
- empty folder: `validation`

`results/` receives the real-data outputs; `validation/` holds the synthetic evidence
(regenerate with `python docs/deterioration_states/run.py selftest` and `... run.py synthetic`).

## Files

### FILE: `README.md`
sha256 `521f28f20b40038c3cabb9dd2f3703830472f143ff00baeccb05acf8d7845f60` · 115 lines · trailing newline: yes

`````markdown
# Deterioration states — DPD-journey states for the bucket 4–7 credit-card spine

One state per account, from the DPD bucket history alone, assigned by a short decision
tree (MECE, no residual behaviour bucket). Three options: **A** (4 states), **B** (6,
recommended), **C** (7). States use common card-risk names — early payment default
(formerly "bust-out"), stabilized, repeat delinquent, seasoned / early-life straight
roller, slow roller (partial payer); code names and display names are kept separate.

- Design, thresholds, evidence and everything tried and dropped: **[METHODOLOGY.md](METHODOLOGY.md)**
- Independent review — 24 findings and what was done: **[REVIEW.md](REVIEW.md)**
- Copy-paste prompts for running this at the workplace with Sonnet: **[PROMPTS.md](PROMPTS.md)**

## Quick start (from the repo root)

```bash
python docs/deterioration_states/run.py selftest    # must end "SELFTEST PASSED" (~1 min)
python docs/deterioration_states/run.py validate    # REAL data: INPUT_FILE / COL_DPD from config.py
```

`validate` reads `data/input/dpd_synthetic_data.xlsx`, column `dpd_history_str` (leftmost =
current month), crops it to the reliable window (2024-01 → 2026-08 = 32 months, set in
`config.py`), keeps today's spine (current bucket 4–7) and writes
`results/dpd_states_file_<file>_<date>.json` + `.md` (aggregates only). Another file:
`run.py validate path/to/file.xlsx`. Needs pandas, numpy, scikit-learn, and openpyxl for
`.xlsx`. A snapshot file has no outcomes, so roll-rate / exit checks are SKIPPED; the Spark
backtest (PROMPTS P6) adds them.

## Layout

```
deterioration_states/
├── README.md                 this file
├── run.py                    run the tools from ANY folder: validate | selftest | synthetic | bundle
├── METHODOLOGY.md            design, thresholds, dropped states + reasons, expectations
├── REVIEW.md                 independent review: findings and dispositions
├── PROMPTS.md                prompts for Sonnet 5 at the workplace (P0–P7)
├── BUNDLE.md                 ALL source files in one .md + extractor (for .py-blocked viewers)
├── dpd_states/               the package (pandas + numpy + scikit-learn; no Spark)
│   ├── config.py             ← the ONLY file to edit: input file / dataset + column names
│   ├── features.py           string → cleaning → encoding → journey features
│   ├── states.py             the state tree, options A/B/C, [business] thresholds, DISPLAY_NAMES / REMARKS
│   ├── analysis.py           real-data analysis: states, backtest / survivor checks, overlap, sweeps
│   ├── expectations.py       E01–E28: expected values with anchors, PASS/WARN/FAIL, "if not met"
│   ├── file_mode.py          run on an xlsx / csv / parquet file (no Spark)
│   ├── discover.py           shapes, n-gram motifs, clustering helpers
│   ├── synth.py              calibrated synthetic generator (method validation only)
│   ├── run_synthetic.py      method validation report  → validation/
│   ├── selftest.py           real-data code path on synthetic data + 24 edge-case regressions → validation/
│   └── bundle.py             rebuilds BUNDLE.md
├── snippets/
│   └── dpd_states_validate.py   Spark / Kedro entry point: main(catalog, model_id=None, ...)
├── validation/               evidence from synthetic runs (committed)
└── results/                  real-data outputs land here (aggregates only)
```

## Can't open .py files?

`BUNDLE.md` holds every source file in one markdown file plus a short extractor that
recreates the folder and verifies each file's SHA-256 — see the instructions at its top.
Regenerate it after any change: `python docs/deterioration_states/run.py bundle`.

## Assign states in your own code

```python
from dpd_states.analysis import clean_strings
from dpd_states.features import build_features
from dpd_states.states import assign_states, OPTIONS, DISPLAY_NAMES

s, ok = clean_strings(df.dpd_history_str, char_map={}, strip_chars=" ")
spine = df.assign(dpd_string=s)[ok & s.str[0].isin(list("4567"))]   # today's spine only
f = build_features(spine)
f["state"] = assign_states(f, **OPTIONS["B_balanced_6"])            # or A_minimal_4 / C_detailed_7
f["state_label"] = f.state.map(DISPLAY_NAMES)                       # business label for reports
```

`dpd_string` must be digits only, **leftmost = current month**, 0 and 1 both mean normal.
`build_features` raises a clear error for an account not in a delinquent spell.

## Spark mode (later, for outcomes and production)

1. Fill in `dpd_states/config.py` (dataset, key, optional as-of / snapshot columns) and the
   `globals_dev` accessor in `snippets/dpd_states_validate.py` → **PROMPTS.md P6**.
2. Dry run in a Kedro notebook — schema, counts, orientation, all as aggregates:
   ```python
   import sys, pathlib
   _c = pathlib.Path.cwd()
   ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
   sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
   from dpd_states_validate import main
   main(catalog, check_only=True)
   ```
3. Full run: `result = main(catalog)` — writes
   `results/dpd_states_validation_<model_id>_<date>.json` + `.md` and prints the checks
   between `=== DPD_STATES OUTPUT START/END ===`. Config edits apply on the next call (no
   kernel restart; a config fingerprint is printed).

## Rules this code follows

- **Read-only.** Nothing is written to the warehouse.
- **Aggregates only** in results — no account keys, no raw DPD strings (examples are banded
  journey shapes shared by ≥ 10 accounts).
- **`model_id` comes from the caller or `globals_dev`** (Spark mode), never hardcoded, and is
  in the output filename, the payload and the first printed line.
- **Scope first**, then sample (≤ `sample_n` rows, default 100k).
- **Never guess a dataset or column name** — every unknown is a `<<FILL-IN>>`.
- **[business] parameters** in `states.py` change only with the business owner.

## Tested / not tested

- `dpd_states` (features, states, analysis, expectations, file mode): tested end to end on
  synthetic data and a mock Excel file (Python 3.13, pandas 3.0, scikit-learn 1.9); the
  independent review also ran it on Python 3.10 / pandas 1.5.3.
- `snippets/dpd_states_validate.py`: the Spark part is **not executed here** (no Spark) —
  syntax-checked and reviewed by reading. The `check_only=True` dry run catches problems
  before the full run.
`````

### FILE: `run.py`
sha256 `dd2718c37073920057e7edff88d2efcced698e35a9c81b5869ba69c1e63cbf87` · 46 lines · trailing newline: yes

`````python
"""Run the package's tools from ANY folder (repo root, a notebook folder, anywhere):

    python docs/deterioration_states/run.py validate [file] [sample_n]   # REAL data from a file
    python docs/deterioration_states/run.py selftest [n_accounts]        # real-data path on synthetic data
    python docs/deterioration_states/run.py synthetic [n_accounts]       # method validation report
    python docs/deterioration_states/run.py bundle                       # rebuild BUNDLE.md

`validate` without a file reads INPUT_FILE / COL_DPD from dpd_states/config.py.
Equivalent to `python -m dpd_states.<tool>` run from inside docs/deterioration_states/.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # makes dpd_states importable

TOOLS = ("validate", "selftest", "synthetic", "bundle")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "validate":
        from dpd_states.file_mode import main as run
        args = sys.argv[2:]
        path = next((a for a in args if not a.isdigit()), None)
        n = next((int(a) for a in args if a.isdigit()), 100_000)
        run(path, sample_n=n)
        return 0
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 20_000
    if cmd == "selftest":
        from dpd_states.selftest import main as run
        return run(n)
    if cmd == "synthetic":
        from dpd_states.run_synthetic import main as run
        run(n)
        return 0
    if cmd == "bundle":
        from dpd_states.bundle import build
        print(build())
        return 0
    print(__doc__)
    print(f"unknown or missing tool {cmd!r}; choose one of {TOOLS}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
`````

### FILE: `METHODOLOGY.md`
sha256 `0fec7f3f70043efa4f79ecd65510f2e71497cd3ec6f7a5e71286378d9fe5fc75` · 476 lines · trailing newline: yes

`````markdown
# Deterioration states — methodology

How a credit-card account in buckets 4–7 fell into delinquency, and what it is doing now,
read from its DPD bucket history only. One state per account, assigned by a short
decision tree. MECE by construction, simple enough to explain to the risk team in one
slide, and designed to stay out of the way of the other persona axes.

> **Status.** Designed and validated on calibrated **synthetic** data, then independently
> reviewed (24 findings — see [REVIEW.md](REVIEW.md) for each finding and what was done).
> Not yet run on the bank's book. Every number marked *(synthetic)* is a *method check*,
> not a finding about the portfolio. The real-data run is `run.py validate` on a file
> (now) or `snippets/dpd_states_validate.py` on Spark (production); expectations in §8.

---

## 1. Where this sits among the persona axes

| Axis | Question it answers | Inputs |
|---|---|---|
| Locatability | Can we reach them? | Reachability flag, in-country flag |
| Ability | Can they pay? | Score: salary, inflow, CASA balance |
| Payment credibility | Do they pay and keep their word? | Score: promises kept (0–2), money coming in last 3 months (0–2), pre-delinquency history clean (0–1) |
| **Deterioration (this)** | **How did they fall in, and are they stabilized now?** | **DPD bucket history only** |

Design rules agreed with the business owner:

1. **MECE** — every account gets exactly one state; no "other" bucket for behaviour.
2. **Simplicity beats precision** — a rule a collector can repeat beats a better-fitting
   one nobody can explain. Thresholds are round numbers.
3. **Orthogonal where possible** — the states must not rebuild the credibility or ability
   score. Known overlaps are named (§7), not hidden.
4. **5–6 states, at most 8**, each with a different action for the risk team.

---

## 2. Population and data conventions

- **Spine:** credit-card accounts whose **current** bucket is 4, 5, 6 or 7. Bucket 8+ is
  a separate category. The input file for sign-off is the CC 60–180 DPD segment
  (Aug 2026); accounts at bucket 3 in it are outside the spine and filtered out.
- **The string:** one digit per month, **leftmost = current month**
  (`54320002000` → today 5, last month 4, …). The **oldest (rightmost) digit is the first
  billed month**, so it is almost always 0 or 1. Exceptions: rare missing history, 180+
  accounts without history (start at 9, outside the spine), and restructured cards/loans
  re-opened as a new account at their previous bucket.
- **Reliable window: January 2024 onwards.** Older DPD history is unreliable, so every
  string is cropped to the newest months from `RELIABLE_FROM` (2024-01) to
  `SNAPSHOT_MONTH` (2026-08) — **32 months** for the Aug 2026 sample (recomputed from the
  two dates in `config.py`). Effects, all handled:
  - EPD is unaffected: an EPD has at most 3 clean months plus a short straight roll, so its
    string is under 12 digits and never cropped. As a safety net, a cropped string can
    never be EPD (its oldest digit is no longer the first billed month).
  - A spell that started before 2024 makes a cropped string start delinquent. That is
    normal history, not a data issue, so Q0 skips cropped strings; these accounts (0.16%
    of the synthetic spine) are classified normally — in practice mostly stabilized.
  - Seasoned (≥ 12 months) and the 24-month repeat window fit inside 32 months; earlier
    spells that ended before 2024 are invisible, which can slightly under-count repeat
    delinquents whose spell began in early 2024.
  *(Synthetic: 74% of strings cropped; option-B shares essentially unchanged.)*
- **Read it as text.** A numeric column drops digits (Excel keeps 15 significant digits;
  leading zeros vanish). The file reader refuses number-like values.
- **0 ≡ 1.** Bucket 1 (a few days late) is treated as normal.
- **Monthly movement `d` = bucket this month − bucket last month**, which reads as a payment:

  | d | Meaning | Months paid that month (= 1 − d) |
  |---|---|---|
  | +1 | roll — paid nothing (or less than one month's due) | 0 |
  | 0 at bucket ≥ 2 | **hold** — paid one month's due, stays in the same bucket | 1 |
  | −k | paid k + 1 months, moved back k buckets | k + 1 |
  | back to 0/1 | **cure** — common from 2–3, very rare from 4+ | — |

- **Spell:** a continuous run of months at bucket ≥ 2. The *current spell* is the one the
  account is in today.
- **Blip:** an earlier spell of 1–2 months that never passed bucket 2 (`0 0 2 0 0`).
  Blips do not count as earlier spells and do not end the clean history.
- **Data artefacts are cleaned before anything else, and counted:**
  - *Impossible one-month glitches.* A single 0/1 month between two months at 3+
    (`4 0 4`: a cure cannot jump straight back to 4) is read as a hold; a single month at
    3+ between two clean months (`0 3 0`: an account cannot jump from 0 to 3) is read as
    clean. Neither creates an earlier spell.
  - *Billing-cycle +2 jumps.* A true `3 4 5` reported as `3 3 5` or `3 5 5` is repaired.
    The hold *before* the jump is preferred as the artefact (it is already observed); the
    hold after is used only if that does not move a month observed at 4 back below 4; a
    hold at 0/1 is never an artefact. The repair is therefore causal: a state assigned
    today does not change when next month's digit arrives. Any other +2 is read as a roll.

---

## 3. Features used by the states

| Feature | Definition | Fixed once past 4? |
|---|---|---|
| `left_censored` | the oldest month in the string is already at bucket 2+ | yes |
| `months_before_spell` | months of history before the current spell started (blip months included) | yes |
| `n_blips` | earlier 1–2 month excursions that never passed bucket 2 (EPD allows one) | yes |
| `n_prior_episodes` | earlier real (non-blip) spells (EPD requires none) | yes |
| `gap_prior_peak3` | clean months between the end of the most recent earlier spell that reached bucket 3 and the start of this one (repeat delinquent: ≤ 24) | yes |
| `spell_pay_events` | months in the current spell with any payment (hold or move back); EPD requires 0 | **no** — EPD ends when they pay, by design |
| `runup_len` | months from the last clean month to the first month at bucket 4 (3 = straight 2→3→4) | yes |
| `runup_pays` | months on the way to 4 in which 2+ months were paid (moved back) | yes |
| `last6_in_band` | of the last 6 months (incl. today), how many were within today's bucket ±1 | **no** — current behaviour, by design |
| `months_since_4`, `chg_6m` | months since first reaching 4 in this spell; today's bucket minus the bucket 6 months ago (long-run clause) | **no** — current behaviour, by design |

All other features (`runup_holds`, `post4_paid_rate`, `max_hold_run`, …) are diagnostics
only. The current-behaviour inputs are confined to the stabilized question and the EPD
"never paid" condition, so every other state is fixed once the account is past 4.

---

## 4. The states

Questions are asked **in order**; the first "yes" assigns the state.

```
Q0  History starts delinquent?  oldest month already at bucket 2+ (restructured re-open,
                                migrated or missing history)  -> history_starts_delinquent
Q1  Early payment default?  <= 3 months of history before this spell (at most one blip,
                            no earlier real spell) AND never paid since crossing bucket 2
                            (every month of the spell a roll — still falling)
                                                               -> early_payment_default
Q2  Stabilized?             >= 5 of the last 6 months within today's bucket ±1
                            OR (>= 6 months since first reaching 4 AND at most 1 bucket
                                higher than 6 months ago)      -> stabilized
Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and ended
                            <= 24 months before this spell started
                                                               -> repeat_delinquent
Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
      yes -> straight_roller  [B, C: >= 12 months of history before the spell
                               -> straight_roller_seasoned, else straight_roller_early_life]
      no  -> slow_roller      [C: paid 2+ months at once on the way down
                               -> slow_roller_erratic, else slow_roller_intermittent]
```

(Q3 "paying since bucket 4" was tested and rejected — §6.4.) Q0 is a data-quality guard,
not a behaviour state: it stops truncated or restructured histories from being forced
into EPD. It should be rare (E04); restructured accounts are a deferred decision.

### Three options

| Option | States | Use when |
|---|---|---|
| **A — minimal (4)** | EPD, stabilized, straight roller, slow roller | Strict orthogonality: prior-spell history is left entirely to credibility |
| **B — balanced (6), recommended** | EPD, stabilized, repeat delinquent, seasoned straight roller, early-life straight roller, slow roller | Default; the 5–6 target |
| **C — detailed (7)** | B with slow roller split into intermittent payer / erratic payer | The risk team has a different action for each and both are ≥ 4% |

Early-life straight roller stays a state in B and C, but if real data puts it under 5%
(E16) it is merged into straight roller and kept as an early-life flag (agreed).

### What each state means and the action it points to

| State (display name · `code`) | Reads as | Action flavour | Share *(synthetic)* |
|---|---|---|---|
| **Early payment default (EPD)** · `early_payment_default` | At most 3 months of history (one blip allowed), rolled straight in and has **never paid since crossing bucket 2** — still falling, so short-tenure by nature | Early-risk / first-party-fraud review, early legal; no restructuring | 4.3% (bank's broader rule: 6%) |
| **Stabilized** · `stabilized` | Paying about one month's due each month for 5 of 6 months — or, 6+ months after first reaching 4, still within one bucket of where it was 6 months ago (pays what is due on average, unevenly) | **Offer restructuring to break the hardship** | 7.8% (bank's rule alone: 6.9%; bank: 6%) |
| **Repeat delinquent (re-default)** · `repeat_delinquent` | Cured a spell that reached bucket 3 and fell back in within 24 months | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 14.8% |
| **Seasoned straight roller** · `straight_roller_seasoned` | At least a year on book, then rolled straight to bucket 4 with no payment on the way down (some have paid since) | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 53.4% |
| **Early-life straight roller** · `straight_roller_early_life` | 4–11 months on book, then rolled straight to bucket 4 | Same triage; also an underwriting signal for acquisition | 4.7% — under the 5% floor in synthetic data; the real share decides (E16) |
| **Slow roller (partial payer)** · `slow_roller` | Paid something on the way down to bucket 4 but kept rolling | Over-indebted: longer-tenor restructure or settlement | 15.1% |
| ↳ **Intermittent payer** *(C)* · `slow_roller_intermittent` | Paid one month here and there on the way down, never caught up | Chronic insufficiency: restructure to what they actually pay | 9.3% |
| ↳ **Erratic payer** *(C)* · `slow_roller_erratic` | Caught up 2+ months at once on the way down, then rolled again | Lumpy / irregular income: plan aligned to inflow timing | 5.7% |
| **Not classified — history starts delinquent** · `history_starts_delinquent` | Data quality: the string starts already delinquent | Fix the data / treat restructured accounts separately (deferred) | 0% *(synthetic has none)*; expect < 1% |

In option A the two straight-roller states are one: **Straight roller** · `straight_roller`.

**What moves month to month.** Stabilized is current behaviour (*synthetic:* 60% are still
stabilized next month). EPD ends the month the account pays (it then becomes stabilized
or a straight roller). Every other state describes how the account fell in and is fixed
once it is past bucket 4 — it can only move into stabilized (*synthetic:* 99.7%+ keep their
state or move into stabilized next month). Read "straight roller" as *rolled straight to
bucket 4*, not *never paid since*: 32–36% of straight rollers have paid at least one
month since reaching 4 *(review, synthetic)*.

### 4.1 Names

The names use established card-risk and collections terms, and follow two rules:

1. **Describe behaviour, not intent.** These labels reach collector screens, audit trails
   and possibly complaint files. They say what the DPD history shows ("never paid since
   crossing 2", "rolled straight to 4", "paid one month at a time"), never why ("fraud",
   "won't pay"), which the history cannot prove.
2. **Code names are stable; display names are free.** Code uses short identifiers
   (`early_payment_default`, `straight_roller_seasoned`, …). `DISPLAY_NAMES` and `REMARKS`
   in `dpd_states/states.py` carry the business labels, so renaming for the risk team never
   breaks the pipeline or old results. Every report starts with the names table.

| Term | Where it comes from | Note |
|---|---|---|
| **Early payment default (EPD)** | Early-risk monitoring (FPD / SPD / TPD = first / second / third payment default; EPD = default early in the life of the account) | **Formerly "bust-out"** — the bank's internal name, kept in remarks. Classic *bust-out* fraud is different: a customer builds a good record and limit, maxes out (often with cash advances) and disappears. Its DPD history is clean-then-straight-roll, so it lands in **seasoned straight roller**; spotting it needs spend / utilisation spikes before delinquency — a fraud overlay, not this axis |
| **Stabilized** | The bank's own term; roll-rate "stay" behaviour | Industry has no single standard label for "pays enough to stay in the bucket" |
| **Repeat delinquent / re-default** | Collections recidivism; re-default rates after cure or restructure, usually within 12–24 months | |
| **Straight roller** | Core card-collections term: rolls through the buckets without a payment | Here: on the way down to bucket 4 |
| **Seasoned / early-life** | Seasoning and months on book (MOB); the first 12 months is the standard early-life window | |
| **Slow roller (partial payer)** | Roll-rate language: the counterpart of the straight roller | **Also called partial payer** — the more common collections term. The rejected Q3 state was renamed `paying_since_4` so "partial payer" means only this state |
| **Intermittent / erratic payer** | Collections payment-pattern labels | |

---

## 5. Thresholds and the evidence behind them

Parameters marked **[business]** are agreed business definitions. They change only with
the business owner — never to make a share or an expectation check come out right (a
share-matching tune is circular: §6.14). Sweeps are reported in every run to show
sensitivity, not as a menu.

| Threshold (`parameter`) | Value | Why this value | What moving it does *(synthetic)* |
|---|---|---|---|
| EPD history (`epd_max_history`, `epd_max_blips`) [business] | **≤ 3 months, at most one blip** | A customer who never pays misses the first or second bill: 2–3 clean months at most (`0 0 2 3 4`, `0 0 0 2 3 4`, `0 2 0 2 3 4`) | At 6 or 12 months the state fills with early-life defaults (`0 0 0 0 0 0 2 3 4`), which now land in early-life straight roller |
| EPD "never paid" [business] | **no hold or move back in the current spell** | Owner: an EPD never pays after crossing bucket 2, it keeps falling and leaves the spine | `0 0 2 3 4 4 4 4 4 4` (paying monthly) is stabilized, not EPD; `0 0 2 3 4 4 5 6` (paid once) is an early-life straight roller |
| Straight-roller run-up (`straight_max_runup`) | **≤ 3 months** | Any single paid month on the way down makes it a slow roller | ≤ 4 moves ~70% of slow rollers into straight roller. 41% of slow rollers rest on one hold — E23 / E28 test whether that month is real |
| Stabilized band (`stabilized_min_in_band`) [business] | **5 of last 6 months within ±1** | The bank's existing stabilized rule, unchanged | 4 of 6: share ~14%, next-month roll ~46%. 6 of 6: ~5%, ~32% |
| Stabilized long-run clause (`stabilized_long_run_months`, `_max_rise`) [business] | **≥ 6 months since first reaching 4, at most +1 bucket over 6 months** | Fixes oscillating payers and accounts that just paid down (§6.15). Straight rollers cannot meet it (they leave the spine within ~4 months) | Adds ~1% of the spine to stabilized. +2 would take in slow drifters paying ~4 of 6 dues; `None` switches it off |
| Repeat-delinquent depth (`repeat_min_prior_peak`) [business] | **earlier spell reached 3** | Cures from 4+ are rare; spells reaching 3 give 83% one-spell vs the bank's ~85% | From 2: more; from 4: ~5% |
| Repeat-delinquent window (`repeat_window_months`) [business] | **ended ≤ 24 months before this spell** | Owner decision; the common re-default window. Measured to the start of this spell, so the state stays fixed | Lowers the overlap with credibility's lifetime clean point (eta² 0.81 → 0.72) |
| Seasoned (`seasoned_min_months`) [business] | **≥ 12 months** | The first year on book is the standard early-life window; EPD already takes ≤ 3 months, so early life = 4–11 months | Early life 4.7% at 12 m; it depends on the book's tenure mix, so the real share decides (E16) |

**Rule order.** Q0 and EPD come before stabilized; since an EPD has never paid in its
spell, an account cannot be both, so the order no longer matters for them.

---

## 6. What was tried and dropped — and why

### 6.1 Unsupervised clustering as the source of states (k-means, GMM)

- **Whole spine, k-means:** very stable (bootstrap ARI 0.99) but only ARI 0.3–0.4 against
  the planted patterns and 0.1–0.3 against the rule states. It always merged holders with
  staircases and never isolated slow slides. **Stability does not mean validity** — on real
  data stability is the only check available, and it cannot detect merged behaviours.
- **GMM:** BIC never reached a minimum (kept improving to 12 components) because the
  features are spiky — 56–93% of accounts sit on a single value (run-up = 3, no earlier
  spell, …), and GMM fits narrow components to the spikes. Under 1% of accounts were
  ambiguous, so the soft-assignment advantage disappears. Not used. GMM fits continuous
  inputs (ability scores, balances) far better than DPD-derived counts.
- **Residual clustering (after EPD and stabilized) — a diagnostic only.** k-means at k = 6
  on the rest found six nameable groups (long-clean straight roll, short-clean straight
  roll, earlier spell to 3+, paying after 4 but still rolling, held on the way, paid 2+ on
  the way), and every B/C split maps to one of them with a one-line rule. Its agreement
  score (ARI) is **not** evidence for B over A: the independent review showed that any
  finer partition built on the clustered features gains ARI — a meaningless split at
  median tenure gained 0.16. E22 is therefore INFO only.

### 6.2 A "mixed" / residual state
Dropped. An ordered tree with a default branch is MECE without one, and a residual
bucket invites "everything we don't understand" to grow. (Q0 is a data-quality guard, not
a behaviour bucket.)

### 6.3 Staircase (holds for months at each level, then steps up)
Merged. While it is holding a bucket it *is* stabilized (that is the actionable fact);
just after a step it reads as a slow roller. Telling a genuine holder from a staircase
mid-hold needs more than 6 months of history and an extra rule, and the next-month risk
was the same (*synthetic:* 0.28 vs 0.29).

### 6.4 "Paying since bucket 4" — pays after reaching 4 but still rolling (Q3)
Tested at 0.34 / 0.5 / 0.67 months paid per month since 4. Rejected:
- barely separates risk (next-month roll ~80% vs ~86%);
- unstable — ~37% leave it every month — and it drags the stability of the fixed states
  down by ~7pp, because accounts flip in and out of it;
- 79% of it is "paid in the last 3 months" — the credibility axis's 2-point component.

It is one of the natural residual clusters, so it is real behaviour — but it belongs to
credibility. The switch is kept (`paying_since_4_min_rate`) so the test can be repeated (E24).

### 6.5 Separate states for slow slide, dip-and-roll, volatile
Merged into slow roller (A, B) or split once by "paid 2+ months on the way" (C). The three
confuse each other in every view, and the risk actions are close. Much of "volatile"
(cure then relapse) is a repeat delinquent by definition.

### 6.6 Repeat delinquent in option A
Left out of A on purpose. Repeat delinquent is built from earlier spells — the history
credibility's 1-point "pre-delinquency clean" flag scores. In the self-test the states
explain **72%** of that point's variance (81% before the 24-month window). It is in B/C
because it is only 1 of credibility's 5 points and *cured from bucket 3 recently* is
evidence of catch-up capacity. E19b measures the real overlap and decides A vs B.

### 6.7 "Stabilized or improving" clause (today's bucket ≤ 6 months ago)
Dropped. It changed **0.0%** of assignments; the long-run clause (§6.15) covers the real cases.

### 6.8 Payment-based refinement of stabilized
Tested: "≤ 1 roll in 6 months AND paid 2+ months at least once" separated holders from
staircases at 99% precision — but only because the synthetic generator built it that way,
and it leans on payment behaviour (credibility). Replaced by the bank's own 5-of-6 rule.

### 6.9 Features that drift with time since bucket 4
Dropped from assignment: whole-spell roll rate, fixed-window counts, months paid since 4
as a count. Replaced by run-up features (fixed once past 4). The remaining
current-behaviour inputs (§3) are deliberate and confined to stabilized and EPD.

### 6.10 Shape table as the assignment
Kept for discovery and stakeholder examples only. ~5–6k distinct banded shapes; the top
30 cover ~35–40% of accounts — too fragmented to assign everyone.

### 6.11 n-gram ranking by planted-label purity
Fixed. Lift is measured against each account's own codes in shuffled order: lift > 1
means the order of moves matters. No planted labels are needed.

### 6.12 Treating +2 jumps as impossible — and the first repair
Replaced by repair. The first version of the repair looked ahead (it used next month's
digit) and also treated clean months as holds, so a "fixed" straight roller could become a
slow roller when the next month arrived (`…0224` → `…02244`), and `000034` borrowed a clean
month and became EPD. The repair is now causal and only uses holds at bucket 2+ (§2).

### 6.13 Payment-promise or inflow inputs in any state
Never used — credibility and ability own them. Their overlap is *measured* (§7).

### 6.14 EPD ("bust-out") with up to 6 months of history
The first version allowed ≤ 6 months, chosen to match "a few months". It made
`0 0 0 0 0 0 2 3 4` an EPD — but six clean months means about four bills were paid: an
**early-life default**. Its synthetic 6% match was circular: the generator's bust-out
volume had been tuned to hit 6% under that rule. Replaced by the agreed definition
(≤ 3 months, one blip) and, after review, the owner's "never paid since crossing 2".

### 6.15 Stabilized measured only around today's bucket (edge cases)
The bank's rule — 5 of the last 6 months within ±1 of **today's** bucket — misreads two
uncommon but real histories (oldest → newest, today is the last digit):

- **Oscillating payer** `0000 0000 2344 4334 5433 4565 54` — swings between 3 and 6 for over
  a year, paying roughly what is due on average. The rule flipped it between stabilized and
  "straight roller" **5 times in 16 months**.
- **Just paid down** `… 3 4 5 6 6 5 4` — paid two months twice (6 → 5 → 4). The band around
  today's 4 excludes the two 6s, so the rule called it a straight roller *because* it paid.

Fix adopted: the **long-run clause** (§5). Both cases are now stabilized from their sixth
month after first reaching 4; the only remaining dip is the single month at the top of a
3-month roll (3 → 4 → 5 → 6). Rejected alternatives: allowing +2 over 6 months (takes in
slow drifters), and a "sticky" rule that remembers last month's state (harder to audit).
Measured *(synthetic, with oscillating payers at 1.2% of the spine)*: of accounts ever
stabilized over 6 months, the share that **left and came back** is ~5% with the clause vs
~5.5–8% on the bank's rule alone. E26 tracks this on real data; both examples are
permanent regression cases.

### 6.16 Seasoned / early-life split in option A
Not in A: in synthetic data it adds no risk separation (by construction). It is in B/C for
its action difference (life event vs underwriting signal), with the merge rule in §4.

### 6.17 EPD that has started paying
Before the review, an account that entered like an EPD but then paid its monthly due for
6–10 months (`0 0 2 3 4 4 4 4 4 4`) stayed EPD, with the action "early legal; no
restructuring". The owner's rule — an EPD never pays after crossing bucket 2 — now sends it
to stabilized.

---

## 7. Overlap with the other axes (known and measured)

| Overlap | Size *(synthetic)* | Treatment |
|---|---|---|
| stabilized ↔ credibility "money coming in" (2 pts) | 98% of stabilized have money in; ~44% of the rest do too | One-directional: stabilized is stricter (enough to hold the bucket, 6 months). Accept and state it. E21 |
| slow roller ↔ credibility "money coming in" | near bucket 4 almost all slow rollers paid in the last 3 months (they paid on the way down); by bucket 7 far fewer | A clock effect of the run-up, not a separate signal. Reported by state × bucket in every run |
| stabilized ↔ credibility "promises kept" (2 pts) | likely (paying monthly) — not testable without the score | E19 measures the total |
| repeat delinquent ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.72 of the clean point explained by B states | Decides A vs B. E19b |
| straight / slow roller ↔ ability | none in synthetic (by construction) | Straight rolling may proxy income loss on real data — fine, but say so. E20 |
| any state ↔ locatability | none expected | E20b |

---

## 8. Real-data validation

### Two ways to run
- **File mode — for sign-off, no Spark.** `python docs/deterioration_states/run.py validate`
  reads `INPUT_FILE` (`data/input/dpd_synthetic_data.xlsx`, column `dpd_history_str`,
  CC 60–180 DPD, Aug 2026). A snapshot of today's segment has **no outcomes**: accounts that
  rolled to 8+ since are not in it, so roll rates and exits are SKIPPED. What it can show:
  shares, data quality, shapes, overlaps (if axis columns are in the file), and stability
  among the survivors (E13, E14, E26 run on accounts in the spine last month and today).
- **Spark mode — production.** `snippets/dpd_states_validate.py`, `main(catalog)`.

### How the backtest works from a single table (Spark mode)
Today's string holds the past: dropping its newest *k* digits gives the string as it was
*k* months ago, and the dropped digits are what happened next. Assumptions, each checked:
1. The table **keeps accounts that have since rolled to 8+ or closed** (a survivor-only
   table biases outcomes — the snippet warns when no backtest account is at 8+ today).
2. **Every string ends in the same (latest) month.** Strings frozen at charge-off or
   closure are not "today" — set `COL_STRING_AS_OF` to exclude them. Even 20% frozen exits
   bias bucket-4 roll by ~5pp while E03 still passes *(review)*.
3. **Exit codes are digits** — a write-off letter must be mapped in `CHAR_MAP`, or those
   accounts silently drop out (E02 now covers the backtest and the whole table).
4. The bank's roll rates (E03) are compared like for like (count- vs balance-weighted).

Outcome comparisons are **standardised to the bucket mix** (stabilized sits mostly at
bucket 4) and use exit within **3 months**, because 6-month exit saturates near 100% at
buckets 5–7.

### Expectations (checked automatically — `dpd_states/expectations.py`)

Anchor: **bank** = the bank's figures or rules · **design** = follows from the rules ·
**synthetic** = calibrated on the generator only (a WARN is a prompt to look) · **data**.

| | Check | Expected | Anchor |
|---|---|---|---|
| E01 | Exactly one known state per account | True (FAIL) | design |
| E02 | Unparseable strings (spine, backtest, whole table) | ≤ 2% (FAIL) | data |
| E03 | Backtest monthly roll rates vs 70/80/90/95% | ≤ 7pp (FAIL) | bank |
| E04 | Histories that start delinquent | ≤ 1% | bank |
| E05 | Unrepaired +2 jumps | ≤ 2% | synthetic |
| E06 | Bucket mix declines 4 → 7 | yes | bank |
| E07 | INFO: one-spell share, four definitions vs ~85% | report | bank |
| E08 / E09 | EPD / stabilized share | 3–8% / 4–10% | bank |
| E10 / E11 | Recall of the bank's existing flags | ≥ 80% / ≥ 90% | bank |
| E12 | Stabilized next-month roll below the rest (bucket-standardised) | ≥ 20pp | synthetic |
| E13 | Fixed states keep their state (or move into stabilized) | ≥ 95% | design |
| E14 | Stabilized persistence next month | 45–85% | synthetic |
| E15 | Option A straight-roller share | 55–80% | bank |
| E16 | Smallest optional option-B state (EPD and stabilized are required at any size; empty = 0) | ≥ 5% | design |
| E17 | Smaller slow-roller split (C) | ≥ 4% | design |
| E18 | Stabilized at bucket 4 vs 7 | ≥ 2× | bank |
| E19 / E19b / E20 / E20b | eta² of credibility / clean point / ability / locatability by state | ≤ 0.25 / 0.50 / 0.10 / 0.05 | design |
| E21 | Stabilized with money coming in | ≥ 90% | design |
| E22 | INFO: residual-cluster ARI gain (diagnostic only) | report | synthetic |
| E23 | INFO: straight vs one-hold slow roller, next-month roll | report | — |
| E24 | "Paying since 4" stays rejected | persistence ≤ 75% | synthetic |
| E25 | INFO: exit-within-3m spread across fixed states (bucket-std) | report | — |
| E26 | Stabilized accounts that leave and come back | ≤ 10% | synthetic |
| E27 | Uncropped string lengths vary (not padded / fixed-length) | p95 − p05 ≥ 6 | data |
| E28 | Run-up holds: largest calendar month vs its neighbours | ≤ 2.5× | data |

Every check carries an "if not met" action in the code and in the report; none of them
says "tune a business parameter until it passes". The self-test also runs **24 edge
cases** from the design discussion and the review, and fails if any changes state.

### Choosing the option on real data
1. Any **FAIL** → fix config/data first; read nothing else.
2. **E19b high** (repeat delinquent ≈ credibility clean point) **and** the risk team does
   not want the cured-recently nuance → **A**. Otherwise **B**.
3. **E17 passes and** the risk team has distinct actions for intermittent vs erratic payers → **C**.
4. **E16 fails on early-life straight roller** → merge it into straight roller (agreed).
5. **E25 ≥ 5pp** → how they fell in carries risk on its own; report it to the risk team.

---

## 9. Validation done so far *(synthetic)*

- **Calibrated generator** (`dpd_states/synth.py`): eight planted journey patterns
  (bust-out, clean abrupt shock, slow slide, staircase, stabilized, repeat episodes,
  dip-and-roll, volatile) plus a rare oscillating payer; full lifecycles to exit;
  length-biased snapshot like a real spine; payment holidays and billing-cycle +2 jumps;
  one continuous tenure distribution. Matches the bank's roll rates (71/78/89/94% vs
  70/80/90/95%), single spell 83% from bucket 3 (85%) and stabilized 6.9% under the
  bank's rule (6%).
- **Known calibration gap:** "never paid since reaching 4" is 59% in the generator vs the
  owner's first estimate of ~90% (which the owner later called overkill). The generator's
  holders are therefore probably over-represented; this affects synthetic shares of
  stabilized and slow roller, not the rules.
- **Method report:** `validation/dpd_states_validation_*.md` (`run.py synthetic`).
- **Real-data path self-test:** `validation/selftest_report_*.md` (`run.py selftest`) runs the
  exact analysis and expectations the workplace run uses, with fake axis columns, plus the
  24 edge cases. All checks pass except two expected WARNs: E16 (early-life straight roller
  4.7%) and E19b (repeat delinquent ≈ clean point).
- **Independent review:** 24 findings, none critical — see [REVIEW.md](REVIEW.md).

**What synthetic data cannot tell you:** whether the rolling states differ in outcome
(they share post-4 dynamics by construction), how big the real overlaps with credibility
and ability are, and how much payment holidays contaminate stabilized.

---

## 10. Open decisions

1. Option A, B or C — decide from E19b, E17 and the risk team's actions (§8).
2. The bank's exact spell definition — E07 reports four; it matters for the 85% check
   and for the repeat-delinquent depth.
3. EPD vs the bank's existing bust-out rule — ours is stricter ("never paid since
   crossing 2"); E10 shows the agreement.
4. Restructured accounts re-opened at their old bucket (Q0) — deferred by the owner.
5. Payment holidays / restructurings — account-level flags only show how often stabilized
   accounts carry them (E21, section 4 of the report); month-level exclusion needs
   month-level flags.
6. The long-run clause widens the bank's stabilized definition (~+1% of the spine) —
   confirm with the owners of the existing rule (E11).

## Glossary

Bucket — DPD band, one digit per month · Roll — +1 bucket, nothing paid · Hold — same
bucket, one month's due paid · Cure — back to 0/1 · Spell — continuous months at ≥ 2 ·
Blip — 1–2 month spell never past 2 · Run-up — last clean month to first month at 4 ·
Spine — accounts currently at 4–7 · eta² — share of an axis score's variance explained by
the states (0 = orthogonal) · ARI — agreement between two groupings (0 = chance, 1 = identical).
`````

### FILE: `REVIEW.md`
sha256 `dfc00a2572ce7c2cdb687d82e81b79e136842a4142782ff5b351e32554ddc579` · 48 lines · trailing newline: yes

`````markdown
# Independent review — findings and what was done

An independent reviewer (fresh context, no part in the design) reviewed the methodology and
code on 2026-10-16: read every file, probed the rules with crafted DPD strings, ran the
real-data path on Python 3.10 / pandas 1.5.3 as well as 3.13 / pandas 3.0, and reviewed the
Spark snippet by reading. **24 findings, none critical; 9 high or medium-high.** The
rules were confirmed MECE and the original edge cases passed. Business decisions were
taken by the owner (marked **owner**); everything else was fixed in code and documents.

Case strings are written oldest → newest (last digit = today's bucket).

| # | Sev. | Finding | Disposition |
|---|---|---|---|
| F01 | High | EPD depends on where the string starts; padded / fixed-length strings, numeric columns (lost digits), re-keyed cards and a `{"X": "9"}` example could all fake or hide EPD; E08's action invited circular tuning | **owner:** the oldest digit is the first billed month (0/1). Fixed: file reader refuses number-like values; Spark warns on non-string type; E27 flags fixed-length strings; `STRIP_CHARS` strips only the ends; `CHAR_MAP` example corrected; E08 action → compare and escalate |
| F02 | High | Strings that start inside the spell (`4567`, `444444`) became EPD; E04 (≤ 10%) too loose | **owner:** such histories are restructured re-opens or missing data. New Q0 data-quality state `history_starts_delinquent`; E04 tightened to ≤ 1%. Restructured accounts deferred |
| F03 | High | One-table backtest assumes all strings end in the same month; frozen / purged exits and letter exit codes bias it silently, with misleading diagnostics | Fixed: `COL_STRING_AS_OF` excludes stale strings; E02 covers backtest and whole table; E03 action lists frozen strings, letter codes, count vs balance; assumptions in METHODOLOGY §8. A T−k snapshot join remains an option if strings freeze |
| F04 | Med-high | +2 repair looked ahead and treated clean months as holds: `…0224` straight → `…02244` slow; `000034` became EPD | Fixed: causal repair (hold before the jump first), only holds at 2+, never moves a 4 below 4. Both cases are regression tests; E13 now 99.7% |
| F05 | Medium | Long-run clause documented as "6 months in 4+" but code counts months since first reaching 4; features used by rules missing from §3 and P6 | Fixed wording everywhere; §3 lists every input incl. `months_since_4`, `chg_6m`, `spell_pay_events`, `gap_prior_peak3`; P6 audit list updated |
| F06 | Medium | E16 passed when a state was empty | Fixed: shares reindexed to the option's full state list (empty = 0); E16 scoped to optional states |
| F07 | Medium | Crashes: a length-1 string (in `shape`), empty spine, < 8 residual rows, `"0000"`; an account at 0 silently labelled | Fixed: guards in `shape`, `build_features`, `run`, clustering; `journey_features` raises a clear error below bucket 2; P6 applies cleaning + spine filter first |
| F08 | Medium | Y/N flag columns silently became all-false | Fixed: `parse_flag` reads 1/0, Y/N, Yes/No, True/False; reports and skips when unparseable |
| F09 | Medium | E22 (residual-cluster ARI gain) cannot discriminate — a meaningless split passes | Demoted to INFO; METHODOLOGY no longer cites it as evidence for B |
| F10 | Medium | E25 already fired on synthetic (claim "cannot show" was false); 6-month exit saturates; E12 bucket-confounded | Fixed: bucket-standardised next-month roll and exit within 3 months; documentation corrected |
| F11 | Medium | Labels overclaim ("never paid"); an EPD paying monthly for 6–10 months stayed EPD → "early legal" | **owner:** an EPD never pays after crossing bucket 2 (new condition). Remarks now say "rolled straight to bucket 4 … some have paid since" |
| F12 | Medium | Slow roller overlaps credibility "money in" near bucket 4 (clock effect), undisclosed | Disclosed in §7; money-in by state × bucket reported every run |
| F13 | Medium | Straight vs slow rests on a single month for 41% of slow rollers; holds may be artefacts | Added E23 (outcome of one-hold slow rollers vs straight rollers) and E28 (calendar-month spike test of run-up holds). Business call deferred until real data |
| F14 | Medium | E07 spell definition ambiguous ("run at ≥4" also ≈ 85%) | E07 now INFO reporting four definitions; bank's exact definition is an open decision |
| F15 | Medium | Results contained raw 30-month DPD strings, against the stated governance | Fixed: only banded shapes shared by ≥ 10 accounts in results; check-only prints aggregates (newest/oldest digit counts, shapes) |
| F16 | Medium | Re-running in the same kernel used stale config | Fixed: snippet reloads the package each call and prints a config fingerprint |
| F17 | Medium | Expectation actions invited tuning agreed business definitions to hit shares | Fixed: `[business]` markers in `states.py`; all such actions say escalate; PROMPTS P3 forbids it |
| F18 | Low-med | Checks differed when re-run from the saved JSON (int vs str bucket keys) | Fixed: results are JSON-safe (str keys, no NaN) before checks run |
| F19 | Low-med | E02 blind to backtest / table; `STRIP_CHARS` removed mid-string characters | Fixed (see F01, F03) |
| F20 | Low-med | Repeat delinquent had no recency window; a one-month glitch created it | **owner:** earlier spell must end within 24 months of this one. Fixed: impossible one-month glitches (`4 0 4`, `0 3 0`) cleaned and counted; both are regression tests |
| F21 | Low | Ranges anchored on synthetic data not labelled; "never paid since 4" gap (59% vs ~90%) undiscussed | Every check now has an anchor (bank / design / synthetic / data); gap discussed in §9 |
| F22 | Low | `model_id` resolved before the config guard; E01 could never fail; hard-coded spine; NaN in JSON; Spark re-scans | Fixed all: guard first; E01 also checks unknown states; spine from config; JSON-safe; `cache()` |
| F23 | Low | Document inconsistencies (E01–E25 vs E26, stale names, quoted shares, "first three payments" vs "first or second bill") | Fixed in README, METHODOLOGY, PROMPTS, config |
| F24 | Low | Early-life straight roller acts for underwriting, small in synthetic; seasoned straight roller is in practice the residual | **owner:** keep early-life as a state; merge into straight roller if real share < 5% (E16). Seasoned straight roller's action is "read the other axes" by design |

## Verified independently before acting
F02 (`4567`, `444444` → EPD), F04 (`…0224` vs `…02244`; `000034` → EPD) and F11
(`00234444444444` → EPD) were reproduced before any change; all are now regression cases
in `dpd_states/selftest.py`.

## Still open
- The bank's exact spell definition (F14) and existing bust-out rule (F01 / E10).
- Restructured accounts re-opened at their old bucket (F02) — deferred by the owner.
- Whether a single paid month should separate slow from straight rollers (F13) — decide
  from E23 / E28 on real outcomes.
`````

### FILE: `PROMPTS.md`
sha256 `118f3e4c33e022a1a2b78182dc362c5a5d11f1e7d43c0113eda4a6c077389dc6` · 219 lines · trailing newline: yes

`````markdown
# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace repository. Each prompt is
self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 (file mode) → P2**, then P3 / P4 as the results require, then P5.
**P6 (Spark) and P7 (production)** only after the methodology and states are signed off.

---

## P0 — Orientation (paste first, every session)

```
You are working in our workplace repository on the "deterioration states" package in
docs/deterioration_states/. Read these first, fully, before doing anything:
  1. docs/deterioration_states/README.md
  2. docs/deterioration_states/METHODOLOGY.md
  3. docs/deterioration_states/REVIEW.md
  4. docs/deterioration_states/dpd_states/config.py
  5. docs/deterioration_states/dpd_states/states.py

What it is: one state per credit-card account in DPD buckets 4–7, assigned from the DPD
bucket-history string (leftmost digit = current month, rightmost = first billed month) by
a short decision tree (options A/B/C). The state logic and thresholds were designed,
validated and independently reviewed elsewhere.

Ground rules — follow all of them:
- Do NOT change the state logic, thresholds or expectations in dpd_states/states.py or
  dpd_states/expectations.py unless a prompt explicitly asks you to. Parameters marked
  [business] in states.py are agreed business definitions: never change them to make a
  share or a check come out right — report and escalate to me instead.
- NEVER invent a dataset, table or column name. Find it in the repo (Kedro catalog
  conf/**/catalog*.yml, pipeline code, notebooks, data/) or ask me. Leave <<FILL-IN>>
  where you cannot confirm a name.
- Run every tool from the repo root as `python docs/deterioration_states/run.py <tool>`
  (validate | selftest | synthetic | bundle). `python -m dpd_states...` only works from
  inside docs/deterioration_states/.
- Results files contain aggregates only — no account keys, CIFs, names, raw DPD strings
  or other row-level data. Do not paste raw DPD strings into this chat.
- Never present a number you have not seen in actual output. If something has not run,
  say it has not run.
- Keep code changes minimal and confined to dpd_states/config.py and the clearly marked
  <<FILL-IN>> spots unless asked otherwise.

Reply with a 5-line summary of what the package does and which names need filling in.
```

---

## P1 — File mode: check the input and do the first run

```
Task: run the package on our DPD-history file, without Spark.

1. The input is data/input/dpd_synthetic_data.xlsx (CC 60–180 DPD segment, Aug 2026),
   DPD string column "dpd_history_str". These are already the defaults in
   dpd_states/config.py (INPUT_FILE, COL_DPD). The file has other derived columns — ignore
   them unless they are one of the optional columns below.
2. Before running, check with a few lines of pandas (print aggregates only, no raw strings):
   - the column reads as TEXT (dtype object/string) when loaded with dtype={"dpd_history_str": str};
     if Excel stored it as a number, digits are lost — stop and tell me;
   - the share of strings whose LEFTMOST digit is 4–7 (today's spine) and the
     distribution of the RIGHTMOST digit (should be mostly 0/1 = first billed month);
   - min / median / max string length (strings are cropped to the reliable window,
     RELIABLE_FROM = 2024-01 to SNAPSHOT_MONTH = 2026-08 = 32 months, inside the package —
     do not crop them yourself; if the snapshot month differs, update SNAPSHOT_MONTH);
   - any characters other than 0–9 (if so, list them with counts; do not guess a mapping).
3. Optional columns: if the file (or another file I point you to) has any of the persona
   scores (credibility total and its three components, ability score, reachability /
   in-country flags), the bank's existing bust-out / stabilized flags, or payment-holiday /
   restructured flags, map them in AXIS_COLS / EXISTING_RULE_COLS / FLAG_COLS in config.py.
   Show me the diff. Do not build joins without asking.
4. Install openpyxl if pandas cannot read .xlsx, then run from the repo root:
       python docs/deterioration_states/run.py selftest     (must end "SELFTEST PASSED")
       python docs/deterioration_states/run.py validate
5. Paste me the block between === DPD_STATES OUTPUT START === and END.
```

---

## P2 — Interpret the run

```
Task: interpret the latest results/dpd_states_file_<file>_<date>.json and .md (file mode)
or results/dpd_states_validation_<model_id>_<date>.json (Spark mode).

Report, in this order:
a. Any FAIL (E01, E02, E03). If present, STOP: diagnose and propose the config fix.
b. In FILE mode, outcome checks (E03, E10–E12, E23–E25) are SKIPPED because a snapshot of
   today's segment has no accounts that left it — say so once; that is expected. E13, E14
   and E26 run on survivors.
c. Each WARN: observed value, expected range, the check's anchor (bank / design /
   synthetic / data) and its "if_not_met" action. Say whether the action needs a config
   change, a decision from me, or nothing. A WARN on a "synthetic" anchor is a prompt to
   look, not proof of a problem.
d. The option-B state shares, and how they compare with the bank's figures (EPD ~6% under
   the bank's broader bust-out rule; stabilized ~6%).
e. E07: which of the four spell definitions comes closest to the bank's ~85%.
f. E04 (histories that start delinquent) and E27 / E28 (padding, calendar artefacts).
g. Which option the data supports, using METHODOLOGY.md §8 "Choosing the option".
Every number you quote must come from the output. Mark anything you infer as an inference.
```

---

## P3 — Fix-up loop for WARNs (bounded)

```
Task: address the WARN checks from the last run, within strict limits.

Allowed without asking me: config.py changes (names, CHAR_MAP, STRIP_CHARS, filters,
optional columns, COL_STRING_AS_OF).

Allowed only after I approve, one at a time: the technical parameter
straight_max_runup, and merging early-life straight roller into straight roller if E16
shows it under 5% (set seasoned_min_months=None in the option — this was pre-agreed).

Never: changing [business] parameters (epd_max_history, epd_max_blips,
stabilized_min_in_band, stabilized_long_run_*, repeat_min_prior_peak,
repeat_window_months, seasoned_min_months) to hit a share; changing the tree; adding or
removing states; editing expectations to make a check pass; using payment-promise /
inflow / ability columns inside states.py. For those, write me the evidence (the sweep
rows in section 6 of the report) and I decide.

After approved changes, re-run and compare old vs new check tables.
```

---

## P4 — Compare with the bank's existing bust-out and stabilized rules

```
Task: compare this package's early_payment_default (the bank calls it bust-out) and
stabilized with the bank's existing implementations.

1. Find the existing bust-out and stabilized logic in this repo (search for "bust",
   "stabil", "dpd", pipeline nodes, SQL). List the files and quote the rules.
2. Translate each into the terms of METHODOLOGY.md §4 (history before the spell, blips,
   earlier spells, "never paid since crossing bucket 2", months within ±1 of today's
   bucket out of the last 6, the long-run clause).
3. List every difference and its likely effect on the shares (E08/E09) and recall
   (E10/E11). If the existing flags are available as columns, wire them into
   EXISTING_RULE_COLS in config.py so the next run measures agreement directly
   (1/0, Y/N and True/False are all read correctly).
4. Do not change states.py. Report the differences to me for a decision.
```

---

## P5 — One-page summary for the risk team

```
Task: write a one-page summary for the Group Retail Risk team from the latest results
file (and its .md).

Audience: risk managers, not data scientists. No code, no eta², no ARI.
Structure:
1. What the states are (one line each, display names) and the action each points to —
   use the table in METHODOLOGY.md §4 and §4.1 (EPD was formerly called bust-out; slow
   roller is also called partial payer), with the REAL shares from the results.
2. What the run shows — real numbers only. In file mode: shares, stability, data quality;
   say that outcomes need the Spark backtest.
3. How this fits with locatability, ability and credibility: where it adds information
   and where it overlaps (stabilized ↔ money coming in; repeat delinquent ↔ clean history).
4. The option we recommend (A/B/C) and why, in two sentences.
5. Open decisions for the risk team (METHODOLOGY.md §10), as questions.
Write it to docs/deterioration_states/results/risk_summary_<date>.md.
```

---

## P6 — Spark validation with outcomes (after file-mode sign-off)

```
Task: run the Spark validation, which adds the outcome backtest.

1. Find the dataset with one DPD-history string per credit-card account at the latest
   month. For outcomes it must still contain accounts that have since rolled to 8+ or
   closed, and every string must end in the same month (if strings freeze at charge-off,
   find the column with the string's as-of date for COL_STRING_AS_OF). If several
   candidates exist, list them with their columns and ask me.
2. Fill in DS_STRINGS_TMPL, KEY, COL_SNAPSHOT / ROW_FILTER / COL_STRING_AS_OF as needed in
   config.py, and the globals_dev accessor in snippets/dpd_states_validate.py
   (_resolve_model_id). The string column must be a string type.
3. Give me the notebook cell from the snippet docstring for main(catalog, check_only=True).
   When I paste the CHECK block back, verify: counts plausible, rows == accounts, newest
   digit 4–7 / oldest digit mostly 0/1, no WARNING lines. Then the full run:
   result = main(catalog). Config edits take effect without a kernel restart (the config
   fingerprint is printed).
4. Interpret with P2 (now E03 and the outcome checks run).
```

---

## P7 — Productionise the chosen option (only after sign-off)

```
Task: add the deterioration state as a pipeline output, using the option I name:
<A_minimal_4 | B_balanced_6 | C_detailed_7>.

1. Follow this repo's existing pipeline patterns (find a comparable node and copy its
   structure, naming, catalog entries and tests). Do not invent conventions.
2. The node takes the DPD strings and, in this order: cleans them with
   dpd_states.analysis.clean_strings, keeps today's spine (current bucket 4–7), then calls
   dpd_states.features.build_features and dpd_states.states.assign_states — do not
   re-implement the logic. Apply per partition (mapInPandas / applyInPandas).
3. Output: account key, snapshot date, state code, display name
   (dpd_states.states.DISPLAY_NAMES), option name, and the assignment features for
   auditability: left_censored, months_before_spell, n_blips, n_prior_episodes,
   gap_prior_peak3, spell_pay_events, runup_len, runup_pays, last6_in_band,
   months_since_4, chg_6m, n_glitches, n_jumps_repaired.
4. model_id from globals, never hardcoded; new catalog entries model_id-namespaced like
   the existing ones.
5. Ship a validation snippet to the same contract as snippets/dpd_states_validate.py:
   row counts, null rates, share per state, MECE check (exactly one state per account),
   agreement with the last validation run's shares (within 1pp), and banded journey
   shapes (no raw strings, no keys).
6. Show me the diff and the catalog entries before anything runs.
```
`````

### FILE: `dpd_states/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `dpd_states/config.py`
sha256 `d0dc44974896f1cda6baec3b3d944b8e5a432831370486d7468966b62d5e79ac` · 93 lines · trailing newline: yes

`````python
"""Workplace configuration — the ONLY file that needs editing to run on real data.

Every <<FILL-IN>> must be replaced with a name discovered in the workplace repo / Kedro
catalog. Never guess a dataset or column name: if it cannot be found, ask the user.
`model_id` is NOT configured here — the Spark snippet resolves it from the caller or globals.

Two ways to run:
  * FILE mode (methodology sign-off, no Spark):  python docs/deterioration_states/run.py validate
    reads INPUT_FILE / COL_DPD below.
  * SPARK mode (PROD, later):  snippets/dpd_states_validate.py  main(catalog)
    reads DS_STRINGS_TMPL / KEY / COL_DPD.
"""

# --- file mode -------------------------------------------------------------------------
# Path relative to the repo root (or absolute). One row per account, today's snapshot.
INPUT_FILE = "data/input/dpd_synthetic_data.xlsx"   # CC 60–180 DPD segment, Aug 2026

# --- the DPD string (both modes) --------------------------------------------------------
# Must be read as TEXT: a numeric column drops digits (Excel keeps only 15 significant
# digits; leading zeros vanish). The first billed month is the OLDEST (rightmost) digit.
COL_DPD = "dpd_history_str"

# --- Spark mode dataset ----------------------------------------------------------------
# One row per credit-card account with its DPD bucket-history string AS OF THE LATEST
# MONTH. For the backtest it must contain ALL card accounts that were in buckets 4–7
# `BACKTEST_MONTHS` ago — including those that have since rolled to 8+ or closed — and
# every string must end in the same (latest) month. If only today's spine is available,
# set DS_STRINGS_HAS_EXITED = False: outcome checks are skipped, stability checks run on
# the survivors.
DS_STRINGS_TMPL = "{model_id}.<<FILL-IN: dataset with one DPD-history string per card account>>"
DS_STRINGS_HAS_EXITED = True
KEY = "<<FILL-IN: account key column>>"          # used only for counting distinct accounts

# Several snapshots per account? Name the snapshot column; the latest snapshot is used.
COL_SNAPSHOT = None
# Date the string was last updated, if it can lag the snapshot (strings frozen at
# charge-off / closure). Rows whose string is older than the latest are excluded from the
# backtest, because their newest digit is not "today". None = all strings are current.
COL_STRING_AS_OF = None
# Optional Spark SQL filter applied first (scope), e.g. "product_type = 'CREDIT_CARD'".
ROW_FILTER = None

# --- reliable history window --------------------------------------------------------------
# DPD history is only reliable from RELIABLE_FROM onwards. Every string is cropped to the
# months from RELIABLE_FROM to SNAPSHOT_MONTH (the month of the leftmost digit), inclusive;
# older (rightmost) digits are dropped. A cropped string's oldest digit is NOT the first
# billed month, so a cropped account can never be EPD, and a spell that started before
# the window is not a data-quality case. Set RELIABLE_FROM = None to keep full strings.
SNAPSHOT_MONTH = "2026-08"
RELIABLE_FROM = "2024-01"


def _months_between(first: str, last: str) -> int:
    y0, m0 = map(int, first.split("-"))
    y1, m1 = map(int, last.split("-"))
    return (y1 - y0) * 12 + (m1 - m0) + 1


MAX_HISTORY_MONTHS = _months_between(RELIABLE_FROM, SNAPSHOT_MONTH) if RELIABLE_FROM else None   # 32

# --- string conventions ------------------------------------------------------------------
LEFTMOST_IS_CURRENT = True    # '54320002000': leftmost digit = current month's bucket
CHAR_MAP = {}                 # non-digit BUCKET codes -> digit, e.g. a write-off letter {"W": "9"}.
                              # Never map a pre-opening / padding character to a bucket.
STRIP_CHARS = " "             # removed from the two ENDS only (padding); never mid-string
SPINE_BUCKETS = (4, 5, 6, 7)  # today's spine
EXIT_BUCKET = 8               # 8+ is a different category (leaves the spine)
BACKTEST_MONTHS = 6           # outcomes are read from the newest k digits

# --- optional columns on the same dataset / file (None = not available) -------------------
# Other persona axes, at the latest month. Used only to MEASURE overlap with the
# deterioration states (orthogonality), never to assign states.
AXIS_COLS = {
    "credibility_score": None,      # 0–5 total
    "cred_ptp_points": None,        # 0–2  payment promises kept
    "cred_money_in_points": None,   # 0–2  money coming in, last 3 months
    "cred_clean_point": None,       # 0–1  pre-delinquency history clean
    "ability_score": None,          # salary / inflow / CASA score
    "reachable_flag": None,         # locatability
    "in_country_flag": None,        # locatability
}
# The bank's existing implementations of the two known states, if they exist as columns
# (1/0, Y/N or True/False). Used to measure agreement with this package's
# early_payment_default (the bank's "bust-out") and stabilized.
EXISTING_RULE_COLS = {
    "existing_bust_out": None,
    "existing_stabilized": None,
}
# Data-quality flags that change how a hold should be read (frozen bucket, not paid).
FLAG_COLS = {
    "payment_holiday_flag": None,
    "restructured_flag": None,
}
`````

### FILE: `dpd_states/features.py`
sha256 `a748b3314dc2bd84dcc03295ce9c73ce85ed10a5788059c1d4c45eb8371c47ac` · 177 lines · trailing newline: yes

`````python
"""Encode DPD strings and derive per-account journey features.

Encoding (time runs oldest -> newest after reversing the string):
    b : bucket per month, 0 merged into 1
    d : month-on-month difference. Months paid that month = 1 - d:
        +1 roll (paid nothing) / 0 hold (paid one month's due) / -k (paid k+1 months)
    c : state code per transition
        0 = N  normal (stayed at <=1)
        1 = R  roll, paid nothing (d = +1)
        2 = H  hold at >=2, paid one month (d = 0)
        3 = P  moved back, paid 2+ months (d < 0); back to <=1 is a cure

Data artefacts are cleaned before encoding (all counted, never silent):
  * impossible one-month glitches — a single month at 0/1 between two months at 3+ (a cure
    cannot be followed by a jump to 3+), or a single month at 3+ between two clean months
    (an account cannot jump from 0 to 3) — are read as a hold and as a clean month;
  * billing-cycle +2 jumps (3 3 5 or 3 5 5 for a true 3 4 5) are rewritten as the straight
    roll. The hold BEFORE the jump is preferred as the artefact (it is already observed), the
    hold after only if that does not move a month observed at 4 back below 4; a hold at 0/1
    is never treated as an artefact. Any other +2 stays and is read as a roll.

Features are built to be invariant to the current bucket, which for most of the spine is
only a clock (months since reaching 4): lifetime and run-up features are fixed once the
account passes 4. The two exceptions are deliberate current-behaviour inputs to the
'stabilized' question: last6_in_band, and months_since_4 + chg_6m (long-run clause).
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N, R, H, P = 0, 1, 2, 3
LETTERS = "NRHP"
NO_PRIOR = 9999          # gap value when there is no qualifying earlier spell


def _glitches(b: np.ndarray) -> tuple[np.ndarray, int]:
    """Impossible single-month glitches. Returns (b, n_fixed)."""
    b = b.copy()
    n = 0
    for t in range(1, len(b) - 1):
        if b[t] <= 1 and b[t - 1] >= 3 and b[t + 1] >= 3:      # 4 0 4 -> 4 4 4
            b[t] = b[t - 1]
            n += 1
        elif b[t] >= 3 and b[t - 1] <= 1 and b[t + 1] <= 1:    # 0 3 0 -> 0 0 0
            b[t] = 1
            n += 1
    return b, n


def _repair(b: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Undo +2 billing-cycle jumps next to a hold at >=2. Returns (b, repaired, left)."""
    b = b.copy()
    repaired = 0
    for i in range(len(b) - 1):
        if b[i + 1] - b[i] != 2:
            continue
        if i >= 1 and b[i] == b[i - 1] and b[i] >= 2:                     # 3 3 5 -> 3 4 5
            b[i] += 1
            repaired += 1
        elif i + 2 < len(b) and b[i + 2] == b[i + 1] and b[i + 1] != 4:    # 3 5 5 -> 3 4 5
            b[i + 1] -= 1
            repaired += 1
    left = int((np.diff(b) >= 2).sum())
    return b, repaired, left


def _digits(dpd: str) -> np.ndarray:
    if not isinstance(dpd, str) or not dpd.isdigit():
        raise ValueError(f"DPD string must be digits only, got {dpd!r}")
    return np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)


def encode(dpd: str, repair: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    b = _digits(dpd)
    if repair:
        b = _repair(_glitches(b)[0])[0]
    d = np.diff(b)
    cur = b[1:]
    c = np.full(len(d), R)                  # +1 and any leftover +2 read as a roll
    c[(d == 0) & (cur == 1)] = N
    c[(d == 0) & (cur >= 2)] = H
    c[d < 0] = P
    return b, d, c


def _runs(mask: np.ndarray) -> list[tuple[int, int]]:
    """(start, end_exclusive) of True runs."""
    edges = np.diff(np.concatenate([[0], mask.astype(int), [0]]))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def journey_features(dpd: str) -> dict:
    g, n_glitches = _glitches(_digits(dpd))
    _, n_repaired, n_jumps_left = _repair(g)
    b, d, c = encode(dpd)
    if b[-1] < 2:
        raise ValueError(f"not in a delinquent spell (current bucket < 2): {dpd!r} — "
                         "apply the spine filter (current bucket 4–7) before build_features")
    paid = np.clip(1 - d, 0, None)                      # months paid per month

    episodes = _runs(b >= 2)                            # current spell is the last one
    sp_start, sp_end = episodes[-1]
    # a blip is a 1–2 month excursion that never went past 2 (0 0 2 0 0)
    is_blip = [e - s <= 2 and b[s:e].max() <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]        # blips don't end clean tenure

    def gap_prior(peak: int) -> int:
        """Clean months between the end of the most recent earlier (non-blip) spell that
        reached `peak` and the start of the current spell. Fixed once the spell starts."""
        ends = [e for s, e in prior if b[s:e].max() >= peak]
        return int(sp_start - ends[-1]) if ends else NO_PRIOR

    # transitions landing inside the current spell
    t0 = max(sp_start - 1, 0)
    sp_c, sp_d = c[t0:sp_end - 1], d[t0:sp_end - 1]
    hold_runs = [e - s for s, e in _runs(sp_c == H)]

    # run-up: last clean month -> first month at 4+. Fixed once they pass 4.
    first4 = sp_start + int(np.argmax(b[sp_start:sp_end] >= 4))
    ru_c = c[t0:first4]
    months_since_4 = len(b) - 1 - first4

    # recent behaviour: last 6 months, but only inside the current spell
    w0 = max(len(c) - 6, t0)
    w_c = c[w0:]
    tail_hold = 0
    for x in c[::-1]:
        if x != H:
            break
        tail_hold += 1

    b_now = int(b[-1])
    return {
        "b_now": b_now,
        "hist_len": len(b),
        # lifetime
        "months_before_spell": int(sp_start),
        "clean_tenure_first": int(first_spell),
        "n_blips": int(sum(is_blip)),
        "n_prior_episodes": len(prior),
        "max_prior_bucket": int(max((b[s:e].max() for s, e in prior), default=0)),
        "clean_gap_before_current": int(sp_start - (prior[-1][1] if prior else 0)),
        "gap_prior_peak2": gap_prior(2),
        "gap_prior_peak3": gap_prior(3),
        "gap_prior_peak4": gap_prior(4),
        # run-up (fixed once past 4)
        "runup_len": int(first4 - sp_start + 1),        # 3 = straight 2-3-4
        "runup_holds": int((ru_c == H).sum()),
        "runup_pays": int((ru_c == P).sum()),
        # current spell
        "spell_len": int(sp_end - sp_start),
        "spell_pay_events": int((sp_c != R).sum()),     # months in this spell with a payment
        "max_hold_run": int(max(hold_runs, default=0)),
        "months_since_4": int(months_since_4),          # months since first reaching 4 this spell
        "post4_paid_rate": float(paid[first4:].mean()) if months_since_4 > 0 else 0.0,
        # recent behaviour (rates within the current spell, last 6 months)
        "rec_roll_rate": float((w_c == R).mean()) if len(w_c) else 1.0,
        "rec_paid_rate": float(paid[w0:].mean()) if len(w_c) else 0.0,
        "paid_any_3m": bool((paid[-3:] > 0).any()),     # DPD proxy of 'money coming in'
        "current_hold_run": tail_hold,
        "last6_in_band": int((np.abs(b[-6:] - b_now) <= 1).sum()),
        "chg_6m": int(b_now - b[max(len(b) - 7, 0)]),
        # data quality
        "left_censored": bool(sp_start == 0),           # history starts inside the spell
        "n_glitches": n_glitches,
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


def build_features(df: pd.DataFrame, col: str = "dpd_string") -> pd.DataFrame:
    if len(df) == 0:
        raise ValueError("build_features got an empty frame — check the spine filter / sample")
    feats = pd.DataFrame([journey_features(s) for s in df[col]], index=df.index)
    return pd.concat([df, feats], axis=1)
`````

### FILE: `dpd_states/states.py`
sha256 `2be349b42fd42abd8594b9397540e133becf958d1051f466d98db25ef759dba1` · 196 lines · trailing newline: yes

`````python
"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q0  History starts delinquent?  the string's oldest month is already at bucket 2+
                                (restructured account opened at its old bucket, migrated
                                or missing history) — data quality, not behaviour. Not
                                asked when the string was cropped to the reliable window
                                (a spell older than the window is normal history)
                                                               -> history_starts_delinquent
    Q1  Early payment default?  <=3 months of history before this spell (at most one
                                blip inside it, no earlier real spell) AND never paid
                                since crossing bucket 2: every month of the spell a
                                roll, still falling; and the string was not cropped (it
                                must start at the first billed month) -> early_payment_default
    Q2  Stabilized?             5 of the last 6 months within today's bucket ±1,
                                OR (>= 6 months since first reaching 4 AND at most 1
                                bucket higher than 6 months ago) -> stabilized
    Q3  Paying since 4?         [tested, NOT recommended] paid >= half a month's
                                due per month since first reaching 4 -> paying_since_4
    Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and
                                ended within 24 months before this spell started
                                                               -> repeat_delinquent
    Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
          yes -> straight_roller   [B, C split: >=12 months of history before the spell
                                    -> straight_roller_seasoned, else straight_roller_early_life]
          no  -> slow_roller       [C split: paid 2+ months at once on the way down
                                    -> slow_roller_erratic, else slow_roller_intermittent]

Code names are stable identifiers; DISPLAY_NAMES / REMARKS carry the business labels.

Orthogonality: Q3 (paying now) and Q4 (earlier spell) overlap the payment-credibility
axis (money coming in; pre-delinquency clean), which is why Q3 is off everywhere and Q4
is off in option A. Q1, Q5 and the splits use only the run-up and history length.
Q2 describes current behaviour and moves month to month; EPD ends the month the account
pays; every other state is fixed once the account has passed bucket 4 (it can only move
into stabilized).

Parameters marked [business] are agreed business definitions: change them only with the
business owner — never to make a share or an expectation check come out right.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {
    "epd_max_history": 3,           # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,             # [business] at most one blip (1–2 months at 2, paid off)
    "straight_max_runup": 3,        # months from last clean month to first month at 4
    "stabilized_min_in_band": 5,    # [business] of the last 6 months within today's bucket ±1
    # [business] Long-run clause: an account 6+ months past first reaching 4 that has risen
    # at most one bucket in 6 months has paid roughly what was due, even if unevenly
    # (oscillating payers, accounts that just paid down). Straight rollers cannot meet it:
    # they leave the spine within ~4 months. None disables it.
    "stabilized_long_run_months": 6,
    "stabilized_long_run_max_rise": 1,
    # Q3 tested and NOT recommended: unstable (~37% leave it each month), drags the
    # stability of other states to ~90%, barely separates risk, and is mostly the
    # credibility axis's 'money coming in'. Kept only so the test can be repeated.
    "paying_since_4_min_rate": None,  # e.g. 0.5 -> Q3 on
    "repeat_min_prior_peak": None,  # [business] e.g. 3 -> Q4 on (earlier spell reached 3)
    "repeat_window_months": 24,     # [business] earlier spell ended <= 24 months before this one
    "seasoned_min_months": None,    # [business] e.g. 12 -> split straight roller (first year = early life)
    "split_slow_roller": False,     # True -> split slow roller by 2+ month payments in run-up
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12},
    "C_detailed_7": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12, "split_slow_roller": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["history_starts_delinquent", "early_payment_default", "stabilized", "paying_since_4",
               "repeat_delinquent", "straight_roller", "straight_roller_seasoned",
               "straight_roller_early_life", "slow_roller", "slow_roller_intermittent",
               "slow_roller_erratic"]
# States that never change once the account is past bucket 4 (how they fell in). EPD is
# not one of them: it ends the month the account pays. Stabilized / paying_since_4 describe
# current behaviour. A fixed state may legitimately move INTO stabilized.
FIXED_STATES = [s for s in STATE_ORDER
                if s not in ("early_payment_default", "stabilized", "paying_since_4")]
CURRENT_STATES = ["stabilized", "paying_since_4"]

# Business labels (common card-risk / collections terms). Change freely: code never
# reads these, so renaming for the risk team cannot break the pipeline or old results.
DISPLAY_NAMES = {
    "history_starts_delinquent": "Not classified — history starts delinquent",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "paying_since_4": "Paying since bucket 4 (tested, not used)",
    "repeat_delinquent": "Repeat delinquent (re-default)",
    "straight_roller": "Straight roller",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
    "slow_roller_intermittent": "Intermittent payer",
    "slow_roller_erratic": "Erratic payer",
}
REMARKS = {
    "history_starts_delinquent": "Data quality, not behaviour: the oldest month in the string is "
                                 "already delinquent — typically a restructured card/loan re-opened at "
                                 "its old bucket, a migrated account or missing history. Rare; treatment "
                                 "of restructured accounts is deferred.",
    "early_payment_default": "Never paid since crossing bucket 2 and still falling, at most 3 months "
                             "after the first bill. Called 'bust-out' internally — but classic bust-out "
                             "fraud (good history, limit build-up, then max-out) shows as a seasoned "
                             "straight roller and needs a fraud overlay on spend data.",
    "stabilized": "The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months since "
                  "first reaching 4, at most one bucket higher than 6 months ago) so oscillating "
                  "payers and accounts that just paid down are not mislabelled.",
    "paying_since_4": "Rejected — current-behaviour state that belongs to credibility (money coming in).",
    "repeat_delinquent": "Re-default within 24 months of curing a spell that reached bucket 3; "
                         "collections 'recidivism'.",
    "straight_roller": "Rolled straight to bucket 4 (no payment on the way down). Describes how "
                       "they fell in — some have paid since.",
    "straight_roller_seasoned": "Rolled straight to bucket 4 after at least a year on book (seasoned).",
    "straight_roller_early_life": "Rolled straight to bucket 4 in the first year on book (early-life default).",
    "slow_roller": "Paid something on the way down to bucket 4 but kept rolling. Also called partial payer.",
    "slow_roller_intermittent": "Slow roller that paid one month here and there on the way down.",
    "slow_roller_erratic": "Slow roller that caught up 2+ months at once on the way down, then rolled again.",
}


def option_states(option: str) -> list[str]:
    """Every state an option can produce (for share tables that must show empty states)."""
    p = {**DEFAULTS, **OPTIONS[option]}
    out = ["history_starts_delinquent", "early_payment_default", "stabilized"]
    out += ["paying_since_4"] if p["paying_since_4_min_rate"] is not None else []
    out += ["repeat_delinquent"] if p["repeat_min_prior_peak"] is not None else []
    out += (["straight_roller_seasoned", "straight_roller_early_life"]
            if p["seasoned_min_months"] is not None else ["straight_roller"])
    out += (["slow_roller_erratic", "slow_roller_intermittent"] if p["split_slow_roller"]
            else ["slow_roller"])
    return order(out)


def assign_states(f: pd.DataFrame, **params) -> pd.Series:
    """f: output of features.build_features. Returns one state name per row."""
    p = {**DEFAULTS, **params}
    fast = f.runup_len <= p["straight_max_runup"]
    conds, names = [], []

    def add(cond, name):
        conds.append(cond)
        names.append(name)

    # cropped to the reliable window: the oldest digit is not the first billed month
    cropped = f["history_truncated"].astype(bool) if "history_truncated" in f else False
    add(f.left_censored & ~cropped, "history_starts_delinquent")
    add((f.months_before_spell <= p["epd_max_history"]) & (f.n_blips <= p["epd_max_blips"])
        & (f.n_prior_episodes == 0) & (f.spell_pay_events == 0) & ~cropped, "early_payment_default")
    stab = f.last6_in_band >= p["stabilized_min_in_band"]
    if p["stabilized_long_run_months"] is not None:
        stab |= ((f.months_since_4 >= p["stabilized_long_run_months"])
                 & (f.chg_6m <= p["stabilized_long_run_max_rise"]))
    add(stab, "stabilized")
    if p["paying_since_4_min_rate"] is not None:
        add(f.post4_paid_rate >= p["paying_since_4_min_rate"], "paying_since_4")
    if p["repeat_min_prior_peak"] is not None:
        gap = f[f"gap_prior_peak{min(max(int(p['repeat_min_prior_peak']), 2), 4)}"]
        add(gap <= p["repeat_window_months"], "repeat_delinquent")
    if p["seasoned_min_months"] is not None:
        add(fast & (f.months_before_spell >= p["seasoned_min_months"]), "straight_roller_seasoned")
        add(fast, "straight_roller_early_life")
    else:
        add(fast, "straight_roller")
    if p["split_slow_roller"]:
        add(f.runup_pays >= 1, "slow_roller_erratic")
        default = "slow_roller_intermittent"
    else:
        default = "slow_roller"
    return pd.Series(np.select(conds, names, default), index=f.index)


def order(states) -> list[str]:
    return [s for s in STATE_ORDER if s in set(states)]


def state_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series | None = None) -> pd.DataFrame:
    """Share, outcome and stability per state. Outcome columns need futures
    (`next_bucket`, `exit_6m`) — present in synthetic data and in real-data backtests."""
    g = f.assign(state=state)
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True)})
    if "next_bucket" in g:
        out["roll_next_month"] = (g.next_bucket >= g.b_now + 1).groupby(g.state).mean()
        out["exit_to_8_in_6m"] = g.groupby("state").exit_6m.mean()
    if state_next is not None:
        same = (state.loc[state_next.index] == state_next)
        out["same_state_next_month"] = same.groupby(state.loc[state_next.index]).mean()
    if "paid_any_3m" in g:
        out["paid_in_last_3m"] = g.groupby("state").paid_any_3m.mean()
        out["earlier_spell"] = (g.n_prior_episodes > 0).groupby(g.state).mean()
    return out.loc[order(out.index)]
`````

### FILE: `dpd_states/analysis.py`
sha256 `c157a3300df8b897e6e50fb915b646b74b82e956f455a1d6cb182d05e4623955` · 567 lines · trailing newline: yes

`````python
"""Real-data analysis of deterioration states — pure pandas, no Spark.

`run(current, latest_bt, cfg, spark_counts=None)` takes two small pandas frames that the
Spark snippet has already scoped and sampled:

    current    accounts in today's spine (current bucket 4–7): `dpd_string` plus any
               optional columns named as the keys of cfg.AXIS_COLS / EXISTING_RULE_COLS /
               FLAG_COLS.
    latest_bt  accounts that were in the spine k = cfg.BACKTEST_MONTHS months ago, with
               their string AS OF TODAY (k newer digits on the left). Dropping those k
               digits gives the string as it was k months ago; the dropped digits are what
               happened next. ASSUMES every string ends in the same (latest) month — strings
               frozen at charge-off or closure break this (see METHODOLOGY §8). None = no
               backtest (outcome checks are skipped).

Returns (results, markdown). Both hold aggregates only — no keys and no raw DPD strings;
examples are banded journey shapes shared by at least MIN_SHAPE_COUNT accounts.
"""
from __future__ import annotations

import math
import re

import numpy as np
import pandas as pd

from . import discover as dv
from .features import H, P, build_features, encode, _runs
from .states import (DISPLAY_NAMES, FIXED_STATES, OPTIONS, RECOMMENDED, REMARKS,
                     assign_states, option_states, order)

MIN_SHAPE_COUNT = 10          # governance: never show a journey shape rarer than this


# --- helpers ---------------------------------------------------------------------

def md(df: pd.DataFrame, index: bool = True, floatfmt: str = "{:.3f}") -> str:
    if df is None or len(df) == 0:
        return "_(empty)_"
    if index:
        df = df.reset_index()
    cells = [[floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
             for row in df.itertuples(index=False)]
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in cells])


def _num(v):
    if isinstance(v, (float, np.floating)):
        return None if math.isnan(v) else round(float(v), 4)
    return v.item() if hasattr(v, "item") else v


def _records(df: pd.DataFrame) -> list[dict]:
    return [{str(k): _num(v) for k, v in r.items()} for r in df.reset_index().to_dict("records")]


def _json_safe(obj):
    """Recursively make results JSON-safe: str keys, NaN -> None, numpy -> python."""
    if isinstance(obj, dict):
        return {str(k): _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return _num(obj)


def clean_strings(s: pd.Series, char_map: dict, strip_chars: str, leftmost_is_current: bool = True):
    """Normalise strings; returns (clean series, valid mask). STRIP_CHARS are removed from
    the two ends only — removing them mid-string would shift every older month."""
    s = s.astype(str)
    if strip_chars:
        s = s.str.strip(strip_chars)
    for a, b in (char_map or {}).items():
        s = s.str.replace(a, b, regex=False)
    if not leftmost_is_current:
        s = s.str[::-1]
    valid = s.str.fullmatch(r"\d+").fillna(False).astype(bool) & (s.str.len() > 0)
    return s, valid


_TRUE = {"1", "y", "yes", "true", "t"}
_FALSE = {"0", "n", "no", "false", "f"}


def parse_flag(x: pd.Series) -> tuple[pd.Series, float]:
    """1/0, Y/N, Yes/No, True/False (any case) -> bool. Returns (flag, share unparsed)."""
    t = x.astype(str).str.strip().str.lower()
    known = t.isin(_TRUE | _FALSE)
    return t.isin(_TRUE), float(1 - known[x.notna()].mean()) if x.notna().any() else 1.0


def crop_history(s: pd.Series, max_len: int | None) -> tuple[pd.Series, pd.Series]:
    """Keep the newest max_len months (leftmost digits) — history older than the reliable
    window is dropped. Returns (cropped strings, truncated flag)."""
    if not max_len:
        return s, pd.Series(False, index=s.index)
    return s.str[:max_len], s.str.len() > max_len


def _spells(s: str, from_bucket: int, how: str) -> int:
    """'reached': runs at >=2 that reached the bucket; 'at': runs of months at >= the bucket."""
    b = encode(s)[0]
    if how == "reached":
        return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)
    return len(_runs(b >= from_bucket))


def _eta2(y: pd.Series, g: pd.Series) -> float:
    """Share of the variance of an axis score explained by the state (0 = orthogonal)."""
    y = pd.to_numeric(y, errors="coerce")
    ok = y.notna()
    y, g = y[ok], g[ok]
    if len(y) < 2 or y.var() == 0:
        return float("nan")
    means = y.groupby(g).transform("mean")
    return float(((means - y.mean()) ** 2).sum() / ((y - y.mean()) ** 2).sum())


def _ari(a, b) -> float:
    from sklearn.metrics import adjusted_rand_score
    return float(adjusted_rand_score(a, b))


def _std_rate(outcome: pd.Series, state: pd.Series, bucket: pd.Series) -> pd.Series:
    """Outcome rate per state, standardised to the population's current-bucket mix, so a
    state concentrated at bucket 4 is not flattered (or penalised) by where it sits."""
    mix = bucket.value_counts(normalize=True)
    rates = outcome.astype(float).groupby([state, bucket]).mean().unstack()
    out = {}
    for s_, row in rates.iterrows():
        w = mix[row.dropna().index]
        out[s_] = float((row.dropna() * w).sum() / w.sum()) if w.sum() else float("nan")
    return pd.Series(out)


# --- backtest frame ---------------------------------------------------------------

def backtest_frame(latest: pd.Series, k: int, spine, exit_bucket: int) -> pd.DataFrame:
    """From today's strings, rebuild the spine as of k months ago plus what happened next."""
    latest = latest[latest.str.len() > k]
    as_of = latest.str[k:]
    in_spine = as_of.str[0].astype(int).isin(spine)
    latest, as_of = latest[in_spine], as_of[in_spine]
    fut = latest.str[:k]                                   # newest first
    digits = fut.apply(lambda x: [int(ch) for ch in x])
    return pd.DataFrame({
        "dpd_string": as_of,
        "next_bucket": latest.str[k - 1].astype(int),
        "next_string": latest.str[k - 1:],
        "bucket_k": latest.str[0].astype(int),
        "exit_k": digits.apply(lambda d: max(d) >= exit_bucket),
        "exit_3m": digits.apply(lambda d: max(d[-3:]) >= exit_bucket),   # first 3 future months
        "cure_k": digits.apply(lambda d: min(d) <= 1),
    })


def backtest_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series, spine) -> pd.DataFrame:
    g = f.assign(state=state)
    rolled = g.next_bucket >= g.b_now + 1
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True),
                        "n": g.state.value_counts()})
    out["roll_next_month"] = rolled.groupby(g.state).mean()
    out["roll_next_month_bucket_std"] = _std_rate(rolled, g.state, g.b_now)
    out["exit_8plus_within_3m_bucket_std"] = _std_rate(g.exit_3m, g.state, g.b_now)
    out["exit_8plus_within_k"] = g.groupby("state").exit_k.mean()
    out["cure_within_k"] = g.groupby("state").cure_k.mean()
    out["median_bucket_change_k"] = (g.bucket_k.clip(upper=9) - g.b_now).groupby(g.state).median()
    idx = state_next.index
    out["same_state_next_month"] = (state.loc[idx] == state_next).groupby(state.loc[idx]).mean()
    kept = (state.loc[idx] == state_next) | (state_next == "stabilized")
    out["kept_or_stabilized_next_month"] = kept.groupby(state.loc[idx]).mean()
    out["left_spine_next_month"] = (~g.next_bucket.isin(spine)).groupby(g.state).mean()
    return out.loc[order(out.index)]


def stabilized_flips(latest: pd.Series, k: int, spine, n: int = 10_000, seed: int = 7,
                     truncated: pd.Series | None = None) -> dict:
    """Month-by-month stabilized status over the k backtest months, for a sample of the
    backtest population. A 'bounce-back' is an account that LEFT stabilized and later came
    BACK while staying in the spine (S . S). Entering once and leaving once (. S S .) is a
    normal lifecycle and is not counted. Reported with and without the long-run clause."""
    latest = latest[latest.str.len() > k]
    latest = latest.sample(min(n, len(latest)), random_state=seed)
    tr = truncated if truncated is not None else pd.Series(False, index=latest.index)
    rows = [{"acct": i, "j": j, "dpd_string": s_[k - j:], "history_truncated": bool(tr.get(i, False))}
            for i, s_ in latest.items() for j in range(k + 1)]
    panel = pd.DataFrame(rows)
    panel = panel[panel.dpd_string.str[0].astype(int).isin(spine)]
    out = {"n_accounts": int(latest.size)}
    if not len(panel):
        return out
    pf = build_features(panel)
    for name, kw in (("with_long_run_clause", {}), ("bank_rule_only", {"stabilized_long_run_months": None})):
        st = (assign_states(pf, **OPTIONS[RECOMMENDED], **kw) == "stabilized")
        g = pf.assign(stab=st).sort_values(["acct", "j"])
        cons = g.groupby("acct").j.diff() == 1
        prev = g.groupby("acct").stab.shift(1, fill_value=False).astype(bool)
        left = cons & prev & ~g.stab
        left_before = left.groupby(g.acct).cumsum() - left
        back = cons & ~prev & g.stab & (left_before > 0)
        bounced = back.groupby(g.acct).any()
        changes = (cons & (prev != g.stab)).groupby(g.acct).sum()
        ever = g.groupby("acct").stab.any()
        out[name] = {"ever_stabilized": float(ever.mean()),
                     "bounce_back_share_of_ever_stabilized": float(bounced[ever].mean()) if ever.any() else None,
                     "mean_status_changes_per_account": float(changes.mean())}
    return out


def runup_hold_calendar(f: pd.DataFrame, max_months_ago: int = 36) -> pd.DataFrame:
    """When did run-up holds happen, in calendar months before today? Strings share an
    as-of month, so a spike at one 'months ago' means a system artefact (cycle-date change,
    reversal batch, deferral), not customer behaviour."""
    counts = pd.Series(0, index=range(1, max_months_ago + 1), dtype=float)
    for s in f.dpd_string[f.runup_holds > 0]:
        b, d, c = encode(s)
        ep = _runs(b >= 2)[-1]
        first4 = ep[0] + int(np.argmax(b[ep[0]:ep[1]] >= 4))
        for t in range(max(ep[0] - 1, 0), first4):
            if c[t] == H:
                ago = len(b) - 1 - (t + 1)
                if 1 <= ago <= max_months_ago:
                    counts[ago] += 1
    total = counts.sum()
    return (counts / total).rename("share_of_runup_holds").rename_axis("months_ago").to_frame() if total else counts.to_frame()


# --- main ----------------------------------------------------------------------------

def run(current: pd.DataFrame, latest_bt: pd.DataFrame | None, cfg, spark_counts: dict | None = None,
        seed: int = 7):
    k = cfg.BACKTEST_MONTHS
    spine = tuple(cfg.SPINE_BUCKETS)
    R, M = {}, []            # results (JSON) and markdown sections

    # ---- data quality + current spine --------------------------------------------
    max_len = getattr(cfg, "MAX_HISTORY_MONTHS", None)
    s, ok = clean_strings(current.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
    s, trunc = crop_history(s, max_len)
    cur = current.assign(dpd_string=s, history_truncated=trunc)[ok]
    cur = cur[cur.dpd_string.str[0].astype(int).isin(spine)]
    if not len(cur):
        raise ValueError("no account in today's spine after cleaning — check COL_DPD, "
                         "LEFTMOST_IS_CURRENT, CHAR_MAP and SPINE_BUCKETS in config.py")
    f = build_features(cur)
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}
    f["state"] = opts[RECOMMENDED]

    q = f.hist_len.quantile([.05, .5, .95])
    dq = {
        "n_current_rows": int(len(current)),
        "share_invalid_strings_current": float(1 - ok.mean()),
        "share_non_digit_strings_table": (float(spark_counts["non_digit_strings"] / max(spark_counts["rows"], 1))
                                          if spark_counts else None),
        "n_current_spine_analysed": int(len(f)),
        "max_history_months": max_len,
        "share_history_cropped_to_window": float(f.history_truncated.mean()),
        "share_spell_started_before_window": float((f.left_censored & f.history_truncated).mean()),
        "string_length_p05_p50_p95": [int(x) for x in q],
        "string_length_spread": (int(f.hist_len[~f.history_truncated].quantile(.95)
                                     - f.hist_len[~f.history_truncated].quantile(.05))
                                 if (~f.history_truncated).sum() >= 20 else None),
        "share_history_starts_delinquent": float((f.left_censored & ~f.history_truncated).mean()),
        "share_glitch_fixed": float((f.n_glitches > 0).mean()),
        "share_jump_repaired": float((f.n_jumps_repaired > 0).mean()),
        "share_jump_left": float((f.n_jumps_left > 0).mean()),
        "one_spell_share": {f"{how}_{x}": float((f.dpd_string.map(lambda v: _spells(v, x, how)) == 1).mean())
                            for how in ("reached", "at") for x in (3, 4)},
        "bucket_mix": {str(b): float(v) for b, v in f.b_now.value_counts(normalize=True).sort_index().items()},
    }
    R["data_quality"] = dq
    R["state_names"] = {s_: {"display": DISPLAY_NAMES[s_], "remark": REMARKS[s_]} for s_ in DISPLAY_NAMES}
    M.append("## State names\n\n" + md(pd.DataFrame(
        [{"code": s_, "display name": DISPLAY_NAMES[s_], "remark": REMARKS[s_]} for s_ in DISPLAY_NAMES]),
        index=False))
    dq_tbl = {kk: v for kk, v in dq.items() if not isinstance(v, dict)}
    M.append("## 1. Data quality and population\n\n" + md(pd.Series(dq_tbl, name="value").rename_axis("metric").to_frame())
             + "\n\nShare of the spine with ONE spell only, by definition (the bank quotes ~85% — "
             "the matching row tells which definition the bank uses):\n\n"
             + md(pd.Series({"run at >=2 that reached 3": dq["one_spell_share"]["reached_3"],
                             "run at >=2 that reached 4": dq["one_spell_share"]["reached_4"],
                             "run of months at >=3": dq["one_spell_share"]["at_3"],
                             "run of months at >=4": dq["one_spell_share"]["at_4"]},
                            name="share").rename_axis("spell definition").to_frame()))

    # ---- states today, all options ----------------------------------------------
    R["states_today"] = {}
    parts = ["## 2. States today (current spine)"]
    for o, st in opts.items():
        allowed = option_states(o)
        share = st.value_counts(normalize=True).reindex(allowed, fill_value=0.0).rename_axis("state")
        by_b = pd.crosstab(st, f.b_now, normalize="columns").reindex(allowed, fill_value=0.0)
        by_b = by_b.rename_axis(index="state", columns="bucket")
        R["states_today"][o] = {"share": share.round(4).to_dict(),
                                "by_bucket": {str(c): by_b[c].round(4).to_dict() for c in by_b.columns},
                                "mece": bool(st.notna().all()),
                                "n_unknown_state": int((~st.isin(allowed)).sum())}
        parts.append(f"### {o}\n\nShare:\n\n" + md(share.to_frame("share"))
                     + "\n\nMix by current bucket (column shares):\n\n" + md(by_b))
    shp = f.assign(shape=f.dpd_string.map(dv.shape)).groupby(["state", "shape"]).size().rename("accounts")
    shp = shp[shp >= MIN_SHAPE_COUNT].reset_index()
    shp = shp.sort_values(["state", "accounts"], ascending=[True, False]).groupby("state").head(3)
    shp = shp.sort_values("state", key=lambda x: x.map({s_: i for i, s_ in enumerate(order(x))}))
    parts.append(f"Most common journey shapes per state ({RECOMMENDED}; N clean, R roll, H hold, P paid "
                 f"2+ months; only shapes shared by >= {MIN_SHAPE_COUNT} accounts):\n\n" + md(shp, index=False))
    M.append("\n\n".join(parts))

    # ---- agreement with the bank's existing rules -------------------------------
    agree = {}
    for col, ours in (("existing_bust_out", "early_payment_default"), ("existing_stabilized", "stabilized")):
        if col in f and f[col].notna().any():
            theirs, unparsed = parse_flag(f[col])
            if unparsed > 0.5:
                agree[ours] = {"skipped": f"{unparsed:.0%} of {col} values not recognised as 1/0, Y/N, True/False"}
                continue
            mine = f.state == ours
            agree[ours] = {"their_share": float(theirs.mean()), "our_share": float(mine.mean()),
                           "recall_of_theirs": float((mine & theirs).sum() / max(theirs.sum(), 1)),
                           "precision_vs_theirs": float((mine & theirs).sum() / max(mine.sum(), 1)),
                           "share_unparsed": unparsed}
    R["existing_rule_agreement"] = agree or "SKIPPED (no existing rule columns configured)"
    M.append("## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules\n\n"
             + (md(pd.DataFrame(agree).T.rename_axis("state")) if agree else "_Skipped — no existing rule columns configured._"))

    # ---- overlap with the other persona axes ------------------------------------
    axes = [c for c in cfg.AXIS_COLS if c in f and f[c].notna().any()]
    ov = {}
    if axes:
        eta = pd.DataFrame({o: {a: _eta2(f[a], st) for a in axes} for o, st in opts.items()}).rename_axis("axis")
        means = f.groupby("state")[axes].agg(lambda x: pd.to_numeric(x, errors="coerce").mean())
        means = means.loc[order(means.index)]
        ov = {"eta2_by_option": _records(eta), "mean_by_state": _records(means)}
        txt = ("Variance of each axis explained by the states (eta², 0 = orthogonal):\n\n" + md(eta)
               + f"\n\nMean of each axis by state ({RECOMMENDED}):\n\n" + md(means))
    else:
        txt = "_No axis columns configured — using the DPD proxy for 'money coming in' only._"
    money = "cred_money_in_points" if "cred_money_in_points" in axes else None
    paid_now = (pd.to_numeric(f[money], errors="coerce") > 0) if money else f.paid_any_3m
    stab = f.state == "stabilized"
    ov["stabilized_vs_money_in"] = {"source": money or "DPD proxy (paid >= 1 month in last 3)",
                                    "stabilized_with_money_in": float(paid_now[stab].mean()) if stab.any() else None,
                                    "others_with_money_in": float(paid_now[~stab].mean())}
    mib = paid_now.groupby([f.state, f.b_now]).mean().unstack()
    mib = mib.loc[order(mib.index)].rename_axis(index="state", columns="bucket")
    ov["money_in_by_state_and_bucket"] = {str(c): mib[c].round(4).to_dict() for c in mib.columns}
    flags = {}
    for c in cfg.FLAG_COLS:
        if c in f and f[c].notna().any():
            fl, unparsed = parse_flag(f[c])
            flags[c] = float(fl[stab].mean()) if unparsed <= 0.5 else None
    ov["stabilized_flagged"] = flags
    R["overlap_other_axes"] = ov
    M.append("## 4. Overlap with the other persona axes\n\n" + txt + "\n\nStabilized vs money coming in:\n\n"
             + md(pd.Series(ov["stabilized_vs_money_in"], name="value").rename_axis("metric").to_frame())
             + "\n\nMoney coming in by state and current bucket (slow rollers paid on the way down, so "
             "near bucket 4 they overlap credibility's 'money in' — a clock effect):\n\n" + md(mib)
             + ("\n\nShare of stabilized accounts carrying a data flag (frozen bucket, not a payment):\n\n"
                + md(pd.Series(flags, name="share").to_frame()) if flags else ""))

    # ---- backtest: outcomes and stability ----------------------------------------
    bt = nf = None
    if latest_bt is not None and len(latest_bt):
        s2, ok2 = clean_strings(latest_bt.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
        dq["share_invalid_strings_backtest"] = float(1 - ok2.mean())
        s2, trunc2 = crop_history(s2[ok2], max_len)
        btf = backtest_frame(s2, k, spine, cfg.EXIT_BUCKET)
        btf["history_truncated"] = trunc2.loc[btf.index]
        ok2 = pd.Series(True, index=s2.index)
    else:
        btf = None
    if btf is not None and len(btf):
        bt = build_features(btf)
        nxt = (btf[btf.next_bucket.isin(spine)][["next_string", "history_truncated"]]
               .rename(columns={"next_string": "dpd_string"}))
        nf = build_features(nxt) if len(nxt) else None
        roll = (bt.next_bucket >= bt.b_now + 1).groupby(bt.b_now).mean()
        R["backtest"] = {"k_months": k, "n_analysed": int(len(bt)),
                         "share_exited_within_k": float(bt.exit_k.mean()),
                         "monthly_roll_rate": {str(b): float(v) for b, v in roll.items()},
                         "scorecards": {}}
        parts = [f"## 5. Backtest — spine as of {k} months ago, outcomes since\n\n"
                 f"{len(bt):,} accounts. Monthly roll rate by bucket (should match the bank's "
                 "~70/80/90/95%):\n\n" + md(roll.rename_axis("bucket").to_frame("roll_rate"))]
        for o, kw in OPTIONS.items():
            nxt_st = assign_states(nf, **kw) if nf is not None else pd.Series(dtype=object)
            card = backtest_scorecard(bt, assign_states(bt, **kw), nxt_st, spine)
            R["backtest"]["scorecards"][o] = _records(card)
            parts.append(f"### {o}\n\n" + md(card))
        # slow roller resting on a single paid month vs straight roller
        a_bt = assign_states(bt, **OPTIONS["A_minimal_4"])
        one = (a_bt == "slow_roller") & (bt.runup_holds == 1) & (bt.runup_pays == 0)
        grp = pd.Series(np.select([one, a_bt == "slow_roller", a_bt == "straight_roller"],
                                  ["slow roller: exactly one hold", "slow roller: more than one payment",
                                   "straight roller"], "other"), index=bt.index)
        keep = grp != "other"
        rolled = bt.next_bucket >= bt.b_now + 1
        one_hold = pd.DataFrame({
            "share_of_spine": grp[keep].value_counts() / len(bt),
            "roll_next_month_bucket_std": _std_rate(rolled[keep], grp[keep], bt.b_now[keep]),
            "exit_8plus_within_3m_bucket_std": _std_rate(bt.exit_3m[keep], grp[keep], bt.b_now[keep])})
        R["backtest"]["one_hold_slow_rollers"] = _records(one_hold)
        parts.append("### Is one paid month enough to separate slow from straight rollers?\n\n"
                     + md(one_hold.rename_axis("group")))
        flips = stabilized_flips(s2, k, spine, seed=seed, truncated=trunc2)
        R["backtest"]["stabilized_flips"] = flips
        parts.append(f"### Stabilized bounce-backs over the {k} backtest months "
                     f"({flips['n_accounts']:,} accounts)\n\nShare of ever-stabilized accounts that left "
                     "stabilized and came back while staying in the spine (S . S):\n\n"
                     + md(pd.DataFrame({kk: v for kk, v in flips.items() if isinstance(v, dict)}).T
                          .rename_axis("stabilized rule")))
        M.append("\n\n".join(parts))
    else:
        R["backtest"] = ("SKIPPED (no backtest population: outcomes need strings for accounts that have "
                         "since left the spine — a snapshot of today's segment is survivor-only)")
        # What a snapshot CAN show: stability among accounts that stayed in the spine.
        prev = f[f.dpd_string.str.len() > 1].dpd_string.str[1:]
        prev = prev[prev.str[0].astype(int).isin(spine)]
        prev_tr = f.loc[prev.index, "history_truncated"]
        surv = {"note": "survivor-only: accounts in the spine both last month and today"}
        if len(prev):
            pf = build_features(prev.to_frame("dpd_string").assign(history_truncated=prev_tr))
            st_prev = assign_states(pf, **OPTIONS[RECOMMENDED])
            now = f.loc[pf.index, "state"]
            same = pd.DataFrame({
                "same_state_next_month": (st_prev == now).groupby(st_prev).mean(),
                "kept_or_stabilized_next_month": ((st_prev == now) | (now == "stabilized")).groupby(st_prev).mean(),
                "n": st_prev.value_counts()})
            same = same.loc[order(same.index)]
            surv["same_state_next_month"] = _records(same.rename_axis("state"))
        surv["stabilized_flips"] = stabilized_flips(f.dpd_string, k, spine, seed=seed,
                                                    truncated=f.history_truncated)
        R["survivor_checks"] = surv
        M.append("## 5. Backtest\n\n_Skipped — outcomes (roll rates, exits) need strings for accounts that "
                 "have since left the spine; a snapshot of today's segment only has the survivors._\n\n"
                 "### Survivor-only stability (accounts in the spine last month and today)\n\n"
                 + (md(same) if len(prev) else "_(none)_")
                 + f"\n\nStabilized bounce-backs over the last {k} months:\n\n"
                 + md(pd.DataFrame({kk: v for kk, v in surv["stabilized_flips"].items() if isinstance(v, dict)}).T
                      .rename_axis("stabilized rule")))

    # ---- run-up holds by calendar month (artefact check) ---------------------------
    cal = runup_hold_calendar(f)
    if len(cal) and cal.iloc[:, 0].sum():
        v = cal.iloc[:, 0]
        # a month compared with the median of its neighbours (±2 months): the natural shape
        # (more holds in recent months) cancels out, a one-month system event does not
        ratios = {}
        for m in v.index:
            nb_ = v[[x for x in range(m - 2, m + 3) if x != m and x in v.index]]
            base_ = float(nb_.median())
            if base_ > 0 and v[m] * len(f) >= 20:                 # ignore near-empty months
                ratios[m] = float(v[m] / base_)
        R["runup_hold_calendar_spike"] = max(ratios.values()) if ratios else None
        R["runup_hold_calendar"] = {str(i): float(x) for i, x in v.items()}
        spike = R["runup_hold_calendar_spike"]
        M.append("## 5b. Run-up holds by calendar month (months before today)\n\nEach month is "
                 "compared with its neighbours (±2 months); a month far above them points to a system "
                 "artefact (cycle-date change, reversal batch, deferral), not customer behaviour. "
                 f"Largest month / neighbour-median ratio: {spike if spike is None else round(spike, 2)}\n\n" + md(cal))

    # ---- threshold sweeps (on the backtest population when available) ------------
    base = bt if bt is not None else f
    nb = nf if bt is not None else None
    sw = {}

    def _stay(kw, name):
        if nb is None:
            return None
        a, b = assign_states(base, **kw), assign_states(nb, **kw)
        m = (a == name).loc[nb.index]
        return float((b[m[m].index] == name).mean()) if m.any() else None

    rows = []
    for v in (2, 3, 4, 6, 9, 12):
        st = assign_states(base, epd_max_history=v)
        b_ = st == "early_payment_default"
        rows.append({"epd_max_history": v, "share": b_.mean(),
                     "exit_within_k": base.exit_k[b_].mean() if bt is not None and b_.any() else None})
    sw["epd_max_history"] = rows
    rows = []
    for v in (4, 5, 6):
        st = assign_states(base, stabilized_min_in_band=v)
        h = st == "stabilized"
        rows.append({"stabilized_min_in_band": v, "share": h.mean(),
                     "roll_next_month": (base.next_bucket[h] >= base.b_now[h] + 1).mean() if bt is not None and h.any() else None,
                     "still_stabilized_next_month": _stay({"stabilized_min_in_band": v}, "stabilized")})
    sw["stabilized_min_in_band"] = rows
    rows = []
    for v in (2, 3, 4):
        for w in (12, 24, 36, 9999):
            st = assign_states(base, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v, "repeat_window_months": w})
            rows.append({"repeat_min_prior_peak": v, "repeat_window_months": "any" if w == 9999 else w,
                         "share": (st == "repeat_delinquent").mean()})
    sw["repeat_delinquent"] = rows
    rows = []
    for v in (3, 4, 5):
        st = assign_states(base, straight_max_runup=v)
        rows.append({"straight_max_runup": v, "straight_share": (st == "straight_roller").mean(),
                     "slow_share": (st == "slow_roller").mean()})
    sw["straight_max_runup"] = rows
    rows = []
    for v in (12, 18, 24, 36):
        st = assign_states(base, **{**OPTIONS[RECOMMENDED], "seasoned_min_months": v})
        rows.append({"seasoned_min_months": v, "seasoned": (st == "straight_roller_seasoned").mean(),
                     "early_life": (st == "straight_roller_early_life").mean()})
    sw["seasoned_min_months"] = rows
    rows = []
    for v in (0.34, 0.5, 0.67):
        kw = {**OPTIONS["C_detailed_7"], "paying_since_4_min_rate": v}
        st = assign_states(base, **kw)
        row = {"paying_since_4_min_rate": v, "share": (st == "paying_since_4").mean(),
               "still_paying_since_4_next_month": _stay(kw, "paying_since_4")}
        if nb is not None:
            st2 = assign_states(nb, **kw)
            fixed = st.loc[nb.index].isin(FIXED_STATES)
            row["stability_of_fixed_states"] = float((st.loc[nb.index][fixed] == st2[fixed]).mean())
            kw0 = OPTIONS["C_detailed_7"]
            a0, b0 = assign_states(base, **kw0).loc[nb.index], assign_states(nb, **kw0)
            fx0 = a0.isin(FIXED_STATES)
            row["stability_of_fixed_states_without_q3"] = float((a0[fx0] == b0[fx0]).mean())
        rows.append(row)
    sw["paying_since_4_test"] = rows
    R["sweeps"] = {kk: [{a: _num(b) for a, b in r.items()} for r in v] for kk, v in sw.items()}
    M.append("## 6. Threshold sweeps (" + ("backtest population" if bt is not None else "current spine")
             + "). Parameters marked [business] in states.py are agreed definitions — the sweeps "
             "show sensitivity; they are not a menu for matching a share.\n\n"
             + "\n\n".join(f"### {kk}\n\n" + md(pd.DataFrame(v), index=False) for kk, v in sw.items()))

    # ---- residual clustering agreement (diagnostic only) ---------------------------
    a_states = opts["A_minimal_4"]
    r = f[~a_states.isin(["early_payment_default", "stabilized", "history_starts_delinquent"])]
    if len(r) > 30_000:
        r = r.sample(30_000, random_state=seed)
    if len(r) >= 50:
        from sklearn.cluster import KMeans
        from sklearn.preprocessing import StandardScaler
        feats = ["months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
                 "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
                 "post4_paid_rate", "rec_paid_rate"]
        X = r[feats].astype(float).copy()
        for c in ("months_before_spell", "clean_gap_before_current", "runup_len"):
            X[c] = np.log1p(X[c])
        X = StandardScaler().fit_transform(X)
        rows = []
        for kk in range(2, 9):
            lab = KMeans(kk, n_init=10, random_state=seed).fit_predict(X)
            rows.append({"k": kk, **{f"agree_{o}": _ari(lab, st.loc[r.index]) for o, st in opts.items()}})
        R["residual_cluster_agreement"] = rows
        M.append("## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with each "
                 "option. Diagnostic only: a finer partition built on the clustered features always "
                 "gains ARI, so this is not evidence for B over A.\n\n" + md(pd.DataFrame(rows), index=False))
    else:
        R["residual_cluster_agreement"] = "SKIPPED (fewer than 50 residual accounts)"

    # ---- shapes and motifs ---------------------------------------------------------
    smp = f.sample(min(len(f), 30_000), random_state=seed)
    shapes = dv.shape_table(smp, label="state", top=20)
    shapes = shapes[shapes.n >= MIN_SHAPE_COUNT]
    grams = dv.ngram_table(smp, n=4, label="state", top=15)
    R["top_shapes"] = _records(shapes.set_index("shape"))
    R["top_4grams"] = _records(grams.set_index("gram")) if len(grams) else []
    M.append("## 8. Most common journey shapes and motifs\n\nShapes (N clean, R roll, H hold = paid "
             f"one month, P paid 2+ months; run lengths banded; shared by >= {MIN_SHAPE_COUNT} accounts):\n\n"
             + md(shapes, index=False) + "\n\n4-grams by lift vs shuffled order:\n\n" + md(grams, index=False))

    return _json_safe(R), "\n\n".join(M)
`````

### FILE: `dpd_states/expectations.py`
sha256 `c961ab8a1e3c18eecec8a46345c5fc045c38b5af8750330bf9137690191b3159` · 349 lines · trailing newline: yes

`````python
"""What we expect to see on real data, as checkable rules.

Each expectation states the metric, the expected range, what the range is anchored on,
why we expect it, and what to do if it is not met. `evaluate(R)` reads the results dict
from analysis.run (in memory or re-loaded from the saved JSON — same answer) and returns
one row per check with PASS / WARN / FAIL / SKIPPED / INFO.

Severity: FAIL = the run itself is not trustworthy (fix config/data before reading
anything else). WARN = the run is fine but an assumption behind the design is off —
follow the 'if not met' action. INFO = reported, no pass/fail.

Anchor: bank = the bank's own figures or rules · design = follows from the rules by
construction · synthetic = calibrated on the synthetic generator only (a WARN there is a
prompt to look, not proof of a problem) · data = data-quality expectation.

Actions never say "tune a [business] parameter until the check passes": business
definitions change only with the business owner (escalate).
"""
from __future__ import annotations

import pandas as pd

from .states import FIXED_STATES, RECOMMENDED, option_states

ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}
MIN_N = 100                    # states smaller than this are not used in stability checks


def _card(R, option):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rows = bt["scorecards"][option]
    return pd.DataFrame(rows).set_index("state" if "state" in rows[0] else "index") if rows else None


def _share(R, option):
    allowed = [s for s in option_states(option) if s != "history_starts_delinquent"]
    return pd.Series(R["states_today"][option]["share"]).reindex(allowed).fillna(0.0)


def _sweep(R, name):
    return pd.DataFrame(R["sweeps"][name])


def _eta(R, axis, option=RECOMMENDED):
    ov = R.get("overlap_other_axes", {})
    if "eta2_by_option" not in ov:
        return None
    eta = pd.DataFrame(ov["eta2_by_option"]).set_index("axis")
    return float(eta.loc[axis, option]) if axis in eta.index and eta.loc[axis, option] is not None else None


def _agree(R, state, key):
    a = R.get("existing_rule_agreement")
    return a[state].get(key) if isinstance(a, dict) and state in a else None


def _bucket(d, b):
    return d.get(str(b), d.get(b))


def _stab_gap(R):
    c = _card(R, RECOMMENDED)
    if c is None or "stabilized" not in c.index:
        return None
    col = "roll_next_month_bucket_std"
    rolling = c.loc[[s for s in c.index if s in FIXED_STATES or s == "early_payment_default"], col].dropna()
    w = c.loc[rolling.index, "share"]
    return float((rolling * w).sum() / w.sum() - c.loc["stabilized", col])


def _surv_card(R):
    sc = R.get("survivor_checks", {})
    rows = sc.get("same_state_next_month")
    return pd.DataFrame(rows).set_index("state") if rows else None


def _fixed_stability(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        c = _surv_card(R)                 # snapshot-only run: survivors in the spine both months
    if c is None:
        return None
    c = c[(c.index.isin(FIXED_STATES)) & (c.n >= MIN_N)]
    return float(c.kept_or_stabilized_next_month.min()) if len(c) else None


def _stab_persist(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        c = _surv_card(R)
    return float(c.loc["stabilized", "same_state_next_month"]) if c is not None and "stabilized" in c.index else None


def _flips(R):
    bt = R.get("backtest")
    fl = bt.get("stabilized_flips") if isinstance(bt, dict) else R.get("survivor_checks", {}).get("stabilized_flips")
    return (fl or {}).get("with_long_run_clause", {}).get("bounce_back_share_of_ever_stabilized")


def _roll_dev(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rr = bt["monthly_roll_rate"]
    return max(abs((_bucket(rr, b) if _bucket(rr, b) is not None else float("nan")) - t)
               for b, t in ROLL_TARGET.items())


def _invalid(R):
    dq = R["data_quality"]
    vals = [dq.get("share_invalid_strings_current"), dq.get("share_invalid_strings_backtest"),
            dq.get("share_non_digit_strings_table")]
    vals = [v for v in vals if v is not None]
    return max(vals) if vals else None


def _spell_closest(R):
    one = R["data_quality"]["one_spell_share"]
    name = min(one, key=lambda kk: abs(one[kk] - 0.85))
    return f"{name}: {one[name]:.2f}"


def _resid_gain(R):
    rows = R.get("residual_cluster_agreement")
    if not isinstance(rows, list):
        return None
    rows = pd.DataFrame(rows).set_index("k")
    return float(rows.loc[6, f"agree_{RECOMMENDED}"] - rows.loc[6, "agree_A_minimal_4"])


def _one_hold(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict) or "one_hold_slow_rollers" not in bt:
        return None
    t = pd.DataFrame(bt["one_hold_slow_rollers"]).set_index("index")
    a = t.loc["slow roller: exactly one hold", "roll_next_month_bucket_std"]
    b = t.loc["straight roller", "roll_next_month_bucket_std"]
    return float(b - a)


def _partial(R):
    sw = _sweep(R, "paying_since_4_test").set_index("paying_since_4_min_rate")
    if "stability_of_fixed_states" not in sw or 0.5 not in sw.index:
        return None
    return sw.loc[0.5, "still_paying_since_4_next_month"]


def _spread(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    x = c.loc[[s for s in c.index if s in FIXED_STATES and s != "history_starts_delinquent"],
              "exit_8plus_within_3m_bucket_std"].dropna()
    return float(x.max() - x.min()) if len(x) > 1 else None


def _by_bucket_ratio(R):
    bb = R["states_today"][RECOMMENDED]["by_bucket"]
    at4 = (_bucket(bb, 4) or {}).get("stabilized", 0)
    at7 = (_bucket(bb, 7) or {}).get("stabilized", 0)
    return at4 / max(at7, 1e-9)


def _bucket_mix_drop(R):
    mix = R["data_quality"]["bucket_mix"]
    return (_bucket(mix, 4) or 0) - (_bucket(mix, 7) or 0)


def _max_eta(R, axes):
    vals = [v for v in (_eta(R, a) for a in axes) if v is not None]
    return max(vals) if vals else None


# id, title, metric(R), check(value)->bool, expected, severity, anchor, why, if not met
EXPECTATIONS = [
    ("E01", "Every account gets exactly one known state (all options)",
     lambda R: all(v["mece"] and v["n_unknown_state"] == 0 for v in R["states_today"].values()),
     lambda v: v is True, "True", "FAIL", "design",
     "The tree ends in a default branch, so it is MECE by construction; unknown labels mean a code change broke it.",
     "A code or data-type bug — stop and fix before reading anything else."),
    ("E02", "Unparseable strings (worst of: today's spine, backtest, whole table)",
     _invalid, lambda v: v <= 0.02, "<= 2%", "FAIL", "data",
     "Strings should be digits once CHAR_MAP / STRIP_CHARS are set.",
     "Inspect the non-digit characters (check-only output); extend CHAR_MAP (e.g. a write-off letter "
     "-> 9). Untreated letters silently drop accounts from the backtest."),
    ("E03", "Backtest monthly roll rates vs the bank's 70/80/90/95% (max abs deviation)",
     _roll_dev, lambda v: v <= 0.07, "<= 7pp", "FAIL", "bank",
     "Confirms the string orientation and that the one-table backtest is valid.",
     "Check, in order: LEFTMOST_IS_CURRENT; that every string ends in the SAME month (strings frozen at "
     "charge-off/closure, or exited accounts dropped from the table, make roll rates too low — set "
     "COL_STRING_AS_OF); letter exit codes missing from CHAR_MAP; whether the bank's roll rates are "
     "count- or balance-weighted."),
    ("E04", "Histories that start already delinquent (history_starts_delinquent)",
     lambda R: R["data_quality"]["share_history_starts_delinquent"], lambda v: v <= 0.01,
     "<= 1%", "WARN", "bank",
     "The first digit is the first billed month (0/1); exceptions are rare data issues and restructured "
     "accounts re-opened at their old bucket.",
     "Confirm the string-start convention (PROMPTS P1). Many cases point to restructured accounts or "
     "truncated strings — their treatment is a deferred business decision."),
    ("E05", "Accounts with an unrepaired +2 jump",
     lambda R: R["data_quality"]["share_jump_left"], lambda v: v <= 0.02,
     "<= 2%", "WARN", "synthetic",
     "Billing-cycle jumps mostly sit next to a hold and get repaired.",
     "Look at the shapes; a systematic code (e.g. 2-cycle buckets) needs an encoding change."),
    ("E06", "Current bucket mix declines from 4 to 7 (share at 4 minus share at 7)",
     _bucket_mix_drop, lambda v: v >= 0, ">= 0", "WARN", "bank",
     "Rising roll rates 70→95% thin the spine out towards bucket 7.",
     "Check the spine filter and whether a cohort shock is passing through."),
    ("E07", "INFO — one-spell share: definition closest to the bank's ~85%",
     _spell_closest, None, "report", "INFO", "bank",
     "Four spell definitions are reported in section 1; the bank's exact one is unconfirmed.",
     "Get the bank's definition; if it is 'reached 4' or 'run at >=4', discuss repeat_min_prior_peak."),
    ("E08", "Early payment default share (today)",
     lambda R: float(_share(R, RECOMMENDED).get("early_payment_default", 0)), lambda v: 0.03 <= v <= 0.08,
     "3–8%", "WARN", "bank",
     "Bank's own bust-out rule gives ~6%; the agreed definition is stricter (never paid since crossing 2).",
     "Compare with the bank's rule (E10, PROMPTS P4) and escalate to the business owner. Do not move "
     "epd_max_history to match a share."),
    ("E09", "Stabilized share (today)",
     lambda R: float(_share(R, RECOMMENDED).get("stabilized", 0)), lambda v: 0.04 <= v <= 0.10,
     "4–10%", "WARN", "bank",
     "Bank's 5-of-6 rule gives ~6%; the long-run clause adds about one point.",
     "Compare with the bank's implementation (E11, PROMPTS P4) and escalate."),
    ("E10", "Recall of the bank's existing bust-out flag by our EPD",
     lambda R: _agree(R, "early_payment_default", "recall_of_theirs"), lambda v: v >= 0.80,
     ">= 80%", "WARN", "bank",
     "Same concept; ours additionally requires no payment since crossing bucket 2.",
     "Read the bank's rule (PROMPTS P4), list the differences and escalate."),
    ("E11", "Recall of the bank's existing stabilized flag by our stabilized",
     lambda R: _agree(R, "stabilized", "recall_of_theirs"), lambda v: v >= 0.90,
     ">= 90%", "WARN", "bank",
     "Ours is the bank's 5-of-6 rule plus the long-run clause; differences: EPD/ordering, glitch and "
     "+2-jump cleaning.",
     "Check the band definition (±1 of today's bucket, 5 of the last 6 months incl. today)."),
    ("E12", "Stabilized separates risk: fixed states' next-month roll minus stabilized (bucket-standardised)",
     _stab_gap, lambda v: v >= 0.20, ">= 20pp", "WARN", "synthetic",
     "Synthetic: ~0.37. Standardised to the same bucket mix, because stabilized sits mostly at bucket 4.",
     "Stabilized is not behaving as stable: check payment holidays / restructuring flags (E21) and "
     "escalate whether to use 6 of 6."),
    ("E13", f"Fixed states keep their state (or move into stabilized) next month — min over states with n >= {MIN_N}",
     _fixed_stability, lambda v: v >= 0.95, ">= 95%", "WARN", "design",
     "Run-up, history and the repairs are causal: how they fell in never changes once past 4. EPD is "
     "not fixed (it ends when the account pays) and moving into stabilized is not a leak.",
     "A feature is drifting with time or with the next month's data — find the leaking state."),
    ("E14", "Stabilized persistence next month",
     _stab_persist,
     lambda v: 0.45 <= v <= 0.85, "45–85%", "WARN", "synthetic",
     "Stabilized is current behaviour; it should persist but not forever (synthetic ~60%).",
     "Too low: the band is too loose. Too high: frozen buckets (holidays) are read as payments."),
    ("E15", "Option A: straight-roller share",
     lambda R: float(_share(R, "A_minimal_4").get("straight_roller", 0)), lambda v: 0.55 <= v <= 0.80,
     "55–80%", "WARN", "bank",
     "Most accounts roll straight 2-3-4 (synthetic ~70%).",
     "If much lower, many run-ups contain a hold — look at E28 (artefacts) before trusting slow roller."),
    ("E16", "Smallest optional state in option B (EPD and stabilized are required; empty = 0)",
     lambda R: float(_share(R, "B_balanced_6").drop(["early_payment_default", "stabilized"]).min()),
     lambda v: v >= 0.05, ">= 5%", "WARN", "design",
     "Actionable size for the optional splits; the bank's two known states are kept at any size. "
     "Synthetic: early-life straight roller ~4.7% under the 12-month cut.",
     "If it is early-life straight roller: merge it into straight roller (agreed with the owner: set "
     "seasoned_min_months=None and keep early life as a flag). Any other state: escalate."),
    ("E17", "Option C: smaller of intermittent / erratic payer",
     lambda R: float(_share(R, "C_detailed_7").reindex(["slow_roller_intermittent", "slow_roller_erratic"]).fillna(0).min()),
     lambda v: v >= 0.04, ">= 4%", "WARN", "design",
     "Synthetic 10% / 6%.", "Too small to act on — use option B."),
    ("E18", "Stabilized sits low in the spine: share at bucket 4 / share at bucket 7",
     _by_bucket_ratio, lambda v: v >= 2, ">= 2x", "WARN", "bank",
     "90–95% roll rates at 6–7 leave little room to hold there.",
     "Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays)."),
    ("E19", "Orthogonality: credibility score explained by the states (eta²)",
     lambda R: _eta(R, "credibility_score"), lambda v: v <= 0.25, "<= 0.25", "WARN", "design",
     "Known overlap via stabilized (money in), slow roller (money in near bucket 4) and repeat "
     "delinquent (clean point); the states should not reproduce the score.",
     "Use option A (drops repeat delinquent) or report stabilized under credibility instead."),
    ("E19b", "Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²)",
     lambda R: _eta(R, "cred_clean_point"), lambda v: v <= 0.50, "<= 0.50", "WARN", "design",
     "Repeat delinquent uses earlier spells — the history the clean point scores (now limited to the "
     "last 24 months, which lowers the overlap).",
     "Repeat delinquent duplicates the clean point: use option A, or keep it and tell the persona grid "
     "it is the same signal (only 1 of credibility's 5 points)."),
    ("E20", "Orthogonality: ability score explained by the states (eta²)",
     lambda R: _eta(R, "ability_score"), lambda v: v <= 0.10, "<= 0.10", "WARN", "design",
     "DPD shape should carry little of salary/inflow/CASA.",
     "Straight vs slow roller may proxy income loss — fine, but say so in the persona grid."),
    ("E20b", "Orthogonality: reachability / in-country explained by the states (max eta²)",
     lambda R: _max_eta(R, ["reachable_flag", "in_country_flag"]), lambda v: v <= 0.05, "<= 0.05",
     "WARN", "design", "Locatability is independent of how the debt was paid.",
     "A state is acting as a departure proxy — report it to the persona owners."),
    ("E21", "Stabilized accounts with money coming in (credibility component or DPD proxy)",
     lambda R: R["overlap_other_axes"]["stabilized_vs_money_in"]["stabilized_with_money_in"],
     lambda v: v >= 0.90, ">= 90%", "WARN", "design",
     "Stabilized = paid one month's due most months, so money must be coming in.",
     "Stabilized accounts without money in are frozen buckets (holiday/restructure) — flag them."),
    ("E22", "INFO — residual clusters: option-B ARI gain over option A at k=6",
     _resid_gain, None, "report", "INFO", "synthetic",
     "Diagnostic only: any finer partition built on the clustered features gains ARI (a meaningless "
     "tenure split gained 0.16 in review), so this is not evidence for B over A.",
     "—"),
    ("E23", "INFO — one paid month: straight minus one-hold slow roller, next-month roll (bucket-std)",
     _one_hold, None, "report", "INFO", "synthetic",
     "41% of slow rollers rest on a single hold. Unknowable from synthetic data (same post-4 dynamics).",
     "Near 0 and E28 shows artefacts: the straight/slow split rests on noise — escalate whether a single "
     "hold should still make a slow roller (straight_max_runup = 4)."),
    ("E24", "'Paying since 4' stays rejected: share still in it next month at 0.5",
     _partial, lambda v: v <= 0.75, "<= 75%", "WARN", "synthetic",
     "Synthetic ~63%: an unstable current-behaviour state.",
     "If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'."),
    ("E25", "INFO — spread of exit to 8+ within 3 months across fixed states (option B, bucket-std)",
     _spread, None, "report", "INFO", "synthetic",
     "Standardised to the bucket mix and over 3 months, because 6-month exit saturates near 100% at 5–7.",
     ">= 5pp means how they fell in carries risk information beyond stabilized."),
    ("E26", "Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months",
     _flips,
     lambda v: v <= 0.10, "<= 10%", "WARN", "synthetic",
     "Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating payers "
     "bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold).",
     "Too many bounce: look at shapes; +2 tolerance or a sticky rule widen the definition — escalate."),
    ("E27", "Uncropped string lengths vary (p95 minus p05 of history length, months)",
     lambda R: R["data_quality"]["string_length_spread"], lambda v: v >= 6, ">= 6", "WARN", "data",
     "Full history from the first billed month gives very different lengths across accounts.",
     "Strings look fixed-length (padded or truncated): EPD and early-life cannot be judged from the "
     "string — confirm the convention (PROMPTS P1) before reading those states."),
    ("E28", "Run-up holds by calendar month: largest month vs its neighbours (artefact check)",
     lambda R: R.get("runup_hold_calendar_spike"), lambda v: v <= 2.5, "<= 2.5", "WARN", "data",
     "Customer payments spread over calendar months; a spike means a system event (cycle-date change, "
     "reversal batch, deferral).",
     "Find the month (section 5b) and ask the data owners; holds from that month should not count."),
]


def evaluate(R: dict) -> pd.DataFrame:
    rows = []
    for eid, title, metric, check, expected, sev, anchor, why, action in EXPECTATIONS:
        try:
            v = metric(R)
        except (KeyError, TypeError, ValueError, IndexError, AttributeError, ZeroDivisionError):
            v = None
        if v is None or (isinstance(v, float) and v != v):
            status = "SKIPPED"
        elif check is None:
            status = "INFO"
        else:
            status = "PASS" if check(v) else sev
        rows.append({"id": eid, "status": status, "check": title,
                     "observed": round(v, 3) if isinstance(v, float) else v,
                     "expected": expected, "anchor": anchor, "why": why, "if_not_met": action})
    return pd.DataFrame(rows)
`````

### FILE: `dpd_states/file_mode.py`
sha256 `459464c28c496f0b80ec218b4ab2b3d4717479fcf67e4d42764d76c5a2438d29` · 117 lines · trailing newline: yes

`````python
"""Validate the states on a DPD-history FILE (xlsx / csv / parquet) — no Spark needed.

    python docs/deterioration_states/run.py validate                              # cfg.INPUT_FILE
    python docs/deterioration_states/run.py validate data/input/other_file.xlsx   # another file

Reads cfg.COL_DPD (leftmost = most recent month) as TEXT, keeps today's spine (current
bucket in cfg.SPINE_BUCKETS), runs analysis.run + the expectations, and writes
results/dpd_states_file_<file>_<date>.json + .md (aggregates only, no keys, no raw strings).

A snapshot of today's segment has no outcomes: accounts that rolled to 8+ since are not
in it, so roll rates / exits are SKIPPED. Stability checks run on the survivors.
"""
from __future__ import annotations

import datetime
import json
import pathlib
import re

import pandas as pd

from . import config as cfg
from .analysis import md, run
from .expectations import evaluate
from .states import DISPLAY_NAMES, RECOMMENDED


def _repo_root() -> pathlib.Path:
    here = pathlib.Path(__file__).resolve()
    for parent in here.parents:
        if (parent / ".git").exists() or (parent / "conf").is_dir():
            return parent
    return here.parents[3]


def _read(path: pathlib.Path, col: str) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in (".xlsx", ".xlsm", ".xls"):
        try:
            return pd.read_excel(path, dtype={col: str})
        except ImportError as e:                       # openpyxl missing
            raise SystemExit(f"{e}\nInstall it with: python -m pip install openpyxl") from None
    if suffix == ".csv":
        return pd.read_csv(path, dtype={col: str})
    if suffix == ".parquet":
        return pd.read_parquet(path)
    raise SystemExit(f"unsupported file type {suffix!r} — use .xlsx, .csv or .parquet")


def main(path: str | None = None, sample_n: int = 100_000, out_dir: str | None = None, seed: int = 42) -> dict:
    root = _repo_root()
    src = pathlib.Path(path) if path else pathlib.Path(cfg.INPUT_FILE)
    if not src.is_absolute() and not src.exists():
        src = root / src
    if not src.exists():
        raise SystemExit(f"input file not found: {src}")
    col = cfg.COL_DPD
    df = _read(src, col)
    if col not in df.columns:
        raise SystemExit(f"column {col!r} not in {src.name}. Available: {sorted(map(str, df.columns))}\n"
                         "Set COL_DPD in dpd_states/config.py.")

    s = df[col].astype("string")
    looks_numeric = s.str.contains(r"[.eE+]", regex=True, na=False).mean()
    if looks_numeric > 0.01:
        raise SystemExit(f"{looks_numeric:.0%} of {col} look like numbers (e.g. '5.4e+10'): the column was "
                         "stored as a number, which drops digits. Re-export it as text.")

    keep = {"dpd_string": s}
    optional = {**cfg.AXIS_COLS, **cfg.EXISTING_RULE_COLS, **cfg.FLAG_COLS}
    present = {name: c for name, c in optional.items() if c and c in df.columns}
    for name, c in present.items():
        keep[name] = df[c]
    cur = pd.DataFrame(keep).dropna(subset=["dpd_string"])
    cur["dpd_string"] = cur.dpd_string.astype(str)

    lead = cur.dpd_string.str.strip(cfg.STRIP_CHARS or None).str[:1]
    in_spine = lead.isin([str(b) for b in cfg.SPINE_BUCKETS])
    counts = {"rows": int(len(df)), "rows_with_string": int(len(cur)),
              "current_spine": int(in_spine.sum()),
              "non_digit_strings": int((~cur.dpd_string.str.strip(cfg.STRIP_CHARS or None)
                                        .str.fullmatch(r"\d+").fillna(False)).sum())}
    cur = cur[in_spine]
    if len(cur) > sample_n:
        cur = cur.sample(sample_n, random_state=seed)

    R, report = run(cur.reset_index(drop=True), None, cfg, spark_counts=counts)
    checks = evaluate(R)

    stamp = datetime.date.today().strftime("%Y%m%d")
    slug = re.sub(r"[^A-Za-z0-9]+", "_", src.stem).strip("_")
    out = pathlib.Path(out_dir) if out_dir else pathlib.Path(__file__).resolve().parents[1] / "results"
    out.mkdir(parents=True, exist_ok=True)
    scope = (f"file {src.name}, column {col}; today's spine = leftmost digit in "
             f"{list(cfg.SPINE_BUCKETS)}; sampled to <= {sample_n:,}")
    payload = {"task": "DPD_STATES_VALIDATION_FILE", "run_date": datetime.date.today().isoformat(),
               "source": src.name, "scope": scope, "counts": counts,
               "optional_columns_present": sorted(present), "results": R,
               "expectations": checks.to_dict("records")}
    jf = out / f"dpd_states_file_{slug}_{stamp}.json"
    jf.write_text(json.dumps(payload, indent=2, default=str))
    mf = jf.with_suffix(".md")
    mf.write_text(f"# DPD deterioration states — validation on {src.name}\n\nRun {payload['run_date']} · "
                  f"{scope}\n\n## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    rec = R["states_today"][RECOMMENDED]["share"]
    print("=== DPD_STATES OUTPUT START ===")
    print(f"source: {src.name}")
    print(f"scope: {scope}")
    print(f"counts: {counts}")
    print(f"expectations: {checks.status.value_counts().to_dict()}")
    for r in checks.itertuples():
        print(f"  {r.id:<4} {r.status:<7} observed={r.observed!s:<14} expected={r.expected:<8} {r.check[:70]}")
    print(f"{RECOMMENDED} shares today: " + ", ".join(f"{DISPLAY_NAMES[k]}={v:.1%}" for k, v in rec.items()))
    print(f"wrote: {jf} and {mf.name}")
    print("=== DPD_STATES OUTPUT END ===")
    return payload
`````

### FILE: `dpd_states/discover.py`
sha256 `b78da74aa467ec7d9029a99e489ad9266aa765946c3c0f44d289a5c9fba94bbd` · 136 lines · trailing newline: yes

`````python
"""Pattern discovery on encoded DPD journeys: shapes, n-grams, feature clusters, rule tree."""
from __future__ import annotations

from collections import Counter

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text

from .features import LETTERS, N, encode

# Run-length bands per code. R bands end at 3+ so a straight roll to 4 and to 7
# give the same shape (the current bucket is mostly a clock).
BANDS = {
    "N": [(1, "1"), (3, "2-3"), (6, "4-6"), (12, "7-12"), (24, "13-24"), (10**9, "25+")],
    "R": [(1, "1"), (2, "2"), (10**9, "3+")],
    "H": [(1, "1"), (3, "2-3"), (10**9, "4+")],
    "P": [(1, "1"), (10**9, "2+")],
}


def _band(letter: str, n: int) -> str:
    return next(lbl for hi, lbl in BANDS[letter] if n <= hi)


def shape(dpd: str, max_runs: int = 8) -> str:
    """Run-length encoded journey with banded run lengths, last `max_runs` runs."""
    _, _, c = encode(dpd)
    if len(c) == 0:
        return "(one month only)"
    runs, prev, n = [], None, 0
    for code in c:
        if code == prev:
            n += 1
        else:
            if prev is not None:
                runs.append(f"{LETTERS[prev]}{_band(LETTERS[prev], n)}")
            prev, n = code, 1
    runs.append(f"{LETTERS[prev]}{_band(LETTERS[prev], n)}")
    prefix = "… " if len(runs) > max_runs else ""
    return prefix + " ".join(runs[-max_runs:])


def shape_table(df: pd.DataFrame, label: str = "true_archetype", top: int = 30) -> pd.DataFrame:
    s = df.dpd_string.map(shape)
    g = (pd.DataFrame({"shape": s, "label": df[label]})
         .groupby("shape").label.agg(n="size",
                                     top_label=lambda x: x.value_counts().index[0],
                                     purity=lambda x: x.value_counts(normalize=True).iloc[0]))
    g = g.sort_values("n", ascending=False)
    g["share"] = g.n / len(df)
    g["cum_share"] = g.share.cumsum()
    return g.head(top).reset_index()


def ngram_table(df: pd.DataFrame, n: int = 3, min_support: float = 0.01,
                label: str | None = None, top: int = 20, seed: int = 7) -> pd.DataFrame:
    """Share of accounts containing each code n-gram (pure-normal grams skipped), and
    lift = that share / the share when each account's own codes are shuffled. Lift > 1
    means the ORDER matters (a real motif), not just that the codes are common.
    `label` (optional) adds the dominant label among accounts containing the gram —
    on real data pass the discovered clusters or states, not a planted truth."""
    rng = np.random.default_rng(seed)
    obs, shuf = [], []
    for s in df.dpd_string:
        c = encode(s)[2]
        cs = rng.permutation(c)
        for store, seq in ((obs, c), (shuf, cs)):
            grams = {tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)}
            store.append({g for g in grams if any(x != N for x in g)})
    sup_obs = Counter(g for gs in obs for g in gs)
    sup_shuf = Counter(g for gs in shuf for g in gs)
    rows = []
    for g, cnt in sup_obs.items():
        sup = cnt / len(df)
        if sup < min_support:
            continue
        row = {"gram": "".join(LETTERS[x] for x in g), "support": sup,
               "lift": sup / max(sup_shuf.get(g, 0), 1) * len(df)}
        if label is not None:
            mask = np.array([g in gs for gs in obs])
            mix = df.loc[mask, label].value_counts(normalize=True)
            row.update({"top_label": mix.index[0], "purity": mix.iloc[0]})
        rows.append(row)
    return pd.DataFrame(rows).sort_values("lift", ascending=False).head(top)


# Clock-safe only: lifetime, run-up (fixed once past 4), and recent rates within the spell.
CLUSTER_FEATURES = [
    "months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
    "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
    "max_hold_run", "post4_paid_rate", "rec_paid_rate", "last6_in_band", "chg_6m",
]
LOG_FEATURES = {"months_before_spell", "clean_gap_before_current", "runup_len", "max_hold_run"}


def cluster_matrix(f: pd.DataFrame) -> np.ndarray:
    X = f[CLUSTER_FEATURES].astype(float).copy()
    for col in LOG_FEATURES:
        X[col] = np.log1p(X[col])
    return StandardScaler().fit_transform(X)


def kmeans_scan(f: pd.DataFrame, ks=range(4, 11), label: str = "true_archetype",
                seed: int = 7) -> tuple[pd.DataFrame, dict]:
    X = cluster_matrix(f)
    rng = np.random.default_rng(seed)
    sample = rng.choice(len(X), size=min(4000, len(X)), replace=False)
    rows, fits = [], {}
    for k in ks:
        km = KMeans(n_clusters=k, n_init=10, random_state=seed).fit(X)
        fits[k] = km.labels_
        rows.append({"k": k,
                     "silhouette": silhouette_score(X[sample], km.labels_[sample]),
                     "ARI_vs_truth": adjusted_rand_score(f[label], km.labels_)})
    return pd.DataFrame(rows), fits


def cluster_profile(f: pd.DataFrame, labels: np.ndarray, label: str = "true_archetype") -> pd.DataFrame:
    g = f.assign(cluster=labels).groupby("cluster")
    prof = g[CLUSTER_FEATURES].median().round(2)
    prof.insert(0, "share", (g.size() / len(f)).round(3))
    mix = g[label].agg(top_label=lambda x: x.value_counts().index[0],
                       purity=lambda x: round(x.value_counts(normalize=True).iloc[0], 2))
    return mix.join(prof).sort_values("share", ascending=False)


def rule_tree(f: pd.DataFrame, target: pd.Series, max_leaves: int = 8,
              min_leaf: float = 0.02, seed: int = 7) -> tuple[DecisionTreeClassifier, str]:
    X = f[CLUSTER_FEATURES]
    tree = DecisionTreeClassifier(max_leaf_nodes=max_leaves, min_samples_leaf=min_leaf,
                                  random_state=seed).fit(X, target)
    return tree, export_text(tree, feature_names=CLUSTER_FEATURES, decimals=2)
`````

### FILE: `dpd_states/synth.py`
sha256 `0ede551aed03d51a1dd0857c503b31305f717f7ba5859f83877a0b1edaffe410` · 324 lines · trailing newline: yes

`````python
"""Synthetic DPD bucket histories for the bucket 4–7 spine.

Each account gets a full LIFECYCLE: from opening, through the run-up, until it exits
at bucket 8. A snapshot is then taken the way a real one is: an account is in the
spine with probability proportional to the months it spends in buckets 4–7 (so long
holders are over-represented), and its history is cut at a random one of those months.
Because the future is simulated too, monthly roll rates can be measured on the spine
and calibrated to the bank's observed rates (ROLL_TARGET), and 6-month outcomes kept.

Real-data effects layered on top: payment holidays (bucket frozen, nothing paid) and
billing-cycle artefacts (+2 jump next to a fake hold: 3 3 5 or 3 5 5 for 3 4 5).

Strings are emitted with the CURRENT bucket leftmost (bank convention). 0 ≡ 1.
Archetype weights are shares of the INFLOW into bucket 4, not of the spine.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SPINE = (4, 5, 6, 7)
EXIT = 8
ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}   # observed monthly roll rates

P_ONE = 0.05                # chance a normal month shows as bucket 1 instead of 0
P_BLIPPY = 0.30             # share of clean stretches that carry one-month blips to 2
BLIP_RATE = (0.02, 0.10)    # per-month blip probability for a blippy stretch
P_CURE_FROM_4PLUS = 0.05    # full cures to 0 from bucket 4+ are rare
P_HOLIDAY = 0.015           # lifecycles with a payment holiday (bucket frozen 3–6 months)
P_CYCLE_JUMP = 0.01         # per straight-roll triple: reported as 3 3 5 or 3 5 5

# Post-4 monthly roll probability for the "keeps rolling" archetypes. Calibrated by
# calibrate() so that spine-level roll rates match ROLL_TARGET.
Q_ROLL = {4: 0.95, 5: 0.95, 6: 0.95, 7: 0.97}
P_PAY2_POST4 = 0.10         # of non-roll months after 4, share paying 2 months (back 1)


def _merged(x: int) -> int:
    return max(x, 1)


def _tenure(rng, lo: int = 1) -> int:
    """Clean months before the first real spell: one skewed distribution for the whole
    book (median ~4y), so tenure is continuous across patterns — no planted gaps."""
    return int(np.clip(rng.gamma(2.0, 28.0), lo, 180))


def _normal(rng, n: int) -> list[int]:
    """Clean months; some stretches carry one-month blips (0 0 2 0 0)."""
    rate = rng.uniform(*BLIP_RATE) if rng.random() < P_BLIPPY else 0.0
    out = []
    while len(out) < n:
        if rate and len(out) > 0 and out[-1] <= 1 and rng.random() < rate and len(out) < n - 1:
            out += [2, 0]
        else:
            out.append(1 if rng.random() < P_ONE else 0)
    return out[:n]


def _roll_to(path: list[int], target: int) -> None:
    """Straight roll: one bucket per month (paid nothing) until `target`."""
    while _merged(path[-1]) < target:
        path.append(_merged(path[-1]) + 1)


def _post4(path: list[int], rng) -> None:
    """After reaching 4: roll with Q_ROLL, otherwise pay one month (hold) or,
    rarely, two months (back one bucket) — until exit at 8."""
    while path[-1] < EXIT:
        b = path[-1]
        if rng.random() < Q_ROLL.get(b, 1.0):
            path.append(b + 1)
        elif rng.random() < P_PAY2_POST4:
            path.append(b - 1)
        else:
            path.append(b)


def _cure(path: list[int], rng) -> None:
    """Pay back to normal, in one go or in two steps."""
    b = _merged(path[-1])
    if b > 2 and rng.random() < 0.4:
        path.append(b - 1)
    path.append(0)


# --- archetypes: each returns a full lifecycle ending at EXIT ----------------

def bust_out(rng) -> list[int]:
    """0 0 2 3 4 5 or 0 2 0 2 3 4 — at most 3 months of history before rolling in, at most
    one blip (a payoff from 2, never higher) inside it, then gone."""
    if rng.random() < 0.3:
        path = [0, 2, 0]                          # one-shot payoff, only ever from 2
    else:
        path = [0] * int(rng.integers(1, 4))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def clean_abrupt_shock(rng) -> list[int]:
    """0 0 0 … 0 2 3 4 5 6 7 — clean, then a straight roll. Tenure from the book-wide
    distribution, so some are short and genuinely hard to tell from a bust-out."""
    path = _normal(rng, _tenure(rng, lo=3))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def slow_slide(rng) -> list[int]:
    """0 0 0 0 2 2 3 3 4 5 6 — monotonic but slower than one bucket a month: pays one
    month's due now and then (stays in the same bucket), at least once on the way to 4.
    Never pays 2+ months, so never goes back. After 4 rolls like the rest."""
    path = _normal(rng, _tenure(rng, lo=6))
    steps = [2, 3]
    must_hold = int(rng.choice(steps))
    for level in steps:
        path.append(level)
        if level == must_hold or rng.random() < 0.3:
            path.append(level)
    path.append(4)
    _post4(path, rng)
    return path


def repeat_episodes(rng) -> list[int]:
    """Earlier episodes cured to normal, e.g. 0 0 2 2 3 3 2 0 2 3 4 5 (gap can be 1 month).
    Tenure can be very short: 0 2 3 4 0 0 2 3 4 5 6 is a repeat, not a bust-out."""
    path = _normal(rng, _tenure(rng, lo=1) if rng.random() < 0.8 else int(rng.integers(1, 6)))
    for _ in range(int(rng.integers(1, 4))):
        peak = 4 if rng.random() < P_CURE_FROM_4PLUS else int(rng.integers(2, 4))
        path.append(2)
        while path[-1] < peak:                    # may hold on the way up
            path += [path[-1]] * int(rng.integers(0, 2)) + [path[-1] + 1]
        path += [path[-1]] * int(rng.integers(0, 3))
        _cure(path, rng)
        path += _normal(rng, int(rng.integers(1, 18)))
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def volatile(rng) -> list[int]:
    """0 0 2 3 2 3 4 2 3 4 5 6 — rolls, pays 2+ months, rolls again, repeatedly (mostly below 4)."""
    path = _normal(rng, _tenure(rng, lo=6))
    path.append(2)
    for _ in range(int(rng.integers(10, 20))):
        b, u = path[-1], rng.random()
        if (u < 0.5 or b == 2) and b < 4:          # oscillates below 4; no stall at 2
            path.append(b + 1)
        elif u < 0.8 and b > 2:
            floor = 1 if (b <= 3 or rng.random() < P_CURE_FROM_4PLUS) else 2
            path.append(max(b - int(rng.integers(1, 3)), floor))
        elif b == 4:
            break
        else:
            path.append(b)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def dip_and_roll(rng) -> list[int]:
    """0 0 2 3 4 3 4 5 6 — rolls, pays two months once (back one bucket), keeps rolling."""
    path = _normal(rng, _tenure(rng, lo=6))
    peak = int(rng.integers(3, 5))
    _roll_to(path, peak)
    path.append(peak - 1)
    if rng.random() < 0.3:
        path.append(peak - 1)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def staircase(rng) -> list[int]:
    """0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5 — holds several months per level, then steps up."""
    path = _normal(rng, _tenure(rng, lo=6))
    for level in range(2, EXIT):
        path += [level] * (int(rng.integers(2, 8)) if level <= 5 else int(rng.integers(1, 3)))
    path.append(EXIT)
    return path


def stabilized(rng) -> list[int]:
    """0 0 … 2 3 4 5 5 5 4 5 5 5 6 5 5 … — reaches a level and keeps paying around one
    month's due for a long time (±1 bucket), eventually breaks and rolls out."""
    path = _normal(rng, _tenure(rng, lo=6))
    _roll_to(path, int(rng.choice([4, 5, 6], p=[0.6, 0.3, 0.1])))
    for _ in range(int(rng.integers(6, 36))):
        b, u = path[-1], rng.random()
        if u < 0.75:
            path.append(b)
        elif u < 0.87 and b < 6:
            path.append(b + 1)
        elif b > 3:
            path.append(b - 1)
        else:
            path.append(b)
    _roll_to(path, 4)
    _post4(path, rng)
    return path


def oscillating_payer(rng) -> list[int]:
    """0 0 … 2 3 4 4 4 3 3 4 5 4 3 3 4 5 6 5 5 4 — reaches 4, then swings between 3 and 6
    for a year or more: misses a few months, catches up 2 months at once, misses again.
    Pays roughly what is due on average, just unevenly. Uncommon (the bank's edge cases)."""
    path = _normal(rng, _tenure(rng, lo=6))
    _roll_to(path, 4)
    for _ in range(int(rng.integers(10, 30))):
        b, u = path[-1], rng.random()
        if u < 0.40 and b < 6:
            path.append(b + 1)                    # missed a month
        elif u < 0.70 and b > 3:
            path.append(b - 1)                    # caught up two months
        else:
            path.append(b)                        # paid one month
    _roll_to(path, 4)
    _post4(path, rng)
    return path


# Inflow weights tuned so the spine shows bust-out ~6% and stabilized ~6% (the bank's
# actual shares under its own rules) while roll rates still hit ROLL_TARGET.
ARCHETYPES = {                      # name: (share of INFLOW into bucket 4, generator)
    "bust_out": (0.055, bust_out),
    "stabilized": (0.006, stabilized),
    "clean_abrupt_shock": (0.42, clean_abrupt_shock),
    "slow_slide": (0.08, slow_slide),
    "staircase": (0.008, staircase),
    "oscillating_payer": (0.004, oscillating_payer),
    "repeat_episodes": (0.16, repeat_episodes),
    "dip_and_roll": (0.10, dip_and_roll),
    "volatile": (0.10, volatile),
}


# --- real-data effects ---------------------------------------------------------

def _payment_holiday(path: list[int], rng) -> bool:
    """Freeze the bucket for 3–6 months somewhere in the delinquent stretch (nothing paid,
    but it reads exactly like a hold)."""
    idx = [k for k, x in enumerate(path) if 2 <= x < EXIT]
    if not idx or rng.random() >= P_HOLIDAY:
        return False
    k = int(rng.choice(idx))
    path[k + 1:k + 1] = [path[k]] * int(rng.integers(3, 7))
    return True


def _cycle_jumps(path: list[int], rng) -> None:
    """Billing-cycle artefact on straight rolls: true 3 4 5 reported as 3 3 5 or 3 5 5."""
    for k in range(len(path) - 2):
        a, m, z = path[k], path[k + 1], path[k + 2]
        if a >= 2 and m == a + 1 and z == a + 2 and z <= 7 and rng.random() < P_CYCLE_JUMP:
            path[k + 1] = a if rng.random() < 0.5 else a + 2


def _snapshot_rows(n: int, rng, k_future: int = 6) -> list[dict]:
    names = list(ARCHETYPES)
    w = np.array([ARCHETYPES[k][0] for k in names])
    pool_names = rng.choice(names, size=4 * n, p=w / w.sum())
    pool, holiday = [], []
    for k in pool_names:
        p = ARCHETYPES[k][1](rng)
        holiday.append(_payment_holiday(p, rng))
        _cycle_jumps(p, rng)
        pool.append(p)
    months = np.array([sum(1 for x in p if x in SPINE) for p in pool], dtype=float)
    chosen = rng.choice(len(pool), size=n, replace=False, p=months / months.sum())
    rows = []
    for i, j in enumerate(chosen):
        path = pool[j]
        first4 = next(k for k, x in enumerate(path) if x >= 4)
        t = int(rng.choice([k for k, x in enumerate(path) if x in SPINE]))
        fut = path[t + 1:t + 7]
        ext = path[:t + k_future + 1]
        while len(ext) < t + k_future + 1:          # after exit the bucket keeps climbing
            ext.append(min(ext[-1] + 1, 9))
        exit_at = next((k for k, x in enumerate(fut) if x >= EXIT), None)
        rows.append({
            "account_id": f"A{i:06d}",
            "dpd_string": "".join(str(x) for x in reversed(path[:t + 1])),
            "true_archetype": pool_names[j],
            "had_holiday": holiday[j],
            # future — validation only, never used to assign states
            "next_bucket": path[t + 1],
            "next_string": "".join(str(x) for x in reversed(path[:t + 2])),
            "exit_6m": exit_at is not None,
            "bucket_6m": EXIT if exit_at is not None else fut[-1],
            "paid_after_4_so_far": bool((np.diff(path[first4:t + 1]) < 1).any()),
            "latest_string": "".join(str(x) for x in reversed(ext)),   # k_future months later
        })
    return rows


def generate(n: int = 20_000, seed: int = 7) -> pd.DataFrame:
    return pd.DataFrame(_snapshot_rows(n, np.random.default_rng(seed)))


def latest_month_strings(n: int = 20_000, k: int = 6, seed: int = 7) -> pd.DataFrame:
    """What the workplace table looks like for a backtest: accounts that were in the spine
    k months ago, with their DPD string as of the LATEST month (k newer digits on the left;
    after exit the bucket keeps climbing 8, 9, 9 …). Used to test analysis.py end to end."""
    df = pd.DataFrame(_snapshot_rows(n, np.random.default_rng(seed), k_future=k))
    return df[["latest_string", "true_archetype"]].rename(columns={"latest_string": "dpd_string"})


def roll_rates(df: pd.DataFrame) -> pd.Series:
    cur = df.dpd_string.str[0].astype(int)
    return (df.next_bucket >= cur + 1).groupby(cur).mean()


def calibrate(n: int = 10_000, iters: int = 8, seed: int = 11) -> pd.DataFrame:
    """Tune Q_ROLL so spine roll rates match ROLL_TARGET. Returns the iteration log."""
    log = []
    for it in range(iters):
        rr = roll_rates(generate(n, seed + it))
        log.append({"iter": it, **{f"rr_{b}": rr[b] for b in SPINE},
                    **{f"q_{b}": Q_ROLL[b] for b in SPINE}})
        for b in SPINE:
            Q_ROLL[b] = float(np.clip(Q_ROLL[b] + 1.2 * (ROLL_TARGET[b] - rr[b]), 0.3, 0.999))
    return pd.DataFrame(log)
`````

### FILE: `dpd_states/run_synthetic.py`
sha256 `32d211485caea1fc12020b206e9d60c196a15d05f56de607ab139c0a80799be8` · 250 lines · trailing newline: yes

`````python
"""METHOD validation on synthetic data: generate a calibrated synthetic spine with planted
patterns, assign the states, and write the evidence report to ../validation/.

    python docs/deterioration_states/run.py synthetic [n_accounts]      # from any folder
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score, silhouette_score
from sklearn.preprocessing import StandardScaler

from . import discover as dv
from . import synth
from .features import build_features, encode, _runs
from .states import DEFAULTS, OPTIONS, RECOMMENDED, assign_states, state_scorecard

OUT = Path(__file__).resolve().parents[1] / "validation"   # docs/deterioration_states/validation


def md(df: pd.DataFrame, index: bool = False, floatfmt: str = "{:.2f}") -> str:
    if index:
        df = df.reset_index()
    cells = [[floatfmt.format(v) if isinstance(v, (float, np.floating)) else str(v) for v in row]
             for row in df.itertuples(index=False)]
    head = "| " + " | ".join(map(str, df.columns)) + " |"
    sep = "|" + "---|" * len(df.columns)
    return "\n".join([head, sep] + ["| " + " | ".join(r) + " |" for r in cells])


def _spells(s: str, from_bucket: int) -> int:
    b = encode(s)[0]
    return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)


def realism(f: pd.DataFrame, st: pd.Series) -> str:
    rr = synth.roll_rates(f)
    one3 = (f.dpd_string.map(lambda s: _spells(s, 3)) == 1).mean()
    one4 = (f.dpd_string.map(lambda s: _spells(s, 4)) == 1).mean()
    bust = (st == "early_payment_default").mean()
    stab = ((f.last6_in_band >= 5) & (st != "early_payment_default")).mean()
    stab_clause = (st == "stabilized").mean()
    rows = [(f"Monthly roll rate at {b}", f"{synth.ROLL_TARGET[b]:.0%}", f"{rr[b]:.0%}") for b in synth.SPINE]
    rows += [
        ("One spell only (spell from bucket 3)", "~85%", f"{one3:.0%}"),
        ("One spell only (spell from bucket 4)", "~85%", f"{one4:.0%}"),
        ("EPD ('bust-out') share", "6%", f"{bust:.1%}"),
        ("Stabilized share (your 5/6 rule, after EPD)", "6%", f"{stab:.1%}"),
        ("Stabilized share incl. long-run clause", "—", f"{stab_clause:.1%}"),
        ("Never paid since reaching 4", "majority (90% 'overkill')", f"{1 - f.paid_after_4_so_far.mean():.0%}"),
    ]
    t = pd.DataFrame(rows, columns=["check", "your book", "synthetic"])
    mix = f.b_now.value_counts(normalize=True).sort_index().rename("share").to_frame()
    ten = pd.cut(f.months_before_spell, [-1, 3, 6, 12, 24, 36, 60, 120, 999],
                 labels=["0-3", "4-6", "7-12", "13-24", "25-36", "37-60", "61-120", "121+"])
    ten = ten.value_counts(normalize=True).sort_index().rename("share").to_frame()
    dq = pd.DataFrame([
        ("accounts with a payment holiday in history", f"{f.had_holiday.mean():.1%}"),
        ("accounts with a +2 jump repaired (next to a hold)", f"{(f.n_jumps_repaired > 0).mean():.1%}"),
        ("accounts with a +2 jump left (read as roll)", f"{(f.n_jumps_left > 0).mean():.1%}"),
    ], columns=["data-quality effect", "share"])
    return ("## A. Is the synthetic spine life-like?\n\n" + md(t)
            + "\n\nCurrent bucket mix:\n\n" + md(mix, index=True, floatfmt="{:.0%}")
            + "\n\nMonths of history before the current spell (continuous — no planted gaps):\n\n"
            + md(ten, index=True, floatfmt="{:.0%}") + "\n\n" + md(dq))


def sweep(f: pd.DataFrame, nx: pd.DataFrame) -> str:
    out = ["## D. Threshold sweeps (one parameter at a time, others at default)"]
    planted = f.true_archetype

    rows = []
    for v in (2, 3, 4, 6, 9, 12):
        s = assign_states(f, epd_max_history=v)
        b = s == "early_payment_default"
        rows.append({"epd_max_history": v, "epd_share": b.mean(), "exit_6m": f.exit_6m[b].mean(),
                     "planted_bustouts_caught": b[planted == "bust_out"].mean(),
                     "share_of_state_planted_bustout": (planted[b] == "bust_out").mean()})
    out.append("### Q1 early payment default (EPD) — months of history before the spell\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for band in (4, 5, 6):
        s = assign_states(f, stabilized_min_in_band=band)
        h = s == "stabilized"
        s2 = assign_states(nx, stabilized_min_in_band=band)
        held = h.loc[nx.index]
        rows.append({"min_in_band (of 6)": band, "stabilized_share": h.mean(),
                     "roll_next_month": (f.next_bucket[h] >= f.b_now[h] + 1).mean(),
                     "exit_6m": f.exit_6m[h].mean(),
                     "still_stabilized_next_month": (s2[held[held].index] == "stabilized").mean(),
                     "payment_holiday_share": f.had_holiday[h].mean(),
                     "planted_stabilizers_caught": h[planted == "stabilized"].mean()})
    out.append("### Q2 stabilized — months within today's bucket ±1 (of the last 6)\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (0.34, 0.5, 0.67):
        kw = {**OPTIONS["C_detailed_7"], "paying_since_4_min_rate": v}
        s, s2 = assign_states(f, **kw), assign_states(nx, **kw)
        m = s == "paying_since_4"
        mm = m.loc[nx.index]
        others = ~s.isin(["stabilized", "paying_since_4"])
        rows.append({"paying_since_4_min_rate": v, "share": m.mean(),
                     "roll_next_month": (f.next_bucket[m] >= f.b_now[m] + 1).mean(),
                     "still_paying_since_4_next_month": (s2[mm[mm].index] == "paying_since_4").mean(),
                     "paid_in_last_3m": f.paid_any_3m[m].mean(),
                     "stability_of_other_states": (s.loc[nx.index][others.loc[nx.index]]
                                                   == s2[others.loc[nx.index]]).mean()})
    out.append("### Q3 paying since 4 (tested, not recommended) — months paid per month since 4\n\n"
               + md(pd.DataFrame(rows)))

    rows = []
    for v in (2, 3, 4):
        s = assign_states(f, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v})
        rows.append({"earlier spell reached bucket": v, "repeat_share": (s == "repeat_delinquent").mean()})
    out.append("### Q4 repeat delinquent — how deep the earlier spell must have gone\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (3, 4, 5):
        s = assign_states(f, straight_max_runup=v)
        g = s == "slow_roller"
        rows.append({"straight_max_runup": v, "straight_share": (s == "straight_roller").mean(),
                     "slow_share": g.mean(),
                     "slow_slides_in_slow_roller": g[planted == "slow_slide"].mean(),
                     "abrupt_in_straight": (s[planted == "clean_abrupt_shock"] == "straight_roller").mean()})
    out.append("### Q5 straight vs slow roller — max run-up months\n\n" + md(pd.DataFrame(rows)))

    rows = []
    for v in (12, 18, 24, 36):
        s = assign_states(f, **{**OPTIONS[RECOMMENDED], "seasoned_min_months": v})
        rows.append({"seasoned_min_months": v, "seasoned": (s == "straight_roller_seasoned").mean(),
                     "early_life": (s == "straight_roller_early_life").mean()})
    out.append("### Q5 split — months of history before the spell (seasoned vs early-life straight roller)\n\n"
               + md(pd.DataFrame(rows)))
    return "\n\n".join(out)


RESIDUAL_FEATURES = ["months_before_spell", "n_blips", "n_prior_episodes", "max_prior_bucket",
                     "clean_gap_before_current", "runup_len", "runup_holds", "runup_pays",
                     "post4_paid_rate", "rec_paid_rate"]


def residual_clusters(f: pd.DataFrame, options: dict[str, pd.Series]) -> str:
    """Cluster only what is left after EPD and stabilized, and see which option's
    residual states the natural groups agree with."""
    base = assign_states(f)
    res = ~base.isin(["early_payment_default", "stabilized"])
    r = f[res]
    X = r[RESIDUAL_FEATURES].astype(float).copy()
    for c in ("months_before_spell", "clean_gap_before_current", "runup_len"):
        X[c] = np.log1p(X[c])
    X = StandardScaler().fit_transform(X)
    smp = np.random.default_rng(7).choice(len(X), size=min(4000, len(X)), replace=False)
    rows, fits = [], {}
    for k in range(2, 9):
        lab = KMeans(k, n_init=10, random_state=7).fit_predict(X)
        boot = KMeans(k, n_init=10, random_state=3).fit(X[np.random.default_rng(3).choice(len(X), len(X))]).predict(X)
        fits[k] = lab
        rows.append({"k": k, "silhouette": silhouette_score(X[smp], lab[smp]),
                     "bootstrap_ARI": adjusted_rand_score(lab, boot),
                     **{f"agree_{o}": adjusted_rand_score(lab, s[res]) for o, s in options.items()}})
    g = r.assign(c=fits[6]).groupby("c")
    prof = pd.DataFrame({
        "share_of_spine": g.size() / len(f),
        "median_months_before_spell": g.months_before_spell.median(),
        "earlier_spell_to_3+": g.max_prior_bucket.apply(lambda x: (x >= 3).mean()),
        "straight_runup": g.runup_len.apply(lambda x: (x <= 3).mean()),
        "held_on_way": g.runup_holds.apply(lambda x: (x > 0).mean()),
        "paid_2+_on_way": g.runup_pays.apply(lambda x: (x > 0).mean()),
        "median_paid_rate_since_4": g.post4_paid_rate.median(),
        "top_state_option_C": g.apply(lambda x: options["C_detailed_7"][x.index].value_counts().index[0]),
    }).sort_values("share_of_spine", ascending=False)
    return ("## C. Clustering the residual (after EPD and stabilized)\n\n"
            f"Residual = {res.mean():.0%} of the spine. Agreement (ARI) between k-means clusters and each "
            "option's residual states:\n\n" + md(pd.DataFrame(rows), floatfmt="{:.2f}")
            + "\n\nk = 6 cluster profiles:\n\n" + md(prof, index=True))


def discovery(f: pd.DataFrame) -> str:
    out = [f"## E. Discovery views (states = {RECOMMENDED})"]
    st = dv.shape_table(f, label="state", top=15)
    out.append(f"### Top 15 shapes ({f.dpd_string.map(dv.shape).nunique()} distinct) — by state\n\n" + md(st))
    ng = dv.ngram_table(f, n=4, label="state")
    out.append("### 4-grams ranked by lift vs shuffled order (support ≥ 1%)\n\n" + md(ng))
    X = dv.cluster_matrix(f)
    sample = np.random.default_rng(7).choice(len(X), size=min(4000, len(X)), replace=False)
    rows = []
    for k in (4, 5, 6, 7, 8):
        lab = KMeans(k, n_init=10, random_state=7).fit_predict(X)
        boots = [KMeans(k, n_init=5, random_state=s).fit(X[np.random.default_rng(s).choice(len(X), len(X))]).predict(X)
                 for s in (1, 2)]
        rows.append({"k": k, "silhouette": silhouette_score(X[sample], lab[sample]),
                     "bootstrap_ARI": adjusted_rand_score(*boots),
                     "ARI_vs_planted": adjusted_rand_score(f.true_archetype, lab),
                     "ARI_vs_states": adjusted_rand_score(f.state, lab)})
    out.append("### k-means on clock-safe features\n\n" + md(pd.DataFrame(rows), floatfmt="{:.3f}"))
    return "\n\n".join(out)


def main(n: int = 20_000) -> Path:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    synth.calibrate()
    df = synth.generate(n)
    f = build_features(df)
    nx_in = df[df.next_bucket.between(4, 7)][["next_string"]].rename(columns={"next_string": "dpd_string"})
    nx = build_features(nx_in)
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}
    opts_next = {o: assign_states(nx, **kw) for o, kw in OPTIONS.items()}
    f["state"] = opts[RECOMMENDED]
    sec = [realism(f, opts["A_minimal_4"])]

    # B. the three options
    parts = ["## B. State options — each a MECE tree (first 'yes' wins)\n\n"
             f"Shared thresholds: `{DEFAULTS}`"]
    for o, kw in OPTIONS.items():
        s = opts[o]
        assert s.notna().all()
        card = state_scorecard(f, s, opts_next[o])
        parts.append(f"### {o} — {s.nunique()} states (extra switches: `{kw}`)\n\n" + md(card, index=True))
    c = opts["C_detailed_7"]
    parts.append("Option C — state mix by current bucket:\n\n"
                 + md(pd.crosstab(c, f.b_now, normalize="columns"), index=True)
                 + "\n\nOption C — planted pattern → state (row share):\n\n"
                 + md(pd.crosstab(f.true_archetype, c, normalize="index"), index=True))
    ex = (f.assign(state_c=c).groupby("state_c").sample(3, random_state=1)[["state_c", "dpd_string"]]
          .assign(oldest_to_newest=lambda x: x.dpd_string.str[::-1].str[-30:]))
    parts.append("Option C — examples (last 30 months, oldest → newest):\n\n" + md(ex[["state_c", "oldest_to_newest"]]))
    sec.append("\n\n".join(parts))

    sec.append(residual_clusters(f, opts))
    sec.append(sweep(f, nx))

    sec.append(discovery(f))

    report = (f"# DPD deterioration states — synthetic validation {ts}\n\n"
              f"{n:,} calibrated synthetic spine accounts (current bucket 4–7). "
              "Strings: leftmost = current bucket. 0 ≡ 1.\n\n" + "\n\n".join(sec) + "\n")
    OUT.mkdir(exist_ok=True)
    path = OUT / f"dpd_states_validation_{ts}.md"
    path.write_text(report)
    print(path)
    return path


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000)
`````

### FILE: `dpd_states/selftest.py`
sha256 `e1fc37dfc16fa14e01764e022a347cda7a3be8016d32d96f3923aaafb3744272` · 178 lines · trailing newline: yes

`````python
"""End-to-end self-test of the REAL-DATA path on synthetic data (no Spark needed).

Builds the two frames the Spark snippet would collect — today's spine with optional
axis columns, and latest-month strings for the backtest — runs analysis.run and the
expectations, and writes the same report the workplace run produces.

    python docs/deterioration_states/run.py selftest [n_accounts]       # from any folder

Pass = no FAIL and E01 (MECE) PASS. WARNs are reported, not asserted: synthetic data is
calibrated to the bank's figures but is not the bank's book.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path
from types import SimpleNamespace

import numpy as np

from . import config, synth
from .analysis import md, run
from .expectations import evaluate
from .features import build_features
from .states import OPTIONS, RECOMMENDED, assign_states

OUT = Path(__file__).resolve().parents[1] / "validation"

# Edge cases discussed with the business owner, written OLDEST -> NEWEST (the last digit is
# today's bucket), with the option-B state they must get. Any rule change that moves one
# of these fails the self-test.
CASES = [
    ("0 2 0 2 3 4", "early_payment_default", "3 months incl. one blip, then straight roll"),
    ("0 0 0 2 3 4", "early_payment_default", "3 clean months, straight roll"),
    ("0 2 3 4 5", "early_payment_default", "1 clean month"),
    ("0 0 2 0 2 3 4", "straight_roller_early_life", "4 months of history: too long for EPD"),
    ("0 0 0 0 0 0 2 3 4", "straight_roller_early_life", "6 clean months: early-life default, not EPD"),
    ("0 2 0 2 0 2 3 4", "straight_roller_early_life", "two blips: not EPD"),
    ("0 2 3 4 0 0 2 3 4 5 6", "repeat_delinquent", "paid off from 4, then relapsed"),
    ("0 0 2 2 3 4", "slow_roller", "held once on the way down"),
    ("0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5", "stabilized", "staircase holding at 4 then one step"),
    ("000000000000002345", "straight_roller_seasoned", "14 clean months, straight roll"),
    ("0000000000000234444567", "straight_roller_seasoned", "held at 4, then rolled 3 buckets: not stable"),
    ("0000000000000023455555", "stabilized", "holding at 5"),
    ("00000000234443345433456554", "stabilized", "oscillating payer (example 1)"),
    ("00000000234443345433456654", "stabilized", "oscillating payer that just paid down 6-5-4 (example 2)"),
    ("0 0 2 3 4 4 4 4 4 4", "stabilized", "entered like EPD but pays the monthly due since: not EPD"),
    ("0 0 2 3 4 4 5 6", "straight_roller_early_life", "entered like EPD, paid once at 4: EPD needs no payment"),
    ("4 5 6 7", "history_starts_delinquent", "string starts delinquent (restructured / missing history)"),
    ("0000000000000000224", "straight_roller_seasoned", "+2 jump after a hold at 2: repaired to 2 3 4"),
    ("00000000000000002244", "straight_roller_seasoned", "same account a month later: fixed state must not change"),
    ("000034", "straight_roller_early_life", "jump from clean to 3: no clean month is borrowed"),
    ("0 2 3 4" + " 0" * 30 + " 2 3 4", "straight_roller_seasoned", "cured 30 months earlier: outside 24-month window"),
    ("0 2 3 4" + " 0" * 20 + " 2 3 4 5", "repeat_delinquent", "cured 20 months earlier: repeat delinquent"),
    ("0000000000000000 2 3 4 4 0 4 5", "stabilized", "single 0 inside a spell at 4 is a glitch, not a cure"),
    ("0000 3 0000000000000 2 3 4", "straight_roller_seasoned", "single spike 0 3 0 is a glitch, not an earlier spell"),
]


CROP_CASES = [   # (oldest -> newest, max months kept, expected option-B state, why)
    ("0" * 10 + "234" + "45" * 18 + "4", 32, "stabilized",
     "spell older than the window: not a data-quality case; long-run holder -> stabilized"),
    ("0" * 40 + "234", 32, "straight_roller_seasoned", "long clean history cropped: still seasoned"),
    ("0000000000234", 6, "straight_roller_early_life", "cropped to 0 0 0 2 3 4: looks like EPD but is not new"),
    ("0 0 0 2 3 4", 32, "early_payment_default", "short history, not cropped: EPD"),
]


def check_crop() -> tuple[list[str], int]:
    import pandas as pd
    from .analysis import crop_history
    lines, bad = [], 0
    for chron, n, want, why in CROP_CASES:
        s, tr = crop_history(pd.Series([chron.replace(" ", "")[::-1]]), n)
        f = build_features(pd.DataFrame({"dpd_string": s, "history_truncated": tr}))
        got = assign_states(f, **OPTIONS[RECOMMENDED]).iloc[0]
        bad += got != want
        lines.append(f"{'OK  ' if got == want else 'FAIL'} keep {n:>2}: {chron[-24:]:<25} -> {got:<27} {why}")
    return lines, bad


def check_file_mode() -> bool:
    """File mode end to end on a temporary CSV (no openpyxl needed): reading the text column,
    filtering to today's spine, survivor-only checks, results written outside the repo."""
    import contextlib
    import io
    import tempfile
    from . import config, file_mode
    df = synth.generate(1500, seed=21)[["dpd_string"]].rename(columns={"dpd_string": config.COL_DPD})
    df.loc[df.index[:100], config.COL_DPD] = "3" + df[config.COL_DPD][:100].str[1:]   # outside the spine
    df["derived_column"] = 1
    with tempfile.TemporaryDirectory() as tmp:
        src = Path(tmp) / "mock.csv"
        df.to_csv(src, index=False)
        with contextlib.redirect_stdout(io.StringIO()):
            payload = file_mode.main(str(src), out_dir=tmp)
    good = (payload["counts"]["current_spine"] == 1400
            and payload["results"]["states_today"][RECOMMENDED]["mece"]
            and isinstance(payload["results"].get("survivor_checks"), dict))
    print(f"\nFile mode on a temporary CSV: {'OK' if good else 'FAIL'} "
          f"(spine {payload['counts']['current_spine']} of {payload['counts']['rows']} rows)")
    return good


def check_cases() -> list[str]:
    import pandas as pd
    df = pd.DataFrame({"dpd_string": [c.replace(" ", "")[::-1] for c, _, _ in CASES]})
    got = assign_states(build_features(df), **OPTIONS[RECOMMENDED])
    lines, bad = [], 0
    for (c, want, why), g in zip(CASES, got):
        ok = g == want
        bad += not ok
        lines.append(f"{'OK  ' if ok else 'FAIL'} {c[:36]:<37} -> {g:<27} {'' if ok else '(expected ' + want + ') '}{why}")
    return lines, bad


def _fake_axes(cur, rng):
    """Plausible other-axis columns so the overlap code paths run. Not real behaviour."""
    f = build_features(cur)
    st = assign_states(f, **OPTIONS[RECOMMENDED])
    money = np.where(f.paid_any_3m, 2, rng.choice([0, 1], len(f), p=[0.8, 0.2]))
    clean = (f.n_prior_episodes == 0).astype(int)
    ptp = rng.choice([0, 1, 2], len(f), p=[0.5, 0.3, 0.2])
    out = cur.copy()
    out["cred_money_in_points"] = money
    out["cred_clean_point"] = clean
    out["cred_ptp_points"] = ptp
    out["credibility_score"] = money + clean + ptp
    out["ability_score"] = rng.normal(50, 15, len(f)).round(1)
    out["reachable_flag"] = rng.choice([0, 1], len(f), p=[0.3, 0.7])
    out["in_country_flag"] = rng.choice([0, 1], len(f), p=[0.15, 0.85])
    # the bank's own rules: ours, with a little disagreement
    out["existing_bust_out"] = ((st == "early_payment_default") ^ (rng.random(len(f)) < 0.005)).astype(int)
    out["existing_stabilized"] = ((f.last6_in_band >= 5) ^ (rng.random(len(f)) < 0.005)).astype(int)
    return out


def main(n: int = 20_000) -> int:
    rng = np.random.default_rng(3)
    synth.calibrate()
    cur = synth.generate(n)[["dpd_string"]]
    cur = _fake_axes(cur, rng)
    # a few strings with a non-digit code and padding, to exercise CHAR_MAP / STRIP_CHARS
    cur.loc[cur.index[:50], "dpd_string"] = " " + cur.dpd_string[:50].str.replace("0", "X", n=1)
    latest = synth.latest_month_strings(n, k=6, seed=11)[["dpd_string"]]

    cfg = SimpleNamespace(**{k: getattr(config, k) for k in dir(config) if k.isupper()})
    cfg.CHAR_MAP = {"X": "0"}
    R, report = run(cur, latest, cfg)
    checks = evaluate(R)

    OUT.mkdir(exist_ok=True)
    stamp = date.today().strftime("%Y%m%d")
    (OUT / f"selftest_results_{stamp}.json").write_text(json.dumps(R, indent=2, default=str))
    (OUT / f"selftest_report_{stamp}.md").write_text(
        f"# Self-test on synthetic data — {stamp}\n\nFake axis columns; real-data code path.\n\n"
        "## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    print(md(checks[["id", "status", "observed", "expected", "check"]], index=False))
    case_lines, bad = check_cases()
    crop_lines, bad_crop = check_crop()
    print("\nReliable-window cropping:\n" + "\n".join(crop_lines))
    bad += bad_crop
    file_ok = check_file_mode()
    print("\nEdge cases (oldest -> newest, option B):\n" + "\n".join(case_lines))
    (OUT / f"selftest_report_{stamp}.md").write_text(
        (OUT / f"selftest_report_{stamp}.md").read_text().replace(
            "## 0. Expectation checks", "## 0a. Edge cases (oldest → newest, option B)\n\n```\n"
            + "\n".join(case_lines) + "\n```\n\n## 0. Expectation checks"))
    ok = ((checks.status != "FAIL").all() and checks.set_index("id").loc["E01", "status"] == "PASS"
          and bad == 0 and file_ok)
    print("\nSELFTEST", "PASSED" if ok else "FAILED", f"-> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000))
`````

### FILE: `dpd_states/bundle.py`
sha256 `6117c212db36d252253672b11ae7a4091b4d761fbf6f591d694ef36da83a3060` · 218 lines · trailing newline: yes

``````python
"""Build BUNDLE.md: every source file of docs/deterioration_states in one markdown file,
for environments that can open .md but not .py files.

    python docs/deterioration_states/run.py bundle                      # from any folder

The bundle starts with instructions and a small extractor script. Running the extractor on
the saved BUNDLE.md recreates every file and checks each against its SHA-256, so nothing
depends on an LLM retyping code correctly.
"""
from __future__ import annotations

import hashlib
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]           # docs/deterioration_states
OUT = ROOT / "BUNDLE.md"

# Shipped files, in reading order. Evidence (validation/), outputs (results/) and the PDF
# are not code and are left out; empty folders are recreated by the extractor.
FILES = [
    "README.md",
    "run.py",
    "METHODOLOGY.md",
    "REVIEW.md",
    "PROMPTS.md",
    "dpd_states/__init__.py",
    "dpd_states/config.py",
    "dpd_states/features.py",
    "dpd_states/states.py",
    "dpd_states/analysis.py",
    "dpd_states/expectations.py",
    "dpd_states/file_mode.py",
    "dpd_states/discover.py",
    "dpd_states/synth.py",
    "dpd_states/run_synthetic.py",
    "dpd_states/selftest.py",
    "dpd_states/bundle.py",
    "snippets/dpd_states_validate.py",
]
EMPTY_DIRS = ["results", "validation"]

LANG = {".py": "python", ".md": "markdown"}

EXTRACTOR = '''"""Recreate docs/deterioration_states/ from BUNDLE.md and verify every file.

Run from the repo root, in this order:

    1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
         -> must end with "N files OK, 0 mismatched"
    2. python docs/deterioration_states/run.py selftest
         -> must end with "SELFTEST PASSED" (~1 minute; needs pandas, numpy, scikit-learn)
    3. Fill in docs/deterioration_states/dpd_states/config.py and the <<FILL-IN>> in
       snippets/dpd_states_validate.py (PROMPTS.md P1), then in a Kedro notebook:
         main(catalog, check_only=True)   # dry run
         main(catalog)                    # full validation

Optional second argument writes somewhere else: extract_bundle.py BUNDLE.md <folder>
"""
import hashlib
import pathlib
import re
import sys

src = pathlib.Path(sys.argv[1])
root = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else src.resolve().parent
lines = src.read_text(encoding="utf-8").split("\\n")
ok = bad = 0
i = 0
while i < len(lines):
    m = re.match(r"^### FILE: `([^`]+)`\\s*$", lines[i])
    if not m:
        i += 1
        continue
    rel = m.group(1)
    meta = lines[i + 1]
    sha = re.search(r"sha256 `([0-9a-f]{64})`", meta).group(1)
    trailing = "trailing newline: yes" in meta
    j = i + 2
    while not lines[j].startswith("`````"):
        j += 1
    fence = re.match(r"^(`+)", lines[j]).group(1)
    k = j + 1
    while lines[k] != fence:
        k += 1
    body = "\\n".join(lines[j + 1:k])
    if body and trailing:
        body += "\\n"
    out = root / rel
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body.encode("utf-8"))
    good = hashlib.sha256(body.encode("utf-8")).hexdigest() == sha
    ok += good
    bad += not good
    print(("OK       " if good else "MISMATCH ") + rel)
    i = k + 1
for d in re.findall(r"^- empty folder: `([^`]+)`", "\\n".join(lines), flags=re.M):
    (root / d).mkdir(parents=True, exist_ok=True)
    (root / d / ".gitkeep").touch()
print(f"\\n{ok} files OK, {bad} mismatched -> {root}")
if not bad:
    print("Next: python docs/deterioration_states/run.py selftest   (from the repo root)")
sys.exit(1 if bad else 0)
'''


def _fence(text: str) -> str:
    longest = max((len(m) for m in re.findall(r"`+", text)), default=0)
    return "`" * max(5, longest + 1)


def build() -> Path:
    parts = []
    tree = ["docs/deterioration_states/"] + [f"├── {f}" for f in FILES] + [f"├── {d}/" for d in EMPTY_DIRS]
    total = 0
    for rel in FILES:
        raw = (ROOT / rel).read_bytes()
        text = raw.decode("utf-8")
        total += text.count("\n")
        sha = hashlib.sha256(raw).hexdigest()
        trailing = "yes" if text.endswith("\n") else "no"
        body = text[:-1] if text.endswith("\n") else text
        fence = _fence(text)
        lang = LANG.get(Path(rel).suffix, "")
        parts.append(f"### FILE: `{rel}`\n"
                     f"sha256 `{sha}` · {text.count(chr(10))} lines · trailing newline: {trailing}\n\n"
                     f"{fence}{lang}\n{body}\n{fence}\n")

    doc = f"""# Deterioration states — full source bundle

## Run this (from the repo root)

```bash
# 1. recreate every file and verify checksums  -> "N files OK, 0 mismatched"
python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md

# 2. self-test on synthetic data              -> "SELFTEST PASSED"  (~1 min)
python docs/deterioration_states/run.py selftest

# 3. optional: rebuild the synthetic method-validation report
python docs/deterioration_states/run.py synthetic
```

Step 1 needs `extract_bundle.py` — create it from the **Extractor** section below the first
time. Then fill in `dpd_states/config.py` and the `<<FILL-IN>>` in
`snippets/dpd_states_validate.py` (PROMPTS.md P1) and, in a Kedro notebook:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
from dpd_states_validate import main
main(catalog, check_only=True)   # dry run: schema, counts, example strings
result = main(catalog)           # full validation -> results/ (aggregates only)
```

---

Generated {date.today().isoformat()} by `dpd_states/bundle.py`. {len(FILES)} files, {total:,} lines.
This one markdown file contains **every source file** of `docs/deterioration_states/`, for
environments where `.py` files cannot be opened. Regenerate it after any change with
`python docs/deterioration_states/run.py bundle`.

## Instructions for the assistant recreating the files (read first)

1. **Do not retype the code.** Long files retyped by hand (or by a model) pick up small
   errors. Instead:
   - save this whole file, unchanged, as `docs/deterioration_states/BUNDLE.md` in the
     workplace repository (copy the **raw** markdown — e.g. GitHub's "Copy raw file"
     button — not the rendered page, which drops the code fences);
   - create `docs/deterioration_states/extract_bundle.py` with the extractor below;
   - run `python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md`.
2. The extractor writes every file and checks its SHA-256. It must end with
   **"N files OK, 0 mismatched"**. A mismatch means the copy of this markdown was altered
   (line endings, smart quotes, a rendered instead of raw copy) — recopy the raw file;
   do not hand-fix the code.
3. Then run the self-test — from any folder, e.g. the repo root:
   `python docs/deterioration_states/run.py selftest` → must print **SELFTEST PASSED**
   (needs pandas, numpy, scikit-learn; ~1 minute). Do not use `python -m dpd_states...`
   from the repo root: the package sits inside `docs/deterioration_states/`, so Python
   will not find it there.
4. Only after that, follow `PROMPTS.md` (P0 → P1 → P2). The only files to edit are
   `dpd_states/config.py` and the marked `<<FILL-IN>>` spot in
   `snippets/dpd_states_validate.py`.
5. Fallback, only if no script can be run: create each file below verbatim from its code
   block (the text between the fence lines, nothing else), then run the extractor's
   checksum part to confirm.

## Extractor

`````python
{EXTRACTOR.rstrip()}
`````

## Folder structure

```
{chr(10).join(tree)}
```

- empty folder: `results`
- empty folder: `validation`

`results/` receives the real-data outputs; `validation/` holds the synthetic evidence
(regenerate with `python docs/deterioration_states/run.py selftest` and `... run.py synthetic`).

## Files

{chr(10).join(parts)}"""
    OUT.write_text(doc, encoding="utf-8")
    return OUT


if __name__ == "__main__":
    p = build()
    print(p, f"{p.stat().st_size / 1024:.0f} KB")
``````

### FILE: `snippets/dpd_states_validate.py`
sha256 `ed57a1f7da1efdb29e9c7fa33bd11b539b11b6d214e654357d6380508f80cbed` · 247 lines · trailing newline: yes

`````python
"""DPD deterioration states — validation on real data (PROD).

Assigns the deterioration states (options A / B / C) to today's bucket 4–7 spine,
backtests them on the spine as of BACKTEST_MONTHS ago (outcomes read from the newer
digits of today's strings), measures overlap with the other persona axes, sweeps every
threshold, and checks each result against the written expectations (PASS / WARN / FAIL).

Run in a Kedro notebook where `catalog` exists. Works from any notebook location:

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))

    from dpd_states_validate import main
    result = main(catalog, check_only=True)        # 1st: schema, counts, orientation (aggregates only)
    result = main(catalog)                         # full run, model_id from globals_dev
    result = main(catalog, model_id="<variant>")   # or one variant explicitly

READ-ONLY: writes nothing to the warehouse. Writes one aggregates-only JSON (+ a markdown
report) to docs/deterioration_states/results/ — no account keys, no raw DPD strings
(examples are banded journey shapes shared by >= 10 accounts). Config and threshold edits
take effect on the next call; no kernel restart needed (the config fingerprint is printed).

Before sign-off, validate in FILE mode without Spark: python docs/deterioration_states/run.py validate

FILL IN before running:
  * docs/deterioration_states/dpd_states/config.py — dataset and column names
  * _resolve_model_id below — the globals_dev accessor
Never guess a name: discover it in the repo catalog, or ask.

Sizes: the spine populations are sampled to `sample_n` rows each (default 100k) and only
the DPD string plus the configured optional columns are collected. The analysis itself
is pandas (the tested package in ../dpd_states).
"""
import datetime
import json
import pathlib
import re
import sys


def _pkg_root() -> pathlib.Path:
    """docs/deterioration_states — resolved from this file, independent of the CWD."""
    return pathlib.Path(__file__).resolve().parents[1]


def _resolve_model_id(model_id=None) -> str:
    """caller arg → project globals. Never a hardcoded literal."""
    if model_id:
        return model_id
    # <<FILL-IN: the real accessor — discover it in the workplace repo, never guess.
    #  Shape is one of:
    #    from <pkg>.<module> import globals_dev   ->  globals_dev["model_id"]
    #    conf_loader["globals"]["model_id"]  (Kedro OmegaConfigLoader) >>
    from FILL_IN_module_exposing_globals_dev import globals_dev  # noqa  <<FILL-IN>>
    return globals_dev["model_id"]                              # <<FILL-IN: key, if it differs>>


def _sample(sdf, n_rows, sample_n, seed):
    if not n_rows or n_rows <= sample_n:
        return sdf
    return sdf.sample(False, min(1.0, 1.1 * sample_n / n_rows), seed).limit(sample_n)


def _load_package():
    """Import (and RE-import) the package, so config / threshold edits made since the last
    run in the same notebook kernel take effect without a restart."""
    import hashlib
    import importlib
    sys.path.insert(0, str(_pkg_root()))
    import dpd_states.config, dpd_states.features, dpd_states.states, dpd_states.discover  # noqa: E401
    import dpd_states.analysis, dpd_states.expectations                                    # noqa: E401
    for m in (dpd_states.config, dpd_states.features, dpd_states.states, dpd_states.discover,
              dpd_states.analysis, dpd_states.expectations):
        importlib.reload(m)
    cfg, st = dpd_states.config, dpd_states.states
    fingerprint = hashlib.sha256(repr(
        ({k_: getattr(cfg, k_) for k_ in dir(cfg) if k_.isupper()}, st.DEFAULTS, st.OPTIONS)).encode()).hexdigest()[:12]
    return cfg, dpd_states.analysis, dpd_states.expectations, st, fingerprint


def main(catalog, model_id=None, out_dir=None, sample_n=100_000, check_only=False, seed=42):
    from pyspark.sql import functions as F

    cfg, an, ex, st, fingerprint = _load_package()
    md, run, evaluate = an.md, an.run, ex.evaluate
    DISPLAY_NAMES, RECOMMENDED = st.DISPLAY_NAMES, st.RECOMMENDED

    unfilled = [n for n, v in (("DS_STRINGS_TMPL", cfg.DS_STRINGS_TMPL), ("KEY", cfg.KEY), ("COL_DPD", cfg.COL_DPD))
                if "<<FILL-IN" in str(v)]
    if unfilled:
        print(f"CONFIG NOT FILLED: {unfilled} in dpd_states/config.py (see PROMPTS.md P1)")
        return None
    model_id = _resolve_model_id(model_id)
    out_dir = pathlib.Path(out_dir) if out_dir else _pkg_root() / "results"
    k = cfg.BACKTEST_MONTHS
    ds = cfg.DS_STRINGS_TMPL.format(model_id=model_id)

    # 1. load + schema guard ---------------------------------------------------------
    sdf = catalog.load(ds)
    required = ([cfg.KEY, cfg.COL_DPD] + ([cfg.COL_SNAPSHOT] if cfg.COL_SNAPSHOT else [])
                + ([cfg.COL_STRING_AS_OF] if cfg.COL_STRING_AS_OF else []))
    missing = [c for c in required if c not in sdf.columns]
    if missing:
        print(f"SCHEMA MISMATCH in {ds}. missing={missing}")
        print(f"available={sorted(sdf.columns)}")
        return None
    optional = {**cfg.AXIS_COLS, **cfg.EXISTING_RULE_COLS, **cfg.FLAG_COLS}
    present = {name: col for name, col in optional.items() if col and col in sdf.columns}
    absent = {name: col for name, col in optional.items() if col and col not in sdf.columns}
    warnings = []
    dpd_type = dict(sdf.dtypes)[cfg.COL_DPD]
    if dpd_type != "string":
        warnings.append(f"{cfg.COL_DPD} is stored as {dpd_type}, not string — numbers drop digits "
                        "(leading zeros, Excel's 15-digit limit). Use a string column.")

    # 2. scope FIRST: filter, latest snapshot, normalise the string -------------------
    if cfg.ROW_FILTER:
        sdf = sdf.where(cfg.ROW_FILTER)
    if cfg.COL_SNAPSHOT:
        latest = sdf.agg(F.max(cfg.COL_SNAPSHOT)).first()[0]
        sdf = sdf.where(F.col(cfg.COL_SNAPSHOT) == F.lit(latest))
    s = F.col(cfg.COL_DPD).cast("string")
    if cfg.STRIP_CHARS:                          # padding at the two ENDS only, never mid-string
        cls = "[" + re.escape(cfg.STRIP_CHARS) + "]+"
        s = F.regexp_replace(s, f"^{cls}|{cls}$", "")
    for a, b in (cfg.CHAR_MAP or {}).items():
        s = F.regexp_replace(s, re.escape(a), b)
    if not cfg.LEFTMOST_IS_CURRENT:
        s = F.reverse(s)
    asof_cols = [F.col(cfg.COL_STRING_AS_OF).alias("_asof")] if cfg.COL_STRING_AS_OF else []
    sdf = sdf.select(F.col(cfg.KEY).alias("_key"), s.alias("dpd_string"), *asof_cols,
                     *[F.col(c).alias(n) for n, c in present.items()]).cache()
    stale = None
    if cfg.COL_STRING_AS_OF:                     # strings frozen at charge-off / closure
        newest = sdf.agg(F.max("_asof")).first()[0]
        stale = sdf.where(F.col("_asof") != F.lit(newest)).count()
        sdf = sdf.where(F.col("_asof") == F.lit(newest)).drop("_asof")

    spine = [str(b) for b in cfg.SPINE_BUCKETS]
    is_cur = F.substring("dpd_string", 1, 1).isin(spine)
    is_bt = (F.length("dpd_string") > k) & F.substring("dpd_string", k + 1, 1).isin(spine)
    exited = is_bt & (F.substring("dpd_string", 1, 1).cast("int") >= cfg.EXIT_BUCKET)
    counts = sdf.agg(
        F.count("*").alias("rows"),
        F.countDistinct("_key").alias("accounts"),
        F.sum(is_cur.cast("int")).alias("current_spine"),
        F.sum(is_bt.cast("int")).alias("backtest_spine"),
        F.sum(exited.cast("int")).alias("backtest_now_8plus"),
        F.sum((~F.col("dpd_string").rlike("^[0-9]+$")).cast("int")).alias("non_digit_strings"),
        F.expr("percentile_approx(length(dpd_string), array(0.05, 0.5, 0.95))").alias("len_p05_p50_p95"),
    ).first().asDict()
    counts["stale_strings_excluded"] = stale
    sdf = sdf.drop("_key")                      # keys never leave Spark

    scope_note = (f"{ds}" + (f" where {cfg.ROW_FILTER}" if cfg.ROW_FILTER else "")
                  + (f", latest {cfg.COL_SNAPSHOT}" if cfg.COL_SNAPSHOT else "")
                  + f"; today's spine = current digit in {spine}; backtest = digit {k + 1} in {spine}"
                  + f"; sampled to <= {sample_n:,} rows each")
    if counts["rows"] != counts["accounts"]:
        warnings.append("more rows than accounts — set COL_SNAPSHOT or de-duplicate")
    if cfg.DS_STRINGS_HAS_EXITED and counts["backtest_spine"] and not counts["backtest_now_8plus"]:
        warnings.append("no backtest account is at 8+ today — the table looks survivor-only; "
                        "outcomes would be biased. Point DS_STRINGS at a table that keeps exited "
                        "accounts, or set DS_STRINGS_HAS_EXITED = False")

    if check_only:
        # Orientation check from aggregates only (no raw strings leave the notebook): with the
        # newest month on the left, today's spine starts with 4–7 and its oldest month is 0/1.
        ends = (sdf.where(is_cur)
                .select(F.substring("dpd_string", 1, 1).alias("newest"),
                        F.expr("substring(dpd_string, length(dpd_string), 1)").alias("oldest"))
                .groupBy("newest", "oldest").count().orderBy(F.desc("count")).limit(10).collect())
        smp = [r.dpd_string for r in sdf.where(is_cur).select("dpd_string").limit(2000).collect()]
        from dpd_states.discover import shape
        from collections import Counter
        shapes = [(sh, n) for sh, n in Counter(shape(x) for x in smp if x.isdigit()).most_common(8) if n >= 10]
        print("=== DPD_STATES CHECK START ===")
        print(f"model_id: {model_id}")
        print(f"config fingerprint: {fingerprint}")
        print(f"scope: {scope_note}")
        print(f"counts: {counts}")
        print(f"optional columns present: {present}")
        print(f"optional columns configured but missing: {absent}")
        print("newest / oldest digit of today's spine (expect newest 4–7, oldest mostly 0/1):")
        for r in ends:
            print(f"  newest={r.newest} oldest={r.oldest}  n={r['count']:,}")
        print("most common journey shapes in a 2,000-string sample (N clean, R roll, H hold, P paid 2+):")
        for sh, n in shapes:
            print(f"  {n:>5}  {sh}")
        for w in warnings:
            print(f"WARNING: {w}")
        print("=== DPD_STATES CHECK END ===")
        return {"model_id": model_id, "counts": counts, "present": present, "absent": absent,
                "warnings": warnings}

    # 3. collect two small samples (no keys), analyse in pandas -----------------------
    cur_pd = _sample(sdf.where(is_cur), counts["current_spine"], sample_n, seed).toPandas()
    bt_pd = None
    if cfg.DS_STRINGS_HAS_EXITED and counts["backtest_spine"]:
        bt_pd = _sample(sdf.where(is_bt).select("dpd_string"), counts["backtest_spine"],
                        sample_n, seed).toPandas()
    R, report = run(cur_pd, bt_pd, cfg, spark_counts=counts)
    checks = evaluate(R)

    payload = {
        "task": "DPD_STATES_VALIDATION",
        "run_date": datetime.date.today().isoformat(),
        "model_id": model_id,
        "config_fingerprint": fingerprint,
        "scope": scope_note,
        "counts": counts,
        "warnings": warnings,
        "optional_columns_present": sorted(present),
        "results": R,
        "expectations": checks.to_dict("records"),
    }

    # 4. file hand-off + printed headline --------------------------------------------
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^A-Za-z0-9]+", "_", model_id).strip("_")
    stamp = payload["run_date"].replace("-", "")
    out = out_dir / f"dpd_states_validation_{slug}_{stamp}.json"
    out.write_text(json.dumps(payload, indent=2, default=str))
    rep = out.with_suffix(".md")
    rep.write_text(f"# DPD deterioration states — validation\n\nmodel_id: `{model_id}` · run "
                   f"{payload['run_date']} · scope: {scope_note}\n\n"
                   + "".join(f"> WARNING: {w}\n\n" for w in warnings)
                   + "## 0. Expectation checks\n\n" + md(checks, index=False) + "\n\n" + report + "\n")

    n_status = checks.status.value_counts().to_dict()
    rec = R["states_today"][RECOMMENDED]["share"]
    print("=== DPD_STATES OUTPUT START ===")
    print(f"model_id: {model_id}")
    print(f"config fingerprint: {fingerprint}")
    print(f"scope: {scope_note}")
    print(f"counts: {counts}")
    for w in warnings:
        print(f"WARNING: {w}")
    print(f"expectations: {n_status}")
    for r in checks.itertuples():
        print(f"  {r.id:<4} {r.status:<7} observed={r.observed!s:<14} expected={r.expected:<8} {r.check[:70]}")
    print(f"{RECOMMENDED} shares today: " + ", ".join(f"{DISPLAY_NAMES[s]}={v:.1%}" for s, v in rec.items()))
    print(f"wrote: {out} and {rep.name} (aggregates only) -> commit & push from PROD, pull in UAT")
    print("=== DPD_STATES OUTPUT END ===")
    return payload
`````
