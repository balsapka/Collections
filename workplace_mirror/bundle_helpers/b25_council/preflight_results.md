# Bundle 25 preflight: results on the mirror (branch `feature/persona_refactor`)

These greps ran on the mirror checkout, not on the workplace repo. The hits are a baseline for what the mirror still
references outside the 29 files the bundle rewrites. They are not the workplace answer. Every line is at most 120
characters, so the tables are written as lists.

"Inside" means one of the 29 rewritten files. Only outside hits are listed.

## (a) Symbols: hits outside the rewritten files

Every hit outside the rewritten files is a test or a `tmp_validation` snippet, unless noted.

### Removed or renamed

- `lookback_floor`: referenced elsewhere.
  - `tmp_validation/a1_high_whatif/whatif_scenarios.py:31,138`
  - `tmp_validation/a1_high_whatif/whatif_signals.py:29,214`
- `PRODUCT_TYPES`: referenced elsewhere.
  - `src/tests/nodes/features/products/test_feat_cif_cross_product.py:84`
- `_window`: name clash only. Nothing imports `prm_products._window`.
  - `nodes/staging/dcore/stg_dcore_observation_spine.py:70,83`: unrelated local variable.
  - `pipelines/retail_loans/spine.py:78,84`: unrelated local variable.
  - `tmp_validation/persona_deck/state_relevance.py:896,1018,1024,1096`: defines its own `_window`.
- `_with_next_month`: referenced elsewhere.
  - `tmp_validation/a1_aecb_whatif/a1_aecb_whatif_snippet.py:137` patches it with `mock.patch.object`.
  - `tmp_validation/a1_bureau_fill/a1_bureau_fill_snippet.py:89` and `bf_states.py:55` do the same.
  - Mentioned in READMEs and results files under `tmp_validation/a1_aecb_whatif` and `a1_bureau_fill`.
  - Comment only: `nodes/features/casa/feat_cif_windows.py:92`, `tasks/bureau_salary_unified_handover.md:41`.
- `_cross_product_node`: 0 references outside.
- `__all__` (a1_ability): 0 references outside. The other `__all__` hits belong to other packages.
- `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`: referenced elsewhere.
  - `tmp_validation/a1_bureau_unified/a1_bureau_unified_snippet.py:62,63,145`
  - `tmp_validation/a1_payment_cure/a1_payment_cure_snippet.py:68,69` reads them through `getattr` with a fallback.
- `FLOW_FLOOR`, `FLOW_ANCHOR_MULT`, `BALANCE_FLOOR`, `BALANCE_ANCHOR_MULT`, `ASSET_FLOOR`, `ASSET_ANCHOR_MULT`,
  `MONEY_IN_SOME`, `MONEY_OUT_SOME`: 0 references outside.
- `_strong_months`, `_flow_level`: 0 references outside.
- `FOLLOWUP_RUN_DAYS`, `MATCH_DAYS`, `STATEMENT_FALLBACK_D`, `DEADLINES`: 0 references outside.
- `_followup_promises`, `_consolidate`: 0 references outside.
- `_cutoff`: referenced elsewhere.
  - `src/tests/pipelines/crx_persona/test_a3_promise_events.py:24,174,188`
- `_with_due`, `_with_paid`, `_with_paid_by`, `_event_starts`, `_run_step`, `_no_runs`: absent. 0 references anywhere,
  so they are already gone from the mirror.
- `pit_latest` (lost the `anchor=` keyword): callers need checking.
  - `pipelines/crx_persona/_dpd_journey/anchor.py:15,50`
  - `tmp_validation/a3_detail/a3_detail_snippet.py:44,278`
  - Not checked: whether either call passes `anchor=`.

### Moved

- `build_promise_events`, `EVENTS`: referenced elsewhere.
  - `src/tests/pipelines/crx_persona/test_a3_promise_events.py:25,149` (`build_promise_events`), `:23,159` (`EVENTS`)
  - `build_promise_events` is also imported in `tmp_validation/a3_detail/a3_detail_snippet.py:63`,
    `a3_v1h/a3_v1h_snippet.py:63` and `a3_v1i/a3_v1i_snippet.py:64`.
- `build_cc_acct_windows`: referenced only in docs and comments. No Python import outside the rewritten files.
  - `notebooks/data_engineering/crx_persona/docs/cc_raw_extract_pipeline_lineage_flow.md:17-19,55,80`
  - `conf/base/catalog/catalog_crx.yml:21` (comment)
- Parameter names `crx_cc_obs_base` and `crx_cc_a4_deterioration`: these are dataset names, not parameter names, so
  the rename breaks nothing.
- `CYCLE_MAX_DAYS`, `FLOOR_LOOKBACK_DAYS`, `BUCKET08_BASELINE_MONTHS`: 0 references outside.

### Changed signatures

- `build_income_signals`: callers outside use the old arguments, with no `crx_persona`.
  - `src/tests/pipelines/crx_persona/test_a1_ability.py:244,256,259`
  - `tmp_validation/a1_aecb_whatif/a1_aecb_whatif_snippet.py:138`
  - `tmp_validation/a1_bulk_pull/a1_bulk_pull_snippet.py:52,276`
- `build_distress_signals`: `tmp_validation/a1_casa_accounts/a1_casa_accounts_snippet.py:53,509` uses the old
  arguments.
- `build_eosb_signals`, `build_rl_liquidity_anchor`: 0 references outside.
- `build_contact_signals`: `tmp_validation/a3_detail/a3_detail_snippet.py:57,118`, `a3_v1h/a3_v1h_snippet.py:55,422`
  and `a3_v1i/a3_v1i_snippet.py:58,115`. Not checked: whether they pass `max_months=`.
- `max_months`: name clash only. `nodes/intermediate/retail_loans/int_loan_master.py` has an unrelated parameter.
- `promise_deadline`: callers use the two-argument form.
  - `src/tests/pipelines/crx_persona/test_a3_promise_events.py:17,179-182`
  - `tmp_validation/a3_detail/a3_detail_snippet.py:159`
  - `tmp_validation/a3_v1h/a3_v1h_snippet.py:51,394`
- `cross_product_level`: `src/tests/pipelines/crx_persona/test_a1_ability.py:143`.
- `_latest_in_month`: 0 references outside.
- `_events`: name clash only. The a3 `_events` is not in the mirror's a3 files. Unrelated functions with that name:
  - `nodes/features/location/feat_cif_location_monthly.py:77`
  - `tmp_validation/a1_bulk_pull/bp_analysis.py:345`
  - `tmp_validation/a1_casa_accounts/a1_casa_accounts_snippet.py:976`
  - `tmp_validation/a3_v1_v4/a3_v1_v4_snippet.py:1147`
- `_floor`, `persona_floor`, `history_floor`: no clash. 0 references outside and none inside. `history_floor_date`
  exists only as a parameter name (`_dpd_journey/params.py`, `cc_a3_payment_credibility/pipeline.py:21`).

### A3 log label

- `"A3 credibility"`: the only source use is `a3_credibility/classify.py:88`, which is inside the rewritten files.
  The only other hits are the `tmp_validation/a3_check_new/summary_*.md` files, which quote the log lines. No test or
  notebook asserts on it.

## (b) Dead packages and unread CASA features

- `_spine_utils.py`: no imports. It mentions `crx_cc_spell_table` and `crx_rl_a4_spine` in docstrings.
- `rl_a4_spine/`
  - registry: import `pipeline_registry.py:100`, entry `:251`
  - catalog: `catalog_crx.yml:302,325,327`
  - other: comment in `conf/base/parameters/parameters_crx_persona.yml:6`
- `rl_spell_table/`
  - registry: import `pipeline_registry.py:98`, entry `:250`
  - catalog: `catalog_crx.yml:314,325`
  - test: `src/tests/pipelines/crx_persona/test_rl_spell_table.py:23`
- `cc_spell/`
  - registry: import `pipeline_registry.py:75`, entry `:238`
  - other: comments in `cc_a4_deterioration/nodes.py:23` and `nodes/staging/cc_way4/stg_last_operation.py:58`
  - notebooks: `validate_a4_deterioration_class.ipynb:1226`, and the `t42_*` notebooks
- `crx_cc_spell_table`
  - catalog: `catalog_crx.yml:80`
  - node input: `cc_raw_extract/pipeline.py:47`, `cc_raw_extract/nodes.py:199-224`
  - test: `src/tests/pipelines/crx_persona/schema_registry.py:142`
  - docstrings only: `cc_departure_signature`, `cc_payment_trajectory`, `cc_utilisation`
- `crx_rl_spell_table`, `crx_rl_a4_spine`: catalog and registry only, as above.
- `build_cc_limits`
  - `cc_raw_extract/pipeline.py:18,46`
  - tests: `test_cc_raw_extract_nodes.py:18,180,192,203` and `test_crx_persona.py:15,63-72`
- `crx_cc_limits`
  - catalog: `catalog_crx.yml:36`
  - `cc_raw_extract/pipeline.py:48-49`
  - test: `src/tests/pipelines/crx_persona/schema_registry.py:135`
- `raw_stg_limit`
  - catalog: `conf/base/catalog/catalog_raw_way4.yml:20`
  - input of `cc_raw_extract/pipeline.py:47`. No other node reads it.
  - schema-intelligence JSON under `data/08_reporting/`, and about 14 md/tmp files.
- `feat_cif_casa_activity_monthly`: **0 readers.** It is written by `pipelines/casa/features.py:55-56` and has a
  catalog entry at `catalog_casa.yml:232`. Mentioned in `nodes/features/casa/feat_cif_casa.py:11` and 14 md/tmp files.
- `feat_cif_ext_card_payment_monthly`: **0 readers.** It is written by `pipelines/casa/features.py:66-67` and has a
  catalog entry at `catalog_casa.yml:255`. Mentioned in `feat_cif_casa.py:12` and 1 md file.

Deleting `crx_cc_spell_table` and `build_cc_limits` also requires removing `raw_stg_limit` from
`cc_raw_extract/pipeline.py`, two registry blocks, three test files and `schema_registry.py`.

## (c) Catalog and registry

### Top-level keys of `conf/base/catalog/catalog_crx.yml`, in file order

CC extract, spell and A4:

- 22 `crx_cc_acct_windows`
- 29 `crx_cc_transactions`
- 36 `crx_cc_limits`
- 48 `crx_cc_balance`
- 57 `crx_cc_billing`
- 68 `crx_cc_full_history`
- 80 `crx_cc_spell_table`
- 97 `crx_cc_dpd_sequences`
- 108 `crx_cc_a4_deterioration`

CC A2 and obs_base:

- 123 `crx_cc_a2_location_signals`
- 130 `crx_cc_a2_dcore_signals`
- 137 `crx_cc_a2_way4_deceased`
- 144 `crx_cc_a2_demographics_deceased`
- 151 `crx_cc_a2_locatability`
- 159 `crx_cc_obs_base`
- 166 `crx_rl_obs_base`

CC A1:

- 178 `crx_cc_a1_income_signals`
- 185 `crx_cc_a1_casa_signals`
- 192 `crx_cc_a1_cross_product_signals`
- 199 `crx_cc_a1_distress_signals`
- 206 `crx_cc_a1_eosb_signals`
- 213 `crx_cc_a1_liquidity_anchor`
- 220 `crx_cc_a1_ability`

CC A3:

- 235 `crx_cc_a3_commitment_signals`
- 242 `crx_cc_a3_payment_cycles`
- 249 `crx_cc_a3_dlq_payment_signals_single_payment_cycle_count`
- 256 `crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count`
- 263 `crx_cc_a3_strong_negative_signals`
- 270 `crx_cc_a3_episode`
- 277 `crx_cc_a3_instalments`
- 284 `crx_cc_a3_promise_events`
- 291 `crx_cc_a3_payment_credibility`

RL Foundation, spell and A4:

- 303 `crx_rl_full_history`
- 314 `crx_rl_spell_table`
- 327 `crx_rl_a4_spine`
- 342 `crx_rl_dpd_sequences`
- 353 `crx_rl_a4_deterioration`
- 361 `crx_rl_full_history_linked`
- 369 `crx_rl_restructure_chains`
- 377 `crx_rl_dpd_sequences_linked`

RL A1:

- 389 `crx_rl_a1_income_signals`
- 396 `crx_rl_a1_casa_signals`
- 403 `crx_rl_a1_cross_product_signals`
- 410 `crx_rl_a1_distress_signals`
- 417 `crx_rl_a1_eosb_signals`
- 424 `crx_rl_a1_liquidity_anchor`
- 431 `crx_rl_a1_ability`

RL A2:

- 446 `crx_rl_a2_location_signals`
- 453 `crx_rl_a2_dcore_signals`
- 460 `crx_rl_a2_way4_deceased`
- 467 `crx_rl_a2_demographics_deceased`
- 474 `crx_rl_a2_locatability`

RL A3:

- 483 `crx_rl_a3_commitment_signals`
- 490 `crx_rl_a3_dlq_cycles`
- 497 `crx_rl_a3_dlq_payment_signals_single_payment_cycle_count`
- 504 `crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count`
- 511 `crx_rl_a3_strong_negative_signals`
- 518 `crx_rl_a3_episode`
- 525 `crx_rl_a3_instalments`
- 532 `crx_rl_a3_promise_events`
- 539 `crx_rl_a3_payment_credibility`

### `a3` entries

All 18 entries have the same body, with the key name substituted into `filepath`. The keys are the A3 keys listed
above. No other file in `conf/`, including `conf/dev` and `conf/local`, contains `a3`, apart from the parameter below.

```yaml
<key>:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<key>"
  save_args:
    mode: overwrite
```

Comments in the file:

- Lines 227-233, above `crx_cc_a3_commitment_signals`:
  - `# — CC A3 Payment Credibility (shared a3_credibility engine) —`
  - `# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).`
  - `# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,`
  - `#             payment_credibility_low, payment_credibility_unknown}.`
  - `# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE plan`
  - `# instalments; crx_cc_a3_promise_events: the promise events judged by payment.`
  - `# Spec: workplace_mirror/specs/A3_credibility_spec.md.`
- Lines 481-482, above `crx_rl_a3_commitment_signals`:
  - `# — RL A3 Payment Credibility (shared a3_credibility engine) —`
  - `# Grain and states as CC (crx_rl_obs_base).`
- Line 46, inside the `crx_cc_limits` block: a comment that mentions `resolve_due_amount_m`. It is not an `a3` entry.

Parameter: `conf/base/parameters/parameters_crx_persona.yml:30` has `cc_a3_history_floor_date: "2024-01-01"`.

### `a3_dues` / `a3_payments` keys

None exist in `conf/`. There are 0 matches for `crx_cc_a3_dues`, `crx_rl_a3_dues`, `crx_cc_a3_payments` and
`crx_rl_a3_payments`.

### Registry lines mentioning `a3`, in `src/enbd_collections/pipeline_registry.py`

- `:94` `cc_a3_payment_credibility as crx_cc_a3_payment_credibility,`
- `:109` `rl_a3_payment_credibility as crx_rl_a3_payment_credibility,`
- `:246-247` `"crx_cc_a3_payment_credibility": ( crx_cc_a3_payment_credibility.create_pipeline() )`
- `:255-256` the same for `rl`.

There is no registry entry for `a3_credibility` itself.

## (d) Surprises

- **The mirror may already contain part of the bundle.** `cc_a3_payment_credibility/pipeline.py:17-31` and
  `rl_a3_payment_credibility/pipeline.py:17-27` already define the `build_cc_a3_dues`, `build_cc_a3_payments`,
  `build_rl_a3_dues` and `build_rl_a3_payments` nodes. They output `crx_<p>_a3_dues` and `crx_<p>_a3_payments`,
  which have no catalog entries, so Kedro would hold them as memory datasets. The `build_cc_a3_dues` signature in
  `nodes.py` already takes `history_floor_date`. The bundle may need to add the catalog entries in the right place.
  Not checked: how far the mirror's `promises.py` and `sources.py` already match the bundle.
- **Old-signature callers are mainly in `tmp_validation`:** the `a1_*` and `a3_*` snippets, plus `whatif_*.py`, which
  import `lookback_floor`. The tests that will break are `test_a1_ability.py`, `test_a3_promise_events.py` (it
  imports `_cutoff`, `promise_deadline` and `EVENTS`) and `test_feat_cif_cross_product.py`. These files are in the
  mirror, so they may be the same in the workplace.
- **Spell-table dependency chain:** the dead-package deletion also touches `cc_raw_extract` (`build_cc_limits` and
  `build_cc_acct_windows`, which reads `crx_cc_spell_table`), `schema_registry.py` and three test files. The bundle
  moves `build_cc_acct_windows` to take `obs_base` and `deterioration`, so check that no other node still depends on
  the spell table.
- **Unverified items:** the `pit_latest(anchor=)` callers, the `build_contact_signals(max_months=)` callers, and the
  exact old-versus-new signature of `a3_credibility/signals.py`.
