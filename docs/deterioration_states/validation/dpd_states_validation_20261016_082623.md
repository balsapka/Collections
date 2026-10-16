# DPD deterioration states — synthetic validation 20261016_082623

20,000 calibrated synthetic spine accounts (current bucket 4–7). Strings: leftmost = current bucket. 0 ≡ 1.

## A. Is the synthetic spine life-like?

| check | your book | synthetic |
|---|---|---|
| Monthly roll rate at 4 | 70% | 70% |
| Monthly roll rate at 5 | 80% | 79% |
| Monthly roll rate at 6 | 90% | 89% |
| Monthly roll rate at 7 | 95% | 94% |
| One spell only (spell from bucket 3) | ~85% | 83% |
| One spell only (spell from bucket 4) | ~85% | 95% |
| Bust-out share | 6% | 5.8% |
| Stabilized share (your 5/6 rule, after bust-out) | 6% | 6.6% |
| Never paid since reaching 4 | majority (90% 'overkill') | 61% |

Current bucket mix:

| b_now | share |
|---|---|
| 4 | 30% |
| 5 | 25% |
| 6 | 23% |
| 7 | 22% |

Months of history before the current spell (continuous — no planted gaps):

| months_before_spell | share |
|---|---|
| 0-3 | 3% |
| 4-6 | 3% |
| 7-12 | 5% |
| 13-24 | 13% |
| 25-36 | 14% |
| 37-60 | 25% |
| 61-120 | 29% |
| 121+ | 8% |

| data-quality effect | share |
|---|---|
| accounts with a payment holiday in history | 2.1% |
| accounts with a +2 jump repaired (next to a hold) | 2.3% |
| accounts with a +2 jump left (read as roll) | 0.3% |

## B. State options — each a MECE tree (first 'yes' wins)

Shared thresholds: `{'bust_max_history': 6, 'bust_max_prior_peak': 2, 'sudden_max_runup': 3, 'hold_min_in_band': 5, 'partial_min_paid_rate': None, 'relapse_min_prior_peak': None, 'established_min': None, 'split_gradual': False}`

### A_minimal_4 — 4 states (extra switches: `{}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.86 | 0.96 | 1.00 | 0.23 | 0.00 |
| holding | 0.07 | 0.44 | 0.56 | 0.60 | 1.00 | 0.10 |
| sudden_decline | 0.70 | 0.85 | 0.95 | 0.99 | 0.24 | 0.24 |
| gradual_decline | 0.18 | 0.82 | 0.91 | 0.98 | 0.57 | 0.09 |

### B_balanced_6 — 6 states (extra switches: `{'relapse_min_prior_peak': 3, 'established_min': 36}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.86 | 0.96 | 1.00 | 0.23 | 0.00 |
| holding | 0.07 | 0.44 | 0.56 | 0.60 | 1.00 | 0.10 |
| relapse | 0.17 | 0.85 | 0.94 | 0.99 | 0.26 | 1.00 |
| sudden_established | 0.35 | 0.84 | 0.95 | 0.99 | 0.25 | 0.04 |
| sudden_early_life | 0.20 | 0.85 | 0.94 | 0.98 | 0.25 | 0.03 |
| gradual_decline | 0.16 | 0.84 | 0.93 | 0.98 | 0.57 | 0.00 |

### C_detailed_7 — 7 states (extra switches: `{'relapse_min_prior_peak': 3, 'established_min': 36, 'split_gradual': True}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.86 | 0.96 | 1.00 | 0.23 | 0.00 |
| holding | 0.07 | 0.44 | 0.56 | 0.60 | 1.00 | 0.10 |
| relapse | 0.17 | 0.85 | 0.94 | 0.99 | 0.26 | 1.00 |
| sudden_established | 0.35 | 0.84 | 0.95 | 0.99 | 0.25 | 0.04 |
| sudden_early_life | 0.20 | 0.85 | 0.94 | 0.98 | 0.25 | 0.03 |
| gradual_slide | 0.10 | 0.82 | 0.91 | 0.97 | 0.62 | 0.00 |
| gradual_fought_back | 0.06 | 0.86 | 0.94 | 0.99 | 0.48 | 0.00 |

Option C — state mix by current bucket:

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.05 | 0.06 | 0.06 | 0.07 |
| gradual_fought_back | 0.06 | 0.06 | 0.06 | 0.07 |
| gradual_slide | 0.10 | 0.09 | 0.09 | 0.10 |
| holding | 0.13 | 0.07 | 0.03 | 0.01 |
| relapse | 0.15 | 0.18 | 0.18 | 0.17 |
| sudden_early_life | 0.18 | 0.19 | 0.21 | 0.21 |
| sudden_established | 0.32 | 0.34 | 0.37 | 0.37 |

Option C — planted pattern → state (row share):

| true_archetype | bust_out | gradual_fought_back | gradual_slide | holding | relapse | sudden_early_life | sudden_established |
|---|---|---|---|---|---|---|---|
| bust_out | 0.80 | 0.00 | 0.00 | 0.00 | 0.00 | 0.20 | 0.00 |
| clean_abrupt_shock | 0.03 | 0.00 | 0.01 | 0.02 | 0.00 | 0.33 | 0.62 |
| dip_and_roll | 0.01 | 0.47 | 0.00 | 0.06 | 0.00 | 0.15 | 0.30 |
| repeat_episodes | 0.00 | 0.00 | 0.02 | 0.01 | 0.69 | 0.08 | 0.18 |
| slow_slide | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 | 0.00 |
| stabilized | 0.02 | 0.00 | 0.00 | 0.65 | 0.00 | 0.13 | 0.20 |
| staircase | 0.00 | 0.00 | 0.23 | 0.77 | 0.00 | 0.00 | 0.00 |
| volatile | 0.01 | 0.09 | 0.07 | 0.15 | 0.40 | 0.11 | 0.18 |

Option C — examples (last 30 months, oldest → newest):

| state_c | oldest_to_newest |
|---|---|
| bust_out | 000234 |
| bust_out | 0002345 |
| bust_out | 023456777777 |
| gradual_fought_back | 1000002323455 |
| gradual_fought_back | 000000000000000001000233234 |
| gradual_fought_back | 000010001000000000001000023234 |
| gradual_slide | 000000000001020001000000022345 |
| gradual_slide | 001001000100000000000000002334 |
| gradual_slide | 000100000000000000000000002334 |
| holding | 556666666555555544455566656666 |
| holding | 020002345545444444444444333344 |
| holding | 000000000100000000100002334234 |
| relapse | 022000000002220000000000234567 |
| relapse | 001000000233123343323423123556 |
| relapse | 010233300002233400000000023456 |
| sudden_early_life | 000000000234 |
| sudden_early_life | 000001000000000000010010100234 |
| sudden_early_life | 00000000000200000000002345 |
| sudden_established | 200000000120000000000000202345 |
| sudden_established | 010000101000000000000000234567 |
| sudden_established | 000000000000000000023423342345 |

## C. Clustering the residual (after bust-out and holding)

Residual = 88% of the spine. Agreement (ARI) between k-means clusters and each option's residual states:

| k | silhouette | bootstrap_ARI | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|---|---|
| 2 | 0.35 | 1.00 | -0.07 | 0.28 | 0.26 |
| 3 | 0.38 | 1.00 | 0.30 | 0.41 | 0.42 |
| 4 | 0.35 | 1.00 | 0.19 | 0.35 | 0.36 |
| 5 | 0.37 | 0.86 | 0.18 | 0.33 | 0.36 |
| 6 | 0.31 | 0.87 | 0.16 | 0.55 | 0.58 |
| 7 | 0.33 | 0.90 | 0.10 | 0.52 | 0.55 |
| 8 | 0.34 | 0.83 | 0.16 | 0.59 | 0.62 |

k = 6 cluster profiles:

| c | share_of_spine | median_months_before_spell | earlier_spell_to_3+ | straight_runup | held_on_way | paid_2+_on_way | median_paid_rate_since_4 | top_state_option_C |
|---|---|---|---|---|---|---|---|---|
| 5 | 0.24 | 72.00 | 0.00 | 0.97 | 0.03 | 0.00 | 0.00 | sudden_established |
| 2 | 0.19 | 23.00 | 0.00 | 0.96 | 0.04 | 0.00 | 0.00 | sudden_early_life |
| 0 | 0.17 | 62.00 | 0.91 | 0.96 | 0.03 | 0.00 | 0.00 | relapse |
| 4 | 0.12 | 48.00 | 0.03 | 0.92 | 0.08 | 0.00 | 0.67 | sudden_established |
| 1 | 0.07 | 45.00 | 0.02 | 0.00 | 1.00 | 0.01 | 0.00 | gradual_slide |
| 3 | 0.07 | 47.00 | 0.11 | 0.00 | 0.31 | 1.00 | 0.00 | gradual_fought_back |

## D. Threshold sweeps (one parameter at a time, others at default)

### Q1 bust-out — months of history before the spell

| bust_max_history | bust_share | exit_6m | planted_bustouts_caught | share_of_state_planted_bustout |
|---|---|---|---|---|
| 3 | 0.03 | 0.99 | 0.47 | 0.87 |
| 6 | 0.06 | 0.96 | 0.80 | 0.73 |
| 9 | 0.08 | 0.96 | 0.94 | 0.63 |
| 12 | 0.10 | 0.95 | 0.98 | 0.52 |
| 18 | 0.14 | 0.94 | 1.00 | 0.38 |
| 24 | 0.18 | 0.94 | 1.00 | 0.29 |

### Q2 holding — months within today's bucket ±1 (of the last 6)

| min_in_band (of 6) | holding_share | roll_next_month | exit_6m | still_holding_next_month | payment_holiday_share | planted_stabilizers_caught |
|---|---|---|---|---|---|---|
| 4 | 0.13 | 0.54 | 0.65 | 0.54 | 0.07 | 0.74 |
| 5 | 0.07 | 0.44 | 0.56 | 0.60 | 0.10 | 0.65 |
| 6 | 0.03 | 0.34 | 0.47 | 0.75 | 0.13 | 0.57 |

### Q3 partial payer (tested, not recommended) — months paid per month since 4

| partial_min_paid_rate | share | roll_next_month | still_partial_next_month | paid_in_last_3m | stability_of_other_states |
|---|---|---|---|---|---|
| 0.34 | 0.19 | 0.81 | 0.74 | 0.76 | 0.91 |
| 0.50 | 0.18 | 0.80 | 0.63 | 0.79 | 0.91 |
| 0.67 | 0.08 | 0.72 | 0.43 | 0.78 | 0.96 |

### Q4 relapse — how deep the earlier spell must have gone

| earlier spell reached bucket | relapse_share |
|---|---|
| 2 | 0.19 |
| 3 | 0.17 |
| 4 | 0.05 |

### Q5 sudden vs gradual — max run-up months

| sudden_max_runup | sudden_share | gradual_share | slow_slides_in_gradual | abrupt_in_sudden |
|---|---|---|---|---|
| 3 | 0.70 | 0.18 | 0.98 | 0.95 |
| 4 | 0.77 | 0.10 | 0.29 | 0.95 |
| 5 | 0.84 | 0.03 | 0.00 | 0.95 |

### Q5 split — months of history before the spell (established vs early-life)

| established_min | established | early_life |
|---|---|---|
| 24 | 0.43 | 0.11 |
| 36 | 0.35 | 0.20 |
| 48 | 0.27 | 0.28 |
| 60 | 0.21 | 0.34 |

## E. Discovery views (states = B_balanced_6)

### Top 15 shapes (5891 distinct) — by state

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3763 | sudden_established | 0.81 | 0.19 | 0.19 |
| N13-24 R3+ | 815 | sudden_early_life | 1.00 | 0.04 | 0.23 |
| N7-12 R3+ | 357 | sudden_early_life | 1.00 | 0.02 | 0.25 |
| N25+ R3+ H1 | 317 | sudden_established | 0.83 | 0.02 | 0.26 |
| N2-3 R3+ | 249 | bust_out | 1.00 | 0.01 | 0.28 |
| N4-6 R3+ | 246 | bust_out | 0.69 | 0.01 | 0.29 |
| N25+ R2 P1 R3+ | 236 | gradual_decline | 0.94 | 0.01 | 0.30 |
| N25+ R3+ H1 R1 | 229 | sudden_established | 0.82 | 0.01 | 0.31 |
| N25+ R3+ P1 R3+ | 177 | sudden_established | 0.82 | 0.01 | 0.32 |
| N25+ R3+ H1 R2 | 152 | sudden_established | 0.84 | 0.01 | 0.33 |
| N25+ R1 H1 R3+ | 139 | gradual_decline | 1.00 | 0.01 | 0.33 |
| N1 R3+ | 137 | bust_out | 1.00 | 0.01 | 0.34 |
| N25+ R3+ P1 R2 | 135 | sudden_established | 0.90 | 0.01 | 0.35 |
| R3+ | 132 | bust_out | 1.00 | 0.01 | 0.35 |
| N25+ R2 P1 R2 | 128 | gradual_decline | 1.00 | 0.01 | 0.36 |

### 4-grams ranked by lift vs shuffled order (support ≥ 1%)

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.09 | 127.79 | relapse | 0.73 |
| HHPP | 0.02 | 72.50 | relapse | 0.97 |
| RHRH | 0.10 | 33.69 | relapse | 0.53 |
| RHPP | 0.02 | 29.71 | relapse | 0.97 |
| HRHP | 0.03 | 27.36 | relapse | 0.89 |
| RRPH | 0.05 | 27.35 | gradual_decline | 0.35 |
| RPRP | 0.09 | 26.74 | relapse | 0.37 |
| HHPN | 0.07 | 25.53 | relapse | 0.72 |
| RRHH | 0.07 | 25.29 | relapse | 0.45 |
| RRRH | 0.18 | 21.05 | sudden_established | 0.35 |
| HRPP | 0.02 | 21.00 | relapse | 0.88 |
| RHRP | 0.05 | 20.94 | relapse | 0.68 |
| RRHP | 0.04 | 19.40 | relapse | 0.82 |
| RPHR | 0.04 | 19.33 | gradual_decline | 0.41 |
| RRHR | 0.15 | 19.07 | gradual_decline | 0.32 |
| HPPN | 0.04 | 18.23 | relapse | 0.99 |
| RPRH | 0.04 | 16.51 | relapse | 0.36 |
| PRRP | 0.05 | 15.71 | relapse | 0.46 |
| PRHP | 0.01 | 15.62 | relapse | 0.58 |
| RHRR | 0.12 | 15.21 | gradual_decline | 0.59 |

### k-means on clock-safe features

| k | silhouette | bootstrap_ARI | ARI_vs_planted | ARI_vs_states |
|---|---|---|---|---|
| 4 | 0.309 | 0.869 | 0.351 | 0.276 |
| 5 | 0.345 | 0.881 | 0.389 | 0.299 |
| 6 | 0.263 | 0.987 | 0.360 | 0.455 |
| 7 | 0.277 | 0.632 | 0.331 | 0.388 |
| 8 | 0.278 | 0.984 | 0.355 | 0.380 |
