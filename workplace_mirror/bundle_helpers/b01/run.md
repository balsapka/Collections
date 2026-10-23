**Step 9.** Run the check pipeline (terminal). It builds `crx_cc_obs_base`, the A1 signals and
anchor, writes the new A1 output to the **temporary** dataset `crx_cc_a1_ability_b01_check`
(the current `crx_cc_a1_ability_v2` is read, never overwritten), then logs two blocks:

```bash
kedro run --pipeline=crx_cc_a1_ability_b01_check
```

Paste back everything from `=== B01 SALARY START ===` to `=== B01 SALARY END ===` and from
`=== B01 OUTPUT START ===` to `=== B01 OUTPUT END ===` (aggregates only, no customer rows).

**Step 10.** Repeat step 9 for the other CC segment: in `conf/dev/globals_dev.yml` switch
`model_id` from `cc_60_180` to `cc_180_plus`, run step 9 again, paste both blocks, then
switch `model_id` back (do not commit this switch):

```bash
git diff --stat conf/dev/globals_dev.yml
```

(must print nothing once `model_id` is switched back).
