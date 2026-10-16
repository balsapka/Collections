# DPD deterioration states — synthetic validation 20261016_112955

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
| EPD ('bust-out') share | 6% | 4.3% |
| Stabilized share (your 5/6 rule, after EPD) | 6% | 6.9% |
| Stabilized share incl. long-run clause | — | 7.8% |
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
| accounts with a +2 jump repaired (next to a hold) | 1.9% |
| accounts with a +2 jump left (read as roll) | 0.7% |

## B. State options — each a MECE tree (first 'yes' wins)

Shared thresholds: `{'epd_max_history': 3, 'epd_max_blips': 1, 'straight_max_runup': 3, 'stabilized_min_in_band': 5, 'stabilized_long_run_months': 6, 'stabilized_long_run_max_rise': 1, 'paying_since_4_min_rate': None, 'repeat_min_prior_peak': None, 'repeat_window_months': 24, 'seasoned_min_months': None, 'split_slow_roller': False}`

### A_minimal_4 — 4 states (extra switches: `{}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.04 | 0.87 | 0.99 | 0.84 | 0.00 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| straight_roller | 0.71 | 0.85 | 0.94 | 0.98 | 0.27 | 0.24 |
| slow_roller | 0.17 | 0.83 | 0.93 | 0.98 | 0.56 | 0.09 |

### B_balanced_6 — 6 states (extra switches: `{'repeat_min_prior_peak': 3, 'seasoned_min_months': 12}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.04 | 0.87 | 0.99 | 0.84 | 0.00 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| repeat_delinquent | 0.15 | 0.85 | 0.93 | 0.99 | 0.27 | 1.00 |
| straight_roller_seasoned | 0.53 | 0.85 | 0.94 | 0.98 | 0.26 | 0.07 |
| straight_roller_early_life | 0.05 | 0.85 | 0.95 | 0.97 | 0.48 | 0.01 |
| slow_roller | 0.15 | 0.85 | 0.94 | 0.98 | 0.56 | 0.00 |

### C_detailed_7 — 7 states (extra switches: `{'repeat_min_prior_peak': 3, 'seasoned_min_months': 12, 'split_slow_roller': True}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| early_payment_default | 0.04 | 0.87 | 0.99 | 0.84 | 0.00 | 0.00 |
| stabilized | 0.08 | 0.49 | 0.57 | 0.61 | 0.98 | 0.14 |
| repeat_delinquent | 0.15 | 0.85 | 0.93 | 0.99 | 0.27 | 1.00 |
| straight_roller_seasoned | 0.53 | 0.85 | 0.94 | 0.98 | 0.26 | 0.07 |
| straight_roller_early_life | 0.05 | 0.85 | 0.95 | 0.97 | 0.48 | 0.01 |
| slow_roller_intermittent | 0.09 | 0.84 | 0.94 | 0.97 | 0.62 | 0.01 |
| slow_roller_erratic | 0.06 | 0.85 | 0.95 | 0.99 | 0.47 | 0.00 |

Option C — state mix by current bucket:

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.04 | 0.04 | 0.04 | 0.04 |
| repeat_delinquent | 0.14 | 0.14 | 0.16 | 0.16 |
| slow_roller_erratic | 0.05 | 0.06 | 0.06 | 0.06 |
| slow_roller_intermittent | 0.08 | 0.09 | 0.09 | 0.11 |
| stabilized | 0.15 | 0.09 | 0.04 | 0.01 |
| straight_roller_early_life | 0.04 | 0.05 | 0.06 | 0.05 |
| straight_roller_seasoned | 0.50 | 0.53 | 0.55 | 0.57 |

Option C — planted pattern → state (row share):

| true_archetype | early_payment_default | repeat_delinquent | slow_roller_erratic | slow_roller_intermittent | stabilized | straight_roller_early_life | straight_roller_seasoned |
|---|---|---|---|---|---|---|---|
| bust_out | 0.76 | 0.00 | 0.00 | 0.00 | 0.01 | 0.23 | 0.00 |
| clean_abrupt_shock | 0.01 | 0.00 | 0.00 | 0.00 | 0.02 | 0.06 | 0.91 |
| dip_and_roll | 0.00 | 0.00 | 0.43 | 0.00 | 0.06 | 0.03 | 0.47 |
| oscillating_payer | 0.00 | 0.00 | 0.00 | 0.00 | 0.64 | 0.03 | 0.34 |
| repeat_episodes | 0.00 | 0.59 | 0.00 | 0.02 | 0.02 | 0.01 | 0.36 |
| slow_slide | 0.00 | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 |
| stabilized | 0.00 | 0.00 | 0.00 | 0.00 | 0.68 | 0.03 | 0.29 |
| staircase | 0.00 | 0.00 | 0.00 | 0.28 | 0.72 | 0.00 | 0.00 |
| volatile | 0.00 | 0.39 | 0.08 | 0.06 | 0.20 | 0.02 | 0.25 |

Option C — examples (last 30 months, oldest → newest):

| state_c | oldest_to_newest |
|---|---|
| early_payment_default | 023456 |
| early_payment_default | 020234567 |
| early_payment_default | 00234 |
| repeat_delinquent | 000122320000023301000001234567 |
| repeat_delinquent | 000000001000002220023200023445 |
| repeat_delinquent | 000000010022334430010000000234 |
| slow_roller_erratic | 010000000000000000233234234567 |
| slow_roller_erratic | 000000000000100000000232234556 |
| slow_roller_erratic | 000232334222222343434342323455 |
| slow_roller_intermittent | 000000000000000120000002233456 |
| slow_roller_intermittent | 000000000000000010100000023345 |
| slow_roller_intermittent | 000000001000000000000022334566 |
| stabilized | 000000101000000000023234334234 |
| stabilized | 000000000000000012334233234234 |
| stabilized | 000000000000000000000234456544 |
| straight_roller_early_life | 010000002345677 |
| straight_roller_early_life | 020234555 |
| straight_roller_early_life | 00000000010234566 |
| straight_roller_seasoned | 120000000002000020000002345567 |
| straight_roller_seasoned | 000000000000000000000000100234 |
| straight_roller_seasoned | 000000000000000010000002344567 |

## C. Clustering the residual (after EPD and stabilized)

Residual = 88% of the spine. Agreement (ARI) between k-means clusters and each option's residual states:

| k | silhouette | bootstrap_ARI | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|---|---|
| 2 | 0.34 | 1.00 | -0.06 | 0.37 | 0.35 |
| 3 | 0.38 | 1.00 | 0.30 | 0.56 | 0.57 |
| 4 | 0.34 | 1.00 | 0.17 | 0.40 | 0.40 |
| 5 | 0.29 | 0.66 | 0.11 | 0.31 | 0.31 |
| 6 | 0.32 | 1.00 | 0.11 | 0.30 | 0.31 |
| 7 | 0.34 | 0.87 | 0.10 | 0.28 | 0.30 |
| 8 | 0.36 | 0.98 | 0.17 | 0.36 | 0.38 |

k = 6 cluster profiles:

| c | share_of_spine | median_months_before_spell | earlier_spell_to_3+ | straight_runup | held_on_way | paid_2+_on_way | median_paid_rate_since_4 | top_state_option_C |
|---|---|---|---|---|---|---|---|---|
| 3 | 0.30 | 64.00 | 0.00 | 0.90 | 0.10 | 0.00 | 0.00 | straight_roller_seasoned |
| 2 | 0.17 | 63.00 | 0.89 | 0.96 | 0.03 | 0.00 | 0.00 | repeat_delinquent |
| 0 | 0.17 | 19.00 | 0.00 | 0.89 | 0.11 | 0.00 | 0.00 | straight_roller_seasoned |
| 1 | 0.14 | 48.00 | 0.02 | 0.89 | 0.11 | 0.00 | 0.67 | straight_roller_seasoned |
| 5 | 0.06 | 49.00 | 0.10 | 0.00 | 0.28 | 1.00 | 0.00 | slow_roller_erratic |
| 4 | 0.03 | 46.00 | 0.05 | 0.00 | 1.00 | 0.02 | 0.00 | slow_roller_intermittent |

## D. Threshold sweeps (one parameter at a time, others at default)

### Q1 early payment default (EPD) — months of history before the spell

| epd_max_history | epd_share | exit_6m | planted_bustouts_caught | share_of_state_planted_bustout |
|---|---|---|---|---|
| 2 | 0.02 | 0.98 | 0.37 | 1.00 |
| 3 | 0.04 | 0.99 | 0.76 | 0.92 |
| 4 | 0.04 | 0.98 | 0.76 | 0.88 |
| 6 | 0.05 | 0.98 | 0.76 | 0.81 |
| 9 | 0.06 | 0.97 | 0.76 | 0.69 |
| 12 | 0.07 | 0.97 | 0.76 | 0.58 |

### Q2 stabilized — months within today's bucket ±1 (of the last 6)

| min_in_band (of 6) | stabilized_share | roll_next_month | exit_6m | still_stabilized_next_month | payment_holiday_share | planted_stabilizers_caught |
|---|---|---|---|---|---|---|
| 4 | 0.14 | 0.59 | 0.67 | 0.55 | 0.05 | 0.73 |
| 5 | 0.08 | 0.49 | 0.57 | 0.61 | 0.08 | 0.68 |
| 6 | 0.05 | 0.45 | 0.52 | 0.66 | 0.09 | 0.64 |

### Q3 paying since 4 (tested, not recommended) — months paid per month since 4

| paying_since_4_min_rate | share | roll_next_month | still_paying_since_4_next_month | paid_in_last_3m | stability_of_other_states |
|---|---|---|---|---|---|
| 0.34 | 0.21 | 0.83 | 0.73 | 0.77 | 0.89 |
| 0.50 | 0.19 | 0.82 | 0.61 | 0.80 | 0.89 |
| 0.67 | 0.08 | 0.79 | 0.31 | 0.80 | 0.95 |

### Q4 repeat delinquent — how deep the earlier spell must have gone

| earlier spell reached bucket | repeat_share |
|---|---|
| 2 | 0.17 |
| 3 | 0.15 |
| 4 | 0.04 |

### Q5 straight vs slow roller — max run-up months

| straight_max_runup | straight_share | slow_share | slow_slides_in_slow_roller | abrupt_in_straight |
|---|---|---|---|---|
| 3 | 0.71 | 0.17 | 0.98 | 0.97 |
| 4 | 0.78 | 0.10 | 0.29 | 0.97 |
| 5 | 0.85 | 0.03 | 0.01 | 0.97 |

### Q5 split — months of history before the spell (seasoned vs early-life straight roller)

| seasoned_min_months | seasoned | early_life |
|---|---|---|
| 12 | 0.53 | 0.05 |
| 18 | 0.50 | 0.08 |
| 24 | 0.46 | 0.13 |
| 36 | 0.37 | 0.21 |

## E. Discovery views (states = B_balanced_6)

### Top 15 shapes (6023 distinct) — by state

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3787 | straight_roller_seasoned | 1.00 | 0.19 | 0.19 |
| N13-24 R3+ | 821 | straight_roller_seasoned | 1.00 | 0.04 | 0.23 |
| N25+ R3+ H1 | 363 | straight_roller_seasoned | 1.00 | 0.02 | 0.25 |
| N7-12 R3+ | 334 | straight_roller_early_life | 0.68 | 0.02 | 0.27 |
| N2-3 R3+ | 274 | early_payment_default | 0.87 | 0.01 | 0.28 |
| N25+ R3+ H1 R1 | 248 | straight_roller_seasoned | 1.00 | 0.01 | 0.29 |
| R1 P1 R3+ | 234 | early_payment_default | 1.00 | 0.01 | 0.30 |
| N25+ R2 P1 R3+ | 217 | slow_roller | 0.93 | 0.01 | 0.31 |
| N1 R3+ | 202 | early_payment_default | 1.00 | 0.01 | 0.32 |
| R3+ | 186 | early_payment_default | 1.00 | 0.01 | 0.33 |
| N25+ R3+ P1 R3+ | 181 | straight_roller_seasoned | 1.00 | 0.01 | 0.34 |
| N25+ R3+ H1 R2 | 174 | straight_roller_seasoned | 1.00 | 0.01 | 0.35 |
| N25+ R1 H1 R3+ | 168 | slow_roller | 1.00 | 0.01 | 0.36 |
| N25+ R3+ P1 R1 | 165 | straight_roller_seasoned | 1.00 | 0.01 | 0.37 |
| N25+ R3+ P1 R2 | 113 | straight_roller_seasoned | 1.00 | 0.01 | 0.37 |

### 4-grams ranked by lift vs shuffled order (support ≥ 1%)

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| HHPP | 0.02 | 92.80 | repeat_delinquent | 0.81 |
| RHHP | 0.09 | 71.15 | repeat_delinquent | 0.59 |
| HRHP | 0.03 | 38.87 | repeat_delinquent | 0.76 |
| RHPP | 0.02 | 32.29 | repeat_delinquent | 0.81 |
| HHPN | 0.07 | 27.11 | repeat_delinquent | 0.56 |
| RHRH | 0.10 | 26.03 | repeat_delinquent | 0.44 |
| RRHH | 0.07 | 22.36 | repeat_delinquent | 0.40 |
| RPRP | 0.10 | 20.84 | repeat_delinquent | 0.34 |
| RRRH | 0.19 | 20.37 | straight_roller_seasoned | 0.55 |
| RRHP | 0.04 | 19.68 | repeat_delinquent | 0.69 |
| HPPN | 0.04 | 19.45 | repeat_delinquent | 0.86 |
| RHRP | 0.05 | 18.00 | repeat_delinquent | 0.60 |
| RRPH | 0.05 | 17.11 | slow_roller | 0.30 |
| PRHP | 0.01 | 16.64 | repeat_delinquent | 0.54 |
| RPHR | 0.04 | 16.60 | slow_roller | 0.36 |
| RRHR | 0.15 | 16.36 | straight_roller_seasoned | 0.38 |
| HRPP | 0.02 | 15.52 | repeat_delinquent | 0.71 |
| HRHH | 0.05 | 14.32 | repeat_delinquent | 0.43 |
| RHHH | 0.04 | 13.66 | stabilized | 0.68 |
| HRHR | 0.05 | 13.33 | slow_roller | 0.64 |

### k-means on clock-safe features

| k | silhouette | bootstrap_ARI | ARI_vs_planted | ARI_vs_states |
|---|---|---|---|---|
| 4 | 0.328 | 0.988 | 0.381 | 0.413 |
| 5 | 0.338 | 0.985 | 0.383 | 0.384 |
| 6 | 0.283 | 0.979 | 0.373 | 0.453 |
| 7 | 0.278 | 0.607 | 0.387 | 0.432 |
| 8 | 0.291 | 0.989 | 0.363 | 0.400 |
