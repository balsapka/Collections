# A1 ability b12 check — RL (rl_60_180), run 2026-11-03

Pipeline: `crx_rl_a1_ability_b12_check` (dev env). Config: dlq 3-6, collateral WO/SK, horizon 1 month.
Latest month 2026-08-31, base 3,985 accounts / 3,608 CIFs. Run time 474.2 s. Window W = 2026-06-01 .. 2026-08-31 (3 months).

## 1. New a1_state (2026-08-31, n=3,985)

| state | n | % |
|---|---:|---:|
| high | 10 | 0.3 |
| moderate | 362 | 9.1 |
| low | 1,835 | 46.0 |
| unknown | 1,778 | 44.6 |

By product x a1_state:

| product | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| Auto | 1 | 125 | 636 | 602 |
| Personal | 6 | 99 | 595 | 697 |
| Personal Cash | 3 | 138 | 604 | 479 |

## 2. Old x new a1_state

Row counts: new 3,985 / old 3,985 / new-only 0 / old-only 0.

| old | new | n | % |
|---|---|---:|---:|
| high | high | 10 | 0.3 |
| high | moderate | 1 | 0.0 |
| moderate | moderate | 342 | 8.6 |
| moderate | low | 16 | 0.4 |
| low | low | 1,818 | 45.6 |
| low | moderate | 19 | 0.5 |
| unknown | unknown | 1,778 | 44.6 |
| unknown | low | 1 | 0.0 |

Changed rows: 1 + 16 + 19 + 1 = 37 (0.9%).

## 3. New a1_state share by month (%)

| month | n | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 2,324 | 0.04 | 12.61 | 46.13 | 41.22 |
| 2026-02 | 2,213 | 0.09 | 10.85 | 44.33 | 44.74 |
| 2026-03 | 2,218 | 0.14 | 11.09 | 46.03 | 42.74 |
| 2026-04 | 2,661 | 0.15 | 12.14 | 47.50 | 40.21 |
| 2026-05 | 3,096 | 0.10 | 11.82 | 48.80 | 39.28 |
| 2026-06 | 3,514 | 0.17 | 10.36 | 48.78 | 40.69 |
| 2026-07 | 3,728 | 0.08 | 9.68 | 47.37 | 42.86 |
| 2026-08 | 3,985 | 0.25 | 9.08 | 46.05 | 44.62 |

Range over months (min-max %): high 0.04-0.25; moderate 9.08-12.61; low 44.33-48.80; unknown 39.28-44.74.

## 4. AECB step-wise build (rows per state)

| step | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| s0_no_aecb | 9 | 89 | 1,811 | 2,076 |
| s1_pull_months | 11 | 278 | 1,864 | 1,832 |
| s2_one_month_carry | 11 | 360 | 1,836 | 1,778 |
| s3_level_check | 10 | 362 | 1,835 | 1,778 |

Last step vs output: 0 states, 0 income levels differ.

Moves between steps:

| transition | from | to | n | % of moved |
|---|---|---|---:|---:|
| s0 → s1 (315 move) | low | moderate | 69 | 21.9 |
| | moderate | high | 2 | 0.6 |
| | unknown | low | 122 | 38.7 |
| | unknown | moderate | 122 | 38.7 |
| s1 → s2 (130 move) | low | moderate | 74 | 56.9 |
| | moderate | low | 2 | 1.5 |
| | unknown | low | 44 | 33.8 |
| | unknown | moderate | 10 | 7.7 |
| s2 → s3 (34 move) | high | moderate | 1 | 2.9 |
| | low | moderate | 17 | 50.0 |
| | moderate | low | 16 | 47.1 |

## 5. Income

M4 income source in W x income level:

| source | level | n | % |
|---|---|---:|---:|
| both | stable | 13 | 0.3 |
| both | weak | 8 | 0.2 |
| bureau_only | stable | 317 | 8.0 |
| bureau_only | weak | 229 | 5.7 |
| internal_only | stable | 41 | 1.0 |
| internal_only | weak | 143 | 3.6 |
| neither | none | 3,234 | 81.2 |

Income source x a1_state:

| source | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| both | 1 | 10 | 10 | - |
| bureau | - | 268 | 278 | - |
| internal | 9 | 61 | 114 | - |
| none | - | 23 | 1,433 | 1,778 |

AECB months in W (with carry) x income level:

| months | stable | weak | none |
|---:|---:|---:|---:|
| 0 | 41 | 143 | 3,234 |
| 1 | 46 | 139 | - |
| 2 | 165 | 74 | - |
| 3 | 119 | 24 | - |

AECB in W, window total passes, 25% check fails: 80.

Salary stopped x income source x level:

| source | level | n | % |
|---|---|---:|---:|
| bureau | stable | 51 | 4.5 |
| bureau | weak | 76 | 6.6 |
| none | none | 1,019 | 88.9 |

Salary stopped x a1_state:

| stopped | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 10 | 319 | 1,330 | 1,180 |
| 1 | - | 43 | 505 | 598 |

## 6. Internal salary (>= 1000) history x a1_state

| history | n | % | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 205 | 5.1 | 10 | 71 | 124 | - |
| last_m4-6 | 1,146 | 28.8 | - | 43 | 505 | 598 |
| last_m7-12 | 888 | 22.3 | - | 68 | 401 | 419 |
| last_m13-24 | 528 | 13.2 | - | 62 | 251 | 215 |
| never | 1,218 | 30.6 | - | 118 | 554 | 546 |

## 7. AECB salary (>= 1000) by last pull month, before carry

| last pull | n | % |
|---|---:|---:|
| alert_never_salary | 2,325 | 58.3 |
| in_W | 472 | 11.8 |
| last_m4-6 | 257 | 6.4 |
| last_m7-12 | 229 | 5.7 |
| last_m13-24 | 274 | 6.9 |
| last_m25+ | 284 | 7.1 |
| no_alert_row | 144 | 3.6 |

Internal salary x AECB salary history (n):

| internal \ AECB | alert_never_salary | in_W | last_m4-6 | last_m7-12 | last_m13-24 | last_m25+ | no_alert_row |
|---|---:|---:|---:|---:|---:|---:|---:|
| in_W | 144 | 21 | 1 | 4 | 10 | 19 | 6 |
| last_m4-6 | 736 | 99 | 46 | 41 | 81 | 96 | 47 |
| last_m7-12 | 501 | 109 | 61 | 42 | 59 | 77 | 39 |
| last_m13-24 | 257 | 93 | 48 | 40 | 36 | 40 | 14 |
| never | 687 | 150 | 101 | 102 | 88 | 52 | 38 |

## 8. Liquidity

M5 CASA relationship x a1_state:

| CASA | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| active_casa | 10 | 172 | 1,150 | - |
| dormant_casa | - | 190 | 685 | 1,778 |

(No `no_casa` rows in RL.)

M6 max monthly CASA balance in W x covers max(3000, anchor):

| balance | covers | n | % |
|---|---|---:|---:|
| <1000 | False | 1,410 | 35.4 |
| 1000-3000 | False | 193 | 4.8 |
| >=3,000 | True | 105 | 2.6 |
| >=3,000 | False | 53 | 1.3 |
| none | False | 2,224 | 55.8 |

M6 external card payment in W x liquidity level:

| ext card pay | adequate | weak | none |
|---|---:|---:|---:|
| False | 46 | 291 | 3,609 |
| True | 11 | 14 | 14 |

M6 liquidity level: adequate 57 (1.4%), weak 305 (7.7%), none 3,623 (90.9%).

## 9. Reasons

M7 unknown reason: dormant_casa 1,778 (100%).

M8 low reason:

| reason | n | % |
|---|---:|---:|
| 0pt_active_casa | 649 | 35.4 |
| 1pt | 557 | 30.4 |
| 0pt_distress | 539 | 29.4 |
| 2-3pt_distress | 90 | 4.9 |

M9 moderate/high: state x income x liquidity x distress:

| state | income | liquidity | distress | n | % |
|---|---|---|---:|---:|---:|
| high | stable | adequate | 0 | 10 | 2.7 |
| moderate | none | adequate | 0 | 23 | 6.2 |
| moderate | stable | adequate | 1 | 4 | 1.1 |
| moderate | stable | none | 0 | 273 | 73.4 |
| moderate | stable | weak | 0 | 19 | 5.1 |
| moderate | weak | adequate | 0 | 4 | 1.1 |
| moderate | weak | weak | 0 | 39 | 10.5 |

## 10. Distress

M10 distress parts in W:

| parts | n | % |
|---|---:|---:|
| none | 3,260 | 81.8 |
| bureau | 283 | 7.1 |
| cheque | 189 | 4.7 |
| dds | 184 | 4.6 |
| cheque+dds | 36 | 0.9 |
| cheque+bureau | 28 | 0.7 |
| dds+bureau | 4 | 0.1 |
| cheque+dds+bureau | 1 | 0.0 |

M10 distress parts x a1_state (all distress rows are low or moderate):

| parts | low | moderate |
|---|---:|---:|
| bureau | 283 | - |
| cheque | 189 | - |
| cheque+bureau | 28 | - |
| cheque+dds | 36 | - |
| cheque+dds+bureau | 1 | - |
| dds | 180 | 4 |
| dds+bureau | 4 | - |

## 11. EOSB and anchor

M11 EOSB result in W x a1_state:

| EOSB | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 10 | 360 | 1,830 | 1,773 |
| 1 | - | 2 | 5 | 5 |

M11 EOSB in W x liquidity level: none 6 (50.0%), weak 6 (50.0%).

M11 anchor present: True 3,985 (100%); p10 / p50 / p90 = 1,193 / 2,389 / 8,018.

Anchor raises the income x CASA x card-payment floor (three flags, in the log's order):

| flag 1 | flag 2 | flag 3 | n | % |
|---|---|---|---:|---:|
| False | False | False | 26 | 0.7 |
| False | False | True | 712 | 17.9 |
| True | False | True | 1,724 | 43.3 |
| True | True | True | 1,523 | 38.2 |

## 12. By product: unknown reason and low reason

| product | dormant_casa (unknown) | 0pt_active_casa | 0pt_distress | 1pt | 2-3pt_distress |
|---|---|---|---|---|---|
| Auto | 602 (33.9%) | 148 (8.1%) | 336 (18.3%) | 118 (6.4%) | 34 (1.9%) |
| Personal | 697 (39.2%) | 258 (14.1%) | 83 (4.5%) | 239 (13.0%) | 15 (0.8%) |
| Personal Cash | 479 (26.9%) | 243 (13.2%) | 120 (6.5%) | 200 (10.9%) | 41 (2.2%) |

(Percentages are shares within the unknown reason / low reason totals, per the log.)

## 13. Source depth and CASA legs

Source depth (month_end), base CIFs:

| source | range |
|---|---|
| feat_cif_internal_salary_monthly | 2024-09-30 .. 2026-08-31 |
| feat_cif_bureau_salary_monthly | 2022-11-30 .. 2026-11-30 (all CIFs from 2022-10-31) |
| feat_cif_casa_balance_monthly | 2025-02-28 .. 2026-09-30 |
| feat_cif_casa_activity_monthly | 2025-02-28 .. 2026-10-31 |

CASA legs of base CIFs in W (2026-06-01 .. 2026-08-31):

| lane | legs | CIFs |
|---|---:|---:|
| signal | 23,404 | 388 |
| card_spend | 7,359 | 294 |
| economic | 6,570 | 1,178 |
| wash | 6,163 | 2,379 |
| ambiguous | 3,789 | 1,390 |
| own_loan | 3,163 | 1,207 |
| fee_interest | 964 | 391 |
| card_payment | 479 | 196 |
| group_internal | 386 | 91 |
| refund | 136 | 73 |
| reversal | 112 | 44 |
| unclassified | 2 | 2 |

Top unclassified / ambiguous: ambiguous MISCELLANEOUS 3,788; unclassified POS TRANSACTIONS 2; ambiguous MC/DD-ISSUE 1.

## 14. WM vs FTR (base CIFs, last 12 months)

| WM row | WM positive | FTR leg | FTR customer leg | n | % |
|---|---|---|---|---:|---:|
| False | False | True | False | 76 | 2.1 |
| False | False | True | True | 165 | 4.6 |
| True | False | True | False | 318 | 8.8 |
| True | False | True | True | 139 | 3.9 |
| True | True | True | False | 56 | 1.6 |
| True | True | True | True | 2,854 | 79.1 |

(Every base CIF has an FTR leg.)
