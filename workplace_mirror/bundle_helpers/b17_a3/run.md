Bundles 15 and 16 must be applied and their checks back. The A3 output from the last real run is the baseline: do not re-run A3 before the check. Run for **`rl_60_180`**, then **`cc_60_180`** (set `model_id` in `conf/dev/globals_dev.yml`). `crx_<p>_obs_base` and `crx_<p>_a4_deterioration` must be current for the model_id (bundle 16 step 11 for 180+).

**Step 7.** Run the check (it reads the current CC raw extracts as they are):

```bash
kedro run --env=dev --pipeline=crx_rl_a3_check
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_check
```

Paste back every block from `=== A3 … START ===` to `=== A3 … END ===` (5 per model_id). A summary file is fine.

**Step 8.** Only after the blocks are reviewed and the judge is chosen (`a3_kept_by` in `parameters_crx_persona.yml`): write the real output. CC first rebuilds the raw extracts on the new window:

```bash
kedro run --env=dev --pipeline=crx_cc_raw_extract
```

```bash
kedro run --env=dev --pipeline=crx_cc_a3_payment_credibility
```

```bash
kedro run --env=dev --pipeline=crx_rl_a3_payment_credibility
```

For every model_id you score (all four). Then the cleanup prompt.
