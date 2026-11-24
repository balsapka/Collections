# UC1 bundle 31 follow-up: workshop numbers (month end 2026-07-31)

Source: `results_cc_60_180.md`, `results_rl_60_180.md` (PROD, snippet `2026-11-24a`). Control matches the B31
PAID block (cc `891 16.3/18.3`, rl `334 31.4/40.7`). Outcome `paid_due` = August payments reaching max(due,
100 AED). Intervals: 200 account resamples, 95%. 180+ not run. AED in thousands (k) or millions (M).

## Read first (limits of this run)

- **CC DPD band is `unknown` for most UC1 rows** (A4 `current_bucket` did not map to 4-7 for them), so cc T3
  has one band only. RL's band worked. Defect in this snippet's band step, not fixed; a rerun needs the cc
  `current_bucket` values checked first.
- **CC outstanding is not a month-end figure:** only 71 of 18,397 `prm_balance` snapshots are dated on
  2026-07-31; the rest are the latest snapshot of July. RL is exact (3,728 of 3,728 on the month end). Compare
  CC outstanding as an order of magnitude only.
- **The remark reading is almost empty:** `not-detected` in 826 of 891 cc and 319 of 334 rl UC1 rows (A5); 609
  / 260 for A6. "Transcript vs remark" is therefore mostly "transcript vs nothing".

## 1. Transcript reading vs remark reading (rows with both readings = all rows in scope)

AUC on `paid_due` (able > partly > not stated > unable; pays in full > partly or later > not stated >
refuses). Agreement = share of rows where the transcript and remark states are equal; agree - differ =
`paid_due` pp.

| model_id | scope | n | AUC transcript | AUC remark | transcript - remark [95% CI] |
|---|---|---|---|---|---|
| cc_60_180 | A5 in A1 unknown | 314 | 0.578 | 0.521 | +0.057 [-0.031, 0.139] |
| cc_60_180 | A6 in A3 no_promise | 122 | 0.608 | 0.456 | +0.152 [-0.079, 0.400] |
| cc_60_180 | A6 in A3 promised | 245 | 0.529 | 0.550 | -0.020 [-0.140, 0.111] |
| rl_60_180 | A5 in A1 unknown | 98 | 0.563 | 0.479 | +0.085 [-0.046, 0.222] |
| rl_60_180 | A6 in A3 no_promise | 126 | 0.543 | 0.475 | +0.069 [-0.051, 0.197] |
| rl_60_180 | A6 in A3 promised | 82 | 0.510 | 0.443 | +0.068 [-0.038, 0.183] |

| model_id | scope | n | equal % | paid_due agree - differ, pp [95% CI] |
|---|---|---|---|---|
| cc_60_180 | A5 in A1 unknown | 314 | 34.4 | -0.7 [-6.8, 7.3] |
| cc_60_180 | A6 in A3 no_promise | 122 | 32.8 | -3.5 [-12.5, 5.0] |
| cc_60_180 | A6 in A3 promised | 245 | 26.5 | 1.1 [-7.0, 10.6] |
| rl_60_180 | A5 in A1 unknown | 98 | 32.7 | -17.8 [-31.2, -1.1] |
| rl_60_180 | A6 in A3 no_promise | 126 | 18.3 | -11.2 [-25.2, 7.2] |
| rl_60_180 | A6 in A3 promised | 82 | 12.2 | -15.8 [-45.9, 13.9] |

- Where both sources state a level (neither not stated), A6 agreement is 62% (cc, n 155) and 59% (rl, n 54);
  A5 agreement is 45% (cc, n 40).
- RL agree vs differ is negative (differ pays more): not read further, since most "differ" rows are
  "transcript stated, remark not detected", so the split follows who has a transcript reading, not a conflict
  (my reading of the encoding; not tested).

## 2. Money at stake (AED; due at the month end, August payments in the window)

| model_id | group | accounts | sum due | sum outstanding | August payments | paid / due % |
|---|---|---|---|---|---|---|
| cc_60_180 | whole book | 18,397 | 21.9M | 519.4M | 4.18M | 19.1 |
| cc_60_180 | all UC1 rows | 891 | 1.28M | 29.8M | 396k | 30.9 |
| cc_60_180 | unlogged flag = 1, all | 239 | 349k | 8.1M | 99k | 28.4 |
| cc_60_180 | unlogged, A3 kept | 11 | 14k | 311k | 0 | 0.0 |
| cc_60_180 | unlogged, A3 partly_kept | 133 | 197k | 4.9M | 64k | 32.4 |
| cc_60_180 | unlogged, A3 promised | 49 | 63k | 1.4M | 31k | 49.6 |
| cc_60_180 | unlogged, A3 no_promise | 46 | 76k | 1.5M | 4k | 5.5 |
| cc_60_180 | A1 unknown, all | 10,001 | 11.8M | 282.8M | 1.59M | 13.4 |
| cc_60_180 | A1 unknown, a5 no_evidence | 9,687 | 11.3M | 271.6M | 1.48M | 13.0 |
| cc_60_180 | A1 unknown, a5 partly_able | 108 | 173k | 4.0M | 42k | 24.2 |
| cc_60_180 | A1 unknown, a5 not_stated | 101 | 161k | 3.9M | 35k | 21.9 |
| cc_60_180 | A1 unknown, a5 unable | 72 | 116k | 2.2M | 6k | 5.1 |
| cc_60_180 | A1 unknown, a5 able | 33 | 42k | 1.1M | 28k | 65.8 |
| cc_60_180 | a5_reason = lost_employment | 249 | 390k | 8.5M | 88k | 22.6 |
| cc_60_180 | a5_reason = reduced_employment | 96 | 131k | 3.0M | 17k | 13.0 |
| rl_60_180 | whole book | 3,728 | 14.5M | 418.1M | 5.02M | 34.5 |
| rl_60_180 | all UC1 rows | 334 | 1.31M | 36.8M | 578k | 44.0 |
| rl_60_180 | unlogged flag = 1, all | 137 | 531k | 14.4M | 303k | 57.2 |
| rl_60_180 | unlogged, A3 kept | 11 | 52k | 1.4M | 16k | 31.0 |
| rl_60_180 | unlogged, A3 partly_kept | 33 | 165k | 4.8M | 68k | 41.4 |
| rl_60_180 | unlogged, A3 promised | 33 | 135k | 3.5M | 125k | 92.9 |
| rl_60_180 | unlogged, A3 no_promise | 60 | 179k | 4.8M | 94k | 52.4 |
| rl_60_180 | A1 unknown, all | 1,493 | 5.58M | 148.3M | 1.65M | 29.6 |
| rl_60_180 | A1 unknown, a5 no_evidence | 1,395 | 5.19M | 137.7M | 1.49M | 28.8 |
| rl_60_180 | A1 unknown, a5 partly_able | 33 | 167k | 5.1M | 57k | 33.8 |
| rl_60_180 | A1 unknown, a5 not_stated | 30 | 72k | 2.1M | 13k | 17.4 |
| rl_60_180 | A1 unknown, a5 unable | 22 | 102k | 2.2M | 81k | 78.7 |
| rl_60_180 | A1 unknown, a5 able | 13 | 45k | 1.2M | 6k | 14.0 |
| rl_60_180 | a5_reason = lost_employment | 103 | 480k | 13.6M | 170k | 35.3 |
| rl_60_180 | a5_reason = reduced_employment | 36 | 152k | 4.9M | 57k | 37.5 |

(paid / due % is computed here from the two sums; it is not the account-level `paid_due`.)

## 3. Reasons inside A1 Unknown (UC1 rows; cell = share % (`paid_due` %); `<10` suppressed)

| model_id | A1 state, band | n | lost | reduced | incr_oblig | has_empl | none |
|---|---|---|---|---|---|---|---|
| cc_60_180 | unknown, unk | 310 | 38.4 (10.9) | 7.4 (4.3) | 7.4 (30.4) | 20.6 (14.1) | 26.1 (17.3) |
| cc_60_180 | low, unk | 333 | 27.0 (17.8) | 14.4 (10.4) | 8.7 (20.7) | 24.6 (19.5) | 25.2 (25.0) |
| cc_60_180 | moderate, unk | 204 | 16.2 (15.2) | 10.8 (18.2) | 10.3 (14.3) | 29.9 (16.4) | 32.8 (13.4) |
| cc_60_180 | high, unk | <10 | - | - | - | - | n 12 |
| rl_60_180 | unknown, 91-120 | 35 | 31.4 (9.1) | <10 | <10 | <10 | 31.4 (9.1) |
| rl_60_180 | unknown, 121-150 | 35 | 34.3 (0.0) | <10 | <10 | <10 | 37.1 (7.7) |
| rl_60_180 | low, 61-90 | 68 | 26.5 (38.9) | 20.6 (42.9) | <10 | 22.1 (33.3) | 23.5 (37.5) |
| rl_60_180 | low, 121-150 | 45 | 42.2 (15.8) | <10 | <10 | <10 | 35.6 (12.5) |

Columns: reason; lost = lost_employment, reduced = reduced_employment, incr_oblig = increased_obligations,
has_empl = has_employment. unk = DPD band unknown (cc).

- cc A1 unknown: reduced_employment is -10.6 pp [-18.0, -0.9] vs the rest of the cell; increased_obligations
  +17.5 pp [-0.4, 38.5] (n 23).
- rl A1 unknown 121-150: lost_employment 0.0% paid (n 12), -21.7 pp [-40.9, -8.0] vs the rest. RL unknown
  61-90 and 151-180, and all RL moderate / high cells, are under 10.

## Answers

1. **Transcript vs remark:** the transcript AUC is higher in 5 of 6 comparisons (+0.06 to +0.15), but every
   interval includes 0, so "better" is not shown; the remark is near chance (0.44-0.55) because it is almost
   always not detected.
2. **AED:** the unlogged promise is cc 239 accounts (349k due, 8.1M outstanding) and rl 137 (531k due, 14.4M),
   with the no_promise slice cc 46 (76k, 5.5% paid) and rl 60 (179k, 52% paid); A1 Unknown holds cc 11.8M due
   / 282.8M outstanding (54% of the book's outstanding, 13% paid) and rl 5.6M / 148.3M (36%, 30% paid), and
   UC1 reaches only 314 cc (4% of due) and 98 rl (6%) of those accounts; within UC1 the order by due is
   partly_able > not_stated > unable > able (cc) and partly_able > unable > not_stated > able (rl).
3. **Reasons in A1 Unknown:** lost_employment is the largest reason (cc 38% vs 27% in low and 16% in moderate;
   rl 31-34%), lost plus reduced employment is 46% of cc A1 unknown, and the weakest payers are the reduced /
   lost employment groups (cc 4.3% / 10.9% vs 17.3% for none); cc band and all small rl cells are the limit.
