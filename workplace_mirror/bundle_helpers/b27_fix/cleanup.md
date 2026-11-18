This replaces bundle 25's cleanup (run it once, after bundle 25's step 8 and after the A3 results snippet has read the `__b25` copies).

- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the path from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for each of the four model_ids (skip folders that do not exist): `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/b25_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundles 25 / 27):
  - delete `conf/base/catalog/catalog_tmp_b25_check.yml` (and `tmp_b25_check.yml` if it is still there);
  - `src/enbd_collections/pipeline_registry.py`: the `crx_cc_b25_check` / `crx_rl_b25_check` entries, their comment line and the `b25_check` import;
  - delete `src/enbd_collections/pipelines/crx_persona/b25_check.py`.
- **Retired snippets that no longer import** (from finished validation prompts): delete `tmp_validation/a1_high_whatif/`, `a1_aecb_whatif/`, `a1_bureau_fill/`, `a1_bureau_unified/`, `a1_payment_cure/`, `a1_bulk_pull/`, `a1_casa_accounts/`, `a3_detail/`, `a3_v1h/`, `a3_v1i/`, `a3_v1_v4/`, `a3_check_new/` (whichever exist); list any other `tmp_validation/` folder without deleting it.
- Delete `data/input/mirror_bundles/`.

  Then check that `kedro registry list` still works and that `grep -rn "b25" src conf` prints nothing.
