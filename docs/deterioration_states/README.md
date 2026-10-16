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
