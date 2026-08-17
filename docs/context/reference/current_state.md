# Current State and Diagnosis

## 1. What already exists (modify, don't rebuild)

The workplace repo's own `CLAUDE.md`/docs describe the built assets: DE pipelines
(staging → feature layers) for every domain in `domain_and_decisions.md §4`, LightGBM modelling pipelines
for the current targets, and reporting pipelines. Defer to those docs for names and
patterns (R9). What the strategy needs to know:

- New feature families (A2/A4) are **additions** beside the existing feature layer,
  reusing its patterns — not a parallel stack.
- T26 modifies the label layer; the later retrain covers segments and extends reporting.
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

**Diagnosis — tautology. CONFIRMED, not hypothesised** (user's prior testing; T01 is
closed — do not re-run it):

- A model built **only** from delinquency-related features — all derived from the
  single **24-month DPD bucket history** feature — was not quite as good as the full
  model but **close enough** that the gap does not change how the score behaves in use.
- With no cap on feature-importance allowances, **2–3 features dominate SHAP**
  (`days since last payment`, `dpd velocity last 3m`). Importance restrictions were
  needed to stop the model collapsing onto them — itself evidence that the remaining
  features carry little independent weight.

Six of nine top features restate delinquency state (how delinquent, how fast). The
model learned "worse now → worse later": true, mechanical, and already on the
collections officer's screen. On the roll target the link is near-mechanical (no
payment in 90 days ⇒ will roll) — it partly computes rather than predicts. This also
explains AUC being flat across buckets, and is the substance behind the stakeholder
complaint.

**Consequence:** persona axes must be judged on **novelty** — can the 24-month DPD
string predict them (T19)? — not on incremental AUC.

Note: this is *not* a leakage finding. The existing modelling spectrum is already
leakage-controlled (R2) — the features are legitimate, they are simply restatements of
what the officer already sees. Keep that discipline; the problem is orthogonality, not
correctness.

**The two genuine signals in the list:**
- `CASA inflow/outflow` + `bureau total salary` — real ability signal. But importance
  may be inflated relative to ~20% coverage (split-based GBM importance artefact).
  **T09** (CASA-holder vs card-only performance split) decides what Axis A1 is worth.
- `lifetime fee velocity` — a **proto-A4 feature**: accrues over years, separates the
  chronically marginal from the suddenly broken. Its rank is direct evidence that
  deterioration-shape carries signal the current set captures only by accident.

**Metric context:** PR-AUC ≈ 0.6 for cure. PR-AUC baseline = positive prevalence
(~0.25 at 60–90), so ≈ 2.4x baseline — a decent model on a mis-specified question,
not a broken model. Do not frame this to stakeholders as "the model is weak".

## 3. Known contamination risks (verify before trusting results)

Note on `card block codes`: existing CC outflow features are anchored on the **block
date** (~60 DPD), which is downstream of the deterioration and is an operational rather
than customer event. See `feature_specs.md §3.0` — those features are reusable as an
*early-delinquency response* family; A4 needs them re-anchored to T0.

| Risk | Check | Consequence if real |
|---|---|---|
| **Restructure = account succession** (R13): the old CC/loan is closed and a new one opened. If closure posts a settlement-like credit, a restructure reads as **recovery** — inverted, since the debt moved rather than being repaid. The old→new link is not yet identifiable (O13) | T02 / T03 | Recovery and futility labels inflated on every restructured account; `payments()` must exclude succession postings (`feature_specs.md §1`); restructured customers are an A4 blind spot until T03/T04 lands |
| Card block codes fire after observation date, or are DPD-triggered operational actions | T06 | Leakage or self-fulfilling feature — drop or lag it |
| Bureau salary freshness inconsistent across rows (AECB dry at delinquency) | T06 | Feature means different things per row; model exploits the inconsistency |

## 4. What is missing (the actual gap)

Hundreds of features exist on the saturated state dimension; approximately zero on the
four orthogonal mechanism dimensions: locatability (A2), ability (A1), willingness
(A3), manner-of-deterioration (A4). Coverage reality (`domain_and_decisions.md §4`) says A4 is the only one
buildable for the whole book — hence the build order in `../TASKS.md`.
