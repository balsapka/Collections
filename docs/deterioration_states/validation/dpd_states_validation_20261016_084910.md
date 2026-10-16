# DPD deterioration states — synthetic validation 20261016_084910

20,000 calibrated synthetic spine accounts (current bucket 4–7). Strings: leftmost = current bucket. 0 ≡ 1.

## A. Is the synthetic spine life-like?

| check | your book | synthetic |
|---|---|---|
| Monthly roll rate at 4 | 70% | 70% |
| Monthly roll rate at 5 | 80% | 80% |
| Monthly roll rate at 6 | 90% | 89% |
| Monthly roll rate at 7 | 95% | 95% |
| One spell only (spell from bucket 3) | ~85% | 83% |
| One spell only (spell from bucket 4) | ~85% | 95% |
| Bust-out share | 6% | 5.8% |
| Stabilized share (your 5/6 rule, after bust-out) | 6% | 6.5% |
| Never paid since reaching 4 | majority (90% 'overkill') | 61% |

Current bucket mix:

| b_now | share |
|---|---|
| 4 | 30% |
| 5 | 26% |
| 6 | 23% |
| 7 | 22% |

Months of history before the current spell (continuous — no planted gaps):

| months_before_spell | share |
|---|---|
| 0-3 | 6% |
| 4-6 | 1% |
| 7-12 | 4% |
| 13-24 | 12% |
| 25-36 | 14% |
| 37-60 | 24% |
| 61-120 | 30% |
| 121+ | 8% |

| data-quality effect | share |
|---|---|
| accounts with a payment holiday in history | 2.2% |
| accounts with a +2 jump repaired (next to a hold) | 2.3% |
| accounts with a +2 jump left (read as roll) | 0.3% |

## B. State options — each a MECE tree (first 'yes' wins)

Shared thresholds: `{'bust_max_history': 3, 'bust_max_blips': 1, 'sudden_max_runup': 3, 'hold_min_in_band': 5, 'partial_min_paid_rate': None, 'relapse_min_prior_peak': None, 'established_min': None, 'split_gradual': False}`

### A_minimal_4 — 4 states (extra switches: `{}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.88 | 0.98 | 1.00 | 0.21 | 0.00 |
| holding | 0.07 | 0.40 | 0.54 | 0.62 | 1.00 | 0.11 |
| sudden_decline | 0.71 | 0.86 | 0.95 | 0.99 | 0.25 | 0.24 |
| gradual_decline | 0.17 | 0.82 | 0.91 | 0.97 | 0.54 | 0.09 |

### B_balanced_6 — 6 states (extra switches: `{'relapse_min_prior_peak': 3, 'established_min': 12}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.88 | 0.98 | 1.00 | 0.21 | 0.00 |
| holding | 0.07 | 0.40 | 0.54 | 0.62 | 1.00 | 0.11 |
| relapse | 0.16 | 0.85 | 0.93 | 0.99 | 0.26 | 1.00 |
| sudden_established | 0.52 | 0.85 | 0.95 | 0.99 | 0.26 | 0.04 |
| sudden_early_life | 0.03 | 0.85 | 0.94 | 0.99 | 0.25 | 0.01 |
| gradual_decline | 0.16 | 0.84 | 0.93 | 0.97 | 0.54 | 0.00 |

### C_detailed_7 — 7 states (extra switches: `{'relapse_min_prior_peak': 3, 'established_min': 12, 'split_gradual': True}`)

| state | share | roll_next_month | exit_to_8_in_6m | same_state_next_month | paid_in_last_3m | earlier_spell |
|---|---|---|---|---|---|---|
| bust_out | 0.06 | 0.88 | 0.98 | 1.00 | 0.21 | 0.00 |
| holding | 0.07 | 0.40 | 0.54 | 0.62 | 1.00 | 0.11 |
| relapse | 0.16 | 0.85 | 0.93 | 0.99 | 0.26 | 1.00 |
| sudden_established | 0.52 | 0.85 | 0.95 | 0.99 | 0.26 | 0.04 |
| sudden_early_life | 0.03 | 0.85 | 0.94 | 0.99 | 0.25 | 0.01 |
| gradual_slide | 0.10 | 0.83 | 0.92 | 0.96 | 0.58 | 0.01 |
| gradual_fought_back | 0.06 | 0.85 | 0.93 | 0.99 | 0.46 | 0.00 |

Option C — state mix by current bucket:

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.06 | 0.06 | 0.06 | 0.06 |
| gradual_fought_back | 0.05 | 0.06 | 0.06 | 0.07 |
| gradual_slide | 0.09 | 0.09 | 0.10 | 0.10 |
| holding | 0.13 | 0.06 | 0.03 | 0.01 |
| relapse | 0.16 | 0.16 | 0.16 | 0.18 |
| sudden_early_life | 0.03 | 0.04 | 0.04 | 0.03 |
| sudden_established | 0.49 | 0.52 | 0.55 | 0.55 |

Option C — planted pattern → state (row share):

| true_archetype | bust_out | gradual_fought_back | gradual_slide | holding | relapse | sudden_early_life | sudden_established |
|---|---|---|---|---|---|---|---|
| bust_out | 1.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 | 0.00 |
| clean_abrupt_shock | 0.01 | 0.00 | 0.00 | 0.02 | 0.00 | 0.06 | 0.91 |
| dip_and_roll | 0.00 | 0.46 | 0.00 | 0.06 | 0.00 | 0.03 | 0.45 |
| repeat_episodes | 0.00 | 0.00 | 0.02 | 0.01 | 0.70 | 0.01 | 0.25 |
| slow_slide | 0.00 | 0.00 | 0.98 | 0.02 | 0.00 | 0.00 | 0.00 |
| stabilized | 0.00 | 0.00 | 0.00 | 0.60 | 0.00 | 0.04 | 0.37 |
| staircase | 0.00 | 0.00 | 0.26 | 0.74 | 0.00 | 0.00 | 0.00 |
| volatile | 0.00 | 0.08 | 0.06 | 0.17 | 0.37 | 0.02 | 0.30 |

Option C — examples (last 30 months, oldest → newest):

| state_c | oldest_to_newest |
|---|---|
| bust_out | 02345 |
| bust_out | 02023445 |
| bust_out | 020234545677 |
| gradual_fought_back | 00000000000232345 |
| gradual_fought_back | 010000000100000000000002322345 |
| gradual_fought_back | 0100000000000000000023234567 |
| gradual_slide | 000000000010000001002233445567 |
| gradual_slide | 000000000000000000000222223445 |
| gradual_slide | 000000010000000000000000023345 |
| holding | 001000000000000000010023342334 |
| holding | 100000000002344565444 |
| holding | 000000000000000000023456666667 |
| relapse | 023332000000233300000002345567 |
| relapse | 000022333001000000000000000234 |
| relapse | 000000100002220000000000023456 |
| sudden_early_life | 00000000000234433333333333446 |
| sudden_early_life | 00002002345 |
| sudden_early_life | 0000000000023456 |
| sudden_established | 120000002000000000020000002344 |
| sudden_established | 100001000000000000000023434345 |
| sudden_established | 000000000022000000000000002345 |

## C. Clustering the residual (after bust-out and holding)

Residual = 88% of the spine. Agreement (ARI) between k-means clusters and each option's residual states:

| k | silhouette | bootstrap_ARI | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|---|---|
| 2 | 0.34 | 1.00 | -0.07 | 0.44 | 0.42 |
| 3 | 0.38 | 1.00 | 0.31 | 0.65 | 0.65 |
| 4 | 0.34 | 1.00 | 0.19 | 0.46 | 0.47 |
| 5 | 0.37 | 0.87 | 0.31 | 0.56 | 0.59 |
| 6 | 0.31 | 1.00 | 0.11 | 0.32 | 0.34 |
| 7 | 0.34 | 0.99 | 0.10 | 0.29 | 0.31 |
| 8 | 0.35 | 0.96 | 0.16 | 0.35 | 0.37 |

k = 6 cluster profiles:

| c | share_of_spine | median_months_before_spell | earlier_spell_to_3+ | straight_runup | held_on_way | paid_2+_on_way | median_paid_rate_since_4 | top_state_option_C |
|---|---|---|---|---|---|---|---|---|
| 4 | 0.27 | 70.50 | 0.00 | 0.90 | 0.10 | 0.00 | 0.00 | sudden_established |
| 3 | 0.19 | 23.00 | 0.00 | 0.89 | 0.11 | 0.00 | 0.00 | sudden_established |
| 0 | 0.17 | 63.00 | 0.90 | 0.96 | 0.04 | 0.00 | 0.00 | relapse |
| 1 | 0.13 | 48.00 | 0.02 | 0.90 | 0.10 | 0.00 | 0.67 | sudden_established |
| 5 | 0.07 | 47.00 | 0.10 | 0.00 | 0.30 | 1.00 | 0.00 | gradual_fought_back |
| 2 | 0.04 | 44.00 | 0.04 | 0.00 | 1.00 | 0.02 | 0.00 | gradual_slide |

## D. Threshold sweeps (one parameter at a time, others at default)

### Q1 bust-out — months of history before the spell

| bust_max_history | bust_share | exit_6m | planted_bustouts_caught | share_of_state_planted_bustout |
|---|---|---|---|---|
| 2 | 0.02 | 0.99 | 0.45 | 0.99 |
| 3 | 0.06 | 0.98 | 1.00 | 0.93 |
| 4 | 0.06 | 0.98 | 1.00 | 0.90 |
| 6 | 0.07 | 0.97 | 1.00 | 0.79 |
| 9 | 0.08 | 0.96 | 1.00 | 0.66 |
| 12 | 0.10 | 0.95 | 1.00 | 0.55 |

### Q2 holding — months within today's bucket ±1 (of the last 6)

| min_in_band (of 6) | holding_share | roll_next_month | exit_6m | still_holding_next_month | payment_holiday_share | planted_stabilizers_caught |
|---|---|---|---|---|---|---|
| 4 | 0.13 | 0.53 | 0.65 | 0.54 | 0.08 | 0.67 |
| 5 | 0.07 | 0.40 | 0.54 | 0.62 | 0.11 | 0.60 |
| 6 | 0.03 | 0.31 | 0.45 | 0.78 | 0.14 | 0.54 |

### Q3 partial payer (tested, not recommended) — months paid per month since 4

| partial_min_paid_rate | share | roll_next_month | still_partial_next_month | paid_in_last_3m | stability_of_other_states |
|---|---|---|---|---|---|
| 0.34 | 0.20 | 0.82 | 0.73 | 0.77 | 0.91 |
| 0.50 | 0.18 | 0.81 | 0.61 | 0.80 | 0.91 |
| 0.67 | 0.08 | 0.73 | 0.42 | 0.81 | 0.96 |

### Q4 relapse — how deep the earlier spell must have gone

| earlier spell reached bucket | relapse_share |
|---|---|
| 2 | 0.18 |
| 3 | 0.16 |
| 4 | 0.04 |

### Q5 sudden vs gradual — max run-up months

| sudden_max_runup | sudden_share | gradual_share | slow_slides_in_gradual | abrupt_in_sudden |
|---|---|---|---|---|
| 3 | 0.71 | 0.17 | 0.98 | 0.97 |
| 4 | 0.77 | 0.10 | 0.32 | 0.97 |
| 5 | 0.85 | 0.03 | 0.01 | 0.97 |

### Q5 split — months of history before the spell (established vs early-life)

| established_min | established | early_life |
|---|---|---|
| 12 | 0.52 | 0.03 |
| 18 | 0.49 | 0.07 |
| 24 | 0.45 | 0.11 |
| 36 | 0.36 | 0.20 |

## E. Discovery views (states = B_balanced_6)

### Top 15 shapes (5757 distinct) — by state

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3863 | sudden_established | 1.00 | 0.19 | 0.19 |
| N13-24 R3+ | 827 | sudden_established | 1.00 | 0.04 | 0.23 |
| N25+ R3+ H1 | 334 | sudden_established | 1.00 | 0.02 | 0.25 |
| N7-12 R3+ | 315 | sudden_early_life | 0.66 | 0.02 | 0.27 |
| N2-3 R3+ | 283 | bust_out | 0.90 | 0.01 | 0.28 |
| R1 P1 R3+ | 273 | bust_out | 1.00 | 0.01 | 0.29 |
| N25+ R3+ H1 R1 | 257 | sudden_established | 1.00 | 0.01 | 0.31 |
| N25+ R2 P1 R3+ | 257 | gradual_decline | 0.93 | 0.01 | 0.32 |
| R3+ | 196 | bust_out | 1.00 | 0.01 | 0.33 |
| N25+ R1 H1 R3+ | 179 | gradual_decline | 1.00 | 0.01 | 0.34 |
| N1 R3+ | 174 | bust_out | 1.00 | 0.01 | 0.35 |
| N25+ R3+ H1 R2 | 165 | sudden_established | 1.00 | 0.01 | 0.36 |
| N25+ R3+ P1 R3+ | 156 | sudden_established | 1.00 | 0.01 | 0.36 |
| N25+ R3+ P1 R1 | 139 | sudden_established | 1.00 | 0.01 | 0.37 |
| N4-6 R3+ | 135 | sudden_early_life | 1.00 | 0.01 | 0.38 |

### 4-grams ranked by lift vs shuffled order (support ≥ 1%)

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.09 | 101.11 | relapse | 0.72 |
| HHPP | 0.02 | 60.75 | relapse | 0.96 |
| RHRH | 0.10 | 29.91 | relapse | 0.52 |
| HRHP | 0.03 | 29.55 | relapse | 0.91 |
| HRPP | 0.02 | 28.73 | relapse | 0.87 |
| RHPP | 0.02 | 27.19 | relapse | 0.98 |
| HHPN | 0.07 | 26.43 | relapse | 0.71 |
| RRHH | 0.08 | 25.16 | relapse | 0.43 |
| RPRP | 0.09 | 23.85 | sudden_established | 0.38 |
| RRHP | 0.04 | 22.64 | relapse | 0.80 |
| HPPN | 0.04 | 22.16 | relapse | 0.99 |
| RHRP | 0.05 | 19.80 | relapse | 0.71 |
| RRRH | 0.18 | 19.43 | sudden_established | 0.53 |
| RPHR | 0.04 | 17.33 | gradual_decline | 0.39 |
| RRHR | 0.15 | 16.18 | sudden_established | 0.37 |
| RRPH | 0.04 | 16.07 | gradual_decline | 0.35 |
| HHHP | 0.01 | 15.86 | holding | 0.61 |
| HRHH | 0.06 | 14.81 | relapse | 0.48 |
| HRHR | 0.05 | 13.96 | gradual_decline | 0.68 |
| PHRR | 0.03 | 13.95 | gradual_decline | 0.56 |

### k-means on clock-safe features

| k | silhouette | bootstrap_ARI | ARI_vs_planted | ARI_vs_states |
|---|---|---|---|---|
| 4 | 0.312 | 0.715 | 0.323 | 0.359 |
| 5 | 0.337 | 0.993 | 0.387 | 0.419 |
| 6 | 0.282 | 0.992 | 0.387 | 0.493 |
| 7 | 0.300 | 0.985 | 0.362 | 0.454 |
| 8 | 0.291 | 0.988 | 0.378 | 0.431 |
