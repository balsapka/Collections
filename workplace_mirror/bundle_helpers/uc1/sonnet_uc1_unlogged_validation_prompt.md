# UAT Sonnet prompt: UC1 promises with no DCORE promise — transcript and full DCORE log, case by case

Paste everything below the line into the UAT Sonnet session.

---

Goal
UC1 finds promises to pay in call transcripts. For about 25% (cards) / 30% (loans) of them we find no promise in DCORE
within ±7 days (your last run: `tmp_validation/uc1_unlogged/`, waterfall up to H3). Find out, case by case, what
happened: read the transcript and the customer's entire DCORE log around the call.

Decisions already made (user)
- "Logged" means DCORE holds a promise for the customer: a row in the PTP / settlement / instalment tables, or a
  follow-up with one of A3's promise result codes, on any agreement of the customer, within ±7 days of the call.
- A same-day follow-up with a non-promise code (settlement, callback, already paid, deferment) does NOT make the promise
  logged. If the call held a promise and the promise tables have nothing, that is a DCORE recording / data issue, not a
  match. (This is why A3 also reads follow-up result codes for promises.)
- Drop the broad-name rule (H4) from the definition; keep H1 (±1 day), H2 (all date columns), H3 (all agreements), H5
  (raw PTP / settlement tables).
- The claim "loan promises are often entered on the customer's card" is NOT accepted. Only about 15% of customers have
  more than one product with the bank, but your run found an agreement outside the model map for 74% (cc) / 99% (rl) of
  promise customers. Settle this first (step 1).

Work plan
1. Agreement puzzle (aggregates). For the promise customers:
   - n CIFs with more than one product in our account masters vs n with more than one DCORE agreement; distinct DCORE
     customer numbers per CIF (does the CIF to `icustomerseqno` link fan out?).
   - The agreements outside `prm_dcore_account_agreements`: what each one is per the DCORE agreement master (product,
     status, open / close dates), and whether its account number equals an account of the model's base (same account,
     another agreement id = a gap in our map) or a different account (another product). Say which column "CARD OPEN /
     LOAN OPEN" came from and what it means.
   - For the promise days matched only through an outside agreement (H3): same account vs other product, counts.
   Verdict: real cross-product entries, a gap in our agreement map, or a wrong customer link.
2. Rebuild the "no DCORE promise" set under the definition above (strict promises: paying intent AND amount or date
   named; cc_60_180 and rl_60_180, calls 2026-03-06 .. 07-16). n customer-days; share by call month.
3. Case review (PROD, on screen only, nothing written to a file). Every case if 100 or fewer per product, else a random
   100. For each case show, in one block:
   - the call: date and time, duration; the transcript turns around each promise UC1 flagged (the flagged utterance
     ±5 turns), and UC1's readings for the day (intent, amount, date, reason);
   - the customer's entire DCORE log from 14 days before to 14 days after the call, all agreements, in date order:
     every follow-up (all codes, result name, action / result timestamps, agreement, the agent remark text), every PTP
     header / detail row (with status, amount, promised date, created date), settlement and instalment rows.
   The user records only a class per case:
   (a) no promise on the call: UC1 misread it (already paid, asked for a settlement or deferment, callback, refused);
   (b) promise on the call, and DCORE has it after all (say where: table, agreement, date): our matching missed it;
   (c) promise on the call, a follow-up that day under another code, no promise row anywhere: DCORE did not record it;
   (d) promise on the call, nothing in DCORE around the call at all.
   Also note per case (as a tick, not text): amount / date in the transcript matches a DCORE remark; the follow-up
   remark mentions a promise.
4. Reverse check, same block and classes: 30 random calls per product where DCORE has a promise that day and UC1 found
   no paying intent.

Rules
catalog.load where datasets are catalogued; uncatalogued raw DCORE / transcript tables read read-only in the same
session (say how). model_id = catalog.load("params:model_id"). Committed outputs: aggregates and class counts only, no
account, CIF, agreement, conversation or agent ids, no transcript or remark text; cells under 10 as "<10". Step 3 and 4
blocks are printed to screen only. Reuse tmp_validation/uc1_unlogged/; commit only that folder. No pipeline, catalog
or registry change.

Deliverables
1. Snippet + README; the user runs it in PROD for cc_60_180 and rl_60_180, does the case review and commits
   results_case_review_<model_id>.md (step 1 tables, step 2 counts, class counts per product, the two ticks).
2. Back in UAT: summary_uc1_case_review.md (under 100 lines): the agreement verdict, class counts with shares, and the
   resulting split of the ~25-30%: UC1 misreads / matching misses / DCORE not recording.
