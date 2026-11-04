# A3 V1–V4: Claude's review (2026-11-04)

Source: `v1_v4_summary_60_180.md` (cc_60_180 19,292 accounts, rl_60_180 3,985, latest month 2026-08).
180+ not run. RL V2 N1 / N2 / N4, the candidate overlap and the latest-contact stats failed (Java heap).

## V1: commitments

- **The anchor works as intended.** The new counts equal `dcore_feat_*` on 99–100% of agreements when
  there is no anchor cut. The differences (CC 16%, RL 7.5% of agreements) are all instalments from
  before the current delinquency. Commitments become Thin more often: CC Thin 14,648 → 16,300 of
  19,292 (84%). Dimension A says nothing for most accounts, so its thresholds hardly matter (V4).
- **DCORE vs ledger.** The prompt's ledger test is flawed, and the flaw is mine. It summed card payments
  from the plan start to each due date and compared the sum with that one instalment's amount, so a
  later instalment counts as "kept" from earlier instalments' money. That inflates ledger-kept for
  multi-instalment plans, which is the likely cause of the CC settlement result (no relation,
  V 0.06; 68.6% of DCORE-overdue "kept"). What can still be read:
  - CC PTP: DCORE `overdue` is never ledger-kept by the due date (0%), so a DCORE "broken" holds.
  - CC PTP: DCORE `paid` is confirmed in 52% of cases by the due date and 69% at +5 days. A "kept"
    from DCORE is only partly backed by money.
  - RL PTP agrees 78% overall and 87% in the last 3 months; DCORE `paid` is ledger-kept in 94%.
  - Settlement cannot be judged from this run.
- **Snapshot statuses.** `B` / `F` statuses appear on instalments due after the observation date, so the
  statuses are current values, not values as of the observation date. That is harmless for the
  latest-month score, but on history months DCORE's status looks ahead. A ledger-based kept / broken
  has no such look-ahead.
- `payment_amount` is NULL on 55–72% of instalments, so DCORE's own amounts cannot replace the ledger.
- Fix needed before deciding D-A3-11: allocate payments to the plan's instalments in due-date order
  (an instalment is kept when cumulative payments since the plan start reach the cumulative due up to
  and including it). Rerun V1c only, CC and RL, PTP and settlement.

## V2: strong negatives

| Candidate | Fires (CC / RL) | In A2 non-reachable (CC / RL) | Reading |
|---|---|---|---|
| Explicit refusal | 4.4% / 4.4% | 57% / 34% | Adds stated intent and moves 623 / 123 rows. Passes the test. |
| Dispute | 0.3% / 0 | 45% | Too rare to matter. Diagnostic at most. |
| N0, today's no-response | 36% / 26% | 84% / 78% | Re-derives A2: the top names are dead-line outcomes. Fails test 3. |
| N1, no pickup | 7.6% | 70% | Mostly A2 again; A2's failed set includes ringing. |
| N2, no pickup after a contact | 4.3% | 66% | 77% of it is N1. Still mostly A2. |
| N4, hang-up | 2.0% | 76% | Mostly A2. |

- Today's negatives, N0 above all, change 37% of CC states and 20% of RL. Dropping N0 is the largest
  single change in this redesign: rows move up from Low.
- No avoidance variant gets below about two thirds overlap with A2 Non-Reachable. Any
  "doesn't answer" signal is largely A2's fact.
- Right-party fix (O80): 0 rows change on CC. The two names may not occur in the follow-up table at all.

## V3: overlap with the other axes

- Dimension C against A4 (V 0.58 CC):
  - `no_record` is A4's early payment default almost exactly (1,439 of 1,440 CC), since an early
    defaulter has no record by definition. Harmless, but not new information.
  - Clean / not clean still splits the large A4 states: seasoned straight roller 7,199 / 862, slow roller
    2,195 / 699.
- Dimension B against A4 (V 0.62): `regular` is mostly A4 `stabilized` (1,100 of 1,273 CC). Some / none
  splits slow rollers and seasoned accounts.
- A3 against A1: independent (V 0.10 / 0.12). A3 against A2: partly linked (V 0.22 CC), most likely
  through N0.
- Reading: B and C overlap A4, as they must, because payments drive the DPD path. They still add
  inside A4's big states. Keep both, and report the overlap in the axis report.

## V4: sensitivity

- Only the Moderate cut-off really matters: Moderate from 2 points instead of 1 moves 19% (CC) / 29%
  (RL) of rows. High from 3 / 5 moves 2–6%, the clean share 2–4%, everything else ≤ 1.5%.
- The Broken rule's hard-coded `>= 2` (O75) is confirmed: the "concluded needed" variants cannot move it.

## Questions this opens (asked one at a time)

1. No response / avoidance: drop N0; keep N1 / N2 / N4 out of the state (diagnostic columns only)?
2. Explicit refusal: keep as the strong negative, with the narrow list; dispute as a diagnostic only?
3. Rerun V1c with the corrected allocation before deciding D-A3-11 and the Broken question?
4. Moderate from 1 point (today) or 2: one piece of positive evidence (e.g. a clean record alone, or
   some payment alone) gives Moderate today.
5. High only reachable with DCORE commitments (High from 3 moves 4.7% CC).
6. Keep Dimensions B and C despite the A4 overlap (recommended).

## V1c: corrected ledger (2026-11-04, `v1c_summary_60_180.md`)

- **The numbers hold together.** The handoff flagged three possible inconsistencies; all reconcile:
  - CC PTP: 85.8% overdue and not kept + 7.4% paid and kept = 93.2% agreement. `paid` is then 14.2% of
    instalments, 52% of it kept: consistent.
  - CC settlement: 6,311 overdue (almost none kept) = 51.9%, plus 22.1% of the 5,840 `paid` = 10.6%:
    62.5% agreement. Consistent.
  - RL 84.0% vs 85.9%: different scopes (all vs last 3 months), not a conflict.
- **PTP is always a single instalment**, so the fix changed nothing there; settlements are 4+ instalment
  plans and move (CC V 0.06 → 0.36–0.48).
- **CC: the disagreement is one-sided.** DCORE `overdue` is never ledger-kept, so a DCORE broken is
  true. DCORE `paid` is backed by card payments in 52% (PTP) and 22% (settlement) at the due date,
  69% / 35% with 5 days. DCORE status overstates kept, most of all for settlements.
- **RL:** `paid` is backed 94% (PTP) / 53% (settlement). 24.6% of PTP `overdue` is ledger-kept, which
  month-level `total_paid` cannot split into late payment and DCORE error. RL PTP status adds no
  accuracy over the base rate on all concluded instalments.
- **Risk in judging by the ledger: CC settlement.** 78% of DCORE-paid settlement instalments have no
  matching card payment. Either DCORE marks them paid too early, or the money reaches the bank in a way
  `crx_cc_transactions` does not show as a payment. Candidates: waiver or adjustment credits, another
  `txn_category`, or O87 (`.distinct()` collapses identical same-day payments). If it is the second,
  the ledger would mark real payers as broken. The bundle check should split those instalments by the
  card's balance movement and by non-payment credits.
- **Section 4 (level DCORE vs ledger) failed again** (driver plan growth). How often Broken fires under
  the ledger is still unmeasured; the bundle check gives it directly from the new output.
- `HISTORICAL PROMISE TO PAY` never occurs; `RETAIN PTP` 26 agreements per model; `EOSB_PTP_DOCUMENTS`
  immaterial. The PTP name sets need no change.
