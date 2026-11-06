**Step 7.** Re-run the CC check of bundle 17 (`model_id: cc_60_180`); the RL check does not read this entry, so its blocks stand:

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back the 5 `A3 …` blocks, as for bundle 17.
