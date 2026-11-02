# Mirror bundle 12 — A1 — AECB level check in the 25% test, alert refresh check

apply_bundle version: 7 · built 2026-11-02 from `60090b0..1b47c26` · source: 1 added, 9 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/persona_redesign_b12
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/12_a1_level_check.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '12_a1_level_check.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/12_a1_level_check.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet two things:

1. Run the A1 test modules. `income_level` now reads `internal_salary_w` and
   `internal_salary_prior`, so fix any test that builds income rows without them.
2. Find the nodes that build the alert staging dataset and `prm_bureau_alert_enriched`, and write out
   the exact command that rebuilds **only those** (`kedro run --env=dev --pipeline=... --nodes=...`),
   because other raw AECB tables are missing and a full `bureau_staging` run may stop on them.
   Say whether `prm_bureau_alert_enriched` needs another dataset rebuilt first. You will use it in
   step 6.

Then `grep -rnE "a1_ability_v2|b09" src conf --include='*.py' --include='*.yml' | grep -v scoring_engine.py`
must print nothing, and `kedro registry list | grep a1_ability` lists the two `*_b12_check` pipelines.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: AECB level check in the 25% test; temporary b12 check" && git push -u origin feature/persona_redesign_b12
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/12_a1_level_check.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b12 && git pull
```

First, if you have not yet, run `bundle_helpers/a1_final/sonnet_a1_date_gaps_prompt.md`. If it finds
gaps in a source other than the alerts, send its summary back before going on.

Run steps 6–8 for **`cc_60_180`** (the default in `conf/dev/globals_dev.yml`), then for
**`rl_60_180`** (set `model_id: rl_60_180`, persona dates unchanged). Switch back when you are done.
180+ is not needed.

**Step 6.** Rebuild the alerts with the command Sonnet gave you in step 4, then the bureau features:

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

No CASA or salary rerun is needed: this bundle does not change them, and they are already built for
both model_ids, unless the date check found gaps there.

**Step 7.** Run the check (it reads the current real output, so do not run step 8 yet). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b12_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b12_check
```

Paste back every block from `=== B12 … START ===` to `=== B12 … END ===`: `OUTPUT`, `REPORT`,
`SOURCES`, `AECB`. A summary file like the last ones is fine.

**Step 8.** Only after the B12 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The A1 income rule compares levels when only AECB salary is present, and a
new check measures this and the refreshed alerts together. Bundle 09's check is already gone.

- **`income_level`** (`a1_ability/classify.py`): with no internal salary of AED 1,000 or more in the
  window or the prior window, the 25% check compares the average of the months with a value, not
  the totals. AECB alerts arrive only on a change, and the payment validation showed rows failing
  the total check on sparse months behave like Stable, while real falls behave like Weak. Any row
  with internal salary in either window keeps the total check, so a stopped salary still shows.
- **Check** (`a1_ability/b12_check.py`, pipelines `crx_cc_a1_ability_b12_check`,
  `crx_rl_a1_ability_b12_check`): blocks `B12 OUTPUT`, `REPORT`, `SOURCES` and `AECB`. `OUTPUT` compares
  with the current `crx_<p>_a1_ability`, so it shows the refreshed alerts and this rule together.
  `AECB` adds a last step, `s3_level_check`, which isolates the rule.
- No output column changes. Expected for `cc_60_180` (rough, before the alert refresh): about 680
  accounts move from Weak to Stable. The refresh also raises August's salary and bounces.

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
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/b12_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `a4dbda7f3e900d6ea59dec508dc3d06c62c8926ace70fb1d4dae835b401dd5a3` · base trailing newline: yes · new sha256 `fe94cae6c05d0cf2b929a71925e0e7a9ce26607c4026a490231d15c422660e80` · new trailing newline: yes

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
# Built by crx_cc_raw_extract pipeline (T04c). Consumed by T04b, T05, T06.
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

# -- T04: CC Payment & Balance Trajectory Features ---------------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# W12 = [T0-365d, T0); H1 = older 9m; H2 = recent 3m.
# Blocked features (FILL-IN): min_pay_share_w12, months_since_full_pay_t0.
crx_cc_payment_trajectory:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_payment_trajectory"
  save_args:
    mode: overwrite

# -- T05: CC Utilisation, Spend & Liquidity Features ------------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# W_pre truncation columns carried from crx_cc_payment_trajectory (T04b).
# Pass A: util_mean_h1/h2, util_t0, util_slope, util_accel (from prm_limit).
# Pass B: cash_adv_ramp, cash_adv_amt_share_h2, spend_taper_ratio,
#         spend_cliff_flag, spend_active_days_share_h2, txn_cnt_slope
#         (from prm_transaction).
crx_cc_utilisation_features:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_utilisation_features"
  save_args:
    mode: overwrite

# -- T06: CC Departure Signature & History Shape Features -------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# Pass A: travel_mcc_flag_h2, foreign_txn_share_h2, last_txn_foreign_flag
#         (from prm_transaction; MCC codes 3000-3299, 4511, 4722)
# Pass B: casa_inflow_stop_gap_d, eosb_like_flag
#         (from comp_financial_tran_repos_dly; R20 scoped; schema-guarded)
# Pass C: prior_spell_cnt_24m, months_since_prior_spell, roll_speed_30/60_d
#         (from crx_cc_spell_table self-window; free reads)
# Pass D: tenure_at_t0_m, fee_velocity_life, fee_velocity_ratio_h2
#         (from prm_contract SCD2 + prm_turnovers PIT joins)
# Pass E: aecb_leverage_slope (OLS over int_bureau_pull_monthly [M0-24, M0))
# Pass F: relationship_breadth (from feat_product_holding PIT join)
# Always-NULL: foreign_login_flag (no geo login data), cross_prod_t0_gap_d,
#              simultaneous_default_flag (both blocked on T25)

# -- T06 intermediates: modular pass checkpoints ------------------------------
# Each intermediate corresponds to one Kedro node. Re-run a single pass with:
#   kedro run --pipeline=crx_cc_departure_signature --from-nodes=build_crx_departure_pass_k
crx_cc_departure_spell_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_spell_base"
  save_args:
    mode: overwrite

crx_cc_departure_contract_cif:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_contract_cif"
  save_args:
    mode: overwrite

crx_cc_departure_pass_a:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_a"
  save_args:
    mode: overwrite

crx_cc_departure_pass_b:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_b"
  save_args:
    mode: overwrite

crx_cc_departure_pass_c:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_c"
  save_args:
    mode: overwrite

crx_cc_departure_pass_d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_d"
  save_args:
    mode: overwrite

crx_cc_departure_pass_e:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_e"
  save_args:
    mode: overwrite

crx_cc_departure_pass_f:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_f"
  save_args:
    mode: overwrite

crx_cc_departure_pass_g:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_g"
  save_args:
    mode: overwrite

crx_cc_departure_pass_h:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_h"
  save_args:
    mode: overwrite

crx_cc_departure_pass_h2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_h2"
  save_args:
    mode: overwrite

crx_cc_departure_pass_i:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_i"
  save_args:
    mode: overwrite

crx_cc_departure_pass_j:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_j"
  save_args:
    mode: overwrite

crx_cc_departure_pass_k:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_k"
  save_args:
    mode: overwrite

crx_cc_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_signature"
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

# TEMPORARY (mirror bundle 06): the A2 check output; removed by the bundle's cleanup.
crx_cc_a2_locatability_b06_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability_b06_check"
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
# crx_rl_spell_table) — no classification columns. Built by rl_a4_spine pipeline,
# which reuses rl_departure_signature's build_rl_depart_spine (R14) so
# rl_a1_ability/rl_a2_locatability/rl_a3_payment_credibility need no changes.
# Filter point per TASKS_RL.md.
crx_rl_a4_spine:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine"
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

# TEMPORARY (mirror bundle 11): the sequences of the b11 check.
crx_rl_dpd_sequences_b11_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b11_check"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 11): the new output written by the b11 check pipeline.
crx_rl_a4_deterioration_b11_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b11_check"
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

# ── RL Departure Signature (RL-A2-2) ───────────────────────────────────────

# Node 1: travel MCC hits from comp_financial_tran_repos_dly H2 window.
# Grain: (account_id, observation_date). Null = no H2 debit transactions.
crx_rl_depart_travel_mcc:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_depart_travel_mcc"
  save_args:
    mode: overwrite

# Node 2: FX leakage (last_txn_foreign_flag) + digital login (foreign_login_flag).
# Grain: (account_id, observation_date).
crx_rl_depart_foreign_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_depart_foreign_signals"
  save_args:
    mode: overwrite

# Shipped RL departure signature — all 4 departure-trail signals at obs-date grain.
# Grain: (account_id, observation_date). Consumed by the RL A1 waterfall.
# travel_mcc_flag_h2/foreign_login_flag coalesced to 0; casa_inflow_stop_gap_d may be NULL.
crx_rl_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_departure_signature"
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

# TEMPORARY (mirror bundle 06): the A2 check output; removed by the bundle's cleanup.
crx_rl_a2_locatability_b06_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability_b06_check"
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
#   rm conf/base/catalog_crx.yml
#   rm -r src/enbd_collections/pipelines/crx_persona/
#   revert the one-line addition to pipeline_registry.py
#
# Physical paths: ${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/<asset_name>
# model_id-namespaced — each model run writes to its own directory.
# ==============================================================================

# -- T04c: T0-scoped CC raw DDI intermediates ----------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by crx_cc_raw_extract pipeline (T04c). Consumed by T04b, T05, T06.
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

# -- T04: CC Payment & Balance Trajectory Features ---------------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# W12 = [T0-365d, T0); H1 = older 9m; H2 = recent 3m.
# Blocked features (FILL-IN): min_pay_share_w12, months_since_full_pay_t0.
crx_cc_payment_trajectory:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_payment_trajectory"
  save_args:
    mode: overwrite

# -- T05: CC Utilisation, Spend & Liquidity Features ------------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# W_pre truncation columns carried from crx_cc_payment_trajectory (T04b).
# Pass A: util_mean_h1/h2, util_t0, util_slope, util_accel (from prm_limit).
# Pass B: cash_adv_ramp, cash_adv_amt_share_h2, spend_taper_ratio,
#         spend_cliff_flag, spend_active_days_share_h2, txn_cnt_slope
#         (from prm_transaction).
crx_cc_utilisation_features:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_utilisation_features"
  save_args:
    mode: overwrite

# -- T06: CC Departure Signature & History Shape Features -------------------
# Grain: (account_id, spell_id). One row per delinquency spell.
# All features anchored to T0 (from crx_cc_spell_table).
# Pass A: travel_mcc_flag_h2, foreign_txn_share_h2, last_txn_foreign_flag
#         (from prm_transaction; MCC codes 3000-3299, 4511, 4722)
# Pass B: casa_inflow_stop_gap_d, eosb_like_flag
#         (from comp_financial_tran_repos_dly; R20 scoped; schema-guarded)
# Pass C: prior_spell_cnt_24m, months_since_prior_spell, roll_speed_30/60_d
#         (from crx_cc_spell_table self-window; free reads)
# Pass D: tenure_at_t0_m, fee_velocity_life, fee_velocity_ratio_h2
#         (from prm_contract SCD2 + prm_turnovers PIT joins)
# Pass E: aecb_leverage_slope (OLS over int_bureau_pull_monthly [M0-24, M0))
# Pass F: relationship_breadth (from feat_product_holding PIT join)
# Always-NULL: foreign_login_flag (no geo login data), cross_prod_t0_gap_d,
#              simultaneous_default_flag (both blocked on T25)

# -- T06 intermediates: modular pass checkpoints ------------------------------
# Each intermediate corresponds to one Kedro node. Re-run a single pass with:
#   kedro run --pipeline=crx_cc_departure_signature --from-nodes=build_crx_departure_pass_k
crx_cc_departure_spell_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_spell_base"
  save_args:
    mode: overwrite

crx_cc_departure_contract_cif:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_contract_cif"
  save_args:
    mode: overwrite

crx_cc_departure_pass_a:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_a"
  save_args:
    mode: overwrite

crx_cc_departure_pass_b:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_b"
  save_args:
    mode: overwrite

crx_cc_departure_pass_c:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_c"
  save_args:
    mode: overwrite

crx_cc_departure_pass_d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_d"
  save_args:
    mode: overwrite

crx_cc_departure_pass_e:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_e"
  save_args:
    mode: overwrite

crx_cc_departure_pass_f:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_f"
  save_args:
    mode: overwrite

crx_cc_departure_pass_g:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_g"
  save_args:
    mode: overwrite

crx_cc_departure_pass_h:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_h"
  save_args:
    mode: overwrite

crx_cc_departure_pass_h2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_h2"
  save_args:
    mode: overwrite

crx_cc_departure_pass_i:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_i"
  save_args:
    mode: overwrite

crx_cc_departure_pass_j:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_j"
  save_args:
    mode: overwrite

crx_cc_departure_pass_k:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_pass_k"
  save_args:
    mode: overwrite

crx_cc_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_departure_signature"
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

# TEMPORARY (mirror bundle 06): the A2 check output; removed by the bundle's cleanup.
crx_cc_a2_locatability_b06_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability_b06_check"
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

# TEMPORARY (mirror bundle 12): the new output written by the b12 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b12_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b12_check"
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
# crx_rl_spell_table) — no classification columns. Built by rl_a4_spine pipeline,
# which reuses rl_departure_signature's build_rl_depart_spine (R14) so
# rl_a1_ability/rl_a2_locatability/rl_a3_payment_credibility need no changes.
# Filter point per TASKS_RL.md.
crx_rl_a4_spine:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_spine"
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

# TEMPORARY (mirror bundle 11): the sequences of the b11 check.
crx_rl_dpd_sequences_b11_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b11_check"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 11): the new output written by the b11 check pipeline.
crx_rl_a4_deterioration_b11_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b11_check"
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

# TEMPORARY (mirror bundle 12): the new output written by the b12 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b12_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b12_check"
  save_args:
    mode: overwrite

# ── RL Departure Signature (RL-A2-2) ───────────────────────────────────────

# Node 1: travel MCC hits from comp_financial_tran_repos_dly H2 window.
# Grain: (account_id, observation_date). Null = no H2 debit transactions.
crx_rl_depart_travel_mcc:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_depart_travel_mcc"
  save_args:
    mode: overwrite

# Node 2: FX leakage (last_txn_foreign_flag) + digital login (foreign_login_flag).
# Grain: (account_id, observation_date).
crx_rl_depart_foreign_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_depart_foreign_signals"
  save_args:
    mode: overwrite

# Shipped RL departure signature — all 4 departure-trail signals at obs-date grain.
# Grain: (account_id, observation_date). Consumed by the RL A1 waterfall.
# travel_mcc_flag_h2/foreign_login_flag coalesced to 0; casa_inflow_stop_gap_d may be NULL.
crx_rl_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_departure_signature"
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

# TEMPORARY (mirror bundle 06): the A2 check output; removed by the bundle's cleanup.
crx_rl_a2_locatability_b06_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability_b06_check"
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

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `ded27ec4f0e7cfd2bc0e11ef4e438625fd875a3dbb842c2b679292f30630c18b` · base trailing newline: yes · new sha256 `798a2633d7faf2579df094e5082f1b65845043bb316f518c0349cdb7a4c523b6` · new trailing newline: yes

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
    cc_payment_trajectory as crx_cc_payment_trajectory,
)
from enbd_collections.pipelines.crx_persona import (
    cc_utilisation as crx_cc_utilisation,
)
from enbd_collections.pipelines.crx_persona import (
    cc_departure_signature as crx_cc_departure,
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
from enbd_collections.pipelines.crx_persona import (
    rl_departure_signature as crx_rl_departure_signature,
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
        "crx_cc_payment_trajectory": crx_cc_payment_trajectory.create_pipeline(),
        "crx_cc_utilisation_features": crx_cc_utilisation.create_pipeline(),
        "crx_cc_departure_signature": crx_cc_departure.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_cc_a2_locatability_b06_check": (
            crx_cc_a2_locatability.create_b06_check_pipeline()
        ),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        # TEMPORARY (mirror bundle 11): A4 check; removed by the bundle's cleanup.
        "crx_rl_a4_deterioration_b11_check": (
            crx_rl_a4_deterioration.create_b11_check_pipeline()
        ),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_rl_a2_locatability_b06_check": (
            crx_rl_a2_locatability.create_b06_check_pipeline()
        ),
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
    cc_payment_trajectory as crx_cc_payment_trajectory,
)
from enbd_collections.pipelines.crx_persona import (
    cc_utilisation as crx_cc_utilisation,
)
from enbd_collections.pipelines.crx_persona import (
    cc_departure_signature as crx_cc_departure,
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
from enbd_collections.pipelines.crx_persona import (
    rl_departure_signature as crx_rl_departure_signature,
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
        "crx_cc_payment_trajectory": crx_cc_payment_trajectory.create_pipeline(),
        "crx_cc_utilisation_features": crx_cc_utilisation.create_pipeline(),
        "crx_cc_departure_signature": crx_cc_departure.create_pipeline(),
        "crx_cc_a4_deterioration": crx_cc_a4_deterioration.create_pipeline(),
        "crx_cc_a2_locatability": crx_cc_a2_locatability.create_pipeline(),
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_cc_a2_locatability_b06_check": (
            crx_cc_a2_locatability.create_b06_check_pipeline()
        ),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 12): A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_ability_b12_check": (
            crx_cc_a1_ability.create_b12_check_pipeline()
        ),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        # TEMPORARY (mirror bundle 11): A4 check; removed by the bundle's cleanup.
        "crx_rl_a4_deterioration_b11_check": (
            crx_rl_a4_deterioration.create_b11_check_pipeline()
        ),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 12): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b12_check": (
            crx_rl_a1_ability.create_b12_check_pipeline()
        ),
        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_rl_a2_locatability_b06_check": (
            crx_rl_a2_locatability.create_b06_check_pipeline()
        ),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `e32f97ee2ac900b861ca4efe58d020dc84564265bf3fd0816c0396192252eff4` · base trailing newline: yes · new sha256 `10ea20a369fa61f7644c16700b99826c4a20e1371d4cc0cd6c8b32b361cf2196` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule table is the GRR workbook
`A1_ability_20261022` and the spec `specs/A1_ability_spec.md` (S1–S13); the code is
`signals.py` (evidence), `classify.py` (levels and state) and `pipeline.py` (nodes). CC wraps
it in `cc_a1_ability`, RL in `rl_a1_ability`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends**. Only the persona months are scored,
  `crx_persona.persona_start_date` to `persona_end_date`.
- **Layers:** the signal nodes read the observation base and monthly feature tables, one
  row per `(cif_id, month_end)` — never raw or staging tables:

  | Feature | Built from (pipeline) |
  |---|---|
  | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` (`casa_features`) |
  | `feat_cif_casa_balance_monthly` | WM CASA balance and flow tables (`casa_features`) |
  | `feat_cif_casa_activity_monthly` | `prm_casa_transactions` ← FTR (`casa_primary`, `casa_features`) |
  | `feat_cif_ext_card_payment_monthly` | `wm_pri_labelled_transactions` + `prm_beneficiary_cards` |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |
  | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |

- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month. CC 180+: none.
  - RL: one EMI — `installment_due_amount` on the observation month's `int_loan_master`
    snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — the salary on AECB's alert feed (types 31 and 32, keyed by CIF), an
  accurate level on the pull date. It counts in the pull's month and the next, never before
  the pull and no further (S14), so pulls every 2 months make a continuous series; a salary
  account closure (type 43) ends it. RL also reads `feature_retail_loans`: the salary of each
  loan's latest bureau pull, handled the same way.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`) and the prior window's internal salary (`internal_salary_prior`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`D_INC = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`) — current + savings average balance, the
  4-week average on the month's last weekly WM snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA payment in
  m1–m3 to a card registered as a payment beneficiary (money paid to another bank's card).

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3 (3 of 6 at 180+), **and** the
    m1–m3 average not more than 50% below the m4–m6 average (months without data skipped); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a **new** bounced cheque in a bureau pull — per alert key (CIF, contract type,
  alert), a pull whose bounced amount differs from the key's previous pull, or follows a
  pull without one. A bounce repeated unchanged in later pulls counts once. Dated by the
  pull (the bureau gives no bounce date).

## 4. Activity — is there a CASA we can read? (spec S11)

The CASA legs of the transaction table (FTR) are sorted into lanes
(`feat_cif_casa.transaction_lane`, after the FTR row-handling reference). **Customer-initiated
movement** = a leg in the `economic` lane (remittances in and out, transfers to others, cash,
clearing, bill payments), `card_spend` (POS) or `card_payment` (paying their own credit
card). It does **not** count: transfers between the customer's own accounts and auto-save
(`wash`), the bank recovering the customer's loan instalment (`own_loan`), fees and interest,
reversals, returns, group-internal transfers and the ambiguous rest of `MISCELLANEOUS`.

- `casa_active` = a customer-initiated leg in m1–m3.
- `casa_held` = any CASA leg, or a positive balance, in the last 12 months. WM may fill a
  missing balance with 0, so a zero balance alone does not show a CASA.

## 5. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `unknown` | 0 points, no distress **and** no customer-initiated movement in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA with us in 12 months) or `dormant_casa` |
| `high` | 4 points, no distress |
| `moderate` | 2–3 points without distress, or 4 points with distress |
| `low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down.
`a1_eosb_flag` (a DCORE end-of-service result in the window) is a diagnostic column and
changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts.** Regular non-salary income is invisible; about a
  third of customers ever show an internal salary, and about a third hold no CASA with us.
- **Bureau salary is an event feed for now.** An alert row appears only when something changes,
  so no row means nothing is known, not that the salary stopped, and few pulls fall in the
  window. GRR's feed of pulls every 2 months enters through the same rule. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions` and
  the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

New:

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule table is the GRR workbook
`A1_ability_20261022` and the spec `specs/A1_ability_spec.md` (S1–S13); the code is
`signals.py` (evidence), `classify.py` (levels and state) and `pipeline.py` (nodes). CC wraps
it in `cc_a1_ability`, RL in `rl_a1_ability`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends**. Only the persona months are scored,
  `crx_persona.persona_start_date` to `persona_end_date`.
- **Layers:** the signal nodes read the observation base and monthly feature tables, one
  row per `(cif_id, month_end)` — never raw or staging tables:

  | Feature | Built from (pipeline) |
  |---|---|
  | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` (`casa_features`) |
  | `feat_cif_casa_balance_monthly` | WM CASA balance and flow tables (`casa_features`) |
  | `feat_cif_casa_activity_monthly` | `prm_casa_transactions` ← FTR (`casa_primary`, `casa_features`) |
  | `feat_cif_ext_card_payment_monthly` | `wm_pri_labelled_transactions` + `prm_beneficiary_cards` |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |
  | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |

- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month. CC 180+: none.
  - RL: one EMI — `installment_due_amount` on the observation month's `int_loan_master`
    snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — the salary on AECB's alert feed (types 31 and 32, keyed by CIF), an
  accurate level on the pull date. It counts in the pull's month and the next, never before
  the pull and no further (S14), so pulls every 2 months make a continuous series; a salary
  account closure (type 43) ends it. RL also reads `feature_retail_loans`: the salary of each
  loan's latest bureau pull, handled the same way.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`) and the prior window's internal salary (`internal_salary_prior`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`D_INC = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`) — current + savings average balance, the
  4-week average on the month's last weekly WM snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA payment in
  m1–m3 to a card registered as a payment beneficiary (money paid to another bank's card).

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3 (3 of 6 at 180+), **and** the
    m1–m3 average not more than 50% below the m4–m6 average (months without data skipped); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a **new** bounced cheque in a bureau pull — per alert key (CIF, contract type,
  alert), a pull whose bounced amount differs from the key's previous pull, or follows a
  pull without one. A bounce repeated unchanged in later pulls counts once. Dated by the
  pull (the bureau gives no bounce date).

## 4. Activity — is there a CASA we can read? (spec S11)

The CASA legs of the transaction table (FTR) are sorted into lanes
(`feat_cif_casa.transaction_lane`, after the FTR row-handling reference). **Customer-initiated
movement** = a leg in the `economic` lane (remittances in and out, transfers to others, cash,
clearing, bill payments), `card_spend` (POS) or `card_payment` (paying their own credit
card). It does **not** count: transfers between the customer's own accounts and auto-save
(`wash`), the bank recovering the customer's loan instalment (`own_loan`), fees and interest,
reversals, returns, group-internal transfers and the ambiguous rest of `MISCELLANEOUS`.

- `casa_active` = a customer-initiated leg in m1–m3.
- `casa_held` = any CASA leg, or a positive balance, in the last 12 months. WM may fill a
  missing balance with 0, so a zero balance alone does not show a CASA.

## 5. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `unknown` | 0 points, no distress **and** no customer-initiated movement in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA with us in 12 months) or `dormant_casa` |
| `high` | 4 points, no distress |
| `moderate` | 2–3 points without distress, or 4 points with distress |
| `low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down.
`a1_eosb_flag` (a DCORE end-of-service result in the window) is a diagnostic column and
changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts.** Regular non-salary income is invisible; about a
  third of customers ever show an internal salary, and about a third hold no CASA with us.
- **Bureau salary is an event feed for now.** An alert row appears only when something changes,
  so no row means nothing is known, not that the salary stopped, and few pulls fall in the
  window. GRR's feed of pulls every 2 months enters through the same rule. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions` and
  the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/b12_check.py`
action: add · new sha256 `72be4c9475700180b52f664c830f5eccf43ffcd376caa10799c44f903cb4d189` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 12): the A1 report tables and the AECB salary check, in PROD.

Log blocks, aggregates only, latest observation month unless named:

* ``compare_a1_outputs`` (``B12 OUTPUT``): states (M1) — latest month, old
  (``crx_<p>_a1_ability``, the output before this bundle) × new, the monthly range; RL by
  ``loan_type``.
* ``describe_a1_report`` (``B12 REPORT``): income source and level (M4), CASA
  relationship (M5), liquidity (M6), Unknown / Low / Moderate-High reasons (M7–M9),
  distress parts (M10), EOSB and the anchor (M11).
* ``describe_a1_sources`` (``B12 SOURCES``): how far back each source goes, internal
  salary history (M2), AECB salary coverage (M3), CASA legs by lane, WM vs FTR coverage.
* ``explain_a1_aecb`` (``B12 AECB``): the state without the alert salary, with its pull
  months, with the 1-month carry (S14), then with the level check; the last step is checked
  against the output.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging
from itertools import pairwise

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import transaction_lane

from .._common import GRAIN, lookback_floor, window_months
from ..scoring_engine import points_from_level
from .classify import (
    _LADDER,
    D_INC,
    DEMIN,
    F_CASA,
    F_INC,
    F_PAY,
    INC_FLOORS,
    K_CASA,
    K_INC,
    K_PAY,
    _count_at_least,
    _months,
    _not_weakening,
    _window,
    income_level,
)
from .signals import CUSTOMER_LANES, _loan_bureau_salary, _with_next_month

LOG = logging.getLogger(__name__)
_STATES = ("high", "moderate", "low", "unknown")


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B12 {name} START === [{model_id}]",
        *lines,
        f"=== B12 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<24}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _rows_and_cifs(df: DataFrame) -> str:
    r = df.agg(
        F.count(F.lit(1)).alias("n"), F.countDistinct("cif_id").alias("c")
    ).first()
    return f"{r['n']} accounts, {r['c']} CIFs"


def _with_cif(df: DataFrame, obs_base: DataFrame) -> DataFrame:
    cifs = obs_base.select(*GRAIN, F.col("cif_id").cast("string").alias("cif_id"))
    return df.join(cifs, on=list(GRAIN), how="left")


# ── B12 OUTPUT (M1) ───────────────────────────────────────────────────────────


def _product(df: DataFrame, products: DataFrame) -> DataFrame:
    """``loan_type`` from ``rl_spine`` (RL), else one product."""
    if "loan_type" not in products.columns:
        return df.withColumn("loan_type", F.lit("all"))
    types = products.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(list(GRAIN))
    return df.join(types, on=list(GRAIN), how="left")


def compare_a1_outputs(
    old: DataFrame, new: DataFrame, products: DataFrame, model_id: str
) -> None:
    """New states in the latest month (and by product), old × new, the monthly range."""
    latest = _latest_month(new)
    month = latest.agg(F.max("observation_date")).first()[0]
    old_m = old.filter(F.col("observation_date") == F.lit(month)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("a1_state").alias("old_state"),
    )
    both = latest.join(old_m, on="account_id", how="full")
    monthly = (
        new.groupBy(F.trunc("observation_date", "month").alias("month"))
        .agg(
            F.count(F.lit(1)).alias("n"),
            *[F.sum((F.col("a1_state") == s).cast("int")).alias(s) for s in _STATES],
        )
        .orderBy("month")
        .collect()
    )
    lines = [
        (
            f"month {month}: new {latest.count()} rows, old {old_m.count()}, "
            f"new only {both.filter(F.col('old_state').isNull()).count()}, "
            f"old only {both.filter(F.col('a1_state').isNull()).count()}"
        ),
        "new a1_state:",
        *_table(latest, "a1_state"),
        "by product x a1_state:",
        *_table(_product(latest, products), "loan_type", "a1_state"),
        "old x new a1_state:",
        *_table(both.filter(F.col("a1_state").isNotNull()), "old_state", "a1_state"),
        "new a1_state share by month (n, high, moderate, low, unknown %):",
        *[
            f"  {r['month']} {r['n']:>8} "
            + " ".join(f"{100.0 * r[s] / max(r['n'], 1):6.2f}" for s in _STATES)
            for r in monthly
        ],
        "range over the months (min-max %):",
        *[
            f"  {s:<9} "
            + f"{min(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}-"
            + f"{max(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}"
            for s in _STATES
        ],
    ]
    _log("OUTPUT", model_id, lines)


# ── B12 REPORT (M4–M11) ──────────────────────────────────────────────────────


def _bucket(amount: Column, edges: list[tuple[float, str]], none: str) -> Column:
    expr = F.when(amount.isNull() | (amount <= 0), none)
    for edge, label in edges:
        expr = expr.when(amount < edge, label)
    return expr.otherwise(f">={edges[-1][0]:,.0f}")


def describe_a1_report(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    products: DataFrame,
    model_id: str,
) -> None:
    """The latest month's report tables, M4–M11."""
    w = window_months(model_id)
    df = (
        _with_cif(_latest_month(new), obs_base)
        .join(income, on=list(GRAIN), how="left")
        .join(liquidity, on=list(GRAIN), how="left")
        .join(distress, on=list(GRAIN), how="left")
    )
    df = _product(df, products)
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    casa_w = F.greatest(
        *[F.coalesce(c, F.lit(0.0)) for c in _months("casa", _window(w)[0])]
    )
    has_int = F.coalesce(F.col("internal_salary_w"), F.lit(0.0)) >= DEMIN
    has_bur = F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= DEMIN
    parts = [
        ("distress_cheque", "cheque"),
        ("distress_dds", "dds"),
        ("distress_bureau", "bureau"),
    ]
    df = df.select(
        "*",
        F.when(has_int & has_bur, "both")
        .when(has_int, "internal_only")
        .when(has_bur, "bureau_only")
        .otherwise("neither")
        .alias("income_source_w"),
        F.when(F.col("casa_held") == 0, "no_casa")
        .when(F.col("casa_active") == 0, "dormant_casa")
        .otherwise("active_casa")
        .alias("casa_relationship"),
        _bucket(casa_w, [(1000.0, "<1000"), (3000.0, "1000-3000")], "none").alias(
            "casa_max_w"
        ),
        (casa_w >= F.greatest(F.lit(F_CASA), K_CASA * anchor)).alias(
            "casa_covers_floor"
        ),
        (F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0)) > 0).alias(
            "ext_card_payment"
        ),
        F.when(F.col("a1_state") != "low", None)
        .when(
            (F.col("a1_points_total") == 0) & (F.col("a1_distress_flag") == 0),
            "0pt_active_casa",
        )
        .when(F.col("a1_points_total") == 0, "0pt_distress")
        .when(F.col("a1_points_total") == 1, "1pt")
        .otherwise("2-3pt_distress")
        .alias("low_reason"),
        F.concat_ws(
            "+", *[F.when(F.col(c) == 1, F.lit(label)) for c, label in parts]
        ).alias("distress_parts"),
        F.col("liquidity_anchor_amt").isNotNull().alias("anchor_present"),
        (K_INC * anchor > F_INC).alias("anchor_raises_income"),
        (K_CASA * anchor > F_CASA).alias("anchor_raises_casa"),
        (K_PAY * anchor > F_PAY).alias("anchor_raises_payment"),
    )
    q = (
        df.filter(F.col("liquidity_anchor_amt").isNotNull())
        .agg(F.percentile_approx("liquidity_anchor_amt", [0.1, 0.5, 0.9]).alias("p"))
        .first()["p"]
    )
    mh = df.filter(F.col("a1_state").isin("high", "moderate"))
    lines = [
        f"base: {_rows_and_cifs(df)}",
        "M4 income source in W x income level:",
        *_table(df, "income_source_w", "a1_income_level"),
        "M5 CASA relationship x a1_state:",
        *_table(df, "casa_relationship", "a1_state"),
        "M6 max monthly CASA balance in W x covers max(3000, anchor):",
        *_table(df, "casa_max_w", "casa_covers_floor"),
        "M6 external card payment in W x liquidity level:",
        *_table(df, "ext_card_payment", "a1_liquidity_level"),
        "M6 liquidity level:",
        *_table(df, "a1_liquidity_level"),
        "M7 unknown reason:",
        *_table(df.filter(F.col("a1_state") == "unknown"), "a1_unknown_reason"),
        "M8 low reason:",
        *_table(df.filter(F.col("a1_state") == "low"), "low_reason"),
        "M9 moderate / high: state x income x liquidity x distress:",
        *_table(
            mh, "a1_state", "a1_income_level", "a1_liquidity_level", "a1_distress_flag"
        ),
        "M10 distress parts in W ('' = none):",
        *_table(df, "distress_parts"),
        "M10 distress parts x a1_state:",
        *_table(
            df.filter(F.col("a1_distress_flag") == 1), "distress_parts", "a1_state"
        ),
        "M11 EOSB result in W x a1_state:",
        *_table(df, "a1_eosb_flag", "a1_state"),
        "M11 EOSB in W x liquidity level:",
        *_table(df.filter(F.col("a1_eosb_flag") == 1), "a1_liquidity_level"),
        f"M11 anchor present / p10 p50 p90: {q}",
        *_table(df, "anchor_present"),
        "M11 anchor raises the income x CASA x card-payment floor:",
        *_table(
            df, "anchor_raises_income", "anchor_raises_casa", "anchor_raises_payment"
        ),
        "by product: loan_type x a1_state, x unknown reason, x low reason:",
        *_table(df, "loan_type", "a1_state"),
        *_table(
            df.filter(F.col("a1_state") == "unknown"), "loan_type", "a1_unknown_reason"
        ),
        *_table(df.filter(F.col("a1_state") == "low"), "loan_type", "low_reason"),
    ]
    _log("REPORT", model_id, lines)


# ── B12 SOURCES (M2, M3, lanes, coverage) ────────────────────────────────────


def _months_since(last: Column) -> Column:
    return F.months_between(
        F.trunc("observation_date", "month"), F.trunc(last, "month")
    ).cast("int")


def describe_a1_sources(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    casa_balance: DataFrame,
    casa_activity: DataFrame,
    transactions: DataFrame,
    alerts: DataFrame,
    model_id: str,
) -> None:
    """Source depth, salary history (M2), AECB coverage (M3), legs by lane, WM vs FTR."""
    w = window_months(model_id)
    base = _with_cif(_latest_month(new).select(*GRAIN, "a1_state"), obs_base).filter(
        F.col("cif_id").isNotNull()
    )
    cifs = base.select("cif_id").distinct()

    def depth(df: DataFrame, col: str, name: str) -> str:
        all_ = df.agg(F.min(col), F.max(col)).first()
        ours = df.join(cifs, on="cif_id").agg(F.min(col)).first()[0]
        return f"  {name:<36} all CIFs {all_[0]} .. {all_[1]}, base CIFs from {ours}"

    def last_before(df: DataFrame, value: str) -> DataFrame:
        return (
            base.join(df.filter(F.col(value) >= DEMIN), on="cif_id")
            .filter(F.col("month_end") <= F.col("observation_date"))
            .groupBy(*GRAIN)
            .agg(F.max("month_end").alias("last"))
        )

    def history(last: DataFrame, label: str) -> DataFrame:
        since = _months_since(F.col("last")) + 1
        return base.join(last, on=list(GRAIN), how="left").withColumn(
            label,
            F.when(F.col("last").isNull(), "never")
            .when(since <= w, "in_W")
            .when(since <= 6, "last_m4-6")
            .when(since <= 12, "last_m7-12")
            .when(since <= 24, "last_m13-24")
            .otherwise("last_m25+"),
        )

    internal = history(last_before(internal_salary, "salary"), "internal_salary")
    alert_cifs = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
        .withColumn("_alert", F.lit(1))
    )
    bureau = (
        history(last_before(bureau_salary, "bureau_salary"), "_hist")
        .join(alert_cifs, on="cif_id", how="left")
        .withColumn(
            "bureau",
            F.when(F.col("_alert").isNull(), "no_alert_row")
            .when(F.col("_hist") == "never", "alert_never_salary")
            .otherwise(F.col("_hist")),
        )
    )
    salary_sources = internal.select(*GRAIN, "internal_salary").join(
        bureau.select(*GRAIN, "bureau"), on=list(GRAIN)
    )
    obs_month = base.agg(F.max("observation_date")).first()[0]
    w_floor = lookback_floor(base, w)
    legs = (
        transactions.filter(
            (F.col("tran_date") >= F.lit(w_floor))
            & (F.col("tran_date") <= F.lit(obs_month))
        )
        .withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(cifs, on="cif_id")
        .withColumn("lane", transaction_lane())
    )
    by_lane = (
        legs.groupBy("lane")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy("lane")
        .collect()
    )
    odd = (
        legs.filter(F.col("lane").isin("unclassified", "ambiguous"))
        .groupBy("lane", "tran_type", "reason_for_excluding")
        .count()
        .orderBy(F.col("count").desc())
        .limit(25)
        .collect()
    )
    held_floor = lookback_floor(base, 12)
    wm12 = (
        casa_balance.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(
            F.max(F.coalesce(F.col("casa_balance"), F.lit(0.0)) > 0).alias(
                "wm_positive"
            )
        )
        .withColumn("wm_row", F.lit(True))
    )
    ftr12 = (
        casa_activity.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(F.max(F.col("lane").isin(*CUSTOMER_LANES)).alias("ftr_customer"))
        .withColumn("ftr_leg", F.lit(True))
    )
    coverage = (
        cifs.join(wm12, on="cif_id", how="left")
        .join(ftr12, on="cif_id", how="left")
        .fillna(False, subset=["wm_row", "wm_positive", "ftr_leg", "ftr_customer"])
    )
    lines = [
        f"base (latest month): {_rows_and_cifs(base)}",
        "source depth (month_end):",
        depth(internal_salary, "month_end", "feat_cif_internal_salary_monthly"),
        depth(bureau_salary, "month_end", "feat_cif_bureau_salary_monthly"),
        depth(casa_balance, "month_end", "feat_cif_casa_balance_monthly"),
        depth(casa_activity, "month_end", "feat_cif_casa_activity_monthly"),
        "M2 internal salary (>= 1000) history x a1_state:",
        *_table(internal, "internal_salary"),
        *_table(internal, "internal_salary", "a1_state"),
        "M3 AECB salary (>= 1000) by last pull month, before the carry:",
        *_table(bureau, "bureau"),
        "M3 internal salary x AECB salary history:",
        *_table(salary_sources, "internal_salary", "bureau"),
        f"CASA legs of base CIFs in W ({w_floor} .. {obs_month}) by lane (legs, CIFs):",
        *[f"  {r['lane']:<16} {r['legs']:>10} {r['cifs']:>8}" for r in by_lane],
        "top unclassified / ambiguous (lane, tran_type, reason):",
        *[
            f"  {r['lane']:<12} {r['tran_type']!s:<34} {r['reason_for_excluding']!s:<28}"
            f" {r['count']:>8}"
            for r in odd
        ],
        (
            "WM vs FTR, base CIFs, last 12 months: WM row x WM positive x FTR leg x"
            " FTR customer leg:"
        ),
        *_table(coverage, "wm_row", "wm_positive", "ftr_leg", "ftr_customer"),
    ]
    _log("SOURCES", model_id, lines)


# ── B12 AECB ──────────────────────────────────────────────────────────────────


def _spread(base: DataFrame, series: DataFrame, prefix: str, months: int) -> DataFrame:
    """``(cif_id, month_end, amount)`` → ``{prefix}_m1 … _m{months}`` (max per month)."""
    k = (
        F.months_between(
            F.trunc("observation_date", "month"), F.trunc("month_end", "month")
        ).cast("int")
        + 1
    )
    return (
        base.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", k)
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col("amount"))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _total_rule(anchor: Column, w: int) -> Column:
    """The income rule before this bundle: the 25% check on window totals for every row."""
    last = _months("income", _window(w)[0])
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (total >= INC_FLOORS[w] * floor) & _not_weakening("income", D_INC, True, w)
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def explain_a1_aecb(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> None:
    """Latest month: the state without the alert salary, with its pull months, with the
    1-month carry, with the level check. RL's loan salary stays in every step and is
    carried from the third."""
    w = window_months(model_id)
    keys = list(GRAIN)
    base = (
        _with_cif(_latest_month(new), obs_base)
        .filter(F.col("cif_id").isNotNull())
        .join(liquidity.select(*keys, "casa_active"), on=keys, how="left")
        .join(
            income.select(*keys, "internal_salary_w", "internal_salary_prior"),
            on=keys,
            how="left",
        )
        .fillna(0, subset=["casa_active"])
    )
    since = lookback_floor(base, 2 * w)
    columns = ["cif_id", "month_end", "amount"]
    internal = internal_salary.withColumnRenamed("salary", "amount").select(*columns)
    alert = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        loans = _loan_bureau_salary(obs_base, loan_features)
    else:
        loans = alert.limit(0)
    carried = _with_next_month(alert.unionByName(loans))

    def amounts(df: DataFrame) -> DataFrame:
        return df.withColumnRenamed("bureau_salary", "amount").select(*columns)

    def recent(df: DataFrame) -> DataFrame:
        return df.filter(F.col("month_end") >= F.lit(since))

    with_carry = internal.unionByName(amounts(carried))
    steps = {
        "s0_no_aecb": (internal.unionByName(amounts(loans)), _total_rule),
        "s1_pull_months": (
            internal.unionByName(amounts(loans)).unionByName(amounts(alert)),
            _total_rule,
        ),
        "s2_one_month_carry": (with_carry, _total_rule),
        "s3_level_check": (with_carry, income_level),
    }
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    liq = points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    distressed = F.col("a1_distress_flag") == 1
    last = _months("income", _window(w)[0])
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    floor = F.greatest(F.lit(F_INC), K_INC * amt)
    df = base
    for name, (series, rule) in steps.items():
        level = rule(amt, w)
        points = points_from_level(level, {"stable": 2, "weak": 1}) + liq
        unknown = (points == 0) & ~distressed & (F.col("casa_active") == 0)
        step = base.join(
            _spread(base, recent(series), "income", 2 * w), on=keys, how="left"
        ).select(
            *keys,
            level.alias(f"{name}_income"),
            _LADDER.state(points, distressed, unknown).alias(name),
            (total >= INC_FLOORS[w] * floor).alias(f"{name}_total_ok"),
        )
        df = df.join(step, on=keys, how="left")
    aecb_w = (
        base.select(*keys, "cif_id")
        .join(amounts(carried).filter(F.col("amount") >= DEMIN), on="cif_id")
        .filter(
            (
                F.col("month_end")
                >= F.add_months(F.trunc("observation_date", "month"), 1 - w)
            )
            & (F.col("month_end") <= F.col("observation_date"))
        )
        .groupBy(*keys)
        .agg(F.count(F.lit(1)).alias("aecb_months_w"))
    )
    df = df.join(aecb_w, on=keys, how="left").fillna(0, subset=["aecb_months_w"])
    final = "s3_level_check"
    checks = df.agg(
        F.sum((~F.col(final).eqNullSafe(F.col("a1_state"))).cast("int")).alias("state"),
        F.sum(
            (~F.col(f"{final}_income").eqNullSafe(F.col("a1_income_level"))).cast("int")
        ).alias("income"),
        F.sum(
            (
                (F.col("aecb_months_w") > 0)
                & F.col(f"{final}_total_ok")
                & (F.col("a1_income_level") != "stable")
            ).cast("int")
        ).alias("fall"),
    ).first()
    lines = [
        (
            f"rows {df.count()}; last step vs the output: {checks['state']} states, "
            f"{checks['income']} income levels differ"
        ),
        "rows per state at each step (high, moderate, low, unknown):",
        *[
            f"  {n:<20} "
            + " ".join(
                f"{r[s]:>8}"
                for r in [
                    df.agg(
                        *[F.sum((F.col(n) == s).cast("int")).alias(s) for s in _STATES]
                    ).first()
                ]
                for s in _STATES
            )
            for n in steps
        ],
    ]
    for a, b in pairwise(steps):
        moved = df.filter(~F.col(a).eqNullSafe(F.col(b)))
        lines += [f"{a} -> {b}: {moved.count()} rows move", *_table(moved, a, b)]
    lines += [
        "income source x income level:",
        *_table(df, "a1_income_source", "a1_income_level"),
        "income source x a1_state:",
        *_table(df, "a1_income_source", "a1_state"),
        "AECB months in W (with the carry) x income level:",
        *_table(df, "aecb_months_w", "a1_income_level"),
        f"AECB in W, window total passes, the 25% check fails: {checks['fall']}",
        "salary stopped x income source x income level:",
        *_table(
            df.filter(F.col("a1_salary_stopped") == 1),
            "a1_income_source",
            "a1_income_level",
        ),
        "salary stopped x a1_state:",
        *_table(df, "a1_salary_stopped", "a1_state"),
    ]
    _log("AECB", model_id, lines)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: replace · base sha256 `57f3970f7dcc5c6fc8b383d183bc9dffe51492cf35a09d18fcee6981862080e6` · base trailing newline: yes · new sha256 `278af8b51db0a35029a57a02a94dc058212c9001418001f167562b0461e2638d` · new trailing newline: yes

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
    salaries in one month and none in the next."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    stable = (total >= INC_FLOORS[w] * floor) & _not_weakening("income", D_INC, True, w)
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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: replace · base sha256 `8ae75773e8de5d602b3c7b0c14f3cfa69bb73946738380332e0fc8acf3e4f7af` · base trailing newline: yes · new sha256 `21c0fb3def888e91ef133091c1e63ed9dc71917807f0d7d2897395f9b8fab424` · new trailing newline: yes

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

TEMPORARY (mirror bundle 12): ``create_b12_check_pipeline`` runs the observation base and
the same nodes, writes the axis to ``crx_<p>_a1_ability_b12_check`` and logs the report
tables (``b12_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b12_check import (
    compare_a1_outputs,
    describe_a1_report,
    describe_a1_sources,
    explain_a1_aecb,
)
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


def create_b12_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_<p>_a1_ability_b12_check + the log-only report nodes.
    Remove with b12_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    check = f"{prefix}_ability_b12_check"
    signals = {
        "income": f"{prefix}_income_signals",
        "liquidity": f"{prefix}_liquidity_signals",
        "distress": f"{prefix}_distress_signals",
    }
    products = "rl_spine" if product == "rl" else obs
    aecb = {
        "obs_base": obs,
        "new": check,
        "income": f"{prefix}_income_signals",
        "liquidity": f"{prefix}_liquidity_signals",
        "internal_salary": "feat_cif_internal_salary_monthly",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        aecb["loan_features"] = "feature_retail_loans"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a1_outputs,
            inputs={
                "old": f"{prefix}_ability",
                "new": check,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"compare_{prefix}_b12",
            tags=tags,
        ),
        node(
            func=describe_a1_report,
            inputs={
                "obs_base": obs,
                "new": check,
                **signals,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b12_report",
            tags=tags,
        ),
        node(
            func=describe_a1_sources,
            inputs={
                "obs_base": obs,
                "new": check,
                "internal_salary": "feat_cif_internal_salary_monthly",
                "bureau_salary": "feat_cif_bureau_salary_monthly",
                "casa_balance": "feat_cif_casa_balance_monthly",
                "casa_activity": "feat_cif_casa_activity_monthly",
                "transactions": "prm_casa_transactions",
                "alerts": "prm_bureau_alert_enriched",
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b12_sources",
            tags=tags,
        ),
        node(
            func=explain_a1_aecb,
            inputs=aecb,
            outputs=None,
            name=f"explain_{prefix}_b12_aecb",
            tags=tags,
        ),
    ]
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_a1_pipeline(product, output=check, anchor=anchor)
        + Pipeline(checks)
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py`
action: replace · base sha256 `628cbd7062a01853872310fe7d00b2f35d3d1b52364696fd7ac73fdd227cdb3f` · base trailing newline: yes · new sha256 `cb0ec529012417c67d7d59da8ce6c5882b4a552e868625747b0fa1b40690f9e4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b12_check_pipeline, create_pipeline

__all__ = ["create_b12_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py`
action: replace · base sha256 `bcd8538b4c889e66fb89dc7187e21aebdcdc8a95793af8a2642d5bbfd652cea1` · base trailing newline: yes · new sha256 `65471a0dac0ff9a071d0c212ed96c20a9504b51271621893f68d04114733268a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CC A1 ability axis on the shared ``a1_ability`` engine; the anchor is
the amount in the oldest overdue bucket (``nodes.py``).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_cc_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_cc_liquidity_anchor

_ANCHOR = node(
    func=build_cc_liquidity_anchor,
    inputs={
        "obs_base": "crx_cc_obs_base",
        "prm_balance": "prm_balance",
        "model_id": "params:model_id",
    },
    outputs="crx_cc_a1_liquidity_anchor",
    name="build_crx_cc_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a1_ability", **kwargs
) -> Pipeline:
    """The CC A1 axis written to ``output``."""
    return create_a1_pipeline("cc", output, _ANCHOR)
`````

New:

`````python
"""Kedro pipeline: CC A1 ability axis on the shared ``a1_ability`` engine; the anchor is
the amount in the oldest overdue bucket (``nodes.py``).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_cc_a1_ability

TEMPORARY (mirror bundle 12): ``create_b12_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b12_check_pipeline as _b12_check
from .nodes import build_cc_liquidity_anchor

_ANCHOR = node(
    func=build_cc_liquidity_anchor,
    inputs={
        "obs_base": "crx_cc_obs_base",
        "prm_balance": "prm_balance",
        "model_id": "params:model_id",
    },
    outputs="crx_cc_a1_liquidity_anchor",
    name="build_crx_cc_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a1_ability", **kwargs
) -> Pipeline:
    """The CC A1 axis written to ``output``."""
    return create_a1_pipeline("cc", output, _ANCHOR)


def create_b12_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the CC A1 check (bundle 12)."""
    return _b12_check("cc", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py`
action: replace · base sha256 `d9c80826be5a36b98e8049bfebe1ad3ddd5b7e7732d9623a954273b03bfed837` · base trailing newline: yes · new sha256 `62ba8267bba4176aa5a72c9f7987fc965f326206237a3b6342f4ffcce45569ce` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b12_check_pipeline, create_pipeline

__all__ = ["create_b12_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `37c113db3d2f61a2869df81ab39279651523c80a12d1a62a69fd5b1dd7992def` · base trailing newline: yes · new sha256 `1e8c5ef25b1239c23f7885de42a4679323931448c61635467b07fbeabbebd662` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``) and the loan's latest bureau pull adds a salary source.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from .nodes import build_rl_liquidity_anchor

_ANCHOR = node(
    func=build_rl_liquidity_anchor,
    inputs={"obs_base": "crx_rl_obs_base", "int_loan_master": "int_loan_master"},
    outputs="crx_rl_a1_liquidity_anchor",
    name="build_crx_rl_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability", **kwargs
) -> Pipeline:
    """The RL A1 axis written to ``output``."""
    return create_a1_pipeline("rl", output, _ANCHOR)
`````

New:

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``) and the loan's latest bureau pull adds a salary source.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_rl_a1_ability

TEMPORARY (mirror bundle 12): ``create_b12_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b12_check_pipeline as _b12_check
from .nodes import build_rl_liquidity_anchor

_ANCHOR = node(
    func=build_rl_liquidity_anchor,
    inputs={"obs_base": "crx_rl_obs_base", "int_loan_master": "int_loan_master"},
    outputs="crx_rl_a1_liquidity_anchor",
    name="build_crx_rl_a1_liquidity_anchor",
    tags=TAGS,
)


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability", **kwargs
) -> Pipeline:
    """The RL A1 axis written to ``output``."""
    return create_a1_pipeline("rl", output, _ANCHOR)


def create_b12_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the RL A1 check (bundle 12)."""
    return _b12_check("rl", _ANCHOR)
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
Clean up after mirror bundle 12_a1_level_check.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths from the
  workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b12_check` (cc_60_180);
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b12_check` (rl_60_180).
- Remove the temporary check (everything marked TEMPORARY for bundle 12):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b12_check` and
    `crx_rl_a1_ability_b12_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a1_ability_b12_check` entries and comments;
  - crx_persona/a1_ability/pipeline.py: `create_b12_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b12_check`, and the TEMPORARY paragraph
    of the module docstring;
  - crx_persona/cc_a1_ability/ and rl_a1_ability/: `create_b12_check_pipeline` in `pipeline.py`
    (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a1_ability/b12_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b12" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under data/input/ is
  tracked or staged. Commit src/ and conf/ and push. Report what you removed and the hdfs commands
  the user still has to run in PROD.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
