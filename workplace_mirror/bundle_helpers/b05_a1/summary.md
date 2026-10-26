**What this bundle does.** RL A1 on the shared `a1_ability` engine, next to the RL
waterfall, plus a temporary check that compares the two in PROD.

- **New package `crx_persona/rl_a1_ability_v2/`** (pipeline `crx_rl_a1_ability_v2`, output
  `crx_rl_a1_ability_v2`): the same income, liquidity, distress and state logic as CC, on
  `crx_rl_obs_base` (month-end `rl_spine` rows in the persona months). Customer-level signals
  are read across the whole CIF, as for CC. States `high` / `moderate` / `low` / `unknown`,
  display `a1_state_label`.
- **RL anchor** (`build_rl_liquidity_anchor`): one EMI, `installment_due_amount` on the
  loan's `int_loan_master` snapshot in the observation month. Missing, stale or not positive
  → flat floors (AED 3,000 income, 3,000 CASA, 500 card payment).
- **Extra bureau salary for RL**: `build_income_signals` takes an optional
  `loan_features` (`feature_retail_loans`). `aecb_last_salary_credit_amount` of each loan's
  latest bureau pull counts as bureau salary in the pull month (`aecb_bureau_pull_date`),
  merged with the other sources (larger value per month). CC does not pass it. Pulls are
  rare today (most loans have one), so it seldom lands in the window.
- **Not in RL A1**: EMI payment behaviour (`int_loan_master.total_paid`, `emi_*_flag`,
  `feat_loan_emi`) — it belongs to credibility (A3). The waterfall's EMI-coverage arms go.
- **CC pipeline style**: every `node()` in `cc_a1_ability_v2/pipeline.py`,
  `obs_base/pipeline.py` and `casa/primary.py` now spells out `func=`, `inputs=`,
  `outputs=`, `name=`, `tags=` (tags on each node). No behaviour change. The bundle 03
  cleanup you already did at work is in the bundle's base-to-head diff too, so those files
  apply as `MERGED` or unchanged.
- **Check** (`b05_check.py`, pipeline `crx_rl_a1_ability_b05_check`): RL waterfall
  (`crx_rl_a1_ability`) vs the engine (`crx_rl_a1_ability_b05_check`) by account and month,
  plus what the `feature_retail_loans` salary adds. Removed by the cleanup prompt.
- The waterfall (`rl_a1_ability/`) stays until the check is reviewed; it is deleted with the
  CC v1 package in the CC finish bundle, which also drops the `_v2` names.
