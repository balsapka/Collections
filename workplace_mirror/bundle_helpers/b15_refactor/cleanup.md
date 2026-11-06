- **HDFS first.** The user runs these in PROD; UAT has no data. Resolve the catalog path pattern `${_project.hdfs_path}/<model_id>/${globals:folders.persona}/crx/<dataset>` from the workplace conf and write out each command in full, `hdfs dfs -rm -r <resolved path>`. Skip any folder that does not exist.
  - The check output, for `rl_60_180`: `crx_rl_a4_spine_ra_check`.
  - The removed CC datasets, for `cc_60_180` and `cc_180_plus`: `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_cc_departure_signature`, `crx_cc_departure_spell_base`, `crx_cc_departure_contract_cif`, `crx_cc_departure_pass_a`, `_b`, `_c`, `_d`, `_e`, `_f`, `_g`, `_h`, `_h2`, `_i`, `_j`, `_k`.
  - The removed RL datasets, for `rl_60_180` and `rl_180_plus`: `crx_rl_departure_signature`, `crx_rl_depart_travel_mcc`, `crx_rl_depart_foreign_signals`.
- **Remove the temporary check** (everything marked TEMPORARY for refactor bundle R-A):
  - `conf/base/catalog/catalog_crx.yml`: the `crx_rl_a4_spine_ra_check` entry and its comments;
  - `src/enbd_collections/pipeline_registry.py`: the `crx_rl_a4_spine_ra_check` entry and its comment;
  - `crx_persona/rl_a4_spine/pipeline.py`: `create_ra_check_pipeline`, the `ra_check` import and the TEMPORARY docstring paragraph (keep `_spine_node`);
  - `crx_persona/rl_a4_spine/__init__.py`: `create_ra_check_pipeline`;
  - delete `crx_persona/rl_a4_spine/ra_check.py`.

  Then check that `kedro registry list` still works and that `grep -rn "ra_check" src conf` prints nothing.
