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
