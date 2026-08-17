# T09 — CASA-holder vs card-only performance split

**Goal.** Measure how much better the current model performs where ability signal is
directly observable, to decide whether estimating ability for everyone else is worth
building.

**Why.** `CASA inflow/outflow` and `bureau total salary` are the only non-tautological
features in the current top set — but they cover a minority of the book (only ~10–20%
of delinquent CC customers hold another product; CASA coverage is partial). Split-based
GBM importance can overweight a high-variance feature in a subpopulation, so their
ranking may be an artefact. The performance gap between the two groups is the honest
measure, and it is the business case for the A1 ability proxy.

**Load.** `reference/domain_and_decisions.md §4`.

## Steps

1. Split the scored population into CASA-holders (and/or multi-product) vs card-only.
2. Report capture@10% (accounts and AED), PR-AUC against each group's own base rate,
   and precision@bottom-decile for each group separately.
3. Report each group's share of accounts and of total recoverable AED, so the gap can
   be weighed by how much of the book it applies to.
4. Optional if cheap: refit without the CASA/bureau features and measure the drop on
   the CASA-holder group — isolates the ability contribution from group composition.

## Decision rule

- **Material gap** → the ability signal is real. A1 (estimating ability for the ~80%
  card-only population) is justified; record the gap as its expected ceiling.
- **Gap ≈ 0** → the importance ranking was largely an artefact. **Deprioritise A1** and
  keep the ability axis out of the near-term persona set.

## Done when

Per-group metrics, group shares, and the A1 go/no-go conclusion are logged in
`RESULTS.md`, and the A1 gate is marked accordingly in `TASKS.md`.
