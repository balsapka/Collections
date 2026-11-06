# Mirror bundle 15 — Refactor R-A — delete dead persona code (departure signatures, payment trajectory, utilisation, old A2 nodes)

apply_bundle version: 7 · built 2026-11-06 from `2463964..7bdba03` · source: 2 added, 8 replaced, 12 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/persona_refactor
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/15_refactor_dead_code.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '15_refactor_dead_code.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/15_refactor_dead_code.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **Tests of deleted code.** Find every test under `src/tests/` that imports `cc_departure_signature`, `rl_departure_signature`, `cc_payment_trajectory`, `cc_utilisation`, `cc_a2_locatability.nodes`, `cc_a2_locatability.constants` or `rl_a2_locatability.nodes`. Delete tests of deleted code. A test of `build_rl_depart_spine` imports it from `crx_persona.rl_a4_spine.nodes` now. Run the remaining crx_persona tests; they must pass.
2. **Other readers.** `grep -rn` over `src` and `conf` for the deleted package names, the 20 removed datasets (`crx_cc_departure_*`, `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_rl_departure_signature`, `crx_rl_depart_travel_mcc`, `crx_rl_depart_foreign_signals`) and `parse_yyyymmdd`, `priority_reason`, `SEGMENTS`. Report any hit outside the tests; do not change it.

Then check: `kedro registry list` runs and lists `crx_rl_a4_spine_ra_check`, and none of the 4 removed pipelines.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Refactor R-A: delete dead persona code" && git push -u origin feature/persona_refactor
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/15_refactor_dead_code.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

**Step 7.** Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`. `crx_rl_a4_spine` from the last run is the baseline. Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a4_spine_ra_check
```

Paste back the block from `=== RA SPINE OUTPUT START ===` to `=== RA SPINE OUTPUT END ===`. Expected: the same rows old and new, `same schema: True`, 0 rows only in old and 0 only in new.

**Step 8.** Nothing else to run: no live output changes. Go on with the next bundle (the refactor) once the block is back.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Removes the persona code nothing runs any more, after the A1, A2 and A4 rebuilds. No live output changes. It is the first of three bundles applied in order: this one (dead code), then the refactor of the shared layer, A1, A2 and A4 (zero-difference checks), then the new A3.

- **Deleted packages and files:** `cc_departure_signature/`, `rl_departure_signature/` (except one function, below), `cc_payment_trajectory/`, `cc_utilisation/`, and the old A2 `cc_a2_locatability/nodes.py` + `constants.py` and `rl_a2_locatability/nodes.py` (orphaned since the A2 refactor; the wrappers call the `a2_locatability` engine).
- **Moved, unchanged:** `build_rl_depart_spine` moves from `rl_departure_signature/nodes.py` into `rl_a4_spine/nodes.py`, because `crx_rl_a4_spine` (read by A3) is built by it. Same code, same name, same output.
- **Removed from the registry:** the 4 pipelines of the deleted packages (`crx_cc_departure_signature`, `crx_rl_departure_signature`, `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`).
- **Removed from the catalog:** their 20 datasets (17 CC, 3 RL); the HDFS folders go in the cleanup.
- **Removed unused symbols:** `parse_yyyymmdd` (`_common`), `priority_reason` (`scoring_engine`), `SEGMENTS` (`_dpd_journey.constants`).
- **Not touched:** A3, `_dcore_codes.py`, `cc_raw_extract/`, the spell tables, every A1 / A2 / A4 node.
- **Check** (temporary): `crx_rl_a4_spine_ra_check` rebuilds the spine with the moved function and compares it with the current `crx_rl_a4_spine`. Expected: same row count, same schema, 0 rows only in either.

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
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/constants.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/ra_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/scoring_engine.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/constants.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_departure_signature/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_departure_signature/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_payment_trajectory/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_payment_trajectory/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_utilisation/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_utilisation/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `a615fe039248e50dfb840ff7afab5a39a1da0f08e5e8d0327887c6292c08d9d9` · base trailing newline: yes · new sha256 `ba11c14cedca684fcf059a49af8dad836833ffd6be4defc62c3b0aee9c5c886f` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `2b38b555b1ef366804002928de0679e04aabbd7a41cf55b12365c88c2fa79044` · base trailing newline: yes · new sha256 `91b45276a70a044eb43afb0b435b31c91cfd10289bd515156b8f9387c393c305` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/_common.py`
action: replace · base sha256 `00b6ff7d04506ecb3f1016d52106624eccca773bbaa8ae80f5302e56c305488c` · base trailing newline: yes · new sha256 `b8c83a80cdf936c922f9f545bcfd1699d77d188425b04d0cafd1e4391e83a08b` · new trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/__init__.py`
action: replace · base sha256 `b62c20a658aedee6fb8e3c6aecabe58f998528b9b760e0a01a1c636a19c14d88` · base trailing newline: yes · new sha256 `64b489bba62d8c19f4eb2540abd6a5fa24446b3c66445e4eacb505ba76b2a66d` · new trailing newline: yes

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
    constants.py  BucketScheme, CC, RL, SEGMENTS, MODEL_ID_SEGMENT
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
from .constants import CC, MODEL_ID_SEGMENT, RL, SEGMENTS, BucketScheme
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

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/constants.py`
action: replace · base sha256 `431988f16953ae1a9a9ecd62a8f4397564c944805090629f12d448e18e18de33` · base trailing newline: yes · new sha256 `7fdb29c788fb916fd1ea425dfda20f121d66c8d804afc8f7ac21a7ec0376ad58` · new trailing newline: yes

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

# Segments on the canonical scale.
SEGMENTS = {
    "60_180": (4, 5, 6, 7),  # CC native 4-7, RL native 3-6
    "180_plus": (8, 9),  # CC native 8-9, RL native 7
}

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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/__init__.py`
action: replace · base sha256 `5ca4d657ab1e964dca62e067af7be4d74e8e7469a597faa15cbf80f6a0cb5788` · base trailing newline: yes · new sha256 `437b464085ae47e6aba3fae58634e7e491004bfdcd05ba7ca4b454313750af11` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A4 Spine — structural spine/spell window projection for Retail Loans.

Inputs: rl_spine, crx_rl_spell_table
Output: crx_rl_a4_spine
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A4 Spine — structural spine/spell window projection for Retail Loans.

Inputs: rl_spine, crx_rl_spell_table
Output: crx_rl_a4_spine
"""

from .pipeline import create_pipeline, create_ra_check_pipeline

__all__ = ["create_pipeline", "create_ra_check_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/nodes.py`
action: add · new sha256 `23c4fbc9c0bb26c66dd3348626a0102d1c55debdb5583d76eb669622c7349897` · new trailing newline: yes

New:

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
action: replace · base sha256 `b912a37a44ac2cee38becaa7a94620ec56c18235e2b8ef7bd241b2c9ec9be784` · base trailing newline: yes · new sha256 `3d546001a76bc6ede13f3d9f538cf950f7891d285f2caa08d351965141f22af9` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A4 Spine — structural spine/spell window projection.

Replaces rl_a4_class's Node 2 (build_rl_a4_spine_projection), which broadcast a
now-superseded CASA/EMI classification onto the spine. crx_rl_a4_spine is now
a pure structural join — (account_id, cif_id, observation_date, spell_id, t0),
decoupled from any A4 classifier, scoped by crx_rl_a4_deterioration instead.

Reuses rl_departure_signature's build_rl_depart_spine (R14 — identical logic,
already exercised by that pipeline) rather than re-deriving the same join.

Run with:
    kedro run --pipeline=crx_rl_a4_spine
"""

from kedro.pipeline import Pipeline, node

from ..rl_departure_signature.nodes import build_rl_depart_spine

_TAGS = ["crx", "rl", "rl_a4_spine"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """One-node pipeline: rl_spine + crx_rl_spell_table -> crx_rl_a4_spine."""
    return Pipeline(
        [
            node(
                func=build_rl_depart_spine,
                inputs=[
                    "rl_spine",
                    "crx_rl_spell_table",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a4_spine",
                name="build_crx_rl_a4_spine",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL A4 Spine — structural spine/spell window projection.

Replaces rl_a4_class's Node 2 (build_rl_a4_spine_projection), which broadcast a
now-superseded CASA/EMI classification onto the spine. crx_rl_a4_spine is now
a pure structural join — (account_id, cif_id, observation_date, spell_id, t0),
decoupled from any A4 classifier, scoped by crx_rl_a4_deterioration instead.

Run with:
    kedro run --pipeline=crx_rl_a4_spine

TEMPORARY (refactor bundle R-A): ``create_ra_check_pipeline`` rebuilds the spine into
``crx_rl_a4_spine_ra_check`` and compares it with ``crx_rl_a4_spine``; removed by the
bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_rl_depart_spine
from .ra_check import compare_rl_a4_spine

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


def create_ra_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the spine into crx_rl_a4_spine_ra_check, then old vs new (bundle R-A)."""
    return Pipeline(
        [
            _spine_node("crx_rl_a4_spine_ra_check"),
            node(
                func=compare_rl_a4_spine,
                inputs={
                    "old": "crx_rl_a4_spine",
                    "new": "crx_rl_a4_spine_ra_check",
                    "model_id": "params:model_id",
                },
                outputs=None,
                name="compare_crx_rl_a4_spine_ra",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a4_spine/ra_check.py`
action: add · new sha256 `2b92a63b61d45ed1bd831e8a85e2a3a2dcb3580cddc938a7d7247df55636c3ab` · new trailing newline: yes

New:

`````python
"""TEMPORARY (refactor bundle R-A): the moved ``build_rl_depart_spine`` must rebuild
``crx_rl_a4_spine`` exactly. Logs one block; removed by the bundle's cleanup."""

import logging

from pyspark.sql import DataFrame

logger = logging.getLogger(__name__)


def compare_rl_a4_spine(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Row counts, schema and rows in one output but not the other (``exceptAll``)."""
    same_schema = old.schema.simpleString() == new.schema.simpleString()
    cols = old.columns
    lines = [
        f"model_id: {model_id}",
        f"rows old / new: {old.count()} / {new.count()}",
        f"same schema: {same_schema}",
    ]
    if same_schema:
        lines += [
            f"rows only in old: {old.exceptAll(new.select(*cols)).count()}",
            f"rows only in new: {new.select(*cols).exceptAll(old).count()}",
        ]
    else:
        lines += [
            f"old: {old.schema.simpleString()}",
            f"new: {new.schema.simpleString()}",
        ]
    block = "\n".join(lines)
    logger.info(
        "\n=== RA SPINE OUTPUT START ===\n%s\n=== RA SPINE OUTPUT END ===", block
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/scoring_engine.py`
action: replace · base sha256 `28012d415d25e4b62b0ea9deb52bef5819eaa222af1eec2d5898648862089c89` · base trailing newline: yes · new sha256 `b2a6f15da8227b4892e68817c2503d58f629b66ea32e6fd94f168885d1282dd2` · new trailing newline: yes

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
from typing import Mapping, Sequence

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


def priority_reason(
    conditions: Mapping[str, Column], priority_high_to_low: Sequence[str]
) -> Column:
    """Pick the single highest-priority named condition that fires, else NULL.

    ``conditions`` maps a reason name to its boolean Column. ``priority_high_to_low``
    must list every key in ``conditions``, most important first — when more
    than one condition fires for the same row, the first (highest-priority)
    match wins.
    """
    expr = F.lit(None).cast("string")
    for reason in reversed(priority_high_to_low):
        expr = F.when(conditions[reason], F.lit(reason)).otherwise(expr)
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/constants.py`
action: delete · base sha256 `c44565988cce642443abf2cee295e763ec98986b3107c8d4fbf2127f4902eaf2` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""DCORE result description allowlists for the cc_a2_locatability pipeline.

Centralised here so that result-name allowlists can be inspected and updated
without navigating node logic.

All allowlists use result_name (szresultname), carried directly on
dcore_prm_followup_outcomes — not result_code — because descriptions are
self-documenting and stable across DCORE deployments.

Constants:
    _RIGHT_PARTY_CONTACT_RESULT_NAMES  — confirmed two-way contact (any channel)
    _REFUSING_RESULT_NAMES             — explicit refusal/hang-up/dispute signals
    _RINGING_RESULT_NAMES              — ringing no-answer (live channel, no pickup)
    _DECEASED_RESULT_NAMES             — confirmed or claimed deceased
    _DEPARTURE_RESULT_NAMES            — contact record states customer left UAE
    _FIELD_VISIT_RESULT_NAMES          — completed field visits only
    _HARDSHIP_RESULT_NAMES             — hardship / special-case signals
    _PROMISE_TO_PAY_RESULT_NAMES       — PTP and payment commitments
    _NOT_REACHABLE_RESULT_NAMES        — structurally invalid/dead contact info
    _RETAIN_PTP_RESULT_NAMES           — customer honoured/maintained an existing PTP
    _PAYMENT_CONFIRMED_RESULT_NAMES    — confirmed completed payment (not a promise)
"""

# Comprehensive right-party contact (RPC) set — every result_name that confirms
# the account holder was personally reached, regardless of result_category.
# Covers: payment commitments (PTP), payments made, verbal engagement/refusal,
# customer-disclosed circumstances, customer-initiated requests, and physical
# field-visit contact.
# Excludes: third-party messages, scheduling/routing notes, administrative
# referrals, system/technical codes, deceased status, and dunning letters.
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(_RIGHT_PARTY_CONTACT_RESULT_NAMES)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RIGHT_PARTY_CONTACT_RESULT_NAMES = {
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


# Explicit refusal signals — result names where confirmed right-party contact was
# made but the customer explicitly refused, hung up, or disputed.
# Subset of _RIGHT_PARTY_CONTACT_RESULT_NAMES (every entry here also confirms contact).
# Excludes settlement-seeking behaviour (engagement) and autodialler intermediates.
#
# Drives refusing_n counter → non_cooperative state (confirmed contact + refusal).
#
# Matching must normalise the source column first:
#   result_name_upper = F.upper(F.trim(F.col("result_name")))
#   result_name_upper.isin(_REFUSING_RESULT_NAMES)
#
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_REFUSING_RESULT_NAMES = {
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

# Ringing no-answer signals — phone rang at the customer end but was not answered.
# Excludes LINE BUSY (transient, does not indicate call screening).
# Drives ringing_n counter → avoiding state when ≥3 ringing events and line is live.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RINGING_RESULT_NAMES = {
    "RINGING NO REPLY",
    "RINGING NO RESPONSE",
}

# Confirmed or claimed deceased — drives deceased_flag → highest-priority state.
# Retained in _HARDSHIP_RESULT_NAMES as well (hardship_flag still used for routing).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_DECEASED_RESULT_NAMES = {
    "DECEASED",
    "DECEASED CLAIMED",
    "DECEASED OR EXPIRED",
    "DECEASED/EXPIRED",
    "KSA/DECEASED",
}

# Contact records explicitly stating customer has left UAE.
# Contributes to dcore_departure_flag — additional departure evidence
# from within the delinquency window.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_DEPARTURE_RESULT_NAMES = {
    "KSA/NATHEER-CROSSING FINAL EXIT VISA",
    "LEFT THE COUNTRY",
    "OUT OF COUNTRY",
}

# Completed field visit — excluded from phone rpc_n; tracked via field_visit_flag.
# Scheduling/workflow events (FIELD VISIT REJECTED/SENT/RE FIELD VISIT REQUIRED/
# REQUEST FOR FIELD VISIT) are excluded — they do not confirm contact.
# Note: FIELD VISIT DONE is also in _RIGHT_PARTY_CONTACT_RESULT_NAMES, so it
# contributes to contact_confirmed_n automatically.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_FIELD_VISIT_RESULT_NAMES = {
    "FIELD VISIT DONE",
}

# Hardship / special cases — accounts requiring non-standard treatment.
# Covers: death (confirmed and claimed), permanent disability, incarceration,
# bankruptcy, employment loss/termination, and income hardship signals.
# Flag separately — do not count as regular unreachable or RPC.
# Includes KSA-channel equivalents and additional signals from the data
# not in the reference doc (MEDICAL ISSUES, SALARY DELAY, UNPAID LEAVE).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_HARDSHIP_RESULT_NAMES = {
    "BANKRUPTCY",
    "CUSTOMER HAVE NO JOB",
    "CUSTOMER IS IN JAIL",
    "CUSTOMER IS PERMANENT DISABLED",
    "CUSTOMER TERMINATED",
    "DECEASED",
    "DECEASED CLAIMED",
    "DECEASED OR EXPIRED",
    "DECEASED/EXPIRED",
    "JOB LOST",
    "KSA/DECEASED",
    "KSA/DISABLED",
    "KSA/JOB LOST",
    "LEFT JOB",
    "MEDICAL ISSUES",
    "NIL SALARY",
    "SALARY DELAY",
    "SALARY REDUCTION",
    "UNPAID LEAVE",
}

# Promise to pay or willingness to pay — result names signalling the customer
# has committed to pay, made a payment arrangement, or actually paid.
# Covers: all PTP-category outcomes, actual payments (SUC), and INT entries
# where the customer verbally committed or agreed to a specific arrangement
# (balance consolidation, rewrite, deferment, settlement, salary-date promise).
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_PROMISE_TO_PAY_RESULT_NAMES = {
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

# Customer is fundamentally unreachable — wrong/invalid number, line
# permanently dead/disconnected, or explicitly flagged uncontactable.
# Signals a structural contact barrier, not a single failed attempt.
# Excludes: transient failures (no answer, busy, disconnected call,
# voicemail, message left) — those only mean the customer didn't pick up
# this time, not that they are unreachable.
# Covers both autodialler (ININ-OUTBOUND-*) and manual/KSA-channel outcomes.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_NOT_REACHABLE_RESULT_NAMES = {
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

# Customer honoured or is actively maintaining an existing promise-to-pay — a
# stronger/narrower signal than generic _PROMISE_TO_PAY_RESULT_NAMES. Not restricted to
# a particular action_code: in practice RETAIN PTP is logged administratively (action_code
# IA) rather than against a live call, so consumers must not pre-filter to call-type
# action codes before matching this set.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_RETAIN_PTP_RESULT_NAMES = {
    "CUSTOMER KEPT PROMISE MADE",
    "RETAIN PTP",
}

# Confirmed completed payment — distinct from a promise/commitment (_PROMISE_TO_PAY_
# RESULT_NAMES) or an unverified claim of payment ("CLAIMS MADE PAYMENT", which stays
# PTP-classified). Drives a dedicated "paid" disposition, separate from PTP.
# Values: upper-cased, leading/trailing whitespace stripped, sorted ASC.
_PAYMENT_CONFIRMED_RESULT_NAMES = {
    "ACCOUNT PAID",
    "CUSTOMER MADE PAYMENT",
}
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/nodes.py`
action: delete · base sha256 `1762a3a8f6e853e4dc6860da097e264fdd769fe488c67580d931b0398dd8ee20` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A2 Locatability axis — location x reachability (2-dimension cross).

# pylint: disable=too-many-locals, too-many-statements, too-many-lines

Build functions:
    build_a2_base(cc_spine, crx_cc_spell_table, crx_cc_departure_signature)
        -> crx_cc_a2_base

    build_a2_login_presence(crx_cc_a2_base, prm_digital_login_monthly)
        -> crx_cc_a2_login_presence

    build_a2_contact_signals(crx_cc_a2_base, dcore_observation_spine,
                             dcore_prm_followup_outcomes)
        -> crx_cc_a2_contact_signals

    build_a2_locatability(crx_cc_a2_base, crx_cc_a2_login_presence,
                          crx_cc_a2_contact_signals, model_id,
                          prm_contract=None, prm_client=None,
                          feat_demographics_cif=None)
        -> crx_cc_a2_locatability   <- shipped persona axis

Provenance: T12 (2026-09) shipped a 7-state contact-outcome x presence waterfall
(deceased | non_cooperative | reachable | avoiding | skip | gone | unknown). GRR
feedback (data/input/Axes and States for UC2 - Cards 61-180.xlsx, sheet "A1, A2, A4",
rows 8-14) asked for a simpler 2-dimension cross instead -- T29 built that redesign as a
parallel, additive pipeline (cc_a2_locatability_v2, R18) beside T12 so the two could be
compared before any integration decision (see
docs/context/results/MASTER_SUMMARY_a2_locatability_v2_20261012.md). The user has now
promoted T29's design to the shipped A2 derivation (2026-10-22) -- T12's 7-state
waterfall is retired (RESULTS.md). Node 4 below is T29's derivation ported in place of
T12's; Nodes 1-3 are unchanged -- T29 always consumed them read-only and never needed its
own copies.

Goal -- assign each (account_id, observation_date) a location x reachability pair:

    Location      in {Skip, In Country, Unknown}          -- presence evidence only
    Reachability  in {Reachable, Non-Reachable, Unknown} -- RPC-established condition

Location must be derived *purely* from departure_trail_flag / in_country_flag (login,
digital footprints, transactions) -- never mixed with any conversational/contact-outcome
condition. Reachability keeps T12's spirit but collapses the old non_cooperative/avoiding
split into a plain binary (confirmed contact vs. confirmed dead). Deceased stays a
separate pre-guard state; as of T34 (2026-10-12) the flag it fires on is
deceased_flag_v2, a corroborated combination rather than DCORE alone (see "Deceased
corroboration" below).

**Model-agnostic, shared across CC and RL.** build_a2_locatability is the one and only
state-derivation function for this axis -- RL's rl_a2_locatability pipeline imports it
directly from this module rather than duplicating it. Only the *upstream* intermediates
differ by domain (crx_rl_a2_base/crx_rl_a2_login_presence/crx_rl_a2_contact_signals,
schema-identical to CC's own intermediates); the location x reachability cross itself is
identical regardless of domain. The _TAU_RECENT_D_BY_MODEL_ID/_TAU_LABEL_D_BY_MODEL_ID
dicts below carry all four model_ids (cc_60_180, cc_180_plus, rl_60_180, rl_180_plus).

State rules (first match wins):
    1. deceased_flag_v2=1                                          -> Deceased
       (pre-guard, absolute first priority; deceased_flag_v2 = deceased_flag OR
        way4_deceased_flag OR demographics_deceased_flag -- T34)
    2. location_state:
        departure_trail_flag=1 AND in_country_flag=0              -> Skip
        in_country_flag=1                                          -> In Country
          (recent in-country evidence wins over a stale departure trail)
        otherwise (both flags 0)                                   -> Unknown
    3. reachability_state:
        guard: contact_attempts_n < _TAU_A_ATTEMPTS, or
        label_event_gap_d > _TAU_LABEL_D (model_id-resolved), or
        either NULL                                                -> Unknown
        recent_avoidance_flag=1                                    -> Non-Reachable
          (2026-10-22 amendment -- downgrades a lifetime-established confirmed
          contact when the last _TAU_RECENT_AVOIDANCE_N outbound attempts were ALL
          ringing/no-answer, zero confirmed among them, and recent -- see below.
          Checked BEFORE contact_confirmed_flag so a stale historical RPC cannot
          outrank a fresh, consistent avoidance pattern.)
        contact_confirmed_flag=1                                   -> Reachable
          (absorbs T12's non_cooperative -- contact was made, refusal or not;
          this is a LIFETIME count over [t0, obs) -- see recent_avoidance_flag
          above for the recency override)
        gone_contact_flag=1 AND last_attempt_contact_flag=0        -> Non-Reachable
          (absorbs T12's avoiding -- last-N attempts all dead-or-ringing, no
          confirmed contact, and the single most recent call-type action was not
          itself a confirmed contact)
        otherwise                                                  -> Unknown
    4. a2_state = "Deceased" if deceased_flag_v2=1, else
                  f"{location_state} - {reachability_state}"

location_state and reachability_state are emitted as their own columns (not just folded
into a2_state) so a consumer can cut by either dimension independently. Both are computed
unconditionally from the signals, even on deceased rows.

Segment-aware thresholds (amendment, 2026-10-08, ratified against T29's EDA): the
2026-10-07 T29 EDA run found location_state saturates to Unknown at 90.37% for
cc_180_plus under a flat 90-day _TAU_RECENT_D -- that segment's documented thinner
digital/contact cadence (T12b: 11.54% pre-obs login coverage). Both the location-recency
window (_TAU_RECENT_D) and the reachability staleness guard (_TAU_LABEL_D) vary by
model_id:

    _TAU_RECENT_D_BY_MODEL_ID = {"cc_60_180": 90, "cc_180_plus": 180,
                                 "rl_60_180": 90, "rl_180_plus": 180}  # days
    _TAU_LABEL_D_BY_MODEL_ID  = {"cc_60_180": 90, "cc_180_plus": 180,
                                 "rl_60_180": 90, "rl_180_plus": 180}  # days

Any model_id not in these dicts falls back to the 90-day default (fail soft, not hard --
see _resolve_tau). _TAU_A_ATTEMPTS is a count, not a time window, and stays flat at 3 for
every segment.

Reachability recency override -- recent_avoidance_flag (amendment, 2026-10-22): as shipped
2026-10-22, contact_confirmed_flag is a LIFETIME count over [t0, obs) -- once any contact is
confirmed anywhere in the delinquency spell, the account is Reachable for the rest of the
spell, even if every attempt since has gone dead/unanswered (gone_contact_flag is windowed
to the last _TAU_NOT_REACHABLE_N=2 attempts, but is only ever evaluated when
contact_confirmed_flag=0, so it can never override a historical confirmed contact). The user
asked for this fixed: Reachable should downgrade to Non-Reachable when the customer has gone
dark recently, not just when they were never reached at all. recent_avoidance_flag fires when
the last _TAU_RECENT_AVOIDANCE_N=3 distinct outbound attempt dates were ALL ringing/no-answer
(the T12 "avoiding" signal -- line confirmed live, no pickup; deliberately NOT mixed with
dead/invalid-number outcomes, which is a different failure mode), zero confirmed contact
among those 3, and the oldest of those 3 attempts is still within tau_label_d (the same
segment-aware staleness window as the 4.4c guard -- 90d for *_60_180, 180d for *_180_plus) of
observation_date. It is checked ahead of contact_confirmed_flag in the reachability_state
waterfall, so a fresh 3-strike avoidance run overrides a stale historical RPC. Computed from
a second chronologically-ranked window in build_a2_contact_signals (Step 5c), parallel to the
existing _TAU_NOT_REACHABLE_N=2 window that feeds not_reachable_flag/gone_contact_flag (Step
5b) -- the two windows are independent and intentionally different sizes (2 for the
never-confirmed path, 3 for the recency-override path, per the user's explicit threshold).

Deceased corroboration -- CC/RL asymmetry (T34, 2026-10-12): deceased_flag was DCORE-only
until this amendment. PROD evidence on cc_60_180 found Way4 block code block_code_2='D'
catches 36 accounts (81.8% of DCORE's own count) that DCORE missed -- material,
OR-combined in. For cc_180_plus, prm_contract matched zero rows for that snapshot (a
join-reach anomaly, not an absent code -- see RESULTS.md Proposed amendments); the
Way4/demographics terms are harmlessly 0 there. Both terms are wired **data-driven, not
domain-branched**: Way4 (prm_contract.block_code_1/block_code_2) activates only when
prm_contract is supplied *and* carries those columns -- CC-only, since RL has no
Way4-equivalent block-code table anywhere in its data model (grep-confirmed).
Demographics (feat_demographics_cif.ft_deceased_flag) activates whenever a cif_id is
resolvable: RL's crx_rl_a2_base already carries cif_id directly (no bridge needed), while
CC's crx_cc_a2_base does not, so CC must also supply prm_contract+prm_client to build the
bridge (_build_cif_bridge) before demographics can join. Net effect: CC's pipeline wires
Way4 + demographics; RL's pipeline wires demographics only (no Way4 inputs supplied --
prm_contract/prm_client stay None).

Design decisions (Nodes 1-3, unchanged since T12):
  - cc_spine is the grain anchor -- already model_id-scoped via Kedro namespace.
    No segment filter via max_dpd_so_far is needed or correct here.
  - Departure trail columns reused from crx_cc_departure_signature (T06, R14).
    Only the obs-anchored login presence is new here.
  - Schema guard in build_a2_contact_signals: empty/missing DCORE -> all-NULL /
    zero contact signals; state derivation handles NULL gracefully -> Unknown.
  - rpc_rate is now (rpc_n + rpc_proxy_n) / contact_attempts_n -- includes
    result descriptions miscategorised as INT/UNS (e.g. "REFUSED TO PAY" = INT).
  - contact_confirmed_n = _rpc_n + _rpc_proxy_n -- channel-agnostic confirmed
    contact count; used by the reachability derivation.
  - result_name-based allowlists used throughout -- self-documenting and stable
    across DCORE deployments; carried directly on dcore_prm_followup_outcomes.
  - Field visit events: only FIELD VISIT DONE counts as contact confirmation.
    Scheduling events (SENT/REJECTED/REQUEST) do not confirm contact.
  - not_reachable_flag fires when the last _TAU_NOT_REACHABLE_N distinct outbound
    attempt dates all produced dead/unconnected outcomes with no confirmed contact.
    Accounts with fewer than _TAU_NOT_REACHABLE_N distinct attempt dates fall
    through to the reachability guard anyway. not_reachable_n (total count) is
    kept in the output for diagnostics.
  - gone_contact_flag fires when the last _TAU_NOT_REACHABLE_N outbound dates were
    all dead OR ringing, no confirmed contact -- shared denominator with
    not_reachable_flag, different numerator (dead only vs. dead-or-ringing).
"""

# pylint: disable=too-many-lines
import datetime
import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.constants import (
    _DECEASED_RESULT_NAMES,
    _DEPARTURE_RESULT_NAMES,
    _FIELD_VISIT_RESULT_NAMES,
    _HARDSHIP_RESULT_NAMES,
    _NOT_REACHABLE_RESULT_NAMES,
    _PROMISE_TO_PAY_RESULT_NAMES,
    _REFUSING_RESULT_NAMES,
    _RIGHT_PARTY_CONTACT_RESULT_NAMES,
    _RINGING_RESULT_NAMES,
)
from enbd_collections.pipelines.crx_persona._spine_utils import (
    _build_cif_bridge,
    join_spine_to_spell,
)

LOG = logging.getLogger(__name__)

# ── Guard threshold shared with Node 3's chronological skip/gone check ─────────
_TAU_NOT_REACHABLE_N = (
    2  # skip + gone: last N outbound attempt dates checked chronologically  [CONFIRM]
    # skip requires all N dead; gone_contact_flag requires all N dead OR ringing.
)

# ── Guard threshold for the recent-avoidance override (2026-10-22 amendment) ──
_TAU_RECENT_AVOIDANCE_N = (
    3  # reachability override: last N outbound attempt dates checked chronologically.
    # Downgrades a lifetime-established Reachable state (contact_confirmed_n > 0
    # somewhere in [t0, obs)) to Non-Reachable when the most recent N attempts were
    # ALL ringing/no-answer ("avoiding" — line confirmed live, no pickup, no dead/
    # invalid-number mix) AND fall within the segment's tau_label recency window.
    # See build_a2_locatability Step 4b (recent_avoidance_flag).
)

# ── Node 4 guard thresholds — ported from T29 (cc_a2_locatability_v2) ─────────
# §4.4b: reachability Unknown if contact_attempts_n < this. A flat count, not a
# time window — stays the same across every model_id (unlike the two dicts below).
_TAU_A_ATTEMPTS = 3

# Segment-aware recency windows (amendment, 2026-10-08). cc_180_plus's documented
# thinner digital/contact cadence (T12b: 11.54% pre-obs login coverage) saturates
# location_state to Unknown at 90.37% under the flat 90d window — widened to 180d
# (6m) for that segment. The same thin-cadence argument applies to the
# reachability staleness guard. Default (90d) covers any model_id not listed here
# — fail soft, not hard.
_TAU_RECENT_D_BY_MODEL_ID = {  # in_country: login within this many days of obs_date
    "cc_60_180": 90,
    "cc_180_plus": 180,
    "rl_60_180": 90,
    "rl_180_plus": 180,
}
_TAU_LABEL_D_BY_MODEL_ID = (
    {  # §4.4c: reachability Unknown if contact evidence is this stale
        "cc_60_180": 90,
        "cc_180_plus": 180,
        "rl_60_180": 90,
        "rl_180_plus": 180,
    }
)
_TAU_DEFAULT_D = 90

# Way4 block-code deceased signal — CC-only (no RL equivalent exists). T34, PROD
# discovery 2026-10-12: confirmed on block_code_2 for cc_60_180 (47/19,292 rows);
# block_code_1 never carries it in either segment observed. Checked defensively on
# both columns — org-specific suffix patterns (BLOCK_CODE_ACC1_%/BLOCK_CODE_ACC2_%)
# mean this could in principle appear on either.
_WAY4_DECEASED_BLOCK_CODES = {"D"}


def _resolve_tau(model_id: str, tau_by_model_id: dict) -> int:
    """Segment-aware tau lookup with a soft default (never raises on an unknown id)."""
    return tau_by_model_id.get(model_id, _TAU_DEFAULT_D)


# ── Departure trail columns reused from T06 (R14 — never re-derive) ───────────
_DEPART_COLS = [
    "account_id",
    "spell_id",
    "travel_mcc_flag_h2",  # Pass A — travel MCC in H2 pre-T0
    "last_txn_foreign_flag",  # Pass A — last W_pre txn was international
    "foreign_login_flag",  # Pass J — most recent login before spine_obs_date is foreign
    "casa_inflow_stop_gap_d",  # Pass B — CASA salary stop gap (days)
]

# ── DCORE call action codes ──────────────────────────────────────────────────
_OUTBOUND_CODES = ["OC", "CB"]  # outbound call / callback attempt (we initiated)
_INBOUND_CODES = ["IC"]  # inbound call — customer called us (confirmed 2026-09-11)
_CALL_CODES = (
    _OUTBOUND_CODES + _INBOUND_CODES
)  # OC, CB, IC — real dial/call events only


# ── Node 1: build_a2_base ────────────────────────────────────────────────────


def build_a2_base(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    departure_sig: DataFrame,
) -> DataFrame:
    """Attach spell window + departure trail columns to the spine grain.

    Uses cc_spine as the grain anchor — it is already model_id-scoped
    (cc_60_180 spine contains only 60-180 DPD accounts; cc_180_plus spine
    contains only 180+ accounts).  No segment filter via max_dpd_so_far
    is needed or correct here.

    Joins spell_table only to obtain t0 and spell_id for feature windows.
    Then attaches reusable departure trail columns from T06 (R14 — do not
    re-derive what T06 already built).

    Args:
        cc_spine:      Model-id-scoped spine; grain (account_id, observation_date).
            Required cols: account_id (= contract_id), observation_date.
        spell_table:   crx_cc_spell_table; grain (account_id, spell_id).
            Required cols: account_id, spell_id, t0, spell_end.
        departure_sig: crx_cc_departure_signature (T06); grain (account_id, spell_id).
            Required cols: _DEPART_COLS.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id            (string)
            observation_date      (date)
            spell_id              (int)
            t0                    (date)
            cif_id                (string)
            travel_mcc_flag_h2    (int)
            last_txn_foreign_flag (int)
            foreign_login_flag    (int)
            casa_inflow_stop_gap_d (double)
    """
    # ── Step 1: join spine to spell_table to get t0 / spell_id ──────────────
    # Shared utility — equality join + date filters (same pattern as A1, A4).
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    # Recover cif_id from cc_spine (dropped by join_spine_to_spell).
    spine_cif = cc_spine.select(
        F.col("contract_id").cast("string").alias("_cid"),
        F.col("cif_id").cast("string"),
    )
    spine_with_spell = spine_with_spell.join(
        spine_cif, on=spine_with_spell["account_id"] == spine_cif["_cid"], how="left"
    ).drop("_cid")

    # ── Step 2: attach departure signature columns (T06 reuse, R14) ──────────
    base = spine_with_spell.join(
        departure_sig.select(*_DEPART_COLS),
        on=["account_id", "spell_id"],
        how="left",
    )

    n_rows = base.count()
    n_with_spell = base.filter(F.col("spell_id").isNotNull()).count()
    n_with_depart = base.filter(F.col("travel_mcc_flag_h2").isNotNull()).count()
    LOG.info(
        "build_a2_base: %d rows | spell join: %d (%.1f%%) | departure trail: %d (%.1f%%)",
        n_rows,
        n_with_spell,
        100.0 * n_with_spell / max(n_rows, 1),
        n_with_depart,
        100.0 * n_with_depart / max(n_rows, 1),
    )

    return base


# ── Node 2: build_a2_login_presence ──────────────────────────────────────────


def build_a2_login_presence(  # pylint: disable=too-many-locals
    base: DataFrame,
    prm_login: DataFrame,
    obs_month_end: bool = False,
) -> DataFrame:
    """Derive obs-anchored digital presence signals.

    A single PIT join is computed from the login table:

    1. Current presence (obs-date anchor): most recent login month strictly
       before trunc(observation_date, 'month') when obs_month_end=False
       (default — CC mid-month observations).  Use obs_month_end=True for
       month-end observation dates (retail loans, or CC if it ever moves
       to month-end) — the observation month is fully closed so <= is safe.

    Args:
        base:          crx_cc_a2_base; grain (account_id, observation_date).
            Required cols: account_id, observation_date, t0, cif_id.
            cif_id is propagated from build_a2_base — no PRM bridge needed.
        prm_login:     prm_digital_login_monthly — monthly login records per cif.
            Required cols: cif_id, month_number (yyyyMMdd string),
            last_login_date, last_login_foreign_flag,
            last_login_country, last_login_countrycode.
        obs_month_end: If True, include the observation month itself in the
                       PIT window (safe only when observation_date is the last
                       day of the month).  Default False (CC mid-month).

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id              (string)
            observation_date        (date)
            last_login_date         (date;   NULL if no pre-obs login found)
            last_digital_login_gap_d (int;   days; NULL if no login)
            last_login_foreign_flag (int;    0/1;  NULL if no login)
            last_login_country      (string; NULL if no login)
    """
    # ── Parse month_number string → date ──────────────────────────────────────
    prm_dated = prm_login.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    )

    # ── Base with CIF for obs-date join ───────────────────────────────────────
    base_with_cif = base.select("account_id", "observation_date", "cif_id").join(
        prm_dated.select(
            "cif_id",
            "_month_date",
            "last_login_date",
            "last_login_foreign_flag",
            "last_login_country",
            "last_login_countrycode",
        ),
        on="cif_id",
        how="inner",
    )

    # ── Join 1: current presence — latest login before trunc(obs, 'month') ─────
    # obs_month_end=False (CC default): exclude observation month — partial calendar
    #   month would introduce look-ahead for mid-month observation dates.
    # obs_month_end=True  (retail loans, or CC if moved to month-end): include it —
    #   the month is fully closed when observation_date is month-end.
    _obs_cutoff = F.trunc(F.col("observation_date"), "month")
    _obs_filter = (
        F.col("_month_date") <= _obs_cutoff
        if obs_month_end
        else F.col("_month_date") < _obs_cutoff
    )
    w_obs = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("_month_date").desc()
    )
    latest_obs = (
        base_with_cif.filter(_obs_filter)
        .withColumn("_rn", F.row_number().over(w_obs))
        .filter(F.col("_rn") == 1)
        .withColumn(
            "last_digital_login_gap_d",
            F.datediff(F.col("observation_date"), F.col("last_login_date")),
        )
        .select(
            "account_id",
            "observation_date",
            "last_login_date",
            "last_digital_login_gap_d",
            "last_login_foreign_flag",
            "last_login_country",
        )
    )

    # ── Left-join back to all base pairs (no login → NULLs) ───────────────────
    result = base.select("account_id", "observation_date").join(
        latest_obs, on=["account_id", "observation_date"], how="left"
    )

    n_rows = result.count()
    n_with_login = result.filter(F.col("last_login_date").isNotNull()).count()
    LOG.info(
        "build_a2_login_presence: %d rows | obs login: %d (%.1f%%)",
        n_rows,
        n_with_login,
        100.0 * n_with_login / max(n_rows, 1),
    )

    return result


# ── Node 3: build_a2_contact_signals ─────────────────────────────────────────


def build_a2_contact_signals(  # pylint: disable=too-many-locals
    base: DataFrame,
    observation_spine: DataFrame,
    followup: DataFrame,
) -> DataFrame:
    """Derive attempt-normalised contact signals from DCORE.

    Window: [t0, observation_date) — entire delinquency window to obs.
    All rates are normalised over contact_attempts_n (§4.4b denominator).

    result_name allowlists (carried directly on dcore_prm_followup_outcomes)
    are used for fine-grained signal classification:
      - rpc_proxy_n:         RPC events miscategorised as INT/UNS (e.g. REFUSED TO PAY)
      - refusing_n:          Explicit refusal/hang-up/dispute (non_cooperative signal)
      - ringing_n:           Ringing no-answer events (avoiding signal; ≥3 required)
      - deceased_flag:       Confirmed or claimed deceased (highest-priority state)
      - contact_confirmed_n: Channel-agnostic confirmed contact (_rpc_n + _rpc_proxy_n)
      - dcore_departure_n:   Contact record explicitly states customer left UAE
      - field_visit_n:       Completed field visits only (excluded from phone rpc_n)
      - not_reachable_n:     Contact info structurally invalid (wrong number, mobile off)

    rpc_rate = (rpc_n + rpc_proxy_n) / contact_attempts_n — corrected numerator.
    Field visit SUC codes are excluded from rpc_n to prevent inflation.

    Schema guard (R21): if dcore_prm_followup_outcomes is empty or missing
    required columns, this node emits all-NULL / zero contact signals.  The
    state derivation in build_a2_locatability handles this gracefully
    (falls through §4.4b guard → unknown).

    Args:
        base:              crx_cc_a2_base; grain (account_id, observation_date).
            Required cols: account_id, observation_date, t0.
        observation_spine: dcore_observation_spine — full account→agreement mapping.
            Required cols: contract_id, observation_date, agreement_id, cif_id.
            contract_id = account_id; joined on (account_id, observation_date).
        followup:          dcore_prm_followup_outcomes.
            Required cols: agreement_id, action_ts, action_code,
            result_category, result_name.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id               (string)
            observation_date         (date)
            contact_attempts_n       (int;    NULL if no DCORE coverage)
            rpc_rate                 (double; NULL if attempts=0 or no DCORE)
            uns_rate                 (double; NULL if attempts=0 or no DCORE)
            last_contact_attempt_dt  (date;   NULL if no attempts; call-type
                                              codes only (OC/CB/IC) — excludes
                                              IA administrative notes)
            label_event_gap_d        (int;    days; NULL if no attempts)
            refusing_n               (int;    0 if no DCORE; explicit refusal count)
            ringing_n                (int;    0 if no DCORE; ringing no-answer count)
            deceased_flag            (int;    0/1; 1 = DCORE confirmed/claimed deceased)
            contact_confirmed_n      (int;    0 if no DCORE; _rpc_n + _rpc_proxy_n)
            dcore_departure_flag     (int;    0/1)
            field_visit_flag         (int;    0/1; 1 = ≥1 completed field visit)
            not_reachable_flag       (int;    0/1; 1 = contact info structurally invalid)
            gone_contact_flag        (int;    0/1; 1 = last _TAU_NOT_REACHABLE_N outbound
                                              dates all produced ringing/dead result_names,
                                              no confirmed outbound contact)
            ptp_flag                 (int;    0/1; 1 = ≥1 promise-to-pay or payment commitment)
            hardship_flag            (int;    0/1; 1 = ≥1 hardship / special-case signal)
            recent3_attempt_dates_n  (int;    0 if no DCORE; distinct outbound attempt
                                              dates found within the last
                                              _TAU_RECENT_AVOIDANCE_N ranks, ≤3)
            recent3_ringing_n        (int;    0 if no DCORE; ringing/no-answer count among
                                              those same last-3-ranked attempts)
            recent3_confirmed_n      (int;    0 if no DCORE; confirmed-contact count among
                                              those same last-3-ranked attempts)
            recent3_oldest_gap_d     (int;    days; NULL if fewer than
                                              _TAU_RECENT_AVOIDANCE_N distinct outbound
                                              dates exist; gap between observation_date and
                                              the oldest of the last-3-ranked attempts —
                                              2026-10-22 amendment, feeds Node 4's
                                              recent_avoidance_flag)
    """
    _REQUIRED_FOLLOWUP_COLS = {
        "agreement_id",  # was "iagreementseqno"
        "action_ts",
        "action_code",
        "result_category",  # was "szcategorycode"
        "result_name",  # was "szresultname" — now carried directly, no join needed
    }

    def _null_signals(df: DataFrame) -> DataFrame:
        return df.select("account_id", "observation_date").select(
            F.col("account_id"),
            F.col("observation_date"),
            F.lit(None).cast("int").alias("contact_attempts_n"),
            F.lit(None).cast("double").alias("rpc_rate"),
            F.lit(None).cast("double").alias("uns_rate"),
            F.lit(None).cast("date").alias("last_contact_attempt_dt"),
            F.lit(None).cast("int").alias("label_event_gap_d"),
            F.lit(0).cast("int").alias("refusing_n"),
            F.lit(0).cast("int").alias("ringing_n"),
            F.lit(0).cast("int").alias("deceased_flag"),
            F.lit(0).cast("int").alias("contact_confirmed_n"),
            F.lit(0).cast("int").alias("dcore_departure_flag"),
            F.lit(0).cast("int").alias("field_visit_flag"),
            F.lit(0).cast("int").alias("inbound_call_flag"),
            F.lit(0).cast("int").alias("not_reachable_flag"),
            F.lit(0).cast("int").alias("gone_contact_flag"),
            F.lit(0).cast("int").alias("ptp_flag"),
            F.lit(0).cast("int").alias("hardship_flag"),
            F.lit(0).cast("int").alias("recent3_attempt_dates_n"),
            F.lit(0).cast("int").alias("recent3_ringing_n"),
            F.lit(0).cast("int").alias("recent3_confirmed_n"),
            F.lit(None).cast("int").alias("recent3_oldest_gap_d"),
        )

    # ── Schema guard: return all-NULL if DCORE is unavailable ──────────────────
    followup_cols = set(followup.columns)
    if not _REQUIRED_FOLLOWUP_COLS.issubset(followup_cols):
        missing = _REQUIRED_FOLLOWUP_COLS - followup_cols
        LOG.warning(
            "build_a2_contact_signals: dcore_prm_followup_outcomes missing columns %s "
            "— emitting all-NULL contact signals (§4.4b guard will fire → unknown).",
            missing,
        )
        return _null_signals(base)

    empty_check = followup.limit(1).count()
    if empty_check == 0:
        LOG.warning(
            "build_a2_contact_signals: dcore_prm_followup_outcomes is empty "
            "— emitting all-NULL contact signals."
        )
        return _null_signals(base)

    # ── Schema guard: observation_spine required columns ──────────────────────
    _SPINE_REQUIRED = {"account_id", "observation_date", "agreement_id", "cif_id"}
    if not _SPINE_REQUIRED.issubset(set(observation_spine.columns)):
        missing = _SPINE_REQUIRED - set(observation_spine.columns)
        LOG.warning(
            "build_a2_contact_signals: dcore_observation_spine missing columns %s "
            "— emitting all-NULL contact signals (§4.4b guard will fire → unknown).",
            missing,
        )
        return _null_signals(base)

    # ── Step 1: bridge base pairs to DCORE via observation_spine ──────────────
    scope = observation_spine.select(
        "account_id",
        "observation_date",
        F.col("agreement_id").alias("iagreementseqno"),
        "cif_id",
    ).distinct()

    base_with_agreement = base.select("account_id", "observation_date", "t0").join(
        scope,
        on=["account_id", "observation_date"],
        how="left",
    )

    # ── Step 2: filter followup to window [t0, observation_date) ──────────────
    # result_name is carried directly on dcore_prm_followup_outcomes — no join needed.
    followup_dated = followup.withColumn(
        "_action_date", F.col("action_ts").cast("date")
    )
    scoped_followup = base_with_agreement.join(
        followup_dated.select(
            F.col("agreement_id").alias("iagreementseqno"),
            "_action_date",
            "action_code",
            F.col("result_category").alias("szcategorycode"),
            "result_name",
        ),
        on="iagreementseqno",
        how="inner",
    ).filter(
        (F.col("_action_date") >= F.col("t0"))
        & (F.col("_action_date") < F.col("observation_date"))
    )

    # ── Step 5: aggregate per (account_id, observation_date) ──────────────────
    aggregated = scoped_followup.groupBy("account_id", "observation_date").agg(
        # contact_attempts_n: distinct outbound attempt dates (OC + CB only)
        F.countDistinct(
            F.when(F.col("action_code").isin(_OUTBOUND_CODES), F.col("_action_date"))
        ).alias("contact_attempts_n"),
        # rpc_n: SUC outcomes on outbound calls only (OC / CB).
        # Scoping to _OUTBOUND_CODES naturally excludes field visits (FV),
        # inbound calls (IC), and all non-call channels without extra conditions.
        F.sum(
            F.when(
                (F.col("szcategorycode") == "SUC")
                & F.col("action_code").isin(_OUTBOUND_CODES),
                1,
            ).otherwise(0)
        ).alias("_rpc_n"),
        # rpc_proxy_n: RPC events confirmed via result_name across all categories
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_rpc_proxy_n"),
        # refusing_n: explicit refusal/hang-up/dispute — drives non_cooperative state
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_REFUSING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("refusing_n"),
        # ringing_n: ringing no-answer events — drives avoiding state (≥_TAU_RINGING_N)
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES), 1
            ).otherwise(0)
        ).alias("ringing_n"),
        # _deceased_n: confirmed or claimed deceased — drives deceased_flag
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_DECEASED_RESULT_NAMES), 1
            ).otherwise(0)
        ).alias("_deceased_n"),
        # uns_n: UNS category hits
        F.sum(F.when(F.col("szcategorycode") == "UNS", 1).otherwise(0)).alias("_uns_n"),
        # dcore_departure_n: contact records indicating customer left UAE
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_DEPARTURE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_dcore_departure_n"),
        # field_visit_n: field visit lifecycle events
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_FIELD_VISIT_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_field_visit_n"),
        # not_reachable_n: contact info structurally invalid — wrong number,
        # mobile switched off, line disconnected, ININ-OUTBOUND invalid codes.
        # Drives skip state (skip-tracing intervention required).
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_NOT_REACHABLE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_not_reachable_n"),
        # ptp_n: promise-to-pay or willingness-to-pay signals — customer committed
        # to pay, made an arrangement, or actually paid.  Output as ptp_flag for
        # downstream strategy routing; does not change the locatability state.
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(
                    _PROMISE_TO_PAY_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_ptp_n"),
        # hardship_n: hardship / special-case signals — death, disability, job loss,
        # bankruptcy, incarceration.  Output as hardship_flag for routing; does not
        # change the locatability state.
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_HARDSHIP_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_hardship_n"),
        # inbound_call_n: customer-initiated calls (IC) — distinct dates
        F.countDistinct(
            F.when(F.col("action_code").isin(_INBOUND_CODES), F.col("_action_date"))
        ).alias("_inbound_call_n"),
        # last_contact_attempt_dt: restricted to call-type codes (OC/CB/IC) — an
        # IA-logged administrative note must not make genuinely stale contact
        # evidence look fresh (would silently suppress the §4.4c guard below).
        F.max(
            F.when(F.col("action_code").isin(_CALL_CODES), F.col("_action_date"))
        ).alias("last_contact_attempt_dt"),
        # _last_confirmed_contact_dt: most recent date with confirmed RPC or inbound call
        F.max(
            F.when(
                (
                    (
                        (F.col("szcategorycode") == "SUC")
                        & F.col("action_code").isin(_OUTBOUND_CODES)
                    )
                    | F.upper(F.trim(F.col("result_name"))).isin(
                        _RIGHT_PARTY_CONTACT_RESULT_NAMES
                    )
                    | F.col("action_code").isin(_INBOUND_CODES)
                ),
                F.col("_action_date"),
            ).otherwise(F.lit(None).cast("date"))
        ).alias("_last_confirmed_contact_dt"),
    )

    # ── Step 5b: chronological recent-dead-contact check ──────────────────────
    # Dense-rank distinct outbound attempt dates (most recent = rank 1) per
    # (account_id, observation_date). Check if the last _TAU_NOT_REACHABLE_N
    # attempt dates were all dead-contact outcomes with no confirmed contact.
    _w_attempt_rank = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("_action_date").desc()
    )
    _outbound_ranked = scoped_followup.filter(
        F.col("action_code").isin(_OUTBOUND_CODES)
    ).withColumn("_attempt_date_rank", F.dense_rank().over(_w_attempt_rank))
    _last_n = _outbound_ranked.filter(
        F.col("_attempt_date_rank") <= _TAU_NOT_REACHABLE_N
    )
    _last_n_signals = _last_n.groupBy("account_id", "observation_date").agg(
        F.max("_attempt_date_rank").alias("_n_attempt_dates"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_NOT_REACHABLE_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_last_n_dead"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_last_n_ringing"),
        F.sum(
            F.when(
                (
                    (F.col("szcategorycode") == "SUC")
                    & F.col("action_code").isin(_OUTBOUND_CODES)
                )
                | F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_last_n_confirmed"),
    )

    # ── Step 5c: recent-avoidance window (2026-10-22 amendment) ───────────────
    # Same chronological ranking as Step 5b, windowed to _TAU_RECENT_AVOIDANCE_N (3)
    # instead of _TAU_NOT_REACHABLE_N (2) — feeds the reachability override in
    # Node 4 (Step 4b), which downgrades a lifetime Reachable determination when the
    # most recent attempts are all ringing/no-answer and recent.
    _recent_m = _outbound_ranked.filter(
        F.col("_attempt_date_rank") <= _TAU_RECENT_AVOIDANCE_N
    )
    _recent_m_signals = _recent_m.groupBy("account_id", "observation_date").agg(
        F.max("_attempt_date_rank").alias("_recent3_n_dates"),
        F.min("_action_date").alias("_recent3_oldest_date"),
        F.sum(
            F.when(
                F.upper(F.trim(F.col("result_name"))).isin(_RINGING_RESULT_NAMES),
                1,
            ).otherwise(0)
        ).alias("_recent3_ringing_n"),
        F.sum(
            F.when(
                (
                    (F.col("szcategorycode") == "SUC")
                    & F.col("action_code").isin(_OUTBOUND_CODES)
                )
                | F.upper(F.trim(F.col("result_name"))).isin(
                    _RIGHT_PARTY_CONTACT_RESULT_NAMES
                ),
                1,
            ).otherwise(0)
        ).alias("_recent3_confirmed_n"),
    )

    result = (
        aggregated.join(
            _last_n_signals, on=["account_id", "observation_date"], how="left"
        )
        .join(_recent_m_signals, on=["account_id", "observation_date"], how="left")
        .withColumn(
            "rpc_rate",
            F.when(
                F.col("contact_attempts_n") > 0,
                (F.col("_rpc_n") + F.col("_rpc_proxy_n")) / F.col("contact_attempts_n"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .withColumn(
            "uns_rate",
            F.when(
                F.col("contact_attempts_n") > 0,
                F.col("_uns_n") / F.col("contact_attempts_n"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .withColumn(
            "label_event_gap_d",
            F.datediff(F.col("observation_date"), F.col("last_contact_attempt_dt")),
        )
        .withColumn(
            "dcore_departure_flag",
            F.when(F.col("_dcore_departure_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "field_visit_flag",
            F.when(F.col("_field_visit_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "inbound_call_flag",
            F.when(F.col("_inbound_call_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "not_reachable_n",
            F.col("_not_reachable_n").cast("int"),
        )
        .withColumn(
            "not_reachable_flag",
            F.when(
                F.col("_n_attempt_dates").isNotNull()
                & (F.col("_n_attempt_dates") >= _TAU_NOT_REACHABLE_N)
                & (F.col("_last_n_dead") > 0)
                & (F.col("_last_n_confirmed") == 0),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "gone_contact_flag",
            F.when(
                F.col("_n_attempt_dates").isNotNull()
                & (F.col("_n_attempt_dates") >= _TAU_NOT_REACHABLE_N)
                & (F.col("_last_n_confirmed") == 0)
                & ((F.col("_last_n_dead") > 0) | (F.col("_last_n_ringing") > 0)),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "ptp_flag",
            F.when(F.col("_ptp_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "hardship_flag",
            F.when(F.col("_hardship_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "deceased_flag",
            F.when(F.col("_deceased_n") > 0, F.lit(1)).otherwise(F.lit(0)),
        )
        .withColumn(
            "contact_confirmed_n",
            (F.col("_rpc_n") + F.col("_rpc_proxy_n")).cast("int"),
        )
        .withColumn(
            "last_attempt_contact_flag",
            F.when(
                F.col("_last_confirmed_contact_dt").isNotNull()
                & (
                    F.col("_last_confirmed_contact_dt")
                    == F.col("last_contact_attempt_dt")
                ),
                F.lit(1),
            ).otherwise(F.lit(0)),
        )
        .withColumn(
            "recent3_attempt_dates_n",
            F.coalesce(F.col("_recent3_n_dates"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_ringing_n",
            F.coalesce(F.col("_recent3_ringing_n"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_confirmed_n",
            F.coalesce(F.col("_recent3_confirmed_n"), F.lit(0)).cast("int"),
        )
        .withColumn(
            "recent3_oldest_gap_d",
            F.when(
                F.col("_recent3_oldest_date").isNotNull(),
                F.datediff(F.col("observation_date"), F.col("_recent3_oldest_date")),
            ).otherwise(F.lit(None).cast("int")),
        )
        .drop(
            "_rpc_n",
            "_rpc_proxy_n",
            "_uns_n",
            "_dcore_departure_n",
            "_field_visit_n",
            "_inbound_call_n",
            "_not_reachable_n",
            "_last_confirmed_contact_dt",
            "_ptp_n",
            "_hardship_n",
            "_deceased_n",
            "_n_attempt_dates",
            "_last_n_dead",
            "_last_n_ringing",
            "_last_n_confirmed",
            "_recent3_n_dates",
            "_recent3_oldest_date",
            "_recent3_ringing_n",
            "_recent3_confirmed_n",
        )
    )

    # ── Left-join back to all base pairs (no DCORE coverage → NULLs / zeros) ──
    final = (
        base.select("account_id", "observation_date")
        .join(result, on=["account_id", "observation_date"], how="left")
        .fillna(
            {
                "refusing_n": 0,
                "ringing_n": 0,
                "deceased_flag": 0,
                "contact_confirmed_n": 0,
                "dcore_departure_flag": 0,
                "field_visit_flag": 0,
                "inbound_call_flag": 0,
                "not_reachable_flag": 0,
                "gone_contact_flag": 0,
                "not_reachable_n": 0,
                "last_attempt_contact_flag": 0,
                "ptp_flag": 0,
                "hardship_flag": 0,
                "recent3_attempt_dates_n": 0,
                "recent3_ringing_n": 0,
                "recent3_confirmed_n": 0,
            }
        )
    )

    n_rows = final.count()
    n_with_contact = final.filter(F.col("contact_attempts_n").isNotNull()).count()
    LOG.info(
        "build_a2_contact_signals: %d rows | DCORE coverage: %d (%.1f%%)",
        n_rows,
        n_with_contact,
        100.0 * n_with_contact / max(n_rows, 1),
    )

    return final


# ── Node 4: build_a2_locatability ────────────────────────────────────────────


def build_a2_locatability(  # pylint: disable=too-many-locals,too-many-positional-arguments
    base: DataFrame,
    login_presence: DataFrame,
    contact_signals: DataFrame,
    model_id: str,
    prm_contract: DataFrame = None,
    prm_client: DataFrame = None,
    feat_demographics_cif: DataFrame = None,
) -> DataFrame:
    """Join the three upstream passes and derive the location x reachability A2 axis.

    Args:
        base:            crx_cc_a2_base.
        login_presence:  crx_cc_a2_login_presence.
        contact_signals: crx_cc_a2_contact_signals.
        model_id:        `cc_60_180` | `cc_180_plus` | `rl_60_180` | `rl_180_plus`
            (or any other model_id) — selects the segment-aware `_TAU_RECENT_D` /
            `_TAU_LABEL_D` values (amendment, 2026-10-08). Resolved from
            `${globals:model_id}` via `params:model_id`. CC and RL both call this
            same function (model-agnostic — see module docstring).
        prm_contract:    Optional. CC only — carries `block_code_1`/`block_code_2`
            (Way4 deceased corroboration, T34). RL supplies nothing here (no Way4
            equivalent exists). `None` by default.
        prm_client:      Optional. CC only — paired with `prm_contract` to bridge
            to `cif_id` when `base` doesn't already carry one. `None` by default.
        feat_demographics_cif: Optional. Both domains — `ft_deceased_flag` at CIF
            grain (T34). RL supplies this directly since `base` already carries
            `cif_id`; CC supplies it alongside `prm_contract`/`prm_client` to build
            the bridge. `None` by default.

    Returns:
        DataFrame at grain (account_id, observation_date) with schema::

            account_id                 (string)
            observation_date           (date)
            spell_id                   (int)
            deceased_flag              (int;    0/1)
            location_state             (string; 'Skip' | 'In Country' | 'Unknown')
            reachability_state         (string; 'Reachable' | 'Non-Reachable' | 'Unknown')
            a2_state                   (string; 'Deceased' | '<location> - <reachability>')
            departure_trail_flag       (int;    0/1 — location evidence)
            in_country_flag            (int;    0/1 — location evidence)
            contact_confirmed_flag     (int;    0/1 — reachability evidence)
            gone_contact_flag          (int;    0/1 — reachability evidence)
            recent_avoidance_flag      (int;    0/1 — reachability evidence; 2026-10-22
                                                amendment; downgrades a lifetime Reachable
                                                determination to Non-Reachable when the last
                                                recent3_attempt_dates_n (≤3) outbound attempts
                                                were all ringing/no-answer, zero confirmed, and
                                                within tau_label of observation_date)
            reachability_guard_triggered (string; NULL | '4.4b_insufficient_attempts'
                                                | '4.4c_stale_evidence')
            contact_attempts_n         (int)
            label_event_gap_d          (int)
            last_digital_login_gap_d   (int)
            last_login_foreign_flag    (int)
            ringing_n                  (int)
            recent3_ringing_n          (int;    ringing/no-answer count among the last
                                                _TAU_RECENT_AVOIDANCE_N ranked outbound attempts)
            recent3_attempt_dates_n    (int;    distinct outbound attempt dates found
                                                within that same last-N-ranked window, ≤3)
            recent3_oldest_gap_d       (int;    days; NULL if fewer than
                                                _TAU_RECENT_AVOIDANCE_N distinct outbound dates
                                                exist)
            location_unknown_reason    (string; NULL when location_state != 'Unknown',
                                                else 'no_login_on_record' |
                                                'recent_login_but_foreign' |
                                                'login_stale_beyond_window' | 'other')
            way4_deceased_flag         (int;    0/1 — CC-only Way4 block-code deceased
                                                corroboration, T34; always 0 if
                                                `prm_contract` has no block-code columns)
            demographics_deceased_flag (int;    0/1 — `ft_deceased_flag` corroboration,
                                                T34; always 0 if `feat_demographics_cif` is
                                                not supplied or `cif_id` cannot be resolved)
            deceased_flag_v2           (int;    0/1 — OR of `deceased_flag`,
                                                `way4_deceased_flag`, `demographics_deceased_flag`,
                                                T34; drives `a2_state`'s "Deceased" branch.
                                                `deceased_flag` itself is untouched pass-through)
            computed_at                (string)
    """
    tau_recent_d = _resolve_tau(model_id, _TAU_RECENT_D_BY_MODEL_ID)
    tau_label_d = _resolve_tau(model_id, _TAU_LABEL_D_BY_MODEL_ID)

    # ── Step 1: join all three passes ─────────────────────────────────────────
    df = base.join(
        login_presence,
        on=["account_id", "observation_date"],
        how="left",
    ).join(
        contact_signals,
        on=["account_id", "observation_date"],
        how="left",
    )

    # ── Step 2: derived presence/reachability flags ───────────────────────────
    # departure_trail_flag: positive departure signal — pre-T0 sources only.
    # Intentionally pure location evidence — no reachability term mixed in, per
    # GRR's instruction.
    departure_trail_flag = F.when(
        (F.col("travel_mcc_flag_h2") == 1)
        | (F.col("last_txn_foreign_flag") == 1)
        | (F.col("foreign_login_flag") == 1)
        | (
            F.col("casa_inflow_stop_gap_d").isNotNull()
            & (F.col("casa_inflow_stop_gap_d") > 180)
        )
        | (F.col("dcore_departure_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))

    # in_country_flag: recent UAE login — also pure location evidence.
    in_country_flag = F.when(
        (F.col("last_login_foreign_flag") == 0)
        & F.col("last_digital_login_gap_d").isNotNull()
        & (F.col("last_digital_login_gap_d") <= tau_recent_d),
        F.lit(1),
    ).otherwise(F.lit(0))

    # contact_confirmed_flag: any confirmed two-way contact (outbound RPC or inbound call)
    contact_confirmed_flag = F.when(
        (F.col("contact_confirmed_n") > 0) | (F.col("inbound_call_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))

    # recent_avoidance_flag (2026-10-22 amendment): downgrades a lifetime-established
    # Reachable determination when the most recent _TAU_RECENT_AVOIDANCE_N outbound
    # attempts were ALL ringing/no-answer, zero confirmed among them, and recent
    # (within the segment's tau_label window) — see Step 4 below.
    recent_avoidance_flag = F.when(
        (F.col("recent3_attempt_dates_n") >= _TAU_RECENT_AVOIDANCE_N)
        & (F.col("recent3_confirmed_n") == 0)
        & (F.col("recent3_ringing_n") == _TAU_RECENT_AVOIDANCE_N)
        & F.col("recent3_oldest_gap_d").isNotNull()
        & (F.col("recent3_oldest_gap_d") <= tau_label_d),
        F.lit(1),
    ).otherwise(F.lit(0))

    df = (
        df.withColumn("departure_trail_flag", departure_trail_flag)
        .withColumn("in_country_flag", in_country_flag)
        .withColumn("contact_confirmed_flag", contact_confirmed_flag)
        .withColumn("recent_avoidance_flag", recent_avoidance_flag)
    )

    # ── Step 3: location_state — purely departure_trail_flag / in_country_flag ─
    location_state = (
        F.when(
            (F.col("departure_trail_flag") == 1) & (F.col("in_country_flag") == 0),
            F.lit("Skip"),
        )
        .when(F.col("in_country_flag") == 1, F.lit("In Country"))
        .otherwise(F.lit("Unknown"))
    )

    df = df.withColumn("location_state", location_state)

    # ── Step 3b: location_unknown_reason — diagnostic, present only when relevant —
    # Mirrors the EDA snippet's already-proven `_location_unknown_cause_expr`
    # (t29_a2_locatability_v2_eda.py:163-182), now shipped as a first-class column
    # against this function's own resolved tau_recent_d rather than something only
    # the EDA snippet can compute (T29 Oct-12 retest root-cause finding).
    location_unknown_reason = F.when(
        F.col("location_state") != "Unknown", F.lit(None).cast("string")
    ).otherwise(
        F.when(
            F.col("last_digital_login_gap_d").isNull(),
            F.lit("no_login_on_record"),
        )
        .when(
            (F.col("last_login_foreign_flag") == 1)
            & (F.col("last_digital_login_gap_d") <= tau_recent_d),
            F.lit("recent_login_but_foreign"),
        )
        .when(
            F.col("last_digital_login_gap_d") > tau_recent_d,
            F.lit("login_stale_beyond_window"),
        )
        .otherwise(F.lit("other"))
    )

    df = df.withColumn("location_unknown_reason", location_unknown_reason)

    # ── Step 4: reachability_state — guards, then confirmed-contact vs dead ────
    reachability_guard_triggered = (
        F.when(
            F.col("contact_attempts_n").isNull()
            | (F.col("contact_attempts_n") < _TAU_A_ATTEMPTS),
            F.lit("4.4b_insufficient_attempts"),
        )
        .when(
            F.col("label_event_gap_d").isNull()
            | (F.col("label_event_gap_d") > tau_label_d),
            F.lit("4.4c_stale_evidence"),
        )
        .otherwise(F.lit(None).cast("string"))
    )

    df = df.withColumn("reachability_guard_triggered", reachability_guard_triggered)

    reachability_state = (
        F.when(F.col("reachability_guard_triggered").isNotNull(), F.lit("Unknown"))
        .when(F.col("recent_avoidance_flag") == 1, F.lit("Non-Reachable"))
        .when(F.col("contact_confirmed_flag") == 1, F.lit("Reachable"))
        .when(
            (F.col("gone_contact_flag") == 1)
            & (F.col("last_attempt_contact_flag") == 0),
            F.lit("Non-Reachable"),
        )
        .otherwise(F.lit("Unknown"))
    )

    df = df.withColumn("reachability_state", reachability_state)

    # ── Step 4b: deceased corroboration beyond DCORE (T34, 2026-10-12) ──────
    # Way4 block code — CC only, activates iff prm_contract carries block codes.
    if (
        prm_contract is not None
        and "block_code_1" in prm_contract.columns
        and "block_code_2" in prm_contract.columns
    ):
        contract_block_codes = prm_contract.select(
            F.col("contract_id").alias("account_id"),
            "observation_date",
            F.upper(F.trim(F.col("block_code_1"))).alias("_block_code_1"),
            F.upper(F.trim(F.col("block_code_2"))).alias("_block_code_2"),
        )
        df = df.join(
            contract_block_codes, on=["account_id", "observation_date"], how="left"
        )
        way4_deceased_flag = F.when(
            F.col("_block_code_1").isin(_WAY4_DECEASED_BLOCK_CODES)
            | F.col("_block_code_2").isin(_WAY4_DECEASED_BLOCK_CODES),
            F.lit(1),
        ).otherwise(F.lit(0))
        df = df.withColumn("way4_deceased_flag", way4_deceased_flag).drop(
            "_block_code_1", "_block_code_2"
        )
    else:
        df = df.withColumn("way4_deceased_flag", F.lit(0))

    # Demographics — both domains. Use cif_id already on the frame if present (RL);
    # otherwise bridge via prm_contract/prm_client if supplied (CC). Skip cleanly if
    # neither path resolves cif_id.
    if feat_demographics_cif is not None:
        if (
            "cif_id" not in df.columns
            and prm_contract is not None
            and prm_client is not None
        ):
            cif_bridge = _build_cif_bridge(prm_contract, prm_client)
            df = df.join(
                cif_bridge, on=df["account_id"] == cif_bridge["contract_id"], how="left"
            ).drop("contract_id")
        if "cif_id" in df.columns:
            demo = feat_demographics_cif.select(
                "cif_id", F.col("ft_deceased_flag").alias("_ft_deceased_flag")
            )
            df = df.join(demo, on="cif_id", how="left")
            demographics_deceased_flag = F.when(
                F.col("_ft_deceased_flag") == 1, F.lit(1)
            ).otherwise(F.lit(0))
            df = df.withColumn(
                "demographics_deceased_flag", demographics_deceased_flag
            ).drop("_ft_deceased_flag")
        else:
            df = df.withColumn("demographics_deceased_flag", F.lit(0))
    else:
        df = df.withColumn("demographics_deceased_flag", F.lit(0))

    # ── Step 5: deceased pre-guard + combined state ──────────────────────────
    deceased_flag_v2 = F.when(
        (F.col("deceased_flag") == 1)
        | (F.col("way4_deceased_flag") == 1)
        | (F.col("demographics_deceased_flag") == 1),
        F.lit(1),
    ).otherwise(F.lit(0))
    df = df.withColumn("deceased_flag_v2", deceased_flag_v2)

    a2_state = F.when(F.col("deceased_flag_v2") == 1, F.lit("Deceased")).otherwise(
        F.concat(F.col("location_state"), F.lit(" - "), F.col("reachability_state"))
    )

    df = df.withColumn("a2_state", a2_state)

    # ── Step 6: emit typed schema ────────────────────────────────────────────
    output = df.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("deceased_flag").cast("int"),
        F.col("location_state").cast("string"),
        F.col("reachability_state").cast("string"),
        F.col("a2_state").cast("string"),
        F.col("departure_trail_flag").cast("int"),
        F.col("in_country_flag").cast("int"),
        F.col("contact_confirmed_flag").cast("int"),
        F.col("gone_contact_flag").cast("int"),
        F.col("recent_avoidance_flag").cast("int"),
        F.col("reachability_guard_triggered").cast("string"),
        F.col("contact_attempts_n").cast("int"),
        F.col("label_event_gap_d").cast("int"),
        F.col("last_digital_login_gap_d").cast("int"),
        F.col("last_login_foreign_flag").cast("int"),
        F.col("ringing_n").cast("int"),
        F.col("recent3_ringing_n").cast("int"),
        F.col("recent3_attempt_dates_n").cast("int"),
        F.col("recent3_oldest_gap_d").cast("int"),
        F.col("location_unknown_reason").cast("string"),
        F.col("way4_deceased_flag").cast("int"),
        F.col("demographics_deceased_flag").cast("int"),
        F.col("deceased_flag_v2").cast("int"),
        F.lit(datetime.date.today().isoformat()).alias("computed_at"),
    )

    _log_a2_stats(output)

    return output


def _log_a2_stats(df: DataFrame) -> None:
    """Log state distribution for post-run monitoring."""
    try:
        n_total = df.count()
        state_dist = df.groupBy("a2_state").count().collect()

        LOG.info("build_a2_locatability: total rows = %d", n_total)
        for row in state_dist:
            pct = 100.0 * row["count"] / max(n_total, 1)
            LOG.info(
                "  a2_state=%-25s n=%7d  (%.1f%%)",
                str(row["a2_state"]),
                row["count"],
                pct,
            )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning("build_a2_locatability: stats logging failed: %s", exc)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_departure_signature/nodes.py`
action: delete · base sha256 `bab901b3f07d3fff85bd50e2aaa545a7f300125f54ad1d4b0a4a71be01554f6b` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T06 — CC Departure Signature & History Shape Features.

Public nodes (15):
    build_departure_spell_base, build_departure_contract_cif,
    build_departure_pass_a, build_departure_pass_b, build_departure_pass_c,
    build_departure_pass_d, build_departure_pass_e, build_departure_pass_f,
    build_departure_pass_g, build_departure_pass_h, build_departure_pass_h2,
    build_departure_pass_i, build_departure_pass_j, build_departure_pass_k,
    build_departure_final

Output grain: (account_id, spell_id) — joins seamlessly with T04b/T05 outputs.

Window design (same convention as T04b/T05)::

    M0      = trunc(t0, 'month')                  — onset month (excluded)
    W_pre   = [w_pre_start, M0)                   — clean pre-delinquency window (≤12 months)
    H2      = [M0-3m, M0) → m_from_m0 1..3        — recent behaviour (T0-anchored)
    H1      = [w_pre_start, M0-3m) → m_from_m0 ≥ 4  — baseline
    H2_blk  = [block_date-3m, block_date) → m_from_block 1..3 — block-anchored (Pass A travel)

T0 leakage guard: all joins enforce strict obs_date < M0.

Pass A  — CC departure + fee signals from prm_transaction (travel_mcc_flag_h2,
          foreign_txn_share_h2, last_txn_foreign_flag; internal _fee_amt_h2)
Pass B  — CASA inflow signals from comp_financial_tran_repos_dly [COND: schema guard]
          (casa_inflow_stop_gap_d, eosb_like_flag)
Pass C  — History shape self-window from crx_cc_spell_table (prior_spell_cnt_24m,
          months_since_prior_spell, roll_speed_30_d, roll_speed_60_d)
Pass D  — Tenure + lifetime fees from prm_contract + prm_turnovers
          (tenure_at_t0_m, fee_rate_life, fee_accel_h2)
Pass E  — AECB leverage slope from int_bureau_pull_monthly (aecb_leverage_slope)
          [T21 DROP candidate — 0.11% bureau coverage on CC 60+ DPD book; code retained]
Pass F  — Relationship breadth from feat_product_holding (relationship_breadth)
Pass G  — AECB alert signals from fea_monthly_aecb_alerts (REUSE — retail.feature_space)
          (aecb_new_enquiry_3m, aecb_credit_opened_3m, aecb_total_alerts_3m)
Pass H  — Cross-border CASA outflow from feat_fx_leakage [COND: schema guard]
          (cross_border_outflow_amt_h2, cross_border_outflow_cnt_h2)
Pass H2 — Retail.feature_space CC travel+tours MCC from feat_cc_txns_rfs [COND: schema guard]
          (retail_travel_mcc_amt_h2, retail_travel_mcc_cnt_h2)
Pass I  — Payroll indicator from feat_payroll_indicator [COND: schema guard]
          (payroll_present_h2, payroll_stopped_flag)
Pass J  — Foreign login detection from prm_digital_login_monthly (OMB login logs)
          (foreign_login_flag, last_login_country_h2)
Pass K  — Bust-out / fraudster utilisation signals (crx_cc_transactions + prm_contract reuse)
          (limit_util_first_7d_flag, ever_paid_flag, max_7d_spend_ratio)
Nulls   — Always-NULL placeholders: cross_prod_t0_gap_d, simultaneous_default_flag

FILL-IN items (resolve before or during PROD run):
  FI-1: _SALARY_CODES — RESOLVED 2026-08-21 (sourced from WM income.py ENBD params)
  FI-2: _TRAN_DC_CREDIT — RESOLVED 2026-08-21 ('C' confirmed from WM ENBD entity config)
  FI-4: _CONTRACT_CIF_COL — confirmed 'client_id' from prm_contract schema
  FI-5: _CONTRACT_OPEN_DATE_COL — prm_contract column for account open date
  FI-6: _TURNOVERS_SNAPSHOT_COL — prm_turnovers snapshot date column name
  FI-7: _FEE_CATEGORY — exact value of CC fee tag in prm_transaction.txn_category
  FI-8: _PAYMENT_CATEGORY — exact value of CC payment tag in crx_cc_transactions.txn_category
"""

# pylint: disable=too-many-lines  # 13 private pass helpers (~1700 lines) + 15 thin public wrappers

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)

# ── Travel MCC codes (R14 — departure proxy, no protected attributes) ────────
# Source: ISO 18245 Merchant Category Codes (Visa/Mastercard published mapping).
# Scope: booking or using international travel services — strong departure proxy.
#   Airlines (brand codes):        3000-3299
#   Airlines (generic):            4511
#   Travel agencies/tour ops:      4722
#   Cruise / steamship lines:      4411  — added: clear departure signal
# Deliberately excluded (domestic-ambiguous; captured by is_international instead):
#   Hotels/lodging:                3501-3999, 7011
#   Car rentals:                   3351-3441, 7512, 7513
_TRAVEL_MCCS = list(set(range(3000, 3300)) | {4411, 4511, 4722})

# ── Travel keyword regex for txn_description fallback (Pass A) ───────────────
# Catches transactions where MCC is absent or miscoded (R14).
# Covers UAE-headquartered airlines and generic booking keywords.
# Case-insensitive via (?i); word-boundary anchors minimise false positives.
_TRAVEL_KEYWORDS_RE = (
    r"(?i)\b(AIRLINE|AIRWAYS|AIR TICKET|FLIGHT|AIRPORT|DEPARTURE|"
    r"EMIRATES AIR|ETIHAD|FLYDUBAI|AIR ARABIA|WIZZ AIR|BOARDING PASS)\b"
)

# ── FILL-IN constants ─────────────────────────────────────────────────────────
# FI-1: salary tran_particular_code values — sourced from
#   wealth_management/conf/enbd/parameters/parameters.yml → particular_codes_unique
#   (ENBD entity, confirmed 2026-08-21).  These are the codes that, when seen on a credit
#   transaction, positively identify a salary credit.
_SALARY_CODES = [
    "505",
    "506",
    "507",
    "503",
    "585",
    "586",
    "587",
    "588",
    "085",
    "086",
    "087",
    "088",
    "328",
    "828",
]
# Codes to EXCLUDE even if the narrative matches salary regex — from WM particular_codes_not_in
_SALARY_EXCLUDE_CODES = ["947", "LV3", "LV4"]

# FI-2: credit indicator in tran_dc column — confirmed 'C' from WM sal_casa_txns_part_tran_type
_TRAN_DC_CREDIT = "C"  # confirmed: matches wealth_management ENBD entity config


# FI-5: prm_contract column name for account open date
# 'open_date' confirmed from PROD schema (error: record_date_to unresolved;
# suggested columns include open_date, close_date, writeoff_date)
_CONTRACT_OPEN_DATE_COL = "open_date"  # confirmed from prm_contract schema

# FI-6: prm_turnovers snapshot date column — confirmed 'observation_date' from primary layer
_TURNOVERS_SNAPSHOT_COL = "observation_date"  # confirmed from prm_cc.py rename mapping

# FI-7: CC fee tag in prm_transaction.txn_category (exact string value)
_FEE_CATEGORY = "fee"  # <<FILL-IN: verify exact value in PROD>>

# FI-8: CC payment category tag in crx_cc_transactions.txn_category
_PAYMENT_CATEGORY = "payment"  # <<FILL-IN: verify exact value in PROD>>

# ── Pass H column names ───────────────────────────────────────────────────────
# Source: feat_fx_leakage = fea_monthly_agg_fx_leakage (retail.feature_space).
# Pre-rolled 3-month sum; covers H2 = [M0-3m, M0) at the last H2 month.
# T06d (2026-08-26): feat_casa_txns had no cross-border columns — correct source is
# fea_monthly_agg_fx_leakage which derives is_cross_border_outflow_txn from
# counter_party_bank_cntry in raw FTR transactions.
_FX_CB_AMT_COL = "ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum"
# No pre-rolled count equivalent in fea_monthly_agg_fx_leakage — cross_border_outflow_cnt_h2
# emits NULL. T21 candidate for formal dropping.
_FX_CB_CNT_COL: str | None = None  # absent — T21 candidate

# ── Pass H2 column names (PROD schema probe required — T06d) ─────────────────
# Source: feat_cc_txns_rfs = fea_cc_inflow_outflow_txns_monthly
# The ft_ prefix and window suffix are added downstream; bare column at source grain.
_CC_TRAVEL_AMT_COL = "outflow_cc_mcc_travel_and_tours_amt"
_CC_TRAVEL_CNT_COL = "outflow_cc_mcc_travel_and_tours_count"

# ── Pass I column names ───────────────────────────────────────────────────────
# Source: feat_payroll_indicator = pri_monthly_payroll_indicator
# T06d (2026-08-26): confirmed actual column name is "payroll_flag" (0/1 per month row).
_PAYROLL_HAS_COL = "payroll_flag"  # confirmed via t06d 2026-08-26


# ── Public nodes ──────────────────────────────────────────────────────────────


def build_departure_spell_base(
    crx_cc_spell_table: DataFrame,
    crx_cc_payment_trajectory: DataFrame,
    cc_spine: DataFrame,
) -> DataFrame:
    """Build spell base with T04b truncation columns (Node 1 of 15).

    Filters crx_cc_spell_table to non-censored spells and inner-joins
    the W_pre truncation columns from crx_cc_payment_trajectory.
    Also derives block_date (t0 + days_to_dpd60) and spine_obs_date for
    downstream passes that anchor windows on card-block or observation date.

    Args:
        crx_cc_spell_table:        T03b spell table (all spells including censored).
        crx_cc_payment_trajectory: T04b output carrying w_pre truncation columns.
        cc_spine:                  Spine table with observation_date per contract.

    Returns:
        DataFrame at grain (account_id, spell_id) with t0, prior_spell_end,
        days_to_dpd30/60, all w_pre_* columns, block_date, and spine_obs_date.
    """
    # Excludes both censored subtypes (data_depth + restructured_entry) — see
    # cc_payment_trajectory/nodes.py Step 0 comment for rationale.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id",
        "spell_id",
        "t0",
        "prior_spell_end",
        "days_to_dpd30",
        "days_to_dpd60",
    )
    trunc = crx_cc_payment_trajectory.select(
        "account_id",
        "spell_id",
        "w_pre_start",
        "w_pre_clean_m",
        "w_pre_contaminated_flag",
        "w_pre_truncation_reason",
    )
    # Derive block_date: t0 + days_to_dpd60 (NULL-safe fallback to M0)
    result = spell.join(trunc, on=["account_id", "spell_id"], how="inner").withColumn(
        "block_date",
        F.when(
            F.col("days_to_dpd60").isNotNull(),
            F.expr("date_add(t0, cast(days_to_dpd60 as int))"),
        ).otherwise(F.trunc(F.col("t0"), "month")),
    )

    # Join cc_spine for spine_obs_date (latest obs_date per account — typically one row)
    spine_obs = cc_spine.groupBy("contract_id").agg(
        F.max("observation_date").alias("spine_obs_date")
    )
    return result.join(
        spine_obs.withColumnRenamed("contract_id", "_spine_ctr"),
        result["account_id"] == F.col("_spine_ctr"),
        how="left",
    ).drop("_spine_ctr")


def build_departure_contract_cif(
    prm_contract: DataFrame,
    prm_client: DataFrame,
) -> DataFrame:
    """Build contract_id → cif_id bridge (Node 2 of 15).

    Maps Way4 client_idt (prm_contract.client_id) → bank CIF (prm_client.cif_id).
    Pattern mirrors spine_builders.py::finalize_contract_spine().

    Both prm_contract and prm_client expose 'client_id' after primary-layer renaming
    (client_idt → client_id in both). Aliasing to '_way4_cid' is defensive PySpark
    practice (prevents ambiguity if column sets shift) and signals semantic intent:
    this is the Way4 system ID, NOT the bank CIF.

    Args:
        prm_contract:  Primary CC contracts. Required cols: contract_id, client_id.
        prm_client:    Primary client dimension. Required cols: client_id, cif_id.

    Returns:
        DataFrame at grain contract_id with columns (contract_id, cif_id).
    """
    return (
        prm_contract.select("contract_id", F.col("client_id").alias("_way4_cid"))
        .join(
            prm_client.select(F.col("client_id").alias("_way4_cid"), "cif_id"),
            on="_way4_cid",
            how="left",
        )
        .select("contract_id", "cif_id")
        .dropDuplicates(["contract_id"])
    )


def build_departure_pass_a(
    crx_cc_transactions: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """CC departure signals + H2 fee amount (Node 3 of 15).

    Wraps _build_pass_a. Returns full output including _fee_amt_h2 — this
    intermediate column is consumed by build_departure_pass_d and dropped
    in build_departure_final before the final join.

    Args:
        crx_cc_transactions:    T04c intermediate — T0-scoped CC transactions.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with travel_mcc_flag_h2,
        foreign_txn_share_h2, last_txn_foreign_flag, _fee_amt_h2.

        Anchor semantics (T06 anchor-change):
            travel_mcc_flag_h2 / foreign_txn_share_h2 — H2 anchored on block_date
                (card-block date = t0 + days_to_dpd60), window [block-3m, block).
            last_txn_foreign_flag — most recent transaction before spine_obs_date
                (extends W_pre right boundary to obs_date, covering the T0→block gap).
            _fee_amt_h2 — still T0-anchored [M0-3m, M0) (unchanged; used by Pass D).
    """
    return _build_pass_a(crx_cc_transactions, spell_w)


def build_departure_pass_b(
    comp_financial_tran_repos_dly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """CASA inflow stop signals (Node 4 of 15).

    Wraps _build_pass_b. Schema guard emits NULL if required columns absent.

    Args:
        comp_financial_tran_repos_dly:  Raw CASA transactions (2.4B rows, R20).
        contract_cif:                   crx_cc_departure_contract_cif output.
        spell_w:                        crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with casa_inflow_stop_gap_d,
        eosb_like_flag.
    """
    return _build_pass_b(comp_financial_tran_repos_dly, contract_cif, spell_w)


def build_departure_pass_c(
    crx_cc_spell_table: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """History shape from spell table self-window (Node 5 of 15).

    Wraps _build_pass_c. Needs original spell table (including censored spells)
    for the 24-month prior-spell lookback.

    Args:
        crx_cc_spell_table: T03b spell table (all spells, unfiltered).
        spell_w:            crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with prior_spell_cnt_24m,
        months_since_prior_spell, roll_speed_30_d, roll_speed_60_d.
    """
    return _build_pass_c(crx_cc_spell_table, spell_w)


def build_departure_pass_d(
    prm_contract: DataFrame,
    prm_turnovers: DataFrame,
    spell_w: DataFrame,
    pass_a_df: DataFrame,
) -> DataFrame:
    """Tenure and lifetime fee velocity features (Node 6 of 15).

    Extracts _fee_amt_h2 from pass_a_df and passes it to _build_pass_d.

    Args:
        prm_contract:   Primary CC contracts (SCD2 via observation_date).
        prm_turnovers:  Primary CC lifetime turnover snapshots.
        spell_w:        crx_cc_departure_spell_base output.
        pass_a_df:      crx_cc_departure_pass_a output (includes _fee_amt_h2).

    Returns:
        DataFrame at (account_id, spell_id) with tenure_at_t0_m,
        fee_rate_life, fee_accel_h2.
    """
    fee_feats = pass_a_df.select("account_id", "spell_id", "_fee_amt_h2")
    return _build_pass_d(prm_contract, prm_turnovers, spell_w, fee_feats)


def build_departure_pass_e(
    int_bureau_pull_monthly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """AECB leverage slope via OLS (Node 7 of 15).

    Wraps _build_pass_e. T21 DROP confirmed — all values NULL in production.

    Args:
        int_bureau_pull_monthly:  AECB monthly pull snapshots.
        contract_cif:             crx_cc_departure_contract_cif output.
        spell_w:                  crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with aecb_leverage_slope.
    """
    return _build_pass_e(int_bureau_pull_monthly, contract_cif, spell_w)


def build_departure_pass_f(
    feat_product_holding: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Relationship breadth from feat_product_holding (Node 8 of 15).

    Inlines the cif_id → account_id and month_number → observation_date
    normalisation before calling _build_pass_f (original lines 318–327).

    Args:
        feat_product_holding:   fea_timeseries_based_product_holding.
                                Grain cif_id × month_number (yyyyMMdd); normalised
                                to account_id × observation_date before _build_pass_f.
        contract_cif:           crx_cc_departure_contract_cif output.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with relationship_breadth.
    """
    _ph_cols = {c.lower() for c in feat_product_holding.columns}
    if "cif_id" in _ph_cols and "account_id" not in _ph_cols:
        _cif_map = contract_cif.withColumnRenamed("contract_id", "account_id")
        feat_product_holding = feat_product_holding.join(
            _cif_map, on="cif_id", how="inner"
        )
    if "month_number" in _ph_cols and "observation_date" not in _ph_cols:
        feat_product_holding = feat_product_holding.withColumn(
            "observation_date", F.to_date(F.col("month_number"), "yyyyMMdd")
        )
    return _build_pass_f(feat_product_holding, spell_w)


def build_departure_pass_g(
    fea_monthly_aecb_alerts: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """AECB alert signals — REUSE from retail.feature_space (Node 9 of 15).

    Wraps _build_pass_g. Schema guard emits NULL if required columns absent.

    Args:
        fea_monthly_aecb_alerts:  AECB alert feature table (retail.feature_space).
        contract_cif:             crx_cc_departure_contract_cif output.
        spell_w:                  crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with aecb_new_enquiry_3m,
        aecb_credit_opened_3m, aecb_total_alerts_3m.
    """
    return _build_pass_g(fea_monthly_aecb_alerts, contract_cif, spell_w)


def build_departure_pass_h(
    feat_fx_leakage: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Cross-border CASA outflow signals (Node 10 of 15).

    Wraps _build_pass_h. Schema guard emits NULL if required columns absent.

    Args:
        feat_fx_leakage:  fea_monthly_agg_fx_leakage (retail.feature_space).
        contract_cif:     crx_cc_departure_contract_cif output.
        spell_w:          crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with cross_border_outflow_amt_h2,
        cross_border_outflow_cnt_h2.
    """
    return _build_pass_h(feat_fx_leakage, contract_cif, spell_w)


def build_departure_pass_h2(
    feat_cc_txns_rfs: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Retail.feature_space CC travel+tours MCC signals (Node 11 of 15).

    Wraps _build_pass_h2. Schema guard emits NULL if required columns absent.

    Args:
        feat_cc_txns_rfs:  fea_cc_inflow_outflow_txns_monthly (retail.feature_space).
        contract_cif:      crx_cc_departure_contract_cif output.
        spell_w:           crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with retail_travel_mcc_amt_h2,
        retail_travel_mcc_cnt_h2.
    """
    return _build_pass_h2(feat_cc_txns_rfs, contract_cif, spell_w)


def build_departure_pass_i(
    feat_payroll_indicator: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Payroll presence and stop signals (Node 12 of 15).

    Wraps _build_pass_i. Schema guard emits NULL if required columns absent.

    Args:
        feat_payroll_indicator: pri_monthly_payroll_indicator (retail.feature_space).
        contract_cif:           crx_cc_departure_contract_cif output.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with payroll_present_h2,
        payroll_stopped_flag.
    """
    return _build_pass_i(feat_payroll_indicator, contract_cif, spell_w)


def build_departure_pass_j(
    prm_digital_login_monthly: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Foreign login detection from OMB login logs (Node 13 of 15).

    Wraps _build_pass_j. Schema guard emits NULL if required columns absent.

    Args:
        prm_digital_login_monthly:  Monthly OMB login aggregation.
        contract_cif:               crx_cc_departure_contract_cif output.
        spell_w:                    crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with foreign_login_flag,
        last_login_country_h2.

        Anchor semantics (T06 anchor-change):
            foreign_login_flag — most recent login before spine_obs_date (not [T0-3m, T0)).
            Login can occur post-card-block (digital channel stays active), so obs_date
            is the correct ceiling; fallback to M0 if spine_obs_date is NULL.
    """
    return _build_pass_j(prm_digital_login_monthly, contract_cif, spell_w)


def build_departure_pass_k(
    crx_cc_transactions: DataFrame,
    prm_contract: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Bust-out / fraudster utilisation signals (Node 14 of 15).

    Wraps _build_pass_k. Reuses crx_cc_transactions (Pass A source) and
    prm_contract (Pass D source); no new inputs.

    Args:
        crx_cc_transactions:    T04c intermediate — T0-scoped CC transactions.
        prm_contract:           Primary CC contracts.
        spell_w:                crx_cc_departure_spell_base output.

    Returns:
        DataFrame at (account_id, spell_id) with ever_paid_flag,
        limit_util_first_7d_flag, max_7d_spend_ratio.
    """
    return _build_pass_k(crx_cc_transactions, prm_contract, spell_w)


def build_departure_final(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    spell_w: DataFrame,
    pass_a: DataFrame,
    pass_b: DataFrame,
    pass_c: DataFrame,
    pass_d: DataFrame,
    pass_e: DataFrame,
    pass_f: DataFrame,
    pass_g: DataFrame,
    pass_h: DataFrame,
    pass_h2: DataFrame,
    pass_i: DataFrame,
    pass_j: DataFrame,
    pass_k: DataFrame,
) -> DataFrame:
    """Assemble all pass outputs into the final departure signature (Node 15 of 15).

    Left-joins all pass outputs onto spell_w. Drops _fee_amt_h2 from pass_a
    before joining (internal column consumed by Pass D; not in final schema).
    Adds always-NULL placeholder columns. Calls _log_departure_stats.
    Applies final typed .select() to enforce schema contract.

    Args:
        spell_w:    crx_cc_departure_spell_base — the grain anchor.
        pass_a:     crx_cc_departure_pass_a (includes _fee_amt_h2 — dropped here).
        pass_b..k:  crx_cc_departure_pass_b through crx_cc_departure_pass_k.

    Returns:
        DataFrame at (account_id, spell_id) — 36-column typed departure signature.
        Schema is identical to the pre-refactor build_cc_departure_signature output.
    """
    result = (
        spell_w.join(
            pass_a.drop("_fee_amt_h2"), on=["account_id", "spell_id"], how="left"
        )
        .join(pass_b, on=["account_id", "spell_id"], how="left")
        .join(pass_c, on=["account_id", "spell_id"], how="left")
        .join(pass_d, on=["account_id", "spell_id"], how="left")
        .join(pass_e, on=["account_id", "spell_id"], how="left")
        .join(pass_f, on=["account_id", "spell_id"], how="left")
        .join(pass_g, on=["account_id", "spell_id"], how="left")
        .join(pass_h, on=["account_id", "spell_id"], how="left")
        .join(pass_h2, on=["account_id", "spell_id"], how="left")
        .join(pass_i, on=["account_id", "spell_id"], how="left")
        .join(pass_j, on=["account_id", "spell_id"], how="left")
        .join(pass_k, on=["account_id", "spell_id"], how="left")
        # Always-NULL placeholders (confirmed absent from all repos in T01 reuse map)
        .withColumn("cross_prod_t0_gap_d", F.lit(None).cast("double"))
        .withColumn("simultaneous_default_flag", F.lit(None).cast("int"))
        .withColumn("computed_at", F.current_timestamp())
    )

    _log_departure_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
        F.col("foreign_txn_share_h2").cast("double"),
        F.col("last_txn_foreign_flag").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
        F.col("eosb_like_flag").cast("int"),
        F.col("foreign_login_flag").cast("int"),
        F.col("last_login_country_h2").cast("string"),
        F.col("fee_rate_life").cast("double"),
        F.col("fee_accel_h2").cast("double"),
        F.col("tenure_at_t0_m").cast("int"),
        F.col("prior_spell_cnt_24m").cast("int"),
        F.col("months_since_prior_spell").cast("int"),
        F.col("roll_speed_30_d").cast("int"),
        F.col("roll_speed_60_d").cast("int"),
        F.col("cross_prod_t0_gap_d").cast("double"),
        F.col("simultaneous_default_flag").cast("int"),
        F.col("aecb_leverage_slope").cast("double"),
        F.col("relationship_breadth").cast("int"),
        F.col("aecb_new_enquiry_3m").cast("int"),
        F.col("aecb_credit_opened_3m").cast("int"),
        F.col("aecb_total_alerts_3m").cast("int"),
        F.col("cross_border_outflow_amt_h2").cast("double"),
        F.col("cross_border_outflow_cnt_h2").cast("int"),
        F.col("retail_travel_mcc_amt_h2").cast("double"),
        F.col("retail_travel_mcc_cnt_h2").cast("int"),
        F.col("payroll_present_h2").cast("int"),
        F.col("payroll_stopped_flag").cast("int"),
        F.col("limit_util_first_7d_flag").cast("int"),
        F.col("ever_paid_flag").cast("int"),
        F.col("max_7d_spend_ratio").cast("double"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("computed_at"),
    )


# ── Private: Pass A ───────────────────────────────────────────────────────────


def _build_pass_a(prm_transaction: DataFrame, spell_w: DataFrame) -> DataFrame:
    """CC departure signals and H2 fee amount from crx_cc_transactions.

    Business purpose: captures intent to leave UAE before the delinquency onset (T0).
    At 61+ DPD accounts go Block-X (no new transactions), so departure signals must
    come from the pre-delinquency window.  A customer booking flights or making
    foreign transactions in the 3 months before T0 is a strong flight-risk indicator.

    Window terminology (same as module header):
        M0      = trunc(t0, 'month')                  — onset month (excluded from all windows)
        H2      = [M0-3m, M0) → m_from_m0 in [1, 3]   — T0-anchored (fee signals only)
        H1      = [w_pre_start, M0-3m) → m_from_m0 >= 4 — baseline
        W_pre   = [w_pre_start, obs_ceil)             — extended to spine_obs_date (covers T0→block gap)
        H2_blk  = [block-3m, block) → m_from_block in [1, 3] — block-anchored (travel signals)
        block   = t0 + days_to_dpd60                  — card-block date

    Detection strategy (Sub-pass A1):
        Primary — MCC-based: travel MCCs (ISO 18245: airlines 3000–3299/4511,
            cruise 4411, travel agencies 4722) identify explicit travel bookings.
        Fallback — txn_description keyword: catches transactions where the MCC is
            absent or miscoded (common for aggregated/wallet payments).  Mirrors the
            dual particular-code + narration pattern used for salary in Pass B.
        Combined: is_travel = is_travel_mcc | is_travel_desc

    Sub-pass A1 — departure:
        travel_mcc_flag_h2          : 1 if any H2_blk txn matches travel MCC or keyword;
                                      0 if H2_blk txns exist but none match;
                                      NULL if no H2_blk txns (left-join result — treat as 0
                                      downstream; do NOT coalesce to 0 here to distinguish
                                      "no travel" from "no data").
                                      Anchored on block_date (not T0) — captures bookings in
                                      the T0→block window that T0-anchoring missed.
        foreign_txn_share_h2        : mean(is_international) over H2_blk txns;
                                      NULL if no H2_blk txns (avg of empty set).
                                      Anchored on block_date for same reason as above.
        last_txn_foreign_flag       : is_international of the last transaction before
                                      spine_obs_date (extended from old M0 ceiling);
                                      NULL if no W_pre transactions at all.

    Sub-pass A2 — fee velocity intermediate:
        _fee_amt_h2                 : sum(abs(txn_amount_aed)) for H2 fee transactions;
                                      0.0 if H2 transactions exist but none are fee-type
                                      (coalesced in aggregation, never NULL).
                                      Still T0-anchored [M0-3m, M0) — unchanged; used by
                                      Pass D to compute fee_accel_h2.
    """
    scope = spell_w.select("account_id").distinct()

    txn = prm_transaction.select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("merchant_category_code"),
        F.col("is_international"),
        F.col("txn_amount_aed"),
        F.col("txn_category"),
        F.col("txn_description"),
    ).join(
        F.broadcast(scope),
        prm_transaction["contract_id"] == scope["account_id"],
        "leftsemi",
    )

    # Join to spell and filter to W_pre: [w_pre_start, _obs_ceil)
    # _obs_ceil extends the right boundary to spine_obs_date (fallback: block_date)
    # so transactions in the T0→card-block gap are captured for last_txn_foreign_flag
    # and the block-anchored travel window.
    txn_w = (
        txn.join(spell_w, on=(txn["contract_id"] == spell_w["account_id"]), how="inner")
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("merchant_category_code"),
            F.col("is_international"),
            F.col("txn_amount_aed"),
            F.col("txn_category"),
            F.col("txn_description"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
            F.col("block_date"),
            F.coalesce(F.col("spine_obs_date"), F.col("block_date")).alias("_obs_ceil"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.col("_obs_ceil"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
        .withColumn(
            "m_from_block",
            F.floor(
                F.months_between(
                    F.trunc(F.col("block_date"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
    )

    # Travel detection: MCC-based (primary) OR txn_description keyword fallback.
    # The narration fallback mirrors the salary narration pattern in Pass B,
    # covering cases where the MCC is absent or miscoded.
    mcc_int_col = F.col("merchant_category_code").cast("int")
    is_travel = (mcc_int_col.isNotNull() & mcc_int_col.isin(_TRAVEL_MCCS)) | F.upper(
        F.coalesce(F.col("txn_description"), F.lit(""))
    ).rlike(_TRAVEL_KEYWORDS_RE)

    # h2: T0-anchored — used only for _fee_amt_h2 (fee velocity; unchanged)
    # h2_block: block_date-anchored — used for travel features
    h2 = (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3)
    h2_block = (F.col("m_from_block") >= 1) & (F.col("m_from_block") <= 3)

    # Fee detection: exact category first, narration fallback (FI-7)
    fee_cond = (F.col("txn_category") == F.lit(_FEE_CATEGORY)) | F.upper(
        F.coalesce(F.col("txn_description"), F.lit(""))
    ).rlike(r"(?i)\bFEE\b|\bCHARGE\b|\bANNUAL\b")

    # Window to identify last transaction per spell (for last_txn_foreign_flag)
    txn_ranked = txn_w.withColumn(
        "_last_rank",
        F.row_number().over(
            Window.partitionBy("account_id", "spell_id").orderBy(
                F.col("txn_date").desc()
            )
        ),
    )

    agg = txn_ranked.groupBy("account_id", "spell_id").agg(
        # A1 — departure signals (block_date-anchored for travel; obs_date ceiling for last-txn)
        F.max(F.when(h2_block & is_travel, F.lit(1)).otherwise(F.lit(0))).alias(
            "travel_mcc_flag_h2"
        ),
        F.avg(F.when(h2_block, F.col("is_international").cast("double"))).alias(
            "foreign_txn_share_h2"
        ),
        F.first(
            F.when(F.col("_last_rank") == 1, F.col("is_international").cast("int")),
            ignorenulls=True,
        ).alias("last_txn_foreign_flag"),
        # A2 — H2 fee amount (internal; used by Pass D)
        F.sum(
            F.when(h2 & fee_cond, F.abs(F.col("txn_amount_aed"))).otherwise(F.lit(0.0))
        ).alias("_fee_amt_h2"),
    )

    return agg.select(
        "account_id",
        "spell_id",
        "travel_mcc_flag_h2",
        "foreign_txn_share_h2",
        "last_txn_foreign_flag",
        "_fee_amt_h2",
    )


# ── Private: Pass B ───────────────────────────────────────────────────────────


def _build_pass_b(  # pylint: disable=too-many-locals
    comp_financial_tran_repos_dly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """CASA inflow stop signals from raw transaction table (conditional).

    Business purpose: captures salary disruption and End-of-Service Benefit (EOSB)
    patterns in the customer's CASA account before T0.  A salary stopping or a large
    terminal credit (EOSB payout) shortly before delinquency onset is a strong
    indicator of job loss / departure — directly correlated with cure probability.

    Detection strategy: dual-signal salary identification mirrors WM income.py ENBD
    entity logic (FI-1 resolved 2026-08-21).  A transaction is salary if:
      (1) credit side (tran_dc == 'C') AND not an excluded code AND
      (2) either a known salary particular_code OR tran_narration_1 matches a
          salary keyword regex (SALARY|PAYROLL|INCENTIVE|BONUS|OVERTIME|COMMISSION …).
    This two-path approach handles both structured SWIFT credits (code present) and
    direct/payroll credits that arrive with no structured code but a descriptive narration.

    R20 compliance: CIF-level leftsemi scope applied *before* any date filter
    to limit the 2.4B-row scan.

    Schema guard: if required CASA columns are absent, emits NULL for both
    features and logs a warning.

    Features::

        casa_inflow_stop_gap_d  : days between last salary-like credit and M0;
                                  NULL if no salary-like inflow found in [M0-24, M0).
        eosb_like_flag          : 1 if any single salary credit in [M0-6, M0)
                                  exceeds 3× the monthly median over [M0-24, M0-6)
                                  AND casa_inflow_stop_gap_d <= 90 days;
                                  0 if data present but condition not met;
                                  NULL if monthly_salary_median cannot be computed
                                  (i.e. fewer than one salary month in the baseline window).
    """
    _CASA_REQUIRED = [
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ]
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    missing = [c for c in _CASA_REQUIRED if c not in casa_cols_lower]

    if missing:
        LOG.warning(
            "Pass B [CASA]: missing columns %s in comp_financial_tran_repos_dly "
            "— emitting NULL for casa_inflow_stop_gap_d and eosb_like_flag",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("casa_inflow_stop_gap_d", F.lit(None).cast("double"))
            .withColumn("eosb_like_flag", F.lit(None).cast("int"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select("cif_id").distinct()

    # R20 — scope CASA via CIF IDs before any other filter
    casa_scoped = comp_financial_tran_repos_dly.select(
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # Salary detection — mirrors WM income.py ENBD entity logic (FI-1 resolved 2026-08-21):
    # credit transaction AND NOT an excluded code AND (positive code OR narrative match)
    is_salary = (
        (F.col("tran_dc") == _TRAN_DC_CREDIT)
        & ~F.col("tran_particular_code").isin(_SALARY_EXCLUDE_CODES)
        & (
            F.col("tran_particular_code").isin(_SALARY_CODES)
            | F.upper(F.coalesce(F.col("tran_narration_1"), F.lit(""))).rlike(
                r"SALARY|PAYROLL|SALAR|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK"
            )
        )
    )

    # Join to spell_cif to get (account_id, spell_id, t0) per transaction
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.withColumnRenamed("_ctr_id", "account_id"),
        on="account_id",
        how="left",
    )

    casa_w = (
        casa_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("tran_dc") == _TRAN_DC_CREDIT)
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn("is_salary", is_salary)
    )

    # ── Gap feature: last salary credit date ──────────────────────────────────
    last_sal = (
        casa_w.filter(F.col("is_salary"))
        .groupBy("account_id", "spell_id", "t0")
        .agg(F.max("tran_date").alias("last_sal_date"))
        .withColumn(
            "casa_inflow_stop_gap_d",
            F.datediff(F.trunc(F.col("t0"), "month"), F.col("last_sal_date")).cast(
                "double"
            ),
        )
        .select("account_id", "spell_id", "casa_inflow_stop_gap_d")
    )

    # ── EOSB flag: monthly salary median [M0-24, M0-6) vs large credit in [M0-6, M0)
    monthly_sal = (
        casa_w.filter(F.col("is_salary"))
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("tran_date"), "month"),
                )
            ).cast("int"),
        )
        .groupBy("account_id", "spell_id", "m_from_m0")
        .agg(F.sum("tran_amt_aed").alias("monthly_sal_total"))
    )

    # Baseline median: m_from_m0 in [7, 24] → months [M0-24m, M0-6m)
    sal_median = (
        monthly_sal.filter((F.col("m_from_m0") >= 7) & (F.col("m_from_m0") <= 24))
        .groupBy("account_id", "spell_id")
        .agg(
            F.percentile_approx("monthly_sal_total", 0.5).alias("monthly_salary_median")
        )
    )

    # Max single salary credit in recent window: m_from_m0 in [1, 6] → [M0-6m, M0)
    recent_max = (
        casa_w.filter(
            F.col("is_salary")
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -6))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.max("tran_amt_aed").alias("max_sal_recent"))
    )

    eosb = (
        spell_w.select("account_id", "spell_id")
        .join(last_sal, on=["account_id", "spell_id"], how="left")
        .join(sal_median, on=["account_id", "spell_id"], how="left")
        .join(recent_max, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "eosb_like_flag",
            F.when(
                # Cannot evaluate if no baseline median
                F.col("monthly_salary_median").isNull(),
                F.lit(None).cast("int"),
            )
            .when(
                # Condition met: single large credit + salary stopped recently
                F.col("max_sal_recent").isNotNull()
                & (F.col("monthly_salary_median") > 0)
                & (F.col("max_sal_recent") > 3.0 * F.col("monthly_salary_median"))
                & F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= 90.0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "spell_id", "casa_inflow_stop_gap_d", "eosb_like_flag")
    )

    return eosb


# ── Private: Pass C ───────────────────────────────────────────────────────────


def _build_pass_c(crx_cc_spell_table: DataFrame, spell_w: DataFrame) -> DataFrame:
    """History shape features from crx_cc_spell_table self-window.

    Business purpose: characterises the delinquency history pattern of the account.
    Repeat delinquency within 24 months signals systemic financial stress rather than
    a one-off event; rapid roll speed (days to reach 30/60 DPD) predicts trajectory
    toward 180+ DPD.  These features are available without any new data sources —
    pure self-joins on the already-built spell table.

    Detection strategy: self-join on crx_cc_spell_table using (account_id, spell_id)
    to find prior spells.  prior_spell_cnt_24m counts by spell_id < current and t0
    within the 24-month lookback.  roll_speed_* are direct pass-throughs computed
    by T03b (days from first missed payment to each DPD threshold).

    All features are free reads from the existing spell table — no new data sources.

    Features::

        prior_spell_cnt_24m     : count of prior spells (same account_id, lower
                                  spell_id) whose t0 falls in [t0_current-24m, t0_current);
                                  0 if no qualifying prior spells (never NULL — coalesced).
        months_since_prior_spell: floor(months_between(t0, prior_spell_end));
                                  NULL for first spell (prior_spell_end is NULL in T03b).
        roll_speed_30_d         : days_to_dpd30 pass-through from spell table;
                                  NULL if the account never reached 30 DPD in this spell.
        roll_speed_60_d         : days_to_dpd60 pass-through from spell table;
                                  NULL if the account never reached 60 DPD in this spell.
    """
    # All spells (including censored) — used only for prior-spell counting
    prior_candidates = crx_cc_spell_table.select(
        F.col("account_id"),
        F.col("spell_id").alias("prior_spell_id"),
        F.col("t0").alias("prior_t0"),
    )

    current = spell_w.select("account_id", "spell_id", "t0")

    prior_cnt = (
        current.join(prior_candidates, on="account_id", how="left")
        .filter(
            (F.col("prior_spell_id") < F.col("spell_id"))
            & (F.col("prior_t0") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("prior_t0") < F.col("t0"))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.count("prior_spell_id").alias("prior_spell_cnt_24m"))
    )

    result = (
        spell_w.select(
            "account_id",
            "spell_id",
            "t0",
            "prior_spell_end",
            "days_to_dpd30",
            "days_to_dpd60",
        )
        .join(prior_cnt, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "prior_spell_cnt_24m",
            # 0 for first spells or accounts with no recent prior spells
            F.coalesce(F.col("prior_spell_cnt_24m"), F.lit(0)),
        )
        .withColumn(
            "months_since_prior_spell",
            F.when(
                F.col("prior_spell_end").isNotNull(),
                F.floor(F.months_between(F.col("t0"), F.col("prior_spell_end"))).cast(
                    "int"
                ),
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumnRenamed("days_to_dpd30", "roll_speed_30_d")
        .withColumnRenamed("days_to_dpd60", "roll_speed_60_d")
    )

    return result.select(
        "account_id",
        "spell_id",
        "prior_spell_cnt_24m",
        "months_since_prior_spell",
        "roll_speed_30_d",
        "roll_speed_60_d",
    )


# ── Private: Pass D ───────────────────────────────────────────────────────────


def _build_pass_d(
    prm_contract: DataFrame,
    prm_turnovers: DataFrame,
    spell_w: DataFrame,
    fee_feats: DataFrame,
) -> DataFrame:
    """Tenure and lifetime fee velocity features.

    Business purpose: captures whether the customer has a history of incurring
    late/overlimit fees relative to their account lifetime.  A high fee_rate_life
    signals chronic near-limit behaviour; fee_accel_h2 > 1 means fees
    accelerated in the 3 months before T0, an early stress indicator.  Tenure
    contextualises risk: short-tenure accounts with high fees are higher risk than
    long-tenure accounts with the same absolute fee amount.

    PIT join pattern:
        prm_contract  : take row with latest observation_date <= t0 per account
        prm_turnovers : take row with latest observation_date <= t0 per account

    fee_feats is (account_id, spell_id, _fee_amt_h2) from Pass A.

    Features::

        tenure_at_t0_m          : floor(months_between(M0, account_open_date));
                                  NULL if account_open_date is NULL in prm_contract.
        fee_rate_life           : (ltd_late_fee_amount + ltd_overlimit_fee_amount)
                                  / max(tenure_at_t0_m, 1);
                                  0.0 if both fee columns are NULL (coalesced to 0);
                                  NULL if no prm_contract snapshot on or before t0.
        fee_accel_h2            : (H2 fees / H2 months) / fee_rate_life;
                                  H2 months = min(w_pre_clean_m, 3) to avoid
                                  over-denominating short windows;
                                  NULL if fee_rate_life is NULL or zero, or if
                                  _fee_amt_h2 is NULL, or if _h2_months is 0.
    """
    spell_base = spell_w.select(
        F.col("account_id"),
        F.col("spell_id"),
        F.col("t0"),
        F.col("w_pre_clean_m"),
    )

    scope = spell_base.select("account_id").distinct()

    # ── Tenure: PIT join prm_contract (snapshot via observation_date) ─────────
    # prm_contract uses observation_date (renamed from banking_date in primary layer).
    # Take latest snapshot on or before t0 per account.
    contract_scoped = prm_contract.select(
        F.col("contract_id").alias("_ctr_id"),
        F.col(_CONTRACT_OPEN_DATE_COL).alias("account_open_date"),
        F.col("observation_date").alias("_eff_start"),
    ).join(
        F.broadcast(scope),
        F.col("_ctr_id") == F.col("account_id"),
        "leftsemi",
    )

    contract_pit = (
        spell_base.join(
            contract_scoped,
            on=(spell_base["account_id"] == contract_scoped["_ctr_id"]),
            how="left",
        )
        .filter(F.col("_eff_start") <= F.col("t0"))
        .withColumn(
            "_rn_ctr",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_eff_start").desc()
                )
            ),
        )
        .filter(F.col("_rn_ctr") == 1)
        .withColumn(
            "tenure_at_t0_m",
            F.when(
                F.col("account_open_date").isNotNull(),
                F.floor(
                    F.months_between(
                        F.trunc(F.col("t0"), "month"),
                        F.trunc(F.col("account_open_date"), "month"),
                    )
                ).cast("int"),
            ).otherwise(F.lit(None).cast("int")),
        )
        .select("account_id", "spell_id", "tenure_at_t0_m")
    )

    # ── Lifetime fees: PIT join prm_turnovers ─────────────────────────────────
    # prm_turnovers exposes the two fee-type columns; no pre-computed total exists.
    # Both are stored positive in the primary layer (Way4 sign=-1 absorbed upstream).
    turnovers_scoped = prm_turnovers.select(
        F.col("contract_id").alias("_tov_id"),
        F.col(_TURNOVERS_SNAPSHOT_COL).alias("_snap_date"),
        F.col("ltd_late_fee_amount"),
        F.col("ltd_overlimit_fee_amount"),
    ).join(
        F.broadcast(scope),
        F.col("_tov_id") == F.col("account_id"),
        "leftsemi",
    )

    turnovers_pit = (
        spell_base.join(
            turnovers_scoped,
            on=(spell_base["account_id"] == turnovers_scoped["_tov_id"]),
            how="left",
        )
        .filter(F.col("_snap_date") <= F.col("t0"))
        .withColumn(
            "_rn_tov",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_snap_date").desc()
                )
            ),
        )
        .filter(F.col("_rn_tov") == 1)
        .withColumn(
            "_ltd_fees_charged",
            F.coalesce(F.col("ltd_late_fee_amount"), F.lit(0.0))
            + F.coalesce(F.col("ltd_overlimit_fee_amount"), F.lit(0.0)),
        )
        .select("account_id", "spell_id", "_ltd_fees_charged")
    )

    # ── Combine and derive velocity features ──────────────────────────────────
    result = (
        spell_base.join(contract_pit, on=["account_id", "spell_id"], how="left")
        .join(turnovers_pit, on=["account_id", "spell_id"], how="left")
        .join(fee_feats, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "fee_rate_life",
            # _ltd_fees_charged is always non-null (coalesced); 0 for no-fee accounts
            F.col("_ltd_fees_charged")
            / F.greatest(F.col("tenure_at_t0_m").cast("double"), F.lit(1.0)),
        )
        # H2 denominator: actual clean months in H2 (≤ 3); avoids over-denominating
        .withColumn(
            "_h2_months",
            F.when(
                F.col("w_pre_clean_m") < 3, F.col("w_pre_clean_m").cast("double")
            ).otherwise(F.lit(3.0)),
        )
        .withColumn(
            "fee_accel_h2",
            F.when(
                F.col("fee_rate_life").isNotNull()
                & (F.col("fee_rate_life") > 0.0)
                & F.col("_fee_amt_h2").isNotNull()
                & (F.col("_h2_months") > 0.0),
                (F.col("_fee_amt_h2") / F.col("_h2_months")) / F.col("fee_rate_life"),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    return result.select(
        "account_id",
        "spell_id",
        "tenure_at_t0_m",
        "fee_rate_life",
        "fee_accel_h2",
    )


# ── Private: Pass E ───────────────────────────────────────────────────────────


def _build_pass_e(
    int_bureau_pull_monthly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """AECB leverage slope via OLS of bureau_total_balance vs months before T0.

    Business purpose: detects whether the customer's total bureau-reported liabilities
    were growing or shrinking in the 24 months before T0.  An upward slope (leverage
    accumulation) correlates with inability to cure; a downward slope (deleveraging)
    may indicate active debt management.

    T21 DROP — CONFIRMED. Coverage: 0.11% cc_180_plus, 0.46% cc_60_180 (T06b 2026-08-24).
    Genuine data absence; not fixable by bridge repair. Code retained solely for output
    schema stability. All values are NULL in production. Remove at T21.

    Detection strategy: OLS computed via Spark accumulators (_n, _sx, _sy, _sxy, _sx2)
    to avoid collecting data to the driver.  x-variable = m_from_m0 (positive integer,
    ≥ 1; larger = further from T0).  Same pattern as T05 util_slope.
    Positive slope = balance was growing toward T0 (increasing leverage).
    Negative slope = balance was shrinking toward T0 (deleveraging).

    Features::

        aecb_leverage_slope     : OLS β₁ of bureau_total_balance on m_from_m0;
                                  NULL if fewer than 2 non-null pulls in [M0-24m, M0)
                                  or if the OLS denominator is zero (all pulls same month).

    One pull per (account_id, spell_id, m_from_m0) — deduped to latest in month.
    """
    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select("cif_id").distinct()

    # Scope bureau via CIF IDs (leftsemi before date filter)
    bureau_scoped = int_bureau_pull_monthly.select(
        "cif_id", "pull_date", "bureau_total_balance"
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # Join spell_cif to get (account_id, spell_id, t0) per pull
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.withColumnRenamed("_ctr_id", "account_id"),
        on="account_id",
        how="left",
    )

    bureau_w = (
        bureau_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pull_date") < F.trunc(F.col("t0"), "month"))
            & (F.col("pull_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & F.col("bureau_total_balance").isNotNull()
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("pull_date"), "month"),
                )
            ).cast("int"),
        )
        # Dedup to one pull per (account_id, spell_id, month) — take latest pull
        .withColumn(
            "_rn_bur",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id", "m_from_m0").orderBy(
                    F.col("pull_date").desc()
                )
            ),
        )
        .filter(F.col("_rn_bur") == 1)
    )

    # OLS accumulators (x = m_from_m0)
    agg = bureau_w.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_n"),
        F.sum(F.col("m_from_m0").cast("double")).alias("_sx"),
        F.sum(F.col("bureau_total_balance")).alias("_sy"),
        F.sum(F.col("m_from_m0").cast("double") * F.col("bureau_total_balance")).alias(
            "_sxy"
        ),
        F.sum(
            F.col("m_from_m0").cast("double") * F.col("m_from_m0").cast("double")
        ).alias("_sx2"),
    )

    _denom = F.col("_n").cast("double") * F.col("_sx2") - F.col("_sx") * F.col("_sx")

    slope = agg.withColumn(
        "aecb_leverage_slope",
        F.when(
            (F.col("_n") >= 2) & (_denom != 0.0),
            (F.col("_n").cast("double") * F.col("_sxy") - F.col("_sx") * F.col("_sy"))
            / _denom,
        ).otherwise(F.lit(None).cast("double")),
    ).select("account_id", "spell_id", "aecb_leverage_slope")

    # Left join to emit NULL for spells with no bureau pulls
    return spell_w.select("account_id", "spell_id").join(
        slope, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass F ───────────────────────────────────────────────────────────


def _build_pass_f(feat_product_holding: DataFrame, spell_w: DataFrame) -> DataFrame:
    """Relationship breadth from feat_product_holding.

    Business purpose: captures the customer's product footprint at the bank at T0.
    Customers with a deeper relationship (multiple products: mortgage, personal loan,
    auto, CASA) are less likely to default strategically — they have more to lose and
    may respond better to in-house collection.  Single-product (CC-only) customers
    with no other bank ties are higher flight risk.

    Schema guard: if total_products column or a recognised join key / observation
    date column is absent, emits NULL and logs a warning.

    PIT join: latest obs_date <= t0 per (account_id, spell_id).

    Feature::

        relationship_breadth    : total_products cast to int at T0;
                                  NULL if no snapshot on or before T0, or if the
                                  required column / join key is absent (schema guard).
    """
    ph_cols_lower = {c.lower() for c in feat_product_holding.columns}

    # Schema guard: total_products required
    if "total_products" not in ph_cols_lower:
        LOG.warning(
            "Pass F: feat_product_holding missing 'total_products' column "
            "— relationship_breadth = NULL (<<FILL-IN: verify catalog key>>)"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    # Resolve join key
    ph_key = None
    for candidate in ("account_id", "contract_id"):
        if candidate in ph_cols_lower:
            ph_key = candidate
            break

    if ph_key is None:
        LOG.warning(
            "Pass F: feat_product_holding missing account_id/contract_id key "
            "— relationship_breadth = NULL"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    # Resolve observation date column
    ph_obs = None
    for candidate in ("obs_date", "observation_date", "snapshot_date", "edp_load_date"):
        if candidate in ph_cols_lower:
            ph_obs = candidate
            break

    if ph_obs is None:
        LOG.warning(
            "Pass F: feat_product_holding missing observation date column "
            "— relationship_breadth = NULL"
        )
        return spell_w.select("account_id", "spell_id").withColumn(
            "relationship_breadth", F.lit(None).cast("int")
        )

    scope = spell_w.select("account_id").distinct()

    ph_scoped = feat_product_holding.select(
        F.col(ph_key).alias("_ph_key"),
        F.col(ph_obs).alias("_ph_obs"),
        F.col("total_products").cast("int").alias("_total_products"),
    ).join(
        F.broadcast(scope),
        F.col("_ph_key") == F.col("account_id"),
        "leftsemi",
    )

    spell_dates = spell_w.select("account_id", "spell_id", "t0")

    ph_pit = (
        ph_scoped.join(
            spell_dates,
            on=(ph_scoped["_ph_key"] == spell_dates["account_id"]),
            how="inner",
        )
        .filter(F.col("_ph_obs") <= F.col("t0"))
        .withColumn(
            "_rn_ph",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_ph_obs").desc()
                )
            ),
        )
        .filter(F.col("_rn_ph") == 1)
        .select(
            "account_id",
            "spell_id",
            F.col("_total_products").alias("relationship_breadth"),
        )
    )

    return spell_w.select("account_id", "spell_id").join(
        ph_pit, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass G ───────────────────────────────────────────────────────────

# Column names in fea_monthly_aecb_alerts (from retail.feature_space aecb_alert pipeline)
_ALERT_NEW_ENQUIRY_COL = "aecb_alert_new_inquiry_alert_flag"
_ALERT_CREDIT_OPENED_COL = "aecb_credit_facility_opened_alert_flag"
_ALERT_TOTAL_COL = "aecb_total_alerts_flag"


def _build_pass_g(  # pylint: disable=too-many-locals
    fea_monthly_aecb_alerts: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """AECB alert-based signals from fea_monthly_aecb_alerts (REUSE — retail.feature_space).

    Business purpose: captures external credit-market activity (new enquiries, new
    facilities) in the 3 months before T0.  A spike in new credit enquiries or newly
    opened facilities just before delinquency onset suggests the customer was seeking
    alternative credit — either to service existing debt or in anticipation of financial
    stress.  These are bureau-derived, unbiased by internal bank behaviour, making them
    strong early-warning signals independent of transactional history.

    R2 PASS: month_number is the last day of each calendar month (yyyyMMdd).
    Filter ``F.to_date(month_number,'yyyyMMdd') < F.trunc(t0,'month')`` is strict <
    T0 month, so no post-T0 leakage is possible.
    R7 PASS: source is sa_ops_aecb_alert (prvdr_subj_num, alert_desc, contract_type,
    extract_dt). No nationality, visa, residency, iqama, or expat inputs.
    Coverage: 92.99% (T06c, cc_60_180).

    Window: 3 calendar months immediately before T0 — [M0-3m, M0).
    cif_id type: fea_monthly_aecb_alerts stores cif_id as IntegerType; normalised to
    string for the join to match prm_client.cif_id convention.

    Schema guard: if cif_id, month_number, or aecb_total_alerts_flag are absent,
    emits NULL for all three features and logs a warning.

    Features::

        aecb_new_enquiry_3m     : count of new-enquiry alerts in [M0-3m, M0);
                                  NULL if no alert rows in window or column absent;
                                  note: individual month values are coalesced(flag, 0)
                                  before summing, so only fully absent data produces NULL.
        aecb_credit_opened_3m   : count of credit-facility-opened alerts in [M0-3m, M0);
                                  NULL if no alert rows in window or column absent.
        aecb_total_alerts_3m    : total alert count in [M0-3m, M0);
                                  NULL if no alert rows in window (left-join result).
    """
    _ALERT_REQUIRED = ["cif_id", "month_number", _ALERT_TOTAL_COL]
    alert_cols_lower = {c.lower() for c in fea_monthly_aecb_alerts.columns}
    missing = [c for c in _ALERT_REQUIRED if c not in alert_cols_lower]

    if missing:
        LOG.warning(
            "Pass G [AECB alerts]: missing columns %s in fea_monthly_aecb_alerts "
            "— emitting NULL for aecb_new_enquiry_3m, aecb_credit_opened_3m, "
            "aecb_total_alerts_3m",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("aecb_new_enquiry_3m", F.lit(None).cast("int"))
            .withColumn("aecb_credit_opened_3m", F.lit(None).cast("int"))
            .withColumn("aecb_total_alerts_3m", F.lit(None).cast("int"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    # cif_id in fea_monthly_aecb_alerts is IntegerType — cast to string to match prm_client
    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    # Optional alert columns — coalesce to 0 if column exists but value is NULL;
    # emit NULL feature if the column is entirely absent (pivot may not produce it)
    has_new_enq = _ALERT_NEW_ENQUIRY_COL in alert_cols_lower
    has_cred_open = _ALERT_CREDIT_OPENED_COL in alert_cols_lower

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("alert_month"),
        (
            F.coalesce(F.col(_ALERT_NEW_ENQUIRY_COL), F.lit(0)).alias("_new_enq")
            if has_new_enq
            else F.lit(None).cast("int").alias("_new_enq")
        ),
        (
            F.coalesce(F.col(_ALERT_CREDIT_OPENED_COL), F.lit(0)).alias("_cred_open")
            if has_cred_open
            else F.lit(None).cast("int").alias("_cred_open")
        ),
        F.coalesce(F.col(_ALERT_TOTAL_COL), F.lit(0)).alias("_total"),
    ]

    alerts_scoped = fea_monthly_aecb_alerts.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # spell_cif: (account_id, spell_id, t0) per CIF
    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # R2: 3-month window strictly before T0
    alerts_w = alerts_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        (F.col("alert_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("alert_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    agg = alerts_w.groupBy("account_id", "spell_id").agg(
        F.sum("_new_enq").alias("aecb_new_enquiry_3m"),
        F.sum("_cred_open").alias("aecb_credit_opened_3m"),
        F.sum("_total").alias("aecb_total_alerts_3m"),
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass H ───────────────────────────────────────────────────────────


def _build_pass_h(
    feat_fx_leakage: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Cross-border CASA outflow signals from fea_monthly_agg_fx_leakage.

    Business purpose: captures fund outflows to foreign accounts in the 3 months
    before T0.  Cross-border transfers are a direct capital-flight signal — a customer
    remitting large amounts abroad while accumulating card debt is a strong flight risk.
    LGBM importance 156.5, IV 0.035 (existing model, 12-month window).  This pass uses
    the H2 (3-month) window for tighter T0 proximity.

    Source: feat_fx_leakage = fea_monthly_agg_fx_leakage (retail.feature_space).
    The table carries pre-rolled features; _FX_CB_AMT_COL is a 3-month rolling sum
    (in_last_0_2_months), which equals the H2 = [M0-3m, M0) window when read at the
    last H2 month (most recent month_number strictly before M0).

    Approach: point-in-time join — find the row with the latest month_number in H2
    for each (spell, cif) and read the pre-rolled 3-month sum directly.  No re-aggregation
    needed (unlike raw-monthly sources).

    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Features::

        cross_border_outflow_amt_h2  (double) — pre-rolled 3m AED cross-border outflow;
                                                NULL if no H2 row or column absent.
        cross_border_outflow_cnt_h2  (int)    — always NULL; no count equivalent in
                                                fea_monthly_agg_fx_leakage (T21 candidate).
    """
    _REQUIRED = ["cif_id", "month_number"]
    fx_cols_lower = {c.lower() for c in feat_fx_leakage.columns}
    missing_base = [c for c in _REQUIRED if c not in fx_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass H [cross-border FX leakage]: missing base columns %s in feat_fx_leakage "
            "— emitting NULL for cross_border_outflow_amt_h2, cross_border_outflow_cnt_h2",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("cross_border_outflow_amt_h2", F.lit(None).cast("double"))
            .withColumn("cross_border_outflow_cnt_h2", F.lit(None).cast("int"))
        )

    has_amt = _FX_CB_AMT_COL in fx_cols_lower
    if not has_amt:
        LOG.warning(
            "Pass H [cross-border FX leakage]: column '%s' absent from feat_fx_leakage "
            "— cross_border_outflow_amt_h2 = NULL",
            _FX_CB_AMT_COL,
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    # cif_id in retail.feature_space tables is IntegerType — cast to string to match prm_client
    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    fx_scoped = feat_fx_leakage.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("fx_month"),
        (
            F.col(_FX_CB_AMT_COL).cast("double").alias("_cb_amt")
            if has_amt
            else F.lit(None).cast("double").alias("_cb_amt")
        ),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # Point-in-time: most recent H2 row per (spell, cif).
    # H2 = [M0-3m, M0); the pre-rolled _FX_CB_AMT_COL at that row already covers 3m.
    h2_w = spell_cif.join(fx_scoped, on="cif_id", how="inner").filter(
        (F.col("fx_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("fx_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    pit_w = Window.partitionBy("account_id", "spell_id").orderBy(
        F.col("fx_month").desc()
    )
    agg = (
        h2_w.withColumn("_rn", F.row_number().over(pit_w))
        .filter(F.col("_rn") == 1)
        .groupBy("account_id", "spell_id")
        .agg(F.first("_cb_amt").alias("cross_border_outflow_amt_h2"))
        .withColumn("cross_border_outflow_cnt_h2", F.lit(None).cast("int"))
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass H2 ──────────────────────────────────────────────────────────


def _build_pass_h2(  # pylint: disable=too-many-locals
    feat_cc_txns_rfs: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Retail.feature_space CC travel+tours MCC signals from fea_cc_inflow_outflow_txns_monthly.

    Business purpose: retail.feature_space uses a 24-category MCC taxonomy including
    a 'travel_and_tours' category that partially overlaps but is NOT identical to the
    ISO 18245 airline/cruise/agency codes used in Pass A.  Both signals together cover
    more MCCs than either alone — Pass A catches explicit booking MCCs; this pass catches
    the retail.feature_space categorisation which may include different merchant types.
    Recreation and Car Fuel from this same table are already STRONG_SIGNAL features in
    the existing model (LGBM importance 721/452), confirming the table's signal quality.

    Source: feat_cc_txns_rfs = fea_cc_inflow_outflow_txns_monthly (retail.feature_space).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: H2 = [M0-3m, M0) — 3 months immediately before T0.
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if _CC_TRAVEL_AMT_COL or _CC_TRAVEL_CNT_COL are absent, emits NULL
    and logs a warning.  Run t06d_schema_probes.py in PROD to confirm column names.

    Features::

        retail_travel_mcc_amt_h2  (double) — AED sum of travel+tours CC spend in H2;
                                             NULL if no rows in H2 or column absent.
        retail_travel_mcc_cnt_h2  (int)    — count of travel+tours CC transaction months
                                             in H2; NULL if no rows or column absent.
    """
    _REQUIRED = ["cif_id", "month_number"]
    cc_cols_lower = {c.lower() for c in feat_cc_txns_rfs.columns}
    missing_base = [c for c in _REQUIRED if c not in cc_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass H2 [CC travel MCC]: missing base columns %s in feat_cc_txns_rfs "
            "— emitting NULL for retail_travel_mcc_amt_h2, retail_travel_mcc_cnt_h2",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("retail_travel_mcc_amt_h2", F.lit(None).cast("double"))
            .withColumn("retail_travel_mcc_cnt_h2", F.lit(None).cast("int"))
        )

    has_amt = _CC_TRAVEL_AMT_COL in cc_cols_lower
    has_cnt = _CC_TRAVEL_CNT_COL in cc_cols_lower

    if not has_amt:
        LOG.warning(
            "Pass H2 [CC travel MCC]: column '%s' absent — retail_travel_mcc_amt_h2 = NULL "
            "(run t06d_schema_probes.py to confirm name)",
            _CC_TRAVEL_AMT_COL,
        )
    if not has_cnt:
        LOG.warning(
            "Pass H2 [CC travel MCC]: column '%s' absent — retail_travel_mcc_cnt_h2 = NULL "
            "(run t06d_schema_probes.py to confirm name)",
            _CC_TRAVEL_CNT_COL,
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("cc_month"),
        (
            F.col(_CC_TRAVEL_AMT_COL).cast("double").alias("_travel_amt")
            if has_amt
            else F.lit(None).cast("double").alias("_travel_amt")
        ),
        (
            F.col(_CC_TRAVEL_CNT_COL).cast("int").alias("_travel_cnt")
            if has_cnt
            else F.lit(None).cast("int").alias("_travel_cnt")
        ),
    ]

    cc_scoped = feat_cc_txns_rfs.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    spell_cif = spell_w.select("account_id", "spell_id", "t0").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    cc_w = cc_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        (F.col("cc_month") < F.trunc(F.col("t0"), "month"))
        & (F.col("cc_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
    )

    agg = cc_w.groupBy("account_id", "spell_id").agg(
        F.sum("_travel_amt").alias("retail_travel_mcc_amt_h2"),
        F.sum("_travel_cnt").alias("retail_travel_mcc_cnt_h2"),
    )

    return spell_w.select("account_id", "spell_id").join(
        agg, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass I ───────────────────────────────────────────────────────────


def _build_pass_i(
    feat_payroll_indicator: DataFrame,
    contract_cif: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Payroll presence and stop signals from pri_monthly_payroll_indicator.

    Business purpose: a salary stopping just before T0 is a strong cure-negative signal.
    `payroll_present_h2` confirms whether any payroll credit landed in the 3 months before
    T0.  `payroll_stopped_flag` is 1 if payroll was present in the baseline window (H1:
    m_from_m0 >= 4) but absent in H2 — the single strongest cure predictor (stopping salary
    ≈ job loss ≈ no cure).

    This complements Pass B (which detects EOSB/stop from raw 2.4B-row CASA table) with a
    pre-computed primary-layer signal:
      - Pass B: raw CASA, 2.4B rows, detects stop + EOSB lump sum.
      - Pass I: pre-computed, cheaper join, confirms consistency of payroll receipt.
    LGBM importance in existing model: has_payroll_credit_1m=53.6, payroll_consistency_3m=28.8.

    Source: feat_payroll_indicator = pri_monthly_payroll_indicator (retail.feature_space).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: H2 = [M0-3m, M0) for payroll_present_h2; H1 = [w_pre_start, M0-3m) for baseline.
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if _PAYROLL_HAS_COL is absent, emits NULL for both features.
    Run t06d_schema_probes.py in PROD to confirm exact column name.

    Features::

        payroll_present_h2   (int 0/1) — 1 if any H2 month shows a payroll credit;
                                         0 if H2 rows exist but no payroll found;
                                         NULL if no H2 rows in window or column absent.
        payroll_stopped_flag (int 0/1) — 1 if payroll present in H1 (m_from_m0 >= 4)
                                         but absent in H2 (m_from_m0 in [1, 3]);
                                         0 if payroll present in both or absent in both;
                                         NULL if no H1 rows (cannot assess baseline).
    """
    _REQUIRED = ["cif_id", "month_number"]
    pay_cols_lower = {c.lower() for c in feat_payroll_indicator.columns}
    missing_base = [c for c in _REQUIRED if c not in pay_cols_lower]

    if missing_base:
        LOG.warning(
            "Pass I [payroll]: missing base columns %s in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            missing_base,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    if _PAYROLL_HAS_COL not in pay_cols_lower:
        LOG.warning(
            "Pass I [payroll]: column '%s' absent in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            _PAYROLL_HAS_COL,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    pay_scoped = feat_payroll_indicator.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("pay_month"),
        F.col(_PAYROLL_HAS_COL).cast("int").alias("_has_payroll"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    spell_cif = spell_w.select("account_id", "spell_id", "t0", "w_pre_start").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # Full pre-delinquency window [w_pre_start, M0)
    pay_w = (
        pay_scoped.join(spell_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pay_month") >= F.trunc(F.col("w_pre_start"), "month"))
            & (F.col("pay_month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.col("pay_month"),
                )
            ).cast("int"),
        )
    )

    agg = pay_w.groupBy("account_id", "spell_id").agg(
        # H2: m_from_m0 in [1, 3] — recent 3 months
        F.max(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("_has_payroll"),
            )
        ).alias("_h2_max"),
        # H1: m_from_m0 >= 4 — baseline
        F.max(F.when(F.col("m_from_m0") >= 4, F.col("_has_payroll"))).alias("_h1_max"),
        F.count(F.when(F.col("m_from_m0") >= 4, F.lit(1))).alias("_h1_row_count"),
    )

    result = (
        agg.withColumn(
            "payroll_present_h2",
            F.when(
                F.col("_h2_max").isNotNull(), F.col("_h2_max").cast("int")
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumn(
            "payroll_stopped_flag",
            F.when(
                # No H1 data — cannot assess whether payroll stopped
                F.col("_h1_row_count").isNull() | (F.col("_h1_row_count") == 0),
                F.lit(None).cast("int"),
            )
            .when(
                # Payroll present in H1 but absent/zero in H2 → stopped
                (F.col("_h1_max") == 1) & (F.coalesce(F.col("_h2_max"), F.lit(0)) == 0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "spell_id", "payroll_present_h2", "payroll_stopped_flag")
    )

    return spell_w.select("account_id", "spell_id").join(
        result, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass J ───────────────────────────────────────────────────────────


def _build_pass_j(  # pylint: disable=too-many-locals
    prm_digital_login_monthly: DataFrame,
    contract_cif: DataFrame,  # pre-built: contract_id → cif_id
    spell_w: DataFrame,
) -> DataFrame:
    """Foreign login detection from prm_digital_login_monthly (OMB login logs).

    Business purpose: a customer logging in from outside UAE before the spine observation
    date is a departure-intent proxy — digital access from a foreign IP indicates
    continued presence abroad or imminent relocation.  Unlike transactions (blocked at
    61+ DPD), login can occur after card block, so the window extends to spine_obs_date
    (fallback: M0 if spine_obs_date is NULL).

    Source: prm_digital_login_monthly (digital_login pipeline output).
    Grain: cif_id × month_number (yyyyMMdd last day of month).
    Window: all months before spine_obs_date — most recent login picked (no lower bound).
    CIF bridge: reuses pre-built _contract_cif (contract_id → cif_id).

    Schema guard: if cif_id, month_number, or last_login_foreign_flag are absent,
    emits NULL for both features and logs a warning.

    Features::

        foreign_login_flag    (int 0/1) — is_foreign_login of the most recent login
                                          before spine_obs_date;
                                          1 = latest login was from outside UAE;
                                          0 = latest login was from within UAE;
                                          NULL if no logins found before obs_date.
        last_login_country_h2 (str)     — countrylocation of most recent pre-obs login;
                                          NULL if no logins or country data absent.
                                          Not encoded — consumers (T07 class rules,
                                          segment inspection) decide encoding strategy.
    """
    _REQUIRED = ["cif_id", "month_number", "last_login_foreign_flag"]
    login_cols_lower = {c.lower() for c in prm_digital_login_monthly.columns}
    missing = [c for c in _REQUIRED if c not in login_cols_lower]

    if missing:
        LOG.warning(
            "Pass J [foreign login]: missing columns %s in prm_digital_login_monthly "
            "— emitting NULL for foreign_login_flag, last_login_country_h2",
            missing,
        )
        return (
            spell_w.select("account_id", "spell_id")
            .withColumn("foreign_login_flag", F.lit(None).cast("int"))
            .withColumn("last_login_country_h2", F.lit(None).cast("string"))
        )

    # Scope the pre-built CIF bridge to accounts in this spell window
    scope = spell_w.select("account_id").distinct()
    _ctr_cif = (
        contract_cif.join(
            F.broadcast(scope),
            contract_cif["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .select(F.col("contract_id").alias("_ctr_id"), "cif_id")
        .distinct()
    )

    cif_scope = _ctr_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    has_country = "last_login_country" in login_cols_lower

    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("login_month"),
        F.col("last_login_foreign_flag").cast("int").alias("_foreign_flag"),
        (
            F.col("last_login_country").cast("string").alias("_login_country")
            if has_country
            else F.lit(None).cast("string").alias("_login_country")
        ),
    ]

    login_scoped = prm_digital_login_monthly.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # spell_cif: (account_id, spell_id, t0, spine_obs_date) per CIF
    spell_cif = spell_w.select("account_id", "spell_id", "t0", "spine_obs_date").join(
        _ctr_cif.select(
            F.col("_ctr_id").alias("account_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        ),
        on="account_id",
        how="left",
    )

    # All pre-obs months — no lower bound; pick most recent login before spine_obs_date.
    # Login can occur post-card-block (digital channel stays active after Block-X).
    # NULL-safe fallback to M0 if spine_obs_date is absent.
    _obs_ceil_j = F.coalesce(
        F.trunc(F.col("spine_obs_date"), "month"),
        F.trunc(F.col("t0"), "month"),
    )
    login_w = login_scoped.join(spell_cif, on="cif_id", how="inner").filter(
        F.col("login_month") < _obs_ceil_j
    )

    # Most recent H2 login month per (account_id, spell_id)
    w_recent = Window.partitionBy("account_id", "spell_id").orderBy(
        F.col("login_month").desc()
    )
    most_recent = (
        login_w.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(
            "account_id",
            "spell_id",
            F.col("_foreign_flag").alias("foreign_login_flag"),
            F.col("_login_country").alias("last_login_country_h2"),
        )
    )

    return spell_w.select("account_id", "spell_id").join(
        most_recent, on=["account_id", "spell_id"], how="left"
    )


# ── Private: Pass K ───────────────────────────────────────────────────────────


def _build_pass_k(  # pylint: disable=too-many-locals
    crx_cc_transactions: DataFrame,
    prm_contract: DataFrame,
    spell_w: DataFrame,
) -> DataFrame:
    """Bust-out / fraudster utilisation signals from crx_cc_transactions + prm_contract.

    Business purpose: identifies accounts fraudulently opened and immediately exhausted
    (bust-out pattern).  Cure probability ≈ 0% for these accounts.  The 2022–2023
    origination spike included a material population: limit consumed in 1–2 days or
    concentrated in a single week, followed by zero repayment.  Identifying them prevents
    waste of collection effort and removes a confounding population from the cure model.

    Detection strategy:
    - ever_paid_flag: was any payment made in W_pre?  0 = never paid.
    - limit_util_first_7d_flag: did the account consume 80%+ of its lifetime peak
      spend within the first 7 days of opening?  (Total W_pre abs spend used as a
      proxy for limit — prm_limit may post-date the bust-out period.)
    - max_7d_spend_ratio: peak rolling 7-day spend / total W_pre spend.  Captures
      concentration of spend into a short burst window regardless of account age.

    Sign convention: txn_amount_aed > 0 = purchase (increases balance);
    txn_amount_aed < 0 = payment (reduces balance). Confirmed FI-2: Way4 CC convention.

    PIT join: prm_contract observation_date PIT join for open_date — same pattern as Pass D.
    Sources reused: crx_cc_transactions (Pass A) + prm_contract (Pass D); no new inputs.

    Features::

        ever_paid_flag           (int 0/1) — 1 if any payment in W_pre (txn_amount_aed < 0
                                             or txn_category == payment); 0 if W_pre txns
                                             exist but none are payments; NULL if no W_pre txns.
        limit_util_first_7d_flag (int 0/1) — 1 if cumulative spend in first 7 days after
                                             open_date > 80% of total W_pre spend;
                                             0 if open_date available but condition not met;
                                             NULL if open_date is NULL or no W_pre txns.
        max_7d_spend_ratio       (double)  — max rolling 7-day purchase sum / total W_pre
                                             purchase sum; NULL if no purchase transactions.
    """
    scope = spell_w.select("account_id").distinct()
    spell_base = spell_w.select("account_id", "spell_id", "t0", "w_pre_start")

    # Scope CC transactions to in-scope accounts (leftsemi before window filter)
    txn = crx_cc_transactions.select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("txn_amount_aed"),
        F.col("txn_category"),
    ).join(
        F.broadcast(scope),
        crx_cc_transactions["contract_id"] == scope["account_id"],
        "leftsemi",
    )

    # Join to spell_w and filter to W_pre: [w_pre_start, M0)
    txn_w = (
        txn.join(spell_w, on=(txn["contract_id"] == spell_w["account_id"]), how="inner")
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("txn_category"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
    )

    # Payment detection: negative amount (Way4 CC sign convention, FI-2) OR payment category
    is_payment = (F.col("txn_amount_aed") < 0) | (
        F.col("txn_category") == F.lit(_PAYMENT_CATEGORY)
    )

    # ever_paid_flag aggregation
    ever_paid_agg = txn_w.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_row_count"),
        F.max(F.when(is_payment, F.lit(1)).otherwise(F.lit(0))).alias("_any_payment"),
    )

    # Purchase transactions (positive amounts = spend on card)
    purchase_txns = txn_w.filter(
        F.col("txn_amount_aed").isNotNull() & (F.col("txn_amount_aed") > 0)
    ).withColumn(
        "_epoch_day",
        F.datediff(F.col("txn_date"), F.to_date(F.lit("1970-01-01"))).cast("long"),
    )

    # Total W_pre purchase spend per spell
    total_spend = purchase_txns.groupBy("account_id", "spell_id").agg(
        F.sum("txn_amount_aed").alias("_total_spend"),
    )

    # Max rolling 7-day spend: rangeBetween(-6, 0) on epoch-day ordered window
    w_7d = (
        Window.partitionBy("account_id", "spell_id")
        .orderBy("_epoch_day")
        .rangeBetween(-6, 0)
    )
    max_7d_spend = (
        purchase_txns.withColumn("_rolling_7d", F.sum("txn_amount_aed").over(w_7d))
        .groupBy("account_id", "spell_id")
        .agg(F.max("_rolling_7d").alias("_max_7d_spend"))
    )

    # PIT join prm_contract for account open_date (same pattern as Pass D)
    contract_scoped = prm_contract.select(
        F.col("contract_id").alias("_ctr_id"),
        F.col(_CONTRACT_OPEN_DATE_COL).alias("account_open_date"),
        F.col("observation_date").alias("_eff_start"),
    ).join(F.broadcast(scope), F.col("_ctr_id") == F.col("account_id"), "leftsemi")

    contract_open = (
        spell_base.join(
            contract_scoped,
            on=(spell_base["account_id"] == contract_scoped["_ctr_id"]),
            how="left",
        )
        .filter(F.col("_eff_start") <= F.col("t0"))
        .withColumn(
            "_rn_ctr",
            F.row_number().over(
                Window.partitionBy("account_id", "spell_id").orderBy(
                    F.col("_eff_start").desc()
                )
            ),
        )
        .filter(F.col("_rn_ctr") == 1)
        .select("account_id", "spell_id", "account_open_date")
    )

    # First-7-day spend: purchases on or within 6 days after open_date
    first7d_spend = (
        purchase_txns.join(contract_open, on=["account_id", "spell_id"], how="left")
        .filter(
            F.col("account_open_date").isNotNull()
            & (F.col("txn_date") >= F.col("account_open_date"))
            & (F.col("txn_date") <= F.date_add(F.col("account_open_date"), 6))
        )
        .groupBy("account_id", "spell_id")
        .agg(F.sum("txn_amount_aed").alias("_first_7d_spend"))
    )

    # Combine all aggregations and compute final features
    result = (
        spell_w.select("account_id", "spell_id")
        .join(ever_paid_agg, on=["account_id", "spell_id"], how="left")
        .join(total_spend, on=["account_id", "spell_id"], how="left")
        .join(max_7d_spend, on=["account_id", "spell_id"], how="left")
        .join(first7d_spend, on=["account_id", "spell_id"], how="left")
        .join(contract_open, on=["account_id", "spell_id"], how="left")
        .withColumn(
            "ever_paid_flag",
            F.when(F.col("_row_count").isNull(), F.lit(None).cast("int"))
            .when(F.col("_any_payment") == 1, F.lit(1))
            .otherwise(F.lit(0)),
        )
        .withColumn(
            "limit_util_first_7d_flag",
            F.when(
                F.col("account_open_date").isNull() | F.col("_total_spend").isNull(),
                F.lit(None).cast("int"),
            )
            .when(
                F.col("_first_7d_spend").isNull(),
                F.lit(0),  # no spend in first 7d → not bust-out
            )
            .when(
                (F.col("_total_spend") > 0)
                & (F.col("_first_7d_spend") / F.col("_total_spend") > 0.80),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .withColumn(
            "max_7d_spend_ratio",
            F.when(
                F.col("_total_spend").isNotNull() & (F.col("_total_spend") > 0),
                F.col("_max_7d_spend") / F.col("_total_spend"),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    return result.select(
        "account_id",
        "spell_id",
        "ever_paid_flag",
        "limit_util_first_7d_flag",
        "max_7d_spend_ratio",
    )


# ── Private: logging ──────────────────────────────────────────────────────────


def _log_departure_stats(result: DataFrame) -> None:
    """Log null-rate summary for the built departure signature table."""
    try:
        total = result.count()
        if total == 0:
            LOG.warning("CC departure signature: 0 rows produced — check spell filter")
            return
        cov_travel = result.filter(F.col("travel_mcc_flag_h2").isNotNull()).count()
        cov_casa = result.filter(F.col("casa_inflow_stop_gap_d").isNotNull()).count()
        cov_bureau = result.filter(F.col("aecb_leverage_slope").isNotNull()).count()
        cov_breadth = result.filter(F.col("relationship_breadth").isNotNull()).count()
        cov_alerts = result.filter(F.col("aecb_total_alerts_3m").isNotNull()).count()
        cov_cb_outflow = result.filter(
            F.col("cross_border_outflow_amt_h2").isNotNull()
        ).count()
        cov_retail_travel = result.filter(
            F.col("retail_travel_mcc_amt_h2").isNotNull()
        ).count()
        cov_payroll = result.filter(F.col("payroll_present_h2").isNotNull()).count()
        cov_ever_paid = result.filter(F.col("ever_paid_flag").isNotNull()).count()
        cov_foreign_login = result.filter(
            F.col("foreign_login_flag").isNotNull()
        ).count()
        LOG.info(
            "CC departure signature built: %d spells | "
            "travel_mcc_flag_h2: %.1f%% | "
            "casa_inflow_stop_gap_d: %.1f%% | "
            "aecb_leverage_slope: %.1f%% (T21 DROP — all NULL expected) | "
            "relationship_breadth: %.1f%% | "
            "aecb_total_alerts_3m: %.1f%% | "
            "cross_border_outflow_amt_h2: %.1f%% | "
            "retail_travel_mcc_amt_h2: %.1f%% | "
            "payroll_present_h2: %.1f%% | "
            "ever_paid_flag: %.1f%% | "
            "foreign_login_flag: %.1f%%",
            total,
            100.0 * cov_travel / total,
            100.0 * cov_casa / total,
            100.0 * cov_bureau / total,
            100.0 * cov_breadth / total,
            100.0 * cov_alerts / total,
            100.0 * cov_cb_outflow / total,
            100.0 * cov_retail_travel / total,
            100.0 * cov_payroll / total,
            100.0 * cov_ever_paid / total,
            100.0 * cov_foreign_login / total,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute departure signature stats: %s (lazy eval context)",
            str(exc),
        )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_departure_signature/pipeline.py`
action: delete · base sha256 `576355549a655429ab43b83149b4d2db921bcf9dd3f0e5168ea167a36087a258` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T06 — CC departure signature & history shape features.

Modular 15-node pipeline replacing the former single-node monolith.
Each pass is cached independently — fix Pass K, only re-run:
    kedro run --pipeline=crx_cc_departure_signature --from-nodes=build_crx_departure_pass_k

Input wiring note:
    Fourteen raw inputs cover three categories:
      1. CC tables: crx_cc_transactions (T04c intermediate — replaces prm_transaction;
         departure + fee txns), prm_turnovers (lifetime fee totals),
         prm_contract (tenure + cif bridge),
         prm_client (CIF bridge — maps Way4 client_idt to bank CIF number)
      2. CRX persona tables: crx_cc_spell_table (spell anchor + history),
         crx_cc_payment_trajectory (w_pre truncation columns from T04b)
      3. Cross-domain tables: int_bureau_pull_monthly (AECB leverage slope — T21 DROP confirmed),
         feat_product_holding (relationship breadth),
         comp_financial_tran_repos_dly (CASA inflow signals — R20 scoped),
         fea_monthly_aecb_alerts (AECB alert signals — REUSE from retail.feature_space;
           R2 PASS + R7 PASS confirmed 2026-08-21),
         feat_fx_leakage (cross-border FX leakage — fea_monthly_agg_fx_leakage),
         feat_cc_txns_rfs (CC travel+tours MCC — retail.feature_space),
         feat_payroll_indicator (payroll presence — retail.feature_space primary),
         prm_digital_login_monthly (OMB login monthly grain — digital_login pipeline)

    comp_financial_tran_repos_dly is the raw 2.4B-row CASA table (R20). Pass B
    scopes it via CIF-level leftsemi join before any date filtering. Pass B has
    an inline schema guard and emits NULL features if required columns are absent.

Node graph summary:
    Node 1  build_crx_departure_spell_base     → crx_cc_departure_spell_base
    Node 2  build_crx_departure_contract_cif   → crx_cc_departure_contract_cif
    Node 3  build_crx_departure_pass_a         → crx_cc_departure_pass_a
    Node 4  build_crx_departure_pass_b         → crx_cc_departure_pass_b
    Node 5  build_crx_departure_pass_c         → crx_cc_departure_pass_c
    Node 6  build_crx_departure_pass_d         → crx_cc_departure_pass_d
    Node 7  build_crx_departure_pass_e         → crx_cc_departure_pass_e
    Node 8  build_crx_departure_pass_f         → crx_cc_departure_pass_f
    Node 9  build_crx_departure_pass_g         → crx_cc_departure_pass_g
    Node 10 build_crx_departure_pass_h         → crx_cc_departure_pass_h
    Node 11 build_crx_departure_pass_h2        → crx_cc_departure_pass_h2
    Node 12 build_crx_departure_pass_i         → crx_cc_departure_pass_i
    Node 13 build_crx_departure_pass_j         → crx_cc_departure_pass_j
    Node 14 build_crx_departure_pass_k         → crx_cc_departure_pass_k
    Node 15 build_crx_departure_final          → crx_cc_departure_signature

Run with:
    kedro run --pipeline=crx_cc_departure_signature
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_departure_contract_cif,
    build_departure_final,
    build_departure_pass_a,
    build_departure_pass_b,
    build_departure_pass_c,
    build_departure_pass_d,
    build_departure_pass_e,
    build_departure_pass_f,
    build_departure_pass_g,
    build_departure_pass_h,
    build_departure_pass_h2,
    build_departure_pass_i,
    build_departure_pass_j,
    build_departure_pass_k,
    build_departure_spell_base,
)

_TAGS = ["crx", "departure_signature", "t06"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """15-node pipeline: build CC departure signature & history shape features."""
    return Pipeline(
        [
            # ── Node 1: spell base ─────────────────────────────────────────────
            node(
                func=build_departure_spell_base,
                inputs=[
                    "crx_cc_spell_table",
                    "crx_cc_payment_trajectory",
                    "cc_spine",  # adds spine_obs_date + block_date
                ],
                outputs="crx_cc_departure_spell_base",
                name="build_crx_departure_spell_base",
                tags=_TAGS,
            ),
            # ── Node 2: contract → CIF bridge ─────────────────────────────────
            node(
                func=build_departure_contract_cif,
                inputs=[
                    "prm_contract",
                    "prm_client",
                ],
                outputs="crx_cc_departure_contract_cif",
                name="build_crx_departure_contract_cif",
                tags=_TAGS,
            ),
            # ── Node 3: Pass A — CC departure + fee signals ─────────────────
            node(
                func=build_departure_pass_a,
                inputs=[
                    "crx_cc_transactions",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_a",
                name="build_crx_departure_pass_a",
                tags=_TAGS,
            ),
            # ── Node 4: Pass B — CASA inflow stop (2.4B row, R20) ───────────
            node(
                func=build_departure_pass_b,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_b",
                name="build_crx_departure_pass_b",
                tags=_TAGS,
            ),
            # ── Node 5: Pass C — history shape self-window ──────────────────
            node(
                func=build_departure_pass_c,
                inputs=[
                    "crx_cc_spell_table",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_c",
                name="build_crx_departure_pass_c",
                tags=_TAGS,
            ),
            # ── Node 6: Pass D — tenure + lifetime fees ─────────────────────
            node(
                func=build_departure_pass_d,
                inputs=[
                    "prm_contract",
                    "prm_turnovers",
                    "crx_cc_departure_spell_base",
                    "crx_cc_departure_pass_a",
                ],
                outputs="crx_cc_departure_pass_d",
                name="build_crx_departure_pass_d",
                tags=_TAGS,
            ),
            # ── Node 7: Pass E — AECB leverage slope (T21 DROP) ─────────────
            node(
                func=build_departure_pass_e,
                inputs=[
                    "int_bureau_pull_monthly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_e",
                name="build_crx_departure_pass_e",
                tags=_TAGS,
            ),
            # ── Node 8: Pass F — relationship breadth ───────────────────────
            node(
                func=build_departure_pass_f,
                inputs=[
                    "feat_product_holding",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_f",
                name="build_crx_departure_pass_f",
                tags=_TAGS,
            ),
            # ── Node 9: Pass G — AECB alert signals ─────────────────────────
            node(
                func=build_departure_pass_g,
                inputs=[
                    "fea_monthly_aecb_alerts",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_g",
                name="build_crx_departure_pass_g",
                tags=_TAGS,
            ),
            # ── Node 10: Pass H — cross-border CASA outflow ─────────────────
            node(
                func=build_departure_pass_h,
                inputs=[
                    "feat_fx_leakage",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_h",
                name="build_crx_departure_pass_h",
                tags=_TAGS,
            ),
            # ── Node 11: Pass H2 — retail.feature_space CC travel MCC ───────
            node(
                func=build_departure_pass_h2,
                inputs=[
                    "feat_cc_txns_rfs",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_h2",
                name="build_crx_departure_pass_h2",
                tags=_TAGS,
            ),
            # ── Node 12: Pass I — payroll indicator ─────────────────────────
            node(
                func=build_departure_pass_i,
                inputs=[
                    "feat_payroll_indicator",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_i",
                name="build_crx_departure_pass_i",
                tags=_TAGS,
            ),
            # ── Node 13: Pass J — foreign login detection ───────────────────
            node(
                func=build_departure_pass_j,
                inputs=[
                    "prm_digital_login_monthly",
                    "crx_cc_departure_contract_cif",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_j",
                name="build_crx_departure_pass_j",
                tags=_TAGS,
            ),
            # ── Node 14: Pass K — bust-out utilisation signals ──────────────
            node(
                func=build_departure_pass_k,
                inputs=[
                    "crx_cc_transactions",
                    "prm_contract",
                    "crx_cc_departure_spell_base",
                ],
                outputs="crx_cc_departure_pass_k",
                name="build_crx_departure_pass_k",
                tags=_TAGS,
            ),
            # ── Node 15: final assembly ─────────────────────────────────────
            node(
                func=build_departure_final,
                inputs=[
                    "crx_cc_departure_spell_base",
                    "crx_cc_departure_pass_a",
                    "crx_cc_departure_pass_b",
                    "crx_cc_departure_pass_c",
                    "crx_cc_departure_pass_d",
                    "crx_cc_departure_pass_e",
                    "crx_cc_departure_pass_f",
                    "crx_cc_departure_pass_g",
                    "crx_cc_departure_pass_h",
                    "crx_cc_departure_pass_h2",
                    "crx_cc_departure_pass_i",
                    "crx_cc_departure_pass_j",
                    "crx_cc_departure_pass_k",
                ],
                outputs="crx_cc_departure_signature",
                name="build_crx_departure_final",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_payment_trajectory/nodes.py`
action: delete · base sha256 `f6dc1d5d6808949d6875d5647f6f98ac3892b1a01a52e39c018a56f1d4f3d297` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T04b — CC Payment & Balance Trajectory Features (re-anchored).

# pylint: disable=too-many-locals, too-many-statements
# Rationale: two-pass feature builder (Pass A: transaction DOM/gap features;
# Pass B: monthly pay-ratio features). Each pass is self-contained; splitting
# further would obscure the T0-anchored window logic.

Build function: build_cc_payment_trajectory(crx_cc_transactions, crx_cc_balance,
                                            crx_cc_spell_table, prm_contract)

Business context:
    At 61+ DPD, credit cards receive Block X (permanent cancellation). All
    transaction activity stops — no utilization, no payment signals from that
    point. Features must be derived entirely from pre-delinquency history.
    This pipeline extracts that history anchored to T0 (spell onset), not to
    the model's observation_date. For cc_180_plus accounts T0 may be 18-24+
    months before observation_date; anchoring to observation_date would produce
    zero months of usable history.

    Output grain: one row per (account_id, spell_id). An account that cured and
    re-defaulted gets a separate spell — and separate features — for each episode.

Feature interpretation:
    Pass A (DOM/gap features) → payment discipline axis:
        A habitual payer with low pay_dom_std / high pay_dom_window_share who hit
        a sudden shock looks different from a chronically erratic payer. A large
        pay_dom_drift means payments were drifting later each month before onset.
        pay_gap_last_d measures the elapsed silence before T0.

    Pass B (ratio features) → payment capacity axis:
        pay_ratio_m = P_m / D_m per month (capped at 2.0). The contrast
        pay_ratio_mean_h2 vs pay_ratio_mean_h1 — whether recent repayment
        deteriorated relative to baseline — is a strong default predictor.
        pay_ratio_slope captures the direction of the trend over W_pre.

Window design (T04b — month-based, per 2026-08-19 decision)::

    M0          = trunc(t0, 'month')            — onset month (excluded from all windows)
    W_pre       = [w_pre_start, M0)             — clean pre-delinquency window (≤12 months)
    w_pre_start = max(M0−12m, prior_spell_cut, account_open_month, retention_floor)
    H2          = [M0−3m, M0)       → month_idx 1..3  — recent behaviour
    H1          = [w_pre_start, M0−3m) → month_idx ≥4  — baseline behaviour

T0 leakage guard: all transaction joins use strict ``txn_date < M0``
(M0 = trunc(t0, 'month')). The onset month is excluded; month_idx = 0
never appears.

Censored spells (t0_censored_flag=1) are excluded from feature computation;
they receive NULL for all features via left-join null-propagation.

Truncation columns (new in T04b):
    w_pre_start             : date — effective W_pre start (month-start date)
    w_pre_clean_m           : int — months in [w_pre_start, M0)
    w_pre_contaminated_flag : int — 1 if w_pre_start > M0−12m
    w_pre_truncation_reason : string — none | prior_spell | tenure | retention

FILL-IN blockers (T01 flagged, surfaced here per R17):
    min_pay_share_w12        : blocked by <<FILL-IN: prm_billing column for min_due_amount>>
    months_since_full_pay_t0 : blocked by <<FILL-IN: full-pay condition or source table>>

Day arithmetic note:
    pay_dom_* and pay_gap_*_d use actual day-of-month / datediff values.
    Month boundary changes affect WHICH transactions are included, but the
    gap/DOM calculations themselves remain day-based.

OLS slope implementation note:
    ``compute_ols_slope()`` from utils/ols.py is designed for pre-bucketed
    wide monthly data (dict of month_index → Column expression). For
    transaction-level OLS (pay_dom_drift) and monthly aggregate OLS
    (pay_ratio_slope), inline aggregation statistics are used instead —
    same mathematical formula, no pivot step required. This avoids a
    separate pivot shuffle for 12 columns on a large transactions table.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)

# Minimum number of non-null H1 months required before pay_ratio_mean_h1 is
# considered reliable.  H1 spans [w_pre_start, M0-3) — nominally 9 months.
# Fewer than 3 months of pre-delinquency payment history is not a credible
# baseline; the mean would rest on noise (one unusual month can shift it ±1.0).
_MIN_H1_MONTHS = 3


def build_cc_payment_trajectory(
    crx_cc_transactions: DataFrame,
    crx_cc_balance: DataFrame,
    crx_cc_spell_table: DataFrame,
    prm_contract: DataFrame,
) -> DataFrame:
    """Build CC payment & balance trajectory features anchored to T0 per spell.

    Args:
        crx_cc_transactions:  T04c intermediate — T0-scoped CC transaction history.
            direction=1 rows are credit/inflow (payments). Replaces raw_transaction.
            Required cols: contract_id, observation_date, direction, txn_amount_aed.
        crx_cc_balance:       T04c intermediate — T0-scoped total_due billing history.
            Replaces raw_stg_balance + raw_stg_account_group.
            Required cols: contract_id, observation_date, total_due.
        crx_cc_spell_table: T03b output at (account_id, spell_id) grain.
            Already scoped to the active cc_spine population.
        prm_contract:         Way4 monthly contract snapshots. Used to derive
            account_open_month via open_date per account.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id, spell_id, t0,
            w_pre_start, w_pre_clean_m, w_pre_contaminated_flag, w_pre_truncation_reason,
            pay_dom_std, pay_dom_window_share, pay_dom_drift,
            pay_gap_max_d, pay_gap_last_d,
            pay_ratio_mean_h1, pay_ratio_mean_h2, pay_ratio_slope,
            min_pay_share_w12       (NULL — FILL-IN blocker),
            months_since_full_pay_t0 (NULL — FILL-IN blocker),
            computed_at
    """
    # ── Step 0: spell base — exclude censored spells, carry prior_spell_end ──
    # t0_censored_flag=1 covers two subtypes (see cc_spell/nodes.py):
    #   data_depth        — T0 outside the billing window; may become scorable later.
    #   restructured_entry — new account ID opened mid-delinquency; T0-anchored features
    #                        cannot be computed from this account alone; needs T18/T19.
    # Both are correctly excluded here.  The distinction matters for T03c / coverage
    # reporting but not for feature computation — neither subtype can have a valid W_pre.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id", "spell_id", "t0", "prior_spell_end"
    )

    # ── Step -1: T0-scoped intermediates (pre-built by crx_cc_raw_extract T04c) ─
    # crx_cc_transactions and crx_cc_balance are already scoped to the T0 window;
    # no further raw extraction required here.
    txn = crx_cc_transactions
    balance = crx_cc_balance

    # ── Compute per-spell W_pre truncation boundaries ──────────────────────────
    w_pre = _compute_w_pre_truncation(txn, prm_contract, spell)
    spell_with_w = spell.join(w_pre, on=["account_id", "spell_id"], how="left")

    # ── Pass A: transaction-level features (DOM consistency, payment gaps) ──
    pass_a = _build_pass_a(txn, spell_with_w)

    # ── Pass B: monthly billing features (payment ratio vs total due) ─────────
    pass_b = _build_pass_b(txn, balance, spell_with_w)

    # ── Combine onto spell base ─────────────────────────────────────────────────
    # Left join: spells with zero payments in W_pre receive NULL for all features.
    result = spell_with_w.join(pass_a, on=["account_id", "spell_id"], how="left").join(
        pass_b, on=["account_id", "spell_id"], how="left"
    )

    # ── FILL-IN blocked features (NULL until column sources are confirmed) ────
    result = (
        result
        # <<FILL-IN: prm_billing column for min_due_amount>>
        # Once resolved: share of W_pre months where P_m ∈ [0.9×min_due, 1.1×min_due]
        .withColumn("min_pay_share_w12", F.lit(None).cast("double"))
        # <<FILL-IN: full-pay condition or source table>>
        # Once resolved: months since last month where P_m >= total_due (full statement pay)
        .withColumn("months_since_full_pay_t0", F.lit(None).cast("double")).withColumn(
            "computed_at", F.current_timestamp()
        )
    )

    _log_trajectory_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("pay_dom_std").cast("double"),
        F.col("pay_dom_window_share").cast("double"),
        F.col("pay_dom_drift").cast("double"),
        F.col("pay_gap_max_d").cast("int"),
        F.col("pay_gap_last_d").cast("int"),
        F.col("pay_ratio_mean_h1").cast("double"),
        F.col("pay_ratio_mean_h2").cast("double"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("min_pay_share_w12").cast("double"),
        F.col("months_since_full_pay_t0").cast("double"),
        F.col("computed_at"),
    )


# ── Private: W_pre truncation ──────────────────────────────────────────────────


def _compute_w_pre_truncation(
    prm_transaction: DataFrame,
    prm_contract: DataFrame,
    spell: DataFrame,
) -> DataFrame:
    """Compute per-spell W_pre window boundaries and truncation diagnostics.

    Three cut points (all scoped via inner-join to spell population — no
    unscoped scan of large tables):

    1. Retention floor: earliest transaction month in the raw data — hard limit
       of available history; no fabricating coverage that doesn't exist.
    2. Account open month: open_date from prm_contract — window cannot precede
       account existence.
    3. Prior spell cut: month after prior_spell_end — the previous delinquency
       episode is "dirty"; crossing into it would contaminate features with
       in-spell behavior from a different episode.

    w_pre_start = max(M0−12m, prior_spell_cut, account_open_month, retention_floor)
    where M0 = trunc(t0, 'month').

    Args:
        prm_transaction: used for retention floor (earliest txn month per account).
        prm_contract:    used for account open month (min obs_date per account).
        spell:           (account_id, spell_id, t0, prior_spell_end) — non-censored.

    Returns:
        DataFrame at (account_id, spell_id) grain with:
            w_pre_start             : date — effective W_pre start (month-start date)
            w_pre_clean_m           : int — months in [w_pre_start, M0)
            w_pre_contaminated_flag : int — 1 if w_pre_start > M0−12m
            w_pre_truncation_reason : string — none | prior_spell | tenure | retention
    """
    scope = spell.select("account_id").distinct()

    # ── Cut point 1: retention floor — earliest transaction month per account ──
    acct_retention = (
        prm_transaction.select(
            F.col("contract_id").alias("account_id"),
            F.col("observation_date").alias("txn_date"),
        )
        .join(scope, on="account_id", how="inner")
        .groupBy("account_id")
        .agg(F.trunc(F.min("txn_date"), "month").alias("retention_floor_month"))
    )

    # ── Cut point 2: account open month — open_date from prm_contract ────────────
    acct_open = (
        prm_contract.select(
            F.col("contract_id").alias("account_id"),
            F.col("open_date").alias("obs_date"),
        )
        .join(scope, on="account_id", how="inner")
        .groupBy("account_id")
        .agg(F.trunc(F.min("obs_date"), "month").alias("account_open_month"))
    )

    # ── Join per-account cut points onto the spell table ─────────────────────────
    spell_w = spell.join(acct_retention, on="account_id", how="left").join(
        acct_open, on="account_id", how="left"
    )

    # ── Per-spell truncation expressions ─────────────────────────────────────────
    m0 = F.trunc(F.col("t0"), "month")
    nominal = F.add_months(m0, -12)  # 12-month lookback — binding when no cut is later

    # Prior spell cut: month after cure month (cure month is partly delinquent)
    prior_cut = F.when(
        F.col("prior_spell_end").isNotNull(),
        F.add_months(F.trunc(F.col("prior_spell_end"), "month"), 1),
    )

    w_pre_start_expr = F.greatest(
        nominal,
        F.coalesce(prior_cut, nominal),
        F.coalesce(F.col("account_open_month"), nominal),
        F.coalesce(F.col("retention_floor_month"), nominal),
    )

    spell_w = (
        spell_w.withColumn("_m0", m0)
        .withColumn("_nominal", nominal)
        .withColumn("_prior_cut", prior_cut)
        .withColumn("w_pre_start", w_pre_start_expr)
        .withColumn(
            "w_pre_clean_m",
            F.floor(F.months_between(F.col("_m0"), F.col("w_pre_start"))).cast("int"),
        )
        .withColumn(
            "w_pre_contaminated_flag",
            F.when(F.col("w_pre_start") > F.col("_nominal"), 1).otherwise(0),
        )
        .withColumn(
            "w_pre_truncation_reason",
            # Priority: prior_spell > tenure > retention > none
            F.when(F.col("w_pre_contaminated_flag") == 0, "none")
            .when(
                F.col("_prior_cut").isNotNull()
                & (F.col("w_pre_start") == F.col("_prior_cut")),
                "prior_spell",
            )
            .when(
                F.col("account_open_month").isNotNull()
                & (F.col("w_pre_start") == F.col("account_open_month")),
                "tenure",
            )
            .when(
                F.col("retention_floor_month").isNotNull()
                & (F.col("w_pre_start") == F.col("retention_floor_month")),
                "retention",
            )
            .otherwise("none"),
        )
    )

    # Clamp negative w_pre_clean_m (retention_floor > T0).
    # Must override reason BEFORE clamping so the negative signal is not lost.
    spell_w = spell_w.withColumn(
        "w_pre_truncation_reason",
        F.when(F.col("w_pre_clean_m") < 0, F.lit("negative_window")).otherwise(
            F.col("w_pre_truncation_reason")
        ),
    ).withColumn(
        "w_pre_clean_m",
        F.greatest(F.col("w_pre_clean_m"), F.lit(0)),
    )

    return spell_w.select(
        "account_id",
        "spell_id",
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
    )


# ── Private: Pass A ────────────────────────────────────────────────────────────


def _build_pass_a(prm_transaction: DataFrame, spell: DataFrame) -> DataFrame:
    """Transaction-level payment features: DOM consistency and payment gaps.

    spell carries w_pre_start (date) and w_pre_clean_m (int) from
    _compute_w_pre_truncation, already joined onto spell_with_w.

    Returns one row per (account_id, spell_id) that has ≥1 payment in W_pre.
    Spells with no payments are absent; they become NULLs via left join.

    Window: [w_pre_start, M0) where M0 = trunc(t0, 'month').
    month_idx: M0−1 → 1, M0−2 → 2, …, M0−12 → 12.  M0 (idx=0) is excluded.

    Features computed::

        pay_dom_std         : stddev of dayofmonth across W_pre payments (NULL if <3).
                              Low = disciplined habitual payer; high = erratic timing.
        pay_dom_window_share: share of w_pre_clean_m months with ≥1 payment within
                              ±2 DOM of modal DOM (NULL if <3 payments).
                              Measures payment habit consistency.
        pay_dom_drift       : OLS slope of dayofmonth vs month_idx over W_pre
                              (NULL if <3 payments). Positive slope = payments were
                              drifting to later dates each month approaching onset.
        pay_gap_max_d       : max gap (days) between consecutive payments in W_pre
                              (NULL if <2 payments). Captures whether the customer
                              ever went a very long time without paying.
        pay_gap_last_d      : datediff(t0, most_recent_payment) (NULL if 0 payments).
                              Uses actual t0, not M0. A short gap suggests a sudden
                              shock; a long gap suggests slow drift into delinquency.
    """
    # Filter to payment transactions
    # direction == 1 = credit (inflow / payment reduces outstanding balance)
    # <<FILL-IN: any additional payment exclusion conditions>>
    txn_pay = prm_transaction.filter(F.col("direction") == 1).select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
    )

    # Join to spell table: one txn can match multiple spells when W_pre windows
    # of consecutive spells overlap the same calendar period. This is correct —
    # payment history before T0 is a valid feature for any spell anchored after it.
    payments = (
        txn_pay.join(
            spell,
            on=txn_pay["contract_id"] == spell["account_id"],
            how="inner",
        ).select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        # W_pre window: [w_pre_start, M0). M0 = trunc(t0,'month') is excluded.
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
    )

    payments = payments.withColumn("dom", F.dayofmonth("txn_date"))

    # month_idx: whole months before M0 (both endpoints truncated to month-start
    # to avoid partial-month bias when t0 falls mid-month).
    # M0-1 → 1,  M0-2 → 2, ...,  M0-12 → 12
    payments = payments.withColumn(
        "month_idx",
        F.floor(
            F.months_between(
                F.trunc(F.col("t0"), "month"), F.trunc(F.col("txn_date"), "month")
            )
        ).cast("int"),
    )

    # Lagged payment date for consecutive-gap computation within each spell
    w_pay = Window.partitionBy("account_id", "spell_id").orderBy("txn_date")
    payments = payments.withColumn("_prev_txn", F.lag("txn_date").over(w_pay))
    payments = payments.withColumn(
        "_gap_days",
        F.when(
            F.col("_prev_txn").isNotNull(),
            F.datediff(F.col("txn_date"), F.col("_prev_txn")),
        ),
    )

    # ── Step 1: spell-level aggregation ────────────────────────────────────────
    spell_agg = payments.groupBy("account_id", "spell_id").agg(
        F.count("*").alias("_n_pay"),
        F.first("t0").alias("t0"),
        F.first("w_pre_clean_m").alias(
            "_w_pre_clean_m"
        ),  # denominator for window_share
        # DOM stats
        F.stddev_samp("dom").alias("_dom_std_raw"),
        F.percentile_approx("dom", 0.5).alias("_modal_dom"),
        # Payment gap
        F.max("_gap_days").alias("_gap_max_raw"),
        F.max("txn_date").alias("_last_txn"),
        # OLS accumulators for pay_dom_drift (transaction-level inline OLS)
        F.sum(F.col("month_idx").cast("double")).alias("_dom_sx"),
        F.sum(F.col("dom").cast("double")).alias("_dom_sy"),
        F.sum(F.col("month_idx").cast("double") * F.col("dom").cast("double")).alias(
            "_dom_sxy"
        ),
        F.sum(
            F.col("month_idx").cast("double") * F.col("month_idx").cast("double")
        ).alias("_dom_sx2"),
    )

    # ── Step 2: pay_dom_window_share (requires modal DOM from Step 1) ──────────
    # Count calendar months in W_pre where ≥1 payment falls within ±2 days of
    # modal DOM.
    near_modal = (
        payments.join(
            spell_agg.select("account_id", "spell_id", "_modal_dom"),
            on=["account_id", "spell_id"],
        )
        .filter(F.abs(F.col("dom") - F.col("_modal_dom")) <= 2)
        .withColumn("_cal_month", F.trunc(F.col("txn_date"), "MM"))
        .groupBy("account_id", "spell_id")
        .agg(F.countDistinct("_cal_month").alias("_near_modal_months"))
    )

    spell_agg = spell_agg.join(near_modal, on=["account_id", "spell_id"], how="left")

    # ── Step 3: apply null guards and derive final feature columns ─────────────

    # pay_dom_std: NULL if < 3 payments
    spell_agg = spell_agg.withColumn(
        "pay_dom_std",
        F.when(F.col("_n_pay") >= 3, F.col("_dom_std_raw")).otherwise(
            F.lit(None).cast("double")
        ),
    )

    # pay_dom_window_share: NULL if < 3 payments; denominator = w_pre_clean_m
    # (actual clean months available per spell, not a fixed 12)
    spell_agg = spell_agg.withColumn(
        "pay_dom_window_share",
        F.when(
            (F.col("_n_pay") >= 3) & (F.col("_w_pre_clean_m") > 0),
            F.coalesce(F.col("_near_modal_months"), F.lit(0)).cast("double")
            / F.col("_w_pre_clean_m").cast("double"),
        ).otherwise(F.lit(None).cast("double")),
    )

    # pay_dom_drift: OLS slope of dayofmonth vs month_idx; NULL if < 3 payments
    _dom_denom = F.col("_n_pay").cast("double") * F.col("_dom_sx2") - F.col(
        "_dom_sx"
    ) * F.col("_dom_sx")
    spell_agg = spell_agg.withColumn(
        "pay_dom_drift",
        F.when(
            (F.col("_n_pay") >= 3) & (_dom_denom != 0.0),
            (
                F.col("_n_pay").cast("double") * F.col("_dom_sxy")
                - F.col("_dom_sx") * F.col("_dom_sy")
            )
            / _dom_denom,
        ).otherwise(F.lit(None).cast("double")),
    )

    # pay_gap_max_d: NULL if < 2 payments (no consecutive pair exists)
    spell_agg = spell_agg.withColumn(
        "pay_gap_max_d",
        F.when(F.col("_n_pay") >= 2, F.col("_gap_max_raw")).otherwise(
            F.lit(None).cast("int")
        ),
    )

    # pay_gap_last_d: days from most-recent W_pre payment to T0; NULL if no payments.
    # Uses actual t0 (not M0) — measures elapsed days to delinquency onset.
    # Always >= 0: guaranteed by txn_date < M0 ≤ t0 (onset month not yet started).
    spell_agg = spell_agg.withColumn(
        "pay_gap_last_d",
        F.when(
            F.col("_n_pay") > 0,
            F.datediff(F.col("t0"), F.col("_last_txn")),
        ).otherwise(F.lit(None).cast("int")),
    )

    return spell_agg.select(
        "account_id",
        "spell_id",
        "pay_dom_std",
        "pay_dom_window_share",
        "pay_dom_drift",
        "pay_gap_max_d",
        "pay_gap_last_d",
    )


# ── Private: Pass B ────────────────────────────────────────────────────────────


def _build_pass_b(
    prm_transaction: DataFrame,
    prm_billing: DataFrame,
    spell: DataFrame,
) -> DataFrame:
    """Monthly billing features: payment ratio relative to total due (D_m).

    spell carries w_pre_start (date) from _compute_w_pre_truncation, already
    joined onto spell_with_w.

    Window: [w_pre_start, M0). month_idx: M0−1 → 1, ..., M0−12 → 12.
    H2 = month_idx 1..3  (recent 3 months).
    H1 = month_idx ≥ 4   (older months beyond 3).

    pay_ratio_m = P_m / D_m per billing month (capped at 2.0 to limit outlier
    distortion). 1.0 = paid exactly what was due; < 1.0 = partial payment;
    0.0 = no payment. Undefined (NULL) when D_m = 0 or NULL.

    Features::

        pay_ratio_mean_h1 : mean(P_m / D_m) over H1 months (month_idx ≥ 4).
                            Baseline repayment behaviour in the older lookback.
                            NULL if fewer than _MIN_H1_MONTHS (3) non-null H1
                            months exist — one or two months is not a credible
                            baseline; a single outlier month would dominate.
        pay_ratio_mean_h2 : mean(P_m / D_m) over H2 months (month_idx 1..3).
                            Recent repayment in the 3 months just before onset.
                            The contrast h2 vs h1 — whether behaviour deteriorated
                            in the final quarter — is a strong default predictor.
        pay_ratio_slope   : OLS slope of pay_ratio_m vs month_idx over W_pre
                            (NULL if < 4 non-null months). Negative slope =
                            ratio was declining toward onset (worsening capacity).
        min_pay_share_w12 : NULL — <<FILL-IN: min_due_amount source>>
        months_since_full_pay_t0 : NULL — <<FILL-IN: full-pay condition or source>>
    """
    # ── Monthly payment totals P_m ─────────────────────────────────────────────
    txn_pay = prm_transaction.filter(F.col("direction") == 1).select(
        F.col("contract_id"),
        F.col("observation_date").alias("txn_date"),
        F.col("txn_amount_aed"),
    )

    monthly_p = (
        txn_pay.join(
            spell,
            on=txn_pay["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))  # T0 leakage guard
        )
        .withColumn(
            "month_idx",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"), F.trunc(F.col("txn_date"), "month")
                )
            ).cast("int"),
        )
        .groupBy("account_id", "spell_id", "month_idx")
        .agg(F.sum("txn_amount_aed").alias("p_m"))
    )

    # ── Monthly billing D_m from prm_balance (wired as prm_billing) ────────────
    # <<FILL-IN: prm_billing column for total_due_amount (D_m)>>
    # Using CreditCardBalance.total_due (100% coverage) pending confirmation.
    billing = prm_billing.select(
        F.col("contract_id"),
        F.col("observation_date").alias("billing_date"),
        F.col("total_due").alias("d_m"),
    )

    monthly_d = (
        billing.join(
            spell,
            on=billing["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("billing_date"),
            F.col("d_m"),
            F.col("w_pre_start"),
        )
        .filter(
            (F.col("billing_date") >= F.col("w_pre_start"))
            & (F.col("billing_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "month_idx",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("billing_date"), "month"),
                )
            ).cast("int"),
        )
        # One billing record per (account, spell, month) — take first if duplicates
        .groupBy("account_id", "spell_id", "month_idx")
        .agg(F.first("d_m").alias("d_m"))
    )

    # ── Join P_m and D_m; compute monthly pay_ratio ────────────────────────────
    # Left join from monthly_d: billing record defines the eligible months.
    # Months where billing exists but no payment was made → P_m defaults to 0.
    # Months where D_m = 0 or NULL → pay_ratio_m = NULL (undefined).
    monthly = (
        monthly_d.join(
            monthly_p, on=["account_id", "spell_id", "month_idx"], how="left"
        )
        .withColumn("p_m", F.coalesce(F.col("p_m"), F.lit(0.0)))
        .withColumn(
            "pay_ratio_m",
            F.when(
                F.col("d_m").isNotNull() & (F.col("d_m") > 0),
                F.least(F.col("p_m") / F.col("d_m"), F.lit(2.0)),
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    # ── Aggregate per spell ─────────────────────────────────────────────────────
    result = monthly.groupBy("account_id", "spell_id").agg(
        # H1 = older half: month_idx >= 4 (months M0-4 through end of W_pre)
        F.avg(
            F.when(
                (F.col("month_idx") >= 4) & F.col("pay_ratio_m").isNotNull(),
                F.col("pay_ratio_m"),
            )
        ).alias("pay_ratio_mean_h1"),
        # Count of non-null H1 months — used to enforce _MIN_H1_MONTHS floor below
        F.count(
            F.when(
                (F.col("month_idx") >= 4) & F.col("pay_ratio_m").isNotNull(),
                F.lit(1),
            )
        ).alias("_h1_n"),
        # H2 = recent half: month_idx 1..3 (months M0-1, M0-2, M0-3)
        F.avg(
            F.when(
                (F.col("month_idx") >= 1)
                & (F.col("month_idx") <= 3)
                & F.col("pay_ratio_m").isNotNull(),
                F.col("pay_ratio_m"),
            )
        ).alias("pay_ratio_mean_h2"),
        # OLS accumulators for pay_ratio_slope (inline OLS; no pivot required)
        F.count(F.when(F.col("pay_ratio_m").isNotNull(), F.lit(1))).alias("_pr_n"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sx"),
        F.sum(
            F.when(F.col("pay_ratio_m").isNotNull(), F.col("pay_ratio_m")).otherwise(
                F.lit(0.0)
            )
        ).alias("_pr_sy"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double") * F.col("pay_ratio_m"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sxy"),
        F.sum(
            F.when(
                F.col("pay_ratio_m").isNotNull(),
                F.col("month_idx").cast("double") * F.col("month_idx").cast("double"),
            ).otherwise(F.lit(0.0))
        ).alias("_pr_sx2"),
    )

    # OLS slope for pay_ratio_slope: NULL if < 4 non-null months
    _pr_denom = F.col("_pr_n").cast("double") * F.col("_pr_sx2") - F.col(
        "_pr_sx"
    ) * F.col("_pr_sx")
    result = result.withColumn(
        "pay_ratio_slope",
        F.when(
            (F.col("_pr_n") >= 4) & (_pr_denom != 0.0),
            (
                F.col("_pr_n").cast("double") * F.col("_pr_sxy")
                - F.col("_pr_sx") * F.col("_pr_sy")
            )
            / _pr_denom,
        ).otherwise(F.lit(None).cast("double")),
    )

    # Enforce minimum H1 month floor: pay_ratio_mean_h1 requires at least
    # _MIN_H1_MONTHS non-null H1 months to be considered a reliable baseline.
    # Fewer months → NULL; downstream c_shock_2 condition then fails cleanly.
    result = result.withColumn(
        "pay_ratio_mean_h1",
        F.when(F.col("_h1_n") >= _MIN_H1_MONTHS, F.col("pay_ratio_mean_h1")).otherwise(
            F.lit(None).cast("double")
        ),
    )

    # FILL-IN blocked features — return NULL until column sources confirmed
    result = result.withColumn(
        "min_pay_share_w12",
        F.lit(None).cast(
            "double"
        ),  # <<FILL-IN: prm_billing column for min_due_amount>>
    ).withColumn(
        "months_since_full_pay_t0",
        F.lit(None).cast("double"),  # <<FILL-IN: full-pay condition or source table>>
    )

    return result.select(
        "account_id",
        "spell_id",
        "pay_ratio_mean_h1",
        "pay_ratio_mean_h2",
        "pay_ratio_slope",
        "min_pay_share_w12",
        "months_since_full_pay_t0",
    )


# ── Private: logging ───────────────────────────────────────────────────────────


def _log_trajectory_stats(result: DataFrame) -> None:
    """Log coverage summary for the built trajectory table."""
    try:
        total = result.count()
        cov_gap = result.filter(F.col("pay_gap_last_d").isNotNull()).count()
        cov_dom = result.filter(F.col("pay_dom_std").isNotNull()).count()
        cov_ratio = result.filter(F.col("pay_ratio_mean_h2").isNotNull()).count()
        LOG.info(
            "CC payment trajectory built: %d spells | "
            "pay_gap_last_d: %.1f%% | pay_dom_std: %.1f%% | pay_ratio_mean_h2: %.1f%%",
            total,
            100.0 * cov_gap / total if total > 0 else 0.0,
            100.0 * cov_dom / total if total > 0 else 0.0,
            100.0 * cov_ratio / total if total > 0 else 0.0,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute trajectory stats: %s (lazy eval context)", str(exc)
        )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_payment_trajectory/pipeline.py`
action: delete · base sha256 `db3d25a5fe652c990af8a2280c0f13d84c8c42c976dc6a779147b7ce20726125` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T04b — CC payment & balance trajectory features (re-anchored).

Input wiring note:
    crx_cc_transactions and crx_cc_balance replace the raw/primary-layer inputs.
    Both are T04c intermediates built by crx_cc_raw_extract — T0-scoped per-account
    windows already extracted from the DDI-backed raw tables.

    prm_contract is used to derive account_open_month via the open_date column
    (Way4 monthly contract snapshots, one row per contract per observation month).

Run with:
    kedro run --pipeline=crx_cc_payment_trajectory
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_payment_trajectory


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: build CC payment trajectory from T04c intermediates + spells."""
    return Pipeline(
        [
            node(
                func=build_cc_payment_trajectory,
                inputs=[
                    "crx_cc_transactions",
                    "crx_cc_balance",
                    "crx_cc_spell_table",
                    "prm_contract",
                ],
                outputs="crx_cc_payment_trajectory",
                name="build_crx_cc_payment_trajectory",
                tags=["crx", "payment_trajectory", "t04b"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_utilisation/nodes.py`
action: delete · base sha256 `852e7fbdbea8f5519ee6c9b19a5addfe26e442b7a436e6c262dea9cd002b1a2d` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T05 — CC Utilisation, Spend & Liquidity Features.

# pylint: disable=too-many-locals, too-many-statements
# Rationale: two-pass feature builder (Pass A: monthly utilisation from crx_cc_limits;
# Pass B: transaction-level spend/CA features). Each pass is self-contained.
# Splitting further would obscure the T0-anchored window logic shared across passes.

Build function: build_cc_utilisation_features(crx_cc_limits, crx_cc_transactions,
                                              crx_cc_spell_table,
                                              crx_cc_payment_trajectory)

Output grain: (account_id, spell_id) — one row per delinquency spell.
All lookback windows reuse w_pre_start / w_pre_clean_m from T04b output.

Window design (same as T04b)::

    M0      = trunc(t0, 'month')              — onset month (excluded)
    W_pre   = [w_pre_start, M0)               — clean pre-delinquency window (≤12 months)
    H2      = [M0-3m, M0)       → m_from_m0 1..3  — recent behaviour
    H1      = [w_pre_start, M0-3m) → m_from_m0 ≥ 4  — baseline behaviour

T0 leakage guard: all joins use strict ``obs_date < M0``
(M0 = trunc(t0, 'month')). Onset month excluded; m_from_m0 = 0 never appears.

Truncation columns are read directly from crx_cc_payment_trajectory (T04b output).
No re-derivation of retention floor or account-open-date cuts.

Null rules:
    util_slope       : NULL if < 4 non-null util months in W_pre
    util_accel       : NULL if < 3 non-null util months in W_pre
    util_t0          : NULL if no util snapshot at m_from_m0 == 1
    H2 util features : NULL if w_pre_clean_m < 3 (no H2 months)
    txn_cnt_slope    : NULL if < 4 months with ≥1 transaction
    H2 txn features  : NULL if w_pre_clean_m < 3

Cash-advance detection (R17: replicates feat_transaction.py lines 301-309):
    is_cash_adv = upper(coalesce(txn_description,'')) RLIKE 'CASH ADVANCE|CASH DISBURSEMENT'
    Source column: txn_description (CreditCardTransaction schema).

util_ratio computation:
    util_ratio = (credit_limit - available_limit) / credit_limit * 100
    NULL when credit_limit <= 0 or either column is NULL.
    Source: CreditCardLimit schema (prm_limit catalog key).

Amount convention:
    txn_amount_aed is negative for outflows (debits). Use F.abs() for spend sums.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build_cc_utilisation_features(
    crx_cc_limits: DataFrame,
    crx_cc_transactions: DataFrame,
    crx_cc_spell_table: DataFrame,
    crx_cc_payment_trajectory: DataFrame,
) -> DataFrame:
    """Build CC utilisation, spend & liquidity features anchored to T0 per spell.

    Args:
        crx_cc_limits:              T04c intermediate — T0-scoped CC limit snapshots.
                                    Replaces prm_limit.
                                    Required cols: contract_id, observation_date,
                                    credit_limit, available_limit.
        crx_cc_transactions:        T04c intermediate — T0-scoped CC transactions.
                                    Replaces prm_transaction.
                                    Required cols: contract_id, observation_date,
                                    direction, txn_amount_aed, txn_description.
        crx_cc_spell_table:         T03b output at (account_id, spell_id) grain.
        crx_cc_payment_trajectory:  T04b output — carries w_pre truncation columns.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id, spell_id, t0,
            util_mean_h1, util_mean_h2, util_t0,
            util_slope, util_accel,
            cash_adv_ramp, cash_adv_amt_share_h2,
            spend_taper_ratio, spend_cliff_flag,
            spend_active_days_share_h2, txn_cnt_slope,
            w_pre_start, w_pre_clean_m,
            w_pre_contaminated_flag, w_pre_truncation_reason,
            computed_at
    """
    # ── Step 0: spell base + truncation columns from T04b ──────────────────────
    # Excludes both censored subtypes (data_depth + restructured_entry) — see
    # cc_payment_trajectory/nodes.py Step 0 comment for rationale.
    spell = crx_cc_spell_table.filter(F.col("t0_censored_flag") == 0).select(
        "account_id", "spell_id", "t0"
    )

    trunc = crx_cc_payment_trajectory.select(
        "account_id",
        "spell_id",
        "w_pre_start",
        "w_pre_clean_m",
        "w_pre_contaminated_flag",
        "w_pre_truncation_reason",
    )

    # Inner join: any spell absent from T04b output is excluded (should not happen
    # for non-censored spells; inner join surfaces unexpected mismatches via row count).
    spell_w = spell.join(trunc, on=["account_id", "spell_id"], how="inner")

    # ── Pass A: monthly utilisation (from crx_cc_limits) ───────────────────────
    pass_a = _build_pass_a(crx_cc_limits, spell_w)

    # ── Pass B: spend & cash-advance features (from crx_cc_transactions) ──────
    pass_b1, pass_b2 = _build_pass_b(crx_cc_transactions, spell_w)

    # ── Combine: left-join passes onto spell base ──────────────────────────────
    result = (
        spell_w.join(pass_a, on=["account_id", "spell_id"], how="left")
        .join(pass_b1, on=["account_id", "spell_id"], how="left")
        .join(pass_b2, on=["account_id", "spell_id"], how="left")
        .withColumn("computed_at", F.current_timestamp())
    )

    _log_utilisation_stats(result)

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("util_mean_h1").cast("double"),
        F.col("util_mean_h2").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("util_slope").cast("double"),
        F.col("util_accel").cast("double"),
        F.col("cash_adv_ramp").cast("double"),
        F.col("cash_adv_amt_share_h2").cast("double"),
        F.col("spend_taper_ratio").cast("double"),
        F.col("spend_cliff_flag").cast("int"),
        F.col("spend_active_days_share_h2").cast("double"),
        F.col("txn_cnt_slope").cast("double"),
        F.col("w_pre_start").cast("date"),
        F.col("w_pre_clean_m").cast("int"),
        F.col("w_pre_contaminated_flag").cast("int"),
        F.col("w_pre_truncation_reason").cast("string"),
        F.col("computed_at"),
    )


# ── Private: Pass A ────────────────────────────────────────────────────────────


def _build_pass_a(prm_limit: DataFrame, spell: DataFrame) -> DataFrame:
    """Monthly utilisation features from prm_limit snapshots.

    spell carries w_pre_start and w_pre_clean_m from T04b output.
    Returns one row per (account_id, spell_id).
    Spells with no limit snapshots in W_pre have NULL for all Pass A features.

    Features::

        util_mean_h1    : mean util_ratio over H1 months (m_from_m0 >= 4)
        util_mean_h2    : mean util_ratio over H2 months (m_from_m0 1..3)
        util_t0         : util_ratio at m_from_m0 == 1 (month immediately before T0)
        util_slope      : OLS slope of util_ratio vs m_from_m0 over W_pre
                          (NULL if < 4 non-null months)
        util_accel      : mean second-difference of util_ratio chronologically
                          (NULL if < 3 non-null months)
    """
    scope = spell.select("account_id").distinct()

    limit = (
        prm_limit.select(
            F.col("contract_id"),
            F.col("observation_date").alias("obs_date"),
            F.col("credit_limit"),
            F.col("available_limit"),
        )
        .join(
            F.broadcast(scope),
            prm_limit["contract_id"] == scope["account_id"],
            "leftsemi",
        )
        .withColumn(
            "util_ratio",
            F.when(
                F.col("credit_limit").isNotNull() & (F.col("credit_limit") > 0),
                (F.col("credit_limit") - F.col("available_limit"))
                / F.col("credit_limit")
                * 100.0,
            ).otherwise(F.lit(None).cast("double")),
        )
        .select("contract_id", "obs_date", "util_ratio")
    )

    # Join to spell and filter to W_pre window
    util_w = (
        limit.join(
            spell,
            on=limit["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("obs_date"),
            F.col("util_ratio"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        # One snapshot per month — take the trunc(obs_date,'month') month
        # W_pre: [w_pre_start, M0); M0 = trunc(t0,'month') excluded
        .filter(
            (F.trunc(F.col("obs_date"), "month") >= F.col("w_pre_start"))
            & (F.trunc(F.col("obs_date"), "month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("obs_date"), "month"),
                )
            ).cast("int"),
        )
        # One record per (account_id, spell_id, m_from_m0) — take max util if duplicates
        .groupBy("account_id", "spell_id", "m_from_m0")
        .agg(F.first("util_ratio").alias("util_ratio"))
    )

    # ── Rank rows for util_accel boundary accumulators ─────────────────────────
    # rank_oldest: 1 = oldest month (highest m_from_m0, farthest from T0)
    # rank_newest: 1 = newest month (lowest m_from_m0, closest to T0)
    w_oldest = Window.partitionBy("account_id", "spell_id").orderBy(F.desc("m_from_m0"))
    w_newest = Window.partitionBy("account_id", "spell_id").orderBy("m_from_m0")

    util_w = (
        util_w.filter(F.col("util_ratio").isNotNull())
        .withColumn("_rank_oldest", F.row_number().over(w_oldest))
        .withColumn("_rank_newest", F.row_number().over(w_newest))
    )

    # ── Spell-level aggregation ────────────────────────────────────────────────
    agg = util_w.groupBy("account_id", "spell_id").agg(
        # H1 / H2 means
        F.avg(F.when(F.col("m_from_m0") >= 4, F.col("util_ratio"))).alias(
            "util_mean_h1"
        ),
        F.avg(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("util_ratio"),
            )
        ).alias("util_mean_h2"),
        # util_t0: value at m_from_m0 == 1 (month immediately before T0)
        F.first(
            F.when(F.col("m_from_m0") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("util_t0"),
        # Non-null count for null guards
        F.count(F.lit(1)).alias("_n_util"),
        # OLS accumulators for util_slope (x = m_from_m0)
        F.sum(F.col("m_from_m0").cast("double")).alias("_sx"),
        F.sum(F.col("util_ratio")).alias("_sy"),
        F.sum(F.col("m_from_m0").cast("double") * F.col("util_ratio")).alias("_sxy"),
        F.sum(
            F.col("m_from_m0").cast("double") * F.col("m_from_m0").cast("double")
        ).alias("_sx2"),
        # util_accel boundary accumulators (telescoping second-difference)
        # u_first = util at oldest rank (highest m_from_m0)
        # u_second = util at second oldest
        # u_penultimate = util at second newest
        # u_last = util at newest (lowest m_from_m0)
        F.first(
            F.when(F.col("_rank_oldest") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_first"),
        F.first(
            F.when(F.col("_rank_oldest") == 2, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_second"),
        F.first(
            F.when(F.col("_rank_newest") == 2, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_penultimate"),
        F.first(
            F.when(F.col("_rank_newest") == 1, F.col("util_ratio")), ignorenulls=True
        ).alias("_u_last"),
    )

    # ── Derive slope + accel with null guards ──────────────────────────────────
    _denom = F.col("_n_util").cast("double") * F.col("_sx2") - F.col("_sx") * F.col(
        "_sx"
    )

    agg = agg.withColumn(
        "util_slope",
        F.when(
            (F.col("_n_util") >= 4) & (_denom != 0.0),
            (
                F.col("_n_util").cast("double") * F.col("_sxy")
                - F.col("_sx") * F.col("_sy")
            )
            / _denom,
        ).otherwise(F.lit(None).cast("double")),
    ).withColumn(
        "util_accel",
        # mean second-difference = (u_last - u_penultimate - u_second + u_first) / (n - 2)
        F.when(
            (F.col("_n_util") >= 3)
            & F.col("_u_first").isNotNull()
            & F.col("_u_second").isNotNull()
            & F.col("_u_penultimate").isNotNull()
            & F.col("_u_last").isNotNull(),
            (
                F.col("_u_last")
                - F.col("_u_penultimate")
                - F.col("_u_second")
                + F.col("_u_first")
            )
            / (F.col("_n_util").cast("double") - 2.0),
        ).otherwise(F.lit(None).cast("double")),
    )

    return agg.select(
        "account_id",
        "spell_id",
        "util_mean_h1",
        "util_mean_h2",
        "util_t0",
        "util_slope",
        "util_accel",
    )


# ── Private: Pass B ────────────────────────────────────────────────────────────


def _build_pass_b(
    prm_transaction: DataFrame,
    spell: DataFrame,
) -> tuple:
    """Spend and cash-advance features from outflow transactions.

    Returns two DataFrames:
        pass_b1 : (account_id, spell_id) with spend_active_days_share_h2
        pass_b2 : (account_id, spell_id) with cash_adv_ramp, cash_adv_amt_share_h2,
                  spend_taper_ratio, spend_cliff_flag, txn_cnt_slope

    spell carries w_pre_start and w_pre_clean_m from T04b.

    Cash-advance detection (replicates feat_transaction.py lines 301-309)::

        is_cash_adv = upper(coalesce(txn_description,'')) RLIKE 'CASH ADVANCE|CASH DISBURSEMENT'

    Amount convention: txn_amount_aed is negative for outflows (debits). F.abs() used
    for spend sums to yield positive AED amounts.
    """
    scope = spell.select("account_id").distinct()

    # Outflows only (direction == -1)
    txn_out = (
        prm_transaction.filter(F.col("direction") == -1)
        .select(
            F.col("contract_id"),
            F.col("observation_date").alias("txn_date"),
            F.abs(F.col("txn_amount_aed")).alias("txn_amount_aed"),
            F.col("txn_description"),
        )
        .join(
            F.broadcast(scope),
            prm_transaction["contract_id"] == scope["account_id"],
            "leftsemi",
        )
    )

    # Cash-advance flag (replicates feat_transaction.py logic)
    is_cash_adv = F.upper(F.coalesce(F.col("txn_description"), F.lit(""))).rlike(
        "CASH ADVANCE|CASH DISBURSEMENT"
    )

    txn_out = txn_out.withColumn(
        "is_cash_adv", F.when(is_cash_adv, F.lit(1)).otherwise(0)
    )

    # Join spell and filter to W_pre window
    txn_w = (
        txn_out.join(
            spell,
            on=txn_out["contract_id"] == spell["account_id"],
            how="inner",
        )
        .select(
            F.col("account_id"),
            F.col("spell_id"),
            F.col("t0"),
            F.col("txn_date"),
            F.col("txn_amount_aed"),
            F.col("is_cash_adv"),
            F.col("w_pre_start"),
            F.col("w_pre_clean_m"),
        )
        .filter(
            (F.col("txn_date") >= F.col("w_pre_start"))
            & (F.col("txn_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("txn_date"), "month"),
                )
            ).cast("int"),
        )
    )

    # ── Sub-pass B1: active days share in H2 (transaction-level groupBy) ───────
    # calendar_days_h2 = number of days in the 3-month H2 window [M0-3m, M0)
    # = datediff(trunc(t0,'month'), add_months(trunc(t0,'month'), -3))
    pass_b1 = (
        txn_w.groupBy("account_id", "spell_id", "t0", "w_pre_clean_m")
        .agg(
            F.countDistinct(
                F.when(F.col("m_from_m0") <= 3, F.to_date(F.col("txn_date")))
            ).alias("_active_days_h2")
        )
        .withColumn(
            "_calendar_days_h2",
            F.datediff(
                F.trunc(F.col("t0"), "month"),
                F.add_months(F.trunc(F.col("t0"), "month"), -3),
            ).cast("double"),
        )
        .withColumn(
            "spend_active_days_share_h2",
            F.when(
                (F.col("w_pre_clean_m") >= 3) & (F.col("_calendar_days_h2") > 0),
                F.col("_active_days_h2").cast("double") / F.col("_calendar_days_h2"),
            ).otherwise(F.lit(None).cast("double")),
        )
        .select("account_id", "spell_id", "spend_active_days_share_h2")
    )

    # ── Sub-pass B2: monthly aggregate → spell aggregate ───────────────────────
    monthly = txn_w.groupBy("account_id", "spell_id", "m_from_m0").agg(
        F.sum("txn_amount_aed").alias("spend_m"),
        F.sum(F.when(F.col("is_cash_adv") == 1, F.lit(1)).otherwise(0)).alias(
            "ca_count_m"
        ),
        F.sum(F.when(F.col("is_cash_adv") == 1, F.col("txn_amount_aed"))).alias(
            "ca_amt_m"
        ),
        F.count("*").alias("txn_count_m"),
    )

    m = F.col("m_from_m0")

    feats_b2 = monthly.groupBy("account_id", "spell_id").agg(
        # H1/H2 spend means for taper ratio
        F.avg(F.when(m <= 3, F.col("spend_m"))).alias("_spend_h2_avg"),
        F.avg(F.when(m >= 4, F.col("spend_m"))).alias("_spend_h1_avg"),
        # M0-1 and M0-2 spend for cliff flag
        F.sum(F.when(m == 1, F.col("spend_m")).otherwise(0)).alias("_spend_m1"),
        F.sum(F.when(m == 2, F.col("spend_m")).otherwise(0)).alias("_spend_m2"),
        # Cash-advance ramp: (sum CA count H2 + 1) / (avg CA count H1 + 1)
        F.sum(F.when(m <= 3, F.col("ca_count_m")).otherwise(0)).alias("_ca_cnt_h2"),
        F.avg(F.when(m >= 4, F.col("ca_count_m"))).alias("_ca_cnt_h1_avg"),
        # Cash-advance amount share in H2
        F.sum(F.when(m <= 3, F.col("ca_amt_m")).otherwise(0)).alias("_ca_amt_h2"),
        F.sum(F.when(m <= 3, F.col("spend_m")).otherwise(0)).alias("_spend_h2_sum"),
        # OLS accumulators for txn_cnt_slope (x = -m_from_m0 → positive = increasing toward T0)
        F.count("*").alias("_ols_n"),
        F.sum((-m).cast("double")).alias("_ols_sx"),
        F.sum(F.pow(-m, 2)).alias("_ols_sx2"),
        F.sum(F.col("txn_count_m").cast("double")).alias("_ols_sy"),
        F.sum((-m).cast("double") * F.col("txn_count_m").cast("double")).alias(
            "_ols_sxy"
        ),
    )

    # ── Post-aggregate derived features ────────────────────────────────────────
    _ols_denom = F.col("_ols_n").cast("double") * F.col("_ols_sx2") - F.col(
        "_ols_sx"
    ) * F.col("_ols_sx")

    feats_b2 = (
        feats_b2
        # spend_taper_ratio: avg(H2 spend) / avg(H1 spend) — NULL if either is NULL
        .withColumn(
            "spend_taper_ratio",
            F.when(
                F.col("_spend_h2_avg").isNotNull()
                & F.col("_spend_h1_avg").isNotNull()
                & (F.col("_spend_h1_avg") > 0),
                F.col("_spend_h2_avg") / F.col("_spend_h1_avg"),
            ).otherwise(F.lit(None).cast("double")),
        )
        # spend_cliff_flag: M0-1 spend < 20% of H1 avg AND M0-2 spend >= 80% of H1 avg
        .withColumn(
            "spend_cliff_flag",
            F.when(
                F.col("_spend_h1_avg").isNotNull() & (F.col("_spend_h1_avg") > 0),
                F.when(
                    (F.col("_spend_m1") < 0.2 * F.col("_spend_h1_avg"))
                    & (F.col("_spend_m2") >= 0.8 * F.col("_spend_h1_avg")),
                    F.lit(1),
                ).otherwise(F.lit(0)),
            ).otherwise(F.lit(0)),
        )
        # cash_adv_ramp: (sum CA count H2 + 1) / (avg CA count H1 + 1)
        .withColumn(
            "cash_adv_ramp",
            (F.col("_ca_cnt_h2").cast("double") + 1.0)
            / (F.coalesce(F.col("_ca_cnt_h1_avg"), F.lit(0.0)) + 1.0),
        )
        # cash_adv_amt_share_h2: total CA amt H2 / total spend H2
        .withColumn(
            "cash_adv_amt_share_h2",
            F.when(
                (F.col("_spend_h2_sum").isNotNull()) & (F.col("_spend_h2_sum") != 0),
                F.col("_ca_amt_h2") / F.col("_spend_h2_sum"),
            ).otherwise(F.lit(None).cast("double")),
        )
        # txn_cnt_slope: OLS slope, NULL if < 4 months
        .withColumn(
            "txn_cnt_slope",
            F.when(
                (F.col("_ols_n") >= 4) & (_ols_denom != 0.0),
                (
                    F.col("_ols_n").cast("double") * F.col("_ols_sxy")
                    - F.col("_ols_sx") * F.col("_ols_sy")
                )
                / _ols_denom,
            ).otherwise(F.lit(None).cast("double")),
        )
    )

    pass_b2 = feats_b2.select(
        "account_id",
        "spell_id",
        "spend_taper_ratio",
        "spend_cliff_flag",
        "cash_adv_ramp",
        "cash_adv_amt_share_h2",
        "txn_cnt_slope",
    )

    return pass_b1, pass_b2


# ── Private: logging ───────────────────────────────────────────────────────────


def _log_utilisation_stats(result: DataFrame) -> None:
    """Log coverage summary for the built utilisation table."""
    try:
        total = result.count()
        cov_util = result.filter(F.col("util_mean_h2").isNotNull()).count()
        cov_spend = result.filter(F.col("spend_taper_ratio").isNotNull()).count()
        cov_cliff = result.filter(F.col("spend_cliff_flag").isNotNull()).count()
        LOG.info(
            "CC utilisation features built: %d spells | "
            "util_mean_h2: %.1f%% | spend_taper_ratio: %.1f%% | spend_cliff_flag: %.1f%%",
            total,
            100.0 * cov_util / total if total > 0 else 0.0,
            100.0 * cov_spend / total if total > 0 else 0.0,
            100.0 * cov_cliff / total if total > 0 else 0.0,
        )
    except Exception as exc:  # pylint: disable=broad-except
        LOG.warning(
            "Could not compute utilisation stats: %s (lazy eval context)", str(exc)
        )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_utilisation/pipeline.py`
action: delete · base sha256 `cc6f49227c68c3594db35e8df51d11173009a98bacde932b53cdc975a00fc910` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T05 — CC utilisation, spend & liquidity features.

Input wiring note:
    crx_cc_limits (catalog key) replaces prm_limit.
    crx_cc_transactions replaces prm_transaction.
    Both are T04c intermediates (T0-scoped DDI raw extracts) with full history
    needed for cc_180_plus accounts where T0 may be 18-24+ months before
    observation_date.

    crx_cc_payment_trajectory is the 4th input — provides w_pre truncation
    columns (w_pre_start, w_pre_clean_m, w_pre_contaminated_flag,
    w_pre_truncation_reason) computed in T04b, avoiding re-derivation here.

Run with:
    kedro run --pipeline=crx_cc_utilisation_features
"""

from kedro.pipeline import Pipeline, node

from .nodes import build_cc_utilisation_features


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Single-node pipeline: build CC utilisation features."""
    return Pipeline(
        [
            node(
                func=build_cc_utilisation_features,
                inputs=[
                    "crx_cc_limits",
                    "crx_cc_transactions",
                    "crx_cc_spell_table",
                    "crx_cc_payment_trajectory",
                ],
                outputs="crx_cc_utilisation_features",
                name="build_crx_cc_utilisation_features",
                tags=["crx", "utilisation", "t05"],
            ),
        ],
        tags=["crx_persona"],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/nodes.py`
action: delete · base sha256 `1cfcebece045da21dcb742b7dca78a880b5372b63e50227aba8e9cfad0308852` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A2 Locatability axis — RL-specific adapter nodes (RL-A2-1).

# pylint: disable=too-many-locals

Four-node pipeline adapter that reuses CC A2 logic via thin wrappers:

    build_rl_a2_base            → crx_rl_a2_base            [Node 1]
    build_rl_a2_login_presence  → crx_rl_a2_login_presence  [Node 2]
    build_rl_a2_contact_signals→ crx_rl_a2_contact_signals[Node 3]
    build_a2_locatability       → crx_rl_a2_locatability    [Node 4] (CC import)

Node 1 difference from CC: crx_rl_a4_spine already carries (account_id,
observation_date, spell_id, t0, cif_id) from the spine-projection join (rl_a4_spine
pipeline) — no separate spell table join is needed. Departure signals sourced
from crx_rl_departure_signature (RL-A2-2 pre-computation pipeline).

Departure signals (RL-A2-2):
    travel_mcc_flag_h2     — H2 debit travel MCC from comp_financial_tran_repos_dly
    last_txn_foreign_flag  — FX leakage proxy (99.88% CIF coverage)
    foreign_login_flag     — PIT foreign login from prm_digital_login_monthly
    casa_inflow_stop_gap_d — from crx_rl_departure_signature itself (Pass B)

Node 2: obs_month_end=True because RL observation dates are month-end.

Node 3: applies DCORE 24-month partition floor before calling CC function
    (action_ts filter for performance — dcore_prm_followup_outcomes is large).
"""

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.nodes import (
    build_a2_contact_signals,
    build_a2_locatability,  # noqa: F401 — re-exported for pipeline use
    build_a2_login_presence,
)

LOG = logging.getLogger(__name__)

__all__ = [
    "build_rl_a2_base",
    "build_rl_a2_login_presence",
    "build_rl_a2_contact_signals",
    "build_a2_locatability",
]


# ── Node 1: build_rl_a2_base ───────────────────────────────────────────────────


def build_rl_a2_base(
    crx_rl_a4_spine: DataFrame,
    crx_rl_departure_signature: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Build RL A2 base. Mirrors crx_cc_a2_base schema.

    crx_rl_a4_spine already carries (account_id, observation_date, spell_id,
    t0, cif_id). No separate spell table join needed.

    Departure signals sourced from crx_rl_departure_signature (RL-A2-2 pipeline):
        travel_mcc_flag_h2     — H2 debit travel MCC from comp_financial_tran_repos_dly
        last_txn_foreign_flag  — FX leakage proxy (99.88% CIF coverage)
        foreign_login_flag     — PIT foreign login from prm_digital_login_monthly
        casa_inflow_stop_gap_d — forwarded from crx_rl_a4_class

    Left-join crx_rl_departure_signature on (account_id, observation_date).
    All 4 departure-trail columns are non-null on join hit (coalesced in RL-A2-2 Node 3).

    Args:
        crx_rl_a4_spine:            RL spine at (account_id, observation_date) grain.
            Required cols: account_id, observation_date, spell_id, t0, cif_id.
        crx_rl_departure_signature: RL departure pre-computation (RL-A2-2).
            Required cols: account_id, observation_date, travel_mcc_flag_h2,
            last_txn_foreign_flag, foreign_login_flag, casa_inflow_stop_gap_d.
        crx_persona:                Persona param dict with persona_start_date /
                                    persona_end_date.

    Returns:
        DataFrame at grain (account_id, observation_date) — schema matches
        crx_cc_a2_base departure-trail columns::

            account_id              (string)
            observation_date        (date)
            spell_id                (int)
            t0                      (date)
            cif_id                  (string)
            travel_mcc_flag_h2      (int)    0/1
            last_txn_foreign_flag   (int)    0/1
            foreign_login_flag      (int)    0/1
            casa_inflow_stop_gap_d  (double) NULL if no salary inflow in [M0-24m, M0)
    """
    base = crx_rl_a4_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("cif_id").cast("string"),
    )

    depart = crx_rl_departure_signature.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
        F.col("last_txn_foreign_flag").cast("int"),
        F.col("foreign_login_flag").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
    )

    result = base.join(
        depart, on=["account_id", "observation_date"], how="left"
    ).select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("cif_id").cast("string"),
        F.coalesce(F.col("travel_mcc_flag_h2"), F.lit(0))
        .cast("int")
        .alias("travel_mcc_flag_h2"),
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0))
        .cast("int")
        .alias("last_txn_foreign_flag"),
        F.coalesce(F.col("foreign_login_flag"), F.lit(0))
        .cast("int")
        .alias("foreign_login_flag"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
    )

    n_rows = result.count()
    LOG.info(
        "build_rl_a2_base [%s → %s]: %d spine rows | departure signals joined from "
        "crx_rl_departure_signature",
        crx_persona["persona_start_date"],
        crx_persona["persona_end_date"],
        n_rows,
    )

    return result


# ── Node 2: build_rl_a2_login_presence ─────────────────────────────────────────


def build_rl_a2_login_presence(
    base: DataFrame,
    prm_login: DataFrame,
) -> DataFrame:
    """Obs-date-anchored digital presence signals for RL. Thin wrapper.

    Delegates to build_a2_login_presence with obs_month_end=True because RL
    observation dates are month-end (the observation month is fully closed,
    so the login month is safe to include).

    Args:
        base:      crx_rl_a2_base — must carry cif_id (propagated from Node 1).
        prm_login: prm_digital_login_monthly.

    Returns:
        crx_rl_a2_login_presence — same schema as crx_cc_a2_login_presence.
    """
    return build_a2_login_presence(
        base=base,
        prm_login=prm_login,
        obs_month_end=True,
    )


# ── Node 3: build_rl_a2_contact_signals ────────────────────────────────────────


def build_rl_a2_contact_signals(
    base: DataFrame,
    observation_spine: DataFrame,
    followup_outcomes: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """DCORE contact signals for RL. Thin wrapper with 24m partition floor.

    Applies a partition floor on dcore_prm_followup_outcomes to avoid scanning
    the full DCORE history (performance guard per TASKS_RL.md). Floor =
    persona_start_date - 24m; covers all T0 dates in the persona window plus
    the full post-T0 delinquency window up to observation_date.

    Delegates to build_a2_contact_signals from CC (R14 reuse).

    Args:
        base:              crx_rl_a2_base.
        observation_spine: dcore_observation_spine (RL-scoped, built by RL-D5).
            Required cols: account_id, observation_date, agreement_id, cif_id.
        followup_outcomes: dcore_prm_followup_outcomes.
        crx_persona:       params dict with persona_start_date.

    Returns:
        crx_rl_a2_contact_signals — same schema as crx_cc_a2_contact_signals.
    """
    persona_start_date = crx_persona["persona_start_date"]
    dcore_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=24)
    ).isoformat()

    followup_filtered = followup_outcomes.filter(
        F.col("action_ts").cast("date") >= F.lit(dcore_floor)
    )

    return build_a2_contact_signals(
        base=base,
        observation_spine=observation_spine,
        followup=followup_filtered,
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/__init__.py`
action: delete · base sha256 `4da50dfda151844ee71ce62ddcc48e2ea94949ca727e0113c9e2efccc55b474e` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL Departure Signature pipeline (RL-A2-2).

Inputs: rl_spine, crx_rl_spell_table, comp_financial_tran_repos_dly,
        feat_payroll_indicator, feat_fx_leakage, prm_digital_login_monthly
Output: crx_rl_departure_signature
"""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/nodes.py`
action: delete · base sha256 `642f48d97e852409443a86339f05381e07bbccc35691ab1bcd0ad2c5fb5bb995` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL Departure Signature — 5-node pipeline (RL-A2-2, aligned to CC T06 order).

# pylint: disable=too-many-locals

Departure signature runs standalone BEFORE rl_a1_ability, mirroring the CC
T06→T07 execution order. Node 0 (build_rl_depart_spine) is also reused directly
by the rl_a4_spine pipeline (R14) to produce crx_rl_a4_spine's structural
projection, and Node 5 of rl_a1_ability reads this pipeline's output
(crx_rl_departure_signature) for eosb_like_flag.

Signals produced:
    travel_mcc_flag_h2       : H2 debit travel MCC hits from comp_financial_tran_repos_dly
    last_txn_foreign_flag    : FX leakage proxy (99.88% coverage)
    foreign_login_flag       : PIT foreign login from prm_digital_login_monthly
    casa_inflow_stop_gap_d   : days from last salary credit to M0 (Pass B)
    eosb_like_flag           : end-of-service benefit spike detection (Pass B)
    payroll_present_h2       : payroll present in H2 [T0-3m, T0) (Pass I)
    payroll_stopped_flag     : payroll was in H1 but absent in H2 (Pass I)

Output dataset: crx_rl_departure_signature at grain (account_id, observation_date).

Pipeline nodes:
    build_rl_depart_spine          → crx_rl_depart_spine           [Node 0]
    build_rl_depart_casa_signals   → crx_rl_depart_casa_signals    [Node 1]
    build_rl_depart_travel_mcc     → crx_rl_depart_travel_mcc      [Node 2]
    build_rl_depart_foreign_signals → crx_rl_depart_foreign_signals [Node 3]
    build_rl_departure_final       → crx_rl_departure_signature     [Node 4]

Window anchor: t0 (first delinquency onset month).
H2_blk = [add_months(trunc(t0,'month'), -3), trunc(t0,'month'))
"""

# pylint: disable=too-many-locals,duplicate-code

import logging
from datetime import date

from dateutil.relativedelta import relativedelta
from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_departure_signature.nodes import (
    _TRAVEL_KEYWORDS_RE,
    _TRAVEL_MCCS,
)

LOG = logging.getLogger(__name__)

_FX_COL = "ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum"

# ── CASA salary / payroll constants (moved from rl_a4_class/nodes.py) ──────────
# FI-1 resolved 2026-08-21: sourced from wealth_management ENBD entity params
_SALARY_CODES = [
    "505",
    "506",
    "507",
    "503",
    "585",
    "586",
    "587",
    "588",
    "085",
    "086",
    "087",
    "088",
    "328",
    "828",
]
_SALARY_EXCLUDE_CODES = ["947", "LV3", "LV4"]
_TRAN_DC_CREDIT = "C"  # confirmed: WM ENBD entity config
_PAYROLL_HAS_COL = "payroll_flag"  # confirmed via t06d 2026-08-26

__all__ = [
    "build_rl_depart_spine",
    "build_rl_depart_casa_signals",
    "build_rl_depart_travel_mcc",
    "build_rl_depart_foreign_signals",
    "build_rl_departure_final",
]


# ── Node 0: build_rl_depart_spine ──────────────────────────────────────────────


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


# ── Node 1: build_rl_depart_casa_signals ───────────────────────────────────────


def build_rl_depart_casa_signals(  # pylint: disable=too-many-locals
    crx_rl_depart_spine: DataFrame,
    comp_financial_tran_repos_dly: DataFrame,
    feat_payroll_indicator: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Compute CASA salary + payroll signals for departure signature (Node 1 of 5).

    Ports build_rl_a4_casa_signals (formerly rl_a4_class Node 1) to use
    crx_rl_depart_spine as the scope anchor. The spine is already filtered to
    persona-window non-censored active spells; no additional spell-table join needed.

    Sub-A (Pass B port — CASA salary inflow stop):
        Window: [M0-24m, M0) per account.
        Outputs: casa_inflow_stop_gap_d, eosb_like_flag.

    Sub-B (Pass I port — payroll indicator):
        Window: [M0-12m, M0), H2=[M0-3m, M0), H1=[M0-12m, M0-3m).
        Outputs: payroll_present_h2, payroll_stopped_flag.

    Args:
        crx_rl_depart_spine:           Node 0 output — (account_id, observation_date)
            grain scoped to persona window. Required cols: account_id, spell_id, t0,
            cif_id.
        comp_financial_tran_repos_dly: Raw CASA transactions (2.4B rows, R20).
        feat_payroll_indicator:        pri_monthly_payroll_indicator.
        crx_persona:                   Persona param dict — used for edp_load_date
                                       partition filter.

    Returns:
        DataFrame at grain (account_id, spell_id) with schema::

            account_id              string
            spell_id                int
            casa_inflow_stop_gap_d  double  NULL if no salary in [M0-24m, M0)
            eosb_like_flag          int     0/1/NULL
            payroll_present_h2      int     0/1/NULL
            payroll_stopped_flag    int     0/1/NULL
    """
    # Derive spell-grain base from the already-scoped spine
    spell_base = (
        crx_rl_depart_spine.filter(F.col("spell_id").isNotNull())
        .select("account_id", "spell_id", "t0", "cif_id")
        .dropDuplicates(["account_id", "spell_id"])
    )

    persona_start_date = crx_persona["persona_start_date"]
    LOG.info(
        "[%s → %s] build_rl_depart_casa_signals: %d accounts scoped",
        persona_start_date,
        crx_persona["persona_end_date"],
        spell_base.count(),
    )

    # Partition floor for efficiency — same as former build_rl_a4_casa_signals
    casa_floor = (
        date.fromisoformat(persona_start_date) - relativedelta(months=12)
    ).isoformat()
    comp_financial_tran_repos_dly = comp_financial_tran_repos_dly.filter(
        F.col("edp_load_date") >= F.lit(casa_floor)
    )

    payroll_floor_int = int(
        (date.fromisoformat(persona_start_date) - relativedelta(months=12))
        .isoformat()
        .replace("-", "")
    )
    feat_payroll_indicator = feat_payroll_indicator.filter(
        F.col("month_number") >= payroll_floor_int
    )

    account_cif = spell_base.select("account_id", "cif_id")
    t0_for_signals = spell_base.select("account_id", "t0")

    sub_a = _build_rl_pass_b(comp_financial_tran_repos_dly, account_cif, t0_for_signals)
    sub_b = _build_rl_pass_i(feat_payroll_indicator, account_cif, t0_for_signals)

    return (
        spell_base.select("account_id", "spell_id")
        .join(sub_a, on="account_id", how="left")
        .join(sub_b, on="account_id", how="left")
        .select(
            F.col("account_id").cast("string"),
            F.col("spell_id").cast("int"),
            F.col("casa_inflow_stop_gap_d").cast("double"),
            F.col("eosb_like_flag").cast("int"),
            F.col("payroll_present_h2").cast("int"),
            F.col("payroll_stopped_flag").cast("int"),
        )
    )


def _build_rl_pass_b(  # pylint: disable=too-many-locals
    comp_financial_tran_repos_dly: DataFrame,
    account_cif: DataFrame,  # (account_id, cif_id)
    t0_base: DataFrame,  # (account_id, t0)
) -> DataFrame:
    """CASA inflow stop signals — RL adaptation of CC _build_pass_b.

    Returns DataFrame at grain account_id:
        (account_id, casa_inflow_stop_gap_d, eosb_like_flag).

    Window: [M0-24m, M0). Grain: account_id.
    """
    _CASA_REQUIRED = [
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ]
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    missing = [c for c in _CASA_REQUIRED if c not in casa_cols_lower]

    if missing:
        LOG.warning(
            "RL Pass B [CASA]: missing columns %s in comp_financial_tran_repos_dly "
            "— emitting NULL for casa_inflow_stop_gap_d and eosb_like_flag",
            missing,
        )
        return (
            t0_base.select("account_id")
            .withColumn("casa_inflow_stop_gap_d", F.lit(None).cast("double"))
            .withColumn("eosb_like_flag", F.lit(None).cast("int"))
        )

    # R20: scope CASA to relevant CIF IDs BEFORE any date filter
    cif_scope = account_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    casa_scoped = comp_financial_tran_repos_dly.select(
        "cif_id",
        "tran_date",
        "tran_amt_aed",
        "tran_dc",
        "tran_particular_code",
        "tran_narration_1",
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    t0_cif = t0_base.join(
        account_cif.select("account_id", F.col("cif_id").cast("string")),
        on="account_id",
        how="left",
    )

    is_salary = (
        (F.col("tran_dc") == _TRAN_DC_CREDIT)
        & ~F.col("tran_particular_code").isin(_SALARY_EXCLUDE_CODES)
        & (
            F.col("tran_particular_code").isin(_SALARY_CODES)
            | F.upper(F.coalesce(F.col("tran_narration_1"), F.lit(""))).rlike(
                r"SALARY|PAYROLL|SALAR|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK"
            )
        )
    )

    casa_w = (
        casa_scoped.join(t0_cif, on="cif_id", how="inner")
        .filter(
            (F.col("tran_dc") == _TRAN_DC_CREDIT)
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -24))
            & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn("is_salary", is_salary)
    )

    last_sal = (
        casa_w.filter(F.col("is_salary"))
        .groupBy("account_id", "t0")
        .agg(F.max("tran_date").alias("last_sal_date"))
        .withColumn(
            "casa_inflow_stop_gap_d",
            F.datediff(F.trunc(F.col("t0"), "month"), F.col("last_sal_date")).cast(
                "double"
            ),
        )
        .select("account_id", "casa_inflow_stop_gap_d")
    )

    monthly_sal = (
        casa_w.filter(F.col("is_salary"))
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.trunc(F.col("tran_date"), "month"),
                )
            ).cast("int"),
        )
        .groupBy("account_id", "m_from_m0")
        .agg(F.sum("tran_amt_aed").alias("monthly_sal_total"))
    )

    sal_median = (
        monthly_sal.filter((F.col("m_from_m0") >= 7) & (F.col("m_from_m0") <= 24))
        .groupBy("account_id")
        .agg(
            F.percentile_approx("monthly_sal_total", 0.5).alias("monthly_salary_median")
        )
    )

    recent_max = (
        casa_w.filter(
            F.col("is_salary")
            & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -6))
        )
        .groupBy("account_id")
        .agg(F.max("tran_amt_aed").alias("max_sal_recent"))
    )

    eosb = (
        t0_base.select("account_id")
        .join(last_sal, on="account_id", how="left")
        .join(sal_median, on="account_id", how="left")
        .join(recent_max, on="account_id", how="left")
        .withColumn(
            "eosb_like_flag",
            F.when(F.col("monthly_salary_median").isNull(), F.lit(None).cast("int"))
            .when(
                F.col("max_sal_recent").isNotNull()
                & (F.col("monthly_salary_median") > 0)
                & (F.col("max_sal_recent") > 3.0 * F.col("monthly_salary_median"))
                & F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= 90.0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "casa_inflow_stop_gap_d", "eosb_like_flag")
    )

    return eosb


def _build_rl_pass_i(
    feat_payroll_indicator: DataFrame,
    account_cif: DataFrame,  # (account_id, cif_id)
    t0_base: DataFrame,  # (account_id, t0)
) -> DataFrame:
    """Payroll presence and stop signals — RL adaptation of CC _build_pass_i.

    Returns DataFrame at grain account_id:
        (account_id, payroll_present_h2, payroll_stopped_flag).

    Window: [M0-12m, M0). H2 = m_from_m0 in [1, 3]; H1 = m_from_m0 in [4, 12].
    _PAYROLL_HAS_COL = 'payroll_flag' confirmed via t06d 2026-08-26.
    """
    _REQUIRED = ["cif_id", "month_number"]
    pay_cols_lower = {c.lower() for c in feat_payroll_indicator.columns}
    missing_base = [c for c in _REQUIRED if c not in pay_cols_lower]

    if missing_base:
        LOG.warning(
            "RL Pass I [payroll]: missing base columns %s in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            missing_base,
        )
        return (
            t0_base.select("account_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    if _PAYROLL_HAS_COL not in pay_cols_lower:
        LOG.warning(
            "RL Pass I [payroll]: column '%s' absent in feat_payroll_indicator "
            "— emitting NULL for payroll_present_h2, payroll_stopped_flag",
            _PAYROLL_HAS_COL,
        )
        return (
            t0_base.select("account_id")
            .withColumn("payroll_present_h2", F.lit(None).cast("int"))
            .withColumn("payroll_stopped_flag", F.lit(None).cast("int"))
        )

    cif_scope = account_cif.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    pay_scoped = feat_payroll_indicator.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number"), "yyyyMMdd").alias("pay_month"),
        F.col(_PAYROLL_HAS_COL).cast("int").alias("_has_payroll"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    t0_cif = t0_base.join(
        account_cif.select("account_id", F.col("cif_id").cast("string")),
        on="account_id",
        how="left",
    )

    pay_w = (
        pay_scoped.join(t0_cif, on="cif_id", how="inner")
        .filter(
            (F.col("pay_month") >= F.add_months(F.trunc(F.col("t0"), "month"), -12))
            & (F.col("pay_month") < F.trunc(F.col("t0"), "month"))
        )
        .withColumn(
            "m_from_m0",
            F.floor(
                F.months_between(
                    F.trunc(F.col("t0"), "month"),
                    F.col("pay_month"),
                )
            ).cast("int"),
        )
    )

    agg = pay_w.groupBy("account_id").agg(
        F.max(
            F.when(
                (F.col("m_from_m0") >= 1) & (F.col("m_from_m0") <= 3),
                F.col("_has_payroll"),
            )
        ).alias("_h2_max"),
        F.max(
            F.when(
                (F.col("m_from_m0") >= 4) & (F.col("m_from_m0") <= 12),
                F.col("_has_payroll"),
            )
        ).alias("_h1_max"),
        F.count(
            F.when((F.col("m_from_m0") >= 4) & (F.col("m_from_m0") <= 12), F.lit(1))
        ).alias("_h1_row_count"),
    )

    result = (
        agg.withColumn(
            "payroll_present_h2",
            F.when(
                F.col("_h2_max").isNotNull(), F.col("_h2_max").cast("int")
            ).otherwise(F.lit(None).cast("int")),
        )
        .withColumn(
            "payroll_stopped_flag",
            F.when(
                F.col("_h1_row_count").isNull() | (F.col("_h1_row_count") == 0),
                F.lit(None).cast("int"),
            )
            .when(
                (F.col("_h1_max") == 1) & (F.coalesce(F.col("_h2_max"), F.lit(0)) == 0),
                F.lit(1),
            )
            .otherwise(F.lit(0)),
        )
        .select("account_id", "payroll_present_h2", "payroll_stopped_flag")
    )

    return t0_base.select("account_id").join(result, on="account_id", how="left")


# ── Node 2: build_rl_depart_travel_mcc ─────────────────────────────────────────


def build_rl_depart_travel_mcc(
    crx_rl_depart_spine: DataFrame,
    comp_financial_tran_repos_dly: DataFrame,
) -> DataFrame:
    """Derive travel_mcc_flag_h2 from CASA debit transactions (Node 2 of 5).

    Source: comp_financial_tran_repos_dly.merchant_category (4-digit MCC).
    ~50% populated on POS/debit rows; ~0% on credit-only rows.

    Window: H2_blk = [add_months(trunc(t0,'month'), -3), trunc(t0,'month')).
    Filter: tran_dc = 'D' (debit side only).
    Travel detection: merchant_category.cast(int).isin(_TRAVEL_MCCS) OR
        _TRAVEL_KEYWORDS_RE regex on merchant_name (keyword fallback).

    Null semantics:
        1    — any H2 debit travel hit
        0    — H2 debits exist but none match travel criteria
        NULL — no H2 debit transactions found (not coalesced here; coalesced to 0 in Node 4)

    R20 compliance: CIF-level leftsemi scope applied before any date filter.

    Args:
        crx_rl_depart_spine:           Node 0 output at (account_id, observation_date).
            Required cols: account_id, spell_id, t0, cif_id.
        comp_financial_tran_repos_dly: Raw CASA/debit transaction table.
            Required cols: cif_id, tran_date, tran_dc, merchant_category.
            Optional col: merchant_name (keyword fallback).

    Returns:
        DataFrame at (account_id, observation_date) grain with travel_mcc_flag_h2.
    """
    casa_cols_lower = {c.lower() for c in comp_financial_tran_repos_dly.columns}
    _REQUIRED = ["cif_id", "tran_date", "tran_dc"]

    missing = [c for c in _REQUIRED if c not in casa_cols_lower]
    has_mcc = "merchant_category" in casa_cols_lower
    has_name = "merchant_name" in casa_cols_lower

    if missing or not has_mcc:
        if missing:
            LOG.warning(
                "build_rl_depart_travel_mcc: comp_financial_tran_repos_dly missing columns "
                "%s — travel_mcc_flag_h2 = NULL for all rows.",
                missing,
            )
        else:
            LOG.warning(
                "build_rl_depart_travel_mcc: merchant_category absent from "
                "comp_financial_tran_repos_dly — travel_mcc_flag_h2 = NULL for all rows."
            )
        return crx_rl_depart_spine.select("account_id", "observation_date").withColumn(
            "travel_mcc_flag_h2", F.lit(None).cast("int")
        )

    # ── Account-level scope anchor ─────────────────────────────────────────────
    spell_base = crx_rl_depart_spine.select(
        "account_id", "spell_id", "t0", "cif_id"
    ).dropDuplicates(["account_id", "spell_id"])

    cif_scope = spell_base.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    # R20 scope: leftsemi before date filter
    select_exprs = [
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("tran_date").cast("date").alias("tran_date"),
        F.col("tran_dc").cast("string").alias("tran_dc"),
        F.col("merchant_category").cast("string").alias("merchant_category"),
    ]
    if has_name:
        select_exprs.append(
            F.col("merchant_name").cast("string").alias("merchant_name")
        )
    else:
        select_exprs.append(F.lit(None).cast("string").alias("merchant_name"))

    casa_scoped = comp_financial_tran_repos_dly.select(*select_exprs).join(
        F.broadcast(cif_scope), on="cif_id", how="leftsemi"
    )

    # ── Join to spell base ─────────────────────────────────────────────────────
    casa_spell = casa_scoped.join(
        spell_base.select(
            "account_id",
            "spell_id",
            "t0",
            F.col("cif_id").cast("string").alias("_cif"),
        ),
        on=(casa_scoped["cif_id"] == F.col("_cif")),
        how="inner",
    ).filter(
        (F.col("tran_dc") == "D")
        & (F.col("tran_date") >= F.add_months(F.trunc(F.col("t0"), "month"), -3))
        & (F.col("tran_date") < F.trunc(F.col("t0"), "month"))
    )

    # Travel detection: MCC primary + keyword fallback
    mcc_int = F.col("merchant_category").cast("int")
    is_travel_mcc = mcc_int.isNotNull() & mcc_int.isin(_TRAVEL_MCCS)
    is_travel_kw = F.upper(F.coalesce(F.col("merchant_name"), F.lit(""))).rlike(
        _TRAVEL_KEYWORDS_RE
    )
    is_travel = is_travel_mcc | is_travel_kw

    agg = casa_spell.groupBy("account_id", "spell_id").agg(
        F.max(F.when(is_travel, F.lit(1)).otherwise(F.lit(0))).alias(
            "travel_mcc_flag_h2"
        )
    )

    # Expand to all observation dates via spine join
    spine_obs = crx_rl_depart_spine.select("account_id", "observation_date", "spell_id")
    result = spine_obs.join(agg, on=["account_id", "spell_id"], how="left").select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("travel_mcc_flag_h2").cast("int"),
    )

    n_accounts = spell_base.count()
    n_flagged = agg.filter(F.col("travel_mcc_flag_h2") == 1).count()
    n_null = (
        result.select("account_id")
        .dropDuplicates()
        .join(
            agg.select("account_id"),
            on="account_id",
            how="leftanti",
        )
        .count()
    )
    LOG.info(
        "build_rl_depart_travel_mcc: %d accounts | travel_hit: %d (%.1f%%) | "
        "no_h2_debits (NULL): %d (%.1f%%)",
        n_accounts,
        n_flagged,
        100.0 * n_flagged / max(n_accounts, 1),
        n_null,
        100.0 * n_null / max(n_accounts, 1),
    )

    return result


# ── Node 3: build_rl_depart_foreign_signals ────────────────────────────────────


def build_rl_depart_foreign_signals(  # pylint: disable=too-many-locals
    crx_rl_depart_spine: DataFrame,
    feat_fx_leakage: DataFrame,
    prm_digital_login_monthly: DataFrame,
) -> DataFrame:
    """Derive last_txn_foreign_flag and foreign_login_flag (Node 3 of 5).

    last_txn_foreign_flag:
        FX leakage proxy — same logic as former RL A2 Node 1.
        Account-grain join at T0 month; broadcast to all observation dates.
        Source: feat_fx_leakage (fea_monthly_agg_fx_leakage).
        flag=1 if ft_amt_cross_border_outflow_txn_in_last_0_2_months_sum > 0 at T0.

    foreign_login_flag:
        PIT join per (account_id, observation_date).
        Most recent login month <= trunc(observation_date, 'month').
        Extracts last_login_foreign_flag from prm_digital_login_monthly.
        Same source and semantics as CC Pass J.

    Args:
        crx_rl_depart_spine:       Node 0 output at (account_id, observation_date).
            Required cols: account_id, observation_date, spell_id, t0, cif_id.
        feat_fx_leakage:           fea_monthly_agg_fx_leakage.
            Required cols: cif_id, month_number, _FX_COL.
        prm_digital_login_monthly: Monthly OMB login aggregation.
            Required cols: cif_id, month_number, last_login_foreign_flag.

    Returns:
        DataFrame at (account_id, observation_date) grain with:
            last_txn_foreign_flag   (int) 0/1
            foreign_login_flag      (int) 0/1/NULL
    """
    # ── Part A: last_txn_foreign_flag ──────────────────────────────────────────
    spell_base = crx_rl_depart_spine.select(
        "account_id", "spell_id", "t0", "cif_id"
    ).dropDuplicates(["account_id", "spell_id"])

    _required_fx = {"cif_id", "month_number", _FX_COL}
    if not _required_fx.issubset({c.lower() for c in feat_fx_leakage.columns}):
        missing = _required_fx - {c.lower() for c in feat_fx_leakage.columns}
        LOG.warning(
            "build_rl_depart_foreign_signals: feat_fx_leakage missing %s "
            "— last_txn_foreign_flag = 0 for all rows.",
            missing,
        )
        fx_flag_by_account = spell_base.select("account_id", "spell_id").withColumn(
            "last_txn_foreign_flag", F.lit(0).cast("int")
        )
    else:
        fx_dated = feat_fx_leakage.select(
            F.col("cif_id").cast("string").alias("_fx_cif"),
            F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
                "_fx_month"
            ),
            F.col(_FX_COL).alias("_fx_amt"),
        )

        joined_fx = spell_base.join(
            fx_dated,
            on=(
                (spell_base["cif_id"].cast("string") == fx_dated["_fx_cif"])
                & (
                    F.trunc(fx_dated["_fx_month"], "month")
                    == F.trunc(spell_base["t0"], "month")
                )
            ),
            how="left",
        ).withColumn(
            "last_txn_foreign_flag",
            F.coalesce(
                F.when(F.col("_fx_amt") > 0, F.lit(1)).otherwise(F.lit(0)),
                F.lit(0),
            ).cast("int"),
        )

        fx_flag_by_account = joined_fx.select(
            "account_id", "spell_id", "last_txn_foreign_flag"
        ).dropDuplicates(["account_id", "spell_id"])

        n_fx = fx_flag_by_account.count()
        n_fx_flagged = fx_flag_by_account.filter(
            F.col("last_txn_foreign_flag") == 1
        ).count()
        LOG.info(
            "build_rl_depart_foreign_signals: FX — %d accounts | "
            "last_txn_foreign_flag=1: %d (%.1f%%)",
            n_fx,
            n_fx_flagged,
            100.0 * n_fx_flagged / max(n_fx, 1),
        )

    # Broadcast fx flag to all observation dates
    spine_obs = crx_rl_depart_spine.select(
        "account_id", "observation_date", "spell_id", "cif_id"
    )
    with_fx = spine_obs.join(
        fx_flag_by_account, on=["account_id", "spell_id"], how="left"
    ).withColumn(
        "last_txn_foreign_flag",
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0)).cast("int"),
    )

    # ── Part B: foreign_login_flag ─────────────────────────────────────────────
    _required_login = {"cif_id", "month_number", "last_login_foreign_flag"}
    login_cols_lower = {c.lower() for c in prm_digital_login_monthly.columns}
    missing_login = [c for c in _required_login if c not in login_cols_lower]

    if missing_login:
        LOG.warning(
            "build_rl_depart_foreign_signals: prm_digital_login_monthly missing %s "
            "— foreign_login_flag = 0 for all rows.",
            missing_login,
        )
        result = with_fx.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("last_txn_foreign_flag").cast("int"),
            F.lit(0).cast("int").alias("foreign_login_flag"),
        )
        return result

    cif_scope = spine_obs.select(
        F.col("cif_id").cast("string").alias("cif_id")
    ).distinct()

    login_scoped = prm_digital_login_monthly.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
            "login_month"
        ),
        F.col("last_login_foreign_flag").cast("int").alias("_foreign_flag"),
    ).join(F.broadcast(cif_scope), on="cif_id", how="leftsemi")

    # PIT join: all login months <= trunc(observation_date, 'month')
    login_w = with_fx.join(
        login_scoped,
        on=(with_fx["cif_id"].cast("string") == login_scoped["cif_id"]),
        how="left",
    ).filter(
        F.col("login_month").isNull()
        | (F.col("login_month") <= F.trunc(F.col("observation_date"), "month"))
    )

    # Most recent login per (account_id, observation_date)
    w_recent = Window.partitionBy("account_id", "observation_date").orderBy(
        F.col("login_month").desc_nulls_last()
    )

    result = (
        login_w.withColumn("_rn", F.row_number().over(w_recent))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date"),
            F.col("last_txn_foreign_flag").cast("int"),
            F.col("_foreign_flag").cast("int").alias("foreign_login_flag"),
        )
    )

    n_obs = result.count()
    n_login_flagged = result.filter(F.col("foreign_login_flag") == 1).count()
    n_login_null = result.filter(F.col("foreign_login_flag").isNull()).count()
    LOG.info(
        "build_rl_depart_foreign_signals: login — %d obs rows | "
        "foreign_login_flag=1: %d (%.1f%%) | NULL: %d (%.1f%%)",
        n_obs,
        n_login_flagged,
        100.0 * n_login_flagged / max(n_obs, 1),
        n_login_null,
        100.0 * n_login_null / max(n_obs, 1),
    )

    return result


# ── Node 4: build_rl_departure_final ───────────────────────────────────────────


def build_rl_departure_final(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    crx_rl_depart_spine: DataFrame,
    crx_rl_depart_travel_mcc: DataFrame,
    crx_rl_depart_foreign_signals: DataFrame,
    crx_rl_depart_casa_signals: DataFrame,
) -> DataFrame:
    """Assemble crx_rl_departure_signature (Node 4 of 5).

    Joins Nodes 1–3 outputs to the spine. CASA signals sourced from Node 1
    (crx_rl_depart_casa_signals) at spell grain, broadcast to obs-date rows.

    Coalesce defaults applied here (not in upstream nodes to preserve NULL
    semantics for diagnostic purposes):
        travel_mcc_flag_h2   → 0 on NULL (no H2 debits)
        foreign_login_flag   → 0 on NULL (no login history)

    Args:
        crx_rl_depart_spine:           Node 0 output at (account_id, observation_date).
        crx_rl_depart_travel_mcc:      Node 2 output — travel_mcc_flag_h2.
        crx_rl_depart_foreign_signals: Node 3 output — last_txn_foreign_flag,
                                       foreign_login_flag.
        crx_rl_depart_casa_signals:    Node 1 output at (account_id, spell_id) grain.
                                       Cols: casa_inflow_stop_gap_d, eosb_like_flag,
                                       payroll_present_h2, payroll_stopped_flag.

    Returns:
        crx_rl_departure_signature at (account_id, observation_date) grain::

            account_id              string
            observation_date        date
            spell_id                int
            travel_mcc_flag_h2      int     0/1 (coalesced, no NULL)
            last_txn_foreign_flag   int     0/1
            foreign_login_flag      int     0/1 (coalesced, no NULL)
            casa_inflow_stop_gap_d  double  NULL if no salary inflow in [M0-24m, M0)
            eosb_like_flag          int     0/1/NULL
            payroll_present_h2      int     0/1/NULL
            payroll_stopped_flag    int     0/1/NULL
    """
    spine = crx_rl_depart_spine.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
    )

    # CASA signals are at (account_id, spell_id) grain — broadcast to obs-date rows
    _casa_cols = {c.lower() for c in crx_rl_depart_casa_signals.columns}
    _expected = {
        "casa_inflow_stop_gap_d",
        "eosb_like_flag",
        "payroll_present_h2",
        "payroll_stopped_flag",
    }
    _missing_casa = _expected - _casa_cols
    if _missing_casa:
        LOG.warning(
            "build_rl_departure_final: crx_rl_depart_casa_signals missing %s "
            "— emitting NULL for missing cols.",
            _missing_casa,
        )

    casa_src = crx_rl_depart_casa_signals.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        (
            F.col("casa_inflow_stop_gap_d").cast("double")
            if "casa_inflow_stop_gap_d" in _casa_cols
            else F.lit(None).cast("double").alias("casa_inflow_stop_gap_d")
        ),
        (
            F.col("eosb_like_flag").cast("int")
            if "eosb_like_flag" in _casa_cols
            else F.lit(None).cast("int").alias("eosb_like_flag")
        ),
        (
            F.col("payroll_present_h2").cast("int")
            if "payroll_present_h2" in _casa_cols
            else F.lit(None).cast("int").alias("payroll_present_h2")
        ),
        (
            F.col("payroll_stopped_flag").cast("int")
            if "payroll_stopped_flag" in _casa_cols
            else F.lit(None).cast("int").alias("payroll_stopped_flag")
        ),
    )

    result = (
        spine.join(
            crx_rl_depart_travel_mcc.select(
                "account_id", "observation_date", "travel_mcc_flag_h2"
            ),
            on=["account_id", "observation_date"],
            how="left",
        )
        .join(
            crx_rl_depart_foreign_signals.select(
                "account_id",
                "observation_date",
                "last_txn_foreign_flag",
                "foreign_login_flag",
            ),
            on=["account_id", "observation_date"],
            how="left",
        )
        .join(
            casa_src,
            on=["account_id", "spell_id"],
            how="left",
        )
    )

    # Apply coalesce defaults
    result = result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.coalesce(F.col("travel_mcc_flag_h2"), F.lit(0))
        .cast("int")
        .alias("travel_mcc_flag_h2"),
        F.coalesce(F.col("last_txn_foreign_flag"), F.lit(0))
        .cast("int")
        .alias("last_txn_foreign_flag"),
        F.coalesce(F.col("foreign_login_flag"), F.lit(0))
        .cast("int")
        .alias("foreign_login_flag"),
        F.col("casa_inflow_stop_gap_d").cast("double"),
        F.col("eosb_like_flag").cast("int"),
        F.col("payroll_present_h2").cast("int"),
        F.col("payroll_stopped_flag").cast("int"),
    )

    n_rows = result.count()
    n_travel = result.filter(F.col("travel_mcc_flag_h2") == 1).count()
    n_foreign_login = result.filter(F.col("foreign_login_flag") == 1).count()
    n_casa = result.filter(F.col("casa_inflow_stop_gap_d").isNotNull()).count()
    n_payroll_stopped = result.filter(F.col("payroll_stopped_flag") == 1).count()
    LOG.info(
        "build_rl_departure_final: %d rows | travel_mcc_flag_h2=1: %d (%.1f%%) | "
        "foreign_login_flag=1: %d (%.1f%%) | casa_inflow_stop_gap_d non-null: %d (%.1f%%) | "
        "payroll_stopped_flag=1: %d (%.1f%%)",
        n_rows,
        n_travel,
        100.0 * n_travel / max(n_rows, 1),
        n_foreign_login,
        100.0 * n_foreign_login / max(n_rows, 1),
        n_casa,
        100.0 * n_casa / max(n_rows, 1),
        n_payroll_stopped,
        100.0 * n_payroll_stopped / max(n_rows, 1),
    )

    return result
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_departure_signature/pipeline.py`
action: delete · base sha256 `e2c56683ab98b591a856fcbd0f2d98de2e25e1e49f54ade9baac057e05e1c35e` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A2-2 — RL Departure Signature (standalone, no A4 dependency).

# pylint: disable=line-too-long

5-node pipeline that derives all departure-trail signals for RL accounts.
Runs BEFORE rl_a1_ability; Node 5 (build_rl_a1_classify) depends on
crx_rl_departure_signature for eosb_like_flag.

    build_rl_depart_spine            → crx_rl_depart_spine            [Node 0]
    build_rl_depart_casa_signals     → crx_rl_depart_casa_signals     [Node 1]
    build_rl_depart_travel_mcc       → crx_rl_depart_travel_mcc       [Node 2]
    build_rl_depart_foreign_signals  → crx_rl_depart_foreign_signals  [Node 3]
    build_rl_departure_final         → crx_rl_departure_signature     [Node 4]

Node 0: spell-scoped spine — mirrors build_rl_a4_spine_projection steps 1–4
    without the A4 label join. Produces (cif_id, account_id, observation_date,
    spell_id, t0) at obs-date grain scoped to persona window.

Node 1: CASA salary inflow stop (Pass B) + payroll stop (Pass I).
    R20 CIF scope applied before date filter.
    Same logic as former rl_a4_class Node 1 (build_rl_a4_casa_signals).

Node 2: comp_financial_tran_repos_dly.merchant_category → travel_mcc_flag_h2.
    MCC list + keyword regex imported from cc_departure_signature.nodes.

Node 3: feat_fx_leakage → last_txn_foreign_flag.
        prm_digital_login_monthly → foreign_login_flag (PIT per observation_date).

Node 4: assembles all 4 signal groups into crx_rl_departure_signature.
    CASA signals sourced from Node 1 (no A4 dependency).

Run with:
    kedro run --pipeline=crx_rl_departure_signature
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_depart_casa_signals,
    build_rl_depart_foreign_signals,
    build_rl_depart_spine,
    build_rl_depart_travel_mcc,
    build_rl_departure_final,
)

_TAGS = ["crx", "rl_departure_signature", "rl_a2"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 5-node RL departure signature pipeline."""
    return Pipeline(
        [
            # ── Node 0: spell-scoped spine (no A4 dependency) ───────────────
            node(
                func=build_rl_depart_spine,
                inputs=[
                    "rl_spine",
                    "crx_rl_spell_table",
                    "params:crx_persona",
                ],
                outputs="crx_rl_depart_spine",
                name="build_rl_depart_spine",
                tags=_TAGS,
            ),
            # ── Node 1: CASA salary + payroll signals (R20: 2.4B row scope) ─
            node(
                func=build_rl_depart_casa_signals,
                inputs=[
                    "crx_rl_depart_spine",
                    "comp_financial_tran_repos_dly",
                    "feat_payroll_indicator",
                    "params:crx_persona",
                ],
                outputs="crx_rl_depart_casa_signals",
                name="build_rl_depart_casa_signals",
                tags=_TAGS,
            ),
            # ── Node 2: travel MCC from CASA debit transactions ─────────────
            node(
                func=build_rl_depart_travel_mcc,
                inputs=[
                    "crx_rl_depart_spine",
                    "comp_financial_tran_repos_dly",
                ],
                outputs="crx_rl_depart_travel_mcc",
                name="build_rl_depart_travel_mcc",
                tags=_TAGS,
            ),
            # ── Node 3: FX leakage + digital login foreign flag ─────────────
            node(
                func=build_rl_depart_foreign_signals,
                inputs=[
                    "crx_rl_depart_spine",
                    "feat_fx_leakage",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_rl_depart_foreign_signals",
                name="build_rl_depart_foreign_signals",
                tags=_TAGS,
            ),
            # ── Node 4: assemble final departure signature ──────────────────
            node(
                func=build_rl_departure_final,
                inputs=[
                    "crx_rl_depart_spine",
                    "crx_rl_depart_travel_mcc",
                    "crx_rl_depart_foreign_signals",
                    "crx_rl_depart_casa_signals",
                ],
                outputs="crx_rl_departure_signature",
                name="build_rl_departure_final",
                tags=_TAGS,
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
Clean up after mirror bundle 15_refactor_dead_code.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the catalog path pattern `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`. Skip any folder that does not exist.
  - The check output, for `rl_60_180`: `crx_rl_a4_spine_ra_check`.
  - The removed CC datasets, for `cc_60_180` and `cc_180_plus`: `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_cc_departure_signature`, `crx_cc_departure_spell_base`, `crx_cc_departure_contract_cif`, `crx_cc_departure_pass_a`, `_b`, `_c`, `_d`, `_e`, `_f`, `_g`, `_h`, `_h2`, `_i`, `_j`, `_k`.
  - The removed RL datasets, for `rl_60_180` and `rl_180_plus`: `crx_rl_departure_signature`, `crx_rl_depart_travel_mcc`, `crx_rl_depart_foreign_signals`.
- **Remove the temporary check** (everything marked TEMPORARY for refactor bundle R-A):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_rl_a4_spine_ra_check` entry and its comments;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_rl_a4_spine_ra_check` entry and its comment;
  - `crx_persona/rl_a4_spine/pipeline.py`: `create_ra_check_pipeline`, the `ra_check` import and the TEMPORARY docstring paragraph (keep `_spine_node`);
  - `crx_persona/rl_a4_spine/__init__.py`: `create_ra_check_pipeline`;
  - delete `crx_persona/rl_a4_spine/ra_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "ra_check" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
