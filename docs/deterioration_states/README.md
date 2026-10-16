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
