# T10 — DCORE trust assessment

**Goal.** Establish objectively whether DCORE fields can be trusted, without waiting
for the data owners' investigation to conclude.

**Why.** DCORE holds PTP, contact attempts and dispositions. It gates the willingness
axis entirely, the supervised version of locatability, and the descriptive
action/outcome crosstab. Its data quality is unresolved and may not be fixed in time,
so the build order deliberately puts DCORE-dependent work last — but that ordering
needs a measurement behind it.

**Load.** `reference/snippet_contract.md`; `reference/domain_and_decisions.md §4`.

**Snippet notes.** The PTP reconciliation is a join between DCORE promises and the
payments table — bound it to a recent window (say 12 months) rather than all history;
agreement rate is a ratio and does not need the full record. Print rates and code
distributions only, never individual records: DCORE rows contain customer contact
detail that should not be pasted into a chat session.

## Steps

1. **PTP reconciliation (the decisive test).** For promises recorded as *kept*, check
   the payments table for a corresponding payment in the expected window. Report
   agreement rate. Do the same for *broken* promises (expect no payment).
2. **Coverage.** What share of delinquent accounts have any DCORE record at all? Break
   down by band, account type, and time — did coverage shift at a migration or policy
   change?
3. **Code discipline.** Distribution of disposition codes: what share are specific vs
   generic/"other"? A dominant generic bucket makes the field unusable for the
   locatability states even if coverage looks fine.
4. **Integrity.** Referential integrity to accounts; duplicates; orphans.
5. **Field visits specifically.** Are dispositions recorded, and do they distinguish
   the outcomes locatability needs (vacant / relocated / person unknown / confirmed
   residing / contacted)?

## Decision rule

Provisional thresholds — **CONFIRM with the user before acting on them**:
- PTP agreement < ~90% **or** coverage < ~80% → DCORE fields untrusted: **A3 blocked**,
  A2 ships core-banking-only (T21 without T22), crosstab deferred.
- Passes both but field-visit dispositions are unusable → A2 stays at v1 rules; record
  that its supervised version has no label source.
- Passes all → A3 and A2-v2 unblock; note it in `TASKS.md`.

## Done when

Agreement rates, coverage, code distribution and the field-visit finding are logged in
`RESULTS.md`, and the gates on T22 / A3 are set in `TASKS.md`.
