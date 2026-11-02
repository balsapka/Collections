# A1: are all the dates really there? (short prompt for the UAT Sonnet)

Give the block below to the UAT Sonnet 5.5 as it is. Run its snippet in PROD before bundle 12's
step 6, then paste `summary.md` back here. Rerun it after the alert rebuild if alerts had gaps.

````text
Goal
Sandpit ingestion can leave holes. For every source A1 reads, check that the dates are continuous,
not just that the max date is right. Change no pipeline code.

Sources (find the catalog names; use the raw table and each persisted copy where both exist)
AECB alerts: raw, staging, prm_bureau_alert_enriched, by extract_date and edp_load_date.
WM weekly: wm_fea_salary_days_since_increment, wm_fea_casa_eod_avg_balance,
wm_fea_casa_cc_inflow_outflow, by week_number (yyyyMM0W, expect weeks 01-04 every month).
Daily: comp_financial_tran_repos_dly, prm_casa_transactions, prm_casa_return_events,
wm_pri_labelled_transactions, dcore_prm_followup_outcomes.
Monthly / snapshots: prm_balance (CC), int_loan_master and feature_retail_loans (RL).

For each, from 2025-01-01 to the latest date, per model_id where the data is scoped
1. min, max, distinct periods, and the list of every missing period (day, week or month). For daily
   sources mark which missing days are weekends or holidays only if the pattern shows it.
2. Rows per period, plus median of the neighbouring 8 periods: list periods under 50% of that median
   (a partly loaded day looks present but is a gap).
3. Raw vs persisted: periods in raw missing from the copy, and periods where the row counts differ
   by more than 5%.
4. Alerts only: distinct CIFs and rows with salary_credit_amount > 0 per extract date, Jun-Oct 2026.

Rules: catalog.load only; model_id = catalog.load("params:model_id"), in the output file name; aggregates
only, no ids; a source that fails to load records its error and the rest still runs. Work in a new
tracked folder tmp_validation/a1_date_gaps/ and commit only that. Filter early on the date column
so the raw tables are not fully scanned.

Deliverables
1. Snippet + README, pushed from UAT.
2. After the user commits results_<model_id>.json for cc_60_180 and rl_60_180: summary.md under 30
   lines. One row per source: OK or GAPS, the exact missing or thin periods, whether they touch
   Nov 2025-Aug 2026 (what A1 reads), and which rebuild would fix them.
````
