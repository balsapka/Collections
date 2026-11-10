# A1 ability: bring the CASA balance back as evidence (proposal, 2026-11-10)

For the next round of the evidence-family redesign. Not decided; test it before the rule changes.

## Why

- Rule R3 dropped liquidity (CASA balance), because GRR said balances are swept against the overdue
  amount, and "Adequate" liquidity fired for only ~1.0% of cards and ~1.4% of loans.
- New fact (user, 2026-11-10): the sweep is **operational and manual** (a team does it). It is not
  automatic or rule-based, so mistakes and delays happen and balances can survive it.
- A balance that survives the sweep is therefore real money the customer holds. It is rare, but it
  is still an ability signal, and R3 currently ignores it.

## Proposal

Count a CASA balance above the floor towards the **F2 "Money in"** family. It would not become a
fifth family.
- F2 reads "money arriving or held, not salary".
- A family stays strong / weak / absent. The High rule is unchanged: 2+ strong families.
- Alternatives considered:
  - leave it out (R3 as is);
  - a fifth family "Balance held". This was rejected because it would almost never be strong,
    which makes the 2+ strong rule odd.

## To test (round 3 or the next round)

1. **Firing.** How often does a balance above the floor occur at 61–180 and 180+, per product?
   Use the same floor as the old liquidity rule (max(AED 3,000, 1 × minimum due), 2 of 3 months),
   and a looser variant.
2. **State moves.** How many rows does it move (Low → Moderate, Moderate → High), and which F2 cases
   does it add?
3. **Outcomes.** Do the moved rows cure or pay like their new band, or like their old one?
4. **The sweep itself.** Does a held balance tend to disappear the following month? If so, the
   balance is a timing artefact rather than ability.

## Side note for GRR (not part of the persona)

A delinquent customer holding a balance above the floor is an operational lead: that money is
recoverable now through the sweep. It could be a flag in the output or a line in the GRR deck.
