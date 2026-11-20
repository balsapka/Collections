# Mirror bundle 30 — Remove the spell tables and their dead code

apply_bundle version: 7 · built 2026-11-20 from `36cf30d..b7d04c4` · source: 0 added, 6 replaced, 9 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/spell_tables_removed
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/30_spell_tables_removed.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '30_spell_tables_removed.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/30_spell_tables_removed.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go, and fix what it finds before committing:

1. **Catalog and registry.** List every top-level key the apply removed from `conf/base/catalog/catalog_crx.yml` and `src/enbd_collections/pipeline_registry.py` compared with the last commit. Expected: exactly `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine`, `crx_cc_limits` (catalog) and the three registry entries `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine`. Put back anything else that went missing.
2. **Leftover files and references.** Delete whatever is left in `crx_persona/cc_spell/`, `crx_persona/rl_spell_table/` and `crx_persona/rl_a4_spine/` (e.g. an `__init__.py` the mirror does not have) and the folders. Search the whole repo (src, conf, tests, notebooks) for `cc_spell`, `rl_spell_table`, `rl_a4_spine`, `_spine_utils`, `join_spine_to_spell`, `build_cc_limits`, `crx_cc_limits`, `crx_cc_spell_table`, `crx_rl_spell_table`. Delete tests that only cover the removed code; fix any other reader, and list what you changed.
3. `kedro registry list` runs, without the three removed pipelines; `python -c "import enbd_collections.pipeline_registry"` imports.
4. The crx_persona tests pass; black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Mirror bundle 30: Remove the spell tables and their dead code" && git push -u origin feature/spell_tables_removed
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/30_spell_tables_removed.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/spell_tables_removed && git pull
```

No persona output changes, so there is no comparison run.

**Step 7.** In PROD, after the pull, confirm the persona pipelines still resolve (no data is read):

```bash
kedro registry list | grep crx_
```

Paste back the list. Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Removes the spell (T0) tables and the code that only they fed. Every axis is keyed on `(account_id, observation_date)` through the obs base, and A3 reads the episode start from A4 (`months_before_spell`), so nothing reads the spell tables any more (DESIGN_REVIEW §6, D5, steps 6–7). **Apply on top of bundles 25–29 and their cleanups.** No persona output changes.

Removed:
- packages `crx_persona/cc_spell/`, `crx_persona/rl_spell_table/`, `crx_persona/rl_a4_spine/` and `crx_persona/_spine_utils.py`;
- the node `build_crx_cc_limits` in `cc_raw_extract` (credit limits on the spell window; no reader);
- catalog entries `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine`, `crx_cc_limits`;
- registry entries `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine` and their imports.

Kept: `crx_cc_full_history` / `crx_rl_full_history` (A4 reads them) and `cc_raw_extract`'s account windows, transactions, balance and billing (A3 reads them). Comments that still described T0 windows now describe what the code does.

Tested in the mirror: the golden harness (`checks/refactor_golden.py`) reproduces every persona output of the previous head; smoke import check; black, ruff and pylint clean on the touched files.

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
| replace | `conf/base/parameters/parameters_crx_persona.yml` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/_spine_utils.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_spell/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_spell/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_spell_table/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_spell_table/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_spell_table/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `bce375402b7d490077c245dffa548b19a9408b5a325101ff0277c0bb2f954933` · base trailing newline: yes · new sha256 `4ec7791f15b8b4ca55bd4366a1bd3f8c03c527e3978ac113e14de960c48bd527` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the T03+ persona-axis pipeline live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- T04c: T0-scoped CC raw DDI intermediates ----------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions,
# crx_cc_balance and crx_cc_billing.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.
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

crx_cc_limits:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_limits"
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

# -- T03: Delinquency-spell table (CC) ----------------------------------------
# Grain: (account_id, spell_id). One row per delinquency episode.
# T0 = spell anchor for all A4 features.
# Built from raw_stg_billing (no date/DLQ filter; leftsemi-scoped to cc_spine).
# model_id-namespaced so cc_60_180 and cc_180_plus runs do not overwrite each other.
crx_cc_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_spell_table"
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
# Grain: (account_id, month_end_date). Full pre-delinquency monthly history for
# all RL spine accounts. Source: int_loan_master (month-end snapshots).
# No date window — full history required for T0 identification (RL-B2) and
# pre-T0 A4 lookback (RL-A4-2). Date filter applied downstream in crx_rl_a4_spine.
crx_rl_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history"
  save_args:
    mode: overwrite

# ── RL Foundation (RL-B2) ───────────────────────────────────────────────────
# Grain: one row per account_id. T0 anchor table with first delinquency onset
# date and pre-T0 behavioural metadata. spell_id=1 / spell_end=NULL adapter
# makes this compatible with join_spine_to_spell() (R18).
crx_rl_spell_table:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_spell_table"
  save_args:
    mode: overwrite

# ── RL A4 Spine (structural — superseded CASA/EMI classifier removed) ───────

# Spine-grain structural projection (windowed to persona_start_date / persona_end_date).
# Grain: (account_id, observation_date). Carries cif_id, spell_id, t0 (sourced from
# crx_rl_spell_table) — no classification columns. Built by the rl_a4_spine pipeline.
# Filter point per TASKS_RL.md.
crx_rl_a4_spine:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine"
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

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `d9ca974faf8c9e332925ec3e5bb8cc90ba8bdea3114a3cd2060736023c6e0b00` · base trailing newline: yes · new sha256 `082b2ad86c5dd804c60fd19233fe03ccd0599d12e9ac885457c92ce1f585d6f4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
##################################################
# CRX PERSONA PIPELINE CONFIGURATION
##################################################
# Evaluation window for the RL persona pipeline.
# These dates control which spine rows are included in persona outputs
# (crx_rl_a4_spine and all downstream assets).
#
# Filter is applied at the spine-join step (RL-A4-2), NOT on raw history
# or T0 tables — full history is required for T0 identification and
# pre-T0 feature lookback.
#
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
action: replace · base sha256 `f3a2c8654b14ef782295eb4c52f3677cbd113fafcf01a226dceff378695ba918` · base trailing newline: yes · new sha256 `581be2c57723cc6c8bfe7fda5840dcb2f2215c50a510d4d85a5d4bae8c02efa4` · new trailing newline: yes

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
from enbd_collections.pipelines.crx_persona import cc_spell as crx_cc_spell
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
    rl_spell_table as crx_rl_spell_table,
)
from enbd_collections.pipelines.crx_persona import rl_a4_spine as crx_rl_a4_spine
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
        "crx_cc_spell_table": crx_cc_spell.create_pipeline(),
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
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/nodes.py`
action: replace · base sha256 `a64ea101d8c7d11194c9a41748cc2326892b4520552b4255225d498aaae3c039` · base trailing newline: yes · new sha256 `10b32f8941f8dd6fae3b4a968d6776e39c8e12c89d4e76421a99ea3471335237` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A4 — deterioration state for credit cards (wrappers on ``_dpd_journey``).

Node 1 build_cc_dpd_sequences     crx_cc_full_history -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration  crx_cc_dpd_sequences + cc_spine
                                  -> crx_cc_a4_deterioration
Run: ``kedro run --pipeline=crx_cc_a4_deterioration`` (needs crx_cc_full_history).

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210,
9 = 210+. History before ``dpd_journey.cc_history_floor_date`` (default 2024-01-01:
the billing history is unreliable before it, temporary) is not used; accounts with
older history are flagged cropped. ``cc_180_plus`` reads
``cc_history_floor_date_180_plus`` (same default) instead, because the journey of most
long charged-off accounts starts before the shared floor and leaves them "unknown";
override that key alone to relax the floor at 180+ (conformance D5).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns
from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

# Same value as cc_spell's _RESTRUCTURE_DLQ_THRESHOLD: an account whose earliest
# billing row is already at this dlq_bucket or above was opened mid-delinquency by a
# restructure, not merely cut off by the data depth (conformance D2).
_RESTRUCTURE_DLQ_THRESHOLD = 4


def _restructure_blind_spot(history: DataFrame) -> DataFrame:
    """``account_id``, ``restructure_blind_spot_flag``: 1 when the account's earliest
    dated row is already at ``_RESTRUCTURE_DLQ_THRESHOLD`` or worse."""
    # Earliest dated row; on a same-date tie the worst bucket wins, because the bucket
    # is negated so the smallest struct is that row.
    first = F.min(F.struct("obs_date", (-F.col("dlq_bucket")).alias("neg_bucket")))
    return (
        history.filter(F.col("dlq_bucket").isNotNull())
        .groupBy("account_id")
        .agg(first.alias("_first"))
        .select(
            "account_id",
            (-F.col("_first.neg_bucket") >= _RESTRUCTURE_DLQ_THRESHOLD)
            .cast("int")
            .alias("restructure_blind_spot_flag"),
        )
    )


def build_cc_dpd_sequences(
    crx_cc_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per CC account: _dpd_journey.build_dpd_sequences with the restructure
    blind-spot flag of ``_restructure_blind_spot``."""
    require_columns(
        crx_cc_full_history,
        ["account_id", "billing_date", "dlq_bucket"],
        "crx_cc_full_history",
    )
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket"
    )

    restructure = _restructure_blind_spot(history)
    return build_dpd_sequences(
        history, CC, journey_params(crx_persona, CC, model_id), restructure=restructure
    )


def build_cc_a4_deterioration(
    crx_cc_dpd_sequences: DataFrame,
    cc_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, cc_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_cc_dpd_sequences. cc_spine is already scoped to the model_id's DLQ band, so no
    segment filter is applied here. See _dpd_journey.build_deterioration.
    """
    require_columns(cc_spine, ["contract_id", "observation_date"], "cc_spine")
    spine = cc_spine.select(
        F.col("contract_id").alias("account_id"), "observation_date"
    )
    return build_deterioration(
        crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC, model_id), spine
    )
`````

New:

`````python
"""CC A4 — deterioration state for credit cards (wrappers on ``_dpd_journey``).

Node 1 build_cc_dpd_sequences     crx_cc_full_history -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration  crx_cc_dpd_sequences + cc_spine
                                  -> crx_cc_a4_deterioration
Run: ``kedro run --pipeline=crx_cc_a4_deterioration`` (needs crx_cc_full_history).

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210,
9 = 210+. History before ``dpd_journey.cc_history_floor_date`` (default 2024-01-01:
the billing history is unreliable before it, temporary) is not used; accounts with
older history are flagged cropped. ``cc_180_plus`` reads
``cc_history_floor_date_180_plus`` (same default) instead, because the journey of most
long charged-off accounts starts before the shared floor and leaves them "unknown";
override that key alone to relax the floor at 180+ (conformance D5).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns
from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

# An account whose earliest billing row is already at this dlq_bucket or above was
# opened mid-delinquency by a restructure, not merely cut off by the data depth
# (conformance D2).
_RESTRUCTURE_DLQ_THRESHOLD = 4


def _restructure_blind_spot(history: DataFrame) -> DataFrame:
    """``account_id``, ``restructure_blind_spot_flag``: 1 when the account's earliest
    dated row is already at ``_RESTRUCTURE_DLQ_THRESHOLD`` or worse."""
    # Earliest dated row; on a same-date tie the worst bucket wins, because the bucket
    # is negated so the smallest struct is that row.
    first = F.min(F.struct("obs_date", (-F.col("dlq_bucket")).alias("neg_bucket")))
    return (
        history.filter(F.col("dlq_bucket").isNotNull())
        .groupBy("account_id")
        .agg(first.alias("_first"))
        .select(
            "account_id",
            (-F.col("_first.neg_bucket") >= _RESTRUCTURE_DLQ_THRESHOLD)
            .cast("int")
            .alias("restructure_blind_spot_flag"),
        )
    )


def build_cc_dpd_sequences(
    crx_cc_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per CC account: _dpd_journey.build_dpd_sequences with the restructure
    blind-spot flag of ``_restructure_blind_spot``."""
    require_columns(
        crx_cc_full_history,
        ["account_id", "billing_date", "dlq_bucket"],
        "crx_cc_full_history",
    )
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket"
    )

    restructure = _restructure_blind_spot(history)
    return build_dpd_sequences(
        history, CC, journey_params(crx_persona, CC, model_id), restructure=restructure
    )


def build_cc_a4_deterioration(
    crx_cc_dpd_sequences: DataFrame,
    cc_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, cc_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_cc_dpd_sequences. cc_spine is already scoped to the model_id's DLQ band, so no
    segment filter is applied here. See _dpd_journey.build_deterioration.
    """
    require_columns(cc_spine, ["contract_id", "observation_date"], "cc_spine")
    spine = cc_spine.select(
        F.col("contract_id").alias("account_id"), "observation_date"
    )
    return build_deterioration(
        crx_cc_dpd_sequences, CC, journey_params(crx_persona, CC, model_id), spine
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py`
action: replace · base sha256 `985def5b2e78c79474f7d5b53eadd17d176e76a1652707cd9cf7d360b9352de6` · base trailing newline: yes · new sha256 `93253830ef46af0d53324034a75e983d072fe5be14ac61a810b984ca63719c38` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC raw extract nodes: Way4 extracts scoped to each account's window.

    build_cc_transactions : transaction history with the ``prm_cc`` derivations (A3
                            payments).
    build_cc_balance      : minimum_due / overdue buckets / total_due (A3 dues).
    build_cc_billing      : billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).
    build_cc_limits       : credit-limit snapshots pivoted by type_code, on its own
                            spell-table window (no persona reader at present).

The first three read ``crx_cc_acct_windows`` (``build_cc_acct_windows`` in
``cc_a3_payment_credibility.nodes``) and prune raw partitions with
``_window_utils.prune_by_edp_load_date``. ``contract_idt`` is cast double -> long at the
raw boundary; transactions keep primary_entry_idt != 0 and org == 100.
"""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import (
    derive_billing_amounts,
    derive_overdue_buckets,
)
from enbd_collections.nodes.utils.config import (
    POST_BLOCK_X_SENTINEL_DATE,
    TXN_CATEGORIES,
)
from enbd_collections.pipelines.crx_persona._common import require_columns
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    require_columns(
        acct_windows, ["account_id", "acct_start", "acct_end"], "crx_cc_acct_windows"
    )
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC transactions in each account's window, with ``txn_category`` (``prm_cc``'s
    ``TXN_CATEGORIES`` by ``txn_code``; NULL for an unrecognised code),
    ``is_international`` (``DOMESTIC=N`` in ``add_info``) and ``is_post_block_x_fee``
    (the Block-W fee-accrual artefacts, as in ``stg_transaction.build()``, which A3 must
    not read as payments).

    Returns::

        contract_id (long), observation_date (date, banking date), direction (int),
        txn_amount_aed (double), txn_description (string),
        merchant_category_code (int), is_international (int),
        txn_category (string), is_post_block_x_fee (int)
    """
    require_columns(
        raw_transaction,
        [
            "primary_entry_idt",
            "org",
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "settl_amount",
            "direction",
            "txn_code",
            "txn_description",
            "add_info",
            "trans_mcc",
            "trans_date",
            "card_idt",
            "service_class",
        ],
        "raw_transaction",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        .filter(F.col("primary_entry_idt") != 0)
        .filter(F.col("org") == 100)
    )
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # NULL for unrecognised codes: excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # System-generated fee accruals posted after collector Block W carry a sentinel
    # trans_date; flagged so A3 Dimension B/C never count them as a payment.
    sentinel = F.lit(POST_BLOCK_X_SENTINEL_DATE).cast(DateType())
    df = df.withColumn(
        "is_post_block_x_fee",
        F.when(
            (F.col("trans_date").cast(DateType()) == sentinel)
            & (F.col("card_idt") == 0)
            & (F.col("settl_amount") == 0)
            & (F.col("service_class") == "I"),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
        F.col("is_post_block_x_fee").cast("int"),
    ).distinct()


def build_cc_limits(
    raw_stg_limit: DataFrame,
    crx_cc_spell_table: DataFrame,
) -> DataFrame:
    """CC credit-limit snapshots (``FIN_LIMIT`` and ``AVAILABLE`` pivoted by type_code)
    in the window [min(t0) − 12 months, max(t0)] of each account's non-censored spells;
    it does not read ``crx_cc_acct_windows``, whose forward edge is the observation
    base.

    Returns::

        contract_id (long), observation_date (date),
        credit_limit (double), available_limit (double)
    """
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)

    acct_windows = (
        spell.groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("acct_start"),
            F.trunc(F.max("t0"), "month").alias("acct_end"),
        )
        .select(
            F.col("account_id").alias("contract_idt"),
            "acct_start",
            "acct_end",
        )
    )

    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped.filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # max(): the highest limit and the highest available amount win on a tie
        .groupBy("contract_idt", "banking_date")
        .pivot("type_code", ["FIN_LIMIT", "AVAILABLE"])
        .agg(F.max("amount"))
        .withColumnRenamed("FIN_LIMIT", "credit_limit")
        .withColumnRenamed("AVAILABLE", "available_limit")
    )

    return pivoted.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("credit_limit").cast("double"),
        F.col("available_limit").cast("double"),
    )


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC balance history in each account's window: the billing amounts and overdue
    buckets of ``prm_cc.derive_billing_amounts`` / ``derive_overdue_buckets`` per
    banking date (Way4 stores credit balances as negative; both flip the sign).

    Returns::

        contract_id (long), observation_date (date), minimum_due (double),
        stmt_balance (double), total_due (double),
        overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    require_columns(
        raw_stg_balance,
        ["contract_idt", "banking_date", "edp_load_date"],
        "raw_stg_balance",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = prune_by_edp_load_date(
        raw_stg_balance, crx_cc_acct_windows
    ).withColumn("banking_date", F.col("banking_date").cast(DateType()))
    scoped_balance = scope_to_acct_window(scoped_balance, acct_windows, "banking_date")

    billing_amounts = derive_billing_amounts(scoped_balance, raw_stg_account_group)
    overdue_buckets = derive_overdue_buckets(scoped_balance, raw_stg_account_group)

    combined = billing_amounts.join(
        overdue_buckets, on=["contract_idt", "banking_date"], how="left"
    )

    select_cols = [
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("minimum_due").cast("double"),
        F.col("stmt_balance").cast("double"),
        F.col("total_due").cast("double"),
    ] + [
        F.col(f"overdue_ovd_{i:02d}").cast("double").alias(f"overdue_bucket_{i:02d}")
        for i in range(1, 9)
    ]

    return combined.select(*select_cols)


def build_cc_billing(
    raw_stg_billing: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC billing-cycle headers in each account's window. ``next_billing_date`` is the
    next statement of the contract (NULL for its latest cycle). A payment belongs to the
    cycle ``(billing_date, next_billing_date]``, not ``(billing_date, due_date]``: the
    due date falls about 5 days before the next statement, and late payments would
    otherwise be dropped. ``dlq_level_m`` is Way4's per-cycle bucket
    (``BS_PMT_CYCLE_DUE`` in ``add_info``; NULL when blank).

    Returns::

        contract_id (long), observation_date (date, = billing_date),
        due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    require_columns(
        raw_stg_billing,
        ["contract_idt", "billing_date", "edp_load_date", "due_date", "add_info"],
        "raw_stg_billing",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    pruned = prune_by_edp_load_date(raw_stg_billing, crx_cc_acct_windows)
    scoped = (
        scope_to_acct_window(pruned, acct_windows, "billing_date")
        .withColumn("billing_date", F.col("billing_date").cast(DateType()))
        .withColumn("due_date", F.col("due_date").cast(DateType()))
        .withColumn(
            "dlq_level_m",
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1).cast(
                "int"
            ),
        )
        .select("contract_idt", "billing_date", "due_date", "dlq_level_m")
        .distinct()
    )

    next_billing_window = Window.partitionBy("contract_idt").orderBy("billing_date")
    with_next = scoped.withColumn(
        "next_billing_date", F.lead("billing_date").over(next_billing_window)
    )

    return with_next.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("billing_date").alias("observation_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
        F.col("dlq_level_m"),
    )
`````

New:

`````python
"""CC raw extract nodes: Way4 extracts scoped to each account's window.

    build_cc_transactions : transaction history with the ``prm_cc`` derivations (A3
                            payments).
    build_cc_balance      : minimum_due / overdue buckets / total_due (A3 dues).
    build_cc_billing      : billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).

All three read ``crx_cc_acct_windows`` (``build_cc_acct_windows`` in
``cc_a3_payment_credibility.nodes``) and prune raw partitions with
``_window_utils.prune_by_edp_load_date``. ``contract_idt`` is cast double -> long at the
raw boundary; transactions keep primary_entry_idt != 0 and org == 100.
"""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import (
    derive_billing_amounts,
    derive_overdue_buckets,
)
from enbd_collections.nodes.utils.config import (
    POST_BLOCK_X_SENTINEL_DATE,
    TXN_CATEGORIES,
)
from enbd_collections.pipelines.crx_persona._common import require_columns
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    require_columns(
        acct_windows, ["account_id", "acct_start", "acct_end"], "crx_cc_acct_windows"
    )
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC transactions in each account's window, with ``txn_category`` (``prm_cc``'s
    ``TXN_CATEGORIES`` by ``txn_code``; NULL for an unrecognised code),
    ``is_international`` (``DOMESTIC=N`` in ``add_info``) and ``is_post_block_x_fee``
    (the Block-W fee-accrual artefacts, as in ``stg_transaction.build()``, which A3 must
    not read as payments).

    Returns::

        contract_id (long), observation_date (date, banking date), direction (int),
        txn_amount_aed (double), txn_description (string),
        merchant_category_code (int), is_international (int),
        txn_category (string), is_post_block_x_fee (int)
    """
    require_columns(
        raw_transaction,
        [
            "primary_entry_idt",
            "org",
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "settl_amount",
            "direction",
            "txn_code",
            "txn_description",
            "add_info",
            "trans_mcc",
            "trans_date",
            "card_idt",
            "service_class",
        ],
        "raw_transaction",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        .filter(F.col("primary_entry_idt") != 0)
        .filter(F.col("org") == 100)
    )
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # NULL for unrecognised codes: excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # System-generated fee accruals posted after collector Block W carry a sentinel
    # trans_date; flagged so A3 Dimension B/C never count them as a payment.
    sentinel = F.lit(POST_BLOCK_X_SENTINEL_DATE).cast(DateType())
    df = df.withColumn(
        "is_post_block_x_fee",
        F.when(
            (F.col("trans_date").cast(DateType()) == sentinel)
            & (F.col("card_idt") == 0)
            & (F.col("settl_amount") == 0)
            & (F.col("service_class") == "I"),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return df.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("direction").cast("int"),
        F.col("settl_amount").cast("double").alias("txn_amount_aed"),
        F.col("txn_description").cast("string"),
        F.col("trans_mcc").cast("int").alias("merchant_category_code"),
        F.col("is_international").cast("int"),
        F.col("txn_category").cast("string"),
        F.col("is_post_block_x_fee").cast("int"),
    ).distinct()


def build_cc_balance(
    raw_stg_balance: DataFrame,
    raw_stg_account_group: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC balance history in each account's window: the billing amounts and overdue
    buckets of ``prm_cc.derive_billing_amounts`` / ``derive_overdue_buckets`` per
    banking date (Way4 stores credit balances as negative; both flip the sign).

    Returns::

        contract_id (long), observation_date (date), minimum_due (double),
        stmt_balance (double), total_due (double),
        overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    require_columns(
        raw_stg_balance,
        ["contract_idt", "banking_date", "edp_load_date"],
        "raw_stg_balance",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = prune_by_edp_load_date(
        raw_stg_balance, crx_cc_acct_windows
    ).withColumn("banking_date", F.col("banking_date").cast(DateType()))
    scoped_balance = scope_to_acct_window(scoped_balance, acct_windows, "banking_date")

    billing_amounts = derive_billing_amounts(scoped_balance, raw_stg_account_group)
    overdue_buckets = derive_overdue_buckets(scoped_balance, raw_stg_account_group)

    combined = billing_amounts.join(
        overdue_buckets, on=["contract_idt", "banking_date"], how="left"
    )

    select_cols = [
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("banking_date").cast(DateType()).alias("observation_date"),
        F.col("minimum_due").cast("double"),
        F.col("stmt_balance").cast("double"),
        F.col("total_due").cast("double"),
    ] + [
        F.col(f"overdue_ovd_{i:02d}").cast("double").alias(f"overdue_bucket_{i:02d}")
        for i in range(1, 9)
    ]

    return combined.select(*select_cols)


def build_cc_billing(
    raw_stg_billing: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """CC billing-cycle headers in each account's window. ``next_billing_date`` is the
    next statement of the contract (NULL for its latest cycle). A payment belongs to the
    cycle ``(billing_date, next_billing_date]``, not ``(billing_date, due_date]``: the
    due date falls about 5 days before the next statement, and late payments would
    otherwise be dropped. ``dlq_level_m`` is Way4's per-cycle bucket
    (``BS_PMT_CYCLE_DUE`` in ``add_info``; NULL when blank).

    Returns::

        contract_id (long), observation_date (date, = billing_date),
        due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    require_columns(
        raw_stg_billing,
        ["contract_idt", "billing_date", "edp_load_date", "due_date", "add_info"],
        "raw_stg_billing",
    )
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    pruned = prune_by_edp_load_date(raw_stg_billing, crx_cc_acct_windows)
    scoped = (
        scope_to_acct_window(pruned, acct_windows, "billing_date")
        .withColumn("billing_date", F.col("billing_date").cast(DateType()))
        .withColumn("due_date", F.col("due_date").cast(DateType()))
        .withColumn(
            "dlq_level_m",
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1).cast(
                "int"
            ),
        )
        .select("contract_idt", "billing_date", "due_date", "dlq_level_m")
        .distinct()
    )

    next_billing_window = Window.partitionBy("contract_idt").orderBy("billing_date")
    with_next = scoped.withColumn(
        "next_billing_date", F.lead("billing_date").over(next_billing_window)
    )

    return with_next.select(
        F.col("contract_idt").alias("contract_id"),  # long
        F.col("billing_date").alias("observation_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
        F.col("dlq_level_m"),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py`
action: replace · base sha256 `292e6baa67bcadd7652a16056abf0cbbe3bf5593d20a2c95f75960bad477bb2f` · base trailing newline: yes · new sha256 `4f5331b2008a3f48298da8be09f1af567625cdd0de2508e9e4eb78d38d204cf5` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: the CC raw extract for A3.

``build_cc_acct_windows`` reads the obs base and A4 (the episode anchor), so this runs
after ``crx_cc_a4_deterioration`` and before ``crx_cc_a3_payment_credibility``. The
transactions, balance and billing extracts read its windows; ``build_cc_limits`` keeps
its own spell-table window.

    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from ..cc_a3_payment_credibility.nodes import build_cc_acct_windows
from .nodes import (
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The account windows and the four extracts."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs={
                    "obs_base": "crx_cc_obs_base",
                    "deterioration": "crx_cc_a4_deterioration",
                    "history_floor_date": "params:cc_a3_history_floor_date",
                },
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs={
                    "raw_transaction": "raw_transaction",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs={
                    "raw_stg_limit": "raw_stg_limit",
                    "crx_cc_spell_table": "crx_cc_spell_table",
                },
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs={
                    "raw_stg_balance": "raw_stg_balance",
                    "raw_stg_account_group": "raw_stg_account_group",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs={
                    "raw_stg_billing": "raw_stg_billing",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: the CC raw extract for A3.

``build_cc_acct_windows`` reads the obs base and A4 (the episode anchor), so this runs
after ``crx_cc_a4_deterioration`` and before ``crx_cc_a3_payment_credibility``. The
transactions, balance and billing extracts read its windows.

    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from ..cc_a3_payment_credibility.nodes import build_cc_acct_windows
from .nodes import (
    build_cc_balance,
    build_cc_billing,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The account windows and the three extracts."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs={
                    "obs_base": "crx_cc_obs_base",
                    "deterioration": "crx_cc_a4_deterioration",
                    "history_floor_date": "params:cc_a3_history_floor_date",
                },
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs={
                    "raw_transaction": "raw_transaction",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs={
                    "raw_stg_balance": "raw_stg_balance",
                    "raw_stg_account_group": "raw_stg_account_group",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs={
                    "raw_stg_billing": "raw_stg_billing",
                    "crx_cc_acct_windows": "crx_cc_acct_windows",
                },
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_spine_utils.py`
action: delete · base sha256 `6e7971bfd62d62cbc4b5286ae37cafd675956e71c27ea9b2fde55d5786593980` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared spine and CIF utilities for crx_persona pipelines.

Used by: cc_a1_ability, cc_a2_locatability, cc_a3_payment_credibility,
rl_a3_payment_credibility.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def join_spine_to_spell(cc_spine: DataFrame, spell_table: DataFrame) -> DataFrame:
    """Join cc_spine to crx_cc_spell_table to obtain spell window columns.

    Uses an equality-only join on ``contract_id == account_id`` so Spark can
    plan a hash/sort-merge join, then applies date-range filters as separate
    post-join steps.  This is more efficient than embedding the date conditions
    inside the ``on=`` clause (which forces a cross-join-with-filter plan).

    Left join preserves all spine rows; spell columns are NULL for spine points
    with no active spell at that observation_date (e.g. new accounts added to
    the spine before the spell table is regenerated).

    Args:
        cc_spine:    Model-id-scoped spine; required cols: contract_id,
            observation_date.
        spell_table: crx_cc_spell_table; required cols: account_id, spell_id,
            t0, spell_end.

    Returns:
        DataFrame with columns:
            account_id       (string)  — alias of contract_id
            observation_date (date)
            spell_id         (int)     — NULL if no active spell
            t0               (date)    — NULL if no active spell
    """
    spine = cc_spine.alias("spine")
    spell = spell_table.select("account_id", "spell_id", "t0", "spell_end").alias(
        "spell"
    )
    return (
        spine.join(
            spell,
            on=F.col("spine.contract_id") == F.col("spell.account_id"),
            how="left",
        )
        .filter(
            F.col("spell.t0").isNull()
            | (F.col("spell.t0") <= F.col("spine.observation_date"))
        )
        .filter(
            F.col("spell.spell_end").isNull()
            | (F.col("spine.observation_date") <= F.col("spell.spell_end"))
        )
        .select(
            F.col("spine.contract_id").alias("account_id"),
            F.col("spine.observation_date"),
            F.col("spell.spell_id"),
            F.col("spell.t0"),
        )
    )


def _build_cif_bridge(contract: DataFrame, client: DataFrame) -> DataFrame:
    """Two-hop bridge: contract_id → cif_id.

    prm_contract holds the link between account/contract numbers and the
    customer CIF.  prm_client carries the canonical cif_id field.

    Returns DataFrame with columns: (contract_id, cif_id).
    """
    return (
        contract.select("contract_id", "client_id")
        .join(
            client.select("client_id", "cif_id"),
            on="client_id",
            how="inner",
        )
        .select("contract_id", "cif_id")
        .dropDuplicates(["contract_id"])
    )


def rl_spine_as_cc_shim(rl_a4_spine: DataFrame) -> "tuple[DataFrame, DataFrame]":
    """Reshape an RL spine into the (cc_spine, spell_table) column contract.

    CC build functions such as build_a3_commitment_signals take a cc_spine +
    spell_table pair and call join_spine_to_spell() internally, which hard-codes
    cc_spine["contract_id"] == spell_table["account_id"]. RL spines use
    account_id (not contract_id) and already carry a broadcast spell_id/t0 per
    row — resolved once when crx_rl_a4_spine was built — rather than a separate
    spell table. This derives both shapes from that single spine so the CC
    function can run completely unchanged (R14 reuse / R18 additive — no CC
    code touched).

    Args:
        rl_a4_spine: RL spine already joined to its T0/spell window — e.g.
            crx_rl_a4_spine. Required cols: account_id, observation_date,
            cif_id, spell_id, t0.

    Returns:
        Tuple of:
            cc_spine_shim:    (contract_id, observation_date, cif_id) — one row
                per rl_a4_spine row.
            spell_table_shim: (account_id, spell_id, t0, spell_end) — one row
                per (account_id, spell_id); spell_end is always NULL (RL has no
                closed-spell concept at this grain — join_spine_to_spell only
                needs t0 <= observation_date, which NULL spell_end satisfies).
    """
    cc_spine_shim = rl_a4_spine.select(
        F.col("account_id").alias("contract_id"),
        F.col("observation_date"),
        F.col("cif_id"),
    )
    spell_table_shim = (
        rl_a4_spine.select("account_id", "spell_id", "t0")
        .where(F.col("spell_id").isNotNull())
        .dropDuplicates(["account_id", "spell_id"])
        .withColumn("spell_end", F.lit(None).cast("date"))
    )
    return cc_spine_shim, spell_table_shim
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_spell/nodes.py`
action: delete · base sha256 `97e9cedbe6ca75f6e09a88bc2faf55ed6505adfa5c719ed57f38d37693b75623` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T03 — Delinquency-spell table for Credit Cards.

Build function: build_cc_spell_table(raw_stg_billing, cc_spine) -> DataFrame

Output grain: (account_id, spell_id) — one row per delinquency episode.
T0 is the spell anchor for every A4 feature. Every A4 lookback window is
relative to T0, not to the calendar or observation date.

Shared dependency (R18 cleanup, A4 pipeline retirement): this table now carries
only the columns its surviving consumers (cc_a1_ability, cc_a2_locatability,
cc_a3_payment_credibility, cc_departure_signature, cc_payment_trajectory,
cc_utilisation, cc_raw_extract) actually read — account_id, spell_id, t0,
spell_end, t0_censored_flag, prior_spell_end, days_to_dpd30, days_to_dpd60.
The superseded cc_a4_class pipeline and its spine-table consumers are removed;
crx_cc_a4_deterioration derives its own restructure signal directly from
crx_cc_full_history instead of this table's former censored_subtype column.

Population scoping:
- cc_spine (model_id-namespaced) defines the target population for the current
  run (e.g. cc_60_180 or cc_180_plus). Only accounts appearing in cc_spine are
  processed. All their DLQ history rows are retained — not just M1 observations
  — because spell start/end detection requires the full temporal sequence
  including DLQ=0 rows.

Known limitations (by design, not bugs):
- 24-month horizon / censoring: t0_censored_flag = 1 is emitted for spell_id = 1
  on any account whose earliest recorded observation is already delinquent
  (delinquency_bucket >= _CC_DELINQ_MIN, i.e. ≥ 2 on CC) — T0 genuinely fell
  outside the data window, or (R13) the account was opened mid-delinquency as
  part of a restructure. Cure is a return to code < _CC_DELINQ_MIN (≤ 1 on CC).
  Code 1 = 'due but not overdue' is ordinary revolver behaviour and is outside
  spells.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

LOG = logging.getLogger(__name__)

# DPD30 and DPD60 entry thresholds (DLQ = max_ovd_bucket + 1):
# DLQ >= 3 → account has entered 31-60 DPD range (OVD_02 has balance)
# DLQ >= 4 → account has entered 61+ DPD range (M1 entry)
_DPD30_ENTRY_THRESHOLD = 3
_DPD60_ENTRY_THRESHOLD = 4

# CC delinquency threshold: code 1 = "due but not overdue" (normal revolver behaviour).
# Delinquency starts at code 2 (0-30 DPD).  Retail loans use 1 — hence per-unit constant.
_CC_DELINQ_MIN = 2


def build_cc_spell_table(raw_stg_billing: DataFrame, cc_spine: DataFrame) -> DataFrame:
    """Build the delinquency-spell table for CC accounts.

    One row per (account_id, spell_id). A spell is a continuous run of
    monthly observations with delinquency_bucket >= _CC_DELINQ_MIN (code ≥ 2
    on CC: code 1 = 'due but not overdue', delinquency starts at code 2).
    T0 = first such observation in the run. Cure = first observation with
    delinquency_bucket < _CC_DELINQ_MIN (≤ 1 on CC).

    Args:
        raw_stg_billing: Raw billing staging table — full history, all DLQ
            levels (0-9), no date or DLQ filter applied. Required columns:
            contract_idt (Long), billing_date (Date), add_info (string —
            contains BS_PMT_CYCLE_DUE=<N> from which delinquency_bucket is
            extracted via regex).
        cc_spine: Model-namespace spine (produced by the spine pipeline for the
            current model_id). Used to scope raw_stg_billing to the target
            population via leftsemi join. Required column: contract_id (Long).

    Returns:
        DataFrame at grain (account_id, spell_id) with schema:
            account_id          long
            spell_id            int     (1-indexed, per account, no gaps)
            t0                  date    (first DLQ>=DELINQ_MIN observation in the spell)
            spell_end           date    (nullable — first DLQ<DELINQ_MIN after spell, or NULL)
            prior_spell_end     date    (nullable — previous spell's cure date; NULL for spell_id=1)
            t0_censored_flag    int     (1 if T0 is outside the data window)
            days_to_dpd30       int     (nullable — datediff from t0 to first DLQ>=3)
            days_to_dpd60       int     (nullable — datediff from t0 to first DLQ>=4)
    """
    # -- Step 0: scope to target population + extract full DLQ history ---------
    # raw_stg_billing carries all DLQ levels (0-9) and all history — no date or
    # DLQ filter applied. leftsemi join on cc_spine limits the scan to accounts
    # in the current model_id population. Column name difference: billing uses
    # contract_idt (Long), cc_spine uses contract_id (Long).
    _spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()

    df = (
        raw_stg_billing.join(F.broadcast(_spine_keys), "contract_idt", "leftsemi")
        .select(
            F.col("contract_idt").alias("account_id"),
            F.col("billing_date").cast(DateType()).alias("observation_date"),
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
            .cast("int")
            .alias("delinquency_bucket"),
        )
        .distinct()
    )

    # -- Step 2: detect spell starts -----------------------------------------
    w_acct = Window.partitionBy("account_id").orderBy("observation_date")

    df = df.withColumn("_prev_dlq", F.lag("delinquency_bucket").over(w_acct))

    df = df.withColumn(
        "_spell_start",
        F.when(
            (F.col("delinquency_bucket") >= _CC_DELINQ_MIN)
            & ((F.col("_prev_dlq") < _CC_DELINQ_MIN) | F.col("_prev_dlq").isNull()),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )

    # -- Step 3: assign spell_id (cumulative sum of _spell_start) ----------
    w_acct_unbounded = (
        Window.partitionBy("account_id")
        .orderBy("observation_date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )
    df = df.withColumn("spell_id", F.sum("_spell_start").over(w_acct_unbounded))

    # -- Step 4: detect censored accounts ----------------------------------
    # An account is censored if its very first observation already has
    # dlq >= _CC_DELINQ_MIN. This means T0 fell outside the data window.
    # Only spell_id = 1 is flagged (the only one whose T0 might be unknown).
    w_first = Window.partitionBy("account_id").orderBy("observation_date")
    censored_accounts = (
        df.withColumn("_rn", F.row_number().over(w_first))
        .filter(F.col("_rn") == 1)
        .filter(F.col("delinquency_bucket") >= _CC_DELINQ_MIN)
        .select("account_id")
        .distinct()
        .withColumn("_is_censored", F.lit(1))
    )

    # -- Step 5: aggregate spell-level metrics (in-spell rows only) --------
    in_spell = df.filter(F.col("delinquency_bucket") >= _CC_DELINQ_MIN)

    spell_agg = in_spell.groupBy("account_id", "spell_id").agg(
        F.min("observation_date").alias("t0"),
        F.max("observation_date").alias("_spell_max_obs"),
        F.min(
            F.when(
                F.col("delinquency_bucket") >= _DPD30_ENTRY_THRESHOLD,
                F.col("observation_date"),
            )
        ).alias("_date_dlq3"),
        F.min(
            F.when(
                F.col("delinquency_bucket") >= _DPD60_ENTRY_THRESHOLD,
                F.col("observation_date"),
            )
        ).alias("_date_dlq4"),
    )

    # -- Step 6: roll speed metrics ------------------------------------------
    spell_agg = spell_agg.withColumn(
        "days_to_dpd30",
        F.datediff(F.col("_date_dlq3"), F.col("t0")),
    ).withColumn(
        "days_to_dpd60",
        F.datediff(F.col("_date_dlq4"), F.col("t0")),
    )

    # -- Step 7: cure date detection (self-join on account_id) ------------
    # For each spell, find the first DLQ<_CC_DELINQ_MIN observation strictly after
    # the spell's last DLQ>=_CC_DELINQ_MIN snapshot (_spell_max_obs).
    cure_candidates = df.filter(F.col("delinquency_bucket") < _CC_DELINQ_MIN).select(
        F.col("account_id"),
        F.col("observation_date").alias("_cure_obs"),
    )

    cure_dates = (
        spell_agg.select("account_id", "spell_id", "_spell_max_obs")
        .join(cure_candidates, on="account_id", how="left")
        .filter(F.col("_cure_obs") > F.col("_spell_max_obs"))
        .groupBy("account_id", "spell_id")
        .agg(F.min("_cure_obs").alias("_cure_date"))
    )

    spell_agg = spell_agg.join(cure_dates, on=["account_id", "spell_id"], how="left")

    # spell_end: cure_date if known; NULL for active (no cure yet)
    spell_agg = spell_agg.withColumn(
        "spell_end",
        F.when(F.col("_cure_date").isNotNull(), F.col("_cure_date")).otherwise(
            F.lit(None).cast("date")
        ),
    )

    # prior_spell_end: previous spell's cure date — NULL for spell_id=1.
    # T04b uses it to truncate W_pre at the prior spell boundary (§3.0b).
    _w_prev_spell = Window.partitionBy("account_id").orderBy("spell_id")
    spell_agg = spell_agg.withColumn(
        "prior_spell_end", F.lag("spell_end").over(_w_prev_spell)
    )

    # -- Step 8: t0_censored_flag --------------------------------------------
    spell_agg = spell_agg.join(
        censored_accounts, on="account_id", how="left"
    ).withColumn(
        "t0_censored_flag",
        F.when(
            (F.col("spell_id") == 1) & (F.col("_is_censored") == 1),
            F.lit(1),
        ).otherwise(F.lit(0)),
    )

    # -- Step 9: final select in schema order --------------------------------
    result = spell_agg.select(
        F.col("account_id").cast("long"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("spell_end").cast("date"),
        F.col("prior_spell_end").cast("date"),
        F.col("t0_censored_flag").cast("int"),
        F.col("days_to_dpd30").cast("int"),
        F.col("days_to_dpd60").cast("int"),
    )

    _log_spell_stats(result)
    return result


def _log_spell_stats(result: DataFrame) -> None:
    """Log basic spell table statistics."""
    try:
        total_spells = result.count()
        LOG.info(
            "CC spell table built: %d spells",  # total_accounts omitted: Filtering_Sensitive_Logs
            total_spells,
        )
    except Exception as e:  # pylint: disable=broad-except
        LOG.warning("Could not compute spell stats: %s (lazy eval context)", str(e))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_spell/pipeline.py`
action: delete · base sha256 `de64d1e46d903d4b38bcb8afb02d7192b5dea6eceed51bd80455196ad383da29` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T03 — CC delinquency-spell table (raw_stg_billing → crx_cc_spell_table)."""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_spell_table


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [raw_stg_billing, cc_spine] → crx_cc_spell_table.

    raw_stg_billing provides full DLQ history (all levels 0-9, all dates) for
    all accounts. cc_spine (model_id-namespaced) scopes the scan to the target
    population via leftsemi join. Must run after the spine pipeline for the
    relevant model_id (cc_60_180.spine or cc_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_cc_spell_table
    """
    return Pipeline(
        [
            node(
                func=build_cc_spell_table,
                inputs=["raw_stg_billing", "cc_spine"],
                outputs="crx_cc_spell_table",
                name="build_crx_cc_spell_table",
                tags=["crx", "spell", "t03"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/__init__.py`
action: delete · base sha256 `5ca4d657ab1e964dca62e067af7be4d74e8e7469a597faa15cbf80f6a0cb5788` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A4 Spine — structural spine/spell window projection for Retail Loans.

Inputs: rl_spine, crx_rl_spell_table
Output: crx_rl_a4_spine
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/nodes.py`
action: delete · base sha256 `23c4fbc9c0bb26c66dd3348626a0102d1c55debdb5583d76eb669622c7349897` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A4 spine: the persona-window spine rows with their delinquency spell.

Inputs: rl_spine, crx_rl_spell_table, params:crx_persona
Output: crx_rl_a4_spine
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_rl_depart_spine(
    rl_spine: DataFrame,
    crx_rl_spell_table: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Build spell-scoped spine for departure signal computation (Node 0 of 5).

    Mirrors steps 1–4 of build_rl_a4_spine_projection WITHOUT the A4 label join,
    producing the raw spine grain used by all downstream departure nodes.

    Join logic (mirrors join_spine_to_spell pattern from _spine_utils.py):
        rl_spine["account_id"] == t0_table["account_id"]
        AND t0 <= observation_date
        AND spell_end IS NULL (always passes — open spell for RL)

    Args:
        rl_spine:           Model spine at (account_id, observation_date) grain.
        crx_rl_spell_table: T0 anchor. Required cols: account_id, spell_id, t0,
                            t0_censored_flag, spell_end, cif_id.
        crx_persona:        Persona param dict with persona_start_date /
                            persona_end_date.

    Returns:
        DataFrame at (account_id, observation_date) grain with cols::

            cif_id           string  NULL if no active non-censored spell
            account_id       string
            observation_date date
            spell_id         int     NULL if no active spell
            t0               date    NULL if no active spell
    """
    persona_start_date = crx_persona["persona_start_date"]
    persona_end_date = crx_persona["persona_end_date"]

    # Step 1: non-censored active spells (spell_end IS NULL = current episode)
    t0_filtered = crx_rl_spell_table.filter(
        (F.col("t0_censored_flag") == 0) & F.col("spell_end").isNull()
    ).select("account_id", "spell_id", "t0", "spell_end", "cif_id")

    # Step 2: left-join spine to spell info (all spine rows preserved)
    spine_for_join = (
        rl_spine.drop("cif_id") if "cif_id" in rl_spine.columns else rl_spine
    )
    spine_with_t0 = spine_for_join.join(t0_filtered, on="account_id", how="left")

    # Step 3: date filter — t0 <= observation_date (spell_end IS NULL always passes)
    spine_filtered = spine_with_t0.filter(
        F.col("t0").isNull() | (F.col("t0") <= F.col("observation_date"))
    )

    # Step 4: persona window filter
    start_dt = F.to_date(F.lit(persona_start_date))
    end_dt = F.to_date(F.lit(persona_end_date))
    result = spine_filtered.filter(
        (F.col("observation_date") >= start_dt) & (F.col("observation_date") <= end_dt)
    )

    n_rows = result.count()
    n_with_spell = result.filter(F.col("spell_id").isNotNull()).count()
    LOG.info(
        "build_rl_depart_spine [%s → %s]: %d spine rows | with active spell: %d (%.1f%%)",
        persona_start_date,
        persona_end_date,
        n_rows,
        n_with_spell,
        100.0 * n_with_spell / max(n_rows, 1),
    )

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/pipeline.py`
action: delete · base sha256 `c50dd0459c0e244cf361591df9b4272550863a3b7fb04792c46034d45d6ea71e` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A4 Spine — structural spine/spell window projection.

Replaces rl_a4_class's Node 2 (build_rl_a4_spine_projection), which broadcast a
now-superseded CASA/EMI classification onto the spine. crx_rl_a4_spine is now
a pure structural join — (account_id, cif_id, observation_date, spell_id, t0),
decoupled from any A4 classifier, scoped by crx_rl_a4_deterioration instead.

Run with:
    kedro run --pipeline=crx_rl_a4_spine
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_depart_spine

_TAGS = ["crx", "rl", "rl_a4_spine"]


def _spine_node(output: str) -> node:
    return node(
        func=build_rl_depart_spine,
        inputs=[
            "rl_spine",
            "crx_rl_spell_table",
            "params:crx_persona",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=_TAGS,
    )


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """One-node pipeline: rl_spine + crx_rl_spell_table -> crx_rl_a4_spine."""
    return Pipeline([_spine_node("crx_rl_a4_spine")], tags=["crx_persona"])
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_spell_table/__init__.py`
action: delete · base sha256 `c1e6f6202fbab7e82f482d2b6242b2668da481717fef9ed6ddaf8d8bd9229e57` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL spell table pipeline: crx_rl_full_history + rl_spine → crx_rl_spell_table."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_spell_table/nodes.py`
action: delete · base sha256 `819b0725352dbbb4587a0a1c8b71c58ff13b0ec3169e45301cceb35a72e6eb7a` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-B2 — T0 anchor table for Retail Loan persona pipeline.

Build function: build_rl_spell_table(crx_rl_full_history, rl_spine) -> DataFrame

Output grain: one row per (account_id, spell_id).

A spell is a contiguous run of months where dlq_bucket >= 1.  Episode
boundaries are detected via a cumulative-sum of spell-start flags ordered by
month_end_date per account (mirrors cc_spell/nodes.py, adapted for RL threshold
dlq_bucket >= 1 vs CC dlq_bucket >= 2).

T0 = min(month_end_date) where dlq_bucket >= 1 within the spell.
spell_end = first clean (dlq_bucket == 0) month_end_date strictly after the
last delinquent row of the spell; NULL for the active spell.

t0_censored_flag = 1 for spell_id = 1 when the account's very first history row
is already delinquent (T0 predates the data window).

For the ~0% of accounts with no DLQ >= 1 in history (censored with no episodes),
a single stub row is synthesised with spell_id = 1, t0 = min(rl_spine
.observation_date), t0_censored_flag = 1.

Key behavioural columns derived per spell:
- restructure_blind_spot_flag: 1 if account was ever restructured in history (R13)
- pre_t0_months: count of history rows with month_end_date < t0
- prior_spell_cnt_12m: distinct prior DLQ-1+ episodes in 12m before T0
- w_pre_clean_m: consecutive DLQ-0 months immediately preceding T0

Inputs: crx_rl_full_history (RL-B1 output), rl_spine (model-namespaced spine, requires cif_id)
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_rl_spell_table(  # pylint: disable=too-many-locals
    crx_rl_full_history: DataFrame,
    rl_spine: DataFrame,
) -> DataFrame:
    """Build the T0 anchor table for RL accounts.

    Args:
        crx_rl_full_history: Full monthly history for RL spine accounts.
            Required columns: account_id (string), month_end_date (date),
            dlq_bucket (int), restructure_flag (int).
        rl_spine: Model-namespaced spine. Required columns:
            account_id (string), observation_date (date), cif_id (string).

    Returns:
        DataFrame at grain (account_id, spell_id) with schema:
            account_id                  string
            cif_id                      string
            spell_id                    int     (1-indexed per account)
            t0                          date    (start of delinquency episode)
            t0_censored_flag            int     (1 if T0 before data window)
            restructure_blind_spot_flag int     (1 if ever restructured — R13)
            pre_t0_months               int     (months of history before T0)
            prior_spell_cnt_12m         int     (prior DLQ-1+ episodes in 12m before T0)
            w_pre_clean_m               int     (consecutive DLQ-0 months before T0)
            spell_end                   date    (NULL for active spell)
            computed_at                 timestamp
    """
    hist = crx_rl_full_history

    # -- Step 1: spine_anchor — first spine observation and cif_id per account --
    spine_anchor = (
        rl_spine.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("cif_id").cast("string"),
        )
        .groupBy("account_id")
        .agg(
            F.min("observation_date").alias("anchor_date"),
            F.first("cif_id").alias("cif_id"),
        )
    )

    # -- Step 2: scope history to spine accounts only -------------------------
    hist_scoped = hist.join(
        spine_anchor.select("account_id"), on="account_id", how="inner"
    )

    # -- Step 3: detect spell starts via lag and assign spell_id (cumsum) -----
    # Spell starts when dlq_bucket >= 1 and previous month was dlq_bucket == 0
    # (or no previous row). coalesce(lag, 0) treats first row as "clean before".
    w_acct = Window.partitionBy("account_id").orderBy("month_end_date")
    w_acct_unbounded = (
        Window.partitionBy("account_id")
        .orderBy("month_end_date")
        .rowsBetween(Window.unboundedPreceding, Window.currentRow)
    )

    labeled = (
        hist_scoped.withColumn(
            "_prev_dlq",
            F.coalesce(F.lag("dlq_bucket").over(w_acct), F.lit(0)),
        )
        .withColumn(
            "_spell_start",
            F.when(
                (F.col("dlq_bucket") >= 1) & (F.col("_prev_dlq") == 0),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "spell_id",
            F.sum("_spell_start").over(w_acct_unbounded).cast("int"),
        )
    )

    # -- Step 4: censored detection — first history row already delinquent ----
    # Only spell_id = 1 can be censored (T0 before data window).
    censored_accts = (
        labeled.withColumn("_rn", F.row_number().over(w_acct))
        .filter((F.col("_rn") == 1) & (F.col("dlq_bucket") >= 1))
        .select("account_id")
        .distinct()
    )

    # -- Step 5: per-spell aggregation (delinquent rows only) -----------------
    in_spell = labeled.filter(F.col("dlq_bucket") >= 1)

    spell_agg = in_spell.groupBy("account_id", "spell_id").agg(
        F.min("month_end_date").alias("t0"),
        F.max("month_end_date").alias("_spell_max_obs"),
    )

    # -- Step 6: spell_end detection — first clean month after last DLQ row ---
    clean_rows = hist_scoped.filter(F.col("dlq_bucket") == 0).select(
        F.col("account_id"),
        F.col("month_end_date").alias("_clean_date"),
    )

    cure_dates = (
        spell_agg.select("account_id", "spell_id", "_spell_max_obs")
        .join(clean_rows, on="account_id", how="left")
        .filter(F.col("_clean_date") > F.col("_spell_max_obs"))
        .groupBy("account_id", "spell_id")
        .agg(F.min("_clean_date").alias("spell_end"))
    )

    spell_agg = spell_agg.join(cure_dates, on=["account_id", "spell_id"], how="left")

    # -- Step 7: t0_censored_flag and T0 fallback ------------------------------
    spell_agg = (
        spell_agg.join(
            censored_accts.withColumn("_is_censored", F.lit(1)),
            on="account_id",
            how="left",
        )
        .withColumn(
            "t0_censored_flag",
            F.when(
                (F.col("spell_id") == 1) & (F.col("_is_censored") == 1),
                F.lit(1),
            )
            .otherwise(F.lit(0))
            .cast("int"),
        )
        .drop("_is_censored")
    )

    # -- Step 8: stub rows for ~0% accounts with no DLQ in history -----------
    # These have no rows in spell_agg; synthesise spell_id=1, t0=anchor_date.
    no_spell_accts = spine_anchor.select("account_id", "anchor_date").join(
        spell_agg.select("account_id").distinct(),
        on="account_id",
        how="left_anti",
    )

    stubs = (
        no_spell_accts.withColumn("spell_id", F.lit(1).cast("int"))
        .withColumnRenamed("anchor_date", "t0")
        .withColumn("_spell_max_obs", F.lit(None).cast("date"))
        .withColumn("spell_end", F.lit(None).cast("date"))
        .withColumn("t0_censored_flag", F.lit(1).cast("int"))
    )

    spell_agg = spell_agg.unionByName(stubs, allowMissingColumns=True)

    # -- Step 9: join cif_id and restructure_blind_spot_flag ------------------
    restructure = hist_scoped.groupBy("account_id").agg(
        F.max("restructure_flag").cast("int").alias("restructure_blind_spot_flag")
    )

    spell_agg = (
        spell_agg.join(
            spine_anchor.select("account_id", "cif_id"), on="account_id", how="left"
        )
        .join(restructure, on="account_id", how="left")
        .withColumn(
            "restructure_blind_spot_flag",
            F.coalesce(F.col("restructure_blind_spot_flag"), F.lit(0)).cast("int"),
        )
    )

    # -- Step 10: per-spell ancillary metrics ---------------------------------
    # pre_t0_months, prior_spell_cnt_12m, w_pre_clean_m are per (account_id, spell_id).
    spell_t0s = spell_agg.select("account_id", "spell_id", "t0")

    pre_t0_cnt = _compute_pre_t0_months(hist_scoped, spell_t0s)
    prior_spells = _compute_prior_spells(labeled, spell_t0s)
    w_clean_tbl = _compute_w_clean_m(hist_scoped, spell_t0s)

    # -- Step 11: assemble and finalize ----------------------------------------
    result = (
        spell_agg.select(
            "account_id",
            "cif_id",
            "spell_id",
            "t0",
            "t0_censored_flag",
            "restructure_blind_spot_flag",
            "spell_end",
        )
        .join(pre_t0_cnt, on=["account_id", "spell_id"], how="left")
        .join(prior_spells, on=["account_id", "spell_id"], how="left")
        .join(w_clean_tbl, on=["account_id", "spell_id"], how="left")
        .withColumn("computed_at", F.current_timestamp())
        .withColumn(
            "pre_t0_months", F.coalesce(F.col("pre_t0_months"), F.lit(0)).cast("int")
        )
        .withColumn(
            "prior_spell_cnt_12m",
            F.coalesce(F.col("prior_spell_cnt_12m"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "w_pre_clean_m",
            F.coalesce(F.col("w_pre_clean_m"), F.lit(0)).cast("int"),
        )
        .select(
            F.col("account_id").cast("string"),
            F.col("cif_id").cast("string"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("t0_censored_flag"),
            F.col("restructure_blind_spot_flag"),
            F.col("pre_t0_months"),
            F.col("prior_spell_cnt_12m"),
            F.col("w_pre_clean_m"),
            F.col("spell_end"),
            F.col("computed_at"),
        )
    )

    # -- Step 12: log stats --------------------------------------------------------
    _log_stats(result)
    return result


def _compute_pre_t0_months(
    hist_scoped: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count history rows with month_end_date < T0 per (account_id, spell_id)."""
    return (
        spell_t0s.join(
            hist_scoped.select("account_id", "month_end_date"),
            on="account_id",
            how="left",
        )
        .filter(F.col("month_end_date") < F.col("t0"))
        .groupBy("account_id", "spell_id")
        .agg(F.count("*").cast("int").alias("pre_t0_months"))
    )


def _compute_prior_spells(
    labeled: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count distinct prior DLQ-1+ episodes in the 12m window before each spell's T0."""
    # labeled carries spell_id (the episode each row belongs to).
    # For target spell N, count distinct prior spell_ids where rows fall in [T0-12m, T0).
    hist_dlq = labeled.filter(F.col("dlq_bucket") >= 1).select(
        F.col("account_id"),
        F.col("month_end_date"),
        F.col("spell_id").alias("_hist_spell_id"),
    )

    return (
        spell_t0s.withColumnRenamed("spell_id", "_target_spell_id")
        .join(hist_dlq, on="account_id", how="left")
        .filter(
            (F.col("month_end_date") < F.col("t0"))
            & (F.col("month_end_date") >= F.add_months(F.col("t0"), -12))
            & (F.col("_hist_spell_id") != F.col("_target_spell_id"))
        )
        .groupBy("account_id", "_target_spell_id")
        .agg(F.countDistinct("_hist_spell_id").cast("int").alias("prior_spell_cnt_12m"))
        .withColumnRenamed("_target_spell_id", "spell_id")
    )


def _compute_w_clean_m(
    hist_scoped: DataFrame,
    spell_t0s: DataFrame,
) -> DataFrame:
    """Count consecutive DLQ-0 months immediately before each spell's T0."""
    pre_t0 = spell_t0s.join(
        hist_scoped.select("account_id", "month_end_date", "dlq_bucket"),
        on="account_id",
        how="left",
    ).filter(F.col("month_end_date") < F.col("t0"))

    pre_t0_cnt = pre_t0.groupBy("account_id", "spell_id").agg(
        F.count("*").cast("int").alias("_pre_t0_cnt")
    )

    w_desc = Window.partitionBy("account_id", "spell_id").orderBy(
        F.desc("month_end_date")
    )

    first_nc = (
        pre_t0.withColumn("_rn_desc", F.row_number().over(w_desc))
        .filter(F.col("dlq_bucket") > 0)
        .groupBy("account_id", "spell_id")
        .agg(F.min("_rn_desc").alias("_first_nc_rn"))
    )

    return (
        pre_t0_cnt.join(first_nc, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "w_pre_clean_m",
            F.when(F.col("_first_nc_rn").isNull(), F.col("_pre_t0_cnt")).otherwise(
                (F.col("_first_nc_rn") - 1).cast("int")
            ),
        )
        .select("account_id", "spell_id", "w_pre_clean_m")
    )


def _log_stats(df: DataFrame) -> None:
    """Log spell count, censored%, and restructure_blind_spot%."""
    try:
        row_count = df.count()
        acct_count = df.select("account_id").distinct().count()
        agg_row = df.agg(
            F.sum("t0_censored_flag").alias("censored_cnt"),
            F.sum("restructure_blind_spot_flag").alias("restructure_cnt"),
        ).collect()[0]
        active_cnt = df.filter(F.col("spell_end").isNull()).count()
        censored_pct = (
            agg_row["censored_cnt"] / row_count * 100 if row_count > 0 else 0.0
        )
        restructure_pct = (
            agg_row["restructure_cnt"] / acct_count * 100 if acct_count > 0 else 0.0
        )
        LOG.info(
            "crx_rl_spell_table built: %d spells across %d accounts | "
            "active (spell_end NULL)=%d | censored=%.2f%% | restructure_blind_spot=%.2f%%",
            row_count,
            acct_count,
            active_cnt,
            censored_pct,
            restructure_pct,
        )
    except Exception as e:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute rl_spell_table stats: %s (lazy eval context)", str(e)
        )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_spell_table/pipeline.py`
action: delete · base sha256 `bb7bcd18f696a35ba3e31b530d0d69985aabf18bfe5636398a525b2f2f38d15f` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-B2 — T0 anchor table for Retail Loan persona pipeline."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_spell_table


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [crx_rl_full_history, rl_spine] → crx_rl_spell_table.

    crx_rl_full_history (RL-B1) provides the full monthly history from which
    T0 (first DLQ >= 1 onset) is derived. rl_spine (model_id-namespaced) provides
    the censored fallback for the ~0% of accounts with no DLQ >= 1 in history.

    No date filter applied — full history required to find true first delinquency
    onset. Date filtering is applied downstream in crx_rl_a4_spine.

    Run with:
        kedro run --pipeline=crx_rl_spell_table
    """
    return Pipeline(
        [
            node(
                func=build_rl_spell_table,
                inputs=["crx_rl_full_history", "rl_spine"],
                outputs="crx_rl_spell_table",
                name="build_crx_rl_spell_table",
                tags=["crx", "rl", "rl_b2"],
            ),
        ],
        tags=["crx_persona"],
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
Clean up after mirror bundle 30_spell_tables_removed.md, on the bundle's branch.
- Remove the old outputs of the deleted datasets in HDFS, for each model_id (cc_60_180, cc_180_plus, rl_60_180, rl_180_plus): `hdfs dfs -rm -r <persona path>/<model_id>/<persona folder>/crx/{crx_cc_spell_table,crx_rl_spell_table,crx_rl_a4_spine,crx_cc_limits}` (paths from the catalog entries in the previous commit; a folder that does not exist is fine).
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
