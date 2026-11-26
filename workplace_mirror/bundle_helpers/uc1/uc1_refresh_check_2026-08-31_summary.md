# UC1 refresh, export snapshot 2026-08-31: coverage and what the readings say (cc_60_180, rl_60_180)

Source: `results_cc_60_180_2026-08-31.md`, `results_rl_60_180_2026-08-31.md` (PROD 2026-11-26, snippet
2026-11-26a, evidence partition `2026-08-31`, no failed section). 180+ models not run: every number is
60-180. Axes: A1 deterioration, A2 locatability, A3 credibility, A4 ability. Counts under 10 are `<10`.
Reading (M2) = a transcript or remark day of the CIF in the 90 days strictly before the month end. No
coverage target, no minimum n.

**Verdict.** UC1 has not read everything it could; the gap sits between the Genesys store and UC1's
metadata (and, inside metadata, in what was extracted after March), and metadata stops at 2026-07-16.
Coverage is far above the earlier delivery through the export and the posteriors, but the posteriors
carry mostly old evidence, so they are a state with an age, not a reading of the month.

## What arrived, and what changed since the previous results files

Same delivery as the previous results files (`results_cc_60_180.md`, `results_rl_60_180.md`): no new CIFs,
no new calls, identical M2 counts (cards 1,587 / 1,299 / 1,362 at 06 / 07 / 08). New in the check only:
right-party step 1, M1 / M3, April-May, readings content, evidence age, grid origin.

| table | snapshot | rows | CIFs | note |
|---|---|---|---|---|
| customer_signal_export | 08-31 | 196,170 | 19,617 | was 5,040 CIFs (snapshot 10-31) |
| proposer_level_observations | 08-31 | 126,880 | 19,598 | new cut, observed to 08-31 |
| proposer_level_observations | 09-30, 10-31 | 28,158; 35,151 | 4,678; 5,038 | identical to earlier |
| signal_level_posteriors | 08-31 | 1,040,551 | 19,598 | monthly grid from 2022-02 |
| time_weighted_signal_agg. | 08-31 | 338,628 | 19,598 | new |
| signal_level_conflicts | none | 860,090 | 20,293 | 39,095 conversations |
| latest_flags; simple_signal_agg. | none | 11,920; 5,751 | -; 5,751 | new; unchanged |
| extracted_signals; metadata | none | 11,920; 147,004 | -; 54,176 | NOT refreshed (11-16) |

All timelines tables written 2026-11-26 06:51; metadata calls 2026-03-06 .. 07-16, none after. Evidence:
transcripts 95,795 rows, 16,780 CIFs (to 07-16); remarks 31,085 rows, 5,575 CIFs (to 08-31).

## Q2 Has UC1 read everything it could? Persona CIFs, customer-days from 2026-01

Step 1 = days with a right-party DCORE contact (OC / CB / IC, result in `RIGHT_PARTY_CONTACT`); they are
8-14% of the days with any call attempt. "Read" = an observation in the proposer evidence (the refreshed
output the export and posteriors come from); the extraction ledger is beside it (stale, 11-16).

| step | cards | loans |
|---|---|---|
| right-party call days | 111,752 | 19,388 |
| + transcript in the Genesys store | 14,902 (13.3%) | 938 (4.8%) |
| + in UC1 metadata | 12,730 (11.4%) | 811 (4.2%) |
| + read: evidence observation | 4,055 (3.6%) | 297 (1.5%) |
| + read: extraction ledger | 1,778 (1.6%) | 231 (1.2%) |
| in the store, not in metadata | 2,172 | 127 |
| not in the store (not UC1's gap) | 96,850 (86.7%) | 18,450 (95.2%) |

- Read share of the store-and-metadata days by call month, cards (loans): March 2,715 of 3,326 (144 of 189),
  April 501 of 4,017 (82 of 329), May 285 of 2,343 (34 of 155), June 338 of 2,398 (34 of 124), July 216 of
  646 (<10 of 14). UC1 read March almost fully; April-June 12-14% (cards), 22-27% (loans); July 33% (cards).
- The store holds nothing before March (Jan-Feb right-party days: 31,757 cards, 4,388 loans).

| conversations Mar-Sep | cards | loans |
|---|---|---|
| in the Genesys store | 34,062 | 6,615 |
| in UC1 metadata | 27,255 (80.0%) | 4,961 (75.0%) |
| in the extraction ledger | 4,242 (15.6%) | 1,662 (33.5%) |
| in the conflicts table | 10,548 (38.7%) | 2,667 (53.8%) |
| store only, dated after 07-16 | 3,158 | 1,028 |
| store, not in metadata (all) | 6,807 | 1,654 |

- Conflicts table, share of metadata conversations, March / Apr-Jun / July: cards 93% / 19-21% / 35%; loans
  95% / 35-44% / 65%. It reads more than the ledger, a better proxy for what UC1 read (not proof).
- Ledger share by DPD band at the call, cards: 61-90 28.5%, 91-120 48.1%, 121-150 54.1%, 151-180 37.0%.
- Agent remarks: of 2,083,436 DCORE remark days (cards) UC1 has a remark observation on 11,469 (0.6%; call
  follow-up days 1.1%, best month April 2.7%); loans 1,170 of 374,727 (0.3%). UC1 remark days: March-July
  only; after 07-16 cards 100 days, loans 12; after 08-31 none.

## Q3 Coverage at every persona month end, M1 / M2 / M3, whole population: % of accounts (n)

M1 export row on the CIF (looks ahead: it is one snapshot). M2 evidence 90 days before. M3 posterior row
dated on the month end. Accounts, cards / loans: 04-30 14,671 / 2,661; 05-31 15,890 / 3,096; 06-30 16,982 /
3,514; 07-31 18,397 / 3,728; 08-31 19,292 / 3,985.

| month end | cards M1 | cards M2 | cards M3 | loans M1 | loans M2 | loans M3 |
|---|---|---|---|---|---|---|
| 04-30 | 4.8% (699) | 3.0% (433) | 3.0% (435) | 10.3% (274) | 8.6% (228) | 8.6% (228) |
| 05-31 | 11.2% (1,786) | 10.2% (1,627) | 10.2% (1,627) | 14.2% (440) | 13.5% (419) | 13.5% (419) |
| 06-30 | 15.7% (2,668) | 9.3% (1,587) | 15.4% (2,615) | 17.2% (606) | 12.2% (428) | 17.1% (602) |
| 07-31 | 19.2% (3,528) | 7.1% (1,299) | 19.2% (3,525) | 18.2% (680) | 8.2% (307) | 18.2% (679) |
| 08-31 | 22.4% (4,315) | 7.1% (1,362) | 22.3% (4,311) | 19.7% (784) | 6.1% (245) | 19.6% (783) |

A2 reachable pool (accounts cards / loans: 3,873 / 793, 4,207 / 945, 4,260 / 1,000, 4,046 / 1,064,
4,043 / 1,043), M1 / M2 / M3 %:

| month end | cards M1 / M2 / M3 | loans M1 / M2 / M3 |
|---|---|---|
| 04-30 | 11.9 / 6.8 / 6.9 | 19.5 / 15.9 / 15.9 |
| 05-31 | 21.6 / 18.8 / 18.8 | 25.0 / 24.0 / 24.0 |
| 06-30 | 26.5 / 17.9 / 25.7 | 26.8 / 21.6 / 26.5 |
| 07-31 | 31.5 / 14.8 / 31.5 | 24.9 / 12.2 / 24.9 |
| 08-31 | 34.9 / 14.2 / 34.9 | 28.7 / 10.5 / 28.7 |

- M3 is close to M1 from June and to M2 in April-May: the posterior row is the evidence ever seen, so M2
  (recent) falls from 10.2% (05-31) to 7.1% while M3 keeps rising. M1 at 04-30 (699) exceeds M2 (433) by
  266 accounts whose export row exists only through later evidence: the look-ahead.
- Earlier delivery at 07-31: 891 / 334 accounts with a reading (M2 now 1,299 / 307); transcript readers
  420 / 164 are unchanged, the gain is remarks (remark-involved accounts 1,213 / 263).
- Cards at 07-31, M1 / M2 / M3 %: DPD 61-90 22.6 / 13.4 / 22.6, 91-120 21.7 / 6.7 / 21.6, 121-150 20.9 /
  2.4 / 20.9, 151-180 6.2 / 1.0 / 6.2; A3 partly_kept 35.6 / 13.4 / 35.6, promised 35.6 / 13.8 / 35.5,
  no_promise 6.9 / 2.4 / 6.9; A4 moderate 26.8 / 9.8, low 24.1 / 9.9, unknown 14.3 / 4.6. Loans follow the
  same order (all cuts: results files). Call in 90 days, no M2 reading, 07-31: cards 639, loans 153.

## What the readings say: share of CIFs where the signal is not detected (cards; loans similar)

Neither table has a "not stated" level: not detected = the signal has no row. M2 at 05-31 .. 08-31:

| signal | transcript: not detected | remark only: not detected |
|---|---|---|
| intent | 7-11% | 25-37% |
| delinquency reason | 21-26% | 37-49% |
| request | 17-27% | 38-43% |
| capacity | 19-29% | 88-91% |
| period | 30-36% | 63-75% |
| dispute | 69-74% | 91-93% |

Remark readings are not mostly empty: they name intent (63-75%), reason (51-63%) and request (57-62%).
They are nearly empty for capacity, dispute and period. The M3 groups give the same picture.

## Q4 Do the posteriors give a usable dated value?

- Dated: a monthly grid, 55 dates 2022-02-28 .. 2026-08-31, a row on every month end for every (CIF, signal)
  (persona CIFs with a row: cards 3,809 / 4,479 / 5,319 / 5,522 / 5,522 at 04..08, loans 810 .. 1,118).
  A score per level (sum 0.50-3.95), not a distribution: take the top level. No duplicates of the grain.
- Reproduces the export: top level equal on pairs with both sides, cards / loans: reason 95.7 / 94.5%,
  dispute 98.4 / 98.8%, capacity 98.9 / 99.1%, intent 94.0 / 92.8%, period 90.2 / 89.8%, request 100%.
- Rebuilt from the evidence with `parameters.json` (unchanged: half-life 30 d, bits 3 / 3 / 1; an
  approximation) at all five month ends: equal 94.6-100% (cards reason 95.7-96.8, capacity 95.7-96.1,
  intent 96.5-96.7, period 97.4-97.8, request 100); no pair one-sided. The posteriors are the evidence.
- Age of the evidence behind each (CIF, signal) row, cards (loans): at 04-30 0-30 d 49.5% (55.1%); 06-30
  23.9% (24.6%) and 91-180 d 35.4% (29.6%); 07-31 0-30 d 10.1% and 91-180 d 56.0%; at 08-31 0-30 d 0.2%
  (<10), 31-90 d 28.3% (28.0%), 91-180 d 71.5% (71.8%). Almost no row at 08-31 rests on a recent call.
- Why 2022: 451 remark rows dated 2022-2025 (60 / 35 / 188 / 168) start the grid at 2022-02; all other
  evidence is 2026 (remarks 30,634 rows, transcripts from 03-06). Sources: remark, transcript only; no UC2
  or bank-data source in the evidence (the `uc2` weight in `parameters.json` is unused).

## Q5 Outcome readiness (last payment date 2026-08-31)
1-month outcome exists for 04-30 .. 07-31, 3-month for 04-30 and 05-31 only; none for 08-31 (September
payments missing). M2 readings with an outcome, cards / loans: 04-30 433 / 228 (1- and 3-month), 05-31
1,627 / 419 (both), 06-30 1,587 / 428 and 07-31 1,299 / 307 (1-month only), 08-31 none.

## Not computed, open

- 180+ models not run. Observation ids are not conversation ids: observations match calls on CIF-day.
  Other-product agreements are not in the DCORE days. Export-only pairs in the export check are not read.
- Ask UC1: ingest the 3,158 / 1,028 store conversations after 07-16 and the 20-25% missing from metadata;
  refresh `metadata` and `extracted_signals`; explain the March re-read; say which table is the ledger.
