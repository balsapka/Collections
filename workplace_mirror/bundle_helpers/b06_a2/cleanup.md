- HDFS first (the user runs this in PROD; UAT has no data): resolve these catalog paths
  for model_id cc_60_180 **and** rl_60_180 from the workplace conf and write out each
  command in full, `hdfs dfs -rm -r <resolved path>`:
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_a2_locatability_b06_check` (cc_60_180)
  - `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_rl_a2_locatability_b06_check` (rl_60_180)
  - the retired old A2 intermediates, for the model_id of their prefix:
    `crx_cc_a2_base`, `crx_cc_a2_login_presence`, `crx_cc_a2_contact_signals` (cc_60_180),
    `crx_rl_a2_base`, `crx_rl_a2_login_presence`, `crx_rl_a2_contact_signals` (rl_60_180),
    each under `${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/`.
- Remove the temporary check (everything marked TEMPORARY for bundle 06):
  - conf/base/catalog/catalog_crx.yml: the `crx_cc_a2_locatability_b06_check` and
    `crx_rl_a2_locatability_b06_check` entries and their TEMPORARY comments;
  - src/enbd_collections/pipeline_registry.py: the two `*_a2_locatability_b06_check`
    entries and their comments;
  - crx_persona/a2_locatability/pipeline.py: `create_b06_check_pipeline`, the imports of
    `create_location_pipeline`, `create_cc_obs_pipeline`, `create_rl_obs_pipeline` and
    `b06_check`, and the TEMPORARY paragraph of the module docstring;
  - crx_persona/cc_a2_locatability/ and rl_a2_locatability/: `create_b06_check_pipeline`
    in `pipeline.py` (+ its import and TEMPORARY docstring paragraph) and in `__init__.py`;
  - delete crx_persona/a2_locatability/b06_check.py.
  Then check: `kedro registry list` still works and `grep -rn "b06" src conf` prints nothing.
- Delete the folder data/input/mirror_bundles/ (bundle file, apply script):
  rm -rf data/input/mirror_bundles
- Run `git status`: only the files named above may have changed, nothing under
  data/input/ is tracked or staged. Commit src/ and conf/ and push. Report what
  you removed and the hdfs commands the user still has to run in PROD.
