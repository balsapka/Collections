**Step 4.** The tests are yours to update (the bundle does not touch them): remove `ecl_gap_blind_spot_flag`, `ecl_gap_blind_spot`, `ecl_gap_cutoff_date` and `rl_ecl_gap_cutoff_date` from `src/tests/pipelines/crx_persona/` (schemas, fixtures, tests of the rule) and `disbursement_date` / `product_code` from the `crx_rl_full_history` schema. Keep the rest passing.

If `ECL_WINNOWED_PRODUCT_CODES` in `stg_rr_portf.py` has no other use and the source no longer works that way, remove it and its comment; the bundle leaves that file alone because the history fix may have changed it.

Then this must print nothing except `b11_check.py` and that constant if you kept it (otherwise stop and send the output back):

```bash
grep -rnE "ecl_gap|ECL_WINNOWED" src conf --include='*.py' --include='*.yml'
```

A `dpd_journey.rl_ecl_gap_cutoff_date` key left in any parameters file would now stop the run with "unknown parameter(s)": remove it if the grep shows one.

`kedro registry list | grep a4_deterioration` lists `crx_cc_a4_deterioration`, `crx_rl_a4_deterioration` and `crx_rl_a4_deterioration_b11_check`.
