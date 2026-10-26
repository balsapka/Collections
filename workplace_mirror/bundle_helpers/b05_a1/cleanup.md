- HDFS first (the user runs this in PROD; UAT has no data): resolve the catalog path
  `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b05_check`
  for model_id rl_60_180 from the workplace conf, and write out the command in full,
  `hdfs dfs -rm -r <resolved path>`.
- Remove the temporary check (everything marked TEMPORARY for bundle 05):
  - conf/base/catalog/catalog_crx.yml: the `crx_rl_a1_ability_b05_check` entry and its
    TEMPORARY comment;
  - src/enbd_collections/pipeline_registry.py: the `"crx_rl_a1_ability_b05_check"` entry and
    its comment;
  - crx_persona/rl_a1_ability_v2/pipeline.py: `create_b05_check_pipeline`, the imports of
    `create_rl_obs_pipeline` and `b05_check`, and the TEMPORARY paragraph of the module
    docstring;
  - crx_persona/rl_a1_ability_v2/__init__.py: the `create_b05_check_pipeline` export;
  - delete crx_persona/rl_a1_ability_v2/b05_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b05" src conf` prints nothing.
