# T25 — Loan monthly-grain feasibility

**Track C** · **Depends:** T01 · **PROD round trip:** Yes

**Goal.** Establish what payment behaviour can be derived for loan accounts from
month-end snapshots (plus CASA where available), and decide whether granular loan
payment data needs to be sourced.

**Why (R15).** CC has payment, balance and utilisation tables plus transaction
history. Loans have **only month-end snapshots**, so the CC payment-timing features do
not port. Sourcing granular loan payment data is possible but costs effort and has
lead time — so this decision should be made early even though CC leads the build.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §3.1` (the CC payment features, as the target to
approximate). Repo docs for the loan snapshot schema.

## Known loan columns (user-confirmed 2026-08-20)

`payment_mtd`, principal outstanding, `emi`, at month-end grain. Transaction-level loan data
**can be sourced if needed** — but see the scoping warning below before asking for it.

## The loan A4 sketch — what carries the work

- **`payment_mtd / emi` as a monthly series is the workhorse**, the direct analogue of
  `pay_ratio` (§3.1). It carries the class separation on its own: a step from ~1.0 to 0 reads
  `abrupt_shock`; shrinking partials read `gradual_spiral`; persistent 0.3–0.7 reads
  `chronic_marginal`.
- **Schedule divergence** — expected outstanding from the amortisation schedule against
  actual principal outstanding — substitutes for rising utilisation (§3.2 has no loan analogue).
- **Prepayment behaviour** is loan-only, with no card equivalent. Ceasing to prepay is an
  early warning cards cannot give.
- **Dead:** day-of-month rhythm, spend cliff/taper, cash-advance ramp, MCC/travel signatures.
- **Coverage inverts in our favour.** Personal loans are typically salary-transfer, so CASA
  coverage is probably far higher than on the card-only book — meaning the salary-stop and
  EOSB signals that are weak and `[COND]` on cards may be *stronger* here.

⚠ **Scope the sourcing ask correctly.** A loan account has no spend stream to recover — its
"transactions" are disbursements, repayments and fee postings, largely already in
`payment_mtd`. **The stream with real marginal value is CASA depth, not loan-account
transactions.** Establish that before triggering any sourcing exercise; it may avoid one.

## Steps

1. Confirm the loan snapshot schema and its true grain (strictly month-end? any
   intra-month rows?).
2. **Answer O17: is there a days-overdue column?** If so, bucket derivation is *assembly*,
   not *reconstruction* (`feature_specs §2`) — and establish the four conventions listed
   there (DPD basis, partial-payment application, at-snapshot vs max-in-month, days→bucket
   boundary). Also measure **snapshot history depth**: CC's 24-month string is a hard
   censoring limit, and a snapshot table may retain longer, which would make loans *better*
   than CC for long-horizon spell detection.
3. If there is no DPD column, prototype `arrears / emi` as months-in-arrears — and
   **validate it specifically on partial payers**, where it drifts from calendar DPD. That
   drift concentrates in exactly the `chronic_marginal` population.
4. For each CC payment feature in `§3.1`, judge: derivable monthly / partially derivable /
   not derivable. Prototype the derivable ones on a sample, starting with `payment_mtd / emi`.
5. **Measure CASA coverage on the loan book** and compare it to the card book — test whether
   the expected inversion holds. For loan customers with CASA, is the repayment visible as a
   debit (giving timing)?
6. Estimate the gap: what fraction of the A4 signal is lost at monthly grain? Where possible,
   test on CC by degrading its data to month-end and comparing feature informativeness.

## Decision rule

- Monthly grain + CASA covers the behaviour signal adequately → build the loan A4 as a
  **distinct monthly-grain feature set**; no data sourcing needed.
- Substantial signal loss AND loans are a material share of recoverable value (T22) →
  **recommend sourcing CASA depth first**, with the CC-degradation test as the evidence.
  Only recommend loan-account transaction sourcing if there is a specific feature it unlocks
  that `payment_mtd` and the schedule cannot — name it explicitly. Flag to the user; this has
  lead time.

## Done when

Feature-by-feature derivability table, CASA coverage share, and the sourcing
recommendation (with evidence) are logged in `RESULTS.md`, and the loan A4 approach is
recorded for later carding.
