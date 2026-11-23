# Mirror bundle 31 — UC1 stated block on UC1's signal export (July month end, two flags)

apply_bundle version: 7 · built 2026-11-23 from `d828d20..a2aaf31` · source: 2 added, 8 replaced, 1 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/uc1_signal_export
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/31_uc1_signal_export.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '31_uc1_signal_export.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/31_uc1_signal_export.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go, and fix what it finds before committing:

1. **Catalog and registry.** List every top-level key the apply added or removed in `conf/base/catalog/catalog_crx.yml` and `src/enbd_collections/pipeline_registry.py` compared with the last commit. Expected: catalog adds `crx_uc1_customer_signal_export`, removes nothing (`crx_uc1_metadata` only moved up); registry adds the `b31_check` import and `crx_cc_b31_snapshot`, `crx_rl_b31_snapshot`, `crx_cc_b31_compare`, `crx_rl_b31_compare`. Put back anything else that went missing (compare with the last commit), and make sure no key appears twice across `conf/base/catalog/*.yml` (`catalog_tmp_uc1_cov.yml` must be gone; `catalog_tmp_uc1_full.yml` stays, its keys are `crx_uc1_full_*`).
2. **Parameters.** `parameters_crx_persona.yml` has `uc1_month_end: "2026-07-31"` and everything it had before.
3. **Tests.** Update the crx_persona tests of `uc1_stated` to the new inputs and columns (the module docstrings and `checks/uc1_stated_spec.py` in the bundle describe the rules); delete tests of removed functions. The crx_persona tests pass.
4. `kedro registry list` shows the four `*_b31_*` pipelines; `python -c "import enbd_collections.pipeline_registry"` imports; black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Mirror bundle 31: UC1 stated block on UC1's signal export (July month end, two flags)" && git push -u origin feature/uc1_signal_export
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/31_uc1_signal_export.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/uc1_signal_export && git pull
```

**Step 7.** In PROD, after the pull, for each model_id (`cc_60_180`, `rl_60_180`, then `cc_180_plus`, `rl_180_plus`; switch `model_id` in `globals_dev.yml`), with `<p>` = cc or rl:

```bash
kedro run --pipeline=crx_<p>_b31_snapshot
```

```bash
kedro run --pipeline=crx_<p>_uc1_stated
```

```bash
kedro run --pipeline=crx_<p>_b31_compare
```

The snapshot must run before the new block overwrites the old one. A1 and A3 outputs are read as persisted (no rerun needed). Paste back the four blocks `=== B31 ROWS / B31 DIST / B31 OLD NEW / B31 PAID … START/END ===` per model_id (180+: ROWS and DIST are enough if UC1 has no 180+ customers). Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Rebuilds the UC1 stated block on UC1's official customer table, `customer_signal_export`, read as it is (user and manager decision, 2026-11-23). **Apply on top of bundles 25–30 and their cleanups.** Only `crx_<p>_uc1_stated` and `crx_<p>_uc1_conversation_signals` change.

- **State value = UC1's `estimated_value`** per signal (call transcripts and agent remarks, as UC1 weighs them). A5 stated ability from `payment_capacity`, A6 stated intent from `payment_intent`; mapping unchanged. A tie (`a|b`) takes the more cautious level; the raw value stays in `a5_capacity_level` / `a6_intent_level`. `not-detected` → `not_stated`; a customer not in UC1's table → `no_evidence`, with `uc1_evidence` = no_cif / no_conversation / not_extracted from the call metadata.
- **Scored month = new parameter `uc1_month_end`** (`parameters_crx_persona.yml`, set to `2026-07-31`: the last UC1 call is 2026-07-16; `null` = `crx_persona.persona_end_date`). Other months stay NULL, as before.
- **UC1's details passed through:** confidence, latest transcript value and latest remark value for A5 / A6; `supporting_data` for capacity; reason (+ confidence), period, dispute, request, fraudulent customer; amount / date / plan mentioned flags; `uc1_snapshot_date`.
- **Two new flags:** `stated_promise_unlogged_flag` (pays in full or partly / later, an amount or a date mentioned, and no A3 promise event of the customer's accounts alive within ±7 days of the last UC1 call; NULL when there is no dated call) and `verify_stated_ability_flag` (able or pays in full while `a1_state` = low). The pipeline now also reads `crx_<p>_a1_ability` and `crx_<p>_a3_promise_events`, so it runs after A1 and A3.
- **No longer read by the pipeline:** `simple_signal_aggregation`, `signal_level_conflicts`, `extracted_signals` (catalog entries kept for the UC1 validation snippets). Columns gone: the agree / conversation counts per axis, `uc1_extracted_n`, `uc1_last_extracted_date`, `uc1_after_obs_flag`.
- **Catalog:** new `crx_uc1_customer_signal_export`; `catalog_tmp_uc1_cov.yml` (quick-check entries, same key) deleted.
- **Temporary check** `b31_check.py` + `catalog_tmp_b31_check.yml` + 4 registry lines: snapshot of the old block, then distributions, old × new and paid_due over the next month at July end by state and flag.

Tested in the mirror: spec test `checks/uc1_stated_spec.py` (11 cases, month fallback, unknown level stops the run, catalog); golden harness unchanged (185 datasets); smoke check (the 6 known `cc_raw_extract` lines plus the two temporary check inputs from `catalog_tmp_b31_check.yml`); black, ruff and pylint clean on the touched files.

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
| replace | `conf/base/catalog/catalog_crx.yml` |
| add | `conf/base/catalog/catalog_tmp_b31_check.yml` |
| replace | `conf/base/parameters/parameters_crx_persona.yml` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/crx_persona/b31_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_uc1_stated/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_uc1_stated/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/uc1_stated/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/uc1_stated/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/uc1_stated/signals.py` |
| delete | `conf/base/catalog/catalog_tmp_uc1_cov.yml` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `4ec7791f15b8b4ca55bd4366a1bd3f8c03c527e3978ac113e14de960c48bd527` · base trailing newline: yes · new sha256 `74e87bd5995f670c5f898cc4e8ee60d87c955b29f3229b1a939b69a26c6cf061` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the persona-axis pipelines live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- CC raw extracts for A3 ------------------------------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions,
# crx_cc_balance and crx_cc_billing. Read from raw because the spine-scoped primaries
# lack the history the cc_180_plus windows need.
# Grain: (account_id). The per-account [acct_start, acct_end] window of the CC raw
# extracts, from the A3 episode anchor (build_cc_acct_windows).
crx_cc_acct_windows:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_cc_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_balance"
  save_args:
    mode: overwrite

# Grain: (contract_id, observation_date): one row per billing cycle, with due_date and
# next_billing_date (the next statement). A3 builds its cycles from it.
crx_cc_billing:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_billing"
  save_args:
    mode: overwrite

# -- CC full billing history ------------------------------------------------
# Grain: (account_id, billing_date) — one row per billing cycle.
# Full history, no date window — built straight from raw_stg_billing (dlq_bucket
# parsed from add_info), leftsemi-scoped to cc_spine.
crx_cc_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history"
  save_args:
    mode: overwrite

# -- CC A4 deterioration: DPD journey (one shuffle + per-account Python engine) --
# Built from crx_cc_full_history by the shared crx_persona/_dpd_journey/ package
# (CC scheme; RL uses the same package with its own scheme).
# restructure_blind_spot_flag is derived from crx_cc_full_history alone
# (see cc_a4_deterioration/nodes.py).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_cc_full_history gets a row (nothing silently dropped);
# build_cc_a4_deterioration keeps only build_status == 'ok'.
crx_cc_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: CC native 4-7; 180_plus:
# CC native 8-9).
crx_cc_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a4_deterioration"
  save_args:
    mode: overwrite

# ── CC A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_cc_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_cc_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_location_signals"
  save_args:
    mode: overwrite

crx_cc_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_cc_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── Observation base: (account_id, observation_date, cif_id), one per product ──
crx_cc_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_obs_base"
  save_args:
    mode: overwrite

crx_rl_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_obs_base"
  save_args:
    mode: overwrite

# ── CC A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_cc_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_cc_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_distress_signals"
  save_args:
    mode: overwrite

crx_cc_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
  save_args:
    mode: overwrite

# ── CC A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).
# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,
#             payment_credibility_low, payment_credibility_unknown}.
# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE plan
# instalments; crx_cc_a3_promise_events: the promise events judged by payment.
# Spec: workplace_mirror/specs/A3_credibility_spec.md.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_episode"
  save_args:
    mode: overwrite

crx_cc_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_instalments"
  save_args:
    mode: overwrite

crx_cc_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_promise_events"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_cc_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_dues"
  save_args:
    mode: overwrite

crx_cc_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payments"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B1) ───────────────────────────────────────────────────
# Grain: (account_id, month_end_date). Full monthly history for all RL spine
# accounts. Source: int_loan_master (month-end snapshots). No date window: A4 reads
# the whole DPD history to find the current delinquency episode.
crx_rl_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history"
  save_args:
    mode: overwrite

# ── RL A4 deterioration: DPD journey (one shuffle + per-account Python engine) ──
# Built from crx_rl_full_history by the shared crx_persona/_dpd_journey/ package
# (RL scheme; CC uses the same package with its own scheme).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_rl_full_history gets a row (nothing silently dropped);
# build_rl_a4_deterioration keeps only build_status == 'ok'.
crx_rl_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: RL native 3-6; 180_plus:
# RL native 7).
crx_rl_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration"
  save_args:
    mode: overwrite

# Spine history with the original loans of matched restructured accounts in front.
crx_rl_full_history_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history_linked"
  save_args:
    mode: overwrite

# One row per restructure chain: when it is known, its size and match audit.
crx_rl_restructure_chains:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_restructure_chains"
  save_args:
    mode: overwrite

# crx_rl_dpd_sequences on the linked history.
crx_rl_dpd_sequences_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_linked"
  save_args:
    mode: overwrite

# ── RL A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_rl_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_rl_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_distress_signals"
  save_args:
    mode: overwrite

crx_rl_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability"
  save_args:
    mode: overwrite

# ── RL A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_rl_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_rl_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_location_signals"
  save_args:
    mode: overwrite

crx_rl_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_rl_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability"
  save_args:
    mode: overwrite

# ── RL A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain and states as CC (crx_rl_obs_base).
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_rl_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_episode"
  save_args:
    mode: overwrite

crx_rl_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_instalments"
  save_args:
    mode: overwrite

crx_rl_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_promise_events"
  save_args:
    mode: overwrite

crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_rl_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_dues"
  save_args:
    mode: overwrite

crx_rl_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payments"
  save_args:
    mode: overwrite

# ── UC1 stated block (stated ability A5, stated intent A6, dispute / request flags) ──
# UC1's outputs, read as they are from the shared file store (read only; written by the
# UC1 team, never by us). No model_id in the path: one store for all model_ids.
crx_uc1_metadata:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/metadata"

crx_uc1_extracted_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/extracted_signals"

crx_uc1_simple_signal_aggregation:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/simple_signal_aggregation"

crx_uc1_signal_level_conflicts:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/signal_level_conflicts"

# Grain (account_id, observation_date); only the month of persona_end_date is scored.
crx_cc_uc1_conversation_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_uc1_conversation_signals"
  save_args:
    mode: overwrite

crx_cc_uc1_stated:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_uc1_stated"
  save_args:
    mode: overwrite

crx_rl_uc1_conversation_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_uc1_conversation_signals"
  save_args:
    mode: overwrite

crx_rl_uc1_stated:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_uc1_stated"
  save_args:
    mode: overwrite
`````

New:

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the persona-axis pipelines live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- CC raw extracts for A3 ------------------------------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions,
# crx_cc_balance and crx_cc_billing. Read from raw because the spine-scoped primaries
# lack the history the cc_180_plus windows need.
# Grain: (account_id). The per-account [acct_start, acct_end] window of the CC raw
# extracts, from the A3 episode anchor (build_cc_acct_windows).
crx_cc_acct_windows:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_cc_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_balance"
  save_args:
    mode: overwrite

# Grain: (contract_id, observation_date): one row per billing cycle, with due_date and
# next_billing_date (the next statement). A3 builds its cycles from it.
crx_cc_billing:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_billing"
  save_args:
    mode: overwrite

# -- CC full billing history ------------------------------------------------
# Grain: (account_id, billing_date) — one row per billing cycle.
# Full history, no date window — built straight from raw_stg_billing (dlq_bucket
# parsed from add_info), leftsemi-scoped to cc_spine.
crx_cc_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history"
  save_args:
    mode: overwrite

# -- CC A4 deterioration: DPD journey (one shuffle + per-account Python engine) --
# Built from crx_cc_full_history by the shared crx_persona/_dpd_journey/ package
# (CC scheme; RL uses the same package with its own scheme).
# restructure_blind_spot_flag is derived from crx_cc_full_history alone
# (see cc_a4_deterioration/nodes.py).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_cc_full_history gets a row (nothing silently dropped);
# build_cc_a4_deterioration keeps only build_status == 'ok'.
crx_cc_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: CC native 4-7; 180_plus:
# CC native 8-9).
crx_cc_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a4_deterioration"
  save_args:
    mode: overwrite

# ── CC A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_cc_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_cc_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_location_signals"
  save_args:
    mode: overwrite

crx_cc_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_cc_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── Observation base: (account_id, observation_date, cif_id), one per product ──
crx_cc_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_obs_base"
  save_args:
    mode: overwrite

crx_rl_obs_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_obs_base"
  save_args:
    mode: overwrite

# ── CC A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_cc_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_cc_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_distress_signals"
  save_args:
    mode: overwrite

crx_cc_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
  save_args:
    mode: overwrite

# ── CC A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).
# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,
#             payment_credibility_low, payment_credibility_unknown}.
# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE plan
# instalments; crx_cc_a3_promise_events: the promise events judged by payment.
# Spec: workplace_mirror/specs/A3_credibility_spec.md.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_episode"
  save_args:
    mode: overwrite

crx_cc_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_instalments"
  save_args:
    mode: overwrite

crx_cc_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_promise_events"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_cc_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_dues"
  save_args:
    mode: overwrite

crx_cc_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payments"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B1) ───────────────────────────────────────────────────
# Grain: (account_id, month_end_date). Full monthly history for all RL spine
# accounts. Source: int_loan_master (month-end snapshots). No date window: A4 reads
# the whole DPD history to find the current delinquency episode.
crx_rl_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history"
  save_args:
    mode: overwrite

# ── RL A4 deterioration: DPD journey (one shuffle + per-account Python engine) ──
# Built from crx_rl_full_history by the shared crx_persona/_dpd_journey/ package
# (RL scheme; CC uses the same package with its own scheme).

# Intermediate — one row per account: build_status + gap-filled monthly
# dlq_buckets array<int> (oldest -> newest, native buckets) + audit columns.
# Every account in crx_rl_full_history gets a row (nothing silently dropped);
# build_rl_a4_deterioration keeps only build_status == 'ok'.
crx_rl_dpd_sequences:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences"
  save_args:
    mode: overwrite

# Shipped output — DPD-journey deterioration state (one state tree, 7 states,
# same vocabulary in both segments), scoped to accounts whose most recent
# (native) bucket is in the run's segment (60_180: RL native 3-6; 180_plus:
# RL native 7).
crx_rl_a4_deterioration:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration"
  save_args:
    mode: overwrite

# Spine history with the original loans of matched restructured accounts in front.
crx_rl_full_history_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history_linked"
  save_args:
    mode: overwrite

# One row per restructure chain: when it is known, its size and match audit.
crx_rl_restructure_chains:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_restructure_chains"
  save_args:
    mode: overwrite

# crx_rl_dpd_sequences on the linked history.
crx_rl_dpd_sequences_linked:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_linked"
  save_args:
    mode: overwrite

# ── RL A1 ability (shared a1_ability engine) ────────────────────────────────
# Signal tables at (account_id, observation_date) and the axis crx_rl_a1_ability:
# a1_state in {high, moderate, low, unknown}; a1_state_label in {High, Moderate, Low,
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_rl_a1_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_distress_signals"
  save_args:
    mode: overwrite

crx_rl_a1_eosb_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability"
  save_args:
    mode: overwrite

# ── RL A2 Locatability (shared a2_locatability engine) ─────────────────────────
# Inputs: crx_rl_obs_base, feat_cif_location_monthly, dcore_prm_followup_outcomes,
#         prm_dcore_account_agreements, prm_contract, prm_client, feat_demographics_cif.
# Grain: (account_id, observation_date), month ends, persona months.
# location_state ∈ {skip, in_country, unknown}; reachability_state ∈ {reachable,
# non_reachable, unknown}; a2_state = "deceased" or "<location>__<reachability>".
# Spec: workplace_mirror/specs/A2_locatability_spec.md.

crx_rl_a2_location_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_location_signals"
  save_args:
    mode: overwrite

crx_rl_a2_dcore_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_rl_a2_way4_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_demographics_deceased:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability"
  save_args:
    mode: overwrite

# ── RL A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain and states as CC (crx_rl_obs_base).
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_rl_a3_episode:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_episode"
  save_args:
    mode: overwrite

crx_rl_a3_instalments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_instalments"
  save_args:
    mode: overwrite

crx_rl_a3_promise_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_promise_events"
  save_args:
    mode: overwrite

crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

# the dues and payments the A3 ledger, promise events and contacts read
crx_rl_a3_dues:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_dues"
  save_args:
    mode: overwrite

crx_rl_a3_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payments"
  save_args:
    mode: overwrite

# ── UC1 stated block (stated ability A5, stated intent A6, dispute / request flags) ──
# UC1's outputs, read as they are from the shared file store (read only; written by the
# UC1 team, never by us). No model_id in the path: one store for all model_ids.
# The pipeline reads the customer table and the call metadata.
crx_uc1_customer_signal_export:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/customer_signal_export"

crx_uc1_metadata:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/metadata"

# Read only by the UC1 validation snippets (tmp_validation/uc1_full), not by the pipeline.
crx_uc1_extracted_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/extracted_signals"

crx_uc1_simple_signal_aggregation:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/simple_signal_aggregation"

crx_uc1_signal_level_conflicts:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/signal_level_conflicts"

# Grain (account_id, observation_date); only the UC1 month (uc1_month_end, else
# persona_end_date) is scored.
crx_cc_uc1_conversation_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_uc1_conversation_signals"
  save_args:
    mode: overwrite

crx_cc_uc1_stated:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_uc1_stated"
  save_args:
    mode: overwrite

crx_rl_uc1_conversation_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_uc1_conversation_signals"
  save_args:
    mode: overwrite

crx_rl_uc1_stated:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_uc1_stated"
  save_args:
    mode: overwrite
`````

### FILE: `conf/base/catalog/catalog_tmp_b31_check.yml`
action: add · new sha256 `347a1bdea1a871659221d3ee413e3952e2aed9de67984b409f0ad64f7d02784e` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundle 31): the UC1 block before step 8; removed by the bundle's cleanup.
crx_cc_b31_old_uc1:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b31_check/crx_cc_b31_old_uc1"
  save_args:
    mode: overwrite

crx_rl_b31_old_uc1:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b31_check/crx_rl_b31_old_uc1"
  save_args:
    mode: overwrite
`````

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `082b2ad86c5dd804c60fd19233fe03ccd0599d12e9ac885457c92ce1f585d6f4` · base trailing newline: yes · new sha256 `90f28469de46ee5497538ba472a5f8a304cc9d055a9c2bfa19a3da138615f276` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
##################################################
# CRX PERSONA PIPELINE CONFIGURATION
##################################################
# Persona window: the months the obs base keeps (persona_start_date .. persona_end_date).
# Raw histories (crx_cc_full_history, crx_rl_full_history) are not windowed: A4 reads
# the whole DPD history to find the current delinquency episode.
# Orthogonal to modelling.start_date / modelling.end_date (training spine window).
##################################################

crx_persona: "${globals:crx_persona}"

# Segment id for the currently-running model variant (cc_60_180 / cc_180_plus /
# rl_60_180 / rl_180_plus). Additive key (R18) — read by the persona nodes (e.g. the shared
# a2_locatability engine) to select segment-aware behaviour; same resolver pattern
# as crx_persona above.
model_id: "${globals:model_id}"

# CC A3 payment credibility - earliest billing date A3 reads (TEMPORARY).
# Billing has no rows 2021-01..2023-12 (balance/transaction: 2019-2021), so history
# before this date is not used by A3, and the raw extract windows never start more than
# 35 days before it (crx_cc_acct_windows). Set to null once the
# source backfill lands. Separate from A4's dpd_journey.cc_history_floor_date, so
# relaxing A4's floor for the 180+ vintage never moves A3. crx_cc_full_history is NOT
# floored (A4 reads it).
cc_a3_history_floor_date: "2024-01-01"
`````

New:

`````yaml
##################################################
# CRX PERSONA PIPELINE CONFIGURATION
##################################################
# Persona window: the months the obs base keeps (persona_start_date .. persona_end_date).
# Raw histories (crx_cc_full_history, crx_rl_full_history) are not windowed: A4 reads
# the whole DPD history to find the current delinquency episode.
# Orthogonal to modelling.start_date / modelling.end_date (training spine window).
##################################################

crx_persona: "${globals:crx_persona}"

# Segment id for the currently-running model variant (cc_60_180 / cc_180_plus /
# rl_60_180 / rl_180_plus). Additive key (R18) — read by the persona nodes (e.g. the shared
# a2_locatability engine) to select segment-aware behaviour; same resolver pattern
# as crx_persona above.
model_id: "${globals:model_id}"

# UC1 stated block: the month end UC1 is scored at (UC1's customer table carries no date
# per level). null = crx_persona.persona_end_date. 2026-07-31: the last UC1 call is
# 2026-07-16, so July is the month its table describes.
uc1_month_end: "2026-07-31"

# CC A3 payment credibility - earliest billing date A3 reads (TEMPORARY).
# Billing has no rows 2021-01..2023-12 (balance/transaction: 2019-2021), so history
# before this date is not used by A3, and the raw extract windows never start more than
# 35 days before it (crx_cc_acct_windows). Set to null once the
# source backfill lands. Separate from A4's dpd_journey.cc_history_floor_date, so
# relaxing A4's floor for the 180+ vintage never moves A3. crx_cc_full_history is NOT
# floored (A4 reads it).
cc_a3_history_floor_date: "2024-01-01"
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `581be2c57723cc6c8bfe7fda5840dcb2f2215c50a510d4d85a5d4bae8c02efa4` · base trailing newline: yes · new sha256 `3659124f4d2402d098a5ae2cb2a7fb861c16768242148651cb8a1e6bb8de486e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 28): removed by the cleanup
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

New:

`````python
"""Project pipeline registry."""

from kedro.pipeline import Pipeline

from enbd_collections.pipelines import schema_intelligence as si
from enbd_collections.pipelines import credit_card as cc_dpl
from enbd_collections.pipelines import credit_card_way4 as cc_way4
from enbd_collections.pipelines import demographics as demo
from enbd_collections.pipelines import bureau
from enbd_collections.pipelines import retail_loans

from enbd_collections.pipelines.credit_card import staging as cc_dpl_stg
from enbd_collections.pipelines.credit_card import primary as cc_dpl_prm
from enbd_collections.pipelines.credit_card import features as cc_dpl_feat
from enbd_collections.pipelines.credit_card import spine as cc_dpl_spine
from enbd_collections.pipelines.credit_card import model_input as cc_dpl_mi

from enbd_collections.pipelines.credit_card_way4 import staging as cc_way4_stg
from enbd_collections.pipelines.credit_card_way4 import primary as cc_way4_prm
from enbd_collections.pipelines.credit_card_way4 import features as cc_way4_feat
from enbd_collections.pipelines.credit_card_way4 import spine as cc_way4_spine
from enbd_collections.pipelines.credit_card_way4 import target as cc_way4_target
from enbd_collections.pipelines.demographics import staging as demo_stg
from enbd_collections.pipelines.demographics import intermediate as demo_int
from enbd_collections.pipelines.demographics import primary as demo_prm
from enbd_collections.pipelines.demographics import features as demo_feat

from enbd_collections.pipelines.bureau import staging as bureau_stg
from enbd_collections.pipelines.bureau import primary as bureau_prm
from enbd_collections.pipelines.bureau import intermediate as bureau_int
from enbd_collections.pipelines.bureau import features as bureau_feat
from enbd_collections.pipelines.bureau import salary_bounces as bureau_salary_bounces

from enbd_collections.pipelines.casa import primary as casa_prm
from enbd_collections.pipelines.casa import features as casa_feat
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

from enbd_collections.pipelines.retail_loans import staging as retail_loans_stg
from enbd_collections.pipelines.retail_loans import primary as retail_loans_prm
from enbd_collections.pipelines.retail_loans import intermediate as retail_loans_int
from enbd_collections.pipelines.retail_loans import features as retail_loans_feat
from enbd_collections.pipelines.retail_loans import spine as retail_loans_spine
from enbd_collections.pipelines.retail_loans import target as retail_loans_target

from enbd_collections.pipelines import dcore
from enbd_collections.pipelines.dcore import staging as dcore_stg
from enbd_collections.pipelines.dcore import primary as dcore_prm
from enbd_collections.pipelines.dcore import intermediate as dcore_int
from enbd_collections.pipelines.dcore import features as dcore_feat

from enbd_collections.pipelines.sampling import dpl as sampling_dpl
from enbd_collections.pipelines.sampling import overdue as sampling_overdue
from enbd_collections.pipelines.sampling import aecb as sampling_aecb
from enbd_collections.pipelines.sampling import demographics as sampling_demo
from enbd_collections.pipelines.sampling import ddi as sampling_ddi
from enbd_collections.pipelines.sampling import way4 as sampling_way4
from enbd_collections.pipelines.sampling import retail_loans as sampling_retail
from enbd_collections.pipelines.sampling import dcore as sampling_dcore
from enbd_collections.pipelines.validation import mpdpd as validation_mpdpd
from enbd_collections.pipelines.validation import (
    demographics as validation_demographics,
)
from enbd_collections.pipelines.validation import (
    validate_dcore_cc_180_plus as validation_dcore_cc_180_plus,
)
from enbd_collections.pipelines.bureau import validation as validation_bureau
from enbd_collections.pipelines import model_input
from enbd_collections.pipelines import model_training
from enbd_collections.pipelines import model_reporting
from enbd_collections.pipelines.crx_persona import (
    cc_full_history as crx_cc_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    cc_raw_extract as crx_cc_raw_extract,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a4_deterioration as crx_cc_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a2_locatability as crx_cc_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability as crx_cc_a1_ability,
)
from enbd_collections.pipelines.crx_persona import obs_base as crx_obs_base

from enbd_collections.pipelines.crx_persona import (
    cc_a3_payment_credibility as crx_cc_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import (
    rl_full_history as crx_rl_full_history,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a4_deterioration as crx_rl_a4_deterioration,
)
from enbd_collections.pipelines.crx_persona import rl_a1_ability as crx_rl_a1_ability
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines.crx_persona import cc_uc1_stated as crx_cc_uc1_stated
from enbd_collections.pipelines.crx_persona import rl_uc1_stated as crx_rl_uc1_stated
from enbd_collections.pipelines.crx_persona import b31_check  # TEMPORARY
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


def register_pipelines() -> dict[str, Pipeline]:
    """Pipeline registry."""

    return {
        # -- Model input (cross-domain) ------------------------------------
        "model_input": model_input.create_pipeline(),
        "model_input_base": model_input.create_base_pipeline(),
        "model_input_features": model_input.create_features_pipeline(),
        # -- Model training & reporting ------------------------------------
        "model_training": model_training.create_pipeline(),
        "model_reporting": model_reporting.create_pipeline(),
        # -- Credit card DPL (domain) --------------------------------------
        "cc_dpl": cc_dpl.create_pipeline(),
        "cc_dpl_data_spine": cc_dpl_spine.create_data_spine_pipeline(),
        "cc_dpl_staging": cc_dpl_stg.create_pipeline(),
        "cc_dpl_primary": cc_dpl_prm.create_pipeline(),
        "cc_dpl_spine_target": cc_dpl_spine.create_pipeline(),
        "cc_dpl_spine_recovery_target": cc_dpl_spine.create_recovery_pipeline(),
        "cc_dpl_features": cc_dpl_feat.create_pipeline(),
        "cc_dpl_model_input": cc_dpl_mi.create_pipeline(),
        # -- Credit card Way4 (domain) -------------------------------------
        "cc_way4_spine": cc_way4_spine.create_pipeline(),
        "cc_way4_staging": cc_way4_stg.create_pipeline(),
        "cc_way4_primary": cc_way4_prm.create_pipeline(),
        "cc_way4_target": cc_way4_target.create_pipeline(),
        "cc_way4_features": cc_way4_feat.create_pipeline(),
        # -- Demographics (domain) -----------------------------------------
        "demographics": demo.create_pipeline(cif_obs_spine="rl_cif_obs_spine"),
        "demographics_cc": demo.create_pipeline(cif_obs_spine="cc_cif_obs_spine"),
        "demographics_staging": demo_stg.create_pipeline(),
        "demographics_primary": demo_prm.create_pipeline(),
        "demographics_intermediate": demo_int.create_pipeline(),
        "demographics_features": demo_feat.create_pipeline(
            cif_obs_spine="rl_cif_obs_spine"
        ),
        "demographics_features_cc": demo_feat.create_pipeline(
            cif_obs_spine="cc_cif_obs_spine"
        ),
        # -- Bureau / AECB (domain) ----------------------------------------
        "bureau": bureau.create_pipeline(),
        "bureau_staging": bureau_stg.create_pipeline(),
        "bureau_primary": bureau_prm.create_pipeline(),
        "bureau_intermediate": bureau_int.create_pipeline(),
        "bureau_features": bureau_feat.create_pipeline(),
        "bureau_salary_bounces": bureau_salary_bounces.create_pipeline(),
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
        "casa_features": casa_feat.create_pipeline(),
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        # -- Retail Loans (domain) -----------------------------------------
        "retail_loans": retail_loans.create_pipeline(),
        "retail_loans_staging": retail_loans_stg.create_pipeline(),
        "retail_loans_primary": retail_loans_prm.create_pipeline(),
        "retail_loans_intermediate": retail_loans_int.create_pipeline(),
        "retail_loans_features": retail_loans_feat.create_pipeline(),
        # -- Schema intelligence -------------------------------------------
        "schema_intelligence": si.create_pipeline(),
        # -- Sampling ------------------------------------------------------
        "dpl_sampling": sampling_dpl.create_pipeline(),
        "overdue_sampling": sampling_overdue.create_pipeline(),
        "aecb_sampling": sampling_aecb.create_pipeline(),
        "demographics_sampling": sampling_demo.create_pipeline(),
        "ddi_sampling": sampling_ddi.create_pipeline(),
        "way4_sampling": sampling_way4.create_pipeline(),
        "retail_loans_sampling": sampling_retail.create_pipeline(),
        "dcore_sampling": sampling_dcore.create_pipeline(),
        # -- Validation ----------------------------------------------------
        "validate_mpdpd": validation_mpdpd.create_pipeline(),
        "validate_bureau_alerts": validation_bureau.create_pipeline(),
        "validate_demographics": validation_demographics.create_pipeline(),
        "validate_dcore_cc_180_plus": validation_dcore_cc_180_plus.create_pipeline(),
        # -- DCORE (Collections Management System) -------------------------
        "dcore": dcore.create_pipeline(),
        "dcore_staging": dcore_stg.create_pipeline(),
        "dcore_primary": dcore_prm.create_pipeline(),
        "dcore_intermediate": dcore_int.create_pipeline(),
        "dcore_features": dcore_feat.create_pipeline(),
        # -- Model variant pipelines (namespaced by model_id) --------------
        # Full pipelines — run with: kedro run --env=dev --pipeline=<model_id>
        "cc_60_180": cc_way4.create_pipeline(),
        "cc_180_plus": cc_way4.create_180_plus_pipeline(),
        "rl_60_180": retail_loans.create_rl_60_180_pipeline(),
        "rl_180_plus": retail_loans.create_rl_180_plus_pipeline(),
        # Sub-pipelines for incremental cc_60_180 runs
        "cc_60_180.spine": cc_way4_spine.create_pipeline(),
        "cc_60_180.staging": cc_way4_stg.create_pipeline(),
        "cc_60_180.target": cc_way4_target.create_pipeline(),
        "cc_60_180.features": cc_way4_feat.create_pipeline(),
        "cc_60_180.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Bureau scoped to this model's spine CIFs (model_id set by ModelConfigHook)
        "cc_60_180.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        "cc_180_plus.bureau": bureau.create_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_60_180.bureau": bureau.create_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.bureau": bureau.create_pipeline(),
        # -- CRX Persona (experimental, additive) ---------------------------
        # Revert: remove this entry + the import above + rm -r crx_persona/
        "crx_cc_full_history": crx_cc_full_history.create_pipeline(),
        "crx_cc_raw_extract": crx_cc_raw_extract.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_uc1_stated": crx_cc_uc1_stated.create_pipeline(),
        "crx_rl_uc1_stated": crx_rl_uc1_stated.create_pipeline(),
        "crx_cc_b31_snapshot": b31_check.create_snapshot_pipeline("cc"),
        "crx_rl_b31_snapshot": b31_check.create_snapshot_pipeline("rl"),
        "crx_cc_b31_compare": b31_check.create_compare_pipeline("cc"),
        "crx_rl_b31_compare": b31_check.create_compare_pipeline("rl"),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (bundle 28): removed by the cleanup
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
        # -- Genesys / PCA interactions ----------------------------------------
        "genesys": genesys.create_pipeline(),
        # -- Default ---------------------------------------------------------
        "__default__": cc_way4.create_pipeline(),
        "rerun": model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
        "rerun_full": model_input.create_base_pipeline()
        + model_input.create_features_pipeline()
        + model_training.create_pipeline()
        + model_reporting.create_pipeline(),
    }
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/b31_check.py`
action: add · new sha256 `431247b950f2f6e6b3f27f753ed26341d697db1016db52cc986523940d4f2503` · new trailing newline: yes

New:

`````python
"""TEMPORARY (bundle 31): the UC1 stated block before and after the bundle's step 8.

``crx_<p>_b31_snapshot`` (run before step 8) copies the persisted UC1 block's evidence and
states into ``crx_<p>_b31_old_uc1`` (explicit entry in ``catalog_tmp_b31_check.yml``).
``crx_<p>_b31_compare`` (run after step 8) logs, for ``model_id``:

- ``B31 ROWS``: per month, rows and rows with a UC1 value;
- ``B31 DIST``: at the UC1 month, ``uc1_evidence``, the states, UC1's confidence, the
  flags, and ``uc1_evidence`` by A2 reachability;
- ``B31 OLD NEW``: per account, the old block (persona end month) x the new one (UC1
  month): evidence, A5, A6;
- ``B31 PAID``: at the UC1 month, paid_due / paid_any over the next month (payments
  reaching max(the due at the month end, 100 AED) / 100 AED, from the A3 dues and
  payments) by state and flag, inside the A1 / A3 states, with two AUCs.

Counts under 10 show as "<10". Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b31_snapshot      (before step 8)
    kedro run --pipeline=crx_<p>_b31_compare       (after step 8)
"""

import logging

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.window import Window

from ._common import GRAIN
from .uc1_stated.signals import scored_month

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "b31_check"]
OLD_COLUMNS = ["uc1_evidence", "a5_state", "a6_state"]
MIN_CELL = 10
A5_ORDER = {"able": 3, "partly_able": 2, "not_stated": 1, "unable": 0}
A6_ORDER = {"pays_in_full": 3, "partly_or_later": 2, "not_stated": 1, "refuses": 0}


def snapshot(uc1: DataFrame) -> DataFrame:
    """``GRAIN`` and the old block's evidence and states (those the table has)."""
    return uc1.select(*GRAIN, *(c for c in OLD_COLUMNS if c in uc1.columns))


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _n(count: int) -> str:
    return f"<{MIN_CELL}" if count < MIN_CELL else str(count)


def _counts(df: DataFrame, cols: list[str], title: str) -> list[str]:
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [f"  {title}:"] + [
        f"    {' | '.join(str(r[c]) for c in cols)}: {_n(r['count'])}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ]


def _rates(df: DataFrame, cols: list[str], title: str) -> list[str]:
    """n, paid_due % and paid_any % per value of ``cols``."""
    rows = (
        df.groupBy(*cols)
        .agg(
            F.count(F.lit(1)).alias("n"),
            F.avg("paid_due").alias("due"),
            F.avg("paid_any").alias("any"),
        )
        .orderBy(*cols)
        .collect()
    )
    out = [f"  {title} (n, paid_due %, paid_any %):"]
    for r in rows:
        key = " | ".join(str(r[c]) for c in cols)
        if r["n"] < MIN_CELL:
            out.append(f"    {key}: <{MIN_CELL}")
        else:
            out.append(
                f"    {key}: {r['n']}, {100 * r['due']:.1f}, {100 * r['any']:.1f}"
            )
    return out


def _auc(df: DataFrame, col: str, order: dict[str, int], title: str) -> list[str]:
    """AUC of ``order`` on paid_due over the rows whose ``col`` is in it (ties = 1/2)."""
    score = F.create_map(*[F.lit(x) for kv in order.items() for x in kv])[F.col(col)]
    cells = (
        df.select(score.alias("s"), "paid_due")
        .filter(F.col("s").isNotNull())
        .groupBy("s")
        .agg(F.sum("paid_due").alias("pos"), F.count(F.lit(1)).alias("n"))
        .collect()
    )
    pos = {r["s"]: r["pos"] for r in cells}
    neg = {r["s"]: r["n"] - r["pos"] for r in cells}
    n_pos, n_neg = sum(pos.values()), sum(neg.values())
    if not n_pos or not n_neg:
        return [f"  {title}: no AUC (one outcome only)"]
    won = sum(
        pos[a] * neg[b] * (1.0 if a > b else 0.5 if a == b else 0.0)
        for a in pos
        for b in neg
    )
    return [f"  {title}: {won / (n_pos * n_neg):.3f} (n {n_pos + n_neg})"]


def _outcomes(base: DataFrame, dues: DataFrame, payments: DataFrame) -> DataFrame:
    """``GRAIN`` + paid_due / paid_any over the month after the observation date."""
    obs = F.col("observation_date")
    latest_due = (
        base.select(*GRAIN)
        .join(dues.select("account_id", "cycle_start", "due_amount"), "account_id")
        .filter(F.col("cycle_start") <= obs)
        .withColumn(
            "_r",
            F.row_number().over(
                Window.partitionBy(*GRAIN).orderBy(F.col("cycle_start").desc())
            ),
        )
        .filter("_r = 1")
        .select(*GRAIN, "due_amount")
    )
    paid = (
        base.select(*GRAIN)
        .join(payments.select("account_id", "pay_date", "amount"), "account_id")
        .filter((F.col("pay_date") > obs) & (F.col("pay_date") <= F.add_months(obs, 1)))
        .groupBy(*GRAIN)
        .agg(F.sum("amount").alias("_paid"))
    )
    amount = F.coalesce(F.col("_paid"), F.lit(0))
    due = F.greatest(F.coalesce(F.col("due_amount"), F.lit(0)), F.lit(100))
    return (
        base.select(*GRAIN)
        .join(latest_due, list(GRAIN), "left")
        .join(paid, list(GRAIN), "left")
        .select(
            *GRAIN,
            (amount >= due).cast("int").alias("paid_due"),
            (amount >= 100).cast("int").alias("paid_any"),
        )
    )


def _promise_kind() -> Column:
    a6 = F.col("a6_state")
    named = (F.col("a6_amount_named_flag") == 1) | (F.col("a6_date_named_flag") == 1)
    paying = a6.isin("pays_in_full", "partly_or_later")
    flag = F.col("stated_promise_unlogged_flag")
    return (
        F.when(F.col("uc1_evidence") != "extracted", "no_uc1")
        .when(flag == 1, "said_unlogged")
        .when(paying & named & (flag == 0), "said_logged")
        .when(paying & named, "said_no_dated_call")
        .when(paying, "paying_no_amount_date")
        .otherwise("other_reading")
    )


def compare(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old: DataFrame,
    uc1: DataFrame,
    a1: DataFrame,
    a2: DataFrame,
    a3: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    *,
    model_id: str,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> None:
    """Log the ``B31`` blocks (module docstring)."""
    month = scored_month(persona_end_date, uc1_month_end)
    per_month = (
        uc1.groupBy(F.last_day("observation_date").alias("month"))
        .agg(
            F.count(F.lit(1)).alias("rows"),
            F.count("uc1_evidence").alias("scored"),
        )
        .orderBy("month")
        .collect()
    )
    _block(
        "B31 ROWS",
        model_id,
        ["  month: rows / with a UC1 value"]
        + [f"    {r['month']}: {r['rows']} / {r['scored']}" for r in per_month],
    )

    def at(df: DataFrame, date: str) -> DataFrame:
        return df.filter(
            F.trunc("observation_date", "month") == F.trunc(F.lit(str(date)), "month")
        )

    new = (
        at(uc1, month)
        .join(at(a1, month).select(*GRAIN, "a1_state"), list(GRAIN), "left")
        .join(at(a2, month).select(*GRAIN, "reachability_state"), list(GRAIN), "left")
        .join(
            at(a3, month).select(*GRAIN, "a3_state", "a3_commitments_level"),
            list(GRAIN),
            "left",
        )
        .localCheckpoint()
    )
    stated = new.filter(F.col("uc1_evidence") == "extracted")
    dist = []
    for col in ("uc1_evidence", "a5_state", "a6_state"):
        dist += _counts(new, [col], col)
    for col in (
        "a5_confidence",
        "a6_confidence",
        "stated_promise_unlogged_flag",
        "verify_stated_ability_flag",
        "stated_dispute",
        "stated_request_flag",
    ):
        dist += _counts(stated, [col], f"{col} (UC1 rows)")
    dist += _counts(new, ["reachability_state", "uc1_evidence"], "reach x evidence")
    _block("B31 DIST", model_id, [f"  UC1 month {month}"] + dist)

    def side(df: DataFrame, prefix: str) -> DataFrame:
        return df.select(
            "account_id", *(F.col(c).alias(f"{prefix}_{c}") for c in OLD_COLUMNS)
        )

    pairs = side(at(old, persona_end_date), "old").join(
        side(new, "new"), "account_id", "full"
    )
    old_new = [f"  old = {persona_end_date} month, new = {month} month, per account"]
    for col in OLD_COLUMNS:
        old_new += _counts(pairs, [f"old_{col}", f"new_{col}"], f"{col} old | new")
    _block("B31 OLD NEW", model_id, old_new)

    rows = (
        new.join(_outcomes(new, dues, payments), list(GRAIN), "left")
        .withColumn("promise_kind", _promise_kind())
        .localCheckpoint()
    )
    rows_stated = rows.filter(F.col("uc1_evidence") == "extracted")
    unknown = rows_stated.filter(F.col("a1_state") == "unknown")
    no_promise = rows_stated.filter(F.col("a3_commitments_level") == "no_promise")
    paid = (
        [f"  UC1 month {month}; outcome = the next month"]
        + _rates(rows, ["uc1_evidence"], "evidence")
        + _rates(rows, ["a1_state", "a5_state"], "A1 x A5")
        + _auc(unknown, "a5_state", A5_ORDER, "AUC A5 inside A1 unknown")
        + _rates(rows, ["a3_commitments_level", "a6_state"], "A3 level x A6")
        + _auc(no_promise, "a6_state", A6_ORDER, "AUC A6 inside A3 no_promise")
        + _rates(rows, ["a3_state", "a6_state"], "A3 state x A6")
        + _rates(rows_stated, ["a5_reason"], "reason (UC1 rows)")
        + _rates(unknown, ["a5_reason"], "reason inside A1 unknown")
        + _rates(
            rows_stated.filter(F.col("a1_state") == "low"),
            ["verify_stated_ability_flag"],
            "verify flag inside A1 low",
        )
        + _rates(rows, ["a3_commitments_level", "promise_kind"], "A3 level x promise")
        + _rates(rows, ["promise_kind"], "promise")
        + _rates(
            rows_stated.withColumn(
                "dispute_any", (F.col("stated_dispute") != "none").cast("int")
            ),
            ["dispute_any"],
            "stated dispute (UC1 rows)",
        )
        + _rates(rows_stated, ["stated_request_flag"], "request (UC1 rows)")
        + _rates(rows_stated, ["a6_confidence", "a6_state"], "A6 by confidence")
    )
    _block("B31 PAID", model_id, paid)


def create_snapshot_pipeline(product: str) -> Pipeline:
    """Copy the persisted UC1 block of ``product`` before step 8."""
    return pipeline(
        [
            node(
                func=snapshot,
                inputs={"uc1": f"crx_{product}_uc1_stated"},
                outputs=f"crx_{product}_b31_old_uc1",
                name=f"crx_{product}_b31_snapshot",
                tags=TAGS,
            )
        ]
    )


def create_compare_pipeline(product: str) -> Pipeline:
    """Log the ``B31`` blocks of ``product`` after step 8."""
    return pipeline(
        [
            node(
                func=compare,
                inputs={
                    "old": f"crx_{product}_b31_old_uc1",
                    "uc1": f"crx_{product}_uc1_stated",
                    "a1": f"crx_{product}_a1_ability",
                    "a2": f"crx_{product}_a2_locatability",
                    "a3": f"crx_{product}_a3_payment_credibility",
                    "dues": f"crx_{product}_a3_dues",
                    "payments": f"crx_{product}_a3_payments",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                    "uc1_month_end": "params:uc1_month_end",
                },
                outputs=None,
                name=f"crx_{product}_b31_compare",
                tags=TAGS,
            )
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_uc1_stated/pipeline.py`
action: replace · base sha256 `2cf0bc6612791f039aeedd575564738a6b0c5f1ef27d087b997f39db35e688f1` · base trailing newline: yes · new sha256 `a145749861c2a23780c55aa4bd5494ac36bc6cc3379144e3d203716748696158` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CC UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``.

    kedro run --pipeline=crx_cc_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_uc1_stated", **kwargs
) -> Pipeline:
    """The CC UC1 stated block written to ``output``."""
    return create_uc1_pipeline("cc", output)
`````

New:

`````python
"""Kedro pipeline: CC UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``, ``crx_cc_a1_ability``,
``crx_cc_a3_promise_events``.

    kedro run --pipeline=crx_cc_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_uc1_stated", **kwargs
) -> Pipeline:
    """The CC UC1 stated block written to ``output``."""
    return create_uc1_pipeline("cc", output)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_uc1_stated/pipeline.py`
action: replace · base sha256 `1d03847bf280b5f8648a132490d9688f82313aada820790ed38530c563cccbaf` · base trailing newline: yes · new sha256 `8ffa5b7804eb3a6c72a6f78f4841f26ae7f002d939ab51c58bd79ab6334ff4c2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``.

    kedro run --pipeline=crx_rl_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_uc1_stated", **kwargs
) -> Pipeline:
    """The RL UC1 stated block written to ``output``."""
    return create_uc1_pipeline("rl", output)
`````

New:

`````python
"""Kedro pipeline: RL UC1 stated block on the shared ``uc1_stated`` engine.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``, ``crx_rl_a1_ability``,
``crx_rl_a3_promise_events``.

    kedro run --pipeline=crx_rl_uc1_stated
"""

from kedro.pipeline import Pipeline

from ..uc1_stated.pipeline import create_uc1_pipeline


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_uc1_stated", **kwargs
) -> Pipeline:
    """The RL UC1 stated block written to ``output``."""
    return create_uc1_pipeline("rl", output)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/uc1_stated/classify.py`
action: replace · base sha256 `7d1bd448cfcebf3ab48eaf39f4582220869d420c272dddc85742d25c56d27dac` · base trailing newline: yes · new sha256 `10c56f612bd7846cdc8db9b962f8194524f0d7df9a8e19013c2051515e9d33a0` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""UC1 stated block at (account_id, observation_date), shared by CC and RL.

UC1's customer table ``timelines/simple_signal_aggregation`` is read as it is: one level
per signal per customer, the most frequent over all of the customer's extracted
conversations (UC1's rule; no date, confidence or count). This module maps levels to
states and adds the conversation counts of ``signals.py``:

* ``a5_state``, stated ability, from ``payment_capacity``: able / partly_able / unable;
* ``a6_state``, stated intent, from ``payment_intent``: pays_in_full / partly_or_later
  (partial or with delay) / refuses;
* ``not_stated``: the customer has an extracted conversation before the observation
  date, and the signal was not detected;
* ``no_evidence``: no such conversation; ``uc1_evidence`` says why (no_cif /
  no_conversation / not_extracted).

Legacy-format extractions are not read (``signals.py`` drops those conversations).

Support: the conversations before the observation date that detected the signal, and
how many of them detected the published level (``a5_agree_n``, ``a6_agree_n``).
``uc1_after_obs_flag`` = 1 when the published level may rest on a conversation dated on
or after the observation date. Only the month of ``crx_persona.persona_end_date`` is
scored; the other months' rows carry NULL in every UC1 column.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month, require_columns, string_key
from .signals import CAPACITY_LEVELS, INTENT_LEVELS, latest_month

NOT_DETECTED = "NA"
LEVELS = {
    "payment_capacity": CAPACITY_LEVELS,
    "payment_intent": INTENT_LEVELS,
    "delinquency_reason": (
        "lost_employment",
        "reduced_employment",
        "has_employment",
        "increased_obligations",
    ),
    "payment_period": ("salary_cycle_dependent", "weeks", "months_or_longer"),
    "dispute": ("system_problem", "customer_scammed", "other"),
    "request": ("detected",),
}
ABILITY_STATES = {"full": "able", "partial": "partly_able", "none": "unable"}
INTENT_STATES = {
    "payback_full": "pays_in_full",
    "partial": "partly_or_later",
    "with_delay": "partly_or_later",
    "no_payment": "refuses",
}
_COUNTS = [
    "uc1_conversations_n",
    "uc1_extracted_n",
    "uc1_after_obs_flag",
    "amount_named_flag",
    "date_named_flag",
    *[f"capacity_{level}_n" for level in CAPACITY_LEVELS],
    *[f"intent_{level}_n" for level in INTENT_LEVELS],
]
_OUTPUT = [
    "uc1_evidence",
    "a5_state",
    "a5_reason",
    "a5_conversations_n",
    "a5_agree_n",
    "a6_state",
    "a6_intent_level",
    "a6_period",
    "a6_amount_named_flag",
    "a6_date_named_flag",
    "a6_conversations_n",
    "a6_agree_n",
    "stated_dispute",
    "stated_request_flag",
    "uc1_conversations_n",
    "uc1_extracted_n",
    "uc1_last_conversation_date",
    "uc1_last_extracted_date",
    "uc1_after_obs_flag",
]


def _levels(aggregation: DataFrame) -> DataFrame:
    """``cif_id`` and the published level of each signal in ``LEVELS`` (NULL = not
    detected), checked: an unknown level or a missing signal stops the run."""
    require_columns(
        aggregation, ["cif_id", "signals_json"], "UC1 simple_signal_aggregation"
    )
    js = F.col("signals_json")
    levels = aggregation.select(
        string_key(aggregation, "cif_id").alias("cif_id"),
        *[F.get_json_object(js, f"$.{s}").alias(f"_raw_{s}") for s in LEVELS],
        *[F.get_json_object(js, f"$.{s}.level").alias(s) for s in LEVELS],
    )
    unknown = None
    for signal, allowed in LEVELS.items():
        raw = F.col(f"_raw_{signal}")
        known = (raw == NOT_DETECTED) | F.coalesce(
            F.col(signal).isin(*allowed), F.lit(False)
        )
        rows = levels.filter(raw.isNull() | ~known).select(
            F.lit(signal).alias("signal"), raw.alias("value")
        )
        unknown = rows if unknown is None else unknown.unionByName(rows)
    found = unknown.distinct().limit(20).collect()
    if found:
        values = sorted(f"{r['signal']}={r['value']}" for r in found)
        raise ValueError(f"UC1 simple_signal_aggregation has unknown values: {values}")
    return levels.select("cif_id", *LEVELS)


def _mapped(col: str, mapping: dict[str, str]) -> Column:
    pairs = [F.lit(x) for item in mapping.items() for x in item]
    return F.create_map(*pairs)[F.col(col)]


def _support(
    signal: str, prefix: str, levels: tuple[str, ...]
) -> tuple[Column, Column]:
    """Conversations that detected ``signal``, and those that detected its published
    level."""
    total = sum((F.col(f"{prefix}_{level}_n") for level in levels), F.lit(0))
    agree = F.coalesce(
        *[
            F.when(F.col(signal) == level, F.col(f"{prefix}_{level}_n"))
            for level in levels
        ],
        F.lit(0),
    )
    return total, agree


def _evidence() -> Column:
    return (
        F.when(F.col("cif_id").isNull(), "no_cif")
        .when(F.col("uc1_conversations_n") == 0, "no_conversation")
        .when(F.col("uc1_extracted_n") == 0, "not_extracted")
        .otherwise("extracted")
    )


def _stated_columns() -> dict[str, Column]:
    """The stated columns, read after ``uc1_evidence``: NULL details and
    ``no_evidence`` states unless the evidence is ``extracted``."""
    stated = F.col("uc1_evidence") == "extracted"

    def when_stated(col: Column) -> Column:
        return F.when(stated, col)

    def state(signal: str, mapping: dict[str, str]) -> Column:
        value = F.coalesce(_mapped(signal, mapping), F.lit("not_stated"))
        return F.when(stated, value).otherwise("no_evidence")

    a5_total, a5_agree = _support("payment_capacity", "capacity", CAPACITY_LEVELS)
    a6_total, a6_agree = _support("payment_intent", "intent", INTENT_LEVELS)
    request = F.coalesce(F.col("request") == "detected", F.lit(False)).cast("int")
    return {
        "a5_state": state("payment_capacity", ABILITY_STATES),
        "a5_reason": when_stated(F.col("delinquency_reason")),
        "a5_conversations_n": when_stated(a5_total),
        "a5_agree_n": when_stated(a5_agree),
        "a6_state": state("payment_intent", INTENT_STATES),
        "a6_intent_level": when_stated(F.col("payment_intent")),
        "a6_period": when_stated(F.col("payment_period")),
        "a6_amount_named_flag": when_stated(F.col("amount_named_flag")),
        "a6_date_named_flag": when_stated(F.col("date_named_flag")),
        "a6_conversations_n": when_stated(a6_total),
        "a6_agree_n": when_stated(a6_agree),
        "stated_dispute": when_stated(F.coalesce(F.col("dispute"), F.lit("none"))),
        "stated_request_flag": when_stated(request),
    }


def build_uc1_stated(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    aggregation: DataFrame,
    conversations: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation: the evidence status, both stated axes with their
    support and details, the dispute and request flags and the conversation counts."""
    scored = (
        latest_month(obs_base, persona_end_date)
        .join(_levels(aggregation), "cif_id", "left")
        .join(conversations, list(GRAIN), "left")
        .fillna(0, subset=_COUNTS)
        .withColumn("uc1_evidence", _evidence())
    )
    scored = scored.select(
        *scored.columns,
        *[col.alias(name) for name, col in _stated_columns().items()],
    )
    out = obs_base.select(*GRAIN).join(
        scored.select(*GRAIN, *_OUTPUT), list(GRAIN), "left"
    )
    name = f"uc1_stated [{model_id}]"
    for col in ("uc1_evidence", "a5_state", "a6_state"):
        log_latest_month(out, col, name, persona_end_date)
    return out
`````

New:

`````python
"""UC1 stated block at (account_id, observation_date), shared by CC and RL.

UC1's customer table ``customer_signal_export`` is read as it is: one row per customer
and signal, ``estimated_value`` = UC1's final level (call transcripts and agent remarks,
recent evidence weighted higher), with its confidence, the latest transcript value and
the latest agent-remark value. Tied levels arrive joined by ``|``. This module maps the
levels to states and adds two flags:

* ``a5_state``, stated ability, from ``payment_capacity``: able / partly_able / unable;
* ``a6_state``, stated intent, from ``payment_intent``: pays_in_full / partly_or_later
  (partial or with delay) / refuses; a tie takes the more cautious level;
* ``not_stated``: the customer is in UC1's table and the signal is ``not-detected``;
* ``no_evidence``: not in UC1's table; ``uc1_evidence`` says why (no_cif /
  no_conversation / not_extracted);
* ``stated_promise_unlogged_flag``: pays in full or partly / later, an amount or a date
  mentioned, and no A3 promise event near the last call (``signals.py``); NULL when
  that holds but there is no dated call;
* ``verify_stated_ability_flag``: able, or pays in full, while ``a1_state`` is low.

UC1's table carries no date per level, so only one month is scored
(``signals.scored_month``); every other month's row carries NULL in every UC1 column.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, log_latest_month, require_columns, string_key
from .signals import latest_month, scored_month

NOT_DETECTED = "not-detected"
NO_VALUE = (NOT_DETECTED, "N/A", "")
TIE = "|"
# Levels in cautious-first order (a tie keeps the first of its levels in this order).
LEVELS = {
    "payment_capacity": ("none", "partial", "full"),
    "payment_intent": ("no_payment", "with_delay", "partial", "payback_full"),
    "delinquency_reason": (
        "lost_employment",
        "reduced_employment",
        "increased_obligations",
        "has_employment",
    ),
    "payment_period": ("months_or_longer", "salary_cycle_dependent", "weeks"),
    "dispute": ("customer_scammed", "system_problem", "other"),
    "request": ("detected",),
    "fraudulent_customer": ("detected",),
}
REPAYMENT = {
    "amount": "repayment_specifics:amount_mentioned",
    "date": "repayment_specifics:date_specific",
    "plan": "repayment_specifics:plan_structure_mentioned",
}
EXPORT = [
    "cif_id",
    "signal",
    "estimated_value",
    "confidence",
    "latest_value",
    "agent_remark_value",
    "supporting_data",
    "snapshot_date",
]
ABILITY_STATES = {"full": "able", "partial": "partly_able", "none": "unable"}
INTENT_STATES = {
    "payback_full": "pays_in_full",
    "partial": "partly_or_later",
    "with_delay": "partly_or_later",
    "no_payment": "refuses",
}
PAYING = ("pays_in_full", "partly_or_later")
_OUTPUT = [
    "uc1_evidence",
    "uc1_snapshot_date",
    "a5_state",
    "a5_capacity_level",
    "a5_confidence",
    "a5_latest_value",
    "a5_remark_value",
    "a5_supporting_data",
    "a5_reason",
    "a5_reason_confidence",
    "a6_state",
    "a6_intent_level",
    "a6_confidence",
    "a6_latest_value",
    "a6_remark_value",
    "a6_period",
    "a6_amount_named_flag",
    "a6_date_named_flag",
    "a6_plan_named_flag",
    "stated_dispute",
    "stated_request_flag",
    "stated_fraud_flag",
    "stated_promise_unlogged_flag",
    "verify_stated_ability_flag",
    "uc1_conversations_n",
    "uc1_last_conversation_date",
]


def _check_levels(export: DataFrame) -> None:
    """Stop the run on a level UC1's table holds outside ``LEVELS`` (a schema change
    on their side, to be looked at, not guessed)."""
    allowed = F.create_map(
        *[
            x
            for signal, levels in LEVELS.items()
            for x in (F.lit(signal), F.array(*[F.lit(v) for v in levels]))
        ]
    )
    parts = export.filter(F.col("signal").isin(*LEVELS)).select(
        "signal",
        F.explode(F.split("estimated_value", f"\\{TIE}")).alias("level"),
    )
    found = (
        parts.filter(
            F.col("level").isNull()
            | (
                (F.col("level") != NOT_DETECTED)
                & ~F.array_contains(allowed[F.col("signal")], F.col("level"))
            )
        )
        .select("signal", "level")
        .distinct()
        .limit(20)
        .collect()
    )
    if found:
        values = sorted(f"{r['signal']}={r['level']}" for r in found)
        raise ValueError(f"UC1 customer_signal_export has unknown values: {values}")


def _level(col: str, signal: str) -> Column:
    """The level of ``col`` (NULL = not detected); a tie keeps its most cautious level."""
    parts = F.split(F.col(col), f"\\{TIE}")
    cautious = F.coalesce(
        *[F.when(F.array_contains(parts, v), F.lit(v)) for v in LEVELS[signal]]
    )
    return F.when(F.col(col).isin(*NO_VALUE) | F.col(col).isNull(), None).otherwise(
        F.when(F.col(col).contains(TIE), cautious).otherwise(F.col(col))
    )


def _wide(export: DataFrame) -> DataFrame:
    """One row per customer: per signal its estimate and details, the repayment slots'
    mentioned flags, and the snapshot date."""
    require_columns(export, EXPORT, "UC1 customer_signal_export")
    _check_levels(export)
    signal = F.col("signal")

    def pick(name: str, col: str) -> Column:
        return F.max(F.when(signal == name, F.col(col)))

    def mentioned(slot: str) -> Column:
        values = [F.col(c) for c in ("latest_value", "agent_remark_value")]
        named = [(v.isNotNull() & ~v.isin(*NO_VALUE)) for v in values]
        return F.max(F.when((signal == slot) & (named[0] | named[1]), 1).otherwise(0))

    return export.groupBy(string_key(export, "cif_id").alias("cif_id")).agg(
        F.max(F.to_date("snapshot_date")).alias("uc1_snapshot_date"),
        *[pick(s, "estimated_value").alias(f"_est_{s}") for s in LEVELS],
        *[
            pick(s, c).alias(f"_{c}_{s}")
            for s in ("payment_capacity", "payment_intent")
            for c in ("confidence", "latest_value", "agent_remark_value")
        ],
        pick("payment_capacity", "supporting_data").alias("_supporting"),
        pick("delinquency_reason", "confidence").alias("_reason_confidence"),
        *[mentioned(slot).alias(f"_{key}_named") for key, slot in REPAYMENT.items()],
    )


def _mapped(level: Column, mapping: dict[str, str]) -> Column:
    pairs = [F.lit(x) for item in mapping.items() for x in item]
    return F.create_map(*pairs)[level]


def _evidence() -> Column:
    return (
        F.when(F.col("cif_id").isNull(), "no_cif")
        .when(F.col("uc1_snapshot_date").isNotNull(), "extracted")
        .when(F.coalesce(F.col("uc1_conversations_n"), F.lit(0)) > 0, "not_extracted")
        .otherwise("no_conversation")
    )


def _stated_columns() -> dict[str, Column]:
    """The stated columns, read after ``uc1_evidence``: NULL details and
    ``no_evidence`` states unless the evidence is ``extracted``."""
    stated = F.col("uc1_evidence") == "extracted"

    def when_stated(col: Column) -> Column:
        return F.when(stated, col)

    def state(level: Column, mapping: dict[str, str]) -> Column:
        value = F.coalesce(_mapped(level, mapping), F.lit("not_stated"))
        return F.when(stated, value).otherwise("no_evidence")

    capacity = _level("_est_payment_capacity", "payment_capacity")
    intent = _level("_est_payment_intent", "payment_intent")
    a5, a6 = state(capacity, ABILITY_STATES), state(intent, INTENT_STATES)
    named = (F.col("_amount_named") == 1) | (F.col("_date_named") == 1)
    near = F.col("dcore_promise_near_call_flag")
    promise = F.when(a6.isin(*PAYING) & named, 1 - near).otherwise(0)
    verify = (F.col("a1_state") == "low") & ((a5 == "able") | (a6 == "pays_in_full"))

    def detected(signal: str) -> Column:
        level = _level(f"_est_{signal}", signal)
        return F.coalesce(level == "detected", F.lit(False)).cast("int")

    return {
        "a5_state": a5,
        "a5_capacity_level": when_stated(F.col("_est_payment_capacity")),
        "a5_confidence": when_stated(F.col("_confidence_payment_capacity")),
        "a5_latest_value": when_stated(F.col("_latest_value_payment_capacity")),
        "a5_remark_value": when_stated(F.col("_agent_remark_value_payment_capacity")),
        "a5_supporting_data": when_stated(F.col("_supporting")),
        "a5_reason": when_stated(
            _level("_est_delinquency_reason", "delinquency_reason")
        ),
        "a5_reason_confidence": when_stated(F.col("_reason_confidence")),
        "a6_state": a6,
        "a6_intent_level": when_stated(F.col("_est_payment_intent")),
        "a6_confidence": when_stated(F.col("_confidence_payment_intent")),
        "a6_latest_value": when_stated(F.col("_latest_value_payment_intent")),
        "a6_remark_value": when_stated(F.col("_agent_remark_value_payment_intent")),
        "a6_period": when_stated(_level("_est_payment_period", "payment_period")),
        "a6_amount_named_flag": when_stated(F.col("_amount_named")),
        "a6_date_named_flag": when_stated(F.col("_date_named")),
        "a6_plan_named_flag": when_stated(F.col("_plan_named")),
        "stated_dispute": when_stated(
            F.coalesce(_level("_est_dispute", "dispute"), F.lit("none"))
        ),
        "stated_request_flag": when_stated(detected("request")),
        "stated_fraud_flag": when_stated(detected("fraudulent_customer")),
        "stated_promise_unlogged_flag": when_stated(promise),
        "verify_stated_ability_flag": when_stated(verify.cast("int")),
    }


def build_uc1_stated(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    export: DataFrame,
    conversations: DataFrame,
    a1_ability: DataFrame,
    model_id: str,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> DataFrame:
    """One row per observation: the evidence status, both stated axes with UC1's
    confidence and values, the reason, period, repayment, dispute, request and fraud
    details, the two flags and the conversation count."""
    require_columns(a1_ability, [*GRAIN, "a1_state"], "A1 ability")
    month = scored_month(persona_end_date, uc1_month_end)
    scored = (
        latest_month(obs_base, month)
        .join(_wide(export), "cif_id", "left")
        .join(conversations, list(GRAIN), "left")
        .join(a1_ability.select(*GRAIN, "a1_state"), list(GRAIN), "left")
        .withColumn("uc1_evidence", _evidence())
    )
    scored = scored.select(
        *scored.columns,
        *[col.alias(name) for name, col in _stated_columns().items()],
    )
    out = obs_base.select(*GRAIN).join(
        scored.select(*GRAIN, *_OUTPUT), list(GRAIN), "left"
    )
    name = f"uc1_stated [{model_id}]"
    for col in ("uc1_evidence", "a5_state", "a6_state", "stated_promise_unlogged_flag"):
        log_latest_month(out, col, name, month)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/uc1_stated/pipeline.py`
action: replace · base sha256 `816ae16bc0184494bce34abb15c20427b465f58b6f5f911403b0809c608fe4e4` · base trailing newline: yes · new sha256 `561c44bb2aa5c3b47f63e95287fb3b09a4bd77a795be8ab4b2b6b952dfed2f2f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The UC1 stated-block pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ conversation evidence ──► crx_<p>_uc1_conversation_signals
                      │  (crx_uc1_metadata, crx_uc1_extracted_signals,       │
                      │   crx_uc1_signal_level_conflicts)                    │
                      └─ stated block ◄──────────────────────────────────────┘
                         (crx_uc1_simple_signal_aggregation) ──► crx_<p>_uc1_stated

UC1's outputs are read as they are, from the shared file store (``catalog_crx.yml``).
Needs, for the model_id: the observation base.
"""

from kedro.pipeline import Pipeline, node

from .classify import build_uc1_stated
from .signals import build_uc1_conversation_signals

TAGS = ["crx_persona", "crx", "uc1", "stated"]


def create_uc1_pipeline(product: str, output: str) -> Pipeline:
    """The conversation-evidence node and the state node of ``product``'s UC1 stated
    block, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_uc1"
    end_date = "params:crx_persona.persona_end_date"
    return Pipeline(
        [
            node(
                func=build_uc1_conversation_signals,
                inputs={
                    "obs_base": obs,
                    "metadata": "crx_uc1_metadata",
                    "extracted_signals": "crx_uc1_extracted_signals",
                    "signal_level_conflicts": "crx_uc1_signal_level_conflicts",
                    "persona_end_date": end_date,
                },
                outputs=f"{prefix}_conversation_signals",
                name=f"build_{prefix}_conversation_signals",
                tags=TAGS,
            ),
            node(
                func=build_uc1_stated,
                inputs={
                    "obs_base": obs,
                    "aggregation": "crx_uc1_simple_signal_aggregation",
                    "conversations": f"{prefix}_conversation_signals",
                    "model_id": "params:model_id",
                    "persona_end_date": end_date,
                },
                outputs=output,
                name=f"build_{prefix}_stated",
                tags=TAGS,
            ),
        ],
    )
`````

New:

`````python
"""The UC1 stated-block pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ conversations, DCORE promises ──► crx_<p>_uc1_conversation_signals
                      │  (crx_uc1_metadata, crx_<p>_a3_promise_events)          │
                      └─ stated block ◄─────────────────────────────────────────┘
                         (crx_uc1_customer_signal_export, crx_<p>_a1_ability) ──► crx_<p>_uc1_stated

UC1's outputs are read as they are, from the shared file store (``catalog_crx.yml``).
Scored month: ``uc1_month_end``, else ``crx_persona.persona_end_date``.
Needs, for the model_id: the observation base, A1 ability and A3 promise events.
"""

from kedro.pipeline import Pipeline, node

from .classify import build_uc1_stated
from .signals import build_uc1_conversation_signals

TAGS = ["crx_persona", "crx", "uc1", "stated"]


def create_uc1_pipeline(product: str, output: str) -> Pipeline:
    """The conversation node and the state node of ``product``'s UC1 stated block,
    written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_uc1"
    dates = {
        "persona_end_date": "params:crx_persona.persona_end_date",
        "uc1_month_end": "params:uc1_month_end",
    }
    return Pipeline(
        [
            node(
                func=build_uc1_conversation_signals,
                inputs={
                    "obs_base": obs,
                    "metadata": "crx_uc1_metadata",
                    "promise_events": f"crx_{product}_a3_promise_events",
                    **dates,
                },
                outputs=f"{prefix}_conversation_signals",
                name=f"build_{prefix}_conversation_signals",
                tags=TAGS,
            ),
            node(
                func=build_uc1_stated,
                inputs={
                    "obs_base": obs,
                    "export": "crx_uc1_customer_signal_export",
                    "conversations": f"{prefix}_conversation_signals",
                    "a1_ability": f"crx_{product}_a1_ability",
                    "model_id": "params:model_id",
                    **dates,
                },
                outputs=output,
                name=f"build_{prefix}_stated",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/uc1_stated/signals.py`
action: replace · base sha256 `802e6c9e981032a36cef7658da60549a6196d1c1bc16979fa990440f73d683e9` · base trailing newline: yes · new sha256 `1f67af1216d5e25711b644c391cc0ae906dbf0c8a7ffa03b64c294e9ace1aab2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""UC1 conversation evidence at (account_id, observation_date), shared by CC and RL.

UC1 is another team's signal extraction from call transcripts. Its outputs are read as
they are, from the shared file store: ``metadata`` (every conversation), the extraction
ledger ``extracted_signals`` (only ``model_version``) and the per-conversation grid
``timelines/signal_level_conflicts`` (the level each conversation detected).

Conversations UC1 extracted only in the ``legacy`` format are dropped everywhere (UC1
reads no level from them). Per customer (``cif_id``, all accounts) this counts the
remaining conversations dated strictly before the observation date: all of them, the
extracted ones, and those that detected each capacity and intent level or named an
amount or a date. Only the month of
``crx_persona.persona_end_date`` is scored: UC1's customer table has no date, so earlier
months cannot be read point in time.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, require_columns, scoped, string_key

CAPACITY_LEVELS = ("none", "partial", "full")
INTENT_LEVELS = ("no_payment", "with_delay", "partial", "payback_full")
LEGACY_MODEL_VERSION = "legacy"


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The ``obs_base`` rows of the month of ``persona_end_date``, with a string
    ``cif_id`` join key."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month).select(
        *GRAIN, string_key(obs_base, "cif_id").alias("cif_id")
    )


def _conversations(
    base: DataFrame, metadata: DataFrame, extracted: DataFrame, grid: DataFrame
) -> DataFrame:
    """One row per conversation of the base's customers, legacy-only extractions
    dropped: ``cif_id``, its date, ``_extracted`` (1 = extracted in the current format,
    NULL = not extracted) and what it detected (``_capacity``, ``_intent``, ``_amount``,
    ``_date``)."""
    meta = scoped(
        metadata.select(
            string_key(metadata, "cif_id").alias("cif_id"),
            "conversationid",
            F.to_date("conversationstart").alias("_conv_date"),
        ),
        base,
        "cif_id",
    )
    is_current = F.coalesce(F.col("model_version") != LEGACY_MODEL_VERSION, F.lit(True))
    ledger = extracted.groupBy("conversationid").agg(
        F.max(is_current.cast("int")).alias("_current")
    )
    signal, value = F.col("signal"), F.col("value")
    slot = F.split(value, ":").getItem(0)
    specifics = signal == "repayment_specifics"
    detected = (
        grid.filter(F.col("observation") == "detected")
        .groupBy("conversationid")
        .agg(
            F.max(F.when(signal == "payment_capacity", value)).alias("_capacity"),
            F.max(F.when(signal == "payment_intent", value)).alias("_intent"),
            F.max(F.when(specifics & (slot == "amount_mentioned"), 1)).alias("_amount"),
            F.max(F.when(specifics & (slot == "date_specific"), 1)).alias("_date"),
        )
    )
    return (
        meta.join(ledger, "conversationid", "left")
        .filter(F.coalesce(F.col("_current"), F.lit(1)) == 1)
        .withColumnRenamed("_current", "_extracted")
        .join(detected, "conversationid", "left")
    )


def build_uc1_conversation_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    metadata: DataFrame,
    extracted_signals: DataFrame,
    signal_level_conflicts: DataFrame,
    persona_end_date: str,
) -> DataFrame:
    """Conversation counts per latest-month observation whose customer has any UC1
    conversation (earlier or later): ``uc1_conversations_n``, ``uc1_extracted_n``,
    the last conversation / extracted dates, ``uc1_after_obs_flag``
    (an extracted conversation on or after the observation date), ``amount_named_flag``,
    ``date_named_flag`` and one ``capacity_<level>_n`` / ``intent_<level>_n`` per level.
    """
    require_columns(
        metadata, ["conversationid", "cif_id", "conversationstart"], "UC1 metadata"
    )
    require_columns(
        extracted_signals, ["conversationid", "model_version"], "UC1 extracted_signals"
    )
    require_columns(
        signal_level_conflicts,
        ["conversationid", "signal", "value", "observation"],
        "UC1 signal_level_conflicts",
    )
    base = latest_month(obs_base, persona_end_date)
    conversations = _conversations(
        base, metadata, extracted_signals, signal_level_conflicts
    )

    before = F.col("_conv_date") < F.col("observation_date")
    extracted = F.col("_extracted").isNotNull()

    def count(cond: Column) -> Column:
        return F.sum(F.when(before & cond, 1).otherwise(0))

    def flag(col: str) -> Column:
        return F.coalesce(F.max(F.when(before, F.col(col))), F.lit(0))

    return (
        base.join(conversations, on="cif_id")
        .groupBy(*GRAIN)
        .agg(
            count(F.lit(True)).alias("uc1_conversations_n"),
            count(extracted).alias("uc1_extracted_n"),
            F.max(F.when(before, F.col("_conv_date"))).alias(
                "uc1_last_conversation_date"
            ),
            F.max(F.when(before & extracted, F.col("_conv_date"))).alias(
                "uc1_last_extracted_date"
            ),
            F.max(F.when(~before & extracted, 1).otherwise(0)).alias(
                "uc1_after_obs_flag"
            ),
            flag("_amount").alias("amount_named_flag"),
            flag("_date").alias("date_named_flag"),
            *[
                count(F.col("_capacity") == level).alias(f"capacity_{level}_n")
                for level in CAPACITY_LEVELS
            ],
            *[
                count(F.col("_intent") == level).alias(f"intent_{level}_n")
                for level in INTENT_LEVELS
            ],
        )
    )
`````

New:

`````python
"""UC1 conversations and DCORE promises at the UC1 month, shared by CC and RL.

Per observation of the scored month (``scored_month``): the customer's UC1 conversations
(``crx_uc1_metadata``, every account of the ``cif_id``) dated strictly before the
observation date, the date of the last one, and ``dcore_promise_near_call_flag``: 1 when
an A3 promise event of any of the customer's accounts in the base is alive within
``NEAR_CALL_DAYS`` days of that call (it starts on or before the call + 7 days and its
cutoff is on or after the call - 7 days), 0 when none is, NULL without a call. Events
dated after the observation date are not used.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, require_columns, scoped, string_key

NEAR_CALL_DAYS = 7


def scored_month(persona_end_date: str, uc1_month_end: str | None) -> str:
    """The month UC1 is scored at: ``uc1_month_end`` when set, else the persona end
    date."""
    return str(uc1_month_end or persona_end_date)


def latest_month(obs_base: DataFrame, month_date: str) -> DataFrame:
    """The ``obs_base`` rows of the month of ``month_date``, with a string ``cif_id``
    join key."""
    month = F.trunc(F.lit(str(month_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month).select(
        *GRAIN, string_key(obs_base, "cif_id").alias("cif_id")
    )


def build_uc1_conversation_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    metadata: DataFrame,
    promise_events: DataFrame,
    persona_end_date: str,
    uc1_month_end: str | None,
) -> DataFrame:
    """``GRAIN`` of the scored month's observations whose customer had a UC1
    conversation before the observation date: ``uc1_conversations_n``,
    ``uc1_last_conversation_date`` and ``dcore_promise_near_call_flag``."""
    require_columns(
        metadata, ["conversationid", "cif_id", "conversationstart"], "UC1 metadata"
    )
    require_columns(
        promise_events,
        ["account_id", "event_date", "promise_cutoff"],
        "A3 promise events",
    )
    base = latest_month(obs_base, scored_month(persona_end_date, uc1_month_end))
    meta = scoped(
        metadata.select(
            string_key(metadata, "cif_id").alias("cif_id"),
            F.to_date("conversationstart").alias("_conv_date"),
        ),
        base,
        "cif_id",
    )
    calls = (
        base.join(meta, "cif_id")
        .filter(F.col("_conv_date") < F.col("observation_date"))
        .groupBy(*GRAIN, "cif_id")
        .agg(
            F.count(F.lit(1)).alias("uc1_conversations_n"),
            F.max("_conv_date").alias("uc1_last_conversation_date"),
        )
    )
    events = (
        base.select("cif_id", F.col("account_id").alias("_event_account"))
        .distinct()
        .join(
            promise_events.select(
                F.col("account_id").alias("_event_account"),
                F.to_date("event_date").alias("_event_date"),
                F.to_date(F.coalesce("promise_cutoff", "event_date")).alias("_cutoff"),
            ),
            "_event_account",
        )
        .select("cif_id", "_event_date", "_cutoff")
    )
    last = F.col("uc1_last_conversation_date")
    near = (
        (F.col("_event_date") <= F.date_add(last, NEAR_CALL_DAYS))
        & (F.col("_cutoff") >= F.date_sub(last, NEAR_CALL_DAYS))
        & (F.col("_event_date") <= F.col("observation_date"))
    )
    return (
        calls.join(events, "cif_id", "left")
        .groupBy(*GRAIN, "uc1_conversations_n", "uc1_last_conversation_date")
        .agg(F.max(F.when(near, 1).otherwise(0)).alias("dcore_promise_near_call_flag"))
    )
`````

### FILE: `conf/base/catalog/catalog_tmp_uc1_cov.yml`
action: delete · base sha256 `5f3c910d1e6b8c2513416129c36998df1f91dac05d448ee3b41878f0b074bf84` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# Temporary (UC1 quick coverage check); removed in the cleanup.
# The evidence table holds one folder per snapshot_date: read the one of the persona end date (globals).
crx_uc1_customer_signal_export:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/customer_signal_export"

crx_uc1_proposer_level_observations:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/file_store/current/outputs/timelines/proposer_level_observations/snapshot_date=${globals:crx_persona.persona_end_date}"
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
Clean up after mirror bundle 31_uc1_signal_export.md, on the bundle's branch.
- Remove `src/enbd_collections/pipelines/crx_persona/b31_check.py`, `conf/base/catalog/catalog_tmp_b31_check.yml`, and from `pipeline_registry.py` the `b31_check` import and the four `crx_*_b31_*` entries.
- HDFS, for each model_id: `hdfs dfs -rm -r <persona path>/<model_id>/<persona folder>/b31_check` (path from `catalog_tmp_b31_check.yml`).
- Remove the tracked folder `tmp_validation/uc1_cov/` (quick coverage check, finished). Keep `tmp_validation/uc1_full/` and `catalog_tmp_uc1_full.yml`: they rerun on the full UC1 data.
- Remove `data/input/mirror_bundles/`.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
