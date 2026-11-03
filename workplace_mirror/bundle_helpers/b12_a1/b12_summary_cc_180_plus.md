# A1 ability b12 check — CC (cc_180_plus), run 2026-11-03

Pipeline: `crx_cc_a1_ability_b12_check` (dev env). Latest month 2026-08-31, base 318,663 accounts / 299,026 CIFs. Run time 1090.9 s.

## 1. New a1_state (2026-08-31, n=318,663)

| state | n | % |
|---|---:|---:|
| high | 111 | 0.0 |
| moderate | 19,907 | 6.2 |
| low | 19,991 | 6.3 |
| unknown | 278,654 | 87.4 |

## 2. Old x new a1_state

Row counts: new 318,663 / old 318,663 / new-only 0 / old-only 0.

| old | new | n | % |
|---|---|---:|---:|
| high | high | 108 | 0.0 |
| moderate | high | 3 | 0.0 |
| moderate | moderate | 17,672 | 5.5 |
| moderate | low | 1,538 | 0.5 |
| low | moderate | 2,235 | 0.7 |
| low | low | 18,453 | 5.8 |
| unknown | unknown | 278,654 | 87.4 |

Changed rows: 3 + 1,538 + 2,235 = 3,776 (1.2%).

## 3. New a1_state share by month (%)

| month | n | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|
| 2026-01 | 305,257 | 0.03 | 6.19 | 6.51 | 87.27 |
| 2026-02 | 306,854 | 0.02 | 6.22 | 6.53 | 87.23 |
| 2026-03 | 308,742 | 0.03 | 6.29 | 6.46 | 87.22 |
| 2026-04 | 310,709 | 0.03 | 6.35 | 6.43 | 87.20 |
| 2026-05 | 312,626 | 0.03 | 6.35 | 6.36 | 87.26 |
| 2026-06 | 314,827 | 0.03 | 6.43 | 6.03 | 87.50 |
| 2026-07 | 316,738 | 0.03 | 6.33 | 6.34 | 87.30 |
| 2026-08 | 318,663 | 0.03 | 6.25 | 6.27 | 87.44 |

Range over months (min-max %): high 0.02-0.03; moderate 6.19-6.43; low 6.03-6.53; unknown 87.20-87.50.

## 4. AECB step-wise build (rows per state)

| step | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| s0_no_aecb | 64 | 836 | 12,148 | 305,615 |
| s1_pull_months | 100 | 15,630 | 22,739 | 280,194 |
| s2_one_month_carry | 108 | 19,213 | 20,688 | 278,654 |
| s3_level_check | 111 | 19,907 | 19,991 | 278,654 |

Last step vs output: 0 states, 0 income levels differ.

Moves between steps:

| transition | from | to | n | % of moved |
|---|---|---|---:|---:|
| s0 → s1 (26,217 move) | low | moderate | 756 | 2.9 |
| | moderate | high | 36 | 0.1 |
| | moderate | low | 4 | 0.0 |
| | unknown | low | 11,343 | 43.3 |
| | unknown | moderate | 14,078 | 53.7 |
| s1 → s2 (6,409 move) | low | moderate | 4,165 | 65.0 |
| | moderate | high | 8 | 0.1 |
| | moderate | low | 696 | 10.9 |
| | unknown | low | 1,418 | 22.1 |
| | unknown | moderate | 122 | 1.9 |
| s2 → s3 (3,776 move) | low | moderate | 2,235 | 59.2 |
| | moderate | high | 3 | 0.1 |
| | moderate | low | 1,538 | 40.7 |

## 5. Income

M4 income source in W x income level:

| source | level | n | % |
|---|---|---:|---:|
| both | stable | 75 | 0.0 |
| both | weak | 27 | 0.0 |
| bureau_only | stable | 20,827 | 6.5 |
| bureau_only | weak | 10,096 | 3.2 |
| internal_only | stable | 335 | 0.1 |
| internal_only | weak | 176 | 0.1 |
| neither | none | 287,127 | 90.1 |

Income source x a1_state:

| source | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| both | 6 | 59 | 37 | - |
| bureau | 44 | 19,113 | 11,766 | - |
| internal | 61 | 299 | 151 | - |
| none | - | 436 | 8,037 | 278,654 |

AECB months in W (with carry) x income level:

| months | stable | weak | none |
|---:|---:|---:|---:|
| 0 | 335 | 176 | 287,127 |
| 1 | 807 | 2,978 | - |
| 2 | 4,495 | 3,651 | - |
| 3 | 4,325 | 1,502 | - |
| 4 | 4,894 | 1,077 | - |
| 5 | 3,557 | 582 | - |
| 6 | 2,824 | 333 | - |

AECB in W, window total passes, 25% check fails: 4,691.

Salary stopped x income source x level:

| source | level | n | % |
|---|---|---:|---:|
| bureau | stable | 345 | 10.9 |
| bureau | weak | 347 | 10.9 |
| none | none | 2,480 | 78.2 |

Salary stopped x a1_state:

| stopped | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 108 | 19,599 | 19,014 | 276,770 |
| 1 | 3 | 308 | 977 | 1,884 |

## 6. Internal salary (>= 1000) history x a1_state

| history | n | % | high | moderate | low | unknown |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 613 | 0.2 | 67 | 358 | 188 | - |
| last_m7-12 | 3,172 | 1.0 | 3 | 308 | 977 | 1,884 |
| last_m13-24 | 11,280 | 3.5 | 10 | 1,234 | 2,578 | 7,458 |
| never | 303,598 | 95.3 | 31 | 18,007 | 16,248 | 269,312 |

## 7. AECB salary (>= 1000) by last pull month, before carry

| last pull | n | % |
|---|---:|---:|
| alert_never_salary | 150,930 | 47.4 |
| in_W | 29,248 | 9.2 |
| last_m7-12 | 9,812 | 3.1 |
| last_m13-24 | 12,432 | 3.9 |
| last_m25+ | 27,234 | 8.5 |
| no_alert_row | 89,007 | 27.9 |

Internal salary x AECB salary history (n):

| internal \ AECB | alert_never_salary | in_W | last_m7-12 | last_m13-24 | last_m25+ | no_alert_row |
|---|---:|---:|---:|---:|---:|---:|
| in_W | 346 | 97 | 30 | 47 | 80 | 13 |
| last_m7-12 | 1,775 | 637 | 237 | 146 | 154 | 223 |
| last_m13-24 | 6,054 | 2,012 | 838 | 918 | 724 | 734 |
| never | 142,755 | 26,502 | 8,707 | 11,321 | 26,276 | 88,037 |

## 8. Liquidity

M5 CASA relationship x a1_state:

| CASA | high | moderate | low | unknown |
|---|---:|---:|---:|---:|
| active_casa | 89 | 1,329 | 3,326 | - |
| dormant_casa | 22 | 4,049 | 6,686 | 38,743 |
| no_casa | - | 14,529 | 9,979 | 239,911 |

M6 max monthly CASA balance in W x covers max(3000, anchor):

| balance | covers | n | % |
|---|---|---:|---:|
| <1000 | False | 23,929 | 7.5 |
| 1000-3000 | False | 596 | 0.2 |
| >=3,000 | True | 776 | 0.2 |
| none | False | 293,362 | 92.1 |

M6 external card payment in W x liquidity level:

| ext card pay | adequate | weak | none |
|---|---:|---:|---:|
| False | 583 | 760 | 317,226 |
| True | 72 | 3 | 19 |

M6 liquidity level: adequate 655 (0.2%), weak 763 (0.2%), none 317,245 (99.6%) *(sums to 318,663)*.

## 9. Reasons

M7 unknown reason: dormant_casa 38,743 (13.9%); no_casa 239,911 (86.1%).

M8 low reason:

| reason | n | % |
|---|---:|---:|
| 0pt_active_casa | 1,937 | 9.7 |
| 0pt_distress | 5,560 | 27.8 |
| 1pt | 10,672 | 53.4 |
| 2-3pt_distress | 1,822 | 9.1 |

M9 moderate/high: state x income x liquidity x distress:

| state | income | liquidity | distress | n | % |
|---|---|---|---:|---:|---:|
| high | stable | adequate | 0 | 111 | 0.6 |
| moderate | none | adequate | 0 | 436 | 2.2 |
| moderate | stable | adequate | 1 | 22 | 0.1 |
| moderate | stable | none | 0 | 19,197 | 95.9 |
| moderate | stable | weak | 0 | 156 | 0.8 |
| moderate | weak | adequate | 0 | 30 | 0.1 |
| moderate | weak | weak | 0 | 66 | 0.3 |

## 10. Distress

M10 distress parts in W:

| parts | n | % |
|---|---:|---:|
| none | 310,349 | 97.4 |
| bureau | 4,104 | 1.3 |
| dds | 2,558 | 0.8 |
| cheque | 1,310 | 0.4 |
| cheque+dds | 147 | 0.0 |
| cheque+bureau | 103 | 0.0 |
| dds+bureau | 77 | 0.0 |
| cheque+dds+bureau | 15 | 0.0 |

M10 distress parts x a1_state (all distress rows are low or moderate):

| parts | low | moderate |
|---|---:|---:|
| bureau | 4,098 | 6 |
| cheque | 1,305 | 5 |
| cheque+bureau | 102 | 1 |
| cheque+dds | 146 | 1 |
| cheque+dds+bureau | 15 | - |
| dds | 2,549 | 9 |
| dds+bureau | 77 | - |

## 11. EOSB and anchor

M11 EOSB result in W x a1_state:

| EOSB | high | moderate | low | unknown |
|---:|---:|---:|---:|---:|
| 0 | 111 | 19,903 | 19,987 | 278,644 |
| 1 | - | 4 | 4 | 10 |

M11 EOSB in W x liquidity level: none 16 (88.9%), weak 2 (11.1%).

M11 anchor present: False 318,663 (100%); p10/p50/p90 = None. Anchor raises income x CASA x card-payment floor: False for all 318,663.

## 12. Source depth and CASA legs

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
| signal | 807,809 | 3,974 |
| card_spend | 139,304 | 1,622 |
| economic | 85,901 | 4,318 |
| fee_interest | 47,154 | 9,763 |
| wash | 29,495 | 4,829 |
| ambiguous | 12,925 | 5,036 |
| own_loan | 4,450 | 966 |
| group_internal | 3,312 | 500 |
| reversal | 2,975 | 1,247 |
| card_payment | 1,615 | 442 |
| refund | 1,308 | 443 |
| unclassified | 29 | 25 |

Top unclassified / ambiguous: ambiguous MISCELLANEOUS 12,920; unclassified POS TRANSACTIONS 28; ambiguous MC/DD-ISSUE 5; unclassified TRADE FINANCE 1.

## 13. WM vs FTR (base CIFs, last 12 months)

| WM row | WM positive | FTR leg | FTR customer leg | n | % |
|---|---|---|---|---:|---:|
| False | False | False | False | 6,798 | 2.3 |
| False | False | True | False | 316 | 0.1 |
| False | False | True | True | 610 | 0.2 |
| True | False | False | False | 239,314 | 80.0 |
| True | False | True | False | 18,688 | 6.2 |
| True | False | True | True | 1,864 | 0.6 |
| True | True | False | False | 11,868 | 4.0 |
| True | True | True | False | 8,112 | 2.7 |
| True | True | True | True | 11,456 | 3.8 |
