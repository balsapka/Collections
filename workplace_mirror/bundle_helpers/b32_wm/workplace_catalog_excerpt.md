# Workplace `catalog_casa_plus_ftr.yml` after the bundle 32 UAT step (excerpt, 2026-11-26)

Editor lines 95–119 only; the other three switched entries, the globals line and Sonnet's report were not shown.

```yaml
# Excerpt of conf/base/catalog/catalog_casa_plus_ftr.yml, editor lines 95-119
# (line 96 is partly cut off; 97 not visible). Terminal pane below the editor:
#   "The pkill pattern matched my own shell, so that exit was self-inflicted. I'll rerun the check."
#   "Ran 2 shell commands"   ("1 new message (ctrl+End)" overlay)

# 95  # WM CPR-RELATED FEATURE DATASETS (product holdings, balance, surplus, AUM)
# 96  # ====================================================================== (ruler, length approximate)

# wm_fea_non_wealth_product_holding: unpinned — real per-row date column not
# confirmed (R9); do not assume full-history-per-partition without checking.
wm_fea_non_wealth_product_holding:
  type: spark.SparkDataset
  filepath: "hdfs://cdpprod/data/aacoe/adv/enbd/wealth_management/04_feature/fea_non_wealth_product_holding_by_cif"
  file_format: parquet

# wm_fea_casa_eod_avg_balance is deliberately unpinned on adv_load_date — see
# rl_a1_ability/nodes.py build_rl_a1_group_b_income_obs_anchored docstring.
wm_fea_casa_eod_avg_balance:
  type: enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset
  filepath: "hdfs://cdpprod/data/aacoe/adv/enbd/wealth_management/04_feature/fea_casa_eod_avg_bal_by_cif"
  snapshot: "${globals:snapshot_adv_load_date}"
  required_from: "${globals:wm_snapshot_required_from}"
  required_through: "${globals:crx_persona.persona_end_date}"

# wm_fea_casa_wealth_surplus: unpinned — real per-row date column not confirmed (R9).
wm_fea_casa_wealth_surplus:
  type: spark.SparkDataset
  filepath: "hdfs://cdpprod/data/aacoe/adv/enbd/wealth_management/04_feature/fea_casa_eod_balances_wealth_surplus"
  file_format: parquet
```
