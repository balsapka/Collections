**What this bundle does.** Adds the shared helpers every persona axis will use
(`crx_persona/_common.py`), a per-product observation base (`obs_base/`: datasets
`crx_cc_obs_base`, `crx_rl_obs_base`) and the A1 ability engine (`crx_persona/a1_ability/`), which
implements the GRR workbook `A1_ability_20261022` (spec: `specs/A1_ability_spec.md` in the
mirror repo). The CC A1 axis (`cc_a1_ability_v2`) becomes a thin wrapper on the engine.
CC A1 v1, RL A1 and every other axis are untouched.

**What changes in `crx_cc_a1_ability_v2`:**
- the rules now follow the workbook month by month: a salary month needs a credit
  ≥ max(AED 3,000, 2 × anchor) (2 of the last 3 months, not more than 25% below the prior
  quarter); CASA ≥ max(AED 3,000, anchor) in 2 of the last 3 months (not more than 50%
  below the prior quarter); one external card payment ≥ max(AED 500, anchor); "last 3
  months" = the 3 complete calendar months before the observation month;
- anchor: CC 60–180 = amount in the oldest overdue bucket (OVD_01..06, snapshot ≤ 31
  days old); CC 180+ = none, absolute thresholds only; missing → flat floors;
- inputs: `wm_fea_casa_eod_avg_balance` replaces `feat_casa_eod_balance`;
  `feat_payroll_indicator` is no longer read (salary amounts per month come from the WM
  salary snapshots); `params:model_id` feeds the anchor;
- columns lose the `_v2` suffix (`a1_state`, `a1_income_level`, …) and gain
  `liquidity_anchor_amt`; intermediate datasets are `crx_cc_a1_{income,liquidity,distress}_signals`
  and `crx_cc_a1_liquidity_anchor`;
- accounts without a CIF now appear as `ability_unknown` instead of being missing;
- a missing source column stops the run with a clear error.
  Required: `wm_fea_salary_days_since_increment.ft_days_since_salary_transaction`,
  `wm_fea_casa_eod_avg_balance.ft_avg_casa_eod_balance_in_last_0_3_weeks_avg`.

**TODOs for the workplace assistant** (search `TODO(sonnet)` in `a1_ability/signals.py`):
1. Internal cheque bounces / DDS returns: find the source (CASA transaction codes or
   narrations in `comp_financial_tran_repos_dly`, a DDS mandate table), build
   `(cif_id, event_date)` across all of the customer's accounts, and pass it as
   `internal_returns` to the distress node.
2. Validate the per-month internal salary credits recovered from the WM snapshots against
   `feat_payroll_indicator`; prefer a table with monthly salary amounts if one exists.

The PROD check snippet (`b01_a1_engine_check.py`) is shipped to `data/input/mirror_bundles/`;
its snapshot copy lives on HDFS next to the A1 output and is deleted by the cleanup step.
