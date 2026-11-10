# Mirror bundle 21 — A1 — evidence-family rule: money in or held (CASA balance included), money out, cross-product; High = two strong families

apply_bundle version: 7 · built 2026-11-10 from `8f9d69e..b159b5b` · source: 5 added, 14 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/21_a1_evidence_family_rule.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '21_a1_evidence_family_rule.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/21_a1_evidence_family_rule.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go. The round-3 code in `tmp_validation/a1_family_redesign/` (snippet, `flow_dictionary_<model_id>.md`) is the reference for every item; keep the bundle's names, signatures and output columns.

1. **Cross-product feature.** Implement `nodes/features/products/feat_cif_cross_product.build` from the round-3 F4 builder (with the other cards of R3), exactly to the module's contract (`COLUMNS`, one row per `(cif_id, month_end, product_account_id)`, `product_account_id` = the persona spines' `account_id` so the scored account can be left out; supplementary cards are not products; no CASA balances). Set the card-balance and WM-asset dataset names in `pipelines/products/features.py` to the catalog entries the snippet loaded; fail loud on missing columns.
2. **WM labels.** In `feat_cif_casa.py`, set `WM_SELF_COLUMN` / `WM_SELF_VALUE` to the column and value the snippet used for WM "self" (own account at another bank), and confirm `prm_casa_transactions` and `wm_pri_labelled_transactions` both carry `tran_id` (the round-3 join on `cif_id, tran_id, tran_date`).
3. **Class table against the dictionary.** Compare `flow_class()` with the class of every `flow_dictionary_<model_id>.md` combination (60_180, both products). Report each combination where they differ (combination, both classes, legs, AED). Change `flow_class()` only where the dictionary is explicit and the bundle has no rule for it; never change these user decisions: cash deposits count, own-account transfers with other banks count both ways, `MISCELLANEOUS` / cheque stems never count. List what you changed.
4. **Outcomes in the check.** Implement `cohort_outcome_lines` in `a1_ability/check.py` with the round-3 outcome definitions (same cohort, `cure_3` / `pay_any_3` / `roll_3`, raw and DPD-band standardised, 95% intervals, n per state), adding the datasets it needs as inputs of the `compare_a1` node. Aggregates only.
5. **Catalog and tests.** `crx_<p>_a1_casa_signals`, `crx_<p>_a1_cross_product_signals`, `crx_<p>_a1_check_new`, `feat_cif_casa_flows_monthly`, `feat_cif_cross_product_monthly` exist exactly once; list every top-level key the apply removed from `catalog_crx.yml` / `catalog_casa.yml` compared with the last commit and put back any that is not `crx_<p>_a1_liquidity_signals`. Update the A1 tests for the new signal builders and levels (the mirror's `workplace_mirror/checks/a1_engine_spec.py` has 92 cases); drop the liquidity tests.

Then check: `kedro registry list` lists `product_features`, `crx_cc_a1_check` and `crx_rl_a1_check`.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: evidence-family rule (bundle 21)" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/21_a1_evidence_family_rule.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

Today's real `crx_<p>_a1_ability` (bundle 14 rule) is the baseline: do not re-run A1 before the check. Run for **all four model_ids** (`cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus`; set `model_id` in `conf/dev/globals_dev.yml`).

**Step 6.** Build the new features (per model_id):

```bash
kedro run --env=dev --pipeline=casa_features
```

```bash
kedro run --env=dev --pipeline=product_features
```

**Step 7.** Run the check (CC model_ids: the CC check; RL model_ids: the RL check):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_check
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_check
```

Paste back every block from `=== A1 … START ===` to `=== A1 … END ===` (4 per model_id). A summary file is fine.

**Step 8.** After the blocks are reviewed, write the real output for every model_id, then re-run the persona master if the deck needs it:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Rebuilds A1 ability on the evidence-family rule (spec `specs/A1_ability_family_rule.md`, family-redesign rounds 1–3, rule R4, plus the CASA balance in money in and own-account transfers with other banks, user 2026-11-10). Apply on top of bundle 20 (A3; independent files except `catalog_crx.yml` and `pipeline_registry.py`).

**What changes in the logic.**
- **Four families**, each strong / some / none. Only strong scores (2 points); weak / some are evidence (Low rather than Unknown):
  - **F1 Income**: as today (`income_level`, S12, S14). Weak no longer scores.
  - **F2 Money in or held**: money in ≥ max(AED 1,000, 1 × anchor) in 2 of 3 months (3 of 6 at 180+), **or** the CASA balance ≥ max(AED 3,000, 1 × anchor) in 2 of 3 months and not more than 50% below the prior window (today's liquidity "adequate" on balances). Some: any month with ≥ AED 1,000 money in.
  - **F3 Money out**: chosen spend + transfers to own accounts at other banks ≥ max(AED 1,000, 1 × anchor) in 2 of 3 months. Some: any month ≥ AED 500.
  - **F4 Cross-product**: other products with us at the observation month end (the scored account left out): assets ≥ max(AED 10,000, 3 × anchor), or another current credit product (other cards included) with instalment / minimum due ≥ max(AED 1,000, 1 × anchor). Some: any other current credit product or any asset.
- **State:** High = 2+ strong families, Moderate = 1, Low = evidence but none strong, Unknown = no evidence and no counted CASA leg in the window. Distress demotes one rung (unchanged).
- **Which transactions count** (new feature `feat_cif_casa_flows_monthly`, inclusion list): money in = transfers / remittances / clearing credits from others, cash deposits, credits from own accounts at other banks (WM label); money out = POS, ATM, bills, transfers to others, debits to own accounts at other banks. Never: salary-flagged credits (income), reversals, returned cheques / DDS and the presentments they undo (`CHQ RTN` / `CHQ NO`), refunds, own transfers with us, fees, own card / loan payments, the rest of `MISCELLANEOUS`. A counted leg mirrored by a non-evidence leg (same amount ±1%, within 3 days) is dropped.
- **Dropped:** liquidity as a dimension, the external card payment rule.
- **New output columns:** `a1_reason`, `a1_money_in_level`, `a1_money_out_level`, `a1_cross_product_level`, `a1_sweepable_balance_flag` (the balance is strong: money the bank could still sweep; diagnostic). `a1_liquidity_level` goes. `a1_state` keeps its values, so the persona master is unaffected.

**Code:** `feat_cif_casa.py` gains `FLOW_CLASSES`, `flow_class`, `build_casa_flows` (node in `casa_features`); new `nodes/features/products/feat_cif_cross_product.py` + pipeline `product_features` (`feat_cif_cross_product_monthly`; body written in UAT from the round-3 F4 builder); `a1_ability/signals.py`: `build_casa_signals` and `build_cross_product_signals` replace `build_liquidity_signals`; `classify.py`: the four families on the shared `Scorecard`; catalog `crx_<p>_a1_liquidity_signals` → `crx_<p>_a1_casa_signals` + `crx_<p>_a1_cross_product_signals`.

**Check** (temporary, `a1_ability/check.py`, pipelines `crx_<p>_a1_check`): runs the new A1 into `crx_<p>_a1_check_new` and compares with today's persisted `crx_<p>_a1_ability` on the latest month. Blocks: `A1 OUTPUT` (new and old state mix, reasons, unknown reasons), `A1 MOVES` (old × new), `A1 FAMILIES` (levels per family, strong families per row, the sweepable-balance flag, rows the balance makes strong and the states it moves), `A1 OUTCOMES` (60_180: cure / pay / roll by new state, Jan–May cohort).

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
| replace | `src/enbd_collections/nodes/features/casa/feat_cif_casa.py` |
| add | `src/enbd_collections/nodes/features/products/__init__.py` |
| add | `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/casa/features.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |
| add | `src/enbd_collections/pipelines/products/__init__.py` |
| add | `src/enbd_collections/pipelines/products/features.py` |

## Files

### FILE: `conf/base/catalog/catalog_casa.yml`
action: replace · base sha256 `d4975eb895699094e89bc601b5e72ac2bdab805175ed667694ca8242ae9efe25` · base trailing newline: yes · new sha256 `d50259a9ab0902ee340a975de3d010e4ef6fd7b4ac2b97d88549d36fe1263431` · new trailing newline: yes

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

# CASA money in / out per (cif_id, month_end, flow_class): legs, credit / debit AED,
# largest leg; mirrored non-evidence pairs netted (A1 money in / out, FLOW_CLASSES).
feat_cif_casa_flows_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_flows_monthly"
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

# The customer's other products with us per (cif_id, month_end, product_account_id):
# product_type, balance_aed, is_current, instalment_aed (A1 cross-product, F4).
feat_cif_cross_product_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/products/cif_cross_product_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `9c253367e800b9b108a4610c34e7c85624138e21276e016fb4dff06ae74733c2` · base trailing newline: yes · new sha256 `a52059312831af9aae281053d87eff150bbf81bce4fe67ffba695a5fac650161` · new trailing newline: yes

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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_cc_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_cross_product_signals"
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

# TEMPORARY (A1 bundle 21): the new rule's states for the check; removed by the cleanup.
crx_cc_a1_check_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_check_new"
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
# Unknown}; a1_unknown_reason in {no_casa, dormant_casa} on unknown rows; a1_reason the
# strongest family (income, money_in, money_out, cross_product) or distress.
crx_rl_a1_income_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_cross_product_signals"
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

# TEMPORARY (A1 bundle 21): the new rule's states for the check; removed by the cleanup.
crx_rl_a1_check_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_check_new"
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

### FILE: `src/enbd_collections/nodes/features/casa/feat_cif_casa.py`
action: replace · base sha256 `7b49e51b066fb8bd230f72401f3d86180de7eb02f53d15867c91a1e397b3adef` · base trailing newline: yes · new sha256 `ddcb4b9eb6c64451b1363b67582f8b12c6ea51026cea392ebd509306158087db` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
* ``feat_cif_returns_monthly``          — returned-transaction events per reason (FTR);
* ``feat_cif_casa_flows_monthly``       — CASA money in / out per month and flow class (FTR +
  WM labels; A1 evidence: ``FLOW_CLASSES``).

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


# ── Flow classes (A1 money in / out, specs/A1_ability_family_rule.md §3) ─────────
# A leg counts as evidence only in a class that is positively identified; every other
# leg is a class that does not count. Assigned in this order: a leg takes the first
# class it matches.
FLOW_CLASSES = (
    "salary",  # salary-flagged credit (WM): income (F1), not money in
    "reversal_return",  # reversals, returned cheques / DDS, refunds, cheque presentments
    "own_in_external",  # credit from the customer's own account at another bank
    "own_out_external",  # debit to the customer's own account at another bank
    "own_transfer",  # between the customer's accounts with us, auto-save, group
    "bank_initiated",  # fees, interest
    "debt_to_us",  # paying their own card / loan with us (A3)
    "cash_in",  # cash deposits
    "third_party_in",  # transfers, remittances, clearing credits from others
    "chosen_spend",  # POS, ATM, bills, transfers to others
    "unplaced",  # meaning not established (the rest of MISCELLANEOUS, …)
)
MONEY_IN_CLASSES = ("third_party_in", "cash_in", "own_in_external")
MONEY_OUT_CLASSES = ("chosen_spend", "own_out_external")
# Narration stems of cheque returns and the presentments they undo (both legs, round 3:
# 100% mirrored the same day).
_CHEQUE_STEMS = ("CHQ RTN", "CHQ NO")
# WM's label for a transfer between the customer and their own account at another bank.
# TODO(sonnet): set the column and value the round-3 snippet used for WM "self"
# (tmp_validation/a1_family_redesign/round3_snippet.py); keep the names below.
WM_SELF_COLUMN = "counterparty_type"
WM_SELF_VALUE = "self"
NET_DAYS = 3  # a counted leg mirrored within this many days by a non-evidence leg …
NET_TOLERANCE = 0.01  # … of the same amount (±1%) is dropped (bounce, reversal, sweep)


def flow_class() -> Column:
    """The ``FLOW_CLASSES`` class of a leg carrying ``lane`` (``transaction_lane``),
    ``wm_salary`` and ``wm_self`` (WM labels, false when unlabelled)."""
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    narration = F.upper(F.trim("tran_narration_1"))
    credit = F.col("tran_dc") == "C"
    lane = F.col("lane")
    cheque = F.lit(False)
    for stem in _CHEQUE_STEMS:
        cheque |= F.coalesce(narration.startswith(stem), F.lit(False))
    return (
        F.when(lane.isin("signal", "refund", "reversal") | cheque, "reversal_return")
        .when(credit & F.col("wm_salary"), "salary")
        .when(F.col("wm_self") & credit, "own_in_external")
        .when(F.col("wm_self"), "own_out_external")
        .when(lane.isin("wash", "group_internal"), "own_transfer")
        .when(lane == "fee_interest", "bank_initiated")
        .when(lane.isin("card_payment", "own_loan"), "debt_to_us")
        .when(lane == "card_spend", "chosen_spend")
        .when((lane == "economic") & credit & (t == "CASH DEPOSIT"), "cash_in")
        .when((lane == "economic") & credit, "third_party_in")
        .when(lane == "economic", "chosen_spend")
        .otherwise("unplaced")
    )


def _net_mirrored(legs: DataFrame) -> DataFrame:
    """``legs`` without the counted legs (money in / out classes) that an opposite leg of
    a class that does not count mirrors: the same amount within ``NET_TOLERANCE``,
    0–``NET_DAYS`` days apart, on any account of the customer."""
    counted = F.col("flow_class").isin(*MONEY_IN_CLASSES, *MONEY_OUT_CLASSES)
    other = legs.filter(~counted & (F.col("flow_class") != "salary")).select(
        F.col("cif_id").alias("_cif"),
        F.col("tran_dc").alias("_dc"),
        F.col("tran_date").alias("_day"),
        F.col("amount").alias("_amt"),
    )
    hit = (
        (F.col("cif_id") == F.col("_cif"))
        & (F.col("tran_dc") != F.col("_dc"))
        & (F.abs(F.datediff(F.col("_day"), F.col("tran_date"))) <= NET_DAYS)
        & (F.abs(F.col("_amt") - F.col("amount")) <= NET_TOLERANCE * F.col("amount"))
    )
    mirrored = (
        legs.filter(counted)
        .join(other, hit, "leftsemi")
        .select("cif_id", "tran_id", "tran_date", "tran_dc")
    )
    return legs.join(
        mirrored, on=["cif_id", "tran_id", "tran_date", "tran_dc"], how="left_anti"
    )


def build_casa_flows(
    transactions: DataFrame,
    casa_accounts: DataFrame,
    labelled: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """Per ``(cif_id, month_end, flow_class)``: ``legs``, ``credit_aed``, ``debit_aed``
    and ``max_leg_aed`` of the ``prm_casa_transactions`` legs on CASA accounts, from the
    first of the last ``history_months`` months up to the persona start month on.

    Salary and WM's own-account-elsewhere label come from ``wm_pri_labelled_transactions``
    joined on ``(cif_id, tran_id, tran_date)``. Counted legs mirrored by a leg that does
    not count are dropped (``_net_mirrored``)."""
    _require(
        transactions,
        [
            "cif_id",
            "foracid",
            "tran_id",
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
    _require(
        labelled,
        ["cif_id", "tran_id", "tran_date", "salary_txn_flag", WM_SELF_COLUMN],
        "wm_pri_labelled_transactions",
    )
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    labels = (
        labelled.filter(F.to_date("tran_date") >= floor)
        .groupBy(
            _cif(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
        )
        .agg(
            F.max(F.coalesce(F.col("salary_txn_flag").cast("int"), F.lit(0))).alias(
                "_sal"
            ),
            F.max(
                F.coalesce(
                    (F.lower(F.trim(WM_SELF_COLUMN)) == WM_SELF_VALUE).cast("int"),
                    F.lit(0),
                )
            ).alias("_self"),
        )
    )
    legs = (
        _on_casa_accounts(transactions, casa_accounts)
        .filter(F.to_date("tran_date") >= floor)
        .withColumn("lane", transaction_lane())
        .select(
            _cif(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            "tran_dc",
            "tran_type",
            "tran_narration_1",
            "lane",
            F.col("actual_tran_amt_aed").cast("double").alias("amount"),
        )
        .join(labels, on=["cif_id", "tran_id", "tran_date"], how="left")
        .withColumn("wm_salary", F.coalesce(F.col("_sal"), F.lit(0)) == 1)
        .withColumn("wm_self", F.coalesce(F.col("_self"), F.lit(0)) == 1)
        .withColumn("flow_class", flow_class())
    )
    return (
        _net_mirrored(legs)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "flow_class")
        .agg(
            F.count(F.lit(1)).alias("legs"),
            F.sum(F.when(F.col("tran_dc") == "C", F.col("amount"))).alias("credit_aed"),
            F.sum(F.when(F.col("tran_dc") == "D", F.col("amount"))).alias("debit_aed"),
            F.max("amount").alias("max_leg_aed"),
        )
    )
`````

### FILE: `src/enbd_collections/nodes/features/products/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py`
action: add · new sha256 `9957acb804539bd55d36696658be33128cca9ce9d932a82247680b32042e4bbe` · new trailing newline: yes

New:

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` — ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` — the month-end balance (assets: deposits, investments, WM; NULL for
  credit products);
* ``is_current`` — credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` — credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``), so the A1 engine can leave out the scored account itself. Supplementary
cards post to their contract and never appear as a product of their own. CASA balances are
never a product here (they are A1's money held, ``feat_cif_casa_balance_monthly``).
"""

from __future__ import annotations

from pyspark.sql import DataFrame

PRODUCT_TYPES = ("deposit", "investment", "wm", "card", "loan")
COLUMNS = (
    "cif_id",
    "month_end",
    "product_account_id",
    "product_type",
    "balance_aed",
    "is_current",
    "instalment_aed",
)


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    product_holding: DataFrame,
    loan_portfolio: DataFrame,
    card_balances: DataFrame,
    wm_assets: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the month ends of the last ``history_months`` months up to the
    persona start month on.

    TODO(sonnet): implement from the round-3 snippet's F4 builder
    (``tmp_validation/a1_family_redesign/round3_snippet.py``, family F4 with other cards,
    R3), which reads these sources: ``feat_product_holding`` (deposits / investments),
    ``bo_rr_portf_actv_acct_mthly`` (loans: DPD and instalment), the card balances
    snapshot (cards: DPD and minimum due) and the WM asset balances. Output exactly
    ``COLUMNS``, one row per ``(cif_id, month_end, product_account_id)``, ``cif_id`` as
    string; fail loud on missing columns (``_require`` as in ``feat_cif_casa``).
    """
    raise NotImplementedError(
        "feat_cif_cross_product.build: implement from the round-3 F4 builder "
        "(bundle 21, UAT step)"
    )
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `034577e2961b1fee5629fab92523d1255fea1ed33d7633a035ced64abe303bd8` · base trailing newline: yes · new sha256 `3c6f58a1c42fa531baa622070b1514abd38b8125d35d21eac424fa5e5e362a6a` · new trailing newline: yes

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
from enbd_collections.pipelines.products import features as products_feat

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
        "product_features": products_feat.create_pipeline(),
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
        # TEMPORARY (A1 bundle 21): the A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_check": crx_cc_a1_ability.create_check_pipeline(),
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
        # TEMPORARY (A1 bundle 21): the A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_check": crx_rl_a1_ability.create_check_pipeline(),
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

### FILE: `src/enbd_collections/pipelines/casa/features.py`
action: replace · base sha256 `eaa95c898351d153353e3be548e122267ec5c6aa3fe8e0214b5778e4fef5beb3` · base trailing newline: yes · new sha256 `eddae51cf6f9311a1f8badd2ffb9f2985ff94f8289de0fd7fb5bd03b51f97abf` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

`````python
"""CASA feature pipeline: monthly CASA features per customer (per model_id).

    wm_fea_salary_days_since_increment ──────────────────► feat_cif_internal_salary_monthly
    wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow ► feat_cif_casa_balance_monthly
    prm_casa_transactions, prm_casa_accounts ────────────► feat_cif_casa_activity_monthly
    wm_pri_labelled_transactions, prm_beneficiary_cards ─► feat_cif_ext_card_payment_monthly
    prm_casa_return_events, prm_casa_accounts ───────────► feat_cif_returns_monthly
    prm_casa_transactions, prm_casa_accounts,
    wm_pri_labelled_transactions ────────────────────────► feat_cif_casa_flows_monthly

Needs ``casa_primary`` for the model_id first.

    kedro run --pipeline=casa_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.casa import feat_cif_casa


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The six monthly CASA feature tables."""
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
            node(
                func=feat_cif_casa.build_casa_flows,
                inputs={
                    "transactions": "prm_casa_transactions",
                    "casa_accounts": "prm_casa_accounts",
                    "labelled": "wm_pri_labelled_transactions",
                    **window,
                },
                outputs="feat_cif_casa_flows_monthly",
                name="build_feat_cif_casa_flows_monthly",
                tags=tags,
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `10ea20a369fa61f7644c16700b99826c4a20e1371d4cc0cd6c8b32b361cf2196` · base trailing newline: yes · new sha256 `3dc8b844907db4756e4ca6a31b0d4e3a8c8fd363f6beee0896f2bb2b11eba5e2` · new trailing newline: yes

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
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions` and
  the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

New:

`````markdown
# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks for independent evidence that the customer has
money — income, money coming in or held, money going out by choice, other products with us —
and failed payments, and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule is `specs/A1_ability_family_rule.md`
(income: `specs/A1_ability_spec.md` S1–S16); the code is
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
  | `feat_cif_casa_flows_monthly` | `prm_casa_transactions` ← FTR + `wm_pri_labelled_transactions` (`casa_features`) |
  | `feat_cif_cross_product_monthly` | product holding, loan portfolio, card balances, WM assets (`product_features`) |
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

## 1. F1 Income — Stable (2 points) / Weak (evidence) / None

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
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000 (no points, but evidence: Low rather
  than Unknown). **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Which transactions count (`feat_cif_casa_flows_monthly`)

Every CASA leg gets one class (`feat_cif_casa.flow_class`, on top of `transaction_lane`).
Only these count:

- **Money in:** transfers and remittances from others and clearing credits
  (`third_party_in`), cash deposits (`cash_in`), credits from the customer's own account at
  another bank (`own_in_external`, WM label).
- **Money out:** card spend, ATM, bills, transfers to others (`chosen_spend`), debits to the
  customer's own account at another bank (`own_out_external`, WM label).

Nothing else counts: salary-flagged credits (they are income), reversals, returned cheques /
DDS and the cheque presentments they undo (narrations `CHQ RTN` / `CHQ NO`), refunds,
transfers between the customer's accounts with us, fees and interest, paying their own card
or loan, and anything whose meaning is not established (the rest of `MISCELLANEOUS`). A
counted leg mirrored by a leg that does not count — the same amount (±1%) within 3 days —
is dropped (a bounce, a reversal, a sweep).

## 3. F2 Money in or held, F3 Money out — Strong (2) / Some (evidence) / None

- **F2 strong** = money in ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3 (3 of 6 at 180+),
  **or** the CASA balance ≥ max(AED 3,000, 1 × anchor) in 2 of m1–m3 and not more than 50%
  below the m4–m6 average (money held: the bank's sweep is manual, so a balance can survive
  it). **Some** = any month with ≥ AED 1,000 of money in. A balance below strong is not
  evidence.
- **F3 strong** = money out ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3. **Some** = any month
  ≥ AED 500.
- `a1_sweepable_balance_flag` = the balance is strong: money above the floor the bank could
  still sweep (a lead for collections; it changes nothing).

## 4. F4 Cross-product — Strong (2) / Some (evidence) / None

At the observation month end, the customer's other products with us (the scored account
left out): **strong** = deposits + investments + WM assets ≥ max(AED 10,000, 3 × anchor), or
another credit product (incl. other cards) that is current with an instalment / minimum due
≥ max(AED 1,000, 1 × anchor); **some** = any other current credit product or any asset.

## 5. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a bounced cheque reported by the bureau, one per CIF and return date
  (`DT_OF_RETURN`, S15).

## 6. The state

Only strong levels score (2 points each); weak / some are evidence.

| State | Rule |
|---|---|
| `high` | two or more strong families (4+ points) |
| `moderate` | one strong family |
| `low` | no strong family, but some evidence (income weak, money in / out some, cross-product some), or distress alone |
| `unknown` | no evidence in any family, no distress **and** no counted CASA leg in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA leg or positive balance in 12 months) or `dormant_casa` |

Distress moves a customer exactly one rung down (High → Moderate → Low). `a1_reason` names
the strongest family (or `distress`). `a1_eosb_flag` (a DCORE end-of-service result in the
window) is a diagnostic column and changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts as income.** Other regular credits count as money in;
  about a third of customers hold no CASA with us, so F2 / F3 cannot see them.
- **Money in / out rest on the class table.** A flow type counts only once its meaning is
  established; new transaction types land in `unplaced` until they are classified.
- **Bureau salary is an event feed for now.** An alert row appears only when something changes,
  so no row means nothing is known, not that the salary stopped, and few pulls fall in the
  window. GRR's feed of pulls every 2 months enters through the same rule. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions`,
  the flows and the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: replace · base sha256 `0587cd7e9811420a06aaaa62d0c193ccbb782ca69a50c4946e370767b79dd843` · base trailing newline: yes · new sha256 `e8b88e8d6b0f728b3e1f8741682b4a63b9853f2dceabaa95c4e5911457a1b05c` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
    build_liquidity_signals,
)

__all__ = [
    "build_a1_ability",
    "build_distress_signals",
    "build_eosb_signals",
    "build_income_signals",
    "build_liquidity_signals",
]
`````

New:

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
)

__all__ = [
    "build_a1_ability",
    "build_casa_signals",
    "build_cross_product_signals",
    "build_distress_signals",
    "build_eosb_signals",
    "build_income_signals",
]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/check.py`
action: add · new sha256 `ed1542df073b9c2d95e5cd4907ea065e0532edee41e5c742d5626477758164b7` · new trailing newline: yes

New:

`````python
"""TEMPORARY (A1 bundle 21): the evidence-family rule against the A1 output persisted
before it (bundle 14 rule: income + liquidity), all persona months.

The check runs the new A1 pipeline into ``crx_<p>_a1_check_new`` (the real output is
untouched) and logs, for the latest month:

- ``A1 OUTPUT``: new and old state mix, the reason and unknown-reason mix;
- ``A1 MOVES``: old x new states;
- ``A1 FAMILIES``: each family's levels, strong families per row, the balance in money in
  (rows it makes strong, the states it moves) and the sweepable-balance flag;
- ``A1 OUTCOMES`` (60_180): cure / pay / roll by new state over the Jan–May cohort.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a1_check
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals

import logging

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node
from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, window_months
from .classify import FAMILIES, MONEY_IN_SOME, SCORECARD, _flow_level
from .pipeline import TAGS, create_a1_pipeline

logger = logging.getLogger(__name__)
LEVEL_COLS = [dimension.level for _, dimension in FAMILIES]


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], total: int) -> list[str]:
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "  "
        + " | ".join(str(r[c]) for c in cols)
        + f": {r['count']} ({100 * r['count'] / max(total, 1):.1f}%)"
        for r in rows
    ]


def _without_balance(new: DataFrame, casa: DataFrame, model_id: str) -> DataFrame:
    """``new`` + ``state_no_balance``: the state when the CASA balance does not count
    towards money in (money in = the inflow level alone)."""
    w = window_months(model_id)
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    df = new.join(casa, on=list(GRAIN), how="left").withColumn(
        "_inflow", _flow_level("in", MONEY_IN_SOME, amt, w)
    )
    rescored = SCORECARD.score(
        df.withColumn(
            "a1_money_in_level",
            F.when(F.col("a1_sweepable_balance_flag") == 1, F.col("_inflow")).otherwise(
                F.col("a1_money_in_level")
            ),
        )
        .withColumn("a1_distress_flag", F.col("a1_distress_flag") == 1)
        .drop("a1_state", "a1_points_total", "a1_reason"),
        unknown_also=F.coalesce(F.col("casa_active"), F.lit(0)) == 0,
    )
    return rescored.select(
        *GRAIN,
        F.col("a1_state").alias("state_no_balance"),
        (
            (F.col("a1_sweepable_balance_flag") == 1)
            & (F.coalesce(F.col("_inflow"), F.lit("")) != "strong")
        )
        .cast("int")
        .alias("balance_only_strong"),
    )


def cohort_outcome_lines(new: DataFrame, model_id: str) -> list[str]:
    """``cure_3`` / ``pay_any_3`` / ``roll_3`` (%) by new A1 state over the Jan–May 2026
    cohort, n per state, 60_180 only.

    TODO(sonnet): implement with the round-3 snippet's outcome definitions
    (``tmp_validation/a1_family_redesign/round3_snippet.py``: the same cohort, the same
    three outcomes, raw and DPD-band standardised, with 95% intervals), adding the
    catalog datasets it needs as node inputs of ``compare_a1``. Aggregates only.
    """
    if "60_180" not in model_id:
        return ["  180+: no outcomes (as in rounds 1-3)"]
    del new
    return ["  TODO(sonnet): cohort outcomes not implemented"]


def compare_a1(
    old: DataFrame,
    new: DataFrame,
    casa: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Logs the A1 OUTPUT / MOVES / FAMILIES / OUTCOMES blocks for ``model_id``."""
    head = [f"  model_id {model_id}, latest month {persona_end_date}"]
    new_l = _latest(new, persona_end_date).cache()
    old_l = _latest(old, persona_end_date).select(
        *GRAIN, F.col("a1_state").alias("old_state")
    )
    n_new, n_old = new_l.count(), old_l.count()
    _block(
        "A1 OUTPUT",
        head
        + [f"  new rows {n_new}, old rows {n_old}", "  new state:"]
        + _counts(new_l, ["a1_state"], n_new)
        + ["  old state:"]
        + _counts(old_l, ["old_state"], n_old)
        + ["  new reason:"]
        + _counts(new_l, ["a1_reason"], n_new)
        + ["  new unknown reason (unknown rows):"]
        + _counts(
            new_l.filter(F.col("a1_state") == "unknown"), ["a1_unknown_reason"], n_new
        ),
    )
    moves = old_l.join(new_l.select(*GRAIN, "a1_state"), on=list(GRAIN), how="full")
    _block(
        "A1 MOVES",
        head + ["  old | new"] + _counts(moves, ["old_state", "a1_state"], n_new),
    )
    top = ["stable"] + ["strong"] * (len(LEVEL_COLS) - 1)
    strong = sum(
        F.coalesce(F.col(c) == lvl, F.lit(False)).cast("int")
        for c, lvl in zip(LEVEL_COLS, top)
    )
    nb = _without_balance(new_l, _latest(casa, persona_end_date), model_id).cache()
    families = head[:]
    for col in LEVEL_COLS:
        families += [f"  {col}:"] + _counts(new_l, [col], n_new)
    families += ["  strong families per row:"] + _counts(
        new_l.withColumn("strong_families", strong), ["strong_families"], n_new
    )
    families += ["  sweepable balance flag:"] + _counts(
        new_l, ["a1_sweepable_balance_flag"], n_new
    )
    families += ["  money in strong only through the balance:"] + _counts(
        nb, ["balance_only_strong"], n_new
    )
    moved = new_l.select(*GRAIN, "a1_state").join(nb, on=list(GRAIN))
    families += [
        "  state without the balance | with it (rows the balance moves):"
    ] + _counts(
        moved.filter(F.col("state_no_balance") != F.col("a1_state")),
        ["state_no_balance", "a1_state"],
        n_new,
    )
    _block("A1 FAMILIES", families)
    _block("A1 OUTCOMES", head + cohort_outcome_lines(new, model_id))
    new_l.unpersist()
    nb.unpersist()


def create_a1_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """The new A1 pipeline into ``crx_<p>_a1_check_new``, then the comparison."""
    prefix = f"crx_{product}_a1"
    return create_a1_pipeline(product, f"{prefix}_check_new", anchor) + Pipeline(
        [
            node(
                func=compare_a1,
                inputs={
                    "old": f"{prefix}_ability",
                    "new": f"{prefix}_check_new",
                    "casa": f"{prefix}_casa_signals",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"compare_{prefix}_check",
                tags=TAGS,
            )
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: replace · base sha256 `361a41ca2b147df1c80f350dec6761f4efa9e57e2090a86fa0b1fef54719c9a5` · base trailing newline: yes · new sha256 `0518f4504399eddb1605d593b674029c3d925e5d03b1eabf5204721ec191d38e` · new trailing newline: yes

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
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (spec §3, S2–S12): the workbook's starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
CASA_MIN_MONTHS = {3: 2, 6: 3}  # S7: months of the window the CASA must be at its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
INCOME_FLOOR = 3000.0  # S2: salary floor (internal and bureau), AED
INCOME_ANCHOR_MULT = 2.0  # S2: income must also cover this multiple of the anchor
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
CASA_FLOOR = 3000.0  # S7
CASA_ANCHOR_MULT = 1.0  # S7
CASA_MAX_FALL = 0.50  # S7
CARD_PAYMENT_FLOOR = 500.0  # S8
CARD_PAYMENT_ANCHOR_MULT = 1.0  # S8
MIN_EVIDENCE_AMT = 1000.0  # smallest amount that counts as evidence (Weak, S5-S8)
INCOME_POINTS = {"stable": 2, "weak": 1}  # spec points table (GRR)
LIQUIDITY_POINTS = {"adequate": 2, "weak": 1}  # same table
HIGH_FROM, MODERATE_FROM = 4, 2  # points for High / Moderate (spec s_high / s_mod)

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


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
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
    floor = F.greatest(F.lit(INCOME_FLOOR), INCOME_ANCHOR_MULT * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (spec S7, S8)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(CASA_FLOOR), CASA_ANCHOR_MULT * anchor)
    casa_ok = (
        _count_at_least(last, casa_floor) >= CASA_MIN_MONTHS[w]
    ) & _not_weakening("casa", CASA_MAX_FALL, missing_is_zero=False, w=w)
    adequate = casa_ok | (
        payment
        >= F.greatest(F.lit(CARD_PAYMENT_FLOOR), CARD_PAYMENT_ANCHOR_MULT * anchor)
    )
    weak = (_count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0) | (
        payment >= MIN_EVIDENCE_AMT
    )
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (liquidity_level, Dimension("liquidity", "a1_liquidity_level", LIQUIDITY_POINTS)),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={s: s for s in ("high", "moderate", "low", "unknown")},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def build_a1_ability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Points: S2–S12; the unknown gate: S11; distress lowers the state one rung (S9).

    ``signals`` (income, liquidity, distress, EOSB: ``GRAIN`` + columns) and ``anchor``
    (``GRAIN + liquidity_anchor_amt``, product builder) are left-joined in that order.
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``. Diagnostics, which
    change nothing: ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the
    prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0  # S11
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    internal_w = _shows_evidence("internal_salary_w")
    bureau_w = _shows_evidence("bureau_salary_w")
    internal_prior = _shows_evidence("internal_salary_prior")
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
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
"""A1 ability state — evidence families.

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md``.

    F1 income        stable 2 / weak 0 (evidence) / none
    F2 money in/held strong 2 / some 0 (evidence) / none   (inflow, or a CASA balance)
    F3 money out     strong 2 / some 0 (evidence) / none
    F4 cross-product strong 2 / some 0 (evidence) / none
    = points         4+ high (two strong families), 2 moderate, else low
  distress (cheque / DDS return, new bureau bounce) lowers the state one rung;
  no evidence in any family and no counted CASA leg in the window → unknown.

Thresholds scale with ``liquidity_anchor_amt`` — what the customer must find now
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only,
S1). Run through ``crx_cc_a1_ability`` / ``crx_rl_a1_ability``.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import DEMOTE, Dimension, Override, Scorecard, state_label

# Thresholds (family rule §2; income: spec S2–S12): starting values, not tuned on PROD.
# Keyed by window length W (3 months at 60–180, 6 at 180+, S10).
MIN_MONTHS = {3: 2, 6: 3}  # months of the window a flow / balance must reach its floor
STABLE_INCOME_FLOORS = {3: 2, 6: 3}  # S12: the window's salary covers this many floors
INCOME_FLOOR = 3000.0  # S2: salary floor (internal and bureau), AED
INCOME_ANCHOR_MULT = 2.0  # S2: income must also cover this multiple of the anchor
INCOME_MAX_FALL = 0.25  # S12: ... and is at most this share below the prior window
FLOW_FLOOR = 1000.0  # F2 / F3 strong: a month's flow reaches max(floor, mult x anchor)
FLOW_ANCHOR_MULT = 1.0
MONEY_IN_SOME = 1000.0  # F2 some: any month with this much money in
MONEY_OUT_SOME = 500.0  # F3 some: any month with this much money out
BALANCE_FLOOR = 3000.0  # F2 balance strong (today's liquidity "adequate" on balances)
BALANCE_ANCHOR_MULT = 1.0
BALANCE_MAX_FALL = 0.50
ASSET_FLOOR = 10000.0  # F4 strong: assets reach max(floor, mult x anchor) …
ASSET_ANCHOR_MULT = 3.0
INSTALMENT_FLOOR = 1000.0  # … or a current credit product's instalment reaches
INSTALMENT_ANCHOR_MULT = 1.0  # max(floor, mult x anchor)
MIN_EVIDENCE_AMT = 1000.0  # smallest salary that counts as evidence (income weak)
INCOME_POINTS = {"stable": 2}  # weak is evidence (Low), not points
FAMILY_POINTS = {"strong": 2}  # some is evidence (Low), not points
HIGH_FROM, MODERATE_FROM = 4, 2  # two strong families / one

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


def _shows_evidence(col: str) -> Column:
    """The column holds an amount of at least ``MIN_EVIDENCE_AMT`` (NULL: no)."""
    return F.coalesce(F.col(col), F.lit(0.0)) >= MIN_EVIDENCE_AMT


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, *, missing_is_zero: bool, w: int
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
    floor = F.greatest(F.lit(INCOME_FLOOR), INCOME_ANCHOR_MULT * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    has_internal_salary = _shows_evidence("internal_salary_w") | _shows_evidence(
        "internal_salary_prior"
    )
    holding = F.when(
        has_internal_salary,
        _not_weakening("income", INCOME_MAX_FALL, missing_is_zero=True, w=w),
    ).otherwise(_not_weakening("income", INCOME_MAX_FALL, missing_is_zero=False, w=w))
    stable = (total >= STABLE_INCOME_FLOORS[w] * floor) & holding
    weak = _count_at_least(last, F.lit(MIN_EVIDENCE_AMT)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def _strong_months(prefix: str, floor: Column, w: int) -> Column:
    """At least ``MIN_MONTHS[w]`` months of the window reach ``floor``."""
    return _count_at_least(_months(prefix, _window(w)[0]), floor) >= MIN_MONTHS[w]


def balance_strong(anchor: Column, w: int) -> Column:
    """The CASA balance holds max(floor, anchor) in ``MIN_MONTHS`` months of the window
    and is not more than ``BALANCE_MAX_FALL`` below the prior window (money held)."""
    floor = F.greatest(F.lit(BALANCE_FLOOR), BALANCE_ANCHOR_MULT * anchor)
    return _strong_months("casa", floor, w) & _not_weakening(
        "casa", BALANCE_MAX_FALL, missing_is_zero=False, w=w
    )


def _flow_level(prefix: str, some_floor: float, anchor: Column, w: int) -> Column:
    """strong / some / none / NULL (no flow in the window) of a monthly flow."""
    last = _months(prefix, _window(w)[0])
    floor = F.greatest(F.lit(FLOW_FLOOR), FLOW_ANCHOR_MULT * anchor)
    has_data = F.greatest(*[c.isNotNull() for c in last])
    return (
        F.when(_strong_months(prefix, floor, w), "strong")
        .when(_count_at_least(last, F.lit(some_floor)) > 0, "some")
        .when(has_data, "none")
    )


def money_in_level(anchor: Column, w: int) -> Column:
    """F2: strong when money in or the balance held is strong; some on money in only (a
    balance below strong is not evidence)."""
    inflow = _flow_level("in", MONEY_IN_SOME, anchor, w)
    return F.when(balance_strong(anchor, w), "strong").otherwise(inflow)


def money_out_level(anchor: Column, w: int) -> Column:
    """F3: chosen spend and transfers to the customer's own accounts elsewhere."""
    return _flow_level("out", MONEY_OUT_SOME, anchor, w)


def cross_product_level(anchor: Column, w: int) -> Column:  # pylint: disable=W0613
    """F4 at the observation month end: strong on assets of max(floor, 3 x anchor) or a
    current credit product whose instalment reaches max(floor, anchor); some on any other
    current credit product or any asset."""
    assets = F.coalesce(F.col("xp_assets_aed"), F.lit(0.0))
    instalment = F.coalesce(F.col("xp_instalment_max"), F.lit(0.0))
    strong = (assets >= F.greatest(F.lit(ASSET_FLOOR), ASSET_ANCHOR_MULT * anchor)) | (
        (F.col("xp_current") == 1)
        & (
            instalment
            >= F.greatest(F.lit(INSTALMENT_FLOOR), INSTALMENT_ANCHOR_MULT * anchor)
        )
    )
    some = (F.col("xp_current") == 1) | (F.col("xp_holding") == 1)
    return F.when(strong, "strong").when(some, "some").otherwise("none")


# A1's families: the function giving the level (anchor amount, window W), the dimension.
FAMILIES = (
    (income_level, Dimension("income", "a1_income_level", INCOME_POINTS)),
    (money_in_level, Dimension("money_in", "a1_money_in_level", FAMILY_POINTS)),
    (money_out_level, Dimension("money_out", "a1_money_out_level", FAMILY_POINTS)),
    (
        cross_product_level,
        Dimension("cross_product", "a1_cross_product_level", FAMILY_POINTS),
    ),
)
SCORECARD = Scorecard(
    prefix="a1",
    dimensions=tuple(dimension for _, dimension in FAMILIES),
    overrides=(Override("distress", "a1_distress_flag", DEMOTE),),  # S9
    # state id = rung name; the display text is DISPLAY_NAMES
    labels={s: s for s in ("high", "moderate", "low", "unknown")},
    high_from=HIGH_FROM,
    moderate_from=MODERATE_FROM,
)


def build_a1_ability(  # pylint: disable=too-many-locals
    obs_base: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
    **signals: DataFrame,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).
    Families and points: family rule §2–§4; distress lowers the state one rung (S9).

    ``signals`` (income, CASA, cross-product, distress, EOSB: ``GRAIN`` + columns) and
    ``anchor``
    (``GRAIN + liquidity_anchor_amt``, product builder) are left-joined in that order.
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``; ``a1_reason`` is the
    strongest family (or ``distress``). Diagnostics, which change nothing:
    ``a1_sweepable_balance_flag`` (the CASA balance is strong: money above the floor the
    bank could still sweep), ``a1_eosb_flag`` (a DCORE end-of-service result in the window),
    ``a1_income_source`` (who shows AED 1,000 or more in the window: ``internal``,
    ``bureau``, ``both`` or ``none``), ``a1_salary_stopped`` (internal salary in the
    prior window, none in the window).
    """
    # join order follows the node inputs; output is the same (left joins on GRAIN)
    df = left_join_all(obs_base, [*signals.values(), anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    for level, dimension in FAMILIES:
        df = df.withColumn(dimension.level, level(amt, w))
    df = df.withColumn("a1_distress_flag", F.col("distress_flag") == 1)
    no_casa_activity = F.coalesce(F.col("casa_active"), F.lit(0)) == 0
    df = SCORECARD.score(df, unknown_also=no_casa_activity)
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    internal_w = _shows_evidence("internal_salary_w")
    bureau_w = _shows_evidence("bureau_salary_w")
    internal_prior = _shows_evidence("internal_salary_prior")
    out = df.select(
        *GRAIN,
        "a1_state",
        state_label("a1_state", DISPLAY_NAMES).alias("a1_state_label"),
        F.when(F.col("a1_state") == "unknown", "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == "unknown", unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_reason",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        balance_strong(amt, w).cast("int").alias("a1_sweepable_balance_flag"),
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
action: replace · base sha256 `dbb05c5b63fbf0ed5676b287eba3eba894f7fd73a8aab0531a9b77b493d5803b` · base trailing newline: yes · new sha256 `9ac0eed0ccee7dc3f9fac5a59385733ecc8ed9ed246ec9a3c7fb71a7136e8f8b` · new trailing newline: yes

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
                    "crx_persona": "params:crx_persona",
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
                      ├─ CASA signals ──────┤   feat_cif_casa_balance_monthly,
                      │                     │   feat_cif_casa_flows_monthly
                      ├─ cross-product ─────┤   feat_cif_cross_product_monthly
                      ├─ distress signals ──┼─► crx_<p>_a1_ability
                      │                     │   feat_cif_returns_monthly,
                      │                     │   feat_cif_bureau_bounces_monthly
                      ├─ EOSB signals ──────┤   dcore_prm_followup_outcomes,
                      │                     │   prm_dcore_account_agreements
                      └─ liquidity anchor ──┘   (product node: prm_balance / int_loan_master)

Needs, for the model_id: the observation base, ``casa_primary``, ``casa_features``,
``product_features``, ``bureau_salary_bounces`` and ``location_features``
(``prm_dcore_account_agreements``).
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from .classify import build_a1_ability
from .signals import (
    build_casa_signals,
    build_cross_product_signals,
    build_distress_signals,
    build_eosb_signals,
    build_income_signals,
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
                func=build_casa_signals,
                inputs={
                    "obs_base": obs,
                    "casa_balance": "feat_cif_casa_balance_monthly",
                    "casa_flows": "feat_cif_casa_flows_monthly",
                    "model_id": "params:model_id",
                    "crx_persona": "params:crx_persona",
                },
                outputs=f"{prefix}_casa_signals",
                name=f"build_{prefix}_casa_signals",
                tags=TAGS,
            ),
            node(
                func=build_cross_product_signals,
                inputs={
                    "obs_base": obs,
                    "products": "feat_cif_cross_product_monthly",
                },
                outputs=f"{prefix}_cross_product_signals",
                name=f"build_{prefix}_cross_product_signals",
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
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py`
action: replace · base sha256 `ec700a69a43c97024e6c938d35fa9c0e28b7ee44d961b8dfe9d708f046824633` · base trailing newline: yes · new sha256 `13b4a878dfb01d9ae32caf9b01b7f021329b8abf287b47ea989ca6c017e14fbd` · new trailing newline: yes

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
    window_start,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
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
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


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
    none = F.lit(None).cast("double")
    own = bureau.select("cif_id", "month_end", "bureau_salary", none.alias("_carried"))
    carried = bureau.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        none.alias("bureau_salary"),
        F.col("bureau_salary").alias("_carried"),
    )
    return (
        own.unionByName(carried)
        .groupBy("cif_id", "month_end")
        .agg(
            F.coalesce(F.max("bureau_salary"), F.max("_carried")).alias("bureau_salary")
        )
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.

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
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── Liquidity and activity ────────────────────────────────────────────────────


def _casa_legs(casa_activity: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``balance`` (NULL on an
    activity leg), ``customer`` (1: a leg in ``CUSTOMER_LANES``, S11) and ``held`` (1: a
    leg, or a positive balance)."""
    return casa_activity.select(
        "cif_id",
        "month_end",
        F.lit(None).cast(casa_balance.schema["casa_balance"].dataType).alias("balance"),
        F.col("lane").isin(*CUSTOMER_LANES).cast("int").alias("customer"),
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            F.col("casa_balance").alias("balance"),
            F.lit(0).alias("customer"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_liquidity_signals(  # pylint: disable=too-many-arguments
    obs_base: DataFrame,
    casa_balance: DataFrame,
    ext_card_payments: DataFrame,
    casa_activity: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``casa_m1 … casa_m{2W}`` (S7, ``feat_cif_casa_balance_monthly``),
    ``ext_card_payment_max`` (S8: largest single payment to an external card in W),
    ``casa_active`` (S11: a leg in ``CUSTOMER_LANES`` in W) and ``casa_held`` (any CASA
    leg or a positive balance in the last ``CASA_HELD_MONTHS`` months). CASA means the
    scheme-code accounts of S16."""
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
    # The obs base starts in the persona start month: no window reaches older rows.
    first = F.lit(str(crx_persona["persona_start_date"])).cast("date")
    legs = _casa_legs(casa_activity, casa_balance).filter(
        F.col("month_end") >= window_start(CASA_HELD_MONTHS, first)
    )
    payments = ext_card_payments.filter(F.col("month_end") >= window_start(w, first))
    in_w = _month_index(F.col("month_end")) <= w
    casa_active = F.max(F.when((F.col("customer") == 1) & in_w, F.lit(1)))  # S11
    casa_held = F.max(F.when(F.col("held") == 1, F.lit(1)))
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                legs,
                CASA_HELD_MONTHS,
                *_by_month("balance", "casa", 2 * w),
                casa_active.alias("casa_active"),
                casa_held.alias("casa_held"),
            ),
            _in_window(
                obs, payments, w, F.max("max_payment").alias("ext_card_payment_max")
            ),
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "ext_card_payment_max",
        "casa_active",
        "casa_held",
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
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
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
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
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
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

Spec: ``workplace_mirror/specs/A1_ability_family_rule.md`` (income: S2–S16 of
``A1_ability_spec.md``).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income   — salary in each month: the larger of the internal credit and the bureau
             salary, a pull counting in its own month and the next (S14);
* CASA     — money in and money out per month (the counted flow classes of
             ``feat_cif_casa_flows_monthly``), the CASA average balance per month, whether
             any counted leg falls in the window (the Unknown gate) and whether the
             customer holds a CASA with us at all;
* products — the customer's other products with us at the observation month (F4);
* distress — a cheque return, a direct-debit (DDS) return or a new bureau bounce in
             the window;
* EOSB     — a DCORE end-of-service result in the window (diagnostic only).

Features are per customer (CIF): every account of the customer counts, never the scored
account_id alone (an RL account_id is not a CASA account).
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    MONEY_IN_CLASSES,
    MONEY_OUT_CLASSES,
)
from enbd_collections.nodes.features.products.feat_cif_cross_product import (
    COLUMNS as CROSS_PRODUCT_COLUMNS,
)

from .._common import (
    GRAIN,
    left_join_all,
    lookback_floor,
    require_columns,
    window_agg,
    window_months,
    window_start,
)

# prm_casa_return_events reasons that count as distress; it also carries "RETURNS"
# (POS refunds).
CHEQUE_RETURN, DDS_RETURN = "CHEQUE RETURNS", "DDS Rejects/Reversal"
REASON_BUREAU_BOUNCE = "BUREAU"  # the reason given to bureau-reported bounces (S15)
# Months in which a CASA leg or a positive balance shows the customer holds a CASA
# with us (WM may fill missing balances with 0, so a zero balance proves nothing).
CASA_HELD_MONTHS = 12
EOSB = "EOSB"  # in a DCORE result name: end-of-service benefits expected / received
# Which source a salary row comes from, in ``build_income_signals``.
SOURCE_INTERNAL, SOURCE_BUREAU = "int", "bur"


def _cifs(obs_base: DataFrame) -> DataFrame:
    """Observation rows with a CIF, ``cif_id`` as string (the features' type)."""
    return obs_base.filter(F.col("cif_id").isNotNull()).withColumn(
        "cif_id", F.col("cif_id").cast("string")
    )


def _month_index(date: Column) -> Column:
    """1 for the observation month, 2 for the one before, …"""
    obs_month = F.trunc(F.col("observation_date"), "month")
    return F.months_between(obs_month, F.trunc(date, "month")).cast("int") + 1


def _by_month(value: str, prefix: str, months: int) -> list[Column]:
    """Aggregates spreading ``value`` of a ``(cif_id, month_end, …)`` series over
    ``{prefix}_m1 … _m{months}`` per observation (NULL where the month has no value)."""
    k = _month_index(F.col("month_end"))
    return [
        F.max(F.when(k == i, F.col(value))).alias(f"{prefix}_m{i}")
        for i in range(1, months + 1)
    ]


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
    none = F.lit(None).cast("double")
    own = bureau.select("cif_id", "month_end", "bureau_salary", none.alias("_carried"))
    carried = bureau.select(
        "cif_id",
        F.last_day(F.add_months("month_end", 1)).alias("month_end"),
        none.alias("bureau_salary"),
        F.col("bureau_salary").alias("_carried"),
    )
    return (
        own.unionByName(carried)
        .groupBy("cif_id", "month_end")
        .agg(
            F.coalesce(F.max("bureau_salary"), F.max("_carried")).alias("bureau_salary")
        )
    )


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.

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
        F.lit(SOURCE_INTERNAL).alias("src"),
    )
    bureau = bureau_salary.select("cif_id", "month_end", "bureau_salary")
    if loan_features is not None:
        bureau = bureau.unionByName(_loan_bureau_salary(obs_base, loan_features))
    sources = internal.unionByName(
        _with_next_month(bureau).select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit(SOURCE_BUREAU).alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    in_w = _month_index(F.col("month_end")) <= w
    internal_rows = F.col("src") == SOURCE_INTERNAL
    return left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                sources,
                2 * w,
                *_by_month("amount", "income", 2 * w),
                F.max(F.when(internal_rows & in_w, F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(~internal_rows & in_w, F.col("amount"))).alias(
                    "bureau_salary_w"
                ),
                F.max(F.when(internal_rows & ~in_w, F.col("amount"))).alias(
                    "internal_salary_prior"
                ),
            )
        ],
    )


# ── CASA: money in / out / held ──────────────────────────────────────────────


def _casa_rows(casa_flows: DataFrame, casa_balance: DataFrame) -> DataFrame:
    """CASA rows of both features by ``(cif_id, month_end)``: ``money_in`` / ``money_out``
    (AED of the counted classes; NULL on a balance row), ``balance`` (NULL on a flow row),
    ``counted`` (1: a counted leg) and ``held`` (1: any leg, or a positive balance)."""
    null = F.lit(None).cast("double")
    counted_in = F.col("flow_class").isin(*MONEY_IN_CLASSES)
    counted_out = F.col("flow_class").isin(*MONEY_OUT_CLASSES)
    flows = casa_flows.groupBy("cif_id", "month_end").agg(
        F.sum(F.when(counted_in, F.col("credit_aed"))).alias("money_in"),
        F.sum(F.when(counted_out, F.col("debit_aed"))).alias("money_out"),
        F.max((counted_in | counted_out).cast("int")).alias("counted"),
    )
    return flows.select(
        "cif_id",
        "month_end",
        "money_in",
        "money_out",
        null.alias("balance"),
        "counted",
        F.lit(1).alias("held"),
    ).unionByName(
        casa_balance.select(
            "cif_id",
            "month_end",
            null.alias("money_in"),
            null.alias("money_out"),
            F.col("casa_balance").cast("double").alias("balance"),
            F.lit(0).alias("counted"),
            (F.col("casa_balance") > 0).cast("int").alias("held"),
        )
    )


def build_casa_signals(
    obs_base: DataFrame,
    casa_balance: DataFrame,
    casa_flows: DataFrame,
    model_id: str,
    *,
    crx_persona: dict,
) -> DataFrame:
    """``in_m1 … in_mW`` / ``out_m1 … out_mW`` (money in / out per month, the counted
    classes of ``feat_cif_casa_flows_monthly``; salary credits are income, not money in),
    ``casa_m1 … casa_m{2W}`` (``feat_cif_casa_balance_monthly``), ``casa_active`` (a
    counted leg in W: the Unknown gate) and ``casa_held`` (any CASA leg or a positive
    balance in the last ``CASA_HELD_MONTHS`` months). CASA means the scheme-code accounts
    of S16."""
    require_columns(
        casa_balance,
        ["cif_id", "month_end", "casa_balance"],
        "feat_cif_casa_balance_monthly",
    )
    require_columns(
        casa_flows,
        ["cif_id", "month_end", "flow_class", "credit_aed", "debit_aed"],
        "feat_cif_casa_flows_monthly",
    )
    obs = _cifs(obs_base)
    w = window_months(model_id)
    # The obs base starts in the persona start month: no window reaches older rows.
    first = F.lit(str(crx_persona["persona_start_date"])).cast("date")
    rows = _casa_rows(casa_flows, casa_balance).filter(
        F.col("month_end") >= window_start(CASA_HELD_MONTHS, first)
    )
    in_w = _month_index(F.col("month_end")) <= w
    signals = left_join_all(
        obs_base,
        [
            _in_window(
                obs,
                rows,
                CASA_HELD_MONTHS,
                *_by_month("money_in", "in", w),
                *_by_month("money_out", "out", w),
                *_by_month("balance", "casa", 2 * w),
                F.max(F.when((F.col("counted") == 1) & in_w, F.lit(1))).alias(
                    "casa_active"
                ),
                F.max(F.when(F.col("held") == 1, F.lit(1))).alias("casa_held"),
            )
        ],
    )
    return signals.fillna(0, subset=["casa_active", "casa_held"]).select(
        *GRAIN,
        *[f"in_m{i}" for i in range(1, w + 1)],
        *[f"out_m{i}" for i in range(1, w + 1)],
        *[f"casa_m{i}" for i in range(1, 2 * w + 1)],
        "casa_active",
        "casa_held",
    )


# ── Cross-product (F4) ────────────────────────────────────────────────────────


def build_cross_product_signals(obs_base: DataFrame, products: DataFrame) -> DataFrame:
    """At the observation month end, the customer's other products with us
    (``feat_cif_cross_product_monthly``), the scored account itself left out:
    ``xp_assets_aed`` (deposits + investments + WM), ``xp_instalment_max`` (the largest
    instalment / minimum due of another credit product that is current), ``xp_current``
    (1: another credit product is current) and ``xp_holding`` (1: any asset above 0)."""
    require_columns(
        products, list(CROSS_PRODUCT_COLUMNS), "feat_cif_cross_product_monthly"
    )
    obs = _cifs(obs_base).select(*GRAIN, "cif_id")
    asset = F.col("product_type").isin("deposit", "investment", "wm")
    current_credit = F.col("product_type").isin("card", "loan") & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    rows = (
        obs.join(
            products.select(
                F.col("cif_id").cast("string").alias("cif_id"),
                F.col("month_end").alias("observation_date"),
                F.col("product_account_id").cast("string").alias("_acct"),
                "product_type",
                F.col("balance_aed").cast("double").alias("_bal"),
                "is_current",
                F.col("instalment_aed").cast("double").alias("_inst"),
            ),
            on=["cif_id", "observation_date"],
        )
        .filter(F.col("_acct") != F.col("account_id").cast("string"))
        .groupBy(*GRAIN)
        .agg(
            F.sum(F.when(asset, F.col("_bal"))).alias("xp_assets_aed"),
            F.max(F.when(current_credit, F.col("_inst"))).alias("xp_instalment_max"),
            F.max(current_credit.cast("int")).alias("xp_current"),
            F.max((asset & (F.col("_bal") > 0)).cast("int")).alias("xp_holding"),
        )
    )
    return left_join_all(obs_base, [rows]).fillna(
        0, subset=["xp_current", "xp_holding"]
    )


# ── Distress ──────────────────────────────────────────────────────────────────


def _flag(reason: str) -> Column:
    """1 when any event in the window has this ``reason``."""
    return F.max((F.col("reason") == reason).cast("int"))


def _require_returns_from(returns: DataFrame, since: str) -> None:
    """Stop the run when the returns table starts after ``since`` (an ISO date)."""
    first = returns.agg(F.min("month_end")).first()[0]
    if first is None or first.isoformat()[:7] > since[:7]:
        raise ValueError(
            f"feat_cif_returns_monthly starts at {first}, but the observations need "
            f"returns from {since}: rerun casa_primary and casa_features after changing "
            "crx_persona.persona_start_date"
        )


def _distress_events(
    returns: DataFrame,
    bureau_bounces: DataFrame,
    payment_order: DataFrame | None,
    since: str,
) -> DataFrame:
    """``(cif_id, month_end, reason)`` per distress event: the bank's own cheque / DDS
    returns, bureau bounces and, when given, ``payment_order`` returns. The returns and
    bounces are read from ``since`` (an ISO date) on."""
    events = bureau_bounces.filter(
        (F.col("bounce_events") > 0) & (F.col("month_end") >= F.lit(since))
    ).select("cif_id", "month_end", F.lit(REASON_BUREAU_BOUNCE).alias("reason"))
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
                F.lit(REASON_BUREAU_BOUNCE).alias("reason"),
            )
        )
    return events.unionByName(
        returns.filter(
            F.col("reason").isin(CHEQUE_RETURN, DDS_RETURN)
            & (F.col("events") > 0)
            & (F.col("month_end") >= F.lit(since))
        ).select("cif_id", "month_end", "reason")
    )


def build_distress_signals(
    obs_base: DataFrame,
    returns: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    payment_order: DataFrame | None = None,
) -> DataFrame:
    """``distress_flag`` (S9) and its parts in the window, each 0 / 1:

    * ``distress_cheque`` / ``distress_dds`` — the bank's own returned cheques and DDS
      returns, across all the customer's CASA accounts (``feat_cif_returns_monthly``);
    * ``distress_bureau`` — a bureau-reported bounce dated by its return date
      (``feat_cif_bureau_bounces_monthly`` ``bounce_events``, S15);
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
    _require_returns_from(returns, since)
    events = _distress_events(returns, bureau_bounces, payment_order, since)
    hits = _in_window(
        obs,
        events,
        w,
        _flag(CHEQUE_RETURN).alias("distress_cheque"),
        _flag(DDS_RETURN).alias("distress_dds"),
        _flag(REASON_BUREAU_BOUNCE).alias("distress_bureau"),
    )
    parts = ["distress_cheque", "distress_dds", "distress_bureau"]
    return (
        left_join_all(obs_base, [hits])
        .fillna(0, subset=parts)
        .withColumn("distress_flag", F.greatest(*[F.col(p) for p in parts]))
    )


# ── EOSB (diagnostic) ─────────────────────────────────────────────────────────


def build_eosb_signals(
    obs_base: DataFrame, followup: DataFrame, agreements: DataFrame, model_id: str
) -> DataFrame:
    """``eosb_flag`` (S13): 1 when a DCORE result on any of the customer's agreements
    names an end-of-service benefit (EOSB expected / awaited / received) in the
    window. A diagnostic only: it changes no level or state."""
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
action: replace · base sha256 `628cbd7062a01853872310fe7d00b2f35d3d1b52364696fd7ac73fdd227cdb3f` · base trailing newline: yes · new sha256 `c5175998cb6e85dd1de42ec1f3fad62a40abb616feb5c2f8b858e2d803994da1` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py`
action: replace · base sha256 `bcd8538b4c889e66fb89dc7187e21aebdcdc8a95793af8a2642d5bbfd652cea1` · base trailing newline: yes · new sha256 `62d7ecfab02363023392314b6d24ab40f802109a7ceffc95eced6d32e6a960fb` · new trailing newline: yes

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
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_cc_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.check import create_a1_check_pipeline
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


def create_check_pipeline() -> Pipeline:
    """TEMPORARY (A1 bundle 21): the new rule against the persisted ``crx_cc_a1_ability``;
    removed by the bundle's cleanup."""
    return create_a1_check_pipeline("cc", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py`
action: replace · base sha256 `d9c80826be5a36b98e8049bfebe1ad3ddd5b7e7732d9623a954273b03bfed837` · base trailing newline: yes · new sha256 `b4f488f99134182df2fc734478fda49790796da6f782c600c1509e7b669ac4db` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_check_pipeline, create_pipeline

__all__ = ["create_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `37c113db3d2f61a2869df81ab39279651523c80a12d1a62a69fd5b1dd7992def` · base trailing newline: yes · new sha256 `c61f90ed785079addf9ad5549b96f807573c7c7a316e52db9a29195409b8340c` · new trailing newline: yes

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
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.check import create_a1_check_pipeline
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


def create_check_pipeline() -> Pipeline:
    """TEMPORARY (A1 bundle 21): the new rule against the persisted ``crx_rl_a1_ability``;
    removed by the bundle's cleanup."""
    return create_a1_check_pipeline("rl", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/products/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/pipelines/products/features.py`
action: add · new sha256 `5300ed9e7688056c941a126d2a36826406e1ab922178b6c9ae93b248419dd3e8` · new trailing newline: yes

New:

`````python
"""Product feature pipeline: the customer's other products with us per month.

feat_product_holding, bo_rr_portf_actv_acct_mthly,
card balances, WM assets ────────────────────────────► feat_cif_cross_product_monthly

kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline(
        [
            node(
                func=feat_cif_cross_product.build,
                inputs={
                    "product_holding": "feat_product_holding",
                    "loan_portfolio": "bo_rr_portf_actv_acct_mthly",
                    # TODO(sonnet): the card balances and WM asset datasets the round-3
                    # snippet loaded for F4.
                    "card_balances": "prm_balance",
                    "wm_assets": "wm_fea_aum_balance",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:casa_features.history_months",
                },
                outputs="feat_cif_cross_product_monthly",
                name="build_feat_cif_cross_product_monthly",
                tags=["products", "features"],
            )
        ]
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
Clean up after mirror bundle 21_a1_evidence_family_rule.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id (CC datasets for the CC model_ids, RL for RL); skip folders that do not exist: `crx_<p>_a1_check_new` and the retired `crx_<p>_a1_liquidity_signals`.
- **Remove the temporary check** (everything marked TEMPORARY for A1 bundle 21):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_<p>_a1_check_new` entries and their comments;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_a1_check` and `crx_rl_a1_check` entries and their comments;
  - `crx_persona/cc_a1_ability/` and `rl_a1_ability/`: `create_check_pipeline` in `pipeline.py` (with its import) and in `__init__.py`;
  - delete `crx_persona/a1_ability/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "a1_check" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
