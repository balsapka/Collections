# Results Log

Append-only. Every session records what it measured, built, or decided here, so later
sessions do not re-run or re-litigate. Newest entries at the top of each section.
(Repo/pipeline inventory lives in the workplace repo's own docs — not here.)

## New assets manifest (R18 — the abandon path)

Every new file, pipeline, catalog entry and output table created by this programme.
Append as you create. Deleting everything listed here must return the repo and the
warehouse to their current behaviour.

**Isolation mechanism.** Code: dedicated module directory + dedicated catalog file, so
deletion is `rm -r` plus one file. Physical paths and warehouse tables: prefix
`crx_` — **CONFIRM the marker with the user before first use** (or adopt the repo's own
experimental-asset convention if one exists).

| Date | Type (file / pipeline / catalog entry / table) | Name or path | Created by | Notes |
|---|---|---|---|---|
| | | | | |

## Defects found in existing system (R19 — reported, NOT fixed)

Problems found in the running system during diagnostics. These are **not** repaired by
this programme — they are separate decisions for the user, with their own testing and
timing.

| Date | Found by | Defect | Impact if unfixed | Suggested owner |
|---|---|---|---|---|
| | | | | |

## Returned outputs (raw PROD results)

So no later session needs a re-run, and results can be re-interpreted if a decision
rule changes. Two forms depending on the return channel used:

- **Small results:** paste the raw output block below, keeping the scope line.
- **File hand-off:** record the path in `results/` — do not duplicate its contents.

| Date | Task | Channel | Location / block |
|---|---|---|---|
| | | | |

<details>
<summary>T## — &lt;task&gt; — run YYYY-MM-DD (pasted)</summary>

```
(paste the === T## OUTPUT START/END === block here)
```
</details>

## Diagnostics

| Date | ID | Headline result | Decision taken | Artifact |
|---|---|---|---|---|
| pre-plan | T01 | **Tautology confirmed.** A model using only delinquency features (all derived from the single 24-month DPD bucket history) performs *close enough* to the full model that the gap does not change behaviour in use. Uncapped, 2–3 features dominate SHAP (`days since last payment`, `dpd velocity 3m`); importance restrictions were needed to stop collapse onto them. | T01 CLOSED — do not re-run. Persona axes judged on **novelty** (T09), not incremental AUC. T10 baselines against the current production model. | user's prior testing |

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
| 2026-08-16 | **Portfolio-level aggregates may be stored in the repo** — results files under `results/` are approved. Row-level/customer-identifiable data remains prohibited | `results/README.md` |
| 2026-08-16 | Existing CC outflow features are anchored on **card block date** (~60 DPD). Re-anchor to T0 for A4; retain block-anchored originals as a distinct `W_early` (early-delinquency response) family — reuse, do not rebuild | `reference/feature_specs.md §3.0` |
| 2026-08-16 | CC has a ready-made **24-month DPD bucket history** feature → near-free spell/T0 derivation (with a 24-month censoring limit and monthly resolution). Loans have no equivalent; buckets must be reconstructed | `reference/feature_specs.md §2` |
| 2026-08-16 | **Loans are month-end snapshot only** — payment behaviour partly derivable, payment timing not. T25 decides whether to trigger granular data sourcing | `00 R15`, T25 |
| 2026-08-16 | **Ready-made departure/travel features exist** from internal retail use cases (CASA + product holdings). Reuse via T06, do not rebuild | `00 R14`, T06 |
| 2026-08-16 | Reuse-before-build is a hard rule; T01 produces the reuse map before any feature build | `00 R14` |
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
