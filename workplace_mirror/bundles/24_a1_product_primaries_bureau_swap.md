# Mirror bundle 24 — A1: product primaries + bureau salary from the unified table

apply_bundle version: 7 · built 2026-11-12 from `ca3f382..79bc263` · source: 9 added, 12 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/24_a1_product_primaries_bureau_swap.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '24_a1_product_primaries_bureau_swap.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/24_a1_product_primaries_bureau_swap.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **Catalog and registry.** `catalog_products.yml` and `tmp_b24_check.yml` are new and `feat_cif_cross_product_monthly` now lives there only: confirm it is gone from `catalog_casa.yml` and defined exactly once in `conf/`. List every top-level key the apply removed from `catalog_casa.yml`, `catalog_bureau.yml`, `catalog_products.yml` and `pipeline_registry.py` compared with the last commit and put back any that is not `feat_cif_cross_product_monthly` (the `casa_windows*` entries and `genesys` must survive). `kedro registry list` shows `product_primary`, `product_features`, `product_features_b24_check`, `crx_cc_a1_b24_check` and `crx_rl_a1_b24_check`. `feat_bureau_salary_unified` must be defined exactly once in `conf/` (the mirror has it in `catalog_bureau.yml`; if the DE's entries were merged into `catalog_outputs.yml`, keep one, same path) and point at the parquet the DE wrote for every model_id.
2. **`derive_billing_amounts`.** `nodes/primary/products/prm_products.py` calls `prm_cc.derive_billing_amounts(tail, account_group)` exactly as bundle 21's node did; confirm the signature and that it returns `contract_idt`, `banking_date` and `minimum_due`.
3. **Callers of the moved helpers.** `grep -rn "feat_cif_casa import\|_require\|_wm_month\|_cif()" src`: nothing outside `feat_cif_casa.py` may still import its old private helpers (they are now `nodes/utils/frames.py`); fix any workplace-only caller and report it.
4. **Parameters.** `products.history_months` resolves (`parameters_products.yml`); `crx_persona.persona_start_date` / `persona_end_date` exist.
5. **Bureau swap.** `feat_cif_bureau_salary_monthly.build(unified)` reads `cif_id`, `salary_month_end`, `monthly_salary`, `salary_source`: confirm these names and types on the real `feat_bureau_salary_unified` schema. `grep -rn "loan_features\|_loan_bureau_salary\|feat_cif_bureau_salary_monthly.build" src`: no A1 code may still pass `loan_features`; report any other caller of the old `build(alerts)`.
6. **Tests.** Update the tests of `feat_cif_cross_product` for the new signature (primaries + WM; no `feat_product_holding`, no raw tables) and add tests for the three primaries; update the tests of `feat_cif_bureau_salary_monthly` (unified rows in, no alert types) and of `build_income_signals` (no `loan_features`); update any CASA test that imported `_require` / `_cif` / `_wm_month` / `months_back` from `feat_cif_casa`. Black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1: product_primary replaces the raw reads in product_features; bureau salary from feat_bureau_salary_unified (carry kept, RL loan salary dropped); temporary checks product_features_b24_check, crx_<p>_a1_b24_check (bundle 24)" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/24_a1_product_primaries_bureau_swap.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

The persisted tables are the baseline: do not re-run `product_features`, `bureau_salary_bounces` or the A1 pipelines before the checks. Set `model_id` in `conf/dev/globals_dev.yml` for each run.

**Step 7.** Run the checks.

**cc_60_180:** build the product primaries, then both checks:

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features_b24_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_b24_check
```

**rl_60_180, cc_180_plus, rl_180_plus:** the A1 check only (`crx_rl_a1_b24_check` for rl, `crx_cc_a1_b24_check` for cc):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_b24_check
```

Paste back, per model_id, every `=== B24 … START ===` … `END ===` block: `B24 PRODUCTS` and `B24 A1 INPUTS` (cc_60_180 only), `B24 BUREAU`, `B24 INCOME`, `B24 A1 OUTPUT`, `B24 A1 MOVES`. Also note the run time of each pipeline.

**Step 8.** After the blocks are reviewed, write the real tables for **all four model_ids**, in this order:

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

(`crx_rl_a1_ability` for the rl model_ids.) Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Two A1 changes in one bundle (the bureau swap planned as bundle 25 is folded in, user 2026-11-12): (1) the product inputs leave the raw tables, with no change to A1; (2) A1's bureau salary comes from the DE's unified table.

**Part 1: product primaries.** The A1 cross-product feature (`product_features`, F4) no longer reads raw tables. The raw Way4 card tables and the loan portfolio are read once, by a new primary pipeline `product_primary`; the feature node reads those primaries and the two WM asset features only (DESIGN_REVIEW §7: primary nodes read raw, feature nodes read primary or a WM feature). Part 1 changes no A1 input. Apply after bundle 21's cleanup (and bundle 23, which this branch was built on; no shared lines).

**New primaries** (`nodes/primary/products/prm_products.py`, all customers, the last `products.history_months` months up to the persona start month):
- `prm_card_contracts`: every Way4 card contract of a known client (`cif_id`, `contract_id`, `parent_contract_id`), from `raw_stg_client` + `raw_stg_contract`;
- `prm_card_month_end`: per `(contract_id, month_end)` with a billing row in the month: `level` (`BS_PMT_CYCLE_DUE` of the latest billing row) and `minimum_due` (latest balance snapshot in the month's last 5 days, via `derive_billing_amounts`), from `raw_stg_billing` / `raw_stg_balance` / `raw_stg_account_group`;
- `prm_loan_month_end`: every monthly loan snapshot of `bo_rr_portf_actv_acct_mthly`, renamed and typed (bucket, overdue days, instalment due, write-off date as loaded).
The workplace's `prm_contract` / `prm_balance` are spine-scoped (only the model's own accounts), which is why the node read raw: these new primaries hold every customer's cards.

**Feature node** (`feat_cif_cross_product.build`): inputs `prm_card_contracts`, `prm_card_month_end`, `prm_loan_month_end`, `wm_fea_casa_eod_avg_balance`, `wm_fea_wealth_holdings_by_cif`. Same `COLUMNS` and the same rules as bundle 21 (replaced cards out, current card = level ≤ 1, current loan = bucket 0 + no overdue days + not written off, assets > 0). "Current" stays in the feature layer; the primaries hold source values only.
- **One change:** the term-deposit holder rows without a balance (`deposit`, NULL balance, from `feat_product_holding`) are gone, and so is the `feat_product_holding` input. A1 never counted them (`xp_assets_aed` sums balances; `xp_holding` needs a balance above 0), so no A1 input moves.

**Tidy-ups:** the node no longer imports private helpers from `feat_cif_casa`: `months_back`, `require_columns`, `wm_month` and `cif_column` move to `nodes/utils/frames.py`, used by both (CASA logic unchanged). The pipeline has its own parameter `products.history_months` (12, as before via `casa_features.history_months`; new file `parameters_products.yml`). The `feat_cif_cross_product_monthly` catalog entry moves to the new `catalog_products.yml` (same path, so the existing table stays).

**Check 1** (temporary, `pipelines/products/check.py`, pipeline `product_features_b24_check`): builds the new table into `feat_cif_cross_product_monthly_b24_new` and compares it with the persisted bundle 21 table. Blocks `B24 PRODUCTS` (rows per type: old / new / only old / only new / values that differ) and `B24 A1 INPUTS` (customer-months whose A1 cross-product inputs differ). Expected: only `deposit` rows with a NULL balance are "only old"; everything else matches; A1 inputs differ in 0 customer-months. Tested locally on synthetic data against bundle 21's node: identical except that row kind.


**Part 2: bureau salary from `feat_bureau_salary_unified`** (spec `A1_ability_family_rule.md`, bureau section). `feat_cif_bureau_salary_monthly` stays the A1 contract and its catalog name and path do not change, but its node (`nodes/features/bureau/feat_cif_bureau_salary_monthly.py`, pipeline `bureau_salary_bounces`) now reads the DE's `feat_bureau_salary_unified` (read-only, already run in PROD for all four model_ids) instead of the alert feed: `cif_id` as string, `month_end` = `last_day(salary_month_end)`, `bureau_salary` = `monthly_salary`, plus `salary_source` for reporting. The unified table already picks one salary per CIF-month across `alert` > `salary_credit` > `bureau_salary` (bulk pull).
- **Kept:** the one-month carry (S14, `_with_next_month`; user 2026-11-11). A 0 row still ends the carry. The S12 level check for bureau-only windows is unchanged.
- **Dropped:** the RL loan salary (`feature_retail_loans`, `aecb_last_salary_credit_amount`; application-time, not a monthly series, user 2026-11-11): `_loan_bureau_salary`, the `loan_features` argument and the RL-only input in `a1_ability/pipeline.py`. `feature_retail_loans` itself is untouched.
- **What moves, by construction:** alert selection is now the DE's rule (latest `extract_date`, then the larger amount; closure alerts count only with an amount), `salary_credit` and pull months add rows, a usable amount beats a 0 in the same month, and RL loses the loan salary. The bounces node is unchanged (still the alert feed).

**Check 2** (temporary, `pipelines/crx_persona/a1_ability/check.py`, pipelines `crx_cc_a1_b24_check` / `crx_rl_a1_b24_check`): rebuilds the bureau feature into `feat_cif_bureau_salary_monthly_b24_new`, the income signals into `crx_<p>_a1_income_b24_new` and the A1 state into `crx_<p>_a1_b24_new` (the other signals are the persisted ones; no real output is touched), against the persisted A1 output. Blocks, for the latest month: `B24 BUREAU` (old vs new bureau CIF-months of the observation CIFs over the last 2W + 1 months: rows, zero rows, only old / only new / > 1% apart, new by `salary_source`), `B24 INCOME` (old x new bureau evidence in W, income source and income level), `B24 A1 OUTPUT`, `B24 A1 MOVES`. All four model_ids.

All temporary datasets are in one new file, `conf/base/catalog/tmp_b24_check.yml` (the bundle 24 product entry moved there from `catalog_products.yml`). Spec test 90/90 (the alert-type cases moved to the DE's code; new cases for pull and mid-month rows).

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
| replace | `conf/base/catalog/catalog_bureau.yml` |
| replace | `conf/base/catalog/catalog_casa.yml` |
| add | `conf/base/catalog/catalog_products.yml` |
| add | `conf/base/catalog/tmp_b24_check.yml` |
| add | `conf/base/parameters/parameters_products.yml` |
| replace | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py` |
| replace | `src/enbd_collections/nodes/features/casa/feat_cif_casa.py` |
| replace | `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` |
| add | `src/enbd_collections/nodes/primary/products/__init__.py` |
| add | `src/enbd_collections/nodes/primary/products/prm_products.py` |
| add | `src/enbd_collections/nodes/utils/frames.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| replace | `src/enbd_collections/pipelines/bureau/salary_bounces.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |
| add | `src/enbd_collections/pipelines/products/check.py` |
| replace | `src/enbd_collections/pipelines/products/features.py` |
| add | `src/enbd_collections/pipelines/products/primary.py` |

## Files

### FILE: `conf/base/catalog/catalog_bureau.yml`
action: replace · base sha256 `b11cccc0d0382114792455d7bcd0949980fb13f17c3edd606146f269aa5e57e0` · base trailing newline: yes · new sha256 `7192c9d518f98abc273c8cdb69acdbeb201d0515c170e531e4821d66d1d9244e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# Bureau salary and bounce datasets of the persona axes (pipeline bureau_salary_bounces).

# AECB-reported salary per (cif_id, month_end of the pull): the latest pull's level, all history.
feat_cif_bureau_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# DE-owned (branch bureau-pipeline-analysis, read-only here): one monthly salary per CIF unified across
# alert > salary_credit > bureau_salary sources. cif_id (long), salary_month_end (date),
# monthly_salary (double), salary_source (string). Replaces feat_cif_bureau_salary_monthly in A1 income.
feat_bureau_salary_unified:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/salary_unified"
  metadata:
    kedro-viz:
      layer: feature

# Bureau bounce pulls and new bounce events per (cif_id, month_end).
feat_cif_bureau_bounces_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_bounces_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

New:

`````yaml
# Bureau salary and bounce datasets of the persona axes (pipeline bureau_salary_bounces).

# A1's bureau salary per (cif_id, month_end): feat_bureau_salary_unified as the A1 contract.
feat_cif_bureau_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# DE-owned (branch bureau-pipeline-analysis, read-only here): one monthly salary per CIF unified across
# alert > salary_credit > bureau_salary sources. cif_id (long), salary_month_end (date),
# monthly_salary (double), salary_source (string). Read by feat_cif_bureau_salary_monthly.
feat_bureau_salary_unified:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/salary_unified"
  metadata:
    kedro-viz:
      layer: feature

# Bureau bounce pulls and new bounce events per (cif_id, month_end).
feat_cif_bureau_bounces_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_bounces_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature
`````

### FILE: `conf/base/catalog/catalog_casa.yml`
action: replace · base sha256 `18f6f92c6b228fe53a599c8883d149a7389960d5cdb03c4bc938a7dcd9aa5833` · base trailing newline: yes · new sha256 `83b62ecdae3a0761522e6f2c6b2a665381c005ab2852f23fbd11d6a825fa2d0a` · new trailing newline: yes

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

# The classified CASA legs of the A1 flow evidence (flow_class per leg, persona window only),
# one row per leg; the flows node starts from it (pipeline casa_features).
prm_casa_flow_legs:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/flow_legs"
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

# Salary (internal, external, consolidated), CASA inflow and net flow per (cif_id, month_end): the
# month and its trailing 3 / 6 / 12 month average, all history (casa_windows).
feat_cif_inflow_outflow_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Same columns as feat_cif_inflow_outflow_salary_monthly, but inflow / outflow / netflow are built
# from CASA-scheme account legs only (loans and other schemes excluded), all history (casa_windows_casa).
feat_cif_casa_inflow_outflow_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Copies of feat_cif_casa_inflow_outflow_salary_monthly with the model id hardcoded, so one pipeline
# (casa_windows_casa_all_models) can read all four. Each is written by casa_windows_casa run for that model_id.
feat_cif_casa_inflow_outflow_salary_monthly_cc_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_60_180/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_cc_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_180_plus/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_rl_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_60_180/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_rl_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_180_plus/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# All customers of the four models, one row per (cif_id, month_end), model-agnostic (shared
# namespace): union and de-duplication of the four tables above (casa_windows_casa_all_models).
feat_cif_casa_inflow_outflow_salary_monthly_all_models:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Copies of feat_cif_inflow_outflow_salary_monthly with the model id hardcoded, so one pipeline
# (casa_windows_all_models) can read all four. Each is written by casa_windows run for that model_id.
feat_cif_inflow_outflow_salary_monthly_cc_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_60_180/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_cc_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_180_plus/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_rl_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_60_180/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_rl_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_180_plus/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# All customers of the four models, one row per (cif_id, month_end), model-agnostic (shared
# namespace): union and de-duplication of the four tables above (casa_windows_all_models).
feat_cif_inflow_outflow_salary_monthly_all_models:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
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

# The classified CASA legs of the A1 flow evidence (flow_class per leg, persona window only),
# one row per leg; the flows node starts from it (pipeline casa_features).
prm_casa_flow_legs:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/casa/flow_legs"
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

# Salary (internal, external, consolidated), CASA inflow and net flow per (cif_id, month_end): the
# month and its trailing 3 / 6 / 12 month average, all history (casa_windows).
feat_cif_inflow_outflow_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Same columns as feat_cif_inflow_outflow_salary_monthly, but inflow / outflow / netflow are built
# from CASA-scheme account legs only (loans and other schemes excluded), all history (casa_windows_casa).
feat_cif_casa_inflow_outflow_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Copies of feat_cif_casa_inflow_outflow_salary_monthly with the model id hardcoded, so one pipeline
# (casa_windows_casa_all_models) can read all four. Each is written by casa_windows_casa run for that model_id.
feat_cif_casa_inflow_outflow_salary_monthly_cc_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_60_180/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_cc_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_180_plus/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_rl_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_60_180/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_casa_inflow_outflow_salary_monthly_rl_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_180_plus/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# All customers of the four models, one row per (cif_id, month_end), model-agnostic (shared
# namespace): union and de-duplication of the four tables above (casa_windows_casa_all_models).
feat_cif_casa_inflow_outflow_salary_monthly_all_models:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/casa/cif_casa_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# Copies of feat_cif_inflow_outflow_salary_monthly with the model id hardcoded, so one pipeline
# (casa_windows_all_models) can read all four. Each is written by casa_windows run for that model_id.
feat_cif_inflow_outflow_salary_monthly_cc_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_60_180/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_cc_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/cc_180_plus/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_rl_60_180:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_60_180/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_inflow_outflow_salary_monthly_rl_180_plus:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/rl_180_plus/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

# All customers of the four models, one row per (cif_id, month_end), model-agnostic (shared
# namespace): union and de-duplication of the four tables above (casa_windows_all_models).
feat_cif_inflow_outflow_salary_monthly_all_models:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:shared_id}/${globals:folders.feat}/casa/cif_inflow_outflow_salary_monthly"
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
`````

### FILE: `conf/base/catalog/catalog_products.yml`
action: add · new sha256 `7608f99a27895ec7cd5b1ddb90ba61ca1f07f1400d8edd14b2587362f55d1e1c` · new trailing newline: yes

New:

`````yaml
# Product primaries (pipeline product_primary) and the cross-product feature (product_features).

# Every Way4 card contract of a known client, all CIFs: cif_id, contract_id,
# parent_contract_id (the contract a newer one replaced).
prm_card_contracts:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/products/card_contracts"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Per (contract_id, month_end) with a billing row in the month: level (BS_PMT_CYCLE_DUE of
# the latest billing row) and minimum_due (latest balance snapshot in the month's last days).
prm_card_month_end:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/products/card_month_end"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Every monthly retail-loan snapshot (bo_rr_portf_actv_acct_mthly), all CIFs: cif_id,
# account_id, month_end, bucket, overdue days, instalment due, write-off date.
prm_loan_month_end:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/products/loan_month_end"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

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

### FILE: `conf/base/catalog/tmp_b24_check.yml`
action: add · new sha256 `7daee5d44c4b5512a795baf9e0bcf7e605cd6a1e5ea71668616c24ffd68179ba` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundle 24): the datasets of the bundle's checks (product_features_b24_check,
# crx_<p>_a1_b24_check); this file and their HDFS folders are removed by the cleanup.

feat_cif_cross_product_monthly_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/products/cif_cross_product_monthly_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

feat_cif_bureau_salary_monthly_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_salary_monthly_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: feature

crx_cc_a1_income_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_income_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: persona

crx_cc_a1_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: persona

crx_rl_a1_income_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_income_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: persona

crx_rl_a1_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_b24_new"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: persona
`````

### FILE: `conf/base/parameters/parameters_products.yml`
action: add · new sha256 `401c6d7430301f413bbc60ff0a1b351764ac28314c8c7aac286904e8df16f9bf` · new trailing newline: yes

New:

`````yaml
##################################################
# PRODUCTS (product_primary, product_features)
##################################################
products:
  # Calendar months kept up to and including the persona start month by the product
  # primaries and the cross-product feature: the A1 cross-product family reads the
  # observation month only, so this matches the CASA features' 12 months.
  history_months: 12
`````

### FILE: `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py`
action: replace · base sha256 `31863ef4c0fb89778fb9993283a8d8c6448c216fd5689c6a5aed1fefebe4448e` · base trailing newline: yes · new sha256 `0e2a8a5a0f02b3724772fe4d4c4860a33c600d3a7952235a2fcab3a28eaa471a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: AECB-reported salary per customer and pull month.

One row per ``(cif_id, month_end)`` with a salary alert, dated by the pull
(``extract_date``). ``bureau_salary`` is the salary reported on the month's latest pull, an
accurate level on that date, not a month's credit: salary rows are ``alert_type_number`` 31
(average salary changed) and 32 (salary account added) with an amount; 43 (salary account
closed) gives 0. Months without a pull have no row. How far a pull carries is decided by the
consumer.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

_SALARY_TYPES = (31, 32)
_CLOSED_TYPE = 43


def build(alerts: DataFrame) -> DataFrame:
    """The month's latest pull from ``prm_bureau_alert_enriched``; on the same pull a
    closure wins, then the largest amount."""
    columns = {"cif_id", "extract_date", "alert_type_number", "salary_credit_amount"}
    missing = sorted(columns - set(alerts.columns))
    if missing:
        raise ValueError(f"prm_bureau_alert_enriched is missing columns: {missing}")
    alert_type = F.col("alert_type_number").cast("double")
    amount = F.col("salary_credit_amount").cast("double")
    closed = alert_type == _CLOSED_TYPE
    latest = F.max(F.struct("pull_date", "closed", "amount")).alias("_latest")
    return (
        alerts.filter(
            F.col("cif_id").isNotNull()
            & (closed | (alert_type.isin(*_SALARY_TYPES) & (amount > 0)))
        )
        .select(
            F.col("cif_id").cast("string").alias("cif_id"),
            F.to_date("extract_date").alias("pull_date"),
            closed.alias("closed"),
            F.when(closed, 0.0).otherwise(amount).alias("amount"),
        )
        .groupBy("cif_id", F.last_day("pull_date").alias("month_end"))
        .agg(latest)
        .select("cif_id", "month_end", F.col("_latest.amount").alias("bureau_salary"))
    )
`````

New:

`````python
"""Feature node: bureau salary per customer and month, the A1 income contract.

One row per ``(cif_id, month_end)`` from the DE's ``feat_bureau_salary_unified``, which
picks one monthly salary per customer across three AECB sources (``alert`` change events,
``salary_credit`` application-time history, ``bureau_salary`` bulk-pull aggregates spread
back over 12 months):

* ``bureau_salary`` - the unified ``monthly_salary`` (AED; 0 = no usable amount that
  month, e.g. a salary account closed);
* ``salary_source`` - the source that gave it (reporting only).

Months without a row have no bureau salary. How far a row carries is decided by the
consumer (A1 carries it one month, S14). To swap the bureau source, rebuild this table
from the new one; the A1 engine reads only this contract.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import require_columns


def build(unified: DataFrame) -> DataFrame:
    """``cif_id`` (string), ``month_end``, ``bureau_salary``, ``salary_source`` from
    ``feat_bureau_salary_unified`` (already one row per customer and month)."""
    require_columns(
        unified,
        ["cif_id", "salary_month_end", "monthly_salary", "salary_source"],
        "feat_bureau_salary_unified",
    )
    return unified.filter(
        F.col("cif_id").isNotNull() & F.col("monthly_salary").isNotNull()
    ).select(
        F.trim(F.col("cif_id").cast("string")).alias("cif_id"),
        F.last_day("salary_month_end").alias("month_end"),
        F.col("monthly_salary").cast("double").alias("bureau_salary"),
        "salary_source",
    )
`````

### FILE: `src/enbd_collections/nodes/features/casa/feat_cif_casa.py`
action: replace · base sha256 `17dea7e8b3837fb9eb0915ba0dab2979504e145c3c37ee9dd946fb6b93fdc23b` · base trailing newline: yes · new sha256 `84858f724b751c138863dc1402add14c8f8fd05b8bc62bf16a285bf434bea94e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature nodes: monthly CASA features per customer, all customers.

Each table has one row per ``(cif_id, month_end)`` (plus ``lane`` / ``reason`` where
named) with any data; customers are CIFs, so every CASA account of the customer counts.
The FTR-based tables keep only legs on current and savings accounts (``prm_casa_accounts``):
the transaction table also holds the loan account itself. Values are raw: which lanes,
reasons or amounts count is decided by the consumers.

* ``feat_cif_internal_salary_monthly``  - salary credited with us per month (WM);
* ``feat_cif_casa_balance_monthly``     - CASA average balance and any flow per month (WM);
* ``feat_cif_casa_activity_monthly``    - transaction legs per month and lane (FTR);
* ``feat_cif_ext_card_payment_monthly`` - payments to registered external cards (WM);
* ``feat_cif_returns_monthly``          - returned-transaction events per reason (FTR);
* ``prm_casa_flow_legs``                - the classified CASA legs, saved so the flows node
  starts from them (FTR + WM labels);
* ``feat_cif_casa_flows_monthly``       - CASA money in / out per month and flow class from
  those legs (A1 evidence: ``FLOW_CLASSES``).

WM weekly tables carry ``week_number`` as ``yyyyMM0W`` (week 01-04 of the month).
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
    reason)`` from ``prm_casa_return_events`` - one event per ``(tran_id, tran_date)``, so
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


def _flag(column: str) -> Column:
    """A WM 0 / 1 flag column as an int, 0 when NULL."""
    return F.coalesce(F.col(column).cast("int"), F.lit(0))


# — Flow classes (A1 money in / out, specs/A1_ability_family_rule.md §3) ──────────
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
# WM's label for a transfer between the customer and their own account at another bank:
# ``self_transfer_flag`` = 1 on ``wm_pri_labelled_transactions`` (round-3 ``wm_labels``).
WM_SELF_COLUMN = "self_transfer_flag"
WM_SELF_VALUE = 1
# The other WM flags of the flow dictionary: a fee / charge, a loan payment, and a bank
# counterparty (``bank_transfer`` / ``local_`` / ``international_bank_transfer``).
WM_FEE_COLUMN, WM_LOAN_COLUMN = "fees_charges", "loan_payment_flag"
WM_BANK_COLUMNS = (
    "bank_transfer",
    "local_bank_transfer",
    "international_bank_transfer",
)
WM_LABEL_FLAGS = (WM_FEE_COLUMN, WM_LOAN_COLUMN, *WM_BANK_COLUMNS)
NET_DAYS = 3  # a counted leg mirrored within this many days by a non-evidence leg …
NET_TOLERANCE = 0.01  # … of the same amount (±1%) is dropped (bounce, reversal, sweep)


def flow_class() -> Column:
    """The ``FLOW_CLASSES`` class of a leg carrying ``lane`` (``transaction_lane``) and the
    WM labels ``wm_salary``, ``wm_self``, ``wm_fee``, ``wm_loan`` and ``wm_bank`` (false
    when unlabelled).

    The self label decides ``own_in_external`` / ``own_out_external`` outside the wash lane
    only; on it the lane's ``own_transfer`` stands (round-3 dictionary, lane first).

    Debits only, as in the round-3 flow dictionary: a fee label is ``bank_initiated``; a
    loan-payment label with no other-bank counterparty is ``unplaced`` (the instalment may
    be our own loan)."""
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    narration = F.upper(F.trim("tran_narration_1"))
    credit = F.col("tran_dc") == "C"
    debit = F.col("tran_dc") == "D"
    lane = F.col("lane")
    on_wash_lane = (
        lane == "wash"
    )  # the lane decides first: DDS returns carry the self label
    cheque = F.lit(False)
    for stem in _CHEQUE_STEMS:
        cheque |= F.coalesce(narration.startswith(stem), F.lit(False))
    return (
        F.when(lane.isin("signal", "refund", "reversal") | cheque, "reversal_return")
        .when(credit & F.col("wm_salary"), "salary")
        .when(F.col("wm_self") & credit & ~on_wash_lane, "own_in_external")
        .when(F.col("wm_self") & ~on_wash_lane, "own_out_external")
        .when(lane.isin("wash", "group_internal"), "own_transfer")
        .when(lane == "fee_interest", "bank_initiated")
        .when(lane.isin("card_payment", "own_loan"), "debt_to_us")
        .when(debit & F.col("wm_fee") & ~F.col("wm_salary"), "bank_initiated")
        .when(debit & F.col("wm_loan") & ~F.col("wm_bank"), "unplaced")
        .when(lane == "card_spend", "chosen_spend")
        .when((lane == "economic") & credit & (t == "CASH DEPOSIT"), "cash_in")
        .when((lane == "economic") & credit, "third_party_in")
        .when(lane == "economic", "chosen_spend")
        .otherwise("unplaced")
    )


def _net_mirrored(legs: DataFrame) -> DataFrame:
    """``legs`` without the counted legs (money in / out classes) that an opposite leg of
    a class that does not count mirrors: the same amount within ``NET_TOLERANCE``,
    0-``NET_DAYS`` days apart, on any account of the customer.

    Each non-counted leg is spread over the days it can mirror, so the match is an
    equi-join on customer, day and direction (never all legs of a customer against all).
    """
    counted = F.col("flow_class").isin(*MONEY_IN_CLASSES, *MONEY_OUT_CLASSES)
    days = F.sequence(
        F.date_sub("tran_date", NET_DAYS), F.date_add("tran_date", NET_DAYS)
    )
    mirrors = legs.filter(~counted & (F.col("flow_class") != "salary")).select(
        F.col("cif_id").alias("_cif"),
        F.explode(days).alias("_day"),
        F.when(F.col("tran_dc") == "C", "D")
        .when(F.col("tran_dc") == "D", "C")
        .alias("_dc"),
        F.col("amount").alias("_amt"),
    )
    hit = (
        (F.col("cif_id") == F.col("_cif"))
        & (F.col("tran_date") == F.col("_day"))
        & (F.col("tran_dc") == F.col("_dc"))
        & (F.abs(F.col("_amt") - F.col("amount")) <= NET_TOLERANCE * F.col("amount"))
    )
    mirrored = (
        legs.filter(counted)
        .join(mirrors, hit, "leftsemi")
        .select("cif_id", "tran_id", "tran_date", "tran_dc")
    )
    return legs.join(
        mirrored, on=["cif_id", "tran_id", "tran_date", "tran_dc"], how="left_anti"
    )


_TRANSACTION_COLUMNS = (
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
)
_LABEL_KEYS = ["cif_id", "tran_id", "tran_date", "tran_dc"]
_LABEL_COLUMNS = ("_sal", "_self", "_fee", "_loan", "_bank")


def _usable_key(*columns: str) -> Column:
    """True when every column is neither NULL nor blank (NULL when a column is NULL)."""
    usable = F.lit(True)
    for column in columns:
        usable &= F.length(F.trim(F.col(column).cast("string"))) > 0
    return usable


def _flow_labels(labelled: DataFrame, floor_day: date) -> DataFrame:
    """One row per ``(cif_id, tran_id, tran_date, tran_dc)`` of ``wm_pri_labelled_transactions``
    that carries a label the flow classes read, with ``_sal``, ``_self``, ``_fee``,
    ``_loan`` and ``_bank``.

    The table is partitioned by ``week_number`` (``yyyyMM0W``), so a bound on it lets Spark
    skip old partitions (one month of margin: a week can start in the month before its
    ``tran_date``; ``tran_date`` stays the exact filter). Only the key and flag columns are
    read. A row with every flag 0 / NULL would end up unlabelled anyway, so it is dropped
    before the aggregate; so is a group with no salary, self, fee or loan label (a bank
    flag alone changes nothing: it is read only together with the loan label)."""
    direction = F.when(F.lower(F.trim("in_out_flow")) == "inflow", "C").when(
        F.lower(F.trim("in_out_flow")) == "outflow", "D"
    )
    flags = ("salary_txn_flag", WM_SELF_COLUMN, *WM_LABEL_FLAGS)
    keep = ["cif_id", "tran_id", "tran_date", "in_out_flow", *flags]
    has_week = "week_number" in labelled.columns
    labelled = labelled.select(*keep, *(["week_number"] if has_week else []))
    if has_week:
        week_bound = int(months_back(floor_day, 1).strftime("%Y%m")) * 100 + 1
        labelled = labelled.filter(F.col("week_number") >= week_bound)
    carries_label = F.lit(False)
    for column in flags:
        carries_label |= _flag(column) != 0
    carries_label_we_use = (F.col("_sal") == 1) | (F.col("_self") == 1)
    carries_label_we_use |= (F.col("_fee") == 1) | (F.col("_loan") == 1)
    return (
        labelled.filter((F.to_date("tran_date") >= F.lit(floor_day)) & carries_label)
        .groupBy(
            _cif(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            direction.alias("tran_dc"),
        )
        .agg(
            F.max(F.coalesce(F.col("salary_txn_flag").cast("int"), F.lit(0))).alias(
                "_sal"
            ),
            F.max(
                F.coalesce(
                    (F.col(WM_SELF_COLUMN).cast("int") == WM_SELF_VALUE).cast("int"),
                    F.lit(0),
                )
            ).alias("_self"),
            F.max(_flag(WM_FEE_COLUMN)).alias("_fee"),
            F.max(_flag(WM_LOAN_COLUMN)).alias("_loan"),
            F.max(F.greatest(*[_flag(c) for c in WM_BANK_COLUMNS])).alias("_bank"),
        )
        .filter(carries_label_we_use)
    )


def build_casa_flow_legs(
    transactions: DataFrame,
    casa_accounts: DataFrame,
    labelled: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """One row per classified ``prm_casa_transactions`` leg on CASA accounts, from the
    first of the last ``history_months`` months up to the persona start month on:
    ``cif_id``, ``tran_id``, ``tran_date``, ``tran_dc``, ``amount``, ``flow_class`` and
    ``event_month`` (the first of the leg's month, the partition).

    Salary and WM's own-account-elsewhere label come from ``wm_pri_labelled_transactions``
    joined on ``(cif_id, tran_id, tran_date)`` and the direction (``in_out_flow``), as in
    round 3. Saved on its own so the heavy join / classification is read once and a failed
    run restarts from here (``build_casa_flows`` nets and aggregates it)."""
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
        [
            "cif_id",
            "tran_id",
            "tran_date",
            "in_out_flow",
            "salary_txn_flag",
            WM_SELF_COLUMN,
            *WM_LABEL_FLAGS,
        ],
        "wm_pri_labelled_transactions",
    )
    floor_day = months_back(persona_start_date, history_months - 1)
    floor = F.lit(floor_day)
    labels = _flow_labels(labelled, floor_day)
    legs = (
        _on_casa_accounts(transactions.select(*_TRANSACTION_COLUMNS), casa_accounts)
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
    )
    # A leg without a usable key can never match a label; in the join they would all hash
    # to one partition, so they skip it (every label column NULL = unlabelled).
    usable = _usable_key("cif_id", "tran_id", "tran_dc", "tran_date")
    unkeyed = legs.filter(~F.coalesce(usable, F.lit(False)))
    keyed = legs.filter(F.coalesce(usable, F.lit(False))).join(
        labels, on=_LABEL_KEYS, how="left"
    )
    unkeyed = unkeyed.select(
        *legs.columns,
        *[F.lit(None).cast("int").alias(c) for c in _LABEL_COLUMNS],
    )
    legs = (
        keyed.unionByName(unkeyed)
        .withColumn("wm_salary", F.coalesce(F.col("_sal"), F.lit(0)) == 1)
        .withColumn("wm_self", F.coalesce(F.col("_self"), F.lit(0)) == 1)
        .withColumn("wm_fee", F.coalesce(F.col("_fee"), F.lit(0)) == 1)
        .withColumn("wm_loan", F.coalesce(F.col("_loan"), F.lit(0)) == 1)
        .withColumn("wm_bank", F.coalesce(F.col("_bank"), F.lit(0)) == 1)
        .withColumn("flow_class", flow_class())
    )
    # One shuffle by ``event_month`` so each month folder gets one file, not one per
    # shuffle partition (the partitioned overwrite commits a rename per task file).
    return legs.select(
        "cif_id",
        "tran_id",
        "tran_date",
        "tran_dc",
        "amount",
        "flow_class",
        F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd").alias("event_month"),
    ).repartition("event_month")


def build_casa_flows(legs: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, flow_class)``: ``legs``, ``credit_aed``, ``debit_aed``
    and ``max_leg_aed`` of the classified legs (``build_casa_flow_legs``). Counted legs
    mirrored by a leg that does not count are dropped (``_net_mirrored``)."""
    _require(
        legs,
        ["cif_id", "tran_id", "tran_date", "tran_dc", "amount", "flow_class"],
        "prm_casa_flow_legs",
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

New:

`````python
"""Feature nodes: monthly CASA features per customer, all customers.

Each table has one row per ``(cif_id, month_end)`` (plus ``lane`` / ``reason`` where
named) with any data; customers are CIFs, so every CASA account of the customer counts.
The FTR-based tables keep only legs on current and savings accounts (``prm_casa_accounts``):
the transaction table also holds the loan account itself. Values are raw: which lanes,
reasons or amounts count is decided by the consumers.

* ``feat_cif_internal_salary_monthly``  - salary credited with us per month (WM);
* ``feat_cif_casa_balance_monthly``     - CASA average balance and any flow per month (WM);
* ``feat_cif_casa_activity_monthly``    - transaction legs per month and lane (FTR);
* ``feat_cif_ext_card_payment_monthly`` - payments to registered external cards (WM);
* ``feat_cif_returns_monthly``          - returned-transaction events per reason (FTR);
* ``prm_casa_flow_legs``                - the classified CASA legs, saved so the flows node
  starts from them (FTR + WM labels);
* ``feat_cif_casa_flows_monthly``       - CASA money in / out per month and flow class from
  those legs (A1 evidence: ``FLOW_CLASSES``).

WM weekly tables carry ``week_number`` as ``yyyyMM0W`` (week 01-04 of the month).
"""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    months_back,
    require_columns,
    wm_month,
)

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


def _wm_week_date(week_number: str = "week_number") -> Column:
    """The middle of week W of the month (day 4, 11, 18 or 25): within 4 days of any
    day of that week."""
    week = F.substring(F.col(week_number).cast("string"), 7, 2).cast("int")
    return F.date_add(wm_month(week_number), 7 * week - 4)


def build_internal_salary(wm_salary: DataFrame) -> DataFrame:
    """``salary``: the month's total of salary-flagged credits with us, recovered from
    every weekly snapshot of ``wm_fea_salary_days_since_increment`` (all history).

    Each snapshot carries the latest salary month's total and the days from the first of
    that month to the snapshot; the snapshot's week date minus those days lands within a
    few days of the first of the salary month, so it is rounded to the nearest first.
    Snapshots that see the same month collapse to its largest total.
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
    credited = F.date_sub(
        _wm_week_date(), F.col("ft_days_since_salary_transaction").cast("int")
    )
    month = F.trunc(F.date_add(credited, 15), "month")  # nearest first of a month
    return (
        wm_salary.filter(
            (F.col("ft_last_salary_amount") > 0)
            & F.col("ft_days_since_salary_transaction").isNotNull()
        )
        .groupBy(cif_column(), F.last_day(month).alias("month_end"))
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
    require_columns(
        wm_casa_balance,
        ["cif_id", "week_number", _CASA_BALANCE],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
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
        wm_casa_balance.filter(wm_month() >= floor)
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(last_week.alias("_last"))
        .select("cif_id", "month_end", F.col("_last.v").alias("casa_balance"))
    )
    moved = (F.col(_CASA_IN) > 0) | (F.col(_CASA_OUT) > 0)
    flow = (
        wm_casa_flow.filter(wm_month() >= floor)
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
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
    require_columns(casa_accounts, ["foracid"], "prm_casa_accounts")
    accounts = casa_accounts.select("foracid").distinct()
    return legs.withColumn("foracid", F.trim(F.col("foracid").cast("string"))).join(
        accounts, on="foracid", how="leftsemi"
    )


def build_casa_activity(transactions: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, lane)``: ``legs`` and the credit / debit AED of the
    ``prm_casa_transactions`` legs on CASA accounts (its whole history)."""
    require_columns(
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
        .groupBy(
            cif_column(), F.last_day(F.to_date("tran_date")).alias("month_end"), "lane"
        )
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
    require_columns(
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
    require_columns(beneficiary_cards, ["card_number"], "prm_beneficiary_cards")
    floor = F.lit(months_back(persona_start_date, history_months - 1))
    cards = beneficiary_cards.select(F.col("card_number").alias("transaction_acid"))
    return (
        labelled.filter(
            (F.to_date("tran_date") >= floor)
            & (F.col("in_out_flow") == "outflow")
            & (F.col("product_category") == "CASA")
        )
        .join(F.broadcast(cards), on="transaction_acid", how="leftsemi")
        .groupBy(cif_column(), F.last_day(F.to_date("tran_date")).alias("month_end"))
        .agg(
            F.max(F.col("tran_amt").cast("double")).alias("max_payment"),
            F.count(F.lit(1)).alias("payments"),
        )
    )


def build_returns(return_events: DataFrame, casa_accounts: DataFrame) -> DataFrame:
    """``events``: returned transactions on CASA accounts per ``(cif_id, month_end,
    reason)`` from ``prm_casa_return_events`` - one event per ``(tran_id, tran_date)``, so
    the debit and credit legs of a return count once."""
    require_columns(
        return_events,
        ["cif_id", "foracid", "tran_id", "tran_date", "reason_for_excluding"],
        "prm_casa_return_events",
    )
    one_event = Window.partitionBy("cif_id", "tran_id", "tran_date")
    return (
        _on_casa_accounts(return_events, casa_accounts)
        .select(
            cif_column(),
            "tran_id",
            F.to_date("tran_date").alias("tran_date"),
            F.trim("reason_for_excluding").alias("reason"),
        )
        .withColumn("_rn", F.row_number().over(one_event.orderBy("reason")))
        .filter(F.col("_rn") == 1)
        .groupBy("cif_id", F.last_day("tran_date").alias("month_end"), "reason")
        .agg(F.count(F.lit(1)).alias("events"))
    )


def _flag(column: str) -> Column:
    """A WM 0 / 1 flag column as an int, 0 when NULL."""
    return F.coalesce(F.col(column).cast("int"), F.lit(0))


# — Flow classes (A1 money in / out, specs/A1_ability_family_rule.md §3) ──────────
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
# WM's label for a transfer between the customer and their own account at another bank:
# ``self_transfer_flag`` = 1 on ``wm_pri_labelled_transactions`` (round-3 ``wm_labels``).
WM_SELF_COLUMN = "self_transfer_flag"
WM_SELF_VALUE = 1
# The other WM flags of the flow dictionary: a fee / charge, a loan payment, and a bank
# counterparty (``bank_transfer`` / ``local_`` / ``international_bank_transfer``).
WM_FEE_COLUMN, WM_LOAN_COLUMN = "fees_charges", "loan_payment_flag"
WM_BANK_COLUMNS = (
    "bank_transfer",
    "local_bank_transfer",
    "international_bank_transfer",
)
WM_LABEL_FLAGS = (WM_FEE_COLUMN, WM_LOAN_COLUMN, *WM_BANK_COLUMNS)
NET_DAYS = 3  # a counted leg mirrored within this many days by a non-evidence leg …
NET_TOLERANCE = 0.01  # … of the same amount (±1%) is dropped (bounce, reversal, sweep)


def flow_class() -> Column:
    """The ``FLOW_CLASSES`` class of a leg carrying ``lane`` (``transaction_lane``) and the
    WM labels ``wm_salary``, ``wm_self``, ``wm_fee``, ``wm_loan`` and ``wm_bank`` (false
    when unlabelled).

    The self label decides ``own_in_external`` / ``own_out_external`` outside the wash lane
    only; on it the lane's ``own_transfer`` stands (round-3 dictionary, lane first).

    Debits only, as in the round-3 flow dictionary: a fee label is ``bank_initiated``; a
    loan-payment label with no other-bank counterparty is ``unplaced`` (the instalment may
    be our own loan)."""
    t = F.regexp_replace(F.upper(F.trim("tran_type")), r"\s+", " ")
    narration = F.upper(F.trim("tran_narration_1"))
    credit = F.col("tran_dc") == "C"
    debit = F.col("tran_dc") == "D"
    lane = F.col("lane")
    on_wash_lane = (
        lane == "wash"
    )  # the lane decides first: DDS returns carry the self label
    cheque = F.lit(False)
    for stem in _CHEQUE_STEMS:
        cheque |= F.coalesce(narration.startswith(stem), F.lit(False))
    return (
        F.when(lane.isin("signal", "refund", "reversal") | cheque, "reversal_return")
        .when(credit & F.col("wm_salary"), "salary")
        .when(F.col("wm_self") & credit & ~on_wash_lane, "own_in_external")
        .when(F.col("wm_self") & ~on_wash_lane, "own_out_external")
        .when(lane.isin("wash", "group_internal"), "own_transfer")
        .when(lane == "fee_interest", "bank_initiated")
        .when(lane.isin("card_payment", "own_loan"), "debt_to_us")
        .when(debit & F.col("wm_fee") & ~F.col("wm_salary"), "bank_initiated")
        .when(debit & F.col("wm_loan") & ~F.col("wm_bank"), "unplaced")
        .when(lane == "card_spend", "chosen_spend")
        .when((lane == "economic") & credit & (t == "CASH DEPOSIT"), "cash_in")
        .when((lane == "economic") & credit, "third_party_in")
        .when(lane == "economic", "chosen_spend")
        .otherwise("unplaced")
    )


def _net_mirrored(legs: DataFrame) -> DataFrame:
    """``legs`` without the counted legs (money in / out classes) that an opposite leg of
    a class that does not count mirrors: the same amount within ``NET_TOLERANCE``,
    0-``NET_DAYS`` days apart, on any account of the customer.

    Each non-counted leg is spread over the days it can mirror, so the match is an
    equi-join on customer, day and direction (never all legs of a customer against all).
    """
    counted = F.col("flow_class").isin(*MONEY_IN_CLASSES, *MONEY_OUT_CLASSES)
    days = F.sequence(
        F.date_sub("tran_date", NET_DAYS), F.date_add("tran_date", NET_DAYS)
    )
    mirrors = legs.filter(~counted & (F.col("flow_class") != "salary")).select(
        F.col("cif_id").alias("_cif"),
        F.explode(days).alias("_day"),
        F.when(F.col("tran_dc") == "C", "D")
        .when(F.col("tran_dc") == "D", "C")
        .alias("_dc"),
        F.col("amount").alias("_amt"),
    )
    hit = (
        (F.col("cif_id") == F.col("_cif"))
        & (F.col("tran_date") == F.col("_day"))
        & (F.col("tran_dc") == F.col("_dc"))
        & (F.abs(F.col("_amt") - F.col("amount")) <= NET_TOLERANCE * F.col("amount"))
    )
    mirrored = (
        legs.filter(counted)
        .join(mirrors, hit, "leftsemi")
        .select("cif_id", "tran_id", "tran_date", "tran_dc")
    )
    return legs.join(
        mirrored, on=["cif_id", "tran_id", "tran_date", "tran_dc"], how="left_anti"
    )


_TRANSACTION_COLUMNS = (
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
)
_LABEL_KEYS = ["cif_id", "tran_id", "tran_date", "tran_dc"]
_LABEL_COLUMNS = ("_sal", "_self", "_fee", "_loan", "_bank")


def _usable_key(*columns: str) -> Column:
    """True when every column is neither NULL nor blank (NULL when a column is NULL)."""
    usable = F.lit(True)
    for column in columns:
        usable &= F.length(F.trim(F.col(column).cast("string"))) > 0
    return usable


def _flow_labels(labelled: DataFrame, floor_day: date) -> DataFrame:
    """One row per ``(cif_id, tran_id, tran_date, tran_dc)`` of ``wm_pri_labelled_transactions``
    that carries a label the flow classes read, with ``_sal``, ``_self``, ``_fee``,
    ``_loan`` and ``_bank``.

    The table is partitioned by ``week_number`` (``yyyyMM0W``), so a bound on it lets Spark
    skip old partitions (one month of margin: a week can start in the month before its
    ``tran_date``; ``tran_date`` stays the exact filter). Only the key and flag columns are
    read. A row with every flag 0 / NULL would end up unlabelled anyway, so it is dropped
    before the aggregate; so is a group with no salary, self, fee or loan label (a bank
    flag alone changes nothing: it is read only together with the loan label)."""
    direction = F.when(F.lower(F.trim("in_out_flow")) == "inflow", "C").when(
        F.lower(F.trim("in_out_flow")) == "outflow", "D"
    )
    flags = ("salary_txn_flag", WM_SELF_COLUMN, *WM_LABEL_FLAGS)
    keep = ["cif_id", "tran_id", "tran_date", "in_out_flow", *flags]
    has_week = "week_number" in labelled.columns
    labelled = labelled.select(*keep, *(["week_number"] if has_week else []))
    if has_week:
        week_bound = int(months_back(floor_day, 1).strftime("%Y%m")) * 100 + 1
        labelled = labelled.filter(F.col("week_number") >= week_bound)
    carries_label = F.lit(False)
    for column in flags:
        carries_label |= _flag(column) != 0
    carries_label_we_use = (F.col("_sal") == 1) | (F.col("_self") == 1)
    carries_label_we_use |= (F.col("_fee") == 1) | (F.col("_loan") == 1)
    return (
        labelled.filter((F.to_date("tran_date") >= F.lit(floor_day)) & carries_label)
        .groupBy(
            cif_column(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            direction.alias("tran_dc"),
        )
        .agg(
            F.max(F.coalesce(F.col("salary_txn_flag").cast("int"), F.lit(0))).alias(
                "_sal"
            ),
            F.max(
                F.coalesce(
                    (F.col(WM_SELF_COLUMN).cast("int") == WM_SELF_VALUE).cast("int"),
                    F.lit(0),
                )
            ).alias("_self"),
            F.max(_flag(WM_FEE_COLUMN)).alias("_fee"),
            F.max(_flag(WM_LOAN_COLUMN)).alias("_loan"),
            F.max(F.greatest(*[_flag(c) for c in WM_BANK_COLUMNS])).alias("_bank"),
        )
        .filter(carries_label_we_use)
    )


def build_casa_flow_legs(
    transactions: DataFrame,
    casa_accounts: DataFrame,
    labelled: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """One row per classified ``prm_casa_transactions`` leg on CASA accounts, from the
    first of the last ``history_months`` months up to the persona start month on:
    ``cif_id``, ``tran_id``, ``tran_date``, ``tran_dc``, ``amount``, ``flow_class`` and
    ``event_month`` (the first of the leg's month, the partition).

    Salary and WM's own-account-elsewhere label come from ``wm_pri_labelled_transactions``
    joined on ``(cif_id, tran_id, tran_date)`` and the direction (``in_out_flow``), as in
    round 3. Saved on its own so the heavy join / classification is read once and a failed
    run restarts from here (``build_casa_flows`` nets and aggregates it)."""
    require_columns(
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
    require_columns(
        labelled,
        [
            "cif_id",
            "tran_id",
            "tran_date",
            "in_out_flow",
            "salary_txn_flag",
            WM_SELF_COLUMN,
            *WM_LABEL_FLAGS,
        ],
        "wm_pri_labelled_transactions",
    )
    floor_day = months_back(persona_start_date, history_months - 1)
    floor = F.lit(floor_day)
    labels = _flow_labels(labelled, floor_day)
    legs = (
        _on_casa_accounts(transactions.select(*_TRANSACTION_COLUMNS), casa_accounts)
        .filter(F.to_date("tran_date") >= floor)
        .withColumn("lane", transaction_lane())
        .select(
            cif_column(),
            F.trim(F.col("tran_id").cast("string")).alias("tran_id"),
            F.to_date("tran_date").alias("tran_date"),
            "tran_dc",
            "tran_type",
            "tran_narration_1",
            "lane",
            F.col("actual_tran_amt_aed").cast("double").alias("amount"),
        )
    )
    # A leg without a usable key can never match a label; in the join they would all hash
    # to one partition, so they skip it (every label column NULL = unlabelled).
    usable = _usable_key("cif_id", "tran_id", "tran_dc", "tran_date")
    unkeyed = legs.filter(~F.coalesce(usable, F.lit(False)))
    keyed = legs.filter(F.coalesce(usable, F.lit(False))).join(
        labels, on=_LABEL_KEYS, how="left"
    )
    unkeyed = unkeyed.select(
        *legs.columns,
        *[F.lit(None).cast("int").alias(c) for c in _LABEL_COLUMNS],
    )
    legs = (
        keyed.unionByName(unkeyed)
        .withColumn("wm_salary", F.coalesce(F.col("_sal"), F.lit(0)) == 1)
        .withColumn("wm_self", F.coalesce(F.col("_self"), F.lit(0)) == 1)
        .withColumn("wm_fee", F.coalesce(F.col("_fee"), F.lit(0)) == 1)
        .withColumn("wm_loan", F.coalesce(F.col("_loan"), F.lit(0)) == 1)
        .withColumn("wm_bank", F.coalesce(F.col("_bank"), F.lit(0)) == 1)
        .withColumn("flow_class", flow_class())
    )
    # One shuffle by ``event_month`` so each month folder gets one file, not one per
    # shuffle partition (the partitioned overwrite commits a rename per task file).
    return legs.select(
        "cif_id",
        "tran_id",
        "tran_date",
        "tran_dc",
        "amount",
        "flow_class",
        F.date_format(F.trunc("tran_date", "month"), "yyyy-MM-dd").alias("event_month"),
    ).repartition("event_month")


def build_casa_flows(legs: DataFrame) -> DataFrame:
    """Per ``(cif_id, month_end, flow_class)``: ``legs``, ``credit_aed``, ``debit_aed``
    and ``max_leg_aed`` of the classified legs (``build_casa_flow_legs``). Counted legs
    mirrored by a leg that does not count are dropped (``_net_mirrored``)."""
    require_columns(
        legs,
        ["cif_id", "tran_id", "tran_date", "tran_dc", "amount", "flow_class"],
        "prm_casa_flow_legs",
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

### FILE: `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py`
action: replace · base sha256 `967ae1a3e02a8000aef14d9f08adfe91cfd8755a1d4210c199577db4b307d107` · base trailing newline: yes · new sha256 `979a803fb21087fd82602f4bd457878ed78318dfe470a6c1cdbd41cf21019e65` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets: deposits, investments, WM; NULL for
  credit products, and for a term-deposit holder without a balance snapshot);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 id for cards, ``acct_num`` for loans), so the A1 engine
can leave out the scored account itself. The asset sources are per customer, not per
account: their rows carry the fixed ids ``ASSET_IDS`` (they never equal a spine account).
Supplementary cards post to their contract and never appear as a product of their own;
a card that a newer card replaced (``parent_contract_idt``) is left out, so the scored
card's predecessor is not "another card". CASA balances are never a product here (they
are A1's money held, ``feat_cif_casa_balance_monthly``).

Sources (the ones the round-3 F4 builder loaded): ``wm_fea_casa_eod_avg_balance``
(``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the CASA columns are never read),
``wm_fea_wealth_holdings_by_cif`` (``etw_total_market_value_aed``),
``feat_product_holding`` (term-deposit holders), ``bo_rr_portf_actv_acct_mthly`` (loans)
and the raw Way4 client / contract / billing / balance / account-group tables (cards:
``derive_billing_amounts`` is the repo's own minimum-due derivation).
"""

# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    _cif,
    _require,
    _wm_month,
    months_back,
)
from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts

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
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (CC code: 1 = not overdue)
BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _wm_last_week(df: DataFrame, columns: list[str], floor) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the month's
    last week, from the month of ``floor`` on."""
    return (
        df.filter(_wm_month() >= F.lit(floor))
        .groupBy(_cif(), F.last_day(_wm_month()).alias("month_end"))
        .agg(
            *[
                F.max(
                    F.struct(
                        F.col("week_number").cast("string").alias("w"),
                        F.col(c).cast("double").alias("v"),
                    )
                )["v"].alias(c)
                for c in columns
            ]
        )
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series; a
    balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    none = F.lit(None)
    return (
        series.filter(F.col(column) > 0)
        .select(
            "cif_id",
            "month_end",
            F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
            F.lit(product_type).alias("product_type"),
            F.col(column).alias("balance_aed"),
            none.cast("int").alias("is_current"),
            none.cast("double").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def _wm_assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    _require(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    _require(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _term_deposit_holders(product_holding: DataFrame, floor) -> DataFrame:
    """``deposit`` rows without a balance for the months ``feat_product_holding`` counts a
    term deposit (``month_number`` = ``yyyyMMdd``): the holding is known, the amount is
    not."""
    _require(
        product_holding,
        ["cif_id", "month_number", "term_deposits_total_active_accounts"],
        "feat_product_holding",
    )
    month_end = F.last_day(F.to_date(F.col("month_number").cast("string"), "yyyyMMdd"))
    holders = (
        product_holding.filter(F.col("term_deposits_total_active_accounts") > 0)
        .select(_cif(), month_end.alias("month_end"))
        .filter(F.col("month_end") >= F.lit(floor))
        .distinct()
    )
    none = F.lit(None)
    return holders.select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS["deposit"]).alias("product_account_id"),
        F.lit("deposit").alias("product_type"),
        none.cast("double").alias("balance_aed"),
        none.cast("int").alias("is_current"),
        none.cast("double").alias("instalment_aed"),
    )


def _loans(loan_portfolio: DataFrame, floor) -> DataFrame:
    """``loan`` rows: every retail loan in the monthly portfolio snapshot; current = bucket
    0, no overdue days and not written off, the instalment is the one due."""
    columns = [
        "cust_num",
        "acct_num",
        "ss_dt",
        "ra_delq_bkt",
        "ra_ovd_days",
        "ra_instl_due_amt",
        "ra_woff_dt",
    ]
    _require(loan_portfolio, columns, "bo_rr_portf_actv_acct_mthly")
    overdue = F.coalesce(F.col("ra_ovd_days").cast("double"), F.lit(0.0))
    current = (
        (F.col("ra_delq_bkt").cast("int") == 0)
        & (overdue <= 0)
        & F.col("ra_woff_dt").isNull()
    )
    return (
        loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor))
        .select(
            F.col("cust_num").cast("string").alias("cif_id"),
            F.last_day(F.to_date("ss_dt")).alias("month_end"),
            F.trim(F.col("acct_num").cast("string")).alias("product_account_id"),
            F.lit("loan").alias("product_type"),
            F.lit(None).cast("double").alias("balance_aed"),
            current.cast("int").alias("is_current"),
            F.col("ra_instl_due_amt").cast("double").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def _card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id, contract_id, parent_id`` of every card contract (``ident_number`` is the
    CIF); a contract that a newer one replaced is left out."""
    _require(client, ["client_idt", "ident_number"], "raw_stg_client")
    _require(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", F.trim(F.col("ident_number").cast("string")).alias("cif_id")
    ).distinct()
    contracts = (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_id"),
        )
        .distinct()
    )
    replaced = contracts.select(F.col("parent_id").alias("contract_id")).distinct()
    return contracts.join(replaced, "contract_id", "left_anti")


def _card_levels(billing: DataFrame, contracts: DataFrame, lo) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    _require(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = (
        billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_id", F.col("contract_idt").cast("long"))
        .join(F.broadcast(contracts.select("contract_id")), "contract_id", "left_semi")
        .select(
            "contract_id",
            F.col("billing_date").cast(DateType()).alias("bdate"),
            F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
            .cast("int")
            .alias("level"),
        )
        .withColumn("month_end", F.last_day("bdate"))
    )
    latest = Window.partitionBy("contract_id", "month_end").orderBy(
        F.col("bdate").desc()
    )
    return (
        rows.withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .select("contract_id", "month_end", "level")
    )


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, contracts: DataFrame, lo
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot in
    the last ``BALANCE_TAIL_DAYS`` days of the month."""
    _require(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .join(
            F.broadcast(contracts.select(F.col("contract_id").alias("contract_idt"))),
            "contract_idt",
            "left_semi",
        )
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    latest = Window.partitionBy("contract_idt", F.last_day("banking_date")).orderBy(
        F.col("banking_date").desc()
    )
    return (
        amounts.withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .select(
            F.col("contract_idt").alias("contract_id"),
            F.last_day("banking_date").alias("month_end"),
            F.col("minimum_due").cast("double").alias("min_due"),
        )
    )


def _cards(
    client: DataFrame,
    contract: DataFrame,
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    floor,
) -> DataFrame:
    """``card`` rows: a contract with a billing row in the month; current = billing level
    at most ``CARD_CURRENT_MAX_LEVEL``; the instalment is the month's minimum due."""
    lo = floor - datetime.timedelta(days=LOAD_LAG_DAYS)
    contracts = _card_contracts(client, contract)
    month = _card_levels(billing, contracts, lo).join(
        _card_minimum_due(balance, account_group, contracts, lo),
        ["contract_id", "month_end"],
        "left",
    )
    return (
        month.filter(F.col("month_end") >= F.lit(floor))
        .join(contracts.select("cif_id", "contract_id"), "contract_id")
        .select(
            "cif_id",
            "month_end",
            F.col("contract_id").cast("string").alias("product_account_id"),
            F.lit("card").alias("product_type"),
            F.lit(None).cast("double").alias("balance_aed"),
            (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
            F.col("min_due").alias("instalment_aed"),
        )
        .select(*COLUMNS)
    )


def build(
    product_holding: DataFrame,
    loan_portfolio: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    card_client: DataFrame,
    card_contract: DataFrame,
    card_billing: DataFrame,
    card_balance: DataFrame,
    card_account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the first of the last ``history_months`` months up to the persona
    start month on, for all customers (the persona scope is applied by the A1 engine's
    join on the observation base).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = months_back(persona_start_date, history_months - 1)
    deposits, investments, wm = _wm_assets(wm_balances, wm_holdings, floor)
    holders = _term_deposit_holders(product_holding, floor).join(
        deposits.select("cif_id", "month_end"), ["cif_id", "month_end"], "left_anti"
    )
    cards = _cards(
        card_client,
        card_contract,
        card_billing,
        card_balance,
        card_account_group,
        floor,
    )
    parts = [deposits, investments, wm, holders, _loans(loan_portfolio, floor), cards]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

New:

`````python
"""Feature node: the customer's other products with us per month (A1 cross-product, F4).

One row per ``(cif_id, month_end, product_account_id)`` for every product the customer
holds with us at that month end:

* ``product_type`` - ``deposit`` (term deposits), ``investment``, ``wm`` (WM assets under
  management), ``card`` or ``loan``;
* ``balance_aed`` - the month-end balance (assets; NULL for credit products);
* ``is_current`` - credit products: 0 DPD at the month end (NULL for assets);
* ``instalment_aed`` - credit products: the monthly instalment (loans) or minimum due
  (cards) at the month end (NULL for assets).

``product_account_id`` is the account / contract id the persona spines use
(``account_id``: the Way4 contract id for cards, ``acct_num`` for loans), so the A1 engine
can leave out the scored account itself. The WM asset sources are per customer, not per
account: their rows carry the fixed ids ``ASSET_IDS`` (they never equal a spine account).
Supplementary cards post to their contract and never appear as a product of their own; a
card that a newer card replaced is left out, so the scored card's predecessor is not
"another card". CASA balances are never a product here (they are A1's money held,
``feat_cif_casa_balance_monthly``).

Sources: the primaries ``prm_card_contracts``, ``prm_card_month_end`` and
``prm_loan_month_end`` (pipeline ``product_primary``), and WM's
``wm_fea_casa_eod_avg_balance`` (``avg_itd_eod_balance``, ``avg_inv_eod_balance``; the
CASA columns are never read) and ``wm_fea_wealth_holdings_by_cif``
(``etw_total_market_value_aed``).
"""

from __future__ import annotations

import datetime
from functools import reduce

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.utils.frames import (
    cif_column,
    months_back,
    require_columns,
    wm_month,
)

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
# Fixed ids of the per-customer asset rows (one row per customer, month and type).
ASSET_IDS = {"deposit": "ITD", "investment": "INV", "wm": "WM_AUM"}
CARD_CURRENT_MAX_LEVEL = 1  # billing level of a current card (Way4: 1 = not overdue)


def _null(spark_type: str) -> Column:
    """A typed NULL column (built per call: a column needs an active Spark session)."""
    return F.lit(None).cast(spark_type)


def _wm_last_week(df: DataFrame, columns: list[str], floor: datetime.date) -> DataFrame:
    """Weekly WM rows (``yyyyMM0W``) to one value per ``(cif_id, month_end)``: the month's
    last week, from the month of ``floor`` on."""
    last_week = [
        F.max(
            F.struct(
                F.col("week_number").cast("string").alias("w"),
                F.col(c).cast("double").alias("v"),
            )
        )["v"].alias(c)
        for c in columns
    ]
    return (
        df.filter(wm_month() >= F.lit(floor))
        .groupBy(cif_column(), F.last_day(wm_month()).alias("month_end"))
        .agg(*last_week)
    )


def _asset_rows(series: DataFrame, column: str, product_type: str) -> DataFrame:
    """``COLUMNS`` rows of one asset type from a ``(cif_id, month_end, column)`` series; a
    balance of 0 or less is not a holding (WM may fill missing balances with 0)."""
    return series.filter(F.col(column) > 0).select(
        "cif_id",
        "month_end",
        F.lit(ASSET_IDS[product_type]).alias("product_account_id"),
        F.lit(product_type).alias("product_type"),
        F.col(column).alias("balance_aed"),
        _null("int").alias("is_current"),
        _null("double").alias("instalment_aed"),
    )


def _assets(
    wm_balances: DataFrame, wm_holdings: DataFrame, floor: datetime.date
) -> list[DataFrame]:
    """Deposit, investment and WM-AUM rows."""
    require_columns(
        wm_balances,
        ["cif_id", "week_number", "avg_itd_eod_balance", "avg_inv_eod_balance"],
        "wm_fea_casa_eod_avg_balance",
    )
    require_columns(
        wm_holdings,
        ["cif_id", "week_number", "etw_total_market_value_aed"],
        "wm_fea_wealth_holdings_by_cif",
    )
    balances = _wm_last_week(
        wm_balances, ["avg_itd_eod_balance", "avg_inv_eod_balance"], floor
    )
    holdings = _wm_last_week(wm_holdings, ["etw_total_market_value_aed"], floor)
    return [
        _asset_rows(balances, "avg_itd_eod_balance", "deposit"),
        _asset_rows(balances, "avg_inv_eod_balance", "investment"),
        _asset_rows(holdings, "etw_total_market_value_aed", "wm"),
    ]


def _cards(card_contracts: DataFrame, card_month_end: DataFrame) -> DataFrame:
    """``card`` rows: a live contract (not replaced by a newer one) with a billing row in
    the month; current = billing level at most ``CARD_CURRENT_MAX_LEVEL``; the instalment
    is the month's minimum due."""
    require_columns(
        card_contracts,
        ["cif_id", "contract_id", "parent_contract_id"],
        "prm_card_contracts",
    )
    require_columns(
        card_month_end,
        ["contract_id", "month_end", "level", "minimum_due"],
        "prm_card_month_end",
    )
    replaced = card_contracts.select(
        F.col("parent_contract_id").alias("contract_id")
    ).distinct()
    live = card_contracts.join(replaced, "contract_id", "left_anti")
    return card_month_end.join(
        live.select("cif_id", "contract_id"), "contract_id"
    ).select(
        "cif_id",
        "month_end",
        F.col("contract_id").cast("string").alias("product_account_id"),
        F.lit("card").alias("product_type"),
        _null("double").alias("balance_aed"),
        (F.col("level") <= CARD_CURRENT_MAX_LEVEL).cast("int").alias("is_current"),
        F.col("minimum_due").alias("instalment_aed"),
    )


def _loans(loan_month_end: DataFrame) -> DataFrame:
    """``loan`` rows: every retail loan snapshot; current = bucket 0, no overdue days and
    not written off; the instalment is the one due."""
    require_columns(
        loan_month_end,
        [
            "cif_id",
            "account_id",
            "month_end",
            "delinquency_bucket",
            "overdue_days",
            "instalment_due_aed",
            "write_off_date",
        ],
        "prm_loan_month_end",
    )
    current = (
        (F.col("delinquency_bucket") == 0)
        & (F.coalesce(F.col("overdue_days"), F.lit(0.0)) <= 0)
        & F.col("write_off_date").isNull()
    )
    return loan_month_end.select(
        "cif_id",
        "month_end",
        F.col("account_id").alias("product_account_id"),
        F.lit("loan").alias("product_type"),
        _null("double").alias("balance_aed"),
        current.cast("int").alias("is_current"),
        F.col("instalment_due_aed").alias("instalment_aed"),
    )


def build(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    card_contracts: DataFrame,
    card_month_end: DataFrame,
    loan_month_end: DataFrame,
    wm_balances: DataFrame,
    wm_holdings: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``COLUMNS`` from the first of the last ``history_months`` months up to the persona
    start month on, for all customers (the persona scope is applied by the A1 engine's
    join on the observation base). The primaries are already bounded to that window by
    ``product_primary`` (same parameter).

    Raises ``ValueError`` naming the source when a column is missing."""
    floor = months_back(persona_start_date, history_months - 1)
    parts = [
        *_assets(wm_balances, wm_holdings, floor),
        _loans(loan_month_end),
        _cards(card_contracts, card_month_end),
    ]
    return reduce(DataFrame.unionByName, parts).select(*COLUMNS)
`````

### FILE: `src/enbd_collections/nodes/primary/products/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/nodes/primary/products/prm_products.py`
action: add · new sha256 `e5aca8dd53f80a371a6eb2f2607d5a433a93efa963a6ff4d58543e0baa07fd63` · new trailing newline: yes

New:

`````python
"""Primary nodes: every customer's card contracts, card month ends and retail-loan month
ends (the raw Way4 and loan-portfolio reads behind the A1 cross-product feature).

* ``prm_card_contracts`` - one row per ``(cif_id, contract_id)``: every Way4 card contract
  of a client, with ``parent_contract_id`` (the contract a newer one replaced; NULL for
  none);
* ``prm_card_month_end`` - one row per ``(contract_id, month_end)`` with a billing row in
  the month: ``level`` (``BS_PMT_CYCLE_DUE`` of the month's latest billing row; 1 = not
  overdue) and ``minimum_due`` (of the latest balance snapshot in the month's last
  ``BALANCE_TAIL_DAYS`` days; NULL without one);
* ``prm_loan_month_end`` - one row per retail loan and monthly snapshot of
  ``bo_rr_portf_actv_acct_mthly``: bucket, overdue days, instalment due and write-off date.

All customers, from the first of the last ``history_months`` months up to the persona
start month on; values as in the source (which level or bucket is "current" is decided
by the consumers). The spine-scoped ``prm_contract`` / ``prm_balance`` hold only the
model's own accounts, so they cannot list a customer's other cards.
"""

from __future__ import annotations

import datetime

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F
from pyspark.sql.types import DateType

from enbd_collections.nodes.primary.cc_way4.prm_cc import derive_billing_amounts
from enbd_collections.nodes.utils.frames import months_back, require_columns

BALANCE_TAIL_DAYS = 5  # a card's minimum due is read from the last days of the month
LOAD_LAG_DAYS = 40  # edp_load_date bound before the first month (load lag)


def _window(persona_start_date: str, history_months: int) -> tuple:
    """The first month kept and the ``edp_load_date`` bound that covers it."""
    floor = months_back(persona_start_date, history_months - 1)
    return floor, floor - datetime.timedelta(days=LOAD_LAG_DAYS)


def _latest_in_month(df: DataFrame, key: str, day: str) -> DataFrame:
    """``df`` with ``month_end`` = the month end of ``day``, keeping each ``key``'s latest
    ``day`` row per month."""
    month_end = F.last_day(day)
    latest = Window.partitionBy(key, month_end).orderBy(F.col(day).desc())
    return (
        df.withColumn("month_end", month_end)
        .withColumn("_rn", F.row_number().over(latest))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )


def build_card_contracts(client: DataFrame, contract: DataFrame) -> DataFrame:
    """``cif_id``, ``contract_id``, ``parent_contract_id`` of every card contract whose
    client is known (``ident_number`` is the CIF)."""
    require_columns(client, ["client_idt", "ident_number"], "raw_stg_client")
    require_columns(
        contract,
        ["contract_idt", "client_idt", "parent_contract_idt"],
        "raw_stg_contract",
    )
    cif = client.select(
        "client_idt", F.trim(F.col("ident_number").cast("string")).alias("cif_id")
    ).distinct()
    return (
        contract.join(F.broadcast(cif), "client_idt")
        .select(
            "cif_id",
            F.col("contract_idt").cast("long").alias("contract_id"),
            F.col("parent_contract_idt").cast("long").alias("parent_contract_id"),
        )
        .distinct()
    )


def _card_levels(billing: DataFrame, lo: datetime.date) -> DataFrame:
    """Per ``(contract_id, month_end)``: the latest billing row's delinquency level."""
    require_columns(
        billing,
        ["contract_idt", "billing_date", "edp_load_date", "add_info"],
        "raw_stg_billing",
    )
    rows = billing.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo)).select(
        F.col("contract_idt").cast("long").alias("contract_id"),
        F.col("billing_date").cast(DateType()).alias("billing_date"),
        F.regexp_extract(F.col("add_info"), r"BS_PMT_CYCLE_DUE=(\d+)", 1)
        .cast("int")
        .alias("level"),
    )
    return _latest_in_month(rows, "contract_id", "billing_date").select(
        "contract_id", "month_end", "level"
    )


def _card_minimum_due(
    balance: DataFrame, account_group: DataFrame, lo: datetime.date
) -> DataFrame:
    """Per ``(contract_id, month_end)``: the minimum due of the latest balance snapshot in
    the month's last ``BALANCE_TAIL_DAYS`` days (``derive_billing_amounts``, the repo's
    own minimum-due derivation)."""
    require_columns(
        balance,
        [
            "contract_idt",
            "banking_date",
            "edp_load_date",
            "account_group_id",
            "balance",
        ],
        "raw_stg_balance",
    )
    banking = F.col("banking_date").cast(DateType())
    tail = (
        balance.filter(F.col("edp_load_date").cast(DateType()) >= F.lit(lo))
        .withColumn("contract_idt", F.col("contract_idt").cast("long"))
        .withColumn("banking_date", banking)
        .filter(
            F.col("banking_date")
            >= F.date_sub(F.last_day("banking_date"), BALANCE_TAIL_DAYS)
        )
    )
    amounts = derive_billing_amounts(tail, account_group)
    return _latest_in_month(amounts, "contract_idt", "banking_date").select(
        F.col("contract_idt").alias("contract_id"),
        "month_end",
        F.col("minimum_due").cast("double").alias("minimum_due"),
    )


def build_card_month_end(
    billing: DataFrame,
    balance: DataFrame,
    account_group: DataFrame,
    persona_start_date: str,
    history_months: int,
) -> DataFrame:
    """``contract_id``, ``month_end``, ``level``, ``minimum_due`` for every card contract
    with a billing row in the month."""
    floor, lo = _window(persona_start_date, history_months)
    return (
        _card_levels(billing, lo)
        .filter(F.col("month_end") >= F.lit(floor))
        .join(
            _card_minimum_due(balance, account_group, lo),
            ["contract_id", "month_end"],
            "left",
        )
        .select("contract_id", "month_end", "level", "minimum_due")
    )


def build_loan_month_end(
    loan_portfolio: DataFrame, persona_start_date: str, history_months: int
) -> DataFrame:
    """``cif_id``, ``account_id``, ``month_end``, ``delinquency_bucket``, ``overdue_days``,
    ``instalment_due_aed`` and ``write_off_date`` of every monthly loan snapshot."""
    require_columns(
        loan_portfolio,
        [
            "cust_num",
            "acct_num",
            "ss_dt",
            "ra_delq_bkt",
            "ra_ovd_days",
            "ra_instl_due_amt",
            "ra_woff_dt",
        ],
        "bo_rr_portf_actv_acct_mthly",
    )
    floor, _ = _window(persona_start_date, history_months)
    return loan_portfolio.filter(F.to_date("ss_dt") >= F.lit(floor)).select(
        F.col("cust_num").cast("string").alias("cif_id"),
        F.trim(F.col("acct_num").cast("string")).alias("account_id"),
        F.last_day(F.to_date("ss_dt")).alias("month_end"),
        F.col("ra_delq_bkt").cast("int").alias("delinquency_bucket"),
        F.col("ra_ovd_days").cast("double").alias("overdue_days"),
        F.col("ra_instl_due_amt").cast("double").alias("instalment_due_aed"),
        F.col("ra_woff_dt").alias(
            "write_off_date"
        ),  # as loaded: NULL = not written off
    )
`````

### FILE: `src/enbd_collections/nodes/utils/frames.py`
action: add · new sha256 `e0391589906491e07ea5095b6d033ab084c232c98ec9ccde15ea02df81558195` · new trailing newline: yes

New:

`````python
"""Small helpers shared by the primary and feature nodes (CASA, products)."""

from __future__ import annotations

from datetime import date

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F


def months_back(day: str | date, months: int) -> date:
    """First day of the month ``months`` calendar months before ``day``'s month."""
    day = date.fromisoformat(str(day))
    year, month = divmod(day.year * 12 + day.month - 1 - months, 12)
    return date(year, month + 1, 1)


def require_columns(df: DataFrame, columns: list[str], source: str) -> None:
    """Raise ``ValueError`` naming ``source`` when ``df`` lacks any of ``columns``."""
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def wm_month(week_number: str = "week_number") -> Column:
    """First day of the month of a WM ``yyyyMM0W`` week."""
    return F.to_date(F.substring(F.col(week_number).cast("string"), 1, 6), "yyyyMM")


def cif_column() -> Column:
    """``cif_id`` as a string (the persona join type)."""
    return F.col("cif_id").cast("string").alias("cif_id")
`````

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `55891314e2b8b0aee8d166672caafcad6b7ad923b3cb733cb73cc4ee2913fd63` · base trailing newline: yes · new sha256 `216399a176be0058bcd28857c620fcf3b96c58f1b05e2292fb6138027ec36771` · new trailing newline: yes

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
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
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
from enbd_collections.pipelines import genesys


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
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
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
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (A3 bundle 23): the A3 check; removed by the bundle's cleanup.
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
        # TEMPORARY (A3 bundle 23): the A3 check; removed by the bundle's cleanup.
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
from enbd_collections.pipelines.casa import windows as casa_win
from enbd_collections.pipelines.casa import windows_all_models as casa_win_all
from enbd_collections.pipelines.casa import windows_casa as casa_win_casa
from enbd_collections.pipelines.casa import windows_casa_all_models as casa_win_casa_all
from enbd_collections.pipelines.products import features as products_feat
from enbd_collections.pipelines.products import primary as products_prm

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
from enbd_collections.pipelines.crx_persona.a1_ability import (  # TEMPORARY (bundle 24)
    check as crx_a1_b24_check,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a2_locatability as crx_rl_a2_locatability,
)
from enbd_collections.pipelines.crx_persona import (
    rl_a3_payment_credibility as crx_rl_a3_payment_credibility,
)
from enbd_collections.pipelines import digital_login as dl
from enbd_collections.pipelines.location import pipeline as location_features
from enbd_collections.pipelines import genesys


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
        "casa_windows": casa_win.create_pipeline(),
        "casa_windows_all_models": casa_win_all.create_pipeline(),
        "casa_windows_casa": casa_win_casa.create_pipeline(),
        "casa_windows_casa_all_models": casa_win_casa_all.create_pipeline(),
        "product_primary": products_prm.create_pipeline(),
        "product_features": products_feat.create_pipeline(),
        "product_features_b24_check": products_feat.create_b24_check_pipeline(),
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
        # TEMPORARY (A1 bundle 24): the A1 bureau check; removed by the bundle's cleanup.
        "crx_cc_a1_b24_check": crx_a1_b24_check.create_b24_check_pipeline("cc"),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": (
            crx_cc_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (A3 bundle 23): the A3 check; removed by the bundle's cleanup.
        "crx_cc_a3_check": crx_cc_a3_payment_credibility.create_check_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        # TEMPORARY (A1 bundle 24): the A1 bureau check; removed by the bundle's cleanup.
        "crx_rl_a1_b24_check": crx_a1_b24_check.create_b24_check_pipeline("rl"),
        "crx_rl_a2_locatability": crx_rl_a2_locatability.create_pipeline(),
        "crx_rl_a3_payment_credibility": (
            crx_rl_a3_payment_credibility.create_pipeline()
        ),
        # TEMPORARY (A3 bundle 23): the A3 check; removed by the bundle's cleanup.
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

### FILE: `src/enbd_collections/pipelines/bureau/salary_bounces.py`
action: replace · base sha256 `b9b0861bc022ae5d20c64dfae12f5d33db6cdc2e1df98693f7238452b672272a` · base trailing newline: yes · new sha256 `816fa665a06d0d1a8caa1fb88995cb3f1ad41ea53baf4655e743a2d0acc459b0` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Bureau salary and bounce inputs of the persona axes (per model_id).

    prm_bureau_alert_enriched ─┬─► feat_cif_bureau_salary_monthly
                               └─► feat_cif_bureau_bounces_monthly

Needs ``bureau_staging`` and ``bureau_primary`` (the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_salary_monthly",
                name="build_feat_cif_bureau_salary_monthly",
                tags=["bureau", "features"],
            ),
            node(
                func=feat_cif_bureau_bounces_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_bounces_monthly",
                name="build_feat_cif_bureau_bounces_monthly",
                tags=["bureau", "features"],
            ),
        ]
    )
`````

New:

`````python
"""Bureau salary and bounce inputs of the persona axes (per model_id).

    feat_bureau_salary_unified ──► feat_cif_bureau_salary_monthly
    prm_bureau_alert_enriched ───► feat_cif_bureau_bounces_monthly

Needs the DE's ``feat_bureau_salary_unified`` (read-only here) and ``bureau_staging`` +
``bureau_primary`` (the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"unified": "feat_bureau_salary_unified"},
                outputs="feat_cif_bureau_salary_monthly",
                name="build_feat_cif_bureau_salary_monthly",
                tags=["bureau", "features"],
            ),
            node(
                func=feat_cif_bureau_bounces_monthly.build,
                inputs={"alerts": "prm_bureau_alert_enriched"},
                outputs="feat_cif_bureau_bounces_monthly",
                name="build_feat_cif_bureau_bounces_monthly",
                tags=["bureau", "features"],
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `3dc8b844907db4756e4ca6a31b0d4e3a8c8fd363f6beee0896f2bb2b11eba5e2` · base trailing newline: yes · new sha256 `a9e284be1769f8bbaa3eee6b08bc8e87323df1a29ea53369160bd50db46e79ec` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
  | `feat_cif_bureau_salary_monthly` | the DE's `feat_bureau_salary_unified` (`bureau_salary_bounces`) |
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
- **Bureau salary** — one monthly AECB salary per CIF from the DE's unified table (alert
  change events first, then application-time salary history, then the bulk pull's
  aggregates spread back over 12 months). A row counts in its month and the next, never
  before it and no further (S14); a 0 row ends the carry.

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
- **Bureau salary is mostly an event feed for now.** Most rows are alerts, which appear only
  when something changes, so no row means nothing is known, not that the salary stopped; the
  bulk pull covers about 1% of customers. GRR's feed of pulls every 2 months enters through
  the same table. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions`,
  the flows and the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/check.py`
action: add · new sha256 `00c8a464ec27f4232de23edaaa8dd3ab13c5a8f43ea39920a647c3bd169c48af` · new trailing newline: yes

New:

`````python
"""TEMPORARY (A1 bundle 24): A1 with bureau salary from the DE's unified table against the
persisted A1 output (bureau salary from the alert feed, RL plus the loan's bureau pull).

The check rebuilds ``feat_cif_bureau_salary_monthly`` from ``feat_bureau_salary_unified``
into ``feat_cif_bureau_salary_monthly_b24_new`` and the income signals and A1 state into
``crx_<p>_a1_income_b24_new`` / ``crx_<p>_a1_b24_new``; the other signals are the persisted
ones, and no real output is touched. It logs, for the latest month's observation CIFs:

- ``B24 BUREAU``: old and new bureau rows in the last 2W + 1 months (rows, zero rows, new
  rows by ``salary_source``), CIF-months only old / only new / in both with amounts more
  than 1% apart;
- ``B24 INCOME``: old x new bureau evidence in the window, income source and income level;
- ``B24 A1 OUTPUT``: old and new state mix;
- ``B24 A1 MOVES``: old x new state.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_a1_b24_check
"""

import logging

from kedro.pipeline import Pipeline, node
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.bureau import feat_cif_bureau_salary_monthly

from .._common import GRAIN, window_months
from .classify import build_a1_ability
from .pipeline import TAGS
from .signals import build_income_signals

logger = logging.getLogger(__name__)
NEW_BUREAU = "feat_cif_bureau_salary_monthly_b24_new"
EVIDENCE_AED = 1000  # a window month the A1 engine counts as salary evidence


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


def _bureau_lines(
    old: DataFrame, new: DataFrame, cifs: DataFrame, since: Column
) -> list[str]:
    """Old vs new bureau rows of ``cifs`` from ``since`` on."""

    def scoped(df: DataFrame, side: str) -> DataFrame:
        return (
            df.join(cifs, "cif_id")
            .filter(F.col("month_end") >= since)
            .select("cif_id", "month_end", F.col("bureau_salary").alias(side))
        )

    a, b = scoped(old, "old"), scoped(new, "new")
    both = a.join(b, ["cif_id", "month_end"], "full")
    apart = F.abs(F.col("old") - F.col("new")) > 0.01 * F.greatest(
        F.abs("old"), F.abs("new")
    )
    s = both.agg(
        F.count("old").alias("old"),
        F.count("new").alias("new"),
        F.sum((F.col("old") == 0).cast("int")).alias("old_zero"),
        F.sum((F.col("new") == 0).cast("int")).alias("new_zero"),
        F.sum((F.col("new").isNull()).cast("int")).alias("only_old"),
        F.sum((F.col("old").isNull()).cast("int")).alias("only_new"),
        F.sum(apart.cast("int")).alias("apart"),
    ).collect()[0]
    n_new = max(s["new"], 1)
    return [
        f"  CIF-months: old {s['old']} (zero {s['old_zero']}) | new {s['new']} "
        f"(zero {s['new_zero']})",
        f"  only old {s['only_old']} | only new {s['only_new']} | in both, > 1% apart "
        f"{s['apart']}",
        "  new by salary_source:",
    ] + _counts(
        new.join(cifs, "cif_id").filter(F.col("month_end") >= since),
        ["salary_source"],
        n_new,
    )


def compare(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    old_bureau: DataFrame,
    new_bureau: DataFrame,
    old_income: DataFrame,
    new_income: DataFrame,
    old: DataFrame,
    new: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """Logs the B24 BUREAU / INCOME / A1 OUTPUT / A1 MOVES blocks for ``model_id``."""
    head = [f"  model_id {model_id}, latest month {persona_end_date}"]
    w = window_months(model_id)
    old_l = _latest(old, persona_end_date)
    new_l = _latest(new, persona_end_date).cache()
    n = new_l.count()
    cifs = (
        _latest(obs_base, persona_end_date)
        .filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
    )
    since = F.trunc(F.add_months(F.lit(str(persona_end_date)), -2 * w), "month")
    _block("B24 BUREAU", head + _bureau_lines(old_bureau, new_bureau, cifs, since))

    def evidence(df: DataFrame, side: str) -> DataFrame:
        return _latest(df, persona_end_date).select(
            *GRAIN,
            (F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= EVIDENCE_AED)
            .cast("int")
            .alias(f"{side}_bureau_evidence"),
        )

    states = old_l.select(
        *GRAIN,
        F.col("a1_state").alias("old_state"),
        F.col("a1_income_source").alias("old_source"),
        F.col("a1_income_level").alias("old_income"),
    ).join(
        new_l.select(
            *GRAIN,
            F.col("a1_state").alias("new_state"),
            F.col("a1_income_source").alias("new_source"),
            F.col("a1_income_level").alias("new_income"),
        ),
        list(GRAIN),
        "full",
    )
    income = evidence(old_income, "old").join(
        evidence(new_income, "new"), list(GRAIN), "full"
    )
    _block(
        "B24 INCOME",
        head
        + ["  bureau evidence in W (>= AED 1,000), old | new:"]
        + _counts(income, ["old_bureau_evidence", "new_bureau_evidence"], n)
        + ["  income source, old | new:"]
        + _counts(states, ["old_source", "new_source"], n)
        + ["  income level, old | new:"]
        + _counts(states, ["old_income", "new_income"], n),
    )
    _block(
        "B24 A1 OUTPUT",
        head
        + [f"  rows: new {n}", "  new state:"]
        + _counts(states, ["new_state"], n)
        + ["  old state:"]
        + _counts(states, ["old_state"], n),
    )
    _block(
        "B24 A1 MOVES",
        head + ["  old | new"] + _counts(states, ["old_state", "new_state"], n),
    )
    new_l.unpersist()


def create_b24_check_pipeline(product: str) -> Pipeline:
    """The new bureau feature, income signals and A1 state into temporary datasets, then
    the comparison."""
    prefix = f"crx_{product}_a1"
    obs = f"crx_{product}_obs_base"
    return Pipeline(
        [
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={"unified": "feat_bureau_salary_unified"},
                outputs=NEW_BUREAU,
                name=f"build_{prefix}_b24_bureau",
                tags=TAGS,
            ),
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": NEW_BUREAU,
                    "model_id": "params:model_id",
                },
                outputs=f"{prefix}_income_b24_new",
                name=f"build_{prefix}_income_b24_new",
                tags=TAGS,
            ),
            node(
                func=build_a1_ability,
                inputs={
                    "obs_base": obs,
                    "income": f"{prefix}_income_b24_new",
                    "casa": f"{prefix}_casa_signals",
                    "cross_product": f"{prefix}_cross_product_signals",
                    "distress": f"{prefix}_distress_signals",
                    "eosb": f"{prefix}_eosb_signals",
                    "anchor": f"{prefix}_liquidity_anchor",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=f"{prefix}_b24_new",
                name=f"build_{prefix}_b24_new",
                tags=TAGS,
            ),
            node(
                func=compare,
                inputs={
                    "obs_base": obs,
                    "old_bureau": "feat_cif_bureau_salary_monthly",
                    "new_bureau": NEW_BUREAU,
                    "old_income": f"{prefix}_income_signals",
                    "new_income": f"{prefix}_income_b24_new",
                    "old": f"{prefix}_ability",
                    "new": f"{prefix}_b24_new",
                    "model_id": "params:model_id",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name=f"compare_{prefix}_b24",
                tags=TAGS,
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: replace · base sha256 `9ac0eed0ccee7dc3f9fac5a59385733ecc8ed9ed246ec9a3c7fb71a7136e8f8b` · base trailing newline: yes · new sha256 `2b068c6ce426211319022b7a88fe4273964e1d8b8e9b0e142279d69ff05bdb1e` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

`````python
"""The A1 ability pipeline for one product (``cc`` or ``rl``).

    crx_<p>_obs_base ─┬─ income signals ────┐   feat_cif_internal_salary_monthly,
                      │                     │   feat_cif_bureau_salary_monthly
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
    return Pipeline(
        [
            node(
                func=build_income_signals,
                inputs={
                    "obs_base": obs,
                    "internal_salary": "feat_cif_internal_salary_monthly",
                    "bureau_salary": "feat_cif_bureau_salary_monthly",
                    "model_id": "params:model_id",
                },
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
action: replace · base sha256 `13b4a878dfb01d9ae32caf9b01b7f021329b8abf287b47ea989ca6c017e14fbd` · base trailing newline: yes · new sha256 `990812ce5f0f7c5a2671b823bba73ea54de2e444eed3eac26ae3b0eb3f68e6d6` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
             salary, a bureau row counting in its own month and the next (S14);
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


def _with_next_month(bureau: DataFrame) -> DataFrame:
    """One bureau salary per ``(cif_id, month_end)``: each row's month, and the month
    after it unless that month has its own row (never before a row; pulls every 2 months
    make a continuous series). A row of 0 ends the carry.
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
) -> DataFrame:
    """``income_m1 … income_m{2W}`` (S3, S12, S14): salary received per month — the
    larger of the internal salary (``feat_cif_internal_salary_monthly``) and the bureau
    salary (``feat_cif_bureau_salary_monthly``, carried one month forward); NULL: no
    salary that month. Also the largest month per source: ``internal_salary_w`` /
    ``bureau_salary_w`` in the window, ``internal_salary_prior`` in the prior window.
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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `128e0ebcae44ca2e8218efe203d45e54c868957c1d74a28a0032857a3cc1b4e3` · base trailing newline: yes · new sha256 `0971a2ae70291a54efd81cc964cbb8c1eadb599b9c5c726a17f9165895090881` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``) and the loan's latest bureau pull adds a salary source.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

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
one EMI (``nodes.py``).

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``product_features``, ``bureau_salary_bounces`` and
``location_features``.

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

### FILE: `src/enbd_collections/pipelines/products/check.py`
action: add · new sha256 `255168df42a864b8323c5f887abd4d9d97c11259c4e2816361ba43d12e215674` · new trailing newline: yes

New:

`````python
"""TEMPORARY (bundle 24): the cross-product feature rebuilt from the product primaries
against the persisted ``feat_cif_cross_product_monthly`` (bundle 21, raw Way4 reads).

The check builds the new table into ``feat_cif_cross_product_monthly_b24_new`` (the real
output is untouched) and logs:

- ``B24 PRODUCTS``: rows per product type, old / new / only old / only new, and the rows
  in both whose balance, current flag or instalment differ;
- ``B24 A1 INPUTS``: customer-months whose A1 cross-product inputs (assets, largest
  current instalment, any current credit product, any asset holding) differ.

Expected: only the term-deposit holder rows without a balance disappear (``deposit``,
NULL balance), and no A1 input changes. Removed by the bundle's cleanup.

    kedro run --pipeline=product_features_b24_check
"""

import logging

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

logger = logging.getLogger(__name__)
_KEY = ["cif_id", "month_end", "product_account_id", "product_type"]
_VALUES = ["balance_aed", "is_current", "instalment_aed"]


def _block(name: str, lines: list[str]) -> None:
    body = "\n".join(lines)
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _differs(column: str) -> Column:
    old, new = F.col(f"old_{column}"), F.col(f"new_{column}")
    both = old.isNotNull() & new.isNotNull()
    return (old.isNull() != new.isNull()) | (both & (F.abs(old - new) > 1e-6))


def _side(df: DataFrame, side: str) -> DataFrame:
    return df.select(
        *[F.col(c).cast("string").alias(c) if c != "month_end" else c for c in _KEY],
        *[F.col(c).cast("double").alias(f"{side}_{c}") for c in _VALUES],
        F.lit(1).alias(f"_{side}"),
    )


def _a1_inputs(df: DataFrame) -> DataFrame:
    asset = F.col("product_type").isin("deposit", "investment", "wm")
    current = F.col("product_type").isin("card", "loan") & (
        F.coalesce(F.col("is_current").cast("int"), F.lit(0)) == 1
    )
    return df.groupBy(F.col("cif_id").cast("string").alias("cif_id"), "month_end").agg(
        F.sum(F.when(asset, F.col("balance_aed"))).alias("assets"),
        F.max(F.when(current, F.col("instalment_aed"))).alias("instalment"),
        F.max(current.cast("int")).alias("current"),
        F.max((asset & (F.col("balance_aed") > 0)).cast("int")).alias("holding"),
    )


def compare(old: DataFrame, new: DataFrame, persona_end_date: str) -> None:
    """Log the ``B24 PRODUCTS`` and ``B24 A1 INPUTS`` blocks."""
    joined = _side(old, "old").join(_side(new, "new"), _KEY, "full")
    in_both = F.col("_old").isNotNull() & F.col("_new").isNotNull()
    rows = (
        joined.groupBy("product_type")
        .agg(
            F.count("_old").alias("old"),
            F.count("_new").alias("new"),
            F.sum(F.col("_new").isNull().cast("int")).alias("only_old"),
            F.sum(F.col("_old").isNull().cast("int")).alias("only_new"),
            F.sum(
                (F.col("_new").isNull() & F.col("old_balance_aed").isNull()).cast("int")
            ).alias("only_old_null_balance"),
            *[
                F.sum((in_both & _differs(c)).cast("int")).alias(f"diff_{c}")
                for c in _VALUES
            ],
        )
        .orderBy("product_type")
        .collect()
    )
    _block(
        "B24 PRODUCTS",
        [
            f"  {r['product_type']}: old {r['old']} | new {r['new']} | only old "
            f"{r['only_old']} (null balance {r['only_old_null_balance']}) | only new "
            f"{r['only_new']} | differ balance {r['diff_balance_aed']} / current "
            f"{r['diff_is_current']} / instalment {r['diff_instalment_aed']}"
            for r in rows
        ],
    )
    inputs = ["assets", "instalment", "current", "holding"]
    a = _a1_inputs(old).select(
        "cif_id", "month_end", *[F.col(c).alias(f"old_{c}") for c in inputs]
    )
    b = _a1_inputs(new).select(
        "cif_id", "month_end", *[F.col(c).alias(f"new_{c}") for c in inputs]
    )
    latest = F.last_day(F.lit(str(persona_end_date)).cast("date"))
    diff = a.join(b, ["cif_id", "month_end"], "full").select(
        "month_end", *[_differs(c).alias(c) for c in inputs]
    )
    any_diff = F.greatest(*[F.col(c).cast("int") for c in inputs])
    stats = diff.agg(
        F.count(F.lit(1)).alias("months"),
        F.sum(any_diff).alias("any"),
        F.sum(F.when(F.col("month_end") == latest, 1)).alias("latest_months"),
        F.sum(F.when(F.col("month_end") == latest, any_diff)).alias("latest_any"),
        *[F.sum(F.col(c).cast("int")).alias(c) for c in inputs],
    ).collect()[0]
    _block(
        "B24 A1 INPUTS",
        [
            f"  customer-months: {stats['months']}, any input differs: {stats['any']}",
            f"  latest month ({persona_end_date}): {stats['latest_months']}, "
            f"differ: {stats['latest_any']}",
            "  by input: " + " | ".join(f"{c} {stats[c]}" for c in inputs),
        ],
    )
`````

### FILE: `src/enbd_collections/pipelines/products/features.py`
action: replace · base sha256 `b28c554dc3c12e472188d9a0601341d1ecf71f6a99e102d8634f40e16191ec53` · base trailing newline: yes · new sha256 `644e2f09e738a8431b7d681318877ee134cfa11585dbe6a5554bf6de50638517` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Product feature pipeline: the customer's other products with us per month.

feat_product_holding, bo_rr_portf_actv_acct_mthly,
wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif,
raw_stg_client / contract / billing / balance / account_group
                                    ─────────────→ feat_cif_cross_product_monthly

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
                    "wm_balances": "wm_fea_casa_eod_avg_balance",
                    "wm_holdings": "wm_fea_wealth_holdings_by_cif",
                    "card_client": "raw_stg_client",
                    "card_contract": "raw_stg_contract",
                    "card_billing": "raw_stg_billing",
                    "card_balance": "raw_stg_balance",
                    "card_account_group": "raw_stg_account_group",
                    "persona_start_date": "params:crx_persona.persona_start_date",
                    "history_months": "params:casa_features.history_months",
                },
                outputs="feat_cif_cross_product_monthly",
                name="build_feat_cif_cross_product_monthly",
                tags=["products", "features"],
            ),
        ]
    )
`````

New:

`````python
"""Product feature pipeline: the customer's other products with us per month.

    prm_card_contracts, prm_card_month_end, prm_loan_month_end,
    wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif ► feat_cif_cross_product_monthly

Needs ``product_primary`` for the model_id first.

    kedro run --pipeline=product_features
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.products import feat_cif_cross_product


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The monthly cross-product table (A1 F4)."""
    return Pipeline([_cross_product_node("feat_cif_cross_product_monthly")])


def _cross_product_node(output: str):
    return node(
        func=feat_cif_cross_product.build,
        inputs={
            "card_contracts": "prm_card_contracts",
            "card_month_end": "prm_card_month_end",
            "loan_month_end": "prm_loan_month_end",
            "wm_balances": "wm_fea_casa_eod_avg_balance",
            "wm_holdings": "wm_fea_wealth_holdings_by_cif",
            "persona_start_date": "params:crx_persona.persona_start_date",
            "history_months": "params:products.history_months",
        },
        outputs=output,
        name=f"build_{output}",
        tags=["products", "features"],
    )


def create_b24_check_pipeline() -> Pipeline:
    """TEMPORARY (bundle 24): the table rebuilt from the product primaries against the
    persisted one; removed by the bundle's cleanup."""
    from . import check  # pylint: disable=import-outside-toplevel

    return Pipeline(
        [
            _cross_product_node("feat_cif_cross_product_monthly_b24_new"),
            node(
                func=check.compare,
                inputs={
                    "old": "feat_cif_cross_product_monthly",
                    "new": "feat_cif_cross_product_monthly_b24_new",
                    "persona_end_date": "params:crx_persona.persona_end_date",
                },
                outputs=None,
                name="b24_check_compare",
                tags=["products", "b24_check"],
            ),
        ]
    )
`````

### FILE: `src/enbd_collections/pipelines/products/primary.py`
action: add · new sha256 `db8b7412573944529d605a381bedea2350b5d6e95aedb132810fa7152b544197` · new trailing newline: yes

New:

`````python
"""Product primary pipeline: every customer's card contracts, card month ends and loan
month ends (per model_id).

    raw_stg_client, raw_stg_contract ─────────────────────► prm_card_contracts
    raw_stg_billing, raw_stg_balance, raw_stg_account_group ► prm_card_month_end
    bo_rr_portf_actv_acct_mthly ──────────────────────────► prm_loan_month_end

    kedro run --pipeline=product_primary
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.primary.products import prm_products


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """The three product primaries read by ``product_features``."""
    tags = ["products", "primary"]
    window = {
        "persona_start_date": "params:crx_persona.persona_start_date",
        "history_months": "params:products.history_months",
    }
    return Pipeline(
        [
            node(
                func=prm_products.build_card_contracts,
                inputs={"client": "raw_stg_client", "contract": "raw_stg_contract"},
                outputs="prm_card_contracts",
                name="build_prm_card_contracts",
                tags=tags,
            ),
            node(
                func=prm_products.build_card_month_end,
                inputs={
                    "billing": "raw_stg_billing",
                    "balance": "raw_stg_balance",
                    "account_group": "raw_stg_account_group",
                    **window,
                },
                outputs="prm_card_month_end",
                name="build_prm_card_month_end",
                tags=tags,
            ),
            node(
                func=prm_products.build_loan_month_end,
                inputs={"loan_portfolio": "bo_rr_portf_actv_acct_mthly", **window},
                outputs="prm_loan_month_end",
                name="build_prm_loan_month_end",
                tags=tags,
            ),
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
Clean up after mirror bundle 24_a1_product_primaries_bureau_swap.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve these paths from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for every model_id the checks ran on (skip folders that do not exist):
  - `${_project.hdfs_path}/<model_id>/${globals:folders.feat}/products/cif_cross_product_monthly_b24_new` (cc_60_180);
  - `${_project.hdfs_path}/<model_id>/${globals:folders.feat}/bureau/cif_bureau_salary_monthly_b24_new` (all four);
  - `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/crx_<p>_a1_income_b24_new` and `…/crx/crx_<p>_a1_b24_new` (all four, `<p>` = cc / rl).
- **Remove the temporary checks** (everything marked TEMPORARY for bundle 24):
  - delete `conf/base/catalog/tmp_b24_check.yml`;
  - `src/enbd_collections/pipeline_registry.py`: the `product_features_b24_check`, `crx_cc_a1_b24_check` and `crx_rl_a1_b24_check` entries and the `crx_a1_b24_check` import;
  - `src/enbd_collections/pipelines/products/features.py`: `create_b24_check_pipeline`;
  - delete `src/enbd_collections/pipelines/products/check.py` and `src/enbd_collections/pipelines/crx_persona/a1_ability/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "b24" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
