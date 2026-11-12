- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve `${_project.hdfs_path}/<model_id>/${globals:folders.feat}/products/cif_cross_product_monthly_b24_new` from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for every model_id the check ran on (skip folders that do not exist).
- **Remove the temporary check** (everything marked TEMPORARY for bundle 24):
  - `conf/base/catalog/catalog_products.yml`: the `feat_cif_cross_product_monthly_b24_new` entry and its comment;
  - `src/enbd_collections/pipeline_registry.py`: the `product_features_b24_check` entry;
  - `src/enbd_collections/pipelines/products/features.py`: `create_b24_check_pipeline`;
  - delete `src/enbd_collections/pipelines/products/check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "b24" src conf` prints nothing.
