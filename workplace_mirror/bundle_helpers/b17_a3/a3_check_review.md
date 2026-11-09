# A3 bundle 17 check: Claude's review (2026-11-09)

Source: `a3_check_results_60_180.md` (cc_60_180 19,292 rows, rl_60_180 3,985, month 2026-08). The
check ran cleanly on both products (15/15 tasks, 226 s / 351 s).

## Data note

The summary's first table (CC payments low 3,920 / moderate 12,729; dcore 3,893 / 12,377) disagrees
with three other tables by 2 and 4 rows. The old × new marginals, the dcore × payments marginals and
the v2_minus1 rows all give payments 3,918 / 12,731 and dcore 3,889 / 12,381; that table is not one
the check logs, so the Sonnet derived it. The numbers below use 3,918 / 12,731.

## 1. The new A3 against the old one

- **About half of CC rows and a quarter of RL rows change state** (payments judge: 8,778 = 45.5% CC,
  1,089 = 27.3% RL). As designed, almost all of it comes from no-response leaving the state:
  - old `no_response` rows: CC 6,937 (36.0%), RL 1,051 (26.4%), the V2 rates (36% / 26%);
  - Low → Moderate: CC 6,105 (31.6%), RL 713 (17.9%);
  - Low → Unknown: CC 1,691 (8.8%), RL 176 (4.4%). These are rows whose only evidence was the
    no-response rule; with it gone they have none.
  - Moderate → Low: CC 454 (2.4%), RL 131 (3.3%): Broken now −1, the 100 AED floor, the episode
    windows.
- **New distribution (payments judge):** CC High 1.3%, Moderate 66.0%, Low 20.3%, Unknown 12.4%; RL
  1.6% / 66.4% / 25.2% / 6.9%.

## 2. The judge: DCORE vs payments

- **At state level the two judges agree on 96.2% of CC rows and 97.2% of RL rows.**
- **Dimension A level:** they agree on 93.0% (CC) / 93.5% (RL), but most rows are Thin under both.
  Among rows with promise evidence under either judge, they agree on 60% (CC) / 41% (RL).
- **CC: DCORE credits twice as many kept instalments.** Concluded / kept: DCORE 17,841 / 6,910
  (38.7%), payments 16,610 / 3,250 (19.6%). This is V1d's finding (DCORE 'paid' premature for PTPs,
  late for settlements). Effect on the state: High 653 (DCORE) vs 255 (payments): 427 CC rows are High
  only because DCORE calls their instalments paid.
- **RL goes the other way.** DCORE 1,210 / 291 (24.0%), payments 1,074 / 578 (53.8%). The loan's monthly
  total paid, with the grace month, keeps more than DCORE does (V1c: 24.6% of RL PTP 'overdue' were
  covered by the month's cash). RL High: payments 62, DCORE 24.
- **The cascade shows, mildly.** On CC, 509 accounts kept / partly kept under DCORE are Broken under
  payments (256 + 253). Broken accounts: payments 2,197 (11.4%) vs DCORE 1,855 (9.6%), so +342 rows
  (1.8% of CC). Most of these are settlement plans where one missed instalment carries into the next
  (V1d cascade addendum).

## 3. Broken: how much it weighs

- **"Broken but still pays" is not small on CC.** Broken accounts with B + C ≥ 2 points (regular
  payments, or some payment plus a clean record): payments 1,115 (5.8% of CC, 51% of Broken), DCORE 748
  (3.9%). RL: 29 / 66 (0.7% / 1.7%).
- **The weight moves CC Low by up to 9 points** (payments judge): today's override 26.0%, −2 23.7%,
  **−1 20.3%**, 0 16.8%. RL barely moves: 24.5–25.9%.
- **The v2_minus1 variant reproduces the real state exactly**, so the −1 in the Scorecard works as
  designed.

## 4. Refusal and the diagnostics

- **Refusal fires on 857 CC (4.4%) and 185 RL (4.6%)**, the V2 rate (4.4%). The latest right-party
  contact is a refusal for 908 / 206; 51 / 21 of those are cleared by a plan or a payment of 100 AED or
  more afterwards.
- **The 24-month DCORE cap removes nothing** (857 / 185 with and without it). Q-30 (b) holds: keep the cap.
- **The old and new refusal flags overlap only partly** (CC): 607 rows are refusal in both. 490 old
  refusals are cleared now (the narrowed list; a later plan or payment). 250 new refusals were another
  reason before (123 broken, 30 no-response) or nothing (97).
- **Diagnostics:**
  - no pickup after contact: CC 1,344 (7.0%), RL 329 (8.3%);
  - hung up last: 443 (2.3%) / 41 (1.0%);
  - dispute: 74 (0.4%) / 0, as in V2.

## 5. Episode and coverage

- **Every row has an episode anchor** (no `no_episode`). Censored anchors: 5 CC rows.
- **History floor (D-A3-10):** 26 CC rows read No record with the record window starting before
  2024-01. That's negligible, so keep the floor.
- **Dimension C:** Clean CC 64.3%, RL 44.3%; No record 15.6% / 11.1%.
- **Dimension B:** None CC 74.9%, RL 56.7%; Some 17.6% / 32.4%; Regular 7.5% / 10.9%.

## Reading

- **The redesign behaves as designed.** The big moves are the decided ones (no-response out, Broken
  −1), and every coverage number is clean.
- **Judge: payments (option B).** On cards it removes the 427 Highs that rest only on DCORE's premature
  'paid'; on loans it credits money DCORE marks overdue. The state differs from DCORE on only 3–4% of
  rows. The cascade adds 1.8% Broken on CC; an own-amount rule would soften that, but it isn't needed
  to ship.
- **Broken weight: −1.** On CC, the group it decides (Broken but paying) is 5.8% of rows, so the
  choice matters. −1 sits between the override (26.0% Low) and 0 (16.8%). V1e's outcome part (what
  these customers paid and how they rolled next) is the remaining evidence if GRR asks.
