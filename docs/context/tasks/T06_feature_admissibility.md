# T06 — Feature admissibility: block codes & bureau salary

**Goal.** Determine whether two high-importance features in the current models are
admissible as-is.

**Why.** Both are among the current top features, and both have a specific defect
risk. Leakage discipline is already in place across the modelling spectrum (R2), so
this is a check on two known-awkward cases rather than a general audit.

**Load.** `reference/current_state.md §3`.

## Card block codes

1. When does the block event fire relative to `observation_date`? Compare timestamps.
2. Is blocking a DPD-triggered operational action (i.e. does it record our own
   decision rather than customer behaviour)?

**Decision rule.** Any block timestamps after the observation date → **leakage in the
existing system. Report it, do not fix it** (R19): log it under "Defects found in
existing system" in `RESULTS.md` with its impact, and let the user decide on the repair
separately. For this programme's own work, exclude the feature. Purely DPD-triggered
with no independent information → it is a state restatement (consistent with T01),
usable but not signal.

## Bureau salary field

1. What pull date sits behind `bureau total salary last 6m` for each row?
2. Is the freshness consistent, or do some accounts carry newer pulls than others?
   (AECB pulls stop firing once a customer is delinquent, so most should be pre-T0.)

**Decision rule.** Consistent pre-delinquency staleness → acceptable as a *historical*
ability signal; document it as such so nobody reads it as current income. Inconsistent
freshness → recompute from the **last pre-T0 pull only**, so the feature means the same
thing on every row.

## Done when

Findings logged in `RESULTS.md` — under "Diagnostics" for the measurement, and under
"Defects found in existing system" for anything wrong with the running models. Note
which existing models would be affected *if* the user chooses to fix, but do not make
that change here (R19).
