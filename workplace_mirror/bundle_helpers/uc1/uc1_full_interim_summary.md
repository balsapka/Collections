# UC1 full export: exploration and validation against the persona, summary (cc_60_180, rl_60_180)

Source: `results_uc1_full_cc_60_180.md`, `results_uc1_full_rl_60_180` (PROD run of 2026-11-23, snippet 2026-11-23a plus the fixes of commits `8b6e5096` and earlier; no errors, no failed part).
Numbers only inside tables; counts under 10 are `<10`.

**Scope and reading rules.** `cc_180_plus` and `rl_180_plus` were not run (UC1's sample holds no 180+; D8 = not run). Best effort, no n gate (interim decision): every difference is paid_due, covered group only, with the account bootstrap interval (200 draws) and n; strength = strong (interval excludes 0 and >= 5 pp / +0.02 AUC), suggestive (direction or size but the interval includes 0), no signal. Month-end view: pool 2026-04..07, headline 2026-07-31, outcomes `paid_due` 1 and 3 months; last payment date 2026-08-31, so 3-month outcomes exist only for month ends up to 2026-05-31 (none at the headline). Reading = our own `latest` (latest transcript day in 90 days; remark level as its own source) unless a table says otherwise; dropped by decision: 2.1 (confidence is flat), 3.2 and 3.3 (reproducing the estimate); 2.3 (estimated vs latest vs average of the export) was replaced by our own readings and was not run. Two result labels are wrong in the code and are corrected here: in 5.1a the `+-3 d` and `+-7 d` columns are swapped (a wider window cannot give a larger unlogged share; 5.2 and the key facts agree), and the D1.1 row "affected accounts" shows the whole book.

## Part 0 - what was delivered

| item | model_id | table | rows | CIFs |
|---|---|---|---|---|
| 0.1 | both | customer_signal_export | 50,400 | 5,040 |
| 0.1 | both | proposer_level_observations (3 partitions, rows overlap) | 98,407 | 5,038 |
| 0.1 | both | signal_level_posteriors | 305,914 | 5,038 |
| 0.1 | both | time_weighted_signal_aggregation | 98,319 | 5,038 |
| 0.1 | both | simple_signal_aggregation (undated) | 5,751 | 5,751 |
| 0.1 | both | signal_level_conflicts (undated) | 262,240 | 5,751 |

| item | model_id | snapshot_date | written |
|---|---|---|---|
| 0.1 | both | 2026-10-31 | 2026-11-23 04:54 |
| 0.1 | both | 2026-08-31 / 09-30 / 10-31 | 2026-11-23 04:55 |
| 0.1 | both | 2026-10-31 | 2026-11-23 04:55 |
| 0.1 | both | 2026-10-31 | 2026-11-23 04:55 |
| 0.1 | both | none | 2026-11-23 04:55 |
| 0.1 | both | none | 2026-11-23 04:55 |

Tables are identical for both model_ids (shared store). The export, posteriors and time-weighted tables share snapshot 2026-10-31 and hold the same 5,038 CIFs as the evidence (the export has 2 more); `simple_signal_aggregation` / `conflicts` hold 5,751 CIFs (4,832 in the export). `parameters.json`: half_life_days 30.0 (description: 60), bits transcript 3.0 / remark 3.0 / uc2 1.0 (description: remark 1.0), copy_share_mode same_source_half_life_cross_source_zero, HIGH top 0.60 margin 0.15, MEDIUM top 0.50 margin 0.10. The evidence has a 17th column `detected` that the description does not list.

| item | partition | rows | CIFs | max observed_at | rows dated <= 2026-07-31 |
|---|---|---|---|---|---|
| 0.1 | 2026-08-31 | 35,098 | 5,038 | 2026-08-31 | 35,021 |
| 0.1 | 2026-09-30 | 28,158 | 4,678 | 2026-07-16 | 28,158 |
| 0.1 | 2026-10-31 (used) | 35,151 | 5,038 | 2026-10-14 | 35,021 |

08-31 and 10-31 are **identical for everything dated up to 07-31** (a full-key comparison on cif, observation, signal, source, level: 35,021 rows in both, 0 only in either; the "identical to first partition" flag in the file compared against 09-30, an arbitrary reference, and is not reliable). 09-30 is a different, smaller cut (28,158 rows, 4,678 CIFs, from 2026-03-07, no earlier remarks). Observations after July (130 rows) are remarks only. **Question to UC1: is the `parameters.json` (30-day half-life, remark weight 3.0) the intended setting? The description says 60 days and 1.0. And what is the 09-30 partition (a cut without the pre-March remarks)?**

| item | model_id | signal | levels new / gone vs bundle 26 |
|---|---|---|---|
| 0.2 | both | capacity, intent, reason, period, dispute | none / none |
| 0.2 | both | request | none / none |
| 0.2 | both | fraudulent_customer | none / none |

| item | model_id | signal | note |
|---|---|---|---|
| 0.2 | both | capacity, intent, reason, period, dispute | all levels inside the old value set |
| 0.2 | both | request | one level `detected`: no type column in export or evidence |
| 0.2 | both | fraudulent_customer | detections <10 CIFs (export and evidence, remark only) |

- **0.3 / both**
  - check: export grain
  - value: 50,400 rows = 50,400 (cif, signal), 0 duplicates, 10 rows per CIF
- **0.3 / both**
  - check: categorical `estimated_value` not-detected
  - value: 17,108 of 35,280 (48.5%); repayment slots all N/A
- **0.3 / both**
  - check: tied estimates
  - value: reason 2.1%, dispute 0.5%, intent 2.5%, period 4.1%, capacity <10, request 0
- **0.3 / both**
  - check: multi-level statements, transcript
  - value: reason 8.0%, dispute 2.1%, capacity 0.3%, intent 3.2%, period 12.6%
- **0.3 / both**
  - check: `is_pick` vs first named level
  - value: order not recoverable (statement stored sorted); the pick matters for the multi-level statements above

| item | model_id | month | conversations (model CIFs) | extracted |
|---|---|---|---|---|
| 0.4 | cc_60_180 | 2026-03 | 6,608 | 822 |
| 0.4 | cc_60_180 | 2026-04 | 8,048 | 1,057 |
| 0.4 | cc_60_180 | 2026-05 | 5,086 | 908 |
| 0.4 | cc_60_180 | 2026-06 | 5,358 | 933 |
| 0.4 | cc_60_180 | 2026-07 | 1,498 | 460 |
| 0.4 | rl_60_180 | 2026-03 | 1,215 | 321 |
| 0.4 | rl_60_180 | 2026-04 | 1,514 | 434 |
| 0.4 | rl_60_180 | 2026-05 | 896 | 318 |
| 0.4 | rl_60_180 | 2026-06 | 982 | 403 |
| 0.4 | rl_60_180 | 2026-07 | 289 | 182 |

| item | model_id | month | called CIFs with a transcript obs | share of calls extracted |
|---|---|---|---|---|
| 0.4 | cc_60_180 | 2026-03 | 280 of 3,198 (8.8%) | 12.8% |
| 0.4 | cc_60_180 | 2026-04 | 446 of 3,356 (13.3%) | 13.4% |
| 0.4 | cc_60_180 | 2026-05 | 387 of 2,442 (15.8%) | 18.3% |
| 0.4 | cc_60_180 | 2026-06 | 372 of 2,070 (18.0%) | 17.9% |
| 0.4 | cc_60_180 | 2026-07 | 247 of 796 (31.0%) | 32.2% |
| 0.4 | rl_60_180 | 2026-03 | 135 of 613 (22.0%) | 27.7% |
| 0.4 | rl_60_180 | 2026-04 | 197 of 750 (26.3%) | 29.6% |
| 0.4 | rl_60_180 | 2026-05 | 142 of 499 (28.5%) | 36.3% |
| 0.4 | rl_60_180 | 2026-06 | 144 of 391 (36.8%) | 42.3% |
| 0.4 | rl_60_180 | 2026-07 | 69 of 132 (52.3%) | 65.5% |

All CIFs: 1,094 / 1,359 / 1,220 / 3,014 / 3,796 conversations extracted of 28,381 / 39,197 / 28,534 / 36,528 / 14,364 in 2026-03..07. Latest conversation in the store and latest transcript observation: both 2026-07-16; no conversation after the latest observation; the export's last_call_date is the same. Remark-only customer-days (all CIFs): 2026-03 394 (34%), 04 560 (35%), 05 424 (32%), 06 620 (20%), 07 295 (8%); before March only remarks, <10 to 34 per month.

- **0.5 / both**
  - check: bundle 26 required columns (metadata, extracted_signals, conflicts, simple agg)
  - result: all present
- **0.5 / both**
  - check: levels read from conflicts / `signals_json` outside the old set
  - result: none (0 rows); key missing 0; unknown level 0
- **0.5 / both**
  - check: new signal
  - result: `fraudulent_customer` (conflicts 11,920 rows; `signals_json` all NA)
- **0.5 / cc_60_180**
  - check: A5 capacity, persisted vs export (CIF in both)
  - result: had a level 690; same 642; different 48; now not-detected 0; newly covered 33
- **0.5 / cc_60_180**
  - check: A6 intent
  - result: had a level 772; same 691; different 81; now not-detected 0; newly covered 153
- **0.5 / rl_60_180**
  - check: A5 capacity
  - result: had a level 239; same 228; different 11; now not-detected 0; newly covered <10
- **0.5 / rl_60_180**
  - check: A6 intent
  - result: had a level 290; same 260; different 30; now not-detected 0; newly covered 19
- **0.5 / both**
  - check: repayment slots in the conflicts table
  - result: amount_mentioned 3,657, date_specific 2,147, plan 561 conversations (amount or date named in 35-51% of conversations, rising to 51% in 06-07)

`latest` (2026-07-31) vs the export estimate, CIFs:

| item | model_id | signal | equal | different | export only | both none |
|---|---|---|---|---|---|---|
| 0.5 | cc_60_180 | payment_capacity | 608 | 27 | 324 | 501 |
| 0.5 | cc_60_180 | payment_intent | 745 | 66 | 414 | 181 |
| 0.5 | rl_60_180 | payment_capacity | 198 | 13 | 155 | 116 |
| 0.5 | rl_60_180 | payment_intent | 215 | 15 | 185 | 47 |

## Part 1 - coverage and selection (A2 reachable and whole book)

| item | model_id | month end | book n | reachable n | covered n (% book) |
|---|---|---|---|---|---|
| 1.1 | cc_60_180 | 2026-04-30 | 14,671 | 3,873 | 181 (1.2%) |
| 1.1 | cc_60_180 | 2026-05-31 | 15,890 | 4,207 | 438 (2.8%) |
| 1.1 | cc_60_180 | 2026-06-30 | 16,982 | 4,260 | 552 (3.3%) |
| 1.1 | cc_60_180 | 2026-07-31 | 18,397 | 4,046 | 526 (2.9%) |
| 1.1 | rl_60_180 | 2026-04-30 | 2,661 | 793 | 124 (4.7%) |
| 1.1 | rl_60_180 | 2026-05-31 | 3,096 | 945 | 223 (7.2%) |
| 1.1 | rl_60_180 | 2026-06-30 | 3,514 | 1,000 | 248 (7.1%) |
| 1.1 | rl_60_180 | 2026-07-31 | 3,728 | 1,064 | 177 (4.7%) |

| item | model_id | month end | covered reachable (% reachable) |
|---|---|---|---|
| 1.1 | cc_60_180 | 2026-04-30 | 119 (3.1%) |
| 1.1 | cc_60_180 | 2026-05-31 | 259 (6.2%) |
| 1.1 | cc_60_180 | 2026-06-30 | 313 (7.3%) |
| 1.1 | cc_60_180 | 2026-07-31 | 263 (6.5%) |
| 1.1 | rl_60_180 | 2026-04-30 | 71 (9.0%) |
| 1.1 | rl_60_180 | 2026-05-31 | 127 (13.4%) |
| 1.1 | rl_60_180 | 2026-06-30 | 140 (14.0%) |
| 1.1 | rl_60_180 | 2026-07-31 | 79 (7.4%) |

Covered = a transcript or remark day in the prior 90 days. Pooled Apr..Jul: cc 2.6% of the book, 5.8% of reachable (reachable = 24.8% of the book); rl 5.9% and 11.0% (reachable 29.2%). Covered share by A1 (book / reachable, cc): high 8.3 / 13.4, moderate 3.7 / 6.1, low 3.6 / 6.9, unknown 1.4 / 4.2; by A3 (cc): kept 2.5, partly_kept 5.3, promised 4.3, no_promise 0.7; by DPD band (cc): 61-90 4.5, 91-120 2.7, 121-150 1.0, 151-180 0.6; rl follows the same order (A3 no_promise 3.7%, 151-180 1.4%). Persona cells on reachable personas only: cc 217 cells, none with covered n >= 100 (954 covered of 16,386); rl 154 cells, none (417 of 3,802). Export (timeless, all LOW for capacity and intent, MEDIUM for reason / period / dispute / request, HIGH <10): any row for 4.8% of the cc book and 9.8% of reachable, rl 9.0% and 13.3%. HIGH confidence does not exist for capacity or intent.

| item | model_id | group (reachable, paid_due 1 month) |
|---|---|---|
| 1.2 | cc_60_180 | all reachable |
| 1.2 | cc_60_180 | A3 kept |
| 1.2 | cc_60_180 | A3 partly_kept |
| 1.2 | cc_60_180 | A3 promised |
| 1.2 | cc_60_180 | A3 no_promise |
| 1.2 | cc_60_180 | A1 moderate / low / unknown / high |
| 1.2 | cc_60_180 | whole book |
| 1.2 | cc_60_180 | DCORE promise events with vs without a transcript day within +-7 d |
| 1.2 | rl_60_180 | all reachable |
| 1.2 | rl_60_180 | A3 kept / partly_kept / promised / no_promise |
| 1.2 | rl_60_180 | A1 moderate / low / unknown |
| 1.2 | rl_60_180 | whole book |
| 1.2 | rl_60_180 | DCORE promise events with vs without a transcript day within +-7 d |

| item | model_id | n covered / not |
|---|---|---|
| 1.2 | cc_60_180 | 954 / 15,432 |
| 1.2 | cc_60_180 | 38 / 1,096 |
| 1.2 | cc_60_180 | 567 / 6,432 |
| 1.2 | cc_60_180 | 252 / 3,587 |
| 1.2 | cc_60_180 | 97 / 4,317 |
| 1.2 | cc_60_180 | 247 / 352 / 273 / 82 |
| 1.2 | cc_60_180 | 1,697 / 64,243 |
| 1.2 | cc_60_180 | 61 / 2,948 |
| 1.2 | rl_60_180 | 417 / 3,385 |
| 1.2 | rl_60_180 | 27 / 139 / 128 / 123 |
| 1.2 | rl_60_180 | 79 / 220 / 113 |
| 1.2 | rl_60_180 | 772 / 12,227 |
| 1.2 | rl_60_180 | 12 / 461 |

| item | model_id | paid covered / not |
|---|---|---|
| 1.2 | cc_60_180 | 21.2% / 28.3% |
| 1.2 | cc_60_180 | 15.8% / 45.7% |
| 1.2 | cc_60_180 | 25.2% / 35.3% |
| 1.2 | cc_60_180 | 17.9% / 25.6% |
| 1.2 | cc_60_180 | 8.2% / 15.5% |
| 1.2 | cc_60_180 | 19.8 / 18.2 / 22.3 / 34.1% vs 33.5 / 25.9 / 25.9 / 39.9% |
| 1.2 | cc_60_180 | 18.0% / 11.3% |
| 1.2 | cc_60_180 | 32.8% / 50.7% |
| 1.2 | rl_60_180 | 31.7% / 29.9% |
| 1.2 | rl_60_180 | 44.4 / 34.5 / 35.9 / 21.1% vs 51.2 / 36.3 / 29.6 / 23.4% |
| 1.2 | rl_60_180 | 49.4 / 24.5 / 34.5% vs 41.0 / 28.3 / 27.6% |
| 1.2 | rl_60_180 | 29.7% / 19.0% |
| 1.2 | rl_60_180 | 16.7% / 47.9% |

| item | model_id | difference [95%] | strength |
|---|---|---|---|
| 1.2 | cc_60_180 | -7.1 [-10.6, -4.1] pp | strong |
| 1.2 | cc_60_180 | -29.9 [-40.7, -16.5] | strong |
| 1.2 | cc_60_180 | -10.1 [-14.6, -5.6] | strong |
| 1.2 | cc_60_180 | -7.7 [-12.8, -1.8] | strong |
| 1.2 | cc_60_180 | -7.3 [-13.3, +1.7] | suggestive |
| 1.2 | cc_60_180 | -13.6 / -7.7 / -3.5 / -5.8 | strong / strong / no signal / suggestive |
| 1.2 | cc_60_180 | +6.7 [+4.5, +8.8] | strong |
| 1.2 | cc_60_180 | -18.0 [-31.3, -5.6] | strong |
| 1.2 | rl_60_180 | +1.8 [-3.2, +6.9] pp | no signal |
| 1.2 | rl_60_180 | -6.8 / -1.7 / +6.3 / -2.2 | suggestive / no signal / suggestive / no signal |
| 1.2 | rl_60_180 | +8.4 / -3.8 / +6.9 | suggestive / no signal / suggestive |
| 1.2 | rl_60_180 | +10.7 [+8.0, +14.3] | strong |
| 1.2 | rl_60_180 | -31.3 [-50.4, -6.3] | strong (n 12) |

Selection is real on cards (covered reachable customers pay 7 pp less, in every A3 level), absent on loans overall; the whole-book gap is the reachable-vs-not effect. Parts 4-5 are therefore read inside the covered group, within A3 level x DPD band where n allows.

| item | model_id | scope | n treated / control | raw diff [95%] pp |
|---|---|---|---|---|
| 1.6 | cc_60_180 | paid_due 1m, whole book | 1,443 / 64,243 | +6.3 [+4.1, +8.7] |
| 1.6 | cc_60_180 | paid_due 1m, reachable pooled | 822 / 15,432 | -7.1 [-10.4, -3.6] |
| 1.6 | cc_60_180 | paid_due 1m, reachable 2026-07-31 | 216 / 3,783 | -6.2 [-11.8, +0.3] |
| 1.6 | cc_60_180 | paid_due 3m, reachable pooled | 328 / 7,702 | -4.1 [-10.4, +1.6] |
| 1.6 | rl_60_180 | paid_due 1m, whole book | 721 / 12,227 | +11.0 [+8.1, +15.1] |
| 1.6 | rl_60_180 | paid_due 1m, reachable pooled | 386 / 3,385 | +2.5 [-2.7, +7.3] |
| 1.6 | rl_60_180 | paid_due 3m, reachable pooled | 183 / 1,540 | +9.4 [+1.3, +17.4] |

| item | model_id | scope | standardised diff [95%] pp | strength |
|---|---|---|---|---|
| 1.6 | cc_60_180 | paid_due 1m, whole book | -0.8 [-3.1, +1.8] | no signal |
| 1.6 | cc_60_180 | paid_due 1m, reachable pooled | -11.4 [-15.1, -7.7] | strong (reversed) |
| 1.6 | cc_60_180 | paid_due 1m, reachable 2026-07-31 | -11.6 [-16.4, -6.3] | strong (reversed) |
| 1.6 | cc_60_180 | paid_due 3m, reachable pooled | -8.5 [-15.7, +0.3] | suggestive |
| 1.6 | rl_60_180 | paid_due 1m, whole book | +6.8 [+3.2, +11.2] | strong |
| 1.6 | rl_60_180 | paid_due 1m, reachable pooled | +0.2 [-6.1, +4.0] | no signal |
| 1.6 | rl_60_180 | paid_due 3m, reachable pooled | +2.5 [-4.7, +11.9] | no signal |

Contact effect (a transcript day in 90 days vs none, within A1 x A3 x DPD cells weighted to the book): cards -11.4 pp inside reachable, loans 0; a call in itself does not raise payment. Hence cards' covered customers are the ones who needed a call.

| item | model_id | DPD band at the call | conversations |
|---|---|---|---|
| 1.3 | cc_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 935 / 183 / 133 / 70 |
| 1.3 | cc_60_180 | no account row in the model scope (incl. calls at 1-60 DPD) | 24,583 |
| 1.3 | rl_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 252 / 110 / 39 / <10 |
| 1.3 | rl_60_180 | no account row in the model scope | 4,331 |

| item | model_id | DPD band at the call | extracted |
|---|---|---|---|
| 1.3 | cc_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 310 / 108 / 90 / 40 |
| 1.3 | cc_60_180 | no account row in the model scope (incl. calls at 1-60 DPD) | 3,652 |
| 1.3 | rl_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 171 / 75 / 35 / <10 |
| 1.3 | rl_60_180 | no account row in the model scope | 1,378 |

| item | model_id | DPD band at the call | % |
|---|---|---|---|
| 1.3 | cc_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 33.2 / 59.0 / 67.7 / 57.1 |
| 1.3 | cc_60_180 | no account row in the model scope (incl. calls at 1-60 DPD) | 14.9 |
| 1.3 | rl_60_180 | 61-90 / 91-120 / 121-150 / 151-180 | 67.9 / 68.2 / 89.7 / <10 |
| 1.3 | rl_60_180 | no account row in the model scope | 31.8 |

Overall extracted share of model-CIF calls Mar..Jul: cc 16.2%, rl 35.0%. The 1-60 DPD gap of the sample cannot be isolated: those calls sit in the "no account row" line with other out-of-scope accounts. 1.5 (data note for A2): covered customers that A2 calls non_reachable per month end: cc 58 / 163 / 223 / 249 (04..07), rl 31 / 69 / 83 / 84; the last transcript day is 31-90 days before the month end for 92% (cc) and 79% (rl) of them. 1.4 (180+): not run.

## Part 2 - quality of the new fields

- **2.rule / cc_60_180**
  - signal: capacity, covered
  - rule: latest90 / modal90 / latest90 support>=2 / latest180 / modal180
  - n: 1,430 / 1,441 / 718 / 1,426 / 1,441
  - AUC [95%]: 0.570 / 0.577 / 0.564 / 0.574 / 0.580 [0.527-0.613]
  - hi-lo pp [95%]: +15.7 / +16.5 / +31.8 / +14.4 / +14.8
- **2.rule / cc_60_180**
  - signal: intent, covered
  - rule: latest90 / modal90 / support>=2 / latest180 / modal180
  - n: 1,365 / 1,402 / 580 / 1,359 / 1,402
  - AUC [95%]: 0.545 / 0.544 / 0.542 / 0.547 / 0.547 [0.479-0.602]
  - hi-lo pp [95%]: +14.4 / +16.4 / +18.0 / +12.5 / +16.9
- **2.rule / rl_60_180**
  - signal: capacity, covered
  - rule: same five rules
  - n: 718 / - / 334 / - / -
  - AUC [95%]: 0.570 / 0.573 / 0.577 / 0.570 / 0.572
  - hi-lo pp [95%]: -
- **2.rule / rl_60_180**
  - signal: intent, covered
  - rule: same five rules
  - n: 671 / - / 218 / - / -
  - AUC [95%]: 0.584 / 0.585 / 0.625 [0.550, 0.693] / 0.582 / 0.577
  - hi-lo pp [95%]: +22.3 / +27.9 / +41.9 / - / -
- **2.rule / cc_60_180**
  - signal: intent in A3 no_promise
  - rule: latest90 / modal90 / latest180 / modal180
  - n: 214 / 218 / 212 / 218
  - AUC [95%]: 0.585 / 0.622 / 0.605 / 0.679 [0.504, 0.823]
  - hi-lo pp [95%]: +11.8 / +13.7 / +11.1 / +17.2
- **2.rule / rl_60_180**
  - signal: intent in A3 no_promise
  - rule: latest90 / modal90 / latest180 / modal180
  - n: 244
  - AUC [95%]: 0.610 / 0.615 / 0.600 / 0.612 [0.539-0.689]
  - hi-lo pp [95%]: -

Reading rule: the five rules are indistinguishable on capacity in both products (all within 0.564-0.580, intervals overlap). On intent `latest` and `modal` are equal; `support >= 2` is best on loans (0.625, on 218 of 671 rows) and not better on cards. **Decision: `latest` within 90 days (simplest, same AUC); `support >= 2` is worth keeping as a strength flag, not a requirement.** No fade with age: capacity AUC by age 0-30 / 31-60 / 61-90 d: cc 0.558 / 0.591 / 0.586; rl 0.547 / 0.563 / 0.556; intent cc 0.522 / 0.563 / 0.544; rl 0.556 / 0.540 / 0.608 (rl intent in no_promise 0.518 / 0.530 / 0.715): older readings separate as well as fresh ones within 90 days. 3-month outcomes: cc capacity 0.545 [0.494, 0.592], intent 0.509; rl capacity 0.545, intent 0.601 [0.527, 0.673]. 180-day windows add rows without losing separation.

- **2.4 / cc_60_180**
  - signal: capacity / intent / reason / period
  - share Agree / Disagree / N/A of export rows: 63.3 / 2.5 / 34.2; 80.8 / 6.8 / 12.4; 62.4 / 5.9 / 31.6; 55.9 / 4.6 / 39.4
  - note: export is one snapshot; paid_due by level is descriptive (not point in time): capacity Agree full 20.5% (88), none 12.8% (156), partial 18.9% (322)
- **2.4 / rl_60_180**
  - signal: capacity / intent / reason / period
  - share Agree / Disagree / N/A of export rows: 72.0 / 3.9 / 24.1; 83.4 / 6.8 / 9.8; 71.6 / 5.8 / 22.6; 64.3 / 6.6 / 29.0
  - note: no paid_due ordering distinguishes Agree from Disagree (cells <10)
- **2.5 / cc_60_180**
  - signal: supporting_data (Agree / Disagree / N/A)
  - share Agree / Disagree / N/A of export rows: lost_employment 83 / 113 / 130; capacity full 0 / 48 / 173; capacity none 136 / <10 / 97
  - note: 50 (signal, level) pairs always N/A
- **2.5 / rl_60_180**
  - signal: supporting_data
  - share Agree / Disagree / N/A of export rows: lost_employment 52 / 53 / 43; capacity full 0 / 25 / 40; capacity none 75 / 0 / 18
  - note: 39 pairs always N/A

`supporting_data` exists only for lost_employment and capacity full / none, never agrees with "full" (0 Agree) and is built from UC2 income features: described, not used. The cross-tabs with a1_state / income level are all cells <10 except a few cc cells (circularity, not validity). 2.2 (remark vs transcript, remark origin):

- **2.2 / cc_60_180**
  - measure: remark days with a DCORE follow-up event the same day / same or day before (2,317 days)
  - value: 92.3% / 93.4%
- **2.2 / cc_60_180**
  - measure: remark days with an A3 promise event (DCORE promise) same day / +-1
  - value: 13.6% / 15.4%
- **2.2 / rl_60_180**
  - measure: remark days with a DCORE follow-up event the same day / same or day before (499 days)
  - value: 54.3% / 63.1%
- **2.2 / rl_60_180**
  - measure: remark days with an A3 promise event same day / +-1
  - value: 6.6% / 7.6%
- **2.2 / cc_60_180**
  - measure: remark and transcript both on a day: same statement / overlap, capacity 22 days; intent 360; reason 254; period 118
  - value: 63.6% / 63.6%; 35.6% / 43.3%; 68.5% / 80.3%; 60.2% / 86.4%
- **2.2 / rl_60_180**
  - measure: same: intent 127 days; reason 72; period 52
  - value: 38.6% / 49.6%; 72.2% / 80.6%; 53.8% / 88.5%
- **2.2 / cc_60_180**
  - measure: remark-only readings vs transcript readings (AUC, o1)
  - value: capacity 0.410 (n 41, reversed) vs 0.570; intent 0.535 [0.501, 0.570] vs 0.545
- **2.2 / rl_60_180**
  - measure: remark-only readings
  - value: capacity n 11 (AUC 0.500); intent 0.495 [0.374, 0.643] (n 42) vs 0.584

Remarks are DCORE notes (92% of cc remark days have a follow-up record that day) but are almost never structured promise events (14% / 7%); remark-named intent agrees with the transcript on only 36-39% of days; remark-only intent orders payers on cards (0.535) but not on loans. 2.6 (repayment text): in the export `latest_value` carries clean amounts (cc 673 of 1,464 rows, rl 232 of 482) and clean dates (cc 470, rl 180); percentages, ranges, words and redaction tokens: 0 to <10 in both; the amount-to-due ratio shows no ordering (cc 0.5-<1 19.0%, 1-<1.5 18.5%, 3+ 22.4%; rl cells mostly <10). The clean-date bins carry no information (measured from the export snapshot, all "before snapshot"; cc 268, 20.5% paid).

## Part 3 - point in time

- **3.1 / both**
  - check: snapshots
  - result: export one (2026-10-31); evidence three overlapping partitions 08-31 / 09-30 / 10-31; posteriors and time-weighted one
- **3.1 / both**
  - check: export vs a past month end
  - result: not point in time (the export is one snapshot; its evidence includes observations after every earlier month end)
- **3.3 / both**
  - check: rule used for Parts 2 and 4
  - result: our own `latest` / `modal90` from evidence dated strictly before the month end (not the export)
- **3.4 / cc_60_180**
  - check: capacity class changes month to month, covered at both (n 591-694)
  - result: 04->05 9.5%, 05->06 9.1%, 06->07 10.2%
- **3.4 / cc_60_180**
  - check: intent
  - result: 10.8%, 8.4%, 10.2%
- **3.4 / rl_60_180**
  - check: capacity (both months named)
  - result: 03->04 19.4%, 04->05 7.3%, 05->06 8.5%
- **3.4 / rl_60_180**
  - check: intent
  - result: 15.9%, 8.1%, 5.0%, 07->08 7.0%

Past month ends can be read point in time from the evidence (dated observations) but not from the export. The 08-31 and 10-31 partitions hold the same observations up to 07-31, so the choice between them does not change a past-month-end read (09-30 is a smaller cut and should not be used). 3.2 and 3.3 recomputation was not run.

## Part 4 - decisions (covered group; paid_due; strength as defined above; D8 not run)

- **D1 / cc_60_180**
  - measure: transcript days as A3 events: level / state changes per 1,000 book rows
  - n: 1,472 days, 157 extra account-days
  - estimate [95%]: 0.6 / 0.2
  - strength: no signal
- **D1 / cc_60_180**
  - measure: state AUC difference, 1m pooled book (AUC 0.764 both)
  - n: 65,940
  - estimate [95%]: -0.0000 [-0.0001, +0.0001]
  - strength: no signal
- **D1 / cc_60_180**
  - measure: state AUC difference, 3m book / affected 1m rows
  - n: 30,561 / 263
  - estimate [95%]: +0.0001 [-0.0000, +0.0003] / -0.0026 [-0.0197, +0.0162]
  - strength: no signal
- **D1 / cc_60_180**
  - measure: share of A3 promise events started by an extra day
  - n: 14,517 events
  - estimate [95%]: 0.8% (remark: 0.5%)
  - strength: -
- **D1 / rl_60_180**
  - measure: level / state changes per 1,000 book rows
  - n: 555 days, 95 extra
  - estimate [95%]: 4.6 / 2.5
  - strength: no signal
- **D1 / rl_60_180**
  - measure: state AUC difference 1m pooled / headline / 3m (AUC 0.673)
  - n: 12,999
  - estimate [95%]: +0.0005 [-0.0003, +0.0014] / +0.0008 [-0.0003, +0.0020] / +0.0011 [-0.0000, +0.0024]
  - strength: no signal
- **D1 / rl_60_180**
  - measure: share of A3 promise events started by an extra day
  - n: 2,446 events
  - estimate [95%]: 2.8% (remark 1.5%)
  - strength: -
- **D2 / cc_60_180**
  - measure: unlogged promise vs no promise: pay30_due / pay45_any, all A3 levels
  - n: 386
  - estimate [95%]: +0.5 [-7.5, +9.0] / +3.5 [-5.9, +11.2]
  - strength: no signal
- **D2 / cc_60_180**
  - measure: unlogged vs logged promise: pay30_due / pay45_any
  - n: 256
  - estimate [95%]: +8.9 [-0.1, +17.4] / +7.6 [-3.7, +17.7]
  - strength: suggestive
- **D2 / cc_60_180**
  - measure: direction in A3 level x DPD strata (unlogged - no promise, pay45_any)
  - n: 4 strata
  - estimate [95%]: same sign in 3 of 4
  - strength: -
- **D2 / rl_60_180**
  - measure: unlogged vs no promise: pay30_due / pay45_any
  - n: 229
  - estimate [95%]: +12.2 [-0.8, +24.8] / +13.0 [-0.2, +28.1]
  - strength: suggestive
- **D2 / rl_60_180**
  - measure: by A3 level: promised pay45_any / partly_kept / no_promise
  - n: 81 / - / -
  - estimate [95%]: +30.9 [+5.3, +49.2] / +17.6 [-14.2, +42.1] / -13.9 [-38.1, +11.5]
  - strength: strong (promised)
- **D2 / rl_60_180**
  - measure: direction in strata
  - n: 4 strata
  - estimate [95%]: same sign in 3 of 4
  - strength: -
- **D3 / cc_60_180**
  - measure: stated dispute with flag false vs covered without a stated dispute (o1 / o3)
  - n: 1,687 / 614
  - estimate [95%]: +3.3 [-0.2, +7.6] / -2.4 [-11.8, +8.1]
  - strength: no signal
- **D3 / rl_60_180**
  - measure: same, against the RL dispute codes (o1 / o3)
  - n: 772 / 347
  - estimate [95%]: +1.8 [-8.1, +12.5] / -8.8 [-23.9, +10.4]
  - strength: no signal
- **D4 / cc_60_180**
  - measure: A1 Unknown: paid by able / partly / not stated / unable (o1)
  - n: 51 / 181 / 113 / 81
  - estimate [95%]: 23.5 / 17.7 / 23.9 / 12.3%
  - strength: -
- **D4 / cc_60_180**
  - measure: AUC inside A1 Unknown (pool; 07-31 n 143)
  - n: 426
  - estimate [95%]: 0.528 [0.457, 0.588]; 0.567 [0.444, 0.683]
  - strength: suggestive
- **D4 / cc_60_180**
  - measure: top vs bottom; top vs second; named reading / no reading ratio
  - n: 426; 34,813
  - estimate [95%]: +11.2 [-4.6, +24.4]; +5.8 [-8.9, +18.0]; 2.150 [1.529, 2.702]
  - strength: suggestive; ratio strong
- **D4 / rl_60_180**
  - measure: paid by able / partly / not stated / unable
  - n: 34 / 78 / 32 / 28
  - estimate [95%]: 32.4 / 26.9 / <10 / <10%
  - strength: -
- **D4 / rl_60_180**
  - measure: AUC (pool; 07-31 n 45); top vs bottom; ratio
  - n: 172; 4,858
  - estimate [95%]: 0.533 [0.424, 0.647]; 0.506; +7.4 [-15.0, +34.6]; 1.767 [1.303, 2.286]
  - strength: suggestive; ratio strong
- **D4 / both**
  - measure: direction (able above unable) in A3 x DPD strata with n >= 10
  - n: -
  - estimate [95%]: cc 1 of 1 (able+partly vs unable 3 of 4); rl 0 of 0
  - strength: n too small to confirm
- **D5 / cc_60_180**
  - measure: A3 no_promise: AUC (pool; 07-31 n 56); top vs bottom; ratio
  - n: 214; 34,774
  - estimate [95%]: 0.585 [0.323, 0.802]; 0.433; +11.8 [-13.0, +37.8]; 1.443 [0.515, 2.735]
  - strength: no signal
- **D5 / cc_60_180**
  - measure: amount or date named vs not (pays in full / partly), o1 / o3
  - n: 132 / 48
  - estimate [95%]: +5.8 [-4.6, +19.4] / +7.0 [-17.3, +28.2]
  - strength: no signal
- **D5 / rl_60_180**
  - measure: paid by pays in full / partly / refuses (o1; o3)
  - n: 85 / 109 / 22
  - estimate [95%]: 34.1 / 18.3 / <10%; 73.1 / 45.0%
  - strength: -
- **D5 / rl_60_180**
  - measure: AUC o1 (n 244) / o3 (n 114); top vs second o1 / o3; ratio o1
  - n: -
  - estimate [95%]: 0.610 [0.539, 0.689] / 0.710 [0.586, 0.823]; +15.8 [+6.1, +26.7] / +28.1 [+6.4, +51.3]; 1.800 [1.424, 2.316]
  - strength: strong
- **D5 / rl_60_180**
  - measure: amount or date named vs not, o1 / o3
  - n: 194 / 92
  - estimate [95%]: +2.6 [-8.9, +16.3] / +18.5 [-1.9, +42.1]
  - strength: no signal
- **D6 / cc_60_180**
  - measure: says able while A1 Low vs concordant (o1; o3)
  - n: 61 / 31
  - estimate [95%]: -25.4 [-48.8, +0.7]; -44.3 [-67.5, -6.5]
  - strength: suggestive; strong (reversed)
- **D6 / cc_60_180**
  - measure: says pays in full while A1 Low (o1; o3)
  - n: 103 / 31
  - estimate [95%]: -26.7 [-47.0, -0.2]; -36.5 [-63.1, -2.4]
  - strength: strong (reversed)
- **D6 / cc_60_180**
  - measure: says unable while A1 High / Moderate (o1)
  - n: 36 / 122
  - estimate [95%]: +4.9 [-5.7, +15.7]
  - strength: no signal
- **D6 / cc_60_180**
  - measure: says unable while CASA balance >= due
  - n: flag <10
  - estimate [95%]: n too small
  - strength: n too small
- **D6 / cc_60_180**
  - measure: says has_employment while income stopped (o1)
  - n: 74 / 154
  - estimate [95%]: -9.8 [-20.3, +2.1]
  - strength: suggestive
- **D6 / cc_60_180**
  - measure: says lost_employment while income continues (o1; o3)
  - n: 84 / 185
  - estimate [95%]: +6.1 [-1.1, +14.8]; +21.0 [-1.7, +40.0]
  - strength: suggestive
- **D6 / rl_60_180**
  - measure: says able / pays in full while A1 Low
  - n: 53 / 106 flagged, concordant <10
  - estimate [95%]: -9.8 / +0.6, intervals +-40
  - strength: n too small
- **D6 / rl_60_180**
  - measure: says unable while A1 High / Moderate
  - n: 11 / 85
  - estimate [95%]: +30.2 [+3.1, +65.4]
  - strength: n too small (flag n 11)
- **D6 / rl_60_180**
  - measure: says has_employment while income stopped; lost_employment while income continues
  - n: 17 / 54; 29 / 97
  - estimate [95%]: -15.0 [-40.6, +11.7]; +3.2 [-10.1, +18.4]
  - strength: suggestive; no signal

Claim vs data: the stated reason matches our income reading about half of the time (cc has_employment with income continuing 154 of 339, lost_employment with income stopped or dropped 185 of 395; rl 54 of 134 and 97 of 195). D6 strata: direction of the flag effect is consistent in 2 of 3 strata for F3 / F4 (cc); all rl strata have cells < 10.

| item | model_id | reading (o1 paid_due, n) |
|---|---|---|
| D7 | cc_60_180 | reason, request, period (account-months) |
| D7 | rl_60_180 | same |

| item | model_id | has_employment / lost_employment / reduced / increased_obligations |
|---|---|---|
| D7 | cc_60_180 | 20.9% (339) / 10.4% (395) / 14.7% (170) / 23.5% (115) |
| D7 | rl_60_180 | 36.6% (134) / 18.5% (195) / 37.9% (87) / 43.4% (53) |

| item | model_id | request detected / not detected / no evidence |
|---|---|---|
| D7 | cc_60_180 | 18.3% (1,263) / 17.1% (434) / 11.3% (64,243) |
| D7 | rl_60_180 | 30.9% (596) / 25.6% (176) / - |

| item | model_id | weeks / salary cycle / months or longer |
|---|---|---|
| D7 | cc_60_180 | 19.2% (475) / 14.1% (283) / 21.1% (90) |
| D7 | rl_60_180 | 30.0% (233) / 35.3% (136) / <10 (33) |

Call-anchored pay45_any after a request (transcript days): cc detected 28.4% (268 pairs) vs none named 29.0% (217), median 21 vs 17 days to pay; rl detected 57.7% (137) vs none named 57.4% (108). Requests carry no type, so the settlement / restructure / waiver / deferral contrast cannot be read; the request itself does not change payment within covered customers. Reason is the treatment hint that separates payers: lost employment pays about half of has employment (cc 10.4 vs 20.9%, rl 18.5 vs 36.6%).

## Part 5 - logging gaps (call-anchored view)

Promise = paying intent plus an amount or a date named (transcripts); intent only (remarks).

- **5.1 / cc_60_180**
  - measure: promise customer-days (CIFs)
  - transcript: 1,472 (797): 47.0% of transcript days
  - remark: 1,444 (486)
- **5.1 / cc_60_180**
  - measure: no DCORE promise on the CIF within +-7 d / +-3 d
  - transcript: 59.9% / 70.2%
  - remark: 55.4% / 68.4%
- **5.1 / cc_60_180**
  - measure: no DCORE promise on the account within +-7 d / +-3 d (account-days 256 / 62)
  - transcript: 64.5% / 78.9%
  - remark: 62.9% / 82.3%
- **5.1 / cc_60_180**
  - measure: reverse: DCORE promise events within +-3 d of a transcript day with no paying intent stated
  - transcript: 158 of 542 (29.2%)
  - remark: -
- **5.1 / rl_60_180**
  - measure: promise customer-days (CIFs)
  - transcript: 555 (287): 44.2% of transcript days
  - remark: 308 (115)
- **5.1 / rl_60_180**
  - measure: no DCORE promise on the CIF within +-7 d / +-3 d
  - transcript: 80.7% / 86.1%
  - remark: 83.8% / 87.3%
- **5.1 / rl_60_180**
  - measure: no DCORE promise on the account within +-7 d / +-3 d (account-days 111 / 37)
  - transcript: 88.3% / 91.0%
  - remark: 94.6% / 94.6%
- **5.1 / rl_60_180**
  - measure: reverse
  - transcript: 43 of 116 (37.1%)
  - remark: -

Where the gap sits (share unlogged within +-7 d on the CIF; metadata has no agent, team, queue, campaign or direction column, only call length and the CIF's worst DPD bucket):

| item | model_id | dimension |
|---|---|---|
| 5.2 | cc_60_180 | month |
| 5.2 | cc_60_180 | DPD band of the account |
| 5.2 | cc_60_180 | call length |
| 5.2 | cc_60_180 | promise type |
| 5.2 | cc_60_180 | worst DPD bucket of the conversation month |
| 5.2 | rl_60_180 | month |
| 5.2 | rl_60_180 | DPD band / call length / promise type (spread) |

| item | model_id | values (share unlogged) | spread max - min |
|---|---|---|---|
| 5.2 | cc_60_180 | 03 46.5%, 04 61.0%, 05 69.0%, 06 67.0%, 07 50.2% | 22.5 pp |
| 5.2 | cc_60_180 | 61-90 53.2%, 91-120 65.0%, 121-150 70.7%, 151-180 94.4% (n 18) | 17.5 pp |
| 5.2 | cc_60_180 | 60-179 s 57.5%, 180-299 s 52.0%, 300-599 s 61.8%, 600+ s 70.0% | 18.1 pp |
| 5.2 | cc_60_180 | payback_full 49.9%, partial 67.7%, with_delay 62.0%, mixed 67.8% | 17.9 pp |
| 5.2 | cc_60_180 | 0-30 DPD 46.2-46.8%, 31-60 66.1%, 61-90 66.9%, 180+ 86.0% | 39.9 pp |
| 5.2 | rl_60_180 | 03 68.2%, 04 81.3%, 05 77.1%, 06 88.0%, 07 89.8% | 21.6 pp |
| 5.2 | rl_60_180 | - | 14.2 / 17.4 / 5.9 pp |

The gap is not even (22-40 pp spread by month, DPD and call length) and it grows with delinquency and call length; it is largest for partial and with-delay promises. Together with 5.3 and R this points to logging practice (what an agent chooses to code as a promise event), not to a feed that drops records at random; the available metadata cannot name a team or queue. Logged promises that exist: cc 291 of 591 are entered the same day, 216 before the call and 84 after; the logged amount matches the stated amount within +-10% in 29.2% (438 days), the logged date within +-3 days in 12.1% (305); rl amount 17.2% (64 days), date <10.

- **5.4 / cc_60_180**
  - stated dispute (customer-days): system_problem 582 / other 51 / customer_scammed 32
  - with no A3 dispute flag on the CIF at the next month end: 99.8% / 100.0% / 100.0% (all types 99.9%)
  - with no DCORE dispute code: 98.8% / 88.2% / <10
  - note: DCORE has DISPUTE 855 events / 376 CIFs and FRAUD CASE 370 / 195
- **5.4 / rl_60_180**
  - stated dispute (customer-days): system_problem 186 / other 13
  - with no A3 dispute flag on the CIF at the next month end: 100.0% / 100.0%
  - with no DCORE dispute code: 100.0% / 100.0%
  - note: RL codes: DISPUTE 27 events / 23 CIFs, FRAUD CASE <10 (result_name of `dcore_prm_followup_outcomes`): too few to call a gap

| item | model_id | requests with a full 90-day window | any matching DCORE keyword |
|---|---|---|---|
| 5.5 | cc_60_180 | transcript 1,775 (remark 1,048) | 36.3% (41.5%) |
| 5.5 | rl_60_180 | transcript 328 (remark 158) | 26.8% (43.0%) |

| item | model_id | settlement / restructure / waiver / deferral |
|---|---|---|
| 5.5 | cc_60_180 | 33.0 / 2.2 / 0.0 / 1.7% (39.8 / 1.5 / 0.0 / <10%) |
| 5.5 | rl_60_180 | 6.1 / 4.6 / 0.0 / 19.5% (17.1 / 10.1 / 0.0 / 19.0%) |

| item | model_id | restructure flagged |
|---|---|---|
| 5.5 | cc_60_180 | no dated card restructure source |
| 5.5 | rl_60_180 | <10 (restructure link reaches 2026-07-31, chains 2025-12-31) |

Any DCORE event at all follows 98-100% of requests, so only the keyword match is informative; it is a text match on the result name, not a verified request record. Rl request window is complete only for requests up to 2026-05-02.

| item | model_id | pay30_due / pay30_any / pay45_due / pay45_any (account-days) |
|---|---|---|
| 5.6 | cc_60_180 | all A3 levels |
| 5.6 | rl_60_180 | all A3 levels |

| item | model_id | unlogged promise | logged promise |
|---|---|---|---|
| 5.6 | cc_60_180 | 21.0 / 27.4 / 24.8 / 31.8% (157) | 12.1 / 15.2 / 17.2 / 24.2% (99) |
| 5.6 | rl_60_180 | 49.5 / 63.2 / 52.6 / 65.3% (95) | <10 (16) |

| item | model_id | no promise |
|---|---|---|
| 5.6 | cc_60_180 | 20.5 / 23.1 / 24.0 / 28.4% (229) |
| 5.6 | rl_60_180 | 37.3 / 52.2 / 38.8 / 52.2% (134) |

Within A3 level (cc): partly_kept unlogged pay45_any 35.4% (96) vs logged 19.7% (66) vs none 32.3% (127). The gap matters for loans (unlogged promises pay +13 pp over no promise, suggestive) and not measurably for cards; in neither product do unlogged promises pay less than logged ones.

## Part 6 - sample statements re-checked

- **S1 UC1 levels match our recomputation / both**
  - verdict: holds (3.2 not run)
  - new numbers: bundle 26 levels all inside the old set; A5 agreement cc 642 of 690, rl 228 of 239; A6 cc 691 of 772, rl 260 of 290; `latest` equals export on 608 / 27 different (cc capacity)
- **S2 coverage low, 3% / 5-8% extracted, no 180+ / cc / rl**
  - verdict: holds
  - new numbers: covered 2.6% / 5.9% of the book (5.8% / 11.0% of reachable); 180+ not in UC1's sample
- **S3 covered customers are a selected group, 15% vs 41% / cc**
  - verdict: holds
  - new numbers: reachable covered pay 21.2% vs 28.3% (-7.1); promise events with a transcript day 32.8% vs 50.7% (-18.0)
- **S3 / rl**
  - verdict: changes
  - new numbers: reachable covered 31.7% vs 29.9% (+1.8, no signal); promise-event gap -31.3 on n 12 vs 461
- **S4 unlogged 60% / 85%; unlogged pay more than no promise on loans / cc / rl**
  - verdict: holds
  - new numbers: unlogged within +-7 d on the CIF 59.9% / 80.7%; rl +13.0 [-0.2, +28.1] suggestive; cc +3.5 no signal
- **S5 stated disputes almost never in A3's flag / cc / rl**
  - verdict: holds
  - new numbers: 99.9% / 100% unflagged (rl DCORE codes have 27 events, so almost uninformative)
- **S6 specific statements go with payment (employed, salary cycle, amount or date, requests; card settlement the exception) / both**
  - verdict: changes
  - new numbers: employed yes (cc 20.9% vs 10.4% lost; rl 36.6% vs 18.5%); salary cycle lowest on cards (14.1%), highest on loans (35.3%); amount or date named +5.8 / +2.6 no signal; requests no difference (28.4 vs 29.0 / 57.7 vs 57.4); request type not delivered
- **S7 inside A1 Unknown a stated reading pays about twice no reading; able > unable on cards / cc / rl**
  - verdict: holds
  - new numbers: ratio 2.15 [1.53, 2.70] / 1.77 [1.30, 2.29]; able 23.5% vs unable 12.3% (AUC 0.528, interval includes 0.5)
- **S8 able vs partly able and the intent levels barely separate / cc / rl**
  - verdict: holds / changes
  - new numbers: able vs partly +5.8 / +5.4 pp, intervals include 0; intent in no_promise: cc no signal (AUC 0.585), rl separates (AUC 0.610, top vs second +15.8 [+6.1, +26.7])
- **S9 job and income claims loosely match income data, the match does not change payment / cc / rl**
  - verdict: holds
  - new numbers: match 45-50% of statements; flagged vs concordant intervals include 0 for F3 / F4 (cc -9.8, +6.1; rl -15.0, +3.2); F1 (says able while A1 Low) pays 25 pp less on cards
- **S10 transcript promises as A3 events move almost nothing / cc / rl**
  - verdict: holds
  - new numbers: 0.2 / 2.5 state changes per 1,000; state AUC +0.0000 / +0.0005 [-0.0003, +0.0014]; 0.8% / 2.8% of events
- **S11 calls at 61+ DPD are mostly extracted / cc**
  - verdict: changes
  - new numbers: 33.2% at 61-90, 57-68% above; 16.2% of all calls
- **S11 / rl**
  - verdict: holds
  - new numbers: 67.9 / 68.2 / 89.7% (35.0% of all calls); the 1-60 DPD gap cannot be isolated

## Verdicts

- **Delivered / full run (0.1, 0.4).** Six tables written 2026-11-23 04:54-04:56: export 5,040 CIFs (snapshot 2026-10-31), evidence in three overlapping partitions, posteriors and time-weighted at the same snapshot, plus the undated simple aggregation and conflicts for 5,751 CIFs. **It is not the full transcript run:** the store holds 14k-39k conversations a month, 1.1k-3.8k are extracted; cards 16% of model-CIF calls, loans 35%; latest conversation and latest transcript 2026-07-16 (nothing after July in the store; the post-July evidence rows are remarks). Settings differ from UC1's description (30-day half-life, remark weight 3.0); the 08-31 and 10-31 histories are identical up to 07-31 (09-30 is a smaller cut).
- **Bundle 26 (0.5).** Nothing breaks on columns or levels (all required columns present, no unknown level, `fraudulent_customer` is new but all NA in `signals_json`); the pipeline was not run. The overwritten aggregation / conflicts tables are undated and hold 5,751 CIFs; agreement with the persisted A5 / A6 is 89-95%, nothing becomes not-detected, 33 / 153 (cc) and <10 / 19 (rl) CIFs are newly covered.
- **Coverage and selection (1).** 60-180 only. Cards 2.6% of the book (5.8% of reachable), loans 5.9% (11.0%); concentrated at 61-90 DPD and in A3 levels with promises. Cards: covered reachable customers pay 7 pp less (strong, in every A3 level) and a call does not lift payment (-11 pp standardised); loans: no selection inside reachable. 180+ not run.
- **Which field and confidence (2).** Read our `latest` within 90 days (equal AUC to modal and 180-day rules; `support >= 2` helps on loan intent only); no fade with age. HIGH confidence is not worth requiring: it does not exist for capacity or intent (all LOW). The export is not point in time and its `supporting_data` is built from our income features: do not use as evidence or predictor.
- **Point in time (3).** Yes from the dated evidence (strictly before the month end), not from the export. The 08-31 and 10-31 partitions agree on every observation up to 07-31, so either gives the same past-month-end reads (09-30 is a smaller cut: do not use).
- **Decisions (strength = best current reading, not pass / fail).** D1: no signal (0.2 / 2.5 state changes per 1,000, AUC +0.0000 / +0.0005). D2: cards no signal (+3.5), loans suggestive (+13.0 [-0.2, +28.1]). D3: no signal (cc +3.3, rl +1.8). D4: suggestive, direction able > unable in both products, AUC 0.528 / 0.533 with intervals including 0.5, reading vs none ratio 2.15 / 1.77 (strong). D5: cards no signal, loans strong (AUC 0.610, 3m 0.710; top vs second +15.8 [+6.1, +26.7]). D6: "says able / pays in full while A1 Low" pays about 25 pp less than concordant on cards (suggestive to strong, concordant n 31), the other flags suggestive or no signal, loans n too small. D7: descriptive; reason separates payers (lost employment about half), requests and period do not; request has no type. D8: not run.
- **What the refresh would change most.** More extracted transcripts (cards 16%, loans 35% of calls; today at most 31% / 52% of called CIFs in July), calls after 2026-07-16 and a 3-month outcome window for July; request types and repayment amounts in the evidence (the export has none); an agent / team / queue field in the call metadata for 5.2; 180+ in scope; and more A1 Unknown / A3 no_promise rows on loans, where D4 and D6 strata are all below 10.
