# A3: detailed results for the model document (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
and pastes `summary_a3_detail.md` back here. The numbers go into the A3 model document
(`docs/credibility/build_a3_workbook.py`: 'Results' and 'Validation' sheets), which the user shows
to GRR.

Why (user, 2026-11-13): the document already has the August state mix, the outcome rates by state
and the back-tests. GRR will ask whether the states hold:
- month to month;
- within loan products and 180+ charge-off ages;
- within DPD buckets;
- and how A3 sits next to the other three axes.

The workplace runs bundle 23's code. Its step 8 has not run, so the persisted A3 output is still
bundle 20's: compute from the engine, not from the persisted table. The deadline is the shipped one
(GRR). The 30-day variant is needed only for the state mix.

````text
Goal
Produce the detailed results tables for the A3 payment credibility model document, for all four
model_ids, under today's rules. Aggregates only, no pipeline change, no real output written.

Decided, to follow
- Engine: the applied code in src/enbd_collections/pipelines/crx_persona/a3_credibility/ and the
  product wrappers. Run the node functions in pipeline order on catalog loads, as the V1h and V1i
  snippets do (reuse tmp_validation/a3_v1h/ or a3_v1i/ code if present). Do not re-implement any
  rule, and do not read the persisted crx_<p>_a3_payment_credibility (it is the previous version).
  GRR = no deadline override. LEN = CC "30_days", RL "30_days_month_end": used for R1 only.
- Months: every persona month the obs base holds (persona_start_date..persona_end_date), scored in
  one engine run. The outcome tables use the month ends that leave 3 full months of outcome
  (expected 2026-03-31..2026-05-31, pooled).
- Outcomes over the 3 months after the observation date, per (account, observation date), as V1h:
  paid_due = payments reach at least one month's due (the A3 dues);
  paid_any = payments >= 100 AED;
  rolled = a worse DPD bucket at month 3 (61-180 only);
  cured = below 61 DPD at month 3 (61-180 only; the definition the other axis documents use);
  exited = not in the base at month 3, its own category, never dropped.
  At 180+ lead with paid_due and paid_any.
- Splits:
  - RL product: rl_spine.loan_type (Personal / Personal Cash / Auto; any other value as is).
  - 180+ charge-off age: < 24 vs >= 24 months. CC: chargeoff_age_months where the spine has it,
    else months since the episode start (say which). RL: feat_loan_chargeoff_segment.
  - DPD bucket at the observation date: 61-90 / 91-120 / 121-150 / 151-180 at 61-180;
    181-360 / 361-720 / 720+ at 180+. Take it from the spine or the A4 output, whichever the
    persona code already joins.
- Other axes, persona_end_date's month, from their persisted outputs (catalog loads):
  - A1 ability state (crx_<p>_a1_ability);
  - A2 locatability (crx_<p>_a2_locatability: location x reachability, plus deceased);
  - A4 deterioration family (the A4 / DPD journey output the persona code reads).

Tables (each per model_id; counts and row %; cells under 10 as "<10")
R1 Trend. State mix (High / Moderate / Low / Unknown) for every persona month, n per month.
   Also persona_end_date's month under LEN.
R2 Detail, persona_end_date's month:
   - level mix of A (Kept / Partly / Thin / Broken), B (Regular / Some / None) and
     C (Clean / Not clean / No record, with No record split by reason: censored / too few months
     due);
   - the points-total distribution (-1..6) with the state each value lands in;
   - refusal rate, and how many states it demotes;
   - the diagnostics: dispute, no pickup after contact, hung up.
R3 Splits, persona_end_date's month. State mix by RL product (RL only), by 180+ charge-off age
   (180+ only) and by DPD bucket (all).
R4 Validation by split. paid_due, paid_any, rolled and cured by state, within each R3 split,
   pooled over the outcome months, with n. Also the state AUC on paid_due within each DPD bucket,
   with a 95% interval (bootstrap over accounts, 200 resamples). Say where the order High >
   Moderate > Low breaks, if anywhere.
R5 Points. paid_due and paid_any (and rolled at 61-180) by points total (-1..6), pooled, with n.
   This is the evidence for the 180+ cut-off question.
R6 Next to the other axes, persona_end_date's month. Crosstab of the A3 state with:
   - the A1 ability state;
   - A2 reachability (Reachable / Non-Reachable / Unknown) and location (In Country / Skip /
     Unknown);
   - the A4 family.
   Row % within the A3 state, plus Cramer's V for each pair. A3 should overlap the others only
   partly; say where it overlaps most.
R7 Stability. For accounts present in consecutive persona months: the A3 state transition matrix
   month m -> m+1, pooled. Share unchanged, up and down, and share moving two steps.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance: one engine run for all months (plus one LEN run for R1);
localCheckpoint the scored output before counting; literal date filters right after catalog.load;
broadcast the small tables; no row-level collect; at 180+ (300k+ rows a month) check the driver
memory before the bootstrap and sample accounts if needed (say so). Work in a new tracked folder
tmp_validation/a3_detail/ and commit only that.

Deliverables
1. Snippet + README_a3_detail.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_a3_detail_<model_id>.md.
3. Back in UAT: summary_a3_detail.md, which the user pastes back to Claude.
   - All four model_ids together; every table in markdown with a model_id column, ready to copy
     into the document.
   - Under 300 lines: drop rows with n < 10.
   - End with five lines of observations:
     - does the order hold in every split and month;
     - how stable the states are month to month;
     - where A3 overlaps the other axes most;
     - what the points total shows at 180+;
     - anything that looks wrong.
````
