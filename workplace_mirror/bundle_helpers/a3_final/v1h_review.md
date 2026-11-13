# A3 V1h review (2026-11-13)

Source: `v1h_summary.md` (UAT Sonnet, PROD run for all four model_ids; observation months 2026-03..05, outcomes over the
next 3 months to 2026-08-31). Prompt `sonnet_a3_v1h_deadline_backtest_prompt.md`, retired.

## 1. Deadline (D-A3-28 vs bundle 20 vs 30 days)

| model_id | paid_due AUC B20 / GRR / LEN | read |
|---|---|---|
| cc_60_180 | .692 (= GRR) / .692 / .714 | 30 days +.022, clear, every month |
| rl_60_180 | .666 / .643 / .666 | GRR month end -.023, clear; LEN = B20 |
| cc_180_plus | .670 / .665 / .690 | LEN best, GRR worst |
| rl_180_plus | .746 / .736 / .746 | GRR -.010, clear |

- The order is the same in all three observation months and on paid_any and not_rolled.
- **GRR's month end ranks worst for loans and at 180+.** The rows it demotes pay like the state they came from:
  - RL 61–180 Moderate → Low: 48.6% paid_due, against 52.6% for rows that stayed Moderate and 23.9% for rows that
    stayed Low.
  - Promises paid only in the following month are followed by the same account payment rate as promises paid by the
    month end (RL 61–180: 57.7 vs 57.5%; unpaid: 45.9%).
  - The stricter deadline turns payers into "broken".
- **30 days ranks best everywhere.** It equals or beats every other deadline, for cards (+.02) and loans (level with
  B20).
- **Cure has no signal at cards 61–180** (AUC .49, cure 0.2%). The outcome's "back to current" is too strict for cards
  in this segment; read paid and not_rolled. "Exited" (25–43% at cc 61–180) is mostly rolling past 180, which leaves the
  60_180 base.

## 2. Unknown → Low (D-A3-27)

- **ex_unknown is never better than the other Low rows:** paid_due -8.4 / -18.9 / -7.1 / -3.7 pt (cc61, rl61, cc180,
  rl180), all clear. By the agreed test it belongs in Low, not in a better state.
- **But Low is no longer one population.** ex_unknown is the weakest group, and it is most of Low at 180+ (83% of cc,
  65% of rl rows).
- **What it is:**
  - cc 61–180 (12.2%): 71% are accounts on book under 6 months (EPD-like), about 25% are old idle cards with no bill.
  - rl 61–180: all young loans.
  - 180+: censored episodes and long charged-off accounts.
- **The user's ~7% EPD at cc 61–180 is consistent:** 71% of the 12.2% is about 8.7% of rows, on an account-month
  basis.

## 3. Found in passing

- **Dimension A ladder:** Thin (no concluded promise) pays less than Broken (cc61 11.6 vs 28.5%; rl61 27.7 vs 40.5%).
  Points have Broken -1 < Thin 0 (D-A3-23); the data put Broken above Thin. A promise, even broken, is engagement.
- **States vs points:** the points total ranks far better than the three-rung state at 180+ (paid_due .82 / .86 vs .67
  / .75). 96–97% of 180+ rows sit in Low, so the 180+ thresholds lose most of the information.

## 4. Decisions for the user (open)

1. **Deadline before bundle 23 step 8.** The options:
   - (a) run step 8 with GRR's rule and take the evidence to GRR;
   - (b) revert loans to bundle 20's next month end;
   - (c) 30 days for all (best everywhere).

   (b) and (c) are a new bundle (one constant: `PROMISE_DEADLINE`; the `30_days` options are built in). Earlier
   decision (2026-11-09): ship GRR's logic, 30 days maybe after GRR.
2. **ex_unknown:** keep it in Low (the test passes). Optionally expose a `no_record` flag or sub-label so strategy can
   tell it apart.
3. Later, with GRR: Broken vs Thin points; 180+ thresholds (or points instead of three rungs at 180+).

Workplace: `tmp_validation/a3_v1h/` can be deleted.
