# Work Plan

Statuses: `todo | in-progress | done | blocked | n/a`. Update the Status column when a
session completes something, and log numbers in `RESULTS.md`.

## Phase 0 — Diagnostics (D1–D10)

Cheap, mostly on existing scored outputs and label tables. Each has a decision rule so
the result is actionable without re-adjudication. Log every result in `RESULTS.md`,
and update the corresponding evidence line in `../problem_statement.md` (P1–P8) so the
stakeholder document stays current.

| ID | Question | Method | Decision rule | Effort | Status |
|---|---|---|---|---|---|
| D1 | Auto vs CC positive rate + recovery AED at 180+ | Group existing 180+ outcomes by product | Auto ≥ 2× CC rate → confirm separate auto track (W8); never pool | hours | todo |
| D2 | Does discrimination survive *within* time-in-bucket cohorts (<2y / >2y)? | Re-score existing 180+ model; AUC + capture@10 within each cohort | Within-cohort ≪ pooled → apparent skill was cohort membership; re-baseline all 180+ results within cohort | hours | todo |
| D3 | Recoverable AED by segment (band × product × cohort) | accounts × positive rate × avg recovered AED | Largest pool gets modelling priority; cite when stakeholders ask "why are you working on X" | hours | todo |
| D4 | Tautology test: state-only baseline | Model on ONLY days-since-last-payment + DPD velocity (+ missed EMIs), same split as full model | State-only ≥ ~95% of full model's capture@10 → current model is state restatement; this becomes the mandatory baseline for W5 | 0.5 day | todo |
| D5 | CASA-holder vs card-only performance split | Evaluate existing model separately on the two groups | Gap large → ability signal is real, business case for A1 (W9); gap ≈ 0 → deprioritise A1 | 0.5 day | todo |
| D6 | DCORE trustworthiness | (a) PTP-kept vs payments-table reconciliation; (b) coverage: % delinquent accounts with any DCORE record; (c) % dispositions ≠ generic/other | Agreement < ~90% or coverage < ~80% → DCORE fields untrusted: A3 blocked, A2 ships core-banking-only, crosstab (W6) deferred. Thresholds provisional — CONFIRM with user | 1–2 days | todo |
| D7 | Re-aging contamination | % of "moved back" outcomes preceded by a restructure event within ~30d | Material (> ~5%) → futility label must exclude/flag re-aged accounts (W1); current roll-model results caveated | 0.5 day | todo |
| D8 | Positive rate by balance band at 180+ | Group by outstanding-balance bands under current 5%/1000 target | Strong gradient → quantifies why W1 replaces the dual threshold; include in stakeholder material | hours | todo |
| D9 | Transaction retention: is [T0−12m, T0] available? | % accounts per segment/cohort with ≥ 12 full months of pre-T0 transactions | Low for a cohort → A4 unavailable there (consistent with S5 for >2y); low everywhere → shrink window to what exists, note in `RESULTS.md` | hours | todo |
| D10 | Feature admissibility: block-code timing; bureau salary provenance | Compare block event timestamps vs observation dates; distribution of bureau pull dates behind the salary field | Post-observation timestamps → leakage: drop/lag the feature in W5. Inconsistent pull freshness → recompute feature from last pre-T0 pull only | 0.5 day | todo |

## Phase 1 — Work items (W1–W9)

### W1 — Revised targets and labels  `[modifies existing label/modelling pipelines]`
Depends: D7 (re-aging flag). Spec: `04 §1`.
- Add label builders: `futility_60_180` (N months, ε floor), `recovery_aed_60_180`,
  and 180+ hurdle labels (`any_recovery_gt_floor`, `recovery_amount`). Params N, ε,
  floor from config with defaults marked CONFIRM (O4, O5).
- Keep roll labels and 5%/1000 labels running as reports (R11).
- **DoD:** label tables build; prevalence by segment logged in `RESULTS.md`; unit
  tests cover horizon boundaries, ε edge, re-aged handling; leakage test passes.

### W2 — Spell / T0 table  `[net-new DE asset, reusable]`
Depends: D7 (re-aging semantics), O6. Spec: `04 §2`.
- One table: contract × spell with T0, end, re-aged flag, spell metadata. The anchor
  for every A4 feature and for event-anchored windows generally.
- **DoD:** invariants tested (no overlapping spells per contract; DPD=0 outside
  spells modulo re-aging rule); spot-check sample validated; documented per the
  repo's docs conventions.

### W3 — A4: manner-of-deterioration features  `[net-new feature pipeline]`
Depends: W2; D9 for window depth. Spec: `04 §3`. **Highest-priority axis** — full
coverage of the card-only ~80%, zero DCORE dependency.
- Trajectory/periodicity/shape features over pre-T0 window; deterioration class v1
  (rules: abrupt_shock / gradual_spiral / chronic_marginal / mixed).
- Sequence encoder is NOT part of W3 (see W7 gate).
- **DoD:** feature table with full CC coverage; null-rate report; leakage tests
  (max feature timestamp ≤ T0); class separation shown — realised recovery/cure
  differs materially across classes within segment (target: extreme-class outcome
  ratio ≥ 1.5×, else iterate rules); logged in `RESULTS.md`.

### W4 — A2: locatability states  `[net-new feature pipeline + label table]`
Depends: D6 (DCORE tier), O10 (disposition codes). Spec: `04 §4`.
- v1 rules on core-banking signals (channel-death simultaneity, travel/foreign
  signature, post-T0 domestic activity). v2 supervised on field-visit disposition
  labels if D6/O10 allow. DCORE delivered/unanswered signals only as enhancement.
- **DoD:** state assigned to full delinquent book with confidence + `observed|inferred`;
  agreement vs held-out field-visit labels reported (v2) or face-validity table (v1).

### W5 — Retrain decision models per segment + reporting upgrade  `[modifies existing]`
Depends: W1; W3 (first retrain can precede W4). Models: B1/B2 (60–180), B3 (180+ <2y).
- Add A4 (then A2) features to existing LightGBM pipelines; train within segment (R3).
- Reporting additions: decile tables with capture@k accounts AND AED; precision@bottom
  decile for futility (with CI); calibration by decile; monthly stability; the two
  mandatory baselines (balance-only, D4 state-only).
- **DoD:** per-segment reports comparing new vs current vs baselines; improvement
  quantified on capture@k / precision@bottom (NOT AUC alone, R4); `RESULTS.md` updated.

### W6 — Deployment gates  `[new report artifacts + one business ask]`
Depends: W3/W4/W5 for the gates; O1 for the priced line.
- **Orthogonality gate (S7):** persona-state distribution within each score decile.
  Provisional rule: any decile with > ~80% one state → grid adds little there; review
  before strategy design.
- **Proxy check (R7/C3):** can a protected attribute be predicted from each axis
  output? High separability → compliance review before shipping. Especially A2 "gone".
- **Priced cutoff curve (S4):** expected-AED-by-decile vs agency economics line
  (placeholder line until O1).
- **Holdout proposal (S14):** one-pager for the business — ~1% random carve-out below
  the 180+ cutoff, permanent, measurement plan. Raise EARLY; blocks deployment (R12).
- **Descriptive crosstab (X6 fallback):** persona × score band × action taken ×
  outcome, headed with a correlational disclaimer. Gated on D6.

### W7 — Sequence encoder for A4  `[gated]`
Gate: W3 cheap features plateau — measurable headroom on B-model metrics remains AND
D9 shows event-level depth. Self-supervised (masked/next-event) GRU or small
transformer over pre-T0 transaction sequences; pretrain on the whole portfolio (not
just delinquents); output = embedding features into LightGBM (C4 keeps MRM light).
Always compare against W3 features; if no lift on capture@k, drop (R8).

### W8 — Auto / secured track  `[gated on D1, O3]`
Separate target and features: asset locatability, vehicle value vs outstanding (LTV),
export risk. Persona axes A1–A4 mostly n/a. Do not start before D1.

### W9 — A1 ability proxy + A3 willingness  `[gated]`
A1 gate: D5 shows a real gap. Train "active salary" on card+CASA customers with
universal features only; validate on held-out visible slice; ship with
`observed|inferred`. A3 gate: D6 passes. PTP kept/broken ratios, inbound contact,
post-contact payment; validated against cured-after-contact.

## Execution order — start here

1. **Start with D4 + D5** (existing scored outputs; fastest, and they can redirect
   everything downstream).
2. D1, D2, D3, D8 (segment economics) and D7, D9, D10 (data checks) in any order.
   D6 when DCORE access is arranged.
3. W1 targets (small change, existing pipelines) + W5's reporting upgrade (needed to
   measure everything after).
4. W2 spell table → W3 A4 features → W5 retrain with A4.
5. W4 A2 v1 → W5 retrain including A2 → W6 gates.
6. Raise the W6 holdout ask with the business **now** (it blocks deployment, not build).
7. W7/W8/W9 only through their gates.
