# Bundle 23 check: Claude's review (2026-11-12)

Source: `b23_check_results.md` (all four model_ids, month 2026-08). b20 = the persisted bundle 20
output; old = the Unknown rule (D-A3-27); new = old + GRR's month-end deadline (D-A3-28).

## Verdict

Both steps behave as designed; no bug. The Unknown rule empties Unknown everywhere. GRR's deadline
leaves cards at 61–180 untouched and makes loans clearly stricter: 7.2% of RL 61–180 states move,
almost all down. The check carries no outcomes, so it cannot say whether the stricter deadline ranks
customers better; V1g's earlier evidence pointed the other way (the more lenient 30 days ranked best).

## Unknown rule (b20 -> old)

- Every Unknown row becomes Low: CC 61–180 11.5% (2,228), RL 61–180 6.6% (263), CC 180+ 81.4%
  (259,503), RL 180+ 63.5% (35,142). No row is left without an episode, so Unknown is now empty.
- Low becomes the bulk at 180+: CC 97.2%, RL 95.4%. High + Moderate stay 2.8% / 4.6%.
- The few other moves (CC 61–180: 3 rows, CC 180+: 5) are not the rule: see "Ties" below.

## Deadline (old -> new)

- **CC 61–180:** 2 rows and 1 event change, all ties (below); outcomes and levels are identical.
- **RL 61–180:** 287 states change (7.2%): High 4.9 -> 3.2%, Moderate 27.9 -> 24.6%, Low 67.2 ->
  72.2%. Paid events fall from 70.5% to 46.8% (388 paid -> none, 294 paid -> partial); accounts with
  a kept promise 991 -> 818; Kept level 9.7 -> 4.8%, Broken 3.6 -> 8.6%. The flips are spread over
  the month (21–31: 39.5% of flips vs 37.8% of events), so it is not promises made late in the
  month: about a quarter of loan promises are paid only the following month.
- **CC 180+:** 0.4% of states (1,127); paid 20.3 -> 16.3%; 1,654 more events conclude (the month end
  comes before the next statement or the 31-day fallback). Flips lean to promises made on the 21st
  or later (54% vs 51%). High 222 -> 159.
- **RL 180+:** 0.5% (274); paid 47.2 -> 34.5%.

## Ties (low)

CC 61–180 moves 2 states with identical Dimension A levels, and b20 vs old moves 3 CC 61–180 and 5
CC 180+ rows the Unknown rule cannot explain. Same cause as the 1-row note in the bundle 20 review:
a latest-row pick without a full tie-break (contacts / payment rows) gives a different row on each
evaluation. About 0.01% of rows; a deterministic tie-break would fix it in a later bundle.

## Open

- Whether GRR's deadline ranks better than bundle 20's: an outcome test (roll / cure over the next
  3 months by state, old vs new) would answer it before step 8, if wanted.
- 180+ is now almost all Low by construction; the persona at 180+ rests on the few High / Moderate.
