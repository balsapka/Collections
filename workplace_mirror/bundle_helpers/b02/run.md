**Step 8.** Run the check pipeline (terminal), first for `cc_60_180` (the `model_id` in
`conf/dev/globals_dev.yml`):

```bash
kedro run --env=dev --pipeline=crx_cc_a1_ability_b01_check
```

Paste back the three blocks, each from `=== B01 … START ===` to `=== B01 … END ===`:
`B01 DISTRESS`, `B01 SALARY` and `B01 OUTPUT` (aggregates only, no customer rows). Text is
best, if you can copy it out; otherwise one photo per block.

**Step 9.** Same for `cc_180_plus`: in `conf/dev/globals_dev.yml` switch `model_id` from
`cc_60_180` to `cc_180_plus`, run step 8 again, paste the three blocks, then switch
`model_id` back (do not commit this switch). This must print nothing afterwards:

```bash
git diff --stat conf/dev/globals_dev.yml
```
