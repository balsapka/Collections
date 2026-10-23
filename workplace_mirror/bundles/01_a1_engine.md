# Mirror bundle 01 — Shared helpers, observation base and A1 engine (CC)

apply_bundle version: 2 · built 2026-10-23 from `0c45e6e..4756b25` · source: 6 added, 6 replaced, 0 deleted · helpers: 1

## Steps — do these in order, from the workplace repo root

Everything this bundle adds outside `src/` and `conf/` lives in `data/input/mirror_bundles/`
(gitignored). Nothing here is committed; commit `src/` and `conf/` only if you
decide to keep the change. Copy each command block exactly as it is.

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/persona_redesign_b01
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/01_a1_engine.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script from the *Apply script* section at the bottom (prints `apply_bundle.py written`):

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '01_a1_engine.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')"
```

**Step 4.** Dry run — must end with `CHECK PASSED` (nothing is written):

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/01_a1_engine.md --check
```

**Step 5.** Apply — must end with `APPLY PASSED`:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/01_a1_engine.md --apply
```

**Step 6.** Look at what changed:

```bash
git status && git diff --stat
```

**Step 7.** Before re-running A1, keep a copy of the current output. In a Kedro notebook
(`kedro jupyter notebook`), run this cell:

```python
import sys, pathlib
_c = pathlib.Path.cwd()
ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
from b01_a1_engine_check import main
main(catalog, step="snapshot")
```

**Step 8.** Rebuild the observation base, then the A1 axis (terminal):

```bash
kedro run --pipeline=crx_cc_obs_base
```

```bash
kedro run --pipeline=crx_cc_a1_ability_v2
```

**Step 9.** Compare old vs new in the same notebook and paste the printed `B01 OUTPUT`
block back:

```python
main(catalog, step="compare")
```

**Step 10.** Repeat steps 7–9 for the other CC segment: set `model_id` in
`conf/dev/globals_dev.yml` (`cc_60_180` ↔ `cc_180_plus`), restart the notebook kernel, run
again.

**Undo** (before any commit) — restores every touched file exactly:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/01_a1_engine.md --revert
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant (or run its steps yourself).

## What this bundle does

**What this bundle does.** Adds the shared helpers every persona axis will use
(`crx_persona/_common.py`), a per-product observation base (`obs_base/`: datasets
`crx_cc_obs_base`, `crx_rl_obs_base`) and the A1 ability engine (`crx_persona/a1_ability/`), which
implements the GRR workbook `A1_ability_20261022` (spec: `specs/A1_ability_spec.md` in the
mirror repo). The CC A1 axis (`cc_a1_ability_v2`) becomes a thin wrapper on the engine.
CC A1 v1, RL A1 and every other axis are untouched.

**What changes in `crx_cc_a1_ability_v2`:**
- the rules now follow the workbook month by month: a salary month needs a credit
  ≥ max(AED 3,000, 2 × anchor) (2 of the last 3 months, not more than 25% below the prior
  quarter); CASA ≥ max(AED 3,000, anchor) in 2 of the last 3 months (not more than 50%
  below the prior quarter); one external card payment ≥ max(AED 500, anchor); "last 3
  months" = the 3 complete calendar months before the observation month;
- anchor: CC 60–180 = amount in the oldest overdue bucket (OVD_01..06, snapshot ≤ 31
  days old); CC 180+ = none, absolute thresholds only; missing → flat floors;
- inputs: `wm_fea_casa_eod_avg_balance` replaces `feat_casa_eod_balance`;
  `feat_payroll_indicator` is no longer read (salary amounts per month come from the WM
  salary snapshots); `params:model_id` feeds the anchor;
- columns lose the `_v2` suffix (`a1_state`, `a1_income_level`, …) and gain
  `liquidity_anchor_amt`; intermediate datasets are `crx_cc_a1_{income,liquidity,distress}_signals`
  and `crx_cc_a1_liquidity_anchor`;
- accounts without a CIF now appear as `ability_unknown` instead of being missing;
- a missing source column stops the run with a clear error.
  Required: `wm_fea_salary_days_since_increment.ft_days_since_salary_transaction`,
  `wm_fea_casa_eod_avg_balance.ft_avg_casa_eod_balance_in_last_0_3_weeks_avg`.

**TODOs for the workplace assistant** (search `TODO(sonnet)` in `a1_ability/signals.py`):
1. Internal cheque bounces / DDS returns: find the source (CASA transaction codes or
   narrations in `comp_financial_tran_repos_dly`, a DDS mandate table), build
   `(cif_id, event_date)` across all of the customer's accounts, and pass it as
   `internal_returns` to the distress node.
2. Validate the per-month internal salary credits recovered from the WM snapshots against
   `feat_payroll_indicator`; prefer a table with monthly salary amounts if one exists.

The PROD check snippet (`b01_a1_engine_check.py`) is shipped to `data/input/mirror_bundles/`;
its snapshot copy lives on HDFS next to the A1 output and is deleted by the cleanup step.

## Instructions for the workplace assistant

1. Do not retype or hand-edit code from this file; `apply_bundle.py` writes it.
2. `--check` must print **CHECK PASSED**. On CONFLICT the workplace file differs from
   the version this bundle was built from: stop and show the printed diff to the user.
3. `DAMAGED` means the markdown copy was altered — recopy the raw file.
4. `--apply` must print **APPLY PASSED**; if an import fails, run `--revert` and report.
5. Touch nothing outside the manifest. Never commit `data/input/mirror_bundles/`.

## Manifest

| Action | Path |
|---|---|
| replace | `conf/base/catalog/catalog_crx.yml` |
| replace | `conf/base/parameters/parameters_crx_persona.yml` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/crx_persona/_common.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/obs_base/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py` |
| add (helper) | `data/input/mirror_bundles/b01_a1_engine_check.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `61123e0aac20d9bb2531dd7d5f54ea98212b9a41910a9430480a543936d63dd2` · base trailing newline: yes · new sha256 `f8cf0cfe691280c8ef9bcea7317e7ffdbb28649f83968a2ff5401a0cd4221dd2` · new trailing newline: yes

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

# ── A1 Ability axis v2 (T31 — GRR MECE points redesign) ─────────────────────
# Additive beside cc_a1_ability (R18) — T26's pipeline/catalog entries above
# are never modified. Abandon path: delete this block + cc_a1_ability_v2/.

# Node 1: CIF-resolved spine rows (observation_date anchor only — no T0/spell)
crx_cc_a1v2_cif_base:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1v2_cif_base"
  save_args:
    mode: overwrite

# Node 2: income evidence (salary_months_h2, salary_amt_last, bureau salary)
crx_cc_a1v2_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1v2_income_signals"
  save_args:
    mode: overwrite

# Node 3: liquidity evidence + oldest-overdue-bucket anchor (blueprint §4)
crx_cc_a1v2_liquidity_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1v2_liquidity_signals"
  save_args:
    mode: overwrite

# Node 4: distress evidence (cheque bounce / DDS return)
crx_cc_a1v2_distress_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1v2_distress_signals"
  save_args:
    mode: overwrite

# Node 5: assembled A1 ability v2 axis (parallel/temporary beside crx_cc_a1_ability)
# Grain: (account_id, observation_date). a1_state_v2 in {ability_high,
# ability_moderate, ability_low, ability_unknown}.
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

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `c05c0d007f901891229fc5f6ab5634dbd07139c2911e7bf20331b3cedd6f0c11` · base trailing newline: yes · new sha256 `0ed7b0bb06924ed787a655fbf49119fbe97b771618d3260b1c0d8c9c8cecf023` · new trailing newline: yes

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
# rl_60_180 / rl_180_plus). Additive key (R18) — used by cc_a2_locatability and
# rl_a2_locatability (Node 4, T29/RL-A2-3 design, promoted 2026-10-22) to select
# segment-aware thresholds; same resolver pattern as crx_persona above.
model_id: "${globals:model_id}"
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
# rl_60_180 / rl_180_plus). Additive key (R18) — used by cc_a2_locatability and
# rl_a2_locatability (Node 4, T29/RL-A2-3 design, promoted 2026-10-22) to select
# segment-aware thresholds; same resolver pattern as crx_persona above.
model_id: "${globals:model_id}"

# Log state distributions (one extra Spark job per axis). Off in production runs.
crx_log_stats: false
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `ef9f6f5a8f2dbf2d5e39f72bd5cbd8e5ca4c9e7dbb806edd79e40e1e912ec7b2` · base trailing newline: yes · new sha256 `976767843031be1f282f9d8257d3c1dce3bd1688ed39d3d28c47b24975768683` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: add · new sha256 `69266100d0a55b19bcd5cacce6e406bd06e056c3db65e40b54c5aec9759813a1` · new trailing newline: yes

New:

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

from enbd_collections.pipelines.crx_persona._spine_utils import _build_cif_bridge

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


def build_cc_obs_base(
    cc_spine: DataFrame, contract: DataFrame, client: DataFrame
) -> DataFrame:
    """Every CC spine row with its ``cif_id`` (NULL if the contract has no client).

    Rows without a CIF are kept: customer-level signals are simply absent for them.
    """
    spine = cc_spine.select(
        F.col("contract_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date"),
    ).dropDuplicates(list(GRAIN))
    bridge = _build_cif_bridge(contract, client).select(
        F.col("contract_id").cast("string").alias("account_id"), "cif_id"
    )
    return spine.join(bridge, on="account_id", how="left")


def build_rl_obs_base(rl_spine: DataFrame) -> DataFrame:
    """Every RL spine row with the ``cif_id`` the spine already carries."""
    return rl_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        "cif_id",
    ).dropDuplicates(list(GRAIN))
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: add · new sha256 `de7eff27ace0fdcdc5690de1b1cd9c56a44085dae4e10e8c75e0a33ae1cecf4e` · new trailing newline: yes

New:

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)

__all__ = [
    "build_a1_ability",
    "build_distress_signals",
    "build_income_signals",
    "build_liquidity_signals",
]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: add · new sha256 `537653831b6fe08435661252621aee9642766eb7b10390ed82a44f6bd393a6d3` · new trailing newline: yes

New:

`````python
"""A1 ability state — GRR MECE points.

Spec: ``workplace_mirror/specs/A1_ability_spec.md``.

    income level     stable 2 / weak 1 / none 0
  + liquidity level  adequate 2 / weak 1 / none 0
  = points           4 high, 2–3 moderate, 0–1 low
  distress (cheque bounce / DDS return) lowers the state one level;
  no income, no liquidity, no distress and no CASA transaction → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_distribution
from ..scoring_engine import StateLadder, points_from_level

N3 = 2  # months of the last 3 that must qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
D_INC = 0.25  # stable income may fall at most this share vs the prior 3 months
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=4,
    moderate_from_points=2,
)
_LAST3, _PRIOR3 = (1, 2, 3), (4, 5, 6)


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


def _not_weakening(prefix: str, max_drop: float, missing_is_zero: bool) -> Column:
    """The last-3-month average is not more than ``max_drop`` below the prior 3 months
    (true when there is no prior quarter to compare with)."""
    recent = _mean(_months(prefix, _LAST3), missing_is_zero)
    prior = _mean(_months(prefix, _PRIOR3), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column) -> Column:
    last3 = _months("income", _LAST3)
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last3, floor) >= N3) & _not_weakening(
        "income", D_INC, True
    )
    weak = _count_at_least(last3, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column) -> Column:
    last3 = _months("casa", _LAST3)
    payment = F.coalesce(F.col("ext_card_payment_max_3m"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last3, casa_floor) >= N3) & _not_weakening(
        "casa", D_CASA, False
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last3, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    log_stats: bool = False,
) -> DataFrame:
    """One A1 state per observation-base row.

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    df = (
        df.withColumn("a1_income_level", income_level(amt))
        .withColumn("a1_liquidity_level", liquidity_level(amt))
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
        & (F.coalesce(F.col("casa_active_3m"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    out = df.select(
        *GRAIN,
        "a1_state",
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.current_date().alias("computed_at"),
    )
    log_distribution(out, "a1_state", "a1_ability", log_stats)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: add · new sha256 `1736daea69c92ee7bcec3245b5f5ca33319f8e9ade24c5e1ad12ec654173e8f5` · new trailing newline: yes

New:

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
      ``(cif_id, event_date)``.

    TODO(sonnet): no internal source exists in the code base yet. Find where returned
    cheques and DDS returns are recorded internally (candidates: CASA transaction codes
    or narrations in ``comp_financial_tran_repos_dly``, a DDS mandate table), build a
    ``(cif_id, event_date)`` frame and pass it here from the pipeline. Take every
    account of the customer (CIF level), not the scored account: an RL account_id is
    not the customer's CASA account.
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
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py`
action: replace · base sha256 `6499bc5e770ab066f3d239787726d3fe5c992d62b6ee9db71854e6058e8c5f35` · base trailing newline: yes · new sha256 `65c9988c7d9e81a1dfeba967bdfe4f03037ccf21b7749032026e46e7beafee42` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T31 — A1 Ability axis v2 (GRR MECE points redesign)."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py`
action: replace · base sha256 `0eebf8f3efc79067df2ef50942774f405de3e9889ed05bcf591369ddaf2ef142` · base trailing newline: yes · new sha256 `5cb0d9f21a093685fc39936236a09c381eb18af5487326b1ae630b55d0a81036` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T31 — A1 Ability axis v2: GRR MECE points redesign.

Replaces T26's 5-dimension T0-anchored waterfall (``cc_a1_ability``) with the
GRR-specified MECE points system (`data/input/A1_ability_framework_1008_blueprint.md`):
two point dimensions (``income_points``, ``liquidity_points``, each 0/1/2)
summed to a total, a single distress override (cheque bounce / DDS return)
that drops the state one level, and a no-signal gate to ``ability_unknown``.
Purely ``observation_date``-anchored — the blueprint drops every T0-anchored
dimension (utilisation pressure, payment trajectory) the old waterfall used,
so there is no T0 variant here at all.

Additive beside T26 (R18): ``cc_a1_ability/{nodes,enrichers,pipeline}.py`` are
never imported for their classifier logic, only reused via
``enrichers.enrich_salary_months_h2`` / ``enrich_salary_pit`` /
``enrich_bureau_salary`` / ``enrich_ext_cc_payments_h2`` /
``enrich_casa_inflow_h2`` (R14 — zero duplication of those functions).

Five-node pipeline:
    build_a1v2_cif_base(cc_spine, prm_contract, prm_client)
        -> crx_cc_a1v2_cif_base                [Node 1]  CIF-resolved spine rows
    build_a1v2_income_signals(...)
        -> crx_cc_a1v2_income_signals          [Node 2]  salary_months_h2,
                                                         salary_amt_last,
                                                         bureau_salary_*
    build_a1v2_liquidity_signals(...)
        -> crx_cc_a1v2_liquidity_signals       [Node 3]  oldest_overdue_amount,
                                                         casa_recent3m/prior3m_avg,
                                                         ext_cc_payment_*,
                                                         casa_inflow/outflow_cnt_h2
    build_a1v2_distress_signals(...)
        -> crx_cc_a1v2_distress_signals        [Node 4]  bounced_cheque_amt_3m
    build_a1v2_classify(...)
        -> crx_cc_a1_ability_v2                [Node 5]  shipped v2 axis

Grounding (T31 Leg A, `docs/context/results/T31_a1_mece_eda_cc_{60_180,180_plus}_20261022.json`):
  - Oldest-active-overdue-bucket anchor: 100% coverage on both segments,
    monotonic bucket population confirmed by eyeball sample — used as the
    balance-relative anchor (``k_casa``/``k_pay``) per blueprint §4, replacing
    the sheet's rejected ``min_due`` formula.
  - Distress: ``prm_bureau_alert_enriched.bounced_cheque_amount`` confirmed
    present and populated — used directly. ``prm_bureau_payment_order``
    (reason_code) and ``feature_retail_loans`` (aecb_direct_debit_returns_6m)
    are real primary-model fields (confirmed against
    ``src/data_engineering/primary/models/{bureau,external_risk}.py``) but
    both PATH_NOT_FOUND in this PROD environment today (not yet
    materialized) — accepted per the card's decision gate; the optional
    enrichers below degrade to "no evidence" (not an error) when their
    source DataFrame is absent, and are not wired into ``pipeline.py`` yet.
    Wiring them is a pipeline.py input addition only, once the tables land
    — no change to the distress formula itself.
  - Income monthly-amount series: NOT available (``feat_payroll_indicator``
    carries only presence/count columns, no amount column). Approximated
    per the card's sanctioned fallback: ``salary_months_h2`` (presence
    count) combined with the scalar PIT amounts T26 already sources
    (``salary_amt_last``, ``bureau_salary_amt_last``) against the flat
    income floor. The sheet's literal "25% weakening vs prior 3m" trend
    test is NOT built for income — no monthly amount series exists to
    trend. Flagged as a known approximation, same discipline as T26's own
    [CONFIRM] thresholds.
  - CASA 2-of-3-months test: real monthly series confirmed (6 distinct
    months per CIF in a 6m window, ~99.9% coverage). Approximated as a
    recent-3m-average vs prior-3m-average comparison (reusing
    ``ft_avg_eod_balance_in_last_0_2_months_avg`` — already a 3-month
    trailing average per monthly row) rather than a literal per-month
    qualifying count, since the only confirmed balance column is itself a
    rolling average, not a single-month balance. Flagged as an
    approximation of the sheet's literal 2-of-3 test.

Locked decisions (blueprint, do not reopen):
  - Income floor is flat AED 3,000 (``k_inc = 0``) — no balance-relative term.
  - ``k_casa = k_pay = 1`` anchor to ``oldest_overdue_amount``, not
    ``cc_total_outstanding`` and not a derived minimum-due figure.
  - State names carry over unchanged: High/Moderate/Limited/Unknown ->
    ability_high/ability_moderate/ability_low/ability_unknown. T26's
    `cc_a1_ability` keeps its own `ability_limited` label (not renamed).

No confidence column — not needed for this axis (user direction). Breakdown
columns (``a1_income_level_v2``, ``a1_liquidity_level_v2``,
``a1_points_total_v2``, ``a1_distress_flag_v2``) are presence/evidence
breakdowns, analogous to A3's own dimension-level columns.

All ``_TAU_A1V2_*`` / ``_F_*`` / ``_K_*`` thresholds are the blueprint's own
starting values (§6) — explicitly un-validated against PROD data, same
[CONFIRM] discipline as every other axis in this programme.
"""

import datetime
import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import _build_cif_bridge
from enbd_collections.pipelines.crx_persona.cc_a1_ability import enrichers
from enbd_collections.pipelines.crx_persona.scoring_engine import (
    StateLadder,
    points_from_level,
)

LOG = logging.getLogger(__name__)

# ── Blueprint thresholds (§6) — starting values, [CONFIRM] against PROD ──────
_TAU_A1V2_N3 = 2  # months out of last 3 that must qualify
_F_INT = (
    3000.0  # internal/bureau salary floor (k_inc=0 — flat, no balance-relative term)
)
_F_CASA = 3000.0  # CASA average balance floor
_F_PAY = 500.0  # external card payment floor
_DEMIN = 1000.0  # smallest amount counting as any evidence
_K_CASA = 1.0  # CASA x oldest-overdue-bucket multiple
_K_PAY = 1.0  # external payment x oldest-overdue-bucket multiple
_D_CASA = 0.5  # CASA weakening threshold (share drop, recent-3m vs prior-3m)
_S_HIGH = 4  # points needed for High
_S_MOD = 2  # points needed for Moderate

_INCOME_POINTS_BY_LEVEL = {"stable": 2, "weak": 1, "none": 0}
_LIQUIDITY_POINTS_BY_LEVEL = {"adequate": 2, "weak": 1, "none": 0}

_STATE_LADDER = StateLadder(
    high="ability_high",
    moderate="ability_moderate",
    low="ability_low",
    unknown="ability_unknown",
    high_from_points=_S_HIGH,
    moderate_from_points=_S_MOD,
)

_OVERDUE_BUCKET_COLS = [f"overdue_bucket_{i:02d}" for i in range(1, 9)]


# ── Node 1: build_a1v2_cif_base ──────────────────────────────────────────────


def build_a1v2_cif_base(
    cc_spine: DataFrame,
    contract: DataFrame,
    client: DataFrame,
) -> DataFrame:
    """Resolve CIF for every spine row; emit only CIF-resolved rows.

    Purely observation_date-anchored (no T0/spell join — this axis has no
    T0-anchored dimension, per the blueprint). Mirrors T26's build_a1_cif_bridge
    CIF-resolution shape (R14 — same _build_cif_bridge helper), but applied
    directly to the spine instead of a spell-windowed base.

    Args:
        cc_spine:  Model-id-scoped spine — (contract_id, observation_date).
        contract:  prm_contract — contract_id -> client_id.
        client:    prm_client  — client_id -> cif_id.

    Returns:
        crx_cc_a1v2_cif_base — (account_id, observation_date, cif_id).
        Only rows where CIF was resolved.
    """
    cif_bridge = _build_cif_bridge(contract, client)

    # Rename contract_id -> account_id before joining (not after) so the two
    # sides never carry a same-named column into the join at the same time —
    # cif_bridge's own contract_id is then unambiguous and can be dropped
    # directly. Same shape as T26's build_a1_cif_bridge / enrich_prm_balance.
    spine_sel = cc_spine.select(
        F.col("contract_id").alias("account_id"),
        F.col("observation_date").cast("date"),
    )

    with_cif = spine_sel.join(
        cif_bridge,
        on=spine_sel["account_id"] == cif_bridge["contract_id"],
        how="left",
    ).drop("contract_id")

    return with_cif.filter(F.col("cif_id").isNotNull()).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("cif_id"),
    )


# ── Node 2: build_a1v2_income_signals ────────────────────────────────────────


def build_a1v2_income_signals(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    wm_salary: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
) -> DataFrame:
    """Income evidence at observation_date anchor — presence counts + scalar amounts.

    Three enrichers reused unmodified from cc_a1_ability.enrichers (R14),
    anchored to observation_date instead of t0:
      1. enrich_salary_months_h2   -> salary_months_h2 (count of last-3-months
         with payroll_flag=1 — presence, not a monthly amount series; see
         module docstring on the income-amount-series gap).
      2. enrich_salary_pit         -> salary_amt_last (latest WM PIT salary
         amount — scalar, not monthly).
      3. enrich_bureau_salary      -> bureau_salary_present_6m_flag,
         bureau_salary_amt_last (6m window bureau salary — single-pull
         reality per T31 Leg A §5/§9.5).

    Args:
        cif_base:               crx_cc_a1v2_cif_base.
        feat_payroll:           feat_payroll_indicator (retail.feature_space).
        wm_salary:              wm_fea_salary_days_since_increment (WM).
        stg_salary_hist:        stg_aecb_salary_history (AECB).
        prm_bureau_cif_bridge:  bureau file UUID -> cif_id bridge.

    Returns:
        crx_cc_a1v2_income_signals — (account_id, observation_date,
            salary_months_h2, salary_amt_last, bureau_salary_present_6m_flag,
            bureau_salary_amt_last).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_base, feat_payroll, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(cif_base, wm_salary, anchor_col, grain_key)
    bur_sal = enrichers.enrich_bureau_salary(
        cif_base, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )

    result = cif_base.select(*grain_key)

    if salary_h2 is not None:
        result = result.join(salary_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("salary_months_h2", F.lit(None).cast("int"))

    if sal_pit is not None:
        result = result.join(
            sal_pit.select(*grain_key, "salary_amt_last"),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("salary_amt_last", F.lit(None).cast("double"))

    if bur_sal is not None:
        result = result.join(bur_sal, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "bureau_salary_present_6m_flag", F.lit(None).cast("int")
        ).withColumn("bureau_salary_amt_last", F.lit(None).cast("double"))

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("salary_amt_last").cast("double"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("bureau_salary_amt_last").cast("double"),
    )


# ── Node 3: build_a1v2_liquidity_signals ─────────────────────────────────────


def _enrich_oldest_overdue_amount(
    base: DataFrame,
    prm_balance: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """PIT-join prm_balance's 8 overdue buckets; derive the oldest active amount.

    "Oldest active overdue bucket" = the value in the highest-indexed
    non-null/non-zero overdue_bucket_01..08 column — buckets accumulate
    (confirmed by T31 Leg A check 1 eyeball sample: lower-indexed buckets
    populate first and stay populated as the account ages), so the
    highest-active-index bucket is the longest-aged unpaid slice. Replaces
    the rejected cc_total_outstanding/min_due anchor (blueprint §4).

    Mirrors cc_a1_ability.enrichers.enrich_prm_balance's exact PIT join
    pattern (anchor-collision handling, contract_id == account_id join).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., oldest_overdue_amount).
    """
    _required = ["contract_id", "observation_date"] + _OVERDUE_BUCKET_COLS
    missing = [c for c in _required if c not in prm_balance.columns]
    if missing:
        LOG.warning(
            "_enrich_oldest_overdue_amount: prm_balance missing %s"
            " — oldest_overdue_amount will be NULL",
            missing,
        )
        return None

    _grain_cols = list(grain_key)

    bal = prm_balance.select(
        F.col("contract_id"),
        F.col("observation_date").cast("date").alias("_bal_obs_date"),
        *[F.col(c).cast("double").alias(c) for c in _OVERDUE_BUCKET_COLS],
    )

    if anchor_col in _grain_cols:
        base_sel = base.select(*_grain_cols).withColumn("_anchor", F.col(anchor_col))
    else:
        base_sel = base.select(*_grain_cols, F.col(anchor_col).alias("_anchor"))

    joined = (
        base_sel.join(
            bal,
            on=(base_sel["account_id"] == bal["contract_id"]),
            how="left",
        )
        .filter(
            F.col("_bal_obs_date").isNotNull()
            & (F.col("_bal_obs_date") <= F.col("_anchor"))
        )
        .drop("contract_id", "_anchor")
    )

    w = Window.partitionBy(*_grain_cols).orderBy(F.col("_bal_obs_date").desc())
    pit = joined.withColumn("_rn", F.row_number().over(w)).filter(F.col("_rn") == 1)

    # Highest-indexed non-null/non-zero bucket wins — buckets accumulate from
    # 01 upward, so coalescing from 08 down to 01 (skipping nulls/zeros) picks
    # the longest-aged unpaid slice.
    oldest_expr = F.coalesce(
        *[F.when(F.col(c) > 0, F.col(c)) for c in reversed(_OVERDUE_BUCKET_COLS)]
    )

    return pit.select(*_grain_cols, oldest_expr.alias("oldest_overdue_amount"))


def _enrich_casa_eod_balance_windows(
    base: DataFrame,
    feat_casa_bal: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """Recent-3m vs prior-3m CASA average balance from feat_casa_eod_balance.

    T31 Leg A check 3 confirmed 6 distinct month_end_date rows per CIF in the
    [obs-6m, obs) window for ~99.9% of CIFs on both segments — a real monthly
    series exists. Each row's ft_avg_eod_balance_in_last_0_2_months_avg is
    already a 3-month-trailing average as of that row's month_end_date (the
    same column cc_a1_ability.enrichers uses for a single PIT sample), so the
    latest row in [obs-3m, obs) stands in for "the recent 3-month average" and
    the latest row in [obs-6m, obs-3m) stands in for "the prior 3-month
    average" — reusing the one confirmed real column rather than deriving a
    new one (R9). This approximates the blueprint's literal 2-of-3-months
    qualifying count with a window-average comparison; flagged as an
    approximation, not an exact re-derivation.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_recent3m_avg, casa_prior3m_avg).
    """
    _CASA_BAL_COL = enrichers._CASA_BAL_COL  # pylint: disable=protected-access
    _required = ["month_end_date", _CASA_BAL_COL]
    missing = [c for c in _required if c not in feat_casa_bal.columns]
    if missing:
        LOG.warning(
            "_enrich_casa_eod_balance_windows: feat_casa_eod_balance missing %s"
            " — casa_recent3m_avg/casa_prior3m_avg will be NULL",
            missing,
        )
        return None

    cb_dated = feat_casa_bal.withColumn(
        "_month_date", F.col("month_end_date").cast("date")
    ).select("cif_id", "_month_date", _CASA_BAL_COL)

    joined = base.join(cb_dated, on="cif_id", how="inner").filter(
        (F.col("_month_date") >= F.date_sub(F.col(anchor_col), 180))
        & (F.col("_month_date") < F.col(anchor_col))
    )

    recent = joined.filter(F.col("_month_date") >= F.date_sub(F.col(anchor_col), 90))
    prior = joined.filter(F.col("_month_date") < F.date_sub(F.col(anchor_col), 90))

    w_recent = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    recent_pit = (
        recent.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(*grain_key, F.col(_CASA_BAL_COL).alias("casa_recent3m_avg"))
    )

    w_prior = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    prior_pit = (
        prior.withColumn("_rn", F.row_number().over(w_prior))
        .filter(F.col("_rn") == 1)
        .select(*grain_key, F.col(_CASA_BAL_COL).alias("casa_prior3m_avg"))
    )

    return recent_pit.join(prior_pit, on=list(grain_key), how="outer")


def _enrich_casa_outflow_h2(
    cif_base: DataFrame,
    wm_casa_inflow: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """H2 generic CASA outflow count from wm_fea_casa_cc_inflow_outflow.

    Mirrors cc_a1_ability.enrichers.enrich_casa_inflow_h2 exactly, reading
    the outflow-named column T31 Leg A check 4 confirmed exists alongside the
    inflow column (ft_outflow_casa_amt_in_last_0_0_weeks_sum) — needed for
    the any-direction CASA-activity signal gate (blueprint §2.4).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_outflow_cnt_h2).
    """
    _OUTFLOW_COL = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"
    if _OUTFLOW_COL not in wm_casa_inflow.columns:
        LOG.warning(
            "_enrich_casa_outflow_h2: wm_fea_casa_cc_inflow_outflow missing '%s'"
            " — casa_outflow_cnt_h2 will be NULL",
            _OUTFLOW_COL,
        )
        return None

    co_dated = wm_casa_inflow.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", _OUTFLOW_COL)

    outflow_h2 = (
        cif_base.join(co_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col(_OUTFLOW_COL) > 0, F.lit(1)).otherwise(F.lit(0)))
            .cast("int")
            .alias("casa_outflow_cnt_h2")
        )
    )

    return outflow_h2


def build_a1v2_liquidity_signals(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    cif_base: DataFrame,
    prm_balance: DataFrame,
    feat_casa_bal: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Liquidity evidence + the balance-relative anchor, at observation_date.

    New enrichers (oldest_overdue_amount, casa window averages, CASA
    outflow count) plus one reused unmodified from cc_a1_ability.enrichers
    (R14): enrich_ext_cc_payments_h2 and enrich_casa_inflow_h2.

    Args:
        cif_base:                 crx_cc_a1v2_cif_base.
        prm_balance:              prm_balance — overdue_bucket_01..08.
        feat_casa_bal:            feat_casa_eod_balance (retail.feature_space).
        wm_casa_inflow:           wm_fea_casa_cc_inflow_outflow (WM).
        wm_labelled_transactions: wm_pri_labelled_transactions (WM).
        beneficiary_cards:        raw_beneficiary_cards.
        crx_persona:              Persona param dict (persona_start_date).

    Returns:
        crx_cc_a1v2_liquidity_signals — (account_id, observation_date,
            oldest_overdue_amount, casa_recent3m_avg, casa_prior3m_avg,
            ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2, casa_inflow_cnt_h2,
            casa_outflow_cnt_h2).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(crx_persona["persona_start_date"])
    )

    overdue = _enrich_oldest_overdue_amount(
        cif_base, prm_balance, anchor_col, grain_key
    )
    casa_windows = _enrich_casa_eod_balance_windows(
        cif_base, feat_casa_bal, anchor_col, grain_key
    )
    ext_pay = enrichers.enrich_ext_cc_payments_h2(
        cif_base, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )
    casa_inflow = enrichers.enrich_casa_inflow_h2(
        cif_base, wm_casa_inflow, anchor_col, grain_key
    )
    casa_outflow = _enrich_casa_outflow_h2(
        cif_base, wm_casa_inflow, anchor_col, grain_key
    )

    result = cif_base.select(*grain_key)

    if overdue is not None:
        result = result.join(overdue, on=list(grain_key), how="left")
    else:
        result = result.withColumn("oldest_overdue_amount", F.lit(None).cast("double"))

    if casa_windows is not None:
        result = result.join(casa_windows, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "casa_recent3m_avg", F.lit(None).cast("double")
        ).withColumn("casa_prior3m_avg", F.lit(None).cast("double"))

    if ext_pay is not None:
        result = result.join(ext_pay, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "ext_cc_payment_amt_h2", F.lit(None).cast("double")
        ).withColumn("ext_cc_payment_cnt_h2", F.lit(None).cast("int"))

    if casa_inflow is not None:
        result = result.join(
            casa_inflow.select(*grain_key, "casa_inflow_cnt_h2"),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("casa_inflow_cnt_h2", F.lit(None).cast("int"))

    if casa_outflow is not None:
        result = result.join(casa_outflow, on=list(grain_key), how="left")
    else:
        result = result.withColumn("casa_outflow_cnt_h2", F.lit(None).cast("int"))

    return result.select(
        *grain_key,
        F.col("oldest_overdue_amount").cast("double"),
        F.col("casa_recent3m_avg").cast("double"),
        F.col("casa_prior3m_avg").cast("double"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("casa_outflow_cnt_h2").cast("int"),
    )


# ── Node 4: build_a1v2_distress_signals ──────────────────────────────────────


def _enrich_distress_bureau_alert(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """3-month bounced-cheque amount from prm_bureau_alert_enriched.

    T31 Leg A check 2 confirmed bounced_cheque_amount is present and
    populated on this table (independent of the return_date column, which
    is absent — not used here). Window: [anchor-90d, anchor), same pre-T0-
    style lookback discipline as cc_a1_ability.enrichers.enrich_bureau_alerts.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., bounced_cheque_amt_3m).
    """
    _required = ["cif_id", "extract_date", "bounced_cheque_amount"]
    missing = [c for c in _required if c not in prm_bureau_alert.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_bureau_alert: prm_bureau_alert_enriched missing %s"
            " — bounced_cheque_amt_3m will be NULL",
            missing,
        )
        return None

    alerts_dated = prm_bureau_alert.withColumn(
        "_alert_date", F.to_date(F.col("extract_date"))
    ).select(
        F.col("cif_id").alias("_bur_cif_id"),
        "_alert_date",
        F.col("bounced_cheque_amount").cast("double").alias("_bounced_amt"),
    )

    joined = cif_base.join(
        alerts_dated,
        on=cif_base["cif_id"] == alerts_dated["_bur_cif_id"],
        how="inner",
    ).filter(
        (F.col("_alert_date") >= F.date_sub(F.col(anchor_col), 90))
        & (F.col("_alert_date") < F.col(anchor_col))
    )

    return joined.groupBy(*grain_key).agg(
        F.sum(F.coalesce(F.col("_bounced_amt"), F.lit(0.0)))
        .cast("double")
        .alias("bounced_cheque_amt_3m")
    )


def _enrich_distress_payment_order(
    cif_base: DataFrame,
    prm_bureau_payment_order: DataFrame | None,
    anchor_col: str,
    grain_key: tuple,
) -> DataFrame | None:
    """Optional distress source: prm_bureau_payment_order.reason_code (3m window).

    PATH_NOT_FOUND in this PROD environment as of T31 Leg A (2026-10-22) — not
    yet materialized. Degrades to None (no evidence, not an error) whenever
    the caller doesn't have this table to pass in; wiring it is a pipeline.py
    input addition only (see nodes.py module docstring) — no change needed
    here once it lands, since the schema guard and join logic are already
    written against the real BureauPaymentOrder primary-model field names
    (cif_id, return_date, reason_code — confirmed from
    src/data_engineering/primary/models/bureau.py, not guessed).

    Returns None if the table is absent or required columns are missing.
    Returns DataFrame with (grain_key..., payment_order_distress_flag).
    """
    if prm_bureau_payment_order is None:
        return None

    _required = ["cif_id", "return_date", "reason_code"]
    missing = [c for c in _required if c not in prm_bureau_payment_order.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_payment_order: prm_bureau_payment_order missing %s"
            " — payment_order_distress_flag will be NULL",
            missing,
        )
        return None

    po_dated = prm_bureau_payment_order.withColumn(
        "_return_date", F.to_date(F.col("return_date"))
    ).select(
        F.col("cif_id").alias("_po_cif_id"),
        "_return_date",
        F.col("reason_code"),
    )

    joined = cif_base.join(
        po_dated,
        on=cif_base["cif_id"] == po_dated["_po_cif_id"],
        how="inner",
    ).filter(
        (F.col("_return_date") >= F.date_sub(F.col(anchor_col), 90))
        & (F.col("_return_date") < F.col(anchor_col))
        & F.col("reason_code").isNotNull()
    )

    return joined.groupBy(*grain_key).agg(
        F.lit(1).cast("int").alias("payment_order_distress_flag")
    )


def _enrich_distress_retail_loans(
    cif_base: DataFrame,
    feature_retail_loans: DataFrame | None,
    grain_key: tuple,
) -> DataFrame | None:
    """Optional distress source: feature_retail_loans.aecb_direct_debit_returns_6m.

    PATH_NOT_FOUND in this PROD environment as of T31 Leg A (2026-10-22) — not
    yet materialized. cif_id-only join, explicitly not PIT-correct (bureau
    data is person-level and this table carries no per-row date column usable
    for a windowed join at this grain — same caveat T31 Leg A flagged). Same
    "degrades to None" contract as _enrich_distress_payment_order.

    Returns None if the table is absent or required columns are missing.
    Returns DataFrame with (grain_key..., retail_loans_distress_flag).
    """
    if feature_retail_loans is None:
        return None

    _required = ["cif_id", "aecb_direct_debit_returns_6m"]
    missing = [c for c in _required if c not in feature_retail_loans.columns]
    if missing:
        LOG.warning(
            "_enrich_distress_retail_loans: feature_retail_loans missing %s"
            " — retail_loans_distress_flag will be NULL",
            missing,
        )
        return None

    rl_dated = feature_retail_loans.select(
        F.col("cif_id").alias("_rl_cif_id"),
        F.col("aecb_direct_debit_returns_6m").cast("int").alias("_dd_returns_6m"),
    )

    joined = cif_base.join(
        rl_dated, on=cif_base["cif_id"] == rl_dated["_rl_cif_id"], how="inner"
    ).filter(F.col("_dd_returns_6m") > 0)

    return joined.groupBy(*grain_key).agg(
        F.lit(1).cast("int").alias("retail_loans_distress_flag")
    )


def build_a1v2_distress_signals(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_payment_order: DataFrame | None = None,
    feature_retail_loans: DataFrame | None = None,
) -> DataFrame:
    """Cheque-bounce / DDS-return distress evidence at observation_date anchor.

    prm_bureau_payment_order / feature_retail_loans default to None — not
    wired as formal pipeline inputs yet (both PATH_NOT_FOUND in PROD today,
    T31 Leg A). When wired later (pipeline.py input addition only), their
    OR-terms activate automatically with no change to this function.

    Args:
        cif_base:                 crx_cc_a1v2_cif_base.
        prm_bureau_alert:         prm_bureau_alert_enriched (AECB).
        prm_bureau_payment_order: Optional — prm_bureau_payment_order (AECB).
        feature_retail_loans:     Optional — feature_retail_loans.

    Returns:
        crx_cc_a1v2_distress_signals — (account_id, observation_date,
            distress_flag).
    """
    grain_key = ("account_id", "observation_date")
    anchor_col = "observation_date"

    bur_alert = _enrich_distress_bureau_alert(
        cif_base, prm_bureau_alert, anchor_col, grain_key
    )
    pay_order = _enrich_distress_payment_order(
        cif_base, prm_bureau_payment_order, anchor_col, grain_key
    )
    retail_loans = _enrich_distress_retail_loans(
        cif_base, feature_retail_loans, grain_key
    )

    result = cif_base.select(*grain_key)

    if bur_alert is not None:
        result = result.join(bur_alert, on=list(grain_key), how="left")
    else:
        result = result.withColumn("bounced_cheque_amt_3m", F.lit(None).cast("double"))

    if pay_order is not None:
        result = result.join(pay_order, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "payment_order_distress_flag", F.lit(None).cast("int")
        )

    if retail_loans is not None:
        result = result.join(retail_loans, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "retail_loans_distress_flag", F.lit(None).cast("int")
        )

    result = result.withColumn(
        "distress_flag",
        F.when(
            (F.coalesce(F.col("bounced_cheque_amt_3m"), F.lit(0.0)) > 0)
            | (F.coalesce(F.col("payment_order_distress_flag"), F.lit(0)) == 1)
            | (F.coalesce(F.col("retail_loans_distress_flag"), F.lit(0)) == 1),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    return result.select(*grain_key, "distress_flag")


# ── Node 5: build_a1v2_classify ──────────────────────────────────────────────


def _income_level_col() -> "F.Column":
    """income_points dimension: Stable/Weak/None (blueprint §2.1, k_inc=0 flat floor)."""
    _amt_evidence = F.coalesce(
        F.col("salary_amt_last"), F.col("bureau_salary_amt_last")
    )
    _stable = (
        (F.coalesce(F.col("salary_months_h2"), F.lit(0)) >= _TAU_A1V2_N3)
        & _amt_evidence.isNotNull()
        & (_amt_evidence >= _F_INT)
    )
    _weak = (
        (F.coalesce(F.col("salary_months_h2"), F.lit(0)) >= 1)
        | (F.coalesce(F.col("bureau_salary_present_6m_flag"), F.lit(0)) == 1)
        | (_amt_evidence.isNotNull() & (_amt_evidence >= _DEMIN))
    )
    return (
        F.when(_stable, F.lit("stable"))
        .when(_weak, F.lit("weak"))
        .otherwise(F.lit("none"))
    )


def _liquidity_level_col() -> "F.Column":
    """liquidity_points dimension: Adequate/Weak/None (blueprint §2.2).

    casa_floor/pay_floor anchor to oldest_overdue_amount (k_casa=k_pay=1);
    falls back to the flat floor alone when oldest_overdue_amount is NULL
    (account has no active overdue bucket in scope — treat the balance-
    relative term as 0, consistent with setting k=0 per blueprint §4).
    """
    _casa_floor = F.greatest(
        F.lit(_F_CASA), _K_CASA * F.coalesce(F.col("oldest_overdue_amount"), F.lit(0.0))
    )
    _pay_floor = F.greatest(
        F.lit(_F_PAY), _K_PAY * F.coalesce(F.col("oldest_overdue_amount"), F.lit(0.0))
    )

    _casa_weakening = (
        F.col("casa_recent3m_avg").isNotNull()
        & F.col("casa_prior3m_avg").isNotNull()
        & (F.col("casa_recent3m_avg") < F.col("casa_prior3m_avg") * (1 - _D_CASA))
    )

    _casa_adequate = (
        F.col("casa_recent3m_avg").isNotNull()
        & (F.col("casa_recent3m_avg") >= _casa_floor)
        & (~_casa_weakening)
    )
    _ext_pay_adequate = (F.coalesce(F.col("ext_cc_payment_cnt_h2"), F.lit(0)) >= 1) & (
        F.coalesce(F.col("ext_cc_payment_amt_h2"), F.lit(0.0)) >= _pay_floor
    )

    _casa_weak = F.col("casa_recent3m_avg").isNotNull() & (
        F.col("casa_recent3m_avg") >= _DEMIN
    )
    _ext_pay_weak = (F.coalesce(F.col("ext_cc_payment_cnt_h2"), F.lit(0)) >= 1) & (
        F.coalesce(F.col("ext_cc_payment_amt_h2"), F.lit(0.0)) >= _DEMIN
    )

    _adequate = _casa_adequate | _ext_pay_adequate
    _weak = _casa_weak | _ext_pay_weak

    return (
        F.when(_adequate, F.lit("adequate"))
        .when(_weak, F.lit("weak"))
        .otherwise(F.lit("none"))
    )


def build_a1v2_classify(
    cif_base: DataFrame,
    income_signals: DataFrame,
    liquidity_signals: DataFrame,
    distress_signals: DataFrame,
) -> DataFrame:
    """Assemble signals and classify the A1 v2 MECE state.

    income_points/liquidity_points via scoring_engine.points_from_level;
    distress is a single boolean override (OR of the 3 distress sources —
    never a prioritized reason list, unlike A3; A1 has exactly one override
    condition per the blueprint); is_unknown (signal gate, blueprint §2.4) is
    computed inline here and passed to StateLadder.state() alongside
    points_total and the distress override.

    Args:
        cif_base:          crx_cc_a1v2_cif_base.
        income_signals:    crx_cc_a1v2_income_signals.
        liquidity_signals: crx_cc_a1v2_liquidity_signals.
        distress_signals:  crx_cc_a1v2_distress_signals.

    Returns:
        crx_cc_a1_ability_v2 — (account_id, observation_date, a1_state_v2,
            a1_provenance_v2, a1_income_level_v2, a1_liquidity_level_v2,
            a1_points_total_v2, a1_distress_flag_v2, computed_at).
        a1_state_v2 in {ability_high, ability_moderate, ability_low,
            ability_unknown}.
    """
    grain_key = ["account_id", "observation_date"]

    result = (
        cif_base.select(*grain_key)
        .join(income_signals, on=grain_key, how="left")
        .join(liquidity_signals, on=grain_key, how="left")
        .join(distress_signals, on=grain_key, how="left")
    )

    result = result.withColumn("a1_income_level_v2", _income_level_col()).withColumn(
        "a1_liquidity_level_v2", _liquidity_level_col()
    )

    result = result.withColumn(
        "a1_income_points_v2",
        points_from_level(F.col("a1_income_level_v2"), _INCOME_POINTS_BY_LEVEL),
    ).withColumn(
        "a1_liquidity_points_v2",
        points_from_level(F.col("a1_liquidity_level_v2"), _LIQUIDITY_POINTS_BY_LEVEL),
    )

    result = result.withColumn(
        "a1_points_total_v2",
        F.col("a1_income_points_v2") + F.col("a1_liquidity_points_v2"),
    )

    result = result.withColumn(
        "a1_distress_flag_v2", F.coalesce(F.col("distress_flag"), F.lit(0)) == 1
    )

    _has_casa_activity = (F.coalesce(F.col("casa_inflow_cnt_h2"), F.lit(0)) > 0) | (
        F.coalesce(F.col("casa_outflow_cnt_h2"), F.lit(0)) > 0
    )
    _is_unknown = (
        (F.col("a1_income_points_v2") == 0)
        & (F.col("a1_liquidity_points_v2") == 0)
        & (~F.col("a1_distress_flag_v2"))
        & (~_has_casa_activity)
    )

    result = result.withColumn(
        "a1_state_v2",
        _STATE_LADDER.state(
            F.col("a1_points_total_v2"), F.col("a1_distress_flag_v2"), _is_unknown
        ),
    )

    result = result.withColumn(
        "a1_provenance_v2",
        F.when(F.col("a1_state_v2") == "ability_unknown", F.lit("no_signal")).otherwise(
            F.lit("observed")
        ),
    )

    output = result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("a1_state_v2").cast("string"),
        F.col("a1_provenance_v2").cast("string"),
        F.col("a1_income_level_v2").cast("string"),
        F.col("a1_liquidity_level_v2").cast("string"),
        F.col("a1_points_total_v2").cast("int"),
        F.col("a1_distress_flag_v2").cast("int"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )

    _log_a1v2_stats(output)
    return output


def _log_a1v2_stats(df: DataFrame) -> None:
    """Log state distribution for the A1 ability v2 axis."""
    state_counts = df.groupBy("a1_state_v2").count().orderBy("a1_state_v2").collect()
    total = sum(r["count"] for r in state_counts)
    LOG.info("build_a1v2_classify — state distribution (n=%d):", total)
    for row in state_counts:
        pct = 100.0 * row["count"] / max(total, 1)
        LOG.info(
            "  a1_state_v2=%-25s %6d  (%5.1f%%)",
            row["a1_state_v2"],
            row["count"],
            pct,
        )
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py`
action: replace · base sha256 `3f1c91165090f34d46cce7e3291d004e0414fcf045b758c75f08731eb2e51b6d` · base trailing newline: yes · new sha256 `ad2071bcfae2ddfff5691fd9597d30eceaa91d9fec5df525823dd58d665a3e29` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T31 — A1 Ability axis v2 (GRR MECE points redesign).

Five-node pipeline, additive beside T26's cc_a1_ability (R18 — that
pipeline's nodes/enrichers/catalog entries are never modified). Emits a new
persona axis table, ``crx_cc_a1_ability_v2``, carrying ``a1_state_v2``.

Architecture:
    build_a1v2_cif_base           -> crx_cc_a1v2_cif_base          [Node 1]
    build_a1v2_income_signals     -> crx_cc_a1v2_income_signals    [Node 2] ┐
    build_a1v2_liquidity_signals -> crx_cc_a1v2_liquidity_signals [Node 3] ┤ parallel
    build_a1v2_distress_signals   -> crx_cc_a1v2_distress_signals  [Node 4] ┘
    build_a1v2_classify           -> crx_cc_a1_ability_v2          [Node 5]

prm_bureau_payment_order / feature_retail_loans are NOT wired into Node 4
here — both PATH_NOT_FOUND in PROD as of T31 Leg A (2026-10-22), not yet
materialized (see cc_a1_ability_v2/nodes.py module docstring). Node 4's
function signature already accepts them as optional parameters; wiring them
in once the tables land is a 2-line addition to this file's inputs list, no
change to the distress logic itself.

Run with:
    kedro run --pipeline=crx_cc_a1_ability_v2
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a1v2_cif_base,
    build_a1v2_classify,
    build_a1v2_distress_signals,
    build_a1v2_income_signals,
    build_a1v2_liquidity_signals,
)

_TAGS = ["crx", "a1", "ability", "a1_v2", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 5-node A1 Ability v2 pipeline."""
    return Pipeline(
        [
            node(
                func=build_a1v2_cif_base,
                inputs=["cc_spine", "prm_contract", "prm_client"],
                outputs="crx_cc_a1v2_cif_base",
                name="build_crx_a1v2_cif_base",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_income_signals,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "feat_payroll_indicator",
                    "wm_fea_salary_days_since_increment",
                    "stg_aecb_salary_history",
                    "prm_bureau_cif_bridge",
                ],
                outputs="crx_cc_a1v2_income_signals",
                name="build_crx_a1v2_income_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_liquidity_signals,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "prm_balance",
                    "feat_casa_eod_balance",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1v2_liquidity_signals",
                name="build_crx_a1v2_liquidity_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_distress_signals,
                inputs=["crx_cc_a1v2_cif_base", "prm_bureau_alert_enriched"],
                outputs="crx_cc_a1v2_distress_signals",
                name="build_crx_a1v2_distress_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a1v2_classify,
                inputs=[
                    "crx_cc_a1v2_cif_base",
                    "crx_cc_a1v2_income_signals",
                    "crx_cc_a1v2_liquidity_signals",
                    "crx_cc_a1v2_distress_signals",
                ],
                outputs="crx_cc_a1_ability_v2",
                name="build_crx_a1v2_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: CC A1 ability axis.

    crx_cc_obs_base ─┬─ income signals ────┐
                     ├─ liquidity signals ─┤
                     ├─ distress signals ──┼─► crx_cc_a1_ability_v2
                     └─ liquidity anchor ──┘

Needs crx_cc_obs_base (``kedro run --pipeline=crx_cc_obs_base``) first. Optional
distress sources (prm_bureau_payment_order, internal cheque / DDS returns) are added as
extra inputs of the distress node once they exist.

    kedro run --pipeline=crx_cc_a1_ability_v2
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability import (
    build_a1_ability,
    build_distress_signals,
    build_income_signals,
    build_liquidity_signals,
)
from .nodes import build_cc_liquidity_anchor

_OBS = "crx_cc_obs_base"


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
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
                build_distress_signals,
                [_OBS, "prm_bureau_alert_enriched"],
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
                "crx_cc_a1_ability_v2",
                name="build_crx_cc_a1_ability",
            ),
        ],
        tags=["crx_persona", "crx", "a1", "ability", "persona_axis"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/obs_base/__init__.py`
action: add · new sha256 `f9be618c051c28408fbce798c25df7dc7bd7def2df87515a1d50d365661d834d` · new trailing newline: yes

New:

`````python
"""Observation base: (account_id, observation_date, cif_id) per product."""

from .pipeline import create_cc_pipeline, create_rl_pipeline

__all__ = ["create_cc_pipeline", "create_rl_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/obs_base/pipeline.py`
action: add · new sha256 `d1b957c04ba57fea55b0e37a00af27c1bcf48f8ffb260500bb05c472e4541fdc` · new trailing newline: yes

New:

`````python
"""Kedro pipelines building the observation base every persona axis reads.

kedro run --pipeline=crx_cc_obs_base   (cc_60_180 / cc_180_plus)
kedro run --pipeline=crx_rl_obs_base   (rl_60_180 / rl_180_plus)
"""

from kedro.pipeline import Pipeline, node

from .._common import build_cc_obs_base, build_rl_obs_base


def create_cc_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_cc_obs_base,
                inputs=["cc_spine", "prm_contract", "prm_client"],
                outputs="crx_cc_obs_base",
                name="build_crx_cc_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
    )


def create_rl_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    return Pipeline(
        [
            node(
                func=build_rl_obs_base,
                inputs=["rl_spine"],
                outputs="crx_rl_obs_base",
                name="build_crx_rl_obs_base",
            )
        ],
        tags=["crx_persona", "crx", "obs_base"],
    )
`````

### FILE: `data/input/mirror_bundles/b01_a1_engine_check.py`
action: add · new sha256 `c7ceb6917f3bd6ad3219c1cdbd4f0aaef7c6d9d79fbb9d11d0f65b916432add0` · new trailing newline: yes

New:

`````python
"""Bundle 01 PROD check: CC A1 ability before vs after the shared-engine refactor.

Lives in data/input/mirror_bundles/ (gitignored) — never commit it. Run in a Kedro
notebook (``catalog`` defined):

    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
    from b01_a1_engine_check import main

    main(catalog, step="snapshot")  # BEFORE re-running A1: copies the current output
    # ... run crx_cc_obs_base and crx_cc_a1_ability_v2 ...
    main(catalog, step="compare")   # old vs new, prints the B01 OUTPUT block
    main(catalog, step="cleanup")   # deletes the snapshot copy

The snapshot is a parquet copy on HDFS next to the A1 output (``<path>__pre_b01``), so no
catalog entry is needed. Results (aggregates only) go to
data/input/mirror_bundles/results/.
"""

import datetime
import json
import pathlib
import re

DS = "crx_cc_a1_ability_v2"
GRAIN = ["account_id", "observation_date"]


def _dataset_path(catalog) -> str:
    """Filesystem path of the A1 output dataset (Kedro 0.18 / 0.19 / 1.x)."""
    getter = getattr(catalog, "_get_dataset", None) or getattr(catalog, "get", None)
    ds = getter(DS)
    for attr in ("_filepath", "filepath", "_path"):
        path = getattr(ds, attr, None)
        if path:
            return str(path).rstrip("/")
    raise RuntimeError(f"cannot read the filepath of {DS}; describe(): {ds._describe()}")


def _snapshot_path(catalog) -> str:
    return _dataset_path(catalog) + "__pre_b01"


def _counts(df, col):
    return {r[col]: r["count"] for r in df.groupBy(col).count().collect()}


def main(catalog, step="compare"):
    from pyspark.sql import functions as F

    model_id = catalog.load("params:model_id")  # ${globals:model_id}
    print(f"model_id={model_id}  step={step}")
    current = catalog.load(DS)
    spark = current.sparkSession
    snap = _snapshot_path(catalog)

    if step == "snapshot":
        if "a1_state_v2" not in current.columns:
            raise ValueError(f"{DS} already has the new schema — snapshot too late")
        current.select(*GRAIN, "a1_state_v2").write.mode("overwrite").parquet(snap)
        print(f"saved {spark.read.parquet(snap).count()} rows to {snap}")
        return None

    if step == "cleanup":
        jvm = spark.sparkContext._jvm
        path = jvm.org.apache.hadoop.fs.Path(snap)
        fs = path.getFileSystem(spark.sparkContext._jsc.hadoopConfiguration())
        print(f"deleted {snap}: {fs.delete(path, True)}")
        return None

    if "a1_state" not in current.columns:
        raise ValueError(f"{DS} still has the old schema — run the pipeline first")
    old = spark.read.parquet(snap).withColumnRenamed("a1_state_v2", "old_state")
    both = (
        current.select(
            *GRAIN,
            F.col("a1_state").alias("new_state"),
            "a1_income_level",
            "a1_liquidity_level",
        )
        .join(old, GRAIN, "full")
        .fillna({"old_state": "(absent)", "new_state": "(absent)"})
        .cache()
    )
    crosstab = [
        {"old": r["old_state"], "new": r["new_state"], "rows": r["count"]}
        for r in both.groupBy("old_state", "new_state")
        .count()
        .orderBy("old_state", "new_state")
        .collect()
    ]
    n = both.count()
    changed = both.filter(F.col("old_state") != F.col("new_state")).count()
    payload = {
        "task": "B01_a1_engine",
        "run_date": datetime.date.today().isoformat(),
        "model_id": model_id,
        "scope": f"{snap} (pre-refactor output) vs {DS} (shared engine)",
        "results": {
            "rows": n,
            "changed": changed,
            "changed_pct": round(100.0 * changed / max(n, 1), 2),
            "old_states": _counts(both, "old_state"),
            "new_states": _counts(both, "new_state"),
            "new_income_levels": _counts(both, "a1_income_level"),
            "new_liquidity_levels": _counts(both, "a1_liquidity_level"),
            "crosstab": crosstab,
        },
    }
    out = pathlib.Path(__file__).resolve().parent / "results"
    out.mkdir(parents=True, exist_ok=True)
    tag = re.sub(r"[^A-Za-z0-9]+", "_", str(model_id))
    path = out / f"B01_a1_engine_{tag}_{payload['run_date'].replace('-', '')}.json"
    path.write_text(json.dumps(payload, indent=2, default=str))

    print("=== B01 OUTPUT START ===")
    pct = payload["results"]["changed_pct"]
    print(f"model_id={model_id} rows={n} changed={changed} ({pct}%)")
    for name in ("new_income_levels", "new_liquidity_levels"):
        print(f"  {name}: {payload['results'][name]}")
    for row in crosstab:
        print(f"  {row['old']:<18} -> {row['new']:<18} {row['rows']:>9}")
    print("=== B01 OUTPUT END ===")
    print(f"written: {path}")
    return payload
`````

## Apply script

Written to `data/input/mirror_bundles/apply_bundle.py` by step 3.

`````python
"""Apply a mirror bundle (.md) to the workplace repo — safely.

Run from the workplace repo root:

    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --check
        -> dry run, changes nothing. Must end with "CHECK PASSED".
    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --apply
        -> writes the files, verifies them, compiles and imports every touched module.
           Must end with "APPLY PASSED".
    python docs/mirror_bundles/apply_bundle.py docs/mirror_bundles/<bundle>.md --revert
        -> puts every touched file back the way it was before --apply (uncommitted work only).

Safety rules:
  * every file the bundle replaces or deletes must be byte-identical (line endings aside) to
    the version the bundle was built from; otherwise nothing is written and the diff is
    printed. Someone else's edits are never overwritten.
  * refuses to write on main/master, or when a touched file has uncommitted changes.
  * the bundle carries a SHA-256 for every block, so a damaged copy (rendered instead of raw
    markdown, smart quotes, lost lines) is detected before anything is written.

Options: --no-import skips the import check (e.g. outside the dev container).
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

APPLY_VERSION = 2
PROTECTED_BRANCHES = {"main", "master"}
FENCE = re.compile(r"^(`{5,})")


def _norm(text: str) -> str:
    return text.replace("\r\n", "\n")


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


def file_status(e: dict) -> str:
    """One of: todo, done, conflict."""
    current = _read(pathlib.Path(e["path"]))
    cur_sha = None if current is None else _sha(current)
    if e["action"] == "add":
        if current is None:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    if e["action"] == "replace":
        if cur_sha == e["base_sha"]:
            return "todo"
        return "done" if cur_sha == e["new_sha"] else "conflict"
    # delete
    if current is None:
        return "done"
    return "todo" if cur_sha == e["base_sha"] else "conflict"


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
    diff = list(
        difflib.unified_diff(
            _norm(expected).splitlines(),
            _norm(current or "").splitlines(),
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


def print_table(entries: list[dict], statuses: list[str]) -> None:
    word = {"todo": "will apply", "done": "already applied", "conflict": "CONFLICT"}
    width = max(len(e["path"]) for e in entries)
    for e, s in zip(entries, statuses):
        print(f"  {e['action']:<8} {e['path']:<{width}}  {word[s]}")


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
        if s == "conflict":
            explain_conflict(e)
    for p in problems:
        print("REFUSED: " + p)
    n_conflict = statuses.count("conflict")
    ok = n_conflict == 0 and not problems
    print(
        f"\n{statuses.count('todo')} to apply, {statuses.count('done')} already applied, "
        f"{n_conflict} conflicts"
    )
    print("CHECK PASSED" if ok else "CHECK FAILED — nothing was written")
    if n_conflict:
        print(
            "A conflict means this repo's file differs from the version the bundle was "
            "built from. Do NOT hand-edit to force it: send the diff above back so the "
            "bundle can be rebuilt."
        )
    return ok


def cmd_apply(entries: list[dict], do_import: bool) -> bool:
    if not cmd_check(entries, quiet=True):
        return False
    for e in entries:
        if file_status(e) != "todo":
            continue
        path = pathlib.Path(e["path"])
        if e["action"] == "delete":
            path.unlink()
            _prune_empty_dirs(path.parent)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(e["new"].encode("utf-8"))
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
        elif cur_sha == e["new_sha"] or (e["action"] == "delete" and current is None):
            # prefer the committed bytes (keeps the repo's own line endings)
            committed = _head_version(e["path"])
            restore = committed if committed and _sha(committed) == e["base_sha"] else e["base"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(restore.encode("utf-8"))
        elif cur_sha != e["base_sha"]:
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
    args = ap.parse_args()

    md = pathlib.Path(args.bundle).read_text(encoding="utf-8")
    need = re.search(r"apply_bundle version: (\d+)", md)
    if need and int(need.group(1)) > APPLY_VERSION:
        print(f"This bundle needs apply_bundle.py version {need.group(1)}; you have "
              f"{APPLY_VERSION}. Recreate it from the bundle's 'Apply script' section.")
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

Copy this to the workplace assistant once the bundle's checks are done:

````text
Clean up after mirror bundle 01_a1_engine.md. Leave src/ and conf/ as they are, apart from
any temporary switch a step below asks you to make and undo.
- For each model_id that was checked (cc_60_180, cc_180_plus): set it in
  conf/dev/globals_dev.yml, then in a Kedro notebook delete the HDFS snapshot copy:
    import sys, pathlib
    _c = pathlib.Path.cwd()
    ROOT = next(p for p in [_c, *_c.parents] if (p / "conf").is_dir())
    sys.path.insert(0, str(ROOT / "data" / "input" / "mirror_bundles"))
    from b01_a1_engine_check import main
    main(catalog, step="cleanup")
  Restore model_id in globals_dev.yml to what it was before.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script, helpers, results):
  rm -rf data/input/mirror_bundles
- Run `git status` and confirm nothing under data/input/ is tracked or staged and
  that no other file changed. Report what you deleted.
````
