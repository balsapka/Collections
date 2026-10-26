Same `model_id` (`cc_60_180`) and persona dates as bundle 03. `prm_casa_return_events` is
already built (bundle 03 Step 7), so it is not rerun.

**Step 6.** Rerun the bundle 03 check pipeline:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b03_check
```

Paste back the `B03 OUTPUT` and `B03 INCOME` blocks (from `=== B03 … START ===` to
`=== B03 … END ===`). Then continue with bundle 03 Step 9 only after they have been
reviewed.
