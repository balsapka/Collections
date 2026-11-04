**Step 4.** Ask Sonnet the following, in one go:

1. **Account master catalog entry.** Add `raw_casa_acid_to_cif` to our raw catalog, a copy of WM's
   entry of the same name (`wealth_management` `conf/base/catalog.yml`, around line 364). Keep the
   same table (`general_acct_mast_table`), columns (`cif_id, acid, schm_code, acct_crncy_code,
   foracid`), `SELECT DISTINCT` and WM's filters (`emp_id`, `acct_ownership`, non-null `cif_id` and
   `acid`). Use our `*finacle` anchor and `aacoe_prefix`, as `general_acct_mast_bridge` does in
   `catalog_raw_demographics.yml`.
2. **Bounce date on the alert primary.** `feat_cif_bureau_bounces_monthly` now reads `dt_of_return`
   from `prm_bureau_alert_enriched` (raw alert column `DT_OF_RETURN`). Find the node that builds
   `prm_bureau_alert_enriched` and its staging input. If the column is not carried through, add it
   (as a date, name `dt_of_return`). Then write out the exact command that rebuilds **only** those
   nodes (`kedro run --env=dev --pipeline=... --nodes=...`), as for bundle 12. You will use it in
   step 6.
3. **Tests.** Run the CASA and A1 test modules and fix the ones the new signatures break:
   - `build_casa_activity(transactions, casa_accounts)` and `build_returns(return_events,
     casa_accounts)` need `foracid` on the legs;
   - `build_casa_accounts` is new;
   - the bounce feature reads `cif_id`, `dt_of_return` and `bounced_cheque_amount`, and returns
     `bounce_events` and `max_bounce_amount`.

Then check:
- `grep -rn "b12" src conf --include='*.py' --include='*.yml'` prints nothing;
- `kedro registry list | grep a1_ability` lists the two `*_b14_check` pipelines;
- `kedro catalog list | grep -E "raw_casa_acid_to_cif|prm_casa_accounts"` finds both.
