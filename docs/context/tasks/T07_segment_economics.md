# T07 — Segment economics

**Goal.** Size every segment: positive rate, recovery magnitude, and total recoverable
AED — so effort goes where the value is, decided by a number rather than an argument.

**Why.** Several open questions collapse once this exists: whether auto behaves
differently enough to justify its own track, whether the >2y cohort holds enough
absolute value to deserve attention despite a 1–2% rate, and whether the current
180+ target's dual threshold is balance-dependent.

**Load.** `reference/domain_and_decisions.md §3`.

## Steps

Group existing outcome data by modelling unit (CC / loan-auto / loan-other) × band ×
(at 180+) time-in-bucket cohort, and report:

1. Positive rate under the current target definitions.
2. Average and total recovered AED among positives.
3. **Total recoverable AED** = accounts × positive rate × average recovered AED.
4. Positive rate by **outstanding-balance band** within 180+ (tests whether the
   `5% or 1000 AED` threshold makes the target's meaning balance-dependent).

## Decision rules

- **Auto materially different from CC** (rate and/or magnitude) → confirms the separate
  auto track; record the size so it can be prioritised against CC.
- **>2y cohort holds large absolute value** despite its low rate → revisit how much
  attention the aged book gets; otherwise confirm bulk treatment.
- **Strong balance gradient in positive rate** → evidence that the dual threshold is
  partly measuring account size; feeds the T26 label revision and the stakeholder
  material.

## Done when

The full segment table (counts, rates, magnitudes, recoverable AED) and the
balance-band gradient are logged in `RESULTS.md`, and the P3/P4 evidence lines in
`../problem_statement.md` are updated.
