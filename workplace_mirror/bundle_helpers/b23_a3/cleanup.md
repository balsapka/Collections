- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id (CC datasets for the CC model_ids, RL for RL); skip folders that do not exist: the check outputs `crx_<p>_a3_check_new`, `crx_<p>_a3_check_old`.
- **Remove the temporary check** (everything marked TEMPORARY for A3 bundle 23):
  - `conf/base/catalog/catalog_crx.yml`: the four `crx_<p>_a3_check_*` entries and their comment block;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_a3_check` and `crx_rl_a3_check` entries and their comments;
  - `crx_persona/cc_a3_payment_credibility/` and `rl_a3_payment_credibility/`: `create_check_pipeline` in `pipeline.py` (with its import and the TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete `crx_persona/a3_credibility/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "a3_check" src conf` prints nothing.
