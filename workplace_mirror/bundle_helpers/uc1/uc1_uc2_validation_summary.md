# UC1 stated signals vs UC2 persona states - summary (cc_60_180, rl_60_180)

Scope: 60-180 only. The 180+ model_ids were not run: the UC1 sample did not cover their customers. Sources:
`results_uc1_uc2_cc_60_180.md`, `results_uc1_uc2_rl_60_180.md` (this folder), snippet version 2026-11-19e, A1 and A3
recomputed 2026-11-19 (A3 commitments levels: kept, partly_kept, promised, no_promise). The conversation set drops
legacy_only conversations.
Outcomes: payments end 2026-08-31, so only complete windows are used: 1-month window for the month ends Mar to Jul,
3-month window for Mar to May. Part A7 (outcomes at 2026-08-31) cannot be computed. Cells under 10 are shown as <10.
Small cells: read differences against the n in each cell.

### A1.1 rows whose evidence status changed when legacy conversations are dropped
| model_id | rows | moved (all) | moved from legacy_only | moved other than from legacy_only |
|---|---|---|---|---|
| cc_60_180 | 19,292 | 66 | 66 | 0 |
| rl_60_180 | 3,985 | 24 | 24 | 0 |

### A1.2 evidence (legacy dropped) x A2 reachability
| model_id | conv_status \ reach | n | reachable | non_reachable | unknown |
|---|---|---|---|---|---|
| cc_60_180 | extracted | 991 | 405 (40.9%) | 532 (53.7%) | 54 (5.4%) |
| cc_60_180 | not_extracted | 4,868 | 1,342 (27.6%) | 3,137 (64.4%) | 389 (8.0%) |
| cc_60_180 | no_conversation | 13,433 | 2,296 (17.1%) | 9,369 (69.7%) | 1,768 (13.2%) |
| rl_60_180 | extracted | 364 | 163 (44.8%) | 152 (41.8%) | 49 (13.5%) |
| rl_60_180 | not_extracted | 756 | 216 (28.6%) | 443 (58.6%) | 97 (12.8%) |
| rl_60_180 | no_conversation | 2,865 | 664 (23.2%) | 1,697 (59.2%) | 504 (17.6%) |

### A2.1 days from the last extracted conversation to 2026-08-31, by A5 state
| model_id | a5_state \ age_b | n | 31-60 | 61-90 | 91-180 |
|---|---|---|---|---|---|
| cc_60_180 | able | 127 | 35 (27.6%) | 37 (29.1%) | 55 (43.3%) |
| cc_60_180 | partly_able | 419 | 71 (16.9%) | 102 (24.3%) | 246 (58.7%) |
| cc_60_180 | unable | 144 | 19 (13.2%) | 45 (31.2%) | 80 (55.6%) |
| cc_60_180 | not_stated | 301 | 30 (10.0%) | 81 (26.9%) | 190 (63.1%) |
| rl_60_180 | able | 34 | <10 (<10) | 11 (32.4%) | 17 (50.0%) |
| rl_60_180 | partly_able | 156 | 30 (19.2%) | 38 (24.4%) | 88 (56.4%) |
| rl_60_180 | unable | 49 | 10 (20.4%) | 12 (24.5%) | 27 (55.1%) |
| rl_60_180 | not_stated | 125 | <10 (<10) | 26 (20.8%) | 90 (72.0%) |

### A3.1 A5 state x a1_state
| model_id | a5_state \ a1_state | n | high | moderate | low | unknown |
|---|---|---|---|---|---|---|
| cc_60_180 | able | 127 | <10 (<10) | 32 (25.2%) | 39 (30.7%) | 50 (39.4%) |
| cc_60_180 | partly_able | 419 | 11 (2.6%) | 95 (22.7%) | 167 (39.9%) | 146 (34.8%) |
| cc_60_180 | unable | 144 | <10 (<10) | 20 (13.9%) | 55 (38.2%) | 68 (47.2%) |
| cc_60_180 | not_stated | 301 | 11 (3.7%) | 63 (20.9%) | 108 (35.9%) | 119 (39.5%) |
| rl_60_180 | able | 34 | <10 (<10) | <10 (<10) | 15 (44.1%) | 13 (38.2%) |
| rl_60_180 | partly_able | 156 | 0 | 37 (23.7%) | 75 (48.1%) | 44 (28.2%) |
| rl_60_180 | unable | 49 | <10 (<10) | <10 (<10) | 28 (57.1%) | 16 (32.7%) |
| rl_60_180 | not_stated | 125 | <10 (<10) | 12 (9.6%) | 67 (53.6%) | 45 (36.0%) |

### A4.1 A6 state x a3_state
| model_id | a6_state \ a3_state | n | high | moderate | low |
|---|---|---|---|---|---|
| cc_60_180 | pays_in_full | 191 | 35 (18.3%) | 131 (68.6%) | 25 (13.1%) |
| cc_60_180 | partly_or_later | 543 | 123 (22.7%) | 304 (56.0%) | 116 (21.4%) |
| cc_60_180 | refuses | 38 | <10 (<10) | 19 (50.0%) | 17 (44.7%) |
| cc_60_180 | not_stated | 219 | 31 (14.2%) | 103 (47.0%) | 85 (38.8%) |
| rl_60_180 | pays_in_full | 74 | 13 (17.6%) | 40 (54.1%) | 21 (28.4%) |
| rl_60_180 | partly_or_later | 210 | 32 (15.2%) | 108 (51.4%) | 70 (33.3%) |
| rl_60_180 | refuses | <10 | 0 | <10 (<10) | <10 (<10) |
| rl_60_180 | not_stated | 74 | 12 (16.2%) | 34 (45.9%) | 28 (37.8%) |

### A5.1 support: capacity conversations, agreement, A5 = A1 concordance
| model_id | conversations | rows | agree share (agree / conversations) | unanimous rows | comparable rows (A1 scored) |
 A5 = A1 concordance |
|---|---|---|---|---|---|---|
| cc_60_180 | 1 | 300 | 99.7% | 99.7% | 169 | 34.9% |
| cc_60_180 | 2 | 216 | 82.6% | 65.3% | 147 | 34.7% |
| cc_60_180 | 3-5 | 135 | 77.8% | 37.0% | 86 | 41.9% |
| cc_60_180 | 6+ | 39 | 71.3% | <10 | 24 | 41.7% |
| rl_60_180 | 1 | 114 | 100.0% | 100.0% | 77 | 36.4% |
| rl_60_180 | 2 | 62 | 75.8% | 51.6% | 43 | 48.8% |
| rl_60_180 | 3-5 | 49 | 77.5% | 42.9% | 34 | 41.2% |
| rl_60_180 | 6+ | 14 | 82.1% | <10 | 12 | <10 |

### A6.2 Non-Reachable rows with an extracted conversation: last extracted conversation vs A2 dates
| model_id | rel \ a6_state | n | pays_in_full | partly_or_later | refuses | not_stated |
|---|---|---|---|---|---|---|
| cc_60_180 | 1 before the A2 window start | 316 | 50 (15.8%) | 169 (53.5%) | 10 (3.2%) | 87 (27.5%) |
| cc_60_180 | 2 in the window, on or before the last contact (before the failed days) | 150 | 42 (28.0%) | 77 (51.3%) |
 <10 (<10) | 28 (18.7%) |
| cc_60_180 | 3 in the window, after the last contact, on or before the last attempt (inside or before the failed span)
 | 66 | 13 (19.7%) | 32 (48.5%) | <10 (<10) | 16 (24.2%) |
| rl_60_180 | 1 before the A2 window start | 94 | 15 (16.0%) | 56 (59.6%) | <10 (<10) | 21 (22.3%) |
| rl_60_180 | 2 in the window, on or before the last contact (before the failed days) | 29 | <10 (<10) | 19 (65.5%) | 0
 | <10 (<10) |
| rl_60_180 | 3 in the window, after the last contact, on or before the last attempt (inside or before the failed span)
 | 29 | 10 (34.5%) | 16 (55.2%) | 0 | <10 (<10) |

### B1.1 account-months and readings per month end
| model_id | month end | account-months | with a conversation | with an extracted conversation | with an L capacity |
 with an L intent |
|---|---|---|---|---|---|---|
| cc_60_180 | 2026-03-31 | 14,455 | 70 | 40 | 16 | 21 |
| cc_60_180 | 2026-04-30 | 14,671 | 626 | 208 | 105 | 128 |
| cc_60_180 | 2026-05-31 | 15,890 | 2,058 | 455 | 282 | 328 |
| cc_60_180 | 2026-06-30 | 16,982 | 3,441 | 704 | 463 | 527 |
| cc_60_180 | 2026-07-31 | 18,397 | 4,834 | 879 | 569 | 644 |
| rl_60_180 | 2026-03-31 | 2,218 | 74 | 60 | 23 | 27 |
| rl_60_180 | 2026-04-30 | 2,661 | 294 | 160 | 89 | 109 |
| rl_60_180 | 2026-05-31 | 3,096 | 577 | 265 | 145 | 184 |
| rl_60_180 | 2026-06-30 | 3,514 | 817 | 345 | 204 | 258 |
| rl_60_180 | 2026-07-31 | 3,728 | 963 | 369 | 222 | 280 |

### B2.1 paid_due by L capacity, overall, 1-month window (month ends Mar-Jul)
| model_id | level | n | paid_due % | paid_any % |
|---|---|---|---|---|
| cc_60_180 | able | 273 | 22.3% (273) | 23.4% (273) |
| cc_60_180 | partly_able | 854 | 18.7% (854) | 22.7% (854) |
| cc_60_180 | unable | 308 | 14.0% (308) | 15.3% (308) |
| cc_60_180 | not_stated | 851 | 14.5% (851) | 17.0% (851) |
| cc_60_180 | no_reading | 78,109 | 11.5% (78,109) | 13.0% (78,109) |
| rl_60_180 | able | 146 | 30.8% (146) | 41.1% (146) |
| rl_60_180 | partly_able | 379 | 36.1% (379) | 49.1% (379) |
| rl_60_180 | unable | 158 | 20.9% (158) | 31.6% (158) |
| rl_60_180 | not_stated | 516 | 26.9% (516) | 37.4% (516) |
| rl_60_180 | no_reading | 14,018 | 18.8% (14,018) | 25.5% (14,018) |

### B2.2 paid_due by L capacity within a1_state, 1-month window
| model_id | L capacity | All | high | moderate | low | unknown |
|---|---|---|---|---|---|---|
| cc_60_180 | able | 22.3% (273) | 39.5% (38) | 18.5% (65) | 18.6% (86) | 21.4% (84) |
| cc_60_180 | partly_able | 18.7% (854) | 28.0% (50) | 16.9% (236) | 20.1% (304) | 17.0% (264) |
| cc_60_180 | unable | 14.0% (308) | <10 | <10 | 14.4% (153) | 12.0% (100) |
| cc_60_180 | not_stated | 14.5% (851) | 20.4% (49) | 11.3% (221) | 14.8% (325) | 15.6% (256) |
| cc_60_180 | no_reading | 11.5% (78,109) | 26.2% (1,480) | 18.8% (13,786) | 12.5% (20,833) | 8.2% (42,010) |
| rl_60_180 | able | 30.8% (146) | <10 | 38.5% (26) | 26.2% (65) | 30.6% (49) |
| rl_60_180 | partly_able | 36.1% (379) | <10 | 52.0% (75) | 36.9% (195) | 24.3% (103) |
| rl_60_180 | unable | 20.9% (158) | - | <10 | 18.8% (101) | <10 |
| rl_60_180 | not_stated | 26.9% (516) | <10 | 28.0% (100) | 28.3% (290) | 23.9% (117) |
| rl_60_180 | no_reading | 18.8% (14,018) | 28.3% (92) | 32.8% (1,407) | 18.4% (7,049) | 15.5% (5,470) |

### B2.4 paid_due by L intent within a3_state, 1-month window
| model_id | L intent | All | high | moderate | low |
|---|---|---|---|---|---|
| cc_60_180 | pays_in_full | 19.1% (392) | 33.3% (90) | 16.8% (244) | <10 |
| cc_60_180 | partly_or_later | 18.1% (1,153) | 31.7% (252) | 16.4% (627) | 9.5% (274) |
| cc_60_180 | refuses | 14.6% (103) | <10 | <10 | <10 |
| cc_60_180 | not_stated | 13.8% (638) | 26.4% (106) | 16.8% (297) | 4.3% (235) |
| cc_60_180 | no_reading | 11.5% (78,109) | 38.8% (10,950) | 13.5% (24,420) | 3.4% (42,739) |
| rl_60_180 | pays_in_full | 34.1% (258) | 62.2% (37) | 32.1% (134) | 25.3% (87) |
| rl_60_180 | partly_or_later | 29.5% (560) | 42.7% (96) | 30.7% (280) | 20.7% (184) |
| rl_60_180 | refuses | <10 | <10 | <10 | <10 |
| rl_60_180 | not_stated | 27.6% (341) | 31.4% (51) | 29.1% (151) | 24.5% (139) |
| rl_60_180 | no_reading | 18.8% (14,018) | 44.7% (1,343) | 27.0% (4,509) | 10.0% (8,166) |

### B2.9 how often L and M differ
| model_id | signal | rows with both | L differs from M | share |
|---|---|---|---|---|
| cc_60_180 | capacity | 1,435 | 72 | 5.0% |
| cc_60_180 | intent | 1,648 | 87 | 5.3% |
| rl_60_180 | capacity | 683 | 25 | 3.7% |
| rl_60_180 | intent | 858 | 27 | 3.1% |

### B3.2 gap between best and worst capacity level per age bucket, 1-month window
| model_id | gap | 0-30 | 31-60 | 61-90 | 91+ |
|---|---|---|---|---|---|
| cc_60_180 | best - worst | +0.8 pp (partly_able vs able) | +19.1 pp (able vs unable) | +15.7 pp (able vs unable) |
 +2.1 pp (unable vs partly_able) |
| rl_60_180 | best - worst | +12.4 pp (partly_able vs able) | +15.1 pp (able vs unable) | +2.8 pp (partly_able vs able)
 | - |

### B3.4 gap between best and worst intent level per age bucket, 1-month window
| model_id | gap | 0-30 | 31-60 | 61-90 | 91+ |
|---|---|---|---|---|---|
| cc_60_180 | best - worst | +0.8 pp (pays_in_full vs partly_or_later) | +6.1 pp (pays_in_full vs partly_or_later) |
 +4.6 pp (pays_in_full vs partly_or_later) | +10.0 pp (partly_or_later vs pays_in_full) |
| rl_60_180 | best - worst | +0.3 pp (pays_in_full vs partly_or_later) | +6.7 pp (pays_in_full vs partly_or_later) |
 +16.4 pp (pays_in_full vs partly_or_later) | +7.6 pp (partly_or_later vs pays_in_full) |

### B4.1 AUC on paid_due, state alone vs state then stated level, 1-month window
| model_id | signal | reading | rows | n | paid_due n | AUC state alone | AUC state then level | difference |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | capacity | L | all rows | 9,393 | 10,597 | 0.606 | 0.607 | 0.001 |
| cc_60_180 | capacity | L | rows with a reading | 264 | 305 | 0.533 | 0.544 | 0.011 |
| cc_60_180 | intent | L | all rows | 9,393 | 10,597 | 0.769 | 0.770 | 0.001 |
| cc_60_180 | intent | L | rows with a reading | 299 | 347 | 0.637 | 0.637 | 0.001 |
| rl_60_180 | capacity | L | all rows | 2,986 | 4,069 | 0.569 | 0.574 | 0.005 |
| rl_60_180 | capacity | L | rows with a reading | 215 | 296 | 0.572 | 0.589 | 0.016 |
| rl_60_180 | intent | L | all rows | 2,986 | 4,069 | 0.680 | 0.685 | 0.005 |
| rl_60_180 | intent | L | rows with a reading | 260 | 357 | 0.607 | 0.617 | 0.010 |

### B4.2 AUC on paid_due, state alone vs state then stated level, 3-month window
| model_id | signal | reading | rows | n | paid_due n | AUC state alone | AUC state then level | difference |
|---|---|---|---|---|---|---|---|---|
| cc_60_180 | capacity | L | all rows | 8,272 | 8,886 | 0.610 | 0.611 | 0.001 |
| cc_60_180 | capacity | L | rows with a reading | 143 | 160 | 0.581 | 0.589 | 0.008 |
| cc_60_180 | intent | L | all rows | 8,272 | 8,886 | 0.760 | 0.761 | 0.001 |
| cc_60_180 | intent | L | rows with a reading | 167 | 186 | 0.631 | 0.625 | -0.007 |
| rl_60_180 | capacity | L | all rows | 2,815 | 3,481 | 0.573 | 0.578 | 0.004 |
| rl_60_180 | capacity | L | rows with a reading | 154 | 168 | 0.567 | 0.569 | 0.002 |
| rl_60_180 | intent | L | all rows | 2,815 | 3,481 | 0.691 | 0.699 | 0.008 |
| rl_60_180 | intent | L | rows with a reading | 197 | 216 | 0.599 | 0.617 | 0.018 |

### B4.4 paid_due by conversation status within a3_state, 1-month window
| model_id | a3_state | All | extracted | not_extracted | no_conversation |
|---|---|---|---|---|---|
| cc_60_180 | high | 38.5% (11,412) | 31.0% (462) | 25.7% (1,206) | 40.4% (9,744) |
| cc_60_180 | moderate | 13.6% (25,630) | 16.6% (1,210) | 12.9% (4,112) | 13.6% (20,308) |
| cc_60_180 | low | 3.5% (43,353) | 7.0% (614) | 5.7% (3,425) | 3.2% (39,314) |
| rl_60_180 | high | 44.5% (1,531) | 43.6% (188) | 48.4% (126) | 44.3% (1,217) |
| rl_60_180 | moderate | 27.4% (5,080) | 30.5% (571) | 24.9% (574) | 27.3% (3,935) |
| rl_60_180 | low | 10.6% (8,606) | 22.3% (440) | 11.9% (826) | 9.7% (7,340) |

### B6.1 paid_due by L capacity within A2 reachability, 1-month window
| model_id | L capacity | All | reachable | non_reachable | unknown |
|---|---|---|---|---|---|
| cc_60_180 | able | 22.3% (273) | 28.3% (159) | 14.3% (98) | <10 |
| cc_60_180 | partly_able | 18.7% (854) | 23.3% (443) | 14.3% (371) | <10 |
| cc_60_180 | unable | 14.0% (308) | 17.7% (181) | <10 | <10 |
| cc_60_180 | not_stated | 14.5% (851) | 20.5% (366) | 10.8% (427) | <10 |
| cc_60_180 | no_reading | 11.5% (78,109) | 28.7% (19,276) | 5.9% (50,409) | 6.3% (8,424) |
| rl_60_180 | able | 30.8% (146) | 35.5% (76) | 27.3% (55) | <10 |
| rl_60_180 | partly_able | 36.1% (379) | 36.0% (214) | 37.5% (136) | <10 |
| rl_60_180 | unable | 20.9% (158) | 21.4% (84) | 21.3% (61) | <10 |
| rl_60_180 | not_stated | 26.9% (516) | 33.8% (207) | 19.4% (211) | 28.6% (98) |
| rl_60_180 | no_reading | 18.8% (14,018) | 30.4% (3,950) | 13.1% (7,844) | 18.2% (2,224) |

### C1.1 conversation holders, extracted vs not, 1-month window
| model_id | group | account-months | paid_due % (n) |
|---|---|---|---|
| cc_60_180 | extracted | 2,286 | 16.9% (2,286) |
| cc_60_180 | not extracted | 8,743 | 11.9% (8,743) |
| rl_60_180 | extracted | 1,199 | 29.5% (1,199) |
| rl_60_180 | not extracted | 1,526 | 19.8% (1,526) |

### C1.2 A2 reachability, extracted vs not (column shares)
| model_id | reach | extracted n | extracted % | not extracted n | not extracted % |
|---|---|---|---|---|---|
| cc_60_180 | reachable | 1,149 | 50.3% | 2,960 | 33.9% |
| cc_60_180 | non_reachable | 1,015 | 44.4% | 5,145 | 58.8% |
| cc_60_180 | unknown | 122 | 5.3% | 638 | 7.3% |
| rl_60_180 | reachable | 581 | 48.5% | 566 | 37.1% |
| rl_60_180 | non_reachable | 463 | 38.6% | 784 | 51.4% |
| rl_60_180 | unknown | 155 | 12.9% | 176 | 11.5% |

### C2.1 paid_due by L capacity, unweighted vs reweighted, 1-month window
| model_id | level | n | unweighted | reweighted |
|---|---|---|---|---|
| cc_60_180 | able | 273 | 22.3% (273) | 21.9% |
| cc_60_180 | partly_able | 854 | 18.7% (854) | 17.5% |
| cc_60_180 | unable | 308 | 14.0% (308) | 12.3% |
| cc_60_180 | not_stated | 851 | 14.5% (851) | 12.5% |
| rl_60_180 | able | 146 | 30.8% (146) | 29.4% |
| rl_60_180 | partly_able | 379 | 36.1% (379) | 34.5% |
| rl_60_180 | unable | 158 | 20.9% (158) | 20.6% |
| rl_60_180 | not_stated | 516 | 26.9% (516) | 26.9% |

### X1 UC1 aggregation level vs the most frequent primary level per conversation, per CIF
| model_id | signal | result | CIFs |
|---|---|---|---|
| cc_60_180 | capacity | different level | <10 |
| cc_60_180 | intent | different level | 17 |
| rl_60_180 | capacity | different level | <10 |
| rl_60_180 | intent | different level | <10 |

### X2 shipped support counts vs recomputed from the grid
| model_id | a5_conversations_n equal | a5_conversations_n different | a6_conversations_n equal | a6_conversations_n
 different |
|---|---|---|---|---|
| cc_60_180 | 991 | 0 | 991 | 0 |
| rl_60_180 | 364 | 0 | 364 | 0 |
### Verdicts

1. Age of the stated signals at the latest month: none is fresh, no last extracted conversation is under a month old and
   about half or more are older than three months (A2.1), because calls stop in mid July and the stated block is only
   scored at the end of August.
2. Stated ability adds nothing usable to A1 on paid_due: the AUC gain is negligible on all rows and noisy on the few
   rows with a reading (B4.1, B4.2), and inside an A1 state the able, partly_able and unable ordering is weak and
   inconsistent (B2.2).
3. Stated intent adds almost nothing to A3: no gain in cc_60_180, a small gain in rl_60_180 that stays within noise
   (B4.1, B4.2); a pays_in_full edge over partly_or_later shows up inside A3 states in rl_60_180 and mostly not in
   cc_60_180 (B2.4), and refuses is too small to judge.
4. L and M do not differ in value: they disagree on a few percent of rows (B2.9) and give the same AUC and the same
   level ordering (B4.1, B4.2).
5. The signal does not show decay with age: level rates do not fall and the gap between best and worst level does not
   shrink as the reading ages (B3.2, B3.4); the 3-month window only reaches readings up to 90 days (month ends Mar to
   May), so this rests on the 1-month window and on small cells.
6. Non-Reachable customers have UC1 conversations because they were reached earlier and then stopped answering: no last
   conversation falls after the last A2 attempt and most precede the A2 window (A6.2), and Non-Reachable customers with
   a reading pay more than those without (B6.1), so the stated level mainly marks that earlier contact; the oldest
   failed call day is not in the A2 output, so the middle class of A6.2 cannot be placed exactly.
7. The sample is not representative of the conversation holders in composition (more Reachable, fewer A3 Low, higher
   paid_due; C1.1, C1.2), but reweighting on A3 state by DPD band moves level rates only slightly and keeps their order
   (C2.1); it is enough for a coarse read of level ordering, not for within-state comparisons, and having a
   reading is itself a selection effect (B4.4).
8. No defect found in the UC1 inputs or bundle 26's output: the shipped evidence differs from the recomputed one only
   for legacy_only rows (A1.1), the shipped support counts equal the recomputed ones (X2) and UC1's aggregation matches
   the per-conversation grid except for a handful of intent customers (X1), which UC1's detection counting could explain
   (not tested); two items to carry: bundle 26 still ships the legacy_only label, and the payments table ending at the
   end of August is a data limit that blocks outcome windows after it.
