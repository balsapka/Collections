# UC1 refresh (August month end): coverage and the month end to take (cc_60_180, rl_60_180)

Source: `results_cc_60_180.md`, `results_rl_60_180.md` (PROD 2026-11-26, evidence partition `2026-08-31`,
no failed section; earlier runs on the old `2026-10-31` cut discarded). Axes: A1 deterioration, A2
locatability, A3 credibility, A4 ability. Counts under 10 are `<10`. 180+ models not run (outside UC1's
sample): all numbers are 60-180. Reading = a transcript or remark day of the CIF in the 90 days strictly
before the month end. No coverage target.

**Answers.** (1) No: UC1 has not read all it could. Metadata and the extraction ledger are still the 11-16
files (calls to 2026-07-16); the refresh added remarks and, it seems, a March re-read. (2) At 07-31 a
reading exists for 7.1% of card and 8.2% of loan accounts (14.8% / 12.2% of A2 reachable). (3) Posteriors
give a dated value at every month end (a monthly grid) but carry old evidence forward. (4) More CIFs are
covered, mainly through remarks; transcript readers are most numerous at 06-30 (577 / 247), but June cannot
be assumed fully covered, so freeze its cohort. Take 06-30 for transcripts, 07-31 as the check.

## Q1 What arrived (shared store, same for both model_ids; all written 2026-11-26 06:51 unless noted)

| table | snapshot | rows | CIFs | vs earlier delivery |
|---|---|---|---|---|
| customer_signal_export | 08-31 | 196,170 | 19,617 | new: was 5,040 CIFs (10-31) |
| proposer_level_observations | 08-31 | 126,880 | 19,598 | new cut, observed to 08-31 |
| proposer_level_observations | 09-30, 10-31 | 28,158; 35,151 | 4,678; 5,038 | identical to earlier |
| signal_level_posteriors | 08-31 | 1,040,551 | 19,598 | new: monthly grid |
| time_weighted_signal_aggregation | 08-31 | 338,628 | 19,598 | new |
| signal_level_conflicts | none | 860,090 | 20,293 | was 262,240 rows / 5,751 CIFs |
| latest_flags (new); simple_signal_agg. | none | 11,920; 5,751 | -; 5,751 | new; unchanged |
| extracted_signals; metadata | none | 11,920; 147,004 | -; 54,176 | NOT refreshed (11-16) |

- Conflicts table: 39,095 conversations, ledger 11,920. `parameters.json` unchanged (half-life 30 d, bits
  3 / 3 / 1). Calls in metadata 2026-03-06 .. 07-16, none after; remark days after 07-16: 140.

## Q2 Has UC1 read everything it could? Persona CIFs, calls from 2026-01-01

Waterfall, customer-days (CIF x day, same-day match). Store = `stg_genesys_transcripts`.

| step | cards | loans |
|---|---|---|
| DCORE call days (OC / CB / IC) | 1,635,452 | 328,426 |
| + transcript in the store that day | 31,280 (1.9%) | 2,760 (0.8%) |
| + in UC1 metadata | 25,577 (1.6%) | 2,056 (0.6%) |
| + extracted (ledger) | 3,815 (0.2%) | 684 (0.2%) |
| days with a transcript observation | 6,907 (0.4%) | 704 (0.2%) |
| in the store, not in metadata (UC1 gap) | 5,703 | 704 |
| not in the store (not UC1's gap) | 1,604,172 | 325,666 |

Conversations of the persona CIFs, Mar-Sep:

| step | cards | loans |
|---|---|---|
| in the store | 34,062 | 6,615 |
| in UC1 metadata | 27,255 (80.0%) | 4,961 (75.0%) |
| extracted (ledger), of metadata | 4,242 (15.6%) | 1,662 (33.5%) |
| in the conflicts table, of metadata | 10,548 (38.7%) | 2,667 (53.8%) |
| store, not in metadata | 6,807 | 1,654 |
| of which after 07-16 (Aug-Sep) | 2,590 | 837 |

- **Verdict: UC1 has not read everything it could.** Three gaps. (a) 98% of DCORE call days have no
  transcript in the store at all (store empty in Jan-Feb, under 7% of call days from March): not UC1's gap.
  (b) Of conversations in the store, 20% (cards) / 25% (loans) are not in UC1 metadata, 2,590 / 837 because
  metadata stops at 07-16; metadata/store is 84-92% for Mar-Jun, 68% / 58% for July. (c) Of what is in
  metadata, 84% (cards) / 66% (loans) have no ledger extraction.
- The conflicts table reads more than the ledger, unevenly. In metadata, March calls: 93.0% (cards) / 94.9%
  (loans); Apr-Jun 19-21% / 35-44%; July 35% / 65%. Days with a transcript observation in March: 4,374
  (cards, 61% of store days) vs 924 in April. Presence in conflicts is not proof of an observation.
- Extracted share of metadata by DPD band: cards 61-90 28.5%, 91-120 48.1%, 121-150 54.1%, 151-180 37.0%;
  loans 64.8%, 62.8%, 69.0%, <10.
- DCORE `szconversationid` (July on, 11-27%) is not the Genesys id: 66 of 37,219 July follow-ups match.

Agent remarks (customer-days, DCORE remark text vs a UC1 remark observation the same CIF-day): cards
2,083,436 DCORE remark days, 11,469 read (0.6%; best month April 1.6%); loans 374,727, 1,170 (0.3%; April
1.1%). UC1 remarks cover March-July only, none after 08-31; 92-97% (cards) / 28-68% (loans) of UC1's remark
days have DCORE remark text that day.

## Q3 Coverage at the month ends (accounts with a reading, 90 days strictly before)

Whole model population (A2 reachable pool in brackets), n beside every share:

| month end | cards: accounts | any reading | loans: accounts | any reading |
|---|---|---|---|---|
| 2026-06-30 | 16,982 (4,260) | 1,587 9.3% (763 17.9%) | 3,514 (1,000) | 428 12.2% (216 21.6%) |
| 2026-07-31 | 18,397 (4,046) | 1,299 7.1% (600 14.8%) | 3,728 (1,064) | 307 8.2% (130 12.2%) |
| 2026-08-31 | 19,292 (4,043) | 1,362 7.1% (573 14.2%) | 3,985 (1,043) | 245 6.1% (109 10.5%) |

At 07-31 (cards; loans): transcript only 86 (44), remark only 879 (143), both 334 (120); transcript readers
420 / 164 are unchanged from the old run. Earlier delivery at 07-31: 891 / 334 accounts (loans now lower,
cause not checked). UC1 export row on the CIF: cards 19.2% (07-31), 22.4% (08-31); loans 18.2%, 19.7% (was
4.8% / 9.0%). A call in the last 90 days but no reading: cards 639 (3.5%), loans 153 (4.1%).

Cards at 07-31, reading share (whole / reachable): DPD 61-90 13.4 / 22.4%, 91-120 6.7 / 12.0%, 121-150
2.4 / 6.0%, 151-180 1.0 / 4.8%; A4 high 11.7 / 16.4%, low 9.9 / 17.0%, unknown 4.6 / 12.3%; A3 partly_kept
13.4 / 17.7%, promised 13.8 / 20.5%, no_promise 2.4 / 7.5%. Loans (whole): DPD 61-90 12.2%, 91-120 8.6%,
121-150 5.0%. Coverage falls with DPD; full tables (3 month ends, 4 dimensions) are in the results files.

## Calls read after 2026-08-31 that no persona month end can use

None read: 0 conversations, transcript days or remark days after 08-31. The store holds persona-CIF calls
UC1 has not ingested: cards 1,332 (Aug) + 1,258 (Sep), loans 531 + 306.

## Q4 Do the posteriors give a dated value per month end?

- Structure: grain (snapshot, as_of_month, CIF, signal, level); 55 monthly dates 2022-02-28 .. 2026-08-31;
  1,040,551 rows, 19,598 CIFs; 0 duplicates. A score per level, not a distribution (sum per CIF, signal,
  date 0.50-3.95): use the top level. Persona CIFs with a row: 5,522 cards / 1,118 loans.
- Yes, a value can be read at each month end: every (CIF, signal) pair has a row dated exactly on it. But
  rows are carried forward: a row does not show a call in the last 90 days.
- Export reproduction (top level equal, pairs with both sides, cards / loans): reason 95.7 / 94.5%, dispute
  98.4 / 98.8%, capacity 98.9 / 99.1%, intent 94.0 / 92.8%, period 90.2 / 89.8%, request 100 / 100%.
  Difference counts equal the tied-top counts (within 2): mismatches coincide with ties.
- Rebuild from the evidence with `parameters.json` (approximation: no UC2, no copy-share rule), top level
  equal at 06-30 / 07-31 / 08-31 (cards): reason 96.7 / 96.8 / 96.8%, capacity 96-96.1%, intent 96.5-96.7%,
  period 97.4-97.5%, dispute 99.2-99.4%, request 100%; loans 94.8-100%. No pair is one-sided: usable.
- Accounts whose CIF has a posterior row (06 / 07 / 08): cards 2,615 / 3,525 / 4,311, loans 602 / 679 / 783
  (evidence of any age, 1.4-3.2 times the 90-day readings).

## Q5 Which month end? Readings with a payment outcome

Last payment date 2026-08-31: 1-month outcome for 06-30 and 07-31 only; no 3-month outcome for any.

| month end | cards readings | paid any / due | loans readings | paid any / due |
|---|---|---|---|---|
| 2026-06-30 | 1,587 | 19.2% / 16.2% | 428 | 40.2% / 27.8% |
| 2026-07-31 | 1,299 | 16.8% / 14.9% | 307 | 41.0% / 29.0% |
| 2026-08-31 | 1,362 | no outcome yet | 245 | no outcome yet |

**Recommendation.** Of 07 and 08, 07-31 has the most readings with an outcome (1,299 / 307 against 0). 06-30
has more readings (1,587 / 428), more transcript readers (below) and a complete 1-month outcome too: take
06-30 as the base for a transcript-based assessment and 07-31 as the check. 08-31 waits for September.

## More CIFs covered, and can June be taken as covered with transcripts?

- More coverage: export 19,617 CIFs (was 5,040). Accounts with a reading at 06-30: cards 1,587 (9.3%),
  loans 428 (12.2%); the old run showed 552 / 248. Transcript readers at 06-30: 577 / 247 (old 488 / 230):
  the gain is remarks, not transcripts.
- June has the best transcript coverage: transcript readers 06-30 vs 07-31 are 577 vs 420 (cards), 247 vs
  164 (loans). The June window (Mar 2 - Jun 29) includes March, which UC1 appears to have re-read: 93% /
  95% of March metadata conversations are in the conflicts table, against 19-21% / 35-44% for Apr-Jun.
- Do not assume June's CIFs are fully covered. June conversations in metadata: cards 5,517, of which 949
  in the ledger (17.2%) and 1,131 in the conflicts table (20.5%); loans 990, 404 and 434 (43.8%). UC1 chose
  the calls; the earlier run found covered card customers pay about 7 points less, so selection is not
  random. When UC1 extracts the rest, June readings grow retroactively: a June cohort today is "as of now".
- So: freeze the June CIF list and rerun after UC1's extraction to see how the cohort changes.

## Not computed, open, and to ask UC1

- 180+ models not run; posterior `n_calls` unused (the row date does not show age).
- Export-only pairs in Q4 (cards capacity 2,979 of 5,526) are not read: the export has a value in every
  pair, so one placeholder is not in my list. Observation ids are not conversation ids (0 of 7,344).
- Ask UC1: extract the calls after 07-16 and the 20-25% of store calls missing from metadata (refresh
  `metadata`, `extracted_signals`); why March was re-read and April-June was not; which table is the ledger.
