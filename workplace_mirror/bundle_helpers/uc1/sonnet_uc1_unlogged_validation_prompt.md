# UAT Sonnet prompt: verify "promises said on calls are not logged in DCORE" against the raw data

Paste everything below the line into the UAT Sonnet session.

---

Goal
Our UC1 analyses found that most promises customers make on calls have no DCORE promise: 60% (cards) / 81% (loans) of
transcript promises with no DCORE promise on the customer within ±7 days (interim run), 41% / 70% at the July month end
(bundle 31 flag `stated_promise_unlogged_flag`). Before this goes to GRR it must be proven from a data perspective:
either the promises truly are not in DCORE, or our matching misses them. Assume nothing; check every link from the raw
call to the raw DCORE records.

What our matching did (to be tested, not trusted)
- Call date: `crx_uc1_metadata.conversationstart` cast to a date (time zone never checked); UC1 evidence dated by
  `observed_at` (midnight of the customer-day). In bundle 31 the anchor was the customer's last conversation before the
  month end, not necessarily the call with the promise.
- Promise on the call: UC1 intent paying (payback_full / partial / with_delay) plus an amount or date mentioned.
- DCORE side: A3's promise events (`crx_<p>_a3_promise_events`: event_date, promise_cutoff), built from
  `dcore_prm_followup_outcomes` promise result codes and the PTP / settlement instalment tables, through
  `prm_dcore_account_agreements` (model-scoped: only agreements of accounts in this model's base).
- "Logged" = an event of any of the customer's accounts in the base alive within ±7 days of the call.

Hypotheses to test (each one: how many unlogged cases it explains)
H1 Time zone / timestamp: call timestamps in UTC vs DCORE in local time (UAE, +4) or the reverse; a date shift at
   the day boundary. Report the hour-of-day distribution of `conversationstart` and of DCORE `action_ts`, and redo the
   match with a ±1 day shift.
H2 Wrong DCORE date: the match used the promised payment date or the event date instead of the entry date (or the
   reverse). Redo with each date column the raw tables hold (entry / created, action, promised payment, plan start).
H3 Scope of the agreement map: the promise was logged on an agreement outside `prm_dcore_account_agreements` (other
   product, closed or written-off account, an account not in this model's base, a CIF-level agreement). Redo against
   ALL DCORE agreements of the customer (raw DCORE customer / agreement tables; find them), not the model map.
H4 Codes: the promise was logged under a result code A3 does not count (payment arrangement, settlement, will pay,
   callback with amount, digital collect, ...). List every DCORE follow-up result code / name recorded on the
   customer within ±3 days of the call, ranked by frequency, for unlogged vs logged cases.
H5 Raw PTP tables: the promise is in `dcore_int_ptp` / `dcore_int_settlement` / the instalment tables but dropped on the
   way into A3 (filters, de-duplication, event merging). Match the raw tables directly.
H6 Not a collections call: the call was not handled in the collections workflow (inbound service, another
   department, a vendor). Share of unlogged cases with ANY DCORE follow-up of any code on the customer that day; call
   direction, queue / campaign or any metadata field that identifies the team (say what exists).
H7 Load lag / coverage: DCORE rows missing for some dates (load gaps). Daily counts of DCORE follow-ups and PTPs over
   2026-03 .. 2026-08 next to daily call counts; any gap days.
H8 Extraction error: UC1 says a promise was made but the transcript does not show one. For a sample, read the
   transcript text around the promise (find the raw transcript table UC1 reads; say which).
H9 Wrong call: the promise call is not the call we anchored on (bundle 31: last call before the month end). Redo with
   the customer-day UC1 marks as the promise (from `proposer_level_observations`, intent levels, transcript source).

Work plan
1. Locate the raw tables (catalog first, then the shared store and the DCORE raw layer): transcripts, call metadata,
   DCORE follow-ups (raw and prm), PTP, settlement, instalments, DCORE customer / agreement master. Report each one's
   key columns, date / timestamp columns with their time zone if documented, and date range.
2. Rebuild the promise set from scratch: transcript customer-days with a paying intent and an amount or date mentioned
   (cards and loans 61-180, March-July 2026). n customers, n customer-days.
3. Population checks (all cases, aggregates): the unlogged share under the original matching, then with each fix
   H1-H5, H9 applied one at a time and all together. A waterfall: original unlogged share → after each fix → final.
4. Case review (PROD only, nothing committed): a random sample of 40 still-unlogged cases per product. For each, show
   on screen the promise sentence from the transcript, the call timestamp, and every DCORE row of the customer (all
   agreements, all codes, raw tables) from 14 days before to 14 days after. The user reads them and records only a
   class per case: (a) UC1 extraction error, (b) logged but missed by matching (which reason), (c) not a collections
   call, (d) truly not logged. The committed results hold the class counts only.
5. Also the reverse, for scale: DCORE promises entered on a call day where UC1 found no paying intent (sample 20 per
   product, same classes).

Rules
catalog.load where datasets are catalogued; raw tables that are not may be read read-only with the same session
(say how). model_id = catalog.load("params:model_id"). Committed outputs: aggregates and class counts only, no account,
CIF, agreement, conversation or agent ids, no transcript text, no notes; cells under 10 as "<10". Step 4 is shown on
screen only, never written to a file. New tracked folder tmp_validation/uc1_unlogged/; commit only that folder. No
pipeline, catalog or registry change.

Deliverables
1. Snippet + README; the user runs it in PROD for cc_60_180 and rl_60_180, does the case review and commits
   results_<model_id>.md.
2. Back in UAT: summary_uc1_unlogged.md (under 150 lines): the tables found (step 1), the waterfall (step 3), the case
   classes (steps 4-5), and one verdict line per hypothesis H1-H9 (explains n% of the gap / does not). End with the
   verified unlogged share per product and whether the remaining gap is agent logging, data linking, or not
   collections calls.
