**What this bundle does.** RL A4 decides whether a loan is restructured from `feature_retail_loans.has_restructured_loan_flag`, not `is_restructured` (user, 2026-11-02).

- **`restructure_blind_spot_flag`** = the feature flag was ever set for the account, except an account with its original loans' months in front of its own, which is no longer blind. `build_rl_dpd_sequences` reads the feature; `build_rl_linked_dpd_sequences` is new.
- **Removed**: `is_restructured` from the A4 path. `crx_rl_full_history_linked` no longer has `restructure_flag`, `crx_rl_restructure_chains` no longer has `chain_restructure_flag`.
- **One rule goes**: "a chain ending in an unmatched restructure stays blind" read `is_restructured` on the original loans. `feature_retail_loans` has spine rows only, so it has no value for them, and a stitched account is now simply not blind.
- **Unchanged**: chains and stitching (still `int_loan_restructure_link`), unmatched restructured loans blind for life, `crx_rl_full_history.restructure_flag` (`crx_rl_spell_table` still reads it), every state rule, CC.
- **Check** (`rl_a4_deterioration/b13_check.py`, pipeline `crx_rl_a4_deterioration_b13_check`, replacing bundle 11's): blocks `B13 OUTPUT` (old × new, new by `loan_type`), `RESTRUCTURE` (flag by `loan_type`, stitched, blind, old vs new blind, stitched without the flag), `UNKNOWN`.
- **Expected**: few state moves, only on accounts whose blind spot changes. The number to read is restructured Auto in `B13 RESTRUCTURE`: bundle 11 showed 0.
