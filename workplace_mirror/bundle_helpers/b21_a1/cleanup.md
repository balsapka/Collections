- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id (CC datasets for the CC model_ids, RL for RL); skip folders that do not exist: `crx_<p>_a1_check_new` and the retired `crx_<p>_a1_liquidity_signals`.
- **Remove the temporary check** (everything marked TEMPORARY for A1 bundle 21):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_<p>_a1_check_new` entries and their comments;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_a1_check` and `crx_rl_a1_check` entries and their comments;
  - `crx_persona/cc_a1_ability/` and `rl_a1_ability/`: `create_check_pipeline` in `pipeline.py` (with its import) and in `__init__.py`;
  - delete `crx_persona/a1_ability/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "a1_check" src conf` prints nothing.
