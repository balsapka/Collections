# Mirror bundle 11 — A4: RL ECL gap rule removed

apply_bundle version: 7 · built 2026-11-02 from `e342b5f..9912f08` · source: 1 added, 9 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/a4_rl_ecl_gap_removed
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/11_a4_rl_ecl_gap_removed.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '11_a4_rl_ecl_gap_removed.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/11_a4_rl_ecl_gap_removed.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** The tests are yours to update (the bundle does not touch them): remove `ecl_gap_blind_spot_flag`, `ecl_gap_blind_spot`, `ecl_gap_cutoff_date` and `rl_ecl_gap_cutoff_date` from `src/tests/pipelines/crx_persona/` (schemas, fixtures, tests of the rule) and `disbursement_date` / `product_code` from the `crx_rl_full_history` schema. Keep the rest passing.

If `ECL_WINNOWED_PRODUCT_CODES` in `stg_rr_portf.py` has no other use and the source no longer works that way, remove it and its comment; the bundle leaves that file alone because the history fix may have changed it.

Then this must print nothing except `b11_check.py` and that constant if you kept it (otherwise stop and send the output back):

```bash
grep -rnE "ecl_gap|ECL_WINNOWED" src conf --include='*.py' --include='*.yml'
```

A `dpd_journey.rl_ecl_gap_cutoff_date` key left in any parameters file would now stop the run with "unknown parameter(s)": remove it if the grep shows one.

`kedro registry list | grep a4_deterioration` lists `crx_cc_a4_deterioration`, `crx_rl_a4_deterioration` and `crx_rl_a4_deterioration_b11_check`.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A4: RL ECL gap rule removed; temporary b11 check" && git push -u origin feature/a4_rl_ecl_gap_removed
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/11_a4_rl_ecl_gap_removed.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/a4_rl_ecl_gap_removed && git pull
```

Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`, persona dates unchanged. Switch it back when you are done. `int_loan_master` must already hold the fixed history.

**Step 6.** Rebuild the history from the fixed source:

```bash
kedro run --env=dev --pipeline=crx_rl_full_history
```

**Step 7.** Run the check (`crx_rl_a4_deterioration` must still be the old output, so do not run step 8 first):

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration_b11_check
```

Paste back every block from `=== B11 … START ===` to `=== B11 … END ===`: `OUTPUT`, `ECL`, `UNKNOWN`. Aggregates only. Text is best; otherwise one photo per block.

**Step 8.** Only after the B11 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration
```

For `rl_180_plus`, repeat steps 6–8 with that `model_id` if A4 has been run for it.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** RL A4 no longer uses the ECL gap rule, now that the history source covers all loans.

- **Removed**: `ecl_gap_blind_spot_flag` and the rule behind it (`assign_state`, `classify`, `build_dpd_sequences`, `build_deterioration`), the parameter `rl_ecl_gap_cutoff_date`, and `disbursement_date` / `product_code` in `crx_rl_full_history`, which only that rule read.
- **Why**: the rule looked at disbursement date and product code alone, never at the history. Those accounts went to Stabilized or Unknown even with a full clean history.
- **Unchanged**: `ECL_CUTOFF_DATE` and the source union in `stg_rr_portf.py`, the restructured path (`restructure_blind_spot_flag`, Q0), every CC result, every other state rule.
- **Check** (`rl_a4_deterioration/b11_check.py`, pipeline `crx_rl_a4_deterioration_b11_check`): the new state goes to temporary entries and `crx_rl_a4_deterioration` stays untouched as the baseline until step 8. Blocks `B11 OUTPUT` (old × new, new by `loan_type`), `ECL` (flagged accounts: does their history now start before 2025-12, and what they became), `UNKNOWN` (what is left, by route × `loan_type`).
- **Expected**: Unknown falls and, after this bundle, only restructured and cropped accounts can be Unknown, so route `other` must be 0. In `B11 ECL`, `2025_12_or_later` should be near 0: those accounts still miss their older history and would now get a state from a short history. Restructured accounts stay as they are until their new columns are wired in.

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
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/params.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/states.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b11_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_full_history/nodes.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `f4beb7f0165578b7504144fe4adc3ca2ed0325cdbcbde36f68804e868cb0e460` · base trailing newline: yes · new sha256 `b2852152779ea757ccb69c54f8770c9f9e4c89f9f1b70067335ac9e2ac34fd34` · new trailing newline: yes

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

# TEMPORARY (mirror bundle 09): the bundle 05 output, the baseline of the b09 check.
# Remove the entry and its HDFS folder with the check.
crx_cc_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 09): the new output written by the b09 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b09_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b09_check"
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

# TEMPORARY (mirror bundle 09): the bundle 05 output, the baseline of the b09 check.
# Remove the entry and its HDFS folder with the check.
crx_rl_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 09): the new output written by the b09 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b09_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b09_check"
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

# TEMPORARY (mirror bundle 09): the bundle 05 output, the baseline of the b09 check.
# Remove the entry and its HDFS folder with the check.
crx_cc_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 09): the new output written by the b09 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b09_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b09_check"
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

# TEMPORARY (mirror bundle 09): the bundle 05 output, the baseline of the b09 check.
# Remove the entry and its HDFS folder with the check.
crx_rl_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 09): the new output written by the b09 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b09_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b09_check"
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
action: replace · base sha256 `552a4e8a3a680fb83b9a64388c5f3e12d0501eaf73708d5ded906edaec07fd23` · base trailing newline: yes · new sha256 `44e83dc8aaae035aaaf8b60e86d2f6bb8045d0d347675267103138b775ef96af` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 09): A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_ability_b09_check": (
            crx_cc_a1_ability.create_b09_check_pipeline()
        ),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 09): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b09_check": (
            crx_rl_a1_ability.create_b09_check_pipeline()
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
        # TEMPORARY (mirror bundle 09): A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_ability_b09_check": (
            crx_cc_a1_ability.create_b09_check_pipeline()
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
        # TEMPORARY (mirror bundle 09): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b09_check": (
            crx_rl_a1_ability.create_b09_check_pipeline()
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

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/params.py`
action: replace · base sha256 `d9eb11817bbc817a7d6a84e5dad2139c0af819a5e14c9ed7e3cfe2d710be6097` · base trailing newline: yes · new sha256 `0e0e8f0450b7fc0102cda7b1932d3cf7a609eb805e25ec283550e227f946411b` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Run parameters: defaults, the resolved dataclass, and the merge/validate entrypoint."""

from __future__ import annotations

from dataclasses import dataclass

from enbd_collections.nodes.staging.retail_loans.stg_rr_portf import ECL_CUTOFF_DATE

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
    # RL only. The int_loan_master lineage unions the Group ECL historical extract
    # (pre-cutoff) with the DPL monthly tables (post-cutoff) at this exact date — imported
    # from stg_rr_portf.py::ECL_CUTOFF_DATE (single source of truth, no longer duplicated).
    # Accounts disbursed before this date whose product_code falls outside
    # ECL_WINNOWED_PRODUCT_CODES are a confirmed raw-source gap (the pre-cutoff ECL
    # historical extract is structurally winnowed to those codes server-side) — RL-A4-5/
    # RL-A4-6/RL-A4-8 -> ecl_gap_blind_spot_flag. No cc_ variant: CC has no equivalent
    # mechanism.
    "rl_ecl_gap_cutoff_date": ECL_CUTOFF_DATE,
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
    ecl_gap_cutoff_date: str | None
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
        ecl_gap_cutoff_date=p.get(f"{scheme.name}_ecl_gap_cutoff_date"),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py`
action: replace · base sha256 `4fd316620ecdfc471660724285b0821a357bca60f8a8bf538068139998f6dfec` · base trailing newline: yes · new sha256 `423acd6fe8711e087a8fcbd6da08d8c693b823cbbea619456e4451476fd38030` · new trailing newline: yes

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

from enbd_collections.nodes.staging.retail_loans.stg_rr_portf import (
    ECL_WINNOWED_PRODUCT_CODES,
)

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
    optionally restructure_flag (0/1 per row; max over the account's rows), optionally
    disbursement_date (date; max over the account's rows, robust to nulls elsewhere),
    optionally product_code (string; max over the account's rows, robust to nulls
    elsewhere).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag,
        ecl_gap_blind_spot_flag (1 if disbursement_date AND product_code are both present,
        params.ecl_gap_cutoff_date is set, the account disbursed before that cutoff, and its
        product_code is NOT one of ECL_WINNOWED_PRODUCT_CODES -- the pre-cutoff ECL
        historical extract is structurally winnowed server-side to those codes only, so a
        loan outside that set is genuinely, structurally absent from it regardless of
        disbursement date (confirmed root cause, RL-A4-5/RL-A4-6/RL-A4-8); 0 otherwise/when
        a required column or the param is absent, e.g. CC, which has neither column)
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
    has_ecl_gap_check = (
        "disbursement_date" in history.columns
        and "product_code" in history.columns
        and params.ecl_gap_cutoff_date
    )
    if has_ecl_gap_check:
        aggs.append(F.max(F.col("disbursement_date").cast("date")).alias("_disb_date"))
        aggs.append(
            F.max(F.trim(F.col("product_code").cast("string"))).alias("_product_code")
        )
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    per_acc = per_acc.crossJoin(F.broadcast(source_min))

    if has_ecl_gap_check:
        covered = list(ECL_WINNOWED_PRODUCT_CODES)
        per_acc = per_acc.withColumn(
            "_ecl_gap_blind_spot",
            (
                F.col("_disb_date").isNotNull()
                & (F.col("_disb_date") < F.lit(params.ecl_gap_cutoff_date).cast("date"))
                & F.col("_product_code").isNotNull()
                & (~F.col("_product_code").isin(covered))
            ).cast("int"),
        )
    else:
        per_acc = per_acc.withColumn("_ecl_gap_blind_spot", F.lit(0))

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
        F.col("_ecl_gap_blind_spot").alias("ecl_gap_blind_spot_flag"),
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
    sequences: DataFrame, scheme: BucketScheme, params: JourneyParams, spine: DataFrame
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
        restructure_blind_spot_flag, ecl_gap_blind_spot_flag, computed_at
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

    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot, ecl_gap_blind_spot):
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
            bool(ecl_gap_blind_spot),
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema)(
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
            "ecl_gap_blind_spot_flag",
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
        F.col("ecl_gap_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always-on, like every other persona axis's own state-distribution log
    # (cc_a2_locatability_v2/cc_a3_payment_credibility's own _log_*_stats) — not
    # gated behind log_stats, which here only controls the heavier Stage 1
    # build_dpd_sequences telemetry above. The month filter inside _log_state_stats
    # pushes down through the join, so this does not force materialization of the
    # full point-in-time result.
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
    sequences: DataFrame, scheme: BucketScheme, params: JourneyParams, spine: DataFrame
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
    _log_state_stats(out, params.end_date, scheme, params)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/states.py`
action: replace · base sha256 `ab01ce21d5405b6ee831fd858a78dfac618fd46bb53754150b06d81e83dd9464` · base trailing newline: yes · new sha256 `40be38e3fa8c6a71d1fef19b4dbb18e1a7fc292ffd4e8de2617c64889a0da797` · new trailing newline: yes

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
    ecl_gap_blind_spot: bool = False,
) -> str:
    """One state per account, same tree and vocabulary in both segments. First 'yes' wins.

    ECL  a confirmed per-account source gap (RL ECL/DPL union seam, RL-A4-5/RL-A4-6) means
                             we have no reliable signal about this account's shape before
                             the visible window AT ALL, not just its exact onset month ->
                             bypasses the whole cascade: stabilized if Q2, else unknown
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
    # ECL — a confirmed per-account source gap (RL ECL/DPL union seam) means we have no
    # reliable signal about this account's shape before the visible window AT ALL, not
    # just its exact onset month. Unlike cropped/restructure_blind_spot (which still
    # trust the visible run-up's shape for Q3/Q4), this also disqualifies that shape,
    # since the run-up itself may be a window-boundary artifact of the data gap, not the
    # account's true history — bypasses the whole cascade. This is the only path that
    # reaches "unknown" for an EPD-shaped (clean-then-delinquent) sequence, which
    # starts_delinquent-gated Q0 structurally cannot do (RL-A4-7).
    if ecl_gap_blind_spot:
        return "stabilized" if stab else "unknown"
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
    ecl_gap_blind_spot: bool = False,
) -> dict:
    """Features + state for one account (native buckets, oldest -> newest)."""
    f = journey_features(
        [max(x + offset, 1) for x in buckets_native], canon_top, repair
    )
    f["det_state"] = assign_state(
        f, cropped, restructure_blind_spot, ecl_gap_blind_spot
    )
    return f
`````

New:

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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py`
action: replace · base sha256 `03e71607f8704f47eecb5035ff4660a46d9e67ea2097b77a7c6f29103a94a449` · base trailing newline: yes · new sha256 `75b8bdfdadb4c89fdd15f82fc6b3df9540fe804c82213243ad3a3611d4414142` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4-3 — DPD-journey deterioration state pipeline for Retail Loans."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL-A4-3 — DPD-journey deterioration state pipeline for Retail Loans."""

from .pipeline import create_b11_check_pipeline, create_pipeline

__all__ = ["create_b11_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b11_check.py`
action: add · new sha256 `3efe7c669b98df92a7a85cf8728ccf73c3c1d9a8a1a3ea655aeeaf86fd40c91b` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 11): RL A4 without the ECL gap rule, old vs new, in PROD.

The old output (``crx_rl_a4_deterioration``) still carries ``ecl_gap_blind_spot_flag``
until step 8 rewrites it. Log blocks, aggregates only, latest observation month:

* ``B11 OUTPUT``: states old × new, and new states by ``loan_type``.
* ``B11 ECL``: the accounts the rule flagged, by ``loan_type`` and whether their history
  now starts before the old table's end (2025-12), then their new states.
* ``B11 UNKNOWN``: what is left in Unknown, by route and ``loan_type``.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_KEY = ["account_id", "observation_date"]
_SEAM = "2025-12-01"


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B11 {name} START === [{model_id}]",
        *lines,
        f"=== B11 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<28}" for c in cols)
        + f" {r['count']:>9}  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest_month(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(
        F.trunc("observation_date", "month") == F.trunc(F.lit(last), "month")
    )


def _keyed(df: DataFrame, *cols: str) -> DataFrame:
    return df.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        *cols,
    )


def compare_rl_a4_outputs(
    old: DataFrame,
    new: DataFrame,
    sequences: DataFrame,
    rl_spine: DataFrame,
    model_id: str,
) -> None:
    """Log the B11 blocks; the baseline must carry ``ecl_gap_blind_spot_flag``."""
    start = sequences.select(
        F.col("account_id").cast("string").alias("account_id"), "first_month"
    )
    products = _keyed(rl_spine, "loan_type").dropDuplicates(_KEY)
    frame = (
        _keyed(
            new,
            "det_state",
            "starts_delinquent",
            "history_cropped",
            "n_months_truncated",
            "restructure_blind_spot_flag",
            "history_months",
        )
        .join(
            _keyed(
                old,
                F.col("det_state").alias("old_state"),
                F.col("ecl_gap_blind_spot_flag").alias("ecl_flag"),
            ),
            on=_KEY,
            how="left",
        )
        .join(products, on=_KEY, how="left")
        .join(start, on="account_id", how="left")
    )
    latest = _latest_month(frame).cache()

    _log(
        "OUTPUT",
        model_id,
        [
            f"accounts {latest.count()}",
            "old x new",
            *_table(latest, "old_state", "det_state"),
            "loan_type x new",
            *_table(latest, "loan_type", "det_state"),
        ],
    )

    flagged = latest.filter(F.col("ecl_flag") == 1).withColumn(
        "history_from",
        F.when(
            F.col("first_month") < F.lit(_SEAM).cast("date"), "before_2025_12"
        ).otherwise("2025_12_or_later"),
    )
    _log(
        "ECL",
        model_id,
        [
            f"flagged {flagged.count()}",
            "loan_type x history_from",
            *_table(flagged, "loan_type", "history_from"),
            "history_from x old x new",
            *_table(flagged, "history_from", "old_state", "det_state"),
            "history_from: history_months min / median / max",
            *[
                f"  {r['history_from']}: {r['q']}"
                for r in flagged.groupBy("history_from")
                .agg(
                    F.expr("percentile_approx(history_months, array(0, 0.5, 1))").alias(
                        "q"
                    )
                )
                .collect()
            ],
        ],
    )

    unknown = latest.filter(F.col("det_state") == "unknown").withColumn(
        "route",
        F.when(F.col("restructure_blind_spot_flag") == 1, "restructured")
        .when(F.col("n_months_truncated") > 0, "cropped_gap")
        .when(F.col("history_cropped"), "cropped_source_start")
        .otherwise("other"),
    )
    _log(
        "UNKNOWN",
        model_id,
        [
            f"unknown {unknown.count()}",
            "route x loan_type",
            *_table(unknown, "route", "loan_type"),
        ],
    )
    latest.unpersist()
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py`
action: replace · base sha256 `51c249836d0833ad14845b09a42f031d0385c3da8c8a700f1f0dd288da045867` · base trailing newline: yes · new sha256 `4266f27ae8587c027f026c0349a1f0423eb2d3dfd43abf380b3b0094aaf88ea7` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_dpd_sequences    crx_rl_full_history  -> crx_rl_dpd_sequences
Node 2 build_rl_a4_deterioration crx_rl_dpd_sequences -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import RL, build_deterioration, build_dpd_sequences, journey_params


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (1 if the loan was restructured in any month) +
    ecl_gap_blind_spot_flag (1 if the loan was disbursed before the ECL/DPL union seam
    AND its product_code falls outside the set the pre-cutoff ECL historical extract is
    structurally winnowed to — see _dpd_journey.spark.build_dpd_sequences).
    """
    history = crx_rl_full_history.select(
        "account_id",
        F.col("month_end_date").alias("obs_date"),
        "dlq_bucket",
        "restructure_flag",
        "disbursement_date",
        "product_code",
    )
    return build_dpd_sequences(history, RL, journey_params(crx_persona, RL, model_id))


def build_rl_a4_deterioration(
    crx_rl_dpd_sequences: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here."""
    spine = rl_spine.select("account_id", "observation_date")
    return build_deterioration(
        crx_rl_dpd_sequences, RL, journey_params(crx_persona, RL, model_id), spine
    )
`````

New:

`````python
"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_dpd_sequences    crx_rl_full_history  -> crx_rl_dpd_sequences
Node 2 build_rl_a4_deterioration crx_rl_dpd_sequences -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._dpd_journey import RL, build_deterioration, build_dpd_sequences, journey_params


def build_rl_dpd_sequences(
    crx_rl_full_history: DataFrame, crx_persona: dict, model_id: str
) -> DataFrame:
    """One row per RL account: gap-filled monthly bucket array + audit columns +
    restructure_blind_spot_flag (1 if the loan was restructured in any month).
    """
    history = crx_rl_full_history.select(
        "account_id",
        F.col("month_end_date").alias("obs_date"),
        "dlq_bucket",
        "restructure_flag",
    )
    return build_dpd_sequences(history, RL, journey_params(crx_persona, RL, model_id))


def build_rl_a4_deterioration(
    crx_rl_dpd_sequences: DataFrame,
    rl_spine: DataFrame,
    crx_persona: dict,
    model_id: str,
) -> DataFrame:
    """One deterioration state per (account, rl_spine observation_date) row: this row's
    billing history truncated to its own date, classified by the same engine as
    build_rl_dpd_sequences. rl_spine is already model_id/DLQ-band scoped by construction
    (R20) -- no separate segment filter needed here."""
    spine = rl_spine.select("account_id", "observation_date")
    return build_deterioration(
        crx_rl_dpd_sequences, RL, journey_params(crx_persona, RL, model_id), spine
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py`
action: replace · base sha256 `375a6b3e356c0a496eb9aea6717f5bc5f263b26e821833b85c9a4477f08679fc` · base trailing newline: yes · new sha256 `fd2f0bff5d1d549b48f1332b2b63ca05fa43fc6c04eea382c3ce11ccaaf77440` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

2-node pipeline:
    Node 1  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 2  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_a4_deterioration, build_rl_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=[
                    "crx_rl_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_dpd_sequences",
                name="build_crx_rl_dpd_sequences",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=[
                    "crx_rl_dpd_sequences",
                    "rl_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_a4_deterioration",
                name="build_crx_rl_a4_deterioration",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

2-node pipeline:
    Node 1  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 2  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration

TEMPORARY (mirror bundle 11): create_b11_check_pipeline writes the new state to temporary
entries and logs old vs new; removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .b11_check import compare_rl_a4_outputs
from .nodes import build_rl_a4_deterioration, build_rl_dpd_sequences


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """2-node pipeline: build per-account DPD sequences, then classify deterioration state."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=[
                    "crx_rl_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_dpd_sequences",
                name="build_crx_rl_dpd_sequences",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=[
                    "crx_rl_dpd_sequences",
                    "rl_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_a4_deterioration",
                name="build_crx_rl_a4_deterioration",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )


def create_b11_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the new RL A4 into temporary entries, then old vs new (bundle 11)."""
    return Pipeline(
        [
            node(
                func=build_rl_dpd_sequences,
                inputs=[
                    "crx_rl_full_history",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_dpd_sequences_b11_check",
                name="build_crx_rl_dpd_sequences_b11_check",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=build_rl_a4_deterioration,
                inputs=[
                    "crx_rl_dpd_sequences_b11_check",
                    "rl_spine",
                    "params:crx_persona",
                    "params:model_id",
                ],
                outputs="crx_rl_a4_deterioration_b11_check",
                name="build_crx_rl_a4_deterioration_b11_check",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
            node(
                func=compare_rl_a4_outputs,
                inputs=[
                    "crx_rl_a4_deterioration",
                    "crx_rl_a4_deterioration_b11_check",
                    "crx_rl_dpd_sequences_b11_check",
                    "rl_spine",
                    "params:model_id",
                ],
                outputs=None,
                name="compare_rl_a4_outputs",
                tags=["crx", "rl", "rl_a4_deterioration"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_full_history/nodes.py`
action: replace · base sha256 `f2472dbacbc97d9789a2bcabd0c018284298281fe472f06a0c3a587b42dc2a0f` · base trailing newline: yes · new sha256 `c45a11daed8c58243be19a5a08c597653bfe89fbc09cab8fcaf57f9ddf260e5e` · new trailing newline: yes

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
            emi_coverage_ratio, outstanding_balance, is_restructured, loan_type,
            disbursement_date, product_code.
        crx_persona: optional params dict (only dpd_journey.log_stats is read).

    Returns:
        DataFrame at grain (account_id, month_end_date): account_id string, month_end_date
        date, dlq_bucket int, emi_coverage_ratio double, outstanding_balance double,
        restructure_flag int, loan_type string, disbursement_date date, product_code string,
        computed_at timestamp.
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
        F.col("disbursement_date").cast("date"),
        F.col("product_code").cast("string"),
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
Clean up after mirror bundle 11_a4_rl_ecl_gap_removed.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths for model_id rl_60_180 **and** rl_180_plus from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`. Skip any that does not exist:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b11_check`
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b11_check`
- Remove the temporary check (everything marked TEMPORARY for bundle 11):
  - conf/base/catalog/catalog_crx.yml: the two `*_b11_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the `crx_rl_a4_deterioration_b11_check` entry and its comment;
  - crx_persona/rl_a4_deterioration/pipeline.py: `create_b11_check_pipeline`, the `b11_check` import and the TEMPORARY docstring paragraph;
  - crx_persona/rl_a4_deterioration/__init__.py: `create_b11_check_pipeline`;
  - delete crx_persona/rl_a4_deterioration/b11_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b11\|ecl_gap" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script): rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what you removed and the hdfs commands the user still has to run in PROD.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
