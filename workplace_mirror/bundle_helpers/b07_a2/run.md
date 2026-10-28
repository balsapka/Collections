Only the two log nodes that did not run are re-run; everything upstream is already written.
First **`cc_60_180`** (the default), then **`rl_60_180`** (full bundle 06 step 7, since RL has
not run yet). Switch `model_id` back to `cc_60_180` when done.

**Step 6.** CC — resume the two comparison nodes:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check --from-nodes "compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules"
```

**Step 7.** RL (`model_id: rl_60_180`) — bundle 06 steps 6 and 7 (logins and CASA primaries
for RL, then the full check):

```bash
kedro run --env=dev --pipeline=digital_login
```

```bash
kedro run --env=dev --pipeline=casa_primary
```

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check
```

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: CC `OUTPUT` and
`RULES` (DEBIT already received); RL `OUTPUT`, `RULES`, `DEBIT`, `PRODUCT`. Then continue with
bundle 06 step 8 and its cleanup only after the review.
