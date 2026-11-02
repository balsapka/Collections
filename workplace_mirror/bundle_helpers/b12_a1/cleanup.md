- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths from the
  workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a1_ability_b12_check` (cc_60_180);
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a1_ability_b12_check` (rl_60_180).
- Remove the temporary check (everything marked TEMPORARY for bundle 12):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a1_ability_b12_check` and
    `crx_rl_a1_ability_b12_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a1_ability_b12_check` entries and comments;
  - crx_persona/a1_ability/pipeline.py: `create_b12_check_pipeline`, the imports of
    `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and `b12_check`, and the TEMPORARY paragraph
    of the module docstring;
  - crx_persona/cc_a1_ability/ and rl_a1_ability/: `create_b12_check_pipeline` in `pipeline.py`
    (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a1_ability/b12_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b12" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under data/input/ is
  tracked or staged. Commit src/ and conf/ and push. Report what you removed and the hdfs commands
  the user still has to run in PROD.
