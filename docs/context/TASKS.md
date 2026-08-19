# Task Queue

One task per session. **Take T01 first, then work down** — the numbering is the
execution order. Otherwise take the task the user names, or the first `todo` whose
dependencies are `done`. Update `Status` here and append results to `RESULTS.md`.

**UAT has no data access (R16).** Most tasks run in two legs: emit a PROD snippet, then
interpret the output the user returns (pasted, or via a results file pulled from PROD).
`in-progress` means the snippet is out and awaiting results. See
`reference/snippet_contract.md`.

**Additive only (R18).** New assets beside the existing ones, never modifications.
Record everything created in the `RESULTS.md` manifest.

Status: `todo | in-progress (snippet out) | done | blocked | dropped | n/a`

---

## Track A — Persona axes  ·  THE PRIORITY

This is the part that decides whether the whole approach works. The axes must carry
information the current model does not (T09 is where that is settled). Track B can
proceed in parallel — it does not block this.

| ID | Task | Depends | Round trip? | Status |
|---|---|---|---|---|
| T01 | [**Feature inventory & reuse map**](tasks/T01_feature_inventory.md) — what already exists vs what A4/A2 need (R14) | — | **No — UAT only** | todo |
| T02 | [Transaction retention depth](tasks/T02_transaction_retention.md) — is `[T0−12m, T0]` available? Sets the A4 window | — | Yes — **fire early**, runs while T03 is built | todo |
| T03 | [Spell / T0 table (CC)](tasks/T03_spell_table.md) — the anchor for every A4 feature | T01 | Yes (validation) | todo |
| T04 | [A4 — payment & balance trajectory](tasks/T04_a4_payment_features.md) | T03, T02, T01 | Yes (validation) | todo |
| T05 | [A4 — utilisation, spend, liquidity](tasks/T05_a4_spend_features.md) | T03, T02, T01 | Yes (validation) | todo |
| T06 | [A4 — departure & history shape](tasks/T06_a4_departure_history.md) — **search `wealth_management` / `retail.feature_space` first, derive only the gaps** | T03, T01 | Yes (validation) | todo |
| T07 | [A4 deterioration class v1](tasks/T07_a4_class_rules.md) | T04, T05, T06 | Yes | todo |
| T08 | [A4 gate PV1+PV3 — buildability & outcome separation](tasks/T08_a4_pv1_pv3.md) | T07 | Yes | todo |
| T09 | [**A4 gate PV2 — novelty**](tasks/T09_a4_pv2_novelty.md) — *the decisive gate* | T07 | Yes | todo |
| T10 | [A4 gate PV4 — incremental lift](tasks/T10_a4_pv4_lift.md) | T09 | Yes | todo |
| T11 | [DCORE trust assessment](tasks/T11_dcore_trust.md) — gates T13 and the willingness axis | — | Yes — fire before T12 | todo |
| T12 | [A2 locatability v1](tasks/T12_a2_locatability_v1.md) | T03, T01, T06 | Yes (validation) | todo |
| T13 | [A2 supervised v2](tasks/T13_a2_supervised.md) — gated on T11 | T12, T11 | Yes | todo |
| T14 | [A2 gates PV1–PV4](tasks/T14_a2_gates.md) | T12 (or T13) | Yes | todo |
| T15 | [Proxy check on shipped axes](tasks/T15_proxy_check.md) — R7/compliance, before anything ships | T08, T14 | Yes | todo |
| T16 | [PV5 action-distinctness workshop pack](tasks/T16_pv5_workshop_pack.md) — assemble the materials; the session itself is a business meeting | T08, T14 | No | todo |

**If T09 fails**, stop and re-plan before continuing to T10–T16. An axis that
reproduces the 24-month DPD string will fail in exactly the way the current score
fails, and no amount of downstream work fixes that.

---

## Track B — Targets & risk models  ·  parallel, independent of Track A

| ID | Task | Depends | Round trip? | Status |
|---|---|---|---|---|
| T17 | [Restructure volume & label contamination](tasks/T17_restructure_contamination.md) — may affect figures already reported | — | Yes | todo |
| T18 | [Succession link — explicit](tasks/T18_succession_link_explicit.md) | T17 | Yes | todo |
| T19 | [Succession link — heuristic](tasks/T19_succession_link_heuristic.md) — only if T18 finds nothing | T18 | Yes | todo |
| T20 | [Revised labels](tasks/T20_revised_labels.md) — futility + hurdle, succession-safe, **new table** | T17 | Yes (validation) | todo |
| T21 | [Feature admissibility](tasks/T21_feature_admissibility.md) — block-code timing, bureau salary provenance | — | Yes | todo |

Track B enhances Track A but does not block it: T03 can derive spells without the
succession link (set `inherited_history_flag = 0` and accept the blind spot), and
refine later once T18/T19 lands.

---

## Track C — Supporting diagnostics  ·  when convenient

| ID | Task | Depends | Round trip? | Status |
|---|---|---|---|---|
| T22 | [Segment economics](tasks/T22_segment_economics.md) — rates, recoverable AED, balance-band gradient | — | Yes | todo |
| T23 | [Within-cohort discrimination](tasks/T23_within_cohort_auc.md) — does 180+ skill survive inside <2y / >2y? | — | Yes | todo |
| T24 | [CASA vs card-only split](tasks/T24_casa_vs_cardonly.md) — is the ability signal (A1) worth building? | — | Yes | todo |
| T25 | [Loan monthly-grain feasibility](tasks/T25_loan_grain_feasibility.md) — **fire early if T22 shows loans matter**; data sourcing has lead time | T01 | Yes | todo |

---

## Closed before this plan

The **state-only baseline** was already run by the user: a model built only from the
24-month DPD history performs close enough to the full model, and 2–3 features dominate
SHAP unless importance is capped. The tautology is confirmed — no task needed. See
`reference/current_state.md §2`.

## Later — not yet carded

Expand into cards when reached; earlier results may redirect them.

- **A4 for loans** — a distinct monthly-grain feature set (T25 decides its shape), not
  a port of the CC one
- Retrain decision models per segment + reporting upgrade (needs T20 + axes past T10)
- Orthogonality gate: persona mix within score deciles
- Priced cutoff curve; holdout proposal; descriptive crosstab
- Sequence encoder for A4 (gated on T04–T07 plateauing with headroom + T02)
- Auto / secured track (gated on T22)
- A1 ability proxy (gated on T24) and A3 willingness (gated on T11 + T18/T19)

See `reference/roadmap.md` for why these exist and what gates them.

## Standing ask (not a coding task)

Raise the permanent ~1% random holdout below the 180+ cutoff with the business
**now** — it blocks deployment, not build, and cannot be retrofitted (R12).
