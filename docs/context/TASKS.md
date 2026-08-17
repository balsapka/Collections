# Task Queue

One task per session. Take the task the user names, or the first `todo` whose
dependencies are `done`. Update `Status` here and append results to `RESULTS.md`.

Status: `todo | in-progress | done | blocked | dropped | n/a`

## Phase 0 — Diagnostics and inventory (read-only)

| ID | Task | Depends | Status |
|---|---|---|---|
| T01 | [State-only baseline](tasks/T01_state_only_baseline.md) — **CLOSED, do not re-run.** Tautology confirmed by prior testing | — | done |
| T02 | [Restructure volume & label contamination](tasks/T02_restructure_contamination.md) | — | todo |
| T03 | [Succession link — explicit](tasks/T03_succession_link_explicit.md) — is old→new account recorded anywhere? | T02 | todo |
| T04 | [Succession link — heuristic](tasks/T04_succession_link_heuristic.md) — only if T03 finds nothing | T03 | todo |
| T05 | [Transaction retention depth](tasks/T05_transaction_retention.md) — is [T0−12m, T0] available? | — | todo |
| T06 | [Feature admissibility](tasks/T06_feature_admissibility.md) — block-code timing, bureau salary provenance | — | todo |
| T07 | [Segment economics](tasks/T07_segment_economics.md) — rates, recoverable AED, balance-band gradient | — | todo |
| T08 | [Within-cohort discrimination](tasks/T08_within_cohort_auc.md) — does skill survive inside <2y / >2y? | — | todo |
| T09 | [CASA vs card-only split](tasks/T09_casa_vs_cardonly.md) — what is the ability signal worth? | — | todo |
| T10 | [DCORE trust assessment](tasks/T10_dcore_trust.md) — PTP reconciliation, coverage, code discipline | — | todo |
| T11 | [**Feature inventory & reuse map**](tasks/T11_feature_inventory.md) — what already exists vs what A4/A2 need (R14). **Do before any build task.** | — | todo |
| T12 | [Loan monthly-grain feasibility](tasks/T12_loan_grain_feasibility.md) — what payment behaviour is derivable from month-end snapshots + CASA; does data sourcing need triggering? | T11 | todo |

## Phase P — Persona axes (lead phase; independent of the risk models)

CC leads. Loan A4 is a **different feature set**, not a port (R15) — carded after CC
axes clear their gates.

| ID | Task | Depends | Status |
|---|---|---|---|
| T13 | [Spell / T0 table (CC)](tasks/T13_spell_table.md) | T02, T03/T04, T11 | todo |
| T14 | [A4 CC — payment & balance trajectory](tasks/T14_a4_payment_features.md) | T13, T05, T11 | todo |
| T15 | [A4 CC — utilisation, spend, liquidity](tasks/T15_a4_spend_features.md) | T13, T05, T11 | todo |
| T16 | [A4 — departure & history shape](tasks/T16_a4_departure_history.md) — **reuse ready-made retail features** | T13, T11 | todo |
| T17 | [A4 deterioration class v1](tasks/T17_a4_class_rules.md) | T14, T15, T16 | todo |
| T18 | [A4 gate PV1+PV3 — buildability & outcome separation](tasks/T18_a4_pv1_pv3.md) | T17 | todo |
| T19 | [A4 gate PV2 — novelty (critical gate)](tasks/T19_a4_pv2_novelty.md) | T17, T01 | todo |
| T20 | [A4 gate PV4 — incremental lift](tasks/T20_a4_pv4_lift.md) | T19, T01 | todo |
| T21 | [A2 locatability v1](tasks/T21_a2_locatability_v1.md) — reuse sourced departure features | T13, T11, T16 | todo |
| T22 | [A2 supervised v2](tasks/T22_a2_supervised.md) — gated on T10 | T21, T10 | todo |
| T23 | [A2 gates PV1–PV4](tasks/T23_a2_gates.md) | T21 (or T22) | todo |
| T24 | [Proxy check on shipped axes](tasks/T24_proxy_check.md) — R7/compliance | T18, T23 | todo |
| T25 | PV5 action-distinctness workshop — business session, not a coding task | T18, T23 | todo |

## Phase 1 — Targets (independent of Phase P; can interleave)

| ID | Task | Depends | Status |
|---|---|---|---|
| T26 | [Revised labels](tasks/T26_revised_labels.md) — futility + hurdle, succession-safe | T02 | todo |

## Later — not yet carded

Expand into cards when reached; early results may redirect these.

- **A4 for loans** — a distinct monthly-grain feature set (T12 decides its shape), not
  a port of the CC one
- Retrain decision models per segment + reporting upgrade (needs T26 + axes past PV4)
- Orthogonality gate: persona mix within score deciles
- Priced cutoff curve; holdout proposal; descriptive crosstab
- Sequence encoder for A4 (gated on T14–T17 plateauing with headroom + T05)
- Auto / secured track (gated on T07)
- A1 ability proxy (gated on T09) and A3 willingness (gated on T10 + T03/T04)

See `reference/roadmap.md` for why these exist and what gates them.

## Standing ask (not a coding task)

Raise the permanent ~1% random holdout below the 180+ cutoff with the business
**now** — it blocks deployment, not build, and cannot be retrofitted (R12).
