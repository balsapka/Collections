# Domain, Decisions, Constraints

## 1. Business context

UAE bank, Group Retail Risk, delinquent retail collections. Stakeholder complaint: the
existing LightGBM scores "lack differentiation power". Diagnosis (evidence in `02`):
the model restates delinquency state the collections officer already sees, and one
score has been serving several distinct decisions. The programme answers this with
revised targets per segment plus supervised "persona" axes that carry mechanism
information (why collection is failing), not more magnitude information (how bad).

Division of labour: we ship axes, scores, and evidence. The business owns the action
mapping (which treatment per cell). Do not design collection strategies.

## 2. Products, source systems, and the segmentation that follows

**The primary split is the source system, not security.** Credit card and loan
accounts sit in different systems with different structures, so they need separate
feature pipelines and separate models (S15, R3) — this is an engineering boundary
before it is a modelling choice.

| Product | Source group | Secured | Notes |
|---|---|---|---|
| Credit card | **CC system** | No | Primary book; all measured base rates in §3 are CC |
| Auto | Loan system | **Yes** | The one sub-split that is *easy* within loans. Recovery = repossess/sell asset; persona axes mostly n/a (W8). Ijarah vs lien unknown (O3) |
| Personal loan | Loan system | No | Typically salary-transfer → income observed. Not cleanly separable from personal cash |
| Personal cash loan | Loan system | No | Not cleanly separable from personal loan |

Modelling units: **CC**, **loan-auto**, **loan-other**. Treat CC as the lead track
(largest measured book, thinnest data — see §4); build loan tracks by porting patterns
once the CC persona axes validate.

## 3. Segments and economics

| Segment | Size | Positive rate | Decision to support | Model |
|---|---|---|---|---|
| 60–180 DPD, unsecured | 1x | cure ~25% at 60–90, falls with depth | **Exclusion**: business works every account; model flags the futile few | B1 (futility), B2 (recovery) |
| 180+ CC, < 2y in bucket | part of a book ~10x the 60–180 | **5%** (per current 5%/1000 AED def.) | **Selection**: keep top X in-house, sell/agency the rest | B3 (hurdle) |
| 180+ CC, > 2y in bucket | large share of 180+ | **1–2%** | Bulk treatment; trigger monitoring blocked on data feed (O8) | B4 (blocked) |
| Auto, both bands | unmeasured (D1) | unknown | Repossession economics | B5 (gated on D1) |

Decision graph the outputs must serve:

```
can we reach them?
├─ yes → negotiate → settle / restructure / pressure   (ability + willingness)
└─ no  → why not?  → chase / field visit / agency / write off   (locatability)
```

Contactability is a gate upstream of scoring, not a feature inside it.

## 4. Data domain truths

| Domain | Grain | Coverage of delinquent CC book | Allowed use | Known issues |
|---|---|---|---|---|
| Credit card (account + txn) | account / event | 100% | Primary instrument for everything | Retention depth of transactions unverified (D9) |
| Financial transactions | event | 100% of card activity | A4 sequence/trajectory features | Same retention question (D9) |
| Retail loan | account | **~10–20%** also hold RL | Internal cross-product ability signal | Small overlap — never design as if universal |
| CASA | account / txn | partial (`<<FILL-IN share>>`) | Salary continuity (A1), EOSB signature | Missingness is informative AND a confound (S12 note) |
| AECB (bureau) | snapshot at credit decisions | pulls stop at delinquency | **Pre-T0 leverage trajectory only** (A4 input) | No live signal during delinquency (X9). PIT snapshot retention unknown (O7) |
| DCORE | event | delinquent book | PTP, contact attempts, dispositions, field visits | **Trust unresolved** — gate everything on D6 |
| Demographics | static | 100% | Controls only | Proxy risk for protected attributes (R7) |
| Digital / login | event | wherever app/web used | Engagement, foreign-login, channel-death signals | Coverage varies |

**Restructures create new accounts (R13).** A restructure closes the CC/loan and opens
a replacement. Consequences, all currently unmitigated because the old→new link is not
identifiable (O13):
- **Label risk:** if closure posts a credit that resembles settlement, a restructure
  reads as *recovery* in futility and hurdle labels — inverted, since the debt moved
  rather than being repaid. `payments()` must exclude it (`04 §1`).
- **Feature blind spot:** the new account has no pre-delinquency history, so A4 has
  nothing to anchor on for restructured customers.
- **Missed signal:** restructuring is strong evidence of *willingness* (the customer
  negotiated and re-committed) and needs no DCORE. Recovering the link partly rescues
  A3 from its DCORE dependency.
Whether the new account starts at DPD 0, lower, or the same bucket is not uniform and
not yet known (O14).

**Population fact that shapes everything:** roughly **80% of the delinquent CC book is
card-only** (no RL, often no CASA). For them the card's own transaction/payment stream
plus digital is the entire live instrument. Consequences: (a) squeeze the card stream
hard — A4 is the only axis with full coverage; (b) when using CASA/RL-derived features,
always include an explicit `relationship_breadth` feature so the model separates "has a
relationship with us" from the signal itself; (c) validate card-only estimates on the
10–20% where the truth is visible.

## 5. Settled decisions (S1–S17)

| ID | Decision |
|---|---|
| S1 | Two bands = two different products: 60–180 is an **exclusion tool**; 180+ (<2y) is a **shortlist generator**. Never one "risk score" spanning both (X8). |
| S2 | Targets: 60–180 primary = **futility** (zero/negligible payment over N months), secondary = expected recovery (hurdle). 180+ = **hurdle** with a small noise floor. The legacy roll target and the 5%/1000 AED rule remain as *reports*, not training targets. |
| S3 | Score names: `futility_60_180`, `exp_recovery_aed_60_180`, `exp_recovery_aed_180p_lt2y`. Direction per R5. |
| S4 | The 180+ keep/sell cutoff is **priced** (expected AED vs agency economics curve), never a chosen round number. Blocked on O1 for the final line, but the curve is built now. |
| S5 | The >2y cohort is **not scored from internal history** (stale by construction). Plan = bulk treatment now; trigger monitoring is a costed data-acquisition proposal (O8), not a build item. |
| S6 | Personas = **supervised mechanism axes**, never unsupervised clusters (X1). Axes: A2 locatability, A4 manner-of-deterioration (full coverage, build first); A1 ability and A3 willingness gated (D5, D6). Expected recovery is NOT an axis (X7). |
| S7 | Grid stays small: ~3 persona states × ~3 score bands, collapsing to ≤6 strategies. The **orthogonality gate** (W6) runs before any strategy is designed on the cells. |
| S8 | Every estimated axis ships `observed|inferred` + a validation number (R6). |
| S9 | Build order follows **DCORE dependency**: A4 (none) → A1/direct ability (low) → A2 (moderate, core-banking v1 first) → A3 (total, contingent). |
| S10 | Deterioration features are **event-anchored to T0** (spell start), never to calendar or observation date. Spell spec in `04`. |
| S11 | AECB is used **only** for the pre-T0 leverage trajectory. All live-signal uses rejected (X9). |
| S12 | Live ability signal comes from the **internal cross-product view** (other products current? salary landing?) where it exists (~10–20%); the card-only proxy (A1) covers the rest and must validate on the visible minority first. |
| S13 | "Synthesized features" is defined to stakeholders as **inferred latent state** (the axes), never generative/synthetic data (X5). |
| S14 | A permanent **random ~1% holdout** below the 180+ cutoff is required before deployment (R12). Raise with the business early — cannot be retrofitted. |
| S15 | **CC and loan accounts get separate feature pipelines and models** (different source systems/structures). Within loans, auto splits out; personal vs personal cash does not. Modelling units: CC, loan-auto, loan-other (R3). |
| S16 | **Persona axes are built and validated FIRST, independently of the risk models.** They must pass the four-gate ladder in `03 Phase P` — buildability, novelty, outcome separation, incremental lift — before any risk-model retrain depends on them. A4 and A2 are deliverables in their own right, not model inputs awaiting a model. |
| S17 | **Restructures are account successions, not DPD resets** (R13). Linkage discovery (W0) is a prerequisite for correct labels and for A4 coverage of restructured customers. |

## 6. Rejected approaches (X1–X10) — do not re-propose

| ID | Approach | Why rejected | Do instead |
|---|---|---|---|
| X1 | Unsupervised persona clustering | Cluster id is a lossy function of features the GBM already sees; adds no lift | Supervised axes (S6) |
| X2 | More/better delinquency-state features | That dimension is saturated (see `02` tautology evidence); marginal value ≈ 0 | Orthogonal families A2/A4 |
| X3 | Continuous recovery-rate regression at 180+ | 2–5% positive rate → spike-at-zero; regression predicts ~0 for all and scores well | Hurdle model (S2) |
| X4 | Capacity-constrained allocation optimisation | We don't own or see collections capacity; ranking + cutoff suffices | Priced cutoff curve (S4) |
| X5 | Synthetic data generation as differentiator | Cannot create information absent from the source | Synthesized = inferred state (S13) |
| X6 | Full causal / uplift modelling this cycle | Needs treatment-variation analysis there is no time for; officers assign actions non-randomly (confounding by indication) | Descriptive crosstab, labelled correlational (W6); revisit next cycle |
| X7 | Expected recovery amount as a persona axis | It IS the score; guarantees grid collinearity | Mechanism axes only |
| X8 | Single risk score across bands | Targets genuinely differ; produced the current complaint | S1/S3 |
| X9 | AECB as live delinquency signal | Pulls stop firing at 60+ DPD: no contemporaneous cross-lender status; absence ≠ gone; enquiry triggers need a feed we don't have | Pre-T0 leverage only (S11); internal cross-product for live ability (S12) |
| X10 | Pooled-AUC-inflation hypothesis (DPD buckets) | Tested and closed: within-bucket AUC ≈ pooled | The finer within-time-in-bucket version is still open → D2 |

## 7. Constraints

| ID | Constraint |
|---|---|
| C1 | **Shariah**: on Murabaha/Tawarruq the receivable is fixed sale debt; ibra' cannot be promised upfront. Concession menu differs by product and is owned by the Shariah board (O2). Never assume a discount is offerable. |
| C2 | **IFRS 9**: forbearance/restructure triggers stage migration; settlement books a loss. Affects how outputs are framed (prefer "cease effort" over "write off early" at 60–180). |
| C3 | **Protected attributes** (CBUAE/SAMA): R7. Inferred "left country" is the highest proxy risk — W6 check mandatory. |
| C4 | **Model risk**: outputs feeding provisioning/credit decisions carry full MRM burden; operational collections prioritisation is lighter. Sequence-encoder embeddings are features, not decisions, to stay in the lighter regime (W7). |

## 8. Open questions (O1–O12)

| ID | Question | Blocks | Owner |
|---|---|---|---|
| O1 | Agency commission / sale price by cohort; field visit unit cost | Final priced cutoff (S4); persona ROI framing | Business |
| O2 | Feasible action menu per product (post-Shariah) | Strategy mapping (business side) | Business |
| O3 | Auto structure: Ijarah (bank owns) vs lien | W8 target design | Business |
| O4 | Horizon N for futility (operational review cycle length) | W1 (default 3m, CONFIRM) | Business |
| O5 | "Negligible" threshold ε for futility | W1 (default min(100 AED, 0.5% outstanding), CONFIRM) | Business |
| O13 | **How is the old→new account link identifiable after a restructure?** Any explicit reference field, closure reason code, or DCORE record naming both accounts? | W0, W1 labels, W2/W3 coverage, A3 signal | User/IT/DCORE |
| O14 | Does the replacement account start at DPD 0, a lower bucket, or the same bucket? Is it uniform by product/policy? | W1 label semantics, W2 spell continuity | Collections/IT |
| O7 | Are historical AECB pulls retained point-in-time? | A4 leverage-trajectory feature | User |
| O8 | AECB ongoing-monitoring feed: permissible purpose + cost vs uplift at 1–2% base rate | B4 (trigger monitor) | Business/Compliance |
| O9 | Transaction retention depth: is T0−12m available per cohort? | D9 → A4 scope, W7 feasibility | User |
| O10 | Field-visit disposition codes: list + where stored | A2 labels (`04` mapping table) | User/DCORE |
| O11 | Card block code timing vs observation date | D10 → feature admissibility | User |
| O12 | Bureau salary field provenance (stale pull? consistent freshness?) | D10 → feature admissibility | User |
