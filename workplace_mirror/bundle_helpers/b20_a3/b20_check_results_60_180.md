# Bundle 20 check, CC and RL 60_180 (handoff 56, runs of 2026-11-10)

Transcribed from photos of the workplace `tmp_validation/a3_check/summary_cc_rl_60_180.md` (lines 1-310) by the cloud chat; sums checked there. Review: `b20_check_review.md`.

# Combined A3 check summary, CC 60-180 and RL 60-180 (runs of 2026-11-10)

Both runs completed 19 of 19 tasks, CC in 371.4 sec and RL in 298.4 sec. The observation month is 2026-08-31, with
CC n=19,292 and RL n=3,985, all matched to old. Every table below uses the compare-step numbers.

Variant key:
- **old**: previous A3 output.
- **old_m2**: old with the new thresholds.
- **grr_ep**: promise events, episode window.
- **grr**: promise events, 12-month window.
- **d30**: 30-day deadline instead of GRR.

The `-` in the tables means the combination did not occur.

## 1. State distribution

CC (n=19,292):

| State | old | old_m2 | grr_ep | grr | d30 |
|---|---:|---:|---:|---:|---:|
| high | 272 (1.4%) | 272 (1.4%) | 450 (2.3%) | 491 (2.5%) | 765 (4.0%) |
| low | 3,877 (20.1%) | 13,827 (71.7%) | 13,558 (70.3%) | 12,825 (66.5%) | 11,919 (61.8%) |
| moderate | 12,796 (66.3%) | 2,846 (14.8%) | 3,014 (15.6%) | 3,748 (19.4%) | 4,384 (22.7%) |
| unknown | 2,347 (12.2%) | 2,347 (12.2%) | 2,270 (11.8%) | 2,228 (11.5%) | 2,224 (11.5%) |

RL (n=3,985):

| State | old | old_m2 | grr_ep | grr | d30 |
|---|---:|---:|---:|---:|---:|
| high | 62 (1.6%) | 62 (1.6%) | 144 (3.6%) | 196 (4.9%) | 197 (4.9%) |
| low | 1,004 (25.2%) | 2,693 (67.6%) | 2,620 (65.7%) | 2,413 (60.6%) | 2,413 (60.6%) |
| moderate | 2,645 (66.4%) | 956 (24.0%) | 952 (23.9%) | 1,113 (27.9%) | 1,112 (27.9%) |
| unknown | 274 (6.9%) | 274 (6.9%) | 269 (6.8%) | 263 (6.6%) | 263 (6.6%) |

The per-node log lines differ from these by 1 row in a few cells. For CC grr, low is 12,824 and moderate is 3,749.
For CC d30, high is 764 and low is 11,920.

## 2. State transitions

**old x grr** (whole bundle). Changed: CC 10,074 (52.2%), RL 1,717 (43.1%).

| old -> grr | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| high -> high | 120 | 0.6% | 46 | 1.2% |
| high -> low | 13 | 0.1% | - | - |
| high -> moderate | 139 | 0.7% | 16 | 0.4% |
| low -> low | 3,575 | 18.5% | 933 | 23.4% |
| low -> moderate | 292 | 1.5% | 71 | 1.8% |
| low -> unknown | 10 | 0.1% | - | - |
| moderate -> high | 371 | 1.9% | 150 | 3.8% |
| moderate -> low | 9,100 | 47.2% | 1,469 | 36.9% |
| moderate -> moderate | 3,315 | 17.2% | 1,026 | 25.7% |
| moderate -> unknown | 10 | 0.1% | - | - |
| unknown -> low | 137 | 0.7% | 11 | 0.3% |
| unknown -> moderate | 2 | 0.0% | - | - |
| unknown -> unknown | 2,208 | 11.4% | 263 | 6.6% |

**old x old_m2** (thresholds only). Changed: CC 9,950 (51.6%), RL 1,689 (42.4%).

| old -> old_m2 | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| high -> high | 272 | 1.4% | 62 | 1.6% |
| low -> low | 3,877 | 20.1% | 1,004 | 25.2% |
| moderate -> low | 9,950 | 51.6% | 1,689 | 42.4% |
| moderate -> moderate | 2,846 | 14.8% | 956 | 24.0% |
| unknown -> unknown | 2,347 | 12.2% | 274 | 6.9% |

**old_m2 x grr_ep** (promise events). Changed: CC 1,644 (8.5%), RL 285 (7.2%).

| old_m2 -> grr_ep | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| high -> high | 115 | 0.6% | 45 | 1.1% |
| high -> low | 11 | 0.1% | - | - |
| high -> moderate | 146 | 0.8% | 17 | 0.4% |
| low -> high | 36 | 0.2% | 6 | 0.2% |
| low -> low | 13,094 | 67.9% | 2,569 | 64.5% |
| low -> moderate | 677 | 3.5% | 118 | 3.0% |
| low -> unknown | 20 | 0.1% | - | - |
| moderate -> high | 299 | 1.5% | 93 | 2.3% |
| moderate -> low | 358 | 1.9% | 46 | 1.2% |
| moderate -> moderate | 2,189 | 11.3% | 817 | 20.5% |
| unknown -> low | 95 | 0.5% | 5 | 0.1% |
| unknown -> moderate | 2 | 0.0% | - | - |
| unknown -> unknown | 2,250 | 11.7% | 269 | 6.8% |

**grr_ep x grr** (12-month window). Changed: CC 1,229 (6.4%), RL 281 (7.1%).

| grr_ep -> grr | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| high -> high | 425 | 2.2% | 142 | 3.6% |
| high -> low | 1 | 0.0% | - | - |
| high -> moderate | 24 | 0.1% | 2 | 0.1% |
| low -> low | 12,622 | 65.4% | 2,404 | 60.3% |
| low -> moderate | 936 | 4.9% | 216 | 5.4% |
| moderate -> high | 66 | 0.3% | 54 | 1.4% |
| moderate -> low | 160 | 0.8% | 3 | 0.1% |
| moderate -> moderate | 2,788 | 14.5% | 895 | 22.5% |
| unknown -> low | 42 | 0.2% | 6 | 0.2% |
| unknown -> unknown | 2,228 | 11.5% | 263 | 6.6% |

**grr x d30** (30 days instead of GRR). Changed: CC 1,206 (6.3%), RL 1 (0.0%).

| grr -> d30 | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| high -> high | 479 | 2.5% | 196 | 4.9% |
| high -> moderate | 12 | 0.1% | - | - |
| low -> high | 32 | 0.2% | - | - |
| low -> low | 11,902 | 61.7% | 2,413 | 60.6% |
| low -> moderate | 887 | 4.6% | - | - |
| low -> unknown | 4 | 0.0% | - | - |
| moderate -> high | 254 | 1.3% | 1 | 0.0% |
| moderate -> low | 9 | 0.0% | - | - |
| moderate -> moderate | 3,485 | 18.1% | 1,112 | 27.9% |
| unknown -> low | 8 | 0.0% | - | - |
| unknown -> unknown | 2,220 | 11.5% | 263 | 6.6% |

## 3. Promise events

Events in the window were 22,115 for CC and 3,379 for RL. The counts are the same for GRR and 30 days.

| kind -> source | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| followup_only -> followup | 9,440 | 42.7% | 1,974 | 58.4% |
| matched -> ptp | 6,977 | 31.5% | 968 | 28.6% |
| matched -> settlement | 304 | 1.4% | 4 | 0.1% |
| table_only -> ptp | 2,675 | 12.1% | 322 | 9.5% |
| table_only -> settlement | 2,719 | 12.3% | 111 | 3.3% |

Concluded events:

| window | CC | RL |
|---|---:|---:|
| GRR | 21,239 | 3,091 |
| 30 days | 20,838 | 3,091 |

**Outcome by kind, GRR**

| kind -> outcome | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| followup_only -> none | 4,983 | 23.5% | 321 | 10.4% |
| followup_only -> paid | 3,664 | 17.3% | 1,274 | 41.2% |
| followup_only -> partial | 475 | 2.2% | 240 | 7.8% |
| matched -> none | 4,309 | 20.3% | 148 | 4.8% |
| matched -> paid | 2,407 | 11.3% | 645 | 20.9% |
| matched -> partial | 480 | 2.3% | 117 | 3.8% |
| table_only -> none | 2,956 | 13.9% | 52 | 1.7% |
| table_only -> paid | 1,750 | 8.2% | 260 | 8.4% |
| table_only -> partial | 215 | 1.0% | 34 | 1.1% |

**Outcome by kind, 30 days**

| kind -> outcome | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| followup_only -> none | 3,690 | 17.7% | 322 | 10.4% |
| followup_only -> paid | 4,748 | 22.8% | 1,273 | 41.2% |
| followup_only -> partial | 603 | 2.9% | 240 | 7.8% |
| matched -> none | 2,825 | 13.6% | 148 | 4.8% |
| matched -> paid | 3,693 | 17.7% | 647 | 20.9% |
| matched -> partial | 626 | 3.0% | 115 | 3.7% |
| table_only -> none | 1,820 | 8.7% | 52 | 1.7% |
| table_only -> paid | 2,495 | 12.0% | 260 | 8.4% |
| table_only -> partial | 338 | 1.6% | 34 | 1.1% |

**GRR events concluded before the episode start** (12-month window only). CC has 8,133 events across 4,147
accounts. RL has 1,048 events across 593 accounts.

| outcome | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| none | 3,527 | 16.6% | 25 | 0.8% |
| paid | 3,991 | 18.8% | 922 | 29.8% |
| partial | 615 | 2.9% | 101 | 3.3% |

**Follow-up names** (GRR events in the window)

| name | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| CODE25 WILL PAY AT SALARY | 4,393 | 19.9% | 645 | 19.1% |
| DIGITAL COLLECT PTP SUBSCRIBED | 711 | 3.2% | 182 | 5.4% |
| EOSB_PTP_DOCUMENTS | 1 | 0.0% | - | - |
| PROMISE TO PAY | 6,512 | 29.4% | 918 | 27.2% |
| PROMISE TO PAY PARTIALLY | 6 | 0.0% | 7 | 0.2% |
| PROMISE TO PAY SCHEDULED | 5,094 | 23.0% | 1,194 | 35.3% |
| WILL PAY AT SALARY | 4 | 0.0% | - | - |

**Accounts with at least 1 concluded promise or instalment**

| product | old | GRR episode window | GRR | 30 days |
|---|---:|---:|---:|---:|
| CC | 4,626 | 5,627 | 7,905 | 7,786 |
| RL | 556 | 939 | 1,310 | 1,310 |

## 4. Levels (dimension A)

CC:

| level | old | grr_ep | grr | d30 |
|---|---:|---:|---:|---:|
| broken | 2,190 (11.4%) | 1,949 (10.1%) | 2,621 (13.6%) | 1,712 (8.9%) |
| kept | 208 (1.1%) | 221 (1.1%) | 441 (2.3%) | 1,053 (5.5%) |
| partly_kept | 682 (3.5%) | 1,317 (6.8%) | 2,686 (13.9%) | 3,419 (17.7%) |
| thin | 16,212 (84.0%) | 15,805 (81.9%) | 13,544 (70.2%) | 13,108 (67.9%) |

RL:

| level | old | grr_ep | grr | d30 |
|---|---:|---:|---:|---:|
| broken | 80 (2.0%) | 145 (3.6%) | 142 (3.6%) | 142 (3.6%) |
| kept | 73 (1.8%) | 213 (5.3%) | 385 (9.7%) | 385 (9.7%) |
| partly_kept | 243 (6.1%) | 322 (8.1%) | 556 (14.0%) | 557 (14.0%) |
| thin | 3,589 (90.1%) | 3,305 (82.9%) | 2,902 (72.8%) | 2,901 (72.8%) |

**old x grr level**

| old -> grr | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| broken -> broken | 1,044 | 5.4% | 30 | 0.8% |
| broken -> kept | 130 | 0.7% | 17 | 0.4% |
| broken -> partly_kept | 687 | 3.6% | 27 | 0.7% |
| broken -> thin | 329 | 1.7% | 6 | 0.2% |
| kept -> broken | 39 | 0.2% | 2 | 0.1% |
| kept -> kept | 22 | 0.1% | 49 | 1.2% |
| kept -> partly_kept | 87 | 0.5% | 21 | 0.5% |
| kept -> thin | 60 | 0.3% | 1 | 0.0% |
| partly_kept -> broken | 184 | 1.0% | 17 | 0.4% |
| partly_kept -> kept | 62 | 0.3% | 96 | 2.4% |
| partly_kept -> partly_kept | 267 | 1.4% | 100 | 2.5% |
| partly_kept -> thin | 169 | 0.9% | 30 | 0.8% |
| thin -> broken | 1,354 | 7.0% | 93 | 2.3% |
| thin -> kept | 227 | 1.2% | 223 | 5.6% |
| thin -> partly_kept | 1,645 | 8.5% | 408 | 10.2% |
| thin -> thin | 12,986 | 67.3% | 2,865 | 71.9% |

**old x grr_ep level**

| old -> grr_ep | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| broken -> broken | 998 | 5.2% | 36 | 0.9% |
| broken -> kept | 110 | 0.6% | 14 | 0.4% |
| broken -> partly_kept | 570 | 3.0% | 18 | 0.5% |
| broken -> thin | 512 | 2.7% | 12 | 0.3% |
| kept -> broken | 31 | 0.2% | 1 | 0.0% |
| kept -> kept | 19 | 0.1% | 48 | 1.2% |
| kept -> partly_kept | 90 | 0.5% | 23 | 0.6% |
| kept -> thin | 68 | 0.4% | 1 | 0.0% |
| partly_kept -> broken | 153 | 0.8% | 17 | 0.4% |
| partly_kept -> kept | 49 | 0.3% | 80 | 2.0% |
| partly_kept -> partly_kept | 262 | 1.4% | 109 | 2.7% |
| partly_kept -> thin | 218 | 1.1% | 37 | 0.9% |
| thin -> broken | 767 | 4.0% | 91 | 2.3% |
| thin -> kept | 43 | 0.2% | 71 | 1.8% |
| thin -> partly_kept | 395 | 2.0% | 172 | 4.3% |
| thin -> thin | 15,007 | 77.8% | 3,255 | 81.7% |

**grr_ep x grr level**

| grr_ep -> grr | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| broken -> broken | 1,860 | 9.6% | 128 | 3.2% |
| broken -> kept | - | - | 1 | 0.0% |
| broken -> partly_kept | 89 | 0.5% | 16 | 0.4% |
| kept -> broken | 1 | 0.0% | - | - |
| kept -> kept | 196 | 1.0% | 209 | 5.2% |
| kept -> partly_kept | 24 | 0.1% | 4 | 0.1% |
| partly_kept -> broken | 78 | 0.4% | 2 | 0.1% |
| partly_kept -> kept | 61 | 0.3% | 51 | 1.3% |
| partly_kept -> partly_kept | 1,178 | 6.1% | 269 | 6.8% |
| thin -> broken | 682 | 3.5% | 12 | 0.3% |
| thin -> kept | 184 | 1.0% | 124 | 3.1% |
| thin -> partly_kept | 1,395 | 7.2% | 267 | 6.7% |
| thin -> thin | 13,544 | 70.2% | 2,902 | 72.8% |

**grr x d30 level**

| grr -> d30 | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| broken -> broken | 1,705 | 8.8% | 142 | 3.6% |
| broken -> kept | 143 | 0.7% | - | - |
| broken -> partly_kept | 732 | 3.8% | - | - |
| broken -> thin | 41 | 0.2% | - | - |
| kept -> kept | 432 | 2.2% | 384 | 9.6% |
| kept -> partly_kept | 9 | 0.0% | 1 | 0.0% |
| partly_kept -> broken | 7 | 0.0% | - | - |
| partly_kept -> kept | 478 | 2.5% | 1 | 0.0% |
| partly_kept -> partly_kept | 2,175 | 11.3% | 555 | 13.9% |
| partly_kept -> thin | 26 | 0.1% | - | - |
| thin -> partly_kept | 503 | 2.6% | 1 | 0.0% |
| thin -> thin | 13,041 | 67.6% | 2,901 | 72.8% |

## 5. Contacts

**Refusal flag, old x new**

| old -> new | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| False -> False | 18,448 | 95.6% | 3,800 | 95.4% |
| True -> True | 844 | 4.4% | 185 | 4.6% |

**Last right-party disposition, old x new**

| old -> new | CC n | CC % | RL n | RL % |
|---|---:|---:|---:|---:|
| None -> None | 8,721 | 45.2% | 1,440 | 36.1% |
| dispute -> dispute | 74 | 0.4% | - | - |
| hung_up -> hung_up | 443 | 2.3% | 41 | 1.0% |
| paid -> paid | 2,168 | 11.2% | 545 | 13.7% |
| ptp -> paid | 686 | 3.6% | 233 | 5.8% |
| ptp -> ptp | 2,442 | 12.7% | 445 | 11.2% |
| refusal -> refusal | 908 | 4.7% | 206 | 5.2% |
| success -> success | 3,850 | 20.0% | 1,075 | 27.0% |

