# A3: results for the model document (prompt for the UAT Sonnet)

When to send: now (UAT writes the snippet). PROD runs it after bundle 25's check (step 7) and
before step 8 and the cleanup, per model_id (cc_60_180, cc_180_plus, rl_60_180, rl_180_plus), on the
check's `<name>__b25` copies: they are what step 8 will persist, so the Broken decision (T6b) comes
before the real run and the pipelines run once. If Broken stays, step 8 + cleanup follow and the
results stand; if it goes, a small A3 bundle comes first and the snippet is re-run (one source switch).
The user pastes `summary_a3_results.md` back to Claude, who then fills the yellow cells of the A3
model document (`docs/credibility/build_a3_workbook.py` → `a3_credibility_reference.xlsx`): Results,
Results detail, Results trend, Results 180+ vintage and Validation. Sensitivity keeps its back-tests.

````text
Goal
Produce every table of the A3 payment credibility model document's results sheets from the
A3 output of bundle 25 (rules D-A3-28..33: promise events, refusal lifted by a later
plan or payment, card due at bucket 08, same-day contact order, points Kept 3 / Partly kept 2 /
Broken 1 / Promised 1 / No promise 0). All four model_ids. Aggregates only; no pipeline change.

Decided, to follow
- Source: crx_<p>_a3_payment_credibility__b25 (p = cc / rl), the bundle 25 check's copy (catalog
  pattern "{name}__b25" in tmp_b25_check.yml), loaded from the catalog. One constant SOURCE_SUFFIX
  = "__b25" applies to every dataset the check reran (A3 output, crx_<p>_a3_dues / _a3_payments,
  A1 and A4 outputs); A2 is not rerun, read it persisted. Setting SOURCE_SUFFIX = "" must switch
  the whole snippet to the persisted tables (used after step 8 if the rules change). Do not re-run
  or re-implement the engine. First check it is bundle 25's output: commitments_n is a
  column, and a3_commitments_level takes values in kept / partly_kept / broken / promised /
  no_promise. If not, stop and say so.
- Scored rows = a3_unknown_reason is null. "Accounts in scope" = every row of the month; every
  other count is over scored rows. The document shows three states (High / Moderate / Low); report
  the Unknown count once per model_id as a check, not as a state.
- Months: Results, detail and vintage use persona_end_date's month. Trend uses every month the
  output holds. Validation pools the month ends that leave 3 full months of outcome after them.
- Splits (the definitions the persona code already uses; say which column you took):
  - RL product: rl_spine.loan_type → Personal Loans / Personal Cash Loans / Auto (anything else
    as is, listed separately).
  - DPD band at the observation date: 61–90 / 91–120 / 121–150 / 151–180 at 61–180;
    181–360 / 361–720 / 720+ at 180+. Cards at 180+: from the charge-off age where the spine has
    no DPD.
  - 180+ vintage: early-stage = charged off less than 24 months ago, late-stage = 24 or more
    (CC chargeoff_age_months; RL feat_loan_chargeoff_segment).
- Outcomes, per (account, observation date), over the 3 months after the observation date, from
  the A3 dues and payments (crx_<p>_a3_dues / crx_<p>_a3_payments + SOURCE_SUFFIX):
  - paid_due = payments in the 3 months reach max(one month's due at the observation date,
    100 AED);
  - paid_any = payments in the 3 months reach 100 AED.
- Other axes, persona_end_date's month: A1 ability state and A4 family (+ SOURCE_SUFFIX); A2 (persisted)
  reachability (Reachable / Non-Reachable / Unknown) and location (In Country / Skip / Unknown).

Tables (per model_id; counts unless a % is asked; cells under 10 as "<10")
T1 Results. Accounts in scope, High, Moderate, Low. CC: one row. RL: one row per product and a
   total.
T2 Results detail (scored rows):
   - scored accounts;
   - A levels: kept, partly_kept, broken, promised, no_promise;
   - B levels: regular, some, none;
   - C levels: clean, not_clean, no_record split by pre_dlq_reason (too few months due vs
     censored = delinquent since before the history we hold);
   - a3_points_total 0..6 (any other value: list it, it is a defect);
   - refusal flag; refusals that lower the state (the state is below the one its points give);
     refusals lifted (refusal_followed_by_plan or refusal_followed_by_payment); dispute; no pickup
     after contact; hung up.
T3 State by DPD band: High / Moderate / Low counts per band.
T4 Trend: High / Moderate / Low counts per month end, labelled "Jan 2026" style.
T5 180+ vintage (180+ only): accounts in scope, High / Moderate / Low per vintage.
T6 Validation (pooled outcome months; give the months):
   - per state: n, paid_due %, paid_any %;
   - paid_due % by state within each group: DPD band; RL product (RL); vintage (180+);
   - AUC of the state on paid_due: overall, within each DPD band, and of a3_points_total;
   - paid_due % by a3_points_total 0..6, with n;
   - stability, accounts present in consecutive months, pooled: same state %, up %, down %, High
     staying High %, Moderate staying Moderate %;
   - Cramér's V of the A3 state with A1, A2 reachability, A2 location and the A4 family (latest
     month).
T6b Is the Broken level needed? (pooled outcome months, as T6). Broken scores 1 like Promised, so
   only Broken rows with commitments_kept >= 1 would move without it.
   - Split Broken rows by trigger: streak (commitments_last_broken_n >= 3) only, rate (>= 2
     concluded, kept rate < 40%) only, both; and within each by commitments_kept >= 1 vs 0.
   - Per cell: n, paid_due %, paid_any %, with Kept, Partly kept and Promised rows beside them
     for comparison, plus a 95% interval for (Broken with a kept event) minus Partly kept.
   - Without Broken: level = kept (>= 2 concluded, kept rate >= 80%), else partly_kept (any kept),
     else promised (any event), else no_promise; recompute points and state with the T7 rule.
     Report the state AUC on paid_due with and without Broken (overall and per DPD band), the
     share of rows whose state changes, and the from × to state counts.
T7 Checks: Unknown count; rows whose a3_points_total differs from the points of their three levels
   (Kept 3 / Partly kept 2 / Broken 1 / Promised 1 / No promise 0; Regular 2 / Some 1; Clean 1)
   and rows whose state differs from the points and refusal rule (High from 4, Moderate from 2,
   one level down for a refusal): both expected 0.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name;
aggregates only, no account / agreement / CIF ids. A part that fails records its error and the
rest still runs. Performance: literal date filters right after catalog.load; one pass per table
group over a localCheckpoint of the joined frame; broadcast the small tables; no row-level
collect; for the AUCs at 180+ aggregate to (score, outcome) counts first. Work in a new tracked
folder tmp_validation/a3_results/ and commit only that.

Deliverables
1. Snippet + README_a3_results.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_a3_<model_id>.md.
3. Back in UAT: summary_a3_results.md, which the user pastes back to Claude.
   - All four model_ids together, one markdown table per T-table with a model_id column, in the
     row order above, numbers only (no prose inside tables).
   - Under 300 lines.
   - End with six lines: does High > Moderate > Low hold on paid_due in every group; does Broken
     with a kept event pay like Partly kept or below it, and does dropping Broken raise or lower
     the state AUC (T6b); how the
     state mix compares with the earlier back-test (cards 61–180 High / Moderate / Low 11.8 /
     32.9 / 55.3%); where A3 overlaps the other axes most; the T7 checks; anything that looks
     wrong.
````
