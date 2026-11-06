**Step 4.** Print the Spark version (the A2 rewrite needs 3.1 or later):

```bash
python -c "import pyspark; print(pyspark.__version__)"
```

**Step 5.** Ask Sonnet the following, in one go:

1. **Tests.** Run the crx_persona test modules and update the ones the new signatures and names break (the list is in the bundle's "Changes you will see": `build_a1_ability`, `build_liquidity_signals`, `build_rl_full_history`, `episode_start`, `StateLadder` → `Scorecard`, the renamed symbols). Behaviour must not change: fix the test calls, never the expected values. Report any test whose expected value would have to change.
2. **Other readers of renamed symbols.** `grep -rn` over `src` for `StateLadder`, `points_from_level`, `_window_start`, `_string_key`, `_log_state_stats`, `_month_label` outside crx_persona. Report hits; do not change them.
3. **Tags.** `grep -rn` over the repo's run scripts / docs for `--tags` using `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`, `cc` or `rl` with the persona pipelines. Report hits.

Then check: `kedro registry list | grep rf_check` lists the six `crx_<cc|rl>_<a4|a2|a1>_rf_check` pipelines.
