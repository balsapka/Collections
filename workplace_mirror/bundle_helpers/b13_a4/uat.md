**Step 4.** Confirm `feature_retail_loans` has `has_restructured_loan_flag` and `account_id` at (account_id, observation_date); if not, name the dataset that does and stop. If bundle 11's check is already cleaned up in this repo, the merge keeps it out.

The tests are yours to update: `build_rl_dpd_sequences` and `build_rl_a4_deterioration` callers, the new `build_rl_linked_dpd_sequences`, and the schemas without `restructure_flag` (linked history) and `chain_restructure_flag`. Keep the rest passing.

Then `kedro registry list | grep a4_deterioration` lists `crx_rl_a4_deterioration_b13_check` and no `b11`, and this prints only `b13_check.py` lines if anything:

```bash
grep -rn "is_restructured" src/enbd_collections/pipelines/crx_persona/rl_a4_deterioration
```
