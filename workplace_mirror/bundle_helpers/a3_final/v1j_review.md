# A3 V1j review (2026-11-15)

Source: `v1j_summary.md` (UAT Sonnet, PROD run for all four model_ids; observation months 2026-03..05, outcomes over
the next 3 months to 2026-08-31). Prompt `sonnet_a3_v1j_promise_points_prompt.md`, retired. P0 re-scored = the shipped
`a3_state` (0 rows differ) in all four, so the variants are measured against the real output.

## 1. What the run settles

- **A promise is evidence beyond contact, but a small one** (Q1). Matched on B, C, DPD, A2 reachability, A4 and loan
  type, Broken beats "talked, never promised" (C1) by +2.9 to +6.1 points paid_due under GRR (clear in all four), +0.8
  to +6.0 under 30 days (clear in two). Half or more of V1i's Broken > Thin gap was contact and reachability.
- **Broken is not one group** (Q2). Broken with money around the promise (BA) pays like Partly at 61–180; Broken with
  nothing (BN) pays like C1 under 30 days. The signal is money moving, not the broken label. But splitting the points
  (P6) ranks below P5 in all four, so the split is a reason code at most, not a points rule.
- **Engagement credit is not reachability showing through** (Q7). Inside S1 (reachable, in country) P5 still beats P0
  clearly in three of four models; only rl_180 (1,892 S1 rows) is flat.
- **P5 is the best order-keeping scheme at 61–180** (Kept 3 / Partly 2 / Broken 1 / T2 1 / T1 1 / T0 0, thresholds
  unchanged): state AUC +.059 cc / +.045 rl over P0 (GRR), positive in every month, DPD level and loan type, and
  High > Moderate > Low holds in every slice. High grows 4.0 → 11.8% (cc 61–180) and the extra rows carry money: High
  + Moderate hold 78% of AED collected against 53% today. P7 (High ≥ 5) loses the gain.

## 2. 180+: P8 vs P5

| model_id | P0 | P5 | P8 (contact +1) |
|---|---|---|---|
| cc_180_plus (GRR / LEN) | .665 / .690 | +.083 / +.058 | +.084 / +.077 |
| rl_180_plus | .736 / .746 | +.047 / +.037 | +.075 / +.072 |

- P8 ranks best at 180+ because 85–95% of its movers are C1: customers we reached who never promised. That is
  reachability, which A2 already scores (Reachable = a contact within W). Contact points in A3 would count the same
  evidence on two axes, against the orthogonality rule.
- **Recommendation: P5 in all four.** It is clear over P0 at 180+ too (+.083 cc, equal to P8 under GRR), keeps the
  axis on promises and payments, and needs one scheme. The hybrid P5 + contact (Sonnet's suggestion) has the same
  double-count and was not tested.

## 3. Side findings

- **P5 makes the deadline almost neutral.** Absolute state AUC under P5, GRR vs 30 days: cc 61–180 .751 / .756, rl
  61–180 .688 / .692, cc 180+ .748 / .748, rl 180+ .783 / .783. With P5, GRR's month end costs at most .005, so the
  deadline can stay GRR's without a ranking argument.
- **Kept < Partly at 180+ is real** (cc -9.4 points, clear) on 417 / 227 rows (0.0–0.3%). P5's Kept 3 > Partly 2 has no
  support there but moves no state. No action.
- **Q0 (follow-up merge, old D-A3-29) was not answered** and is no longer needed: D-A3-29 was rewritten in the council
  tree (one promise stream, an event lives until its deadline or the amount is paid, no 7-day chaining). Its size comes
  from the bundle 25 check (A3-1 block: event kinds, outcomes, events ended early).
- All numbers are on today's events; bundle 25 rewrites them (D-A3-29, D-A3-30, D-A3-31), so the P5 gain is re-read in
  that check, not assumed.
- Snippet defect, cosmetic: the rl_180 DPD slice used `ceil(dpd / 30)` (~100 levels). Not a result.

## 4. Business sentence (verdict (e), Sonnet did not write it)

A customer who made a promise has engaged with repaying: even when the promise was missed, they pay more than equally
reachable customers who never promised. Keeping it is stronger evidence still, so Kept > Partly > Broken > never
promised; we score what the customer said and paid, not whether we could reach them.

## 5. Decision for the user

- Points: P5 in all four (recommended), P5 at 61–180 + P8 at 180+, or keep P0.
- If P5: fold it into bundle 25 (new points, and Thin split into T0 / T1 / T2 so a promiser with nothing concluded earns 1: a small engine change plus spec cases; the check's
  "A3 state moves split by cause" gets a points step) or ship it in the next A3 bundle.
