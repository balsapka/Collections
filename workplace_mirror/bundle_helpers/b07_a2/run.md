Only the log nodes are re-run; everything upstream is already written (the earlier runs stopped
at the comparison node). First **`cc_60_180`** (the default), then **`rl_60_180`**. Switch
`model_id` back to `cc_60_180` when done.

**Step 6.** CC — the three log nodes:

```bash
kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check --nodes "compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules,explain_crx_cc_a2_b06_reach"
```

**Step 7.** RL (`model_id: rl_60_180`) — the log nodes, including the debit and product blocks:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check --nodes "compare_crx_rl_a2_b06,describe_crx_rl_a2_b06_rules,explain_crx_rl_a2_b06_reach,describe_crx_rl_a2_b06_debit,split_crx_rl_a2_b06_product"
```

Paste back every block from `=== B06 … START ===` to `=== B06 … END ===`: CC `OUTPUT`,
`RULES` and `REACH` (DEBIT already received); RL `OUTPUT`, `RULES`, `REACH`, `DEBIT`, `PRODUCT`. Then continue with
bundle 06 step 8 and its cleanup only after the review.
