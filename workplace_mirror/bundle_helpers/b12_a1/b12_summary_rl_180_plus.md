# A1 ability b12 check — RL (rl_180_plus), run 2026-11-03

Pipeline: `crx_rl_a1_ability_b12_check` (dev env). Config: dlq 7-7, collateral WO/SK, horizon 12 months.
Latest month 2026-08-31, base 55,371 accounts / 52,904 CIFs. Run time 556.3 s. Window W = 2026-03-01 .. 2026-08-31 (6 months).

## 1. New a1_state (2026-08-31, n=55,371)

| state | n | % |
|---|---:|---:|
| high | 17 | 0.0 |
| moderate | 1,987 | 3.6 |
| low | 3,793 | 6.9 |
| unknown | 49,574 | 89.5 |

By product x a1_state:

| product | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| Auto | 3 | 458 | 753 | 9,989 |
| Personal | 11 | 748 | 1,174 | 31,929 |
| Personal Cash | 3 | 781 | 1,866 | 7,656 |

## 2. Old x new a1_state

Row counts: new 55,371 / old 55,371 / new-only 0 / old-only 0.

| old | new | n | % |
|---|---|---:|---:|
| high | high | 16 | 0.0 |
| moderate | high | 1 | 0.0 |
| moderate | moderate | 1,791 | 3.2 |
| moderate | low | 105 | 0.2 |
| low | low | 3,675 | 6.6 |
| low | moderate | 193 | 0.3 |
| unknown | unknown | 49,574 | 89.5 |
| unknown | low | 13 | 0.0 |
| unknown | moderate | 3 | 0.0 |

Changed rows: 1 + 105 + 193 + 13 + 3 = 315 (0.6%).

## 3. New a1_state share by month (%)

| month | n | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 52,657 | 0.02 | 3.30 | 6.73 | 89.96 |
| 2026-02 | 52,882 | 0.03 | 3.33 | 6.65 | 89.98 |
| 2026-03 | 53,270 | 0.04 | 3.46 | 6.68 | 89.83 |
| 2026-04 | 53,615 | 0.03 | 3.45 | 6.74 | 89.78 |
| 2026-05 | 54,006 | 0.03 | 3.47 | 6.74 | 89.76 |
| 2026-06 | 54,383 | 0.03 | 3.53 | 6.40 | 90.04 |
| 2026-07 | 54,819 | 0.03 | 3.54 | 6.68 | 89.75 |
| 2026-08 | 55,371 | 0.03 | 3.59 | 6.85 | 89.53 |

Range over months (min-max %): high 0.02-0.04; moderate 3.30-3.59; low 6.40-6.85; unknown 89.53-90.04.

## 4. AECB step-wise build (rows per state)

| step | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| s0_no_aecb | 12 | 281 | 3,158 | 51,920 |
| s1_pull_months | 14 | 1,516 | 4,137 | 49,704 |
| s2_one_month_carry | 16 | 1,910 | 3,871 | 49,574 |
| s3_level_check | 17 | 1,987 | 3,793 | 49,574 |

Last step vs output: 0 states, 0 income levels differ.

Moves between steps:

| transition | from | to | n | % of moved |
|---|---|---|---:|---:|
| s0 → s1 (2,394 move) | low | moderate | 176 | 7.4 |
| | moderate | high | 2 | 0.1 |
| | unknown | low | 1,155 | 48.2 |
| | unknown | moderate | 1,061 | 44.3 |
| s1 → s2 (612 move) | low | moderate | 434 | 70.9 |
| | moderate | high | 2 | 0.3 |
| | moderate | low | 46 | 7.5 |
| | unknown | low | 122 | 19.9 |
| | unknown | moderate | 8 | 1.3 |
| s2 → s3 (289 move) | low | moderate | 183 | 63.3 |
| | moderate | high | 1 | 0.3 |
| | moderate | low | 105 | 36.3 |

## 5. Income

M4 income source in W x income level:

| source | level | n | % |
|---|---|---:|---:|
| both | stable | 16 | 0.0 |
| both | weak | 11 | 0.0 |
| bureau_only | stable | 1,927 | 3.5 |
| bureau_only | weak | 1,217 | 2.2 |
| internal_only | stable | 51 | 0.1 |
| internal_only | weak | 71 | 0.1 |
| neither | none | 52,078 | 94.1 |

Income source x a1_state:

| source | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| both | 1 | 14 | 12 | - |
| bureau | 5 | 1,708 | 1,431 | - |
| internal | 11 | 72 | 39 | - |
| none | - | 193 | 2,311 | 49,574 |

AECB months in W (with carry) x income level:

| months | stable | weak | none |
|---:|---:|---:|---:|
| 0 | 51 | 71 | 52,078 |
| 1 | 68 | 344 | - |
| 2 | 449 | 475 | - |
| 3 | 392 | 185 | - |
| 4 | 460 | 136 | - |
| 5 | 328 | 63 | - |
| 6 | 246 | 25 | - |

AECB in W, window total passes, 25% check fails: 430.

Salary stopped x income source x level:

| source | level | n | % |
|---|---|---:|---:|
| bureau | stable | 95 | 7.5 |
| bureau | weak | 119 | 9.3 |
| none | none | 1,059 | 83.2 |

Salary stopped x a1_state:

| stopped | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 17 | 1,891 | 3,317 | 48,873 |
| 1 | - | 96 | 476 | 701 |

## 6. Internal salary (>= 1000) history x a1_state

| history | n | % | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 149 | 0.3 | 12 | 86 | 51 | - |
| last_m7-12 | 1,273 | 2.3 | - | 96 | 476 | 701 |
| last_m13-24 | 3,963 | 7.2 | 1 | 355 | 962 | 2,645 |
| never | 49,986 | 90.3 | 4 | 1,450 | 2,304 | 46,228 |

## 7. AECB salary (>= 1000) by last pull month, before carry

| last pull | n | % |
|---|---:|---:|
| alert_never_salary | 21,760 | 39.3 |
| in_W | 2,981 | 5.4 |
| last_m7-12 | 1,045 | 1.9 |
| last_m13-24 | 1,181 | 2.1 |
| last_m25+ | 2,248 | 4.1 |
| no_alert_row | 26,156 | 47.2 |

Internal salary x AECB salary history (n):

| internal \ AECB | alert_never_salary | in_W | last_m7-12 | last_m13-24 | last_m25+ | no_alert_row |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 100 | 25 | 5 | 3 | 10 | 6 |
| last_m7-12 | 772 | 191 | 81 | 72 | 107 | 50 |
| last_m13-24 | 2,260 | 643 | 272 | 260 | 382 | 146 |
| never | 18,628 | 2,122 | 687 | 846 | 1,749 | 25,954 |

## 8. Liquidity

M5 CASA relationship x a1_state:

| CASA | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| active_casa | 13 | 320 | 1,086 | - |
| dormant_casa | 4 | 1,124 | 2,247 | 13,542 |
| no_casa | - | 543 | 460 | 36,032 |

M6 max monthly CASA balance in W x covers max(3000, anchor):

| balance | covers | n | % |
|---|---|---:|---:|
| <1000 | False | 7,237 | 13.1 |
| 1000-3000 | False | 274 | 0.5 |
| >=3,000 | True | 328 | 0.6 |
| >=3,000 | False | 79 | 0.1 |
| none | False | 47,453 | 85.7 |

M6 external card payment in W x liquidity level:

| ext card pay | adequate | weak | none |
|---|---:|---:|---:|
| False | 255 | 408 | 54,671 |
| True | 10 | 18 | 9 |

M6 liquidity level: adequate 265 (0.5%), weak 426 (0.8%), none 54,680 (98.8%).

## 9. Reasons

M7 unknown reason: no_casa 36,032 (72.7%); dormant_casa 13,542 (27.3%).

M8 low reason:

| reason | n | % |
|---|---:|---:|
| 1pt | 1,496 | 39.4 |
| 0pt_distress | 1,417 | 37.4 |
| 0pt_active_casa | 572 | 15.1 |
| 2-3pt_distress | 308 | 8.1 |

M9 moderate/high: state x income x liquidity x distress:

| state | income | liquidity | distress | n | % |
|---|---|---|---:|---:|---:|
| high | stable | adequate | 0 | 17 | 0.8 |
| moderate | none | adequate | 0 | 193 | 9.6 |
| moderate | stable | adequate | 1 | 8 | 0.4 |
| moderate | stable | none | 0 | 1,664 | 83.0 |
| moderate | stable | weak | 0 | 47 | 2.3 |
| moderate | weak | adequate | 0 | 13 | 0.6 |
| moderate | weak | weak | 0 | 62 | 3.1 |

## 10. Distress

M10 distress parts in W:

| parts | n | % |
|---|---:|---:|
| none | 53,383 | 96.4 |
| dds | 796 | 1.4 |
| bureau | 636 | 1.1 |
| cheque | 415 | 0.7 |
| cheque+dds | 71 | 0.1 |
| cheque+bureau | 41 | 0.1 |
| dds+bureau | 24 | 0.0 |
| cheque+dds+bureau | 5 | 0.0 |

M10 distress parts x a1_state (all distress rows are low or moderate):

| parts | low | moderate |
|---|---:|---:|
| bureau | 636 | - |
| cheque | 414 | 1 |
| cheque+bureau | 40 | 1 |
| cheque+dds | 70 | 1 |
| cheque+dds+bureau | 5 | - |
| dds | 791 | 5 |
| dds+bureau | 24 | - |

## 11. EOSB and anchor

M11 EOSB result in W x a1_state:

| EOSB | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 17 | 1,986 | 3,787 | 49,566 |
| 1 | - | 1 | 6 | 8 |

M11 EOSB in W x liquidity level: none 13 (86.7%), adequate 1 (6.7%), weak 1 (6.7%).

M11 anchor present: True 55,371 (100%); p10 / p50 / p90 = 323.83 / 1,616.98 / 5,960.62.

Anchor raises the income x CASA x card-payment floor (three flags, in the log's order):

| flag 1 | flag 2 | flag 3 | n | % |
|---|---|---|---:|---:|
| False | False | False | 8,320 | 15.0 |
| False | False | True | 17,673 | 31.9 |
| True | False | True | 15,180 | 27.4 |
| True | True | True | 14,198 | 25.6 |

## 12. By product: unknown reason and low reason

| product | dormant_casa (unknown) | no_casa (unknown) | 0pt_active_casa | 0pt_distress | 1pt | 2-3pt_distress |
|---|---|---|---|---|---|---|
| Auto | 2,349 (4.7%) | 7,640 (15.4%) | 58 (1.5%) | 380 (10.0%) | 242 (6.4%) | 73 (1.9%) |
| Personal | 8,134 (16.4%) | 23,795 (48.0%) | 196 (5.2%) | 321 (8.5%) | 568 (15.0%) | 89 (2.3%) |
| Personal Cash | 3,059 (6.2%) | 4,597 (9.3%) | 318 (8.4%) | 716 (18.9%) | 686 (18.1%) | 146 (3.8%) |

(Percentages as printed in the log; they are shares of the all-product unknown-reason / low-reason totals.)

## 13. Source depth and CASA legs

Source depth (month_end), base CIFs:

| source | range |
|---|---|
| feat_cif_internal_salary_monthly | 2024-09-30 .. 2026-08-31 |
| feat_cif_bureau_salary_monthly | 2022-10-31 .. 2026-11-30 |
| feat_cif_casa_balance_monthly | 2025-02-28 .. 2026-09-30 |
| feat_cif_casa_activity_monthly | 2025-02-28 .. 2026-10-31 |

CASA legs of base CIFs in W (2026-03-01 .. 2026-08-31):

| lane | legs | CIFs |
|---|---:|---:|
| signal | 243,275 | 1,278 |
| fee_interest | 20,992 | 4,513 |
| wash | 17,363 | 3,934 |
| card_spend | 15,188 | 252 |
| economic | 9,885 | 1,329 |
| ambiguous | 8,449 | 2,785 |
| own_loan | 3,291 | 1,238 |
| reversal | 2,008 | 785 |
| group_internal | 334 | 97 |
| card_payment | 309 | 118 |
| refund | 240 | 73 |
| unclassified | 8 | 5 |

Top unclassified / ambiguous: ambiguous MISCELLANEOUS 8,449; unclassified TRADE FINANCE 5; unclassified POS TRANSACTIONS 3.

## 14. WM vs FTR (base CIFs, last 12 months)

| WM row | WM positive | FTR leg | FTR customer leg | n | % |
|---|---|---|---|---:|---:|
| False | False | False | False | 479 | 0.9 |
| False | False | True | False | 204 | 0.4 |
| False | False | True | True | 127 | 0.2 |
| True | False | False | False | 34,956 | 66.1 |
| True | False | True | False | 7,389 | 14.0 |
| True | False | True | True | 322 | 0.6 |
| True | True | False | False | 3,284 | 6.2 |
| True | True | True | False | 2,712 | 5.1 |
| True | True | True | True | 3,431 | 6.5 |
