# Self-test on synthetic data — 20261016

Fake axis columns; real-data code path.

## 0a. Edge cases (oldest → newest, option B)

```
OK   0 2 0 2 3 4                           -> early_payment_default       3 months incl. one blip, then straight roll
OK   0 0 0 2 3 4                           -> early_payment_default       3 clean months, straight roll
OK   0 2 3 4 5                             -> early_payment_default       1 clean month
OK   0 0 2 0 2 3 4                         -> straight_roller_early_life  4 months of history: too long for EPD
OK   0 0 0 0 0 0 2 3 4                     -> straight_roller_early_life  6 clean months: early-life default, not EPD
OK   0 2 0 2 0 2 3 4                       -> straight_roller_early_life  two blips: not EPD
OK   0 2 3 4 0 0 2 3 4 5 6                 -> repeat_delinquent           paid off from 4, then relapsed
OK   0 0 2 2 3 4                           -> slow_roller                 held once on the way down
OK   0 0 0 0 2 2 2 2 3 3 3 4 4 4 4 4 4 4   -> stabilized                  staircase holding at 4 then one step
OK   000000000000002345                    -> straight_roller_seasoned    14 clean months, straight roll
OK   0000000000000234444567                -> straight_roller_seasoned    held at 4, then rolled 3 buckets: not stable
OK   0000000000000023455555                -> stabilized                  holding at 5
OK   00000000234443345433456554            -> stabilized                  oscillating payer (example 1)
OK   00000000234443345433456654            -> stabilized                  oscillating payer that just paid down 6-5-4 (example 2)
OK   0 0 2 3 4 4 4 4 4 4                   -> stabilized                  entered like EPD but pays the monthly due since: not EPD
OK   0 0 2 3 4 4 5 6                       -> straight_roller_early_life  entered like EPD, paid once at 4: EPD needs no payment
OK   4 5 6 7                               -> history_starts_delinquent   string starts delinquent (restructured / missing history)
OK   0000000000000000224                   -> straight_roller_seasoned    +2 jump after a hold at 2: repaired to 2 3 4
OK   00000000000000002244                  -> straight_roller_seasoned    same account a month later: fixed state must not change
OK   000034                                -> straight_roller_early_life  jump from clean to 3: no clean month is borrowed
OK   0 2 3 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0   -> straight_roller_seasoned    cured 30 months earlier: outside 24-month window
OK   0 2 3 4 0 0 0 0 0 0 0 0 0 0 0 0 0 0   -> repeat_delinquent           cured 20 months earlier: repeat delinquent
OK   0000000000000000 2 3 4 4 0 4 5        -> stabilized                  single 0 inside a spell at 4 is a glitch, not a cure
OK   0000 3 0000000000000 2 3 4            -> straight_roller_seasoned    single spike 0 3 0 is a glitch, not an earlier spell
```

## 0. Expectation checks

| id | status | check | observed | expected | anchor | why | if_not_met |
|---|---|---|---|---|---|---|---|
| E01 | PASS | Every account gets exactly one known state (all options) | True | True | design | The tree ends in a default branch, so it is MECE by construction; unknown labels mean a code change broke it. | A code or data-type bug — stop and fix before reading anything else. |
| E02 | PASS | Unparseable strings (worst of: today's spine, backtest, whole table) | 0.000 | <= 2% | data | Strings should be digits once CHAR_MAP / STRIP_CHARS are set. | Inspect the non-digit characters (check-only output); extend CHAR_MAP (e.g. a write-off letter -> 9). Untreated letters silently drop accounts from the backtest. |
| E03 | PASS | Backtest monthly roll rates vs the bank's 70/80/90/95% (max abs deviation) | 0.013 | <= 7pp | bank | Confirms the string orientation and that the one-table backtest is valid. | Check, in order: LEFTMOST_IS_CURRENT; that every string ends in the SAME month (strings frozen at charge-off/closure, or exited accounts dropped from the table, make roll rates too low — set COL_STRING_AS_OF); letter exit codes missing from CHAR_MAP; whether the bank's roll rates are count- or balance-weighted. |
| E04 | PASS | Histories that start already delinquent (history_starts_delinquent) | 0.000 | <= 1% | bank | The first digit is the first billed month (0/1); exceptions are rare data issues and restructured accounts re-opened at their old bucket. | Confirm the string-start convention (PROMPTS P1). Many cases point to restructured accounts or truncated strings — their treatment is a deferred business decision. |
| E05 | PASS | Accounts with an unrepaired +2 jump | 0.007 | <= 2% | synthetic | Billing-cycle jumps mostly sit next to a hold and get repaired. | Look at the shapes; a systematic code (e.g. 2-cycle buckets) needs an encoding change. |
| E06 | PASS | Current bucket mix declines from 4 to 7 (share at 4 minus share at 7) | 0.073 | >= 0 | bank | Rising roll rates 70→95% thin the spine out towards bucket 7. | Check the spine filter and whether a cohort shock is passing through. |
| E07 | INFO | INFO — one-spell share: definition closest to the bank's ~85% | reached_3: 0.83 | report | bank | Four spell definitions are reported in section 1; the bank's exact one is unconfirmed. | Get the bank's definition; if it is 'reached 4' or 'run at >=4', discuss repeat_min_prior_peak. |
| E08 | PASS | Early payment default share (today) | 0.043 | 3–8% | bank | Bank's own bust-out rule gives ~6%; the agreed definition is stricter (never paid since crossing 2). | Compare with the bank's rule (E10, PROMPTS P4) and escalate to the business owner. Do not move epd_max_history to match a share. |
| E09 | PASS | Stabilized share (today) | 0.078 | 4–10% | bank | Bank's 5-of-6 rule gives ~6%; the long-run clause adds about one point. | Compare with the bank's implementation (E11, PROMPTS P4) and escalate. |
| E10 | PASS | Recall of the bank's existing bust-out flag by our EPD | 0.919 | >= 80% | bank | Same concept; ours additionally requires no payment since crossing bucket 2. | Read the bank's rule (PROMPTS P4), list the differences and escalate. |
| E11 | PASS | Recall of the bank's existing stabilized flag by our stabilized | 0.941 | >= 90% | bank | Ours is the bank's 5-of-6 rule plus the long-run clause; differences: EPD/ordering, glitch and +2-jump cleaning. | Check the band definition (±1 of today's bucket, 5 of the last 6 months incl. today). |
| E12 | PASS | Stabilized separates risk: fixed states' next-month roll minus stabilized (bucket-standardised) | 0.336 | >= 20pp | synthetic | Synthetic: ~0.37. Standardised to the same bucket mix, because stabilized sits mostly at bucket 4. | Stabilized is not behaving as stable: check payment holidays / restructuring flags (E21) and escalate whether to use 6 of 6. |
| E13 | PASS | Fixed states keep their state (or move into stabilized) next month — min over states with n >= 100 | 0.997 | >= 95% | design | Run-up, history and the repairs are causal: how they fell in never changes once past 4. EPD is not fixed (it ends when the account pays) and moving into stabilized is not a leak. | A feature is drifting with time or with the next month's data — find the leaking state. |
| E14 | PASS | Stabilized persistence next month | 0.600 | 45–85% | synthetic | Stabilized is current behaviour; it should persist but not forever (synthetic ~60%). | Too low: the band is too loose. Too high: frozen buckets (holidays) are read as payments. |
| E15 | PASS | Option A: straight-roller share | 0.714 | 55–80% | bank | Most accounts roll straight 2-3-4 (synthetic ~70%). | If much lower, many run-ups contain a hold — look at E28 (artefacts) before trusting slow roller. |
| E16 | WARN | Smallest optional state in option B (EPD and stabilized are required; empty = 0) | 0.047 | >= 5% | design | Actionable size for the optional splits; the bank's two known states are kept at any size. Synthetic: early-life straight roller ~4.7% under the 12-month cut. | If it is early-life straight roller: merge it into straight roller (agreed with the owner: set seasoned_min_months=None and keep early life as a flag). Any other state: escalate. |
| E17 | PASS | Option C: smaller of intermittent / erratic payer | 0.057 | >= 4% | design | Synthetic 10% / 6%. | Too small to act on — use option B. |
| E18 | PASS | Stabilized sits low in the spine: share at bucket 4 / share at bucket 7 | 15.141 | >= 2x | bank | 90–95% roll rates at 6–7 leave little room to hold there. | Stabilized accounts at 6–7 are unusual — check for frozen buckets (payment holidays). |
| E19 | PASS | Orthogonality: credibility score explained by the states (eta²) | 0.182 | <= 0.25 | design | Known overlap via stabilized (money in), slow roller (money in near bucket 4) and repeat delinquent (clean point); the states should not reproduce the score. | Use option A (drops repeat delinquent) or report stabilized under credibility instead. |
| E19b | WARN | Orthogonality: credibility 'pre-delinquency clean' point explained by the states (eta²) | 0.723 | <= 0.50 | design | Repeat delinquent uses earlier spells — the history the clean point scores (now limited to the last 24 months, which lowers the overlap). | Repeat delinquent duplicates the clean point: use option A, or keep it and tell the persona grid it is the same signal (only 1 of credibility's 5 points). |
| E20 | PASS | Orthogonality: ability score explained by the states (eta²) | 0.000 | <= 0.10 | design | DPD shape should carry little of salary/inflow/CASA. | Straight vs slow roller may proxy income loss — fine, but say so in the persona grid. |
| E20b | PASS | Orthogonality: reachability / in-country explained by the states (max eta²) | 0.000 | <= 0.05 | design | Locatability is independent of how the debt was paid. | A state is acting as a departure proxy — report it to the persona owners. |
| E21 | PASS | Stabilized accounts with money coming in (credibility component or DPD proxy) | 0.983 | >= 90% | design | Stabilized = paid one month's due most months, so money must be coming in. | Stabilized accounts without money in are frozen buckets (holiday/restructure) — flag them. |
| E22 | INFO | INFO — residual clusters: option-B ARI gain over option A at k=6 | 0.186 | report | synthetic | Diagnostic only: any finer partition built on the clustered features gains ARI (a meaningless tenure split gained 0.16 in review), so this is not evidence for B over A. | — |
| E23 | INFO | INFO — one paid month: straight minus one-hold slow roller, next-month roll (bucket-std) | 0.027 | report | synthetic | 41% of slow rollers rest on a single hold. Unknowable from synthetic data (same post-4 dynamics). | Near 0 and E28 shows artefacts: the straight/slow split rests on noise — escalate whether a single hold should still make a slow roller (straight_max_runup = 4). |
| E24 | PASS | 'Paying since 4' stays rejected: share still in it next month at 0.5 | 0.588 | <= 75% | synthetic | Synthetic ~63%: an unstable current-behaviour state. | If it is stable on real data, reconsider Q3 — but it remains credibility's 'money in'. |
| E25 | INFO | INFO — spread of exit to 8+ within 3 months across fixed states (option B, bucket-std) | 0.007 | report | synthetic | Standardised to the bucket mix and over 3 months, because 6-month exit saturates near 100% at 5–7. | >= 5pp means how they fell in carries risk information beyond stabilized. |
| E26 | PASS | Stabilized bounce-backs: ever-stabilized accounts that left and came back within k months | 0.047 | <= 10% | synthetic | Synthetic ~5–7% with the long-run clause vs ~8% on the bank's rule alone; oscillating payers bounce 41% less. Remaining bounces are mostly staircases (hold, step, hold). | Too many bounce: look at shapes; +2 tolerance or a sticky rule widen the definition — escalate. |
| E27 | PASS | String lengths vary (p95 minus p05 of history length, months) | 132 | >= 6 | data | Full history from the first billed month gives very different lengths across accounts. | Strings look fixed-length (padded or truncated): EPD and early-life cannot be judged from the string — confirm the convention (PROMPTS P1) before reading those states. |
| E28 | PASS | Run-up holds by calendar month: largest month vs its neighbours (artefact check) | 1.248 | <= 2.5 | data | Customer payments spread over calendar months; a spike means a system event (cycle-date change, reversal batch, deferral). | Find the month (section 5b) and ask the data owners; holds from that month should not count. |

## State names

| code | display name | remark |
|---|---|---|
| history_starts_delinquent | Not classified — history starts delinquent | Data quality, not behaviour: the oldest month in the string is already delinquent — typically a restructured card/loan re-opened at its old bucket, a migrated account or missing history. Rare; treatment of restructured accounts is deferred. |
| early_payment_default | Early payment default (EPD) | Never paid since crossing bucket 2 and still falling, at most 3 months after the first bill. Called 'bust-out' internally — but classic bust-out fraud (good history, limit build-up, then max-out) shows as a seasoned straight roller and needs a fraud overlay on spend data. |
| stabilized | Stabilized | The bank's 5-of-6 stabilized rule, plus a long-run clause (6+ months since first reaching 4, at most one bucket higher than 6 months ago) so oscillating payers and accounts that just paid down are not mislabelled. |
| paying_since_4 | Paying since bucket 4 (tested, not used) | Rejected — current-behaviour state that belongs to credibility (money coming in). |
| repeat_delinquent | Repeat delinquent (re-default) | Re-default within 24 months of curing a spell that reached bucket 3; collections 'recidivism'. |
| straight_roller | Straight roller | Rolled straight to bucket 4 (no payment on the way down). Describes how they fell in — some have paid since. |
| straight_roller_seasoned | Seasoned straight roller | Rolled straight to bucket 4 after at least a year on book (seasoned). |
| straight_roller_early_life | Early-life straight roller | Rolled straight to bucket 4 in the first year on book (early-life default). |
| slow_roller | Slow roller (partial payer) | Paid something on the way down to bucket 4 but kept rolling. Also called partial payer. |
| slow_roller_intermittent | Intermittent payer | Slow roller that paid one month here and there on the way down. |
| slow_roller_erratic | Erratic payer | Slow roller that caught up 2+ months at once on the way down, then rolled again. |

## 1. Data quality and population

| metric | value |
|---|---|
| n_current_rows | 20000 |
| share_invalid_strings_current | 0.000 |
| share_non_digit_strings_table | None |
| n_current_spine_analysed | 20000 |
| string_length_p05_p50_p95 | [9, 53, 141] |
| string_length_spread | 132 |
| share_history_starts_delinquent | 0.000 |
| share_glitch_fixed | 0.000 |
| share_jump_repaired | 0.019 |
| share_jump_left | 0.007 |

Share of the spine with ONE spell only, by definition (the bank quotes ~85% — the matching row tells which definition the bank uses):

| spell definition | share |
|---|---|
| run at >=2 that reached 3 | 0.827 |
| run at >=2 that reached 4 | 0.948 |
| run of months at >=3 | 0.736 |
| run of months at >=4 | 0.820 |

## 2. States today (current spine)

### A_minimal_4

Share:

| state | share |
|---|---|
| history_starts_delinquent | 0.000 |
| early_payment_default | 0.043 |
| stabilized | 0.078 |
| straight_roller | 0.714 |
| slow_roller | 0.165 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| history_starts_delinquent | 0.000 | 0.000 | 0.000 | 0.000 |
| early_payment_default | 0.043 | 0.044 | 0.043 | 0.041 |
| stabilized | 0.150 | 0.088 | 0.039 | 0.010 |
| straight_roller | 0.657 | 0.705 | 0.750 | 0.761 |
| slow_roller | 0.150 | 0.162 | 0.168 | 0.187 |

### B_balanced_6

Share:

| state | share |
|---|---|
| history_starts_delinquent | 0.000 |
| early_payment_default | 0.043 |
| stabilized | 0.078 |
| repeat_delinquent | 0.148 |
| straight_roller_seasoned | 0.534 |
| straight_roller_early_life | 0.047 |
| slow_roller | 0.151 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| history_starts_delinquent | 0.000 | 0.000 | 0.000 | 0.000 |
| early_payment_default | 0.043 | 0.044 | 0.043 | 0.041 |
| stabilized | 0.150 | 0.088 | 0.039 | 0.010 |
| repeat_delinquent | 0.139 | 0.139 | 0.158 | 0.160 |
| straight_roller_seasoned | 0.499 | 0.532 | 0.550 | 0.567 |
| straight_roller_early_life | 0.036 | 0.045 | 0.058 | 0.051 |
| slow_roller | 0.133 | 0.151 | 0.153 | 0.171 |

### C_detailed_7

Share:

| state | share |
|---|---|
| history_starts_delinquent | 0.000 |
| early_payment_default | 0.043 |
| stabilized | 0.078 |
| repeat_delinquent | 0.148 |
| straight_roller_seasoned | 0.534 |
| straight_roller_early_life | 0.047 |
| slow_roller_intermittent | 0.093 |
| slow_roller_erratic | 0.057 |

Mix by current bucket (column shares):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| history_starts_delinquent | 0.000 | 0.000 | 0.000 | 0.000 |
| early_payment_default | 0.043 | 0.044 | 0.043 | 0.041 |
| stabilized | 0.150 | 0.088 | 0.039 | 0.010 |
| repeat_delinquent | 0.139 | 0.139 | 0.158 | 0.160 |
| straight_roller_seasoned | 0.499 | 0.532 | 0.550 | 0.567 |
| straight_roller_early_life | 0.036 | 0.045 | 0.058 | 0.051 |
| slow_roller_intermittent | 0.084 | 0.091 | 0.094 | 0.107 |
| slow_roller_erratic | 0.049 | 0.060 | 0.059 | 0.065 |

Most common journey shapes per state (B_balanced_6; N clean, R roll, H hold, P paid 2+ months; only shapes shared by >= 10 accounts):

| state | shape | accounts |
|---|---|---|
| early_payment_default | N2-3 R3+ | 238 |
| early_payment_default | R1 P1 R3+ | 234 |
| early_payment_default | N1 R3+ | 202 |
| stabilized | N25+ R3+ H2-3 | 20 |
| stabilized | N25+ R3+ H4+ | 27 |
| stabilized | N25+ R3+ P1 H1 R1 | 42 |
| repeat_delinquent | N25+ R2 P1 R3+ | 15 |
| repeat_delinquent | … N13-24 R1 H1 R1 H2-3 P1 N7-12 R3+ | 13 |
| repeat_delinquent | … N7-12 R1 H1 R1 H2-3 P1 N7-12 R3+ | 10 |
| straight_roller_seasoned | N25+ R3+ | 3787 |
| straight_roller_seasoned | N25+ R3+ H1 | 363 |
| straight_roller_seasoned | N13-24 R3+ | 821 |
| straight_roller_early_life | N7-12 R3+ | 228 |
| straight_roller_early_life | N4-6 R3+ | 113 |
| straight_roller_early_life | N2-3 R3+ | 36 |
| slow_roller | N25+ R1 H1 R3+ | 168 |
| slow_roller | N25+ R2 P1 R3+ | 202 |
| slow_roller | N25+ R2 P1 R2 | 104 |

## 3. Agreement with the bank's existing EPD ('bust-out') / stabilized rules

| state | their_share | our_share | recall_of_theirs | precision_vs_theirs | share_unparsed |
|---|---|---|---|---|---|
| early_payment_default | 0.047 | 0.043 | 0.919 | 0.998 | 0.000 |
| stabilized | 0.073 | 0.078 | 0.941 | 0.881 | 0.000 |

## 4. Overlap with the other persona axes

Variance of each axis explained by the states (eta², 0 = orthogonal):

| axis | A_minimal_4 | B_balanced_6 | C_detailed_7 |
|---|---|---|---|
| credibility_score | 0.105 | 0.182 | 0.184 |
| cred_ptp_points | 0.000 | 0.000 | 0.000 |
| cred_money_in_points | 0.181 | 0.183 | 0.186 |
| cred_clean_point | 0.031 | 0.723 | 0.723 |
| ability_score | 0.000 | 0.000 | 0.000 |
| reachable_flag | 0.000 | 0.000 | 0.000 |
| in_country_flag | 0.000 | 0.000 | 0.000 |

Mean of each axis by state (B_balanced_6):

| state | credibility_score | cred_ptp_points | cred_money_in_points | cred_clean_point | ability_score | reachable_flag | in_country_flag |
|---|---|---|---|---|---|---|---|
| early_payment_default | 1.889 | 0.684 | 0.204 | 1.000 | 49.537 | 0.700 | 0.827 |
| stabilized | 3.508 | 0.681 | 1.962 | 0.865 | 50.470 | 0.702 | 0.841 |
| repeat_delinquent | 1.395 | 0.725 | 0.670 | 0.000 | 49.844 | 0.704 | 0.852 |
| straight_roller_seasoned | 2.319 | 0.711 | 0.674 | 0.933 | 50.168 | 0.694 | 0.855 |
| straight_roller_early_life | 2.769 | 0.724 | 1.055 | 0.990 | 50.570 | 0.684 | 0.852 |
| slow_roller | 2.904 | 0.708 | 1.201 | 0.995 | 49.996 | 0.689 | 0.846 |

Stabilized vs money coming in:

| metric | value |
|---|---|
| source | cred_money_in_points |
| stabilized_with_money_in | 0.983 |
| others_with_money_in | 0.447 |

Money coming in by state and current bucket (slow rollers paid on the way down, so near bucket 4 they overlap credibility's 'money in' — a clock effect):

| state | 4 | 5 | 6 | 7 |
|---|---|---|---|---|
| early_payment_default | 0.155 | 0.187 | 0.242 | 0.250 |
| stabilized | 1.000 | 0.949 | 0.983 | 1.000 |
| repeat_delinquent | 0.403 | 0.424 | 0.435 | 0.352 |
| straight_roller_seasoned | 0.346 | 0.447 | 0.451 | 0.408 |
| straight_roller_early_life | 0.462 | 0.646 | 0.651 | 0.523 |
| slow_roller | 1.000 | 0.651 | 0.452 | 0.443 |

## 5. Backtest — spine as of 6 months ago, outcomes since

20,000 accounts. Monthly roll rate by bucket (should match the bank's ~70/80/90/95%):

| bucket | roll_rate |
|---|---|
| 4 | 0.699 |
| 5 | 0.787 |
| 6 | 0.888 |
| 7 | 0.940 |

### A_minimal_4

| state | share | n | roll_next_month | roll_next_month_bucket_std | exit_8plus_within_3m_bucket_std | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | kept_or_stabilized_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.044 | 877 | 0.909 | 0.909 | 0.625 | 0.986 | 0.000 | 4.000 | 0.890 | 0.890 | 0.210 |
| stabilized | 0.081 | 1624 | 0.474 | 0.508 | 0.425 | 0.587 | 0.046 | 3.000 | 0.600 | 0.600 | 0.210 |
| straight_roller | 0.703 | 14051 | 0.852 | 0.846 | 0.622 | 0.947 | 0.008 | 3.000 | 0.984 | 1.000 | 0.267 |
| slow_roller | 0.172 | 3448 | 0.818 | 0.815 | 0.626 | 0.912 | 0.044 | 3.000 | 0.969 | 1.000 | 0.272 |

### B_balanced_6

| state | share | n | roll_next_month | roll_next_month_bucket_std | exit_8plus_within_3m_bucket_std | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | kept_or_stabilized_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.044 | 877 | 0.909 | 0.909 | 0.625 | 0.986 | 0.000 | 4.000 | 0.890 | 0.890 | 0.210 |
| stabilized | 0.081 | 1624 | 0.474 | 0.508 | 0.425 | 0.587 | 0.046 | 3.000 | 0.600 | 0.600 | 0.210 |
| repeat_delinquent | 0.150 | 3002 | 0.838 | 0.831 | 0.627 | 0.934 | 0.022 | 3.000 | 0.985 | 1.000 | 0.288 |
| straight_roller_seasoned | 0.521 | 10419 | 0.851 | 0.847 | 0.620 | 0.945 | 0.007 | 3.000 | 0.984 | 1.000 | 0.262 |
| straight_roller_early_life | 0.046 | 915 | 0.850 | 0.838 | 0.627 | 0.951 | 0.014 | 3.000 | 0.971 | 0.997 | 0.290 |
| slow_roller | 0.158 | 3163 | 0.832 | 0.828 | 0.625 | 0.925 | 0.037 | 3.000 | 0.971 | 1.000 | 0.260 |

### C_detailed_7

| state | share | n | roll_next_month | roll_next_month_bucket_std | exit_8plus_within_3m_bucket_std | exit_8plus_within_k | cure_within_k | median_bucket_change_k | same_state_next_month | kept_or_stabilized_next_month | left_spine_next_month |
|---|---|---|---|---|---|---|---|---|---|---|---|
| early_payment_default | 0.044 | 877 | 0.909 | 0.909 | 0.625 | 0.986 | 0.000 | 4.000 | 0.890 | 0.890 | 0.210 |
| stabilized | 0.081 | 1624 | 0.474 | 0.508 | 0.425 | 0.587 | 0.046 | 3.000 | 0.600 | 0.600 | 0.210 |
| repeat_delinquent | 0.150 | 3002 | 0.838 | 0.831 | 0.627 | 0.934 | 0.022 | 3.000 | 0.985 | 1.000 | 0.288 |
| straight_roller_seasoned | 0.521 | 10419 | 0.851 | 0.847 | 0.620 | 0.945 | 0.007 | 3.000 | 0.984 | 1.000 | 0.262 |
| straight_roller_early_life | 0.046 | 915 | 0.850 | 0.838 | 0.627 | 0.951 | 0.014 | 3.000 | 0.971 | 0.997 | 0.290 |
| slow_roller_intermittent | 0.101 | 2013 | 0.824 | 0.821 | 0.624 | 0.919 | 0.048 | 3.000 | 0.964 | 1.000 | 0.259 |
| slow_roller_erratic | 0.058 | 1150 | 0.846 | 0.842 | 0.627 | 0.937 | 0.017 | 3.000 | 0.982 | 1.000 | 0.260 |

### Is one paid month enough to separate slow from straight rollers?

| group | share_of_spine | roll_next_month_bucket_std | exit_8plus_within_3m_bucket_std |
|---|---|---|---|
| slow roller: exactly one hold | 0.073 | 0.825 | 0.657 |
| slow roller: more than one payment | 0.100 | 0.822 | 0.650 |
| straight roller | 0.703 | 0.851 | 0.648 |

### Stabilized bounce-backs over the 6 backtest months (10,000 accounts)

Share of ever-stabilized accounts that left stabilized and came back while staying in the spine (S . S):

| stabilized rule | ever_stabilized | bounce_back_share_of_ever_stabilized | mean_status_changes_per_account |
|---|---|---|---|
| with_long_run_clause | 0.132 | 0.047 | 0.123 |
| bank_rule_only | 0.125 | 0.055 | 0.125 |

## 5b. Run-up holds by calendar month (months before today)

Each month is compared with its neighbours (±2 months); a month far above them points to a system artefact (cycle-date change, reversal batch, deferral), not customer behaviour. Largest month / neighbour-median ratio: 1.25

| months_ago | share_of_runup_holds |
|---|---|
| 1 | 0.067 |
| 2 | 0.098 |
| 3 | 0.126 |
| 4 | 0.124 |
| 5 | 0.105 |
| 6 | 0.071 |
| 7 | 0.050 |
| 8 | 0.047 |
| 9 | 0.042 |
| 10 | 0.038 |
| 11 | 0.036 |
| 12 | 0.035 |
| 13 | 0.032 |
| 14 | 0.026 |
| 15 | 0.026 |
| 16 | 0.022 |
| 17 | 0.014 |
| 18 | 0.011 |
| 19 | 0.010 |
| 20 | 0.007 |
| 21 | 0.005 |
| 22 | 0.004 |
| 23 | 0.003 |
| 24 | 0.001 |
| 25 | 0.001 |
| 26 | 0.000 |
| 27 | 0.000 |
| 28 | 0.000 |
| 29 | 0.000 |
| 30 | 0.000 |
| 31 | 0.000 |
| 32 | 0.000 |
| 33 | 0.000 |
| 34 | 0.000 |
| 35 | 0.000 |
| 36 | 0.000 |

## 6. Threshold sweeps (backtest population). Parameters marked [business] in states.py are agreed definitions — the sweeps show sensitivity; they are not a menu for matching a share.

### epd_max_history

| epd_max_history | share | exit_within_k |
|---|---|---|
| 2 | 0.019 | 0.989 |
| 3 | 0.044 | 0.986 |
| 4 | 0.045 | 0.982 |
| 6 | 0.050 | 0.976 |
| 9 | 0.058 | 0.974 |
| 12 | 0.068 | 0.966 |

### stabilized_min_in_band

| stabilized_min_in_band | share | roll_next_month | still_stabilized_next_month |
|---|---|---|---|
| 4 | 0.141 | 0.567 | 0.564 |
| 5 | 0.081 | 0.474 | 0.600 |
| 6 | 0.053 | 0.420 | 0.663 |

### repeat_delinquent

| repeat_min_prior_peak | repeat_window_months | share |
|---|---|---|
| 2 | 12 | 0.122 |
| 2 | 24 | 0.173 |
| 2 | 36 | 0.184 |
| 2 | any | 0.875 |
| 3 | 12 | 0.106 |
| 3 | 24 | 0.150 |
| 3 | 36 | 0.163 |
| 3 | any | 0.875 |
| 4 | 12 | 0.037 |
| 4 | 24 | 0.042 |
| 4 | 36 | 0.045 |
| 4 | any | 0.875 |

### straight_max_runup

| straight_max_runup | straight_share | slow_share |
|---|---|---|
| 3 | 0.703 | 0.172 |
| 4 | 0.775 | 0.100 |
| 5 | 0.846 | 0.029 |

### seasoned_min_months

| seasoned_min_months | seasoned | early_life |
|---|---|---|
| 12 | 0.521 | 0.046 |
| 18 | 0.485 | 0.082 |
| 24 | 0.444 | 0.123 |
| 36 | 0.361 | 0.206 |

### paying_since_4_test

| paying_since_4_min_rate | share | still_paying_since_4_next_month | stability_of_fixed_states | stability_of_fixed_states_without_q3 |
|---|---|---|---|---|
| 0.340 | 0.201 | 0.708 | 0.890 | 0.981 |
| 0.500 | 0.181 | 0.588 | 0.891 | 0.981 |
| 0.670 | 0.072 | 0.283 | 0.950 | 0.981 |

## 7. Clustering the residual (after EPD and stabilized) — agreement (ARI) with each option. Diagnostic only: a finer partition built on the clustered features always gains ARI, so this is not evidence for B over A.

| k | agree_A_minimal_4 | agree_B_balanced_6 | agree_C_detailed_7 |
|---|---|---|---|
| 2 | -0.065 | 0.367 | 0.347 |
| 3 | 0.296 | 0.559 | 0.568 |
| 4 | 0.166 | 0.401 | 0.405 |
| 5 | 0.114 | 0.307 | 0.306 |
| 6 | 0.111 | 0.296 | 0.315 |
| 7 | 0.101 | 0.280 | 0.298 |
| 8 | 0.168 | 0.364 | 0.383 |

## 8. Most common journey shapes and motifs

Shapes (N clean, R roll, H hold = paid one month, P paid 2+ months; run lengths banded; shared by >= 10 accounts):

| shape | n | top_label | purity | share | cum_share |
|---|---|---|---|---|---|
| N25+ R3+ | 3787 | straight_roller_seasoned | 1.000 | 0.189 | 0.189 |
| N13-24 R3+ | 821 | straight_roller_seasoned | 1.000 | 0.041 | 0.230 |
| N25+ R3+ H1 | 363 | straight_roller_seasoned | 1.000 | 0.018 | 0.249 |
| N7-12 R3+ | 334 | straight_roller_early_life | 0.683 | 0.017 | 0.265 |
| N2-3 R3+ | 274 | early_payment_default | 0.869 | 0.014 | 0.279 |
| N25+ R3+ H1 R1 | 248 | straight_roller_seasoned | 1.000 | 0.012 | 0.291 |
| R1 P1 R3+ | 234 | early_payment_default | 1.000 | 0.012 | 0.303 |
| N25+ R2 P1 R3+ | 217 | slow_roller | 0.931 | 0.011 | 0.314 |
| N1 R3+ | 202 | early_payment_default | 1.000 | 0.010 | 0.324 |
| R3+ | 186 | early_payment_default | 1.000 | 0.009 | 0.333 |
| N25+ R3+ P1 R3+ | 181 | straight_roller_seasoned | 1.000 | 0.009 | 0.342 |
| N25+ R3+ H1 R2 | 174 | straight_roller_seasoned | 1.000 | 0.009 | 0.351 |
| N25+ R1 H1 R3+ | 168 | slow_roller | 1.000 | 0.008 | 0.359 |
| N25+ R3+ P1 R1 | 165 | straight_roller_seasoned | 1.000 | 0.008 | 0.368 |
| N25+ R3+ P1 R2 | 113 | straight_roller_seasoned | 1.000 | 0.006 | 0.373 |
| N4-6 R3+ | 113 | straight_roller_early_life | 1.000 | 0.006 | 0.379 |
| N25+ R2 P1 R2 | 104 | slow_roller | 1.000 | 0.005 | 0.384 |
| N25+ R2 H1 R1 | 102 | slow_roller | 0.951 | 0.005 | 0.389 |
| N25+ R2 H1 R3+ | 99 | slow_roller | 0.980 | 0.005 | 0.394 |
| N25+ R2 P1 H1 R3+ | 77 | slow_roller | 1.000 | 0.004 | 0.398 |

4-grams by lift vs shuffled order:

| gram | support | lift | top_label | purity |
|---|---|---|---|---|
| RHHP | 0.092 | 92.500 | repeat_delinquent | 0.587 |
| HHPP | 0.023 | 66.286 | repeat_delinquent | 0.808 |
| HHPN | 0.073 | 36.600 | repeat_delinquent | 0.558 |
| HRHP | 0.029 | 30.684 | repeat_delinquent | 0.760 |
| RHRH | 0.099 | 29.970 | repeat_delinquent | 0.445 |
| RHPP | 0.023 | 28.250 | repeat_delinquent | 0.814 |
| RRHH | 0.075 | 25.390 | repeat_delinquent | 0.399 |
| PRHP | 0.012 | 23.300 | repeat_delinquent | 0.541 |
| RPRP | 0.096 | 23.096 | repeat_delinquent | 0.345 |
| HPPN | 0.041 | 19.927 | repeat_delinquent | 0.863 |
| RRPH | 0.047 | 18.096 | slow_roller | 0.302 |
| RRRH | 0.188 | 17.289 | straight_roller_seasoned | 0.549 |
| HRPP | 0.016 | 17.158 | repeat_delinquent | 0.706 |
| RHRP | 0.051 | 16.286 | repeat_delinquent | 0.602 |
| RRHP | 0.043 | 15.464 | repeat_delinquent | 0.691 |
