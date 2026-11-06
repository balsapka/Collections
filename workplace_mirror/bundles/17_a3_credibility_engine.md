# Mirror bundle 17 — A3 — payment credibility on one engine (decisions D-A3-1..21; both promise judges for comparison)

apply_bundle version: 7 · built 2026-11-06 from `8e57673..d05e763` · source: 7 added, 12 replaced, 4 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/17_a3_credibility_engine.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '17_a3_credibility_engine.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/17_a3_credibility_engine.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **DCORE helpers.** The engine calls `instalment_amount_flags()` (`a3_credibility/signals.py`, on rows with `due_date`, `due_amount`, `payment_amount`, `observation_date`) and `null_cancelled_instalment_fields(df, status)` (`a3_credibility/sources.py`, on rows with those columns and `instalment_status`), as the old A3 did. Confirm from `enbd_collections/nodes/features/dcore/_feat_dcore_utils.py` that they read exactly these column names; if not, adapt the call, not the helper.
2. **Old catalog entries.** Remove from `conf/base/catalog/catalog_crx.yml` the six A3 datasets no pipeline writes any more: `crx_cc_a3_dlq_payment_signals_dpd_bucket_movement`, `crx_cc_a3_dlq_payment_signals_payment_sum_waterfall`, `crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement` and the three `crx_rl_a3_…` twins. Keep `crx_<p>_a3_commitment_signals`, `_strong_negative_signals`, `_dlq_payment_signals_single_payment_cycle_count`, `_pre_dlq_payment_signals_single_payment_cycle_count`, `crx_cc_a3_payment_cycles`, `crx_rl_a3_dlq_cycles` and `crx_<p>_a3_payment_credibility` (the new pipeline writes them). Make sure `crx_<p>_a3_episode`, `crx_<p>_a3_instalments` and the four `crx_<p>_a3_check_*` entries exist exactly once.
3. **Tests.** Delete the tests of the deleted A3 code (`_signals_common`, the per-method builders, `build_a3_payment_credibility`, `_spine_utils.rl_spine_as_cc_shim` callers in A3) and of `build_cc_acct_windows`' old signature. Add tests for the engine only where cheap: the mirror's spec test (`workplace_mirror/checks/a3_engine_spec.py`) has the cases.
4. **Other readers.** `grep -rn` over `src` and `conf` for `REFUSING`, `a3_state_v1`, `a3_strong_negative_reason`, `a3_dlq_payment_evidence_method`, `a3_pre_dlq_payment_evidence_method`, `rl_a3_`. Report every hit outside A3; do not change them.

Then check: `kedro registry list | grep a3` lists `crx_cc_a3_check` and `crx_rl_a3_check`.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A3: payment credibility on one engine" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/17_a3_credibility_engine.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

Bundles 15 and 16 must be applied and their checks back. The A3 output from the last real run is the baseline: do not re-run A3 before the check. Run for **`rl_60_180`**, then **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`). `crx_<p>_obs_base` and `crx_<p>_a4_deterioration` must be current for the model_id (bundle 16 step 11 for 180+).

**Step 7.** Run the check (it reads the current CC raw extracts as they are):

```bash
kedro run --env=dev --pipeline=crx_rl_a3_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back every block from `=== A3 … START ===` to `=== A3 … END ===` (5 per model_id). A summary file is fine.

**Step 8.** Only after the blocks are reviewed and the judge is chosen (`a3_kept_by` in `parameters_crx_persona.yml`): write the real output. CC first rebuilds the raw extracts on the new window:

```bash
kedro run --env=dev --pipeline=crx_cc_raw_extract
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

For every model_id you score (all four). Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Rebuilds A3 payment credibility on one engine (`a3_credibility/`) with thin CC / RL wrappers, the shape of A1, A2 and A4, and applies the A3 decisions (spec `specs/A3_credibility_spec.md`, D-A3-1..21, the council's Q-11..Q-32 answers). It carries **both options for who decides that a promise was kept**, so the check can compare them: `payments` (the money arrived within the grace) and `dcore` (DCORE's paid amount reaches the due). Third of three bundles: apply after 15 and 16.

**What changes in the logic** (business view: the workbook's Changes sheet):
- **No spells, no T0.** Rows are the month-end obs base; every window hangs on the start of the current delinquency episode, read from A4 (`crx_<p>_a3_episode`). Rows A4 does not score are Unknown (`a3_unknown_reason = no_episode`); a censored episode start (A4 cropped the history) counts as unknown: windows from the observation lookback, Dimension C No record (`pre_dlq_reason = censored`).
- **Promises (Dimension A):** PTP + settlement instalments of the scored account (linked through `prm_dcore_account_agreements`), due in the last 12 months of this episode, pending ones not counted. Judge (`params:a3_kept_by`, TEMPORARY): `payments` = payments since the plan start reach the cumulative due by the first statement on or after the due date (CC) / the end of the next month (RL); `dcore` = DCORE's flags. Points Kept 2, Partly kept 1, Thin 0, **Broken −1** (no longer a strong negative).
- **Payments while delinquent (Dimension B):** from the month after the episode month; qualifying = at least one month's due and at least 100 AED; Some = a cycle with 100 AED or more; 61–180 vs 180+ windows by `model_id`.
- **Record before delinquency (Dimension C):** the 12 months before the episode month; paid as billed = paid before the next statement; RL against the last known EMI.
- **Strong negative:** refusal only (refuse to pay, refused to pay, KSA refuse to pay, rewrite not agreed as the latest right-party contact in the episode, with no plan and no cycle / month of 100 AED or more after it; DCORE read at most 24 months back). No response is gone. Diagnostic columns: dispute, hung up, no pickup after a contact.
- **Output:** `a3_state` (was `a3_state_v1`) plus every input (D-A3-17); `a3_confidence`, `a3_provenance`, `computed_at`, the per-method columns and the strong-negative reason column go (`a3_override` / `a3_reason` replace the last).

**Code:** new `a3_credibility/` (constants, sources, signals, classify, pipeline); the wrappers only build dues / payments; `_signals_common.py` and `constants.py` of both A3 packages are deleted; `_dcore_codes.REFUSING` is split into `REFUSAL`, `DISPUTE`, `HUNG_UP`; `cc_raw_extract.build_cc_acct_windows` takes its window from the episode (obs base + A4) instead of the spell table, so CC runs A4 → raw extract → A3. Params: the four `*_evidence_method` keys go, `a3_kept_by` is added. Catalog: `crx_<p>_a3_episode`, `crx_<p>_a3_instalments` added; the waterfall / bucket-movement datasets are no longer written.

**Check** (temporary, `a3_credibility/check.py`, pipelines `crx_<p>_a3_check`): the latest month through the new engine with both judges (into `crx_<p>_a3_check_payments` / `_dcore`; intermediates in memory, nothing real overwritten), against the A3 output persisted before the bundle. Blocks: `A3 OUTPUT` (old × payments, old × dcore, dcore × payments), `A3 COMMITMENTS` (Dimension A level by judge, instalments concluded / kept), `A3 BROKEN` (Broken rows by B + C points; the state with Broken as today's override, 0, −1, −2), `A3 CONTACTS` (refusal, what followed it, the diagnostics, refusal without the 24-month cap, old strong negative × new refusal), `A3 EPISODE` (Unknown reasons, Dimension C reasons, rows cut by the history floor, Dimension B levels).

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
| replace | `src/enbd_collections/pipelines/crx_persona/_dcore_codes.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/_signals_common.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/constants.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/_signals_common.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/constants.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `d433ffc0d5a5db93b3ae82cb008d0b81b583d19a715001922e54bdacace33089` · base trailing newline: yes · new sha256 `ce8dccf20cb2ec66fb7d87f241ca17efe7f546e66e9229838c4bf037dfc64633` · new trailing newline: yes

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

# ── CC A3 Payment Credibility (shared a3_credibility engine) ──────────────────
# Grain: (account_id, observation_date), month ends, persona months (crx_cc_obs_base).
# a3_state ∈ {payment_credibility_high, payment_credibility_moderate,
#             payment_credibility_low, payment_credibility_unknown}.
# crx_cc_a3_episode: the episode anchor from A4; crx_cc_a3_instalments: the DCORE promise
# instalments of the base's accounts. Spec: workplace_mirror/specs/A3_credibility_spec.md.

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

crx_rl_a3_payment_credibility:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

# TEMPORARY (A3 bundle): the new A3 on the latest month, both judges (the A3 check).
# Remove these entries, check.py, the check pipelines and the HDFS folders after the check.
crx_cc_a3_check_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_check_payments"
  save_args:
    mode: overwrite

crx_cc_a3_check_dcore:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_check_dcore"
  save_args:
    mode: overwrite

crx_rl_a3_check_payments:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_check_payments"
  save_args:
    mode: overwrite

crx_rl_a3_check_dcore:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_check_dcore"
  save_args:
    mode: overwrite
`````

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `3704d32b07b9f792842937f2db2c1785e8a4dcbe6308703a2c94a82494cc3c80` · base trailing newline: yes · new sha256 `2ac7620a43b254254948998ee22e49c4f0e448ced21f4da5acbaac8509545023` · new trailing newline: yes

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

# A3 payment credibility - which payment-evidence method SHIPS for each
# dimension. All methods are always computed; this only picks the shipped one.
# The others stay as shadow columns (a3_*_<method>) for cross-checking.

# Dimension B (payments while delinquent). "Some" vs "none" (and the refusal /
# no_response strong negatives) look back 12 months at 180+ DPD (3 months at 61-180);
# "regular" keeps 3 months (61-180) / 6 months (180+). Options for what counts:
#   "single_payment_cycle_count" (default) - counts cycles where ONE payment >= 100%
#                                of that cycle's due_amount_m; 2+ of 3 months
#                                (61-180 DPD) or 3+ of 6 months (180+ DPD) =
#                                regular. A lumpsum counts once.
#   "payment_sum_waterfall"    - old method: payments summed and walked down
#                                the overdue buckets; one lumpsum can clear
#                                several months
#   "dpd_bucket_movement"      - infers it from DPD-bucket improvement between
#                                consecutive billing cycles
a3_dlq_payment_evidence_method: "single_payment_cycle_count"

# Dimension C (payments before delinquency). Options:
#   "single_payment_cycle_count" (default) - counts months where that month's
#                                payment >= 100% of its due amount (no summing
#                                across months, no waterfall)
#   "dpd_bucket_movement"      - infers it from DPD-bucket movement between
#                                consecutive billing cycles
a3_pre_dlq_payment_evidence_method: "single_payment_cycle_count"

# Retail Loans (RL) A3 payment credibility - same idea as the two keys above,
# but separate keys so a CC config change never moves RL. All approaches are
# always computed; these only pick the shipped one.

# RL Dimension B (payments while delinquent). Same windows as CC: "some"/"none" and the
# strong negatives look back 12 months in the 180+ band (3 months otherwise); "regular"
# keeps 3 / 6 months. Options for what counts:
#   "single_payment_cycle_count" (default) - counts months where the month's cash
#                                (total_paid) >= 100% of its EMI; 2+ of 3 months
#                                (61-180 DPD band) or 3+ of 6 months (180+) =
#                                regular. A large payment counts once.
#   "payment_sum_waterfall"    - floor(sum of the window's cash / EMI); one large
#                                payment can credit several months (a division,
#                                RL has no bucket walk)
#   "dpd_bucket_movement"      - infers it from month-over-month bucket movement
rl_a3_dlq_payment_evidence_method: "single_payment_cycle_count"

# RL Dimension C (payments before delinquency). Options:
#   "single_payment_cycle_count" (default) - counts months where the month's cash >= 100%
#                                of its EMI
#   "dpd_bucket_movement"      - month counts as paid when its own month-end bucket
#                                is 0
rl_a3_pre_dlq_payment_evidence_method: "single_payment_cycle_count"

# CC A3 payment credibility - earliest billing date A3 reads (TEMPORARY).
# Billing has no rows 2021-01..2023-12 (balance/transaction: 2019-2021), so history
# before this date is not used by Dimension B or C, and the raw extract gives every
# spine account a window starting here (crx_cc_acct_windows). Set to null once the
# source backfill lands. Separate from A4's dpd_journey.cc_history_floor_date, so
# relaxing A4's floor for the 180+ vintage never moves A3. The spell table and
# crx_cc_full_history are NOT floored (other pipelines read them).
cc_a3_history_floor_date: "2024-01-01"
`````

New:

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

# A3 payment credibility - who decides that a promise instalment was kept (TEMPORARY,
# until the choice is made from the bundle check; then this key and the losing option go):
#   "payments" - the payments since the plan start reach the cumulative due by the grace
#                cutoff (CC: the first statement on or after the due date; RL: the end
#                of the next month)
#   "dcore"    - DCORE's own paid / overdue flags (paid amount >= due amount)
a3_kept_by: "payments"

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
action: replace · base sha256 `019325f81c26e1b090cb161e291597f37814e7076091dec9b8cb804149cfb25c` · base trailing newline: yes · new sha256 `8ff2a70216938240380e5c89ec6fb48d7b33111fb6c09f8ba51bb5025a0ff7c1` · new trailing newline: yes

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
        # TEMPORARY (A3 bundle): the A3 check; removed by the bundle's cleanup.
        "crx_cc_a3_check": crx_cc_a3_payment_credibility.create_check_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (A3 bundle): the A3 check; removed by the bundle's cleanup.
        "crx_rl_a3_check": crx_rl_a3_payment_credibility.create_check_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/_dcore_codes.py`
action: replace · base sha256 `4499439767b39f43aaf39b6b435ee45512f614ddfc4ddd1b90cad0bde0c9dfdc` · base trailing newline: yes · new sha256 `368535c2a2589af988f18e163af1d0177cb41f7c2b75b521696297d759898e02` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""DCORE follow-up vocabulary (``dcore_prm_followup_outcomes``) shared by A2 and A3.

Single source of truth for call action codes and result-name sets. A2 (reachability,
deceased) and A3 (payment credibility) import from here and never from each other.
Result names are compared upper-cased and trimmed. The departure notes (location
evidence) live in the location feature.

The A2 ``FAILED_CALL`` and A3 ``NOT_REACHABLE`` / ``RINGING`` sets overlap only partly:
they are different classifications, not copies.
"""

OUTBOUND_CODES = ("OC", "CB")  # outbound call, callback: we called
INBOUND_CODES = ("IC",)  # the customer called us
CALL_CODES = (*OUTBOUND_CODES, *INBOUND_CODES)  # IA administrative notes never count
SUCCESS_CATEGORY = "SUC"

# The account holder was reached personally (any call code, any category).
RIGHT_PARTY_CONTACT = frozenset(
    {
        "ACCOUNT PAID",
        "APPRECIATIONS",
        "BALCON WOP 12 MONTHS",
        "BALCON WOP 24 MONTHS",
        "BALCON WP 12 MONTHS",
        "BALCON WP 24 MONTHS",
        "BALCON WP 48 MONTHS",
        "CHANGE OF EMPLOYER",
        "CLAIMS MADE PAYMENT",
        "CODE25 WILL PAY AT SALARY",
        "CUSTOMER BEHAVIOUR GREEN",
        "CUSTOMER BEHAVIOUR ORANGE",
        "CUSTOMER BEHAVIOUR RED",
        "CUSTOMER BEHAVIOUR YELLOW",
        "CUSTOMER HAVE NO JOB",
        "CUSTOMER HUNG UP",
        "CUSTOMER IS PERMANENT DISABLED",
        "CUSTOMER KEPT PROMISE MADE",
        "CUSTOMER MADE PAYMENT",
        "CUSTOMER MISBEHAVED",
        "CUSTOMER TERMINATED",
        "CUSTOMER WANTS SETTLEMENT",
        "CUSTOMER WILL VISIT US",
        "CUSTOMER_HUNG_UP",
        "DEBT COUNSELLING",
        "DEFERMENT FOR IMPACTED CUSTOMERS",
        "DEMAND FOR HUMAN AGENT",
        "DIGITAL COLLECT  PTP SUBSCRIBED",
        "DISPUTE",
        "E MAIL RECEIVED",
        "EPP REQUEST",
        "EXPECTING EOSB",
        "FIELD VISIT DONE",
        "FIELD VISIT REJECTED",
        "JOB LOST",
        "KSA/CALLBACK",
        "KSA/CONNECT AND DROP",
        "KSA/CUSTOMER WILL PAY AT SALARY",
        "KSA/CUSTOMER WILL SEND EMAIL",
        "KSA/CUSTOMER WILL VISIT US",
        "KSA/DISPUTE",
        "KSA/EARLY/FINAL SETTLEMENT",
        "KSA/EOSB",
        "KSA/JOB LOST",
        "KSA/NEED DEFERMENT",
        "KSA/PAID AMOUNT",
        "KSA/PARTIAL PAYMENT",
        "KSA/PROMISE TO PAY",
        "KSA/REFUSE TO PAY",
        "KSA/RESCHEDULING REQUEST",
        "MEDICAL ISSUES",
        "MEMBER ON LEAVE/VACATION",
        "NEED BALCON",
        "NEED DEFERMENT",
        "NEED RESTRUCTURE",
        "NEW SECURITY CHEQUE COLLECTED",
        "NIL SALARY",
        "NO NEED DEFERMENT",
        "PARTIALLY PAID",
        "POST DATED CHEQUE AVAILABLE",
        "POST DATED COLLECTED",
        "PROMISE TO PAY",
        "PROMISE TO PAY PARTIALLY",
        "PROMISE TO PAY SCHEDULED",
        "RECEIVED EOSB",
        "REFUSE TO PAY",
        "REFUSED TO PAY",
        "REQUEST FOR DUE DATE CHANGE",
        "REQUEST FOR FUNDING ACCOUNT CHANGE",
        "REQUEST FOR LIEN REMOVAL",
        "REQUEST FOR PAYMENT MODE CHANGE",
        "REQUEST TO PRESENT SECURITY CHEQUE",
        "REQUESTED FOR FD LIQUIDATION",
        "RESTRUCTURE NOT REQUIRED",
        "RESTRUCTURE REQUIRED",
        "REWRITE AGREED",
        "REWRITE NOT AGREED",
        "SALARY DELAY",
        "SALARY REDUCTION",
        "SETTLEMENT",
        "SOFTPTP",
        "UNPAID LEAVE",
        "WILL PAY AT SALARY",
    }
)

# A failed outbound call: it rang out or nobody answered (a message left included), or the
# line is dead / the number invalid. CALL CONNECTED without SUC and any other outcome
# (e.g. LINE BUSY) is a neutral attempt: neither failed nor a contact.
FAILED_CALL = frozenset(
    {
        # rang out, no answer
        "RINGING NO REPLY",
        "RINGING NO RESPONSE",
        "NO ANSWER",
        "LEFT_MSG",
        # dead line, invalid number
        "CUSTOMER NOT CONTACTABLE",
        "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
        "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
        "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
        "ININ-OUTBOUND-SIT-UNCALLABLE",
        "KSA/MOBILE SWITCHED OFF",
        "KSA/OUT OF SERVICE",
        "KSA/UNCONTACTABLE",
        "KSA/WRONG NUMBER",
        "LINE DISCONNECTED",
        "MOBILE SWICTHED OFF",
        "MOBILE SWITCHED OFF",
        "NOT REACHABLE",
        "OUTBOUND-INVALID-PHONE-NUMBER",
        "PHONE OUT OF SERVICE",
        "UNCONTACTABLE",
        "WRONG NO",
        "WRONG NUMBER",
    }
)

# Collector skip-trace statuses: a diagnostic column, not location or reachability evidence.
SKIP_TRACE = frozenset({"SKIP - UNDER TRACING", "SKIP - TRACED"})

# Dropped before any reachability rule: administrative entries, RL legal / repossession
# routing (plus every "RPO CASE …" name) and the skip-trace statuses.
IGNORED = frozenset(
    {
        "RESULT NOT FOUND",
        "FOLLOW UP",
        "E MAIL SENT",
        "LEGAL NOTICE SENT",
        "VEHICLE REPOSSESED/UNDER AUCTION",
        *SKIP_TRACE,
    }
)
IGNORED_PREFIX = "RPO CASE"

# Confirmed or claimed (a relative's claim counts until disproved).
DECEASED = frozenset(
    {
        "DECEASED",
        "DECEASED CLAIMED",
        "DECEASED OR EXPIRED",
        "DECEASED/EXPIRED",
        "KSA/DECEASED",
    }
)

# Explicit refusal signals – result names where confirmed right-party contact was
# made but the customer explicitly refused, hung up, or disputed.
# Subset of RIGHT_PARTY_CONTACT (every entry here also confirms contact).
# Excludes settlement-seeking behaviour (engagement) and autodialler intermediates.
#
# Drives refusing_n counter → non_cooperative state (confirmed contact + refusal).
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(REFUSING)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
REFUSING = {
    "CUSTOMER HUNG UP",
    "CUSTOMER MISBEHAVED",
    "CUSTOMER_HUNG_UP",
    "DISPUTE",
    "KSA/DISPUTE",
    "KSA/REFUSE TO PAY",
    "REFUSE TO PAY",
    "REFUSED TO PAY",
    "REWRITE NOT AGREED",
}

# Ringing no-answer signals – phone rang at the customer end but was not answered.
# Excludes LINE BUSY (transient, does not indicate call screening).
# Drives ringing_n counter → avoiding state when ≥3 ringing events and line is live.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RINGING = {
    "RINGING NO REPLY",
    "RINGING NO RESPONSE",
}

# Promise to pay or willingness to pay – result names signalling the customer
# has committed to pay, made a payment arrangement, or actually paid.
# Covers: all PTP-category outcomes, actual payments (SUC), and INT entries
# where the customer verbally committed or agreed to a specific arrangement
# (balance consolidation, rewrite, deferment, settlement, salary-date promise).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PROMISE_TO_PAY = {
    "ACCOUNT PAID",
    "BALCON WOP 12 MONTHS",
    "BALCON WOP 24 MONTHS",
    "BALCON WP 12 MONTHS",
    "BALCON WP 24 MONTHS",
    "BALCON WP 48 MONTHS",
    "CLAIMS MADE PAYMENT",
    "CODE25 WILL PAY AT SALARY",
    "CUSTOMER KEPT PROMISE MADE",
    "CUSTOMER MADE PAYMENT",
    "DEFERMENT FOR IMPACTED CUSTOMERS",
    "DIGITAL COLLECT  PTP SUBSCRIBED",
    "HISTORICAL PROMISE TO PAY",
    "KSA/CUSTOMER WILL PAY AT SALARY",
    "KSA/EARLY/FINAL SETTLEMENT",
    "KSA/PAID AMOUNT",
    "KSA/PARTIAL PAYMENT",
    "KSA/PROMISE TO PAY",
    "PARTIALLY PAID",
    "PROMISE TO PAY",
    "PROMISE TO PAY PARTIALLY",
    "PROMISE TO PAY SCHEDULED",
    "REWRITE AGREED",
    "SETTLEMENT",
    "SOFTPTP",
    "WILL PAY AT SALARY",
}

# Customer is fundamentally unreachable – wrong/invalid number, line
# permanently dead/disconnected, or explicitly flagged uncontactable.
# Signals a structural contact barrier, not a single failed attempt.
# Excludes: transient failures (no answer, busy, disconnected call,
# voicemail, message left) – those only mean the customer didn't pick up
# this time, not that they are unreachable.
# Covers both autodialler (ININ-OUTBOUND-*) and manual/KSA-channel outcomes.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
NOT_REACHABLE = {
    "CUSTOMER NOT CONTACTABLE",
    "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
    "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
    "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
    "ININ-OUTBOUND-SIT-UNCALLABLE",
    "KSA/MOBILE SWITCHED OFF",
    "KSA/OUT OF SERVICE",
    "KSA/UNCONTACTABLE",
    "KSA/WRONG NUMBER",
    "LINE DISCONNECTED",
    "MOBILE SWICTHED OFF",
    "MOBILE SWITCHED OFF",
    "NOT REACHABLE",
    "OUTBOUND-INVALID-PHONE-NUMBER",
    "PHONE OUT OF SERVICE",
    "UNCONTACTABLE",
    "WRONG NO",
    "WRONG NUMBER",
}

# Customer honoured or is actively maintaining an existing promise-to-pay – a
# stronger/narrower signal than generic PROMISE_TO_PAY. Not restricted to
# a particular action_code: in practice RETAIN PTP is logged administratively (action_code
# IA) rather than against a live call, so consumers must not pre-filter to call-type
# action codes before matching this set.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RETAIN_PTP = {
    "CUSTOMER KEPT PROMISE MADE",
    "RETAIN PTP",
}

# Confirmed completed payment – distinct from a promise/commitment (PROMISE_TO_PAY) or
# an unverified claim of payment ("CLAIMS MADE PAYMENT", which stays PTP-classified).
# Drives a dedicated "paid" disposition, separate from PTP.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PAYMENT_CONFIRMED = {
    "ACCOUNT PAID",
    "CUSTOMER MADE PAYMENT",
}
`````

New:

`````python
"""DCORE follow-up vocabulary (``dcore_prm_followup_outcomes``) shared by A2 and A3.

Single source of truth for call action codes and result-name sets. A2 (reachability,
deceased) and A3 (payment credibility) import from here and never from each other.
Result names are compared upper-cased and trimmed. The departure notes (location
evidence) live in the location feature.

The A2 ``FAILED_CALL`` and A3 ``NOT_REACHABLE`` / ``RINGING`` sets overlap only partly:
they are different classifications, not copies.
"""

OUTBOUND_CODES = ("OC", "CB")  # outbound call, callback: we called
INBOUND_CODES = ("IC",)  # the customer called us
CALL_CODES = (*OUTBOUND_CODES, *INBOUND_CODES)  # IA administrative notes never count
SUCCESS_CATEGORY = "SUC"

# The account holder was reached personally (any call code, any category).
RIGHT_PARTY_CONTACT = frozenset(
    {
        "ACCOUNT PAID",
        "APPRECIATIONS",
        "BALCON WOP 12 MONTHS",
        "BALCON WOP 24 MONTHS",
        "BALCON WP 12 MONTHS",
        "BALCON WP 24 MONTHS",
        "BALCON WP 48 MONTHS",
        "CHANGE OF EMPLOYER",
        "CLAIMS MADE PAYMENT",
        "CODE25 WILL PAY AT SALARY",
        "CUSTOMER BEHAVIOUR GREEN",
        "CUSTOMER BEHAVIOUR ORANGE",
        "CUSTOMER BEHAVIOUR RED",
        "CUSTOMER BEHAVIOUR YELLOW",
        "CUSTOMER HAVE NO JOB",
        "CUSTOMER HUNG UP",
        "CUSTOMER IS PERMANENT DISABLED",
        "CUSTOMER KEPT PROMISE MADE",
        "CUSTOMER MADE PAYMENT",
        "CUSTOMER MISBEHAVED",
        "CUSTOMER TERMINATED",
        "CUSTOMER WANTS SETTLEMENT",
        "CUSTOMER WILL VISIT US",
        "CUSTOMER_HUNG_UP",
        "DEBT COUNSELLING",
        "DEFERMENT FOR IMPACTED CUSTOMERS",
        "DEMAND FOR HUMAN AGENT",
        "DIGITAL COLLECT  PTP SUBSCRIBED",
        "DISPUTE",
        "E MAIL RECEIVED",
        "EPP REQUEST",
        "EXPECTING EOSB",
        "FIELD VISIT DONE",
        "FIELD VISIT REJECTED",
        "JOB LOST",
        "KSA/CALLBACK",
        "KSA/CONNECT AND DROP",
        "KSA/CUSTOMER WILL PAY AT SALARY",
        "KSA/CUSTOMER WILL SEND EMAIL",
        "KSA/CUSTOMER WILL VISIT US",
        "KSA/DISPUTE",
        "KSA/EARLY/FINAL SETTLEMENT",
        "KSA/EOSB",
        "KSA/JOB LOST",
        "KSA/NEED DEFERMENT",
        "KSA/PAID AMOUNT",
        "KSA/PARTIAL PAYMENT",
        "KSA/PROMISE TO PAY",
        "KSA/REFUSE TO PAY",
        "KSA/RESCHEDULING REQUEST",
        "MEDICAL ISSUES",
        "MEMBER ON LEAVE/VACATION",
        "NEED BALCON",
        "NEED DEFERMENT",
        "NEED RESTRUCTURE",
        "NEW SECURITY CHEQUE COLLECTED",
        "NIL SALARY",
        "NO NEED DEFERMENT",
        "PARTIALLY PAID",
        "POST DATED CHEQUE AVAILABLE",
        "POST DATED COLLECTED",
        "PROMISE TO PAY",
        "PROMISE TO PAY PARTIALLY",
        "PROMISE TO PAY SCHEDULED",
        "RECEIVED EOSB",
        "REFUSE TO PAY",
        "REFUSED TO PAY",
        "REQUEST FOR DUE DATE CHANGE",
        "REQUEST FOR FUNDING ACCOUNT CHANGE",
        "REQUEST FOR LIEN REMOVAL",
        "REQUEST FOR PAYMENT MODE CHANGE",
        "REQUEST TO PRESENT SECURITY CHEQUE",
        "REQUESTED FOR FD LIQUIDATION",
        "RESTRUCTURE NOT REQUIRED",
        "RESTRUCTURE REQUIRED",
        "REWRITE AGREED",
        "REWRITE NOT AGREED",
        "SALARY DELAY",
        "SALARY REDUCTION",
        "SETTLEMENT",
        "SOFTPTP",
        "UNPAID LEAVE",
        "WILL PAY AT SALARY",
    }
)

# A failed outbound call: it rang out or nobody answered (a message left included), or the
# line is dead / the number invalid. CALL CONNECTED without SUC and any other outcome
# (e.g. LINE BUSY) is a neutral attempt: neither failed nor a contact.
FAILED_CALL = frozenset(
    {
        # rang out, no answer
        "RINGING NO REPLY",
        "RINGING NO RESPONSE",
        "NO ANSWER",
        "LEFT_MSG",
        # dead line, invalid number
        "CUSTOMER NOT CONTACTABLE",
        "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
        "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
        "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
        "ININ-OUTBOUND-SIT-UNCALLABLE",
        "KSA/MOBILE SWITCHED OFF",
        "KSA/OUT OF SERVICE",
        "KSA/UNCONTACTABLE",
        "KSA/WRONG NUMBER",
        "LINE DISCONNECTED",
        "MOBILE SWICTHED OFF",
        "MOBILE SWITCHED OFF",
        "NOT REACHABLE",
        "OUTBOUND-INVALID-PHONE-NUMBER",
        "PHONE OUT OF SERVICE",
        "UNCONTACTABLE",
        "WRONG NO",
        "WRONG NUMBER",
    }
)

# Collector skip-trace statuses: a diagnostic column, not location or reachability evidence.
SKIP_TRACE = frozenset({"SKIP - UNDER TRACING", "SKIP - TRACED"})

# Dropped before any reachability rule: administrative entries, RL legal / repossession
# routing (plus every "RPO CASE …" name) and the skip-trace statuses.
IGNORED = frozenset(
    {
        "RESULT NOT FOUND",
        "FOLLOW UP",
        "E MAIL SENT",
        "LEGAL NOTICE SENT",
        "VEHICLE REPOSSESED/UNDER AUCTION",
        *SKIP_TRACE,
    }
)
IGNORED_PREFIX = "RPO CASE"

# Confirmed or claimed (a relative's claim counts until disproved).
DECEASED = frozenset(
    {
        "DECEASED",
        "DECEASED CLAIMED",
        "DECEASED OR EXPIRED",
        "DECEASED/EXPIRED",
        "KSA/DECEASED",
    }
)

# A3 (D-A3-20): explicit refusal, the stated-intent negative. Every name below also
# confirms right-party contact (RIGHT_PARTY_CONTACT). Values upper-cased and trimmed.
REFUSAL = {
    "KSA/REFUSE TO PAY",
    "REFUSE TO PAY",
    "REFUSED TO PAY",
    "REWRITE NOT AGREED",
}

# A3 diagnostic column only: a contested debt is not unwillingness to pay.
DISPUTE = {
    "DISPUTE",
    "KSA/DISPUTE",
}

# A3 avoidance diagnostic (D-A3-19): hang-up as the latest right-party contact.
HUNG_UP = {
    "CUSTOMER HUNG UP",
    "CUSTOMER_HUNG_UP",
}

# Ringing no-answer signals – phone rang at the customer end but was not answered.
# Excludes LINE BUSY (transient, does not indicate call screening).
# Drives ringing_n counter → avoiding state when ≥3 ringing events and line is live.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RINGING = {
    "RINGING NO REPLY",
    "RINGING NO RESPONSE",
}

# Promise to pay or willingness to pay – result names signalling the customer
# has committed to pay, made a payment arrangement, or actually paid.
# Covers: all PTP-category outcomes, actual payments (SUC), and INT entries
# where the customer verbally committed or agreed to a specific arrangement
# (balance consolidation, rewrite, deferment, settlement, salary-date promise).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PROMISE_TO_PAY = {
    "ACCOUNT PAID",
    "BALCON WOP 12 MONTHS",
    "BALCON WOP 24 MONTHS",
    "BALCON WP 12 MONTHS",
    "BALCON WP 24 MONTHS",
    "BALCON WP 48 MONTHS",
    "CLAIMS MADE PAYMENT",
    "CODE25 WILL PAY AT SALARY",
    "CUSTOMER KEPT PROMISE MADE",
    "CUSTOMER MADE PAYMENT",
    "DEFERMENT FOR IMPACTED CUSTOMERS",
    "DIGITAL COLLECT  PTP SUBSCRIBED",
    "HISTORICAL PROMISE TO PAY",
    "KSA/CUSTOMER WILL PAY AT SALARY",
    "KSA/EARLY/FINAL SETTLEMENT",
    "KSA/PAID AMOUNT",
    "KSA/PARTIAL PAYMENT",
    "KSA/PROMISE TO PAY",
    "PARTIALLY PAID",
    "PROMISE TO PAY",
    "PROMISE TO PAY PARTIALLY",
    "PROMISE TO PAY SCHEDULED",
    "REWRITE AGREED",
    "SETTLEMENT",
    "SOFTPTP",
    "WILL PAY AT SALARY",
}

# Customer is fundamentally unreachable – wrong/invalid number, line
# permanently dead/disconnected, or explicitly flagged uncontactable.
# Signals a structural contact barrier, not a single failed attempt.
# Excludes: transient failures (no answer, busy, disconnected call,
# voicemail, message left) – those only mean the customer didn't pick up
# this time, not that they are unreachable.
# Covers both autodialler (ININ-OUTBOUND-*) and manual/KSA-channel outcomes.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
NOT_REACHABLE = {
    "CUSTOMER NOT CONTACTABLE",
    "ININ-OUTBOUND-INVALID-PHONE-NUMBER",
    "ININ-OUTBOUND-NUMBER_COULD_NOT_BE_DIALED",
    "ININ-OUTBOUND-ON-DO-NOT-CALL-LIST",
    "ININ-OUTBOUND-SIT-UNCALLABLE",
    "KSA/MOBILE SWITCHED OFF",
    "KSA/OUT OF SERVICE",
    "KSA/UNCONTACTABLE",
    "KSA/WRONG NUMBER",
    "LINE DISCONNECTED",
    "MOBILE SWICTHED OFF",
    "MOBILE SWITCHED OFF",
    "NOT REACHABLE",
    "OUTBOUND-INVALID-PHONE-NUMBER",
    "PHONE OUT OF SERVICE",
    "UNCONTACTABLE",
    "WRONG NO",
    "WRONG NUMBER",
}

# Customer honoured or is actively maintaining an existing promise-to-pay – a
# stronger/narrower signal than generic PROMISE_TO_PAY. Not restricted to
# a particular action_code: in practice RETAIN PTP is logged administratively (action_code
# IA) rather than against a live call, so consumers must not pre-filter to call-type
# action codes before matching this set.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
RETAIN_PTP = {
    "CUSTOMER KEPT PROMISE MADE",
    "RETAIN PTP",
}

# Confirmed completed payment – distinct from a promise/commitment (PROMISE_TO_PAY) or
# an unverified claim of payment ("CLAIMS MADE PAYMENT", which stays PTP-classified).
# Drives a dedicated "paid" disposition, separate from PTP.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PAYMENT_CONFIRMED = {
    "ACCOUNT PAID",
    "CUSTOMER MADE PAYMENT",
}
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py`
action: add · new sha256 `c9cbc47de883cf9d1e10b33199812d05dfc0082e0e209aba4894d5cf855a1b35` · new trailing newline: yes

New:

`````python
"""A3 payment credibility engine shared by the CC and RL credibility pipelines."""

from .classify import build_a3_credibility
from .pipeline import create_a3_pipeline
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import build_a3_episode, build_cycle_ledger, build_instalments
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py`
action: add · new sha256 `9ea7c4c22ea3c1dd41508197e2a84759c3c365fa8a61dbba14e1cd36980789f3` · new trailing newline: yes

New:

`````python
"""TEMPORARY (A3 bundle): the new A3 on the latest month, with both Dimension A judges,
against the A3 output persisted before the bundle. Logs ``A3 OUTPUT``, ``A3 COMMITMENTS``,
``A3 BROKEN``, ``A3 CONTACTS``, ``A3 EPISODE``. Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals,too-many-statements

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals, build_contact_signals
from .constants import GRACE

logger = logging.getLogger(__name__)
NS = "a3_check"


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The base rows of persona_end_date's month."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _state(
    points_a: Column,
    points_bc: Column,
    refusal: Column,
    override: Column,
    unknown: Column,
) -> Column:
    """The A3 ladder for a what-if of the Broken weight."""
    pts = points_a + points_bc
    demote = refusal | override
    rung = (
        F.when(pts >= 4, F.when(demote, "moderate").otherwise("high"))
        .when((pts >= 1) & ~demote, "moderate")
        .otherwise("low")
    )
    return F.when(unknown, "unknown").otherwise(rung)


def compare_a3(
    old: DataFrame,
    pay: DataFrame,
    dcore: DataFrame,
    uncapped: DataFrame,
    model_id: str,
    persona_end_date: str,
    floor: str | None,
) -> None:
    """The check blocks (latest month)."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    old_m = old.filter(F.trunc("observation_date", "month") == month)
    keep = ["a3_state_v1", "a3_commitments_level", "a3_strong_negative_reason"]
    old_m = old_m.select(
        "account_id", "observation_date", *[c for c in keep if c in old_m.columns]
    )
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    old_m = (
        old_m.withColumn("_r", newest).where("_r = 1").drop("_r", "observation_date")
    )
    n = pay.count()
    p, d = pay.alias("p"), dcore.alias("d")
    both = p.join(d, "account_id").join(old_m.alias("o"), "account_id", "left")
    head = [
        f"model_id: {model_id}",
        f"rows new: {n}, old (latest per account): {old_m.count()}",
    ]

    lines = head + ["old a3_state_v1 x new (payments):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("p.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["old x new (dcore):"]
    lines += _counts(
        both.select(
            F.col("o.a3_state_v1").alias("old"), F.col("d.a3_state").alias("new")
        ),
        ["old", "new"],
        n,
    )
    lines += ["new dcore x new payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_state").alias("dcore"), F.col("p.a3_state").alias("payments")
        ),
        ["dcore", "payments"],
        n,
    )
    _block("A3 OUTPUT", lines)

    lines = head + ["Dimension A level, dcore x payments:"]
    lines += _counts(
        both.select(
            F.col("d.a3_commitments_level").alias("dcore"),
            F.col("p.a3_commitments_level").alias("payments"),
        ),
        ["dcore", "payments"],
        n,
    )
    s = both.agg(
        *[
            F.sum(f"{j}.{c}").alias(f"{j}_{c}")
            for j in ("d", "p")
            for c in ("commitments_concluded", "commitments_kept")
        ]
    ).first()
    lines += [
        f"instalments concluded / kept: dcore {s['d_commitments_concluded']} / "
        f"{s['d_commitments_kept']}, payments {s['p_commitments_concluded']} / "
        f"{s['p_commitments_kept']}"
    ]
    if "a3_commitments_level" in old_m.columns:
        lines += ["old level x new (payments):"]
        lines += _counts(
            both.select(
                F.col("o.a3_commitments_level").alias("old"),
                F.col("p.a3_commitments_level").alias("new"),
            ),
            ["old", "new"],
            n,
        )
    _block("A3 COMMITMENTS", lines)

    lines = list(head)
    for j, frame in (("payments", pay), ("dcore", dcore)):
        lvl = F.col("a3_commitments_level")
        pa = F.when(lvl == "kept", 2).when(lvl == "partly_kept", 1).otherwise(0)
        bc = F.col("a3_dlq_payments_points") + F.col("a3_pre_dlq_record_points")
        broken = lvl == "broken"
        unknown = F.col("a3_state") == "payment_credibility_unknown"
        f = frame.select(
            broken.alias("broken"),
            bc.alias("bc"),
            _state(pa, bc, F.col("a3_refusal_flag"), broken, unknown).alias(
                "v0_override"
            ),
            _state(pa, bc, F.col("a3_refusal_flag"), F.lit(False), unknown).alias(
                "v1_zero"
            ),
            _state(
                pa - broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v2_minus1"),
            _state(
                pa - 2 * broken.cast("int"),
                bc,
                F.col("a3_refusal_flag"),
                F.lit(False),
                unknown,
            ).alias("v3_minus2"),
        )
        lines += [f"[{j}] Broken rows by B + C points:"]
        lines += _counts(f.where("broken"), ["bc"], n)
        for v in ("v0_override", "v1_zero", "v2_minus1", "v3_minus2"):
            lines += [f"[{j}] state {v}:"] + _counts(f, [v], n)
    _block("A3 BROKEN", lines)

    u = uncapped.select("account_id", F.col("a3_refusal_flag").alias("uncapped"))
    c = pay.join(u, "account_id", "left")
    lines = head + [
        f"{col}: {c.where(F.col(col)).count()}"
        for col in (
            "a3_refusal_flag",
            "refusal_followed_by_plan",
            "refusal_followed_by_payment",
            "a3_dispute_flag",
            "a3_hung_up_last",
            "a3_no_pickup_after_contact",
        )
    ]
    lines += [
        f"refusal without the 24-month cap: {c.where(F.col('uncapped')).count()}",
        "last right-party disposition:",
    ]
    lines += _counts(pay, ["last_rpc_disposition"], n)
    if "a3_strong_negative_reason" in old_m.columns:
        lines += ["old strong negative x new refusal:"]
        lines += _counts(
            both.select(
                F.col("o.a3_strong_negative_reason").alias("old"),
                F.col("p.a3_refusal_flag").alias("refusal"),
            ),
            ["old", "refusal"],
            n,
        )
    _block("A3 CONTACTS", lines)

    lines = head + ["unknown reason:"] + _counts(pay, ["a3_unknown_reason"], n)
    lines += ["Dimension C reason x level:"]
    lines += _counts(pay, ["pre_dlq_reason", "a3_pre_dlq_payment_level"], n)
    if floor:
        cut = pay.where(
            (F.col("pre_dlq_window_start") < F.lit(floor).cast("date"))
            & (F.col("a3_pre_dlq_payment_level") == "no_record")
            & F.col("pre_dlq_reason").isNull()
        )
        lines += [
            f"no record with the window starting before the floor {floor}: {cut.count()}"
        ]
    lines += ["Dimension B level:"] + _counts(pay, ["a3_dlq_payment_level"], n)
    _block("A3 EPISODE", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): payments judge, DCORE judge and uncapped contacts, then the blocks.
    """
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    base = create_a3_pipeline(
        product, f"{p}_check_payments", dues, payments, kept_by="payments"
    )
    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: f"{NS}.obs_latest"},
        outputs={f"{p}_check_payments": f"{p}_check_payments"},
        parameters=params,
    )

    def ns(name: str) -> str:
        return f"{NS}.{name}"

    signals = {
        "episode": ns(f"{p}_episode"),
        "instalments": ns(f"{p}_instalments"),
        "payments": ns(f"{p}_payments"),
        "dues": ns(f"{p}_dues"),
    }
    extra = [
        node(
            func=latest_month,
            inputs={
                "obs_base": obs,
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=ns("obs_latest"),
            name=f"{p}_check_latest",
            tags=TAGS,
        ),
        node(
            func=partial(
                build_commitment_signals, kept_by="dcore", grace=GRACE[product]
            ),
            inputs=signals,
            outputs=ns("commitments_dcore"),
            name=f"{p}_check_commitments_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_a3_credibility, kept_by="dcore"),
            inputs={
                "episode": signals["episode"],
                "commitments": ns("commitments_dcore"),
                "dlq_payments": ns(
                    f"{p}_dlq_payment_signals_single_payment_cycle_count"
                ),
                "pre_dlq": ns(
                    f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                ),
                "contacts": ns(f"{p}_strong_negative_signals"),
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=f"{p}_check_dcore",
            name=f"{p}_check_state_dcore",
            tags=TAGS,
        ),
        node(
            func=partial(build_contact_signals, max_months=None),
            inputs={
                "episode": signals["episode"],
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": signals["instalments"],
                "payments": signals["payments"],
                "dues": signals["dues"],
                "model_id": "params:model_id",
            },
            outputs=ns("contacts_uncapped"),
            name=f"{p}_check_contacts_uncapped",
            tags=TAGS,
        ),
        node(
            func=partial(compare_a3, floor=None) if product == "rl" else compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "pay": f"{p}_check_payments",
                "dcore": f"{p}_check_dcore",
                "uncapped": ns("contacts_uncapped"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
                **(
                    {}
                    if product == "rl"
                    else {"floor": "params:cc_a3_history_floor_date"}
                ),
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py`
action: add · new sha256 `f48284511fe0b206552ad116dd0c6f40a61aac887dfd7b3dcb16fc463bdff197` · new trailing newline: yes

New:

`````python
"""The A3 state: points over the three dimensions, the refusal override, Unknown."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month
from .constants import DISPLAY_NAMES, SCORECARD

# Every input of the decision is carried (D-A3-17).
OUTPUT_COLUMNS = [
    *GRAIN,
    "cif_id",
    "episode_start",
    "episode_left_censored",
    "a3_kept_by",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_kept_rate",
    "commitments_last_broken_n",
    "a3_commitments_level",
    # Dimension B
    "dlq_payment_window_start",
    "dlq_payment_qualifying_month_cnt",
    "dlq_payment_any_flag",
    "a3_dlq_payment_level",
    # Dimension C
    "pre_dlq_window_start",
    "pre_dlq_months_due_n",
    "pre_dlq_months_paid_as_billed_n",
    "pre_dlq_paid_as_billed_share",
    "a3_pre_dlq_payment_level",
    "pre_dlq_reason",
    # contacts
    "last_rpc_date",
    "last_rpc_disposition",
    "contact_dates_n",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
    "no_pickup_days_n",
    "a3_no_pickup_after_contact",
    # state
    "a3_commitments_points",
    "a3_dlq_payments_points",
    "a3_pre_dlq_record_points",
    "a3_points_total",
    "a3_state",
    "a3_override",
    "a3_reason",
    "a3_unknown_reason",
]


def build_a3_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    episode: DataFrame,
    commitments: DataFrame,
    dlq_payments: DataFrame,
    pre_dlq: DataFrame,
    contacts: DataFrame,
    kept_by: str,
    persona_end_date: str,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20).

    High from 4 points, Moderate from 1, else Low; a refusal takes one rung off. Unknown:
    no evidence in any dimension and no refusal, or no episode anchor (Q-12,
    ``a3_unknown_reason``).
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn("a3_kept_by", F.lit(kept_by))
    scored = SCORECARD.score(df)
    no_episode = F.col("episode_start").isNull()
    unknown = DISPLAY_NAMES["unknown"]
    out = scored.withColumn(
        "a3_unknown_reason",
        F.when(no_episode, "no_episode").when(
            F.col("a3_state") == unknown, "no_evidence"
        ),
    ).withColumn("a3_state", F.when(no_episode, unknown).otherwise(F.col("a3_state")))
    out = out.select(*OUTPUT_COLUMNS)
    log_latest_month(out, "a3_state", "A3 credibility", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py`
action: add · new sha256 `1f83f2a0470fdb796e306980014a6bc4f5eca01f223104ff590b9686ebaff078` · new trailing newline: yes

New:

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_180_PLUS, SEG_60_180
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-11, D-A3-16) ─────────────────────
COMMITMENT_MONTHS = 12  # instalments due in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded instalments before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
# Who decides that an instalment was kept: "payments" (the money arrived within the
# grace) or "dcore" (DCORE's paid amount reaches the due). TEMPORARY choice, compared in
# the bundle check; the losing option goes.
KEPT_BY = ("payments", "dcore")
# Grace after the due date (payments judge): CC up to the first statement on or after
# the due date (the "paid as billed" clock, D-A3-8); RL to the end of the next month.
GRACE = {"cc": "next_statement", "rl": "next_month_end"}
CC_GRACE_FALLBACK_D = 31  # no statement yet after the due date

# ── Dimension B: payments while delinquent (D-A3-3, -5, -6) ───────────────────
QUALIFYING_SHARE = 1.0  # a cycle qualifies at 100% of one month's due (row 80)
MIN_PAYMENT_AED = 100  # and at least 100 AED; also "any payment" (D-A3-5)
REGULAR_FROM = {SEG_60_180: 2, SEG_180_PLUS: 3}  # qualifying cycles (rows 81, 89)
ANY_PAYMENT_MONTHS = {SEG_60_180: 3, SEG_180_PLUS: 12}  # the Some window (row 25)

# ── Dimension C: record before delinquency (D-A3-2, -8, -13) ──────────────────
PRE_DLQ_MONTHS = 12  # the 12 months before the episode (row 82)
PRE_DLQ_MIN_MONTHS_DUE = 3  # fewer months with a due: No record (row 83)
CLEAN_SHARE = 0.80  # Clean from (row 84)

# ── Contacts (D-A3-19, -20; Q-28, Q-29, Q-30) ─────────────────────────────────
DCORE_MAX_MONTHS = 24  # DCORE events read at most 24 months back (Q-30)
NO_PICKUP_NAMES = ("NO ANSWER", "LEFT_MSG")  # with _dcore_codes.RINGING

# ── CC cycles (D-A3-12, -15) ──────────────────────────────────────────────────
CYCLE_MAX_DAYS = 62  # a longer "cycle" spans missing statements: dropped
FLOOR_LOOKBACK_DAYS = 35  # keep the statement just before the history floor
BUCKET08_BASELINE_MONTHS = 12  # months of positive minimum due averaged (D-A3-12)

# ── State (D-A3-16, -19, -20, proposal 2026-11-05: Broken -1) ─────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 1

SCORECARD = Scorecard(
    prefix="a3",
    dimensions=(
        Dimension("commitments", "a3_commitments_level", COMMITMENT_POINTS, ("thin",)),
        Dimension(
            "dlq_payments", "a3_dlq_payment_level", DLQ_PAYMENT_POINTS, ("none",)
        ),
        Dimension(
            "pre_dlq_record", "a3_pre_dlq_payment_level", PRE_DLQ_POINTS, ("no_record",)
        ),
    ),
    overrides=(Override("refusal", "a3_refusal_flag", DEMOTE),),
    labels=DISPLAY_NAMES,
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py`
action: add · new sha256 `83fc43259e8be5b62f731b16e7657220a04daf7bc5bb28a34f90e0d8a91b7ac9` · new trailing newline: yes

New:

`````python
"""The A3 payment credibility pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base, crx_<p>_a4_deterioration ─► episode ─┬──────────────────┐
    product dues + payments (wrapper nodes) ─► cycle ledger ┼─ Dim B, Dim C ───┤
    DCORE plans + instalments ─► instalments ───────────────┼─ Dim A ──────────┼─► state
    dcore_prm_followup_outcomes ────────────────────────────┴─ contacts ───────┘

Needs, for the model_id: the obs base, A4, the product's payment sources and the DCORE
tables. ``params:a3_kept_by`` (``payments`` / ``dcore``) picks the Dimension A judge.
"""

from functools import partial

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a3_credibility
from .constants import GRACE
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import build_a3_episode, build_cycle_ledger, build_instalments

TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
# Ledger names as in the workplace catalog.
LEDGER = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}


def create_a3_pipeline(
    product: str, output: str, dues: Node, payments: Node, kept_by: str | None = None
) -> Pipeline:
    """The A3 axis for ``product``, written to ``output``. ``dues`` / ``payments`` are
    the product nodes writing ``crx_<p>_a3_dues`` / ``crx_<p>_a3_payments``. ``kept_by``
    fixes the Dimension A judge (the bundle check); default ``params:a3_kept_by``."""
    p = f"crx_{product}_a3"
    judge = {} if kept_by else {"kept_by": "params:a3_kept_by"}
    fixed = {"kept_by": kept_by} if kept_by else {}
    episode, ledger, inst = f"{p}_episode", LEDGER[product], f"{p}_instalments"

    def step(func, inputs: dict, out: str, name: str) -> Node:
        return node(
            func=func, inputs=inputs, outputs=out, name=f"build_{name}", tags=TAGS
        )

    return Pipeline(
        [
            step(
                build_a3_episode,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "deterioration": f"crx_{product}_a4_deterioration",
                },
                episode,
                episode,
            ),
            dues,
            payments,
            step(
                build_cycle_ledger,
                {"dues": f"{p}_dues", "payments": f"{p}_payments"},
                ledger,
                ledger,
            ),
            step(
                build_instalments,
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "agreements": "prm_dcore_account_agreements",
                    "int_ptp": "dcore_int_ptp",
                    "ptp_instalments": "dcore_prm_promise_instalments",
                    "int_settlement": "dcore_int_settlement",
                    "settlement_instalments": "dcore_prm_settlement_schedule_instalments",
                },
                inst,
                inst,
            ),
            step(
                partial(build_commitment_signals, grace=GRACE[product], **fixed),
                {
                    "episode": episode,
                    "instalments": inst,
                    "payments": f"{p}_payments",
                    "dues": f"{p}_dues",
                    **judge,
                },
                f"{p}_commitment_signals",
                f"{p}_commitment_signals",
            ),
            step(
                build_dlq_payment_signals,
                {"episode": episode, "ledger": ledger, "model_id": "params:model_id"},
                f"{p}_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_dlq_payment_signals",
            ),
            step(
                build_pre_dlq_payment_signals,
                {"episode": episode, "ledger": ledger},
                f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                f"{p}_pre_dlq_payment_signals",
            ),
            step(
                build_contact_signals,
                {
                    "episode": episode,
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "payments": f"{p}_payments",
                    "dues": f"{p}_dues",
                    "model_id": "params:model_id",
                },
                f"{p}_strong_negative_signals",
                f"{p}_contact_signals",
            ),
            step(
                partial(build_a3_credibility, **fixed),
                {
                    "episode": episode,
                    "commitments": f"{p}_commitment_signals",
                    "dlq_payments": f"{p}_dlq_payment_signals_single_payment_cycle_count",
                    "pre_dlq": f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                    "contacts": f"{p}_strong_negative_signals",
                    **judge,
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                output,
                f"{p}_payment_credibility",
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py`
action: add · new sha256 `eb8613bac8883b24600fddaafe8803c09dbbd8806b6761ae8f4adf829666021c` · new trailing newline: yes

New:

`````python
"""A3 signals per ``(account_id, observation_date)``: one builder per dimension and the
contact evidence. Every builder starts from the episode table (``build_a3_episode``).

Episode bounds (Q-11, Q-25, Q-31): the anchor is the episode's first month; a censored
anchor (A4 cropped the history and the episode ran from its first kept month) counts as
unknown, so its windows come from the observation lookback alone and Dimension C reads
No record. Dimension B starts the month after the episode month, Dimension C ends
before it, so the onset cycle is in neither.
"""

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import Window

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    instalment_amount_flags,
)

from .. import _dcore_codes as codes
from .._common import (
    GONE_DARK_DAYS,
    GRAIN,
    dcore_account_events,
    segment,
    window_agg,
    window_months,
    window_start,
)
from .constants import (
    ANY_PAYMENT_MONTHS,
    BROKEN_RATE,
    BROKEN_STREAK,
    CC_GRACE_FALLBACK_D,
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
    KEPT_BY,
    KEPT_RATE,
    MIN_CONCLUDED,
    MIN_PAYMENT_AED,
    NO_PICKUP_NAMES,
    PRE_DLQ_MIN_MONTHS_DUE,
    PRE_DLQ_MONTHS,
    QUALIFYING_SHARE,
    REGULAR_FROM,
)


def _anchor() -> Column:
    """The episode start, NULL when censored or missing (the bounds then fall back)."""
    return F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )


def _base(episode: DataFrame) -> DataFrame:
    return episode.select(*GRAIN, _anchor().alias("_anchor"))


# ── Dimension A: promises kept ────────────────────────────────────────────────


def _grace_cutoff(instalments: DataFrame, dues: DataFrame, grace: str) -> DataFrame:
    """``instalments`` + ``cutoff``: the last day a payment still keeps the instalment."""
    if grace == "next_month_end":
        return instalments.withColumn("cutoff", F.last_day(F.add_months("due_date", 1)))
    statements = dues.select("account_id", F.col("cycle_end").alias("_stmt")).distinct()
    first = (
        instalments.select("account_id", "due_date")
        .distinct()
        .join(statements, on="account_id")
        .filter(F.col("_stmt") >= F.col("due_date"))
        .groupBy("account_id", "due_date")
        .agg(F.min("_stmt").alias("cutoff"))
    )
    return instalments.join(
        first, on=["account_id", "due_date"], how="left"
    ).withColumn(
        "cutoff", F.coalesce("cutoff", F.date_add("due_date", CC_GRACE_FALLBACK_D))
    )


def _covered(instalments: DataFrame, payments: DataFrame) -> DataFrame:
    """``instalments`` + ``covered_date``: the day payments since the plan start first
    reach the plan's cumulative due up to and including the instalment (V1c rule)."""
    plan = Window.partitionBy("plan_id").orderBy("due_date", "due_amount")
    inst = instalments.withColumn("_n", F.row_number().over(plan)).withColumn(
        "cum_due",
        F.sum(F.coalesce("due_amount", F.lit(0.0))).over(
            plan.rowsBetween(Window.unboundedPreceding, 0)
        ),
    )
    running = (
        Window.partitionBy("plan_id", "_n")
        .orderBy("pay_date")
        .rangeBetween(Window.unboundedPreceding, 0)
    )
    hit = (
        inst.select("account_id", "plan_id", "_n", "plan_start", "cum_due")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(F.col("pay_date") >= F.col("plan_start"))
        .withColumn("_paid", F.sum("amount").over(running))
        .filter(F.col("_paid") >= F.col("cum_due"))
        .groupBy("plan_id", "_n")
        .agg(F.min("pay_date").alias("covered_date"))
    )
    return inst.join(hit, on=["plan_id", "_n"], how="left")


def build_commitment_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    episode: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    kept_by: str,
    grace: str,
) -> DataFrame:
    """Dimension A: kept / partly kept / thin / broken (D-A3-9, D-A3-11).

    Instalments due in ``[max(episode start, last 12 months), observation date]``.
    ``kept_by="payments"``: kept when payments reach the cumulative due by the grace
    cutoff; concluded once kept or past the cutoff. ``kept_by="dcore"``: DCORE's own
    paid / overdue flags. Broken: the last 3 concluded all broken (a broken instalment
    ranks first on a shared due date), or at least 2 concluded and under 40% kept.
    """
    if kept_by not in KEPT_BY:
        raise ValueError(f"a3_kept_by must be one of {KEPT_BY}, got {kept_by!r}")
    if kept_by == "payments":
        instalments = _covered(_grace_cutoff(instalments, dues, grace), payments)
    base = _base(episode)
    lower = F.greatest(window_start(COMMITMENT_MONTHS), F.col("_anchor"))
    rows = base.join(instalments, on="account_id").filter(
        (F.col("due_date") >= lower) & (F.col("due_date") <= F.col("observation_date"))
    )
    if kept_by == "payments":
        obs = F.col("observation_date")
        kept = F.col("covered_date") <= F.least("cutoff", obs)
        concluded = kept | (F.col("cutoff") <= obs)
    else:
        is_paid, _, is_overdue = instalment_amount_flags()
        kept, concluded = is_paid, is_paid | is_overdue
    rows = rows.withColumn("_kept", F.coalesce(kept, F.lit(False))).withColumn(
        "_concluded", F.coalesce(concluded, F.lit(False))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct("due_date", (~F.col("_kept")).cast("int").alias("broken")),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    agg = rows.groupBy(*GRAIN).agg(
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum((F.col("_concluded") & F.col("_kept")).cast("int")).alias(
            "commitments_kept"
        ),
        F.size(F.filter(last, lambda x: x["broken"] == 1)).alias(
            "commitments_last_broken_n"
        ),
    )
    done, ok = F.col("commitments_concluded"), F.col("commitments_kept")
    rate = F.when(done > 0, ok / done)
    level = (
        F.when(
            (F.col("commitments_last_broken_n") >= BROKEN_STREAK)
            | ((done >= MIN_CONCLUDED) & (rate < BROKEN_RATE)),
            "broken",
        )
        .when((done >= MIN_CONCLUDED) & (rate >= KEPT_RATE), "kept")
        .when(ok >= 1, "partly_kept")
        .otherwise("thin")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(
            0,
            ["commitments_concluded", "commitments_kept", "commitments_last_broken_n"],
        )
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_concluded",
            "commitments_kept",
            rate.alias("commitments_kept_rate"),
            "commitments_last_broken_n",
            level.alias("a3_commitments_level"),
        )
    )


# ── Dimension B: payments while delinquent ────────────────────────────────────


def build_dlq_payment_signals(
    episode: DataFrame, ledger: DataFrame, model_id: str
) -> DataFrame:
    """Dimension B: regular / some / none (D-A3-3, -5, -6).

    Cycles whose result statement falls after the episode month and in the window.
    Qualifying: paid >= max(one month's due, 100 AED). Regular: 2 of the last 3 months
    (61-180) / 3 of 6 (180+). Some: a cycle with 100 AED or more in the last 3 / 12
    months.
    """
    seg = segment(model_id)
    base = _base(episode).withColumn("dlq_from", F.add_months("_anchor", 1))
    regular_from = F.greatest(window_start(window_months(model_id)), F.col("dlq_from"))
    due, paid = F.col("due_amount"), F.col("paid_amount")
    qualifies = (due > 0) & (
        paid >= F.greatest(due * QUALIFYING_SHARE, F.lit(MIN_PAYMENT_AED))
    )
    agg = window_agg(
        base,
        ledger.withColumn("_q", qualifies),
        date_col="cycle_end",
        key="account_id",
        months=ANY_PAYMENT_MONTHS[seg],
        start="dlq_from",
        aggs=[
            F.sum(
                (F.col("_q") & (F.col("cycle_end") >= regular_from)).cast("int")
            ).alias("dlq_payment_qualifying_month_cnt"),
            F.max((paid >= MIN_PAYMENT_AED).cast("int")).alias("dlq_payment_any_flag"),
        ],
    )
    n, anyp = F.col("dlq_payment_qualifying_month_cnt"), F.col("dlq_payment_any_flag")
    level = (
        F.when(n >= REGULAR_FROM[seg], "regular")
        .when(anyp == 1, "some")
        .otherwise("none")
    )
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, ["dlq_payment_qualifying_month_cnt", "dlq_payment_any_flag"])
        .select(
            *GRAIN,
            regular_from.alias("dlq_payment_window_start"),
            n,
            anyp,
            level.alias("a3_dlq_payment_level"),
        )
    )


# ── Dimension C: record before delinquency ────────────────────────────────────


def build_pre_dlq_payment_signals(episode: DataFrame, ledger: DataFrame) -> DataFrame:
    """Dimension C: clean / not clean / no record (D-A3-2, -8, -13).

    Cycles whose result statement falls in the 12 months before the episode month.
    Paid as billed: the cycle's payments reach the billed amount (the minimum counts, no
    100 AED floor). Fewer than 3 months with a due: No record; also when the anchor is
    censored or missing (``pre_dlq_reason``).
    """
    base = episode.select(
        *GRAIN,
        _anchor().alias("_anchor"),
        F.when(F.col("episode_start").isNull(), "no_episode")
        .when(F.col("episode_left_censored"), "censored")
        .alias("pre_dlq_reason"),
    ).withColumn("pre_dlq_window_start", F.add_months("_anchor", -PRE_DLQ_MONTHS))
    has_due = F.col("billed_amount") > 0
    agg = (
        base.where(F.col("_anchor").isNotNull())
        .join(ledger, on="account_id")
        .filter(
            (F.col("cycle_end") >= F.col("pre_dlq_window_start"))
            & (F.col("cycle_end") < F.col("_anchor"))
        )
        .groupBy(*GRAIN)
        .agg(
            F.sum(has_due.cast("int")).alias("pre_dlq_months_due_n"),
            F.sum(
                (has_due & (F.col("paid_amount") >= F.col("billed_amount"))).cast("int")
            ).alias("pre_dlq_months_paid_as_billed_n"),
        )
    )
    due_n = F.coalesce(F.col("pre_dlq_months_due_n"), F.lit(0))
    share = F.when(
        due_n >= PRE_DLQ_MIN_MONTHS_DUE,
        F.col("pre_dlq_months_paid_as_billed_n") / due_n,
    )
    level = (
        F.when(share.isNull(), "no_record")
        .when(share >= CLEAN_SHARE, "clean")
        .otherwise("not_clean")
    )
    return base.join(agg, on=list(GRAIN), how="left").select(
        *GRAIN,
        "pre_dlq_window_start",
        due_n.alias("pre_dlq_months_due_n"),
        F.coalesce("pre_dlq_months_paid_as_billed_n", F.lit(0)).alias(
            "pre_dlq_months_paid_as_billed_n"
        ),
        share.alias("pre_dlq_paid_as_billed_share"),
        level.alias("a3_pre_dlq_payment_level"),
        "pre_dlq_reason",
    )


# ── Contacts: refusal and the diagnostics ─────────────────────────────────────

_DISPOSITIONS = [  # first match wins
    ("paid", codes.PAYMENT_CONFIRMED),
    ("refusal", codes.REFUSAL),
    ("dispute", codes.DISPUTE),
    ("hung_up", codes.HUNG_UP),
    ("ptp", set(codes.PROMISE_TO_PAY) | set(codes.RETAIN_PTP)),
    ("success", codes.RIGHT_PARTY_CONTACT),
]


def _disposition(name: Column) -> Column:
    out = F.lit(None).cast("string")
    for label, names in reversed(_DISPOSITIONS):
        out = F.when(name.isin(*sorted(names)), label).otherwise(out)
    return out


def _paid_after_refusal(
    refusals: DataFrame, payments: DataFrame, dues: DataFrame
) -> DataFrame:
    """Rows with a cycle (CC) / month (RL) holding 100 AED or more paid after the
    refusal day, up to the observation date (Q-29)."""
    cycles = dues.select("account_id", "cycle_start", "cycle_end")
    pays = (
        payments.alias("p")
        .join(
            cycles.alias("c"),
            (F.col("p.account_id") == F.col("c.account_id"))
            & (F.col("p.pay_date") > F.col("c.cycle_start"))
            & (F.col("p.pay_date") <= F.col("c.cycle_end")),
            "left",
        )
        .select(
            F.col("p.account_id").alias("account_id"),
            "p.pay_from",
            "p.pay_date",
            "p.amount",
            F.coalesce("c.cycle_end", F.last_day("p.pay_date")).alias("_cycle"),
        )
    )
    return (
        refusals.join(pays, on="account_id")
        .filter(
            (F.col("pay_from") > F.col("last_rpc_date"))
            & (F.col("pay_date") <= F.col("observation_date"))
        )
        .groupBy(*GRAIN, "_cycle")
        .agg(F.sum("amount").alias("_amount"))
        .filter(F.col("_amount") >= MIN_PAYMENT_AED)
        .select(*GRAIN)
        .distinct()
        .withColumn("_paid_after", F.lit(True))
    )


def build_contact_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    episode: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    payments: DataFrame,
    dues: DataFrame,
    model_id: str,
    max_months: int | None = DCORE_MAX_MONTHS,
) -> DataFrame:
    """The latest right-party contact in the episode and what it means (D-A3-19, -20).

    DCORE events of the account in ``[max(episode start, last 24 months), observation
    date]``. Latest right-party contact: on the same day a non-refusal counts as later
    (a same-day promise followed the refusal); a remaining tie takes the largest
    disposition (Q-28). ``a3_refusal_flag``: it was a refusal and no plan started and no
    cycle / month with 100 AED or more paid followed. Diagnostics (not in the state):
    dispute, hung up, and no pickup on N days after it with no dead line in between.
    """
    base = _base(episode)
    lower = window_start(max_months) if max_months else None
    lower = F.col("_anchor") if lower is None else F.greatest(lower, F.col("_anchor"))
    events = (
        base.join(dcore_account_events(episode, followup, agreements), on="account_id")
        .filter((F.col("day") >= lower) & (F.col("day") <= F.col("observation_date")))
        .withColumn("_disp", _disposition(F.col("name")))
    )
    latest = F.max(
        F.when(
            F.col("_disp").isNotNull(),
            F.struct(
                "day", (F.col("_disp") != "refusal").cast("int").alias("later"), "_disp"
            ),
        )
    )
    summary = events.groupBy(*GRAIN).agg(
        latest["day"].alias("last_rpc_date"),
        latest["_disp"].alias("last_rpc_disposition"),
        F.countDistinct(
            F.when(F.col("action_code").isin(*codes.CALL_CODES), F.col("day"))
        ).alias("contact_dates_n"),
    )
    after = events.join(summary.select(*GRAIN, "last_rpc_date"), on=list(GRAIN)).filter(
        F.col("day") > F.col("last_rpc_date")
    )
    no_pickup = F.col("name").isin(
        *sorted(set(codes.RINGING) | set(NO_PICKUP_NAMES))
    ) & F.col("action_code").isin(*codes.OUTBOUND_CODES)
    quiet = after.groupBy(*GRAIN).agg(
        F.countDistinct(F.when(no_pickup, F.col("day"))).alias("no_pickup_days_n"),
        F.max(F.col("name").isin(*sorted(codes.NOT_REACHABLE)).cast("int")).alias(
            "_dead"
        ),
    )
    refusals = summary.where(F.col("last_rpc_disposition") == "refusal").select(
        *GRAIN, "last_rpc_date"
    )
    planned = (
        refusals.join(
            instalments.select("account_id", "plan_start").distinct(), on="account_id"
        )
        .filter(
            (F.col("plan_start") > F.col("last_rpc_date"))
            & (F.col("plan_start") <= F.col("observation_date"))
        )
        .select(*GRAIN)
        .distinct()
        .withColumn("_planned", F.lit(True))
    )
    paid = _paid_after_refusal(refusals, payments, dues)
    disp = F.col("last_rpc_disposition")
    days = F.coalesce(F.col("no_pickup_days_n"), F.lit(0))
    return (
        base.select(*GRAIN)
        .join(summary, on=list(GRAIN), how="left")
        .join(quiet, on=list(GRAIN), how="left")
        .join(planned, on=list(GRAIN), how="left")
        .join(paid, on=list(GRAIN), how="left")
        .select(
            *GRAIN,
            "last_rpc_date",
            "last_rpc_disposition",
            F.coalesce("contact_dates_n", F.lit(0)).alias("contact_dates_n"),
            (
                (disp == "refusal")
                & F.col("_planned").isNull()
                & F.col("_paid_after").isNull()
            ).alias("a3_refusal_flag"),
            F.coalesce(F.col("_planned"), F.lit(False)).alias(
                "refusal_followed_by_plan"
            ),
            F.coalesce(F.col("_paid_after"), F.lit(False)).alias(
                "refusal_followed_by_payment"
            ),
            (disp == "dispute").alias("a3_dispute_flag"),
            (disp == "hung_up").alias("a3_hung_up_last"),
            days.alias("no_pickup_days_n"),
            (
                F.col("last_rpc_date").isNotNull()
                & (days >= GONE_DARK_DAYS[segment(model_id)])
                & (F.coalesce(F.col("_dead"), F.lit(0)) == 0)
            ).alias("a3_no_pickup_after_contact"),
        )
        .fillna(
            False,
            [
                "a3_refusal_flag",
                "a3_dispute_flag",
                "a3_hung_up_last",
                "a3_no_pickup_after_contact",
            ],
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py`
action: add · new sha256 `4eef4c47f561b21c469ddcd3799485de7b93fcb289f029a1150a3c8b4c82271c` · new trailing newline: yes

New:

`````python
"""A3 source nodes shared by both products: the episode anchor, the cycle ledger and
the DCORE promise instalments."""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)

from .._common import GRAIN, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start

DUES = ["account_id", "cycle_start", "cycle_end", "due_amount", "billed_amount"]
PAYMENTS = ["account_id", "pay_from", "pay_date", "amount"]


def build_a3_episode(obs_base: DataFrame, deterioration: DataFrame) -> DataFrame:
    """``GRAIN + episode_start, episode_left_censored`` for every base row (D-A3-2).

    ``episode_start`` is the first day of the month the current delinquency episode
    began, from A4 as of the observation date; NULL when A4 did not score the row (A3
    then reads Unknown, reason ``no_episode``, Q-12).
    """
    return obs_base.select(*GRAIN, "cif_id").join(
        episode_start(obs_base, deterioration), on=list(GRAIN), how="left"
    )


def build_cycle_ledger(dues: DataFrame, payments: DataFrame) -> DataFrame:
    """One row per account cycle: ``DUES`` + ``paid_amount``, the payments with
    ``cycle_start < pay_date <= cycle_end`` (paid before the next statement, D-A3-8).

    ``dues`` and ``payments`` follow the product contracts ``DUES`` / ``PAYMENTS``
    (CC: statement cycles and card payments; RL: months and the month's cash).
    """
    require_columns(dues, DUES, "A3 dues")
    require_columns(payments, PAYMENTS, "A3 payments")
    paid = (
        dues.select("account_id", "cycle_start", "cycle_end")
        .join(payments.select("account_id", "pay_date", "amount"), on="account_id")
        .filter(
            (F.col("pay_date") > F.col("cycle_start"))
            & (F.col("pay_date") <= F.col("cycle_end"))
        )
        .groupBy("account_id", "cycle_end")
        .agg(F.sum("amount").alias("paid_amount"))
    )
    return (
        dues.select(*DUES)
        .join(paid, on=["account_id", "cycle_end"], how="left")
        .withColumn("paid_amount", F.coalesce(F.col("paid_amount"), F.lit(0.0)))
    )


def build_instalments(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    agreements: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
) -> DataFrame:
    """PTP and settlement instalments of the base's accounts (D-A3-7, D-A3-9).

    One row per instalment of a non-cancelled plan: ``account_id``, ``plan_id``,
    ``plan_type``, ``plan_start`` (PTP: promise start, else event date; settlement: event
    date, the only date DCORE keeps), ``due_date``, ``due_amount``, ``payment_amount``
    (DCORE's). Cancelled instalments are nulled by DCORE's own rule and dropped.
    """
    require_columns(
        agreements, ["account_id", "agreement_id"], "prm_dcore_account_agreements"
    )
    require_columns(
        int_ptp,
        [
            "agreement_id",
            "promise_seqno",
            "promise_start",
            "event_date",
            "is_cancelled",
        ],
        "dcore_int_ptp",
    )
    require_columns(
        int_settlement,
        ["agreement_id", "rps_seqno", "event_date", "is_cancelled"],
        "dcore_int_settlement",
    )
    cols = ["due_date", "due_amount", "payment_amount", "instalment_status"]
    require_columns(
        ptp_instalments, ["promise_seqno", *cols], "dcore_prm_promise_instalments"
    )
    require_columns(
        settlement_instalments,
        ["rps_seqno", *cols],
        "dcore_prm_settlement_schedule_instalments",
    )
    links = scoped(
        agreements.select(
            string_key(agreements).alias("account_id"),
            F.col("agreement_id").cast("string").alias("agreement_id"),
        ),
        obs_base,
        "account_id",
    )

    def plans(  # pylint: disable=too-many-arguments,too-many-positional-arguments
        plan: DataFrame, seq: str, start, kind: str, rows: DataFrame, cancelled
    ) -> DataFrame:
        live = plan.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            seq,
            F.concat_ws(":", F.lit(kind), F.col(seq).cast("string")).alias("plan_id"),
            F.lit(kind).alias("plan_type"),
            start.cast("date").alias("plan_start"),
        )
        return null_cancelled_instalment_fields(
            live.join(rows.select(seq, *cols), on=seq), cancelled
        ).drop(seq)

    ptp = plans(
        int_ptp,
        "promise_seqno",
        F.coalesce(F.col("promise_start"), F.col("event_date")),
        "ptp",
        ptp_instalments,
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = plans(
        int_settlement,
        "rps_seqno",
        F.col("event_date"),
        "settlement",
        settlement_instalments,
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    return (
        ptp.unionByName(settlement)
        .join(F.broadcast(links), on="agreement_id")
        .where(F.col("due_date").isNotNull())
        .select(
            "account_id",
            "plan_id",
            "plan_type",
            "plan_start",
            F.col("due_date").cast("date").alias("due_date"),
            F.col("due_amount").cast("double").alias("due_amount"),
            F.col("payment_amount").cast("double").alias("payment_amount"),
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/__init__.py`
action: replace · base sha256 `6943ac69ca109c566c10c2abc368ceb31a27a56cb714d66220f85000bb3a188f` · base trailing newline: yes · new sha256 `117f8514c4f2102cc37c970e382ed6f85b97358824df3152f567a1474de7dca8` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T27 – A3 Payment Credibility axis v1 (4-state, DCORE PTP-based)."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/nodes.py`
action: replace · base sha256 `712615062d404db292ed1ee6358accdc0a268ae748157d798883d4bb7bc5e476` · base trailing newline: yes · new sha256 `eb424eba496165e83e60be411712720dfbb5b3c58c7294b1fb38d16deff439ad` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A3 Payment Credibility – node functions, in pipeline.py order.

Spec: logs/A3_credibility_shared.xlsx, sheet "A3 framework" (validated against the
12-account "Tester" fixture, test_a3_v2_scoring.py). Three scored dimensions sum to
a3_points_total (0-5); a strong negative demotes the state one level; zero evidence
gives Unknown:
    A. Commitments kept          Broken / Kept(2) / Partly kept(1) / Thin  (DCORE PTP + settlement)
    B. Payments in delinquency   Regular(2) / Some(1) / None(0)  (Way4 billing + transactions)
    C. Record before delinquency Clean(1) / Not clean / No record  (Way4 billing + transactions)
    State: payment_credibility_{high, moderate, low, unknown}.

Nodes (output dataset = function name with "build_" -> "crx_cc_"):
    1. build_a3_commitment_signals          Dimension A: level, points, broken streak
    2. build_a3_strong_negative_signals     strong-negative evidence (rules run in node 9)
    3. build_a3_payment_cycles              shared cycle/payment/due ledger for B and C
    4-6. build_a3_dlq_payment_signals_*     Dimension B: payment_sum_waterfall (shadow),
                                            single_payment_cycle_count (default),
                                            dpd_bucket_movement (shadow)
    7-8. build_a3_pre_dlq_payment_signals_* Dimension C: single_payment_cycle_count
                                            (default), dpd_bucket_movement (shadow)
    9. build_a3_payment_credibility         combiner -> a3_state_v1

Every method of B and C is always computed (per-method columns in the output for
cross-checking); params:a3_dlq_payment_evidence_method and
params:a3_pre_dlq_payment_evidence_method independently pick the shipped one.
RL (rl_a3_payment_credibility) wraps these functions.

Notes:
  - Grain: (account_id, observation_date) from cc_spine; Dimension C is
    (account_id, spell_id) and joins on (account_id, t0).
  - Right-party classification uses result_name allowlists from
    cc_a3_payment_credibility.constants (result_category is unreliable: "SUC" contains
    refusals) and considers all action codes, IA included; only contact_dates_n is
    limited to call-type codes (OC/CB/IC).
  - due_amount_m (_signals_common.resolve_due_amount_m) is the highest-impact
    assumption in Dimensions B and C.
"""

# pylint: disable=too-many-lines, duplicate-code

# pylint: disable=too-many-lines, duplicate-code
import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._common import log_latest_month
from enbd_collections.pipelines.crx_persona._spine_utils import join_spine_to_spell
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility._signals_common import (
    attribute_payments_to_billing_cycles,
    filter_payment_cycles,
    resolve_dpd_bucket_movement_history,
    resolve_dlq_payment_window,
    resolve_bucket08_fallback_due,
    resolve_due_amount_m,
    resolve_pre_dlq_spell_window,
    resolve_dlq_waterfall_qualifying_months_cleared,
    aggregate_dlq_window,
    aggregate_pre_dlq_window,
    payment_meets_floor,
    flag_followups_after_refusal,
    flag_plans_on_record,
    pooled_trailing_broken_streak,
)
from enbd_collections.pipelines.crx_persona._dcore_codes import (
    CALL_CODES,
    PAYMENT_CONFIRMED,
    PROMISE_TO_PAY,
    REFUSING,
    RETAIN_PTP,
    RIGHT_PARTY_CONTACT,
)
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _CONF_HIGH,
    _CONF_LOW,
    _CONF_MODERATE,
    _CONF_UNKNOWN,
    _DLQ_LEVEL_SATURATED,
    _METHOD_DPD_BUCKET_MOVEMENT,
    _METHOD_PAYMENT_SUM_WATERFALL,
    _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    _SB_PRIORITY,
    _TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M,
    _TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP,
    _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
    _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180,
    _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS,
    _TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE,
    _TAU_A3V2_PRE_DLQ_CLEAN_SHARE,
    _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    _TAU_A3V2_COMMITMENTS_BROKEN_RATE,
    _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
    _TAU_A3V2_COMMITMENTS_KEPT_RATE,
    _TAU_A3V2_COMMITMENTS_MIN_CONCLUDED,
    _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS,
    _TAU_A3V2_HIGH_FROM_POINTS,
    _TAU_A3V2_MODERATE_FROM_POINTS,
    _TAU_MIN_CONTACT_DATES,
)

LOG = logging.getLogger(__name__)

# ── Required columns for schema guards ────────────────────────────────────

# Dimension A reads the 12-month instalment counts; each guard nulls only its own columns.
_PTP_COUNT_COLS = [
    "agreement_id",
    "observation_date",
    "ptp_instalment_due_cnt_12m",  # Dimension A concluded count
    "ptp_instalment_paid_cnt_12m",  # Dimension A kept count
]
_SETTLEMENT_COUNT_COLS = [
    "agreement_id",
    "observation_date",
    "settlement_instalment_due_cnt_12m",  # Dimension A concluded count
    "settlement_instalment_paid_cnt_12m",  # Dimension A kept count
]

# Canonical right-party disposition labels (last_rpc_disposition)
_DISP_PAID = "paid"
_DISP_PTP = "ptp"
_DISP_RTP = "rtp"
_DISP_SUCCESS = "success"


# ── Shared: spine → spell → DCORE agreement bridge ───────────────────────


def _build_agreement_bridge(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    caller: str,
) -> DataFrame:
    """(account_id, observation_date, iagreementseqno, cif_id, t0) for every spine row.

    cc_spine joined to the spell active at the observation date (t0), then to
    dcore_observation_spine for the DCORE agreement id. Used by nodes 1 and 2.

    Args:
        cc_spine: contract_id (= account_id), observation_date, cif_id (authoritative).
        spell_table: account_id, spell_id, t0, spell_end.
        observation_spine: account_id, observation_date, agreement_id, cif_id.
        caller: node name, for error and log messages.
    """
    _SPINE_REQUIRED = {"account_id", "observation_date", "agreement_id", "cif_id"}
    if not _SPINE_REQUIRED.issubset(set(observation_spine.columns)):
        missing = _SPINE_REQUIRED - set(observation_spine.columns)
        raise ValueError(
            f"{caller}: dcore_observation_spine missing columns {missing}."
        )

    # (account_id, observation_date, spell_id, t0) – shared equality-join pattern.
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    # cc_spine.cif_id is authoritative; observation_spine.cif_id is excluded below.
    spine_base = spine_with_spell.join(
        cc_spine.select(
            F.col("contract_id").alias("account_id"), "observation_date", "cif_id"
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    agreement_scope = observation_spine.select(
        "account_id",
        "observation_date",
        F.col("agreement_id").alias("iagreementseqno"),
    )
    # spell_id dropped – A3 grain is (account_id, observation_date)
    agreement_bridge = spine_base.join(
        agreement_scope, on=["account_id", "observation_date"], how="left"
    ).select("account_id", "observation_date", "iagreementseqno", "cif_id", "t0")

    n_rows = spine_base.count()
    n_with_agreement = agreement_bridge.filter(
        F.col("iagreementseqno").isNotNull()
    ).count()
    LOG.info(
        "%s: %d rows | agreement bridge: %d (%.1f%%)",
        caller,
        n_rows,
        n_with_agreement,
        100.0 * n_with_agreement / max(n_rows, 1),
    )
    return agreement_bridge


def _guarded_feat(feat: DataFrame, required_cols: list, name: str, caller: str):
    """feat if it has every required column and at least one row, else None (warned)."""
    present = set(feat.columns)
    if all(c in present for c in required_cols) and feat.limit(1).count() > 0:
        return feat
    LOG.warning(
        "%s: %s schema guard fired (missing=%s or empty) – its columns will be NULL.",
        caller,
        name,
        [c for c in required_cols if c not in present],
    )
    return None


# ── Node 1 – Dimension A: build_a3_commitment_signals ─────────────────────


def derive_commitments_level(df: DataFrame) -> DataFrame:
    """Dimension A: instalment counts and streak -> level and points.

    Concluded / kept are PTP + settlement instalments due / paid in the last 12 months
    (instalment level, not plan level – a plan-level bar of 2 whole plans left 79% of
    the population Thin). [CONFIRM] a deviation from the business "Tester" sheet, which
    was built on plan-level inputs.

    Level, checked in this order: Broken (last 3 concluded all broken, or >= 2
    concluded and kept-rate < 40%), Kept (>= 2 concluded, kept-rate >= 80%), Partly
    kept (>= 1 kept), else Thin. Pending instalments earn nothing (spec window rule).

    Needs ptp_/settlement_instalment_{due,paid}_cnt_12m and commitments_broken_streak
    (NULL counts as 0). Adds commitments_concluded / _kept / _kept_rate, the coalesced
    commitments_broken_streak, a3_commitments_level and a3_commitments_points
    (Kept 2, Partly kept 1, else 0).
    """
    kept = F.coalesce(F.col("ptp_instalment_paid_cnt_12m"), F.lit(0)) + F.coalesce(
        F.col("settlement_instalment_paid_cnt_12m"), F.lit(0)
    )
    concluded = F.coalesce(F.col("ptp_instalment_due_cnt_12m"), F.lit(0)) + F.coalesce(
        F.col("settlement_instalment_due_cnt_12m"), F.lit(0)
    )
    df = (
        df.withColumn("commitments_concluded", concluded)
        .withColumn("commitments_kept", kept)
        .withColumn(
            "commitments_kept_rate",
            F.when(concluded > 0, kept.cast("double") / concluded.cast("double")),
        )
        .withColumn(
            "commitments_broken_streak",
            F.coalesce(F.col("commitments_broken_streak"), F.lit(0)),
        )
    )
    rate = F.col("commitments_kept_rate")
    df = df.withColumn(
        "a3_commitments_level",
        F.when(
            (
                F.col("commitments_broken_streak")
                >= _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N
            )
            | (
                (F.col("commitments_concluded") >= 2)
                & rate.isNotNull()
                & (rate < _TAU_A3V2_COMMITMENTS_BROKEN_RATE)
            ),
            F.lit("broken"),
        )
        .when(
            (F.col("commitments_concluded") >= _TAU_A3V2_COMMITMENTS_MIN_CONCLUDED)
            & rate.isNotNull()
            & (rate >= _TAU_A3V2_COMMITMENTS_KEPT_RATE),
            F.lit("kept"),
        )
        .when(F.col("commitments_kept") >= 1, F.lit("partly_kept"))
        .otherwise(F.lit("thin")),
    )
    return df.withColumn(
        "a3_commitments_points",
        F.when(F.col("a3_commitments_level") == "kept", F.lit(2))
        .when(F.col("a3_commitments_level") == "partly_kept", F.lit(1))
        .otherwise(F.lit(0)),
    )


def build_a3_commitment_signals(  # pylint: disable=too-many-positional-arguments,too-many-locals
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    feat_ptp: DataFrame,
    feat_settlement: DataFrame,
    int_ptp: DataFrame = None,
    ptp_instalments: DataFrame = None,
    int_settlement: DataFrame = None,
    settlement_instalments: DataFrame = None,
) -> DataFrame:
    """Dimension A (commitments kept) per (account_id, observation_date).

    Steps: agreement bridge; 12-month PTP and settlement instalment counts from
    dcore_feat_ptp / dcore_feat_settlement (each guarded: missing columns or empty ->
    NULL counts); broken streak from the raw instalment tables
    (_signals_common.pooled_trailing_broken_streak, NULL when any is None); then
    derive_commitments_level.

    Args:
        cc_spine: master grain (account_id, observation_date, cif_id).
        spell_table: crx_cc_spell_table – t0 per spell.
        observation_spine: dcore_observation_spine – account -> agreement.
        feat_ptp / feat_settlement: dcore_feat_ptp / dcore_feat_settlement.
        int_ptp / ptp_instalments / int_settlement / settlement_instalments:
            dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments.

    Returns:
        (account_id, observation_date, iagreementseqno, t0, commitments_concluded,
        commitments_kept, commitments_kept_rate, commitments_broken_streak,
        a3_commitments_level, a3_commitments_points).
    """
    caller = "build_a3_commitment_signals"
    bridge = _build_agreement_bridge(cc_spine, spell_table, observation_spine, caller)
    keys = ["iagreementseqno", "observation_date"]

    result = bridge.select("account_id", "observation_date", "iagreementseqno", "t0")

    ptp = _guarded_feat(feat_ptp, _PTP_COUNT_COLS, "dcore_feat_ptp", caller)
    if ptp is None:
        result = result.withColumn(
            "ptp_instalment_due_cnt_12m", F.lit(None).cast("int")
        ).withColumn("ptp_instalment_paid_cnt_12m", F.lit(None).cast("int"))
    else:
        # AS-OF: one row per (agreement_id, obs_date).
        result = result.join(
            ptp.select(
                F.col("agreement_id").alias("iagreementseqno"),
                "observation_date",
                "ptp_instalment_due_cnt_12m",
                "ptp_instalment_paid_cnt_12m",
            ),
            on=keys,
            how="left",
        )

    settlement = _guarded_feat(
        feat_settlement, _SETTLEMENT_COUNT_COLS, "dcore_feat_settlement", caller
    )
    if settlement is None:
        result = result.withColumn(
            "settlement_instalment_due_cnt_12m", F.lit(None).cast("int")
        ).withColumn("settlement_instalment_paid_cnt_12m", F.lit(None).cast("int"))
    else:
        result = result.join(
            settlement.select(
                F.col("agreement_id").alias("iagreementseqno"),
                "observation_date",
                "settlement_instalment_due_cnt_12m",
                "settlement_instalment_paid_cnt_12m",
            ),
            on=keys,
            how="left",
        )

    # Built from the raw instalment tables, not dcore_feat_*: those carry only
    # plan-level / windowed aggregates, not the order of the latest instalments.
    if any(
        df is None
        for df in (int_ptp, ptp_instalments, int_settlement, settlement_instalments)
    ):
        LOG.warning(
            "%s: instalment tables not supplied – commitments_broken_streak is NULL.",
            caller,
        )
        result = result.withColumn("commitments_broken_streak", F.lit(None).cast("int"))
    else:
        streak = pooled_trailing_broken_streak(
            result, int_ptp, ptp_instalments, int_settlement, settlement_instalments
        )
        result = result.join(streak, on=keys, how="left")

    return derive_commitments_level(result).select(
        "account_id",
        "observation_date",
        "iagreementseqno",
        "t0",
        "commitments_concluded",
        "commitments_kept",
        "commitments_kept_rate",
        "commitments_broken_streak",
        "a3_commitments_level",
        "a3_commitments_points",
    )


# ── Node 2 – Strong negatives: build_a3_strong_negative_signals ──────────


def build_a3_strong_negative_signals(  # pylint: disable=too-many-positional-arguments,too-many-locals
    cc_spine: DataFrame,
    spell_table: DataFrame,
    observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
    transactions: DataFrame = None,
) -> DataFrame:
    """Evidence for the strong negatives per (account_id, observation_date).

    Evidence only; the rules (broken commitments / refusal / no response) run in
    build_a3_payment_credibility, which holds Dimension A's level and Dimension B's
    any-payment flag.

    Steps: agreement bridge; contact evidence from dcore_prm_followup_outcomes
    (_aggregate_disposition); PTP / settlement on record since T0
    (_signals_common.flag_plans_on_record); what followed the latest refusal
    (_signals_common.flag_followups_after_refusal).

    Args:
        cc_spine / spell_table / observation_spine: as build_a3_commitment_signals.
        followup_outcomes: dcore_prm_followup_outcomes (agreement_id, action_ts,
            action_code, result_category, result_name).
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
        transactions: crx_cc_transactions. None (RL) -> the Refusal rule falls back to
            Dimension B's any-payment flag.

    Returns:
        (account_id, observation_date, contact_dates_n, rpc_confirmed, ptp_on_record_flag,
        arrangement_on_record_flag, last_rpc_disposition, refusal_followed_by_commitment,
        refusal_followed_by_payment, refusal_followed_by_payment_min_amount,
        payment_evidence_available).
    """
    caller = "build_a3_strong_negative_signals"
    bridge = _build_agreement_bridge(cc_spine, spell_table, observation_spine, caller)

    # ── Pass B: DCORE disposition signals ─────────────────────────────────
    _REQUIRED_FOLLOWUP_COLS = {
        "agreement_id",  # was iagreementseqno
        "action_ts",  # was szactiondate
        "action_code",  # OC/CB/IC/IA – used to restrict to call-type events
        "result_category",  # was szcategorycode
        "result_name",  # was szresultname – now carried directly, no join needed
    }

    followup_cols = set(followup_outcomes.columns)
    if not _REQUIRED_FOLLOWUP_COLS.issubset(followup_cols):
        missing = _REQUIRED_FOLLOWUP_COLS - followup_cols
        LOG.warning(
            "%s: dcore_prm_followup_outcomes missing columns %s – disposition signals "
            "will be all-NULL / zero.",
            caller,
            missing,
        )
        result = _null_disposition(bridge)
    elif followup_outcomes.limit(1).count() == 0:
        LOG.warning(
            "%s: dcore_prm_followup_outcomes is empty – disposition signals will be "
            "all-NULL / zero.",
            caller,
        )
        result = _null_disposition(bridge)
    else:
        result = _aggregate_disposition(bridge, followup_outcomes)

    # ── Pass C: PTP / settlement on record since T0 ───────────────────────
    result = flag_plans_on_record(result, int_ptp, int_settlement)

    # ── Pass D: what followed the latest right-party refusal ──────────────
    result = flag_followups_after_refusal(result, int_ptp, int_settlement, transactions)
    return result.drop("iagreementseqno", "cif_id", "t0", "last_rpc_date")


# ── helpers for node 2 ─────


def _null_disposition(base: DataFrame) -> DataFrame:
    """Return base with all disposition signal columns as NULL/zero."""
    return base.select(
        "account_id",
        "observation_date",
        "iagreementseqno",
        "t0",
        F.lit(None).cast("int").alias("contact_dates_n"),
        F.lit(0).cast("int").alias("rpc_confirmed"),
        F.lit(None).cast("string").alias("last_rpc_disposition"),
        F.lit(None).cast("date").alias("last_rpc_date"),
    )


def _aggregate_disposition(
    agreement_bridge: DataFrame, followup: DataFrame
) -> DataFrame:
    """Contact evidence per (account_id, observation_date) for the strong negatives.

    Window: [t0, observation_date); falls back to (-inf, observation_date)
    when t0 is NULL (no active spell) so real followup history still
    surfaces – see inline comment above the filter. result_name is carried
    directly on dcore_prm_followup_outcomes (no join required); allowlists from
    cc_a3_payment_credibility.constants are matched against result_name (upper-stripped).

    Outputs (added to the bridge columns):
        contact_dates_n      – distinct dates with a call-type action (OC outbound
                               call, CB callback, IC inbound call). 3 calls on one
                               day are weaker evidence than 3 separate days. No-response.
        rpc_confirmed        – 1 if any event matched RIGHT_PARTY_CONTACT
                               (result_category is not used: "SUC" is unreliable, it
                               contains refusals). No-response.
        last_rpc_disposition / last_rpc_date – the latest right-party event
                               (paid / rtp / ptp / success); Refusal.

    Right-party classification considers ALL action codes, including IA (internal
    action): confirmed payments and RETAIN PTP are frequently logged administratively
    rather than against a live call.

    Disposition waterfall (first match wins – order is load-bearing):
        _DISP_PAID    – PAYMENT_CONFIRMED (confirmed completed payment)
        _DISP_RTP     – REFUSING (explicit refusal/hang-up/dispute)
        _DISP_PTP     – PROMISE_TO_PAY | RETAIN_PTP
        _DISP_SUCCESS – RIGHT_PARTY_CONTACT (cooperative contact not
                        already claimed above)
    Anything else (unreachable, ringing, unclassified) is not a right-party event.
    """

    # Window [t0, observation_date). A NULL t0 (no active spell) is an unbounded lower
    # bound: comparing against NULL would drop every event and turn "window unknown"
    # into a false "no contact".
    window_events = (
        followup.select(
            F.col("agreement_id").alias("iagreementseqno"),
            F.col("action_ts").cast("date").alias("szactiondate"),
            F.col("action_code"),
            F.col("result_category").alias("szcategorycode"),
            "result_name",
        )
        .join(
            agreement_bridge.select(
                "account_id", "observation_date", "t0", "iagreementseqno"
            ),
            on="iagreementseqno",
            how="inner",
        )
        .filter(
            (F.col("t0").isNull() | (F.col("szactiondate") >= F.col("t0")))
            & (F.col("szactiondate") < F.col("observation_date"))
        )
        .withColumn("_result_name_upper", F.upper(F.trim(F.col("result_name"))))
        # Tags call-type events for the attempt-volume counters only
        # (contact_attempts_n / contact_dates_n) – disposition classification
        # below is intentionally NOT restricted by this flag.
        .withColumn("_is_call_code", F.col("action_code").isin(*CALL_CODES))
    )

    # Classify each event; a NULL _disp is not a right-party contact. Order is
    # load-bearing: PAID first, RTP next so refusals inside _RIGHT_PARTY_CONTACT are
    # not mis-classified as SUCCESS, PTP before SUCCESS for the same reason.
    window_with_disp = window_events.withColumn(
        "_disp",
        F.when(
            F.col("_result_name_upper").isin(*PAYMENT_CONFIRMED),
            F.lit(_DISP_PAID),
        )
        .when(F.col("_result_name_upper").isin(*REFUSING), F.lit(_DISP_RTP))
        .when(
            F.col("_result_name_upper").isin(*PROMISE_TO_PAY)
            | F.col("_result_name_upper").isin(*RETAIN_PTP),
            F.lit(_DISP_PTP),
        )
        .when(
            F.col("_result_name_upper").isin(*RIGHT_PARTY_CONTACT),
            F.lit(_DISP_SUCCESS),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    # Latest right-party contact. On the same date a non-refusal ranks as later: a
    # same-day promise followed the refusal.
    last_rpc = (
        window_with_disp.filter(F.col("_disp").isNotNull())
        .withColumn(
            "_rpc_rn",
            F.row_number().over(
                Window.partitionBy("account_id", "observation_date").orderBy(
                    F.col("szactiondate").desc(),
                    F.when(F.col("_disp") == _DISP_RTP, 1).otherwise(0),
                )
            ),
        )
        .filter(F.col("_rpc_rn") == 1)
        .select(
            "account_id",
            "observation_date",
            F.col("_disp").alias("last_rpc_disposition"),
            F.col("szactiondate").alias("last_rpc_date"),
        )
    )

    agg = window_with_disp.groupBy("account_id", "observation_date").agg(
        F.countDistinct(F.when(F.col("_is_call_code"), F.col("szactiondate")))
        .cast("int")
        .alias("contact_dates_n"),
        F.max(
            F.when(
                F.col("_result_name_upper").isin(*RIGHT_PARTY_CONTACT),
                F.lit(1),
            ).otherwise(F.lit(0))
        )
        .cast("int")
        .alias("rpc_confirmed"),
    )

    return (
        agreement_bridge.join(agg, on=["account_id", "observation_date"], how="left")
        .join(last_rpc, on=["account_id", "observation_date"], how="left")
        .fillna({"contact_dates_n": 0, "rpc_confirmed": 0})
        # fillna turned "no DCORE agreement at all" into 0 contact dates; restore NULL to
        # tell it apart from "agreement found but no call-type event in the window"
        # (the no_response rule requires a non-NULL contact_dates_n).
        .withColumn(
            "contact_dates_n",
            F.when(
                F.col("iagreementseqno").isNull(), F.lit(None).cast("int")
            ).otherwise(F.col("contact_dates_n")),
        )
    )


# ── Node 3 – build_a3_payment_cycles (shared by Dimensions B and C) ──────


def build_a3_payment_cycles(
    crx_cc_billing: DataFrame,
    crx_cc_balance: DataFrame,
    crx_cc_transactions: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Billing-cycle payment attribution and due-amount resolution, run once for B and C.

    A cycle runs to the next existing statement, so cycles spanning missing statements
    (e.g. the 2021-2023 billing gap) are dropped: those starting more than 35 days before
    history_floor_date and those longer than 62 days
    (_signals_common.filter_payment_cycles).

    Args:
        crx_cc_billing: billing_date, due_date, next_billing_date.
        crx_cc_balance: minimum_due, overdue_bucket_01..08, total_due.
        crx_cc_transactions: payment transactions (txn_category, is_post_block_x_fee).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, billing_date) with due_date, next_billing_date,
        payment_sum_in_cycle, on_time_payment_sum_in_cycle
        (resolve_due_amount_m), due_amount_fallback_m (the account's frozen baseline on
        statements where only overdue_bucket_08 is left, else NULL;
        resolve_bucket08_fallback_due; read only by the Dimension B default method) and
        waterfall_qualifying_months_cleared_m (Dimension B's lumpsum-aware count,
        resolve_dlq_waterfall_qualifying_months_cleared).
    """
    cycles_raw = filter_payment_cycles(
        attribute_payments_to_billing_cycles(crx_cc_billing, crx_cc_transactions),
        history_floor_date,
    )
    cycles = cycles_raw.withColumnRenamed("contract_id", "account_id")

    balance_due = resolve_due_amount_m(crx_cc_balance)
    qualifying_months = resolve_dlq_waterfall_qualifying_months_cleared(
        crx_cc_balance,
        cycles_raw,
        _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
        bucket08_baseline_lookback_m=_TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M,
        bucket08_max_split=_TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP,
    )

    return (
        cycles.join(balance_due, on=["account_id", "billing_date"], how="left")
        .join(
            resolve_bucket08_fallback_due(crx_cc_balance),
            on=["account_id", "billing_date"],
            how="left",
        )
        .join(qualifying_months, on=["account_id", "billing_date"], how="left")
    )


# ── Nodes 4-6 – Dimension B: payments in delinquency ─────────────────────


def _dlq_payment_level_and_points(agg: DataFrame) -> DataFrame:
    """Dimension B ladder shared by the methods: regular / some / none, points 2 / 1 / 0."""
    result = agg.withColumn(
        "dlq_payment_level",
        F.when(
            (
                (
                    F.col("dlq_payment_window_months")
                    == _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS
                )
            )
            | (
                (
                    F.col("dlq_payment_window_months")
                    != _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180
                )
            ),
            F.lit("regular"),
        )
        .when(F.col("dlq_payment_any_flag") == 1, F.lit("some"))
        .otherwise(F.lit("none")),
    )
    return result.withColumn(
        "dlq_payment_points",
        F.when(F.col("dlq_payment_level") == "regular", F.lit(2))
        .when(F.col("dlq_payment_level") == "some", F.lit(1))
        .otherwise(F.lit(0)),
    )


def _dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Typed output select shared by the three Dimension B methods."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("t0").cast("date"),
        F.col("dlq_payment_window_months").cast("int"),
        F.col("dlq_payment_any_window_months").cast("int"),
        F.col("dlq_payment_qualifying_month_cnt").cast("int"),
        F.col("dlq_payment_any_flag").cast("int"),
        F.col("dlq_payment_level").cast("string"),
        F.col("dlq_payment_points").cast("int"),
    )


def build_a3_dlq_payment_signals_payment_sum_waterfall(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, payment_sum_waterfall method (shadow): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    A lumpsum that clears several overdue buckets credits several months
    (waterfall_qualifying_months_cleared_m). Amount-only, no due-date check.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    agg = aggregate_dlq_window(
        spine_with_window,
        crx_cc_a3_payment_cycles.filter(F.col("next_billing_date").isNotNull()),
        "next_billing_date",
        # 180+ (_min_payment_aed = 100): a cycle credits months only if its payment is
        # at least 100 AED; 61-180 has no floor.
        F.when(
            payment_meets_floor(F.col("c.payment_sum_in_cycle")),
            F.coalesce(F.col("c.waterfall_qualifying_months_cleared_m"), F.lit(0)),
        ).otherwise(F.lit(0)),
        (F.col("c.payment_sum_in_cycle") > 0)
        & payment_meets_floor(F.col("c.payment_sum_in_cycle")),
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


def build_a3_dlq_payment_signals_single_payment_cycle_count(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, single_payment_cycle_count method (default): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    Each cycle is judged on its own: qualifying when payment_sum_in_cycle >=
    max(due x share, minimum payment); no multi-month credit from one lumpsum.
    Rule: 2+ qualifying months of 3 (61-180), 3+ of 6 (180+). The due is due_amount_m, or
    for a statement where only overdue_bucket_08 is left the account's frozen baseline
    (due_amount_fallback_m); NULL when neither exists, and the cycle cannot qualify.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    cycles_with_evidence = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    )
    if "due_amount_fallback_m" not in cycles_with_evidence.columns:
        cycles_with_evidence = cycles_with_evidence.withColumn(
            "due_amount_fallback_m", F.lit(None).cast("double")
        )

    # Due = due_amount_m, else the frozen bucket-08 baseline.
    _due = F.coalesce(F.col("c.due_amount_m"), F.col("c.due_amount_fallback_m"))
    # Required payment = max(100% of the due, the 180+ minimum payment): at 180+ a tiny
    # due cannot be cleared by a token payment (_min_payment_aed = 0 at 61-180).
    _required_payment = F.greatest(
        _due * F.lit(_TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE),
        F.col("s._min_payment_aed"),
    )
    _is_qualifying_cycle = F.when(
        _due.isNotNull() & (_due > 0),
        F.col("c.payment_sum_in_cycle") >= _required_payment,
    ).otherwise(F.lit(False))

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "next_billing_date",
        _is_qualifying_cycle.cast("int"),
        (F.col("c.payment_sum_in_cycle") > 0)
        & payment_meets_floor(F.col("c.payment_sum_in_cycle")),
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


def build_a3_dlq_payment_signals_dpd_bucket_movement(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_full_history: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension B, dpd_bucket_movement method (shadow): is money coming in now?

    Window after onset: "regular" counts qualifying months over 3 months at 61-180 DPD and
    6 at 180+ (window from cc_spine.dlq_bucket_from_hist, 3 when NULL [CONFIRM]); "some"
    is any payment over 3 months (61-180) or 12 months (180+). At 180+ a cycle also needs
    a payment of at least 100 AED (_signals_common.payment_meets_floor).
    Cycles are keyed on next_billing_date, the statement that shows the result of that
    cycle's payment; the latest cycle (no next statement yet) is excluded.

    Infers payment from month-over-month DLQ bucket movement. Per statement, the bucket
    (crx_cc_full_history via resolve_dpd_bucket_movement_history) already reflects cash
    received since the previous statement, so it is compared with the previous row:
        no previous cycle                  -> 0
        improved (level < prev)            -> prev - level, +1 unless fully cured (level 0)
        flat, nonzero, below the cap       -> 1
        flat at zero                       -> 0 (cannot tell dormant from paying on time)
        flat at the cap (9)                -> ambiguous; the waterfall count for that cycle
        worsened                           -> 0
    The +1 offsets the bucket index being net of the cycle's own new unpaid minimum due.
    Bucket credits carry no amount, so the 100 AED floor applies only to the cap fallback.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_full_history: account_id, billing_date, dlq_bucket.
        crx_cc_spell_table: t0 per spell.
        cc_spine: observation_date grid and dlq_bucket_from_hist (sets the window).
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, observation_date): t0, dlq_payment_window_months,
        dlq_payment_any_window_months, dlq_payment_qualifying_month_cnt,
        dlq_payment_any_flag, dlq_payment_level (regular / some / none),
        dlq_payment_points (2 / 1 / 0).
    """
    spine_with_window = resolve_dlq_payment_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    qualifying_months_by_evidence_date = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    ).select(
        "account_id",
        F.col("next_billing_date").alias("billing_date"),
        "waterfall_qualifying_months_cleared_m",
        F.col("payment_sum_in_cycle").alias("_cycle_payment_sum"),
    )
    dlq_bucket_history = resolve_dpd_bucket_movement_history(
        crx_cc_full_history, history_floor_date
    ).join(
        qualifying_months_by_evidence_date,
        on=["account_id", "billing_date"],
        how="left",
    )

    _dlq_levels_improved = F.col("dlq_level_prev_m") - F.col("dlq_level_m")
    # +1 unless this row is fully cured (see docstring).
    _improved_credit = F.when(
        F.col("dlq_level_m") == 0, _dlq_levels_improved
    ).otherwise(_dlq_levels_improved + 1)
    cycles_with_evidence = dlq_bucket_history.withColumn(
        "_qualifying_months_m",
        F.when(F.col("dlq_level_prev_m").isNull(), F.lit(0))
        .when(_dlq_levels_improved > 0, _improved_credit)
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") < _DLQ_LEVEL_SATURATED)
            & (F.col("dlq_level_m") != 0),
            F.lit(1),
        )
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") == _DLQ_LEVEL_SATURATED),
            F.coalesce(F.col("waterfall_qualifying_months_cleared_m"), F.lit(0)),
        )
        .otherwise(F.lit(0)),
    ).withColumn(
        "_is_cap_fallback",
        (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
        & (F.col("dlq_level_m") == _DLQ_LEVEL_SATURATED),
    )

    # Bucket-movement credits carry no amount, so the 180+ minimum payment (100 AED)
    # applies only to the amount-based fallback at the bucket cap.
    _months = F.when(
        F.col("c._is_cap_fallback")
        & ~payment_meets_floor(F.coalesce(F.col("c._cycle_payment_sum"), F.lit(0.0))),
        F.lit(0),
    ).otherwise(F.col("c._qualifying_months_m"))

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "billing_date",
        _months,
        _months >= 1,
    )

    result = _dlq_payment_level_and_points(agg)

    return _dlq_payment_signals_output(result)


# ── Nodes 7-8 – Dimension C: record before delinquency ───────────────────


def _pre_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Typed output select shared by the two Dimension C methods."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("pre_dlq_months_due_n").cast("int"),
        F.col("pre_dlq_months_paid_as_billed_n").cast("int"),
        F.col("pre_dlq_paid_as_billed_share").cast("double"),
    )


def build_a3_pre_dlq_payment_signals_single_payment_cycle_count(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension C, single_payment_cycle_count method (default): did they pay as billed
    before delinquency started?

    Window: the 12 months strictly before t0, never mixed with post-onset months. "Paid as
    billed" = payment_sum_in_cycle >= _TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE (strict 100%) x
    due_amount_m. Cycles are keyed on next_billing_date (the statement that shows the
    result); cycles without one are excluded.

    [TEMPORARY, 2026-10-21] The check ignores the due date (whole-cycle payment, not
    on_time_payment_sum_in_cycle) so both Dimension C methods answer the same question;
    the due-date-sensitive version disagreed with dpd_bucket_movement on 39% of rows.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_spell_table: t0 per spell.
        cc_spine: population filter only – drops spells not in the current model_id
            population; the window itself is purely t0-anchored.
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, spell_id): t0, pre_dlq_months_due_n, pre_dlq_months_paid_as_billed_n,
        pre_dlq_paid_as_billed_share (NULL below _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, the
        "No record" condition).
    """
    spells = resolve_pre_dlq_spell_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    cycles_with_due = (
        crx_cc_a3_payment_cycles.filter(F.col("next_billing_date").isNotNull())
        .withColumn(
            "_has_due",
            F.col("due_amount_m").isNotNull() & (F.col("due_amount_m") > 0),
        )
        .withColumn(
            "_paid_on_time",
            F.when(
                F.col("_has_due"),
                # Strict 100% of due; ignores the due date (see docstring).
                F.col("payment_sum_in_cycle")
                >= F.col("due_amount_m") * F.lit(_TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE),
            ).otherwise(F.lit(False)),
        )
    )

    result = aggregate_pre_dlq_window(spells, cycles_with_due, "_paid_on_time")

    return _pre_dlq_payment_signals_output(result)


def build_a3_pre_dlq_payment_signals_dpd_bucket_movement(
    crx_cc_a3_payment_cycles: DataFrame,
    crx_cc_full_history: DataFrame,
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Dimension C, dpd_bucket_movement method (shadow): did they pay as billed before
    delinquency started?

    Same window and months_due denominator as the single_payment_cycle_count method. A
    cycle is "paid as billed" when the resulting statement's dlq_bucket
    (crx_cc_full_history at next_billing_date, the row that shows the result) is <= 1,
    i.e. the account did not fall into an overdue bucket. Level-only, so there is no
    flat-bucket ambiguity.

    Args:
        crx_cc_a3_payment_cycles: build_a3_payment_cycles output.
        crx_cc_full_history: account_id, billing_date, dlq_bucket.
        crx_cc_spell_table: t0 per spell.
        cc_spine: population filter only – drops spells not in the current model_id
            population; the window itself is purely t0-anchored.
        history_floor_date: params:cc_a3_history_floor_date (None = no floor).

    Returns:
        (account_id, spell_id): t0, pre_dlq_months_due_n, pre_dlq_months_paid_as_billed_n,
        pre_dlq_paid_as_billed_share (NULL below _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, the
        "No record" condition).
    """
    spells = resolve_pre_dlq_spell_window(
        cc_spine, crx_cc_spell_table, history_floor_date
    )

    resulting_dlq_bucket = crx_cc_full_history.select(
        F.col("account_id").alias("_evidence_account_id"),
        F.col("billing_date").alias("_evidence_date"),
        F.col("dlq_bucket").alias("_resulting_dlq_bucket"),
    )
    base = crx_cc_a3_payment_cycles.filter(
        F.col("next_billing_date").isNotNull()
    ).withColumn(
        "_has_due",
        F.col("due_amount_m").isNotNull() & (F.col("due_amount_m") > 0),
    )
    cycles_with_evidence = base.join(
        resulting_dlq_bucket,
        (base["account_id"] == resulting_dlq_bucket["_evidence_account_id"])
        & (base["next_billing_date"] == resulting_dlq_bucket["_evidence_date"]),
        "left",
    ).withColumn(
        "_paid_as_billed",
        F.col("_resulting_dlq_bucket").isNotNull()
        & (F.col("_resulting_dlq_bucket") <= 1),
    )

    result = aggregate_pre_dlq_window(spells, cycles_with_evidence, "_paid_as_billed")

    return _pre_dlq_payment_signals_output(result)


# ── Node 9 – build_a3_payment_credibility (combiner) ─────────────────────

_DLQ_PAIR_COLUMNS = {
    "dlq_payment_window_months": "int",
    "dlq_payment_any_window_months": "int",
    "dlq_payment_qualifying_month_cnt": "int",
    "dlq_payment_any_flag": "int",
    "dlq_payment_level": "string",
    "dlq_payment_points": "int",
}
_PRE_DLQ_PAIR_COLUMNS = {
    "pre_dlq_months_due_n": "int",
    "pre_dlq_months_paid_as_billed_n": "int",
    "pre_dlq_paid_as_billed_share": "double",
}
_STATE_HIGH = "payment_credibility_high"
_STATE_MODERATE = "payment_credibility_moderate"
_STATE_LOW = "payment_credibility_low"
_STATE_UNKNOWN = "payment_credibility_unknown"


def _join_signals_pair(
    df: DataFrame, pair: DataFrame, join_keys: list, columns: dict, approach: str
) -> DataFrame:
    """Left-join one approach's signals onto df, suffixing each column with the approach.

    A None pair, or a column the pair lacks, becomes a typed NULL so the column set
    is the same whichever pairs were supplied.
    """
    renamed = [
        (
            F.col(name)
            if pair is not None and name in pair.columns
            else F.lit(None).cast(dtype)
        ).alias(f"{name}_{approach}")
        for name, dtype in columns.items()
    ]
    if pair is None:
        return df.select("*", *renamed)
    return df.join(pair.select(*join_keys, *renamed), on=join_keys, how="left")


def _validate_method_pairs(
    dlq_pairs: dict,
    pre_dlq_pairs: dict,
    dlq_payment_evidence_method: str,
    pre_dlq_payment_evidence_method: str,
) -> None:
    """Reject unknown method names and a shipped method whose signals were not supplied.

    A missing shipped pair would otherwise be NULL-filled and silently ship as level
    "none" / "no_record" for every row. Shadow pairs stay optional.
    """
    checks = (
        (
            "dlq_payment_evidence_method",
            dlq_payment_evidence_method,
            dlq_pairs,
            "dlq_payment_signals_*",
        ),
        (
            "pre_dlq_payment_evidence_method",
            pre_dlq_payment_evidence_method,
            pre_dlq_pairs,
            "pre_dlq_payment_signals_*",
        ),
    )
    for param, method, pairs, _ in checks:
        if method not in pairs:
            raise ValueError(
                f"build_a3_payment_credibility: {param} must be one of "
                f"{list(pairs)}, got {method!r}."
            )
    for param, method, pairs, inputs in checks:
        if pairs[method] is None:
            raise ValueError(
                f"build_a3_payment_credibility: {param}={method!r} selects an "
                f"approach whose {inputs} input was not supplied."
            )


def _score_dimension_b(df: DataFrame, approaches) -> DataFrame:
    """Per-approach Dimension B level (NULL -> "none"), points (NULL -> 0) and count."""
    for approach in approaches:
        df = (
            df.withColumn(
                f"a3_dlq_payment_level_{approach}",
                F.coalesce(F.col(f"dlq_payment_level_{approach}"), F.lit("none")),
            )
            .withColumn(
                f"a3_dlq_payment_points_{approach}",
                F.coalesce(F.col(f"dlq_payment_points_{approach}"), F.lit(0)),
            )
            .withColumn(
                f"a3_dlq_payment_qualifying_month_cnt_{approach}",
                F.col(f"dlq_payment_qualifying_month_cnt_{approach}"),
            )
        )
    return df


def _pre_dlq_payment_level_col(months_due_col: Column, share_col: Column) -> Column:
    """Dimension C ladder: no_record (too few billed months) / clean / not_clean."""
    return (
        F.when(
            months_due_col.isNull()
            | (months_due_col < _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE),
            F.lit("no_record"),
        )
        .when(share_col >= _TAU_A3V2_PRE_DLQ_CLEAN_SHARE, F.lit("clean"))
        .otherwise(F.lit("not_clean"))
    )


def _score_dimension_c(df: DataFrame, approaches) -> DataFrame:
    """Per-approach Dimension C level, points (Clean 1, else 0) and months due."""
    for approach in approaches:
        df = (
            df.withColumn(
                f"a3_pre_dlq_payment_level_{approach}",
                _pre_dlq_payment_level_col(
                    F.col(f"pre_dlq_months_due_n_{approach}"),
                    F.col(f"pre_dlq_paid_as_billed_share_{approach}"),
                ),
            )
            .withColumn(
                f"a3_pre_dlq_payment_points_{approach}",
                F.when(
                    F.col(f"a3_pre_dlq_payment_level_{approach}") == "clean", F.lit(1)
                ).otherwise(F.lit(0)),
            )
            .withColumn(
                f"a3_pre_dlq_months_due_n_{approach}",
                F.col(f"pre_dlq_months_due_n_{approach}"),
            )
        )
    return df


def _select_shipped_methods(
    df: DataFrame, dlq_method: str, pre_dlq_method: str
) -> DataFrame:
    """Unsuffixed shipped Dimension B / C columns plus a3_points_total."""
    b, c = dlq_method, pre_dlq_method
    return (
        df.withColumn("a3_dlq_payment_level", F.col(f"a3_dlq_payment_level_{b}"))
        .withColumn("a3_dlq_payment_points", F.col(f"a3_dlq_payment_points_{b}"))
        .withColumn(
            "a3_dlq_payment_qualifying_month_cnt",
            F.col(f"a3_dlq_payment_qualifying_month_cnt_{b}"),
        )
        .withColumn(
            "a3_dlq_payment_window_months", F.col(f"dlq_payment_window_months_{b}")
        )
        .withColumn(
            "a3_dlq_payment_any_window_months",
            F.col(f"dlq_payment_any_window_months_{b}"),
        )
        .withColumn("a3_pre_dlq_payment_level", F.col(f"a3_pre_dlq_payment_level_{c}"))
        .withColumn(
            "a3_pre_dlq_payment_points", F.col(f"a3_pre_dlq_payment_points_{c}")
        )
        .withColumn("a3_pre_dlq_months_due_n", F.col(f"a3_pre_dlq_months_due_n_{c}"))
        .withColumn(
            "a3_points_total",
            F.col("a3_commitments_points")
            + F.col("a3_dlq_payment_points")
            + F.col("a3_pre_dlq_payment_points"),
        )
    )


def _strong_negative_reason(dlq_payment_evidence_method: str) -> Column:
    """Strong-negative reason per row, or NULL (framework block 3; one reason, no stacking).

    broken_commitments: Dimension A is Broken. refusal: the latest right-party contact
    was a refusal and nothing followed it. no_response: 3+ contact dates without
    reaching the customer, no promise / arrangement, no payment in the window. When
    several fire, _SB_PRIORITY picks the reason. Needs a3_commitments_level and
    commitments_concluded (Dimension A), the strong-negative evidence columns and
    Dimension B's shipped any-payment flag / window.
    """
    # No-response uses Dimension B's shipped any-payment flag (3 months at 61-180, 12 at
    # 180+).
    _dlq_any_flag_shipped = F.col(f"dlq_payment_any_flag_{dlq_payment_evidence_method}")
    _sn_broken_commitments = F.col("a3_commitments_level") == "broken"
    # Refusal: latest right-party contact was a refusal, with no later promise or
    # arrangement and no later payment (100 AED floor at 180+). Without card
    # transactions (RL) the payment test is Dimension B's any-payment flag.
    _is_180_plus = (
        F.col(f"dlq_payment_any_window_months_{dlq_payment_evidence_method}")
        == _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS
    )
    _payment_followed_refusal = F.when(
        F.coalesce(F.col("payment_evidence_available"), F.lit(0)) == 1,
        F.when(
            _is_180_plus,
            F.coalesce(F.col("refusal_followed_by_payment_min_amount"), F.lit(0)) == 1,
        ).otherwise(F.coalesce(F.col("refusal_followed_by_payment"), F.lit(0)) == 1),
    ).otherwise(F.coalesce(_dlq_any_flag_shipped, F.lit(0)) == 1)
    _sn_refusal = (
        (F.col("last_rpc_disposition") == _DISP_RTP)
        & (F.coalesce(F.col("refusal_followed_by_commitment"), F.lit(0)) == 0)
        & ~_payment_followed_refusal
    )
    _sn_no_response = (
        F.col("contact_dates_n").isNotNull()
        & (F.col("contact_dates_n") >= _TAU_MIN_CONTACT_DATES)
        & (F.coalesce(F.col("rpc_confirmed"), F.lit(0)) == 0)
        & (F.col("commitments_concluded") == 0)
        & (F.coalesce(F.col("ptp_on_record_flag"), F.lit(0)) == 0)
        & (F.coalesce(F.col("arrangement_on_record_flag"), F.lit(0)) == 0)
        & (F.coalesce(_dlq_any_flag_shipped, F.lit(0)) == 0)
    )

    # Priority order (for the rare case more than one fires) is driven by
    # _SB_PRIORITY – the single source of truth, instead of duplicating the
    # order here.
    _sn_conditions = {
        "broken_commitments": _sn_broken_commitments,
        "refusal": _sn_refusal,
        "no_response": _sn_no_response,
    }
    _sn_reason_expr = F.lit(None).cast("string")
    for _reason in reversed(_SB_PRIORITY):
        _sn_reason_expr = F.when(_sn_conditions[_reason], F.lit(_reason)).otherwise(
            _sn_reason_expr
        )
    _sn_reason_expr = F.lit(None).cast("string")
    for _reason in reversed(_SB_PRIORITY):
        _sn_reason_expr = F.when(_sn_conditions[_reason], F.lit(_reason)).otherwise(
            _sn_reason_expr
        )
    return _sn_reason_expr


def _a3_state_col(
    level_a: Column,
    level_b: Column,
    level_c: Column,
    points_total: Column,
    has_strong_negative: Column,
) -> Column:
    """State ladder, checked in order: Unknown, High, Moderate, else Low.

    Unknown: A thin, B none, C no_record and no strong negative (zero evidence, distinct
    from Low – evidence exists and it is bad; a pending PTP alone is still Thin).
    High: points >= HIGH and no strong negative. Moderate: points >= MODERATE and no
    strong negative, or points >= HIGH knocked down one level by a strong negative.
    """
    no_sn = ~has_strong_negative
    is_unknown = (
        (level_a == "thin") & (level_b == "none") & (level_c == "no_record") & no_sn
    )
    return (
        F.when(is_unknown, F.lit(_STATE_UNKNOWN))
        .when((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & no_sn, F.lit(_STATE_HIGH))
        .when(
            ((points_total >= _TAU_A3V2_MODERATE_FROM_POINTS) & no_sn)
            | ((points_total >= _TAU_A3V2_HIGH_FROM_POINTS) & has_strong_negative),
            F.lit(_STATE_MODERATE),
        )
        .otherwise(F.lit(_STATE_LOW))
    )


def _a3_output(df: DataFrame, dlq_method: str, pre_dlq_method: str) -> DataFrame:
    """State, path, confidence, provenance and the typed output select."""
    df = df.withColumn(
        "a3_state_v1",
        _a3_state_col(
            F.col("a3_commitments_level"),
            F.col("a3_dlq_payment_level"),
            F.col("a3_pre_dlq_payment_level"),
            F.col("a3_points_total"),
            F.col("_has_strong_negative"),
        ),
    )
    df = df.withColumn(
        "a3_path",
        F.concat_ws(
            "|",
            F.col("a3_commitments_level"),
            F.col("a3_dlq_payment_level"),
            F.col("a3_pre_dlq_payment_level"),
            F.coalesce(F.col("a3_strong_negative_reason"), F.lit("none")),
        ),
    )
    df = df.withColumn(
        "a3_confidence",
        F.when(F.col("a3_state_v1") == _STATE_HIGH, F.lit(_CONF_HIGH))
        .when(F.col("a3_state_v1") == _STATE_MODERATE, F.lit(_CONF_MODERATE))
        .when(F.col("a3_state_v1") == _STATE_LOW, F.lit(_CONF_LOW))
        .otherwise(F.lit(_CONF_UNKNOWN)),
    )
    # Every non-Unknown state rests on concrete points or a strong negative (observed
    # behaviour). [CONFIRM: simplified]
    df = df.withColumn(
        "a3_provenance",
        F.when(F.col("a3_state_v1") == _STATE_UNKNOWN, F.lit("unknown")).otherwise(
            F.lit("observed")
        ),
    )
    return df.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("t0").cast("date"),
        F.col("a3_state_v1").cast("string"),
        F.col("a3_path").cast("string"),
        F.col("a3_confidence").cast("double"),
        F.col("a3_provenance").cast("string"),
        # Dimension breakdown
        F.col("a3_commitments_level").cast("string"),
        F.col("a3_dlq_payment_level").cast("string"),
        F.col("a3_pre_dlq_payment_level").cast("string"),
        F.col("a3_commitments_points").cast("int"),
        F.col("a3_dlq_payment_points").cast("int"),
        F.col("a3_pre_dlq_payment_points").cast("int"),
        F.col("a3_points_total").cast("int"),
        F.col("a3_strong_negative_reason").cast("string"),
        F.col("a3_dlq_payment_window_months").cast("int"),
        F.col("a3_dlq_payment_any_window_months").cast("int"),
        # Track the shipped methods; the per-method columns below are method-pinned.
        F.col("a3_dlq_payment_qualifying_month_cnt").cast("int"),
        F.col("a3_pre_dlq_months_due_n").cast("int"),
        # Per-method correlation columns (all methods are always computed).
        F.lit(pre_dlq_method).alias("a3_pre_dlq_payment_evidence_method"),
        F.lit(dlq_method).alias("a3_dlq_payment_evidence_method"),
        F.col("a3_dlq_payment_level_single_payment_cycle_count").cast("string"),
        F.col("a3_dlq_payment_qualifying_month_cnt_single_payment_cycle_count").cast(
            "int"
        ),
        F.col("a3_dlq_payment_level_payment_sum_waterfall").cast("string"),
        F.col("a3_dlq_payment_level_dpd_bucket_movement").cast("string"),
        F.col("a3_pre_dlq_payment_level_single_payment_cycle_count").cast("string"),
        F.col("a3_pre_dlq_payment_level_dpd_bucket_movement").cast("string"),
        F.col("a3_dlq_payment_qualifying_month_cnt_payment_sum_waterfall").cast("int"),
        F.col("a3_dlq_payment_qualifying_month_cnt_dpd_bucket_movement").cast("int"),
        F.col("a3_pre_dlq_months_due_n_single_payment_cycle_count").cast("int"),
        F.col("a3_pre_dlq_months_due_n_dpd_bucket_movement").cast("int"),
        # Strong-negative evidence
        F.col("contact_dates_n").cast("int"),
        F.col("rpc_confirmed").cast("int"),
        F.col("last_rpc_disposition").cast("string"),
        F.col("refusal_followed_by_commitment").cast("int"),
        F.col("ptp_on_record_flag").cast("int"),
        F.col("arrangement_on_record_flag").cast("int"),
        F.col("commitments_broken_streak").cast("int"),
        F.current_timestamp().cast("string").alias("computed_at"),
    )


def build_a3_payment_credibility(  # pylint: disable=too-many-positional-arguments,too-many-arguments,too-many-locals
    commitment_signals: DataFrame,
    negative_signals: DataFrame,
    dlq_payment_signals_payment_sum_waterfall: DataFrame = None,
    dlq_payment_signals_single_payment_cycle_count: DataFrame = None,
    dlq_payment_signals_dpd_bucket_movement: DataFrame = None,
    pre_dlq_payment_signals_single_payment_cycle_count: DataFrame = None,
    pre_dlq_payment_signals_dpd_bucket_movement: DataFrame = None,
    dlq_payment_evidence_method: str = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    pre_dlq_payment_evidence_method: str = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
    model_id: str = None,
    persona_end_date: str = None,
) -> DataFrame:
    """Combine Dimensions A, B, C and the strong negatives into a3_state_v1.

    Dimension A's level and points come from commitment_signals; B and C from their
    per-method signal tables. Each method of B (3) and C (2) is scored into suffixed
    columns for cross-checking; dlq_payment_evidence_method and
    pre_dlq_payment_evidence_method (independent switches) pick the shipped one. The
    strong-negative rules (_strong_negative_reason) read Dimension B's shipped
    any-payment flag. [CONFIRM: simplification – acceptable for the shadow columns,
    not independently recomputed per method]

    State (see _a3_state_col): Unknown / High / Moderate / Low. The old waterfall's
    pre-rule guards (window too short, no DCORE data) are deliberately gone; Unknown is
    the single "insufficient evidence" gate.

    Signal inputs default to None for domains without that source; the SELECTED
    approach's input must be supplied (ValueError otherwise). Keep the defaults:
    rl_a3_payment_credibility passes its own pairs.

    Args:
        commitment_signals: crx_cc_a3_commitment_signals – (account_id,
            observation_date) Dimension A level, points and streak.
        negative_signals: crx_cc_a3_strong_negative_signals – same grain; the
            strong-negative evidence.
        dlq_payment_signals_payment_sum_waterfall / _single_payment_cycle_count /
        _dpd_bucket_movement: Dimension B methods, (account_id, observation_date).
        pre_dlq_payment_signals_single_payment_cycle_count / _dpd_bucket_movement:
            Dimension C methods, (account_id, spell_id), joined on (account_id, t0).
        dlq_payment_evidence_method: "single_payment_cycle_count" (default),
            "payment_sum_waterfall" or "dpd_bucket_movement".
        pre_dlq_payment_evidence_method: "single_payment_cycle_count" (default) or
            "dpd_bucket_movement".
        model_id / persona_end_date: when both are given, log the latest month's
            a3_state_v1 distribution.

    Returns:
        (account_id, observation_date) typed A3 output; a3_state_v1 in
        payment_credibility_{high, moderate, low, unknown}.
    """
    dlq_pairs = {
        _METHOD_PAYMENT_SUM_WATERFALL: dlq_payment_signals_payment_sum_waterfall,
        _METHOD_SINGLE_PAYMENT_CYCLE_COUNT: (
            dlq_payment_signals_single_payment_cycle_count
        ),
        _METHOD_DPD_BUCKET_MOVEMENT: dlq_payment_signals_dpd_bucket_movement,
    }
    pre_dlq_pairs = {
        _METHOD_SINGLE_PAYMENT_CYCLE_COUNT: (
            pre_dlq_payment_signals_single_payment_cycle_count
        ),
        _METHOD_DPD_BUCKET_MOVEMENT: pre_dlq_payment_signals_dpd_bucket_movement,
    }
    _validate_method_pairs(
        dlq_pairs,
        pre_dlq_pairs,
        dlq_payment_evidence_method,
        pre_dlq_payment_evidence_method,
    )

    df = commitment_signals.join(
        negative_signals, on=["account_id", "observation_date"], how="left"
    )
    for approach, pair in dlq_pairs.items():
        df = _join_signals_pair(
            df, pair, ["account_id", "observation_date"], _DLQ_PAIR_COLUMNS, approach
        )
    for approach, pair in pre_dlq_pairs.items():
        df = _join_signals_pair(
            df, pair, ["account_id", "t0"], _PRE_DLQ_PAIR_COLUMNS, approach
        )

    df = _score_dimension_b(df, dlq_pairs)
    df = _score_dimension_c(df, pre_dlq_pairs)
    df = _select_shipped_methods(
        df, dlq_payment_evidence_method, pre_dlq_payment_evidence_method
    )
    df = df.withColumn(
        "a3_strong_negative_reason",
        _strong_negative_reason(dlq_payment_evidence_method),
    ).withColumn("_has_strong_negative", F.col("a3_strong_negative_reason").isNotNull())

    output = _a3_output(
        df, dlq_payment_evidence_method, pre_dlq_payment_evidence_method
    )

    _log_a3_stats(output)
    if model_id and persona_end_date:
        log_latest_month(
            output,
            "a3_state_v1",
            f"a3_payment_credibility [{model_id}]",
            persona_end_date,
        )
    return output


def _log_a3_stats(df: DataFrame) -> None:
    """Log state distribution for post-run monitoring."""
    try:
        n_total = df.count()
        state_dist = df.groupBy("a3_state_v1").count().collect()
        path_dist = df.groupBy("a3_path").count().collect()

        LOG.info("build_a3_payment_credibility: total rows = %d", n_total)
        for row in state_dist:
            pct = 100.0 * row["count"] / max(n_total, 1)
            LOG.info(
                "  a3_state_v1=%-35s n=%7d  (%.1f%%)",
                str(row["a3_state_v1"]),
                row["count"],
                pct,
            )
        LOG.info("  path breakdown:")
        for row in path_dist:
            LOG.info("  %-30s n=%d", str(row["a3_path"]), row["count"])
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("_log_a3_stats: stats collection failed – %s", exc)
`````

New:

`````python
"""CC A3 sources: statement cycles with one month's due, and card payments."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, string_key
from ..a3_credibility.constants import (
    BUCKET08_BASELINE_MONTHS,
    CYCLE_MAX_DAYS,
    FLOOR_LOOKBACK_DAYS,
)

_LADDER = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]


def _nonzero(col: str):
    """Way4 writes an empty bucket as 0, not NULL."""
    return F.col(col).isNotNull() & (F.col(col) != 0.0)


def _balance_dues(balance: DataFrame) -> DataFrame:
    """``(account_id, cycle_start, billed_amount, due_amount)`` per statement.

    One month's due: the oldest open bucket 07..01, else the minimum due (bucket 08 is
    Way4's accumulator, not one month). Once only bucket 08 holds money, ``due_amount``
    is the average positive minimum due of the 12 months before that point (D-A3-12);
    ``billed_amount`` (Dimension C) has no such fallback.
    """
    rows = balance.select(
        string_key(balance, "contract_id").alias("account_id"),
        F.col("observation_date").cast("date").alias("cycle_start"),
        "minimum_due",
        F.coalesce(*[F.when(_nonzero(c), F.col(c)) for c in _LADDER]).alias(
            "billed_amount"
        ),
        (
            ~F.coalesce(
                *[F.when(_nonzero(c), F.lit(True)) for c in _LADDER], F.lit(False)
            )
            & _nonzero("overdue_bucket_08")
        ).alias("_stagnated"),
    )
    since = (
        rows.where("_stagnated")
        .groupBy("account_id")
        .agg(F.min("cycle_start").alias("_since"))
    )
    recent = Window.partitionBy("account_id").orderBy(F.col("_month").desc())
    baseline = (
        rows.join(since, "account_id")
        .where(_nonzero("minimum_due") & (F.col("cycle_start") < F.col("_since")))
        .groupBy("account_id", F.trunc("cycle_start", "month").alias("_month"))
        .agg(F.avg("minimum_due").alias("_m"))
        .withColumn("_r", F.row_number().over(recent))
        .where(F.col("_r") <= BUCKET08_BASELINE_MONTHS)
        .groupBy("account_id")
        .agg(F.avg("_m").alias("_baseline"))
    )
    return rows.join(baseline, "account_id", "left").select(
        "account_id",
        "cycle_start",
        "billed_amount",
        F.coalesce(
            "billed_amount", F.when(F.col("_stagnated"), F.col("_baseline"))
        ).alias("due_amount"),
    )


def build_cc_a3_dues(
    billing: DataFrame, balance: DataFrame, history_floor_date: str
) -> DataFrame:
    """A3 dues contract per statement cycle (D-A3-15): ``cycle_start`` = the statement,
    ``cycle_end`` = the next one. A cycle longer than 62 days spans missing statements
    and is dropped, as is one starting more than 35 days before the history floor; the
    latest cycle (no next statement yet) has no result and is left out."""
    require_columns(
        billing,
        ["contract_id", "observation_date", "next_billing_date"],
        "crx_cc_billing",
    )
    require_columns(
        balance,
        ["contract_id", "observation_date", "overdue_bucket_08", *_LADDER],
        "crx_cc_balance",
    )
    start, end = F.col("observation_date").cast("date"), F.col(
        "next_billing_date"
    ).cast("date")
    floor = F.date_sub(F.lit(str(history_floor_date)).cast("date"), FLOOR_LOOKBACK_DAYS)
    cycles = (
        billing.where(
            end.isNotNull()
            & (F.datediff(end, start) <= CYCLE_MAX_DAYS)
            & (start >= floor)
        )
        .select(
            string_key(billing, "contract_id").alias("account_id"),
            start.alias("cycle_start"),
            end.alias("cycle_end"),
        )
        .distinct()
    )
    return cycles.join(
        _balance_dues(balance), on=["account_id", "cycle_start"], how="left"
    )


def build_cc_a3_payments(transactions: DataFrame) -> DataFrame:
    """A3 payments contract: card payments (category ``payment``, no post-block fee
    artefacts), dated by banking date."""
    require_columns(
        transactions,
        [
            "contract_id",
            "observation_date",
            "txn_amount_aed",
            "txn_category",
            "is_post_block_x_fee",
        ],
        "crx_cc_transactions",
    )
    day = F.col("observation_date").cast("date")
    return transactions.where(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        string_key(transactions, "contract_id").alias("account_id"),
        day.alias("pay_from"),
        day.alias("pay_date"),
        F.col("txn_amount_aed").cast("double").alias("amount"),
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py`
action: replace · base sha256 `1ee6f95340ded475b51044325a26186bb492b06b0e6f21399586a9da4899b6a1` · base trailing newline: yes · new sha256 `28e41df045870af6eb8118a9e4d87a8d5928959e4605a600622eb9c2f0e8c493` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T27 – A3 Payment Credibility axis.

# pylint: disable=line-too-long

Nine-node pipeline that derives the A3 payment-credibility axis and emits
the shipped persona column ``a3_state_v1`` at (account_id, observation_date) grain.

Architecture:
    build_a3_commitment_signals          → crx_cc_a3_commitment_signals      (Dimension A: level, points, broken streak)
    build_a3_strong_negative_signals     → crx_cc_a3_strong_negative_signals (strong-negative evidence; rules run in the combiner)
    build_a3_payment_cycles              → crx_cc_a3_payment_cycles          (shared by Dimension B/C)
    build_a3_dlq_payment_signals_payment_sum_waterfall      → crx_cc_a3_dlq_payment_signals_payment_sum_waterfall      (Dimension B, payment_sum_waterfall – shadow)
    build_a3_dlq_payment_signals_single_payment_cycle_count → crx_cc_a3_dlq_payment_signals_single_payment_cycle_count (Dimension B, single_payment_cycle_count – default)
    build_a3_dlq_payment_signals_dpd_bucket_movement        → crx_cc_a3_dlq_payment_signals_dpd_bucket_movement        (Dimension B, dpd_bucket_movement – shadow)
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count → crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count (Dimension C, single_payment_cycle_count – default)
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement        → crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement        (Dimension C, dpd_bucket_movement – shadow)
    build_a3_payment_credibility         → crx_cc_a3_payment_credibility     ← shipped axis

params:cc_a3_history_floor_date (default 2024-01-01, null = off) is the earliest billing
date Dimension B and C read; it is passed to the five Dimension B/C nodes and to
cc_raw_extract's build_cc_acct_windows. crx_cc_spell_table / crx_cc_full_history stay
unfloored (other pipelines read them).

Dimension B and C have INDEPENDENT evidence-method switches (decoupled
2026-10-26 – see build_a3_payment_credibility's docstring, "Why decoupled"):
params:a3_dlq_payment_evidence_method ("single_payment_cycle_count" default,
Dimension B only, 3-way) and params:a3_pre_dlq_payment_evidence_method
("single_payment_cycle_count" default, Dimension C only, 2-way, unchanged). All pairs of
nodes above always run regardless of either switch, so every method's output
can be correlated directly off crx_cc_a3_payment_credibility's per-method
columns (a3_dlq_payment_level_single_payment_cycle_count / _payment_sum_waterfall /
_dpd_bucket_movement for Dimension B; a3_pre_dlq_payment_level_single_payment_cycle_count /
_dpd_bucket_movement for Dimension C).

build_a3_payment_cycles combines the billing-cycle payment attribution and
due-amount resolution once, so build_a3_dlq_payment_signals_payment_sum_waterfall and
build_a3_pre_dlq_payment_signals_single_payment_cycle_count both consume its output instead of each
re-deriving it independently from crx_cc_billing/crx_cc_balance/
crx_cc_transactions. The two dimension nodes have no dependency on each other
and run independently; both feed the final combiner. Both also take cc_spine
as an input – for build_a3_dlq_payment_signals_payment_sum_waterfall it drives the window-length
choice (3mo/6mo); for build_a3_pre_dlq_payment_signals_single_payment_cycle_count it is a population
filter only (scopes crx_cc_spell_table down to spells actually represented in
the current model_id population, avoiding wasted per-spell joins for accounts
with many historical cured spells no longer in scope) – its window is still
purely t0-anchored.

Inputs:
    cc_spine                    Model-id-scoped spine – master grain (account_id, observation_date, cif_id)
    crx_cc_spell_table          T03 – lookup for t0 per spell (joined on account_id + date range)
    dcore_observation_spine     account+agreement mapping (contract_id, observation_date, agreement_id, cif_id)
    dcore_prm_followup_outcomes DCORE contact attempt log (strong negatives)
    dcore_feat_ptp              Aggregated PTP history per agreement
    dcore_feat_settlement       Arrangement / settlement status per agreement
    dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
    dcore_prm_settlement_schedule_instalments
                                Dimension A broken streak (latest concluded instalments);
                                dcore_int_ptp / dcore_int_settlement also feed the strong-negative
                                plan-on-record and Refusal evidence
    crx_cc_transactions         Refusal strong negative (payment after the refusal)
    crx_cc_billing              T04c – billing_date, due_date, next_billing_date
    crx_cc_balance              T04c – minimum_due, overdue_bucket_01..08, total_due
    crx_cc_transactions         T04c – payment transactions, txn_category, is_post_block_x_fee
    crx_cc_full_history         Full, floor-free (account_id, billing_date) → dlq_bucket
                                history – feeds both DPD-bucket-method nodes
                                (build_a3_dlq_payment_signals_dpd_bucket_movement /
                                build_a3_pre_dlq_payment_signals_dpd_bucket_movement) via
                                _signals_common.resolve_dpd_bucket_movement_history

Output:
    crx_cc_a3_payment_credibility – A3 axis for every (account_id, observation_date)
    pair; a3_state_v1 ∈ {payment_credibility_high, payment_credibility_moderate,
    payment_credibility_low, payment_credibility_unknown}.

Run with:
    kedro run --pipeline=crx_cc_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a3_commitment_signals,
    build_a3_strong_negative_signals,
    build_a3_dlq_payment_signals_payment_sum_waterfall,
    build_a3_dlq_payment_signals_single_payment_cycle_count,
    build_a3_dlq_payment_signals_dpd_bucket_movement,
    build_a3_payment_credibility,
    build_a3_payment_cycles,
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count,
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
)

_TAGS = ["crx", "a3", "payment_credibility", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node A3 Payment Credibility pipeline."""
    return Pipeline(
        [
            # ── Dimension A: commitments kept (DCORE PTP / settlement signals) ──
            node(
                func=build_a3_commitment_signals,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "dcore_observation_spine",
                    "dcore_feat_ptp",
                    "dcore_feat_settlement",
                    "dcore_int_ptp",
                    "dcore_prm_promise_instalments",
                    "dcore_int_settlement",
                    "dcore_prm_settlement_schedule_instalments",
                ],
                outputs="crx_cc_a3_commitment_signals",
                name="build_a3_commitment_signals",
                tags=_TAGS,
            ),
            # ── Strong negatives: evidence only; the rules run in the combiner ──
            node(
                func=build_a3_strong_negative_signals,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "dcore_int_ptp",
                    "dcore_int_settlement",
                    "crx_cc_transactions",
                ],
                outputs="crx_cc_a3_strong_negative_signals",
                name="build_a3_strong_negative_signals",
                tags=_TAGS,
            ),
            # ── Shared input for Dimensions B and C: per-cycle payments, due amount
            # and waterfall months ──────────────────────────────────────────────
            node(
                func=build_a3_payment_cycles,
                inputs=[
                    "crx_cc_billing",
                    "crx_cc_balance",
                    "crx_cc_transactions",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_payment_cycles",
                name="build_a3_payment_cycles",
                tags=_TAGS,
            ),
            # ── Dimension B (dlq): payments in delinquency – three approaches, all
            # always computed for cross-checking; the shipped one is chosen by
            # params:a3_dlq_payment_evidence_method (default single_payment_cycle_count).
            node(
                func=build_a3_dlq_payment_signals_payment_sum_waterfall,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
                name="build_a3_dlq_payment_signals_payment_sum_waterfall",
                tags=_TAGS,
            ),
            node(
                func=build_a3_dlq_payment_signals_single_payment_cycle_count,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
                name="build_a3_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_a3_dlq_payment_signals_dpd_bucket_movement,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_full_history",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
                name="build_a3_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Dimension C (pre_dlq): record before delinquency – two approaches,
            # all always computed; the shipped one is chosen by
            # params:a3_pre_dlq_payment_evidence_method (default single_payment_cycle_count).
            node(
                func=build_a3_pre_dlq_payment_signals_single_payment_cycle_count,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                name="build_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_a3_pre_dlq_payment_signals_dpd_bucket_movement,
                inputs=[
                    "crx_cc_a3_payment_cycles",
                    "crx_cc_full_history",
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                name="build_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Combiner: Dimensions A + B + C -> a3_state_v1 ──────────────────
            node(
                func=build_a3_payment_credibility,
                inputs=[
                    "crx_cc_a3_commitment_signals",
                    "crx_cc_a3_strong_negative_signals",
                    "crx_cc_a3_dlq_payment_signals_payment_sum_waterfall",
                    "crx_cc_a3_dlq_payment_signals_single_payment_cycle_count",
                    "crx_cc_a3_dlq_payment_signals_dpd_bucket_movement",
                    "crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                    "crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                    "params:a3_dlq_payment_evidence_method",
                    "params:a3_pre_dlq_payment_evidence_method",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs="crx_cc_a3_payment_credibility",
                name="build_a3_payment_credibility",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: CC A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (statement cycles) and the payments (card payments).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``crx_cc_a4_deterioration``, ``crx_cc_raw_extract`` (billing, balance, transactions)
and the DCORE tables.

    kedro run --pipeline=crx_cc_a3_payment_credibility

TEMPORARY (A3 bundle): ``create_check_pipeline`` (``a3_credibility/check.py``); removed by
the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a3_credibility.check import create_a3_check_pipeline
from ..a3_credibility.pipeline import TAGS, create_a3_pipeline
from .nodes import build_cc_a3_dues, build_cc_a3_payments

DUES = node(
    func=build_cc_a3_dues,
    inputs={
        "billing": "crx_cc_billing",
        "balance": "crx_cc_balance",
        "history_floor_date": "params:cc_a3_history_floor_date",
    },
    outputs="crx_cc_a3_dues",
    name="build_crx_cc_a3_dues",
    tags=TAGS,
)
PAYMENTS = node(
    func=build_cc_a3_payments,
    inputs={"transactions": "crx_cc_transactions"},
    outputs="crx_cc_a3_payments",
    name="build_crx_cc_a3_payments",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a3_payment_credibility", **kwargs
) -> Pipeline:
    """The CC A3 axis written to ``output``."""
    return create_a3_pipeline("cc", output, DUES, PAYMENTS)


def create_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the A3 bundle check for CC."""
    return create_a3_check_pipeline("cc", DUES, PAYMENTS)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_raw_extract/nodes.py`
action: replace · base sha256 `161b053ef74ea67406aa0beb783db4c7f74d4991d29ed5499d5a40f9ef1fc027` · base trailing newline: yes · new sha256 `cfc2c63b81b0d5084c12b45e1ea0516185dffa2f74ecacb123597845ad80f10c` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T04c — CRX CC Raw Extract nodes.

# pylint: disable=too-many-locals
# Rationale: build functions, each with per-account window scoping and schema
# derivations. Logic is self-contained within each function.

Five build functions:

    build_cc_acct_windows : shared per-account [acct_start, acct_end] window,
                            forward edge anchored to cc_spine — computed once
                            here instead of independently inside each of the
                            three consumers below (same cc_spine/
                            crx_cc_spell_table groupBy was previously
                            recomputed 3x per pipeline run).
    build_cc_transactions : window-scoped transaction history with enriched schema
                            (replaces _load_t0_scoped_transactions + prm_cc
                            derivations; consumed by T04b, T05, T06, A3 Dimension B/C)
    build_cc_limits       : T0-scoped credit-limit snapshots pivoted by type_code
                            (replaces prm_limit; consumed by T05)
    build_cc_balance      : window-scoped minimum_due/stmt_balance/total_due billing
                            history (replaces _load_t0_scoped_balance; consumed by
                            T04b, A3 Dimension B/C)
    build_cc_billing      : window-scoped billing-cycle header (billing_date, due_date,
                            next_billing_date, dlq_level_m) — new, consumed by A3
                            Dimension B/C.

build_cc_transactions, build_cc_balance and build_cc_billing all consume
build_cc_acct_windows' output (crx_cc_acct_windows):
    acct_start = add_months(trunc(min(t0), 'month'), -12)
    acct_end   = max(cc_spine.observation_date) for that account, falling back to
                 trunc(max(t0), 'month') when the account has no cc_spine rows.
computed over non-censored spells in crx_cc_spell_table; spine accounts without one
get acct_start = max(params:cc_a3_history_floor_date, min spine obs - 12 months) so A3
has payment cycles for them too (see build_cc_acct_windows). The forward edge is anchored
to cc_spine (not t0) so post-T0 observation dates are retained — needed for A3
Dimension B ("payments in delinquency"), which looks at the window after onset.
This can only add rows relative to the old trunc(max(t0),'month') bound, since
cc_spine.observation_date is always >= t0 for an active account — pre-T0 rows and
values are unaffected.

build_cc_limits keeps the original T0-anchored (no post-T0) window — it is not
needed past onset by any current consumer, so it computes its own window inline
rather than consuming crx_cc_acct_windows.

Quality filter (transactions + limits): primary_entry_idt != 0, org == 100.
Type cast: contract_idt (double → long) at the DDI raw boundary.
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
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def build_cc_acct_windows(
    crx_cc_spell_table: DataFrame,
    cc_spine: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Shared per-account [acct_start, acct_end] window, forward edge anchored to cc_spine.

    Accounts with a non-censored spell (unchanged from the original T0-only window):
    acct_start = add_months(trunc(min(t0), 'month'), -12).
    acct_end   = max(cc_spine.observation_date) for the account; falls back to
    trunc(max(t0), 'month') when the account has no cc_spine rows, so the window
    never shrinks relative to the pre-widening behaviour.

    Spine-only accounts (no non-censored spell: first billing row already delinquent,
    ~60% of the 180+ stock) also get a window, so A3 Dimension B has payment cycles for
    them. acct_start = add_months(trunc(min(cc_spine.observation_date), 'month'), -12),
    never earlier than history_floor_date (params:cc_a3_history_floor_date) when set;
    acct_end = max(cc_spine.observation_date). These windows lie inside the raw-scan
    bound set by the spell accounts, and the other consumers of the extract
    (payment_trajectory, utilisation, departure_signature) reach it only through
    non-censored spells, so the added accounts do not change their results.

    Persisted once and consumed by build_cc_transactions, build_cc_balance and
    build_cc_billing — avoids recomputing the same crx_cc_spell_table/cc_spine
    aggregation three times per pipeline run.

    Args:
        crx_cc_spell_table: Required cols: account_id, t0, t0_censored_flag.
        cc_spine: Required cols: contract_id, observation_date.
        history_floor_date: ISO date or None. Lower bound for spine-only accounts.

    Returns:
        DataFrame with columns (account_id, acct_start, acct_end).
    """
    spell_windows = (
        crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0)
        .groupBy("account_id")
        .agg(
            F.add_months(F.trunc(F.min("t0"), "month"), -12).alias("_spell_start"),
            F.trunc(F.max("t0"), "month").alias("_acct_end_fallback"),
        )
    )

    spine_windows = cc_spine.groupBy(F.col("contract_id").alias("account_id")).agg(
        F.add_months(F.trunc(F.min("observation_date"), "month"), -12).alias(
            "_spine_start"
        ),
        F.max("observation_date").alias("_spine_max_obs"),
    )

    spine_only_start = F.col("_spine_start")
    if history_floor_date:
        spine_only_start = F.greatest(
            F.lit(str(history_floor_date)).cast(DateType()), spine_only_start
        )

    return (
        spell_windows.join(spine_windows, on="account_id", how="full_outer")
        .withColumn("acct_start", F.coalesce(F.col("_spell_start"), spine_only_start))
        .withColumn(
            "acct_end",
            F.coalesce(F.col("_spine_max_obs"), F.col("_acct_end_fallback")),
        )
        .select("account_id", "acct_start", "acct_end")
    )


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped CC transaction history with enriched schema.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for why the forward edge is cc_spine-anchored rather
    than T0-anchored.
    Partition pruning: raw_transaction is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a transaction happens (banking_date) and when it
    lands in its edp_load_date partition. Unlike stg_transaction.build() (whose
    spine, data_spine_contracts_way4, already bakes the lookback into
    observation_date, so it needs no extra buffer), cc_spine has no backward
    lookback at all — crx_cc_acct_windows builds that bound itself, so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.
    Quality filters: primary_entry_idt != 0, org == 100 (same as stg_transaction.build()).
    Replicates prm_cc.build_transaction() derivation logic for txn_category and
    is_international, and stg_transaction.build()'s is_post_block_x_fee sentinel-fee
    derivation (Block-W fee-accrual artifacts that must not be mistaken for real
    post-delinquency payment activity).

    Args:
        raw_transaction:     Raw Way4 transaction table (DDI-backed). Long history.
                             Required cols: primary_entry_idt, org, contract_idt,
                             banking_date, edp_load_date, settl_amount, direction,
                             txn_code, txn_description, add_info, trans_mcc,
                             trans_date, card_idt, service_class.
        crx_cc_acct_windows: T04c — build_cc_acct_windows output.
                             Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), direction (int),
            txn_amount_aed (double), txn_description (string),
            merchant_category_code (int), is_international (int),
            txn_category (string), is_post_block_x_fee (int)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        # Base quality filters (same as stg_transaction.build())
        .filter(F.col("primary_entry_idt") != 0).filter(F.col("org") == 100)
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # Derive txn_category from txn_code (replicates prm_cc.build_transaction logic).
    # Default NULL — unrecognized codes excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # Derive is_international from DOMESTIC flag in add_info JSON
    # (replicates prm_cc.build_transaction logic).
    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # Derive is_post_block_x_fee (replicates stg_transaction.build()'s sentinel-fee
    # derivation) — system-generated fee-accrual events posted after collector
    # Block W, flagged so A3 Dimension B/C never count them as a real payment.
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
    """Extract T0-anchored CC credit-limit snapshots, pivoted by type_code.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Pivot logic replicates stg_limit.build() but uses type_code FIN_LIMIT and
    AVAILABLE only (ADD_LIMIT excluded; not needed for util_ratio computation).

    Deliberately does NOT consume crx_cc_acct_windows — that window's forward
    edge is cc_spine-anchored (extends past T0), which this function does not
    need (see module docstring).

    Args:
        raw_stg_limit:       Raw Way4 limit table (DDI-backed).
                             Required cols: contract_idt, banking_date,
                             type_code, amount.
        crx_cc_spell_table:  T03 output. Used for per-account T0 window.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date),
            credit_limit (double), available_limit (double)
    """
    # Excludes both censored subtypes — see build_cc_transactions Step 0 comment.
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

    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join). This T0-only
    # acct_windows is the one built just above, NOT crx_cc_acct_windows —
    # see module/function docstring for why this window is deliberately kept
    # separate.
    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped
        # Only limit types needed for util_ratio: FIN_LIMIT (credit_limit) + AVAILABLE
        .filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # Pivot — max() is deterministic when multiple rows exist for same key
        # (highest approved limit wins; highest available = least alarming)
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
    """Extract window-scoped minimum_due/stmt_balance/total_due/overdue-bucket history.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge.

    Reuses prm_cc.derive_billing_amounts() and prm_cc.derive_overdue_buckets() —
    the authoritative, production-verified derivations — rather than hand-rolling
    the pivots here, per the standing team decision to never reverse-engineer
    billing amounts from raw stg_balance. raw_stg_balance already carries its own
    native banking_date column (the daily snapshot grain both derive_* functions
    group by) distinct from billing_date — scoping/output use banking_date
    directly rather than aliasing billing_date onto it.

    Way4 stores credit balances as negative; derive_billing_amounts/
    derive_overdue_buckets flip the sign.

    Partition pruning: raw_stg_balance is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a balance snapshot is taken (banking_date) and
    when it lands in its edp_load_date partition. cc_spine has no backward
    lookback at all (unlike data_spine_contracts_way4, which already bakes it
    into observation_date for the credit_card_way4 staging layer), so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.

    Args:
        raw_stg_balance:       Raw Way4 balance table (DDI-backed).
                               Required cols: contract_idt, banking_date,
                               edp_load_date, account_group_id, balance.
        raw_stg_account_group: Dimension table mapping account_group_id →
                               type_code / class_code.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), minimum_due (double),
            stmt_balance (double), total_due (double),
            overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_stg_balance, crx_cc_acct_windows).withColumn(
            "banking_date", F.col("banking_date").cast(DateType())
        )
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
    """Extract window-scoped billing-cycle header: billing_date, due_date,
    next_billing_date, dlq_level_m.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge. This is the
    primitive A3 Dimension B/C's payment-attribution helper
    (cc_a3_payment_credibility._signals_common.attribute_payments_to_billing_cycles)
    is built on.

    next_billing_date = F.lead(billing_date) per contract. A payment belongs to
    the cycle (billing_date, due_date) iff billing_date < banking_date <=
    next_billing_date — NOT billing_date < banking_date <= due_date. due_date is
    ~billing_date+25d while the next statement cuts ~billing_date+30d, leaving a
    ~5-6 day dead zone where late payments (common in practice) would otherwise
    be dropped or misattributed to the wrong cycle — found and fixed in the
    exploratory notebook (notebooks/data_engineering/crx_persona/
    cc_account_payment_profiling.ipynb). next_billing_date is NULL for the most
    recent cycle per contract — treated as open-ended by the attribution helper.

    dlq_level_m is Way4's own per-cycle DLQ bucket (0-9), extracted from the
    add_info KV field's BS_PMT_CYCLE_DUE= key — the identical extraction
    nodes/spine/cc_way4/spine_builders.py uses to build cc_spine's
    dlq_bucket_from_hist, so this is the same ground truth the rest of the
    business already treats as authoritative, not a reconstruction from
    crx_cc_balance's overdue buckets. [CONFIRM]: BS_PMT_CYCLE_DUE is
    sometimes blank/missing in add_info (seen in sample data) — regexp_extract
    then casts to NULL, same as spine_builders.py's own behavior; no fallback
    is applied. Consumed by build_a3_payment_cycles for the DPD-bucket-based
    alternative to Dimension B/C's payment-cycle method (see
    cc_a3_payment_credibility.constants._DLQ_LEVEL_SATURATED).

    Partition pruning: raw_stg_billing is filtered on edp_load_date to the
    global [min(acct_start), max(acct_end)] bound (from crx_cc_acct_windows)
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS (12 months), before the
    per-account join — same rationale as build_cc_transactions/build_cc_balance
    (cc_spine has no backward lookback of its own).

    Args:
        raw_stg_billing:       Raw Way4 billing table (DDI-backed).
                               Required cols: contract_idt, billing_date,
                               edp_load_date, due_date, add_info.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date, = billing_date),
            due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    # Partition prune on edp_load_date before the join (see docstring), then
    # scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
"""CRX CC raw extract nodes: window-scoped Way4 extracts for A3.

# pylint: disable=too-many-locals

    build_cc_acct_windows : per-account [acct_start, acct_end] window from the A3
                            episode anchor (A4) and the observation rows; persisted
                            once, read by the three extracts below.
    build_cc_transactions : window-scoped transaction history with the prm_cc
                            derivations (A3 payments).
    build_cc_limits       : credit-limit snapshots pivoted by type_code, on its own
                            spell-table window (no persona reader at present).
    build_cc_balance      : window-scoped minimum_due / overdue buckets / total_due
                            (A3 dues).
    build_cc_billing      : window-scoped billing-cycle header (billing_date, due_date,
                            next_billing_date) (A3 cycles).

Quality filter (transactions + limits): primary_entry_idt != 0, org == 100.
Type cast: contract_idt (double -> long) at the DDI raw boundary.
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
from enbd_collections.pipelines.crx_persona._dpd_journey.anchor import episode_start
from enbd_collections.pipelines.crx_persona.cc_raw_extract._window_utils import (
    prune_by_edp_load_date,
    scope_to_acct_window,
)


def build_cc_acct_windows(
    crx_cc_obs_base: DataFrame,
    crx_cc_a4_deterioration: DataFrame,
    history_floor_date: str,
) -> DataFrame:
    """Shared per-account [acct_start, acct_end] window for the A3 extracts.

    acct_start covers 12 months plus one cycle before the earliest episode start the
    account's observation rows have (A3 Dimension C, D-A3-2), and at least 13 months
    before its first observation (A3 Dimensions A and B); never before
    history_floor_date minus 35 days (the statement just before the floor).
    acct_end = the account's last observation date.

    Persisted once and consumed by build_cc_transactions, build_cc_balance and
    build_cc_billing.

    Args:
        crx_cc_obs_base: account_id, observation_date, cif_id.
        crx_cc_a4_deterioration: the A4 rows the episode anchor is read from.
        history_floor_date: ISO date (params:cc_a3_history_floor_date).

    Returns:
        DataFrame with columns (account_id, acct_start, acct_end).
    """
    episodes = episode_start(crx_cc_obs_base, crx_cc_a4_deterioration)
    first = (
        crx_cc_obs_base.join(
            episodes, on=["account_id", "observation_date"], how="left"
        )
        .groupBy("account_id")
        .agg(
            F.least(
                F.min("episode_start"), F.trunc(F.min("observation_date"), "month")
            ).alias("_first"),
            F.max("observation_date").alias("acct_end"),
        )
    )
    floor = F.date_sub(F.lit(str(history_floor_date)).cast(DateType()), 35)
    return first.select(
        "account_id",
        F.greatest(F.add_months(F.col("_first"), -13), floor).alias("acct_start"),
        "acct_end",
    )


def _as_contract_windows(acct_windows: DataFrame) -> DataFrame:
    """crx_cc_acct_windows, keyed as contract_idt to join against raw DDI tables."""
    return acct_windows.select(
        F.col("account_id").alias("contract_idt"), "acct_start", "acct_end"
    )


def build_cc_transactions(
    raw_transaction: DataFrame,
    crx_cc_acct_windows: DataFrame,
) -> DataFrame:
    """Extract window-scoped CC transaction history with enriched schema.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows).
    Partition pruning: raw_transaction is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a transaction happens (banking_date) and when it
    lands in its edp_load_date partition. Unlike stg_transaction.build() (whose
    spine, data_spine_contracts_way4, already bakes the lookback into
    observation_date, so it needs no extra buffer), cc_spine has no backward
    lookback at all — crx_cc_acct_windows builds that bound itself, so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.
    Quality filters: primary_entry_idt != 0, org == 100 (same as stg_transaction.build()).
    Replicates prm_cc.build_transaction() derivation logic for txn_category and
    is_international, and stg_transaction.build()'s is_post_block_x_fee sentinel-fee
    derivation (Block-W fee-accrual artifacts that must not be mistaken for real
    post-delinquency payment activity).

    Args:
        raw_transaction:     Raw Way4 transaction table (DDI-backed). Long history.
                             Required cols: primary_entry_idt, org, contract_idt,
                             banking_date, edp_load_date, settl_amount, direction,
                             txn_code, txn_description, add_info, trans_mcc,
                             trans_date, card_idt, service_class.
        crx_cc_acct_windows: T04c — build_cc_acct_windows output.
                             Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), direction (int),
            txn_amount_aed (double), txn_description (string),
            merchant_category_code (int), is_international (int),
            txn_category (string), is_post_block_x_fee (int)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    df = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_transaction, crx_cc_acct_windows)
        # Base quality filters (same as stg_transaction.build())
        .filter(F.col("primary_entry_idt") != 0).filter(F.col("org") == 100)
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
    df = scope_to_acct_window(df, acct_windows, "banking_date")

    # Derive txn_category from txn_code (replicates prm_cc.build_transaction logic).
    # Default NULL — unrecognized codes excluded rather than mislabelled.
    category_expr = F.lit(None).cast("string")
    for cat_name, codes in TXN_CATEGORIES.items():
        category_expr = F.when(
            F.col("txn_code").isin(codes), F.lit(cat_name)
        ).otherwise(category_expr)
    df = df.withColumn("txn_category", category_expr)

    # Derive is_international from DOMESTIC flag in add_info JSON
    # (replicates prm_cc.build_transaction logic).
    # DOMESTIC=N → international (1); DOMESTIC=Y or absent → domestic (0).
    df = df.withColumn(
        "is_international",
        F.when(
            F.regexp_extract(F.col("add_info"), r"DOMESTIC=(.)", 1) == "N", 1
        ).otherwise(0),
    )

    # Derive is_post_block_x_fee (replicates stg_transaction.build()'s sentinel-fee
    # derivation) — system-generated fee-accrual events posted after collector
    # Block W, flagged so A3 Dimension B/C never count them as a real payment.
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
    """Extract T0-anchored CC credit-limit snapshots, pivoted by type_code.

    Scope: per-account window [min(T0) − 12m, max(T0)] from non-censored spells.
    Pivot logic replicates stg_limit.build() but uses type_code FIN_LIMIT and
    AVAILABLE only (ADD_LIMIT excluded; not needed for util_ratio computation).

    Deliberately does NOT consume crx_cc_acct_windows — that window's forward
    edge is cc_spine-anchored (extends past T0), which this function does not
    need (see module docstring).

    Args:
        raw_stg_limit:       Raw Way4 limit table (DDI-backed).
                             Required cols: contract_idt, banking_date,
                             type_code, amount.
        crx_cc_spell_table:  T03 output. Used for per-account T0 window.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date),
            credit_limit (double), available_limit (double)
    """
    # Excludes both censored subtypes — see build_cc_transactions Step 0 comment.
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

    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join). This T0-only
    # acct_windows is the one built just above, NOT crx_cc_acct_windows —
    # see module/function docstring for why this window is deliberately kept
    # separate.
    scoped = scope_to_acct_window(raw_stg_limit, acct_windows, "banking_date")

    pivoted = (
        scoped
        # Only limit types needed for util_ratio: FIN_LIMIT (credit_limit) + AVAILABLE
        .filter(F.col("type_code").isin("FIN_LIMIT", "AVAILABLE"))
        # Pivot — max() is deterministic when multiple rows exist for same key
        # (highest approved limit wins; highest available = least alarming)
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
    """Extract window-scoped minimum_due/stmt_balance/total_due/overdue-bucket history.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge.

    Reuses prm_cc.derive_billing_amounts() and prm_cc.derive_overdue_buckets() —
    the authoritative, production-verified derivations — rather than hand-rolling
    the pivots here, per the standing team decision to never reverse-engineer
    billing amounts from raw stg_balance. raw_stg_balance already carries its own
    native banking_date column (the daily snapshot grain both derive_* functions
    group by) distinct from billing_date — scoping/output use banking_date
    directly rather than aliasing billing_date onto it.

    Way4 stores credit balances as negative; derive_billing_amounts/
    derive_overdue_buckets flip the sign.

    Partition pruning: raw_stg_balance is filtered on edp_load_date — the actual
    Hive partition column — to the global [min(acct_start), max(acct_end)] bound
    (computed from crx_cc_acct_windows) widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS
    (12 months — the project's shared feature-lookback constant, reused here as
    the pruning buffer), *before* the per-account join. The buffer absorbs the
    load-date lag between when a balance snapshot is taken (banking_date) and
    when it lands in its edp_load_date partition. cc_spine has no backward
    lookback at all (unlike data_spine_contracts_way4, which already bakes it
    into observation_date for the credit_card_way4 staging layer), so this
    buffer is still needed here. This lets Spark/Hive skip partitions outside
    the bound instead of scanning the full table. The subsequent per-account
    filter (on banking_date vs. acct_start/acct_end) still narrows further — the
    global bound is only a superset of each account's own window.

    Args:
        raw_stg_balance:       Raw Way4 balance table (DDI-backed).
                               Required cols: contract_idt, banking_date,
                               edp_load_date, account_group_id, balance.
        raw_stg_account_group: Dimension table mapping account_group_id →
                               type_code / class_code.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date), minimum_due (double),
            stmt_balance (double), total_due (double),
            overdue_bucket_01 (double) .. overdue_bucket_08 (double)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    scoped_balance = (
        # Partition prune on edp_load_date before the join (see docstring).
        prune_by_edp_load_date(raw_stg_balance, crx_cc_acct_windows).withColumn(
            "banking_date", F.col("banking_date").cast(DateType())
        )
    )
    # Scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
    """Extract window-scoped billing-cycle header: billing_date, due_date,
    next_billing_date, dlq_level_m.

    Scope: per-account window from crx_cc_acct_windows (build_cc_acct_windows) —
    see module docstring for the cc_spine-anchored forward edge. This is the
    primitive A3 Dimension B/C's payment-attribution helper
    (cc_a3_payment_credibility._signals_common.attribute_payments_to_billing_cycles)
    is built on.

    next_billing_date = F.lead(billing_date) per contract. A payment belongs to
    the cycle (billing_date, due_date) iff billing_date < banking_date <=
    next_billing_date — NOT billing_date < banking_date <= due_date. due_date is
    ~billing_date+25d while the next statement cuts ~billing_date+30d, leaving a
    ~5-6 day dead zone where late payments (common in practice) would otherwise
    be dropped or misattributed to the wrong cycle — found and fixed in the
    exploratory notebook (notebooks/data_engineering/crx_persona/
    cc_account_payment_profiling.ipynb). next_billing_date is NULL for the most
    recent cycle per contract — treated as open-ended by the attribution helper.

    dlq_level_m is Way4's own per-cycle DLQ bucket (0-9), extracted from the
    add_info KV field's BS_PMT_CYCLE_DUE= key — the identical extraction
    nodes/spine/cc_way4/spine_builders.py uses to build cc_spine's
    dlq_bucket_from_hist, so this is the same ground truth the rest of the
    business already treats as authoritative, not a reconstruction from
    crx_cc_balance's overdue buckets. [CONFIRM]: BS_PMT_CYCLE_DUE is
    sometimes blank/missing in add_info (seen in sample data) — regexp_extract
    then casts to NULL, same as spine_builders.py's own behavior; no fallback
    is applied. Consumed by build_a3_payment_cycles for the DPD-bucket-based
    alternative to Dimension B/C's payment-cycle method (see
    cc_a3_payment_credibility.constants._DLQ_LEVEL_SATURATED).

    Partition pruning: raw_stg_billing is filtered on edp_load_date to the
    global [min(acct_start), max(acct_end)] bound (from crx_cc_acct_windows)
    widened by +/-EDP_LOAD_DATE_BUFFER_MONTHS (12 months), before the
    per-account join — same rationale as build_cc_transactions/build_cc_balance
    (cc_spine has no backward lookback of its own).

    Args:
        raw_stg_billing:       Raw Way4 billing table (DDI-backed).
                               Required cols: contract_idt, billing_date,
                               edp_load_date, due_date, add_info.
        crx_cc_acct_windows:   T04c — build_cc_acct_windows output.
                               Required cols: account_id, acct_start, acct_end.

    Returns:
        DataFrame with schema::

            contract_id (long), observation_date (date, = billing_date),
            due_date (date), next_billing_date (date), dlq_level_m (int, nullable)
    """
    acct_windows = _as_contract_windows(crx_cc_acct_windows)

    # Partition prune on edp_load_date before the join (see docstring), then
    # scope + date filter via inner join on per-account windows (also casts
    # raw double contract_idt key to long before the join).
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
action: replace · base sha256 `c279788b74313a7d3ce5ecd36fba9e04d063a159745499ddba9c976ea006f38f` · base trailing newline: yes · new sha256 `26866762bbd0f8125a23ea96b0c9d1f91a080d5e38004237d4ed11d41b6122b1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T04c — CRX CC raw DDI extract (5 intermediate datasets).

Promotes the T0-scoped raw extracts (formerly private helpers inside T04b) to
persisted intermediate catalog datasets so that T04b, T05, T06 and A3 Dimension
B/C all consume the same pre-scoped, pre-enriched tables instead of re-reading
prm_* or raw_* directly.

build_cc_acct_windows computes the shared per-account [acct_start, acct_end]
window once; build_cc_transactions, build_cc_balance and build_cc_billing all
consume its output (crx_cc_acct_windows) instead of each independently
recomputing the same crx_cc_spell_table/cc_spine aggregation. The window's
forward edge is cc_spine-anchored (not just T0) — needed by A3 Dimension B,
which looks at payment behaviour after onset. build_cc_billing is new,
providing the billing-cycle header (billing_date, due_date, next_billing_date)
A3 Dimension B/C's payment-attribution helper is built on. build_cc_limits
keeps its own self-contained T0-only window (see nodes.py docstring) and does
not consume crx_cc_acct_windows.

build_cc_acct_windows also takes params:cc_a3_history_floor_date: spine accounts
without a non-censored spell get a window starting no earlier than it, so A3 has
payment cycles for them (the other consumers are unaffected, see nodes.py).

Run with:
    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_cc_acct_windows,
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Five-node pipeline: build window-scoped CC raw extract intermediates."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs=[
                    "crx_cc_spell_table",
                    "cc_spine",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs=["raw_transaction", "crx_cc_acct_windows"],
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs=["raw_stg_limit", "crx_cc_spell_table"],
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs=[
                    "raw_stg_balance",
                    "raw_stg_account_group",
                    "crx_cc_acct_windows",
                ],
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs=["raw_stg_billing", "crx_cc_acct_windows"],
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
"""Kedro pipeline: CRX CC raw DDI extract (5 intermediate datasets) for A3.

build_cc_acct_windows reads the obs base and A4 (the episode anchor), so this runs
after crx_cc_a4_deterioration and before crx_cc_a3_payment_credibility. The three A3
extracts (transactions, balance, billing) read its window; build_cc_limits keeps its own
spell-table window.

Run with:
    kedro run --pipeline=crx_cc_raw_extract
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_cc_acct_windows,
    build_cc_balance,
    build_cc_billing,
    build_cc_limits,
    build_cc_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Five-node pipeline: build window-scoped CC raw extract intermediates."""
    return Pipeline(
        [
            node(
                func=build_cc_acct_windows,
                inputs=[
                    "crx_cc_obs_base",
                    "crx_cc_a4_deterioration",
                    "params:cc_a3_history_floor_date",
                ],
                outputs="crx_cc_acct_windows",
                name="build_crx_cc_acct_windows",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_transactions,
                inputs=["raw_transaction", "crx_cc_acct_windows"],
                outputs="crx_cc_transactions",
                name="build_crx_cc_transactions",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_limits,
                inputs=["raw_stg_limit", "crx_cc_spell_table"],
                outputs="crx_cc_limits",
                name="build_crx_cc_limits",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_balance,
                inputs=[
                    "raw_stg_balance",
                    "raw_stg_account_group",
                    "crx_cc_acct_windows",
                ],
                outputs="crx_cc_balance",
                name="build_crx_cc_balance",
                tags=["crx", "t04c"],
            ),
            node(
                func=build_cc_billing,
                inputs=["raw_stg_billing", "crx_cc_acct_windows"],
                outputs="crx_cc_billing",
                name="build_crx_cc_billing",
                tags=["crx", "t04c"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/__init__.py`
action: replace · base sha256 `1cc2b913ad776572263e59484eb8185f946f1e53093ca253d12ef89b7e3a09ea` · base trailing newline: yes · new sha256 `bce0a6d599f3fc73ca3ccc3b207291a0723953e3b136fbbb23cdd161c0f2dc5a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A3-1 A3 Payment Credibility axis for Retail Loans."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/nodes.py`
action: replace · base sha256 `07c3f431221a2509d423870a96f489d7d1e40d61f02728eb28c77dcff10ff5bb` · base trailing newline: yes · new sha256 `eed7ff91aed7fccf276cae34d64d88ab550029ed9e1aaef7044e1e715df75844` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A3 Payment Credibility axis – RL-specific adapter nodes (RL-A3-1).

Nine-node pipeline that mirrors cc_a3_payment_credibility's structure (same
approach names, same shipped defaults, same window semantics), reusing CC logic
where possible and rebuilding only what is hardcoded to CC's statement ladder:

    build_rl_a3_commitment_signals                                 [Dim A]
    build_rl_a3_strong_negative_signals                            [strong-negative evidence]
    build_rl_a3_dlq_cycles                                         [shared monthly ledger rows]
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall          [Dim B]
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count     [Dim B, shipped]
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement            [Dim B]
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count [Dim C, shipped]
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement        [Dim C]
    build_rl_a3_payment_credibility                                [CC combiner, wrapped]

Naming: "dlq" = Dimension B (payments while delinquent), "pre_dlq" = Dimension
C (record before delinquency); the suffix is the approach.
  - payment_sum_waterfall (Dim B): floor(sum of the window's cash / EMI) – one
    large payment can credit several months, RL has no bucket ladder to walk,
    so this is a division rather than CC's waterfall walk; the tag is kept so
    the shared combiner's shadow columns line up with CC's.
  - single_payment_cycle_count: each month judged on its own (Dim B: cash >=
    100% of EMI, Dim B and Dim C), counting qualifying months.
  - dpd_bucket_movement: payment inferred from month-over-month bucket movement.

Each node's output dataset is the function name with "build_" replaced by
"crx_" (see pipeline.py).

Timing: RL's total_paid is the cash received during the month and the bucket is
the month-end state, so a month's cash and bucket result sit on the same row.
Dimension B uses result months (window_start, observation_date]; Dimension C
uses months [window_start, t0).

Node 1 difference from CC: crx_rl_a4_spine already carries (account_id,
observation_date, spell_id, t0, cif_id) resolved by RL-A4-2, so no separate
spell-table lookup is needed. rl_spine_as_cc_shim() reshapes it into the
(cc_spine, spell_table) contract build_a3_commitment_signals and
build_a3_strong_negative_signals expect, so the CC functions run unchanged (R14). The
strong-negative node also applies a 24-month partition floor to
dcore_prm_followup_outcomes (performance guard, not a logic change).

The last node wraps CC's build_a3_payment_credibility (never modified) and pins
both shipped approaches to single_payment_cycle_count, CC's defaults.
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.crx_persona._spine_utils import rl_spine_as_cc_shim
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.nodes import (
    build_a3_commitment_signals,
    build_a3_payment_credibility,
    build_a3_strong_negative_signals,
)
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility._signals_common import (
    aggregate_dlq_window,
    aggregate_pre_dlq_window,
    payment_meets_floor,
    resolve_pre_dlq_spell_window,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility._signals_common import (
    resolve_rl_dlq_payment_window,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility.constants import (
    _DLQ_LEVEL_SATURATED_RL,
    _DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    _PRE_DLQ_NOT_DELINQUENT_MAX_RL,
    _PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    _TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE,
    _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP,
    _TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE,
    _TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
)

LOG = logging.getLogger(__name__)

__all__ = [
    "build_rl_a3_commitment_signals",
    "build_rl_a3_strong_negative_signals",
    "build_rl_a3_dlq_cycles",
    "build_rl_a3_dlq_payment_signals_payment_sum_waterfall",
    "build_rl_a3_dlq_payment_signals_single_payment_cycle_count",
    "build_rl_a3_dlq_payment_signals_dpd_bucket_movement",
    "build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
    "build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
    "build_rl_a3_payment_credibility",
]


# ── Node 1: build_rl_a3_commitment_signals ───────────────────────────────


def build_rl_a3_commitment_signals(  # pylint: disable=too-many-positional-arguments
    crx_rl_a4_spine: DataFrame,
    dcore_observation_spine: DataFrame,
    feat_ptp: DataFrame,
    feat_settlement: DataFrame,
    int_ptp: DataFrame = None,
    ptp_instalments: DataFrame = None,
    int_settlement: DataFrame = None,
    settlement_instalments: DataFrame = None,
) -> DataFrame:
    """Dimension A (commitments kept) for RL. Thin wrapper over CC's node.

    Reshapes crx_rl_a4_spine into the (cc_spine, spell_table) shim pair via
    rl_spine_as_cc_shim() and delegates to build_a3_commitment_signals (R14 reuse) –
    identical PTP / settlement counts, pooled broken streak and level / points as CC.

    Args:
        crx_rl_a4_spine: RL spine at (account_id, observation_date) grain,
            already windowed to the persona date range and carrying
            spell_id / t0 / cif_id (RL-A4-2 Node 2 output).
        dcore_observation_spine: RL-scoped DCORE account→agreement mapping
            (RL-D5). Required cols: account_id, observation_date, agreement_id,
            cif_id.
        feat_ptp: dcore_feat_ptp – PTP history per agreement.
        feat_settlement: dcore_feat_settlement – settlement/arrangement
            history per agreement.
        int_ptp / ptp_instalments / int_settlement / settlement_instalments:
            dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments – Dimension A broken streak.

    Returns:
        crx_rl_a3_commitment_signals – same schema as
        crx_cc_a3_commitment_signals.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    return build_a3_commitment_signals(
        cc_spine=cc_spine_shim,
        spell_table=spell_table_shim,
        observation_spine=dcore_observation_spine,
        feat_ptp=feat_ptp,
        feat_settlement=feat_settlement,
        int_ptp=int_ptp,
        ptp_instalments=ptp_instalments,
        int_settlement=int_settlement,
        settlement_instalments=settlement_instalments,
    )


# ── Node 1b: build_rl_a3_strong_negative_signals ─────────────────────────


def build_rl_a3_strong_negative_signals(  # pylint: disable=too-many-positional-arguments
    crx_rl_a4_spine: DataFrame,
    dcore_observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    crx_persona: dict,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
) -> DataFrame:
    """Strong-negative evidence for RL. Thin wrapper with a 24m partition floor.

    Same shim as build_rl_a3_commitment_signals, delegating to CC's
    build_a3_strong_negative_signals. RL has no card transactions, so the Refusal rule
    keeps Dimension B's any-payment flag as its payment test.

    Args:
        crx_rl_a4_spine / dcore_observation_spine / int_ptp / int_settlement: as
            build_rl_a3_commitment_signals.
        followup_outcomes: dcore_prm_followup_outcomes – DCORE contact attempt
            log. Required cols: agreement_id, action_ts, action_code,
            result_category, result_name.
        crx_persona: Persona param dict with persona_start_date /
            persona_end_date.

    Returns:
        crx_rl_a3_strong_negative_signals – same schema as
        crx_cc_a3_strong_negative_signals.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)

    persona_start_date = crx_persona["persona_start_date"]
    dcore_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=24)
    ).isoformat()
    followup_filtered = followup_outcomes.filter(
        F.col("action_ts").cast("date") >= F.lit(dcore_floor)
    )
    LOG.info(
        "build_rl_a3_strong_negative_signals [%s → %s]: "
        "dcore_prm_followup_outcomes floored at %s",
        persona_start_date,
        crx_persona["persona_end_date"],
        dcore_floor,
    )

    return build_a3_strong_negative_signals(
        cc_spine=cc_spine_shim,
        spell_table=spell_table_shim,
        observation_spine=dcore_observation_spine,
        followup_outcomes=followup_filtered,
        int_ptp=int_ptp,
        int_settlement=int_settlement,
    )


# ── Node 2: build_rl_a3_dlq_cycles ───────────────────────────────────────


def _rl_string_key(df: DataFrame, col: str = "account_id"):
    """Double/decimal-safe account_id -> string cast, replicated locally
    rather than importing rl_full_history.nodes' private _string_key helper
    (a double/decimal account_id cast straight to string gives
    "1.23456789E8" and silently zeroes a leftsemi join – the same trap
    build_rl_full_history already guards against)."""
    dtype = df.schema[col].dataType
    c = F.col(col)
    if isinstance(dtype, (T.DoubleType, T.FloatType, T.DecimalType)):
        c = c.cast("long")
    return F.trim(c.cast("string"))


def build_rl_a3_dlq_cycles(
    crx_rl_full_history: DataFrame,
    int_loan_master: DataFrame,
    rl_spine: DataFrame,
) -> DataFrame:
    """Per-month ledger rows shared by every RL Dimension B/C approach – the
    RL counterpart of CC's build_a3_payment_cycles (bucket history + EMI due
    + cash received), without a billing-cycle ladder (RL has none).

    One row per account per month-end. The month-end row M carries both the
    month's cash (total_paid = payment_amount_mtd, cash received during M) and
    the month-end bucket, so bucket(M-1) -> bucket(M) is explained by the
    cash in M: payment and bucket result sit on the SAME row. (CC needs a
    result-statement re-key because its payment belongs to the cycle that
    OPENS at the statement; RL does not.) [CONFIRM] – see the validation
    snippet's cash-explains-bucket-change check.

    dlq_level_m is read straight from crx_rl_full_history.dlq_bucket (0-7).
    dlq_level_prev_m is the previous month's bucket, computed over the FULL
    unwindowed history so the first in-scope month still has a real previous
    month (same reason CC sources its lag from crx_cc_full_history).

    monthly_emi_due and total_paid come from int_loan_master (scoped to
    rl_spine through a broadcast leftsemi, with a double/decimal-safe
    account_id cast – see _rl_string_key). monthly_emi_asof is monthly_emi_due
    forward-filled to the latest non-null value up to that month – the EMI a
    month's payment is judged against when its own row is NULL, and robust to
    the rare EMI change on restructure.

    Args:
        crx_rl_full_history: RL-B1 – (account_id, month_end_date, dlq_bucket,
            ...), full unwindowed history, already scoped to rl_spine.
        int_loan_master: monthly loan snapshots – account_id, observation_date,
            monthly_emi_due, total_paid.
        rl_spine: model-namespaced RL spine – used only to scope
            int_loan_master the same way build_rl_full_history already scopes
            crx_rl_full_history itself.

    Returns:
        DataFrame at grain (account_id, billing_date) with: dlq_level_m (int),
        dlq_level_prev_m (int, NULL on an account's first month),
        monthly_emi_due (double, nullable), monthly_emi_asof (double,
        nullable), total_paid (double, nullable).
    """
    spine_keys = rl_spine.select(
        _rl_string_key(rl_spine).alias("account_id")
    ).distinct()
    emi = int_loan_master.join(
        F.broadcast(spine_keys), on="account_id", how="leftsemi"
    ).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("monthly_emi_due").cast("double"),
        F.col("total_paid").cast("double"),
    )

    history = crx_rl_full_history.select(
        F.col("account_id").cast("string"),
        F.col("month_end_date").alias("billing_date"),
        F.col("dlq_bucket").cast("int").alias("dlq_level_m"),
    )

    _w_account_history = Window.partitionBy("account_id").orderBy("billing_date")
    with_lag = history.withColumn(
        "dlq_level_prev_m", F.lag("dlq_level_m").over(_w_account_history)
    )

    joined = (
        with_lag.alias("h")
        .join(
            emi.alias("e"),
            (F.col("h.account_id") == F.col("e.account_id"))
            & (F.col("h.billing_date") == F.col("e.observation_date")),
            "left",
        )
        .select(
            F.col("h.account_id").alias("account_id"),
            F.col("h.billing_date").alias("billing_date"),
            F.col("h.dlq_level_m").alias("dlq_level_m"),
            F.col("h.dlq_level_prev_m").alias("dlq_level_prev_m"),
            F.col("e.monthly_emi_due").alias("monthly_emi_due"),
            F.col("e.total_paid").alias("total_paid"),
        )
    )

    _w_asof = (
        Window.partitionBy("account_id")
        .orderBy("billing_date")
        .rowsBetween(Window.unboundedPreceding, 0)
    )
    return joined.withColumn(
        "monthly_emi_asof",
        F.last(F.col("monthly_emi_due"), ignorenulls=True).over(_w_asof),
    )


# ── Dimension B shared helpers ───────────────────────────────────────────


def _rl_dlq_payment_level_and_points(agg: DataFrame) -> DataFrame:
    """Add dlq_payment_level (regular/some/none) + dlq_payment_points (2/1/0)
    – shared ladder for ALL Dimension B approaches (payment_sum_waterfall,
    single_payment_cycle_count, dpd_bucket_movement),
    mirroring CC's _dlq_payment_level_and_points (cc_a3_payment_credibility
    .nodes) which CC itself factored out for the identical reason: both of
    its methods need the same window-length-dependent "regular" thresholds,
    only the per-cycle "did they pay" primitive differs. Expects agg to
    already have dlq_payment_window_months, dlq_payment_qualifying_month_cnt,
    dlq_payment_any_flag."""
    result = agg.withColumn(
        "dlq_payment_level",
        F.when(
            (
                (
                    F.col("dlq_payment_window_months")
                    == _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP
                )
            )
            | (
                (
                    F.col("dlq_payment_window_months")
                    != _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP
                )
                & (
                    F.col("dlq_payment_qualifying_month_cnt")
                    >= _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID
                )
            ),
            F.lit("regular"),
        )
        .when(F.col("dlq_payment_any_flag") == 1, F.lit("some"))
        .otherwise(F.lit("none"))
    )
    return result.withColumn(
        "dlq_payment_points",
        F.when(F.col("dlq_payment_level") == "regular", F.lit(2))
        .when(F.col("dlq_payment_level") == "some", F.lit(1))
        .otherwise(F.lit(0)),
    )


def _rl_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Final select/cast shared by all three Dimension B approaches –
    identical output contract by design (each feeds the matching
    dlq_payment_signals_<approach> argument of
    build_rl_a3_payment_credibility)."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("t0").cast("date"),
        F.col("dlq_payment_window_months").cast("int"),
        F.col("dlq_payment_any_window_months").cast("int"),
        F.col("dlq_payment_qualifying_month_cnt").cast("int"),
        F.col("dlq_payment_any_flag").cast("int"),
        F.col("dlq_payment_level").cast("string"),
        F.col("dlq_payment_points").cast("int"),
    )


# ── Dimension B approaches ───────────────────────────────────────────────
# All three use the same window – result months (window_start, observation_date]
# on the month-end row – because RL's cash and bucket for month M sit on row M.
# The month at t0 is excluded (the cash that failed to stop onset); the
# observation month is included (known at the observation).


def build_rl_a3_dlq_payment_signals_payment_sum_waterfall(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, payment_sum_waterfall approach – is money coming in now?

    RL's counterpart of CC's build_a3_dlq_payment_signals_payment_sum_waterfall
    (same tag, so the shared combiner's columns line up). RL has no bucket
    ladder to walk: monthly_emi_due is a FIXED contractual amount, so "how
    many EMI-months did the payments cover" reduces to division:

        dlq_payment_qualifying_month_cnt = floor(sum(total_paid over window) / emi)

    emi is the account's monthly_emi_asof at observation_date (forward-filled,
    resolved before any groupBy – an F.last() inside a groupBy is not
    deterministic). Like CC's waterfall, one large payment can credit several
    months. any_flag = any cash in the "any payment" window (12 months in the
    deep band, otherwise the regular window).

    Window: months in (window_start, observation_date], window length from
    resolve_rl_dlq_payment_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        CC's Dimension B builders: t0, dlq_payment_window_months,
        dlq_payment_qualifying_month_cnt, dlq_payment_any_flag,
        dlq_payment_level (regular/some/none), dlq_payment_points (2/1/0).
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    emi_at_obs = crx_rl_a3_dlq_cycles.select(
        F.col("account_id"),
        F.col("billing_date").alias("observation_date"),
        F.col("monthly_emi_asof").alias("_emi_amount"),
    )

    joined = spine_with_window.alias("s").join(
        crx_rl_a3_dlq_cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col("c.billing_date") > F.col("s._any_window_start"))
        & (F.col("c.billing_date") <= F.col("s.observation_date")),
        "left",
    )

    # One join over the wider "any payment" window; the EMI-month count only sums the
    # "Regular" window (billing_date > _window_start). In the deep band, months with cash
    # below the minimum (100 AED) are ignored in both sums.
    _counted_cash = payment_meets_floor(F.col("c.total_paid"))
    agg = joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.observation_date").alias("observation_date"),
        F.col("s.t0").alias("t0"),
        F.col("s._window_months").alias("dlq_payment_window_months"),
        F.col("s._any_window_months").alias("dlq_payment_any_window_months"),
    ).agg(
        F.coalesce(
            F.sum(
                F.when(
                    (F.col("c.billing_date") > F.col("s._window_start"))
                    & _counted_cash,
                    F.col("c.total_paid"),
                )
            ),
            F.lit(0.0),
        ).alias("_window_payment_sum"),
        F.coalesce(
            F.sum(F.when(_counted_cash, F.col("c.total_paid"))), F.lit(0.0)
        ).alias("_any_window_payment_sum"),
    )

    agg = agg.join(emi_at_obs, on=["account_id", "observation_date"], how="left")

    agg = agg.withColumn(
        "dlq_payment_qualifying_month_cnt",
        F.when(
            F.col("_emi_amount").isNotNull() & (F.col("_emi_amount") > 0),
            F.floor(F.col("_window_payment_sum") / F.col("_emi_amount")),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    ).withColumn(
        "dlq_payment_any_flag",
        (F.col("_any_window_payment_sum") > 0).cast("int"),
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


def build_rl_a3_dlq_payment_signals_single_payment_cycle_count(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, single_payment_cycle_count approach (RL default).

    RL counterpart of CC's build_a3_dlq_payment_signals_single_payment_cycle_count:
    each month is judged on its own – total_paid >= 100% of that month's EMI
    (_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE x monthly_emi_asof) – and the
    window count is the number of qualifying months. No partial credit and no
    multi-month credit from one large payment (unlike payment_sum_waterfall).
    Note total_paid is the month's cash total, not one transaction. any_flag =
    any cash in the "any payment" window (12 months in the deep band). A month with no
    EMI cannot qualify.

    Window: months in (window_start, observation_date]; the window join and
    aggregation are CC's shared aggregate_dlq_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        build_rl_a3_dlq_payment_signals_payment_sum_waterfall.
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    # Required cash = max(100% of the month's EMI, the deep-band minimum of 100 AED).
    _required_cash = F.greatest(
        F.col("c.monthly_emi_asof") * F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE),
        F.col("s._min_payment_aed"),
    )
    _is_qualifying_cycle = F.when(
        F.col("c.monthly_emi_asof").isNotNull() & (F.col("c.monthly_emi_asof") > 0),
        F.coalesce(F.col("c.total_paid"), F.lit(0.0)) >= _required_cash,
    ).otherwise(F.lit(False))

    agg = aggregate_dlq_window(
        spine_with_window,
        crx_rl_a3_dlq_cycles,
        "billing_date",
        _is_qualifying_cycle.cast("int"),
        (F.col("c.total_paid") > 0) & payment_meets_floor(F.col("c.total_paid")),
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


def build_rl_a3_dlq_payment_signals_dpd_bucket_movement(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension B, dpd_bucket_movement approach – RL counterpart of CC's
    build_a3_dlq_payment_signals_dpd_bucket_movement.

    Infers payment from month-over-month bucket movement. For month M, the
    month-end bucket already reflects the cash received in M, so M's bucket is
    compared with the PREVIOUS month's (dlq_level_prev_m, a lag):
        no previous month                                   -> 0
        bucket improved (level < prev)                      -> prev - level (raw delta)
        flat, nonzero, below the cap                        -> 1
        flat at zero                                        -> 0 (nothing delinquent)
        flat at the cap (_DLQ_LEVEL_SATURATED_RL = 7)       -> 0 (no RL ladder to
            fall back on; ~all arrivals at RL bucket 7 coincide with
            charge-off/write-off, after which no real payments occur)
        worsened                                            -> 0
    RL credits the RAW delta on an improvement (no CC-style "+1 unless cured")
    – [CONFIRM], see constants.py. Window and aggregation are the same as the
    other Dimension B approaches.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine (observation grid, spell_id/t0).

    Returns:
        DataFrame at grain (account_id, observation_date) – same contract as
        build_rl_a3_dlq_payment_signals_payment_sum_waterfall.
    """
    spine_with_window = resolve_rl_dlq_payment_window(
        crx_rl_a4_spine, crx_rl_a3_dlq_cycles
    )

    _dlq_levels_improved = F.col("dlq_level_prev_m") - F.col("dlq_level_m")
    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_qualifying_months_m",
        F.when(F.col("dlq_level_prev_m").isNull(), F.lit(0))
        .when(_dlq_levels_improved > 0, _dlq_levels_improved)
        .when(
            (F.col("dlq_level_m") == F.col("dlq_level_prev_m"))
            & (F.col("dlq_level_m") < _DLQ_LEVEL_SATURATED_RL)
            & (F.col("dlq_level_m") != 0),
            F.lit(1),
        )
        .otherwise(F.lit(0)),
    )

    agg = aggregate_dlq_window(
        spine_with_window,
        cycles_with_evidence,
        "billing_date",
        F.col("c._qualifying_months_m"),
        F.col("c._qualifying_months_m") >= 1,
    )

    result = _rl_dlq_payment_level_and_points(agg)
    return _rl_dlq_payment_signals_output(result)


# ── Dimension C approaches ───────────────────────────────────────────────
# Window: the 12 months strictly before t0 (CC's resolve_pre_dlq_spell_window,
# reused through rl_spine_as_cc_shim). Month M's cash and bucket sit on row M,
# so both approaches judge row M: cash vs EMI, or bucket(M) back at zero.


def _rl_pre_dlq_payment_signals_output(result: DataFrame) -> DataFrame:
    """Final select/cast shared by both Dimension C approaches (identical
    output contract by design)."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("pre_dlq_months_due_n").cast("int"),
        F.col("pre_dlq_months_paid_as_billed_n").cast("int"),
        F.col("pre_dlq_paid_as_billed_share").cast("double"),
    )


def build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension C, single_payment_cycle_count approach (RL default) –
    record before delinquency.

    RL counterpart of CC's
    build_a3_pre_dlq_payment_signals_single_payment_cycle_count: a month is
    "paid as billed" when total_paid >= _TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE
    (100%) of monthly_emi_due; a month "has due" when monthly_emi_due is not
    null and > 0. Window: months in [window_start, t0). The window join and
    share derivation are CC's shared aggregate_pre_dlq_window.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine – resolves spell_id/t0 and limits the
            spells to the current population.

    Returns:
        DataFrame at grain (account_id, spell_id): t0, pre_dlq_months_due_n,
        pre_dlq_months_paid_as_billed_n, pre_dlq_paid_as_billed_share (NULL
        when pre_dlq_months_due_n is below _TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE –
        the "no_record" condition).
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spells = resolve_pre_dlq_spell_window(cc_spine_shim, spell_table_shim)

    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_has_due",
        F.col("monthly_emi_due").isNotNull() & (F.col("monthly_emi_due") > 0),
    ).withColumn(
        "_paid_as_billed",
        F.col("total_paid").isNotNull()
        & (
            F.col("total_paid")
            >= F.col("monthly_emi_due") * F.lit(_TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE)
        ),
    )

    result = aggregate_pre_dlq_window(
        spells,
        cycles_with_evidence,
        "_paid_as_billed",
        evidence_date_col="billing_date",
        min_months_due=_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    )
    return _rl_pre_dlq_payment_signals_output(result)


def build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement(
    crx_rl_a3_dlq_cycles: DataFrame,
    crx_rl_a4_spine: DataFrame,
) -> DataFrame:
    """Dimension C, dpd_bucket_movement approach – RL counterpart of CC's
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement.

    "Paid as billed" = the month's own bucket is back to / still at
    <= _PRE_DLQ_NOT_DELINQUENT_MAX_RL (0 – RL bucket 1 is already real
    delinquency, so the threshold is 0, not CC's 1). The month's own
    (month-end) bucket is used, not the next month's: it already reflects
    that month's cash, and using the next month's would count the onset
    transition (always delinquent by definition of t0) as an unpaid month in
    every spell. "Has due" and the window are the same as the
    single_payment_cycle_count approach.

    Args:
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output.
        crx_rl_a4_spine: RL model spine – resolves spell_id/t0 and limits the
            spells to the current population.

    Returns:
        DataFrame at grain (account_id, spell_id) – same contract as
        build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spells = resolve_pre_dlq_spell_window(cc_spine_shim, spell_table_shim)

    cycles_with_evidence = crx_rl_a3_dlq_cycles.withColumn(
        "_has_due",
        F.col("monthly_emi_due").isNotNull() & (F.col("monthly_emi_due") > 0),
    ).withColumn(
        "_paid_as_billed",
        F.col("dlq_level_m").isNotNull()
        & (F.col("dlq_level_m") <= _PRE_DLQ_NOT_DELINQUENT_MAX_RL),
    )

    result = aggregate_pre_dlq_window(
        spells,
        cycles_with_evidence,
        "_paid_as_billed",
        evidence_date_col="billing_date",
        min_months_due=_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    )
    return _rl_pre_dlq_payment_signals_output(result)


# ── Node: build_rl_a3_payment_credibility ────────────────────────────────


def build_rl_a3_payment_credibility(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    commitment_signals: DataFrame,
    negative_signals: DataFrame,
    dlq_payment_signals_payment_sum_waterfall: DataFrame,
    dlq_payment_signals_single_payment_cycle_count: DataFrame,
    dlq_payment_signals_dpd_bucket_movement: DataFrame,
    pre_dlq_payment_signals_single_payment_cycle_count: DataFrame,
    pre_dlq_payment_signals_dpd_bucket_movement: DataFrame,
    dlq_payment_evidence_method: str = _DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    pre_dlq_payment_evidence_method: str = _PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL,
    model_id: str = None,
    persona_end_date: str = None,
) -> DataFrame:
    """Thin wrapper over CC's build_a3_payment_credibility (imported
    unchanged, R14): feeds it all three Dimension B approaches and both
    Dimension C approaches. The shipped approach per dimension is switchable
    from RL's own config keys (params:rl_a3_dlq_payment_evidence_method /
    params:rl_a3_pre_dlq_payment_evidence_method, default
    single_payment_cycle_count – the same default CC ships), deliberately
    separate from CC's a3_* keys so a CC config change never moves RL. The
    other approaches stay in the output as per-approach shadow columns. CC's
    combiner rejects unknown method names and raises if the selected
    approach's signals are missing, so a misconfiguration cannot silently
    ship level "none".

    Args:
        commitment_signals: crx_rl_a3_commitment_signals (Dimension A).
        negative_signals: crx_rl_a3_strong_negative_signals (strong-negative evidence).
        dlq_payment_signals_payment_sum_waterfall:
            crx_rl_a3_dlq_payment_signals_payment_sum_waterfall (Dimension B).
        dlq_payment_signals_single_payment_cycle_count:
            crx_rl_a3_dlq_payment_signals_single_payment_cycle_count
            (Dimension B, shipped).
        dlq_payment_signals_dpd_bucket_movement:
            crx_rl_a3_dlq_payment_signals_dpd_bucket_movement (Dimension B).
        pre_dlq_payment_signals_single_payment_cycle_count:
            crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count
            (Dimension C, shipped).
        pre_dlq_payment_signals_dpd_bucket_movement:
            crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement (Dimension C).
        dlq_payment_evidence_method: shipped Dimension B approach –
            "single_payment_cycle_count" (default), "payment_sum_waterfall" or
            "dpd_bucket_movement" (params:rl_a3_dlq_payment_evidence_method).
        pre_dlq_payment_evidence_method: shipped Dimension C approach –
            "single_payment_cycle_count" (default) or "dpd_bucket_movement"
            (params:rl_a3_pre_dlq_payment_evidence_method).
        model_id: optional – with persona_end_date, logs the latest-month
            a3_state_v1 distribution.
        persona_end_date: optional – paired with model_id.

    Returns:
        crx_rl_a3_payment_credibility – same schema as
        crx_cc_a3_payment_credibility.
    """
    signals = {
        "dlq_payment_signals_payment_sum_waterfall": (
            dlq_payment_signals_payment_sum_waterfall
        ),
        "dlq_payment_signals_single_payment_cycle_count": (
            dlq_payment_signals_single_payment_cycle_count
        ),
        "dlq_payment_signals_dpd_bucket_movement": (
            dlq_payment_signals_dpd_bucket_movement
        ),
        "pre_dlq_payment_signals_single_payment_cycle_count": (
            pre_dlq_payment_signals_single_payment_cycle_count
        ),
        "pre_dlq_payment_signals_dpd_bucket_movement": (
            pre_dlq_payment_signals_dpd_bucket_movement
        ),
    }
    return build_a3_payment_credibility(
        commitment_signals,
        negative_signals,
        **signals,
        dlq_payment_evidence_method=dlq_payment_evidence_method,
        pre_dlq_payment_evidence_method=pre_dlq_payment_evidence_method,
        model_id=model_id,
        persona_end_date=persona_end_date,
    )
`````

New:

`````python
"""RL A3 sources: months with the EMI, and the month's cash (``int_loan_master``)."""

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import require_columns, scoped, string_key


def _months(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """The latest snapshot of each month for the base's loans."""
    require_columns(
        int_loan_master,
        ["account_id", "observation_date", "monthly_emi_due", "total_paid"],
        "int_loan_master",
    )
    rows = int_loan_master.select(
        string_key(int_loan_master).alias("account_id"),
        F.col("observation_date").cast("date").alias("_d"),
        F.col("monthly_emi_due").cast("double").alias("emi"),
        F.col("total_paid").cast("double").alias("paid"),
    )
    latest = F.max(F.struct("_d", "emi", "paid"))
    return (
        scoped(rows, obs_base, "account_id")
        .groupBy("account_id", F.last_day("_d").alias("month_end"))
        .agg(latest["emi"].alias("emi"), latest["paid"].alias("paid"))
    )


def build_rl_a3_dues(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """A3 dues contract per month: the due and the billed amount are the month's EMI,
    else the last known one (D-A3-13)."""
    asof = (
        Window.partitionBy("account_id")
        .orderBy("month_end")
        .rowsBetween(Window.unboundedPreceding, 0)
    )
    emi = F.last("emi", ignorenulls=True).over(asof)
    return _months(int_loan_master, obs_base).select(
        "account_id",
        F.last_day(F.add_months("month_end", -1)).alias("cycle_start"),
        F.col("month_end").alias("cycle_end"),
        emi.alias("due_amount"),
        emi.alias("billed_amount"),
    )


def build_rl_a3_payments(int_loan_master: DataFrame, obs_base: DataFrame) -> DataFrame:
    """A3 payments contract: the month's cash (``total_paid``), known only to the month:
    it arrived some day between the first and the last day of the month."""
    return (
        _months(int_loan_master, obs_base)
        .where(F.col("paid") > 0)
        .select(
            "account_id",
            F.trunc("month_end", "month").alias("pay_from"),
            F.col("month_end").alias("pay_date"),
            F.col("paid").alias("amount"),
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py`
action: replace · base sha256 `e54c9aa6114f92ef6fd23530e2b7c0c907073f68919f1f18033a698f964d983e` · base trailing newline: yes · new sha256 `c701912e44658e9235d0c49c2d0063c5ebf8c5524dd14bdd0bc339f6ee58091f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A3-1 – A3 Payment Credibility axis for Retail Loans.

Nine nodes mirroring cc_a3_payment_credibility: Dimension A reuses CC nodes
through a thin wrapper; Dimension B has three approaches and
Dimension C two, all always computed and named like CC's
(dimension prefix + approach: payment_sum_waterfall / single_payment_cycle_count
/ dpd_bucket_movement); the last node wraps CC's domain-agnostic combiner and
ships the approach chosen by params:rl_a3_dlq_payment_evidence_method /
params:rl_a3_pre_dlq_payment_evidence_method (default single_payment_cycle_count
for both dimensions, CC's defaults). See
nodes.py's module docstring for what each approach computes and the timing
convention (RL's cash and bucket for a month sit on the same month-end row).

Architecture (output dataset = function name, "build_" -> "crx_" prefix):
    build_rl_a3_commitment_signals                                 [Dimension A]
    build_rl_a3_strong_negative_signals                            [strong-negative evidence]
    build_rl_a3_dlq_cycles                                         [shared B/C input]
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall          [Dimension B]
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count     [Dimension B, shipped]
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement            [Dimension B]
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count [Dimension C, shipped]
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement        [Dimension C]
    build_rl_a3_payment_credibility                                [combiner A+B+C, shipped]

Dimension A: crx_rl_a4_spine already carries (account_id, observation_date,
spell_id, t0, cif_id) – reshaped into the CC (cc_spine, spell_table) shim
pair via rl_spine_as_cc_shim so build_a3_commitment_signals runs
unchanged. Strong negatives (build_rl_a3_strong_negative_signals) use the same
shim and apply a 24m partition floor on dcore_prm_followup_outcomes
(performance guard per TASKS_RL.md).

The five Dimension B/C nodes depend only on build_rl_a3_dlq_cycles' output and
crx_rl_a4_spine (which carries spell_id/t0 directly), so they run in parallel
once it completes.

Run with:
    kedro run --pipeline=crx_rl_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a3_commitment_signals,
    build_rl_a3_dlq_cycles,
    build_rl_a3_dlq_payment_signals_dpd_bucket_movement,
    build_rl_a3_dlq_payment_signals_payment_sum_waterfall,
    build_rl_a3_dlq_payment_signals_single_payment_cycle_count,
    build_rl_a3_payment_credibility,
    build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement,
    build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count,
    build_rl_a3_strong_negative_signals,
)

_TAGS = ["crx", "a3", "payment_credibility", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node RL A3 Payment Credibility pipeline."""
    return Pipeline(
        [
            # ── Dimension A: commitments kept (DCORE PTP / settlement signals,
            # 24m partition floor, RL-D5 spine) ────────────────────────────────
            node(
                func=build_rl_a3_commitment_signals,
                inputs=[
                    "crx_rl_a4_spine",
                    "dcore_observation_spine",
                    "dcore_feat_ptp",
                    "dcore_feat_settlement",
                    "dcore_int_ptp",
                    "dcore_prm_promise_instalments",
                    "dcore_int_settlement",
                    "dcore_prm_settlement_schedule_instalments",
                ],
                outputs="crx_rl_a3_commitment_signals",
                name="build_rl_a3_commitment_signals",
                tags=_TAGS,
            ),
            # ── Strong negatives: evidence only (24m follow-up floor); the rules
            # run in the combiner ───────────────────────────────────────────────
            node(
                func=build_rl_a3_strong_negative_signals,
                inputs=[
                    "crx_rl_a4_spine",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "params:crx_persona",
                    "dcore_int_ptp",
                    "dcore_int_settlement",
                ],
                outputs="crx_rl_a3_strong_negative_signals",
                name="build_rl_a3_strong_negative_signals",
                tags=_TAGS,
            ),
            # ── Shared input for Dimensions B and C: monthly bucket + lag +
            # monthly_emi_due + total_paid ──────────────────────────────────────
            node(
                func=build_rl_a3_dlq_cycles,
                inputs=["crx_rl_full_history", "int_loan_master", "rl_spine"],
                outputs="crx_rl_a3_dlq_cycles",
                name="build_rl_a3_dlq_cycles",
                tags=_TAGS,
            ),
            # ── Dimension B (dlq): payments in delinquency – three approaches,
            # all always computed; shipped one chosen by
            # params:rl_a3_dlq_payment_evidence_method ──────────────────────────
            node(
                func=build_rl_a3_dlq_payment_signals_payment_sum_waterfall,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                name="build_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_dlq_payment_signals_single_payment_cycle_count,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                name="build_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_dlq_payment_signals_dpd_bucket_movement,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                name="build_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Dimension C (pre_dlq): record before delinquency – two approaches,
            # all always computed; shipped one chosen by
            # params:rl_a3_pre_dlq_payment_evidence_method ──────────────────────
            node(
                func=build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                name="build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                tags=_TAGS,
            ),
            node(
                func=build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement,
                inputs=["crx_rl_a3_dlq_cycles", "crx_rl_a4_spine"],
                outputs="crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                name="build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                tags=_TAGS,
            ),
            # ── Combiner: Dimensions A + B + C -> a3_state_v1 (CC's
            # build_a3_payment_credibility, wrapped) ────────────────────────────
            node(
                func=build_rl_a3_payment_credibility,
                inputs=[
                    "crx_rl_a3_commitment_signals",
                    "crx_rl_a3_strong_negative_signals",
                    "crx_rl_a3_dlq_payment_signals_payment_sum_waterfall",
                    "crx_rl_a3_dlq_payment_signals_single_payment_cycle_count",
                    "crx_rl_a3_dlq_payment_signals_dpd_bucket_movement",
                    "crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count",
                    "crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement",
                    "params:rl_a3_dlq_payment_evidence_method",
                    "params:rl_a3_pre_dlq_payment_evidence_method",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs="crx_rl_a3_payment_credibility",
                name="build_rl_a3_payment_credibility",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (the month's EMI) and the payments (the month's cash).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``crx_rl_a4_deterioration``, ``int_loan_master`` and the DCORE tables.

    kedro run --pipeline=crx_rl_a3_payment_credibility

TEMPORARY (A3 bundle): ``create_check_pipeline`` (``a3_credibility/check.py``); removed by
the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a3_credibility.check import create_a3_check_pipeline
from ..a3_credibility.pipeline import TAGS, create_a3_pipeline
from .nodes import build_rl_a3_dues, build_rl_a3_payments

_SOURCES = {"int_loan_master": "int_loan_master", "obs_base": "crx_rl_obs_base"}
DUES = node(
    func=build_rl_a3_dues,
    inputs=_SOURCES,
    outputs="crx_rl_a3_dues",
    name="build_crx_rl_a3_dues",
    tags=TAGS,
)
PAYMENTS = node(
    func=build_rl_a3_payments,
    inputs=_SOURCES,
    outputs="crx_rl_a3_payments",
    name="build_crx_rl_a3_payments",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a3_payment_credibility", **kwargs
) -> Pipeline:
    """The RL A3 axis written to ``output``."""
    return create_a3_pipeline("rl", output, DUES, PAYMENTS)


def create_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the A3 bundle check for RL."""
    return create_a3_check_pipeline("rl", DUES, PAYMENTS)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/_signals_common.py`
action: delete · base sha256 `4a1a4938629fe2f113f0702a06c39e1400ead95203729f40bc03ff9196fa250b` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared payment-attribution and due-amount helpers for A3 Dimension B and C.

Both dimensions need to know, per billing cycle, how much the customer paid,
whether it arrived by the due date, and how much was actually due that cycle –
factored once here so build_a3_dlq_payment_signals_payment_sum_waterfall (post-onset, "payments in
delinquency") and build_a3_pre_dlq_payment_signals_single_payment_cycle_count (pre-onset, "record
before
delinquency") reuse identical logic instead of diverging.

Naming mirrors the existing pipeline-local shared module
crx_persona/_spine_utils.py.
"""

# pylint: disable=too-many-lines

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    instalment_amount_flags,
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from enbd_collections.pipelines.crx_persona._spine_utils import join_spine_to_spell
from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _PAYMENT_CYCLE_FLOOR_LOOKBACK_D,
    _PAYMENT_CYCLE_MAX_LENGTH_D,
    _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
    _TAU_A3V2_COMMITMENTS_WINDOW_M,
    _TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS,
    _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180,
    _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS,
    _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
    _TAU_A3V2_PRE_DLQ_WINDOW_M,
)


def _floor_column(history_floor_date):
    """The history floor as a date literal, or None when no floor is set."""
    return F.lit(str(history_floor_date)).cast("date") if history_floor_date else None


def resolve_dlq_payment_window(
    cc_spine: DataFrame,
    crx_cc_spell_table: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """DLQ-depth-dependent payment-evidence window, shared by both Dimension
    B methods (build_a3_dlq_payment_signals_payment_sum_waterfall / _dpd) – pure extraction of a
    block that was duplicated near-verbatim between the two, no behavior
    change (2026-10-21).

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): the
    window never starts before it. Never binding for observation dates a few
    months past the floor; a guard that keeps the rule explicit.

    Two windows: the "Regular" window (_window_months / _window_start: 3 months at
    61-180 DPD, 6 at 180+) and the "any payment" window (_any_window_months /
    _any_window_start: same at 61-180, 12 months at 180+) used for Some vs None
    and the strong negatives. _any_window_start <= _window_start.

    _min_payment_aed: 100 at 180+ DPD, else 0 – the minimum payment for a cycle to
    qualify / a payment to count (see payment_meets_floor).

    Returns:
        DataFrame with (account_id, observation_date, t0, dlq_bucket_from_hist,
        _window_months, _window_start, _any_window_months, _any_window_start,
        _min_payment_aed).
    """
    spine_with_spell = join_spine_to_spell(cc_spine, crx_cc_spell_table)

    spine_with_dlq = spine_with_spell.join(
        cc_spine.select(
            F.col("contract_id").alias("account_id"),
            "observation_date",
            "dlq_bucket_from_hist",
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    floor = _floor_column(history_floor_date)

    def _window_start(months_col):
        starts = [F.col("t0"), F.add_months(F.col("observation_date"), -months_col)]
        if floor is not None:
            starts.append(floor)
        return F.greatest(*starts)

    is_180_plus = F.col("dlq_bucket_from_hist") >= 8
    return (
        spine_with_dlq.withColumn(
            "_window_months",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS)
            ).otherwise(F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180)),
        )
        .withColumn(
            "_any_window_months",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS)
            ).otherwise(F.lit(_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180)),
        )
        .withColumn("_window_start", _window_start(F.col("_window_months")))
        .withColumn("_any_window_start", _window_start(F.col("_any_window_months")))
        .withColumn(
            "_min_payment_aed",
            F.when(
                is_180_plus, F.lit(_TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS)
            ).otherwise(F.lit(0.0)),
        )
    )


def payment_meets_floor(payment_col):
    """Boolean: the payment reaches the spine row's minimum payment (``s._min_payment_aed``:
    100 AED at 180+ DPD, 0 otherwise = no floor). For use inside aggregate_dlq_window
    expressions, where the spine row is the ``s`` alias."""
    return (F.col("s._min_payment_aed") <= 0) | (
        payment_col >= F.col("s._min_payment_aed")
    )


def resolve_dpd_bucket_movement_history(
    crx_cc_full_history: DataFrame, history_floor_date: str = None
) -> DataFrame:
    """Per-cycle dlq_level_m + its lag (dlq_level_prev_m), shared by both Dimension
    B and C's dpd_bucket_movement methods (build_a3_dlq_payment_signals_dpd_bucket_movement /
    build_a3_pre_dlq_payment_signals_dpd_bucket_movement).

    Sourced from crx_cc_full_history – the full, floor-free account history – rather
    than crx_cc_billing (windowed via crx_cc_acct_windows, floored at
    min(t0) - 12 months). Same BS_PMT_CYCLE_DUE ground truth as crx_cc_billing.dlq_level_m
    (confirmed identical extraction field), but unbounded, so even the very first
    post-onset row has a genuine previous cycle to compare against instead of a NULL
    lag at the edge of the 12-month window.

    A lag, not a lead (2026-10-26 fix): a billing statement's own bucket numbers
    already reflect whatever cash arrived since the PREVIOUS statement – confirmed by
    hand-reconciling a real account's billing/balance history (logs/dim_c_validation.log,
    Scenario 2): a payment "labeled" on a given billing_date has zero visible effect on
    that same row's own past_due_amount (which keeps growing by the usual monthly
    charge), and only reconciles exactly against the NEXT row once that payment is
    subtracted. So "did this row's bucket improve" must compare this row's own
    dlq_level_m against the PRIOR row's (dlq_level_prev_m) – comparing against the next
    row instead (the pre-fix behavior) attaches the evidence of a transition to the row
    one cycle before the one whose own ledger state actually shows it.

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): rows
    before it are dropped BEFORE the lag, so the first in-window statement has a
    NULL previous level (no credit) and is never compared with a statement from
    before the 2021-2023 billing gap. crx_cc_full_history itself stays unfloored.

    Args:
        crx_cc_full_history: account_id, billing_date, dlq_bucket (int, nullable).
        history_floor_date: ISO date or None.

    Returns:
        DataFrame with (account_id, billing_date, dlq_level_m, dlq_level_prev_m).
    """
    history = crx_cc_full_history.select(
        "account_id", "billing_date", F.col("dlq_bucket").alias("dlq_level_m")
    )
    floor = _floor_column(history_floor_date)
    if floor is not None:
        history = history.where(F.col("billing_date") >= floor)
    w_account_history = Window.partitionBy("account_id").orderBy("billing_date")
    return history.withColumn(
        "dlq_level_prev_m", F.lag("dlq_level_m").over(w_account_history)
    )


def resolve_pre_dlq_spell_window(
    cc_spine: DataFrame,
    crx_cc_spell_table: DataFrame,
    history_floor_date: str = None,
) -> DataFrame:
    """Pre-onset 12-month window, population-filtered to spells active in
    cc_spine – shared by both Dimension C methods
    (build_a3_pre_dlq_payment_signals_single_payment_cycle_count
    / _dpd) – pure extraction of a block that was duplicated near-verbatim
    between the two, no behavior change (2026-10-21).

    The spell is the one active at the observation date (join_spine_to_spell), so
    an account with an old cured spell and a newer one uses the newer one.

    history_floor_date (params:cc_a3_history_floor_date, None = no floor): the
    window never starts before it. A spell whose T0 is before the floor therefore
    gets a start after T0, matches no cycles and reads as "no record"; T0 shortly
    after the floor keeps only the in-floor months. Other callers (RL) leave it
    None and are unchanged.

    Returns:
        DataFrame with (account_id, spell_id, t0, _window_start).
    """
    active_spells = (
        join_spine_to_spell(cc_spine, crx_cc_spell_table)
        .select("account_id", "t0")
        .where(F.col("t0").isNotNull())
        .distinct()
    )

    window_start = F.add_months(F.col("t0"), -_TAU_A3V2_PRE_DLQ_WINDOW_M)
    floor = _floor_column(history_floor_date)
    if floor is not None:
        window_start = F.greatest(window_start, floor)

    return (
        crx_cc_spell_table.select("account_id", "spell_id", "t0")
        .join(active_spells, on=["account_id", "t0"], how="inner")
        .withColumn("_window_start", window_start)
    )


def attribute_payments_to_billing_cycles(
    billing: DataFrame, transactions: DataFrame
) -> DataFrame:
    """Attribute payment transactions to the billing cycle they land in.

    Cycle attribution uses billing_date < banking_date <= next_billing_date – NOT
    due_date – because due_date (~billing_date+25d) falls short of the next
    statement cut (~billing_date+30d), leaving a ~5-6 day dead zone where late
    payments would otherwise be dropped or misattributed to the wrong cycle.
    This was found and fixed in the exploratory notebook
    (notebooks/data_engineering/crx_cc_account_payment_profiling.ipynb).
    due_date is used only for the separate on_time_payment_sum_in_cycle check.

    Excludes is_post_block_x_fee (Block-W sentinel-date fee-accrual artifacts)
    and anything not categorised "payment" via TXN_CATEGORIES.

    Args:
        billing: crx_cc_billing. Required cols: contract_id, observation_date
            (billing_date), due_date, next_billing_date.
        transactions: crx_cc_transactions. Required cols: contract_id,
            observation_date (banking_date), txn_amount_aed, txn_category,
            is_post_block_x_fee.

    Returns:
        DataFrame at grain (contract_id, billing_date, due_date,
        next_billing_date) with:
            payment_sum_in_cycle (double)         – total payment in the cycle.
            on_time_payment_sum_in_cycle (double) – payment with banking_date
                                                    <= due_date only.
    """
    billing_cycles = billing.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("due_date"),
        F.col("next_billing_date"),
    )

    payments = transactions.filter(
        (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
    ).select(
        F.col("contract_id"),
        F.col("observation_date").alias("banking_date"),
        F.col("txn_amount_aed"),
    )

    attributed = billing_cycles.alias("b").join(
        payments.alias("p"),
        (F.col("b.contract_id") == F.col("p.contract_id"))
        & (F.col("p.banking_date") > F.col("b.billing_date"))
        & (
            F.col("b.next_billing_date").isNull()
            | (F.col("p.banking_date") <= F.col("b.next_billing_date"))
        ),
        "left",
    )

    return attributed.groupBy(
        F.col("b.contract_id").alias("contract_id"),
        F.col("b.billing_date").alias("billing_date"),
        F.col("b.due_date").alias("due_date"),
        F.col("b.next_billing_date").alias("next_billing_date"),
    ).agg(
        F.coalesce(F.sum("p.txn_amount_aed"), F.lit(0.0)).alias("payment_sum_in_cycle"),
        F.coalesce(
            F.sum(
                F.when(
                    F.col("p.banking_date") <= F.col("b.due_date"),
                    F.col("p.txn_amount_aed"),
                )
            ),
            F.lit(0.0),
        ).alias("on_time_payment_sum_in_cycle"),
    )


_QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST = [
    f"overdue_bucket_0{i}" for i in range(7, 0, -1)
]
# bucket_08 is NOT in this list – it is decomposed into synthetic sub-items
# (see _bucket08_slice_cols in resolve_dlq_waterfall_qualifying_months_cleared) and walked
# first, ahead of bucket_07, instead of being walked as one named column.


def resolve_dlq_waterfall_qualifying_months_cleared(  # pylint: disable=too-many-locals
    balance: DataFrame,
    cycles: DataFrame,
    qualifying_share: float = 1.0,
    bucket08_baseline_lookback_m: int = 24,
    bucket08_max_split: int = 6,
) -> DataFrame:
    """Count how many overdue-bucket "months" a cycle's payment fully clears.

    Dimension-B-only extension of resolve_due_amount_m's single-bucket view. A
    payment doesn't necessarily land just the oldest open bucket – a
    lumpsum payment can clear several buckets in one shot (e.g. bucket_06=600
    + bucket_05=550, payment=1200 clears both, 2 qualifying months, not 1).

    Two corrections to the naive "walk the existing buckets" view, both found
    by hand-tracing real lumpsum cycles in logs/sample_scenario1.log against
    the resulting statements, and cross-checked against sample_scenario3.log
    and sample_scenario4.log (2026-10-20):

    1. overdue_bucket_08 is included, as the OLDEST item in the walk – NOT
       excluded as a "terminal accumulator". resolve_due_amount_m's exclusion
       of bucket_08 was an unconfirmed assumption; a large enough payment
       (e.g. a 10,500 payment in sample_scenario1) does clear it, oldest-
       first, same as 07..01 – confirmed by the resulting next statement.
       Under pure non-payment (sample_scenario4), bucket_08 only ever
       accumulates (never ages back down on its own), consistent with it
       being a real waterfall slot a payment can reach, not a dead counter.
    2. The cycle's own freshly-billed minimum_due is appended as the NEWEST
       item in the same walk, scaled by qualifying_share like every other
       item. It isn't in any bucket yet at snapshot time, but it's exactly
       what becomes the new bucket_01 on the *next* statement if the
       leftover payment doesn't cover it. Confirmed two ways: (a) in
       sample_scenario1, the next cycle's new bucket_01 was numerically
       identical to this cycle's own minimum_due, carried forward unpaid;
       (b) sample_scenario4's clean period independently confirms
       total_due == (existing overdue as of this statement) +
       (this cycle's own minimum_due) exactly, the same relationship this
       fix relies on.
    3. overdue_bucket_08, when included, is no longer walked as ONE atomic
       item (2026-10-21). A large accumulated bucket_08 can represent
       several real historical months' worth of charges; walking it
       atomically means a payment that is genuinely larger than one month's
       due but smaller than the full accumulated pot credits zero months –
       indistinguishable from paying nothing (confirmed by hand against
       logs/scenarios.log scenario 1: a 5,200 payment against a 5,066.04
       bucket_08, trailing minimum_due baseline ~2,400, credited 0 months
       atomic vs. 1 decomposed). bucket_08 is split into up to
       bucket08_max_split uniform synthetic slices, each sized
       bucket_08 / n where n = the account's own bucket_08 amount divided by
       its trailing bucket08_baseline_lookback_m-cycle average minimum_due
       (rounded, floored at 1, capped), and walked oldest-first ahead of
       bucket_07 – same walk mechanics, just more/smaller items. If no
       reliable trailing baseline exists (e.g. no real billing history in
       the lookback), bucket_08 falls back to being walked as one atomic
       item (n=1) – the pre-fix behaviour, a conscious degrade rather than
       an invented number, matching resolve_due_amount_m's own honest-NULL
       philosophy.

    The walk (08 -> 07 -> ... -> 01 -> minimum_due) accumulates each item's
    amount and counts how many the cycle's payment_sum_in_cycle fully
    covers, strictly in order: a later item is never credited ahead of an
    earlier one that is not yet cleared, and an item only partially covered
    stops the walk there – no partial credit, matching "at least 100% of
    one month's due" wording. Zero/null buckets are skipped without
    breaking the walk or affecting the running total.

    The RETURNED count is a plain count, not a net-of-something adjustment
    (correction 4, 2026-10-21, replacing a prior "net, not gross" design):
    minimum_due is walked as just the newest item in the same oldest-first
    list (correction 2 above), and the function returns exactly how many
    items – decomposed bucket_08 slices, buckets 07..01, and minimum_due –
    the cycle's payment fully clears, full stop. This axis answers one
    question, "how many months of minimum due did the customer pay," which
    is inherently a count, not a value to be netted against anything.

    A prior design (2026-10-20 through 2026-10-21) instead subtracted 1 from
    the bucket-only count whenever the leftover payment did NOT also cover
    minimum_due, specifically to make this function's count match
    dlq_level_m's month-over-month delta on the DPD-bucket method
    (build_a3_dlq_payment_signals_dpd_bucket_movement) exactly, cycle for cycle. That
    convergence goal is now understood to be the wrong target:
    dlq_level_m is a lossy single-integer summary of the ladder (confirmed
    repeatedly – e.g. a large bucket_08 can silently represent several real
    months, which is exactly why correction 3 above exists), so forcing this
    function to match its delta means inheriting dlq_level_m's own
    compression artifacts rather than reporting the real count. Found by
    hand against logs/scenarios.log scenario 3's 2025-02-25 row: a 34,484.32
    payment against b04=2,578.22 plus three 7,500 buckets plus a 7,500
    minimum_due sums to exactly 32,578.22 (1,906.10 left over, discarded,
    same as every other over-payment this walk handles) – genuinely 5
    months' due paid, matching the real dlq drop of 5 (9->... no, 5->0)
    exactly. The old net-of-new-charge formula stopped at 4: it used
    minimum_due only as a pass/fail gate that could subtract credit, never
    add it, so a payment that covered every old bucket AND the new charge
    still scored one short of what was actually paid. Expected consequence:
    this function's count and dlq_level_m's delta will now disagree on some
    cycles (e.g. scenario 2's 2024-08-25: this function reads 3 – a
    decomposed bucket_08 slice, bucket_07, and bucket_06, each a real
    month-sized amount, all three fully paid – where dlq_level_m's delta
    reads 2, because Way4's own bucket_08 had already compressed more than
    one month into what dlq_level_m counts as a single occupied slot). That
    divergence is accepted, not a regression: dlq_level_m
    (build_a3_dlq_payment_signals_dpd_bucket_movement) remains a cheap, always-available
    cross-check/fallback; this function is the authoritative count whenever
    the billing ledger is available.

    PROD OOM fix, 2026-10-21 (mechanical, not a behavior change). The walk
    below used to thread a plain Python 3-tuple of raw Column objects through
    the loop (each iteration nesting the previous iteration's Column inside a
    new F.when(...).otherwise(...)) – 14 items (6 bucket08 slices + 7 ladder
    buckets + minimum_due) x 3 tuple elements produced one single, unevaluated
    ~42-node-deep Column AST, fed straight into this function's own final
    .select() below. In production, build_a3_payment_cycles hung 10+ minutes
    then crashed with java.lang.OutOfMemoryError: Java heap space, with the
    stack trace pointing at Catalyst's ColumnResolutionHelper during exactly
    that .select() call – i.e. analysis time, not row execution, and
    identical on every call regardless of data volume (the depth is
    structural, driven by the fixed 14-item list length). This exact
    pathology had already been diagnosed in an earlier session (45+ seconds
    to build a Catalyst plan for a single trivial row – see
    test_cc_a3_dimension_bc_signals.py's module docstring) but left
    unaddressed since performance tuning was out of scope for that pass; it
    is now a real production outage, so the walk below materializes each
    iteration's (running_total, still_clearing, gross_cleared) state as 3
    real, uniquely-named DataFrame columns via .withColumns() instead of
    nesting raw Column objects – the same pattern the bucket08-slice loop
    above already uses safely for the same reason (each step becomes a
    shallow Project node Catalyst resolves cheaply by column-name reference,
    instead of one deep expression tree). The arithmetic per step
    (candidate_total / meets_threshold / clears, and the three
    F.when(...).otherwise(...) updates) is byte-identical to before – only
    the threading mechanism changed. See
    test_cc_a3_dimension_bc_signals.py's TestResolveQualifyingMonthsClearedRealSpark
    for a real-Spark timing regression test and a reconstruction of this
    docstring's own scenario-1/scenario-3 anchors proving the output is
    unchanged.

    sample_scenario3.log's largest cycle (a 12,700 payment against ~19,678
    in old arrears + current due) does NOT reconcile even with both fixes –
    the shortfall is a genuine account-closure/final-settlement event
    (confirmed: the account's balance goes to true zero and cc_spine has no
    further rows for it at all), not a cash waterfall this function can or
    should model. No live A3 output is affected by that gap, since no later
    observation row's window ever includes that cycle.

    Not used by Dimension C: "paid as billed" there is inherently per-cycle
    and on-time (by due_date) – a later lumpsum clearing an old bucket cannot
    retroactively make that original cycle's payment on-time, so Dimension C
    keeps using resolve_due_amount_m / the single oldest-bucket figure
    unchanged (see build_a3_pre_dlq_payment_signals_single_payment_cycle_count). This function feeds
    only build_a3_dlq_payment_signals_payment_sum_waterfall (Dimension B), which has no on-time
    requirement ("qualifying ... promised or not").

    Args:
        balance: crx_cc_balance. Required cols: contract_id, observation_date
            (billing_date), overdue_bucket_01..08, minimum_due.
        cycles: attribute_payments_to_billing_cycles output (pre-rename –
            contract_id, billing_date, payment_sum_in_cycle).
        qualifying_share: fraction of an item's amount required to count it
            as cleared (matches _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE).
        bucket08_baseline_lookback_m: trailing cycles (rows), per account, to
            average minimum_due over for the bucket_08 decomposition baseline
            (matches _TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M).
        bucket08_max_split: ceiling on how many synthetic sub-items a single
            bucket_08 lump can be split into (matches
            _TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP).

    Returns:
        DataFrame with (account_id, billing_date, waterfall_qualifying_months_cleared_m).
    """
    balance_buckets = balance.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("minimum_due"),
        F.col("overdue_bucket_08"),
        *_QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST,
    )

    _w_trailing_minimum_due = (
        Window.partitionBy("contract_id")
        .orderBy("billing_date")
        .rowsBetween(-bucket08_baseline_lookback_m, -1)
    )
    balance_with_baseline = balance_buckets.withColumn(
        "_minimum_due_baseline",
        F.avg(F.when(F.col("minimum_due") > 0, F.col("minimum_due"))).over(
            _w_trailing_minimum_due
        ),
    )

    _bucket_08_amt = F.coalesce(F.col("overdue_bucket_08"), F.lit(0.0))
    _has_baseline = F.col("_minimum_due_baseline").isNotNull() & (
        F.col("_minimum_due_baseline") > 0
    )
    _n_bucket08_items = F.when(
        _has_baseline,
        F.greatest(
            F.lit(1),
            F.least(
                F.lit(bucket08_max_split),
                F.round(_bucket_08_amt / F.col("_minimum_due_baseline")).cast("int"),
            ),
        ),
    ).otherwise(
        F.lit(1)
    )  # no baseline -> atomic fallback, n=1 (pre-fix behaviour)

    balance_with_slices = balance_with_baseline.withColumn(
        "_n_bucket08_items", _n_bucket08_items
    )
    _slice_cols = [f"_bucket08_slice_{i:02d}" for i in range(1, bucket08_max_split + 1)]
    for i, slice_col in enumerate(_slice_cols, start=1):
        balance_with_slices = balance_with_slices.withColumn(
            slice_col,
            F.when(
                F.lit(i) <= F.col("_n_bucket08_items"),
                _bucket_08_amt / F.col("_n_bucket08_items").cast("double"),
            ).otherwise(F.lit(0.0)),
        )

    joined = cycles.select("contract_id", "billing_date", "payment_sum_in_cycle").join(
        balance_with_slices, on=["contract_id", "billing_date"], how="left"
    )

    def _walk_one_item_materialized(df, idx, prev_names, amount_col):
        """One waterfall-walk step, materialized as 3 real DataFrame columns
        instead of nesting the previous step's Column objects inside a new
        F.when(...) – see this function's "PROD OOM fix" docstring paragraph
        above for why. prev_names / the returned names are plain column-name
        strings threaded through the driving loop below; the arithmetic here
        is byte-identical to the pre-fix _walk_one_item closure."""
        prev_running_total = F.col(prev_names[0])
        prev_still_clearing = F.col(prev_names[1])
        prev_gross_cleared = F.col(prev_names[2])

        amt = F.coalesce(F.col(amount_col), F.lit(0.0))
        candidate_total = prev_running_total + amt * F.lit(qualifying_share)
        meets_threshold = F.col("payment_sum_in_cycle") >= candidate_total
        clears = prev_still_clearing & (amt > 0) & meets_threshold

        names = (
            f"_running_total_{idx:02d}",
            f"_still_clearing_{idx:02d}",
            f"_gross_cleared_{idx:02d}",
        )
        df = df.withColumns(
            {
                names[0]: F.when(clears, candidate_total).otherwise(prev_running_total),
                names[1]: F.when(
                    amt > 0, prev_still_clearing & meets_threshold
                ).otherwise(prev_still_clearing),
                names[2]: F.when(clears, prev_gross_cleared + 1).otherwise(
                    prev_gross_cleared
                ),
            }
        ).drop(
            *prev_names
        )  # bound schema width -- only the current step's state survives
        return df, names

    # minimum_due walked as the newest item, same as every bucket -- this
    # axis answers one question, "how many months of minimum due did the
    # customer pay," so there is nothing special about the freshest one
    # (2026-10-21 fix, replacing the old net-of-new-charge penalty entirely).
    # Real anchor: logs/scenarios.log scenario 3's 2025-02-25 row -- a
    # 34,484.32 payment against b04=2,578.22 + b03/b02/b01=7,500 each +
    # minimum_due=7,500 sums to exactly 32,578.22, with 1,906.10 left over
    # (simply discarded, same as every other over-payment in this walk) --
    # genuinely 5 months' due paid in full, matching the real dlq drop 5->0
    # exactly. The old formula stopped at the bucket walk (gross=4) and used
    # minimum_due only as a pass/fail gate that could subtract credit, never
    # add it, so a payment covering ALL of the old debt plus the new
    # charge still only scored 4, one short of what was actually paid.
    _walk_cols_oldest_first = (
        _slice_cols + _QUALIFYING_LADDER_BUCKET_COLS_OLDEST_FIRST + ["minimum_due"]
    )
    _seed_names = ("_running_total_00", "_still_clearing_00", "_gross_cleared_00")
    joined = joined.withColumns(
        {
            _seed_names[0]: F.lit(0.0),
            _seed_names[1]: F.lit(True),
            _seed_names[2]: F.lit(0),
        }
    )
    _state_names = _seed_names
    for _idx, _col_name in enumerate(_walk_cols_oldest_first, start=1):
        joined, _state_names = _walk_one_item_materialized(
            joined, _idx, _state_names, _col_name
        )
    qualifying_months_cleared = F.col(_state_names[2])

    return joined.select(
        F.col("contract_id").alias("account_id"),
        F.col("billing_date"),
        qualifying_months_cleared.alias("waterfall_qualifying_months_cleared_m"),
    )


def filter_payment_cycles(
    cycles: DataFrame, history_floor_date: str = None
) -> DataFrame:
    """Drop billing cycles that span a stretch of missing statements.

    A cycle runs from one statement to the NEXT statement that exists, so a missing
    stretch (the 2021-2023 billing gap, a missing statement run) becomes one long cycle
    whose payment sum covers several months against a single (stale) due amount. Two
    rules, both on the cycle's own dates:

    * billing_date >= history_floor_date - _PAYMENT_CYCLE_FLOOR_LOOKBACK_D days (only when
      a floor is set): keeps the legitimate predecessor of the first in-floor statement
      (up to ~35 days earlier), drops a cycle that starts years before the floor;
    * datediff(next_billing_date, billing_date) <= _PAYMENT_CYCLE_MAX_LENGTH_D days (a
      NULL next_billing_date, the account's latest cycle, is kept – it is never a
      result evidence).

    Dropped cycles give no payment evidence at all (they are not turned into
    zero-payment months).

    Args:
        cycles: attribute_payments_to_billing_cycles output (billing_date,
            next_billing_date, ...).
        history_floor_date: ISO date or None (params:cc_a3_history_floor_date).
    """
    result = cycles.where(
        F.col("next_billing_date").isNull()
        | (
            F.datediff(F.col("next_billing_date"), F.col("billing_date"))
            <= _PAYMENT_CYCLE_MAX_LENGTH_D
        )
    )
    floor = _floor_column(history_floor_date)
    if floor is not None:
        result = result.where(
            F.col("billing_date") >= F.date_sub(floor, _PAYMENT_CYCLE_FLOOR_LOOKBACK_D)
        )
    return result


def resolve_due_amount_m(balance: DataFrame) -> DataFrame:
    """Resolve "one month's due amount" per billing cycle for A3 Dimension B/C.

    due_amount_m = coalesce(overdue_bucket_07, ..., overdue_bucket_01, minimum_due),
    treating 0 the same as NULL at every step. Way4 represents the minimum_due
    (ENBD_DUE) coverage collapse about DLQ as an explicit 0 – not NULL – so a
    plain F.coalesce(minimum_due, ...) would never actually fall through to the
    next candidate; this is why each candidate is wrapped to treat 0 as missing.

    overdue_bucket_01 is the newest cycle's missed amount – verified against
    sample billing data (logs/billing_cycle.log, billing5.log, billing6.log) to
    consistently equal the prior cycle's minimum_due, i.e. the right
    single-month granularity. Once minimum_due goes dark, new amounts stop
    landing in overdue_bucket_01 too (nothing new is being billed that cycle);
    the existing single-month figure keeps aging through buckets 02..07 as a
    pure FIFO shift (confirmed: past_due_amount stays flat while this happens).

    A payment clears the oldest outstanding bucket first (standard collections
    waterfall – the longest-overdue amount is settled before anything newer),
    so bucket_07 (the most aged of 01..07) is the one actually at stake for
    "did this cycle's payment clear what's due" and must be checked first;
    falling through 07..01 then minimum_due recovers the oldest still-open
    single-month figure, which is the amount a qualifying payment needs to
    clear.

    overdue_bucket_08 is deliberately EXCLUDED – it is Way4's terminal
    accumulator bucket (confirmed by its magnitude: ~20x a single bucket's
    value once the ladder fully drains into it), not a single month's amount.
    total_due is also deliberately excluded – confirmed by sample data to grow
    unboundedly from compounding interest/fees even at zero payment activity,
    making a "100% of total_due" bar structurally unreachable deep in
    delinquency.

    NULL when none of the candidates has a real value – genuinely nothing
    determinable to check a payment against that cycle (pre-delinquency before
    anything is billed, or post write-off/settlement, or the ladder has fully
    drained into the bucket_08 accumulator with no single-month figure left).
    [CONFIRM] – the single highest-impact assumption in the A3 framework.

    Args:
        balance: crx_cc_balance. Required cols: contract_id, observation_date
            (billing_date), minimum_due, overdue_bucket_01..07.

    Returns:
        DataFrame with (account_id, billing_date, due_amount_m).
    """

    def _nonzero(column: str):
        return F.when(F.col(column).isNotNull() & (F.col(column) != 0.0), F.col(column))

    candidates = [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]
    due_amount_m = F.coalesce(*[_nonzero(c) for c in candidates])

    return balance.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").alias("billing_date"),
        due_amount_m.alias("due_amount_m"),
    )


def resolve_bucket08_fallback_due(
    balance: DataFrame, baseline_months: int = _TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS
) -> DataFrame:
    """Due amount for statements where only overdue_bucket_08 is left (default method).

    resolve_due_amount_m returns NULL once buckets 01-07 and minimum_due are all 0 and
    bucket 08 holds the money, so such a cycle can never qualify. Per account, the
    stagnation point is the first balance row in that state; the frozen baseline is the
    average minimum_due of its last ``baseline_months`` months with a positive
    minimum_due before that point. Every later stagnated statement gets that one number.
    Accounts with no positive minimum_due before stagnation get no row (stay NULL).

    Args:
        balance: crx_cc_balance (contract_id, observation_date, minimum_due,
            overdue_bucket_01..08).
        baseline_months: months of positive minimum_due averaged.

    Returns:
        (account_id, billing_date, due_amount_fallback_m) for stagnated statements of
        accounts that have a baseline.
    """

    def _nonzero(column: str):
        return F.col(column).isNotNull() & (F.col(column) != 0.0)

    ladder_empty = F.lit(True)
    for column in [f"overdue_bucket_0{i}" for i in range(7, 0, -1)] + ["minimum_due"]:
        ladder_empty = ladder_empty & ~_nonzero(column)
    stagnated = ladder_empty & _nonzero("overdue_bucket_08")

    rows = balance.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").alias("billing_date"),
        "minimum_due",
        stagnated.alias("_stagnated"),
    )
    stagnation = (
        rows.filter("_stagnated")
        .groupBy("account_id")
        .agg(F.min("billing_date").alias("_stagnation_date"))
    )
    baseline = (
        rows.join(stagnation, "account_id")
        .filter(
            _nonzero("minimum_due")
            & (F.col("billing_date") < F.col("_stagnation_date"))
        )
        .groupBy("account_id", F.trunc("billing_date", "month").alias("_month"))
        .agg(F.avg("minimum_due").alias("_month_min_due"))
        .withColumn(
            "_recency",
            F.row_number().over(
                Window.partitionBy("account_id").orderBy(F.col("_month").desc())
            ),
        )
        .filter(F.col("_recency") <= baseline_months)
        .groupBy("account_id")
        .agg(F.avg("_month_min_due").alias("due_amount_fallback_m"))
    )
    return (
        rows.filter("_stagnated")
        .join(baseline, "account_id")
        .select("account_id", "billing_date", "due_amount_fallback_m")
    )


def aggregate_dlq_window(
    spine_with_window: DataFrame,
    cycles: DataFrame,
    evidence_date_col: str,
    qualifying_months_expr,
    any_payment_expr,
) -> DataFrame:
    """Shared Dimension B window join + aggregation for all three approaches.

    Joins each spine row (account_id, observation_date) to the cycles whose
    ``evidence_date_col`` (the statement that shows the cycle's result) falls
    in (_any_window_start, observation_date]. The window is open at the start
    because the cycle whose result statement IS t0 is the pre-onset payment
    that failed to stop the account going delinquent, and closed at the end
    because the statement at observation_date is already known at the
    observation. Two windows share that one join:

    * "Regular": sums ``qualifying_months_expr`` (per-cycle int) over cycles
      after _window_start (3 months at 61-180 DPD, 6 at 180+) into
      dlq_payment_qualifying_month_cnt;
    * "any payment": flags every joined cycle where ``any_payment_expr``
      (per-cycle boolean) holds as dlq_payment_any_flag, over the whole
      _any_window_start window (same as Regular at 61-180, 12 months at 180+).

    Both expressions reference the cycles side via the ``c`` alias. Each
    approach supplies only its own per-cycle expressions; the join and the
    grouping are identical across approaches. ``spine_with_window`` must carry
    _window_start / _window_months / _any_window_start / _any_window_months.
    """
    joined = spine_with_window.alias("s").join(
        cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col(f"c.{evidence_date_col}") > F.col("s._any_window_start"))
        & (F.col(f"c.{evidence_date_col}") <= F.col("s.observation_date")),
        "left",
    )
    in_regular_window = F.col(f"c.{evidence_date_col}") > F.col("s._window_start")
    return joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.observation_date").alias("observation_date"),
        F.col("s.t0").alias("t0"),
        F.col("s._window_months").alias("dlq_payment_window_months"),
        F.col("s._any_window_months").alias("dlq_payment_any_window_months"),
    ).agg(
        F.coalesce(
            F.sum(F.when(in_regular_window, qualifying_months_expr)), F.lit(0)
        ).alias("dlq_payment_qualifying_month_cnt"),
        F.coalesce(
            F.max(F.when(any_payment_expr, F.lit(1)).otherwise(F.lit(0))),
            F.lit(0),
        ).alias("dlq_payment_any_flag"),
    )


def aggregate_pre_dlq_window(
    spells: DataFrame,
    cycles: DataFrame,
    paid_as_billed_col: str,
    evidence_date_col: str = "next_billing_date",
    min_months_due: int = _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE,
) -> DataFrame:
    """Shared Dimension C window join + aggregation for both approaches.

    Joins each spell to the cycles whose ``evidence_date_col`` (the
    statement/month-end row that shows the cycle's result) falls in
    [_window_start, t0), counts cycles with a due amount
    (pre_dlq_months_due_n) and those flagged ``paid_as_billed_col``
    (pre_dlq_months_paid_as_billed_n), and derives
    pre_dlq_paid_as_billed_share – NULL below ``min_months_due``
    (the "no_record" condition downstream). ``cycles`` must carry ``_has_due``
    and the named boolean column.
    """
    joined = spells.alias("s").join(
        cycles.alias("c"),
        (F.col("s.account_id") == F.col("c.account_id"))
        & (F.col(f"c.{evidence_date_col}") >= F.col("s._window_start"))
        & (F.col(f"c.{evidence_date_col}") < F.col("s.t0")),
        "left",
    )
    agg = joined.groupBy(
        F.col("s.account_id").alias("account_id"),
        F.col("s.spell_id").alias("spell_id"),
        F.col("s.t0").alias("t0"),
    ).agg(
        F.coalesce(F.sum(F.col("c._has_due").cast("int")), F.lit(0)).alias(
            "pre_dlq_months_due_n"
        ),
        F.coalesce(
            F.sum((F.col("c._has_due") & F.col(f"c.{paid_as_billed_col}")).cast("int")),
            F.lit(0),
        ).alias("pre_dlq_months_paid_as_billed_n"),
    )
    return agg.withColumn(
        "pre_dlq_paid_as_billed_share",
        F.when(
            F.col("pre_dlq_months_due_n") >= min_months_due,
            F.col("pre_dlq_months_paid_as_billed_n").cast("double")
            / F.col("pre_dlq_months_due_n").cast("double"),
        ),  # NULL otherwise -> "No record" downstream
    )


def pooled_trailing_broken_streak(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    agreement_bridge: DataFrame,
    int_ptp: DataFrame,
    ptp_instalments: DataFrame,
    int_settlement: DataFrame,
    settlement_instalments: DataFrame,
    months_back: int = _TAU_A3V2_COMMITMENTS_WINDOW_M,
    n_latest: int = _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N,
) -> DataFrame:
    """Dimension A streak: the broken run at the head of the latest concluded instalments.

    Pools PTP and settlement instalments of an agreement, keeps those due in the last
    months_back months, takes the latest n_latest concluded ones and counts the
    consecutive broken ones from the most recent. A streak of n_latest means "the last
    N concluded were all broken".

    Concluded = due on or before the observation date and either fully paid or overdue
    (an instalment due today and still unpaid is not concluded). Broken = overdue, i.e.
    not fully paid, partial payments included. Paid / overdue and the cancelled-
    instalment rule are dcore's own (instalment_amount_flags,
    null_cancelled_instalment_fields). On the same due date a broken instalment ranks
    first (the stricter reading).

    Args:
        agreement_bridge: (iagreementseqno, observation_date, ...) rows to score.
        int_ptp / ptp_instalments: dcore_int_ptp, dcore_prm_promise_instalments.
        int_settlement / settlement_instalments: dcore_int_settlement,
            dcore_prm_settlement_schedule_instalments.

    Returns:
        (iagreementseqno, observation_date, commitments_broken_streak) for agreements
        with at least one concluded instalment in the window; absent agreements have
        no concluded instalment (streak 0 for the caller).
    """
    instalment_cols = ["agreement_id", "due_date", "due_amount", "payment_amount"]
    ptp = null_cancelled_instalment_fields(
        int_ptp.select("agreement_id", "promise_seqno").join(
            ptp_instalments.select(
                "promise_seqno",
                "due_date",
                "due_amount",
                "payment_amount",
                "instalment_status",
            ),
            on="promise_seqno",
        ),
        PTP_INSTALMENT_STATUS_CANCELLED,
    )
    settlement = null_cancelled_instalment_fields(
        int_settlement.select("agreement_id", "rps_seqno").join(
            settlement_instalments.select(
                "rps_seqno",
                "due_date",
                "due_amount",
                "payment_amount",
                "instalment_status",
            ),
            on="rps_seqno",
        ),
        SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
    )
    instalments = (
        ptp.select(*instalment_cols)
        .unionByName(settlement.select(*instalment_cols))
        .where(F.col("due_date").isNotNull())
    )

    scored = (
        agreement_bridge.where(F.col("iagreementseqno").isNotNull())
        .select(F.col("iagreementseqno").alias("agreement_id"), "observation_date")
        .distinct()
    )
    in_window = scored.join(instalments, on="agreement_id").where(
        (F.col("due_date") <= F.col("observation_date"))
        & (F.col("due_date") >= F.add_months(F.col("observation_date"), -months_back))
    )

    is_paid, _, is_overdue = instalment_amount_flags()
    ranked = (
        in_window.where(is_paid | is_overdue)
        .withColumn("_broken", F.when(is_overdue, 1).otherwise(0))
        .withColumn(
            "_rn",
            F.row_number().over(
                Window.partitionBy("agreement_id", "observation_date").orderBy(
                    F.col("due_date").desc(), F.col("_broken").desc()
                )
            ),
        )
        .where(F.col("_rn") <= n_latest)
    )
    return (
        ranked.groupBy("agreement_id", "observation_date")
        .agg(
            F.count(F.lit(1)).alias("_n"),
            F.min(F.when(F.col("_broken") == 0, F.col("_rn"))).alias("_first_kept"),
        )
        .select(
            F.col("agreement_id").alias("iagreementseqno"),
            "observation_date",
            F.coalesce(F.col("_first_kept") - 1, F.col("_n"))
            .cast("int")
            .alias("commitments_broken_streak"),
        )
    )


def _plan_starts(int_ptp: DataFrame, int_settlement: DataFrame) -> DataFrame:
    """(agreement_id, start, plan_type) for every non-cancelled PTP and settlement plan.

    PTP start = coalesce(promise_start, event_date); settlement start = event_date (its
    first instalment due date, the only date dcore keeps for it) [CONFIRM: proxy].
    """
    ptp = int_ptp.where(F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1).select(
        "agreement_id",
        F.coalesce(F.col("promise_start"), F.col("event_date")).alias("start"),
        F.lit("ptp").alias("plan_type"),
    )
    settlement = int_settlement.where(
        F.coalesce(F.col("is_cancelled"), F.lit(0)) != 1
    ).select(
        "agreement_id",
        F.col("event_date").alias("start"),
        F.lit("settlement").alias("plan_type"),
    )
    return ptp.unionByName(settlement)


def flag_plans_on_record(
    signals: DataFrame, int_ptp: DataFrame = None, int_settlement: DataFrame = None
) -> DataFrame:
    """Flag a PTP / settlement on record between T0 and the observation date.

    Adds ptp_on_record_flag and arrangement_on_record_flag (1 when the agreement has a
    non-cancelled PTP / settlement plan started in [t0, observation_date]; a NULL t0 is
    an unbounded lower bound). Both are NULL when the plan tables are not supplied.
    Used by the No-response strong negative ("no promise or arrangement on record").

    Args:
        signals: rows with account_id, observation_date, iagreementseqno, t0.
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
    """
    keys = ["account_id", "observation_date"]
    if int_ptp is None or int_settlement is None:
        return signals.withColumn(
            "ptp_on_record_flag", F.lit(None).cast("int")
        ).withColumn("arrangement_on_record_flag", F.lit(None).cast("int"))

    scored = (
        signals.where(F.col("iagreementseqno").isNotNull())
        .select(*keys, "iagreementseqno", "t0")
        .distinct()
    )
    on_record = (
        scored.join(
            _plan_starts(int_ptp, int_settlement),
            F.col("iagreementseqno") == F.col("agreement_id"),
        )
        .where(
            (F.col("start") <= F.col("observation_date"))
            & (F.col("t0").isNull() | (F.col("start") >= F.col("t0")))
        )
        .groupBy(*keys)
        .agg(
            F.max(F.when(F.col("plan_type") == "ptp", 1).otherwise(0)).alias(
                "ptp_on_record_flag"
            ),
            F.max(F.when(F.col("plan_type") == "settlement", 1).otherwise(0)).alias(
                "arrangement_on_record_flag"
            ),
        )
    )
    return (
        signals.join(on_record, on=keys, how="left")
        .withColumn(
            "ptp_on_record_flag", F.coalesce(F.col("ptp_on_record_flag"), F.lit(0))
        )
        .withColumn(
            "arrangement_on_record_flag",
            F.coalesce(F.col("arrangement_on_record_flag"), F.lit(0)),
        )
    )


def flag_followups_after_refusal(  # pylint: disable=too-many-locals
    signals: DataFrame,
    int_ptp: DataFrame = None,
    int_settlement: DataFrame = None,
    transactions: DataFrame = None,
) -> DataFrame:
    """Flag what followed the latest right-party refusal, for the Refusal strong negative.

    Only rows whose last_rpc_disposition is the refusal ('rtp') are looked at; the
    others get 0. Adds, all dated strictly after last_rpc_date and up to the
    observation date:
        refusal_followed_by_commitment (int) – a non-cancelled PTP (start =
            coalesce(promise_start, event_date)) or settlement (start = event_date,
            its first instalment due date, the only date dcore keeps) of the agreement.
            0 when the plan tables are not supplied.
        refusal_followed_by_payment (int)     – a card payment of any amount.
        refusal_followed_by_payment_min_amount (int) – card payments since the refusal
            sum to at least the 180+ minimum payment (Dimension B's guard).
        payment_evidence_available (int)      – 1 when transactions were supplied; when
            0 the payment flags are 0 and the caller falls back to Dimension B's
            any-payment flag.

    Args:
        signals: Rows with account_id, observation_date, iagreementseqno,
            last_rpc_disposition, last_rpc_date.
        int_ptp / int_settlement: dcore_int_ptp / dcore_int_settlement.
        transactions: crx_cc_transactions (contract_id, observation_date = banking
            date, txn_amount_aed, txn_category, is_post_block_x_fee).
    """
    keys = ["account_id", "observation_date"]
    refusals = (
        signals.where(F.col("last_rpc_disposition") == "rtp")
        .select(*keys, "iagreementseqno", "last_rpc_date")
        .distinct()
    )

    result = signals
    if int_ptp is not None and int_settlement is not None:
        starts = _plan_starts(int_ptp, int_settlement)
        followed_commitment = (
            refusals.join(
                starts,
                (F.col("iagreementseqno") == F.col("agreement_id"))
                & (F.col("start") > F.col("last_rpc_date"))
                & (F.col("start") <= F.col("observation_date")),
            )
            .select(*keys)
            .distinct()
            .withColumn("refusal_followed_by_commitment", F.lit(1))
        )
        result = result.join(followed_commitment, on=keys, how="left")
    else:
        result = result.withColumn("refusal_followed_by_commitment", F.lit(0))

    if transactions is not None:
        payments = transactions.where(
            (F.col("txn_category") == "payment") & (F.col("is_post_block_x_fee") == 0)
        ).select(
            F.col("contract_id").alias("account_id"),
            F.col("observation_date").alias("banking_date"),
            "txn_amount_aed",
        )
        followed_payment = (
            refusals.join(
                payments,
                (refusals["account_id"] == payments["account_id"])
                & (payments["banking_date"] > refusals["last_rpc_date"])
                & (payments["banking_date"] <= refusals["observation_date"]),
            )
            .groupBy(refusals["account_id"], refusals["observation_date"])
            .agg(
                F.lit(1).alias("refusal_followed_by_payment"),
                F.when(
                    F.sum("txn_amount_aed")
                    >= _TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS,
                    F.lit(1),
                )
                .otherwise(F.lit(0))
                .alias("refusal_followed_by_payment_min_amount"),
            )
        )
        result = result.join(followed_payment, on=keys, how="left").withColumn(
            "payment_evidence_available", F.lit(1)
        )
    else:
        result = (
            result.withColumn("refusal_followed_by_payment", F.lit(0))
            .withColumn("refusal_followed_by_payment_min_amount", F.lit(0))
            .withColumn("payment_evidence_available", F.lit(0))
        )

    flag_cols = [
        "refusal_followed_by_commitment",
        "refusal_followed_by_payment",
        "refusal_followed_by_payment_min_amount",
    ]
    for col in flag_cols:
        result = result.withColumn(col, F.coalesce(F.col(col), F.lit(0)).cast("int"))
    return result.withColumn(
        "payment_evidence_available", F.col("payment_evidence_available").cast("int")
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/constants.py`
action: delete · base sha256 `5dbdccbf99babe8653bd5a4594f6d3bd060d701463a8edca5027f85ec56d4832` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Constants for the cc_a3_payment_credibility pipeline, grouped by section.

State = points from Dimension A (commitments kept), B (payments while delinquent) and
C (record before delinquency), demoted one level by a strong negative. Every threshold
tagged [CONFIRM] is a proposal from logs/A3_credibility_shared.xlsx ("A3 framework",
block 5), not yet measured on PROD. The DCORE call codes and result-name sets live in
``crx_persona/_dcore_codes.py`` (shared with A2, which A3 does not import).
"""

# ── Evidence-method switches (params:a3_dlq_/a3_pre_dlq_payment_evidence_method) ─
# Canonical values; parameters_crx_persona.yml must match one of these exactly.
# Dimension B accepts all three; Dimension C only single_payment_cycle_count and
# dpd_bucket_movement.
_METHOD_SINGLE_PAYMENT_CYCLE_COUNT = "single_payment_cycle_count"  # default
_METHOD_PAYMENT_SUM_WATERFALL = "payment_sum_waterfall"
_METHOD_DPD_BUCKET_MOVEMENT = "dpd_bucket_movement"

# ── State: points cut-offs and confidence ─────────────────────────────────
# Total points (A+B+C), with no strong negative.
_TAU_A3V2_HIGH_FROM_POINTS = 4  # [CONFIRM] High
_TAU_A3V2_MODERATE_FROM_POINTS = 1  # [CONFIRM] at least Moderate
# Fixed confidence per state: evidence quality of the typical path, not a probability.
_CONF_HIGH = 0.90
_CONF_MODERATE = 0.75
_CONF_LOW = 0.60
_CONF_UNKNOWN = 0.00

# ── Strong negatives (each demotes the state by one level; they do not stack) ──
# Distinct contact dates needed before "no_response" fires (3 calls on one day are
# weaker evidence than 3 separate days).
_TAU_MIN_CONTACT_DATES = 3  # [CONFIRM]
# Tie-break when more than one fires on the same row.
_SB_PRIORITY = ("broken_commitments", "refusal", "no_response")  # [CONFIRM]

# ── Dimension A: commitments kept (PTP / settlement instalments) ──────────
_TAU_A3V2_COMMITMENTS_WINDOW_M = 12  # [CONFIRM] months of instalments considered
_TAU_A3V2_COMMITMENTS_MIN_CONCLUDED = 2  # [CONFIRM] concluded instalments for a pattern
_TAU_A3V2_COMMITMENTS_KEPT_RATE = 0.8  # [CONFIRM] paid share for "Kept"
# Kept-rate below this (with >= MIN_CONCLUDED), or the last N concluded all broken -> "Broken".
_TAU_A3V2_COMMITMENTS_BROKEN_RATE = 0.4  # [CONFIRM]
_TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N = 3  # [CONFIRM]

# ── Dimension B: payments while delinquent ────────────────────────────────
# Due amount per cycle = first non-zero of overdue_bucket_07..01, then minimum_due (see
# _signals_common.resolve_due_amount_m). [CONFIRM – the highest-impact assumption]

# Windows after onset, in months, chosen by the row's DLQ bucket (>= 8 is 180+).
_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180 = 3  # [CONFIRM] "Regular" and any-payment window
_TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS = 6  # [CONFIRM] "Regular" window
# Any-payment window (Some vs None, and the refusal / no_response strong negatives);
# 61-180 uses 3 for both tests.
_TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS = 12  # [CONFIRM]

# "Regular" = qualifying months in the window.
_TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180 = 2  # [CONFIRM] 2 of 3
_TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS = 3  # [CONFIRM] 3 of 6

# When only overdue_bucket_08 is left, the cycle has no due amount; the default method uses
# the account's frozen baseline instead: the average minimum_due of its last N months with
# a positive minimum_due before it stagnated (_signals_common.resolve_bucket08_fallback_due).
_TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS = 12  # [CONFIRM]

# What qualifies a month: payment >= max(share x due_amount_m, minimum payment).
_TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE = 1.0  # [CONFIRM] full due amount
# AED floor at 180+ for a qualifying month and for the any-payment flag. 61-180 has none;
# bucket-movement credits carry no amount, so only amount-based parts use it.
_TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS = 100.0  # [CONFIRM]

# Billing-cycle sanity (build_a3_payment_cycles). A cycle runs to the next statement that
# exists, so missing statements (2021-2023 gap, 2024-11-12 run) make one long cycle.
# Keep cycles starting up to this many days before the floor; drop cycles longer than the max
# (a normal cycle is 26-35 days).
_PAYMENT_CYCLE_FLOOR_LOOKBACK_D = 35  # [CONFIRM]
_PAYMENT_CYCLE_MAX_LENGTH_D = 62  # [CONFIRM]

# dpd_bucket_movement: the highest DLQ bucket (max overdue bucket + 1; only 8 exist). A flat
# bucket at the cap is ambiguous, so it defers to the waterfall count for that cycle.
_DLQ_LEVEL_SATURATED = 9

# payment_sum_waterfall: overdue_bucket_08 is the multi-month accumulator, so it is split
# into synthetic "one month" slices sized off the account's trailing minimum_due average.
_TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M = 24  # [CONFIRM] prior rows averaged
# Maximum slices (one payment cannot credit more months than the longest window).
_TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP = _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS

# ── Dimension C: record before delinquency ────────────────────────────────
_TAU_A3V2_PRE_DLQ_WINDOW_M = 12  # [CONFIRM] months before onset (T0)
_TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE = 3  # [CONFIRM] fewer billed months = "No record"
_TAU_A3V2_PRE_DLQ_CLEAN_SHARE = 0.8  # [CONFIRM] share of billed months paid for "Clean"
# Per-cycle amount for "paid as billed": payment >= this x due_amount_m (single_payment_
# cycle_count only; dpd_bucket_movement has no amount check). Strict 100% since 2026-10-30;
# it was 0.85 (2026-10-22). Set below 1.0 to relax again.
_TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE = 1.0  # [CONFIRM]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/_signals_common.py`
action: delete · base sha256 `aa3f53f0215876ede244204c340e40adade9852fedb87d42620bc34bed994ea4` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-native Dimension B window resolver for rl_a3_payment_credibility.

Dimension C's window resolver needs no RL-native rebuild – CC's
resolve_pre_dlq_spell_window (cc_a3_payment_credibility._signals_common)
only needs account_id/observation_date/spell_id/t0/spell_end, no CC-bucket
-specific column, so it is reused unchanged via rl_spine_as_cc_shim() in
nodes.py directly. Only Dimension B's window resolver needs a rebuild here
because CC's resolve_dlq_payment_window reads cc_spine.dlq_bucket_from_hist
(a column rl_spine_as_cc_shim's cc_spine_shim does not carry) and its 3mo/6mo
split threshold is a CC-bucket-numeral that does not translate literally to
RL's 0-7 scale.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import (
    join_spine_to_spell,
    rl_spine_as_cc_shim,
)
from enbd_collections.pipelines.crx_persona.rl_a3_payment_credibility.constants import (
    _DLQ_WINDOW_SPLIT_THRESHOLD_RL,
    _TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP,
    _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID,
)


def resolve_rl_dlq_payment_window(
    crx_rl_a4_spine: DataFrame,
    crx_rl_a3_dlq_cycles: DataFrame,
) -> DataFrame:
    """RL-native rebuild of cc_a3_payment_credibility._signals_common
    .resolve_dlq_payment_window.

    Reuses join_spine_to_spell (via rl_spine_as_cc_shim) unchanged for the
    account/spell/t0 join – only the window-length decision itself is new.
    No separate spell-table input is needed (unlike CC's
    resolve_dlq_payment_window, which takes crx_cc_spell_table): RL's
    crx_rl_a4_spine already carries spell_id/t0 directly, and
    rl_spine_as_cc_shim derives both shim halves from it alone. Current
    dlq_bucket is read from crx_rl_a3_dlq_cycles' dlq_level_m at
    (account_id, billing_date == observation_date), not from the spine
    (rl_spine_as_cc_shim's cc_spine_shim carries no bucket column).

    Window-depth split at _DLQ_WINDOW_SPLIT_THRESHOLD_RL (7, RL's single
    terminal 180+ bucket) – see constants.py for why this is not a literal
    copy of CC's ">= 8" threshold.

    Args:
        crx_rl_a4_spine: RL spine – (account_id, observation_date, spell_id, t0).
        crx_rl_a3_dlq_cycles: build_rl_a3_dlq_cycles output – (account_id,
            billing_date, dlq_level_m).

    Returns:
        DataFrame with (account_id, observation_date, t0, _window_months,
        _window_start, _any_window_months, _any_window_start, _min_payment_aed (100 in
        the deep band, else 0). The "any payment"
        window (Some vs None, strong negatives) is 12 months in the deep band, the
        regular window elsewhere; "Regular" keeps _window_*.
    """
    cc_spine_shim, spell_table_shim = rl_spine_as_cc_shim(crx_rl_a4_spine)
    spine_with_spell = join_spine_to_spell(cc_spine_shim, spell_table_shim)

    current_bucket = crx_rl_a3_dlq_cycles.select(
        F.col("account_id"),
        F.col("billing_date").alias("observation_date"),
        F.col("dlq_level_m").alias("_current_dlq_bucket"),
    )

    spine_with_dlq = spine_with_spell.join(
        current_bucket, on=["account_id", "observation_date"], how="left"
    )

    is_deep = F.col("_current_dlq_bucket") >= _DLQ_WINDOW_SPLIT_THRESHOLD_RL

    def _window_start(months_col):
        return F.greatest(
            F.col("t0"),
            F.add_months(F.col("observation_date"), -months_col),
        )

    return (
        spine_with_dlq.withColumn(
            "_window_months",
            F.when(is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP)).otherwise(
                F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID)
            ),
        )
        .withColumn(
            "_any_window_months",
            F.when(
                is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP)
            ).otherwise(F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID)),
        )
        .withColumn("_window_start", _window_start(F.col("_window_months")))
        .withColumn("_any_window_start", _window_start(F.col("_any_window_months")))
        .withColumn(
            "_min_payment_aed",
            F.when(is_deep, F.lit(_TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP)).otherwise(
                F.lit(0.0)
            ),
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/constants.py`
action: delete · base sha256 `4842f35028d9ecb1d863e1518f58556477b3794309ce09d0db43f8fe36c07f0c` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Constants for RL A3 Payment Credibility's Dimension B and C, grouped by section.

RL has the same three approaches as CC, built on RL-native primitives (see nodes.py):
  - single_payment_cycle_count (default): each month judged on its own, cash vs EMI.
  - payment_sum_waterfall (Dimension B): floor(window cash / EMI); RL has no bucket
    ladder to walk, so it is a division.
  - dpd_bucket_movement: payment inferred from month-over-month bucket movement.

These are RL-local copies of cc_a3_payment_credibility/constants.py, deliberately not
imported (a CC retune must not move RL). RL has its own switches,
rl_a3_dlq_payment_evidence_method / rl_a3_pre_dlq_payment_evidence_method; the
constants below are their defaults. Values tagged [CONFIRM] are inherited from CC
pending RL business validation.
"""

from enbd_collections.pipelines.crx_persona.cc_a3_payment_credibility.constants import (
    _METHOD_SINGLE_PAYMENT_CYCLE_COUNT,
)

# ── Evidence-method defaults (same as CC; the params override them) ──────────
_DLQ_PAYMENT_EVIDENCE_METHOD_RL = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT
_PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL = _METHOD_SINGLE_PAYMENT_CYCLE_COUNT

# ── Bucket-scale translations (CC scale 0-9, delinquency from 2; RL 0-7, from 1) –
# Cross-checked against _dpd_journey/constants.py (RL: offset 1, top 7).
_DLQ_LEVEL_SATURATED_RL = 7  # RL's highest bucket (CC: 9)
_DLQ_WINDOW_SPLIT_THRESHOLD_RL = 7  # the 180+ band is the single bucket 7 (CC: >= 8)
_PRE_DLQ_NOT_DELINQUENT_MAX_RL = 0  # "not in any overdue bucket" (CC: <= 1)

# ── Dimension B: payments while delinquent ───────────────────────────────
# Windows after onset, in months, by band: MID = RL 60-180 (dlq 3-6), DEEP = 180+ (dlq 7).
_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID = 3  # [CONFIRM] "Regular" and any-payment window
_TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP = 6  # [CONFIRM] "Regular" window
# Any-payment window: Some vs None and the refusal / no_response strong negatives.
# MID uses 3 for both tests.
_TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP = 12  # [CONFIRM]

# "Regular" = qualifying months in the window.
_TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID = 2  # [CONFIRM] 2 of 3
_TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP = 3  # [CONFIRM] 3 of 6

# What qualifies a month: cash >= max(share x EMI, minimum cash).
_TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE = 1.0  # [CONFIRM] full EMI
# AED floor in the DEEP band for a qualifying month and for the any-payment flag (and
# the EMI-month sum); none in the MID band.
_TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP = 100.0  # [CONFIRM]

# dpd_bucket_movement credits the RAW bucket delta on an improvement (no CC-style "+1
# unless cured"); [CONFIRM] – no partially-cured RL account has been hand-traced yet.

# ── Dimension C: record before delinquency ───────────────────────────────
_TAU_RL_A3V2_PRE_DLQ_WINDOW_M = 12  # [CONFIRM] months before onset (T0)
_TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE = 3  # [CONFIRM] fewer billed months = "no_record"
# Share of billed months paid as billed for "clean".
_TAU_RL_A3V2_PRE_DLQ_CLEAN_SHARE = 0.8  # [CONFIRM]
# Cash needed for "paid as billed": >= this x EMI. Strict 100% since 2026-10-30 (was
# 0.85, inherited from CC); set below 1.0 to relax again.
_TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE = 1.0  # [CONFIRM]
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
Clean up after mirror bundle 17_a3_credibility_engine.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id (CC datasets for the CC model_ids, RL for RL); skip folders that do not exist:
  - the check outputs: `crx_<p>_a3_check_payments`, `crx_<p>_a3_check_dcore`;
  - the retired A3 datasets: `crx_<p>_a3_dlq_payment_signals_dpd_bucket_movement`, `crx_<p>_a3_dlq_payment_signals_payment_sum_waterfall`, `crx_<p>_a3_pre_dlq_payment_signals_dpd_bucket_movement`.
- **Remove the temporary check** (everything marked TEMPORARY for the A3 bundle):
  - `conf/base/catalog/catalog_crx.yml`: the four `crx_<p>_a3_check_*` entries and their comment block;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_a3_check` and `crx_rl_a3_check` entries and their comments;
  - `crx_persona/cc_a3_payment_credibility/` and `rl_a3_payment_credibility/`: `create_check_pipeline` in `pipeline.py` (with its import and the TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete `crx_persona/a3_credibility/check.py`.
- **The judge.** Keep `params:a3_kept_by` as decided until the mirror sends the bundle that removes the losing option (do not remove it here).

  Then check that `kedro registry list` still works and that `grep -rn "a3_check" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
