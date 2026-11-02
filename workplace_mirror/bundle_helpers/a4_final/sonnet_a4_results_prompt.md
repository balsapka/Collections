# A4: deterioration results by product and charge-off vintage for the model workbook

**Before this:** copy the new `docs/deterioration_states/spark/stakeholder/dpd_deterioration_states_reference.xlsx` to the workplace repo. It has four new sheets. `crx_cc_a4_deterioration` and `crx_rl_a4_deterioration` must be final for every model_id you run.

Give this to the UAT Sonnet 5.5. Sonnet writes the snippet in UAT. You run it in PROD once per model_id (`cc_60_180`, `cc_180_plus`, `rl_60_180`, `rl_180_plus`; switch `model_id` in `globals_dev.yml` and reload the kernel), then commit and push the results. Pull in UAT in the same Sonnet session: it checks the numbers and fills the workbook. Paste back `tmp_validation/a4_results/summary.md` so the mirror has the numbers too.

````text
Goal: the A4 (deterioration) model workbook needs its final results, split by retail-loan product
and, at 180+, by charge-off vintage. You work in UAT with no data: write a validation snippet, the
user runs it in PROD per model_id and commits the results, then you fill the workbook. Change no
pipeline code.

What is known:
- crx_<p>_a4_deterioration (p = cc, rl): one row per (account_id, observation_date). Columns in
  _dpd_journey/spark.py::build_deterioration: det_state, current_bucket (native), starts_delinquent,
  history_months, history_cropped, n_months_truncated, last6_in_band, months_since_4, chg_6m,
  restructure_blind_spot_flag. RL adds chain_stitched_flag, chain_months_added, chain_match_type.
- States: unknown, early_payment_default, stabilized, repeat_delinquent, straight_roller_seasoned,
  straight_roller_early_life, slow_roller.
- rl_spine has account_id, observation_date, loan_type, chargeoff_age_months. cc_spine has
  contract_id (= account_id), observation_date, chargeoff_age_months. cc_spine may still be on
  mid-month billing dates: join on account as string and the calendar month of observation_date,
  spine deduplicated on that key.
- crx_<p>_dpd_sequences has first_month per account (for RL use crx_rl_dpd_sequences_linked).
- Latest month rl_60_180 (2026-08), 3,985 accounts: unknown 0, early_payment_default 229, stabilized
  411, repeat_delinquent 363, straight_roller_seasoned 1,349, straight_roller_early_life 700,
  slow_roller 933. Personal 1,397, Personal Cash 1,224, Auto 1,364. Restructure: 65 stitched, 2 blind.

Deliverables per model_id; T1-T4 and T6 for the latest observation month:
  T1 det_state x product: every raw loan_type value mapped to Personal Loans, Personal Cash Loans,
     Auto; any other value and NULL kept as its own column and named; plus a total. CC: total only.
  T2 accounts in scope: distinct spine rows in that month (per product for RL), and spine rows with
     no output row.
  T3 why Unknown, on det_state = unknown, first match wins: restructure_blind_spot_flag = 1
     (restructured, no original loan found); n_months_truncated > 0 (cut at a long gap);
     history_cropped (cut by the window); anything else, which must be 0.
  T4 the detail blocks:
     a. stabilized: last6_in_band >= 5 (short-term), else long-term only;
     b. start of the delinquency: starts_delinquent; else history_cropped (cut, oldest month clean);
        else complete;
     c. history_months: under 12, 12-23, 24-35, 36 or more;
     d. DPD band today from current_bucket: CC 4 / 5 / 6 / 7 / 8+9, RL 3 / 4 / 5 / 6 / 7 = 61-90 /
        91-120 / 121-150 / 151-180 / 181+;
     e. restructured: RL chain_stitched_flag = 1 (original found), restructure_blind_spot_flag = 1
        (not found); CC restructure_blind_spot_flag = 1 only.
  T5 60-180 model_ids only: det_state by month for January to August 2026, month ends.
  T6 180+ model_ids only: det_state by vintage (chargeoff_age_months < 24 = early-stage charge-off,
     else late-stage; NULL its own column), products pooled.
  T7 min(first_month) across the accounts in the latest month, and the earliest observation month.

Hard rules:
- First check crx_rl_a4_deterioration has chain_stitched_flag and no ecl_gap_blind_spot_flag; if not,
  stop and say the final RL pipeline has not run for this model_id.
- catalog.load only (no spark.read, no paths); model_id from catalog.load("params:model_id"), in the
  output file name; nothing hardcoded or overridden.
- Aggregates only: counts, no account ids, CIFs or customer rows. Exact counts, small ones too; the
  workbook computes the shares.
- Write context.project_path / "tmp_validation/a4_results/results_<model_id>.json"; each table in its
  own try/except with the error recorded.
- Work only in tmp_validation/a4_results/ (tracked); commit and push only that folder.

Deliverables:
1. a4_results_snippet.py and a README.md with the run steps (one run per model_id, kernel reloaded).
2. After the user commits the JSONs, fill dpd_deterioration_states_reference.xlsx (find it in the
   repo; ask the user if there is more than one or none). Find cells by sheet, section title and
   row / column labels, never by fixed address. Change only the pale-yellow entry cells listed here:
   formulas, formats and text stay. Use openpyxl and keep the formulas (no data_only).
   - "Results": T1 into columns CC 61–180, CC 180+, RL 61–180 <product>, RL 180+ <product>;
     "Accounts in scope": T2. The RL total columns are formulas; leave them. The RL 61–180 cells
     already hold the check numbers: if a new number differs, keep the new one and report it.
   - "Results detail": columns CC 61–180, CC 180+, RL 61–180, RL 180+. Accounts: T2. Why Unknown: T3.
     Stabilized: T4a. Start of the delinquency: T4b. Months of history: T4c. DPD band today: T4d.
     Restructured loans: T4e; leave the CC "Original loan found" cell blank.
   - "Results trend": T5, sections Credit cards 61–180 and Retail loans 61–180.
   - "Results 180+ vintage": T6.
   Products outside the three, NULL vintages: add no columns; list them in the summary.
   Then reopen the file and check: every filled cell equals the JSON, each total equals its product
   sum, and nothing else changed (diff cell values and formulas of every sheet against the file
   before your edit). Commit the workbook only if the user says so.
3. summary.md (one line per check, no other commentary):
   - checks: splits add up to totals; rl_60_180 matches the numbers above; T2 spine rows with no
     output; T3 "anything else" = 0; T4 blocks each add up to their base. FAIL with the difference
     if one does not hold;
   - the workbook fill: cells written per sheet, the reopen check, any number that replaced a check
     number;
   - per model_id, T1-T7 as markdown tables, rows in the order listed, counts only. Check every
     number against the JSON; write NOT IN JSON when one is missing.
````
