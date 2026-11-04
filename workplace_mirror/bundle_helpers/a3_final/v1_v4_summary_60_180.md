# A3 V1–V4 summary, cc_60_180 and rl_60_180 (UAT Sonnet, 2026-11-04)

Handoff 33 (5 photos, transcribed in chat from `tmp_validation/a3_v1_v4/summary.md`; numbers to be
checked against `results_cc_60_180.md` / `results_rl_60_180.md`). Prompt:
`sonnet_a3_v1_v4_prompt.md`. Claude's review: `v1_v4_review.md`.

# A3 V1-V4 summary - 60/180 models (cc_60_180, rl_60_180)

Evidence: `results_cc_60_180.md` (19,292 accounts) and `results_rl_60_180.md` (3,985 accounts), latest month
2026-08-31, anchor = A4 spell start (same month as the A3 `t0` on 19,290 / 19,292 CC, 3,964 / 3,985 RL). The 180+
models were not run. **Gap: RL V2 N1, N2, N4, the overlap matrix and the latest-contact stats failed** (Java heap
error) and are not in this summary.

## V1 - DCORE commitments

**Facts (same in both models).**
- `dcore_int_ptp` and `dcore_int_settlement` (intermediate) link agreement to plan (`promise_seqno` / `rps_seqno`,
 `event_date`, `is_cancelled`). `dcore_prm_promise_instalments` and `dcore_prm_settlement_schedule_instalments`
 (primary) carry `due_date`, `due_amount`, `payment_amount`, `instalment_status`.
- `payment_amount` is NULL on 63% / 55% (PTP / settlement) of CC and 72% / 67% of RL instalments. Plans cancelled:
 CC 5.3% / 9.0%, RL 3.2% / 6.0%.
- PTP status vs dcore's flags (CC): `B` = overdue (98.6% of all `B`), `F` = paid (98.1%), `C` = nulled, `A` = not
 yet due. `P` is neither paid nor overdue (251 of 252 land in "pending").

**Recount agreement with `dcore_feat_*` (agreements with equal counts).**

| model | pooled concluded | pooled kept | no-anchor concluded | no-anchor kept | mean concluded old -> new |
|---|---|---|---|---|---|
| cc_60_180 | 83.0% | 90.8% | 99.1% | 100.0% | 1.239 -> 0.874 |
| rl_60_180 | 92.4% | 97.5% | 99.8% | 100.0% | 0.423 -> 0.304 |

- The anchor, not the paid / overdue definition, explains the differences: 16% (CC) / 7.5% (RL) of agreements had
 instalments from before the current delinquency.
- Dimension A level old -> new, CC: `partly_kept` -> `thin` 55.3%, `kept` -> `thin` 13.7%, `broken` -> `thin` 27.2%
 (71.2% stay `broken`). RL: 33.3%, <10, 32.4%. `thin` never gains rows from other levels; CC `thin` grows
 14,648 -> 16,300.

**DCORE vs ledger agreement (concluded instalments).**

| ledger | PTP all | PTP last 3m | settlement all | settlement last 3m |
|---|---|---|---|---|
| cc, to due date | 93.2% | 92.0% | 52.0% | 48.7% |
| cc, to due date + 5 days | 88.8% | 91.6% | 55.0% | 51.0% |
| rl, total_paid of due month | 78.4% | 86.5% | 80.5% | 87.7% |

- CC PTP: DCORE `paid` is ledger-kept 52% (to due date) / 69% (+5d); DCORE `overdue` is ledger-kept 0% / 7.9%.
- CC settlement: no relation (Cramer's V 0.06); 68.6% of DCORE-`overdue` are "kept" by the ledger.
- RL: DCORE `paid` is ledger-kept 94% (PTP) / 67% (settlement); DCORE `overdue` is ledger-kept 25% / 8%.

## V2 - strong-negative candidates

| candidate | CC fires | CC % A2 non_reach. | CC moved | RL fires | RL % A2 non_reach. | RL moved |
|---|---|---|---|---|---|---|
| Explicit refusal | 4.4% (841) | 56.7% | 623 | 4.4% (177) | 33.9% | 123 |
| Dispute | 0.3% (62) | 45.2% | 47 | 0 | - | 0 |
| N0 no-response (today) | 36.0% (6,937) | 84.2% | 6,247 | 26.4% (1,051) | 77.8% | 715 |
| N1 live-line no-pickup | 7.6% (1,464) | 70.3% | 1,187 | failed | - | - |
| N2 no-pickup after a contact | 4.3% (835) | 66.3% | 675 | failed | - | - |
| N4 customer hung up | 2.0% (395) | 75.7% | 303 | failed | - | - |

Top result names (CC unless stated):
- Refusal: REFUSED TO PAY 561, REFUSE TO PAY 280 (RL: 144, 33). Dispute: DISPUTE 62 (RL: no rows).
- N0: MOBILE SWICTHED OFF 6,053 rows, UNCONTACTABLE 4,288, RINGING NO REPLY 3,155.
- N1 and N2: RINGING NO REPLY (1,135 / 703), RINGING NO RESPONSE (1,074 / 669), LEFT_MSG (599 / 474).
- N4: CUSTOMER_HUNG_UP 366, CUSTOMER HUNG UP 29.

Other V2 results:
- Every candidate only moves rows down to `low` (moderate or unknown -> low); fewer than 10 refusals leave `high`.
- Overlap (CC): refusal and N1 143, refusal and N2 155, N1 and N2 641 (77% of N2), N0 and N1 582; hang-up and
 refusal / dispute 0 by construction.
- Latest right-party contact (CC, 10,091 rows with one): REFUSED TO PAY 597, CUSTOMER_HUNG_UP 431, REFUSE TO PAY 297,
 DISPUTE 65, CUSTOMER HUNG UP 29, CUSTOMER MISBEHAVED <10.
- Baseline (broken only) differs from the shipped state on 7,195 rows (37%) CC, 808 (20%) RL: today's negatives.

## V3 - overlap with other axes

V = Cramer's V. Accuracy = guessing the row level from the column vs always guessing the modal row level.

| crosstab | CC V | CC accuracy | RL V | RL accuracy |
|---|---|---|---|---|
| Dimension C x A4 state | 0.58 | 77.2% vs 64.4% | 0.53 | 58.9% vs 44.6% |
| Dimension C x n_prior_episodes | 0.34 | 69.2% vs 64.4% | 0.30 | 58.8% vs 44.6% |
| Dimension B x A4 state | 0.62 | 78.9% vs 72.9% | 0.53 | 67.6% vs 53.1% |
| A3 state x A1 state | 0.10 | 58.4% vs 58.4% | 0.12 | 59.0% vs 52.6% |
| A3 state x A2 reachability | 0.22 | 58.4% vs 58.4% | 0.16 | 55.8% vs 52.6% |

- Dimension C x A4 state: `no_record` duplicates A4 `early_payment_default` (CC 1,439 of 1,440; RL 223 of 229).
 Clean / not_clean still adds inside the big states (CC seasoned straight roller 7,199 vs 862, slow roller
 2,195 vs 699).
- Dimension C x n_prior_episodes: partly duplicates. Clean has no prior episode in 93.9% (CC) / 94.2% (RL), not_clean
 in 55.9% / 61.7%. `clean_gap_before_current` is not persisted in the A4 output, so it cannot be checked.
- Dimension B x A4 state: `regular` mostly duplicates `stabilized` (CC 1,100 of 1,273; RL 282 of 411); some / none
 still adds inside slow_roller and seasoned.
- A3 x A1 adds (nearly independent). A3 x A2 partly overlaps: CC high is 77% reachable, low 75% non_reachable.

## V4 - rows changing state vs today (% of population; recomputed state = shipped state on 100.0% of rows)

| variant | CC | RL |
|---|---|---|
| High from 3 points | 4.7% | 5.6% |
| High from 5 points | 1.9% | 0.6% |
| Moderate from 2 points | 19.4% | 28.9% |
| kept rate 70% / 90% | 0.1% / 0.1% | <10 / <10 |
| broken rate 30% / 50% | 1.3% / 0.4% | 0.7% / <10 |
| broken streak 2 / 4 | 0.5% / 1.5% | <10 / <10 |
| concluded needed 1 / 3 | 1.0% / 0.2% | 1.1% / <10 |
| Regular 1 of 3 / 3 of 3 | 1.4% / 0.8% | 0.7% / 0.3% |
| record clean share 70% / 90% | 2.1% / 3.8% | 2.7% / 2.9% |
| record months due 2 / 4 | 1.0% / 0.8% | 0.7% / 0.5% |

Only "Moderate from 2" and the High / clean-share cut-offs move over ~5%; commitment thresholds barely matter.

## Looked wrong in the data
- **N0 is mostly A2**: 84% / 78% non_reachable, and its top names are dead-line outcomes (switched off,
uncontactable, disconnected, wrong number).
- CC PTP: DCORE-`overdue` with a kept ledger is exactly 0 to the due date; CC settlement shows no link to the
ledger. The ledger sum is cumulative from the plan start and card-only, so non-card payments and later
instalments distort it.
- `P`-status PTP instalments (252) are neither paid nor overdue; `B` / `F` rows have due dates after the observation
date (snapshot statuses, not point-in-time).
- Counting HISTORICAL PROMISE TO PAY / RETAIN PTP as right-party changes `rpc_confirmed` on 0 rows (CC): check that
those names occur in `dcore_prm_followup_outcomes` at all.
- The Broken rate test hard-codes `>= 2` concluded in `derive_commitments_level`, so the "concluded needed"
variants do not move it.

## Transcription notes (handoff 33)
- Sum and ratio checks that pass: 841 / 19,292 = 4.4%; 62 = 0.3%; 6,937 = 36.0%; 1,464 = 7.6%; 835 = 4.3%; 395 = 2.0%; RL 177 / 3,985 = 4.4%; 1,051 = 26.4%. Refusal names 561 + 280 = 841 (CC) and 144 + 33 = 177 (RL) match the table. N4 names 366 + 29 = 395. 641 / 835 = 77% (line 63). 7,195 / 19,292 = 37%; 808 / 3,985 = 20%.
- Line 57: "SWICTHED" is spelled that way in the photo (a data-value typo, not mine). The N0 name counts (6,053 + 4,288 + 3,155 = 13,496) are larger than the 6,937 N0 fires; they are "rows", so a different unit from the account count (copied as shown).
- Line 4: A3 `t0` match is 19,290 / 19,292 CC and 3,964 / 3,985 RL.
- Line 29: `thin` grows 14,648 -> 16,300 (CC).
- Lines 48-53 and 97-103: `<10` is a masked small count. In the V2 table the RL columns for N1, N2, N4 read "failed" with dashes, consistent with the Java heap gap in line 5.
- Lines 78-79: the CC accuracy is "58.4% vs 58.4%" on both rows, as printed.
- Line 116: the second line of this bullet is partly cut in photo 4 and complete in photo 5.
- OCR-risk digits: lines 23-24 (means 1.239 / 0.874 / 0.423 / 0.304), 36-38, 75-79 (V and accuracy values), 94-103.
