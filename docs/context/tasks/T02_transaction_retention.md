# T02 — Transaction retention depth

**Track A** · **Depends:** — · **PROD round trip:** Yes — fire early

**Goal.** Establish whether the pre-delinquency window `[T0−12m, T0]` actually exists
in retained data, per segment and cohort.

**Why.** A4 is anchored to T0 and reads the 12 months before it. For a 180+ account
that entered the bucket over two years ago, that window is 3+ years back and may be
purged or archived — which would make A4 unavailable for exactly the cohort where
deterioration history matters most. This sets the achievable scope of T04–T07.

**Load.** `reference/snippet_contract.md`. `feature_specs.md §3` for the window
definition if useful.

**Snippet cost warning.** A naive version scans full transaction history across
billions of rows. Instead: draw a bounded random sample of accounts per segment
(a few thousand each is ample for a coverage estimate), compute min/max transaction
date per sampled account, and derive months-available from that. State the sample size
and method in the output so the estimate is interpretable.

## Steps

1. For a sample per segment (CC / loan × band × 180+ cohort), compute months of
   available transaction (CC) or snapshot (loan) history before T0.
2. Report the share with ≥ 12, ≥ 9, ≥ 6, ≥ 3 full months.
3. Identify where the cliff falls — is it a retention policy boundary, an archive
   tier, or a source-system migration?
4. Check the same for the other A4 inputs: payment/balance tables (CC), month-end
   snapshots (loan), and CASA where present.

## Decision rule

- Adequate depth for the <2y cohort but not >2y → confirms the existing decision not
  to score the aged book from internal history; record and move on.
- Thin everywhere → **shrink the A4 window** to what actually exists (e.g. 6 months),
  record the change, and note the expected weakening of trajectory features.
- Data exists but only in archive → flag to the user as a sourcing question before
  T04 is scheduled.

## Done when

Availability table (share by months-available, per segment and cohort) logged in
`RESULTS.md`, and the A4 window decision recorded for T04–T07 to consume.
