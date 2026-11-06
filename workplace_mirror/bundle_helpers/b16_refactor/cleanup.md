- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, for every model_id a check ran for (CC datasets for the CC model_ids, RL for RL). Skip folders that do not exist: `crx_<p>_full_history_rf_check`, `crx_<p>_a4_deterioration_rf_check`, `crx_<p>_obs_base_rf_check`, `crx_<p>_a2_locatability_rf_check`, `crx_<p>_a1_ability_rf_check`.
- **Remove the temporary checks** (everything marked TEMPORARY for refactor bundle R-B):
  - `conf/base/catalog/catalog_crx.yml`: the ten `*_rf_check` entries and their comment block;
  - `src/enbd_collections/pipeline_registry.py`: the `rf_check` import with its comment, and the six `crx_<p>_<axis>_rf_check` entries with their comment;
  - delete `src/enbd_collections/pipelines/crx_persona/rf_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "rf_check" src conf` prints nothing.
