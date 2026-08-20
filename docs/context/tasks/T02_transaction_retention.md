# T02 — Retention depth, per source table

**Track A** · **Depends:** — · **PROD round trip:** Yes — fire early

**Goal.** Establish whether the pre-delinquency window `[T0−12m, T0]` actually exists
in retained data, **per source table**, per segment and cohort.

⚠ **Ask the question of each table separately (O18, user-ratified 2026-08-20).** CC
balance, utilisation and payment data live in **dedicated tables**, not only in transaction
history. A single transaction-derived floor would truncate feature families that never
depended on the transaction stream — only §3.3 (departure: MCC, country codes) genuinely
needs transactions. The output is a floor **per family**, not one window.

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

1. For a sample per segment (CC / loan × band × 180+ cohort), compute months of history
   available before T0 **for each source separately**: transaction history, payment table,
   balance table, utilisation table (CC); month-end snapshots (loan); CASA where present.
2. Report the share with ≥ 12, ≥ 9, ≥ 6, ≥ 3 full months — **one row per source table**.
3. Identify where each cliff falls — retention policy boundary, archive tier, or
   source-system migration? They may differ by table.
4. Map each floor to the A4 feature families it constrains: §3.1 payment rhythm, §3.2
   utilisation/spend, §3.3 departure, §3.4 history shape.

**While you are here (O17, loans):** confirm whether the loan month-end snapshot carries a
**days-overdue column**, and how deep the snapshot history goes. If it does, loan bucket
derivation is *assembly* rather than *reconstruction* — see `feature_specs §2`. Existence is
answerable from the workplace schema docs in UAT; only the convention questions need data.

## Decision rule

- Adequate depth for the <2y cohort but not >2y → confirms the existing decision not
  to score the aged book from internal history; record and move on.
- **Thin for one source but not others** → shrink only the families fed by that source;
  record the per-family floor. Do not shrink the whole window.
- Thin everywhere → **shrink the A4 window** to what actually exists (e.g. 6 months),
  record the change, and note the expected weakening of trajectory features.
- Data exists but only in archive → flag to the user as a sourcing question before
  T04 is scheduled.

## Done when

Availability table (share by months-available, **per source table**, per segment and cohort)
logged in `RESULTS.md`; the per-family window floors recorded for T04b–T07 to consume; and
the loan days-overdue column question (O17) answered or explicitly deferred.
