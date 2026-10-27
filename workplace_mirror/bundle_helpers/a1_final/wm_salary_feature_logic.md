# `wm_fea_salary_days_since_increment.ft_last_salary_amount` — how WM builds it

Reverse-engineered by the workplace Sonnet from the `wealth_management` repo (HEAD `749ae21`,
read only, 2026-10-27); transcribed from photos (`pics/claude_code_handoff_5.md`), so file:line
references are worth a second look. The user confirmed the double-counting in the data.

- **Nodes:** `calculate_monthly_salary_from_casa_txns` (`income.py:17`) →
  `pri_salary_from_casa_txns`; `create_days_since_salary_and_increment_features`
  (`income.py:1204`) → `fea_weekly_salary_days_since_and_increment` (our
  `wm_fea_salary_days_since_increment`). Wired in `income_pipeline.py`.
- **Raw source:** Finacle CASA transactions (`hist_tran_dtl_table` ∪
  `history_hist_tran_dtl_table`, header table for remarks / channel); account → CIF from
  `general_acct_mast_table` (employee accounts excluded); non-AED converted at the day's rate.
- **Salary flag** (ENBD branch, `income.py:153`): a credit (`part_tran_type = 'C'`),
  `tran_particular_code` not in 947 / LV3 / LV4, and either the code is one of 505, 506, 507,
  503, 585–588, 085–088, 328, 828, or the narrative (particulars + remarks, upper-cased, spaces
  removed) matches the salary regex (`parameters.yml:3090`): SALARY, PAYROLL, SALAR, B/O,
  INCENTIVE, BONUS, OVERTIME, COMMISSION, misspellings, month prefixes (JANSAL, FEB SAL).
- **Aggregation:** flagged credits are **summed per CIF and calendar month** across all
  accounts (`month_sum`, `salary_count`); months without one have no row. A 500 AED minimum
  exists in the config but is not used.
- **The feature** (`income.py:1308`): `last_salary_amount = month_sum`, placed on the first of
  the month and **forward-filled** onto the weekly spine with no staleness cap; "days since" is
  counted from the first of the salary month, so it is accurate to about a month.
- **Lookback:** about 3 months of transactions per run (`income_last_n_months: -3`); history
  older than a run's window comes only from earlier runs' rows.
- **EOS** is not flagged as salary (user).

## What it means for A1

- Engine income per month (`_internal_salary`: snapshot date − days since → the first of the
  salary month) = WM's **monthly total of flagged credits**. Repeated forward-filled rows
  collapse to one value per month. There are no credit dates.
- **Early pay:** two salaries in one calendar month show as one month at ~2× and an empty next
  month (user, 2026-10-27: confirmed in the data). Two of them in m3 and nothing after count as
  1 of 3 → Weak.
- **Bonus, incentive, overtime, commission** add to the month total, so a month total is not a
  clean basic salary; keyword matches can also be false positives.
- Spec S12 ("count salary credits") cannot be built on this table; see the S12 revision.
