# R-E review, run 2 round 1 (efficiency engineer)

Frozen rubric `rubrics/efficiency.md`. Input `d24114a`, output `a6a0b95`. Blind to R-I and R-O. "Fits A3 easily" is
read as "fits the pending A3 / A1 rule changes easily" (promise points, deadline, 180+ cut-offs, bureau carry and
closure rule). Gates are the Master's; not re-run.

Measured on `src/` only: 986 added, 921 deleted, **net +65 lines** (S5 alone is -150). Spark actions: -4 per A1 run
(`lookback_floor`'s `.first()`, S1-01); nothing added. The growth is fail-loud `require_columns` (S3-02, S3-04, about
+75, rule D2) and the S4 splits; code that went: the second `_cutoff`, the due / paid side tables, the contact
self-join and second aggregate, the `lookback_floor` job, `PRODUCT_TYPES`, `max_months`, `pit_latest(anchor=)`.

## Proposals

### S1
S1-01: accept (blocking: no)  criteria: E2, E1, E5
  Removes four Spark jobs per A1 run and the `_common.lookback_floor` concept; `history_floor` has five callers
  (A1 x4 via `_floor`, RL anchor, both product primaries, cross-product). Cost: a whole `crx_persona` dict into five
  node signatures (see N-2). Net lines neutral.
S1-02: accept (no)  criteria: E2, E1
  Cutoff computed once per event date; the second `_cutoff` pass over all events is gone.
S1-03: accept (no)  criteria: E5, E1
  The override rule written once. `promise_deadline(product, model_id, override)` is the single place A3's pending
  deadline decision lands.
S1-04: accept (no)  criteria: E7, E3
  Pure move: `sources.py` 372 -> 199, `promises.py` 262. Neutral on lines, and it puts everything bundle 25 will rewrite
  (points, deadline, cut-offs) in one module with `constants.py`. That is the A3-fit win; no other criterion moves.
S1-05: accept (no)  criteria: E5, E3, E1
  Literals `35` / `-13` become `FLOOR_LOOKBACK_DAYS` / `HISTORY_MONTHS`; `build_cc_acct_windows` sits with its only
  consumer. `_history_floor` is a two-caller one-line helper (E3 2 there); harmless.
S1-06: accept (no)  criteria: E7, E1
  The one constant the family rule promises for the 3-month carry. Small revise, not blocking: `_with_carry` builds
  `F.col("month_end") if age == 0 else F.last_day(F.add_months(...))`; on month-end input
  `F.last_day(F.add_months("month_end", age))` is correct for age 0 too (the contract is month ends), so the
  conditional (4 lines) can go. The closure rule (amount > 0 = that month only) will not fit this helper either way;
  it needs a per-row carry length, so expect to rewrite `_with_carry`, not just the constant.
S1-07: accept (no)  criteria: E5, E1
  Hand-rolled check replaced by the shared `frames.require_columns`; -3 lines.
S1-08: accept (no)  criteria: E3, E1
  Inlines a one-caller node factory.
S1-09: accept (no)  criteria: E5, E2
  `dcore_account_events` uses `scoped()`; one scoping idiom, same plan.

### S2
S2-01: accept (no)  criteria: E2, E4
  Window then one `groupBy().agg` replaces summary + join-back + second aggregate: one join, one aggregate and two
  Expand nodes fewer on the largest A3 input. Best change of the round.
S2-02: accept (no)  criteria: E2, E1
  `_with_due` / `_with_paid` join the events directly: the two distinct-key side tables and their join-backs are gone.
S2-03 (held, needs catalog entries): accept in principle (no)  criteria: E2
  Three consumers recompute the dues plan today. Real saving, but a catalog edit (rule 6) and a user decision; keep it
  on the user list.
S2-04: accept (no)  criteria: E2
  Base agreements before the join: two bank-wide exchanges avoided.
S2-05: accept (no)  criteria: E2, E4
  Stagnation start as a window over rows: one aggregate and one join less, three consumers.
S2-06: n/a (dropped for S1-01).
S2-07: accept (no)  criteria: E2
  EOSB agreements scoped to the base CIFs before the join; two exchanges removed. `F.broadcast(mine)` after `scoped()`
  (which already broadcasts its key side) is a second hint on the scoped agreements: fine at persona scope.
S2-08: accept (no)  criteria: E2
  Two broadcast semi-joins add join operators but cut the range join to refusal accounts; net fewer rows shuffled.
S2-09: accept (no)  criteria: E2, E3
  The episode self-join is removed. The loop of four left joins duplicates `left_join_all` in spirit; it cannot use it
  because `left_join_all` keeps only `GRAIN` from the base (see N-5).
S2-10: accept (no)  criteria: E2, E4
  Two row_number windows become grouped `max(struct)` (partial aggregation). Ties now resolve by value, so reruns
  agree; the oracle passes.
S2-11: accept (no)  criteria: E2
  `F.broadcast(obs)` keeps the product table from shuffling. The obs rows are persona-scope (latest month) today; the
  hint must go if the persona scope widens (N-4).
S2-12 (held): accept (no)  criteria: E2
  Three raw-table exchanges removed for one hint on a one-row-per-card table. Cannot be gated (the module does not
  import in the mirror), so the user's UAT run is the check. Take it with the cc_raw_extract UAT grep.

### S3
S3-01 (held): accept (no)  criteria: E5, E1
  Two `require_columns` remain (`_common`, `frames`) with different message formats. -5 lines, one concept, and
  S1-07 already points the bureau node at the `frames` one. The only cost is the failure text of an aborted run, which
  is not data behaviour. Take it.
S3-02: accept (no)  criteria: E1 (2, rule-mandated), E7
  +27 lines of D2 fail-loud checks; the blocking-4 exception applies. Column lists are named once (`EPISODE`,
  `CYCLE_LEDGER`, `INSTALMENTS`) next to the builders that make them. See N-3: the same two-line pair is typed five
  times.
S3-03 (skipped): revise, re-raise in round 2 (no)  criteria: E1, E3
  Skipped correctly in stage 3. Now five A1 nodes take the whole `crx_persona` dict and read one key. Change: pass
  `params:crx_persona.persona_start_date` (a string, as `product_features` already does) to all five nodes and make
  `_floor` take the string. -5 subscripts, one parameter convention, no dict shape for A3 to learn.
S3-04: accept (no)  criteria: E1 (2, rule-mandated)
  Raw schema checks at the extract boundary; D2.
S3-05, S3-06, S3-08: n/a (dropped as duplicates).
S3-07: n/a (skipped, gain gone).
S3-09: accept (no)  criteria: E3
  Dict inputs; same lines, order-independent wiring.
S3-10 (partial): accept (no)  criteria: E5
  One `tags` list per pipeline function; neutral.
S3-11 (held): reject (blocking: no)  criteria: E1 (1)
  +30 lines to check the five signal tables that the same pipeline's builders just produced and already checked. A
  stale persisted table is a catalog hygiene problem, not a column-name problem. Drop it.

### S4
S4-01: accept (no)  criteria: E3 (2), E2
  Three single-caller helpers (`_contact_events`, `_contact_summary`, `_plan_after_refusal`) for a 113-line builder.
  Under rubric §4 I score E3 2 and leave the trade to R-O. It also removed a `too-many-locals` disable and
  `_contact_summary` is where S2-01's window lives, which is the part the pending DCORE rules touch.
S4-02: accept (no)  criteria: E3 (2)
  `_with_due` / `_with_paid` are single-caller but are the S2-02 joins by name; builder reads as the outcome rule.
S4-03: revise (blocking: no)  criteria: E3, E1
  `_plan_instalments` removes a nested closure: keep. `_require_plan_sources` (single caller, 25 lines, a new
  `# pylint: disable-next`) only moves the checks. Change: keep the checks in `build_instalments` but write them as a
  loop over `(frame, columns, source)` tuples; about -15 lines and no extra helper or disable.
S4-04 (reverted): accept the revert (no)  criteria: gate
  R0914 on the proposal alone; the Master was right. The A3 pipeline function stays as is.
S4-05: accept (no)  criteria: E1, E6
  One file-level `# ruff: noqa: F401` replaces ten per-line findings and the A1 `__all__`; -8 lines.
S4-06 (held): reject (blocking: yes, objection 3)  criteria: E3 (1)
  `_salary_rows` has one caller; after S1-06 the builder is already shorter and the carry change will edit
  `_with_carry`, not the source assembly. Moves 25 lines into a helper for no deletion.
S4-07: accept (no)  criteria: E3, E4, E1
  `labels=` from `DISPLAY_NAMES` is a real removal; `_income_source` / `_salary_stopped` are single-caller (E3 2) but
  take two pylint disables with them. Neutral overall.
S4-08: accept (no)  criteria: E5, E4
  `ASSET_TYPES` / `CREDIT_TYPES` shared by feature and consumer; `cif_column()` x3 replaces hand-typed casts.
S4-09: n/a (dropped, S1-07).
S4-10 (partial): accept (no)  criteria: E5, E1
  `_window` tuple helper becomes `_load_bound`; `history_floor` shared.
S4-11: accept (no)  criteria: E1, E4
  One ladder expression, not two; -5 lines.
S4-13: accept (no)  criteria: E6
  Ruff leftovers; neutral.
S4-14: accept (no)  criteria: E3 (2)
  `_run_step` / `_no_runs` hoisted out of `_followup_promises`; names the D-A3-29 fold. Same trade as S4-01.
S4-15: accept (no)  criteria: E3 (2)
  `_commitment_counts` single-caller; same trade.
S4-16 (held): accept (no)  criteria: E1 (3)
  The name `state_label` is wrong for point mapping. Five call sites, zero line change; touches A2 / A4 files. I do not
  mind either way; accept if R-I values the name.

### S7
B-01: accept (no)  criteria: E1  — unused constant.
B-02: accept (no)  criteria: E1, E3  — `pit_latest(anchor=)` never passed; A3 uses `window_agg(start=)` and its own
  `_anchor()`, so nothing is lost for the cycle ledger.
B-03: accept (no)  criteria: E1  — dead `max_months=None` branch.
B-04 (held): accept (no)  criteria: E1 (5)
  Scorecard `CAP`, `FORCE`, `Override.mode/to`, `high_min_dimensions`, `high_current`: nothing passes them, -18 net.
  It reopens run 1 D-2-3, so it is the user's call. Caveat for the user: if the pending A3 promise points need a cap or
  a forced rung, they come back with the points decision; they are two lines to re-add against the spec then.
B-05: accept (no)  criteria: E6  — stale constant name in the README.
B-06 (held): accept (no)  criteria: E1
  `build_instalments` outputs two columns nobody reads, -2 lines; the persisted columns need the user.
Group A (`_spine_utils`, `rl_a4_spine`, `rl_spell_table`, `cc_spell`, `build_cc_limits`): accept (no)  criteria: E1 (5)
  About -1,060 lines, the largest removal on the table. Waits on the workplace grep.

## Files (merged tree), tier L and touched files

Weights: E1 25, E2 20, E3 15, E4 15, E5 10, E6 5, E7 10. Untouched criteria score 3.

pipelines/crx_persona/_common.py  E1 4 · E2 5 · E3 4 · E4 4 · E5 3 · E6 4 · E7 4  weighted 4.1  — -10 lines, `lookback_floor` and the `anchor` parameter gone (:99-120), `scoped()` reused in `dcore_account_events` (:281); second `require_columns` still lives in `frames.py` (E5).
nodes/utils/frames.py  E1 4 · E2 3 · E3 4 · E4 3 · E5 4 · E6 4 · E7 4  weighted 3.65  — `history_floor` replaces three copies of `months_back(start, n - 1)`.
pipelines/crx_persona/a3_credibility/promises.py (new)  E1 3 · E2 5 · E3 3 · E4 4 · E5 4 · E6 4 · E7 5  weighted 3.9  — moved code plus S2-02 / S4-02 chain; `_cutoff` once per event table (:139), single rule file for the pending deadline / points decisions.
pipelines/crx_persona/a3_credibility/sources.py  E1 4 · E2 4 · E3 3 · E4 4 · E5 4 · E6 4 · E7 4  weighted 3.85  — 372 -> 199; `_require_plan_sources` (:75) is the one single-caller helper to fold back.
pipelines/crx_persona/a3_credibility/signals.py  E1 2 · E2 5 · E3 3 · E4 4 · E5 3 · E6 4 · E7 4  weighted 3.45  — +56 lines (checks, four helpers); contact in one pass (:350-385); the `episode` / `ledger` check pair is typed five times (:110, :162, :215, :417).
pipelines/crx_persona/a3_credibility/classify.py  E1 3 · E2 5 · E3 4 · E4 4 · E5 3 · E6 4 · E7 4  weighted 3.85  — self-join removed; `for part in (...)` (:77) is a private `left_join_all`.
pipelines/crx_persona/a3_credibility/constants.py  E1 3 · E2 3 · E3 4 · E4 3 · E5 4 · E6 4 · E7 5  weighted 3.5  — one `promise_deadline`, one `HISTORY_MONTHS`; the three CC cycle constants now sit in the one module that uses them.
pipelines/crx_persona/a3_credibility/pipeline.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 4  weighted 3.15  — import change and a shorter diagram; S4-04 reverted so the E501 lines stay.
pipelines/crx_persona/a3_credibility/__init__.py  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.3  — one `noqa`, no ten-line findings.
pipelines/crx_persona/cc_a3_payment_credibility/nodes.py  E1 3 · E2 5 · E3 3 · E4 4 · E5 4 · E6 4 · E7 4  weighted 3.8  — `billed` once, stagnation as a window (:70-85); `build_cc_acct_windows` now beside its sole caller.
pipelines/crx_persona/a1_ability/signals.py  E1 2 · E2 5 · E3 3 · E4 4 · E5 3 · E6 4 · E7 5  weighted 3.55  — +33 lines (carry generality, five `crx_persona` parameters); four actions gone; `.first()` at :352 remains (baseline); `_floor` (:77) duplicated by the RL anchor.
pipelines/crx_persona/a1_ability/classify.py  E1 3 · E2 3 · E3 3 · E4 4 · E5 3 · E6 4 · E7 4  weighted 3.3  — `labels` from `DISPLAY_NAMES`; two single-caller helpers (:196-213) for pylint.
pipelines/crx_persona/a1_ability/pipeline.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 4  weighted 3.15  — three more node inputs, redrawn diagram.
pipelines/crx_persona/a1_ability/__init__.py  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.3  — `__all__` gone.
pipelines/crx_persona/rl_a1_ability/nodes.py  E1 3 · E2 5 · E3 3 · E4 3 · E5 2 · E6 4 · E7 3  weighted 3.4  — job removed (:29); re-types `history_floor(...isoformat())` that A1 `_floor` also does.
pipelines/crx_persona/rl_a1_ability/pipeline.py, cc_a1_ability/nodes.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.05  — wiring / comment only.
pipelines/crx_persona/scoring_engine.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.05  — docstring only; B-04 would be the real change.
pipelines/crx_persona/cc_raw_extract/nodes.py  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 5 · E7 3  weighted 3.4  — -147 lines (docstrings, window builder moved out) against +requires; S2-12 broadcast still open.
pipelines/crx_persona/cc_raw_extract/{__init__,_window_utils,pipeline}.py  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 5 · E7 3  weighted 3.4  — ticket history removed.
nodes/primary/products/prm_products.py  E1 3 · E2 5 · E3 4 · E4 5 · E5 4 · E6 4 · E7 3  weighted 4.0  — grouped `max(struct)` for latest-in-month (:38), one `_load_bound`.
nodes/features/products/feat_cif_cross_product.py  E1 3 · E2 3 · E3 3 · E4 4 · E5 4 · E6 4 · E7 3  weighted 3.3  — shared type tuples (:55-56), `history_floor`.
nodes/features/bureau/feat_cif_bureau_bounces_monthly.py  E1 4 · E2 3 · E3 4 · E4 3 · E5 4 · E6 4 · E7 3  weighted 3.45  — shared check.
nodes/features/bureau/feat_cif_bureau_salary_monthly.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 4  weighted 3.15  — docstring only.
pipelines/bureau/salary_bounces.py  E1 3 · E2 3 · E3 3 · E4 3 · E5 4 · E6 3 · E7 3  weighted 3.1  — one `tags` list.
pipelines/products/features.py  E1 4 · E2 3 · E3 5 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.4  — one-caller factory inlined.

Weighted average, all touched tier L files: **3.5**. Shared layer and engines (`_common`, `frames`, `promises`, `sources`,
`classify`, A1 `signals`): **3.75**, under my 4.0 target; the gap is E1 (net +65 lines) and E5 (two `require_columns`,
`_floor` copies). Spark actions: below baseline.

### Five largest remaining removals
1. Group A dead packages, about -1,060 lines (held on the workplace grep).
2. B-04 Scorecard modes -18 and B-06 -2 (user decisions).
3. S3-01 single `require_columns`, -5, one concept.
4. A3 builders: one `_require_inputs(episode, ledger)` helper or table, about -6, and S4-03's loop, about -15.
5. `_floor` / RL anchor shared, plus S3-03 string parameter, about -8.

## New issues

N-1 [a1_ability/signals.py:77, rl_a1_ability/nodes.py:29] The persona-start floor is computed in two places (`_floor` returning an ISO string, and the RL anchor re-typing `history_floor(...).isoformat()`); A3 will need it as well → move `_floor` to `_common` as `source_floor(persona_start_date, months) -> str` (after S3-03 takes the string); RL anchor calls it. About -3 lines, one concept → S1 / S3.
N-2 [a1_ability/signals.py:130-160, 245, 395, 450; pipeline.py:47,83,96] Five nodes receive the whole `crx_persona` dict to read one key → S3-03 as written under Proposals (string parameter). Not a correctness risk.
N-3 [a3_credibility/signals.py:110,162-163,215-216,417-420] The same `require_columns(episode, EPISODE, ...)` (and the ledger twin) is repeated at the top of five builders → a table-driven `_require(**{"A3 episode": (episode, EPISODE), ...})` is not shorter; the real fix is checking the episode once, where it is built (`build_a3_episode` output is the contract) and keeping only the ledger and event checks in the consumers. About -5 lines → S3.
N-4 [a1_ability/signals.py:315, 482; cc_raw_extract (S2-12)] Broadcast hints without a size bound (`F.broadcast(obs)` is every obs row of the model, not distinct keys). Fine at latest-month persona scope; if scope widens, drop the hint or use `scoped()`'s distinct-key form. Comment-free; note for the test owner → none, watch item.
N-5 [a3_credibility/classify.py:77, _common.py `left_join_all`] `build_a3_credibility` hand-rolls `left_join_all` because the shared helper keeps only `GRAIN` from the base. Let `left_join_all` accept `keep=base.columns` (one optional argument, A1 never sets it, so it is an unused-parameter risk for objection 3): rather leave the loop, three lines. No action; recorded so it is not raised twice.
N-6 [a1_ability/signals.py:352] `_require_returns_from` is still one Spark job per A1 run (`returns.agg(min).first()`), the only guard action left in A1 after S1-01. It protects a real failure (returns reloaded after a persona start change) → keep, but fold into the node's existing logging action if a logging pass is ever added; no change now.
N-7 [a1_ability/signals.py:108-130] `_with_carry` will not host the closure rule (carry length per row, amount > 0 = that month only). When the DE ships `is_closure`, rewrite the helper rather than extend the constant; in the meantime apply the age-0 simplification in S1-06 so the rewrite starts from less code → S1 (round 2, optional).

## Summary line for the Master

Accepted: all applied proposals (non-blocking). Held: take S3-01, S2-12, B-04, B-06, Group A, S4-16 and S2-03 (user items); reject S3-11 and S4-06 (S4-06 blocking, objection 3); revise S4-03 and S3-03; S4-04 revert correct. Weighted 3.5 (shared layer 3.75). Net +65 `src` lines is the one miss against my line target.
