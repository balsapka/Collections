- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve these catalog paths from the
  workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`, once for
  every model_id the check ran for:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b14_check`;
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b14_check`.
- **Remove the temporary check** (everything marked TEMPORARY for bundle 14):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_cc_a1_ability_b14_check` and
    `crx_rl_a1_ability_b14_check` entries and their TEMPORARY comments;
  - `src/enbd_collections/pipeline_registry.py`: the two `*_a1_ability_b14_check` entries and their
    comments;
  - `crx_persona/a1_ability/pipeline.py`: `create_b14_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b14_check`, and the TEMPORARY paragraph of
    the module docstring;
  - `crx_persona/cc_a1_ability/` and `rl_a1_ability/`: `create_b14_check_pipeline` in `pipeline.py`
    (with its import and the TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete `crx_persona/a1_ability/b14_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "b14" src conf` prints nothing.
- **Delete the bundle folder** `data/input/mirror_bundles/` (the bundle file and the apply script):
  `rm -rf data/input/mirror_bundles`
- **Finish.** Run `git status`: only the files named above may have changed, and nothing under
  `data/input/` may be tracked or staged. Commit `src/` and `conf/` and push. Report what you removed
  and the hdfs commands the user still has to run in PROD.
