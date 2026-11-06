**Step 4.** Check the catalog: each entry exactly once, and nothing else lost since before bundle 15. `<commit>` = the last commit before you applied bundle 15 (`git log --oneline -8` shows it):

```bash
grep -cE "^crx_cc_(billing|acct_windows):$" conf/base/catalog/catalog_crx.yml
```

```bash
git diff <commit> HEAD -- conf/base/catalog/catalog_crx.yml | grep -E "^-[a-z_0-9]+:$"
```

The first prints `2`. The second may list only: the 20 entries bundle 15 deleted (`crx_cc_departure_*`, `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_rl_departure_signature`, `crx_rl_depart_*`), the six old A3 datasets (`*_dpd_bucket_movement`, `*_payment_sum_waterfall`) and the cleaned-up check entries (`*_b13_check`, `*_b14_check`, `*_ra_check`, `*_rf_check`). Paste anything else back before going on.
