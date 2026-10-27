# A1 v03: why each state fires (initial results for GRR)

Give this to the workplace Sonnet in UAT. It reads the real CC A1 output
(`crx_cc_a1_ability_v2`, refreshed by bundle 03 Step 9) and its signal tables, so it runs now,
before the rename. Same flow as v01 / v02 (Sonnet writes, you run in PROD, Sonnet analyses),
folder `tmp_validation/a1_v03/`. Run for `cc_60_180` and, once bundle 05 Step 8 has written
`crx_rl_a1_ability_v2`, for `rl_60_180` (`model_id` in `conf/dev/globals_dev.yml`). Paste back
`summary.md` (part C). Part D tests whether the activity gate fires on administrative records (CC and RL) and
whether RL's DDS rejects are failed EMI collections (bundle 05 check: RL is 89.5% Low).

````text
Task: explain, with PROD aggregates, why the CC A1 ability states fire at the rates they do —
which rule decides each state and which information is missing — as the basis of a results
note for GRR. You work in UAT with no data: you write a snippet, the user runs it in PROD, you
analyse the results file. Change no pipeline code.

Context. A1 logic is in src/enbd_collections/pipelines/crx_persona/a1_ability/README.md;
read it first. Per (account_id, observation_date), month-end dates, window W = 3 months at
60-180 (m1 = the observation month):
  income level     stable (2 pts) / weak (1) / none (0): income_m1..m3 >= max(3000, 2 x
                   anchor) in 2 of 3 months and not weakening (m1-m3 mean >= 75% of m4-m6
                   mean) = stable; else any month >= 1000 = weak; else none. income_m = larger
                   of WM-recovered internal salary and bureau salary that month.
  liquidity level  adequate (2) / weak (1) / none (0): CASA >= max(3000, anchor) in 2 of 3
                   months and not falling > 50%, or one external card payment >=
                   max(500, anchor) = adequate; else CASA >= 1000 in any month or a card
                   payment >= 1000 = weak; else none.
  distress         cheque return or DDS reject/reversal (prm_casa_return_events) or a bureau
                   bounced cheque (dated by extract_date) in W -> one rung down.
  state            unknown = 0 points, no distress, no CASA flow in W (casa_active = 0);
                   high = 4 points no distress; moderate = 2-3 points no distress or 4 with
                   distress; low = everything else.
Latest PROD distribution (2026-08-31, n=19,292): unknown 62.7%, low 36.2%, moderate 1.1%,
high 8 rows. Income is none on ~98% of rows, liquidity none on ~97%.

A. Write tmp_validation/a1_v03/a1_v03_snippet.py and README.md (run steps).
   Rules: catalog.load only (no spark.read, no paths); model_id from
   catalog.load("params:model_id") and in the output filename; aggregates only — no ids,
   account / card numbers or names; counts and shares, percentiles where asked. Reuse the
   engine's own functions instead of re-implementing rules: import from
   crx_persona.a1_ability.classify (income_level, liquidity_level, _window, _months,
   _count_at_least, _not_weakening, the constants F_INC, K_INC, D_INC, F_CASA, K_CASA, D_CASA,
   F_PAY, K_PAY, DEMIN, MIN_MONTHS) and from crx_persona.a1_ability.signals (_internal_salary,
   _bureau_salary, _casa_by_month and the distress reason list). Check: your recomputed
   income / liquidity level and state equal the output's on every row (log the mismatch
   count; it must be 0).
   Datasets (add dcore_prm_followup_outcomes and the DCORE account -> agreement map for v2c):
   crx_cc_a1_ability_v2, crx_cc_obs_base, crx_cc_a1_income_signals,
   crx_cc_a1_liquidity_signals, crx_cc_a1_distress_signals, crx_cc_a1_internal_returns,
   crx_cc_a1_liquidity_anchor, wm_fea_salary_days_since_increment, stg_aecb_salary_history,
   prm_bureau_cif_bridge, prm_bureau_alert_enriched, wm_fea_casa_eod_avg_balance.
   Base = the latest observation month (params:crx_persona.persona_end_date) unless a table
   says otherwise. One JSON at context.project_path / "tmp_validation/a1_v03/results_<model_id>.json";
   wrap each table in try/except and record the error; commit and push only
   tmp_validation/a1_v03/.

B. Tables:
   v1_states      state counts and shares; the decision table: income level x liquidity level
                  x distress flag -> state, with counts (every non-empty cell).
   v2_income_why  rows by income level and reason:
                    none   N1 no salary month from either source in the 24 months up to the
                              observation date; N2 the latest salary month is m4-m6;
                              N3 m7-m12; N4 older than m12; N5 salary in m1-m3 but every month
                              < 1000
                    weak   W1 only 1 of 3 months >= the threshold; W2 2 of 3 >= the threshold
                              but weakening fails; W3 salary in m1-m3, all >= 1000 and below the
                              threshold
                    stable by source of the qualifying months: internal only / bureau only /
                              both
                  First, the bureau month format: stg_aecb_salary_history.subj_salcr_hist_ref_mnth
                  parsed as MMyyyy (what the engine does) vs yyyyMM (the DE model
                  BureauSalaryHistory documents reference_month as YYYYMM): NULL share of each
                  parse, and 10 distinct raw values (they are month codes, not customer data).
                  Also: share of base CIFs with any internal salary month in 24 months, any
                  bureau salary month, both, neither; the median age in months of the latest
                  salary per source; how often the 2 x anchor bar (not the 3000 floor) is what
                  W1 / W3 rows miss.
   v2b_salary_timing  ft_last_salary_amount is WM's monthly total of salary-flagged credits
                  (bonus, incentive, overtime and commission included), dated to the first of the
                  month and forward-filled weekly (bundle_helpers/a1_final/wm_salary_feature_logic.md
                  in the mirror; your own reading of wealth_management income.py:17 / :1204 /
                  :1308). An employer that pays early puts two salaries in one month and none in
                  the next (user, 2026-10-27: confirmed in the data). From _internal_salary over
                  24 months, base CIFs, one value per CIF-month:
                  - history depth: earliest and latest salary month per CIF (p10/p50/p90 of the
                    number of salary months), and whether months older than ~4 months before each
                    weekly snapshot are present at all (the WM run looks back ~3 months);
                  - "double" months: total >= 1.8x the CIF's median monthly total; of those, the
                    share whose next month (or previous) has no salary (early-pay pattern) vs
                    both neighbours present (bonus pattern);
                  - whether our catalog can load WM's monthly primary pri_salary_from_casa_txns
                    (month_sum, salary_count): its catalog entry, or NOT FOUND and where you looked;
                  - for every row, the income level under (1) the window-total rule: Stable =
                    salary received in the window >= 2 x the threshold (3 x at 180+) and the
                    window total not more than 25% below the prior window's; crosstab engine
                    level x (1), split by whether the window holds a double month.
   v2c_eos        end-of-service (EOS / EOSB) payments. The user confirmed that
                  wm_fea_salary_days_since_increment does not count EOS as salary, so only the
                  bureau sources can carry it. Base CIFs, 24 months: share with a bureau salary
                  month (stg_aecb_salary_history; RL also feature_retail_loans) > 3x their median
                  bureau month of the 12 months before it; of those, the share with no salary
                  (either source) afterwards; how many rows have such a month in the window, and
                  their income level / state. Also DCORE result names mentioning EOSB (EXPECTING
                  EOSB, RECEIVED EOSB, KSA/EOSB, ...): base rows with one in 24 months, by A1 state
                  and liquidity level.
   v3_liquidity_why rows by liquidity level and reason:
                    none   L1 no CASA balance row for the CIF in the 12 months (no CASA with us);
                              L2 CASA rows but every month in m1-m3 < 1000 or missing
                    weak   K1 CASA >= 1000 in some month, fewer than 2 months >= the floor;
                              K2 2 of 3 >= the floor but the decline check fails; K3 only a card
                              payment between 1000 and the payment floor
                    adequate by path: CASA / external card payment / both
                  Also: CASA balance p10/p50/p90 in m1 for CIFs with a CASA row; share with
                  casa_active = 1; share with any external card payment, and its p50 amount.
   v4_distress_why distress rows by source in W: internal cheque return / internal DDS /
                  bureau bounce, every combination (7 cells); bureau-only rows split by whether
                  the same bounced amount appears in an earlier extract; distress share by
                  state.
   v5_unknown_why unknown rows by CASA (L1 no CASA with us / L2 CASA but dormant) x salary
                  (any month in 24 months: internal / bureau / none) x bureau pull for the CIF
                  in 12 months (yes / no).
   v6_low_why     low rows by path: 0 points + distress / 0 points + CASA flow, no distress /
                  1 point from income / 1 point from liquidity / 2-3 points + distress.
   v7_anchor      share of rows with an anchor; anchor p10/p50/p90; income threshold
                  (max(3000, 2 x anchor)) p50/p90; share where the anchor raises the income
                  bar and the liquidity floor.
   v8_months      state shares per observation month over the persona months (all rows of
                  crx_cc_a1_ability_v2), to show stability.

C. After the user commits the results: read results_cc_60_180.json and save
   tmp_validation/a1_v03/summary.md, under 90 lines, written for a business reader (GRR):
   1. the state distribution, one line;
   2. per state (High, Moderate, Low, Unknown): the share, the rule path that produces most of
      it (v1 / v6), and the 2-3 numbers that explain it;
   3. Salary timing (v2b): history depth, how often a month doubles (early pay vs bonus), and
      how many rows the window-total rule (1) moves between levels (and states); EOS (v2c): how often a bureau month
      looks like an EOS spike, and where the EOSB-noted rows end up.
   4. "What information is missing": income (v2: the N1-N4 split, internal vs bureau
      coverage), liquidity (v3: no CASA vs low balance), and what the GRR bureau salary feed
      would change (rows in N1/N2-N4 whose CIF has a bureau pull but no bureau salary);
   5. distress: sources and their overlap (v4);
   6. the anchor's effect (v7) and month-to-month stability (v8);
   7. the recomputation check (mismatch count).
   No code proposals; numbers from the JSON only. Commit and push.

D. RL (rl_60_180), and the activity gate for both. The same snippet must run for RL: pick the
   dataset names by model_id (crx_rl_a1_ability_v2, crx_rl_obs_base, crx_rl_a1_income_signals,
   crx_rl_a1_liquidity_signals, crx_rl_a1_distress_signals, crx_rl_a1_internal_returns,
   crx_rl_a1_liquidity_anchor); the anchor is one EMI (int_loan_master.installment_due_amount),
   and income also reads feature_retail_loans (aecb_last_salary_credit_amount dated by
   aecb_bureau_pull_date).
   RL results (latest month 2026-08-31, n=3,985): low 89.5%, unknown 9.1%, moderate 1.4%,
   high 1; 0-point rows 88.9%, distress 19.8%. At least ~14K rows (all months) are Low only
   because casa_active = 1 (CC: unknown 62.7%, low 36.2%).
   Facts from the user (2026-10-27): wm_fea_casa_cc_inflow_outflow's CC outflow (and maybe
   inflow) amounts include administrative records (e.g. fees) that are not real transactions;
   its CASA inflow / outflow amounts do not include the loan account itself, but the EMI
   repayment (money from the CASA account to the loan account) is a CASA outflow. A1 reads only the
   CASA columns (ft_inflow_casa_amt_in_last_0_0_weeks_sum, ft_outflow_casa_amt_in_last_0_0_weeks_sum).
   Test, for cc_60_180 and rl_60_180:
   H-A    casa_active fires on administrative records: for many 0-point rows the window's only
          CASA movements are fees, charges, interest, system postings or reversals, not
          customer-initiated transactions (salary or other credits, cash, ATM, POS, transfers,
          bill payments, cheques).
   H-RL1  (RL) casa_active fires on loan servicing: the window's only customer-side CASA
          movements are the EMI repayment to the loan account (an outflow to the loan account,
          or within 5% of the loan's EMI) and inflows that only top it up.
   H-RL2  (RL) The DDS rejects are failed EMI collections: the DDS debit leg amount is within 5%
          of the loan's EMI (prm_casa_return_events amounts vs int_loan_master).
   Part A first: from code / profiles, how wm_fea_casa_cc_inflow_outflow's CASA columns are
   built (source table, filters, which transaction types they sum) and which columns of
   wm_pri_labelled_transactions and of comp_financial_tran_repos_dly tell a customer-initiated
   transaction from an administrative one (tran_type, tran_sub_type, tran_particular_code,
   reason_for_excluding, product_category, ...), with their top values; quote file:line.
   (Reading comp_financial_tran_repos_dly is fine in this validation, filtered to base CIFs and
   the window.)
   Extra tables:
   v9_activity    rows with 0 points, no distress and casa_active = 1, per model_id: share whose
                  window CASA transactions are all administrative; share with any
                  customer-initiated one; top 15 transaction types of the administrative-only
                  rows; and the share of WM weeks with flow > 0 that have no customer-initiated
                  transaction that week. Same split for unknown rows (casa_active = 0) as a
                  control (share with a customer-initiated transaction the WM flag missed).
                  RL: of the rows with a customer-initiated transaction, the share whose only
                  ones are EMI repayments to the loan account (plus same-week top-ups).
   v10_dds_emi    (RL) distress rows from internal DDS: share whose DDS debit legs are all
                  EMI-like; share with any non-EMI DDS; the same for cheque returns.
   In summary.md add a verdict per hypothesis (CONFIRMED / REJECTED / INCONCLUSIVE) with the
   3-5 numbers that decide it, per model_id, and how many Low rows would become Unknown if only
   customer-initiated transactions counted, and (RL) if EMI repayments did not count either
   (numbers, not proposals).
````
