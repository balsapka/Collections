- Remove the temporary check (everything marked TEMPORARY for bundle 01):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b01_check` entry and its
    TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_cc_a1_ability_b01_check"` entry;
  - crx_persona/cc_a1_ability_v2/pipeline.py: `create_b01_check_pipeline`, the imports of
    `create_cc_obs_pipeline` and `b01_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/cc_a1_ability_v2/__init__.py: the `create_b01_check_pipeline` export;
  - delete crx_persona/cc_a1_ability_v2/b01_check.py.
  Then check: `kedro registry list` still works and no file mentions `b01`
  (`grep -rn b01 src conf` prints nothing).
- HDFS (the user runs this in PROD; UAT has no data): resolve the catalog path
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b01_check`
  from the workplace conf for model_id cc_60_180 and cc_180_plus, and write out the two
  commands in full, e.g. `hdfs dfs -rm -r <resolved path>`. Do this before removing the
  catalog entry.
