First, if you have not yet, run `bundle_helpers/a1_final/sonnet_a1_date_gaps_prompt.md`. If it finds
gaps in a source other than the alerts, send its summary back before going on.

Run steps 6–8 for **`cc_60_180`** (the default in `conf/dev/globals_dev.yml`), then for
**`rl_60_180`** (set `model_id: rl_60_180`, persona dates unchanged). Switch back when you are done.
180+ is not needed.

**Step 6.** Rebuild the alerts with the command Sonnet gave you in step 4, then the bureau features:

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

No CASA or salary rerun is needed: this bundle does not change them, and they are already built for
both model_ids, unless the date check found gaps there.

**Step 7.** Run the check (it reads the current real output, so do not run step 8 yet). For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b12_check
```

For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b12_check
```

Paste back every block from `=== B12 … START ===` to `=== B12 … END ===`: `OUTPUT`, `REPORT`,
`SOURCES`, `AECB`. A summary file like the last ones is fine.

**Step 8.** Only after the B12 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```
