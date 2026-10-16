# DPD deterioration states — synthetic validation 20261016_091847

20,000 calibrated synthetic spine accounts (current bucket 4–7). Strings: leftmost = current bucket. 0 ≡ 1.

## A. Is the synthetic spine life-like?

| check | your book | synthetic |
|---|---|---|
| Monthly roll rate at 4 | 70% | 71% |
| Monthly roll rate at 5 | 80% | 78% |
| Monthly roll rate at 6 | 90% | 89% |
| Monthly roll rate at 7 | 95% | 94% |
| One spell only (spell from bucket 3) | ~85% | 83% |
| One spell only (spell from bucket 4) | ~85% | 95% |
| EPD ('bust-out') share | 6% | 5.7% |
| Stabilized share (your 5/6 rule, after EPD) | 6% | 6.8% |
| Stabilized share incl. long-run clause | — | 7.7% |
| Never paid since reaching 4 | majority (90% 'overkill') | 59% |

Current bucket mix:

| b_now | share |
|---|---|
| 4 | 29% |
| 5 | 26% |
| 6 | 23% |
| 7 | 22% |

Months of history before the current spell (continuous — no planted gaps):

| months_before_spell | share |
|---|---|
| 0-3 | 6% |
| 4-6 | 2% |
| 7-12 | 4% |
| 13-24 | 13% |
| 25-36 | 14% |
| 37-60 | 25% |
| 61-120 | 30% |
| 121+ | 8% |

| data-quality effect | share |
|---|---|
| accounts with a payment holiday in history | 1.9% |
| accounts with a +2 jump repaired (next to a hold) | 2.4% |
| accounts with a +2 jump left (read as roll) | 0.3% |

## B. State options — each a MECE tree (first 'yes' wins)

Shared thresholds: `{'epd_max_history': 3, 'epd_max_blips': 1, 'straight_max_runup': 3, 'stabilized_min_in_band': 5, 'stabilized_long_run_months': 6, 'stabilized_long_run_max_rise': 1, 'paying_since_4_min_rate': None, 'repeat_min_prior_peak': None, 'seasoned_min_months': None, 'split_slow_roller': False}`

### A_minimal_4 — 4 states (extra switches: `{}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.06 | 0.88 | 0.99 | 1.00 | 0.22 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| straight_roller | 0.70 | 0.85 | 0.94 | 0.98 | 0.26 | 0.24 |
| slow_roller | 0.17 | 0.84 | 0.93 | 0.98 | 0.56 | 0.09 |

### B_balanced_6 — 6 states (extra switches: `{'repeat_min_prior_peak': 3, 'seasoned_min_months': 12}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.06 | 0.88 | 0.99 | 1.00 | 0.22 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| repeat_delinquent | 0.16 | 0.85 | 0.94 | 0.99 | 0.26 | 1.00 |
| straight_roller_seasoned | 0.52 | 0.84 | 0.94 | 0.98 | 0.26 | 0.04 |
| straight_roller_early_life | 0.03 | 0.84 | 0.94 | 0.98 | 0.30 | 0.01 |
| slow_roller | 0.15 | 0.85 | 0.94 | 0.98 | 0.56 | 0.00 |

### C_detailed_7 — 7 states (extra switches: `{'repeat_min_prior_peak': 3, 'seasoned_min_months': 12, 'split_slow_roller': True}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.06 | 0.88 | 0.99 | 1.00 | 0.22 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| repeat_delinquent | 0.16 | 0.85 | 0.94 | 0.99 | 0.26 | 1.00 |
| straight_roller_seasoned | 0.52 | 0.84 | 0.94 | 0.98 | 0.26 | 0.04 |
| straight_roller_early_life | 0.03 | 0.84 | 0.94 | 0.98 | 0.30 | 0.01 |
| slow_roller_intermittent | 0.09 | 0.84 | 0.94 | 0.97 | 0.61 | 0.01 |
| slow_roller_erratic | 0.06 | 0.85 | 0.95 | 0.99 | 0.47 | 0.00 |

Option C — state mix by current bucket:

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.05 | 0.06 | 0.06 | 0.06 |
| repeat_delinquent | 0.15 | 0.15 | 0.17 | 0.18 |
| slow_roller_erratic | 0.05 | 0.06 | 0.06 | 0.06 |
| slow_roller_intermittent | 0.08 | 0.09 | 0.10 | 0.11 |
| stabilized | 0.15 | 0.09 | 0.04 | 0.01 |
| straight_roller_early_life | 0.03 | 0.03 | 0.04 | 0.03 |
| straight_roller_seasoned | 0.48 | 0.52 | 0.54 | 0.55 |

Option C — planted pattern → state (row share):

| true_archetype | early_payment_default | repeat_delinquent | slow_roller_erratic | slow_roller_intermittent | stabilized | straight_roller_early_life | straight_roller_seasoned |
|---|---|---|---|---|---|---|---|
| bust_out | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| clean_abrupt_shock | 0.01 | 0.00 | 0.00 | 0.00 | 0.02 | 0.06 | 0.91 |
| dip_and_roll | 0.00 | 0.00 | 0.43 | 0.00 | 0.06 | 0.03 | 0.47 |
| oscillating_payer | 0.00 | 0.00 | 0.00 | 0.00 | 0.64 | 0.03 | 0.34 |
| repeat_episodes | 0.00 | 0.69 | 0.00 | 0.02 | 0.02 | 0.01 | 0.26 |
| slow_slide | 0.00 | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 |
| stabilized | 0.00 | 0.00 | 0.00 | 0.01 | 0.68 | 0.03 | 0.28 |
| staircase | 0.00 | 0.00 | 0.00 | 0.28 | 0.72 | 0.00 | 0.00 |
| volatile | 0.00 | 0.39 | 0.08 | 0.06 | 0.20 | 0.02 | 0.25 |

Option C — examples (last 30 months, oldest → newest):

| state_c | oldest_to_newest |
|---|---|
| early_payment_default | 0202355 |
| early_payment_default | 0234567 |
| early_payment_default | 0002345456 |
| repeat_delinquent | 100002342333423333342311234567 |
| repeat_delinquent | 200000000000000000023330010234 |
| repeat_delinquent | 220000000223300001010000023445 |
| slow_roller_erratic | 000100000020000000010000232345 |
| slow_roller_erratic | 100000000000000000001002323455 |
| slow_roller_erratic | 000000000000000000000023234567 |
| slow_roller_intermittent | 00010010010000023345667 |
| slow_roller_intermittent | 000000000010010000000000023344 |
| slow_roller_intermittent | 200000200000020200200000002234 |
| stabilized | 000000000000011000000002345455 |
| stabilized | 000001000000234456555666565665 |
| stabilized | 000000000000000233123234343434 |
| straight_roller_early_life | 00000000234567 |
| straight_roller_early_life | 00000234 |
| straight_roller_early_life | 00002345 |
| straight_roller_seasoned | 100000000020000000000000023456 |
| straight_roller_seasoned | 000000000000000000000023434556 |
| straight_roller_seasoned | 100000000000000000000000001234 |

## C. Clustering the residual (after EPD and stabilized)

Residual = 87% of the spine. Agreement (ARI) between k-means clusters and each option's residual states:

| k | silhouette | bootstrap_ARI | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|---|---|
| 2 | 0.34 | 1.00 | -0.07 | 0.44 | 0.42 |
| 3 | 0.37 | 1.00 | 0.29 | 0.63 | 0.64 |
| 4 | 0.34 | 1.00 | 0.18 | 0.45 | 0.46 |
| 5 | 0.37 | 0.87 | 0.30 | 0.55 | 0.58 |
| 6 | 0.30 | 0.98 | 0.11 | 0.30 | 0.32 |
| 7 | 0.32 | 0.72 | 0.17 | 0.37 | 0.39 |
| 8 | 0.34 | 0.99 | 0.15 | 0.34 | 0.36 |

k = 6 cluster profiles:

| c | share_of_spine | median_months_before_spell | earlier_spell_to_3+ | straight_runup | held_on_way | paid_2+_on_way | median_paid_rate_since_4 | top_state_option_C |
|---|---|---|---|---|---|---|---|---|
| 0 | 0.26 | 71.00 | 0.00 | 0.90 | 0.10 | 0.00 | 0.00 | straight_roller_seasoned |
| 3 | 0.20 | 24.00 | 0.00 | 0.89 | 0.11 | 0.00 | 0.00 | straight_roller_seasoned |
| 1 | 0.17 | 63.00 | 0.89 | 0.96 | 0.03 | 0.00 | 0.00 | repeat_delinquent |
| 5 | 0.14 | 47.00 | 0.02 | 0.89 | 0.11 | 0.00 | 0.67 | straight_roller_seasoned |
| 2 | 0.06 | 49.00 | 0.10 | 0.00 | 0.28 | 1.00 | 0.00 | slow_roller_erratic |
| 4 | 0.03 | 46.00 | 0.05 | 0.00 | 1.00 | 0.02 | 0.00 | slow_roller_intermittent |

## D. Threshold sweeps (one parameter at a time, others at default)

### Q1 early payment default (EPD) — months of history before the spell

| epd_max_history | epd_share | exit_6m | planted_bustouts_caught | share_of_state_planted_bustout |
|---|---|---|---|---|
| 2 | 0.02 | 0.98 | 0.48 | 1.00 |
| 3 | 0.06 | 0.99 | 1.00 | 0.92 |
| 4 | 0.06 | 0.99 | 1.00 | 0.88 |
| 6 | 0.07 | 0.97 | 1.00 | 0.77 |
| 9 | 0.08 | 0.96 | 1.00 | 0.64 |
| 12 | 0.10 | 0.95 | 1.00 | 0.53 |

### Q2 stabilized — months within today's bucket ±1 (of the last 6)

| min_in_band (of 6) | stabilized_share | roll_next_month | exit_6m | still_stabilized_next_month | payment_holiday_share | planted_stabilizers_caught |
|---|---|---|---|---|---|---|
| 4 | 0.14 | 0.58 | 0.66 | 0.55 | 0.05 | 0.73 |
| 5 | 0.08 | 0.49 | 0.57 | 0.61 | 0.08 | 0.68 |
| 6 | 0.05 | 0.45 | 0.51 | 0.66 | 0.08 | 0.64 |

### Q3 paying since 4 (tested, not recommended) — months paid per month since 4

| paying_since_4_min_rate | share | roll_next_month | still_paying_since_4_next_month | paid_in_last_3m | stability_of_other_states |
|---|---|---|---|---|---|
| 0.34 | 0.20 | 0.83 | 0.74 | 0.76 | 0.91 |
| 0.50 | 0.18 | 0.82 | 0.62 | 0.79 | 0.91 |
| 0.67 | 0.07 | 0.79 | 0.32 | 0.79 | 0.96 |

### Q4 repeat delinquent — how deep the earlier spell must have gone

| earlier spell reached bucket | repeat_share |
|---|---|
| 2 | 0.18 |
| 3 | 0.16 |
| 4 | 0.05 |

### Q5 straight vs slow roller — max run-up months

| straight_max_runup | straight_share | slow_share | slow_slides_in_slow_roller | abrupt_in_straight |
|---|---|---|---|---|
| 3 | 0.70 | 0.17 | 0.98 | 0.97 |
| 4 | 0.77 | 0.10 | 0.30 | 0.97 |
| 5 | 0.84 | 0.03 | 0.01 | 0.97 |

### Q5 split — months of history before the spell (seasoned vs early-life straight roller)

| seasoned_min_months | seasoned | early_life |
|---|---|---|
| 12 | 0.52 | 0.03 |
| 18 | 0.48 | 0.07 |
| 24 | 0.44 | 0.11 |
| 36 | 0.35 | 0.20 |

## E. Discovery views (states = B_balanced_6)

### Top 15 shapes (5993 distinct) — by state

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3808 | straight_roller_seasoned | 1.00 | 0.19 | 0.19 |
| N13-24 R3+ | 823 | straight_roller_seasoned | 1.00 | 0.04 | 0.23 |
| N25+ R3+ H1 | 362 | straight_roller_seasoned | 1.00 | 0.02 | 0.25 |
| N7-12 R3+ | 336 | straight_roller_early_life | 0.68 | 0.02 | 0.27 |
| N2-3 R3+ | 275 | early_payment_default | 0.87 | 0.01 | 0.28 |
| N25+ R3+ H1 R1 | 247 | straight_roller_seasoned | 1.00 | 0.01 | 0.29 |
| R1 P1 R3+ | 234 | early_payment_default | 1.00 | 0.01 | 0.30 |
| N25+ R2 P1 R3+ | 217 | slow_roller | 0.93 | 0.01 | 0.32 |
| N1 R3+ | 204 | early_payment_default | 1.00 | 0.01 | 0.33 |
| R3+ | 188 | early_payment_default | 1.00 | 0.01 | 0.33 |
| N25+ R3+ P1 R3+ | 182 | straight_roller_seasoned | 1.00 | 0.01 | 0.34 |
| N25+ R3+ H1 R2 | 176 | straight_roller_seasoned | 1.00 | 0.01 | 0.35 |
| N25+ R1 H1 R3+ | 170 | slow_roller | 1.00 | 0.01 | 0.36 |
| N25+ R3+ P1 R1 | 165 | straight_roller_seasoned | 1.00 | 0.01 | 0.37 |
| N4-6 R3+ | 114 | straight_roller_early_life | 1.00 | 0.01 | 0.38 |

### 4-grams ranked by lift vs shuffled order (support ≥ 1%)

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| HHPP | 0.02 | 92.80 | repeat_delinquent | 0.93 |
| RHHP | 0.09 | 71.04 | repeat_delinquent | 0.71 |
| HRHP | 0.03 | 38.87 | repeat_delinquent | 0.87 |
| RHPP | 0.02 | 32.29 | repeat_delinquent | 0.92 |
| HHPN | 0.07 | 27.07 | repeat_delinquent | 0.70 |
| RHRH | 0.10 | 26.59 | repeat_delinquent | 0.51 |
| RRHH | 0.07 | 22.21 | repeat_delinquent | 0.44 |
| RPRP | 0.10 | 20.62 | repeat_delinquent | 0.35 |
| RRRH | 0.19 | 20.33 | straight_roller_seasoned | 0.53 |
| RRHP | 0.04 | 19.52 | repeat_delinquent | 0.75 |
| HPPN | 0.04 | 19.45 | repeat_delinquent | 0.99 |
| RHRP | 0.05 | 18.25 | repeat_delinquent | 0.66 |
| RRPH | 0.05 | 17.24 | slow_roller | 0.30 |
| RPHR | 0.04 | 16.70 | slow_roller | 0.35 |
| PRHP | 0.01 | 16.36 | repeat_delinquent | 0.56 |
| RRHR | 0.15 | 16.15 | straight_roller_seasoned | 0.36 |
| HRPP | 0.02 | 15.52 | repeat_delinquent | 0.77 |
| HRHH | 0.05 | 14.30 | repeat_delinquent | 0.49 |
| RHHH | 0.04 | 13.66 | stabilized | 0.67 |
| HRHR | 0.05 | 13.47 | slow_roller | 0.65 |

### k-means on clock-safe features

| k | silhouette | bootstrap_ARI | ARI_vs_planted | ARI_vs_states |
|---|---|---|---|---|
| 4 | 0.316 | 0.988 | 0.386 | 0.437 |
| 5 | 0.338 | 0.674 | 0.383 | 0.421 |
| 6 | 0.284 | 0.991 | 0.374 | 0.492 |
| 7 | 0.279 | 0.599 | 0.389 | 0.474 |
| 8 | 0.292 | 0.786 | 0.365 | 0.438 |
