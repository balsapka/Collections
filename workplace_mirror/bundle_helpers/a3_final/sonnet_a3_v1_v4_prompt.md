# A3: validations V1–V4 before the refactor (prompt for the UAT Sonnet)

Give the block below to the UAT Sonnet 5.5 as it is. The user runs its snippet in PROD for each
model_id A3 has output for (switch `model_id` in `globals_dev.yml`), commits the results files, and
pastes the summary back here. The spec behind it is `specs/A3_credibility_spec.md` (V1–V4).

````text
Goal
We are redesigning A3 payment credibility (DE code: src/enbd_collections/pipelines/crx_persona/
cc_a3_payment_credibility/, rl_a3_payment_credibility/, the code lists in crx_persona/_dcore_codes.py).
Before we design it, measure four things on PROD with aggregates only. Change no pipeline code; read
the existing A3 outputs and their inputs as they are.

What A3 measures (decided)
Payment credibility: how far we can believe this customer will pay this debt. Two kinds of evidence:
trust (promises and arrangements kept; stated refusal) and flow (payments while delinquent; the record
before delinquency). Not capacity (A1), not reachability / location (A2), not the DPD path (A4).
A strong negative stays only if it adds evidence the points don't carry, rests on reliable data, does
not re-derive another axis, and moves states sensibly. These validations decide which ones pass.

Decisions already taken that the measurements must follow
- Anchor = the latest spell start as of the observation date: the start of the current delinquency
  episode from the A4 engine (`months_before_spell` in crx_persona/_dpd_journey). Find where it is
  persisted for CC and RL (A4 output or dpd sequences); if it is not persisted, use the A3 output's
  t0 and say so in the summary. "In the delinquency" below means [anchor, observation_date).
- DCORE evidence is per account: link account -> agreement through prm_dcore_account_agreements.
- Band rules by model_id: *_60_180 -> 61-180 rules, *_180_plus -> 180+ rules.
- 100 AED minimum: a "payment" below means a CC billing cycle (or an RL month) whose payments sum to
  >= 100 AED. The any-payment window is 3 months (61-180) / 12 months (180+).
- Contact days: distinct dates with action_code in CALL_CODES. 3 days at 61-180, 6 at 180+.
- Population: the latest month only (the month of params crx_persona.persona_end_date), rows of
  crx_cc_a3_payment_credibility / crx_rl_a3_payment_credibility. CC observation dates may still be
  mid-month billing dates: select by month, never join other axes on the exact date (match the month).

V1 – DCORE commitments
a) Describe dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement,
   dcore_prm_settlement_schedule_instalments as A3 uses them: key and link columns, due / paid amount
   columns, instalment_status and is_cancelled value counts, and what dcore's instalment_amount_flags /
   null_cancelled_instalment_fields call paid / overdue / pending. Note each table's catalog layer.
b) Recount, per agreement of the population, concluded and kept instalments (PTP + settlement pooled;
   concluded = due on or before the observation date and paid or overdue; window = due date in
   [max(anchor, obs - 12 months), obs]). Compare with dcore_feat_ptp / dcore_feat_settlement
   *_instalment_due_cnt_12m / *_paid_cnt_12m: rows equal, rows different, and the mean difference.
   Then the resulting Dimension A level (kept / partly_kept / thin / broken, same rule as
   derive_commitments_level) old vs new: crosstab.
c) Promise vs ledger: for every concluded instalment in b), did the money actually arrive?
   CC: payment transactions (crx_cc_transactions, txn_category = payment, is_post_block_x_fee = 0) of
   the agreement's account dated from the plan start (PTP: coalesce(promise_start, event_date);
   settlement: event_date) to the due date, and separately up to due date + 5 days. RL: total_paid of
   int_loan_master in the due month. Kept by ledger = that sum >= due_amount.
   Report the 2x2 DCORE status (paid / overdue) x ledger (kept / not kept), for PTP and settlement
   separately, overall and for the latest 3 months of due dates. Then the Dimension A level by DCORE
   vs by ledger: crosstab.

V2 – strong-negative candidates (each measured on its own)
Use the code lists in _dcore_codes.py; result names compared upper-cased and trimmed.
- Explicit refusal: the latest right-party contact in the delinquency is REFUSE TO PAY, REFUSED TO PAY,
  KSA/REFUSE TO PAY or REWRITE NOT AGREED, and after it up to obs: no PTP / settlement started and no
  payment (CC cycle / RL month >= 100 AED).
- Dispute: the same rule with DISPUTE / KSA/DISPUTE.
- Avoidance:
  N0 today's no-response rule as in _strong_negative_reason (3 days in every band).
  N1 live-line no-pickup outcomes (RINGING set, NO ANSWER, LEFT_MSG) on >= 3 days (61-180) / >= 6 days
     (180+) in the delinquency, no NOT_REACHABLE outcome between the first and last of them, no plan
     started in the delinquency, no payment in the any-payment window.
  N2 N1, counting only days after a right-party contact earlier in the delinquency.
  N4 the latest right-party contact is CUSTOMER HUNG UP / CUSTOMER_HUNG_UP, nothing after (as refusal).
For each candidate: rows firing (n, %); crosstab with A2 reachability (non_reachable / reachable /
unknown; find the A2 output column, match by account and month); the A3 state with only
broken_commitments as negative (baseline) vs baseline + this candidate (crosstab, rows moved); the
result names driving it (top 15 with counts); pairwise overlap between candidates.
Also: how often each REFUSING name and CUSTOMER MISBEHAVED is the latest right-party contact, and how
many rows would change rpc_confirmed if HISTORICAL PROMISE TO PAY and RETAIN PTP counted as right-party.

V3 – overlap with the other axes (latest month, match by account and month)
- Dimension C level (clean / not_clean / no_record) x A4 state, and x A4's prior-episode features
  if persisted (n_prior_episodes buckets 0 / 1 / 2+; clean_gap_before_current buckets).
- Dimension B level (regular / some / none) x A4 state.
- A3 state x A1 state; A3 state x A2 reachability.
Report counts and row %; say in one line per crosstab whether the A3 level adds anything beyond the
other axis (e.g. does clean / not_clean split each A4 state, or is it nearly determined by it).

V4 – threshold sensitivity
Recompute the A3 state (same ladder as _a3_state_col, baseline negatives as today) moving one
threshold at a time one step either way: High from 3 / 5 points; Moderate from 2; kept rate 70% / 90%;
broken rate 30% / 50%; broken streak 2 / 4; concluded needed 1 / 3; Regular 1 / 3 of 3 (61-180) or
2 / 4 of 6 (180+); record clean share 70% / 90%; record months due 2 / 4. Use the intermediate
signal datasets (crx_*_a3_commitment_signals, *_dlq_payment_signals_single_payment_cycle_count,
*_pre_dlq_payment_signals_single_payment_cycle_count) for the inputs. Per variant: state distribution
and rows that change state vs today.

Rules
catalog.load only (no spark.read, no paths); model_id = catalog.load("params:model_id"), in every output
file name; aggregates only, no account / agreement / CIF ids, cells under 10 shown as "<10"; a part that
fails records its error and the rest still runs; filter DCORE and transaction tables early by date.
Work in a new tracked folder tmp_validation/a3_v1_v4/ and commit only that.

Deliverables
1. Snippet + README, pushed from UAT. The README names the A4 / A2 / A1 output columns you used.
2. The user runs it in PROD per model_id and commits results_<model_id>.md (or .json).
3. Back in UAT: summary.md, under 120 lines: one section per validation, per model_id. V1: the
   column / status facts, recount agreement %, DCORE-vs-ledger agreement % (PTP, settlement).
   V2: one row per candidate (fires %, % of it that is A2 non_reachable, rows moved, top names).
   V3: one line per crosstab (adds / mostly duplicates, with the key numbers). V4: one row per
   variant (rows changing state, %). End with anything that looked wrong in the data.
````
