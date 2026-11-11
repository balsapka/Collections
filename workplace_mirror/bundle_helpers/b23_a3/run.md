Bundle 20's real A3 output is the baseline: do not re-run A3 before the check. Run the check for **`rl_60_180` and `cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`); 180+ only if wanted.

**Step 7.** Run the check:

```bash
kedro run --env=dev --pipeline=crx_rl_a3_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back every block from `=== A3 … START ===` to `=== A3 … END ===` (3 per model_id). A summary file is fine.

**Step 8.** Only once the change is agreed: write the real output for **all four model_ids**:

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

Then the cleanup prompt. If the change is not agreed, skip step 8 and ask for a revert bundle instead.
