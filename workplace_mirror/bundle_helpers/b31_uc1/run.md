**Step 7.** In PROD, after the pull, for each model_id (`cc_60_180`, `rl_60_180`, then `cc_180_plus`, `rl_180_plus`; switch `model_id` in `globals_dev.yml`), with `<p>` = cc or rl:

```bash
kedro run --pipeline=crx_<p>_b31_snapshot
```

```bash
kedro run --pipeline=crx_<p>_uc1_stated
```

```bash
kedro run --pipeline=crx_<p>_b31_compare
```

The snapshot must run before the new block overwrites the old one. A1 and A3 outputs are read as persisted (no rerun needed). Paste back the four blocks `=== B31 ROWS / B31 DIST / B31 OLD NEW / B31 PAID … START/END ===` per model_id (180+: ROWS and DIST are enough if UC1 has no 180+ customers). Then the cleanup prompt.
