# Tier stability - results (rl_60_180, cc_60_180)

Source: `tier_stability_rl_60_180.json`, `tier_stability_cc_60_180.json` (PROD run of `tier_stability.py`; BASE and PB
reproduce `inhouse_check.py` S and PB with 0 tier differences in both products, both schemes). Cohort months **Jan-May
2026 only** (12,512 loan account-months / 5,416 accounts; 74,256 card account-months / 29,629 accounts). Adjacent =
mapping built on months ≤ m-1 (4 scored months, 3 consecutive pairs); strict = ≤ m-3 (2 scored months, 1 pair). "Money @
equal share" = money captured by the top-x% of accounts, x = BASE's in-house share that month, ranked tier first, then
by the rule's estimate. Cells under 10 suppressed. Means over scored months.

## Verdict

1. **Loan churn is mostly sampling noise.** Two bootstrap resamples of one month flip **27.4 %** of loan tiers (Jaccard
   .505) against 33.8 % observed month to month (Jaccard .416): noise ≈ **81 %** of the flip and 85 % of the Jaccard
   gap. Cards: 16.6 % noise vs 16.8 % observed (≈ 99 %; against the full sample only ~12 %, so read "most", not "all").
   Level shift is real on loans from March (book AED/acct index .99 / .95 / 1.06 / 1.19 / 1.15; in-house personas 9 / 10
   / 8 / 16 / 19) but a relative cut moves monthly flips only 35.0 → 33.3 %. Tails: the top account is a median 33 % of
   a loan persona's money (71 % of persona-months above 25 %); a p99 cap moves flips 35.0 → 33.6 %. Amount source: none
   (see A4). Granularity: 73 of 226 loan personas have ≥ 10 accounts (79 % of accounts), 18 have ≥ 30, 2 have ≥ 100;
   cards 164 of 331 and 34 with ≥ 100. Not shown: how much of the remaining ~19 % is real drift vs overlap of accounts
   across months.
2. **Recommended rule** (nothing meets both criteria on loans; see trade-off below).
   - **Loans:** E2(6)-V2-C2-H0 on the family × reach × credible-or-able key (G3): pooled estimate over up to 6 months,
     mean capped at the training p99, cut relative to the book level, no hysteresis. The **simpler persona-preserving
     fallback** is E2(6)-V2-C1-H0 (P1: full persona, pooled, capped).
   - **Cards:** the pre-registered selection returns **G2** (E1, FRN key, otherwise today's rule); I prefer **G3** (same
     key, pooled 6 months, capped, relative cut) because G2's pick rests on a single churn pair and its list overlap
     fell to 50.6 % in Apr→May. If GRR wants the full persona kept, **PB** (E2(6)-V1-C1-H1) is the alternative.
3. **Stability reached and value paid, against today's rule (adjacent; strict in brackets).**
   - Loans G3: tier changes with persona unchanged 4.5 % (6.6) vs 35.0 (27.4); list Jaccard .80 vs .42; account overlap
     100 vs 45.5; money @ equal share 25.4 vs 25.1 (strict 15.9 vs 17.1); AUC .743 vs .718. P1: 11.0 (12.4) %, Jaccard
     .75, money @ equal share 26.1.
   - Cards G3: 1.2 % (3.0) vs 12.9 (16.2); Jaccard .89 vs .57; overlap 99.7 vs 77.5; money @ equal share 44.6 vs 44.6
     (strict -0.4 pt); AUC .810 vs .803. PB: 5.4 % (8.6), Jaccard .78, money @ equal share 44.6.
   - **Cost: none visible in adjacent;** all rules sit within ±1.4 pt of BASE on money @ equal share, inside the
     month-to-month spread (BASE loans 24.8-25.4, cards 39.0-51.9). In strict (2 months) every loan rule gives up
     0.8-1.3 pt (G3 1.1) and cards ≤ 0.85 pt. The price is coarseness: G3 has 20 loan / 27 card FRN cells, with 2-4 loan
     and ~6 card in-house cells, so tiers no longer follow location or credibility/ability separately.
4. **Cadence (data-limited: h ≤ 4).** Loans G3: frozen vs rebuilt loses 0.0 / 0.1 / -0.6 pt money @ equal share at h = 2
   / 3 / 4 (paid -0.1 / -0.8 / -1.1 pt); mapping churn between builds 4.3 / 5.9 / 11.3 % at h = 1 / 2 / 3. **Re-run
   every 3 months on loans** (not evidenced beyond). Cards G3: -0.1 / +0.2 / -1.1 pt, churn 1.9 / 2.8 / 5.9 % → **every
   3 months**; PB and BASE already lose 2-2.5 pt at h = 2, so with the full persona re-run monthly. Twice a year is
   **not testable** with 5 cohort months: h = 9 and 12 are impossible, h = 3 rests on 2 pairs and h = 4 on 1.
5. **Early re-run trigger (bands from the five validation months).**
   - Loans: in-house realised paid % outside **65-80 %** (G3 ran 70.5-75.8; BASE 57-65), the book AED/account outside
     **±20 % of the reference** (index .95-1.19 observed), or in-house account share outside **6-15 %** (G3 6.0-14.4;
     May 6.0 % is already at the edge).
   - Cards: in-house paid % outside **52-60 %** (G3 54.4-59.2), book AED/account outside **±10 %** (index .94-1.09),
     in-house share outside **14-22 %**.
   - The bands are the observed range, not a tested threshold; treat them as provisional.
6. **Hold-out: not run.** `payment_data_ends` = 2026-08-31 in both products, so the last complete 3-month outcome is
   **May 2026**, not July as assumed. June/July have axis rows but no complete outcome; `holdout_present` = [] and no
   hold-out file was written. Nothing below is confirmed out of time. The rule above was fixed from validation months
   only.
7. **Loan types.** Counts (account-months / accounts): Personal 4,660 / 1,922, Personal Cash 4,142 / 1,845, Auto 3,710 /
   1,649 (all above the 1,000-row own-fit threshold; no "other"). The pooled G3 mapping holds on all three: tier changes
   3.1 / 6.6 / 4.6 %, in-house paid 71.7 / 73.7 / 72.1 %. Its lift (money share ÷ account share) is 2.7 / 2.3 / **1.0**:
   on **Auto it adds no money over the account share**, and under BASE too (1.2). Own fits per type are no better and
   Auto collapses (G3 own fit lists 1.2 % of Auto accounts). One pooled rule works for all three on stability; Auto has
   little value signal at this sample size.
8. **Needs.** (a) Payment data refreshed past 2026-10-31 (card transactions, `int_loan_master`) to get June/July
   outcomes and rerun for the hold-out; (b) longer history (a 12-month pool is what noise removal needs; today ≤ 5
   months); (c) a dated loan payment source (none in the catalog) to test the month-grain `total_paid` question.

## Key tables

### A1 noise floor and A2 level shift

| | loans | cards |
|---|---|---|
| resample-vs-resample tier flip % (per month range) | 27.4 (26.3-28.2) | 16.6 (11.5-22.3) |
| observed BASE flip, h = 1 | 33.8 | 16.8 |
| list Jaccard: noise / observed | .505 / .416 | .593 / .570 |
| share of observed flip that is noise | 0.81 | 0.99 |
| Spearman of persona value, consecutive months | .63 / .45 / .58 / .47 | .85 / .82 / .76 / .73 |
| book AED/acct, Jan-May | 3,117 / 2,997 / 3,340 / 3,746 / 3,637 | 683 / 610 / 588 / 630 / 639 |
| in-house personas at fixed cut (loans) | 9 / 10 / 8 / 16 / 19 | - |
| side-of-cut flips, fixed cut, % | 9.5 / 13.6 / 19.0 / 20.0 | 15.5 / 15.4 / 17.8 / 19.2 |
| side-of-cut flips, relative cut, % | 9.5 / 11.9 / 12.7 / 17.1 | 14.2 / 14.1 / 16.4 / 20.5 |

### Rules, adjacent scheme

Tier change = share of accounts whose tier changes while their persona stays the same (pooled over pairs; strict in
brackets).

**Loans**

| id | rule | flips % (strict) | Jaccard | in-house share % | in-house paid % | money @ equal share (Δ BASE) | AUC |
|---|---|---|---|---|---|---|---|
| BASE | E1-V1-C1-H0 | 35.0 (27.4) | 0.42 | 13.8 | 62.2 | 25.1 (+0.00) | 0.718 |
| PB | E2(6)-V1-C1-H1 | 13.9 (10.3) | 0.80 | 10.0 | 66.7 | 25.7 (+0.55) | 0.728 |
| N6 | E2(6)-V1-C1-H0 | 15.4 (12.8) | 0.75 | 11.4 | 63.9 | 25.7 (+0.55) | 0.728 |
| P1 | E2(6)-V2-C1-H0 | 11.0 (12.4) | 0.75 | 10.0 | 67.4 | 26.1 (+0.95) | 0.731 |
| H2 | E1-V1-C1-H2 | 8.1 (1.4) | 0.78 | 11.4 | 62.1 | 24.8 (-0.40) | 0.718 |
| G2 | E1[FRN]-V1-C1-H0 | 24.0 (17.4) | 0.53 | 11.7 | 67.7 | 25.4 (+0.23) | 0.737 |
| S4 | E3(3)-V2-C2-H0 | 10.0 (10.2) | 0.69 | 10.4 | 72.8 | 25.8 (+0.62) | 0.747 |
| **G3** | E2(6)[FRN]-V2-C2-H0 | 4.5 (6.6) | 0.80 | 12.1 | 73.0 | 25.4 (+0.28) | 0.743 |

**Cards**

| id | rule | flips % (strict) | Jaccard | in-house share % | in-house paid % | money @ equal share (Δ BASE) | AUC |
|---|---|---|---|---|---|---|---|
| BASE | E1-V1-C1-H0 | 12.9 (16.2) | 0.57 | 15.2 | 57.1 | 44.6 (+0.00) | 0.803 |
| PB | E2(6)-V1-C1-H1 | 5.4 (8.6) | 0.78 | 15.7 | 56.7 | 44.5 (-0.05) | 0.810 |
| N6 | E2(6)-V1-C1-H0 | 5.9 (9.9) | 0.70 | 16.2 | 56.6 | 44.6 (-0.02) | 0.810 |
| P1 | E2(6)-V2-C1-H0 | 6.6 (9.4) | 0.70 | 15.4 | 57.9 | 45.0 (+0.42) | 0.813 |
| H2 | E1-V1-C1-H2 | 4.9 (0.5) | 0.76 | 15.3 | 57.3 | 44.6 (+0.00) | 0.803 |
| G2 | E1[FRN]-V1-C1-H0 | 4.3 (4.4) | 0.53 | 16.4 | 57.9 | 44.7 (+0.07) | 0.808 |
| S4 | E3(3)-V2-C2-H0 | 4.0 (1.8) | 0.83 | 16.4 | 57.9 | 45.1 (+0.48) | 0.818 |
| **G3** | E2(6)[FRN]-V2-C2-H0 | 1.2 (3.0) | 0.89 | 16.9 | 56.9 | 44.6 (+0.02) | 0.810 |

L2, L3, T2, T3 (relative cut, rank cut, cap, P×amount alone) stay at 25-34 % flips on loans and 12-13 % on cards: **no
stability gain**. Every rule keeps the order in-house > agency > non-workable in every fold. Full 20-rule tables:
`tier_stability_<model_id>.md`.

### Selection (coded before looking at any hold-out; here there is none)

Criteria: mapping churn at the cadence < 10 %; money @ equal share lost vs BASE ≤ 2 pt in adjacent **and** strict;
cadence ≥ 3 months.

| | meets churn | meets value | meets cadence | meets all | auto pick | trade-off curve |
|---|---|---|---|---|---|---|
| loans | none (best G3 11.3 %) | all 20 | 17 of 20 | none | none | G3, S4, S1 |
| cards | G2 2.3 %, G3 5.9 %, + others at cadence 1-2 | all | G2, G3, P3, S4… | G2, G3 | G2 | G2, S3, G1 |

### Cadence: frozen minus rebuilt every month

Cells: money @ equal share / paid @ equal share, in points. Churn = % of tiers that change between builds h months
apart.

| | h = 2 | h = 3 | h = 4 | churn h1 / h2 / h3 |
|---|---|---|---|---|
| loans BASE | +.3 / +2.2 | -.5 / +2.0 | **-2.0** / +2.6 | 33.8 / 34.9 / 45.1 |
| loans PB | -.1 / +2.6 | -.2 / +.3 | -.5 / -.1 | 13.4 / 22.2 / 31.1 |
| loans G3 | +.1 / -.1 | +.1 / -.8 | -.6 / -1.1 | 4.3 / 5.9 / 11.3 |
| cards BASE | **-2.2** / -.7 | -1.9 / -1.0 | -4.0 / -1.2 | 16.8 / 19.5 / 27.0 |
| cards PB | **-2.5** / -1.6 | -2.0 / -1.6 | -3.9 / -3.2 | 6.3 / 9.5 / 14.2 |
| cards G3 | -.1 / +.1 | +.2 / +.9 | **-1.1** / -.1 | 1.9 / 2.8 / 5.9 |

Pairs per h: 4 / 3 / 2 / 1 (cutoffs differ by h); churn pairs 3 / 2 / 1 / none.

### Loans by type - pooled G3 mapping, adjacent

| type | account-months | tier change % | in-house share % | in-house paid % | money share % (lift) |
|---|---|---|---|---|---|
| Personal | 4,660 | 3.1 | 8.2 | 71.7 | 22.1 (2.7×) |
| Personal Cash | 4,142 | 6.6 | 13.9 | 73.7 | 32.1 (2.3×) |
| Auto | 3,710 | 4.6 | 13.4 | 72.1 | 14.0 (1.0×) |

### A3-A5 in short

- **A3 tails (loans / cards):** in-house persona-months, median top-1 account share of money .33 / .23; p95 cap changes
  25.6 % / 25.1 % of persona-months by > 10 % (25 / 40 in→out crossings, 0 out→in); p99 cap 6.8 % / 8.4 %.
- **A4 amount source:** no dated customer loan payment source in the catalog (`comp_financial_tran_repos_dly` is
  CASA/FTR with no loan repayment class; `prm_loan_payments` is retired). `int_loan_master` holds one snapshot date per
  month, so `total_paid` is month-end month-to-date. Comparison not run, none built.
- **A5 granularity (loans, mean per month):** 226 personas; 73 with ≥ 10 accounts (79 % of accounts), 18 with ≥ 30 (41
  %), 7 with ≥ 50 (25 %), 2 with ≥ 100 (11 %). FRN: 20 cells, all ≥ 10. No-location: 96 personas, 48 with ≥ 10.

## Caveats

- **No hold-out and only five cohort months** (Jan-May). Strict scores April and May with mappings from 1 and 2 months
  of history, so N3 = N6 and P1 = P2 in strict, and every strict figure is one pair. Cadence at h = 3 is 2 pairs, h = 4
  is one pair; churn at h = 4 is not measured.
- **G3 is a coarser product.** It tiers on family × reach × credible-or-able (20 loan, ~27 card cells). On loans 2-4
  in-house cells decide the list: share ran 14.4 / 14.3 / 13.8 / 6.0 % and the Apr→May Jaccard was .39. Low flips partly
  come from having few cells to flip.
- **Relative-cut rules can shrink the list** after the book moves (loans S4 May 3.1 % in-house, S2 May 0.6 %); L3
  realises 7.7 % on loans although it targets BASE's share. Money @ equal share ignores the cut and hysteresis (L2 = L3
  = BASE, P1 = P2 = P3 on it), so "value ok" says nothing about those.
- **Adjacent is optimistic:** the mapping at m-1 includes outcomes of months m to m+2 that would not be known in
  production; strict is the deployable number and is thin. Cards' "frozen loses 2 pt at h = 2" partly reflects that the
  rebuilt comparator sees overlapping outcomes.
- **Cohort overlap:** an account is in up to five cohort months (loans ~77 % of accounts repeat between consecutive
  pairs under BASE), so folds are not independent and the noise share is an upper-ish read.
- **Observed payments reflect today's handling;** loan `total_paid` is month-grain; the suppressed values (G3 cards 2 of
  3 flip pairs <10 changes) are left out of means, so the 1.2 % pooled figure is the one to read.
- G2's `why` text quotes AUC .749 vs .757 from the earlier run; this run has .808 vs .803 (cards) and .737 vs .718
  (loans).
