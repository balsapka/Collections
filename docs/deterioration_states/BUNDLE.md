# Deterioration states — full source bundle

## Run this (from the repo root)

```bash
# 1. recreate every file and verify checksums      -> "N files OK, 0 mismatched"
python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md

# 2. dependencies (once)
python -m pip install pandas numpy scikit-learn openpyxl

# 3. self-test on synthetic data                    -> "SELFTEST PASSED"  (~1 min)
python docs/deterioration_states/run.py selftest

# 4. validate on the real file                      -> checks + state shares
#    reads data/input/dpd_synthetic_data.xlsx, column dpd_history_str (config.py),
#    crops to the reliable history window (2024-01 .. 2026-08 = 32 months), keeps buckets 4-7
python docs/deterioration_states/run.py validate
#    another file and/or sample size:
#    python docs/deterioration_states/run.py validate data/input/other_file.xlsx 50000

# 5. optional: synthetic method-validation report
python docs/deterioration_states/run.py synthetic

# 6. PySpark pipeline (CC + RL) — review + rewrite: read spark/REVIEW_SPARK.md first
python docs/deterioration_states/spark/tests/test_parity.py      # -> "PARITY PASSED" (no Spark, ~30 s)
python docs/deterioration_states/spark/tests/test_spark_e2e.py   # -> "SPARK E2E PASSED" (local Spark + Java 17)
```

**For the PySpark pipeline, start at `spark/REVIEW_SPARK.md`** — findings on the workplace
code (F1–F12), the rewrite design, the coverage plan (99.9%) and the shipping steps (§5).
Roles: the workplace assistant has **no PROD data access** — it edits code and runs the
offline tests only (S1–S4, never `catalog.load`). The user runs the pipelines in PROD and
then `spark/prod_check.py` (P1–P2), which prints aggregates only. The copy-paste prompt for the assistant is **PROMPTS.md P8**; **P9** adds the tests to `src/tests/` and cleans up afterwards; **P10** moves the repo to one state vocabulary for both segments (no stabilized at 180+); **P11** rebuilds the stakeholder workbook.

Step 1 needs `extract_bundle.py` — create it from the **Extractor** section below the first
time. Step 4 prints the checks between `=== DPD_STATES OUTPUT START ===` and `END` and writes
`docs/deterioration_states/results/dpd_states_file_<file>_<date>.json` + `.md` (aggregates
only) — paste the printed block back, or follow PROMPTS.md P0 -> P2 with Sonnet.

If it fails: "column ... not in" -> check COL_DPD in `dpd_states/config.py`; "look like
numbers" -> the Excel column is stored as numbers (digits lost), re-save it as text;
"No module named openpyxl" -> step 2; snapshot not Aug 2026 -> set SNAPSHOT_MONTH in config.

Spark mode (later, for outcomes / production), in a Kedro notebook — PROMPTS.md P6:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
from dpd_states_validate import main
main(catalog, check_only=True)   # dry run: schema, counts, orientation (aggregates)
result = main(catalog)           # full validation incl. backtest -> results/
```

---

Generated 2026-10-21 by `dpd_states/bundle.py`. 42 files, 7,330 lines.
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
    2. python -m pip install pandas numpy scikit-learn openpyxl      (once)
    3. python docs/deterioration_states/run.py selftest
         -> must end with "SELFTEST PASSED" (~1 minute)
    4. python docs/deterioration_states/run.py validate
         -> checks + state shares on data/input/dpd_synthetic_data.xlsx (config.py)
    5. optional: python docs/deterioration_states/run.py synthetic
    Spark mode later: snippets/dpd_states_validate.py, main(catalog) (PROMPTS.md P6)
    PySpark pipeline (CC + RL): read spark/REVIEW_SPARK.md, then
       python docs/deterioration_states/spark/tests/test_parity.py   -> "PARITY PASSED"

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
    print("Next, from the repo root: python docs/deterioration_states/run.py selftest")
    print("then:                     python docs/deterioration_states/run.py validate")
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
├── dpd_states/segment_180.py
├── dpd_states/discover.py
├── dpd_states/synth.py
├── dpd_states/run_synthetic.py
├── dpd_states/selftest.py
├── dpd_states/bundle.py
├── snippets/dpd_states_validate.py
├── spark/REVIEW_SPARK.md
├── spark/conf/parameters_crx_persona_dpd_journey.yml
├── spark/crx_persona/__init__.py
├── spark/crx_persona/_dpd_journey.py
├── spark/crx_persona/cc_full_history/__init__.py
├── spark/crx_persona/cc_full_history/nodes.py
├── spark/crx_persona/rl_full_history/__init__.py
├── spark/crx_persona/rl_full_history/nodes.py
├── spark/crx_persona/cc_a4_deterioration/__init__.py
├── spark/crx_persona/cc_a4_deterioration/nodes.py
├── spark/crx_persona/cc_a4_deterioration/pipeline.py
├── spark/crx_persona/rl_a4_deterioration/__init__.py
├── spark/crx_persona/rl_a4_deterioration/nodes.py
├── spark/crx_persona/rl_a4_deterioration/pipeline.py
├── spark/tests/test_parity.py
├── spark/tests/test_spark_e2e.py
├── spark/tests/conftest.py
├── spark/tests/nodes/crx_persona/conftest.py
├── spark/tests/nodes/crx_persona/test_dpd_journey.py
├── spark/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py
├── spark/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py
├── spark/prod_check.py
├── spark/stakeholder/build_states_workbook.py
├── results/
├── validation/
```

- empty folder: `results`
- empty folder: `validation`

`results/` receives the real-data outputs; `validation/` holds the synthetic evidence
(regenerate with `python docs/deterioration_states/run.py selftest` and `... run.py synthetic`).

## Files

### FILE: `README.md`
sha256 `dabd6c3fa3a1a93d53d74036f19310987551da39902751808ba9556223b4b239` · 123 lines · trailing newline: yes

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
current month), crops it to the reliable history window (2024-01 → 2026-08 = 32 months, set in
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
├── spark/                    PySpark / Kedro PIPELINE for the workplace (CC + RL)
│   ├── REVIEW_SPARK.md       review of the workplace code (F1–F12), rewrite design, coverage, prompts W1–W4
│   ├── crx_persona/          drop-in: _dpd_journey.py engine + cc/rl full_history + a4_deterioration nodes
│   ├── conf/                 parameters (dpd_journey: floor, segment, option, gap rules)
│   ├── prod_check.py         run in PROD after the pipelines: coverage + state shares (aggregates only; save_json for the workbook)
│   ├── stakeholder/          build_states_workbook.py: the stakeholder xlsx, rules + examples from the engine (PROMPTS P11);
│   │                         dpd_deterioration_states_reference.xlsx = reference copy, Results empty (git only, not in the bundle)
│   └── tests/                nodes/ + pipelines/crx_persona/ (96 tests, ship to src/tests/) · test_parity.py · test_spark_e2e.py (bundle-only)
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
sha256 `da50a569980d6cc81dd756f72d52a4319ae7396714a1fffbc9cbc32ebffb04d4` · 50 lines · trailing newline: yes

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

TOOLS = ("validate", "selftest", "synthetic", "s180", "bundle")


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
    if cmd == "s180":
        from dpd_states.segment_180 import main as run
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
sha256 `c1cfdcb731453183676a0d8af865e4e8f91c7d06734ffff2cbc54aaf24565a27` · 487 lines · trailing newline: yes

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
  `SNAPSHOT_MONTH` (2026-08) — **32 months** — or to the source's own fixed window if shorter
  (`SOURCE_WINDOW_MONTHS`; the sign-off file now carries full history, so 32 applies). A
  string that fills the whole window may have older history and is treated as cropped —
  never EPD, never "history starts delinquent", and a straight roller is seasoned.
  Effects, all handled:
  - EPD is unaffected: an EPD has at most 3 clean months plus a short straight roll, so its
    string is under 12 digits and never cropped. As a safety net, a cropped string can
    never be EPD (its oldest digit is no longer the first billed month).
  - A spell that started before 2024 makes a cropped string start delinquent: how the
    account fell in is not visible, so it is **unknown** unless it is stabilized (Q0;
    3.3% of the synthetic spine, 17–32% of the synthetic 180+ segment).
  - Seasoned (≥ 12 months) and the 12-month repeat window fit inside 32 months; earlier
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
| `gap_prior_peak3` | clean months between the end of the most recent earlier spell that reached bucket 3 and the start of this one (repeat delinquent: ≤ 12) | yes |
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
Q0  Journey start observed?  the oldest OBSERVED month is already at bucket 2+ (spell
                            older than the window / floor, restructured re-open, migrated
                            or missing history): stabilized if Q2 holds, else -> unknown
Q1  Early payment default?  <= 3 months of history before this spell (at most one blip,
                            no earlier real spell) AND never paid since crossing bucket 2
                            (every month of the spell a roll — still falling)
                                                               -> early_payment_default
Q2  Stabilized?             today's bucket <= 7 (151-180 DPD; never at 180+) AND
                            >= 5 of the last 6 months within today's bucket ±1
                            OR (>= 6 months since first reaching 4 AND at most 1 bucket
                                higher than 6 months ago)      -> stabilized
Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and ended
                            <= 12 months before this spell started
                                                               -> repeat_delinquent
Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
      yes -> straight_roller  [B, C: >= 12 months of history before the spell
                               -> straight_roller_seasoned, else straight_roller_early_life]
      no  -> slow_roller      [C: paid 2+ months at once on the way down
                               -> slow_roller_erratic, else slow_roller_intermittent]
```

(Q3 "paying since bucket 4" was tested and rejected — §6.4.) Q0 is a confidence guard,
not a behaviour state: when the history starts at 0 DPD the whole journey is observed and
the fall-in states are confident; when it starts delinquent they would be guesses, so the
account is `unknown` (stabilized needs only the last 6 months and is still assigned). At
the ceiling bucket (CC 9, RL 7) the bucket cannot rise, so a run of 9s is not a payment:
stabilized is assigned only up to bucket 7 (151-180 DPD, never at 180+), and holds at the
ceiling do not count as payments (EPD). The 180+ segment uses this same tree and the same
states — production uses option B only. Uncropped starts-delinquent histories should stay
rare (E04).

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
| **Repeat delinquent (re-default)** · `repeat_delinquent` | Cured a spell that reached bucket 3 and fell back in within 12 months | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 10.8% |
| **Seasoned straight roller** · `straight_roller_seasoned` | At least a year on book, then rolled straight to bucket 4 with no payment on the way down (some have paid since) | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 57.4% |
| **Early-life straight roller** · `straight_roller_early_life` | 4–11 months on book, then rolled straight to bucket 4 | Same triage; also an underwriting signal for acquisition | 4.7% — under the 5% floor in synthetic data; the real share decides (E16) |
| **Slow roller (partial payer)** · `slow_roller` | Paid something on the way down to bucket 4 but kept rolling | Over-indebted: longer-tenor restructure or settlement | 15.1% |
| ↳ **Intermittent payer** *(C)* · `slow_roller_intermittent` | Paid one month here and there on the way down, never caught up | Chronic insufficiency: restructure to what they actually pay | 9.3% |
| ↳ **Erratic payer** *(C)* · `slow_roller_erratic` | Caught up 2+ months at once on the way down, then rolled again | Lumpy / irregular income: plan aligned to inflow timing | 5.7% |
| **Unknown** · `unknown` | The oldest observed month is already delinquent: how the account fell in is not visible (spell older than the window / floor, restructured, migrated or missing history) | Treat on current behaviour and other axes only | 3.3% with the 32-month window (synthetic); large at 180+ |

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
| Repeat-delinquent window (`repeat_window_months`) [business] | **ended ≤ 12 months before this spell** | Owner decision (changed from 24); the common re-default window. Measured to the start of this spell, so the state stays fixed | Lowers the overlap with credibility's lifetime clean point (eta² 0.81 with no window → 0.52 at 12 months) |
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
explain **52%** of that point's variance under the 12-month window (81% with no window). It is in B/C
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
| repeat delinquent ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.52 of the clean point explained by B states (12-month window) | Decides A vs B. E19b |
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
sha256 `6857ab3f9c05a2765ca828b0dfa68c368390985a7c55061bebb44bc8c60693a5` · 606 lines · trailing newline: yes

`````markdown
# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace repository. Each prompt is
self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 (file mode) → P2**, then P3 / P4 as the results require, then P5.
**P6 (Spark) and P7 (production)** only after the methodology and states are signed off.
**P8 ships the reviewed PySpark pipeline (CC + RL)** into the existing Kedro code — it
replaces P7 for that work. Sonnet has no PROD data access: P8 is code changes and offline
tests only; the user runs the pipelines and `spark/prod_check.py` in PROD.
**P9 runs after P8**: adds the regression tests under `src/tests/{nodes,pipelines}/crx_persona/`
and removes everything unpacked from the bundle (recoverable from BUNDLE.md), plus any dead
code the rewrite left in `src/`.
**P10 fixes the state vocabulary** (after P9): one tree and the same 7 states for 60–180
and 180+ (option B only), no stabilized at 180+, holds at the ceiling are not payments.
**P11 rebuilds the stakeholder workbook** (after P10) from the deployed engine plus the
PROD counts — replaces `dpd_states_review_20261016.xlsx` (7 business-facing sheets).

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

## P5 — Short stakeholder report: rules and results

```
Task: write the shortest possible report for the Group Retail Risk stakeholders from the
latest results/dpd_states_file_<file>_<date>.json and .md (or the Spark results file).
Target: one screen. No code, no eta², no ARI, no check IDs.

Write exactly these sections:

1. Title + one sentence: what the states are (one state per credit-card account in
   90–180+ DPD, buckets 4–7, from its DPD history since Jan 2024) and the data used
   (file, snapshot month, number of accounts).

2. The rules — one table, rows in this order (option B), columns: State | Rule (one line,
   plain words) | Share | Action. Use the display names and these rules:
   - Early payment default (EPD, formerly "bust-out"): at most 3 months on book before
     falling in (one paid-off blip allowed) and never paid since — still rolling.
   - Stabilized: paying about one month's due each month — 5 of the last 6 months within
     one bucket of today's, or 6+ months past bucket 4 and at most one bucket higher than
     6 months ago.
   - Repeat delinquent: cured a spell that reached 60+ DPD and fell back in within 12 months.
   - Seasoned straight roller: 12+ months on book, then rolled straight to bucket 4 with no
     payment on the way down.
   - Early-life straight roller: same, within the first 12 months on book.
   - Slow roller (partial payer): paid something on the way down but kept rolling.
   Actions: from METHODOLOGY.md §4. Shares: from the results file only.
   Add one line under the table: states are checked in this order, first match wins, so
   every account gets exactly one state.

3. Results — at most 5 bullets, real numbers only: the biggest state(s), stabilized vs
   the bank's ~6%, EPD vs the bank's ~6% bust-out, data quality in one line (accounts
   excluded and why), and that outcome checks (roll rates, exits) come with the Spark
   backtest.

4. Decisions needed — at most 3 bullets, from METHODOLOGY.md §10.

Every number must come from the results file. If a check FAILED (e.g. unparseable
strings), say so in one line under Results with the count and what is being done.
Write it to docs/deterioration_states/results/stakeholder_report_<date>.md and show it to me.
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

*Superseded by **P8** for the CC / RL Kedro pipelines (`crx_persona`), which already exist.*

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

---

## P8 — Ship the reviewed PySpark pipeline (CC + RL) into the Kedro repo

Background: `spark/REVIEW_SPARK.md` (findings F1–F12, design, rule changes, §5 roles).
Sonnet runs this prompt (code + offline tests). Afterwards **you** run REVIEW_SPARK.md §5
P1–P2 in PROD and paste the `=== DPD_JOURNEY PROD CHECK START / END ===` block back.

```
Context: I am adding a reviewed PySpark/Kedro rewrite of the DPD-journey deterioration
pipelines (CC + RL) to this repo. Everything is in docs/deterioration_states/BUNDLE.md,
which I have saved raw at that path.

Hard rules:
- You have NO PROD data access. Never call catalog.load, never run kedro run, never
  query any table. Only edit code and run offline tests (synthetic data).
- Never guess a dataset, column or module name: find it in the repo or ask me.
- Do not retype bundled code by hand: use the extractor, which checks SHA-256.
- Stop and wait for my OK where marked STOP.

Step 1 — unpack and verify
1. Create docs/deterioration_states/extract_bundle.py from the "Extractor" section of
   BUNDLE.md, then run:
   python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
   It must end with "N files OK, 0 mismatched". If anything mismatches, stop and tell
   me (the copy was altered); do not hand-fix code.
2. Run: python docs/deterioration_states/spark/tests/test_parity.py
   It must print "PARITY PASSED". If pyspark or another package is missing, tell me
   which; do not change code to work around it.

Step 2 — impact scan (report only, change nothing)
Read docs/deterioration_states/spark/REVIEW_SPARK.md first (findings, design, §5).
Then report:
a) every importer of _dpd_journey under src/ and the names each one imports
   (grep -rn "_dpd_journey" src/);
b) the catalog entries (conf/**/catalog*.yml) for crx_cc_dpd_sequences,
   crx_rl_dpd_sequences, crx_cc_a4_deterioration, crx_rl_a4_deterioration — format,
   partitioning, schema settings;
c) any consumer of those four datasets outside the cc/rl_a4_deterioration pipelines;
d) the current value of _DPD_BUCKET_REGEX and where it is defined;
e) the PySpark version the project pins (the new code needs >= 3.3);
f) the current params:crx_persona block (file path + keys).
STOP — show me the report.

Step 3 — apply (only after my OK)
Replace, keeping this repo's import style, logging and lint conventions:
- src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
    <- docs/deterioration_states/spark/crx_persona/_dpd_journey.py
- cc_full_history/nodes.py: build_cc_full_history
    <- spark/crx_persona/cc_full_history/nodes.py (keep the repo's _DPD_BUCKET_REGEX)
- rl_full_history/nodes.py: build_rl_full_history
    <- spark/crx_persona/rl_full_history/nodes.py
- cc_a4_deterioration/nodes.py and rl_a4_deterioration/nodes.py
    <- the files under spark/crx_persona/
- pipeline.py files: only if the node inputs differ from what is there now.
- Merge spark/conf/parameters_crx_persona_dpd_journey.yml under the existing
  crx_persona: block (do not touch persona_start_date / persona_end_date).
- Catalog: crx_cc_dpd_sequences and crx_rl_dpd_sequences are now ONE ROW PER ACCOUNT
  with an array<int> column dlq_buckets. Propose the catalog change (drop any
  partitioning by month).
If step 2a/2c found anything that still needs resolve_gaps, encode_transitions,
classify_from_grid or old BucketScheme fields, do NOT delete it: STOP and show me.
STOP — show me the full diff before writing files.

Step 4 — offline verification (after the files are written)
1. The repo's lint / test command on the changed files.
2. python -c "from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import create_pipeline as c; from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import create_pipeline as r; print(c().describe()); print(r().describe())"
3. python docs/deterioration_states/spark/tests/test_parity.py  -> PARITY PASSED
4. If Java + local Spark work in the dev container:
   python docs/deterioration_states/spark/tests/test_spark_e2e.py 2000  -> SPARK E2E PASSED
   (synthetic data only; if Java is missing, say so and skip.)
Report every result verbatim. Then list what I must run in PROD (REVIEW_SPARK.md §5
P1-P2) using this repo's real pipeline names.
```

---

## P9 — Add the tests, then clean up (after P8)

Before pasting: replace `docs/deterioration_states/BUNDLE.md` in the workplace repo with
the **latest raw** BUNDLE.md (it now carries the tests). The pipeline code in it is the
same as the bundle P8 used — step 1 checks that.

```
Context: P8 is done — the reviewed DPD-journey deterioration pipelines (CC + RL) are in
src/enbd_collections/pipelines/crx_persona/. I have just replaced
docs/deterioration_states/BUNDLE.md with a newer version that adds regression tests.
Now: (1) check src/ matches the bundle, (2) add the tests under src/tests/, (3) remove
everything else unpacked from the bundle and any dead code, so the repo holds only what
the registered pipelines use, plus their tests. I will re-extract from BUNDLE.md if I
ever need the rest.

Hard rules:
- No PROD data access: never call catalog.load, never run kedro run, never query a table.
- Delete nothing before I approve the plan (STOP below). Use `git rm` / `git mv`.
  Do not commit or push.
- Never delete anything a registered pipeline imports, any test of it, or any file that
  was not unpacked from the bundle without asking me.

Step 1 — re-extract and check src/ is current (report only)
1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
   -> must end with "0 mismatched" (if extract_bundle.py is gone, recreate it from the
   bundle's "Extractor" section first).
2. Compare the bundled engine and nodes with src/, ignoring import lines and formatting:
     docs/deterioration_states/spark/crx_persona/_dpd_journey.py   vs src/.../crx_persona/_dpd_journey.py
     .../spark/crx_persona/cc_full_history/nodes.py                vs src/.../cc_full_history/nodes.py
     .../spark/crx_persona/rl_full_history/nodes.py                vs src/.../rl_full_history/nodes.py
     .../spark/crx_persona/cc_a4_deterioration/nodes.py, pipeline.py vs src/...
     .../spark/crx_persona/rl_a4_deterioration/nodes.py, pipeline.py vs src/...
   Report every LOGIC difference (anything beyond imports, the repo's _DPD_BUCKET_REGEX,
   logging and lint style). Quick check that the latest rules are in src/:
   grep -n "starts_delinquent\|def _stabilized\|\"unknown\"" src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
   must show all three.
If there is any logic difference, STOP and show me before going on.

Step 2 — add the tests (only after step 1 is clean)
Copy, keeping file names:
  docs/deterioration_states/spark/tests/nodes/crx_persona/test_dpd_journey.py
  docs/deterioration_states/spark/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py
  docs/deterioration_states/spark/tests/nodes/crx_persona/conftest.py
      -> src/tests/nodes/crx_persona/
  docs/deterioration_states/spark/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py
      -> src/tests/pipelines/crx_persona/
Create the crx_persona folders; add __init__.py files only if the sibling test folders
under src/tests/nodes and src/tests/pipelines have them. If src/tests (or a parent
conftest) already defines a session-scoped `spark` fixture, do not copy conftest.py — the
tests use the existing fixture. Do NOT copy docs/deterioration_states/spark/tests/conftest.py
or test_parity.py / test_spark_e2e.py (bundle-only: an import shim and the one-time proof
against the numpy reference). If step 1 found that the repo's pipeline uses different
dataset or node names, adapt the EXPECTED table in test_a4_deterioration_pipelines.py to
the repo — never the pipeline to the test.
Run:
  python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona
  -> 96 passed (the Spark node tests need Java + pyspark; if Java is missing, report it
     and run the other two files: 89 passed).

Step 3 — inventory for the clean-up (report only, change nothing)
a) Registered pipelines: from the pipeline registry, list the crx_persona pipelines and
   every module they import, transitively, inside src/enbd_collections/pipelines/crx_persona/.
b) Bundle files: every path in BUNDLE.md's "### FILE: `...`" headers that exists on disk,
   plus extract_bundle.py, results/, validation/, __pycache__/ and .gitkeep files under
   docs/deterioration_states/. Separately: anything under docs/deterioration_states/ that
   is NOT from the bundle (my notes, real-data outputs in results/) -> "ask", never "delete".
c) Dead code in src/enbd_collections/pipelines/crx_persona/ left by the rewrite:
   functions, constants and imports nothing references any more (e.g. old resolve_gaps /
   encode_transitions / classify_from_grid, old _log_* helpers, _CC_HISTORY_FLOOR_DATE,
   _DET_OPTION, _SCHEME, _AUDIT_COLS, unused imports). Confirm each with grep across
   src/ (including src/tests/), conf/ and notebooks/; if available, also run
   `ruff check --select F401,F811,F841` (or the repo's linter) and
   `python -m vulture src/enbd_collections/pipelines/crx_persona` as a hint, not a verdict.
d) Old tests, notebooks and docs that reference removed names (e.g. tests of resolve_gaps /
   encode_transitions) or docs/deterioration_states paths.
e) Parameters and catalog entries no longer read by any node.
Show the plan as one table: path or symbol | evidence it is unused | action
(delete / keep / ask). Defaults:
- docs/deterioration_states/**: delete everything from the bundle EXCEPT BUNDLE.md (the
  archive to re-extract from) — i.e. spark/ (its code is in src/, its tests now in
  src/tests/), dpd_states/, snippets/, run.py, extract_bundle.py, METHODOLOGY.md / .pdf,
  README.md, REVIEW.md, PROMPTS.md, validation/, __pycache__/.
- results/ with real-data outputs: ask.
- src/: delete only symbols with zero references.
STOP — wait for my approval of the table.

Step 4 — apply the approved table only
git rm the files; remove dead symbols and unused imports with minimal edits (no
reformatting of untouched code); remove empty folders. Leave BUNDLE.md unchanged.

Step 5 — verify (offline) and report verbatim
1. The repo's lint command on src/enbd_collections/pipelines/crx_persona/ and
   src/tests/nodes/crx_persona/, src/tests/pipelines/crx_persona/.
2. python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona -> all pass
   (and the rest of src/tests, if it ran green before).
3. kedro registry list   (imports every pipeline; no data) — crx_persona pipelines listed.
4. grep -rn "docs/deterioration_states\|resolve_gaps\|encode_transitions\|classify_from_grid" src/ conf/
   -> nothing (or only what I approved to keep).
5. git status --short and git diff --stat.
```

---

## P10 — One state vocabulary for both segments; no stabilized at 180+ (after P9)

Why: the previous engine had a separate 180+ tree that allowed `stabilized` at CC 8 and
added 180+-only states (`paying_in_default`, `broken_payer`), and it kept the A / C option
states that production never uses (`straight_roller`, `slow_roller_intermittent`,
`slow_roller_erratic`) plus a dead one (`paying_since_4`). Both came from the bundle, not
from Sonnet. Fixed: ONE tree and the same 7 states in both segments — `unknown`,
`early_payment_default`, `stabilized`, `repeat_delinquent`, `straight_roller_seasoned`,
`straight_roller_early_life`, `slow_roller`. Stabilized only up to CC 7 / RL 6 (151–180
DPD), never at 180+. Holds at the ceiling (CC 9, RL 7) are not payments, so EPD still works
at 180+. `det_option` and the `det_state_option` column are removed.

Before pasting: replace `docs/deterioration_states/BUNDLE.md` with the **latest raw**
BUNDLE.md. Changed for the repo: `_dpd_journey.py`, the `dpd_journey` params (no
`det_option`), and the three tests in `src/tests/{nodes,pipelines}/crx_persona/`. The node
and pipeline files are unchanged.

```
Context: src/enbd_collections/pipelines/crx_persona/ holds the DPD-journey deterioration
pipelines (CC + RL) from an earlier bundle, with tests in src/tests/nodes/crx_persona/ and
src/tests/pipelines/crx_persona/. docs/deterioration_states/ holds only BUNDLE.md, which I
have just replaced with a newer version. The new engine has ONE state tree for both
segments (60_180 and 180_plus) with 7 states: unknown, early_payment_default, stabilized,
repeat_delinquent, straight_roller_seasoned, straight_roller_early_life, slow_roller.
No stabilized at 180+, no 180+-only states, no A/C options. Bring src/ and the tests in
line, and remove everything the old vocabulary left behind.

Hard rules:
- No PROD data access: never call catalog.load, never run kedro run, never query a table.
- Extract the bundle OUTSIDE the repo (a temp folder) so nothing is unpacked into
  docs/ again; delete the temp folder at the end.
- STOP where marked. Do not commit or push.
- Never adapt the engine to make a test pass; adapt only repo-specific names in tests.

Step 1 — extract to a temp folder and verify (report only)
1. mkdir a temp folder outside the repo, e.g. T=$(mktemp -d). Create $T/extract_bundle.py
   from the "Extractor" section of docs/deterioration_states/BUNDLE.md, then:
   python $T/extract_bundle.py docs/deterioration_states/BUNDLE.md $T
   -> must end with "0 mismatched".
2. python $T/spark/tests/test_parity.py -> must print "PARITY PASSED" (needs pandas,
   numpy, pyspark importable; no Spark session).

Step 2 — compare (report only)
Diff, ignoring import lines and formatting:
  $T/spark/crx_persona/_dpd_journey.py vs src/enbd_collections/pipelines/crx_persona/_dpd_journey.py
  $T/spark/tests/nodes/crx_persona/*.py vs src/tests/nodes/crx_persona/*.py
  $T/spark/tests/pipelines/crx_persona/*.py vs src/tests/pipelines/crx_persona/*.py
  $T/spark/crx_persona/{cc,rl}_{full_history,a4_deterioration}/*.py vs src/... (expected: no logic change)
Expected engine differences: one assign_state(f, cropped) for both segments;
classify(buckets, cropped, offset, canon_top) without segment/option; STATE_RULES/STATES
replace STATE_DEFAULTS/OPTIONS; features_180 / assign_state_180 / _FEATURES_180 removed;
journey_features(..., canon_top) does not count holds at the ceiling as payments; no
det_option param (an unknown dpd_journey key now raises); no det_state_option column.
List any OTHER difference in src/ — e.g. adaptations made in P8/P9 (logging, import
style, _DPD_BUCKET_REGEX, fixture names, EXPECTED table names) — those must be kept.
Then find every remaining use of the old vocabulary and options:
  grep -rn "det_option\|det_state_option\|segment_180_prototype\|assign_state_180\|features_180\|_FEATURES_180\|STATE_DEFAULTS\|OPTIONS\|paying_in_default\|broken_payer\|history_not_available\|history_starts_delinquent\|paying_since_4\|slow_roller_intermittent\|slow_roller_erratic\|\"straight_roller\"\|A_minimal_4\|C_detailed_7\|B_balanced_6" src/ conf/ notebooks/ 2>/dev/null
including catalog schemas / column lists that name det_state_option or the 180+ extra
columns (all_default, months_in_default, default_left_censored, pay_events_before_top,
paid_in_default, stabilized_months_in_4_7).
STOP — show me the diff summary and the grep results with a proposed action for each.

Step 3 — apply (only after my OK)
- Replace src/enbd_collections/pipelines/crx_persona/_dpd_journey.py with
  $T/spark/crx_persona/_dpd_journey.py, re-applying only the repo adaptations listed in
  step 2 (imports, logging, lint style).
- Remove `det_option` from the crx_persona.dpd_journey params (conf/**/parameters*.yml).
- Replace the three test files with the $T versions, re-applying only the repo
  adaptations from P9 (fixture choice, names in the EXPECTED table).
- Fix or remove every grep hit approved in step 2 (catalog column lists, notebooks, docs).
- Leave the node and pipeline files alone unless step 2 found a logic difference I
  approved.

Step 4 — verify (offline) and report verbatim
1. The repo's lint command on the changed files.
2. python -m pytest src/tests/nodes/crx_persona src/tests/pipelines/crx_persona
   -> 96 passed (89 if Java is missing: report it).
3. kedro registry list   (imports every pipeline; no data needed).
4. The step-2 grep again -> no hits (or only ones I approved to keep).
5. python -c "from enbd_collections.pipelines.crx_persona import _dpd_journey as J; print(J.STATES)"
   -> the 7 states.
6. Delete $T. Show git status --short and git diff --stat.
Then tell me what to re-run in PROD: Node 2 of both products for segment 60_180 and
180_plus (Node 1 is unchanged and need not be re-run), using this repo's real pipeline
and node names.
```

For the PROD check afterwards: `prod_check.py` is no longer in the repo. Extract the bundle
to a temp folder as in step 1, then in the Kedro session
`sys.path.insert(0, "<temp>/spark"); from prod_check import report; report(catalog)`.

---

## P11 — Rebuild the stakeholder workbook (after P10)

What it produces: `dpd_deterioration_states_<YYYYMMDD>.xlsx`, replacing
`dpd_states_review_20261016.xlsx`. Seven business-facing sheets: **Overview** (the states:
one sentence, action, whether they change over time) · **How states are assigned** (a
visual flow of the 6 ordered questions, the exact tests, terms) · **Worked examples** (CC
only: month-by-month coloured journeys) · **Thresholds** (plain names, value, why) ·
**Buckets & segments** (CC vs RL, the ceiling) · **Data handling** · **Results** (counts
per product × segment × state; shares and coverage are formulas). Rules, thresholds and examples are read
from the deployed engine, so the workbook cannot drift from the pipeline; the build fails
if an example no longer gets the state it illustrates. The old "Rule tester" sheet is gone
(it was a second copy of the rules in Excel formulas and had drifted), and so is roll rate
(circular: measured on the months that define the state).

Reference copy (layout and content, Results left empty — the real counts come from your
PROD JSONs): `docs/deterioration_states/spark/stakeholder/dpd_deterioration_states_reference.xlsx`
on GitHub (branch `feat/dpd-deterioration-states`). It is not inside BUNDLE.md (binary).

**You, in PROD first** (after P10 is deployed), once per segment run of Node 2:
1. Extract the bundle to a temp folder (P10 step 1), then in the Kedro session:
   `sys.path.insert(0, "<temp>/spark"); from prod_check import report`
2. After the 60_180 run: `report(catalog, save_json="dpd_journey_results_60_180.json")`;
   after the 180_plus run: `report(catalog, save_json="dpd_journey_results_180_plus.json")`.
   The JSONs hold counts only (no account ids, no DPD histories).
3. Put both JSONs where Sonnet can read them (e.g. next to the old workbook) and paste P11.

```
Context: the DPD-journey deterioration pipelines (CC + RL) in
src/enbd_collections/pipelines/crx_persona/ are up to date with
docs/deterioration_states/BUNDLE.md (P10 done). The stakeholder workbook
<PATH>/dpd_states_review_20261016.xlsx is outdated. Rebuild it with the bundled generator.
Results JSONs (aggregates from PROD): <PATH>/dpd_journey_results_60_180.json and
<PATH>/dpd_journey_results_180_plus.json. Scoring date: <Mon YYYY>.

Hard rules:
- No PROD data access: never call catalog.load, never run kedro run, never query a table.
- Extract the bundle OUTSIDE the repo (a temp folder) and delete it at the end. Do not add
  the generator script to the repo.
- Never hand-edit rule text, thresholds or examples in the workbook: they come from the
  engine. Never type numbers into Results: they come from the JSONs.
- Do not delete the old workbook; do not commit or push.

Step 1 — extract and check
1. T=$(mktemp -d); create $T/extract_bundle.py from BUNDLE.md's "Extractor" section;
   python $T/extract_bundle.py docs/deterioration_states/BUNDLE.md $T  -> "0 mismatched".
2. From the repo root, confirm the generator will use the DEPLOYED engine:
   python -c "from enbd_collections.pipelines.crx_persona import _dpd_journey as J; print(J.STATES)"
   -> the 7 states. If the import fails, STOP and tell me (do not let it fall back to the
   bundled copy).

Step 2 — read the old workbook (report only)
Open <PATH>/dpd_states_review_20261016.xlsx (openpyxl or markitdown) and list anything it
holds that the new workbook does not cover — e.g. stakeholder names, owner decisions,
comments, extra notes. Do NOT carry over: the 'Rule tester' sheet, roll rates, 'Not
classified — history starts delinquent', option A/C states, or the 16-Oct shares (they
predate the Unknown / 180+ rules). STOP — show me the list and wait.

Step 3 — build
From the repo root:
python $T/spark/stakeholder/build_states_workbook.py \
    --out <PATH>/dpd_deterioration_states_<YYYYMMDD>.xlsx \
    --results <PATH>/dpd_journey_results_60_180.json \
    --results <PATH>/dpd_journey_results_180_plus.json \
    --scoring-date "<Mon YYYY>"
If it stops with "example ... now gives ...", STOP and report it verbatim — the deployed
engine differs from the bundle; do not edit the examples.
If I approved items in step 2, add them ONLY as a new last sheet "Notes" (plain text,
Arial 10, short, business wording), never by editing the generated sheets.

Step 4 — verify and report
1. Sheet names: Overview, How states are assigned, Worked examples, Thresholds,
   Buckets & segments, Data handling, Results (+ Notes if added).
2. Results: for each product x segment, the account counts in the sheet equal the JSON
   state_counts (print a small comparison table); every state present; RL/CC 180+ blocks
   filled if their JSON had them, otherwise yellow and empty (say which).
3. If LibreOffice is available: recalculate (soffice --headless --convert-to xlsx) and
   confirm no #DIV/0!, #REF!, #NAME?. Otherwise say that Excel computes the shares on open.
4. Delete $T. Report the output path, and git status --short (the xlsx may be untracked).
```

`````

### FILE: `dpd_states/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `dpd_states/config.py`
sha256 `a35ec3ac537f61917e811a330c810f28994972bbddb762844b0bd3676df7004e` · 99 lines · trailing newline: yes

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


# The source may itself be a fixed-length extract (the sign-off file pivots every account
# onto a fixed grid). A string that fills the whole window may have older history, so
# it is treated as cropped (never EPD, never "history starts delinquent"). None = full history.
SOURCE_WINDOW_MONTHS = None          # the sign-off file now carries full history

_reliable = _months_between(RELIABLE_FROM, SNAPSHOT_MONTH) if RELIABLE_FROM else None   # 32
MAX_HISTORY_MONTHS = min(x for x in (_reliable, SOURCE_WINDOW_MONTHS) if x) if (_reliable or SOURCE_WINDOW_MONTHS) else None   # 24

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
sha256 `5cf855512d12b36c7b7028a8e4a14e03305a0e951d5f1181cdcd1196bfc937c3` · 180 lines · trailing newline: yes

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


def journey_features(dpd: str, cap: int = 9) -> dict:
    """cap: the ceiling bucket (CC 9). A hold at the ceiling is not a payment (the bucket
    cannot rise), so it does not count in spell_pay_events."""
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
        "spell_pay_events": int(((sp_c != R) & ~((sp_c == H) & (b[t0 + 1:sp_end] >= cap))).sum()),
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
        "starts_delinquent": bool(b[0] >= 2),           # oldest observed month already delinquent
        "n_glitches": n_glitches,
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


def build_features(df: pd.DataFrame, col: str = "dpd_string", cap: int = 9) -> pd.DataFrame:
    if len(df) == 0:
        raise ValueError("build_features got an empty frame — check the spine filter / sample")
    feats = pd.DataFrame([journey_features(s, cap) for s in df[col]], index=df.index)
    return pd.concat([df, feats], axis=1)
`````

### FILE: `dpd_states/states.py`
sha256 `35c8cf04760bff030a95a9671663801e95cace608d0de87c046ecd7efceb5eb9` · 204 lines · trailing newline: yes

`````python
"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q0  Journey start observed?   the OLDEST OBSERVED month is already at bucket 2+ (a spell
                                older than the window / floor, a restructured account
                                re-opened at its old bucket, migrated or missing history):
                                how the account fell in is not visible, so every
                                fall-in state would be a guess. Stabilized needs only
                                the last 6 months, so it is still assigned; otherwise
                                                               -> unknown
    Q1  Early payment default?  <=3 months of history before this spell (at most one
                                blip inside it, no earlier real spell) AND never paid
                                since crossing bucket 2: every month of the spell a
                                roll, still falling; and the string was not cropped (it
                                must start at the first billed month) -> early_payment_default
    Q2  Stabilized?             today's bucket <= 7 (151-180 DPD; RL <= 6) — never at 180+ —
                                AND 5 of the last 6 months within
                                today's bucket ±1, OR (>= 6 months since first reaching 4
                                AND at most 1 bucket higher than 6 months ago) -> stabilized
    Q3  Paying since 4?         [tested, NOT recommended] paid >= half a month's
                                due per month since first reaching 4 -> paying_since_4
    Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3, cured, and
                                ended within 12 months before this spell started
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
    "repeat_window_months": 12,     # [business] earlier spell ended <= 12 months before this one
    "seasoned_min_months": None,    # [business] e.g. 12 -> split straight roller (first year = early life)
    "split_slow_roller": False,     # True -> split slow roller by 2+ month payments in run-up
    # [business] Stabilized only up to bucket 7 (151-180 DPD; RL 6): never in the 180+
    # segment, where a hold at the ceiling is not a payment.
    "stabilized_max_bucket": 7,
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12},
    "C_detailed_7": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12, "split_slow_roller": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["unknown", "early_payment_default", "stabilized", "paying_since_4",
               "repeat_delinquent", "straight_roller", "straight_roller_seasoned",
               "straight_roller_early_life", "slow_roller", "slow_roller_intermittent",
               "slow_roller_erratic"]
# States that never change once the account is past bucket 4 (how they fell in). EPD is
# not one of them: it ends the month the account pays. Stabilized / paying_since_4 describe
# current behaviour. A fixed state may legitimately move INTO stabilized.
FIXED_STATES = [s for s in STATE_ORDER
                if s not in ("unknown", "early_payment_default", "stabilized", "paying_since_4")]
CURRENT_STATES = ["stabilized", "paying_since_4"]

# Business labels (common card-risk / collections terms). Change freely: code never
# reads these, so renaming for the risk team cannot break the pipeline or old results.
DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
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
    "unknown": "The oldest observed month is already delinquent, so how the account fell in "
               "is not visible: a spell older than the history window / floor (common at 180+), "
               "a restructured card/loan re-opened at its old bucket, a migrated account or "
               "missing history. Stabilized is still assigned (it needs only the last 6 months).",
    "early_payment_default": "Never paid since crossing bucket 2 and still falling, at most 3 months "
                             "after the first bill. Called 'bust-out' internally — but classic bust-out "
                             "fraud (good history, limit build-up, then max-out) shows as a seasoned "
                             "straight roller and needs a fraud overlay on spend data.",
    "stabilized": "The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months since "
                  "first reaching 4, at most one bucket higher than 6 months ago) so oscillating "
                  "payers and accounts that just paid down are not mislabelled.",
    "paying_since_4": "Rejected — current-behaviour state that belongs to credibility (money coming in).",
    "repeat_delinquent": "Re-default within 12 months of curing a spell that reached bucket 3; "
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
    out = ["unknown", "early_payment_default", "stabilized"]
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
    stab = (f.last6_in_band >= p["stabilized_min_in_band"])
    if p["stabilized_long_run_months"] is not None:
        stab |= ((f.months_since_4 >= p["stabilized_long_run_months"])
                 & (f.chg_6m <= p["stabilized_long_run_max_rise"]))
    stab &= f.b_now <= p["stabilized_max_bucket"]
    add(f.starts_delinquent & stab, "stabilized")
    add(f.starts_delinquent, "unknown")
    add((f.months_before_spell <= p["epd_max_history"]) & (f.n_blips <= p["epd_max_blips"])
        & (f.n_prior_episodes == 0) & (f.spell_pay_events == 0) & ~cropped, "early_payment_default")
    add(stab, "stabilized")
    if p["paying_since_4_min_rate"] is not None:
        add(f.post4_paid_rate >= p["paying_since_4_min_rate"], "paying_since_4")
    if p["repeat_min_prior_peak"] is not None:
        gap = f[f"gap_prior_peak{min(max(int(p['repeat_min_prior_peak']), 2), 4)}"]
        add(gap <= p["repeat_window_months"], "repeat_delinquent")
    if p["seasoned_min_months"] is not None:
        # a cropped string means the account is older than the window: seasoned
        add(fast & ((f.months_before_spell >= p["seasoned_min_months"]) | cropped), "straight_roller_seasoned")
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
sha256 `2bf13fa9f0eb9d2eac4305443e2d9e33f683d2ad3e161a96c424fe1e5adadd37` · 568 lines · trailing newline: yes

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
    """Keep the newest max_len months (leftmost digits) — history older than the window is
    dropped. A string that fills the whole window may have older history, so it is flagged
    as cropped too (>=). Returns (cropped strings, cropped flag)."""
    if not max_len:
        return s, pd.Series(False, index=s.index)
    return s.str[:max_len], s.str.len() >= max_len


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
    r = f[~a_states.isin(["early_payment_default", "stabilized", "unknown"])]
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
sha256 `4893508026c0c612db4002630ef45dec26a7ef8dcd8e89f676b3c527b07a09eb` · 349 lines · trailing newline: yes

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
    allowed = [s for s in option_states(option) if s != "unknown"]
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
    x = c.loc[[s for s in c.index if s in FIXED_STATES and s != "unknown"],
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
    ("E04", "Uncropped histories that start already delinquent (part of unknown)",
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
     "last 12 months, which lowers the overlap).",
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

### FILE: `dpd_states/segment_180.py`
sha256 `c4e75922ac7cf72143fd49a315606822b46762b105238902b2dab49279c138f2` · 156 lines · trailing newline: yes

`````python
"""180+ segment (current bucket 8 or 9; 9 is the cap) — synthetic generator and run.

The 180+ segment uses the SAME state tree and vocabulary as the 60-180 spine (states.py,
option B): unknown, early_payment_default, stabilized, repeat_delinquent,
straight_roller_seasoned / _early_life, slow_roller. Two rules make it valid at 180+:
  * stabilized only up to bucket 7 (151-180 DPD) — never at 180+;
  * a hold AT the ceiling (9 -> 9) is not a payment (features.py, cap=9), so EPD still
    means "never paid since crossing bucket 2".
Accounts whose window is all 8/9 start delinquent -> unknown.

Plus an attribute, not a state: time in default (months since first reaching 8), banded.

    python docs/deterioration_states/run.py s180            # synthetic run, three time-at-9 scenarios
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import synth
from .analysis import crop_history, md
from .features import _runs, build_features, encode
from .states import OPTIONS, RECOMMENDED, assign_states, option_states

DEFAULT_TOP = 9
from .config import MAX_HISTORY_MONTHS as WINDOW   # reliable history window (32 months)


# --- synthetic 180+ lifecycles -----------------------------------------------------------

def _to_default(path: list[int], rng, median_months_at_9: float) -> tuple[list[int], str]:
    """Continue a lifecycle that reached 8 into the 180+ segment: 9, then months at 9 until
    write-off / end of observation, with rare 'paying in default' events."""
    tag = ""
    path.append(DEFAULT_TOP)
    months = int(np.clip(rng.gamma(1.5, median_months_at_9 / 1.2), 1, 96))
    for _ in range(months):
        if rng.random() < 0.012:                     # paid several months at once
            drop = int(rng.integers(1, 4))
            path.append(DEFAULT_TOP - drop)
            tag = "paid_in_default"
            while path[-1] < DEFAULT_TOP:            # rolls back up unless it keeps paying
                path.append(path[-1] + 1)
        else:
            path.append(DEFAULT_TOP)
    return path, tag


def _broken_payer(rng) -> list[int]:
    """Stabilized for a long time in 4–7, then the arrangement / capacity broke: rolls to 9."""
    path = synth._normal(rng, synth._tenure(rng, lo=6))
    synth._roll_to(path, int(rng.choice([4, 5, 6], p=[0.6, 0.3, 0.1])))
    for _ in range(int(rng.integers(8, 30))):
        b, u = path[-1], rng.random()
        path.append(b if u < 0.8 else (b + 1 if u < 0.9 and b < 7 else max(b - 1, 4)))
    synth._roll_to(path, 8)
    return path


def generate_180(n: int = 20_000, median_months_at_9: float = 12, seed: int = 7,
                 share_no_history: float = 0.03) -> pd.DataFrame:
    """Snapshot of the 180+ segment: accounts whose current bucket is 8 or 9, sampled in
    proportion to the months they spend there, history cropped to the reliable window."""
    rng = np.random.default_rng(seed)
    names = list(synth.ARCHETYPES) + ["broken_payer"]
    w = np.array([synth.ARCHETYPES[k][0] for k in synth.ARCHETYPES] + [0.03])
    pool_names = rng.choice(names, size=4 * n, p=w / w.sum())
    pool, tags = [], []
    for k in pool_names:
        p = _broken_payer(rng) if k == "broken_payer" else synth.ARCHETYPES[k][1](rng)
        if p[-1] < 8:                                # lifecycle ended before 180+ (cure / settle)
            synth._roll_to(p, 8)
        p = p[:next(i for i, x in enumerate(p) if x >= 8) + 1]
        p, tag = _to_default(p, rng, median_months_at_9)
        pool.append(p)
        tags.append(tag)
    months = np.array([sum(1 for x in p if x >= 8) for p in pool], dtype=float)
    chosen = rng.choice(len(pool), size=n, replace=False, p=months / months.sum())
    rows = []
    for j in chosen:
        p = pool[j]
        t = int(rng.choice([i for i, x in enumerate(p) if x >= 8]))
        hist = p[:t + 1]
        label = pool_names[j]
        if DEFAULT_TOP in hist and min(hist[hist.index(DEFAULT_TOP):]) < DEFAULT_TOP:
            label = "paid_in_default"                # the payment is visible in this snapshot
        rows.append({"dpd_string": "".join(map(str, reversed(hist))), "planted": label})
    df = pd.DataFrame(rows)
    nh = rng.random(len(df)) < share_no_history          # migrated / no history: all 9s
    df.loc[nh, "dpd_string"] = df.loc[nh, "dpd_string"].map(lambda s: "9" * min(len(s), int(rng.integers(3, 25))))
    df.loc[nh, "planted"] = "no_history"
    return df


# --- 180+ features and states -------------------------------------------------------------

def features_180(df: pd.DataFrame, window: int = WINDOW) -> pd.DataFrame:
    s, cropped = crop_history(df.dpd_string, window)
    f = build_features(df.assign(dpd_string=s, history_truncated=cropped))
    extra = []
    for x in f.dpd_string:
        b, d, c = encode(x)
        sp0 = _runs(b >= 2)[-1][0]
        first8 = int(np.argmax(b >= 8))
        first9 = int(np.argmax(b >= 9)) if (b >= 9).any() else None
        # payment events from spell start until first reaching 9 (holds at the cap are not payments)
        upto = (first9 if first9 is not None else len(b) - 1)
        pre9 = c[max(sp0 - 1, 0):upto]
        after9 = d[first9:] if first9 is not None else np.array([])
        # was stabilized (bank rule: 5 of 6 within ±1) at some month while in 4–7, for 6+ months
        stab_months = 0
        for t in range(sp0, first8):
            if 4 <= b[t] <= 7 and t >= 5 and (np.abs(b[t - 5:t + 1] - b[t]) <= 1).sum() >= 5:
                stab_months += 1
        extra.append({"all_default": bool(set(x) <= {"8", "9"}),
                      "months_in_default": len(b) - 1 - first8,
                      "default_left_censored": first8 == 0,
                      "pay_events_before_9": int((pre9 != 1).sum()),
                      "paid_in_default": bool((after9 < 0).any()),
                      "stabilized_months_in_4_7": stab_months})
    return pd.concat([f, pd.DataFrame(extra, index=f.index)], axis=1)


def assign_180(f: pd.DataFrame) -> pd.Series:
    """The SAME tree and vocabulary as the 60-180 spine (option B). Stabilized cannot occur
    (bucket <= 7 only) and holds at the ceiling are not payments (features, cap=9)."""
    return assign_states(f, **OPTIONS[RECOMMENDED])


def default_band(f: pd.DataFrame) -> pd.Series:
    m = f.months_in_default
    return pd.Series(np.select([f.default_left_censored, m < 6, m < 12],
                               [f"{WINDOW - 1}+ (since before window)", "0–5", "6–11"], "12+"),
                     index=f.index)


ORDER = option_states(RECOMMENDED)


def main(n: int = 20_000) -> None:
    synth.calibrate(n=6000, iters=5)
    for med in (6, 12, 24):
        df = generate_180(n, median_months_at_9=med)
        f = features_180(df)
        st = assign_180(f).rename("state")
        band = default_band(f).rename("time_in_default")
        share = st.value_counts(normalize=True).reindex(ORDER).fillna(0).rename("share")
        print(f"\n=== typical (median) time at 9 = {med} months · {len(df):,} accounts · window {WINDOW} ===")
        print(md(share.to_frame()))
        print("\nTime in default (months since first reaching 8):\n")
        print(md(band.value_counts(normalize=True).rename("share").to_frame()))
        if med == 12:
            print("\nState × time in default (row shares):\n")
            print(md(pd.crosstab(st, band, normalize="index").reindex(ORDER).dropna(how="all")))
            print("\nPlanted pattern → state (row shares):\n")
            print(md(pd.crosstab(df.planted, st, normalize="index")[[c for c in ORDER if c in set(st)]]))
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
sha256 `6b199dd89eff692fea775301533570f6ca0838952eefa5d78cff9e7b3c019a56` · 180 lines · trailing newline: yes

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
    ("4 5 6 7", "unknown", "string starts delinquent (restructured / missing history)"),
    ("4 4 4 4 4 5", "stabilized", "starts delinquent but holding: stabilized needs only 6 months"),
    ("0 0 0 2 3 4 4 4 4 4", "stabilized", "journey observed from 0 DPD, holding at 4"),
    ("0000000000000000224", "straight_roller_seasoned", "+2 jump after a hold at 2: repaired to 2 3 4"),
    ("00000000000000002244", "straight_roller_seasoned", "same account a month later: fixed state must not change"),
    ("000034", "straight_roller_early_life", "jump from clean to 3: no clean month is borrowed"),
    ("0 2 3 4" + " 0" * 20 + " 2 3 4", "straight_roller_seasoned", "cured 20 months earlier: outside 12-month window"),
    ("0 2 3 4" + " 0" * 8 + " 2 3 4 5", "repeat_delinquent", "cured 8 months earlier: repeat delinquent"),
    ("0000000000000000 2 3 4 4 0 4 5", "stabilized", "single 0 inside a spell at 4 is a glitch, not a cure"),
    ("0000 3 0000000000000 2 3 4", "straight_roller_seasoned", "single spike 0 3 0 is a glitch, not an earlier spell"),
]


CROP_CASES = [   # (oldest -> newest, max months kept, expected option-B state, why)
    ("0" * 10 + "234" + "45" * 18 + "4", 32, "stabilized",
     "spell older than the window: not a data-quality case; long-run holder -> stabilized"),
    ("0" * 40 + "234", 32, "straight_roller_seasoned", "long clean history cropped: still seasoned"),
    ("0000000000234", 6, "straight_roller_seasoned", "cropped to 0 0 0 2 3 4: looks like EPD, but older than the window"),
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
sha256 `e53b3ecdfb16870b036b9b2e3365b285a77124881ebc61c8a0148abc67fdbeb3` · 274 lines · trailing newline: yes

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
    "dpd_states/segment_180.py",
    "dpd_states/discover.py",
    "dpd_states/synth.py",
    "dpd_states/run_synthetic.py",
    "dpd_states/selftest.py",
    "dpd_states/bundle.py",
    "snippets/dpd_states_validate.py",
    # PySpark / Kedro pipeline for the workplace (CC + RL) — review, engine, nodes, tests
    "spark/REVIEW_SPARK.md",
    "spark/conf/parameters_crx_persona_dpd_journey.yml",
    "spark/crx_persona/__init__.py",
    "spark/crx_persona/_dpd_journey.py",
    "spark/crx_persona/cc_full_history/__init__.py",
    "spark/crx_persona/cc_full_history/nodes.py",
    "spark/crx_persona/rl_full_history/__init__.py",
    "spark/crx_persona/rl_full_history/nodes.py",
    "spark/crx_persona/cc_a4_deterioration/__init__.py",
    "spark/crx_persona/cc_a4_deterioration/nodes.py",
    "spark/crx_persona/cc_a4_deterioration/pipeline.py",
    "spark/crx_persona/rl_a4_deterioration/__init__.py",
    "spark/crx_persona/rl_a4_deterioration/nodes.py",
    "spark/crx_persona/rl_a4_deterioration/pipeline.py",
    "spark/tests/test_parity.py",
    "spark/tests/test_spark_e2e.py",
    "spark/tests/conftest.py",
    "spark/tests/nodes/crx_persona/conftest.py",
    "spark/tests/nodes/crx_persona/test_dpd_journey.py",
    "spark/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py",
    "spark/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py",
    "spark/prod_check.py",
    "spark/stakeholder/build_states_workbook.py",
]
EMPTY_DIRS = ["results", "validation"]

LANG = {".py": "python", ".md": "markdown", ".yml": "yaml"}

EXTRACTOR = '''"""Recreate docs/deterioration_states/ from BUNDLE.md and verify every file.

Run from the repo root, in this order:

    1. python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md
         -> must end with "N files OK, 0 mismatched"
    2. python -m pip install pandas numpy scikit-learn openpyxl      (once)
    3. python docs/deterioration_states/run.py selftest
         -> must end with "SELFTEST PASSED" (~1 minute)
    4. python docs/deterioration_states/run.py validate
         -> checks + state shares on data/input/dpd_synthetic_data.xlsx (config.py)
    5. optional: python docs/deterioration_states/run.py synthetic
    Spark mode later: snippets/dpd_states_validate.py, main(catalog) (PROMPTS.md P6)
    PySpark pipeline (CC + RL): read spark/REVIEW_SPARK.md, then
       python docs/deterioration_states/spark/tests/test_parity.py   -> "PARITY PASSED"

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
    print("Next, from the repo root: python docs/deterioration_states/run.py selftest")
    print("then:                     python docs/deterioration_states/run.py validate")
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
# 1. recreate every file and verify checksums      -> "N files OK, 0 mismatched"
python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md

# 2. dependencies (once)
python -m pip install pandas numpy scikit-learn openpyxl

# 3. self-test on synthetic data                    -> "SELFTEST PASSED"  (~1 min)
python docs/deterioration_states/run.py selftest

# 4. validate on the real file                      -> checks + state shares
#    reads data/input/dpd_synthetic_data.xlsx, column dpd_history_str (config.py),
#    crops to the reliable history window (2024-01 .. 2026-08 = 32 months), keeps buckets 4-7
python docs/deterioration_states/run.py validate
#    another file and/or sample size:
#    python docs/deterioration_states/run.py validate data/input/other_file.xlsx 50000

# 5. optional: synthetic method-validation report
python docs/deterioration_states/run.py synthetic

# 6. PySpark pipeline (CC + RL) — review + rewrite: read spark/REVIEW_SPARK.md first
python docs/deterioration_states/spark/tests/test_parity.py      # -> "PARITY PASSED" (no Spark, ~30 s)
python docs/deterioration_states/spark/tests/test_spark_e2e.py   # -> "SPARK E2E PASSED" (local Spark + Java 17)
```

**For the PySpark pipeline, start at `spark/REVIEW_SPARK.md`** — findings on the workplace
code (F1–F12), the rewrite design, the coverage plan (99.9%) and the shipping steps (§5).
Roles: the workplace assistant has **no PROD data access** — it edits code and runs the
offline tests only (S1–S4, never `catalog.load`). The user runs the pipelines in PROD and
then `spark/prod_check.py` (P1–P2), which prints aggregates only. The copy-paste prompt for the assistant is **PROMPTS.md P8**; **P9** adds the tests to `src/tests/` and cleans up afterwards; **P10** moves the repo to one state vocabulary for both segments (no stabilized at 180+); **P11** rebuilds the stakeholder workbook.

Step 1 needs `extract_bundle.py` — create it from the **Extractor** section below the first
time. Step 4 prints the checks between `=== DPD_STATES OUTPUT START ===` and `END` and writes
`docs/deterioration_states/results/dpd_states_file_<file>_<date>.json` + `.md` (aggregates
only) — paste the printed block back, or follow PROMPTS.md P0 -> P2 with Sonnet.

If it fails: "column ... not in" -> check COL_DPD in `dpd_states/config.py`; "look like
numbers" -> the Excel column is stored as numbers (digits lost), re-save it as text;
"No module named openpyxl" -> step 2; snapshot not Aug 2026 -> set SNAPSHOT_MONTH in config.

Spark mode (later, for outcomes / production), in a Kedro notebook — PROMPTS.md P6:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
from dpd_states_validate import main
main(catalog, check_only=True)   # dry run: schema, counts, orientation (aggregates)
result = main(catalog)           # full validation incl. backtest -> results/
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

### FILE: `spark/REVIEW_SPARK.md`
sha256 `34bb4033f53c46047fc7353afc634899abb710dd0289a43573825a6f513f1e6c` · 283 lines · trailing newline: yes

`````markdown
# PySpark deterioration pipeline — review and rewrite (CC + RL)

Reviewed from 15 screenshots (Oct 2026) of `src/enbd_collections/pipelines/crx_persona/`:
`cc_full_history/nodes.py`, `rl_full_history/nodes.py`, `cc_a4_deterioration/{nodes,pipeline}.py`,
`rl_a4_deterioration/pipeline.py`, `_dpd_journey.py` (`resolve_gaps`, `encode_transitions`).
**Not seen:** `classify_from_grid`, `BucketScheme`, `_log_*` bodies, the start of
`build_cc_full_history`. Findings about those are marked *(inferred)*.

**Verdict:** the code is careful and well documented, but it has three correctness problems
that change states — dropped accounts (F7), no cropped flag behind the CC floor (F8), and
glitch/repair results that differ from the signed-off reference (F9). Fixing them inside the
window-function design is hard, so the logic is **rewritten**: Spark scopes the data and
makes **one shuffle**, then a plain-Python port of the reference runs per account. Parity
with the reference is tested (0 mismatches), and so is the Spark pipeline end to end.

---

## 1. Findings

| # | Where | Severity | Finding | Fix (in this folder) |
|---|---|---|---|---|
| F7 | `resolve_gaps` | **High** | An account with any gap whose two neighbours differ is **dropped**. Real CC run: 17,675 of 192,587 (9.2%) gone — the output no longer covers the spine. Causes, roughly in order of likely size: (a) **billing-cycle shift**: a cycle date near month-end puts two bills in one month and none in the next; the month dedupe throws one bill away and leaves a hole; (b) **CC 0 vs 1** compared natively — both mean clean, yet `0 _ 1` counts as a disagreement; (c) **straight-roll gaps** `3 _ 5` (only one path is possible); (d) short ambiguous gaps `3 _ 4`. | Cycle-shift repair, canonical comparison, straight-roll fill, inference for gaps ≤ 2 months (all counted per account), and **truncate instead of drop**: keep the months after an unresolvable gap, flag `history_cropped`, still classify. No account with rows is dropped. |
| F8 | `build_cc_dpd_sequences` (+ `classify_from_grid`, *inferred*) | **High** | The 2024-01 floor removes older months, but Node 1's output has **no "cropped" flag**. In the reference, a cropped history can never be EPD, and a cropped straight roller is seasoned. Without the flag, a card opened in 2019 whose spell started in Mar 2024 has `months_before_spell = 2` → labelled **EPD**; a 2019 card that rolled in Jun 2024 → **early-life**. (Synthetic: 74% of spine histories are cropped by a 32-month window.) | `history_cropped` uses dates, which is better than the reference's length heuristic: the first raw bill is before the floor, or the history was truncated at a gap, or the first month is the very first month of the source. |
| F9 | `encode_transitions` | **High** | Glitch fix and +2 repair use `lag`/`lead` on the unfixed column. The reference loops and **cascades**: a fixed month feeds the next comparison. The docstring calls this a "known, flagged divergence". It changes states for chains of artefacts, and nobody has measured by how much. | Exact loop port. `tests/test_parity.py`: 20,000 spine accounts × options A/B/C, the same accounts in RL numbering, 8,000 accounts at 180+, and 56 business cases — **0 mismatches** on every feature and state. |
| F3 | `resolve_gaps` dedupe | Medium | The month dedupe keeps the latest `obs_date` **even when its bucket is NULL** (an unparseable `add_info`). A valid bill earlier that month is lost, the month becomes a gap, and the account may be dropped. | NULL / out-of-range buckets are removed before the dedupe and counted (`n_invalid_rows`). |
| F2 | `build_cc_full_history` | Medium | `dropDuplicates(["account_id","billing_date"])` keeps an **arbitrary** row: two runs can give different buckets, and a NULL row can win. | `groupBy(...).agg(max(dlq_bucket))`: deterministic, the worst non-NULL bucket wins. |
| F1 | `build_cc_full_history` | Medium | `regexp_extract(...).cast("int")`: no match gives `""`. That casts to NULL with ANSI off, but **fails the job** with ANSI on (the default from Spark 4 / some CDP profiles). | `when(x != "", x.cast("int"))`. |
| F4 | `build_rl_full_history` | Medium | `rl_spine.account_id.cast("string")`: if the spine key is a double, the cast gives `"1.23456789E8"` and the leftsemi join **silently matches nothing**. This is the trap the CC node's own comment warns about. | A double or decimal key is cast to long first, then trimmed to string. Tested: 100/100 matched. |
| F5 | `build_rl_full_history` | Low–Med | "No broadcast — rl_spine is model-sized" — that is exactly when to broadcast. ~31k keys is under 1 MB. Without the hint, Spark cannot estimate the size of a `distinct()` and may **shuffle all of `int_loan_master`**. | `F.broadcast(spine_keys)`. |
| F6 | `_log_stats`, `_log_sequence_stats`, `_log_state_stats` | Low–Med | Logging inside a node runs extra jobs. Without `persist()`, Kedro then recomputes the whole node to save the output — each node can run 2–4 times. | Opt-in (`dpd_journey.log_stats`): one `agg` job each, after `persist()`. |
| F10 | `build_cc_a4_deterioration` | Low–Med | An account is in the spine if its **latest grid row** is 4–7, even when that row is months old (frozen or closed accounts). Accounts excluded for this reason are not counted. | `history_stale_months` column (snapshot month − last observed month); Node 1 keeps every account with a `build_status`. |
| F11 | constants | Low | `_CC_HISTORY_FLOOR_DATE` and `_DET_OPTION` are code constants. The floor is temporary, so lifting it should be a config change, not a code change. | Moved to params (`conf/parameters_crx_persona_dpd_journey.yml`). |
| F12 | structure | Low | CC and RL are two near-copies of the same logic, with thresholds hand-ported ("CC ≥3, RL ≥2"). | One engine. RL is mapped onto the CC scale with **+1** (RL 0 → 1 = clean, RL 7 → 8 = 180+), so every threshold is written once. |

### Rule changes agreed after the review (Oct 2026) — in the engine AND the reference

| Rule | Why | Effect (synthetic) |
|---|---|---|
| **One tree, one vocabulary for both segments** (option B only) | The 180+ prototype had its own tree (`paying_in_default`, `broken_payer`), and options A / C added states production never uses (`straight_roller`, `slow_roller_intermittent` / `_erratic`) plus a dead one (`paying_since_4`). Now 60–180 and 180+ share the same 7 states: `unknown`, `early_payment_default`, `stabilized`, `repeat_delinquent`, `straight_roller_seasoned`, `straight_roller_early_life`, `slow_roller`. The segment only decides which accounts are classified. `det_option` / `det_state_option` are gone. | — |
| **Stabilized never at 180+** (only up to CC 7 / RL 6 = 151–180 DPD) | At the ceiling (CC 9, RL 7) the bucket cannot rise, so `9 9 9` looks like a hold although nothing was paid; at 180+ a hold is not a meaningful "stabilized" signal. | 180+: 0% stabilized; 60–180 unchanged |
| **Holds at the ceiling are not payments** | Same reason. Without it, EPD would fail for every account that has sat at the cap for a month. A move down from the cap (9 → 8) is still a payment. | — |
| **Unknown** replaces `history_starts_delinquent` and `history_not_available` | If the oldest OBSERVED month is clean (0 DPD), the whole current journey is seen and the fall-in states are confident. If it is already delinquent (spell older than the window / CC floor, restructured, migrated, missing), they would be guesses. Stabilized (60–180 only) still wins: it needs only the last 6 months. | 60–180: 3.3% unknown with the 32-month window; 180+: 17–32% unknown depending on time at 9 |

New output column `starts_delinquent` (oldest observed month at canonical 2+). A stale
`dpd_journey` parameter (e.g. `det_option`) now raises an error instead of being ignored.

### Efficiency

Old Node 1 + Node 2 (from the screenshots): a groupBy for bounds, sequence/explode, a join
back, two windows, a filter, an anti-join, a groupBy, a join, several lag/lead windows, more
windows and groupBys in `classify_from_grid` *(inferred)*, a `row_number` window, a leftsemi
join and a restructure join. That is many shuffle stages over an (account × month) grid —
and each `_log_*` reruns all of it.

New: **Node 1 = one shuffle** (`groupBy(account_id)` that collects the month rows) plus a
1-row broadcast aggregate and the restructure join. **Node 2 = no shuffle** (filter + map).
Python work per account is about 30–60 list steps. At about 200k accounts that is seconds
of executor CPU. Local run (4 cores, 5k CC accounts + 2.5k RL, raw rows to states, ANSI on):
about 30 s, mostly Spark start-up.

---

## 2. Design

```
raw_stg_billing ──► build_cc_full_history ──► crx_cc_full_history ─┐
cc_spine ─────────┘   (F1, F2; NO floor here)                       ├► build_cc_dpd_sequences ─► crx_cc_dpd_sequences ─► build_cc_a4_deterioration ─► crx_cc_a4_deterioration
crx_cc_spell_table ─────────────────────────────────────────────────┘   (one row / account)          (one row / account in segment)

int_loan_master ──► build_rl_full_history ──► crx_rl_full_history ──► build_rl_dpd_sequences ─► crx_rl_dpd_sequences ─► build_rl_a4_deterioration ─► crx_rl_a4_deterioration
rl_spine ─────────┘   (F4, F5, F6)
```

**Bucket scale.** Every rule is written once, on the CC ("canonical") scale:
canonical = max(native + offset, 1), with CC offset 0 and RL offset 1.

| DPD | 0 | 1–30 | 31–60 | 61–90 | 91–120 | 121–150 | 151–180 | 181–210 | 210+ |
|---|---|---|---|---|---|---|---|---|---|
| CC native | 0 / 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 (cap) |
| RL native | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 (cap = 180+) | — |
| canonical | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 |

Segments: `60_180` = canonical 4–7 (CC native 4–7, RL native 3–6). `180_plus` = canonical
8+ (CC 8–9, RL 7). Both segments use the same state tree; the ceiling is CC 9 / RL 7.
Outputs carry native buckets (`dlq_buckets`, `current_bucket`). Feature names
keep the reference's names: `months_since_4` means months since first reaching canonical 4
(CC 4, RL 3, i.e. 61–90 DPD).

**Node 1 — `build_dpd_sequences`**: one row per account, every account in the history.

| column | meaning |
|---|---|
| `build_status` | `ok` / `no_rows_in_window` (all rows before the floor) / `no_valid_rows` / `dropped_unresolvable_gap` (only with `on_unresolvable_gap: drop`) |
| `first_month`, `last_month`, `history_months` | the kept window (month-end dates) |
| `dlq_buckets` | array<int>, native, oldest → newest, gap-filled |
| `dpd_string` | the same, as the bank's string (leftmost = latest month), for the file-mode validator |
| `history_cropped` | older history exists but is not used (floor, gap truncation, or starts at the source's first month) |
| `n_gap_months_filled` / `_rolled` / `_inferred` | gap months filled by: neighbours agree / straight roll / short-gap inference |
| `n_cycle_shift_moves`, `n_months_truncated`, `n_dup_month_rows`, `n_invalid_rows` | audit counts |
| `legacy_drop` | **the old rule would have dropped this account** — reconciles with the 17,675 |
| `restructure_blind_spot_flag` | CC: any spell `restructured_entry` (R13). RL: `is_restructured` in any month |

Gap rules, in order (all in `build_history`, all counted):

1. **Cycle shift.** A month with two bills next to an empty interior month gives one bill
   to that month. The earlier bill moves back if the previous month is empty, otherwise
   the later bill moves forward.
2. Dedupe: the latest bill in the month (ties → worst bucket).
3. **Neighbours agree** on the canonical scale → fill (hold, or clean through; CC 0 = 1).
4. **Straight roll** when `R − L = gap + 1` on the canonical scale → `L+1, L+2, …` (the only path without a +2 jump).
5. **Inferred** when the gap is ≤ `max_inferred_gap_months` (default 2): carry the left
   value, roll as late as possible (`3 _ 4 → 3 3 4`, `6 _ _ 3 → 6 6 6 3`). Note that an
   inferred month in a spell reads as a hold, i.e. a payment, so it can move an account
   out of EPD. That is why it is counted, and why the default is short.
6. Anything else → **truncate**: keep the months after the gap and flag `history_cropped`.

**Node 2 — `build_deterioration`**: filters `build_status = 'ok'` and today's segment.
Features and the state come from the reference port. Output columns: `account_id,
det_state, det_state_label, det_segment, current_bucket,
n_gap_months_filled, left_censored, months_before_spell, n_blips, n_prior_episodes,
gap_prior_peak3, spell_pay_events, runup_len, runup_pays, last6_in_band, months_since_4,
chg_6m, n_glitches, n_jumps_repaired, n_jumps_left, starts_delinquent, history_months,
history_cropped, n_months_truncated, history_stale_months, restructure_blind_spot_flag,
computed_at` — identical for both segments. Compared with the old schema: no
`det_state_option`; new `det_segment`, `current_bucket`, `n_jumps_left`,
`starts_delinquent`, `history_months`, `history_cropped`, `n_months_truncated` and
`history_stale_months`.

**Schema change:** `crx_*_dpd_sequences` changes from grain (account, month) to grain
(account) with an array. Its only consumer is Node 2. If anything else needs the long grid:

```python
seq.select("account_id", "first_month", F.posexplode("dlq_buckets").alias("t", "dlq_bucket")) \
   .withColumn("calendar_month", F.last_day(F.add_months("first_month", F.col("t"))))
```

**Python UDFs on the executors.** The per-account code is pickled **by value**
(`cloudpickle.register_pickle_by_value`, PySpark ≥ 3.3), so the executors do not need the
Kedro package installed. The local test proves this: the workers there cannot import
`crx_persona`. On PySpark < 3.3 the package must be importable on the executors (a wheel
or `--py-files`). If the cluster forbids Python UDFs entirely, keep the old window-function
code and apply F1–F8 and F10–F12 to it. F9 (exact parity) cannot be reached with
`lag`/`lead`; it would need Spark SQL `aggregate()` folds over the array.

---

## 3. Coverage — reaching 99.9%

Coverage = accounts classified ÷ accounts whose latest bucket is in the segment. With
`truncate`, every account with at least one valid row in the window is classified. So only
these lose coverage: `no_rows_in_window` (no bill since the floor), `no_valid_rows` (every
bucket NULL), and spine accounts missing from the history altogether (a key mismatch —
see `spine accounts found` in the RL log).

`prod_check.py` (run by you in PROD, §5 step P2) prints coverage per segment against the
99.9% target. It also reconciles with the old code: `old rule would have dropped` should
be close to 17,675 (same rule as the old `resolve_gaps`), followed by which new rule
rescued those accounts. If many are `truncated`, the gaps are long and real (missing
billing months) — ask the data owner before raising `max_inferred_gap_months`. The
truncated and cropped accounts should show state shares similar to the rest, apart from
fewer EPD / early-life (expected: they are cropped).

## 4. Tests

Shipped with the pipeline (P9 copies them to `src/tests/`; they import
`enbd_collections.pipelines.crx_persona` and need no bundle files):

| file | what | needs |
|---|---|---|
| `tests/nodes/crx_persona/test_dpd_journey.py` | 84 unit tests: business cases (CC + RL numbering), crop cases, ceiling / unknown, 180+, gap rules | nothing |
| `tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py` | 7 Spark tests: raw tables with real-source noise → node functions → every account checked; ANSI on | Java + pyspark |
| `tests/nodes/crx_persona/conftest.py` | local `spark` fixture (skip if `src/tests` has one) | |
| `tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py` | 5 wiring tests: node names, functions, inputs, outputs, tags, order, params | kedro |

Bundle-only (stay in BUNDLE.md): `tests/conftest.py` (maps the package name onto the staged
copy so the shipped tests run here), and:

```bash
python -m pytest docs/deterioration_states/spark/tests/nodes docs/deterioration_states/spark/tests/pipelines   # -> 96 passed
python docs/deterioration_states/spark/tests/test_parity.py     # no Spark: core vs numpy reference -> PARITY PASSED (~30 s)
python docs/deterioration_states/spark/tests/test_spark_e2e.py  # local Spark (Java 17, pyspark) -> SPARK E2E PASSED
```

The e2e test builds raw billing and loan-master tables from the synthetic generators, with
noise: same-day duplicates, unparseable `add_info`, cycle shifts, months missing between
equal neighbours, unresolvable 3-month gaps, history before the floor, and a double spine
key. It runs the actual node functions under ANSI mode and checks every account against
the expected state and cropped flag (CC 60–180, CC 180+, RL 60–180).

## 5. Shipping to the workplace repo

Two roles. **Sonnet** (workplace assistant): edits code and runs offline tests only — it
has no PROD data and must not load catalog datasets. **You**: run the pipelines in PROD
and paste the aggregate report back.

### Sonnet — code changes and offline tests (no catalog, no PROD data)

The whole sequence as one copy-paste prompt: **PROMPTS.md P8**. The steps below are the same, one at a time.

**S1 — unpack.** "Save BUNDLE.md raw at `docs/deterioration_states/BUNDLE.md`, create
`docs/deterioration_states/extract_bundle.py` from its Extractor section, run
`python docs/deterioration_states/extract_bundle.py docs/deterioration_states/BUNDLE.md`
— it must end with `0 mismatched`. Then run
`python docs/deterioration_states/spark/tests/test_parity.py` → must print `PARITY PASSED`.
If `pyspark` is missing, report it; do not change any code to work around it."

**S2 — impact scan, no edits yet.** "Read `docs/deterioration_states/spark/REVIEW_SPARK.md`.
In `src/enbd_collections/pipelines/crx_persona/`, list (a) every importer of
`_dpd_journey` and every name it imports (`grep -rn "_dpd_journey"`), (b) every dataset in
`conf/**/catalog*.yml` named `crx_cc_dpd_sequences`, `crx_rl_dpd_sequences`,
`crx_cc_a4_deterioration`, `crx_rl_a4_deterioration`, with format / partitioning / schema
settings, (c) every consumer of those four datasets in other pipelines, (d) the current
value of `_DPD_BUCKET_REGEX`. Report only — change nothing."

**S3 — apply.** "Replace, keeping the repo's own imports and conventions:
`crx_persona/_dpd_journey.py` ← `spark/crx_persona/_dpd_journey.py`;
`cc_full_history/nodes.py::build_cc_full_history`,
`rl_full_history/nodes.py::build_rl_full_history`, and `cc_a4_deterioration/nodes.py`,
`rl_a4_deterioration/nodes.py` ← the files under `spark/crx_persona/`. Keep the repo's
`_DPD_BUCKET_REGEX` value. If S2(a) found importers of names the new module no longer has
(`resolve_gaps`, `encode_transitions`, `classify_from_grid`, `BucketScheme` fields), stop
and show them to me. Merge `spark/conf/parameters_crx_persona_dpd_journey.yml` under the
existing `crx_persona:` block. If `rl_full_history`'s pipeline should pass
`params:crx_persona` (only needed for `log_stats`), add it. Update the catalog entries for
the two `*_dpd_sequences` datasets: the grain is now one row per account with an array
column `dlq_buckets` — drop any partitioning by month. Show me the full diff."

**S4 — offline verification.** "Run `python -m pytest` (or the repo's lint/test command)
on the changed files; run
`python -c "from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import create_pipeline as c; from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import create_pipeline as r; print(c().describe()); print(r().describe())"`;
and, if Java + local Spark work in the dev container,
`python docs/deterioration_states/spark/tests/test_spark_e2e.py 2000` → `SPARK E2E PASSED`
(synthetic data only). Report each result verbatim."

### You — in PROD, after Sonnet's changes are merged

**P1 — run.** First run on dev settings: `log_stats: true` in the params.

```bash
kedro run --pipeline=crx_cc_full_history       # whatever the repo calls the CC full-history pipeline
kedro run --pipeline=crx_cc_a4_deterioration
kedro run --pipeline=crx_rl_a4_deterioration    # after crx_rl_full_history
```

For the 180+ run, set `dpd_journey.segment: "180_plus"` (CC 8–9, RL 7) and re-run Node 2.
Node 1 does not depend on the segment.

**P2 — check.** In `kedro ipython` / a Kedro notebook:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "spark"))
from prod_check import report
report(catalog)                    # or report(catalog, products=("cc",))
```

It is read-only and prints aggregates only (counts and shares, no account ids or DPD
strings). Paste the block between `=== DPD_JOURNEY PROD CHECK START / END ===` back for
review.

**P3 — decide** (business owner): are truncated / inferred-gap accounts acceptable as
classified, and is the `unknown` share at 180+ acceptable as reported?

**P4 — tests and clean-up** (Sonnet, after P8): **PROMPTS.md P9** checks `src/` matches
the bundle, adds the regression tests (`spark/tests/nodes/crx_persona/` ->
`src/tests/nodes/crx_persona/`, `spark/tests/pipelines/crx_persona/` ->
`src/tests/pipelines/crx_persona/`; 96 tests), then removes everything unpacked from the
bundle except BUNDLE.md, plus dead code the rewrite left in `src/`.

## 6. Open points

- `BucketScheme` and `classify_from_grid` were not visible. If other pipelines import them,
  W1 lists those importers before anything is overwritten.
- CC bucket meaning is assumed as in the table above (CC 2 = 1–30 DPD = RL 1). The node
  thresholds in the screenshots ("CC ≥3 / RL ≥2", "CC ≥2 / RL ≥1") imply exactly this
  offset of 1.
- RL 180+ uses the 180+ prototype tree with cap RL 7. It has not been validated on RL
  data — the 180+ tree is a prototype for CC too.
- The cycle-shift rule assumes two bills in one month next to an empty month are one
  shifted cycle. If cycles legitimately double up (a product change, re-issue),
  `n_cycle_shift_moves` will be high on those accounts — check a few dozen.
`````

### FILE: `spark/conf/parameters_crx_persona_dpd_journey.yml`
sha256 `fc610b3b42a383d72f0bd6542b11c44ef2633d0ae4ab75bce6cbf81414dc5484` · 15 lines · trailing newline: yes

`````yaml
# Merge under the existing `crx_persona:` block (persona_start_date / persona_end_date stay
# as they are). Every key is optional; the values below are the code defaults.
crx_persona:
  dpd_journey:
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. Accounts with older history are flagged
    # history_cropped (never EPD / never "history starts delinquent"; straight rollers seasoned).
    cc_history_floor_date: "2024-01-01"
    rl_history_floor_date: null          # RL history is trusted in full
    segment: "60_180"                    # "180_plus" for the cc_180_plus / RL 180+ run
    on_unresolvable_gap: "truncate"      # truncate = keep months after the gap (flag cropped); drop = old behaviour
    fill_straight_roll_gaps: true        # 3 _ 5 -> 3 4 5 (the only path without a +2 jump)
    repair_cycle_shift: true             # 2 bills in one month next to an empty month: one belongs there
    max_inferred_gap_months: 2           # ambiguous gaps up to this length are inferred (carry, roll late); 0 = never
    log_stats: false                     # true: one extra aggregate job per node + persist
`````

### FILE: `spark/crx_persona/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `spark/crx_persona/_dpd_journey.py`
sha256 `64757dd76c8923a0b88def3fd19563d98861a3dc90d42d6fa30649dc77af1de5` · 674 lines · trailing newline: yes

`````python
"""DPD-journey deterioration states — one engine for credit cards (CC) and retail loans (RL).

Replaces the window-function port (resolve_gaps / encode_transitions / classify_from_grid).
Spark does what Spark is good at — scoping, the history floor, and ONE shuffle that gathers
each account's monthly buckets into an array. The journey logic then runs per account as a
plain-Python port of the signed-off numpy reference (docs/deterioration_states/dpd_states:
features.py, states.py option B). Sequential rules (glitch fix, +2 jump repair, runs
of months) are loops, exactly as in the reference — no lag/lead approximation, no cascade
divergence. Parity with the reference is a test (tests/test_parity.py), not a hope.

Bucket numbering
----------------
Every rule is written once, on the CC scale ("canonical"):
    CC  0 = no due, 1 = current, 2 = 1-30 DPD, 3 = 31-60, 4 = 61-90 ... 7 = 151-180,
        8 = 181-210, 9 = 210+ (cap)
    RL  0 = 0 DPD,  1 = 1-30 DPD, 2 = 31-60 ... 6 = 151-180, 7 = 180+ (cap)
canonical = max(native + offset, 1): CC offset 0, RL offset 1 (0 and 1 are both "clean").
So the 60-180 DPD spine is canonical 4-7 for both (CC native 4-7, RL native 3-6), and the
180+ segment is canonical 8+ (CC native 8-9, RL native 7). Outputs carry NATIVE buckets.

One state tree and one vocabulary for both segments (7 states): unknown, early_payment_default,
stabilized, repeat_delinquent, straight_roller_seasoned, straight_roller_early_life,
slow_roller. Stabilized only up to 151-180 DPD (never at 180+); holds at the ceiling bucket
are not payments. The segment only decides which accounts are classified.

Two stages (two Kedro nodes per product)
----------------------------------------
build_dpd_sequences   (account_id, obs_date, dlq_bucket) long history
                      -> one row per account: gap-filled monthly bucket array + audit
build_deterioration   sequences -> one row per account in the segment: state + features

Nothing is dropped silently: every account in the history gets a sequences row with a
`build_status`; the classifier keeps only status 'ok' and the segment's current buckets.
"""
from __future__ import annotations

import datetime as _dt
import logging
import sys
from dataclasses import dataclass

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)


# --- bucket schemes ----------------------------------------------------------------------

@dataclass(frozen=True)
class BucketScheme:
    name: str
    offset: int        # canonical = max(native + offset, 1)
    top: int           # highest native bucket (the cap)

    @property
    def canon_top(self) -> int:
        return self.top + self.offset

    def native_buckets(self, canonical) -> list[int]:
        """Native bucket values whose canonical value is in `canonical`."""
        return [n for n in range(self.top + 1) if max(n + self.offset, 1) in set(canonical)]


CC = BucketScheme("cc", offset=0, top=9)
RL = BucketScheme("rl", offset=1, top=7)

# Segments on the canonical scale.
SEGMENTS = {
    "60_180": (4, 5, 6, 7),      # CC native 4-7, RL native 3-6
    "180_plus": (8, 9),          # CC native 8-9, RL native 7
}


# --- parameters ----------------------------------------------------------------------------

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    "rl_history_floor_date": None,
    "segment": "60_180",                  # "60_180" or "180_plus" (the run's spine)
    "on_unresolvable_gap": "truncate",    # "truncate" (keep months after the gap) or "drop"
    "fill_straight_roll_gaps": True,      # 3 _ 5 -> 3 4 5: the only path without a +2 jump
    "repair_cycle_shift": True,           # two bills in one month + empty neighbour month
    "max_inferred_gap_months": 2,         # shorter ambiguous gaps are inferred (0 = never)
    "log_stats": False,                   # one extra aggregate job per node when True
}


@dataclass(frozen=True)
class JourneyParams:
    end_date: str
    floor_date: str | None
    segment: str
    on_unresolvable_gap: str
    fill_straight_roll_gaps: bool
    repair_cycle_shift: bool
    max_inferred_gap_months: int
    log_stats: bool


def journey_params(crx_persona: dict, scheme: BucketScheme) -> JourneyParams:
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    if unknown:          # a stale key (e.g. the removed det_option) must not be silently ignored
        raise ValueError(f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}")
    p = {**PARAM_DEFAULTS, **given}
    if p["segment"] not in SEGMENTS:
        raise ValueError(f"dpd_journey.segment must be one of {list(SEGMENTS)}, got {p['segment']!r}")
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    return JourneyParams(
        end_date=str(crx_persona["persona_end_date"]),
        floor_date=p[f"{scheme.name}_history_floor_date"],
        segment=p["segment"],
        on_unresolvable_gap=p["on_unresolvable_gap"],
        fill_straight_roll_gaps=bool(p["fill_straight_roll_gaps"]),
        repair_cycle_shift=bool(p["repair_cycle_shift"]),
        max_inferred_gap_months=int(p["max_inferred_gap_months"] or 0),
        log_stats=bool(p["log_stats"]),
    )


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


# =========================================================================================
# Per-account core — plain Python, no Spark / numpy / pandas (runs inside the UDFs).
# Lists run OLDEST -> NEWEST on the canonical scale. Port of the numpy reference.
# =========================================================================================

N, R, H, P = 0, 1, 2, 3
NO_PRIOR = 9999


def _glitches(b: list[int]) -> tuple[list[int], int]:
    """Impossible single-month glitches (4 0 4 -> 4 4 4; 0 3 0 -> 0 1 0). Sequential: a fixed
    month is seen by the next comparison, as in features.py::_glitches."""
    b = list(b)
    n = 0
    for t in range(1, len(b) - 1):
        if b[t] <= 1 and b[t - 1] >= 3 and b[t + 1] >= 3:
            b[t] = b[t - 1]
            n += 1
        elif b[t] >= 3 and b[t - 1] <= 1 and b[t + 1] <= 1:
            b[t] = 1
            n += 1
    return b, n


def _repair(b: list[int]) -> tuple[list[int], int, int]:
    """Undo +2 billing-cycle jumps next to a hold at >=2 (3 3 5 / 3 5 5 -> 3 4 5)."""
    b = list(b)
    repaired = 0
    for i in range(len(b) - 1):
        if b[i + 1] - b[i] != 2:
            continue
        if i >= 1 and b[i] == b[i - 1] and b[i] >= 2:
            b[i] += 1
            repaired += 1
        elif i + 2 < len(b) and b[i + 2] == b[i + 1] and b[i + 1] != 4:
            b[i + 1] -= 1
            repaired += 1
    left = sum(1 for i in range(len(b) - 1) if b[i + 1] - b[i] >= 2)
    return b, repaired, left


def encode(b_canon: list[int]) -> tuple[list[int], list[int], list[int]]:
    """(b, d, c): repaired buckets, month-on-month change, transition code N/R/H/P."""
    b = _repair(_glitches([max(x, 1) for x in b_canon])[0])[0]
    d = [b[t + 1] - b[t] for t in range(len(b) - 1)]
    c = []
    for t, x in enumerate(d):
        cur = b[t + 1]
        if x == 0:
            c.append(N if cur == 1 else H)
        elif x < 0:
            c.append(P)
        else:
            c.append(R)                       # +1 and any leftover +2 read as a roll
    return b, d, c


def _runs(mask: list[bool]) -> list[tuple[int, int]]:
    """(start, end_exclusive) of True runs."""
    out, start = [], None
    for i, m in enumerate(mask):
        if m and start is None:
            start = i
        elif not m and start is not None:
            out.append((start, i))
            start = None
    if start is not None:
        out.append((start, len(mask)))
    return out


def _mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs) if xs else 0.0


def journey_features(b_canon: list[int], canon_top: int = 9) -> dict:
    """features.py::journey_features on a canonical bucket list (oldest -> newest).
    canon_top: the ceiling bucket (CC 9, RL 7 -> 8). A hold AT the ceiling is not a payment
    (the bucket cannot rise), so it is not counted in spell_pay_events."""
    raw = [max(x, 1) for x in b_canon]
    g, n_glitches = _glitches(raw)
    _, n_repaired, n_jumps_left = _repair(g)
    b, d, c = encode(b_canon)
    if b[-1] < 2:
        raise ValueError("not in a delinquent spell (current bucket < 2)")
    paid = [max(1 - x, 0) for x in d]

    episodes = _runs([x >= 2 for x in b])
    sp_start, sp_end = episodes[-1]
    is_blip = [e - s <= 2 and max(b[s:e]) <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]

    def gap_prior(peak: int) -> int:
        ends = [e for s, e in prior if max(b[s:e]) >= peak]
        return sp_start - ends[-1] if ends else NO_PRIOR

    t0 = max(sp_start - 1, 0)
    sp_c = c[t0:sp_end - 1]
    hold_runs = [e - s for s, e in _runs([x == H for x in sp_c])]
    first4 = sp_start + next((i for i, x in enumerate(b[sp_start:sp_end]) if x >= 4), 0)
    ru_c = c[t0:first4]
    months_since_4 = len(b) - 1 - first4
    w0 = max(len(c) - 6, t0)
    w_c = c[w0:]
    tail_hold = 0
    for x in reversed(c):
        if x != H:
            break
        tail_hold += 1
    b_now = b[-1]
    return {
        "b_now": b_now,
        "hist_len": len(b),
        "months_before_spell": sp_start,
        "clean_tenure_first": first_spell,
        "n_blips": sum(is_blip),
        "n_prior_episodes": len(prior),
        "max_prior_bucket": max((max(b[s:e]) for s, e in prior), default=0),
        "clean_gap_before_current": sp_start - (prior[-1][1] if prior else 0),
        "gap_prior_peak2": gap_prior(2),
        "gap_prior_peak3": gap_prior(3),
        "gap_prior_peak4": gap_prior(4),
        "runup_len": first4 - sp_start + 1,
        "runup_holds": sum(1 for x in ru_c if x == H),
        "runup_pays": sum(1 for x in ru_c if x == P),
        "spell_len": sp_end - sp_start,
        "spell_pay_events": sum(1 for t in range(t0, sp_end - 1)
                                if c[t] != R and not (c[t] == H and b[t + 1] >= canon_top)),
        "max_hold_run": max(hold_runs, default=0),
        "months_since_4": months_since_4,
        "post4_paid_rate": _mean(paid[first4:]) if months_since_4 > 0 else 0.0,
        "rec_roll_rate": _mean(x == R for x in w_c) if w_c else 1.0,
        "rec_paid_rate": _mean(paid[w0:]) if w_c else 0.0,
        "paid_any_3m": any(x > 0 for x in paid[-3:]),
        "current_hold_run": tail_hold,
        "last6_in_band": sum(1 for x in b[-6:] if abs(x - b_now) <= 1),
        "chg_6m": b_now - b[max(len(b) - 7, 0)],
        "left_censored": sp_start == 0,
        "starts_delinquent": b[0] >= 2,
        "n_glitches": n_glitches,
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


# --- the state tree (states.py, option B) — ONE tree for 60-180 and 180+ -------------------

STATE_RULES = {
    "epd_max_history": 3,                # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,                  # [business]
    "straight_max_runup": 3,             # last clean month -> first month at 4
    "stabilized_min_in_band": 5,         # [business] of the last 6 months within today's bucket ±1
    "stabilized_long_run_months": 6,     # [business]
    "stabilized_long_run_max_rise": 1,   # [business]
    "stabilized_max_bucket": 7,          # [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "repeat_min_prior_peak": 3,          # [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,          # [business] ... and ended <= 12 months before this one
    "seasoned_min_months": 12,           # [business] months on book before the spell
}

STATES = ["unknown", "early_payment_default", "stabilized", "repeat_delinquent",
          "straight_roller_seasoned", "straight_roller_early_life", "slow_roller"]

DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "repeat_delinquent": "Repeat delinquent (re-default)",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
}


def assign_state(f: dict, cropped: bool) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    Q0 journey start not observed (oldest observed month delinquent) -> stabilized if Q2, else unknown
    Q1 early payment default   <=3 months before the spell, <=1 blip, no earlier spell, no payment
                               in the spell (holds at the ceiling are not payments), not cropped
    Q2 stabilized              60-180 only (today <= CC 7 / RL 6): 5 of the last 6 months within
                               today's bucket ±1, or >=6 months since first reaching 4 and at most
                               1 bucket higher than 6 months ago
    Q3 repeat delinquent       an earlier spell reached 3, cured, ended <=12 months before this one
    Q4 straight roller         run-up to 4 took <=3 months: seasoned (>=12 months on book, or
                               cropped = older than the window) / early life
    else slow roller
    """
    p = STATE_RULES
    stab = (f["b_now"] <= p["stabilized_max_bucket"]
            and (f["last6_in_band"] >= p["stabilized_min_in_band"]
                 or (f["months_since_4"] >= p["stabilized_long_run_months"]
                     and f["chg_6m"] <= p["stabilized_long_run_max_rise"])))
    if f["starts_delinquent"]:
        return "stabilized" if stab else "unknown"
    if (f["months_before_spell"] <= p["epd_max_history"] and f["n_blips"] <= p["epd_max_blips"]
            and f["n_prior_episodes"] == 0 and f["spell_pay_events"] == 0 and not cropped):
        return "early_payment_default"
    if stab:
        return "stabilized"
    if f["gap_prior_peak3"] <= p["repeat_window_months"]:
        return "repeat_delinquent"
    if f["runup_len"] <= p["straight_max_runup"]:
        if f["months_before_spell"] >= p["seasoned_min_months"] or cropped:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    return "slow_roller"


# --- Stage 1 core: monthly grid from raw rows ----------------------------------------------

def _legacy_drop(best: dict[int, tuple[int, int]]) -> bool:
    """Would the old window-function rule have dropped this account? (any interior gap whose
    neighbours differ in NATIVE value, after keeping the latest row per month). Lets the
    first run reconcile with the old drop count."""
    ms = sorted(best)
    return any(b - a > 1 and best[a][1] != best[b][1] for a, b in zip(ms, ms[1:]))


def build_history(rows, first_raw_idx: int, global_min_idx: int, offset: int,
                  fill_straight: bool = True, on_unresolvable: str = "truncate",
                  repair_cycle_shift: bool = True, max_inferred_gap: int = 2) -> dict:
    """rows: (month_idx, day_ordinal, native_bucket) inside [floor, end], valid buckets only.

    1. billing-cycle shift: a month with two bills next to an EMPTY interior month gives one
       bill to that month (cycle date near month-end: bills on 31 Jan and 1 Mar, none in
       Feb -> the 1 Mar bill is February's). The earlier bill moves back if the previous
       month is empty, else the later bill moves forward;
    2. one value per month: the latest observation in the month (ties -> worst bucket);
    3. dense grid from the first to the last observed month; a gap is filled when
       a. both neighbours agree on the canonical scale (hold / clean through; CC 0 = 1), or
       b. the only path without a +2 jump is a straight roll (3 _ 5 -> 3 4 5), or
       c. it is short (<= max_inferred_gap months): inferred — carry the left value and
          roll as late as possible (3 _ 4 -> 3 3 4; 5 _ 3 -> 5 5 3). Counted separately;
    4. any other gap is unresolvable: keep the months after the last one ('truncate', the
       history is then cropped) or drop the account ('drop');
    5. cropped = older history exists but is not used (history floor, truncation), or the
       first month is the first month of the whole source (opening date unknown).
    """
    out = {"build_status": "ok", "first_month_idx": None, "last_month_idx": None, "buckets": None,
           "history_cropped": None, "n_gap_months_filled": 0, "n_gap_months_rolled": 0,
           "n_gap_months_inferred": 0, "n_months_truncated": 0, "n_dup_month_rows": 0,
           "n_cycle_shift_moves": 0, "legacy_drop": False}
    by_month: dict[int, list[tuple[int, int]]] = {}
    for m, day, bkt in rows or []:
        by_month.setdefault(m, []).append((day, bkt))
    if not by_month:
        out["build_status"] = "no_rows_in_window"
        return out
    out["legacy_drop"] = _legacy_drop({m: max(v) for m, v in by_month.items()})

    if repair_cycle_shift:
        lo, hi = min(by_month), max(by_month)
        for m in sorted(by_month):
            obs = sorted(set(by_month[m]))
            days = sorted({d for d, _ in obs})
            if len(days) < 2:
                continue
            if lo < m - 1 and m - 1 not in by_month:
                by_month[m - 1] = [x for x in obs if x[0] == days[0]]
                by_month[m] = [x for x in obs if x[0] != days[0]]
                out["n_cycle_shift_moves"] += 1
            elif m + 1 < hi and m + 1 not in by_month:
                by_month[m + 1] = [x for x in obs if x[0] == days[-1]]
                by_month[m] = [x for x in obs if x[0] != days[-1]]
                out["n_cycle_shift_moves"] += 1

    best = {m: max(v) for m, v in by_month.items()}       # latest day, then worst bucket
    out["n_dup_month_rows"] = sum(len(v) for v in by_month.values()) - len(best)
    first, last = min(best), max(best)
    vals = [best[m][1] if m in best else None for m in range(first, last + 1)]
    canon = lambda x: max(x + offset, 1)          # noqa: E731
    cut = 0                                        # index of the first month kept
    filled, rolled, inferred = [], [], []          # indexes of filled months, by rule
    i = 0
    while i < len(vals):
        if vals[i] is not None:
            i += 1
            continue
        j = i
        while vals[j] is None:                     # last month is observed: always stops
            j += 1
        left, right, k = vals[i - 1], vals[j], j - i
        if canon(left) == canon(right):            # CC 0 _ 1 is clean-through, not a conflict
            vals[i:j] = [left] * k
            filled += range(i, j)
        elif fill_straight and canon(right) - canon(left) == k + 1:
            vals[i:j] = [canon(left) + s + 1 - offset for s in range(k)]
            rolled += range(i, j)
        elif k <= max_inferred_gap:
            cl, cr = canon(left), canon(right)
            vals[i:j] = [(max(cl, cr - (k - s)) if cr > cl else cl) - offset for s in range(k)]
            vals[i:j] = [max(v, 0) for v in vals[i:j]]
            inferred += range(i, j)
        else:
            if on_unresolvable == "drop":
                out["build_status"] = "dropped_unresolvable_gap"
                return out
            cut = j
        i = j
    out["n_gap_months_filled"] = sum(1 for t in filled if t >= cut)    # counted in the kept part
    out["n_gap_months_rolled"] = sum(1 for t in rolled if t >= cut)
    out["n_gap_months_inferred"] = sum(1 for t in inferred if t >= cut)
    out["n_months_truncated"] = cut
    kept_first = first + cut
    out.update(first_month_idx=kept_first, last_month_idx=last, buckets=vals[cut:],
               history_cropped=bool(kept_first > first_raw_idx or first_raw_idx <= global_min_idx))
    return out


# --- Stage 2 core: classify one account -------------------------------------------------

def classify(buckets_native: list[int], cropped: bool, offset: int, canon_top: int) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features([max(x + offset, 1) for x in buckets_native], canon_top)
    f["det_state"] = assign_state(f, cropped)
    return f


# =========================================================================================
# Spark side
# =========================================================================================

def _ship_by_value() -> None:
    """Pickle this module's functions BY VALUE into the UDFs, so executors do not need the
    Kedro project installed (cloudpickle >= 2.0, bundled with PySpark >= 3.3). If the
    project is installed on the executors this is harmless."""
    try:
        from pyspark import cloudpickle
        if hasattr(cloudpickle, "register_pickle_by_value") and __name__ in sys.modules \
                and __name__ != "__main__":
            cloudpickle.register_pickle_by_value(sys.modules[__name__])
    except Exception as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning("could not register %s for pickle-by-value (%s); the package must be "
                    "importable on the executors", __name__, exc)


_HISTORY_SCHEMA = T.StructType([
    T.StructField("build_status", T.StringType()),
    T.StructField("first_month_idx", T.IntegerType()),
    T.StructField("last_month_idx", T.IntegerType()),
    T.StructField("buckets", T.ArrayType(T.IntegerType())),
    T.StructField("history_cropped", T.BooleanType()),
    T.StructField("n_gap_months_filled", T.IntegerType()),
    T.StructField("n_gap_months_rolled", T.IntegerType()),
    T.StructField("n_gap_months_inferred", T.IntegerType()),
    T.StructField("n_cycle_shift_moves", T.IntegerType()),
    T.StructField("legacy_drop", T.BooleanType()),
    T.StructField("n_months_truncated", T.IntegerType()),
    T.StructField("n_dup_month_rows", T.IntegerType()),
])

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None), ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()), ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()), ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()), ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()), ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()), ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()), ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType([T.StructField("det_state", T.StringType())]
                                + [T.StructField(n, t) for n, t in _FEATURES if t is not None])


def _month_col(c) -> F.Column:
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(F.expr("make_date(cast({0} div 12 as int), cast({0} % 12 + 1 as int), 1)".format(c)))


def build_dpd_sequences(history: DataFrame, scheme: BucketScheme, params: JourneyParams,
                        restructure: DataFrame | None = None) -> DataFrame:
    """history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
    optionally restructure_flag (0/1 per row; max over the account's rows).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag
    """
    missing = [c for c in ("account_id", "obs_date", "dlq_bucket") if c not in history.columns]
    if missing:
        raise ValueError(f"build_dpd_sequences: history is missing {missing}; has {sorted(history.columns)}")
    _ship_by_value()
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None

    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(F.when(in_window, F.struct(
            m.alias("m"),
            F.datediff(F.col("obs_date").cast("date"), F.lit("1970-01-01")).alias("d"),
            bucket.alias("b"),
        ))).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias("n_invalid_rows"),   # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)                       # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))     # 1 row
    per_acc = per_acc.crossJoin(F.broadcast(source_min))

    offset, fill, how = scheme.offset, params.fill_straight_roll_gaps, params.on_unresolvable_gap
    shift, max_inf = params.repair_cycle_shift, params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history([(r["m"], r["d"], r["b"]) for r in rows], first_raw, global_min,
                             offset, fill, how, shift, max_inf)

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias("dpd_string"),
        F.col("_h.history_cropped").alias("history_cropped"),
        F.coalesce("_h.n_gap_months_filled", F.lit(0)).alias("n_gap_months_filled"),
        F.coalesce("_h.n_gap_months_rolled", F.lit(0)).alias("n_gap_months_rolled"),
        F.coalesce("_h.n_gap_months_inferred", F.lit(0)).alias("n_gap_months_inferred"),
        F.coalesce("_h.n_cycle_shift_moves", F.lit(0)).alias("n_cycle_shift_moves"),
        F.coalesce("_h.legacy_drop", F.lit(False)).alias("legacy_drop"),
        F.coalesce("_h.n_months_truncated", F.lit(0)).alias("n_months_truncated"),
        F.coalesce("_h.n_dup_month_rows", F.lit(0)).alias("n_dup_month_rows"),
        F.col("n_invalid_rows").cast("int"),
        (F.col("_rf") if "_rf" in s.columns else F.lit(None).cast("int")).alias("_rf"),
    )
    if restructure is not None:
        out = out.join(restructure.select("account_id", F.col("restructure_blind_spot_flag").alias("_rs")),
                       "account_id", "left")
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop("_rf", "_rs")
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


def build_deterioration(sequences: DataFrame, scheme: BucketScheme, params: JourneyParams) -> DataFrame:
    """sequences: output of build_dpd_sequences. Keeps build_status 'ok' and accounts whose
    LATEST month is in the segment (native buckets), and assigns one state per account.

    Returns one row per account:
        account_id, det_state, det_state_label, det_segment, current_bucket
        (native), <features>, history_months, history_cropped, n_months_truncated,
        history_stale_months (snapshot month - last observed month), restructure_blind_spot_flag,
        computed_at
    """
    _ship_by_value()
    segment = params.segment
    native = scheme.native_buckets(SEGMENTS[segment])
    cur = F.element_at("dlq_buckets", -1)
    seg = sequences.where((F.col("build_status") == "ok") & cur.isin(native))

    offset, top = scheme.offset, scheme.canon_top

    def _udf(buckets, cropped):
        return classify(list(buckets), bool(cropped), offset, top)

    schema = _CLASSIFY_SCHEMA
    res = seg.withColumn("_s", F.udf(_udf, schema)("dlq_buckets", "history_cropped"))

    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    snap = _month_idx(params.end_date)
    feat_cols = [F.col(f"_s.{f.name}").alias(f.name) for f in schema.fields if f.name != "det_state"]
    out = res.select(
        F.col("account_id"),
        F.col("_s.det_state").alias("det_state"),
        labels[F.col("_s.det_state")].alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        cur.alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        (F.lit(snap) - _month_col(F.col("last_month"))).alias("history_stale_months"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    if params.log_stats:
        out = out.persist()
        _log_state_stats(sequences, out, scheme, params)
    return out


# --- logging (opt-in: each call is one aggregate job) ------------------------------------------

def _log_sequence_stats(seq: DataFrame, scheme: BucketScheme, params: JourneyParams) -> None:
    r = seq.agg(
        F.count("*").alias("accounts"),
        *[F.sum((F.col("build_status") == s).cast("int")).alias(s)
          for s in ("ok", "no_rows_in_window", "no_valid_rows", "dropped_unresolvable_gap")],
        F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated_accounts"),
        F.sum("n_gap_months_filled").alias("gap_months_filled"),
        F.sum("n_gap_months_rolled").alias("gap_months_rolled"),
        F.sum("n_gap_months_inferred").alias("gap_months_inferred"),
        F.sum("n_cycle_shift_moves").alias("cycle_shift_moves"),
        F.sum(F.col("legacy_drop").cast("int")).alias("legacy_rule_would_drop"),
        F.sum("n_dup_month_rows").alias("dup_month_rows"),
        F.sum("n_invalid_rows").alias("invalid_rows"),
        F.min("first_month").alias("first_month"),
        F.max("last_month").alias("last_month"),
    ).first().asDict()
    LOG.info("build_%s_dpd_sequences [end %s, floor %s, gaps %s]: %s",
             scheme.name, params.end_date, params.floor_date, params.on_unresolvable_gap, r)


def _log_state_stats(seq: DataFrame, out: DataFrame, scheme: BucketScheme, params: JourneyParams) -> None:
    n_ok = seq.where(F.col("build_status") == "ok").count()
    rows = out.groupBy("det_state").count().orderBy(F.desc("count")).collect()
    n = sum(r["count"] for r in rows) or 1
    LOG.info("build_%s_deterioration [%s]: %d of %d ok accounts in segment; %s", scheme.name,
             params.segment, n, n_ok,
             ", ".join(f"{r['det_state']} {r['count']} ({r['count'] / n:.1%})" for r in rows))
`````

### FILE: `spark/crx_persona/cc_full_history/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `spark/crx_persona/cc_full_history/nodes.py`
sha256 `19b8f83a7e3b662e17443c3e76af1312ba8bf1fefdf657f1d5182307651c2b62` · 48 lines · trailing newline: yes

`````python
"""CC full billing history (amended). Same output contract as before:
(account_id long, billing_date date, dlq_bucket int) at grain (account_id, billing_date).

Changes vs the current node (see REVIEW_SPARK.md, findings F1-F3):
  * a bucket that cannot be parsed from add_info becomes NULL explicitly — never "" cast to
    int (an error under ANSI mode, the default from Spark 4);
  * the same-date dedupe is deterministic: the worst (max) non-null bucket wins. Before,
    dropDuplicates kept an arbitrary row, so two runs could disagree, and a NULL row could
    beat a valid one;
  * the history floor (2024-01, CC data quality) is NOT applied here: the full history is
    kept so build_cc_dpd_sequences can tell a floor-cropped account from a new one.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

# Keep the existing constant if it differs: add_info carries "BS_PMT_CYCLE_DUE=<bucket>".
_DPD_BUCKET_REGEX = r"BS_PMT_CYCLE_DUE=(\d+)"


def build_cc_full_history(raw_stg_billing: DataFrame, cc_spine: DataFrame) -> DataFrame:
    """Full billing history of the run's CC spine.

    Args:
        raw_stg_billing: raw billing table, all CC accounts. Columns: contract_idt (double,
            whole-number account id), billing_date (timestamp), add_info (string carrying
            BS_PMT_CYCLE_DUE=<bucket>).
        cc_spine: model-namespaced spine of the run (cc_60_180 or cc_180_plus). Column:
            contract_id.

    Returns:
        DataFrame at grain (account_id, billing_date): account_id long, billing_date date,
        dlq_bucket int (NULL when add_info carries no bucket).
    """
    # -- Step 1 (R20): scope to the spine, distinct leftsemi on the native contract id ----
    # Join BEFORE any cast to string (double "939877870.0" vs "939877870" zeroes the join).
    spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()
    raw_bucket = F.regexp_extract(F.col("add_info"), _DPD_BUCKET_REGEX, 1)
    df = raw_stg_billing.join(F.broadcast(spine_keys), "contract_idt", "leftsemi").select(
        # contract_idt is a whole-number double at the raw boundary -- cast to long (never
        # string), same convention as the rest of crx_persona.
        F.col("contract_idt").cast("long").alias("account_id"),
        F.col("billing_date").cast("date").alias("billing_date"),
        # regexp_extract returns "" when there is no match: NULL, not a failing cast
        F.when(raw_bucket != "", raw_bucket.cast("int")).alias("dlq_bucket"),
    )

    # -- Step 2: one row per (account_id, billing_date), deterministic: worst bucket -------
    return df.groupBy("account_id", "billing_date").agg(F.max("dlq_bucket").alias("dlq_bucket"))
`````

### FILE: `spark/crx_persona/rl_full_history/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `spark/crx_persona/rl_full_history/nodes.py`
sha256 `72792afad8991dd5e6f1cac93055bfe5747e5ff8df328785554d4121716260ae` · 79 lines · trailing newline: yes

`````python
"""RL full monthly history (amended). Same output contract as before.

Changes vs the current node (see REVIEW_SPARK.md, findings F4-F6):
  * the spine key is cast to string SAFELY: a double/decimal account_id is cast to long
    first (double -> string gives "1.23456789E8" and silently zeroes the leftsemi join —
    the exact trap the CC node documents);
  * the spine keys are broadcast: ~31k keys are tiny, and without the hint Spark may shuffle
    the whole int_loan_master (all RL accounts x all months) for a sort-merge join;
  * _log_stats is opt-in (params dpd_journey.log_stats): it runs extra jobs over the whole
    output, and without a persist the node is computed twice.
"""
import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)


def _string_key(df: DataFrame, col: str = "account_id"):
    dtype = df.schema[col].dataType
    c = F.col(col)
    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
        c = c.cast("long")
    return F.trim(c.cast("string"))


def build_rl_full_history(rl_spine: DataFrame, int_loan_master: DataFrame,
                          crx_persona: dict | None = None) -> DataFrame:
    """Full monthly history of the run's RL spine.

    Args:
        rl_spine: model-namespaced RL spine (~31k accounts). Column: account_id.
        int_loan_master: monthly snapshots for all RL accounts. Columns: account_id (string),
            observation_date (date), dpd_bucket (int: 0 = 0 DPD, 1 = 1-30, ..., 7 = 180+),
            emi_coverage_ratio, outstanding_balance, is_restructured, loan_type.
        crx_persona: optional params dict (only dpd_journey.log_stats is read).

    Returns:
        DataFrame at grain (account_id, month_end_date): account_id string, month_end_date
        date, dlq_bucket int, emi_coverage_ratio double, outstanding_balance double,
        restructure_flag int, loan_type string, computed_at timestamp.
    """
    # -- Step 1 (R20): scope to the spine (broadcast: the spine is model-sized) ----------
    spine_keys = rl_spine.select(_string_key(rl_spine).alias("account_id")).distinct()
    df = int_loan_master.join(F.broadcast(spine_keys), on="account_id", how="leftsemi")

    # -- Step 2: select + alias + cast to the output schema ------------------------------
    result = df.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date").alias("month_end_date"),
        F.col("dpd_bucket").cast("int").alias("dlq_bucket"),
        F.col("emi_coverage_ratio").cast("double"),
        F.col("outstanding_balance").cast("double"),
        F.col("is_restructured").cast("int").alias("restructure_flag"),
        F.col("loan_type").cast("string"),
        F.current_timestamp().alias("computed_at"),
    )

    # -- Step 3 (opt-in): one aggregate job — rows, date range, null rates, spine match ---
    if ((crx_persona or {}).get("dpd_journey") or {}).get("log_stats"):
        result = result.persist()
        _log_stats(result, spine_keys)
    return result


def _log_stats(df: DataFrame, spine_keys: DataFrame) -> None:
    r = df.agg(
        F.count("*").alias("rows"),
        F.countDistinct("account_id").alias("accounts"),
        F.min("month_end_date").alias("first_month"),
        F.max("month_end_date").alias("last_month"),
        *[F.avg(F.col(c).isNull().cast("double")).alias(f"null_{c}")
          for c in ("dlq_bucket", "month_end_date", "restructure_flag")],
    ).first().asDict()
    r["spine_accounts"] = spine_keys.count()
    LOG.info("build_rl_full_history: %s (spine accounts found: %s of %s)", r, r["accounts"],
             r["spine_accounts"])
`````

### FILE: `spark/crx_persona/cc_a4_deterioration/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `spark/crx_persona/cc_a4_deterioration/nodes.py`
sha256 `1dffbe91a326dc4fe1632e1bfe8e6f443d925906a774f66287b8ff6949b6c766` · 36 lines · trailing newline: yes

`````python
"""CC-A4 — DPD-journey deterioration state for credit cards (thin wrappers on _dpd_journey).

Node 1 build_cc_dpd_sequences   crx_cc_full_history + crx_cc_spell_table -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration crx_cc_dpd_sequences                     -> crx_cc_a4_deterioration

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210, 9 = 210+.
History before params dpd_journey.cc_history_floor_date (default 2024-01-01, known data-
quality issue, temporary) is not used; accounts with older history are flagged cropped.
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

_RESTRUCTURED_ENTRY = "restructured_entry"


def build_cc_dpd_sequences(crx_cc_full_history: DataFrame, crx_cc_spell_table: DataFrame,
                           crx_persona: dict) -> DataFrame:
    """One row per CC account: gap-filled monthly bucket array (from the history floor to
    persona_end_date) + audit columns + restructure_blind_spot_flag (R13: 1 if ANY spell of
    the account is censored_subtype == 'restructured_entry'). See _dpd_journey.build_dpd_sequences.
    """
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket")
    restructure = crx_cc_spell_table.groupBy("account_id").agg(
        F.max((F.col("censored_subtype") == _RESTRUCTURED_ENTRY).cast("int"))
        .alias("restructure_blind_spot_flag"))
    return build_dpd_sequences(history, CC, journey_params(crx_persona, CC), restructure=restructure)


def build_cc_a4_deterioration(crx_cc_dpd_sequences: DataFrame, crx_persona: dict) -> DataFrame:
    """One state per CC account whose latest bucket is in the run's segment (params
    dpd_journey.segment: 60_180 -> buckets 4-7, 180_plus -> 8-9). See _dpd_journey.build_deterioration.
    """
    return build_deterioration(crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC))
`````

### FILE: `spark/crx_persona/cc_a4_deterioration/pipeline.py`
sha256 `d15ebb0ef8a32f614c5884aed06b274418a5f43bc9d2e7d7fac1e4e1caa206a5` · 38 lines · trailing newline: yes

`````python
"""Kedro pipeline: CC-A4 — DPD-journey deterioration state for Credit Cards.

2-node pipeline:
    Node 1  build_cc_dpd_sequences      -> crx_cc_dpd_sequences
    Node 2  build_cc_a4_deterioration   -> crx_cc_a4_deterioration

Requires crx_cc_full_history and crx_cc_spell_table to already be materialized.

Run with:
    kedro run --pipeline=crx_cc_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_a4_deterioration, build_cc_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_cc_dpd_sequences,
                inputs=["crx_cc_full_history", "crx_cc_spell_table", "params:crx_persona"],
                outputs="crx_cc_dpd_sequences",
                name="build_crx_cc_dpd_sequences",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
            node(
                func=build_cc_a4_deterioration,
                inputs=["crx_cc_dpd_sequences", "params:crx_persona"],
                outputs="crx_cc_a4_deterioration",
                name="build_crx_cc_a4_deterioration",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `spark/crx_persona/rl_a4_deterioration/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `spark/crx_persona/rl_a4_deterioration/nodes.py`
sha256 `0cc3d54ce5d1d6c4d83c4b2aa0184c1e8b3608b31a3e6ba21839afad28076f35` · 27 lines · trailing newline: yes

`````python
"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_dpd_sequences    crx_rl_full_history  -> crx_rl_dpd_sequences
Node 2 build_rl_a4_deterioration crx_rl_dpd_sequences -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).
"""
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import RL, build_deterioration, build_dpd_sequences, journey_params


def build_rl_dpd_sequences(crx_rl_full_history: DataFrame, crx_persona: dict) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (1 if the loan was restructured in any month)."""
    history = crx_rl_full_history.select(
        "account_id", F.col("month_end_date").alias("obs_date"), "dlq_bucket", "restructure_flag")
    return build_dpd_sequences(history, RL, journey_params(crx_persona, RL))


def build_rl_a4_deterioration(crx_rl_dpd_sequences: DataFrame, crx_persona: dict) -> DataFrame:
    """One state per RL account whose latest bucket is in the run's segment (60_180 -> RL 3-6,
    180_plus -> RL 7)."""
    return build_deterioration(crx_rl_dpd_sequences, RL, journey_params(crx_persona, RL))
`````

### FILE: `spark/crx_persona/rl_a4_deterioration/pipeline.py`
sha256 `45d7ebf1e3212afbab310c827ac839a9f932d1c7ad2429c417d3f817795061e7` · 38 lines · trailing newline: yes

`````python
"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

2-node pipeline:
    Node 1  build_rl_dpd_sequences      -> crx_rl_dpd_sequences
    Node 2  build_rl_a4_deterioration   -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_a4_deterioration, build_rl_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=["crx_rl_full_history", "params:crx_persona"],
                outputs="crx_rl_dpd_sequences",
                name="build_crx_rl_dpd_sequences",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=["crx_rl_dpd_sequences", "params:crx_persona"],
                outputs="crx_rl_a4_deterioration",
                name="build_crx_rl_a4_deterioration",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `spark/tests/test_parity.py`
sha256 `d4c962371a858edeafa86a4a853bc890b7f0dbfbab71a16313d1a7e8faa4cf16` · 196 lines · trailing newline: yes

`````python
"""Parity: the per-account core of crx_persona/_dpd_journey.py vs the signed-off numpy
reference (docs/deterioration_states/dpd_states). No Spark needed.

    python docs/deterioration_states/spark/tests/test_parity.py        # or: pytest <this file>

Checks every feature and the state (one tree, both segments) on the synthetic
generators, the business edge cases (selftest CASES / CROP_CASES) on CC and RL numbering,
and the Stage 1 gap rules.
"""
from __future__ import annotations

import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1] / "crx_persona"))       # the engine
sys.path.insert(0, str(HERE.parents[2]))                       # the reference package

import _dpd_journey as J                                       # noqa: E402
from dpd_states import segment_180, synth                      # noqa: E402
from dpd_states.analysis import crop_history                   # noqa: E402
from dpd_states.config import MAX_HISTORY_MONTHS               # noqa: E402
from dpd_states.features import build_features                 # noqa: E402
from dpd_states.selftest import CASES, CROP_CASES              # noqa: E402
from dpd_states.states import OPTIONS, RECOMMENDED, assign_states  # noqa: E402

N = 20_000
FEATURES = [k for k in J.journey_features([1, 2, 3, 4])]


def _chron(s: str) -> list[int]:
    """Bank string (leftmost = current) -> list oldest -> newest."""
    return [int(ch) for ch in reversed(s)]


def _to_rl(cc: list[int]) -> list[int]:
    """CC buckets -> RL native buckets (CC 0/1 -> 0, CC 2 -> 1, ..., CC 8/9 -> 7)."""
    return [min(max(x, 1), 8) - 1 for x in cc]


def _compare(ref, mine, what: str) -> int:
    bad = 0
    for k in FEATURES:
        r, m = ref[k], mine[k]
        same = abs(float(r) - float(m)) < 1e-9 if isinstance(m, float) else bool(r == m) if isinstance(m, bool) else int(r) == int(m)
        if not same:
            bad += 1
            if bad <= 3:
                print(f"  MISMATCH {what} {k}: reference {r!r} vs engine {m!r}")
    return bad


def _reference(strings, cropped, cap=9):
    import pandas as pd
    f = build_features(pd.DataFrame({"dpd_string": list(strings), "history_truncated": list(cropped)}), cap=cap)
    return f, assign_states(f, **OPTIONS[RECOMMENDED])


def test_spine_cc_and_rl():
    synth.calibrate(n=4000, iters=3)
    df = synth.generate(N)
    s, cropped = crop_history(df.dpd_string, MAX_HISTORY_MONTHS)
    f, ref = _reference(s, cropped)
    bad = 0
    for i, (string, cr) in enumerate(zip(s, cropped)):
        mine = J.classify(_chron(string), bool(cr), 0, 9)
        if mine["det_state"] != ref.iloc[i]:
            bad += 1
            print(f"  STATE {string}: {ref.iloc[i]} vs {mine['det_state']}")
        bad += _compare(f.iloc[i], mine, f"cc {string}")
    # RL: the same journeys in RL numbering (cap RL 7 = canonical 8) give the same states
    rl_ref_strings = ["".join(str(min(max(x, 1), 8)) for x in reversed(_chron(x))) for x in s]
    f_rl, ref_rl = _reference(rl_ref_strings, cropped, cap=8)
    for i, (string, cr) in enumerate(zip(s, cropped)):
        mine = J.classify(_to_rl(_chron(string)), bool(cr), 1, 8)
        if mine["det_state"] != ref_rl.iloc[i]:
            bad += 1
            print(f"  RL STATE {string}: {ref_rl.iloc[i]} vs {mine['det_state']}")
        bad += _compare(f_rl.iloc[i], mine, f"rl {string}")
    print(f"spine: {len(s):,} accounts, CC + RL, {bad} mismatches")
    assert bad == 0


def test_segment_180_cc():
    df = segment_180.generate_180(8000, median_months_at_9=12)
    f = segment_180.features_180(df)
    ref = segment_180.assign_180(f)
    bad = 0
    for i, (string, cr) in enumerate(zip(f.dpd_string, f.history_truncated)):
        mine = J.classify(_chron(string), bool(cr), 0, 9)
        if mine["det_state"] != ref.iloc[i]:
            bad += 1
            if bad <= 5:
                print(f"  180 STATE {string}: {ref.iloc[i]} vs {mine['det_state']}")
        bad += _compare(f.iloc[i], mine, f"180 {string}")
    assert "stabilized" not in set(ref), "stabilized must never occur at 180+"
    print(f"180+: {len(f):,} accounts, {bad} mismatches; states {sorted(set(ref))}")
    assert bad == 0


def test_business_cases():
    bad = 0
    for chron, want, why in CASES:
        b = [int(ch) for ch in chron.replace(" ", "")]
        for name, buckets, off, top in (("cc", b, 0, 9), ("rl", _to_rl(b), 1, 8)):
            got = J.classify(buckets, False, off, top)["det_state"]
            if got != want:
                bad += 1
                print(f"  CASE {name} {chron!r}: want {want}, got {got} — {why}")
    for chron, n, want, why in CROP_CASES:
        b = [int(ch) for ch in chron.replace(" ", "")]
        got = J.classify(b[-n:], len(b) >= n, 0, 9)["det_state"]
        if got != want:
            bad += 1
            print(f"  CROP {chron!r}: want {want}, got {got} — {why}")
    cases_180 = [   # (product, oldest -> newest native buckets, expected) — same tree as 60-180
        ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 9] + [9] * 12, "straight_roller_seasoned"),
        ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], "straight_roller_seasoned"),  # holding at 8: NOT stabilized
        ("cc", [8, 9, 9, 9, 9, 9, 9], "unknown"),
        ("cc", [0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9], "early_payment_default"),     # holds at the cap are not payments
        ("cc", [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 8, 9], "straight_roller_early_life"),  # 9 -> 8 is a payment: not EPD
        ("rl", [0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 7], "straight_roller_seasoned"),
        ("rl", [7, 7, 7, 7], "unknown"),
        ("rl", [0, 0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 7], "early_payment_default"),
        ("rl", [0] * 20 + [1, 2, 3, 4, 5] + [6] * 12 + [7, 7], "straight_roller_seasoned"),
        ("rl", [0] * 20 + [1, 1, 2, 2, 3, 4, 5, 6, 7], "slow_roller"),
    ]
    for product, buckets, want in cases_180:
        off, top = (0, 9) if product == "cc" else (1, 8)
        got = J.classify(buckets, False, off, top)["det_state"]
        if got != want:
            bad += 1
            print(f"  180 {product} {buckets}: want {want}, got {got}")
    print(f"business cases: {len(CASES) * 2 + len(CROP_CASES) + len(cases_180)} checked, {bad} wrong")
    assert bad == 0


def test_build_history():
    """Stage 1 rules: dedupe, cycle shift, gap fill / roll / infer, truncate/drop, cropped."""
    def run(rows, first_raw=None, gmin=0, offset=0, fill=True, how="truncate", max_inf=2):
        first_raw = first_raw if first_raw is not None else min(r[0] for r in rows)
        return J.build_history(rows, first_raw, gmin, offset, fill, how, True, max_inf)

    bad = []
    r = run([(100, 1, 3), (101, 5, 4), (101, 9, 5), (102, 1, 5)])         # same month: latest wins
    bad += [] if r["buckets"] == [3, 5, 5] and r["n_dup_month_rows"] == 1 else ["dedupe latest"]
    r = run([(100, 1, 3), (101, 5, 4), (101, 5, 6), (102, 1, 6)])         # same day: worst wins
    bad += [] if r["buckets"] == [3, 6, 6] else ["dedupe tie"]
    r = run([(100, 1, 4), (102, 1, 4)])                                    # hold through
    bad += [] if r["buckets"] == [4, 4, 4] and r["n_gap_months_filled"] == 1 else ["hold fill"]
    r = run([(100, 1, 0), (102, 1, 1)])                                    # CC 0 _ 1: clean
    bad += [] if r["buckets"] == [0, 0, 1] and r["n_months_truncated"] == 0 else ["cc 0/1 fill"]
    r = run([(100, 1, 3), (103, 1, 6)])                                    # 3 _ _ 6: straight roll
    bad += [] if r["buckets"] == [3, 4, 5, 6] and r["n_gap_months_rolled"] == 2 else ["roll fill"]
    r = run([(100, 1, 0), (102, 1, 2)], offset=1)                          # RL 0 _ 2 -> 0 1 2
    bad += [] if r["buckets"] == [0, 1, 2] else ["rl roll fill"]
    r = run([(100, 1, 0), (101, 1, 0), (105, 1, 4), (106, 1, 5)])          # 0 _ _ _ 4: unresolvable
    bad += [] if (r["buckets"] == [4, 5] and r["n_months_truncated"] == 5
                  and r["history_cropped"] and r["legacy_drop"]) else ["truncate"]
    r = run([(100, 1, 3), (102, 1, 4)])                                    # 3 _ 4: inferred, roll late
    bad += [] if r["buckets"] == [3, 3, 4] and r["n_gap_months_inferred"] == 1 else ["infer up"]
    r = run([(100, 1, 6), (103, 1, 3)])                                    # 6 _ _ 3: carry, pay at end
    bad += [] if r["buckets"] == [6, 6, 6, 3] and r["n_gap_months_inferred"] == 2 else ["infer down"]
    r = run([(100, 1, 3), (102, 1, 4)], max_inf=0)                         # inference off -> truncate
    bad += [] if r["buckets"] == [4] and r["n_months_truncated"] == 2 else ["infer off"]
    # cycle shift: bills on day 30 of month 100 and day 31 / day 61 (next cycle) in month 101,
    # none in 102: the later bill of 101 belongs to 102
    r = run([(100, 30, 2), (101, 60, 3), (101, 61, 4), (103, 90, 5)])
    bad += [] if (r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1
                  and r["n_gap_months_filled"] + r["n_gap_months_inferred"] == 0) else ["cycle shift fwd"]
    r = run([(100, 1, 2), (102, 50, 3), (102, 80, 4), (103, 90, 5)])       # earlier bill moves back
    bad += [] if r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1 else ["cycle shift back"]
    r = run([(100, 1, 0), (102, 1, 4)], how="drop", max_inf=0)
    bad += [] if r["build_status"] == "dropped_unresolvable_gap" else ["drop"]
    r = run([(100, 1, 0), (101, 1, 2)], fill=False)
    bad += [] if r["history_cropped"] is False else ["not cropped"]
    r = run([(110, 1, 0), (111, 1, 2)], first_raw=90)                      # floor cut older rows
    bad += [] if r["history_cropped"] else ["cropped by floor"]
    r = run([(110, 1, 0), (111, 1, 2)], gmin=110)                          # starts with the source
    bad += [] if r["history_cropped"] else ["cropped at source start"]
    r = J.build_history([], 100, 0, 0)
    bad += [] if r["build_status"] == "no_rows_in_window" else ["empty"]
    print(f"build_history: {17 - len(bad)}/17 rules OK {bad or ''}")
    assert not bad


if __name__ == "__main__":
    fails = 0
    for t in (test_build_history, test_business_cases, test_segment_180_cc, test_spine_cc_and_rl):
        try:
            t()
        except AssertionError:
            fails += 1
            print(f"FAILED {t.__name__}")
    print("PARITY PASSED" if not fails else f"PARITY FAILED ({fails})")
    sys.exit(1 if fails else 0)
`````

### FILE: `spark/tests/test_spark_e2e.py`
sha256 `d25b4fd07e617741dbf14beba6d81bb75726b66c0e8dddf1ea33cda983eb30bf` · 205 lines · trailing newline: yes

`````python
"""End to end on local Spark: synthetic raw tables -> the Kedro node functions -> states,
compared account by account with the (parity-tested) per-account core.

    python docs/deterioration_states/spark/tests/test_spark_e2e.py [n_accounts]

The raw tables carry the noise the real ones have: same-day duplicates, NULL / unparseable
add_info, billing-cycle shifts (two bills in one month, none in the next), months missing
between equal neighbours, history before the CC floor, and a few unresolvable gaps. The
node code is imported as a package that the Spark workers CANNOT import — so this also
proves the pickle-by-value shipping works without the project installed on executors.
"""
from __future__ import annotations

import datetime as dt
import os
import pathlib
import random
import sys
import time

HERE = pathlib.Path(__file__).resolve()
sys.path.insert(0, str(HERE.parents[1]))                       # crx_persona package
sys.path.insert(0, str(HERE.parents[2]))                       # reference generators
os.environ.setdefault("JAVA_HOME", "/opt/homebrew/opt/openjdk@17")
os.environ["PYSPARK_PYTHON"] = sys.executable

from pyspark.sql import SparkSession                           # noqa: E402
from pyspark.sql import functions as F                         # noqa: E402

from crx_persona import _dpd_journey as J                      # noqa: E402
from crx_persona.cc_a4_deterioration.nodes import build_cc_a4_deterioration, build_cc_dpd_sequences  # noqa: E402
from crx_persona.cc_full_history.nodes import build_cc_full_history  # noqa: E402
from crx_persona.rl_a4_deterioration.nodes import build_rl_a4_deterioration, build_rl_dpd_sequences  # noqa: E402
from crx_persona.rl_full_history.nodes import build_rl_full_history  # noqa: E402
from dpd_states import segment_180, synth                      # noqa: E402

SNAP = dt.date(2026, 8, 31)
SNAP_IDX = SNAP.year * 12 + SNAP.month - 1
FLOOR_IDX = 2024 * 12 + 0


def _month_date(idx: int, day: int) -> dt.datetime:
    y, m = divmod(idx, 12)
    return dt.datetime(y, m + 1, day)


def _accounts(n: int) -> list[list[int]]:
    """CC journeys oldest -> newest, all ending in the snapshot month."""
    synth.calibrate(n=4000, iters=3)
    spine = [[int(c) for c in reversed(s)] for s in synth.generate(n).dpd_string]
    s180 = [[int(c) for c in reversed(s)] for s in segment_180.generate_180(n // 4).dpd_string]
    return spine + s180


def _cc_raw(journeys, rng):
    """raw_stg_billing rows + the expected (kept history, cropped) per account."""
    rows, expected = [], {}
    for k, b in enumerate(journeys):
        acc = 900_000_000 + k
        start = SNAP_IDX - len(b) + 1
        noise = rng.random()
        months = {start + t: v for t, v in enumerate(b)}
        bills = [(m, 15, v) for m, v in months.items()]
        trunc_from = None
        interior = [m for m in months if max(start, FLOOR_IDX) + 1 < m < SNAP_IDX - 1]
        if noise < 0.05 and len(interior) > 2:                      # cycle shift
            m = rng.choice(interior[:-1])
            bills = [x for x in bills if x[0] != m] + [(m + 1, 1, months[m])]
        elif noise < 0.10 and len(interior) > 2:                    # gap between equal neighbours
            cand = [m for m in interior if months[m - 1] == months[m] == months[m + 1]]
            if cand:
                drop = rng.choice(cand)
                bills = [x for x in bills if x[0] != drop]
        elif noise < 0.12 and len(interior) > 6:                    # unresolvable 3-month gap
            m = interior[len(interior) // 2 - 3]
            cl, cr = max(months[m - 1], 1), max(months[m + 3], 1)
            if cl != cr and cr - cl != 4:
                bills = [x for x in bills if not m <= x[0] <= m + 2]
                trunc_from = m + 3
        for m, day, v in bills:
            ts = _month_date(m, day)
            rows.append((float(acc), ts, f"X=1;BS_PMT_CYCLE_DUE={v};Y=2"))
            if rng.random() < 0.02:                                 # same-day duplicate
                rows.append((float(acc), ts, f"X=1;BS_PMT_CYCLE_DUE={v};Y=2"))
            if rng.random() < 0.02:                                 # unparseable row same day
                rows.append((float(acc), ts, "X=1;NO_BUCKET"))
        first_kept = max(start, FLOOR_IDX)
        if trunc_from is not None and trunc_from > first_kept:
            first_kept = trunc_from
        kept = [months[m] for m in range(first_kept, SNAP_IDX + 1)]
        expected[acc] = (kept, first_kept > start)
    return rows, expected


def main(n: int = 4000) -> int:
    t0 = time.time()
    rng = random.Random(3)
    spark = (SparkSession.builder.master("local[4]").appName("dpd_journey_e2e")
             .config("spark.sql.shuffle.partitions", "8").config("spark.ui.enabled", "false")
             .config("spark.sql.ansi.enabled", "true")               # Spark 4 default
             .getOrCreate())
    spark.sparkContext.setLogLevel("ERROR")
    journeys = _accounts(n)
    bad = 0

    # ---------------- CC ----------------
    rows, expected = _cc_raw(journeys, rng)
    raw = spark.createDataFrame(rows, "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(float(a),) for a in expected], "contract_id double")
    spells = spark.createDataFrame([(a, "restructured_entry" if a % 50 == 0 else "none") for a in expected],
                                   "account_id long, censored_subtype string")
    cc_outs = []
    for segment in ("60_180", "180_plus"):
        params = {"persona_start_date": "2024-01-01", "persona_end_date": str(SNAP),
                  "dpd_journey": {"segment": segment, "log_stats": True}}
        full = build_cc_full_history(raw, spine)
        seq = cc_seq = build_cc_dpd_sequences(full, spells, params)
        out = build_cc_a4_deterioration(seq, params)
        cc_outs.append(out)
        got = {r.account_id: r for r in out.collect()}
        seg = J.SEGMENTS[segment]
        want = {a: J.classify(k, c, 0, 9) for a, (k, c) in expected.items()
                if max(k[-1], 1) in seg}
        miss = set(want) ^ set(got)
        wrong = [a for a in want if a in got and (got[a].det_state != want[a]["det_state"]
                                                  or got[a].history_cropped != expected[a][1])]
        bad += len(miss) + len(wrong)
        for a in wrong[:5]:
            print("  CC WRONG", a, got[a].det_state, want[a]["det_state"], expected[a])
        st = seq.groupBy("build_status").count().collect()
        print(f"CC {segment}: {len(got):,} classified of {len(want):,} expected; "
              f"{len(miss)} missing/extra, {len(wrong)} wrong; build_status {[tuple(r) for r in st]}")
        if segment == "60_180":
            counts = seq.agg(*[F.sum(c).alias(c) for c in ("n_cycle_shift_moves", "n_gap_months_filled",
                                                          "n_months_truncated", "n_dup_month_rows", "n_invalid_rows")],
                             F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop"),
                             F.sum("restructure_blind_spot_flag").alias("restructured")).first()
            print("   audit:", counts.asDict())

    # ---------------- RL ----------------
    rl_rows, rl_expected = [], {}
    for k, b in enumerate(journeys[: len(journeys) // 2]):
        acc = f"L{k:07d}"
        rlb = [min(max(x, 1), 8) - 1 for x in b]
        start = SNAP_IDX - len(rlb) + 1
        for t, v in enumerate(rlb):
            rl_rows.append((acc, _month_date(start + t, 28).date(), v, 1.0, 1000.0, int(k % 40 == 0), "PL"))
        rl_expected[acc] = rlb
    global_min = min(SNAP_IDX - len(b) + 1 for b in rl_expected.values())
    master = spark.createDataFrame(rl_rows, "account_id string, observation_date date, dpd_bucket int, "
                                            "emi_coverage_ratio double, outstanding_balance double, "
                                            "is_restructured int, loan_type string")
    rl_spine = spark.createDataFrame([(a,) for a in rl_expected], "account_id string")
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"log_stats": True}}
    full = build_rl_full_history(rl_spine, master, params)
    seq = build_rl_dpd_sequences(full, params)
    out = build_rl_a4_deterioration(seq, params)
    got = {r.account_id: r for r in out.collect()}
    want = {}
    for a, rlb in rl_expected.items():
        if max(rlb[-1] + 1, 1) in J.SEGMENTS["60_180"]:
            cropped = SNAP_IDX - len(rlb) + 1 <= global_min
            want[a] = J.classify(rlb, cropped, 1, 8)
    miss = set(want) ^ set(got)
    wrong = [a for a in want if a in got and got[a].det_state != want[a]["det_state"]]
    bad += len(miss) + len(wrong)
    cur = sorted({r.current_bucket for r in got.values()})
    print(f"RL 60_180: {len(got):,} classified of {len(want):,} expected; {len(miss)} missing/extra, "
          f"{len(wrong)} wrong; current RL buckets {cur}")

    # numeric-key trap: a double spine key must still match a string master key
    num_master = master.withColumn(
        "account_id", F.regexp_replace("account_id", "L", "").cast("long").cast("string"))
    num_spine = spark.createDataFrame([(float(a[1:]),) for a in list(rl_expected)[:100]], "account_id double")
    matched = build_rl_full_history(num_spine, num_master).select("account_id").distinct().count()
    print(f"RL double spine key -> string master key: {matched}/100 matched")
    bad += 100 - matched

    # PROD check snippet on a fake catalog (CC with both segments, RL)
    from prod_check import report

    class _Catalog(dict):
        def load(self, name):
            return self[name]

    cat = _Catalog(crx_cc_dpd_sequences=cc_seq,
                   crx_cc_a4_deterioration=cc_outs[0].unionByName(cc_outs[1], allowMissingColumns=True),
                   crx_rl_dpd_sequences=seq, crx_rl_a4_deterioration=out)
    import tempfile
    out_json = pathlib.Path(tempfile.gettempdir()) / "dpd_journey_e2e_results.json"
    text = report(cat, save_json=str(out_json))
    import json
    res = json.loads(out_json.read_text())
    print("results json segments:", {p: sorted(v["segments"]) for p, v in res["products"].items()})
    ok = (text.count("coverage 100.000% [OK]") == 3 and "FAILED" not in text)
    print(f"prod_check report: {'OK' if ok else 'UNEXPECTED'}")
    bad += 0 if ok else 1

    spark.stop()
    print(f"{'SPARK E2E PASSED' if not bad else f'SPARK E2E FAILED ({bad})'} in {time.time() - t0:.0f}s")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 4000))
`````

### FILE: `spark/tests/conftest.py`
sha256 `14104ec1b07262fce76d614832c6c4f0ee1cb358684925bc151b2bd1f352dbe4` · 28 lines · trailing newline: yes

`````python
"""BUNDLE-ONLY (not shipped): lets the shipped tests under tests/nodes/ and tests/pipelines/
import `enbd_collections.pipelines.crx_persona` exactly as they will in the workplace repo,
by mapping that package name onto ../crx_persona (the staged copy).

In the workplace repo the real package is installed, so this file is not copied.
"""
import importlib.util
import pathlib
import sys
import types

_STAGED = pathlib.Path(__file__).resolve().parents[1] / "crx_persona"
_NAME = "enbd_collections.pipelines.crx_persona"

if _NAME not in sys.modules:
    try:
        import enbd_collections  # noqa: F401  — the real package is present: use it
    except ImportError:
        for name in ("enbd_collections", "enbd_collections.pipelines"):
            mod = types.ModuleType(name)
            mod.__path__ = []
            sys.modules[name] = mod
        spec = importlib.util.spec_from_file_location(
            _NAME, _STAGED / "__init__.py", submodule_search_locations=[str(_STAGED)])
        pkg = importlib.util.module_from_spec(spec)
        sys.modules[_NAME] = pkg
        spec.loader.exec_module(pkg)
        sys.modules["enbd_collections.pipelines"].crx_persona = pkg
`````

### FILE: `spark/tests/nodes/crx_persona/conftest.py`
sha256 `4207bdcd56c66cafdd9256cb78c9fc5818d2963928e5f68efe0adf30c48a2ba9` · 27 lines · trailing newline: yes

`````python
"""Local SparkSession for the crx_persona node tests (synthetic data only, no catalog).

If src/tests already provides a session-scoped `spark` fixture, delete this file and the
tests use that one. Needs Java 8/11/17 on the machine (JAVA_HOME) and pyspark >= 3.3.
"""
import os
import sys

import pytest


@pytest.fixture(scope="session")
def spark():
    from pyspark.sql import SparkSession

    os.environ.setdefault("PYSPARK_PYTHON", sys.executable)
    session = (
        SparkSession.builder.master("local[2]")
        .appName("crx_persona_tests")
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.ui.enabled", "false")
        .config("spark.sql.ansi.enabled", "true")      # the strictest setting (Spark 4 default)
        .getOrCreate()
    )
    session.sparkContext.setLogLevel("ERROR")
    yield session
    session.stop()
`````

### FILE: `spark/tests/nodes/crx_persona/test_dpd_journey.py`
sha256 `c261fdc59688991b41eba8708b888803816d3fdc159b55e9f2bb9ef4875b9239` · 188 lines · trailing newline: yes

`````python
"""Unit tests for crx_persona/_dpd_journey.py — self-contained (no Spark session, no data).

Workplace location: src/tests/nodes/crx_persona/test_dpd_journey.py.
Run: python -m pytest src/tests/nodes/crx_persona

The cases are the business edge cases agreed for the deterioration states (option B),
the history-window (crop) cases, the ceiling / unknown rules, and the Stage 1 gap rules.
Exact parity of the engine with the numpy reference was proven separately
(docs/deterioration_states/spark/tests/test_parity.py, recoverable from BUNDLE.md).
"""
from __future__ import annotations

import pytest

from enbd_collections.pipelines.crx_persona import _dpd_journey as J

# (oldest -> newest CC buckets, expected option-B state, why)
CASES = [   ('0 2 0 2 3 4', 'early_payment_default', '3 months incl. one blip, then straight roll'),
    ('0 0 0 2 3 4', 'early_payment_default', '3 clean months, straight roll'),
    ('0 2 3 4 5', 'early_payment_default', '1 clean month'),
    ('0 0 2 0 2 3 4', 'straight_roller_early_life', '4 months of history: too long for EPD'),
    (   '0 0 0 0 0 0 2 3 4',
        'straight_roller_early_life',
        '6 clean months: early-life default, not EPD'),
    ('0 2 0 2 0 2 3 4', 'straight_roller_early_life', 'two blips: not EPD'),
    ('0 2 3 4 0 0 2 3 4 5 6', 'repeat_delinquent', 'paid off from 4, then relapsed'),
    ('0 0 2 2 3 4', 'slow_roller', 'held once on the way down'),
    ('0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5', 'stabilized', 'staircase holding at 4 then one step'),
    ('000000000000002345', 'straight_roller_seasoned', '14 clean months, straight roll'),
    (   '0000000000000234444567',
        'straight_roller_seasoned',
        'held at 4, then rolled 3 buckets: not stable'),
    ('0000000000000023455555', 'stabilized', 'holding at 5'),
    ('00000000234443345433456554', 'stabilized', 'oscillating payer (example 1)'),
    (   '00000000234443345433456654',
        'stabilized',
        'oscillating payer that just paid down 6-5-4 (example 2)'),
    (   '0 0 2 3 4 4 4 4 4 4',
        'stabilized',
        'entered like EPD but pays the monthly due since: not EPD'),
    (   '0 0 2 3 4 4 5 6',
        'straight_roller_early_life',
        'entered like EPD, paid once at 4: EPD needs no payment'),
    ('4 5 6 7', 'unknown', 'string starts delinquent (restructured / missing history)'),
    ('4 4 4 4 4 5', 'stabilized', 'starts delinquent but holding: stabilized needs only 6 months'),
    ('0 0 0 2 3 4 4 4 4 4', 'stabilized', 'journey observed from 0 DPD, holding at 4'),
    (   '0000000000000000224',
        'straight_roller_seasoned',
        '+2 jump after a hold at 2: repaired to 2 3 4'),
    (   '00000000000000002244',
        'straight_roller_seasoned',
        'same account a month later: fixed state must not change'),
    ('000034', 'straight_roller_early_life', 'jump from clean to 3: no clean month is borrowed'),
    (   '0 2 3 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 2 3 4',
        'straight_roller_seasoned',
        'cured 20 months earlier: outside 12-month window'),
    (   '0 2 3 4 0 0 0 0 0 0 0 0 2 3 4 5',
        'repeat_delinquent',
        'cured 8 months earlier: repeat delinquent'),
    (   '0000000000000000 2 3 4 4 0 4 5',
        'stabilized',
        'single 0 inside a spell at 4 is a glitch, not a cure'),
    (   '0000 3 0000000000000 2 3 4',
        'straight_roller_seasoned',
        'single spike 0 3 0 is a glitch, not an earlier spell')]

# (oldest -> newest, months kept by the history window, expected option-B state, why)
CROP_CASES = [   (   '00000000002344545454545454545454545454545454545454',
        32,
        'stabilized',
        'spell older than the window: not a data-quality case; long-run holder -> stabilized'),
    (   '0000000000000000000000000000000000000000234',
        32,
        'straight_roller_seasoned',
        'long clean history cropped: still seasoned'),
    (   '0000000000234',
        6,
        'straight_roller_seasoned',
        'cropped to 0 0 0 2 3 4: looks like EPD, but older than the window'),
    ('0 0 0 2 3 4', 32, 'early_payment_default', 'short history, not cropped: EPD')]

# 180+ segment: the SAME tree and vocabulary as 60-180; no stabilized at 180+; holds at the
# ceiling (CC 9, RL 7) are not payments
CASES_180 = [
    ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 9] + [9] * 12, "straight_roller_seasoned"),
    ("cc", [0] * 20 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], "straight_roller_seasoned"),   # holding at 8: NOT stabilized
    ("cc", [8, 9, 9, 9, 9, 9, 9], "unknown"),                                             # journey start not observed
    ("cc", [0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9, 9], "early_payment_default"),                # cap holds are not payments
    ("cc", [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 8, 9], "straight_roller_early_life"),        # 9 -> 8 is a payment
    ("rl", [0] * 20 + [1, 2, 3, 4, 5, 6, 7, 7, 7], "straight_roller_seasoned"),
    ("rl", [7, 7, 7, 7], "unknown"),
    ("rl", [0, 0, 1, 2, 3, 4, 5, 6, 7, 7, 7, 7], "early_payment_default"),
    ("rl", [0] * 20 + [1, 2, 3, 4, 5] + [6] * 12 + [7, 7], "straight_roller_seasoned"),
    ("rl", [0] * 20 + [1, 1, 2, 2, 3, 4, 5, 6, 7], "slow_roller"),
]
SCHEME = {"cc": (0, 9), "rl": (1, 8)}     # (offset, canonical cap)


def _to_rl(cc: list[int]) -> list[int]:
    """CC buckets -> RL native (CC 0/1 -> 0, CC 2 -> 1, ..., CC 8/9 -> 7)."""
    return [min(max(x, 1), 8) - 1 for x in cc]


def _chron(text: str) -> list[int]:
    return [int(ch) for ch in text.replace(" ", "")]


@pytest.mark.parametrize("chron,want,why", CASES)
@pytest.mark.parametrize("product", ["cc", "rl"])
def test_business_case(product, chron, want, why):
    b = _chron(chron)
    buckets = b if product == "cc" else _to_rl(b)
    off, top = SCHEME[product]
    assert J.classify(buckets, False, off, top)["det_state"] == want, why


@pytest.mark.parametrize("chron,n,want,why", CROP_CASES)
def test_crop_case(chron, n, want, why):
    b = _chron(chron)
    got = J.classify(b[-n:], len(b) >= n, 0, 9)["det_state"]
    assert got == want, why


@pytest.mark.parametrize("product,buckets,want", CASES_180)
def test_180_and_ceiling(product, buckets, want):
    off, top = SCHEME[product]
    assert J.classify(buckets, False, off, top)["det_state"] == want


def test_one_vocabulary_and_no_stabilized_at_180():
    """Both segments use the same 7 states; stabilized never occurs at 180+ (CC 8-9, RL 7)."""
    assert list(J.DISPLAY_NAMES) == J.STATES and len(J.STATES) == 7
    holds = [[0] * 20 + [2, 3, 4, 5, 6, 7] + [top] * k for top in (8, 9) for k in range(1, 13)]
    for b in holds + [c for _, c, _ in CASES_180 if _ == "cc"]:
        st = J.classify(b, False, 0, 9)["det_state"]
        assert st in J.STATES
        if max(b[-1], 1) >= 8:
            assert st != "stabilized", b
    for b in [[0] * 20 + [1, 2, 3, 4, 5, 6] + [7] * k for k in range(1, 13)]:
        assert J.classify(b, False, 1, 8)["det_state"] != "stabilized", b


def _hist(rows, first_raw=None, gmin=0, offset=0, fill=True, how="truncate", max_inf=2):
    first_raw = first_raw if first_raw is not None else min(r[0] for r in rows)
    return J.build_history(rows, first_raw, gmin, offset, fill, how, True, max_inf)


@pytest.mark.parametrize("kwargs,check", [
    (dict(rows=[(100, 1, 3), (101, 5, 4), (101, 9, 5), (102, 1, 5)]),
     lambda r: r["buckets"] == [3, 5, 5] and r["n_dup_month_rows"] == 1),            # latest in month wins
    (dict(rows=[(100, 1, 3), (101, 5, 4), (101, 5, 6), (102, 1, 6)]),
     lambda r: r["buckets"] == [3, 6, 6]),                                           # same day: worst wins
    (dict(rows=[(100, 1, 4), (102, 1, 4)]),
     lambda r: r["buckets"] == [4, 4, 4] and r["n_gap_months_filled"] == 1),         # hold through
    (dict(rows=[(100, 1, 0), (102, 1, 1)]),
     lambda r: r["buckets"] == [0, 0, 1] and r["n_months_truncated"] == 0),          # CC 0 _ 1 is clean
    (dict(rows=[(100, 1, 3), (103, 1, 6)]),
     lambda r: r["buckets"] == [3, 4, 5, 6] and r["n_gap_months_rolled"] == 2),      # straight roll
    (dict(rows=[(100, 1, 0), (102, 1, 2)], offset=1),
     lambda r: r["buckets"] == [0, 1, 2]),                                           # RL straight roll
    (dict(rows=[(100, 1, 0), (101, 1, 0), (105, 1, 4), (106, 1, 5)]),
     lambda r: r["buckets"] == [4, 5] and r["n_months_truncated"] == 5
     and r["history_cropped"] and r["legacy_drop"]),                                 # unresolvable: truncate
    (dict(rows=[(100, 1, 3), (102, 1, 4)]),
     lambda r: r["buckets"] == [3, 3, 4] and r["n_gap_months_inferred"] == 1),       # inferred, roll late
    (dict(rows=[(100, 1, 6), (103, 1, 3)]),
     lambda r: r["buckets"] == [6, 6, 6, 3] and r["n_gap_months_inferred"] == 2),    # carry, pay at end
    (dict(rows=[(100, 1, 3), (102, 1, 4)], max_inf=0),
     lambda r: r["buckets"] == [4] and r["n_months_truncated"] == 2),                # inference off
    (dict(rows=[(100, 30, 2), (101, 60, 3), (101, 61, 4), (103, 90, 5)]),
     lambda r: r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1),      # cycle shift forward
    (dict(rows=[(100, 1, 2), (102, 50, 3), (102, 80, 4), (103, 90, 5)]),
     lambda r: r["buckets"] == [2, 3, 4, 5] and r["n_cycle_shift_moves"] == 1),      # cycle shift back
    (dict(rows=[(100, 1, 0), (102, 1, 4)], how="drop", max_inf=0),
     lambda r: r["build_status"] == "dropped_unresolvable_gap"),
    (dict(rows=[(100, 1, 0), (101, 1, 2)], fill=False),
     lambda r: r["history_cropped"] is False),
    (dict(rows=[(110, 1, 0), (111, 1, 2)], first_raw=90),
     lambda r: r["history_cropped"]),                                                # older rows before the floor
    (dict(rows=[(110, 1, 0), (111, 1, 2)], gmin=110),
     lambda r: r["history_cropped"]),                                                # starts with the source
])
def test_build_history(kwargs, check):
    assert check(_hist(**kwargs))


def test_build_history_empty():
    assert J.build_history([], 100, 0, 0)["build_status"] == "no_rows_in_window"
`````

### FILE: `spark/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py`
sha256 `7b1502e612df6e6de2a2ef540d303e30b0a7df014f2a65096a7b1cd18c5be303` · 197 lines · trailing newline: yes

`````python
"""Spark tests for the crx_persona deterioration nodes — synthetic data, no catalog, no PROD.

Workplace location: src/tests/nodes/crx_persona/test_dpd_journey_spark_nodes.py.
Run: python -m pytest src/tests/nodes/crx_persona   (needs Java + pyspark >= 3.3)

Builds raw tables the way the sources look (CC billing with add_info, RL monthly loan
master) with their known noise — same-day duplicates, unparseable add_info, billing-cycle
shifts, months missing between equal neighbours, unresolvable gaps, history before the CC
floor, double spine keys — runs the node functions end to end, and checks every account
against the per-account engine (itself covered by test_dpd_journey.py).
"""
from __future__ import annotations

import datetime as dt
import random

import pytest
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona import _dpd_journey as J
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.nodes import (
    build_cc_a4_deterioration, build_cc_dpd_sequences)
from enbd_collections.pipelines.crx_persona.cc_full_history.nodes import build_cc_full_history
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.nodes import (
    build_rl_a4_deterioration, build_rl_dpd_sequences)
from enbd_collections.pipelines.crx_persona.rl_full_history.nodes import build_rl_full_history

SNAP = dt.date(2026, 8, 31)
SNAP_IDX = SNAP.year * 12 + SNAP.month - 1
FLOOR_IDX = 2024 * 12                      # 2024-01, the CC history floor default
N = 600


def _journey(rng: random.Random) -> list[int]:
    """One CC journey, oldest -> newest, ending in the 60-180 or 180+ segment."""
    b = [0] * rng.randint(0, 60)
    if rng.random() < 0.25:                                    # an earlier cured spell
        b += [2, 3][: rng.randint(1, 2)] + [0] * rng.randint(1, 20)
    level = 2
    b.append(level)
    target = rng.choice([4, 5, 6, 7, 7, 9])
    while level < target:
        u = rng.random()
        if u < 0.7:
            level += 1                                         # roll
        elif u < 0.9 or level < 4:
            pass                                               # hold
        else:
            level -= 1                                         # pay two months
        b.append(level)
    for _ in range(rng.randint(0, 14)):                        # life in the segment
        u = rng.random()
        if target == 9 or u < 0.5:
            pass
        elif u < 0.8 and level < 7:
            level += 1
        elif level > 4:
            level -= 1
        b.append(level)
    if rng.random() < 0.05:
        b = [rng.choice([4, 5, 9])] * rng.randint(3, 10)       # history starts delinquent
    return b


def _month(idx: int, day: int) -> dt.datetime:
    y, m = divmod(idx, 12)
    return dt.datetime(y, m + 1, day)


@pytest.fixture(scope="module")
def journeys():
    rng = random.Random(11)
    return [_journey(rng) for _ in range(N)]


def _cc_raw(journeys):
    """raw_stg_billing rows and the expected (kept history, cropped) per account."""
    rng = random.Random(5)
    rows, expected = [], {}
    for k, b in enumerate(journeys):
        acc = 900_000_000 + k
        start = SNAP_IDX - len(b) + 1
        months = {start + t: v for t, v in enumerate(b)}
        bills = [(m, 15, v) for m, v in months.items()]
        first_kept = max(start, FLOOR_IDX)
        interior = [m for m in months if first_kept + 1 < m < SNAP_IDX - 4]
        u = rng.random()
        if u < 0.10 and len(interior) > 2:                     # billing-cycle shift
            m = rng.choice(interior)
            bills = [x for x in bills if x[0] != m] + [(m + 1, 1, months[m])]
        elif u < 0.20 and len(interior) > 2:                   # gap between equal neighbours
            cand = [m for m in interior if months[m - 1] == months[m] == months[m + 1]]
            if cand:
                bills = [x for x in bills if x[0] != rng.choice(cand)]
        elif u < 0.25 and len(interior) > 6:                   # unresolvable 3-month gap
            m = interior[len(interior) // 2 - 3]
            cl, cr = max(months[m - 1], 1), max(months[m + 3], 1)
            if cl != cr and cr - cl != 4:
                bills = [x for x in bills if not m <= x[0] <= m + 2]
                first_kept = max(first_kept, m + 3)
        for m, day, v in bills:
            rows.append((float(acc), _month(m, day), f"A=1;BS_PMT_CYCLE_DUE={v};B=2"))
            if rng.random() < 0.03:
                rows.append((float(acc), _month(m, day), f"A=1;BS_PMT_CYCLE_DUE={v};B=2"))
            if rng.random() < 0.03:
                rows.append((float(acc), _month(m, day), "A=1;NO_BUCKET"))
        kept = [months[m] for m in range(first_kept, SNAP_IDX + 1)]
        expected[acc] = (kept, first_kept > start)
    return rows, expected


@pytest.fixture(scope="module")
def cc(spark, journeys):
    rows, expected = _cc_raw(journeys)
    raw = spark.createDataFrame(rows, "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(float(a),) for a in expected], "contract_id double")
    spells = spark.createDataFrame(
        [(a, "restructured_entry" if a % 37 == 0 else "none") for a in expected],
        "account_id long, censored_subtype string")
    return raw, spine, spells, expected


@pytest.mark.parametrize("segment", ["60_180", "180_plus"])
def test_cc_end_to_end(cc, segment):
    raw, spine, spells, expected = cc
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"segment": segment}}
    seq = build_cc_dpd_sequences(build_cc_full_history(raw, spine), spells, params)
    got = {r.account_id: r for r in build_cc_a4_deterioration(seq, params).collect()}
    want = {a: J.classify(k, c, 0, 9)
            for a, (k, c) in expected.items() if max(k[-1], 1) in J.SEGMENTS[segment]}
    assert set(got) == set(want), "every account in the segment is classified, no others"
    for a, w in want.items():
        assert got[a].det_state == w["det_state"], (a, expected[a])
        assert got[a].history_cropped == expected[a][1], a
        assert got[a].det_state_label == J.DISPLAY_NAMES[w["det_state"]]
    assert {r.det_state for r in got.values()} <= set(J.STATES)
    if segment == "180_plus":
        assert "stabilized" not in {r.det_state for r in got.values()}
    statuses = {r.build_status for r in seq.select("build_status").distinct().collect()}
    assert statuses == {"ok"}, "no account dropped"


def test_cc_audit_columns(cc):
    raw, spine, spells, _ = cc
    params = {"persona_end_date": str(SNAP)}
    seq = build_cc_dpd_sequences(build_cc_full_history(raw, spine), spells, params)
    r = seq.agg(*[F.sum(c).alias(c) for c in ("n_cycle_shift_moves", "n_gap_months_filled",
                                              "n_months_truncated", "restructure_blind_spot_flag")],
                F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop")).first()
    assert r.n_cycle_shift_moves > 0 and r.n_gap_months_filled > 0 and r.n_months_truncated > 0
    assert r.legacy_drop > 0, "the old rule would have dropped some of these accounts"
    assert r.restructure_blind_spot_flag == len([a for a in cc[3] if a % 37 == 0])


def test_cc_full_history_dedupe_and_bad_rows(spark):
    raw = spark.createDataFrame([
        (1.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=3"),
        (1.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=4"),     # same date: worst wins
        (1.0, dt.datetime(2025, 2, 15), "NO_BUCKET"),               # unparseable: NULL, no error
        (2.0, dt.datetime(2025, 1, 15), "BS_PMT_CYCLE_DUE=2"),      # not in the spine
    ], "contract_idt double, billing_date timestamp, add_info string")
    spine = spark.createDataFrame([(1.0,)], "contract_id double")
    out = {(r.billing_date.month, r.dlq_bucket) for r in build_cc_full_history(raw, spine).collect()}
    assert out == {(1, 4), (2, None)}


@pytest.mark.parametrize("segment", ["60_180", "180_plus"])
def test_rl_end_to_end(spark, journeys, segment):
    rows, want = [], {}
    rl = {f"L{k:07d}": [min(max(x, 1), 8) - 1 for x in b] for k, b in enumerate(journeys)}
    global_min = min(SNAP_IDX - len(b) + 1 for b in rl.values())
    for acc, b in rl.items():
        start = SNAP_IDX - len(b) + 1
        rows += [(acc, _month(start + t, 28).date(), v, 1.0, 100.0, 0, "PL") for t, v in enumerate(b)]
        if max(b[-1] + 1, 1) in J.SEGMENTS[segment]:
            want[acc] = J.classify(b, start <= global_min, 1, 8)["det_state"]
    master = spark.createDataFrame(rows, "account_id string, observation_date date, dpd_bucket int, "
                                         "emi_coverage_ratio double, outstanding_balance double, "
                                         "is_restructured int, loan_type string")
    spine = spark.createDataFrame([(a,) for a in rl], "account_id string")
    params = {"persona_end_date": str(SNAP), "dpd_journey": {"segment": segment}}
    seq = build_rl_dpd_sequences(build_rl_full_history(spine, master, params), params)
    got = {r.account_id: r for r in build_rl_a4_deterioration(seq, params).collect()}
    assert {a: r.det_state for a, r in got.items()} == want
    allowed = set(J.RL.native_buckets(J.SEGMENTS[segment]))
    assert {r.current_bucket for r in got.values()} <= allowed
    if segment == "180_plus":
        assert "stabilized" not in set(want.values())


def test_rl_double_spine_key_matches_string_master(spark):
    master = spark.createDataFrame(
        [(str(123456789 + k), dt.date(2026, 8, 31), 3, 1.0, 1.0, 0, "PL") for k in range(20)],
        "account_id string, observation_date date, dpd_bucket int, emi_coverage_ratio double, "
        "outstanding_balance double, is_restructured int, loan_type string")
    spine = spark.createDataFrame([(float(123456789 + k),) for k in range(20)], "account_id double")
    assert build_rl_full_history(spine, master).select("account_id").distinct().count() == 20
`````

### FILE: `spark/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py`
sha256 `24e6b6b0e9e2429f0d62a1157e0c17bf59763f3970bc425236884fb9209e9d9b` · 61 lines · trailing newline: yes

`````python
"""Wiring of the CC / RL deterioration pipelines — no Spark, no data.

Workplace location: src/tests/pipelines/crx_persona/test_a4_deterioration_pipelines.py.
Run: python -m pytest src/tests/pipelines/crx_persona
"""
import pytest

from enbd_collections.pipelines.crx_persona import _dpd_journey as J
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration import nodes as cc_nodes
from enbd_collections.pipelines.crx_persona.cc_a4_deterioration.pipeline import (
    create_pipeline as create_cc_pipeline)
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration import nodes as rl_nodes
from enbd_collections.pipelines.crx_persona.rl_a4_deterioration.pipeline import (
    create_pipeline as create_rl_pipeline)

EXPECTED = {
    "cc": (create_cc_pipeline, [
        ("build_crx_cc_dpd_sequences", cc_nodes.build_cc_dpd_sequences,
         ["crx_cc_full_history", "crx_cc_spell_table", "params:crx_persona"], ["crx_cc_dpd_sequences"]),
        ("build_crx_cc_a4_deterioration", cc_nodes.build_cc_a4_deterioration,
         ["crx_cc_dpd_sequences", "params:crx_persona"], ["crx_cc_a4_deterioration"]),
    ]),
    "rl": (create_rl_pipeline, [
        ("build_crx_rl_dpd_sequences", rl_nodes.build_rl_dpd_sequences,
         ["crx_rl_full_history", "params:crx_persona"], ["crx_rl_dpd_sequences"]),
        ("build_crx_rl_a4_deterioration", rl_nodes.build_rl_a4_deterioration,
         ["crx_rl_dpd_sequences", "params:crx_persona"], ["crx_rl_a4_deterioration"]),
    ]),
}


@pytest.mark.parametrize("product", sorted(EXPECTED))
def test_pipeline_wiring(product):
    create, spec = EXPECTED[product]
    pipe = create()
    by_name = {n.name.split(".")[-1]: n for n in pipe.nodes}     # namespaced names end in the node name
    assert set(by_name) == {name for name, *_ in spec}
    for name, func, inputs, outputs in spec:
        n = by_name[name]
        assert n.func is func
        assert n.inputs == inputs
        assert n.outputs == outputs
        assert {"crx", product, "crx_persona"} <= set(n.tags)


@pytest.mark.parametrize("product", sorted(EXPECTED))
def test_sequences_run_before_classification(product):
    pipe = EXPECTED[product][0]()
    order = [n.name.split(".")[-1] for n in pipe.nodes]          # Kedro returns topological order
    assert order.index(f"build_crx_{product}_dpd_sequences") < order.index(f"build_crx_{product}_a4_deterioration")


def test_params_defaults_are_valid():
    """The params the nodes read: defaults resolve, and a bad value fails loudly."""
    p = J.journey_params({"persona_end_date": "2026-08-31"}, J.CC)
    assert p.floor_date == "2024-01-01" and p.segment == "60_180"
    assert J.journey_params({"persona_end_date": "2026-08-31"}, J.RL).floor_date is None
    with pytest.raises(ValueError):
        J.journey_params({"persona_end_date": "2026-08-31", "dpd_journey": {"segment": "90_plus"}}, J.CC)
    with pytest.raises(ValueError):    # stale key from the old A/B/C options must not pass silently
        J.journey_params({"persona_end_date": "2026-08-31", "dpd_journey": {"det_option": "B_balanced_6"}}, J.CC)
`````

### FILE: `spark/prod_check.py`
sha256 `3d186a02806858ec3a665802b4d2d1e006e1dbbe3f79370841285e00530a3209` · 132 lines · trailing newline: yes

`````python
"""PROD check — run by a person with PROD access, AFTER the pipelines have run.

    kedro run --pipeline=crx_cc_a4_deterioration      # and/or crx_rl_a4_deterioration

Then, in a Kedro notebook / `kedro ipython` session where `catalog` exists:

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "spark"))
    from prod_check import report
    report(catalog)                       # CC and RL; report(catalog, products=("cc",)) for one
    report(catalog, save_json="dpd_journey_results.json")   # also save the counts for the
                                                             # stakeholder workbook (aggregates only)

READ-ONLY. Prints AGGREGATES ONLY (counts and shares — no account ids, no DPD strings)
between === DPD_JOURNEY PROD CHECK START / END ===. Paste that block back for review.
Datasets read: crx_<p>_dpd_sequences and crx_<p>_a4_deterioration (the pipeline outputs).
"""
import datetime
import json

from pyspark.sql import functions as F

TARGET_COVERAGE = 0.999


def _pct(x, n):
    return f"{x:,} ({x / n:.2%})" if n else f"{x:,}"


def _product(catalog, p: str, store: dict) -> list[str]:
    seq = catalog.load(f"crx_{p}_dpd_sequences")
    out = catalog.load(f"crx_{p}_a4_deterioration")
    lines = [f"## {p.upper()}"]

    # -- Node 1: every account in the history, with a build status ----------------------
    s = seq.agg(
        F.count("*").alias("accounts"),
        F.sum((F.col("build_status") == "ok").cast("int")).alias("ok"),
        F.sum(F.col("legacy_drop").cast("int")).alias("legacy_drop"),
        F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated"),
        F.sum((F.col("n_cycle_shift_moves") > 0).cast("int")).alias("acc_cycle_shift"),
        F.sum((F.col("n_gap_months_filled") > 0).cast("int")).alias("acc_gap_filled"),
        F.sum((F.col("n_gap_months_rolled") > 0).cast("int")).alias("acc_gap_rolled"),
        F.sum((F.col("n_gap_months_inferred") > 0).cast("int")).alias("acc_gap_inferred"),
        F.sum((F.col("n_invalid_rows") > 0).cast("int")).alias("acc_invalid_rows"),
        F.min("first_month").alias("first_month"),
        F.max("last_month").alias("last_month"),
        F.expr("percentile_approx(history_months, array(0.05, 0.5, 0.95))").alias("history_months_p05_p50_p95"),
    ).first().asDict()
    n = s["accounts"]
    store[p] = {"sequences": {k: (str(v) if k in ("first_month", "last_month") else v)
                              for k, v in s.items()}, "segments": {}}
    lines.append(f"sequences: {n:,} accounts, months {s['first_month']} .. {s['last_month']}, "
                 f"history months p05/p50/p95 {s['history_months_p05_p50_p95']}")
    lines.append("build_status: " + ", ".join(
        f"{r['build_status']} {_pct(r['count'], n)}"
        for r in seq.groupBy("build_status").count().orderBy(F.desc("count")).collect()))
    lines.append(f"old rule would have dropped: {_pct(s['legacy_drop'], n)}")
    lg = seq.where("legacy_drop").agg(
        F.count("*").alias("n"),
        F.sum((F.col("n_cycle_shift_moves") > 0).cast("int")).alias("cycle_shift"),
        F.sum((F.col("n_gap_months_rolled") > 0).cast("int")).alias("straight_roll"),
        F.sum((F.col("n_gap_months_inferred") > 0).cast("int")).alias("inferred"),
        F.sum((F.col("n_months_truncated") > 0).cast("int")).alias("truncated"),
        F.expr("percentile_approx(n_months_truncated, 0.5)").alias("median_months_truncated"),
    ).first().asDict()
    lines.append(f"  of those, now resolved by (an account can have several): {lg}")
    lines.append(f"cropped {_pct(s['cropped'], n)}; truncated at a gap {_pct(s['truncated'], n)}; "
                 f"accounts with cycle-shift repair {_pct(s['acc_cycle_shift'], n)}, gap filled "
                 f"{_pct(s['acc_gap_filled'], n)}, straight-roll fill {_pct(s['acc_gap_rolled'], n)}, "
                 f"inferred fill {_pct(s['acc_gap_inferred'], n)}, invalid bucket rows {_pct(s['acc_invalid_rows'], n)}")

    # -- Node 2: coverage and state shares ------------------------------------------------
    segs = [r["det_segment"] for r in out.select("det_segment").distinct().collect()]
    for seg in segs or ["(empty output)"]:
        o = out.where(F.col("det_segment") == seg)
        m = o.count()
        cur = [r["current_bucket"] for r in o.select("current_bucket").distinct().collect()]
        # accounts whose latest bucket is in this segment but that were NOT classified
        in_seg = seq.where(F.element_at("dlq_buckets", -1).isin(cur)) if cur else seq.limit(0)
        lost = in_seg.where(F.col("build_status") != "ok").count()
        cov = m / (m + lost) if (m + lost) else 0.0
        lines.append(f"### segment {seg} (current buckets {sorted(cur)}): {m:,} classified, "
                     f"{lost:,} in segment but not classified -> coverage {cov:.3%} "
                     f"[{'OK' if cov >= TARGET_COVERAGE else 'BELOW 99.9%'}]")
        lines.append("| state | accounts | share |")
        lines.append("|---|---|---|")
        counts = o.groupBy("det_state").count().orderBy(F.desc("count")).collect()
        for r in counts:
            lines.append(f"| {r['det_state']} | {r['count']:,} | {r['count'] / m:.1%} |")
        store[p]["segments"][seg] = {"classified": m, "in_segment_not_classified": lost,
                                     "state_counts": {r["det_state"]: r["count"] for r in counts}}
        q = o.agg(
            F.avg(F.col("starts_delinquent").cast("double")).alias("starts_delinquent"),
            F.avg(F.col("history_cropped").cast("double")).alias("cropped"),
            F.avg((F.col("history_stale_months") > 1).cast("double")).alias("stale_over_1m"),
            F.avg(F.col("restructure_blind_spot_flag").cast("double")).alias("restructured"),
            F.avg((F.col("n_glitches") > 0).cast("double")).alias("glitch_fixed"),
            F.avg((F.col("n_jumps_repaired") > 0).cast("double")).alias("jump_repaired"),
        ).first().asDict()
        lines.append("shares: " + ", ".join(f"{k} {v:.1%}" for k, v in q.items() if v is not None))
        lines.append("state x starts_delinquent / cropped (shares within state):")
        for r in (o.groupBy("det_state").agg(
                F.avg(F.col("starts_delinquent").cast("double")).alias("sd"),
                F.avg(F.col("history_cropped").cast("double")).alias("cr"))
                .orderBy("det_state").collect()):
            lines.append(f"  {r['det_state']}: starts_delinquent {r['sd']:.1%}, cropped {r['cr']:.1%}")
    return lines


def report(catalog, products=("cc", "rl"), save_json: str | None = None) -> str:
    """Print the check; with save_json, also write the counts (aggregates only) to that path —
    the input of the stakeholder workbook's Results sheet."""
    lines = ["=== DPD_JOURNEY PROD CHECK START ==="]
    store: dict = {}
    for p in products:
        try:
            lines += _product(catalog, p, store)
        except Exception as exc:          # one product failing must not hide the other
            lines.append(f"## {p.upper()}: FAILED — {type(exc).__name__}: {str(exc)[:300]}")
    lines.append("=== DPD_JOURNEY PROD CHECK END ===")
    text = "\n".join(lines)
    print(text)
    if save_json:
        payload = {"generated": datetime.date.today().isoformat(), "products": store}
        with open(save_json, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2, default=str)
        print(f"saved {save_json}")
    return text
`````

### FILE: `spark/stakeholder/build_states_workbook.py`
sha256 `04a9351b09da6dc26d9c80f86c0ca0df4eb030d61bfd418ba81834069821f0bc` · 660 lines · trailing newline: yes

`````python
"""Build the stakeholder workbook for the DPD deterioration states (the 'deterioration axis').

    python build_states_workbook.py --out dpd_deterioration_states_<date>.xlsx \
        [--results results_60_180.json --results results_180_plus.json] [--scoring-date "Aug 2026"]

Everything rule-related is read from the deployed engine, so the workbook cannot drift from
the pipeline: thresholds come from STATE_RULES / PARAM_DEFAULTS, and every worked example is
run through classify() — the build FAILS if an example no longer gets the state it
illustrates. Results (counts per product x segment x state) come from the JSON that
prod_check.report(catalog, save_json=...) writes in PROD (aggregates only); without it the
Results sheet is left for manual entry. Shares and coverage are Excel formulas.

The engine is imported from the repo package (enbd_collections.pipelines.crx_persona) or,
when run from the bundle, from ../crx_persona/_dpd_journey.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import pathlib
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.worksheet import Worksheet


def _engine():
    try:
        from enbd_collections.pipelines.crx_persona import _dpd_journey as J  # noqa: N811
        return J
    except ImportError:
        path = pathlib.Path(__file__).resolve().parents[1] / "crx_persona" / "_dpd_journey.py"
        spec = importlib.util.spec_from_file_location("_dpd_journey", path)
        mod = importlib.util.module_from_spec(spec)
        sys.modules["_dpd_journey"] = mod          # dataclasses need the module registered
        spec.loader.exec_module(mod)
        return mod


J = _engine()

# --- look ----------------------------------------------------------------------------------
FONT = "Arial"
NAVY, GREY, LIGHT, RULE = "1F3864", "595959", "F2F2F2", "BFBFBF"
STATE_COLOUR = {                      # one colour per state, used on every sheet
    "unknown": "A6A6A6",
    "early_payment_default": "C00000",
    "stabilized": "548235",
    "repeat_delinquent": "C55A11",
    "straight_roller_seasoned": "2F5597",
    "straight_roller_early_life": "8FAADC",
    "slow_roller": "7030A0",
}
BUCKET_FILL = {0: "FFFFFF", 1: "FFFFFF", 2: "FFF2CC", 3: "FFE699", 4: "F8CBAD", 5: "F4B183",
               6: "ED7D31", 7: "C55A11", 8: "843C0C", 9: "3B1A06"}
THIN = Side(style="thin", color=RULE)
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CENTER = Alignment(horizontal="center", vertical="center", wrap_text=True)


def _font(**kw) -> Font:
    return Font(name=FONT, size=kw.pop("size", 10), **kw)


def _fill(hex_: str) -> PatternFill:
    return PatternFill("solid", start_color=hex_, end_color=hex_)


def _text_on(hex_: str) -> str:
    r, g, b = (int(hex_[i:i + 2], 16) for i in (0, 2, 4))
    return "FFFFFF" if (0.299 * r + 0.587 * g + 0.114 * b) < 150 else "000000"


def _title(ws: Worksheet, title: str, subtitle: str, width_cols: int) -> int:
    ws["A1"] = title
    ws["A1"].font = _font(size=16, bold=True, color=NAVY)
    ws["A2"] = subtitle
    ws["A2"].font = _font(size=10, italic=True, color=GREY)
    ws["A2"].alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=width_cols)
    ws.row_dimensions[2].height = 30
    ws.sheet_view.showGridLines = False
    return 4


def _section(ws: Worksheet, row: int, text: str, width_cols: int) -> int:
    c = ws.cell(row=row, column=1, value=text)
    c.font = _font(size=12, bold=True, color=NAVY)
    for col in range(1, width_cols + 1):
        ws.cell(row=row, column=col).border = Border(bottom=Side(style="medium", color=NAVY))
    return row + 1


def _header(ws: Worksheet, row: int, labels: list[str]) -> int:
    for i, lab in enumerate(labels, 1):
        c = ws.cell(row=row, column=i, value=lab)
        c.font = _font(bold=True, color="FFFFFF")
        c.fill = _fill(NAVY)
        c.alignment = CENTER
        c.border = BOX
    return row + 1


def _row(ws: Worksheet, row: int, values: list, bold_first: bool = False, height: float | None = None) -> int:
    for i, v in enumerate(values, 1):
        c = ws.cell(row=row, column=i, value=v)
        c.font = _font(bold=bold_first and i == 1)
        c.alignment = WRAP
        c.border = BOX
    if height:
        ws.row_dimensions[row].height = height
    return row + 1


def _chip(cell, state: str, label: str | None = None) -> None:
    cell.value = label or J.DISPLAY_NAMES[state]
    cell.fill = _fill(STATE_COLOUR[state])
    cell.font = _font(bold=True, color=_text_on(STATE_COLOUR[state]))
    cell.alignment = Alignment(wrap_text=True, vertical="center")
    cell.border = BOX


def _widths(ws: Worksheet, widths: list[float]) -> None:
    for i, w in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = w


def _print(ws: Worksheet) -> None:
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True


# --- content -------------------------------------------------------------------------------
R = J.STATE_RULES
FLOOR = J.PARAM_DEFAULTS["cc_history_floor_date"]
CC_WINDOW = dt.date.fromisoformat(FLOOR).strftime("%b %Y") if FLOOR else "the start of the data"
RL_WINDOW = "Jan 2019"     # RL history window start (set in the workplace params, not the bundle defaults)
WINDOWS = f"CC {CC_WINDOW}, RL {RL_WINDOW}"

# Workbook labels: the engine's display names, with workbook-only overrides.
LABELS = {**J.DISPLAY_NAMES, "unknown": "Unknown", "repeat_delinquent": "Repeat delinquent"}

STATE_TEXT = {   # state: (one sentence, typical action, changes over time)
    "unknown": (
        "We cannot see how the account fell into delinquency: the start of this delinquency "
        "is not in the history we hold.",
        "Treat on current behaviour and the other persona axes.",
        "Fixed"),
    "early_payment_default": (
        f"Fell behind within {R['epd_max_history']} months of the start of its history and has "
        "not paid since.",
        "Early-risk / first-party fraud review; early legal; no restructuring.",
        "Current: ends when the customer pays"),
    "stabilized": (
        "Paying about one month's due each month: the bucket has stopped climbing. "
        "61–180 DPD only.",
        "Offer restructuring.",
        "Current: re-read monthly"),
    "repeat_delinquent": (
        f"Was 31+ DPD before, caught up, and fell back within {R['repeat_window_months']} months.",
        "Firm promise-based plan; credibility sets the pressure.",
        "Fixed"),
    "straight_roller_seasoned": (
        f"Rolled straight to 61+ DPD (no payment), {R['seasoned_min_months']}+ months after its "
        "history began.",
        "Likely a life event: read with the other axes; best fit for a hardship route.",
        "Fixed"),
    "straight_roller_early_life": (
        f"Rolled straight to 61+ DPD within its first {R['seasoned_min_months']} months (after "
        "the EPD window).",
        "As seasoned; also an underwriting signal.",
        "Fixed"),
    "slow_roller": (
        "Paid something on the way to 61+ DPD but kept rolling.",
        "Over-indebted: longer-tenor restructure or settlement.",
        "Fixed"),
}

STEPS = [   # (step, question, state on yes, exact test)
    ("0", "Is the start of this delinquency missing?", "unknown",
     "Oldest month we hold is already overdue (CC 1+ DPD; RL 31+ DPD). "
     "Stabilized if Step 2 passes, else Unknown."),
    ("1", "Early payment default?", "early_payment_default",
     f"Fell behind within {R['epd_max_history']} months of the start of its history, with no "
     "earlier delinquency (one short paid-off slip allowed), and has not paid since: one bucket "
     "worse every month."),
    ("2", "Stabilized?", "stabilized",
     "Today 61–180 DPD and no longer getting worse. Either:\n"
     f"• short-term: in {R['stabilized_min_in_band']} of the last 6 months the bucket was within "
     "one of today's; or\n"
     f"• long-term: {R['stabilized_long_run_months']}+ months after reaching 61+ DPD, today's "
     f"bucket is at most {R['stabilized_long_run_max_rise']} higher than 6 months ago."),
    ("3", "Repeat delinquent?", "repeat_delinquent",
     "An earlier delinquency reached 31+ DPD, was cured, and ended at most "
     f"{R['repeat_window_months']} months before this one began."),
    ("4", "Straight roller?", "straight_roller_seasoned",
     "1–30 → 31–60 → 61–90 DPD in three consecutive months (no payment). Seasoned if "
     f"{R['seasoned_min_months']}+ months of history before this delinquency (or history older "
     "than the window); otherwise Early-life."),
    ("5", "Otherwise", "slow_roller",
     "Everything else: paid at least once on the way to 61+ DPD."),
]
STEP_OF = {"unknown": "0", "early_payment_default": "1", "stabilized": "2", "repeat_delinquent": "3",
           "straight_roller_seasoned": "4", "straight_roller_early_life": "4", "slow_roller": "5"}

TERMS = [
    ("DPD bucket", "Days-past-due band at month end (see 'Buckets & segments')."),
    ("Delinquency", "A continuous run of months at 1+ DPD."),
    ("Short slip", "An earlier 1–2 month delinquency, never past 1–30 DPD, paid off. Not counted "
                   "as an earlier delinquency."),
    ("Month to month", "One bucket worse = nothing paid. Same bucket = one month's due paid. "
                       "Better = two or more months paid."),
    ("Months before this delinquency", "Months in the history before the current delinquency "
                                       "started."),
    ("Ceiling bucket", "CC 210+ / RL 180+ DPD. The bucket cannot rise, so staying there is not a "
                       "payment."),
    ("History window", f"{WINDOWS}. With older history an account is never EPD, and a straight "
                       "roller counts as seasoned."),
]

EXAMPLES = [   # (CC buckets oldest -> newest, history cropped by the window, expected state, why)
    ([0, 0, 0, 2, 3, 4, 5], False, "early_payment_default",
     "3 clean months, then one bucket worse every month."),
    ([0, 2, 3, 4, 5, 6, 7, 8, 9, 9, 9], False, "early_payment_default",
     "Same at 180+: months at the ceiling (9 9 9) are not payments."),
    ([0] * 8 + [2, 3, 4, 4, 5, 5, 5, 5, 5], False, "stabilized",
     "Holding at 91–120 DPD for 5 months."),
    ([int(c) for c in "00000000234443345433456554"], False, "stabilized",
     "Swings between 61–90 and 151–180 DPD, no worse than 6 months ago."),
    ([5, 5, 5, 5, 5, 5], True, "stabilized",
     f"Overdue since before {CC_WINDOW}, but clearly holding."),
    ([0, 2, 3, 4] + [0] * 8 + [2, 3, 4, 5], False, "repeat_delinquent",
     "Reached 61–90 DPD, caught up, fell back 8 months later."),
    ([0] * 14 + [2, 3, 4, 5], False, "straight_roller_seasoned",
     "14 clean months, then missed every payment."),
    ([0, 0, 0, 2, 3, 4], True, "straight_roller_seasoned",
     f"History starts before {CC_WINDOW}: older than a year."),
    ([0] * 6 + [2, 3, 4, 5], False, "straight_roller_early_life",
     "6 clean months, then a straight roll."),
    ([0] * 10 + [2, 2, 3, 3, 4, 5], False, "slow_roller",
     "Paid one month at 1–30 and at 31–60 DPD, still rolled."),
    ([0] * 12 + [2, 3, 4, 5, 6, 7, 8, 8, 8, 8, 8, 8], False, "straight_roller_seasoned",
     "Holding at 181–210 DPD is not Stabilized (61–180 DPD only)."),
    ([6, 6, 7, 7, 8, 9], True, "unknown",
     "Already 121–150 DPD in the oldest month we hold."),
]
TIMELINE = 18   # months shown per example


def _chip_l(cell, state: str, label: str | None = None) -> None:
    _chip(cell, state, label or LABELS[state])


def _overview(wb: Workbook, scoring_date: str) -> None:
    ws = wb.active
    ws.title = "Overview"
    r = _title(ws, "DPD deterioration states",
               "One of the persona axes: how a delinquent account got where it is, read from its "
               "monthly DPD history. Every account in scope gets exactly one state.", 5)
    for k, v in [
        ("Scope", "Credit cards (CC) and retail loans (RL) at 61–180 DPD and at 180+ DPD on the "
                  f"scoring date ({scoring_date})."),
        ("Input", f"One DPD bucket per account per month. CC from {CC_WINDOW} (older history has "
                  f"known data-quality issues); RL from {RL_WINDOW}."),
        ("How", "Six yes/no questions in a fixed order; the first 'yes' decides. See 'How states "
                "are assigned'."),
        ("Over time", "EPD and Stabilized can change month to month. The others are fixed once "
                      "set, except that an account can move into Stabilized."),
    ]:
        lab = ws.cell(row=r, column=1, value=k)
        lab.font = _font(bold=True, color=NAVY)
        lab.alignment = WRAP
        c = ws.cell(row=r, column=2, value=v)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 22
        r += 1
    r = _section(ws, r + 1, "The states", 5)
    r = _header(ws, r, ["State", "In one sentence", "Typical action", "Changes over time?",
                        "Decided at step"])
    for st in J.STATES:
        sentence, action, moves = STATE_TEXT[st]
        _row(ws, r, [None, sentence, action, moves, STEP_OF[st]], height=36)
        _chip_l(ws.cell(row=r, column=1), st)
        ws.cell(row=r, column=5).alignment = CENTER
        r += 1
    ws.cell(row=r + 1, column=1, value="Shares: see 'Results'. Thresholds: see 'Thresholds'."
            ).font = _font(italic=True, color=GREY)
    _widths(ws, [30, 58, 50, 24, 12])
    ws.freeze_panes = "A4"
    _print(ws)


def _assignment(wb: Workbook) -> None:
    ws = wb.create_sheet("How states are assigned")
    r = _title(ws, "How states are assigned",
               "Questions are asked top to bottom; the first 'yes' decides the state.", 5)
    r = _section(ws, r, "The flow", 5)
    for step, q, st, _ in STEPS:
        c = ws.cell(row=r, column=1, value=f"Step {step}")
        c.font = _font(bold=True, color="FFFFFF")
        c.fill = _fill(NAVY)
        c.alignment = CENTER
        q_cell = ws.cell(row=r, column=2, value=q)
        q_cell.font = _font(bold=True)
        q_cell.fill = _fill(LIGHT)
        q_cell.border = BOX
        q_cell.alignment = Alignment(vertical="center", wrap_text=True)
        arrow = ws.cell(row=r, column=3, value="yes  ▶" if step != "5" else "▶")
        arrow.font = _font(bold=True, color=GREY)
        arrow.alignment = CENTER
        if step == "0":
            _chip_l(ws.cell(row=r, column=4), "unknown", "Unknown  (Stabilized if Step 2 passes)")
        elif step == "4":
            _chip_l(ws.cell(row=r, column=4), "straight_roller_seasoned",
                    f"Seasoned straight roller  ({R['seasoned_min_months']}+ months)")
            _chip_l(ws.cell(row=r, column=5), "straight_roller_early_life",
                    f"Early-life straight roller  (< {R['seasoned_min_months']} months)")
        else:
            _chip_l(ws.cell(row=r, column=4), st)
        ws.row_dimensions[r].height = 30
        r += 1
        if step != "5":
            down = ws.cell(row=r, column=2, value="no  ▼")
            down.font = _font(color=GREY)
            down.alignment = Alignment(horizontal="center")
            r += 1
    r = _section(ws, r + 1, "The exact tests", 5)
    r = _header(ws, r, ["Step", "Question", "State if yes", "Exact test", ""])
    ws.merge_cells(start_row=r - 1, start_column=4, end_row=r - 1, end_column=5)
    for step, q, st, test in STEPS:
        _row(ws, r, [step, q, None, test, None], height=62 if step == "2" else 44)
        ws.merge_cells(start_row=r, start_column=4, end_row=r, end_column=5)
        _chip_l(ws.cell(row=r, column=3), st)
        ws.cell(row=r, column=1).alignment = CENTER
        r += 1
    r = _section(ws, r + 1, "Terms", 5)
    for term, meaning in TERMS:
        lab = ws.cell(row=r, column=1, value=term)
        lab.font = _font(bold=True)
        lab.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c = ws.cell(row=r, column=3, value=meaning)
        c.font = _font()
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=3, end_row=r, end_column=5)
        ws.row_dimensions[r].height = 22
        r += 1
    _widths(ws, [9, 36, 30, 48, 44])
    _print(ws)


def _examples(wb: Workbook) -> None:
    ws = wb.create_sheet("Worked examples")
    n_lead = 2
    last_col = n_lead + TIMELINE + 2
    r = _title(ws, "Worked examples (credit cards)",
               "One account per row: monthly DPD bucket, oldest on the left, this month on the "
               "right.", last_col)
    ws.cell(row=r, column=1, value="Bucket colours").font = _font(bold=True)
    labels = {2: "1–30", 3: "31–60", 4: "61–90", 5: "91–120", 6: "121–150", 7: "151–180",
              8: "181–210", 9: "210+"}
    for i, b in enumerate(range(1, 10)):
        col = n_lead + 1 + 2 * i
        c = ws.cell(row=r, column=col, value=f"{b}: {labels[b]}" if b > 1 else "0/1: 0 DPD")
        c.fill = _fill(BUCKET_FILL[b])
        c.font = _font(size=8, bold=True, color=_text_on(BUCKET_FILL[b]))
        c.alignment = CENTER
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=col, end_row=r, end_column=col + 1)
    r += 2
    head = ["State", "Decided at step"] + \
        [("Now" if k == TIMELINE - 1 else f"-{TIMELINE - 1 - k}") for k in range(TIMELINE)] + ["Why", ""]
    r = _header(ws, r, head)
    ws.merge_cells(start_row=r - 1, start_column=last_col - 1, end_row=r - 1, end_column=last_col)
    for buckets, cropped, want, why in EXAMPLES:
        got = J.classify(buckets, cropped, 0, 9)
        if got["det_state"] != want:
            raise SystemExit(f"example {buckets} now gives {got['det_state']}, not {want}: "
                             "update the example or its text")
        step = "0 → 2" if (want == "stabilized" and got["starts_delinquent"]) else STEP_OF[want]
        _chip_l(ws.cell(row=r, column=1), want)
        c = ws.cell(row=r, column=2, value=step)
        c.font = _font()
        c.alignment = CENTER
        c.border = BOX
        shown = buckets[-TIMELINE:]
        pad = TIMELINE - len(shown)
        for k in range(TIMELINE):
            c = ws.cell(row=r, column=n_lead + 1 + k)
            c.border = BOX
            c.alignment = CENTER
            if k < pad:
                c.value = "" if cropped else "·"
                c.font = _font(color=RULE)
                continue
            b = shown[k - pad]
            canon = max(b, 1)
            c.value = b
            c.fill = _fill(BUCKET_FILL[canon])
            c.font = _font(bold=k == TIMELINE - 1, color=_text_on(BUCKET_FILL[canon]))
        note = why + (f" ({len(buckets) - TIMELINE} earlier months not shown.)"
                      if len(buckets) > TIMELINE else "")
        c = ws.cell(row=r, column=last_col - 1, value=note)
        c.font = _font()
        c.alignment = WRAP
        c.border = BOX
        ws.merge_cells(start_row=r, start_column=last_col - 1, end_row=r, end_column=last_col)
        ws.row_dimensions[r].height = 28
        r += 1
    ws.cell(row=r + 1, column=1, value="'·' = no history yet (account not open)."
            ).font = _font(italic=True, color=GREY)
    _widths(ws, [28, 10] + [5.2] * TIMELINE + [44, 6])
    ws.freeze_panes = ws.cell(row=8, column=3)
    _print(ws)


def _thresholds(wb: Workbook) -> None:
    ws = wb.create_sheet("Thresholds")
    ws["A1"] = "Thresholds"
    ws["A1"].font = _font(size=16, bold=True, color=NAVY)
    ws.sheet_view.showGridLines = False
    r = 3
    gap = J.PARAM_DEFAULTS["max_inferred_gap_months"]
    rows = [
        ("Early payment default", "Months before first falling behind",
         f"≤ {R['epd_max_history']}", "Someone who never pays misses the 1st or 2nd bill."),
        ("Early payment default", "Short paid-off slips allowed",
         str(R["epd_max_blips"]), "One brief slip doesn't show good behaviour."),
        ("Straight roller", "Months from first miss to 61–90 DPD",
         str(R["straight_max_runup"]), "Three misses in a row: nothing paid on the way."),
        ("Stabilized", "Last 6 months within one bucket of today's",
         f"{R['stabilized_min_in_band']} of 6", "The bank's existing rule."),
        ("Stabilized (long-term)", "Months since reaching 61+ DPD",
         f"{R['stabilized_long_run_months']}+", "Gives uneven payers time before a plateau counts."),
        ("Stabilized (long-term)", "Rise vs 6 months ago",
         f"≤ {R['stabilized_long_run_max_rise']} bucket", "More than one bucket means still getting worse."),
        ("Stabilized", "Highest DPD", "151–180", "At 180+ a flat bucket is not evidence of payment."),
        ("Repeat delinquent", "Depth of the earlier delinquency", "31+ DPD",
         "Matches the bank's re-default view."),
        ("Repeat delinquent", "Months since it ended", f"≤ {R['repeat_window_months']}",
         "Common re-default window."),
        ("Seasoned vs early-life", "Months before this delinquency",
         f"{R['seasoned_min_months']}+", "Standard first-year window."),
        ("History window", "CC data used from", CC_WINDOW, "Older CC data has known quality issues."),
        ("History window", "RL data used from", RL_WINDOW, "Start of the RL window."),
        ("Missing months", "Filled if the gap is at most", f"{gap} months",
         "Longer gaps: history starts after the gap."),
    ]
    r = _header(ws, r, ["Applies to", "Threshold", "Value", "Why"])
    for row in rows:
        _row(ws, r, list(row), height=22)
        ws.cell(row=r, column=3).alignment = CENTER
        ws.cell(row=r, column=3).font = _font(bold=True)
        r += 1
    _widths(ws, [24, 42, 14, 54])
    ws.freeze_panes = "A4"
    _print(ws)


def _buckets(wb: Workbook) -> None:
    ws = wb.create_sheet("Buckets & segments")
    r = _title(ws, "Buckets & segments",
               "CC and RL number buckets differently; the rules read both as DPD bands.", 5)
    r = _header(ws, r, ["DPD band", "CC bucket", "RL bucket", "Segment", "Note"])
    rows = [   # (canonical colour, band, CC, RL, segment, note)
        (1, "0 DPD", "0 (no due) / 1 (current)", "0", "—", "Clean."),
        (2, "1–30 DPD", "2", "1", "—", "Delinquency starts."),
        (3, "31–60 DPD", "3", "2", "—", ""),
        (4, "61–90 DPD", "4", "3", "61–180 DPD", "Segment starts."),
        (5, "91–120 DPD", "5", "4", "61–180 DPD", ""),
        (6, "121–150 DPD", "6", "5", "61–180 DPD", ""),
        (7, "151–180 DPD", "7", "6", "61–180 DPD", "Highest bucket for Stabilized."),
        (8, "181–210 DPD", "8", "7 (ceiling)", "180+ DPD", "RL ceiling: RL 7 = all of 180+."),
        (9, "210+ DPD", "9 (ceiling)", "7 (ceiling)", "180+ DPD", "CC ceiling."),
    ]
    for canon, *vals in rows:
        _row(ws, r, vals, height=20)
        for col in (2, 3):
            ws.cell(row=r, column=col).alignment = CENTER
        ws.cell(row=r, column=1).fill = _fill(BUCKET_FILL[canon])
        ws.cell(row=r, column=1).font = _font(bold=True, color=_text_on(BUCKET_FILL[canon]))
        r += 1
    r = _section(ws, r + 1, "Reading one month to the next", 5)
    r = _header(ws, r, ["This month vs last", "Meaning", "Months' due paid"])
    for row in [("One bucket worse", "Nothing paid", "0"),
                ("Same bucket", "One month's due paid", "1"),
                ("k buckets better", "k + 1 months paid at once", "k + 1"),
                ("Back to 0 DPD", "Cured (rare from 61+ DPD)", "all"),
                ("Same bucket at the ceiling", "Not a payment: the bucket cannot rise", "—")]:
        _row(ws, r, list(row), height=20)
        ws.cell(row=r, column=3).alignment = CENTER
        r += 1
    _widths(ws, [28, 34, 18, 16, 36])
    _print(ws)


def _data_handling(wb: Workbook) -> None:
    ws = wb.create_sheet("Data handling")
    r = _title(ws, "Data handling",
               "How the monthly history is prepared before the questions are asked.", 3)
    gap = J.PARAM_DEFAULTS["max_inferred_gap_months"]
    r = _header(ws, r, ["Situation", "What we do", "Effect on states"])
    rows = [
        (f"History before the window start ({WINDOWS})", "Not used.",
         "Never EPD; a straight roller counts as seasoned."),
        ("History starts already overdue", "Start of the delinquency is missing.",
         "Unknown, unless Stabilized."),
        ("RL loan 1–30 DPD in its first month", "Normal: its first payment is due that month.",
         "Classified as usual."),
        ("Two bills in one month, none in the next (CC)", "One bill moved to the empty month.",
         "None."),
        ("Missing month between two equal buckets", "Filled with that bucket.", "None."),
        ("Missing month where only a straight roll fits", "Filled as the roll.", "None."),
        (f"Other gaps of up to {gap} months", "Filled: last bucket carried, rising as late as "
         "possible.", "Can read as a payment."),
        ("Longer gaps", "History starts after the gap.", "As for history before the window start."),
        ("One-month blips (4 0 4, 0 3 0)", "Corrected to the neighbours.",
         "No false cure or false earlier delinquency."),
        ("Billing-cycle jumps (3 3 5 for 3 4 5)", "Corrected to the roll.", "No false payment."),
        ("No usable bucket in the window", "Not classified.", "Counts against coverage (target "
         "99.9%)."),
        ("Latest month older than the scoring date", "Flagged.", "Classified on the history we have."),
    ]
    for row in rows:
        _row(ws, r, list(row), bold_first=True, height=30)
        r += 1
    _widths(ws, [40, 44, 44])
    _print(ws)


def _results(wb: Workbook, results: dict | None, scoring_date: str) -> None:
    ws = wb.create_sheet("Results")
    blocks = [("cc", "60_180", "CC 61–180 DPD"), ("cc", "180_plus", "CC 180+ DPD"),
              ("rl", "60_180", "RL 61–180 DPD"), ("rl", "180_plus", "RL 180+ DPD")]
    last_col = 1 + 2 * len(blocks)
    r = _title(ws, "Results",
               f"Accounts per state, scoring date {scoring_date}. Blue = counts from the scoring "
               "run; shares and coverage are calculated. Yellow = to fill in.", last_col)
    head = ["State"]
    for _, _, label in blocks:
        head += [f"{label}\naccounts", "share"]
    r = _header(ws, r, head)
    ws.row_dimensions[r - 1].height = 44
    first = r
    total_row = first + len(J.STATES)

    def seg_res(prod, seg):
        return (results or {}).get("products", {}).get(prod, {}).get("segments", {}).get(seg)

    for st in J.STATES:
        _chip_l(ws.cell(row=r, column=1), st)
        for b, (prod, seg, _) in enumerate(blocks):
            col = 2 + 2 * b
            res = seg_res(prod, seg)
            c = ws.cell(row=r, column=col)
            if res is not None:
                c.value = int(res["state_counts"].get(st, 0))
            else:
                c.fill = _fill("FFFF00")
            c.font = _font(color="0000FF")
            c.number_format = "#,##0"
            c.border = BOX
            L = get_column_letter(col)
            s = ws.cell(row=r, column=col + 1,
                        value=f'=IF(${L}${total_row}=0,"",{L}{r}/${L}${total_row})')
            s.number_format = "0.0%"
            s.font = _font()
            s.border = BOX
        r += 1
    ws.cell(row=r, column=1, value="Classified accounts").font = _font(bold=True)
    for b in range(len(blocks)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b, value=f"=SUM({L}{first}:{L}{r - 1})")
        c.number_format = "#,##0"
        c.font = _font(bold=True)
        c.border = Border(top=Side(style="medium", color=NAVY))
    r += 1
    lost_row = r
    ws.cell(row=r, column=1, value="In segment, not classified").font = _font()
    for b, (prod, seg, _) in enumerate(blocks):
        res = seg_res(prod, seg)
        c = ws.cell(row=r, column=2 + 2 * b)
        if res is not None:
            c.value = int(res["in_segment_not_classified"])
        else:
            c.fill = _fill("FFFF00")
        c.font = _font(color="0000FF")
        c.number_format = "#,##0"
    r += 1
    ws.cell(row=r, column=1, value="Coverage (target 99.9%)").font = _font(bold=True)
    for b in range(len(blocks)):
        L = get_column_letter(2 + 2 * b)
        c = ws.cell(row=r, column=2 + 2 * b,
                    value=f'=IF(({L}{total_row}+{L}{lost_row})=0,"",{L}{total_row}/({L}{total_row}+{L}{lost_row}))')
        c.number_format = "0.00%"
        c.font = _font(bold=True)
    r += 2
    for note in [
        "Stabilized is not possible at 180+ (61–180 DPD only).",
        "Roll rates are not shown: they would be measured on the same months that define the states.",
        "No account-level data.",
    ]:
        c = ws.cell(row=r, column=1, value=note)
        c.font = _font(italic=True, color=GREY)
        c.alignment = WRAP
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=last_col)
        r += 1
    _widths(ws, [34] + [14, 9] * len(blocks))
    ws.freeze_panes = ws.cell(row=first, column=2)
    _print(ws)


def build(out: pathlib.Path, results: dict | None, scoring_date: str) -> pathlib.Path:
    wb = Workbook()
    _overview(wb, scoring_date)
    _assignment(wb)
    _examples(wb)
    _thresholds(wb)
    _buckets(wb)
    _data_handling(wb)
    _results(wb, results, scoring_date)
    wb.calculation.fullCalcOnLoad = True      # Excel computes the share / coverage formulas on open
    wb.save(out)
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", default=f"dpd_deterioration_states_{dt.date.today():%Y%m%d}.xlsx")
    ap.add_argument("--results", action="append", default=[],
                    help="JSON written by prod_check.report(..., save_json=...); repeat it for "
                         "each run (one per segment) — they are merged")
    ap.add_argument("--scoring-date", dest="scoring_date", default="(scoring date)")
    a = ap.parse_args()
    res = None
    for path in a.results:
        part = json.loads(pathlib.Path(path).read_text())
        if res is None:
            res = {"generated": part.get("generated"), "products": {}}
        res["generated"] = max(filter(None, [res["generated"], part.get("generated")]), default=None)
        for prod, body in part.get("products", {}).items():
            tgt = res["products"].setdefault(prod, {"segments": {}})
            for seg, val in body.get("segments", {}).items():
                if seg in tgt["segments"]:
                    raise SystemExit(f"{prod} {seg} appears in more than one --results file")
                tgt["segments"][seg] = val
    print(build(pathlib.Path(a.out), res, a.scoring_date))


if __name__ == "__main__":
    main()
`````
