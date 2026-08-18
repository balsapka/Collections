# T09 — A4 gate PV2: novelty  ·  **the critical gate**

**Goal.** Determine whether the deterioration axis carries information the existing
feature set does not already contain.

**Why.** This is the whole premise. The current model is already known to be
substantially a function of one 24-month DPD vector (`current_state.md §2`) — if the new axis can be
predicted from those same features, it is a repackaging of what we know, and it will
fail in exactly the way the current score fails. Every other gate can pass while this
one fails, which is why it is worth running deliberately rather than assuming.

**Load.** Outputs of T07; `reference/current_state.md §2` (the state feature set and
its confirmed dominance); `reference/snippet_contract.md`.

## Steps

1. Assemble the predictor set. The sharpest version of this test is concrete: the
   existing state features are derivatives of **one 24-month DPD bucket history
   string**. So ask directly — *can the 24-month DPD string predict the A4 class?*
   Include its derivatives (days-since-last-payment, DPD velocity, missed EMIs) plus
   the current production feature set.
2. Train a multiclass model to predict `det_class_v1` from those features alone.
3. Report accuracy, per-class recall, and macro-AUC. Compare against the trivial
   baseline of always predicting the majority class.
4. Inspect *which* existing features predict the axis best — informative even on a
   pass, since it shows where the overlap sits.
5. Repeat treating the continuous A4 features as targets (regression R²) — a class may
   look novel while its underlying features are not.

## Decision rule

- **Existing features predict the axis well** (e.g. multiclass accuracy near the
  achievable ceiling, or macro-AUC ≳ 0.85) → **FAIL. The axis is a repackaging.**
  Revise it toward the components that were *not* predictable, or drop it. Do not
  carry it forward on the strength of PV1/PV3.
- **Poorly predicted** → PASS. The axis is genuinely orthogonal; this is the headline
  result for the persona programme and should be reported as such.
- **Mixed** (some classes predictable, others not) → keep the novel classes, merge or
  drop the predictable ones, and re-run T08.

## Done when

Prediction metrics (class and continuous), the most-predictive existing features, and
an explicit PASS/FAIL/MIXED verdict are logged in `RESULTS.md`, with the P8 evidence
line in `../problem_statement.md` updated.
