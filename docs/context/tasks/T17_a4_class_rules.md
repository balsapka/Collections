# T17 — A4 deterioration class v1

**Goal.** Collapse the A4 feature set into a small set of interpretable classes:
`abrupt_shock`, `gradual_spiral`, `chronic_marginal`, `mixed`.

**Why.** The features are the substance, but the *class* is what a person can act on
and what the persona grid uses. A customer whose income stopped abruptly may be solvent
and recoverable if located; one who spiralled into over-indebtedness is structurally
insolvent. Both look identical at 180+ DPD — the class is what tells them apart.

**Load.** `reference/feature_specs.md §3.5` (rules and thresholds). Outputs of
T14–T16.

## Steps

1. Implement the ordered rules in `§3.5`; first match wins; emit
   `det_class_confidence` = matched conditions / listed conditions.
2. Thresholds (`τ_u`, `τ_p`, tercile cuts) are **placeholders** — tune them on the data
   actually available after T05's window decision, and log the values chosen.
3. Report class shares per segment.
4. Iterate the thresholds if `mixed` dominates.

## Decision rule

- `mixed` > ~50% of volume → the rules are not discriminating; iterate before moving
  to the gates. Consider whether a threshold is mis-scaled or a required feature has
  poor coverage.
- Any class < ~5% of volume → consider merging it; the grid must stay small.

## Done when

Class assigned for the CC delinquent population with confidence; class shares per
segment and the chosen thresholds logged in `RESULTS.md`; output schema
`(account_id, spell_id, t0, <features>, det_class_v1, det_class_confidence,
computed_at)` as in `§3.5`.
