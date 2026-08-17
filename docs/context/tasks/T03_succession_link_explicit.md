# T03 — Succession link: is it recorded anywhere?

**Goal.** Determine whether the old→new account relationship created by a restructure
is explicitly recorded in any system, before attempting to infer it.

**Why.** The link is needed for three things: excluding succession postings from labels
(T24), giving successor accounts their predecessor's history so A4 can see them
(T11–T15), and capturing restructure participation as a willingness signal. An explicit
link makes this a lookup; its absence makes it a record-linkage problem (T04).

**Load.** `reference/feature_specs.md §6` (steps 1–2).

## Steps

1. Search the account/facility schemas for a parent/reference/predecessor field on the
   new account, or a successor field on the old one.
2. Check closure reason codes — is "restructure" (or equivalent) distinguishable from
   other closures?
3. Check DCORE for restructure events; do they record both account numbers, or enough
   to join?
4. If any candidate exists, measure its coverage: what share of the T02 restructure
   population does it actually link?

## Decision rule

- A usable explicit link with good coverage → **skip T04.** Build the succession table
  directly from it and mark T04 `n/a`.
- Partial coverage → keep it as ground truth for validating T04's heuristic.
- Nothing found → proceed to T04.

## Done when

Findings per candidate source (exists? coverage?) are logged in `RESULTS.md`, T04 is
marked `todo` or `n/a` in `TASKS.md`, and O13 in
`reference/domain_and_decisions.md §8` is annotated with the answer.
