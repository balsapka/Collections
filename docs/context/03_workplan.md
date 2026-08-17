# Work Plan

Statuses: `todo | in-progress | done | blocked | n/a`. Update the Status column when a
session completes something, and log numbers in `RESULTS.md`.

**Priority (S16): the persona axes come first and are validated on their own merits.**
They are deliverables in their own right, not inputs waiting on a risk model. Phase P
answers "does the persona angle work?" without touching the risk models. Only after
Phase P gates pass does persona work feed the model track (Phase 2).

Scope note (R3/S15): the lead track is **CC**. Loan tracks (`loan-auto`, `loan-other`)
are separate pipelines and follow by porting patterns once the CC axes validate.

---

## Phase 0 — Prerequisites and diagnostics

Cheap, mostly on existing scored outputs and label tables. Each has a decision rule so
the result is actionable without re-adjudication. Log every result in `RESULTS.md`, and
update the matching evidence line in `../problem_statement.md` (P1–P8).

### W0 — Account succession linkage  `[prerequisite, net-new]`
Depends: O13, O14. Spec: `04 §6`. **Blocks correct labels (W1) and A4 coverage (W3).**
- Measure restructure volume first — if it is a trivial share of the book, cap effort
  and record the blind spot instead of solving it.
- Discover the link: explicit reference field or closure reason code if one exists;
  otherwise heuristic record linkage (same CIF, close/open date proximity, balance
  correspondence), validated against any subset with an explicit link.
- **DoD:** succession table `(old_account_id, new_account_id, link_method, confidence)`;
  precision/recall vs the explicit-link subset; restructure share of book logged; if
  linkage proves infeasible, record it as an accepted limitation with its size.

| ID | Question | Method | Decision rule | Effort | Status |
|---|---|---|---|---|---|
| D7 | Restructure volume + label contamination | % of accounts closed into a successor; do closure postings resemble settlement credits? | Any material share → `payments()` must exclude succession postings (`04 §1`); current recovery/cure results caveated | 0.5 day | todo |
| D9 | Transaction retention: is [T0−12m, T0] available? | % accounts per segment with ≥ 12 full months pre-T0 | Low for a cohort → A4 unavailable there; low everywhere → shrink window to what exists and log | hours | todo |
| D10 | Feature admissibility: block-code timing; bureau salary provenance | Block event timestamps vs observation dates; distribution of pull dates behind the salary field | Post-observation timestamps → drop/lag. Inconsistent pull freshness → recompute from last pre-T0 pull only | 0.5 day | todo |
| D6 | DCORE trustworthiness | (a) PTP-kept vs payments reconciliation; (b) coverage: % delinquent accounts with any record; (c) % dispositions ≠ generic | Agreement < ~90% or coverage < ~80% → A3 blocked, A2 ships core-banking-only, crosstab deferred. Thresholds provisional — CONFIRM | 1–2 days | todo |
| D1 | Auto vs CC vs loan-other positive rate + recovery AED at 180+ | Group existing 180+ outcomes by modelling unit | Confirms the S15 split empirically and sizes each track | hours | todo |
| D2 | Discrimination *within* time-in-bucket cohorts (<2y / >2y) | Re-score existing 180+ model; AUC + capture@10 within each | Within-cohort ≪ pooled → apparent skill was cohort membership; re-baseline within cohort | hours | todo |
| D3 | Recoverable AED by segment (unit × band × cohort) | accounts × positive rate × avg recovered AED | Largest pool gets priority; cite when asked "why work on X" | hours | todo |
| D4 | Tautology test: state-only baseline | Model on ONLY days-since-last-payment + DPD velocity (+ missed EMIs), same split | State-only ≥ ~95% of full capture@10 → current model is state restatement. **This baseline becomes the reference for PV2/PV4 and W5** | 0.5 day | todo |
| D5 | CASA-holder vs card-only performance split | Evaluate existing model on the two groups | Gap large → ability signal real, A1 justified (W9); gap ≈ 0 → deprioritise A1 | 0.5 day | todo |
| D8 | Positive rate by balance band at 180+ | Group by outstanding bands under the current 5%/1000 target | Strong gradient → quantifies why W1 replaces the dual threshold | hours | todo |

**Do D4 first** — Phase P's novelty and lift gates are defined against it.

---

## Phase P — Persona axes (lead phase, independent of risk models)

### W2 — Spell / T0 table  `[net-new DE asset, reusable]`
Depends: W0 (succession), O14. Spec: `04 §2`. Anchor for all A4 features.
- **DoD:** invariants tested (non-overlapping spells per account; DPD=0 outside spells);
  successor accounts carry `predecessor_account_id` and `inherited_history_flag` where
  W0 provides a link; spot-check validated.

### W3 — A4: manner-of-deterioration  `[net-new feature pipeline]` — HIGHEST PRIORITY AXIS
Depends: W2; D9 for window depth. Spec: `04 §3`.
Full coverage of the card-only ~80%, zero DCORE dependency, and the only axis with
evidence it already works (`lifetime fee velocity`, `02 §2`).
- Trajectory / periodicity / shape features over the pre-T0 window; deterioration class
  v1 by rules (abrupt_shock / gradual_spiral / chronic_marginal / mixed).
- Sequence encoder is NOT in scope here (W7 gate).
- **DoD:** feature table with full CC coverage; null-rate report; T0-boundary leakage
  tests; passes PV1–PV4.

### W4 — A2: locatability states  `[net-new feature pipeline + label table]`
Depends: D6 (DCORE tier), O10 (disposition codes). Spec: `04 §4`.
- v1 rules on core-banking signals; v2 supervised on field-visit dispositions if D6/O10
  allow. DCORE delivery/disposition signals are enhancement only.
- **DoD:** state assigned across the delinquent book with confidence +
  `observed|inferred`; agreement vs held-out field-visit labels (v2) or face-validity
  table (v1); passes PV1–PV4.

### Phase P gates — the persona validation ladder (PV1–PV5)

Run per axis, per modelling unit. **These answer "is the persona angle working?"** and
require no risk-model changes. Log every number in `RESULTS.md`.

| ID | Gate | Method | Pass rule |
|---|---|---|---|
| PV1 | **Buildability** | Coverage, null rates, class distribution by segment | Axis computable for ≥ ~80% of the segment; no class < ~5% or > ~60% of volume (else rules need work). `mixed` > ~50% → iterate before proceeding |
| PV2 | **Novelty** | Predict the axis output *from the existing state feature set* (the D4 features plus current production features) | If state features predict the axis well (e.g. multiclass accuracy near the achievable ceiling / AUC ≳ 0.85 for a binary axis), the axis is a **repackaging — fail and revise**. This is the persona analogue of the tautology test and the most important gate |
| PV3 | **Outcome separation** | Realised cure / recovery rate and recovery AED by axis class, within segment | Extreme-class outcome ratio ≥ ~1.5×, monotone where the axis implies an ordering, stable across at least two time periods |
| PV4 | **Incremental lift** | D4 state-only baseline vs D4 + axis, same split | Material gain on capture@10 (accounts and AED) and, for 60–180, precision@bottom-decile. No gain → the axis does not ship as a model input (it may still ship as a segmentation if PV3 and PV5 hold) |
| PV5 | **Action distinctness** | Business workshop: do the classes imply *different* actions? | Stakeholders can name a distinct action per class. If two classes map to the same action, collapse them (S7 keeps the grid small) |

**Gate outcome recorded per axis** in `RESULTS.md` as pass/fail with the numbers. An
axis failing PV2 must be revised or dropped — do not carry it into Phase 2.

### W6a — Orthogonality gate vs the score  `[after Phase P and a Phase 2 retrain]`
Persona-state distribution within each score decile (S7). Provisional rule: any decile
> ~80% one state → the grid adds little there. Blocks strategy design on the cells.

### W6b — Proxy check  `[R7/C3, before any axis ships]`
Can a protected attribute be predicted from each axis output? High separability →
compliance review first. Highest risk: A2 `gone`.

---

## Phase 1 — Targets (can run in parallel with Phase P)

### W1 — Revised targets and labels  `[modifies existing label pipelines]`
Depends: W0/D7 (succession postings must be excluded). Spec: `04 §1`.
- Add `futility_60_180` (N months, ε floor), `recovery_aed_60_180`, and the 180+ hurdle
  labels. Params from config with CONFIRM defaults (O4, O5).
- Keep roll and 5%/1000 labels running as reports (R11).
- **DoD:** prevalence by segment logged; unit tests for horizon boundaries, ε edge, and
  succession-posting exclusion; leakage tests pass.

---

## Phase 2 — Decision models (after Phase P gates)

### W5 — Retrain per segment + reporting upgrade  `[modifies existing]`
Depends: W1; axes that passed PV4. Models B1/B2 (60–180), B3 (180+ <2y), per modelling
unit (R3).
- Reporting additions: decile tables with capture@k accounts AND AED;
  precision@bottom-decile for futility with CI; calibration by decile; monthly
  stability; the two mandatory baselines (balance-only, D4 state-only).
- **DoD:** per-segment comparison of new vs current vs baselines, on capture@k /
  precision@bottom — never AUC alone (R4).

### W6c — Deployment artifacts
Priced cutoff curve (S4, needs O1); holdout proposal one-pager (S14/R12 — raise EARLY,
blocks deployment not build); descriptive crosstab (X6 fallback, gated on D6, headed
with a correlational disclaimer).

---

## Phase 3 — Gated extensions

- **W7 — Sequence encoder for A4.** Gate: W3 cheap features plateau with measurable
  headroom AND D9 shows event-level depth. Self-supervised over pre-T0 sequences,
  pretrained on the whole portfolio; embeddings feed LightGBM (C4 keeps MRM light).
  No lift on capture@k → drop (R8).
- **W8 — Auto / secured track.** Gate: D1. Asset locatability, LTV at default, export
  risk; persona axes mostly n/a.
- **W9 — A1 ability proxy + A3 willingness.** A1 gate: D5 shows a real gap. A3 gate:
  D6 passes — **plus** W0, since restructure participation is a strong DCORE-free
  willingness signal (`01 §4`).
- **Loan tracks.** Port CC patterns to `loan-other` once CC axes clear Phase P.

---

## Execution order — start here

1. **D4** (state-only baseline — everything in Phase P is measured against it), then
   **D7 + W0** (succession: blocks correct labels and A4 coverage).
2. **D9, D10, D6** (data checks), and **D1, D2, D3, D5, D8** (segment economics) as
   access allows.
3. **W2 spell/T0 table** → **W3 A4 features** → run **PV1–PV4 for A4**.
4. **W4 A2 v1** → run **PV1–PV4 for A2**. Run **W6b proxy check** on both.
5. **PV5 workshop** with the business on whichever axes passed — this is the real test
   of the persona angle, and it needs stakeholders in a room.
6. **W1 labels** in parallel with 3–4 (independent of the axes).
7. Only then **Phase 2** (W5 retrain, W6a orthogonality, W6c artifacts).
8. Raise the **W6c holdout ask** with the business now — it blocks deployment, not
   build, and cannot be retrofitted.
9. Phase 3 items strictly through their gates.
