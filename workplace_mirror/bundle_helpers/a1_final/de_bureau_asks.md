# Messages to the DE: bureau salary (2026-11-12)

## 1. Closure alerts (needed)

In `int_bureau_alert_salary_monthly`, please read the closure alerts (`salaryaccountclosed` and
`salaryaccountisadded/closed`) by their amount, since the bureau mixes added and closed:

- amount > 0 → keep it as that month's salary;
- amount 0 or NULL → salary 0 (a stop). Today the NULL-amount ones are dropped.

Please also add a boolean `is_closure` to `feat_bureau_salary_unified`, true on rows that come from a
closure alert, so we can count a positive closure amount in its month without carrying it forward.

Added / average-changed alerts stay as they are (an added alert with no amount stays dropped).

## 2. Bulk pull (no rush; for when the pull grows)

1. Codes 232–235 are the salaries reported for the last 1 / 3 / 6 / 12 months. The months are counted
   back from `EDP_LOAD_DATE`: is that the bureau's response date, or can the load lag the pull? If it
   lags, where is the real response date (`sa_ops_aecb_sub_basic_dtl`, the header)?
2. On our spines the raw pull holds about 650 records for cc_60_180 (0.8% of customers), one load in
   2026-09. We expected about 5%: how many 232–235 records does `sa_ops_aecb_subj_charac` hold in total,
   and how many lose their `cif_id` in `prm_bureau_subj_charac` or fall outside the file-level scope?
3. What is the pull schedule, and which customers does it cover?
4. When two pulls cover the same month, a later pull's 0 loses to an earlier pull's positive amount
   ("usable first"). Should the latest pull win instead?
