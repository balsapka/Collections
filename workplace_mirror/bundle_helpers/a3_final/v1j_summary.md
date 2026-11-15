# A3 V1j summary - the final test of the promise points (Dimension A)

Source: `results_v1j_<model_id>.md` x4 (PROD, persona_end_date 2026-08-31; months 03-31, 04-30,
05-31; outcomes to 08-31). Episode rows (accounts): cc_60_180 45,016 (22,714); cc_180_plus 932,077
(314,294); rl_60_180 7,975 (4,312); rl_180_plus 160,891 (54,172). No part failed; P0 re-scored =
shipped `a3_state` (0 rows differ) in all four. Deadlines: GRR as shipped, LEN 30 days. "Clear" =
95% account-group interval (paired where a difference) excludes 0. Points: P0 today (Kept 2 / Partly
1 / Broken -1); P2 Broken +1; P5 Kept 3 / Partly 2 / Broken, T2, T1 1 / T0 0; P6 = P5 with Broken
split (BA 1, BN 0, same for T2); P7 = P5, High >= 5; P8 = Kept 2 / Partly 1 / Broken 0 / contact
without promise (C1) +1.

## Q1 Promise or contact? paid_due next 3 months, GRR (LEN)
- C0 / C1 / Broken: cc_60 4.2 / 15.8 / 28.5 (25.7); rl_60 17.9 / 32.9 / 47.9 (40.0); cc_180 0.6 /
  9.7 / 17.6 (13.8); rl_180 0.6 / 10.1 / 19.8 (14.9). Contact alone lifts C1 over C0 by +9.6 to
  +15.1 points, clear everywhere.
- Matched Broken vs C1 (same B, C, DPD level, A2 reachability, A4 state, loan type), GRR (LEN):
  cc_60 +6.1 (+6.0) clear; rl_60 +4.4 clear (+4.6 not clear); cc_180 +2.9 (+1.7) clear; rl_180 +4.5
  clear (+0.8 not clear). Matching removes half or more of the unmatched gap (cc_60 +12.7 -> +6.1;
  rl_180 +9.7 -> +4.5). T2 vs C1 matched is +1.8 to +7.6, clear in all eight.
- Reading: **both**. A promise adds a clear but small gain over contact; most of the Broken > Thin
  gap in V1i was contact and reachability. Whether C1 sits nearer C0 or Broken depends on the
  deadline (GRR: cc_60 and rl_180 nearer C0; LEN: all four nearer Broken), so C1 is not "like never
  promised".

## Q2 Is Broken one group? BA (attempted: >= 100 AED around a broken promise) vs BN (nothing),
paid_due GRR
- BA / BN: cc_60 33.4 / 17.9; rl_60 50.2 / 43.9; cc_180 24.3 / 12.7; rl_180 24.7 / 16.4. BA - BN
  clear in cc_60 (+15.5), cc_180 (+11.6), rl_180 (+8.3); rl_60 not clear (+6.3 [-3.4, +13.8]; LEN
  +8.8 not clear, only 131 BN rows). BA is 11.0 / 6.6 / 0.5 / 0.3% of rows, BN 5.1 / 3.8 / 0.6 /
  0.4%.
- BN vs C1 (never promised, contacted): +2.0 n.s. (cc_60), +11.0 clear (rl_60), +2.9 clear (cc_180),
  +6.3 clear (rl_180) under GRR; under LEN all four are not clear (+0.2, +1.4, +0.7, +3.5). A broken
  promise with no money behind it is worth no more than contact in most cuts (rl GRR is the
  exception).
- BA vs Partly: cc_60 +0.5 n.s., rl_60 -3.7 n.s. (BA pays like Partly at 60-180); at 180+ BA is
  clearly below Partly (cc -6.2 GRR / -15.7 LEN; rl -18.8 / -25.9).
- T2 splits the same way and more sharply: T2a - T2n +18.9 / +9.7 (n.s. GRR; clear paid_any) / +33.4
  / +25.2 (GRR). Event mix of broken events: nothing 55% (cc_60) to 73% (cc_180, rl_180);
  late-in-full 33% cc_60, 6% rl_180; partial 32% rl_60.
- Reading: Broken (and T2) is **not one group**; the signal is whether money moved around the
  promise, not that a promise was broken. Caveat: BA is defined from payments, so it overlaps
  Dimension B (payment level); no matched test of BA vs BN was run.

## Q3 Point schemes: state AUC on paid_due, GRR (LEN); every scheme is clear vs P0
- cc_60 (P0 0.692 [0.714]): P2 +.045 [+.026]; **P5 +.059 [+.042]**; P6 +.055 [+.040]; P7 +.037
  [+.025]; P8 +.018 [+.008].
- rl_60 (0.643 [0.666]): P2 +.030 [+.009]; **P5 +.045 [+.026]**; P6 +.036 [+.021]; P7 +.037 [+.020];
  P8 +.012 [+.005 n.s.].
- cc_180 (0.665 [0.690]): P2 +.032 [+.018]; P5 +.083 [+.058]; P6 +.055 [+.040]; P7 +.083 [+.057];
  **P8 +.084 [+.077]**.
- rl_180 (0.736 [0.746]): P2 +.020 [+.010]; P5 +.047 [+.037]; P6 +.028 [+.024]; P7 +.046 [+.036];
  **P8 +.075 [+.072]**.
- Best order-preserving scheme (Kept > Partly > Broken): **P5 at 60-180, P8 at 180+**; P6 (Broken
  split) is below P5 in all four; P7 (High >= 5) is below P5 at 60-180 and shrinks High back to P0
  size (cc_60 4.0%); P8 is the worst of P5-P8 at 60-180. P5 beats P2 in every month and DPD level
  (cc_60 +.011 to +.018; rl_60 +.006 to +.019).
- Money: High / High+Moderate hold of all AED collected, GRR, P0 -> best: cc_60 12.2 / 52.6 -> 32.9
  / 78.0 (P5); rl_60 6.8 / 42.4 -> 18.0 / 63.3; cc_180 0.8 / 27.0 -> 1.0 / 41.8 (P8); rl_180 3.3 /
  38.3 -> 5.6 / 58.4. AED-weighted rank AUC moves the same way (cc_60 0.640 -> 0.694; rl_180 0.673
  -> 0.753).
- State mix P0 -> best (High / Moderate / Low, GRR): cc_60 4.0/21.7/74.3 -> 11.8/32.9/55.3; rl_60
  3.8/26.4/69.8 -> 11.0/33.7/55.3; cc_180 0.0/2.6/97.4 -> 0.1/5.1/94.9; rl_180 0.2/3.6/96.2 ->
  0.4/7.7/91.9. Rows changing state: 26.8% / 21.7% (60-180), 2.5% / 4.4% (180+).

## Q4 Robustness of the best scheme (P5 at 60-180, P8 at 180+) vs P0 and P2
- Positive vs P0 in every month, DPD level and (RL) loan type, GRR and LEN; High > Moderate > Low
  holds in every slice (P0 fails only on RL Auto at 60-180, GRR). Gain over P2: +.006 to +.020 at
  60-180; +.05 to +.06 at 180+ (month).
- 180+ by charge-off age: P8 - P0 is larger at >= 24 months (cc +.099, rl +.076) than < 24 (+.045,
  +.032) but positive in both.
- Exceptions: cc_180 DPD level 8 (8,734 rows) P8 - P2 is -.007 (GRR) / -.006 (LEN), still above P0.
- **Snippet defect (cosmetic):** at rl_180_plus the DPD-level slice is `ceil(dpd / 30)`, so ~100
  levels print (about 400 lines in the file, most `n/a` with 300 rows and AUC 0.5 / 1.0). Not a
  result; band the level (e.g. 7-12, 13+) before any rerun.

## Q5 Who moves (best scheme vs P0), paid_due GRR
- cc_60 (P5): Low -> Moderate 22.6 (stayed Low 7.0, stayed Moderate 26.5); Moderate -> High 50.5
  (stayed High 64.9). rl_60: 45.8 (21.0, 49.9); 65.6 (71.5). cc_180 (P8): Low -> Moderate 17.4 (1.1,
  30.4), 87.6% C1. rl_180: 11.5 (0.9, 30.5), 95.6% C1.
- Movers pay between Low and Moderate (Low -> Moderate) and between Moderate and High (Moderate ->
  High); they are far more reachable than stayed-Low. BN is 12.1% of cc_60 movers, 10.8% rl_60, 4.6%
  cc_180, 2.0% rl_180.

## Q6 Kept vs Partly (Kept - Partly paid_due points, GRR / LEN)
- 60-180: cc +5.5 clear / +5.5 clear; rl +4.1 n.s. / +9.1 clear. Kept > Partly holds.
- 180+: cc **-9.4 clear / -7.8 clear** (AED -538 clear GRR); rl -6.9 n.s. / -7.5 clear (AED -2,511
  clear GRR). Kept < Partly is real at 180+, on small groups (cc 417 / 1,126 rows, rl 227 / 475 of
  160k-930k). The "Kept 3 / Partly 2" order has no support there, but Kept is 0.0-0.3% of rows so it
  does not move the state.

## Q7 A2 segments: does P0 rank as well as engagement credit inside S1 (reachable, in country)? GRR
- cc_60: **NO** (P5 +.030, P6 +.038 clear). rl_60: **NO** (+.032, +.026). cc_180: **NO** (+.021,
  +.033). rl_180: **YES** (P5 +.006, P6 +.005 n.s.; LEN -.009 / -.001) on only 1,892 S1 rows, wide
  intervals.
- S2-S5 (and rl_180 S0, no A2 row): P5 and P6 clear + in all, +.012 to +.080 (largest S5 / S4 at
  cc_180).
- P7 (High >= 5) does not gain in S1 (cc_60 -.008 GRR, -.011 clear LEN); P2 loses in S1 at 180+
  under LEN (cc -.015, rl -.011 clear).
- Reading: the promise adds evidence beyond reachability in three of four models; in the segment
  where the axis is used most (S1, 12-14% of 60-180 rows) it still helps. No sign that engagement
  credit is reachability showing through, except possibly rl_180.

## Verdict (Dimension A points)
1. **Give Broken a positive point.** Replacing P0's -1 raises state AUC clearly in all four models,
   both deadlines, every month, and in S1 in 3 of 4. P2 (+1 only) is superseded by P5.
2. **P5 at 60-180** (Kept 3 / Partly 2 / Broken 1 / T2 1 / T1 1 / T0 0; High >= 4) is best on state
   AUC, money in High, stability and keeps Kept > Partly > Broken. P6 (split Broken by money) and P7
   (higher High threshold) do not beat it.
3. **At 180+ contact beats promise** (P8 over P5: cc GRR equal, LEN +.019; rl +.028 / +.035) because
   85-88% of rows never promised and C1 vs C0 is a +10 point gap. The two are not exclusive: **not
   tested** P5 with C1 +1 (a hybrid), the obvious next scheme; I would not adopt P8 alone, as at
   60-180 it is worst of P5-P8.
4. **Do not split Broken or T2 into BA / BN in the points** (P6 < P5), but BA/BN is real information
   (Q2) and worth a reason code; the T2a/T2n gap (+19 to +33) is larger than any Broken gap.
5. Kept < Partly at 180+ stands (cc clear); small groups, no action.

## Caveats
- In-sample on three overlapping months (account-group bootstrap handles repeats); no holdout;
  high-tail thresholds (High >= 4 on the larger P5 scale) not tuned, so part of the P5 gain is a
  bigger High state (4.0 -> 11.8% cc_60); the money-in-High columns show the extra rows do carry
  money.
- Best scheme selected on GRR state AUC; LEN gains are smaller (cc_60 P5 +.042 vs +.059) but clear
  and same ranking, except rl_60 P8 (n.s.).
- The deadline for T1 / T2 / Broken under GRR at RL and 180+ is month-end, so no T1 there.
- Not changed: the shipped A3 node, catalog and configs (R18). Adopting P5 / P8 is a separate build
  task.
