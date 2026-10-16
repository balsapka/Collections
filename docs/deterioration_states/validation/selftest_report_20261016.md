# Self-test on synthetic data — 20261016

Fake axis columns; real-data code path.

## 0a. Edge cases (oldest → newest, option B)

```
OK   0 2 0 2 3 4                    -> early_payment_default       3 months incl. one blip, then straight roll
OK   0 0 0 2 3 4                    -> early_payment_default       3 clean months, straight roll
OK   0 2 3 4 5                      -> early_payment_default       1 clean month
OK   0 0 2 0 2 3 4                  -> straight_roller_early_life  4 months of history: too long for EPD
OK   0 0 0 0 0 0 2 3 4              -> straight_roller_early_life  6 clean months: early-life default, not EPD
OK   0 2 0 2 0 2 3 4                -> straight_roller_early_life  two blips: not EPD
OK   0 2 3 4 0 0 2 3 4 5 6          -> repeat_delinquent           paid off from 4, then relapsed
OK   0 0 2 2 3 4                    -> slow_roller                 held once on the way down
OK   0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4 5 -> stabilized                  staircase holding at 4 then one step
OK   000000000000002345             -> straight_roller_seasoned    14 clean months, straight roll
OK   0000000000000234444567         -> straight_roller_seasoned    held at 4, then rolled 3 buckets: not stable
OK   0000000000000023455555         -> stabilized                  holding at 5
OK   00000000234443345433456554     -> stabilized                  oscillating payer (example 1)
OK   00000000234443345433456654     -> stabilized                  oscillating payer that just paid down 6-5-4 (example 2)
```

## 0. Expectation checks

| id | status | check | observed | expected | why | if_not_met |
|---|---|---|---|---|---|---|
| E01 | PASS | Every account gets exactly one state (all options) | True | True | The tree has a default branch, so it is MECE by construction. | A code or data-type bug — stop and fix before reading anything else. |
| E02 | PASS | Share of DPD strings that cannot be parsed | 0.000 | <= 2% | Strings should be digits once CHAR_MAP / STRIP_CHARS are set. | Inspect the non-digit characters; extend CHAR_MAP or STRIP_CHARS in config.py. |
| E03 | PASS | Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation) | 0.015 | <= 7pp | Confirms the string orientation and the backtest reconstruction are right. | Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine (survivor-only data shows roll rates that are too low). |
| E04 | PASS | Share of histories that start inside the current spell (no clean month seen) | 0.000 | <= 10% | Full history is available for everyone. | Strings are truncated; EPD (short history) will be over-assigned — cap the EPD rule to accounts with full history or raise the threshold. |
| E05 | PASS | Share of accounts with an unrepaired +2 jump | 0.003 | <= 2% | Billing-cycle jumps are mostly next to a hold and get repaired. | Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding. |
| E06 | PASS | Current bucket mix declines from 4 to 7 | 0.077 | >= 0 | Flow-driven book with rising roll rates (synthetic 29/26/23/22%). | Check the spine filter and whether a cohort shock is passing through. |
| E07 | PASS | One spell only, spell counted from bucket 3 | 0.825 | 78–92% | Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one near 85%, the bank counts spells from 4. | Set repeat_min_prior_peak to whichever spell definition matches the bank's 85%. |
| E08 | PASS | Early payment default (EPD, 'bust-out') share (today) | 0.058 | 4–8% | Bank's own rule gives ~6% (synthetic 5.8%). | Move epd_max_history along the sweep until the share matches the bank's rule. |
| E09 | PASS | Stabilized share (today) | 0.083 | 4–9% | Bank's own stabilized rule gives ~6% (synthetic 6.6%). | Compare with the bank's implementation of the 5-of-6 rule (E10/E11). |
| E10 | PASS | Recall of the bank's existing bust-out (EPD) flag | 0.926 | >= 80% | Same concept; thresholds may differ slightly. | Read the bank's rule and align epd_max_history / epd_max_blips. |
| E11 | PASS | Recall of the bank's existing stabilized flag | 0.933 | >= 90% | Stabilized IS the bank's 5-of-6 rule; only EPD-first ordering differs. | Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today). |
| E12 | PASS | Stabilized separates risk: weighted next-month roll of fixed states minus stabilized | 0.384 | >= 20pp | Synthetic: stabilized 40% vs ~85% for the rest. | Stabilized is not behaving as 'stable'; check payment holidays / restructuring flags (E21) and try stabilized_min_in_band = 6. |
| E13 | PASS | Fixed states keep their state next month (minimum over fixed states) | 0.980 | >= 95% | Run-up and history are fixed once past 4 (synthetic 98–100%). | A feature is drifting with time since 4 — inspect which state leaks and why. |
| E14 | PASS | Stabilized persistence next month | 0.644 | 45–85% | Stabilized is current behaviour; it should persist but not forever (synthetic 62%). | Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments. |
| E15 | PASS | Option A: straight-roller share | 0.690 | 55–80% | Most accounts roll straight 2-3-4 (synthetic 70%). | If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting slow roller. |
| E16 | WARN | Every option-B state holds at least 5% of the spine | 0.030 | >= 5% | Actionable size. Synthetic: straight_roller_early_life 3.4% under the 12-month seasoned cut (depends on the book's tenure mix). | Merge the small state into its neighbour (repeat_delinquent→straight_roller, early-life→seasoned), or move seasoned_min_months along its sweep (12 → 18 → 24 months). |
| E17 | PASS | Option C: smaller of intermittent / erratic payer (slow-roller split) | 0.065 | >= 4% | Synthetic 10% / 6%. | Too small to act on — use option B. |
| E18 | PASS | Stabilized sits low in the spine: share at bucket 4 / share at bucket 7 | 30.554 | >= 2x | 90–95% roll rates at 6–7 leave little room to hold there. | Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays). |
| E19 | PASS | Orthogonality: credibility score explained by the states (eta²) | 0.193 | <= 0.25 | Known overlap via stabilized (money in) and repeat delinquent (clean point), but the states should not reproduce the score. | Use option A (drops repeat delinquent) or report stabilized under credibility instead. |
| E19b | WARN | Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²) | 0.810 | <= 0.50 | Repeat delinquent is defined from earlier spells — the same history the clean point scores. Synthetic (with a clean point = 'no earlier spell'): 0.84 → WARN. | Repeat delinquent duplicates the credibility clean point: use option A, or keep it and tell the persona grid it is the same signal (it is only 1 of credibility's 5 points). |
| E20 | PASS | Orthogonality: ability score explained by the states (eta²) | 0.001 | <= 0.10 | DPD shape should carry little of salary/inflow/CASA. | Straight vs slow roller may be a proxy for income loss — fine, but say so in the persona grid. |
| E21 | PASS | Stabilized accounts with money coming in (credibility component or DPD proxy) | 0.983 | >= 90% | Stabilized = paid one month's due most months, so money must be coming in (synthetic 100%). | Stabilized accounts without money in are frozen buckets (holiday/restructure) — exclude those months. |
| E22 | PASS | Residual clusters agree more with option B than with A (ARI gain at k=6) | 0.206 | >= 0.15 | Synthetic at k=6: 0.32 (B) vs 0.11 (A) — the data has more than two residual groups. | The extra B splits are not natural groups in this book — prefer option A. |
| E23 | PASS | One paid month on the way down matters: slow-roller share at run-up<=4 / at <=3 | 0.580 | <= 0.70 | Synthetic ~0.58: most slow rollers held exactly once. | Slow roller is driven by long run-ups, not single payments — keep 3 but review examples. |
| E24 | PASS | 'Paying since 4' stays rejected: share still in it next month at 0.5 | 0.608 | <= 75% | Synthetic 63%: unstable current-behaviour state. | If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'. |
| E26 | PASS | Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months | 0.041 | <= 10% | Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating payers bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold) and swingers in their first 6 months at 4 (both rules are reported). | Too many accounts bounce: look at examples; consider stabilized_long_run_max_rise = 2 or a sticky rule — but both widen the definition, so agree it with the business. |
| E25 | INFO | INFO — spread of exit-within-k across fixed states (option B) | 0.041 | report | Synthetic data cannot show this (same post-4 dynamics by construction). | >= 5pp means the mechanism carries risk information beyond stabilized. |

## State names

| code | display name | remark |
|---|---|---|
| early_payment_default | Early payment default (EPD) | Never really paid: defaulted within the first three payments. Called 'bust-out' internally — but classic bust-out fraud (good history, limit build-up, then max-out) shows as a seasoned straight roller and needs a fraud overlay on spend data. |
| stabilized | Stabilized | The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months in buckets 4+, at most one bucket higher than 6 months ago) so oscillating payers and accounts that just paid down are not mislabelled. |
| paying_since_4 | Paying since bucket 4 (tested, not used) | Rejected — current-behaviour state that belongs to credibility (money coming in). |
| repeat_delinquent | Repeat delinquent (re-default) | Re-default after a cured spell; collections 'recidivism'. |
| straight_roller | Straight roller | Rolled through every bucket without paying. |
| straight_roller_seasoned | Seasoned straight roller | Straight roller after at least a year on book (seasoned). |
| straight_roller_early_life | Early-life straight roller | Straight roller in the first year on book (early-life default). |
| slow_roller | Slow roller (partial payer) | Paid something on the way down but kept rolling. Also called partial payer. |
| slow_roller_intermittent | Intermittent payer | Slow roller that paid one month here and there. |
| slow_roller_erratic | Erratic payer | Slow roller that caught up 2+ months at once, then rolled again. |

## 1. Data quality and population

| metric | value |
|---|---|
| n_current_rows | 5000 |
| share_invalid_strings | 0.000 |
| n_current_spine_analysed | 5000 |
| string_length_p05_p50_p95 | [9, 54, 141] |
| share_left_censored | 0.000 |
| share_jump_repaired | 0.020 |
| share_jump_left | 0.003 |
| share_one_spell_from3 | 0.825 |
| share_one_spell_from4 | 0.954 |
| bucket_mix | {4: 0.2922, 5: 0.2558, 6: 0.2368, 7: 0.2152} |

## 2. States today (current spine)

### A_minimal_4

Share:

| state | share |
|---|---|
| early_payment_default | 0.058 |
| stabilized | 0.083 |
| straight_roller | 0.690 |
| slow_roller | 0.169 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.045 | 0.065 | 0.062 | 0.062 |
| stabilized | 0.171 | 0.088 | 0.041 | 0.006 |
| straight_roller | 0.639 | 0.686 | 0.718 | 0.734 |
| slow_roller | 0.144 | 0.162 | 0.180 | 0.198 |

### B_balanced_6

Share:

| state | share |
|---|---|
| early_payment_default | 0.058 |
| stabilized | 0.083 |
| repeat_delinquent | 0.164 |
| straight_roller_seasoned | 0.508 |
| straight_roller_early_life | 0.030 |
| slow_roller | 0.157 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.045 | 0.065 | 0.062 | 0.062 |
| stabilized | 0.171 | 0.088 | 0.041 | 0.006 |
| repeat_delinquent | 0.167 | 0.147 | 0.177 | 0.165 |
| straight_roller_seasoned | 0.467 | 0.508 | 0.528 | 0.543 |
| straight_roller_early_life | 0.021 | 0.038 | 0.030 | 0.033 |
| slow_roller | 0.129 | 0.155 | 0.164 | 0.191 |

### C_detailed_7

Share:

| state | share |
|---|---|
| early_payment_default | 0.058 |
| stabilized | 0.083 |
| repeat_delinquent | 0.164 |
| straight_roller_seasoned | 0.508 |
| straight_roller_early_life | 0.030 |
| slow_roller_intermittent | 0.092 |
| slow_roller_erratic | 0.065 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.045 | 0.065 | 0.062 | 0.062 |
| stabilized | 0.171 | 0.088 | 0.041 | 0.006 |
| repeat_delinquent | 0.167 | 0.147 | 0.177 | 0.165 |
| straight_roller_seasoned | 0.467 | 0.508 | 0.528 | 0.543 |
| straight_roller_early_life | 0.021 | 0.038 | 0.030 | 0.033 |
| slow_roller_intermittent | 0.073 | 0.091 | 0.101 | 0.111 |
| slow_roller_erratic | 0.056 | 0.064 | 0.063 | 0.080 |

Examples (B_balanced_6, no keys):

| state | last_30_months_oldest_to_newest |
|---|---|
| early_payment_default | 0234567 |
| early_payment_default | 00234 |
| early_payment_default | 00234545 |
| stabilized | 000000001000002311111112343234 |
| stabilized | 000000002000000000022222233344 |
| stabilized | 000000123443334544444444445555 |
| repeat_delinquent | 000000000023000223332000102245 |
| repeat_delinquent | 001000001002342342342311123456 |
| repeat_delinquent | 000000000000222000000000023455 |
| straight_roller_seasoned | 000000000002010000000000234345 |
| straight_roller_seasoned | 010000000000001000000000023445 |
| straight_roller_seasoned | 000000000000000000000100002345 |
| straight_roller_early_life | 0000000000023433456 |
| straight_roller_early_life | 000000023423423234233345567 |
| straight_roller_early_life | 00002345 |
| slow_roller | 000000100000000000000023234455 |
| slow_roller | 020000020000000000001000232234 |
| slow_roller | 000000000000000000023234 |

## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules

| state | their_share | our_share | recall_of_theirs | precision_vs_theirs |
|---|---|---|---|---|
| early_payment_default | 0.062 | 0.058 | 0.926 | 0.993 |
| stabilized | 0.078 | 0.083 | 0.933 | 0.870 |

## 4. Overlap with the other persona axes

Variance of each axis explained by the states (eta², 0 = orthogonal):

| axis | A_minimal_4 | B_balanced_6 | C_detailed_7 |
|---|---|---|---|
| credibility_score | 0.113 | 0.193 | 0.195 |
| cred_ptp_points | 0.000 | 0.000 | 0.000 |
| cred_money_in_points | 0.179 | 0.174 | 0.178 |
| cred_clean_point | 0.045 | 0.810 | 0.810 |
| ability_score | 0.001 | 0.001 | 0.001 |
| reachable_flag | 0.000 | 0.000 | 0.001 |
| in_country_flag | 0.003 | 0.003 | 0.003 |

Mean of each axis by state (B_balanced_6):

| state | credibility_score | cred_ptp_points | cred_money_in_points | cred_clean_point | ability_score | reachable_flag | in_country_flag |
|---|---|---|---|---|---|---|---|
| early_payment_default | 2.228 | 0.654 | 0.574 | 1.000 | 50.286 | 0.671 | 0.844 |
| stabilized | 3.502 | 0.678 | 1.966 | 0.858 | 48.944 | 0.709 | 0.853 |
| repeat_delinquent | 1.331 | 0.670 | 0.661 | 0.000 | 50.589 | 0.703 | 0.852 |
| straight_roller_seasoned | 2.335 | 0.699 | 0.675 | 0.961 | 50.463 | 0.713 | 0.835 |
| straight_roller_early_life | 2.362 | 0.718 | 0.651 | 0.993 | 49.662 | 0.698 | 0.859 |
| slow_roller | 2.875 | 0.700 | 1.179 | 0.996 | 49.759 | 0.709 | 0.888 |

Stabilized vs money coming in:

| metric | value |
|---|---|
| source | cred_money_in_points |
| stabilized_with_money_in | 0.983 |
| others_with_money_in | 0.446 |

## 5. Backtest — spine as of 6 months ago, outcomes since

5,000 accounts. Monthly roll rate by bucket (should match the bank's ~70/80/90/95%):

| bucket | roll_rate |
|---|---|
| 4 | 0.715 |
| 5 | 0.785 |
| 6 | 0.896 |
| 7 | 0.943 |

### A_minimal_4

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.058 | 288 | 0.878 | 0.976 | 0.000 | 3.000 | 1.000 | 0.274 |
| stabilized | 0.075 | 374 | 0.471 | 0.567 | 0.037 | 3.000 | 0.644 | 0.182 |
| straight_roller | 0.690 | 3452 | 0.853 | 0.953 | 0.011 | 3.000 | 0.983 | 0.260 |
| slow_roller | 0.177 | 886 | 0.854 | 0.928 | 0.038 | 3.000 | 0.978 | 0.292 |

### B_balanced_6

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.058 | 288 | 0.878 | 0.976 | 0.000 | 3.000 | 1.000 | 0.274 |
| stabilized | 0.075 | 374 | 0.471 | 0.567 | 0.037 | 3.000 | 0.644 | 0.182 |
| repeat_delinquent | 0.162 | 812 | 0.849 | 0.945 | 0.018 | 3.000 | 0.980 | 0.273 |
| straight_roller_seasoned | 0.510 | 2549 | 0.850 | 0.952 | 0.011 | 3.000 | 0.982 | 0.262 |
| straight_roller_early_life | 0.032 | 162 | 0.877 | 0.963 | 0.006 | 3.000 | 0.992 | 0.235 |
| slow_roller | 0.163 | 815 | 0.864 | 0.935 | 0.033 | 3.000 | 0.980 | 0.277 |

### C_detailed_7

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.058 | 288 | 0.878 | 0.976 | 0.000 | 3.000 | 1.000 | 0.274 |
| stabilized | 0.075 | 374 | 0.471 | 0.567 | 0.037 | 3.000 | 0.644 | 0.182 |
| repeat_delinquent | 0.162 | 812 | 0.849 | 0.945 | 0.018 | 3.000 | 0.980 | 0.273 |
| straight_roller_seasoned | 0.510 | 2549 | 0.850 | 0.952 | 0.011 | 3.000 | 0.982 | 0.262 |
| straight_roller_early_life | 0.032 | 162 | 0.877 | 0.963 | 0.006 | 3.000 | 0.992 | 0.235 |
| slow_roller_intermittent | 0.102 | 510 | 0.841 | 0.920 | 0.043 | 3.000 | 0.970 | 0.284 |
| slow_roller_erratic | 0.061 | 305 | 0.902 | 0.961 | 0.016 | 3.000 | 0.996 | 0.266 |

### Stabilized bounce-backs over the 6 backtest months (5,000 accounts)

Share of ever-stabilized accounts that left stabilized and came back while staying in the spine (S . S):

| stabilized rule | ever_stabilized | bounce_back_share_of_ever_stabilized | mean_status_changes_per_account |
|---|---|---|---|
| with_long_run_clause | 0.122 | 0.041 | 0.113 |
| bank_rule_only | 0.113 | 0.049 | 0.113 |

## 6. Threshold sweeps (backtest population)

### epd_max_history

| epd_max_history | share | exit_within_k |
|---|---|---|
| 2 | 0.025 | 0.992 |
| 3 | 0.058 | 0.976 |
| 4 | 0.059 | 0.976 |
| 6 | 0.070 | 0.971 |
| 9 | 0.081 | 0.966 |
| 12 | 0.096 | 0.965 |

### stabilized_min_in_band

| stabilized_min_in_band | share | roll_next_month | still_stabilized_next_month |
|---|---|---|---|
| 4 | 0.132 | 0.572 | 0.556 |
| 5 | 0.075 | 0.471 | 0.644 |
| 6 | 0.049 | 0.421 | 0.699 |

### repeat_min_prior_peak

| repeat_min_prior_peak | share |
|---|---|
| 2 | 0.183 |
| 3 | 0.162 |
| 4 | 0.045 |

### straight_max_runup

| straight_max_runup | straight_share | slow_share |
|---|---|---|
| 3 | 0.690 | 0.177 |
| 4 | 0.765 | 0.103 |
| 5 | 0.837 | 0.030 |

### seasoned_min_months

| seasoned_min_months | seasoned | early_life |
|---|---|---|
| 12 | 0.510 | 0.032 |
| 18 | 0.472 | 0.070 |
| 24 | 0.431 | 0.112 |
| 36 | 0.343 | 0.200 |

### paying_since_4_test

| paying_since_4_min_rate | share | still_paying_since_4_next_month | stability_of_fixed_states | stability_of_fixed_states_without_q3 |
|---|---|---|---|---|
| 0.340 | 0.192 | 0.719 | 0.906 | 0.983 |
| 0.500 | 0.174 | 0.608 | 0.909 | 0.983 |
| 0.670 | 0.070 | 0.336 | 0.956 | 0.983 |

## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with each option

| k | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|
| 2 | -0.074 | 0.439 | 0.414 |
| 3 | 0.297 | 0.646 | 0.656 |
| 4 | 0.189 | 0.474 | 0.480 |
| 5 | 0.183 | 0.463 | 0.491 |
| 6 | 0.112 | 0.318 | 0.340 |
| 7 | 0.105 | 0.297 | 0.318 |
| 8 | 0.160 | 0.359 | 0.381 |

## 8. Most common journey shapes and motifs

Shapes (N clean, R roll, H hold = paid one month, P paid 2+ months; run lengths banded):

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 906 | straight_roller_seasoned | 1.000 | 0.181 | 0.181 |
| N13-24 R3+ | 192 | straight_roller_seasoned | 1.000 | 0.038 | 0.220 |
| N25+ R3+ H1 | 81 | straight_roller_seasoned | 1.000 | 0.016 | 0.236 |
| N2-3 R3+ | 74 | early_payment_default | 0.919 | 0.015 | 0.251 |
| N7-12 R3+ | 72 | straight_roller_early_life | 0.625 | 0.014 | 0.265 |
| N25+ R2 P1 R3+ | 68 | slow_roller | 0.941 | 0.014 | 0.279 |
| N25+ R3+ H1 R1 | 66 | straight_roller_seasoned | 1.000 | 0.013 | 0.292 |
| R1 P1 R3+ | 63 | early_payment_default | 1.000 | 0.013 | 0.304 |
| N25+ R3+ H1 R2 | 52 | straight_roller_seasoned | 1.000 | 0.010 | 0.315 |
| N1 R3+ | 49 | early_payment_default | 1.000 | 0.010 | 0.325 |
| R3+ | 48 | early_payment_default | 1.000 | 0.010 | 0.334 |
| N25+ R1 H1 R3+ | 45 | slow_roller | 1.000 | 0.009 | 0.343 |
| N25+ R3+ P1 R3+ | 40 | straight_roller_seasoned | 1.000 | 0.008 | 0.351 |
| N25+ R3+ P1 R2 | 35 | straight_roller_seasoned | 1.000 | 0.007 | 0.358 |
| N4-6 R3+ | 32 | straight_roller_early_life | 1.000 | 0.006 | 0.365 |
| N25+ R3+ P1 R1 | 27 | straight_roller_seasoned | 1.000 | 0.005 | 0.370 |
| N25+ R2 H1 R1 | 25 | slow_roller | 1.000 | 0.005 | 0.375 |
| N25+ R2 H1 R3+ | 22 | slow_roller | 1.000 | 0.004 | 0.379 |
| N25+ R2 H1 R2 | 20 | slow_roller | 1.000 | 0.004 | 0.383 |
| N13-24 R3+ H1 R1 | 20 | straight_roller_seasoned | 1.000 | 0.004 | 0.387 |

4-grams by lift vs shuffled order:

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.095 | 94.600 | repeat_delinquent | 0.721 |
| HRHP | 0.030 | 50.667 | repeat_delinquent | 0.875 |
| RRPH | 0.047 | 47.000 | slow_roller | 0.379 |
| RHPP | 0.023 | 38.333 | repeat_delinquent | 0.922 |
| HHPP | 0.021 | 34.667 | repeat_delinquent | 0.913 |
| RHRH | 0.095 | 31.667 | repeat_delinquent | 0.526 |
| HRPP | 0.019 | 31.333 | repeat_delinquent | 0.787 |
| HHPN | 0.077 | 29.692 | repeat_delinquent | 0.712 |
| RRRH | 0.189 | 29.594 | straight_roller_seasoned | 0.544 |
| RRHH | 0.078 | 27.929 | repeat_delinquent | 0.453 |
| RPRP | 0.095 | 22.571 | repeat_delinquent | 0.350 |
| RHRP | 0.050 | 19.077 | repeat_delinquent | 0.702 |
| RPRH | 0.038 | 18.900 | stabilized | 0.381 |
| RPHR | 0.040 | 18.182 | slow_roller | 0.445 |
| HHRP | 0.011 | 18.000 | stabilized | 0.556 |
