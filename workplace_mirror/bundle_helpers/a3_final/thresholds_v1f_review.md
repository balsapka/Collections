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

## 3. V1g: GRR's next-statement deadline (G) vs a fixed 30 days (F) (handoff 54, `v1g_summary_60_180.md`)

60_180 only; 180+ was not run (the snippet takes the model_id from globals, so it is a re-run).

- **F beats G on almost everything.**
  - State AUC (non-roll vs roll): F 0.740 / 0.588 (CC / RL), G 0.714 / 0.578.
  - Ladder AUC with Thin third: F 0.624 / 0.548, G 0.550 / 0.521.
  - Coverage: G is slightly ahead (29.2 vs 28.3% CC, 26.3 vs 23.6% RL), but F moves as many accounts
    out of Thin (7.8 vs 7.5%, 9.3 vs 8.8%).
- **G's bias is confirmed.** Of CC promises made 7 days or less before a statement, 15.1% are paid by
  it and another 22.1% in the next cycle, so G calls them broken (F: 37.2% paid). Beyond 7 days
  the two read alike (G 34–37%, F 39–44%). G-paid is almost a subset of F-paid.
- **Against bundle 17, F raises the state AUC** by 0.054 (CC, 0.686 → 0.740) and 0.023 (RL, 0.565
  → 0.588). CC Kept is less pure (roll 62% vs bundle 17's 28%, but bundle 17's Kept is 1.1% of
  accounts); RL Kept is purer under the events (61% vs 65%). With Thin last, the ladders tie on CC
  (0.713 vs 0.701).
- **Overlap with B:** under G, every recent paid event is a B cycle (same rule, same money); under F,
  93.5% (CC) / 76% (RL). Kept with no B payment: 0.6–0.7% under F. 68–76% of paid events are older
  than B's window under both, where A adds its own information.
- **Settlement plans:** instalments paid 33% (G) vs 54% (F) on CC; plans fully paid 12% vs 21%.
- **Points confirm D-A3-24.** Roll share by points total on the baseline: CC 95.0 / 90.6 / 73.8 / 62.9
  / 33.5% (0 / 1 / 2 / 3 / 4+), RL 86.4 / 72.5 / 68.8 / 59.2 / 58.2%. On CC, 1 point rolls like 0
  points; the step is at 2. Refusal on rolls more (CC 92.7 vs 86.6%, RL 84.7 vs 75.2%).
- **Points below 0 (Broken, no B or C) roll less than 0 points** (CC 87.4 vs 95.0%), and Thin is the
  worst-rolling level everywhere. Under Moderate from 2 this changes no state (both are Low); it
  matters only for Broken with B + C = 2 (Low at −1, Moderate at 0). For later, not this bundle.
- **Caveats.**
  - 39.7% of CC accounts (6,314) have no level 3 months later (they left 60–180, cured or rolled past
    180). They are left out of every AUC, the same rows in each variant, so the comparison between
    variants is fair, but the absolute roll rates are not the whole population.
  - No intervals; the RL gaps (0.01–0.03 on ~3,100 accounts) may be noise.
  - **Day-level RL repayments exist** (`ec_account_loan_transaction.la_txn_dt` + amounts,
    `sa_account_loan_dmd`), which would fix RL's month-level cash for A3 as a whole (Dimension B
    too). Needs an EDA and a primary (`prm_loan_payments`), per the spec's open item.

**Reading:** at 60–180, Dimension A = GRR's promise events judged on a 30-day deadline is better
than both G and bundle 17's instalment rule. A middle way for GRR's cycle framing, untested: the next
statement, or the one after when the promise is 7 days or less before it (its paid rates come out
like F's for those promises and like G's for the rest). 180+ needs the re-run before shipping.
