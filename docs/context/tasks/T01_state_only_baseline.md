# T01 — State-only baseline  ·  **CLOSED — do not re-run**

Already established by the user prior to this plan. Recorded here so no session
repeats it.

## Finding

- A model built **only** from delinquency-related features — all derived from a single
  **24-month DPD history** — was *not quite as good* as the full model, but **close
  enough** that the difference does not change how the score behaves in use.
- With no cap on feature-importance allowances, **2–3 features dominate SHAP**:
  `days since last payment` and `dpd velocity in last 3 months`. Feature-importance
  restrictions were needed to stop the model collapsing onto them.

## What it means

The tautology diagnosis is **confirmed, not hypothesised**. The current model is
substantially a function of one 24-month DPD vector — i.e. of information the
collections officer already sees. That is the mechanism behind the "no differentiation"
complaint, and it is why the persona axes must be judged on **novelty** (T19) rather
than on incremental AUC.

Note the second finding is evidence in its own right: needing importance caps to
prevent collapse onto two state features says the non-state features currently carry
little independent weight.

## Consequences for downstream tasks

- **T19 (PV2 novelty)** does not need a trained baseline. Predict the axis directly
  from the existing state feature set — the 24-month DPD derivatives plus the current
  production features.
- **T20 (PV4 lift)** measures against the **current production model**. Since
  state-only ≈ production, beating production is the same test as beating a state
  baseline, and it is the comparison stakeholders care about.
- Rank-by-outstanding-balance remains a required second baseline (R4).
