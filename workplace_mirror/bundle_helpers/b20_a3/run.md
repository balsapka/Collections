Bundle 17's real A3 output is the baseline: do not re-run A3 before the check. Run for **all four model_ids** (`rl_60_180`, `cc_60_180`, `rl_180_plus`, `cc_180_plus`; set `model_id` in `conf/dev/globals_dev.yml`).

**Step 7.** Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a3_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back every block from `=== A3 … START ===` to `=== A3 … END ===` (4 per model_id). A summary file is fine.

**Step 8.** After the blocks are reviewed: write the real output (no raw extract rebuild needed):

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

For every model_id. Then the cleanup prompt.
