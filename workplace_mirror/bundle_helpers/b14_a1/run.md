Run steps 6–8 for **`rl_60_180`**, then **`cc_60_180`**: set `model_id` in
`conf/dev/globals_dev.yml`, with the persona dates unchanged. The 180+ model_ids are optional for the
check, but step 6 and step 8 must run for every model_id you score (all four). Switch back when you
are done.

**Step 6.** Rebuild the inputs. First the CASA primaries (this writes the new `prm_casa_accounts`):

```bash
kedro run --env=dev --pipeline=casa_primary
```

Then the alert primary, with the command Sonnet gave you in step 4. Then the features:

```bash
kedro run --env=dev --pipeline=bureau_salary_bounces
```

```bash
kedro run --env=dev --pipeline=casa_features
```

**Step 7.** Run the check. It compares with the current real output, so do not run step 8 yet. For RL:

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability_b14_check
```

For CC:

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b14_check
```

Paste back every block from `=== B14 … START ===` to `=== B14 … END ===`: `OUTPUT`, `ACCOUNTS`,
`BOUNCES`. A summary file like the last ones is fine.

**Step 8.** Only after the B14 blocks have been reviewed: write the real output.

```bash
kedro run --env=dev --pipeline=crx_rl_a1_ability
```

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability
```
