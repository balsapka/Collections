# T18 — A4 gates PV1 + PV3: buildability & outcome separation

**Goal.** Confirm the axis is computable across the book and that its classes actually
differ in what happens next.

**Why.** These are the two cheapest ways an axis can fail. If it only computes for
half the population it cannot drive strategy; if its classes have the same outcomes it
describes nothing that matters. Both are checkable without touching the risk models.

**Load.** Outputs of T17. `reference/domain_and_decisions.md §3` for segment
definitions.

## PV1 — Buildability

Report per segment: coverage (share with a non-null class), null rates of the
underlying features, class distribution.

**Pass:** computable for ≥ ~80% of the segment; no class below ~5% or above ~60% of
volume; `mixed` not dominant.

## PV3 — Outcome separation

For each class, within segment, report realised cure rate, recovery rate and mean
recovered AED over the relevant horizon.

**Pass:** extreme-class outcome ratio ≥ ~1.5×; ordering is stable across at least two
distinct time periods (guards against a one-off).

## Decision rule

- Both pass → proceed to T19 (novelty), the harder gate.
- PV1 fails → return to T17 (thresholds) or T14–T16 (coverage) before proceeding.
- PV3 fails → the axis describes something real but outcome-irrelevant. It may still
  have operational value (e.g. for routing), but it does not enter the risk models —
  record that distinction explicitly rather than quietly dropping it.

## Done when

Coverage, class distribution, and per-class outcome tables (with the two-period
stability check) logged in `RESULTS.md`, with an explicit PASS/FAIL per gate.
