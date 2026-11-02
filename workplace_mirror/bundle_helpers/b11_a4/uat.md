**Step 4.** First read `nodes/intermediate/retail_loans/int_loan_restructure_link.py` and its catalog entry. The mirror has neither, so `rl_a4_deterioration/nodes.py` guesses two column names: set `_LINK_ACCOUNT` (the restructured account) and `_LINK_ORIGINAL` (the predecessor) to the real ones. Confirm `restr_flagged_date`, `orig_close_date`, `match_type`, `candidate_count`, that `int_loan_restructure_link` is the catalog name and that `int_loan_master` has `account_status`. Change nothing else; if one of these differs in meaning, stop and send it back.

The tests are yours to update (the bundle does not touch them): remove `ecl_gap_blind_spot_flag`, `ecl_gap_blind_spot`, `ecl_gap_cutoff_date` and `rl_ecl_gap_cutoff_date` from `src/tests/pipelines/crx_persona/` (schemas, fixtures, tests of the rule) and `disbursement_date` / `product_code` from the `crx_rl_full_history` schema, and add the `chain_*` columns to the `crx_rl_a4_deterioration` schema. Tests calling `build_rl_a4_deterioration` need its new inputs. Add tests for `chains.py::resolve_chains`. Keep the rest passing.

If `ECL_WINNOWED_PRODUCT_CODES` in `stg_rr_portf.py` has no other use and the source no longer works that way, remove it and its comment; the bundle leaves that file alone because the history fix may have changed it.

Then this must print nothing except `b11_check.py` and that constant if you kept it (otherwise stop and send the output back):

```bash
grep -rnE "ecl_gap|ECL_WINNOWED" src conf --include='*.py' --include='*.yml'
```

A `dpd_journey.rl_ecl_gap_cutoff_date` key left in any parameters file would now stop the run with "unknown parameter(s)": remove it if the grep shows one.

`kedro registry list | grep a4_deterioration` lists `crx_cc_a4_deterioration`, `crx_rl_a4_deterioration` and `crx_rl_a4_deterioration_b11_check`.
