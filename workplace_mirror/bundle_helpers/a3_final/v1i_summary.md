# A3 V1i summary - Thin vs Broken promises in Dimension A's points

Source: `results_v1i_<model_id>.md` x4 (PROD, persona_end_date 2026-08-31; months 03-31, 04-30, 05-31; outcomes to
08-31).
Episode rows (accounts): cc_60_180 45,016 (22,714); cc_180_plus 932,077 (314,294); rl_60_180 7,975 (4,312); rl_180_plus
160,891 (54,172). No part failed; P0 re-scored = shipped state (0 rows differ) and T0+T1+T2 = Thin in all four.
Deadlines: GRR as shipped, LEN 30 days. "Clear" = 95% account-group interval (paired where a difference) excludes 0.
Points: P0 Broken -1; P1 0; P2 +1; P3 Broken 0 and Thin -1; P4 (data-led, rule in the README) Broken 0, T0 -1, T1/T2 0.

## Q1 Sizes (GRR; LEN in brackets)
- cc_60_180: Kept 2.7 [5.7]%, Partly 15.6 [20.2], Broken 16.0 [10.8], T0 51.8, T1 1.0 [1.6], T2 12.9 [9.9].
- cc_180_plus: Kept 0.0 [0.1], Partly 0.8 [1.3], Broken 1.1 [0.9], T0 95.0, T1 0.0 [0.3], T2 3.1 [2.4].
- rl_60_180: Kept 5.7 [11.7], Partly 14.0 [15.2], Broken 10.4 [4.6], T0 59.8, T1 0.0 [1.9], T2 10.1 [6.8].
- rl_180_plus: Kept 0.1 [0.3], Partly 1.2 [1.3], Broken 0.7 [0.5], T0 96.1, T1 0.0 [0.2], T2 1.9 [1.6].
- Thin is mostly T0 (never promised). T1 is 0 under GRR at 180+ and RL (month-end deadline: every event is concluded).

## Q2 paid_due next 3 months, GRR (Kept / Partly / Broken / T0 / T1 / T2)
- cc_60_180: 38.4 / 32.9 / 28.5 / 8.2 / 33.3 / 24.0. Order Kept > Partly > Broken > Thin holds; T1 sits near Partly.
- cc_180_plus: 21.1 / 30.5 / 17.6 / 1.3 / (none) / 21.0. Kept < Partly (417 rows, interval 15-26); Broken < T2.
- rl_60_180: 58.0 / 53.9 / 47.9 / 25.3 / (none) / 42.9. Order holds.
- rl_180_plus: 36.6 / 43.5 / 19.8 / 1.6 / (none) / 20.4. Kept < Partly (227 rows); Broken = T2.
- LEN T1 (cc_60 33.5, cc_180 32.8, rl_60 61.6, rl_180 40.7) pays like or above Kept/Partly. Same order under LEN. Cure
  has no
  signal at cc_60_180 (0.1-0.3%); rolled and paid_any tell the same story as paid_due.

## Q3 Engagement? Broken minus other, paid_due points, GRR (all rows -> in A2 reachable -> in contacted)
- cc_60_180: vs T0 +20.4 -> +18.8 -> +14.0 (clear). vs T2 +4.5 (clear) -> -0.5 -> +1.2 (gone).
- cc_180_plus: vs T0 +16.3 -> +9.1 -> +7.6 (clear). vs T2 -3.4 (T2 higher) -> -8.1 -> -10.8 (T2 clearly higher).
- rl_60_180: vs T0 +22.6 -> +15.1 -> +14.4 (clear). vs T2 +5.0 (not clear) -> +8.8 (clear) -> +5.8 (not clear).
- rl_180_plus: vs T0 +18.2 -> +8.9 -> +9.7 (clear). vs T2 -0.6 (not clear) -> -2.8 -> -5.7 (not clear).
- Broken vs all Thin, strata (a)-(d): clearly higher in 11/12 (cc_60), 7/10 (cc_180), 11/12 (rl_60), 14 of 31 usable
  (rl_180); clearly lower in 1 (cc_180); the rest overlap. In Dimension B "regular" there is no gap (everyone pays
  60-80%).

## Q4 Point variants: state AUC on paid_due, GRR (LEN); difference vs P0, all "clear" unless noted
- cc_60_180 (P0 0.692 [0.714]): P1 +.030 [+.017]; P2 +.045 [+.026]; P3 -.002 n.s. [-.012]; P4 +.016 [+.002 n.s.].
- cc_180_plus (P0 0.665 [0.690]): P1 +.015 [+.008]; P2 +.032 [+.018]; P3 -.088 [-.069]; P4 -.033 [-.041].
- rl_60_180 (P0 0.643 [0.666]): P1 +.012 [+.003]; P2 +.030 [+.009]; P3 -.018 [-.028]; P4 -.010 n.s. [-.021].
- rl_180_plus (P0 0.736 [0.746]): P1 +.006 [+.003]; P2 +.020 [+.010]; P3 -.092 [-.091]; P4 -.068 [-.071].
- paid_any and not_rolled (61-180) agree in sign. On the points total (not the state) P3/P4 gain everywhere: P4 +.069 /
  +.046 / +.047 / +.033 (GRR). State mix P0 -> P2 (high/mod/low, GRR): cc_60 4.0/21.7/74.3 -> 5.5/30.4/64.1; rl_60
  3.8/26.4/69.8 -> 4.2/33.2/62.6; cc_180 0.0/2.6/97.4 -> 0.1/3.4/96.6; rl_180 0.2/3.6/96.2 -> 0.2/4.1/95.6.

## Q5 Who moves, P2 vs P0 (GRR): rows moved; paid_due of Low -> Moderate movers | stayed Low | stayed Moderate
- cc_60_180: 11.7% of rows; 28.8 | 8.2 | 33.0. Movers 53% non-reachable (stayed Low 72%, stayed Moderate 52%).
- cc_180_plus: 0.8%; 20.2 | 1.4 | 30.4. Movers 32% non-reachable, 42% reachable (stayed Low 5% / 3%, mostly Unknown).
- rl_60_180: 7.6%; 52.9 | 23.1 | 53.8. rl_180_plus: 0.6%; 21.6 | 1.3 | 32.4. P1 movers look the same, fewer rows.
- Movers pay like Moderate (cc_60, rl_60) or between Low and Moderate (180+), and are far more reachable than
  stayed-Low.

## Q6 Stability: P2 minus P0 state AUC per month (03 / 04 / 05), GRR then LEN
- cc_60_180 +.039 +.046 +.049 | +.022 +.028 +.028. cc_180_plus +.034 +.032 +.031 | +.018 +.018 +.018.
- rl_60_180 +.036 +.027 +.028 | +.015 +.010 +.004. rl_180_plus +.018 +.020 +.022 | +.009 +.009 +.010. Positive every
  month.

## Verdicts
**61-180 - (a) credibility or engagement.** Mostly not credibility. The Broken > Thin gap is Broken against T0: accounts
that never made a promise. It shrinks inside reachable and contacted accounts but survives (cc +14 to +19, rl +14 to
+15), so reachability and contact do not explain it; promising at all is a behaviour A2 and the contact flag do not
capture. Against T2 (concluded, nothing kept, not Broken) the gap is +4.5 / +5.0 and disappears inside reachable (cc) or
is not clear (rl): a broken promise carries no more credibility than a single failed one, and T1 (promised, not yet due)
pays as well as Partly. **(b) Best variant.** P2 (Broken +1) on state AUC in both products, clear, under GRR and LEN, in
every month (gains +.045 / +.030 GRR, +.026 / +.009 LEN, smaller under LEN). P1 gets about half the gain. Caution: P2
ties Broken with Partly, yet Partly pays more (cc 32.9 vs 28.5, rl 53.9 vs 47.9), and T2 stays at 0 though it pays like
Broken. P3 and P4 do not help the state (P3 -.018 to -.028 in rl, nil to -.012 in cc; P4 only helps cc GRR, +.016)
although they help the points total clearly. **(c) Split Thin.** Yes as information: T0 (never promised) pays 8-25%
against 24-43% for T2 and 33-62% for T1, so Thin is three populations. As points, T0 -1 is not supported for the state:
T0 rows with regular payments pay 61-82% (Dimension B regular) and would fall to Low. If Thin is split, raise T1 and T2
(+ with Broken), not lower T0. **(d) State mix.** P2 moves 11.7% (cc) and 7.6% (rl) of rows, almost all Low -> Moderate
(cc Low 74.3 -> 64.1%, rl 69.8 -> 62.6%), High +0.4 to 1.5 points. Movers pay like Moderate, not like Low.

**180+ - (a)** Same picture, weaker. Broken vs T0 is +16 / +18 overall and +8 to +10 inside reachable or contacted;
Broken vs T2 is -3.4 (cc, T2 clearly higher) and -0.6 (rl, not clear). Credibility is not separable from engagement: the
only separation is promised or not. **(b)** P2 again best and clear in every month and under both deadlines (cc +.032
GRR / +.018 LEN; rl +.020 / +.010), P1 half of it. But 95% of rows are T0, so P2 moves only 0.8% (cc) and 0.6% (rl) of
rows; Moderate goes 2.6 -> 3.4% (cc) and 3.6 -> 4.1% (rl). Broken pays 17.6 / 19.8% against Partly 30.5 / 43.5%, so
Broken +1 again equals Partly. P3 and P4 cut the state AUC clearly (-.033 to -.092) while lifting the points total
(+.046 cc, +.033 rl); not for the state. **(c)** T0 vs T2 is the split that matters (1.3-1.6% against 20-21% paid_due);
at 180+ no T1 under GRR. Keep T0 at 0. **(d)** Almost no change in the mix.

Not tested, worth a next run: Broken and T2 raised together (T2 pays like Broken), and Broken +1 with Partly +2 so that
the order Kept > Partly > Broken holds; Kept < Partly at 180+ rests on 227-417 rows (wide intervals).
