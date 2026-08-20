# T11 — DCORE trust assessment

**Track A** · **Depends:** — · **PROD round trip:** Yes — fire before T12

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
   residing / contacted)? **Also: how many accounts have any visit at all** — T13's scope
   depends on it, and it is currently unverified.
6. **Contact-attempt outcome codes — as a label source, not only as features.** A2 now
   derives its states from these (S18, `feature_specs §4.1b`), so they need their own check;
   clearing field-visit dispositions does not clear them. Telephony metadata and
   hand-written visit dispositions fail differently — auto-dialler behaviour and carrier
   reporting versus human recording discipline.
   - Is the vocabulary as described: right-party contact / rang-no-answer / answered-no-
     meaningful-conversation / did-not-go-through / email no-reply?
   - **O15, the decisive one:** does "answered but no meaningful conversation" distinguish
     *the customer deflecting* from *a stranger on a reassigned number*? One undifferentiated
     code collapses a row of the `§4.0` matrix and blurs `avoiding` against `skip`.
   - Is `contact_attempts_n` reliably countable? Attempt-normalisation (§4.4b) depends on a
     trustworthy denominator — if attempts are logged inconsistently, every rate is wrong.
7. **O16 — dispatch rule.** How are field visits triggered: by failed contact, by balance, or
   by a routing rule? The `§4.0` selection argument and T13's population both rest on this.

## Decision rule

Provisional thresholds — **CONFIRM with the user before acting on them**. Note the three
consumers now fail independently, so report a verdict per consumer, not one overall:

| Test | If it fails |
|---|---|
| PTP agreement < ~90% or coverage < ~80% | **A3 deferred** — but not permanently: UC1 transcripts are its eventual source (S19). Descriptive crosstab deferred |
| Contact-attempt codes unusable, or `contact_attempts_n` untrustworthy | **A2 degrades to three states** (`gone` / `active-but-not-paying` / `unknown`, §4.2) — it does not block, but say so in the output |
| O15 collapses (one undifferentiated "answered" code) | `avoiding` and `skip` blur; record the ambiguity in the state definitions rather than presenting four clean states |
| Field-visit dispositions unusable **or** coverage thin | **T13 dropped or scoped down.** A2 still ships from T12 — the derivation does not depend on visits (S18) |
| Passes all | A3 unblocks now rather than waiting for UC1; T13 proceeds at whatever scale coverage supports |

## Done when

Agreement rates, coverage, code distribution, the contact-code findings (including O15), the
field-visit coverage number and the dispatch rule (O16) are logged in `RESULTS.md`, and the
per-consumer gates on T12 / T13 / A3 are set in `TASKS.md`.
