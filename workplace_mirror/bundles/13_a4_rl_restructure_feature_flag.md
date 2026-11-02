# Mirror bundle 13 — A4: restructured loans from has_restructured_loan_flag

apply_bundle version: 7 · built 2026-11-02 from `e65001a..230139b` · source: 1 added, 6 replaced, 1 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/a4_rl_restructure_feature_flag
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/13_a4_rl_restructure_feature_flag.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '13_a4_rl_restructure_feature_flag.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/13_a4_rl_restructure_feature_flag.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Confirm `feature_retail_loans` has `has_restructured_loan_flag` and `account_id` at (account_id, observation_date); if not, name the dataset that does and stop. If bundle 11's check is already cleaned up in this repo, the merge keeps it out.

The tests are yours to update: `build_rl_dpd_sequences` and `build_rl_a4_deterioration` callers, the new `build_rl_linked_dpd_sequences`, and the schemas without `restructure_flag` (linked history) and `chain_restructure_flag`. Keep the rest passing.

Then `kedro registry list | grep a4_deterioration` lists `crx_rl_a4_deterioration_b13_check` and no `b11`, and this prints only `b13_check.py` lines if anything:

```bash
grep -rn "is_restructured" src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration
```

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A4: restructured from has_restructured_loan_flag; temporary b13 check" && git push -u origin feature/a4_rl_restructure_feature_flag
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/13_a4_rl_restructure_feature_flag.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/a4_rl_restructure_feature_flag && git pull
```

**Before this:** bundle 11's step 8 must be done, so `crx_rl_a4_deterioration` is the baseline. Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`, and make sure `feature_retail_loans` is built for it.

**Step 6.** Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration_b13_check
```

Paste back every block from `=== B13 … START ===` to `=== B13 … END ===`: `OUTPUT`, `RESTRUCTURE`, `UNKNOWN`. Aggregates only. Text is best; otherwise one photo per block.

**Step 7.** Only after the B13 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** RL A4 decides whether a loan is restructured from `feature_retail_loans.has_restructured_loan_flag`, not `is_restructured` (user, 2026-11-02).

- **`restructure_blind_spot_flag`** = the feature flag was ever set for the account, except an account with its original loans' months in front of its own, which is no longer blind. `build_rl_dpd_sequences` reads the feature; `build_rl_linked_dpd_sequences` is new.
- **Removed**: `is_restructured` from the A4 path. `crx_rl_full_history_linked` no longer has `restructure_flag`, `crx_rl_restructure_chains` no longer has `chain_restructure_flag`.
- **One rule goes**: "a chain ending in an unmatched restructure stays blind" read `is_restructured` on the original loans. `feature_retail_loans` has spine rows only, so it has no value for them, and a stitched account is now simply not blind.
- **Unchanged**: chains and stitching (still `int_loan_restructure_link`), unmatched restructured loans blind for life, `crx_rl_full_history.restructure_flag` (`crx_rl_spell_table` still reads it), every state rule, CC.
- **Check** (`rl_a4_deterioration/b13_check.py`, pipeline `crx_rl_a4_deterioration_b13_check`, replacing bundle 11's): blocks `B13 OUTPUT` (old × new, new by `loan_type`), `RESTRUCTURE` (flag by `loan_type`, stitched, blind, old vs new blind, stitched without the flag), `UNKNOWN`.
- **Expected**: few state moves, only on accounts whose blind spot changes. The number to read is restructured Auto in `B13 RESTRUCTURE`: bundle 11 showed 0.

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
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b13_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/chains.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b11_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `5f3c6482d189b90a75ddbb36d755b86fe91ff9036aaa9119f320001329b9a081` · base trailing newline: yes · new sha256 `49a3de021a0adcbf5d0b13f605cec09b0897358094c0bbd70304914024c74283` · new trailing newline: yes

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

# TEMPORARY (mirror bundle 13): the sequences of the b13 check.
crx_rl_dpd_sequences_b13_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b13_check"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 13): the new output written by the b13 check pipeline.
crx_rl_a4_deterioration_b13_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b13_check"
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
action: replace · base sha256 `281a3618092d863124ef9377489d8556ed8e0c32189c817d47dfe003f3087c59` · base trailing newline: yes · new sha256 `bd44dc2e35c492d467d2debe5f6bce6cd844362332091c49772007b9192ab90c` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 13): A4 check; removed by the bundle's cleanup.
        "crx_rl_a4_deterioration_b13_check": (
            crx_rl_a4_deterioration.create_b13_check_pipeline()
        ),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 12): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b12_check": (
            crx_rl_a1_ability.create_b12_check_pipeline()
        ),
        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/__init__.py`
action: replace · base sha256 `75b8bdfdadb4c89fdd15f82fc6b3df9540fe804c82213243ad3a3611d4414142` · base trailing newline: yes · new sha256 `89d7b08c25ac77cd65ca383de1d6ba5c1717a1e8b916efc6d52f7a756def2d4e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4-3 — DPD-journey deterioration state pipeline for Retail Loans."""

from .pipeline import create_b11_check_pipeline, create_pipeline

__all__ = ["create_b11_check_pipeline", "create_pipeline"]
`````

New:

`````python
"""RL-A4-3 — DPD-journey deterioration state pipeline for Retail Loans."""

from .pipeline import create_b13_check_pipeline, create_pipeline

__all__ = ["create_b13_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b13_check.py`
action: add · new sha256 `fd7cf345de7ab8599036cba1e47c2ae0e0e8cc53210bf2146be8e49fc1534364` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 13): RL A4 on ``has_restructured_loan_flag``, old vs new, in PROD.

The old output (``crx_rl_a4_deterioration``) is bundle 11's, which read ``is_restructured``.
Log blocks, aggregates only, latest observation month:

* ``B13 OUTPUT``: states old × new, and new states by ``loan_type``.
* ``B13 RESTRUCTURE``: the feature flag by ``loan_type``, stitched and still blind, old vs
  new blind spot, states of the blind rows, stitched accounts the flag does not mark.
* ``B13 UNKNOWN``: what is left in Unknown, by route and ``loan_type``.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_KEY = ["account_id", "observation_date"]


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B13 {name} START === [{model_id}]",
        *lines,
        f"=== B13 {name} END ===",
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
    feature_retail_loans: DataFrame,
    rl_spine: DataFrame,
    model_id: str,
) -> None:
    """Log the B13 blocks; the baseline is bundle 11's output (step 8 done)."""
    products = _keyed(rl_spine, "loan_type").dropDuplicates(_KEY)
    flags = _keyed(
        feature_retail_loans,
        F.col("has_restructured_loan_flag").cast("int").alias("feature_flag"),
    ).dropDuplicates(_KEY)
    frame = (
        _keyed(
            new,
            "det_state",
            "history_cropped",
            "n_months_truncated",
            F.col("restructure_blind_spot_flag").alias("blind"),
            F.col("chain_stitched_flag").alias("stitched"),
        )
        .join(
            _keyed(
                old,
                F.col("det_state").alias("old_state"),
                F.col("restructure_blind_spot_flag").alias("old_blind"),
            ),
            on=_KEY,
            how="left",
        )
        .join(products, on=_KEY, how="left")
        .join(flags, on=_KEY, how="left")
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

    restructured = latest.filter(F.col("feature_flag") == 1)
    blind = latest.filter(F.col("blind") == 1)
    unflagged = latest.filter(
        (F.col("stitched") == 1) & ~F.coalesce(F.col("feature_flag") == 1, F.lit(False))
    )
    _log(
        "RESTRUCTURE",
        model_id,
        [
            f"flag set {restructured.count()}",
            "loan_type x stitched x blind (flag set)",
            *_table(restructured, "loan_type", "stitched", "blind"),
            "old_blind x blind",
            *_table(latest, "old_blind", "blind"),
            "blind: old x new",
            *_table(blind, "old_state", "det_state"),
            f"stitched without the flag: {unflagged.count()}",
        ],
    )

    unknown = latest.filter(F.col("det_state") == "unknown").withColumn(
        "route",
        F.when(F.col("blind") == 1, "restructured")
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/chains.py`
action: replace · base sha256 `4abb99aa6bc346224899d22d2159955423c60353f7b27119d30fc3ae6d103cb3` · base trailing newline: yes · new sha256 `15f8b81e2dbcede9e20228b19674c4b499d198d87d0030838e2866a9a2a1c11c` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Restructure chains: a restructured loan and the closed original loans behind it.

``int_loan_restructure_link`` is one edge per (restructured account, original account). An
original can itself be a restructured loan, so edges are walked transitively; plain Python,
as the link is small and a cycle must not loop.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, NamedTuple


class Edge(NamedTuple):
    """One link row. ``known``: the later of restructure flag and original closure."""

    account: str
    original: str
    known: date
    match_type: str
    candidates: int


class Chain(NamedTuple):
    """One restructured account with everything walked behind it."""

    account: str
    known: date
    n_originals: int
    match_type: str
    candidates: int


class Member(NamedTuple):
    """One original loan of a chain. ``is_end``: it has no original of its own."""

    account: str
    original: str
    is_end: bool


def resolve_chains(
    edges: Iterable[Edge], accounts: Iterable[str]
) -> tuple[list[Chain], list[Member]]:
    """Walk every account in ``accounts`` back through ``edges``."""
    by_account: dict[str, list[Edge]] = defaultdict(list)
    for edge in edges:
        by_account[edge.account].append(edge)

    chains, members = [], []
    for account in accounts:
        seen, stack, walked = {account}, [account], []
        while stack:
            for edge in by_account.get(stack.pop(), ()):
                walked.append(edge)
                if edge.original not in seen:
                    seen.add(edge.original)
                    stack.append(edge.original)
        if not walked:
            continue
        originals = sorted(seen - {account})
        chains.append(
            Chain(
                account,
                max(e.known for e in walked),
                len(originals),
                (
                    "many_to_one"
                    if any(e.match_type == "many_to_one" for e in walked)
                    else "one_to_one"
                ),
                max(e.candidates for e in walked),
            )
        )
        members += [Member(account, o, o not in by_account) for o in originals]
    return chains, members
`````

New:

`````python
"""Restructure chains: a restructured loan and the closed original loans behind it.

``int_loan_restructure_link`` is one edge per (restructured account, original account). An
original can itself be a restructured loan, so edges are walked transitively; plain Python,
as the link is small and a cycle must not loop.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import date
from typing import Iterable, NamedTuple


class Edge(NamedTuple):
    """One link row. ``known``: the later of restructure flag and original closure."""

    account: str
    original: str
    known: date
    match_type: str
    candidates: int


class Chain(NamedTuple):
    """One restructured account with everything walked behind it."""

    account: str
    known: date
    n_originals: int
    match_type: str
    candidates: int


class Member(NamedTuple):
    """One original loan of a chain."""

    account: str
    original: str


def resolve_chains(
    edges: Iterable[Edge], accounts: Iterable[str]
) -> tuple[list[Chain], list[Member]]:
    """Walk every account in ``accounts`` back through ``edges``."""
    by_account: dict[str, list[Edge]] = defaultdict(list)
    for edge in edges:
        by_account[edge.account].append(edge)

    chains, members = [], []
    for account in accounts:
        seen, stack, walked = {account}, [account], []
        while stack:
            for edge in by_account.get(stack.pop(), ()):
                walked.append(edge)
                if edge.original not in seen:
                    seen.add(edge.original)
                    stack.append(edge.original)
        if not walked:
            continue
        originals = sorted(seen - {account})
        chains.append(
            Chain(
                account,
                max(e.known for e in walked),
                len(originals),
                (
                    "many_to_one"
                    if any(e.match_type == "many_to_one" for e in walked)
                    else "one_to_one"
                ),
                max(e.candidates for e in walked),
            )
        )
        members += [Member(account, o) for o in originals]
    return chains, members
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/nodes.py`
action: replace · base sha256 `ba735f330e2164de99a11c274af774a0097160d5c4c8350991a165932bf9fa2e` · base trailing newline: yes · new sha256 `9087ba44674bb2d61fdf3309e14220ec981cafc81e3d21d6cea95e380b9a474f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A4 — DPD-journey deterioration state for retail loans (thin wrappers on _dpd_journey).

Node 1 build_rl_full_history_linked  crx_rl_full_history + int_loan_master
                                     + int_loan_restructure_link
                                     -> crx_rl_full_history_linked, crx_rl_restructure_chains
Node 2 build_rl_dpd_sequences        crx_rl_full_history -> crx_rl_dpd_sequences
Node 3 build_rl_dpd_sequences        crx_rl_full_history_linked
                                     -> crx_rl_dpd_sequences_linked
Node 4 build_rl_a4_deterioration     both sequences + chains -> crx_rl_a4_deterioration

RL buckets: 0 = 0 DPD, 1 = 1-30, 2 = 31-60, ..., 6 = 151-180, 7 = 180+ (cap). The engine maps
them onto the CC scale (+1), so every rule and threshold is shared with CC. The 60-180
segment is RL 3-6, the 180+ segment is RL 7. RL history is trusted in full (no floor).

A restructure closes the old account and opens a new one. A matched new account gets the
original loans' months in front of its own, from the month both the restructure flag and
the closure have happened; before that month it keeps its own history, so nothing leaks
from the future. Unmatched restructured accounts stay blind spots.
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
        T.StructField("is_end", T.BooleanType()),
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
    ``restructure_flag`` becomes 0 on a chain with months added, unless the chain ends in a
    restructured loan with no original of its own.

    Returns:
        crx_rl_full_history_linked: account_id, month_end_date, dlq_bucket, restructure_flag.
        crx_rl_restructure_chains: one row per chain: account_id, chain_known_date,
        chain_n_originals, chain_match_type, chain_candidate_count, chain_months_added,
        chain_restructure_flag.
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
            "is_restructured",
            "account_status",
        ),
        "int_loan_master",
    )
    own = crx_rl_full_history.select(
        "account_id",
        F.last_day("month_end_date").alias("month_end_date"),
        "dlq_bucket",
        "restructure_flag",
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
            F.col("is_restructured").cast("int").alias("_flag"),
            F.upper(F.col("account_status")).alias("_status"),
        )
        .join(F.broadcast(member_df), on="original_id")
        .filter(F.coalesce(F.col("_status"), F.lit("")) != "CLOSED")
        .groupBy("account_id", "month_end_date")
        .agg(
            F.max("dlq_bucket").alias("dlq_bucket"),
            F.max(F.when(F.col("is_end"), F.col("_flag"))).alias("_end_flag"),
        )
        .join(own, on=["account_id", "month_end_date"], how="left_anti")
    )
    added = original.groupBy("account_id").agg(
        F.count(F.lit(1)).cast("int").alias("chain_months_added"),
        F.coalesce(F.max("_end_flag"), F.lit(0)).cast("int").alias("_end_flag"),
    )
    chain_out = (
        chain_df.join(added, on="account_id", how="left")
        .withColumn("chain_months_added", F.coalesce("chain_months_added", F.lit(0)))
        .withColumn(
            "chain_restructure_flag",
            F.when(F.col("chain_months_added") > 0, F.col("_end_flag")).otherwise(1),
        )
        .drop("_end_flag")
    )
    linked = (
        own.unionByName(
            original.select(
                "account_id",
                "month_end_date",
                "dlq_bucket",
                F.lit(0).alias("restructure_flag"),
            )
        )
        .join(
            F.broadcast(chain_out.select("account_id", "chain_restructure_flag")),
            on="account_id",
            how="left",
        )
        .withColumn(
            "restructure_flag",
            F.coalesce("chain_restructure_flag", "restructure_flag"),
        )
        .drop("chain_restructure_flag")
    )
    return linked, chain_out


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
    out = out.join(
        chains.drop("chain_restructure_flag"), on="account_id", how="left"
    ).withColumn(
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/pipeline.py`
action: replace · base sha256 `846d3404012b2c48cb7223a3f2343e532d67706d8617f5e5435abe2ab408575a` · base trailing newline: yes · new sha256 `df8f038541fc786d471d2c15ee6ce34cd8eece3417d93ebb961eb8f0a2659679` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A4-3 — DPD-journey deterioration state for Retail Loans.

4-node pipeline:
    Node 1  build_rl_full_history_linked -> crx_rl_full_history_linked,
                                            crx_rl_restructure_chains
    Node 2  build_rl_dpd_sequences       -> crx_rl_dpd_sequences
    Node 3  build_rl_dpd_sequences       -> crx_rl_dpd_sequences_linked
    Node 4  build_rl_a4_deterioration    -> crx_rl_a4_deterioration

Requires crx_rl_full_history (RL-B1) to already be materialized.

Run with:
    kedro run --pipeline=crx_rl_a4_deterioration

TEMPORARY (mirror bundle 11): create_b11_check_pipeline writes the new state to temporary
entries and logs old vs new; removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .b11_check import compare_rl_a4_outputs
from .nodes import (
    build_rl_a4_deterioration,
    build_rl_dpd_sequences,
    build_rl_full_history_linked,
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


def _sequences_node(history: str, output: str) -> node:
    return node(
        func=build_rl_dpd_sequences,
        inputs=[history, "params:crx_persona", "params:model_id"],
        outputs=output,
        name=f"build_{output}",
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
            _sequences_node("crx_rl_full_history", "crx_rl_dpd_sequences"),
            _sequences_node(
                "crx_rl_full_history_linked", "crx_rl_dpd_sequences_linked"
            ),
            _state_node("crx_rl_dpd_sequences", "crx_rl_a4_deterioration"),
        ],
        tags=["crx_persona"],
    )


def create_b11_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the new RL A4 into temporary entries, then old vs new (bundle 11)."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_full_history", "crx_rl_dpd_sequences_b11_check"),
            _sequences_node(
                "crx_rl_full_history_linked", "crx_rl_dpd_sequences_linked"
            ),
            _state_node(
                "crx_rl_dpd_sequences_b11_check", "crx_rl_a4_deterioration_b11_check"
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

New:

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

TEMPORARY (mirror bundle 13): create_b13_check_pipeline writes the new state to temporary
entries and logs old vs new; removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .b13_check import compare_rl_a4_outputs
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


def create_b13_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the new RL A4 into temporary entries, then old vs new (bundle 13)."""
    return Pipeline(
        [
            _linked_node(),
            _sequences_node("crx_rl_dpd_sequences_b13_check"),
            _linked_sequences_node(),
            _state_node(
                "crx_rl_dpd_sequences_b13_check", "crx_rl_a4_deterioration_b13_check"
            ),
            node(
                func=compare_rl_a4_outputs,
                inputs=[
                    "crx_rl_a4_deterioration",
                    "crx_rl_a4_deterioration_b13_check",
                    "feature_retail_loans",
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration/b11_check.py`
action: delete · base sha256 `6511cb373074ef05647535435d09b62945d16c2b759af15561a1e140bf4bc7e4` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (mirror bundle 11): RL A4 without the ECL gap rule, old vs new, in PROD.

The old output (``crx_rl_a4_deterioration``) still carries ``ecl_gap_blind_spot_flag``
until step 8 rewrites it. Log blocks, aggregates only, latest observation month:

* ``B11 OUTPUT``: states old × new, and new states by ``loan_type``.
* ``B11 ECL``: the accounts the rule flagged, by ``loan_type`` and whether their history
  now starts before the old table's end (2025-12), then their new states.
* ``B11 CHAIN``: restructured accounts stitched or not, by ``loan_type``; match type,
  ambiguous links, months added, old × new on the stitched rows.
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
            "chain_stitched_flag",
            "chain_match_type",
            "chain_candidate_count",
            "chain_months_added",
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

    stitched = latest.filter(F.col("chain_stitched_flag") == 1)
    restructured = latest.filter(
        (F.col("chain_stitched_flag") == 1)
        | (F.col("restructure_blind_spot_flag") == 1)
    )
    months = stitched.agg(
        F.expr("percentile_approx(chain_months_added, array(0, 0.5, 1))").alias("q")
    ).first()["q"]
    _log(
        "CHAIN",
        model_id,
        [
            f"restructured {restructured.count()}, stitched {stitched.count()}",
            "loan_type x stitched x still blind",
            *_table(
                restructured,
                "loan_type",
                "chain_stitched_flag",
                "restructure_blind_spot_flag",
            ),
            "match_type",
            *_table(stitched, "chain_match_type"),
            f"ambiguous (candidate_count > 1) "
            f"{stitched.filter(F.col('chain_candidate_count') > 1).count()}",
            f"months added min / median / max {months}",
            "stitched: old x new",
            *_table(stitched, "old_state", "det_state"),
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
Clean up after mirror bundle 13_a4_rl_restructure_feature_flag.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths for model_id rl_60_180 and rl_180_plus from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`. Skip any that does not exist:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b11_check`
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b11_check`
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_dpd_sequences_b13_check`
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a4_deterioration_b13_check`
- Remove the temporary check (everything marked TEMPORARY for bundle 13):
  - conf/base/catalog/catalog_crx.yml: the two `*_b13_check` entries and their comments;
  - src/enbd_collections/pipeline_registry.py: the `crx_rl_a4_deterioration_b13_check` entry and its comment;
  - crx_persona/rl_a4_deterioration/pipeline.py: `create_b13_check_pipeline`, the `b13_check` import and the TEMPORARY docstring paragraph;
  - crx_persona/rl_a4_deterioration/__init__.py: `create_b13_check_pipeline`;
  - delete crx_persona/rl_a4_deterioration/b13_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b11\|b13" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/: rm -rf data/input/mirror_bundles
- Run `git status`, commit src/ and conf/ and push. Report what you removed and the hdfs commands the user still has to run in PROD.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
