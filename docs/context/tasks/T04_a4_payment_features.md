# T04 — A4 CC: payment & balance trajectory features

**Goal.** Build the payment-behaviour half of the deterioration axis, anchored to T0.

**Why.** Payment *rhythm* is the closest thing to an income proxy available for the
~80% of the book with no CASA or cross-product signal. Salaried customers pay in a
tight day-of-month band; the loss or drift of that rhythm is a distress signature that
window aggregates flatten away. This is the feature group most likely to carry the
"new information" the axis exists to provide.

**Load.** `reference/feature_specs.md §3.1` (definitions). T01 reuse map. T02's window
decision (the 12-month window may have been shortened).

## Steps

1. **Reuse check (R14).** For each feature in `§3.1`, consult T01's map: REUSE as-is,
   ADAPT (most likely — existing features are anchored to `observation_date`, these
   need `T0`), or BUILD. Record which applied per feature.
2. Build against the T03 spell table, using CC payment/balance tables as well as
   transaction history — CC has richer sources than transactions alone (R15).
3. Implement the `§3.1` set: day-of-month dispersion and drift, payment gaps,
   payment-ratio level and slope across the two half-windows, minimum-payment share,
   months since last full payment.
4. Respect the null rules: features requiring ≥ 3 payments or ≥ 4 non-null months emit
   NULL rather than a fabricated value.

## Done when

- Feature table built for the CC delinquent population, keyed `(account_id, spell_id)`.
- Null-rate and coverage report per segment — flag any feature with implausibly low
  coverage before proceeding.
- **T0-boundary leakage test passes:** max source timestamp per row ≤ `T0` (R2).
- Reuse classification counts (REUSE/ADAPT/BUILD) logged in `RESULTS.md`.
