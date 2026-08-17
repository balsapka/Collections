# Current State and Diagnosis

## 1. What already exists (modify, don't rebuild)

The workplace repo's own `CLAUDE.md`/docs describe the built assets: DE pipelines
(staging → feature layers) for every domain in `01 §4`, LightGBM modelling pipelines
for the current targets, and reporting pipelines. Defer to those docs for names and
patterns (R9). What the strategy needs to know:

- New feature families (A2/A4) are **additions** beside the existing feature layer,
  reusing its patterns — not a parallel stack.
- W1 modifies the label layer; W5 retrains per segment and extends reporting.
- R11: the existing roll model and its reports keep running throughout.

Current targets implemented:
- **60–180:** roll-based — positive = stays in bucket or moves back; negative = rolls
  forward one 30-day bucket. One-month-flavoured horizon.
- **180+:** cumulative recovery in next 6m ≥ 5% of outstanding OR ≥ 1000 AED.

## 2. Why the current model underdelivers (evidence)

Reported top features (both targets), from the user:

> days since last payment · DPD velocity last 3m · missed EMIs · last payment amount ·
> card block codes · lifetime fee velocity · DPD 6 months ago · bureau total salary
> last 6m · CASA inflow/outflow ratio features

**Diagnosis — tautology.** Six of nine are restatements of delinquency state (how
delinquent, how fast). The model learned "worse now → worse later": true, mechanical,
and already on the collections officer's screen. On the roll target the link is
near-mechanical (no payment in 90 days ⇒ will roll) — the model partly computes rather
than predicts. This also explains AUC being flat across buckets (state features work
mechanically in every bucket) and is the substance behind the stakeholder complaint.

Quantify it with **D4** (state-only baseline) before presenting anything.

Note: this is *not* a leakage finding. The existing modelling spectrum is already
leakage-controlled (R2) — the features are legitimate, they are simply restatements of
what the officer already sees. Keep that discipline; the problem is orthogonality, not
correctness.

**The two genuine signals in the list:**
- `CASA inflow/outflow` + `bureau total salary` — real ability signal. But importance
  may be inflated relative to ~20% coverage (split-based GBM importance artefact).
  **D5** (CASA-holder vs card-only performance split) decides what Axis A1 is worth.
- `lifetime fee velocity` — a **proto-A4 feature**: accrues over years, separates the
  chronically marginal from the suddenly broken. Its rank is direct evidence that
  deterioration-shape carries signal the current set captures only by accident.

**Metric context:** PR-AUC ≈ 0.6 for cure. PR-AUC baseline = positive prevalence
(~0.25 at 60–90), so ≈ 2.4x baseline — a decent model on a mis-specified question,
not a broken model. Do not frame this to stakeholders as "the model is weak".

## 3. Known contamination risks (verify before trusting results)

| Risk | Check | Consequence if real |
|---|---|---|
| **Restructure = account succession** (R13): the old CC/loan is closed and a new one opened. If closure posts a settlement-like credit, a restructure reads as **recovery** — inverted, since the debt moved rather than being repaid. The old→new link is not yet identifiable (O13) | D7 / W0 | Recovery and futility labels inflated on every restructured account; `payments()` must exclude succession postings (`04 §1`); restructured customers are an A4 blind spot until W0 lands |
| Card block codes fire after observation date, or are DPD-triggered operational actions | D10 / O11 | Leakage or self-fulfilling feature — drop or lag it |
| Bureau salary freshness inconsistent across rows (AECB dry at delinquency) | D10 / O12 | Feature means different things per row; model exploits the inconsistency |

## 4. What is missing (the actual gap)

Hundreds of features exist on the saturated state dimension; approximately zero on the
four orthogonal mechanism dimensions: locatability (A2), ability (A1), willingness
(A3), manner-of-deterioration (A4). Coverage reality (`01 §4`) says A4 is the only one
buildable for the whole book — hence the build order in `03`.
