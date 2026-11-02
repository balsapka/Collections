**Before this:** bundle 11's step 8 must be done, so `crx_rl_a4_deterioration` is the baseline. Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`, and make sure `feature_retail_loans` is built for it.

**Step 6.** Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration_b13_check
```

Paste back every block from `=== B13 … START ===` to `=== B13 … END ===`: `OUTPUT`, `RESTRUCTURE`, `UNKNOWN`. Aggregates only. Text is best; otherwise one photo per block.

**Step 7.** Only after the B13 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration
```
