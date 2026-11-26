# UAT Sonnet prompt: UC1 signals and reachability (going dark; unreachable but talking)

Paste everything below the line into the UAT Sonnet session. Deadline: results the same day.

---

Goal
Two questions about UC1 signals and A2 reachability, on UC1's August refresh:
Q1 Which UC1 signals come before a customer goes from Reachable to Non-Reachable the next month?
Q2 Are there accounts A2 calls Non-Reachable whose customer had a recent conversation in UC1, and did any of those
   conversations carry a positive signal? How many, what do they owe, and do they pay?
Data understanding and sizing only: no pipeline change, no A2 rule change.

Decided (do not reopen)
- Axis numbers: A1 deterioration, A2 locatability, A3 credibility, A4 ability (`crx_<p>_a1_ability` holds the A4
  states). A2 is fixed and signed off: `reachability_state` reachable / non_reachable / unknown; Non-Reachable = the
  last 3 failed attempt days (6 at 180+) in the window, no contact since; A2 reads DCORE on the account's own
  agreements. A2's output carries `last_contact_date` and `last_attempt_date`: use them.
- UC1 readings as in `tmp_validation/uc1_latest/`: posteriors top level on the month end (any age, and evidence in the
  last 90 days), the export at 07-31, evidence dates from `proposer_level_observations` (08-31 partition), split
  transcript / remark. Stated-block mapping from `crx_persona/uc1_stated/classify.py`.
- Positive signal = stated ability able or partly able; intent pays in full or partly or later; reason has employment
  or increased obligations; an amount or a date named (export only); request stated. Negative = intent refuses;
  ability unable; reason lost or reduced employment; dispute stated. Report each signal and "any positive".
- No minimum n; n beside every share; 95% intervals from 200 account resamples for the differences quoted.
- Signal age decides how a signal is read: a customer's situation changes, so a statement from four months ago is not
  a statement about today. For every signal, age = days from the latest evidence naming it (on or before the month
  end) to the month end. Every signal table in Q1 and Q2 is shown by age band: 0-30, 31-60, 61-90, 91-180, over 180
  days. Posteriors carry old values forward, so take the age from the evidence, never from the posterior row. Say
  where a signal holds only when recent.

Q1 Going dark
- Unit: account-months reachable at month end t, t = 2026-04-30 .. 07-31; outcome = `reachability_state` at t + 1
  (non_reachable / reachable / unknown / deceased). The 07-31 → 08-31 pair needs no payments, so use it.
- Rate of going Non-Reachable by each UC1 signal level at t vs readers without that level vs no reading; within A3
  level and within A4 state as well (the base rates differ). Rate ratio and pp difference with intervals.
- The last conversation before t: its stance (signals above), its source (transcript / remark), days from it to t.
- Context only, no UC1: the same rate by A3 level, A4 state, DPD band, location_state.
- 60-180 both products; 180+ if n allows.

Q2 Non-Reachable but talking
- Unit: account-months non_reachable at month end t, 04-30 .. 08-31 (payments only to 07-31).
- Accounts whose CIF has UC1 evidence in the 90 days before t; split by when the latest evidence falls:
  (a) on or before A2's `last_contact_date`; (b) after it, or no contact ever — a conversation A2 does not see.
  Also days from the latest evidence to A2's `last_attempt_date` (did the customer talk after the failed calls began?).
- For (b), why A2 does not see it, on the evidence day: a DCORE right-party contact on another account of the same
  CIF; any DCORE follow-up on the CIF but not a contact; nothing in DCORE (a Genesys-only conversation). Say whether
  the call was inbound or outbound if `crx_uc1_metadata` or Genesys holds the direction (say which field).
- Per group: accounts, amount due, outstanding, location_state, each positive / negative signal and "any positive";
  paid_due next month vs Non-Reachable accounts with no recent evidence.
- All four model_ids (180+ matters: Non-Reachable is common there and a recorded call went with payment).

Rules
`catalog.load` only; reuse the loaders of `tmp_validation/uc1_latest/`; temporary entries only in
`conf/base/catalog/catalog_tmp_uc1_full.yml`, explicit. Persisted persona outputs as they are; do not re-run any
engine. model_id = `catalog.load("params:model_id")`, in every output file name. Join persona rows to UC1 on
`cif_id`. Aggregates only: no account, CIF, agreement, conversation or agent ids, no transcript or remark text;
cells under 10 as "<10". A part that fails records its error and the rest still runs. New tracked folder
`tmp_validation/uc1_reach/`; commit only that folder. No pipeline, catalog (beyond the temp file) or registry change.

Deliverables
1. Snippet + README (one command per model_id), pushed from UAT.
2. After the user commits the PROD results: `summary_uc1_reach.md` (under 150 lines): Q1 table (signal → going-dark
   rate, within A3 / A4, by signal age), Q2 table (by signal age) (groups a / b, the reasons for b, positive signals, amount due, paid_due), a short
   "what this means" list, and what could not be computed and why.
