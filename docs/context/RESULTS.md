# Results Log

Append-only. Every session records what it measured, built, or decided here, so later
sessions do not re-run or re-litigate. Newest entries at the top of each section.
(Repo/pipeline inventory lives in the workplace repo's own docs — not here.)

## Diagnostics

| Date | ID | Headline result | Decision taken | Artifact |
|---|---|---|---|---|
| pre-plan | T01 | **Tautology confirmed.** A model using only delinquency features (all derived from the single 24-month DPD bucket history) performs *close enough* to the full model that the gap does not change behaviour in use. Uncapped, 2–3 features dominate SHAP (`days since last payment`, `dpd velocity 3m`); importance restrictions were needed to stop collapse onto them. | T01 CLOSED — do not re-run. Persona axes judged on **novelty** (T19), not incremental AUC. T20 baselines against the current production model. | user's prior testing |

## Model runs

| Date | Segment | Change | capture@10 (acct / AED) | precision@bottom | vs baseline | Artifact |
|---|---|---|---|---|---|---|
| | | | | | | |

## Persona gate outcomes (PV1–PV5)

| Date | Axis | Unit | PV1 | PV2 | PV3 | PV4 | PV5 | Verdict |
|---|---|---|---|---|---|---|---|---|
| | | | | | | | | |

## Decisions taken (user-ratified)

| Date | Decision | Ref |
|---|---|---|
| 2026-08-16 | Existing CC outflow features are anchored on **card block date** (~60 DPD). Re-anchor to T0 for A4; retain block-anchored originals as a distinct `W_early` (early-delinquency response) family — reuse, do not rebuild | `reference/feature_specs.md §3.0` |
| 2026-08-16 | CC has a ready-made **24-month DPD bucket history** feature → near-free spell/T0 derivation (with a 24-month censoring limit and monthly resolution). Loans have no equivalent; buckets must be reconstructed | `reference/feature_specs.md §2` |
| 2026-08-16 | **Loans are month-end snapshot only** — payment behaviour partly derivable, payment timing not. T12 decides whether to trigger granular data sourcing | `00 R15`, T12 |
| 2026-08-16 | **Ready-made departure/travel features exist** from internal retail use cases (CASA + product holdings). Reuse via T16, do not rebuild | `00 R14`, T16 |
| 2026-08-16 | Reuse-before-build is a hard rule; T11 produces the reuse map before any feature build | `00 R14` |
| 2026-08-16 | Restructured into task cards: one small task per session, minimal context load | `00`, `TASKS.md` |
| 2026-08-16 | Persona axes prioritised ahead of and independent of risk models; PV1–PV5 ladder (S16) | `reference/roadmap.md` |
| 2026-08-16 | CC and loan accounts get separate pipelines/models — different source systems (S15). Units: CC / loan-auto / loan-other | `reference/domain_and_decisions.md §2` |
| 2026-08-16 | Restructure = account closure + new account, NOT a DPD reset (S17/R13). Succession linkage is a prerequisite for labels and A4 | `reference/feature_specs.md §6` |
| 2026-08-16 | Leakage already controlled across the current modelling spectrum; R2 is maintain-not-build | `00 R2` |
| 2026-08-16 | Context pack created; S1–S17 / X1–X10 ratified as of this date | `reference/domain_and_decisions.md` |

## Proposed amendments (awaiting user)

| Date | Proposal | Rationale |
|---|---|---|
| | | |
