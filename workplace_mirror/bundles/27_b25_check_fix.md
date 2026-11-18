# Mirror bundle 27 — Bundle 25 check fix: saved __b25 copies (explicit catalog entries) + A4 UDF cross-join warning

apply_bundle version: 7 · built 2026-11-18 from `f20ecaf..8f52576` · source: 1 added, 2 replaced, 1 deleted · helpers: 0

## Steps — do these in order, from the workplace repo root

The bundle file and the apply script live in `data/input/mirror_bundles/` (gitignored) and are
never committed; only `src/` and `conf/` are (step 4). Copy each command
block exactly as it is.

### In UAT

**Step 1.** Continue on the branch of the earlier bundle (nothing uncommitted on it):

```bash
git checkout feature/council_a1_a3_refactor && git pull && git status --short
```

**Step 2.** Create the folder, then save this file **raw** (GitHub → Raw → copy all) as `data/input/mirror_bundles/27_b25_check_fix.md`:

```bash
mkdir -p data/input/mirror_bundles
```

**Step 3.** Write the apply script, apply, and list what changed — must end with `APPLY PASSED`:

```bash
python -c "import pathlib, re; d = pathlib.Path('data/input/mirror_bundles'); md = (d / '27_b25_check_fix.md').read_text(encoding='utf-8'); sec = md.split('\n## Apply script\n', 1)[1]; m = re.search(r'^(\x60{5,})python\n(.*?)\n\1$', sec, re.S | re.M); (d / 'apply_bundle.py').write_text(m.group(2) + '\n', encoding='utf-8'); print('apply_bundle.py written')" && python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/27_b25_check_fix.md --apply && git status --short
```

A file this repo changed since the bundle's copy (an edit at work, a lint fix) is
merged, not refused: the apply lists it as `MERGED`. Look at its `git diff` before
committing.

1. **Catalog.** Confirm `conf/base/catalog/tmp_b25_check.yml` is gone and `conf/base/catalog/catalog_tmp_b25_check.yml` exists. Then check that Kedro resolves the names: in a `kedro ipython` session (or the project's equivalent), `type(catalog._get_dataset("crx_cc_a1_ability__b25")).__name__` and the same for `crx_rl_a3_dlq_cycles__b25` must both print `SparkDataset`. If either prints MemoryDataset or fails, stop and report how this repo's settings load catalog files (`settings.py` `CONFIG_LOADER_ARGS`).
2. **No other catalog key removed.** List any top-level key the apply removed from `conf/base/catalog/*.yml` compared with the last commit (expected: none).

**Step 4.** Commit the source only, and push:

```bash
git add src conf && git commit -m "Bundle 27: b25 check saves its __b25 copies (explicit catalog entries); A4 UDFs non-deterministic" && git push
```

**Undo** (before step 4) — puts every touched file back to the last commit:

```bash
python data/input/mirror_bundles/apply_bundle.py data/input/mirror_bundles/27_b25_check_fix.md --revert
```

### In PROD

**Step 5.** Get the branch:

```bash
git fetch origin && git checkout feature/council_a1_a3_refactor && git pull
```

Stop any `crx_<p>_b25_check` run still going (Ctrl+C); its in-memory outputs are lost anyway. Blocks it already printed stay valid: paste them if you have them.

**Step 7 (again).** Run the check for **all four model_ids** (set `model_id` in `conf/dev/globals_dev.yml` each time), cc_60_180 first. Each node now writes its `__b25` copy to HDFS and the comparisons read the copies, so it should run faster than the first attempt:

```bash
kedro run --env=dev --pipeline=crx_cc_b25_check
```

```bash
kedro run --env=dev --pipeline=crx_rl_b25_check
```

The log should now show `Saving data to crx_cc_..._b25 (SparkDataset)`; if it still says MemoryDataset, stop and paste the first such line. Paste back, per model_id, every `=== B25 … START ===` … `END ===` block and the run time. Then bundle 25's step 8, then this bundle's cleanup (not bundle 25's). The A3 results prompt (`a3_final/sonnet_a3_results_prompt.md`) runs on the `__b25` copies **before** step 8 and the cleanup.

**When you are done**, give the *Cleanup prompt* at the bottom to the workplace
assistant in UAT.

## What this bundle does

**What this bundle does.** Two fixes to bundle 25's check, to apply now, on top of bundle 25 (bundle 26 may come before or after; they touch different files).

- **Check outputs are saved.** The `"{name}__b25"` catalog pattern did not resolve in the workplace: every rerun dataset fell back to MemoryDataset. Nothing was saved, and each comparison recomputed the whole chain from the raw tables (`compare_a1` ran over 30 minutes; repeated "Broadcasting large task binary" warnings). `tmp_b25_check.yml` is replaced by `catalog_tmp_b25_check.yml`: 64 explicit entries (36 cc, 34 rl, 6 shared), same HDFS folder `.../<model_id>/<persona>/b25_check/<name>`, Spark parquet, overwrite.
- **A4 UDF warning.** Both Python UDFs in the A4 engine (`_dpd_journey/spark.py`) are marked non-deterministic. Spark had copied the UDF's output into a join condition (`ExtractPythonUDFFromJoinCondition`), which turned the join into a cross join, and it ran the UDF several times per row. Output unchanged: A4 chain spec and the golden harness (188 datasets) pass.

Bundle 25's step 7 and step 8 stay as they are; this bundle's cleanup replaces bundle 25's.

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
| add | `conf/base/catalog/catalog_tmp_b25_check.yml` |
| replace | `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py` |
| replace | `src/enbd_collections/pipelines/crx_persona/b25_check.py` |
| delete | `conf/base/catalog/tmp_b25_check.yml` |

## Files

### FILE: `conf/base/catalog/catalog_tmp_b25_check.yml`
action: add · new sha256 `07d84febe9833085fef20747f6f81e4430485f68b41e6d9e9b0fe4327daa861b` · new trailing newline: yes

New:

`````yaml
# TEMPORARY (bundles 25 + 27): every dataset crx_<p>_b25_check reruns, saved as <name>__b25.
# Explicit entries (the workplace does not resolve dataset patterns). This file and the
# HDFS folder b25_check are removed by the cleanup.

crx_cc_a1_ability__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_ability"
  save_args:
    mode: overwrite

crx_cc_a1_casa_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_casa_signals"
  save_args:
    mode: overwrite

crx_cc_a1_cross_product_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_cc_a1_distress_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_distress_signals"
  save_args:
    mode: overwrite

crx_cc_a1_eosb_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_cc_a1_income_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_income_signals"
  save_args:
    mode: overwrite

crx_cc_a1_liquidity_anchor__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_cc_a2_dcore_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_cc_a2_demographics_deceased__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_cc_a2_locatability__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a2_locatability"
  save_args:
    mode: overwrite

crx_cc_a2_location_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a2_location_signals"
  save_args:
    mode: overwrite

crx_cc_a2_way4_deceased__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_cc_a3_commitment_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_cc_a3_dlq_payment_signals_single_payment_cycle_count__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_dlq_payment_signals_single_payment_cycle_count"
  save_args:
    mode: overwrite

crx_cc_a3_dues__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_dues"
  save_args:
    mode: overwrite

crx_cc_a3_episode__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_episode"
  save_args:
    mode: overwrite

crx_cc_a3_instalments__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_instalments"
  save_args:
    mode: overwrite

crx_cc_a3_payment_credibility__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_payment_credibility"
  save_args:
    mode: overwrite

crx_cc_a3_payment_cycles__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_payment_cycles"
  save_args:
    mode: overwrite

crx_cc_a3_payments__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_payments"
  save_args:
    mode: overwrite

crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count"
  save_args:
    mode: overwrite

crx_cc_a3_promise_events__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_promise_events"
  save_args:
    mode: overwrite

crx_cc_a3_strong_negative_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a3_strong_negative_signals"
  save_args:
    mode: overwrite

crx_cc_a4_deterioration__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_a4_deterioration"
  save_args:
    mode: overwrite

crx_cc_acct_windows__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_balance__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_balance"
  save_args:
    mode: overwrite

crx_cc_billing__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_billing"
  save_args:
    mode: overwrite

crx_cc_dpd_sequences__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_dpd_sequences"
  save_args:
    mode: overwrite

crx_cc_limits__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_limits"
  save_args:
    mode: overwrite

crx_cc_transactions__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_rl_a1_ability__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_ability"
  save_args:
    mode: overwrite

crx_rl_a1_casa_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_casa_signals"
  save_args:
    mode: overwrite

crx_rl_a1_cross_product_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_cross_product_signals"
  save_args:
    mode: overwrite

crx_rl_a1_distress_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_distress_signals"
  save_args:
    mode: overwrite

crx_rl_a1_eosb_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_eosb_signals"
  save_args:
    mode: overwrite

crx_rl_a1_income_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_income_signals"
  save_args:
    mode: overwrite

crx_rl_a1_liquidity_anchor__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a1_liquidity_anchor"
  save_args:
    mode: overwrite

crx_rl_a2_dcore_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a2_dcore_signals"
  save_args:
    mode: overwrite

crx_rl_a2_demographics_deceased__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a2_demographics_deceased"
  save_args:
    mode: overwrite

crx_rl_a2_locatability__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a2_locatability"
  save_args:
    mode: overwrite

crx_rl_a2_location_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a2_location_signals"
  save_args:
    mode: overwrite

crx_rl_a2_way4_deceased__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a2_way4_deceased"
  save_args:
    mode: overwrite

crx_rl_a3_commitment_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_commitment_signals"
  save_args:
    mode: overwrite

crx_rl_a3_dlq_cycles__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_dlq_cycles"
  save_args:
    mode: overwrite

crx_rl_a3_dlq_payment_signals_single_payment_cycle_count__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_dlq_payment_signals_single_payment_cycle_count"
  save_args:
    mode: overwrite

crx_rl_a3_dues__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_dues"
  save_args:
    mode: overwrite

crx_rl_a3_episode__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_episode"
  save_args:
    mode: overwrite

crx_rl_a3_instalments__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_instalments"
  save_args:
    mode: overwrite

crx_rl_a3_payment_credibility__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_payment_credibility"
  save_args:
    mode: overwrite

crx_rl_a3_payments__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_payments"
  save_args:
    mode: overwrite

crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count"
  save_args:
    mode: overwrite

crx_rl_a3_promise_events__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_promise_events"
  save_args:
    mode: overwrite

crx_rl_a3_strong_negative_signals__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a3_strong_negative_signals"
  save_args:
    mode: overwrite

crx_rl_a4_deterioration__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_a4_deterioration"
  save_args:
    mode: overwrite

crx_rl_dpd_sequences__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_dpd_sequences"
  save_args:
    mode: overwrite

crx_rl_dpd_sequences_linked__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_dpd_sequences_linked"
  save_args:
    mode: overwrite

crx_rl_full_history_linked__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_full_history_linked"
  save_args:
    mode: overwrite

crx_rl_restructure_chains__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/crx_rl_restructure_chains"
  save_args:
    mode: overwrite

feat_cif_bureau_bounces_monthly__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/feat_cif_bureau_bounces_monthly"
  save_args:
    mode: overwrite

feat_cif_bureau_salary_monthly__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/feat_cif_bureau_salary_monthly"
  save_args:
    mode: overwrite

feat_cif_cross_product_monthly__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/feat_cif_cross_product_monthly"
  save_args:
    mode: overwrite

prm_card_contracts__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/prm_card_contracts"
  save_args:
    mode: overwrite

prm_card_month_end__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/prm_card_month_end"
  save_args:
    mode: overwrite

prm_loan_month_end__b25:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/prm_loan_month_end"
  save_args:
    mode: overwrite
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/_dpd_journey/spark.py`
action: replace · base sha256 `d8124294bc0fdf39f3bc367d74480dedbb176e659375e88956ef39751475878e` · base trailing newline: yes · new sha256 `a49add61a4c7a548129097783ced339303e47b2be4dc61b3fa141aa26090d29a` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""Spark side: scoping, the history floor, and ONE shuffle that gathers each account's
monthly buckets into an array; the per-account core (history.py/states.py) then runs inside
the UDFs. Two stages (two Kedro nodes per product):

build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features
"""

from __future__ import annotations

import logging
import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns, string_key
from ..scoring_engine import state_label
from ._dates import _month_col, _month_idx
from .constants import BucketScheme
from .history import build_history
from .logging import _log_sequence_stats, log_state_stats
from .params import JourneyParams
from .states import DISPLAY_NAMES, classify

LOG = logging.getLogger(__name__)

_PACKAGE = __name__.rsplit(".", 1)[0]
_SUBMODULES = (
    "constants",
    "params",
    "_dates",
    "core",
    "states",
    "history",
    "spark",
    "logging",
)


def _ship_by_value() -> None:
    """Pickle every module of this package BY VALUE into the UDFs (cloudpickle >= 2.0),
    so executors need not have the Kedro project: the UDF closures reach history.py and
    states.py too, and by-reference pickling only works locally (shared sys.path)."""
    try:
        from pyspark import cloudpickle  # pylint: disable=import-outside-toplevel

        if not hasattr(cloudpickle, "register_pickle_by_value"):
            return  # pragma: no cover — older PySpark
        for name in (_PACKAGE, *(f"{_PACKAGE}.{m}" for m in _SUBMODULES)):
            mod = sys.modules.get(name)
            if mod is not None:
                cloudpickle.register_pickle_by_value(mod)
    except (
        Exception  # pylint: disable=broad-exception-caught
    ) as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning(
            "could not register %s for pickle-by-value (%s); the package must be "
            "importable on the executors",
            _PACKAGE,
            exc,
        )


_HISTORY_SCHEMA = T.StructType(
    [
        T.StructField("build_status", T.StringType()),
        T.StructField("first_month_idx", T.IntegerType()),
        T.StructField("last_month_idx", T.IntegerType()),
        T.StructField("buckets", T.ArrayType(T.IntegerType())),
        T.StructField("history_cropped", T.BooleanType()),
        T.StructField("n_gap_months_filled", T.IntegerType()),
        T.StructField("n_gap_months_rolled", T.IntegerType()),
        T.StructField("n_gap_months_inferred", T.IntegerType()),
        T.StructField("n_cycle_shift_moves", T.IntegerType()),
        T.StructField("legacy_drop", T.BooleanType()),
        T.StructField("n_months_truncated", T.IntegerType()),
        T.StructField("n_dup_month_rows", T.IntegerType()),
    ]
)

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None),
    ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()),
    ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()),
    ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()),
    ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()),
    ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()),
    ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()),
    ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType(
    [T.StructField("det_state", T.StringType())]
    + [T.StructField(n, t) for n, t in _FEATURES if t is not None]
)


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(
        F.expr(f"make_date(cast({c} div 12 as int), cast({c} % 12 + 1 as int), 1)")
    )


def _monthly_rows_per_account(
    history: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> DataFrame:
    """One row per account: `_rows` (array of struct m, d, b: month index, day number,
    native bucket; windowed and valid only), `_first_raw` and `n_invalid_rows`, plus
    `_rf` if `history` has `restructure_flag`; `_global_min` is the first valid month
    of the whole history."""
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None
    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(
            F.when(
                in_window,
                F.struct(
                    m.alias("m"),
                    F.datediff(
                        F.col("obs_date").cast("date"), F.lit("1970-01-01")
                    ).alias("d"),
                    bucket.alias("b"),
                ),
            )
        ).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias(
            "n_invalid_rows"
        ),  # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    return per_acc.crossJoin(F.broadcast(source_min))


def build_dpd_sequences(
    history: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    restructure: DataFrame | None = None,
) -> DataFrame:
    """Stage 1: monthly rows per account -> one shuffle -> `build_history` per account.
    history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
    optionally restructure_flag (0/1 per row; max over the account's rows).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag
    """
    require_columns(history, ["account_id", "obs_date", "dlq_bucket"], "A4 history")
    _ship_by_value()
    per_acc = _monthly_rows_per_account(history, scheme, params)

    offset, shift = scheme.offset, params.repair_cycle_shift
    fill, how = params.fill_straight_roll_gaps, params.on_unresolvable_gap
    max_inf = params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):  # month rows, first month -> history struct
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history(
            [(r["m"], r["d"], r["b"]) for r in rows],
            first_raw,
            global_min,
            offset,
            fill,
            how,
            shift,
            max_inf,
        )

    hist_udf = F.udf(_udf, _HISTORY_SCHEMA)
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias(
            "dpd_string"
        ),
        F.col("_h.history_cropped").alias("history_cropped"),
        F.coalesce("_h.n_gap_months_filled", F.lit(0)).alias("n_gap_months_filled"),
        F.coalesce("_h.n_gap_months_rolled", F.lit(0)).alias("n_gap_months_rolled"),
        F.coalesce("_h.n_gap_months_inferred", F.lit(0)).alias("n_gap_months_inferred"),
        F.coalesce("_h.n_cycle_shift_moves", F.lit(0)).alias("n_cycle_shift_moves"),
        F.coalesce("_h.legacy_drop", F.lit(False)).alias("legacy_drop"),
        F.coalesce("_h.n_months_truncated", F.lit(0)).alias("n_months_truncated"),
        F.coalesce("_h.n_dup_month_rows", F.lit(0)).alias("n_dup_month_rows"),
        F.col("n_invalid_rows").cast("int"),
        (F.col("_rf") if "_rf" in s.columns else F.lit(None).cast("int")).alias("_rf"),
    )
    if restructure is not None:
        out = out.join(
            restructure.select(
                "account_id", F.col("restructure_blind_spot_flag").alias("_rs")
            ),
            "account_id",
            "left",
        )
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop(
        "_rf", "_rs"
    )
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


def _spine_rows_with_history(
    sequences: DataFrame, spine: DataFrame, params: JourneyParams
) -> DataFrame:
    """Spine rows (account_id, observation_date) joined to the account's `ok` sequence
    row, kept when the observation month lies in first_month..last_month. Adds
    `_obs_idx` and `_trunc_len`, the number of history months up to that month."""
    end_dt = F.to_date(F.lit(params.end_date))
    seq = (
        sequences.where(F.col("build_status") == "ok")
        .withColumn("_first_idx", _month_col(F.col("first_month")))
        .withColumn("_last_idx", _month_col(F.col("last_month")))
        .withColumn("_key", string_key(sequences))
    )
    sp = spine.where(F.col("observation_date").cast("date") <= end_dt).select(
        string_key(spine).alias("_key"),
        F.col("observation_date").cast("date").alias("observation_date"),
    )

    # join on the safe string key only — account_id in the output keeps seq's own
    # native type (long for CC, string for RL), never the stringified join key.
    obs_idx = _month_col(F.col("observation_date"))
    trunc_len = (obs_idx - F.col("_first_idx") + 1).cast("int")
    return (
        sp.join(seq, "_key", "inner")
        .withColumn("_obs_idx", obs_idx)
        .withColumn("_trunc_len", trunc_len)
        .where((F.col("_trunc_len") >= 1) & (F.col("_obs_idx") <= F.col("_last_idx")))
    )


def build_deterioration(
    sequences: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    spine: DataFrame,
    log_states: bool = True,
) -> DataFrame:
    """Stage 2: spine rows + sequences -> history cut at each row's month -> `classify`.
    sequences: output of build_dpd_sequences (one row per account). spine: 2-column
    (account_id, observation_date) — one row per point-in-time state to classify, e.g.
    cc_spine/rl_spine already filtered to the run's model_id/DLQ-band scope. Classifies
    EVERY spine row, not one row per account: each row's billing history is the account's
    Stage 1 dlq_buckets array truncated up to and including that row's own month, run
    through the same, unmodified classify() engine.

    A spine row is kept only if its month falls inside the account's observed/gap-filled
    window (first_month..last_month) and the truncated bucket is itself delinquent
    (canonical >= 2) — both explainable "no billing history at this date" cases, not a
    silent drop. No model_id/segment bucket-set filter is applied here: that scoping is
    inherited for free from the spine's own population.

    Returns one row per (account_id, observation_date):
        account_id, observation_date, det_state, det_state_label, det_segment,
        current_bucket (native, as of this row's date), <features>, history_months
        (months observed as of this row), history_cropped, n_months_truncated,
        restructure_blind_spot_flag, computed_at
    """
    _ship_by_value()
    segment = params.segment
    offset, top = scheme.offset, scheme.canon_top
    repair = scheme.repair_jumps
    joined = _spine_rows_with_history(sequences, spine, params)

    # in: buckets, truncation length, cropped, blind-spot flag; out: classify struct
    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot):
        sl = list(buckets)[:trunc_len_]
        if not sl or max(sl[-1] + offset, 1) < 2:
            return None
        return classify(
            sl, bool(cropped), offset, top, repair, bool(restructure_blind_spot)
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema)(
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
        ),
    ).where(F.col("_s").isNotNull())

    feat_cols = [
        F.col(f"_s.{f.name}").alias(f.name)
        for f in schema.fields
        if f.name != "det_state"
    ]
    out = res.select(
        F.col("account_id"),
        F.col("observation_date"),
        F.col("_s.det_state").alias("det_state"),
        state_label("_s.det_state", DISPLAY_NAMES).alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        F.element_at("dlq_buckets", F.col("_trunc_len")).alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("_trunc_len").alias("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always on, as on every axis (_common.log_latest_month); log_stats only gates the
    # Stage 1 telemetry above. The month filter pushes down through the join.
    if log_states:  # False: the caller unions two runs and logs the result
        log_state_stats(out, params.end_date, scheme, params)
    return out
`````

New:

`````python
"""Spark side: scoping, the history floor, and ONE shuffle that gathers each account's
monthly buckets into an array; the per-account core (history.py/states.py) then runs inside
the UDFs. Two stages (two Kedro nodes per product):

build_dpd_sequences    (account_id, obs_date, dlq_bucket) long history
                       -> one row per account: gap-filled monthly bucket array + audit
build_deterioration    sequences -> one row per account in the segment: state + features
"""

from __future__ import annotations

import logging
import sys

from pyspark.sql import DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from .._common import require_columns, string_key
from ..scoring_engine import state_label
from ._dates import _month_col, _month_idx
from .constants import BucketScheme
from .history import build_history
from .logging import _log_sequence_stats, log_state_stats
from .params import JourneyParams
from .states import DISPLAY_NAMES, classify

LOG = logging.getLogger(__name__)

_PACKAGE = __name__.rsplit(".", 1)[0]
_SUBMODULES = (
    "constants",
    "params",
    "_dates",
    "core",
    "states",
    "history",
    "spark",
    "logging",
)


def _ship_by_value() -> None:
    """Pickle every module of this package BY VALUE into the UDFs (cloudpickle >= 2.0),
    so executors need not have the Kedro project: the UDF closures reach history.py and
    states.py too, and by-reference pickling only works locally (shared sys.path)."""
    try:
        from pyspark import cloudpickle  # pylint: disable=import-outside-toplevel

        if not hasattr(cloudpickle, "register_pickle_by_value"):
            return  # pragma: no cover — older PySpark
        for name in (_PACKAGE, *(f"{_PACKAGE}.{m}" for m in _SUBMODULES)):
            mod = sys.modules.get(name)
            if mod is not None:
                cloudpickle.register_pickle_by_value(mod)
    except (
        Exception  # pylint: disable=broad-exception-caught
    ) as exc:  # pragma: no cover — older PySpark: needs the package on executors
        LOG.warning(
            "could not register %s for pickle-by-value (%s); the package must be "
            "importable on the executors",
            _PACKAGE,
            exc,
        )


_HISTORY_SCHEMA = T.StructType(
    [
        T.StructField("build_status", T.StringType()),
        T.StructField("first_month_idx", T.IntegerType()),
        T.StructField("last_month_idx", T.IntegerType()),
        T.StructField("buckets", T.ArrayType(T.IntegerType())),
        T.StructField("history_cropped", T.BooleanType()),
        T.StructField("n_gap_months_filled", T.IntegerType()),
        T.StructField("n_gap_months_rolled", T.IntegerType()),
        T.StructField("n_gap_months_inferred", T.IntegerType()),
        T.StructField("n_cycle_shift_moves", T.IntegerType()),
        T.StructField("legacy_drop", T.BooleanType()),
        T.StructField("n_months_truncated", T.IntegerType()),
        T.StructField("n_dup_month_rows", T.IntegerType()),
    ]
)

# Output features (name, type). Order = output column order after det_state*.
_FEATURES = [
    ("n_gap_months_filled", None),
    ("left_censored", T.BooleanType()),
    ("starts_delinquent", T.BooleanType()),
    ("months_before_spell", T.IntegerType()),
    ("n_blips", T.IntegerType()),
    ("n_prior_episodes", T.IntegerType()),
    ("gap_prior_peak3", T.IntegerType()),
    ("spell_pay_events", T.IntegerType()),
    ("runup_len", T.IntegerType()),
    ("runup_pays", T.IntegerType()),
    ("last6_in_band", T.IntegerType()),
    ("months_since_4", T.IntegerType()),
    ("chg_6m", T.IntegerType()),
    ("n_glitches", T.IntegerType()),
    ("n_jumps_repaired", T.IntegerType()),
    ("n_jumps_left", T.IntegerType()),
]
_CLASSIFY_SCHEMA = T.StructType(
    [T.StructField("det_state", T.StringType())]
    + [T.StructField(n, t) for n, t in _FEATURES if t is not None]
)


def _idx_to_month_end(c) -> F.Column:
    return F.last_day(
        F.expr(f"make_date(cast({c} div 12 as int), cast({c} % 12 + 1 as int), 1)")
    )


def _monthly_rows_per_account(
    history: DataFrame, scheme: BucketScheme, params: JourneyParams
) -> DataFrame:
    """One row per account: `_rows` (array of struct m, d, b: month index, day number,
    native bucket; windowed and valid only), `_first_raw` and `n_invalid_rows`, plus
    `_rf` if `history` has `restructure_flag`; `_global_min` is the first valid month
    of the whole history."""
    end_dt = F.to_date(F.lit(params.end_date))
    floor_idx = _month_idx(params.floor_date) if params.floor_date else None
    m = _month_col(F.col("obs_date"))
    bucket = F.col("dlq_bucket").cast("int")
    valid = bucket.isNotNull() & bucket.between(0, scheme.top)
    in_window = valid if floor_idx is None else valid & (m >= F.lit(floor_idx))
    h = history.where(F.col("obs_date").cast("date") <= end_dt)

    aggs = [
        F.collect_list(
            F.when(
                in_window,
                F.struct(
                    m.alias("m"),
                    F.datediff(
                        F.col("obs_date").cast("date"), F.lit("1970-01-01")
                    ).alias("d"),
                    bucket.alias("b"),
                ),
            )
        ).alias("_rows"),
        F.min(F.when(valid, m)).alias("_first_raw"),
        F.sum((~valid).cast("int")).alias(
            "n_invalid_rows"
        ),  # null / out-of-range buckets
    ]
    if "restructure_flag" in history.columns:
        aggs.append(F.max(F.col("restructure_flag").cast("int")).alias("_rf"))
    per_acc = h.groupBy("account_id").agg(*aggs)  # the one shuffle
    source_min = h.where(valid).agg(F.min(m).alias("_global_min"))  # 1 row
    return per_acc.crossJoin(F.broadcast(source_min))


def build_dpd_sequences(
    history: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    restructure: DataFrame | None = None,
) -> DataFrame:
    """Stage 1: monthly rows per account -> one shuffle -> `build_history` per account.
    history: account_id, obs_date (date/timestamp), dlq_bucket (native int),
    optionally restructure_flag (0/1 per row; max over the account's rows).
    restructure: optional (account_id, restructure_blind_spot_flag), one row per account.

    Returns ONE row per account (every account in `history`, with a build_status):
        account_id, build_status, first_month, last_month (month-end dates),
        history_months, dlq_buckets array<int> (native, oldest -> newest, gap-filled),
        dpd_string (native digits, LEFTMOST = latest month — the bank's string convention),
        history_cropped, n_gap_months_filled, n_gap_months_rolled, n_gap_months_inferred,
        n_cycle_shift_moves, n_months_truncated, n_dup_month_rows, n_invalid_rows,
        legacy_drop (the old rule would have dropped it), restructure_blind_spot_flag
    """
    require_columns(history, ["account_id", "obs_date", "dlq_bucket"], "A4 history")
    _ship_by_value()
    per_acc = _monthly_rows_per_account(history, scheme, params)

    offset, shift = scheme.offset, params.repair_cycle_shift
    fill, how = params.fill_straight_roll_gaps, params.on_unresolvable_gap
    max_inf = params.max_inferred_gap_months

    def _udf(rows, first_raw, global_min):  # month rows, first month -> history struct
        if first_raw is None:
            return {"build_status": "no_valid_rows"}
        return build_history(
            [(r["m"], r["d"], r["b"]) for r in rows],
            first_raw,
            global_min,
            offset,
            fill,
            how,
            shift,
            max_inf,
        )

    # non-deterministic: Spark then runs the UDF once per row and never copies its
    # output into a join condition (ExtractPythonUDFFromJoinCondition, cross join)
    hist_udf = F.udf(_udf, _HISTORY_SCHEMA).asNondeterministic()
    s = per_acc.withColumn("_h", hist_udf("_rows", "_first_raw", "_global_min"))

    out = s.select(
        "account_id",
        F.col("_h.build_status").alias("build_status"),
        _idx_to_month_end("_h.first_month_idx").alias("first_month"),
        _idx_to_month_end("_h.last_month_idx").alias("last_month"),
        F.size("_h.buckets").alias("history_months"),
        F.col("_h.buckets").alias("dlq_buckets"),
        F.concat_ws("", F.reverse(F.col("_h.buckets").cast("array<string>"))).alias(
            "dpd_string"
        ),
        F.col("_h.history_cropped").alias("history_cropped"),
        F.coalesce("_h.n_gap_months_filled", F.lit(0)).alias("n_gap_months_filled"),
        F.coalesce("_h.n_gap_months_rolled", F.lit(0)).alias("n_gap_months_rolled"),
        F.coalesce("_h.n_gap_months_inferred", F.lit(0)).alias("n_gap_months_inferred"),
        F.coalesce("_h.n_cycle_shift_moves", F.lit(0)).alias("n_cycle_shift_moves"),
        F.coalesce("_h.legacy_drop", F.lit(False)).alias("legacy_drop"),
        F.coalesce("_h.n_months_truncated", F.lit(0)).alias("n_months_truncated"),
        F.coalesce("_h.n_dup_month_rows", F.lit(0)).alias("n_dup_month_rows"),
        F.col("n_invalid_rows").cast("int"),
        (F.col("_rf") if "_rf" in s.columns else F.lit(None).cast("int")).alias("_rf"),
    )
    if restructure is not None:
        out = out.join(
            restructure.select(
                "account_id", F.col("restructure_blind_spot_flag").alias("_rs")
            ),
            "account_id",
            "left",
        )
        flag = F.greatest(F.coalesce("_rf", F.lit(0)), F.coalesce("_rs", F.lit(0)))
    else:
        flag = F.coalesce("_rf", F.lit(0))
    out = out.withColumn("restructure_blind_spot_flag", flag.cast("int")).drop(
        "_rf", "_rs"
    )
    if params.log_stats:
        out = out.persist()
        _log_sequence_stats(out, scheme, params)
    return out


def _spine_rows_with_history(
    sequences: DataFrame, spine: DataFrame, params: JourneyParams
) -> DataFrame:
    """Spine rows (account_id, observation_date) joined to the account's `ok` sequence
    row, kept when the observation month lies in first_month..last_month. Adds
    `_obs_idx` and `_trunc_len`, the number of history months up to that month."""
    end_dt = F.to_date(F.lit(params.end_date))
    seq = (
        sequences.where(F.col("build_status") == "ok")
        .withColumn("_first_idx", _month_col(F.col("first_month")))
        .withColumn("_last_idx", _month_col(F.col("last_month")))
        .withColumn("_key", string_key(sequences))
    )
    sp = spine.where(F.col("observation_date").cast("date") <= end_dt).select(
        string_key(spine).alias("_key"),
        F.col("observation_date").cast("date").alias("observation_date"),
    )

    # join on the safe string key only — account_id in the output keeps seq's own
    # native type (long for CC, string for RL), never the stringified join key.
    obs_idx = _month_col(F.col("observation_date"))
    trunc_len = (obs_idx - F.col("_first_idx") + 1).cast("int")
    return (
        sp.join(seq, "_key", "inner")
        .withColumn("_obs_idx", obs_idx)
        .withColumn("_trunc_len", trunc_len)
        .where((F.col("_trunc_len") >= 1) & (F.col("_obs_idx") <= F.col("_last_idx")))
    )


def build_deterioration(
    sequences: DataFrame,
    scheme: BucketScheme,
    params: JourneyParams,
    spine: DataFrame,
    log_states: bool = True,
) -> DataFrame:
    """Stage 2: spine rows + sequences -> history cut at each row's month -> `classify`.
    sequences: output of build_dpd_sequences (one row per account). spine: 2-column
    (account_id, observation_date) — one row per point-in-time state to classify, e.g.
    cc_spine/rl_spine already filtered to the run's model_id/DLQ-band scope. Classifies
    EVERY spine row, not one row per account: each row's billing history is the account's
    Stage 1 dlq_buckets array truncated up to and including that row's own month, run
    through the same, unmodified classify() engine.

    A spine row is kept only if its month falls inside the account's observed/gap-filled
    window (first_month..last_month) and the truncated bucket is itself delinquent
    (canonical >= 2) — both explainable "no billing history at this date" cases, not a
    silent drop. No model_id/segment bucket-set filter is applied here: that scoping is
    inherited for free from the spine's own population.

    Returns one row per (account_id, observation_date):
        account_id, observation_date, det_state, det_state_label, det_segment,
        current_bucket (native, as of this row's date), <features>, history_months
        (months observed as of this row), history_cropped, n_months_truncated,
        restructure_blind_spot_flag, computed_at
    """
    _ship_by_value()
    segment = params.segment
    offset, top = scheme.offset, scheme.canon_top
    repair = scheme.repair_jumps
    joined = _spine_rows_with_history(sequences, spine, params)

    # in: buckets, truncation length, cropped, blind-spot flag; out: classify struct
    def _udf(buckets, trunc_len_, cropped, restructure_blind_spot):
        sl = list(buckets)[:trunc_len_]
        if not sl or max(sl[-1] + offset, 1) < 2:
            return None
        return classify(
            sl, bool(cropped), offset, top, repair, bool(restructure_blind_spot)
        )

    schema = _CLASSIFY_SCHEMA
    res = joined.withColumn(
        "_s",
        F.udf(_udf, schema).asNondeterministic()(  # once per row, as in Stage 1
            "dlq_buckets",
            "_trunc_len",
            "history_cropped",
            "restructure_blind_spot_flag",
        ),
    ).where(F.col("_s").isNotNull())

    feat_cols = [
        F.col(f"_s.{f.name}").alias(f.name)
        for f in schema.fields
        if f.name != "det_state"
    ]
    out = res.select(
        F.col("account_id"),
        F.col("observation_date"),
        F.col("_s.det_state").alias("det_state"),
        state_label("_s.det_state", DISPLAY_NAMES).alias("det_state_label"),
        F.lit(segment).alias("det_segment"),
        F.element_at("dlq_buckets", F.col("_trunc_len")).alias("current_bucket"),
        F.col("n_gap_months_filled"),
        *feat_cols,
        F.col("_trunc_len").alias("history_months"),
        F.col("history_cropped"),
        F.col("n_months_truncated"),
        F.col("restructure_blind_spot_flag"),
        F.current_timestamp().alias("computed_at"),
    )
    # Always on, as on every axis (_common.log_latest_month); log_stats only gates the
    # Stage 1 telemetry above. The month filter pushes down through the join.
    if log_states:  # False: the caller unions two runs and logs the result
        log_state_stats(out, params.end_date, scheme, params)
    return out
`````

### FILE: `src/enbd_collections/pipelines/crx_persona/b25_check.py`
action: replace · base sha256 `b7c3797f73f93125177c0b654890e35bd5203764c8db69fa45ee0d37aebea7b6` · base trailing newline: yes · new sha256 `f791d5e57e5179351b84deb430153e3af86c917760d9093465f7e12bf01c517d` · new trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````python
"""TEMPORARY (bundle 25): the shipped code rerun next to the persisted outputs.

``crx_<p>_b25_check`` runs the product's pipelines as they ship (CC raw extract, A4, A2,
A1, A3, plus product primaries / features and the bureau features) with every output
renamed ``<name>__b25`` (one catalog pattern, ``tmp_b25_check.yml``), so no real output
is touched; inputs they do not build are the persisted ones. Then it logs, for
``model_id``:

- ``B25 DIFF``: per dataset, rows old / new and rows only on one side (``exceptAll``,
  doubles rounded to 2 decimals). The refactor must give 0; datasets a behaviour step
  changes are marked, with the columns outside that step compared on their own;
- ``B25 A3 EVENTS``: promise events old / new (kind, outcome, 31-day cap, 100 AED floor);
- ``B25 A3 LEVELS``: latest month, Dimension A / B levels, refusal and latest contact
  old x new, refusals lifted by a later payment or plan;
- ``B25 A3 MOVES``: the state step by step: old -> new events and dues (old points, old
  refusal) -> new refusal -> new points (D-A3-33);
- ``B25 A3 DUES``: cards: statements with bucket 08 open and no baseline (no due);
  loans: B-window months with EMI 0 / NULL / > 0;
- ``B25 A1``: latest month, state and family levels old x new, the sweepable balance
  flag, and F1 / F2 / F3 strong (8 cells) with paid a due in the next 3 months;
- ``B25 PARENT LINK`` (cards): what ``parent_contract_id`` links on the card contracts.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b25_check
"""

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.bureau import salary_bounces
from enbd_collections.pipelines.products import features as product_features
from enbd_collections.pipelines.products import primary as product_primary

from . import (
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_raw_extract,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
)
from ._common import GRAIN, window_months
from .a3_credibility.constants import DISPLAY_NAMES, HIGH_FROM, MODERATE_FROM
from .cc_a4_deterioration import pipeline as cc_a4_deterioration

logger = logging.getLogger(__name__)
NEW = "__b25"
TAGS = ["crx_persona", "crx", "b25_check"]
OLD_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}  # before D-A3-33
NEW_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
B_POINTS, C_POINTS = {"regular": 2, "some": 1}, {"clean": 1}
CONTACT_STEP = [  # contact columns D-A3-30 / D-A3-32 may change
    "last_rpc_disposition",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
]


def _parts(product: str) -> list[Pipeline]:
    """The pipelines step 8 reruns for ``product``, in run order."""
    shared = [
        product_primary.create_pipeline(),
        product_features.create_pipeline(),
        salary_bounces.create_pipeline(),
    ]
    if product == "cc":
        axes = [cc_raw_extract, cc_a4_deterioration, cc_a2_locatability]
        axes += [cc_a1_ability, cc_a3_payment_credibility]
    else:
        axes = [rl_a4_deterioration, rl_a2_locatability, rl_a1_ability]
        axes += [rl_a3_payment_credibility]
    return shared + [m.create_pipeline() for m in axes]


def _expected(product: str) -> dict[str, list[str] | None]:
    """Datasets a behaviour step changes: name -> the columns it may change (None =
    every column). Datasets with no old version (new outputs) map to ``[]``."""
    p = f"crx_{product}"
    out: dict[str, list[str] | None] = {
        f"{p}_a3_promise_events": None,
        f"{p}_a3_commitment_signals": None,
        f"{p}_a3_payment_credibility": None,
        f"{p}_a1_ability": None,
        f"{p}_a3_strong_negative_signals": CONTACT_STEP,
        f"{p}_a3_dues": [],
        f"{p}_a3_payments": [],
    }
    if product == "cc":  # D-A3-31 changes card dues at bucket 08
        out["crx_cc_a3_payment_cycles"] = ["due_amount"]
        out["crx_cc_a3_dlq_payment_signals_single_payment_cycle_count"] = None
    return out


# ── Logging helpers ───────────────────────────────────────────────────────────


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], changed_only: bool = False) -> list[str]:
    """``cols`` value counts (``old_x`` / ``new_x`` pairs may be filtered to changes)."""
    if changed_only:
        df = df.filter(~F.col(cols[0]).eqNullSafe(F.col(cols[1])))
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "    " + " | ".join(str(r[c]) for c in cols) + f": {r['count']}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ] or ["    none"]


# ── B25 DIFF ──────────────────────────────────────────────────────────────────


def _comparable(df: DataFrame, cols: list[str]) -> DataFrame:
    """``cols`` with doubles rounded to 2 decimals; map columns cannot be compared."""
    kinds = {f.name: f.dataType for f in df.schema.fields}
    return df.select(
        *[
            (
                F.round(c, 2).alias(c)
                if isinstance(kinds[c], (T.DoubleType, T.FloatType))
                else F.col(c)
            )
            for c in cols
            if not isinstance(kinds[c], T.MapType)
        ]
    )


def _one_sided(old: DataFrame, new: DataFrame, cols: list[str]) -> tuple[int, int]:
    a, b = _comparable(old, cols), _comparable(new, cols)
    return a.exceptAll(b).count(), b.exceptAll(a).count()


def _diff_line(name: str, old: DataFrame, new: DataFrame, step) -> list[str]:
    common = [c for c in new.columns if c in old.columns]
    gone = sorted(set(old.columns) - set(new.columns))
    added = sorted(set(new.columns) - set(old.columns))
    only_old, only_new = _one_sided(old, new, common)
    tag = {False: "refactor, expect 0", None: "behaviour step"}.get(
        step if step is None or step is False else "cols", "behaviour step on columns"
    )
    line = (
        f"  {name} [{tag}]: rows old {old.count()} new {new.count()}; only old "
        f"{only_old}, only new {only_new}"
    )
    lines = [line]
    if gone or added:
        lines.append(f"      columns dropped {gone or '-'}, added {added or '-'}")
    if step:  # the columns outside the behaviour step must match
        rest = [c for c in common if c not in step]
        o, n = _one_sided(old, new, rest)
        lines.append(f"      without {step}: only old {o}, only new {n} (expect 0)")
    return lines


def compare_datasets(model_id: str, names: list[str], expected: dict, **frames) -> None:
    """``B25 DIFF``: every rerun dataset against its persisted version."""
    lines = []
    for i, name in enumerate(names):
        try:
            step = expected.get(name, False)
            lines += _diff_line(name, frames[f"o{i}"], frames[f"n{i}"], step)
        except Exception as err:  # noqa: BLE001  # pylint: disable=broad-except
            lines.append(f"  {name}: FAILED {type(err).__name__}: {err}")
    _block("B25 DIFF", model_id, lines)


# ── A3 ────────────────────────────────────────────────────────────────────────


def _events_lines(events: DataFrame, side: str) -> list[str]:
    days = F.datediff("promise_cutoff", "event_date")
    s = events.agg(
        F.count(F.lit(1)).alias("n"),
        F.sum((days == 31).cast("int")).alias("cap"),
        F.sum((F.col("promise_amount") <= 100).cast("int")).alias("floor"),
    ).collect()[0]
    return [
        (
            f"  {side}: events {s['n']}, deadline 31 days after {s['cap']}, amount at "
            f"the 100 AED floor {s['floor']}"
        ),
        "   kind | outcome:",
    ] + _counts(events, ["event_kind", "promise_outcome"])


def _points(levels: dict[str, int], col: str) -> Column:
    expr = F.lit(0)
    for level, pts in levels.items():
        expr = F.when(F.col(col) == level, F.lit(pts)).otherwise(expr)
    return expr


def _state(a_points: dict[str, int], refusal: str) -> Column:
    """The A3 state from the level columns, ``a_points`` for Dimension A and the
    ``refusal`` flag column (a refusal takes one rung off)."""
    pts = (
        _points(a_points, "a3_commitments_level")
        + _points(B_POINTS, "a3_dlq_payment_level")
        + _points(C_POINTS, "a3_pre_dlq_payment_level")
    )
    rung = F.when(pts >= HIGH_FROM, 2).when(pts >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(
        rung - F.coalesce(F.col(refusal), F.lit(False)).cast("int"), F.lit(0)
    )
    label = (
        F.when(rung == 2, DISPLAY_NAMES["high"])
        .when(rung == 1, DISPLAY_NAMES["moderate"])
        .otherwise(DISPLAY_NAMES["low"])
    )
    return F.when(F.col("episode_start").isNull(), DISPLAY_NAMES["unknown"]).otherwise(
        label
    )


def _dues_lines(ledger: DataFrame, base: DataFrame, model_id: str) -> list[str]:
    if "rl" not in model_id:
        no_due = ledger.filter(F.col("due_amount").isNull())
        return [
            (
                f"  card statements with no due (bucket 08 open, no baseline): "
                f"{no_due.count()} on {no_due.select('account_id').distinct().count()} "
                "accounts"
            ),
        ]
    since = F.add_months(F.col("observation_date"), -window_months(model_id))
    window = base.select("account_id", "observation_date").join(ledger, "account_id")
    window = window.filter(
        (F.col("cycle_end") > since) & (F.col("cycle_end") <= F.col("observation_date"))
    )
    emi = (
        F.when(F.col("due_amount").isNull(), "NULL")
        .when(F.col("due_amount") == 0, "0")
        .otherwise("> 0")
    )
    return ["  loan B-window months by EMI:"] + _counts(
        window.withColumn("emi", emi), ["emi"]
    )


def compare_a3(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old_events: DataFrame,
    new_events: DataFrame,
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A3 EVENTS / LEVELS / MOVES / DUES``."""
    _block(
        "B25 A3 EVENTS",
        model_id,
        _events_lines(old_events, "old") + _events_lines(new_events, "new"),
    )
    cols = [
        "a3_commitments_level",
        "a3_dlq_payment_level",
        "a3_pre_dlq_payment_level",
        "a3_refusal_flag",
        "last_rpc_disposition",
        "a3_state",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols]
    )
    rows = (
        _latest(new, persona_end_date)
        .join(o, list(GRAIN), "left")
        .withColumn("s_events", _state(OLD_POINTS, "old_a3_refusal_flag"))
        .withColumn("s_refusal", _state(OLD_POINTS, "a3_refusal_flag"))
        .withColumn("s_points", _state(NEW_POINTS, "a3_refusal_flag"))
        .localCheckpoint()
    )
    lines = []
    for c in cols[:5]:
        lines += [f"  {c}, old | new (changed rows):"]
        lines += _counts(rows, [f"old_{c}", c], changed_only=True)
    lines += ["  latest contact a refusal: followed by a payment | by a plan:"]
    lines += _counts(
        rows.filter(F.col("last_rpc_disposition") == "refusal"),
        ["refusal_followed_by_payment", "refusal_followed_by_plan"],
    )
    _block("B25 A3 LEVELS", model_id, lines)
    moves = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a3_state"])
    for step, a, b in (
        ("events and dues", "old_a3_state", "s_events"),
        ("refusal", "s_events", "s_refusal"),
        ("points", "s_refusal", "s_points"),
    ):
        moves += [f"  step {step}, from | to (changed rows):"]
        moves += _counts(rows, [a, b], changed_only=True)
    check = rows.filter(~F.col("s_points").eqNullSafe(F.col("a3_state"))).count()
    moves += [
        f"  rows whose recomputed state differs from a3_state: {check} (expect 0)"
    ]
    _block("B25 A3 MOVES", model_id, moves)
    _block(
        "B25 A3 DUES",
        model_id,
        _dues_lines(ledger, _latest(new, persona_end_date), model_id),
    )


# ── A1 ────────────────────────────────────────────────────────────────────────


def _paid_due(base: DataFrame, ledger: DataFrame) -> DataFrame:
    """Per base row: paid a due = payments of the cycles ending in the 3 months after
    the observation date reach max(the latest due on or before it, 100 AED)."""
    obs = F.col("observation_date")
    joined = base.select(*GRAIN).join(ledger, "account_id")
    due = F.max(F.when(F.col("cycle_end") <= obs, F.struct("cycle_end", "due_amount")))[
        "due_amount"
    ]
    paid = F.sum(
        F.when(
            (F.col("cycle_end") > obs) & (F.col("cycle_end") <= F.add_months(obs, 3)),
            F.col("paid_amount"),
        )
    )
    agg = joined.groupBy(*GRAIN).agg(due.alias("_due"), paid.alias("_paid"))
    hit = F.coalesce("_paid", F.lit(0.0)) >= F.greatest(
        F.coalesce("_due", F.lit(0.0)), F.lit(100.0)
    )
    return agg.select(*GRAIN, hit.cast("int").alias("paid_due"))


def compare_a1(  # pylint: disable=too-many-arguments
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A1``: old x new, and F1 / F2 / F3 strong with paid a due."""
    cols = [
        "a1_state",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        "a1_sweepable_balance_flag",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols if c in old.columns]
    )
    rows = _latest(new, persona_end_date).join(o, list(GRAIN), "left").localCheckpoint()
    lines = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a1_state"])
    for c in cols:
        if f"old_{c}" in rows.columns:
            lines += [f"  {c}, old | new (changed rows):"]
            lines += _counts(rows, [f"old_{c}", c], changed_only=True)
        else:
            lines += [f"  {c} (new column):"] + _counts(rows, [c])
    strong = [
        F.coalesce(F.col("a1_income_level") == "stable", F.lit(False))
        .cast("int")
        .alias("f1"),
        F.coalesce(F.col("a1_money_in_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f2"),
        F.coalesce(F.col("a1_money_out_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f3"),
    ]
    lines += ["  F1 | F2 | F3 strong, latest month:"]
    lines += _counts(rows.select(*strong), ["f1", "f2", "f3"])
    end = F.add_months(F.lit(str(persona_end_date)), -3)
    pooled = new.filter(F.col("observation_date") <= end).select(*GRAIN, *strong)
    outcome = pooled.join(_paid_due(pooled, ledger), list(GRAIN), "left")
    rates = (
        outcome.groupBy("f1", "f2", "f3")
        .agg(F.count(F.lit(1)).alias("n"), F.avg("paid_due").alias("rate"))
        .orderBy("f1", "f2", "f3")
        .collect()
    )
    lines += ["  F1 | F2 | F3 strong, pooled months with 3 months after: n, paid a due"]
    lines += [
        f"    {r['f1']} | {r['f2']} | {r['f3']}: {r['n']}, "
        f"{100 * (r['rate'] or 0):.1f}%"
        for r in rates
    ] or ["    none"]
    _block("B25 A1", model_id, lines)


# ── Card parent link (Q-S6-14) ────────────────────────────────────────────────


def _share(part: int, whole: int) -> str:
    return f"{part} ({100 * part / max(whole, 1):.1f}%)"


def compare_parent_link(  # pylint: disable=too-many-locals
    contracts: DataFrame,
    month_end: DataFrame,
    obs_base: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 PARENT LINK``: what ``parent_contract_id`` links on the card contracts."""
    c = contracts.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("contract_id").cast("string").alias("contract_id"),
        F.col("parent_contract_id").cast("string").alias("parent_id"),
    ).localCheckpoint()
    n = c.count()
    parents = c.filter(F.col("parent_id").isNotNull()).select(
        F.col("parent_id").alias("contract_id")
    )
    kids = parents.groupBy("contract_id").count()
    bands = F.when(F.col("count") >= 4, "4+").otherwise(F.col("count").cast("string"))
    pairs = c.filter(F.col("parent_id").isNotNull()).join(
        c.select(
            F.col("contract_id").alias("parent_id"), F.col("cif_id").alias("parent_cif")
        ),
        "parent_id",
        "left",
    )
    n_pairs = pairs.count()
    month = F.last_day(F.lit(str(persona_end_date)))
    live = (
        month_end.filter(F.col("month_end") == month)
        .select(F.col("contract_id").cast("string").alias("contract_id"))
        .distinct()
    )
    both_live = pairs.join(live, "contract_id").join(
        live.withColumnRenamed("contract_id", "parent_id"), "parent_id"
    )
    scored = (
        _latest(obs_base, persona_end_date)
        .select(F.col("account_id").cast("string").alias("contract_id"))
        .distinct()
    )
    n_scored = scored.count()
    named = scored.join(parents.distinct(), "contract_id").count()
    with_parent = scored.join(
        c.filter(F.col("parent_id").isNotNull()).select("contract_id"), "contract_id"
    ).count()
    no_parent_row = pairs.filter(F.col("parent_cif").isNull()).count()
    same_cif = pairs.filter(F.col("cif_id") == F.col("parent_cif")).count()
    lines = [
        (
            f"  card contracts {n}; with a parent {_share(n_pairs, n)}; named as a parent "
            f"{_share(kids.count(), n)}"
        ),
        "  children per parent:",
        *_counts(kids.withColumn("children", bands), ["children"]),
        (
            f"  pairs: parent not a card contract {_share(no_parent_row, n_pairs)}; same CIF "
            f"{_share(same_cif, n_pairs)}; both with a month-end row in the latest month "
            f"{_share(both_live.count(), n_pairs)}"
        ),
        (
            f"  scored accounts {n_scored}: named as a parent {_share(named, n_scored)}; "
            f"with a parent {_share(with_parent, n_scored)}"
        ),
    ]
    _block("B25 PARENT LINK", model_id, lines)


# ── Pipeline ──────────────────────────────────────────────────────────────────


def create_pipeline(product: str, parts: list[Pipeline] | None = None) -> Pipeline:
    """The shipped pipelines into ``<name>__b25``, then the comparisons. ``parts``
    replaces the pipelines rerun (a local test runs one axis at a time)."""
    real = sum(parts if parts is not None else _parts(product), Pipeline([]))
    outputs = sorted(real.all_outputs())
    rerun = pipeline(real, outputs={o: f"{o}{NEW}" for o in outputs})
    expected = _expected(product)
    names = [o for o in outputs if expected.get(o) != []]
    common = {"model_id": "params:model_id"}
    end = {**common, "persona_end_date": "params:crx_persona.persona_end_date"}
    nodes = [
        node(
            func=partial(compare_datasets, names=names, expected=expected),
            inputs={
                **common,
                **{f"o{i}": o for i, o in enumerate(names)},
                **{f"n{i}": f"{o}{NEW}" for i, o in enumerate(names)},
            },
            outputs=None,
            name=f"crx_{product}_b25_diff",
            tags=TAGS,
        )
    ]
    p = f"crx_{product}_a3"
    ledger = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}[product]
    if f"{p}_payment_credibility" in outputs:
        nodes.append(
            node(
                func=compare_a3,
                inputs={
                    "old_events": f"{p}_promise_events",
                    "new_events": f"{p}_promise_events{NEW}",
                    "old": f"{p}_payment_credibility",
                    "new": f"{p}_payment_credibility{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a3",
                tags=TAGS,
            )
        )
    if (
        f"crx_{product}_a1_ability" in outputs
        and f"{ledger}{NEW}" in rerun.all_outputs()
    ):
        nodes.append(
            node(
                func=compare_a1,
                inputs={
                    "old": f"crx_{product}_a1_ability",
                    "new": f"crx_{product}_a1_ability{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a1",
                tags=TAGS,
            )
        )
    if product == "cc" and "prm_card_contracts" in outputs:
        nodes.append(
            node(
                func=compare_parent_link,
                inputs={
                    "contracts": f"prm_card_contracts{NEW}",
                    "month_end": f"prm_card_month_end{NEW}",
                    "obs_base": "crx_cc_obs_base",
                    **end,
                },
                outputs=None,
                name="crx_cc_b25_parent_link",
                tags=TAGS,
            )
        )
    return rerun + Pipeline(nodes)
`````

New:

`````python
"""TEMPORARY (bundle 25): the shipped code rerun next to the persisted outputs.

``crx_<p>_b25_check`` runs the product's pipelines as they ship (CC raw extract, A4, A2,
A1, A3, plus product primaries / features and the bureau features) with every output
renamed ``<name>__b25`` (explicit entries in ``catalog_tmp_b25_check.yml``), so no real
output is touched; inputs they do not build are the persisted ones. Then it logs, for
``model_id``:

- ``B25 DIFF``: per dataset, rows old / new and rows only on one side (``exceptAll``,
  doubles rounded to 2 decimals). The refactor must give 0; datasets a behaviour step
  changes are marked, with the columns outside that step compared on their own;
- ``B25 A3 EVENTS``: promise events old / new (kind, outcome, 31-day cap, 100 AED floor);
- ``B25 A3 LEVELS``: latest month, Dimension A / B levels, refusal and latest contact
  old x new, refusals lifted by a later payment or plan;
- ``B25 A3 MOVES``: the state step by step: old -> new events and dues (old points, old
  refusal) -> new refusal -> new points (D-A3-33);
- ``B25 A3 DUES``: cards: statements with bucket 08 open and no baseline (no due);
  loans: B-window months with EMI 0 / NULL / > 0;
- ``B25 A1``: latest month, state and family levels old x new, the sweepable balance
  flag, and F1 / F2 / F3 strong (8 cells) with paid a due in the next 3 months;
- ``B25 PARENT LINK`` (cards): what ``parent_contract_id`` links on the card contracts.

Removed by the bundle's cleanup.

    kedro run --pipeline=crx_<p>_b25_check
"""

import logging
from functools import partial

from kedro.pipeline import Pipeline, node, pipeline
from pyspark.sql import Column, DataFrame
from pyspark.sql import functions as F
from pyspark.sql import types as T

from enbd_collections.pipelines.bureau import salary_bounces
from enbd_collections.pipelines.products import features as product_features
from enbd_collections.pipelines.products import primary as product_primary

from . import (
    cc_a1_ability,
    cc_a2_locatability,
    cc_a3_payment_credibility,
    cc_raw_extract,
    rl_a1_ability,
    rl_a2_locatability,
    rl_a3_payment_credibility,
    rl_a4_deterioration,
)
from ._common import GRAIN, window_months
from .a3_credibility.constants import DISPLAY_NAMES, HIGH_FROM, MODERATE_FROM
from .cc_a4_deterioration import pipeline as cc_a4_deterioration

logger = logging.getLogger(__name__)
NEW = "__b25"
TAGS = ["crx_persona", "crx", "b25_check"]
OLD_POINTS = {"kept": 2, "partly_kept": 1, "broken": -1}  # before D-A3-33
NEW_POINTS = {"kept": 3, "partly_kept": 2, "broken": 1, "promised": 1}
B_POINTS, C_POINTS = {"regular": 2, "some": 1}, {"clean": 1}
CONTACT_STEP = [  # contact columns D-A3-30 / D-A3-32 may change
    "last_rpc_disposition",
    "a3_refusal_flag",
    "refusal_followed_by_plan",
    "refusal_followed_by_payment",
    "a3_dispute_flag",
    "a3_hung_up_last",
]


def _parts(product: str) -> list[Pipeline]:
    """The pipelines step 8 reruns for ``product``, in run order."""
    shared = [
        product_primary.create_pipeline(),
        product_features.create_pipeline(),
        salary_bounces.create_pipeline(),
    ]
    if product == "cc":
        axes = [cc_raw_extract, cc_a4_deterioration, cc_a2_locatability]
        axes += [cc_a1_ability, cc_a3_payment_credibility]
    else:
        axes = [rl_a4_deterioration, rl_a2_locatability, rl_a1_ability]
        axes += [rl_a3_payment_credibility]
    return shared + [m.create_pipeline() for m in axes]


def _expected(product: str) -> dict[str, list[str] | None]:
    """Datasets a behaviour step changes: name -> the columns it may change (None =
    every column). Datasets with no old version (new outputs) map to ``[]``."""
    p = f"crx_{product}"
    out: dict[str, list[str] | None] = {
        f"{p}_a3_promise_events": None,
        f"{p}_a3_commitment_signals": None,
        f"{p}_a3_payment_credibility": None,
        f"{p}_a1_ability": None,
        f"{p}_a3_strong_negative_signals": CONTACT_STEP,
        f"{p}_a3_dues": [],
        f"{p}_a3_payments": [],
    }
    if product == "cc":  # D-A3-31 changes card dues at bucket 08
        out["crx_cc_a3_payment_cycles"] = ["due_amount"]
        out["crx_cc_a3_dlq_payment_signals_single_payment_cycle_count"] = None
    return out


# ── Logging helpers ───────────────────────────────────────────────────────────


def _block(name: str, model_id: str, lines: list[str]) -> None:
    body = "\n".join([f"  model_id {model_id}", *lines])
    logger.info("\n=== %s START ===\n%s\n=== %s END ===", name, body, name)


def _latest(df: DataFrame, persona_end_date: str) -> DataFrame:
    month = F.trunc(F.lit(str(persona_end_date)), "month")
    return df.filter(F.trunc("observation_date", "month") == month)


def _counts(df: DataFrame, cols: list[str], changed_only: bool = False) -> list[str]:
    """``cols`` value counts (``old_x`` / ``new_x`` pairs may be filtered to changes)."""
    if changed_only:
        df = df.filter(~F.col(cols[0]).eqNullSafe(F.col(cols[1])))
    total = max(df.count(), 1)
    rows = df.groupBy(*cols).count().orderBy(*cols).collect()
    return [
        "    " + " | ".join(str(r[c]) for c in cols) + f": {r['count']}"
        f" ({100 * r['count'] / total:.1f}%)"
        for r in rows
    ] or ["    none"]


# ── B25 DIFF ──────────────────────────────────────────────────────────────────


def _comparable(df: DataFrame, cols: list[str]) -> DataFrame:
    """``cols`` with doubles rounded to 2 decimals; map columns cannot be compared."""
    kinds = {f.name: f.dataType for f in df.schema.fields}
    return df.select(
        *[
            (
                F.round(c, 2).alias(c)
                if isinstance(kinds[c], (T.DoubleType, T.FloatType))
                else F.col(c)
            )
            for c in cols
            if not isinstance(kinds[c], T.MapType)
        ]
    )


def _one_sided(old: DataFrame, new: DataFrame, cols: list[str]) -> tuple[int, int]:
    a, b = _comparable(old, cols), _comparable(new, cols)
    return a.exceptAll(b).count(), b.exceptAll(a).count()


def _diff_line(name: str, old: DataFrame, new: DataFrame, step) -> list[str]:
    common = [c for c in new.columns if c in old.columns]
    gone = sorted(set(old.columns) - set(new.columns))
    added = sorted(set(new.columns) - set(old.columns))
    only_old, only_new = _one_sided(old, new, common)
    tag = {False: "refactor, expect 0", None: "behaviour step"}.get(
        step if step is None or step is False else "cols", "behaviour step on columns"
    )
    line = (
        f"  {name} [{tag}]: rows old {old.count()} new {new.count()}; only old "
        f"{only_old}, only new {only_new}"
    )
    lines = [line]
    if gone or added:
        lines.append(f"      columns dropped {gone or '-'}, added {added or '-'}")
    if step:  # the columns outside the behaviour step must match
        rest = [c for c in common if c not in step]
        o, n = _one_sided(old, new, rest)
        lines.append(f"      without {step}: only old {o}, only new {n} (expect 0)")
    return lines


def compare_datasets(model_id: str, names: list[str], expected: dict, **frames) -> None:
    """``B25 DIFF``: every rerun dataset against its persisted version."""
    lines = []
    for i, name in enumerate(names):
        try:
            step = expected.get(name, False)
            lines += _diff_line(name, frames[f"o{i}"], frames[f"n{i}"], step)
        except Exception as err:  # noqa: BLE001  # pylint: disable=broad-except
            lines.append(f"  {name}: FAILED {type(err).__name__}: {err}")
    _block("B25 DIFF", model_id, lines)


# ── A3 ────────────────────────────────────────────────────────────────────────


def _events_lines(events: DataFrame, side: str) -> list[str]:
    days = F.datediff("promise_cutoff", "event_date")
    s = events.agg(
        F.count(F.lit(1)).alias("n"),
        F.sum((days == 31).cast("int")).alias("cap"),
        F.sum((F.col("promise_amount") <= 100).cast("int")).alias("floor"),
    ).collect()[0]
    return [
        (
            f"  {side}: events {s['n']}, deadline 31 days after {s['cap']}, amount at "
            f"the 100 AED floor {s['floor']}"
        ),
        "   kind | outcome:",
    ] + _counts(events, ["event_kind", "promise_outcome"])


def _points(levels: dict[str, int], col: str) -> Column:
    expr = F.lit(0)
    for level, pts in levels.items():
        expr = F.when(F.col(col) == level, F.lit(pts)).otherwise(expr)
    return expr


def _state(a_points: dict[str, int], refusal: str) -> Column:
    """The A3 state from the level columns, ``a_points`` for Dimension A and the
    ``refusal`` flag column (a refusal takes one rung off)."""
    pts = (
        _points(a_points, "a3_commitments_level")
        + _points(B_POINTS, "a3_dlq_payment_level")
        + _points(C_POINTS, "a3_pre_dlq_payment_level")
    )
    rung = F.when(pts >= HIGH_FROM, 2).when(pts >= MODERATE_FROM, 1).otherwise(0)
    rung = F.greatest(
        rung - F.coalesce(F.col(refusal), F.lit(False)).cast("int"), F.lit(0)
    )
    label = (
        F.when(rung == 2, DISPLAY_NAMES["high"])
        .when(rung == 1, DISPLAY_NAMES["moderate"])
        .otherwise(DISPLAY_NAMES["low"])
    )
    return F.when(F.col("episode_start").isNull(), DISPLAY_NAMES["unknown"]).otherwise(
        label
    )


def _dues_lines(ledger: DataFrame, base: DataFrame, model_id: str) -> list[str]:
    if "rl" not in model_id:
        no_due = ledger.filter(F.col("due_amount").isNull())
        return [
            (
                f"  card statements with no due (bucket 08 open, no baseline): "
                f"{no_due.count()} on {no_due.select('account_id').distinct().count()} "
                "accounts"
            ),
        ]
    since = F.add_months(F.col("observation_date"), -window_months(model_id))
    window = base.select("account_id", "observation_date").join(ledger, "account_id")
    window = window.filter(
        (F.col("cycle_end") > since) & (F.col("cycle_end") <= F.col("observation_date"))
    )
    emi = (
        F.when(F.col("due_amount").isNull(), "NULL")
        .when(F.col("due_amount") == 0, "0")
        .otherwise("> 0")
    )
    return ["  loan B-window months by EMI:"] + _counts(
        window.withColumn("emi", emi), ["emi"]
    )


def compare_a3(  # pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-locals
    old_events: DataFrame,
    new_events: DataFrame,
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A3 EVENTS / LEVELS / MOVES / DUES``."""
    _block(
        "B25 A3 EVENTS",
        model_id,
        _events_lines(old_events, "old") + _events_lines(new_events, "new"),
    )
    cols = [
        "a3_commitments_level",
        "a3_dlq_payment_level",
        "a3_pre_dlq_payment_level",
        "a3_refusal_flag",
        "last_rpc_disposition",
        "a3_state",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols]
    )
    rows = (
        _latest(new, persona_end_date)
        .join(o, list(GRAIN), "left")
        .withColumn("s_events", _state(OLD_POINTS, "old_a3_refusal_flag"))
        .withColumn("s_refusal", _state(OLD_POINTS, "a3_refusal_flag"))
        .withColumn("s_points", _state(NEW_POINTS, "a3_refusal_flag"))
        .localCheckpoint()
    )
    lines = []
    for c in cols[:5]:
        lines += [f"  {c}, old | new (changed rows):"]
        lines += _counts(rows, [f"old_{c}", c], changed_only=True)
    lines += ["  latest contact a refusal: followed by a payment | by a plan:"]
    lines += _counts(
        rows.filter(F.col("last_rpc_disposition") == "refusal"),
        ["refusal_followed_by_payment", "refusal_followed_by_plan"],
    )
    _block("B25 A3 LEVELS", model_id, lines)
    moves = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a3_state"])
    for step, a, b in (
        ("events and dues", "old_a3_state", "s_events"),
        ("refusal", "s_events", "s_refusal"),
        ("points", "s_refusal", "s_points"),
    ):
        moves += [f"  step {step}, from | to (changed rows):"]
        moves += _counts(rows, [a, b], changed_only=True)
    check = rows.filter(~F.col("s_points").eqNullSafe(F.col("a3_state"))).count()
    moves += [
        f"  rows whose recomputed state differs from a3_state: {check} (expect 0)"
    ]
    _block("B25 A3 MOVES", model_id, moves)
    _block(
        "B25 A3 DUES",
        model_id,
        _dues_lines(ledger, _latest(new, persona_end_date), model_id),
    )


# ── A1 ────────────────────────────────────────────────────────────────────────


def _paid_due(base: DataFrame, ledger: DataFrame) -> DataFrame:
    """Per base row: paid a due = payments of the cycles ending in the 3 months after
    the observation date reach max(the latest due on or before it, 100 AED)."""
    obs = F.col("observation_date")
    joined = base.select(*GRAIN).join(ledger, "account_id")
    due = F.max(F.when(F.col("cycle_end") <= obs, F.struct("cycle_end", "due_amount")))[
        "due_amount"
    ]
    paid = F.sum(
        F.when(
            (F.col("cycle_end") > obs) & (F.col("cycle_end") <= F.add_months(obs, 3)),
            F.col("paid_amount"),
        )
    )
    agg = joined.groupBy(*GRAIN).agg(due.alias("_due"), paid.alias("_paid"))
    hit = F.coalesce("_paid", F.lit(0.0)) >= F.greatest(
        F.coalesce("_due", F.lit(0.0)), F.lit(100.0)
    )
    return agg.select(*GRAIN, hit.cast("int").alias("paid_due"))


def compare_a1(  # pylint: disable=too-many-arguments
    old: DataFrame,
    new: DataFrame,
    ledger: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 A1``: old x new, and F1 / F2 / F3 strong with paid a due."""
    cols = [
        "a1_state",
        "a1_income_level",
        "a1_money_in_level",
        "a1_money_out_level",
        "a1_cross_product_level",
        "a1_sweepable_balance_flag",
    ]
    o = _latest(old, persona_end_date).select(
        *GRAIN, *[F.col(c).alias(f"old_{c}") for c in cols if c in old.columns]
    )
    rows = _latest(new, persona_end_date).join(o, list(GRAIN), "left").localCheckpoint()
    lines = [f"  rows {rows.count()}", "  new state:"] + _counts(rows, ["a1_state"])
    for c in cols:
        if f"old_{c}" in rows.columns:
            lines += [f"  {c}, old | new (changed rows):"]
            lines += _counts(rows, [f"old_{c}", c], changed_only=True)
        else:
            lines += [f"  {c} (new column):"] + _counts(rows, [c])
    strong = [
        F.coalesce(F.col("a1_income_level") == "stable", F.lit(False))
        .cast("int")
        .alias("f1"),
        F.coalesce(F.col("a1_money_in_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f2"),
        F.coalesce(F.col("a1_money_out_level") == "strong", F.lit(False))
        .cast("int")
        .alias("f3"),
    ]
    lines += ["  F1 | F2 | F3 strong, latest month:"]
    lines += _counts(rows.select(*strong), ["f1", "f2", "f3"])
    end = F.add_months(F.lit(str(persona_end_date)), -3)
    pooled = new.filter(F.col("observation_date") <= end).select(*GRAIN, *strong)
    outcome = pooled.join(_paid_due(pooled, ledger), list(GRAIN), "left")
    rates = (
        outcome.groupBy("f1", "f2", "f3")
        .agg(F.count(F.lit(1)).alias("n"), F.avg("paid_due").alias("rate"))
        .orderBy("f1", "f2", "f3")
        .collect()
    )
    lines += ["  F1 | F2 | F3 strong, pooled months with 3 months after: n, paid a due"]
    lines += [
        f"    {r['f1']} | {r['f2']} | {r['f3']}: {r['n']}, "
        f"{100 * (r['rate'] or 0):.1f}%"
        for r in rates
    ] or ["    none"]
    _block("B25 A1", model_id, lines)


# ── Card parent link (Q-S6-14) ────────────────────────────────────────────────


def _share(part: int, whole: int) -> str:
    return f"{part} ({100 * part / max(whole, 1):.1f}%)"


def compare_parent_link(  # pylint: disable=too-many-locals
    contracts: DataFrame,
    month_end: DataFrame,
    obs_base: DataFrame,
    model_id: str,
    persona_end_date: str,
) -> None:
    """``B25 PARENT LINK``: what ``parent_contract_id`` links on the card contracts."""
    c = contracts.select(
        F.col("cif_id").cast("string").alias("cif_id"),
        F.col("contract_id").cast("string").alias("contract_id"),
        F.col("parent_contract_id").cast("string").alias("parent_id"),
    ).localCheckpoint()
    n = c.count()
    parents = c.filter(F.col("parent_id").isNotNull()).select(
        F.col("parent_id").alias("contract_id")
    )
    kids = parents.groupBy("contract_id").count()
    bands = F.when(F.col("count") >= 4, "4+").otherwise(F.col("count").cast("string"))
    pairs = c.filter(F.col("parent_id").isNotNull()).join(
        c.select(
            F.col("contract_id").alias("parent_id"), F.col("cif_id").alias("parent_cif")
        ),
        "parent_id",
        "left",
    )
    n_pairs = pairs.count()
    month = F.last_day(F.lit(str(persona_end_date)))
    live = (
        month_end.filter(F.col("month_end") == month)
        .select(F.col("contract_id").cast("string").alias("contract_id"))
        .distinct()
    )
    both_live = pairs.join(live, "contract_id").join(
        live.withColumnRenamed("contract_id", "parent_id"), "parent_id"
    )
    scored = (
        _latest(obs_base, persona_end_date)
        .select(F.col("account_id").cast("string").alias("contract_id"))
        .distinct()
    )
    n_scored = scored.count()
    named = scored.join(parents.distinct(), "contract_id").count()
    with_parent = scored.join(
        c.filter(F.col("parent_id").isNotNull()).select("contract_id"), "contract_id"
    ).count()
    no_parent_row = pairs.filter(F.col("parent_cif").isNull()).count()
    same_cif = pairs.filter(F.col("cif_id") == F.col("parent_cif")).count()
    lines = [
        (
            f"  card contracts {n}; with a parent {_share(n_pairs, n)}; named as a parent "
            f"{_share(kids.count(), n)}"
        ),
        "  children per parent:",
        *_counts(kids.withColumn("children", bands), ["children"]),
        (
            f"  pairs: parent not a card contract {_share(no_parent_row, n_pairs)}; same CIF "
            f"{_share(same_cif, n_pairs)}; both with a month-end row in the latest month "
            f"{_share(both_live.count(), n_pairs)}"
        ),
        (
            f"  scored accounts {n_scored}: named as a parent {_share(named, n_scored)}; "
            f"with a parent {_share(with_parent, n_scored)}"
        ),
    ]
    _block("B25 PARENT LINK", model_id, lines)


# ── Pipeline ──────────────────────────────────────────────────────────────────


def create_pipeline(product: str, parts: list[Pipeline] | None = None) -> Pipeline:
    """The shipped pipelines into ``<name>__b25``, then the comparisons. ``parts``
    replaces the pipelines rerun (a local test runs one axis at a time)."""
    real = sum(parts if parts is not None else _parts(product), Pipeline([]))
    outputs = sorted(real.all_outputs())
    rerun = pipeline(real, outputs={o: f"{o}{NEW}" for o in outputs})
    expected = _expected(product)
    names = [o for o in outputs if expected.get(o) != []]
    common = {"model_id": "params:model_id"}
    end = {**common, "persona_end_date": "params:crx_persona.persona_end_date"}
    nodes = [
        node(
            func=partial(compare_datasets, names=names, expected=expected),
            inputs={
                **common,
                **{f"o{i}": o for i, o in enumerate(names)},
                **{f"n{i}": f"{o}{NEW}" for i, o in enumerate(names)},
            },
            outputs=None,
            name=f"crx_{product}_b25_diff",
            tags=TAGS,
        )
    ]
    p = f"crx_{product}_a3"
    ledger = {"cc": "crx_cc_a3_payment_cycles", "rl": "crx_rl_a3_dlq_cycles"}[product]
    if f"{p}_payment_credibility" in outputs:
        nodes.append(
            node(
                func=compare_a3,
                inputs={
                    "old_events": f"{p}_promise_events",
                    "new_events": f"{p}_promise_events{NEW}",
                    "old": f"{p}_payment_credibility",
                    "new": f"{p}_payment_credibility{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a3",
                tags=TAGS,
            )
        )
    if (
        f"crx_{product}_a1_ability" in outputs
        and f"{ledger}{NEW}" in rerun.all_outputs()
    ):
        nodes.append(
            node(
                func=compare_a1,
                inputs={
                    "old": f"crx_{product}_a1_ability",
                    "new": f"crx_{product}_a1_ability{NEW}",
                    "ledger": f"{ledger}{NEW}",
                    **end,
                },
                outputs=None,
                name=f"crx_{product}_b25_a1",
                tags=TAGS,
            )
        )
    if product == "cc" and "prm_card_contracts" in outputs:
        nodes.append(
            node(
                func=compare_parent_link,
                inputs={
                    "contracts": f"prm_card_contracts{NEW}",
                    "month_end": f"prm_card_month_end{NEW}",
                    "obs_base": "crx_cc_obs_base",
                    **end,
                },
                outputs=None,
                name="crx_cc_b25_parent_link",
                tags=TAGS,
            )
        )
    return rerun + Pipeline(nodes)
`````

### FILE: `conf/base/catalog/tmp_b25_check.yml`
action: delete · base sha256 `a1556ab0a3f23c849267fb8d09d6ddbfc6448b10f9fd3e30bda1c0a22a253728` · base trailing newline: yes

Base (as photographed — used only for the safety check and --revert):

`````yaml
# TEMPORARY (bundle 25): every dataset crx_<p>_b25_check reruns, saved as <name>__b25;
# this file and the HDFS folder b25_check are removed by the cleanup.

"{name}__b25":
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/b25_check/{name}"
  save_args:
    mode: overwrite
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
Clean up after mirror bundle 27_b25_check_fix.md, on the bundle's branch.
This replaces bundle 25's cleanup (run it once, after bundle 25's step 8 and after the A3 results snippet has read the `__b25` copies).

- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the path from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for each of the four model_ids (skip folders that do not exist): `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/b25_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundles 25 / 27):
  - delete `conf/base/catalog/catalog_tmp_b25_check.yml` (and `tmp_b25_check.yml` if it is still there);
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_b25_check` / `crx_rl_b25_check` entries, their comment line and the `b25_check` import;
  - delete `src/enbd_collections/pipelines/crx_persona/b25_check.py`.
- **Retired snippets that no longer import** (from finished validation prompts): delete `tmp_validation/a1_high_whatif/`, `a1_aecb_whatif/`, `a1_bureau_fill/`, `a1_bureau_unified/`, `a1_payment_cure/`, `a1_bulk_pull/`, `a1_casa_accounts/`, `a3_detail/`, `a3_v1h/`, `a3_v1i/`, `a3_v1_v4/`, `a3_check_new/` (whichever exist); list any other `tmp_validation/` folder without deleting it.
- Delete `data/input/mirror_bundles/`.

  Then check that `kedro registry list` still works and that `grep -rn "b25" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
````
