# UAT Sonnet prompt: UC1 transcript signals — where they add, whether they fit our data

Paste everything below the line into the UAT Sonnet session.

---

Goal
The first UC1 / UC2 validation (tmp_validation/uc1_uc2/, 60-180 only) tested only stated capacity and
stated intent, pooled across all A1 / A3 states, on a 1-month paid_due window. Across all states they
added little, but inside A1 Unknown and inside A3 Low the stated level did separate payers (cc A1
Unknown: able 21.4% / partly 17.0% / not stated 15.6% / unable 12.0% vs no reading 8.2%; cc A3 Low:
partly_or_later 9.5% vs not stated 4.3%). We now want the full picture of what the transcript signals
can do for the persona, judged on our own data and outcomes:
1. which of the other signals (reason, period, repayment specifics, request, dispute) line up with
   payment after the call, beyond the UC2 states;
2. where UC2 has no evidence (A1 Unknown, A3 no_promise), how much a stated signal differentiates;
3. whether what customers say is consistent with what our data shows (salary, CASA, DCORE promises,
   disputes), and whether the inconsistent cases behave differently;
4. how many accounts a full UC1 run over all transcripts could cover, 180+ included.

Decided, to follow
- UC1 signals are what the customer said on the call, as extracted. We never treat them as true. We
  test only (a) whether they line up with what the customer does next and (b) whether they are
  consistent with observed data. Do not use the UC1 team's own corroboration.
- Legacy-format extractions are out (as in the first validation): a conversation whose only rows have
  model_version = 'legacy' does not exist for this work.
- model_ids: Part A all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus); Parts B–F
  cc_60_180 and rl_60_180 (if Part A finds 180+ customers with extracted conversations, run B–F there
  too and report n).
- Unit for Parts B–F: the conversation. Each current-format extracted conversation of a CIF in the
  model, call date 2026-03-06 .. 2026-07-16, joined to every account of that CIF in crx_<p>_obs_base at
  the last month end strictly before the call date. UC2 states, supporting signals and DPD band come
  from that month end (point in time). Report n conversations and n distinct accounts in every table.
- Signal level per conversation: the detected (primary) level per slot from
  crx_uc1_signal_level_conflicts (slot = the part of value before ':'). Where a confidence field
  exists, every Part B and D table also gets a high-confidence-only version; say which field.
- Outcomes after the call date, per account, from crx_<p>_a3_payments and crx_<p>_a3_dues:
  pay30_due = payments in days 1–30 after the call ≥ max(one month's due at the prior month end,
  100 AED); pay30_any = payments in days 1–30 ≥ 100 AED; pay45_due / pay45_any the same over 45 days;
  days_to_pay = days to the first payment ≥ 100 AED, within 45 days. Payments end 2026-08-31, so 45 days
  is the longest window every call has. Statements like with_delay, partial or "weeks" may pay late or
  below the due: always show the 45-day and the _any versions next to pay30_due.
- Observed data (catalog, read only): income per CIF month = larger of
  feat_cif_internal_salary_monthly.salary and feat_cif_bureau_salary_monthly.bureau_salary (A1's
  rule); feat_cif_casa_balance_monthly; feat_cif_casa_inflow_outflow_salary_monthly; "has CASA with us"
  = any CASA balance row in the 6 months before the call. DCORE promises and disputes: what A3 reads
  (prm_dcore_account_agreements; a3_dispute_flag on crx_<p>_a3_payment_credibility). RL restructures:
  crx_rl_restructure_chains or the A4 restructure flag (say which).
- Persisted outputs as they are now; do not re-run or re-implement any engine. Keep Unknown and
  not-detected as their own rows.

Part A — Coverage a full UC1 run could reach (all four model_ids, month ends 2026-03 .. 07)
A1 Per month end: account-months with any conversation in the prior 90 days (metadata, legacy
   dropped) and with an extracted one; split by a1_state, a3_commitments_level, DPD band.
A2 Extracted vs not-extracted conversations: call month, and every metadata field that could explain
   the selection (duration, direction, campaign, agent group or whatever exists; say which); the date
   range of each group.
A3 Do 180+ customers have conversations in the store at all (counts per month end)?

Part B — Other signals vs payment after the call
B1 For each level of delinquency_reason, payment_period, repayment_specifics (amount_mentioned,
   date_specific, plan_structure_mentioned), request_type and dispute: pay30_due, pay30_any,
   pay45_any, median days_to_pay; reference row = conversations where that slot is not detected.
B2 The same within each a1_state and within each a3_state.
B3 Capacity and intent redone on this call-anchored basis, all outcomes, overall and within states.

Part C — Stated vs observed (consistency, not truth)
For delinquency_reason lost_employment / reduced_employment / has_employment / increased_obligations
and payment_capacity none / full:
C1 Share with income > 0 per month relative to the call month (−6 .. +2), per claim.
C2 Class per conversation: income_stopped (income in ≥ 1 of months −6..−3, none in −1 and 0);
   income_dropped (income in −1 or 0 below 70% of the −6..−3 average); income_continues (other cases
   with income in −1 or 0); never_visible (no income in −6..0). Claim × class, split by has CASA with us.
C3 pay30_any and pay45_any by claim × class.
C4 payment_capacity none: CASA balance at the prior month end ≥ one month's due; CASA inflows in the
   call month; share and payment.

Part D — Where UC2 has no evidence
D1 a1_state = Unknown: stated capacity and stated reason → all outcomes; AUC on pay45_any of the order
   able > partly_able > not stated > unable among Unknown conversation holders.
D2 a3_state = Low, split by a3_commitments_level (no_promise vs the rest): stated intent and
   repayment_specifics (amount or date named) → all outcomes.
D3 Month-end view, as the block would be used: at month ends 2026-05 .. 07, A1 Unknown account-months
   by the latest stated capacity in the prior 90 days → 1-month paid_due / paid_any as in the first
   validation.

Part E — Discrepancy flags (each: n, pay30_due, pay30_any, pay45_any, and its concordant comparison)
E1 Says able / full, or intent payback_full, while a1_state = Low.
E2 Says capacity none, while a1_state is High or Moderate, or the CASA balance ≥ one month's due.
E3 Says has_employment, while a1_salary_stopped or C2 income_stopped.
E4 Says lost_employment, while C2 income_continues.
E5 Transcript promise (intent payback_full / partial / with_delay with amount_mentioned or
   date_specific) with no DCORE promise on the account within ±3 days of the call; and the reverse
   (DCORE promise within ±3 days, stated intent no_payment or not stated). Share of each; pay30_due of
   unmatched transcript promises vs transcript promises that match a DCORE promise vs DCORE promises
   with no conversation.
E6 Stated dispute while a3_dispute_flag is false at the next month end; and the reverse.
E7 Stated intent no_payment while a3_state = High.

Part F — Requests
F1 request_type × a1_state × a3_state (counts: demand for each treatment).
F2 pay45_any per request type, within a1_state.
F3 RL: restructured within 90 days after a restructure request vs RL conversations without one (say
   how far the data reaches), and pay45_any after.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF / conversation ids in any output; cells under 10 as "<10". A part
that fails records its error and the rest still runs. Reuse the loaders and point-in-time joins of
tmp_validation/uc1_uc2/ if they are still there. Performance: literal date filters right after
catalog.load; scope UC1 tables to the model's CIFs first; one pass per table group over a
localCheckpoint of the joined frame; broadcast small tables; no row-level collect; AUCs from (score,
outcome) counts. New tracked folder tmp_validation/uc1_signals/, commit only that. No pipeline,
catalog or registry change.

Deliverables
1. Snippet + README_uc1_signals.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_uc1_signals_<model_id>.md.
3. Back in UAT: summary_uc1_signals.md, which the user pastes back to Claude.
   - All model_ids together, one markdown table per numbered table with a model_id column, numbers
     only inside tables; under 300 lines.
   - End with one verdict line each: full-run coverage at 60-180 and 180+ (A); which non-capacity /
     intent signals separate payers beyond the UC2 states (B); does the call-anchored, 45-day basis
     change the capacity / intent picture (B3); how consistent stated job / income claims are with our
     income data, and does consistency matter for payment (C); does stated ability differentiate inside
     A1 Unknown, and stated intent inside A3 no_promise (D); which discrepancy flags behave differently
     from their concordant group (E); do transcript promises carry evidence DCORE misses (E5); what the
     requests say about treatment demand (F).

---

Follow-up run (2026-11-19, after the 60-180 results)
Paste below the line into the same UAT Sonnet session.

---

Two additions to tmp_validation/uc1_signals/, same rules and deliverable format (summary_uc1_signals_followup.md):
1. Run Part A (and B–F only where n allows) for cc_180_plus and rl_180_plus.
2. 60-180 again, E5 and E6 at CIF level: a DCORE promise (or dispute) on any account of the conversation's CIF within
   ±3 days (and ±7 days) of the call, beside the account-level result. Report how many unmatched transcript promises
   become matched, and pay30_due / pay45_any of the still-unmatched vs the matched vs no promise at all. For E5.3,
   split the DCORE promise events without a conversation by promise source (plan vs follow-up note, and the follow-up
   code: digital collect, will pay at salary, etc.), to explain why they pay 41% against 15% for those with a call.
