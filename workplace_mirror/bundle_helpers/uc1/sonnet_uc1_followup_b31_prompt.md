# UAT Sonnet prompt: UC1 follow-up on the bundle 31 block (workshop numbers)

Paste everything below the line into the UAT Sonnet session.

---

Goal
Three extra cuts of the UC1 stated block (`crx_<p>_uc1_stated`, bundle 31, scored at the 2026-07-31 month end) for the
workshop: (1) what UC1's transcript reading shows against its remark reading, (2) how much money sits behind each UC1
signal, (3) why A1 Unknown customers are delinquent.

Decided, to follow
- Read the persisted outputs as they are; no pipeline, catalog or registry change. model_ids: cc_60_180 and
  rl_60_180 (180+: counts only).
- Month end 2026-07-31; outcome = paid_due / paid_any over August, exactly as the B31 check computed it (payments in
  the month after the month end reaching max(the due at the month end, 100 AED) / 100 AED, from crx_<p>_a3_dues and
  crx_<p>_a3_payments). Join A1 (crx_<p>_a1_ability.a1_state), A3 (crx_<p>_a3_payment_credibility: a3_state,
  a3_commitments_level) on (account_id, observation_date).
- Best effort, no n gate: show n and a bootstrap 95% interval (account resampling, 200 draws) for every paid difference.

Tables
T1 Transcript vs remark. For UC1 rows, map `a5_latest_value` / `a5_remark_value` and `a6_latest_value` /
   `a6_remark_value` to the A5 / A6 states (same mapping as the block; `not-detected` → not stated). Per source:
   - A5 inside A1 unknown: paid_due per state and the AUC of able > partly > not stated > unable;
   - A6 inside A3 no_promise and inside A3 promised: paid_due per state and the AUC of pays in full > partly or later >
     not stated > refuses;
   - agreement of transcript and remark state where both exist (share equal), and paid_due when they agree vs differ.
T2 Money at stake (AED, aggregates only). For each group: accounts, sum of the due at the month end, sum of the
   outstanding balance at the month end (say which column and table), and August payments:
   - stated_promise_unlogged_flag = 1, split by a3_commitments_level;
   - A1 unknown by a5_state;
   - a5_reason = lost_employment and = reduced_employment;
   - all UC1 rows, and the whole book, for scale.
T3 Reason inside A1 unknown: distribution of a5_reason (incl. none) by product and DPD band, with paid_due, and the same
   for A1 low / moderate / high for comparison.

Rules
catalog.load only; model_id = catalog.load("params:model_id") in every output file name; aggregates only (no account,
CIF or conversation ids, no free text); cells under 10 as "<10". New tracked folder tmp_validation/uc1_b31_followup/;
commit only that folder.

Deliverables
1. Snippet + README, pushed from UAT; the user runs it in PROD per model_id and commits results_<model_id>.md.
2. Back in UAT: summary_uc1_b31_followup.md (under 120 lines, one table per item with a model_id column), ending with
   one line each: does the transcript reading separate payers better than the remark reading; AED at stake behind
   the unlogged promise and the A1 Unknown order; the reason mix inside A1 Unknown.
