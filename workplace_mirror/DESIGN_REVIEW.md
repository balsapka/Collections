# crx_persona — design review and refactor proposal

Status: **D2–D6 decided 2026-10-23 (§6); D1 waits for the R4 grep.** Nothing is changed yet.
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
  for this is in `REQUESTS.md` (R4).
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
