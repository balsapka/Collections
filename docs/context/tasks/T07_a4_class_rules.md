# T07 — A4 deterioration class v1

**Track A** · **Depends:** T04, T05, T06 · **PROD round trip:** Yes

**Goal.** Collapse the A4 feature set into a small set of interpretable classes:
`abrupt_shock`, `gradual_spiral`, `chronic_marginal`, `mixed`.

**Why.** The features are the substance, but the *class* is what a person can act on
and what the persona grid uses. A customer whose income stopped abruptly may be solvent
and recoverable if located; one who spiralled into over-indebtedness is structurally
insolvent. Both look identical at 180+ DPD — the class is what tells them apart.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §3.5` (rules and thresholds). Outputs of
T04–T06.

## Steps

1. Implement the ordered rules in `§3.5`; first match wins; emit
   `det_class_confidence` = matched conditions / listed conditions.
2. Thresholds (`τ_u`, `τ_p`, `τ_m`, tercile cuts) are **placeholders** — tune them on the
   data actually available after T02's per-family window decision, and log the values chosen.
3. **Dormancy check on `abrupt_shock`.** Cross-tab the class against `months_at_code0_w12`
   (§2's code-`0`/code-`1` signal). The zero-payment condition may be firing on accounts
   where *nothing was due* — paid-ahead or dormant — rather than on income stopping. If the
   class is enriched for code-`0` months, the not-dormant guard is required.
4. **Chronicity check on `chronic_marginal`.** Two of its three original conditions saw only
   the ~12-month window. Confirm the recruited duration features (`prior_spell_cnt_24m`,
   `months_since_prior_spell`, `tenure_at_t0_m`) and the `w_pre_clean_m ≥ τ_m` floor are
   actually separating it from `gradual_spiral` — specifically, check whether accounts moving
   between the two classes under threshold changes are plateaued spirals (`§3.5 ⚠`).
5. **Face validity (distinct from T08's outcome separation).** Do the classes mean what their
   *names* claim? `abrupt_shock` → low prior spells, longer clean tenure; `gradual_spiral` →
   rising `fee_velocity_ratio_h2`; `chronic_marginal` → high `prior_spell_cnt_24m`. Report the
   crosstab.
6. Report class shares per segment. Iterate thresholds if `mixed` dominates.

## Decision rule

- `mixed` > ~50% of volume → the rules are not discriminating; iterate before moving
  to the gates. Consider whether a threshold is mis-scaled or a required feature has
  poor coverage.
- Any class < ~5% of volume → consider merging it; the grid must stay small.
- **`abrupt_shock` enriched for code-`0` months** → add the not-dormant guard and re-run.
- **Face validity fails for a class** → do not proceed to the gates on that class. Either
  recruit a feature that evidences the name, or **rename the class**. A class can pass PV3
  and PV4 while being misnamed, and the gates will not catch it (`personas.md §5`).

## Standing naming check

For each class: state what the name claims, then name the feature that evidences the claim.
Where there is no such feature, recruit one or rename. Two of the four failed this on
inspection — `abrupt_shock` implies a diagnosed cause the trajectory cannot supply, and
`chronic_marginal` implied a duration the window could not see.

## Done when

Class assigned for the CC delinquent population with confidence; class shares per
segment, chosen thresholds, the dormancy crosstab and the face-validity crosstab logged in
`RESULTS.md`; output schema as in `§3.5` including `w_pre_clean_m` and
`w_pre_contaminated_flag`.
