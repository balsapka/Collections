# A3 check results, cc_60_180 + rl_60_180 (bundle 17), verbatim from handoff 51 (2026-11-09)

Source: workplace `tmp_validation/a3_check/results_summary_cc_rl_60_180.md` (the UAT Sonnet's summary of the two check logs), transcribed from 8 photos. Review: `a3_check_review.md`.

# crx_cc_a3_check + crx_rl_a3_check — consolidated log summary (cc_60_180, rl_60_180)

| | CC | RL |
|---|---|---|
| Command | `kedro run --env=dev --pipeline=crx_cc_a3_check` | `kedro run --env=dev --pipeline=crx_rl_a3_check` |
| Run date | 2026-11-06 | 2026-11-09 |
| Duration | 225.8 sec | 351.2 sec |
| Tasks completed | 15/15 | 15/15 |
| Observation month | 2026-08-31 | 2026-08-31 |
| Rows (new = old, latest per account) | 19,292 | 3,985 |

"old" = previous A3 output (`a3_state_v1`); "payments" = rebuilt engine on payments; "dcore" = rebuilt engine on DCORE commitments.
In cross-tabs, "—" means the combination did not occur in that product. Cells show `n (%)`.

## A3 state distribution (new engine, month 2026-08-31)

| State | CC payments | CC dcore | RL payments | RL dcore |
|---|---:|---:|---:|---:|
| payment_credibility_high | 255 (1.3%) | 653 (3.4%) | 62 (1.6%) | 24 (0.6%) |
| payment_credibility_low | 3,920 (20.3%) | 3,893 (20.2%) | 1,004 (25.2%) | 1,062 (26.6%) |
| payment_credibility_moderate | 12,729 (66.0%) | 12,377 (64.2%) | 2,645 (66.4%) | 2,625 (65.9%) |
| payment_credibility_unknown | 2,388 (12.4%) | 2,369 (12.3%) | 274 (6.9%) | 274 (6.9%) |

## A3 OUTPUT

### old a3_state_v1 × new (payments)

| old | new | CC | RL |
|---|---|---:|---:|
| high | high | 225 (1.2%) | 21 (0.5%) |
| high | low | 3 (0.0%) | — |
| high | moderate | 406 (2.1%) | 5 (0.1%) |
| low | high | 19 (0.1%) | 21 (0.5%) |
| low | low | 3,457 (17.9%) | 873 (21.9%) |
| low | moderate | 6,105 (31.6%) | 713 (17.9%) |
| low | unknown | 1,691 (8.8%) | 176 (4.4%) |
| moderate | high | 11 (0.1%) | 20 (0.5%) |
| moderate | low | 454 (2.4%) | 131 (3.3%) |
| moderate | moderate | 6,217 (32.2%) | 1,926 (48.3%) |
| moderate | unknown | 82 (0.4%) | 22 (0.6%) |
| unknown | low | 4 (0.0%) | — |
| unknown | moderate | 3 (0.0%) | 1 (0.0%) |
| unknown | unknown | 615 (3.2%) | 76 (1.9%) |

### old × new (dcore)

| old | new | CC | RL |
|---|---|---:|---:|
| high | high | 586 (3.0%) | 23 (0.6%) |
| high | moderate | 48 (0.2%) | 3 (0.1%) |
| low | high | 10 (0.1%) | — |
| low | low | 3,476 (18.0%) | 936 (23.5%) |
| low | moderate | 6,100 (31.6%) | 672 (16.9%) |
| low | unknown | 1,686 (8.7%) | 175 (4.4%) |
| moderate | high | 57 (0.3%) | 1 (0.0%) |
| moderate | low | 404 (2.1%) | 126 (3.2%) |
| moderate | moderate | 6,228 (32.3%) | 1,950 (48.9%) |
| moderate | unknown | 75 (0.4%) | 22 (0.6%) |
| unknown | low | 9 (0.0%) | — |
| unknown | moderate | 5 (0.0%) | — |
| unknown | unknown | 608 (3.2%) | 77 (1.9%) |

### new dcore × new payments

| new dcore | new payments | CC | RL |
|---|---|---:|---:|
| high | high | 226 (1.2%) | 21 (0.5%) |
| high | moderate | 427 (2.2%) | 3 (0.1%) |
| low | low | 3,780 (19.6%) | 999 (25.1%) |
| low | moderate | 104 (0.5%) | 62 (1.6%) |
| low | unknown | 5 (0.0%) | 1 (0.0%) |
| moderate | high | 29 (0.2%) | 41 (1.0%) |
| moderate | low | 136 (0.7%) | 5 (0.1%) |
| moderate | moderate | 12,197 (63.2%) | 2,579 (64.7%) |
| moderate | unknown | 19 (0.1%) | — |
| unknown | low | 2 (0.0%) | — |
| unknown | moderate | 3 (0.0%) | 1 (0.0%) |
| unknown | unknown | 2,364 (12.3%) | 273 (6.9%) |

## A3 COMMITMENTS

### Dimension A level, dcore × payments

| dcore | payments | CC | RL |
|---|---|---:|---:|
| broken | broken | 1,676 (8.7%) | 73 (1.8%) |
| broken | kept | 11 (0.1%) | 38 (1.0%) |
| broken | partly_kept | 113 (0.6%) | 48 (1.2%) |
| broken | thin | 55 (0.3%) | 13 (0.3%) |
| kept | broken | 256 (1.3%) | 2 (0.1%) |
| kept | kept | 147 (0.8%) | 16 (0.4%) |
| kept | partly_kept | 78 (0.4%) | — |
| kept | thin | 27 (0.1%) | — |
| partly_kept | broken | 253 (1.3%) | 5 (0.1%) |
| partly_kept | kept | 25 (0.1%) | 19 (0.5%) |
| partly_kept | partly_kept | 249 (1.3%) | 84 (2.1%) |
| partly_kept | thin | 414 (2.1%) | 9 (0.2%) |
| thin | broken | 12 (0.1%) | — |
| thin | partly_kept | 114 (0.6%) | 111 (2.8%) |
| thin | thin | 15,862 (82.2%) | 3,567 (89.5%) |

### Instalments concluded / kept

| source | CC concluded | CC kept | RL concluded | RL kept |
|---|---:|---:|---:|---:|
| dcore | 17,841 | 6,910 | 1,210 | 291 |
| payments | 16,610 | 3,250 | 1,074 | 578 |

### old level × new (payments)

| old | new | CC | RL |
|---|---|---:|---:|
| broken | broken | 1,658 (8.6%) | 73 (1.8%) |
| broken | kept | 16 (0.1%) | 39 (1.0%) |
| broken | partly_kept | 152 (0.8%) | 61 (1.5%) |
| broken | thin | 640 (3.3%) | 83 (2.1%) |
| kept | broken | 258 (1.3%) | 2 (0.1%) |
| kept | kept | 140 (0.7%) | 15 (0.4%) |
| kept | partly_kept | 50 (0.3%) | 1 (0.0%) |
| kept | thin | 85 (0.4%) | 1 (0.0%) |
| partly_kept | broken | 281 (1.5%) | 5 (0.1%) |
| partly_kept | kept | 27 (0.1%) | 19 (0.5%) |
| partly_kept | partly_kept | 276 (1.4%) | 88 (2.2%) |
| partly_kept | thin | 1,061 (5.5%) | 62 (1.6%) |
| thin | partly_kept | 76 (0.4%) | 93 (2.3%) |
| thin | thin | 14,572 (75.5%) | 3,443 (86.4%) |

## A3 BROKEN

Each log prints two blocks, the first for the payments variant and the second for dcore (matching the state totals in the distribution table).

### Broken rows by B + C points

| B + C points | CC payments | CC dcore | RL payments | RL dcore |
|---:|---:|---:|---:|---:|
| 0 | 367 (1.9%) | 373 (1.9%) | 23 (0.6%) | 32 (0.8%) |
| 1 | 715 (3.7%) | 734 (3.8%) | 28 (0.7%) | 74 (1.9%) |
| 2 | 671 (3.5%) | 543 (2.8%) | 27 (0.7%) | 58 (1.5%) |
| 3 | 444 (2.3%) | 205 (1.1%) | 2 (0.1%) | 8 (0.2%) |

### State by broken-handling variant — payments

| product | variant | high | low | moderate | unknown |
|---|---|---:|---:|---:|---:|
| CC | v0_override | 255 (1.3%) | 5,007 (26.0%) | 11,642 (60.3%) | 2,388 (12.4%) |
| CC | v1_zero | 255 (1.3%) | 3,243 (16.8%) | 13,406 (69.5%) | 2,388 (12.4%) |
| CC | v2_minus1 | 255 (1.3%) | 3,918 (20.3%) | 12,731 (66.0%) | 2,388 (12.4%) |
| CC | v3_minus2 | 255 (1.3%) | 4,569 (23.7%) | 12,080 (62.6%) | 2,388 (12.4%) |
| RL | v0_override | 62 (1.6%) | 1,032 (25.9%) | 2,617 (65.7%) | 274 (6.9%) |
| RL | v1_zero | 62 (1.6%) | 978 (24.5%) | 2,671 (67.0%) | 274 (6.9%) |
| RL | v2_minus1 | 62 (1.6%) | 1,004 (25.2%) | 2,645 (66.4%) | 274 (6.9%) |
| RL | v3_minus2 | 62 (1.6%) | 1,030 (25.8%) | 2,619 (65.7%) | 274 (6.9%) |

### State by broken-handling variant — dcore

| product | variant | high | low | moderate | unknown |
|---|---|---:|---:|---:|---:|---:|
| CC | v0_override | 653 (3.4%) | 4,614 (23.9%) | 11,656 (60.4%) | 2,369 (12.3%) |
| CC | v1_zero | 653 (3.4%) | 3,198 (16.6%) | 13,072 (67.8%) | 2,369 (12.3%) |
| CC | v2_minus1 | 653 (3.4%) | 3,889 (20.2%) | 12,381 (64.2%) | 2,369 (12.3%) |
| CC | v3_minus2 | 653 (3.4%) | 4,413 (22.9%) | 11,857 (61.5%) | 2,369 (12.3%) |
| RL | v0_override | 24 (0.6%) | 1,125 (28.2%) | 2,562 (64.3%) | 274 (6.9%) |
| RL | v1_zero | 24 (0.6%) | 990 (24.8%) | 2,697 (67.7%) | 274 (6.9%) |
| RL | v2_minus1 | 24 (0.6%) | 1,062 (26.6%) | 2,625 (65.9%) | 274 (6.9%) |
| RL | v3_minus2 | 24 (0.6%) | 1,117 (28.0%) | 2,570 (64.5%) | 274 (6.9%) |

## A3 CONTACTS

### Flag counts

| flag | CC | RL |
|---|---:|---:|
| a3_refusal_flag | 857 | 185 |
| refusal_followed_by_plan | 20 | 1 |
| refusal_followed_by_payment | 38 | 20 |
| a3_dispute_flag | 74 | 0 |
| a3_hung_up_last | 443 | 41 |
| a3_no_pickup_after_contact | 1,344 | 329 |
| refusal without the 24-month cap | 857 | 185 |

### Last right-party disposition

| disposition | CC | RL |
|---|---:|---:|
| None | 8,721 (45.2%) | 1,440 (36.1%) |
| dispute | 74 (0.4%) | — |
| hung_up | 443 (2.3%) | 41 (1.0%) |
| paid | 2,168 (11.2%) | 545 (13.7%) |
| ptp | 3,128 (16.2%) | 678 (17.0%) |
| refusal | 908 (4.7%) | 206 (5.2%) |
| success | 3,850 (20.0%) | 1,075 (27.0%) |

### old strong negative × new refusal

| old strong negative | new refusal | CC | RL |
|---|---|---:|---:|
| None | False | 8,695 (45.1%) | 2,480 (62.2%) |
| None | True | 97 (0.5%) | 51 (1.3%) |
| broken_commitments | False | 2,343 (12.1%) | 247 (6.2%) |
| broken_commitments | True | 123 (0.6%) | 9 (0.2%) |
| no_response | False | 6,907 (35.8%) | 1,048 (26.3%) |
| no_response | True | 30 (0.2%) | 3 (0.1%) |
| refusal | False | 490 (2.5%) | 25 (0.6%) |
| refusal | True | 607 (3.1%) | 122 (3.1%) |

## A3 EPISODE

### Unknown reason

| reason | CC | RL |
|---|---:|---:|
| None | 16,904 (87.6%) | 3,711 (93.1%) |
| no_evidence | 2,388 (12.4%) | 274 (6.9%) |

### Dimension C reason × level

| reason | level | CC | RL |
|---|---|---:|---:|
| None | clean | 12,410 (64.3%) | 1,767 (44.3%) |
| None | no_record | 3,015 (15.6%) | 441 (11.1%) |
| None | not_clean | 3,862 (20.0%) | 1,777 (44.6%) |
| censored | no_record | 5 (0.0%) | — |

Rows with no record and window starting before the floor 2024-01-01: CC 26; RL not printed.

### Dimension B level

| level | CC | RL |
|---:|---:|---:|
| none | 14,459 (74.9%) | 2,261 (56.7%) |
| regular | 1,445 (7.5%) | 434 (10.9%) |
| some | 3,388 (17.6%) | 1,290 (32.4%) |


## Notes on specific spots
- **Does not tie out (CC only), as printed:** line 130 says the variant blocks match the state totals in the distribution table, but the CC v2_minus1 rows differ from the distribution table. Payments: line 147 has low 3,918 / moderate 12,731, line 20-21 has low 3,920 / moderate 12,729 (2 rows apart). dcore: line 160 has low 3,889 / moderate 12,381, line 20-21 has low 3,893 / moderate 12,377 (4 rows apart). The `new dcore x new payments` table (lines 67-78) agrees with the variant tables (its marginals are payments low 3,918 / moderate 12,731 and dcore low 3,889 / moderate 12,381), not with the distribution table. All of these sum to 19,292; high and unknown match everywhere. RL ties out everywhere (v2_minus1 = the distribution table). Copied as shown; check against the real file or log.
- Sum checks that pass (everything else): lines 19-22 add to 19,292 / 19,292 / 3,985 / 3,985; the three old x new tables and the dcore x payments tables add to 19,292 (CC) and 3,985 (RL); old broken = 2,466 (CC, lines 113-116 and line 199-200), old high = 634 (lines 30-32 = 49-50), old moderate = 6,764, old low = 11,272 in both old x new tables; Broken rows by B+C: payments 2,197 (CC) / 80 (RL) = the broken payments rows in lines 86-100 (1,676 + 256 + 253 + 12 and 73 + 2 + 5), dcore 1,855 (CC) / 172 (RL) = the broken dcore rows (1,676 + 11 + 113 + 55 and 73 + 38 + 48 + 13); the eight broken-handling variant rows add to 19,292 / 3,985 per product and block; `Last right-party disposition` adds to 19,292 / 3,985; `old strong negative x new refusal` adds to 19,292 / 3,985 and the `True` rows add to 857 / 185 (= `a3_refusal_flag`, lines 173, 179); Unknown reason, Dimension C and Dimension B each add to 19,292 / 3,985.
- Line 190 `refusal` disposition (908 CC / 206 RL) differs from `a3_refusal_flag` (857 / 185); different definitions, as printed.
- Line 179 `refusal without the 24-month cap` equals line 173 (857 / 185), as printed.
- Line 224: `RL not printed`, as written in the file.
- Table alignment markers: separators with `:` (right-aligned) are as shown; line 229 starts with `|---:|` (the level column is right-aligned, as printed); the first column separators elsewhere are plain `---`.
- Line 1 and the two headings with `—` use an em dash in the source; I typed it as shown.
- OCR-risk digits: nearly all counts and percentages (every table), especially lines 20-21, 67-78, 145-165 (the discrepancy above), 185-204 and 219-232; the durations 225.8 / 351.2 sec and the run date 2026-11-09 in lines 6-7.
