# Self-test on synthetic data — 20261016

Fake axis columns; real-data code path.

## 0. Expectation checks

| id | status | check | observed | expected | why | if_not_met |
|---|---|---|---|---|---|---|
| E01 | PASS | Every account gets exactly one state (all options) | True | True | The tree has a default branch, so it is MECE by construction. | A code or data-type bug — stop and fix before reading anything else. |
| E02 | PASS | Share of DPD strings that cannot be parsed | 0.000 | <= 2% | Strings should be digits once CHAR_MAP / STRIP_CHARS are set. | Inspect the non-digit characters; extend CHAR_MAP or STRIP_CHARS in config.py. |
| E03 | PASS | Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation) | 0.015 | <= 7pp | Confirms the string orientation and the backtest reconstruction are right. | Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine (survivor-only data shows roll rates that are too low). |
| E04 | PASS | Share of histories that start inside the current spell (no clean month seen) | 0.000 | <= 10% | Full history is available for everyone. | Strings are truncated; bust-out (short history) will be over-assigned — cap the bust-out rule to accounts with full history or raise the threshold. |
| E05 | PASS | Share of accounts with an unrepaired +2 jump | 0.003 | <= 2% | Billing-cycle jumps are mostly next to a hold and get repaired. | Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding. |
| E06 | PASS | Current bucket mix declines from 4 to 7 | 0.079 | >= 0 | Flow-driven book with rising roll rates (synthetic 29/26/23/22%). | Check the spine filter and whether a cohort shock is passing through. |
| E07 | PASS | One spell only, spell counted from bucket 3 | 0.825 | 78–92% | Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one near 85%, the bank counts spells from 4. | Set relapse_min_prior_peak to whichever spell definition matches the bank's 85%. |
| E08 | PASS | Bust-out share (today) | 0.058 | 4–8% | Bank's own rule gives ~6% (synthetic 5.8%). | Move bust_max_history along the sweep until the share matches the bank's rule. |
| E09 | PASS | Holding share (today) | 0.066 | 4–9% | Bank's own stabilized rule gives ~6% (synthetic 6.6%). | Compare with the bank's implementation of the 5-of-6 rule (E10/E11). |
| E10 | PASS | Recall of the bank's existing bust-out flag | 0.941 | >= 80% | Same concept; thresholds may differ slightly. | Read the bank's rule and align bust_max_history / the prior-peak guard. |
| E11 | PASS | Recall of the bank's existing stabilized flag | 0.922 | >= 90% | Holding IS the bank's 5-of-6 rule; only bust-out-first ordering differs. | Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today). |
| E12 | PASS | Holding separates risk: weighted next-month roll of fixed states minus holding | 0.431 | >= 20pp | Synthetic: holding 44% vs ~85% for the rest. | Holding is not behaving as 'stable'; check payment holidays / restructuring flags (E21) and try hold_min_in_band = 6. |
| E13 | PASS | Fixed states keep their state next month (minimum over fixed states) | 0.974 | >= 95% | Run-up and history are fixed once past 4 (synthetic 98–100%). | A feature is drifting with time since 4 — inspect which state leaks and why. |
| E14 | PASS | Holding persistence next month | 0.628 | 45–85% | Holding is current behaviour; it should persist but not forever (synthetic 60%). | Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments. |
| E15 | PASS | Option A: sudden share | 0.700 | 55–80% | Most accounts roll straight 2-3-4 (synthetic 70%). | If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting gradual. |
| E16 | PASS | Every option-B state holds at least 5% of the spine | 0.058 | >= 5% | Synthetic minimum 5.8% (bust-out). | Merge the small state into its neighbour (relapse→sudden, early_life→established). |
| E17 | PASS | Option C: smaller of gradual_slide / gradual_fought_back | 0.064 | >= 4% | Synthetic 10% / 6%. | Too small to act on — use option B. |
| E18 | PASS | Holding sits low in the spine: share at bucket 4 / share at bucket 7 | 19.157 | >= 2x | 90–95% roll rates at 6–7 leave little room to hold there. | Holders at 6–7 are unusual — check for frozen buckets (payment holidays). |
| E19 | PASS | Orthogonality: credibility score explained by the states (eta²) | 0.191 | <= 0.25 | Known overlap via holding (money in) and relapse (clean point), but the states should not reproduce the score. | Use option A (drops relapse) or report holding under credibility instead. |
| E20 | PASS | Orthogonality: ability score explained by the states (eta²) | 0.000 | <= 0.10 | DPD shape should carry little of salary/inflow/CASA. | Sudden vs gradual may be a proxy for income loss — fine, but say so in the persona grid. |
| E21 | PASS | Holders with money coming in (credibility component or DPD proxy) | 1.000 | >= 90% | Holding = paid one month's due most months, so money must be coming in (synthetic 100%). | Holders without money in are frozen buckets (holiday/restructure) — exclude those months. |
| E22 | PASS | Residual clusters agree more with option B than with A (ARI gain at k=6) | 0.388 | >= 0.15 | Synthetic: 0.55 (B) vs 0.16 (A) — the data has more than two residual groups. | The extra B splits are not natural groups in this book — prefer option A. |
| E23 | PASS | One paid month on the way down matters: gradual share at run-up<=4 / at <=3 | 0.600 | <= 0.70 | Synthetic 0.56: most gradual accounts held exactly once. | Gradual is driven by long run-ups, not single payments — keep 3 but review examples. |
| E24 | PASS | Partial payer stays rejected: share still partial next month at 0.5 | 0.636 | <= 75% | Synthetic 63%: unstable current-behaviour state. | If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'. |
| E25 | INFO | INFO — spread of exit-within-k across fixed states (option B) | 0.026 | report | Synthetic data cannot show this (same post-4 dynamics by construction). | >= 5pp means the mechanism carries risk information beyond holding. |

## 1. Data quality and population

| index | value |
|---|---|
| n_current_rows | 20000 |
| share_invalid_strings | 0.000 |
| n_current_spine_analysed | 20000 |
| string_length_p05_p50_p95 | [11, 53, 142] |
| share_left_censored | 0.000 |
| share_jump_repaired | 0.023 |
| share_jump_left | 0.003 |
| share_one_spell_from3 | 0.825 |
| share_one_spell_from4 | 0.949 |
| bucket_mix | {4: 0.29865, 5: 0.2539, 6: 0.22745, 7: 0.22} |

## 2. States today (current spine)

### A_minimal_4

Share:

| index | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.066 |
| sudden_decline | 0.700 |
| gradual_decline | 0.176 |

Mix by current bucket (column shares):

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.051 | 0.059 | 0.056 | 0.067 |
| holding | 0.134 | 0.070 | 0.030 | 0.007 |
| sudden_decline | 0.635 | 0.701 | 0.743 | 0.743 |
| gradual_decline | 0.180 | 0.169 | 0.171 | 0.183 |

### B_balanced_6

Share:

| index | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.066 |
| relapse | 0.168 |
| sudden_established | 0.350 |
| sudden_early_life | 0.197 |
| gradual_decline | 0.160 |

Mix by current bucket (column shares):

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.051 | 0.059 | 0.056 | 0.067 |
| holding | 0.134 | 0.070 | 0.030 | 0.007 |
| relapse | 0.149 | 0.179 | 0.177 | 0.173 |
| sudden_established | 0.324 | 0.344 | 0.372 | 0.372 |
| sudden_early_life | 0.180 | 0.194 | 0.209 | 0.212 |
| gradual_decline | 0.162 | 0.153 | 0.156 | 0.169 |

### C_detailed_7

Share:

| index | share |
|---|---|
| bust_out | 0.058 |
| holding | 0.066 |
| relapse | 0.168 |
| sudden_established | 0.350 |
| sudden_early_life | 0.197 |
| gradual_slide | 0.097 |
| gradual_fought_back | 0.064 |

Mix by current bucket (column shares):

| row_0 | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| bust_out | 0.051 | 0.059 | 0.056 | 0.067 |
| holding | 0.134 | 0.070 | 0.030 | 0.007 |
| relapse | 0.149 | 0.179 | 0.177 | 0.173 |
| sudden_established | 0.324 | 0.344 | 0.372 | 0.372 |
| sudden_early_life | 0.180 | 0.194 | 0.209 | 0.212 |
| gradual_slide | 0.099 | 0.093 | 0.095 | 0.100 |
| gradual_fought_back | 0.063 | 0.061 | 0.061 | 0.069 |

Examples (B_balanced_6, no keys):

| state | last_30_months_oldest_to_newest |
|---|---|
| bust_out | 002345 |
| bust_out | 002344556 |
| bust_out | 0234 |
| holding | 000000000000100000222223333344 |
| holding | 000001011000000234343123434234 |
| holding | 00000000000000234555655544 |
| relapse | 020002200000010000230000002345 |
| relapse | 001000000023434231231231112345 |
| relapse | 100000100000023000000000010234 |
| sudden_established | 000000000000000100000000023434 |
| sudden_established | 000000000000001000000000023456 |
| sudden_established | 000000010000000002000000123456 |
| sudden_early_life | 000000000000000000000002344456 |
| sudden_early_life | 0000000001000000000000000234 |
| sudden_early_life | 0110010100000000234 |
| gradual_decline | 000002000100000000000002323456 |
| gradual_decline | 0001000000002334567 |
| gradual_decline | 010000000000000000000002233456 |

## 3. Agreement with the bank's existing bust-out / stabilized rules

| index | their_share | our_share | recall_of_theirs | precision_vs_theirs |
|---|---|---|---|---|
| bust_out | 0.061 | 0.058 | 0.941 | 0.995 |
| holding | 0.071 | 0.066 | 0.922 | 0.995 |

## 4. Overlap with the other persona axes

Variance of each axis explained by the states (eta², 0 = orthogonal):

| index | A_minimal_4 | B_balanced_6 | C_detailed_7 |
|---|---|---|---|
| credibility_score | 0.116 | 0.191 | 0.193 |
| cred_ptp_points | 0.000 | 0.000 | 0.000 |
| cred_money_in_points | 0.174 | 0.167 | 0.170 |
| cred_clean_point | 0.040 | 0.844 | 0.844 |
| ability_score | 0.000 | 0.000 | 0.000 |
| reachable_flag | 0.000 | 0.000 | 0.000 |
| in_country_flag | 0.000 | 0.000 | 0.000 |

Mean of each axis by state (B_balanced_6):

| state | credibility_score | cred_ptp_points | cred_money_in_points | cred_clean_point | ability_score | reachable_flag | in_country_flag |
|---|---|---|---|---|---|---|---|
| bust_out | 2.336 | 0.739 | 0.599 | 0.998 | 49.490 | 0.685 | 0.833 |
| holding | 3.597 | 0.700 | 2.000 | 0.897 | 50.209 | 0.695 | 0.839 |
| relapse | 1.386 | 0.717 | 0.670 | 0.000 | 50.219 | 0.704 | 0.848 |
| sudden_established | 2.312 | 0.705 | 0.645 | 0.962 | 49.900 | 0.692 | 0.851 |
| sudden_early_life | 2.331 | 0.704 | 0.653 | 0.975 | 50.339 | 0.697 | 0.855 |
| gradual_decline | 2.931 | 0.713 | 1.220 | 0.997 | 50.351 | 0.694 | 0.860 |

Holding vs money coming in:

| index | value |
|---|---|
| source | cred_money_in_points |
| holders_with_money_in | 1.000 |
| non_holders_with_money_in | 0.443 |

## 5. Backtest — spine as of 6 months ago, outcomes since

20,000 accounts. Monthly roll rate by bucket (should match the bank's ~70/80/90/95%):

| b_now | roll_rate |
|---|---|
| 4 | 0.702 |
| 5 | 0.808 |
| 6 | 0.885 |
| 7 | 0.940 |

### A_minimal_4

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.060 | 1195 | 0.879 | 0.965 | 0.007 | 3.000 | 1.000 | 0.257 |
| holding | 0.065 | 1308 | 0.421 | 0.519 | 0.052 | 3.000 | 0.628 | 0.221 |
| sudden_decline | 0.708 | 14152 | 0.855 | 0.947 | 0.010 | 3.000 | 0.988 | 0.261 |
| gradual_decline | 0.167 | 3345 | 0.828 | 0.923 | 0.033 | 3.000 | 0.971 | 0.275 |

### B_balanced_6

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.060 | 1195 | 0.879 | 0.965 | 0.007 | 3.000 | 1.000 | 0.257 |
| holding | 0.065 | 1308 | 0.421 | 0.519 | 0.052 | 3.000 | 0.628 | 0.221 |
| relapse | 0.170 | 3407 | 0.851 | 0.943 | 0.023 | 3.000 | 0.989 | 0.267 |
| sudden_established | 0.352 | 7035 | 0.853 | 0.945 | 0.010 | 3.000 | 0.987 | 0.261 |
| sudden_early_life | 0.201 | 4022 | 0.851 | 0.942 | 0.010 | 3.000 | 0.984 | 0.264 |
| gradual_decline | 0.152 | 3033 | 0.843 | 0.939 | 0.021 | 3.000 | 0.974 | 0.267 |

### C_detailed_7

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| bust_out | 0.060 | 1195 | 0.879 | 0.965 | 0.007 | 3.000 | 1.000 | 0.257 |
| holding | 0.065 | 1308 | 0.421 | 0.519 | 0.052 | 3.000 | 0.628 | 0.221 |
| relapse | 0.170 | 3407 | 0.851 | 0.943 | 0.023 | 3.000 | 0.989 | 0.267 |
| sudden_established | 0.352 | 7035 | 0.853 | 0.945 | 0.010 | 3.000 | 0.987 | 0.261 |
| sudden_early_life | 0.201 | 4022 | 0.851 | 0.942 | 0.010 | 3.000 | 0.984 | 0.264 |
| gradual_slide | 0.092 | 1844 | 0.840 | 0.934 | 0.028 | 3.000 | 0.969 | 0.275 |
| gradual_fought_back | 0.059 | 1189 | 0.847 | 0.948 | 0.012 | 3.000 | 0.983 | 0.254 |

## 6. Threshold sweeps (backtest population)

### bust_max_history

| bust_max_history | share | exit_within_k |
|---|---|---|
| 3 | 0.029 | 0.992 |
| 6 | 0.060 | 0.965 |
| 9 | 0.083 | 0.959 |
| 12 | 0.103 | 0.954 |
| 18 | 0.146 | 0.941 |
| 24 | 0.193 | 0.937 |

### hold_min_in_band

| hold_min_in_band | share | roll_next_month | still_holding_next_month |
|---|---|---|---|
| 4 | 0.127 | 0.543 | 0.537 |
| 5 | 0.065 | 0.421 | 0.628 |
| 6 | 0.034 | 0.349 | 0.745 |

### relapse_min_prior_peak

| relapse_min_prior_peak | share |
|---|---|
| 2 | 0.190 |
| 3 | 0.170 |
| 4 | 0.049 |

### sudden_max_runup

| sudden_max_runup | sudden_share | gradual_share |
|---|---|---|
| 3 | 0.708 | 0.167 |
| 4 | 0.773 | 0.100 |
| 5 | 0.842 | 0.030 |

### established_min

| established_min | established | early_life |
|---|---|---|
| 24 | 0.436 | 0.117 |
| 36 | 0.352 | 0.201 |
| 48 | 0.271 | 0.282 |
| 60 | 0.202 | 0.351 |

### partial_payer_test

| partial_min_paid_rate | share | still_partial_next_month | stability_of_fixed_states | stability_of_fixed_states_without_q3 |
|---|---|---|---|---|
| 0.340 | 0.193 | 0.747 | 0.915 | 0.985 |
| 0.500 | 0.175 | 0.636 | 0.916 | 0.985 |
| 0.670 | 0.079 | 0.405 | 0.957 | 0.985 |

## 7. Clustering the residual (after bust-out and holding) — agreement (ARI) with each option

| k | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|
| 2 | -0.065 | 0.280 | 0.259 |
| 3 | 0.300 | 0.410 | 0.420 |
| 4 | 0.188 | 0.349 | 0.356 |
| 5 | 0.183 | 0.334 | 0.363 |
| 6 | 0.163 | 0.551 | 0.583 |
| 7 | 0.103 | 0.521 | 0.553 |
| 8 | 0.160 | 0.587 | 0.621 |

## 8. Most common journey shapes and motifs

Shapes (N clean, R roll, H hold = paid one month, P paid 2+ months; run lengths banded):

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3763 | sudden_established | 0.814 | 0.188 | 0.188 |
| N13-24 R3+ | 815 | sudden_early_life | 1.000 | 0.041 | 0.229 |
| N7-12 R3+ | 357 | sudden_early_life | 1.000 | 0.018 | 0.247 |
| N25+ R3+ H1 | 317 | sudden_established | 0.830 | 0.016 | 0.263 |
| N2-3 R3+ | 249 | bust_out | 1.000 | 0.012 | 0.275 |
| N4-6 R3+ | 246 | bust_out | 0.691 | 0.012 | 0.287 |
| N25+ R2 P1 R3+ | 236 | gradual_decline | 0.936 | 0.012 | 0.299 |
| N25+ R3+ H1 R1 | 229 | sudden_established | 0.821 | 0.011 | 0.311 |
| N25+ R3+ P1 R3+ | 177 | sudden_established | 0.819 | 0.009 | 0.319 |
| N25+ R3+ H1 R2 | 152 | sudden_established | 0.836 | 0.008 | 0.327 |
| N25+ R1 H1 R3+ | 139 | gradual_decline | 1.000 | 0.007 | 0.334 |
| N1 R3+ | 137 | bust_out | 1.000 | 0.007 | 0.341 |
| N25+ R3+ P1 R2 | 135 | sudden_established | 0.904 | 0.007 | 0.348 |
| R3+ | 132 | bust_out | 1.000 | 0.007 | 0.354 |
| N25+ R2 P1 R2 | 128 | gradual_decline | 1.000 | 0.006 | 0.361 |
| N25+ R3+ P1 R1 | 127 | sudden_established | 0.772 | 0.006 | 0.367 |
| N25+ R2 H1 R1 | 111 | gradual_decline | 1.000 | 0.006 | 0.373 |
| N25+ R2 P1 H1 R3+ | 103 | gradual_decline | 1.000 | 0.005 | 0.378 |
| N25+ R2 H1 R3+ | 100 | gradual_decline | 1.000 | 0.005 | 0.383 |
| N25+ R1 H1 R2 | 88 | gradual_decline | 1.000 | 0.004 | 0.387 |

4-grams by lift vs shuffled order:

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| HHPP | 0.022 | 108.750 | relapse | 0.972 |
| RHHP | 0.089 | 99.389 | relapse | 0.731 |
| HRPP | 0.017 | 56.000 | relapse | 0.881 |
| HRHP | 0.030 | 46.308 | relapse | 0.890 |
| RHRH | 0.098 | 37.577 | relapse | 0.531 |
| HHPN | 0.070 | 33.429 | relapse | 0.721 |
| RRRH | 0.179 | 25.564 | sudden_established | 0.351 |
| RPRP | 0.091 | 22.444 | relapse | 0.366 |
| RRHH | 0.071 | 21.455 | relapse | 0.447 |
| RRPH | 0.046 | 21.136 | gradual_decline | 0.355 |
| RRHP | 0.041 | 20.897 | relapse | 0.821 |
| RHRP | 0.054 | 20.547 | relapse | 0.684 |
| HPPN | 0.039 | 19.600 | relapse | 0.991 |
| RPRH | 0.035 | 18.684 | relapse | 0.358 |
| RPHR | 0.041 | 17.277 | gradual_decline | 0.411 |
