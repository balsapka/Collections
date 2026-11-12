# Mirror bundle 24 — A1 products: raw reads moved to product primaries

apply_bundle version: 7 · built 2026-11-12 from `ca3f382..cdc0d31` · source: 7 added, 5 replaced, 0 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/24_a1_product_primaries.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '24_a1_product_primaries.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/24_a1_product_primaries.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** Ask Sonnet the following, in one go:

1. **Catalog and registry.** `catalog_products.yml` is new and `feat_cif_cross_product_monthly` now lives there only: confirm it is gone from `catalog_casa.yml` and defined exactly once in `conf/`. List every top-level key the apply removed from `catalog_casa.yml` and `pipeline_registry.py` compared with the last commit and put back any that is not `feat_cif_cross_product_monthly` (the `casa_windows*` entries and `genesys` must survive). `kedro registry list` shows `product_primary`, `product_features` and `product_features_b24_check`.
2. **`derive_billing_amounts`.** `nodes/primary/products/prm_products.py` calls `prm_cc.derive_billing_amounts(tail, account_group)` exactly as bundle 21's node did; confirm the signature and that it returns `contract_idt`, `banking_date` and `minimum_due`.
3. **Callers of the moved helpers.** `grep -rn "feat_cif_casa import\|_require\|_wm_month\|_cif()" src`: nothing outside `feat_cif_casa.py` may still import its old private helpers (they are now `nodes/utils/frames.py`); fix any workplace-only caller and report it.
4. **Parameters.** `products.history_months` resolves (`parameters_products.yml`); `crx_persona.persona_start_date` / `persona_end_date` exist.
5. **Tests.** Update the tests of `feat_cif_cross_product` for the new signature (primaries + WM; no `feat_product_holding`, no raw tables) and add tests for the three primaries; update any CASA test that imported `_require` / `_cif` / `_wm_month` / `months_back` from `feat_cif_casa`. Black, ruff and pylint clean on the touched files.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1 products: product_primary (card contracts, card month ends, loan month ends) replaces the raw reads in product_features; temporary check product_features_b24_check (bundle 24)" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/24_a1_product_primaries.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_refactor && git pull
```

Bundle 21's persisted `feat_cif_cross_product_monthly` is the baseline: do not re-run `product_features` before the check. The tables cover all customers, so the check needs one model_id: **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`).

**Step 7.** Build the primaries, then run the check (cc_60_180):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features_b24_check
```

Paste back both blocks, `=== B24 PRODUCTS START ===` … `END ===` and `=== B24 A1 INPUTS START ===` … `END ===`. Also note the run time of each pipeline.

**Step 8.** After the blocks are reviewed, write the real tables for **all four model_ids** (A1 does not need a re-run: its inputs do not change):

```bash
kedro run --env=dev --pipeline=product_primary
```

```bash
kedro run --env=dev --pipeline=product_features
```

Then the cleanup prompt.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The A1 cross-product feature (`product_features`, F4) no longer reads raw tables. The raw Way4 card tables and the loan portfolio are read once, by a new primary pipeline `product_primary`; the feature node reads those primaries and the two WM asset features only (DESIGN_REVIEW §7: primary nodes read raw, feature nodes read primary or a WM feature). A1's inputs do not change. Apply after bundle 21's cleanup (and bundle 23, which this branch was built on; no shared lines).

**New primaries** (`nodes/primary/products/prm_products.py`, all customers, the last `products.history_months` months up to the persona start month):
- `prm_card_contracts`: every Way4 card contract of a known client (`cif_id`, `contract_id`, `parent_contract_id`), from `raw_stg_client` + `raw_stg_contract`;
- `prm_card_month_end`: per `(contract_id, month_end)` with a billing row in the month: `level` (`BS_PMT_CYCLE_DUE` of the latest billing row) and `minimum_due` (latest balance snapshot in the month's last 5 days, via `derive_billing_amounts`), from `raw_stg_billing` / `raw_stg_balance` / `raw_stg_account_group`;
- `prm_loan_month_end`: every monthly loan snapshot of `bo_rr_portf_actv_acct_mthly`, renamed and typed (bucket, overdue days, instalment due, write-off date as loaded).
The workplace's `prm_contract` / `prm_balance` are spine-scoped (only the model's own accounts), which is why the node read raw: these new primaries hold every customer's cards.

**Feature node** (`feat_cif_cross_product.build`): inputs `prm_card_contracts`, `prm_card_month_end`, `prm_loan_month_end`, `wm_fea_casa_eod_avg_balance`, `wm_fea_wealth_holdings_by_cif`. Same `COLUMNS` and the same rules as bundle 21 (replaced cards out, current card = level ≤ 1, current loan = bucket 0 + no overdue days + not written off, assets > 0). "Current" stays in the feature layer; the primaries hold source values only.
- **One change:** the term-deposit holder rows without a balance (`deposit`, NULL balance, from `feat_product_holding`) are gone, and so is the `feat_product_holding` input. A1 never counted them (`xp_assets_aed` sums balances; `xp_holding` needs a balance above 0), so no A1 input moves.

**Tidy-ups:** the node no longer imports private helpers from `feat_cif_casa`: `months_back`, `require_columns`, `wm_month` and `cif_column` move to `nodes/utils/frames.py`, used by both (CASA logic unchanged). The pipeline has its own parameter `products.history_months` (12, as before via `casa_features.history_months`; new file `parameters_products.yml`). The `feat_cif_cross_product_monthly` catalog entry moves to the new `catalog_products.yml` (same path, so the existing table stays).

**Check** (temporary, `pipelines/products/check.py`, pipeline `product_features_b24_check`): builds the new table into `feat_cif_cross_product_monthly_b24_new` and compares it with the persisted bundle 21 table. Blocks `B24 PRODUCTS` (rows per type: old / new / only old / only new / values that differ) and `B24 A1 INPUTS` (customer-months whose A1 cross-product inputs differ). Expected: only `deposit` rows with a NULL balance are "only old"; everything else matches; A1 inputs differ in 0 customer-months. Tested locally on synthetic data against bundle 21's node: identical except that row kind.

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
| add | `conf/base/catalog/catalog_products.yml` |
| add | `conf/base/parameters/parameters_products.yml` |
| replace | `src/enbd_collections/nodes/features/casa/feat_cif_casa.py` |
| replace | `src/enbd_collections/nodes/features/products/feat_cif_cross_product.py` |
| add | `src/enbd_collections/nodes/primary/products/__init__.py` |
| add | `src/enbd_collections/nodes/primary/products/prm_products.py` |
| add | `src/enbd_collections/nodes/utils/frames.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/products/check.py` |
| replace | `src/enbd_collections/pipelines/products/features.py` |
| add | `src/enbd_collections/pipelines/products/primary.py` |

## Files

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
action: add · new sha256 `0fa12192bcbcfbb38adeefefad9bf11b7ae8ac657958ef95ff4d24cc25794ac8` · new trailing newline: yes

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

# TEMPORARY (bundle 24): the cross-product table rebuilt from the primaries, for the check;
# removed by the cleanup.
feat_cif_cross_product_monthly_b24_new:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/products/cif_cross_product_monthly_b24_new"
  save_args:
    mode: overwrite
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
action: replace · base sha256 `55891314e2b8b0aee8d166672caafcad6b7ad923b3cb733cb73cc4ee2913fd63` · base trailing newline: yes · new sha256 `f6417bd3a03734750ca4dbb2a72c6530e6250279d76ef9db28d317f353f337a1` · new trailing newline: yes

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
Clean up after mirror bundle 24_a1_product_primaries.md, on the bundle's branch.
- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.feat}/products/cif_cross_product_monthly_b24_new` from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for every model_id the check ran on (skip folders that do not exist).
- **Remove the temporary check** (everything marked TEMPORARY for bundle 24):
  - `conf/base/catalog/catalog_products.yml`: the `feat_cif_cross_product_monthly_b24_new` entry and its comment;
  - `src/enbd_collections/pipeline_registry.py`: the `product_features_b24_check` entry;
  - `src/enbd_collections/pipelines/products/features.py`: `create_b24_check_pipeline`;
  - delete `src/enbd_collections/pipelines/products/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "b24" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
