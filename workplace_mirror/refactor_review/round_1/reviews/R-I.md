# R-I review, council run 2, round 1 (interpretability advocate)

Frozen rubric `rubrics/interpretability.md`; "Fits A3 easily" read as "fits the pending A3 / A1 rule
changes easily" (promise points, deadline, 180+ cut-offs; A1 bureau carry and closure rule). Reviewed
`git diff d24114a a6a0b95 -- workplace_mirror/src workplace_mirror/specs` at `a6a0b95`, blind to R-E / R-O.
No source edited, nothing run (the Master's gates pass).

Blocking objections open: **none**. Revise list (all non-blocking): S1-06, S2-01, S4-04 (re-propose), S4-16.

## Proposals

### Applied

S7 B-01: accept (blocking: no)  criteria: I2
  Unused `PRODUCT_TYPES` gone; `ASSET_TYPES` / `CREDIT_TYPES` (S4-08) are the one definition. Neutral to positive.
S7 B-02: accept (no)  I5
  Dead `anchor=` parameter and `_anchor` column removed; the `pit_latest` docstring now states the contract it has. Keeps I5.
S7 B-03: accept (no)  I3
  The dead `max_months=None` branch was a rule nobody could fire. Gone; the DCORE window is `DCORE_MAX_MONTHS` alone.
S7 B-05: accept (no)  I5
  README named `D_INC`; the constant is `INCOME_MAX_FALL`. A stale name is an auditor trap (blocking 4); fixed.
S1-01: accept (no)  I2, I6, I7
  One floor rule (`history_floor(persona_start_date, months)`) for features, primaries and A1. `months - 1` semantics
  ("that month included") is documented in the docstring. A1 spells it through `_floor`, RL anchor / `prm_products`
  inline it (see N-13), otherwise good.
S1-02: accept (no)  I1, I3
  One cutoff per event date, so a follow-up event keeps the deadline its run was cut with. The D-A3-29 fold can state its
  rule in one place.
S1-03: accept (no)  I1, I2, I6
  `promise_deadline(product, model_id, override)` is the single resolution of D-A3-28. Exactly the "one helper per
  decision" shape; a changed deadline touches `PROMISE_DEADLINE` and nothing else (but see N-3).
S1-04: accept (no)  I1, I3, I6
  `promises.py` holds the promise-event rule (D-A3-25, -29) and nothing product-specific; `sources.py` is down to the
  ledgers. This is the A3 pending-change home: points stay in `constants.py`, deadline and events in `promises.py`.
S1-05: accept (no)  I2, I6
  `HISTORY_MONTHS` is derived from the dimension windows, the `35` / `-13` literals are gone. Cost: the CC-only numbers
  (`CYCLE_MAX_DAYS`, `FLOOR_LOOKBACK_DAYS`, `BUCKET08_BASELINE_MONTHS`) left `constants.py` for the CC wrapper, so A3's
  numbers now live in two modules (N-12, a pointer comment fixes it).
S1-06: revise (no)  I1, I2, I3, I6
  `BUREAU_CARRY_MONTHS` is the "one constant" the family-rule spec promises, and the carry now reads off a named module
  constant. Revise: `_with_carry` builds `rows` with a list comprehension that holds an inline `if age == 0 else`
  (`classify`-style cleverness, blocking 2 territory). For a month-end `month_end`, `last_day(add_months(month_end, 0))` equals
  `month_end`, so the branch can go and the comprehension becomes one named step. Add one comment that says why
  `coalesce(newest)` realises "newest row wins, a 0 row stops older ones" (the zero is non-null; today this is implicit).
  When the closure rule arrives (`is_closure` rows carry nothing) it is one `where(age == 0 | ~is_closure)` in that step.
S1-07: accept (no)  I7
  Bounces use `frames.require_columns` like the salary feature.
S1-08: accept (no)  I3
  A one-caller wrapper node inlined; neutral.
S1-09: accept (no)  I7
  `scoped()` is the one scoping idiom in `_common`.
S3-02: accept (no)  I5
  Every A3 builder names the table contract it needs; `EPISODE`, `DUES`, `PAYMENTS`, `INSTALMENTS`, `CYCLE_LEDGER` are named
  per boundary. `INSTALMENTS` still lists `due_date` / `due_amount` / `payment_amount` that no A3 rule reads (B-06 held).
S3-04: accept (no)  I5
  Raw-input and window-table checks at the CC extract boundary.
S3-09: accept (no)  I7
  Dict inputs everywhere, as every other pipeline.
S3-10: accept (no)  I7
  `tags` binding only; same idiom.
S2-01: revise (no)  I1, I4
  One pass is fine. In `_contact_summary` the Q-28 tie-break lives in `F.struct("day", (disp != "refusal").cast("int").alias("later"), "_disp")`:
  the field `later` hides "on the same day a non-refusal counts as later", and the last tie-break is the lexicographic
  order of the label strings (success > ptp > paid > hung_up > dispute), a business ranking that exists only by spelling
  (N-1). Revise: name the field (`non_refusal_rank`), and state or declare the label order.
S2-02: accept (no)  I3
  The judged-once chain is the D-A3-25 rule in a straight line.
S2-04: accept (no)  I3
  Agreements scoped before the join; no rule change.
S2-05: accept (no)  I3
  Stagnation start as one window; the `_stagnated` expression has a comment that names the rule.
S2-07, S2-08, S2-09, S2-10, S2-11: accept (no)  I3
  No rule is touched; each reads at least as clearly. S2-10 (`max(struct(day, value))`) matches the `pit_latest` tie
  convention ("largest value first"); the Q-R-09 question is R-O's.
S4-01: accept (no)  I3, I4
  Contact builder 113 → ~70 lines; `_contact_events`, `_contact_summary`, `_plan_after_refusal` name three contact ideas.
S4-02: accept (no)  I1, I3
  `_with_due` / `_with_paid` name the two halves of the D-A3-25 judgement and carry the contract in their docstrings.
S4-03: accept (no)  I3, I5
  `_require_plan_sources` moves the contract out of the reader. `_plan_instalments` takes seven arguments (`seq`, `start`,
  `kind`, ...); acceptable because it is one reader for two plan kinds, not a method switch.
S4-05: accept (no)  I7
  Same `# ruff: noqa: F401` in both engine `__init__` files as `_dpd_journey` (run 1 ruling).
S4-07: accept (no)  I3, I4
  `_income_source`, `_salary_stopped` name two diagnostics; `labels` from `DISPLAY_NAMES`; `build_a1_ability` loses its
  pylint disable.
S4-08: accept (no)  I2
  `ASSET_TYPES` / `CREDIT_TYPES` cannot drift from the feature (the old inline `"deposit", "investment", "wm"` literals are gone).
S4-10: accept (no)  I2, I4
  `_load_bound(floor)` replaces `_window`.
S4-11: accept (no)  I3
  One `billed` ladder expression instead of two.
S4-13: accept (no)  I5
  Message re-wrap and two comments.
S4-14: accept (no)  I1, I5
  `_run_step` / `_no_runs` give the D-A3-29 fold a name and a docstring ("starts a new run when more than 7 days after the
  previous row or after the run's deadline"). Good traceability for the pending A3 change.
S4-15: accept (no)  I3
  `_commitment_counts` separates counting from the ladder; the Dimension A ladder (broken / kept / partly kept / thin) reads as one expression.
S5 (docstrings): accept (no)  I5
  History and ticket names gone; docstrings match the merged code (checked `_with_carry`, `build_income_signals`,
  `promise_deadline`, A3 pipeline diagram). No stale `[CONFIRM]`. The spec edits are name-only.

### Held, reverted, skipped

S3-01 (one `require_columns`): accept, apply later (no)  I7
  Two copies of the same contract is the I7 "same thing written twice". The failure text changes but not an output; R-O rules
  on the text. Not urgent for me.
S3-11 (`build_a1_ability` checks its signal tables): accept the hold (no)  I5
  A boundary contract is welcome, but the proposal copies the column lists of five signal builders into `classify.py`
  (+30 lines); a second list to keep in step with `signals.py` when the carry / closure change lands. Do it only if the lists
  are derived from the builders' own contract constants.
S2-12 (broadcast account windows): accept (no)  neutral
  One word, no rule. Tier K, not in the oracle; R-E / R-O.
S4-06 (`_salary_rows` out of `build_income_signals`): accept, apply now (no)  I3
  `build_income_signals` is the longest A1 builder (62 lines); the carry change lands in `_with_carry`, not in the builder body,
  so the two do not conflict. After S1-06 the builder reads: sources, carry, window levels.
S4-16 (`state_label` → `map_values`): revise (no)  I4
  The current name is wrong (it maps points too). `map_values` is correct but describes the mechanism, the I4 anti-pattern. Rename
  for what the caller means, e.g. `value_of_level(col, values)`, and apply with the next A1 / A3 bundle since it touches A2 and
  A4 files.
S4-04 (reverted, pylint R0914 on `create_a3_pipeline`): revise, re-propose (no)  I2, I4
  The revert is right for the gate but the reason for the proposal stays: the persisted signal output name
  (`..._dlq_payment_signals_single_payment_cycle_count`) is typed twice, and two names (`..._single_payment_cycle_count`,
  `..._strong_negative_signals`) do not say what the table holds. Re-propose with a module-level `DATASETS` mapping (or a small
  `_dataset_names(product)` returning a NamedTuple) so `create_a3_pipeline` has no extra locals; keep the workplace names as the values and say in
  one comment which business table each one is.
S3-03 (skipped): accept the skip (no)  I7
  All four A1 signal nodes take `params:crx_persona`; one convention is better than the proposal.

### Held for the user (not mine to decide, my view)

S7 A-01 (delete spell / spine packages): accept once the workplace grep is back; dead packages next to live engines are an auditor trap.
S7 B-04 (Scorecard `CAP` / `FORCE` / `high_current` unused): hold. It reopens run 1 D-2-3; A3's pending promise points may still need `CAP` (see N-11).
S7 B-06 (`due_amount` / `payment_amount` unused in `build_instalments`): accept deletion if the persisted columns are not read; they widen the `INSTALMENTS` contract with names no rule uses.
S2-03 (persist A3 dues / payments): no I-effect.

## Files (merged tree, tier L changed + new)

Criteria in order I1 22 · I2 14 · I3 16 · I4 12 · I5 12 · I6 16 · I7 8.

| File | I1 | I2 | I3 | I4 | I5 | I6 | I7 | Weighted | Note |
|---|---|---|---|---|---|---|---|---|---|
| `a3_credibility/promises.py` (new) | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | D-A3-25 / -29 rule in named steps; lowest: `MATCH_DAYS` has no ID (constants.py:15), the `for key, tie` loop at :107 hides "nearest, once each" (N-5) |
| `a3_credibility/signals.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.16** | one builder per dimension with D-A3 ids; lowest: tie-break by label spelling (:345-352, N-1) |
| `a3_credibility/sources.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | `_plan_instalments` has 7 parameters and a pylint disable (:114-123); contract lists unused columns (B-06) |
| `a3_credibility/constants.py` | 4 | 4 | 5 | 4 | 4 | 5 | 4 | **4.32** | rows and D-ids per constant, `PROMISE_DEADLINE` by segment and product; `STATEMENT_FALLBACK_D` (:31) cryptic, `30` literal lives in promises.py |
| `a3_credibility/classify.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.38** | state, override, reason, unknown_reason, `a3_promise_deadline` on every row; 9 parameters and a pylint disable (:59) |
| `a3_credibility/pipeline.py` | 4 | 3 | 4 | 3 | 4 | 5 | 4 | **3.90** | dataset names typed twice (:104, :110, :132) after the S4-04 revert; names do not say the table (N-8) |
| `a3_credibility/__init__.py`, `a1_ability/__init__.py` | – | – | – | – | – | – | 4 | 4.00 | same noqa idiom |
| `a1_ability/signals.py` | 4 | 4 | 3 | 4 | 4 | 4 | 3 | **3.76** | `BUREAU_CARRY_MONTHS` is the right lever; `build_income_signals` 62 lines, `_with_carry` comprehension (:108-134), `_floor` vs inline floor (N-13), keyed by W not segment (N-7) |
| `a1_ability/classify.py` | 5 | 4 | 4 | 4 | 4 | 4 | 4 | **4.22** | families, points, `a1_reason`, `a1_unknown_reason`, `a1_income_source`; `MIN_MONTHS = {3: 2, 6: 3}` is keyed by literal window length (:36) |
| `a1_ability/pipeline.py`, `rl_a1_ability/*`, `cc_a1_ability/nodes.py` | 4 | 4 | 5 | 4 | 4 | 4 | 4 | **4.16** | `crx_persona` threaded in the same way on every node; RL anchor inlines `history_floor` where A1 uses `_floor` |
| `_common.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.28** | `lookback_floor` (a Spark action in a helper) gone; `scoped`, `window_months`, `GRAIN`, `GONE_DARK_DAYS` are the A3 hooks |
| `cc_a3_payment_credibility/nodes.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | CC numbers now sit beside the rule (good); `_balance_dues` still builds ladder, stagnation and baseline in one function |
| `scoring_engine.py` | 4 | 3 | 3 | 4 | 4 | 4 | 4 | **3.70** | docstring-only change; `Scorecard.score` ~48 lines with unused CAP / FORCE / `high_current` (N-11) |
| `frames.py`, `prm_products.py`, `feat_cif_cross_product.py`, `feat_cif_bureau_*`, `products/features.py`, `bureau/salary_bounces.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | named floor, `ASSET_TYPES` / `CREDIT_TYPES`, carry doc points at `BUREAU_CARRY_MONTHS`; no rule traceability lost |

## Weighted average

Mean of the file rows above: **4.05** (rubric file rows 12, unweighted by size). Round 1 criterion means: I1 4.2 · I2 3.9 · I3 3.8 ·
I4 3.9 · I5 4.1 · I6 4.4 · I7 3.9. Convergence bar is 3.5 and no blocking objection is open: met. Lowest criterion: I3 (A1
`build_income_signals`, A3 `_plan_instalments`, three pylint "too-many-arguments" disables kept on node entries).

Traceability check from the code (the question the rubric asks): an A3 state traces to `a3_reason` / `a3_override` / `a3_unknown_reason`,
each dimension level to its `D-A3-n` in `signals.py`, each number to its DE row in `constants.py`, and the promise rule to
`promises.py` (D-A3-25, -29) with the outcome per event in `promise_outcome`. An A1 state traces to `a1_reason` /
`a1_unknown_reason` and thresholds with S-numbers in `classify.py`. The only gap an auditor would hit without running data is the
Q-28 tie order (N-1).

Fit to the pending changes: promise points (`COMMITMENT_POINTS`), 180+ cut-offs (`REGULAR_FROM`, `ANY_PAYMENT_MONTHS`) and the deadline
(`PROMISE_DEADLINE`, `_cutoff`) each have one home; the A1 carry is one constant and the closure rule one filter in `_with_carry`
(after the S1-06 revise).

## New issues

N-1 [a3_credibility/signals.py:345-352] The Q-28 tie order inside `_contact_summary` is `max(struct(day, later, _disp))`: the last
  tie-break is the string order of the labels (success > ptp > paid > hung_up > dispute), a business ranking that exists only by
  spelling, and `later` hides the "non-refusal is later on the same day" rule. → declare `DISPOSITION_RANK` (or name the order in the
  `_DISPOSITIONS` comment, which today says "first match wins" for a different purpose), rename `later`; S4. Flag to S6 if the spec means
  a different order. No output change if the declared order equals the current string order.
N-2 [a3_credibility/promises.py:250, constants.py:42] The promise floor ("the due of the cycle open on the event day, at least 100 AED") and the
  partial limit reuse `MIN_PAYMENT_AED`, the Dimension B qualifying floor (D-A3-5). When promise points or the promise floor change, the two
  rules would move together. → `PROMISE_MIN_AED = MIN_PAYMENT_AED` (own name and D-A3-25 comment) in `constants.py`; S1.
N-3 [promises.py:237, classify.py:80, pipeline.py:82,128] The deadline is resolved twice (`promise_deadline` in the events builder and in the
  state builder) and `product` / `deadline` are threaded through `build_a3_credibility` only to label `a3_promise_deadline`. If the deadline is
  undecided and changes, the label can drift from the rule. → carry the resolved deadline on the events table or document that both call sites
  must use `promise_deadline`; S1 / the A3 bundle.
N-4 [promises.py:144-149, constants.py:20-31] `_cutoff` keeps the option names in a local dict beside the `DEADLINES` tuple, and `30` is a literal.
  Adding a deadline edits three places. → `PROMISE_WINDOW_DAYS = 30` (unit and D-A3-25/28 in the comment), build `fixed` from names
  tied to `DEADLINES`; rename `STATEMENT_FALLBACK_D` to `STATEMENT_FALLBACK_DAYS`; S4.
N-5 [promises.py:107-109] `for key, tie in ((["plan_id"], "fu_date"), (["fu_date"], "plan_id"))` is the rule "each plan takes its nearest follow-up promise,
  each promise at most once" written as a loop over key tuples, with `_r` columns. It is a spec rule (D-A3-25) expressed generically
  (blocking 1 territory, tolerable because the docstring states it). → two named steps or a one-line comment per pass; S4.
N-6 [constants.py:15] `MATCH_DAYS` carries no decision ID (D-A3-25) while its sibling `FOLLOWUP_RUN_DAYS` carries D-A3-29. → add the ID; S5.
N-7 [a1_ability/classify.py:35-36, a3_credibility/constants.py:43-44, _common.py GONE_DARK_DAYS] Per-segment numbers are keyed three ways: A1 by window length
  (`{3: 2, 6: 3}`), A3 and A2 by segment. → key A1 by segment in the next A1 bundle (not now: pending carry change, behaviour-neutral but wide); S1.
N-8 [a3_credibility/pipeline.py:41-42, 104, 110, 124] Persisted names `..._single_payment_cycle_count` (dimension B / C signals) and `..._strong_negative_signals`
  (contact signals) do not say the table's content and cannot be renamed (workplace catalog, PLAN §3). → the `DATASETS` mapping of S4-04 with a one-line meaning each; S4.
N-9 [a1_ability/signals.py:113-130] `age == 0` conditional inside the union comprehension is redundant for month-end rows (see S1-06). → drop; S4.
N-10 [a3_credibility/classify.py:59, signals.py:399, promises.py:212] Three node entries keep `# pylint: disable=too-many-arguments,too-many-positional-arguments`
  (nine, seven and nine parameters). Node inputs justify seven, not nine (`product`, `deadline` are label plumbing, N-3). → N-3 removes two.
N-11 [scoring_engine.py:60-93] `Scorecard.score` (~48 lines) holds `CAP`, `FORCE`, `high_min_dimensions`, `high_current` that no axis passes (B-04). Each is a rule an
  analyst must read and cannot find a user for. → decide with the A3 promise-points ruling: if no cap is needed, delete (B-04); if one is, keep and
  name the A3 use in the docstring.
N-12 [a3_credibility/constants.py header, cc_a3_payment_credibility/nodes.py:12-14] After S1-05 the A3 numbers sit in two modules (engine windows in `constants.py`, CC cycle numbers in the wrapper).
  → one comment in `constants.py` pointing to the wrapper constants and their D-A3-12 / -15 ids; S5.
N-13 [a1_ability/signals.py:77-80, rl_a1_ability/nodes.py:29, prm_products.py] The persona floor is spelled `_floor(crx_persona, months)` in A1 and
  `history_floor(crx_persona["persona_start_date"], months)` inline in the RL anchor. → RL anchor imports the same helper (or `_floor` moves to
  `_common`); S1.
