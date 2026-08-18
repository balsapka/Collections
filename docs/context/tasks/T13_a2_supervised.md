# T13 — A2 supervised v2

**Goal.** Replace the v1 rules with a supervised classifier trained on field-visit
dispositions.

**Precondition.** T11 cleared DCORE **and** confirmed field-visit dispositions exist
and distinguish the needed outcomes. If not, this task is `blocked` — T12's rules ship
instead, and that is an acceptable outcome, not a failure.

**Load.** `reference/feature_specs.md §4.2` (label mapping). T12's feature set.

## Steps

1. Fill the disposition-code → label mapping in `§4.2` from the actual code list.
   Codes that do not map cleanly should be excluded, not forced.
2. Assemble the labelled set: accounts with a field visit or recorded right-party
   contact. Note it is a **selected** population — visits are not randomly assigned —
   so report how it differs from the book and treat transfer with caution.
3. Train a multiclass LightGBM (R8) on T12's features; hold out for evaluation.
4. Report the held-out confusion matrix per state, not just overall accuracy — the
   `gone` state's precision is what protects the field-visit budget.
5. Apply to the full book; set `observed` only where a recent visit or right-party
   contact exists, `inferred` elsewhere (R6).

## Done when

Confusion matrix and per-state precision/recall logged in `RESULTS.md`; the selection
caveat documented; comparison against T12's rules (do they agree? where do they
diverge?) recorded so the rules can be improved even if v2 ships.
