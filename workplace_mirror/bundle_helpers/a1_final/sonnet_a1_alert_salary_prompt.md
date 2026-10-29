# A1 — bureau salary from the alert table (validation prompt for the UAT Sonnet)

Give the block below to the UAT Sonnet 5.5 as it is. Flow: Sonnet writes the snippet and commits it
(UAT, no data) → you run it in PROD for `cc_60_180` and `rl_60_180` and commit the results files →
Sonnet analyses them in UAT and writes `summary.md` → paste the summary back here. Independent of
bundle 08: it can run before or after it (part H5 uses bundle 08's internal salary feature when it
exists).

````text
Goal
A1 (ability) needs bureau salary for customers. Today it comes from the AECB salary history
(stg_aecb_salary_history), keyed by bureau file id and linked to customers through
prm_bureau_cif_bridge, which reaches under 4% of our customers. prm_bureau_alert_enriched already
carries cif_id (from PRVDR_SUBJ_NUM) and a salary column, salary_credit_amount (raw SALARY_CRED_AMT,
about 28% filled in an earlier profile). Find out whether that column can be A1's main bureau salary
source: what the amount means, which month it belongs to, whom it covers, and whether it is just our
own salary credit reported back. And test the user's hypothesis (part M): the alert table is the
master bureau table that the other AECB tables (salary history, contract history / detail /
link, credit score, payment orders, court cases, summaries) feed into — so it could be the hub
that links every bureau file to a customer.

Decided (do not revisit)
- A1 income per month = the larger of internal salary and bureau salary. A "salary month" needs
  AED 1,000+ to count at all; the stable threshold is max(AED 3,000, 2 x the anchor) and Stable
  needs the window's total salary >= 2 x that threshold.
- Window W = the observation month and the 2 before it (60-180 DPD models). Observation dates are
  month ends. Customer level = cif_id, across all of the customer's accounts.
- Bureau bounces already come from this table (a new event when the bounced amount changes); this
  task is about salary only.
- Some raw AECB tables are temporarily missing from the sandpit: use the persisted datasets
  (prm_bureau_alert_enriched, prm_bureau_cif_bridge, stg_aecb_salary_history) and say clearly
  which ones did not load.

Hard rules
- Kedro notebook snippet: data only through catalog.load(...); model_id = catalog.load("params:model_id")
  (never hardcoded, never overridden); put the model_id in every output file name.
- Aggregates only: counts, shares, percentiles, value lists of codes / descriptions. No cif_id,
  account_id or amount-per-customer rows; suppress any cell under 10 customers.
- Base = the latest observation month of crx_cc_obs_base (cc_* models) or crx_rl_obs_base (rl_*):
  its account_id / cif_id rows. Report accounts and distinct CIFs.
- Wrap each part in try/except; a failed part records its error and the rest still runs.
- No pipeline, catalog or conf changes. Work in a new tracked folder tmp_validation/a1_alert_salary/
  (snippet + README); commit and push it. The PROD run writes results_<model_id>.json into it.

Hypotheses and the exact aggregates to save
H0 Inputs. For prm_bureau_alert_enriched: row count, columns and types, null share of
   salary_credit_amount (all rows / base CIFs), share > 0, p10/p50/p90/p99 of the positive values,
   min/max extract_date and edp_load_date. Read the code that builds it (nodes/primary/bureau,
   staging alert node, the BureauAlertEnriched model) and say file:line how cif_id and
   salary_credit_amount are derived and which raw rows are dropped on the way.
H1 Meaning. Is the amount a monthly salary, a last credit, or a change? Rows with a salary amount by
   alert_category, alert_type_number + alert_description, contract_type, subject_role,
   provider_code (counts, CIFs, median amount). Per CIF over its pulls: distinct amounts
   (p50/p90), share of consecutive pulls repeating the same amount, share of CIFs whose amount
   changes month to month. Any other column that looks like a salary month or date: name it and
   show its fill rate and how it relates to extract_date.
H2 Dating. extract_date vs edp_load_date (difference p10/p50/p90). Pulls per CIF per month (p50/p90).
   Month of first appearance of a new amount vs the internal salary month of the same amount
   (see H5) where both exist: lag in months, distribution.
H3 Own bank. Which provider_code is ENBD (find it in code, the AECB reference table or the data)?
   Share of salary rows and of CIFs by provider_code; for CIFs with internal salary in the same
   month, share where the alert amount equals the internal amount within 2%, split by provider.
H4 Coverage, base CIFs: alert salary > 0 (and >= 1,000) in W, in the last 6 and 12 months, ever;
   cross-tab with (a) internal salary in W yes / no and (b) today's bureau path
   (stg_aecb_salary_history joined to prm_bureau_cif_bridge on file id, a positive amount in W)
   yes / no. Same for "no internal salary in the last 12 months".
H5 Agreement. Internal salary per CIF and month: feat_cif_internal_salary_monthly (cif_id,
   month_end, salary) if it loads; otherwise wm_fea_salary_days_since_increment decoded so:
   week_number is yyyyMM0W (week 01-04), snapshot date ~ day 7*W-3 of that month, salary month =
   that date minus ft_days_since_salary_transaction, rounded to the nearest first of a month;
   amount = ft_last_salary_amount, max per CIF and month. Where both exist in the same month (and
   with the alert dated one month later): ratio alert / internal p10/p50/p90, share within 10%.
H6 A1 impact (rough). Base rows whose internal salary is below AED 1,000 in every month of W:
   how many have an alert salary >= 1,000 in W, and how many whose W total of alert amounts
   (one per month, max) is >= 6,000 (stable with no anchor). Same counts with the alert month
   taken as extract month minus 1.
L  Link (code and columns only, no heavy scans). prm_bureau_alert_enriched carries cb_subject_id.
   Does any bureau table we can load (staging or primary: salary history, contract link, credit
   score, contract detail, payment order) carry a subject id or provider subject number beside its
   file id? Give file:line and the column, and the share of base CIFs whose cb_subject_id reaches a
   salary-history file that way, if a column exists.
M  Master table? (the user's hypothesis; the other parts do not depend on it)
   M1 Keys. For every AECB dataset you can load (staging or primary; also try the raw
      dpl_uae_operations.sa_ops_aecb_* tables through the catalog, recording which are missing):
      its grain, every id column (file id, subject id, provider subject number, trigger id,
      alert process id / record id, source file name, contract number) and its fill rate.
   M2 Overlap. On a sample of 100k ids per table: the share of each table's file ids found among
      the alert table's id columns (cb_trig_id, alert_process_id, alert_rec_id, cb_subject_id,
      source_file_name, and their raw names), and the reverse. A master table would hold the
      keys of the others.
   M3 Population. Distinct CIFs in the alert table ever and per month; the share of base CIFs
      with an alert row in each of the last 12 months (a monthly full refresh shows ~100% every
      month, a trigger feed shows gaps); rows and pulls per CIF per month (p50/p90); alert rows per
      alert_category over time. Distinct subjects in the alert table vs distinct files / subjects
      in salary history and contract tables.
   M4 Values. For CIFs that reach a file through prm_bureau_cif_bridge: does the alert row of the
      same pull reproduce the detail tables — salary_credit_amount vs the salary-history amount,
      contract_balance_amount / overdue_amount vs contract detail for the same contract, if a
      contract key matches? Match rates.
   M5 Lineage. From code, the DE's bureau docs and the raw table / column names: what the alert
      feed is (AECB monitoring triggers, a daily delta, a full snapshot?), what ref_ops_aecb
      holds, and whether anything says which tables are built from which.
   Verdict for M: MASTER (a customer-level hub holding or reproducing the other tables' keys and
   values), TRIGGER FEED (event rows that summarise other tables, no shared keys), or UNCLEAR —
   with the numbers that decide it, and what it means for linking bureau salary to customers.

Deliverables
1. tmp_validation/a1_alert_salary/a1_alert_salary_snippet.py + README.md (how to run, what it
   saves), committed and pushed from UAT.
2. After the user commits results_cc_60_180.json and results_rl_60_180.json: summary.md in the same
   folder — per hypothesis a verdict (CONFIRMED / REJECTED / UNCLEAR) and the key numbers for CC and
   RL side by side, then "Recommendation": can salary_credit_amount be A1's bureau salary source,
   with which filters (alert types, providers) and which month; what L found; and the M verdict. One page; no
   customer-level data.
````
