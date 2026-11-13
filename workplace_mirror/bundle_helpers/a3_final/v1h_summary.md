# A3 V1h summary - promise deadline (B20 / GRR / LEN) and Unknown -> Low, back-tested on the next 3 months

Source: `results_v1h_<model_id>.md` x4 (PROD, persona_end_date 2026-08-31). Observation months 2026-03-31, 04-30, 05-31,
  outcomes to 2026-08-31. Rows (accounts): cc_60_180 45,016 (22,714); cc_180_plus 932,077 (314,294); rl_60_180 7,975
  (4,312); rl_180_plus 160,891 (54,172). AUC intervals: account-group bootstrap, paired. "Clear" = the paired interval
  of the difference excludes 0. At cc_60_180 GRR = B20 (same rule, shown once). At RL, LEN (30 days to month end) is
  almost the same rule as B20 (next month end).

## Per question, key numbers

**Q1 states (NEW, GRR deadline; High/Mod/Low; ex_unknown share of rows)**
- cc_60_180 (= B20): 4.0 / 21.7 / 74.3 %; ex_unknown 12.2 %. LEN: 6.0 / 24.3 / 69.7 %.
- cc_180_plus: 0.0 / 2.6 / 97.4 %; ex_unknown 83.0 %. B20 0.1/2.7/97.3; LEN 0.1/2.9/97.0.
- rl_60_180: 3.8 / 26.4 / 69.8 %; ex_unknown 7.0 %. B20 6.4/29.5/64.1; LEN 6.4/29.5/64.1.
- rl_180_plus: 0.2 / 3.6 / 96.2 %; ex_unknown 65.1 %. B20 0.3/3.7/96.0; LEN same as B20.
- Rows changing state: RL 61-180 GRR vs B20 8.3 %, vs LEN 8.4 %; CC 61-180 GRR vs LEN 6.8 %; 180+ under 0.6 %
  everywhere.

**Q2 outcomes by state (GRR/NEW; paid_due Hi / Mod / Low)**
- cc_60_180: 64.9 / 35.2 / 11.0 %; cured about 0.2 % in every state (no cure signal); rolled 47 / 73 / 93 %.
- cc_180_plus: 50.2 / 30.6 / 1.6 %. rl_60_180: 71.5 / 54.2 / 26.2 %; cured 8-13 % flat; rolled 54 / 67 / 83 %.
- rl_180_plus: 67.2 / 32.5 / 1.4 %; cured 41.9 / 23.6 / 0.6 %.
- Level A (cc_60_180, B20): paid_due Kept 38.4, Partly 32.9, Broken 28.5, Thin 11.6 %. Thin is the worst level, not
  Broken (same at RL 61-180: Broken 40.5 vs Thin 27.7).
- "Exited" (no level at month 3) is large at cc_60_180 (Low 42.8 %, High 24.7 %): kept as own column, read rolled with
  it.

**Q3 ranking, state NEW, AUC (95 % interval)**
- cc_60_180 paid_due: B20=GRR 0.692 [0.685, 0.700], LEN 0.714 [0.706, 0.722] (+0.022 clear). paid_any 0.689 vs 0.711
  (+0.022 clear). not_rolled 0.715 vs 0.736 (+0.021 clear). cured 0.493 vs 0.492 (no signal, overlap).
- cc_180_plus paid_due: B20 0.670, GRR 0.665, LEN 0.690 (LEN +0.020 vs B20, +0.025 vs GRR, clear). paid_any 0.657 /
  0.652 / 0.674 (clear).
- rl_60_180 paid_due: B20 0.666, GRR 0.643, LEN 0.666. B20 over GRR +0.023 clear; LEN over B20 +0.001. paid_any 0.649 /
  0.627 / 0.650. not_rolled 0.620 / 0.610 / 0.621 (GRR -0.011 clear). cured about 0.52, overlap.
- rl_180_plus paid_due: B20 0.746, GRR 0.736, LEN 0.746 (GRR -0.010 clear; B20 vs LEN overlap). paid_any 0.718 / 0.706 /
  0.718. cured 0.808 / 0.805 / 0.808, overlap.
- Same ranking with ex_unknown left out (OLD): about 0.01 lower AUC everywhere, same order of deadlines.
- Points total beats the 3-rung state: 180+ paid_due 0.82 (CC) / 0.86 (RL) vs 0.67 / 0.75; 61-180 0.70 vs 0.69 (CC),
  0.70 vs 0.67 (RL). The state throws away ordering.
- Level A alone: 0.53-0.60 (Kept>Partly>Thin>Broken) vs 0.62-0.67 (Broken above Thin) at 61-180; the Thin>Broken order
  is the wrong one.

**Q4 who moves**
- Demoted rows behave like the upper state, not the lower: rl_60_180 GRR Low / B20 Moderate (395 rows) paid_due 48.6 %
  (stayed Moderate 52.6, stayed Low 23.9); GRR Low / B20 High (66) 65.2 % vs High 71.2. cc_60_180 GRR Low / LEN Moderate
  (2,032) 27.4 % (Moderate 32.4, Low 9.8). cc_180_plus GRR Low / B20 Moderate (1,718) 25.7 % (Moderate 30.5, Low 1.5).
- RL events: paid under both 3,472 (account paid_due 57.5 %); paid only in the following month (B20 counts, GRR not)
  1,569 (57.7 %); paid under neither 2,190 (45.9 %). Late payers look like payers. rl_180_plus: 1,190 late (37.7 %) vs
  both 2,748 (40.2 %) vs neither 5,300 (17.6 %). cc_180_plus: B20-only 4,073 (27.0 %), both 8,868 (27.2 %), neither
  52,576 (18.0 %).

**Q5 ex_unknown (GRR deadline)**
- Outcomes vs other Low / Moderate (paid_due): cc_60_180 3.9 vs 12.4 / 35.2; rl_60_180 9.2 vs 28.1 / 54.2; cc_180_plus
  0.5 vs 7.6 / 30.6; rl_180_plus 0.2 vs 3.9 / 32.5. Never better than other Low: paid_due -8.4 / -18.9 / -7.1 / -3.7 pp,
  paid_any -9.3 / -24.4 / -9.5 / -5.8 pp (all intervals exclude 0); rolled +6.1 pp (cc_60_180), +13.8 pp (rl_60_180);
  cure no better (rl_60_180 -7.6 pp). The tool's "clearly better" flag on exited (RL and CC 180+, about -0.1 to -1.2 pp)
  is not a real advantage: exits are near zero everywhere there.
- cc_60_180 (5,483): not censored (5,482). On book < 6 months at the episode 3,877 (71 %, of which 2,351 had no billed
  month), 6-12: 275, 12-24: 293, 24+: 1,037 (597 with no bill: dormant). Ledger months missing 7-12 for 3,939 young
  rows; 1,326 old rows (on book >= 12) have a ledger but no bill. Episode age 4-6 months 70 %. So about 70 %
  early-delinquency-like, about 25 % old idle accounts.
- rl_60_180 (556): all not censored, all on book < 6 months, 12 months missing from the ledger: early-delinquency loans.
- cc_180_plus (773k): censored 508k (66 %); not censored 265k, of which 244k have the episode 25+ months old (charge-off
  age >= 24 months); 261k of the 265k miss 7-12 ledger months.
- rl_180_plus (105k): censored 94.9k (91 %); charge-off age >= 24 months 101k (96 %); outcomes about 0.1-0.2 %.

**Q6 stability (state AUC, paid_due)**: ordering of deadlines is the same in all 3 months. cc_60_180 B20 0.710 / 0.695 /
  0.672, LEN 0.730 / 0.716 / 0.695. rl_60_180 B20=LEN 0.684 / 0.667 / 0.655, GRR 0.662 / 0.644 / 0.632. cc_180_plus
  0.674 / 0.668 / 0.668 (B20), LEN 0.697 / 0.688 / 0.685. rl_180_plus B20=LEN 0.746-0.748, GRR 0.735-0.737. AUC falls
  for later months at 61-180 for all deadlines.

## Verdict

**61-180.** A 30-day window ranks best on paid_due, paid_any and not_rolled. At cards it beats the next statement (=
  GRR) by about 0.02 AUC, clear in every month. At loans it is level with bundle 20's next month end (+0.001) and GRR's
  month end is worse by 0.023 on paid_due and paid_any and 0.011 on not_rolled: yes, GRR's month end costs ranking for
  loans, and the rows it demotes behave like the state they came from. Cure does not discriminate on any deadline at
  cards (AUC about 0.49, cure 0.2 %) or loans (about 0.52); read paid and not_rolled. Cards: the next statement is the
  weakest of the three; the gain from 30 days is modest in size but stable.

**180+.** Cure and roll are near zero by construction at cards, so paid_due and paid_any lead. Cards: 30 days best
  (+0.020 over the next statement, +0.025 over GRR's month end, clear); GRR's month end is worst. Loans: next month end
  and 30 days are level (overlap), GRR's month end is 0.010-0.012 lower, clear. Differences are small against coarse
  states (96-97 % of rows sit in Low), and the points total ranks far better (0.82-0.86) than the state, so the state
  thresholds, not the deadline, are the bigger loss at 180+.

**ex_unknown.** It does not look better than other Low on any outcome, so by the stated test it belongs in Low and not
  in a better state of its own. It is clearly worse than the other Low rows on payments (and on roll at 61-180), and it
  is most of Low at 180+ (cards 83 % of rows, loans 65 %), so Low is no longer one population. At 61-180 it is mostly
  young accounts with no history (EPD-like, 71 % of card cases; all loan cases) plus idle old cards; at 180+ it is
  mostly long charged-off accounts and censored episodes. Whether to show it as a labelled sub-group of Low (reason
  `no_record`) is the user's call; the data say it is the weakest group, not a separate "unknown but plausibly fine"
  group.

## Caveats
- Cure at cards 61-180 is about 0.2 % and "exited" (no level at month 3) is 25-43 %; the data cannot separate closed /
  written off / sold from missing billing.
- Q5's "ex_unknown clearly better" flag fires on exited at 180+ where exits are about 0; ignore it.
- Charge-off age at cc_180_plus is a proxy (months since the episode start, non-censored rows only; 508k rows unknown);
  rl_180_plus used `feat_loan_chargeoff_segment`.
- Pooled rows share accounts across 3 months; intervals resample account groups, so they account for that.
