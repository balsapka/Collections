# A1: does the AECB salary predict payment and cure? (prompt for the UAT Sonnet)

Give the block below to the UAT Sonnet 5.5 as it is. Flow: Sonnet writes the snippet and commits it
(UAT, no data) → you run it in PROD for `cc_60_180` and `rl_60_180` and commit the results files →
Sonnet analyses them in UAT and writes `summary.md` → paste the summary back here. Run it after
bundle 09's step 8 and before the bundle's cleanup if you can; it reads the real A1 output.

````text
Goal
A1 (ability) now takes bureau salary from the AECB alert table. It moved many customers out of
Unknown: on cc_60_180, Unknown fell from 74.2% to 56.1% and Moderate rose from 1.4% to 13.9%, nearly
all on AECB salary. Before GRR sees this, find out whether those customers actually behave better:
do customers with an AECB salary pay and cure more, and roll or charge off less, than comparable
customers without one? Also settle whether the AECB salary outlasts a stopped salary.

Decided (do not revisit or propose changes to these rules)
- The AECB salary is salary_credit_amount on alert types 31 and 32, accurate on the pull date. It
  counts in the extract month and the next month only. A type 43 closure ends it.
- A1 income per month = the larger of internal and bureau. Stable = window total >= 2 x
  max(AED 3,000, 2 x amount due) and at most 25% below the prior window's total. Weak = any month
  >= AED 1,000 but not Stable. Window W = the observation month and the 2 before it.
- This is a validation of a signal, not a model. No tuning, no new thresholds.

Find these yourself
- The A1 output is crx_cc_a1_ability / crx_rl_a1_ability (all persona months, with a1_state,
  a1_income_level, a1_liquidity_level, a1_distress_flag, a1_income_source, a1_salary_stopped). If it
  does not carry a1_income_source yet, step 8 has not run: use crx_<p>_a1_ability_b09_check. The
  monthly income series is in crx_<p>_a1_income_signals (income_m1..m6, internal_salary_w,
  bureau_salary_w, internal_salary_prior).
- The outcomes: find the best source of month-end DPD / bucket, payments and charge-off per account
  (crx_cc_dpd_sequences, crx_rl_dpd_sequences, cc_spine, rl_spine, the balance or payment primaries).
  Read the code, say which dataset and columns you chose and why, and note any lag. Spines may still
  carry mid-month billing dates on CC: never join on the exact date; use the month.

Outcomes, per account, from the observation month, 1 and 3 months forward
- cure: back below the 60+ DPD scope (and, separately, fully current);
- roll: a worse DPD bucket, or charge-off / write-off;
- payment: any payment, and a payment of at least the amount due at observation, if the data allows.

Cohorts
Observation months with 3 full outcome months after them, ending at the latest month with complete
outcomes (likely Jan-May 2026). Pool them and also show each month, so a one-month effect is visible.
An account can appear in several months: report rows and distinct accounts, and give every
comparison also on the latest month of each account only.

Compare, always beside the base rate and with counts
H1 By a1_state: high, moderate, low, unknown. Does the order hold for each outcome?
H2 The main test. Rows that would be Unknown without the AECB salary (0 points from internal salary
   and liquidity, no distress, no customer CASA movement) split into: AECB Stable, AECB Weak, no AECB
   salary. Same split for rows that would be Low without it.
H3 Within income level: a1_income_source internal vs bureau. Is AECB Stable as good as internal
   Stable?
H4 Controls. Repeat H2 within DPD band (61-90, 91-120, 121-180), product (RL: loan_type), and
   amount-due band, because customers with an AECB salary may simply be earlier in delinquency.
   Give the difference in rates with a 95% interval; say where it survives and where it disappears.
H5 Stopped salary. a1_salary_stopped = 1 by income level: outcomes compared with not stopped. Then
   the alert path around a stop: for CIFs whose internal salary stopped, alert rows and amounts in
   months -3..+6 around the last internal salary month (share with a positive alert, median amount,
   share with a lower amount than before). Do positive alerts die away after a stop?
H6 The 25% check. Rows with an AECB salary in W whose window total passes but which are Weak because
   of the 25% check, against AECB Stable and other AECB Weak. Do they behave like Stable or Weak?
   Within them, split real level falls (latest amount at least 25% below the previous one) from
   sparse months (same amount or higher, fewer months with a value).
H7 Data checks. Alert rows, salary rows and distinct base CIFs per extract month for the last 12
   months, and the last extract date in the persisted alerts vs the raw table: how short is August?
   Rows that are dormant in A1 whose only CASA legs in W are lane ambiguous (MISCELLANEOUS): how many?

Hard rules
- Kedro notebook snippet: data only through catalog.load(...); model_id =
  catalog.load("params:model_id"), never hardcoded or overridden; model_id in every output file name.
- Aggregates only: counts, shares, intervals. No cif_id, account_id or customer-level rows; suppress
  any cell under 10 accounts.
- Wrap each part in try/except; a failed part records its error and the rest still runs. Cache or
  persist the joined base so the run takes minutes per part, not hours.
- No pipeline, catalog or conf changes. Work in a new tracked folder
  tmp_validation/a1_payment_cure/ (snippet + README); commit and push it. The PROD run writes
  results_<model_id>.json into it.

Deliverables
1. tmp_validation/a1_payment_cure/a1_payment_cure_snippet.py + README.md (how to run, what it saves),
   committed and pushed from UAT.
2. After the user commits results_cc_60_180.json and results_rl_60_180.json: summary.md in the same
   folder, under 60 lines. First the outcome source and the cohort months. Then per hypothesis a
   verdict (CONFIRMED / REJECTED / UNCLEAR) and the key numbers, CC and RL side by side. Then
   "Answer": does the AECB salary separate better from worse payers once DPD band is controlled, and
   by how much? Check every number against the JSON; write NOT IN JSON when one is missing.
````
