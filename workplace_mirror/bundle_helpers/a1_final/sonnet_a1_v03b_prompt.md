# A1 v03b: the v03 parts the first run did not cover (CC and RL)

Give this to the UAT Sonnet 5.5. The first v03 run (`tmp_validation/a1_v03/`, CC only) was
written from an earlier version of the v03 prompt; its summary has no bureau-input check, no
salary timing, no EOS check, no activity-gate test and no RL. Same flow as before: Sonnet
extends the snippet, you run it in PROD for `cc_60_180` and then `rl_60_180` (`model_id` in
`conf/dev/globals_dev.yml`), push the JSONs, Sonnet writes the summary, and you paste back the
new summary sections. Self-contained: the Sonnet needs no other prompt file (the v03 prompt lives
only in the mirror repo).

````text
Goal: finish A1 v03 so the GRR results note can be written. The existing
tmp_validation/a1_v03/ (a1_v03_snippet.py, results_cc_60_180.json, summary.md) covers v1-v8
for cc_60_180 and the recompute check (0 mismatches). Extend that snippet with the tables
below, run it for both model_ids, and extend summary.md. Change no pipeline code.

Context: A1 logic is in src/enbd_collections/pipelines/crx_persona/a1_ability/README.md
(read it first). Per (account_id, observation_date), month-end dates, window W = the
observation month m1 + 2 before. Unknown = 0 points, no distress, casa_active = 0.

Already decided, do not revisit: the engine logic; stg_aecb_salary_history.subj_salcr_hist_ref_mnth
is MMYYYY (staging docstring, e.g. "072023"), so the engine's parse is right and the DE model's
"YYYYMM" is wrong; bureau distress repeats (same amount in a later extract) will be treated as
the same bounce; WM salary excludes EOS.

1. v0_bureau. Priority question: 88% of CC Unknown CIFs have a bureau pull in 12 months but
   only 0.18% of CIFs have any bureau salary in 24 months. Is that the data (no salary
   reported for most pulls) or the join (bridge, file id, edp_load_date)? Show the funnel per
   model_id: base CIFs -> in prm_bureau_cif_bridge -> with a bureau file in 24 months -> with
   any stg_aecb_salary_history row for those files (any month) -> with a parsed month in the
   24 months -> with an amount > 0. Also:
   v0_bureau      the bureau pipeline was written by an earlier model and never validated (user,
                  2026-10-27): treat its docstrings and pydantic models as unverified. Check the
                  three bureau inputs A1 reads, base CIFs only:
                  - prm_bureau_cif_bridge: rows per (bureau_file_id, edp_load_date) and distinct
                    cif_id per bureau_file_id (1 / 2 / 3+), distinct bureau_file_id per cif_id;
                    share of base CIFs present in the bridge; how cif_id is derived (part A, file:line);
                  - stg_aecb_salary_history: subj_salcr_hist_ref_mnth parsed as MMyyyy (what the
                    engine does) vs yyyyMM (the DE model documents YYYYMM): NULL share of each, and
                    10 distinct raw values (month codes only); rows per (file id, month) across
                    EDP_LOAD_DATE and per provider; the column list (part A);
                  - prm_bureau_alert_enriched: share of base CIFs with any row; rows per
                    (alert_process_id, edp_load_date); null shares of cif_id, contract_type,
                    alert_description, bounced_cheque_amount, extract_date.
                  Verdict per input: usable as is / usable with a named fix / not usable.

2. v2_pull_gap: rows by income reason (N1 no salary month from either source in 24 months;
   N2-N4 latest salary month older than m3; as in the existing v2_income_why) x "bureau pull
   for the CIF in 12 months but no bureau salary month in 24 months" (yes / no).

3. Salary timing and EOS:
   v2b_salary_timing  ft_last_salary_amount is WM's monthly total of salary-flagged credits
                  (bonus, incentive, overtime and commission included), dated to the first of the
                  month and forward-filled weekly (see wealth_management income.py:17 / :1204 /
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

4. Part D, the activity gate (CC and RL). CC matters as much as RL: 68% of CC Low is
   0 points + a CASA flow.
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

5. RL: pick dataset names by model_id (crx_rl_a1_ability_v2, crx_rl_obs_base,
   crx_rl_a1_income_signals, crx_rl_a1_liquidity_signals, crx_rl_a1_distress_signals,
   crx_rl_a1_internal_returns, crx_rl_a1_liquidity_anchor); the RL anchor is one EMI
   (int_loan_master.installment_due_amount) and RL income also reads feature_retail_loans
   (aecb_last_salary_credit_amount dated by aecb_bureau_pull_date). Run every table, the
   existing v1-v8 included, for rl_60_180 and keep the recompute check at 0 mismatches.
   RL results so far (2026-08-31, n=3,985): low 89.5%, unknown 9.1%, moderate 1.4%, high 1.

Hard rules: catalog.load only (no spark.read, no paths); model_id from
catalog.load("params:model_id") and in the output filename; aggregates only (no ids, account
or card numbers, names, free text); reuse the engine's own functions (a1_ability.classify,
a1_ability.signals); each table in its own try/except with the error recorded; never join
cc_spine, the DCORE spine or prm_contract on the date (mid-month dates in PROD). Before
handing over, check that the snippet compiles and every catalog name exists in conf/.

Deliverables:
- the extended snippet and README run steps, committed and pushed (UAT);
- after the user pushes results_cc_60_180.json and results_rl_60_180.json, extend summary.md:
  section 0 (bureau inputs: funnel + verdict per input), section 3 (salary timing, the
  window-total rule's moves between levels and states, EOS), the pull-gap count in section 4,
  section 8 (H-A, H-RL1, H-RL2: CONFIRMED / REJECTED / INCONCLUSIVE with the 3-5 deciding
  numbers per model_id; how many Low rows would become Unknown if only customer-initiated
  transactions counted, and for RL if EMI repayments did not count either), and an RL block
  for every section. Numbers only, no code proposals; under 140 lines. Commit and push.
````
