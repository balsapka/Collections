# UC1 "promises said on calls are not logged in DCORE": summary of the raw-data check

Source: `results_cc_60_180.md`, `results_rl_60_180.md` (PROD rerun 2026-11-24 with the fixed snippet; H7, H4b and the printed H6 shares are in). Calls 2026-03-06 .. 2026-07-16 (UC1's metadata ends 07-16, so the "March-July" window is shorter than named); the model's CIFs only (60-180 DPD scope of `crx_<p>_obs_base`); aggregates, cells under 10 masked. UC1's extraction is a purposive sample, so the population is "promises UC1 extracted", not all promises.

**Not done:** the on-screen case review (steps 4-5), so H8 (extraction error) and the class counts are open. Nothing here comes from a run I made: UAT has no data access; the numbers are read from the two results files.

## 1. Tables found (step 1)

- **Call:** `crx_uc1_metadata` (1 row per conversation; `conversationstart` is a timestamp, calls 2026-03-06 .. 07-16; no team, queue, campaign or direction column). Promises from `crx_uc1_signal_level_conflicts` (no `source` column), confidence from `crx_uc1_extracted_signals`.
- **A3 as built:** `crx_<p>_a3_promise_events`, `prm_dcore_account_agreements` (account, agreement, cif), `dcore_prm_followup_outcomes` (`action_ts`, `result_ts`, `updated_at`), `dcore_int_ptp`, `dcore_int_settlement`.
- **DCORE raw, reached through `icustomerseqno`:** `col_his_followup` + `col_mst_result`, `col_trn_agreement`, `col_mst_customer`, `ptp_trn_promiseheader` / `ptp_trn_promisedetail`, `rps_cur_header` / `rps_cur_schedule`. All date columns are timestamps; the catalog documents no time zone; the Spark session is GMT.
- **Link to DCORE:** 100% of the promise CIFs reach DCORE through the model's agreements; the customer-number link added nothing. 74% (cc) and ~99% (rl) of them have at least one DCORE agreement outside the model map.

## 2. The promise set

| | cc_60_180 | rl_60_180 |
|---|---|---|
| Strict (paying intent AND amount or date named): customers / customer-days | 818 / 1,495 | 287 / 555 |
| Loose (paying intent only): customers / customer-days | 1,046 / 2,381 | 401 / 949 |

## 3. Waterfall (strict, customer-days; each fix on the original alone, then cumulative)

| | cc alone | cc cumulative | rl alone | rl cumulative |
|---|---|---|---|---|
| Original: A3 event alive within +-7 days, model scope | 33.0% | 33.0% | 69.4% | 69.4% |
| H1 call day +-1 | 31.8% | 31.8% | 67.7% | 67.7% |
| H2 other date columns of A3's own sources | 31.7% | 30.5% | 69.4% | 67.7% |
| H3 all agreements of the customer, A3 codes | 26.9% | 25.3% | 30.6% | 30.3% |
| H4 other promise-like result codes, all agreements | 12.6% | 9.6% | 34.6% | 12.1% |
| H5 raw PTP / settlement tables, all agreements | 23.5% | **9.0%** | 43.1% | **10.8%** |

- Gap explained alone (original unlogged = 494 cc / 385 rl days): H1 3.6% / <10; H2 4.0% / 0%; H3 18.6% / 55.8%; H4 61.9% / 50.1%; H5 28.9% / 37.9%. Incremental after the earlier steps: H1 3.6% / <10, H2 4.0% / 0%, H3 15.8% / 54.0%, H4 47.6% / 26.2%, H5 <10 / <10.
- Loose definition gives the same picture (cc 37.0% -> 11.1%; rl 72.2% -> 13.9%).
- Customer level: customers with ALL promise days unlogged fall from 31.2% to 8.2% (cc) and from 63.4% to 11.5% (rl).
- **Control (3c):** with a point rule (A3 event DATE within +-7 days, no event life up to its cutoff) the unlogged share is 59.6% (cc) and 80.9% (rl), matching the interim 60% / 81%. The interim run most likely used the event date; I have not re-read its code. The alive rule is what the pipeline and the bundle-31 flag use: 33.0% / 69.4% on promise days, 40.8% (228 of 559) / 67.0% (120 of 179) at the month end, matching the 41% / 70%.

## 4. Case classes (steps 4-5)

Not run. The still-unlogged days after every fix are 135 (cc) and 60 (rl); they are where extraction errors would show.

## 5. Verdict per hypothesis

| | Verdict |
|---|---|
| H1 time zone / day shift | Does not explain it: 3.6% of the gap (cc), <10 (rl). The call hours are 05-12 GMT, so no shift of a few hours moves a call across midnight. The hour comparison is uninformative: 85.7% (cc) / 90.2% (rl) of DCORE follow-ups are stamped 00:00 (date only), so a time-of-day offset cannot be measured. |
| H2 wrong DCORE date column | Does not explain it: 4.0% (cc), 0% (rl). Every date column of A3's own sources gives almost the same matches as the original. |
| H3 agreement scope | Explains a large part, mainly for loans: 18.6% (cc), 55.8% (rl) alone. The promise is logged on another agreement of the same customer. Among original-unlogged days with an A3-coded follow-up on an agreement outside the model map: rl 194 on CARD OPEN, 17 on CARD CLOSE; cc 52 on LOAN OPEN, 25 on CARD OPEN. A3 matches at account level inside one model; the decision is at CIF level. |
| H4 result codes | Largest gain (cc 47.6% incremental, rl 26.2%), but mostly not promise codes. H4b, original-unlogged days (494 cc / 385 rl): an A3-coded follow-up on another agreement 18.6% / 55.8%; matched ONLY by broad names (no A3 code) 51.6% (255) / 26.8% (103). Broad names behind it, days with the name (days where it is the only match): cc SETTLEMENT 103 (34), CALLBACK 61 (17), CALLBACK ACCOUNT MANAGER 58 (19), CLAIMS MADE PAYMENT 52 (17), CUSTOMER MADE PAYMENT 38, ACCOUNT PAID 37 (12), NEED BALCON 25 (14), NEED DEFERMENT 23 (11); rl CALLBACK 36, SETTLEMENT 35, CALLBACK ACCOUNT MANAGER 29, NEED DEFERMENT 27 (15), NEED BALCON 24, CLAIMS MADE PAYMENT 24, CUSTOMER MADE PAYMENT 22. These are arrangement talk (SETTLEMENT, BALCON), payment reports ("already paid"), callbacks and requests (deferment, balcon): none is a promise code. |
| H5 raw PTP / settlement tables, all agreements | 23.5% | **9.0%** | 43.1% | **10.8%** |

- Gap explained alone (original unlogged = 494 cc / 385 rl days): H1 3.6% / <10; H2 4.0% / 0%; H3 18.6% / 55.8%; H4 61.9% / 50.1%; H5 28.9% / 37.9%. Incremental after the earlier steps: H1 3.6% / <10, H2 4.0% / 0%, H3 15.8% / 54.0%, H4 47.6% / 26.2%, H5 <10 / <10.
- Loose definition gives the same picture (cc 37.0% -> 11.1%; rl 72.2% -> 13.9%).
- Customer level: customers with ALL promise days unlogged fall from 31.2% to 8.2% (cc) and from 63.4% to 11.5% (rl).
- **Control (3c):** with a point rule (A3 event DATE within +-7 days, no event life up to its cutoff) the unlogged share is 59.6% (cc) and 80.9% (rl), matching the interim 60% / 81%. The interim run most likely used the event date; I have not re-read its code. The alive rule is what the pipeline and the bundle-31 flag use: 33.0% / 69.4% on promise days, 40.8% (228 of 559) / 67.0% (120 of 179) at the month end, matching the 41% / 70%.

## 4. Case classes (steps 4-5)

Not run. The still-unlogged days after every fix are 135 (cc) and 60 (rl); they are where extraction errors would show.

## 5. Verdict per hypothesis

| | Verdict |
|---|---|
| H1 time zone / day shift | Does not explain it: 3.6% of the gap (cc), <10 (rl). The call hours are 05-12 GMT, so no shift of a few hours moves a call across midnight. The hour comparison is uninformative: 85.7% (cc) / 90.2% (rl) of DCORE follow-ups are stamped 00:00 (date only), so a time-of-day offset cannot be measured. |
| H2 wrong DCORE date column | Does not explain it: 4.0% (cc), 0% (rl). Every date column of A3's own sources gives almost the same matches as the original. |
| H3 agreement scope | Explains a large part, mainly for loans: 18.6% (cc), 55.8% (rl) alone. The promise is logged on another agreement of the same customer. Among original-unlogged days with an A3-coded follow-up on an agreement outside the model map: rl 194 on CARD OPEN, 17 on CARD CLOSE; cc 52 on LOAN OPEN, 25 on CARD OPEN. A3 matches at account level inside one model; the decision is at CIF level. |
| H4 result codes | Largest gain (cc 47.6% incremental, rl 26.2%), but the evidence is weak: the broad set includes names that are not promises. Among unlogged days the names over-represented against logged days are SETTLEMENT (cc 15.6% vs 8.1%), JOB LOST (10.7% vs 3.4%), CLAIMS MADE PAYMENT, NEED DEFERMENT, LEFT_MSG (cc 58.7% vs 41.5%). Whether any of these is a promise is not shown; H4b (pending) breaks the gain down by name. |
| H5 raw PTP / settlement tables | Matches many days alone (cc 28.9%, rl 37.9%) but adds almost nothing after H3 and H4 (<10 cc, 2.0% on loose rl). It was not dropped on the way into A3 beyond what H3/H4 already show. |
| H6 not a collections call | Does not explain it. A same-day DCORE follow-up of some code exists for >97% of the original-unlogged days (cc and rl), 100% of the days still unlogged after all fixes (135 cc, 60 rl), 99.0% (cc) / >94% (rl) of the logged days; a call-type follow-up (OC / CB / IC) the same day is as common. The metadata has no team, queue or direction column. |
| H7 load lag / coverage | Does not explain it, with two real gaps. DCORE follow-ups run at ~215k-332k a month (cc) and ~68k-99k (rl) with no month missing. Gap days: 2026-07-06 has 0 follow-ups in both models while the day has 77 (cc) / 23 (rl) calls and ~10 / <10 promise days; 2026-08-07 has 0 follow-ups and no calls. Weekdays at under 40% of the median follow-up volume: cc 7, rl 22 (rl mostly the first days of a month: 03-02..06, 04-01..03, 06-01/02, 07-01..03; 03-04, 03-20, 05-27/28, 06-15 in both). Separate finding: A3-coded follow-ups per month fall while total follow-ups stay flat: cc 5,612 (Mar), 6,062, 4,415, 3,187, 1,887 (Jul), 1,691 (Aug); rl 799, 1,033, 876, 458, 579, 489. The unlogged share by call month is not in the files. |
| H8 extraction error | Not tested: needs the transcripts. Indirect: unlogged share by UC1 confidence does not differ (cc high 33.2%, low 29.8%); it rises with call length (cc >420 s 41.8% vs 28.6% for 181-420 s; >50 utterances 38.7% vs 25.7% for 11-25), still 12-13% (cc) after all fixes on the long calls. |
| H9 wrong anchor call (bundle 31) | Explains part of the month-end flag. Of the flagged customers (228 cc, 120 rl) the anchor call (the last call before the month end) is itself a promise day for only 42.1% (cc) and 50.8% (rl); 84.6% / 91.7% have some promise day in the rebuilt set; 20.6% / 18.3% have one logged under the original match; 65.8% / 75.0% have one logged under all fixes (including the H4 caveat). |

## 6. The reverse (step 5 population)

| | cc | rl |
|---|---|---|
| DCORE promise days (A3 codes, model agreements, calls window) | 19,705 | 3,215 |
| ... with a call of the customer that day | 6,994 (35.5%) | 352 (10.9%) |
| ... of those, call extracted by UC1 | 1,132 (16.2%) | 113 (32.1%) |
| ... of the extracted, UC1 found a paying intent | 824 (72.8%) | 83 (73.5%) |
| ... of the extracted, UC1 found NO paying intent | 308 (27.2%) | 30 (26.5%) |

Where DCORE has a promise on a call day and UC1 read the call, UC1 agrees in about three cases out of four. Class counts of the 20-case sample were not recorded.

## 7. Conclusion

- **Verified unlogged share of the promises UC1 extracted, with the fixes:**
  - **cc_60_180:** 33.0% under the pipeline's alive rule; 25.3% when A3's own promise codes are matched at CIF level on every agreement; 9.0% if broader result names count.
  - **rl_60_180:** 69.4%; 30.3%; 10.8%.
  - So "no promise code entered anywhere for the customer within +-7 days of the call" is about 25% (cc) and 30% (rl) at the strict end; the 9-11% floor counts a callback, payment or settlement note as logged.
- **What the remaining gap is:**
  - Mostly **data linking**: A3 sees one agreement set of one model, while the promise is often entered on another product of the same customer (strongest for loans, where cards carry the entry).
  - Next is **agent logging**: calls with a same-day DCORE entry under a non-promise code. H4b shows these are settlement / balcon talk, "already paid" reports, callbacks and deferment requests, not promises; whether UC1 coded such talk as a paying intent is open (class a).
  - **Not collections calls** is ruled out (every unlogged-after-fixes day has a same-day follow-up). **Time zone, date column and load gaps** are ruled out (two gap days only).
  - **Extraction error** is untested.
- **What this changes for the earlier numbers:** 60% / 81% came from a point-event rule, and 41% / 70% (bundle 31) mixes anchor-call errors with the account-level scope. Neither should go to GRR as "promises not logged in DCORE".

## 8. Open

1. Read the 135 (cc) and 60 (rl) still-unlogged days, and a sample of the broad-name-only days, against the transcripts (class a/b/c/d), and the reverse sample. Question for the sample: did the customer promise to pay, or say they already paid, ask for a settlement or deferment, or ask to be called back.
2. Unlogged share by call month (from `uc1u_days`), because A3-coded follow-ups fall from March to July.
3. Decide with GRR the grain of "logged": CIF-level any promise code, the same agreement, or an arrangement code (SETTLEMENT, BALCON) as a promise.
4. Calls after 2026-07-16 are not in UC1's metadata: the month-end flag rests on calls up to mid-July. Gap day 2026-07-06 sits inside that window.
