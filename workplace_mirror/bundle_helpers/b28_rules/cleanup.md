Run once, after step 8's blocks are pasted back.

- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the path from the workplace conf and write out `hdfs dfs -rm -r <resolved path>` in full for each of the four model_ids (skip folders that do not exist): `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/b28_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundle 28):
  - delete `conf/base/catalog/catalog_tmp_b28_check.yml`;
  - `src/enbd_collections/pipeline_registry.py`: the four `crx_<p>_b28_snapshot` / `crx_<p>_b28_compare` entries, their comment line and the `b28_check` import;
  - delete `src/enbd_collections/pipelines/crx_persona/b28_check.py`.
- Delete `data/input/mirror_bundles/`.

  Then check that `kedro registry list` still works and that `grep -rn "b28" src conf` prints nothing.
