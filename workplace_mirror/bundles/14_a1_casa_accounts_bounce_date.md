# Mirror bundle 14 — A1 — CASA = current and savings accounts by scheme code, bureau bounces by return date

apply_bundle version: 7 · built 2026-11-04 from `5e21318..6249431` · source: 1 added, 15 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Work on a branch (the apply script refuses to run on main):

```bash
git checkout -b feature/persona_redesign_b14
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/14_a1_casa_accounts_bounce_date.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '14_a1_casa_accounts_bounce_date.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/14_a1_casa_accounts_bounce_date.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **Account master catalog entry.** Add `raw_casa_acid_to_cif` to our raw catalog, a copy of WM's
   entry of the same name (`wealth_management` `conf/base/catalog.yml`, around line 364). Keep the
   same table (`general_acct_mast_table`), columns (`cif_id, acid, schm_code, acct_crncy_code,
   foracid`), `SELECT DISTINCT` and WM's filters (`emp_id`, `acct_ownership`, non-null `cif_id` and
   `acid`). Use our `*finacle` anchor and `aacoe_prefix`, as `general_acct_mast_bridge` does in
   `catalog_raw_demographics.yml`.
2. **Bounce date on the alert primary.** `feat_cif_bureau_bounces_monthly` now reads `dt_of_return`
   from `prm_bureau_alert_enriched` (raw alert column `DT_OF_RETURN`). Find the node that builds
   `prm_bureau_alert_enriched` and its staging input. If the column is not carried through, add it
   (as a date, name `dt_of_return`). Then write out the exact command that rebuilds **only** those
   nodes (`kedro run --env=dev --pipeline=... --nodes=...`), as for bundle 12. You will use it in
   step 6.
3. **Tests.** Run the CASA and A1 test modules and fix the ones the new signatures break:
   - `build_casa_activity(transactions, casa_accounts)` and `build_returns(return_events,
     casa_accounts)` need `foracid` on the legs;
   - `build_casa_accounts` is new;
   - the bounce feature reads `cif_id`, `dt_of_return` and `bounced_cheque_amount`, and returns
     `bounce_events` and `max_bounce_amount`.

Then check:
- `grep -rn "b12" src conf --include='*.py' --include='*.yml'` prints nothing;
- `kedro registry list | grep a1_ability` lists the two `*_b14_check` pipelines;
- `kedro catalog list | grep -E "raw_casa_acid_to_cif|prm_casa_accounts"` finds both.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: CASA accounts by scheme code (S16), bureau bounce by return date (S15), B14 check" && git push -u origin feature/persona_redesign_b14
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/14_a1_casa_accounts_bounce_date.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b14 && git pull
```

Run steps 6–8 for **`rl_60_180`**, then **`cc_60_180`**: set `model_id` in
`conf/dev/globals_dev.yml`, with the persona dates unchanged. The 180+ model_ids are optional for the
check, but step 6 and step 8 must run for every model_id you score (all four). Switch back when you
are done.

**Step 6.** Rebuild the inputs. First the CASA primaries (this writes the new `prm_casa_accounts`):

```bash
kedro run --env=dev --pipeline=casa_primary
```

Then the alert primary, with the command Sonnet gave you in step 4. Then the features:

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=casa_features
```

**Step 7.** Run the check. It compares with the current real output, so do not run step 8 yet. For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b14_check
```

For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b14_check
```

Paste back every block from `=== B14 … START ===` to `=== B14 … END ===`: `OUTPUT`, `ACCOUNTS`,
`BOUNCES`. A summary file like the last ones is fine.

**Step 8.** Only after the B14 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** A1 counts only real current and savings accounts as CASA, and dates bureau
bounces by the day the cheque bounced. It also adds a check that measures both against the current
output.

- **CASA accounts (spec S16).** `comp_financial_tran_repos_dly` also holds the loan account itself, so
  every RL customer looked like a CASA holder and "No CASA" never fired. New primary
  `prm_casa_accounts` (`nodes/primary/casa/prm_casa.py::build_casa_accounts`): the accounts of
  `raw_casa_acid_to_cif` (the Finacle account master, read as WM reads it) whose scheme code is one of
  the 49 current + savings codes (`casa_primary.current_account_codes` / `saving_account_codes`, WM's
  `current_accounts` + `saving_accounts`). `feat_cif_casa_activity_monthly` and
  `feat_cif_returns_monthly` keep only legs on those accounts (`foracid`). The primaries
  `prm_casa_transactions` / `prm_casa_return_events` still hold all legs. The WM balance arm of
  `casa_held` is unchanged.
- **Bureau bounce date (spec S15).** `feat_cif_bureau_bounces_monthly` dates each bounce by
  `dt_of_return`. One bounce = one `(cif_id, dt_of_return)`, with the largest amount that day. The
  comparison with the previous pull is gone. New column `max_bounce_amount`; `bounce_pulls` is dropped
  (no reader).
- **Check** (`a1_ability/b14_check.py`, pipelines `crx_cc_a1_ability_b14_check`,
  `crx_rl_a1_ability_b14_check`). Blocks:
  - `B14 OUTPUT`: old × new state, and why each row moved;
  - `B14 ACCOUNTS`: the base CIFs' legs by account length × scheme class;
  - `B14 BOUNCES`: the pull rule against the return date.
  The bundle 12 check is not in it: its cleanup is done.
- Expected for `rl_60_180` (the `101` proxy run, handoff 34): about 4% of rows move, mostly Low to
  Unknown. "No CASA" goes from 0 to about 13%, most of it on Auto loans. The exact rule should move
  fewer rows than the proxy, because it keeps 13-character current / savings accounts that `101`
  dropped.

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
| replace | `conf/base/parameters/parameters_casa.yml` |
| replace | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` |
| replace | `src/enbd_collections/nodes/features/casa/feat_cif_casa.py` |
| replace | `src/enbd_collections/nodes/primary/casa/prm_casa.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/casa/features.py` |
| replace | `src/enbd_collections/pipelines/casa/primary.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/b14_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_casa.yml`
action: replace · base sha256 `4b8098d484478728340b2f95a871565b24b4f3c52faac4586ea050a285c8c525` · base trailing newline: yes · new sha256 `d4975eb895699094e89bc601b5e72ac2bdab805175ed667694ca8242ae9efe25` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# CASA primary datasets (pipeline casa_primary) and monthly CASA features (casa_features).

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

# Every CASA transaction leg, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
prm_casa_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/transactions"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
  metadata:
    kedro-viz:
      layer: primary

# Card numbers registered as payment beneficiaries (no CIF in the source).
prm_beneficiary_cards:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/beneficiary_cards"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Salary credited with us per (cif_id, month_end), from the WM salary snapshots, all history.
feat_cif_internal_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_internal_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# CASA average balance and any flow per (cif_id, month_end), from the WM weekly tables.
feat_cif_casa_balance_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_balance_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# CASA legs and AED per (cif_id, month_end, lane), from prm_casa_transactions.
feat_cif_casa_activity_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_activity_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Largest CASA payment to a registered external card per (cif_id, month_end).
feat_cif_ext_card_payment_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_ext_card_payment_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Returned-transaction events per (cif_id, month_end, reason), from prm_casa_return_events.
feat_cif_returns_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_returns_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

New:

`````yaml
# CASA primary datasets (pipeline casa_primary) and monthly CASA features (casa_features).

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

# Every CASA transaction leg, all CIFs, one row per (tran_id, part_tran_srl_num, tran_date).
prm_casa_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/transactions"
  save_args:
    mode: overwrite
    partitionBy: ["event_month"]
  metadata:
    kedro-viz:
      layer: primary

# Current and savings accounts (scheme code in casa_primary's CA / SA lists), one row per
# (foracid, cif_id, schm_code), from raw_casa_acid_to_cif.
prm_casa_accounts:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/casa_accounts"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Card numbers registered as payment beneficiaries (no CIF in the source).
prm_beneficiary_cards:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/beneficiary_cards"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Salary credited with us per (cif_id, month_end), from the WM salary snapshots, all history.
feat_cif_internal_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_internal_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# CASA average balance and any flow per (cif_id, month_end), from the WM weekly tables.
feat_cif_casa_balance_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_balance_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# CASA legs and AED per (cif_id, month_end, lane), from prm_casa_transactions on
# prm_casa_accounts.
feat_cif_casa_activity_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_activity_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Largest CASA payment to a registered external card per (cif_id, month_end).
feat_cif_ext_card_payment_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_ext_card_payment_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Returned-transaction events per (cif_id, month_end, reason), from prm_casa_return_events
# on prm_casa_accounts.
feat_cif_returns_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_returns_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `0ba8f9633d801ec0f9e0e884aca0dc2a4fc052bb650be1af6b5aebcff461ffef` · base trailing newline: yes · new sha256 `68baacf72b4af09ce54e093b0da9747f7465a37d3083ed463c09a14182394742` · new trailing newline: yes

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

# TEMPORARY (mirror bundle 14): the new output written by the b14 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b14_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b14_check"
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

# TEMPORARY (mirror bundle 14): the new output written by the b14 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b14_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b14_check"
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

### FILE: `conf/base/parameters/parameters_casa.yml`
action: replace · base sha256 `e90c2f5c365503c1a4019de1d89b565b0ef8b1de2325139f55d54e95313852ec` · base trailing newline: yes · new sha256 `b6aeea68f8589d5225780ae1bca54d04f0b7469b83bf8f55f22e1628b158d845` · new trailing newline: yes

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
  # Calendar months of debit-card rows kept in prm_casa_card_transactions up to and
  # including the persona start month (location evidence has no age limit; the raw
  # table holds about three years).
  card_history_months: 36
  # Calendar months of all CASA legs kept in prm_casa_transactions up to and including the
  # persona start month: the A1 "holds a CASA with us" test looks back 12 months.
  transaction_history_months: 12

##################################################
# CASA FEATURES
##################################################
casa_features:
  # Calendar months kept up to and including the persona start month by the WM-based
  # features (balances, external card payments): the A1 prior window (12 months at 180+)
  # and the 12-month CASA test. Internal salary keeps all history.
  history_months: 12
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
  # Calendar months of all CASA legs kept in prm_casa_transactions up to and including the
  # persona start month: the A1 "holds a CASA with us" test looks back 12 months.
  transaction_history_months: 12
  # Finacle scheme codes of current and savings accounts (WM's current_accounts and
  # saving_accounts lists): prm_casa_accounts keeps these; loans, term deposits and other
  # schemes are not CASA. WM's casa_scheme_codes (207) also holds term deposits and others.
  current_account_codes: [
    "020", "036", "051", "061", "068", "069", "070", "071", "078", "079", "080", "090",
    "100", "101", "102", "103", "104", "105", "106", "110", "113", "117", "118", "119",
    "124", "145", "149", "450", "451", "452", "453", "455", "456", "486", "660", "662",
  ]
  saving_account_codes: [
    "021", "023", "026", "031", "034", "035", "038", "082", "085", "086", "097", "311",
    "590",
  ]

##################################################
# CASA FEATURES
##################################################
casa_features:
  # Calendar months kept up to and including the persona start month by the WM-based
  # features (balances, external card payments): the A1 prior window (12 months at 180+)
  # and the 12-month CASA test. Internal salary keeps all history.
  history_months: 12
`````

### FILE: `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py`
action: replace · base sha256 `2c88f6bf68d9e5bac0539979a50c4a6c731cf0158298a9bea020366ed0e6a4eb` · base trailing newline: yes · new sha256 `c5d9653ae0102575d6c38b21db8616cca961fdecba48c9bd7fdb91a9001542e7` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bureau pull that reports a bounced cheque,
dated by the pull (``extract_date``; the bureau gives no bounce date):

* ``bounce_pulls``  — pulls that report a bounced amount;
* ``bounce_events`` — of those, the pulls that report something new: per alert key
  ``(cif_id, contract_type, alert_description)``, the bounced amount differs from the
  key's previous pull, or the previous pull had none. A bounce repeated unchanged in
  later pulls counts once.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_KEY = ["cif_id", "contract_type", "alert_description"]


def build(alerts: DataFrame) -> DataFrame:
    """Bounce pulls and new bounce events from ``prm_bureau_alert_enriched``. Several
    rows of one key in one pull count as one pull, with the largest amount."""
    missing = sorted(
        {*_KEY, "extract_date", "bounced_cheque_amount"} - set(alerts.columns)
    )
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    pulls = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(
            F.col("cif_id").cast("string").alias("cif_id"),
            "contract_type",
            "alert_description",
            F.to_date("extract_date").alias("pull_date"),
            F.coalesce(F.col("bounced_cheque_amount").cast("double"), F.lit(0.0)).alias(
                "amount"
            ),
        )
        .groupBy(*_KEY, "pull_date")
        .agg(F.max("amount").alias("amount"))
    )
    previous = F.lag("amount").over(Window.partitionBy(*_KEY).orderBy("pull_date"))
    bounced = F.col("amount") > 0
    new = bounced & (F.coalesce(previous, F.lit(0.0)) != F.col("amount"))
    return (
        pulls.withColumn("_new", new)
        .filter(bounced)
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(
            F.count(F.lit(1)).alias("bounce_pulls"),
            F.sum(F.col("_new").cast("int")).alias("bounce_events"),
        )
    )
`````

New:

`````python
"""Feature node: bureau-reported bounced cheques per customer and month.

One row per ``(cif_id, month_end)`` with a bounce, dated by the bureau's return date
(``dt_of_return``), not by the pull. A bounce is a ``(cif_id, dt_of_return)``: the same
return date repeated in later pulls is one bounce, and several cheques returned on one
day are one bounce with the largest amount.

* ``bounce_events`` — bounce days in the month;
* ``max_bounce_amount`` — the largest bounced amount of those days.

Rows with a bounced amount but no return date are not counted.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def build(alerts: DataFrame) -> DataFrame:
    """Bounce days per month from ``prm_bureau_alert_enriched``."""
    missing = sorted(
        {"cif_id", "dt_of_return", "bounced_cheque_amount"} - set(alerts.columns)
    )
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    amount = F.col("bounced_cheque_amount").cast("double")
    bounces = (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & F.col("dt_of_return").isNotNull()
            & (amount > 0)
        )
        .groupBy(
            F.col("cif_id").cast("string").alias("cif_id"),
            F.to_date("dt_of_return").alias("bounce_date"),
        )
        .agg(F.max(amount).alias("amount"))
    )
    return bounces.groupBy("cif_id", F.last_day("bounce_date").alias("month_end")).agg(
        F.count(F.lit(1)).alias("bounce_events"),
        F.max("amount").alias("max_bounce_amount"),
    )
`````

### FILE: `src/enbd_collections/nodes/features/casa/feat_cif_casa.py`
action: replace · base sha256 `f4a04228b00593241e4116710b6b3401b9d728dfeb2dd2c7311b11cc6350422c` · base trailing newline: yes · new sha256 `7b49e51b066fb8bd230f72401f3d86180de7eb02f53d15867c91a1e397b3adef` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature nodes: monthly CASA features per customer, all customers.

Each table has one row per ``(cif_id, month_end)`` (plus ``lane`` / ``reason`` where
named) with any data; customers are CIFs, so every CASA account of the customer counts.
Values are raw: which lanes, reasons or amounts count is decided by the consumers.

* ``feat_cif_internal_salary_monthly`` — salary credited with us per month (WM);
* ``feat_cif_casa_balance_monthly``    — CASA average balance and any flow per month (WM);
* ``feat_cif_casa_activity_monthly``   — transaction legs per month and lane (FTR);
* ``feat_cif_ext_card_payment_monthly`` — payments to registered external cards (WM);
* ``feat_cif_returns_monthly``          — returned-transaction events per reason (FTR).

WM weekly tables carry ``week_number`` as ``yyyyMM0W`` (week 01–04 of the month).
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

_CASA_BALANCE = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"

# Transaction lanes (FTR row-handling reference), assigned in this order: a leg takes the
# first lane it matches.
SIGNAL_REASONS = ("DDS Rejects/Reversal", "CHEQUE RETURNS")
_FEE_TYPES = ("CHARGES", "FEES", "INTEREST PAID", "INTEREST COLLECTION")
_NOISE_REASONS = ("CHARGES", "FEES", "REVERSAL", "CANCELLED")
_GROUP_REASONS = ("SUBSIDIARIES EXCLUSION", "INTERNAL TRANSFER - LIV")
_AUTO_SAVE_CODES = ("LV95", "LV3")
_AMBIGUOUS_TYPES = ("MISCELLANEOUS", "MC/DD", "MC/DD-ISSUE", "STANDING INSTRUCTIONS")
_ECONOMIC_TYPES = (
    "INWARD REMITTANCE",
    "OUTWARD REMITTANCE",
    "INTERNAL TRANSFER - OTHERS",
    "CASH DEPOSIT",
    "CASH WITHDRAWALS",
    "INWARD CLEARING",
    "OUTWARD CLEARING",
    "BILL PAYMENTS",
)
LANES = (
    "signal",  # DDS rejects, cheque returns
    "refund",  # POS refunds (reason RETURNS)
    "card_spend",  # POS debits
    "card_payment",  # payments to the customer's own credit card
    "wash",  # transfers between the customer's own accounts, auto-save
    "fee_interest",
    "reversal",  # reversals, cancellations
    "group_internal",  # group subsidiaries, Liv
    "own_loan",  # the bank recovering the customer's own loan instalment
    "ambiguous",  # the rest of MISCELLANEOUS and the tiny instruction types
    "economic",  # remittances, transfers to others, cash, clearing, bill payments
    "unclassified",
)


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def _wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def _wm_week_date(week_number: str = "week_number") -> Column:
    """The middle of week W of the month (day 4, 11, 18 or 25): within 4 days of any
    day of that week."""
    week = F.substring(F.col(week_number).cast("string"), 7, 2).cast("int")
    return F.date_add(_wm_month(week_number), 7 * week - 4)


def _cif() -> Column:
    return F.col("cif_id").cast("string").alias("cif_id")


def build_internal_salary(wm_salary: DataFrame) -> DataFrame:
    """``salary``: the month's total of salary-flagged credits with us, recovered from
    every weekly snapshot of ``wm_fea_salary_days_since_increment`` (all history).

    Each snapshot carries the latest salary month's total and the days from the first of
    that month to the snapshot; the snapshot's week date minus those days lands within a
    few days of the first of the salary month, so it is rounded to the nearest first.
    Snapshots that see the same month collapse to its largest total.
    """
    _require(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credited = F.date_sub(
        _wm_week_date(), F.col("ft_days_since_salary_transaction").cast("int")
    )
    month = F.trunc(F.date_add(credited, 15), "month")  # nearest first of a month
    return (
        wm_salary.filter(
            (F.col("ft_last_salary_amount") > 0)
            & F.col("ft_days_since_salary_transaction").isNotNull()
        )
        .groupBy(_cif(), F.last_day(month).alias("month_end"))
        .agg(F.max(F.col("ft_last_salary_amount").cast("double")).alias("salary"))
    )


def build_casa_balance(
    wm_casa_balance: DataFrame,
    wm_casa_flow: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``casa_balance``: the 4-week CASA (current + savings) average at the month's last
    weekly snapshot; ``casa_flow``: 1 when any week of the month has an inflow or outflow.
    From the first of the last ``history_months`` months up to the persona start month on.
    """
    _require(
        wm_casa_balance,
        ["cif_id", "week_number", _CASA_BALANCE],
        "wm_fea_casa_eod_avg_balance",
    )
    _require(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN, _CASA_OUT],
        "wm_fea_casa_cc_inflow_outflow",
    )
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    last_week = F.max(
        F.struct(
            F.col("week_number").cast("string").alias("w"),
            F.col(_CASA_BALANCE).cast("double").alias("v"),
        )
    )
    balance = (
        wm_casa_balance.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(last_week.alias("_last"))
        .select("cif_id", "month_end", F.col("_last.v").alias("casa_balance"))
    )
    moved = (F.col(_CASA_IN) > 0) | (F.col(_CASA_OUT) > 0)
    flow = (
        wm_casa_flow.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(F.max(moved.cast("int")).alias("casa_flow"))
    )
    return balance.join(flow, on=["cif_id", "month_end"], how="full")


def transaction_lane() -> Column:
    """The lane of a ``prm_casa_transactions`` leg (``LANES``).

    Signal rows first; card rows before the reason rules, because the bank's reason flag
    also marks own-card payments; then noise, own-loan recovery, ambiguous and economic
    types. Types are compared exactly, after upper-casing and collapsing spaces.
    """
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    reason = F.trim("reason_for_excluding")
    debit = F.col("tran_dc") == "D"
    narration = F.upper(F.trim("tran_narration_1"))
    noise_reason = F.coalesce(reason.isin(*_NOISE_REASONS), F.lit(False))
    return (
        F.when(reason.isin(*SIGNAL_REASONS) | (t == "CHEQUE RETURNS"), "signal")
        .when(reason == "RETURNS", "refund")
        .when((t == "POS TRANSACTIONS") & debit & ~noise_reason, "card_spend")
        .when(t == "CREDIT CARD PAYMENTS", "card_payment")
        .when(
            (t == "INTERNAL TRANSFER - SELF")
            | F.col("tran_particular_code").isin(*_AUTO_SAVE_CODES)
            | (reason == "INTERNAL TRANSFER - SELF"),
            "wash",
        )
        .when(reason.isin("CHARGES", "FEES") | t.isin(*_FEE_TYPES), "fee_interest")
        .when(reason.isin("REVERSAL", "CANCELLED") | (t == "REVERSAL"), "reversal")
        .when(
            reason.isin(*_GROUP_REASONS) | t.endswith("- SUBSIDIARIES"),
            "group_internal",
        )
        .when(
            (t == "MISCELLANEOUS") & narration.startswith("INSTL_RECOVERY"), "own_loan"
        )
        .when(t.isin(*_AMBIGUOUS_TYPES), "ambiguous")
        .when(t.isin(*_ECONOMIC_TYPES), "economic")
        .otherwise("unclassified")
    )


def build_casa_activity(transactions: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, lane)``: ``legs`` and the credit / debit AED of
    ``prm_casa_transactions`` (its whole history)."""
    _require(
        transactions,
        [
            "cif_id",
            "tran_date",
            "tran_dc",
            "tran_type",
            "reason_for_excluding",
            "tran_particular_code",
            "tran_narration_1",
            "actual_tran_amt_aed",
        ],
        "prm_casa_transactions",
    )
    amount = F.col("actual_tran_amt_aed").cast("double")
    return (
        transactions.withColumn("lane", transaction_lane())
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"), "lane")
        .agg(
            F.count(F.lit(1)).alias("legs"),
            F.sum(F.when(F.col("tran_dc") == "C", amount)).alias("credit_aed"),
            F.sum(F.when(F.col("tran_dc") == "D", amount)).alias("debit_aed"),
        )
    )


def build_ext_card_payments(
    labelled: DataFrame,
    beneficiary_cards: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``max_payment`` / ``payments``: CASA payments to a card registered as a payment
    beneficiary (``prm_beneficiary_cards``; an external card) per month, from
    ``wm_pri_labelled_transactions``.

    The beneficiary list is a current snapshot: a card registered later still counts
    (a mild look-ahead, accepted).
    """
    _require(
        labelled,
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
    _require(beneficiary_cards, ["card_number"], "prm_beneficiary_cards")
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    cards = beneficiary_cards.select(F.col("card_number").alias("transaction_acid"))
    return (
        labelled.filter(
            (F.to_date("tran_date") >= floor)
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"))
        .agg(
            F.max(F.col("tran_amt").cast("double")).alias("max_payment"),
            F.count(F.lit(1)).alias("payments"),
        )
    )


def build_returns(return_events: DataFrame) -> DataFrame:
    """``events``: returned transactions per ``(cif_id, month_end, reason)`` from
    ``prm_casa_return_events`` — one event per ``(tran_id, tran_date)``, so the debit and
    credit legs of a return count once."""
    _require(
        return_events,
        ["cif_id", "tran_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    one_event = Window.partitionBy("cif_id", "tran_id", "tran_date")
    return (
        return_events.select(
            _cif(),
            "tran_id",
            F.to_date("tran_date").alias("tran_date"),
            F.trim("reason_for_excluding").alias("reason"),
        )
        .withColumn("_rn", F.row_number().over(one_event.orderBy("reason")))
        .filter(F.col("_rn") == 1)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "reason")
        .agg(F.count(F.lit(1)).alias("events"))
    )
`````

New:

`````python
"""Feature nodes: monthly CASA features per customer, all customers.

Each table has one row per ``(cif_id, month_end)`` (plus ``lane`` / ``reason`` where
named) with any data; customers are CIFs, so every CASA account of the customer counts.
The FTR-based tables keep only legs on current and savings accounts (``prm_casa_accounts``):
the transaction table also holds the loan account itself. Values are raw: which lanes,
reasons or amounts count is decided by the consumers.

* ``feat_cif_internal_salary_monthly`` — salary credited with us per month (WM);
* ``feat_cif_casa_balance_monthly``    — CASA average balance and any flow per month (WM);
* ``feat_cif_casa_activity_monthly``   — transaction legs per month and lane (FTR);
* ``feat_cif_ext_card_payment_monthly`` — payments to registered external cards (WM);
* ``feat_cif_returns_monthly``          — returned-transaction events per reason (FTR).

WM weekly tables carry ``week_number`` as ``yyyyMM0W`` (week 01–04 of the month).
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

_CASA_BALANCE = "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg"  # CA+SA, ~1 month
_CASA_IN = "ft_inflow_casa_amt_in_last_0_0_weeks_sum"
_CASA_OUT = "ft_outflow_casa_amt_in_last_0_0_weeks_sum"

# Transaction lanes (FTR row-handling reference), assigned in this order: a leg takes the
# first lane it matches.
SIGNAL_REASONS = ("DDS Rejects/Reversal", "CHEQUE RETURNS")
_FEE_TYPES = ("CHARGES", "FEES", "INTEREST PAID", "INTEREST COLLECTION")
_NOISE_REASONS = ("CHARGES", "FEES", "REVERSAL", "CANCELLED")
_GROUP_REASONS = ("SUBSIDIARIES EXCLUSION", "INTERNAL TRANSFER - LIV")
_AUTO_SAVE_CODES = ("LV95", "LV3")
_AMBIGUOUS_TYPES = ("MISCELLANEOUS", "MC/DD", "MC/DD-ISSUE", "STANDING INSTRUCTIONS")
_ECONOMIC_TYPES = (
    "INWARD REMITTANCE",
    "OUTWARD REMITTANCE",
    "INTERNAL TRANSFER - OTHERS",
    "CASH DEPOSIT",
    "CASH WITHDRAWALS",
    "INWARD CLEARING",
    "OUTWARD CLEARING",
    "BILL PAYMENTS",
)
LANES = (
    "signal",  # DDS rejects, cheque returns
    "refund",  # POS refunds (reason RETURNS)
    "card_spend",  # POS debits
    "card_payment",  # payments to the customer's own credit card
    "wash",  # transfers between the customer's own accounts, auto-save
    "fee_interest",
    "reversal",  # reversals, cancellations
    "group_internal",  # group subsidiaries, Liv
    "own_loan",  # the bank recovering the customer's own loan instalment
    "ambiguous",  # the rest of MISCELLANEOUS and the tiny instruction types
    "economic",  # remittances, transfers to others, cash, clearing, bill payments
    "unclassified",
)


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def _wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def _wm_week_date(week_number: str = "week_number") -> Column:
    """The middle of week W of the month (day 4, 11, 18 or 25): within 4 days of any
    day of that week."""
    week = F.substring(F.col(week_number).cast("string"), 7, 2).cast("int")
    return F.date_add(_wm_month(week_number), 7 * week - 4)


def _cif() -> Column:
    return F.col("cif_id").cast("string").alias("cif_id")


def build_internal_salary(wm_salary: DataFrame) -> DataFrame:
    """``salary``: the month's total of salary-flagged credits with us, recovered from
    every weekly snapshot of ``wm_fea_salary_days_since_increment`` (all history).

    Each snapshot carries the latest salary month's total and the days from the first of
    that month to the snapshot; the snapshot's week date minus those days lands within a
    few days of the first of the salary month, so it is rounded to the nearest first.
    Snapshots that see the same month collapse to its largest total.
    """
    _require(
        wm_salary,
        [
            "cif_id",
            "week_number",
            "ft_last_salary_amount",
            "ft_days_since_salary_transaction",
        ],
        "wm_fea_salary_days_since_increment",
    )
    credited = F.date_sub(
        _wm_week_date(), F.col("ft_days_since_salary_transaction").cast("int")
    )
    month = F.trunc(F.date_add(credited, 15), "month")  # nearest first of a month
    return (
        wm_salary.filter(
            (F.col("ft_last_salary_amount") > 0)
            & F.col("ft_days_since_salary_transaction").isNotNull()
        )
        .groupBy(_cif(), F.last_day(month).alias("month_end"))
        .agg(F.max(F.col("ft_last_salary_amount").cast("double")).alias("salary"))
    )


def build_casa_balance(
    wm_casa_balance: DataFrame,
    wm_casa_flow: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``casa_balance``: the 4-week CASA (current + savings) average at the month's last
    weekly snapshot; ``casa_flow``: 1 when any week of the month has an inflow or outflow.
    From the first of the last ``history_months`` months up to the persona start month on.
    """
    _require(
        wm_casa_balance,
        ["cif_id", "week_number", _CASA_BALANCE],
        "wm_fea_casa_eod_avg_balance",
    )
    _require(
        wm_casa_flow,
        ["cif_id", "week_number", _CASA_IN, _CASA_OUT],
        "wm_fea_casa_cc_inflow_outflow",
    )
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    last_week = F.max(
        F.struct(
            F.col("week_number").cast("string").alias("w"),
            F.col(_CASA_BALANCE).cast("double").alias("v"),
        )
    )
    balance = (
        wm_casa_balance.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(last_week.alias("_last"))
        .select("cif_id", "month_end", F.col("_last.v").alias("casa_balance"))
    )
    moved = (F.col(_CASA_IN) > 0) | (F.col(_CASA_OUT) > 0)
    flow = (
        wm_casa_flow.filter(_wm_month() >= floor)
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(F.max(moved.cast("int")).alias("casa_flow"))
    )
    return balance.join(flow, on=["cif_id", "month_end"], how="full")


def transaction_lane() -> Column:
    """The lane of a ``prm_casa_transactions`` leg (``LANES``).

    Signal rows first; card rows before the reason rules, because the bank's reason flag
    also marks own-card payments; then noise, own-loan recovery, ambiguous and economic
    types. Types are compared exactly, after upper-casing and collapsing spaces.
    """
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    reason = F.trim("reason_for_excluding")
    debit = F.col("tran_dc") == "D"
    narration = F.upper(F.trim("tran_narration_1"))
    noise_reason = F.coalesce(reason.isin(*_NOISE_REASONS), F.lit(False))
    return (
        F.when(reason.isin(*SIGNAL_REASONS) | (t == "CHEQUE RETURNS"), "signal")
        .when(reason == "RETURNS", "refund")
        .when((t == "POS TRANSACTIONS") & debit & ~noise_reason, "card_spend")
        .when(t == "CREDIT CARD PAYMENTS", "card_payment")
        .when(
            (t == "INTERNAL TRANSFER - SELF")
            | F.col("tran_particular_code").isin(*_AUTO_SAVE_CODES)
            | (reason == "INTERNAL TRANSFER - SELF"),
            "wash",
        )
        .when(reason.isin("CHARGES", "FEES") | t.isin(*_FEE_TYPES), "fee_interest")
        .when(reason.isin("REVERSAL", "CANCELLED") | (t == "REVERSAL"), "reversal")
        .when(
            reason.isin(*_GROUP_REASONS) | t.endswith("- SUBSIDIARIES"),
            "group_internal",
        )
        .when(
            (t == "MISCELLANEOUS") & narration.startswith("INSTL_RECOVERY"), "own_loan"
        )
        .when(t.isin(*_AMBIGUOUS_TYPES), "ambiguous")
        .when(t.isin(*_ECONOMIC_TYPES), "economic")
        .otherwise("unclassified")
    )


def _on_casa_accounts(legs: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """The legs whose ``foracid`` is a current or savings account."""
    _require(casa_accounts, ["foracid"], "prm_casa_accounts")
    accounts = casa_accounts.select("foracid").distinct()
    return legs.withColumn("foracid", F.trim(F.col("foracid").cast("string"))).join(
        accounts, on="foracid", how="leftsemi"
    )


def build_casa_activity(transactions: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, lane)``: ``legs`` and the credit / debit AED of the
    ``prm_casa_transactions`` legs on CASA accounts (its whole history)."""
    _require(
        transactions,
        [
            "cif_id",
            "foracid",
            "tran_date",
            "tran_dc",
            "tran_type",
            "reason_for_excluding",
            "tran_particular_code",
            "tran_narration_1",
            "actual_tran_amt_aed",
        ],
        "prm_casa_transactions",
    )
    amount = F.col("actual_tran_amt_aed").cast("double")
    return (
        _on_casa_accounts(transactions, casa_accounts)
        .withColumn("lane", transaction_lane())
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"), "lane")
        .agg(
            F.count(F.lit(1)).alias("legs"),
            F.sum(F.when(F.col("tran_dc") == "C", amount)).alias("credit_aed"),
            F.sum(F.when(F.col("tran_dc") == "D", amount)).alias("debit_aed"),
        )
    )


def build_ext_card_payments(
    labelled: DataFrame,
    beneficiary_cards: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``max_payment`` / ``payments``: CASA payments to a card registered as a payment
    beneficiary (``prm_beneficiary_cards``; an external card) per month, from
    ``wm_pri_labelled_transactions``.

    The beneficiary list is a current snapshot: a card registered later still counts
    (a mild look-ahead, accepted).
    """
    _require(
        labelled,
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
    _require(beneficiary_cards, ["card_number"], "prm_beneficiary_cards")
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    cards = beneficiary_cards.select(F.col("card_number").alias("transaction_acid"))
    return (
        labelled.filter(
            (F.to_date("tran_date") >= floor)
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .groupBy(_cif(), F.last_day(F.to_date("tran_date")).alias("month_end"))
        .agg(
            F.max(F.col("tran_amt").cast("double")).alias("max_payment"),
            F.count(F.lit(1)).alias("payments"),
        )
    )


def build_returns(return_events: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """``events``: returned transactions on CASA accounts per ``(cif_id, month_end,
    reason)`` from ``prm_casa_return_events`` — one event per ``(tran_id, tran_date)``, so
    the debit and credit legs of a return count once."""
    _require(
        return_events,
        ["cif_id", "foracid", "tran_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    one_event = Window.partitionBy("cif_id", "tran_id", "tran_date")
    return (
        _on_casa_accounts(return_events, casa_accounts)
        .select(
            _cif(),
            "tran_id",
            F.to_date("tran_date").alias("tran_date"),
            F.trim("reason_for_excluding").alias("reason"),
        )
        .withColumn("_rn", F.row_number().over(one_event.orderBy("reason")))
        .filter(F.col("_rn") == 1)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "reason")
        .agg(F.count(F.lit(1)).alias("events"))
    )
`````

### FILE: `src/enbd_collections/nodes/primary/casa/prm_casa.py`
action: replace · base sha256 `d081806274ad3d1f39acd1efc9948aea37e5b7cef8453fba4f56b45270a3a81a` · base trailing newline: yes · new sha256 `0221aa1d531c8c5a0a1147f6e4e12c100f518050c136cb5d36318a9c29b240e6` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Primary CASA datasets built from comp_financial_tran_repos_dly, and the registered
beneficiary cards."""

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

_TRANSACTION_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "tran_dc",
    "tran_type",
    "reason_for_excluding",
    "tran_particular_code",
    "tran_narration_1",
    "actual_tran_amt_aed",
    "edp_load_date",
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


def build_transactions(
    tran_repos: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """Every CASA transaction leg for all CIFs, one row per transaction key,
    partitioned by ``event_month``: direction, type, reason, code, first narration and
    the AED amount, as loaded. Which legs count for what is decided downstream. Same
    history and reload rule as ``build_return_events``; the NI POS sink CIF is dropped.
    """
    rows = _scoped(tran_repos, _TRANSACTION_COLUMNS, persona_start_date, history_months)
    return _latest_load(
        rows.filter(~F.col("cif_id").cast("string").isin(*_NON_CUSTOMER_CIFS))
    )


def build_beneficiary_cards(beneficiary: DataFrame) -> DataFrame:
    """Distinct card numbers registered as payment beneficiaries in online / mobile
    banking (any customer: the source carries no CIF), with the issuing institution."""
    missing = sorted(
        {"instrument_number", "instrument_type", "institution_name"}
        - set(beneficiary.columns)
    )
    if missing:
        raise ValueError(f"raw_beneficiary_cards is missing columns: {missing}")
    return (
        beneficiary.filter(
            (F.col("instrument_type") == "CARD_NUMBER")
            & F.col("instrument_number").isNotNull()
        )
        .groupBy(F.col("instrument_number").cast("string").alias("card_number"))
        .agg(F.max("institution_name").alias("institution_name"))
    )
`````

New:

`````python
"""Primary CASA datasets built from comp_financial_tran_repos_dly, the CASA accounts from
the Finacle account master, and the registered beneficiary cards."""

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

_TRANSACTION_COLUMNS = [
    *_KEY,
    "cif_id",
    "foracid",
    "tran_dc",
    "tran_type",
    "reason_for_excluding",
    "tran_particular_code",
    "tran_narration_1",
    "actual_tran_amt_aed",
    "edp_load_date",
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


def build_transactions(
    tran_repos: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """Every CASA transaction leg for all CIFs, one row per transaction key,
    partitioned by ``event_month``: direction, type, reason, code, first narration and
    the AED amount, as loaded. Which legs count for what is decided downstream. Same
    history and reload rule as ``build_return_events``; the NI POS sink CIF is dropped.
    """
    rows = _scoped(tran_repos, _TRANSACTION_COLUMNS, persona_start_date, history_months)
    return _latest_load(
        rows.filter(~F.col("cif_id").cast("string").isin(*_NON_CUSTOMER_CIFS))
    )


def build_casa_accounts(
    acid_to_cif: DataFrame,
    current_account_codes: Sequence[str],
    saving_account_codes: Sequence[str],
) -> DataFrame:
    """Current and savings accounts: distinct ``(foracid, cif_id, schm_code)`` of
    ``raw_casa_acid_to_cif`` (the Finacle account master, as WM reads it) whose scheme
    code is a current or savings code. Loans, term deposits and other schemes are left
    out; ``foracid`` is the account number of the CASA transaction tables."""
    missing = sorted({"foracid", "cif_id", "schm_code"} - set(acid_to_cif.columns))
    if missing:
        raise ValueError(f"raw_casa_acid_to_cif is missing columns: {missing}")
    codes = [*current_account_codes, *saving_account_codes]
    return (
        acid_to_cif.select(
            F.trim(F.col("foracid").cast("string")).alias("foracid"),
            F.col("cif_id").cast("string").alias("cif_id"),
            F.trim(F.col("schm_code").cast("string")).alias("schm_code"),
        )
        .filter(F.col("foracid").isNotNull() & F.col("schm_code").isin(*codes))
        .distinct()
    )


def build_beneficiary_cards(beneficiary: DataFrame) -> DataFrame:
    """Distinct card numbers registered as payment beneficiaries in online / mobile
    banking (any customer: the source carries no CIF), with the issuing institution."""
    missing = sorted(
        {"instrument_number", "instrument_type", "institution_name"}
        - set(beneficiary.columns)
    )
    if missing:
        raise ValueError(f"raw_beneficiary_cards is missing columns: {missing}")
    return (
        beneficiary.filter(
            (F.col("instrument_type") == "CARD_NUMBER")
            & F.col("instrument_number").isNotNull()
        )
        .groupBy(F.col("instrument_number").cast("string").alias("card_number"))
        .agg(F.max("institution_name").alias("institution_name"))
    )
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `4f3106c63c96d1099fb76930644bcb1924b102c368f09259e35997cb87269d13` · base trailing newline: yes · new sha256 `9922d1cc193a42c3aac025fadfc55542cb3541e799ac92cb35657ebc2b7c4f19` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 13): A4 check; removed by the bundle's cleanup.
        "crx_rl_a4_deterioration_b13_check": (
            crx_rl_a4_deterioration.create_b13_check_pipeline()
        ),
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
        # TEMPORARY (mirror bundle 14): A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_ability_b14_check": (
            crx_cc_a1_ability.create_b14_check_pipeline()
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
        # TEMPORARY (mirror bundle 14): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b14_check": (
            crx_rl_a1_ability.create_b14_check_pipeline()
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

### FILE: `src/enbd_collections/pipelines/casa/features.py`
action: replace · base sha256 `15702e1f037847b6e37792d4b00d0c5641c8aecf612e42979700e304bdda8433` · base trailing newline: yes · new sha256 `eaa95c898351d153353e3be548e122267ec5c6aa3fe8e0214b5778e4fef5beb3` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CASA feature pipeline: monthly CASA features per customer (per model_id).

    wm_fea_salary_days_since_increment ──────────────────► feat_cif_internal_salary_monthly
    wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow ► feat_cif_casa_balance_monthly
    prm_casa_transactions ───────────────────────────────► feat_cif_casa_activity_monthly
    wm_pri_labelled_transactions, prm_beneficiary_cards ─► feat_cif_ext_card_payment_monthly
    prm_casa_return_events ──────────────────────────────► feat_cif_returns_monthly

Needs ``casa_primary`` for the model_id first.

    kedro run --pipeline=casa_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_casa


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The five monthly CASA feature tables."""
    tags = ["casa", "features"]
    window = {
        "persona_start_date": "params:crx_persona.persona_start_date",
        "history_months": "params:casa_features.history_months",
    }
    return Pipeline(
        [
            node(
                func=feat_cif_casa.build_internal_salary,
                inputs={"wm_salary": "wm_fea_salary_days_since_increment"},
                outputs="feat_cif_internal_salary_monthly",
                name="build_feat_cif_internal_salary_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_balance,
                inputs={
                    "wm_casa_balance": "wm_fea_casa_eod_avg_balance",
                    "wm_casa_flow": "wm_fea_casa_cc_inflow_outflow",
                    **window,
                },
                outputs="feat_cif_casa_balance_monthly",
                name="build_feat_cif_casa_balance_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_activity,
                inputs={"transactions": "prm_casa_transactions"},
                outputs="feat_cif_casa_activity_monthly",
                name="build_feat_cif_casa_activity_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_ext_card_payments,
                inputs={
                    "labelled": "wm_pri_labelled_transactions",
                    "beneficiary_cards": "prm_beneficiary_cards",
                    **window,
                },
                outputs="feat_cif_ext_card_payment_monthly",
                name="build_feat_cif_ext_card_payment_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_returns,
                inputs={"return_events": "prm_casa_return_events"},
                outputs="feat_cif_returns_monthly",
                name="build_feat_cif_returns_monthly",
                tags=tags,
            ),
        ]
    )
`````

New:

`````python
"""CASA feature pipeline: monthly CASA features per customer (per model_id).

    wm_fea_salary_days_since_increment ──────────────────► feat_cif_internal_salary_monthly
    wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow ► feat_cif_casa_balance_monthly
    prm_casa_transactions, prm_casa_accounts ────────────► feat_cif_casa_activity_monthly
    wm_pri_labelled_transactions, prm_beneficiary_cards ─► feat_cif_ext_card_payment_monthly
    prm_casa_return_events, prm_casa_accounts ───────────► feat_cif_returns_monthly

Needs ``casa_primary`` for the model_id first.

    kedro run --pipeline=casa_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_casa


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The five monthly CASA feature tables."""
    tags = ["casa", "features"]
    window = {
        "persona_start_date": "params:crx_persona.persona_start_date",
        "history_months": "params:casa_features.history_months",
    }
    return Pipeline(
        [
            node(
                func=feat_cif_casa.build_internal_salary,
                inputs={"wm_salary": "wm_fea_salary_days_since_increment"},
                outputs="feat_cif_internal_salary_monthly",
                name="build_feat_cif_internal_salary_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_balance,
                inputs={
                    "wm_casa_balance": "wm_fea_casa_eod_avg_balance",
                    "wm_casa_flow": "wm_fea_casa_cc_inflow_outflow",
                    **window,
                },
                outputs="feat_cif_casa_balance_monthly",
                name="build_feat_cif_casa_balance_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_casa_activity,
                inputs={
                    "transactions": "prm_casa_transactions",
                    "casa_accounts": "prm_casa_accounts",
                },
                outputs="feat_cif_casa_activity_monthly",
                name="build_feat_cif_casa_activity_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_ext_card_payments,
                inputs={
                    "labelled": "wm_pri_labelled_transactions",
                    "beneficiary_cards": "prm_beneficiary_cards",
                    **window,
                },
                outputs="feat_cif_ext_card_payment_monthly",
                name="build_feat_cif_ext_card_payment_monthly",
                tags=tags,
            ),
            node(
                func=feat_cif_casa.build_returns,
                inputs={
                    "return_events": "prm_casa_return_events",
                    "casa_accounts": "prm_casa_accounts",
                },
                outputs="feat_cif_returns_monthly",
                name="build_feat_cif_returns_monthly",
                tags=tags,
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/casa/primary.py`
action: replace · base sha256 `30ce9bbd30eb13e99dd4ab70de4fd3b2ab2961aed2418bd61ab99cff27f33c39` · base trailing newline: yes · new sha256 `a9ca0fe048628ce25fe9dca8d2d950f964a9e320d8fea8661ccd8db25c6da45e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CASA primary pipeline.

kedro run --pipeline=casa_primary   (per model_id)
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.casa.prm_casa import (
    build_beneficiary_cards,
    build_card_transactions,
    build_return_events,
    build_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events, prm_casa_card_transactions and prm_casa_transactions from
    comp_financial_tran_repos_dly; prm_beneficiary_cards from raw_beneficiary_cards."""
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
            node(
                func=build_transactions,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.transaction_history_months",
                ],
                outputs="prm_casa_transactions",
                name="build_prm_casa_transactions",
                tags=["casa", "primary"],
            ),
            node(
                func=build_beneficiary_cards,
                inputs="raw_beneficiary_cards",
                outputs="prm_beneficiary_cards",
                name="build_prm_beneficiary_cards",
                tags=["casa", "primary"],
            ),
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
    build_beneficiary_cards,
    build_card_transactions,
    build_casa_accounts,
    build_return_events,
    build_transactions,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_casa_return_events, prm_casa_card_transactions and prm_casa_transactions from
    comp_financial_tran_repos_dly; prm_casa_accounts from raw_casa_acid_to_cif;
    prm_beneficiary_cards from raw_beneficiary_cards."""
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
            node(
                func=build_transactions,
                inputs=[
                    "comp_financial_tran_repos_dly",
                    "params:crx_persona.persona_start_date",
                    "params:casa_primary.transaction_history_months",
                ],
                outputs="prm_casa_transactions",
                name="build_prm_casa_transactions",
                tags=["casa", "primary"],
            ),
            node(
                func=build_casa_accounts,
                inputs=[
                    "raw_casa_acid_to_cif",
                    "params:casa_primary.current_account_codes",
                    "params:casa_primary.saving_account_codes",
                ],
                outputs="prm_casa_accounts",
                name="build_prm_casa_accounts",
                tags=["casa", "primary"],
            ),
            node(
                func=build_beneficiary_cards,
                inputs="raw_beneficiary_cards",
                outputs="prm_beneficiary_cards",
                name="build_prm_beneficiary_cards",
                tags=["casa", "primary"],
            ),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/b14_check.py`
action: add · new sha256 `7ad435e04a4e3a6b20edc5ac8f32634601af5d28e536376aaa641ee1862c4f43` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 14): the A1 check of CASA accounts and bounce dates, in PROD.

Log blocks, aggregates only, latest observation month:

* ``compare_a1_outputs`` (``B14 OUTPUT``): states old (``crx_<p>_a1_ability``, the output
  before this bundle) × new, by product, and why rows moved (Unknown reason, distress).
* ``describe_a1_accounts`` (``B14 ACCOUNTS``): the base CIFs' legs of the last 12 months by
  account length × scheme class (current / savings / other scheme / no scheme), the top
  other schemes, and the CIFs left with no CASA leg.
* ``describe_a1_bounces`` (``B14 BOUNCES``): bureau bounce events by the pull rule (before)
  and by the return date (S15), CIF-months and rows with a bounce in the window.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from .._common import GRAIN, window_agg, window_months

LOG = logging.getLogger(__name__)


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B14 {name} START === [{model_id}]",
        *lines,
        f"=== B14 {name} END ===",
    ]
    LOG.info("\n%s", "\n".join(block))


def _table(df: DataFrame, *cols: str) -> list[str]:
    """Counts by ``cols`` with the share of all rows; under 10 shown as ``<10``."""
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    total = sum(r["count"] for r in rows) or 1
    return [
        "  "
        + " x ".join(f"{r[c]!s:<22}" for c in cols)
        + f" {r['count'] if r['count'] >= 10 else '<10':>9}"
        + f"  {100.0 * r['count'] / total:5.1f}%"
        for r in rows
    ]


def _latest(df: DataFrame) -> DataFrame:
    last = df.agg(F.max("observation_date")).first()[0]
    return df.filter(F.col("observation_date") == F.lit(last))


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


def _cifs(obs_base: DataFrame) -> DataFrame:
    return (
        _latest(obs_base)
        .filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
    )


# ── B14 OUTPUT ────────────────────────────────────────────────────────────────


def compare_a1_outputs(
    old: DataFrame, new: DataFrame, products: DataFrame, model_id: str
) -> None:
    """Latest month: old × new state, by product, and the reason behind each move."""
    latest = _latest(new)
    month = latest.agg(F.max("observation_date")).first()[0]
    cols = ["a1_state", "a1_unknown_reason", "a1_distress_flag"]
    old_m = old.filter(F.col("observation_date") == F.lit(month)).select(
        F.col("account_id").cast("string").alias("account_id"),
        *[F.col(c).alias(f"old_{c}") for c in cols],
    )
    both = _product(latest, products).join(old_m, on="account_id", how="inner")
    moved = both.filter(F.col("old_a1_state") != F.col("a1_state")).withColumn(
        "why",
        F.when(
            F.col("old_a1_distress_flag") != F.col("a1_distress_flag"), "distress"
        ).otherwise(F.coalesce("a1_unknown_reason", F.lit("gate_opened"))),
    )
    lines = [
        (
            f"month {month}: new {latest.count()} rows, old {old_m.count()}, "
            f"matched {both.count()}"
        ),
        "new a1_state:",
        *_table(latest, "a1_state"),
        "new a1_state by product:",
        *_table(both, "loan_type", "a1_state"),
        "old x new a1_state:",
        *_table(both, "old_a1_state", "a1_state"),
        "moved rows: old x new x why (distress changed / new Unknown reason):",
        *_table(moved, "old_a1_state", "a1_state", "why"),
        "a1_unknown_reason old x new (Unknown rows):",
        *_table(
            both.filter(F.col("a1_state") == "unknown").fillna(
                "not_unknown", subset=["old_a1_unknown_reason"]
            ),
            "old_a1_unknown_reason",
            "a1_unknown_reason",
        ),
        "a1_unknown_reason by product (new):",
        *_table(
            both.filter(F.col("a1_state") == "unknown"),
            "loan_type",
            "a1_unknown_reason",
        ),
        "a1_distress_flag old x new:",
        *_table(both, "old_a1_distress_flag", "a1_distress_flag"),
    ]
    _log("OUTPUT", model_id, lines)


# ── B14 ACCOUNTS ──────────────────────────────────────────────────────────────


def describe_a1_accounts(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    transactions: DataFrame,
    acid_to_cif: DataFrame,
    current_account_codes: Sequence[str],
    saving_account_codes: Sequence[str],
    casa_activity: DataFrame,
    model_id: str,
) -> None:
    """Legs of the latest month's CIFs by account length × scheme class, the top other
    schemes, and the CIFs with no CASA leg in 12 months."""
    cifs = _cifs(obs_base)
    schemes = acid_to_cif.select(
        F.trim(F.col("foracid").cast("string")).alias("foracid"),
        F.trim(F.col("schm_code").cast("string")).alias("schm_code"),
    ).dropDuplicates(["foracid"])
    last = transactions.agg(F.max("tran_date")).first()[0]
    legs = (
        transactions.withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(cifs, on="cif_id", how="leftsemi")
        .filter(F.col("tran_date") > F.add_months(F.lit(last), -12))
        .withColumn("foracid", F.trim(F.col("foracid").cast("string")))
        .join(schemes, on="foracid", how="left")
        .withColumn("length", F.length("foracid"))
        .withColumn(
            "scheme_class",
            F.when(F.col("schm_code").isin(*current_account_codes), "current")
            .when(F.col("schm_code").isin(*saving_account_codes), "savings")
            .when(F.col("schm_code").isNotNull(), "other_scheme")
            .otherwise("no_scheme"),
        )
    )
    by_class = (
        legs.groupBy("length", "scheme_class")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy("length", "scheme_class")
        .collect()
    )
    top = (
        legs.filter(F.col("scheme_class") == "other_scheme")
        .groupBy("schm_code")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy(F.desc("legs"))
        .limit(10)
        .collect()
    )
    with_casa = (
        casa_activity.withColumn("cif_id", F.col("cif_id").cast("string"))
        .filter(F.col("month_end") > F.add_months(F.lit(last), -12))
        .select("cif_id")
        .distinct()
    )
    n_cifs = cifs.count()
    n_casa = cifs.join(with_casa, on="cif_id", how="leftsemi").count()
    lines = [
        f"{n_cifs} base CIFs; legs since {last} minus 12 months",
        "length x scheme_class: legs, CIFs",
        *[
            f"  {r['length']!s:<4} {r['scheme_class']:<13} {r['legs']:>10} {r['cifs']:>8}"
            for r in by_class
        ],
        "top other schemes: schm_code, legs, CIFs",
        *[f"  {r['schm_code']:<8} {r['legs']:>10} {r['cifs']:>8}" for r in top],
        (
            f"CIFs with a CASA leg (new feat_cif_casa_activity_monthly) in 12 months: "
            f"{n_casa} ({100.0 * n_casa / max(n_cifs, 1):.1f}%)"
        ),
    ]
    _log("ACCOUNTS", model_id, lines)


# ── B14 BOUNCES ───────────────────────────────────────────────────────────────


def _pull_rule(alerts: DataFrame) -> DataFrame:
    """Bounce events by the rule before S15: per (cif, contract type, description), a
    pull whose bounced amount differs from the key's previous pull, dated by the pull.
    """
    key = ["cif_id", "contract_type", "alert_description"]
    pulls = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(
            F.col("cif_id").cast("string").alias("cif_id"),
            "contract_type",
            "alert_description",
            F.to_date("extract_date").alias("pull_date"),
            F.coalesce(F.col("bounced_cheque_amount").cast("double"), F.lit(0.0)).alias(
                "amount"
            ),
        )
        .groupBy(*key, "pull_date")
        .agg(F.max("amount").alias("amount"))
    )
    previous = F.lag("amount").over(Window.partitionBy(*key).orderBy("pull_date"))
    new = (F.col("amount") > 0) & (F.coalesce(previous, F.lit(0.0)) != F.col("amount"))
    return (
        pulls.filter(new)
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(F.count(F.lit(1)).alias("bounce_events"))
    )


def describe_a1_bounces(
    obs_base: DataFrame, alerts: DataFrame, bureau_bounces: DataFrame, model_id: str
) -> None:
    """Bureau bounce events, pull rule against return date: CIF-months, and the latest
    month's rows with a bounce in the window under each."""
    old = _pull_rule(alerts)
    new = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        F.col("cif_id").cast("string").alias("cif_id"), "month_end", "bounce_events"
    )
    months = (
        old.select("cif_id", "month_end")
        .withColumn("old", F.lit(1))
        .join(
            new.select("cif_id", "month_end").withColumn("new", F.lit(1)),
            on=["cif_id", "month_end"],
            how="full",
        )
    )
    obs = _latest(obs_base).filter(F.col("cif_id").isNotNull())
    obs = obs.withColumn("cif_id", F.col("cif_id").cast("string"))
    w = window_months(model_id)

    def flag(series: DataFrame, name: str) -> DataFrame:
        return window_agg(
            obs,
            series,
            date_col="month_end",
            aggs=[F.max(F.lit(1)).alias(name)],
            months=w,
        )

    rows = (
        obs.select(*GRAIN)
        .join(flag(old, "old"), on=list(GRAIN), how="left")
        .join(flag(new, "new"), on=list(GRAIN), how="left")
        .fillna(0, subset=["old", "new"])
    )
    lag = alerts.filter(
        (F.col("bounced_cheque_amount").cast("double") > 0)
        & F.col("dt_of_return").isNotNull()
    ).select(
        F.datediff(F.to_date("extract_date"), F.to_date("dt_of_return")).alias("days")
    )
    q = lag.approxQuantile("days", [0.5, 0.75, 0.95], 0.01)
    lines = [
        (
            f"events: pull rule {old.agg(F.sum('bounce_events')).first()[0]}, "
            f"return date {new.agg(F.sum('bounce_events')).first()[0]}"
        ),
        "CIF-months with an event: old x new",
        *_table(months.fillna(0, subset=["old", "new"]), "old", "new"),
        f"latest-month rows with a bureau bounce in the {w}-month window: old x new",
        *_table(rows, "old", "new"),
        f"extract minus return date, days: p50 / p75 / p95 = {q}",
    ]
    _log("BOUNCES", model_id, lines)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: replace · base sha256 `9c07d473b7675cc9452834d883ae946767bb02f81309f38cb33d143658f7d2f6` · base trailing newline: yes · new sha256 `283108710b72383e09b9e8b9d8ac5e22a1b6898f89579bbe57d3ca97e455b185` · new trailing newline: yes

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

TEMPORARY (mirror bundle 14): ``create_b14_check_pipeline`` runs the observation base and
the same nodes, writes the axis to ``crx_<p>_a1_ability_b14_check`` and logs the check
tables (``b14_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b14_check import compare_a1_outputs, describe_a1_accounts, describe_a1_bounces
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


def create_b14_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_<p>_a1_ability_b14_check + the log-only check nodes.
    Remove with b14_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    check = f"{prefix}_ability_b14_check"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a1_outputs,
            inputs={
                "old": f"{prefix}_ability",
                "new": check,
                "products": "rl_spine" if product == "rl" else obs,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"compare_{prefix}_b14",
            tags=tags,
        ),
        node(
            func=describe_a1_accounts,
            inputs={
                "obs_base": obs,
                "transactions": "prm_casa_transactions",
                "acid_to_cif": "raw_casa_acid_to_cif",
                "current_account_codes": "params:casa_primary.current_account_codes",
                "saving_account_codes": "params:casa_primary.saving_account_codes",
                "casa_activity": "feat_cif_casa_activity_monthly",
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b14_accounts",
            tags=tags,
        ),
        node(
            func=describe_a1_bounces,
            inputs={
                "obs_base": obs,
                "alerts": "prm_bureau_alert_enriched",
                "bureau_bounces": "feat_cif_bureau_bounces_monthly",
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b14_bounces",
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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `1c9809d6770a387d243def17d23081d274810aa48e80a6f3a773693c62409341` · base trailing newline: yes · new sha256 `c7cedcac01c10b3cbb1f4d870427fabb6fd73622fd2e1649c595fecc6d6b3e8a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary in each month: the larger of the internal credit and the bureau
              salary, a pull counting in its own month and the next (S14);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — customer-initiated CASA movement in the window (the Unknown gate) and
              whether the customer holds a CASA with us at all;
* distress  — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
              the window;
* EOSB      — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
# feat_cif_casa_activity_monthly lanes that are money the customer moved (S11): third-
# party credits, transfers to others, cash, clearing, bill payments, card spend and
# paying their own credit card. Not: own-account wash, the bank recovering the
# customer's loan instalment, fees, interest, reversals, returns, group-internal and
# ambiguous rows.
CUSTOMER_LANES = ("economic", "card_spend", "card_payment")
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month_end, value)`` series over ``{prefix}_m1 …
    _m{months}`` per observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series.select("cif_id", "month_end", value), on="cif_id")
        .withColumn("_k", _month_index(F.col("month_end")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = _cifs(obs_base).select("account_id", "cif_id").distinct()
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.last_day(F.to_date("aecb_bureau_pull_date")).alias("month_end"),
            F.col("aecb_last_salary_credit_amount")
            .cast("double")
            .alias("bureau_salary"),
        )
        .filter(F.col("month_end").isNotNull() & (F.col("bureau_salary") > 0))
        .join(cifs, on="account_id")
        .select("cif_id", "month_end", "bureau_salary")
    )


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each pull's month, and the month
    after it unless that month has its own pull (never before a pull; pulls every 2
    months make a continuous series). A pull of 0 (salary account closed) ends the carry.
    """
    pulls = bureau.groupBy("cif_id", "month_end").agg(
        F.max("bureau_salary").alias("bureau_salary")
    )
    carried = pulls.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        F.col("bureau_salary").alias("_carried"),
    )
    return pulls.join(carried, on=["cif_id", "month_end"], how="full").select(
        "cif_id",
        "month_end",
        F.coalesce("bureau_salary", "_carried").alias("bureau_salary"),
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal salary (``feat_cif_internal_salary_monthly``) and the bureau salary
    (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no salary that
    month. Also the largest month per source: ``internal_salary_w`` / ``bureau_salary_w`` in
    the window, ``internal_salary_prior`` in the prior window.

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit("int").alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit("bur").alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    monthly = sources.groupBy("cif_id", "month_end").agg(
        F.max("amount").alias("amount")
    )
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == "int"
    return left_join_all(
        obs_base,
        [
            _by_month(obs, monthly, "amount", "income", 2 * w),
            _in_window(
                obs,
                sources,
                2 * w,
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            ),
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def build_liquidity_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (largest single payment to an external card in W),
    ``casa_active`` (1: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (1: any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months)."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        ext_card_payments,
        ["cif_id", "month_end", "max_payment"],
        "feat_cif_ext_card_payment_monthly",
    )
    require_columns(
        casa_activity,
        ["cif_id", "month_end", "lane", "legs"],
        "feat_cif_casa_activity_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    customer = casa_activity.filter(F.col("lane").isin(*CUSTOMER_LANES))
    held = casa_activity.select("cif_id", "month_end").unionByName(
        casa_balance.filter(F.col("casa_balance") > 0).select("cif_id", "month_end")
    )
    return left_join_all(
        obs_base,
        [
            _by_month(obs, casa_balance, "casa_balance", "casa", 2 * w),
            _in_window(
                obs,
                ext_card_payments,
                w,
                F.max("max_payment").alias("ext_card_payment_max"),
            ),
            _in_window(obs, customer, w, F.max(F.lit(1)).alias("casa_active")),
            _in_window(obs, held, CASA_HELD_MONTHS, F.max(F.lit(1)).alias("casa_held")),
        ],
    ).fillna(0, subset=["casa_active", "casa_held"])


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a new bureau-reported bounce (``feat_cif_bureau_bounces_monthly``
      ``bounce_events``; a bounce repeated unchanged in later pulls counts once);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )

    def flag(reason: str) -> Column:
        return F.max((F.col("reason") == reason).cast("int"))

    events = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        "cif_id", "month_end", F.lit("BUREAU").alias("reason")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit("BUREAU").alias("reason"),
            )
        )
    events = events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN) & (F.col("events") > 0)
        ).select("cif_id", "month_end", "reason")
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    hits = _in_window(
        obs,
        events,
        w,
        flag(CHEQUE_RETURN).alias("distress_cheque"),
        flag(DDS_RETURN).alias("distress_dds"),
        flag("BUREAU").alias("distress_bureau"),
    )
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag``: 1 when a DCORE result on any of the customer's agreements names an
    end-of-service benefit (EOSB expected / awaited / received) in the window. A
    diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary in each month: the larger of the internal credit and the bureau
              salary, a pull counting in its own month and the next (S14);
* liquidity — CASA average balance in each month, largest single external card payment;
* activity  — customer-initiated CASA movement in the window (the Unknown gate) and
              whether the customer holds a CASA with us at all;
* distress  — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
              the window;
* EOSB      — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
# feat_cif_casa_activity_monthly lanes that are money the customer moved (S11): third-
# party credits, transfers to others, cash, clearing, bill payments, card spend and
# paying their own credit card. Not: own-account wash, the bank recovering the
# customer's loan instalment, fees, interest, reversals, returns, group-internal and
# ambiguous rows.
CUSTOMER_LANES = ("economic", "card_spend", "card_payment")
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(
    obs: DataFrame, series: DataFrame, value: str, prefix: str, months: int
) -> DataFrame:
    """Spread a ``(cif_id, month_end, value)`` series over ``{prefix}_m1 …
    _m{months}`` per observation (NULL where the month has no value)."""
    return (
        obs.select(*GRAIN, "cif_id")
        .join(series.select("cif_id", "month_end", value), on="cif_id")
        .withColumn("_k", _month_index(F.col("month_end")))
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col(value))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _in_window(obs: DataFrame, series: DataFrame, months: int, *aggs) -> DataFrame:
    """``aggs`` over the ``(cif_id, month_end, …)`` rows of the last ``months`` months."""
    return window_agg(obs, series, date_col="month_end", aggs=list(aggs), months=months)


# ── Income ────────────────────────────────────────────────────────────────────


def _loan_bureau_salary(obs_base: DataFrame, loan_features: DataFrame) -> DataFrame:
    """RL: the last salary credit reported by each loan's latest bureau pull
    (``feature_retail_loans``, one row per spine row), dated by the pull month.

    Pulls are rare (most accounts have one), so this rarely falls in the window.
    """
    require_columns(
        loan_features,
        ["account_id", "aecb_bureau_pull_date", "aecb_last_salary_credit_amount"],
        "feature_retail_loans",
    )
    cifs = _cifs(obs_base).select("account_id", "cif_id").distinct()
    return (
        loan_features.select(
            F.col("account_id").cast("string").alias("account_id"),
            F.last_day(F.to_date("aecb_bureau_pull_date")).alias("month_end"),
            F.col("aecb_last_salary_credit_amount")
            .cast("double")
            .alias("bureau_salary"),
        )
        .filter(F.col("month_end").isNotNull() & (F.col("bureau_salary") > 0))
        .join(cifs, on="account_id")
        .select("cif_id", "month_end", "bureau_salary")
    )


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each pull's month, and the month
    after it unless that month has its own pull (never before a pull; pulls every 2
    months make a continuous series). A pull of 0 (salary account closed) ends the carry.
    """
    pulls = bureau.groupBy("cif_id", "month_end").agg(
        F.max("bureau_salary").alias("bureau_salary")
    )
    carried = pulls.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        F.col("bureau_salary").alias("_carried"),
    )
    return pulls.join(carried, on=["cif_id", "month_end"], how="full").select(
        "cif_id",
        "month_end",
        F.coalesce("bureau_salary", "_carried").alias("bureau_salary"),
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal salary (``feat_cif_internal_salary_monthly``) and the bureau salary
    (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no salary that
    month. Also the largest month per source: ``internal_salary_w`` / ``bureau_salary_w`` in
    the window, ``internal_salary_prior`` in the prior window.

    ``loan_features`` (RL only): ``feature_retail_loans``, whose latest-pull bureau salary
    joins the bureau salary.
    """
    require_columns(
        internal_salary,
        ["cif_id", "month_end", "salary"],
        "feat_cif_internal_salary_monthly",
    )
    require_columns(
        bureau_salary,
        ["cif_id", "month_end", "bureau_salary"],
        "feat_cif_bureau_salary_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, 2 * w)
    internal = internal_salary.select(
        "cif_id",
        "month_end",
        F.col("salary").alias("amount"),
        F.lit("int").alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit("bur").alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    monthly = sources.groupBy("cif_id", "month_end").agg(
        F.max("amount").alias("amount")
    )
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == "int"
    return left_join_all(
        obs_base,
        [
            _by_month(obs, monthly, "amount", "income", 2 * w),
            _in_window(
                obs,
                sources,
                2 * w,
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            ),
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def build_liquidity_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (largest single payment to an external card in W),
    ``casa_active`` (1: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (1: any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months)."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        ext_card_payments,
        ["cif_id", "month_end", "max_payment"],
        "feat_cif_ext_card_payment_monthly",
    )
    require_columns(
        casa_activity,
        ["cif_id", "month_end", "lane", "legs"],
        "feat_cif_casa_activity_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    customer = casa_activity.filter(F.col("lane").isin(*CUSTOMER_LANES))
    held = casa_activity.select("cif_id", "month_end").unionByName(
        casa_balance.filter(F.col("casa_balance") > 0).select("cif_id", "month_end")
    )
    return left_join_all(
        obs_base,
        [
            _by_month(obs, casa_balance, "casa_balance", "casa", 2 * w),
            _in_window(
                obs,
                ext_card_payments,
                w,
                F.max("max_payment").alias("ext_card_payment_max"),
            ),
            _in_window(obs, customer, w, F.max(F.lit(1)).alias("casa_active")),
            _in_window(obs, held, CASA_HELD_MONTHS, F.max(F.lit(1)).alias("casa_held")),
        ],
    ).fillna(0, subset=["casa_active", "casa_held"])


# ── Distress ──────────────────────────────────────────────────────────────────


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``);
    * ``payment_order`` — prm_bureau_payment_order returns; not in PROD yet.

    Stops the run when the returns table starts after the earliest observation's window
    (it follows ``crx_persona.persona_start_date``; rebuilt for an older one otherwise).
    """
    require_columns(
        returns, ["cif_id", "month_end", "reason", "events"], "feat_cif_returns_monthly"
    )
    require_columns(
        bureau_bounces,
        ["cif_id", "month_end", "bounce_events"],
        "feat_cif_bureau_bounces_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    since = lookback_floor(obs, w)
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )

    def flag(reason: str) -> Column:
        return F.max((F.col("reason") == reason).cast("int"))

    events = bureau_bounces.filter(F.col("bounce_events") > 0).select(
        "cif_id", "month_end", F.lit("BUREAU").alias("reason")
    )
    if payment_order is not None:
        require_columns(
            payment_order,
            ["cif_id", "return_date", "reason_code"],
            "prm_bureau_payment_order",
        )
        events = events.unionByName(
            payment_order.filter(F.col("reason_code").isNotNull()).select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.last_day(F.to_date("return_date")).alias("month_end"),
                F.lit("BUREAU").alias("reason"),
            )
        )
    events = events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN) & (F.col("events") > 0)
        ).select("cif_id", "month_end", "reason")
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    hits = _in_window(
        obs,
        events,
        w,
        flag(CHEQUE_RETURN).alias("distress_cheque"),
        flag(DDS_RETURN).alias("distress_dds"),
        flag("BUREAU").alias("distress_bureau"),
    )
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag``: 1 when a DCORE result on any of the customer's agreements names an
    end-of-service benefit (EOSB expected / awaited / received) in the window. A
    diagnostic only: it changes no level or state."""
    require_columns(
        followup,
        ["agreement_id", "action_ts", "result_name"],
        "dcore_prm_followup_outcomes",
    )
    require_columns(
        agreements, ["agreement_id", "cif_id"], "prm_dcore_account_agreements"
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    notes = (
        followup.filter(F.upper(F.col("result_name")).contains(EOSB))
        .select(
            F.col("agreement_id").cast("string").alias("agreement_id"),
            F.to_date("action_ts").alias("day"),
        )
        .join(
            agreements.select(
                F.col("agreement_id").cast("string").alias("agreement_id"),
                F.col("cif_id").cast("string").alias("cif_id"),
            ).distinct(),
            on="agreement_id",
        )
        .filter(F.col("day") >= F.lit(lookback_floor(obs, w)))
    )
    hits = window_agg(
        obs, notes, date_col="day", aggs=[F.max(F.lit(1)).alias("eosb_flag")], months=w
    )
    return left_join_all(obs_base, [hits]).fillna(0, subset=["eosb_flag"])
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py`
action: replace · base sha256 `628cbd7062a01853872310fe7d00b2f35d3d1b52364696fd7ac73fdd227cdb3f` · base trailing newline: yes · new sha256 `d78b901663f93f977f3414ca303546648919f5bebf61a040ff2d5b80a1931598` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b14_check_pipeline, create_pipeline

__all__ = ["create_b14_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py`
action: replace · base sha256 `3b7794898148e38b8d2db58ffce7ad97edbdf4eecce57ea7e00028c69e2e5d2a` · base trailing newline: yes · new sha256 `83f13219db68396425e92e72a073264d0c5e43b5e0b40d25de4a41ef70564edb` · new trailing newline: yes

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

TEMPORARY (mirror bundle 14): ``create_b14_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b14_check_pipeline as _b14_check
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


def create_b14_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the CC A1 check (bundle 14)."""
    return _b14_check("cc", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py`
action: replace · base sha256 `d9c80826be5a36b98e8049bfebe1ad3ddd5b7e7732d9623a954273b03bfed837` · base trailing newline: yes · new sha256 `5d2e8657e9a3df7fefe6bbf6febbd7e6f3bd33d7c9b290e62d034663206302b0` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b14_check_pipeline, create_pipeline

__all__ = ["create_b14_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `33cb4afb5c48b02907cf0ce9b207009601af5f4b5b0578212d89345815cc4ab3` · base trailing newline: yes · new sha256 `5ff910766f9975ac7caa0cb36e6e331bc7f898c104beb8a52d8a9b2f0fac00e8` · new trailing newline: yes

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

TEMPORARY (mirror bundle 14): ``create_b14_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b14_check_pipeline as _b14_check
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


def create_b14_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the RL A1 check (bundle 14)."""
    return _b14_check("rl", _ANCHOR)
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
Clean up after mirror bundle 14_a1_casa_accounts_bounce_date.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve these catalog paths from the
  workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, once for
  every model_id the check ran for:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b14_check`;
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b14_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundle 14):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_cc_a1_ability_b14_check` and
    `crx_rl_a1_ability_b14_check` entries and their TEMPORARY comments;
  - `src/enbd_collections/pipeline_registry.py`: the two `*_a1_ability_b14_check` entries and their
    comments;
  - `crx_persona/a1_ability/pipeline.py`: `create_b14_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b14_check`, and the TEMPORARY paragraph of
    the module docstring;
  - `crx_persona/cc_a1_ability/` and `rl_a1_ability/`: `create_b14_check_pipeline` in `pipeline.py`
    (with its import and the TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete `crx_persona/a1_ability/b14_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "b14" src conf` prints nothing.
- **Delete the bundle folder** `data/input/mirror_bundles/` (the bundle file and the apply script):
  `rm -rf data/input/mirror_bundles`
- **Finish.** Run `git status`: only the files named above may have changed, and nothing under
  `data/input/` may be tracked or staged. Commit `src/` and `conf/` and push. Report what you removed
  and the hdfs commands the user still has to run in PROD.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
