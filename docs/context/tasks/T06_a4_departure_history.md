# T06 — A4: departure signature & history shape

**Track A** · **Depends:** T03, T01 · **PROD round trip:** Yes — validation snippet

**Goal.** Assemble the departure/travel signals and the long-horizon history features —
**reusing existing feature solutions from across the workspace rather than deriving them
from transaction history ourselves.**

**Why.** Departure is a distinct failure mode: a customer who left the country is
unreachable regardless of willingness or ability, and no amount of collections effort
changes that. Ready-made departure-flavoured features already exist — in the working
repo's own feature layer and in **two sibling repos cloned beside it**,
`wealth_management` and `retail.feature_space` — built on CASA and product-holdings
data. Those should carry this group. The card-transaction signals in `§3.3`
(travel MCC, foreign country code) are the **gap fill, not the starting point**:
deriving them from scratch when a maintained version already exists gives the bank two
versions of the same number.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §3.3` and `§3.4`. T01 reuse map — this is the
task where reuse matters most.

## Steps

1. **Search the workspace first (R14).** Three places, in this order: the working repo's
   feature layer, `retail.feature_space`, `wealth_management`. Resolve the workspace root
   as the parent of the working repo root; **directory names on disk may differ from the
   repo names — confirm the real paths, do not guess (R9).** Search by *concept*, not
   just by name: departure logic hides under labels like travel, non-resident, expat,
   exit, relocation, offshore, dormancy, "out of country", "left country".
2. **Read each candidate's definition, not just its output.** Same name, different
   definition is the standard trap — record the actual formula and its inputs.
3. **Screen every candidate on three tests before adopting it.** A feature that was fine
   for its original use case can fail all three here:
   - **Coverage on *our* population.** This is the test most likely to kill a
     `wealth_management` feature: it was built on an affluent segment that may barely
     intersect the delinquent CC book. Measure the non-null share on the T03 spine
     scope, per segment. A feature covering a few percent of the book is a footnote, not
     a feature. State the number — never adopt on faith.
   - **Point-in-time correctness (R2).** Is it anchored to a date, or is it as-of-today?
     An as-of-today "has left the country" flag is pure leakage against a T0-anchored
     model — recompute it against T0 or drop it.
   - **Protected-attribute inputs (R7).** A departure feature built for another purpose
     may take nationality, visa/iqama or residency status *directly*. Inspect the
     inputs, not just the output. Anything that does is not adoptable as-is, and goes to
     T15 regardless.
   Fold the coverage measurement into this task's PROD snippet — it is the same round
   trip as the validation run, not a separate one.
4. **Classify and record** each feature REUSE / ADAPT / BUILD with provenance — source
   repo, file path, commit sha, original name — feeding the T01 reuse map. Port the
   logic into our own additive module (R18); do not cross-import between repos, and
   never write into a sibling repo.
5. Fill only genuine gaps from card transactions: travel/airline MCC flags, foreign
   country-code share, last-transaction-foreign flag.
6. Add the CASA-conditional signals if not already covered: salary-inflow stop gap,
   EOSB-like lump-sum-then-stop flag.
7. Build the `§3.4` history-shape group: fee velocity (lifetime and recent ratio),
   tenure, prior spells, roll speed, cross-product default timing where available, and
   the bureau leverage slope (pre-T0 pulls only).
8. **Always compute `relationship_breadth`** — it is the confound control that stops
   the model reading "has a relationship with us" as "has income".

## Done when

- Feature table built and joinable with T04/T05.
- **Explicitly recorded:** which features came from which repo (with path and commit),
  which were adapted, which were newly built — and for every borrowed feature, the three
  screen results: coverage %, time-anchoring verdict, protected-input verdict.
- **Where you looked is logged even when you found nothing.** A "searched
  `retail.feature_space` and `wealth_management`, nothing usable because X" line in
  `RESULTS.md` stops the next session repeating the search.
- Null-rate/coverage report; T0-boundary leakage test passes (R2).
- Findings logged in `RESULTS.md`.
