# T13 — A2 supervised refinement

**Track A** · **Depends:** T12, T11 · **PROD round trip:** Yes

**Goal.** Sharpen the **one ambiguous cell** of the `§4.0` matrix — rang-no-answer with no
presence evidence, where T12's rules fall to `unknown` — using field-visit dispositions.

**This is a refinement, not the main path (S18).** T12 ships the axis. If visit coverage is
thin, this task is scoped down or dropped and that is an acceptable outcome, not a failure.
The earlier design — train a multiclass model on visited accounts and apply it to the whole
book — was **withdrawn on 2026-08-20**: visits are dispatched *because* contact already
failed, so such a model learns P(state | features, already-failed-contact) and does not
transfer. Do not reinstate it.

**Precondition.** T11 cleared DCORE **and** confirmed field-visit dispositions exist,
distinguish the needed outcomes, and cover enough accounts to train on. If not, `blocked` —
T12's derivation ships alone.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §4.3`. T12's output.

## Steps

1. **Size the opportunity before building.** How many accounts sit in the ambiguous cell,
   and how many of those have a field visit? If the intersection is small, stop here and
   record it — the refinement is not worth a model.
2. Fill the disposition-code → label mapping in `§4.3` from the actual code list. Codes that
   do not map cleanly are excluded, not forced.
3. **Answer O16 while you are here:** how are visits dispatched — by failed contact, by
   balance, or by a routing rule? The population definition below depends on it.
4. **Train and apply on the same population.** Restrict to the unreached, which is where
   visits are dispatched. A model trained there may be applied *only* there. State the
   population explicitly in the output; never score the book with it.
5. Train multiclass LightGBM (R8) on T12's features; hold out for evaluation.
6. Report the held-out confusion matrix per state, not overall accuracy — **`gone` precision
   is the number that matters**, because it protects the field-visit budget.
7. Report how visited accounts differ from unvisited ones on observables. Even within the
   unreached, dispatch is unlikely to be random (O16) — the residual selection must be
   stated, not assumed away.
8. Compare against T12's derivation: where do they agree, where do they diverge? Feed
   divergences back into the `§4.2` rules so those improve even if this does not ship.

## Decision rule

- Ambiguous-cell ∩ visited too small to train → **drop**; record the size and move on.
- Trains adequately → ships as a refinement **scoped to the unreached population only**.
- Diverges sharply from T12's rules without a clear reason → investigate before adopting;
  the rules are the shipped default and carry the coverage.

## Done when

Ambiguous-cell size and visit intersection logged; O16 answered; confusion matrix and
per-state precision/recall in `RESULTS.md` if a model was built; the population restriction
documented in the output schema; and the T12 comparison recorded so the rules improve either
way.
