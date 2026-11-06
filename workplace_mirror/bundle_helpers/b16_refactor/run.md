The outputs from the last real run are the baseline: do not re-run any axis before the checks. Run for **`rl_60_180`**, then **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`). Order matters only for reading: A4 first.

**Step 8.** A4 (the full history is rebuilt inside the check):

```bash
kedro run --env=dev --pipeline=crx_rl_a4_rf_check
```

**Step 9.** A2:

```bash
kedro run --env=dev --pipeline=crx_rl_a2_rf_check
```

While it runs, open the Spark UI and note the shuffle read and spill of the stage that builds the A2 DCORE signals.

**Step 10.** A1 (also rebuilds the obs base and logs the join-key check):

```bash
kedro run --env=dev --pipeline=crx_rl_a1_rf_check
```

Then the same three for CC: `crx_cc_a4_rf_check`, `crx_cc_a2_rf_check`, `crx_cc_a1_rf_check`.

Paste back every block from `=== RF … START ===` to `=== RF … END ===` (8 per model_id), plus the A2 DCORE stage's shuffle read and spill. Expected: `rows only in old: 0`, `rows only in new: 0`, every state crosstab on the diagonal. In `RF A2 DCORE`, a non-attempt share over 50% or a spilling stage is worth flagging; in `RF STRING KEYS`, any padded count above 0.

**Step 11.** Only after the RF blocks have been reviewed: write the real outputs for the 180+ model_ids as usual (`crx_<p>_a4_deterioration`, `crx_<p>_a2_locatability`, `crx_<p>_a1_ability`). The 60–180 outputs need no re-run (identical by the check). Then go on with the A3 bundle.
