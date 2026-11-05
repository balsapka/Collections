# A1 redesign design-in (S1, between rounds 1 and 2)

Input: worktree HEAD `2942237`, the High what-if / signal-inventory prompt
(`origin/feature/persona_redesign:…/a1_final/sonnet_a1_high_whatif_prompt.md`) and the family-based
redesign the user is exploring. No A1 logic changes here. The aim is an engine where **a family is
added or removed by touching its builder and one declaration line**, with the scoring shared with A3
(`a3_target_shape.md` §5). Every family reads a window that ends at `observation_date` (GRR,
2026-11-05): there is no pre-delinquency family, and A1 does not use `episode_start`.

## 1. The family model on today's engine

| Family idea | Today's code | Fits as |
|---|---|---|
| Family = one signal builder joined onto the obs base | `signals.build_*_signals` (income, liquidity, distress, eosb) → `crx_<p>_a1_<x>_signals`; `classify.build_a1_ability` left-joins a **fixed parameter list** | builder: yes. Join: **structural** (item A1-2: `**signals`) |
| Each family scores 0 / 1 / 2 against the anchor | `income_level(anchor, w)`, `liquidity_level(anchor, w)` called by name in `build_a1_ability`; points in `INCOME_POINTS`, `LIQUIDITY_POINTS` | **structural, small**: one `FAMILIES` table (level function + `Dimension`) instead of named calls (A1-2) |
| Ladder over family points | `_LADDER = StateLadder(...)`, sum of two `points_from_level` | `Scorecard` (A1-1, shared with A3) |
| High needs two families, one of them current | not expressible (`StateLadder` has points only) | `Scorecard(high_min_dimensions=2, high_current=(...))` (A1-1) |
| Distress as a cap or negative points | one-rung demotion through `StateLadder` | `Override("distress", ..., DEMOTE \| CAP)` or `Dimension("distress", ..., {"flag": -2})` (A1-1 allows negative points) |
| Reason: top contributing family | none (`a1_unknown_reason` only; Q-26) | `a1_reason` from the Scorecard; a new output column, so it ships with the redesign bundle |

After A1-1 and A1-2, adding a family = (1) a builder in `signals.py` returning `GRAIN` + its evidence
columns, (2) its node in `create_a1_pipeline` (one input line on the state node), (3) one `FAMILIES`
row: `(level_fn, Dimension(name, level_col, POINTS))`. Removing one = deleting those three. Nothing
else in `classify.py` moves.

The redesign bundle can go one step further (not now: it changes intermediate datasets): each
builder takes the anchor and writes its own `<family>_level`, so `FAMILIES` holds only the
`Dimension`s.

## 2. Where each candidate plugs in

| Candidate (prompt) | Plugs in as | Where | Notes |
|---|---|---|---|
| **A** internal Stable → High | one level + one points constant | `income_level` gets a `prefix` arg; `build_income_signals` adds `internal_m1…m2W`; level `stable_internal` with points 4 (no distress → High, distress → Moderate through the ladder) | or, under families, a High gate counting income as the current family |
| **B** liquidity from flows | one signal column set + one predicate | `build_liquidity_signals`: `flow_m1…m2W` from customer-lane credits via `_by_month`; `classify._flow_ok(anchor, w)` with `FLOW_FLOOR = 1000.0`, `FLOW_ANCHOR_MULT = 1.0` | needs credit **amounts** per lane in `feat_cif_casa_activity_monthly`; if it has only `legs`, the feature table changes (outside the engine, structural) |
| **B′** B without salary credits | one filter | the lane filter in the flow builder | only if `transaction_lane` tags salary legs; otherwise structural (feature change) |
| **C** lower balance floor | one constant | `CASA_FLOOR` 3000 → 1000 | none |
| Inflow capacity family (credits by type, large one-offs ≥ 3 × anchor or AED 10,000) | new builder | `build_inflow_signals` on the CASA activity amounts; `window_agg` over W | same amount caveat as B |
| Spend capacity family (POS, ATM, outward transfers, bill pay, debit card) | new builder | `build_spend_signals`; Way4 debit spend reads a `prm_`/`feat_` table (no raw) | |
| Holdings outside CASA (TD, investment, WM codes) | new builder or an extra leg in liquidity | `pit_latest(max_age_months=w)` on a holdings feature | needs the sweep / lien answer first |
| Cross-product conduct (S12) | new builder | `build_conduct_signals` over the CIF's other products | label A3-adjacent: payment behaviour towards us is A3 (CLAUDE.local A1 notes) |
| ~~Pre-delinquency capacity~~ | dropped (GRR, 2026-11-05) | A1 reads only windows ending at `observation_date`; it never uses `episode_start` (an A3 helper, D-A3-2) | — |
| Profile prior (declared income, DBR, employer, segment, tenure, age, residency) | new builder, a **static attribute** (latest value on or before the observation date, no pre-delinquency window) | `pit_latest(..., max_age_months=None)` on an origination feature | needs a `prm_`/`feat_` origination dataset (structural, outside the engine) |
| Bureau alerts / `bo_rr_aecb_metric` / `feature_retail_loans` fields | new builder, or columns on the income builder | linkable sources only (O65) | `bo_rr_aecb_metric` needs a feature table keyed by `cif_id` |
| Call-transcript slot (UC1, S19) | new builder later | one `FAMILIES` row | — |

## 3. Structural gaps (round 2 items, in `round_1/triage.md`)

- **A1-1 `Scorecard`** (shared with A3; the central item): A1 moves from `StateLadder` to the
  Scorecard with identical output on the golden harness.
- **A1-2 `build_a1_ability(obs_base, anchor, model_id, persona_end_date, **signals)` + `FAMILIES`**:
  the join and the level calls stop naming families.
- **A1-5** (redesign bundle, not round 2): each family builder takes the anchor and writes its own
  `<family>_level`.

Every new family reads its window through today's `window_agg(months=w)` / `pit_latest`, both
anchored at `observation_date`: no other shared helper is needed.
