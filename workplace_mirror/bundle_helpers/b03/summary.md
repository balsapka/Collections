**What this bundle does.** CC A1 on month-end observation dates, the first primary dataset
under the data-layer rules, and the distress fixes from the PROD validation (Sonnet v01).

- **Month-end architecture.** Observation dates are month ends (CC like RL). The A1 windows
  are calendar months: "the last 3 months" = the observation month and the two before it,
  "the prior 3" = the three before those. `_common` works in months only (`window_agg`,
  `pit_latest(max_age_months)`, `lookback_floor`); the CC anchor needs a balance snapshot in
  the observation month. Until `cc_spine` is month-end, `build_cc_obs_base` moves each
  billing-date row to its month end (one row per account and month); any other
  non-month-end spine date stops the run.
- **Window by segment**, as on the other axes: 3 months at 60–180, 6 months at 180+
  (`_common.window_months`); "2 of 3" becomes "3 of 6" at 180+, the prior window is the 6
  months before, and card payments, distress and CASA activity read 6 months. The signal
  and A1 nodes take `params:model_id`; `ext_card_payment_max_3m` / `casa_active_3m` are
  now `ext_card_payment_max` / `casa_active`. cc_180_plus is not run by this bundle.
- **New primary dataset `prm_casa_return_events`** (pipeline `casa_primary`, outside
  crx_persona): every returned CASA transaction (`CHEQUE RETURNS`, `DDS Rejects/Reversal`,
  `RETURNS`; both debit and credit legs) for all CIFs, one row per
  `tran_id + part_tran_srl_num + tran_date`, latest `edp_load_date` kept. It covers the 6 months
  before `crx_persona.persona_start_date` and everything after; each run rebuilds it whole. CC A1 reads it instead of `comp_financial_tran_repos_dly`.
- **Distress** = cheque returns + DDS rejects/reversals in the last 3 months; POS reversals
  (`RETURNS`) no longer count. Bureau bounces stay dated by `extract_date` (the pull date;
  the bounce date is under investigation).
- **Income**: the WM-recovered salary is the only internal salary source.
- **`a1_ability/README.md`**: the A1 logic in plain terms (sources, windows, the 2-of-3
  rules, the state ladder, known limits).
- **Check**: the bundle 01/02 check (`b01_check.py`) is replaced by `b03_check.py`, which
  compares the bundle 02 output (`crx_cc_a1_ability_b01_check`) with the new month-end output
  (`crx_cc_a1_ability_b03_check`), matching each account by month. It also logs how often
  the 2 × anchor income bar and the income-weakening check fire, and the income levels and
  states with a flat AED 3,000 floor and without the weakening check.
