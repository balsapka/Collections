# Round 1 gates (merge, step b)

Run from `workplace_mirror/` after each stage, one Spark job at a time (`JAVA_HOME=/opt/homebrew/opt/openjdk@17`,
same machine and tools as `00_baseline/gates_baseline.md`). Lint gates on every `.py` file changed vs `d24114a`;
ruff counts compare each file with its own `d24114a` copy.

## Summary

| Gate | S7 B | S1 | S3 | S2 | S4 (final) |
|---|---|---|---|---|---|
| a. py_compile | pass (3 files) | pass (21) | pass (22) | pass (22) | pass (25) |
| a. black -l 88 (src) | pass | pass | pass | pass | pass |
| a. ruff F,E,W,I,B,SIM,UP | no new finding in src | no new in src; `checks/a1_engine_spec.py` 114 → 115 (see note 1) | no new | no new | no new; 51 → 36 on the changed src files |
| a. pylint ≥ baseline | pass | **2 files below baseline score with unchanged messages** (note 2) | same 2 | 3 (+ `prm_products.py`) | same 3; S4-04 reverted (new R0914) |
| b. A1 spec | 90/90, 27 s | 90/90, 25 s | 90/90, 26 s | 90/90, 25 s | 90/90, 24 s |
| b. A3 spec | all checks pass, 61 s | pass, 49 s | pass, 49 s | pass, 42 s | pass, 38 s |
| b. A2 spec | 36/36, 14 s | 36/36, 14 s | 36/36, 15 s | 36/36, 14 s | 36/36, 14 s |
| b. A4 chain spec | pass, 12 s | pass, 12 s | pass, 13 s | pass, 13 s | pass, 12 s |
| c. oracle | **pass**, 188 datasets, 171 s | pass, 188, 155 s | pass, 188, 151 s | pass, 188, 162 s | pass, 188, 147 s |
| d. smoke | exactly the 6 baseline lines | same 6 | same 6 | same 6 | same 6 |
| e. grep rules | pass | pass | pass | pass | pass |

A2 / A4 spec tests ran at every stage (`_common.py`, `frames.py`, `prm_products.py` or `cc_raw_extract` changed in
each). The oracle was never run with `--record`; `refactor_golden.py` and `golden_inputs.py` are unchanged. The only
check-script edit is S1-01's `checks/a1_engine_spec.py` call sites (new `crx_persona=PERSONA` arguments), as its
diff wrote them.

## Gate a: per file at the final tree (ruff `d24114a` → now, pylint baseline → now)

| File | Ruff | Pylint |
|---|---|---|
| `nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` | 0 → 0 | 10.0 → 10.0 |
| `nodes/features/products/feat_cif_cross_product.py` | 9 → 9 | 10.0 → 10.0 |
| `nodes/primary/products/prm_products.py` | 8 → 7 | 7.37 → **7.22** (note 2) |
| `nodes/utils/frames.py` | 0 → 0 | 10.0 → 10.0 |
| `pipelines/bureau/salary_bounces.py` | 0 → 0 | 10.0 → 10.0 |
| `pipelines/crx_persona/_common.py` | 3 → 2 | 10.0 → 10.0 |
| `a1_ability/__init__.py` | 0 → 0 | 10.0 → 10.0 |
| `a1_ability/classify.py` | 2 → 2 | 10.0 → 10.0 |
| `a1_ability/pipeline.py` | 1 → 1 | 10.0 → 10.0 |
| `a1_ability/signals.py` | 7 → 6 | 10.0 → 10.0 |
| `a3_credibility/__init__.py` | 10 → 0 | 10.0 → 10.0 |
| `a3_credibility/classify.py` | 1 → 1 | 10.0 → 10.0 |
| `a3_credibility/constants.py` | 0 → 0 | 10.0 → 10.0 |
| `a3_credibility/pipeline.py` | 4 → 4 | 10.0 → 10.0 (S4-04 reverted) |
| `a3_credibility/promises.py` (new) | — → 0 | — → 10.0 |
| `a3_credibility/signals.py` | 0 → 0 | 10.0 → 10.0 |
| `a3_credibility/sources.py` | 1 → 1 | 6.86 → **3.89** (note 2) |
| `cc_a1_ability/nodes.py` | 1 → 0 | 10.0 → 10.0 |
| `cc_a3_payment_credibility/nodes.py` | 0 → 0 | 10.0 → 10.0 |
| `cc_raw_extract/nodes.py` | 2 → 2 | 7.92 → **7.87** (note 2) |
| `cc_raw_extract/pipeline.py` | 0 → 0 | 10.0 → 10.0 |
| `rl_a1_ability/nodes.py` | 1 → 0 | 10.0 → 10.0 |
| `rl_a1_ability/pipeline.py` | 0 → 0 | 10.0 → 10.0 |
| `products/features.py` | 1 → 1 | 10.0 → 10.0 |
| `checks/a1_engine_spec.py` | 114 → 115 | 5.97 → 7.02 |

Notes:

1. `checks/a1_engine_spec.py` is a check script that was never black / ruff clean (black would reformat the
   `d24114a` copy; 114 findings). S1-01's call-site edit adds one E501. Not reformatted (that would rewrite
   the whole script).
2. **For the Master: three files score below their baseline with exactly the baseline messages.** Each one
   loses points only to `E0401` / `E0611` on modules the mirror lacks (`_feat_dcore_utils`, `config_dcore`,
   `prm_cc`) plus, for `sources.py`, the two baseline `C0411`. Pylint divides the same penalty by fewer
   statements: `a3_credibility/sources.py` went from 372 to 198 lines when S1-04 moved the promise rule to
   `promises.py` (S1: 2.41, rising to 3.89 as S3/S4 added statements), `cc_raw_extract/nodes.py` lost
   `build_cc_acct_windows` (S1-05: 7.62, then 7.87 after S3-04), `prm_products.py` lost the window
   statements (S2-10: 7.22). No new message in any of them. Not reverted: reverting S1-04 / S1-05 / S2-10
   would not remove a defect, only restore the dilution. The rule may want "no new message" for files whose
   only messages are unmirrored imports.
3. S4-04 (`a3_credibility/pipeline.py`) added a real message, `R0914 too-many-locals (20/15)` on
   `create_a3_pipeline` (10.00 → 9.55); the proposal's own diff gives the same on `d24114a`. Reverted; the
   gates above were run after the revert.

## Gate d: smoke (every stage, identical)

```
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract: cannot import name 'EDP_LOAD_DATE_BUFFER_MONTHS' from 'enbd_collections.nodes.utils.config'
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils: (same)
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract.nodes: (same)
FAIL import enbd_collections.pipelines.crx_persona.cc_raw_extract.pipeline: (same)
FAIL crx_cc_raw_extract: empty pipeline
FAIL mirrored module stubbed: enbd_collections.pipelines.crx_persona.cc_raw_extract
smoke: FAIL (6 failures)
```

S1-05 moved `build_cc_acct_windows` into `cc_a3_payment_credibility/nodes.py`, which imports in the mirror;
`cc_raw_extract/pipeline.py` now imports it from there. The set of failing modules did not change (the four
`cc_raw_extract` modules still fail on `config.EDP_LOAD_DATE_BUFFER_MONTHS`). S3-04 adds an import of
`_common.require_columns` to `cc_raw_extract/nodes.py`: no cycle, same failures.

## Gate e: grep rules (lines added vs `d24114a`, src + conf)

- `spark.read`: 0 added. Hard-coded model_id: 0 added.
- Spark actions: 0 added, 1 removed (`lookback_floor`'s `.first()`, S1-01).
- `node(` calls in changed files: 16, all with `func=, inputs=, outputs=, name=, tags=`.
- `raw_` / `stg_`: 8 added lines match, none a new input: 5 are S3-09's dict re-statement of the existing
  `cc_raw_extract` inputs (`raw_transaction`, `raw_stg_limit`, `raw_stg_balance`, `raw_stg_account_group`,
  `raw_stg_billing`), 3 are S3-04's `require_columns` source names. No persona or feature node gained a raw input.
- No `conf/` file, `pipeline_registry.py`, tier A file or `_dcore_codes.py` changed.

## For the test owner: renamed / removed / added functions and changed signatures

Paths under `src/enbd_collections/`.

Removed
- `pipelines/crx_persona/_common.py`: `lookback_floor(base, months)` (S1-01)
- `nodes/features/products/feat_cif_cross_product.py`: `PRODUCT_TYPES` (B-01)
- `nodes/primary/products/prm_products.py`: `_window(persona_start_date, history_months)` → `_load_bound(floor)` (S4-10)
- `pipelines/crx_persona/a1_ability/signals.py`: `_with_next_month(bureau)` → `_with_carry(bureau)` + `BUREAU_CARRY_MONTHS` (S1-06)
- `pipelines/products/features.py`: `_cross_product_node(output)` (S1-08)
- `pipelines/crx_persona/a1_ability/__init__.py`: `__all__` (S4-05; same names still importable)

Moved
- `a3_credibility/sources.py` → `a3_credibility/promises.py`: `build_promise_events`, `EVENTS`, `_followup_promises`, `_consolidate`, `_cutoff` (S1-04). `from ...a3_credibility import build_promise_events` still works; a test importing it from `.sources` must import from `.promises`.
- `cc_raw_extract/nodes.py` → `cc_a3_payment_credibility/nodes.py`: `build_cc_acct_windows`, parameters renamed `crx_cc_obs_base` → `obs_base`, `crx_cc_a4_deterioration` → `deterioration` (S1-05; node name, dataset and pipeline unchanged)
- `a3_credibility/constants.py` → `cc_a3_payment_credibility/nodes.py`: `CYCLE_MAX_DAYS`, `FLOOR_LOOKBACK_DAYS`, `BUCKET08_BASELINE_MONTHS` (S1-05)

Changed signatures
- `_common.pit_latest`: `anchor=` removed (B-02)
- `a1_ability.signals.build_income_signals`, `build_distress_signals`, `build_eosb_signals`: new keyword-only `crx_persona: dict` (node input `params:crx_persona`) (S1-01)
- `rl_a1_ability.nodes.build_rl_liquidity_anchor(obs_base, int_loan_master, crx_persona)` (S1-01)
- `a3_credibility.signals.build_contact_signals`: `max_months=` removed (B-03)
- `a3_credibility.constants.promise_deadline(product, model_id, override=None)` (S1-03)
- `a1_ability.classify.cross_product_level(anchor, _w)` (parameter renamed, positional callers unchanged) (S4-07)
- `prm_products._latest_in_month(df, key, day, value)` (S2-10)

Added
- `nodes/utils/frames.py`: `history_floor(persona_start_date, months)` (S1-01)
- `a1_ability/signals.py`: `_floor`, `_with_carry`, `BUREAU_CARRY_MONTHS`; `a1_ability/classify.py`: `_income_source`, `_salary_stopped`
- `a3_credibility/constants.py`: `HISTORY_MONTHS`; `a3_credibility/sources.py`: `EPISODE`, `CYCLE_LEDGER`, `INSTALMENTS`, `_INSTALMENT_FIELDS`, `_require_plan_sources`, `_plan_instalments`
- `a3_credibility/promises.py`: `_run_step`, `_no_runs`, `_with_due`, `_with_paid`
- `a3_credibility/signals.py`: `_commitment_counts`, `_contact_events`, `_contact_summary`, `_plan_after_refusal`
- `cc_a3_payment_credibility/nodes.py`: `_history_floor`
- `feat_cif_cross_product.py`: `ASSET_TYPES`, `CREDIT_TYPES`

New failure points (missing columns now raise `ValueError` naming the table): A3 `build_commitment_signals`,
`build_dlq_payment_signals`, `build_pre_dlq_payment_signals`, `build_contact_signals`, `build_promise_events`
(S3-02); `cc_raw_extract` `build_cc_transactions`, `build_cc_balance`, `build_cc_billing` and the
`crx_cc_acct_windows` input (S3-04). Pipeline wiring: `crx_cc_raw_extract` nodes take dict inputs (S3-09); the
A1 income / distress / EOSB nodes and the RL anchor node take `params:crx_persona` (S1-01).
