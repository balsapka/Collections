# R-E review, round 2 (efficiency engineer)

Frozen rubric `rubrics/efficiency.md`. HEAD `7ae2a08`, diff against `2942237` (src, conf, checks).
Read: PLAN (incl. Axis stability), decisions D-2-1/D-2-2, round 1 triage and my round 1 review,
S1-S5 logs, gates. Other round 2 reviews not read. Gates taken as green per `gates.md`.

## Summary

- My round 1 blocking objections: S4-02, S4-03 and S4-09 resolved; S1-07/S1-08 resolved on the
  condition I set (a test case) but still have no tier-L caller (R-1 stands, not blocking). One new
  blocking item: the unused `Scorecard` modes (S1-R2-01).
- Passes: round 2 removes more. CC A4 restructure flag: join + second groupBy gone for one
  `min(struct)` aggregate. A2 DCORE: the `row_number` window and sort gone, one aggregate, and
  S2's `explain()` shows 7 -> 7 Exchange, Window 1 -> 0, Sort 5 -> 4. Liquidity legs now cut at the
  persona floor before `scoped` and the join. No new action (9).
- Tier L 4,119 -> 4,087 (-32); baseline 3,893, so **my target (no higher than baseline) is still
  missed by 194**. See "Line outcome".

## 1. Items

### S1 architecture
S1-R2-01 `Scorecard` / `Dimension` / `Override` replace `StateLadder`: **revise**  (blocking: yes, #3)  criteria: E1, E3, E7
  A1 sets none of `CAP`, `FORCE`, `high_min_dimensions`, `high_current`, `Dimension.silent`,
  `Override.to`. They are used only by the 14 spec rows, which exist to exercise them
  (`scoring_engine.py:21,38-43,54-55,76-79`). That is "a parameter or mode no current caller
  sets", written "for A3". The core is good: `A1 classify` -9 lines, `points_from_level` and
  `StateLadder` gone, one declaration for the ladder, the reason column back. E7 is a real 5 for
  the shape. Scored 3.25 on the file (E1 2: +25 net).
  Wanted: keep `DEMOTE`, `silent`, `unknown_also`, reason; move `CAP`, `FORCE`,
  `high_min_dimensions`, `high_current` (about 12 lines in `score`, 3 constants/fields, 6-8 spec rows)
  to the A3 bundle where the first caller lands. If R-O keeps them (as D-1-2 kept `episode_start`),
  I record the objection and do not ask for a revert: the budget was set in the triage and met.
  Smaller points: `fired` is rebuilt into the `rung`, `unknown` and select expressions, and
  `a1_*_points`, `_override`, `_reason` are computed then dropped by A1's final select (Catalyst
  prunes them; fine, but the sort_array/struct "top dimension" is the heaviest expression and has
  no consumer until Q-26).
S1-R2-02 `build_a1_ability(..., **signals)` + `FAMILIES`: accept  (blocking: no)  criteria: E1, E4
  Four positional DataFrame parameters and the pylint disable become `**signals`; two `withColumn`
  become one loop. Net 0 lines, so no gain beyond A3-style extension. Weakness: the join order now
  depends on the node inputs dict order and the signature no longer says what is required; if a
  family is missing, `SCORECARD.score` fails late. A one-line `require_columns` on the level columns
  is not needed (Spark fails on the missing column). Score 3.3.
S1-R2-03 `GONE_DARK_DAYS` to `_common`: accept  (blocking: no)  criteria: E5
  Net 0; A3 is the second reader and never imports A2. Score 3.4. N-11 (two per-segment dicts, one
  lookup shape) is now two tables in `_common`: note for the A3 session.
S1-R2-04 `episode_left_censored` + checked cases: accept  (blocking: no)  criteria: E1, E7
  My round 1 objection (S1-07/S1-08 "if kept, must get a test case") is **resolved on its own
  terms**: `check_anchor` covers `episode_start` and both `window_agg(start=)` bounds. It does not
  create a tier-L caller: 57 lines of `anchor.py` and the `start=` branch of `window_agg` are still
  exercised only by `checks/`. `anchor.py` grew +5 (a docstring and a comment); the comment on
  `history_months - 1 - months_before_spell` is a one-line "what", acceptable. Not blocking,
  per R-1. If the A3 bundle slips, S7 deletes both.
S1-R2-05 `build_dpd_sequences` to `require_columns`: accept  (blocking: no)  criteria: E1, E5
  -6 lines, one hand-written check gone, an E501 gone. Score 4.2.
S1-R2-06 `string_key` in RL A4: accept  (blocking: no)  criteria: E5
  Five `trim(cast)` copies to the shared helper; net 0. The "flagged, not changed" table is useful
  and adds no code. Score 3.8.
S1-R2-07 A3 target-shape text: accept (no code).

### S3 conventions
S3-04 tag normalisation: accept  (blocking: no)  criteria: E5, E1
  `TAGS` once per pipeline file, pipeline-level duplicates dropped, `rl_b1` gone; net -4. My N-8
  `persona_tags()` stays dropped (R-3). Q-16 note in the `cc_full_history` docstring (+2): an
  accurate why. Score 3.8.

### S2 performance
S2-06 `_restructure_blind_spot`: accept  (blocking: no)  criteria: E2, E1, E4
  This is the item I asked for. One `groupBy().agg(min(struct))` replaces aggregate -> join ->
  filter -> aggregate over the full CC billing history: a join and a shuffle of the largest A4
  input gone. +3 lines against +2 budget (the wrapped docstring). The two-line tie comment is
  load-bearing (negated bucket). Score 4.3. Round 1 note N-9 resolved.
N-3 window-free DCORE + `_gone_dark`: accept  (blocking: no)  criteria: E2, E4, E1
  Window, sort and three aggregates (`_n_last`, `_failed_last`, `_oldest_last`) become one
  `slice(sort_array(collect_list(when(attempt, struct)))` and a named rule; non-attempt days are
  never sorted, which answers my N-3. Evidence is a plan operator count, not a PROD run: the
  `collect_list` is bounded by attempt days per (account, observation), and S2 names the
  fallback. `build_dcore_signals` 78 -> 69, +2 with `_gone_dark`. `F.forall` needs pyspark >= 3.1
  (workplace version to confirm; S2 gives the `array_contains` equivalent). Score 4.2.
S2-02 naming (`_casa_legs`, `casa_active`, `casa_held`): accept  (blocking: no)  criteria: E3, E6
  `_casa_legs` has one caller (+7 lines for the function with its docstring); I score E3 2,
  but R-O ordered it (triage S2-02 row) and it names the union that S11 reads. Score 3.0.
Q-14(b) liquidity floor from `crx_persona`: accept  (blocking: no)  criteria: E2, E3
  Two `.filter(month_end >= window_start(..., first))` before `scoped` and the join; S2 argues
  correctly that the obs base starts at the persona start month, so no window reads older rows.
  A literal predicate on the source with no action (unlike `lookback_floor`, which runs a job).
  Cost: a new node input `crx_persona`, a keyword parameter and 5 lines. It is the better form
  of the floor; **N-R2-1** moves the other readers to it. Score 3.9.
N-4: no change, measurement recorded: accept (as ruled).

### S4 readability
S4-02 `__all__` -> `# ruff: noqa: F401`, `_month_label`, docstring cut: accept  (blocking: no)  criteria: E1, E6
  `__init__.py` 134 -> 61 lines. Round 1 blocking resolved. Score 4.2 (file 3.7 below). `# isort:
  split` is a small oddity; fine.
S4-03 part (`_monthly_rows_per_account`, `_spine_rows_with_history`): accept  (blocking: no)  criteria: E3, E1
  Exactly the narrowed form I allowed: two data helpers, no UDF helpers, no hints. +6 lines, one
  caller each (E3 2), but `build_dpd_sequences` 122 -> about 90 and `build_deterioration` 104 ->
  about 85 and two pylint disables gone. Round 1 blocking resolved. Score 3.2.
S4-09 RL half (`_original_loan_months`): accept  (blocking: no)  criteria: E1, E3
  Net -2 against a +8 budget; the nested `frame()` closure is gone for one generator unpack; the
  docstring absorbed the "Original rows" paragraph. One caller; the helper's body is the old
  query moved, so the gain is the closure, not the line count. Round 1 blocking resolved. Score 3.4.
Q3 / Q4 predicates + Q ids on `STATE_RULES`: accept  (blocking: no)  criteria: E3, E6
  +3 lines for two single-caller predicates; the `# Q1..# Q4` collapse (6 comment lines gone) pays
  for most of it. Score 3.1. I agree with not mapping state names from `STATES`.
A1 label constants, `kv` -> `pair`: accept  (blocking: no)  criteria: E6
  Renames, +1. Values unchanged. `SOURCE_INTERNAL`/`SOURCE_BUREAU` still used in one function
  (N-6 half resolved: no more `BUREAU` vs `BUREAU_BOUNCE`). Score 3.0.
`black -C` compaction: see line outcome.

### S5 docstrings
S5: accept  (blocking: no)  criteria: E6
  -5 net on tier L; `_ship_by_value` 7 -> 3 lines, the `build_cc_dpd_sequences` docstring stops
  repeating the helper. `_log_sequence_stats` comment +2 (it is an interface line the function
  lacked). The Scorecard docstring is 11 lines for an engine whose A1 use is 10; accurate, and the
  `score` docstring says what columns come out. Score 3.9.

## 2. Files (tier L, changed in round 2)

Criteria: E1 lines · E2 passes · E3 indirection · E4 PySpark · E5 duplication · E6 docs · E7 A3.
Weighted = (25 E1 + 20 E2 + 15 E3 + 15 E4 + 10 E5 + 5 E6 + 10 E7) / 100.

- `_common.py`  E1 3 · E2 4 · E3 4 · E4 5 · E5 5 · E6 4 · E7 4  weighted 4.0  — net +1 (`GONE_DARK_DAYS` +3, `pit_latest` -2); `pit_latest` names `row_date`/`anchor_date` (`:117-121`). At the shared-layer target. Remaining: `scoped` inside `pit_latest` (ruled, measured in the bundle check).
- `scoring_engine.py`  E1 2 · E2 3 · E3 3 · E4 4 · E5 5 · E6 4 · E7 4  weighted 3.25  — +25 (`:21-107`), unused modes (see S1-R2-01). Below the 4.0 engine target.
- `_dpd_journey/__init__.py`  E1 5 · E2 3 · E3 4 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.7  — 134 -> 61 lines, no `__all__`.
- `_dpd_journey/_dates.py`  E1 4 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.3  — `_month_label` gone.
- `_dpd_journey/anchor.py`  E1 1 · E2 4 · E3 2 · E4 4 · E5 5 · E6 4 · E7 5  weighted 3.15  — right shape, tested, still no tier-L caller (`:19-58`).
- `_dpd_journey/spark.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 5 · E6 4 · E7 3  weighted 3.4  — two helpers, `require_columns`; net -3 of which -5 is `black -C`.
- `_dpd_journey/states.py`  E1 2 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 2.9  — +3 for Q3/Q4 predicates; Q1-Q4 predicate set at least consistent (`:62-81`).
- `_dpd_journey/logging.py`  E1 3 · others as round 1  weighted 4.1  — +2 comment lines only.
- `a1_ability/classify.py`  E1 4 · E2 3 · E3 3 · E4 5 · E5 4 · E6 4 · E7 4  weighted 3.8  — -9, one `Scorecard`, `FAMILIES` loop (`:128-170`).
- `a1_ability/signals.py`  E1 2 · E2 4 · E3 2 · E4 4 · E5 3 · E6 4 · E7 3  weighted 3.0  — +12 net: `_casa_legs` (one caller), the param floor (income and distress still use the job-running `lookback_floor`), renames. A1 is "structure only"; stays.
- `a2_locatability/signals.py`  E1 4 · E2 5 · E3 3 · E4 4 · E5 5 · E6 4 · E7 4  weighted 4.15  — window and three aggregates gone, one `_gone_dark` rule (`:198-210,240-255`), `GONE_DARK_DAYS` imported.
- `cc_a4_deterioration/nodes.py`  E1 3 · E2 5 · E3 3 · E4 4 · E5 3 · E6 4 · E7 3  weighted 3.6  — join and groupBy gone (`:29-46`), net -3.
- `rl_a4_deterioration/nodes.py`  E1 4 · E2 3 · E3 3 · E4 4 · E5 4 · E6 4 · E7 3  weighted 3.55  — -2, closure gone, `string_key`.
- `*_pipeline.py` (A4, full history), `a1_ability/pipeline.py`  E1 4 · rest 3  weighted 3.4  — `TAGS` once.
- Files not changed in round 2 keep their round 1 scores.

Shared layer / engines against the 4.0 target: `_common` 4.0 met; `a2 signals` 4.15 met;
`scoring_engine` 3.25 not met; `anchor` 3.15 not met (no caller).

## 3. Line outcome

Tier L 4,087 = baseline 3,893 + 194; round 1 was +226; round 2 is -32 against a budget of -25
(met on the Master's number). Breakdown of the -32:
- Real removal: `__init__` -73 (`__all__` -38, `_month_label` -7, docstring and exports),
  `build_dpd_sequences` check -6, the CC A4 flag -3, tags -4, S5 -5, the Q3/Q4 comment collapse.
- Added: `Scorecard` +25 (A3 design-in, separately budgeted), `_casa_legs`, Q-14 floor, S4-03 helpers,
  `_gone_dark`, anchor docstring, `_dpd_journey` Q predicates.
- **`black -C` (about 18 lines): I do not count it.** It deletes trailing commas so black joins
  argument lists on one line: the same tokens, the same concepts and the same plan. It makes the
  files denser, and a later `black` run restores the commas wherever someone adds an argument, so the
  gain is not stable (S4 notes `git show e4a0294` reverts it). My line metric is a proxy for what a
  reader holds in their head; this moves none of it. Without it the round is **-14**, which
  misses the -25 budget by 11 and leaves tier L at 4,105. I would not reject the compaction
  (it is the repo's own formatter at work and several of the joined lists are more readable), and
  I accept the Master's 4,087 as the working number, but I report -14 as the real figure and note
  the same applies to the other direction: line-wrapping that hits the 88-column limit counted
  against round 1.
- The remaining 194 over baseline is mostly structure that A3 and the redesigns use: shared layer
  (`_common` +88 after round 1), `anchor.py` and the `start=` branch (+58, no tier-L caller), `Scorecard` (+25).
  Under the axis-stability rule I do not expect tier L to fall below baseline before the A3 bundle
  lands; at that point `_signals_common` and the A3 waterfall deletions (~2,300 lines) dwarf it.
  I withdraw the baseline target as a round 3 blocker and keep it as the line to watch.

## 4. New issues for round 3 (consistency and convergence only)

N-R2-1 [`_common.lookback_floor` (`:168-172`), `a1_ability/signals.py:164,376,427`] Q-14(b) shows the
  floor needs no Spark action: `window_start(M, persona_start_date)` from the `crx_persona` param.
  `lookback_floor` runs `base.agg(min).first()` (a job) at each of its call sites, three in A1
  alone, and now has a second spelling next to the liquidity node's. Move income, distress and the
  A2 reads to the param form and delete `lookback_floor`: fewer actions (the obs base already starts
  at the persona start month, so the value is the same or earlier, never later; S2's argument).
  About -5 lines, 3+ jobs. Output-neutral only if the floor stays <= the min observation window;
  S2's proof covers it. → S2 / S1 (shared-layer decision, say so in the commit)
N-R2-2 [`scoring_engine.py`] The unused `CAP`/`FORCE`/`high_min_dimensions`/`high_current` (S1-R2-01).
  Move to the A3 bundle, or R-O records a waiver. About -20 lines with their spec rows. → S1 / R-O
N-R2-3 [`_common.py` `WINDOW_MONTHS`, `GONE_DARK_DAYS`] Two per-segment dicts with the same keys are
  now side by side. Round 1's N-11 said `for_model` at the third table; A3's D-A3-19 diagnostic is
  the third reader of the second, not a third table. No action; recheck at the A3 bundle.
N-R2-4 [`build_a1_ability(**signals)`] If the Kedro dict order changes, the join order changes but
  outputs do not (left joins on `GRAIN`, column names distinct). A one-line comment that order is
  immaterial would stop a reader checking. → S5 (text only)
