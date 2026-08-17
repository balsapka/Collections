# T16 — A4: departure signature & history shape

**Goal.** Assemble the departure/travel signals and the long-horizon history features —
**reusing the existing retail features rather than rebuilding them.**

**Why.** Departure is a distinct failure mode: a customer who left the country is
unreachable regardless of willingness or ability, and no amount of collections effort
changes that. Ready-made departure-flavoured features already exist from internal
retail use cases built on CASA and product-holdings data — those should carry this
group, with card-transaction signals filling gaps rather than duplicating them.

**Load.** `reference/feature_specs.md §3.3` and `§3.4`. T11 reuse map — this is the
task where reuse matters most.

## Steps

1. **Start from the sourced retail features.** Assess coverage, grain, and point-in-time
   correctness (do they respect a T0 or observation-date boundary, or are they
   as-of-today? — the latter would leak and must be recomputed or dropped).
2. Fill only genuine gaps from card transactions: travel/airline MCC flags, foreign
   country-code share, last-transaction-foreign flag.
3. Add the CASA-conditional signals if not already covered: salary-inflow stop gap,
   EOSB-like lump-sum-then-stop flag.
4. Build the `§3.4` history-shape group: fee velocity (lifetime and recent ratio),
   tenure, prior spells, roll speed, cross-product default timing where available, and
   the bureau leverage slope (pre-T0 pulls only).
5. **Always compute `relationship_breadth`** — it is the confound control that stops
   the model reading "has a relationship with us" as "has income".

## Done when

- Feature table built and joinable with T14/T15.
- **Explicitly recorded:** which features came from the sourced retail set, which were
  adapted, which were newly built — and for any reused feature, confirmation that its
  time-anchoring is leakage-safe.
- Null-rate/coverage report; T0-boundary leakage test passes (R2).
- Findings logged in `RESULTS.md`.
