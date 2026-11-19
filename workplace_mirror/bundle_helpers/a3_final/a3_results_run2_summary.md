# A3 results, run 2 - summary (persisted bundle 28 tables, all four model_ids)

Source: `results_a3_<model_id>.md` (PROD, persona_end_date 2026-08-31). Month shown: Aug 2026; trend Jan-Aug 2026.
Scored = no Unknown reason; every row of every model_id is scored, so accounts in scope = scored accounts.
Validation pools month ends Jan-May 2026 (3 full months of outcome); n = account-months, not accounts.
T2, T6.4 and T7 are laid out with model_ids as columns (shorter file); the other tables carry a model_id column.

## T1. Results (Aug 2026)

| model_id | product | accounts in scope | High | Moderate | Low |
|---|---|---|---|---|---|
| cc_60_180 | Cards | 19,292 | 2,215 | 5,861 | 11,216 |
| cc_180_plus | Cards | 318,663 | 2,125 | 13,099 | 303,439 |
| rl_60_180 | Personal Loans | 1,397 | 64 | 362 | 971 |
| rl_60_180 | Personal Cash Loans | 1,224 | 107 | 392 | 725 |
| rl_60_180 | Auto | 1,364 | 198 | 522 | 644 |
| rl_60_180 | Total | 3,985 | 369 | 1,276 | 2,340 |
| rl_180_plus | Personal Loans | 33,862 | 150 | 904 | 32,808 |
| rl_180_plus | Personal Cash Loans | 10,306 | 221 | 1,127 | 8,958 |
| rl_180_plus | Auto | 11,203 | 147 | 732 | 10,324 |
| rl_180_plus | Total | 55,371 | 518 | 2,763 | 52,090 |

## T2. Results detail (Aug 2026, scored rows; n and share of scored)

| item | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---|---|---|---|
| scored accounts | 19,292 | 318,663 | 3,985 | 55,371 |
| A kept | 620 (3.2%) | 227 (0.1%) | 134 (3.4%) | 73 (0.1%) |
| A partly_kept | 4,568 (23.7%) | 4,957 (1.6%) | 684 (17.2%) | 858 (1.5%) |
| A promised | 2,998 (15.5%) | 10,950 (3.4%) | 571 (14.3%) | 1,369 (2.5%) |
| A no_promise | 11,106 (57.6%) | 302,529 (94.9%) | 2,596 (65.1%) | 53,071 (95.8%) |
| B regular | 1,445 (7.5%) | 1,150 (0.4%) | 434 (10.9%) | 548 (1.0%) |
| B some | 3,388 (17.6%) | 17,732 (5.6%) | 1,290 (32.4%) | 3,987 (7.2%) |
| B none | 14,459 (74.9%) | 299,781 (94.1%) | 2,261 (56.7%) | 50,836 (91.8%) |
| C clean | 12,447 (64.5%) | 33,316 (10.5%) | 1,767 (44.3%) | 10,576 (19.1%) |
| C not_clean | 3,864 (20.0%) | 12,605 (4.0%) | 1,777 (44.6%) | 8,515 (15.4%) |
| C no_record | 2,981 (15.5%) | 272,742 (85.6%) | 441 (11.1%) | 36,280 (65.5%) |
| C no_record: censored | <10 | 173,718 (54.5%) | 0 (0.0%) | 32,184 (58.1%) |
| C no_record: too few months due | 2,976 (15.4%) | 99,024 (31.1%) | 441 (11.1%) | 4,096 (7.4%) |
| C other C value | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| points 0 | 3,171 (16.4%) | 268,919 (84.4%) | 804 (20.2%) | 41,662 (75.2%) |
| points 1 | 7,668 (39.7%) | 34,052 (10.7%) | 1,483 (37.2%) | 10,381 (18.7%) |
| points 2 | 3,431 (17.8%) | 8,730 (2.7%) | 822 (20.6%) | 2,049 (3.7%) |
| points 3 | 2,752 (14.3%) | 4,747 (1.5%) | 504 (12.6%) | 752 (1.4%) |
| points 4 | 1,534 (8.0%) | 1,942 (0.6%) | 255 (6.4%) | 417 (0.8%) |
| points 5 | 619 (3.2%) | 266 (0.1%) | 95 (2.4%) | 100 (0.2%) |
| points 6 | 117 (0.6%) | <10 | 22 (0.6%) | 10 (0.0%) |
| refusal flag | 865 (4.5%) | 6,514 (2.0%) | 170 (4.3%) | 1,000 (1.8%) |
| refusals that lower the state | 432 (2.2%) | 558 (0.2%) | 56 (1.4%) | 56 (0.1%) |
| refusals lifted (plan or payment) | 70 (0.4%) | 447 (0.1%) | 42 (1.1%) | 102 (0.2%) |
|   lifted by plan only | 12 (0.1%) | 136 (0.0%) | <10 | <10 |
|   lifted by payment only | 49 (0.3%) | 229 (0.1%) | 38 (1.0%) | 86 (0.2%) |
|   lifted, flag still set | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) | 0 (0.0%) |
| dispute | 75 (0.4%) | 570 (0.2%) | 0 (0.0%) | 58 (0.1%) |
| no pickup after contact | 1,344 (7.0%) | 2,901 (0.9%) | 329 (8.3%) | 403 (0.7%) |
| hung up | 442 (2.3%) | 4,562 (1.4%) | 41 (1.0%) | 615 (1.1%) |

## T3. State by DPD band (Aug 2026, scored rows)

| model_id | DPD band | High | Moderate | Low |
|---|---|---|---|---|
| cc_60_180 | 61-90 | 1,032 | 1,801 | 3,026 |
| cc_60_180 | 91-120 | 609 | 1,503 | 3,148 |
| cc_60_180 | 121-150 | 345 | 1,399 | 2,657 |
| cc_60_180 | 151-180 | 229 | 1,158 | 2,385 |
| cc_180_plus | 181-360 | 1,086 | 5,511 | 10,226 |
| cc_180_plus | 361-720 | 626 | 4,069 | 25,017 |
| cc_180_plus | 720+ | 413 | 3,519 | 268,196 |
| rl_60_180 | 61-90 | 202 | 505 | 694 |
| rl_60_180 | 91-120 | 87 | 387 | 632 |
| rl_60_180 | 121-150 | 59 | 266 | 646 |
| rl_60_180 | 151-180 | 21 | 118 | 368 |
| rl_180_plus | 181-360 | 301 | 1,539 | 2,086 |
| rl_180_plus | 361-720 | 77 | 631 | 4,140 |
| rl_180_plus | 720+ | 140 | 593 | 45,864 |

## T4. Trend (scored rows per month end)

| model_id | month | High | Moderate | Low |
|---|---|---|---|---|
| cc_60_180 | Jan 2026 | 2,386 | 4,571 | 7,707 |
| cc_60_180 | Feb 2026 | 2,378 | 4,454 | 7,744 |
| cc_60_180 | Mar 2026 | 2,347 | 4,413 | 7,695 |
| cc_60_180 | Apr 2026 | 2,250 | 4,656 | 7,765 |
| cc_60_180 | May 2026 | 2,270 | 5,244 | 8,376 |
| cc_60_180 | Jun 2026 | 2,315 | 5,512 | 9,155 |
| cc_60_180 | Jul 2026 | 2,230 | 5,805 | 10,362 |
| cc_60_180 | Aug 2026 | 2,215 | 5,861 | 11,216 |
| cc_180_plus | Jan 2026 | 1,776 | 12,262 | 291,219 |
| cc_180_plus | Feb 2026 | 1,843 | 12,326 | 292,685 |
| cc_180_plus | Mar 2026 | 1,899 | 12,337 | 294,506 |
| cc_180_plus | Apr 2026 | 1,954 | 12,384 | 296,371 |
| cc_180_plus | May 2026 | 1,986 | 12,361 | 298,279 |
| cc_180_plus | Jun 2026 | 2,070 | 12,652 | 300,105 |
| cc_180_plus | Jul 2026 | 2,099 | 12,867 | 301,772 |
| cc_180_plus | Aug 2026 | 2,125 | 13,099 | 303,439 |
| rl_60_180 | Jan 2026 | 293 | 799 | 1,232 |
| rl_60_180 | Feb 2026 | 284 | 717 | 1,212 |
| rl_60_180 | Mar 2026 | 293 | 731 | 1,194 |
| rl_60_180 | Apr 2026 | 328 | 924 | 1,409 |
| rl_60_180 | May 2026 | 285 | 1,080 | 1,731 |
| rl_60_180 | Jun 2026 | 299 | 1,161 | 2,054 |
| rl_60_180 | Jul 2026 | 326 | 1,184 | 2,218 |
| rl_60_180 | Aug 2026 | 369 | 1,276 | 2,340 |
| rl_180_plus | Jan 2026 | 458 | 2,363 | 49,836 |
| rl_180_plus | Feb 2026 | 457 | 2,359 | 50,066 |
| rl_180_plus | Mar 2026 | 449 | 2,348 | 50,473 |
| rl_180_plus | Apr 2026 | 460 | 2,308 | 50,847 |
| rl_180_plus | May 2026 | 485 | 2,408 | 51,113 |
| rl_180_plus | Jun 2026 | 509 | 2,556 | 51,318 |
| rl_180_plus | Jul 2026 | 515 | 2,626 | 51,678 |
| rl_180_plus | Aug 2026 | 518 | 2,763 | 52,090 |

## T5. 180+ vintage (Aug 2026)

| model_id | vintage | accounts in scope | High | Moderate | Low |
|---|---|---|---|---|---|
| cc_180_plus | early (< 24 m) | 61,112 | 1,907 | 10,601 | 48,604 |
| cc_180_plus | late (>= 24 m) | 257,551 | 218 | 2,498 | 254,835 |
| rl_180_plus | early (< 24 m) | 10,050 | 319 | 2,081 | 7,650 |
| rl_180_plus | late (>= 24 m) | 45,321 | 199 | 682 | 44,440 |

## T6. Validation (Jan-May 2026 month ends)

### T6.1 Per state

| model_id | state | n | paid_due % | paid_any % |
|---|---|---|---|---|
| cc_60_180 | high | 11,631 | 54.9% | 57.0% |
| cc_60_180 | moderate | 23,338 | 22.7% | 25.0% |
| cc_60_180 | low | 39,287 | 6.3% | 6.9% |
| cc_180_plus | high | 9,458 | 36.8% | 40.3% |
| cc_180_plus | moderate | 61,670 | 22.3% | 27.6% |
| cc_180_plus | low | 1,473,060 | 1.2% | 1.6% |
| rl_60_180 | high | 1,483 | 64.5% | 71.5% |
| rl_60_180 | moderate | 4,251 | 48.2% | 58.6% |
| rl_60_180 | low | 6,778 | 18.6% | 26.1% |
| rl_180_plus | high | 2,309 | 53.4% | 57.2% |
| rl_180_plus | moderate | 11,786 | 24.7% | 31.1% |
| rl_180_plus | low | 252,335 | 1.0% | 1.6% |

### T6.2 paid_due % by state within each group

| model_id | group | value | High n | High % | Mod n | Mod % | Low n | Low % |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | DPD band | 61-90 | 5,698 | 56.8% | 8,028 | 31.4% | 10,504 | 11.4% |
| cc_60_180 | DPD band | 91-120 | 3,072 | 60.3% | 5,806 | 24.6% | 9,738 | 7.2% |
| cc_60_180 | DPD band | 121-150 | 1,877 | 52.2% | 5,094 | 19.0% | 9,568 | 4.5% |
| cc_60_180 | DPD band | 151-180 | 984 | 31.8% | 4,410 | 8.8% | 9,477 | 1.5% |
| cc_180_plus | DPD band | 181-360 | 4,508 | 13.5% | 26,130 | 9.2% | 49,285 | 3.1% |
| cc_180_plus | DPD band | 361-720 | 3,361 | 53.7% | 20,106 | 22.6% | 141,154 | 2.6% |
| cc_180_plus | DPD band | 720+ | 1,589 | 66.8% | 15,434 | 44.3% | 1,282,621 | 1.0% |
| cc_180_plus | vintage | early (< 24 m) | 8,564 | 33.6% | 49,540 | 16.6% | 263,955 | 2.5% |
| cc_180_plus | vintage | late (>= 24 m) | 894 | 67.1% | 12,130 | 45.9% | 1,209,105 | 0.9% |
| rl_60_180 | DPD band | 61-90 | 726 | 70.8% | 1,805 | 56.2% | 2,290 | 28.3% |
| rl_60_180 | DPD band | 91-120 | 426 | 62.9% | 1,202 | 50.0% | 1,800 | 16.8% |
| rl_60_180 | DPD band | 121-150 | 246 | 55.3% | 860 | 36.5% | 1,669 | 11.2% |
| rl_60_180 | DPD band | 151-180 | 85 | 44.7% | 384 | 30.7% | 1,019 | 12.3% |
| rl_60_180 | RL product | Personal Loans | 296 | 64.5% | 1,244 | 35.8% | 3,120 | 12.0% |
| rl_60_180 | RL product | Personal Cash Loans | 477 | 67.7% | 1,493 | 47.1% | 2,172 | 16.3% |
| rl_60_180 | RL product | Auto | 710 | 62.3% | 1,514 | 59.4% | 1,486 | 35.9% |
| rl_180_plus | DPD band | 181-360 | 1,266 | 44.6% | 6,137 | 18.6% | 9,818 | 5.8% |
| rl_180_plus | DPD band | 361-720 | 472 | 59.3% | 3,044 | 22.9% | 21,028 | 3.1% |
| rl_180_plus | DPD band | 720+ | 571 | 68.0% | 2,605 | 41.2% | 221,489 | 0.6% |
| rl_180_plus | RL product | Personal Loans | 689 | 59.5% | 3,930 | 30.6% | 160,874 | 0.7% |
| rl_180_plus | RL product | Personal Cash Loans | 967 | 51.1% | 4,851 | 23.4% | 41,167 | 2.1% |
| rl_180_plus | RL product | Auto | 653 | 50.4% | 3,005 | 19.0% | 50,294 | 1.2% |
| rl_180_plus | vintage | early (< 24 m) | 1,492 | 45.2% | 8,792 | 18.0% | 37,602 | 3.5% |
| rl_180_plus | vintage | late (>= 24 m) | 817 | 68.4% | 2,994 | 44.4% | 214,733 | 0.6% |

### T6.3 AUC on paid_due

| model_id | score | scope | n | AUC |
|---|---|---|---|---|
| cc_60_180 | state | all | 74,256 | 0.771 |
| cc_60_180 | state | DPD band 61-90 | 24,230 | 0.732 |
| cc_60_180 | state | DPD band 91-120 | 18,616 | 0.776 |
| cc_60_180 | state | DPD band 121-150 | 16,539 | 0.780 |
| cc_60_180 | state | DPD band 151-180 | 14,871 | 0.791 |
| cc_60_180 | a3_points_total | all | 74,256 | 0.783 |
| cc_180_plus | state | all | 1,544,188 | 0.728 |
| cc_180_plus | state | DPD band 181-360 | 79,923 | 0.657 |
| cc_180_plus | state | DPD band 361-720 | 164,621 | 0.769 |
| cc_180_plus | state | DPD band 720+ | 1,299,644 | 0.687 |
| cc_180_plus | a3_points_total | all | 1,544,188 | 0.861 |
| rl_60_180 | state | all | 12,512 | 0.701 |
| rl_60_180 | state | DPD band 61-90 | 4,821 | 0.678 |
| rl_60_180 | state | DPD band 91-120 | 3,428 | 0.715 |
| rl_60_180 | state | DPD band 121-150 | 2,775 | 0.714 |
| rl_60_180 | state | DPD band 151-180 | 1,488 | 0.655 |
| rl_60_180 | a3_points_total | all | 12,512 | 0.730 |
| rl_180_plus | state | all | 266,430 | 0.790 |
| rl_180_plus | state | DPD band 181-360 | 17,221 | 0.713 |
| rl_180_plus | state | DPD band 361-720 | 24,544 | 0.750 |
| rl_180_plus | state | DPD band 720+ | 224,665 | 0.755 |
| rl_180_plus | a3_points_total | all | 266,430 | 0.890 |

### T6.4 paid_due % by a3_points_total (n; paid_due %)

| points | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---|---|---|---|
| 0 | 12,388; 4.9% | 1,329,664; 0.5% | 2,464; 9.5% | 204,495; 0.4% |
| 1 | 25,495; 6.6% | 141,101; 8.0% | 4,165; 23.6% | 47,525; 3.9% |
| 2 | 13,380; 19.0% | 40,668; 17.0% | 2,620; 42.4% | 8,646; 19.7% |
| 3 | 11,057; 26.1% | 23,031; 30.2% | 1,766; 54.9% | 3,432; 35.9% |
| 4 | 7,338; 46.8% | 8,696; 33.9% | 1,005; 61.5% | 1,837; 48.1% |
| 5 | 3,900; 64.5% | 990; 53.4% | 416; 66.6% | 468; 70.9% |
| 6 | 698; 70.3% | 38; 60.5% | 76; 89.5% | 27; 74.1% |

### T6.5 Stability (consecutive month ends, pooled)

| model_id | pairs | same | up | down | High stays | Mod stays |
|---|---|---|---|---|---|---|
| cc_60_180 | 83,907 | 88.3% | 5.1% | 6.6% | 80.7% | 80.4% |
| cc_180_plus | 2,169,028 | 99.2% | 0.3% | 0.4% | 85.9% | 88.8% |
| rl_60_180 | 14,737 | 86.7% | 6.0% | 7.3% | 77.9% | 79.4% |
| rl_180_plus | 374,900 | 99.1% | 0.4% | 0.5% | 87.1% | 89.3% |

### T6.6 Cramer's V of the A3 state with the other axes (Aug 2026)

| model_id | axis | Cramer's V | rows |
|---|---|---|---|
| cc_60_180 | A1 ability state | 0.163 | 19,292 |
| cc_60_180 | A2 reachability | 0.244 | 19,292 |
| cc_60_180 | A2 location | 0.214 | 19,292 |
| cc_60_180 | A4 family (det_state_label) | 0.457 | 19,292 |
| cc_180_plus | A1 ability state | 0.198 | 318,663 |
| cc_180_plus | A2 reachability | 0.283 | 318,663 |
| cc_180_plus | A2 location | 0.237 | 318,663 |
| cc_180_plus | A4 family (det_state_label) | 0.293 | 318,663 |
| rl_60_180 | A1 ability state | 0.099 | 3,985 |
| rl_60_180 | A2 reachability | 0.209 | 3,985 |
| rl_60_180 | A2 location | 0.210 | 3,985 |
| rl_60_180 | A4 family (det_state_label) | 0.405 | 3,985 |
| rl_180_plus | A1 ability state | 0.256 | 55,371 |
| rl_180_plus | A2 reachability | 0.313 | 55,371 |
| rl_180_plus | A2 location | 0.245 | 55,371 |
| rl_180_plus | A4 family (det_state_label) | 0.235 | 55,371 |

## T7. Checks (exact counts)

| check | cc_60_180 | cc_180_plus | rl_60_180 | rl_180_plus |
|---|---|---|---|---|
| Unknown rows, Aug 2026 | 0 | 0 | 0 | 0 |
| Unknown rows, all months | 0 | 0 | 0 | 0 |
| scored rows with state Unknown (exp 0) | 0 | 0 | 0 | 0 |
| rows checked, all months | 128927 | 2494416 | 23739 | 431003 |
| points differ from the three levels (exp 0) | 0 | 0 | 0 | 0 |
| state differs from points + refusal (exp 0) | 0 | 0 | 0 | 0 |
| points outside 0..6 (exp 0) | 0 | 0 | 0 | 0 |
| A level outside the four values (exp 0) | 0 | 0 | 0 | 0 |
| B level outside its three values (exp 0) | 0 | 0 | 0 | 0 |
| C level outside its three values (exp 0) | 0 | 0 | 0 | 0 |

## Notes

- Unknown is 0 everywhere: an episode without evidence scores 0 points and is Low (no_episode is the only Unknown).
- cc_180_plus 181-360: High pays 13.5% vs Moderate 9.2%; the CC band is derived from charge-off age.
- rl_60_180 dispute count is 0 (open item from a3_detail: check the dispute code).
- 180+ Dimension C is mostly no_record (cc 85.6%, rl 65.5%); censored rows are 54.5% (cc) and 58.1% (rl) of all.
- Refusal lift works: no row is lifted and still flagged (0 in all four).
- Points AUC beats state AUC at 180+: points 0 and 1 share Low but pay 0.5% vs 8.0% (cc), 0.4% vs 3.9% (rl).

1. High > Moderate > Low on paid_due holds in every group of all four; thin gaps: rl_60 Auto 62.3/59.4, cc_180 181-360.
2. State AUC (run 1): cc_60 0.771 (0.763), cc_180 0.728 (0.724), rl_60 0.701 (0.698), rl_180 0.790 (0.790).
3. Cards 61-180 Aug High/Mod/Low 11.5/30.4/58.1% vs back-test 11.8/32.9/55.3%; Low was 52.6% in Jan and grows.
4. Largest overlap is A4 (V 0.46 cc_60, 0.41 rl_60, 0.29 cc_180); rl_180 A2 reachability 0.31; A1 lowest (0.10-0.26).
5. T7: every check is 0 in all four model_ids and Unknown is 0; points and state recompute exactly.
6. Odd: points AUC beats state AUC at 180+ (0.861, 0.890); rl_60 dispute 0; 180+ C no_record 66-86%, mostly censored.
