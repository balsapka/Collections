`WMSnapshotDataset`: `required_from` warns instead of refusing.

WM keeps a rolling history (about two years): the 2026-10-02 partition of `fea_casa_cc_inflow_outflow_by_cif` starts at week 20241001, so with `wm_snapshot_required_from` = 2024-02-01 every partition was refused and `casa_features` stopped. Now a partition whose weeks start after the `required_from` month is used, with a warning (`weeks start at <first>, later than the requested month <yyyyMM>; the months before are empty`). `required_through` still refuses an older snapshot that stops before the run's last month.

One file changes: `src/enbd_collections/datasets/wm_snapshot_dataset.py`. No catalog, globals or registry change. Bundle 32's check pipelines and cleanup stay as they are.
