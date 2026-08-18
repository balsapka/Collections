# T10 — A4 gate PV4: incremental lift

**Track A** · **Depends:** T09 · **PROD round trip:** Yes

**Goal.** Measure what the axis adds to predictive performance over the model that
exists today.

**Why.** Novelty (T09) proves the axis is different; this proves the difference is
worth something. Both are needed — an axis can be genuinely orthogonal and still
irrelevant to outcomes.

**Precondition.** T09 passed (or passed for a subset of classes). An axis that failed
novelty is not tested here.

**Load.** Outputs of T07, T09; `reference/domain_and_decisions.md §3` for segments;
`reference/snippet_contract.md`.

## Steps

1. Baselines (R4): the **current production model** (which `current_state.md §2` established is
   effectively a state model, so this doubles as the state comparison) and
   **rank-by-outstanding-balance**.
2. Add the A4 features and class to the production feature set; retrain on the same
   split, within segment (R3).
3. Report capture@1/5/10% in **accounts and AED**, decile lift, calibration by decile,
   and — for the 60–180 exclusion use — precision@bottom-decile with a confidence
   interval. AUC may be reported for context but never alone.
4. Report the delta per segment, not pooled.

## Decision rule

- **Material gain** on capture@10 (AED especially) or precision@bottom → the axis
  ships as a model input. Record the size of the gain per segment.
- **No gain** → it does **not** ship as a model input. It may still ship as a
  *segmentation* if T08 (PV3) and the action workshop (T16) hold — record that
  distinction; a class that routes work usefully without improving ranking is still
  worth something.
- **Gain only in one segment** → ship there only, and say so.

## Done when

Per-segment comparison table (production vs production+A4 vs balance-only) on the R4
metric set, with per-segment ship/no-ship verdicts, logged in `RESULTS.md`.
