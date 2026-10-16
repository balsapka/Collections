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

Generated 2026-10-16 by `dpd_states/bundle.py`. 16 files, 2,954 lines.
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
├── PROMPTS.md
├── dpd_states/__init__.py
├── dpd_states/config.py
├── dpd_states/features.py
├── dpd_states/states.py
├── dpd_states/analysis.py
├── dpd_states/expectations.py
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
sha256 `e9997587da056c880d5a9b876167db94c51bfc3a8cbcd3a74acfc264d49df185` · 100 lines · trailing newline: yes

`````markdown
# Deterioration states — DPD-journey states for the bucket 4–7 credit-card spine

One state per account, from the DPD bucket history alone, assigned by a short decision
tree (MECE, no residual bucket). Three options: **A** (4 states), **B** (6, recommended),
**C** (7). States use common card-risk names — early payment default (formerly
"bust-out"), stabilized, repeat delinquent, seasoned / early-life straight roller, slow
roller (partial payer); code names and display names are kept separate. The design, thresholds, evidence and everything that was tried and dropped
are in **[METHODOLOGY.md](METHODOLOGY.md)**. Copy-paste prompts for running this at the
workplace with Sonnet are in **[PROMPTS.md](PROMPTS.md)**.

## Layout

```
deterioration_states/
├── README.md                 this file
├── run.py                    run the tools from ANY folder: selftest | synthetic | bundle
├── METHODOLOGY.md            design, thresholds, dropped states + reasons, expectations
├── PROMPTS.md                prompts for Sonnet 5 at the workplace (P0–P6)
├── BUNDLE.md                 ALL source files in one .md + extractor (for .py-blocked viewers)
├── dpd_states/               the package (pandas + numpy + scikit-learn; no Spark)
│   ├── config.py             ← the ONLY file to edit: dataset + column names (<<FILL-IN>>)
│   ├── features.py           string → encoding → journey features (clock-safe)
│   ├── states.py             the state tree, options A/B/C, thresholds, DISPLAY_NAMES / REMARKS
│   ├── analysis.py           real-data analysis: states, backtest, overlap, sweeps, clusters
│   ├── expectations.py       E01–E25: expected values, PASS/WARN/FAIL, "if not met" actions
│   ├── discover.py           shapes, n-gram motifs, clustering helpers
│   ├── synth.py              calibrated synthetic generator (method validation only)
│   ├── run_synthetic.py      method validation report  → validation/
│   ├── selftest.py           real-data code path on synthetic data + 14 edge-case regressions → validation/
│   └── bundle.py             rebuilds BUNDLE.md
├── snippets/
│   └── dpd_states_validate.py   PROD entry point: main(catalog, model_id=None, ...)
├── validation/               evidence from synthetic runs (committed)
└── results/                  real-data outputs land here (aggregates only)
```

## Can't open .py files?

`BUNDLE.md` holds every source file in one markdown file plus a 40-line extractor that
recreates the folder and verifies each file's SHA-256 — see the instructions at its top.
Regenerate it after any change: `python docs/deterioration_states/run.py bundle`.

## Assign states in your own code

```python
from dpd_states.features import build_features
from dpd_states.states import assign_states, OPTIONS, DISPLAY_NAMES

f = build_features(df)                                   # df has a 'dpd_string' column
f["state"] = assign_states(f, **OPTIONS["B_balanced_6"])  # or A_minimal_4 / C_detailed_7
f["state_label"] = f.state.map(DISPLAY_NAMES)             # business label for reports
```

`dpd_string` must be digits only, **leftmost = current month**, 0 and 1 both mean normal.
Only accounts whose current bucket is 4–7 belong to the spine.

## Run locally (no data needed)

```bash
python docs/deterioration_states/run.py selftest     # real-data path on synthetic data: expect "SELFTEST PASSED"
python docs/deterioration_states/run.py synthetic    # method validation report (~1 min)
```

## Run at the workplace (PROD, Kedro notebook)

1. Fill in `dpd_states/config.py` (dataset, key, DPD-string column, optional axis columns)
   and the `globals_dev` accessor in `snippets/dpd_states_validate.py` → **PROMPTS.md P1**.
2. Dry run — schema, counts, example strings:
   ```python
   import sys, pathlib
   _c = pathlib.Path.cwd()
   ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
   sys.path.insert(0, str(ROOT / "docs" / "deterioration_states" / "snippets"))
   from dpd_states_validate import main
   main(catalog, check_only=True)
   ```
3. Full run: `result = main(catalog)` — writes
   `results/dpd_states_validation_<model_id>_<date>.json` + `.md` and prints the
   expectation checks between `=== DPD_STATES OUTPUT START/END ===`. Interpret with
   **PROMPTS.md P2**.

## Rules this code follows

- **Read-only.** Nothing is written to the warehouse.
- **Aggregates only** in the results JSON — no account keys, no row-level data. The
  markdown report shows a few example DPD strings without keys.
- **`model_id` comes from the caller or `globals_dev`**, never hardcoded, and is in the
  output filename, the payload and the first printed line.
- **Scope first:** the configured filter and latest snapshot are applied before anything
  else; only two samples (≤ `sample_n` rows each, default 100k) of the string plus the
  configured optional columns are collected.
- **Never guess a dataset or column name** — every unknown is a `<<FILL-IN>>`.

## Tested / not tested

- `dpd_states` (features, states, analysis, expectations): tested end to end on synthetic
  data (`selftest` passes; Python 3.13, pandas 3.0, scikit-learn 1.9).
- `snippets/dpd_states_validate.py`: the Spark part (load, filter, count, sample,
  `toPandas`) is **not executed here** (no Spark available) — syntax-checked only. The
  `check_only=True` dry run is there to catch problems before the full run.
`````

### FILE: `run.py`
sha256 `e250047f43c7f793bfef0b45712c78560f36cc32b7d9b703f5ed3bf9625144c2` · 37 lines · trailing newline: yes

`````python
"""Run the package's tools from ANY folder (repo root, a notebook folder, anywhere):

    python docs/deterioration_states/run.py selftest [n_accounts]    # real-data path on synthetic data
    python docs/deterioration_states/run.py synthetic [n_accounts]   # method validation report
    python docs/deterioration_states/run.py bundle                   # rebuild BUNDLE.md

Equivalent to `python -m dpd_states.<tool>` run from inside docs/deterioration_states/.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))   # makes dpd_states importable

TOOLS = ("selftest", "synthetic", "bundle")


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
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
sha256 `5a19a9a217cf72a2567571a45362a726ad918ca15fe3da0bf8fe5d7f3ca43db7` · 412 lines · trailing newline: yes

`````markdown
# Deterioration states — methodology

How a credit-card account in buckets 4–7 fell into delinquency, and what it is doing now,
read from its DPD bucket history only. One state per account, assigned by a short
decision tree. MECE by construction, simple enough to explain to the risk team in one
slide, and designed to stay out of the way of the other persona axes.

> **Status.** Designed and validated on calibrated **synthetic** data. Not yet run on the
> bank's book. Every number below marked *(synthetic)* is from simulation and is a
> *method check*, not a finding about the portfolio. The real-data run is
> `snippets/dpd_states_validate.py`; its expectations are in §8.

---

## 1. Where this sits among the persona axes

| Axis | Question it answers | Inputs |
|---|---|---|
| Locatability | Can we reach them? | Reachability flag, in-country flag |
| Ability | Can they pay? | Score: salary, inflow, CASA balance |
| Payment credibility | Do they pay and keep their word? | Score: promises kept (0–2), money coming in last 3 months (0–2), pre-delinquency history clean (0–1) |
| **Deterioration (this)** | **How did they fall in, and are they stabilized now?** | **DPD bucket history only** |

Design rules agreed with the business owner:

1. **MECE** — every account gets exactly one state; no "other" bucket.
2. **Simplicity beats precision** — a rule a collector can repeat beats a better-fitting
   one nobody can explain. Thresholds are round numbers.
3. **Orthogonal where possible** — the states must not rebuild the credibility or ability
   score. Known overlaps are named (§7), not hidden.
4. **5–6 states, at most 8**, each with a different action for the risk team.

---

## 2. Population and data conventions

- **Spine:** credit-card accounts whose **current** bucket is 4, 5, 6 or 7. Bucket 8+ is
  a separate category. Full history is available for every account.
- **The string:** one digit per month, **leftmost = current month**
  (`54320002000` → today 5, last month 4, …). Configurable if a source is reversed.
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
- **Billing-cycle jumps:** a +2 move next to a hold (`3 3 5` or `3 5 5`) is the reporting
  artefact of a straight roll and is repaired to `3 4 5`. Any other +2 is read as a roll.

---

## 3. Features used by the states

Only features that **do not drift with time since reaching 4** are used to assign states.
For most of the spine the current bucket is a clock (one bucket per month), so any
count over a fixed window, or any rate over the whole spell, changes with the bucket
rather than with behaviour.

| Feature | Definition | Fixed once past 4? |
|---|---|---|
| `months_before_spell` | months of history before the current spell started | yes |
| `n_blips` | earlier excursions of 1–2 months that never passed bucket 2 (EPD allows one) | yes |
| `n_prior_episodes` | earlier real (non-blip) spells (EPD requires none) | yes |
| `max_prior_bucket` | deepest bucket reached in any earlier (non-blip) spell; 0 if none (repeat delinquent) | yes |
| `runup_len` | months from the last clean month to the first month at bucket 4 (3 = straight 2→3→4) | yes |
| `runup_pays` | months on the way to 4 in which 2+ months were paid (moved back) | yes |
| `last6_in_band` | of the last 6 months (incl. today), how many were within today's bucket ±1 | no — current behaviour, by design |

Other features (`runup_holds`, `post4_paid_rate`, `max_hold_run`, …) are
computed for diagnostics and discovery only.

---

## 4. The states

Questions are asked **in order**; the first "yes" assigns the state.

```
Q1  Early payment default?  <= 3 months of history before this spell
                            (at most one blip inside it — a payoff from 2 — and no
                            earlier real spell) AND run-up to 4 took <= 3 months
                                                           -> early_payment_default
Q2  Stabilized?             >= 5 of the last 6 months within today's bucket ±1
                            OR (>= 6 months in buckets 4+ AND at most 1 bucket
                                higher than 6 months ago)  -> stabilized
Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3 and cured
                                                           -> repeat_delinquent
Q5  Straight roller?        run-up (last clean month -> first month at 4) <= 3 months
      yes -> straight_roller  [B, C: >= 12 months of history before the spell
                               -> straight_roller_seasoned, else straight_roller_early_life]
      no  -> slow_roller      [C: paid 2+ months at once on the way down
                               -> slow_roller_erratic, else slow_roller_intermittent]
```

(Q3 "paying since bucket 4" was tested and rejected — §6.4.)

### Three options

| Option | States | Use when |
|---|---|---|
| **A — minimal (4)** | EPD, stabilized, straight roller, slow roller | Strict orthogonality: prior-spell history is left entirely to credibility |
| **B — balanced (6), recommended** | EPD, stabilized, repeat delinquent, seasoned straight roller, early-life straight roller, slow roller | Default. Matches the natural groups in the data (§6.1) and the 5–6 target |
| **C — detailed (7)** | B with slow roller split into intermittent payer / erratic payer | The risk team has a different action for each and both are ≥ 4% |

### What each state means and the action it points to

| State (display name · `code`) | Reads as | Action flavour | Share *(synthetic)* |
|---|---|---|---|
| **Early payment default (EPD)** · `early_payment_default` | At most 3 months of history (one blip allowed), rolled straight in, never really paid | Early-risk / first-party-fraud review, early legal; no restructuring | 6% (bank: 6%) |
| **Stabilized** · `stabilized` | Paying about one month's due each month for 5 of 6 months — or, after 6+ months in buckets 4+, still within one bucket of where it was 6 months ago (pays what is due on average, unevenly) | **Offer restructuring to break the hardship** | 8% (bank's rule alone: 7%; bank: 6%) |
| **Repeat delinquent (re-default)** · `repeat_delinquent` | Has been here before and cured from bucket 3 | Has shown they can catch up: firm promise-based plan; credibility decides the pressure | 16% |
| **Seasoned straight roller** · `straight_roller_seasoned` | At least a year on book (≥ 12 months clean), then rolled every month without paying | Life event. Read with the other axes: not in country → departed; no salary → income shock; salary still in → won't pay. Most likely to respond to a hardship route | 52% |
| **Early-life straight roller** · `straight_roller_early_life` | 4–11 months on book, then rolled every month without paying | Same triage; also an underwriting signal for acquisition | 3% — below the 5% floor in synthetic data; the real share decides (E16) |
| **Slow roller (partial payer)** · `slow_roller` | Paid something on the way down but kept rolling | Over-indebted: longer-tenor restructure or settlement | 16% |
| ↳ **Intermittent payer** *(C)* · `slow_roller_intermittent` | Paid one month here and there, never caught up | Chronic insufficiency: restructure to what they actually pay | 10% |
| ↳ **Erratic payer** *(C)* · `slow_roller_erratic` | Caught up 2+ months at once, then rolled again | Lumpy / irregular income: plan aligned to inflow timing | 6% |

In option A the two straight-roller states are one: **Straight roller** · `straight_roller`.

**Stabilized is the only state that moves month to month** — it describes what the
customer is doing now (*synthetic:* 62% are still stabilized next month). Every other
state is fixed once the account is past bucket 4 (*synthetic:* 97–100% keep their state
next month).

### 4.1 Names

The names use established card-risk and collections terms, and follow two rules:

1. **Describe behaviour, not intent.** These labels reach collector screens, audit trails
   and possibly complaint files. They say what the DPD history shows ("never really
   paid", "rolled every month", "paid one month at a time"), never why ("fraud",
   "won't pay"), which the history cannot prove.
2. **Code names are stable; display names are free.** Code uses short identifiers
   (`early_payment_default`, `straight_roller_seasoned`, …). `DISPLAY_NAMES` and `REMARKS`
   in `dpd_states/states.py` carry the business labels, so renaming for the risk team never
   breaks the pipeline or old results. Every report starts with the names table.

| Term | Where it comes from | Note |
|---|---|---|
| **Early payment default (EPD)** | Early-risk monitoring (FPD / SPD / TPD = first / second / third payment default; EPD = default early in the life of the account) | **Formerly "bust-out"** — the bank's internal name, kept in remarks. Classic *bust-out* fraud is different: a customer builds a good record and limit, maxes out (often with cash advances) and disappears. Its DPD history is clean-then-straight-roll, so it lands in **seasoned straight roller**; spotting it needs spend / utilisation spikes before delinquency — a fraud overlay, not this axis |
| **Stabilized** | The bank's own term; roll-rate "stay" behaviour | Industry has no single standard label for "pays enough to stay in the bucket" |
| **Repeat delinquent / re-default** | Collections recidivism; re-default rates after cure or restructure | |
| **Straight roller** | Core card-collections term: rolls through every bucket without a payment | |
| **Seasoned / early-life** | Seasoning and months on book (MOB); the first 12 months is the standard early-life window | |
| **Slow roller (partial payer)** | Roll-rate language: the counterpart of the straight roller | **Also called partial payer** — the more common collections term. The rejected Q3 state was renamed `paying_since_4` so "partial payer" means only this state |
| **Intermittent / erratic payer** | Collections payment-pattern labels | |

---

## 5. Thresholds and the evidence behind them *(synthetic sweeps)*

| Threshold (`parameter`) | Value | Why this value | What moving it does |
|---|---|---|---|
| EPD history (`epd_max_history`, `epd_max_blips`) | **≤ 3 months, at most one blip** | Business definition (agreed): a customer who never pays misses the first or second bill, so 2–3 clean months at most (`0 0 2 3 4`, `0 0 0 2 3 4`, `0 2 0 2 3 4`). No natural knee in the data | *Synthetic:* at 3 months 93% of the state is a planted early defaulter; at 6 months 79%, at 12 months 55% — longer histories are early-life defaults and land in early-life straight roller. Sweep reported in every run (2–12 months) |
| EPD earlier spells | **none; one blip allowed** | An early defaulter may pay off once, but only from bucket 2 (a blip) | `0 2 3 4 0 0 2 3 4 5 6` is therefore repeat delinquent, not EPD; two blips (`0 2 0 2 0 2 3 4`) is not EPD |
| Straight-roller run-up (`straight_max_runup`) | **≤ 3 months** | The one sharp threshold: any single paid month on the way down makes it a slow roller | ≤ 4 moves ~70% of genuine slow rollers into straight roller |
| Stabilized band (`stabilized_min_in_band`) | **5 of last 6 months within ±1** | The bank's existing stabilized rule, unchanged | 4 of 6: share ~14%, next-month roll ~46%, persistence ~63%. 6 of 6: ~5%, ~32%, ~80% |
| Stabilized long-run clause (`stabilized_long_run_months`, `stabilized_long_run_max_rise`) | **≥ 6 months in 4+, at most +1 bucket over 6 months** | Fixes the two edge cases in §6.15: oscillating payers and accounts that just paid down. Straight rollers cannot meet it (they leave the spine within ~4 months) | Adds ~1% of the spine to stabilized, which still rolls far less than the rest (~44% vs ~85% next month). +2 would take in slow drifters paying ~4 of 6 dues; `None` switches the clause off |
| Repeat-delinquent depth (`repeat_min_prior_peak`) | **earlier spell reached 3** | The bank counts ~85% single-spell; spells from 3 give 83% *(synthetic)* | From 2: 19%. From 4: 5% (cures from 4+ are rare) |
| Seasoned (`seasoned_min_months`) | **≥ 12 months** | Business definition (agreed): the first year on book is the standard early-life window. EPD already takes ≤ 3 months, so early life = 4–11 months | *Synthetic:* 12 m gives early life only 3.4% (below the 5% floor), 18 m 7%, 24 m 11%, 36 m 20% — but these shares come from the generator's assumed tenure distribution, so the real share decides (E16) |

**Rule order.** EPD is asked before stabilized (the bank's order). Only ~0.2% of the spine
is an early defaulter that is also stabilized today, so the order barely matters.

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
  ambiguous, so the soft-assignment advantage disappears. Best ARI vs planted 0.48 but
  stability fell to 0.67–0.93. Not used. GMM fits continuous inputs (ability scores,
  balances) far better than DPD-derived counts.
- **Residual clustering (after EPD and stabilized) — kept as a diagnostic.** k-means at
  k = 6 on the remaining ~88% found six clean, nameable groups: long-clean straight roll,
  short-clean straight roll, earlier spell to 3+, paying after 4 but still rolling, held on
  the way, paid 2+ on the way. With the final thresholds, agreement at k = 6 is A 0.11,
  **B 0.32, C 0.34** (best at k = 3: B 0.65 vs A 0.31) — the evidence that two residual
  states were too few. Every B/C split maps to one of these clusters with a one-line
  rule; the clusters themselves are not the states. The clusters split clean history
  near 36 months, but that reflects the generator's assumed tenure distribution; the
  seasoned cut is a business definition (12 months, §5).

### 6.2 A "mixed" / residual state
Dropped. An ordered tree with a default branch is MECE without one, and a residual
bucket invites "everything we don't understand" to grow.

### 6.3 Staircase (holds for months at each level, then steps up)
Merged. While it is holding a bucket it *is* stabilized (that is the actionable fact);
just after a step it reads as a slow roller. Telling a genuine holder from a staircase mid-hold needs more
than 6 months of history and an extra rule, and the next-month risk was the same
(*synthetic:* 0.28 vs 0.29). It separates only over 6 months (exit 33% vs 50%).

### 6.4 "Paying since bucket 4" — pays after reaching 4 but still rolling (Q3)
Tested at 0.34 / 0.5 / 0.67 months paid per month since 4. Rejected:
- barely separates risk (next-month roll ~80% vs ~86%);
- unstable — ~37% leave it every month — and it **drags the stability of the fixed
  states from ~98% to ~91%**, because accounts flip in and out of it;
- 79% of it is "paid in the last 3 months" — the credibility axis's 2-point component.

It is one of the six natural residual clusters, so it is real behaviour — but it belongs
to credibility, not here. The switch is kept in code (`paying_since_4_min_rate`, state `paying_since_4` — renamed
from "partial payer" so that term means only the slow roller) so the
test can be repeated (expectation E24).

### 6.5 Separate states for slow slide, dip-and-roll, volatile
Merged into slow roller (A, B) or split once by "paid 2+ months on the way" (C). The three
confuse each other in every view (shapes, clusters, trees), and the risk actions are close.
Much of "volatile" (cure then relapse) is a repeat delinquent by definition.

### 6.6 Repeat delinquent in option A
Left out of A on purpose. Repeat delinquent is built from earlier spells — the same history
credibility's 1-point "pre-delinquency clean" flag scores. In the self-test (with a clean
point defined as "no earlier spell") the states explained **84%** of that point's
variance. It is included in B/C because it is only 1 of credibility's 5 points and it
carries more than a yes/no: *cured from bucket 3 before* is evidence of catch-up capacity.
Expectation E19b measures the real overlap and decides A vs B.

### 6.7 "Stabilized or improving" clause (today's bucket ≤ 6 months ago)
Dropped. It changed **0.0%** of assignments. Straight / slow roller describe how the account fell
in, so an improving account carries no misleading label without it.

### 6.8 Payment-based refinement of stabilized
Tested: "≤ 1 roll in 6 months AND paid 2+ months at least once" separated holders from
staircases at 99% precision — but only because the synthetic generator built it that way,
and it leans on payment behaviour (credibility). Replaced by the bank's own 5-of-6 rule.

### 6.9 Features that drift with time since bucket 4
Dropped from assignment: whole-spell roll rate, fixed-window counts (rolls in the last 6
or 12 months), months paid since 4 as a count. Straight rollers at bucket 4 and 7 looked
different only because of the clock. Replaced by run-up features (fixed once past 4) and
rates within the current spell.

### 6.10 Shape table as the assignment
Kept for discovery and stakeholder examples only. ~5–6k distinct banded shapes; the top
30 cover ~35–40% of accounts — too fragmented to assign everyone.

### 6.11 n-gram ranking by planted-label purity
Fixed. The first version had a meaningless "lift" (per-account presence divided by
per-month code frequencies, rescaled by an arbitrary constant) and ranked by planted
labels that real data does not have. Lift is now measured against each account's own
codes in shuffled order: lift > 1 means the order of moves matters.

### 6.12 Treating +2 jumps as impossible
Replaced by repair (+2 next to a hold → straight roll) and "otherwise a roll". Real data
has billing-cycle effects (example: `…3 4 3 5 4…`).

### 6.13 Payment-promise or inflow inputs in any state
Never used — credibility and ability own them. Their overlap is *measured* (§7).

### 6.14 EPD ("bust-out") with up to 6 months of history
The first version allowed ≤ 6 months before the spell, chosen to match "a few months".
It made `0 0 0 0 0 0 2 3 4` a bust-out (now EPD) — but six clean months means about four bills were
paid (or nothing was due): an **early-life default**, not a customer who never paid. The
synthetic 6% match did not support 6 months either: the generator's bust-out volume had
been tuned to hit 6% *under that rule*, so the match was circular. Replaced by the agreed
business definition: **≤ 3 months, at most one blip**. Under it the generator still gives
5.8% EPD; every planted early defaulter is caught, and 93% of the state is a planted
early defaulter (79% under the old 6-month rule).

### 6.15 Stabilized measured only around today's bucket (edge cases)
The bank's rule — 5 of the last 6 months within ±1 of **today's** bucket — misreads two
uncommon but real histories (oldest → newest, today is the last digit):

- **Oscillating payer** `0000 0000 2344 4334 5433 4565 54` — swings between 3 and 6 for over
  a year, paying roughly what is due on average. The rule flipped it between stabilized and
  "straight roller" **5 times in 16 months**; every time it left the band it was called a
  straight roller, which it is not.
- **Just paid down** `… 3 4 5 6 6 5 4` — paid two months twice (6 → 5 → 4). The band around
  today's 4 excludes the two 6s, so the rule called it a straight roller *because* it paid.

Fix adopted: the **long-run clause** (§5). Both cases are now stabilized from their sixth
month at 4+ onwards; the only remaining dip is the single month at the top of a
3-month roll (3 → 4 → 5 → 6), which is a fair description of that month. Rejected
alternatives: allowing +2 over 6 months (takes in slow drifters), and a "sticky" rule
that remembers last month's state (harder to explain and audit).

Measured on synthetic data with oscillating payers added (1.2% of the spine): of the
accounts ever stabilized during the 6 backtest months, the share that **left and came
back** fell from ~8% (bank's rule) to ~5–7%, and oscillating payers bounced 41% less.
The rest are staircases (hold, step up, hold) and swingers in their first 6 months at 4.
Expectation E26 tracks this on real data. Both examples are permanent regression cases
in the self-test.

**Known limitation.** After an oscillating or stabilized account breaks out and rolls,
its fixed state comes from the original run-up (often "straight roller"). That is by
design — post-4 payment history belongs to credibility — but read "straight roller" as
*how they fell in*, not *never paid since*.

### 6.16 Seasoned / early-life split in option A
Not in A because, in synthetic data, it adds no risk separation (both ~94–95% exit within
6 months, by construction). It is in B/C for its action difference (life event vs
underwriting signal). Real outcomes decide whether it earns its place.

---

## 7. Overlap with the other axes (known and measured)

| Overlap | Size *(synthetic)* | Treatment |
|---|---|---|
| stabilized ↔ credibility "money coming in" (2 pts) | 100% of stabilized have money in; 44% of the rest do too | One-directional: stabilized is stricter (enough to hold the bucket, 6 months). Accept and state it. E21 |
| repeat delinquent ↔ credibility "pre-delinquency clean" (1 pt) | eta² 0.84 of the clean point explained by B states | Decides A vs B. E19b |
| straight / slow roller ↔ ability | none in synthetic (by construction) | Straight rolling may proxy income loss on real data — fine, but say so. E20 |
| any state ↔ locatability | none expected | E19/E20 report it |

---

## 8. Real-data validation

### How the backtest works from a single table
Today's string holds the past: dropping its newest *k* digits gives the string as it was
*k* months ago, and the dropped digits are what happened next. So one table of
latest-month strings gives the spine as of *k* months ago **and** its outcomes (next-month
roll, exit to 8+ within *k*, cure, next-month state). This needs the table to **keep
accounts that have since rolled to 8+ or closed** — a survivor-only table biases the
outcomes (the snippet detects and warns).

### Expectations (checked automatically — `dpd_states/expectations.py`)

| | Check | Expected | Basis |
|---|---|---|---|
| E01 | Exactly one state per account | True (FAIL otherwise) | Tree with default branch |
| E02 | Unparseable strings | ≤ 2% (FAIL) | CHAR_MAP / STRIP_CHARS set right |
| E03 | Backtest monthly roll rates vs 70/80/90/95% | ≤ 7pp off (FAIL) | Confirms orientation and reconstruction |
| E04 | Histories starting inside the spell | ≤ 10% | Full history exists |
| E05 | Unrepaired +2 jumps | ≤ 2% | Most jumps sit next to a hold |
| E06 | Bucket mix declines 4 → 7 | yes | Rising roll rates |
| E07 | One spell only (from bucket 3) | 78–92% | Bank ~85% |
| E08 / E09 | EPD / stabilized share | 4–8% / 4–9% | Bank 6% / 6% |
| E10 / E11 | Recall of the bank's existing flags | ≥ 80% / ≥ 90% | Same definitions |
| E12 | Stabilized next-month roll below the fixed states | ≥ 20pp gap | *Synthetic:* 40% vs ~85% |
| E13 | Fixed states keep their state next month | ≥ 95% | Run-up fixed once past 4 |
| E14 | Stabilized persistence next month | 45–85% | Current behaviour |
| E15 | Option A straight-roller share | 55–80% | Most roll straight |
| E16 | Smallest option-B state | ≥ 5% | Actionable size |
| E17 | Smaller slow-roller split (C) | ≥ 4% | Actionable size |
| E18 | Stabilized at bucket 4 vs 7 | ≥ 2× | 90–95% roll at 6–7 |
| E19 / E19b / E20 | eta² of credibility / clean point / ability by state | ≤ 0.25 / ≤ 0.50 / ≤ 0.10 | Orthogonality |
| E21 | Stabilized with money coming in | ≥ 90% | Stabilized = paying |
| E22 | Residual clusters favour B over A | ARI gain ≥ 0.15 | *Synthetic:* 0.20 |
| E23 | One paid month matters (slow roller at run-up ≤ 4 / ≤ 3) | ≤ 0.70 | Most slow rollers held once |
| E24 | "Paying since 4" stays rejected | persistence ≤ 75% | *Synthetic:* 63% |
| E25 | INFO: exit spread across fixed states | report | Unknowable from synthetic |
| E26 | Stabilized accounts that leave and come back within k months | ≤ 10% | *Synthetic:* ~5–7% (§6.15) |

Every check carries an "if not met" action in the code and in the report. The self-test
also runs 14 **edge cases** from the design discussion (EPD with a blip, six clean months,
two blips, payoff from 4, staircase, both oscillating payers, …) and fails if any changes
state.

### Choosing the option on real data
1. Any **FAIL** → fix config/data first; read nothing else.
2. **E19b high** (repeat delinquent ≈ credibility clean point) **and** the risk team does not want the
   cured-before nuance → **A**. Otherwise **B**.
3. **E17 passes and** the risk team has distinct actions for intermittent vs erratic payers → **C**.
4. **E25 ≥ 5pp** → the mechanism carries risk on its own; report it to the risk team as a bonus.

---

## 9. Validation done so far *(synthetic)*

- **Calibrated generator** (`dpd_states/synth.py`): eight planted journey patterns
  (bust-out, clean abrupt shock, slow slide, staircase, stabilized, repeat episodes,
  dip-and-roll, volatile) plus a rare oscillating payer (1.2% of the spine); full lifecycles to exit; length-biased snapshot like a real
  spine; payment holidays (frozen buckets) and billing-cycle +2 jumps; one continuous
  tenure distribution. Matches the bank's figures: roll rates 70/80/89/95% (target
  70/80/90/95%), EPD 5.8% (6%), stabilized 6.5% (6%), single spell 83% from bucket 3 (85%).
- **Method report:** `validation/dpd_states_validation_*.md` (`python docs/deterioration_states/run.py synthetic`).
- **Real-data path self-test:** `validation/selftest_report_*.md` (`python docs/deterioration_states/run.py selftest`)
  runs the exact analysis and expectations the workplace run uses, on synthetic data with
  fake axis columns. All checks pass except two expected WARNs: E19b (repeat delinquent ≈
  credibility clean point, §6.6) and E16 (early-life straight roller 3.4% under the 12-month
  seasoned cut — a property of the synthetic tenure distribution, §5).

**What synthetic data cannot tell you:** whether the rolling states differ in outcome (they
share post-4 dynamics by construction), how big the real overlaps with credibility and
ability are, and how much payment holidays contaminate stabilized. The real-data run answers
all three.

---

## 10. Open decisions

1. Option A, B or C — decide from E19b, E17 and the risk team's actions (§8).
2. Spell definition (from bucket 3 or 4) — E07 shows which matches the bank's 85%.
3. EPD history threshold — confirm 3 months (one blip) against the bank's existing bust-out rule (E10).
4. Payment holidays / restructurings — if flags exist, exclude frozen months before Q2.
5. The long-run clause widens the bank's stabilized definition (+~1% of the spine) —
   confirm it with the owners of the existing rule (E11 will show the agreement drop).

## Glossary

Bucket — DPD band, one digit per month · Roll — +1 bucket, nothing paid · Hold — same
bucket, one month's due paid · Cure — back to 0/1 · Spell — continuous months at ≥ 2 ·
Blip — 1–2 month spell never past 2 · Run-up — last clean month to first month at 4 ·
Spine — accounts currently at 4–7 · eta² — share of an axis score's variance explained by
the states (0 = orthogonal) · ARI — agreement between two groupings (0 = chance, 1 = identical).
`````

### FILE: `PROMPTS.md`
sha256 `857bce12219ab06d2ee27cdc5c67598e44264f1d205913f6aa55bce77b7d68b8` · 197 lines · trailing newline: yes

`````markdown
# Prompts for running the deterioration states at the workplace

Copy-paste prompts for a Sonnet 5 session in the workplace (PROD) repository. Each prompt
is self-contained. **Paste P0 first in every new session**, then the prompt for the step.

Order: **P0 → P1 → P2**, then P3 / P4 as the results require, then P5. P6 only once an
option is chosen.

---

## P0 — Orientation (paste first, every session)

```
You are working in our workplace repository on the "deterioration states" package in
docs/deterioration_states/. Read these first, fully, before doing anything:
  1. docs/deterioration_states/README.md
  2. docs/deterioration_states/METHODOLOGY.md
  3. docs/deterioration_states/dpd_states/config.py
  4. docs/deterioration_states/snippets/dpd_states_validate.py

What it is: one state per credit-card account in DPD buckets 4–7, assigned from the DPD
bucket-history string by a short decision tree (options A/B/C). The state logic and
thresholds are FINAL for this round — they were designed and validated elsewhere.

Ground rules — follow all of them:
- Do NOT change the state logic, thresholds or expectations in dpd_states/states.py or
  dpd_states/expectations.py unless a prompt explicitly asks you to. If you think one is
  wrong, say so and explain why; do not edit it.
- NEVER invent a dataset, table or column name. Find it in the repo (Kedro catalog
  conf/**/catalog*.yml, pipeline code, existing notebooks) or ask me. Leave <<FILL-IN>>
  where you cannot confirm a name.
- model_id is never hardcoded. It comes from the caller or the project globals
  (globals_dev). Find the real accessor in this repo.
- Read-only: nothing may be written to the warehouse. Results files contain aggregates
  only — no account keys, CIFs, names or row-level data.
- Never present a number you have not seen in actual output. If something has not run,
  say it has not run.
- Keep code changes minimal and confined to config.py and the clearly marked
  <<FILL-IN>> spots unless asked otherwise.

Reply with a 5-line summary of what the package does and which names need filling in.
```

---

## P1 — Wire up names and do the dry run

```
Task: make docs/deterioration_states runnable in this repo, then run the dry run.

1. Find the dataset that holds one DPD bucket-history string per credit-card account.
   Requirements (from config.py): it must have the account key and the DPD string; for
   the backtest it must still contain accounts that have since rolled to bucket 8+ or
   closed — not only today's bucket 4–7 spine. Search the Kedro catalog and pipelines.
   If several candidates exist, list them with their columns and ask me which to use.
2. Fill in dpd_states/config.py:
   - DS_STRINGS_TMPL (keep the "{model_id}." prefix only if the dataset is model_id
     namespaced), KEY, COL_DPD
   - COL_SNAPSHOT if the dataset has several snapshots per account; ROW_FILTER if it
     mixes products (we want credit cards only)
   - LEFTMOST_IS_CURRENT: check on real strings — the leftmost digit must be the
     current month. Verify against a current-bucket column if one exists.
   - CHAR_MAP / STRIP_CHARS if strings contain anything other than digits
   - DS_STRINGS_HAS_EXITED: False if the dataset only has today's spine
   - Optional columns, ONLY if they exist on the same dataset (or tell me they live
     elsewhere — do not build joins yet): credibility score and its three components,
     ability score, reachability and in-country flags, the bank's existing bust-out
     (= our early payment default) and stabilized flags, payment-holiday / restructuring flags. Flags must be 1/0.
3. Fill in _resolve_model_id in snippets/dpd_states_validate.py with the real
   globals_dev accessor from this repo.
4. Show me the diff of config.py and the snippet, then give me the notebook cell for
   main(catalog, check_only=True) (it is in the snippet docstring).
5. When I paste back the CHECK output, verify: counts are plausible, rows == accounts,
   example strings look right (leftmost = today, digits only), no WARNING lines. Fix
   config and repeat until clean. Do not start the full run until I say so.
```

---

## P2 — Full run and interpretation

```
Task: run the full validation and interpret it against the written expectations.

1. Give me the notebook cell: result = main(catalog)   (model_id from globals), or
   main(catalog, model_id="<variant>") for a specific variant.
2. When I paste back the block between === DPD_STATES OUTPUT START === and END (or point
   you to results/dpd_states_validation_<model_id>_<date>.json), read the JSON and .md.
3. Report, in this order:
   a. Any FAIL (E01, E02, E03). If present, STOP: diagnose and propose the config fix.
      Nothing else is trustworthy until these pass.
   b. Each WARN: the observed value, the expected range, and the "if_not_met" action
      written in the check. Say whether the action needs a config change, a decision from
      me, or nothing.
   c. The recommended option (B_balanced_6) scorecard from the backtest: share,
      roll_next_month, exit_8plus_within_k, same_state_next_month per state.
   d. Orthogonality: the eta² table and stabilized-vs-money-in. Name the largest overlap.
   e. Which option the data supports, using METHODOLOGY.md §8 "Choosing the option":
      E19b (repeat delinquent vs credibility clean point), E17 (slow-roller split size), E22 (residual
      clusters), E25 (outcome spread across the fixed states).
4. Keep it factual: every number you quote must come from the output. Mark anything
   you infer as an inference.
```

---

## P3 — Fix-up loop for WARNs (bounded)

```
Task: address the WARN checks from the last run, within strict limits.

Allowed without asking me:
- config.py changes (names, CHAR_MAP, STRIP_CHARS, filters, flags).

Allowed only after I approve, one at a time, each justified by a sweep table in the
report (section 6) and the check's "if_not_met" text:
- epd_max_history (sweep: epd_max_history), stabilized_min_in_band,
  stabilized_long_run_months / stabilized_long_run_max_rise (see E26), repeat_min_prior_peak
  (spell from 3 vs 4, see E07), seasoned_min_months.

Not allowed: changing the tree structure, adding or removing states, editing
expectations to make a check pass, using payment-promise / inflow / ability columns
inside states.py.

For each WARN: propose the smallest change, show the sweep row that supports it, predict
which checks it affects, and wait for my OK. After approved changes, give me the cell to
re-run and compare old vs new check tables.
```

---

## P4 — Compare with the bank's existing bust-out and stabilized rules

```
Task: compare this package's early_payment_default (the bank calls it bust-out) and
stabilized with the bank's existing implementations.

1. Find the existing bust-out and stabilized logic in this repo (search for
   "bust", "stabil", "dpd", pipeline nodes, SQL). List the files and quote the rules.
2. Translate each into the terms of METHODOLOGY.md §4 (history before the spell, earlier
   peak, run-up length, months within ±1 of today's bucket out of the last 6).
3. List every difference and its likely effect on the shares (E08/E09) and recall
   (E10/E11). If the existing flags are available as columns, wire them into
   EXISTING_RULE_COLS in config.py so the next run measures agreement directly.
4. Do not change states.py. If our definition should move toward the bank's, propose
   the parameter change for P3.
```

---

## P5 — One-page summary for the risk team

```
Task: write a one-page summary for the Group Retail Risk team from the latest
results/dpd_states_validation_<model_id>_<date>.json (and .md).

Audience: risk managers, not data scientists. No code, no eta², no ARI.
Structure:
1. What the states are (one line each) and the action each points to — use the display
   names and the table in METHODOLOGY.md §4 (and §4.1 for the names: EPD was formerly
   called bust-out; slow roller is also called partial payer), with the REAL shares from
   the results.
2. What the backtest shows: which states roll, which stay stabilized, how stable they are month to
   month — real numbers only.
3. How this fits with locatability, ability and credibility: where it adds information
   and where it overlaps (stabilized ↔ money coming in; repeat delinquent ↔ clean history).
4. The option we recommend (A/B/C) and why, in two sentences.
5. Open decisions for the risk team (METHODOLOGY.md §10), as questions.
Every number must come from the results file. Write it to
docs/deterioration_states/results/risk_summary_<model_id>_<date>.md.
```

---

## P6 — Productionise the chosen option (only after a decision)

```
Task: add the deterioration state as a pipeline output, using the option I name:
<A_minimal_4 | B_balanced_6 | C_detailed_7>.

1. Follow this repo's existing pipeline patterns (find a comparable node and copy its
   structure, naming, catalog entries and tests). Do not invent conventions.
2. The node takes the spine's DPD strings and returns: account key, snapshot date,
   state code, display name (dpd_states.states.DISPLAY_NAMES), option name, and the
   assignment features (months_before_spell, n_blips,
   n_prior_episodes, max_prior_bucket, runup_len, runup_pays, last6_in_band) for auditability.
   Call dpd_states.features.build_features and dpd_states.states.assign_states — do not
   re-implement the logic. If the data is large, apply them per partition
   (mapInPandas / applyInPandas).
3. model_id from globals, never hardcoded; new catalog entries model_id-namespaced like
   the existing ones.
4. Ship a validation snippet to the same contract as snippets/dpd_states_validate.py:
   row counts, null rates, share per state, MECE check (exactly one state per account),
   agreement with the last validation run's shares (within 1pp), and a few example
   strings without keys.
5. Show me the diff and the catalog entries before anything runs.
```
`````

### FILE: `dpd_states/__init__.py`
sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · 0 lines · trailing newline: no

`````python

`````

### FILE: `dpd_states/config.py`
sha256 `d26c4fa79d7807166f9ad77459a0e94d21bc5b95b023876e6948cc16c9201172` · 56 lines · trailing newline: yes

`````python
"""Workplace configuration — the ONLY file that needs editing to run on real data.

Every <<FILL-IN>> must be replaced with a name discovered in the workplace repo / Kedro
catalog. Never guess a dataset or column name: if it cannot be found, ask the user.
`model_id` is NOT configured here — the snippet resolves it from the caller or globals.
"""

# --- dataset -------------------------------------------------------------------
# One row per credit-card account with its DPD bucket-history string AS OF THE LATEST
# MONTH. For the backtest it must contain ALL card accounts that were in buckets 4–7
# `BACKTEST_MONTHS` ago — including those that have since rolled to 8+ or closed —
# not only today's spine. If only today's spine is available, the backtest is skipped
# (set DS_STRINGS_HAS_EXITED = False) and the outcome checks report SKIPPED.
DS_STRINGS_TMPL = "{model_id}.<<FILL-IN: dataset with one DPD-history string per card account>>"
DS_STRINGS_HAS_EXITED = True

KEY = "<<FILL-IN: account key column>>"          # used only for counting distinct accounts
COL_DPD = "<<FILL-IN: DPD bucket-history string column>>"

# If the dataset holds several snapshots per account, name the snapshot column; the
# latest snapshot is used. None = the dataset is already one row per account.
COL_SNAPSHOT = None
# Optional Spark SQL filter applied first (scope), e.g. "product_type = 'CREDIT_CARD'".
ROW_FILTER = None

# --- string conventions ----------------------------------------------------------
LEFTMOST_IS_CURRENT = True    # '54320002000': leftmost digit = current month's bucket
CHAR_MAP = {}                 # non-digit codes -> digit, e.g. {"X": "9", "W": "9"}
STRIP_CHARS = " "             # characters removed before parsing (padding, separators)
SPINE_BUCKETS = (4, 5, 6, 7)  # today's spine
EXIT_BUCKET = 8               # 8+ is a different category (leaves the spine)
BACKTEST_MONTHS = 6           # outcomes are read from the newest k digits

# --- optional columns on the same dataset (None = not available) -----------------
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
# (1/0). Used to measure agreement with this package's bust_out and holding.
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
sha256 `bee2fa01e483a8554e9515c797a782865f5875a08c64a97fd3e56df3536c7ebc` · 133 lines · trailing newline: yes

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

Billing-cycle artefacts are repaired before encoding: a +2 jump next to a hold
(3 3 5 or 3 5 5) is rewritten as the straight roll it was (3 4 5). A +2 jump with no
neighbouring hold stays and is read as a roll (paid nothing); both are counted.

Features are built to be invariant to the current bucket, which for most of the
spine is only a clock (months since reaching 4): lifetime and run-up features are
fixed once the account passes 4, and recent-behaviour features are rates within the
current spell.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N, R, H, P = 0, 1, 2, 3
LETTERS = "NRHP"


def _repair(b: np.ndarray) -> tuple[np.ndarray, int, int]:
    """Undo +2 billing-cycle jumps that sit next to a hold. Returns (b, repaired, left)."""
    b = b.copy()
    repaired = 0
    for i in np.flatnonzero(np.diff(b) == 2):
        if i + 2 < len(b) and b[i + 2] == b[i + 1]:          # 3 5 5 -> 3 4 5
            b[i + 1] -= 1
            repaired += 1
        elif i >= 1 and b[i] == b[i - 1]:                     # 3 3 5 -> 3 4 5
            b[i] += 1
            repaired += 1
    left = int((np.diff(b) >= 2).sum())
    return b, repaired, left


def encode(dpd: str, repair: bool = True) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    b = np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)
    if repair:
        b = _repair(b)[0]
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
    raw = np.maximum(np.array([int(ch) for ch in reversed(dpd)]), 1)
    _, n_repaired, n_jumps_left = _repair(raw)
    b, d, c = encode(dpd)
    paid = np.clip(1 - d, 0, None)                      # months paid per month

    episodes = _runs(b >= 2)                            # current spell is the last one
    sp_start, sp_end = episodes[-1]
    # a blip is a 1–2 month excursion that never went past 2 (0 0 2 0 0)
    is_blip = [e - s <= 2 and b[s:e].max() <= 2 for s, e in episodes[:-1]]
    prior = [ep for ep, blip in zip(episodes[:-1], is_blip) if not blip]
    first_spell = (prior + [episodes[-1]])[0][0]        # blips don't end clean tenure

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
        # run-up (fixed once past 4)
        "runup_len": int(first4 - sp_start + 1),        # 3 = straight 2-3-4
        "runup_holds": int((ru_c == H).sum()),
        "runup_pays": int((ru_c == P).sum()),
        # current spell
        "spell_len": int(sp_end - sp_start),
        "max_hold_run": int(max(hold_runs, default=0)),
        "months_since_4": int(months_since_4),          # months in buckets 4+ this spell
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
        "n_jumps_repaired": n_repaired,
        "n_jumps_left": n_jumps_left,
    }


def build_features(df: pd.DataFrame, col: str = "dpd_string") -> pd.DataFrame:
    feats = pd.DataFrame([journey_features(s) for s in df[col]], index=df.index)
    return pd.concat([df, feats], axis=1)
`````

### FILE: `dpd_states/states.py`
sha256 `a9ac97495996d19b2f73dfaa4c74a956dd7b3573774ca48562c27c6c89842ae8` · 152 lines · trailing newline: yes

`````python
"""Deterioration states for the bucket 4–7 spine: a small decision tree, MECE by construction.

Questions are asked in order; the first 'yes' assigns the state. Optional questions are
switched on per option (A / B / C) and never break MECE.

    Q1  Early payment default?  <=3 months of history before this spell (at most one
                                blip inside it, no earlier real spell), run-up to 4
                                took <=3 months                -> early_payment_default
    Q2  Stabilized?             5 of the last 6 months within today's bucket ±1,
                                OR (>= 6 months in buckets 4+ AND at most 1 bucket
                                higher than 6 months ago)      -> stabilized
    Q3  Paying since 4?         [tested, NOT recommended] paid >= half a month's
                                due per month since first reaching 4 -> paying_since_4
    Q4  Repeat delinquent?      [B, C] an earlier spell reached bucket 3 and cured
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
Q2 describes current behaviour and moves month to month; every other state is fixed once
the account has passed bucket 4.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

DEFAULTS = {
    "epd_max_history": 3,           # months of history before the current spell (blip incl.)
    "epd_max_blips": 1,             # at most one blip (1–2 months at 2, paid off) in that history
    "straight_max_runup": 3,        # months from last clean month to first month at 4
    "stabilized_min_in_band": 5,    # of the last 6 months within today's bucket ±1
    # Long-run clause: an account that has stayed in buckets 4+ for 6 months while rising
    # at most one bucket has paid roughly what was due, even if unevenly (oscillating
    # payers, accounts that just paid down). Straight rollers cannot meet it: they leave
    # the spine within ~4 months. None disables it.
    "stabilized_long_run_months": 6,
    "stabilized_long_run_max_rise": 1,
    # Q3 tested and NOT recommended: unstable (~37% leave it each month), drags the
    # stability of other states to ~90%, barely separates risk, and is mostly the
    # credibility axis's 'money coming in'. Kept only so the test can be repeated.
    "paying_since_4_min_rate": None,  # e.g. 0.5 -> Q3 on
    "repeat_min_prior_peak": None,  # e.g. 3   -> Q4 on (spell counted from bucket 3)
    "seasoned_min_months": None,    # e.g. 12  -> split straight roller (first year on book = early life)
    "split_slow_roller": False,     # True     -> split slow roller by 2+ month payments in run-up
}

OPTIONS = {
    "A_minimal_4": {},
    "B_balanced_6": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12},
    "C_detailed_7": {"repeat_min_prior_peak": 3, "seasoned_min_months": 12, "split_slow_roller": True},
}
RECOMMENDED = "B_balanced_6"

STATE_ORDER = ["early_payment_default", "stabilized", "paying_since_4", "repeat_delinquent",
               "straight_roller", "straight_roller_seasoned", "straight_roller_early_life",
               "slow_roller", "slow_roller_intermittent", "slow_roller_erratic"]
FIXED_STATES = [s for s in STATE_ORDER if s not in ("stabilized", "paying_since_4")]

# Business labels (common card-risk / collections terms). Change freely: code never
# reads these, so renaming for the risk team cannot break the pipeline or old results.
DISPLAY_NAMES = {
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
    "early_payment_default": "Never really paid: defaulted within the first three payments. Called "
                             "'bust-out' internally — but classic bust-out fraud (good history, limit "
                             "build-up, then max-out) shows as a seasoned straight roller and needs a "
                             "fraud overlay on spend data.",
    "stabilized": "The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months in "
                  "buckets 4+, at most one bucket higher than 6 months ago) so oscillating "
                  "payers and accounts that just paid down are not mislabelled.",
    "paying_since_4": "Rejected — current-behaviour state that belongs to credibility (money coming in).",
    "repeat_delinquent": "Re-default after a cured spell; collections 'recidivism'.",
    "straight_roller": "Rolled through every bucket without paying.",
    "straight_roller_seasoned": "Straight roller after at least a year on book (seasoned).",
    "straight_roller_early_life": "Straight roller in the first year on book (early-life default).",
    "slow_roller": "Paid something on the way down but kept rolling. Also called partial payer.",
    "slow_roller_intermittent": "Slow roller that paid one month here and there.",
    "slow_roller_erratic": "Slow roller that caught up 2+ months at once, then rolled again.",
}


def assign_states(f: pd.DataFrame, **params) -> pd.Series:
    """f: output of features.build_features. Returns one state name per row."""
    p = {**DEFAULTS, **params}
    fast = f.runup_len <= p["straight_max_runup"]
    conds, names = [], []

    def add(cond, name):
        conds.append(cond)
        names.append(name)

    add((f.months_before_spell <= p["epd_max_history"]) & (f.n_blips <= p["epd_max_blips"])
        & (f.n_prior_episodes == 0) & fast, "early_payment_default")
    stab = f.last6_in_band >= p["stabilized_min_in_band"]
    if p["stabilized_long_run_months"] is not None:
        stab |= ((f.months_since_4 >= p["stabilized_long_run_months"])
                 & (f.chg_6m <= p["stabilized_long_run_max_rise"]))
    add(stab, "stabilized")
    if p["paying_since_4_min_rate"] is not None:
        add(f.post4_paid_rate >= p["paying_since_4_min_rate"], "paying_since_4")
    if p["repeat_min_prior_peak"] is not None:
        add(f.max_prior_bucket >= p["repeat_min_prior_peak"], "repeat_delinquent")
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
sha256 `62e3fe95ec69da9d63b0a9bbf60bee146411d31d28231beafa898dc664f9492c` · 377 lines · trailing newline: yes

`````python
"""Real-data analysis of deterioration states — pure pandas, no Spark.

`run(current, latest_bt, cfg)` takes two small pandas frames that the Spark snippet has
already scoped and sampled:

    current    accounts in today's spine (current bucket 4–7): `dpd_string` plus any
               optional columns named as the keys of cfg.AXIS_COLS / EXISTING_RULE_COLS /
               FLAG_COLS.
    latest_bt  accounts that were in the spine k = cfg.BACKTEST_MONTHS months ago, with
               their string AS OF TODAY (k newer digits on the left). Dropping those k
               digits gives the string as it was k months ago; the dropped digits are what
               happened next. None = no backtest (outcome checks are skipped).

Returns (results, markdown). `results` is JSON-serialisable aggregates only — no keys,
no row-level data — so it can be committed. The markdown adds a handful of example
DPD strings (no keys) for eyeballing.
"""
from __future__ import annotations

import re

import numpy as np
import pandas as pd

from . import discover as dv
from .features import build_features, encode, _runs
from .states import (DISPLAY_NAMES, FIXED_STATES, OPTIONS, RECOMMENDED, REMARKS,
                     assign_states, order)


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


def _records(df: pd.DataFrame) -> list[dict]:
    out = df.reset_index().replace({np.nan: None})
    return [{k: (round(v, 4) if isinstance(v, (float, np.floating)) else
                 (v.item() if hasattr(v, "item") else v)) for k, v in r.items()}
            for r in out.to_dict("records")]


def clean_strings(s: pd.Series, char_map: dict, strip_chars: str, leftmost_is_current: bool = True):
    """Normalise strings; returns (clean series, valid mask)."""
    s = s.astype(str)
    if strip_chars:
        s = s.str.replace(f"[{re.escape(strip_chars)}]", "", regex=True)
    for a, b in (char_map or {}).items():
        s = s.str.replace(a, b, regex=False)
    if not leftmost_is_current:
        s = s.str[::-1]
    valid = s.str.fullmatch(r"\d+").fillna(False) & (s.str.len() > 0)
    return s, valid


def _spells(s: str, from_bucket: int) -> int:
    b = encode(s)[0]
    return sum(1 for a, e in _runs(b >= 2) if b[a:e].max() >= from_bucket)


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
        "cure_k": digits.apply(lambda d: min(d) <= 1),
    })


def backtest_scorecard(f: pd.DataFrame, state: pd.Series, state_next: pd.Series) -> pd.DataFrame:
    g = f.assign(state=state)
    out = pd.DataFrame({"share": g.state.value_counts(normalize=True),
                        "n": g.state.value_counts()})
    out["roll_next_month"] = (g.next_bucket >= g.b_now + 1).groupby(g.state).mean()
    out["exit_8plus_within_k"] = g.groupby("state").exit_k.mean()
    out["cure_within_k"] = g.groupby("state").cure_k.mean()
    out["median_bucket_change_k"] = (g.bucket_k.clip(upper=9) - g.b_now).groupby(g.state).median()
    idx = state_next.index
    out["same_state_next_month"] = (state.loc[idx] == state_next).groupby(state.loc[idx]).mean()
    out["left_spine_next_month"] = (~g.next_bucket.between(4, 7)).groupby(g.state).mean()
    return out.loc[order(out.index)]


def stabilized_flips(latest: pd.Series, k: int, spine, n: int = 10_000, seed: int = 7) -> dict:
    """Month-by-month stabilized status over the k backtest months, for a sample of the
    backtest population. A 'bounce-back' is an account that LEFT stabilized and later came
    BACK while staying in the spine (S . S). Entering once and leaving once (. S S .) is a
    normal lifecycle and is not counted. Reported with and without the long-run clause."""
    latest = latest[latest.str.len() > k]
    latest = latest.sample(min(n, len(latest)), random_state=seed)
    rows = [{"acct": i, "j": j, "dpd_string": s_[k - j:]}
            for i, s_ in latest.items() for j in range(k + 1)]
    panel = pd.DataFrame(rows)
    panel = panel[panel.dpd_string.str[0].astype(int).isin(spine)]
    pf = build_features(panel)
    out = {"n_accounts": int(latest.size)}
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


# --- main ----------------------------------------------------------------------------

def run(current: pd.DataFrame, latest_bt: pd.DataFrame | None, cfg, seed: int = 7):
    k = cfg.BACKTEST_MONTHS
    spine = tuple(cfg.SPINE_BUCKETS)
    R, M = {}, []            # results (JSON) and markdown sections
    rng = np.random.default_rng(seed)

    # ---- data quality + current spine --------------------------------------------
    s, ok = clean_strings(current.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
    cur = current.assign(dpd_string=s)[ok]
    cur = cur[cur.dpd_string.str[0].astype(int).isin(spine)]
    f = build_features(cur)
    f["state"] = assign_states(f, **OPTIONS[RECOMMENDED])
    opts = {o: assign_states(f, **kw) for o, kw in OPTIONS.items()}

    one3 = (f.dpd_string.map(lambda x: _spells(x, 3)) == 1).mean()
    one4 = (f.dpd_string.map(lambda x: _spells(x, 4)) == 1).mean()
    dq = {
        "n_current_rows": int(len(current)),
        "share_invalid_strings": float(1 - ok.mean()),
        "n_current_spine_analysed": int(len(f)),
        "string_length_p05_p50_p95": [int(x) for x in f.hist_len.quantile([.05, .5, .95])],
        "share_left_censored": float(f.left_censored.mean()),
        "share_jump_repaired": float((f.n_jumps_repaired > 0).mean()),
        "share_jump_left": float((f.n_jumps_left > 0).mean()),
        "share_one_spell_from3": float(one3),
        "share_one_spell_from4": float(one4),
        "bucket_mix": {int(b): float(v) for b, v in f.b_now.value_counts(normalize=True).sort_index().items()},
    }
    R["data_quality"] = dq
    R["state_names"] = {s: {"display": DISPLAY_NAMES[s], "remark": REMARKS[s]} for s in DISPLAY_NAMES}
    M.append("## State names\n\n" + md(pd.DataFrame(
        [{"code": s, "display name": DISPLAY_NAMES[s], "remark": REMARKS[s]} for s in DISPLAY_NAMES]),
        index=False))
    M.append("## 1. Data quality and population\n\n" + md(pd.Series(dq, name="value").rename_axis("metric").to_frame()))

    # ---- states today, all options ----------------------------------------------
    R["states_today"] = {}
    parts = ["## 2. States today (current spine)"]
    for o, st in opts.items():
        share = st.value_counts(normalize=True)
        by_b = pd.crosstab(st, f.b_now, normalize="columns")
        share = share.loc[order(share.index)].rename_axis("state")
        by_b = by_b.loc[order(by_b.index)].rename_axis(index="state", columns="bucket")
        R["states_today"][o] = {"share": share.round(4).to_dict(),
                                "by_bucket": {int(c): by_b[c].round(4).to_dict() for c in by_b.columns},
                                "mece": bool(st.notna().all())}
        parts.append(f"### {o}\n\nShare:\n\n" + md(share.to_frame("share"))
                     + "\n\nMix by current bucket (column shares):\n\n" + md(by_b))
    ex = (f.sample(frac=1.0, random_state=seed).groupby("state").head(3)[["state", "dpd_string"]]
          .sort_values("state", key=lambda x: x.map({s: i for i, s in enumerate(order(x))}))
          .assign(last_30_months_oldest_to_newest=lambda x: x.dpd_string.str[:30].str[::-1]))
    parts.append(f"Examples ({RECOMMENDED}, no keys):\n\n"
                 + md(ex[["state", "last_30_months_oldest_to_newest"]], index=False))
    M.append("\n\n".join(parts))

    # ---- agreement with the bank's existing rules -------------------------------
    agree = {}
    for col, ours in (("existing_bust_out", "early_payment_default"), ("existing_stabilized", "stabilized")):
        if col in f and f[col].notna().any():
            theirs = pd.to_numeric(f[col], errors="coerce").fillna(0).astype(bool)
            mine = f.state == ours
            agree[ours] = {"their_share": float(theirs.mean()), "our_share": float(mine.mean()),
                           "recall_of_theirs": float((mine & theirs).sum() / max(theirs.sum(), 1)),
                           "precision_vs_theirs": float((mine & theirs).sum() / max(mine.sum(), 1))}
    R["existing_rule_agreement"] = agree or "SKIPPED (no existing rule columns configured)"
    M.append("## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules\n\n"
             + (md(pd.DataFrame(agree).T.rename_axis("state")) if agree else "_Skipped — no existing rule columns configured._"))

    # ---- overlap with the other persona axes ------------------------------------
    axes = [c for c in cfg.AXIS_COLS if c in f and f[c].notna().any()]
    ov = {}
    if axes:
        eta = pd.DataFrame({o: {a: _eta2(f[a], st) for a in axes} for o, st in opts.items()})
        means = f.groupby("state")[axes].agg(lambda x: pd.to_numeric(x, errors="coerce").mean())
        means = means.loc[order(means.index)]
        eta = eta.rename_axis("axis")
        ov = {"eta2_by_option": _records(eta), "mean_by_state": _records(means)}
        txt = ("Variance of each axis explained by the states (eta², 0 = orthogonal):\n\n" + md(eta)
               + f"\n\nMean of each axis by state ({RECOMMENDED}):\n\n" + md(means))
    else:
        txt = "_No axis columns configured — using the DPD proxy for 'money coming in' only._"
    money = "cred_money_in_points" if "cred_money_in_points" in axes else None
    paid_now = (pd.to_numeric(f[money], errors="coerce") > 0) if money else f.paid_any_3m
    hold = f.state == "stabilized"
    ov["stabilized_vs_money_in"] = {"source": money or "DPD proxy (paid >= 1 month in last 3)",
                                    "stabilized_with_money_in": float(paid_now[hold].mean()) if hold.any() else None,
                                    "others_with_money_in": float(paid_now[~hold].mean())}
    flags = {c: float(pd.to_numeric(f.loc[hold, c], errors="coerce").fillna(0).astype(bool).mean())
             for c in cfg.FLAG_COLS if c in f and f[c].notna().any()}
    ov["stabilized_flagged"] = flags
    R["overlap_other_axes"] = ov
    M.append("## 4. Overlap with the other persona axes\n\n" + txt + "\n\nStabilized vs money coming in:\n\n"
             + md(pd.Series(ov["stabilized_vs_money_in"], name="value").rename_axis("metric").to_frame())
             + ("\n\nShare of stabilized accounts carrying a data flag (frozen bucket, not a payment):\n\n"
                + md(pd.Series(flags, name="share").to_frame()) if flags else ""))

    # ---- backtest: outcomes and stability ----------------------------------------
    bt = None
    if latest_bt is not None and len(latest_bt):
        s2, ok2 = clean_strings(latest_bt.dpd_string, cfg.CHAR_MAP, cfg.STRIP_CHARS)
        btf = backtest_frame(s2[ok2], k, spine, cfg.EXIT_BUCKET)
        bt = build_features(btf)
        nxt = btf[btf.next_bucket.isin(spine)][["next_string"]].rename(columns={"next_string": "dpd_string"})
        nf = build_features(nxt)
        roll = (bt.next_bucket >= bt.b_now + 1).groupby(bt.b_now).mean()
        R["backtest"] = {"k_months": k, "n_analysed": int(len(bt)),
                         "share_exited_within_k": float(bt.exit_k.mean()),
                         "monthly_roll_rate": {int(b): float(v) for b, v in roll.items()},
                         "scorecards": {}}
        parts = [f"## 5. Backtest — spine as of {k} months ago, outcomes since\n\n"
                 f"{len(bt):,} accounts. Monthly roll rate by bucket (should match the bank's "
                 "~70/80/90/95%):\n\n" + md(roll.rename_axis("bucket").to_frame("roll_rate"))]
        for o, kw in OPTIONS.items():
            card = backtest_scorecard(bt, assign_states(bt, **kw), assign_states(nf, **kw))
            R["backtest"]["scorecards"][o] = _records(card)
            parts.append(f"### {o}\n\n" + md(card))
        flips = stabilized_flips(s2[ok2], k, spine, seed=seed)
        R["backtest"]["stabilized_flips"] = flips
        parts.append(f"### Stabilized bounce-backs over the {k} backtest months "
                     f"({flips['n_accounts']:,} accounts)\n\nShare of ever-stabilized accounts that left "
                     "stabilized and came back while staying in the spine (S . S):\n\n"
                     + md(pd.DataFrame({kk: v for kk, v in flips.items() if isinstance(v, dict)}).T
                          .rename_axis("stabilized rule")))
        M.append("\n\n".join(parts))
    else:
        R["backtest"] = "SKIPPED (no latest-month strings for the backtest population)"
        M.append("## 5. Backtest\n\n_Skipped — no backtest population supplied._")

    # ---- threshold sweeps (on the backtest population when available) ------------
    base, nb = (bt, nf) if bt is not None else (f, None)
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
                     "exit_within_k": base.exit_k[b_].mean() if bt is not None else None})
    sw["epd_max_history"] = rows
    rows = []
    for v in (4, 5, 6):
        st = assign_states(base, stabilized_min_in_band=v)
        h = st == "stabilized"
        rows.append({"stabilized_min_in_band": v, "share": h.mean(),
                     "roll_next_month": (base.next_bucket[h] >= base.b_now[h] + 1).mean() if bt is not None else None,
                     "still_stabilized_next_month": _stay({"stabilized_min_in_band": v}, "stabilized")})
    sw["stabilized_min_in_band"] = rows
    rows = []
    for v in (2, 3, 4):
        st = assign_states(base, **{**OPTIONS[RECOMMENDED], "repeat_min_prior_peak": v})
        rows.append({"repeat_min_prior_peak": v, "share": (st == "repeat_delinquent").mean()})
    sw["repeat_min_prior_peak"] = rows
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
    R["sweeps"] = {kk: [{a: (round(b, 4) if isinstance(b, float) else b) for a, b in r.items()} for r in v]
                   for kk, v in sw.items()}
    M.append("## 6. Threshold sweeps (" + ("backtest population" if bt is not None else "current spine")
             + ")\n\n" + "\n\n".join(f"### {kk}\n\n" + md(pd.DataFrame(v), index=False) for kk, v in sw.items()))

    # ---- residual clustering agreement -------------------------------------------
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    a_states = opts["A_minimal_4"]
    res = ~a_states.isin(["early_payment_default", "stabilized"])
    r = f[res]
    if len(r) > 30_000:
        r = r.sample(30_000, random_state=seed)
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
    M.append("## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with "
             "each option\n\n" + md(pd.DataFrame(rows), index=False))

    # ---- shapes and motifs ---------------------------------------------------------
    smp = f.sample(min(len(f), 30_000), random_state=seed)
    shapes = dv.shape_table(smp, label="state", top=20)
    grams = dv.ngram_table(smp, n=4, label="state", top=15)
    R["top_shapes"] = _records(shapes.set_index("shape"))
    R["top_4grams"] = _records(grams.set_index("gram"))
    M.append("## 8. Most common journey shapes and motifs\n\nShapes (N clean, R roll, H hold = paid "
             "one month, P paid 2+ months; run lengths banded):\n\n" + md(shapes, index=False)
             + "\n\n4-grams by lift vs shuffled order:\n\n" + md(grams, index=False))

    return R, "\n\n".join(M)
`````

### FILE: `dpd_states/expectations.py`
sha256 `bec4c39af79539ab4dea7cdcefcdada6def8e665c07f8dbe5e1c5d5995a19ed9` · 247 lines · trailing newline: yes

`````python
"""What we expect to see on real data, as checkable rules.

Each expectation states the metric, the expected range, why we expect it (synthetic
validation or the bank's own figures), and what to do if it is not met. `evaluate(R)`
reads the results dict from analysis.run and returns one row per check with
PASS / WARN / FAIL / SKIPPED / INFO.

Severity: FAIL = the run itself is not trustworthy (fix config/data before reading
anything else). WARN = the run is fine but an assumption behind the design is off —
follow the 'if not met' action. INFO = reported, no expectation.
"""
from __future__ import annotations

import pandas as pd

from .states import FIXED_STATES, RECOMMENDED

ROLL_TARGET = {4: 0.70, 5: 0.80, 6: 0.90, 7: 0.95}


def _card(R, option):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    return pd.DataFrame(bt["scorecards"][option]).set_index("state" if "state" in bt["scorecards"][option][0] else "index")


def _share(R, option):
    return pd.Series(R["states_today"][option]["share"])


def _sweep(R, name):
    return pd.DataFrame(R["sweeps"][name])


def _eta(R, axis, option=RECOMMENDED):
    ov = R.get("overlap_other_axes", {})
    if "eta2_by_option" not in ov:
        return None
    eta = pd.DataFrame(ov["eta2_by_option"]).set_index("axis")
    return float(eta.loc[axis, option]) if axis in eta.index else None


def _agree(R, state, key):
    a = R.get("existing_rule_agreement")
    return a[state][key] if isinstance(a, dict) and state in a else None


def _stab_gap(R):
    c = _card(R, RECOMMENDED)
    if c is None or "stabilized" not in c.index:
        return None
    rolling = c.loc[[s for s in c.index if s in FIXED_STATES], "roll_next_month"]
    w = c.loc[rolling.index, "share"]
    return float((rolling * w).sum() / w.sum() - c.loc["stabilized", "roll_next_month"])


def _fixed_stability(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    return float(c.loc[[s for s in c.index if s in FIXED_STATES], "same_state_next_month"].min())


def _roll_dev(R):
    bt = R.get("backtest")
    if not isinstance(bt, dict):
        return None
    rr = {int(k): v for k, v in bt["monthly_roll_rate"].items()}
    return max(abs(rr.get(b, float("nan")) - t) for b, t in ROLL_TARGET.items())


def _resid_gain(R):
    rows = pd.DataFrame(R["residual_cluster_agreement"]).set_index("k")
    return float(rows.loc[6, f"agree_{RECOMMENDED}"] - rows.loc[6, "agree_A_minimal_4"])


def _runup_sharpness(R):
    sw = _sweep(R, "straight_max_runup").set_index("straight_max_runup")
    g3 = sw.loc[3, "slow_share"]
    return float(sw.loc[4, "slow_share"] / g3) if g3 else None


def _partial(R):
    sw = _sweep(R, "paying_since_4_test").set_index("paying_since_4_min_rate")
    if "stability_of_fixed_states" not in sw:
        return None
    r = sw.loc[0.5]
    return {"still_partial": r["still_paying_since_4_next_month"],
            "stability_drop": r["stability_of_fixed_states_without_q3"] - r["stability_of_fixed_states"]}


def _spread(R):
    c = _card(R, RECOMMENDED)
    if c is None:
        return None
    x = c.loc[[s for s in c.index if s in FIXED_STATES], "exit_8plus_within_k"]
    return float(x.max() - x.min())


# id, title, metric(R), check(value)->bool, expected (text), severity, why, if not met
EXPECTATIONS = [
    ("E01", "Every account gets exactly one state (all options)",
     lambda R: all(v["mece"] for v in R["states_today"].values()), lambda v: v is True,
     "True", "FAIL", "The tree has a default branch, so it is MECE by construction.",
     "A code or data-type bug — stop and fix before reading anything else."),
    ("E02", "Share of DPD strings that cannot be parsed",
     lambda R: R["data_quality"]["share_invalid_strings"], lambda v: v <= 0.02,
     "<= 2%", "FAIL", "Strings should be digits once CHAR_MAP / STRIP_CHARS are set.",
     "Inspect the non-digit characters; extend CHAR_MAP or STRIP_CHARS in config.py."),
    ("E03", "Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation)",
     _roll_dev, lambda v: v <= 0.07,
     "<= 7pp", "FAIL", "Confirms the string orientation and the backtest reconstruction are right.",
     "Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine "
     "(survivor-only data shows roll rates that are too low)."),
    ("E04", "Share of histories that start inside the current spell (no clean month seen)",
     lambda R: R["data_quality"]["share_left_censored"], lambda v: v <= 0.10,
     "<= 10%", "WARN", "Full history is available for everyone.",
     "Strings are truncated; EPD (short history) will be over-assigned — cap the "
     "EPD rule to accounts with full history or raise the threshold."),
    ("E05", "Share of accounts with an unrepaired +2 jump",
     lambda R: R["data_quality"]["share_jump_left"], lambda v: v <= 0.02,
     "<= 2%", "WARN", "Billing-cycle jumps are mostly next to a hold and get repaired.",
     "Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding."),
    ("E06", "Current bucket mix declines from 4 to 7",
     lambda R: R["data_quality"]["bucket_mix"].get(4, 0) - R["data_quality"]["bucket_mix"].get(7, 0),
     lambda v: v >= 0, ">= 0", "WARN", "Flow-driven book with rising roll rates (synthetic 29/26/23/22%).",
     "Check the spine filter and whether a cohort shock is passing through."),
    ("E07", "One spell only, spell counted from bucket 3",
     lambda R: R["data_quality"]["share_one_spell_from3"], lambda v: 0.78 <= v <= 0.92,
     "78–92%", "WARN", "Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one "
     "near 85%, the bank counts spells from 4.",
     "Set repeat_min_prior_peak to whichever spell definition matches the bank's 85%."),
    ("E08", "Early payment default (EPD, 'bust-out') share (today)",
     lambda R: _share(R, RECOMMENDED).get("early_payment_default", 0), lambda v: 0.04 <= v <= 0.08,
     "4–8%", "WARN", "Bank's own rule gives ~6% (synthetic 5.8%).",
     "Move epd_max_history along the sweep until the share matches the bank's rule."),
    ("E09", "Stabilized share (today)",
     lambda R: _share(R, RECOMMENDED).get("stabilized", 0), lambda v: 0.04 <= v <= 0.09,
     "4–9%", "WARN", "Bank's own stabilized rule gives ~6% (synthetic 6.6%).",
     "Compare with the bank's implementation of the 5-of-6 rule (E10/E11)."),
    ("E10", "Recall of the bank's existing bust-out (EPD) flag",
     lambda R: _agree(R, "early_payment_default", "recall_of_theirs"), lambda v: v >= 0.80,
     ">= 80%", "WARN", "Same concept; thresholds may differ slightly.",
     "Read the bank's rule and align epd_max_history / epd_max_blips."),
    ("E11", "Recall of the bank's existing stabilized flag",
     lambda R: _agree(R, "stabilized", "recall_of_theirs"), lambda v: v >= 0.90,
     ">= 90%", "WARN", "Stabilized IS the bank's 5-of-6 rule; only EPD-first ordering differs.",
     "Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today)."),
    ("E12", "Stabilized separates risk: weighted next-month roll of fixed states minus stabilized",
     _stab_gap, lambda v: v >= 0.20,
     ">= 20pp", "WARN", "Synthetic: stabilized 40% vs ~85% for the rest.",
     "Stabilized is not behaving as 'stable'; check payment holidays / restructuring flags (E21) "
     "and try stabilized_min_in_band = 6."),
    ("E13", "Fixed states keep their state next month (minimum over fixed states)",
     _fixed_stability, lambda v: v >= 0.95,
     ">= 95%", "WARN", "Run-up and history are fixed once past 4 (synthetic 98–100%).",
     "A feature is drifting with time since 4 — inspect which state leaks and why."),
    ("E14", "Stabilized persistence next month",
     lambda R: (_card(R, RECOMMENDED).loc["stabilized", "same_state_next_month"]
                if _card(R, RECOMMENDED) is not None else None),
     lambda v: 0.45 <= v <= 0.85, "45–85%", "WARN",
     "Stabilized is current behaviour; it should persist but not forever (synthetic 62%).",
     "Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments."),
    ("E15", "Option A: straight-roller share",
     lambda R: _share(R, "A_minimal_4").get("straight_roller", 0), lambda v: 0.55 <= v <= 0.80,
     "55–80%", "WARN", "Most accounts roll straight 2-3-4 (synthetic 70%).",
     "If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting slow roller."),
    ("E16", "Every option-B state holds at least 5% of the spine",
     lambda R: float(_share(R, "B_balanced_6").min()), lambda v: v >= 0.05,
     ">= 5%", "WARN", "Actionable size. Synthetic: straight_roller_early_life 3.4% under the 12-month "
     "seasoned cut (depends on the book's tenure mix).",
     "Merge the small state into its neighbour (repeat_delinquent→straight_roller, "
     "early-life→seasoned), or move seasoned_min_months along its sweep (12 → 18 → 24 months)."),
    ("E17", "Option C: smaller of intermittent / erratic payer (slow-roller split)",
     lambda R: float(_share(R, "C_detailed_7").reindex(["slow_roller_intermittent", "slow_roller_erratic"]).fillna(0).min()),
     lambda v: v >= 0.04, ">= 4%", "WARN", "Synthetic 10% / 6%.",
     "Too small to act on — use option B."),
    ("E18", "Stabilized sits low in the spine: share at bucket 4 / share at bucket 7",
     lambda R: (R["states_today"][RECOMMENDED]["by_bucket"].get(4, {}).get("stabilized", 0)
                / max(R["states_today"][RECOMMENDED]["by_bucket"].get(7, {}).get("stabilized", 0), 1e-9)),
     lambda v: v >= 2, ">= 2x", "WARN", "90–95% roll rates at 6–7 leave little room to hold there.",
     "Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays)."),
    ("E19", "Orthogonality: credibility score explained by the states (eta²)",
     lambda R: _eta(R, "credibility_score"), lambda v: v <= 0.25,
     "<= 0.25", "WARN", "Known overlap via stabilized (money in) and repeat delinquent (clean point), but "
     "the states should not reproduce the score.",
     "Use option A (drops repeat delinquent) or report stabilized under credibility instead."),
    ("E19b", "Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²)",
     lambda R: _eta(R, "cred_clean_point"), lambda v: v <= 0.50,
     "<= 0.50", "WARN", "Repeat delinquent is defined from earlier spells — the same history the clean point "
     "scores. Synthetic (with a clean point = 'no earlier spell'): 0.84 → WARN.",
     "Repeat delinquent duplicates the credibility clean point: use option A, or keep it and "
     "tell the persona grid it is the same signal (it is only 1 of credibility's 5 points)."),
    ("E20", "Orthogonality: ability score explained by the states (eta²)",
     lambda R: _eta(R, "ability_score"), lambda v: v <= 0.10,
     "<= 0.10", "WARN", "DPD shape should carry little of salary/inflow/CASA.",
     "Straight vs slow roller may be a proxy for income loss — fine, but say so in the persona grid."),
    ("E21", "Stabilized accounts with money coming in (credibility component or DPD proxy)",
     lambda R: R["overlap_other_axes"]["stabilized_vs_money_in"]["stabilized_with_money_in"],
     lambda v: v >= 0.90, ">= 90%", "WARN",
     "Stabilized = paid one month's due most months, so money must be coming in (synthetic 100%).",
     "Stabilized accounts without money in are frozen buckets (holiday/restructure) — exclude those months."),
    ("E22", "Residual clusters agree more with option B than with A (ARI gain at k=6)",
     _resid_gain, lambda v: v >= 0.15, ">= 0.15", "WARN",
     "Synthetic at k=6: 0.32 (B) vs 0.11 (A) — the data has more than two residual groups.",
     "The extra B splits are not natural groups in this book — prefer option A."),
    ("E23", "One paid month on the way down matters: slow-roller share at run-up<=4 / at <=3",
     _runup_sharpness, lambda v: v <= 0.70, "<= 0.70", "WARN",
     "Synthetic ~0.58: most slow rollers held exactly once.",
     "Slow roller is driven by long run-ups, not single payments — keep 3 but review examples."),
    ("E24", "'Paying since 4' stays rejected: share still in it next month at 0.5",
     lambda R: (_partial(R) or {}).get("still_partial"), lambda v: v <= 0.75, "<= 75%", "WARN",
     "Synthetic 63%: unstable current-behaviour state.",
     "If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'."),
    ("E26", "Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months",
     lambda R: R["backtest"]["stabilized_flips"]["with_long_run_clause"]["bounce_back_share_of_ever_stabilized"],
     lambda v: v <= 0.10, "<= 10%", "WARN",
     "Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating "
     "payers bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold) "
     "and swingers in their first 6 months at 4 (both rules are reported).",
     "Too many accounts bounce: look at examples; consider stabilized_long_run_max_rise = 2 "
     "or a sticky rule — but both widen the definition, so agree it with the business."),
    ("E25", "INFO — spread of exit-within-k across fixed states (option B)",
     _spread, None, "report", "INFO",
     "Synthetic data cannot show this (same post-4 dynamics by construction).",
     ">= 5pp means the mechanism carries risk information beyond stabilized."),
]


def evaluate(R: dict) -> pd.DataFrame:
    rows = []
    for eid, title, metric, check, expected, sev, why, action in EXPECTATIONS:
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
                     "expected": expected, "why": why, "if_not_met": action})
    return pd.DataFrame(rows)
`````

### FILE: `dpd_states/discover.py`
sha256 `b2d4b8c967fb02377cd4be537cae42f29f56d163499033cb0dc1dcbf96a09155` · 134 lines · trailing newline: yes

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
sha256 `7f7fb03d9ba0016e22ed544d030806ea57b76a779fc2c616a7ec74fe4e2e8c36` · 119 lines · trailing newline: yes

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
]


def check_cases() -> list[str]:
    import pandas as pd
    df = pd.DataFrame({"dpd_string": [c.replace(" ", "")[::-1] for c, _, _ in CASES]})
    got = assign_states(build_features(df), **OPTIONS[RECOMMENDED])
    lines, bad = [], 0
    for (c, want, why), g in zip(CASES, got):
        ok = g == want
        bad += not ok
        lines.append(f"{'OK  ' if ok else 'FAIL'} {c:<30} -> {g:<27} {'' if ok else '(expected ' + want + ') '}{why}")
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
    print("\nEdge cases (oldest -> newest, option B):\n" + "\n".join(case_lines))
    (OUT / f"selftest_report_{stamp}.md").write_text(
        (OUT / f"selftest_report_{stamp}.md").read_text().replace(
            "## 0. Expectation checks", "## 0a. Edge cases (oldest → newest, option B)\n\n```\n"
            + "\n".join(case_lines) + "\n```\n\n## 0. Expectation checks"))
    ok = ((checks.status != "FAIL").all() and checks.set_index("id").loc["E01", "status"] == "PASS"
          and bad == 0)
    print("\nSELFTEST", "PASSED" if ok else "FAILED", f"-> {OUT}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]) if len(sys.argv) > 1 else 20_000))
`````

### FILE: `dpd_states/bundle.py`
sha256 `4a714ce4b9da1459c1c93087e943a36d8a87c9c5b72d4e2d549ecab48003285c` · 216 lines · trailing newline: yes

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
    "PROMPTS.md",
    "dpd_states/__init__.py",
    "dpd_states/config.py",
    "dpd_states/features.py",
    "dpd_states/states.py",
    "dpd_states/analysis.py",
    "dpd_states/expectations.py",
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
sha256 `88d15f86343211a90c4eaf0eca63bd094abfc8d6c5662e0a5afe93b3622a13e1` · 200 lines · trailing newline: yes

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
    result = main(catalog, check_only=True)        # 1st: schema, counts, examples only
    result = main(catalog)                         # full run, model_id from globals_dev
    result = main(catalog, model_id="<variant>")   # or one variant explicitly

READ-ONLY: writes nothing to the warehouse. Writes one aggregates-only JSON (+ a markdown
report) to docs/deterioration_states/results/ — no account keys, no row-level data.
The markdown contains a handful of example DPD strings (no keys) for eyeballing.

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


def main(catalog, model_id=None, out_dir=None, sample_n=100_000, check_only=False, seed=42):
    from pyspark.sql import functions as F

    sys.path.insert(0, str(_pkg_root()))
    from dpd_states import config as cfg
    from dpd_states.analysis import md, run
    from dpd_states.expectations import evaluate
    from dpd_states.states import DISPLAY_NAMES, OPTIONS, RECOMMENDED

    model_id = _resolve_model_id(model_id)
    out_dir = pathlib.Path(out_dir) if out_dir else _pkg_root() / "results"
    k = cfg.BACKTEST_MONTHS
    ds = cfg.DS_STRINGS_TMPL.format(model_id=model_id)

    unfilled = [n for n, v in (("DS_STRINGS_TMPL", ds), ("KEY", cfg.KEY), ("COL_DPD", cfg.COL_DPD))
                if "<<FILL-IN" in str(v)]
    if unfilled:
        print(f"CONFIG NOT FILLED: {unfilled} in dpd_states/config.py")
        return None

    # 1. load + schema guard ---------------------------------------------------------
    sdf = catalog.load(ds)
    required = [cfg.KEY, cfg.COL_DPD] + ([cfg.COL_SNAPSHOT] if cfg.COL_SNAPSHOT else [])
    missing = [c for c in required if c not in sdf.columns]
    if missing:
        print(f"SCHEMA MISMATCH in {ds}. missing={missing}")
        print(f"available={sorted(sdf.columns)}")
        return None
    optional = {**cfg.AXIS_COLS, **cfg.EXISTING_RULE_COLS, **cfg.FLAG_COLS}
    present = {name: col for name, col in optional.items() if col and col in sdf.columns}
    absent = {name: col for name, col in optional.items() if col and col not in sdf.columns}

    # 2. scope FIRST: filter, latest snapshot, normalise the string -------------------
    if cfg.ROW_FILTER:
        sdf = sdf.where(cfg.ROW_FILTER)
    if cfg.COL_SNAPSHOT:
        latest = sdf.agg(F.max(cfg.COL_SNAPSHOT)).first()[0]
        sdf = sdf.where(F.col(cfg.COL_SNAPSHOT) == F.lit(latest))
    s = F.col(cfg.COL_DPD).cast("string")
    if cfg.STRIP_CHARS:
        s = F.regexp_replace(s, "[" + re.escape(cfg.STRIP_CHARS) + "]", "")
    for a, b in (cfg.CHAR_MAP or {}).items():
        s = F.regexp_replace(s, re.escape(a), b)
    if not cfg.LEFTMOST_IS_CURRENT:
        s = F.reverse(s)
    sdf = sdf.select(F.col(cfg.KEY).alias("_key"), s.alias("dpd_string"),
                     *[F.col(c).alias(n) for n, c in present.items()])

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
    sdf = sdf.drop("_key")                      # keys never leave Spark

    scope_note = (f"{ds}" + (f" where {cfg.ROW_FILTER}" if cfg.ROW_FILTER else "")
                  + (f", latest {cfg.COL_SNAPSHOT}" if cfg.COL_SNAPSHOT else "")
                  + f"; today's spine = current digit in {spine}; backtest = digit {k + 1} in {spine}"
                  + f"; sampled to <= {sample_n:,} rows each")
    warnings = []
    if counts["rows"] != counts["accounts"]:
        warnings.append("more rows than accounts — set COL_SNAPSHOT or de-duplicate")
    if cfg.DS_STRINGS_HAS_EXITED and counts["backtest_spine"] and not counts["backtest_now_8plus"]:
        warnings.append("no backtest account is at 8+ today — the table looks survivor-only; "
                        "outcomes would be biased. Point DS_STRINGS at a table that keeps exited "
                        "accounts, or set DS_STRINGS_HAS_EXITED = False")

    if check_only:
        ex = [r.dpd_string[:36] for r in sdf.where(is_cur).select("dpd_string").limit(5).collect()]
        print("=== DPD_STATES CHECK START ===")
        print(f"model_id: {model_id}")
        print(f"scope: {scope_note}")
        print(f"counts: {counts}")
        print(f"optional columns present: {present}")
        print(f"optional columns configured but missing: {absent}")
        print(f"example strings (no keys, newest first, 36 months): {ex}")
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
    R, report = run(cur_pd, bt_pd, cfg)
    checks = evaluate(R)

    payload = {
        "task": "DPD_STATES_VALIDATION",
        "run_date": datetime.date.today().isoformat(),
        "model_id": model_id,
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
    print(f"scope: {scope_note}")
    print(f"counts: {counts}")
    for w in warnings:
        print(f"WARNING: {w}")
    print(f"expectations: {n_status}")
    for r in checks.itertuples():
        print(f"  {r.id:<4} {r.status:<7} observed={r.observed!s:<8} expected={r.expected:<8} {r.check[:70]}")
    print(f"{RECOMMENDED} shares today: " + ", ".join(f"{DISPLAY_NAMES[s]}={v:.1%}" for s, v in rec.items()))
    print(f"wrote: {out} and {rep.name} -> commit & push from PROD, pull in UAT")
    print("=== DPD_STATES OUTPUT END ===")
    return payload
`````
