# crx_persona — design review and refactor proposal

Status: **D2–D6 decided 2026-10-23 (§6); D1 answered by the R4 grep (2026-10-27): no consumers outside the persona code.** Nothing is changed yet.
Scope: every persona axis in the mirror except A3 (DE-owned). Builds on the findings
O1–O41 in `REVIEW_OBSERVATIONS.md`.

## 1. What the code looks like today

| Area | Packages | Lines | Docstring + comment share |
|---|---|---|---|
| Foundation (spine, spells, full history) | `cc_spell`, `cc_full_history`, `rl_spell_table`, `rl_full_history`, `rl_a4_spine`, `_spine_utils` | ~1,060 | ~30% |
| CC feature tables | `cc_raw_extract`, `cc_payment_trajectory`, `cc_utilisation` | ~1,740 | ~34% |
| Departure signature | `cc_departure_signature`, `rl_departure_signature` | ~3,770 | ~29% |
| A1 ability | `cc_a1_ability` (v1), `cc_a1_ability_v2`, `rl_a1_ability`, `scoring_engine` | ~5,430 | ~34% |
| A2 locatability | `cc_a2_locatability`, `rl_a2_locatability` | ~2,060 | ~37% |
| A4 deterioration | `_dpd_journey`, `cc_a4_deterioration`, `rl_a4_deterioration` | ~1,460 | ~25% |
| **Total** | 19 packages | **~15,500** | **~33%** |

Who reads what (pipeline inputs):

```
cc_spine ─► cc_spell ─► cc_raw_extract ─► cc_payment_trajectory ─► cc_utilisation
                │                               │                       │
                ├──────────► cc_departure_signature (12 passes) ◄───────┘ (A1 v1 only)
                │                     │  4 of ~30 columns
                ├──────────► cc_a2_locatability ◄─┘
cc_spine ─────────────────► cc_a1_ability_v2   (reads no crx_ table at all)
cc_spine ─► cc_full_history ─► cc_a4_deterioration
rl_spine ─► rl_full_history ─► rl_spell_table ─► rl_a4_spine ─► rl_a1_ability, rl_a2_locatability
                    └─► rl_a4_deterioration         rl_departure_signature ─┘
```

The A4 engine (`_dpd_journey`) is the one place that already has the target shape: one
product-agnostic engine, a `BucketScheme` per product, thin CC/RL wrappers. The rest grew
ticket by ticket, CC first, RL copied from it.

## 2. Cross-cutting problems

**P1 — Docstrings are a changelog.** `rl_a1_ability/nodes.py` opens with ~140 lines of ticket
history (RL-A1-5 … RL-A1-23: what was added, removed, renamed, rejected). Similar in v1, A2,
departure. Readers have to dig for what the code does *now*; much of it is already wrong
(O12, O35, O41). → Docstrings state contract and reasoning; history lives in git and
`RESULTS*.md`.

**P2 — Two opposite input-failure policies.** ~35 schema guards return `None` and ~26 call sites
stub the columns with NULL, so a renamed source column silently turns a feature off (O14 is
exactly this). RL A1 already switched to fail-loud (`join_required_signals`). → One rule:
required inputs raise; genuinely optional sources (not yet materialised) are explicit
`Optional` parameters. One helper, `require_columns(df, cols, name)`.

**P3 — Logging is the slowest part of several nodes.** ~65 `.count()` / `.collect()` calls in
node code, two `persist()` in total. Each count recomputes the node's full lineage (O20);
`rl_departure_signature` alone runs 16 extra jobs. → One opt-in `log_stats` param (pattern
already in `rl_full_history`), one aggregate job per node, after `persist`.

**P4 — Spine↔spell join implemented three times, all wrong in a different way.**
`join_spine_to_spell` drops rows (O22), `build_rl_depart_spine` keeps only the still-open
spell (O26 — leaks the outcome), A1 v1 dedups to spell grain afterwards. → One
`attach_covering_spell(spine, spells)`: the spell whose `[t0, spell_end)` covers the
observation date, as of that date, left join, never drops a row.

**P5 — The "observation base" is rebuilt per axis.** CC resolves `contract → client → cif`
separately in A1 v1, A1 v2 and A2 (and the departure signature); RL gets `cif_id` from the
spine but routes it through `crx_rl_a4_spine`. → One dataset per product,
`crx_{cc|rl}_obs_base` = `(account_id, observation_date, cif_id, spell_id, t0)`, built once,
read by every axis.

**P6 — Point-in-time lookups are hand-written ~25 times.** The same `row_number` over
`partitionBy(grain).orderBy(date desc)` with a `< anchor` (sometimes `<=`, O40) filter and,
mostly, no staleness bound (O24, O36); window sums `[anchor − 90d, anchor)` ~15 times; source
partition floors computed per node from `persona_start` and often too late (O27, O33, O37).
→ Two helpers with the safe defaults built in:
`pit_latest(base, src, date_col, anchor, max_age_days)` and
`window_agg(base, src, date_col, anchor, days, aggs)`; floors derived from
`min(anchor) − lookback`, not from `persona_start`.

**P7 — Dead and parallel code.** T0-anchored and obs-date variants of the same node side by
side (v1 Nodes 3/3r, 4/4r, 5/5r) though only the obs-date one drives the state; nodes kept
"not wired" (`build_rl_a1_group_d_origination`); catalog entries for removed nodes; `_v2`
suffixes.

## 3. Per axis

### Foundation
- `cc_spell` (CC, bucket ≥ 2) and `rl_spell_table` (RL, bucket ≥ 1) are the same algorithm with
  different thresholds and different bugs (O3/O4 vs O34). → One spell builder parametrised by
  the existing `_dpd_journey` `BucketScheme`; deterministic per-month dedupe (worst bucket) in
  one place; `spell_end` computed so it can be evaluated as-of a date (fixes O26 at the root).
- `cc_full_history` / `rl_full_history` stay (different sources), both via the same scoping and
  `log_stats` conventions.

### A4 deterioration — keep as is
Reference design. Only P3 applies (logging already opt-in in the engine).

### A1 ability — one engine, two wrappers (agreed direction)
`a1_ability/` package, product-agnostic, on the obs base:
- `signals.py` — income (payroll months, WM salary PIT with max age, bureau salary), liquidity
  (CASA recent/prior averages, external card payments, CASA in/outflow counts), distress
  (bounced cheque + optional sources); built on `pit_latest` / `window_agg`.
- `classify.py` — levels, points, `StateLadder` (`scoring_engine` moves in here).
- A `ProductConfig` with the only real differences: the liquidity anchor (CC oldest overdue
  bucket, RL one EMI) and extra income evidence (RL: `feature_retail_loans` AECB salary).

`cc_a1_ability` / `rl_a1_ability` become a `pipeline.py` plus a small anchor node each.
v1, the RL waterfall and the unused enrichers go. **~5,400 → ~1,000 lines (estimate).**
Folds in O24, O36, O37, O39; makes O31/O32 moot.

### A2 locatability
- Already shares `build_a2_locatability` between CC and RL — good. But two functions are
  500+ and 300+ lines (`build_a2_contact_signals`, `build_a2_locatability`). → Split into
  small named steps (event filter, attempt normalisation, reachability, location), same
  outputs.
- Base from the obs base (P5); departure-trail columns from a lean shared module (below).
- Open data checks before any change in behaviour: O13, O14, O15, O16 (row multiplication and
  silently-NULL contact signals).

### Departure signature — the biggest lever (needs your input, D1)
`cc_departure_signature` computes 12 passes / ~30 columns; the only reader left after A1 v1 is
removed is A2, which uses **4 columns**: `travel_mcc_flag_h2`, `last_txn_foreign_flag`
(Pass A), `casa_inflow_stop_gap_d` (Pass B), `foreign_login_flag` (Pass J).
`cc_payment_trajectory` and `cc_utilisation` exist to feed A1 v1 and the departure W_pre
window. If nothing outside `crx_persona` reads the other passes, the departure signature
becomes a ~400-line `departure_trail` shared by CC and RL (product-specific source for
travel: card transactions vs CASA debits), and `cc_utilisation` plus most of
`cc_payment_trajectory` can be deleted. **~5,500 → ~800 lines (estimate).** O1, O2, O8, O21,
O28 then mostly disappear with the code.

## 4. How it ships

Every step is one bundle on its own workplace branch, checked in PROD before the next:

| # | Bundle | Behaviour | PROD check |
|---|---|---|---|
| 1 | Shared utils: `require_columns`, `pit_latest`, `window_agg`, `attach_covering_spell`, obs base, `log_stats` | none (additive) | imports only |
| 2 | A1 engine; CC A1 rebuilt on it, **exactly reproducing v2** | none | parity: `crx_cc_a1_ability_v2` old vs new, row by row |
| 3 | A1 fixes (O24, O36, O37, O39) | changes | state distribution before / after |
| 4 | RL A1 on the engine | new | distribution + RL vs old waterfall crosstab |
| 5 | Remove CC v1 + RL waterfall, drop `_v2` names, registry + catalog; Sonnet updates the 2 test modules | renames | pipelines import, catalog resolves |
| 6 | Foundation: shared spell builder + covering-spell join (O22, O26, O34) | changes | spell counts, rows kept per axis |
| 7 | Departure trail + A2 split (after D1) | depends on D1 | A2 state crosstab old vs new |
| 8 | Docstring / logging sweep (P1, P3) across what remains | none | run time |

Refactors (1, 2, 5, 8) never change outputs, so a parity check is enough; fixes ship
separately so each change in numbers has one cause.

## 5. Decisions needed

- **D1** — Do any models, reports or notebooks read `crx_cc_departure_signature` columns other
  than the 4 A2 uses, or `crx_cc_payment_trajectory` / `crx_cc_utilisation_features`? A grep
  for this is in `REQUESTS.md` (R4). **Answered (R4, 2026-10-27):** only `pipeline_registry.py`
  names them outside `crx_persona/`; they retire with their persona consumers.
- **D2** — Input policy: required sources fail loud; only not-yet-materialised sources are
  optional (recommended), or keep silent NULL stubs.
- **D3** — Strip ticket history out of docstrings into `RESULTS*.md` (recommended).
- **D4** — Refactors strictly behaviour-preserving with fixes as separate bundles (recommended),
  or fold fixes into the refactor to save a PROD cycle.
- **D5** — Order: A1 first as planned (recommended), or foundation (bundle 6) first, since O26
  affects every RL axis.

## 6. Decisions taken (2026-10-23) and what they change

- **D2 — missing source columns stop the run.** Required inputs go through `require_columns`
  and raise, naming the table and the columns. Only sources that do not exist in PROD yet
  (`prm_bureau_payment_order`, …) are explicit optional parameters.

- **D3 — docstrings:** remove ticket-history references and every docstring/comment that does not
  describe what the code does now. History stays in git and `RESULTS*.md`.
- **D4 — fixes are folded into the refactor bundles.** No row-by-row parity checks; each
  bundle's PROD check is a before/after distribution plus a crosstab old vs new state, and the
  bundle notes list which O-findings explain the differences.
- **D5 — deprecate the spell concept.** The axes are now anchored on the scoring date
  (`observation_date`), so tables keyed on spell onset (T0) are no longer needed:

  | Today | After |
  |---|---|
  | `cc_spell`, `rl_spell_table` | removed |
  | `rl_a4_spine`, `join_spine_to_spell`, `build_rl_depart_spine` | replaced by the obs base `(account_id, observation_date, cif_id)` |
  | T0-anchored windows in the departure trail (travel H2, salary stop gap) | anchored on `observation_date` |
  | `cc_raw_extract` (scoped by T0 windows), `cc_payment_trajectory`, `cc_utilisation` | removed; CC card transactions scoped by the spine instead |
  | A2 contact window `[t0, observation_date)` | `[collections_entry_date, observation_date)` (D6) |
  | A4 | unchanged — it never used the spell tables |

  This removes O3, O4, O22, O26, O27, O34 with the code.
- **D6 — DCORE windows start at collections entry.** Contact attempts are counted from when the
  account entered collections (that is what T0 meant). Without spell tables the entry date is
  taken point-in-time from the DPD history: the start of the current delinquency episode as of
  the observation date, which the A4 engine already computes (`months_before_spell`). Same
  meaning as today's T0, without the O26 look-ahead. Data check before shipping: compare it
  with DCORE's own agreement start date, if `dcore_stg_scope_agreements` carries one.
- **A3 keeps the spell tables** until the DE moves it to `observation_date`; bundle 7 then
  deletes them.

  **Blocker:** the DE's A3 (`cc_a3_payment_credibility`, `rl_a3_payment_credibility`) is keyed on
  `(account_id, spell_id)` and reads the spell tables. The spell tables can only be deleted after
  A3 moves off them; until then they stay, unused by the other axes.

### Revised ship order

| # | Bundle | PROD check |
|---|---|---|
| 1 | Shared utils (`require_columns`, `pit_latest`, `window_agg`, obs base, `log_stats`) | imports |
| 2 | A1 engine + CC A1 on it, with fixes O24/O36/O37/O39 | distribution + crosstab vs v2 |
| 3 | RL A1 on the engine | distribution + crosstab vs RL waterfall |
| 4 | Remove CC v1 + RL waterfall, drop `_v2` names, registry + catalog; Sonnet updates the 2 tests | imports, catalog resolves |
| 5 | Departure trail on `observation_date` (CC + RL), A2 on the obs base + split + D6 window | A2 crosstab vs old |
| 6 | Delete T0-only packages (`cc_raw_extract`, `cc_payment_trajectory`, `cc_utilisation`, `rl_a4_spine`, departure passes) | imports |
| 7 | Delete spell tables — after A3 has moved off them | — |

### A1 finish plan (user, 2026-10-26)

The CC month-end output is in PROD (bundle 03 Step 9 matched the check). A1 is concluded after:

| Step | What | Needs | PROD check |
|---|---|---|---|
| a | GRR initial results: why each state fires, what information is missing (`bundle_helpers/a1_final/sonnet_a1_v03_grr_prompt.md`, cc_60_180) → results note | the Sonnet run | — |
| b | **CC finish bundle** (+ spec S12 window-total salary, S13 bureau EOS spikes if any, sized by v03): `prm_bureau_salary_history` + `prm_beneficiary_cards`, the monthly features (§7), signals on obs base + features; rename `cc_a1_ability_v2` → `cc_a1_ability`, `crx_cc_a1_ability_v2` → `crx_cc_a1_ability`; delete CC v1 (`cc_a1_ability/` and its `crx_cc_a1_group_*` entries); Sonnet updates the 2 tests | R5 photos | new vs the current `crx_cc_a1_ability_v2` (kept as a temporary baseline): changes only on rows whose bureau distress moves (first-report dating cuts bureau flags ~23%) |
| c | **RL bundle**: RL wrapper on the engine (EMI anchor via a loan feature, the same CIF features), delete the RL waterfall (`rl_a1_ability/` + `crx_rl_a1_group_*`) | decisions below | distribution + crosstab vs the RL waterfall |
| d | v03 for rl_60_180, then the A1 final report (CC + RL) for GRR | c | — |

RL anchor (user, 2026-10-26): `int_loan_master` is the month-end loan snapshot built on the
loan primary, so the RL anchor node reads it directly (obs base + one dataset):
`monthly_emi_due` (= `installment_due_amount`) on the observation month's snapshot; missing or
0 → flat floors. Its payment columns (`total_paid`, `emi_paid/missed/partial_flag`) and
`feat_loan_emi` (missed / partial / paid counts, discipline rate, coverage ratio per 1/3/6/12 M)
describe payment behaviour, not ability: they stay out of A1 (A3 territory); the waterfall's
EMI-coverage arms go. Decided (user, 2026-10-26): `feature_retail_loans` carries the latest
bureau pull on or before each spine row's observation date (not only the pre-disbursement
pull), so RL keeps `aecb_last_salary_credit_amount` (dated by `aecb_bureau_pull_date`) as an
extra bureau salary source until GRR's bureau salary fix lands. It is dated by the pull month
and merged into the bureau salary series (larger value per month). Pulls are rare today (most
accounts have one), so it seldom falls in the window — expected, not a defect; it grows as the
source is refreshed more often; then RL relies on the bureau
source tables and pipeline only. rl_60_180 first, rl_180_plus later (as cc_180_plus). Bundle numbers: the next free one when built — A2's
refactor waits on v02, so A1's bundles may come first.

## 7. Data layers (decided 2026-10-23)

Persona pipelines read **primary and feature datasets only**. A raw source is read once,
upstream, by a primary node that every consumer reuses. This is the rule for new DE and persona
pipelines alike.

| Layer | Reads | Holds | Business rules |
|---|---|---|---|
| Raw / staging (`raw_`, `stg_`, `comp_`) | — | the source as loaded | — |
| Primary (`prm_`, `wm_pri_`) | raw only | one table per entity or event, all customers, typed, deduplicated, at its natural grain | none |
| Feature (`feat_`, `wm_fea_`) | primary | generic per-customer aggregates | generic only |
| Persona signals (`crx_*_signals`) | primary + feature, never raw | point-in-time aggregates per observation-base row | yes: thresholds, reason lists |
| Persona axes (`crx_*_a1…`) | signals only | states | ladders |

- **One owner per raw table.** A persona node that needs raw data is a request for a new
  primary dataset, not a direct read.
- **Primary datasets carry no decisions.** They keep every value (all reasons, all codes);
  which values count is decided in the signal layer, so a decision never needs a rebuild.
- **Reverse-engineering is a smell.** A signal reconstructed indirectly (salary months
  recovered from "days since last salary" snapshots) marks a missing primary dataset. Log it
  as a candidate; don't build one on the spot. Salary stays on the WM features (decided);
  the GRR bureau feed is the planned coverage fix.
- **Enforced by a test** (Sonnet): no `crx_` node takes a `raw_` / `stg_` / `comp_` input.

### One layer per node (user, 2026-10-26) — proposal, decisions open

A node reads **one layer**: primary nodes read raw / staging, feature nodes read primary
(or reshape a WM feature we do not own), persona signal nodes read the obs base plus feature
datasets. Every `node()` spells out `func=`, `inputs=`, `outputs=`, `name=`, `tags=`.
Feature tables are `cif_id` (or account) × month end, all customers from a parameter floor,
raw values only (every reason, both salary sources): thresholds, reason lists and "larger
of" stay in the signal layer. Monthly features also absorb the mid-month source dates.

**A1 today** — the mixed nodes:

| Node | Reads today | Layers mixed |
|---|---|---|
| `build_crx_cc_a1_income_signals` | `wm_fea_salary_days_since_increment`, `stg_aecb_salary_history`, `prm_bureau_cif_bridge` | feature + staging + primary |
| `build_crx_cc_a1_liquidity_signals` | `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow`, `wm_pri_labelled_transactions`, `raw_beneficiary_cards` | feature + primary + raw |
| `build_crx_cc_a1_internal_returns` → `…_distress_signals` | `prm_casa_return_events`; `prm_bureau_alert_enriched` + the persona `crx_cc_a1_internal_returns` | primary (+ persona) |
| `build_crx_cc_a1_liquidity_anchor` | `prm_balance` (billing-date snapshots) | primary |

**A1 layered** (same logic, so the check is an exact old-vs-new match):

| Layer | Dataset | Built from | Holds |
|---|---|---|---|
| primary (new) | `prm_bureau_salary_history` | `stg_aecb_salary_history` | our own explicit node in the bureau primary pipeline: file id, salary month, provider, `edp_load_date`, total salary (the DE's unbuilt `BureauSalaryHistory` model is a naming guide only — the bureau pipeline is unvalidated, user 2026-10-27); named columns, `require_columns`, no model projection; bureau inputs checked first in A1 v03 (v0) |
| feature (not a primary) | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (has `cif_id`, `contract_type`, `alert_description`, `bounced_cheque_amount`, `extract_date`) | bureau bounce events per CIF × month: per key `(cif_id, contract_type, alert_description)`, a new event whenever the bounced amount differs from the key's previous bounced pull or follows a non-bounced row; identical consecutive repeats dropped (user, until GRR confirms the amount) — no staging read needed |
| primary (new) | `prm_beneficiary_cards` | `raw_beneficiary_cards` | `cif_id`, registered card number |
| feature | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` | WM-recovered salary per month |
| feature | `feat_cif_bureau_salary_monthly` | `prm_bureau_salary_history` + `prm_bureau_cif_bridge` (join on `bureau_file_id` × `edp_load_date`, as `_join_cif_bridge`) | bureau salary per CIF × month (largest reported total across providers and pulls) |
| feature | `feat_cif_casa_monthly` | `wm_fea_casa_eod_avg_balance`, `wm_fea_casa_cc_inflow_outflow` | month's balance (4-week average, last snapshot), any inflow / outflow |
| feature | `feat_cif_ext_card_payment_monthly` | `wm_pri_labelled_transactions`, `prm_beneficiary_cards` | largest single payment to a registered card |
| feature | `feat_cif_returns_monthly` | `prm_casa_return_events` | return events per reason (cheque, DDS, POS reversal) |
| feature | `feat_cc_balance_month_end` | `prm_balance` | overdue buckets 01–08 on the month's latest snapshot, per contract |
| signals | income / liquidity / distress / anchor | obs base + the features above | windows, thresholds, reason list, larger-of |

Placement (R8, handoff 6): nodes in `nodes/primary/bureau/`, `nodes/features/{bureau,casa}/`,
pipelines in `pipelines/bureau/` (primary / features) and `pipelines/casa/`; catalog entries
`<<: *spark_de` with `folders.prm` / `folders.feat` paths (`bundle_helpers/a1_final/workplace_reference.md`).
`catalog_outputs.yml` is not mirrored, so the bundle puts the new entries in our own catalog files
(`catalog_casa.yml`, a new `catalog_bureau.yml`). R7: nothing outside the A1 packages reads the CC
v1 / RL waterfall outputs (registry, tests and docstrings only).

`crx_cc_a1_internal_returns` disappears (the distress node reads two features). RL A1 reuses
every CIF-level feature; it adds an EMI feature from its loan primary.

**A2 (its refactor bundle, next free number) layered from the start:**

| Layer | Dataset | Built from |
|---|---|---|
| primary (fix) | `prm_digital_login_monthly` | staging login (O53–O56) |
| primary (new) | `prm_dcore_account_agreements` | the DCORE agreement source (today only in the staging `dcore_observation_spine`) — account → agreement, no dates |
| primary (v02 decides) | card / CASA spend primary | `prm_transaction`; raw CASA or the WM datasets |
| feature | `feat_cif_location_monthly` | login + card + CASA primaries: latest UAE / foreign evidence date + source, latest travel purchase |
| signals | location | obs base + `feat_cif_location_monthly` |
| signals | reachability | obs base + `dcore_prm_followup_outcomes` + `prm_dcore_account_agreements` (code lists stay here) |
| signals | deceased | obs base + `dcore_prm_followup_outcomes`, `prm_contract`, `prm_demographics` (not `feat_demographics_cif`) |

**Decided (user, 2026-10-26):** `prm_bureau_salary_history` goes into the bureau primary
pipeline now (photos: REQUESTS R5). Our monthly features may be built from the WM feature
tables (we do not own them; they are our source). **Open (user), before A1 is concluded:** the
A1 relayering ships as its own bundle (the CC finish bundle)? — RL A1 shipped first as bundle 05 (user, 2026-10-26).

### First primary: `prm_casa_return_events` (bundle 03)

Its own pipeline outside `crx_persona`, built from `comp_financial_tran_repos_dly`:
- one row per distinct return event, for **all CIFs** (CC and RL A1 both read it);
- columns: `cif_id`, account, `tran_date`, `reason_for_excluding`, transaction key, amount,
  debit/credit and type/code columns — the key and columns are fixed by Sonnet v01's
  `columns_found`;
- every return-type reason, not only the three A1 counts today;
- deduplicated on the transaction key, so reloads across `edp_load_date` count once;
- refreshed incrementally: each run rebuilds only the last N days of `edp_load_date`
  (parameter, to catch late reloads) and overwrites the affected event months; only the first
  build scans the full table.

`build_internal_returns` then becomes a filter on it (reason list, window) in the persona layer.

### Raw inputs the persona pipelines still read

| Raw input | Read by | Plan |
|---|---|---|
| `comp_financial_tran_repos_dly` | CC / RL A1 | → `prm_casa_return_events` (bundle 03) |
| `raw_transaction`, `raw_stg_limit`, `raw_stg_balance`, `raw_stg_account_group` | `cc_raw_extract` | deleted in ship step 6 |
| `raw_stg_billing` | `cc_spell` (step 6/7), `cc_full_history` (feeds A4) | a primary billing-history dataset, or an existing `prm_` equivalent |
| `stg_aecb_salary_history` | bureau salary | GRR's bureau primary when it lands |
| `raw_beneficiary_cards` | external card payments | a `prm_` snapshot later (small, low priority) |
