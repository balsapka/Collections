# Mirror bundle 16 — Refactor R-B — shared layer, A4, A2 and A1 refactored (no output change, zero-difference checks)

apply_bundle version: 7 · built 2026-11-06 from `7bdba03..611b23c` · source: 2 added, 30 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 6). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/16_persona_refactor.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '16_persona_refactor.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/16_persona_refactor.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Print the Spark version (the A2 rewrite needs 3.1 or later):

```bash
python -c "import pyspark; print(pyspark.__version__)"
```

**Step 5.** Ask Sonnet the following, in one go:

1. **Tests.** Run the crx_persona test modules and update the ones the new signatures and names break (the list is in the bundle's "Changes you will see": `build_a1_ability`, `build_liquidity_signals`, `build_rl_full_history`, `episode_start`, `StateLadder` → `Scorecard`, the renamed symbols). Behaviour must not change: fix the test calls, never the expected values. Report any test whose expected value would have to change.
2. **Other readers of renamed symbols.** `grep -rn` over `src` for `StateLadder`, `points_from_level`, `_window_start`, `_string_key`, `_log_state_stats`, `_month_label` outside crx_persona. Report hits; do not change them.
3. **Tags.** `grep -rn` over the repo's run scripts / docs for `--tags` using `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`, `cc` or `rl` with the persona pipelines. Report hits.

Then check: `kedro registry list | grep rf_check` lists the six `crx_<cc|rl>_<a4|a2|a1>_rf_check` pipelines.

**Step 6.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Refactor R-B: shared layer, A4, A2, A1 (no output change)" && git push
```

**Undo** (before step 6) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/16_persona_refactor.md --revert
```

### In PROD

**Step 7.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

The outputs from the last real run are the baseline: do not re-run any axis before the checks. Run for **`rl_60_180`**, then **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`). Order matters only for reading: A4 first.

**Step 8.** A4 (the full history is rebuilt inside the check):

```bash
kedro run --env=dev --pipeline=crx_rl_a4_rf_check
```

**Step 9.** A2:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_rf_check
```

While it runs, open the Spark UI and note the shuffle read and spill of the stage that builds the A2 DCORE signals.

**Step 10.** A1 (also rebuilds the obs base and logs the join-key check):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_rf_check
```

Then the same three for CC: `crx_cc_a4_rf_check`, `crx_cc_a2_rf_check`, `crx_cc_a1_rf_check`.

Paste back every block from `=== RF … START ===` to `=== RF … END ===` (8 per model_id), plus the A2 DCORE stage's shuffle read and spill. Expected: `rows only in old: 0`, `rows only in new: 0`, every state crosstab on the diagonal. In `RF A2 DCORE`, a non-attempt share over 50% or a spilling stage is worth flagging; in `RF STRING KEYS`, any padded count above 0.

**Step 11.** Only after the RF blocks have been reviewed: write the real outputs for the 180+ model_ids as usual (`crx_<p>_a4_deterioration`, `crx_<p>_a2_locatability`, `crx_<p>_a1_ability`). The 60–180 outputs need no re-run (identical by the check). Then go on with the A3 bundle.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Refactors the shared persona layer, A4, A2 and A1 for readability, efficiency and one design across axes. **No output changes**: every axis must come out identical, row for row (checked locally on 79 test datasets, and in PROD by the check pipelines below). Second of three bundles: after the dead-code bundle (15), before the new A3.

- **Shared layer** (`_common.py`): `segment` / `SEG_*`, `string_key`, `window_start`, `window_agg(start=)`, `dcore_account_events`, `GONE_DARK_DAYS`, one state logger for every axis; `_common` no longer imports the A4 engine. `_dpd_journey/anchor.py` adds `episode_start` (the start of the current delinquency episode, which the new A3 reads).
- **One scoring engine** (`scoring_engine.py`): `Scorecard` / `Dimension` / `Override` replace `StateLadder`; A1 now scores on it (A3 will too).
- **Kedro contracts:** dict `inputs` on every node, `require_columns` guards on the spines, sources and A4 history (missing columns now raise instead of passing quietly), `crx_persona` params required, one tag set.
- **PROD cost:** fewer passes and shuffles in A1 (one join per source, scoped `pit_latest`), A2 (the DCORE window replaced by one aggregate), A4 (no `collect` in RL, one aggregate for the CC restructure flag).
- **Readability and docstrings:** A1 thresholds and labels named after their spec cells, smaller functions, docstrings describe what the code does now.
- **Not touched:** A3, `_dcore_codes.py`, `cc_raw_extract/`, the spell tables, `rl_a4_spine` (bundle 15's spine check stays as it is).

**Changes you will see:**
- **Tags:** A4 nodes carry `crx_persona, crx, a4, deterioration, persona_axis`; full histories `crx_persona, crx, full_history`; removed tags `cc`, `rl`, `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`. `--tags full_history` now selects both histories.
- **Logs:** the A4 state-log block uses the same `log_latest_month` format as A1 and A2.
- **Errors:** `build_dpd_sequences` says `A4 history is missing required columns [...]` (still `ValueError`); the new guards on the obs bases, full histories and A4 inputs raise where the code used to continue.
- **Signatures** (tests): `build_a1_ability(obs_base, anchor, model_id, persona_end_date, **signals)`; `build_liquidity_signals(..., *, crx_persona)`; `build_rl_full_history` requires `crx_persona`; `episode_start` needs `history_cropped`.
- **Renamed / removed symbols:** `StateLadder` → `Scorecard` / `Dimension` / `Override`; `points_from_level` removed; `_window_start` → `window_start`; `_string_key` → `_common.string_key`; `MODEL_ID_SEGMENT` moved to `_common` (still re-exported); `_log_state_stats` → `log_state_stats`; `_dpd_journey.__all__` and `_month_label` removed; A1 labels `SOURCE_INTERNAL`, `SOURCE_BUREAU`, `REASON_BUREAU_BOUNCE`. New: `scoring_engine.LOW` / `MOD` / `HIGH`, A1 `HIGH_FROM` / `MODERATE_FROM`, A2 `_reachable`, `_dpd_journey.anchor.episode_start`.

**Checks** (temporary, `crx_persona/rf_check.py`): each re-runs one axis in its own namespace (intermediates in memory, nothing real overwritten) into `*_rf_check` entries and compares with the outputs persisted before the bundle. Blocks: `RF FULL HISTORY OUTPUT`, `RF A4 OUTPUT`, `RF A2 OUTPUT`, `RF A2 DCORE`, `RF KEYS`, `RF OBS BASE OUTPUT`, `RF A1 OUTPUT`, `RF STRING KEYS`. Expected: 0 rows only in old or new and 0 state moves everywhere (`computed_at` is ignored).

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
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_common.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/_dates.py` |
| add | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/anchor.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/constants.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/history.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/logging.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/params.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/states.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_full_history/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_full_history/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rf_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_full_history/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_full_history/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/scoring_engine.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `ba11c14cedca684fcf059a49af8dad836833ffd6be4defc62c3b0aee9c5c886f` · base trailing newline: yes · new sha256 `e18964a6fb14fa407109ec96b1c22b6246f215d8bc4a684079b0b8a692e5402b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# ==============================================================================
# CRX (collections-risk experimental) asset catalog
#
# All assets created by the T03+ persona-axis pipeline live here, under the
# 'crx_' prefix. This separation makes the abandon path clean:
#   rm conf/base/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- T04c: T0-scoped CC raw DDI intermediates ----------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions
# and crx_cc_balance.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.
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

# -- CC Full Billing History (ad hoc, no task card, mirrors RL-B1) -----------
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

# -- T43/P8: CC A4 Deterioration — DPD journey (native PySpark, one shuffle +
# per-account Python engine) -------------------------------------------------
# Port of docs/deterioration_states/dpd_states's journey_features/assign_states
# onto crx_cc_full_history, via the shared crx_persona/_dpd_journey.py module
# (CC scheme) — same module the RL build uses with the RL scheme. Decoupled from
# crx_cc_spell_table — restructure_blind_spot_flag is derived directly from
# crx_cc_full_history (see cc_a4_deterioration/nodes.py).

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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_signals"
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

# ── A3 Payment Credibility (T27) ────────────────────────────────────────────
# Grain: (account_id, spell_id). observation_date = coalesce(spell_end, current_date()).
# a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
#               payment_credibility_low, payment_credibility_unknown}
# Schema guards on dcore_feat_ptp and dcore_feat_settlement — if either is empty
# or missing required columns, commitment signals emit NULL and state falls through
# to payment_credibility_unknown.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
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

# TEMPORARY (refactor bundle R-A): the spine rebuilt by the R-A check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a4_spine_ra_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine_ra_check"
  save_args:
    mode: overwrite

# ── RL A4 Deterioration — DPD journey (RL-A4-3, one-shuffle + per-account
# Python engine) ─────────────────────────────────────────────────────────────
# Port of docs/deterioration_states/dpd_states's journey_features/
# assign_states onto RL's own bucket numbering, via the shared
# crx_persona/_dpd_journey.py module (RL scheme) — same module the CC build
# uses with the CC scheme. Unrelated to the superseded CASA/EMI-based A4
# classifier (formerly rl_a4_class, removed).

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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_signals"
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

# ── RL A3 Payment Credibility (RL-A3-1) ─────────────────────────────────────
# Node 1 intermediate: DCORE commitment signals, 24m partition floor applied to
# dcore_prm_followup_outcomes. Schema matches crx_cc_a3_commitment_signals.
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

# Node 2: shipped A3 payment credibility axis. Grain: (account_id, observation_date).
# a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
# payment_credibility_low, payment_credibility_unknown}.
# Produced by build_a3_payment_credibility (CC function imported directly — domain-agnostic).
crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite
`````

New:

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
# Built by the crx_cc_raw_extract pipeline; the CC A3 pipeline reads crx_cc_transactions
# and crx_cc_balance.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.
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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_signals"
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

# ── A3 Payment Credibility (T27) ────────────────────────────────────────────
# Grain: (account_id, spell_id). observation_date = coalesce(spell_end, current_date()).
# a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
#               payment_credibility_low, payment_credibility_unknown}
# Schema guards on dcore_feat_ptp and dcore_feat_settlement — if either is empty
# or missing required columns, commitment signals emit NULL and state falls through
# to payment_credibility_unknown.

crx_cc_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_payment_credibility"
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

# TEMPORARY (refactor bundle R-A): the spine rebuilt by the R-A check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a4_spine_ra_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine_ra_check"
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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_signals"
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

# ── RL A3 Payment Credibility (RL-A3-1) ─────────────────────────────────────
# Node 1 intermediate: DCORE commitment signals, 24m partition floor applied to
# dcore_prm_followup_outcomes. Schema matches crx_cc_a3_commitment_signals.
crx_rl_a3_commitment_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

# Node 2: shipped A3 payment credibility axis. Grain: (account_id, observation_date).
# a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
# payment_credibility_low, payment_credibility_unknown}.
# Produced by build_a3_payment_credibility (CC function imported directly — domain-agnostic).
crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

# TEMPORARY (refactor bundle R-B): outputs of the zero-difference check pipelines.
# Remove these entries, rf_check.py, the registry lines and the HDFS folders after the check.
crx_cc_full_history_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history_rf_check"
  save_args:
    mode: overwrite

crx_cc_a4_deterioration_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a4_deterioration_rf_check"
  save_args:
    mode: overwrite

crx_cc_obs_base_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_obs_base_rf_check"
  save_args:
    mode: overwrite

crx_cc_a2_locatability_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability_rf_check"
  save_args:
    mode: overwrite

crx_cc_a1_ability_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_rf_check"
  save_args:
    mode: overwrite

crx_rl_full_history_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_full_history_rf_check"
  save_args:
    mode: overwrite

crx_rl_a4_deterioration_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_rf_check"
  save_args:
    mode: overwrite

crx_rl_obs_base_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_obs_base_rf_check"
  save_args:
    mode: overwrite

crx_rl_a2_locatability_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability_rf_check"
  save_args:
    mode: overwrite

crx_rl_a1_ability_rf_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_rf_check"
  save_args:
    mode: overwrite
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `91b45276a70a044eb43afb0b435b31c91cfd10289bd515156b8f9387c393c305` · base trailing newline: yes · new sha256 `1edce01c80ff19cb0616abbe4e79104d427558f41d751c4cc570475c56642c25` · new trailing newline: yes

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
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features


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
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
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
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        # TEMPORARY (refactor bundle R-A): spine check; removed by the bundle's cleanup.
        "crx_rl_a4_spine_ra_check": crx_rl_a4_spine.create_ra_check_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": crx_rl_a3_payment_credibility.create_pipeline(),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
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

# TEMPORARY (refactor bundle R-B): zero-difference checks.
from enbd_collections.pipelines.crx_persona import rf_check as crx_rf_check
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
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features


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
        # Sub-pipelines for incremental cc_180_plus runs
        "cc_180_plus.spine": cc_way4_spine.create_180_plus_pipeline(),
        "cc_180_plus.staging": cc_way4_stg.create_pipeline(),
        "cc_180_plus.target": cc_way4_target.create_recovery_pipeline(),
        "cc_180_plus.features": cc_way4_feat.create_pipeline(),
        "cc_180_plus.rl_scope": retail_loans.create_cc_scoped_pipeline(),
        # Sub-pipelines for incremental rl_60_180 / rl_180_plus runs
        "rl_60_180.spine": retail_loans_spine.create_pipeline(),
        "rl_60_180.staging": retail_loans_stg.create_pipeline(),
        "rl_60_180.target": retail_loans_target.create_pipeline(),
        "rl_60_180.features": retail_loans_feat.create_pipeline(),
        "rl_60_180.primary": retail_loans_prm.create_pipeline(),
        "rl_60_180.intermediate": retail_loans_int.create_pipeline(),
        "rl_60_180.cc_scope": cc_way4.create_rl_scoped_pipeline(),
        "rl_180_plus.spine": retail_loans_spine.create_180_plus_pipeline(),
        "rl_180_plus.staging": retail_loans_stg.create_pipeline(),
        "rl_180_plus.target": retail_loans_target.create_recovery_pipeline(),
        "rl_180_plus.features": retail_loans_feat.create_rl_180_plus_pipeline(),
        "rl_180_plus.primary": retail_loans_prm.create_pipeline(),
        "rl_180_plus.intermediate": retail_loans_int.create_pipeline(),
        "rl_180_plus.cc_scope": cc_way4.create_rl_scoped_pipeline(),
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
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        # TEMPORARY (refactor bundle R-A): spine check; removed by the bundle's cleanup.
        "crx_rl_a4_spine_ra_check": crx_rl_a4_spine.create_ra_check_pipeline(),
        # TEMPORARY (refactor bundle R-B): zero-difference checks; removed by the cleanup.
        "crx_cc_a4_rf_check": crx_rf_check.create_a4_rf_check_pipeline("cc"),
        "crx_cc_a2_rf_check": crx_rf_check.create_a2_rf_check_pipeline("cc"),
        "crx_cc_a1_rf_check": crx_rf_check.create_a1_rf_check_pipeline("cc"),
        "crx_rl_a4_rf_check": crx_rf_check.create_a4_rf_check_pipeline("rl"),
        "crx_rl_a2_rf_check": crx_rf_check.create_a2_rf_check_pipeline("rl"),
        "crx_rl_a1_rf_check": crx_rf_check.create_a1_rf_check_pipeline("rl"),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
        "location_features": location_features.create_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: replace · base sha256 `b8c83a80cdf936c922f9f545bcfd1699d77d188425b04d0cafd1e4391e83a08b` · base trailing newline: yes · new sha256 `8f0711094e9ead483cbd7c8a9133fb94dde8ed7bbab55ea1600fb3669eb085fd` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* windows are whole calendar months: the observation month (observation dates are month
  ends) and the months before it;
* point-in-time lookups read before the observation date and can be bounded in age
  (``pit_latest``), window aggregates read the last N months (``window_agg``);
* source partition floors follow from the earliest observation month
  (``lookback_floor``);
* each axis logs its state distribution for the latest observation month only
  (``log_latest_month``).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from ._dpd_journey.constants import MODEL_ID_SEGMENT

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {"60_180": 3, "180_plus": 6}


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[MODEL_ID_SEGMENT[model_id]]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def _window_start(anchor: Column, months: int) -> Column:
    """First day of the last ``months`` calendar months, the anchor's month included."""
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_months: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_months`` keeps only rows in the anchor's last N calendar
    months (1 = its own month), so a stale record never stands in for a current one.
    Ties on the date are broken by the values (descending), so reruns agree. Returns
    ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_months is not None:
        cond = cond & (F.col("_d") >= _window_start(F.col("_anchor"), max_age_months))
    order = [F.col("_d").desc(), *[F.col(c).desc_nulls_last() for c in value_cols]]
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(src.select(key, F.col(date_col).alias("_d"), *value_cols), on=key)
        .filter(cond)
        .withColumn(
            "_rn", F.row_number().over(Window.partitionBy(*GRAIN).orderBy(*order))
        )
        .filter(F.col("_rn") == 1)
        .select(*GRAIN, *value_cols)
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    months: int,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    obs = F.col("observation_date")
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter(
            (F.col(date_col) >= _window_start(obs, months)) & (F.col(date_col) <= obs)
        )
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, months: int) -> str:
    """ISO start of the earliest observation's ``months``-month window (partition floor)."""
    first: date = base.agg(_window_start(F.min("observation_date"), months)).first()[0]
    return first.isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(df: DataFrame, col: str, name: str, persona_end_date: str) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        rows = (
            df.filter(F.trunc("observation_date", "month") == month)
            .groupBy(col)
            .count()
            .orderBy(col)
            .collect()
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%s: %s distribution not logged: %s", name, col, exc)
        return
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s, month of %s (n=%d)", name, col, persona_end_date, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str, crx_persona: dict) -> DataFrame:
    """The spine rows in the persona months — ``crx_persona.persona_start_date`` to
    ``persona_end_date``, whole months — with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    month = F.trunc("observation_date", "month")
    in_persona = month.between(
        F.trunc(F.lit(str(crx_persona["persona_start_date"])), "month"),
        F.trunc(F.lit(str(crx_persona["persona_end_date"])), "month"),
    )
    base = (
        spine.select(
            F.col(id_col).cast("string").alias("account_id"),
            F.col("observation_date").cast("date"),
            "cif_id",
        )
        .filter(in_persona)
        .dropDuplicates(list(GRAIN))
    )
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The CC observation base at month ends. Until ``cc_spine`` itself is month-end, each
    billing-date row moves to its month end; an account's rows in one month become one
    (the largest ``cif_id`` if they disagree). Remove the shift once the spine is month-end.
    """
    month_end = cc_spine.select(
        "contract_id",
        F.last_day(F.col("observation_date").cast("date")).alias("observation_date"),
        "cif_id",
    )
    collapsed = month_end.groupBy("contract_id", "observation_date").agg(
        F.max("cif_id").alias("cif_id")
    )
    return _obs_base(collapsed, "contract_id", crx_persona)


def build_rl_obs_base(rl_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The RL observation base (``rl_spine`` is already month-end)."""
    return _obs_base(rl_spine, "account_id", crx_persona)
`````

New:

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* windows are whole calendar months: the observation month (observation dates are month
  ends) and the months before it;
* point-in-time lookups read before the observation date and can be bounded in age
  (``pit_latest``), window aggregates read the last N months (``window_agg``);
* source partition floors follow from the earliest observation month
  (``lookback_floor``);
* each axis logs its state distribution for the latest observation month only
  (``log_latest_month``);
* DCORE events are read per scored account, through its agreements
  (``dcore_account_events``); each axis applies its own date window.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")

# The two segments; every per-segment setting in crx_persona is keyed by them.
SEG_60_180, SEG_180_PLUS = "60_180", "180_plus"

# The DPD segment each model_id scores; every segment-dependent rule keys on it.
MODEL_ID_SEGMENT = {
    "cc_60_180": SEG_60_180,
    "cc_180_plus": SEG_180_PLUS,
    "rl_60_180": SEG_60_180,
    "rl_180_plus": SEG_180_PLUS,
}

# Months every axis looks back, the observation month included; the dry 180+ buckets
# look further.
WINDOW_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 6}
# Failed call days in a row that make a customer gone dark: A2 Non-Reachable (D-A2-20),
# A3's no-pickup diagnostic (D-A3-19).
GONE_DARK_DAYS = {SEG_60_180: 3, SEG_180_PLUS: 6}


def segment(model_id: str) -> str:
    """``model_id``'s DPD segment: ``60_180`` or ``180_plus``."""
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    return MODEL_ID_SEGMENT[model_id]


def window_months(model_id: str) -> int:
    """The lookback window of ``model_id``'s segment, in calendar months."""
    return WINDOW_MONTHS[segment(model_id)]


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def string_key(df: DataFrame, col: str = "account_id") -> Column:
    """``col`` as a trimmed string join key. A double or decimal id is cast to ``long``
    first: cast straight to string it reads ``1.23456789E8`` and matches nothing."""
    key = F.col(col)
    if isinstance(df.schema[col].dataType, (T.DoubleType, T.FloatType, T.DecimalType)):
        key = key.cast("long")
    return F.trim(key.cast("string"))


def window_start(months: int, anchor: Column | None = None) -> Column:
    """First day of the last ``months`` calendar months, the month of ``anchor``
    (default ``observation_date``) included."""
    anchor = F.col("observation_date") if anchor is None else anchor
    return F.add_months(F.trunc(anchor, "month"), 1 - months)


def scoped(src: DataFrame, base: DataFrame, key: str) -> DataFrame:
    """``src`` rows whose ``key`` occurs in ``base``. Sources span the whole bank, the
    base one model's customers: the broadcast semi-join drops the rest before the
    shuffle of the join that follows."""
    return src.join(F.broadcast(base.select(key).distinct()), on=key, how="left_semi")


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_months: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_months`` keeps only rows in the anchor's last N calendar
    months (1 = its own month), so a stale record never stands in for a current one.
    Ties on the date are broken by the values (largest first, NULL last), so reruns
    agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    row_date, anchor_date = F.col("_d"), F.col("_anchor")
    cond = row_date <= anchor_date if inclusive else row_date < anchor_date
    if max_age_months is not None:
        cond = cond & (row_date >= window_start(max_age_months, anchor_date))
    latest = F.max(F.struct("_d", *value_cols))
    return (
        base.select(*GRAIN, key, anchor.alias("_anchor"))
        .join(
            scoped(
                src.select(key, F.col(date_col).alias("_d"), *value_cols), base, key
            ),
            on=key,
        )
        .filter(cond)
        .groupBy(*GRAIN)
        .agg(latest.alias("_latest"))
        .select(*GRAIN, *[F.col("_latest")[c].alias(c) for c in value_cols])
    )


def window_agg(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    aggs: Sequence[Column],
    months: int,
    key: str = "cif_id",
    start: str | None = None,
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last ``months`` calendar months — the
    observation month and the ``months - 1`` before it, up to the observation date.

    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read. ``start`` names a
    base date column that bounds each row's window from below as well (A3, D-A3-2:
    the episode start); ``aggs`` may read it. Returns ``GRAIN + aggs`` for base rows
    with at least one row in the window.
    """
    obs = F.col("observation_date")
    lower = window_start(months)
    if start is not None:
        lower = F.greatest(lower, F.col(start))
    return (
        base.select(*GRAIN, key, *([start] if start is not None else []))
        .join(scoped(src, base, key), on=key)
        .filter((F.col(date_col) >= lower) & (F.col(date_col) <= obs))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, months: int) -> str:
    """ISO start of the earliest observation's ``months``-month window (the partition
    floor for a source read)."""
    first: date = base.agg(window_start(months, F.min("observation_date"))).first()[0]
    return first.isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_latest_month(
    df: DataFrame,
    col: str,
    name: str,
    persona_end_date: str,
    *,
    latest_per_account: bool = False,
) -> None:
    """Log the ``col`` distribution of the latest observation month — the month of
    ``persona_end_date`` (one aggregate job; the month filter pushes down). A logging
    failure is a warning, never a failed run. ``latest_per_account`` counts each
    account's latest row of that month once (cc_spine has billing dates, so a card can
    have two rows in a month; drop the option when cc_spine is month-end)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    try:
        latest = df.filter(F.trunc("observation_date", "month") == month)
        if latest_per_account:
            newest_first = Window.partitionBy("account_id").orderBy(
                F.col("observation_date").desc()
            )
            latest = latest.withColumn("_rn", F.row_number().over(newest_first)).filter(
                F.col("_rn") == 1
            )
        rows = latest.groupBy(col).count().orderBy(col).collect()
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("%s: %s distribution not logged: %s", name, col, exc)
        return
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s, month of %s (n=%d)", name, col, persona_end_date, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str, crx_persona: dict) -> DataFrame:
    """The spine rows in the persona months — ``crx_persona.persona_start_date`` to
    ``persona_end_date``, whole months — with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    month = F.trunc("observation_date", "month")
    in_persona = month.between(
        F.trunc(F.lit(str(crx_persona["persona_start_date"])), "month"),
        F.trunc(F.lit(str(crx_persona["persona_end_date"])), "month"),
    )
    base = (
        spine.select(
            F.col(id_col).cast("string").alias("account_id"),
            F.col("observation_date").cast("date"),
            "cif_id",
        )
        .filter(in_persona)
        .dropDuplicates(list(GRAIN))
    )
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The CC observation base at month ends. Until ``cc_spine`` itself is month-end, each
    billing-date row moves to its month end; an account's rows in one month become one
    (the largest ``cif_id`` if they disagree). Remove the shift once the spine is month-end.
    """
    require_columns(cc_spine, ["contract_id", "observation_date", "cif_id"], "cc_spine")
    month_end = cc_spine.select(
        "contract_id",
        F.last_day(F.col("observation_date").cast("date")).alias("observation_date"),
        "cif_id",
    )
    collapsed = month_end.groupBy("contract_id", "observation_date").agg(
        F.max("cif_id").alias("cif_id")
    )
    return _obs_base(collapsed, "contract_id", crx_persona)


def build_rl_obs_base(rl_spine: DataFrame, crx_persona: dict) -> DataFrame:
    """The RL observation base (``rl_spine`` is already month-end)."""
    require_columns(rl_spine, ["account_id", "observation_date", "cif_id"], "rl_spine")
    return _obs_base(rl_spine, "account_id", crx_persona)


# ── DCORE ─────────────────────────────────────────────────────────────────────


def dcore_account_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """DCORE events on the agreements of the base's accounts: ``account_id``,
    ``day``, ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when
    missing). Shared by A2 (D-A2-8: all history, one agreement per account) and A3
    (D-A3-7: account level). Not dated by the observation: the caller joins its rows
    and window."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    return followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/__init__.py`
action: replace · base sha256 `64b489bba62d8c19f4eb2540abd6a5fa24446b3c66445e4eacb505ba76b2a66d` · base trailing newline: yes · new sha256 `7d7d612f655f86393813c5d53ff404248bc83ebc7215decb764d84b528b1d285` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""DPD-journey deterioration states — one engine for credit cards (CC) and retail loans (RL).

Replaces the window-function port (resolve_gaps / encode_transitions / classify_from_grid).
Spark does what Spark is good at — scoping, the history floor, and ONE shuffle that gathers
each account's monthly buckets into an array. The journey logic then runs per account as a
plain-Python port of the signed-off numpy reference (docs/deterioration_states/dpd_states:
features.py, states.py option B). Sequential rules (glitch fix, +2 jump repair, runs
of months) are loops, exactly as in the reference — no lag/lead approximation, no cascade
divergence. Parity with the reference is proven by
docs/deterioration_states/spark/tests/test_parity.py (recoverable from BUNDLE.md) — not a
file under src/tests/, since it needs pandas/numpy and is deliberately not a src/ runtime dep.

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
build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features

Nothing is dropped silently: every account in the history gets a sequences row with a
`build_status`; the classifier keeps only status 'ok' and the segment's current buckets.

Package layout (readability split of the former flat _dpd_journey.py; no behavior change):
    constants.py  BucketScheme, CC, RL, MODEL_ID_SEGMENT
    params.py     PARAM_DEFAULTS, JourneyParams, journey_params()
    _dates.py     _month_idx, _month_label, _month_col — shared by spark.py and logging.py
                  so those two never need to import each other
    core.py       the numpy-reference-mirroring per-account engine (journey_features etc.)
    states.py     the state tree (assign_state) + classify()
    history.py    Stage 1: build_history (not reference-constrained, free to decompose)
    spark.py      Stage 1/2 Spark orchestration (build_dpd_sequences, build_deterioration)
    logging.py    the two stats logs
This module re-exports everything reachable on the old flat module — no caller/test import
needs to change.
"""

from __future__ import annotations

# This module's whole job is re-exporting the package's submodules under the old flat
# module's name, so every caller/test import keeps working unchanged.
# pylint: disable=unused-import
from ._dates import _month_idx, _month_label
from .constants import CC, MODEL_ID_SEGMENT, RL, BucketScheme
from .core import (
    H,
    N,
    NO_PRIOR,
    P,
    R,
    _glitches,
    _mean,
    _repair,
    _runs,
    encode,
    journey_features,
)
from .history import _legacy_drop, build_history
from .logging import LOG, _log_sequence_stats, _log_state_stats
from .params import PARAM_DEFAULTS, JourneyParams, journey_params
from .spark import (
    _CLASSIFY_SCHEMA,
    _FEATURES,
    _HISTORY_SCHEMA,
    _idx_to_month_end,
    _month_col,
    _ship_by_value,
    _string_key,
    build_deterioration,
    build_dpd_sequences,
)
from .states import DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify
`````

New:

`````python
"""DPD-journey deterioration states: one engine for credit cards (CC) and loans (RL).

Spark gathers each account's monthly buckets into an array in ONE shuffle; the journey
logic then runs per account as a plain-Python port of the numpy reference
(docs/deterioration_states/dpd_states: features.py, states.py option B), with parity
tested by docs/deterioration_states/spark/tests/test_parity.py (outside src/: it needs
pandas and numpy). Rules: docs/deterioration_states/METHODOLOGY.md; where the code
differs: specs/A4_deterioration_conformance.md (D1-D6).

Run: the product wrappers call ``build_dpd_sequences`` (long history -> one row per
account: gap-filled monthly bucket array + audit, a ``build_status`` for every account)
and ``build_deterioration`` (sequences + spine -> one row per spine observation in the
segment, ``det_state`` and the journey features):
    kedro run --pipeline=crx_cc_a4_deterioration   (cc_60_180 / cc_180_plus)
    kedro run --pipeline=crx_rl_a4_deterioration   (rl_60_180 / rl_180_plus)

Every rule is written once on the CC scale ("canonical" = max(native + offset, 1); CC
offset 0, RL offset 1, so 0 and 1 are both "clean"): the 60-180 DPD spine is canonical
4-7 for both products, 180+ is canonical 8+. Outputs carry NATIVE buckets.

Modules:
    constants.py  BucketScheme, CC, RL (MODEL_ID_SEGMENT lives in _common)
    params.py     PARAM_DEFAULTS, JourneyParams, journey_params()
    _dates.py     _month_idx, _month_col
    core.py       the numpy-reference-mirroring per-account engine (journey_features etc.)
    states.py     the state tree (assign_state) + classify()
    history.py    Stage 1: build_history (not reference-constrained, free to decompose)
    spark.py      Stage 1/2 Spark orchestration (build_dpd_sequences, build_deterioration)
    logging.py    the state-distribution log and the opt-in sequence stats
    anchor.py     episode_start: the current episode's start per observation (D-A3-2)
"""

# ruff: noqa: F401

from __future__ import annotations

# Public: what the wrappers and the checks import.
from .._common import MODEL_ID_SEGMENT
from .anchor import episode_start
from .constants import CC, RL, BucketScheme
from .core import NO_PRIOR, encode, journey_features
from .logging import LOG, log_state_stats
from .params import PARAM_DEFAULTS, JourneyParams, journey_params
from .spark import build_deterioration, build_dpd_sequences
from .states import DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify

# isort: split

# Re-exported for the parity tests: H, N, P, R are the numpy reference's names.
from ._dates import _month_idx
from .core import H, N, P, R, _glitches, _mean, _repair, _runs
from .history import _legacy_drop, build_history
from .logging import _log_sequence_stats
from .spark import (
    _CLASSIFY_SCHEMA,
    _FEATURES,
    _HISTORY_SCHEMA,
    _idx_to_month_end,
    _month_col,
    _ship_by_value,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/_dates.py`
action: replace · base sha256 `f55b1a5836158cbf863d46bcdf06dc1d4566e133b1025c4282ce04b201ef7ab5` · base trailing newline: yes · new sha256 `a5596f5f03447260a4274733c6253902c6c9b303c9526537f2fb75e7f9ec1e59` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Month-arithmetic helpers, plain-Python and Spark-column alike.

`_month_col` is a Spark column expression, not a date-parsing helper like its neighbours —
it lives here anyway (rather than in spark.py) so that both spark.py and logging.py can
import it one-directionally from a common module. spark.py also calls into logging.py
(build_dpd_sequences/build_deterioration trigger the stats logs), so if `_month_col` lived
in spark.py, logging.py importing it back would make the two modules import each other.
"""

from __future__ import annotations

import datetime as _dt

from pyspark.sql import functions as F


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


def _month_label(d) -> str:
    """'YYYY Month' from a date-like value, e.g. 2026-08-31 -> '2026 August' —
    human-readable logging only, never a machine-compared value."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.strftime("%Y %B")


def _month_col(c) -> F.Column:
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")
`````

New:

`````python
"""Month arithmetic for ``spark.py``, in plain Python and as Spark columns.

A month index is ``year * 12 + month - 1``, so the gap between two months is a
subtraction.
"""

from __future__ import annotations

import datetime as _dt

from pyspark.sql import functions as F


def _month_idx(d) -> int:
    """Month as an integer (year * 12 + month - 1) — gap arithmetic without date math."""
    d = _dt.date.fromisoformat(str(d)[:10]) if not isinstance(d, _dt.date) else d
    return d.year * 12 + d.month - 1


def _month_col(c) -> F.Column:
    """Spark column twin of ``_month_idx``."""
    return (F.year(c) * 12 + F.month(c) - 1).cast("int")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/anchor.py`
action: add · new sha256 `051e6887a910acc2908f092a666d6537a793693462d66c2f3e8e2c24797a368b` · new trailing newline: yes

New:

`````python
"""The episode anchor: the month the current delinquency episode began, point in time.

A4 scores each spine row on the account's monthly history up to that row's month; the
episode (spell) is the last run of delinquent months in it (a cure back to current ends
one) and starts ``months_before_spell`` months into that history. Axes that window on
the episode read its start here instead of from a spell table (D-A3-2: the anchor is
the latest episode start as of the observation date).
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns, string_key

# The A4 row read is the latest one in the observation's own month.
_A4_MAX_AGE_M = 1


def episode_start(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for the base rows A4 scored in
    the observation month.

    ``episode_start`` is the first day of the month the current episode began, taken
    from the latest A4 row on or before the observation date in that month (CC: a
    billing date). ``episode_left_censored``: A4 cropped the history (source start,
    floor, truncation) and the episode already ran in its first kept month, so the true
    onset may be earlier and the consumer treats the anchor as unknown (A3: Q-25); an
    uncropped history delinquent from its first month has a true onset. Base rows A4
    did not score get no row.
    """
    require_columns(
        deterioration,
        [*GRAIN, "months_before_spell", "history_months"]
        + ["left_censored", "history_cropped"],
        "crx_<product>_a4_deterioration",
    )
    # months from the episode's first month to the row's month, back from history end
    months_back = F.col("history_months") - 1 - F.col("months_before_spell")
    censored = F.col("left_censored") & F.col("history_cropped")
    src = deterioration.select(
        string_key(deterioration).alias("account_id"),
        F.col("observation_date").cast("date").alias("a4_date"),
        F.add_months(F.trunc("observation_date", "month"), -months_back).alias(
            "episode_start"
        ),
        censored.alias("episode_left_censored"),
    )
    return pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="a4_date",
        value_cols=["episode_start", "episode_left_censored"],
        inclusive=True,
        max_age_months=_A4_MAX_AGE_M,
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/constants.py`
action: replace · base sha256 `7fdb29c788fb916fd1ea425dfda20f121d66c8d804afc8f7ac21a7ec0376ad58` · base trailing newline: yes · new sha256 `bc1fa7619917932017332f69221a0f7023fe34dee0cb7fb28823a1fdcf4f58a9` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Bucket-numbering constants shared by both segments and both products (CC/RL)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BucketScheme:
    """Per-domain native-bucket constants (CC vs RL)."""

    name: str
    offset: int  # canonical = max(native + offset, 1)
    top: int  # highest native bucket (the cap)
    repair_jumps: bool = True  # CC only: undo +2 billing-cycle jumps (_repair
    # in core.py). RL has no such billing artifact (int_loan_master is one
    # row/account/month) — a +2 jump there is always a genuine DPD move.

    @property
    def canon_top(self) -> int:
        """Highest canonical bucket (the cap), native top + offset."""
        return self.top + self.offset


CC = BucketScheme("cc", offset=0, top=9, repair_jumps=True)
RL = BucketScheme("rl", offset=1, top=7, repair_jumps=False)

# segment is fully determined by model_id — never an independently-settable override.
MODEL_ID_SEGMENT = {
    "cc_60_180": "60_180",
    "cc_180_plus": "180_plus",
    "rl_60_180": "60_180",
    "rl_180_plus": "180_plus",
}
`````

New:

`````python
"""Bucket-numbering constants shared by both segments and both products (CC/RL)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BucketScheme:
    """Per-domain native-bucket constants (CC vs RL)."""

    name: str
    offset: int  # canonical = max(native + offset, 1)
    top: int  # highest native bucket (the cap)
    repair_jumps: bool = True  # CC only: undo +2 billing-cycle jumps (_repair in
    # core.py). RL has no such billing artifact (int_loan_master is one row per
    # account and month): a +2 jump there is a genuine DPD move (conformance D4).

    @property
    def canon_top(self) -> int:
        """Highest canonical bucket (the cap), native top + offset."""
        return self.top + self.offset


CC = BucketScheme("cc", offset=0, top=9, repair_jumps=True)
RL = BucketScheme("rl", offset=1, top=7, repair_jumps=False)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/history.py`
action: replace · base sha256 `f48f61c6e371b4f90cf9959d3e5eae05323ecad467f44ce43429315a16bda7ae` · base trailing newline: yes · new sha256 `7f575a4b3be0ec6ae9eb3fd10be4a82be95cb8d5a7b185f6d266b511805e5dda` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Stage 1 core: monthly grid from raw rows.

Not reference-constrained (no counterpart in the numpy reference — it is the billing-
history gap-fill stage), so unlike core.py it is free to decompose internally.
"""

from __future__ import annotations


def _legacy_drop(best: dict[int, tuple[int, int]]) -> bool:
    """Would the old window-function rule have dropped this account? (any interior gap whose
    neighbours differ in NATIVE value, after keeping the latest row per month). Lets the
    first run reconcile with the old drop count."""
    ms = sorted(best)
    return any(b - a > 1 and best[a][1] != best[b][1] for a, b in zip(ms, ms[1:]))


# pylint: disable-next=too-many-locals
def _fill_gaps(
    vals: list,
    offset: int,
    fill_straight: bool,
    on_unresolvable: str,
    max_inferred_gap: int,
) -> tuple[list, list[int], list[int], list[int], int, bool]:
    """Step 3-4 of build_history's docstring: walk `vals` (one slot per month, `None` where
    unobserved) and fill each gap — clean-through (3a), straight-roll (3b), or short inferred
    (3c) — or mark it unresolvable (4): truncate everything up to it (`cut` advances) or signal
    a drop. Returns (vals, filled, rolled, inferred, cut, dropped) — month-indexes (relative to
    `vals`) for each fill rule, the truncation cut point, and whether `on_unresolvable == "drop"`
    was hit."""

    def canon(x):
        return max(x + offset, 1)

    cut = 0  # index of the first month kept
    filled, rolled, inferred = [], [], []  # indexes of filled months, by rule
    i = 0
    while i < len(vals):
        if vals[i] is not None:
            i += 1
            continue
        j = i
        while vals[j] is None:  # last month is observed: always stops
            j += 1
        left, right, k = vals[i - 1], vals[j], j - i
        if canon(left) == canon(right):  # CC 0 · 1 is clean-through, not a conflict
            vals[i:j] = [left] * k
            filled += range(i, j)
        elif fill_straight and canon(right) - canon(left) == k + 1:
            vals[i:j] = [canon(left) + s + 1 - offset for s in range(k)]
            rolled += range(i, j)
        elif k <= max_inferred_gap:
            cl, cr = canon(left), canon(right)
            vals[i:j] = [
                (max(cl, cr - (k - s)) if cr > cl else cl) - offset for s in range(k)
            ]
            vals[i:j] = [max(v, 0) for v in vals[i:j]]
            inferred += range(i, j)
        else:
            if on_unresolvable == "drop":
                return vals, filled, rolled, inferred, cut, True
            cut = j
        i = j
    return vals, filled, rolled, inferred, cut, False


# pylint: disable-next=too-many-positional-arguments,too-many-locals,too-many-branches,too-many-statements
def build_history(
    rows,
    first_raw_idx: int,
    global_min_idx: int,
    offset: int,
    fill_straight: bool = True,
    on_unresolvable: str = "truncate",
    repair_cycle_shift: bool = True,
    max_inferred_gap: int = 2,
) -> dict:
    """rows: (month_idx, day_ordinal, native_bucket) inside [floor, end], valid buckets only.

    1. billing-cycle shift: a month with two bills next to an EMPTY interior month gives one
       bill to that month (cycle date near month-end: bills on 31 Jan and 1 Mar, none in
       Feb -> the 1 Mar bill is February's). The earlier bill moves back if the previous
       month is empty, else the later bill moves forward;
    2. one value per month: the latest observation in the month (ties -> worst bucket);
    3. dense grid from the first to the last observed month; a gap is filled when
       a. both neighbours agree on the canonical scale (hold / clean through; CC 0 · 1), or
       b. the only path without a +2 jump is a straight roll (3 · 5 -> 3 4 5), or
       c. it is short (<= max_inferred_gap months): inferred — carry the left value and
          roll as late as possible (3 · 4 -> 3 3 4; 5 · 3 -> 5 5 3). Counted separately;
    4. any other gap is unresolvable: keep the months after the last one ('truncate', the
       history is then cropped) or drop the account ('drop');
    5. cropped = older history exists but is not used (history floor, truncation), or the
       first month is the first month of the whole source (opening date unknown).
    """
    out = {
        "build_status": "ok",
        "first_month_idx": None,
        "last_month_idx": None,
        "buckets": None,
        "history_cropped": None,
        "n_gap_months_filled": 0,
        "n_gap_months_rolled": 0,
        "n_gap_months_inferred": 0,
        "n_months_truncated": 0,
        "n_dup_month_rows": 0,
        "n_cycle_shift_moves": 0,
        "legacy_drop": False,
    }
    by_month: dict[int, list[tuple[int, int]]] = {}
    for m, day, bkt in rows or []:
        by_month.setdefault(m, []).append((day, bkt))
    if not by_month:
        out["build_status"] = "no_rows_in_window"
        return out
    out["legacy_drop"] = _legacy_drop({m: max(v) for m, v in by_month.items()})

    # Step 1: billing-cycle shift.
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

    # Step 2: one value per month (latest day, then worst bucket).
    best = {m: max(v) for m, v in by_month.items()}
    out["n_dup_month_rows"] = sum(len(v) for v in by_month.values()) - len(best)
    first, last = min(best), max(best)
    vals = [best[m][1] if m in best else None for m in range(first, last + 1)]

    # Steps 3-4: dense grid + gap fill / truncate / drop.
    vals, filled, rolled, inferred, cut, dropped = _fill_gaps(
        vals, offset, fill_straight, on_unresolvable, max_inferred_gap
    )
    if dropped:
        out["build_status"] = "dropped_unresolvable_gap"
        return out
    out["n_gap_months_filled"] = sum(
        1 for t in filled if t >= cut
    )  # counted in the kept part
    out["n_gap_months_rolled"] = sum(1 for t in rolled if t >= cut)
    out["n_gap_months_inferred"] = sum(1 for t in inferred if t >= cut)
    out["n_months_truncated"] = cut

    # Step 5: cropped flag.
    kept_first = first + cut
    out.update(
        first_month_idx=kept_first,
        last_month_idx=last,
        buckets=vals[cut:],
        history_cropped=bool(
            kept_first > first_raw_idx or first_raw_idx <= global_min_idx
        ),
    )
    return out
`````

New:

`````python
"""Stage 1 core: monthly grid from raw rows.

Not reference-constrained (no counterpart in the numpy reference — it is the billing-
history gap-fill stage), so unlike core.py it is free to decompose internally.
"""

from __future__ import annotations


def _legacy_drop(best: dict[int, tuple[int, int]]) -> bool:
    """Diagnostic: would the earlier window-function rule have dropped this account?
    (any interior gap whose neighbours differ in NATIVE value, after keeping the latest
    row per month)."""
    ms = sorted(best)
    return any(b - a > 1 and best[a][1] != best[b][1] for a, b in zip(ms, ms[1:]))


def _shift_cycle_bills(by_month: dict[int, list[tuple[int, int]]]) -> int:
    """Step 1 of build_history: give a month's extra bill to the empty month next to it.
    Edits ``by_month`` in place; returns the number of bills moved."""
    moves = 0
    lo, hi = min(by_month), max(by_month)
    for m in sorted(by_month):
        obs = sorted(set(by_month[m]))
        days = sorted({d for d, _ in obs})
        if len(days) < 2:
            continue
        if lo < m - 1 and m - 1 not in by_month:
            by_month[m - 1] = [x for x in obs if x[0] == days[0]]
            by_month[m] = [x for x in obs if x[0] != days[0]]
            moves += 1
        elif m + 1 < hi and m + 1 not in by_month:
            by_month[m + 1] = [x for x in obs if x[0] == days[-1]]
            by_month[m] = [x for x in obs if x[0] != days[-1]]
            moves += 1
    return moves


# pylint: disable-next=too-many-locals
def _fill_gaps(
    vals: list,
    offset: int,
    fill_straight: bool,
    on_unresolvable: str,
    max_inferred_gap: int,
) -> tuple[list, list[int], list[int], list[int], int, bool]:
    """Step 3-4 of build_history's docstring: walk `vals` (one slot per month, `None` where
    unobserved) and fill each gap — clean-through (3a), straight-roll (3b), or short inferred
    (3c) — or mark it unresolvable (4): truncate everything up to it (`cut` advances) or signal
    a drop. Returns (vals, filled, rolled, inferred, cut, dropped) — month-indexes (relative to
    `vals`) for each fill rule, the truncation cut point, and whether `on_unresolvable == "drop"`
    was hit."""

    def canon(x):
        return max(x + offset, 1)

    cut = 0  # index of the first month kept
    filled, rolled, inferred = [], [], []  # indexes of filled months, by rule
    i = 0
    while i < len(vals):
        if vals[i] is not None:
            i += 1
            continue
        j = i
        while vals[j] is None:  # last month is observed: always stops
            j += 1
        left, right, k = vals[i - 1], vals[j], j - i
        if canon(left) == canon(right):  # CC 0 · 1 is clean-through, not a conflict
            vals[i:j] = [left] * k
            filled += range(i, j)
        elif fill_straight and canon(right) - canon(left) == k + 1:
            vals[i:j] = [canon(left) + s + 1 - offset for s in range(k)]
            rolled += range(i, j)
        elif k <= max_inferred_gap:
            cl, cr = canon(left), canon(right)
            vals[i:j] = [
                (max(cl, cr - (k - s)) if cr > cl else cl) - offset for s in range(k)
            ]
            vals[i:j] = [max(v, 0) for v in vals[i:j]]
            inferred += range(i, j)
        else:
            if on_unresolvable == "drop":
                return vals, filled, rolled, inferred, cut, True
            cut = j
        i = j
    return vals, filled, rolled, inferred, cut, False


# pylint: disable-next=too-many-positional-arguments,too-many-locals
def build_history(
    rows,
    first_raw_idx: int,
    global_min_idx: int,
    offset: int,
    fill_straight: bool = True,
    on_unresolvable: str = "truncate",
    repair_cycle_shift: bool = True,
    max_inferred_gap: int = 2,
) -> dict:
    """rows: (month_idx, day_ordinal, native_bucket) inside [floor, end], valid buckets only.

    1. billing-cycle shift: a month with two bills next to an EMPTY interior month gives one
       bill to that month (cycle date near month-end: bills on 31 Jan and 1 Mar, none in
       Feb -> the 1 Mar bill is February's). The earlier bill moves back if the previous
       month is empty, else the later bill moves forward;
    2. one value per month: the latest observation in the month (ties -> worst bucket);
    3. dense grid from the first to the last observed month; a gap is filled when
       a. both neighbours agree on the canonical scale (hold / clean through; CC 0 · 1), or
       b. the only path without a +2 jump is a straight roll (3 · 5 -> 3 4 5), or
       c. it is short (<= max_inferred_gap months): inferred — carry the left value and
          roll as late as possible (3 · 4 -> 3 3 4; 5 · 3 -> 5 5 3). Counted separately;
    4. any other gap is unresolvable: keep the months after the last one ('truncate', the
       history is then cropped) or drop the account ('drop');
    5. cropped = older history exists but is not used (history floor, truncation), or the
       first month is the first month of the whole source (opening date unknown).
    """
    out = {
        "build_status": "ok",
        "first_month_idx": None,
        "last_month_idx": None,
        "buckets": None,
        "history_cropped": None,
        "n_gap_months_filled": 0,
        "n_gap_months_rolled": 0,
        "n_gap_months_inferred": 0,
        "n_months_truncated": 0,
        "n_dup_month_rows": 0,
        "n_cycle_shift_moves": 0,
        "legacy_drop": False,
    }
    by_month: dict[int, list[tuple[int, int]]] = {}
    for m, day, bkt in rows or []:
        by_month.setdefault(m, []).append((day, bkt))
    if not by_month:
        out["build_status"] = "no_rows_in_window"
        return out
    out["legacy_drop"] = _legacy_drop({m: max(v) for m, v in by_month.items()})

    # Step 1: billing-cycle shift.
    if repair_cycle_shift:
        out["n_cycle_shift_moves"] = _shift_cycle_bills(by_month)

    # Step 2: one value per month (latest day, then worst bucket).
    best = {m: max(v) for m, v in by_month.items()}
    out["n_dup_month_rows"] = sum(len(v) for v in by_month.values()) - len(best)
    first, last = min(best), max(best)
    vals = [best[m][1] if m in best else None for m in range(first, last + 1)]

    # Steps 3-4: dense grid + gap fill / truncate / drop.
    vals, filled, rolled, inferred, cut, dropped = _fill_gaps(
        vals, offset, fill_straight, on_unresolvable, max_inferred_gap
    )
    if dropped:
        out["build_status"] = "dropped_unresolvable_gap"
        return out
    out["n_gap_months_filled"] = sum(
        1 for t in filled if t >= cut
    )  # counted in the kept part
    out["n_gap_months_rolled"] = sum(1 for t in rolled if t >= cut)
    out["n_gap_months_inferred"] = sum(1 for t in inferred if t >= cut)
    out["n_months_truncated"] = cut

    # Step 5: cropped flag.
    kept_first = first + cut
    out.update(
        first_month_idx=kept_first,
        last_month_idx=last,
        buckets=vals[cut:],
        history_cropped=bool(
            kept_first > first_raw_idx or first_raw_idx <= global_min_idx
        ),
    )
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/logging.py`
action: replace · base sha256 `042112bb8eb56b8122bca6effff007bb26b53e6f7dccb2ec58c08c56b5bb7d83` · base trailing newline: yes · new sha256 `ba89a720f49ac59055cba71a606ea30f6e53451ec60cc65d39ca3e07db24d6a0` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Stage telemetry — state-distribution log is always-on; sequence stats are opt-in,
one extra aggregate job per node when log_stats=True."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import Window
from pyspark.sql import functions as F

from ._dates import _month_col, _month_idx, _month_label
from .constants import BucketScheme
from .params import JourneyParams

LOG = logging.getLogger(__name__)


def _log_sequence_stats(
    seq: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> None:
    r = (
        seq.agg(
            F.count("*").alias("accounts"),
            *[
                F.sum((F.col("build_status") == s).cast("int")).alias(s)
                for s in (
                    "ok",
                    "no_rows_in_window",
                    "no_valid_rows",
                    "dropped_unresolvable_gap",
                )
            ],
            F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
            F.sum((F.col("n_months_truncated") > 0).cast("int")).alias(
                "truncated_accounts"
            ),
            F.sum("n_gap_months_filled").alias("gap_months_filled"),
            F.sum("n_gap_months_rolled").alias("gap_months_rolled"),
            F.sum("n_gap_months_inferred").alias("gap_months_inferred"),
            F.sum("n_cycle_shift_moves").alias("cycle_shift_moves"),
            F.sum(F.col("legacy_drop").cast("int")).alias("legacy_rule_would_drop"),
            F.sum("n_dup_month_rows").alias("dup_month_rows"),
            F.sum("n_invalid_rows").alias("invalid_rows"),
            F.min("first_month").alias("first_month"),
            F.max("last_month").alias("last_month"),
        )
        .first()
        .asDict()
    )
    LOG.info(
        "build_%s_dpd_sequences [end %s, floor %s, gaps %s]: %s",
        scheme.name,
        params.end_date,
        params.floor_date,
        params.on_unresolvable_gap,
        r,
    )


def _log_state_stats(
    out: DataFrame, end_date: str, scheme: BucketScheme, params: JourneyParams
) -> None:
    """det_state distribution for the latest month of the crx modelling date range
    (persona_end_date's calendar month, matched via `_month_col` — NOT an exact-day
    filter: CC billing dates land on a different day per account within the month, so
    `observation_date == persona_end_date` keeps almost none of the population). `out`
    is point-in-time (one row per spine row, not one row per account), so an
    unrestricted groupBy would also mix every historical month together — restrict to
    the target month, then keep the latest row per account within it (in case an
    account has more than one observation that month). Same always-on logging
    convention and format as cc_a2_locatability_v2/cc_a3_payment_credibility's own
    _log_a2_v2_stats/_log_a3_stats."""
    try:
        end_idx = _month_idx(end_date)
        same_month = out.where(_month_col(F.col("observation_date")) == F.lit(end_idx))
        w = Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
        snap = (
            same_month.withColumn("_rn", F.row_number().over(w))
            .where(F.col("_rn") == 1)
            .drop("_rn")
        )
        rows = snap.groupBy("det_state").agg(F.count("*").alias("n")).collect()
        n_total = sum(r["n"] for r in rows)
        LOG.info(
            "build_%s_deterioration [%s]: total accounts (%s) = %d",
            scheme.name,
            params.segment,
            _month_label(end_date),
            n_total,
        )
        for r in sorted(rows, key=lambda r: -r["n"]):
            pct = 100.0 * r["n"] / max(n_total, 1)
            LOG.info(
                "  det_state=%-28s n=%7d  (%.1f%%)", str(r["det_state"]), r["n"], pct
            )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "build_%s_deterioration: stats logging failed: %s", scheme.name, exc
        )
`````

New:

`````python
"""Stage telemetry — the state-distribution log is always on (``_common``'s format,
shared with every axis); sequence stats are opt-in, one extra aggregate job per node
when log_stats=True."""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import log_latest_month
from .constants import BucketScheme
from .params import JourneyParams

LOG = logging.getLogger(__name__)


# Logs the build_status counts and the gap, cycle-shift and invalid-row totals of
# ``seq``: one extra aggregate job, run only when ``log_stats`` is set.
def _log_sequence_stats(
    seq: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> None:
    r = (
        seq.agg(
            F.count("*").alias("accounts"),
            *[
                F.sum((F.col("build_status") == s).cast("int")).alias(s)
                for s in (
                    "ok",
                    "no_rows_in_window",
                    "no_valid_rows",
                    "dropped_unresolvable_gap",
                )
            ],
            F.sum(F.col("history_cropped").cast("int")).alias("cropped"),
            F.sum((F.col("n_months_truncated") > 0).cast("int")).alias(
                "truncated_accounts"
            ),
            F.sum("n_gap_months_filled").alias("gap_months_filled"),
            F.sum("n_gap_months_rolled").alias("gap_months_rolled"),
            F.sum("n_gap_months_inferred").alias("gap_months_inferred"),
            F.sum("n_cycle_shift_moves").alias("cycle_shift_moves"),
            F.sum(F.col("legacy_drop").cast("int")).alias("legacy_rule_would_drop"),
            F.sum("n_dup_month_rows").alias("dup_month_rows"),
            F.sum("n_invalid_rows").alias("invalid_rows"),
            F.min("first_month").alias("first_month"),
            F.max("last_month").alias("last_month"),
        )
        .first()
        .asDict()
    )
    LOG.info(
        "build_%s_dpd_sequences [end %s, floor %s, gaps %s]: %s",
        scheme.name,
        params.end_date,
        params.floor_date,
        params.on_unresolvable_gap,
        r,
    )


def log_state_stats(
    out: DataFrame, end_date: str, scheme: BucketScheme, params: JourneyParams
) -> None:
    """det_state distribution of persona_end_date's month, one row per account."""
    log_latest_month(
        out,
        "det_state",
        f"a4_deterioration [{scheme.name}_{params.segment}]",
        end_date,
        latest_per_account=True,
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/params.py`
action: replace · base sha256 `0e0e8f0450b7fc0102cda7b1932d3cf7a609eb805e25ec283550e227f946411b` · base trailing newline: yes · new sha256 `735a0f94caac633f2e3e62d9e85d5aaa27401b9f4427e72569546d07db38abfe` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Run parameters: defaults, the resolved dataclass, and the merge/validate entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .constants import BucketScheme, MODEL_ID_SEGMENT

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    # Independently overridable for the 180_plus segment (T43 2026-10-20 PROD run: the
    # shared floor left 99.07% of the gt2y chargeoff-age vintage "unknown" — their journey
    # start is almost always before the floor by construction). Defaults to the same value
    # as cc_history_floor_date so today's output is unchanged; override to relax/remove the
    # floor for 180_plus once the pre-2024 data-quality tradeoff is decided.
    "cc_history_floor_date_180_plus": "2024-01-01",
    "rl_history_floor_date": None,
    "on_unresolvable_gap": "truncate",  # "truncate" (keep months after the gap) or "drop"
    "fill_straight_roll_gaps": True,  # 3 · 5 -> 3 4 5: the only path without a +2 jump
    "repair_cycle_shift": True,  # two bills in one month + empty neighbour month
    "max_inferred_gap_months": 2,  # shorter ambiguous gaps are inferred (0 = never)
    "log_stats": False,  # one extra aggregate job per node when True
}


@dataclass(frozen=True)
# pylint: disable-next=too-many-instance-attributes
class JourneyParams:
    """Resolved dpd_journey run parameters (defaults merged with crx_persona overrides)."""

    end_date: str
    floor_date: str | None
    segment: str
    on_unresolvable_gap: str
    fill_straight_roll_gaps: bool
    repair_cycle_shift: bool
    max_inferred_gap_months: int
    log_stats: bool


def journey_params(
    crx_persona: dict, scheme: BucketScheme, model_id: str
) -> JourneyParams:
    """Resolve PARAM_DEFAULTS + crx_persona["dpd_journey"] overrides into a JourneyParams.
    segment is derived from model_id (MODEL_ID_SEGMENT) — not an overridable param."""
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    # a stale key (e.g. the removed det_option, or a removed segment override) must not
    # be silently ignored
    if unknown:
        raise ValueError(
            f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}"
        )
    p = {**PARAM_DEFAULTS, **given}
    if model_id not in MODEL_ID_SEGMENT:
        raise ValueError(
            f"model_id must be one of {sorted(MODEL_ID_SEGMENT)}, got {model_id!r}"
        )
    segment = MODEL_ID_SEGMENT[model_id]
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    floor_key = (
        "cc_history_floor_date_180_plus"
        if scheme.name == "cc" and segment == "180_plus"
        else f"{scheme.name}_history_floor_date"
    )
    return JourneyParams(
        end_date=str(crx_persona["persona_end_date"]),
        floor_date=p[floor_key],
        segment=segment,
        on_unresolvable_gap=p["on_unresolvable_gap"],
        fill_straight_roll_gaps=bool(p["fill_straight_roll_gaps"]),
        repair_cycle_shift=bool(p["repair_cycle_shift"]),
        max_inferred_gap_months=int(p["max_inferred_gap_months"] or 0),
        log_stats=bool(p["log_stats"]),
    )
`````

New:

`````python
"""Run parameters: defaults, the resolved dataclass, and the merge/validate entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from .._common import SEG_180_PLUS
from .._common import segment as model_segment
from .constants import BucketScheme

# Read from params:crx_persona -> dpd_journey (all optional). persona_end_date is required.
PARAM_DEFAULTS = {
    # CC only, TEMPORARY: billing history before this date has known data-quality issues.
    # Set to null once the source is fixed. RL history is trusted in full.
    "cc_history_floor_date": "2024-01-01",
    # Overridable for the 180_plus segment alone: the journey of most long charged-off
    # accounts starts before the shared floor, which leaves them "unknown". Defaults to
    # cc_history_floor_date; override to relax or remove the floor for 180_plus
    # (conformance D5).
    "cc_history_floor_date_180_plus": "2024-01-01",
    "rl_history_floor_date": None,
    "on_unresolvable_gap": "truncate",  # "truncate" (keep months after the gap) or "drop"
    "fill_straight_roll_gaps": True,  # 3 · 5 -> 3 4 5: the only path without a +2 jump
    "repair_cycle_shift": True,  # two bills in one month + empty neighbour month
    "max_inferred_gap_months": 2,  # shorter ambiguous gaps are inferred (0 = never)
    "log_stats": False,  # one extra aggregate job per node when True
}


@dataclass(frozen=True)
# pylint: disable-next=too-many-instance-attributes
class JourneyParams:
    """Resolved dpd_journey run parameters (defaults merged with crx_persona overrides)."""

    end_date: str
    floor_date: str | None
    segment: str
    on_unresolvable_gap: str
    fill_straight_roll_gaps: bool
    repair_cycle_shift: bool
    max_inferred_gap_months: int
    log_stats: bool


def journey_params(
    crx_persona: dict, scheme: BucketScheme, model_id: str
) -> JourneyParams:
    """Resolve PARAM_DEFAULTS + crx_persona["dpd_journey"] overrides into a JourneyParams.
    segment is derived from model_id (_common.segment) — not an overridable param."""
    given = crx_persona.get("dpd_journey") or {}
    unknown = sorted(set(given) - set(PARAM_DEFAULTS))
    # a stale key must not be silently ignored
    if unknown:
        raise ValueError(
            f"dpd_journey: unknown parameter(s) {unknown}; allowed {sorted(PARAM_DEFAULTS)}"
        )
    p = {**PARAM_DEFAULTS, **given}
    segment = model_segment(model_id)
    if p["on_unresolvable_gap"] not in ("truncate", "drop"):
        raise ValueError("dpd_journey.on_unresolvable_gap must be 'truncate' or 'drop'")
    floor_key = (
        "cc_history_floor_date_180_plus"
        if scheme.name == "cc" and segment == SEG_180_PLUS
        else f"{scheme.name}_history_floor_date"
    )
    return JourneyParams(
        end_date=str(crx_persona["persona_end_date"]),
        floor_date=p[floor_key],
        segment=segment,
        on_unresolvable_gap=p["on_unresolvable_gap"],
        fill_straight_roll_gaps=bool(p["fill_straight_roll_gaps"]),
        repair_cycle_shift=bool(p["repair_cycle_shift"]),
        max_inferred_gap_months=int(p["max_inferred_gap_months"] or 0),
        log_stats=bool(p["log_stats"]),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py`
action: replace · base sha256 `9c3473ed368bfc2f4dc6b008dfda513ea6753dd6088f8aa1f930f6ed015f29fa` · base trailing newline: yes · new sha256 `d8124294bc0fdf39f3bc367d74480dedbb176e659375e88956ef39751475878e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Spark side: scoping, the history floor, and ONE shuffle that gathers each account's
monthly buckets into an array; the per-account core (history.py/states.py) then runs inside
the UDFs. Two stages (two Kedro nodes per product):

build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features
"""

from __future__ import annotations

import logging
import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from ._dates import _month_col, _month_idx
from .constants import BucketScheme
from .history import build_history
from .logging import _log_sequence_stats, _log_state_stats
from .params import JourneyParams
from .states import DISPLAY_NAMES, classify

LOG = logging.getLogger(__name__)

_PACKAGE = __name__.rsplit(".", 1)[0]
_SUBMODULES = (
    "constants",
    "params",
    "_dates",
    "core",
    "states",
    "history",
    "spark",
    "logging",
)


def _ship_by_value() -> None:
    """Pickle every module of this package BY VALUE into the UDFs, so executors do not need
    the Kedro project installed (cloudpickle >= 2.0, bundled with PySpark >= 3.3). UDF
    closures reach build_history (history.py) and classify (states.py), not only this module
    — registering only this module (as the flat _dpd_journey.py once did) would leave those
    on pickle-by-reference, which only "works" locally (shared sys.path) and breaks on a
    real executor. If the project is installed on the executors this is harmless."""
    try:
        from pyspark import cloudpickle  # pylint: disable=import-outside-toplevel

        if not hasattr(cloudpickle, "register_pickle_by_value"):
            return  # pragma: no cover — older PySpark
        for name in (_PACKAGE, *(f"{_PACKAGE}.{m}" for m in _SUBMODULES)):
            mod = sys.modules.get(name)
            if mod is not None:
                cloudpickle.register_pickle_by_value(mod)
    except (
        Exception  # pylint: disable=broad-exception-caught
    ) as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning(
            "could not register %s for pickle-by-value (%s); the package must be "
            "importable on the executors",
            _PACKAGE,
            exc,
        )


_HISTORY_SCHEMA = T.StructType(
    [
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
    ]
)

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None),
    ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()),
    ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()),
    ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()),
    ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()),
    ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()),
    ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()),
    ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType(
    [T.StructField("det_state", T.StringType())]
    + [T.StructField(n, t) for n, t in _FEATURES if t is not None]
)


def _string_key(df: DataFrame, col: str = "account_id") -> F.Column:
    """Safe string-cast join key — a Double/Decimal account_id cast straight to string
    renders as "1.23456789E8" and silently zeroes an == join. Same helper as
    rl_full_history/nodes.py._string_key (R18 — duplicated, not imported: that is a
    private helper in an unrelated pipeline module with no stability contract)."""
    dtype = df.schema[col].dataType
    c = F.col(col)
    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
        c = c.cast("long")
    return F.trim(c.cast("string"))


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(
        F.expr(f"make_date(cast({c} div 12 as int), cast({c} % 12 + 1 as int), 1)")
    )


# pylint: disable-next=too-many-locals
def build_dpd_sequences(
    history: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    restructure: DataFrame | None = None,
) -> DataFrame:
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
    missing = [
        c for c in ("account_id", "obs_date", "dlq_bucket") if c not in history.columns
    ]
    if missing:
        raise ValueError(
            f"build_dpd_sequences: history is missing {missing}; has {sorted(history.columns)}"
        )
    _ship_by_value()
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None

    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(
            F.when(
                in_window,
                F.struct(
                    m.alias("m"),
                    F.datediff(
                        F.col("obs_date").cast("date"), F.lit("1970-01-01")
                    ).alias("d"),
                    bucket.alias("b"),
                ),
            )
        ).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias(
            "n_invalid_rows"
        ),  # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    per_acc = per_acc.crossJoin(F.broadcast(source_min))

    offset, fill, how = (
        scheme.offset,
        params.fill_straight_roll_gaps,
        params.on_unresolvable_gap,
    )
    shift, max_inf = params.repair_cycle_shift, params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history(
            [(r["m"], r["d"], r["b"]) for r in rows],
            first_raw,
            global_min,
            offset,
            fill,
            how,
            shift,
            max_inf,
        )

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias(
            "dpd_string"
        ),
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
        out = out.join(
            restructure.select(
                "account_id", F.col("restructure_blind_spot_flag").alias("_rs")
            ),
            "account_id",
            "left",
        )
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop(
        "_rf", "_rs"
    )
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


# pylint: disable-next=too-many-locals
def build_deterioration(
    sequences: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    spine: DataFrame,
    log_states: bool = True,
) -> DataFrame:
    """sequences: output of build_dpd_sequences (one row per account). spine: 2-column
    (account_id, observation_date) — one row per point-in-time state to classify, e.g.
    cc_spine/rl_spine already filtered to the run's model_id/DLQ-band scope. Classifies
    EVERY spine row, not one row per account: each row's billing history is the account's
    Stage 1 dlq_buckets array truncated up to and including that row's own month, run
    through the same, unmodified classify() engine.

    A spine row is kept only if its month falls inside the account's observed/gap-filled
    window (first_month..last_month) and the truncated bucket is itself delinquent
    (canonical >= 2) — both explainable "no billing history at this date" cases, not a
    silent drop. No model_id/segment bucket-set filter is applied here: that scoping is
    inherited for free from the spine's own population.

    Returns one row per (account_id, observation_date):
        account_id, observation_date, det_state, det_state_label, det_segment,
        current_bucket (native, as of this row's date), <features>, history_months
        (months observed as of this row), history_cropped, n_months_truncated,
        restructure_blind_spot_flag, computed_at
    """
    _ship_by_value()
    segment = params.segment
    offset, top = scheme.offset, scheme.canon_top
    repair = scheme.repair_jumps
    end_dt = F.to_date(F.lit(params.end_date))

    seq = (
        sequences.where(F.col("build_status") == "ok")
        .withColumn("_first_idx", _month_col(F.col("first_month")))
        .withColumn("_last_idx", _month_col(F.col("last_month")))
        .withColumn("_key", _string_key(sequences, "account_id"))
    )

    sp = spine.where(F.col("observation_date").cast("date") <= end_dt).select(
        _string_key(spine, "account_id").alias("_key"),
        F.col("observation_date").cast("date").alias("observation_date"),
    )

    # join on the safe string key only — account_id in the output keeps seq's own
    # native type (long for CC, string for RL), never the stringified join key.
    joined = sp.join(seq, "_key", "inner")
    obs_idx = _month_col(F.col("observation_date"))
    trunc_len = (obs_idx - F.col("_first_idx") + 1).cast("int")
    joined = (
        joined.withColumn("_obs_idx", obs_idx)
        .withColumn("_trunc_len", trunc_len)
        .where((F.col("_trunc_len") >= 1) & (F.col("_obs_idx") <= F.col("_last_idx")))
    )

    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot):
        sl = list(buckets)[:trunc_len_]
        if not sl or max(sl[-1] + offset, 1) < 2:
            return None
        return classify(
            sl,
            bool(cropped),
            offset,
            top,
            repair,
            bool(restructure_blind_spot),
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema)(
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
        ),
    ).where(F.col("_s").isNotNull())

    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    feat_cols = [
        F.col(f"_s.{f.name}").alias(f.name)
        for f in schema.fields
        if f.name != "det_state"
    ]
    out = res.select(
        F.col("account_id"),
        F.col("observation_date"),
        F.col("_s.det_state").alias("det_state"),
        labels[F.col("_s.det_state")].alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        F.element_at("dlq_buckets", F.col("_trunc_len")).alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("_trunc_len").alias("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always-on, like every other persona axis's own state-distribution log
    # (cc_a2_locatability_v2/cc_a3_payment_credibility's own _log_*_stats) — not
    # gated behind log_stats, which here only controls the heavier Stage 1
    # build_dpd_sequences telemetry above. The month filter inside _log_state_stats
    # pushes down through the join, so this does not force materialization of the
    # full point-in-time result.
    if log_states:  # False: the caller unions two runs and logs the result
        _log_state_stats(out, params.end_date, scheme, params)
    return out
`````

New:

`````python
"""Spark side: scoping, the history floor, and ONE shuffle that gathers each account's
monthly buckets into an array; the per-account core (history.py/states.py) then runs inside
the UDFs. Two stages (two Kedro nodes per product):

build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features
"""

from __future__ import annotations

import logging
import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns, string_key
from ..scoring_engine import state_label
from ._dates import _month_col, _month_idx
from .constants import BucketScheme
from .history import build_history
from .logging import _log_sequence_stats, log_state_stats
from .params import JourneyParams
from .states import DISPLAY_NAMES, classify

LOG = logging.getLogger(__name__)

_PACKAGE = __name__.rsplit(".", 1)[0]
_SUBMODULES = (
    "constants",
    "params",
    "_dates",
    "core",
    "states",
    "history",
    "spark",
    "logging",
)


def _ship_by_value() -> None:
    """Pickle every module of this package BY VALUE into the UDFs (cloudpickle >= 2.0),
    so executors need not have the Kedro project: the UDF closures reach history.py and
    states.py too, and by-reference pickling only works locally (shared sys.path)."""
    try:
        from pyspark import cloudpickle  # pylint: disable=import-outside-toplevel

        if not hasattr(cloudpickle, "register_pickle_by_value"):
            return  # pragma: no cover — older PySpark
        for name in (_PACKAGE, *(f"{_PACKAGE}.{m}" for m in _SUBMODULES)):
            mod = sys.modules.get(name)
            if mod is not None:
                cloudpickle.register_pickle_by_value(mod)
    except (
        Exception  # pylint: disable=broad-exception-caught
    ) as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning(
            "could not register %s for pickle-by-value (%s); the package must be "
            "importable on the executors",
            _PACKAGE,
            exc,
        )


_HISTORY_SCHEMA = T.StructType(
    [
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
    ]
)

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None),
    ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()),
    ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()),
    ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()),
    ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()),
    ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()),
    ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()),
    ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType(
    [T.StructField("det_state", T.StringType())]
    + [T.StructField(n, t) for n, t in _FEATURES if t is not None]
)


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(
        F.expr(f"make_date(cast({c} div 12 as int), cast({c} % 12 + 1 as int), 1)")
    )


def _monthly_rows_per_account(
    history: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> DataFrame:
    """One row per account: `_rows` (array of struct m, d, b: month index, day number,
    native bucket; windowed and valid only), `_first_raw` and `n_invalid_rows`, plus
    `_rf` if `history` has `restructure_flag`; `_global_min` is the first valid month
    of the whole history."""
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None
    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(
            F.when(
                in_window,
                F.struct(
                    m.alias("m"),
                    F.datediff(
                        F.col("obs_date").cast("date"), F.lit("1970-01-01")
                    ).alias("d"),
                    bucket.alias("b"),
                ),
            )
        ).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias(
            "n_invalid_rows"
        ),  # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    return per_acc.crossJoin(F.broadcast(source_min))


def build_dpd_sequences(
    history: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    restructure: DataFrame | None = None,
) -> DataFrame:
    """Stage 1: monthly rows per account -> one shuffle -> `build_history` per account.
    history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
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
    require_columns(history, ["account_id", "obs_date", "dlq_bucket"], "A4 history")
    _ship_by_value()
    per_acc = _monthly_rows_per_account(history, scheme, params)

    offset, shift = scheme.offset, params.repair_cycle_shift
    fill, how = params.fill_straight_roll_gaps, params.on_unresolvable_gap
    max_inf = params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):  # month rows, first month -> history struct
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history(
            [(r["m"], r["d"], r["b"]) for r in rows],
            first_raw,
            global_min,
            offset,
            fill,
            how,
            shift,
            max_inf,
        )

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias(
            "dpd_string"
        ),
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
        out = out.join(
            restructure.select(
                "account_id", F.col("restructure_blind_spot_flag").alias("_rs")
            ),
            "account_id",
            "left",
        )
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop(
        "_rf", "_rs"
    )
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


def _spine_rows_with_history(
    sequences: DataFrame, spine: DataFrame, params: JourneyParams
) -> DataFrame:
    """Spine rows (account_id, observation_date) joined to the account's `ok` sequence
    row, kept when the observation month lies in first_month..last_month. Adds
    `_obs_idx` and `_trunc_len`, the number of history months up to that month."""
    end_dt = F.to_date(F.lit(params.end_date))
    seq = (
        sequences.where(F.col("build_status") == "ok")
        .withColumn("_first_idx", _month_col(F.col("first_month")))
        .withColumn("_last_idx", _month_col(F.col("last_month")))
        .withColumn("_key", string_key(sequences))
    )
    sp = spine.where(F.col("observation_date").cast("date") <= end_dt).select(
        string_key(spine).alias("_key"),
        F.col("observation_date").cast("date").alias("observation_date"),
    )

    # join on the safe string key only — account_id in the output keeps seq's own
    # native type (long for CC, string for RL), never the stringified join key.
    obs_idx = _month_col(F.col("observation_date"))
    trunc_len = (obs_idx - F.col("_first_idx") + 1).cast("int")
    return (
        sp.join(seq, "_key", "inner")
        .withColumn("_obs_idx", obs_idx)
        .withColumn("_trunc_len", trunc_len)
        .where((F.col("_trunc_len") >= 1) & (F.col("_obs_idx") <= F.col("_last_idx")))
    )


def build_deterioration(
    sequences: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    spine: DataFrame,
    log_states: bool = True,
) -> DataFrame:
    """Stage 2: spine rows + sequences -> history cut at each row's month -> `classify`.
    sequences: output of build_dpd_sequences (one row per account). spine: 2-column
    (account_id, observation_date) — one row per point-in-time state to classify, e.g.
    cc_spine/rl_spine already filtered to the run's model_id/DLQ-band scope. Classifies
    EVERY spine row, not one row per account: each row's billing history is the account's
    Stage 1 dlq_buckets array truncated up to and including that row's own month, run
    through the same, unmodified classify() engine.

    A spine row is kept only if its month falls inside the account's observed/gap-filled
    window (first_month..last_month) and the truncated bucket is itself delinquent
    (canonical >= 2) — both explainable "no billing history at this date" cases, not a
    silent drop. No model_id/segment bucket-set filter is applied here: that scoping is
    inherited for free from the spine's own population.

    Returns one row per (account_id, observation_date):
        account_id, observation_date, det_state, det_state_label, det_segment,
        current_bucket (native, as of this row's date), <features>, history_months
        (months observed as of this row), history_cropped, n_months_truncated,
        restructure_blind_spot_flag, computed_at
    """
    _ship_by_value()
    segment = params.segment
    offset, top = scheme.offset, scheme.canon_top
    repair = scheme.repair_jumps
    joined = _spine_rows_with_history(sequences, spine, params)

    # in: buckets, truncation length, cropped, blind-spot flag; out: classify struct
    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot):
        sl = list(buckets)[:trunc_len_]
        if not sl or max(sl[-1] + offset, 1) < 2:
            return None
        return classify(
            sl, bool(cropped), offset, top, repair, bool(restructure_blind_spot)
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema)(
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
        ),
    ).where(F.col("_s").isNotNull())

    feat_cols = [
        F.col(f"_s.{f.name}").alias(f.name)
        for f in schema.fields
        if f.name != "det_state"
    ]
    out = res.select(
        F.col("account_id"),
        F.col("observation_date"),
        F.col("_s.det_state").alias("det_state"),
        state_label("_s.det_state", DISPLAY_NAMES).alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        F.element_at("dlq_buckets", F.col("_trunc_len")).alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("_trunc_len").alias("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always on, as on every axis (_common.log_latest_month); log_stats only gates the
    # Stage 1 telemetry above. The month filter pushes down through the join.
    if log_states:  # False: the caller unions two runs and logs the result
        log_state_stats(out, params.end_date, scheme, params)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/states.py`
action: replace · base sha256 `40be38e3fa8c6a71d1fef19b4dbb18e1a7fc292ffd4e8de2617c64889a0da797` · base trailing newline: yes · new sha256 `4be077c9914c12f845d8c57c1ff5c4333fcd1fe30f5dfa9afc2086df96e3bf4b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The state tree (states.py, option B) — ONE tree for 60-180 and 180+."""

from __future__ import annotations

from .core import journey_features

STATE_RULES = {
    "epd_max_history": 3,  # [business] months of history before the spell (blip incl.)
    "epd_max_blips": 1,  # [business]
    "straight_max_runup": 3,  # last clean month -> first month at 4
    "stabilized_min_in_band": 5,  # [business] of the last 6 months within today's bucket ±1
    "stabilized_long_run_months": 6,  # [business]
    "stabilized_long_run_max_rise": 1,  # [business]
    "stabilized_max_bucket": 7,  # [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "repeat_min_prior_peak": 3,  # [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,  # [business] ... and ended <= 12 months before this one
    "seasoned_min_months": 12,  # [business] months on book before the spell
}

STATES = [
    "unknown",
    "early_payment_default",
    "stabilized",
    "repeat_delinquent",
    "straight_roller_seasoned",
    "straight_roller_early_life",
    "slow_roller",
]

DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "repeat_delinquent": "Repeat delinquent",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
}


# pylint: disable-next=too-many-return-statements,too-many-arguments
def assign_state(
    f: dict,
    cropped: bool,
    restructure_blind_spot: bool = False,
) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    Q0 journey start not observed (oldest observed month delinquent AND history_blind —
                             history before the window is genuinely missing, or this
                             account is a restructured entry whose predecessor contract's
                             history is invisible) -> stabilized if Q2, else unknown
    Q1 early payment default <=3 months before the spell, <=1 blip, no earlier spell, no payment
                             in the spell (holds at the ceiling are not payments), not
                             history_blind
    Q2 stabilized            60-180 only (today <= CC 7 / RL 6): 5 of the last 6 months within
                             today's bucket ±1, or >=6 months since first reaching 4 and at most
                             1 bucket higher than 6 months ago
    Q3 repeat delinquent     an earlier spell reached 3, cured, ended <=12 months before this one
    Q4 straight roller       run-up to 4 took <=3 months: seasoned (>=12 months on book, or
                             history_blind = older than the window / restructured) / early life
    else slow roller
    """
    p = STATE_RULES
    # "Genuinely observed from a clean start" covers two distinct blind spots: a Stage-1
    # window crop (floor date / unresolvable gap / dataset edge), OR a restructured account
    # whose own first row is a fresh contract_id, not a fresh delinquency journey — the
    # predecessor contract's history is invisible to this engine either way (R13). A normal
    # (non-restructured) CC account structurally cannot observe its first-ever billing cycle
    # already delinquent (DPD >= 2 requires a prior unpaid cycle to exist first); RL's
    # native-bucket-1 start remains legitimate for a genuinely fresh, non-restructured loan.
    history_blind = cropped or restructure_blind_spot
    # Q2 stabilized — computed up front: both Q0 and the main sequence below consult it.
    stab = f["b_now"] <= p["stabilized_max_bucket"] and (
        f["last6_in_band"] >= p["stabilized_min_in_band"]
        or (
            f["months_since_4"] >= p["stabilized_long_run_months"]
            and f["chg_6m"] <= p["stabilized_long_run_max_rise"]
        )
    )
    # Q0 — only a confidence guard when history before the window is genuinely
    # missing (history_blind). When history_blind=False we trust we've seen the
    # whole observed journey, so a delinquent oldest month is not evidence of
    # missing history (e.g. RL native bucket 1 = "1-30 DPD" already counts as
    # delinquent for a loan that missed its very first EMI) — fall through to
    # the normal cascade instead.
    if f["starts_delinquent"] and history_blind:
        return "stabilized" if stab else "unknown"
    # Q1
    if (
        f["months_before_spell"] <= p["epd_max_history"]
        and f["n_blips"] <= p["epd_max_blips"]
        and f["n_prior_episodes"] == 0
        and f["spell_pay_events"] == 0
        and not history_blind
    ):
        return "early_payment_default"
    # Q2
    if stab:
        return "stabilized"
    # Q3
    if f["gap_prior_peak3"] <= p["repeat_window_months"]:
        return "repeat_delinquent"
    # Q4
    if f["runup_len"] <= p["straight_max_runup"]:
        if f["months_before_spell"] >= p["seasoned_min_months"] or history_blind:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    # else
    return "slow_roller"


def classify(  # pylint: disable=too-many-positional-arguments
    buckets_native: list[int],
    cropped: bool,
    offset: int,
    canon_top: int,
    repair: bool = True,
    restructure_blind_spot: bool = False,
) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features(
        [max(x + offset, 1) for x in buckets_native], canon_top, repair
    )
    f["det_state"] = assign_state(f, cropped, restructure_blind_spot)
    return f
`````

New:

`````python
"""The A4 state tree (METHODOLOGY.md option B): ONE tree for 60-180 and 180+.

Rules Q0-Q4 and the thresholds in ``STATE_RULES`` follow the methodology; the code
differs in D1 (Q0 needs history_blind) and D2 (restructured accounts are
history_blind), see specs/A4_deterioration_conformance.md.
"""

from __future__ import annotations

from typing import Any

from .core import journey_features

STATE_RULES = {
    "epd_max_history": 3,  # Q1 [business] months of history before the spell (+ blip)
    "epd_max_blips": 1,  # Q1 [business]
    "straight_max_runup": 3,  # Q4 last clean month -> first month at 4
    "stabilized_min_in_band": 5,  # Q2 [business] of last 6 months in today's bucket ±1
    "stabilized_long_run_months": 6,  # Q2 [business]
    "stabilized_long_run_max_rise": 1,  # Q2 [business]
    # Q2 [business] canonical: CC 7 / RL 6 = 151-180 DPD. Never at 180+.
    "stabilized_max_bucket": 7,
    "repeat_min_prior_peak": 3,  # Q3 [business] earlier spell reached bucket 3 ...
    "repeat_window_months": 12,  # Q3 [business] ... and ended <= 12 months before
    "seasoned_min_months": 12,  # Q4 [business] months on book before the spell
}

STATES = [
    "unknown",
    "early_payment_default",
    "stabilized",
    "repeat_delinquent",
    "straight_roller_seasoned",
    "straight_roller_early_life",
    "slow_roller",
]

DISPLAY_NAMES = {
    "unknown": "Unknown — start of the delinquency journey not observed",
    "early_payment_default": "Early payment default (EPD)",
    "stabilized": "Stabilized",
    "repeat_delinquent": "Repeat delinquent",
    "straight_roller_seasoned": "Seasoned straight roller",
    "straight_roller_early_life": "Early-life straight roller",
    "slow_roller": "Slow roller (partial payer)",
}


def _is_stabilized(f: dict[str, Any]) -> bool:
    """Q2: 60-180 only, five of the last six months within today's bucket +-1, or a long
    run since first reaching 4 that has risen by at most one bucket."""
    p = STATE_RULES
    return f["b_now"] <= p["stabilized_max_bucket"] and (
        f["last6_in_band"] >= p["stabilized_min_in_band"]
        or (
            f["months_since_4"] >= p["stabilized_long_run_months"]
            and f["chg_6m"] <= p["stabilized_long_run_max_rise"]
        )
    )


def _is_early_payment_default(f: dict[str, Any], history_blind: bool) -> bool:
    """Q1: the spell follows a short, clean history, with no payment in it."""
    p = STATE_RULES
    return (
        f["months_before_spell"] <= p["epd_max_history"]
        and f["n_blips"] <= p["epd_max_blips"]
        and f["n_prior_episodes"] == 0
        and f["spell_pay_events"] == 0
        and not history_blind
    )


def _is_repeat_delinquent(f: dict[str, Any]) -> bool:
    """Q3: an earlier spell reached the peak bucket and ended within the window."""
    return f["gap_prior_peak3"] <= STATE_RULES["repeat_window_months"]


def _is_straight_roller(f: dict[str, Any]) -> bool:
    """Q4: the run-up to bucket 4 took at most `straight_max_runup` months."""
    return f["runup_len"] <= STATE_RULES["straight_max_runup"]


# pylint: disable-next=too-many-return-statements
def assign_state(
    f: dict[str, Any], cropped: bool, restructure_blind_spot: bool = False
) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    Q0 journey start not observed (oldest observed month delinquent AND history_blind —
                             history before the window is genuinely missing, or this
                             account is a restructured entry whose predecessor contract's
                             history is invisible) -> stabilized if Q2, else unknown
    Q1 early payment default <=3 months before the spell, <=1 blip, no earlier spell, no payment
                             in the spell (holds at the ceiling are not payments), not
                             history_blind
    Q2 stabilized            60-180 only (today <= CC 7 / RL 6): 5 of the last 6 months within
                             today's bucket ±1, or >=6 months since first reaching 4 and at most
                             1 bucket higher than 6 months ago
    Q3 repeat delinquent     an earlier spell reached 3, cured, ended <=12 months before this one
    Q4 straight roller       run-up to 4 took <=3 months: seasoned (>=12 months on book, or
                             history_blind = older than the window / restructured) / early life
    else slow roller
    """
    p = STATE_RULES
    # history_blind = the journey start is not observed: a Stage-1 crop (floor date,
    # unresolvable gap, dataset edge) or a restructured account, whose first row is a
    # fresh contract and not a fresh delinquency (conformance D1, D2). A CC account
    # cannot start its first billing cycle delinquent; an RL loan can (native bucket 1,
    # first EMI missed), so a delinquent start alone is not blindness.
    history_blind = cropped or restructure_blind_spot
    # Q2 stabilized — computed up front: both Q0 and the main sequence below consult it.
    stab = _is_stabilized(f)
    # Q0 fires only when history_blind; with the whole journey observed a delinquent
    # oldest month is a real start, so fall through to the normal cascade.
    if f["starts_delinquent"] and history_blind:
        return "stabilized" if stab else "unknown"
    if _is_early_payment_default(f, history_blind):  # Q1
        return "early_payment_default"
    if stab:  # Q2
        return "stabilized"
    if _is_repeat_delinquent(f):  # Q3
        return "repeat_delinquent"
    if _is_straight_roller(f):  # Q4
        if f["months_before_spell"] >= p["seasoned_min_months"] or history_blind:
            return "straight_roller_seasoned"
        return "straight_roller_early_life"
    return "slow_roller"


def classify(  # pylint: disable=too-many-positional-arguments
    buckets_native: list[int],
    cropped: bool,
    offset: int,
    canon_top: int,
    repair: bool = True,
    restructure_blind_spot: bool = False,
) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features(
        [max(x + offset, 1) for x in buckets_native], canon_top, repair
    )
    f["det_state"] = assign_state(f, cropped, restructure_blind_spot)
    return f
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: replace · base sha256 `278af8b51db0a35029a57a02a94dc058212c9001418001f167562b0461e2638d` · base trailing newline: yes · new sha256 `361a41ca2b147df1c80f350dec6761f4efa9e57e2090a86fa0b1fef54719c9a5` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque / DDS return, new bureau bounce) lowers the state one level;
  0 points, no distress and no customer-initiated CASA movement → unknown
  (no CASA with us, or a dormant one).

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import StateLadder, points_from_level

MIN_MONTHS = {3: 2, 6: 3}  # CASA: months of the window (by its length) that qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
# Stable income: the window's salary total covers this many monthly floors (S12) …
INC_FLOORS = {3: 2, 6: 3}
D_INC = 0.25  # … and is at most this share below the prior window's total
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="high",
    moderate="moderate",
    low="low",
    unknown="unknown",
    high_from_points=4,
    moderate_from_points=2,
)
DISPLAY_NAMES = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "unknown": "Unknown",
}


def _window(w: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Month indices of the window (m1–mW) and of the prior window (m(W+1)–m(2W))."""
    return tuple(range(1, w + 1)), tuple(range(w + 1, 2 * w + 1))


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    internal = F.greatest(
        F.coalesce(F.col("internal_salary_w"), F.lit(0.0)),
        F.coalesce(F.col("internal_salary_prior"), F.lit(0.0)),
    )
    holding = F.when(
        internal < DEMIN, _not_weakening("income", D_INC, False, w)
    ).otherwise(_not_weakening("income", D_INC, True, w))
    stable = (total >= INC_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (spec S7, S8)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last, casa_floor) >= MIN_MONTHS[w]) & _not_weakening(
        "casa", D_CASA, False, w
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    eosb: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``. Diagnostics, which change
    nothing: ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the prior
    window, none in the window).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, eosb, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    df = (
        df.withColumn("a1_income_level", income_level(amt, w))
        .withColumn("a1_liquidity_level", liquidity_level(amt, w))
        .withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    )
    df = df.withColumn(
        "a1_points_total",
        points_from_level(F.col("a1_income_level"), {"stable": 2, "weak": 1})
        + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1}),
    )
    unknown = (
        (F.col("a1_points_total") == 0)
        & ~F.col("a1_distress_flag")
        & (F.coalesce(F.col("casa_active"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    internal_w = F.coalesce(F.col("internal_salary_w"), F.lit(0.0)) >= DEMIN
    bureau_w = F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= DEMIN
    internal_prior = F.coalesce(F.col("internal_salary_prior"), F.lit(0.0)) >= DEMIN
    out = df.select(
        *GRAIN,
        "a1_state",
        labels[F.col("a1_state")].alias("a1_state_label"),
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == _LADDER.unknown, unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        F.when(internal_w & bureau_w, "both")
        .when(internal_w, "internal")
        .when(bureau_w, "bureau")
        .otherwise("none")
        .alias("a1_income_source"),
        (internal_prior & ~internal_w).cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

New:

`````python
"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque / DDS return, new bureau bounce) lowers the state one level;
  0 points, no distress and no customer-initiated CASA movement → unknown
  (no CASA with us, or a dormant one).

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (spec §3, S2–S12): the workbook's starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
CASA_MIN_MONTHS = {3: 2, 6: 3}  # S7: months of the window the CASA must be at its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
INCOME_FLOOR = 3000.0  # S2: salary floor (internal and bureau), AED
INCOME_ANCHOR_MULT = 2.0  # S2: income must also cover this multiple of the anchor
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
CASA_FLOOR = 3000.0  # S7
CASA_ANCHOR_MULT = 1.0  # S7
CASA_MAX_FALL = 0.50  # S7
CARD_PAYMENT_FLOOR = 500.0  # S8
CARD_PAYMENT_ANCHOR_MULT = 1.0  # S8
MIN_EVIDENCE_AMT = 1000.0  # smallest amount that counts as evidence (Weak, S5-S8)
INCOME_POINTS = {"stable": 2, "weak": 1}  # spec points table (GRR)
LIQUIDITY_POINTS = {"adequate": 2, "weak": 1}  # same table
HIGH_FROM, MODERATE_FROM = 4, 2  # points for High / Moderate (spec s_high / s_mod)

DISPLAY_NAMES = {
    "high": "High",
    "moderate": "Moderate",
    "low": "Low",
    "unknown": "Unknown",
}


def _window(w: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    """Month indices of the window (m1–mW) and of the prior window (m(W+1)–m(2W))."""
    return tuple(range(1, w + 1)), tuple(range(w + 1, 2 * w + 1))


def _months(prefix: str, months: tuple[int, ...]) -> list[Column]:
    return [F.col(f"{prefix}_m{i}") for i in months]


def _count_at_least(cols: list[Column], floor: Column) -> Column:
    return sum((F.coalesce(c, F.lit(0.0)) >= floor).cast("int") for c in cols)


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (spec S12).

    Stable counts the window's total, not months: an employer paying early puts two
    salaries in one month and none in the next. With no internal salary in either window
    the fall compares the level of the months with a value, because AECB alerts arrive
    only on a change and a month without one says nothing."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(INCOME_FLOOR), INCOME_ANCHOR_MULT * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (spec S7, S8)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(CASA_FLOOR), CASA_ANCHOR_MULT * anchor)
    casa_ok = (
        _count_at_least(last, casa_floor) >= CASA_MIN_MONTHS[w]
    ) & _not_weakening("casa", CASA_MAX_FALL, missing_is_zero=False, w=w)
    adequate = casa_ok | (
        payment
        >= F.greatest(F.lit(CARD_PAYMENT_FLOOR), CARD_PAYMENT_ANCHOR_MULT * anchor)
    )
    weak = (_count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0) | (
        payment >= MIN_EVIDENCE_AMT
    )
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (liquidity_level, Dimension("liquidity", "a1_liquidity_level", LIQUIDITY_POINTS)),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={s: s for s in ("high", "moderate", "low", "unknown")},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def build_a1_ability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Points: S2–S12; the unknown gate: S11; distress lowers the state one rung (S9).

    ``signals`` (income, liquidity, distress, EOSB: ``GRAIN`` + columns) and ``anchor``
    (``GRAIN + liquidity_anchor_amt``, product builder) are left-joined in that order.
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``. Diagnostics, which
    change nothing: ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the
    prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0  # S11
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    internal_w = _shows_evidence("internal_salary_w")
    bureau_w = _shows_evidence("bureau_salary_w")
    internal_prior = _shows_evidence("internal_salary_prior")
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        F.when(internal_w & bureau_w, "both")
        .when(internal_w, "internal")
        .when(bureau_w, "bureau")
        .otherwise("none")
        .alias("a1_income_source"),
        (internal_prior & ~internal_w).cast("int").alias("a1_salary_stopped"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: replace · base sha256 `8ae75773e8de5d602b3c7b0c14f3cfa69bb73946738380332e0fc8acf3e4f7af` · base trailing newline: yes · new sha256 `dbb05c5b63fbf0ed5676b287eba3eba894f7fd73a8aab0531a9b77b493d5803b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly (+ RL loans)
                      ├─ liquidity signals ─┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_ext_card_payment_monthly,
                      │                     │   feat_cif_casa_activity_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``bureau_salary_bounces`` and ``location_features`` (``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
    build_liquidity_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    income_inputs = {
        "obs_base": obs,
        "internal_salary": "feat_cif_internal_salary_monthly",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        income_inputs["loan_features"] = "feature_retail_loans"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs=income_inputs,
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_liquidity_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "ext_card_payments": "feat_cif_ext_card_payment_monthly",
                    "casa_activity": "feat_cif_casa_activity_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_liquidity_signals",
                name=f"build_{prefix}_liquidity_signals",
                tags=TAGS,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": obs,
                    "returns": "feat_cif_returns_monthly",
                    "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_distress_signals",
                name=f"build_{prefix}_distress_signals",
                tags=TAGS,
            ),
            node(
                func=build_eosb_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_eosb_signals",
                name=f"build_{prefix}_eosb_signals",
                tags=TAGS,
            ),
            anchor,
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_signals",
                    "liquidity": f"{prefix}_liquidity_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_ability",
                tags=TAGS,
            ),
        ],
    )
`````

New:

`````python
"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly (+ RL loans)
                      ├─ liquidity signals ─┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_ext_card_payment_monthly,
                      │                     │   feat_cif_casa_activity_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``bureau_salary_bounces`` and ``location_features`` (``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
    build_liquidity_signals,
)

TAGS = ["crx_persona", "crx", "a1", "ability", "persona_axis"]


def create_a1_pipeline(product: str, output: str, anchor: Node) -> Pipeline:
    """Signal nodes, ``anchor`` (writing ``crx_<p>_a1_liquidity_anchor``) and the state
    node of ``product``'s A1 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    income_inputs = {
        "obs_base": obs,
        "internal_salary": "feat_cif_internal_salary_monthly",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        income_inputs["loan_features"] = "feature_retail_loans"
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs=income_inputs,
                outputs=f"{prefix}_income_signals",
                name=f"build_{prefix}_income_signals",
                tags=TAGS,
            ),
            node(
                func=build_liquidity_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "ext_card_payments": "feat_cif_ext_card_payment_monthly",
                    "casa_activity": "feat_cif_casa_activity_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_liquidity_signals",
                name=f"build_{prefix}_liquidity_signals",
                tags=TAGS,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": obs,
                    "returns": "feat_cif_returns_monthly",
                    "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_distress_signals",
                name=f"build_{prefix}_distress_signals",
                tags=TAGS,
            ),
            node(
                func=build_eosb_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_eosb_signals",
                name=f"build_{prefix}_eosb_signals",
                tags=TAGS,
            ),
            anchor,
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_signals",
                    "liquidity": f"{prefix}_liquidity_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_ability",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `c7cedcac01c10b3cbb1f4d870427fabb6fd73622fd2e1649c595fecc6d6b3e8a` · base trailing newline: yes · new sha256 `ec700a69a43c97024e6c938d35fa9c0e28b7ee44d961b8dfe9d708f046824633` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary in each month: the larger of the internal credit and the bureau
              salary, a pull counting in its own month and the next (S14);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — customer-initiated CASA movement in the window (the Unknown gate) and
              whether the customer holds a CASA with us at all;
* distress  — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
              the window;
* EOSB      — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
# feat_cif_casa_activity_monthly lanes that are money the customer moved (S11): third-
# party credits, transfers to others, cash, clearing, bill payments, card spend and
# paying their own credit card. Not: own-account wash, the bank recovering the
# customer's loan instalment, fees, interest, reversals, returns, group-internal and
# ambiguous rows.
CUSTOMER_LANES = ("economic", "card_spend", "card_payment")
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month_end, value)`` series over ``{prefix}_m1 …
    _m{months}`` per observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series.select("cif_id", "month_end", value), on="cif_id")
        .withColumn("_k", _month_index(F.col("month_end")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = _cifs(obs_base).select("account_id", "cif_id").distinct()
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.last_day(F.to_date("aecb_bureau_pull_date")).alias("month_end"),
            F.col("aecb_last_salary_credit_amount")
            .cast("double")
            .alias("bureau_salary"),
        )
        .filter(F.col("month_end").isNotNull() & (F.col("bureau_salary") > 0))
        .join(cifs, on="account_id")
        .select("cif_id", "month_end", "bureau_salary")
    )


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each pull's month, and the month
    after it unless that month has its own pull (never before a pull; pulls every 2
    months make a continuous series). A pull of 0 (salary account closed) ends the carry.
    """
    pulls = bureau.groupBy("cif_id", "month_end").agg(
        F.max("bureau_salary").alias("bureau_salary")
    )
    carried = pulls.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        F.col("bureau_salary").alias("_carried"),
    )
    return pulls.join(carried, on=["cif_id", "month_end"], how="full").select(
        "cif_id",
        "month_end",
        F.coalesce("bureau_salary", "_carried").alias("bureau_salary"),
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal salary (``feat_cif_internal_salary_monthly``) and the bureau salary
    (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no salary that
    month. Also the largest month per source: ``internal_salary_w`` / ``bureau_salary_w`` in
    the window, ``internal_salary_prior`` in the prior window.

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit("int").alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit("bur").alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    monthly = sources.groupBy("cif_id", "month_end").agg(
        F.max("amount").alias("amount")
    )
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == "int"
    return left_join_all(
        obs_base,
        [
            _by_month(obs, monthly, "amount", "income", 2 * w),
            _in_window(
                obs,
                sources,
                2 * w,
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            ),
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def build_liquidity_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (largest single payment to an external card in W),
    ``casa_active`` (1: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (1: any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months)."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        ext_card_payments,
        ["cif_id", "month_end", "max_payment"],
        "feat_cif_ext_card_payment_monthly",
    )
    require_columns(
        casa_activity,
        ["cif_id", "month_end", "lane", "legs"],
        "feat_cif_casa_activity_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    customer = casa_activity.filter(F.col("lane").isin(*CUSTOMER_LANES))
    held = casa_activity.select("cif_id", "month_end").unionByName(
        casa_balance.filter(F.col("casa_balance") > 0).select("cif_id", "month_end")
    )
    return left_join_all(
        obs_base,
        [
            _by_month(obs, casa_balance, "casa_balance", "casa", 2 * w),
            _in_window(
                obs,
                ext_card_payments,
                w,
                F.max("max_payment").alias("ext_card_payment_max"),
            ),
            _in_window(obs, customer, w, F.max(F.lit(1)).alias("casa_active")),
            _in_window(obs, held, CASA_HELD_MONTHS, F.max(F.lit(1)).alias("casa_held")),
        ],
    ).fillna(0, subset=["casa_active", "casa_held"])


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )

    def flag(reason: str) -> Column:
        return F.max((F.col("reason") == reason).cast("int"))

    events = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        "cif_id", "month_end", F.lit("BUREAU").alias("reason")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit("BUREAU").alias("reason"),
            )
        )
    events = events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN) & (F.col("events") > 0)
        ).select("cif_id", "month_end", "reason")
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    hits = _in_window(
        obs,
        events,
        w,
        flag(CHEQUE_RETURN).alias("distress_cheque"),
        flag(DDS_RETURN).alias("distress_dds"),
        flag("BUREAU").alias("distress_bureau"),
    )
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag``: 1 when a DCORE result on any of the customer's agreements names an
    end-of-service benefit (EOSB expected / awaited / received) in the window. A
    diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary in each month: the larger of the internal credit and the bureau
              salary, a pull counting in its own month and the next (S14);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — customer-initiated CASA movement in the window (the Unknown gate) and
              whether the customer holds a CASA with us at all;
* distress  — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
              the window;
* EOSB      — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
    window_start,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# feat_cif_casa_activity_monthly lanes that are money the customer moved (S11): third-
# party credits, transfers to others, cash, clearing, bill payments, card spend and
# paying their own credit card. Not: own-account wash, the bank recovering the
# customer's loan instalment, fees, interest, reversals, returns, group-internal and
# ambiguous rows.
CUSTOMER_LANES = ("economic", "card_spend", "card_payment")
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = _cifs(obs_base).select("account_id", "cif_id").distinct()
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.last_day(F.to_date("aecb_bureau_pull_date")).alias("month_end"),
            F.col("aecb_last_salary_credit_amount")
            .cast("double")
            .alias("bureau_salary"),
        )
        .filter(F.col("month_end").isNotNull() & (F.col("bureau_salary") > 0))
        .join(cifs, on="account_id")
        .select("cif_id", "month_end", "bureau_salary")
    )


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each pull's month, and the month
    after it unless that month has its own pull (never before a pull; pulls every 2
    months make a continuous series). A pull of 0 (salary account closed) ends the carry.
    """
    none = F.lit(None).cast("double")
    own = bureau.select("cif_id", "month_end", "bureau_salary", none.alias("_carried"))
    carried = bureau.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        none.alias("bureau_salary"),
        F.col("bureau_salary").alias("_carried"),
    )
    return (
        own.unionByName(carried)
        .groupBy("cif_id", "month_end")
        .agg(
            F.coalesce(F.max("bureau_salary"), F.max("_carried")).alias("bureau_salary")
        )
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_legs(casa_activity: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``balance`` (NULL on an
    activity leg), ``customer`` (1: a leg in ``CUSTOMER_LANES``, S11) and ``held`` (1: a
    leg, or a positive balance)."""
    return casa_activity.select(
        "cif_id",
        "month_end",
        F.lit(None).cast(casa_balance.schema["casa_balance"].dataType).alias("balance"),
        F.col("lane").isin(*CUSTOMER_LANES).cast("int").alias("customer"),
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            F.col("casa_balance").alias("balance"),
            F.lit(0).alias("customer"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (S7, ``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (S8: largest single payment to an external card in W),
    ``casa_active`` (S11: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months). CASA means the
    scheme-code accounts of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        ext_card_payments,
        ["cif_id", "month_end", "max_payment"],
        "feat_cif_ext_card_payment_monthly",
    )
    require_columns(
        casa_activity,
        ["cif_id", "month_end", "lane", "legs"],
        "feat_cif_casa_activity_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    # The obs base starts in the persona start month: no window reaches older rows.
    first = F.lit(str(crx_persona["persona_start_date"])).cast("date")
    legs = _casa_legs(casa_activity, casa_balance).filter(
        F.col("month_end") >= window_start(CASA_HELD_MONTHS, first)
    )
    payments = ext_card_payments.filter(F.col("month_end") >= window_start(w, first))
    in_w = _month_index(F.col("month_end")) <= w
    casa_active = F.max(F.when((F.col("customer") == 1) & in_w, F.lit(1)))  # S11
    casa_held = F.max(F.when(F.col("held") == 1, F.lit(1)))
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                legs,
                CASA_HELD_MONTHS,
                *_by_month("balance", "casa", 2 * w),
                casa_active.alias("casa_active"),
                casa_held.alias("casa_held"),
            ),
            _in_window(
                obs, payments, w, F.max("max_payment").alias("ext_card_payment_max")
            ),
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "ext_card_payment_max",
        "casa_active",
        "casa_held",
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/classify.py`
action: replace · base sha256 `dc119a6701733d2106ac5321328083428f45f51d560220d90c41b0b909f69848` · base trailing newline: yes · new sha256 `0f2c119bf8ca6bdff67cb50d515e006c1ed95eb361232ab053060555c5d8308d` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A2 locatability state: location × reachability, with a deceased override.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md`` §6.

    a2_state = deceased                              if any deceased source
             = <location_state>__<reachability_state> otherwise (9 values)

Both dimensions are kept on every row, deceased included, so each can be used alone.
"""

from __future__ import annotations

from itertools import chain

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .signals import LOCATION_EVIDENCE

LOCATION_LABELS = {"skip": "Skip", "in_country": "In Country", "unknown": "Unknown"}
REACHABILITY_LABELS = {
    "reachable": "Reachable",
    "non_reachable": "Non-Reachable",
    "unknown": "Unknown",
}
_OUTPUT = [
    *GRAIN,
    "a2_state",
    "a2_state_label",
    "location_state",
    "reachability_state",
    "deceased_flag",
    "deceased_source",
    "location_rule",
    "location_unknown_reason",
    *LOCATION_EVIDENCE,
    "reachability_unknown_reason",
    "last_contact_date",
    "last_attempt_date",
    "attempt_days_in_window",
    "last_skip_trace_date",
]


def _label(col: str, labels: dict[str, str]) -> Column:
    return F.create_map(*[F.lit(x) for x in chain(*labels.items())])[F.col(col)]


def build_a2_locatability(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    location: DataFrame,
    dcore: DataFrame,
    way4_deceased: DataFrame,
    demographics_deceased: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation: the A2 state, its label, both dimensions, the deceased
    flag with its sources (``dcore``, ``way4``, ``demographics``) and the diagnostics.
    """
    df = left_join_all(
        obs_base, [location, dcore, way4_deceased, demographics_deceased]
    ).fillna(0, subset=["way4_deceased_flag", "demographics_deceased_flag"])
    sources = F.concat_ws(
        ",",
        F.when(F.col("dcore_deceased_date").isNotNull(), F.lit("dcore")),
        F.when(F.col("way4_deceased_flag") == 1, F.lit("way4")),
        F.when(F.col("demographics_deceased_flag") == 1, F.lit("demographics")),
    )
    deceased = F.col("deceased_flag") == 1
    out = (
        df.withColumn("deceased_source", F.when(sources != "", sources))
        .withColumn("deceased_flag", F.col("deceased_source").isNotNull().cast("int"))
        .withColumn(
            "a2_state",
            F.when(deceased, "deceased").otherwise(
                F.concat_ws("__", "location_state", "reachability_state")
            ),
        )
        .withColumn(
            "a2_state_label",
            F.when(deceased, "Deceased").otherwise(
                F.concat_ws(
                    " – ",
                    _label("location_state", LOCATION_LABELS),
                    _label("reachability_state", REACHABILITY_LABELS),
                )
            ),
        )
        .select(*_OUTPUT)
    )
    log_latest_month(out, "a2_state", f"a2_locatability [{model_id}]", persona_end_date)
    return out
`````

New:

`````python
"""A2 locatability state: location × reachability, with a deceased override.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md`` §6 (D-A2-1, D-A2-9, D-A2-11).

    a2_state = deceased                              if any deceased source
             = <location_state>__<reachability_state> otherwise (9 values)

Both dimensions are kept on every row, deceased included, so each can be used alone.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from ..scoring_engine import state_label
from .signals import LOCATION_EVIDENCE

LOCATION_LABELS = {"skip": "Skip", "in_country": "In Country", "unknown": "Unknown"}
REACHABILITY_LABELS = {
    "reachable": "Reachable",
    "non_reachable": "Non-Reachable",
    "unknown": "Unknown",
}
_OUTPUT = [
    *GRAIN,
    "a2_state",
    "a2_state_label",
    "location_state",
    "reachability_state",
    "deceased_flag",
    "deceased_source",
    "location_rule",
    "location_unknown_reason",
    *LOCATION_EVIDENCE,
    "reachability_unknown_reason",
    "last_contact_date",
    "last_attempt_date",
    "attempt_days_in_window",
    "last_skip_trace_date",
]


def build_a2_locatability(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    location: DataFrame,
    dcore: DataFrame,
    way4_deceased: DataFrame,
    demographics_deceased: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One row per observation: the A2 state, its label, both dimensions, the deceased
    flag with its sources (``dcore``, ``way4``, ``demographics``) and the diagnostics.
    """
    df = left_join_all(
        obs_base, [location, dcore, way4_deceased, demographics_deceased]
    ).fillna(0, subset=["way4_deceased_flag", "demographics_deceased_flag"])
    sources = F.concat_ws(
        ",",
        F.when(F.col("dcore_deceased_date").isNotNull(), F.lit("dcore")),
        F.when(F.col("way4_deceased_flag") == 1, F.lit("way4")),
        F.when(F.col("demographics_deceased_flag") == 1, F.lit("demographics")),
    )
    deceased = F.col("deceased_flag") == 1
    out = (
        df.withColumn("deceased_source", F.when(sources != "", sources))
        .withColumn("deceased_flag", F.col("deceased_source").isNotNull().cast("int"))
        .withColumn(
            "a2_state",
            F.when(deceased, "deceased").otherwise(
                F.concat_ws("__", "location_state", "reachability_state")
            ),
        )
        .withColumn(
            "a2_state_label",
            F.when(deceased, "Deceased").otherwise(
                F.concat_ws(
                    " – ",
                    state_label("location_state", LOCATION_LABELS),
                    state_label("reachability_state", REACHABILITY_LABELS),
                )
            ),
        )
        .select(*_OUTPUT)
    )
    log_latest_month(out, "a2_state", f"a2_locatability [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py`
action: replace · base sha256 `4e3153a7f69d025c46f8227d4729572e52f830cd25ee7ae27606957f8f923376` · base trailing newline: yes · new sha256 `571e0cb7fc94e75929fe21ec8ff092e4a7c36f281a1ca75e8b9e464555882894` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node

from .classify import build_a2_locatability
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)


def create_a2_pipeline(product: str, output: str) -> Pipeline:
    """Signal nodes and the state node of ``product``'s A2 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a2"
    tags = ["crx_persona", "crx", "a2", "locatability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_location_signals,
                inputs={
                    "obs_base": obs,
                    "location_features": "feat_cif_location_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_location_signals",
                name=f"build_{prefix}_location_signals",
                tags=tags,
            ),
            node(
                func=build_dcore_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_dcore_signals",
                name=f"build_{prefix}_dcore_signals",
                tags=tags,
            ),
            node(
                func=build_way4_deceased,
                inputs={
                    "obs_base": obs,
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                },
                outputs=f"{prefix}_way4_deceased",
                name=f"build_{prefix}_way4_deceased",
                tags=tags,
            ),
            node(
                func=build_demographics_deceased,
                inputs={"obs_base": obs, "demographics": "feat_demographics_cif"},
                outputs=f"{prefix}_demographics_deceased",
                name=f"build_{prefix}_demographics_deceased",
                tags=tags,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "obs_base": obs,
                    "location": f"{prefix}_location_signals",
                    "dcore": f"{prefix}_dcore_signals",
                    "way4_deceased": f"{prefix}_way4_deceased",
                    "demographics_deceased": f"{prefix}_demographics_deceased",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_locatability",
                tags=tags,
            ),
        ],
    )
`````

New:

`````python
"""The A2 locatability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ location signals ─────────────┐   feat_cif_location_monthly
                      ├─ DCORE signals ────────────────┤   dcore_prm_followup_outcomes,
                      │  (reachability, DCORE deceased)│   prm_dcore_account_agreements
                      ├─ Way4 deceased ────────────────┼─► crx_<p>_a2_locatability
                      └─ demographics deceased ────────┘   prm_contract, prm_client,
                                                           feat_demographics_cif

Needs, for the model_id: the observation base, ``digital_login``, ``casa_primary`` and
``location_features`` (``feat_cif_location_monthly``, ``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node

from .classify import build_a2_locatability
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)

TAGS = ["crx_persona", "crx", "a2", "locatability", "persona_axis"]


def create_a2_pipeline(product: str, output: str) -> Pipeline:
    """Signal nodes and the state node of ``product``'s A2 axis, written to ``output``."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a2"
    return Pipeline(
        [
            node(
                func=build_location_signals,
                inputs={
                    "obs_base": obs,
                    "location_features": "feat_cif_location_monthly",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_location_signals",
                name=f"build_{prefix}_location_signals",
                tags=TAGS,
            ),
            node(
                func=build_dcore_signals,
                inputs={
                    "obs_base": obs,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_dcore_signals",
                name=f"build_{prefix}_dcore_signals",
                tags=TAGS,
            ),
            node(
                func=build_way4_deceased,
                inputs={
                    "obs_base": obs,
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                },
                outputs=f"{prefix}_way4_deceased",
                name=f"build_{prefix}_way4_deceased",
                tags=TAGS,
            ),
            node(
                func=build_demographics_deceased,
                inputs={"obs_base": obs, "demographics": "feat_demographics_cif"},
                outputs=f"{prefix}_demographics_deceased",
                name=f"build_{prefix}_demographics_deceased",
                tags=TAGS,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "obs_base": obs,
                    "location": f"{prefix}_location_signals",
                    "dcore": f"{prefix}_dcore_signals",
                    "way4_deceased": f"{prefix}_way4_deceased",
                    "demographics_deceased": f"{prefix}_demographics_deceased",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"build_{prefix}_locatability",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py`
action: replace · base sha256 `e78ea2864575d87361a301a8b586611ac278b08dba256db7742029033c7908ad` · base trailing newline: yes · new sha256 `2403f09bbe58da9fa3d00b52b8630d6ad5d470de82b67820e18e30bd70c7ba89` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history (no T0);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, require_columns, window_months
from .._dcore_codes import (
    CALL_CODES,
    DECEASED,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SKIP_TRACE,
    SUCCESS_CATEGORY,
)
from .._dpd_journey.constants import MODEL_ID_SEGMENT

# Travel rule (L2): the latest UAE evidence at most this many months after the last
# ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
# Non-Reachable: the last this-many call days all failed, per segment.
GONE_DARK_DAYS = {"60_180": 3, "180_plus": 6}
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _window_start(months: int) -> Column:
    """First day of the observation's W-month window."""
    return F.add_months(F.trunc(F.col("observation_date"), "month"), 1 - months)


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
    L3 in_country  the latest UAE evidence is in W
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    latest = (
        obs.join(location_features, on="cif_id")
        .filter(F.col("month_end") <= F.col("observation_date"))
        .groupBy(*GRAIN)
        .agg(
            _latest("last_uae_date", "last_uae_source").alias("_uae"),
            _latest("last_foreign_date", "last_foreign_source").alias("_foreign"),
            F.max("last_travel_date").alias("last_travel_date"),
        )
        .select(
            *GRAIN,
            F.col("_uae.last_uae_date").alias("last_uae_date"),
            F.col("_uae.last_uae_source").alias("last_uae_source"),
            F.col("_foreign.last_foreign_date").alias("last_foreign_date"),
            F.col("_foreign.last_foreign_source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )
    uae, foreign, travel = (
        F.col("last_uae_date"),
        F.col("last_foreign_date"),
        F.col("last_travel_date"),
    )
    obs_date = F.col("observation_date")
    rule = (
        F.when(foreign.isNotNull() & (uae.isNull() | (foreign >= uae)), "L1")
        .when(
            travel.isNotNull()
            & (
                uae.isNull()
                | (
                    (uae <= F.add_months(travel, TRAVEL_GAP_MONTHS))
                    & (uae <= F.add_months(obs_date, -TRAVEL_SILENCE_MONTHS))
                )
            ),
            "L2",
        )
        .when(uae >= _window_start(window_months(model_id)), "L3")
        .otherwise("L4")
    )
    return (
        left_join_all(obs_base, [latest])
        .withColumn("location_rule", rule)
        .withColumn(
            "location_state",
            F.when(F.col("location_rule").isin("L1", "L2"), "skip")
            .when(F.col("location_rule") == "L3", "in_country")
            .otherwise("unknown"),
        )
        .withColumn(
            "location_unknown_reason",
            F.when(F.col("location_rule") != "L4", None)
            .when(uae.isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_events(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Each observation row's DCORE events dated on or before it: ``day``,
    ``action_code``, ``category``, ``name`` (upper-cased, trimmed, '' when missing)."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "action_code", "result_category", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    accounts = obs_base.select("account_id").distinct()
    scope = agreements.select("account_id", "agreement_id").join(
        F.broadcast(accounts), on="account_id", how="leftsemi"
    )

    def text(col: str) -> Column:
        return F.coalesce(F.upper(F.trim(col)), F.lit(""))

    events = followup.select(
        F.col("agreement_id").cast("string").alias("agreement_id"),
        F.to_date("action_ts").alias("day"),
        text("action_code").alias("action_code"),
        text("result_category").alias("category"),
        text("result_name").alias("name"),
    ).join(F.broadcast(scope), on="agreement_id")
    return (
        obs_base.select(*GRAIN)
        .join(events, on="account_id")
        .filter(F.col("day") <= F.col("observation_date"))
    )


def gone_dark_days(model_id: str) -> int:
    """The failed-call-day streak that makes ``model_id``'s segment Non-Reachable."""
    return GONE_DARK_DAYS[MODEL_ID_SEGMENT[model_id]]


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``_dcore_codes.FAILED_CALL``) and no contact was confirmed. A contact
    is an inbound call, an outbound call in category SUC, or a right-party result.

    non_reachable  the last ``gone_dark_days`` call days all failed, the oldest in W,
                   and no contact since
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = _window_start(window_months(model_id))
    streak = gone_dark_days(model_id)
    events = _dcore_events(obs_base, followup, agreements)
    name = F.col("name")
    code = F.col("action_code")
    calls = events.filter(
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = code.isin(*OUTBOUND_CODES)
    contact = (
        code.isin(*INBOUND_CODES)
        | (outbound & (F.col("category") == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    days = (
        calls.groupBy(*GRAIN, "day")
        .agg(
            F.max(outbound.cast("int")).alias("_attempt"),
            F.max(contact.cast("int")).alias("_contact"),
            F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
                "_all_failed"
            ),
        )
        .withColumn(
            "_failed",
            ((F.col("_contact") == 0) & (F.col("_all_failed") == 1)).cast("int"),
        )
    )
    recent = Window.partitionBy(*GRAIN).orderBy(F.col("day").desc())
    last_days = (
        days.filter(F.col("_attempt") == 1)
        .withColumn("_rank", F.row_number().over(recent))
        .filter(F.col("_rank") <= streak)
        .groupBy(*GRAIN)
        .agg(
            F.count("*").alias("_n_last"),
            F.sum("_failed").alias("_failed_last"),
            F.min("day").alias("_oldest_last"),
        )
    )
    day = F.col("day")
    calls_summary = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_contact") == 1, day)).alias("last_contact_date"),
        F.max(F.when(F.col("_attempt") == 1, day)).alias("last_attempt_date"),
        F.count(F.when((F.col("_attempt") == 1) & (day >= w_start), day)).alias(
            "attempt_days_in_window"
        ),
    )
    records = events.groupBy(*GRAIN).agg(
        F.max(F.when(name.isin(*DECEASED), day)).alias("dcore_deceased_date"),
        F.max(F.when(name.isin(*SKIP_TRACE), day)).alias("last_skip_trace_date"),
        F.lit(1).alias("_dcore_record"),
    )
    last_contact = F.col("last_contact_date")
    gone_dark = (
        (F.col("_n_last") == streak)
        & (F.col("_failed_last") == streak)
        & (F.col("_oldest_last") >= w_start)
        & (last_contact.isNull() | (last_contact < F.col("_oldest_last")))
    )
    return (
        left_join_all(obs_base, [records, calls_summary, last_days])
        .withColumn(
            "reachability_state",
            F.when(gone_dark, "non_reachable")
            .when(last_contact >= w_start, "reachable")
            .otherwise("unknown"),
        )
        .withColumn(
            "reachability_unknown_reason",
            F.when(F.col("reachability_state") != "unknown", None)
            .when(F.col("_dcore_record").isNull(), "no_dcore_record")
            .otherwise("no_contact_in_window"),
        )
        .withColumn(
            "attempt_days_in_window", F.coalesce("attempt_days_in_window", F.lit(0))
        )
        .drop("_dcore_record", "_n_last", "_failed_last", "_oldest_last")
    )


# ── Deceased (Way4, demographics) ─────────────────────────────────────────────


def build_way4_deceased(
    obs_base: DataFrame, contracts: DataFrame, clients: DataFrame
) -> DataFrame:
    """``way4_deceased_flag``: block code 2 = D on the latest ``prm_contract`` snapshot on
    or before the observation date, on any of the customer's cards. Rows with a card
    only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")
    cifs = obs.select("cif_id").distinct()
    snapshots = contracts.select(
        F.col("contract_id").cast("string").alias("contract_id"),
        "client_id",
        F.to_date("observation_date").alias("snapshot_date"),
        F.upper(F.trim("block_code_2")).alias("block_code_2"),
    )
    cards = (
        snapshots.select("contract_id", "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select("contract_id", "cif_id")
    )
    deceased = F.coalesce(F.col("block_code_2") == WAY4_DECEASED_BLOCK, F.lit(False))
    latest = Window.partitionBy(*GRAIN, "contract_id").orderBy(
        F.col("snapshot_date").desc(), deceased.desc()
    )
    return (
        obs.join(cards, on="cif_id")
        .join(snapshots.drop("client_id"), on="contract_id")
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .groupBy(*GRAIN)
        .agg(F.max(deceased.cast("int")).alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag``: ``ft_deceased_flag`` of the customer (a death is
    permanent: the largest value per CIF, no date). Rows with a demographics record
    only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    flags = demographics.groupBy(F.col("cif_id").cast("string").alias("cif_id")).agg(
        F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
            "demographics_deceased_flag"
        )
    )
    return (
        obs_base.filter(F.col("cif_id").isNotNull())
        .select(*GRAIN, "cif_id")
        .join(flags, on="cif_id")
        .select(*GRAIN, "demographics_deceased_flag")
    )
`````

New:

`````python
"""A2 locatability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A2_locatability_spec.md``. Run through
``crx_cc_a2_locatability`` / ``crx_rl_a2_locatability``.

Observation dates are month ends; the window W is the observation month and the months
before it (``_common.window_months``: 3 at 60–180, 6 at 180+). Evidence counts when dated
on or before the observation date, compared by day; no age limit unless a rule says so.
The latest evidence wins on both dimensions:

* location     — ``feat_cif_location_monthly`` (logins, in-person card use, departure
                 notes, travel purchases; all of the customer's accounts);
* reachability — DCORE calls on the scored account's agreement, all history up to the
                 observation date (D-A2-8);
* deceased     — DCORE results, Way4 block code ``D`` on any of the customer's cards,
                 the demographics flag.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    left_join_all,
    require_columns,
    scoped,
    segment,
    window_months,
    window_start,
)
from .._dcore_codes import (
    CALL_CODES,
    DECEASED,
    FAILED_CALL,
    IGNORED,
    IGNORED_PREFIX,
    INBOUND_CODES,
    OUTBOUND_CODES,
    RIGHT_PARTY_CONTACT,
    SKIP_TRACE,
    SUCCESS_CATEGORY,
)

# Travel rule (L2, D-A2-18): the latest UAE evidence at most this many months after
# the last ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
WAY4_DECEASED_BLOCK = "D"  # block_code_2
# Per-month evidence columns of feat_cif_location_monthly, latest as of the observation.
LOCATION_EVIDENCE = [
    "last_uae_date",
    "last_uae_source",
    "last_foreign_date",
    "last_foreign_source",
    "last_travel_date",
]


def _cif_rows(obs_base: DataFrame) -> DataFrame:
    """``GRAIN + cif_id`` of the observation rows that have a CIF."""
    return obs_base.filter(F.col("cif_id").isNotNull()).select(*GRAIN, "cif_id")


def _latest(date_col: str, source_col: str) -> Column:
    """The row with the latest ``date_col`` as a struct (date, source)."""
    return F.max(F.when(F.col(date_col).isNotNull(), F.struct(date_col, source_col)))


# ── Location ──────────────────────────────────────────────────────────────────


def _latest_evidence(obs: DataFrame, location_features: DataFrame) -> DataFrame:
    """Per ``GRAIN``: the latest UAE and foreign evidence (date and source) and the last
    travel purchase, from the monthly rows up to the observation date."""
    return (
        obs.join(scoped(location_features, obs, "cif_id"), on="cif_id")
        .filter(F.col("month_end") <= F.col("observation_date"))
        .groupBy(*GRAIN)
        .agg(
            _latest("last_uae_date", "last_uae_source").alias("_uae"),
            _latest("last_foreign_date", "last_foreign_source").alias("_foreign"),
            F.max("last_travel_date").alias("last_travel_date"),
        )
        .select(
            *GRAIN,
            F.col("_uae.last_uae_date").alias("last_uae_date"),
            F.col("_uae.last_uae_source").alias("last_uae_source"),
            F.col("_foreign.last_foreign_date").alias("last_foreign_date"),
            F.col("_foreign.last_foreign_source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )


def _location_rule(window: int) -> Column:
    """The first of the rules L1–L4 that fires (see ``build_location_signals``);
    ``window`` is W in months."""
    uae, foreign, travel = map(
        F.col, ("last_uae_date", "last_foreign_date", "last_travel_date")
    )
    obs_date = F.col("observation_date")
    return (
        F.when(foreign.isNotNull() & (uae.isNull() | (foreign >= uae)), "L1")
        .when(
            travel.isNotNull()
            & (
                uae.isNull()
                | (
                    (uae <= F.add_months(travel, TRAVEL_GAP_MONTHS))
                    & (uae <= F.add_months(obs_date, -TRAVEL_SILENCE_MONTHS))
                )
            ),
            "L2",
        )
        .when(uae >= window_start(window), "L3")
        .otherwise("L4")
    )


def build_location_signals(
    obs_base: DataFrame, location_features: DataFrame, model_id: str
) -> DataFrame:
    """``location_state`` (skip / in_country / unknown), the rule that fired
    (``location_rule`` L1–L4), ``location_unknown_reason`` and the evidence behind it.

    L1 skip        the latest foreign evidence is on or after the latest UAE evidence
                   (D-A2-3; the same day: foreign wins, D-A2-14)
    L2 skip        a travel purchase, the latest UAE evidence at most TRAVEL_GAP_MONTHS
                   after the last one (or none), and none for TRAVEL_SILENCE_MONTHS
                   (D-A2-15, D-A2-18)
    L3 in_country  the latest UAE evidence is in W (D-A2-3)
    L4 unknown     no_evidence · domestic_before_window
    """
    require_columns(
        location_features,
        ["cif_id", "month_end", *LOCATION_EVIDENCE],
        "feat_cif_location_monthly",
    )
    latest = _latest_evidence(_cif_rows(obs_base), location_features)
    rule = _location_rule(window_months(model_id))
    return (
        left_join_all(obs_base, [latest])
        .withColumn("location_rule", rule)
        .withColumn(
            "location_state",
            F.when(F.col("location_rule").isin("L1", "L2"), "skip")
            .when(F.col("location_rule") == "L3", "in_country")
            .otherwise("unknown"),
        )
        .withColumn(
            "location_unknown_reason",
            F.when(F.col("location_rule") != "L4", None)
            .when(F.col("last_uae_date").isNull(), "no_evidence")
            .otherwise("domestic_before_window"),
        )
    )


# ── Reachability (+ DCORE deceased) ───────────────────────────────────────────


def _dcore_days(events: DataFrame) -> DataFrame:
    """One row per ``(account_id, day)`` of ``dcore_account_events``, with the day's
    flags: ``_attempt`` (an outbound call), ``_contact`` (see ``build_dcore_signals``),
    ``_all_failed`` (every outbound call failed, NULL without one), ``_deceased`` and
    ``_skip_trace`` (a result of that kind). Reduced to days before the join with the
    observations."""
    code, category, name = F.col("action_code"), F.col("category"), F.col("name")
    call = (
        code.isin(*CALL_CODES) & ~name.isin(*IGNORED) & ~name.startswith(IGNORED_PREFIX)
    )
    outbound = call & code.isin(*OUTBOUND_CODES)
    contact = call & (
        code.isin(*INBOUND_CODES)
        | (outbound & (category == SUCCESS_CATEGORY))
        | name.isin(*RIGHT_PARTY_CONTACT)
    )
    return events.groupBy("account_id", "day").agg(
        F.max(outbound.cast("int")).alias("_attempt"),
        F.max(contact.cast("int")).alias("_contact"),
        F.min(F.when(outbound, name.isin(*FAILED_CALL).cast("int"))).alias(
            "_all_failed"
        ),
        F.max(name.isin(*DECEASED).cast("int")).alias("_deceased"),
        F.max(name.isin(*SKIP_TRACE).cast("int")).alias("_skip_trace"),
    )


def gone_dark_days(model_id: str) -> int:
    """The failed-call-day streak that makes ``model_id``'s segment Non-Reachable."""
    return GONE_DARK_DAYS[segment(model_id)]


def _gone_dark(streak: int, w_start: Column) -> Column:
    """D-A2-7, D-A2-20: the last ``streak`` call days all failed, the oldest in W, and
    no contact since. Reads ``_last_calls`` and ``last_contact_date``."""
    oldest_call = F.array_min("_last_calls.day")
    last_contact = F.col("last_contact_date")
    return (
        (F.size("_last_calls") == streak)
        & F.forall("_last_calls", lambda call: call["failed"])
        & (oldest_call >= w_start)
        & (last_contact.isNull() | (last_contact < oldest_call))
    )


def _reachable(w_start: Column) -> Column:  # D-A2-7: a contact in W
    return F.col("last_contact_date") >= w_start


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``_dcore_codes.FAILED_CALL``) and no contact was confirmed. A contact
    is an inbound call, an outbound call in category SUC, or a right-party result
    (off-list codes: D-A2-17).

    non_reachable  the last ``gone_dark_days`` call days all failed, the oldest in W,
                   and no contact since (D-A2-7, D-A2-20)
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = window_start(window_months(model_id))
    streak = gone_dark_days(model_id)
    days = (
        obs_base.select(*GRAIN)
        .join(
            _dcore_days(dcore_account_events(obs_base, followup, agreements)),
            on="account_id",
        )
        .filter(F.col("day") <= F.col("observation_date"))
    )
    day = F.col("day")
    attempt = F.col("_attempt") == 1
    contact = F.col("_contact") == 1
    failed = ~contact & (F.col("_all_failed") == 1)
    # The last ``streak`` call days, newest first; non-attempt days are never collected.
    last_calls = F.slice(
        F.sort_array(
            F.collect_list(F.when(attempt, F.struct(day, failed.alias("failed")))),
            asc=False,
        ),
        1,
        streak,
    )
    summary = days.groupBy(*GRAIN).agg(
        F.max(F.when(F.col("_deceased") == 1, day)).alias("dcore_deceased_date"),
        F.max(F.when(F.col("_skip_trace") == 1, day)).alias("last_skip_trace_date"),
        F.lit(1).alias("_dcore_record"),
        F.max(F.when(contact, day)).alias("last_contact_date"),
        F.max(F.when(attempt, day)).alias("last_attempt_date"),
        F.count(F.when(attempt & (day >= w_start), day)).alias(
            "attempt_days_in_window"
        ),
        last_calls.alias("_last_calls"),
    )
    return (
        left_join_all(obs_base, [summary])
        .withColumn(
            "reachability_state",
            F.when(_gone_dark(streak, w_start), "non_reachable")
            .when(_reachable(w_start), "reachable")
            .otherwise("unknown"),
        )
        .withColumn(
            "reachability_unknown_reason",
            F.when(F.col("reachability_state") != "unknown", None)
            .when(F.col("_dcore_record").isNull(), "no_dcore_record")
            .otherwise("no_contact_in_window"),
        )
        .withColumn(
            "attempt_days_in_window", F.coalesce("attempt_days_in_window", F.lit(0))
        )
        .drop("_dcore_record", "_last_calls")
    )


# ── Deceased (Way4, demographics) ─────────────────────────────────────────────


def build_way4_deceased(
    obs_base: DataFrame, contracts: DataFrame, clients: DataFrame
) -> DataFrame:
    """``way4_deceased_flag`` (D-A2-9): block code 2 = D on the latest ``prm_contract``
    snapshot on or before the observation date, on any of the customer's cards. Rows
    with a card only."""
    require_columns(
        contracts,
        ["contract_id", "client_id", "observation_date", "block_code_2"],
        "prm_contract",
    )
    require_columns(clients, ["client_id", "cif_id"], "prm_client")
    obs = _cif_rows(obs_base)
    cifs = obs.select("cif_id").distinct()
    snapshots = contracts.select(
        F.col("contract_id").cast("string").alias("contract_id"),
        "client_id",
        F.to_date("observation_date").alias("snapshot_date"),
        F.upper(F.trim("block_code_2")).alias("block_code_2"),
    )
    cards = (
        snapshots.select("contract_id", "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select("contract_id", "cif_id")
    )
    deceased = F.coalesce(F.col("block_code_2") == WAY4_DECEASED_BLOCK, F.lit(False))
    return (
        obs.join(cards, on="cif_id")
        .join(
            scoped(snapshots.drop("client_id"), cards, "contract_id"), on="contract_id"
        )
        .filter(F.col("snapshot_date") <= F.col("observation_date"))
        .groupBy(*GRAIN, "contract_id")
        .agg(
            F.max(F.struct("snapshot_date", deceased.cast("int").alias("flag"))).alias(
                "_latest"
            )
        )
        .groupBy(*GRAIN)
        .agg(F.max("_latest.flag").alias("way4_deceased_flag"))
    )


def build_demographics_deceased(
    obs_base: DataFrame, demographics: DataFrame
) -> DataFrame:
    """``demographics_deceased_flag`` (D-A2-9): ``ft_deceased_flag`` of the customer (a
    death is permanent: the largest value per CIF, no date). Rows with a demographics
    record only."""
    require_columns(
        demographics, ["cif_id", "ft_deceased_flag"], "feat_demographics_cif"
    )
    obs = _cif_rows(obs_base)
    people = demographics.select(
        F.col("cif_id").cast("string").alias("cif_id"), "ft_deceased_flag"
    )
    flags = (
        scoped(people, obs, "cif_id")
        .groupBy("cif_id")
        .agg(
            F.max((F.col("ft_deceased_flag").cast("int") == 1).cast("int")).alias(
                "demographics_deceased_flag"
            )
        )
    )
    return obs.join(flags, on="cif_id").select(*GRAIN, "demographics_deceased_flag")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py`
action: replace · base sha256 `2c45eefef8f32b32cc09382327f477b255b33e508bad1508880d01b3a488061f` · base trailing newline: yes · new sha256 `00e560b625582b4b405e802b92f87d3ef7bc854d3000111c429611002f7c57a4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, pit_latest, require_columns
from .._dpd_journey import MODEL_ID_SEGMENT

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# No balance snapshot in the observation month means the card stopped reporting; no anchor.
_BALANCE_MAX_AGE_M = 1


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll.

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if MODEL_ID_SEGMENT[model_id] != "60_180":
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_months=_BALANCE_MAX_AGE_M,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
`````

New:

`````python
"""CC-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, SEG_60_180, pit_latest, require_columns, segment

# OVD_k holds the amount k cycles overdue (DPD bucket k+1): OVD_01 1-30 … OVD_06
# 151-180 DPD. OVD_07 (181-210) and the catch-all OVD_08 (211+) never anchor.
_OVERDUE_BUCKETS = [f"overdue_bucket_{i:02d}" for i in range(1, 7)]
# No balance snapshot in the observation month means the card stopped reporting; no anchor.
_BALANCE_MAX_AGE_M = 1


def build_cc_liquidity_anchor(
    obs_base: DataFrame, prm_balance: DataFrame, model_id: str
) -> DataFrame:
    """Amount in the oldest non-empty overdue bucket on the latest balance snapshot at
    or before the observation date — what the customer must pay to stop the roll (S1).

    Only for the 60-180 segments: at 180+ the buckets no longer track what is due, so
    the anchor is NULL and A1 uses its flat floors. Also NULL (flat floors) when the
    snapshot is missing or stale, or every bucket is empty.
    """
    if segment(model_id) != SEG_60_180:
        return obs_base.select(
            *GRAIN, F.lit(None).cast("double").alias("liquidity_anchor_amt")
        )
    require_columns(
        prm_balance,
        ["contract_id", "observation_date", *_OVERDUE_BUCKETS],
        "prm_balance",
    )
    src = prm_balance.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        *[F.col(c).cast("double") for c in _OVERDUE_BUCKETS],
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=_OVERDUE_BUCKETS,
        inclusive=True,
        max_age_months=_BALANCE_MAX_AGE_M,
    )
    oldest = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKETS)]
    )
    return latest.select(*GRAIN, oldest.alias("liquidity_anchor_amt"))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/nodes.py`
action: replace · base sha256 `9eae59423d4fdb826dc505980402459da0faff534af34ac85ef8485d5057da42` · base trailing newline: yes · new sha256 `a64ea101d8c7d11194c9a41748cc2326892b4520552b4255225d498aaae3c039` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC-A4 — DPD-journey deterioration state for credit cards (thin wrappers on _dpd_journey).

Node 1 build_cc_dpd_sequences    crx_cc_full_history -> crx_cc_dpd_sequences
Node 2 build_cc_a4_deterioration crx_cc_dpd_sequences                    -> crx_cc_a4_deterioration

CC buckets: 0 = no due, 1 = current, 2 = 1-30 DPD ... 7 = 151-180, 8 = 181-210, 9 = 210+.
History before params dpd_journey.cc_history_floor_date (default 2024-01-01, known data-
quality issue, temporary) is not used; accounts with older history are flagged cropped.
cc_180_plus reads its own dpd_journey.cc_history_floor_date_180_plus (same default) instead
-- T43's 2026-10-20 PROD run found the shared floor leaves 99.07% of the gt2y chargeoff-age
vintage "unknown" (their journey start predates the floor by construction); override this
key alone to relax/remove the floor for 180_plus without touching the 60_180 run.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import CC, build_deterioration, build_dpd_sequences, journey_params

# Mirrors cc_spell/nodes.py's _RESTRUCTURE_DLQ_THRESHOLD: an account whose earliest
# billing observation is already at this dlq_bucket or above was opened mid-delinquency
# as part of a restructure (R13), not merely data-depth censored.
_RESTRUCTURE_DLQ_THRESHOLD = 4


def build_cc_dpd_sequences(
    crx_cc_full_history: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One row per CC account: gap-filled monthly bucket array (from the history floor to
    persona_end_date) + audit columns + restructure_blind_spot_flag (R13: 1 if the
    account's earliest billing observation already has dlq_bucket >= _RESTRUCTURE_DLQ_THRESHOLD).
    Derived directly from crx_cc_full_history — no spell-table dependency.
    See _dpd_journey.build_dpd_sequences.
    """
    history = crx_cc_full_history.select(
        "account_id", F.col("billing_date").alias("obs_date"), "dlq_bucket"
    )

    # Earliest dated row per account; F.max is the deterministic tie-break on
    # same-date conflicting rows (more deterministic than the old spell table's
    # row_number() tie-break — a deliberate improvement, not a regression).
    history_dated = history.filter(F.col("dlq_bucket").isNotNull())
    earliest_date = history_dated.groupBy("account_id").agg(
        F.min("obs_date").alias("_first_date")
    )
    restructure = (
        history_dated.join(earliest_date, on="account_id")
        .filter(F.col("obs_date") == F.col("_first_date"))
        .groupBy("account_id")
        .agg(F.max("dlq_bucket").alias("_first_dlq_bucket"))
        .select(
            "account_id",
            (F.col("_first_dlq_bucket") >= F.lit(_RESTRUCTURE_DLQ_THRESHOLD))
            .cast("int")
            .alias("restructure_blind_spot_flag"),
        )
    )
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
    build_cc_dpd_sequences. cc_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here. See _dpd_journey.build_deterioration.
    """
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a4_deterioration/pipeline.py`
action: replace · base sha256 `8aaa558ca4dc42281e09c59e18d7a004d3c11ec53131444c5eb8d36d91bcb9e5` · base trailing newline: yes · new sha256 `e56fb70b9952cea477c433b6399a1e5b80d9a4878aed2664fad5c37fcc363e91` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T43 — DPD-journey deterioration state for Credit Cards.

2-node pipeline:
    Node 1  build_cc_dpd_sequences       -> crx_cc_dpd_sequences
    Node 2  build_cc_a4_deterioration    -> crx_cc_a4_deterioration

Requires crx_cc_full_history to already be materialized.

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
                inputs=[
                    "crx_cc_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_cc_dpd_sequences",
                name="build_crx_cc_dpd_sequences",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
            node(
                func=build_cc_a4_deterioration,
                inputs=[
                    "crx_cc_dpd_sequences",
                    "cc_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_cc_a4_deterioration",
                name="build_crx_cc_a4_deterioration",
                tags=["crx", "cc", "cc_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: CC A4 deterioration state (credit cards).

2-node pipeline:
    Node 1  build_cc_dpd_sequences       -> crx_cc_dpd_sequences
    Node 2  build_cc_a4_deterioration    -> crx_cc_a4_deterioration

Requires crx_cc_full_history to already be materialized.

Run with:
    kedro run --pipeline=crx_cc_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_a4_deterioration, build_cc_dpd_sequences

TAGS = ["crx_persona", "crx", "a4", "deterioration", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Build per-account DPD sequences, then classify the deterioration state."""
    return Pipeline(
        [
            node(
                func=build_cc_dpd_sequences,
                inputs={
                    "crx_cc_full_history": "crx_cc_full_history",
                    "crx_persona": "params:crx_persona",
                    "model_id": "params:model_id",
                },
                outputs="crx_cc_dpd_sequences",
                name="build_crx_cc_dpd_sequences",
                tags=TAGS,
            ),
            node(
                func=build_cc_a4_deterioration,
                inputs={
                    "crx_cc_dpd_sequences": "crx_cc_dpd_sequences",
                    "cc_spine": "cc_spine",
                    "crx_persona": "params:crx_persona",
                    "model_id": "params:model_id",
                },
                outputs="crx_cc_a4_deterioration",
                name="build_crx_cc_a4_deterioration",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_full_history/nodes.py`
action: replace · base sha256 `0a2c8571b186b0bfd163990012085d1d97a6c83046eb20e8ff3b5eeee93bdf48` · base trailing newline: yes · new sha256 `cc2f35b7de3de805cd6e1b923be62013067158f1cf6cf263afa7b621944c3250` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC full billing history (amended). Same output contract as before, plus cif_id:
(account_id long, billing_date date, dlq_bucket int, cif_id) at grain
(account_id, billing_date).

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
        cc_spine: model-namespaced spine of the run (cc_60_180 or cc_180_plus). Columns:
            contract_id, cif_id.

    Returns:
        DataFrame at grain (account_id, billing_date): account_id long, billing_date date,
        dlq_bucket int (NULL when add_info carries no bucket), cif_id (from the spine).
    """
    # -- Step 1 (R20): scope to the spine, distinct leftsemi on the native contract id ----
    # Join BEFORE any cast to string (double "939877870.0" vs "939877870" zeroes the join).
    spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()
    raw_bucket = F.regexp_extract(F.col("add_info"), _DPD_BUCKET_REGEX, 1)
    df = raw_stg_billing.join(
        F.broadcast(spine_keys), "contract_idt", "leftsemi"
    ).select(
        # contract_idt is a whole-number double at the raw boundary -- cast to long (never
        # string), same convention as the rest of crx_persona.
        F.col("contract_idt").cast("long").alias("account_id"),
        F.col("billing_date").cast("date").alias("billing_date"),
        # regexp_extract returns "" when there is no match: NULL, not a failing cast
        F.when(raw_bucket != "", raw_bucket.cast("int")).alias("dlq_bucket"),
    )

    # -- Step 2: one row per (account_id, billing_date), deterministic: worst bucket -------
    history = df.groupBy("account_id", "billing_date").agg(
        F.max("dlq_bucket").alias("dlq_bucket")
    )

    # -- Step 3: attach cif_id from the spine, same bridge convention as build_account_cif_map
    account_cif_map = cc_spine.select(
        F.col("contract_id").cast("long").alias("account_id"), "cif_id"
    ).dropDuplicates(["account_id"])
    return history.join(F.broadcast(account_cif_map), "account_id", "left")
`````

New:

`````python
"""CC full billing history: ``raw_stg_billing`` scoped to the run's ``cc_spine``.

Output ``crx_cc_full_history`` at grain (account_id long, billing_date date) with
``dlq_bucket`` int and ``cif_id`` from the spine. Run:
``kedro run --pipeline=crx_cc_full_history`` (needs the spine of the model_id).

* a bucket that cannot be parsed from ``add_info`` is NULL, never "" cast to int (an
  error under ANSI mode, the default from Spark 4);
* the same-date duplicate takes the worst (max) non-null bucket, so reruns agree;
* no history floor here: ``build_cc_dpd_sequences`` applies it, so it can tell a
  floor-cropped account from a new one.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns

# add_info carries "BS_PMT_CYCLE_DUE=<bucket>".
_DPD_BUCKET_REGEX = r"BS_PMT_CYCLE_DUE=(\d+)"


def build_cc_full_history(raw_stg_billing: DataFrame, cc_spine: DataFrame) -> DataFrame:
    """Full billing history of the run's CC spine.

    Args:
        raw_stg_billing: raw billing table, all CC accounts. Columns: contract_idt (double,
            whole-number account id), billing_date (timestamp), add_info (string carrying
            BS_PMT_CYCLE_DUE=<bucket>).
        cc_spine: model-namespaced spine of the run (cc_60_180 or cc_180_plus). Columns:
            contract_id, cif_id.

    Returns:
        DataFrame at grain (account_id, billing_date): account_id long, billing_date date,
        dlq_bucket int (NULL when add_info carries no bucket), cif_id (from the spine).
    """
    require_columns(
        raw_stg_billing, ["contract_idt", "billing_date", "add_info"], "raw_stg_billing"
    )
    require_columns(cc_spine, ["contract_id", "cif_id"], "cc_spine")
    # -- Step 1: scope to the spine, distinct leftsemi on the native contract id ----
    # Join BEFORE any cast to string (double "939877870.0" vs "939877870" zeroes the join).
    spine_keys = cc_spine.select(F.col("contract_id").alias("contract_idt")).distinct()
    raw_bucket = F.regexp_extract(F.col("add_info"), _DPD_BUCKET_REGEX, 1)
    df = raw_stg_billing.join(
        F.broadcast(spine_keys), "contract_idt", "leftsemi"
    ).select(
        # contract_idt is a whole-number double at the raw boundary -- cast to long (never
        # string), same convention as the rest of crx_persona.
        F.col("contract_idt").cast("long").alias("account_id"),
        F.col("billing_date").cast("date").alias("billing_date"),
        # regexp_extract returns "" when there is no match: NULL, not a failing cast
        F.when(raw_bucket != "", raw_bucket.cast("int")).alias("dlq_bucket"),
    )

    # -- Step 2: one row per (account_id, billing_date), deterministic: worst bucket -------
    history = df.groupBy("account_id", "billing_date").agg(
        F.max("dlq_bucket").alias("dlq_bucket")
    )

    # -- Step 3: attach cif_id from the spine, same bridge convention as build_account_cif_map
    account_cif_map = cc_spine.select(
        F.col("contract_id").cast("long").alias("account_id"), "cif_id"
    ).dropDuplicates(["account_id"])
    return history.join(F.broadcast(account_cif_map), "account_id", "left")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_full_history/pipeline.py`
action: replace · base sha256 `4509112d16b2c0084b55ab849fb40814bba6aa32dcfad6737df499598139a4ec` · base trailing newline: yes · new sha256 `045e51e4614e518120bf2d72201b6b98bc81f4af1f6b56ce97277e31d4d59006` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: crx_cc_full_history — full billing history (ad hoc, mirrors RL-B1)."""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_full_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [raw_stg_billing, cc_spine] → crx_cc_full_history.

    raw_stg_billing provides the full billing history for all CC accounts.
    cc_spine (model_id-namespaced) scopes the scan to the target population
    via leftsemi join. Must run after the spine pipeline for the relevant
    model_id (cc_60_180.spine or cc_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_cc_full_history
    """
    return Pipeline(
        [
            node(
                func=build_cc_full_history,
                inputs=["raw_stg_billing", "cc_spine"],
                outputs="crx_cc_full_history",
                name="build_crx_cc_full_history",
                tags=["crx", "cc", "full_history"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: crx_cc_full_history — full billing history of the CC spine."""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_full_history

TAGS = ["crx_persona", "crx", "full_history"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [raw_stg_billing, cc_spine] → crx_cc_full_history.

    raw_stg_billing provides the full billing history for all CC accounts.
    This is a documented exception to the no-raw-inputs layer rule: no billing
    primary exists yet, so the parsed bucket is built here.
    cc_spine (model_id-namespaced) scopes the scan to the target population
    via leftsemi join. Must run after the spine pipeline for the relevant
    model_id (cc_60_180.spine or cc_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_cc_full_history
    """
    return Pipeline(
        [
            node(
                func=build_cc_full_history,
                inputs={"raw_stg_billing": "raw_stg_billing", "cc_spine": "cc_spine"},
                outputs="crx_cc_full_history",
                name="build_crx_cc_full_history",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py`
action: replace · base sha256 `ad37f337f49bf07fa13842a86066cb8620521070c89dd09f8572c9d16692236c` · base trailing newline: yes · new sha256 `c3e94d5dae0d7568bb87fc616573c1edfec1382975933170dd758af19f12cfef` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipelines building the observation base every persona axis reads: the spine's
month-end rows from ``crx_persona.persona_start_date`` to ``persona_end_date``.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_cc_obs_base from cc_spine."""
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs=["cc_spine", "params:crx_persona"],
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_rl_obs_base from rl_spine."""
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs=["rl_spine", "params:crx_persona"],
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )
`````

New:

`````python
"""Kedro pipelines building the observation base every persona axis reads: the spine's
month-end rows from ``crx_persona.persona_start_date`` to ``persona_end_date``.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_cc_obs_base from cc_spine."""
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs={"cc_spine": "cc_spine", "crx_persona": "params:crx_persona"},
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """crx_rl_obs_base from rl_spine."""
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs={"rl_spine": "rl_spine", "crx_persona": "params:crx_persona"},
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
                tags=["crx_persona", "crx", "obs_base"],
            )
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rf_check.py`
action: add · new sha256 `ad90fdc6d1c10b0d277cc0fd78749b5751375ffda73518616306b1b9de56cf3e` · new trailing newline: yes

New:

`````python
"""TEMPORARY (refactor bundle R-B): zero-difference checks for the refactored A1, A2, A4.

Each check pipeline re-runs one axis (with the inputs it rebuilds: obs base, full
history) in its own namespace, writes the new outputs to ``*_rf_check`` entries and
compares them with the outputs persisted before the bundle. Nothing real is
overwritten. Logged blocks: ``RF <NAME> OUTPUT``, ``RF A2 DCORE``, ``RF KEYS``,
``RF STRING KEYS``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_<a4|a2|a1>_rf_check
"""

# pylint: disable=protected-access

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .obs_base import pipeline as obs_base
from ._common import GRAIN, dcore_account_events
from .a2_locatability import signals as a2_signals
from .cc_a1_ability.pipeline import create_pipeline as cc_a1
from .cc_a2_locatability.pipeline import create_pipeline as cc_a2
from .cc_a4_deterioration.pipeline import create_pipeline as cc_a4
from .cc_full_history.pipeline import create_pipeline as cc_full_history
from .rl_a1_ability.pipeline import create_pipeline as rl_a1
from .rl_a2_locatability.pipeline import create_pipeline as rl_a2
from .rl_a4_deterioration.pipeline import create_pipeline as rl_a4
from .rl_full_history.pipeline import create_pipeline as rl_full_history

logger = logging.getLogger(__name__)
TAGS = ["crx_persona", "crx", "rf_check"]

# Join-key columns of the sources the refactor reads, per product (Q-21 sites).
STRING_KEY_SITES = {
    "cc": {
        "cc_spine": ["contract_id", "cif_id"],
        "prm_balance": ["contract_id"],
        "prm_contract": ["contract_id"],
    },
    "rl": {
        "rl_spine": ["account_id", "cif_id"],
        "int_loan_master": ["account_id"],
        "feature_retail_loans": ["account_id"],
    },
    "both": {
        "dcore_prm_followup_outcomes": ["agreement_id"],
        "prm_dcore_account_agreements": ["account_id", "agreement_id"],
        "feat_demographics_cif": ["cif_id"],
        "feat_cif_internal_salary_monthly": ["cif_id"],
    },
}


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== RF %s START ===\n%s\n=== RF %s END ===", name, body, name)


def compare_outputs(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    old: DataFrame, new: DataFrame, model_id: str, name: str, keys: list, state: str
) -> None:
    """Rows, schema, rows only in one side; old x new ``state`` on ``keys`` if given."""
    lines = [
        f"model_id: {model_id}",
        f"rows old / new: {old.count()} / {new.count()}",
    ]
    same = old.schema.simpleString() == new.schema.simpleString()
    lines.append(f"same schema: {same}")
    if not same:
        o, n = dict(old.dtypes), dict(new.dtypes)
        lines.append(
            f"only old: {sorted(set(o) - set(n))}; only new: {sorted(set(n) - set(o))}"
        )
        lines.append(
            f"type differs: {sorted(c for c in set(o) & set(n) if o[c] != n[c])}"
        )
    # computed_at is the run's timestamp, so it differs on every row by construction.
    cols = [c for c in old.columns if c in new.columns and c != "computed_at"]

    def hashes(df: DataFrame, side: str) -> DataFrame:
        return df.groupBy(F.xxhash64(*cols).alias("h")).agg(F.count("*").alias(side))

    diff = (
        hashes(old, "o")
        .join(hashes(new, "n"), on="h", how="full")
        .agg(
            F.sum(
                F.greatest(
                    F.coalesce("o", F.lit(0)) - F.coalesce("n", F.lit(0)), F.lit(0)
                )
            ).alias("o"),
            F.sum(
                F.greatest(
                    F.coalesce("n", F.lit(0)) - F.coalesce("o", F.lit(0)), F.lit(0)
                )
            ).alias("n"),
        )
        .first()
    )
    lines.append(f"rows only in old: {diff['o'] or 0}")
    lines.append(f"rows only in new: {diff['n'] or 0}")
    if state:
        both = old.select(*keys, F.col(state).alias("old")).join(
            new.select(*keys, F.col(state).alias("new")), on=keys, how="full"
        )
        moved = both.filter(~F.col("old").eqNullSafe(F.col("new"))).count()
        lines.append(f"rows whose {state} differs: {moved}")
        for r in both.groupBy("old", "new").count().orderBy("old", "new").collect():
            lines.append(f"  {r['old']} -> {r['new']}: {r['count']}")
    _block(f"{name} OUTPUT", lines)


def describe_a2_inputs(
    obs: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> None:
    """N-3: rows into the DCORE aggregate and the non-attempt share; N-4: key counts."""
    days = (
        obs.select(*GRAIN)
        .join(
            a2_signals._dcore_days(dcore_account_events(obs, followup, agreements)),
            "account_id",
        )
        .filter(F.col("day") <= F.col("observation_date"))
    )
    r = days.agg(
        F.count("*").alias("n"),
        F.avg((F.col("_attempt") != 1).cast("double")).alias("p"),
    ).first()
    _block(
        "A2 DCORE",
        [
            f"model_id: {model_id}",
            f"rows into the DCORE aggregate: {r['n']}",
            f"share of non-attempt days: {r['p']}",
            "stage spill / shuffle read of build_*_a2_dcore_signals: read from the Spark UI",
        ],
    )
    k = obs.agg(
        F.countDistinct("cif_id").alias("c"), F.countDistinct("account_id").alias("a")
    ).first()
    _block(
        "KEYS",
        [
            f"model_id: {model_id}",
            f"distinct cif_id: {k['c']}",
            f"distinct account_id: {k['a']}",
        ],
    )


def describe_string_keys(model_id: str, **sources: DataFrame) -> None:
    """Per source key: its type and how many values change under trim."""
    sites = {
        **STRING_KEY_SITES["cc"],
        **STRING_KEY_SITES["rl"],
        **STRING_KEY_SITES["both"],
    }
    lines = [f"model_id: {model_id}"]
    for name, df in sources.items():
        types = dict(df.dtypes)
        present = [c for c in sites[name] if c in types]
        lines += [f"{name}.{c}: missing" for c in sites[name] if c not in types]
        if not present:
            continue
        aggs = []
        for c in present:
            s = F.col(c).cast("string")
            aggs.append(F.sum((s != F.trim(s)).cast("int")).alias(c))
        row = df.agg(*aggs).first()
        lines += [f"{name}.{c} ({types[c]}): {row[c] or 0} padded" for c in present]
    _block("STRING KEYS", lines)


def _scoped(pipe: Pipeline, product: str, rename: dict) -> Pipeline:
    """``pipe`` in the ``rf_<p>`` namespace: free inputs and params keep their names,
    ``rename`` maps outputs to their check entries, the rest stays in memory."""
    inputs = {i for i in pipe.inputs() if not i.startswith("params:")}
    params = {i for i in pipe.all_inputs() if i.startswith("params:")}
    return pipeline(
        pipe,
        namespace=f"rf_{product}",
        inputs=inputs,
        outputs=rename,
        parameters=params,
    )


def _compare(name: str, real: str, keys, state: str = "") -> Pipeline:
    return Pipeline(
        [
            node(
                func=partial(compare_outputs, name=name, keys=list(keys), state=state),
                inputs={
                    "old": real,
                    "new": f"{real}_rf_check",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name=f"compare_{real}_rf",
                tags=TAGS,
            )
        ]
    )


def create_a4_rf_check_pipeline(product: str) -> Pipeline:
    """Full history + A4 into check entries; compares both."""
    history, state = f"crx_{product}_full_history", f"crx_{product}_a4_deterioration"
    build = (
        (cc_full_history() + cc_a4())
        if product == "cc"
        else (rl_full_history() + rl_a4())
    )
    rename = {history: f"{history}_rf_check", state: f"{state}_rf_check"}
    return (
        _scoped(build, product, rename)
        + _compare("FULL HISTORY", history, ())
        + _compare("A4", state, GRAIN, "det_state")
    )


def create_a2_rf_check_pipeline(product: str) -> Pipeline:
    """Obs base + A2 into check entries; compares A2, logs DCORE and key counts."""
    obs, out = f"crx_{product}_obs_base", f"crx_{product}_a2_locatability"
    base = (
        obs_base.create_cc_pipeline()
        if product == "cc"
        else obs_base.create_rl_pipeline()
    )
    axis = cc_a2() if product == "cc" else rl_a2()
    describe = node(
        func=describe_a2_inputs,
        inputs={
            "obs": obs,
            "followup": "dcore_prm_followup_outcomes",
            "agreements": "prm_dcore_account_agreements",
            "model_id": "params:model_id",
        },
        outputs=None,
        name=f"describe_{out}_rf",
        tags=TAGS,
    )
    return (
        _scoped(base + axis, product, {out: f"{out}_rf_check"})
        + _compare("A2", out, GRAIN, "a2_state")
        + Pipeline([describe])
    )


def create_a1_rf_check_pipeline(product: str) -> Pipeline:
    """Obs base + A1 into check entries; compares both, logs the string-key counts."""
    obs, out = f"crx_{product}_obs_base", f"crx_{product}_a1_ability"
    base = (
        obs_base.create_cc_pipeline()
        if product == "cc"
        else obs_base.create_rl_pipeline()
    )
    axis = cc_a1() if product == "cc" else rl_a1()
    sources = {**STRING_KEY_SITES[product], **STRING_KEY_SITES["both"]}
    keys = node(
        func=describe_string_keys,
        inputs={"model_id": "params:model_id", **{s: s for s in sources}},
        outputs=None,
        name=f"describe_crx_{product}_rf_string_keys",
        tags=TAGS,
    )
    return (
        _scoped(base + axis, product, {obs: f"{obs}_rf_check", out: f"{out}_rf_check"})
        + _compare("OBS BASE", obs, GRAIN)
        + _compare("A1", out, GRAIN, "a1_state")
        + Pipeline([keys])
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py`
action: replace · base sha256 `af87ae0a282a508d5dd43f11928eeda3286fb5769d00fd2659aa745951f751a7` · base trailing newline: yes · new sha256 `23f671214c3dcdf1de701638f0f8c80ed854dde309e093e49df1184dbd1a2f78` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, lookback_floor, pit_latest, require_columns

# int_loan_master is a month-end snapshot; none in the observation month means no anchor.
_LOAN_MAX_AGE_M = 1


def build_rl_liquidity_anchor(
    obs_base: DataFrame, int_loan_master: DataFrame
) -> DataFrame:
    """One EMI — ``installment_due_amount`` on the loan's snapshot in the observation
    month. NULL (flat floors) when the snapshot is missing or the EMI is not positive.
    """
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "installment_due_amount"],
        "int_loan_master",
    )
    since = lookback_floor(obs_base, _LOAN_MAX_AGE_M)
    src = int_loan_master.filter(F.col("observation_date") >= F.lit(since)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("installment_due_amount").cast("double").alias("emi"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["emi"],
        inclusive=True,
        max_age_months=_LOAN_MAX_AGE_M,
    )
    return latest.select(
        *GRAIN, F.when(F.col("emi") > 0, F.col("emi")).alias("liquidity_anchor_amt")
    )
`````

New:

`````python
"""RL-specific part of the A1 ability axis: the liquidity anchor.

Everything else (evidence, levels, points, state) is the shared ``a1_ability`` engine.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, lookback_floor, pit_latest, require_columns

# int_loan_master is a month-end snapshot; none in the observation month means no anchor.
_LOAN_MAX_AGE_M = 1


def build_rl_liquidity_anchor(
    obs_base: DataFrame, int_loan_master: DataFrame
) -> DataFrame:
    """One EMI (S1): ``installment_due_amount`` on the loan's snapshot in the
    observation month. NULL (flat floors) when the snapshot is missing or the EMI is not
    positive.
    """
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "installment_due_amount"],
        "int_loan_master",
    )
    since = lookback_floor(obs_base, _LOAN_MAX_AGE_M)
    src = int_loan_master.filter(F.col("observation_date") >= F.lit(since)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("snapshot_date"),
        F.col("installment_due_amount").cast("double").alias("emi"),
    )
    latest = pit_latest(
        obs_base,
        src,
        key="account_id",
        date_col="snapshot_date",
        value_cols=["emi"],
        inclusive=True,
        max_age_months=_LOAN_MAX_AGE_M,
    )
    return latest.select(
        *GRAIN, F.when(F.col("emi") > 0, F.col("emi")).alias("liquidity_anchor_amt")
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py`
action: replace · base sha256 `03e71607f8704f47eecb5035ff4660a46d9e67ea2097b77a7c6f29103a94a449` · base trailing newline: yes · new sha256 `6b1319d4adda2f38834e916496770bc684c8206529c5d4ea02b3971567f927d1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4-3 — DPD-journey deterioration state pipeline for Retail Loans."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A4 deterioration state (retail loans) on the shared ``_dpd_journey`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py`
action: replace · base sha256 `9087ba44674bb2d61fdf3309e14220ec981cafc81e3d21d6cea95e380b9a474f` · base trailing newline: yes · new sha256 `5b07f09efbec63fd29cd7172f34548d791f7052329d3e6c556b40c16d10d01c4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_full_history_linked  crx_rl_full_history + int_loan_master
                                     + int_loan_restructure_link
                                     -> crx_rl_full_history_linked, crx_rl_restructure_chains
Node 2 build_rl_dpd_sequences        crx_rl_full_history + feature_retail_loans
                                     -> crx_rl_dpd_sequences
Node 3 build_rl_linked_dpd_sequences crx_rl_full_history_linked + chains
                                     + feature_retail_loans -> crx_rl_dpd_sequences_linked
Node 4 build_rl_a4_deterioration     both sequences + chains -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).

A restructure closes the old account and opens a new one. A matched new account gets the
original loans' months in front of its own, from the month both the restructure flag and
the closure have happened; before that month it keeps its own history, so nothing leaks
from the future. A loan is restructured if feature_retail_loans.has_restructured_loan_flag
says so; one with no original loan's months stays a blind spot.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns
from .._dpd_journey import (
    RL,
    _log_state_stats,
    build_deterioration,
    build_dpd_sequences,
    journey_params,
)
from .chains import Edge, resolve_chains

# Account columns of int_loan_restructure_link.
_LINK_ACCOUNT = "account_id"
_LINK_ORIGINAL = "orig_account_id"

_CHAIN_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("chain_known_date", T.DateType()),
        T.StructField("chain_n_originals", T.IntegerType()),
        T.StructField("chain_match_type", T.StringType()),
        T.StructField("chain_candidate_count", T.IntegerType()),
    ]
)
_MEMBER_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("original_id", T.StringType()),
    ]
)


def _edges(link: DataFrame) -> list[Edge]:
    """Matched link rows as ``Edge``s (an unmatched row has no original)."""
    rows = (
        link.filter(F.col(_LINK_ORIGINAL).isNotNull())
        .select(
            F.trim(F.col(_LINK_ACCOUNT).cast("string")).alias("account"),
            F.trim(F.col(_LINK_ORIGINAL).cast("string")).alias("original"),
            F.greatest(
                F.col("restr_flagged_date").cast("date"),
                F.col("orig_close_date").cast("date"),
            ).alias("known"),
            "match_type",
            F.col("candidate_count").cast("int").alias("candidates"),
        )
        .collect()
    )
    return [Edge(*r) for r in rows]


def build_rl_full_history_linked(
    crx_rl_full_history: DataFrame,
    int_loan_master: DataFrame,
    int_loan_restructure_link: DataFrame,
) -> tuple[DataFrame, DataFrame]:
    """Every spine account's history, with each matched restructured account's original
    loans re-keyed in front of its own months.

    Original rows: closed months dropped (their zero DPD would fake a cure), the worst
    bucket per month across originals, the account's own row kept where months overlap.

    Returns:
        crx_rl_full_history_linked: account_id, month_end_date, dlq_bucket.
        crx_rl_restructure_chains: one row per chain: account_id, chain_known_date,
        chain_n_originals, chain_match_type, chain_candidate_count, chain_months_added.
    """
    require_columns(
        int_loan_restructure_link,
        (
            _LINK_ACCOUNT,
            _LINK_ORIGINAL,
            "restr_flagged_date",
            "orig_close_date",
            "match_type",
            "candidate_count",
        ),
        "int_loan_restructure_link",
    )
    require_columns(
        int_loan_master,
        (
            "account_id",
            "observation_date",
            "dpd_bucket",
            "account_status",
        ),
        "int_loan_master",
    )
    own = crx_rl_full_history.select(
        "account_id",
        F.last_day("month_end_date").alias("month_end_date"),
        "dlq_bucket",
    )
    accounts = [r[0] for r in own.select("account_id").distinct().collect()]
    chains, members = resolve_chains(_edges(int_loan_restructure_link), accounts)
    spark = crx_rl_full_history.sparkSession
    chain_df = spark.createDataFrame([tuple(c) for c in chains], _CHAIN_SCHEMA)
    member_df = spark.createDataFrame([tuple(m) for m in members], _MEMBER_SCHEMA)

    original = (
        int_loan_master.select(
            F.trim(F.col("account_id").cast("string")).alias("original_id"),
            F.last_day(F.col("observation_date").cast("date")).alias("month_end_date"),
            F.col("dpd_bucket").cast("int").alias("dlq_bucket"),
            F.upper(F.col("account_status")).alias("_status"),
        )
        .join(F.broadcast(member_df), on="original_id")
        .filter(F.coalesce(F.col("_status"), F.lit("")) != "CLOSED")
        .groupBy("account_id", "month_end_date")
        .agg(F.max("dlq_bucket").alias("dlq_bucket"))
        .join(own, on=["account_id", "month_end_date"], how="left_anti")
    )
    added = original.groupBy("account_id").agg(
        F.count(F.lit(1)).cast("int").alias("chain_months_added")
    )
    chain_out = chain_df.join(added, on="account_id", how="left").withColumn(
        "chain_months_added", F.coalesce("chain_months_added", F.lit(0))
    )
    return own.unionByName(original), chain_out


def _history(full_history: DataFrame) -> DataFrame:
    return full_history.select(
        "account_id",
        F.col("month_end_date").alias("obs_date"),
        "dlq_bucket",
    )


def _restructured(feature_retail_loans: DataFrame) -> DataFrame:
    """One row per account: 1 if ``has_restructured_loan_flag`` is ever set."""
    require_columns(
        feature_retail_loans,
        ("account_id", "has_restructured_loan_flag"),
        "feature_retail_loans",
    )
    return feature_retail_loans.groupBy(
        F.trim(F.col("account_id").cast("string")).alias("account_id")
    ).agg(
        F.max(F.col("has_restructured_loan_flag").cast("int")).alias(
            "restructure_blind_spot_flag"
        )
    )


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (the loan is restructured)."""
    return build_dpd_sequences(
        _history(crx_rl_full_history),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans),
    )


def build_rl_linked_dpd_sequences(
    crx_rl_full_history_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """As build_rl_dpd_sequences on the linked history: an account with the original
    loans' months in front of its own is no longer a blind spot."""
    stitched = crx_rl_restructure_chains.filter(F.col("chain_months_added") > 0).select(
        "account_id"
    )
    return build_dpd_sequences(
        _history(crx_rl_full_history_linked),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans).join(
            F.broadcast(stitched), on="account_id", how="left_anti"
        ),
    )


def build_rl_a4_deterioration(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    crx_rl_dpd_sequences: DataFrame,
    crx_rl_dpd_sequences_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here.

    A row before its chain's ``chain_known_date`` reads the account's own history, every
    other row the linked one. Adds the ``chain_*`` columns of crx_rl_restructure_chains
    and chain_stitched_flag (1 if this row's history has the original loans' months)."""
    params = journey_params(crx_persona, RL, model_id)
    chains = F.broadcast(crx_rl_restructure_chains)
    spine = rl_spine.select(
        F.trim(F.col("account_id").cast("string")).alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
    ).join(chains.select("account_id", "chain_known_date"), on="account_id", how="left")
    before_chain = F.coalesce(
        F.col("observation_date") < F.col("chain_known_date"), F.lit(False)
    )
    keys = ("account_id", "observation_date")
    out = build_deterioration(
        crx_rl_dpd_sequences_linked,
        RL,
        params,
        spine.filter(~before_chain).select(*keys),
        log_states=False,
    ).unionByName(
        build_deterioration(
            crx_rl_dpd_sequences,
            RL,
            params,
            spine.filter(before_chain).select(*keys),
            log_states=False,
        )
    )
    out = out.join(chains, on="account_id", how="left").withColumn(
        "chain_stitched_flag",
        F.coalesce(
            (F.col("observation_date") >= F.col("chain_known_date"))
            & (F.col("chain_months_added") > 0),
            F.lit(False),
        ).cast("int"),
    )
    _log_state_stats(out, params.end_date, RL, params)
    return out
`````

New:

`````python
"""RL A4 — deterioration state for retail loans (wrappers on ``_dpd_journey``).

Node 1 build_rl_full_history_linked  crx_rl_full_history + int_loan_master
                                     + int_loan_restructure_link
                                     -> crx_rl_full_history_linked,
                                        crx_rl_restructure_chains
Node 2 build_rl_dpd_sequences        crx_rl_full_history + feature_retail_loans
                                     -> crx_rl_dpd_sequences
Node 3 build_rl_linked_dpd_sequences crx_rl_full_history_linked + chains
                                     + feature_retail_loans
                                     -> crx_rl_dpd_sequences_linked
Node 4 build_rl_a4_deterioration     both sequences + chains
                                     -> crx_rl_a4_deterioration
Run: ``kedro run --pipeline=crx_rl_a4_deterioration`` (needs crx_rl_full_history).

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The
engine maps them onto the CC scale (+1), so every rule and threshold is shared with CC.
The 60-180 segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full
(no floor).

A restructure closes the old account and opens a new one. A matched new account gets the
original loans' months in front of its own, from the month both the restructure flag and
the closure have happened; before that month it keeps its own history, so nothing leaks
from the future (conformance D6). A loan is restructured if
feature_retail_loans.has_restructured_loan_flag says so (D2); one with no original
loan's months stays a blind spot.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns, string_key
from .._dpd_journey import (
    RL,
    build_deterioration,
    build_dpd_sequences,
    journey_params,
    log_state_stats,
)
from .chains import Edge, resolve_chains

# Account columns of int_loan_restructure_link.
_LINK_ACCOUNT = "account_id"
_LINK_ORIGINAL = "orig_account_id"

_CHAIN_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("chain_known_date", T.DateType()),
        T.StructField("chain_n_originals", T.IntegerType()),
        T.StructField("chain_match_type", T.StringType()),
        T.StructField("chain_candidate_count", T.IntegerType()),
    ]
)
_MEMBER_SCHEMA = T.StructType(
    [
        T.StructField("account_id", T.StringType()),
        T.StructField("original_id", T.StringType()),
    ]
)


def _edges(link: DataFrame) -> list[Edge]:
    """Matched link rows as ``Edge``s (an unmatched row has no original)."""
    rows = (
        link.filter(F.col(_LINK_ORIGINAL).isNotNull())
        .select(
            string_key(link, _LINK_ACCOUNT).alias("account"),
            string_key(link, _LINK_ORIGINAL).alias("original"),
            F.greatest(
                F.col("restr_flagged_date").cast("date"),
                F.col("orig_close_date").cast("date"),
            ).alias("known"),
            "match_type",
            F.col("candidate_count").cast("int").alias("candidates"),
        )
        .collect()
    )
    return [Edge(*r) for r in rows]


def _original_loan_months(
    own: DataFrame, int_loan_master: DataFrame, chains: list, members: list
) -> tuple[DataFrame, DataFrame]:
    """Restructure chains: the originals' months to put in front of each account's own.

    Returns (account_id, month_end_date, dlq_bucket) rows, and the chains table with
    chain_months_added. Only chains of accounts in `own` are kept. Closed months are
    dropped (their zero DPD would fake a cure), the worst bucket wins per month, and
    the account's own row stays where months overlap.
    """
    in_history = F.broadcast(own.select("account_id").distinct())
    spark = own.sparkSession
    chain_df = spark.createDataFrame([tuple(r) for r in chains], _CHAIN_SCHEMA)
    member_df = spark.createDataFrame([tuple(r) for r in members], _MEMBER_SCHEMA)
    chain_df = chain_df.join(in_history, on="account_id", how="leftsemi")
    member_df = member_df.join(in_history, on="account_id", how="leftsemi")
    original = (
        int_loan_master.select(
            string_key(int_loan_master).alias("original_id"),
            F.last_day(F.col("observation_date").cast("date")).alias("month_end_date"),
            F.col("dpd_bucket").cast("int").alias("dlq_bucket"),
            F.upper(F.col("account_status")).alias("_status"),
        )
        .join(F.broadcast(member_df), on="original_id")
        .filter(F.coalesce(F.col("_status"), F.lit("")) != "CLOSED")
        .groupBy("account_id", "month_end_date")
        .agg(F.max("dlq_bucket").alias("dlq_bucket"))
        .join(own, on=["account_id", "month_end_date"], how="left_anti")
    )
    added = original.groupBy("account_id").agg(
        F.count(F.lit(1)).cast("int").alias("chain_months_added")
    )
    chain_out = chain_df.join(added, on="account_id", how="left").withColumn(
        "chain_months_added", F.coalesce("chain_months_added", F.lit(0))
    )
    return original, chain_out


def build_rl_full_history_linked(
    crx_rl_full_history: DataFrame,
    int_loan_master: DataFrame,
    int_loan_restructure_link: DataFrame,
) -> tuple[DataFrame, DataFrame]:
    """Every spine account's history, with each matched restructured account's original
    loans re-keyed in front of its own months.

    Returns:
        crx_rl_full_history_linked: account_id, month_end_date, dlq_bucket.
        crx_rl_restructure_chains: one row per chain: account_id, chain_known_date,
        chain_n_originals, chain_match_type, chain_candidate_count, chain_months_added.
    """
    require_columns(
        int_loan_restructure_link,
        (
            _LINK_ACCOUNT,
            _LINK_ORIGINAL,
            "restr_flagged_date",
            "orig_close_date",
            "match_type",
            "candidate_count",
        ),
        "int_loan_restructure_link",
    )
    require_columns(
        int_loan_master,
        ("account_id", "observation_date", "dpd_bucket", "account_status"),
        "int_loan_master",
    )
    own = crx_rl_full_history.select(
        "account_id", F.last_day("month_end_date").alias("month_end_date"), "dlq_bucket"
    )
    edges = _edges(int_loan_restructure_link)
    chains, members = resolve_chains(edges, {e.account for e in edges})
    original, chain_out = _original_loan_months(own, int_loan_master, chains, members)
    return own.unionByName(original), chain_out


def _history(full_history: DataFrame) -> DataFrame:
    return full_history.select(
        "account_id", F.col("month_end_date").alias("obs_date"), "dlq_bucket"
    )


def _restructured(feature_retail_loans: DataFrame) -> DataFrame:
    """One row per account: 1 if ``has_restructured_loan_flag`` is ever set."""
    require_columns(
        feature_retail_loans,
        ("account_id", "has_restructured_loan_flag"),
        "feature_retail_loans",
    )
    return feature_retail_loans.groupBy(
        string_key(feature_retail_loans).alias("account_id")
    ).agg(
        F.max(F.col("has_restructured_loan_flag").cast("int")).alias(
            "restructure_blind_spot_flag"
        )
    )


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (the loan is restructured)."""
    require_columns(
        crx_rl_full_history,
        ("account_id", "month_end_date", "dlq_bucket"),
        "crx_rl_full_history",
    )
    return build_dpd_sequences(
        _history(crx_rl_full_history),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans),
    )


def build_rl_linked_dpd_sequences(
    crx_rl_full_history_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """As build_rl_dpd_sequences on the linked history: an account with the original
    loans' months in front of its own is no longer a blind spot."""
    require_columns(
        crx_rl_full_history_linked,
        ("account_id", "month_end_date", "dlq_bucket"),
        "crx_rl_full_history_linked",
    )
    stitched = crx_rl_restructure_chains.filter(F.col("chain_months_added") > 0).select(
        "account_id"
    )
    return build_dpd_sequences(
        _history(crx_rl_full_history_linked),
        RL,
        journey_params(crx_persona, RL, model_id),
        restructure=_restructured(feature_retail_loans).join(
            F.broadcast(stitched), on="account_id", how="left_anti"
        ),
    )


def build_rl_a4_deterioration(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    crx_rl_dpd_sequences: DataFrame,
    crx_rl_dpd_sequences_linked: DataFrame,
    crx_rl_restructure_chains: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already scoped to the model_id's DLQ band, so no
    segment filter is applied here.

    A row before its chain's ``chain_known_date`` reads the account's own history, every
    other row the linked one. Adds the ``chain_*`` columns of crx_rl_restructure_chains
    and chain_stitched_flag (1 if this row's history has the original loans' months)."""
    require_columns(rl_spine, ("account_id", "observation_date"), "rl_spine")
    params = journey_params(crx_persona, RL, model_id)
    chains = F.broadcast(crx_rl_restructure_chains)
    spine = rl_spine.select(
        string_key(rl_spine).alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
    ).join(chains.select("account_id", "chain_known_date"), on="account_id", how="left")
    before_chain = F.coalesce(
        F.col("observation_date") < F.col("chain_known_date"), F.lit(False)
    )
    keys = ("account_id", "observation_date")
    out = build_deterioration(
        crx_rl_dpd_sequences_linked,
        RL,
        params,
        spine.filter(~before_chain).select(*keys),
        log_states=False,
    ).unionByName(
        build_deterioration(
            crx_rl_dpd_sequences,
            RL,
            params,
            spine.filter(before_chain).select(*keys),
            log_states=False,
        )
    )
    out = out.join(chains, on="account_id", how="left").withColumn(
        "chain_stitched_flag",
        F.coalesce(
            (F.col("observation_date") >= F.col("chain_known_date"))
            & (F.col("chain_months_added") > 0),
            F.lit(False),
        ).cast("int"),
    )
    log_state_stats(out, params.end_date, RL, params)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py`
action: replace · base sha256 `f8d8e64175b32d3b73da3d85550c4f0d154ccfdd9053dd9bd24ea1f7fe86e20e` · base trailing newline: yes · new sha256 `69379750e29bab065ca8d59f69b609f187b783cf3198d8c6e8ce844695dfffb5` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

4-node pipeline:
    Node 1  build_rl_full_history_linked -> crx_rl_full_history_linked,
                                            crx_rl_restructure_chains
    Node 2  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 3  build_rl_linked_dpd_sequences -> crx_rl_dpd_sequences_linked
    Node 4  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
    build_rl_linked_dpd_sequences,
)


def _linked_node() -> node:
    return node(
        func=build_rl_full_history_linked,
        inputs=[
            "crx_rl_full_history",
            "int_loan_master",
            "int_loan_restructure_link",
        ],
        outputs=["crx_rl_full_history_linked", "crx_rl_restructure_chains"],
        name="build_crx_rl_full_history_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _sequences_node(output: str) -> node:
    return node(
        func=build_rl_dpd_sequences,
        inputs=[
            "crx_rl_full_history",
            "feature_retail_loans",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _linked_sequences_node() -> node:
    return node(
        func=build_rl_linked_dpd_sequences,
        inputs=[
            "crx_rl_full_history_linked",
            "crx_rl_restructure_chains",
            "feature_retail_loans",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs="crx_rl_dpd_sequences_linked",
        name="build_crx_rl_dpd_sequences_linked",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def _state_node(own: str, output: str) -> node:
    return node(
        func=build_rl_a4_deterioration,
        inputs=[
            own,
            "crx_rl_dpd_sequences_linked",
            "crx_rl_restructure_chains",
            "rl_spine",
            "params:crx_persona",
            "params:model_id",
        ],
        outputs=output,
        name=f"build_{output}",
        tags=["crx", "rl", "rl_a4_deterioration"],
    )


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Link the restructured loans, build both sequences, classify deterioration state."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_dpd_sequences"),
            _linked_sequences_node(),
            _state_node("crx_rl_dpd_sequences", "crx_rl_a4_deterioration"),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL A4 deterioration state (retail loans).

4-node pipeline:
    Node 1  build_rl_full_history_linked -> crx_rl_full_history_linked,
                                            crx_rl_restructure_chains
    Node 2  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 3  build_rl_linked_dpd_sequences -> crx_rl_dpd_sequences_linked
    Node 4  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
    build_rl_linked_dpd_sequences,
)

TAGS = ["crx_persona", "crx", "a4", "deterioration", "persona_axis"]


def _linked_node() -> node:
    return node(
        func=build_rl_full_history_linked,
        inputs={
            "crx_rl_full_history": "crx_rl_full_history",
            "int_loan_master": "int_loan_master",
            "int_loan_restructure_link": "int_loan_restructure_link",
        },
        outputs=["crx_rl_full_history_linked", "crx_rl_restructure_chains"],
        name="build_crx_rl_full_history_linked",
        tags=TAGS,
    )


def _sequences_node(output: str) -> node:
    return node(
        func=build_rl_dpd_sequences,
        inputs={
            "crx_rl_full_history": "crx_rl_full_history",
            "feature_retail_loans": "feature_retail_loans",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
        outputs=output,
        name=f"build_{output}",
        tags=TAGS,
    )


def _linked_sequences_node() -> node:
    return node(
        func=build_rl_linked_dpd_sequences,
        inputs={
            "crx_rl_full_history_linked": "crx_rl_full_history_linked",
            "crx_rl_restructure_chains": "crx_rl_restructure_chains",
            "feature_retail_loans": "feature_retail_loans",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
        outputs="crx_rl_dpd_sequences_linked",
        name="build_crx_rl_dpd_sequences_linked",
        tags=TAGS,
    )


def _state_node(own: str, output: str) -> node:
    return node(
        func=build_rl_a4_deterioration,
        inputs={
            "crx_rl_dpd_sequences": own,
            "crx_rl_dpd_sequences_linked": "crx_rl_dpd_sequences_linked",
            "crx_rl_restructure_chains": "crx_rl_restructure_chains",
            "rl_spine": "rl_spine",
            "crx_persona": "params:crx_persona",
            "model_id": "params:model_id",
        },
        outputs=output,
        name=f"build_{output}",
        tags=TAGS,
    )


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Link restructured loans, build both sequences, classify the state."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_dpd_sequences"),
            _linked_sequences_node(),
            _state_node("crx_rl_dpd_sequences", "crx_rl_a4_deterioration"),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_full_history/nodes.py`
action: replace · base sha256 `c45a11daed8c58243be19a5a08c597653bfe89fbc09cab8fcaf57f9ddf260e5e` · base trailing newline: yes · new sha256 `c63c8d9e325853d134e5caf9853c63258984e6cc6704af111d9d143f91f61c47` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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


def build_rl_full_history(
    rl_spine: DataFrame, int_loan_master: DataFrame, crx_persona: dict | None = None
) -> DataFrame:
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

    # -- Step 2: select + alias + cast to the output schema ----------------------------
    result = df.select(
        F.col("cif_id").cast("string"),
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
    r = (
        df.agg(
            F.count("*").alias("rows"),
            F.countDistinct("account_id").alias("accounts"),
            F.min("month_end_date").alias("first_month"),
            F.max("month_end_date").alias("last_month"),
            *[
                F.avg(F.col(c).isNull().cast("double")).alias(f"null_{c}")
                for c in ("dlq_bucket", "month_end_date", "restructure_flag")
            ],
        )
        .first()
        .asDict()
    )
    r["spine_accounts"] = spine_keys.count()
    LOG.info(
        "build_rl_full_history: %s (spine accounts found: %s of %s)",
        r,
        r["accounts"],
        r["spine_accounts"],
    )
`````

New:

`````python
"""RL full monthly history: ``int_loan_master`` scoped to the run's ``rl_spine``.

Output ``crx_rl_full_history`` at grain (account_id, month_end_date). Run:
``kedro run --pipeline=crx_rl_full_history`` (needs the spine of the model_id).

* the spine key is cast to string safely: a double/decimal account_id goes through
  long first (double -> string gives "1.23456789E8" and silently empties the left-semi
  join);
* the spine keys are broadcast: they are tiny, and without the hint Spark may shuffle
  the whole int_loan_master (all RL accounts x all months);
* the stats log is opt-in (params dpd_journey.log_stats): it runs extra jobs over the
  whole output.
"""

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import require_columns, string_key

LOG = logging.getLogger(__name__)


def build_rl_full_history(
    rl_spine: DataFrame, int_loan_master: DataFrame, crx_persona: dict
) -> DataFrame:
    """Full monthly history of the run's RL spine.

    Args:
        rl_spine: model-namespaced RL spine (~31k accounts). Column: account_id.
        int_loan_master: monthly snapshots for all RL accounts. Columns: account_id (string),
            observation_date (date), dpd_bucket (int: 0 = 0 DPD, 1 = 1-30, ..., 7 = 180+),
            emi_coverage_ratio, outstanding_balance, is_restructured, loan_type.
        crx_persona: params dict (only dpd_journey.log_stats is read).

    Returns:
        DataFrame at grain (account_id, month_end_date): account_id string, month_end_date
        date, dlq_bucket int, emi_coverage_ratio double, outstanding_balance double,
        restructure_flag int, loan_type string, computed_at timestamp.
    """
    require_columns(rl_spine, ["account_id"], "rl_spine")
    require_columns(
        int_loan_master,
        [
            "account_id",
            "cif_id",
            "observation_date",
            "dpd_bucket",
            "emi_coverage_ratio",
            "outstanding_balance",
            "is_restructured",
            "loan_type",
        ],
        "int_loan_master",
    )
    # -- Step 1: scope to the spine (broadcast: the spine is model-sized) ----------
    spine_keys = rl_spine.select(string_key(rl_spine).alias("account_id")).distinct()
    df = int_loan_master.join(F.broadcast(spine_keys), on="account_id", how="leftsemi")

    # -- Step 2: select + alias + cast to the output schema ----------------------------
    result = df.select(
        F.col("cif_id").cast("string"),
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
    if (crx_persona.get("dpd_journey") or {}).get("log_stats"):
        result = result.persist()
        _log_stats(result, spine_keys)
    return result


def _log_stats(df: DataFrame, spine_keys: DataFrame) -> None:
    r = (
        df.agg(
            F.count("*").alias("rows"),
            F.countDistinct("account_id").alias("accounts"),
            F.min("month_end_date").alias("first_month"),
            F.max("month_end_date").alias("last_month"),
            *[
                F.avg(F.col(c).isNull().cast("double")).alias(f"null_{c}")
                for c in ("dlq_bucket", "month_end_date", "restructure_flag")
            ],
        )
        .first()
        .asDict()
    )
    r["spine_accounts"] = spine_keys.count()
    LOG.info(
        "build_rl_full_history: %s (spine accounts found: %s of %s)",
        r,
        r["accounts"],
        r["spine_accounts"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_full_history/pipeline.py`
action: replace · base sha256 `56ce2a812fdd30bb393b655284c84c85c557d2e6a87714a5b1dfa095789d6b87` · base trailing newline: yes · new sha256 `bbc9963c0b7faad1dba83df34d7c5a08f4f99bfb01ab8d081604d4d54b3c41d6` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-B1 — Full pre-delinquency monthly history."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_full_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [rl_spine, int_loan_master] → crx_rl_full_history.

    int_loan_master provides the full monthly-grain delinquency history. rl_spine
    (model_id-namespaced) scopes scan to target population via leftsemi join. No
    date window applied — full history required for T0 identification (RL-B2) and
    pre-T0 A4 lookback (RL-A4-2).

    Must run after the spine pipeline for the relevant model_id
    (rl_60_180.spine or rl_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_rl_full_history
    """
    return Pipeline(
        [
            node(
                func=build_rl_full_history,
                inputs=["rl_spine", "int_loan_master", "params:crx_persona"],
                outputs="crx_rl_full_history",
                name="build_crx_rl_full_history",
                tags=["crx", "rl", "rl_b1"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: crx_rl_full_history, the monthly DPD history of the RL spine."""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_full_history

TAGS = ["crx_persona", "crx", "full_history"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: [rl_spine, int_loan_master] → crx_rl_full_history.

    int_loan_master provides the monthly delinquency history. rl_spine
    (model_id-namespaced) scopes it to the target population via leftsemi join. No
    date window is applied: the history is used in full.

    Must run after the spine pipeline for the relevant model_id
    (rl_60_180.spine or rl_180_plus.spine).

    Run with:
        kedro run --pipeline=crx_rl_full_history
    """
    return Pipeline(
        [
            node(
                func=build_rl_full_history,
                inputs={
                    "rl_spine": "rl_spine",
                    "int_loan_master": "int_loan_master",
                    "crx_persona": "params:crx_persona",
                },
                outputs="crx_rl_full_history",
                name="build_crx_rl_full_history",
                tags=TAGS,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/scoring_engine.py`
action: replace · base sha256 `b2a6f15da8227b4892e68817c2503d58f629b66ea32e6fd94f168885d1282dd2` · base trailing newline: yes · new sha256 `f175e335a6844f25825a8c30139c0c2ff4dc8b1745f8afd22e0e440985dd901e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared points -> state-ladder scoring primitives for crx_persona axes.

Pulled out after confirming T31's A1 ability v2 (cc_a1_ability_v2) and the
DE's A3 payment-credibility rewrite (cc_a3_payment_credibility) converged
independently on the same shape: N named point dimensions summed to a total,
a priority-ordered override condition that demotes the computed state by
exactly one rung (never stacks), a High/Moderate/Low(/Unknown) ladder, and a
no-signal gate checked first. Verified cell-by-cell against both real
implementations (A1 v2's MECE map and A3's ``_a3_state_col``) before this was
extracted.

Each axis supplies its own dimension logic, state label strings and point
thresholds — this module only owns the combination step. No confidence
scoring lives here; axes that need a confidence column derive it themselves
from the state (as A3 already does).

Pure ``pyspark.sql.Column`` in, ``Column`` out — no DataFrame coupling, so
either axis wires these into its own node without restructuring joins.
"""

from dataclasses import dataclass
from typing import Mapping

from pyspark.sql import Column
from pyspark.sql import functions as F


def points_from_level(level_col: Column, points_by_level: Mapping[str, int]) -> Column:
    """Map a named level string column to its integer point value.

    ``points_by_level`` is an equality lookup, not a ladder — order doesn't
    matter. A level value not present in ``points_by_level`` (including NULL)
    falls through to 0.
    """
    expr = F.lit(0)
    for level, points in points_by_level.items():
        expr = F.when(level_col == F.lit(level), F.lit(points)).otherwise(expr)
    return expr


@dataclass(frozen=True)
class StateLadder:
    """A High/Moderate/Low(/Unknown) points ladder with a one-rung override demotion.

    ``high_from_points`` / ``moderate_from_points`` are inclusive point
    thresholds for the un-demoted ladder. An override (e.g. a distress flag,
    a strong-negative reason) drops the computed level by exactly one rung —
    High -> Moderate, Moderate -> Low — and never pushes below ``low``, the
    ladder's floor. ``unknown`` is a separate gate, not reachable via points;
    the caller decides when it fires (typically "no signal from any
    dimension and no override") and passes that as ``is_unknown``.
    """

    high: str
    moderate: str
    low: str
    unknown: str
    high_from_points: int
    moderate_from_points: int

    def state(
        self, points_total: Column, has_override: Column, is_unknown: Column
    ) -> Column:
        """Combine points, the override boolean and the unknown gate into a state column.

        Unknown is checked first and short-circuits the ladder. Otherwise:
        High requires points >= high_from_points AND no override; Moderate
        fires either on points >= moderate_from_points with no override, or
        on points >= high_from_points WITH an override (the one-rung
        demotion from High); everything else is Low.
        """
        return (
            F.when(is_unknown, F.lit(self.unknown))
            .when(
                (points_total >= self.high_from_points) & (~has_override),
                F.lit(self.high),
            )
            .when(
                ((points_total >= self.moderate_from_points) & (~has_override))
                | ((points_total >= self.high_from_points) & has_override),
                F.lit(self.moderate),
            )
            .otherwise(F.lit(self.low))
        )
`````

New:

`````python
"""Points -> state scoring shared by the axes (A1; A3 next). An axis declares a
``Scorecard`` (dimensions with points per level, thresholds, overrides, state labels)
and builds its own level columns; ``Scorecard.score`` adds points, state, the override
that fired and the reason. Imported by the axes; not run on its own."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

DEMOTE, CAP, FORCE = "demote", "cap", "force"  # Override modes
RUNGS = ("low", "moderate", "high")
LOW, MOD, HIGH = range(len(RUNGS))  # rung indices


@dataclass(frozen=True)
class Dimension:
    """A scored dimension: its ``level`` column, the points per level (others 0; may be
    negative) and the ``silent`` levels that mean "no evidence" (the Unknown gate)."""

    name: str
    level: str
    points: Mapping[str, int]
    silent: tuple[str, ...] = ("none",)


@dataclass(frozen=True)
class Override:
    """A boolean ``flag`` column that, when true, moves the state: ``DEMOTE`` one rung
    (never below Low), ``CAP`` at rung ``to``, or ``FORCE`` to rung ``to``."""

    name: str
    flag: str
    mode: str = DEMOTE
    to: str = "low"


@dataclass(frozen=True)
class Scorecard:  # pylint: disable=too-many-instance-attributes,too-many-locals
    """Points over ``dimensions`` -> High / Moderate / Low, overrides, an Unknown gate.

    Rungs from the points total (``high_from`` / ``moderate_from``, inclusive); High
    also needs ``high_min_dimensions`` dimensions with points, one in ``high_current``
    if given, else Moderate. The first override whose flag is true, in declared order,
    moves the rung (no stacking; a NULL flag does not fire). Unknown: every level silent
    or NULL, no override, and ``unknown_also``. ``labels``: rung or "unknown" -> value.
    """

    prefix: str
    dimensions: tuple[Dimension, ...]
    labels: Mapping[str, str]
    high_from: int
    moderate_from: int
    overrides: tuple[Override, ...] = ()
    high_min_dimensions: int = 0
    high_current: tuple[str, ...] = ()

    def score(self, df: DataFrame, unknown_also: Column | None = None) -> DataFrame:
        """``df`` + ``<prefix>_<dimension>_points``, ``_points_total``, ``_state``,
        ``_override`` (the one that fired), ``_reason`` (it, else the top dimension)."""
        p = self.prefix
        pts = {
            d.name: F.coalesce(state_label(d.level, d.points), F.lit(0))
            for d in self.dimensions
        }
        total = sum(pts.values())
        scored = sum((c > 0).cast("int") for c in pts.values())
        high = (total >= self.high_from) & (scored >= self.high_min_dimensions)
        if self.high_current:
            high &= F.array_max(F.array(*[pts[n] for n in self.high_current])) > 0
        rung = F.when(high, HIGH).when(total >= self.moderate_from, MOD).otherwise(LOW)
        fired = F.coalesce(
            *[F.when(F.col(o.flag), F.lit(o.name)) for o in self.overrides],
            F.lit(None).cast("string"),
        )
        for o in self.overrides:
            to = F.lit(RUNGS.index(o.to))
            moved = {DEMOTE: F.greatest(rung - 1, F.lit(LOW)), CAP: F.least(rung, to)}
            rung = F.when(fired == o.name, {**moved, FORCE: to}[o.mode]).otherwise(rung)
        unknown = F.lit(True) if unknown_also is None else unknown_also
        unknown &= fired.isNull()
        for d in self.dimensions:
            unknown &= F.coalesce(F.col(d.level).isin(*d.silent), F.lit(True))
        state = F.when(unknown, self.labels["unknown"])
        for i in (HIGH, MOD):
            state = state.when(rung == i, self.labels[RUNGS[i]])
        ranked = [
            F.struct(c.alias("pts"), F.lit(-i).alias("i"), F.lit(n).alias("n"))
            for i, (n, c) in enumerate(pts.items())
        ]
        top = F.sort_array(F.array(*ranked), asc=False)[0]  # ties: declared order
        return df.select(
            "*",
            *[c.alias(f"{p}_{n}_points") for n, c in pts.items()],
            total.alias(f"{p}_points_total"),
            state.otherwise(self.labels["low"]).alias(f"{p}_state"),
            fired.alias(f"{p}_override"),
            F.coalesce(fired, F.when(top["pts"] > 0, top["n"])).alias(f"{p}_reason"),
        )


def state_label(col: str, labels: Mapping[str, object]) -> Column:
    """The ``labels`` value of each ``col`` value; NULL for a value ``labels`` lacks."""
    pairs = [F.lit(x) for pair in labels.items() for x in pair]
    return F.create_map(*pairs)[F.col(col)]
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
Clean up after mirror bundle 16_persona_refactor.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id a check ran for (CC datasets for the CC model_ids, RL for RL). Skip folders that do not exist: `crx_<p>_full_history_rf_check`, `crx_<p>_a4_deterioration_rf_check`, `crx_<p>_obs_base_rf_check`, `crx_<p>_a2_locatability_rf_check`, `crx_<p>_a1_ability_rf_check`.
- **Remove the temporary checks** (everything marked TEMPORARY for refactor bundle R-B):
  - `conf/base/catalog/catalog_crx.yml`: the ten `*_rf_check` entries and their comment block;
  - `src/enbd_collections/pipeline_registry.py`: the `rf_check` import with its comment, and the six `crx_<p>_<axis>_rf_check` entries with their comment;
  - delete `src/enbd_collections/pipelines/crx_persona/rf_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "rf_check" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
