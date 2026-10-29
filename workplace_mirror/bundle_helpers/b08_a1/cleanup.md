- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths
  for model_id cc_60_180 **and** rl_60_180 from the workplace conf and write out each
  command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b08_check` and `.../crx_cc_a1_ability_v2` (cc_60_180)
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b08_check` and `.../crx_rl_a1_ability_v2` (rl_60_180)
  - the retired intermediates under `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/`:
    `crx_cc_a1_internal_returns`, `crx_cc_a1_base`, `crx_cc_a1_cif_enriched`,
    `crx_cc_a1_group_b_income`, `crx_cc_a1_group_b_income_recent`, `crx_cc_a1_group_b_bureau`,
    `crx_cc_a1_group_b_bureau_recent`, `crx_cc_a1_group_c`, `crx_cc_a1_group_c_recent`
    (cc_60_180); `crx_rl_a1_internal_returns`, `crx_rl_a1_group_a`,
    `crx_rl_a1_group_b_income_recent`, `crx_rl_a1_group_b_bureau_recent`,
    `crx_rl_a1_group_c_recent`, `crx_rl_a1_group_d` (rl_60_180). Skip any that does not exist.
- Remove the temporary check (everything marked TEMPORARY for bundle 08):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_v2`, `crx_cc_a1_ability_b08_check`,
    `crx_rl_a1_ability_v2` and `crx_rl_a1_ability_b08_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a1_ability_b08_check` entries and
    their comments;
  - crx_persona/a1_ability/pipeline.py: `create_b08_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b08_check`, and the TEMPORARY
    paragraph of the module docstring;
  - crx_persona/cc_a1_ability/ and rl_a1_ability/: `create_b08_check_pipeline` in
    `pipeline.py` (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a1_ability/b08_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b08\|a1_ability_v2" src conf`
  prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
