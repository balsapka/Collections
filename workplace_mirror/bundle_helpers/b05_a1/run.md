Run everything for **`rl_60_180`**: set `model_id: rl_60_180` in
`conf/dev/globals_dev.yml` (persona dates unchanged, dev 2026-01 to 2026-08). Switch it
back to `cc_60_180` when you are done.

**Step 6.** Build `prm_casa_return_events` for the RL namespace (it is stored per
`model_id`, so the CC build does not cover RL):

```bash
kedro run --env=dev --pipeline=casa_primary
```

**Step 7.** Run the check pipeline (observation base + RL A1 into the temporary
`crx_rl_a1_ability_b05_check`, then the comparison with the waterfall):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b05_check
```

It reads the waterfall's existing output `crx_rl_a1_ability`. If it stops with
`PATH_NOT_FOUND` on that dataset, send the error back (the waterfall then has to run first).

Paste back the two blocks, each from `=== B05 … START ===` to `=== B05 … END ===`:
`B05 OUTPUT` (waterfall vs engine states, levels, EMI anchor coverage) and `B05 INCOME`
(what the `feature_retail_loans` salary adds). Aggregates only. Text is best; otherwise
one photo per block.

**Step 8.** Only after the B05 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_v2
```
