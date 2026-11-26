**What this bundle does.** WM `04_feature` tables are read from one `adv_load_date` partition (the `snapshot_adv_load_date` global). If that partition can't be read, the load falls back to a neighbouring one. **Apply on top of bundles 25–31 and their cleanups.** No persona logic changes.

- **Why.** `wm_fea_casa_eod_avg_balance` points at the folder root in `catalog_casa_plus_ftr.yml`. Spark therefore read **every** partition, whatever the global said. One block of `part-00007` in `adv_load_date=2026-06-02` has no reachable replica (`BlockMissingException`; NameNode still lists replicas on `10.229.163.35` / `.87`). Every scan that touches it fails. The table belongs to WM, so we can't repair it. Its sibling entries are already pinned to one partition.
- **New dataset** `enbd_collections.datasets.wm_snapshot_dataset.WMSnapshotDataset` (read-only):
  - Reads `<root>/adv_load_date=<snapshot>`.
  - First it scans the whole partition once (Spark `noop` sink). HDFS can list a file it cannot serve, so the listing alone proves nothing.
  - If the partition is missing, unreadable, or its `week_number` range misses the `required_from` / `required_through` months, it tries newer partitions (nearest first), then older ones. At most `max_fallback` (3) are tried.
  - A fallback is logged as a warning naming the partition used and why the others were refused. When nothing qualifies, the load fails with each reason.
  - Every load logs the week range it got.
- **Catalog (UAT step 4, Sonnet).** `catalog_casa_plus_ftr.yml` is not in the mirror, so Sonnet switches the four WM entries we read: `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_fea_salary_days_since_increment`, `wm_fea_wealth_holdings_by_cif`. It also adds the global `wm_snapshot_required_from`.
- **Temporary check:** `pipelines/casa/b32_check.py`, `catalog_tmp_b32_check.yml` and 3 registry lines. It snapshots the persisted `feat_cif_casa_balance_monthly` (built from all partitions), then compares it with the one rebuilt from the single snapshot, per month: rows only old / only new / both, share of equal balances, size of the differences, `casa_flow` disagreements.

Tested in the mirror:
- Spec test `checks/wm_snapshot_spec.py` (local Spark, 11 cases): healthy snapshot, missing snapshot, damaged part files (they open, but the scan fails), fallback order, coverage refusals, failure message, read-only.
- Check module run on toy data.
- Smoke check at baseline (the 6 known `cc_raw_extract` lines).
- black, ruff and pylint clean on the touched files.
