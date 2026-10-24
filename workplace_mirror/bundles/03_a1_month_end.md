# Mirror bundle 03 — CC A1 on month-end windows, prm_casa_return_events, distress fixes

apply_bundle version: 5 · built 2026-10-24 from `6b30cb2..8ecd486` · source: 8 added, 7 replaced, 1 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 7). Copy each command block
exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/03_a1_month_end.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script from the *Apply script* section at the bottom (prints `apply_bundle.py written`):

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '03_a1_month_end.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')"
```

**Step 4.** Apply — checks every file first, writes, compiles and imports; must end with `APPLY PASSED`:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/03_a1_month_end.md --apply
```

On a **CONFLICT**: stop and send the printed diff back.

**Step 5.** Look at what changed (nothing under `data/input/` shows up):

```bash
git status && git diff --stat
```

**Step 6.** `_common` helpers now take months instead of days. Check that no file outside
this bundle still calls them — this must print nothing (otherwise stop and send the output
back):

```bash
grep -rnE "max_age_days|window_agg\(|lookback_floor\(|pit_latest\(" src --include='*.py' | grep -vE "crx_persona/_common.py|crx_persona/a1_ability/|crx_persona/cc_a1_ability_v2/"
```

**Step 7.** Commit the source only, and push:

```bash
git add src conf && git commit -m "crx_persona A1: month-end windows, prm_casa_return_events, distress fixes (mirror bundle 03)" && git push
```

**Undo** (before step 7) — restores every touched file exactly:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/03_a1_month_end.md --revert
```

### In PROD

**Step 8.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Run everything for `cc_60_180` (the `model_id` in `conf/dev/globals_dev.yml`).

**Step 9.** First full build of `prm_casa_return_events` (scans the whole
`comp_financial_tran_repos_dly` once; later runs use the default `rebuild_days`):

```bash
kedro run --env=dev --pipeline=casa_primary --params=casa_primary.rebuild_days=4000
```

**Step 10.** Run the check pipeline (observation base + A1 into the temporary
`crx_cc_a1_ability_b03_check`, then the comparison):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the two blocks, each from `=== B03 … START ===` to `=== B03 … END ===`:
`B03 OUTPUT` (old vs new states) and `B03 INCOME` (the 2 × anchor income bar and the
income-weakening check: how often each fires and the levels / states without them).
Aggregates only, no customer rows. Text is best; otherwise one photo per block.

**Step 11.** Only after the B03 block has been reviewed: refresh the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_v2
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** CC A1 on month-end observation dates, the first primary dataset
under the data-layer rules, and the distress fixes from the PROD validation (Sonnet v01).

- **Month-end architecture.** Observation dates are month ends (CC like RL). The A1 windows
  are calendar months: "the last 3 months" = the observation month and the two before it,
  "the prior 3" = the three before those. `_common` works in months only (`window_agg`,
  `pit_latest(max_age_months)`, `lookback_floor`); the CC anchor needs a balance snapshot in
  the observation month. Until `cc_spine` is month-end, `build_cc_obs_base` moves each
  billing-date row to its month end (one row per account and month); any other
  non-month-end spine date stops the run.
- **New primary dataset `prm_casa_return_events`** (pipeline `casa_primary`, outside
  crx_persona): every returned CASA transaction (`CHEQUE RETURNS`, `DDS Rejects/Reversal`,
  `RETURNS`; both debit and credit legs) for all CIFs, one row per
  `tran_id + part_tran_srl_num + tran_date`, latest `edp_load_date` kept. Incremental: each
  run rebuilds the event months from (today − `rebuild_days`) and overwrites only those
  partitions. CC A1 reads it instead of `comp_financial_tran_repos_dly`.
- **Distress** = cheque returns + DDS rejects/reversals in the last 3 months; POS reversals
  (`RETURNS`) no longer count. Bureau bounces stay dated by `extract_date` (the pull date;
  the bounce date is under investigation).
- **Income**: the WM-recovered salary is the only internal salary source.
- **`a1_ability/README.md`**: the A1 logic in plain terms (sources, windows, the 2-of-3
  rules, the state ladder, known limits).
- **Check**: the bundle 01/02 check (`b01_check.py`) is replaced by `b03_check.py`, which
  compares the bundle 02 output (`crx_cc_a1_ability_b01_check`) with the new month-end output
  (`crx_cc_a1_ability_b03_check`), matching each account by month. It also logs how often
  the 2 × anchor income bar and the income-weakening check fire, and the income levels and
  states with a flat AED 3,000 floor and without the weakening check.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--apply` must print **APPLY PASSED**. On CONFLICT (other than an `--accept`ed
   file) the workplace file differs from the version this bundle was built from:
   stop and show the printed diff to the user.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. If an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| add | `conf/base/catalog/catalog_casa.yml` |
| replace | `conf/base/catalog/catalog_crx.yml` |
| add | `conf/base/parameters/parameters_casa.yml` |
| add | `src/enbd_collections/nodes/primary/casa/__init__.py` |
| add | `src/enbd_collections/nodes/primary/casa/prm_casa.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/casa/__init__.py` |
| add | `src/enbd_collections/pipelines/casa/primary.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/_common.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b03_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b01_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_casa.yml`
action: add · new sha256 `433e86b959b58cea4554b3e88567ebe835f5a84498336d24791d8d1ca8a57747` · new trailing newline: yes

New:

`````yaml
# CASA primary datasets (pipeline casa_primary).

# Returned CASA transactions, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
# Incremental: each run overwrites only the event_month partitions it rebuilt.
prm_casa_return_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/return_events"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
    partitionOverwriteMode: dynamic
  metadata:
    kedro-viz:
      layer: primary
`````

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `21ecdb9785c376dbe6a3f951fcc3dfb4ab468c4804b05e7f00d224ae5cf20835` · base trailing newline: yes · new sha256 `1dee6b155443227926bbb2eb1a9bc273293d1a4ca3f7ae52ec3ba4639e463a81` · new trailing newline: yes

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
# until the v1 pipeline is removed. a1_state in {ability_high, ability_moderate,
# ability_low, ability_unknown}.
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

# TEMPORARY (mirror bundle 01 check): the new A1 output, kept apart from
# crx_cc_a1_ability_v2 so the two can be compared. Remove this entry, the
# crx_cc_a1_ability_b01_check pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b01_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check"
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
# until the v1 pipeline is removed. a1_state in {ability_high, ability_moderate,
# ability_low, ability_unknown}.
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

### FILE: `conf/base/parameters/parameters_casa.yml`
action: add · new sha256 `6d45da2883c2ec53f2db05ca88ba34405dd690f724ea9e7130d26948bc0c7dce` · new trailing newline: yes

New:

`````yaml
##################################################
# CASA PRIMARY
##################################################
casa_primary:
  # reason_for_excluding values kept in prm_casa_return_events (all return types;
  # which ones count as distress is decided in the persona signal layer).
  return_reasons: ["CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS"]
  # Event months rebuilt per run: from the month start of (today - rebuild_days).
  # Covers late reloads; the first build overrides it with --params.
  rebuild_days: 45
`````

### FILE: `src/enbd_collections/nodes/primary/casa/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/nodes/primary/casa/prm_casa.py`
action: add · new sha256 `cd026c7627bc71b6ce5839e2823f35dcce33e9d2c031c8b723b4bc32f625fef9` · new trailing newline: yes

New:

`````python
"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_KEY = ["tran_id", "part_tran_srl_num", "tran_date"]
_RETURN_EVENT_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "reason_for_excluding",
    "tran_dc",
    "main_tran_type",
    "tran_type",
    "tran_sub_type",
    "channel_tran_type",
    "tran_particular_code",
    "tran_amt",
    "tran_amt_aed",
    "edp_load_date",
]


def build_return_events(
    tran_repos: DataFrame, return_reasons: Sequence[str], rebuild_days: int
) -> DataFrame:
    """Returned CASA transactions (every ``return_reasons`` value, both debit and credit
    legs) for all CIFs, one row per transaction key, partitioned by ``event_month``.

    Incremental: only event months from the month start of (today - ``rebuild_days``)
    are rebuilt, and the catalog overwrites just those partitions. A reload of the same
    transaction in a later ``edp_load_date`` keeps the latest load. The first build runs
    with a ``rebuild_days`` that covers the whole table.
    """
    missing = sorted(set(_RETURN_EVENT_COLUMNS) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    floor = (date.today() - timedelta(days=rebuild_days)).replace(day=1)
    latest_load = Window.partitionBy(*_KEY).orderBy(F.col("edp_load_date").desc())
    return (
        tran_repos.filter(
            (F.col("edp_load_date") >= F.lit(floor))
            & (F.col("tran_date") >= F.lit(floor))
            & F.col("reason_for_excluding").isin(*return_reasons)
        )
        .select(*_RETURN_EVENT_COLUMNS)
        .withColumn("_rn", F.row_number().over(latest_load))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
        .withColumn(
            "event_month", F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd")
        )
    )
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `ed6a35e31f0791cfa4988408196f4f0d513e56f07e352b71b752b88c034cc445` · base trailing newline: yes · new sha256 `ac8a037aade83abe5b27a5ce00ce8079e3ba12f7e21c798eff081209591a8462` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 01 check) — remove with its catalog entry
        "crx_cc_a1_ability_b01_check": crx_cc_a1_ability_v2.create_b01_check_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/casa/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/pipelines/casa/primary.py`
action: add · new sha256 `a1e790236ff3b8e5c829728aa28698899711011cb1f949a6ed780f5f676e3b45` · new trailing newline: yes

New:

`````python
"""CASA primary pipeline.

kedro run --pipeline=casa_primary
First build: kedro run --pipeline=casa_primary --params=casa_primary.rebuild_days=4000
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import build_return_events


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_return_events,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:casa_primary.return_reasons",
                    "params:casa_primary.rebuild_days",
                ],
                outputs="prm_casa_return_events",
                name="build_prm_casa_return_events",
            )
        ],
        tags=["casa", "primary"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: replace · base sha256 `c9b8cfc76650dba8cafa36b70691c924c3af5783ce4efa3b11628f3020656e91` · base trailing newline: yes · new sha256 `b9b017c7705b0ab24b74f7f41dff8a067a6b95618218df7701e61fdf918422e2` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Shared building blocks for the crx_persona axes.

Every axis works at the observation grain ``(account_id, observation_date)`` and looks
up customer-level sources by ``cif_id``. The helpers here encode the conventions once:

* missing source columns stop the run (``require_columns``);
* point-in-time lookups read strictly before the observation date and can be bounded in
  age (``pit_latest``), window aggregates read ``[start, observation_date)``
  (``window_agg``);
* source partition floors follow from the earliest observation date
  (``lookback_floor``);
* logging is opt-in and costs one job (``log_distribution``).
"""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F


LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


def _days_before(anchor: Column, days: int) -> Column:
    return F.date_sub(anchor, days)


def pit_latest(  # pylint: disable=too-many-arguments
    base: DataFrame,
    src: DataFrame,
    *,
    date_col: str,
    value_cols: Sequence[str],
    key: str = "cif_id",
    anchor: Column | None = None,
    max_age_days: int | None = None,
    inclusive: bool = False,
) -> DataFrame:
    """Latest ``src`` row dated before each base row's anchor, per ``GRAIN``.

    ``src`` must carry ``key``, ``date_col`` (a date) and ``value_cols``. The anchor
    defaults to ``observation_date``; ``inclusive`` also accepts rows dated on it (same-
    day snapshots). ``max_age_days`` drops rows older than that, so a stale record never
    stands in for a current one. Ties on the date are broken by the values (descending),
    so reruns agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
    """
    anchor = F.col("observation_date") if anchor is None else anchor
    before = (
        F.col("_d") <= F.col("_anchor") if inclusive else F.col("_d") < F.col("_anchor")
    )
    cond = before
    if max_age_days is not None:
        cond = cond & (F.col("_d") >= _days_before(F.col("_anchor"), max_age_days))
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
    days: int | None = None,
    months: int | None = None,
    key: str = "cif_id",
) -> DataFrame:
    """Aggregate ``src`` rows dated in a window ending before each observation date.

    ``days``: ``[obs - days, obs)``. ``months``: whole calendar months
    ``[trunc(obs) - months, trunc(obs))`` — for month-stamped series.
    ``src`` holds ``key``, ``date_col`` and the columns ``aggs`` read.
    Returns ``GRAIN + aggs`` for base rows with at least one row in the window.
    """
    if (days is None) == (months is None):
        raise ValueError("give exactly one of days / months")
    obs = F.col("observation_date")
    if days is not None:
        start, end = _days_before(obs, days), obs
    else:
        end = F.trunc(obs, "month")
        start = F.add_months(end, -months)
    return (
        base.select(*GRAIN, key)
        .join(src, on=key)
        .filter((F.col(date_col) >= start) & (F.col(date_col) < end))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


def lookback_floor(base: DataFrame, days: int) -> str:
    """ISO date ``days`` before the earliest observation date (partition floor)."""
    first: date = base.agg(F.min("observation_date")).first()[0]
    return (first - timedelta(days=days)).isoformat()


def left_join_all(base: DataFrame, parts: Sequence[DataFrame]) -> DataFrame:
    """Left-join every part onto ``base.select(*GRAIN)`` on ``GRAIN``."""
    result = base.select(*GRAIN)
    for part in parts:
        result = result.join(part, on=list(GRAIN), how="left")
    return result


def log_distribution(df: DataFrame, col: str, name: str, enabled: bool) -> None:
    """Log the value distribution of ``col`` (one job) when ``enabled``."""
    if not enabled:
        return
    rows = df.groupBy(col).count().orderBy(col).collect()
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s distribution (n=%d)", name, col, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str) -> DataFrame:
    """Every spine row with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    """
    return spine.select(
        F.col(id_col).cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))


def build_cc_obs_base(cc_spine: DataFrame) -> DataFrame:
    return _obs_base(cc_spine, "contract_id")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    return _obs_base(rl_spine, "account_id")
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
* logging is opt-in and costs one job (``log_distribution``).
"""

from __future__ import annotations

import logging
from datetime import date
from typing import Sequence

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F


LOG = logging.getLogger(__name__)

GRAIN = ("account_id", "observation_date")


def require_columns(df: DataFrame, columns: Sequence[str], source: str) -> None:
    """Raise if ``df`` lacks any of ``columns`` — a renamed source must fail the run."""
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"{source} is missing required columns {missing}")


def parse_yyyymmdd(col: str) -> Column:
    """``20260531`` (int or string) -> date."""
    return F.to_date(F.col(col).cast("string"), "yyyyMMdd")


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
    day snapshots). ``max_age_months`` keeps only rows in the anchor's last N calendar months
    (1 = its own month), so a stale record never stands in for a current one. Ties on the date are broken by the values (descending),
    so reruns agree. Returns ``GRAIN + value_cols`` for base rows with a match only.
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


def log_distribution(df: DataFrame, col: str, name: str, enabled: bool) -> None:
    """Log the value distribution of ``col`` (one job) when ``enabled``."""
    if not enabled:
        return
    rows = df.groupBy(col).count().orderBy(col).collect()
    total = sum(r["count"] for r in rows)
    LOG.info("%s — %s distribution (n=%d)", name, col, total)
    for r in rows:
        LOG.info(
            "  %-28s %9d  (%5.1f%%)",
            r[col],
            r["count"],
            100.0 * r["count"] / max(total, 1),
        )


# ── Observation base ──────────────────────────────────────────────────────────


def _obs_base(spine: DataFrame, id_col: str) -> DataFrame:
    """Every spine row with the ``cif_id`` the spine already carries.

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    Observation dates must be month ends; any other date stops the run.
    """
    base = spine.select(
        F.col(id_col).cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))
    mid_month = base.filter(F.col("observation_date") != F.last_day("observation_date"))
    if mid_month.limit(1).count():
        raise ValueError("spine observation dates must be month ends")
    return base


def build_cc_obs_base(cc_spine: DataFrame) -> DataFrame:
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
    return _obs_base(collapsed, "contract_id")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    return _obs_base(rl_spine, "account_id")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: add · new sha256 `613f23f3baaef38711908ab0dd374c8e2710daa63189cc2506e1727463b6de07` · new trailing newline: yes

New:

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`ability_high`, `ability_moderate`, `ability_low` or `ability_unknown`.

This page explains the logic in plain terms. The detailed rule table (thresholds, decision
log) is the GRR workbook `A1_ability_20261022`; the code is `signals.py` (evidence) and
`classify.py` (levels and state). CC wraps it in `cc_a1_ability_v2` (the anchor).

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends** (CC: until `cc_spine` itself is month-end, the
  observation base moves each billing-date row to its month end).
- **Windows are calendar months.** m1 = the observation month, m2 and m3 the two before it:
  "the last 3 months" = m1–m3. "The prior 3 months" = m4–m6 (used to spot a decline).
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

The result is `income_m1 … income_m6`; NULL = no salary that month from either source.

**Step 2: the level** (`income_level`).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **2 of 3:** each of `income_m1..m3` scores 1 if it is at or above the threshold (NULL
  scores 0); Stable needs a count ≥ 2 (`N3 = 2`). Any two months — not necessarily
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

- **CASA balance per month** (`casa_m1 … casa_m6`) — `wm_fea_casa_eod_avg_balance`:
  current + savings average balance, taken as the 4-week average on the month's last weekly
  snapshot.
- **External card payment** (`ext_card_payment_max_3m`) — the largest single CASA outflow
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
| `ability_unknown` | 0 points, no distress **and** no CASA transaction in m1–m3 (`casa_active_3m`, from `wm_fea_casa_cc_inflow_outflow`) — we see nothing, which is not evidence of no ability |
| `ability_high` | 4 points, no distress |
| `ability_moderate` | 2–3 points without distress, or 4 points with distress |
| `ability_low` | everything else: 0–1 points, or 2–3 points with distress |

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
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `971c756da1d085bda9efe3843620d86005d2beb9af2c403e5c66ae1947838880` · base trailing newline: yes · new sha256 `ae1107d8c7bc7f3ba43d3995459ea55882d3b79066978e873dc471c782c83d51` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

"The last 3 months" are the three complete calendar months before the observation month
(m1 = the month before, m2, m3); "the prior 3 months" are m4–m6. The builders return the
amounts the classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the last 3 months (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the last 3 months.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from typing import Sequence

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    parse_yyyymmdd,
    require_columns,
)

# reason_for_excluding values marking a returned cheque or DDS return (from a profiled
# sample of comp_financial_tran_repos_dly, not a code dictionary; checked in PROD).
RETURN_REASONS = ("CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS")
_CASA_MONTH_COL = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN_COL = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"


def _month_index(date: Column) -> Column:
    """1 for the month before the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int")


def _by_month(obs: DataFrame, series: DataFrame, value: str, prefix: str) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m6`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, 6))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, 7)
            ]
        )
    )


def _last_3_months(
    obs: DataFrame, src: DataFrame, date_col: str, aggs: Sequence[Column]
) -> DataFrame:
    """Aggregate ``src`` rows dated in the last 3 complete months, per observation."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(src, on="cif_id")
        .filter(_month_index(F.col(date_col)).between(1, 3))
        .groupBy(*GRAIN)
        .agg(*aggs)
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots.

    Each snapshot carries the last salary credited and how many days before the snapshot
    it was, so snapshot date minus that gap is the credit date. Several snapshots see
    the same credit; they collapse to one value per month.

    TODO(sonnet): validate against ``feat_payroll_indicator`` (payroll months without a
    recovered credit and vice versa), and switch to an internal table with salary credit
    amounts per month if one exists.
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
    credit_date = F.date_sub(
        parse_yyyymmdd("week_number"),
        F.col("ft_days_since_salary_transaction").cast("int"),
    )
    return wm_salary.select(
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
) -> DataFrame:
    """``income_m1 … income_m6``: salary received per month — the larger of the internal
    credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    monthly = (
        _internal_salary(wm_salary)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(obs_base, [_by_month(obs, monthly, "amount", "income")])


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame) -> DataFrame:
    """CASA (current + savings) average balance per month: the 4-week average at the
    month's last weekly snapshot."""
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
        wm_casa_bal.groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the last 3 months.

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
            (F.col("tran_date") >= F.lit(lookback_floor(obs, 100)))
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .select(
            "cif_id", F.col("tran_date").cast("date"), F.col("tran_amt").cast("double")
        )
    )
    return _last_3_months(
        obs, src, "tran_date", [F.max("tran_amt").alias("ext_card_payment_max_3m")]
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame) -> DataFrame:
    """Any CASA credit or debit in the last 3 months."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return _last_3_months(obs, src, "week", [F.max("_active").alias("casa_active_3m")])


def build_liquidity_signals(
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
) -> DataFrame:
    """``casa_m1 … casa_m6``, ``ext_card_payment_max_3m``, ``casa_active_3m``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _by_month(obs, _casa_by_month(wm_casa_bal), "balance", "casa"),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards),
            _casa_activity(obs, wm_casa_flow),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    payment_order: DataFrame | None = None,
    internal_returns: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the last 3 months,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques (always wired);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet;
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
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
    if internal_returns is not None:
        require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
        events = events.unionByName(
            internal_returns.select(
                "cif_id", F.to_date("event_date").alias("event_date")
            )
        )
    hits = _last_3_months(
        obs, events, "event_date", [F.max(F.lit(1)).alias("distress_flag")]
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(obs_base: DataFrame, casa_txn: DataFrame) -> DataFrame:
    """The bank's own returned cheques / DDS returns as ``(cif_id, event_date, reason)``,
    across all of the customer's CASA accounts.

    ``casa_txn`` is ``comp_financial_tran_repos_dly`` (2.4B rows): scoped to the
    observation base's CIFs before any other filter (R20), partitions pruned on
    ``edp_load_date``.
    """
    require_columns(
        casa_txn,
        ["cif_id", "edp_load_date", "tran_date", "reason_for_excluding"],
        "comp_financial_tran_repos_dly",
    )
    floor = F.lit(lookback_floor(obs_base, 100))
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    return (
        casa_txn.select("cif_id", "edp_load_date", "tran_date", "reason_for_excluding")
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .filter(
            (F.col("edp_load_date") >= floor)
            & (F.col("tran_date") >= floor)
            & F.col("reason_for_excluding").isin(*RETURN_REASONS)
        )
        .select(
            "cif_id",
            F.to_date("tran_date").alias("event_date"),
            F.col("reason_for_excluding").alias("reason"),
        )
    )
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. "The last 3 months" are the observation month and the
two before it (m1 = the observation month, m2, m3); "the prior 3 months" are m4–m6. The
builders return the amounts the classifier compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — any CASA transaction in the last 3 months (the Unknown gate);
* distress  — a cheque bounce or direct-debit return in the last 3 months.

Customer-level sources are always read for the whole CIF — all the customer's accounts —
never for the scored account_id alone (an RL account_id is not a CASA account).
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


def _by_month(obs: DataFrame, series: DataFrame, value: str, prefix: str) -> DataFrame:
    """Spread a ``(cif_id, month, value)`` series over ``{prefix}_m1 … _m6`` per
    observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", _month_index(F.col("month")))
        .filter(F.col("_k").between(1, 6))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, 7)
            ]
        )
    )


# ── Income ────────────────────────────────────────────────────────────────────


def _internal_salary(wm_salary: DataFrame) -> DataFrame:
    """Salary credits by month, recovered from the weekly WM snapshots.

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
    credit_date = F.date_sub(
        parse_yyyymmdd("week_number"),
        F.col("ft_days_since_salary_transaction").cast("int"),
    )
    return wm_salary.select(
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
) -> DataFrame:
    """``income_m1 … income_m6``: salary received per month — the larger of the internal
    credit and the bureau salary (NULL: no salary that month)."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    monthly = (
        _internal_salary(wm_salary)
        .unionByName(_bureau_salary(salary_hist, bureau_cif_bridge))
        .groupBy("cif_id", "month")
        .agg(F.max("amount").alias("amount"))
    )
    return left_join_all(obs_base, [_by_month(obs, monthly, "amount", "income")])


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_by_month(wm_casa_bal: DataFrame) -> DataFrame:
    """CASA (current + savings) average balance per month: the 4-week average at the
    month's last weekly snapshot."""
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
        wm_casa_bal.groupBy("cif_id", F.trunc(week, "month").alias("month"))
        .agg(last_in_month.alias("_last"))
        .select("cif_id", "month", F.col("_last.v").alias("balance"))
    )


def _ext_card_payments(
    obs: DataFrame, labelled_txn: DataFrame, beneficiary_cards: DataFrame
) -> DataFrame:
    """Largest single CASA payment to one of the customer's registered external credit
    cards in the last 3 months.

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
            (F.col("tran_date") >= F.lit(lookback_floor(obs, 3)))
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
        aggs=[F.max("tran_amt").alias("ext_card_payment_max_3m")],
        months=3,
    )


def _casa_activity(obs: DataFrame, wm_casa_flow: DataFrame) -> DataFrame:
    """Any CASA credit or debit in the last 3 months."""
    require_columns(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN_COL, _CASA_OUT_COL],
        "wm_fea_casa_cc_inflow_outflow",
    )
    src = wm_casa_flow.select(
        "cif_id",
        parse_yyyymmdd("week_number").alias("week"),
        ((F.col(_CASA_IN_COL) > 0) | (F.col(_CASA_OUT_COL) > 0))
        .cast("int")
        .alias("_active"),
    )
    return window_agg(
        obs,
        src,
        date_col="week",
        aggs=[F.max("_active").alias("casa_active_3m")],
        months=3,
    )


def build_liquidity_signals(
    obs_base: DataFrame,
    wm_casa_bal: DataFrame,
    wm_casa_flow: DataFrame,
    labelled_txn: DataFrame,
    beneficiary_cards: DataFrame,
) -> DataFrame:
    """``casa_m1 … casa_m6``, ``ext_card_payment_max_3m``, ``casa_active_3m``."""
    obs = obs_base.filter(F.col("cif_id").isNotNull())
    return left_join_all(
        obs_base,
        [
            _by_month(obs, _casa_by_month(wm_casa_bal), "balance", "casa"),
            _ext_card_payments(obs, labelled_txn, beneficiary_cards),
            _casa_activity(obs, wm_casa_flow),
        ],
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    bureau_alert: DataFrame,
    payment_order: DataFrame | None = None,
    internal_returns: DataFrame | None = None,
) -> DataFrame:
    """distress_flag: a cheque bounce or direct-debit (DDS) return in the last 3 months,
    from the bureau and from the bank's own records.

    * ``bureau_alert`` — bureau-reported bounced cheques, dated by ``extract_date``
      (the bureau pull date, not the bounce date: a bounce can repeat in later pulls);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet;
    * ``internal_returns`` — the bank's own returned cheques / DDS returns as
      ``(cif_id, event_date)`` from ``build_internal_returns``.
    """
    obs = obs_base.filter(F.col("cif_id").isNotNull())
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
    if internal_returns is not None:
        require_columns(internal_returns, ["cif_id", "event_date"], "internal_returns")
        events = events.unionByName(
            internal_returns.select(
                "cif_id", F.to_date("event_date").alias("event_date")
            )
        )
    hits = window_agg(
        obs,
        events,
        date_col="event_date",
        aggs=[F.max(F.lit(1)).alias("distress_flag")],
        months=3,
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["distress_flag"])


def build_internal_returns(obs_base: DataFrame, return_events: DataFrame) -> DataFrame:
    """The bank's own returned cheques and DDS returns for the observation base's CIFs, as
    distinct ``(cif_id, event_date, reason)`` from ``prm_casa_return_events`` (all of the
    customer's CASA accounts; the debit and credit legs of a return collapse to one row).
    """
    require_columns(
        return_events,
        ["cif_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    cifs = obs_base.select("cif_id").filter(F.col("cif_id").isNotNull()).distinct()
    return (
        return_events.filter(
            (F.col("tran_date") >= F.lit(lookback_floor(obs_base, 3)))
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
action: replace · base sha256 `035d30a72f168a15a2a1ab75ca59a3b3d571cd684a254fc9e728720dbe069fef` · base trailing newline: yes · new sha256 `9b14c0ca9d9b3d8f65ee8ad83e309c05637845a13cdd54c40fc885d8c6623dbd` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_b01_check_pipeline, create_pipeline

__all__ = ["create_b01_check_pipeline", "create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_b03_check_pipeline, create_pipeline

__all__ = ["create_b03_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b03_check.py`
action: add · new sha256 `1f0b63d16fe7760cd1ea4d5b0b0c9ff6e27826ab553d810c73071268c6dcf5d8` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 03): old vs new CC A1 states, run in PROD.

Two log blocks, aggregates only:

* ``compare_a1_outputs`` (``B03 OUTPUT``): the bundle 02 engine output
  (``crx_cc_a1_ability_b01_check``, billing-date observations) against the new month-end
  output (``crx_cc_a1_ability_b03_check``). An old row is matched to the new row of the
  same account and month (the month's latest old observation).
* ``compare_income_rules`` (``B03 INCOME``): what the 2 × anchor income bar and the
  income-weakening check do, against a flat AED 3,000 floor and no weakening check.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from ..a1_ability.classify import (
    _LADDER,
    _LAST3,
    D_INC,
    DEMIN,
    F_INC,
    K_INC,
    N3,
    _count_at_least,
    _months,
    _not_weakening,
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
    latest_in_month = Window.partitionBy("account_id", "month").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.withColumn("month", F.trunc("observation_date", "month"))
        .withColumn("_rn", F.row_number().over(latest_in_month))
        .filter(F.col("_rn") == 1)
        .select("account_id", "month", F.col("a1_state").alias("old_state"))
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
    last = new.agg(F.max("observation_date")).first()[0]
    latest = new.filter(F.col("observation_date") == F.lit(last))
    lines = [
        f"model_id={model_id} rows={n} changed={changed} "
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


def _income_level(floor: Column, weakening: bool) -> Column:
    """classify.income_level with the threshold and the weakening check as inputs."""
    last3 = _months("income", _LAST3)
    stable = _count_at_least(last3, floor) >= N3
    if weakening:
        stable = stable & _not_weakening("income", D_INC, True)
    weak = _count_at_least(last3, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _state(income_level: str) -> Column:
    """The A1 state with ``income_level`` in place of the engine's income level (the
    unknown gate only holds while the points stay 0)."""
    points = points_from_level(
        F.col(income_level), {"stable": 2, "weak": 1}
    ) + points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    unknown = (F.col("a1_state") == _LADDER.unknown) & (points == 0)
    return _LADDER.state(points, F.col("a1_distress_flag") == 1, unknown)


def compare_income_rules(income: DataFrame, a1: DataFrame, model_id: str) -> None:
    """How often 2 × anchor raises the income bar above the flat floor, how often the
    weakening check fires, and the levels and states without each of them."""
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    bar = F.greatest(F.lit(F_INC), K_INC * anchor)
    flat = F.lit(F_INC)
    df = (
        a1.join(income, ["account_id", "observation_date"])
        .withColumn("bar", bar)
        .withColumn("raised", bar > flat)
        .withColumn("lvl_engine", _income_level(bar, True))
        .withColumn("lvl_flat", _income_level(flat, True))
        .withColumn("lvl_no_weak", _income_level(bar, False))
        .withColumn("lvl_flat_no_weak", _income_level(flat, False))
        .withColumn("qual_bar", _count_at_least(_months("income", _LAST3), bar) >= N3)
        .withColumn("qual_flat", _count_at_least(_months("income", _LAST3), flat) >= N3)
        .withColumn("weak_ok", _not_weakening("income", D_INC, True))
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
        f"  2 of 3 months reach the bar: {df.filter('qual_bar').count()}"
        f"  reach the flat floor: {df.filter('qual_flat').count()}",
        f"  2 of 3 reach the bar but weakening fails: "
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py`
action: replace · base sha256 `5cb0d9f21a093685fc39936236a09c381eb18af5487326b1ae630b55d0a81036` · base trailing newline: yes · new sha256 `2c45eefef8f32b32cc09382327f477b255b33e508bad1508880d01b3a488061f` · new trailing newline: yes

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
# A balance snapshot older than this means the card stopped reporting; no anchor then.
_BALANCE_MAX_AGE_D = 31


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
        max_age_days=_BALANCE_MAX_AGE_D,
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py`
action: replace · base sha256 `f1fa725a5a187561deb0119512119d2f53f3aa7f3ac4574f0664b8e388447654` · base trailing newline: yes · new sha256 `e6df43db9dfcf19af5398b6300079a211b7bed4fcfe200694d9dcc35ec394fab` · new trailing newline: yes

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

TEMPORARY (mirror bundle 01): ``create_b01_check_pipeline`` runs the same nodes but
writes the axis to the temporary dataset ``crx_cc_a1_ability_b01_check`` (the existing
``crx_cc_a1_ability_v2`` is not overwritten) and logs the old-vs-new comparison
plus diagnostics on salary months, distress sources and levels (``b01_check.py``).
Removed by the bundle's cleanup.
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
from .b01_check import (
    compare_a1_outputs,
    compare_distress_sources,
    compare_salary_months,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,  # pylint: disable=unused-argument
) -> Pipeline:
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
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
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_internal_returns,
                [_OBS, "comp_financial_tran_repos_dly"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
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
                    "params:crx_log_stats",
                ],
                output,
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )


def create_b01_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_cc_a1_ability_b01_check + the log-only comparison nodes.
    Remove with b01_check.py and the catalog entry."""
    return (
        create_cc_obs_pipeline()
        + create_pipeline(output="crx_cc_a1_ability_b01_check")
        + Pipeline(
            [
                node(
                    compare_a1_outputs,
                    [
                        "crx_cc_a1_ability_v2",
                        "crx_cc_a1_ability_b01_check",
                        "params:model_id",
                    ],
                    None,
                    name="compare_crx_cc_a1_b01",
                ),
                node(
                    compare_salary_months,
                    [_OBS, "crx_cc_a1_income_signals", "feat_payroll_indicator"],
                    None,
                    name="compare_crx_cc_a1_b01_salary",
                ),
                node(
                    compare_distress_sources,
                    [
                        _OBS,
                        "prm_bureau_alert_enriched",
                        "crx_cc_a1_internal_returns",
                    ],
                    None,
                    name="compare_crx_cc_a1_b01_distress",
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


def create_pipeline(
    output: str = "crx_cc_a1_ability_v2",
    **kwargs,  # pylint: disable=unused-argument
) -> Pipeline:
    return Pipeline(
        [
            node(
                build_income_signals,
                [
                    _OBS,
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
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
                ],
                "crx_cc_a1_liquidity_signals",
                name="build_crx_cc_a1_liquidity_signals",
            ),
            node(
                build_internal_returns,
                [_OBS, "prm_casa_return_events"],
                "crx_cc_a1_internal_returns",
                name="build_crx_cc_a1_internal_returns",
            ),
            node(
                build_distress_signals,
                {
                    "obs_base": _OBS,
                    "bureau_alert": "prm_bureau_alert_enriched",
                    "internal_returns": "crx_cc_a1_internal_returns",
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
                    "params:crx_log_stats",
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/b01_check.py`
action: delete · base sha256 `abe80aa8d256b3fd723e51600d0f980fa9c99657ef748c9cbecae53e4c33e510` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (mirror bundle 01): checks for the CC A1 rebuild, run in PROD.

The last nodes of the ``crx_cc_a1_ability_b01_check`` pipeline (aggregates only):

* ``compare_a1_outputs`` — the untouched ``crx_cc_a1_ability_v2`` against the new
  ``crx_cc_a1_ability_b01_check``, plus income × liquidity levels; ``B01 OUTPUT`` block;
* ``compare_salary_months`` — salary months recovered from the WM snapshots against
  ``feat_payroll_indicator`` in the same month and one month either side; ``B01 SALARY``;
* ``compare_distress_sources`` — bureau vs internal returns, and each internal
  ``reason_for_excluding`` value; ``B01 DISTRESS`` block.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)
_GRAIN = ["account_id", "observation_date"]


def _counts(df: DataFrame, col: str) -> dict:
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def _crosstab(df: DataFrame, a: str, b: str) -> list[str]:
    rows = df.groupBy(a, b).count().orderBy(a, b).collect()
    return [f"  {r[a]!s:<18} x {r[b]!s:<18} {r['count']:>9}" for r in rows]


def _log(name: str, lines: list[str]) -> None:
    block = [f"=== B01 {name} START ===", *lines, f"=== B01 {name} END ==="]
    LOG.info("\n%s", "\n".join(block))


def _in_last_3_months(date_col: str) -> Column:
    k = F.months_between(
        F.trunc("observation_date", "month"), F.trunc(F.col(date_col), "month")
    )
    return k.between(1, 3)


def compare_a1_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new state, level distributions and crosstab, anchor coverage."""
    both = (
        new.select(
            *_GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
            "a1_distress_flag",
            "liquidity_anchor_amt",
        )
        .join(
            old.select(*_GRAIN, F.col("a1_state_v2").alias("old_state")), _GRAIN, "full"
        )
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    anchor = both.agg(
        F.avg(F.col("liquidity_anchor_amt").isNotNull().cast("double")).alias("share"),
        F.expr("percentile_approx(liquidity_anchor_amt, array(0.1, 0.5, 0.9))").alias(
            "q"
        ),
    ).first()
    _log(
        "OUTPUT",
        [
            f"model_id={model_id} rows={n} changed={changed} "
            f"({100.0 * changed / max(n, 1):.2f}%)",
            f"  distress flag: {_counts(both, 'a1_distress_flag')}",
            f"  anchor present: {anchor['share'] or 0.0:.4f}  p10/p50/p90: {anchor['q']}",
            "  income level x liquidity level:",
            *_crosstab(both, "a1_income_level", "a1_liquidity_level"),
            "  old state x new state:",
            *_crosstab(both, "old_state", "new_state"),
        ],
    )
    both.unpersist()


def compare_salary_months(
    obs_base: DataFrame, income: DataFrame, payroll: DataFrame
) -> None:
    """Recovered salary months (income_m1..m3 > 0) against payroll_flag in the same
    month, the month before and the month after."""
    month = lambda k: F.trunc(F.add_months("observation_date", -k), "month")  # noqa: E731
    credits = (
        income.join(obs_base.select(*_GRAIN, "cif_id"), _GRAIN)
        .filter(F.col("cif_id").isNotNull())
        .select(
            "cif_id",
            F.explode(
                F.array(
                    *[
                        F.struct(
                            month(k).alias("month"),
                            F.col(f"income_m{k}").alias("amount"),
                        )
                        for k in (1, 2, 3)
                    ]
                )
            ).alias("m"),
        )
        .select(
            "cif_id",
            "m.month",
            "m.amount",
            (F.coalesce(F.col("m.amount"), F.lit(0.0)) > 0).alias("recovered"),
        )
    )
    flags = (
        payroll.select(
            "cif_id",
            F.trunc(
                F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"), "month"
            ).alias("pmonth"),
            (F.col("payroll_flag") == 1).cast("int").alias("payroll"),
        )
        .groupBy("cif_id", "pmonth")
        .agg(F.max("payroll").alias("payroll"))
    )
    # payroll_prev: flag in the month before the credit month; payroll_next: the month after
    for shift, name in ((-1, "prev"), (0, "same"), (1, "next")):
        f = flags.select(
            "cif_id",
            F.add_months("pmonth", -shift).alias("month"),
            F.col("payroll").alias(f"payroll_{name}"),
        )
        credits = credits.join(f, ["cif_id", "month"], "left")
    credits = credits.fillna(
        0, ["payroll_prev", "payroll_same", "payroll_next"]
    ).cache()
    amounts = (
        credits.filter("recovered")
        .groupBy("payroll_same")
        .agg(
            F.expr("percentile_approx(amount, array(0.1, 0.5, 0.9))").alias("q"),
            F.avg((F.col("amount") >= 3000).cast("double")).alias("ge3000"),
        )
        .orderBy("payroll_same")
        .collect()
    )
    lines = []
    for name in ("same", "prev", "next"):
        lines += [f"  recovered x payroll flag ({name} month):"]
        lines += _crosstab(credits, "recovered", f"payroll_{name}")
    lines += ["  recovered credit amount by payroll flag (same month):"]
    lines += [
        f"  payroll={r['payroll_same']} p10/p50/p90={r['q']} "
        f"share>=3000={r['ge3000']:.3f}"
        for r in amounts
    ]
    _log("SALARY", lines)
    credits.unpersist()


def compare_distress_sources(
    obs_base: DataFrame, bureau_alert: DataFrame, internal_returns: DataFrame
) -> None:
    """Rows flagged by bureau bounces vs internal returns (last 3 complete months), and
    events / rows flagged per internal reason."""
    obs = obs_base.filter(F.col("cif_id").isNotNull()).select(*_GRAIN, "cif_id")
    bureau = bureau_alert.filter(F.col("bounced_cheque_amount") > 0).select(
        "cif_id", F.to_date("extract_date").alias("event_date")
    )
    internal = (
        obs.join(internal_returns, "cif_id")
        .filter(_in_last_3_months("event_date"))
        .cache()
    )
    hit = lambda df, name: (  # noqa: E731
        df.select(*_GRAIN).distinct().withColumn(name, F.lit(1))
    )
    flags = (
        obs.join(
            hit(
                obs.join(bureau, "cif_id").filter(_in_last_3_months("event_date")),
                "bureau",
            ),
            _GRAIN,
            "left",
        )
        .join(hit(internal, "internal"), _GRAIN, "left")
        .fillna(0, ["bureau", "internal"])
    )
    per_reason = (
        internal.groupBy("reason")
        .agg(
            F.count(F.lit(1)).alias("events"),
            F.countDistinct(*_GRAIN).alias("rows"),
        )
        .orderBy("reason")
        .collect()
    )
    lines = [f"  rows with a CIF: {obs.count()}", "  bureau x internal:"]
    lines += _crosstab(flags, "bureau", "internal")
    lines += ["  internal reason: events in window / rows flagged"]
    lines += [
        f"  {r['reason']:<24} {r['events']:>9} {r['rows']:>9}" for r in per_reason
    ]
    _log("DISTRESS", lines)
    internal.unpersist()
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

Safety rules:
  * every file the bundle replaces or deletes must be byte-identical (line endings aside) to
    the version the bundle was built from; otherwise nothing is written and the diff is
    printed. Someone else's edits are never overwritten.
  * refuses to write on main/master, or when a touched file has uncommitted changes.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
         --accept PATH (repeatable) replaces a conflicting file anyway — only after
         reading its code diff, and only for a file nobody edited by hand.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import os
import pathlib
import re
import subprocess
import sys

APPLY_VERSION = 5
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
    import ast

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
            import ast

            dump = lambda t: ast.dump(_strip_docstrings(ast.parse(t)))  # noqa: E731
            return dump(a) == dump(b)
        if path.endswith((".yml", ".yaml")):
            import yaml

            return yaml.safe_load(a) == yaml.safe_load(b)
    except Exception:  # pylint: disable=broad-except
        return False
    return False


def _is_new(current: str, e: dict) -> bool:
    """The repo file already holds the bundle's new version (comment noise aside)."""
    return _loose(current) == _loose(e["new"]) or _same_code(e["path"], current, e["new"])


def _code_text(path: str, text: str) -> str:
    """The text with comments and docstrings removed (Python) or normalised (YAML)."""
    try:
        if path.endswith(".py"):
            import ast

            return ast.unparse(_strip_docstrings(ast.parse(text)))
        if path.endswith((".yml", ".yaml")):
            import yaml

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


ACCEPTED: set[str] = set()  # paths given with --accept


def file_status(e: dict) -> str:
    """One of: todo, done, conflict, accepted."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    if e["action"] == "replace":
        if current is not None and _loose(current) == _loose(e["new"]):
            return "done"
        if current is not None and _loose(current) == _loose(e["base"]):
            return "todo"
        if current is not None and _same_code(e["path"], current, e["new"]):
            return "done"
        if _matches_base(current, e):
            return "todo"
        return "accepted" if e["path"] in ACCEPTED else "conflict"
    # delete
    if current is None:
        return "done"
    if _matches_base(current, e):
        return "todo"
    return "accepted" if e["path"] in ACCEPTED else "conflict"


def explain_conflict(e: dict) -> None:
    current = _read(pathlib.Path(e["path"]))
    print(f"\n--- CONFLICT: {e['path']} ({e['action']})")
    if e["action"] == "add":
        print("    the file already exists with different content; the bundle would add it.")
        expected, label = e["new"], "bundle (new)"
    else:
        expected, label = e["base"], "bundle base (as photographed)"
        if current is None:
            print("    the file does not exist in this repo.")
            return
    print("    The CODE differs (comments, docstrings, spacing are already ignored).")
    print("    Code-only diff — bundle's copy (-) vs this repo (+):")
    diff = list(
        difflib.unified_diff(
            _code_text(e["path"], expected).splitlines(),
            _code_text(e["path"], current or "").splitlines(),
            fromfile=label,
            tofile="this repo",
            lineterm="",
            n=1,
        )
    )
    for line in diff[:80]:
        print("    " + line)
    if len(diff) > 80:
        print(f"    ... {len(diff) - 80} more diff lines")


def _comment_only(e: dict) -> bool:
    current = _read(pathlib.Path(e["path"]))
    return (
        e["action"] in ("replace", "delete")
        and current is not None
        and _loose(current) != _loose(e["base"])
        and _matches_base(current, e)
    )


def print_table(entries: list[dict], statuses: list[str]) -> None:
    word = {
        "todo": "will apply",
        "done": "already applied",
        "conflict": "CONFLICT",
        "accepted": "CONFLICT, accepted (--accept): will apply",
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
    failures = []
    existing = [e for e in entries if e["action"] != "delete" and e["path"].endswith(".py")]
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
        )
        if r.returncode != 0:
            last = (r.stderr.strip().splitlines() or ["?"])[-1]
            failures.append(f"import: {mod}: {last}")
    return failures


def _prune_empty_dirs(folder: pathlib.Path) -> None:
    """Remove folders left with nothing but bytecode caches after a delete."""
    import shutil

    while folder != pathlib.Path(".") and folder.is_dir():
        rest = [p for p in folder.iterdir() if p.name != "__pycache__"]
        if rest:
            return
        shutil.rmtree(folder)
        folder = folder.parent


# ── Commands ─────────────────────────────────────────────────────────────────


def cmd_check(entries: list[dict], quiet: bool = False) -> bool:
    statuses = [file_status(e) for e in entries]
    problems = git_problems(entries)
    if not quiet:
        print_table(entries, statuses)
    for e, s in zip(entries, statuses):
        if s in ("conflict", "accepted"):
            explain_conflict(e)
    for p in problems:
        print("REFUSED: " + p)
    n_conflict = statuses.count("conflict")
    ok = n_conflict == 0 and not problems
    n_todo = statuses.count("todo") + statuses.count("accepted")
    print(
        f"\n{n_todo} to apply, {statuses.count('done')} already applied, "
        f"{n_conflict} conflicts"
    )
    print("CHECK PASSED" if ok else "CHECK FAILED — nothing was written")
    if n_conflict:
        print(
            "A conflict means this repo's code differs from the copy the bundle was built\n"
            "from (above: the code-only diff). If nobody edited that file by hand, the\n"
            "difference is a transcription slip in the bundle's copy: add\n"
            "  --accept <path>\n"
            "to both the --check and the --apply command. Otherwise send the diff back."
        )
    return ok


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    if not cmd_check(entries, quiet=True):
        return False
    for e in entries:
        status = file_status(e)
        if status not in ("todo", "accepted"):
            continue
        path = pathlib.Path(e["path"])
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
        else:
            new = e["new"]
            if e["action"] == "replace" and status == "todo":
                new = _rebase(new, e["base"], _read(path))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(new.encode("utf-8"))
    bad = [e["path"] for e in entries if file_status(e) != "done"]
    failures = [f"not in the expected final state: {p}" for p in bad]
    failures += compile_and_import(entries, do_import)
    for f in failures:
        print("FAILED " + f)
    if failures:
        print("APPLY FAILED — undo with --revert, then send the messages above back")
        return False
    print(f"{len(entries)} files in their new state, compile OK"
          + (", imports OK" if do_import else " (imports skipped)"))
    print("APPLY PASSED — review with `git status` / `git diff`")
    return True


def cmd_revert(entries: list[dict]) -> bool:
    skipped = []
    for e in entries:
        path = pathlib.Path(e["path"])
        current = _read(path)
        cur_sha = None if current is None else _sha(current)
        if e["action"] == "add":
            if cur_sha == e["new_sha"]:
                path.unlink()
                for parent in path.parents:
                    if parent == pathlib.Path(".") or any(parent.iterdir()):
                        break
                    parent.rmdir()
            elif current is not None:
                skipped.append(e["path"])
        elif (current is not None and e["new"] is not None and _is_new(current, e)) or (
            e["action"] == "delete" and current is None
        ):
            # restore the committed bytes (the repo's own file, exactly); apply refuses
            # to run over uncommitted changes, so HEAD is the state before --apply
            committed = _head_version(e["path"])
            restore = committed if committed is not None else e["base"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(restore.encode("utf-8"))
        elif not _matches_base(current, e):
            skipped.append(e["path"])
    for p in skipped:
        print(f"left alone (edited after apply): {p}")
    print("REVERT DONE" if not skipped else "REVERT PARTIAL — see the files above")
    return not skipped


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("bundle")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--revert", action="store_true")
    ap.add_argument("--no-import", action="store_true")
    ap.add_argument("--accept", action="append", default=[], metavar="PATH")
    args = ap.parse_args()
    ACCEPTED.update(args.accept)

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
              f"{APPLY_VERSION}. Redo step 3 of the bundle.")
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
Clean up after mirror bundle 03_a1_month_end.md, on the bundle's branch.
- HDFS first (the user runs these in PROD; UAT has no data): resolve the catalog paths
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check`
  for model_id cc_60_180 and cc_180_plus, and
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b03_check`
  for cc_60_180, from the workplace conf, and write out the three commands in full, e.g.
  `hdfs dfs -rm -r <resolved path>`.
- Remove the temporary check (everything marked TEMPORARY for bundle 03):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b01_check` and
    `crx_cc_a1_ability_b03_check` entries and their TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_cc_a1_ability_b03_check"` entry and
    its comment;
  - crx_persona/cc_a1_ability_v2/pipeline.py: `create_b03_check_pipeline`, the imports of
    `create_cc_obs_pipeline` and `b03_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/cc_a1_ability_v2/__init__.py: the `create_b03_check_pipeline` export;
  - delete crx_persona/cc_a1_ability_v2/b03_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b01\|b03" src conf` prints
  nothing.
- Delete the validation folder `tmp_validation/a1_v01/` (git rm; leave any other
  tmp_validation folder alone).
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
