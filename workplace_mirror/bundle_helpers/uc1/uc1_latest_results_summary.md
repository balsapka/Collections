# UC1 latest results: August refresh (export snapshot 2026-08-31) against the workshop findings

Source: `results_{cc,rl}_{60_180,180_plus}_2026-08-31.md` (PROD, snippet 2026-11-27a plus the `NA` fix; no failed
section). Axes:
A1 deterioration, A2 locatability, A3 credibility, A4 ability. Counts under 10 are `<10`. n in brackets.
**R1** = export `estimated_value` at 2026-07-31, outcome = August payments (the export holds evidence to 08-31:
look-ahead).
**R2** = posteriors on the month end, 04-30 .. 07-31, next month's payments, pooled (an assessment, not an agreed
input).
`paid_due` = next-month payments >= max(due, 100 AED). 95% intervals from 200 account resamples. Bar for a later
decision: >= 5 pp or >= 0.02 AUC.

**Headline.** Coverage is much higher, but the stated-ability fill (F) did not hold up: inside A4 Unknown the stated
level no longer orders
payers (cards AUC 0.51-0.53 vs 0.613 earlier). What got stronger is the delinquency reason on cards, the "a call was
recorded" signal at 180+,
and the selection effect on cards. The verdict column of the generated table says "stronger (interval includes null)"
for some loan rows; read
those as "no signal" (see section 5).

## 1. Coverage (accounts with a UC1 reading; % of accounts, n)

| month end | cards R1 | cards R2 any age | cards R2 <= 90 d | loans R1 | loans R2 any age | loans R2 <= 90 d |
|---|---|---|---|---|---|---|
| 04-30 | - | 3.0% (435) | 3.0% (435) | - | 8.6% (228) | 8.6% (228) |
| 05-31 | - | 10.2% (1,627) | 10.2% (1,627) | - | 13.5% (419) | 13.5% (419) |
| 06-30 | - | 15.4% (2,615) | 9.4% (1,594) | - | 17.1% (602) | 12.3% (432) |
| 07-31 | 19.2% (3,528) | 19.2% (3,525) | 7.1% (1,299) | 18.2% (680) | 18.2% (679) | 8.2% (307) |

Accounts at 07-31: cards 18,397 (A2 reachable 22.0%, 4,046), loans 3,728 (28.5%, 1,064). Reachable with a reading at
07-31: cards 31.5% (1,275)
R1, 14.8% (600) at <= 90 d; loans 24.9% (265), 12.2% (130). Earlier export at 07-31: 891 cards, 334 loans. Source split
(R2, 07-31, any age):
cards transcript only 4.2% (769), remark only 6.8% (1,246), both 8.2% (1,510); loans 4.1% (154) / 5.7% (211) / 8.4%
(314). At <= 90 d the
mix is mostly remarks (cards remark only 4.8%, transcript only 0.5%). R1 source split is not usable (every export CIF
shows both sources).
180+ at 07-31: cards 3.8% (12,062) of 316,738 accounts (of reachable 1.0%), loans 4.9% (2,701) of 54,819 (of reachable
2.8%).
Evidence age: coverage at <= 90 d falls from 19.2% to 7.1% (cards) because UC1's calls stop at 2026-07-16.

## 2. Findings (paid_due %, n; R1 | R2 pooled | R2 <= 90 d)

**Stated ability inside A4 Unknown (F), cards.**

| state | R1 | R2 | R2 <= 90 d |
|---|---|---|---|
| able | 13.5% (141) | 15.0% (301) | 20.6% (102) |
| partly able | 9.6% (343) | 13.5% (807) | 19.4% (330) |
| not stated | 10.6% (733) | 12.1% (1,453) | 14.2% (976) |
| unable | 10.0% (209) | 11.3% (453) | 11.1% (244) |
| no reading | 6.1% (8,575) | 7.8% (31,992) | 7.8% (33,354) |
| AUC (readers) | 0.510 [0.467, 0.551] (1,426) | 0.525 [0.496, 0.560] (3,014) | 0.557 [0.522, 0.593] (1,652) |

Loans: AUC 0.521 [0.450, 0.601] (221) R1, 0.535 [0.474, 0.589] (541) R2; able 29.2% (24) / partly 22.4% (49) / not
stated 21.4% (103) / unable
22.2% (45) / no reading 15.3% (1,272) at R1. Readers pay more than non-readers in the tier, but the level does not order
them,
Transcript vs remark-only (cards, stated levels, A4 Unknown): AUC 0.531 (1,471) vs 0.389 (90), difference +0.142 [0.063,
0.235] R2; R1 +0.108
[0.013, 0.202]. Remark-only is below 0.5 on 47-90 accounts; loans remark-only n <10 (R1), 14 (R2).

**Delinquency reason (has employment - lost employment, pp).**

| scope | cards R1 | cards R2 | loans R1 | loans R2 |
|---|---|---|---|---|
| all readers | +3.3 [0.7, 6.1] (1,041 / 951) | +6.2 [3.9, 8.3] (2,353 / 2,151) | +9.5 [2.0, 17.6] (173 / 217) | +7.6
[0.9, 14.6] (449 / 627) |
| inside A4 Unknown | +2.2 [-0.9, 6.2] (383 / 442) | +4.6 [1.5, 8.4] (797 / 915) | +8.9 [-3.2, 21.2] (53 / 80) | +5.8
[-2.6, 16.4] (108 / 201) |

Cards R2 per month end +6.4 / +9.2 / +8.5 / +3.3; three-month outcome (04-30, 05-31) +11.0 [5.4, 16.5] (547 / 501).
Cards R1 paid_due: has
employment 14.3% (1,041), increased obligations 16.5% (261), reduced 13.5% (251), lost 11.0% (951).

**Stated intent inside A3 levels (AUC readers; pays in full - partly or later, pp).**

| scope | cards R1 | cards R2 | loans R1 | loans R2 |
|---|---|---|---|---|
| no_promise AUC | 0.599 [0.534, 0.655] (706) | 0.531 [0.484, 0.575] (1,637) | 0.507 [0.428, 0.594] (277) | 0.542
[0.488, 0.585] (784) |
| promised AUC | 0.511 [0.462, 0.553] (1,034) | 0.501 [0.468, 0.528] (2,492) | 0.546 [0.485, 0.624] (155) | 0.527
[0.473, 0.588] (478) |
| partly_kept AUC | 0.482 [0.451, 0.507] (1,654) | 0.498 [0.476, 0.520] (3,771) | 0.542 [0.469, 0.607] (209) | 0.526
[0.484, 0.566] (577) |
| partly_kept, full - partly, pp | -5.2 [-10.0, -0.8] | -3.1 [-6.9, 1.3] | +25.4 [1.5, 47.9] (17 / 149) | +14.4 [3.2,
25.9] (63 / 420) |

Cards no_promise: only July is above 0.5 (0.469 / 0.499 / 0.479 / 0.599 by month end). Loans three-month outcome,
no_promise: AUC 0.661 [0.587, 0.753] (258).

**Having a reading inside A2 reachable (readers - non-readers, pp).** Cards: R1 -7.2 [-10.1, -5.1] (1,275 / 2,771), R2
-9.0 [-10.9, -7.3]
(3,426 / 12,960), <= 90 d -8.8; every month end -7 to -9; three-month -6.0 [-9.0, -2.9]. Loans: R1 -0.8 [-7.6, 5.8], R2
+0.2 [-3.5, 4.5]. Over all
accounts readers pay more (cards +3.6 [2.6, 4.4] R2; loans +7.0 [4.7, 9.4]): readers are a different mix, not better
payers once reachable.

## 3. Money (AED m; whole book, R1 at 07-31)

| group | cards accts | cards outstanding | cards due | cards paid of due | loans accts | loans outstanding | loans due
| loans paid of due |
|---|---|---|---|---|---|---|---|---|
| whole book | 18,397 | 519.39 | 21.92 | 19.1% | 3,728 | 418.14 | 14.68 | 34.2% |
| with a reading | 3,528 | 109.63 | 4.95 | 21.9% | 680 | 78.88 | 2.96 | 34.5% |
| A4 Unknown | 10,001 | 282.83 | 11.84 | 13.4% | 1,493 | 148.30 | 5.62 | 29.4% |
| A4 Unknown, able | 141 | 4.21 | 0.17 | 33.5% | 24 | 2.22 | 0.09 | 26.4% |
| A4 Unknown, partly able | 343 | 10.91 | 0.50 | 15.6% | 49 | 6.91 | 0.23 | 30.4% |
| A4 Unknown, not stated | 733 | 23.76 | 1.04 | 14.6% | 103 | 8.55 | 0.49 | 25.4% |
| A4 Unknown, unable | 209 | 6.03 | 0.31 | 12.2% | 45 | 3.97 | 0.16 | 52.8% |
| A4 Unknown, no reading | 8,575 | 237.92 | 9.81 | 12.9% | 1,272 | 126.65 | 4.65 | 29.0% |

R2 pooled (account-months): cards whole book 65,940, 1,867.33 outstanding, 78.52 due, 21.5% paid of due; readers 8,202,
252.60, 11.66, 26.6%;
A4 Unknown 35,006, 993.50, 41.39, 15.0%. Loans whole book 12,999, 1,446.29, 51.50, 31.5%; readers 1,928, 223.43, 9.03,
35.9%.
**Cards outstanding is not a month-end value**: exact snapshot for 1.1% / 0.4% / 0.9% / 0.4% of accounts at 04-30 ..
07-31 (0.5-1.3% of AED); the
rest is the latest snapshot of the same month. Loans outstanding is exact (100%).

## 4. Impact sizing

**F fill (A4 Unknown, 07-31).** Cards: 10,001 accounts, 6.9% (693) with a stated ability, AED 0.98m of the 11.84m tier
due; able / partly able 4.8%
(484) hold 7.7% (52) of the tier's 675 payers (lift 1.59). Loans: 1,493, 7.9% (118), AED 0.48m of 5.62m; able / partly
4.9% (73) hold 7.3% (18) of 245
payers (lift 1.50). The lift comes from being a reader (readers 10-13% vs 6.1% non-readers), not from the stated level
(section 2). Per month end: A9.

**T treat (lost or reduced employment, 07-31).** Cards: 1,202 accounts, AED 1.76m due, paid_due 11.6% vs 14.3% has
employment. Loans: 273, AED 1.17m,
22.0% vs 28.9%. The gap is larger where the customer is not reachable (cards R1, lost or reduced vs has employment:
Moderate 4.6% vs 10.6%, Low 9.2% vs
12.8%). By A2 x A4 and per month end: A9.

**C context (share with a record, 07-31 R1).** Cards reachable: kept 23.6% (57), partly_kept 39.0% (671), promised 38.5%
(352), no_promise 16.7% (195);
not reachable 19.4% / 33.6% / 34.3% / 5.7% (511). Loans reachable: 35.2% (19) / 34.3% (96) / 26.6% (66) / 17.4% (84). At
<= 90 d (07-31) cards reachable
no_promise 7.5% (88), partly_kept 17.7% (304). All months: A9.

**R recheck (loans, A3 no_promise, 07-31).** 2,412 accounts, 9.3% (224) with a stated intent, AED 0.86m due; paid_due
pays in full 10.8% (37), partly or
later 18.8% (160), not stated 15.1% (53), refuses 11.1% (27), no reading 13.5% (2,135). Earlier: pays in full 22.2% vs
partly 23.7%. Per month end: A9.

**P 180+ (recorded call in the 90 days before the month end, paid_due; n).**

| group | cards R1 07-31 | cards R2 pooled | loans R1 07-31 | loans R2 pooled |
|---|---|---|---|---|
| recorded call, read by UC1 | 4.7% (107), AED 0.18m due | 7.1% (565), 0.95m | 10.4% (67), 0.29m | 8.3% (204), 0.95m |
| recorded call, not read | 13.9% (36), 0.08m | 9.2% (326), 0.59m | 9.5% (21), 0.11m | 10.9% (110), 0.61m |
| no recorded call | 1.2% (316,595), 115.29m | 1.1% (1,254,009), 442.99m | 1.3% (54,731), 165.54m | 1.3% (216,509),
651.66m |

Mean due per account is 1.4-2.0x the no-call group's. The unread calls pay as much as the read ones. Per month end: A9.

## 5. Every idea, old vs new (cards | loans; R1 | R2 pooled [95% CI])

Verdicts are the snippet's; "(ci)" = interval includes the null. My reading in the last column.

| # | idea | earlier | R1 cards | R2 cards | R1 loans | R2 loans | my reading |
|---|---|---|---|---|---|---|---|
| 1 | ability in A4 Unknown, AUC | 0.613 / 0.47 | 0.510 | 0.525 [0.496, 0.560] | 0.521 | 0.535 [0.474, 0.589] | weaker;
no signal both |
| 2 | reason, has - lost, pp | +3.2 / +20.6 | +3.3 | +6.2 [3.9, 8.3] | +9.5 | +7.6 [0.9, 14.6] | cards stronger; loans
signal but smaller |
| 2b | reason in A4 Unknown, pp | +4.1 / - | +2.2 | +4.6 [1.5, 8.4] | +8.9 | +5.8 [-2.6, 16.4] | cards same; loans n
small |
| 3 | intent in no_promise, AUC | - / 0.52 | 0.599 | 0.531 [0.484, 0.575] | 0.507 | 0.542 [0.488, 0.585] | July only
(cards); no signal pooled |
| 4 | intent in promised / partly kept, AUC | - | 0.492 | 0.499 [0.478, 0.513] | 0.545 | 0.528 [0.496, 0.561] | no
signal |
| 5 | period weeks - months, pp | - | +1.4 | +3.4 [-1.1, 7.5] | +2.2 | +10.1 [1.4, 18.8] (547 / 117) | loans R2 only;
weak n |
| 6 | amount or date named, pp | - | +4.2 [1.6, 6.8] | not computed | +2.6 | not computed | cards R1 only; R2 has no
slots |
| 7 | says able / pays in full in A4 Low, pp | +0.6 / -0.5 | +3.5 | +3.0 [-0.6, 6.3] | +1.1 | +9.0 [2.0, 16.9] | loans
R2 now pays more; not a risk flag |
| 8 | says unable in A4 High / Moderate, pp | - | -1.1 | -2.7 [-7.9, 3.3] | -30.0 (14) | -3.6 [-17.2, 12.3] | no signal
|
| 9a | dispute stated, pp | none | +3.3 [0.8, 6.4] | +1.2 [-1.0, 3.6] | +6.2 | +5.0 [-1.4, 11.2] | no signal pooled |
| 9b | request stated, pp | none | -0.8 | -1.4 [-3.2, 0.4] | +2.2 | +0.2 | no signal |
| 10 | confidence HIGH vs LOW | almost all LOW | n <10 HIGH | not computed | n <10 HIGH | not computed | still almost
all LOW / MEDIUM |
| 11a | transcript - remark-only, ability in A4 Unknown, AUC | 0.51-0.61 vs 0.44-0.55 | +0.108 [0.013, 0.202] | +0.142
[0.063, 0.235] | n <10 | +0.104 [-0.010, 0.248] (300 / 14) | cards: transcript clearly ahead |
| 11b | transcript - remark-only, intent, AUC | same | -0.055 [-0.091, -0.006] | -0.041 [-0.070, -0.014] | +0.000 |
+0.011 [-0.044, 0.090] | cards: remark-only ahead (reversed) |
| 12 | reading in reachable, pp | -7 / - | -7.2 [-10.1, -5.1] | -9.0 [-10.9, -7.3] | -0.8 | +0.2 [-3.5, 4.5] | cards
same-to-stronger; loans none |
| 13 | 180+ recorded call, read, pp | +3.6 / +7.5 | +3.5 [-1.2, 7.2] | +5.9 [3.4, 8.6] | +9.2 [2.4, 16.8] | +7.1 [3.4,
12.3] | same; signal is the call |
| 13b | 180+ recorded call, not read, pp | +6.1 / +11.0 | +12.7 [3.4, 24.4] (36) | +8.1 [4.3, 11.5] | +8.3 [-1.3, 25.9]
(21) | +9.6 [3.4, 15.8] | same |

The snippet's "stronger (interval includes null)" for loan ideas 1 and 3 compare against an earlier figure at or below
0.5; they are no signal. Dropped
ideas that look revivable: 7 on loans R2 (+9.0 pp, n 165 flagged), 9a on cards at July only (+3.3), 6 on cards at July
only.

## What got stronger

- Cards delinquency reason: has employment pays 6.2 pp more than lost employment (R2), consistent at every month end and
at three months (+11.0 pp).
- Cards selection: readers in A2 reachable pay 7-9 pp less, at every month end.
- Cards transcript over remark-only for ability in A4 Unknown (+0.11 to +0.19 AUC), though remark-only is below chance
on under 100 accounts.
- 180+ recorded call: 3.5-12.7 pp more payers than no call, both products, both readings; unread calls pay as much (the
call, not the reading, carries it).
- Reach: 3,528 cards and 680 loans read at 07-31 against 891 and 334; the A4 Unknown stated-ability tier is 693 cards /
118 loans, still under 7% of the tier.

## What could not be computed, and why

- Idea 6 on R2 (both products): the posteriors and the evidence carry no repayment-slot rows (amount / date); R1 only.
- Idea 10: UC1 confidence HIGH has under 10 accounts at 07-31 (cards MEDIUM 1,328, LOW 439, other 1,760); the posteriors
carry none.
- R1 transcript / remark-only coverage split: the export shows both sources for every CIF; the split is from the
evidence (R2).
- Three-month outcome: only month ends 04-30 and 05-31 have a complete window (payments end 2026-08-31).
- Cards outstanding at the month end: the exact snapshot exists for about 1% of accounts; amounts are the latest of the
month.
- Export 08-31 writes `NA` for no value: read as `not-detected` / `N/A` in the snippet (to confirm with UC1).
- DPD splits not shown; the band check: unknown 0 at every month end for both 60-180 models (cards buckets 4-7 only),
mapping fixed.
# Appendix A1-A10: the tables the sections above only quote (copied from the results files by script; nothing
recomputed)
## A1. Coverage by month end, 60-180 (% of accounts, n; R2 <= 90 d equals any age at 04-30 and 05-31, rows omitted)
| product | reading, month end | accounts | A2 reachable (% of accounts) | with a reading | transcript only | remark
only | both | neither flag | reachable with a reading (% of reachable) |
|---|---|---|---|---|---|---|---|---|---|
| cards | R1 export, 2026-07-31 | 18,397 | 22.0% (4,046) | 19.2% (3,528) | 0 | 0 | 19.2% (3,528) | 0 | 31.5% (1,275) |
| cards | R2 any age, 2026-04-30 | 14,671 | 26.4% (3,873) | 3.0% (435) | 1.0% (144) | 0.7% (99) | 1.3% (192) | 0 | 6.9%
(267) |
| cards | R2 any age, 2026-05-31 | 15,890 | 26.5% (4,207) | 10.2% (1,627) | 3.1% (492) | 1.9% (300) | 5.3% (835) | 0 |
18.8% (791) |
| cards | R2 any age, 2026-06-30 | 16,982 | 25.1% (4,260) | 15.4% (2,615) | 3.8% (639) | 4.5% (759) | 7.2% (1,217) | 0 |
25.7% (1,094) |
| cards | R2 any age, 2026-07-31 | 18,397 | 22.0% (4,046) | 19.2% (3,525) | 4.2% (769) | 6.8% (1,246) | 8.2% (1,510) | 0
| 31.5% (1,274) |
| cards | R2 <= 90 d, 2026-06-30 | 16,982 | 25.1% (4,260) | 9.4% (1,594) | 0.7% (127) | 6.0% (1,014) | 2.7% (453) | 0 |
18.1% (769) |
| cards | R2 <= 90 d, 2026-07-31 | 18,397 | 22.0% (4,046) | 7.1% (1,299) | 0.5% (86) | 4.8% (879) | 1.8% (334) | 0 |
14.8% (600) |
| loans | R1 export, 2026-07-31 | 3,728 | 28.5% (1,064) | 18.2% (680) | 0 | 0 | 18.2% (680) | 0 | 24.9% (265) |
| loans | R2 any age, 2026-04-30 | 2,661 | 29.8% (793) | 8.6% (228) | 2.1% (56) | 1.8% (49) | 4.6% (123) | 0 | 15.9%
(126) |
| loans | R2 any age, 2026-05-31 | 3,096 | 30.5% (945) | 13.5% (419) | 3.3% (103) | 3.3% (102) | 6.9% (214) | 0 | 24.0%
(227) |
| loans | R2 any age, 2026-06-30 | 3,514 | 28.5% (1,000) | 17.1% (602) | 4.4% (154) | 4.7% (165) | 8.1% (283) | 0 |
26.5% (265) |
| loans | R2 any age, 2026-07-31 | 3,728 | 28.5% (1,064) | 18.2% (679) | 4.1% (154) | 5.7% (211) | 8.4% (314) | 0 |
24.9% (265) |
| loans | R2 <= 90 d, 2026-06-30 | 3,514 | 28.5% (1,000) | 12.3% (432) | 1.8% (63) | 5.2% (183) | 5.3% (186) | 0 | 21.8%
(218) |
| loans | R2 <= 90 d, 2026-07-31 | 3,728 | 28.5% (1,064) | 8.2% (307) | 1.2% (44) | 3.8% (143) | 3.2% (120) | 0 | 12.2%
(130) |
## A2. Coverage, 180+ (any-age rows and the 07-31 <= 90 d row; R1 equals R2 at 07-31)
| product | reading, month end | accounts | A2 reachable (% of accounts) | with a reading | transcript only | remark
only | both | neither flag | reachable with a reading (% of reachable) |
|---|---|---|---|---|---|---|---|---|---|
| cards 180+ | R2 any age, 2026-04-30 | 310,709 | 4.1% (12,685) | 0.0% (128) | 0.0% (33) | 0.0% (51) | 0.0% (44) | 0 |
0.6% (82) |
| cards 180+ | R2 any age, 2026-05-31 | 312,626 | 4.0% (12,503) | 0.1% (174) | 0.0% (34) | 0.0% (78) | 0.0% (62) | 0 |
0.9% (108) |
| cards 180+ | R2 any age, 2026-06-30 | 314,827 | 3.9% (12,151) | 0.1% (210) | 0.0% (30) | 0.0% (101) | 0.0% (79) | 0 |
1.0% (121) |
| cards 180+ | R2 any age, 2026-07-31 | 316,738 | 3.8% (12,062) | 0.1% (236) | 0.0% (31) | 0.0% (113) | 0.0% (92) | 0 |
1.0% (125) |
| cards 180+ | R2 <= 90 d, 2026-07-31 | 316,738 | 3.8% (12,062) | 0.0% (102) | <10 | 0.0% (73) | 0.0% (21) | 0 | 0.5%
(58) |
| loans 180+ | R2 any age, 2026-04-30 | 53,615 | 5.0% (2,665) | 0.1% (33) | <10 | <10 | 0.0% (21) | 0 | 0.9% (23) |
| loans 180+ | R2 any age, 2026-05-31 | 54,006 | 5.0% (2,685) | 0.1% (52) | <10 | 0.0% (13) | 0.1% (34) | 0 | 1.1% (29) |

| loans 180+ | R2 any age, 2026-06-30 | 54,383 | 4.8% (2,614) | 0.1% (80) | <10 | 0.0% (26) | 0.1% (46) | 0 | 1.7% (45) |

| loans 180+ | R2 any age, 2026-07-31 | 54,819 | 4.9% (2,701) | 0.3% (139) | 0.0% (27) | 0.1% (45) | 0.1% (67) | 0 |
2.8% (76) |
| loans 180+ | R2 <= 90 d, 2026-07-31 | 54,819 | 4.9% (2,701) | 0.1% (63) | <10 | 0.0% (22) | 0.1% (33) | 0 | 1.4% (37) |

## A3. Delinquency reason, all states (paid_due %, n; has employment, increased obligations, reduced, lost, none, no
reading)
#### Scope: all readers
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| has_employment | 14.3% (1,041) | 17.2% (2,353) | 19.1% (1,313) | 28.9% (173) | 27.4% (449) | 30.5% (298) |
| increased_obligations | 16.5% (261) | 17.2% (661) | 19.6% (347) | 38.6% (44) | 36.5% (137) | 38.2% (89) |
| reduced_employment | 13.5% (251) | 15.3% (581) | 15.3% (360) | 32.1% (56) | 33.7% (166) | 34.9% (129) |
| lost_employment | 11.0% (951) | 11.0% (2,151) | 10.3% (1,308) | 19.4% (217) | 19.8% (627) | 19.1% (465) |
| none | 11.0% (1,024) | 14.5% (2,456) | 18.4% (1,627) | 22.1% (190) | 25.7% (549) | 30.6% (405) |
| no_reading | 9.0% (14,869) | 11.0% (57,738) | 11.1% (60,985) | 19.8% (3,048) | 18.6% (11,071) | 18.7% (11,613) |
| has employment - lost employment, pp | +3.3 [0.7, 6.1] (n 1,041 / 951) | +6.2 [3.9, 8.3] (n 2,353 / 2,151) | +8.8
[6.0, 11.6] (n 1,313 / 1,308) | +9.5 [2.0, 17.6] (n 173 / 217) | +7.6 [0.9, 14.6] (n 449 / 627) | +11.4 [4.6, 18.7] (n
298 / 465) |
| has employment - (lost or reduced employment), pp | +2.7 [0.5, 5.4] (n 1,041 / 1,202) | +5.3 [3.1, 7.4] (n 2,353 /
2,732) | +7.7 [5.1, 10.4] (n 1,313 / 1,668) | +6.9 [0.3, 15.3] (n 173 / 273) | +4.7 [-1.7, 10.8] (n 449 / 793) | +8.0
[1.6, 14.6] (n 298 / 594) |
#### Scope: inside A4 Unknown
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| has_employment | 11.5% (383) | 14.4% (797) | 17.6% (409) | 26.4% (53) | 22.2% (108) | 24.2% (62) |
| increased_obligations | 18.9% (95) | 20.0% (210) | 30.0% (90) | 35.7% (14) | 41.0% (39) | 45.0% (20) |
| reduced_employment | 10.8% (74) | 13.0% (161) | 14.1% (92) | 30.8% (13) | 32.7% (49) | 35.9% (39) |
| lost_employment | 9.3% (442) | 9.8% (915) | 10.2% (509) | 17.5% (80) | 16.4% (201) | 17.7% (130) |
| none | 9.3% (432) | 12.1% (931) | 15.8% (552) | 21.3% (61) | 27.8% (144) | 35.8% (95) |
| no_reading | 6.1% (8,575) | 7.8% (31,992) | 7.8% (33,354) | 15.3% (1,272) | 15.2% (4,363) | 15.3% (4,558) |
| has employment - lost employment, pp | +2.2 [-0.9, 6.2] (n 383 / 442) | +4.6 [1.5, 8.4] (n 797 / 915) | +7.4 [2.8,
12.1] (n 409 / 509) | +8.9 [-3.2, 21.2] (n 53 / 80) | +5.8 [-2.6, 16.4] (n 108 / 201) | +6.5 [-4.8, 21.5] (n 62 / 130) |
| has employment - (lost or reduced employment), pp | +2.0 [-0.8, 6.1] (n 383 / 516) | +4.1 [0.3, 7.6] (n 797 / 1,076) |
+6.8 [2.5, 11.5] (n 409 / 601) | +7.1 [-5.8, 19.6] (n 53 / 93) | +2.6 [-6.5, 12.8] (n 108 / 250) | +2.3 [-8.5, 17.2] (n
62 / 169) |
## A4. Stated intent by A3 level, all rows (paid_due %, n; AUC rows with 95% interval)
#### Scope: A3 `no_promise`
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| pays_in_full | 10.4% (48) | 6.5% (107) | 7.0% (43) | 10.8% (37) | 20.0% (135) | 27.5% (80) |
| partly_or_later | 9.1% (372) | 8.8% (876) | 9.6% (478) | 18.8% (160) | 19.7% (422) | 22.3% (305) |
| not_stated | 6.0% (199) | 7.5% (453) | 9.8% (275) | 15.1% (53) | 13.0% (146) | 15.6% (109) |
| refuses | 1.1% (87) | 5.0% (201) | 6.6% (137) | 11.1% (27) | 14.8% (81) | 17.1% (70) |
| no_reading | 3.9% (9,501) | 4.7% (33,211) | 4.7% (33,915) | 13.5% (2,135) | 13.6% (7,259) | 13.5% (7,479) |
| AUC, readers (pays in full > partly > not stated > refuses) | 0.599 [0.534, 0.655] (n 706) | 0.531 [0.484, 0.575] (n
1,637) | 0.515 [0.465, 0.570] (n 933) | 0.507 [0.428, 0.594] (n 277) | 0.542 [0.488, 0.585] (n 784) | 0.558 [0.507,
0.608] (n 564) |
| pays in full - partly or later, pp | +1.3 [-7.1, 10.6] (n 48 / 372) | -2.2 [-7.2, 2.8] (n 107 / 876) | -2.6 [-9.6,
5.5] (n 43 / 478) | -7.9 [-19.2, 3.6] (n 37 / 160) | +0.3 [-8.0, 10.2] (n 135 / 422) | +5.2 [-4.7, 15.5] (n 80 / 305) |
| AUC stated levels, transcript-based | 0.493 [0.438, 0.560] (n 303) | 0.484 [0.431, 0.534] (n 817) | 0.480 [0.400,
0.558] (n 388) | 0.459 [0.367, 0.543] (n 162) | 0.509 [0.451, 0.565] (n 490) | 0.533 [0.471, 0.599] (n 321) |
| AUC stated levels, remark-only | 0.711 [0.630, 0.783] (n 204) | 0.607 [0.540, 0.680] (n 367) | 0.578 [0.490, 0.661] (n
270) | 0.529 [0.321, 0.638] (n 62) | 0.500 [0.381, 0.625] (n 148) | 0.503 [0.383, 0.625] (n 134) |
| AUC difference transcript - remark-only | -0.217 [-0.294, -0.118] (n 303 / 204) | -0.122 [-0.212, -0.036] (n 817 /
367) | -0.099 [-0.212, 0.005] (n 388 / 270) | -0.069 [-0.215, 0.151] (n 162 / 62) | +0.009 [-0.135, 0.152] (n 490 / 148)
| +0.030 [-0.112, 0.166] (n 321 / 134) |
#### Scope: A3 `promised`
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| pays_in_full | 8.0% (113) | 10.2% (313) | 13.1% (137) | 30.0% (10) | 22.0% (41) | 26.7% (30) |
| partly_or_later | 10.8% (734) | 13.4% (1,725) | 15.6% (1,075) | 32.2% (118) | 30.5% (338) | 30.2% (255) |
| not_stated | 6.5% (124) | 9.5% (306) | 11.8% (245) | 23.5% (17) | 15.0% (60) | 10.2% (49) |
| refuses | 9.5% (63) | 13.5% (148) | 12.2% (98) | 10.0% (10) | 25.6% (39) | 25.8% (31) |
| no_reading | 14.0% (1,869) | 14.8% (8,643) | 14.3% (9,580) | 30.8% (389) | 23.8% (1,546) | 24.2% (1,659) |
| AUC, readers (pays in full > partly > not stated > refuses) | 0.511 [0.462, 0.553] (n 1,034) | 0.501 [0.468, 0.528] (n
2,492) | 0.517 [0.486, 0.557] (n 1,555) | 0.546 [0.485, 0.624] (n 155) | 0.527 [0.473, 0.588] (n 478) | 0.549 [0.487,
0.606] (n 365) |
| pays in full - partly or later, pp | -2.8 [-7.9, 2.1] (n 113 / 734) | -3.2 [-7.3, 0.8] (n 313 / 1,725) | -2.5 [-9.3,
4.3] (n 137 / 1,075) | -2.2 [-30.7, 32.8] (n 10 / 118) | -8.5 [-22.2, 13.1] (n 41 / 338) | -3.5 [-20.4, 16.2] (n 30 /
255) |
| AUC stated levels, transcript-based | 0.496 [0.436, 0.546] (n 548) | 0.475 [0.438, 0.508] (n 1,509) | 0.496 [0.451,
0.536] (n 804) | 0.529 [0.469, 0.593] (n 99) | 0.471 [0.419, 0.523] (n 305) | 0.476 [0.420, 0.536] (n 227) |
| AUC stated levels, remark-only | 0.482 [0.436, 0.532] (n 362) | 0.505 [0.460, 0.539] (n 677) | 0.509 [0.480, 0.541] (n
506) | 0.425 [0.085, 0.603] (n 39) | 0.520 [0.369, 0.645] (n 113) | 0.548 [0.408, 0.649] (n 89) |
| AUC difference transcript - remark-only | +0.013 [-0.062, 0.079] (n 548 / 362) | -0.030 [-0.078, 0.024] (n 1,509 /
677) | -0.013 [-0.069, 0.027] (n 804 / 506) | +0.104 [-0.073, 0.418] (n 99 / 39) | -0.049 [-0.180, 0.097] (n 305 / 113)
| -0.072 [-0.194, 0.056] (n 227 / 89) |
#### Scope: A3 `partly_kept`
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| pays_in_full | 11.6% (198) | 16.2% (439) | 18.0% (194) | 52.9% (17) | 44.4% (63) | 45.0% (40) |
| partly_or_later | 16.8% (1,182) | 19.3% (2,687) | 21.0% (1,625) | 27.5% (149) | 30.0% (420) | 33.9% (283) |
| not_stated | 16.2% (198) | 18.0% (483) | 21.2% (387) | 25.7% (35) | 32.1% (78) | 35.9% (64) |
| refuses | 17.1% (76) | 16.0% (162) | 7.4% (95) | <10 | 31.2% (16) | 27.3% (11) |
| no_reading | 19.7% (2,995) | 21.4% (13,730) | 20.8% (15,200) | 36.1% (446) | 29.8% (1,890) | 29.3% (2,069) |
| AUC, readers (pays in full > partly > not stated > refuses) | 0.482 [0.451, 0.507] (n 1,654) | 0.498 [0.476, 0.520] (n
3,771) | 0.509 [0.486, 0.530] (n 2,301) | 0.542 [0.469, 0.607] (n 209) | 0.526 [0.484, 0.566] (n 577) | 0.520 [0.464,
0.568] (n 398) |
| pays in full - partly or later, pp | -5.2 [-10.0, -0.8] (n 198 / 1,182) | -3.1 [-6.9, 1.3] (n 439 / 2,687) | -2.9
[-9.3, 3.0] (n 194 / 1,625) | +25.4 [1.5, 47.9] (n 17 / 149) | +14.4 [3.2, 25.9] (n 63 / 420) | +11.1 [-1.0, 24.9] (n 40
/ 283) |
| AUC stated levels, transcript-based | 0.468 [0.435, 0.499] (n 1,038) | 0.485 [0.466, 0.505] (n 2,505) | 0.505 [0.483,
0.529] (n 1,369) | 0.558 [0.485, 0.648] (n 122) | 0.552 [0.505, 0.602] (n 366) | 0.550 [0.507, 0.600] (n 244) |
| AUC stated levels, remark-only | 0.493 [0.455, 0.528] (n 418) | 0.507 [0.478, 0.534] (n 783) | 0.517 [0.491, 0.559] (n
545) | 0.527 [0.432, 0.610] (n 52) | 0.506 [0.445, 0.559] (n 133) | 0.489 [0.426, 0.557] (n 90) |
| AUC difference transcript - remark-only | -0.025 [-0.075, 0.033] (n 1,038 / 418) | -0.022 [-0.057, 0.007] (n 2,505 /
783) | -0.013 [-0.056, 0.021] (n 1,369 / 545) | +0.031 [-0.099, 0.171] (n 122 / 52) | +0.046 [-0.025, 0.107] (n 366 /
133) | +0.061 [-0.014, 0.131] (n 244 / 90) |
#### Scope: all A3 levels
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| AUC stated levels, all A3 levels, transcript-based | 0.477 [0.452, 0.503] (n 1,980) | 0.488 [0.471, 0.503] (n 5,027) |
0.509 [0.489, 0.527] (n 2,652) | 0.511 [0.467, 0.556] (n 408) | 0.512 [0.480, 0.544] (n 1,221) | 0.526 [0.495, 0.558] (n
828) |
| AUC stated levels, all A3 levels, remark-only | 0.532 [0.503, 0.558] (n 1,005) | 0.529 [0.507, 0.551] (n 1,876) |
0.533 [0.509, 0.555] (n 1,356) | 0.511 [0.433, 0.592] (n 161) | 0.501 [0.434, 0.549] (n 410) | 0.502 [0.434, 0.551] (n
325) |
| AUC difference transcript - remark-only, all A3 levels | -0.055 [-0.091, -0.006] (n 1,980 / 1,005) | -0.041 [-0.070,
-0.014] (n 5,027 / 1,876) | -0.024 [-0.055, 0.007] (n 2,652 / 1,356) | +0.000 [-0.086, 0.084] (n 408 / 161) | +0.011
[-0.044, 0.090] (n 1,221 / 410) | +0.024 [-0.032, 0.107] (n 828 / 325) |
## A5. Having a reading or not, loans and cards, all rows
| group | cards R1 | cards R2 | cards R2<=90 | loans R1 | loans R2 | loans R2<=90 |
|---|---|---|---|---|---|---|
| inside A2 reachable: with a reading | 19.8% (1,275) | 20.7% (3,426) | 20.3% (2,427) | 33.2% (265) | 30.2% (883) |
30.1% (701) |
| inside A2 reachable: no reading | 27.0% (2,771) | 29.7% (12,960) | 29.1% (13,959) | 34.0% (799) | 30.0% (2,919) |
30.1% (3,101) |
| inside A2 reachable: readers - non-readers, pp | -7.2 [-10.1, -5.1] (n 1,275 / 2,771) | -9.0 [-10.9, -7.3] (n 3,426 /
12,960) | -8.8 [-10.7, -6.8] (n 2,427 / 13,959) | -0.8 [-7.6, 5.8] (n 265 / 799) | +0.2 [-3.5, 4.5] (n 883 / 2,919) |
+0.0 [-4.4, 3.8] (n 701 / 3,101) |
| all accounts: with a reading | 12.6% (3,528) | 14.7% (8,202) | 16.3% (4,955) | 24.9% (680) | 25.6% (1,928) | 27.6%
(1,386) |
| all accounts: no reading | 9.0% (14,869) | 11.0% (57,738) | 11.1% (60,985) | 19.8% (3,048) | 18.6% (11,071) | 18.7%
(11,613) |
| all accounts: readers - non-readers, pp | +3.6 [2.5, 4.7] (n 3,528 / 14,869) | +3.6 [2.6, 4.4] (n 8,202 / 57,738) |
+5.2 [4.0, 6.5] (n 4,955 / 60,985) | +5.1 [1.1, 8.9] (n 680 / 3,048) | +7.0 [4.7, 9.4] (n 1,928 / 11,071) | +9.0 [6.0,
11.8] (n 1,386 / 11,613) |
## A6. R2 per month end (point estimates, n beside)
| product | metric (R2, any age) | 2026-04-30 | 2026-05-31 | 2026-06-30 | 2026-07-31 | pooled [95% CI] |
|---|---|---|---|---|---|---|
| cards | F: AUC, stated ability in A4 Unknown | 0.508 (n 125) | 0.554 (n 518) | 0.520 (n 947) | 0.510 (n 1,424) | 0.525
[0.496, 0.560] (n 3,014) |
| cards | T: has employment - lost employment, pp | +6.4 (n 84 / 92) | +9.2 (n 463 / 409) | +8.5 (n 766 / 698) | +3.3 (n
1,040 / 952) | +6.2 [3.9, 8.3] (n 2,353 / 2,151) |
| cards | R: AUC, stated intent in A3 no_promise | 0.469 (n 74) | 0.499 (n 335) | 0.479 (n 523) | 0.599 (n 705) | 0.531
[0.484, 0.575] (n 1,637) |
| cards | R: AUC, stated intent in A3 promised | 0.552 (n 135) | 0.502 (n 527) | 0.473 (n 798) | 0.510 (n 1,032) | 0.501
[0.468, 0.528] (n 2,492) |
| cards | Selection: readers - non-readers in A2 reachable, pp | -7.9 (n 267 / 3,606) | -9.3 (n 791 / 3,416) | -8.4 (n
1,094 / 3,166) | -7.2 (n 1,274 / 2,772) | -9.0 [-10.9, -7.3] (n 3,426 / 12,960) |
| loans | F: AUC, stated ability in A4 Unknown | 0.652 (n 45) | 0.545 (n 100) | 0.510 (n 176) | 0.521 (n 220) | 0.535
[0.474, 0.589] (n 541) |
| loans | T: has employment - lost employment, pp | +14.2 (n 51 / 70) | +3.1 (n 90 / 138) | +5.9 (n 135 / 202) | +9.5 (n
173 / 217) | +7.6 [0.9, 14.6] (n 449 / 627) |
| loans | R: AUC, stated intent in A3 no_promise | 0.544 (n 86) | 0.578 (n 172) | 0.545 (n 249) | 0.507 (n 277) | 0.542
[0.488, 0.585] (n 784) |
| loans | R: AUC, stated intent in A3 promised | 0.433 (n 64) | 0.548 (n 112) | 0.523 (n 147) | 0.546 (n 155) | 0.527
[0.473, 0.588] (n 478) |
| loans | Selection: readers - non-readers in A2 reachable, pp | +0.4 (n 126 / 667) | +3.4 (n 227 / 718) | -2.4 (n 265 /
735) | -0.8 (n 265 / 799) | +0.2 [-3.5, 4.5] (n 883 / 2,919) |
## A7. Three-month outcome check (04-30 and 05-31 pooled)
| product | metric | 3-month outcome [95% CI] |
|---|---|---|
| cards | F: AUC, stated ability in A4 Unknown | 0.501 [0.442, 0.544] (n 643) |
| cards | T: has employment - lost employment, pp | +11.0 [5.4, 16.5] (n 547 / 501) |
| cards | R: AUC, stated intent in A3 no_promise | 0.492 [0.428, 0.546] (n 409) |
| cards | R: AUC, stated intent in A3 promised | 0.495 [0.450, 0.536] (n 662) |
| cards | Selection: readers - non-readers in A2 reachable, pp | -6.0 [-9.0, -2.9] (n 1,058 / 7,022) |
| loans | F: AUC, stated ability in A4 Unknown | 0.561 [0.447, 0.668] (n 145) |
| loans | T: has employment - lost employment, pp | +9.2 [-4.0, 20.4] (n 141 / 208) |
| loans | R: AUC, stated intent in A3 no_promise | 0.661 [0.587, 0.753] (n 258) |
| loans | R: AUC, stated intent in A3 promised | 0.510 [0.428, 0.601] (n 176) |
| loans | Selection: readers - non-readers in A2 reachable, pp | +3.0 [-5.6, 9.8] (n 353 / 1,385) |
## A8. Money, R2 pooled (account-months, AED m; the R2 <= 90 d version is in the results files)
#### R2 pooled
| product | group | accounts | with a balance | outstanding, AED m | amount due, AED m | paid next month, AED m | paid
of due (accounts with a due) |
|---|---|---|---|---|---|---|---|
| cards | whole book | 65,940 | 65,940 | 1,867.33 | 78.52 | 16.92 | 21.5% |
| cards | accounts with a reading | 8,202 | 8,202 | 252.60 | 11.66 | 3.10 | 26.6% |
| cards | A4 Unknown | 35,006 | 35,006 | 993.50 | 41.39 | 6.21 | 15.0% |
| cards | A4 Unknown, stated ability able | 301 | 301 | 9.37 | 0.40 | 0.15 | 38.0% |
| cards | A4 Unknown, stated ability partly_able | 807 | 807 | 23.70 | 1.13 | 0.24 | 21.2% |
| cards | A4 Unknown, stated ability not_stated | 1,453 | 1,453 | 46.66 | 2.07 | 0.38 | 18.6% |
| cards | A4 Unknown, stated ability unable | 453 | 453 | 12.41 | 0.67 | 0.14 | 20.8% |
| cards | A4 Unknown, stated ability no_reading | 31,992 | 31,992 | 901.36 | 37.13 | 5.30 | 14.3% |
| loans | whole book | 12,999 | 12,999 | 1,446.29 | 51.50 | 16.20 | 31.5% |
| loans | accounts with a reading | 1,928 | 1,928 | 223.43 | 9.03 | 3.24 | 35.9% |
| loans | A4 Unknown | 4,904 | 4,904 | 500.03 | 18.86 | 4.70 | 24.9% |
| loans | A4 Unknown, stated ability able | 77 | 77 | 5.95 | 0.24 | 0.14 | 58.3% |
| loans | A4 Unknown, stated ability partly_able | 121 | 121 | 16.20 | 0.58 | 0.16 | 27.4% |
| loans | A4 Unknown, stated ability not_stated | 227 | 227 | 22.54 | 1.54 | 0.32 | 20.7% |
| loans | A4 Unknown, stated ability unable | 116 | 116 | 8.85 | 0.37 | 0.16 | 43.6% |
| loans | A4 Unknown, stated ability no_reading | 4,363 | 4,363 | 446.48 | 16.13 | 3.92 | 24.3% |
## A9. Impact sizing per month end
#### F fill (A4 Unknown; the R2 07-31 row equals R1)
| product | slice | A4 Unknown accounts | with a stated ability | amount due of those, AED m | amount due of the tier,
AED m | able / partly able (% of tier accounts) | tier payers | payers in able / partly able (% of tier payers) | lift |
|---|---|---|---|---|---|---|---|---|---|
| cards | R1 2026-07-31 | 10,001 | 6.9% (693) | 0.98 | 11.84 | 4.8% (484) | 675 | 7.7% (52) | 1.59 |
| cards | R2 2026-04-30 | 7,826 | 0.8% (66) | 0.08 | 9.15 | 0.6% (49) | 713 | 1.5% (11) | 2.46 |
| cards | R2 2026-05-31 | 8,269 | 3.7% (302) | 0.43 | 9.80 | 2.8% (232) | 722 | 6.4% (46) | 2.27 |
| cards | R2 2026-06-30 | 8,910 | 5.6% (500) | 0.70 | 10.60 | 3.8% (343) | 753 | 6.0% (45) | 1.55 |
| loans | R1 2026-07-31 | 1,493 | 7.9% (118) | 0.48 | 5.62 | 4.9% (73) | 245 | 7.3% (18) | 1.50 |
| loans | R2 2026-04-30 | 976 | 2.8% (27) | 0.09 | 3.78 | 1.8% (18) | 131 | <10 | 1.66 |
| loans | R2 2026-05-31 | 1,105 | 6.4% (71) | 0.26 | 4.22 | 4.2% (46) | 181 | 9.4% (17) | 2.26 |
| loans | R2 2026-06-30 | 1,330 | 7.4% (98) | 0.36 | 5.24 | 4.6% (61) | 237 | 5.1% (12) | 1.10 |
#### T treat (lost or reduced employment; R2 07-31 equals R1)
| product | slice | lost or reduced: accounts | amount due, AED m | paid_due, lost or reduced | paid_due, has employment
|
|---|---|---|---|---|---|
| cards | R1 2026-07-31 | 1,202 | 1.76 | 11.6% (1,202) | 14.3% (1,041) |
| cards | R2 2026-04-30 | 128 | 0.21 | 18.8% (128) | 23.8% (84) |
| cards | R2 2026-05-31 | 522 | 0.81 | 12.1% (522) | 19.4% (463) |
| cards | R2 2026-06-30 | 879 | 1.34 | 11.4% (879) | 19.1% (766) |
| loans | R1 2026-07-31 | 273 | 1.17 | 22.0% (273) | 28.9% (173) |
| loans | R2 2026-04-30 | 90 | 0.38 | 21.1% (90) | 31.4% (51) |
| loans | R2 2026-05-31 | 175 | 0.75 | 25.7% (175) | 25.6% (90) |
| loans | R2 2026-06-30 | 255 | 1.05 | 22.0% (255) | 25.2% (135) |
#### T treat by A2 reachable x A4 state, R2 pooled
| product | A2 | A4 | lost or reduced: accounts | amount due, AED m | paid_due, lost or reduced | paid_due, has
employment |
|---|---|---|---|---|---|---|
| cards | reachable | high | 29 | 0.03 | 31.0% (29) | 26.9% (52) |
| cards | reachable | moderate | 217 | 0.29 | 20.7% (217) | 22.3% (291) |
| cards | reachable | low | 525 | 0.90 | 17.7% (525) | 21.7% (359) |
| cards | reachable | unknown | 418 | 0.63 | 17.0% (418) | 25.4% (287) |
| cards | not reachable | high | 21 | 0.02 | 9.5% (21) | 46.4% (28) |
| cards | not reachable | moderate | 260 | 0.33 | 6.5% (260) | 15.4% (357) |
| cards | not reachable | low | 604 | 1.04 | 8.1% (604) | 13.9% (469) |
| cards | not reachable | unknown | 658 | 0.88 | 6.1% (658) | 8.2% (510) |
| loans | reachable | moderate | 41 | 0.20 | 34.1% (41) | 59.5% (42) |
| loans | reachable | low | 246 | 1.24 | 20.7% (246) | 26.6% (94) |
| loans | reachable | unknown | 133 | 0.44 | 27.1% (133) | 32.7% (52) |
| loans | not reachable | moderate | 40 | 0.12 | 30.0% (40) | 36.6% (41) |
| loans | not reachable | low | 212 | 0.95 | 25.5% (212) | 21.4% (159) |
| loans | not reachable | unknown | 117 | 0.38 | 11.1% (117) | 12.5% (56) |
#### R recheck (A3 no_promise; R2 07-31 equals R1)
| product | slice | A3 no_promise accounts | with a stated intent | amount due of those, AED m | paid_due, pays_in_full
| paid_due, partly_or_later | paid_due, not_stated | paid_due, refuses | paid_due, no_reading |
|---|---|---|---|---|---|---|---|---|---|
| cards | R1 2026-07-31 | 10,207 | 5.0% (507) | 0.75 | 10.4% (48) | 9.1% (372) | 6.0% (199) | 1.1% (87) | 3.9% (9,501) |
| cards | R2 2026-04-30 | 7,611 | 0.7% (52) | 0.08 | <10 | 12.2% (41) | 9.1% (22) | <10 | 5.3% (7,537) |
| cards | R2 2026-05-31 | 8,117 | 3.0% (247) | 0.35 | 5.0% (20) | 7.5% (187) | 4.5% (88) | 10.0% (40) | 4.8% (7,782) |
| cards | R2 2026-06-30 | 8,913 | 4.2% (378) | 0.57 | 2.9% (34) | 8.7% (276) | 11.0% (145) | 5.9% (68) | 4.8% (8,390) |
| loans | R1 2026-07-31 | 2,412 | 9.3% (224) | 0.86 | 10.8% (37) | 18.8% (160) | 15.1% (53) | 11.1% (27) | 13.5% (2,135)
|
| loans | R2 2026-04-30 | 1,556 | 4.4% (69) | 0.29 | 16.7% (24) | 31.4% (35) | 11.8% (17) | 10.0% (10) | 12.2% (1,470) |
| loans | R2 2026-05-31 | 1,865 | 7.6% (142) | 0.57 | 27.3% (33) | 21.1% (90) | 6.7% (30) | 21.1% (19) | 13.1% (1,693) |
| loans | R2 2026-06-30 | 2,210 | 9.2% (203) | 0.77 | 24.4% (41) | 16.8% (137) | 15.2% (46) | 16.0% (25) | 15.0% (1,961) |

#### C context (share with a record), both products
| product | A2 reachable x A3 level | R1 07-31 | R2 04-30 | R2 05-31 | R2 06-30 | R2 07-31 | R2 <=90d 04-30 | R2 <=90d
05-31 | R2 <=90d 06-30 | R2 <=90d 07-31 |
|---|---|---|---|---|---|---|---|---|---|---|
| cards | reachable / kept | 23.6% (57) | <10 | 13.4% (42) | 14.9% (45) | 23.6% (57) | <10 | 13.4% (42) | 10.3% (31) |
8.3% (20) |
| cards | reachable / partly_kept | 39.0% (671) | 8.6% (144) | 21.6% (381) | 32.0% (589) | 39.0% (671) | 8.6% (144) |
21.6% (381) | 23.2% (427) | 17.7% (304) |
| cards | reachable / promised | 38.5% (352) | 8.6% (83) | 25.1% (254) | 33.4% (317) | 38.5% (352) | 8.6% (83) | 25.1%
(254) | 22.1% (210) | 20.5% (188) |
| cards | reachable / no_promise | 16.7% (195) | 3.3% (32) | 10.2% (114) | 12.3% (143) | 16.6% (194) | 3.3% (32) | 10.2%
(114) | 8.7% (101) | 7.5% (88) |
| cards | not reachable / kept | 19.4% (77) | <10 | 7.3% (23) | 13.0% (45) | 19.4% (77) | <10 | 7.3% (23) | 5.8% (20) |
4.3% (17) |
| cards | not reachable / partly_kept | 33.6% (983) | 3.1% (69) | 12.3% (319) | 22.3% (615) | 33.6% (983) | 3.1% (69) |
12.3% (319) | 12.4% (340) | 10.8% (317) |
| cards | not reachable / promised | 34.3% (682) | 3.1% (52) | 15.3% (273) | 25.6% (481) | 34.2% (680) | 3.1% (52) |
15.3% (273) | 15.1% (283) | 10.7% (212) |
| cards | not reachable / no_promise | 5.7% (511) | 0.6% (42) | 3.2% (221) | 4.9% (380) | 5.7% (511) | 0.6% (42) | 3.2%
(221) | 2.3% (182) | 1.7% (153) |
| loans | reachable / kept | 35.2% (19) | <10 | <10 | 28.3% (17) | 35.2% (19) | <10 | <10 | 20.0% (12) | <10 |
| loans | reachable / partly_kept | 34.3% (96) | 18.0% (44) | 30.1% (75) | 34.6% (89) | 34.3% (96) | 18.0% (44) | 30.1%
(75) | 27.6% (71) | 12.9% (36) |
| loans | reachable / promised | 26.6% (66) | 22.0% (45) | 30.5% (69) | 34.2% (76) | 26.6% (66) | 22.0% (45) | 30.5%
(69) | 27.9% (62) | 14.1% (35) |
| loans | reachable / no_promise | 17.4% (84) | 9.9% (28) | 18.5% (76) | 18.0% (83) | 17.4% (84) | 9.9% (28) | 18.5%
(76) | 15.8% (73) | 10.4% (50) |
| loans | not reachable / kept | 31.7% (20) | <10 | <10 | 19.6% (11) | 31.7% (20) | <10 | <10 | <10 | 17.5% (11) |
| loans | not reachable / partly_kept | 30.1% (113) | 7.6% (23) | 13.6% (49) | 22.4% (89) | 29.9% (112) | 7.6% (23) |
13.6% (49) | 13.3% (53) | 12.5% (47) |
| loans | not reachable / promised | 30.1% (89) | 8.2% (19) | 15.2% (43) | 22.8% (71) | 30.1% (89) | 8.2% (19) | 15.2%
(43) | 15.8% (49) | 14.5% (43) |
| loans | not reachable / no_promise | 10.0% (193) | 4.6% (58) | 6.6% (96) | 9.5% (166) | 10.0% (193) | 4.6% (58) | 6.6%
(96) | 6.1% (107) | 3.9% (76) |
#### P 180+ per month end (paid_due, n)
| product | month end | accounts | recorded, read | recorded, not read | no recorded call |
|---|---|---|---|---|---|
| cards 180+ | 2026-04-30 | 310,709 | 7.8% (128) | 9.0% (89) | 1.1% (310,492) |
| cards 180+ | 2026-05-31 | 312,626 | 7.5% (174) | 7.9% (101) | 1.2% (312,351) |
| cards 180+ | 2026-06-30 | 314,827 | 7.3% (165) | 9.9% (91) | 1.2% (314,571) |
| cards 180+ | 2026-07-31 | 316,738 | 5.1% (98) | 11.1% (45) | 1.2% (316,595) |
| loans 180+ | 2026-04-30 | 53,615 | 12.1% (33) | 10.0% (20) | 1.2% (53,562) |
| loans 180+ | 2026-05-31 | 54,006 | 1.9% (52) | 11.1% (36) | 1.3% (53,918) |
| loans 180+ | 2026-06-30 | 54,383 | 10.7% (56) | 10.3% (29) | 1.3% (54,298) |
| loans 180+ | 2026-07-31 | 54,819 | 9.5% (63) | 12.0% (25) | 1.3% (54,731) |
**A10. Idea 12 on R2 <= 90 d:** cards -8.8 [-10.7, -6.8] (n 2,427 / 13,959), verdict same; loans +0.0 [-4.4, 3.8] (n 701
/ 3,101), still no signal.


