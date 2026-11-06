**Step 7.** Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`. `crx_rl_a4_spine` from the last run is the baseline. Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a4_spine_ra_check
```

Paste back the block from `=== RA SPINE OUTPUT START ===` to `=== RA SPINE OUTPUT END ===`. Expected: the same rows old and new, `same schema: True`, 0 rows only in old and 0 only in new.

**Step 8.** Nothing else to run: no live output changes. Go on with the next bundle (the refactor) once the block is back.
