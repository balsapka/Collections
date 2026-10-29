# Mirror bundle 08 — A1 — finish: features-only engine, salary dating, S12, activity gate, report check

apply_bundle version: 6 · built 2026-10-29 from `3ac0310..ce0ec65` · source: 10 added, 16 replaced, 8 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 5). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/persona_redesign_b01 && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/08_a1_finish.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '08_a1_finish.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/08_a1_finish.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

**Step 4.** The two A1 test modules are yours to update (the bundle does not touch tests):
`src/tests/pipelines/crx_persona/schema_registry.py` and `test_crx_persona.py`. They
import the deleted CC v1 (`cc_a1_ability.nodes`, the `cc_a1_ability_empty` fixture) and the
`CRX_CC_A1_ABILITY` v1 schema. Point them at the new `crx_cc_a1_ability` /
`crx_rl_a1_ability` output (columns: `account_id`, `observation_date`, `a1_state`,
`a1_state_label`, `a1_provenance`, `a1_unknown_reason`, `a1_income_level`,
`a1_liquidity_level`, `a1_points_total`, `a1_distress_flag`, `liquidity_anchor_amt`,
`a1_eosb_flag`, `computed_at`), drop the v1 tests, and keep the rest passing. Then this must
print nothing (otherwise stop and send the output back):

```bash
grep -rnE "a1_ability_v2|build_internal_returns|cc_a1_ability\.enrichers|create_b05_check_pipeline" src --include='*.py' | grep -v "crx_persona/a1_ability/pipeline.py"
```

and `kedro registry list | grep -E "a1|casa|bureau_salary"` lists `casa_primary`,
`casa_features`, `bureau_salary_bounces`, `crx_cc_a1_ability`, `crx_rl_a1_ability` and the
two `*_a1_ability_b08_check` pipelines.

**Step 5.** Commit the source only, and push:

```bash
git add src conf && git commit -m "A1 finish (bundle 08): features-only engine, O64, S12, S11 gate, renames, temporary b08 check" && git push
```

**Undo** (before step 5) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/08_a1_finish.md --revert
```

### In PROD

**Step 6.** Get the branch:

```bash
git fetch origin && git checkout feature/persona_redesign_b01 && git pull
```

Run everything twice: first for **`cc_60_180`** (the default in `conf/dev/globals_dev.yml`),
then for **`rl_60_180`** (set `model_id: rl_60_180`, persona dates unchanged). Switch it
back to `cc_60_180` when you are done. Steps 6–8 per model_id.

**Step 6.** Build the new inputs. Only the two new CASA primaries (the existing ones are
unchanged; `prm_casa_transactions` scans 12+ months of the raw table, so expect a long run),
then the bureau and CASA features:

```bash
kedro run --env=dev --pipeline=casa_primary --nodes=build_prm_casa_transactions,build_prm_beneficiary_cards
```

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=casa_features
```

If `bureau_salary_bounces` stops on `stg_aecb_salary_history`, `prm_bureau_cif_bridge` or
`prm_bureau_alert_enriched` (PATH_NOT_FOUND / table not found), send the error back.

**Step 7.** Run the check pipeline (observation base, the new A1 into the temporary
`crx_<p>_a1_ability_b08_check`, then the report blocks). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b08_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b08_check
```

It reads the current output `crx_<p>_a1_ability_v2` and `prm_dcore_account_agreements`
(built by `location_features`). If it stops with PATH_NOT_FOUND on the agreements, run
`kedro run --env=dev --pipeline=location_features --nodes=build_prm_dcore_account_agreements`
and repeat step 7; on anything else, send the error back.

Paste back every block from `=== B08 … START ===` to `=== B08 … END ===`: `OUTPUT`,
`REPORT`, `SOURCES`, `CHANGES`. Aggregates only. Text is best; otherwise one photo per
block.

**Step 8.** Only after the B08 blocks have been reviewed: write the real output (it
replaces the old CC v1 / RL waterfall output at the same path).

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** The A1 ability finish (spec `A1_ability_spec.md` S1–S13): the
engine reads monthly feature tables only, the known input defects are fixed, the activity
gate counts only money the customer moved, the old CC v1 and the RL waterfall are removed,
and a temporary check logs every table of the A1 report to GRR.

- **New primaries** (pipeline `casa_primary`): `prm_casa_transactions` — every CASA leg of
  `comp_financial_tran_repos_dly`, all CIFs, 12 months before the persona start onwards,
  deduplicated on the transaction key, CIF 13339117 dropped; `prm_beneficiary_cards` — the
  card numbers registered as payment beneficiaries (`raw_beneficiary_cards`).
- **New pipeline `casa_features`**: `feat_cif_internal_salary_monthly` (WM salary, **dated
  correctly**: `week_number` is `yyyyMM0W`, not a date — the old engine put every salary one
  month early, O64), `feat_cif_casa_balance_monthly`, `feat_cif_casa_activity_monthly` (CASA
  legs per lane, after the FTR row-handling reference), `feat_cif_ext_card_payment_monthly`,
  `feat_cif_returns_monthly`.
- **New pipeline `bureau_salary_bounces`** (own file in `pipelines/bureau/`):
  `prm_bureau_salary_history` (typed `stg_aecb_salary_history`), `feat_cif_bureau_salary_monthly`
  (joined to `prm_bureau_cif_bridge` on the file, as today), `feat_cif_bureau_bounces_monthly`
  (pulls with a bounce, and **new** bounce events: a bounce repeated unchanged counts once).
  Catalog entries in a new `catalog_bureau.yml`.
- **Engine `crx_persona/a1_ability/`**: signals read the observation base + these features
  (+ `dcore_prm_followup_outcomes` / `prm_dcore_account_agreements` for the EOSB diagnostic);
  **S12** Stable income = the window's salary total ≥ 2 × the threshold (3 × at 180+) and
  ≥ 75% of the prior window; **S11** Unknown = 0 points, no distress and no
  customer-initiated CASA movement (own-loan recovery, own-account wash, fees, interest,
  reversals do not count), with `a1_unknown_reason` `no_casa` / `dormant_casa`; distress parts
  `distress_cheque` / `_dds` / `_bureau`; diagnostic `a1_eosb_flag`. `pipeline.py` builds the
  axis for either product.
- **Renames and deletions**: `cc_a1_ability_v2` → `cc_a1_ability`, `rl_a1_ability_v2` →
  `rl_a1_ability` (the old CC v1 and RL waterfall packages are replaced); outputs
  `crx_cc_a1_ability` / `crx_rl_a1_ability` (the old v1 / waterfall paths, overwritten);
  `crx_*_a1_internal_returns` and the v1 / waterfall catalog entries deleted. The
  `crx_*_a1_ability_v2` entries stay until the cleanup as the check's baseline. The
  departure-signature packages stay (`rl_a4_spine` imports one).
- **Check** (`a1_ability/b08_check.py`, pipelines `crx_cc_a1_ability_b08_check`,
  `crx_rl_a1_ability_b08_check`): blocks `B08 OUTPUT`, `REPORT`, `SOURCES`, `CHANGES` — the
  GRR report metrics M1–M12 and each state change attributed to salary dating, S12, the gate
  or bureau repeats. Removed by the cleanup prompt.
- Expected moves (A1 v03b): Low → Moderate / Moderate → High from the salary dating and S12
  (CC ~100 / ~30), Low → Unknown from the gate (CC 15–31% of Low, RL Low 89.5% → ~45–60%).

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
| add | `conf/base/catalog/catalog_bureau.yml` |
| replace | `conf/base/catalog/catalog_casa.yml` |
| replace | `conf/base/catalog/catalog_crx.yml` |
| replace | `conf/base/parameters/parameters_casa.yml` |
| add | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` |
| add | `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py` |
| add | `src/enbd_collections/nodes/features/casa/__init__.py` |
| add | `src/enbd_collections/nodes/features/casa/feat_cif_casa.py` |
| add | `src/enbd_collections/nodes/primary/bureau/prm_bureau_salary_history.py` |
| replace | `src/enbd_collections/nodes/primary/casa/prm_casa.py` |
| replace | `src/enbd_collections/pipeline_registry.py` |
| add | `src/enbd_collections/pipelines/bureau/salary_bounces.py` |
| add | `src/enbd_collections/pipelines/casa/features.py` |
| replace | `src/enbd_collections/pipelines/casa/primary.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/b08_check.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py` |
| add | `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/enrichers.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/pipeline.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/__init__.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/b05_check.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/nodes.py` |
| delete | `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/pipeline.py` |

## Files

### FILE: `conf/base/catalog/catalog_bureau.yml`
action: add · new sha256 `c75b9d33c518ca70c90848fa6c1410c872d4f5399130f2ab0be650304024fa7b` · new trailing newline: yes

New:

`````yaml
# Bureau salary and bounce datasets of the persona axes (pipeline bureau_salary_bounces).

# AECB salary history: one row per (bureau_file_id, reference_month, provider_no, edp_load_date).
prm_bureau_salary_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/bureau/salary_history"
  save_args:
    mode: overwrite
  metadata:
    kedro-viz:
      layer: primary

# Bureau-reported salary per (cif_id, month_end): the largest total, all history.
feat_cif_bureau_salary_monthly:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.feat}/bureau/cif_bureau_salary_monthly"
  save_args:
    mode: overwrite
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
action: replace · base sha256 `793f44194b792ee616b6e8c08a1b4d5569f9953797f35d419f24ac2de76b00a5` · base trailing newline: yes · new sha256 `4b8098d484478728340b2f95a871565b24b4f3c52faac4586ea050a285c8c525` · new trailing newline: yes

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

### FILE: `conf/base/catalog/catalog_crx.yml`
action: replace · base sha256 `ad9111e889da9fccfd8fcc4de6213de908b5a1b7e8aec566bb28cfd503dd22b0` · base trailing newline: yes · new sha256 `1daf312720ec9f8af1364b07e4c9a2b86c3ecb26a381799c79ffcc46047829da` · new trailing newline: yes

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

# TEMPORARY (mirror bundle 08): the previous output, the baseline of the b08 check.
# Remove the entry and its HDFS folder with the check.
crx_cc_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 08): the new output written by the b08 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_cc_a1_ability_b08_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b08_check"
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

# TEMPORARY (mirror bundle 08): the previous output, the baseline of the b08 check.
# Remove the entry and its HDFS folder with the check.
crx_rl_a1_ability_v2:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_v2"
  save_args:
    mode: overwrite

# TEMPORARY (mirror bundle 08): the new output written by the b08 check pipeline.
# Remove the entry, the pipeline and its HDFS folder after the check.
crx_rl_a1_ability_b08_check:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b08_check"
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

### FILE: `conf/base/parameters/parameters_casa.yml`
action: replace · base sha256 `0e8b22cb28ff17b35a7f96a12b230c45a0db0197a27fd6e9a8c50a084b3172bc` · base trailing newline: yes · new sha256 `e90c2f5c365503c1a4019de1d89b565b0ef8b1de2325139f55d54e95313852ec` · new trailing newline: yes

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
action: add · new sha256 `2c88f6bf68d9e5bac0539979a50c4a6c731cf0158298a9bea020366ed0e6a4eb` · new trailing newline: yes

New:

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

### FILE: `src/enbd_collections/nodes/features/bureau/feat_cif_bureau_salary_monthly.py`
action: add · new sha256 `1035bf2ef2fb9964c8cf75b25e130b4ef3a515b9d160affb0dad4e908963a680` · new trailing newline: yes

New:

`````python
"""Feature node: bureau-reported salary per customer and month.

One row per ``(cif_id, month_end)`` with a reported salary: ``bureau_salary`` is the
largest monthly total any provider reported for the month, over every pull of every
bureau file linked to the customer. All history the source holds is kept.
"""

from __future__ import annotations

from pyspark.sql import DataFrame
from pyspark.sql import functions as F


def _require(df: DataFrame, columns: list[str], source: str) -> None:
    missing = sorted(set(columns) - set(df.columns))
    if missing:
        raise ValueError(f"{source} is missing columns: {missing}")


def build(salary_history: DataFrame, cif_bridge: DataFrame) -> DataFrame:
    """Join ``prm_bureau_salary_history`` to its customers through
    ``prm_bureau_cif_bridge`` on the bureau file (one CIF per file), then take the
    month's largest total."""
    _require(
        salary_history,
        ["bureau_file_id", "reference_month", "total_salary_amount"],
        "prm_bureau_salary_history",
    )
    _require(cif_bridge, ["bureau_file_id", "cif_id"], "prm_bureau_cif_bridge")
    files = (
        cif_bridge.filter(F.col("cif_id").isNotNull())
        .select(
            F.col("bureau_file_id").cast("string").alias("bureau_file_id"),
            F.col("cif_id").cast("string").alias("cif_id"),
        )
        .distinct()
    )
    return (
        salary_history.filter(F.col("total_salary_amount") > 0)
        .join(files, on="bureau_file_id")
        .groupBy("cif_id", F.last_day("reference_month").alias("month_end"))
        .agg(F.max("total_salary_amount").alias("bureau_salary"))
    )
`````

### FILE: `src/enbd_collections/nodes/features/casa/__init__.py`
action: add · new sha256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` · new trailing newline: no

New:

`````python

`````

### FILE: `src/enbd_collections/nodes/features/casa/feat_cif_casa.py`
action: add · new sha256 `f4a04228b00593241e4116710b6b3401b9d728dfeb2dd2c7311b11cc6350422c` · new trailing newline: yes

New:

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

### FILE: `src/enbd_collections/nodes/primary/bureau/prm_bureau_salary_history.py`
action: add · new sha256 `ce680a3233b534a89cd05b815b6500ad50a16fe0310ad94a5f2696f1fc07d370` · new trailing newline: yes

New:

`````python
"""Primary dataset: AECB salary history (``prm_bureau_salary_history``).

One row per bureau file, salary month, reporting provider and load: the monthly salary
total each provider reported to the bureau. It carries no ``cif_id``; features join the
CIF bridge on ``bureau_file_id``.
"""

from __future__ import annotations

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

_RENAMES = {
    "subj_salcr_hist_hdr_file_id": "bureau_file_id",
    "subj_salcr_hist_ref_mnth": "reference_month",
    "subj_salcrdt_prvdr_no": "provider_no",
    "EDP_LOAD_DATE": "edp_load_date",
    "subj_salcr_hist_tot_sal_amt": "total_salary_amount",
    "subj_salcr_hist_trnsfr_cnt": "transfer_count",
}
_GRAIN = ["bureau_file_id", "reference_month", "provider_no", "edp_load_date"]


def build(stg_salary_history: DataFrame) -> DataFrame:
    """``stg_aecb_salary_history`` typed and renamed: ``reference_month`` is the first day
    of the salary month (the source holds ``MMyyyy``, e.g. ``072023``), amounts are
    doubles. Exact duplicates of a grain row keep one (the largest amount)."""
    missing = sorted(set(_RENAMES) - set(stg_salary_history.columns))
    if missing:
        raise ValueError(f"stg_aecb_salary_history is missing columns: {missing}")
    df = stg_salary_history.select(
        F.col("subj_salcr_hist_hdr_file_id").cast("string").alias("bureau_file_id"),
        F.to_date(
            F.lpad(F.col("subj_salcr_hist_ref_mnth").cast("string"), 6, "0"), "MMyyyy"
        ).alias("reference_month"),
        F.col("subj_salcrdt_prvdr_no").cast("string").alias("provider_no"),
        F.col("EDP_LOAD_DATE").cast("date").alias("edp_load_date"),
        F.col("subj_salcr_hist_tot_sal_amt")
        .cast("double")
        .alias("total_salary_amount"),
        F.col("subj_salcr_hist_trnsfr_cnt").cast("double").alias("transfer_count"),
    ).filter(F.col("bureau_file_id").isNotNull() & F.col("reference_month").isNotNull())
    first = Window.partitionBy(*_GRAIN).orderBy(
        F.col("total_salary_amount").desc_nulls_last()
    )
    return (
        df.withColumn("_rn", F.row_number().over(first))
        .filter(F.col("_rn") == 1)
        .drop("_rn")
    )
`````

### FILE: `src/enbd_collections/nodes/primary/casa/prm_casa.py`
action: replace · base sha256 `b03c9c7d584c1e5b9b85b4ba6ffd4141f3882cbab4b935a2ece8e66655b198df` · base trailing newline: yes · new sha256 `d081806274ad3d1f39acd1efc9948aea37e5b7cef8453fba4f56b45270a3a81a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

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

### FILE: `src/enbd_collections/pipeline_registry.py`
action: replace · base sha256 `6bd897cc0ce4a022fe4136006122a686aa80fe1b7f03259e97a735ac4e55c8a8` · base trailing newline: yes · new sha256 `e25ae415212dd54d93412273e0875f5ee526a5e7935c06c7e63520530ebf350e` · new trailing newline: yes

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
        # TEMPORARY (mirror bundle 06): A2 check; removed by the bundle's cleanup.
        "crx_cc_a2_locatability_b06_check": (
            crx_cc_a2_locatability.create_b06_check_pipeline()
        ),
        "crx_cc_a1_ability": crx_cc_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 08): A1 check; removed by the bundle's cleanup.
        "crx_cc_a1_ability_b08_check": (
            crx_cc_a1_ability.create_b08_check_pipeline()
        ),
        "crx_cc_obs_base": crx_obs_base.create_cc_pipeline(),
        "crx_rl_obs_base": crx_obs_base.create_rl_pipeline(),
        "crx_cc_a3_payment_credibility": crx_cc_a3_payment_credibility.create_pipeline(),
        "crx_rl_full_history": crx_rl_full_history.create_pipeline(),
        "crx_rl_spell_table": crx_rl_spell_table.create_pipeline(),
        "crx_rl_a4_spine": crx_rl_a4_spine.create_pipeline(),
        "crx_rl_a4_deterioration": crx_rl_a4_deterioration.create_pipeline(),
        "crx_rl_a1_ability": crx_rl_a1_ability.create_pipeline(),
        # TEMPORARY (mirror bundle 08): A1 check; removed by the bundle's cleanup.
        "crx_rl_a1_ability_b08_check": (
            crx_rl_a1_ability.create_b08_check_pipeline()
        ),
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

### FILE: `src/enbd_collections/pipelines/bureau/salary_bounces.py`
action: add · new sha256 `787f2abe270975bebd3c0594e770a47ccb3167d123be6d75388424f6b9ff90c5` · new trailing newline: yes

New:

`````python
"""Bureau salary and bounce inputs of the persona axes (per model_id).

    stg_aecb_salary_history ─► prm_bureau_salary_history ─┐
                                 prm_bureau_cif_bridge ───┴─► feat_cif_bureau_salary_monthly
    prm_bureau_alert_enriched ──────────────────────────────► feat_cif_bureau_bounces_monthly

Needs ``bureau_staging`` and ``bureau_primary`` (the bridge and the alerts) first.

    kedro run --pipeline=bureau_salary_bounces
"""

from kedro.pipeline import Pipeline, node

from enbd_collections.nodes.features.bureau import (
    feat_cif_bureau_bounces_monthly,
    feat_cif_bureau_salary_monthly,
)
from enbd_collections.nodes.primary.bureau import prm_bureau_salary_history


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """prm_bureau_salary_history and the two monthly bureau features."""
    return Pipeline(
        [
            node(
                func=prm_bureau_salary_history.build,
                inputs={"stg_salary_history": "stg_aecb_salary_history"},
                outputs="prm_bureau_salary_history",
                name="build_prm_bureau_salary_history",
                tags=["bureau", "primary"],
            ),
            node(
                func=feat_cif_bureau_salary_monthly.build,
                inputs={
                    "salary_history": "prm_bureau_salary_history",
                    "cif_bridge": "prm_bureau_cif_bridge",
                },
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

### FILE: `src/enbd_collections/pipelines/casa/features.py`
action: add · new sha256 `15702e1f037847b6e37792d4b00d0c5641c8aecf612e42979700e304bdda8433` · new trailing newline: yes

New:

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

### FILE: `src/enbd_collections/pipelines/casa/primary.py`
action: replace · base sha256 `6ee21700115339cf0f966270e7d89422e24827b77bb189b44d66110553da8b5f` · base trailing newline: yes · new sha256 `30ce9bbd30eb13e99dd4ab70de4fd3b2ab2961aed2418bd61ab99cff27f33c39` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/README.md`
action: replace · base sha256 `d38a60ca022c59f837f5090fbb37c0ae9c53df9d59e691a21fef9e30fe68d35e` · base trailing newline: yes · new sha256 `548ccdd2aa914e0b7b3463ff6b30598cab56b47417393dcef41d0bd5606e4199` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

New:

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
  | `feat_cif_bureau_salary_monthly` | `prm_bureau_salary_history` + `prm_bureau_cif_bridge` (`bureau_salary_bounces`) |
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
- **Bureau salary** — the AECB salary history, the largest total any provider reported for
  the month, linked to the CIF through `prm_bureau_cif_bridge`. RL also reads
  `feature_retail_loans`: the salary of each loan's latest bureau pull, dated by the pull
  month.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`).

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
- **Bureau salary reaches few customers** because `prm_bureau_cif_bridge` links only the
  bureau files with a contract link (O65). The GRR bureau salary feed and the link fix enter
  through the same "larger of the two per month" rule.
- **Missing salary months count as 0** in the window total and the weakening check.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions` and
  the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/__init__.py`
action: replace · base sha256 `0b214911e28bfaa58483e97adf6166704e7c38e15fa4b4420f25a0c4f31edfa2` · base trailing newline: yes · new sha256 `0587cd7e9811420a06aaaa62d0c193ccbb782ca69a50c4946e370767b79dd843` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""A1 ability engine shared by the CC and RL ability pipelines."""

from .classify import build_a1_ability
from .signals import (
    build_distress_signals,
    build_income_signals,
    build_internal_returns,
    build_liquidity_signals,
)

__all__ = [
    "build_a1_ability",
    "build_distress_signals",
    "build_income_signals",
    "build_internal_returns",
    "build_liquidity_signals",
]
`````

New:

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

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/b08_check.py`
action: add · new sha256 `143b6b58badab0829aa19ecbfe6808730879d8c21faa176c86c0efc5eac65684` · new trailing newline: yes

New:

`````python
"""TEMPORARY (mirror bundle 08): the A1 report tables and the old-vs-new check, in PROD.

Log blocks, aggregates only, latest observation month unless named:

* ``compare_a1_outputs`` (``B08 OUTPUT``): states (M1) — latest month, old
  (``crx_<p>_a1_ability_v2``) × new, the 8-month range; RL by ``loan_type``.
* ``describe_a1_report`` (``B08 REPORT``): income source and level (M4), CASA
  relationship (M5), liquidity (M6), Unknown / Low / Moderate-High reasons (M7–M9),
  distress parts (M10), EOSB and the anchor (M11).
* ``describe_a1_sources`` (``B08 SOURCES``): how far back each source goes, internal
  salary history (M2), bureau coverage (M3), CASA legs by lane, WM vs FTR coverage.
* ``explain_a1_changes`` (``B08 CHANGES``): the state rebuilt under the old rules, then
  each change in turn (salary dating, S12, the activity gate, bureau repeats), with the
  moves at every step (M12); the first and last steps are checked against the outputs.

Removed by the bundle's cleanup.
"""

from __future__ import annotations

import logging
from itertools import pairwise

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from enbd_collections.nodes.features.casa.feat_cif_casa import (
    build_internal_salary,
    transaction_lane,
)

from .._common import GRAIN, lookback_floor, parse_yyyymmdd, window_months
from ..scoring_engine import points_from_level
from .classify import (
    _LADDER,
    D_INC,
    DEMIN,
    F_CASA,
    F_INC,
    F_PAY,
    K_CASA,
    K_INC,
    K_PAY,
    MIN_MONTHS,
    _count_at_least,
    _months,
    _not_weakening,
    _window,
    income_level,
)
from .signals import CUSTOMER_LANES, _loan_bureau_salary

LOG = logging.getLogger(__name__)
_STATES = ("high", "moderate", "low", "unknown")


def _log(name: str, model_id: str, lines: list[str]) -> None:
    block = [
        f"=== B08 {name} START === [{model_id}]",
        *lines,
        f"=== B08 {name} END ===",
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


def _rows_and_cifs(df: DataFrame) -> str:
    r = df.agg(
        F.count(F.lit(1)).alias("n"), F.countDistinct("cif_id").alias("c")
    ).first()
    return f"{r['n']} accounts, {r['c']} CIFs"


def _with_cif(df: DataFrame, obs_base: DataFrame) -> DataFrame:
    cifs = obs_base.select(*GRAIN, F.col("cif_id").cast("string").alias("cif_id"))
    return df.join(cifs, on=list(GRAIN), how="left")


# ── B08 OUTPUT (M1) ───────────────────────────────────────────────────────────


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


def compare_a1_outputs(
    old: DataFrame, new: DataFrame, products: DataFrame, model_id: str
) -> None:
    """New states in the latest month (and by product), old × new, the monthly range."""
    latest = _latest_month(new)
    month = latest.agg(F.max("observation_date")).first()[0]
    old_m = old.filter(F.col("observation_date") == F.lit(month)).select(
        F.col("account_id").cast("string").alias("account_id"),
        F.col("a1_state").alias("old_state"),
    )
    both = latest.join(old_m, on="account_id", how="full")
    monthly = (
        new.groupBy(F.trunc("observation_date", "month").alias("month"))
        .agg(
            F.count(F.lit(1)).alias("n"),
            *[F.sum((F.col("a1_state") == s).cast("int")).alias(s) for s in _STATES],
        )
        .orderBy("month")
        .collect()
    )
    lines = [
        (
            f"month {month}: new {latest.count()} rows, old {old_m.count()}, "
            f"new only {both.filter(F.col('old_state').isNull()).count()}, "
            f"old only {both.filter(F.col('a1_state').isNull()).count()}"
        ),
        "new a1_state:",
        *_table(latest, "a1_state"),
        "by product x a1_state:",
        *_table(_product(latest, products), "loan_type", "a1_state"),
        "old x new a1_state:",
        *_table(both.filter(F.col("a1_state").isNotNull()), "old_state", "a1_state"),
        "new a1_state share by month (n, high, moderate, low, unknown %):",
        *[
            f"  {r['month']} {r['n']:>8} "
            + " ".join(f"{100.0 * r[s] / max(r['n'], 1):6.2f}" for s in _STATES)
            for r in monthly
        ],
        "range over the months (min-max %):",
        *[
            f"  {s:<9} "
            + f"{min(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}-"
            + f"{max(100.0 * r[s] / max(r['n'], 1) for r in monthly):6.2f}"
            for s in _STATES
        ],
    ]
    _log("OUTPUT", model_id, lines)


# ── B08 REPORT (M4–M11) ──────────────────────────────────────────────────────


def _bucket(amount: Column, edges: list[tuple[float, str]], none: str) -> Column:
    expr = F.when(amount.isNull() | (amount <= 0), none)
    for edge, label in edges:
        expr = expr.when(amount < edge, label)
    return expr.otherwise(f">={edges[-1][0]:,.0f}")


def describe_a1_report(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    products: DataFrame,
    model_id: str,
) -> None:
    """The latest month's report tables, M4–M11."""
    w = window_months(model_id)
    df = (
        _with_cif(_latest_month(new), obs_base)
        .join(income, on=list(GRAIN), how="left")
        .join(liquidity, on=list(GRAIN), how="left")
        .join(distress, on=list(GRAIN), how="left")
    )
    df = _product(df, products)
    anchor = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    casa_w = F.greatest(
        *[F.coalesce(c, F.lit(0.0)) for c in _months("casa", _window(w)[0])]
    )
    has_int = F.coalesce(F.col("internal_salary_w"), F.lit(0.0)) >= DEMIN
    has_bur = F.coalesce(F.col("bureau_salary_w"), F.lit(0.0)) >= DEMIN
    parts = [
        ("distress_cheque", "cheque"),
        ("distress_dds", "dds"),
        ("distress_bureau", "bureau"),
    ]
    df = df.select(
        "*",
        F.when(has_int & has_bur, "both")
        .when(has_int, "internal_only")
        .when(has_bur, "bureau_only")
        .otherwise("neither")
        .alias("income_source_w"),
        F.when(F.col("casa_held") == 0, "no_casa")
        .when(F.col("casa_active") == 0, "dormant_casa")
        .otherwise("active_casa")
        .alias("casa_relationship"),
        _bucket(casa_w, [(1000.0, "<1000"), (3000.0, "1000-3000")], "none").alias(
            "casa_max_w"
        ),
        (casa_w >= F.greatest(F.lit(F_CASA), K_CASA * anchor)).alias(
            "casa_covers_floor"
        ),
        (F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0)) > 0).alias(
            "ext_card_payment"
        ),
        F.when(F.col("a1_state") != "low", None)
        .when(
            (F.col("a1_points_total") == 0) & (F.col("a1_distress_flag") == 0),
            "0pt_active_casa",
        )
        .when(F.col("a1_points_total") == 0, "0pt_distress")
        .when(F.col("a1_points_total") == 1, "1pt")
        .otherwise("2-3pt_distress")
        .alias("low_reason"),
        F.concat_ws(
            "+", *[F.when(F.col(c) == 1, F.lit(label)) for c, label in parts]
        ).alias("distress_parts"),
        F.col("liquidity_anchor_amt").isNotNull().alias("anchor_present"),
        (K_INC * anchor > F_INC).alias("anchor_raises_income"),
        (K_CASA * anchor > F_CASA).alias("anchor_raises_casa"),
        (K_PAY * anchor > F_PAY).alias("anchor_raises_payment"),
    )
    q = (
        df.filter(F.col("liquidity_anchor_amt").isNotNull())
        .agg(F.percentile_approx("liquidity_anchor_amt", [0.1, 0.5, 0.9]).alias("p"))
        .first()["p"]
    )
    mh = df.filter(F.col("a1_state").isin("high", "moderate"))
    lines = [
        f"base: {_rows_and_cifs(df)}",
        "M4 income source in W x income level:",
        *_table(df, "income_source_w", "a1_income_level"),
        "M5 CASA relationship x a1_state:",
        *_table(df, "casa_relationship", "a1_state"),
        "M6 max monthly CASA balance in W x covers max(3000, anchor):",
        *_table(df, "casa_max_w", "casa_covers_floor"),
        "M6 external card payment in W x liquidity level:",
        *_table(df, "ext_card_payment", "a1_liquidity_level"),
        "M6 liquidity level:",
        *_table(df, "a1_liquidity_level"),
        "M7 unknown reason:",
        *_table(df.filter(F.col("a1_state") == "unknown"), "a1_unknown_reason"),
        "M8 low reason:",
        *_table(df.filter(F.col("a1_state") == "low"), "low_reason"),
        "M9 moderate / high: state x income x liquidity x distress:",
        *_table(
            mh, "a1_state", "a1_income_level", "a1_liquidity_level", "a1_distress_flag"
        ),
        "M10 distress parts in W ('' = none):",
        *_table(df, "distress_parts"),
        "M10 distress parts x a1_state:",
        *_table(
            df.filter(F.col("a1_distress_flag") == 1), "distress_parts", "a1_state"
        ),
        "M11 EOSB result in W x a1_state:",
        *_table(df, "a1_eosb_flag", "a1_state"),
        "M11 EOSB in W x liquidity level:",
        *_table(df.filter(F.col("a1_eosb_flag") == 1), "a1_liquidity_level"),
        f"M11 anchor present / p10 p50 p90: {q}",
        *_table(df, "anchor_present"),
        "M11 anchor raises the income x CASA x card-payment floor:",
        *_table(
            df, "anchor_raises_income", "anchor_raises_casa", "anchor_raises_payment"
        ),
        "by product: loan_type x a1_state, x unknown reason, x low reason:",
        *_table(df, "loan_type", "a1_state"),
        *_table(
            df.filter(F.col("a1_state") == "unknown"), "loan_type", "a1_unknown_reason"
        ),
        *_table(df.filter(F.col("a1_state") == "low"), "loan_type", "low_reason"),
    ]
    _log("REPORT", model_id, lines)


# ── B08 SOURCES (M2, M3, lanes, coverage) ────────────────────────────────────


def _months_since(last: Column) -> Column:
    return F.months_between(
        F.trunc("observation_date", "month"), F.trunc(last, "month")
    ).cast("int")


def describe_a1_sources(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    new: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    casa_balance: DataFrame,
    casa_activity: DataFrame,
    transactions: DataFrame,
    alerts: DataFrame,
    cif_bridge: DataFrame,
    model_id: str,
) -> None:
    """Source depth, salary history (M2), bureau coverage (M3), legs by lane, WM vs FTR."""
    w = window_months(model_id)
    base = _with_cif(_latest_month(new).select(*GRAIN, "a1_state"), obs_base).filter(
        F.col("cif_id").isNotNull()
    )
    cifs = base.select("cif_id").distinct()

    def depth(df: DataFrame, col: str, name: str) -> str:
        all_ = df.agg(F.min(col), F.max(col)).first()
        ours = df.join(cifs, on="cif_id").agg(F.min(col)).first()[0]
        return f"  {name:<36} all CIFs {all_[0]} .. {all_[1]}, base CIFs from {ours}"

    def last_before(df: DataFrame, value: str) -> DataFrame:
        return (
            base.join(df.filter(F.col(value) >= DEMIN), on="cif_id")
            .filter(F.col("month_end") <= F.col("observation_date"))
            .groupBy(*GRAIN)
            .agg(F.max("month_end").alias("last"))
        )

    def history(last: DataFrame, label: str) -> DataFrame:
        since = _months_since(F.col("last")) + 1
        return base.join(last, on=list(GRAIN), how="left").withColumn(
            label,
            F.when(F.col("last").isNull(), "never")
            .when(since <= w, "in_W")
            .when(since <= 6, "last_m4-6")
            .when(since <= 12, "last_m7-12")
            .when(since <= 24, "last_m13-24")
            .otherwise("last_m25+"),
        )

    internal = history(last_before(internal_salary, "salary"), "internal_salary")
    bureau_last = last_before(bureau_salary, "bureau_salary")
    alert_cifs = (
        alerts.filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
        .withColumn("_alert", F.lit(1))
    )
    bridge_cifs = (
        cif_bridge.filter(F.col("cif_id").isNotNull())
        .select(F.col("cif_id").cast("string").alias("cif_id"))
        .distinct()
        .withColumn("_bridge", F.lit(1))
    )
    bureau = (
        history(bureau_last, "_hist")
        .join(alert_cifs, on="cif_id", how="left")
        .join(bridge_cifs, on="cif_id", how="left")
        .withColumn(
            "bureau",
            F.when(F.col("_alert").isNull() & F.col("_bridge").isNull(), "no_record")
            .when(F.col("_bridge").isNull(), "record_not_linked")
            .when(F.col("_hist") == "never", "linked_never_salary")
            .when(F.col("_hist") != "in_W", "salary_ever_none_in_W")
            .otherwise("salary_in_W"),
        )
    )
    obs_month = base.agg(F.max("observation_date")).first()[0]
    w_floor = lookback_floor(base, w)
    legs = (
        transactions.filter(
            (F.col("tran_date") >= F.lit(w_floor))
            & (F.col("tran_date") <= F.lit(obs_month))
        )
        .withColumn("cif_id", F.col("cif_id").cast("string"))
        .join(cifs, on="cif_id")
        .withColumn("lane", transaction_lane())
    )
    by_lane = (
        legs.groupBy("lane")
        .agg(F.count(F.lit(1)).alias("legs"), F.countDistinct("cif_id").alias("cifs"))
        .orderBy("lane")
        .collect()
    )
    odd = (
        legs.filter(F.col("lane").isin("unclassified", "ambiguous"))
        .groupBy("lane", "tran_type", "reason_for_excluding")
        .count()
        .orderBy(F.col("count").desc())
        .limit(25)
        .collect()
    )
    held_floor = lookback_floor(base, 12)
    wm12 = (
        casa_balance.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(
            F.max(F.coalesce(F.col("casa_balance"), F.lit(0.0)) > 0).alias(
                "wm_positive"
            )
        )
        .withColumn("wm_row", F.lit(True))
    )
    ftr12 = (
        casa_activity.filter(F.col("month_end") >= F.lit(held_floor))
        .groupBy("cif_id")
        .agg(F.max(F.col("lane").isin(*CUSTOMER_LANES)).alias("ftr_customer"))
        .withColumn("ftr_leg", F.lit(True))
    )
    coverage = (
        cifs.join(wm12, on="cif_id", how="left")
        .join(ftr12, on="cif_id", how="left")
        .fillna(False, subset=["wm_row", "wm_positive", "ftr_leg", "ftr_customer"])
    )
    lines = [
        f"base (latest month): {_rows_and_cifs(base)}",
        "source depth (month_end):",
        depth(internal_salary, "month_end", "feat_cif_internal_salary_monthly"),
        depth(bureau_salary, "month_end", "feat_cif_bureau_salary_monthly"),
        depth(casa_balance, "month_end", "feat_cif_casa_balance_monthly"),
        depth(casa_activity, "month_end", "feat_cif_casa_activity_monthly"),
        "M2 internal salary (>= 1000) history x a1_state:",
        *_table(internal, "internal_salary"),
        *_table(internal, "internal_salary", "a1_state"),
        "M3 bureau (record = an alert row; linked = CIF in the bridge):",
        *_table(bureau, "bureau"),
        f"CASA legs of base CIFs in W ({w_floor} .. {obs_month}) by lane (legs, CIFs):",
        *[f"  {r['lane']:<16} {r['legs']:>10} {r['cifs']:>8}" for r in by_lane],
        "top unclassified / ambiguous (lane, tran_type, reason):",
        *[
            f"  {r['lane']:<12} {r['tran_type']!s:<34} {r['reason_for_excluding']!s:<28}"
            f" {r['count']:>8}"
            for r in odd
        ],
        (
            "WM vs FTR, base CIFs, last 12 months: WM row x WM positive x FTR leg x"
            " FTR customer leg:"
        ),
        *_table(coverage, "wm_row", "wm_positive", "ftr_leg", "ftr_customer"),
    ]
    _log("SOURCES", model_id, lines)


# ── B08 CHANGES (M12) ─────────────────────────────────────────────────────────


def _old_internal_salary(wm_salary: DataFrame, since: str) -> DataFrame:
    """The bundle 03–05 dating: ``week_number`` parsed as a date (one month early)."""
    week = parse_yyyymmdd("week_number")
    credit = F.date_sub(week, F.col("ft_days_since_salary_transaction").cast("int"))
    return wm_salary.filter(week >= F.lit(since)).select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.last_day(credit).alias("month_end"),
        F.col("ft_last_salary_amount").cast("double").alias("amount"),
    )


def _spread(base: DataFrame, series: DataFrame, prefix: str, months: int) -> DataFrame:
    """``(cif_id, month_end, amount)`` → ``{prefix}_m1 … _m{months}`` (max per month)."""
    k = (
        F.months_between(
            F.trunc("observation_date", "month"), F.trunc("month_end", "month")
        ).cast("int")
        + 1
    )
    return (
        base.select(*GRAIN, "cif_id")
        .join(series, on="cif_id")
        .withColumn("_k", k)
        .filter(F.col("_k").between(1, months))
        .groupBy(*GRAIN)
        .agg(
            *[
                F.max(F.when(F.col("_k") == i, F.col("amount"))).alias(f"{prefix}_m{i}")
                for i in range(1, months + 1)
            ]
        )
    )


def _months_rule(prefix: str, anchor: Column, w: int) -> Column:
    """The bundle 03–05 income rule: a salary month ≥ the floor in 2 of 3 (3 of 6)."""
    last = _months(prefix, _window(w)[0])
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last, floor) >= MIN_MONTHS[w]) & _not_weakening(
        prefix, D_INC, True, w
    )
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def explain_a1_changes(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    obs_base: DataFrame,
    old: DataFrame,
    new: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    wm_salary: DataFrame,
    bureau_salary: DataFrame,
    casa_balance: DataFrame,
    bureau_bounces: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> None:
    """Latest month: the state under the old rules, then each change in turn."""
    w = window_months(model_id)
    base = _with_cif(_latest_month(new).select(*GRAIN), obs_base)
    since = lookback_floor(base, 2 * w)
    bureau = bureau_salary.select(
        "cif_id", "month_end", F.col("bureau_salary").alias("amount")
    )
    if loan_features is not None:
        bureau = bureau.unionByName(
            _loan_bureau_salary(obs_base, loan_features).withColumnRenamed(
                "bureau_salary", "amount"
            )
        )
    bureau = bureau.filter(F.col("month_end") >= F.lit(since))
    new_internal = (
        build_internal_salary(wm_salary)
        .filter(F.col("month_end") >= F.lit(since))
        .withColumnRenamed("salary", "amount")
    )
    old_series = _old_internal_salary(wm_salary, since).unionByName(bureau)
    new_series = new_internal.unionByName(bureau)
    w_start = F.add_months(F.trunc("observation_date", "month"), 1 - w)
    in_w = (F.col("month_end") >= w_start) & (
        F.col("month_end") <= F.col("observation_date")
    )
    flows = (
        base.join(casa_balance.filter(F.col("casa_flow") == 1), on="cif_id")
        .filter(in_w)
        .groupBy(*GRAIN)
        .agg(F.max(F.lit(1)).alias("old_gate"))
    )
    pulls = (
        base.join(bureau_bounces.filter(F.col("bounce_pulls") > 0), on="cif_id")
        .filter(in_w)
        .groupBy(*GRAIN)
        .agg(F.max(F.lit(1)).alias("old_bureau"))
    )
    keys = list(GRAIN)
    df = (
        base.join(_spread(base, old_series, "old", 2 * w), on=keys, how="left")
        .join(_spread(base, new_series, "income", 2 * w), on=keys, how="left")
        .join(
            income.select(
                *keys,
                *[
                    F.col(f"income_m{i}").alias(f"sig_m{i}")
                    for i in range(1, 2 * w + 1)
                ],
            ),
            on=keys,
            how="left",
        )
        .join(liquidity.select(*keys, "casa_active"), on=keys, how="left")
        .join(
            distress.select(
                *keys, "distress_cheque", "distress_dds", "distress_bureau"
            ),
            on=keys,
            how="left",
        )
        .join(anchor, on=keys, how="left")
        .join(flows, on=keys, how="left")
        .join(pulls, on=keys, how="left")
        .join(new.select(*keys, "a1_liquidity_level", "a1_state"), on=keys, how="left")
        .join(
            old.select(
                F.col("account_id").cast("string").alias("account_id"),
                "observation_date",
                F.col("a1_state").alias("old_state"),
            ),
            on=keys,
            how="left",
        )
        .fillna(
            0,
            subset=[
                "old_gate",
                "old_bureau",
                "casa_active",
                "distress_cheque",
                "distress_dds",
                "distress_bureau",
            ],
        )
    )
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))
    liq = points_from_level(F.col("a1_liquidity_level"), {"adequate": 2, "weak": 1})
    internal_distress = (F.col("distress_cheque") == 1) | (F.col("distress_dds") == 1)

    def state(level: Column, gate: str, bureau_col: str) -> Column:
        points = points_from_level(level, {"stable": 2, "weak": 1}) + liq
        distressed = internal_distress | (F.col(bureau_col) == 1)
        unknown = (points == 0) & ~distressed & (F.col(gate) == 0)
        return _LADDER.state(points, distressed, unknown)

    steps = [
        ("s0_old_rules", state(_months_rule("old", amt, w), "old_gate", "old_bureau")),
        (
            "s1_salary_dating",
            state(_months_rule("income", amt, w), "old_gate", "old_bureau"),
        ),
        ("s2_window_total", state(income_level(amt, w), "old_gate", "old_bureau")),
        ("s3_activity_gate", state(income_level(amt, w), "casa_active", "old_bureau")),
        (
            "s4_bureau_repeats",
            state(income_level(amt, w), "casa_active", "distress_bureau"),
        ),
    ]
    df = df.select("*", *[expr.alias(name) for name, expr in steps])
    same_income = F.lit(True)
    for i in range(1, 2 * w + 1):
        same_income = same_income & F.col(f"income_m{i}").eqNullSafe(F.col(f"sig_m{i}"))
    checks = df.agg(
        F.sum(
            (~F.col("s0_old_rules").eqNullSafe(F.col("old_state"))).cast("int")
        ).alias("s0"),
        F.sum(F.col("old_state").isNull().cast("int")).alias("no_old"),
        F.sum(
            (~F.col("s4_bureau_repeats").eqNullSafe(F.col("a1_state"))).cast("int")
        ).alias("s4"),
        F.sum((~same_income).cast("int")).alias("income"),
    ).first()
    lines = [
        (
            f"rows {df.count()}; s0 vs the old output: {checks['s0']} differ "
            f"({checks['no_old']} without an old row); s4 vs the new output: {checks['s4']} "
            f"differ; income series vs the signals: {checks['income']} differ"
        ),
        "rows per state at each step (high, moderate, low, unknown):",
        *[
            f"  {n:<20} " + " ".join(f"{r[s]:>8}" for s in _STATES)
            for n, r in (
                (
                    n,
                    df.agg(
                        *[F.sum((F.col(n) == s).cast("int")).alias(s) for s in _STATES]
                    ).first(),
                )
                for n, _ in steps
            )
        ],
    ]
    for (a, _), (b, _) in pairwise(steps):
        moved = df.filter(~F.col(a).eqNullSafe(F.col(b)))
        lines += [f"{a} -> {b}: {moved.count()} rows move", *_table(moved, a, b)]
    lines += [
        "old output -> new output:",
        *_table(
            df.filter(~F.col("old_state").eqNullSafe(F.col("a1_state"))),
            "old_state",
            "a1_state",
        ),
    ]
    _log("CHANGES", model_id, lines)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/classify.py`
action: replace · base sha256 `0a9f2836a904a1117151912a9fea0dc0b105d9f721b043f7cd62a424646e8d76` · base trailing newline: yes · new sha256 `a49b23cdfcebda8c0f54af79cbad679c58777a28a6ebcbed63a9909b1f35d805` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import StateLadder, points_from_level

MIN_MONTHS = {3: 2, 6: 3}  # months of the window (by its length) that must qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
D_INC = 0.25  # stable income may fall at most this share vs the prior window
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="high",
    moderate="moderate",
    low="low",
    unknown="unknown",
    high_from_points=4,
    moderate_from_points=2,
)
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


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, missing_is_zero: bool, w: int
) -> Column:
    """The window's average is not more than ``max_drop`` below the prior window's (true
    when there is no prior window to compare with)."""
    last, prior_months = _window(w)
    recent = _mean(_months(prefix, last), missing_is_zero)
    prior = _mean(_months(prefix, prior_months), missing_is_zero)
    return F.coalesce(F.when(prior > 0, recent >= prior * (1 - max_drop)), F.lit(True))


def income_level(anchor: Column, w: int) -> Column:
    """stable / weak / none over a ``w``-month window (README section 1)."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    stable = (_count_at_least(last, floor) >= MIN_MONTHS[w]) & _not_weakening(
        "income", D_INC, True, w
    )
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (README section 2)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last, casa_floor) >= MIN_MONTHS[w]) & _not_weakening(
        "casa", D_CASA, False, w
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    """
    df = left_join_all(obs_base, [income, liquidity, distress, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    df = (
        df.withColumn("a1_income_level", income_level(amt, w))
        .withColumn("a1_liquidity_level", liquidity_level(amt, w))
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
        & (F.coalesce(F.col("casa_active"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    out = df.select(
        *GRAIN,
        "a1_state",
        labels[F.col("a1_state")].alias("a1_state_label"),
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
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

New:

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
(CC 60–180: the oldest overdue bucket; RL: one instalment; NULL: flat floors only).
Values are the workbook's starting values (sheet Thresholds), not yet tuned on PROD.
"""

from __future__ import annotations

from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F

from .._common import GRAIN, left_join_all, log_latest_month, window_months
from ..scoring_engine import StateLadder, points_from_level

MIN_MONTHS = {3: 2, 6: 3}  # CASA: months of the window (by its length) that qualify
F_INC = 3000.0  # salary floor (internal and bureau), AED
K_INC = 2.0  # income must also cover this multiple of the anchor
# Stable income: the window's salary total covers this many monthly floors (S12) …
INC_FLOORS = {3: 2, 6: 3}
D_INC = 0.25  # … and is at most this share below the prior window's total
F_CASA = 3000.0
K_CASA = 1.0
D_CASA = 0.50
F_PAY = 500.0
K_PAY = 1.0
DEMIN = 1000.0  # smallest amount that counts as any evidence

_LADDER = StateLadder(
    high="high",
    moderate="moderate",
    low="low",
    unknown="unknown",
    high_from_points=4,
    moderate_from_points=2,
)
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


def _mean(cols: list[Column], missing_is_zero: bool) -> Column:
    """Mean over the months; a month without data counts as 0 (income) or is skipped
    (balances)."""
    total = sum(F.coalesce(c, F.lit(0.0)) for c in cols)
    if missing_is_zero:
        return total / len(cols)
    present = sum(c.isNotNull().cast("int") for c in cols)
    return F.when(present > 0, total / present)


def _not_weakening(
    prefix: str, max_drop: float, missing_is_zero: bool, w: int
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
    salaries in one month and none in the next."""
    last = _months("income", _window(w)[0])
    floor = F.greatest(F.lit(F_INC), K_INC * anchor)
    total = sum(F.coalesce(c, F.lit(0.0)) for c in last)
    stable = (total >= INC_FLOORS[w] * floor) & _not_weakening("income", D_INC, True, w)
    weak = _count_at_least(last, F.lit(DEMIN)) > 0
    return F.when(stable, "stable").when(weak, "weak").otherwise("none")


def liquidity_level(anchor: Column, w: int) -> Column:
    """adequate / weak / none over a ``w``-month window (spec S7, S8)."""
    last = _months("casa", _window(w)[0])
    payment = F.coalesce(F.col("ext_card_payment_max"), F.lit(0.0))
    casa_floor = F.greatest(F.lit(F_CASA), K_CASA * anchor)
    casa_ok = (_count_at_least(last, casa_floor) >= MIN_MONTHS[w]) & _not_weakening(
        "casa", D_CASA, False, w
    )
    adequate = casa_ok | (payment >= F.greatest(F.lit(F_PAY), K_PAY * anchor))
    weak = (_count_at_least(last, F.lit(DEMIN)) > 0) | (payment >= DEMIN)
    return F.when(adequate, "adequate").when(weak, "weak").otherwise("none")


def build_a1_ability(  # pylint: disable=too-many-arguments,too-many-positional-arguments
    obs_base: DataFrame,
    income: DataFrame,
    liquidity: DataFrame,
    distress: DataFrame,
    eosb: DataFrame,
    anchor: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> DataFrame:
    """One A1 state per observation-base row, over ``model_id``'s window; logs the state
    distribution of the month of ``persona_end_date`` (the latest observation month).

    ``anchor`` carries ``GRAIN + liquidity_anchor_amt`` (product-specific builder).
    ``a1_unknown_reason`` says why a row is unknown: ``no_casa`` (no CASA leg or
    positive balance with us in 12 months) or ``dormant_casa``. ``a1_eosb_flag`` (a DCORE
    end-of-service result in the window) is a diagnostic and changes nothing.
    """
    df = left_join_all(obs_base, [income, liquidity, distress, eosb, anchor])
    amt = F.coalesce(F.col("liquidity_anchor_amt"), F.lit(0.0))  # missing → flat floors
    w = window_months(model_id)
    df = (
        df.withColumn("a1_income_level", income_level(amt, w))
        .withColumn("a1_liquidity_level", liquidity_level(amt, w))
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
        & (F.coalesce(F.col("casa_active"), F.lit(0)) == 0)
    )
    df = df.withColumn(
        "a1_state",
        _LADDER.state(F.col("a1_points_total"), F.col("a1_distress_flag"), unknown),
    )
    unknown_reason = F.when(F.col("casa_held") == 1, "dormant_casa").otherwise(
        "no_casa"
    )
    labels = F.create_map(*[F.lit(x) for kv in DISPLAY_NAMES.items() for x in kv])
    out = df.select(
        *GRAIN,
        "a1_state",
        labels[F.col("a1_state")].alias("a1_state_label"),
        F.when(F.col("a1_state") == _LADDER.unknown, "no_signal")
        .otherwise("observed")
        .alias("a1_provenance"),
        F.when(F.col("a1_state") == _LADDER.unknown, unknown_reason).alias(
            "a1_unknown_reason"
        ),
        "a1_income_level",
        "a1_liquidity_level",
        F.col("a1_points_total").cast("int"),
        F.col("a1_distress_flag").cast("int"),
        F.col("liquidity_anchor_amt").cast("double"),
        F.col("eosb_flag").cast("int").alias("a1_eosb_flag"),
        F.current_date().alias("computed_at"),
    )
    log_latest_month(out, "a1_state", f"a1_ability [{model_id}]", persona_end_date)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/a1_ability/pipeline.py`
action: add · new sha256 `c1f283b6fa39657c6e23a423ab0f08a3c3aec178fcf7eb15e0443b1c73b7cbbe` · new trailing newline: yes

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

TEMPORARY (mirror bundle 08): ``create_b08_check_pipeline`` runs the observation base and
the same nodes, writes the axis to ``crx_<p>_a1_ability_b08_check`` and logs the report
tables (``b08_check.py``). Removed by the bundle's cleanup.
"""

from kedro.pipeline import Pipeline, node
from kedro.pipeline.node import Node

from ..obs_base import create_cc_pipeline as create_cc_obs_pipeline
from ..obs_base import create_rl_pipeline as create_rl_obs_pipeline
from .b08_check import (
    compare_a1_outputs,
    describe_a1_report,
    describe_a1_sources,
    explain_a1_changes,
)
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


def create_b08_check_pipeline(product: str, anchor: Node) -> Pipeline:
    """TEMPORARY: observation base + the A1 pipeline writing to
    crx_<p>_a1_ability_b08_check + the log-only report nodes.
    Remove with b08_check.py and the catalog entries."""
    obs = f"crx_{product}_obs_base"
    prefix = f"crx_{product}_a1"
    check = f"{prefix}_ability_b08_check"
    signals = {
        "income": f"{prefix}_income_signals",
        "liquidity": f"{prefix}_liquidity_signals",
        "distress": f"{prefix}_distress_signals",
    }
    products = "rl_spine" if product == "rl" else obs
    changes = {
        "obs_base": obs,
        "old": f"{prefix}_ability_v2",
        "new": check,
        **signals,
        "anchor": f"{prefix}_liquidity_anchor",
        "wm_salary": "wm_fea_salary_days_since_increment",
        "bureau_salary": "feat_cif_bureau_salary_monthly",
        "casa_balance": "feat_cif_casa_balance_monthly",
        "bureau_bounces": "feat_cif_bureau_bounces_monthly",
        "model_id": "params:model_id",
    }
    if product == "rl":
        changes["loan_features"] = "feature_retail_loans"
    tags = ["crx_persona"]
    checks = [
        node(
            func=compare_a1_outputs,
            inputs={
                "old": f"{prefix}_ability_v2",
                "new": check,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"compare_{prefix}_b08",
            tags=tags,
        ),
        node(
            func=describe_a1_report,
            inputs={
                "obs_base": obs,
                "new": check,
                **signals,
                "products": products,
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b08_report",
            tags=tags,
        ),
        node(
            func=describe_a1_sources,
            inputs={
                "obs_base": obs,
                "new": check,
                "internal_salary": "feat_cif_internal_salary_monthly",
                "bureau_salary": "feat_cif_bureau_salary_monthly",
                "casa_balance": "feat_cif_casa_balance_monthly",
                "casa_activity": "feat_cif_casa_activity_monthly",
                "transactions": "prm_casa_transactions",
                "alerts": "prm_bureau_alert_enriched",
                "cif_bridge": "prm_bureau_cif_bridge",
                "model_id": "params:model_id",
            },
            outputs=None,
            name=f"describe_{prefix}_b08_sources",
            tags=tags,
        ),
        node(
            func=explain_a1_changes,
            inputs=changes,
            outputs=None,
            name=f"explain_{prefix}_b08_changes",
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
action: replace · base sha256 `5c91d96c1e42153abf0906c98bc92a09419e0f7919820e0bb84610f8596b44be` · base trailing newline: yes · new sha256 `8ce652f008a733da17563a4f1e4c36f0a967f83c10f6643749c5208dcdd43a30` · new trailing newline: yes

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

New:

`````python
"""A1 ability evidence at (account_id, observation_date), shared by CC and RL.

Spec: ``workplace_mirror/specs/A1_ability_spec.md`` (GRR workbook A1_ability_20261022).

Observation dates are month ends. The window is W calendar months, the observation month
included (``_common.window_months``: 3 for 60–180, 6 for 180+): m1 = the observation
month … mW; "the prior window" is m(W+1)–m(2W). The builders read the observation base
and monthly ``(cif_id, month_end)`` feature tables, and return what the classifier
compares with its thresholds:

* income    — salary received in each month (internal credit or bureau salary,
              the larger);
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

    Pulls are rare (most accounts have one), so this rarely falls in the window. It is an
    extra bureau source until the bureau salary history covers RL customers.
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


def build_income_signals(
    obs_base: DataFrame,
    internal_salary: DataFrame,
    bureau_salary: DataFrame,
    model_id: str,
    loan_features: DataFrame | None = None,
) -> DataFrame:
    """``income_m1 … income_m{2W}``: salary received per month — the larger of the
    internal salary (``feat_cif_internal_salary_monthly``) and the bureau salary
    (``feat_cif_bureau_salary_monthly``); NULL: no salary that month. Also the window's
    largest month per source, ``internal_salary_w`` / ``bureau_salary_w``.

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
        bureau.select(
            "cif_id",
            "month_end",
            F.col("bureau_salary").alias("amount"),
            F.lit("bur").alias("src"),
        )
    ).filter(F.col("month_end") >= F.lit(since))
    monthly = sources.groupBy("cif_id", "month_end").agg(
        F.max("amount").alias("amount")
    )
    return left_join_all(
        obs_base,
        [
            _by_month(obs, monthly, "amount", "income", 2 * w),
            _in_window(
                obs,
                sources,
                w,
                F.max(F.when(F.col("src") == "int", F.col("amount"))).alias(
                    "internal_salary_w"
                ),
                F.max(F.when(F.col("src") == "bur", F.col("amount"))).alias(
                    "bureau_salary_w"
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/__init__.py`
action: replace · base sha256 `0ffa767eca851acdc6bedcc7edec2e9cb117a88f8ebe0972c7769eb27e12b88a` · base trailing newline: yes · new sha256 `c93c3845745e00b13ecc5f333e3f1e230cefa5ec2e5a4bb26e5234f5f7fef1a7` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T26 — A1 Ability axis v1 (4-state, multi-signal)."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""CC A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b08_check_pipeline, create_pipeline

__all__ = ["create_b08_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/nodes.py`
action: replace · base sha256 `39711b7f48809f5bde54e1c159c58971b367cd12ef47ea5e25cc04fdc907684f` · base trailing newline: yes · new sha256 `2c45eefef8f32b32cc09382327f477b255b33e508bad1508880d01b3a488061f` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
# pylint: disable=R0917,R0801
"""T26 — A1 Ability axis v1 (4-state, multi-signal).

# pylint: disable=too-many-locals, too-many-statements, too-many-branches

Nine-node modular pipeline:
    build_a1_base(cc_spine, crx_cc_spell_table, crx_cc_departure_signature)
        → crx_cc_a1_base                [Node 1]   Group A departure signals

    build_a1_cif_bridge(crx_cc_a1_base, prm_contract, prm_client)
        → crx_cc_a1_cif_enriched        [Node 2]   CIF-resolved rows only

    build_a1_group_b_income(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_income      [Node 3]   T0-anchored income signals (spell-grain)

    build_a1_group_b_bureau(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_bureau      [Node 4]   T0-anchored bureau + recurring (spell-grain)

    build_a1_group_c(crx_cc_a1_base, ...)
        → crx_cc_a1_group_c             [Node 5]   Payment/utilisation/balance (T0 anchor)
                                                   ← Nodes 3, 4, 5 run in parallel

    build_a1_group_b_income_recent(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_income_recent  [Node 3r]  obs-date-anchored income signals

    build_a1_group_b_bureau_recent(crx_cc_a1_cif_enriched, ...)
        → crx_cc_a1_group_b_bureau_recent  [Node 4r]  obs-date-anchored bureau + recurring

    build_a1_group_c_recent(crx_cc_a1_base, prm_balance)
        → crx_cc_a1_group_c_recent      [Node 5r]  obs-date-anchored balance
                                                   ← Nodes 3r, 4r, 5r run in parallel

    build_a1_classify(crx_cc_a1_base, ..., crx_cc_a1_group_c_recent)
        → crx_cc_a1_ability             [Node 6]   ← shipped persona axis
                                                   (a1_state obs-date anchored; no T0 backup)

Goal (personas.md §1): assign each (account_id, observation_date) one of:

    ability_high      — strong, consistent income evidence; not overextended;
                        no pre-existing deterioration.
    ability_moderate  — income weakening or overextended but still earning;
                        OR stopped-but-recoverable (sudden shock, good history);
                        OR stable non-salary recurring income.
    ability_limited   — income stopped/stale AND no savings buffer;
                        OR income present but trajectory already deteriorating;
                        OR EOSB without confirmed post-EOSB salary.
    ability_unknown   — no CASA / payroll / bureau signal from any source.

Signal sources:
  Group A — crx_cc_departure_signature (T06, zero new joins; R14 reuse):
    payroll_present_h2      Pass I — salary deposit observed in any H2 month
    payroll_stopped_flag    Pass I — salary was present H1 but absent/stopping H2
    casa_inflow_stop_gap_d  Pass B — days since last salary CASA credit
                                     (diagnostic output only; not used in classifier)
    eosb_like_flag          Pass B — lump-sum gratuity inflow (termination signal)
    prior_spell_cnt_24m     Pass C — chronic default pattern vs first-time
    aecb_new_enquiry_3m     Pass G — credit-seeking in H2 (distress signal)

  Group B — sibling-repo features (schema-guarded; NULL emitted if absent):
    feat_payroll_indicator    (retail.feature_space) → salary_months_h2
    feat_casa_eod_balance     (retail.feature_space) → casa_eod_bal_h2
      ⚠ date col: month_end_date (YYYY-MM-dd); balance col:
        ft_avg_eod_balance_in_last_0_2_months_avg — PIT join (latest < T0)
    wm_fea_salary_days_since_increment (WM) → salary_amt_last,
                                              salary_change_pct (D5 only, not in output)
    wm_fea_casa_weekly_repeated_inflow (WM) → recurring_inflow_amt_h2,
                                              recurring_inflow_cnt_h2
    stg_aecb_salary_history  (AECB) → bureau_salary_present_6m_flag,
                                      bureau_salary_amt_last (6m window)
      ⚠ requires prm_bureau_cif_bridge for subj_salcr_hist_hdr_file_id→cif_id
    prm_bureau_alert_enriched (AECB) → a1_new_salary_acct_flag (alert_type_flag),
                                        a1_offus_paying_flag (90d window)
      ⚠ _ALERT_OFFUS_PAYING uses "positivealerts" prefix — confirmed from T26a EDA
        2026-09-17. Covers all DPD bands and product types.

  Group C — upstream crx tables (account/spell grain, no CIF bridge):
    crx_cc_payment_trajectory   (T04b) → pay_ratio_slope, pay_ratio_mean_h1/h2
    crx_cc_utilisation_features (T05)  → util_t0, util_slope, spend_cliff_flag
    prm_balance
                                       → cc_total_outstanding (PIT at T0)
  ⚠ WM feature coverage on delinquent CC population is UNPROVEN until T26 CHK-6.

Guard thresholds (tagged [CONFIRM] = pending stakeholder sign-off; Leg B tuning):
    _TAU_SALARY_ACTIVE_D     = 60   salary PIT gap: active if < this (days)  [CONFIRM]
    _TAU_SALARY_RECENCY_D    = 90   salary PIT gap: present if < this        [CONFIRM]
    _TAU_INFLOW_GAP_D        = 90   CASA inflow stop gap: active if < this   [CONFIRM]
    _TAU_RECURRING           = 2    recurring inflow months H2 ≥ this        [CONFIRM]
    _TAU_SALARY_H2_MIN       = 2    H2 payroll months needed for active      [CONFIRM]
    _TAU_UTIL_PRESSURE       = 0.80 util_t0 ≥ this → pressure_high          [CONFIRM]
    _TAU_PAY_SLOPE_GRADUAL   = -0.02 pay_ratio_slope < this → trajectory_gradual [CONFIRM]
    _TAU_UTIL_SLOPE_GRADUAL  =  0.02 util_slope > this → rising utilization  [CONFIRM]
    _TAU_MONTHS_RUNWAY       =  1.0 buffer_adequate: months_runway ≥ this    [CONFIRM]
    _TAU_CASA_INFLOW_H2_MIN  =   4  H2 weeks with any CASA inflow for active  [CONFIRM]

Five dimensions, ordered CASE WHEN:

  D1 — Income flow (salary_days_since_t0 removed; casa_inflow_stop_gap_d restored):
    income_active:  (payroll ≥ 2 H2 months AND not stopped)
                    OR bureau_salary_present_6m_flag=1
                    OR casa_inflow_stop_gap_d ≤ _TAU_INFLOW_GAP_D (salary CASA recent)
                    OR casa_inflow_cnt_h2 ≥ _TAU_CASA_INFLOW_H2_MIN (all CASA types)
    income_present: payroll_present_h2=1 AND salary_months_h2=1
                    OR payroll_stopped=1 (was present but stopping)
                    OR recurring_inflow_cnt_h2 ≥ 1
    income_stopped: payroll_stopped=1 AND bureau_salary_present_6m_flag≠1
                    AND (payroll_present_h2=0 OR salary_months_h2=0)

  ⚠ NULL-safe design: salary_months_h2 and payroll_stopped_flag are coalesced to their
    threshold defaults when NULL so Group A payroll signal is sufficient when Group B
    (feat_payroll_indicator) is absent. income_active + trajectory_gradual + NOT
    pressure_high falls to ability_unknown (spec gap — flag for GRR Leg B).
  ⚠ Income denominator (months_runway, cc_outstanding_vs_income): composite coalesce —
    salary_amt_last → bureau_salary_amt_last → casa_inflow_amt_h2 / 3 months.

  D2 — Savings buffer:
    buffer_adequate:     months_runway ≥ 1.0
    buffer_not_adequate: months_runway NULL or < 1.0

  D3 — Financial pressure at T0 (uses util_t0 from T05):
    pressure_high:  util_t0 ≥ 0.80

  D4 — Pre-T0 trajectory (uses pay_ratio_slope from T04b, util_slope from T05):
    trajectory_gradual: pay_ratio_slope < -0.02
                        OR (util_slope > 0.02 AND pay_ratio_mean_h2 < pay_ratio_mean_h1)
    trajectory_sudden:  pay_ratio_slope ≥ -0.02 AND spend_cliff_flag=1

  D5 — Recovery likelihood:
    recovery_likely: (salary_change_pct ≥ 0
                      OR (eosb_like_flag=1 AND eosb_post_salary_flag=1))
                     AND prior_spell_cnt_24m = 0
    eosb_post_salary_flag: proxy — eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent=1

State rules (ordered CASE WHEN — falls through to ability_unknown):
  1. ability_high:     income_active AND NOT pressure_high AND NOT trajectory_gradual
  2. ability_moderate: (income_active AND pressure_high)
                       OR (income_present AND buffer_adequate)
                       OR (income_stopped AND trajectory_sudden AND recovery_likely)
                       OR recurring_inflow_cnt_h2 ≥ 2
  3. ability_limited:  (income_stopped AND buffer_not_adequate)
                       OR (income_present AND trajectory_gradual)
                       OR (pressure_high AND trajectory_gradual)
                       OR (eosb_like_flag=1 AND eosb_post_salary_flag≠1)
                         — EOSB without confirmed post-EOSB salary → limited
  4. ability_unknown:  everything else (no signal from any source)

  ⚠ All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.

H2 window: [T0 - 3 months, T0) — last 3 complete months before spell anchor.
PIT join (WM weekly): last record with week_number strictly before T0.
PIT join (CASA balance): latest month_end_date < T0.
H2 window (WM weekly): weeks with week_date in [T0 - 90 days, T0).
Bureau salary window: [T0 - 6 months, T0) — H1+H2.
Bureau alert window:  [T0 - 90 days, T0) — pre-T0 only (no leakage).

Design decisions:
  • 9-node pipeline: Nodes 3, 3r, 4, 4r, 5, 5r run in parallel after Node 2.
  • Node 2 (crx_cc_a1_cif_enriched) contains only CIF-resolved rows — the
    downstream Group B enrichers only see rows where cif_id is known.
  • Spine grain (account_id, observation_date): build_a1_base reworked to use
    cc_spine as grain anchor (same pattern as A2).  T0-anchored enrichers dedup
    to (account_id, spell_id) internally to prevent N×M overcounting.
  • Obs-date-anchored enrichers (_recent variants) use full spine grain — each
    observation_date gets its own income window anchored to scoring time.
  • CIF bridge uses the same _build_cif_bridge helper as A2 (R14).
  • Schema guards on all Group B joins: columns missing → NULL, no row loss.
  • account_id == contract_id in CC domain (confirmed by CIF bridge pattern).
  • Group C (T04b / T05 / prm_balance) joined at (account_id, spell_id) —
    no CIF bridge required.
"""

# pylint: disable=too-many-lines  # justified: 9-node pipeline with T0 + recent classifiers

import datetime
import logging

from pyspark.sql import DataFrame
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona._spine_utils import (
    _build_cif_bridge,
    join_spine_to_spell,
)
from . import enrichers

LOG = logging.getLogger(__name__)

# ── Guard thresholds — [CONFIRM] = pending stakeholder sign-off (Leg B) ──────
_TAU_SALARY_ACTIVE_D = 60  # salary PIT gap (days): active if < this    [CONFIRM]
_TAU_SALARY_RECENCY_D = 90  # salary PIT gap (days): present if < this  [CONFIRM]
_TAU_INFLOW_GAP_D = 90  # CASA inflow stop gap: active if < this       [CONFIRM]
_TAU_RECURRING = 2  # recurring inflow months H2 ≥ this              [CONFIRM]
_TAU_SALARY_H2_MIN = 2  # H2 payroll months needed for active          [CONFIRM]
_TAU_UTIL_PRESSURE = 0.80  # util_t0 ≥ this → pressure_high              [CONFIRM]
_TAU_PAY_SLOPE_GRADUAL = -0.02  # pay_ratio_slope < this → gradual          [CONFIRM]
_TAU_UTIL_SLOPE_GRADUAL = 0.02  # util_slope > this → rising util           [CONFIRM]
_TAU_MONTHS_RUNWAY = 1.0  # buffer_adequate: months_runway ≥ this      [CONFIRM]
_TAU_CASA_INFLOW_H2_MIN = 4  # H2 weeks with any CASA inflow for active   [CONFIRM]

# ── Departure-sig columns forwarded in Node 1 ─────────────────────────────────
_DEPART_COLS = [
    "payroll_present_h2",
    "payroll_stopped_flag",
    "casa_inflow_stop_gap_d",
    "eosb_like_flag",
    "prior_spell_cnt_24m",  # Pass C — chronic pattern vs first-time default
    "aecb_new_enquiry_3m",  # Pass G — credit-seeking in H2 (distress signal)
]


# ── Node 1: build_a1_base ─────────────────────────────────────────────────────


def build_a1_base(
    cc_spine: DataFrame,
    spell_table: DataFrame,
    departure_sig: DataFrame,
) -> DataFrame:
    """Attach spell window + Group A income signals to the spine grain.

    Uses cc_spine as the grain anchor — identical pattern to build_a2_base.
    Spine→spell window join keeps all spine rows; spell columns are NULL for
    spine points with no active spell at that observation_date.

    Group A columns forwarded (zero-cost T06 Pass I/B/C/G reuse — R14):
        payroll_present_h2      salary deposit observed in any H2 month
        payroll_stopped_flag    salary was present H1 but absent/stopping H2
        casa_inflow_stop_gap_d  days since last salary CASA credit (NULL=no CASA)
        eosb_like_flag          lump-sum gratuity inflow (employment termination)
        prior_spell_cnt_24m     count of prior spells in last 24m (0 = first-time)
        aecb_new_enquiry_3m     new bureau enquiries in H2 (credit-seeking signal)

    Schema guard: any column absent from departure_sig is emitted as NULL.

    Args:
        cc_spine:      cc_spine — (contract_id, observation_date) grain model spine.
        spell_table:   crx_cc_spell_table (T03b). Grain: (account_id, spell_id).
        departure_sig: crx_cc_departure_signature (T06).

    Returns:
        DataFrame at (account_id, observation_date) grain with spell_id, t0,
        and Group A departure signal columns.
    """
    dep_sig = departure_sig
    for col in _DEPART_COLS:
        if col not in dep_sig.columns:
            LOG.warning(
                "build_a1_base: column '%s' absent from departure_sig — emitting NULL",
                col,
            )
            dep_sig = dep_sig.withColumn(col, F.lit(None))

    dep_sel = dep_sig.select("account_id", "spell_id", *_DEPART_COLS)

    # Spine→spell window join (shared utility — equality join + date filters)
    spine_with_spell = join_spine_to_spell(cc_spine, spell_table)

    result = spine_with_spell.join(dep_sel, on=["account_id", "spell_id"], how="left")
    return result


# ── Node 2: build_a1_cif_bridge ───────────────────────────────────────────────


def build_a1_cif_bridge(
    base: DataFrame,
    contract: DataFrame,
    client: DataFrame,
) -> DataFrame:
    """Resolve CIF for every spell; emit only CIF-resolved rows.

    Builds a two-hop bridge (prm_contract → prm_client) and left-joins onto
    the spell base.  Rows without a resolved cif_id are filtered out here so
    that all downstream Group B enrichers operate only on the joinable subset.
    The full base (including unresolved rows) is still passed to Nodes 5 and 6
    directly via crx_cc_a1_base.

    Logs the CIF resolution rate for CHK-7 validation.

    Args:
        base:     crx_cc_a1_base. Grain: (account_id, spell_id).
        contract: prm_contract — contract_id → client_id.
        client:   prm_client  — client_id → cif_id.

    Returns:
        crx_cc_a1_cif_enriched — (account_id, spell_id, t0, cif_id).
        Only rows where CIF was resolved; NULLs excluded.
    """
    cif_bridge = _build_cif_bridge(contract, client)

    with_cif = base.join(
        cif_bridge,
        on=base["account_id"] == cif_bridge["contract_id"],
        how="left",
    ).drop("contract_id")

    LOG.info(
        "build_a1_cif_bridge: CIF bridge built — resolution rate logged in PROD validation"
    )

    return with_cif.filter(F.col("cif_id").isNotNull()).select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("observation_date").cast("date"),
        F.col("cif_id"),
    )


# ── Node 3: build_a1_group_b_income ───────────────────────────────────────────


def build_a1_group_b_income(  # pylint: disable=too-many-locals
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """WM / retail.feature_space income signals at CIF grain.

    Five enrichers, all schema-guarded:
      1. feat_payroll_indicator   (monthly, CIF-grain) → salary_months_h2
      2. feat_casa_eod_balance    (monthly, CIF-grain) → casa_eod_bal_h2 (PIT)
      3. wm_fea_salary_days_since_increment (weekly, CIF-grain) → salary_amt_last,
         salary_change_pct  [salary_days_since_t0 extracted but dropped — GRR Row 7]
      4. wm_fea_casa_cc_inflow_outflow (weekly, CIF-grain) → casa_inflow_amt_h2,
         casa_inflow_cnt_h2  — ALL CASA credit types, not salary-only
      5. wm_pri_labelled_transactions + raw_beneficiary_cards →
         ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2
         CASA outflows to registered external CC numbers (H2 window)

    Also computes months_runway = casa_eod_bal_h2 / composite_income_monthly
    (savings buffer in months of income). Income denominator waterfall (Node 3 v1):
        salary_amt_last → casa_inflow_amt_h2 / 3 months.
    Note: bureau_salary_amt_last fallback is added by build_a1_classify
    (_assemble_classify_inputs) where Node 4 data is available, overriding this value.

    grain_key controls the output grain:
        ("account_id", "spell_id")         — T0-anchored (default); dedups to spell grain
        ("account_id", "observation_date") — obs-date-anchored (no dedup)

    Args:
        cif_enriched:             crx_cc_a1_cif_enriched — spine-grain CIF-resolved rows.
        feat_payroll:             feat_payroll_indicator. Required column: payroll_flag.
        feat_casa_bal:            feat_casa_eod_balance. Required columns: month_end_date,
                                  ft_avg_eod_balance_in_last_0_2_months_avg.
        wm_salary:                wm_fea_salary_days_since_increment. Required columns:
                                  ft_last_salary_amount, ft_days_since_salary_transaction,
                                  ft_percent_monthly_salary_change.
        wm_casa_inflow:           wm_fea_casa_cc_inflow_outflow. Required column:
                                  ft_inflow_casa_amt_in_last_0_0_weeks_sum.
        wm_labelled_transactions: wm_pri_labelled_transactions. Required columns:
                                  cif_id, in_out_flow, product_category, tran_date,
                                  tran_amt, transaction_acid.
        beneficiary_cards:        raw_beneficiary_cards. Required columns:
                                  instrument_number, instrument_type.
        crx_persona:              Persona param dict with persona_start_date used to
                                  floor wm_pri_labelled_transactions (one week per partition).
        grain_key:                Output grain key columns. Default ("account_id", "spell_id").

    Returns:
        DataFrame at grain_key grain — (grain_key..., salary_months_h2,
            casa_eod_bal_h2, salary_amt_last, salary_change_pct, months_runway,
            casa_inflow_amt_h2, casa_inflow_cnt_h2, ext_cc_payment_amt_h2,
            ext_cc_payment_cnt_h2).
        salary_change_pct is included for D5 use in build_a1_classify; it is
        dropped from the final output.
    """
    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(crx_persona["persona_start_date"])
    )
    # Dedup to spell grain for T0-anchored variant to prevent NxM explosion
    # when spine-grain cif_enriched (N rows per spell) joins external features.
    if "spell_id" in grain_key:
        cif_enriched = cif_enriched.dropDuplicates(["account_id", "spell_id"])

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_enriched, feat_payroll, anchor_col, grain_key
    )
    casa_h2 = enrichers.enrich_casa_eod_bal_h2(
        cif_enriched, feat_casa_bal, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(
        cif_enriched, wm_salary, anchor_col, grain_key
    )
    casa_inflow_h2 = enrichers.enrich_casa_inflow_h2(
        cif_enriched, wm_casa_inflow, anchor_col, grain_key
    )
    obt_h2 = enrichers.enrich_ext_cc_payments_h2(
        cif_enriched, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )

    result = cif_enriched.select(*grain_key)

    if salary_h2 is not None:
        result = result.join(salary_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("salary_months_h2", F.lit(None).cast("int"))

    if casa_h2 is not None:
        result = result.join(casa_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn("casa_eod_bal_h2", F.lit(None).cast("double"))

    if sal_pit is not None:
        result = result.join(sal_pit, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "salary_amt_last", F.lit(None).cast("double")
        ).withColumn("salary_change_pct", F.lit(None).cast("double"))

    if casa_inflow_h2 is not None:
        result = result.join(casa_inflow_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "casa_inflow_amt_h2", F.lit(None).cast("double")
        ).withColumn("casa_inflow_cnt_h2", F.lit(None).cast("int"))

    if obt_h2 is not None:
        result = result.join(obt_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "ext_cc_payment_amt_h2", F.lit(None).cast("double")
        ).withColumn(
            "ext_cc_payment_cnt_h2", F.lit(None).cast("int")
        )  # schema guard

    # months_runway: savings buffer in months of income.
    # Denominator waterfall: WM salary → CASA inflow monthly average (H2 / 3m).
    _income_monthly = F.coalesce(
        F.col("salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway",
        F.when(
            F.col("casa_eod_bal_h2").isNotNull()
            & _income_monthly.isNotNull()
            & (_income_monthly > 0),
            F.col("casa_eod_bal_h2") / _income_monthly,
        ).otherwise(F.lit(None).cast("double")),
    )

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("salary_change_pct").cast(
            "double"
        ),  # D5 input; dropped from final output
        F.col("months_runway").cast("double"),
        F.col("casa_inflow_amt_h2").cast("double"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
    )


# ── Node 4: build_a1_group_b_bureau ───────────────────────────────────────────


def build_a1_group_b_bureau(  # pylint: disable=too-many-arguments
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """AECB bureau + WM recurring inflow signals at CIF grain.

    Four enrichers, all schema-guarded:
      1. wm_fea_casa_weekly_repeated_inflow → recurring_inflow_amt_h2,
         recurring_inflow_cnt_h2
      2. stg_aecb_salary_history + prm_bureau_cif_bridge → bureau_salary_present_6m_flag,
         bureau_salary_amt_last (6m window)
      3. prm_bureau_alert_enriched → a1_new_salary_acct_flag (add-only, exact),
         a1_offus_paying_flag (positivealerts* prefix, 90d pre-T0 window)
      4. fea_monthly_aecb_alerts → fea_salary_acct_flag (add-or-close, 3m rolling sum)

    a1_new_salary_acct_flag is the union of sources 3 and 4: fires if either
    source detects a salary account event.  This provides redundancy while the
    bureau pipeline correctness is being validated.  Source 3 is add-only and
    more precise; source 4 (feature_space) is add-or-close and serves as a
    corroborating fallback.

    Combination rule (NULL-safe OR):
        1 if either source returns 1
        0 if at least one source returned data and neither returned 1
        NULL only if both sources returned NULL (no CIF coverage at all)

    prm_bureau_cif_bridge is required to bridge stg_aecb_salary_history
    (subj_salcr_hist_hdr_file_id) to cif_id.

    grain_key controls the output grain:
        ("account_id", "spell_id")         — T0-anchored (default); dedups to spell grain
        ("account_id", "observation_date") — obs-date-anchored (no dedup)

    Args:
        cif_enriched:          crx_cc_a1_cif_enriched — spine-grain CIF-resolved rows.
        wm_recurring:          wm_fea_casa_weekly_repeated_inflow.
        stg_salary_hist:       stg_aecb_salary_history (AECB bureau salary history).
        prm_bureau_alert:      prm_bureau_alert_enriched (AECB bureau alerts).
        prm_bureau_cif_bridge: prm_bureau_cif_bridge — (bureau_file_id → cif_id).
        fea_aecb_alerts:       fea_monthly_aecb_alerts (retail.feature_space).
        grain_key:             Output grain key columns. Default ("account_id", "spell_id").

    Returns:
        DataFrame at grain_key grain — (grain_key..., recurring_inflow_amt_h2,
            recurring_inflow_cnt_h2, bureau_salary_present_6m_flag,
            a1_new_salary_acct_flag, a1_offus_paying_flag).
    """
    # Dedup to spell grain for T0-anchored variant to prevent NxM explosion
    if "spell_id" in grain_key:
        cif_enriched = cif_enriched.dropDuplicates(["account_id", "spell_id"])

    rec_h2 = enrichers.enrich_recurring_inflow_h2(
        cif_enriched, wm_recurring, anchor_col, grain_key
    )
    bur_sal = enrichers.enrich_bureau_salary(
        cif_enriched, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )
    bur_alerts = enrichers.enrich_bureau_alerts(
        cif_enriched, prm_bureau_alert, anchor_col, grain_key
    )
    fea_alerts = enrichers.enrich_fea_bureau_alerts(
        cif_enriched, fea_aecb_alerts, anchor_col, grain_key
    )

    result = cif_enriched.select(*grain_key)

    if rec_h2 is not None:
        result = result.join(rec_h2, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "recurring_inflow_amt_h2", F.lit(None).cast("double")
        ).withColumn("recurring_inflow_cnt_h2", F.lit(None).cast("int"))

    if bur_sal is not None:
        result = result.join(bur_sal, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "bureau_salary_present_6m_flag", F.lit(None).cast("int")
        ).withColumn("bureau_salary_amt_last", F.lit(None).cast("double"))

    # Join both alert sources; combine into a single a1_new_salary_acct_flag
    if bur_alerts is not None:
        result = result.join(bur_alerts, on=list(grain_key), how="left")
    else:
        result = result.withColumn(
            "a1_new_salary_acct_flag", F.lit(None).cast("int")
        ).withColumn("a1_offus_paying_flag", F.lit(None).cast("int"))

    if fea_alerts is not None:
        result = result.join(
            fea_alerts.withColumnRenamed(
                "fea_salary_acct_flag", "_fea_salary_acct_flag"
            ),
            on=list(grain_key),
            how="left",
        )
    else:
        result = result.withColumn("_fea_salary_acct_flag", F.lit(None).cast("int"))

    # NULL-safe OR: 1 if either fires; NULL only when both are NULL
    result = result.withColumn(
        "a1_new_salary_acct_flag",
        F.when(
            (F.coalesce(F.col("a1_new_salary_acct_flag"), F.lit(0)) == 1)
            | (F.coalesce(F.col("_fea_salary_acct_flag"), F.lit(0)) == 1),
            F.lit(1),
        )
        .when(
            F.col("a1_new_salary_acct_flag").isNull()
            & F.col("_fea_salary_acct_flag").isNull(),
            F.lit(None).cast("int"),
        )
        .otherwise(F.lit(0)),
    ).drop("_fea_salary_acct_flag")

    return result.select(
        *grain_key,
        F.col("recurring_inflow_amt_h2").cast("double"),
        F.col("recurring_inflow_cnt_h2").cast("int"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("bureau_salary_amt_last").cast("double"),
        F.col("a1_new_salary_acct_flag").cast("int"),
        F.col("a1_offus_paying_flag").cast("int"),
    )


# ── Node 3r: build_a1_group_b_income_recent ───────────────────────────────────


def build_a1_group_b_income_recent(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_casa_inflow: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """observation_date-anchored income signals.

    Same logic as build_a1_group_b_income but anchors all H2 windows to
    observation_date instead of t0.  Enables dynamic re-scoring at each
    collection run: answers "what is the customer's financial state RIGHT NOW?"
    rather than "what was it when they went delinquent?".

    For accounts where observation_date == t0 (freshly delinquent), results
    are identical to the T0 variant — correct by design.
    """
    return build_a1_group_b_income(
        cif_enriched,
        feat_payroll,
        feat_casa_bal,
        wm_salary,
        wm_casa_inflow,
        wm_labelled_transactions,
        beneficiary_cards,
        crx_persona,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 4r: build_a1_group_b_bureau_recent ───────────────────────────────────


def build_a1_group_b_bureau_recent(  # pylint: disable=too-many-arguments
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
) -> DataFrame:
    """observation_date-anchored bureau + recurring inflow signals.

    Same logic as build_a1_group_b_bureau but anchors all windows to
    observation_date instead of t0.
    """
    return build_a1_group_b_bureau(
        cif_enriched,
        wm_recurring,
        stg_salary_hist,
        prm_bureau_alert,
        prm_bureau_cif_bridge,
        fea_aecb_alerts,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 5: build_a1_group_c ──────────────────────────────────────────────────


def build_a1_group_c(
    base: DataFrame,
    payment_traj: DataFrame,
    util_features: DataFrame,
    prm_balance: DataFrame,
) -> DataFrame:
    """Payment trajectory, utilisation, and outstanding balance (spell-grain).

    Three enrichers joined at (account_id, spell_id) — no CIF bridge required:
      1. crx_cc_payment_trajectory (T04b) → pay_ratio_slope, pay_ratio_mean_h1/h2
      2. crx_cc_utilisation_features (T05) → util_t0, util_slope, spend_cliff_flag
      3. prm_balance — PIT at banking_date ≤ T0 → cc_total_outstanding

    This node runs in parallel with Nodes 3 and 4 (depends only on Node 1 output).

    Args:
        base:          crx_cc_a1_base. Grain: (account_id, spell_id).
        payment_traj:  crx_cc_payment_trajectory (T04b).
        util_features: crx_cc_utilisation_features (T05).
        prm_balance:   prm_balance.

    Returns:
        crx_cc_a1_group_c — (account_id, spell_id, pay_ratio_slope,
            pay_ratio_mean_h1, pay_ratio_mean_h2, util_t0, util_slope,
            spend_cliff_flag, cc_total_outstanding).
    """
    # Dedup base to spell grain — base is at spine grain after build_a1_base rework.
    # T04b / T05 / prm_balance are all T0-anchored spell-grain enrichers; feeding
    # N spine rows per spell would produce Nx overcounting in those joins.
    spell_base = base.dropDuplicates(["account_id", "spell_id"])

    t04b = enrichers.enrich_payment_trajectory(spell_base, payment_traj)
    t05 = enrichers.enrich_utilisation(spell_base, util_features)
    bal = enrichers.enrich_prm_balance(spell_base, prm_balance)

    result = spell_base.select("account_id", "spell_id")

    if t04b is not None:
        result = result.join(t04b, on=["account_id", "spell_id"], how="left")
    else:
        result = (
            result.withColumn("pay_ratio_slope", F.lit(None).cast("double"))
            .withColumn("pay_ratio_mean_h1", F.lit(None).cast("double"))
            .withColumn("pay_ratio_mean_h2", F.lit(None).cast("double"))
        )

    if t05 is not None:
        result = result.join(t05, on=["account_id", "spell_id"], how="left")
    else:
        result = (
            result.withColumn("util_t0", F.lit(None).cast("double"))
            .withColumn("util_slope", F.lit(None).cast("double"))
            .withColumn("spend_cliff_flag", F.lit(None).cast("int"))
        )

    if bal is not None:
        result = result.join(bal, on=["account_id", "spell_id"], how="left")
    else:
        result = result.withColumn("cc_total_outstanding", F.lit(None).cast("double"))

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("pay_ratio_mean_h1").cast("double"),
        F.col("pay_ratio_mean_h2").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("util_slope").cast("double"),
        F.col("spend_cliff_flag").cast("int"),
        F.col("cc_total_outstanding").cast("double"),
    )


# ── Node 5r: build_a1_group_c_recent ──────────────────────────────────────────


def build_a1_group_c_recent(
    base: DataFrame,
    prm_balance: DataFrame,
) -> DataFrame:
    """Outstanding balance at observation_date grain (spine-grain counterpart to group_c).

    Single enricher — only cc_total_outstanding_recent is needed at obs-date anchor.
    Payment trajectory and utilisation are T0-anchored spell-grain features and are
    not re-windowed here.

    Args:
        base:        crx_cc_a1_base — spine grain (account_id, observation_date).
        prm_balance: prm_balance — CC outstanding balance history.

    Returns:
        DataFrame (account_id, observation_date, cc_total_outstanding_recent).
        cc_total_outstanding_recent is NULL if prm_balance has no row at or before
        the scoring observation_date.
    """
    bal = enrichers.enrich_prm_balance(
        base,
        prm_balance,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )

    result = base.select("account_id", "observation_date").dropDuplicates(
        ["account_id", "observation_date"]
    )

    if bal is not None:
        result = result.join(bal, on=["account_id", "observation_date"], how="left")
    else:
        result = result.withColumn(
            "cc_total_outstanding_recent", F.lit(None).cast("double")
        )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("cc_total_outstanding_recent").cast("double"),
    )


# ── Classify helpers (private) ────────────────────────────────────────────────


def _assemble_classify_inputs(  # pylint: disable=too-many-arguments
    base: DataFrame,
    group_b_income: DataFrame,
    group_b_bureau: DataFrame,
    group_c: DataFrame,
    inc_recent: DataFrame,
    bur_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Join all enrichments onto base; derive EOSB proxy flags and T0 debt-load ratio.

    Renames obs-date-anchored (_recent) columns with the ``_recent`` suffix so
    both T0 and obs-date variants coexist on the same row.  All subsequent
    classifier helpers operate on the assembled result.
    """
    _inc_recent_cols = [
        "salary_months_h2",
        "casa_eod_bal_h2",
        "salary_amt_last",
        "salary_change_pct",
        "months_runway",
        "casa_inflow_amt_h2",
        "casa_inflow_cnt_h2",
        "ext_cc_payment_amt_h2",
        "ext_cc_payment_cnt_h2",
    ]
    _bur_recent_cols = [
        "recurring_inflow_amt_h2",
        "recurring_inflow_cnt_h2",
        "bureau_salary_present_6m_flag",
        "bureau_salary_amt_last",
        "a1_new_salary_acct_flag",
        "a1_offus_paying_flag",
    ]
    inc_recent_renamed = inc_recent.select(
        "account_id",
        "observation_date",
        *[F.col(c).alias(f"{c}_recent") for c in _inc_recent_cols],
    )
    bur_recent_renamed = bur_recent.select(
        "account_id",
        "observation_date",
        *[F.col(c).alias(f"{c}_recent") for c in _bur_recent_cols],
    )

    # T0-anchored (spell-grain) joins broadcast to all spine obs_dates.
    # Obs-date-anchored (_recent) joins match the exact scoring date.
    result = (
        base.join(group_b_income, on=["account_id", "spell_id"], how="left")
        .join(group_b_bureau, on=["account_id", "spell_id"], how="left")
        .join(group_c, on=["account_id", "spell_id"], how="left")
        .join(inc_recent_renamed, on=["account_id", "observation_date"], how="left")
        .join(bur_recent_renamed, on=["account_id", "observation_date"], how="left")
        .join(group_c_recent, on=["account_id", "observation_date"], how="left")
    )

    # eosb_post_salary_flag: obs-date bureau signal confirms post-EOSB income
    result = result.withColumn(
        "eosb_post_salary_flag",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # eosb_post_salary_flag_recent: same proxy anchored to obs-date bureau signal
    result = result.withColumn(
        "eosb_post_salary_flag_recent",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # Fix 4b: recompute months_runway with bureau_salary_amt_last fallback.
    # Node 3 computes months_runway without bureau salary because bureau data
    # (Node 4) is not yet available.  Here in Node 6, all inputs are joined so
    # we override with the full denominator waterfall matching cc_outstanding_vs_income.
    _runway_income_t0 = F.coalesce(
        F.col("salary_amt_last"),
        F.col("bureau_salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway",
        F.when(
            F.col("casa_eod_bal_h2").isNotNull()
            & _runway_income_t0.isNotNull()
            & (_runway_income_t0 > 0),
            F.col("casa_eod_bal_h2") / _runway_income_t0,
        ).otherwise(F.lit(None).cast("double")),
    )
    _runway_income_recent = F.coalesce(
        F.col("salary_amt_last_recent"),
        F.col("bureau_salary_amt_last_recent"),
        F.col("casa_inflow_amt_h2_recent") / F.lit(3.0),
    )
    result = result.withColumn(
        "months_runway_recent",
        F.when(
            F.col("casa_eod_bal_h2_recent").isNotNull()
            & _runway_income_recent.isNotNull()
            & (_runway_income_recent > 0),
            F.col("casa_eod_bal_h2_recent") / _runway_income_recent,
        ).otherwise(F.lit(None).cast("double")),
    )

    # cc_outstanding_vs_income: debt load in months of T0-anchored income
    _income_monthly = F.coalesce(
        F.col("salary_amt_last"),
        F.col("bureau_salary_amt_last"),
        F.col("casa_inflow_amt_h2") / F.lit(3.0),
    )
    result = result.withColumn(
        "cc_outstanding_vs_income",
        F.when(
            F.col("cc_total_outstanding").isNotNull()
            & _income_monthly.isNotNull()
            & (_income_monthly > 0),
            F.col("cc_total_outstanding") / _income_monthly,
        ).otherwise(F.lit(None).cast("double")),
    )

    return result


def _build_ability_conditions(suffix: str = "", obs_date_only: bool = False) -> dict:
    """Build D1–D5 condition expressions for a given signal anchor.

    Args:
        suffix: ``""`` for T0-anchored signals; ``"_recent"`` for obs-date-anchored.
                D3 (pressure_high) and D4 (trajectory_gradual, trajectory_sudden)
                always use T0-anchored Group C columns regardless of suffix —
                Group C is not re-windowed at obs-date.
        obs_date_only: When True, removes T0 Group A gates (payroll_present_h2,
                payroll_stopped_flag, casa_inflow_stop_gap_d) from income_active,
                income_stopped, and income_present.  Used for the primary
                a1_state classifier.  GRR feedback (Sep 2026): ability must
                reflect current state, not pre-delinquency behaviour.

    Returns:
        Dict of Spark Column expressions keyed by condition name.
    """
    # D1 — Income flow
    if obs_date_only:
        # Obs-date-only variant: no T0 Group A gates.
        # income_active: any obs-date income signal above threshold fires.
        # casa_inflow_stop_gap_d (T0 Group A) is excluded; casa_inflow_cnt_h2_recent
        # covers the same population via the obs-date CASA inflow count.
        cond_income_active = (
            (
                F.col(f"salary_months_h2{suffix}").isNotNull()
                & (F.col(f"salary_months_h2{suffix}") >= _TAU_SALARY_H2_MIN)
            )
            | (F.col(f"bureau_salary_present_6m_flag{suffix}") == 1)
            | (
                F.col(f"casa_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"casa_inflow_cnt_h2{suffix}") >= _TAU_CASA_INFLOW_H2_MIN)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 2)
        )

        # income_stopped: no obs-date income signal from any source (absence check).
        # payroll_stopped_flag and payroll_present_h2 (T0) are excluded.
        cond_income_stopped = (
            (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) == 0)
            & (
                F.coalesce(F.col(f"bureau_salary_present_6m_flag{suffix}"), F.lit(0))
                != 1
            )
            & (F.coalesce(F.col(f"casa_inflow_cnt_h2{suffix}"), F.lit(0)) == 0)
        )

        # income_present: obs-date-only variant; T0 Group A gates excluded.
        # Fix: null-safe coalesce on salary_months_h2 — NULL comparison returns NULL
        # in Spark (treated as false). For cc_180_plus ~58% of rows have NULL
        # salary_months_h2; without coalesce the first arm is silently dead.
        cond_income_present = (
            (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) >= 1)
            | (
                F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"recurring_inflow_cnt_h2{suffix}") >= 1)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 1)
        )
    else:
        # Full T0-anchored variant with Group A gates.
        # Arm 1 requires payroll_present_h2 (Group A T0) as a gate.
        # Arm 3 uses casa_inflow_stop_gap_d (Group A T0).
        cond_income_active = (
            (
                (F.col("payroll_present_h2") == 1)
                & (
                    F.coalesce(
                        F.col(f"salary_months_h2{suffix}"), F.lit(_TAU_SALARY_H2_MIN)
                    )
                    >= _TAU_SALARY_H2_MIN
                )
                & (F.coalesce(F.col("payroll_stopped_flag"), F.lit(0)) == 0)
            )
            | (F.col(f"bureau_salary_present_6m_flag{suffix}") == 1)
            | (
                F.col("casa_inflow_stop_gap_d").isNotNull()
                & (F.col("casa_inflow_stop_gap_d") <= _TAU_INFLOW_GAP_D)
            )
            | (
                F.col(f"casa_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"casa_inflow_cnt_h2{suffix}") >= _TAU_CASA_INFLOW_H2_MIN)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 2)
        )

        cond_income_stopped = (
            (F.col("payroll_stopped_flag") == 1)
            & (
                F.coalesce(F.col(f"bureau_salary_present_6m_flag{suffix}"), F.lit(0))
                != 1
            )
            & (
                (F.coalesce(F.col("payroll_present_h2"), F.lit(0)) == 0)
                | (
                    F.col(f"salary_months_h2{suffix}").isNotNull()
                    & (F.col(f"salary_months_h2{suffix}") == 0)
                )
            )
        )

        # Fix: null-safe coalesce on salary_months_h2 — NULL comparison returns NULL
        # in Spark (treated as false). For cc_180_plus ~58% of rows have NULL
        # salary_months_h2; without coalesce the first arm of income_present is
        # silently dead for most of the population.
        cond_income_present = (
            (
                (F.col("payroll_present_h2") == 1)
                & (F.coalesce(F.col(f"salary_months_h2{suffix}"), F.lit(0)) == 1)
            )
            | (F.col("payroll_stopped_flag") == 1)
            | (
                F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull()
                & (F.col(f"recurring_inflow_cnt_h2{suffix}") >= 1)
            )
            | (F.coalesce(F.col(f"ext_cc_payment_cnt_h2{suffix}"), F.lit(0)) >= 1)
        )

    # D2 — Savings buffer
    cond_buffer_adequate = F.col(f"months_runway{suffix}").isNotNull() & (
        F.col(f"months_runway{suffix}") >= _TAU_MONTHS_RUNWAY
    )
    cond_buffer_not_adequate = F.col(f"months_runway{suffix}").isNull() | (
        F.col(f"months_runway{suffix}") < _TAU_MONTHS_RUNWAY
    )

    # D3 — Financial pressure at T0 (always T0-anchored — Group C not re-windowed)
    cond_pressure_high = F.col("util_t0").isNotNull() & (
        F.col("util_t0") >= _TAU_UTIL_PRESSURE
    )

    # D4 — Pre-T0 trajectory (always T0-anchored — Group C not re-windowed)
    cond_trajectory_gradual = (
        F.col("pay_ratio_slope").isNotNull()
        & (F.col("pay_ratio_slope") < _TAU_PAY_SLOPE_GRADUAL)
    ) | (
        F.col("util_slope").isNotNull()
        & (F.col("util_slope") > _TAU_UTIL_SLOPE_GRADUAL)
        & F.col("pay_ratio_mean_h2").isNotNull()
        & F.col("pay_ratio_mean_h1").isNotNull()
        & (F.col("pay_ratio_mean_h2") < F.col("pay_ratio_mean_h1"))
    )

    cond_trajectory_sudden = (
        F.col("pay_ratio_slope").isNull()
        | (F.col("pay_ratio_slope") >= _TAU_PAY_SLOPE_GRADUAL)
    ) & (F.col("spend_cliff_flag") == 1)

    # D5 — Recovery likelihood
    cond_recovery_likely = (
        (
            F.col(f"salary_change_pct{suffix}").isNotNull()
            & (F.col(f"salary_change_pct{suffix}") >= 0)
        )
        | (
            (F.col("eosb_like_flag") == 1)
            & (F.col(f"eosb_post_salary_flag{suffix}") == 1)
        )
    ) & (F.coalesce(F.col("prior_spell_cnt_24m"), F.lit(0)) == 0)

    # Derived compound conditions (suffix-dependent; kept in conds to avoid
    # passing suffix into _apply_ability_classifier)
    cond_recurring_moderate = F.col(f"recurring_inflow_cnt_h2{suffix}").isNotNull() & (
        F.col(f"recurring_inflow_cnt_h2{suffix}") >= _TAU_RECURRING
    )

    # EOSB limited: no confirmed post-EOSB salary; coalesce NULL → 0 (conservative)
    cond_eosb_limited = (F.col("eosb_like_flag") == 1) & (
        F.coalesce(F.col(f"eosb_post_salary_flag{suffix}"), F.lit(0)) != 1
    )

    return {
        "income_active": cond_income_active,
        "income_present": cond_income_present,
        "income_stopped": cond_income_stopped,
        "buffer_adequate": cond_buffer_adequate,
        "buffer_not_adequate": cond_buffer_not_adequate,
        "pressure_high": cond_pressure_high,
        "trajectory_gradual": cond_trajectory_gradual,
        "trajectory_sudden": cond_trajectory_sudden,
        "recovery_likely": cond_recovery_likely,
        "recurring_moderate": cond_recurring_moderate,
        "eosb_limited": cond_eosb_limited,
    }


def _apply_ability_classifier(df: DataFrame, conds: dict, state_col: str) -> DataFrame:
    """Apply the 4-state ordered CASE WHEN and return df with state_col added.

    Full waterfall: HIGH → MODERATE → LIMITED → UNKNOWN, using pressure,
    trajectory, and buffer gates from the supplied conditions dict.
    """
    cond_high = (
        conds["income_active"] & ~conds["pressure_high"] & ~conds["trajectory_gradual"]
    )

    cond_moderate = (
        (conds["income_active"] & conds["pressure_high"])
        | (conds["income_present"] & conds["buffer_adequate"])
        | (
            conds["income_stopped"]
            & conds["trajectory_sudden"]
            & conds["recovery_likely"]
        )
        | conds["recurring_moderate"]
    )

    cond_limited = (
        (conds["income_stopped"] & conds["buffer_not_adequate"])
        | (conds["income_present"] & conds["trajectory_gradual"])
        | (conds["pressure_high"] & conds["trajectory_gradual"])
        | conds["eosb_limited"]
    )

    return df.withColumn(
        state_col,
        F.when(cond_high, "ability_high")
        .when(cond_moderate, "ability_moderate")
        .when(cond_limited, "ability_limited")
        .otherwise("ability_unknown"),
    )


def _apply_ability_classifier_primary(
    df: DataFrame, conds: dict, state_col: str
) -> DataFrame:
    """Simplified 4-state waterfall for primary obs-date-anchored a1_state.

    GRR feedback (Sep 2026 workshop): ability must reflect the customer's current
    state, not pre-delinquency behaviour.  T0-anchored gates (pressure_high,
    trajectory_*, buffer_*) are excluded.

    Waterfall:
        HIGH:     income_active (obs-date income signals only)
        MODERATE: income_present | recovery_likely | recurring_moderate
        LIMITED:  income_stopped | eosb_limited
        UNKNOWN:  fallthrough (no obs-date income signal from any source)

    The CASA buffer (months_runway) is not a gate here — Collections places a lien
    on accessible ENBD CASA funds, so CASA balance is not genuinely available for
    voluntary repayment at 60+ DPD. months_runway_recent remains in the output as a
    pass-through diagnostic column.
    """
    cond_high = conds["income_active"]

    cond_moderate = (
        conds["income_present"] | conds["recovery_likely"] | conds["recurring_moderate"]
    )

    cond_limited = conds["income_stopped"] | conds["eosb_limited"]

    return df.withColumn(
        state_col,
        F.when(cond_high, "ability_high")
        .when(cond_moderate, "ability_moderate")
        .when(cond_limited, "ability_limited")
        .otherwise("ability_unknown"),
    )


def _build_a1_output_select(result: DataFrame) -> DataFrame:
    """Apply typed output schema and return final crx_cc_a1_ability DataFrame."""
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("a1_state").cast("string"),
        F.col("a1_provenance").cast("string"),
        F.col("a1_confidence").cast("double"),
        F.col("a1_payroll_stopped").cast("int"),
        F.col("casa_inflow_stop_gap_d").cast("double").alias("a1_casa_gap_d"),
        F.col("eosb_like_flag").cast("int").alias("a1_eosb_signal"),
        F.col("eosb_post_salary_flag").cast("int").alias("a1_eosb_post_salary"),
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("bureau_salary_amt_last").cast("double"),
        F.col("casa_inflow_amt_h2").cast("double"),
        F.col("casa_inflow_cnt_h2").cast("int"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("recurring_inflow_amt_h2").cast("double"),
        F.col("recurring_inflow_cnt_h2").cast("int"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("a1_new_salary_acct_flag").cast("int"),
        F.col("a1_offus_paying_flag").cast("int"),
        F.col("months_runway").cast("double"),
        F.col("cc_total_outstanding").cast("double"),
        F.col("cc_outstanding_vs_income").cast("double"),
        F.col("pre_stress_flag").cast("int"),
        F.col("pay_ratio_slope").cast("double"),
        F.col("util_t0").cast("double"),
        F.col("recovery_signal").cast("int"),
        F.col("a1_income_source").cast("string"),
        # obs-date feature columns (GRR Rows 2 / 6 / 7 / 10 compliance)
        F.col("salary_months_h2_recent").cast("int"),
        F.col("casa_eod_bal_h2_recent").cast("double"),
        F.col("casa_inflow_cnt_h2_recent").cast("int"),
        F.col("recurring_inflow_cnt_h2_recent").cast("int"),
        F.col("bureau_salary_present_6m_flag_recent").cast("int"),
        F.col("salary_amt_last_recent").cast("double"),
        F.col("months_runway_recent").cast("double"),
        F.col("cc_total_outstanding_recent").cast("double"),
        F.col("cc_outstanding_vs_income_recent").cast("double"),
        F.col("casa_coverage_ratio").cast("double"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )


# ── Node 6: build_a1_classify ─────────────────────────────────────────────────


def build_a1_classify(  # pylint: disable=too-many-arguments
    base: DataFrame,
    group_b_income: DataFrame,
    group_b_bureau: DataFrame,
    group_c: DataFrame,
    inc_recent: DataFrame,
    bur_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Assemble enriched signals and classify A1 income-ability state.

    Thin orchestrator: delegates assembly, condition building, classification,
    and output typing to private helpers.  a1_state is obs-date-anchored.
    a1_provenance: "obs_date" when ≥1 _recent income signal is non-null;
    "no_signal" when all _recent signals are null.

    The EOSB post-salary proxy is derived in _assemble_classify_inputs because
    it requires eosb_like_flag from the departure signature (Group A / base).
    Proxy logic: eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent=1 → 1
                 eosb_like_flag=1 AND bureau_salary_present_6m_flag_recent≠1 → 0
                 eosb_like_flag≠1 → NULL

    Args:
        base:           crx_cc_a1_base — Group A signals + t0.
        group_b_income: crx_cc_a1_group_b_income — T0-anchored income signals.
        group_b_bureau: crx_cc_a1_group_b_bureau — T0-anchored bureau + recurring.
        group_c:        crx_cc_a1_group_c — payment/utilisation/balance.
        inc_recent:     crx_cc_a1_group_b_income_recent — obs-date-anchored income.
        bur_recent:     crx_cc_a1_group_b_bureau_recent — obs-date-anchored bureau.
        group_c_recent: crx_cc_a1_group_c_recent — obs-date-anchored balance.

    Returns:
        crx_cc_a1_ability — ability axis with obs-date primary state.
    """
    result = _assemble_classify_inputs(
        base,
        group_b_income,
        group_b_bureau,
        group_c,
        inc_recent,
        bur_recent,
        group_c_recent,
    )

    # ── Obs-date-anchored state (primary) ─────────────────────────────────────
    # obs_date_only=True: removes T0 Group A gates from income_active and
    # income_stopped. T0 Group A signals (eosb_like_flag, prior_spell_cnt_24m)
    # remain in recovery_likely and eosb_limited — these describe spell-level
    # history that is still valid context, not current financial position.
    # GRR feedback (Sep 2026): ability must reflect current state.
    conds_recent = _build_ability_conditions("_recent", obs_date_only=True)
    result = _apply_ability_classifier_primary(
        result, conds_recent, state_col="a1_state"
    )

    # a1_payroll_stopped derives from the primary obs-date a1_state
    result = result.withColumn(
        "a1_payroll_stopped",
        F.when(
            F.col("a1_state").isin("ability_high", "ability_moderate")
            & (F.col("payroll_stopped_flag") == 1),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # pre_stress_flag intentionally broader than cond_trajectory_gradual:
    # rising utilisation alone is an early stress signal even before payment
    # performance deteriorates. cond_trajectory_gradual requires both.
    result = result.withColumn(
        "pre_stress_flag",
        F.when(
            (
                F.col("pay_ratio_slope").isNotNull()
                & (F.col("pay_ratio_slope") < _TAU_PAY_SLOPE_GRADUAL)
            )
            | (
                F.col("util_slope").isNotNull()
                & (F.col("util_slope") > _TAU_UTIL_SLOPE_GRADUAL)
            ),
            F.lit(1),
        )
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # Fix 4: recovery_signal derived directly from cond_recovery_likely — no duplication
    result = result.withColumn(
        "recovery_signal",
        F.when(conds_recent["recovery_likely"], F.lit(1))
        .otherwise(F.lit(0))
        .cast("int"),
    )

    # Provenance: obs_date when ≥1 _recent income signal present; no_signal otherwise
    result = result.withColumn(
        "a1_provenance",
        F.when(
            F.coalesce(
                F.col("salary_months_h2_recent"),
                F.col("casa_inflow_cnt_h2_recent"),
                F.col("bureau_salary_present_6m_flag_recent"),
            ).isNotNull(),
            F.lit("obs_date"),
        ).otherwise(F.lit("no_signal")),
    ).withColumn(
        "a1_confidence",
        F.when(F.col("a1_state") == "ability_high", F.lit(0.9))
        .when(F.col("a1_state") == "ability_moderate", F.lit(0.7))
        .when(F.col("a1_state") == "ability_limited", F.lit(0.4))
        .otherwise(F.lit(0.0)),
    )

    # a1_income_source: obs-date-anchored _recent signals only
    result = result.withColumn(
        "a1_income_source",
        F.when(
            F.coalesce(F.col("salary_months_h2_recent"), F.lit(0))
            >= _TAU_SALARY_H2_MIN,
            F.lit("payroll"),
        )
        .when(
            F.col("bureau_salary_present_6m_flag_recent") == 1,
            F.lit("bureau_salary"),
        )
        .when(
            F.col("casa_inflow_cnt_h2_recent").isNotNull()
            & (F.col("casa_inflow_cnt_h2_recent") >= _TAU_CASA_INFLOW_H2_MIN),
            F.lit("casa_generic"),
        )
        .when(
            F.coalesce(F.col("ext_cc_payment_cnt_h2_recent"), F.lit(0)) >= 2,
            F.lit("ext_cc_payment"),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    # CASA coverage ratio: obs-date balance vs obs-date outstanding (falls back to T0)
    _casa_bal_eff = F.coalesce(
        F.col("casa_eod_bal_h2_recent"), F.col("casa_eod_bal_h2")
    )
    _outstanding_eff = F.coalesce(
        F.col("cc_total_outstanding_recent"), F.col("cc_total_outstanding")
    )
    result = result.withColumn(
        "casa_coverage_ratio",
        F.when(
            _outstanding_eff.isNotNull() & (_outstanding_eff > 0),
            _casa_bal_eff / _outstanding_eff,
        ).otherwise(F.lit(None).cast("double")),
    )

    # DBR at scoring month (GRR Row 10): outstanding / monthly income at obs-date
    _income_recent = F.coalesce(
        F.col("salary_amt_last_recent"),
        F.col("bureau_salary_amt_last_recent"),
        F.col("casa_inflow_amt_h2_recent") / F.lit(3.0),
    )
    result = result.withColumn(
        "cc_outstanding_vs_income_recent",
        F.when(
            _outstanding_eff.isNotNull()
            & _income_recent.isNotNull()
            & (_income_recent > 0),
            _outstanding_eff / _income_recent,
        ).otherwise(F.lit(None).cast("double")),
    )

    result = _build_a1_output_select(result)
    enrichers.log_a1_stats(result)
    return result
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

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/pipeline.py`
action: replace · base sha256 `bf363d61358cdf5a6d64e2c673d4029ed275b6479c62738d47e56825852ec48e` · base trailing newline: yes · new sha256 `446f090d3e4bd711d4941dac20211808ba9764fe37cdebc65e441e897511bf88` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Kedro pipeline: T26 — A1 Ability axis v1.

# pylint: disable=line-too-long

Nine-node modular pipeline that derives the A1 income-ability axis and emits
the shipped persona column ``a1_state`` at (account_id, observation_date) grain.

Architecture:
    build_a1_base                  → crx_cc_a1_base                  [Node 1]
    build_a1_cif_bridge            → crx_cc_a1_cif_enriched          [Node 2]
    build_a1_group_b_income        → crx_cc_a1_group_b_income        [Node 3] ┐
    build_a1_group_b_bureau        → crx_cc_a1_group_b_bureau        [Node 4] ┤ parallel
    build_a1_group_c               → crx_cc_a1_group_c               [Node 5] ┤ (T0-anchored)
    build_a1_group_b_income_recent → crx_cc_a1_group_b_income_recent [Node 3r] ┤
    build_a1_group_b_bureau_recent → crx_cc_a1_group_b_bureau_recent [Node 4r] ┤ parallel
    build_a1_group_c_recent        → crx_cc_a1_group_c_recent        [Node 5r] ┘ (obs-date)
    build_a1_classify              → crx_cc_a1_ability               [Node 6]  ← shipped axis

Inputs:
    cc_spine                          Model-id-scoped spine (account_id, observation_date)
    crx_cc_spell_table                T03b — spell grain (account_id, spell_id, t0)
    crx_cc_departure_signature        T06  — Group A income signals (R14 reuse)
    prm_contract / prm_client         CIF bridge (contract_id → cif_id)
    feat_payroll_indicator            retail.feature_space — monthly payroll flag
    feat_casa_eod_balance             retail.feature_space — monthly CASA balance
    wm_fea_salary_days_since_increment WM — weekly salary recency + amount
    wm_fea_casa_weekly_repeated_inflow WM — weekly recurring non-salary inflow
    wm_fea_casa_cc_inflow_outflow     WM — weekly generic CASA inflow/outflow (all types)
    stg_aecb_salary_history           AECB — bureau salary history (6m window)
    prm_bureau_alert_enriched         AECB — bureau alerts (90d window)
    prm_bureau_cif_bridge             bureau file UUID → cif_id bridge
    fea_monthly_aecb_alerts           retail.feature_space — pre-engineered alert features
                                      (secondary source for a1_new_salary_acct_flag)
    crx_cc_payment_trajectory         T04b — payment trajectory (spell grain)
    crx_cc_utilisation_features       T05  — utilisation features (spell grain)
    prm_balance                       primary — CC outstanding balance (PIT at T0)

Output:
    crx_cc_a1_ability — A1 axis for every (account_id, observation_date) in cc_spine.
    a1_state ∈ {ability_high, ability_moderate, ability_limited, ability_unknown}.

    ⚠ All _TAU_ thresholds are PLACEHOLDERS — tune at Leg B after T26 PROD run.
    ⚠ WM feature coverage on delinquent CC population is UNPROVEN until T26 CHK-6.
    ⚠ Group B/C sibling-repo columns are NULL where schema guard fires.

Run with:
    kedro run --pipeline=crx_cc_a1_ability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_a1_base,
    build_a1_cif_bridge,
    build_a1_classify,
    build_a1_group_b_bureau,
    build_a1_group_b_bureau_recent,
    build_a1_group_b_income,
    build_a1_group_b_income_recent,
    build_a1_group_c,
    build_a1_group_c_recent,
)

_TAGS = ["crx", "a1", "ability", "persona_axis"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 9-node A1 Ability pipeline."""
    return Pipeline(
        [
            # ── Node 1: spine→spell window join + Group A departure signals ──
            node(
                func=build_a1_base,
                inputs=[
                    "cc_spine",
                    "crx_cc_spell_table",
                    "crx_cc_departure_signature",
                ],
                outputs="crx_cc_a1_base",
                name="build_crx_a1_base",
                tags=_TAGS,
            ),
            # ── Node 2: resolve CIF; emit CIF-keyed subset ──────────────────
            node(
                func=build_a1_cif_bridge,
                inputs=[
                    "crx_cc_a1_base",
                    "prm_contract",
                    "prm_client",
                ],
                outputs="crx_cc_a1_cif_enriched",
                name="build_crx_a1_cif_bridge",
                tags=_TAGS,
            ),
            # ── Node 3: WM + feature_space income signals (parallel) ────────
            node(
                func=build_a1_group_b_income,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1_group_b_income",
                name="build_crx_a1_group_b_income",
                tags=_TAGS,
            ),
            # ── Node 4: AECB bureau + WM recurring signals (parallel) ───────
            node(
                func=build_a1_group_b_bureau,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                ],
                outputs="crx_cc_a1_group_b_bureau",
                name="build_crx_a1_group_b_bureau",
                tags=_TAGS,
            ),
            # ── Node 3r: observation_date-anchored income signals (parallel) ─
            node(
                func=build_a1_group_b_income_recent,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_fea_casa_cc_inflow_outflow",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "params:crx_persona",
                ],
                outputs="crx_cc_a1_group_b_income_recent",
                name="build_crx_a1_group_b_income_recent",
                tags=_TAGS,
            ),
            # ── Node 4r: observation_date-anchored bureau signals (parallel) ─
            node(
                func=build_a1_group_b_bureau_recent,
                inputs=[
                    "crx_cc_a1_cif_enriched",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                ],
                outputs="crx_cc_a1_group_b_bureau_recent",
                name="build_crx_a1_group_b_bureau_recent",
                tags=_TAGS,
            ),
            # ── Node 5: payment trajectory + utilisation + balance (parallel) ─
            node(
                func=build_a1_group_c,
                inputs=[
                    "crx_cc_a1_base",
                    "crx_cc_payment_trajectory",
                    "crx_cc_utilisation_features",
                    "prm_balance",
                ],
                outputs="crx_cc_a1_group_c",
                name="build_crx_a1_group_c",
                tags=_TAGS,
            ),
            # ── Node 5r: obs-date-anchored balance (parallel with Node 5) ────
            node(
                func=build_a1_group_c_recent,
                inputs=["crx_cc_a1_base", "prm_balance"],
                outputs="crx_cc_a1_group_c_recent",
                name="build_crx_a1_group_c_recent",
                tags=_TAGS,
            ),
            # ── Node 6: assemble + classify → shipped persona axis ──────────
            node(
                func=build_a1_classify,
                inputs=[
                    "crx_cc_a1_base",
                    "crx_cc_a1_group_b_income",
                    "crx_cc_a1_group_b_bureau",
                    "crx_cc_a1_group_c",
                    "crx_cc_a1_group_b_income_recent",
                    "crx_cc_a1_group_b_bureau_recent",
                    "crx_cc_a1_group_c_recent",
                ],
                outputs="crx_cc_a1_ability",
                name="build_crx_a1_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: CC A1 ability axis on the shared ``a1_ability`` engine; the anchor is
the amount in the oldest overdue bucket (``nodes.py``).

Needs, for the model_id (cc_60_180 / cc_180_plus): ``crx_cc_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_cc_a1_ability

TEMPORARY (mirror bundle 08): ``create_b08_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b08_check_pipeline as _b08_check
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


def create_b08_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the CC A1 check (bundle 08)."""
    return _b08_check("cc", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/__init__.py`
action: replace · base sha256 `e30657e801349fce0071ff854a2a1ccc0d55f62897a97278ce96843a45e6ace4` · base trailing newline: yes · new sha256 `ae137b2821bbedc0351121d20386fec17b56756c30cf3466133b6d468dbac9e4` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL-A1-1 A1 Income-Ability axis for Retail Loans."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

New:

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b08_check_pipeline, create_pipeline

__all__ = ["create_b08_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/nodes.py`
action: replace · base sha256 `b5e615ae995904281125ee7ae0fe433b63eb0243371811593bd94b32baf5921a` · base trailing newline: yes · new sha256 `af87ae0a282a508d5dd43f11928eeda3286fb5769d00fd2659aa745951f751a7` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
# pylint: disable=R0917,R0801
"""RL-A1-1/9 — A1 Income-Ability axis for Retail Loans (4-node pipeline).

Four-node modular pipeline (T0 nodes removed in RL-A1-5 cleanup; Group A
departure removed in RL-A1-6 cleanup; Node 1 base join eliminated in
RL-A1-7 cleanup — trivial pass-through, crx_rl_a4_spine feeds Nodes 2r/3r/4r/4b
directly, and Node 5 inlines the eosb_like_flag / prior_spell_cnt_12m lookup).
cif_id is carried directly in crx_rl_a4_spine — no separate CIF bridge node needed.

    build_rl_a1_group_b_income_recent(crx_rl_a4_spine, ...)
        → crx_rl_a1_group_b_income_recent  [Node 2r] obs-date income signals

    build_rl_a1_group_b_bureau_recent(crx_rl_a4_spine, ...)
        → crx_rl_a1_group_b_bureau_recent  [Node 3r] obs-date bureau signals

    build_rl_a1_group_c_recent(crx_rl_a4_spine, int_loan_master)
        → crx_rl_a1_group_c_recent         [Node 4r] obs-date EMI coverage

    build_rl_a1_group_d_origination(crx_rl_a4_spine, feat_loan_application_risk)
        → crx_rl_a1_group_d                [Node 4b] Group D: static origination anchors

    build_rl_a1_classify(crx_rl_a4_spine, crx_rl_departure_signature,
        crx_rl_spell_table, ..., crx_rl_a1_group_d)
        → crx_rl_a1_ability                [Node 5]  ← shipped persona axis

Nodes removed (RL-A1-5 cleanup): Node 2 (T0 income), Node 3 (T0 bureau), Node 4 (Group C T0).
Nodes removed (RL-A1-6 cleanup): Node 0 (Group A T0 payroll departure).
Nodes removed (RL-A1-7 cleanup): Node 1 (crx_rl_a1_base join — trivial pass-through).
All a1_state and a1_income_source derivations use obs-date-anchored _recent signals only.
a1_provenance value set: {obs_date, no_signal}.

RL-A1-9 redesign (`data/input/ability_redesign_v3.md`): the classifier no longer
imports `_build_ability_conditions` / `_apply_ability_classifier_primary` from
`cc_a1_ability.nodes` — those stay untouched (R18). The RL waterfall is now
EMI-relative (Signal C: `monthly_emi_recent`) with CASA/payroll refinements
(Signals A/B/D/E) and AECB-anchored arms RL-A1-8 decided KEEP
(`moderate_arm2`, `low_tier2`) plus RL-A1-19's timing-anchored salary arm
(`high_arm3c`, replacing `high_arm7`/`high_arm3b`), built fresh in
`_build_rl_ability_conditions` / `_apply_rl_ability_classifier` below.
`"ability_limited"` is renamed `"ability_low"` (RL pipeline only — CC keeps
`"ability_limited"`), `recovery_signal` is dropped (depended only on the now-
removed import; v3 §7.4 — no replacement, see RESULTS_RL.md schema diff).
Excluded this round (separate follow-up task, see TASKS_RL.md Track E
RL-A1-14): `moderate_arm4a`, `moderate_arm4b`, `low_tier1` and their unique
AECB input columns. `ability_low` Condition 2 shipped under RL-A1-15 —
**removed entirely by RL-A1-21** (see below), its premise
(`inflow_present_h4_h6_recent`) no longer exists.

RL-A1-17 (fixed directly, per the RL-A4-2 cif_id precedent — RL-A1-9 is still
in-progress/unshipped, so R19 does not block iterating our own in-progress
build): Node 4r carried `disbursement_amount_recent`/`disbursement_date_recent`
(intermediate-only) to give Signal D a real disbursement exclusion instead of
RL-A1-9's unfiltered-alias fallback; `aecb_is_recent` is now a genuine
6-month recency cutoff instead of "any pull ever". **Historical note:** the
disbursement-exclusion half is removed entirely by RL-A1-21 (Signal D is
gone); the `high_arm7`/`high_arm3b` AECB carve-out this paragraph originally
described is removed and replaced by RL-A1-19's timing-anchored arms (see
below) — only the plain 6-month `aecb_is_recent` cutoff survives, still used
by `moderate_arm2`/`low_tier2`.

RL-A1-18 (CASA GL self-transfer wash exclusion for Signal D): Node 2r called
`enrichers.enrich_casa_self_transfer_wash_h2` on `comp_financial_tran_repos_dly`
(scope-first, R20/R14) to sum same-day GL-subhead bookkeeping credits
(`tran_type == "INTERNAL TRANSFER - SELF"`) in the same trailing-3m window
Signal D covered — a second, independent correction to
`casa_inflow_excl_disb_amt_3m_recent`. **Removed entirely by RL-A1-21** —
Signal D itself is gone, so this correction has nothing left to correct.

RL-A1-20 (CASA(CA+SA)/all-accounts EOD balance signals): Node 2r now pulls 12
balance columns from enrich_casa_eod_avg_balance (3 scope prefixes — ca
current-account-only, casa CA+SA, all CASA+investments+FDs — x 2 windows x
plain/_max), up from the 2 CA-only columns RL-A1-9 shipped. Every
balance-vs-EMI comparison (High Arm 1/4, the shared casa_low helper,
no_casa_flag_recent) is re-pointed to the casa (CA+SA) variant, which becomes
the primary gating balance; ca and all variants (plus every _max variant)
ship as diagnostic/passthrough columns only, wired into no gate.

RL-A1-19 (timing-anchored salary arms, replacing high_arm3/high_arm3b/
high_arm7): the user rejected comparing a bureau-reported salary amount
against monthly_emi_recent (old Arm 7) and the plain alert-only Arm 3/3b as
not meaningful affordability checks when the underlying bureau pull can be
dated anywhere in the past. Node 2 now also calls
enrichers.enrich_salary_stop_month (new function, mirrors
enrich_salary_months_h4_h6's [obs-6m, obs-3m) window with F.max instead of a
count) to carry salary_stop_month_recent — the actual calendar month payroll
last showed payroll_flag=1. `_aecb_recent_salary_arm` and the old
high_arm7/high_arm3b definitions are removed; replaced by a reworked
high_arm3 (salary stopped AND a bureau new-salary signal whose pull-dated leg
falls within _RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS before salary_stop_month)
and a new high_arm3c (salary never present in the 6m lookback AND the same
bureau new-salary signal, pull-dated leg within
_RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS of observation_date). Both arms are
amount-agnostic. `bureau_new_salary_signal_*` is an OR of an alert-based leg
(already recency-anchored to observation_date inside its own enricher — no
extra date gate) and a pull-dated leg (shares aecb_bureau_pull_date_recent
with feature_retail_loans — carries its own per-arm date gate). moderate_arm2/
low_tier2 are unaffected — they gate on plain aecb_is_recent, never
_aecb_recent_salary_arm.

RL-A1-23 (High Arm 6b, external loan payments): Node 2r now also calls
`enrichers.enrich_ext_loan_payments_h2` on `wm_fea_external_loan_payments`
(weekly PIT-joinable, no R2 look-ahead flag, confirmed Leg B) to carry
`ext_loan_payment_amt_h2_recent`/`_cnt_h2_recent` — "servicing another bank's
loan from this account" is the same evidentiary logic as the existing
`high_arm6` ("servicing another bank's credit card"), additive sibling arm,
`high_arm6` itself untouched.

RL-A1-21 (Signal D removal): Signal D (`casa_inflow_excl_disb_amt_3m`, a raw
sum of generic CASA credit transactions) and every dependent are removed
entirely — `enrich_casa_inflow_h2`/`enrich_casa_inflow_h4_h6`/
`enrich_casa_self_transfer_wash_h2` are no longer called from Node 2,
`months_runway` is gone, `high_arm5`/`moderate_arm3`/`low_cond2` are dropped
with no replacement, `low_cond1`'s trailing income clause is narrowed (not
replaced), `no_casa_flag_recent` is redefined on balance-nullness alone (its
`casa_inflow_cnt_h2_recent` clause is gone), and `a1_income_source`'s
`"casa_generic"` branch is removed. Per an explicit user ruling (2026-10-07):
no reliable PIT-joinable income source currently exists —
`wm_fea_income_from_sources` (RL-A1-22's planned replacement) is confirmed to
have no row-level history (see RESULTS_RL.md's 2026-10-07
RL-A1-22-REJECTED entry); a schema intelligence pipeline is being run on WM
feature datasets to find future candidates, but nothing is available now.
`enrich_casa_inflow_h2` itself is NOT deleted from `cc_a1_ability/enrichers.py`
— it is still used by the CC pipeline (R18) — only RL's call site to it is
removed.
"""

# pylint: disable=too-many-lines,too-many-locals,too-many-statements

import datetime
import logging

from dateutil.relativedelta import relativedelta

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

from enbd_collections.pipelines.crx_persona.cc_a1_ability import enrichers
from enbd_collections.pipelines.crx_persona.cc_a1_ability.nodes import (
    _TAU_SALARY_H2_MIN,
)

LOG = logging.getLogger(__name__)

# ── RL-A1-9 threshold constants (`_RL_TAU_*` prefix) ──────────────────────────
# Fires on count > 1 (repeated default) — RL-A1-8 chk8 live distribution
# (n=1,577, p10=5.0, p50=35.0) confirms real non-null values sit far from the
# 0/1 boundary, so the doc's placeholder is safe to keep as-is (no retuning).
_RL_TAU_AECB_DEFAULT_RECIDIVISM = 1

# RL-A1-17: genuine AECB recency cutoff, replacing the "any pull ever" framing.
# User-confirmed value (RL-A1-16 Leg B chk7 recency-sensitivity table).
_RL_TAU_AECB_RECENCY_MONTHS = 6

# RL-A1-19: timing-anchored salary-arm thresholds (replace high_arm3/3b/7's
# amount-vs-EMI framing with a pull-date-vs-salary-timing framing). User's
# starting values, PROD-confirmed sane by trl_a1_19_salary_timing_probe.py
# (Arm 3 fires 2.86%/691 rows, Arm 3c fires 3.04%/734 rows, mutually
# exclusive) — see RESULTS_RL.md 2026-10-07.
_RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS = 2
_RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS = 3

# RL-A1-20: the 12 CASA(CA+SA)/CA-only/all-accounts EOD balance columns
# enrich_casa_eod_avg_balance now emits (bare names, before the generic
# {col}_recent rename loop in _assemble_rl_classify_inputs). Shared between
# the NULL-fallback branch and the final output select below.
_CASA_EOD_BAL_OUTPUT_COLS = (
    "casa_eod_spot_ca",
    "casa_eod_spot_ca_max",
    "casa_eod_avg_3m_ca",
    "casa_eod_avg_3m_ca_max",
    "casa_eod_spot_casa",
    "casa_eod_spot_casa_max",
    "casa_eod_avg_3m_casa",
    "casa_eod_avg_3m_casa_max",
    "casa_eod_spot_all",
    "casa_eod_spot_all_max",
    "casa_eod_avg_3m_all",
    "casa_eod_avg_3m_all_max",
)


# ── Node 2: build_rl_a1_group_b_income ─────────────────────────────────────────


def build_rl_a1_group_b_income(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    wm_casa_avg_bal: DataFrame,
    wm_ext_loan_payments: DataFrame,
    *,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """WM / retail.feature_space income signals at CIF grain (Node 2).

    Calls CC enrichers directly (R14 reuse). Default grain is T0-anchored
    (account_id, spell_id). Pass anchor_col="observation_date" and
    grain_key=("account_id", "observation_date") for the obs-date delegate
    (Node 2r, build_rl_a1_group_b_income_recent).

    Enrichers called:
        1. enrich_salary_months_h2      → salary_months_h2
        2. enrich_casa_eod_bal_h2       → casa_eod_bal_h2
        3. enrich_salary_pit            → salary_amt_last, salary_change_pct
        4. enrich_ext_cc_payments_h2    → ext_cc_payment_amt_h2, ext_cc_payment_cnt_h2
        5. enrich_salary_months_h4_h6   → salary_months_h4_h6  (RL-A1-9 Signal A)
        6. enrich_casa_eod_avg_balance  → 12 CASA(CA+SA)/CA-only/all-accounts
                                          EOD balance columns (RL-A1-9/20
                                          Signal B; casa is the primary
                                          balance-vs-EMI gate, ca/all/_max
                                          are diagnostic-only)
        7. enrich_salary_stop_month     → salary_stop_month
                                          (RL-A1-19, timing-anchored high_arm3)
        8. enrich_ext_loan_payments_h2  → ext_loan_payment_amt_h2,
                                          ext_loan_payment_cnt_h2
                                          (RL-A1-23, High Arm 6b — external-
                                          bank loan servicing, same evidentiary
                                          logic as Arm 6's external-CC check)

    RL-A1-21 (Signal D removal): Signal D (`casa_inflow_excl_disb_amt_3m`, a
    raw sum of generic CASA credit transactions) and every dependent are
    removed entirely — `enrich_casa_inflow_h2`/`enrich_casa_inflow_h4_h6`/
    `enrich_casa_self_transfer_wash_h2` are no longer called here,
    `months_runway` is gone, and no replacement income-corroboration signal
    is wired in its place. Per an explicit user ruling (2026-10-07): no
    reliable PIT-joinable income source currently exists —
    `wm_fea_income_from_sources` (RL-A1-22's planned replacement) is
    confirmed to have no row-level history (see RESULTS_RL.md's 2026-10-07
    RL-A1-22-REJECTED entry); a schema intelligence pipeline is being run on
    WM feature datasets to find future candidates, but nothing is available
    now. `high_arm5`, `moderate_arm3`, and `low_cond2` are dropped entirely
    with no replacement; `low_cond1`'s trailing income clause is narrowed
    (not replaced). See `_build_rl_ability_conditions` below.

    Args:
        cif_enriched:             crx_rl_a1_base (carries cif_id).
        feat_payroll:             feat_payroll_indicator.
        feat_casa_bal:            feat_casa_eod_balance.
        wm_salary:                wm_fea_salary_days_since_increment.
        wm_labelled_transactions: wm_pri_labelled_transactions.
        beneficiary_cards:        raw_beneficiary_cards.
        wm_casa_avg_bal:          wm_fea_casa_eod_avg_balance.
        wm_ext_loan_payments:     wm_fea_external_loan_payments (RL-A1-23).
        anchor_col:               date column used as enricher anchor; default "t0".
        grain_key:                output grain tuple; default (account_id, spell_id).

    Returns:
        DataFrame at grain_key grain with 22 income columns.
    """
    # Dedup to grain to prevent NxM explosion
    cif_spell = cif_enriched.dropDuplicates(list(grain_key))

    salary_h2 = enrichers.enrich_salary_months_h2(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    casa_h2 = enrichers.enrich_casa_eod_bal_h2(
        cif_spell, feat_casa_bal, anchor_col, grain_key
    )
    sal_pit = enrichers.enrich_salary_pit(cif_spell, wm_salary, anchor_col, grain_key)
    obt_h2 = enrichers.enrich_ext_cc_payments_h2(
        cif_spell, wm_labelled_transactions, beneficiary_cards, anchor_col, grain_key
    )
    salary_h4_h6 = enrichers.enrich_salary_months_h4_h6(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    casa_avg_bal = enrichers.enrich_casa_eod_avg_balance(
        cif_spell, wm_casa_avg_bal, anchor_col, grain_key
    )
    salary_stop_month = enrichers.enrich_salary_stop_month(
        cif_spell, feat_payroll, anchor_col, grain_key
    )
    ext_loan_h2 = enrichers.enrich_ext_loan_payments_h2(
        cif_spell, wm_ext_loan_payments, anchor_col, grain_key
    )

    result = enrichers.join_required_signals(
        cif_spell.select(*grain_key),
        grain_key,
        [
            enrichers.RequiredJoin("enrich_salary_months_h2", salary_h2),
            enrichers.RequiredJoin("enrich_casa_eod_bal_h2", casa_h2),
            enrichers.RequiredJoin("enrich_salary_pit", sal_pit),
            enrichers.RequiredJoin("enrich_ext_cc_payments_h2", obt_h2),
            enrichers.RequiredJoin("enrich_salary_months_h4_h6", salary_h4_h6),
            enrichers.RequiredJoin("enrich_casa_eod_avg_balance", casa_avg_bal),
            enrichers.RequiredJoin("enrich_salary_stop_month", salary_stop_month),
            enrichers.RequiredJoin("enrich_ext_loan_payments_h2", ext_loan_h2),
        ],
    )

    return result.select(
        *grain_key,
        F.col("salary_months_h2").cast("int"),
        F.col("casa_eod_bal_h2").cast("double"),
        F.col("salary_amt_last").cast("double"),
        F.col("salary_change_pct").cast("double"),
        F.col("ext_cc_payment_amt_h2").cast("double"),
        F.col("ext_cc_payment_cnt_h2").cast("int"),
        F.col("salary_months_h4_h6").cast("int"),
        *[F.col(c).cast("double") for c in _CASA_EOD_BAL_OUTPUT_COLS],
        F.col("salary_stop_month").cast("date"),
        F.col("ext_loan_payment_amt_h2").cast("double"),
        F.col("ext_loan_payment_cnt_h2").cast("double"),
    )


# ── Node 2r: build_rl_a1_group_b_income_recent ─────────────────────────────────


def build_rl_a1_group_b_income_recent(
    cif_enriched: DataFrame,
    feat_payroll: DataFrame,
    feat_casa_bal: DataFrame,
    wm_salary: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    wm_casa_avg_bal: DataFrame,
    wm_ext_loan_payments: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored income signals (Node 2r). Delegate of Node 2.

    Calls build_rl_a1_group_b_income with anchor_col="observation_date" so
    the H2 window is [observation_date-3m, observation_date) rather than
    [t0-3m, t0). Grain is (account_id, observation_date).

    wm_pri_labelled_transactions is partitioned by week_number (one week per partition),
    so filter by tran_date >= persona_start_date to avoid a full-history scan.
    feat_payroll_indicator is a full-history snapshot within its partition; apply a
    row-level month_number floor to avoid shipping years of payroll history.
    wm_fea_casa_eod_avg_balance (RL-A1-9 Signal B) is unpinned on adv_load_date
    (no catalog leaf pin) — no raw-source filter needed here.
    wm_fea_external_loan_payments (RL-A1-23) is a weekly PIT-joinable series
    (week_number is the real per-row date, confirmed Leg B — see
    enrich_ext_loan_payments_h2) — no raw-source filter needed here, same
    treatment as wm_fea_casa_eod_avg_balance.

    Args:
        crx_persona: Persona param dict with persona_start_date.
    """
    persona_start = crx_persona["persona_start_date"]
    wm_labelled_transactions = wm_labelled_transactions.filter(
        F.col("tran_date") >= F.lit(persona_start)
    )
    payroll_floor_int = int(
        (datetime.date.fromisoformat(persona_start) - relativedelta(months=12))
        .isoformat()
        .replace("-", "")
    )
    feat_payroll = feat_payroll.filter(F.col("month_number") >= payroll_floor_int)
    # raw_beneficiary_cards is a live snapshot (no partition column)
    return build_rl_a1_group_b_income(
        cif_enriched,
        feat_payroll,
        feat_casa_bal,
        wm_salary,
        wm_labelled_transactions,
        beneficiary_cards,
        wm_casa_avg_bal,
        wm_ext_loan_payments,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )


# ── Node 3: build_rl_a1_group_b_bureau ─────────────────────────────────────────


def build_rl_a1_group_b_bureau(
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    *,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame:
    """AECB bureau + WM recurring inflow signals at CIF grain (Node 3).

    Calls CC enrichers directly (R14 reuse). Default grain is T0-anchored
    (account_id, spell_id). Pass anchor_col="observation_date" and
    grain_key=("account_id", "observation_date") for the obs-date delegate
    (Node 3r, build_rl_a1_group_b_bureau_recent).

    Enrichers called:
        1. enrich_recurring_inflow_h2  → recurring_inflow_amt_h2, recurring_inflow_cnt_h2
        2. enrich_bureau_salary        → bureau_salary_present_6m_flag, bureau_salary_amt_last
        3. enrich_bureau_alerts        → a1_new_salary_acct_flag, a1_offus_paying_flag
        4. enrich_fea_bureau_alerts    → fea_salary_acct_flag (combined into a1_new_salary_acct_flag)

    NULL-safe OR for a1_new_salary_acct_flag (verbatim from CC Node 4).

    Args:
        cif_enriched:          crx_rl_a1_base (carries cif_id).
        wm_recurring:          wm_fea_casa_weekly_repeated_inflow.
        stg_salary_hist:       stg_aecb_salary_history.
        prm_bureau_alert:      prm_bureau_alert_enriched.
        prm_bureau_cif_bridge: prm_bureau_cif_bridge.
        fea_aecb_alerts:       fea_monthly_aecb_alerts.
        anchor_col:            date column used as enricher anchor; default "t0".
        grain_key:             output grain tuple; default (account_id, spell_id).

    Returns:
        DataFrame at grain_key grain with 6 bureau columns.
    """
    cif_spell = cif_enriched.dropDuplicates(list(grain_key))

    rec_h2 = enrichers.enrich_recurring_inflow_h2(
        cif_spell, wm_recurring, anchor_col, grain_key
    )
    bur_sal = enrichers.enrich_bureau_salary(
        cif_spell, stg_salary_hist, prm_bureau_cif_bridge, anchor_col, grain_key
    )
    bur_alerts = enrichers.enrich_bureau_alerts(
        cif_spell, prm_bureau_alert, anchor_col, grain_key
    )
    fea_alerts = enrichers.enrich_fea_bureau_alerts(
        cif_spell, fea_aecb_alerts, anchor_col, grain_key
    )
    if fea_alerts is not None:
        fea_alerts = fea_alerts.withColumnRenamed(
            "fea_salary_acct_flag", "_fea_salary_acct_flag"
        )

    result = enrichers.join_required_signals(
        cif_spell.select(*grain_key),
        grain_key,
        [
            enrichers.RequiredJoin("enrich_recurring_inflow_h2", rec_h2),
            enrichers.RequiredJoin("enrich_bureau_salary", bur_sal),
            enrichers.RequiredJoin("enrich_bureau_alerts", bur_alerts),
            enrichers.RequiredJoin("enrich_fea_bureau_alerts", fea_alerts),
        ],
    )

    # NULL-safe OR (verbatim from CC Node 4)
    result = result.withColumn(
        "a1_new_salary_acct_flag",
        F.when(
            (F.coalesce(F.col("a1_new_salary_acct_flag"), F.lit(0)) == 1)
            | (F.coalesce(F.col("_fea_salary_acct_flag"), F.lit(0)) == 1),
            F.lit(1),
        )
        .when(
            F.col("a1_new_salary_acct_flag").isNull()
            & F.col("_fea_salary_acct_flag").isNull(),
            F.lit(None).cast("int"),
        )
        .otherwise(F.lit(0)),
    ).drop("_fea_salary_acct_flag")

    return result.select(
        *grain_key,
        F.col("recurring_inflow_amt_h2").cast("double"),
        F.col("recurring_inflow_cnt_h2").cast("int"),
        F.col("bureau_salary_present_6m_flag").cast("int"),
        F.col("bureau_salary_amt_last").cast("double"),
        F.col("a1_new_salary_acct_flag").cast("int"),
        F.col("a1_offus_paying_flag").cast("int"),
    )


# ── Node 3r: build_rl_a1_group_b_bureau_recent ─────────────────────────────────


#: feature_retail_loans → crx_rl_a1_group_b_bureau_recent AECB column schema
#: (RL-A1-9). Only the 7 columns the 4 decided-KEEP arms need (R18/task-card
#: "no reporting-only columns" rule) — excludes the Signal-B-dependent arms'
#: unique inputs (aecb_unique_income_records, aecb_total_products_dpd90_6m,
#: aecb_direct_debit_returns_6m, aecb_bank_outstanding_to_loan_pct,
#: bank_ever_90dpd_flag — RL-A1-14) and diagnostic-only columns
#: (aecb_cc_enquiries_30d, aecb_total_outstanding_balance).
_RL_A1_9_AECB_SCHEMA = {
    "aecb_bureau_pull_date": "date",
    "aecb_last_salary_credit_amount": "double",
    "aecb_salary_bank_product_count": "int",
    "aecb_income_record_changes_30d": "int",
    "aecb_total_active_cc_contracts": "long",
    "bank_worst_delinquency_6m_encoded": "int",
    "aecb_bank_times_in_default_90d": "long",
}


def build_rl_a1_group_b_bureau_recent(
    cif_enriched: DataFrame,
    wm_recurring: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_alert: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    fea_aecb_alerts: DataFrame,
    feature_retail_loans: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored bureau + recurring signals (Node 3r). Delegate of Node 3.

    Calls build_rl_a1_group_b_bureau with anchor_col="observation_date" so the
    bureau and recurring-inflow windows are anchored to observation_date rather
    than t0. Grain is (account_id, observation_date).

    WM inputs are pre-filtered to a single partition via the catalog
    (snapshot_adv_load_date global). Way4/AECB staging tables are range-filtered
    by edp_load_date to avoid full-history scans.

    RL-A1-9: left-joins feature_retail_loans directly on
    (account_id, observation_date) — already the grain feature_retail_loans
    is built at (feat_loan_application_risk's own PIT join: freshest
    bureau_pull_date <= observation_date), so no CIF bridge or additional
    PIT logic is needed here; see feat_loan_application_risk.py's module
    docstring for the forward-fill mechanics (PIT correctness for the rare
    multi-pull account, not frequent refresh).

    Schema guard: any missing AECB column raises RuntimeError — schema
    drift on this source is a defect to surface at build time, not degrade
    through silently.

    Args:
        feature_retail_loans: Retail-loan feature table at
            (account_id, observation_date) grain carrying the AECB columns.
        crx_persona: Persona param dict with persona_start_date.
    """
    bureau_floor = (
        datetime.date.fromisoformat(crx_persona["persona_start_date"])
        - relativedelta(months=12)
    ).isoformat()
    stg_salary_hist = stg_salary_hist.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    prm_bureau_alert = prm_bureau_alert.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    prm_bureau_cif_bridge = prm_bureau_cif_bridge.filter(
        F.col("edp_load_date") >= F.lit(bureau_floor)
    )
    # fea_monthly_aecb_alerts pre-filtered via catalog (snapshot_adv_load_date)
    result = build_rl_a1_group_b_bureau(
        cif_enriched,
        wm_recurring,
        stg_salary_hist,
        prm_bureau_alert,
        prm_bureau_cif_bridge,
        fea_aecb_alerts,
        anchor_col="observation_date",
        grain_key=("account_id", "observation_date"),
    )

    missing = [c for c in _RL_A1_9_AECB_SCHEMA if c not in feature_retail_loans.columns]
    if missing:
        raise RuntimeError(
            "build_rl_a1_group_b_bureau_recent: feature_retail_loans missing "
            f"{missing} — required source columns are missing. Fix the "
            "source or the schema; do not silently null the signal."
        )

    aecb = feature_retail_loans.select(
        "account_id",
        "observation_date",
        *[F.col(c).cast(dtype).alias(c) for c, dtype in _RL_A1_9_AECB_SCHEMA.items()],
    )
    result = result.join(aecb, on=["account_id", "observation_date"], how="left")

    return result


# ── Node 4r: build_rl_a1_group_c_recent ────────────────────────────────────────


def build_rl_a1_group_c_recent(
    base: DataFrame,
    int_loan_master: DataFrame,
    crx_persona: dict,
) -> DataFrame:
    """Obs-date-anchored EMI coverage window + monthly EMI (Node 4r).

    PIT window: [observation_date - 3m, observation_date]. Averages
    emi_coverage_ratio from int_loan_master over the 3 months
    immediately before each observation_date.

    monthly_emi_recent (RL-A1-9 Signal C): PIT installment_due_amount at the
    latest loan row in the same window, falling back to overdue_total when
    installment_due_amount is NULL — the EMI-relative threshold used
    throughout the redesigned ability_* waterfall.

    RL-A1-21: disbursement_amount_recent/disbursement_date_recent (RL-A1-17)
    are removed — they fed only Signal D's disbursement-exclusion
    correction, which no longer exists (see _build_rl_ability_conditions).

    Schema guard: if any of account_id, observation_date, emi_coverage_ratio,
    installment_due_amount, overdue_total are absent from int_loan_master,
    raises RuntimeError — schema drift on this source is a defect to surface
    at build time, not degrade through silently.

    Applies a 3-month partition floor on int_loan_master (persona_start_date - 3m)
    to avoid scanning the full loan history.

    Args:
        base:            crx_rl_a1_base — (account_id, observation_date, spell_id).
        int_loan_master: Trusted intermediate loan layer. Required: account_id,
                         observation_date, emi_coverage_ratio,
                         installment_due_amount, overdue_total.
        crx_persona:     Persona param dict with persona_start_date.

    Returns:
        DataFrame at (account_id, observation_date, spell_id) grain:
            account_id                string
            observation_date          date
            spell_id                  int
            emi_coverage_mean_recent  double  (NULL ~where feature absent)
            monthly_emi_recent        double  (NULL ~where feature absent)
    """
    c_floor = (
        datetime.date.fromisoformat(crx_persona["persona_start_date"])
        - relativedelta(months=3)
    ).isoformat()
    int_loan_master = int_loan_master.filter(
        F.col("observation_date") >= F.lit(c_floor)
    )

    obs_dates = base.select("account_id", "observation_date", "spell_id").distinct()

    _required = [
        "account_id",
        "observation_date",
        "emi_coverage_ratio",
        "installment_due_amount",
        "overdue_total",
    ]
    missing = [c for c in _required if c not in int_loan_master.columns]
    if missing:
        raise RuntimeError(
            f"build_rl_a1_group_c_recent: int_loan_master missing {missing}"
            " — required source columns are missing. Fix the source or the"
            " schema; do not silently null the signal."
        )

    loans_windowed = (
        int_loan_master.select(
            F.col("account_id").cast("string"),
            F.col("observation_date").cast("date").alias("_loan_obs_date"),
            F.col("emi_coverage_ratio").cast("double"),
            F.col("installment_due_amount").cast("double"),
            F.col("overdue_total").cast("double"),
        )
        .join(obs_dates, on="account_id", how="inner")
        .filter(
            (F.col("_loan_obs_date") <= F.col("observation_date"))
            & (F.col("_loan_obs_date") >= F.add_months(F.col("observation_date"), -3))
        )
    )

    emi_recent = loans_windowed.groupBy(
        "account_id", "observation_date", "spell_id"
    ).agg(F.mean("emi_coverage_ratio").alias("emi_coverage_mean_recent"))

    result = obs_dates.join(
        emi_recent, on=["account_id", "observation_date", "spell_id"], how="left"
    )

    w_pit = Window.partitionBy("account_id", "observation_date", "spell_id").orderBy(
        F.col("_loan_obs_date").desc()
    )
    pit_recent = (
        loans_windowed.withColumn("_rn", F.row_number().over(w_pit))
        .filter(F.col("_rn") == 1)
        .select(
            "account_id",
            "observation_date",
            "spell_id",
            F.coalesce(F.col("installment_due_amount"), F.col("overdue_total")).alias(
                "monthly_emi_recent"
            ),
        )
    )
    result = result.join(
        pit_recent, on=["account_id", "observation_date", "spell_id"], how="left"
    )

    total = result.count()
    covered = result.filter(F.col("emi_coverage_mean_recent").isNotNull()).count()
    covered_emi = result.filter(F.col("monthly_emi_recent").isNotNull()).count()
    LOG.info(
        "build_rl_a1_group_c_recent: %d rows | emi_coverage_mean_recent coverage %.1f%%"
        " | monthly_emi_recent coverage %.1f%%",
        total,
        100.0 * covered / max(total, 1),
        100.0 * covered_emi / max(total, 1),
    )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("emi_coverage_mean_recent").cast("double"),
        F.col("monthly_emi_recent").cast("double"),
    )


# ── Node 4b: build_rl_a1_group_d_origination ───────────────────────────────────

#: Source → output column rename map for Group D origination signals.
_GROUP_D_RENAME = {
    "aecb_score_at_orig": "aecb_score_at_origination",
    "aecb_total_outstanding_balance": "aecb_total_outstanding_at_origination",
    "bank_worst_delinquency_encoded": "aecb_bank_worst_dlq_at_origination",
    "bank_worst_delinquency_6m_encoded": "aecb_bank_worst_dlq_6m_at_origination",
    "bank_high_utilization_pct": "aecb_bank_high_util_pct_at_origination",
    "aecb_bank_outstanding_to_loan_pct": "aecb_bank_ob_to_loan_pct_at_origination",
    "credit_card_enquiries_12m": "aecb_cc_enquiries_12m_at_origination",
    "aecb_cc_enquiries_30d": "aecb_cc_enquiries_30d_at_origination",
    "aecb_direct_debit_returns_6m": "aecb_dd_returns_6m_at_origination",
    "aecb_bank_times_in_default_90d": "aecb_bank_times_default_90d_at_origination",
    "aecb_total_products_dpd90_6m": "aecb_tot_contracts_dpd90_6m_at_origination",
    "unauthorized_overdraft_flag": "aecb_has_unauth_od_at_origination",
    "bank_ever_90dpd_flag": "aecb_ever_90dpd_at_origination",
    "employer_validation_encoded": "dms_employer_validation_at_origination",
    "ale_indicator_flag": "dms_ale_indicator_at_origination",
    "first_salary_waiver_flag": "dms_first_sal_waiver_at_origination",
}

#: Output column types for Group D (after rename).
_GROUP_D_SCHEMA = {
    "aecb_score_at_origination": "double",
    "aecb_total_outstanding_at_origination": "double",
    "aecb_bank_worst_dlq_at_origination": "int",
    "aecb_bank_worst_dlq_6m_at_origination": "int",
    "aecb_bank_high_util_pct_at_origination": "double",
    "aecb_bank_ob_to_loan_pct_at_origination": "double",
    "aecb_cc_enquiries_12m_at_origination": "long",
    "aecb_cc_enquiries_30d_at_origination": "long",
    "aecb_dd_returns_6m_at_origination": "double",
    "aecb_bank_times_default_90d_at_origination": "long",
    "aecb_tot_contracts_dpd90_6m_at_origination": "long",
    "aecb_has_unauth_od_at_origination": "int",
    "aecb_ever_90dpd_at_origination": "int",
    "dms_employer_validation_at_origination": "int",
    "dms_ale_indicator_at_origination": "int",
    "dms_first_sal_waiver_at_origination": "int",
}


def build_rl_a1_group_d_origination(
    base: DataFrame,
    feat_loan_application_risk: DataFrame,
) -> DataFrame:
    """Add cross-bank origination bureau signals to the spell spine (Node 4b).

    Consumes feat_loan_application_risk — a pre-built, pre-encoded feature table
    combining AECB bureau pull + DMS underwriting at origination. All encoding is
    already done there; no re-implementation here.

    Join strategy: feat_loan_application_risk is at (account_id, observation_date)
    grain from the retail_loans pipeline. Since the same origination record is
    replicated identically across all observation_dates per account, we deduplicate
    to one row per account_id (taking the latest observation_date for safety) and
    join to the spell spine on account_id alone.

    Schema guard: if any required source column is missing from
    feat_loan_application_risk, raises RuntimeError — schema drift on this
    source is a defect to surface at build time, not degrade through
    silently.

    Not wired into create_pipeline() (orphaned since RL-A1-5) — kept for
    consistency with the fail-loud treatment applied to the other nodes in
    this file.

    Args:
        base:                       crx_rl_a1_base — (account_id, spell_id) grain.
        feat_loan_application_risk: Pre-encoded origination feature table.

    Returns:
        crx_rl_a1_group_d at (account_id, spell_id) grain with 16 _at_origination
        columns (AECB cross-bank bureau + DMS underwriting signals).
    """
    spell_base = base.dropDuplicates(["account_id", "spell_id"])

    missing = [
        c for c in _GROUP_D_RENAME if c not in feat_loan_application_risk.columns
    ]
    if missing:
        raise RuntimeError(
            "build_rl_a1_group_d_origination: feat_loan_application_risk missing "
            f"{missing} — required source columns are missing. Fix the source "
            "or the schema; do not silently null the signal."
        )

    # Deduplicate to one row per account — all rows are identical, take latest for safety
    w = Window.partitionBy("account_id").orderBy(F.col("observation_date").desc())
    feat_deduped = (
        feat_loan_application_risk.select(
            "account_id", "observation_date", *_GROUP_D_RENAME.keys()
        )
        .withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .drop("_rn", "observation_date")
    )

    # Rename source columns to _at_origination output names
    for src, dst in _GROUP_D_RENAME.items():
        feat_deduped = feat_deduped.withColumnRenamed(src, dst)

    result = spell_base.select("account_id", "spell_id").join(
        feat_deduped, on="account_id", how="left"
    )

    total = result.count()
    covered = result.filter(F.col("aecb_score_at_origination").isNotNull()).count()
    LOG.info(
        "build_rl_a1_group_d_origination: %d rows | aecb_score coverage %.1f%%",
        total,
        100.0 * covered / max(total, 1),
    )

    return result.select(
        F.col("account_id").cast("string"),
        F.col("spell_id").cast("int"),
        *[
            F.col(out_col).cast(dtype).alias(out_col)
            for out_col, dtype in _GROUP_D_SCHEMA.items()
        ],
    )


# ── Node 5 helpers (private) ───────────────────────────────────────────────────


def _assemble_rl_classify_inputs(
    spine: DataFrame,
    departure_signature: DataFrame,
    spell_table: DataFrame,
    group_b_income_recent: DataFrame,
    group_b_bureau_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Join all enrichment inputs onto spine for RL A1 classify (Node 5).

    Inlines the former Node 1 join: pulls eosb_like_flag from
    crx_rl_departure_signature and prior_spell_cnt_12m (renamed →
    prior_spell_cnt_24m) from crx_rl_spell_table directly — these were pure
    passthroughs inside the now-superseded crx_rl_a4_class (removed; see
    rl_a4_spine pipeline for its structural replacement). Only classification
    signals are selected — casa_inflow_stop_gap_d and emi_coverage_mean_h2 are
    A4-axis carry-through and not gates in _build_ability_conditions.

    All subsequent joins are obs-date-anchored (RL-A1-3 cleanup — T0 nodes removed;
    RL-A1-6 cleanup — Group A T0 departure removed).
    Obs-date joins at (account_id, observation_date) grain:
        group_b_income_recent → {col}_recent columns (salary_months_h2_recent, etc.)
        group_b_bureau_recent → {col}_recent columns (bureau_salary_present_6m_flag_recent
        group_c_recent        → emi_coverage_mean_recent

    eosb_post_salary_flag uses bureau_salary_present_6m_flag_recent (obs-date signal).

    RL-A1-21: Signal D (`casa_inflow_excl_disb_amt_3m_recent`) and both of
    its corrections (RL-A1-17's disbursement exclusion, RL-A1-18's GL
    self-transfer wash exclusion) are removed entirely — the column no
    longer exists.
    """
    # Inline Node 1: attach eosb_like_flag (from crx_rl_departure_signature,
    # deduped to spell grain — constant per spell) and prior_spell_cnt_12m
    # (from crx_rl_spell_table, already at spell grain), renamed →
    # prior_spell_cnt_24m. Formerly sourced from crx_rl_a4_class, which was a
    # pure passthrough of both columns — no unique logic lost by reading them
    # directly from their origin tables.
    eosb_sel = departure_signature.select(
        "account_id", "spell_id", F.col("eosb_like_flag").cast("int")
    ).dropDuplicates(["account_id", "spell_id"])
    prior_spell_sel = spell_table.select(
        "account_id",
        "spell_id",
        F.col("prior_spell_cnt_12m").cast("int").alias("prior_spell_cnt_24m"),
    )
    result = spine.join(eosb_sel, on=["account_id", "spell_id"], how="left").join(
        prior_spell_sel, on=["account_id", "spell_id"], how="left"
    )

    # group_b_income_recent: rename data columns to *_recent before joining
    _income_keys = {"account_id", "observation_date"}
    income_recent = group_b_income_recent
    for _col in [c for c in income_recent.columns if c not in _income_keys]:
        income_recent = income_recent.withColumnRenamed(_col, f"{_col}_recent")
    result = result.join(
        income_recent, on=["account_id", "observation_date"], how="left"
    )

    # group_b_bureau_recent: rename data columns to *_recent before joining
    _bureau_keys = {"account_id", "observation_date"}
    bureau_recent = group_b_bureau_recent
    for _col in [c for c in bureau_recent.columns if c not in _bureau_keys]:
        bureau_recent = bureau_recent.withColumnRenamed(_col, f"{_col}_recent")
    result = result.join(
        bureau_recent, on=["account_id", "observation_date"], how="left"
    )

    # group_c_recent: emi_coverage_mean_recent / monthly_emi_recent (RL-A1-9 Signal C)
    result = result.join(
        group_c_recent.select(
            "account_id",
            "observation_date",
            "emi_coverage_mean_recent",
            "monthly_emi_recent",
        ),
        on=["account_id", "observation_date"],
        how="left",
    )

    # eosb_post_salary_flag: obs-date-anchored bureau signal
    result = result.withColumn(
        "eosb_post_salary_flag",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # eosb_post_salary_flag_recent: mirrors eosb_post_salary_flag (same signal, obs-date variant)
    result = result.withColumn(
        "eosb_post_salary_flag_recent",
        F.when(
            (F.col("eosb_like_flag") == 1)
            & (F.col("bureau_salary_present_6m_flag_recent") == 1),
            F.lit(1),
        )
        .when(F.col("eosb_like_flag") == 1, F.lit(0))
        .otherwise(F.lit(None).cast("int")),
    )

    # ── RL-A1-9 derived signals (built before the classifier) ──────────────────

    # salary_stopped_flag_recent (v3 §7): payroll present 3-6m back, stopped
    # in the last 3m. Always a definite 0/1 (coalesced inputs — never NULL).
    result = result.withColumn(
        "salary_stopped_flag_recent",
        (
            (F.coalesce(F.col("salary_months_h4_h6_recent"), F.lit(0)) > 0)
            & (F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) == 0)
        ).cast("int"),
    )

    # no_casa_flag_recent (v3 §7 Signal E): no observable ENBD CASA
    # relationship — all CASA(CA+SA) balance signals NULL (RL-A1-20
    # re-point — was CA-only casa_eod_spot_recent/casa_eod_avg_3m_recent)
    # and casa_eod_bal_h2_recent NULL. RL-A1-21: the casa_inflow_cnt_h2_recent
    # clause is dropped — that column no longer exists (Signal D removal).
    result = result.withColumn(
        "no_casa_flag_recent",
        (
            F.col("casa_eod_spot_casa_recent").isNull()
            & F.col("casa_eod_avg_3m_casa_recent").isNull()
            & F.col("casa_eod_bal_h2_recent").isNull()
        ).cast("int"),
    )

    # aecb_is_recent (RL-A1-17): genuine recency cutoff, replacing the "any
    # pull ever" framing RL-A1-9 shipped with. RL-A1-16 Leg B's chk7 recency-
    # sensitivity table showed "any pull" collapses the overall ability_high
    # rate from 70.9% to 59.2%/60.1%/62.8% under 3m/6m/12m cutoffs — user
    # confirmed 6 months as the cutoff to ship. moderate_arm2/low_tier2 use
    # this base definition unmodified. high_arm3/high_arm3c (RL-A1-19) do not
    # use aecb_is_recent at all — they gate on their own, narrower timing
    # comparisons (pull date vs. salary_stop_month_recent / observation_date)
    # instead of this 6-month cutoff.
    result = result.withColumn(
        "aecb_is_recent",
        (
            F.col("aecb_bureau_pull_date_recent").isNotNull()
            & (
                F.months_between(
                    F.col("observation_date"), F.col("aecb_bureau_pull_date_recent")
                )
                <= _RL_TAU_AECB_RECENCY_MONTHS
            )
        ).cast("int"),
    )

    return result


def _build_rl_ability_conditions() -> dict:
    """Build the RL-A1-9 ability waterfall condition expressions (RL-local).

    Replaces the shared `_build_ability_conditions` import from
    `cc_a1_ability.nodes` entirely (R18 — that function and
    `_apply_ability_classifier_primary` are untouched). Built from
    `ability_redesign_v3.md` Sections 2-5, scoped per RESULTS_RL.md
    (2026-10-02): the full EMI-relative base waterfall, plus the AECB-anchored
    arms RL-A1-8 decided KEEP (`moderate_arm2`, `low_tier2`) and RL-A1-19's
    timing-anchored salary arm (`high_arm3c`, replacing `high_arm7`/
    `high_arm3b`).

    Explicitly NOT built here (separate follow-up task — TASKS_RL.md Track E
    RL-A1-14, see this module's docstring):
        moderate_arm4a, moderate_arm4b (Signal-B-dependent, RL-A1-8 undecided)
        low_tier1                      (Signal-B-dependent, RL-A1-8 undecided)

    monthly_emi_recent is coalesced to a large sentinel in every comparison so
    a NULL EMI makes the comparison False, not NULL (v3 §2 note) — otherwise
    a missing EMI would silently drop a row out of every EMI-gated arm.

    aecb_is_recent (RL-A1-17) is a genuine 6-month recency cutoff on
    aecb_bureau_pull_date_recent (see _assemble_rl_classify_inputs), replacing
    RL-A1-9's "any pull ever" framing. moderate_arm2/low_tier2 gate on this
    plain cutoff, unmodified. high_arm3/high_arm3c (RL-A1-19) use their own,
    narrower timing comparisons instead (pull date vs. salary_stop_month_recent
    / observation_date) — see below.

    Returns:
        Dict of Spark Column expressions keyed by state name
        (cond_high / cond_low / cond_moderate).
    """
    _emi = F.coalesce(F.col("monthly_emi_recent"), F.lit(1.0e18))
    _aecb_recent = F.col("aecb_is_recent") == 1
    _pull_date = F.col("aecb_bureau_pull_date_recent")

    # ── RL-A1-19: timing-anchored salary-arm bureau signal ─────────────────────
    # Replaces RL-A1-17's _aecb_recent_salary_arm (amount-vs-EMI framing,
    # high_arm7/high_arm3b) — a stale bureau pull showing a large historical
    # salary says nothing about ability to pay today. bureau_new_salary_signal
    # is an OR of two sub-signals that do NOT share a pull date (2026-10-06
    # correction, RESULTS_RL.md "Proposed amendments" — AND'ing the whole OR
    # against aecb_bureau_pull_date_recent produced a near-zero fire rate by
    # stacking two independent, uncorrelated date constraints):
    #   - alert-based leg: already recency-anchored to observation_date
    #     inside its own enricher (enrich_bureau_alerts' 90d window /
    #     enrich_fea_bureau_alerts' latest-month-before PIT join) — fires on
    #     its own, no additional date gate here.
    #   - pull-dated leg: genuinely shares aecb_bureau_pull_date_recent with
    #     the same feature_retail_loans row — keeps its own per-arm date gate.
    _bureau_new_salary_signal_alert_based = (
        F.coalesce(F.col("a1_new_salary_acct_flag_recent"), F.lit(0)) == 1
    )
    _bureau_new_salary_signal_pull_dated = (
        F.coalesce(F.col("aecb_income_record_changes_30d_recent"), F.lit(0)) > 0
    ) | (F.coalesce(F.col("aecb_salary_bank_product_count_recent"), F.lit(0)) >= 1)

    # casa_low (v3 §3): single reusable expression — gates Low Cond 1/2 and
    # Moderate Arm 3 (Arm 4a/4b, which also use it, are out of scope).
    # RL-A1-20: re-pointed to CASA(CA+SA) — was CA-only casa_eod_avg_3m_recent.
    casa_low = F.col("casa_eod_avg_3m_casa_recent").isNull() | (
        F.col("casa_eod_avg_3m_casa_recent") < _emi
    )

    # ── ability_high: Arms 1-6 (Arm 3 now timing-anchored, RL-A1-19) + Arm 3c
    # (AECB-only, RL-A1-19, replaces high_arm7/high_arm3b) + Arm 6b
    # (external loan payments, RL-A1-23) (v3 §2) ──────────────────────────────
    # RL-A1-20: High Arm 1 re-pointed to CASA(CA+SA) spot — was CA-only
    # casa_eod_spot_recent.
    high_arm1 = F.col("casa_eod_spot_casa_recent").isNotNull() & (
        F.col("casa_eod_spot_casa_recent") >= _emi
    )
    high_arm2 = (
        F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) >= _TAU_SALARY_H2_MIN
    ) & (F.col("salary_stopped_flag_recent") == 0)
    # Arm 3 (RL-A1-19, timing-anchored, replaces the plain alert-only check):
    # salary stopped AND a bureau new-salary signal whose pull-dated leg (if
    # that's the leg firing) falls at/within _RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS
    # before the month salary stopped — the alert-based leg needs no extra gate.
    _high_arm3_pull_dated_leg = (
        _bureau_new_salary_signal_pull_dated
        & _pull_date.isNotNull()
        & F.col("salary_stop_month_recent").isNotNull()
        & (
            _pull_date
            >= F.add_months(
                F.col("salary_stop_month_recent"),
                -_RL_TAU_SALARY_STOP_PULL_LEAD_MONTHS,
            )
        )
        & (_pull_date <= F.col("salary_stop_month_recent"))
    )
    high_arm3 = (F.col("salary_stopped_flag_recent") == 1) & (
        _bureau_new_salary_signal_alert_based | _high_arm3_pull_dated_leg
    )
    # RL-A1-20: High Arm 4 re-pointed to CASA(CA+SA) 3m avg — was CA-only
    # casa_eod_avg_3m_recent.
    high_arm4 = F.col("casa_eod_avg_3m_casa_recent").isNotNull() & (
        F.col("casa_eod_avg_3m_casa_recent") >= _emi
    )
    # High Arm 5 (RL-A1-21): removed entirely — it gated on Signal D
    # (casa_inflow_excl_disb_amt_3m_recent), which no longer exists. No
    # replacement income-corroboration arm is wired in its place (see
    # module docstring).
    high_arm6 = F.col("ext_cc_payment_amt_h2_recent").isNotNull() & (
        F.col("ext_cc_payment_amt_h2_recent") >= _emi
    )
    # Arm 6b (RL-A1-23): servicing another bank's loan from this CASA account —
    # same evidentiary logic as Arm 6's external-CC check, additive sibling.
    high_arm6b = F.col("ext_loan_payment_amt_h2_recent").isNotNull() & (
        F.col("ext_loan_payment_amt_h2_recent") >= _emi
    )
    # Arm 3c (RL-A1-19, timing-anchored, replaces high_arm7/high_arm3b):
    # salary never present in the full 6m lookback AND a bureau new-salary
    # signal whose pull-dated leg (if that's the leg firing) is within
    # _RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS of observation_date — the fresh
    # 3-month window is independent of the base 6-month aecb_is_recent cutoff
    # (must not reuse it here, per ability_redesign_v3.md §6).
    _high_arm3c_pull_dated_leg = (
        _bureau_new_salary_signal_pull_dated
        & _pull_date.isNotNull()
        & (
            F.months_between(F.col("observation_date"), _pull_date)
            <= _RL_TAU_NEW_SALARY_PULL_RECENCY_MONTHS
        )
    )
    high_arm3c = (
        (F.coalesce(F.col("salary_months_h2_recent"), F.lit(0)) == 0)
        & (F.coalesce(F.col("salary_months_h4_h6_recent"), F.lit(0)) == 0)
        & (_bureau_new_salary_signal_alert_based | _high_arm3c_pull_dated_leg)
    )

    cond_high = (
        high_arm1
        | high_arm2
        | high_arm3
        | high_arm3c
        | high_arm4
        | high_arm6
        | high_arm6b
    )

    # ── ability_low: Conditions 1 & 3 + Tier 2 (v3 §3) ─────────────────────────
    # Tier 1 (Signal-B-dependent) is out of scope this round — see docstring.
    # RL-A1-21: Condition 1's trailing income clause (Signal D) is dropped,
    # narrowing the condition rather than replacing it (no reliable income
    # source currently exists — see module docstring). Condition 2 (RL-A1-15)
    # is removed entirely — its premise, inflow_present_h4_h6_flag, was
    # itself a bottom-up aggregation of the same rejected category.
    low_cond1 = (
        (F.col("salary_stopped_flag_recent") == 1)
        & (F.coalesce(F.col("a1_new_salary_acct_flag_recent"), F.lit(0)) != 1)
        & casa_low
    )
    low_cond3 = (F.col("eosb_like_flag") == 1) & (
        F.coalesce(F.col("eosb_post_salary_flag_recent"), F.lit(0)) != 1
    )
    # Tier 2: repeated cross-bank default is strong enough alone — no buffer
    # (casa_low) check required, unlike Tier 1.
    low_tier2 = _aecb_recent & (
        F.coalesce(F.col("aecb_bank_times_in_default_90d_recent"), F.lit(0))
        > _RL_TAU_AECB_DEFAULT_RECIDIVISM
    )

    cond_low = low_cond1 | low_cond3 | low_tier2

    # ── ability_moderate: Arms 1 & 2 (v3 §4) ───────────────────────────────────
    # Arm 4a/4b (Signal-B-dependent) are out of scope this round — see docstring.
    # RL-A1-21: Arm 3 (Signal D) removed entirely, no replacement.
    moderate_arm1 = (F.col("no_casa_flag_recent") == 1) & (
        F.col("a1_new_salary_acct_flag_recent") == 1
    )
    # Arm 2 resolves v2's "performing CC elsewhere" gap. CAVEAT:
    # bank_worst_delinquency_6m_encoded is an aggregate across ALL
    # bureau-registered trade lines, not CC-specific. "<=1" on the aggregate
    # worst necessarily implies every individual product (incl. any CC) is
    # also <=1 — that direction is sound. It does NOT work the other way: if
    # the aggregate worst is high because of a *different* (non-CC) product,
    # this arm correctly stays silent (false negative, never a false
    # positive) rather than wrongly asserting the CC itself is distressed.
    moderate_arm2 = (
        (F.col("no_casa_flag_recent") == 1)
        & _aecb_recent
        & (F.coalesce(F.col("aecb_total_active_cc_contracts_recent"), F.lit(0)) > 0)
        & (F.col("bank_worst_delinquency_6m_encoded_recent") <= 1)
    )

    cond_moderate = moderate_arm1 | moderate_arm2

    return {
        "cond_high": cond_high,
        "cond_low": cond_low,
        "cond_moderate": cond_moderate,
    }


def _apply_rl_ability_classifier(
    df: DataFrame, conds: dict, state_col: str
) -> DataFrame:
    """Apply the ability_redesign_v3.md waterfall: high -> low -> moderate -> unknown.

    Low gates before moderate (v3 §1) so a stopped-income customer isn't
    accidentally caught by a moderate arm first. ability_unknown is the
    fallthrough — v3 §5 Condition 1 (total signal absence, incl.
    aecb_is_recent == 0) is implied by this ordering: whenever AECB data is
    recent and carries signal, one of the arms above fires first, so by the
    time execution reaches here that's the only case left.
    """
    return df.withColumn(
        state_col,
        F.when(conds["cond_high"], "ability_high")
        .when(conds["cond_low"], "ability_low")
        .when(conds["cond_moderate"], "ability_moderate")
        .otherwise("ability_unknown"),
    )


def _build_rl_a1_output_select(result: DataFrame) -> DataFrame:
    """Apply typed output schema and return final crx_rl_a1_ability DataFrame.

    Schema matches crx_cc_a1_ability core columns for assembly compatibility
    (RL-G1), with _recent columns from obs-date-anchored enrichers (RL-A1-3)
    and RL-specific additions appended at the end.

    recovery_signal is dropped (RL-A1-9): it depended only on the now-removed
    _build_ability_conditions import; v3 §7.4 states this concept is removed
    entirely from the RL classifier with no replacement.
    """
    return result.select(
        F.col("account_id").cast("string"),
        F.col("observation_date").cast("date"),
        F.col("spell_id").cast("int"),
        F.col("t0").cast("date"),
        F.col("a1_state").cast("string"),
        F.col("a1_provenance").cast("string"),
        F.col("a1_confidence").cast("double"),
        F.col("eosb_like_flag").cast("int").alias("a1_eosb_signal"),
        F.col("eosb_post_salary_flag").cast("int").alias("a1_eosb_post_salary"),
        F.col("a1_income_source").cast("string"),
        # _recent columns: obs-date-anchored (RL-A1-3)
        F.col("salary_months_h2_recent").cast("int"),
        F.col("casa_eod_bal_h2_recent").cast("double"),
        F.col("recurring_inflow_cnt_h2_recent").cast("int"),
        F.col("bureau_salary_present_6m_flag_recent").cast("int"),
        F.col("salary_amt_last_recent").cast("double"),
        F.col("emi_coverage_mean_recent").cast("double"),
        # RL-A1-9 Signals A-E + Signal C EMI threshold
        F.col("salary_months_h4_h6_recent").cast("int"),
        F.col("salary_stopped_flag_recent").cast("int"),
        F.col("no_casa_flag_recent").cast("int"),
        # RL-A1-19: timing-anchor for high_arm3/high_arm3c (gates both arms).
        F.col("salary_stop_month_recent").cast("date"),
        # RL-A1-20: 12 CASA(CA+SA)/CA-only/all-accounts balance columns —
        # casa_eod_spot/avg_3m_recent (CA-only names) replaced by the full
        # ca/casa/all x spot/avg_3m x plain/_max set; casa is the live gate
        # (High Arm 1/4, casa_low), ca/all/_max are diagnostic-only.
        *[F.col(f"{c}_recent").cast("double") for c in _CASA_EOD_BAL_OUTPUT_COLS],
        F.col("monthly_emi_recent").cast("double"),
        # RL-A1-9 AECB columns (4 decided-KEEP arms only)
        F.col("aecb_bureau_pull_date_recent").cast("date"),
        F.col("aecb_is_recent").cast("int"),
        F.col("aecb_last_salary_credit_amount_recent").cast("double"),
        F.col("aecb_salary_bank_product_count_recent").cast("int"),
        F.col("aecb_income_record_changes_30d_recent").cast("int"),
        F.col("aecb_total_active_cc_contracts_recent").cast("long"),
        F.col("bank_worst_delinquency_6m_encoded_recent").cast("int"),
        F.col("aecb_bank_times_in_default_90d_recent").cast("long"),
        F.lit(datetime.date.today().isoformat()).cast("date").alias("computed_at"),
    )


# ── Node 5: build_rl_a1_classify ───────────────────────────────────────────────


def build_rl_a1_classify(
    crx_rl_a4_spine: DataFrame,
    crx_rl_departure_signature: DataFrame,
    crx_rl_spell_table: DataFrame,
    group_b_income_recent: DataFrame,
    group_b_bureau_recent: DataFrame,
    group_c_recent: DataFrame,
) -> DataFrame:
    """Assemble all signals and classify A1 income-ability state for RL (Node 5).

    a1_state uses the RL-A1-9 EMI-relative waterfall (ability_redesign_v3.md
    Sections 2-5): _build_rl_ability_conditions() + _apply_rl_ability_classifier()
    drive the ability_high/low/moderate/unknown state purely from local RL
    functions — the shared cc_a1_ability._build_ability_conditions /
    _apply_ability_classifier_primary import is no longer used (R18).

    a1_provenance: "obs_date" when ≥1 _recent income signal is non-null;
        "no_signal" when all _recent signals are null.

    eosb_post_salary_flag: operable — eosb_like_flag from crx_rl_departure_signature
    + bureau_salary_recent. Group D suspended (RL-A1-5): feat_loan_application_risk
    pull_date unknown. The former Node 1 join (eosb_like_flag, prior_spell_cnt_12m)
    is inlined here (Node 1 eliminated in RL-A1-7 cleanup) and now reads directly
    from crx_rl_departure_signature / crx_rl_spell_table — the superseded
    crx_rl_a4_class was a pure passthrough of both columns (removed; see
    rl_a4_spine pipeline for crx_rl_a4_spine's structural-only replacement).

    Args:
        crx_rl_a4_spine:            Windowed spine (account_id, observation_date,
                                    spell_id, t0).
        crx_rl_departure_signature: Obs-date-grain departure signals — provides
                                    eosb_like_flag (deduped to spell grain).
        crx_rl_spell_table:         Spell-grain T0 anchor — provides
                                    prior_spell_cnt_12m.
        group_b_income_recent: crx_rl_a1_group_b_income_recent — obs-date income.
        group_b_bureau_recent: crx_rl_a1_group_b_bureau_recent — obs-date bureau.
        group_c_recent:        crx_rl_a1_group_c_recent — obs-date EMI coverage.

    Returns:
        crx_rl_a1_ability — A1 axis for every (account_id, observation_date)
        in crx_rl_a4_spine.
    """
    result = _assemble_rl_classify_inputs(
        crx_rl_a4_spine,
        crx_rl_departure_signature,
        crx_rl_spell_table,
        group_b_income_recent,
        group_b_bureau_recent,
        group_c_recent,
    )

    # ── Primary obs-date-anchored state (a1_state) ─────────────────────────────
    # RL-A1-9 waterfall: EMI-relative base arms + 4 decided-KEEP AECB arms.
    # recovery_signal is dropped entirely (depended only on the removed
    # cc_a1_ability import; v3 §7.4 — no replacement, see RESULTS_RL.md).
    conds_rl = _build_rl_ability_conditions()
    result = _apply_rl_ability_classifier(result, conds_rl, state_col="a1_state")

    # Provenance: obs_date when ≥1 _recent income signal populated; no_signal
    # otherwise. RL-A1-21: casa_inflow_cnt_h2_recent dropped from the
    # coalesce — that column no longer exists (Signal D removal).
    result = result.withColumn(
        "a1_provenance",
        F.when(
            F.coalesce(
                F.col("salary_months_h2_recent"),
                F.col("bureau_salary_present_6m_flag_recent"),
            ).isNotNull(),
            F.lit("obs_date"),
        ).otherwise(F.lit("no_signal")),
    ).withColumn(
        "a1_confidence",
        F.when(F.col("a1_state") == "ability_high", F.lit(0.9))
        .when(F.col("a1_state") == "ability_moderate", F.lit(0.7))
        .when(F.col("a1_state") == "ability_low", F.lit(0.4))
        .otherwise(F.lit(0.0)),
    )

    # a1_income_source: obs-date-anchored _recent signals only. RL-A1-21:
    # the "casa_generic" branch (gated on casa_inflow_cnt_h2_recent, Signal D)
    # is removed with no replacement.
    result = result.withColumn(
        "a1_income_source",
        F.when(
            F.coalesce(F.col("salary_months_h2_recent"), F.lit(0))
            >= _TAU_SALARY_H2_MIN,
            F.lit("payroll"),
        )
        .when(
            F.col("bureau_salary_present_6m_flag_recent") == 1, F.lit("bureau_salary")
        )
        .when(
            F.coalesce(F.col("ext_cc_payment_cnt_h2_recent"), F.lit(0)) >= 2,
            F.lit("ext_cc_payment"),
        )
        .otherwise(F.lit(None).cast("string")),
    )

    result = _build_rl_a1_output_select(result)
    enrichers.log_a1_stats(result)
    return result
`````

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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability/pipeline.py`
action: replace · base sha256 `9a36e4af4e1d6e771ec2a26f4c003f34b7d7f16dc4f9c4913712d548e9e7ce92` · base trailing newline: yes · new sha256 `1541cb8d4424fcdfb34558d0cf99368891051d03be6ecd2fb795c1b41774ea01` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
# pylint: disable=R0801
"""Kedro pipeline: RL-A1-1/9 — A1 Ability axis for Retail Loans (4-node).

# pylint: disable=line-too-long

Four-node modular pipeline (T0 nodes removed in RL-A1-5 cleanup;
Node 4b Group D removed in RL-A1-5 cleanup — feat_loan_application_risk pull_date unknown;
Group A departure removed in RL-A1-6 cleanup; Node 1 base join eliminated in
RL-A1-7 cleanup — crx_rl_a4_spine feeds enrichment nodes directly).
cif_id is carried directly in crx_rl_a4_spine — no separate CIF bridge node needed.

Architecture:
    build_rl_a1_group_b_income_recent → crx_rl_a1_group_b_income_recent  [Node 2r] ┐ parallel (obs-date)
    build_rl_a1_group_b_bureau_recent → crx_rl_a1_group_b_bureau_recent  [Node 3r] ┤
    build_rl_a1_group_c_recent        → crx_rl_a1_group_c_recent         [Node 4r] ┘
    build_rl_a1_classify              → crx_rl_a1_ability                [Node 5]  ← shipped axis

Node 5 inputs: crx_rl_a4_spine, crx_rl_departure_signature, crx_rl_spell_table,
    crx_rl_a1_group_b_income_recent, crx_rl_a1_group_b_bureau_recent,
    crx_rl_a1_group_c_recent.
    The eosb_like_flag / prior_spell_cnt_12m lookup (formerly from the superseded
    crx_rl_a4_class) is inlined in build_rl_a1_classify, read directly from
    crx_rl_departure_signature / crx_rl_spell_table.

Node 2r (RL-A1-23) also takes wm_fea_external_loan_payments — a weekly
PIT-joinable WM feature table (no R2 look-ahead flag) feeding High Arm 6b
(ext_loan_payment_amt_h2_recent), additive sibling to the existing Arm 6.

Run with:
    kedro run --pipeline=crx_rl_a1_ability
"""

from kedro.pipeline import Pipeline, node

from .nodes import (
    build_rl_a1_classify,
    build_rl_a1_group_b_bureau_recent,
    build_rl_a1_group_b_income_recent,
    build_rl_a1_group_c_recent,
)

_TAGS = ["crx", "a1", "ability", "persona_axis", "crx_persona"]


def create_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """Return the 4-node RL A1 Ability pipeline."""
    return Pipeline(
        [
            # ── Node 2r: obs-date-anchored income signals ─────────────────
            node(
                func=build_rl_a1_group_b_income_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "feat_payroll_indicator",
                    "feat_casa_eod_balance",
                    "wm_fea_salary_days_since_increment",
                    "wm_pri_labelled_transactions",
                    "raw_beneficiary_cards",
                    "wm_fea_casa_eod_avg_balance",
                    "wm_fea_external_loan_payments",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_b_income_recent",
                name="build_rl_a1_group_b_income_recent",
                tags=_TAGS,
            ),
            # ── Node 3r: obs-date-anchored bureau + recurring signals ─────
            node(
                func=build_rl_a1_group_b_bureau_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "wm_fea_casa_weekly_repeated_inflow",
                    "stg_aecb_salary_history",
                    "prm_bureau_alert_enriched",
                    "prm_bureau_cif_bridge",
                    "fea_monthly_aecb_alerts",
                    "feature_retail_loans",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_b_bureau_recent",
                name="build_rl_a1_group_b_bureau_recent",
                tags=_TAGS,
            ),
            # ── Node 4r: obs-date-anchored EMI coverage window ────────────
            node(
                func=build_rl_a1_group_c_recent,
                inputs=[
                    "crx_rl_a4_spine",
                    "int_loan_master",
                    "params:crx_persona",
                ],
                outputs="crx_rl_a1_group_c_recent",
                name="build_rl_a1_group_c_recent",
                tags=_TAGS,
            ),
            # ── Node 5: assemble + classify → shipped persona axis ────────
            node(
                func=build_rl_a1_classify,
                inputs=[
                    "crx_rl_a4_spine",
                    "crx_rl_departure_signature",
                    "crx_rl_spell_table",
                    "crx_rl_a1_group_b_income_recent",
                    "crx_rl_a1_group_b_bureau_recent",
                    "crx_rl_a1_group_c_recent",
                ],
                outputs="crx_rl_a1_ability",
                name="build_rl_a1_classify",
                tags=_TAGS,
            ),
        ],
        tags=["crx_persona"],
    )
`````

New:

`````python
"""Kedro pipeline: RL A1 ability axis on the shared ``a1_ability`` engine; the anchor is
one EMI (``nodes.py``) and the loan's latest bureau pull adds a salary source.

Needs, for the model_id (rl_60_180 / rl_180_plus): ``crx_rl_obs_base``,
``casa_primary``, ``casa_features``, ``bureau_salary_bounces`` and ``location_features``.

    kedro run --pipeline=crx_rl_a1_ability

TEMPORARY (mirror bundle 08): ``create_b08_check_pipeline`` — see
``a1_ability/pipeline.py``.
"""

from kedro.pipeline import Pipeline, node

from ..a1_ability.pipeline import TAGS, create_a1_pipeline
from ..a1_ability.pipeline import create_b08_check_pipeline as _b08_check
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


def create_b08_check_pipeline(**kwargs) -> Pipeline:  # pylint: disable=unused-argument
    """TEMPORARY: the RL A1 check (bundle 08)."""
    return _b08_check("rl", _ANCHOR)
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability/enrichers.py`
action: delete · base sha256 `2fccbdbb1bd0865b98c5e596eccb54e315c7661ab6966cb3777da3fbe787919e` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""T26 — A1 Ability enrichment helpers.

Helper functions for building A1 ability signals:
  - _enrich_salary_months_h2: payroll_indicator → salary_months_h2
  - _enrich_casa_eod_bal_h2: casa_eod_balance → casa_eod_bal_h2
  - _enrich_salary_pit: salary_days_since_increment → salary signals
  - _enrich_recurring_inflow_h2: casa_weekly_repeated_inflow → recurring signals
  - _enrich_payment_trajectory: T04b → payment trajectory
  - _enrich_utilisation: T05 → utilisation
  - _enrich_prm_balance: prm_balance → cc_total_outstanding
  - enrich_salary_stop_month: payroll_indicator → salary_stop_month
    (RL-A1-19 — timing-anchored salary arm high_arm3)
  - enrich_ext_loan_payments_h2: wm_fea_external_loan_payments →
    ext_loan_payment_amt_h2, ext_loan_payment_cnt_h2 (RL-A1-23 — High Arm 6b)

All functions return None (with warning) if required columns are absent.
"""

# pylint: disable=too-many-lines

import logging
from typing import NamedTuple, Optional, Sequence

from pyspark.sql import DataFrame, Window
from pyspark.sql import functions as F

LOG = logging.getLogger(__name__)


class RequiredJoin(NamedTuple):
    """One declared enrichment signal: a label (for the error message) and
    the already-computed signal DataFrame (None if the enricher's required
    source columns were absent)."""

    label: str
    signal_df: Optional[DataFrame]


def join_required_signals(
    base: DataFrame, grain_key: tuple, joins: Sequence[RequiredJoin]
) -> DataFrame:
    """Left-join every declared signal onto base.

    Raises RuntimeError if any enricher returned None instead of
    null-stubbing it — upstream schema drift is a defect to surface at
    build time, not degrade through silently.
    """
    result = base
    for rj in joins:
        if rj.signal_df is None:
            raise RuntimeError(
                f"{rj.label}: enricher returned None — required source "
                "columns are missing. Fix the source or the enricher; do "
                "not silently null the signal."
            )
        result = result.join(rj.signal_df, on=list(grain_key), how="left")
    return result


# ── CASA EOD balance column name in feat_casa_eod_balance ─────────────────────
# 3-month rolling avg relative to record date: covers ≈ [T0-3m, T0) at PIT.
_CASA_BAL_COL = "ft_avg_eod_balance_in_last_0_2_months_avg"


def enrich_salary_months_h2(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Count H2 months with payroll_flag=1 from feat_payroll_indicator.

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_months_h2).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
            "enrich_salary_months_h2: feat_payroll_indicator missing 'payroll_flag'"
            " — salary_months_h2 will be NULL for all rows"
        )
        return None

    fp_dated = feat_payroll.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_month_date", "payroll_flag")

    h2_salary = (
        cif_base.join(fp_dated, on="cif_id", how="inner")
        .filter(
            (
                F.col("_month_date")
                >= F.add_months(F.trunc(F.col(anchor_col), "month"), -3)
            )
            & (F.col("_month_date") < F.trunc(F.col(anchor_col), "month"))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col("payroll_flag") == 1, 1).otherwise(0))
            .cast("int")
            .alias("salary_months_h2")
        )
    )

    return h2_salary


def enrich_salary_months_h4_h6(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Count H4-H6 months with payroll_flag=1 from feat_payroll_indicator.

    Window shifted 3 months earlier than enrich_salary_months_h2's H2 window:
    [anchor-6m, anchor-3m) instead of [anchor-3m, anchor). Used (RL-A1-9) to
    detect whether payroll was present before the most recent 3-month window,
    feeding the salary_stopped_flag_recent derivation.

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_months_h4_h6).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
            "enrich_salary_months_h4_h6: feat_payroll_indicator missing 'payroll_flag'"
            " — salary_months_h4_h6 will be NULL for all rows"
        )
        return None

    fp_dated = feat_payroll.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_month_date", "payroll_flag")

    h4_h6_salary = (
        cif_base.join(fp_dated, on="cif_id", how="inner")
        .filter(
            (
                F.col("_month_date")
                >= F.add_months(F.trunc(F.col(anchor_col), "month"), -6)
            )
            & (
                F.col("_month_date")
                < F.add_months(F.trunc(F.col(anchor_col), "month"), -3)
            )
        )
        .groupBy(*grain_key)
        .agg(
            F.sum(F.when(F.col("payroll_flag") == 1, 1).otherwise(0))
            .cast("int")
            .alias("salary_months_h4_h6")
        )
    )

    return h4_h6_salary


def enrich_salary_stop_month(
    cif_base: DataFrame,
    feat_payroll: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Latest H4-H6 month with payroll_flag=1 from feat_payroll_indicator (RL-A1-19).

    Same window as enrich_salary_months_h4_h6 ([anchor-6m, anchor-3m)), but
    returns the latest calendar month payroll was present instead of a count —
    the timing-anchored high_arm3 (RL-A1-19) compares this against the bureau
    pull date, not just a presence count. Rows with no payroll_flag=1 month in
    the window get NULL (there is no "stop month" to report, not 0).

    Returns None (with warning) if payroll_flag column is absent.
    Returns DataFrame with (grain_key..., salary_stop_month).
    """
    if "payroll_flag" not in feat_payroll.columns:
        LOG.warning(
            "enrich_salary_stop_month: feat_payroll_indicator missing 'payroll_flag'"
            " — salary_stop_month will be NULL for all rows"
        )
        return None

    fp_dated = feat_payroll.withColumn(
        "_month_date", F.to_date(F.col("month_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_month_date", "payroll_flag")

    stop_month = (
        cif_base.join(fp_dated, on="cif_id", how="inner")
        .filter(
            (
                F.col("_month_date")
                >= F.add_months(F.trunc(F.col(anchor_col), "month"), -6)
            )
            & (
                F.col("_month_date")
                < F.add_months(F.trunc(F.col(anchor_col), "month"), -3)
            )
            & (F.col("payroll_flag") == 1)
        )
        .groupBy(*grain_key)
        .agg(F.max("_month_date").alias("salary_stop_month"))
    )

    return stop_month


# ── CASA EOD avg balance column names (wm_fea_casa_eod_avg_balance, WM) ───────
# RL-A1-20: 3 balance-scope prefixes — ca (current-account-only, diagnostic),
# casa (CA+SA, the primary balance-vs-EMI gate), all (CASA+investments+FDs,
# diagnostic) — at 2 windows (spot ~0-3wk, avg_3m ~0-11wk), each with a plain
# avg and a _max aggregation. ca columns were RL-A1-8/9's confirmed real
# names; casa/all columns confirmed real in the same PROD schema capture
# (RESULTS_RL.md 2026-10-06, TRL_A1_8 check1_schema_guard.actual_columns).
_CASA_EOD_BAL_SOURCE_COLS = {
    "ca": {
        "spot": "ft_avg_ca_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_ca_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_ca_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_ca_eod_balance_in_last_0_11_weeks_max",
    },
    "casa": {
        "spot": "ft_avg_casa_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_casa_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_casa_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_casa_eod_balance_in_last_0_11_weeks_max",
    },
    "all": {
        "spot": "ft_avg_eod_balance_in_last_0_3_weeks_avg",
        "spot_max": "ft_avg_eod_balance_in_last_0_3_weeks_max",
        "avg_3m": "ft_avg_eod_balance_in_last_0_11_weeks_avg",
        "avg_3m_max": "ft_avg_eod_balance_in_last_0_11_weeks_max",
    },
}


def enrich_casa_eod_avg_balance(
    cif_base: DataFrame,
    wm_casa_avg_bal: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT CASA EOD avg balance — 3 scope prefixes x 2 windows x 2 aggs — from
    wm_fea_casa_eod_avg_balance (WM).

    RL-A1-20: casa (CA+SA) is the primary balance-vs-EMI gate; ca (current-
    account-only) and all (CASA+investments+FDs) are passthrough/diagnostic
    only (never wired into a gate). casa ⊇ ca by construction — a
    savings-only customer with no current account still shows a non-null
    casa figure even when their ca figure is null. _max variants are
    diagnostic-only (never wired into a gate).

    PIT join: filters wm_casa_avg_bal to week_date <= anchor_col per row, then
    window-dedups to the freshest week_number per grain_key (same row_number
    pattern as enrich_salary_pit / enrich_casa_inflow_h2's PIT joins).

    week_number, not adv_load_date, is the real per-row time dimension
    (RL-A1-14/RL-A1-9 Leg B, confirmed in PROD 2026-10-05): a direct column
    probe showed adv_load_date is a load-time constant (single value across
    all sampled rows, e.g. 2026-06-02), while week_number varies per row from
    2022-01 onward — the catalog entry being unpinned on adv_load_date made
    adv_load_date a genuine loaded column, but not a genuine per-row date.
    This mirrors the sibling table wm_fea_casa_cc_inflow_outflow
    (enrich_casa_inflow_h2), which already keys off week_number correctly.
    week_number parses the same way: F.to_date(..., "yyyyMMdd").

    Each avg_3m / avg_3m_max output coalesces the 3m-window column to its
    same-prefix spot column (2-level coalesce only — the 6m candidate column
    has no corroborated name, see RESULTS_RL.md 2026-10-02).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., casa_eod_spot_ca, casa_eod_spot_ca_max,
    casa_eod_avg_3m_ca, casa_eod_avg_3m_ca_max, casa_eod_spot_casa,
    casa_eod_spot_casa_max, casa_eod_avg_3m_casa, casa_eod_avg_3m_casa_max,
    casa_eod_spot_all, casa_eod_spot_all_max, casa_eod_avg_3m_all,
    casa_eod_avg_3m_all_max).
    """
    _required = ["week_number"] + [
        c for grp in _CASA_EOD_BAL_SOURCE_COLS.values() for c in grp.values()
    ]
    missing = [c for c in _required if c not in wm_casa_avg_bal.columns]
    if missing:
        LOG.warning(
            "enrich_casa_eod_avg_balance: wm_fea_casa_eod_avg_balance missing %s"
            " — all casa_eod_* columns will be NULL",
            missing,
        )
        return None

    _src_select = [
        F.col(col).cast("double").alias(f"_{prefix}_{window}")
        for prefix, cols in _CASA_EOD_BAL_SOURCE_COLS.items()
        for window, col in cols.items()
    ]
    bal_dated = wm_casa_avg_bal.select(
        "cif_id",
        F.to_date(F.col("week_number").cast("string"), "yyyyMMdd").alias("_snap_date"),
        *_src_select,
    )

    joined = cif_base.join(bal_dated, on="cif_id", how="inner").filter(
        F.col("_snap_date") <= F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_snap_date").desc())
    _out_select = [*grain_key]
    for prefix in _CASA_EOD_BAL_SOURCE_COLS:
        _out_select.append(F.col(f"_{prefix}_spot").alias(f"casa_eod_spot_{prefix}"))
        _out_select.append(
            F.col(f"_{prefix}_spot_max").alias(f"casa_eod_spot_{prefix}_max")
        )
        _out_select.append(
            F.coalesce(F.col(f"_{prefix}_avg_3m"), F.col(f"_{prefix}_spot")).alias(
                f"casa_eod_avg_3m_{prefix}"
            )
        )
        _out_select.append(
            F.coalesce(
                F.col(f"_{prefix}_avg_3m_max"), F.col(f"_{prefix}_spot_max")
            ).alias(f"casa_eod_avg_3m_{prefix}_max")
        )

    pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(*_out_select)
    )

    return pit


def enrich_casa_eod_bal_h2(
    cif_base: DataFrame,
    feat_casa_bal: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT CASA EOD balance from feat_casa_eod_balance (retail.feature_space).

    PIT approach: latest record with month_end_date < T0, per row — the catalog
    entry (feat_casa_eod_balance) is pinned to one adv_load_date snapshot, so
    `adv_load_date` is not a column in this DataFrame at all; the real per-record
    PIT date is `month_end_date`, which is used directly below.
    Balance column: ft_avg_eod_balance_in_last_0_2_months_avg
        — 3-month rolling average relative to the record date, covering
          months 0, 1, 2 back from that date ≈ [T0-3m, T0) at PIT.

    ⚠ IMPORTANT — previous bugs fixed here:
        1. Date column was 'month_number' (yyyyMMdd int) — WRONG.
           Correct column is 'month_end_date' (YYYY-MM-dd string), cast directly.
        2. Balance column was 'avg_casa_eod_balance' — WRONG (not in schema).
           Correct column is 'ft_avg_eod_balance_in_last_0_2_months_avg'.
        3. Filtering/selecting on 'adv_load_date' — WRONG. The catalog entry is
           pinned (`.../adv_load_date=${globals:snapshot_adv_load_date}`), so Spark
           reads directly from that leaf partition and the column does not exist
           in the schema — raises UNRESOLVED_COLUMN, not a silent no-op.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, casa_eod_bal_h2).
    """
    for col in ("month_end_date", _CASA_BAL_COL):
        if col not in feat_casa_bal.columns:
            LOG.warning(
                "enrich_casa_eod_bal_h2: feat_casa_eod_balance missing '%s'"
                " — casa_eod_bal_h2 will be NULL",
                col,
            )
            return None

    cb_dated = feat_casa_bal.withColumn(
        "_month_date", F.col("month_end_date").cast("date")
    ).select("cif_id", "_month_date", _CASA_BAL_COL)

    joined = cif_base.join(cb_dated, on="cif_id", how="inner").filter(
        F.col("_month_date") < F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    casa_pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col(_CASA_BAL_COL).cast("double").alias("casa_eod_bal_h2"),
        )
    )

    return casa_pit


def enrich_salary_pit(
    cif_base: DataFrame,
    wm_salary: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT salary signals from wm_fea_salary_days_since_increment.

    PIT = last week_number strictly before T0, per row — the catalog entry is
    pinned to one adv_load_date snapshot, so `adv_load_date` is not a column in
    this DataFrame at all; the real per-record PIT date is `week_number`, used
    directly below.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, salary_amt_last, salary_change_pct).
    """
    _required = [
        "ft_last_salary_amount",
        "ft_percent_monthly_salary_change",
    ]
    missing = [c for c in _required if c not in wm_salary.columns]
    if missing:
        LOG.warning(
            "enrich_salary_pit: wm_fea_salary_days_since_increment missing %s"
            " — salary PIT signals will be NULL",
            missing,
        )
        return None

    ws_dated = wm_salary.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", *_required)

    joined = cif_base.join(ws_dated, on="cif_id", how="inner").filter(
        F.col("_week_date") < F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_week_date").desc())
    sal_pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col("ft_last_salary_amount").cast("double").alias("salary_amt_last"),
            F.col("ft_percent_monthly_salary_change")
            .cast("double")
            .alias("salary_change_pct"),
        )
    )

    return sal_pit


def enrich_recurring_inflow_h2(
    cif_base: DataFrame,
    wm_recurring: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 recurring non-salary CASA inflow from wm_fea_casa_weekly_repeated_inflow.

    H2 = weeks with week_date in [T0 - 90 days, T0).

    Source schema: (cif_id, week_number, ft_repeated_inflow).
    get_continuous_weekly_fill_from_month renames repeated_inflow_month_amt →
    ft_repeated_inflow and drops repeated_inflow_month_count (not forwarded).
    recurring_inflow_cnt_h2 is derived as count of H2 weeks with ft_repeated_inflow > 0.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, recurring_inflow_amt_h2,
                            recurring_inflow_cnt_h2).
    """
    _required = ["ft_repeated_inflow"]
    missing = [c for c in _required if c not in wm_recurring.columns]
    if missing:
        LOG.warning(
            "enrich_recurring_inflow_h2: wm_fea_casa_weekly_repeated_inflow"
            " missing %s — recurring inflow signals will be NULL",
            missing,
        )
        return None

    wr_dated = wm_recurring.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", "ft_repeated_inflow")

    rec_h2 = (
        cif_base.join(wr_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("ft_repeated_inflow").cast("double").alias("recurring_inflow_amt_h2"),
            F.sum(F.when(F.col("ft_repeated_inflow") > 0, F.lit(1)).otherwise(F.lit(0)))
            .cast("int")
            .alias("recurring_inflow_cnt_h2"),
        )
    )

    return rec_h2


def enrich_casa_inflow_h2(
    cif_base: DataFrame,
    wm_casa_inflow: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 generic CASA inflow from wm_fea_casa_cc_inflow_outflow.

    H2 = weeks with week_date in [T0 - 90 days, T0).

    Captures ALL CASA credit types — salary, family transfers, rental,
    business payments — broader than payroll_present_h2 (ENBD payroll only)
    and recurring_inflow_cnt_h2 (same-counterparty recurring only).

    Source schema: (cif_id, week_number, ft_inflow_casa_amt_in_last_0_0_weeks_sum, ...).
    ft_inflow_casa_amt_in_last_0_0_weeks_sum is the 0:0 window (spot week amount).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, casa_inflow_amt_h2,
                            casa_inflow_cnt_h2).
    """
    _required = ["ft_inflow_casa_amt_in_last_0_0_weeks_sum"]
    missing = [c for c in _required if c not in wm_casa_inflow.columns]
    if missing:
        LOG.warning(
            "enrich_casa_inflow_h2: wm_fea_casa_cc_inflow_outflow"
            " missing %s — generic CASA inflow signals will be NULL",
            missing,
        )
        return None

    ci_dated = wm_casa_inflow.withColumn(
        "_week_date", F.to_date(F.col("week_number").cast("string"), "yyyyMMdd")
    ).select("cif_id", "_week_date", "ft_inflow_casa_amt_in_last_0_0_weeks_sum")

    inflow_h2 = (
        cif_base.join(ci_dated, on="cif_id", how="inner")
        .filter(
            (F.col("_week_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_week_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("ft_inflow_casa_amt_in_last_0_0_weeks_sum")
            .cast("double")
            .alias("casa_inflow_amt_h2"),
            F.sum(
                F.when(
                    F.col("ft_inflow_casa_amt_in_last_0_0_weeks_sum") > 0, F.lit(1)
                ).otherwise(F.lit(0))
            )
            .cast("int")
            .alias("casa_inflow_cnt_h2"),
        )
    )

    return inflow_h2


def enrich_ext_cc_payments_h2(
    cif_base: DataFrame,
    wm_labelled_transactions: DataFrame,
    beneficiary_cards: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """H2 CASA payments to external credit cards from WM primary + BENEFICIARY table.

    H2 = transactions with tran_date in [anchor - 90 days, anchor).

    Source: pri_labelled_transactions_indicators_by_week (WM primary layer) joined
    to AI_TDV_OMB_UAE_EBI.BENEFICIARY on transaction_acid == instrument_number.
    Only CARD_NUMBER instrument types (external CC numbers registered by customers)
    are matched — this captures genuine CC obligation servicing at other banks,
    not generic self-transfers.

    ⚠ [CONFIRM] beneficiary_cards is a live snapshot (edp_activeind='Y'); no
    historical partitioning means mild look-ahead bias if beneficiaries changed
    after T0.  Acceptable for v1 — refine at Leg B if coverage data warrants.

    Required columns:
        wm_labelled_transactions: cif_id, in_out_flow, product_category,
                                  tran_date, tran_amt, transaction_acid
        beneficiary_cards:        instrument_number, instrument_type

    Returns DataFrame(account_id, spell_id, ext_cc_payment_amt_h2,
                      ext_cc_payment_cnt_h2) or None if required columns absent.
    """
    _required_txn = [
        "cif_id",
        "in_out_flow",
        "product_category",
        "tran_date",
        "tran_amt",
        "transaction_acid",
    ]
    _required_bene = ["instrument_number", "instrument_type"]

    missing_txn = [
        c for c in _required_txn if c not in wm_labelled_transactions.columns
    ]
    if missing_txn:
        LOG.warning(
            "enrich_ext_cc_payments_h2: wm_pri_labelled_transactions missing %s"
            " — ext_cc_payment signals will be NULL",
            missing_txn,
        )
        return None

    missing_bene = [c for c in _required_bene if c not in beneficiary_cards.columns]
    if missing_bene:
        LOG.warning(
            "enrich_ext_cc_payments_h2: raw_beneficiary_cards missing %s"
            " — ext_cc_payment signals will be NULL",
            missing_bene,
        )
        return None

    # Distinct set of external CC numbers (may already be filtered to CARD_NUMBER
    # via catalog query, but guard here in case catalog query is broadened later)
    cc_numbers = (
        beneficiary_cards.filter(F.col("instrument_type") == "CARD_NUMBER")
        .select(F.col("instrument_number").alias("_cc_number"))
        .distinct()
    )

    # CASA outflow transactions at transaction grain
    casa_outflow = wm_labelled_transactions.filter(
        (F.col("in_out_flow") == "outflow") & (F.col("product_category") == "CASA")
    ).select(
        F.col("cif_id").cast("string"),
        F.col("tran_date").cast("date").alias("_tran_date"),
        F.col("tran_amt").cast("double"),
        F.col("transaction_acid"),
    )

    # Keep only transactions where the destination matches a registered external CC
    cc_payments = casa_outflow.join(
        cc_numbers,
        on=casa_outflow["transaction_acid"] == cc_numbers["_cc_number"],
        how="inner",
    ).drop("_cc_number")

    # Bridge to spell grain via cif_base and apply H2 window
    result = (
        cif_base.join(cc_payments, on="cif_id", how="inner")
        .filter(
            (F.col("_tran_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_tran_date") < F.col(anchor_col))
        )
        .groupBy(*grain_key)
        .agg(
            F.sum("tran_amt").cast("double").alias("ext_cc_payment_amt_h2"),
            # Count distinct ISO weeks with ≥1 payment (consistent with H2 cnt signals)
            F.countDistinct(F.date_format(F.col("_tran_date"), "yyyyww"))
            .cast("int")
            .alias("ext_cc_payment_cnt_h2"),
        )
    )

    return result


# ── External loan payments column names (wm_fea_external_loan_payments, WM) ──
# Weekly PIT-joinable series (week_number is the real per-row date, same
# confirmed pattern as the sibling wm_fea_casa_eod_avg_balance — see
# docs/context/reference/sibling_repo_partitions.md). No R2 look-ahead flag
# (unlike RL-A1-22's single-pinned-snapshot income dataset).
_EXT_LOAN_AMT_COL = "ft_external_loan_payment_amt_in_last_0_3_weeks_sum"
_EXT_LOAN_CNT_COL = "ft_external_loan_payment_cnt_in_last_0_3_weeks_sum"


def enrich_ext_loan_payments_h2(
    cif_base: DataFrame,
    wm_ext_loan_payments: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT external-bank loan payment amount/count from wm_fea_external_loan_payments.

    RL-A1-23 (High Arm 6b): "servicing another bank's loan from this CASA
    account" is the same evidentiary logic as the existing high_arm6
    ("servicing another bank's credit card") — this enricher mirrors
    enrich_ext_cc_payments_h2's output shape (amt + cnt pair), but the join
    mechanics mirror enrich_casa_eod_avg_balance's PIT pattern instead: the
    source table is already a pre-aggregated weekly trailing-window feature
    (0:3-week sum), not raw transactions, so there is no H2-window
    aggregation to do here — just a PIT pick of the freshest weekly snapshot.

    PIT join: filters wm_ext_loan_payments to week_date <= anchor_col per row,
    then window-dedups to the freshest week_number per grain_key (same
    row_number pattern as enrich_casa_eod_avg_balance).

    week_number, not adv_load_date, is the real per-row time dimension —
    confirmed PROD precedent for this table (RL-A1-23 Leg B,
    trl_a1_23_ext_loan_payment_probe.py chk1), same confirmed pattern as the
    sibling wm_fea_casa_eod_avg_balance.

    Required columns: cif_id, week_number, ft_external_loan_payment_amt_in_
        last_0_3_weeks_sum, ft_external_loan_payment_cnt_in_last_0_3_weeks_sum.

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., ext_loan_payment_amt_h2,
    ext_loan_payment_cnt_h2).
    """
    _required = ["cif_id", "week_number", _EXT_LOAN_AMT_COL, _EXT_LOAN_CNT_COL]
    missing = [c for c in _required if c not in wm_ext_loan_payments.columns]
    if missing:
        LOG.warning(
            "enrich_ext_loan_payments_h2: wm_fea_external_loan_payments missing %s"
            " — ext_loan_payment_amt_h2/cnt_h2 will be NULL",
            missing,
        )
        return None

    ext_dated = wm_ext_loan_payments.select(
        "cif_id",
        F.to_date(F.col("week_number").cast("string"), "yyyyMMdd").alias("_snap_date"),
        F.col(_EXT_LOAN_AMT_COL).cast("double").alias("_amt_sum"),
        F.col(_EXT_LOAN_CNT_COL).cast("double").alias("_cnt_sum"),
    )

    joined = cif_base.join(ext_dated, on="cif_id", how="inner").filter(
        F.col("_snap_date") <= F.col(anchor_col)
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_snap_date").desc())
    pit = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.col("_amt_sum").alias("ext_loan_payment_amt_h2"),
            F.col("_cnt_sum").alias("ext_loan_payment_cnt_h2"),
        )
    )

    return pit


def enrich_payment_trajectory(
    base: DataFrame,
    payment_traj: DataFrame,
) -> DataFrame | None:
    """Join T04b payment trajectory features at (account_id, spell_id) grain.

    No CIF bridge required — T04b is already at spell grain.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, pay_ratio_slope,
                            pay_ratio_mean_h1, pay_ratio_mean_h2).
    """
    _required = ["pay_ratio_slope", "pay_ratio_mean_h1", "pay_ratio_mean_h2"]
    missing = [c for c in _required if c not in payment_traj.columns]
    if missing:
        LOG.warning(
            "enrich_payment_trajectory: crx_cc_payment_trajectory missing %s"
            " — trajectory signals will be NULL",
            missing,
        )
        return None

    result = (
        base.select("account_id", "spell_id")
        .join(
            payment_traj.select("account_id", "spell_id", *_required),
            on=["account_id", "spell_id"],
            how="inner",
        )
        .select(
            "account_id",
            "spell_id",
            F.col("pay_ratio_slope").cast("double"),
            F.col("pay_ratio_mean_h1").cast("double"),
            F.col("pay_ratio_mean_h2").cast("double"),
        )
    )

    return result


def enrich_utilisation(
    base: DataFrame,
    util_features: DataFrame,
) -> DataFrame | None:
    """Join T05 utilisation features at (account_id, spell_id) grain.

    No CIF bridge required — T05 is already at spell grain.
    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (account_id, spell_id, util_t0, util_slope,
                            spend_cliff_flag).
    """
    _required = ["util_t0", "util_slope", "spend_cliff_flag"]
    missing = [c for c in _required if c not in util_features.columns]
    if missing:
        LOG.warning(
            "enrich_utilisation: crx_cc_utilisation_features missing %s"
            " — utilisation signals will be NULL",
            missing,
        )
        return None

    result = (
        base.select("account_id", "spell_id")
        .join(
            util_features.select("account_id", "spell_id", *_required),
            on=["account_id", "spell_id"],
            how="inner",
        )
        .select(
            "account_id",
            "spell_id",
            F.col("util_t0").cast("double"),
            F.col("util_slope").cast("double"),
            F.col("spend_cliff_flag").cast("int"),
        )
    )

    return result


def enrich_prm_balance(
    base: DataFrame,
    prm_balance: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """PIT join prm_balance for cc_total_outstanding at T0 or observation_date.

    anchor_col controls the PIT cutoff column from base:
      - "t0" (default): latest balance ≤ T0 per (account_id, spell_id)
        → output column named cc_total_outstanding
      - "observation_date": latest balance ≤ observation_date per grain_key
        → output column named cc_total_outstanding_recent

    account_id == contract_id in the CC domain (confirmed by CIF bridge pattern).
    total_outstanding = full current + overdue CC balance at anchor point.

    Note: prm_balance renames banking_date → observation_date in the primary layer
    (_BALANCE_RENAMES in prm_cc.py).

    Returns None (with warning) if required columns are absent.
    Returns DataFrame with (grain_key..., cc_total_outstanding[_recent]).
    """
    _required = ["contract_id", "observation_date", "total_outstanding"]
    missing = [c for c in _required if c not in prm_balance.columns]
    if missing:
        LOG.warning(
            "enrich_prm_balance: prm_balance missing %s"
            " — cc_total_outstanding will be NULL",
            missing,
        )
        return None

    out_col = (
        "cc_total_outstanding" if anchor_col == "t0" else "cc_total_outstanding_recent"
    )
    _grain_cols = list(grain_key)

    # Alias balance observation_date to avoid collision with base.observation_date
    bal = prm_balance.select(
        F.col("contract_id"),
        F.col("observation_date").cast("date").alias("_bal_obs_date"),
        F.col("total_outstanding").cast("double"),
    )

    # Select grain cols + anchor aliased to _anchor to handle name collisions
    if anchor_col in _grain_cols:
        # anchor is already a grain key column (e.g. observation_date); copy it
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
    result = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *_grain_cols,
            F.col("total_outstanding").alias(out_col),
        )
    )

    return result


# ── Bureau salary column names (stg_aecb_salary_history) ─────────────────────
# Source: ai_dpl_uae_operations.sa_ops_aecb_sub_sal_cr_hist (110M rows)
# Grain: subj_salcr_hist_hdr_file_id × subj_salcr_hist_ref_mnth × EDP_LOAD_DATE
# No direct cif_id — requires prm_bureau_cif_bridge (bureau_file_id → cif_id).
_AECB_SAL_FILE_COL = "subj_salcr_hist_hdr_file_id"  # bureau file UUID (join key)
_AECB_SAL_DATE_COL = "subj_salcr_hist_ref_mnth"  # reference month of salary credit
_AECB_SAL_AMT_COL = "subj_salcr_hist_tot_sal_amt"  # total salary amount credited

# ── Bureau alert column names (prm_bureau_alert_enriched) ────────────────────
# Source: stg_aecb_alert → prm_bureau_alert_enriched (primary layer renames applied)
# EXTRACT_DT renamed to extract_date; ALERT_DESC normalized to alert_type_flag.
_BUREAU_ALERT_CIF_COL = "cif_id"  # PRVDR_SUBJ_NUM cast to long in primary layer
_BUREAU_ALERT_DATE_COL = "extract_date"  # renamed from EXTRACT_DT in _ALERT_RENAMES
_BUREAU_ALERT_TYPE_COL = "alert_type_flag"  # lower(trim(no-spaces(ALERT_DESC)))

# ── Bureau alert type filter values ──────────────────────────────────────────
# alert_type_flag = lower(trim(regexp_replace(ALERT_DESC, r"\s+", "")))
# e.g. "Salary Account Added" → "salaryaccountadded"
# Confirmed from T26a EDA (2026-09-17) on prm_bureau_alert_enriched.
_ALERT_NEW_SALARY_ACCT = "salaryaccountadded"  # confirmed: 32,780 rows

# Off-us paying: no single value exists.  The signal is the "positive alerts"
# family — any alert where a competitor facility recovered from delinquency
# (e.g. "positivealerts30dpdtoactive-creditcards").  Matched via startswith
# prefix rather than equality; covers all DPD bands and product types.
_ALERT_OFFUS_PAYING_PREFIX = "positivealerts"  # confirmed from T26a EDA


def enrich_bureau_salary(  # pylint: disable=too-many-locals
    cif_base: DataFrame,
    stg_salary_hist: DataFrame,
    prm_bureau_cif_bridge: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Bureau salary history from stg_aecb_salary_history (bureau-file-grain).

    stg_aecb_salary_history has no direct cif_id — it is keyed on bureau file
    UUIDs.  prm_bureau_cif_bridge maps subj_salcr_hist_hdr_file_id → cif_id.

    Window: [T0 - 6 months, T0) — covers H1 and H2.
    Derives:
        bureau_salary_present_6m_flag  int 0/1  — any salary credit in window
        bureau_salary_amt_last         double   — most recent salary credit amount

    ⚠ eosb_post_salary_flag is derived in build_a1_classify (not here) because
      it requires eosb_like_flag from Group A, which is unavailable here.

    ⚠ [LEG B] T0 anchor used for v1.  Upgrade to scoring-month reference after
      observation_date is available in spell table.

    Schema guard: required columns absent → returns None (warning logged).
    Required columns:
        stg_aecb_salary_history: _AECB_SAL_FILE_COL, _AECB_SAL_DATE_COL,
                                 _AECB_SAL_AMT_COL
        prm_bureau_cif_bridge:   bureau_file_id, cif_id

    Returns DataFrame with (account_id, spell_id, bureau_salary_present_6m_flag,
                           bureau_salary_amt_last) or None.
    """
    _required_sal = [_AECB_SAL_FILE_COL, _AECB_SAL_DATE_COL, _AECB_SAL_AMT_COL]
    missing_sal = [c for c in _required_sal if c not in stg_salary_hist.columns]
    if missing_sal:
        LOG.warning(
            "enrich_bureau_salary: stg_aecb_salary_history missing %s"
            " — bureau salary signals will be NULL",
            missing_sal,
        )
        return None

    _required_bridge = ["bureau_file_id", "cif_id"]
    missing_bridge = [
        c for c in _required_bridge if c not in prm_bureau_cif_bridge.columns
    ]
    if missing_bridge:
        LOG.warning(
            "enrich_bureau_salary: prm_bureau_cif_bridge missing %s"
            " — bureau salary signals will be NULL",
            missing_bridge,
        )
        return None

    # Deduplicate CIF bridge: keep one cif_id per bureau_file_id (any snapshot)
    cif_bridge = prm_bureau_cif_bridge.select(
        "bureau_file_id", "cif_id"
    ).dropDuplicates(["bureau_file_id"])

    # Bridge salary history to cif_id via bureau_file_id
    # subj_salcr_hist_ref_mnth is stored as "MMYYYY" string — must specify format
    sal_with_cif = stg_salary_hist.join(
        cif_bridge,
        on=stg_salary_hist[_AECB_SAL_FILE_COL] == cif_bridge["bureau_file_id"],
        how="inner",
    ).select(
        F.col("cif_id").cast("string"),
        F.to_date(F.col(_AECB_SAL_DATE_COL), "MMyyyy").alias("_sal_date"),
        F.col(_AECB_SAL_AMT_COL).cast("double").alias("_sal_amt"),
    )

    n_bridge = sal_with_cif.count()
    LOG.info("enrich_bureau_salary: %d rows after bridge join", n_bridge)
    if n_bridge == 0:
        LOG.warning(
            "enrich_bureau_salary: bureau_file_id join produced 0 rows"
            " — prm_bureau_cif_bridge may not cover stg_aecb_salary_history"
        )
        return None

    # 6-month window join [T0-6m, T0)
    joined = cif_base.join(sal_with_cif, on="cif_id", how="inner").filter(
        (F.col("_sal_date") >= F.add_months(F.col(anchor_col), -6))
        & (F.col("_sal_date") < F.col(anchor_col))
    )

    # PIT: most recent salary record within window
    w_pit = Window.partitionBy(*grain_key).orderBy(F.col("_sal_date").desc())
    pit = (
        joined.withColumn("_rn", F.row_number().over(w_pit))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.lit(1).cast("int").alias("bureau_salary_present_6m_flag"),
            F.col("_sal_amt").cast("double").alias("bureau_salary_amt_last"),
        )
    )

    # Note: bureau_salary_present_6m_flag is always NULL (no bureau record) or 1
    # (salary credit found in window). It is never 0 — analysts querying = 0 find no rows.
    return pit


def enrich_bureau_alerts(
    cif_base: DataFrame,
    prm_bureau_alert: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Bureau alert signals from prm_bureau_alert_enriched (CIF-grain).

    Window: [T0 - 90 days, T0) — pre-T0 to avoid leakage.
    Derives:
        a1_new_salary_acct_flag  int 0/1 — new salary account alert in window
        a1_offus_paying_flag     int 0/1 — positive off-us delinquency in window

    Column names in prm_bureau_alert_enriched (primary layer renames applied):
        cif_id          — PRVDR_SUBJ_NUM cast to long
        extract_date    — EXTRACT_DT renamed in _ALERT_RENAMES
        alert_type_flag — lower(trim(no-spaces(ALERT_DESC))) derived column

    Filter values (alert_type_flag):
        new salary acct:  _ALERT_NEW_SALARY_ACCT = "salaryaccountadded" (exact match)
        off-us paying:    _ALERT_OFFUS_PAYING_PREFIX = "positivealerts" (startswith)
                          Covers all DPD bands and product types, e.g.:
                            positivealerts30dpdtoactive-creditcards
                            positivealerts60dpdtoactive-installments
                          Confirmed from T26a EDA (2026-09-17).

    Schema guard: required columns absent → returns None (warning logged).
    Required columns: _BUREAU_ALERT_CIF_COL, _BUREAU_ALERT_DATE_COL,
                      _BUREAU_ALERT_TYPE_COL

    Returns DataFrame with (account_id, spell_id, a1_new_salary_acct_flag,
                           a1_offus_paying_flag) or None.
    """
    _required = [_BUREAU_ALERT_CIF_COL, _BUREAU_ALERT_DATE_COL, _BUREAU_ALERT_TYPE_COL]
    missing = [c for c in _required if c not in prm_bureau_alert.columns]
    if missing:
        LOG.warning(
            "enrich_bureau_alerts: prm_bureau_alert_enriched missing %s"
            " — bureau alert signals will be NULL",
            missing,
        )
        return None

    alerts_dated = prm_bureau_alert.withColumn(
        "_alert_date", F.to_date(F.col(_BUREAU_ALERT_DATE_COL))
    ).select(
        F.col(_BUREAU_ALERT_CIF_COL).alias("_bur_cif_id"),
        "_alert_date",
        F.col(_BUREAU_ALERT_TYPE_COL).alias("_alert_type"),
    )

    # 90-day pre-T0 window
    joined = (
        cif_base.join(
            alerts_dated,
            on=cif_base["cif_id"] == alerts_dated["_bur_cif_id"],
            how="inner",
        )
        .filter(
            (F.col("_alert_date") >= F.date_sub(F.col(anchor_col), 90))
            & (F.col("_alert_date") < F.col(anchor_col))
        )
        .drop("_bur_cif_id")
    )

    result = joined.groupBy(*grain_key).agg(
        F.max(
            F.when(F.col("_alert_type") == _ALERT_NEW_SALARY_ACCT, F.lit(1)).otherwise(
                F.lit(0)
            )
        )
        .cast("int")
        .alias("a1_new_salary_acct_flag"),
        F.max(
            F.when(
                F.col("_alert_type").startswith(_ALERT_OFFUS_PAYING_PREFIX), F.lit(1)
            ).otherwise(F.lit(0))
        )
        .cast("int")
        .alias("a1_offus_paying_flag"),
    )

    return result


def enrich_fea_bureau_alerts(
    cif_base: DataFrame,
    fea_aecb_alerts: DataFrame,
    anchor_col: str = "t0",
    grain_key: tuple = ("account_id", "spell_id"),
) -> DataFrame | None:
    """Salary-account signal from the retail.feature_space pre-engineered alert table.

    Second source for a1_new_salary_acct_flag — used alongside enrich_bureau_alerts
    (prm_bureau_alert_enriched) so that either source firing is sufficient.

    Source: fea_monthly_aecb_alerts (retail.feature_space).
    Grain: cif_id × month_number (last day of month, YYYY-MM-DD).
    Signal: ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum
        — 3-month rolling sum of salary-account-added-or-closed alerts.
          Non-zero → at least one salary account event in the 3-month window.

    Note: the feature space combines add + close into one flag.  We accept this
    as a corroborating signal; the primary source (prm_bureau_alert_enriched) is
    add-only and more precise.

    PIT join: latest month_number strictly before the calendar month of T0.
    This ensures the rolling window uses only complete months that precede T0,
    matching the ≈90-day pre-T0 window used by enrich_bureau_alerts.

    Schema guard: required columns absent → returns None (warning logged).
    Required columns: cif_id, month_number,
                      ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum

    Returns DataFrame with (account_id, spell_id, fea_salary_acct_flag: int 0/1)
    or None.
    """
    _FEA_SAL_COL = (
        "ft_aecb_salary_account_is_added_or_closed_alert_flag_in_last_0_2_months_sum"
    )
    _required = ["cif_id", "month_number", _FEA_SAL_COL]
    missing = [c for c in _required if c not in fea_aecb_alerts.columns]
    if missing:
        LOG.warning(
            "enrich_fea_bureau_alerts: fea_monthly_aecb_alerts missing %s"
            " — fea_salary_acct_flag will be NULL",
            missing,
        )
        return None

    fea_dated = fea_aecb_alerts.select(
        F.col("cif_id"),
        F.to_date(F.col("month_number").cast("string"), "yyyyMMdd").alias(
            "_month_date"
        ),
        F.col(_FEA_SAL_COL).cast("double").alias("_sal_sum"),
    )

    # PIT: latest complete month strictly before the calendar month of T0
    joined = cif_base.join(fea_dated, on="cif_id", how="inner").filter(
        F.col("_month_date") < F.trunc(F.col(anchor_col), "month")
    )

    w = Window.partitionBy(*grain_key).orderBy(F.col("_month_date").desc())
    result = (
        joined.withColumn("_rn", F.row_number().over(w))
        .filter(F.col("_rn") == 1)
        .select(
            *grain_key,
            F.when(F.col("_sal_sum") > 0, F.lit(1))
            .otherwise(F.lit(0))
            .cast("int")
            .alias("fea_salary_acct_flag"),
        )
    )

    return result


def log_a1_stats(df: DataFrame) -> None:
    """Log state distribution for A1 ability axis."""
    state_counts = df.groupBy("a1_state").count().orderBy("a1_state").collect()
    total = sum(r["count"] for r in state_counts)
    LOG.info("build_a1_ability — state distribution (n=%d):", total)
    for row in state_counts:
        pct = 100.0 * row["count"] / max(total, 1)
        LOG.info(
            "  a1_state=%-25s  %6d  (%5.1f%%)",
            row["a1_state"],
            row["count"],
            pct,
        )
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/__init__.py`
action: delete · base sha256 `65c9988c7d9e81a1dfeba967bdfe4f03037ccf21b7749032026e46e7beafee42` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""CC A1 ability axis (GRR MECE points) on the shared ``a1_ability`` engine."""

from .pipeline import create_pipeline

__all__ = ["create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/cc_a1_ability_v2/nodes.py`
action: delete · base sha256 `2c45eefef8f32b32cc09382327f477b255b33e508bad1508880d01b3a488061f` · base trailing newline: yes

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
action: delete · base sha256 `b611a25947b8deaf41a538ac36f52dee3fd2e450a83d734ecb618d683bfe4001` · base trailing newline: yes

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

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/__init__.py`
action: delete · base sha256 `84f71dbb70ba3bfb15b9c1865aab1cefe578a02d286eed98c1054c66de230288` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""RL A1 ability axis on the shared ``a1_ability`` engine."""

from .pipeline import create_b05_check_pipeline, create_pipeline

__all__ = ["create_b05_check_pipeline", "create_pipeline"]
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/rl_a1_ability_v2/b05_check.py`
action: delete · base sha256 `bd8eda6ef86412eac37b6fda220b1f923aa2a47e4c75d25158cb41e16ede99e8` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
action: delete · base sha256 `af87ae0a282a508d5dd43f11928eeda3286fb5769d00fd2659aa745951f751a7` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
action: delete · base sha256 `a5a8414463e1ac15dcced0da19191eaf029caeeea666182a9b786a60ba83bd8a` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

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
Clean up after mirror bundle 08_a1_finish.md, on the bundle's branch.
- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths
  for model_id cc_60_180 **and** rl_60_180 from the workplace conf and write out each
  command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b08_check` and `.../crx_cc_a1_ability_v2` (cc_60_180)
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b08_check` and `.../crx_rl_a1_ability_v2` (rl_60_180)
  - the retired intermediates under `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/`:
    `crx_cc_a1_internal_returns`, `crx_cc_a1_base`, `crx_cc_a1_cif_enriched`,
    `crx_cc_a1_group_b_income`, `crx_cc_a1_group_b_income_recent`, `crx_cc_a1_group_b_bureau`,
    `crx_cc_a1_group_b_bureau_recent`, `crx_cc_a1_group_c`, `crx_cc_a1_group_c_recent`
    (cc_60_180); `crx_rl_a1_internal_returns`, `crx_rl_a1_group_a`,
    `crx_rl_a1_group_b_income_recent`, `crx_rl_a1_group_b_bureau_recent`,
    `crx_rl_a1_group_c_recent`, `crx_rl_a1_group_d` (rl_60_180). Skip any that does not exist.
- Remove the temporary check (everything marked TEMPORARY for bundle 08):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_v2`, `crx_cc_a1_ability_b08_check`,
    `crx_rl_a1_ability_v2` and `crx_rl_a1_ability_b08_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a1_ability_b08_check` entries and
    their comments;
  - crx_persona/a1_ability/pipeline.py: `create_b08_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b08_check`, and the TEMPORARY
    paragraph of the module docstring;
  - crx_persona/cc_a1_ability/ and rl_a1_ability/: `create_b08_check_pipeline` in
    `pipeline.py` (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a1_ability/b08_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b08\|a1_ability_v2" src conf`
  prints nothing.
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
