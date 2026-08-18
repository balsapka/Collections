# T25 — Loan monthly-grain feasibility

**Goal.** Establish what payment behaviour can be derived for loan accounts from
month-end snapshots (plus CASA where available), and decide whether granular loan
payment data needs to be sourced.

**Why (R15).** CC has payment, balance and utilisation tables plus transaction
history. Loans have **only month-end snapshots**, so the CC payment-timing features do
not port. Sourcing granular loan payment data is possible but costs effort and has
lead time — so this decision should be made early even though CC leads the build.

**Load.** `reference/feature_specs.md §3.1` (the CC payment features, as the target to
approximate). Repo docs for the loan snapshot schema.

## What is likely derivable at monthly grain

Assess each; the first group is behaviour, the second is timing (probably lost):

- **Derivable:** installment-paid vs not (balance delta against expected amortisation),
  partial-payment magnitude, consecutive months without paydown, paydown-rate
  trajectory, outstanding vs original principal, DPD trajectory and roll speed.
- **Not derivable from month-end alone:** payment day-of-month, day-of-month drift,
  intra-month gap structure — i.e. the periodicity signals that act as the income
  proxy in the CC feature set.

## Steps

1. Confirm the loan snapshot schema and its true grain (strictly month-end? any
   intra-month rows?).
2. For each CC payment feature in `§3.1`, judge: derivable monthly / partially
   derivable / not derivable. Prototype the derivable ones on a sample.
3. Test the CASA route: for loan customers with CASA, is the loan repayment visible as
   a debit (giving timing)? Measure what share of loan customers that covers.
4. Estimate the gap: what fraction of the A4 signal is lost at monthly grain? Where
   possible, test on CC by degrading its data to month-end and comparing feature
   informativeness.

## Decision rule

- Monthly grain + CASA covers the behaviour signal adequately → build the loan A4 as a
  **distinct monthly-grain feature set**; no data sourcing needed.
- Substantial signal loss AND loans are a material share of recoverable value (T22) →
  **recommend triggering the granular data sourcing**, with the CC-degradation test as
  the evidence. Flag to the user; this has lead time.

## Done when

Feature-by-feature derivability table, CASA coverage share, and the sourcing
recommendation (with evidence) are logged in `RESULTS.md`, and the loan A4 approach is
recorded for later carding.
