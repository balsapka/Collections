# Mirror bundle 06 — A2 — locatability rebuild on one engine (location features, debit-card evidence, reachability, deceased)

apply_bundle version: 6 · built 2026-10-28 from `00de82d..accade8` · source: 14 added, 13 replaced, 3 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/06_a2_locatability_refactor.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '06_a2_locatability_refactor.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/06_a2_locatability_refactor.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A2: locatability on the shared engine (login fixes, card + DCORE primaries, location feature) + temporary b06 check" && git push
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/06_a2_locatability_refactor.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Run everything twice: first for **`cc_60_180`** (the default in
`conf/dev/globals_dev.yml`), then for **`rl_60_180`** (set `model_id: rl_60_180`, persona
dates unchanged). Switch it back to `cc_60_180` when you are done. Steps 6–8 per model_id.

**Step 6.** Rebuild the logins with the fixes, then the CASA primaries (return events +
the new debit-card table; the card table scans 36 months of the raw table, so expect a
long run):

```bash
kedro run --env=dev --pipeline=digital_login
```

```bash
kedro run --env=dev --pipeline=casa_primary
```

**Step 7.** Run the check pipeline (observation base, `location_features`, the new A2
into the temporary `crx_<p>_a2_locatability_b06_check`, then the comparison). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check
```

It reads the old A2's existing output `crx_<p>_a2_locatability`. If it stops with
`PATH_NOT_FOUND` on that dataset (or on `prm_transaction` / `prm_contract` / `prm_client`
for RL), send the error back.

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: `OUTPUT`,
`RULES`, `DEBIT` (and `PRODUCT` for RL). Aggregates only. Text is best; otherwise one
photo per block.

**Step 8.** Only after the B06 blocks have been reviewed: write the real output (it
replaces the old A2's output at the same path).

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The A2 locatability rebuild (spec `A2_locatability_spec.md`, §11):
one engine shared by CC and RL on the observation base, fed by new primary and feature
datasets, plus a temporary check against the old A2.

- **Login fixes** (`digital_login`, shared with the DE code): a login without any country
  is no longer foreign (`is_foreign_login` NULL, O53); rows without a `sessionid` are no
  longer collapsed into one (O54). `prm_digital_login_monthly` keeps its grain and columns
  and adds `last_uae_login_date`, `last_foreign_login_date`, `unknown_country_login_cnt`; a
  same-day tie takes the foreign login (O55, O56).
- **New primary `prm_casa_card_transactions`** (pipeline `casa_primary`, beside
  `prm_casa_return_events`): debit-card rows of `comp_financial_tran_repos_dly` that can
  place a customer, all CIFs, 36 months — in-person POS (`merchant_type_desc` Machine /
  Offline), ATM withdrawals, and travel purchases on any POS type. `place_country` =
  `merchant_country` (POS) or the narration's country code, else
  `counter_party_bank_cntry` (ATM). Debits only, dedup on the key, CIF 13339117 dropped
  (the A2 v03 rule, D-A2-19).
- **New pipeline `location_features`**: `prm_dcore_account_agreements` (account → DCORE
  agreement from `dcore_observation_spine`, no dates) and `feat_cif_location_monthly`
  (per CIF and month: latest UAE / foreign evidence + source, latest travel purchase) from
  logins, debit cards (reason and remote-MCC lists applied), credit cards (`prm_transaction`
  purchase / cash debits, C2 categories, `is_international`) and DCORE departure notes.
- **New engine `crx_persona/a2_locatability/`**: location L1–L4 (latest evidence wins,
  travel rule GAP 3 m / SILENCE 1 m, In Country within W), reachability (gone dark = last
  3 call days all failed, oldest in W, no contact since; Reachable = contact in W; DCORE
  vocabulary per D-A2-17 in `codes.py`), deceased (DCORE, Way4 `block_code_2 = D` on the
  latest snapshot of any card, demographics). Output `crx_<p>_a2_locatability`: `a2_state`
  (`deceased` or `<location>__<reachability>`), `a2_state_label`, both dimensions,
  `deceased_flag` / `deceased_source` and diagnostics. RL reads Way4 too.
- **Old A2 retired**: `cc_a2_locatability/` and `rl_a2_locatability/` become thin wrappers
  (same pipeline and output names); their `nodes.py` / `constants.py` and the
  `crx_*_a2_base` / `_login_presence` / `_contact_signals` catalog entries are deleted. The
  departure signatures stay until the A1 finish bundle (the A1 waterfall / v1 read them).
- **Check** (`a2_locatability/b06_check.py`, pipelines `crx_cc_a2_locatability_b06_check`,
  `crx_rl_a2_locatability_b06_check`): old vs new crosstabs, rules and sources, debit rows by
  month / type / place, RL by product. Removed by the cleanup prompt.
- Expect a large move on CC Skip: the old A2 counted every Way4 `DOMESTIC=N` row (online
  included) as a departure trail (O59). That is a correction.

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
| replace | `conf/base/catalog/catalog_casa.yml` |
| replace | `conf/base/catalog/catalog_crx.yml` |
| add | `conf/base/catalog/catalog_location.yml` |
| replace | `conf/base/parameters/parameters_casa.yml` |
| replace | `conf/base/parameters/parameters_crx_persona.yml` |
| add | `conf/base/parameters/parameters_location.yml` |
| add | `src/enbd_collections/nodes/features/location/__init__.py` |
| add | `src/enbd_collections/nodes/features/location/feat_cif_location_monthly.py` |
| replace | `src/enbd_collections/nodes/primary/casa/prm_casa.py` |
| add | `src/enbd_collections/nodes/primary/dcore/prm_dcore_account_agreements.py` |
| replace | `src/enbd_collections/nodes/primary/digital_login/prm_digital_login_monthly.py` |
| replace | `src/enbd_collections/nodes/staging/digital_login/stg_digital_login.py` |
| add | `src/enbd_collections/nodes/utils/location.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/casa/primary.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/b06_check.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/classify.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/codes.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/pipeline.py` |
| add | `src/enbd_collections/pipelines/location/__init__.py` |
| add | `src/enbd_collections/pipelines/location/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/constants.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/nodes.py` |

## Files

### FILE: `conf/base/catalog/catalog_casa.yml`
action: replace · base sha256 `569f563c2264e199ae168b0a6c114cda9e35d2756a0384a00ad6ef1a28a6f59a` · base trailing newline: yes · new sha256 `793f44194b792ee616b6e8c08a1b4d5569f9953797f35d419f24ac2de76b00a5` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# CASA primary datasets (pipeline casa_primary).

# Returned CASA transactions, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
prm_casa_return_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/return_events"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
  metadata:
    kedro-viz:
      layer: primary
`````

New:

`````yaml
# CASA primary datasets (pipeline casa_primary).

# Returned CASA transactions, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
prm_casa_return_events:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/return_events"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
  metadata:
    kedro-viz:
      layer: primary

# Debit-card rows that can place a customer (in-person POS / ATM withdrawals, travel
# purchases), all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
prm_casa_card_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/card_transactions"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
  metadata:
    kedro-viz:
      layer: primary
`````

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `e93ab51de9b47ecfdac5eb4d3ecfa64d926652586b377b326b2d9d5b63d003a5` · base trailing newline: yes · new sha256 `ad9111e889da9fccfd8fcc4de6213de908b5a1b7e8aec566bb28cfd503dd22b0` · new trailing newline: yes

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

### FILE: `conf/base/catalog/catalog_location.yml`
action: add · new sha256 `9921487fce8230bdd0d45db01d0f9513228b8f5fa1b6eb9ec6547abbe15ff53a` · new trailing newline: yes

New:

`````yaml
# Location inputs of the A2 axis (pipeline location_features).

# Account → DCORE agreement map of the model's collections scope (no dates).
prm_dcore_account_agreements:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/dcore/account_agreements"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Location evidence per (cif_id, month_end): latest UAE / foreign evidence + source,
# latest travel purchase.
feat_cif_location_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/location/cif_location_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

### FILE: `conf/base/parameters/parameters_casa.yml`
action: replace · base sha256 `41f42367cddc858416be2b67d71a632c223b41f362d491e1ddb50813bfc6418f` · base trailing newline: yes · new sha256 `0e8b22cb28ff17b35a7f96a12b230c45a0db0197a27fd6e9a8c50a084b3172bc` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
##################################################
# CASA PRIMARY
##################################################
casa_primary:
  # reason_for_excluding values kept in prm_casa_return_events (all return types;
  # which ones count as distress is decided in the persona signal layer).
  return_reasons: ["CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS"]
  # Calendar months kept up to and including the persona start month
  # (crx_persona.persona_start_date), so the first observation month has its full
  # distress window (the longest: 6 months at 180+).
  history_months: 6
`````

New:

`````yaml
##################################################
# CASA PRIMARY
##################################################
casa_primary:
  # reason_for_excluding values kept in prm_casa_return_events (all return types;
  # which ones count as distress is decided in the persona signal layer).
  return_reasons: ["CHEQUE RETURNS", "DDS Rejects/Reversal", "RETURNS"]
  # Calendar months kept up to and including the persona start month
  # (crx_persona.persona_start_date), so the first observation month has its full
  # distress window (the longest: 6 months at 180+).
  history_months: 6
  # Calendar months of debit-card rows kept in prm_casa_card_transactions up to and
  # including the persona start month (location evidence has no age limit; the raw
  # table holds about three years).
  card_history_months: 36
`````

### FILE: `conf/base/parameters/parameters_crx_persona.yml`
action: replace · base sha256 `f22f8e063a3b9f4f4439511a2c30bca55d3a3f7c9df194071e39e76eb1cc14f2` · base trailing newline: yes · new sha256 `92772344b683a55758af6dd4779d9b0358d7464d489f85ed1b701c308598474f` · new trailing newline: yes

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

# Segment id of the running model variant (cc_60_180 / cc_180_plus / rl_60_180 /
# rl_180_plus): selects the axes' window length (_common.window_months).
model_id: "${globals:model_id}"

`````

### FILE: `conf/base/parameters/parameters_location.yml`
action: add · new sha256 `566b2e30f18bc6470aef70f3d66bbea47c504371f1c1daa4ca8ec5c2a27896c6` · new trailing newline: yes

New:

`````yaml
##################################################
# LOCATION FEATURES (pipeline location_features)
##################################################
location_features:
  # Calendar months of login, credit-card and DCORE evidence read up to and including
  # the persona start month (prm_casa_card_transactions keeps its own history).
  history_months: 36
`````

### FILE: `src/enbd_collections/nodes/features/location/__init__.py`
action: add · new sha256 `146d82248c1ac91195496d034c84a65dc2289f1ad26503963f3a33ecdc832030` · new trailing newline: yes

New:

`````python
"""Customer-level location features."""
`````

### FILE: `src/enbd_collections/nodes/features/location/feat_cif_location_monthly.py`
action: add · new sha256 `41e33bdc738dbd65a65992f725102a1d6ad1d3c871f91c3042bf68b0ea43b598` · new trailing newline: yes

New:

`````python
"""Feature node: location evidence per customer and month.

One row per ``(cif_id, month_end)`` with any evidence, from the primary datasets only:

* ``last_uae_date`` / ``last_uae_source`` — the month's latest evidence that the customer
  was in the UAE: a login from the UAE, in-person card use in the UAE that is not a travel
  purchase;
* ``last_foreign_date`` / ``last_foreign_source`` — the month's latest evidence of being
  abroad: a login from abroad, in-person card use abroad, a collector's departure note;
* ``last_travel_date`` — the month's latest travel purchase (any channel).

Sources: ``login`` (``prm_digital_login_monthly``), ``debit_card``
(``prm_casa_card_transactions``), ``credit_card`` (``prm_transaction``, the model's scoped
cards) and ``dcore_note`` (``dcore_prm_followup_outcomes``). All of a customer's cards and
accounts count. Evidence is dated by day; on a same-day tie between sources the source
name decides, so reruns agree. Online purchases, transfers, incoming money and logins
without a country are not evidence.
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.primary.casa.prm_casa import ATM, IN_PERSON_POS_TYPES, POS
from enbd_collections.nodes.utils.location import is_travel, is_uae

# Debit rows with these reasons are not customer card use (fees, reversals, refunds,
# returns, deleted rows); NULL, '' and 'NA' mean no reason.
_EXCLUDED_REASONS = (
    "CHARGES",
    "FEES",
    "REVERSAL",
    "CANCELLED",
    "RETURNS",
    "CHEQUE RETURNS",
    "DDS Rejects/Reversal",
    "Status Deleted in Finacle",
)
# Merchants paid remotely (digital goods, telecom, direct marketing, software): never in
# person, whatever the terminal type says.
_REMOTE_MCCS = (*range(5815, 5819), 4814, 4816, 4899, *range(5964, 5970), 5734, 7372)
# Credit cards carry no card-present field: in person = cash advances and merchants paid
# at the counter — grocery, fuel, restaurants, pharmacy, transport, department /
# convenience stores.
_IN_PERSON_CREDIT_MCCS = (
    5411, 5422, 5441, 5451, 5462, 5499,
    5541, 5542,
    5812, 5813, 5814,
    5912,
    4111, 4121, 4131,
    5311, 5331,
)  # fmt: skip
_CREDIT_SPEND = ("purchase", "cash")
_DEPARTURE_RESULT_NAMES = (
    "KSA/NATHEER-CROSSING FINAL EXIT VISA",
    "LEFT THE COUNTRY",
    "OUT OF COUNTRY",
)
_EVENT_COLUMNS = ["cif_id", "event_date", "kind", "source"]


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def _events(cif: Column, day: Column, kind: Column, source: str) -> list[Column]:
    return [
        cif.cast("string").alias("cif_id"),
        day.cast("date").alias("event_date"),
        kind.alias("kind"),
        F.lit(source).alias("source"),
    ]


def _login_events(logins: DataFrame, floor: date) -> DataFrame:
    _require(
        logins,
        ["cif_id", "last_uae_login_date", "last_foreign_login_date"],
        "prm_digital_login_monthly",
    )
    uae = logins.select(
        *_events(F.col("cif_id"), F.col("last_uae_login_date"), F.lit("uae"), "login")
    )
    foreign = logins.select(
        *_events(
            F.col("cif_id"), F.col("last_foreign_login_date"), F.lit("foreign"), "login"
        )
    )
    return uae.unionByName(foreign).filter(F.col("event_date") >= F.lit(floor))


def _debit_events(cards: DataFrame) -> DataFrame:
    _require(
        cards,
        [
            "cif_id",
            "tran_date",
            "value_date",
            "channel_desc",
            "merchant_type_desc",
            "reason_for_excluding",
            "merchant_category",
            "merchant_name",
            "tran_narration_1",
            "place_country",
        ],
        "prm_casa_card_transactions",
    )
    channel = F.col("channel_desc")
    remote = F.coalesce(
        F.col("merchant_category").cast("int").isin(*_REMOTE_MCCS), F.lit(False)
    )
    in_person = (
        (channel == POS)
        & F.col("merchant_type_desc").isin(*IN_PERSON_POS_TYPES)
        & ~remote
    ) | (channel == ATM)
    travel = (channel == POS) & is_travel(
        F.col("merchant_category"), F.col("merchant_name"), F.col("tran_narration_1")
    )
    uae = is_uae(F.col("place_country"))
    rows = cards.filter(
        ~F.coalesce(F.trim("reason_for_excluding"), F.lit("")).isin(*_EXCLUDED_REASONS)
    )
    day = F.coalesce(F.col("value_date"), F.col("tran_date"))
    place = F.when(in_person & ~uae, "foreign").when(in_person & uae & ~travel, "uae")
    return rows.select(*_events(F.col("cif_id"), day, place, "debit_card")).unionByName(
        rows.filter(travel).select(
            *_events(F.col("cif_id"), day, F.lit("travel"), "debit_card")
        )
    )


def _credit_events(
    transactions: DataFrame, contracts: DataFrame, clients: DataFrame, floor: date
) -> DataFrame:
    _require(
        transactions,
        [
            "contract_id",
            "observation_date",
            "direction",
            "txn_category",
            "merchant_category_code",
            "is_international",
            "txn_description",
        ],
        "prm_transaction",
    )
    _require(contracts, ["contract_id", "client_id"], "prm_contract")
    _require(clients, ["client_id", "cif_id"], "prm_client")
    cif_of_contract = (
        contracts.select(F.col("contract_id").cast("string"), "client_id")
        .distinct()
        .join(clients.select("client_id", "cif_id").distinct(), on="client_id")
        .select("contract_id", "cif_id")
    )
    category = F.col("txn_category")
    mcc = F.col("merchant_category_code")
    in_person = (category == "cash") | F.coalesce(
        mcc.cast("int").isin(*_IN_PERSON_CREDIT_MCCS), F.lit(False)
    )
    travel = (category == "purchase") & is_travel(mcc, F.col("txn_description"))
    abroad = F.col("is_international") == 1
    place = F.when(in_person & abroad, "foreign").when(
        in_person & ~abroad & ~travel, "uae"
    )
    rows = (
        transactions.filter(
            (F.col("direction") == -1)
            & category.isin(*_CREDIT_SPEND)
            & (F.col("observation_date") >= F.lit(floor))
        )
        .withColumn("contract_id", F.col("contract_id").cast("string"))
        .join(cif_of_contract, on="contract_id")
    )
    day = F.col("observation_date")
    return rows.select(
        *_events(F.col("cif_id"), day, place, "credit_card")
    ).unionByName(
        rows.filter(travel).select(
            *_events(F.col("cif_id"), day, F.lit("travel"), "credit_card")
        )
    )


def _departure_notes(
    followup: DataFrame, agreements: DataFrame, floor: date
) -> DataFrame:
    _require(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    _require(agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements")
    notes = followup.filter(
        F.upper(F.trim("result_name")).isin(*_DEPARTURE_RESULT_NAMES)
        & (F.to_date("action_ts") >= F.lit(floor))
    ).select(F.col("agreement_id").cast("string"), "action_ts")
    return notes.join(
        agreements.select("agreement_id", "cif_id").distinct(), on="agreement_id"
    ).select(
        *_events(
            F.col("cif_id"), F.to_date("action_ts"), F.lit("foreign"), "dcore_note"
        )
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    logins: DataFrame,
    casa_cards: DataFrame,
    transactions: DataFrame,
    contracts: DataFrame,
    clients: DataFrame,
    followup: DataFrame,
    agreements: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Location evidence per ``(cif_id, month_end)`` from the first day of the last
    ``history_months`` months up to the persona start month (``prm_casa_card_transactions``
    keeps its own history)."""
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
    events = (
        _login_events(logins, floor)
        .unionByName(_debit_events(casa_cards))
        .unionByName(_credit_events(transactions, contracts, clients, floor))
        .unionByName(_departure_notes(followup, agreements, floor))
        .select(*_EVENT_COLUMNS)
        .filter(
            F.col("cif_id").isNotNull()
            & F.col("event_date").isNotNull()
            & F.col("kind").isNotNull()
        )
    )

    def latest(kind: str) -> Column:
        return F.max(F.when(F.col("kind") == kind, F.struct("event_date", "source")))

    return (
        events.groupBy("cif_id", F.last_day("event_date").alias("month_end"))
        .agg(
            latest("uae").alias("_uae"),
            latest("foreign").alias("_foreign"),
            F.max(F.when(F.col("kind") == "travel", F.col("event_date"))).alias(
                "last_travel_date"
            ),
        )
        .select(
            "cif_id",
            "month_end",
            F.col("_uae.event_date").alias("last_uae_date"),
            F.col("_uae.source").alias("last_uae_source"),
            F.col("_foreign.event_date").alias("last_foreign_date"),
            F.col("_foreign.source").alias("last_foreign_source"),
            "last_travel_date",
        )
    )
`````

### FILE: `src/enbd_collections/nodes/primary/casa/prm_casa.py`
action: replace · base sha256 `b5a210a9ffbd9087ed1dbbb0c49c57eef619fe5a8e63d9c8d5d71f334ed869f0` · base trailing newline: yes · new sha256 `b03c9c7d584c1e5b9b85b4ba6ffd4141f3882cbab4b935a2ece8e66655b198df` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from datetime import date
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


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def build_return_events(
    tran_repos: DataFrame,
    return_reasons: Sequence[str],
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Returned CASA transactions (every ``return_reasons`` value, both debit and credit
    legs) for all CIFs, one row per transaction key, partitioned by ``event_month``.

    Covers the last ``history_months`` calendar months up to and including the persona
    start month, and everything after it; each run rebuilds the whole table. A reload of
    the same transaction in a later ``edp_load_date`` keeps the latest load.
    """
    missing = sorted(set(_RETURN_EVENT_COLUMNS) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
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

New:

`````python
"""Primary CASA datasets built from comp_financial_tran_repos_dly."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_travel

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
_CARD_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "value_date",
    "edp_load_date",
    "tran_dc",
    "channel_desc",
    "merchant_type_desc",
    "tran_particular_code_desc",
    "reason_for_excluding",
    "merchant_category",
    "merchant_name",
    "merchant_country",
    "counter_party_bank_cntry",
    "tran_narration_1",
    "actual_tran_amt_aed",
]

POS, ATM = "Point of Sale", "ATM Transactions"
# Card-present POS rows (Offline until ~2025-08, Machine since); Online = e-commerce.
IN_PERSON_POS_TYPES = ("Machine", "Offline")
# ATM cash withdrawals; the other ATM rows are fees, balance enquiries and mePay.
_ATM_WITHDRAWAL_CODES = ("DR ATM TRANSACTION", "UAE SWITCH WDL")
# The NI POS settlement sink: not a customer (millions of POS rows a month).
_NON_CUSTOMER_CIFS = ("13339117",)


def _months_back(day: date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _scoped(
    tran_repos: DataFrame,
    columns: Sequence[str],
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``columns`` of the rows loaded and dated from the first day of the last
    ``history_months`` months up to the persona start month."""
    missing = sorted(set(columns) - set(tran_repos.columns))
    if missing:
        raise ValueError(f"comp_financial_tran_repos_dly is missing columns: {missing}")
    floor = _months_back(
        date.fromisoformat(str(persona_start_date)), history_months - 1
    )
    return tran_repos.filter(
        (F.col("edp_load_date") >= F.lit(floor)) & (F.col("tran_date") >= F.lit(floor))
    ).select(*columns)


def _latest_load(df: DataFrame) -> DataFrame:
    """One row per transaction key (the latest ``edp_load_date``), partitioned by
    ``event_month`` (the month of ``tran_date``)."""
    latest_load = Window.partitionBy(*_KEY).orderBy(F.col("edp_load_date").desc())
    return (
        df.withColumn("_rn", F.row_number().over(latest_load))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
        .withColumn(
            "event_month", F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd")
        )
    )


def build_return_events(
    tran_repos: DataFrame,
    return_reasons: Sequence[str],
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Returned CASA transactions (every ``return_reasons`` value, both debit and credit
    legs) for all CIFs, one row per transaction key, partitioned by ``event_month``.

    Covers the last ``history_months`` calendar months up to and including the persona
    start month, and everything after it; each run rebuilds the whole table. A reload of
    the same transaction in a later ``edp_load_date`` keeps the latest load.
    """
    rows = _scoped(
        tran_repos, _RETURN_EVENT_COLUMNS, persona_start_date, history_months
    )
    return _latest_load(
        rows.filter(F.col("reason_for_excluding").isin(*return_reasons))
    )


def _narration_country() -> Column:
    """The two-letter country code an ATM narration ends with (``…:AE#`` or ``… AE``)."""
    narration = F.upper(F.trim(F.col("tran_narration_1")))
    tagged = F.regexp_extract(narration, r":([A-Z]{2})#", 1)
    trailing = F.regexp_extract(narration, r"\s([A-Z]{2})$", 1)
    return F.when(tagged != "", tagged).when(trailing != "", trailing)


def build_card_transactions(
    tran_repos: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """Debit-card rows that can place a customer, for all CIFs, one row per transaction
    key, partitioned by ``event_month``:

    * in-person candidates — POS debits of a card-present type (``merchant_type_desc``
      Machine / Offline) and ATM cash withdrawals;
    * travel purchases — POS debits with a travel MCC or travel keyword, any type
      (online bookings included).

    ``place_country`` is where the row happened: ``merchant_country`` for POS; for ATM
    the narration's country code, else ``counter_party_bank_cntry``. ``place_source``
    names the column used. Which rows count as evidence (reasons, remote MCCs, UAE or
    abroad) is decided downstream; values are kept as they are. Same history and reload
    rule as ``build_return_events``; the NI POS sink CIF is dropped.
    """
    rows = _scoped(tran_repos, _CARD_COLUMNS, persona_start_date, history_months)
    channel = F.col("channel_desc")
    in_person = (
        (channel == POS) & F.col("merchant_type_desc").isin(*IN_PERSON_POS_TYPES)
    ) | (
        (channel == ATM)
        & F.col("tran_particular_code_desc").isin(*_ATM_WITHDRAWAL_CODES)
    )
    travel = is_travel(
        F.col("merchant_category"), F.col("merchant_name"), F.col("tran_narration_1")
    )
    cards = rows.filter(
        (F.col("tran_dc") == "D")
        & (in_person | ((channel == POS) & travel))
        & ~F.col("cif_id").cast("string").isin(*_NON_CUSTOMER_CIFS)
    )
    code = _narration_country()
    bank = F.col("counter_party_bank_cntry")
    return _latest_load(cards).select(
        "*",
        F.when(channel == POS, F.col("merchant_country"))
        .otherwise(F.coalesce(code, bank))
        .alias("place_country"),
        F.when(
            (channel == POS) & F.col("merchant_country").isNotNull(), "merchant_country"
        )
        .when((channel == ATM) & code.isNotNull(), "narration")
        .when((channel == ATM) & bank.isNotNull(), "counter_party_bank")
        .alias("place_source"),
    )
`````

### FILE: `src/enbd_collections/nodes/primary/dcore/prm_dcore_account_agreements.py`
action: add · new sha256 `1f564b366f06919ac4cd4a445f27bc7b9e7f8ccb24119d800ac1911b3c3a2844` · new trailing newline: yes

New:

`````python
"""Primary node: the account → DCORE agreement map of the model's collections scope.

``dcore_observation_spine`` carries the map on the spine's (billing) dates; here the
dates are dropped, so every DCORE event of an agreement can be read up to any
observation date. One agreement per account holds in PROD (A2 v01); the table keeps
whatever pairs the spine has.
"""

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

_COLUMNS = ["account_id", "agreement_id", "cif_id"]


def build(dcore_observation_spine: DataFrame) -> DataFrame:
    """Distinct ``(account_id, agreement_id, cif_id)``, ids as strings."""
    missing = sorted(set(_COLUMNS) - set(dcore_observation_spine.columns))
    if missing:
        raise ValueError(f"dcore_observation_spine is missing columns: {missing}")
    return (
        dcore_observation_spine.select(
            *[F.col(c).cast("string").alias(c) for c in _COLUMNS]
        )
        .filter(F.col("account_id").isNotNull() & F.col("agreement_id").isNotNull())
        .distinct()
    )
`````

### FILE: `src/enbd_collections/nodes/primary/digital_login/prm_digital_login_monthly.py`
action: replace · base sha256 `19396ba080c70c59e7f4b9254a4ef8a21e5edf994d1b2091a1afe0e69b461684` · base trailing newline: yes · new sha256 `393d4aa68dd1a295784c8e97f52a39d22f232f72b27997c7eac1616bf48505b1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Primary node: monthly OMB digital login aggregation.

Aggregates stg_digital_login event-grain to (cif_id × month_number) grain.

month_number: last day of login month in yyyyMMdd format — consistent with
retail.feature_space fea_customer_digital_engagement and fea_monthly_aecb_alerts.

Schema:
    cif_id                  (str)        — bank CIF number
    month_number            (str)        — yyyyMMdd, last day of month
    last_login_date         (date)       — most recent login_date in month
    last_login_foreign_flag (int 0/1)    — is_foreign_login for most recent login
    last_login_country      (str, null)  — countrylocation of most recent login
    last_login_countrycode  (str, null)  — countrycode of most recent login
    any_foreign_login_flag  (int 0/1)    — 1 if any login in month was foreign
    foreign_login_cnt       (int)        — count of foreign logins in month
    total_login_cnt         (int)        — total successful logins in month
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(stg_digital_login: DataFrame) -> DataFrame:
    """Aggregate login events to (cif_id × month_number) grain.

    Args:
        stg_digital_login: Output of stg_digital_login node.
                           Required cols: cif_id, login_date, is_foreign_login,
                           countrylocation, countrycode.

    Returns:
        DataFrame at grain (cif_id, month_number).
    """
    # ── Derive month_number: last day of login month (yyyyMMdd) ──────────────
    df = stg_digital_login.withColumn(
        "month_number",
        F.date_format(F.last_day(F.col("login_date")), "yyyyMMdd"),
    )

    # ── Window for most-recent login per (cif_id, month_number) ──────────────
    w_last = Window.partitionBy("cif_id", "month_number").orderBy(
        F.col("login_date").desc()
    )
    df_ranked = df.withColumn("_rn", F.row_number().over(w_last))

    # Extract last-login attributes (rank 1 row)
    last_login_details = df_ranked.filter(F.col("_rn") == 1).select(
        "cif_id",
        "month_number",
        F.col("login_date").alias("last_login_date"),
        F.col("is_foreign_login").cast("int").alias("last_login_foreign_flag"),
        F.col("countrylocation").cast("string").alias("last_login_country"),
        F.col("countrycode").cast("string").alias("last_login_countrycode"),
    )

    # ── Monthly aggregation ───────────────────────────────────────────────────
    agg = df.groupBy("cif_id", "month_number").agg(
        F.sum(F.col("is_foreign_login").cast("int"))
        .cast("int")
        .alias("foreign_login_cnt"),
        F.count("*").cast("int").alias("total_login_cnt"),
        F.max(F.col("is_foreign_login").cast("int"))
        .cast("int")
        .alias("any_foreign_login_flag"),
    )

    # ── Join last-login details onto aggregation ──────────────────────────────
    result = agg.join(last_login_details, on=["cif_id", "month_number"], how="left")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("month_number").cast("string"),
        F.col("last_login_date").cast("date"),
        F.col("last_login_foreign_flag").cast("int"),
        F.col("last_login_country").cast("string"),
        F.col("last_login_countrycode").cast("string"),
        F.col("any_foreign_login_flag").cast("int"),
        F.col("foreign_login_cnt").cast("int"),
        F.col("total_login_cnt").cast("int"),
    )
`````

New:

`````python
"""Primary node: monthly OMB digital login aggregation.

Aggregates stg_digital_login event-grain to (cif_id × month_number) grain.

month_number: last day of login month in yyyyMMdd format — consistent with
retail.feature_space fea_customer_digital_engagement and fea_monthly_aecb_alerts.

Schema:
    cif_id                     (str)        — bank CIF number
    month_number               (str)        — yyyyMMdd, last day of month
    last_login_date            (date)       — most recent login_date in month
    last_login_foreign_flag    (int 0/1)    — is_foreign_login for most recent login
                                              (NULL: no country)
    last_login_country         (str, null)  — countrylocation of most recent login
    last_login_countrycode     (str, null)  — countrycode of most recent login
    any_foreign_login_flag     (int 0/1)    — 1 if any login in month was foreign
    foreign_login_cnt          (int)        — count of foreign logins in month
    total_login_cnt            (int)        — total successful logins in month
    last_uae_login_date        (date, null) — latest login from the UAE in month
    last_foreign_login_date    (date, null) — latest login from abroad in month
    unknown_country_login_cnt  (int)        — logins in month without a country

Logins are dated by day, so several can share the month's last login day: the most
recent login is then a foreign one if any (foreign evidence wins a same-day tie),
otherwise a UAE one, otherwise one without a country.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(stg_digital_login: DataFrame) -> DataFrame:
    """Aggregate login events to (cif_id × month_number) grain.

    Args:
        stg_digital_login: Output of stg_digital_login node.
                           Required cols: cif_id, login_date, is_foreign_login,
                           countrylocation, countrycode.

    Returns:
        DataFrame at grain (cif_id, month_number).
    """
    df = stg_digital_login.withColumn(
        "month_number",
        F.date_format(F.last_day(F.col("login_date")), "yyyyMMdd"),
    )
    foreign = F.col("is_foreign_login").cast("int")

    # ── Most recent login per (cif_id, month_number); same day: foreign first ─
    w_last = Window.partitionBy("cif_id", "month_number").orderBy(
        F.col("login_date").desc(),
        foreign.desc_nulls_last(),
        F.col("countrylocation").desc_nulls_last(),
        F.col("countrycode").desc_nulls_last(),
    )
    last_login_details = (
        df.withColumn("_rn", F.row_number().over(w_last))
        .filter(F.col("_rn") == 1)
        .select(
            "cif_id",
            "month_number",
            F.col("login_date").alias("last_login_date"),
            foreign.alias("last_login_foreign_flag"),
            F.col("countrylocation").cast("string").alias("last_login_country"),
            F.col("countrycode").cast("string").alias("last_login_countrycode"),
        )
    )

    # ── Monthly aggregation ───────────────────────────────────────────────────
    agg = df.groupBy("cif_id", "month_number").agg(
        F.coalesce(F.sum(foreign), F.lit(0)).cast("int").alias("foreign_login_cnt"),
        F.count("*").cast("int").alias("total_login_cnt"),
        F.coalesce(F.max(foreign), F.lit(0))
        .cast("int")
        .alias("any_foreign_login_flag"),
        F.max(F.when(foreign == 0, F.col("login_date"))).alias("last_uae_login_date"),
        F.max(F.when(foreign == 1, F.col("login_date"))).alias(
            "last_foreign_login_date"
        ),
        F.sum(F.when(foreign.isNull(), 1).otherwise(0))
        .cast("int")
        .alias("unknown_country_login_cnt"),
    )

    result = agg.join(last_login_details, on=["cif_id", "month_number"], how="left")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("month_number").cast("string"),
        F.col("last_login_date").cast("date"),
        F.col("last_login_foreign_flag").cast("int"),
        F.col("last_login_country").cast("string"),
        F.col("last_login_countrycode").cast("string"),
        F.col("any_foreign_login_flag").cast("int"),
        F.col("foreign_login_cnt").cast("int"),
        F.col("total_login_cnt").cast("int"),
        F.col("last_uae_login_date").cast("date"),
        F.col("last_foreign_login_date").cast("date"),
        F.col("unknown_country_login_cnt").cast("int"),
    )
`````

### FILE: `src/enbd_collections/nodes/staging/digital_login/stg_digital_login.py`
action: replace · base sha256 `2f84d3b24d24be706061ee073a2f5a6222e473f17f5b62418862d00f122b690a` · base trailing newline: yes · new sha256 `d048151b5b24c688c84a3ac2520fa52ad1897ef9b0ddf3cebb951c5f8162641e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Staging node: OMB digital login events.

Unions two raw OMB login tables, filters to successful logins, derives is_foreign_login,
and resolves partyid → cif_id via the PDM users table.

Output grain: one row per login session (deduplicated on sessionid — the tables are
partitioned by edp_load_date and the same session can appear in multiple partitions).

Schema:
    cif_id          (str)        — bank CIF number
    login_date      (date)       — date of login
    is_foreign_login (int 0/1)   — 1 if login originated outside UAE
    countrylocation (str, null)  — country name from login record
    countrycode     (str, null)  — ISO country code from login record
    login_interface (str, null)  — login channel (channel column)
"""

import logging
from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(
    raw_digital_login_data: DataFrame,
    raw_digital_login_data_history: DataFrame,
    raw_digital_user_data: DataFrame,
) -> DataFrame:
    """Stage OMB login events: union, dedup, CIF resolve, country flag.

    Args:
        raw_digital_login_data:         Current OMB login table
                                        (CL_OMB_GROUP_REPORTS.LOGIN_DATA_EBI).
                                        Cols used: partyid, status, createdon,
                                        countrylocation, countrycode, channel,
                                        sessionid.
        raw_digital_login_data_history: Historical OMB login table
                                        (tdv_omb_uae_ebi.loginlog).
                                        May lack countrycode — handled via
                                        allowMissingColumns union.
        raw_digital_user_data:          PDM users table (tdv_pdm_uae_ebi.users).
                                        Maps partyid → cif_id.
                                        Cols used: id (= partyid), cif.

    Returns:
        Session-grain DataFrame with stable schema (NULL-padded for missing columns).
    """
    # ── CIF lookup: PDM users id → cif ────────────────────────────────────────
    # 'id' in the users table is the partyid (Firebase ID); 'cif' is the bank CIF.
    # Dedup on (cif_id, _party_id) — matches retail.feature_space convention.
    # raw_digital_user_data is SCD2 (has edp_activeind, edp_effectivestartdate,
    # edp_effectiveenddate). Filter to 'Y' so superseded historical versions of a
    # user record are excluded from the CIF map.
    user_cols_lower = {c.lower() for c in raw_digital_user_data.columns}
    if "id" not in user_cols_lower or "cif" not in user_cols_lower:
        LOG.warning(
            "stg_digital_login: raw_digital_user_data missing 'id' or 'cif' column "
            "— emitting empty staging output"
        )
        return _empty_schema()

    active_users = raw_digital_user_data
    if "edp_activeind" in user_cols_lower:
        active_users = active_users.filter(F.col("edp_activeind") == F.lit("Y"))

    cif_map = (
        active_users.filter(F.col("cif").isNotNull())
        .select(
            F.col("id").cast("string").alias("_party_id"),
            F.col("cif").cast("string").alias("cif_id"),
        )
        .dropDuplicates(["cif_id", "_party_id"])
    )

    # ── Normalise each source to common columns before union ─────────────────
    current = _normalise_source(raw_digital_login_data, source_label="current")
    history = _normalise_source(raw_digital_login_data_history, source_label="history")

    if current is None and history is None:
        LOG.warning("stg_digital_login: both login tables missing required columns")
        return _empty_schema()

    if current is None:
        combined = history
    elif history is None:
        combined = current
    else:
        combined = current.unionByName(history, allowMissingColumns=True)

    # ── Filter to successful logins ───────────────────────────────────────────
    # Include "pre_login" per retail.feature_space convention — partial logins
    # still carry a valid country signal for the departure feature.
    logins = combined.filter(F.lower(F.col("status")).isin(["success", "pre_login"]))

    # ── Dedup on sessionid ────────────────────────────────────────────────────
    # Both tables are partitioned by edp_load_date; the same sessionid can appear
    # in multiple partitions. Drop to one row per session before deriving features.
    if "sessionid" in {c.lower() for c in logins.columns}:
        logins = logins.dropDuplicates(["sessionid"])

    # ── Derive is_foreign_login ───────────────────────────────────────────────
    # UAE match: UPPER(REGEXP_REPLACE(countrylocation, whitespace, '')) = 'UNITEDARABEMIRATES'
    # OR UPPER(countrycode) = 'AE'.  Each guarded by null-check.
    uae_by_name = F.col("countrylocation").isNotNull() & (
        F.upper(F.regexp_replace(F.col("countrylocation"), r"\s+", ""))
        == F.lit("UNITEDARABEMIRATES")
    )
    uae_by_code = F.col("countrycode").isNotNull() & (
        F.upper(F.col("countrycode")) == F.lit("AE")
    )
    uae_cond = uae_by_name | uae_by_code

    logins = logins.withColumn(
        "is_foreign_login",
        F.when(uae_cond, F.lit(0)).otherwise(F.lit(1)).cast("int"),
    )

    # ── Resolve partyid → cif_id via PDM users (inner join drops unresolved) ──
    result = logins.join(cif_map, logins["partyid"] == cif_map["_party_id"], "inner")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("login_date").cast("date"),
        F.col("is_foreign_login").cast("int"),
        F.col("countrylocation").cast("string"),
        F.col("countrycode").cast("string"),
        F.col("login_interface").cast("string"),
    )


# ── Private helpers ───────────────────────────────────────────────────────────


def _normalise_source(df: DataFrame, source_label: str) -> Optional[DataFrame]:
    """Normalise a raw login source to common columns.

    Required: partyid, status, createdon.
    Optional: countrylocation, countrycode, channel, sessionid.
    Returns None if required columns are absent.
    """
    cols_lower = {c.lower() for c in df.columns}
    required = ["partyid", "status", "createdon"]
    missing = [c for c in required if c not in cols_lower]
    if missing:
        LOG.warning(
            "stg_digital_login [%s]: missing required columns %s — skipping source",
            source_label,
            missing,
        )
        return None

    # SCD2 tables carry edp_activeind (Y/N). Filter to active records only so that
    # historical partition rows (edp_activeind='N') are not counted as login events.
    # The current table (raw_digital_login_data) has no edp_activeind — guard prevents
    # errors on that source.
    if "edp_activeind" in cols_lower:
        df = df.filter(F.col("edp_activeind") == F.lit("Y"))

    # createdon is a TIMESTAMP in both tables — to_date() truncates to date directly.
    login_date_expr = F.to_date(F.col("createdon"))

    # Optional columns — emit NULL if absent
    def _opt(col_name: str, dtype: str) -> F.Column:
        return (
            F.col(col_name).cast(dtype)
            if col_name in cols_lower
            else F.lit(None).cast(dtype)
        )

    return df.select(
        F.col("partyid").cast("string").alias("partyid"),
        F.col("status").cast("string").alias("status"),
        login_date_expr.alias("login_date"),
        _opt("countrylocation", "string").alias("countrylocation"),
        _opt("countrycode", "string").alias("countrycode"),
        _opt("channel", "string").alias("login_interface"),
        _opt("sessionid", "string").alias("sessionid"),
    )


def _empty_schema() -> DataFrame:
    """Return an empty DataFrame with the stable output schema.

    Used when required columns are missing to preserve schema contract.
    """
    from pyspark.sql import SparkSession  # pylint: disable=import-outside-toplevel
    from pyspark.sql.types import (  # pylint: disable=import-outside-toplevel
        DateType,
        IntegerType,
        StringType,
        StructField,
        StructType,
    )

    spark = SparkSession.builder.getOrCreate()
    schema = StructType(
        [
            StructField("cif_id", StringType(), True),
            StructField("login_date", DateType(), True),
            StructField("is_foreign_login", IntegerType(), True),
            StructField("countrylocation", StringType(), True),
            StructField("countrycode", StringType(), True),
            StructField("login_interface", StringType(), True),
        ]
    )
    return spark.createDataFrame([], schema)
`````

New:

`````python
"""Staging node: OMB digital login events.

Unions two raw OMB login tables, filters to successful logins, derives is_foreign_login,
and resolves partyid → cif_id via the PDM users table.

Output grain: one row per login session (deduplicated on sessionid — the tables are
partitioned by edp_load_date and the same session can appear in multiple partitions).
Logins without a sessionid are kept one row each.

Schema:
    cif_id          (str)        — bank CIF number
    login_date      (date)       — date of login
    is_foreign_login (int 0/1)   — 1 if login originated outside UAE; NULL when the
                                   login carries no country
    countrylocation (str, null)  — country name from login record
    countrycode     (str, null)  — ISO country code from login record
    login_interface (str, null)  — login channel (channel column)
"""

import logging
from typing import Optional

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


def build(  # pylint: disable=too-many-locals
    raw_digital_login_data: DataFrame,
    raw_digital_login_data_history: DataFrame,
    raw_digital_user_data: DataFrame,
) -> DataFrame:
    """Stage OMB login events: union, dedup, CIF resolve, country flag.

    Args:
        raw_digital_login_data:         Current OMB login table
                                        (CL_OMB_GROUP_REPORTS.LOGIN_DATA_EBI).
                                        Cols used: partyid, status, createdon,
                                        countrylocation, countrycode, channel,
                                        sessionid.
        raw_digital_login_data_history: Historical OMB login table
                                        (tdv_omb_uae_ebi.loginlog).
                                        May lack countrycode — handled via
                                        allowMissingColumns union.
        raw_digital_user_data:          PDM users table (tdv_pdm_uae_ebi.users).
                                        Maps partyid → cif_id.
                                        Cols used: id (= partyid), cif.

    Returns:
        Session-grain DataFrame with stable schema (NULL-padded for missing columns).
    """
    # ── CIF lookup: PDM users id → cif ────────────────────────────────────────
    # 'id' in the users table is the partyid (Firebase ID); 'cif' is the bank CIF.
    # Dedup on (cif_id, _party_id) — matches retail.feature_space convention.
    # raw_digital_user_data is SCD2 (has edp_activeind, edp_effectivestartdate,
    # edp_effectiveenddate). Filter to 'Y' so superseded historical versions of a
    # user record are excluded from the CIF map.
    user_cols_lower = {c.lower() for c in raw_digital_user_data.columns}
    if "id" not in user_cols_lower or "cif" not in user_cols_lower:
        LOG.warning(
            "stg_digital_login: raw_digital_user_data missing 'id' or 'cif' column "
            "— emitting empty staging output"
        )
        return _empty_schema()

    active_users = raw_digital_user_data
    if "edp_activeind" in user_cols_lower:
        active_users = active_users.filter(F.col("edp_activeind") == F.lit("Y"))

    cif_map = (
        active_users.filter(F.col("cif").isNotNull())
        .select(
            F.col("id").cast("string").alias("_party_id"),
            F.col("cif").cast("string").alias("cif_id"),
        )
        .dropDuplicates(["cif_id", "_party_id"])
    )

    # ── Normalise each source to common columns before union ─────────────────
    current = _normalise_source(raw_digital_login_data, source_label="current")
    history = _normalise_source(raw_digital_login_data_history, source_label="history")

    if current is None and history is None:
        LOG.warning("stg_digital_login: both login tables missing required columns")
        return _empty_schema()

    if current is None:
        combined = history
    elif history is None:
        combined = current
    else:
        combined = current.unionByName(history, allowMissingColumns=True)

    # ── Filter to successful logins ───────────────────────────────────────────
    # Include "pre_login" per retail.feature_space convention — partial logins
    # still carry a valid country signal for the departure feature.
    logins = combined.filter(F.lower(F.col("status")).isin(["success", "pre_login"]))

    # ── Dedup on sessionid ────────────────────────────────────────────────────
    # Both tables are partitioned by edp_load_date; the same sessionid can appear
    # in multiple partitions. Drop to one row per session before deriving features.
    # dropDuplicates treats NULLs as equal, so rows without a sessionid bypass it.
    if "sessionid" in {c.lower() for c in logins.columns}:
        has_session = F.col("sessionid").isNotNull()
        logins = (
            logins.filter(has_session)
            .dropDuplicates(["sessionid"])
            .unionByName(logins.filter(~has_session))
        )

    # ── Derive is_foreign_login ───────────────────────────────────────────────
    # UAE match: UPPER(REGEXP_REPLACE(countrylocation, whitespace, '')) = 'UNITEDARABEMIRATES'
    # OR UPPER(countrycode) = 'AE'.  Each guarded by null-check.
    uae_by_name = F.col("countrylocation").isNotNull() & (
        F.upper(F.regexp_replace(F.col("countrylocation"), r"\s+", ""))
        == F.lit("UNITEDARABEMIRATES")
    )
    uae_by_code = F.col("countrycode").isNotNull() & (
        F.upper(F.col("countrycode")) == F.lit("AE")
    )
    uae_cond = uae_by_name | uae_by_code
    # A login without any country is no location evidence: NULL, not foreign.
    has_country = (F.trim(F.coalesce(F.col("countrylocation"), F.lit(""))) != "") | (
        F.trim(F.coalesce(F.col("countrycode"), F.lit(""))) != ""
    )

    logins = logins.withColumn(
        "is_foreign_login",
        F.when(uae_cond, F.lit(0)).when(has_country, F.lit(1)).cast("int"),
    )

    # ── Resolve partyid → cif_id via PDM users (inner join drops unresolved) ──
    result = logins.join(cif_map, logins["partyid"] == cif_map["_party_id"], "inner")

    return result.select(
        F.col("cif_id").cast("string"),
        F.col("login_date").cast("date"),
        F.col("is_foreign_login").cast("int"),
        F.col("countrylocation").cast("string"),
        F.col("countrycode").cast("string"),
        F.col("login_interface").cast("string"),
    )


# ── Private helpers ───────────────────────────────────────────────────────────


def _normalise_source(df: DataFrame, source_label: str) -> Optional[DataFrame]:
    """Normalise a raw login source to common columns.

    Required: partyid, status, createdon.
    Optional: countrylocation, countrycode, channel, sessionid.
    Returns None if required columns are absent.
    """
    cols_lower = {c.lower() for c in df.columns}
    required = ["partyid", "status", "createdon"]
    missing = [c for c in required if c not in cols_lower]
    if missing:
        LOG.warning(
            "stg_digital_login [%s]: missing required columns %s — skipping source",
            source_label,
            missing,
        )
        return None

    # SCD2 tables carry edp_activeind (Y/N). Filter to active records only so that
    # historical partition rows (edp_activeind='N') are not counted as login events.
    # The current table (raw_digital_login_data) has no edp_activeind — guard prevents
    # errors on that source.
    if "edp_activeind" in cols_lower:
        df = df.filter(F.col("edp_activeind") == F.lit("Y"))

    # createdon is a TIMESTAMP in both tables — to_date() truncates to date directly.
    login_date_expr = F.to_date(F.col("createdon"))

    # Optional columns — emit NULL if absent
    def _opt(col_name: str, dtype: str) -> F.Column:
        return (
            F.col(col_name).cast(dtype)
            if col_name in cols_lower
            else F.lit(None).cast(dtype)
        )

    return df.select(
        F.col("partyid").cast("string").alias("partyid"),
        F.col("status").cast("string").alias("status"),
        login_date_expr.alias("login_date"),
        _opt("countrylocation", "string").alias("countrylocation"),
        _opt("countrycode", "string").alias("countrycode"),
        _opt("channel", "string").alias("login_interface"),
        _opt("sessionid", "string").alias("sessionid"),
    )


def _empty_schema() -> DataFrame:
    """Return an empty DataFrame with the stable output schema.

    Used when required columns are missing to preserve schema contract.
    """
    from pyspark.sql import SparkSession  # pylint: disable=import-outside-toplevel
    from pyspark.sql.types import (  # pylint: disable=import-outside-toplevel
        DateType,
        IntegerType,
        StringType,
        StructField,
        StructType,
    )

    spark = SparkSession.builder.getOrCreate()
    schema = StructType(
        [
            StructField("cif_id", StringType(), True),
            StructField("login_date", DateType(), True),
            StructField("is_foreign_login", IntegerType(), True),
            StructField("countrylocation", StringType(), True),
            StructField("countrycode", StringType(), True),
            StructField("login_interface", StringType(), True),
        ]
    )
    return spark.createDataFrame([], schema)
`````

### FILE: `src/enbd_collections/nodes/utils/location.py`
action: add · new sha256 `d9a2ca6d22b8cacc0c26b7b4d19605ec2a57d524b3037c7ff8f44e2c464b4b8f` · new trailing newline: yes

New:

`````python
"""Shared location vocabulary: travel purchases and UAE country spellings.

Used by the CASA card primary (row selection) and the location feature (evidence).
"""

from pyspark.sql import Column
from pyspark.sql import functions as F

# Airlines and air carriers, cruise lines, airlines (generic), travel agencies.
TRAVEL_MCCS = (*range(3000, 3300), 4411, 4511, 4722)

# Travel keywords for rows whose MCC is missing or generic; case-insensitive, whole words.
TRAVEL_KEYWORDS_RE = (
    r"(?i)\b(AIRLINE|AIRWAYS|AIR TICKET|FLIGHT|AIRPORT|DEPARTURE|"
    r"EMIRATES AIR|ETIHAD|FLYDUBAI|AIR ARABIA|WIZZ AIR|BOARDING PASS)\b"
)

_UAE_CODES = ("AE", "ARE", "UAE")


def is_travel(mcc: Column, *texts: Column) -> Column:
    """A travel MCC, or a travel keyword in any of ``texts``."""
    keyword = F.lit(False)
    for text in texts:
        keyword = keyword | F.coalesce(text, F.lit("")).rlike(TRAVEL_KEYWORDS_RE)
    return F.coalesce(mcc.cast("int").isin(*TRAVEL_MCCS), F.lit(False)) | keyword


def is_uae(country: Column) -> Column:
    """True for a UAE country name or code in free text (``UNITED ARAB EMIRATES``,
    ``U.A.E``, ``AE``, typos such as ``UNITER ARAB EMIRATES``), False for any other
    filled value, NULL when empty."""
    letters = F.regexp_replace(F.upper(country), "[^A-Z]", "")
    return F.when(letters == "", None).otherwise(
        letters.isin(*_UAE_CODES) | letters.contains("EMIRATES")
    )
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `9b449af9a6c1bad9bfd9b05c515fb6044db647c578c2ad9a70fa40b958796dfc` · base trailing newline: yes · new sha256 `6bd897cc0ce4a022fe4136006122a686aa80fe1b7f03259e97a735ac4e55c8a8` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_cc_a2_locatability_b06_check": (
            crx_cc_a2_locatability.create_b06_check_pipeline()
        ),
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

### FILE: `src/enbd_collections/pipelines/casa/primary.py`
action: replace · base sha256 `cfb5b4eada961b8b329a82f81d65f25d9ac2a63c992a13f589acdadfb827a316` · base trailing newline: yes · new sha256 `6ee21700115339cf0f966270e7d89422e24827b77bb189b44d66110553da8b5f` · new trailing newline: yes

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
                tags=["casa", "primary"],
            )
        ],
    )
`````

New:

`````python
"""CASA primary pipeline.

kedro run --pipeline=casa_primary   (per model_id)
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import (
    build_card_transactions,
    build_return_events,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events and prm_casa_card_transactions from
    comp_financial_tran_repos_dly."""
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
            ),
            node(
                func=build_card_transactions,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.card_history_months",
                ],
                outputs="prm_casa_card_transactions",
                name="build_prm_casa_card_transactions",
                tags=["casa", "primary"],
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/__init__.py`
action: add · new sha256 `3c366189957072a37a15897a42fbb78f68549e2becfdfb03c8f77c0bc71208d6` · new trailing newline: yes

New:

`````python
"""A2 locatability engine shared by the CC and RL locatability pipelines."""

from .classify import build_a2_locatability
from .pipeline import create_a2_pipeline
from .signals import (
    build_dcore_signals,
    build_demographics_deceased,
    build_location_signals,
    build_way4_deceased,
)

__all__ = [
    "build_a2_locatability",
    "build_dcore_signals",
    "build_demographics_deceased",
    "build_location_signals",
    "build_way4_deceased",
    "create_a2_pipeline",
]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/b06_check.py`
action: add · new sha256 `d62bab99dddd4d6b7e6c430529b40bedc937c6ad8e064dc0b6ae0c4763fd99d1` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 06): the old A2 vs the new engine, run in PROD.

Log blocks, aggregates only:

* ``compare_a2_outputs`` (``B06 OUTPUT``): the old output (``crx_<p>_a2_locatability``)
  against the new one (``crx_<p>_a2_locatability_b06_check``) in the latest month — an
  old row is matched to the new row of the same account and month (the month's latest
  old observation) — plus the new location / reachability shares per month.
* ``describe_a2_rules`` (``B06 RULES``): which rule fires, which source holds the
  deciding evidence, unknown reasons, call days, deceased sources.
* ``describe_debit_evidence`` (``B06 DEBIT``): the base customers' rows in
  ``prm_casa_card_transactions`` by month, channel / type and place (the Offline → Machine
  change, ATM placement), and their ``reason_for_excluding`` values.
* ``split_by_product`` (``B06 PRODUCT``, RL only): the latest month by ``loan_type``.

Removed by the bundle's cleanup.
"""

import logging

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.location import is_uae

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B06 {name} START === [{model_id}]",
        *lines,
        f"=== B06 {name} END ===",
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


def _snake(col: str) -> F.Column:
    """'In Country' → 'in_country', 'Non-Reachable' → 'non_reachable'."""
    return F.regexp_replace(F.lower(F.trim(col)), "[ -]+", "_")


def compare_a2_outputs(old: DataFrame, new: DataFrame, model_id: str) -> None:
    """Old vs new location, reachability and deceased in the latest month; new shares
    per month."""
    latest_new = _latest_month(new)
    month = latest_new.agg(F.trunc(F.max("observation_date"), "month")).first()[0]
    in_month = Window.partitionBy("account_id").orderBy(
        F.col("observation_date").desc()
    )
    old_m = (
        old.filter(F.trunc("observation_date", "month") == F.lit(month))
        .withColumn("_rn", F.row_number().over(in_month))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("account_id").cast("string").alias("account_id"),
            _snake("location_state").alias("old_location"),
            _snake("reachability_state").alias("old_reachability"),
            F.col("deceased_flag_v2").cast("int").alias("old_deceased"),
        )
    )
    both = latest_new.join(old_m, on="account_id", how="full")
    lines = [
        (
            f"month {month}: new rows {latest_new.count()}, old rows {old_m.count()}, "
            f"new only {both.filter(F.col('old_location').isNull()).count()}, "
            f"old only {both.filter(F.col('a2_state').isNull()).count()}"
        ),
        "new a2_state:",
        *_table(latest_new, "a2_state"),
        "location old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_location", "location_state"
        ),
        "reachability old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()),
            "old_reachability",
            "reachability_state",
        ),
        "deceased old x new:",
        *_table(
            both.filter(F.col("a2_state").isNotNull()), "old_deceased", "deceased_flag"
        ),
        "new location_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "location_state",
        ),
        "new reachability_state by month:",
        *_table(
            new.withColumn("month", F.trunc("observation_date", "month")),
            "month",
            "reachability_state",
        ),
    ]
    _log("OUTPUT", model_id, lines)


def describe_a2_rules(new: DataFrame, model_id: str) -> None:
    """Rules, deciding sources, unknown reasons, call days and deceased sources in the
    latest month."""
    df = _latest_month(new)
    days = F.col("attempt_days_in_window")
    lines = [
        "location_rule x deciding source (L1: latest foreign, else latest UAE):",
        *_table(
            df.withColumn(
                "source",
                F.when(
                    F.col("location_rule") == "L1", F.col("last_foreign_source")
                ).otherwise(F.col("last_uae_source")),
            ),
            "location_rule",
            "source",
        ),
        "location_unknown_reason:",
        *_table(
            df.filter(F.col("location_state") == "unknown"), "location_unknown_reason"
        ),
        "L2 rows by months since the latest UAE evidence:",
        *_table(
            df.filter(F.col("location_rule") == "L2").withColumn(
                "months",
                F.floor(F.months_between("observation_date", "last_uae_date")).cast(
                    "int"
                ),
            ),
            "months",
        ),
        "reachability_state x reason:",
        *_table(df, "reachability_state", "reachability_unknown_reason"),
        "call days in the window:",
        *_table(
            df.withColumn(
                "call_days",
                F.when(days == 0, "0")
                .when(days < 3, "1-2")
                .when(days < 6, "3-5")
                .otherwise("6+"),
            ),
            "call_days",
        ),
        "skip-trace status ever (diagnostic) x location_state:",
        *_table(
            df.withColumn("skip_trace", F.col("last_skip_trace_date").isNotNull()),
            "skip_trace",
            "location_state",
        ),
        "deceased_source:",
        *_table(df.filter(F.col("deceased_flag") == 1), "deceased_source"),
    ]
    _log("RULES", model_id, lines)


def describe_debit_evidence(
    obs_base: DataFrame, casa_cards: DataFrame, model_id: str
) -> None:
    """The latest month's base customers' debit-card rows by month, type and place."""
    cifs = (
        _latest_month(obs_base)
        .select("cif_id")
        .filter(F.col("cif_id").isNotNull())
        .distinct()
    )
    uae = is_uae(F.col("place_country"))
    rows = (
        casa_cards.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(F.broadcast(cifs), on="cif_id", how="leftsemi")
        .withColumn(
            "type",
            F.when(F.col("channel_desc") == "ATM Transactions", F.lit("ATM")).otherwise(
                F.coalesce(F.col("merchant_type_desc"), F.lit("NULL"))
            ),
        )
        .withColumn("place", F.when(uae, "uae").when(~uae, "abroad").otherwise("none"))
        .withColumn("month", F.trunc(F.coalesce("value_date", "tran_date"), "month"))
    )
    lines = [
        "rows by month x type x place:",
        *_table(rows, "month", "type", "place"),
        "place_source by type:",
        *_table(rows, "type", "place_source"),
        "reason_for_excluding (all months):",
        *_table(rows, "reason_for_excluding"),
    ]
    _log("DEBIT", model_id, lines)


def split_by_product(new: DataFrame, rl_spine: DataFrame, model_id: str) -> None:
    """The latest month's states by ``loan_type`` (RL)."""
    products = rl_spine.select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("observation_date").cast("date").alias("observation_date"),
        "loan_type",
    ).dropDuplicates(["account_id", "observation_date"])
    df = _latest_month(new).join(
        products, on=["account_id", "observation_date"], how="left"
    )
    lines = [
        "loan_type x location_state:",
        *_table(df, "loan_type", "location_state"),
        "loan_type x reachability_state:",
        *_table(df, "loan_type", "reachability_state"),
        "loan_type x deceased_flag:",
        *_table(df, "loan_type", "deceased_flag"),
    ]
    _log("PRODUCT", model_id, lines)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/classify.py`
action: add · new sha256 `dc119a6701733d2106ac5321328083428f45f51d560220d90c41b0b909f69848` · new trailing newline: yes

New:

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

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/codes.py`
action: add · new sha256 `020635a25bd2d357fbd62ce4f7f81cef36c741cd2ebc456c1336d56c75c17140` · new trailing newline: yes

New:

`````python
"""DCORE vocabulary for A2 reachability and deceased (``dcore_prm_followup_outcomes``).

Result names are compared upper-cased and trimmed. The departure notes (location
evidence) live in the location feature.
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
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/pipeline.py`
action: add · new sha256 `af38bc9e38fec005ef836d670dd2a55d88320031abbfb3d4b39bc1167d7d184c` · new trailing newline: yes

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

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` runs the observation base,
``location_features`` and the same nodes, writes the axis to
``crx_<p>_a2_locatability_b06_check`` and logs the comparison with the old A2
(``b06_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.location.pipeline import (
    create_pipeline as create_location_pipeline,
)

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b06_check import (
    compare_a2_outputs,
    describe_a2_rules,
    describe_debit_evidence,
    split_by_product,
)
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


def create_b06_check_pipeline(product: str) -> Pipeline:
    """TEMPORARY: observation base + location inputs + the A2 pipeline writing to
    crx_<p>_a2_locatability_b06_check + the log-only comparison nodes.
    Remove with b06_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    check = f"crx_{product}_a2_locatability_b06_check"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a2_outputs,
            inputs=[f"crx_{product}_a2_locatability", check, "params:model_id"],
            outputs=None,
            name=f"compare_crx_{product}_a2_b06",
            tags=tags,
        ),
        node(
            func=describe_a2_rules,
            inputs=[check, "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_rules",
            tags=tags,
        ),
        node(
            func=describe_debit_evidence,
            inputs=[obs, "prm_casa_card_transactions", "params:model_id"],
            outputs=None,
            name=f"describe_crx_{product}_a2_b06_debit",
            tags=tags,
        ),
    ]
    if product == "rl":
        checks.append(
            node(
                func=split_by_product,
                inputs=[check, "rl_spine", "params:model_id"],
                outputs=None,
                name="split_crx_rl_a2_b06_product",
                tags=tags,
            )
        )
    obs_pipeline = (
        create_cc_obs_pipeline() if product == "cc" else create_rl_obs_pipeline()
    )
    return (
        obs_pipeline
        + create_location_pipeline()
        + create_a2_pipeline(product, output=check)
        + Pipeline(checks)
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a2_locatability/signals.py`
action: add · new sha256 `7d32d2bf2f4cef3771ac80f5a95f7a9e45083dbb1ec8717e38c5d36b0f449f3b` · new trailing newline: yes

New:

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
from .codes import (
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

# Travel rule (L2): the latest UAE evidence at most this many months after the last
# ticket, and none for at least SILENCE months before the observation date.
TRAVEL_GAP_MONTHS = 3
TRAVEL_SILENCE_MONTHS = 1
# Non-Reachable: the last this-many call days all failed.
GONE_DARK_DAYS = 3
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


def build_dcore_signals(  # pylint: disable=too-many-locals
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``reachability_state`` (non_reachable / reachable / unknown) and its evidence, plus
    ``dcore_deceased_date`` and ``last_skip_trace_date``.

    A call day is a day with an outbound call; it failed when every outbound call that
    day failed (``codes.FAILED_CALL``) and no contact was confirmed. A contact is an
    inbound call, an outbound call in category SUC, or a right-party result.

    non_reachable  the last GONE_DARK_DAYS call days all failed, the oldest in W, and no
                   contact since
    reachable      a contact in W
    unknown        no_dcore_record · no_contact_in_window
    """
    w_start = _window_start(window_months(model_id))
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
        .filter(F.col("_rank") <= GONE_DARK_DAYS)
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
        (F.col("_n_last") == GONE_DARK_DAYS)
        & (F.col("_failed_last") == GONE_DARK_DAYS)
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/__init__.py`
action: replace · base sha256 `62ef47840e708e821d9d88dffa95de7b2f19e32bdfd82435ffb5d2cf3eee1f06` · base trailing newline: yes · new sha256 `7ba01aa219eabdc0bb797c8f1df0ff14503674026de9d5a4fb6e3cd02ec403fc` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T12 — A2 Locatability axis v1 (3-state, DCORE-degraded)."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A2 locatability axis (location × reachability) on the shared ``a2_locatability``
engine."""

from .pipeline import create_b06_check_pipeline, create_pipeline

__all__ = ["create_b06_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a2_locatability/pipeline.py`
action: replace · base sha256 `19822f583104e8de3827f8f9e994795db1fca9057789fd1613a2c186f8eb904e` · base trailing newline: yes · new sha256 `b34f6eb6ab0b1049925c906f01f1c51b89026ab1a4fefa6cec210649a2f7867e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: A2 Locatability axis (location x reachability).

# pylint: disable=line-too-long

Four-node pipeline that derives the full A2 locatability axis and emits the
shipped persona column ``a2_state`` at (account_id, observation_date) grain.
Node 4 is T29's location x reachability redesign, promoted 2026-10-22 to
replace T12's original 7-state waterfall (see ``RESULTS.md``).

Architecture:
    build_a2_base                → crx_cc_a2_base
    build_a2_login_presence      → crx_cc_a2_login_presence
    build_a2_contact_signals     → crx_cc_a2_contact_signals
    build_a2_locatability        → crx_cc_a2_locatability   ← shipped axis

Inputs:
    cc_spine                        Model-id-scoped spine (anchor grain)
    crx_cc_spell_table              T03b — t0 + spell_end per spell
    crx_cc_departure_signature      T06 — departure trail columns (R14 reuse)
    prm_digital_login_monthly       Obs-anchored digital presence + H2 departure login
    dcore_observation_spine         account→agreement mapping (contract_id, observation_date, agreement_id, cif_id)
    dcore_prm_followup_outcomes     DCORE contact attempt log (carries result_name directly)
    params:model_id                 Selects the segment-aware recency/staleness thresholds
    prm_contract                    Way4 block_code_1/block_code_2 deceased corroboration (T34)
    prm_client                      CIF bridge pair for prm_contract (T34)
    feat_demographics_cif           ft_deceased_flag deceased corroboration (T34)

Output:
    crx_cc_a2_locatability — A2 axis for every (account_id, observation_date)
    pair in cc_spine; a2_state ∈ {Deceased, Skip - Reachable,
    Skip - Non-Reachable, Skip - Unknown, In Country - Reachable,
    In Country - Non-Reachable, In Country - Unknown, Unknown - Reachable,
    Unknown - Non-Reachable, Unknown - Unknown}.

Run with:
    kedro run --pipeline=crx_cc_a2_locatability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a2_base,
    build_a2_contact_signals,
    build_a2_locatability,
    build_a2_login_presence,
)

_TAGS = ["crx", "a2", "locatability", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node A2 Locatability pipeline."""
    return Pipeline(
        [
            node(
                func=build_a2_base,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "crx_cc_departure_signature",
                ],
                outputs="crx_cc_a2_base",
                name="build_crx_a2_base",
                tags=_TAGS,
            ),
            node(
                func=build_a2_login_presence,
                inputs=[
                    "crx_cc_a2_base",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_cc_a2_login_presence",
                name="build_crx_a2_login_presence",
                tags=_TAGS,
            ),
            node(
                func=build_a2_contact_signals,
                inputs=[
                    "crx_cc_a2_base",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                ],
                outputs="crx_cc_a2_contact_signals",
                name="build_crx_a2_contact_signals",
                tags=_TAGS,
            ),
            node(
                func=build_a2_locatability,
                inputs={
                    "base": "crx_cc_a2_base",
                    "login_presence": "crx_cc_a2_login_presence",
                    "contact_signals": "crx_cc_a2_contact_signals",
                    "model_id": "params:model_id",
                    "prm_contract": "prm_contract",
                    "prm_client": "prm_client",
                    "feat_demographics_cif": "feat_demographics_cif",
                },
                outputs="crx_cc_a2_locatability",
                name="build_crx_a2_locatability",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: CC A2 locatability axis on the shared ``a2_locatability`` engine.

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``digital_login``, ``casa_primary`` and ``location_features``.

    kedro run --pipeline=crx_cc_a2_locatability

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` — see
``a2_locatability/pipeline.py``.
"""

from kedro.pipeline import Pipeline

from ..a2_locatability.pipeline import create_a2_pipeline
from ..a2_locatability.pipeline import create_b06_check_pipeline as _b06_check


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_cc_a2_locatability", **kwargs
) -> Pipeline:
    """The CC A2 axis written to ``output``."""
    return create_a2_pipeline("cc", output)


def create_b06_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the CC A2 check (bundle 06)."""
    return _b06_check("cc")
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/__init__.py`
action: replace · base sha256 `e091743321c2247e381a22ab680f73de8dd3f1149443a33e20397d1240284d37` · base trailing newline: yes · new sha256 `44623969a075cd08e3588eeffde5660befd434443023c3ae6e07cd3c9cf41aa1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A2-1 A2 Locatability axis for Retail Loans."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A2 locatability axis (location × reachability) on the shared ``a2_locatability``
engine."""

from .pipeline import create_b06_check_pipeline, create_pipeline

__all__ = ["create_b06_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a2_locatability/pipeline.py`
action: replace · base sha256 `6d21c5b5c8d3507d8615288cbaea12be99454b27a5cb073012bdcb4441140023` · base trailing newline: yes · new sha256 `d546cab2b51d1e2b93dec4f94fbf47460a5f4b7b1cd4f539990c22cad654a054` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL-A2-1 — A2 Locatability axis for Retail Loans.

# pylint: disable=line-too-long

Four-node pipeline adapted from CC A2 locatability for monthly-grain RL accounts.
Reuses CC nodes via thin wrappers; Node 4 imports the CC function directly.
Node 4's underlying derivation is RL-A2-3's location x reachability redesign,
promoted 2026-10-22 to replace RL-A2-1's original 7-state waterfall (see
``RESULTS_RL.md``) — the import path is unchanged, only the implementation
behind ``build_a2_locatability`` changed.

Architecture:
    build_rl_a2_base              → crx_rl_a2_base              [Node 1]
    build_rl_a2_login_presence    → crx_rl_a2_login_presence    [Node 2]
    build_rl_a2_contact_signals   → crx_rl_a2_contact_signals   [Node 3]
    build_a2_locatability         → crx_rl_a2_locatability      [Node 4]  ← shipped axis

Node 1 inputs: crx_rl_a4_spine, crx_rl_departure_signature
    crx_rl_a4_spine already carries (account_id, observation_date, spell_id,
    t0, cif_id). Departure signals sourced from crx_rl_departure_signature
    (RL-A2-2 pre-computation pipeline — all 4 signals derived for real).

Node 2: obs_month_end=True — RL observation dates are month-end.

Node 3: dcore_observation_spine = RL-scoped DCORE spine (built by RL-D5 pipeline).
    Applies 24m partition floor on dcore_prm_followup_outcomes before calling
    build_a2_contact_signals (performance guard per TASKS_RL.md).

Node 4: build_a2_locatability imported directly from cc_a2_locatability.nodes.
    No RL-specific logic needed — a2_state derivation is domain-agnostic.
    RL has no Way4-equivalent block-code table, so `prm_contract`/`prm_client`
    are not supplied here (stay at their Python defaults, `None`) —
    `crx_rl_a2_base` already carries `cif_id` directly, so no CIF bridge is
    needed either; `feat_demographics_cif` is supplied for deceased
    corroboration (T34). This coverage is unvalidated — no RL PROD run has
    measured it yet (see `RESULTS_RL.md`).

Run with:
    kedro run --pipeline=crx_rl_a2_locatability
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.pipelines.crx_persona.cc_a2_locatability.nodes import (
    build_a2_locatability,
)

from .nodes import (
    build_rl_a2_base,
    build_rl_a2_contact_signals,
    build_rl_a2_login_presence,
)

_TAGS = ["crx", "a2", "locatability", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node RL A2 Locatability pipeline."""
    return Pipeline(
        [
            # ── Node 1: spine + departure stub (FX leakage, no spell join) ──
            node(
                func=build_rl_a2_base,
                inputs=[
                    "crx_rl_a4_spine",
                    "crx_rl_departure_signature",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a2_base",
                name="build_rl_a2_base",
                tags=_TAGS,
            ),
            # ── Node 2: obs-date-anchored digital login presence ──────────
            node(
                func=build_rl_a2_login_presence,
                inputs=[
                    "crx_rl_a2_base",
                    "prm_digital_login_monthly",
                ],
                outputs="crx_rl_a2_login_presence",
                name="build_rl_a2_login_presence",
                tags=_TAGS,
            ),
            # ── Node 3: DCORE contact signals (24m floor, RL-D5 spine) ─────
            node(
                func=build_rl_a2_contact_signals,
                inputs=[
                    "crx_rl_a2_base",
                    "dcore_observation_spine",
                    "dcore_prm_followup_outcomes",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a2_contact_signals",
                name="build_rl_a2_contact_signals",
                tags=_TAGS,
            ),
            # ── Node 4: assemble + derive a2_state (CC function, no wrap) ──
            node(
                func=build_a2_locatability,
                inputs={
                    "base": "crx_rl_a2_base",
                    "login_presence": "crx_rl_a2_login_presence",
                    "contact_signals": "crx_rl_a2_contact_signals",
                    "model_id": "params:model_id",
                    "feat_demographics_cif": "feat_demographics_cif",
                },
                outputs="crx_rl_a2_locatability",
                name="build_rl_a2_locatability",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL A2 locatability axis on the shared ``a2_locatability`` engine.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``digital_login``, ``casa_primary`` and ``location_features``.

    kedro run --pipeline=crx_rl_a2_locatability

TEMPORARY (mirror bundle 06): ``create_b06_check_pipeline`` — see
``a2_locatability/pipeline.py``.
"""

from kedro.pipeline import Pipeline

from ..a2_locatability.pipeline import create_a2_pipeline
from ..a2_locatability.pipeline import create_b06_check_pipeline as _b06_check


def create_pipeline(  # pylint: disable=unused-argument
    output: str = "crx_rl_a2_locatability", **kwargs
) -> Pipeline:
    """The RL A2 axis written to ``output``."""
    return create_a2_pipeline("rl", output)


def create_b06_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the RL A2 check (bundle 06)."""
    return _b06_check("rl")
`````

### FILE: `src/enbd_collections/pipelines/location/__init__.py`
action: add · new sha256 `d49f2df0a717db66c765b379f1b82c23b5b90aa3ed96c20c7d6d51578fe3fb72` · new trailing newline: yes

New:

`````python
"""Location inputs (DCORE agreement map, location feature) of the A2 axis."""
`````

### FILE: `src/enbd_collections/pipelines/location/pipeline.py`
action: add · new sha256 `a6ff682d6dc8d56238be8502bcba8ac5678cc907d68236dcaa618db9fb2b3632` · new trailing newline: yes

New:

`````python
"""Location inputs of the A2 locatability axis (per model_id).

    dcore_observation_spine ─► prm_dcore_account_agreements ─┐
    prm_digital_login_monthly, prm_casa_card_transactions,    ├─► feat_cif_location_monthly
    prm_transaction, prm_contract, prm_client,                │
    dcore_prm_followup_outcomes ──────────────────────────────┘

Needs ``digital_login`` and ``casa_primary`` for the model_id first.

    kedro run --pipeline=location_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.location import feat_cif_location_monthly
from enbd_collections.nodes.primary.dcore import prm_dcore_account_agreements


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_dcore_account_agreements and feat_cif_location_monthly."""
    return Pipeline(
        [
            node(
                func=prm_dcore_account_agreements.build,
                inputs="dcore_observation_spine",
                outputs="prm_dcore_account_agreements",
                name="build_prm_dcore_account_agreements",
                tags=["dcore", "primary"],
            ),
            node(
                func=feat_cif_location_monthly.build,
                inputs={
                    "logins": "prm_digital_login_monthly",
                    "casa_cards": "prm_casa_card_transactions",
                    "transactions": "prm_transaction",
                    "contracts": "prm_contract",
                    "clients": "prm_client",
                    "followup": "dcore_prm_followup_outcomes",
                    "agreements": "prm_dcore_account_agreements",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:location_features.history_months",
                },
                outputs="feat_cif_location_monthly",
                name="build_feat_cif_location_monthly",
                tags=["location", "features"],
            ),
        ]
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
Clean up after mirror bundle 06_a2_locatability_refactor.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths
  for model_id cc_60_180 **and** rl_60_180 from the workplace conf and write out each
  command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability_b06_check` (cc_60_180)
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability_b06_check` (rl_60_180)
  - the retired old A2 intermediates, for the model_id of their prefix:
    `crx_cc_a2_base`, `crx_cc_a2_login_presence`, `crx_cc_a2_contact_signals` (cc_60_180),
    `crx_rl_a2_base`, `crx_rl_a2_login_presence`, `crx_rl_a2_contact_signals` (rl_60_180),
    each under `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/`.
- Remove the temporary check (everything marked TEMPORARY for bundle 06):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a2_locatability_b06_check` and
    `crx_rl_a2_locatability_b06_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a2_locatability_b06_check`
    entries and their comments;
  - crx_persona/a2_locatability/pipeline.py: `create_b06_check_pipeline`, the imports of
    `create_location_pipeline`, `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and
    `b06_check`, and the TEMPORARY paragraph of the module docstring;
  - crx_persona/cc_a2_locatability/ and rl_a2_locatability/: `create_b06_check_pipeline`
    in `pipeline.py` (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a2_locatability/b06_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b06" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
