# T01 — Feature inventory & reuse map

**Track A** · **Depends:** — · **PROD round trip:** No — UAT only (optional follow-up snippet)

**Goal.** Produce a mapping from every feature the persona axes need to what already
exists in the repo, so later build tasks reuse instead of rebuild (R14).

**Why.** The repo has full end-to-end pipelines for most domains and hundreds of
existing features. Some of what A4 and A2 need almost certainly exists already — in
the feature layer, in other retail use cases, or as helper logic. Building it again
wastes sessions and creates two versions of the same number. This task is the single
highest-leverage thing to do before any feature build.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §3` and `§4` (the target feature lists). Also
read the workplace repo's own `CLAUDE.md` and docs — they describe the existing
pipelines and are the primary source here (R9).

**This task is mostly runnable in UAT** — it is code and documentation reading, not
data querying, so no PROD round trip is needed for the bulk of it. Where fit can only
be settled by looking at actual values (e.g. does an existing feature's distribution
match what A4 needs?), note the question and batch those into a single optional
snippet at the end rather than blocking the inventory on them.

## Steps

1. Enumerate the required features from `feature_specs.md §3` (A4) and `§4` (A2).
2. Search the repo's feature layer, other use-case pipelines, and shared utility code
   for each. Search by concept as well as by name — the same quantity may exist under
   a different label (e.g. a utilisation trend, a payment-regularity metric, a
   recency/gap feature, a channel-activity flag).
3. Classify each required feature:
   - **REUSE** — exists and matches; record the table/column and any grain caveat
   - **ADAPT** — exists but needs a different window, grain or anchor (most likely
     case: existing features are anchored to `observation_date`, A4 needs `T0`)
   - **BUILD** — nothing equivalent exists
4. Separately inventory reusable *infrastructure*: spell/window helpers, aggregation
   utilities, evaluation and reporting code, test fixtures.
5. Note per-unit availability (CC vs loan) given the grain difference (R15).

## Special cases to check for explicitly

- **Departure / travel signature features:** ready-made features exist from internal
  retail use cases built on CASA and product-holdings data. The user is sourcing these.
  Find them, assess fit, and mark T06 accordingly — do not rebuild departure logic
  from card transactions if these cover it.
- **Payment regularity / recency:** the current models already use days-since-last-
  payment and DPD velocity; check whether richer payment-pattern features exist beside
  them.

## Done when

A reuse map table (feature → REUSE/ADAPT/BUILD → source → caveat) is committed to the
repo's docs and summarised in `RESULTS.md`, with a count per class. T04–T06 and T12
consume it. Any feature classified BUILD that looks expensive should be flagged for
the user before it is scheduled.
