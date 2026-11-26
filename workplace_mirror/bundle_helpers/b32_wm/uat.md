**Step 4.** Ask Sonnet the following, in one go, and fix what it finds before committing:

> **Goal.** The WM `04_feature` snapshot tables we read load one `adv_load_date` partition through the bundle's new dataset `enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset`. If that partition can't be read, they fall back to a neighbouring one. Read the module docstring first.
>
> **Decisions already made (don't revisit):**
> - Switch these four entries in `conf/base/catalog/catalog_casa_plus_ftr.yml`: `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_fea_salary_days_since_increment`, `wm_fea_wealth_holdings_by_cif` (if that one lives in another catalog file, switch it there). Each becomes:
>   ```yaml
>   type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
>   filepath: <the table's folder root, without any /adv_load_date=... suffix>
>   snapshot: "${globals:snapshot_adv_load_date}"
>   required_from: "${globals:wm_snapshot_required_from}"
>   required_through: "${globals:crx_persona.persona_end_date}"
>   ```
>   Keep any existing `load_args` and `metadata`. Drop `file_format: parquet` and `save_args`: parquet is the default and the dataset is read-only.
> - `wm_fea_casa_eod_avg_balance` today points at the folder root, so it reads every partition. That is how the damaged `adv_load_date=2026-06-02` partition (`BlockMissingException` on `part-00007`) broke the run. Pinning it to one snapshot is intended.
> - In `conf/dev/globals_dev.yml`, add right under `snapshot_adv_load_date` (keep every other value exactly as it is now, including the dates the user set):
>   ```yaml
>   # Earliest month any WM snapshot consumer reads: persona_start_date minus 11 months
>   # (products history_months 12). Update with persona_start_date.
>   wm_snapshot_required_from: "<persona_start_date minus 11 months, first of month>"
>   ```
>   Work the value out from the current `crx_persona.persona_start_date` and say what you used.
>
> **Hard rules:** change nothing else in the catalogs or globals. Never run `hdfs fsck -delete` / `-move` or anything else that writes to WM paths. Node code keeps reading through node inputs.
>
> **Deliverables in your reply:**
> 1. Each switched entry, before → after. Also list (don't switch) any other catalog entry under `wealth_management/04_feature/` or with `adv_load_date` in its path.
> 2. Every top-level key the apply added or removed in `src/enbd_collections/pipeline_registry.py` and `conf/base/catalog/*.yml`, compared with the last commit. Expected: the registry adds the `b32_check` import plus `casa_b32_snapshot` and `casa_b32_compare` (the `crx_master` import and the four `*.persona_e2e` entries stay, whether or not they are committed yet); the catalog adds `catalog_tmp_b32_check.yml` (`casa_b32_old_balance`); nothing removed. Put back anything else that went missing, and make sure no key appears twice across `conf/base/catalog/*.yml`.
> 3. `src/enbd_collections/datasets/__init__.py` exists. `python -c "import enbd_collections.datasets.wm_snapshot_dataset, enbd_collections.pipeline_registry"` imports. `kedro registry list` shows `casa_b32_snapshot` and `casa_b32_compare`. `kedro catalog list` (or a `DataCatalog.from_config` of the four entries) builds the datasets without error.
> 4. Unit tests for `WMSnapshotDataset.candidates` (order and cap) and the coverage rule (`coverage_problem` on a small DataFrame), in the existing test style; they pass. black, ruff and pylint clean on the touched files.
