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
| 2026-08-20 | **UC1 will deliver ability and willingness features from call transcripts.** A separate programme, not yet landed. Consequences: A1/A3 stay defined now so UC1 integrates into an existing schema rather than forcing a re-cut; A3's gate is *deferral*, not permanent block on DCORE PTP quality. Transcripts exist only for answered right-party calls, so **A2's `reachable` population is UC1's addressable book**, and UC1 can never cover the unreached — A4 remains the only axis with coverage there. Carry the selection discipline forward: transcript-derived willingness must not be trained as ground truth then applied to non-answering accounts | `domain_and_decisions §5`, T11 |
| 2026-08-20 | **Contact-attempt outcomes are recorded with a usable vocabulary**: call did not go through (dead channel) · ring, no answer (live channel, no pickup) · answered but no meaningful conversation · right-party contact · no reply to email. Richer than `feature_specs §4.1` assumed — enough to derive locatability states without field-visit labels | `feature_specs §4`, T12 |
| 2026-08-20 | **CC balance / utilisation / payment live in dedicated tables, not only transaction history.** So the A4 retention floor is **per source table**, not a single transaction-wide bound. Only the departure family (§3.3 — MCC, country codes) genuinely needs the transaction stream; payment-ratio and utilisation trajectories may reach further back than T02's answer implies | `feature_specs §3.0b`, T02 |
| 2026-08-20 | **Retail loan snapshot columns confirmed**: `payment_mtd`, principal outstanding, `emi` (month-end grain). Transaction-level loan data **can be sourced if needed**. Delinquency buckets must be reconstructed by parsing the snapshot series per account — no dedicated 24-month DPD history feature as on CC | `feature_specs §2`, R15, T25 |
| 2026-08-20 | **A2 is derived, not learned (S18).** States resolve from contact-outcome status × presence evidence (`feature_specs §4.0` matrix). `reachable` = right-party contact, directly observed. Field visits demoted from label source to **adjudicator of the one ambiguous cell** and validator of `gone` precision. Reason: visits are dispatched *because* contact already failed, so a model trained on visited accounts learns P(state \| features, already-failed-contact) and cannot be applied to the book — and `reachable` is near-absent from that sample. Removes A2's hard dependency on unverified visit coverage. Withdrew the 2026-08-19 two-stage proposal, which this subsumes | `feature_specs §4` (rewritten), T12, T13 |
| 2026-08-20 | **Three A2 guards are mandatory, not polish.** (a) `gone` only on a *positive* departure trail, never on absence — ~80% of the book is card-only and once blocked has no observable channel, so silence measures our blindness (`§4.4a`); (b) every contact signal attempt-normalised with `contact_attempts_n` emitted and `unknown` below a minimum — **uncontacted ≠ unreachable** (`§4.4b`); (c) an explicit labelling window — "recent" undefined silently mixes a state observed last week with one observed six months ago (`§4.4c`) | `feature_specs §4.4`, T12 |
| 2026-08-20 | **A2 ends at right-party pickup; what follows is A3.** "Answered but no meaningful conversation" is a willingness signal, not a locatability one. Keeps the axes orthogonal exactly where UC1 will operate | `feature_specs §4.5`, `personas.md §4` |
| 2026-08-20 | **`chronic_marginal` must evidence duration, not assert it.** Two of three conditions saw only the ~12-month window; only `fee_velocity_life` was lifetime. Recruit `prior_spell_cnt_24m` / `months_since_prior_spell` / `tenure_at_t0_m` (already in §3.4, unused by §3.5) plus a `w_pre_clean_m` floor. **Reason: a `gradual_spiral` that plateaued before `W_pre` opened falls through the ordered rules into `chronic_marginal`** — so the class an account receives depends on when the spiral started relative to our window, an artefact of the anchor. Honest ceiling: CC prior-spell history caps at 24 months, so the class can only mean *sustained across up to two years plus lifetime tenure and fee rate*. If the rule cannot carry that meaning, rename it | `feature_specs §3.5`, T07 |
| 2026-08-20 | **`abrupt_shock`'s zero-payment condition needs a dormancy check.** With `DELINQ_MIN = 2`, T0 is the *first* overdue month — so payments stopping two months earlier implies T0 should have been earlier. The condition is either redundant or fires on accounts where **nothing was due** (paid-ahead/dormant). Cross-tab against `months_at_code0_w12` at T07; add the not-dormant guard if enriched | `feature_specs §3.5`, T07 |
| 2026-08-20 | **A class label never ships without its provenance (S20).** Confidence value and `observed\|inferred` travel with any state reaching an agent-facing surface. Reason: the A4 names are *legible* enough to be over-read as diagnosed causes — an agent reading `abrupt_shock` as "this customer lost their job" carries an unearned assumption into a live negotiation. **Two opposite naming failures now recorded**: `skip` too opaque (reader cannot act, but *asks*), `abrupt_shock` too legible (nobody asks, unearned confidence propagates silently) | `personas.md §5`, `§3.5`, `§4.6` |
| 2026-08-20 | **Face validity is a T07 check distinct from the gates.** For each class: state what the name claims, then name the feature evidencing it; recruit one or rename. A class can pass PV3 and PV4 while being misnamed — the gates do not test naming, and a misnamed class misleads every downstream reader including the PV5 workshop | `personas.md §5`, T07 |
| 2026-08-20 | **New reference doc `personas.md`** — what an axis is and is not, state-by-state definitions for A4 and A2, the derivation matrix, naming discipline, the UC1 seam, and how the axes are consumed. Registered in `00_START_HERE.md`. Created because the specs defined states operationally without ever saying plainly what they meant | `reference/personas.md` |
| 2026-08-19 | **DPD bucket code is offset on CC.** `0` = nothing due, `1` = **due but not overdue** (ordinary revolver behaviour), `2` = **0–30 DPD, where delinquency starts**. Retail loans do not differentiate `0`/`1` — their `1` is already 0–30 DPD. So `DELINQ_MIN` = 2 for CC, 1 for loans; cure is a return *below* it, not to `0`. **"Non-zero" must never be used as the delinquency test** | `feature_specs.md §2`, T03b |
| 2026-08-19 | **Window arithmetic is in months, not days** — `[M0−12, M0)` via `F.add_months`/`F.months_between`, matching the existing pipelines. T0 is month-resolved, so day offsets were false precision, and a mid-month boundary makes the first/last monthly buckets partial, biasing every mean and slope. Onset month `M0` excluded. Day arithmetic stays for genuine elapsed-time features (`pay_dom_*`, `pay_gap_*_d`, `t0_to_block_days`) | `feature_specs.md §0` |
| 2026-08-19 | **`W_pre` is truncated and flagged, not assumed.** Cut at the latest of `T0−12m`, `prior_spell_end`, `account_open_date`, `retention_floor`; emit `w_pre_start`, `w_pre_clean_m`, `w_pre_contaminated_flag`, `w_pre_truncation_reason`. Slope features count *clean* months. Chosen over flag-only so a repeat delinquent's prior spell cannot masquerade as pre-delinquency behaviour | `feature_specs.md §3.0b`, T04b |
| 2026-08-16 | **Spine/scope pipelines exist for every model segment except retail loans 180+.** That segment needs an ad-hoc scope, labelled as such in the results `scope` field. Running its spine is deferred — CC leads, loans follow | `domain_and_decisions.md §4` |
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

*The 2026-08-20 design-review round has been **applied** — see "Decisions taken" above and
the `⚠ Revision round` table in `TASKS.md`. Items that were verification questions rather
than design changes became **O15–O18** in `domain_and_decisions.md §8` and were written into
the cards that will answer them (T02, T11, T12, T13, T25). Nothing is awaiting ratification.*

| Date | Proposal | Rationale |
|---|---|---|
| | | |
