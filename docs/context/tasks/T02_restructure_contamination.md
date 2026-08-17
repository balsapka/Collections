# T02 — Restructure volume & label contamination

**Goal.** Measure how often restructures happen, and whether their closing entries are
being counted as recovery in current outcome measures.

**Why (R13).** A restructure closes the account and opens a new one. If the closing
entry resembles a settlement credit, a restructure reads as *recovery* — inverted,
since the debt moved rather than being repaid. That would mean numbers already reported
to stakeholders overstate recovery. Size the problem before solving it: if restructures
are a trivial share of the book, record the blind spot and move on.

**Load.** `reference/snippet_contract.md`; `reference/current_state.md §3`;
`reference/feature_specs.md §1`.

**Snippet notes.** Step 2 is a self-join on the account table keyed by CIF — restrict
it to accounts closed with a balance first, which should cut it to a small fraction of
the book before the join. Step 3 needs the *distribution of posting types* at closure,
not the postings themselves: print the type codes with counts and let the user
identify which are settlement-like. Sequence this as one snippet with clearly separated
parts so a single PROD run answers the whole card.

## Steps

1. Identify closure events with outstanding balance > 0, by account type (R3).
2. Of those, how many are followed within a short window by a new account for the same
   CIF of the same type? Report the share of the delinquent book.
3. Inspect the posting types generated at closure. Do any fall inside the current
   payment/recovery definition used by existing labels?
4. If yes: quantify the inflation — recompute current recovery/cure rates with those
   postings excluded, and report the delta per segment.

## Decision rule

- Restructures are a material share AND closing postings are counted → succession
  postings must be excluded from `payments()` (`reference/feature_specs.md §1`); all
  current recovery/cure figures need a caveat; T24 depends on this.
- Trivial share → record the size, note the blind spot in `RESULTS.md`, and T03/T04
  can be capped or dropped.

## Done when

Restructure share of book (by account type), posting-type findings, and the recomputed
rate deltas are logged in `RESULTS.md`, and the P4b evidence line in
`../problem_statement.md` is updated.
