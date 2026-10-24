- HDFS first (the user runs these in PROD; UAT has no data): resolve the catalog paths
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check`
  for model_id cc_60_180 and cc_180_plus, and
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b03_check`
  for cc_60_180, from the workplace conf, and write out the three commands in full, e.g.
  `hdfs dfs -rm -r <resolved path>`.
- Remove the temporary check (everything marked TEMPORARY for bundle 03):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b01_check` and
    `crx_cc_a1_ability_b03_check` entries and their TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_cc_a1_ability_b03_check"` entry and
    its comment;
  - crx_persona/cc_a1_ability_v2/pipeline.py: `create_b03_check_pipeline`, the imports of
    `create_cc_obs_pipeline` and `b03_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/cc_a1_ability_v2/__init__.py: the `create_b03_check_pipeline` export;
  - delete crx_persona/cc_a1_ability_v2/b03_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b01\|b03" src conf` prints
  nothing.
- Delete the validation folder `tmp_validation/a1_v01/` (git rm; leave any other
  tmp_validation folder alone).
