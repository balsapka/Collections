# Sonnet prompt (UAT): tidy the bundle 32 catalog switch

Paste everything below the line into the workplace Sonnet (UAT, branch with bundle 32 applied).

---

**Goal.** Finish the bundle 32 catalog switch cleanly. The WM `04_feature` snapshot tables we read load one `adv_load_date` partition through `enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset`, and the catalog comments say what the entries do now.

**Decisions already made (don't revisit):**
- `wm_fea_casa_eod_avg_balance` is pinned to one snapshot on purpose. The comment above it in `conf/base/catalog/catalog_casa_plus_ftr.yml` ("deliberately unpinned on adv_load_date — see rl_a1_ability/nodes.py build_rl_a1_group_b_income_obs_anchored docstring") is stale: that function belonged to the RL A1 waterfall, which was removed. Replace the comment with exactly:
  ```yaml
  # One adv_load_date snapshot (globals), with fallback to a neighbouring partition when
  # that one cannot be read in full (WMSnapshotDataset; bundle 32).
  ```
- The same four entries use the dataset: `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_fea_salary_days_since_increment`, `wm_fea_wealth_holdings_by_cif`. Each has `filepath` = the table's folder root (no `/adv_load_date=...` suffix), `snapshot: "${globals:snapshot_adv_load_date}"`, `required_from: "${globals:wm_snapshot_required_from}"`, `required_through: "${globals:crx_persona.persona_end_date}"`. They have no `file_format` or `save_args`. Any `load_args` / `metadata` they had before stay.
- Any other comment above those four entries that talks about pinning, `adv_load_date` or the old waterfall gets the same replacement text.
- `wm_fea_non_wealth_product_holding`, `wm_fea_casa_wealth_surplus` and any other WM entry stay as they are. No persona code reads them.

**Hard rules:**
- Edit only the comments and entries named above, plus `wm_snapshot_required_from` in `conf/dev/globals_dev.yml` if it is missing or wrong.
- Keep every other globals value exactly as it is, including the dates the user set.
- Never write to WM HDFS paths. No `hdfs fsck -delete` / `-move`.
- Don't use `pkill` / `kill` patterns broad enough to match your own shell or a running `kedro` process.

**Deliverables in your reply:**
1. Each of the four entries as it stands now, with the comment above it, and any change you made (before → after).
2. The `wm_snapshot_required_from` line in `globals_dev.yml`, the current `crx_persona.persona_start_date`, and whether the value equals persona start minus 11 months (first of month). Fix it if not.
3. `python -c "import enbd_collections.datasets.wm_snapshot_dataset, enbd_collections.pipeline_registry"` imports. A `DataCatalog.from_config` of the four entries (with the project's globals resolved) builds without error.
4. `git status` and `git diff --stat`. Commit `conf` only, with message `Bundle 32: catalog comments and WM snapshot entries tidied`, and push.
