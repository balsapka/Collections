# UC1 stated block (A5 / A6) — Step 7 PROD run summary, month 2026-07-31

Run: `kedro run --env=dev --pipeline=crx_{cc,rl}_uc1_stated`, 2026-11-24, one run per `model_id`.
Evidence is the pipeline log for observation month **2026-07-31** only. All four runs completed
2 of 2 nodes (`build_crx_{cc,rl}_uc1_conversation_signals`, `build_crx_{cc,rl}_uc1_stated`).
Outputs: `crx_{cc,rl}_uc1_conversation_signals` and `crx_{cc,rl}_uc1_stated`.

This is a different month from `summary.md` (2026-08-31, run 2026-11-18). The 07-31 log shows only
three evidence classes (extracted, no_conversation, not_extracted); there is no `legacy_only`.

## Run configuration

| model_id | dlq_min | dlq_max | collateral_codes | horizon (months) | runtime (s) |
|---|---|---|---|---|---|
| cc_60_180 | 4 | 7 | WO, SK | 1 | 130.9 |
| rl_60_180 | 3 | 6 | WO, SK | 1 | 100.3 |
| cc_180_plus | 8 | 9 | none | 12 | 126.7 |
| rl_180_plus | 7 | 7 | WO, SK | 12 | 124.4 |

## Combined results (count, with % of n where logged)

| metric | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| n (accounts) | 18,397 | 3,728 | 316,738 | 54,819 |
| evidence: extracted | 891 (4.8%) | 334 (9.0%) | 107 (0.0%) | 68 (0.1%) |
| evidence: no_conversation | 13,493 (73.3%) | 2,746 (73.7%) | 316,409 (99.9%) | 54,629 (99.7%) |
| evidence: not_extracted | 4,013 (21.8%) | 648 (17.4%) | 222 (0.1%) | 122 (0.2%) |
| A5: able | 89 (0.5%) | 34 (0.9%) | 27 (0.0%) | 15 (0.0%) |
| A5: partly_able | 325 (1.8%) | 126 (3.4%) | 32 (0.0%) | 18 (0.0%) |
| A5: unable | 180 (1.0%) | 65 (1.7%) | 14 (0.0%) | 9 (0.0%) |
| A5: not_stated | 297 (1.6%) | 109 (2.9%) | 34 (0.0%) | 26 (0.0%) |
| A5: no_evidence | 17,506 (95.2%) | 3,394 (91.0%) | 316,631 (100.0%) | 54,751 (99.9%) |
| A6: pays_in_full | 128 (0.7%) | 59 (1.6%) | 25 (0.0%) | 19 (0.0%) |
| A6: partly_or_later | 594 (3.2%) | 228 (6.1%) | 67 (0.0%) | 26 (0.0%) |
| A6: refuses | 49 (0.3%) | 13 (0.3%) | 4 (0.0%) | 3 (0.0%) |
| A6: not_stated | 120 (0.7%) | 34 (0.9%) | 11 (0.0%) | 20 (0.0%) |
| A6: no_evidence | 17,506 (95.2%) | 3,394 (91.0%) | 316,631 (100.0%) | 54,751 (99.9%) |
| unlogged flag = 1 | 239 (1.3%) | 137 (3.7%) | 63 (0.0%) | 38 (0.1%) |
| unlogged flag = 0 | 652 (3.5%) | 197 (5.3%) | 44 (0.0%) | 30 (0.1%) |
| unlogged flag = None | 17,506 (95.2%) | 3,394 (91.0%) | 316,631 (100.0%) | 54,751 (99.9%) |

`unlogged flag` is `stated_promise_unlogged_flag`.

## Derived (computed from the counts above, not logged)

| metric | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| flag=1 share of extracted | 26.8% | 41.0% | 58.9% | 55.9% |
| extracted / (extracted + not_extracted) | 18.2% | 34.0% | 32.5% | 35.8% |

## Checks (all four models pass)

- Evidence classes sum to n.
- A5 states other than `no_evidence` sum to `extracted`; the same holds for A6.
- `no_evidence` = `no_conversation` + `not_extracted` (= None count of the unlogged flag).
- Flag 0 + flag 1 = `extracted`.

## Reading

- Conversation evidence exists mainly in the 60-180 ranges. cc_60_180 has 4.8% extracted and
  rl_60_180 has 9.0%; the 180+ ranges are at or below 0.1% because 99.7-99.9% of accounts have no
  conversation.
- Where evidence exists, `partly_or_later` is the most common A6 state in every model. `refuses`
  is rare (3 to 49 accounts per model).
- 21.8% of cc_60_180 and 17.4% of rl_60_180 accounts had a conversation that was not extracted.
  Those are the largest recoverable evidence gaps.
- The share of promises not found in the promise log is higher in the 180+ models (55.9-58.9% of
  extracted) than in cc_60_180 (26.8%). The 180+ extracted counts are small (68 and 107).

---

# Compare pipeline (`crx_{cc,rl}_b31_compare`) - Step 7 PROD run, 2026-11-24

Run: `kedro run --env=dev --pipeline=crx_{cc,rl}_b31_compare`, one run per `model_id`. Each run
prints four blocks: B31 ROWS, B31 DIST, B31 OLD NEW and B31 PAID. UC1 month is **2026-07-31**; the
outcome in B31 PAID is the next month. In OLD NEW, old = the 2026-08-31 month (`summary.md`) and
new = the 2026-07-31 month, matched per account, so it compares two different months.

Conventions: `<10` is a count suppressed by the log; `-` means the row was not printed for that
model. In PAID tables a cell is `n due%/any%` (paid_due % / paid_any %), e.g. `891 16.3/18.3`.
Abbreviations: A3 `k` = kept, `pk` = partly_kept, `pr` = promised, `np` = no_promise;
A3 state `hi` / `mod` / `lo` = payment_credibility_high / moderate / low.

Runtime (s): cc_60_180 140.3, rl_60_180 102.6, cc_180_plus 219.1, rl_180_plus 157.8. All four
completed 1 of 1 tasks.

## B31 ROWS - rows per month (UC1 value present only in 2026-07-31, where it is 100%)

| month | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| 2026-01-31 | 14,664 | 2,324 | 305,257 | 52,657 |
| 2026-02-28 | 14,576 | 2,213 | 306,854 | 52,882 |
| 2026-03-31 | 14,455 | 2,218 | 308,742 | 53,270 |
| 2026-04-30 | 14,671 | 2,661 | 310,709 | 53,615 |
| 2026-05-31 | 15,890 | 3,096 | 312,626 | 54,006 |
| 2026-06-30 | 16,982 | 3,514 | 314,827 | 54,383 |
| 2026-07-31 (all with UC1) | 18,397 | 3,728 | 316,738 | 54,819 |
| 2026-08-31 | 19,292 | 3,985 | 318,663 | 55,371 |

## B31 DIST - 2026-07-31

The `uc1_evidence`, `a5_state`, `a6_state` and `stated_promise_unlogged_flag` counts equal the
Step 7 run above. Extra splits (count, % of UC1 rows unless noted):

| metric | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| a5_confidence LOW | 594 (66.7%) | 224 (67.1%) | 73 (68.2%) | 42 (61.8%) |
| a5_confidence MEDIUM | - | <10 (0.3%) | - | - |
| a5_confidence N/A | 297 (33.3%) | 109 (32.6%) | 34 (31.8%) | 26 (38.2%) |
| a6_confidence LOW | 769 (86.3%) | 300 (89.8%) | 96 (89.7%) | 48 (70.6%) |
| a6_confidence MEDIUM | <10 (0.2%) | - | - | - |
| a6_confidence N/A | 120 (13.5%) | 34 (10.2%) | 11 (10.3%) | 20 (29.4%) |
| verify_stated_ability = 1 | 50 (5.6%) | 43 (12.9%) | 12 (11.2%) | 13 (19.1%) |
| verify_stated_ability = 0 | 841 (94.4%) | 291 (87.1%) | 95 (88.8%) | 55 (80.9%) |
| stated_dispute customer_scammed | 15 (1.7%) | - | <10 (0.9%) | - |
| stated_dispute none | 628 (70.5%) | 271 (81.1%) | 78 (72.9%) | 44 (64.7%) |
| stated_dispute other | 28 (3.1%) | <10 (1.2%) | <10 (2.8%) | <10 (2.9%) |
| stated_dispute system_problem | 220 (24.7%) | 59 (17.7%) | 25 (23.4%) | 22 (32.4%) |
| stated_request_flag = 1 | 693 (77.8%) | 263 (78.7%) | 74 (69.2%) | 55 (80.9%) |
| stated_request_flag = 0 | 198 (22.2%) | 71 (21.3%) | 33 (30.8%) | 13 (19.1%) |

Reach x evidence (count, % of all accounts in n):

| reach / evidence | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| non_reachable / extracted | 443 (2.4%) | 154 (4.1%) | 25 (0.0%) | 26 (0.0%) |
| non_reachable / no_conversation | 9221 (50.1%) | 1545 (41.4%) | 20940 (6.6%) | 2876 (5.2%) |
| non_reachable / not_extracted | 2487 (13.5%) | 332 (8.9%) | 49 (0.0%) | 46 (0.1%) |
| reachable / extracted | 398 (2.2%) | 142 (3.8%) | 61 (0.0%) | 36 (0.1%) |
| reachable / no_conversation | 2441 (13.3%) | 681 (18.3%) | 11896 (3.8%) | 2604 (4.8%) |
| reachable / not_extracted | 1207 (6.6%) | 241 (6.5%) | 105 (0.0%) | 61 (0.1%) |
| unknown / extracted | 50 (0.3%) | 38 (1.0%) | 21 (0.0%) | <10 (0.0%) |
| unknown / no_conversation | 1831 (10.0%) | 520 (13.9%) | 283573 (89.5%) | 49149 (89.7%) |
| unknown / not_extracted | 319 (1.7%) | 75 (2.0%) | 68 (0.0%) | 15 (0.0%) |

## B31 OLD NEW - old (2026-08-31) | new (2026-07-31), accounts per cell

`None` = the account has no row in that month. Percentages are in the logs and are omitted here.

uc1_evidence old | new:

| old / new | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| None / extracted | 142 | 79 | <10 | - |
| None / no_conversation | 3316 | 712 | 1080 | 99 |
| None / not_extracted | 555 | 138 | 11 | <10 |
| extracted / None | 255 | 88 | 70 | 59 |
| extracted / extracted | 657 | 249 | 88 | 65 |
| extracted / not_extracted | 79 | 27 | 26 | 21 |
| legacy_only / None | 20 | <10 | 39 | <10 |
| legacy_only / extracted | <10 | <10 | <10 | <10 |
| legacy_only / not_extracted | 37 | <10 | 34 | 14 |
| no_conversation / None | 3210 | 808 | 2679 | 502 |
| no_conversation / no_conversation | 10177 | 2034 | 315329 | 54530 |
| not_extracted / None | 1423 | 281 | 235 | 87 |
| not_extracted / extracted | 83 | - | <10 | - |
| not_extracted / not_extracted | 3342 | 474 | 151 | 86 |

a5_state old | new:

| old / new | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| None / able | 22 | 12 | <10 | - |
| None / no_evidence | 3871 | 850 | 1091 | 100 |
| None / not_stated | 59 | 24 | <10 | - |
| None / partly_able | 43 | 22 | <10 | - |
| None / unable | 18 | 21 | - | - |
| able / None | 58 | 11 | 10 | <10 |
| able / able | 64 | 22 | 25 | 14 |
| able / partly_able | <10 | <10 | <10 | <10 |
| able / unable | <10 | - | - | <10 |
| no_evidence / None | 4653 | 1098 | 2953 | 593 |
| no_evidence / no_evidence | 13556 | 2517 | 315514 | 54630 |
| no_evidence / not_stated | 80 | <10 | <10 | <10 |
| no_evidence / partly_able | <10 | - | - | - |
| no_evidence / unable | 10 | - | <10 | - |
| not_stated / None | 55 | 18 | 35 | 23 |
| not_stated / no_evidence | 79 | 27 | 26 | 21 |
| not_stated / not_stated | 158 | 79 | 22 | 23 |
| not_stated / unable | <10 | <10 | <10 | <10 |
| partly_able / None | 115 | 49 | 18 | 15 |
| partly_able / able | <10 | - | <10 | <10 |
| partly_able / partly_able | 274 | 102 | 28 | 16 |
| partly_able / unable | 27 | <10 | - | <10 |
| unable / None | 27 | 10 | <10 | 14 |
| unable / partly_able | <10 | <10 | - | - |
| unable / unable | 115 | 38 | <10 | <10 |

a6_state old | new:

| old / new | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| None / no_evidence | 3871 | 850 | 1091 | 100 |
| None / not_stated | 24 | <10 | <10 | - |
| None / partly_or_later | 84 | 51 | <10 | - |
| None / pays_in_full | 28 | 13 | <10 | - |
| None / refuses | <10 | <10 | - | - |
| no_evidence / None | 4653 | 1098 | 2953 | 593 |
| no_evidence / no_evidence | 13556 | 2517 | 315514 | 54630 |
| no_evidence / not_stated | 23 | <10 | <10 | <10 |
| no_evidence / partly_or_later | 61 | <10 | 10 | <10 |
| no_evidence / pays_in_full | <10 | - | <10 | - |
| no_evidence / refuses | <10 | - | - | - |
| not_stated / None | 30 | 12 | 26 | 19 |
| not_stated / no_evidence | 79 | 27 | 26 | 21 |
| not_stated / not_stated | 73 | 23 | <10 | 19 |
| not_stated / partly_or_later | 29 | 10 | <10 | - |
| not_stated / pays_in_full | <10 | - | <10 | - |
| not_stated / refuses | <10 | <10 | - | <10 |
| partly_or_later / None | 145 | 56 | 24 | 27 |
| partly_or_later / partly_or_later | 385 | 151 | 38 | 22 |
| partly_or_later / pays_in_full | 10 | <10 | <10 | <10 |
| partly_or_later / refuses | <10 | <10 | - | - |
| pays_in_full / None | 74 | 18 | 19 | <10 |
| pays_in_full / partly_or_later | 33 | 12 | 10 | <10 |
| pays_in_full / pays_in_full | 83 | 44 | 21 | 18 |
| pays_in_full / refuses | <10 | - | - | - |
| refuses / None | <10 | <10 | <10 | <10 |
| refuses / partly_or_later | <10 | - | - | - |
| refuses / refuses | 30 | <10 | <10 | <10 |

## B31 PAID - 2026-07-31, outcome = next month (cell = `n due%/any%`)

By evidence class:

| evidence | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| extracted | 891 16.3/18.3 | 334 31.4/40.7 | 107 4.7/8.4 | 68 8.8/16.2 |
| no_conversation | 13493 9.1/10.2 | 2746 20.1/24.9 | 316409 1.1/1.7 | 54629 1.3/2.1 |
| not_extracted | 4013 10.4/12.4 | 648 20.5/26.9 | 222 7.2/13.5 | 122 12.3/16.4 |

AUC inside strata:

| AUC | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| A5 in A1 unknown | 0.613 (n 314) | 0.472 (n 98) | no AUC (one outcome only) | 0.143 (n 8) |
| A6 in A3 no_promise | 0.579 (n 122) | 0.521 (n 126) | no AUC (one outcome only) | 0.810 (n 22) |

A1 x A5:

| A1 / A5 | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| high / able | <10 | <10 | <10 | <10 |
| high / no_evidence | 263 20.9/22.8 | 25 48.0/48.0 | 704 9.5/13.2 | 53 34.0/41.5 |
| high / not_stated | 11 9.1/18.2 | <10 | <10 | <10 |
| high / partly_able | 14 0.0/0.0 | - | <10 | <10 |
| high / unable | <10 | - | - | - |
| low / able | 28 25.0/25.0 | 14 35.7/42.9 | <10 | 10 10.0/10.0 |
| low / no_evidence | 4923 11.2/13.0 | 1673 20.5/26.2 | 25712 3.0/5.1 | 5828 3.8/7.2 |
| low / not_stated | 109 18.3/19.3 | 62 21.0/30.6 | 16 12.5/12.5 | 19 15.8/21.1 |
| low / partly_able | 122 22.1/24.6 | 69 47.8/66.7 | 18 0.0/5.6 | 11 0.0/18.2 |
| low / unable | 75 14.7/14.7 | 37 24.3/32.4 | 11 0.0/0.0 | <10 |
| moderate / able | 19 0.0/0.0 | <10 | <10 | <10 |
| moderate / no_evidence | 2633 15.3/17.6 | 301 35.2/41.5 | 19703 6.2/9.3 | 1884 12.1/17.9 |
| moderate / not_stated | 76 11.8/15.8 | 16 43.8/50.0 | 12 0.0/0.0 | <10 |
| moderate / partly_able | 81 21.0/21.0 | 24 41.7/50.0 | 11 9.1/18.2 | <10 |
| moderate / unable | 31 16.1/22.6 | <10 | <10 | - |
| unknown / able | 33 27.3/30.3 | 13 23.1/23.1 | <10 | <10 |
| unknown / no_evidence | 9687 6.5/7.3 | 1395 16.0/20.2 | 270512 0.6/0.9 | 46986 0.5/0.9 |
| unknown / not_stated | 101 13.9/16.8 | 30 13.3/13.3 | <10 | <10 |
| unknown / partly_able | 108 15.7/19.4 | 33 27.3/33.3 | <10 | <10 |
| unknown / unable | 72 6.9/6.9 | 22 36.4/40.9 | <10 | <10 |

A3 level x A6:

| A3 level / A6 | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| k / no_evidence | 606 22.8/25.2 | 94 42.6/48.9 | 221 22.2/23.5 | 64 31.2/34.4 |
| k / not_stated | <10 | <10 | - | - |
| k / partly_or_later | 18 16.7/16.7 | 16 43.8/43.8 | - | - |
| k / pays_in_full | <10 | <10 | - | - |
| k / refuses | <10 | - | - | - |
| np / no_evidence | 10085 4.1/4.9 | 2286 13.9/18.1 | 300733 0.6/0.9 | 52561 0.6/1.3 |
| np / not_stated | 33 3.0/3.0 | 16 18.8/37.5 | <10 | <10 |
| np / partly_or_later | 69 8.7/8.7 | 76 23.7/32.9 | 17 0.0/0.0 | <10 |
| np / pays_in_full | <10 | 27 22.2/29.6 | <10 | <10 |
| np / refuses | 12 8.3/8.3 | <10 | <10 | <10 |
| pk / no_evidence | 4157 18.2/20.3 | 552 35.0/41.3 | 4850 20.8/23.3 | 816 26.7/32.6 |
| pk / not_stated | 44 25.0/27.3 | 12 8.3/16.7 | <10 | <10 |
| pk / partly_or_later | 344 20.1/23.8 | 72 27.8/40.3 | 22 9.1/9.1 | <10 |
| pk / pays_in_full | 84 20.2/21.4 | 16 56.2/62.5 | <10 | <10 |
| pk / refuses | 20 10.0/10.0 | <10 | <10 | - |
| pr / no_evidence | 2658 12.5/14.2 | 462 29.0/36.8 | 10827 8.4/14.4 | 1310 9.5/16.3 |
| pr / not_stated | 37 10.8/13.5 | <10 | <10 | <10 |
| pr / partly_or_later | 163 14.7/16.0 | 64 43.8/53.1 | 28 0.0/7.1 | 11 0.0/18.2 |
| pr / pays_in_full | 31 12.9/12.9 | 13 46.2/53.8 | 15 20.0/33.3 | <10 |
| pr / refuses | 14 0.0/0.0 | <10 | - | <10 |

A3 state x A6:

| A3 state / A6 | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| hi / no_evidence | 2053 35.2/38.0 | 270 52.2/60.4 | 2081 26.8/30.1 | 509 38.3/44.6 |
| hi / not_stated | 20 25.0/30.0 | <10 | <10 | <10 |
| hi / partly_or_later | 125 29.6/33.6 | 40 45.0/55.0 | 13 7.7/7.7 | <10 |
| hi / pays_in_full | 25 36.0/40.0 | <10 | <10 | <10 |
| hi / refuses | <10 | <10 | - | - |
| mod / no_evidence | 5301 11.7/13.8 | 1019 30.1/38.3 | 12805 11.2/18.3 | 2583 13.8/21.7 |
| mod / not_stated | 55 14.5/16.4 | 15 6.7/20.0 | <10 | 14 14.3/21.4 |
| mod / partly_or_later | 340 15.6/18.2 | 115 34.8/45.2 | 34 2.9/8.8 | 17 0.0/17.6 |
| mod / pays_in_full | 86 16.3/16.3 | 33 39.4/45.5 | 19 10.5/21.1 | 11 9.1/9.1 |
| mod / refuses | 23 8.7/8.7 | <10 | <10 | <10 |
| lo / no_evidence | 10152 3.0/3.5 | 2105 11.2/14.4 | 301745 0.6/0.9 | 51659 0.3/0.8 |
| lo / not_stated | 45 6.7/6.7 | 13 23.1/46.2 | <10 | <10 |
| lo / partly_or_later | 129 9.3/10.1 | 73 20.5/28.8 | 20 0.0/0.0 | <10 |
| lo / pays_in_full | 17 0.0/0.0 | 17 17.6/29.4 | <10 | <10 |
| lo / refuses | 19 0.0/0.0 | 10 20.0/20.0 | <10 | <10 |

Stated reason (UC1 rows), and inside A1 unknown:

| reason | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| None | 244 18.4/19.3 | 92 20.7/30.4 | 30 0.0/0.0 | 27 14.8/18.5 |
| has_employment | 220 17.3/20.0 | 66 43.9/54.5 | 30 10.0/10.0 | 16 0.0/18.8 |
| increased_obligations | 82 20.7/25.6 | 37 45.9/48.6 | 14 0.0/21.4 | <10 |
| lost_employment | 249 14.1/16.1 | 103 23.3/35.0 | 23 4.3/4.3 | 15 13.3/20.0 |
| reduced_employment | 96 10.4/11.5 | 36 44.4/50.0 | 10 10.0/20.0 | <10 |
| A1 unk: None | 81 17.3/17.3 | 29 10.3/10.3 | <10 | <10 |
| A1 unk: has_employment | 67 14.9/17.9 | 15 40.0/46.7 | <10 | <10 |
| A1 unk: increased_obl | 23 30.4/39.1 | 11 45.5/45.5 | <10 | - |
| A1 unk: lost_employment | 120 10.8/13.3 | 37 21.6/27.0 | <10 | <10 |
| A1 unk: reduced_employment | 23 4.3/8.7 | <10 | <10 | <10 |

Verify flag inside A1 low (UC1 rows):

| verify flag | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| 0 | 284 19.4/20.4 | 139 33.1/46.8 | 40 2.5/5.0 | 33 9.1/21.2 |
| 1 | 50 20.0/22.0 | 43 32.6/41.9 | 12 8.3/8.3 | 13 7.7/7.7 |

A3 level x promise (`no_uc1` = no UC1 evidence):

| A3 level / promise | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| k / no_uc1 | 606 22.8/25.2 | 94 42.6/48.9 | 221 22.2/23.5 | 64 31.2/34.4 |
| k / other_reading | <10 | <10 | - | - |
| k / paying_no_amount_date | <10 | <10 | - | - |
| k / said_logged | <10 | <10 | - | - |
| k / said_unlogged | 11 0.0/0.0 | 11 54.5/54.5 | - | - |
| np / no_uc1 | 10085 4.1/4.9 | 2286 13.9/18.1 | 300733 0.6/0.9 | 52561 0.6/1.3 |
| np / other_reading | 45 4.4/4.4 | 23 17.4/30.4 | <10 | <10 |
| np / paying_no_amount_date | 27 7.4/7.4 | 43 20.9/25.6 | <10 | <10 |
| np / said_logged | <10 | - | - | - |
| np / said_unlogged | 46 8.7/8.7 | 60 25.0/36.7 | 19 0.0/0.0 | 16 6.2/18.8 |
| pk / no_uc1 | 4157 18.2/20.3 | 552 35.0/41.3 | 4850 20.8/23.3 | 816 26.7/32.6 |
| pk / other_reading | 64 20.3/21.9 | 15 13.3/20.0 | <10 | <10 |
| pk / paying_no_amount_date | 61 19.7/21.3 | 26 23.1/42.3 | <10 | <10 |
| pk / said_logged | 234 18.4/22.2 | 29 48.3/55.2 | <10 | - |
| pk / said_unlogged | 133 23.3/26.3 | 33 27.3/36.4 | 20 10.0/10.0 | 12 8.3/8.3 |
| pr / no_uc1 | 2658 12.5/14.2 | 462 29.0/36.8 | 10827 8.4/14.4 | 1310 9.5/16.3 |
| pr / other_reading | 51 7.8/9.8 | <10 | <10 | 10 20.0/30.0 |
| pr / paying_no_amount_date | 41 17.1/19.5 | 19 36.8/42.1 | 12 8.3/8.3 | <10 |
| pr / said_logged | 104 12.5/13.5 | 25 28.0/44.0 | <10 | <10 |
| pr / said_unlogged | 49 16.3/16.3 | 33 60.6/66.7 | 24 8.3/20.8 | 10 0.0/20.0 |

Promise reading, stated dispute, request, A6 by confidence:

| segment | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
|---|---|---|---|---|
| promise: no_uc1 | 17506 9.4/10.7 | 3394 20.2/25.3 | 316631 1.2/1.8 | 54751 1.3/2.2 |
| promise: other_reading | 169 11.8/13.0 | 47 21.3/31.9 | 15 0.0/0.0 | 23 17.4/21.7 |
| promise: paying_no_amt_date | 134 17.2/18.7 | 91 24.2/33.0 | 18 5.6/5.6 | <10 |
| promise: said_logged | 349 16.9/19.8 | 59 39.0/49.2 | 11 0.0/9.1 | <10 |
| promise: said_unlogged | 239 18.0/19.7 | 137 36.5/45.3 | 63 6.3/11.1 | 38 5.3/15.8 |
| dispute = 0 | 628 15.4/17.5 | 271 29.9/38.0 | 78 3.8/7.7 | 44 9.1/15.9 |
| dispute = 1 | 263 18.3/20.2 | 63 38.1/52.4 | 29 6.9/10.3 | 24 8.3/16.7 |
| request = 0 | 198 18.7/19.7 | 71 25.4/35.2 | 33 9.1/15.2 | 13 0.0/0.0 |
| request = 1 | 693 15.6/17.9 | 263 33.1/42.2 | 74 2.7/5.4 | 55 10.9/20.0 |
| A6 LOW / partly_or_later | 592 17.1/19.6 | 228 32.0/41.7 | 67 3.0/6.0 | 26 0.0/15.4 |
| A6 LOW / pays_in_full | 128 18.0/18.8 | 59 37.3/44.1 | 25 12.0/20.0 | 19 10.5/10.5 |
| A6 LOW / refuses | 49 8.2/8.2 | 13 23.1/23.1 | <10 | <10 |
| A6 MEDIUM / partly_or_later | <10 | - | - | - |
| A6 N/A / not_stated | 120 13.3/15.0 | 34 20.6/35.3 | 11 0.0/0.0 | 20 15.0/20.0 |

## Reading (compare)

- UC1 values exist for one month only (2026-07-31) in the old table, so no month-on-month trend
  can be drawn from B31 ROWS.
- Accounts with extracted evidence pay more than those with no conversation in every model.
  paid_due is 16.3 vs 9.1 (cc_60_180), 31.4 vs 20.1 (rl_60_180), 4.7 vs 1.1 (cc_180_plus) and
  8.8 vs 1.3 (rl_180_plus). Evidence class is not controlled for A1 or A3, so this is not a
  causal lift.
- A3 separates payment far more than A5 or A6. With no A6 evidence, paid_due for `hi` vs `lo` is
  35.2 vs 3.0 (cc_60_180), 52.2 vs 11.2 (rl_60_180), 26.8 vs 0.6 (cc_180_plus) and 38.3 vs 0.3
  (rl_180_plus).
- A5 inside A1 unknown has an AUC of 0.613 (n 314) in cc_60_180 and 0.472 (n 98) in rl_60_180.
  A6 inside A3 no_promise has 0.579 (n 122) and 0.521 (n 126). The 180+ models have too few
  rows for a usable AUC (one outcome only in cc_180_plus; n 8 and n 22 in rl_180_plus).
- The OLD NEW comparison mixes two months. About 2 in 3 old `extracted` accounts in cc_60_180
  (657 of 991) stay extracted, 255 have no 07-31 row and 79 become `not_extracted`.
  83 old `not_extracted` accounts become `extracted`.
- Cells under 10 are suppressed, so most 180+ cells below the evidence-class level cannot be read.
