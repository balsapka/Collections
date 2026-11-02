Set `model_id: rl_60_180` in `conf/dev/globals_dev.yml`, persona dates unchanged. Switch it back when you are done. `int_loan_master` and `int_loan_restructure_link` must already be built from the fixed history.

**Step 6.** Rebuild the history from the fixed source:

```bash
kedro run --env=dev --pipeline=crx_rl_full_history
```

**Step 7.** Run the check (`crx_rl_a4_deterioration` must still be the old output, so do not run step 8 first):

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration_b11_check
```

Paste back every block from `=== B11 … START ===` to `=== B11 … END ===`: `OUTPUT`, `ECL`, `CHAIN`, `UNKNOWN`. Aggregates only. Text is best; otherwise one photo per block.

**Step 8.** Only after the B11 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a4_deterioration
```

For `rl_180_plus`, repeat steps 6–8 with that `model_id` if A4 has been run for it.
