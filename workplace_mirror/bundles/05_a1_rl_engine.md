# Mirror bundle 05 — A1 — RL ability on the shared engine (+ CC node() style)

apply_bundle version: 6 · built 2026-10-26 from `a46e2e2..00de82d` · source: 4 added, 8 replaced, 1 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/05_a1_rl_engine.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '05_a1_rl_engine.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/05_a1_rl_engine.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: RL ability on the shared engine (rl_a1_ability_v2) + temporary b05 check" && git push
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/05_a1_rl_engine.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Run everything for **`rl_60_180`**: set `model_id: rl_60_180` in
`conf/dev/globals_dev.yml` (persona dates unchanged, dev 2026-01 to 2026-08). Switch it
back to `cc_60_180` when you are done.

**Step 6.** Build `prm_casa_return_events` for the RL namespace (it is stored per
`model_id`, so the CC build does not cover RL):

```bash
kedro run --env=dev --pipeline=casa_primary
```

**Step 7.** Run the check pipeline (observation base + RL A1 into the temporary
`crx_rl_a1_ability_b05_check`, then the comparison with the waterfall):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b05_check
```

It reads the waterfall's existing output `crx_rl_a1_ability`. If it stops with
`PATH_NOT_FOUND` on that dataset, send the error back (the waterfall then has to run first).

Paste back the two blocks, each from `=== B05 … START ===` to `=== B05 … END ===`:
`B05 OUTPUT` (waterfall vs engine states, levels, EMI anchor coverage) and `B05 INCOME`
(what the `feature_retail_loans` salary adds). Aggregates only. Text is best; otherwise
one photo per block.

**Step 8.** Only after the B05 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_v2
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** RL A1 on the shared `a1_ability` engine, next to the RL
waterfall, plus a temporary check that compares the two in PROD.

- **New package `crx_persona/rl_a1_ability_v2/`** (pipeline `crx_rl_a1_ability_v2`, output
  `crx_rl_a1_ability_v2`): the same income, liquidity, distress and state logic as CC, on
  `crx_rl_obs_base` (month-end `rl_spine` rows in the persona months). Customer-level signals
  are read across the whole CIF, as for CC. States `high` / `moderate` / `low` / `unknown`,
  display `a1_state_label`.
- **RL anchor** (`build_rl_liquidity_anchor`): one EMI, `installment_due_amount` on the
  loan's `int_loan_master` snapshot in the observation month. Missing, stale or not positive
  → flat floors (AED 3,000 income, 3,000 CASA, 500 card payment).
- **Extra bureau salary for RL**: `build_income_signals` takes an optional
  `loan_features` (`feature_retail_loans`). `aecb_last_salary_credit_amount` of each loan's
  latest bureau pull counts as bureau salary in the pull month (`aecb_bureau_pull_date`),
  merged with the other sources (larger value per month). CC does not pass it. Pulls are
  rare today (most loans have one), so it seldom lands in the window.
- **Not in RL A1**: EMI payment behaviour (`int_loan_master.total_paid`, `emi_*_flag`,
  `feat_loan_emi`) — it belongs to credibility (A3). The waterfall's EMI-coverage arms go.
- **CC pipeline style**: every `node()` in `cc_a1_ability_v2/pipeline.py`,
  `obs_base/pipeline.py` and `casa/primary.py` now spells out `func=`, `inputs=`,
  `outputs=`, `name=`, `tags=` (tags on each node). No behaviour change. The bundle 03
  cleanup you already did at work is in the bundle's base-to-head diff too, so those files
  apply as `MERGED` or unchanged.
- **Check** (`b05_check.py`, pipeline `crx_rl_a1_ability_b05_check`): RL waterfall
  (`crx_rl_a1_ability`) vs the engine (`crx_rl_a1_ability_b05_check`) by account and month,
  plus what the `feature_retail_loans` salary adds. Removed by the cleanup prompt.
- The waterfall (`rl_a1_ability/`) stays until the check is reviewed; it is deleted with the
  CC v1 package in the CC finish bundle, which also drops the `_v2` names.

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
| replace | `src/enbd_collections/pipelines/casa/primary.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/b05_check.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/nodes.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b03_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `4c408dd15915e22fca7a712221e45fc8645944e3bc37552271136439a6d430a0` · base trailing newline: yes · new sha256 `e93ab51de9b47ecfdac5eb4d3ecfa64d926652586b377b326b2d9d5b63d003a5` · new trailing newline: yes

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

# ── A2 Locatability (T12, Node 4 promoted from T29 2026-10-22) ──────────────
# Inputs: cc_spine (model_id-scoped), crx_cc_departure_signature (T06),
#         crx_cc_spell_table (T03b), prm_digital_login_monthly,
#         dcore_prm_followup_outcomes, dcore_stg_scope_agreements,
#         params:model_id, prm_contract, prm_client, feat_demographics_cif
# Output: crx_cc_a2_locatability (ships the A2 persona axis)
#
# Grain: (account_id, observation_date) — obs-anchored, matches cc_spine.
# Location x reachability 2D axis (T29 design, promoted — see RESULTS.md
# 2026-10-22): location_state ∈ {Skip, In Country, Unknown}; reachability_state
# ∈ {Reachable, Non-Reachable, Unknown}; a2_state = "Deceased" or
# "<location_state> - <reachability_state>". deceased_flag_v2 (OR of DCORE/Way4/
# demographics corroboration, T34) drives the Deceased pre-guard. T12's original
# 7-state waterfall (deceased/non_cooperative/reachable/avoiding/skip/gone/unknown)
# is retired.

crx_cc_a2_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_base"
  save_args:
    mode: overwrite

crx_cc_a2_login_presence:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_login_presence"
  save_args:
    mode: overwrite

crx_cc_a2_contact_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_contact_signals"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── A1 Ability (T26) ────────────────────────────────────────────────────────
# Inputs: cc_spine (model_id-scoped), crx_cc_spell_table (T03b),
#         crx_cc_departure_signature (T06), prm_contract, prm_client,
#         feat_payroll_indicator (retail.feature_space),
#         feat_casa_eod_balance  (retail.feature_space),
#         wm_fea_salary_days_since_increment (WM),
#         wm_fea_casa_weekly_repeated_inflow (WM)
# Grain: (account_id, observation_date) — spine grain.
# a1_state ∈ {ability_high, ability_moderate, ability_limited, ability_unknown}
# All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.
# Group B sibling-repo columns are NULL where CIF bridge or schema guard fires.

# Node 1: spine-grain base with spell window + Group A departure signals
# Grain: (account_id, observation_date) — spine grain; spell cols NULL if no active spell
crx_cc_a1_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_base"
  save_args:
    mode: overwrite

# Node 2: CIF-resolved rows only — (account_id, observation_date, spell_id, t0, cif_id)
# Spine grain; only rows where CIF was resolved (inner filter on cif_id NOT NULL).
crx_cc_a1_cif_enriched:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cif_enriched"
  save_args:
    mode: overwrite

# Node 3: WM + retail.feature_space income signals (T0-anchored, spell grain after dedup)
# Columns: account_id, spell_id, salary_months_h2, casa_eod_bal_h2,
#          salary_amt_last, salary_change_pct (D5 internal), months_runway
crx_cc_a1_group_b_income:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_income"
  save_args:
    mode: overwrite

# Node 3r: obs-date-anchored income signals (spine grain — answers "what is income NOW?")
# Columns: account_id, observation_date, salary_months_h2, ..., months_runway
crx_cc_a1_group_b_income_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_income_recent"
  save_args:
    mode: overwrite

# Node 4: AECB bureau + WM recurring inflow signals (T0-anchored, spell grain after dedup)
# Columns: account_id, spell_id, recurring_inflow_amt_h2, recurring_inflow_cnt_h2,
#          bureau_salary_present_6m_flag, a1_new_salary_acct_flag, a1_offus_paying_flag
crx_cc_a1_group_b_bureau:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_bureau"
  save_args:
    mode: overwrite

# Node 4r: obs-date-anchored bureau + recurring signals (spine grain)
# Columns: account_id, observation_date, recurring_inflow_amt_h2, ..., a1_offus_paying_flag
crx_cc_a1_group_b_bureau_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_bureau_recent"
  save_args:
    mode: overwrite

# Node 5: Payment trajectory + utilisation + outstanding balance (spell-grain, no CIF)
# Columns: account_id, spell_id, pay_ratio_slope, pay_ratio_mean_h1, pay_ratio_mean_h2,
#          util_t0, util_slope, spend_cliff_flag, cc_total_outstanding
crx_cc_a1_group_c:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_c"
  save_args:
    mode: overwrite

# Node 5r: obs-date-anchored balance (spine grain — answers "what is outstanding NOW?")
# Columns: account_id, observation_date, cc_total_outstanding_recent
crx_cc_a1_group_c_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_c_recent"
  save_args:
    mode: overwrite

# Node 6: assembled A1 ability axis (shipped persona axis)
# Grain: (account_id, observation_date) — spine grain; joins T0-anchored signals via spell_id.
crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
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

# ── CC A1 ability (shared _a1 engine) ───────────────────────────────────────
# Evidence tables at (account_id, observation_date); the axis is crx_cc_a1_ability_v2
# until the v1 pipeline is removed. a1_state in {high, moderate, low, unknown};
# a1_state_label in {High, Moderate, Low, Unknown}.
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

crx_cc_a1_internal_returns:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_internal_returns"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 03 check): the bundle 02 A1 output (b01_check, the
# baseline) and the new month-end A1 output (b03_check), kept apart from
# crx_cc_a1_ability_v2 so the two can be compared. Remove both entries, the
# crx_cc_a1_ability_b03_check pipeline and their HDFS folders after the check.
crx_cc_a1_ability_b01_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check"
  save_args:
    mode: overwrite

crx_cc_a1_ability_b03_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b03_check"
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

# ── RL A1 Income-Ability Axis (RL-A1-1) ─────────────────────────────────────

# Node 0: T0-anchored payroll departure signals (Group A).
# Grain: (account_id, spell_id=1). payroll_stopped_flag, payroll_present_h2
# derived from feat_payroll_indicator with H1=[T0-6m, T0-3m), H2=[T0-3m, T0).
crx_rl_a1_group_a:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_a"
  save_args:
    mode: overwrite

# Node 2r: obs-date-anchored WM / retail.feature_space income signals (obs grain).
# CC enrichers called with anchor_col="observation_date", grain (account_id, observation_date).
# Columns renamed to *_recent in _assemble_rl_classify_inputs before joining.
crx_rl_a1_group_b_income_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_b_income_recent"
  save_args:
    mode: overwrite

# Node 3r: obs-date-anchored AECB bureau + WM recurring inflow signals (obs grain).
# CC enrichers called with anchor_col="observation_date", grain (account_id, observation_date).
# Columns renamed to *_recent in _assemble_rl_classify_inputs before joining.
crx_rl_a1_group_b_bureau_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_b_bureau_recent"
  save_args:
    mode: overwrite

# Node 4r: obs-date-anchored EMI coverage window from feature_retail_loans.
# PIT window: [observation_date - 3m, observation_date]. Schema-guarded.
# Grain: (account_id, observation_date, spell_id).
crx_rl_a1_group_c_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_c_recent"
  save_args:
    mode: overwrite

# Node 4b: static origination bureau signals (RL-A1-4). Grain: (account_id, spell_id).
# 16 _at_origination columns: AECB cross-bank bureau + DMS underwriting at origination.
# Consumed from feat_loan_application_risk (pre-encoded; deduplicated to one row/account).
crx_rl_a1_group_d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_d"
  save_args:
    mode: overwrite

# Node 5: shipped A1 ability axis. Grain: (account_id, observation_date).
# Schema: obs-date-anchored _recent columns only (T0 cols removed in RL-A1-5 cleanup).
# Group D _at_origination columns appended (RL-A1-4).
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
# Grain: (account_id, observation_date). Consumed by crx_rl_a2_locatability Node 1.
# travel_mcc_flag_h2/foreign_login_flag coalesced to 0; casa_inflow_stop_gap_d may be NULL.
crx_rl_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_departure_signature"
  save_args:
    mode: overwrite

# ── RL A2 Locatability Axis (RL-A2-1) ───────────────────────────────────────

# Node 1: spine + departure signals (from crx_rl_departure_signature).
# Grain: (account_id, observation_date). Left-join on (account_id, observation_date).
# Schema matches crx_cc_a2_base departure-trail columns.
crx_rl_a2_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_base"
  save_args:
    mode: overwrite

# Node 2: obs-date-anchored digital login presence.
# obs_month_end=True — RL observation dates are month-end.
# Schema matches crx_cc_a2_login_presence.
crx_rl_a2_login_presence:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_login_presence"
  save_args:
    mode: overwrite

# Node 3: DCORE contact signals (RL-D5 spine, 24m floor filter).
# Schema matches crx_cc_a2_contact_signals.
crx_rl_a2_contact_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_contact_signals"
  save_args:
    mode: overwrite

# Node 4: shipped A2 locatability axis. Grain: (account_id, observation_date).
# Location x reachability 2D axis (RL-A2-3 design, promoted 2026-10-22 — see
# RESULTS_RL.md): location_state ∈ {Skip, In Country, Unknown}; reachability_state
# ∈ {Reachable, Non-Reachable, Unknown}; a2_state = "Deceased" or
# "<location_state> - <reachability_state>". RL-A2-1's original 7-state waterfall
# is retired. Produced by build_a2_locatability (CC function imported directly —
# domain-agnostic); RL supplies no prm_contract/prm_client (no Way4 equivalent).
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

# ── A2 Locatability (T12, Node 4 promoted from T29 2026-10-22) ──────────────
# Inputs: cc_spine (model_id-scoped), crx_cc_departure_signature (T06),
#         crx_cc_spell_table (T03b), prm_digital_login_monthly,
#         dcore_prm_followup_outcomes, dcore_stg_scope_agreements,
#         params:model_id, prm_contract, prm_client, feat_demographics_cif
# Output: crx_cc_a2_locatability (ships the A2 persona axis)
#
# Grain: (account_id, observation_date) — obs-anchored, matches cc_spine.
# Location x reachability 2D axis (T29 design, promoted — see RESULTS.md
# 2026-10-22): location_state ∈ {Skip, In Country, Unknown}; reachability_state
# ∈ {Reachable, Non-Reachable, Unknown}; a2_state = "Deceased" or
# "<location_state> - <reachability_state>". deceased_flag_v2 (OR of DCORE/Way4/
# demographics corroboration, T34) drives the Deceased pre-guard. T12's original
# 7-state waterfall (deceased/non_cooperative/reachable/avoiding/skip/gone/unknown)
# is retired.

crx_cc_a2_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_base"
  save_args:
    mode: overwrite

crx_cc_a2_login_presence:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_login_presence"
  save_args:
    mode: overwrite

crx_cc_a2_contact_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_contact_signals"
  save_args:
    mode: overwrite

crx_cc_a2_locatability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

# ── A1 Ability (T26) ────────────────────────────────────────────────────────
# Inputs: cc_spine (model_id-scoped), crx_cc_spell_table (T03b),
#         crx_cc_departure_signature (T06), prm_contract, prm_client,
#         feat_payroll_indicator (retail.feature_space),
#         feat_casa_eod_balance  (retail.feature_space),
#         wm_fea_salary_days_since_increment (WM),
#         wm_fea_casa_weekly_repeated_inflow (WM)
# Grain: (account_id, observation_date) — spine grain.
# a1_state ∈ {ability_high, ability_moderate, ability_limited, ability_unknown}
# All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.
# Group B sibling-repo columns are NULL where CIF bridge or schema guard fires.

# Node 1: spine-grain base with spell window + Group A departure signals
# Grain: (account_id, observation_date) — spine grain; spell cols NULL if no active spell
crx_cc_a1_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_base"
  save_args:
    mode: overwrite

# Node 2: CIF-resolved rows only — (account_id, observation_date, spell_id, t0, cif_id)
# Spine grain; only rows where CIF was resolved (inner filter on cif_id NOT NULL).
crx_cc_a1_cif_enriched:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cif_enriched"
  save_args:
    mode: overwrite

# Node 3: WM + retail.feature_space income signals (T0-anchored, spell grain after dedup)
# Columns: account_id, spell_id, salary_months_h2, casa_eod_bal_h2,
#          salary_amt_last, salary_change_pct (D5 internal), months_runway
crx_cc_a1_group_b_income:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_income"
  save_args:
    mode: overwrite

# Node 3r: obs-date-anchored income signals (spine grain — answers "what is income NOW?")
# Columns: account_id, observation_date, salary_months_h2, ..., months_runway
crx_cc_a1_group_b_income_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_income_recent"
  save_args:
    mode: overwrite

# Node 4: AECB bureau + WM recurring inflow signals (T0-anchored, spell grain after dedup)
# Columns: account_id, spell_id, recurring_inflow_amt_h2, recurring_inflow_cnt_h2,
#          bureau_salary_present_6m_flag, a1_new_salary_acct_flag, a1_offus_paying_flag
crx_cc_a1_group_b_bureau:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_bureau"
  save_args:
    mode: overwrite

# Node 4r: obs-date-anchored bureau + recurring signals (spine grain)
# Columns: account_id, observation_date, recurring_inflow_amt_h2, ..., a1_offus_paying_flag
crx_cc_a1_group_b_bureau_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_b_bureau_recent"
  save_args:
    mode: overwrite

# Node 5: Payment trajectory + utilisation + outstanding balance (spell-grain, no CIF)
# Columns: account_id, spell_id, pay_ratio_slope, pay_ratio_mean_h1, pay_ratio_mean_h2,
#          util_t0, util_slope, spend_cliff_flag, cc_total_outstanding
crx_cc_a1_group_c:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_c"
  save_args:
    mode: overwrite

# Node 5r: obs-date-anchored balance (spine grain — answers "what is outstanding NOW?")
# Columns: account_id, observation_date, cc_total_outstanding_recent
crx_cc_a1_group_c_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_group_c_recent"
  save_args:
    mode: overwrite

# Node 6: assembled A1 ability axis (shipped persona axis)
# Grain: (account_id, observation_date) — spine grain; joins T0-anchored signals via spell_id.
crx_cc_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability"
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

# ── CC A1 ability (shared _a1 engine) ───────────────────────────────────────
# Evidence tables at (account_id, observation_date); the axis is crx_cc_a1_ability_v2
# until the v1 pipeline is removed. a1_state in {high, moderate, low, unknown};
# a1_state_label in {High, Moderate, Low, Unknown}.
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

crx_cc_a1_internal_returns:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_internal_returns"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_v2"
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

# ── RL A1 Income-Ability Axis (RL-A1-1) ─────────────────────────────────────

# Node 0: T0-anchored payroll departure signals (Group A).
# Grain: (account_id, spell_id=1). payroll_stopped_flag, payroll_present_h2
# derived from feat_payroll_indicator with H1=[T0-6m, T0-3m), H2=[T0-3m, T0).
crx_rl_a1_group_a:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_a"
  save_args:
    mode: overwrite

# Node 2r: obs-date-anchored WM / retail.feature_space income signals (obs grain).
# CC enrichers called with anchor_col="observation_date", grain (account_id, observation_date).
# Columns renamed to *_recent in _assemble_rl_classify_inputs before joining.
crx_rl_a1_group_b_income_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_b_income_recent"
  save_args:
    mode: overwrite

# Node 3r: obs-date-anchored AECB bureau + WM recurring inflow signals (obs grain).
# CC enrichers called with anchor_col="observation_date", grain (account_id, observation_date).
# Columns renamed to *_recent in _assemble_rl_classify_inputs before joining.
crx_rl_a1_group_b_bureau_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_b_bureau_recent"
  save_args:
    mode: overwrite

# Node 4r: obs-date-anchored EMI coverage window from feature_retail_loans.
# PIT window: [observation_date - 3m, observation_date]. Schema-guarded.
# Grain: (account_id, observation_date, spell_id).
crx_rl_a1_group_c_recent:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_c_recent"
  save_args:
    mode: overwrite

# Node 4b: static origination bureau signals (RL-A1-4). Grain: (account_id, spell_id).
# 16 _at_origination columns: AECB cross-bank bureau + DMS underwriting at origination.
# Consumed from feat_loan_application_risk (pre-encoded; deduplicated to one row/account).
crx_rl_a1_group_d:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_group_d"
  save_args:
    mode: overwrite

# Node 5: shipped A1 ability axis. Grain: (account_id, observation_date).
# Schema: obs-date-anchored _recent columns only (T0 cols removed in RL-A1-5 cleanup).
# Group D _at_origination columns appended (RL-A1-4).
crx_rl_a1_ability:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability"
  save_args:
    mode: overwrite

# ── RL A1 ability (shared _a1 engine) ───────────────────────────────────────
# Evidence tables at (account_id, observation_date); the axis is crx_rl_a1_ability_v2
# until the waterfall (crx_rl_a1_ability) is removed. a1_state in {high, moderate, low,
# unknown}; a1_state_label in {High, Moderate, Low, Unknown}.
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

crx_rl_a1_internal_returns:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_internal_returns"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 05 check): the engine's RL output, kept apart from
# crx_rl_a1_ability_v2 so it can be compared with the waterfall. Remove the entry, the
# crx_rl_a1_ability_b05_check pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b05_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b05_check"
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
# Grain: (account_id, observation_date). Consumed by crx_rl_a2_locatability Node 1.
# travel_mcc_flag_h2/foreign_login_flag coalesced to 0; casa_inflow_stop_gap_d may be NULL.
crx_rl_departure_signature:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_departure_signature"
  save_args:
    mode: overwrite

# ── RL A2 Locatability Axis (RL-A2-1) ───────────────────────────────────────

# Node 1: spine + departure signals (from crx_rl_departure_signature).
# Grain: (account_id, observation_date). Left-join on (account_id, observation_date).
# Schema matches crx_cc_a2_base departure-trail columns.
crx_rl_a2_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_base"
  save_args:
    mode: overwrite

# Node 2: obs-date-anchored digital login presence.
# obs_month_end=True — RL observation dates are month-end.
# Schema matches crx_cc_a2_login_presence.
crx_rl_a2_login_presence:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_login_presence"
  save_args:
    mode: overwrite

# Node 3: DCORE contact signals (RL-D5 spine, 24m floor filter).
# Schema matches crx_cc_a2_contact_signals.
crx_rl_a2_contact_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_contact_signals"
  save_args:
    mode: overwrite

# Node 4: shipped A2 locatability axis. Grain: (account_id, observation_date).
# Location x reachability 2D axis (RL-A2-3 design, promoted 2026-10-22 — see
# RESULTS_RL.md): location_state ∈ {Skip, In Country, Unknown}; reachability_state
# ∈ {Reachable, Non-Reachable, Unknown}; a2_state = "Deceased" or
# "<location_state> - <reachability_state>". RL-A2-1's original 7-state waterfall
# is retired. Produced by build_a2_locatability (CC function imported directly —
# domain-agnostic); RL supplies no prm_contract/prm_client (no Way4 equivalent).
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
action: replace · base sha256 `ac8a037aade83abe5b27a5ce00ce8079e3ba12f7e21c798eff081209591a8462` · base trailing newline: yes · new sha256 `9b449af9a6c1bad9bfd9b05c515fb6044db647c578c2ad9a70fa40b958796dfc` · new trailing newline: yes

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

from enbd_collections.pipelines.casa import primary as casa_prm

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
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability_v2 as crx_cc_a1_ability_v2,
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
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
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
        "crx_cc_a1_ability_v2": crx_cc_a1_ability_v2.create_pipeline(),
        # TEMPORARY (mirror bundle 03 check) — remove with its catalog entries
        "crx_cc_a1_ability_b03_check": crx_cc_a1_ability_v2.create_b03_check_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": crx_rl_a3_payment_credibility.create_pipeline(),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
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

from enbd_collections.pipelines.casa import primary as casa_prm

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
from enbd_collections.pipelines.crx_persona import (
    cc_a1_ability_v2 as crx_cc_a1_ability_v2,
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
    rl_a1_ability_v2 as crx_rl_a1_ability_v2,
)
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
        # -- CASA (domain) ---------------------------------------------------
        "casa_primary": casa_prm.create_pipeline(),
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
        "crx_cc_a1_ability_v2": crx_cc_a1_ability_v2.create_pipeline(),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        "crx_rl_a1_ability_v2": crx_rl_a1_ability_v2.create_pipeline(),
        # TEMPORARY (mirror bundle 05 check) — remove with its catalog entry
        "crx_rl_a1_ability_b05_check": crx_rl_a1_ability_v2.create_b05_check_pipeline(),
        "crx_rl_departure_signature": crx_rl_departure_signature.create_pipeline(),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": crx_rl_a3_payment_credibility.create_pipeline(),
        # -- Digital login (OMB) --------------------------------------------
        "digital_login": dl.create_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/casa/primary.py`
action: replace · base sha256 `c06be986a54a112cc7d5f98240f981fcd6ade9d167ea8df172652f8642edf33e` · base trailing newline: yes · new sha256 `cfb5b4eada961b8b329a82f81d65f25d9ac2a63c992a13f589acdadfb827a316` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CASA primary pipeline.

kedro run --pipeline=casa_primary   (per model_id)
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import build_return_events


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events from comp_financial_tran_repos_dly."""
    return Pipeline(
        [
            node(
                func=build_return_events,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:casa_primary.return_reasons",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.history_months",
                ],
                outputs="prm_casa_return_events",
                name="build_prm_casa_return_events",
            )
        ],
        tags=["casa", "primary"],
    )
`````

New:

`````python
"""CASA primary pipeline.

kedro run --pipeline=casa_primary   (per model_id)
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import build_return_events


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events from comp_financial_tran_repos_dly."""
    return Pipeline(
        [
            node(
                func=build_return_events,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:casa_primary.return_reasons",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.history_months",
                ],
                outputs="prm_casa_return_events",
                name="build_prm_casa_return_events",
                tags=["casa", "primary"],
            )
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `353db05af5db5a50e1172b596fec864884aa50e48a6d0b2ab35dd7c9de067b26` · base trailing newline: yes · new sha256 `d38a60ca022c59f837f5090fbb37c0ae9c53df9d59e691a21fef9e30fe68d35e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The detailed rule table (thresholds, decision
log) is the GRR workbook `A1_ability_20261022`; the code is `signals.py` (evidence) and
`classify.py` (levels and state). CC wraps it in `cc_a1_ability_v2` (the anchor).

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends** (CC: until `cc_spine` itself is month-end, the
  observation base moves each billing-date row to its month end). Only the persona months
  are scored, `crx_persona.persona_start_date` to `persona_end_date`; in PROD that is the
  latest inference month (the run on the 2nd scores the previous month end).
- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - Every count scales with it: **"2 of 3" at 60–180 is "3 of 6" at 180+**
    (`MIN_MONTHS`), and every "in the window" rule (card payment, distress, CASA activity)
    reads 6 months at 180+.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 and 3 of 6 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month.
  - CC 180+: none. RL: one EMI.
  - No anchor → the flat floors below apply on their own.

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — `wm_fea_salary_days_since_increment`, a weekly WM snapshot per CIF:
  - `week_number` = the snapshot date;
  - `ft_last_salary_amount` = the last salary credit WM detected;
  - `ft_days_since_salary_transaction` = how many days before the snapshot it came.
  - Credit date = snapshot date − days since; its month is the salary month. Several
    weekly snapshots see the same credit; they collapse to one value per month (a credit on
    30 July, seen by the 2, 9 and 16 August snapshots, lands in July).
- **Bureau salary** — `stg_aecb_salary_history`: `subj_salcr_hist_ref_mnth` (MMyyyy) and
  `subj_salcr_hist_tot_sal_amt`, linked to the CIF through `prm_bureau_cif_bridge`.

The result is `income_m1 … income_m6` (`… m12` at 180+); NULL = no salary that month from either source.

**Step 2: the level** (`income_level`).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **2 of 3:** each of `income_m1..m3` scores 1 if it is at or above the threshold (NULL
  scores 0); Stable needs a count ≥ 2 (`MIN_MONTHS`; 3 of 6 at 180+). Any two months — not necessarily
  consecutive.
- **Not weakening:** the m1–m3 average must be ≥ 75% of the m4–m6 average
  (`D_INC = 0.25`); months without salary count as 0 here. No salary in m4–m6 → nothing to
  compare, the check passes.
- **Stable** = 2 of 3 at or above the threshold **and** not weakening.
  **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | 5,000 | NULL | 4,500 | 5,000 each |

July and May qualify (count 2), but the 3-month average (5,000 + 0 + 4,500) / 3 = 3,167 is
below 75% of 5,000 = 3,750 → **Weak**, not Stable. The missing June pulls the average down.

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`, `… m12` at 180+) — `wm_fea_casa_eod_avg_balance`:
  current + savings average balance, taken as the 4-week average on the month's last weekly
  snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA outflow
  in m1–m3 (`wm_pri_labelled_transactions`) to a credit card the customer registered as a
  beneficiary (`raw_beneficiary_cards`, card numbers). It shows money paid to other banks'
  cards.

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3, **and** the m1–m3 average not
    more than 50% below the m4–m6 average (months without data are skipped here, not 0); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`):

- **Internal:** a returned cheque or a DDS (direct debit) reject/reversal on any of their
  CASA accounts — `prm_casa_return_events`, `reason_for_excluding` in
  `CHEQUE RETURNS`, `DDS Rejects/Reversal`. POS reversals (`RETURNS`) do not count. The
  debit and credit legs of one return count once.
- **Bureau:** `prm_bureau_alert_enriched` with `bounced_cheque_amount > 0`, dated by
  `extract_date` — the date the report was pulled, not the date of the bounce.

## 4. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `unknown` | 0 points, no distress **and** no CASA transaction in m1–m3 (`casa_active`, from `wm_fea_casa_cc_inflow_outflow`) — we see nothing, which is not evidence of no ability |
| `high` | 4 points, no distress |
| `moderate` | 2–3 points without distress, or 4 points with distress |
| `low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down (High →
Moderate, Moderate → Low).

## Known limits

- **Two salary credits in one month count once.** Each snapshot carries only the *last*
  salary and the month keeps the largest amount, not the sum: two credits a month (salary
  plus allowance, split payments) show as the larger one; two credits in the same week can
  hide the earlier.
- **Only what WM labels as salary counts.** Regular non-salary income (own business,
  rent, transfers from family) is invisible — about a third of customers ever show an
  internal salary, and about a third hold no CASA with us at all.
- **Bureau salary is sparse for now.** The GRR bureau salary feed is the planned fix; it
  enters through the same "larger of the two per month" rule.
- **Missing salary months count as 0 in the weakening check**, so one late or missed
  salary can turn Stable into Weak (see the example).
- **Bureau bounces are dated by the pull date.** A bounce repeated in later reports keeps
  the flag on; when the bounce really happened is under investigation.
- **Internal returns follow the persona start.** `prm_casa_return_events` keeps the 6
  months up to `crx_persona.persona_start_date`; after moving that date, rerun
  `casa_primary` first, or the A1 run stops (`build_internal_returns`).
`````

New:

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The detailed rule table (thresholds, decision
log) is the GRR workbook `A1_ability_20261022`; the code is `signals.py` (evidence) and
`classify.py` (levels and state). CC wraps it in `cc_a1_ability_v2`, RL in
`rl_a1_ability_v2`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends** (CC: until `cc_spine` itself is month-end, the
  observation base moves each billing-date row to its month end). Only the persona months
  are scored, `crx_persona.persona_start_date` to `persona_end_date`; in PROD that is the
  latest inference month (the run on the 2nd scores the previous month end).
- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - Every count scales with it: **"2 of 3" at 60–180 is "3 of 6" at 180+**
    (`MIN_MONTHS`), and every "in the window" rule (card payment, distress, CASA activity)
    reads 6 months at 180+.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 and 3 of 6 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month.
  - CC 180+: none. RL: one EMI — `installment_due_amount` on the observation month's
    `int_loan_master` snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — `wm_fea_salary_days_since_increment`, a weekly WM snapshot per CIF:
  - `week_number` = the snapshot date;
  - `ft_last_salary_amount` = the last salary credit WM detected;
  - `ft_days_since_salary_transaction` = how many days before the snapshot it came.
  - Credit date = snapshot date − days since; its month is the salary month. Several
    weekly snapshots see the same credit; they collapse to one value per month (a credit on
    30 July, seen by the 2, 9 and 16 August snapshots, lands in July).
- **Bureau salary** — `stg_aecb_salary_history`: `subj_salcr_hist_ref_mnth` (MMyyyy) and
  `subj_salcr_hist_tot_sal_amt`, linked to the CIF through `prm_bureau_cif_bridge`.
  RL also reads `feature_retail_loans`: `aecb_last_salary_credit_amount` of each loan's latest
  bureau pull, dated by the month of `aecb_bureau_pull_date`. Pulls are rare today (most
  loans have one), so it seldom falls in the window.

The result is `income_m1 … income_m6` (`… m12` at 180+); NULL = no salary that month from either source.

**Step 2: the level** (`income_level`).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **2 of 3:** each of `income_m1..m3` scores 1 if it is at or above the threshold (NULL
  scores 0); Stable needs a count ≥ 2 (`MIN_MONTHS`; 3 of 6 at 180+). Any two months — not necessarily
  consecutive.
- **Not weakening:** the m1–m3 average must be ≥ 75% of the m4–m6 average
  (`D_INC = 0.25`); months without salary count as 0 here. No salary in m4–m6 → nothing to
  compare, the check passes.
- **Stable** = 2 of 3 at or above the threshold **and** not weakening.
  **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | 5,000 | NULL | 4,500 | 5,000 each |

July and May qualify (count 2), but the 3-month average (5,000 + 0 + 4,500) / 3 = 3,167 is
below 75% of 5,000 = 3,750 → **Weak**, not Stable. The missing June pulls the average down.

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`, `… m12` at 180+) — `wm_fea_casa_eod_avg_balance`:
  current + savings average balance, taken as the 4-week average on the month's last weekly
  snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA outflow
  in m1–m3 (`wm_pri_labelled_transactions`) to a credit card the customer registered as a
  beneficiary (`raw_beneficiary_cards`, card numbers). It shows money paid to other banks'
  cards.

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3, **and** the m1–m3 average not
    more than 50% below the m4–m6 average (months without data are skipped here, not 0); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`):

- **Internal:** a returned cheque or a DDS (direct debit) reject/reversal on any of their
  CASA accounts — `prm_casa_return_events`, `reason_for_excluding` in
  `CHEQUE RETURNS`, `DDS Rejects/Reversal`. POS reversals (`RETURNS`) do not count. The
  debit and credit legs of one return count once.
- **Bureau:** `prm_bureau_alert_enriched` with `bounced_cheque_amount > 0`, dated by
  `extract_date` — the date the report was pulled, not the date of the bounce.

## 4. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `unknown` | 0 points, no distress **and** no CASA transaction in m1–m3 (`casa_active`, from `wm_fea_casa_cc_inflow_outflow`) — we see nothing, which is not evidence of no ability |
| `high` | 4 points, no distress |
| `moderate` | 2–3 points without distress, or 4 points with distress |
| `low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down (High →
Moderate, Moderate → Low).

## Known limits

- **Two salary credits in one month count once.** Each snapshot carries only the *last*
  salary and the month keeps the largest amount, not the sum: two credits a month (salary
  plus allowance, split payments) show as the larger one; two credits in the same week can
  hide the earlier.
- **Only what WM labels as salary counts.** Regular non-salary income (own business,
  rent, transfers from family) is invisible — about a third of customers ever show an
  internal salary, and about a third hold no CASA with us at all.
- **Bureau salary is sparse for now.** The GRR bureau salary feed is the planned fix; it
  enters through the same "larger of the two per month" rule.
- **Missing salary months count as 0 in the weakening check**, so one late or missed
  salary can turn Stable into Weak (see the example).
- **Bureau bounces are dated by the pull date.** A bounce repeated in later reports keeps
  the flag on; when the bounce really happened is under investigation.
- **Internal returns follow the persona start.** `prm_casa_return_events` keeps the 6
  months up to `crx_persona.persona_start_date`; after moving that date, rerun
  `casa_primary` first, or the A1 run stops (`build_internal_returns`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `6cd55f2f0cee8a72486eb8e4109e4bb4c0b54cec84118169dcf33dbeabe4e0dc` · base trailing newline: yes · new sha256 `5c91d96c1e42153abf0906c98bc92a09419e0f7919820e0bb84610f8596b44be` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders return the amounts the
classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the window (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the window.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account). Each
builder reads its sources from the earliest observation's first month on
(``lookback_floor``), so source history before it is never shuffled.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
    window_agg,
    window_months,
)

# reason_for_excluding values that count as distress. prm_casa_return_events also carries
# "RETURNS", which is POS reversals (checked in PROD, Sonnet v01).
DISTRESS_RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m{months}`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame, since: str) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots dated ``since`` on
    (an earlier snapshot cannot see a later credit).

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    This is the only internal salary source. ``feat_payroll_indicator`` is not used: it is
    stamped the month after the credit and flags a subset of these months.
    """
    require_columns(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    week = parse_yyyymmdd("week_number")
    credit_date = F.date_sub(
        week, F.col("ft_days_since_salary_transaction").cast("int")
    )
    return wm_salary.filter(week >= F.lit(since)).select(
        "cif_id",
        F.trunc(credit_date, "month").alias("month"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _bureau_salary(salary_hist: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Bureau-reported salary by month."""
    require_columns(
        salary_hist,
        [
            "subj_salcr_hist_hdr_file_id",
            "subj_salcr_hist_ref_mnth",
            "subj_salcr_hist_tot_sal_amt",
        ],
        "stg_aecb_salary_history",
    )
    require_columns(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    bridge = cif_bridge.select(
        F.col("bureau_file_id").alias("subj_salcr_hist_hdr_file_id"), "cif_id"
    ).distinct()
    return salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt").cast("double").alias("amount"),
    )


def build_income_signals(
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
    model_id: str,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    months = 2 * window_months(model_id)
    since = lookback_floor(obs, months)
    monthly = (
        _internal_salary(wm_salary, since)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .filter(F.col("month") >= F.lit(since))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(
        obs_base, [_by_month(obs, monthly, "amount", "income", months)]
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame, since: str) -> DataFrame:
    """CASA (current + savings) average balance per month from ``since`` on: the 4-week
    average at the month's last weekly snapshot."""
    require_columns(
        wm_casa_bal,
        ["cif_id", "week_number", _CASA_MONTH_COL],
        "wm_fea_casa_eod_avg_balance",
    )
    week = parse_yyyymmdd("week_number")
    last_in_month = F.max(
        F.struct(week.alias("w"), F.col(_CASA_MONTH_COL).cast("double").alias("v"))
    )
    return (
        wm_casa_bal.filter(week >= F.lit(since))
        .groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    months: int,
    since: str,
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the window.

    ``raw_beneficiary_cards`` is a live snapshot: a card registered after the
    observation date still counts (mild look-ahead, accepted).
    """
    require_columns(
        labelled_txn,
        [
            "cif_id",
            "in_out_flow",
            "product_category",
            "tran_date",
            "tran_amt",
            "transaction_acid",
        ],
        "wm_pri_labelled_transactions",
    )
    require_columns(
        beneficiary_cards,
        ["instrument_number", "instrument_type"],
        "raw_beneficiary_cards",
    )
    cards = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("transaction_acid"))
        .distinct()
    )
    src = (
        labelled_txn.filter(
            (F.col("tran_date") >= F.lit(since))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        aggs=[F.max("tran_amt").alias("ext_card_payment_max")],
        months=months,
    )


def _casa_activity(
    obs: DataFrame, wm_casa_flow: DataFrame, months: int, since: str
) -> DataFrame:
    """Any CASA credit or debit in the window."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    week = parse_yyyymmdd("week_number")
    src = wm_casa_flow.filter(week >= F.lit(since)).select(
        "cif_id",
        week.alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active")],
        months=months,
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}``, ``ext_card_payment_max``, ``casa_active``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)  # the balances' prior window reaches furthest
    return left_join_all(
        obs_base,
        [
            _by_month(
                obs, _casa_by_month(wm_casa_bal, since), "balance", "casa", 2 * w
            ),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards, w, since),
            _casa_activity(obs, wm_casa_flow, w, since),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    internal_returns: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the window,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``;
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    require_columns(
        bureau_alert,
        ["cif_id", "extract_date", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    events = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                "cif_id", F.to_date("return_date").alias("event_date")
            )
        )
    require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
    events = events.unionByName(
        internal_returns.select("cif_id", F.to_date("event_date").alias("event_date"))
    )
    hits = window_agg(
        obs,
        events.filter(F.col("event_date") >= F.lit(lookback_floor(obs, w))),
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=w,
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(
    obs_base: DataFrame, return_events: DataFrame, model_id: str
) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).

    Stops the run when the table starts after the earliest observation's window (both
    follow ``crx_persona.persona_start_date``; the table was built for an older one).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding", "event_month"],
        "prm_casa_return_events",
    )
    since = lookback_floor(obs_base, window_months(model_id))
    # partition column: Spark infers its folder values as dates, so compare ISO strings
    first = return_events.agg(F.min("event_month")).first()[0]
    if first is None or str(first) > since:
        raise ValueError(
            f"prm_casa_return_events starts at {first}, but the observations need returns "
            f"from {since}: rerun casa_primary after changing "
            "crx_persona.persona_start_date"
        )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    # since is a month start, so event_month >= since is tran_date >= since, and prunes
    return (
        return_events.filter(
            (F.col("event_month") >= F.lit(since))
            & F.col("reason_for_excluding").isin(*DISTRESS_RETURN_REASONS)
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
        .distinct()
    )
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders return the amounts the
classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the window (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the window.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account). Each
builder reads its sources from the earliest observation's first month on
(``lookback_floor``), so source history before it is never shuffled.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
    window_agg,
    window_months,
)

# reason_for_excluding values that count as distress. prm_casa_return_events also carries
# "RETURNS", which is POS reversals (checked in PROD, Sonnet v01).
DISTRESS_RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m{months}`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame, since: str) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots dated ``since`` on
    (an earlier snapshot cannot see a later credit).

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    This is the only internal salary source. ``feat_payroll_indicator`` is not used: it is
    stamped the month after the credit and flags a subset of these months.
    """
    require_columns(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    week = parse_yyyymmdd("week_number")
    credit_date = F.date_sub(
        week, F.col("ft_days_since_salary_transaction").cast("int")
    )
    return wm_salary.filter(week >= F.lit(since)).select(
        "cif_id",
        F.trunc(credit_date, "month").alias("month"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _bureau_salary(salary_hist: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Bureau-reported salary by month."""
    require_columns(
        salary_hist,
        [
            "subj_salcr_hist_hdr_file_id",
            "subj_salcr_hist_ref_mnth",
            "subj_salcr_hist_tot_sal_amt",
        ],
        "stg_aecb_salary_history",
    )
    require_columns(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    bridge = cif_bridge.select(
        F.col("bureau_file_id").alias("subj_salcr_hist_hdr_file_id"), "cif_id"
    ).distinct()
    return salary_hist.join(bridge, on="subj_salcr_hist_hdr_file_id").select(
        "cif_id",
        F.to_date("subj_salcr_hist_ref_mnth", "MMyyyy").alias("month"),
        F.col("subj_salcr_hist_tot_sal_amt").cast("double").alias("amount"),
    )


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window. It is an
    extra bureau source until the bureau salary history covers RL customers.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = (
        obs_base.filter(F.col("cif_id").isNotNull())
        .select("account_id", "cif_id")
        .distinct()
    )
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.trunc(F.to_date("aecb_bureau_pull_date"), "month").alias("month"),
            F.col("aecb_last_salary_credit_amount").cast("double").alias("amount"),
        )
        .filter(F.col("month").isNotNull() & F.col("amount").isNotNull())
        .join(cifs, on="account_id")
        .select("cif_id", "month", "amount")
    )


def build_income_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal credit and the bureau salary (NULL: no salary that month).

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    months = 2 * window_months(model_id)
    since = lookback_floor(obs, months)
    sources = _internal_salary(wm_salary, since).unionByName(
        _bureau_salary(salary_hist, bureau_cif_bridge)
    )
    if loan_features is not None:
        sources = sources.unionByName(_loan_bureau_salary(obs_base, loan_features))
    monthly = (
        sources.filter(F.col("month") >= F.lit(since))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(
        obs_base, [_by_month(obs, monthly, "amount", "income", months)]
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame, since: str) -> DataFrame:
    """CASA (current + savings) average balance per month from ``since`` on: the 4-week
    average at the month's last weekly snapshot."""
    require_columns(
        wm_casa_bal,
        ["cif_id", "week_number", _CASA_MONTH_COL],
        "wm_fea_casa_eod_avg_balance",
    )
    week = parse_yyyymmdd("week_number")
    last_in_month = F.max(
        F.struct(week.alias("w"), F.col(_CASA_MONTH_COL).cast("double").alias("v"))
    )
    return (
        wm_casa_bal.filter(week >= F.lit(since))
        .groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    months: int,
    since: str,
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the window.

    ``raw_beneficiary_cards`` is a live snapshot: a card registered after the
    observation date still counts (mild look-ahead, accepted).
    """
    require_columns(
        labelled_txn,
        [
            "cif_id",
            "in_out_flow",
            "product_category",
            "tran_date",
            "tran_amt",
            "transaction_acid",
        ],
        "wm_pri_labelled_transactions",
    )
    require_columns(
        beneficiary_cards,
        ["instrument_number", "instrument_type"],
        "raw_beneficiary_cards",
    )
    cards = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("transaction_acid"))
        .distinct()
    )
    src = (
        labelled_txn.filter(
            (F.col("tran_date") >= F.lit(since))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return window_agg(
        obs,
        src,
        date_col="tran_date",
        aggs=[F.max("tran_amt").alias("ext_card_payment_max")],
        months=months,
    )


def _casa_activity(
    obs: DataFrame, wm_casa_flow: DataFrame, months: int, since: str
) -> DataFrame:
    """Any CASA credit or debit in the window."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    week = parse_yyyymmdd("week_number")
    src = wm_casa_flow.filter(week >= F.lit(since)).select(
        "cif_id",
        week.alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active")],
        months=months,
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}``, ``ext_card_payment_max``, ``casa_active``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)  # the balances' prior window reaches furthest
    return left_join_all(
        obs_base,
        [
            _by_month(
                obs, _casa_by_month(wm_casa_bal, since), "balance", "casa", 2 * w
            ),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards, w, since),
            _casa_activity(obs, wm_casa_flow, w, since),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    internal_returns: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the window,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``;
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    w = window_months(model_id)
    require_columns(
        bureau_alert,
        ["cif_id", "extract_date", "bounced_cheque_amount"],
        "prm_bureau_alert_enriched",
    )
    events = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                "cif_id", F.to_date("return_date").alias("event_date")
            )
        )
    require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
    events = events.unionByName(
        internal_returns.select("cif_id", F.to_date("event_date").alias("event_date"))
    )
    hits = window_agg(
        obs,
        events.filter(F.col("event_date") >= F.lit(lookback_floor(obs, w))),
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=w,
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(
    obs_base: DataFrame, return_events: DataFrame, model_id: str
) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).

    Stops the run when the table starts after the earliest observation's window (both
    follow ``crx_persona.persona_start_date``; the table was built for an older one).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding", "event_month"],
        "prm_casa_return_events",
    )
    since = lookback_floor(obs_base, window_months(model_id))
    # partition column: Spark infers its folder values as dates, so compare ISO strings
    first = return_events.agg(F.min("event_month")).first()[0]
    if first is None or str(first) > since:
        raise ValueError(
            f"prm_casa_return_events starts at {first}, but the observations need returns "
            f"from {since}: rerun casa_primary after changing "
            "crx_persona.persona_start_date"
        )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    # since is a month start, so event_month >= since is tran_date >= since, and prunes
    return (
        return_events.filter(
            (F.col("event_month") >= F.lit(since))
            & F.col("reason_for_excluding").isin(*DISTRESS_RETURN_REASONS)
        )
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
        .distinct()
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py`
action: replace · base sha256 `9b14c0ca9d9b3d8f65ee8ad83e309c05637845a13cdd54c40fc885d8c6623dbd` · base trailing newline: yes · new sha256 `65c9988c7d9e81a1dfeba967bdfe4f03037ccf21b7749032026e46e7beafee42` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_b03_check_pipeline, create_pipeline

__all__ = ["create_b03_check_pipeline", "create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py`
action: replace · base sha256 `4d176ef1f833d5554c2704bf6b5bfd7013f3107f67508e0f27a49e2af05e390d` · base trailing newline: yes · new sha256 `b611a25947b8deaf41a538ac36f52dee3fd2e450a83d734ecb618d683bfe4001` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ────────────────────┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first.
prm_bureau_payment_order joins the distress node once it exists in PROD.

    kedro run --pipeline=crx_cc_a1_ability_v2

TEMPORARY (mirror bundle 03): ``create_b03_check_pipeline`` runs the same nodes but
writes the axis to the temporary dataset ``crx_cc_a1_ability_b03_check`` (the existing
``crx_cc_a1_ability_v2`` is not overwritten) and logs the old-vs-new comparison
(``b03_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from .b03_check import compare_a1_outputs, compare_income_rules
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,
) -> Pipeline:
    """The CC A1 axis: signal tables, the anchor and the state, written to ``output``."""
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                    "params:model_id",
                ],
                "crx_cc_a1_income_signals",
                name="build_crx_cc_a1_income_signals",
            ),
            node(
                build_liquidity_signals,
                [
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:model_id",
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_internal_returns,
                [_OBS, "prm_casa_return_events", "params:model_id"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
                    "model_id": "params:model_id",
                },
                "crx_cc_a1_distress_signals",
                name="build_crx_cc_a1_distress_signals",
            ),
            node(
                build_cc_liquidity_anchor,
                [_OBS, "prm_balance", "params:model_id"],
                "crx_cc_a1_liquidity_anchor",
                name="build_crx_cc_a1_liquidity_anchor",
            ),
            node(
                build_a1_ability,
                [
                    _OBS,
                    "crx_cc_a1_income_signals",
                    "crx_cc_a1_liquidity_signals",
                    "crx_cc_a1_distress_signals",
                    "crx_cc_a1_liquidity_anchor",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                output,
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )


def create_b03_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_cc_a1_ability_b03_check + the log-only comparison nodes.
    Remove with b03_check.py and the catalog entries."""
    return (
        create_cc_obs_pipeline()
        + create_pipeline(output="crx_cc_a1_ability_b03_check")
        + Pipeline(
            [
                node(
                    compare_a1_outputs,
                    [
                        "crx_cc_a1_ability_b01_check",
                        "crx_cc_a1_ability_b03_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b03",
                ),
                node(
                    compare_income_rules,
                    [
                        "crx_cc_a1_income_signals",
                        "crx_cc_a1_ability_b03_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b03_income",
                ),
            ],
            tags=["crx_persona"],
        )
    )
`````

New:

`````python
"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ────────────────────┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first.
prm_bureau_payment_order joins the distress node once it exists in PROD.

    kedro run --pipeline=crx_cc_a1_ability_v2
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,
) -> Pipeline:
    """The CC A1 axis: signal tables, the anchor and the state, written to ``output``."""
    tags = ["crx_persona", "crx", "a1", "ability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs=[
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                    "params:model_id",
                ],
                outputs="crx_cc_a1_income_signals",
                name="build_crx_cc_a1_income_signals",
                tags=tags,
            ),
            node(
                func=build_liquidity_signals,
                inputs=[
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:model_id",
                ],
                outputs="crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
                tags=tags,
            ),
            node(
                func=build_internal_returns,
                inputs=[_OBS, "prm_casa_return_events", "params:model_id"],
                outputs="crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
                tags=tags,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
                    "model_id": "params:model_id",
                },
                outputs="crx_cc_a1_distress_signals",
                name="build_crx_cc_a1_distress_signals",
                tags=tags,
            ),
            node(
                func=build_cc_liquidity_anchor,
                inputs=[_OBS, "prm_balance", "params:model_id"],
                outputs="crx_cc_a1_liquidity_anchor",
                name="build_crx_cc_a1_liquidity_anchor",
                tags=tags,
            ),
            node(
                func=build_a1_ability,
                inputs=[
                    _OBS,
                    "crx_cc_a1_income_signals",
                    "crx_cc_a1_liquidity_signals",
                    "crx_cc_a1_distress_signals",
                    "crx_cc_a1_liquidity_anchor",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs=output,
                name="build_crx_cc_a1_ability",
                tags=tags,
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py`
action: replace · base sha256 `f2cf859bf862b6bc539557adb22a3f1a646686fd7d6c7fcebf5da3725e358cd0` · base trailing newline: yes · new sha256 `ad37f337f49bf07fa13842a86066cb8620521070c89dd09f8572c9d16692236c` · new trailing newline: yes

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
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
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
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/__init__.py`
action: add · new sha256 `84f71dbb70ba3bfb15b9c1865aab1cefe578a02d286eed98c1054c66de230288` · new trailing newline: yes

New:

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b05_check_pipeline, create_pipeline

__all__ = ["create_b05_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/b05_check.py`
action: add · new sha256 `bd8eda6ef86412eac37b6fda220b1f923aa2a47e4c75d25158cb41e16ede99e8` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 05): RL waterfall vs RL A1 on the engine, run in PROD.

Two log blocks, aggregates only:

* ``compare_rl_a1_outputs`` (``B05 OUTPUT``): the RL waterfall output (``crx_rl_a1_ability``)
  against the engine output (``crx_rl_a1_ability_b05_check``), over the engine output's
  months (the persona months). An old row is matched to the new row of the same account
  and month (the month's latest old observation).
* ``compare_income_sources`` (``B05 INCOME``): what the ``feature_retail_loans`` bureau
  salary adds — income levels and states with and without it.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, window_months
from ..a1_ability import build_income_signals
from ..a1_ability.classify import _LADDER, income_level
from ..a1_ability.signals import _loan_bureau_salary
from ..scoring_engine import points_from_level

LOG = logging.getLogger(__name__)


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B05 {name} START ===", *lines, f"=== B05 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def compare_rl_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state crosstab, new levels, the anchor's coverage and the latest
    month's state distribution."""
    first, last = new.agg(F.min("observation_date"), F.max("observation_date")).first()
    latest_in_month = Window.partitionBy("account_id", "month").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.withColumn("month", F.trunc("observation_date", "month"))
        .filter(F.col("month").between(F.trunc(F.lit(first), "month"), F.lit(last)))
        .withColumn("_rn", F.row_number().over(latest_in_month))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string").alias("account_id"),
            "month",
            # waterfall names: ability_high … ability_unknown
            F.regexp_replace("a1_state", "^ability_", "").alias("old_state"),
        )
    )
    both = (
        new.withColumn("month", F.trunc("observation_date", "month"))
        .select(
            "account_id",
            "month",
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
            F.col("liquidity_anchor_amt").isNotNull().alias("has_anchor"),
        )
        .join(old_m, ["account_id", "month"], "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    latest = new.filter(F.col("observation_date") == F.lit(last))
    anchor_q = new.agg(
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))")
    ).first()[0]
    lines = [
        (
            f"model_id={model_id} months {first}..{last} rows={n} changed={changed} "
            f"({100.0 * changed / max(n, 1):.2f}%)"
        ),
        f"  distress flag: {_counts(both, 'a1_distress_flag')}",
        f"  EMI anchor present: {_counts(both, 'has_anchor')}  p10/p50/p90: {anchor_q}",
        f"  latest month {last}: {_counts(latest, 'a1_state')}",
        "  income level x liquidity level:",
        *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
        "  old state x new state:",
        *_crosstab(both, "old_state", "new_state"),
    ]
    _log("OUTPUT", lines)
    both.unpersist()


def _state(income_col: str) -> Column:
    """The A1 state with ``income_col`` in place of the engine's income level (the
    unknown gate only holds while the points stay 0)."""
    points = points_from_level(
        F.col(income_col), {"stable": 2, "weak": 1}
    ) + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    unknown = (F.col("a1_state") == _LADDER.unknown) & (points == 0)
    return _LADDER.state(points, F.col("a1_distress_flag") == 1, unknown)


def compare_income_sources(  # pylint: disable=too-many-arguments
    *,
    obs_base: DataFrame,
    wm_salary: DataFrame,
    salary_hist: DataFrame,
    bureau_cif_bridge: DataFrame,
    loan_features: DataFrame,
    a1: DataFrame,
    model_id: str,
) -> None:
    """How often the loan bureau salary lands in the window, and the income levels and
    states without it."""
    w = window_months(model_id)
    without = build_income_signals(
        obs_base, wm_salary, salary_hist, bureau_cif_bridge, model_id
    )
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    df = (
        a1.join(without, list(GRAIN))
        .withColumn("lvl_without", income_level(anchor, w))
        .withColumn("st_without", _state("lvl_without"))
        .cache()
    )
    pulls = _loan_bureau_salary(obs_base, loan_features)
    in_window = (
        obs_base.select(*GRAIN, "cif_id")
        .join(pulls, "cif_id")
        .filter(
            (F.col("month") <= F.col("observation_date"))
            & (
                F.col("month")
                >= F.add_months(F.trunc("observation_date", "month"), 1 - w)
            )
        )
        .select(*GRAIN)
        .distinct()
        .count()
    )
    lines = [
        (
            f"model_id={model_id} rows={df.count()} rows with a loan bureau salary in "
            f"the {w}-month window: {in_window}"
        ),
        "  -- without feature_retail_loans: income level engine x variant",
        *_crosstab(df, "a1_income_level", "lvl_without"),
        "  -- without feature_retail_loans: state engine x variant",
        *_crosstab(df, "a1_state", "st_without"),
    ]
    _log("INCOME", lines)
    df.unpersist()
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/nodes.py`
action: add · new sha256 `af87ae0a282a508d5dd43f11928eeda3286fb5769d00fd2659aa745951f751a7` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/pipeline.py`
action: add · new sha256 `a5a8414463e1ac15dcced0da19191eaf029caeeea666182a9b786a60ba83bd8a` · new trailing newline: yes

New:

`````python
"""Kedro pipeline: RL A1 ability axis.

    crx_rl_obs_base ─┬─ income signals ──────────────────────┐
                     ├─ liquidity signals ───────────────────┤
                     ├─ internal returns ─► distress signals ┼─► crx_rl_a1_ability_v2
                     └─ liquidity anchor (EMI) ──────────────┘

Needs crx_rl_obs_base (``kedro run --pipeline=crx_rl_obs_base``) and
prm_casa_return_events for the RL model_id (``kedro run --pipeline=casa_primary``) first.

    kedro run --pipeline=crx_rl_a1_ability_v2

TEMPORARY (mirror bundle 05): ``create_b05_check_pipeline`` runs the same nodes but
writes the axis to ``crx_rl_a1_ability_b05_check`` and logs the comparison with the RL
waterfall (``b05_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b05_check import compare_income_sources, compare_rl_a1_outputs
from .nodes import build_rl_liquidity_anchor

_OBS = "crx_rl_obs_base"


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a1_ability_v2",
    **kwargs,
) -> Pipeline:
    """The RL A1 axis: signal tables, the EMI anchor and the state, written to
    ``output``."""
    tags = ["crx_persona", "crx", "a1", "ability", "persona_axis"]
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": _OBS,
                    "wm_salary": "wm_fea_salary_days_since_increment",
                    "salary_hist": "stg_aecb_salary_history",
                    "bureau_cif_bridge": "prm_bureau_cif_bridge",
                    "model_id": "params:model_id",
                    "loan_features": "feature_retail_loans",
                },
                outputs="crx_rl_a1_income_signals",
                name="build_crx_rl_a1_income_signals",
                tags=tags,
            ),
            node(
                func=build_liquidity_signals,
                inputs=[
                    _OBS,
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:model_id",
                ],
                outputs="crx_rl_a1_liquidity_signals",
                name="build_crx_rl_a1_liquidity_signals",
                tags=tags,
            ),
            node(
                func=build_internal_returns,
                inputs=[_OBS, "prm_casa_return_events", "params:model_id"],
                outputs="crx_rl_a1_internal_returns",
                name="build_crx_rl_a1_internal_returns",
                tags=tags,
            ),
            node(
                func=build_distress_signals,
                inputs={
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_rl_a1_internal_returns",
                    "model_id": "params:model_id",
                },
                outputs="crx_rl_a1_distress_signals",
                name="build_crx_rl_a1_distress_signals",
                tags=tags,
            ),
            node(
                func=build_rl_liquidity_anchor,
                inputs=[_OBS, "int_loan_master"],
                outputs="crx_rl_a1_liquidity_anchor",
                name="build_crx_rl_a1_liquidity_anchor",
                tags=tags,
            ),
            node(
                func=build_a1_ability,
                inputs=[
                    _OBS,
                    "crx_rl_a1_income_signals",
                    "crx_rl_a1_liquidity_signals",
                    "crx_rl_a1_distress_signals",
                    "crx_rl_a1_liquidity_anchor",
                    "params:model_id",
                    "params:crx_persona.persona_end_date",
                ],
                outputs=output,
                name="build_crx_rl_a1_ability",
                tags=tags,
            ),
        ],
    )


def create_b05_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the RL A1 pipeline writing to
    crx_rl_a1_ability_b05_check + the log-only comparison nodes.
    Remove with b05_check.py and the catalog entry."""
    tags = ["crx_persona"]
    return (
        create_rl_obs_pipeline()
        + create_pipeline(output="crx_rl_a1_ability_b05_check")
        + Pipeline(
            [
                node(
                    func=compare_rl_a1_outputs,
                    inputs=[
                        "crx_rl_a1_ability",
                        "crx_rl_a1_ability_b05_check",
                        "params:model_id",
                    ],
                    outputs=None,
                    name="compare_crx_rl_a1_b05",
                    tags=tags,
                ),
                node(
                    func=compare_income_sources,
                    inputs={
                        "obs_base": _OBS,
                        "wm_salary": "wm_fea_salary_days_since_increment",
                        "salary_hist": "stg_aecb_salary_history",
                        "bureau_cif_bridge": "prm_bureau_cif_bridge",
                        "loan_features": "feature_retail_loans",
                        "a1": "crx_rl_a1_ability_b05_check",
                        "model_id": "params:model_id",
                    },
                    outputs=None,
                    name="compare_crx_rl_a1_b05_income",
                    tags=tags,
                ),
            ],
        )
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b03_check.py`
action: delete · base sha256 `0c8d7a9e26f341c9e6c871be3bf9254f261a128c434f1be26195c78027f460aa` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (mirror bundle 03): old vs new CC A1 states, run in PROD.

Two log blocks, aggregates only:

* ``compare_a1_outputs`` (``B03 OUTPUT``): the bundle 02 engine output
  (``crx_cc_a1_ability_b01_check``, billing-date observations) against the new month-end
  output (``crx_cc_a1_ability_b03_check``), over the new output's months (the persona
  months). An old row is matched to the new row of the same account and month (the
  month's latest old observation).
* ``compare_income_rules`` (``B03 INCOME``): what the 2 × anchor income bar and the
  income-weakening check do, against a flat AED 3,000 floor and no weakening check.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from .._common import window_months
from ..a1_ability.classify import (
    _LADDER,
    D_INC,
    DEMIN,
    F_INC,
    K_INC,
    MIN_MONTHS,
    _count_at_least,
    _months,
    _not_weakening,
    _window,
)
from ..scoring_engine import points_from_level

LOG = logging.getLogger(__name__)


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state crosstab, new levels and the latest month's state distribution."""
    first, last = new.agg(F.min("observation_date"), F.max("observation_date")).first()
    latest_in_month = Window.partitionBy("account_id", "month").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.withColumn("month", F.trunc("observation_date", "month"))
        .filter(F.col("month").between(F.trunc(F.lit(first), "month"), F.lit(last)))
        .withColumn("_rn", F.row_number().over(latest_in_month))
        .filter(F.col("_rn") == 1)
        .select(
            "account_id",
            "month",
            # bundle 02 names: ability_high … ability_unknown
            F.regexp_replace("a1_state", "^ability_", "").alias("old_state"),
        )
    )
    both = (
        new.withColumn("month", F.trunc("observation_date", "month"))
        .select(
            "account_id",
            "month",
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
        )
        .join(old_m, ["account_id", "month"], "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    latest = new.filter(F.col("observation_date") == F.lit(last))
    lines = [
        f"model_id={model_id} months {first}..{last} rows={n} changed={changed} "
        f"({100.0 * changed / max(n, 1):.2f}%)",
        f"  distress flag: {_counts(both, 'a1_distress_flag')}",
        f"  latest month {last}: {_counts(latest, 'a1_state')}",
        "  income level x liquidity level:",
        *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
        "  old state x new state:",
        *_crosstab(both, "old_state", "new_state"),
    ]
    _log("OUTPUT", lines)
    both.unpersist()


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B03 {name} START ===", *lines, f"=== B03 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def _income_level(floor: Column, weakening: bool, w: int) -> Column:
    """classify.income_level with the threshold and the weakening check as inputs."""
    last = _months("income", _window(w)[0])
    stable = _count_at_least(last, floor) >= MIN_MONTHS[w]
    if weakening:
        stable = stable & _not_weakening("income", D_INC, True, w)
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _state(income_level: str) -> Column:
    """The A1 state with ``income_level`` in place of the engine's income level (the
    unknown gate only holds while the points stay 0)."""
    points = points_from_level(
        F.col(income_level), {"stable": 2, "weak": 1}
    ) + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    unknown = (F.col("a1_state") == _LADDER.unknown) & (points == 0)
    return _LADDER.state(points, F.col("a1_distress_flag") == 1, unknown)


def compare_income_rules(  # pylint: disable=too-many-locals
    income: DataFrame, a1: DataFrame, model_id: str
) -> None:
    """How often 2 × anchor raises the income bar above the flat floor, how often the
    weakening check fires, and the levels and states without each of them."""
    w = window_months(model_id)
    last = _window(w)[0]
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    income_bar = F.greatest(F.lit(F_INC), K_INC * anchor)
    flat = F.lit(F_INC)
    df = (
        a1.join(income, ["account_id", "observation_date"])
        .withColumn("bar", income_bar)
        .withColumn("raised", income_bar > flat)
        .withColumn("lvl_engine", _income_level(income_bar, True, w))
        .withColumn("lvl_flat", _income_level(flat, True, w))
        .withColumn("lvl_no_weak", _income_level(income_bar, False, w))
        .withColumn("lvl_flat_no_weak", _income_level(flat, False, w))
        .withColumn(
            "qual_bar",
            _count_at_least(_months("income", last), income_bar) >= MIN_MONTHS[w],
        )
        .withColumn(
            "qual_flat", _count_at_least(_months("income", last), flat) >= MIN_MONTHS[w]
        )
        .withColumn("weak_ok", _not_weakening("income", D_INC, True, w))
        .withColumn("st_flat", _state("lvl_flat"))
        .withColumn("st_no_weak", _state("lvl_no_weak"))
        .withColumn("st_flat_no_weak", _state("lvl_flat_no_weak"))
        .cache()
    )
    n = df.count()
    raised = (
        df.filter("raised")
        .agg(
            F.count("*").alias("n"),
            F.expr("percentile_approx(bar, array(0.5, 0.9, 0.99))").alias("q"),
        )
        .first()
    )
    mismatch = df.filter(F.col("lvl_engine") != F.col("a1_income_level")).count()
    lines = [
        f"model_id={model_id} rows={n} engine-level mismatches={mismatch} (must be 0)",
        f"  bar raised above {F_INC:.0f}: {raised['n']} ({100.0 * raised['n'] / max(n, 1):.2f}%)"
        f"  bar p50/p90/p99 where raised: {raised['q']}",
        f"  {MIN_MONTHS[w]} of {w} months reach the bar: {df.filter('qual_bar').count()}"
        f"  reach the flat floor: {df.filter('qual_flat').count()}",
        f"  {MIN_MONTHS[w]} of {w} reach the bar but weakening fails: "
        f"{df.filter(F.col('qual_bar') & ~F.col('weak_ok')).count()}"
        f"  (flat floor: {df.filter(F.col('qual_flat') & ~F.col('weak_ok')).count()})",
    ]
    for name, lvl, st in [
        ("flat floor", "lvl_flat", "st_flat"),
        ("no weakening check", "lvl_no_weak", "st_no_weak"),
        ("flat floor + no weakening check", "lvl_flat_no_weak", "st_flat_no_weak"),
    ]:
        lines += [
            f"  -- {name}: income level engine x variant",
            *_crosstab(df, "a1_income_level", lvl),
            f"  -- {name}: state engine x variant",
            *_crosstab(df, "a1_state", st),
        ]
    _log("INCOME", lines)
    df.unpersist()
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

APPLY_VERSION = 6
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
            else:
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
Clean up after mirror bundle 05_a1_rl_engine.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve the catalog path
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b05_check`
  for model_id rl_60_180 from the workplace conf, and write out the command in full,
  `hdfs dfs -rm -r <resolved path>`.
- Remove the temporary check (everything marked TEMPORARY for bundle 05):
  - conf/base/catalog/catalog_crx.yml: the `crx_rl_a1_ability_b05_check` entry and its
    TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_rl_a1_ability_b05_check"` entry and
    its comment;
  - crx_persona/rl_a1_ability_v2/pipeline.py: `create_b05_check_pipeline`, the imports of
    `create_rl_obs_pipeline` and `b05_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/rl_a1_ability_v2/__init__.py: the `create_b05_check_pipeline` export;
  - delete crx_persona/rl_a1_ability_v2/b05_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b05" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
