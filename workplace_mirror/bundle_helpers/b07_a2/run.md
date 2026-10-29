Only the log nodes are run for CC; everything upstream is already written.
First **`cc_60_180`** (the default), then **`rl_60_180`** (full bundle 06 step 7, since RL has
not run yet). Switch `model_id` back to `cc_60_180` when done.

**Step 6.** CC — run the three log nodes (everything upstream is already written):

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check --nodes "compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules,explain_crx_cc_a2_b06_reach"
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

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: CC `OUTPUT`,
`RULES` and `REACH` (DEBIT already received); RL `OUTPUT`, `RULES`, `REACH`, `DEBIT`, `PRODUCT`. Then continue with
bundle 06 step 8 and its cleanup only after the review.
