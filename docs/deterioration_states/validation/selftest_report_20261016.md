# Self-test on synthetic data — 20261016

Fake axis columns; real-data code path.

## 0. Expectation checks

| id | status | check | observed | expected | why | if_not_met |
|---|---|---|---|---|---|---|
| E01 | PASS | Every account gets exactly one state (all options) | True | True | The tree has a default branch, so it is MECE by construction. | A code or data-type bug — stop and fix before reading anything else. |
| E02 | PASS | Share of DPD strings that cannot be parsed | 0.000 | <= 2% | Strings should be digits once CHAR_MAP / STRIP_CHARS are set. | Inspect the non-digit characters; extend CHAR_MAP or STRIP_CHARS in config.py. |
| E03 | PASS | Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation) | 0.009 | <= 7pp | Confirms the string orientation and the backtest reconstruction are right. | Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine (survivor-only data shows roll rates that are too low). |
| E04 | PASS | Share of histories that start inside the current spell (no clean month seen) | 0.000 | <= 10% | Full history is available for everyone. | Strings are truncated; bust-out (short history) will be over-assigned — cap the bust-out rule to accounts with full history or raise the threshold. |
| E05 | PASS | Share of accounts with an unrepaired +2 jump | 0.003 | <= 2% | Billing-cycle jumps are mostly next to a hold and get repaired. | Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding. |
| E06 | PASS | Current bucket mix declines from 4 to 7 | 0.080 | >= 0 | Flow-driven book with rising roll rates (synthetic 29/26/23/22%). | Check the spine filter and whether a cohort shock is passing through. |
| E07 | PASS | One spell only, spell counted from bucket 3 | 0.829 | 78–92% | Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one near 85%, the bank counts spells from 4. | Set relapse_min_prior_peak to whichever spell definition matches the bank's 85%. |
| E08 | PASS | Bust-out share (today) | 0.058 | 4–8% | Bank's own rule gives ~6% (synthetic 5.8%). | Move bust_max_history along the sweep until the share matches the bank's rule. |
| E09 | PASS | Holding share (today) | 0.065 | 4–9% | Bank's own stabilized rule gives ~6% (synthetic 6.6%). | Compare with the bank's implementation of the 5-of-6 rule (E10/E11). |
| E10 | PASS | Recall of the bank's existing bust-out flag | 0.941 | >= 80% | Same concept; thresholds may differ slightly. | Read the bank's rule and align bust_max_history / bust_max_blips. |
| E11 | PASS | Recall of the bank's existing stabilized flag | 0.926 | >= 90% | Holding IS the bank's 5-of-6 rule; only bust-out-first ordering differs. | Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today). |
| E12 | PASS | Holding separates risk: weighted next-month roll of fixed states minus holding | 0.429 | >= 20pp | Synthetic: holding 40% vs ~85% for the rest. | Holding is not behaving as 'stable'; check payment holidays / restructuring flags (E21) and try hold_min_in_band = 6. |
| E13 | PASS | Fixed states keep their state next month (minimum over fixed states) | 0.973 | >= 95% | Run-up and history are fixed once past 4 (synthetic 98–100%). | A feature is drifting with time since 4 — inspect which state leaks and why. |
| E14 | PASS | Holding persistence next month | 0.615 | 45–85% | Holding is current behaviour; it should persist but not forever (synthetic 62%). | Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments. |
| E15 | PASS | Option A: sudden share | 0.706 | 55–80% | Most accounts roll straight 2-3-4 (synthetic 70%). | If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting gradual. |
| E16 | WARN | Every option-B state holds at least 5% of the spine | 0.034 | >= 5% | Actionable size. Synthetic: sudden_early_life 3.4% under the 12-month established cut (depends on the book's tenure mix). | Merge the small state into its neighbour (relapse→sudden, early_life→established), or move established_min along its sweep (12 → 18 → 24 months). |
| E17 | PASS | Option C: smaller of gradual_slide / gradual_fought_back | 0.060 | >= 4% | Synthetic 10% / 6%. | Too small to act on — use option B. |
| E18 | PASS | Holding sits low in the spine: share at bucket 4 / share at bucket 7 | 16.432 | >= 2x | 90–95% roll rates at 6–7 leave little room to hold there. | Holders at 6–7 are unusual — check for frozen buckets (payment holidays). |
| E19 | PASS | Orthogonality: credibility score explained by the states (eta²) | 0.177 | <= 0.25 | Known overlap via holding (money in) and relapse (clean point), but the states should not reproduce the score. | Use option A (drops relapse) or report holding under credibility instead. |
| E19b | WARN | Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²) | 0.835 | <= 0.50 | Relapse is defined from earlier spells — the same history the clean point scores. Synthetic (with a clean point = 'no earlier spell'): 0.84 → WARN. | Relapse duplicates the credibility clean point: use option A, or keep relapse and tell the persona grid it is the same signal (it is only 1 of credibility's 5 points). |
| E20 | PASS | Orthogonality: ability score explained by the states (eta²) | 0.000 | <= 0.10 | DPD shape should carry little of salary/inflow/CASA. | Sudden vs gradual may be a proxy for income loss — fine, but say so in the persona grid. |
| E21 | PASS | Holders with money coming in (credibility component or DPD proxy) | 1.000 | >= 90% | Holding = paid one month's due most months, so money must be coming in (synthetic 100%). | Holders without money in are frozen buckets (holiday/restructure) — exclude those months. |
| E22 | PASS | Residual clusters agree more with option B than with A (ARI gain at k=6) | 0.204 | >= 0.15 | Synthetic at k=6: 0.32 (B) vs 0.11 (A) — the data has more than two residual groups. | The extra B splits are not natural groups in this book — prefer option A. |
| E23 | PASS | One paid month on the way down matters: gradual share at run-up<=4 / at <=3 | 0.583 | <= 0.70 | Synthetic 0.56: most gradual accounts held exactly once. | Gradual is driven by long run-ups, not single payments — keep 3 but review examples. |
| E24 | PASS | Partial payer stays rejected: share still partial next month at 0.5 | 0.638 | <= 75% | Synthetic 63%: unstable current-behaviour state. | If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'. |
| E25 | INFO | INFO — spread of exit-within-k across fixed states (option B) | 0.061 | report | Synthetic data cannot show this (same post-4 dynamics by construction). | >= 5pp means the mechanism carries risk information beyond holding. |

## 1. Data quality and population

| metric | value |
|---|---|
| n_current_rows | 20000 |
| share_invalid_strings | 0.000 |
| n_current_spine_analysed | 20000 |
| string_length_p05_p50_p95 | [9, 54, 142] |
| share_left_censored | 0.000 |
| share_jump_repaired | 0.023 |
| share_jump_left | 0.003 |
| share_one_spell_from3 | 0.829 |
| share_one_spell_from4 | 0.953 |
| bucket_mix | {4: 0.29645, 5: 0.26075, 6: 0.22625, 7: 0.21655} |

## 2. States today (current spine)

### A_minimal_4

Share:

| state | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.065 |
| sudden_decline | 0.706 |
| gradual_decline | 0.171 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.056 | 0.060 | 0.056 | 0.061 |
| holding | 0.133 | 0.064 | 0.034 | 0.008 |
| sudden_decline | 0.651 | 0.710 | 0.736 | 0.745 |
| gradual_decline | 0.160 | 0.167 | 0.174 | 0.186 |

### B_balanced_6

Share:

| state | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.065 |
| relapse | 0.164 |
| sudden_established | 0.523 |
| sudden_early_life | 0.034 |
| gradual_decline | 0.156 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.056 | 0.060 | 0.056 | 0.061 |
| holding | 0.133 | 0.064 | 0.034 | 0.008 |
| relapse | 0.156 | 0.161 | 0.162 | 0.180 |
| sudden_established | 0.486 | 0.524 | 0.549 | 0.546 |
| sudden_early_life | 0.028 | 0.036 | 0.038 | 0.034 |
| gradual_decline | 0.140 | 0.156 | 0.162 | 0.170 |

### C_detailed_7

Share:

| state | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.065 |
| relapse | 0.164 |
| sudden_established | 0.523 |
| sudden_early_life | 0.034 |
| gradual_slide | 0.095 |
| gradual_fought_back | 0.060 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.056 | 0.060 | 0.056 | 0.061 |
| holding | 0.133 | 0.064 | 0.034 | 0.008 |
| relapse | 0.156 | 0.161 | 0.162 | 0.180 |
| sudden_established | 0.486 | 0.524 | 0.549 | 0.546 |
| sudden_early_life | 0.028 | 0.036 | 0.038 | 0.034 |
| gradual_slide | 0.085 | 0.094 | 0.102 | 0.104 |
| gradual_fought_back | 0.054 | 0.062 | 0.060 | 0.067 |

Examples (B_balanced_6, no keys):

| state | last_30_months_oldest_to_newest |
|---|---|
| bust_out | 020234 |
| bust_out | 02345 |
| bust_out | 0002345 |
| holding | 000000010000000001000000234334 |
| holding | 000000000000000001233423423434 |
| holding | 000001000000000000000000234334 |
| relapse | 100000222000000000010000000234 |
| relapse | 000000000000022344430023445567 |
| relapse | 000000000000000223332000000234 |
| sudden_established | 000000000001000000100000000234 |
| sudden_established | 101000000000000000000001002345 |
| sudden_established | 000100000000000000100000023456 |
| sudden_early_life | 00000010000234567 |
| sudden_early_life | 0220012000234 |
| sudden_early_life | 0010002343423434234234 |
| gradual_decline | 000001000010001000000010023234 |
| gradual_decline | 000000232345 |
| gradual_decline | 001000100000000023234567 |

## 3. Agreement with the bank's existing bust-out / stabilized rules

| state | their_share | our_share | recall_of_theirs | precision_vs_theirs |
|---|---|---|---|---|
| bust_out | 0.061 | 0.058 | 0.941 | 0.995 |
| holding | 0.070 | 0.065 | 0.926 | 0.998 |

## 4. Overlap with the other persona axes

Variance of each axis explained by the states (eta², 0 = orthogonal):

| axis | A_minimal_4 | B_balanced_6 | C_detailed_7 |
|---|---|---|---|
| credibility_score | 0.103 | 0.177 | 0.178 |
| cred_ptp_points | 0.000 | 0.000 | 0.000 |
| cred_money_in_points | 0.164 | 0.157 | 0.159 |
| cred_clean_point | 0.038 | 0.835 | 0.835 |
| ability_score | 0.000 | 0.000 | 0.000 |
| reachable_flag | 0.000 | 0.000 | 0.000 |
| in_country_flag | 0.000 | 0.000 | 0.000 |

Mean of each axis by state (B_balanced_6):

| state | credibility_score | cred_ptp_points | cred_money_in_points | cred_clean_point | ability_score | reachable_flag | in_country_flag |
|---|---|---|---|---|---|---|---|
| bust_out | 2.252 | 0.688 | 0.565 | 1.000 | 49.967 | 0.710 | 0.857 |
| holding | 3.577 | 0.688 | 2.000 | 0.888 | 50.352 | 0.694 | 0.834 |
| relapse | 1.390 | 0.716 | 0.675 | 0.000 | 50.065 | 0.707 | 0.853 |
| sudden_established | 2.332 | 0.709 | 0.659 | 0.964 | 50.224 | 0.690 | 0.852 |
| sudden_early_life | 2.333 | 0.685 | 0.662 | 0.987 | 50.031 | 0.695 | 0.857 |
| gradual_decline | 2.895 | 0.728 | 1.172 | 0.996 | 49.737 | 0.693 | 0.847 |

Holding vs money coming in:

| metric | value |
|---|---|
| source | cred_money_in_points |
| holders_with_money_in | 1.000 |
| non_holders_with_money_in | 0.440 |

## 5. Backtest — spine as of 6 months ago, outcomes since

20,000 accounts. Monthly roll rate by bucket (should match the bank's ~70/80/90/95%):

| bucket | roll_rate |
|---|---|
| 4 | 0.702 |
| 5 | 0.791 |
| 6 | 0.896 |
| 7 | 0.956 |

### A_minimal_4

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.058 | 1169 | 0.902 | 0.991 | 0.002 | 4.000 | 0.999 | 0.237 |
| holding | 0.065 | 1303 | 0.423 | 0.526 | 0.048 | 3.000 | 0.615 | 0.204 |
| sudden_decline | 0.709 | 14180 | 0.854 | 0.947 | 0.010 | 3.000 | 0.985 | 0.265 |
| gradual_decline | 0.167 | 3348 | 0.823 | 0.914 | 0.044 | 3.000 | 0.973 | 0.271 |

### B_balanced_6

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.058 | 1169 | 0.902 | 0.991 | 0.002 | 4.000 | 0.999 | 0.237 |
| holding | 0.065 | 1303 | 0.423 | 0.526 | 0.048 | 3.000 | 0.615 | 0.204 |
| relapse | 0.173 | 3459 | 0.846 | 0.939 | 0.021 | 3.000 | 0.988 | 0.266 |
| sudden_established | 0.519 | 10378 | 0.852 | 0.945 | 0.009 | 3.000 | 0.984 | 0.268 |
| sudden_early_life | 0.033 | 666 | 0.844 | 0.941 | 0.015 | 3.000 | 0.983 | 0.273 |
| gradual_decline | 0.151 | 3025 | 0.838 | 0.930 | 0.035 | 3.000 | 0.973 | 0.259 |

### C_detailed_7

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.058 | 1169 | 0.902 | 0.991 | 0.002 | 4.000 | 0.999 | 0.237 |
| holding | 0.065 | 1303 | 0.423 | 0.526 | 0.048 | 3.000 | 0.615 | 0.204 |
| relapse | 0.173 | 3459 | 0.846 | 0.939 | 0.021 | 3.000 | 0.988 | 0.266 |
| sudden_established | 0.519 | 10378 | 0.852 | 0.945 | 0.009 | 3.000 | 0.984 | 0.268 |
| sudden_early_life | 0.033 | 666 | 0.844 | 0.941 | 0.015 | 3.000 | 0.983 | 0.273 |
| gradual_slide | 0.094 | 1881 | 0.822 | 0.921 | 0.048 | 3.000 | 0.966 | 0.250 |
| gradual_fought_back | 0.057 | 1144 | 0.865 | 0.944 | 0.014 | 3.000 | 0.986 | 0.273 |

## 6. Threshold sweeps (backtest population)

### bust_max_history

| bust_max_history | share | exit_within_k |
|---|---|---|
| 2 | 0.025 | 0.990 |
| 3 | 0.058 | 0.991 |
| 4 | 0.060 | 0.990 |
| 6 | 0.069 | 0.971 |
| 9 | 0.083 | 0.962 |
| 12 | 0.099 | 0.955 |

### hold_min_in_band

| hold_min_in_band | share | roll_next_month | still_holding_next_month |
|---|---|---|---|
| 4 | 0.128 | 0.535 | 0.543 |
| 5 | 0.065 | 0.423 | 0.615 |
| 6 | 0.035 | 0.338 | 0.762 |

### relapse_min_prior_peak

| relapse_min_prior_peak | share |
|---|---|
| 2 | 0.195 |
| 3 | 0.173 |
| 4 | 0.046 |

### sudden_max_runup

| sudden_max_runup | sudden_share | gradual_share |
|---|---|---|
| 3 | 0.709 | 0.167 |
| 4 | 0.778 | 0.098 |
| 5 | 0.847 | 0.029 |

### established_min

| established_min | established | early_life |
|---|---|---|
| 12 | 0.519 | 0.033 |
| 18 | 0.482 | 0.070 |
| 24 | 0.439 | 0.113 |
| 36 | 0.354 | 0.198 |

### partial_payer_test

| partial_min_paid_rate | share | still_partial_next_month | stability_of_fixed_states | stability_of_fixed_states_without_q3 |
|---|---|---|---|---|
| 0.340 | 0.197 | 0.743 | 0.910 | 0.984 |
| 0.500 | 0.179 | 0.638 | 0.911 | 0.984 |
| 0.670 | 0.082 | 0.409 | 0.957 | 0.984 |

## 7. Clustering the residual (after bust-out and holding) — agreement (ARI) with each option

| k | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|
| 2 | -0.065 | 0.441 | 0.418 |
| 3 | 0.309 | 0.647 | 0.655 |
| 4 | 0.187 | 0.461 | 0.465 |
| 5 | 0.306 | 0.562 | 0.588 |
| 6 | 0.112 | 0.316 | 0.337 |
| 7 | 0.101 | 0.289 | 0.308 |
| 8 | 0.156 | 0.349 | 0.369 |

## 8. Most common journey shapes and motifs

Shapes (N clean, R roll, H hold = paid one month, P paid 2+ months; run lengths banded):

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3863 | sudden_established | 1.000 | 0.193 | 0.193 |
| N13-24 R3+ | 827 | sudden_established | 1.000 | 0.041 | 0.234 |
| N25+ R3+ H1 | 334 | sudden_established | 1.000 | 0.017 | 0.251 |
| N7-12 R3+ | 315 | sudden_early_life | 0.660 | 0.016 | 0.267 |
| N2-3 R3+ | 283 | bust_out | 0.905 | 0.014 | 0.281 |
| R1 P1 R3+ | 273 | bust_out | 1.000 | 0.014 | 0.295 |
| N25+ R3+ H1 R1 | 257 | sudden_established | 1.000 | 0.013 | 0.308 |
| N25+ R2 P1 R3+ | 257 | gradual_decline | 0.930 | 0.013 | 0.320 |
| R3+ | 196 | bust_out | 1.000 | 0.010 | 0.330 |
| N25+ R1 H1 R3+ | 179 | gradual_decline | 1.000 | 0.009 | 0.339 |
| N1 R3+ | 174 | bust_out | 1.000 | 0.009 | 0.348 |
| N25+ R3+ H1 R2 | 165 | sudden_established | 1.000 | 0.008 | 0.356 |
| N25+ R3+ P1 R3+ | 156 | sudden_established | 1.000 | 0.008 | 0.364 |
| N25+ R3+ P1 R1 | 139 | sudden_established | 1.000 | 0.007 | 0.371 |
| N4-6 R3+ | 135 | sudden_early_life | 1.000 | 0.007 | 0.378 |
| N25+ R3+ P1 R2 | 134 | sudden_established | 1.000 | 0.007 | 0.384 |
| N25+ R2 P1 R2 | 112 | gradual_decline | 1.000 | 0.006 | 0.390 |
| N25+ R1 H1 R1 H1 R3+ | 111 | gradual_decline | 1.000 | 0.006 | 0.395 |
| N25+ R2 H1 R3+ | 99 | gradual_decline | 1.000 | 0.005 | 0.400 |
| N25+ R2 P1 H1 R3+ | 89 | gradual_decline | 1.000 | 0.004 | 0.405 |

4-grams by lift vs shuffled order:

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.091 | 101.111 | relapse | 0.720 |
| HHPP | 0.024 | 69.429 | relapse | 0.957 |
| RHPP | 0.022 | 39.545 | relapse | 0.979 |
| HHPN | 0.070 | 33.357 | relapse | 0.707 |
| RHRH | 0.100 | 32.323 | relapse | 0.521 |
| HRPP | 0.016 | 28.727 | relapse | 0.867 |
| RHRP | 0.050 | 26.757 | relapse | 0.705 |
| RRPH | 0.044 | 23.892 | gradual_decline | 0.353 |
| HRHP | 0.030 | 21.889 | relapse | 0.905 |
| RRHH | 0.077 | 19.935 | relapse | 0.426 |
| RPRP | 0.089 | 19.878 | sudden_established | 0.378 |
| RRRH | 0.184 | 19.742 | sudden_established | 0.533 |
| HPPN | 0.042 | 17.915 | relapse | 0.990 |
| RRHR | 0.146 | 16.636 | sudden_established | 0.371 |
| RRHP | 0.041 | 16.300 | relapse | 0.801 |
