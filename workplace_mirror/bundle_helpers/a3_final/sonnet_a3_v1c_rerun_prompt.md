# A3: V1c rerun with the corrected ledger allocation (follow-up prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet in the same `tmp_validation/a3_v1_v4/` work. Run in PROD for
cc_60_180 and rl_60_180, then paste `summary_v1c.md` back here. Why: the first V1c compared payments
summed from the plan start with one instalment's amount, so later instalments counted as kept from
earlier money (`v1_v4_review.md`).

````text
Rerun V1c only (DCORE status vs ledger), with a corrected ledger rule. Same population, anchor,
window, tables and rules as the V1–V4 snippet; reuse its persisted base where it exists.

Ledger rule (replaces the old one)
For each plan (PTP: promise_seqno, start = coalesce(promise_start, event_date); settlement: rps_seqno,
start = event_date), order its non-cancelled instalments by due_date. Cumulative due up to an instalment
= the sum of due_amount of it and every earlier instalment of the plan. Cumulative paid by a date = the
customer's payments to the account from the plan start up to that date:
CC: crx_cc_transactions, txn_category = payment, is_post_block_x_fee = 0;
RL: int_loan_master.total_paid, months from the plan-start month up to the due month.
An instalment is kept by the ledger when cumulative paid by its due date >= its cumulative due.
Report two cut-offs: by the due date, and by the due date + 5 days (CC only; RL is month-level).

Report, for PTP and settlement separately, CC and RL, overall and for the latest 3 months of due dates:
1. the 2x2 DCORE status (paid / overdue) x ledger (kept / not kept), counts and row %;
2. agreement %, and Cramer's V;
3. the same split by plan length (1 instalment / 2-3 / 4+), since the allocation matters most for long plans;
4. the Dimension A level by DCORE vs by ledger (crosstab), with today's thresholds.

Also check: do HISTORICAL PROMISE TO PAY and RETAIN PTP occur in dcore_prm_followup_outcomes at all
(row count per name, latest 12 months, the model's agreements)?

Rules as before: catalog.load only; model_id from params, in the file name; aggregates only, cells under
10 as "<10"; filter early to the population and the date range.

Deliverables: results_v1c_<model_id>.md, then summary_v1c.md (under 40 lines): agreement % per product
and plan type at both cut-offs, the plan-length split, the level crosstab, and one line on whether
DCORE's status can stand in for the ledger.
````
