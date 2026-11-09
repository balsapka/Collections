# Mirror bundle 20 — A3 — promise events judged by payment on GRR's deadline over 12 months, Moderate from 2

apply_bundle version: 7 · built 2026-11-09 from `58df544..8f9d69e` · source: 1 added, 14 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/20_a3_promise_events_grr_deadline.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '20_a3_promise_events_grr_deadline.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/20_a3_promise_events_grr_deadline.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **Leftovers of the DCORE judge.** `grep -rn "a3_kept_by\|instalment_amount_flags\|KEPT_BY\|GRACE" src conf` must find nothing in the A3 code or conf (`instalment_amount_flags` may stay in the DCORE feature code). Remove any workplace-only reader of `a3_kept_by` and report it.
2. **Catalog.** `crx_cc_a3_promise_events`, `crx_rl_a3_promise_events` and the four `crx_<p>_a3_check_*` entries exist exactly once; list every top-level key the apply removed from `catalog_crx.yml` compared with the last commit (`git diff` of the file, lines starting with `-` and no indent) and put back any that is not an A3 check entry.
3. **Tests.** Update the A3 tests for the new `build_commitment_signals(episode, events)` signature and `build_promise_events`; drop tests of the DCORE judge. The mirror's spec test (`workplace_mirror/checks/a3_engine_spec.py`) has the cases.

Then check: `kedro registry list | grep a3` lists `crx_cc_a3_check` and `crx_rl_a3_check`.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A3: promise events judged by payment on GRR's deadline over 12 months, Moderate from 2 (bundle 20)" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/20_a3_promise_events_grr_deadline.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

Bundle 17's real A3 output is the baseline: do not re-run A3 before the check. Run for **all four model_ids** (`rl_60_180`, `cc_60_180`, `rl_180_plus`, `cc_180_plus`; set `model_id` in `conf/dev/globals_dev.yml`).

**Step 7.** Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a3_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back every block from `=== A3 … START ===` to `=== A3 … END ===` (4 per model_id). A summary file is fine.

**Step 8.** After the blocks are reviewed: write the real output (no raw extract rebuild needed):

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

For every model_id. Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Changes A3 payment credibility's Dimension A to GRR's promise events judged by a sufficient payment over the last 12 months, moves the Moderate cut-off to 2 points, and removes the DCORE judge option. Apply on top of bundles 17–19 and bundle 17's cleanup.

**What changes in the logic** (spec `specs/A3_credibility_spec.md`, D-A3-24, D-A3-25, D-A3-26):
- **Promises (Dimension A) are promise events, judged by payment.**
  - **Events:** every non-cancelled PTP and settlement plan (dated at its start), plus every follow-up promise (`_dcore_codes.PROMISE_EVENT`: promise to pay, scheduled, digital collect, pay at salary) that no plan claims. Follow-up promises less than 8 days apart are one event; a plan takes its nearest follow-up promise within 7 days.
  - **Judged once:** paid when the payments after the event day reach the due of the cycle open on that day (at least 100 AED) by the deadline. Partial: 100 AED or more but below it (counts as not kept). Otherwise none.
  - **Deadline (GRR):** CC the next statement after the promise, however close; RL the end of the next month. One constant (`PROMISE_DEADLINE`); the 30-day alternative is built in and runs in the check.
  - **Window:** the last 12 months up to the observation date, regardless of the episode start (was: from the episode start), so promises from an earlier delinquency episode count. Contacts and the refusal flag stay on the current episode.
  - The ladder is unchanged (Kept / Partly kept / Thin / Broken); points Kept 2, Partly 1, Thin 0, Broken −1.
- **Moderate from 2 points** (was 1), High from 4; a refusal still takes one rung off.
- **Contact disposition:** payment reports (partially paid, claims made payment, KSA paid / partial payment, customer kept promise made) now read `paid`, not `ptp` (diagnostic only; the refusal rule is unchanged).

**Code:** `a3_credibility/sources.py` gains `build_promise_events` (new dataset `crx_<p>_a3_promise_events`); `build_commitment_signals` reads the events; the DCORE judge, `KEPT_BY`, `GRACE` and `params:a3_kept_by` go. Output: `a3_kept_by` becomes `a3_promise_deadline`, `commitments_partial` is added. `_dcore_codes` gains `PROMISE_EVENT` and `PAYMENT_REPORTED`.

**Check** (temporary, `a3_credibility/check.py`, pipelines `crx_<p>_a3_check`): the impact of the bundle on the latest month, step by step, against bundle 17's real output: `old` (bundle 17) → `old_m2` (Moderate from 2) → `grr_ep` (promise events, GRR's deadline, the episode window) → `grr` (as shipped, 12 months; `crx_<p>_a3_check_grr`), plus `d30` (30 days; `crx_<p>_a3_check_30d`). Blocks: `A3 OUTPUT` (each state, then one crosstab per step with the share changed: whole bundle, thresholds, promise events, 12-month window, 30 days instead of GRR), `A3 PROMISES` (events by kind and source, outcomes, events concluded before the episode start, follow-up names, accounts with a concluded promise), `A3 LEVELS` (Dimension A levels per variant and per step), `A3 CONTACTS` (refusal and disposition old × new).

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
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/constants.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a3_credibility/sources.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `ae3b9a642b8f1dc1cbce1a9570ea72dc5e616d1119439e3a20d7b9305fa6a87d` · base trailing newline: yes · new sha256 `9c253367e800b9b108a4610c34e7c85624138e21276e016fb4dff06ae74733c2` · new trailing newline: yes

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

# TEMPORARY (A3 bundle 20): the new A3 on the latest month, GRR's deadline and 30 days
# (the A3 check). Remove these entries, check.py, the check pipelines and the HDFS
# folders after the check.
crx_cc_a3_check_grr:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_check_grr"
  save_args:
    mode: overwrite

crx_cc_a3_check_30d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a3_check_30d"
  save_args:
    mode: overwrite

crx_rl_a3_check_grr:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_check_grr"
  save_args:
    mode: overwrite

crx_rl_a3_check_30d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a3_check_30d"
  save_args:
    mode: overwrite
`````

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `2ac7620a43b254254948998ee22e49c4f0e448ced21f4da5acbaac8509545023` · base trailing newline: yes · new sha256 `d9ca974faf8c9e332925ec3e5bb8cc90ba8bdea3114a3cd2060736023c6e0b00` · new trailing newline: yes

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
action: replace · base sha256 `019325f81c26e1b090cb161e291597f37814e7076091dec9b8cb804149cfb25c` · base trailing newline: yes · new sha256 `034577e2961b1fee5629fab92523d1255fea1ed33d7633a035ced64abe303bd8` · new trailing newline: yes

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
        # TEMPORARY (A3 bundle 20): the A3 check; removed by the bundle's cleanup.
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
        # TEMPORARY (A3 bundle 20): the A3 check; removed by the bundle's cleanup.
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
action: replace · base sha256 `368535c2a2589af988f18e163af1d0177cb41f7c2b75b521696297d759898e02` · base trailing newline: yes · new sha256 `f92b5552b6ecc31958e72066eeabc78f2f1608fe805cfdef687e1deea01b444b` · new trailing newline: yes

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

# A3 promise events (D-A3-25): a commitment to pay logged in the follow-up, any action
# code. Explicit promises and promises to pay at salary; SOFTPTP, re-affirmations
# (RETAIN PTP), arrangements (judged from their settlement record) and payment reports
# are not events. EOSB_PTP_DOCUMENTS and HISTORICAL PROMISE TO PAY are near-empty.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PROMISE_EVENT = frozenset(
    {
        "CODE25 WILL PAY AT SALARY",
        "DIGITAL COLLECT  PTP SUBSCRIBED",
        "EOSB_PTP_DOCUMENTS",
        "HISTORICAL PROMISE TO PAY",
        "KSA/CUSTOMER WILL PAY AT SALARY",
        "KSA/PROMISE TO PAY",
        "PROMISE TO PAY",
        "PROMISE TO PAY PARTIALLY",
        "PROMISE TO PAY SCHEDULED",
        "WILL PAY AT SALARY",
    }
)

# A3: a payment reported as made by the customer or DCORE (confirmed, partial or
# claimed), not a promise. Drives the "paid" contact disposition.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
PAYMENT_REPORTED = frozenset(
    PAYMENT_CONFIRMED
    | {
        "CLAIMS MADE PAYMENT",
        "CUSTOMER KEPT PROMISE MADE",
        "KSA/PAID AMOUNT",
        "KSA/PARTIAL PAYMENT",
        "PARTIALLY PAID",
    }
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/__init__.py`
action: replace · base sha256 `c9cbc47de883cf9d1e10b33199812d05dfc0082e0e209aba4894d5cf855a1b35` · base trailing newline: yes · new sha256 `5e5b483650ed26f7aa492d416909054d34430919283db04298db2b6da507a891` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
from .sources import (
    build_a3_episode,
    build_cycle_ledger,
    build_instalments,
    build_promise_events,
)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/check.py`
action: add · new sha256 `d9489a656f41c60a0e2116d1c8842b51a56c87d871fe0ca720eceda96f38f61e` · new trailing newline: yes

New:

`````python
"""TEMPORARY (A3 bundle 20): the impact of the bundle on the latest month, against the A3
output persisted before it (bundle 17: instalments, Moderate from 1). Variants:

- ``old``: bundle 17 as persisted; ``old_m2``: its points with Moderate from 2;
- ``grr_ep``: promise events, GRR's deadline, the episode window (bundle 17's);
- ``grr``: as shipped (12 months regardless of the episode, D-A3-26);
- ``d30``: as shipped with the 30-day deadline.

old -> old_m2 is the threshold step, old_m2 -> grr_ep the events, grr_ep -> grr the
window. Logs ``A3 OUTPUT``, ``A3 PROMISES``, ``A3 LEVELS``, ``A3 CONTACTS``. Removed by
the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a3_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .classify import build_a3_credibility
from .constants import HIGH_FROM, MODERATE_FROM, PROMISE_DEADLINE
from .pipeline import TAGS, create_a3_pipeline
from .signals import build_commitment_signals
from .sources import build_promise_events

logger = logging.getLogger(__name__)
NS = "a3_check"
DEADLINE_30D = {"cc": "30_days", "rl": "30_days_month_end"}


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def latest_month(obs_base: DataFrame, persona_end_date: str) -> DataFrame:
    """The base rows of persona_end_date's month."""
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return obs_base.filter(F.trunc("observation_date", "month") == month)


def episode_events(events: DataFrame, episode: DataFrame) -> DataFrame:
    """Events on or after the episode start (bundle 17's window; censored: no bound)."""
    start = episode.select(
        "account_id",
        F.when(
            ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
            F.col("episode_start"),
        ).alias("_start"),
    )
    return (
        events.join(start, "account_id", "left")
        .where(F.col("_start").isNull() | (F.col("event_date") >= F.col("_start")))
        .drop("_start")
    )


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _rung(points: Column, refusal: Column, state: Column) -> Column:
    """The A3 state from points with today's cut-offs (old rows, Moderate from 2)."""
    rung = F.when(points >= HIGH_FROM, 2).when(points >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(rung - F.coalesce(refusal, F.lit(False)).cast("int"), F.lit(0))
    label = F.element_at(F.array(*map(F.lit, ("low", "moderate", "high"))), rung + 1)
    return F.when(state == "payment_credibility_unknown", "unknown").otherwise(label)


def _short(state: Column) -> Column:
    return F.regexp_replace(state, "^payment_credibility_", "")


def compare_a3(
    old: DataFrame,
    grr_ep: DataFrame,
    grr: DataFrame,
    d30: DataFrame,
    events_grr: DataFrame,
    events_30d: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """The check blocks (latest month). The inputs are checkpointed first: the event
    tables are in memory, and every count would otherwise rebuild them."""
    grr_ep, grr, d30, events_grr, events_30d = (
        df.localCheckpoint() for df in (grr_ep, grr, d30, events_grr, events_30d)
    )
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    newest = F.row_number().over(
        Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    )
    o = (
        old.filter(F.trunc("observation_date", "month") == month)
        .withColumn("_r", newest)
        .where("_r = 1")
        .select(
            "account_id",
            _short(F.col("a3_state")).alias("old"),
            _rung(
                F.col("a3_points_total"), F.col("a3_refusal_flag"), F.col("a3_state")
            ).alias("old_m2"),
            F.col("a3_commitments_level").alias("old_level"),
            F.col("commitments_concluded").alias("old_concluded"),
            F.col("last_rpc_disposition").alias("old_disp"),
            F.col("a3_refusal_flag").alias("old_refusal"),
        )
    )
    g = grr.select(
        "account_id",
        "observation_date",
        "commitments_window_start",
        _short(F.col("a3_state")).alias("grr"),
        F.col("a3_commitments_level").alias("grr_level"),
        F.col("commitments_concluded").alias("grr_concluded"),
        F.col("last_rpc_disposition").alias("new_disp"),
        F.col("a3_refusal_flag").alias("new_refusal"),
    )
    ep = grr_ep.select(
        "account_id",
        _short(F.col("a3_state")).alias("grr_ep"),
        F.col("a3_commitments_level").alias("grr_ep_level"),
        F.col("commitments_concluded").alias("grr_ep_concluded"),
    )
    f = d30.select(
        "account_id",
        _short(F.col("a3_state")).alias("d30"),
        F.col("a3_commitments_level").alias("d30_level"),
        F.col("commitments_concluded").alias("d30_concluded"),
    )
    both = (
        g.join(ep, "account_id")
        .join(f, "account_id")
        .join(o, "account_id", "left")
        .localCheckpoint()
    )
    n = both.count()
    head = [f"model_id: {model_id}", f"rows new: {n}, old matched: {o.count()}"]

    lines = list(head)
    for col in ("old", "old_m2", "grr_ep", "grr", "d30"):
        lines += [f"state {col}:"] + _counts(both, [col], n)
    for a, b, what in (
        ("old", "grr", "whole bundle"),
        ("old", "old_m2", "thresholds"),
        ("old_m2", "grr_ep", "promise events"),
        ("grr_ep", "grr", "12-month window"),
        ("grr", "d30", "30 days instead of GRR"),
    ):
        moved = both.where(~F.col(a).eqNullSafe(F.col(b))).count()
        lines += [
            f"{a} x {b} ({what}), changed {moved} ({100 * moved / max(n, 1):.1f}%):"
        ]
        lines += _counts(both, [a, b], n)
    _block("A3 OUTPUT", lines)

    start = F.when(
        ~F.coalesce(F.col("episode_left_censored"), F.lit(False)),
        F.col("episode_start"),
    )
    win = grr.select(
        "account_id",
        "observation_date",
        "commitments_window_start",
        start.alias("_start"),
    )
    lines = list(head)
    for name, ev in (("GRR", events_grr), ("30 days", events_30d)):
        e = (
            ev.join(win, "account_id")
            .where(
                (F.col("event_date") >= F.col("commitments_window_start"))
                & (F.col("event_date") <= F.col("observation_date"))
            )
            .localCheckpoint()
        )
        concluded = e.where(F.col("promise_cutoff") <= F.col("observation_date"))
        m = e.count()
        lines += [f"[{name}] events in the window: {m}, by kind | source:"]
        lines += _counts(e, ["event_kind", "event_source"], m)
        c = concluded.count()
        lines += [f"[{name}] concluded: {c}, outcome by kind:"]
        lines += _counts(concluded, ["event_kind", "promise_outcome"], c)
        if name == "GRR":
            pre = concluded.where(F.col("event_date") < F.col("_start"))
            n_acc = pre.select("account_id").distinct().count()
            lines.append(
                "[GRR] concluded before the episode start (12-month window only): "
                f"{pre.count()} events, {n_acc} accounts; by outcome:"
            )
            lines += _counts(pre, ["promise_outcome"], c)
            lines += ["[GRR] follow-up names (events in the window):"]
            lines += _counts(
                e.where(F.col("event_name").isNotNull()), ["event_name"], m
            )
    lines += [
        "accounts with >= 1 concluded promise / instalment: "
        + ", ".join(
            f"{k} {both.where(F.col(c) > 0).count()}"
            for k, c in (
                ("old", "old_concluded"),
                ("GRR episode window", "grr_ep_concluded"),
                ("GRR", "grr_concluded"),
                ("30 days", "d30_concluded"),
            )
        )
    ]
    _block("A3 PROMISES", lines)

    lines = list(head)
    for col in ("old_level", "grr_ep_level", "grr_level", "d30_level"):
        lines += [f"{col}:"] + _counts(both, [col], n)
    for a, b in (
        ("old_level", "grr_level"),
        ("old_level", "grr_ep_level"),
        ("grr_ep_level", "grr_level"),
        ("grr_level", "d30_level"),
    ):
        lines += [f"{a} x {b}:"] + _counts(both, [a, b], n)
    _block("A3 LEVELS", lines)

    lines = head + ["refusal old x new:"]
    lines += _counts(both, ["old_refusal", "new_refusal"], n)
    lines += ["last right-party disposition old x new:"]
    lines += _counts(both, ["old_disp", "new_disp"], n)
    _block("A3 CONTACTS", lines)


def create_a3_check_pipeline(product: str, dues, payments) -> Pipeline:
    """The latest month through the A3 engine in the ``a3_check`` namespace (nothing real
    is overwritten): as shipped, with the episode window, with 30 days; then the
    blocks."""
    p = f"crx_{product}_a3"
    obs = f"crx_{product}_obs_base"
    final = f"{p}_check_grr"
    base = create_a3_pipeline(product, final, dues, payments)

    def ns(
        name: str,
    ) -> str:  # a check-only dataset name (no dots: Kedro reserves them)
        return f"{NS}__{name}"

    inputs = {i for i in base.inputs() if not i.startswith("params:")} - {obs}
    params = {i for i in base.all_inputs() if i.startswith("params:")}
    # Every intermediate gets an explicit check name, so the namespace only prefixes
    # the node names.
    scoped = pipeline(
        base,
        namespace=NS,
        inputs={**{i: i for i in inputs}, obs: ns("obs_latest")},
        outputs={o: o if o == final else ns(o) for o in base.all_outputs()},
        parameters=params,
    )
    d30 = DEADLINE_30D[product]
    grr = PROMISE_DEADLINE[product]

    def state(tag: str, events: str, deadline: str, output: str) -> list:
        """Commitments from ``events``, then the A3 state with them."""
        return [
            node(
                func=build_commitment_signals,
                inputs={"episode": ns(f"{p}_episode"), "events": events},
                outputs=ns(f"commitments_{tag}"),
                name=f"{p}_check_commitments_{tag}",
                tags=TAGS,
            ),
            node(
                func=partial(build_a3_credibility, deadline=deadline),
                inputs={
                    "episode": ns(f"{p}_episode"),
                    "commitments": ns(f"commitments_{tag}"),
                    "dlq_payments": ns(
                        f"{p}_dlq_payment_signals_single_payment_cycle_count"
                    ),
                    "pre_dlq": ns(
                        f"{p}_pre_dlq_payment_signals_single_payment_cycle_count"
                    ),
                    "contacts": ns(f"{p}_strong_negative_signals"),
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=output,
                name=f"{p}_check_state_{tag}",
                tags=TAGS,
            ),
        ]

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
            func=episode_events,
            inputs={
                "events": ns(f"{p}_promise_events"),
                "episode": ns(f"{p}_episode"),
            },
            outputs=ns("promise_events_ep"),
            name=f"{p}_check_events_ep",
            tags=TAGS,
        ),
        *state("ep", ns("promise_events_ep"), grr, ns("state_ep")),
        node(
            func=partial(build_promise_events, deadline=d30),
            inputs={
                "obs_base": ns("obs_latest"),
                "followup": "dcore_prm_followup_outcomes",
                "agreements": "prm_dcore_account_agreements",
                "instalments": ns(f"{p}_instalments"),
                "dues": ns(f"{p}_dues"),
                "payments": ns(f"{p}_payments"),
            },
            outputs=ns("promise_events_30d"),
            name=f"{p}_check_events_30d",
            tags=TAGS,
        ),
        *state("30d", ns("promise_events_30d"), d30, f"{p}_check_30d"),
        node(
            func=compare_a3,
            inputs={
                "old": f"{p}_payment_credibility",
                "grr_ep": ns("state_ep"),
                "grr": final,
                "d30": f"{p}_check_30d",
                "events_grr": ns(f"{p}_promise_events"),
                "events_30d": ns("promise_events_30d"),
                "model_id": "params:model_id",
                "persona_end_date": "params:crx_persona.persona_end_date",
            },
            outputs=None,
            name=f"{p}_check_compare",
            tags=TAGS,
        ),
    ]
    return scoped + Pipeline(extra)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/classify.py`
action: replace · base sha256 `f48284511fe0b206552ad116dd0c6f40a61aac887dfd7b3dcb16fc463bdff197` · base trailing newline: yes · new sha256 `3bb4768508c4a274d4dda012b1bdae864d0ac953d54a974652794b3d8a3b91c2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
    "a3_promise_deadline",
    # Dimension A
    "commitments_window_start",
    "commitments_concluded",
    "commitments_kept",
    "commitments_partial",
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
    deadline: str,
    persona_end_date: str,
) -> DataFrame:
    """``OUTPUT_COLUMNS`` per base row (D-A3-4, -16, -19, -20, -24).

    High from 4 points, Moderate from 2, else Low; a refusal takes one rung off. Unknown:
    no evidence in any dimension and no refusal, or no episode anchor (Q-12,
    ``a3_unknown_reason``).
    """
    df = left_join_all(
        episode, [episode, commitments, dlq_payments, pre_dlq, contacts]
    ).withColumn("a3_promise_deadline", F.lit(deadline))
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
action: replace · base sha256 `1f83f2a0470fdb796e306980014a6bc4f5eca01f223104ff590b9686ebaff078` · base trailing newline: yes · new sha256 `53ffe52e1e082a62f5646c29641e84910e4a5edbc20f22bca6ae9517cea9ec62` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

`````python
"""A3 payment credibility: thresholds, windows and the Scorecard (spec
``specs/A3_credibility_spec.md``; "row n" = the DE sheet "A3 framework")."""

from .._common import SEG_60_180, SEG_180_PLUS
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard

# ── Dimension A: promises kept (D-A3-9, D-A3-16, D-A3-25) ─────────────────────
COMMITMENT_MONTHS = 12  # promise events in the last 12 months of this episode (row 19)
MIN_CONCLUDED = 2  # concluded promises before a rate counts (row 74)
KEPT_RATE = 0.80  # Kept from (row 75)
BROKEN_RATE = 0.40  # Broken below (row 76)
BROKEN_STREAK = 3  # Broken when the last 3 concluded were all broken (row 77)
FOLLOWUP_RUN_DAYS = 7  # follow-up promises less than 8 days apart are one event
MATCH_DAYS = 7  # a follow-up promise within 7 days of a DCORE plan is that plan
# The deadline a promise is judged by (GRR): CC the next statement after the promise
# day, however close; RL the end of the next month (RL cash is known by month only).
# The alternative is 30 days from the promise ("30_days"; RL "30_days_month_end").
DEADLINES = ("next_statement", "next_month_end", "30_days", "30_days_month_end")
PROMISE_DEADLINE = {"cc": "next_statement", "rl": "next_month_end"}
STATEMENT_FALLBACK_D = 31  # no statement after the promise day yet: 31 days

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

# ── State (D-A3-16, -19, -20, -22, -24) ───────────────────────────────────────────────
DISPLAY_NAMES = {
    "high": "payment_credibility_high",
    "moderate": "payment_credibility_moderate",
    "low": "payment_credibility_low",
    "unknown": "payment_credibility_unknown",
}
COMMITMENT_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}
DLQ_PAYMENT_POINTS = {"regular": 2, "some": 1}
PRE_DLQ_POINTS = {"clean": 1}
HIGH_FROM, MODERATE_FROM = 4, 2  # D-A3-24

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
action: replace · base sha256 `83fc43259e8be5b62f731b16e7657220a04daf7bc5bb28a34f90e0d8a91b7ac9` · base trailing newline: yes · new sha256 `87261dffd8d04a5f03eef5db91f24c9cde1b9a2b3ddc17be51eeeaea78582b1d` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

`````python
"""The A3 payment credibility pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base, crx_<p>_a4_deterioration ─► episode ─┬───────────────────┐
    product dues + payments (wrapper nodes) ─► cycle ledger ┼─ Dim B, Dim C ────┤
    DCORE plans ─► instalments ┬─ promise events ───────────┼─ Dim A ───────────┼─► state
    dcore_prm_followup_outcomes┴────────────────────────────┴─ contacts ────────┘

Needs, for the model_id: the obs base, A4, the product's payment sources and the DCORE
tables. Promises are judged by ``PROMISE_DEADLINE`` (CC the next statement, RL the end of
the next month).
"""

from functools import partial

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a3_credibility
from .constants import PROMISE_DEADLINE
from .signals import (
    build_commitment_signals,
    build_contact_signals,
    build_dlq_payment_signals,
    build_pre_dlq_payment_signals,
)
from .sources import (
    build_a3_episode,
    build_cycle_ledger,
    build_instalments,
    build_promise_events,
)

TAGS = ["crx_persona", "crx", "a3", "payment_credibility", "persona_axis"]
# Ledger names as in the workplace catalog.
LEDGER = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}


def create_a3_pipeline(
    product: str, output: str, dues: Node, payments: Node, deadline: str | None = None
) -> Pipeline:
    """The A3 axis for ``product``, written to ``output``. ``dues`` / ``payments`` are
    the product nodes writing ``crx_<p>_a3_dues`` / ``crx_<p>_a3_payments``.
    ``deadline`` overrides ``PROMISE_DEADLINE`` (the bundle check)."""
    p = f"crx_{product}_a3"
    deadline = deadline or PROMISE_DEADLINE[product]
    episode, ledger, inst = f"{p}_episode", LEDGER[product], f"{p}_instalments"
    events = f"{p}_promise_events"

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
                partial(build_promise_events, deadline=deadline),
                {
                    "obs_base": f"crx_{product}_obs_base",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "instalments": inst,
                    "dues": f"{p}_dues",
                    "payments": f"{p}_payments",
                },
                events,
                events,
            ),
            step(
                build_commitment_signals,
                {"episode": episode, "events": events},
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
                partial(build_a3_credibility, deadline=deadline),
                {
                    "episode": episode,
                    "commitments": f"{p}_commitment_signals",
                    "dlq_payments": f"{p}_dlq_payment_signals_single_payment_cycle_count",
                    "pre_dlq": f"{p}_pre_dlq_payment_signals_single_payment_cycle_count",
                    "contacts": f"{p}_strong_negative_signals",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                output,
                f"{p}_payment_credibility",
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a3_credibility/signals.py`
action: replace · base sha256 `eb8613bac8883b24600fddaafe8803c09dbbd8806b6761ae8f4adf829666021c` · base trailing newline: yes · new sha256 `ab3b282d9aecc152141ccda1826754749d2c8246aaef2667d132aedbcf90099a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
    CLEAN_SHARE,
    COMMITMENT_MONTHS,
    DCORE_MAX_MONTHS,
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


def build_commitment_signals(episode: DataFrame, events: DataFrame) -> DataFrame:
    """Dimension A: kept / partly kept / thin / broken (D-A3-9, -25, -26).

    Promise events (``build_promise_events``) dated in the last 12 months up to the
    observation date, earlier delinquency episodes included (trustworthiness, not this
    episode only), concluded once their cutoff is on or before the
    observation date. Kept: paid; partial counts as not kept. Broken: the last 3
    concluded all not kept (a broken event ranks first on a shared day), or at least 2
    concluded and under 40% kept. Kept: at least 2 concluded and 80% kept.
    """
    base = episode.select(*GRAIN)
    lower = window_start(COMMITMENT_MONTHS)
    obs = F.col("observation_date")
    rows = (
        base.join(events, on="account_id")
        .filter((F.col("event_date") >= lower) & (F.col("event_date") <= obs))
        .withColumn("_concluded", F.col("promise_cutoff") <= obs)
        .withColumn("_kept", F.col("_concluded") & (F.col("promise_outcome") == "paid"))
    )
    last = F.slice(
        F.sort_array(
            F.collect_list(
                F.when(
                    F.col("_concluded"),
                    F.struct(
                        "event_date", (~F.col("_kept")).cast("int").alias("broken")
                    ),
                )
            ),
            asc=False,
        ),
        1,
        BROKEN_STREAK,
    )
    agg = rows.groupBy(*GRAIN).agg(
        F.sum(F.col("_concluded").cast("int")).alias("commitments_concluded"),
        F.sum(F.col("_kept").cast("int")).alias("commitments_kept"),
        F.sum(
            (F.col("_concluded") & (F.col("promise_outcome") == "partial")).cast("int")
        ).alias("commitments_partial"),
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
    counts = [
        "commitments_concluded",
        "commitments_kept",
        "commitments_partial",
        "commitments_last_broken_n",
    ]
    return (
        base.join(agg, on=list(GRAIN), how="left")
        .fillna(0, counts)
        .select(
            *GRAIN,
            lower.alias("commitments_window_start"),
            "commitments_concluded",
            "commitments_kept",
            "commitments_partial",
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
    ("paid", codes.PAYMENT_REPORTED),
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
action: replace · base sha256 `4eef4c47f561b21c469ddcd3799485de7b93fcb289f029a1150a3c8b4c82271c` · base trailing newline: yes · new sha256 `c13eba15c1753f2eda58ff687e178134eeed7c58573918ac4ccf12ead6852dc2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

`````python
"""A3 source nodes shared by both products: the episode anchor, the cycle ledger, the
DCORE plans and the promise events."""

from enbd_collections.nodes.features.dcore._feat_dcore_utils import (
    null_cancelled_instalment_fields,
)
from enbd_collections.nodes.utils.config_dcore import (
    PTP_INSTALMENT_STATUS_CANCELLED,
    SETTLEMENT_INSTALMENT_STATUS_CANCELLED,
)
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .. import _dcore_codes as codes
from .._common import GRAIN, dcore_account_events, require_columns, scoped, string_key
from .._dpd_journey.anchor import episode_start
from .constants import (
    DEADLINES,
    FOLLOWUP_RUN_DAYS,
    MATCH_DAYS,
    MIN_PAYMENT_AED,
    STATEMENT_FALLBACK_D,
)

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


# ── Promise events (D-A3-25) ──────────────────────────────────────────────────

EVENTS = [
    "account_id",
    "event_date",
    "event_kind",
    "event_source",
    "event_name",
    "plan_id",
    "promise_cutoff",
    "promise_amount",
    "promise_paid_amount",
    "promise_outcome",
]


def _followup_promises(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame
) -> DataFrame:
    """Follow-up promise runs per account: rows less than 8 days after the previous one
    belong to the same run, dated (and named) at its first row."""
    rows = (
        dcore_account_events(obs_base, followup, agreements)
        .where(F.col("name").isin(*sorted(codes.PROMISE_EVENT)))
        .select("account_id", "day", "name")
        .distinct()
    )
    order = Window.partitionBy("account_id").orderBy("day", "name")
    gap = F.datediff("day", F.lag("day").over(order))
    new_run = F.when(gap.isNull() | (gap > FOLLOWUP_RUN_DAYS), 1).otherwise(0)
    first = F.min(F.struct("day", "name"))
    return (
        rows.withColumn(
            "_run", F.sum(new_run).over(order.rowsBetween(Window.unboundedPreceding, 0))
        )
        .groupBy("account_id", "_run")
        .agg(first["day"].alias("fu_date"), first["name"].alias("event_name"))
        .drop("_run")
    )


def _consolidate(plans: DataFrame, promises: DataFrame) -> DataFrame:
    """One event per DCORE plan and per follow-up promise no plan claims. A plan takes
    its nearest follow-up promise within 7 days (each promise at most once): the event
    keeps the plan's date and the promise's name (``matched``)."""
    pairs = (
        plans.select("account_id", "plan_id", "event_date")
        .join(promises, on="account_id")
        .withColumn("_dist", F.abs(F.datediff("fu_date", "event_date")))
        .where(F.col("_dist") <= MATCH_DAYS)
    )
    for key, tie in ((["plan_id"], "fu_date"), (["fu_date"], "plan_id")):
        nearest = Window.partitionBy("account_id", *key).orderBy("_dist", tie)
        pairs = pairs.withColumn("_r", F.row_number().over(nearest)).where("_r = 1")
    table = plans.join(
        pairs.select("account_id", "plan_id", "event_name"),
        on=["account_id", "plan_id"],
        how="left",
    ).select(
        "account_id",
        "event_date",
        F.when(F.col("event_name").isNotNull(), "matched")
        .otherwise("table_only")
        .alias("event_kind"),
        F.col("plan_type").alias("event_source"),
        "event_name",
        "plan_id",
    )
    alone = promises.join(
        pairs.select("account_id", "fu_date"), on=["account_id", "fu_date"], how="anti"
    ).select(
        "account_id",
        F.col("fu_date").alias("event_date"),
        F.lit("followup_only").alias("event_kind"),
        F.lit("followup").alias("event_source"),
        "event_name",
        F.lit(None).cast("string").alias("plan_id"),
    )
    return table.unionByName(alone)


def _cutoff(events: DataFrame, dues: DataFrame, deadline: str) -> DataFrame:
    """``events`` + ``promise_cutoff``: the last day a payment still counts."""
    day = F.col("event_date")
    fixed = {
        "next_month_end": F.last_day(F.add_months(day, 1)),
        "30_days": F.date_add(day, 30),
        "30_days_month_end": F.last_day(F.date_add(day, 30)),
    }
    if deadline in fixed:
        return events.withColumn("promise_cutoff", fixed[deadline])
    if deadline != "next_statement":
        raise ValueError(f"promise deadline must be one of {DEADLINES}, got {deadline}")
    nxt = (
        events.select("account_id", "event_date")
        .distinct()
        .join(dues.select("account_id", "cycle_end"), on="account_id")
        .where(F.col("cycle_end") > day)
        .groupBy("account_id", "event_date")
        .agg(F.min("cycle_end").alias("promise_cutoff"))
    )
    return events.join(nxt, on=["account_id", "event_date"], how="left").withColumn(
        "promise_cutoff",
        F.coalesce("promise_cutoff", F.date_add(day, STATEMENT_FALLBACK_D)),
    )


def build_promise_events(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    instalments: DataFrame,
    dues: DataFrame,
    payments: DataFrame,
    deadline: str,
) -> DataFrame:
    """Promise events of the base's accounts, judged by payment (D-A3-25). ``EVENTS``.

    Events: every non-cancelled PTP and settlement plan (dated at its start) and every
    follow-up promise run (``_dcore_codes.PROMISE_EVENT``) no plan claims
    (``event_kind`` matched / table_only / followup_only). Judged once: the payments
    after the event day up to ``promise_cutoff`` (``deadline``, ``PROMISE_DEADLINE``)
    against ``promise_amount``, the due of the cycle open on the event day (the last
    known one, at least 100 AED). Paid: they reach it; partial: 100 AED or more; else
    none. RL cash is dated at the month end, so the event month's cash counts in full.
    """
    plans = instalments.select(
        "account_id", "plan_id", "plan_type", F.col("plan_start").alias("event_date")
    ).distinct()
    events = _cutoff(
        _consolidate(plans, _followup_promises(obs_base, followup, agreements)),
        dues,
        deadline,
    )
    keys = ["account_id", "event_date"]
    due = (
        events.select(*keys)
        .distinct()
        .join(dues.select("account_id", "cycle_start", "due_amount"), on="account_id")
        .where(F.col("cycle_start") <= F.col("event_date"))
        .groupBy(*keys)
        .agg(F.max(F.struct("cycle_start", "due_amount"))["due_amount"].alias("_due"))
    )
    after = (F.col("pay_date") > F.col("event_date")) | (
        (F.col("pay_date") == F.col("event_date"))
        & (F.col("pay_from") < F.col("pay_date"))
    )
    paid = (
        events.select(*keys, "promise_cutoff")
        .distinct()
        .join(
            payments.select("account_id", "pay_from", "pay_date", "amount"),
            "account_id",
        )
        .where(after & (F.col("pay_date") <= F.col("promise_cutoff")))
        .groupBy(*keys, "promise_cutoff")
        .agg(F.sum("amount").alias("promise_paid_amount"))
    )
    amount = F.greatest(F.coalesce("_due", F.lit(0.0)), F.lit(float(MIN_PAYMENT_AED)))
    got = F.coalesce("promise_paid_amount", F.lit(0.0))
    return (
        events.join(due, on=keys, how="left")
        .join(paid, on=[*keys, "promise_cutoff"], how="left")
        .withColumn("promise_amount", amount)
        .withColumn("promise_paid_amount", got)
        .withColumn(
            "promise_outcome",
            F.when(got >= F.col("promise_amount"), "paid")
            .when(got >= MIN_PAYMENT_AED, "partial")
            .otherwise("none"),
        )
        .select(*EVENTS)
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/__init__.py`
action: replace · base sha256 `8562b6fdd15f3335a9a05ad26d452640d5ec49ee018e7b4848c0d6ae0fae9c0e` · base trailing newline: yes · new sha256 `117f8514c4f2102cc37c970e382ed6f85b97358824df3152f567a1474de7dca8` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py`
action: replace · base sha256 `bce3afbc3aa7c0e9ed7f7d7b5836b7d9d905e6943240fa646f9461dd99f255f9` · base trailing newline: yes · new sha256 `905b0116a9bc1e73ee0ba6b6b22592af1f5b56c9f5870b26f3a62b99e620cf45` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CC A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (statement cycles) and the payments (card payments).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``crx_cc_a4_deterioration``, ``crx_cc_raw_extract`` (billing, balance, transactions)
and the DCORE tables.

    kedro run --pipeline=crx_cc_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

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
`````

New:

`````python
"""Kedro pipeline: CC A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (statement cycles) and the payments (card payments).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``crx_cc_a4_deterioration``, ``crx_cc_raw_extract`` (billing, balance, transactions)
and the DCORE tables.

    kedro run --pipeline=crx_cc_a3_payment_credibility

TEMPORARY (A3 bundle 20): ``create_check_pipeline`` (``a3_credibility/check.py``);
removed by the bundle's cleanup.
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
    """TEMPORARY: the A3 bundle 20 check for CC."""
    return create_a3_check_pipeline("cc", DUES, PAYMENTS)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/__init__.py`
action: replace · base sha256 `f49caf143e105080f7474c49d32a63cf8ec6d096bb4ac063def6d2d0a7131a7d` · base trailing newline: yes · new sha256 `bce0a6d599f3fc73ca3ccc3b207291a0723953e3b136fbbb23cdd161c0f2dc5a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A3 payment credibility on the shared ``a3_credibility`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py`
action: replace · base sha256 `19d7a4f5ef4880f745c375a1fccbdbc931e50038cb9cc30e228fbf879bc1524b` · base trailing newline: yes · new sha256 `a0d9df24321df372a69deffc7a3112fce1a96587432b014c247f3214885cab5a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (the month's EMI) and the payments (the month's cash).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``crx_rl_a4_deterioration``, ``int_loan_master`` and the DCORE tables.

    kedro run --pipeline=crx_rl_a3_payment_credibility
"""

from kedro.pipeline import Pipeline, node

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
`````

New:

`````python
"""Kedro pipeline: RL A3 payment credibility on the shared ``a3_credibility`` engine.
The product supplies the dues (the month's EMI) and the payments (the month's cash).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``crx_rl_a4_deterioration``, ``int_loan_master`` and the DCORE tables.

    kedro run --pipeline=crx_rl_a3_payment_credibility

TEMPORARY (A3 bundle 20): ``create_check_pipeline`` (``a3_credibility/check.py``);
removed by the bundle's cleanup.
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
    """TEMPORARY: the A3 bundle 20 check for RL."""
    return create_a3_check_pipeline("rl", DUES, PAYMENTS)
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
Clean up after mirror bundle 20_a3_promise_events_grr_deadline.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id (CC datasets for the CC model_ids, RL for RL); skip folders that do not exist: the check outputs `crx_<p>_a3_check_grr`, `crx_<p>_a3_check_30d`.
- **Remove the temporary check** (everything marked TEMPORARY for A3 bundle 20):
  - `conf/base/catalog/catalog_crx.yml`: the four `crx_<p>_a3_check_*` entries and their comment block;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_a3_check` and `crx_rl_a3_check` entries and their comments;
  - `crx_persona/cc_a3_payment_credibility/` and `rl_a3_payment_credibility/`: `create_check_pipeline` in `pipeline.py` (with its import and the TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete `crx_persona/a3_credibility/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "a3_check" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
