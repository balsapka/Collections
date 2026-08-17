# T04 — Succession link: heuristic matching

**Goal.** Infer the old→new account link where it is not explicitly recorded, with a
measured confidence.

**Precondition.** T03 found no usable explicit link (or only partial coverage). If T03
found a good one, this task is `n/a`.

**Load.** `reference/feature_specs.md §6` (steps 3–4).

## Steps

1. Generate candidate pairs: same CIF, same account-type family,
   `open_date(new) − close_date(old)` within `<<window, default 0–45d>>`.
2. Score each pair on balance correspondence
   (`|initial_principal(new) − closing_balance(old)|` relative to closing balance — the
   tightest single signal), date proximity, product-transition plausibility, and any
   restructure-flavoured posting or DCORE event near the closure.
3. Resolve to at most one successor per predecessor and vice versa: greedy on score
   with a minimum threshold. **Leave ambiguous cases unlinked rather than guessing.**
4. Validate: against T03's partial-coverage subset if one exists, else hand-validate a
   sample and label the result as such.
5. Emit `(old_account_id, new_account_id, link_method, link_confidence, close_date,
   open_date, balance_delta)`.

## Consumer contract

Confidence is used asymmetrically — state this in the table's documentation:
- **Label exclusion: conservative.** Exclude on weak links too (a false exclusion
  costs a row; a missed one inverts a label).
- **A4 history inheritance: strict.** Inherit only on strong links (wrong history is
  worse than no history).

## Done when

Succession table built; precision/recall (or sampled agreement, labelled as such)
logged in `RESULTS.md`; link-rate over the T02 restructure population reported; if
linkage proves infeasible, that is recorded as an accepted limitation with its size.
