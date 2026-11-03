# A1 ability b12 check — CC (cc_60_180), run 2026-11-03

Pipeline: `crx_cc_a1_ability_b12_check` (dev env). Config: dlq 4-7, collateral WO/SK, horizon 1 month.
Latest month 2026-08-31, base 19,292 accounts / 18,731 CIFs. Run time 1256.1 s. Window W = 2026-06-01 .. 2026-08-31 (3 months).

## 1. New a1_state (2026-08-31, n=19,292)

| state | n | % |
|---|---:|---:|
| high | 46 | 0.2 |
| moderate | 2,798 | 14.5 |
| low | 5,688 | 29.5 |
| unknown | 10,760 | 55.8 |

## 2. Old x new a1_state

Row counts: new 19,292 / old 19,292 / new-only 0 / old-only 0.

| old | new | n | % |
|---|---|---:|---:|
| high | high | 46 | 0.2 |
| high | moderate | 1 | 0.0 |
| moderate | moderate | 2,478 | 12.8 |
| moderate | low | 211 | 1.1 |
| low | low | 5,449 | 28.2 |
| low | moderate | 288 | 1.5 |
| unknown | unknown | 10,760 | 55.8 |
| unknown | low | 28 | 0.1 |
| unknown | moderate | 31 | 0.2 |

Changed rows: 1 + 211 + 288 + 28 + 31 = 559 (2.9%).

## 3. New a1_state share by month (%)

| month | n | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 14,664 | 0.44 | 19.94 | 27.73 | 51.90 |
| 2026-02 | 14,576 | 0.41 | 19.47 | 27.35 | 52.77 |
| 2026-03 | 14,455 | 0.33 | 18.71 | 27.76 | 53.21 |
| 2026-04 | 14,671 | 0.31 | 18.68 | 27.39 | 53.62 |
| 2026-05 | 15,890 | 0.34 | 18.02 | 30.20 | 51.44 |
| 2026-06 | 16,982 | 0.28 | 17.57 | 30.76 | 51.39 |
| 2026-07 | 18,397 | 0.29 | 15.59 | 31.92 | 52.19 |
| 2026-08 | 19,292 | 0.24 | 14.50 | 29.48 | 55.77 |

Range over months (min-max %): high 0.24-0.44; moderate 14.50-19.94; low 27.35-31.92; unknown 51.39-55.77.

## 4. AECB step-wise build (rows per state)

| step | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| s0_no_aecb | 37 | 277 | 4,676 | 14,302 |
| s1_pull_months | 47 | 2,154 | 5,716 | 11,375 |
| s2_one_month_carry | 47 | 2,738 | 5,747 | 10,760 |
| s3_level_check | 46 | 2,798 | 5,688 | 10,760 |

Last step vs output: 0 states, 0 income levels differ.

Moves between steps:

| transition | from | to | n | % of moved |
|---|---|---|---:|---:|
| s0 → s1 (3,207 move) | low | moderate | 270 | 8.4 |
| | moderate | high | 10 | 0.3 |
| | unknown | low | 1,310 | 40.8 |
| | unknown | moderate | 1,617 | 50.4 |
| s1 → s2 (1,299 move) | high | moderate | 1 | 0.1 |
| | low | moderate | 588 | 45.3 |
| | moderate | high | 1 | 0.1 |
| | moderate | low | 94 | 7.2 |
| | unknown | low | 525 | 40.4 |
| | unknown | moderate | 90 | 6.9 |
| s2 → s3 (484 move) | high | moderate | 1 | 0.2 |
| | low | moderate | 271 | 56.0 |
| | moderate | low | 212 | 43.8 |

## 5. Income

M4 income source in W x income level:

| source | level | n | % |
|---|---|---:|---:|
| both | stable | 28 | 0.1 |
| both | weak | 13 | 0.1 |
| bureau_only | stable | 2,778 | 14.4 |
| bureau_only | weak | 1,758 | 9.1 |
| internal_only | stable | 190 | 1.0 |
| internal_only | weak | 209 | 1.1 |
| neither | none | 14,316 | 74.2 |

Income source x a1_state:

| source | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| both | 1 | 21 | 19 | - |
| bureau | 8 | 2,525 | 2,003 | - |
| internal | 37 | 163 | 199 | - |
| none | - | 89 | 3,467 | 10,760 |

AECB months in W (with carry) x income level:

| months | stable | weak | none |
|---:|---:|---:|---:|
| 0 | 190 | 209 | 14,316 |
| 1 | 459 | 941 | - |
| 2 | 1,286 | 554 | - |
| 3 | 1,061 | 276 | - |

AECB in W, window total passes, 25% check fails: 848.

Salary stopped x income source x level:

| source | level | n | % |
|---|---|---:|---:|
| bureau | stable | 213 | 6.9 |
| bureau | weak | 208 | 6.7 |
| none | none | 2,673 | 86.4 |

Salary stopped x a1_state:

| stopped | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 46 | 2,610 | 4,424 | 9,118 |
| 1 | - | 188 | 1,264 | 1,642 |

## 6. Internal salary (>= 1000) history x a1_state

| history | n | % | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 440 | 2.3 | 38 | 184 | 218 | - |
| last_m4-6 | 3,094 | 16.0 | - | 188 | 1,264 | 1,642 |
| last_m7-12 | 3,599 | 18.7 | 3 | 282 | 1,192 | 2,122 |
| last_m13-24 | 1,941 | 10.1 | - | 199 | 669 | 1,073 |
| never | 10,218 | 53.0 | 5 | 1,945 | 2,345 | 5,923 |

## 7. AECB salary (>= 1000) by last pull month, before carry

| last pull | n | % |
|---|---:|---:|
| alert_never_salary | 7,693 | 39.9 |
| in_W | 3,820 | 19.8 |
| last_m4-6 | 2,319 | 12.0 |
| last_m7-12 | 2,077 | 10.8 |
| last_m13-24 | 1,346 | 7.0 |
| last_m25+ | 899 | 4.7 |
| no_alert_row | 1,138 | 5.9 |

Internal salary x AECB salary history (n):

| internal \ AECB | alert_never_salary | in_W | last_m4-6 | last_m7-12 | last_m13-24 | last_m25+ | no_alert_row |
|---|---:|---:|---:|---:|---:|---:|---:|
| in_W | 283 | 37 | 15 | 14 | 31 | 48 | 12 |
| last_m4-6 | 2,007 | 356 | 120 | 88 | 130 | 167 | 226 |
| last_m7-12 | 2,091 | 443 | 264 | 196 | 155 | 154 | 296 |
| last_m13-24 | 961 | 280 | 163 | 186 | 120 | 92 | 139 |
| never | 2,351 | 2,704 | 1,757 | 1,593 | 910 | 438 | 465 |

## 8. Liquidity

M5 CASA relationship x a1_state:

| CASA | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| active_casa | 45 | 549 | 3,037 | - |
| dormant_casa | 1 | 841 | 1,567 | 6,716 |
| no_casa | - | 1,408 | 1,084 | 4,044 |

M6 max monthly CASA balance in W x covers max(3000, anchor):

| balance | covers | n | % |
|---|---|---:|---:|
| <1000 | False | 4,775 | 24.8 |
| 1000-3000 | False | 254 | 1.3 |
| >=3,000 | True | 230 | 1.2 |
| >=3,000 | False | 12 | 0.1 |
| none | False | 14,021 | 72.7 |

M6 external card payment in W x liquidity level:

| ext card pay | adequate | weak | none |
|---|---:|---:|---:|
| False | 142 | 327 | 18,705 |
| True | 54 | 15 | 49 |

M6 liquidity level: adequate 196 (1.0%), weak 342 (1.8%), none 18,754 (97.2%).

## 9. Reasons

M7 unknown reason: dormant_casa 6,716 (62.4%); no_casa 4,044 (37.6%).

M8 low reason:

| reason | n | % |
|---|---:|---:|
| 1pt | 2,164 | 38.0 |
| 0pt_active_casa | 2,049 | 36.0 |
| 0pt_distress | 1,153 | 20.3 |
| 2-3pt_distress | 322 | 5.7 |

M9 moderate/high: state x income x liquidity x distress:

| state | income | liquidity | distress | n | % |
|---|---|---|---:|---:|---:|
| high | stable | adequate | 0 | 46 | 1.6 |
| moderate | none | adequate | 0 | 89 | 3.1 |
| moderate | stable | adequate | 1 | 16 | 0.6 |
| moderate | stable | none | 0 | 2,597 | 91.3 |
| moderate | stable | weak | 0 | 46 | 1.6 |
| moderate | weak | adequate | 0 | 21 | 0.7 |
| moderate | weak | weak | 0 | 29 | 1.0 |

## 10. Distress

M10 distress parts in W:

| parts | n | % |
|---|---:|---:|
| none | 17,609 | 91.3 |
| dds | 596 | 3.1 |
| bureau | 490 | 2.5 |
| cheque | 449 | 2.3 |
| cheque+dds | 109 | 0.6 |
| dds+bureau | 21 | 0.1 |
| cheque+bureau | 17 | 0.1 |
| cheque+dds+bureau | 1 | 0.0 |

M10 distress parts x a1_state (all distress rows are low or moderate):

| parts | low | moderate |
|---|---:|---:|
| bureau | 487 | 3 |
| cheque | 446 | 3 |
| cheque+bureau | 17 | - |
| cheque+dds | 108 | 1 |
| cheque+dds+bureau | 1 | - |
| dds | 587 | 9 |
| dds+bureau | 21 | - |

## 11. EOSB and anchor

M11 EOSB result in W x a1_state:

| EOSB | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 46 | 2,795 | 5,672 | 10,754 |
| 1 | - | 3 | 16 | 6 |

M11 EOSB in W x liquidity level: none 23 (92.0%), adequate 1 (4.0%), weak 1 (4.0%).

M11 anchor present: True 19,292 (100%); p10 / p50 / p90 = 128.34 / 837.14 / 2,342.33.

Anchor raises the income x CASA x card-payment floor (three flags, in the log's order):

| flag 1 | flag 2 | flag 3 | n | % |
|---|---|---|---:|---:|
| False | False | False | 5,300 | 27.5 |
| False | False | True | 9,437 | 48.9 |
| True | False | True | 3,490 | 18.1 |
| True | True | True | 1,065 | 5.5 |

## 12. Source depth and CASA legs

Source depth (month_end), base CIFs:

| source | range |
|---|---|
| feat_cif_internal_salary_monthly | 2024-09-30 .. 2026-08-31 |
| feat_cif_bureau_salary_monthly | 2022-10-31 .. 2026-11-30 |
| feat_cif_casa_balance_monthly | 2025-02-28 .. 2026-09-30 |
| feat_cif_casa_activity_monthly | 2025-02-28 .. 2026-10-31 |

CASA legs of base CIFs in W (2026-06-01 .. 2026-08-31):

| lane | legs | CIFs |
|---|---:|---:|
| signal | 101,967 | 1,150 |
| card_spend | 25,724 | 1,062 |
| economic | 18,144 | 2,708 |
| wash | 7,107 | 2,258 |
| ambiguous | 5,223 | 2,440 |
| fee_interest | 3,893 | 1,360 |
| own_loan | 2,054 | 750 |
| card_payment | 1,889 | 1,374 |
| group_internal | 859 | 238 |
| refund | 387 | 198 |
| reversal | 293 | 129 |
| unclassified | 39 | 3 |

Top unclassified / ambiguous: ambiguous MISCELLANEOUS 5,221; unclassified POS TRANSACTIONS 39; ambiguous MC/DD-ISSUE 2.

## 13. WM vs FTR (base CIFs, last 12 months)

| WM row | WM positive | FTR leg | FTR customer leg | n | % |
|---|---|---|---|---:|---:|
| False | False | False | False | 338 | 1.8 |
| False | False | True | False | 15 | 0.1 |
| False | False | True | True | 504 | 2.7 |
| True | False | False | False | 6,031 | 32.2 |
| True | False | True | False | 258 | 1.4 |
| True | False | True | True | 844 | 4.5 |
| True | True | False | False | 103 | 0.5 |
| True | True | True | False | 110 | 0.6 |
