# A3: threshold what-if and V1f, Claude's review (2026-11-09)

Sources: `threshold_whatif_summary_60_180.md` (handoff 52) and `v1f_summary_60_180.md` (handoff 53),
both cc_60_180 / rl_60_180, month 2026-08. 180+ not run.

## 1. Thresholds (Moderate from 1 or 2, High from 4 or 3)

- **Today's setting is reproduced on every row**, so the what-if is exact.
- **Moderate from 2 is one group's decision.** It moves 9,940 CC (51.5%) / 1,689 RL (42.4%) from
  Moderate to Low, all at exactly 1 point. Of the CC movers, 85% (8,436) made no promise and paid
  nothing while delinquent: a clean pre-delinquency record is their only evidence. RL: 60% that group,
  32% one payment with a not-clean record.
- **Distribution:** M1H4 CC 1.3 / 66.0 / 20.3 / 12.4 (High / Moderate / Low / Unknown), M2H4 1.3 /
  14.5 / 71.8 / 12.4; RL 1.6 / 66.4 / 25.2 / 6.9 vs 1.6 / 24.0 / 67.6 / 6.9.
- **Outcome evidence (V1f Q8, by commitments level):** accounts with no promise evidence (Thin) roll
  the most over the next 3 months, CC 93.5% (Broken 78.4%, Kept 46.6%), RL 78.3%. The M2 movers are
  mostly Thin with no payment, so M1 calls the group that rolls most Moderate on the strength of the
  pre-delinquency record alone. This supports Moderate from 2. Not tested directly: roll rates by
  points total.
- **High from 3** adds 446 CC (2.3 pt) / 259 RL (6.5 pt) to High, about half of them regular payers
  while delinquent with no promises. No outcome evidence for them; stays a GRR calibration lever.

## 2. V1f: GRR's Dimension A (promise events judged by a sufficient payment)

- **Coverage.** Follow-up promise events put 33.5% CC / 26.9% RL of accounts under promise evidence,
  against 23.3% / 14.0% with a concluded instalment today. The gain comes only from follow-up-only
  events (11,209 of 18,751 CC events); table events alone move 0.7–0.8% of accounts out of Thin.
- **Consolidation works.** ±7 days is enough (30 days changes matched 3,836 → 4,226 and the accounts
  with an event not at all). Re-affirmations add nothing. Post-dated cheques never occur.
  `SETTLEMENT` as a name is mostly not a plan (538 of 4,429 CC events match a record).
- **The payment reading is not reliable as specified.** The CC paid rate follows the grace window's
  length (15% paid at ≤ 7 days to the next statement, 43% at 15–30 days); RL's comes mostly from the
  same month's cash (59–67% vs 34–38% counting later months only). A fixed window from the event day
  (e.g. 30 days) is needed. Table PTPs carry no promised date (first instalment due = event day).
- **Follow-up-only promises are not worse than table plans** (CC 38.6% paid vs matched 23.9%; RL 60.4
  vs 59.5%), so they look like real promises the tables miss. DCORE's own outcome names agree with
  the payment reading (84–86% paid with one, 17% / 50% without).
- **Bucket movement adds nothing independent at 60–180** (paid events never roll; it is the same
  payment). 180+ untested.
- **Overlap with Dimension B is as the user framed it.** Every recent CC paid event is a B qualifying
  cycle (RL 77%); A's own information is in the 70% of paid events older than B's window. A and B
  disagree on few accounts: Kept with no B payment 0.2–0.7%, Broken with regular B 0.4–2.0%.
- **Ranking is weak and not monotone** for both versions: Thin rolls more than Broken. Ordered Kept >
  Partly > Broken > Thin, AUC CC 0.73 (new) vs 0.72 (bundle 17), RL 0.56 vs 0.52.
- **Run caveats:** refusal demotion off in every V1f state column; the persisted commitments level was
  read for only 78 CC accounts (that comparison is void; RL agrees with the recomputed level on
  90.8%). Neither changes the reading above.

## Reading

- Thresholds: the facts favour Moderate from 2, High from 4.
- Dimension A: GRR's version is promising for coverage but needs a fixed window and a 180+ run before
  it can replace bundle 17's instalment rule. Shipping bundle 17's rule now and GRR's as the next
  version (a V1g with the fixes) keeps the A3 output moving.
