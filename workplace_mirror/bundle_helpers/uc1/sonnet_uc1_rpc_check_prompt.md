# UAT Sonnet prompt: is a DCORE right-party contact a real conversation?

Paste everything below the line into the UAT Sonnet session. cc_60_180 first, then rl_60_180. 180+ is not needed.

---

Goal
The GRR deck uses "right-party contact (RPC) since March" as the upper bound for UC1 coverage: 50.8% of card and 57.2% of
loan accounts at 61-180 had one between March and August. We are not sure an RPC is always a conversation with the
customer:
- the right-party list (`RIGHT_PARTY_CONTACT` in `crx_persona/_dcore_codes.py`) holds results that may not be a talk with
  the customer: payment confirmations (CUSTOMER MADE PAYMENT, ACCOUNT PAID, PARTIALLY PAID, CLAIMS MADE PAYMENT), other
  channels (E MAIL RECEIVED, FIELD VISIT DONE / REJECTED, DIGITAL COLLECT  PTP SUBSCRIBED), labels (CUSTOMER BEHAVIOUR
  GREEN / ORANGE / RED / YELLOW) and barely-connected calls (KSA/CONNECT AND DROP, CUSTOMER HUNG UP);
- only about 13% of card RPC days and 5% of loan RPC days have a Genesys transcript for the CIF on the same day;
- about 1 in 5 accounts with a Genesys transcript in the last 90 days has no RPC in those 90 days;
- call transcripts have two sources: Genesys until before August 2026, PCA from August on. Every earlier run used Genesys
  only, so September-October calls were never counted.
Find out what the RPC measures, why so few RPC days have a transcript, and what the upper bound is when only real
conversations count. Data understanding only: no pipeline change, no A2 rule change.

Four questions
R1 Composition. RPC events and RPC days (CIF × day), March-August 2026, by result name, call code (OC / CB / IC),
   category (SUC or not) and channel or team (whatever fields `dcore_prm_followup_outcomes` has for in-house vs agency vs
   KSA, dialler or queue; list them in the README). Mark each result name as conversation / not a conversation /
   unclear, with a one-line reason, and give the share of RPC days each class makes up.
R2 Transcript match. For each result name, call code and channel: the share of RPC days with a transcript (Genesys or
   PCA, and each source apart) for the same CIF on the same day, within ±1 day and within ±3 days. Run it March-August
   and, separately, for August-October (the PCA months), as far as DCORE and the transcripts go. The reverse: transcripts
   with no RPC on the CIF within ±1 day, by source, and what DCORE shows then (an attempt code, an inbound call without a right-party result, a SUC call
   outside the list, nothing).
R3 Sources, linking and volume. For each source (Genesys: `stg_genesys_transcripts`; PCA: find its dataset in the
   catalog and name it in the README):
   - how a transcript links to a CIF (the field used; share with no CIF or no match; duplicates; the date field and its
     time zone);
   - transcripts per month as the source stands in PROD now (first and last date): all, with a CIF, with a CIF in the
     persona base at 61-180;
   - the hand-over: the last Genesys month, the first PCA month, and calls found in both (same CIF and day);
   - whether PCA transcripts reach UC1: share in UC1 metadata and in the extraction ledger, by month.
   The user knows of more than 150,000 transcripts including September and October; our runs saw Genesys only, to
   2026-08-29. Say how the two sources add up to that number.
R4 Revised upper bound. Recompute "had a conversation" under four definitions, at 07-31 for the last 90 days and per
   account for March-August, cards and loans 61-180:
   (a) RPC as today;
   (b) conversation results only (drop the "not a conversation" class from R1; report "unclear" both ways);
   (c) (b) plus inbound calls and SUC-category calls outside the list (what A2 also counts as contact);
   (d) (b) or any transcript on the CIF (Genesys or PCA).
   Then the transcript share (both sources together, and each apart) and the UC1 reading share against each, as on the deck (any time March-August; last
   90 days to 31 July).

Decided (do not reopen)
- A2 is signed off. If R1 shows A2's contact uses non-conversation results, report how many reachable accounts at 07-31
  rest only on them, as an observation; do not change A2.
- RPC as the deck counts it: a DCORE event with a code in `CALL_CODES` (OC / CB / IC) and a result in
  `RIGHT_PARTY_CONTACT`, read in the CIF view (any agreement of the CIF) and the account view (the account's own
  agreements), exactly as `tmp_validation/uc1_reach/` does.
- Transcripts come from Genesys until before August 2026 and from PCA from August on (user). The Genesys store starts
  about 2026-03-06; UC1 metadata ends 2026-07-16. Report what each source really holds; do not assume these dates.
- Result names are vocabulary, not ids: they may appear in the results.

Tie-outs (print first; report any mismatch at the top of the summary; never adjust to match)
- 07-31, account view, 61-180: RPC since March cards 49.3% / loans 54.7%; RPC in 90 days 36.1% / 42.7%; Genesys
  transcript in 90 days 10.5% / 13.3%.
- March-August per account: RPC 50.8% / 57.2%; Genesys transcript 32.7% / 32.4%; any UC1 evidence 22.3% / 19.6%.
- 07-31: 1,934 card accounts with a transcript in 90 days, 19.5% of them with no RPC in 90 days.

Rules
- Loading: `catalog.load` only. Reuse `tmp_validation/uc1_reach/` (the frame `uc1_reach_frame`, the RPC and store
  loaders) and `tmp_validation/uc1_refresh/` (Genesys store to CIF); do not rebuild what they already give. Load PCA the
  same way; if it has no catalog entry, add one explicit temporary entry for it (below) and say so in the README.
- Catalog: temporary entries only in `conf/base/catalog/catalog_tmp_uc1_full.yml`, explicit ones (no dataset factories).
  No pipeline, other catalog or registry change.
- model_id = `catalog.load("params:model_id")`, in every output file name.
- Aggregates only in results files and the summary: no account, CIF, agreement, conversation or agent ids or names; no
  transcript, remark or note text; team or channel labels only at group level; cells under 10 shown as "<10".
- A part that fails records its error, and the rest still runs.
- New tracked folder `tmp_validation/uc1_rpc_check/`; commit only that folder.

Deliverables
1. The snippet, pushed from UAT, in `tmp_validation/uc1_rpc_check/`: one config block at the top (months, match windows,
   parts to run `r1,r2,r3,r4`); one results file per model_id (`uc1_rpc_check_<model_id>.json` + `.md`) with the
   tie-outs and every table; a README with one command per model_id (cc_60_180 first) and the R1 class of every result
   name.
2. After the user commits the PROD results: `summary_uc1_rpc_check.md` (under 150 lines), in this order:
   - a. Tie-out mismatches, or "all match".
   - b. Verdict in two lines: is RPC a fair measure of "had a conversation"? Share of RPC days that are not a
     conversation, cards and loans.
   - c. Why so few RPC days have a transcript, causes ranked by evidence (not a call; a channel neither source records;
     the source switch from Genesys to PCA; CIF linking; date or time zone), each with its share.
   - d. The upper bound under (a)-(d), both windows, with the transcript and UC1 reading shares against each.
   - e. R3: each source's real date range and monthly volume, the hand-over between them, how much of PCA reaches UC1,
     and how the two add up to the 150,000+ the user knows.
   - f. Deck lines: 3-5 plain sentences with numbers for slide 5 (the coverage table).
   - g. What could not be computed, and why.
