# UC1 promises with no DCORE promise: agreement verdict, rebuilt set, first 20 cases read

Sources: `results_case_review_cc_60_180.md` and `results_case_review_rl_60_180.md` (PROD run 2026-11-24, steps 1-2), and the first 20 of the 100 drawn `rl_60_180` cases as printed on screen (on screen only). Calls 2026-03-06 .. 07-16.

Definitions: strict promise = paying intent AND an amount or date named. "Logged" = a PTP / settlement / instalment row, or a follow-up with an A3 promise code, on ANY agreement of the customer within +-7 days of the call (+-1 day shift, every date column of those tables). A same-day follow-up under another code does not count. The broad-name rule (H4) is dropped.

**Limits.** The classes in sections 4-6 are MY reading of 20 rl cases, not yours. `record` has not been run; the cc cases and rl cases 21-100 are unread; with n = 20 every share carries about +-20 points. I ran nothing on data: the numbers come from the two results files and the pasted cases.

## 1. How the cases were read

- Transcripts: read from the staged table `stg_genesys_transcripts` (100 of 100 readable). The raw column looked encrypted, so the snippet no longer prints it.
- Each case: UC1's readings, the transcript around the flagged lines (and the closing lines), and the customer's DCORE log for the 14 days either side, all agreements, with system noise hidden.
- Flagged-line numbers are UC1's; they matched the transcript lines in every case read (the index base assumption held).

## 2. The agreement puzzle: verdict

| | cc_60_180 | rl_60_180 |
|---|---|---|
| Promise CIFs (loose set) | 1,046 | 401 |
| More than one DCORE agreement | 795 (76.0%) | 396 (>97%) |
| More than one OPEN DCORE agreement | 708 (67.7%) | 377 (94.0%) |
| More than one DCORE product type | 733 (70.1%) | 393 (>97%) |
| More than one DCORE customer number (link fans out) | <10 | <10 |
| Two agreement ids on one account number | <10 | <10 |
| Agreements outside the model map / CIFs with one | 1,743 / 776 (74.2%) | 1,318 / 395 (>97%) |
| Card AND loan held (UC1 metadata, known for all) | 248 (23.7%) | 271 (67.6%) |
| More than one account in this model's base | 76 (7.3%) | 18 (4.5%) |
| More than one loan account (`loan_account_cif_map`) | not available | 174 (43.4%) |

- Agreements per CIF, 1 / 2 / 3 / 4 / 5+: cc 251, 305, 237, 118, 135 (24, 29, 23, 11, 13%); rl <10, 25, 141, 92, 138.
- **The link is sound and it is not a map gap.** Fewer than 10 CIFs have two DCORE customer numbers, and the same account under another agreement id holds under 10 agreements and zero promise days.
- **The outside agreements are other accounts of the same customer.** cc: overdraft 785, other loans 682, other cards 246. rl: cards 531, overdraft 443, closed loans 299, open loans 28. (The close-date column of the table is not a status: `dtinactive` is empty, so it rests on `dtmigclose` / `dtwriteoff`.)
- **The "about 15% hold more than one product" figure does not describe these customers.** They are delinquent: 24% (cc) and 68% (rl) hold a card and a loan, and DCORE also lists overdrafts and closed accounts.
- Days with no match through the model's own agreements (474 cc, 385 rl) that an A3 promise code on another agreement matches: cc 85 (17.9%: same product, other account 33; other product 52), rl 215 (55.8%: other product 208, same product <10).
- `prm_contract` loaded but its account and customer columns were not recognised (`client_id`, `contract_id`), so the cc product count rests on the base and the UC1 flags.

**Verdict:** real entries on other accounts of the same customer (for loans mostly the card), not a gap in our agreement map and not a wrong customer link. Whether such an entry is the same promise as the one on the call is a case question (sections 4-5).

## 3. The "no DCORE promise" set under the new definition

| Strict promise days | cc | rl |
|---|---|---|
| Customer-days (customers) | 1,495 (818) | 555 (287) |
| Unlogged, original A3 rule (alive +-7 days, model scope) | 494 (33.0%) | 385 (69.4%) |
| + H1 call day +-1 | 31.8% | 67.7% |
| + H2 other date columns of A3's own sources | 30.5% | 67.7% |
| + H3 all agreements, A3 codes | 25.3% | 30.3% |
| + H5 raw PTP / settlement / instalment tables: **the case set** | **318 (21.3%)** | **149 (26.8%)** |
| Same, entry dates only | 379 (25.4%) | 166 (29.9%) |
| Customers with at least one / all days unlogged | 226 (27.6%) / 166 | 117 (40.8%) / 74 |

- Your "about 25% / 30%" is the entry-dates-only line. The all-columns set is 4 (cc) and 3 (rl) points lower because update timestamps (`dtupdtimestamp`, `dtstatus`, `dtlasttracked`) of older PTP rows fall near a call; the 61 (cc) and 17 (rl) days that only they log are not in the case sample.
- By call month, new definition (Mar to Jul): cc 20.1, 21.1, 22.6, 22.7, 19.0%; rl 17.6, 25.4, 36.2, 29.5, 23.7%. July holds calls to 07-16 only.
- `szconversationid` cannot link calls to DCORE: filled on about 6% of follow-up rows (6,277 cc, 3,457 rl) and on fewer than 10 promise conversations.
- Reverse population: DCORE promise days (A3 codes) 18,112 (cc) and 2,948 (rl); with a call that day 38.6% / 11.9%; of those extracted by UC1 16.2% / 32.1%; UC1 found a paying intent on 72.8% / 73.5% of the extracted, none on 308 / 30 days (step 4, not read).

## 4. The 20 cases

Case-by-case notes (transcript lines, amounts, remark text) were shown on screen only and are not filed here.

## 5. Result (my reading)

| Class | Cases | n | Share (95% interval) | Of rl's 26.8% (indicative) |
|---|---|---|---|---|
| a UC1 misread | 1, 5, 6, 11, 16, 18; borderline 12, 19 | 8 | 40% (22-61%) | about 11 points |
| b our matching missed it | 14 | 1 | 5% (1-24%) | about 1 point |
| c not recorded as promise | 3, 4, 15, 17, 20; soft 2, 7-10, 13 | 11 | 55% (34-74%) | about 15 points |
| d nothing in DCORE around the call | none | 0 | 0% (0-16%) | 0 |

- **Sensitivity.** If only explicit commitments count as promises, the soft ones become class a: a = 14 (70%), c = 5 (25%), b = 1. If hedged promises count, a = 6 (30%), c = 13 (65%), b = 1. The truth of "was there a promise" is the judgment call, not the matching.
- Marks for `record`: a remark names the promise in 8 cases (2, 3, 8, 9, 10, 15, 17, 20); the transcript's amount or date appears in a remark in 4 (4, 7, 9, 17).

## 6. What the cases show

- **UC1 reads too much as a promise (a).** Past payments are read as promises (1, 6, 11); deferment, settlement or time requests with "I will try" are (5, 12, 16, 18, 19). The amount or date comes from an AGENT turn in cases 4, 8, 10, 17, 18, 20, and the customer confirms it only in 4 and 17. Two dates are impossible for the call (5: 2026-09-22 after "Monday"; 20: 2026-10-05 for "the 5th" on an April call).
- **Agents write the commitment in the remark but pick another code (c).** The codes are FOLLOW UP, LEFT_MSG, SETTLEMENT or JOB LOST. The promise is in free text, and often copied to every agreement of the customer. Four calls are settlement talk (3, 4, 17, 20); A3's promise codes do not include SETTLEMENT.
- **One promise sits in a table nobody reads (b).** `col_trn_atdfeedback` (the dialer feedback) holds result 153 on the call day in case 14. In cases 1 and 18 the same code appears in the dialer and the follow-up, 10 to 11 days later.
- **Nothing is missing from DCORE altogether (d).** Every call has same-day DCORE rows, except case 6, which falls on the 2026-07-06 day when DCORE has no follow-up at all.
- **Widening the window does not help.** Seven of 20 have promise evidence 8 to 14 days away (1, 3, 6, 8, 14, 15, 18), but each is a later call or an older, broken promise (15: both PTPs broken), not the same promise.
- **A structured PTP field exists in the activity remark** (`PTP Date :; PTP Amount :` in `szsystemremark`). It is filled where a PTP row exists (6 at D+14, 15 at D-14 and D-8) and empty on the calls here.

## 7. What it means for the headline

In this sample, about four of ten "unlogged" promises are not promises on the call, five to six of ten are promises that agents noted in free text under another code, and about one in twenty is recorded in a table the matching does not read. None is wholly absent from DCORE. The statement "UC1 promises are missing from DCORE" is therefore not supported; "UC1 over-detects promises, and DCORE records most of the real ones outside the promise codes" is closer. n = 20, one product; the cc cases may differ.

## 8. Open

1. Your classes on these cases, and the cc cases (`record`); the rest of rl (21-100).
2. Test the dialer table (`col_trn_atdfeedback` result names) as promise evidence on all promise days.
3. Decide how the SETTLEMENT code and remark-only promises are treated (a text rule on the remark).
4. Raise UC1's extraction: agent turns, past payments, hedged language, impossible dates.
