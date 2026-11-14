# Gates baseline (run 2)

Input commit `ec0c329`, worktree `.worktrees/council_a1_a3`, run 2026-11-14 from
`workplace_mirror/` on a MacBook (Python 3.13.11, PySpark 3.5.3, Kedro 1.7.0, Java 17,
`local[2]`, 2 GB driver, one Spark job at a time). Tools: black 26.10.1, ruff 0.17.2,
pylint 4.1.3. Installed for this run: `pyarrow` (only to inspect golden parquet; no gate
needs it). Source and config untouched; failures are recorded, not fixed.

| # | Gate (PLAN §6) | Result | Time | Numbers |
|---|---|---|---|---|
| 1 | `py_compile` | **pass** | <1 s | 53 files of tiers L, S, A, D?, K |
| 2a | `black --check -l 88` | **pass** | <1 s | L 34, S 3, A 3, D? 9, K 4 files unchanged |
| 2b | `ruff check --select F,E,W,I,B,SIM,UP` | **101 findings (baseline)** | <1 s | L 48 (37 E501, 10 F401 in `a3_credibility/__init__.py` — re-exports without `__all__`, 1 I001 `prm_products.py:20`); S 6 (5 E501, 1 UP035 `_common.py:23`); A 36 E501; D? 9 E501; K 2 (1 E501, 1 I001 `cc_raw_extract/nodes.py:21`) |
| 2c | `PYTHONPATH=src pylint --disable=relative-beyond-top-level` | **baseline below** | 26 s (with metrics) | line-weighted L 9.48, S 10.0, A 10.0, D? 10.0, K 7.99; four files below 10, all from unmirrored imports (see table) |
| 3 | spec tests | **pass** | A1 54 s, A3 119 s, A2 24 s, A4 20 s | A1 90/90 cases (+ dating, lanes, anchor, returns, Scorecard); A3 all checks; A2 36/36; A4 chain all checks |
| 4 | `python checks/refactor_golden.py` | **pass** | 157 s (record 146 s) | 188 datasets in 23 runs, 0 differences; 7 guards raise; 0 coverage gaps (see below) |
| 5 | `python checks/refactor_smoke.py` | **FAIL, 6 failures (baseline)** | 0.4 s | 106 modules imported, 23 pipelines checked; one root cause, below |
| 6 | grep rules | **pass** | <1 s | no `spark.read`; no hard-coded model_id; 34 `node(` calls in tiers L–K, all with the five keywords; actions and `raw_` inputs as listed below (baseline, none new) |

## Gate 2c: pylint per file (tiers L, S, A, D?, K)

No file may fall below its score here. The four files under 10 lose points only to
`E0401` / `E0611` on workplace modules the mirror lacks (`prm_cc`, `_feat_dcore_utils`,
`config_dcore`, `config.EDP_LOAD_DATE_BUFFER_MONTHS`); `a3_credibility/sources.py` also
has two `C0411` (pyspark imports after the first-party ones, lines 11–12).

| File | Tier | Pylint | Ruff findings |
|---|---|---|---|
| `nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` | L | 10.0 | 0 |
| `nodes/features/bureau/feat_cif_bureau_salary_monthly.py` | L | 10.0 | 2 |
| `nodes/features/products/__init__.py` | L | — (empty) | 0 |
| `nodes/features/products/feat_cif_cross_product.py` | L | 10.0 | 9 |
| `nodes/primary/products/__init__.py` | L | — (empty) | 0 |
| `nodes/primary/products/prm_products.py` | L | 7.37 | 8 |
| `nodes/utils/frames.py` | L | 10.0 | 0 |
| `pipelines/bureau/salary_bounces.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/a1_ability/__init__.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/a1_ability/classify.py` | L | 10.0 | 2 |
| `pipelines/crx_persona/a1_ability/pipeline.py` | L | 10.0 | 1 |
| `pipelines/crx_persona/a1_ability/signals.py` | L | 10.0 | 7 |
| `pipelines/crx_persona/a3_credibility/__init__.py` | L | 10.0 | 10 |
| `pipelines/crx_persona/a3_credibility/classify.py` | L | 10.0 | 1 |
| `pipelines/crx_persona/a3_credibility/constants.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/a3_credibility/pipeline.py` | L | 10.0 | 4 |
| `pipelines/crx_persona/a3_credibility/signals.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/a3_credibility/sources.py` | L | 6.86 | 1 |
| `pipelines/crx_persona/cc_a1_ability/__init__.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/cc_a1_ability/nodes.py` | L | 10.0 | 1 |
| `pipelines/crx_persona/cc_a1_ability/pipeline.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/cc_a3_payment_credibility/__init__.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/cc_a3_payment_credibility/nodes.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/rl_a1_ability/__init__.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/rl_a1_ability/nodes.py` | L | 10.0 | 1 |
| `pipelines/crx_persona/rl_a1_ability/pipeline.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/rl_a3_payment_credibility/__init__.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/rl_a3_payment_credibility/nodes.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/scoring_engine.py` | L | 10.0 | 0 |
| `pipelines/products/__init__.py` | L | — (empty) | 0 |
| `pipelines/products/features.py` | L | 10.0 | 1 |
| `pipelines/products/primary.py` | L | 10.0 | 0 |
| `pipelines/crx_persona/_common.py` | S | 10.0 | 3 |
| `pipelines/crx_persona/_dcore_codes.py` | S | 10.0 | 3 |
| `pipelines/crx_persona/_dpd_journey/anchor.py` | S | 10.0 | 0 |
| `nodes/features/casa/feat_cif_casa.py` | A | 10.0 | 22 |
| `nodes/features/casa/feat_cif_casa_flow.py` | A | 10.0 | 9 |
| `pipelines/casa/features.py` | A | 10.0 | 5 |
| `pipelines/crx_persona/_spine_utils.py` | D | 10.0 | 0 |
| `pipelines/crx_persona/cc_spell/nodes.py` | D | 10.0 | 4 |
| `pipelines/crx_persona/cc_spell/pipeline.py` | D | 10.0 | 1 |
| `pipelines/crx_persona/rl_a4_spine/__init__.py` | D | 10.0 | 0 |
| `pipelines/crx_persona/rl_a4_spine/nodes.py` | D | 10.0 | 1 |
| `pipelines/crx_persona/rl_a4_spine/pipeline.py` | D | 10.0 | 0 |
| `pipelines/crx_persona/rl_spell_table/__init__.py` | D | 10.0 | 0 |
| `pipelines/crx_persona/rl_spell_table/nodes.py` | D | 10.0 | 3 |
| `pipelines/crx_persona/rl_spell_table/pipeline.py` | D | 10.0 | 0 |
| `pipelines/crx_persona/cc_raw_extract/__init__.py` | K | 10.0 | 0 |
| `pipelines/crx_persona/cc_raw_extract/_window_utils.py` | K | 5.45 | 0 |
| `pipelines/crx_persona/cc_raw_extract/nodes.py` | K | 7.92 | 2 |
| `pipelines/crx_persona/cc_raw_extract/pipeline.py` | K | 10.0 | 0 |

## Gate 4: the oracle

- 23 runs: A1, A3, A2, A4 for each of the four model_ids (A3 CC = obs base +
  `crx_cc_raw_extract` + A3, so tier K is in the oracle), the A4 `dpd_journey` alt runs
  (CC, RL), A3 with the other promise deadlines (CC `30_days` with the history floor moved
  to 2025-06-01; RL `next_month_end` and `30_days_month_end`), `product_primary` +
  `product_features`, `bureau_salary_bounces`. Per-run times are in `harness_coverage.md`.
- Guards that must raise (all `ValueError`): mid-month RL spine; `prm_balance` without
  `overdue_bucket_06`; unknown `dpd_journey` key; unknown promise deadline;
  `int_loan_master` without `total_paid` (RL A3); `feat_bureau_salary_unified` without
  `salary_source`; loan portfolio without `ra_woff_dt`.
- Coverage: every listed value of every state column is reached (A1 states, reasons,
  four family levels incl. NULL, points 0/2/4/6, distress, sweepable, EOSB, income source,
  salary stopped, anchor NULL/value; A3 states, the three dimension levels, every
  disposition and contact flag, refusal override, Unknown `no_episode`, censored and
  uncropped episodes, points -1..5, all five deadlines; promise events matched /
  table_only / followup_only, ptp / settlement / followup, paid / partial / none; products
  all five types and is_current 0/1/NULL; all A2 and A4 states and rule counters), and all
  10 probes (D-A3-29 split, 31-day fallback, event outside the window, refusal demotion,
  bucket-08 due baseline, RL EMI carry, post-block fee, open last cycle, limits, bounce
  dedupe). Not covered: `harness_coverage.md`, section "Not covered".
- Sensitivity: replacing one golden row (RL A3, account 101, state changed) makes the
  default mode fail naming the dataset and both rows (`1 new only` / `1 golden only`);
  restoring it passes again.
- Harness choices reviewers should know: each node output is `localCheckpoint`ed when
  saved (the whole lazy plan of raw extract + A3 drove the 2 GB driver into GC thrash; the
  rows are the same); the process and Spark time zone are UTC (naive input datetimes); the
  Kedro `partial` warning is silenced.

## Gate 5: smoke failures (exact)

```
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract: cannot import name 'EDP_LOAD_DATE_BUFFER_MONTHS' from 'enbd_collections.nodes.utils.config'
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils: (same)
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract.nodes: (same)
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract.pipeline: (same)
FAIL crx_cc_raw_extract: empty pipeline
FAIL mirrored module stubbed: enbd_collections.pipelines.crx_persona.cc_raw_extract
smoke: FAIL (6 failures)
```

One cause: the mirror's `nodes/utils/config.py` predates `EDP_LOAD_DATE_BUFFER_MONTHS`
(inventory C5). A later run passes gate 5 when it shows exactly these six lines. Listed, not
failed: 14 node outputs that are MemoryDatasets in the mirror (the A3 ledger / signal names of
the workplace catalog, `stg_digital_login`, `prm_digital_login_monthly`), 36 free inputs from
catalogs the mirror lacks, 72 stubbed workplace modules or names. Every `params:` key resolves.
Run 1's baseline failure (`crx_cc_billing` not in the catalog) is gone (`5b2c0d2`).

## Gate 6: grep baseline (tiers L–K)

- Spark actions (`.count/.collect/.first`, not `F.` aggregates): `_common.py:171`
  (`lookback_floor`), `:206` (`log_latest_month`), `:246` (mid-month guard);
  `a1_ability/signals.py:328` (returns-coverage guard); `cc_raw_extract/_window_utils.py:29`;
  D?: `cc_spell/nodes.py:231`, `rl_a4_spine/nodes.py:72-73`, `rl_spell_table/nodes.py:341-347`.
- `raw_` inputs: `pipelines/products/primary.py` (`raw_stg_client`, `raw_stg_contract`,
  `raw_stg_billing`, `raw_stg_balance`, `raw_stg_account_group`: a primary node, allowed),
  `cc_raw_extract/pipeline.py` (K), `cc_spell/pipeline.py` (D?). No `stg_` / `raw_` input in a
  persona axis or feature node.

## Check scripts

`checks/refactor_golden.py`, `checks/golden_inputs.py`, `checks/refactor_smoke.py`,
`checks/refactor_metrics.py`: black and ruff clean; pylint 9.75 (missing docstrings on small
helpers).
