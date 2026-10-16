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
| E03 | PASS | Backtest monthly roll rates match the bank's 70/80/90/95% (max abs deviation) | 0.013 | <= 7pp | Confirms the string orientation and the backtest reconstruction are right. | Check LEFTMOST_IS_CURRENT and that DS_STRINGS keeps accounts that left the spine (survivor-only data shows roll rates that are too low). |
| E04 | PASS | Share of histories that start inside the current spell (no clean month seen) | 0.000 | <= 10% | Full history is available for everyone. | Strings are truncated; EPD (short history) will be over-assigned — cap the EPD rule to accounts with full history or raise the threshold. |
| E05 | PASS | Share of accounts with an unrepaired +2 jump | 0.003 | <= 2% | Billing-cycle jumps are mostly next to a hold and get repaired. | Look at examples; if a systematic code (e.g. 2-cycle buckets) exists, adjust the encoding. |
| E06 | PASS | Current bucket mix declines from 4 to 7 | 0.073 | >= 0 | Flow-driven book with rising roll rates (synthetic 29/26/23/22%). | Check the spine filter and whether a cohort shock is passing through. |
| E07 | PASS | One spell only, spell counted from bucket 3 | 0.827 | 78–92% | Bank figure ~85% (synthetic 83%). If the 'from 4' figure is the one near 85%, the bank counts spells from 4. | Set repeat_min_prior_peak to whichever spell definition matches the bank's 85%. |
| E08 | PASS | Early payment default (EPD, 'bust-out') share (today) | 0.057 | 4–8% | Bank's own rule gives ~6% (synthetic 5.8%). | Move epd_max_history along the sweep until the share matches the bank's rule. |
| E09 | PASS | Stabilized share (today) | 0.077 | 4–9% | Bank's own stabilized rule gives ~6% (synthetic 6.6%). | Compare with the bank's implementation of the 5-of-6 rule (E10/E11). |
| E10 | PASS | Recall of the bank's existing bust-out (EPD) flag | 0.937 | >= 80% | Same concept; thresholds may differ slightly. | Read the bank's rule and align epd_max_history / epd_max_blips. |
| E11 | PASS | Recall of the bank's existing stabilized flag | 0.932 | >= 90% | Stabilized IS the bank's 5-of-6 rule; only EPD-first ordering differs. | Check the band definition (±1 of today's bucket, 5 of last 6 months incl. today). |
| E12 | PASS | Stabilized separates risk: weighted next-month roll of fixed states minus stabilized | 0.378 | >= 20pp | Synthetic: stabilized 40% vs ~85% for the rest. | Stabilized is not behaving as 'stable'; check payment holidays / restructuring flags (E21) and try stabilized_min_in_band = 6. |
| E13 | PASS | Fixed states keep their state next month (minimum over fixed states) | 0.970 | >= 95% | Run-up and history are fixed once past 4 (synthetic 98–100%). | A feature is drifting with time since 4 — inspect which state leaks and why. |
| E14 | PASS | Stabilized persistence next month | 0.598 | 45–85% | Stabilized is current behaviour; it should persist but not forever (synthetic 62%). | Too low: the band is too loose. Too high: frozen buckets (holidays) are being read as payments. |
| E15 | PASS | Option A: straight-roller share | 0.700 | 55–80% | Most accounts roll straight 2-3-4 (synthetic 70%). | If much lower, many run-ups contain a hold — check +2/billing artefacts before trusting slow roller. |
| E16 | WARN | Every option-B state holds at least 5% of the spine | 0.034 | >= 5% | Actionable size. Synthetic: straight_roller_early_life 3.4% under the 12-month seasoned cut (depends on the book's tenure mix). | Merge the small state into its neighbour (repeat_delinquent→straight_roller, early-life→seasoned), or move seasoned_min_months along its sweep (12 → 18 → 24 months). |
| E17 | PASS | Option C: smaller of intermittent / erratic payer (slow-roller split) | 0.057 | >= 4% | Synthetic 10% / 6%. | Too small to act on — use option B. |
| E18 | PASS | Stabilized sits low in the spine: share at bucket 4 / share at bucket 7 | 15.091 | >= 2x | 90–95% roll rates at 6–7 leave little room to hold there. | Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays). |
| E19 | PASS | Orthogonality: credibility score explained by the states (eta²) | 0.184 | <= 0.25 | Known overlap via stabilized (money in) and repeat delinquent (clean point), but the states should not reproduce the score. | Use option A (drops repeat delinquent) or report stabilized under credibility instead. |
| E19b | WARN | Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²) | 0.812 | <= 0.50 | Repeat delinquent is defined from earlier spells — the same history the clean point scores. Synthetic (with a clean point = 'no earlier spell'): 0.84 → WARN. | Repeat delinquent duplicates the credibility clean point: use option A, or keep it and tell the persona grid it is the same signal (it is only 1 of credibility's 5 points). |
| E20 | PASS | Orthogonality: ability score explained by the states (eta²) | 0.000 | <= 0.10 | DPD shape should carry little of salary/inflow/CASA. | Straight vs slow roller may be a proxy for income loss — fine, but say so in the persona grid. |
| E21 | PASS | Stabilized accounts with money coming in (credibility component or DPD proxy) | 0.983 | >= 90% | Stabilized = paid one month's due most months, so money must be coming in (synthetic 100%). | Stabilized accounts without money in are frozen buckets (holiday/restructure) — exclude those months. |
| E22 | PASS | Residual clusters agree more with option B than with A (ARI gain at k=6) | 0.199 | >= 0.15 | Synthetic at k=6: 0.32 (B) vs 0.11 (A) — the data has more than two residual groups. | The extra B splits are not natural groups in this book — prefer option A. |
| E23 | PASS | One paid month on the way down matters: slow-roller share at run-up<=4 / at <=3 | 0.579 | <= 0.70 | Synthetic ~0.58: most slow rollers held exactly once. | Slow roller is driven by long run-ups, not single payments — keep 3 but review examples. |
| E24 | PASS | 'Paying since 4' stays rejected: share still in it next month at 0.5 | 0.597 | <= 75% | Synthetic 63%: unstable current-behaviour state. | If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'. |
| E26 | PASS | Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months | 0.048 | <= 10% | Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating payers bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold) and swingers in their first 6 months at 4 (both rules are reported). | Too many accounts bounce: look at examples; consider stabilized_long_run_max_rise = 2 or a sticky rule — but both widen the definition, so agree it with the business. |
| E25 | INFO | INFO — spread of exit-within-k across fixed states (option B) | 0.062 | report | Synthetic data cannot show this (same post-4 dynamics by construction). | >= 5pp means the mechanism carries risk information beyond stabilized. |

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
| n_current_rows | 20000 |
| share_invalid_strings | 0.000 |
| n_current_spine_analysed | 20000 |
| string_length_p05_p50_p95 | [9, 53, 141] |
| share_left_censored | 0.000 |
| share_jump_repaired | 0.024 |
| share_jump_left | 0.003 |
| share_one_spell_from3 | 0.827 |
| share_one_spell_from4 | 0.948 |
| bucket_mix | {4: 0.29085, 5: 0.26455, 6: 0.22665, 7: 0.21795} |

## 2. States today (current spine)

### A_minimal_4

Share:

| state | share |
|---|---|
| early_payment_default | 0.057 |
| stabilized | 0.077 |
| straight_roller | 0.700 |
| slow_roller | 0.166 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.048 | 0.057 | 0.064 | 0.058 |
| stabilized | 0.149 | 0.087 | 0.038 | 0.010 |
| straight_roller | 0.652 | 0.693 | 0.728 | 0.743 |
| slow_roller | 0.150 | 0.163 | 0.169 | 0.189 |

### B_balanced_6

Share:

| state | share |
|---|---|
| early_payment_default | 0.057 |
| stabilized | 0.077 |
| repeat_delinquent | 0.163 |
| straight_roller_seasoned | 0.518 |
| straight_roller_early_life | 0.034 |
| slow_roller | 0.151 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.048 | 0.057 | 0.064 | 0.058 |
| stabilized | 0.149 | 0.087 | 0.038 | 0.010 |
| repeat_delinquent | 0.153 | 0.154 | 0.172 | 0.179 |
| straight_roller_seasoned | 0.484 | 0.517 | 0.535 | 0.546 |
| straight_roller_early_life | 0.032 | 0.034 | 0.036 | 0.034 |
| slow_roller | 0.133 | 0.152 | 0.154 | 0.173 |

### C_detailed_7

Share:

| state | share |
|---|---|
| early_payment_default | 0.057 |
| stabilized | 0.077 |
| repeat_delinquent | 0.163 |
| straight_roller_seasoned | 0.518 |
| straight_roller_early_life | 0.034 |
| slow_roller_intermittent | 0.094 |
| slow_roller_erratic | 0.057 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.048 | 0.057 | 0.064 | 0.058 |
| stabilized | 0.149 | 0.087 | 0.038 | 0.010 |
| repeat_delinquent | 0.153 | 0.154 | 0.172 | 0.179 |
| straight_roller_seasoned | 0.484 | 0.517 | 0.535 | 0.546 |
| straight_roller_early_life | 0.032 | 0.034 | 0.036 | 0.034 |
| slow_roller_intermittent | 0.084 | 0.092 | 0.095 | 0.108 |
| slow_roller_erratic | 0.049 | 0.060 | 0.059 | 0.065 |

Examples (B_balanced_6, no keys):

| state | last_30_months_oldest_to_newest |
|---|---|
| early_payment_default | 020234 |
| early_payment_default | 000233567 |
| early_payment_default | 100234 |
| stabilized | 002200100000223200000002345565 |
| stabilized | 000000010001200000200023455566 |
| stabilized | 000000000000000000000000234334 |
| repeat_delinquent | 300000002234300000002000100234 |
| repeat_delinquent | 000012233200000000100000234567 |
| repeat_delinquent | 000000200000232000000100100234 |
| straight_roller_seasoned | 001020000001202000020200234567 |
| straight_roller_seasoned | 00000200002000000002012345 |
| straight_roller_seasoned | 000000000000000001000000002345 |
| straight_roller_early_life | 0000000000023456 |
| straight_roller_early_life | 00020023455 |
| straight_roller_early_life | 00000000234567 |
| slow_roller | 000000000000000000000000232234 |
| slow_roller | 000000000000000001000000223456 |
| slow_roller | 000000001000200010000002233456 |

## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules

| state | their_share | our_share | recall_of_theirs | precision_vs_theirs |
|---|---|---|---|---|
| early_payment_default | 0.060 | 0.057 | 0.937 | 0.998 |
| stabilized | 0.073 | 0.077 | 0.932 | 0.880 |

## 4. Overlap with the other persona axes

Variance of each axis explained by the states (eta², 0 = orthogonal):

| axis | A_minimal_4 | B_balanced_6 | C_detailed_7 |
|---|---|---|---|
| credibility_score | 0.104 | 0.184 | 0.185 |
| cred_ptp_points | 0.000 | 0.000 | 0.000 |
| cred_money_in_points | 0.171 | 0.166 | 0.169 |
| cred_clean_point | 0.036 | 0.812 | 0.812 |
| ability_score | 0.000 | 0.000 | 0.000 |
| reachable_flag | 0.000 | 0.000 | 0.000 |
| in_country_flag | 0.000 | 0.000 | 0.000 |

Mean of each axis by state (B_balanced_6):

| state | credibility_score | cred_ptp_points | cred_money_in_points | cred_clean_point | ability_score | reachable_flag | in_country_flag |
|---|---|---|---|---|---|---|---|
| early_payment_default | 2.288 | 0.687 | 0.601 | 1.000 | 49.724 | 0.686 | 0.827 |
| stabilized | 3.505 | 0.680 | 1.962 | 0.863 | 50.444 | 0.703 | 0.841 |
| repeat_delinquent | 1.375 | 0.719 | 0.656 | 0.000 | 49.870 | 0.707 | 0.854 |
| straight_roller_seasoned | 2.343 | 0.712 | 0.670 | 0.961 | 50.167 | 0.692 | 0.854 |
| straight_roller_early_life | 2.456 | 0.736 | 0.734 | 0.987 | 50.712 | 0.702 | 0.863 |
| slow_roller | 2.905 | 0.710 | 1.200 | 0.996 | 50.009 | 0.689 | 0.846 |

Stabilized vs money coming in:

| metric | value |
|---|---|
| source | cred_money_in_points |
| stabilized_with_money_in | 0.983 |
| others_with_money_in | 0.445 |

## 5. Backtest — spine as of 6 months ago, outcomes since

20,000 accounts. Monthly roll rate by bucket (should match the bank's ~70/80/90/95%):

| bucket | roll_rate |
|---|---|
| 4 | 0.699 |
| 5 | 0.787 |
| 6 | 0.888 |
| 7 | 0.940 |

### A_minimal_4

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.060 | 1193 | 0.896 | 0.987 | 0.002 | 4.000 | 1.000 | 0.226 |
| stabilized | 0.080 | 1602 | 0.470 | 0.581 | 0.047 | 3.000 | 0.598 | 0.211 |
| straight_roller | 0.687 | 13746 | 0.851 | 0.946 | 0.008 | 3.000 | 0.985 | 0.266 |
| slow_roller | 0.173 | 3459 | 0.819 | 0.912 | 0.044 | 3.000 | 0.969 | 0.271 |

### B_balanced_6

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.060 | 1193 | 0.896 | 0.987 | 0.002 | 4.000 | 1.000 | 0.226 |
| stabilized | 0.080 | 1602 | 0.470 | 0.581 | 0.047 | 3.000 | 0.598 | 0.211 |
| repeat_delinquent | 0.165 | 3306 | 0.844 | 0.938 | 0.020 | 3.000 | 0.987 | 0.279 |
| straight_roller_seasoned | 0.506 | 10111 | 0.849 | 0.944 | 0.007 | 3.000 | 0.983 | 0.264 |
| straight_roller_early_life | 0.031 | 618 | 0.843 | 0.932 | 0.018 | 3.000 | 0.989 | 0.294 |
| slow_roller | 0.159 | 3170 | 0.832 | 0.926 | 0.037 | 3.000 | 0.970 | 0.259 |

### C_detailed_7

| state | share | n | roll_next_month | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.060 | 1193 | 0.896 | 0.987 | 0.002 | 4.000 | 1.000 | 0.226 |
| stabilized | 0.080 | 1602 | 0.470 | 0.581 | 0.047 | 3.000 | 0.598 | 0.211 |
| repeat_delinquent | 0.165 | 3306 | 0.844 | 0.938 | 0.020 | 3.000 | 0.987 | 0.279 |
| straight_roller_seasoned | 0.506 | 10111 | 0.849 | 0.944 | 0.007 | 3.000 | 0.983 | 0.264 |
| straight_roller_early_life | 0.031 | 618 | 0.843 | 0.932 | 0.018 | 3.000 | 0.989 | 0.294 |
| slow_roller_intermittent | 0.101 | 2020 | 0.824 | 0.919 | 0.048 | 3.000 | 0.963 | 0.258 |
| slow_roller_erratic | 0.058 | 1150 | 0.846 | 0.937 | 0.017 | 3.000 | 0.982 | 0.260 |

### Stabilized bounce-backs over the 6 backtest months (10,000 accounts)

Share of ever-stabilized accounts that left stabilized and came back while staying in the spine (S . S):

| stabilized rule | ever_stabilized | bounce_back_share_of_ever_stabilized | mean_status_changes_per_account |
|---|---|---|---|
| with_long_run_clause | 0.130 | 0.048 | 0.119 |
| bank_rule_only | 0.122 | 0.056 | 0.121 |

## 6. Threshold sweeps (backtest population)

### epd_max_history

| epd_max_history | share | exit_within_k |
|---|---|---|
| 2 | 0.026 | 0.987 |
| 3 | 0.060 | 0.987 |
| 4 | 0.062 | 0.985 |
| 6 | 0.070 | 0.967 |
| 9 | 0.083 | 0.960 |
| 12 | 0.100 | 0.950 |

### stabilized_min_in_band

| stabilized_min_in_band | share | roll_next_month | still_stabilized_next_month |
|---|---|---|---|
| 4 | 0.138 | 0.561 | 0.565 |
| 5 | 0.080 | 0.470 | 0.598 |
| 6 | 0.053 | 0.417 | 0.660 |

### repeat_min_prior_peak

| repeat_min_prior_peak | share |
|---|---|
| 2 | 0.185 |
| 3 | 0.165 |
| 4 | 0.046 |

### straight_max_runup

| straight_max_runup | straight_share | slow_share |
|---|---|---|
| 3 | 0.687 | 0.173 |
| 4 | 0.760 | 0.100 |
| 5 | 0.831 | 0.029 |

### seasoned_min_months

| seasoned_min_months | seasoned | early_life |
|---|---|---|
| 12 | 0.506 | 0.031 |
| 18 | 0.470 | 0.067 |
| 24 | 0.429 | 0.108 |
| 36 | 0.346 | 0.190 |

### paying_since_4_test

| paying_since_4_min_rate | share | still_paying_since_4_next_month | stability_of_fixed_states | stability_of_fixed_states_without_q3 |
|---|---|---|---|---|
| 0.340 | 0.190 | 0.719 | 0.902 | 0.983 |
| 0.500 | 0.171 | 0.597 | 0.903 | 0.983 |
| 0.670 | 0.069 | 0.295 | 0.955 | 0.983 |

## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with each option

| k | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|
| 2 | -0.065 | 0.440 | 0.418 |
| 3 | 0.292 | 0.632 | 0.641 |
| 4 | 0.178 | 0.450 | 0.455 |
| 5 | 0.299 | 0.554 | 0.579 |
| 6 | 0.106 | 0.304 | 0.323 |
| 7 | 0.171 | 0.375 | 0.395 |
| 8 | 0.154 | 0.345 | 0.363 |

## 8. Most common journey shapes and motifs

Shapes (N clean, R roll, H hold = paid one month, P paid 2+ months; run lengths banded):

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3808 | straight_roller_seasoned | 1.000 | 0.190 | 0.190 |
| N13-24 R3+ | 823 | straight_roller_seasoned | 1.000 | 0.041 | 0.232 |
| N25+ R3+ H1 | 362 | straight_roller_seasoned | 1.000 | 0.018 | 0.250 |
| N7-12 R3+ | 336 | straight_roller_early_life | 0.679 | 0.017 | 0.266 |
| N2-3 R3+ | 275 | early_payment_default | 0.869 | 0.014 | 0.280 |
| N25+ R3+ H1 R1 | 247 | straight_roller_seasoned | 1.000 | 0.012 | 0.293 |
| R1 P1 R3+ | 234 | early_payment_default | 1.000 | 0.012 | 0.304 |
| N25+ R2 P1 R3+ | 217 | slow_roller | 0.931 | 0.011 | 0.315 |
| N1 R3+ | 204 | early_payment_default | 1.000 | 0.010 | 0.325 |
| R3+ | 188 | early_payment_default | 1.000 | 0.009 | 0.335 |
| N25+ R3+ P1 R3+ | 182 | straight_roller_seasoned | 1.000 | 0.009 | 0.344 |
| N25+ R3+ H1 R2 | 176 | straight_roller_seasoned | 1.000 | 0.009 | 0.353 |
| N25+ R1 H1 R3+ | 170 | slow_roller | 1.000 | 0.009 | 0.361 |
| N25+ R3+ P1 R1 | 165 | straight_roller_seasoned | 1.000 | 0.008 | 0.369 |
| N4-6 R3+ | 114 | straight_roller_early_life | 1.000 | 0.006 | 0.375 |
| N25+ R3+ P1 R2 | 114 | straight_roller_seasoned | 1.000 | 0.006 | 0.381 |
| N25+ R2 P1 R2 | 104 | slow_roller | 1.000 | 0.005 | 0.386 |
| N25+ R2 H1 R3+ | 98 | slow_roller | 1.000 | 0.005 | 0.391 |
| N25+ R2 H1 R1 | 97 | slow_roller | 1.000 | 0.005 | 0.396 |
| N25+ R2 P1 H1 R3+ | 78 | slow_roller | 1.000 | 0.004 | 0.400 |

4-grams by lift vs shuffled order:

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.092 | 97.211 | repeat_delinquent | 0.710 |
| HHPP | 0.023 | 66.286 | repeat_delinquent | 0.931 |
| HHPN | 0.073 | 37.487 | repeat_delinquent | 0.696 |
| HRHP | 0.029 | 30.684 | repeat_delinquent | 0.875 |
| RHRH | 0.098 | 30.277 | repeat_delinquent | 0.513 |
| RHPP | 0.023 | 28.250 | repeat_delinquent | 0.920 |
| RRHH | 0.074 | 25.220 | repeat_delinquent | 0.442 |
| RPRP | 0.096 | 23.108 | repeat_delinquent | 0.354 |
| PRHP | 0.011 | 22.900 | repeat_delinquent | 0.563 |
| HPPN | 0.041 | 19.927 | repeat_delinquent | 0.989 |
| RRPH | 0.047 | 18.231 | slow_roller | 0.302 |
| RRRH | 0.188 | 17.412 | straight_roller_seasoned | 0.529 |
| HRPP | 0.016 | 17.158 | repeat_delinquent | 0.773 |
| RHRP | 0.051 | 16.222 | repeat_delinquent | 0.660 |
| RRHP | 0.043 | 15.339 | repeat_delinquent | 0.750 |
