# R-E review, round 1 (efficiency engineer)

Frozen rubric `rubrics/efficiency.md`. Merged tree HEAD `5c24553`, diff against `d1ad38a`.
Read: PLAN §2-§3, scorecard, merge_log, decisions, gates, all proposals, a3_handoff, metrics
(round 1 vs baseline). The other reviews were not read. Gates are taken as green per
`gates.md`; behaviour is not scored.

## Summary

- Spark actions in tier L: 11 -> 9 (target met). Passes: A1 liquidity 5 joins -> 2, A1 income one
  groupBy and one join gone, A1 bureau carry full join -> union + groupBy, A2 DCORE three
  aggregates over the event table -> one window + one aggregate (account-days reduced before the
  observation join), A2 way4 window sort -> struct-max, `pit_latest` window -> struct-max, RL A4
  driver `collect` gone, source pruning (`scoped`, `since`) added. This is where the round pays.
- Tier D: -7,028 lines, no remaining reader. Fine.
- Tier L lines: 3,893 -> 4,130 (+237). **My target (no higher than baseline) is not met.** The
  growth is in the shared layer (`_common` +88), `anchor.py` (+52, no caller), `_dpd_journey/
  __init__.py` (+43, a 38-line `__all__`), A1 signals (+38), and the S4 splits. Round 2 has about
  200 lines of removals available (list below), enough to get under baseline.
- Shared layer / engine score 3.75 (`_common`), 2.3 (`_dpd_journey/__init__`), 3.1 (`anchor`),
  against my 4.0 target. Round 2 work: remove the unused `start=` / `episode_start`, shrink
  `__init__`, drop the redundant `scoped` call in `pit_latest`.
- Two blocking items stand on the merged tree: S1-07 and S1-08 (nothing calls them) and S4-02
  (`__all__` of 38 lines to silence a finding the project already ignores).

## Proposals

### S7 dead code
S7 (patch + 12-file delete + three dead symbols): accept  (blocking: no)  criteria: E1, E5
  -7,028 lines, 20 catalog entries, 4 registry entries, `parse_yyyymmdd`, `priority_reason`,
  `SEGMENTS`. The moved `build_rl_depart_spine` is byte-identical. Follow-up: S1-06 left
  `_dates._month_label` with no caller (N-1).

### S1 architecture
S1-01 (segment map and `segment()` in `_common`): accept  (blocking: no)  criteria: E1, E3, E5
  `segment` has four callers (`window_months`, `gone_dark_days`, `journey_params`, CC A1 anchor)
  and replaces three copies of the KeyError/ValueError check; `MODEL_ID_SEGMENT` stops pointing
  from `_common` into the engine. Plus 6 lines in `_common`, minus 20 in `constants.py`. Score 4.0.
S1-02 (`string_key` in `_common`): accept  (blocking: no)  criteria: E1, E5
  Three copies of one function become one (-26 lines), A3's fourth is a handoff. Score 4.6.
S1-03 (`window_start` public, `(months, anchor=None)`): accept  (blocking: no)  criteria: E5, E1
  The `_common` and A2 copies are one; four callers. Score 4.3.
S1-04 (`state_label`): accept  (blocking: no)  criteria: E5, E4
  Three `create_map` copies (A1, A2, A4) become one; call sites shorter. Score 4.3.
S1-05 (`dcore_account_events` in `_common`): accept  (blocking: no)  criteria: E5, E7
  A move with one caller today (A2, via `_dcore_days`). It passes my rule only because A3
  (D-A3-7) is the second caller; if the A3 session does not call it, it goes back to A2. Net 0
  lines. The inner `text()` closure is used four times and earns its place. Score 3.6.
S1-06 (one state logger, `log_state_stats` over `log_latest_month(latest_per_account=)`):
  accept  (blocking: no)  criteria: E1, E5, E2
  -29 lines in `logging.py`, one Spark job as before, A4 now shares the A1/A2 log. The flag is set
  by a live caller. Score 4.4.
S1-07 (`episode_start`, `_dpd_journey/anchor.py`): **revise**  (blocking: yes, #3, no caller)  criteria: E1, E3, E7
  52 lines, `grep` finds no caller in tier L, tier K or the tests. E7 is a 5: the shape is right (one
  `pit_latest` over the A4 row, no spell join, `episode_left_censored` returned for S6-H03). But
  with E1 at 1 and E3 at 1 it weighs 2.4. Fix, either one: (a) move the file into the A3 bundle
  where its first caller lands (my preference; nothing is lost, the diff is in S1.md), or (b) keep
  it and add the first caller in round 2. Master decided D-1-2 to merge it; I record the
  objection and leave the call to R-O.
S1-08 (`window_agg(start=)`): **revise**  (blocking: yes, #3, parameter no caller sets)  criteria: E1, E3, E7
  Six lines (`lower`, `greatest`, the select splat) for A3's window `[anchor, observation_date)`.
  Same remedy as S1-07: land it with the A3 caller. The signature is the right one for A3
  (per-row start), so the A3 session loses nothing. If kept, `start` must get a test case in
  `a1_engine_spec` or the A3 check, or it is dead code in the next S7 pass.

### S3 conventions
S3-01 (dict inputs, obs base and full histories) and S3-02 (dict inputs, A4): **revise**  (blocking: yes, #4)  criteria: E1, E5
  Dict form repeats every dataset name as key and value (`"cc_spine": "cc_spine"`), +4 to +20
  lines a pipeline file, no deleted counterpart. The gain is a consistency one (A1/A2/A3 style) and
  a swapped dataset in a positional list becomes a build error, both R-O/R-I values. My score is
  2.95. Not a gate; I do not ask for a revert. I ask R-O to waive blocking 4 for this, because
  the convention is already in A1/A2.
S3-03 (`require_columns` on spines and sources): accept  (blocking: no)  criteria: E1
  The rules allow the line growth. It pushes `build_rl_full_history` to 54 lines; a column list
  per node is the cost of D2. Score 3.2.
S3-05 (`crx_persona` required on RL full history): accept  (blocking: no)  criteria: E1, E3
  Removes `or {}` and a default no caller used. Score 3.8.
S3-06 (registry wrap) and S3-07 (catalog comments): accept  (blocking: no)  criteria: E6
  Neutral. Catalog net -188 lines is S7.
S3-04 (tag normalisation, held): accept when Q-15 is answered yes  (blocking: no)  criteria: E5, E1
  It removes `rl_b1` (a ticket id), the repeated literal lists (`tags=TAGS`) and the pipeline-level
  `tags=["crx_persona"]`; net a few lines down, and A1..A4 end with one tag set, which the A3 handoff
  also wants. Score 3.7. It is the only way to one tag set, so it passes the 3.0-3.9 rule. Optional
  step after it: `persona_tags(axis, name)` in `_common`, because A1, A2, A3 and A4 would each carry
  the same five-item list (N-8).

### S2 performance
S2-01 (`scoped` + `pit_latest` as one aggregate): accept  (blocking: no)  criteria: E2, E4, E5
  Window + row_number + filter + select -> `groupBy().agg(max(struct))`; `scoped` has five
  callers. Ties and NULL order are equivalent (struct order puts NULL smallest, so max matches
  `desc_nulls_last`); golden agrees. Caveat in N-4: inside `pit_latest` the base join already
  restricts keys, so `scoped` there adds a broadcast + distinct stage that the inner join does not
  need. Score 4.2.
S2-02 (A1 one join per source): accept  (blocking: no)  criteria: E2, E4
  Liquidity from five source reads and joins to two; income loses a groupBy and a join; the
  `legs` union is hand-built but short. The closing `select` exists only to keep column order
  (D-1-4, hard rule 1); that is a cost of the rule, not of the change. Score 4.1.
S2-03 (A2 DCORE account-days, re-based on S1-05): accept  (blocking: no)  criteria: E2, E1
  Three aggregates over the event table (`records`, `calls_summary`, `last_days`) and two joins
  become one window + one aggregate, with events reduced to account-days before they meet the
  observation rows. N-3 covers one risk: the `rank` window now sorts every DCORE day, not only
  call days. Score 4.3.
S2-04 (A2 scoped location / demographics / Way4, struct-max for the latest card snapshot):
  accept  (blocking: no)  criteria: E2, E4
  Window sort per `(GRAIN, contract_id)` -> `max(struct)`; sources pruned before the join. Score 4.2.
S2-05 (distress floor pruning): accept  (blocking: no)  criteria: E2
  Bounces and returns are cut at `since` before the join, as the payment-order branch's table
  already was. Score 4.0.
S2-07 (RL A4 without `collect`): accept  (blocking: no)  criteria: E2, E4
  Driver round trip over all spine accounts removed; chain frames semi-joined to history instead.
  Score 4.2.

### S4 readability
S4-01 (A1 threshold names, `INCOME_POINTS`, `_shows_evidence`): accept  (blocking: no)  criteria: E4, E6
  +12 lines, but three repeated `coalesce(col, 0) >= DEMIN` expressions become one helper with three
  callers, and the constants carry the spec cell. E1 is 2; the trade is R-I's. Score 3.1.
S4-02 (`__all__`, public `log_state_stats`): **revise**  (blocking: yes, #4)  criteria: E1, E3
  `_dpd_journey/__init__.py` grows 85 -> 128 lines. Thirty-eight of them are `__all__`, and most
  entries are private names (`_glitches`, `_runs`, `_repair`, `_mean`, `_month_idx`, `_month_label`,
  `_FEATURES`, ...) that exist for the workplace tests. The project's own lint rule is to ignore
  F401 in `__init__.py` (CLAUDE.local.md), which is one config line. Wanted: delete `__all__`,
  keep the re-exports tests need, add `# ruff: noqa: F401` (or the per-file ignore). That is about
  -40 lines and +41 ruff findings back, which the gate counts as a pass either way. Keep the
  `log_state_stats` rename.
S4-04 (A2 split: `_latest_evidence`, `_location_rule`, `_cif_rows`): accept  (blocking: no)  criteria: E3, E1
  `_cif_rows` has three callers and removes three copies of the same filter. `_location_rule` names
  rules L1-L4, so the scorecard keeps it. `_latest_evidence` is one caller and names nothing: E3 2.
  I would inline it; R-O decides. Score 3.2.
S4-05 (A1 distress split): accept  (blocking: no)  criteria: E3, E2
  `_require_returns_from` and `_distress_events` have one caller each, but they carry the fail-loud
  contract and the S2-05 floor. `_flag` leaves a closure (neutral). Score 3.2.
S4-06 (`assign_state` predicates): accept  (blocking: no)  criteria: E3
  Two single-caller predicates that name Q1 and Q2; `assign_state` loses its
  `too-many-arguments` disable. Scorecard rule: keep when it names a spec rule. Score 3.1.
S4-07 (`_shift_cycle_bills`): accept  (blocking: no)  criteria: E3, E1
  One caller, +8 lines; the only gain is two pylint disables gone. Acceptable at R-I's request; I
  would not have proposed it. Score 2.9, so the 3.0 floor says revise, but the change is local
  and the harness covers it; I do not object.
S4-10 (`SEG_60_180` / `SEG_180_PLUS`): accept  (blocking: no)  criteria: E5, E1
  Used in `_common`, `params`, A2, CC A1 anchor. Score 3.8.
S4-11 (A2 `TAGS`): accept  (blocking: no)  criteria: E5
  Neutral; S3-04 would make the pattern general. Score 3.4.

### S5 docstrings
S5 (28 files, comments only): accept  (blocking: no)  criteria: E6
  Ticket ids, O-numbers, "amended", "bundle 13", T43 history removed; spec cells (D-A2-n, S-n)
  added where they say which rule the code is. Net +11 lines (blocking 8 asks for no growth
  that says nothing new; these say a rule id, so I let it pass). Remaining weak spots:
  `_dpd_journey/__init__.py` (60-line module docstring that repeats METHODOLOGY.md and
  `states.py`) and `_common.window_agg`, which cites D-A3-2 for a parameter nobody sets. Score 3.6.

### Reverted by gate 2 (D-1-9, D-1-10, D-1-11)
S2-06 (CC A4 restructure flag as one aggregate): **bring back in round 2**, comment rewrapped
  (blocking: no)  criteria: E2, E1
  `min(struct(obs_date, -bucket))` replaces aggregate -> self-join -> filter -> aggregate over the
  full CC billing history: one join and one shuffle of the largest A4 input gone, -3 lines.
  Wrap the comment to under 88, for example `# Worst bucket on the earliest dated row: the
  smallest (date, -bucket).` (76 characters). Score 4.3. This is the best of the three.
S4-03 (split `build_dpd_sequences` / `build_deterioration`, type hints): **do not bring back as written**
  (blocking: yes, #3, #4)  criteria: E1, E3
  Four new single-caller helpers (`_monthly_rows_per_account`, `_history_udf`,
  `_spine_rows_with_history`, `_classify_udf`) and type hints on six small helpers; net lines
  up, no pass changes, no helper has a second caller. The only part worth taking is already in:
  `string_key` and `state_label` came from S1. If R-O wants the long functions shortened, take
  the two data helpers (`_monthly_rows_per_account`, `_spine_rows_with_history`) and leave the UDF
  closures and the hints out. The E501 was in a docstring that S5 has since replaced, so the wrap
  is no longer the question.
S4-09 (A4 wrapper steps): **do not bring back**  (blocking: yes, #3)  criteria: E1, E3
  `_original_loan_months` and `_restructure_blind_spot` have one caller each and add their own
  docstrings. The CC half is superseded by S2-06 (which deletes the code the helper would wrap).
  The RL half moves a 14-line query to a named function with no shorter result (69 -> 57 lines
  in the caller, +21 in the file). Skip.

## A3 handoff verdicts (recorded for the A3 session)

| Item | Verdict | Reason (efficiency lens) |
|---|---|---|
| S1-H1 RL A3 `string_key` | accept | -13 lines, third copy of the function gone. S4-H1 is the same change: merge them. |
| S1-H2 CC A3 ladder on `StateLadder` | accept | One definition for A1 and A3; the 12-line `when` chain becomes `_LADDER.state(...)`. A3 ends with fewer concepts. |
| S1-H3 drop `_log_a3_stats` | accept | -24 lines and three full-lineage actions. The `a3_path` breakdown is lost from the log; list it in the bundle notes. Do the same with `.count()` guards at `nodes.py:176-193,440` (my rubric example 4). |
| S2-H-01 latest right-party contact as `max(struct)` | accept | A window exchange and sort removed, `Window` import gone. Ordering checked: flag ascending with `_disp == RTP` as 1 means non-RTP wins, and `(_disp != RTP)` as a max matches. Apply the same at `_signals_common.py:752` where it fits. |
| S3-A3-H1 dict inputs + one tag set (18 nodes) | revise | A3 is to be rewritten as `a3_credibility/` plus thin wrappers; reformatting 18 nodes (about +60 lines of long dict keys) that the rewrite will replace is churn. Take the `_TAGS` change (one line per pipeline), and write dict inputs once in the new wrappers. |
| S3-A3-H2 guards that null a source | accept | Needs the user's answer (Q-S3-7). Fail-loud via `require_columns` deletes the quiet-null branches, so it is a net cut. |
| S4-H1 `_string_key` third copy | accept (duplicate of S1-H1) | Merge into S1-H1. |
| S6-H01 window start by `add_months` | accept | Use `_common.window_start(months, anchor)` and `greatest` with the anchor; the `_signals_common` copy and the RL twin go. This is exactly what `window_agg(start=)` does, so A3 deletes both. Calendar-month windows also remove the Feb/30-day drift. |
| S6-H02 DCORE window bound | accept inclusive | `window_agg` and `dcore_account_events` consumers use `<= observation_date`. An exclusive bound would need a mode in the shared helper (E7 1) or a private filter in A3. User decides; I vote inclusive. |
| S6-H03 anchor on cropped / blind histories | accept | `episode_start` already returns `episode_left_censored`; A3 treats a censored anchor as "window from the lookback only" with one `when`, and no extra A4 pass. State the rule in D-A3-2. |
| S6-H04 shared "oldest open bucket" | defer | A1's anchor is a four-line coalesce; a shared helper with a range parameter only pays if A3's `resolve_due_amount_m` (about 60 lines) shrinks by more than the helper adds. Decide when the A3 engine is written; do not extract speculatively. |

## Files (merged tree)

Criteria: E1 net lines · E2 passes · E3 indirection · E4 PySpark idiom · E5 duplication · E6 docs · E7 fits A3.

- `_common.py`  E1 2 · E2 4 · E3 4 · E4 5 · E5 5 · E6 4 · E7 4  weighted 3.75  — six new shared concepts, but 3 string-key copies and 2 window-start copies gone; `pit_latest` is a single aggregate (`_common.py:107-133`). Under the 4.0 shared-layer target by the unused `start=` and the redundant `scoped` in `pit_latest`.
- `_dpd_journey/__init__.py`  E1 1 · E2 3 · E3 2 · E4 3 · E5 3 · E6 2 · E7 3  weighted 2.3  — 128 lines for re-exports; `__all__` of private names (`:92-135`); 60-line docstring duplicates METHODOLOGY.
- `_dpd_journey/anchor.py`  E1 1 · E2 4 · E3 2 · E4 4 · E5 5 · E6 3 · E7 5  weighted 3.1  — right shape for A3 (one `pit_latest`, no spell join); no caller yet.
- `_dpd_journey/_dates.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.1  — `_month_label` (`:20`) has no caller left.
- `_dpd_journey/constants.py`  E1 4 · E2 3 · E3 3 · E4 3 · E5 5 · E6 3 · E7 3  weighted 3.4  — segment maps moved out, `SEGMENTS` deleted.
- `_dpd_journey/history.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.1  — `_shift_cycle_bills` is a single-caller split for lint.
- `_dpd_journey/logging.py`  E1 5 · E2 4 · E3 3 · E4 4 · E5 5 · E6 4 · E7 4  weighted 4.2  — 100 -> 71 lines, one logger (`:61-71`).
- `_dpd_journey/params.py`  E1 4 · E2 3 · E3 3 · E4 3 · E5 5 · E6 4 · E7 3  weighted 3.5  — validation moved to `segment`; the `segment as model_segment` alias (`:8`) exists only to dodge a local name.
- `_dpd_journey/spark.py`  E1 4 · E2 3 · E3 3 · E4 3 · E5 5 · E6 3 · E7 3  weighted 3.5  — -15 lines from shared `string_key` / `state_label`; per-account Python UDFs are the baseline design and not in scope.
- `_dpd_journey/states.py`  E1 2 · E2 3 · E3 2 · E4 3 · E5 3 · E6 4 · E7 3  weighted 2.7  — +16 lines for two single-caller predicates that name Q1 and Q2 (kept for R-I).
- `a1_ability/signals.py`  E1 2 · E2 5 · E3 3 · E4 4 · E5 3 · E6 3 · E7 4  weighted 3.4  — joins per source cut (`:234-285`), carry via union (`:112-133`); +38 lines from splits and the order-preserving select. `INTERNAL = "int"` and `BUREAU = "bur"` (`:54`) sit next to `BUREAU_BOUNCE = "BUREAU"` (`:41`) and confuse (N-6).
- `a1_ability/classify.py`  E1 2 · E2 3 · E3 3 · E4 4 · E5 4 · E6 4 · E7 3  weighted 3.1  — named constants and `_shows_evidence` replace three repeated expressions; +12 lines.
- `a1_ability/pipeline.py`, `cc_a1_ability/*`, `rl_a1_ability/*`  E1 3 · E2 3 · E3 3 · E4 3 · E5 4 · E6 4 · E7 3  weighted 3.2  — docs and dict inputs only.
- `a2_locatability/signals.py`  E1 3 · E2 5 · E3 3 · E4 4 · E5 5 · E6 3 · E7 4  weighted 3.85  — account-day reduction, struct-max, shared window start; net +2 lines with five fewer aggregates over big tables.
- `a2_locatability/classify.py`  E1 4 · E2 3 · E3 3 · E4 4 · E5 5 · E6 4 · E7 3  weighted 3.65  — `_label` removed.
- `a2_locatability/pipeline.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 3 · E7 3  weighted 3.0  — `TAGS` constant; four axes still each carry their own copy.
- `cc_a4_deterioration/nodes.py` and `pipeline.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 3.1  — `require_columns` and dict inputs; S2-06 still missing (the join over full history remains at `:47-62`).
- `rl_a4_deterioration/nodes.py`  E1 2 · E2 4 · E3 3 · E4 4 · E5 3 · E6 4 · E7 3  weighted 3.15  — `collect` removed, chain frames semi-joined (`:126-137`); +18 lines mostly `require_columns`.
- `rl_a4_deterioration/pipeline.py`, `__init__.py`  E1 2 · E2 3 · E3 3 · E4 3 · E5 3 · E6 4 · E7 3  weighted 2.95  — dict inputs repeat each name twice.
- `cc_full_history/*`, `rl_full_history/*`  E1 3 · E2 3 · E3 3 · E4 3 · E5 5 · E6 4 · E7 3  weighted 3.4  — third `_string_key` gone; `require_columns` blocks make `build_rl_full_history` 54 lines.
- `obs_base/pipeline.py`  E1 3 · E2 3 · E3 3 · E4 3 · E5 3 · E6 3 · E7 3  weighted 3.0  — dict inputs only.
- `scoring_engine.py`  E1 5 · E2 3 · E3 3 · E4 4 · E5 5 · E6 5 · E7 4  weighted 4.1  — `priority_reason` deleted, `state_label` added, module docstring shortened.

Tier L total 3,893 -> 4,130 lines, Spark actions 11 -> 9, ruff 178 -> 80, pylint unchanged.

## New issues

N-1 [`_dpd_journey/_dates.py:20`, `__init__.py:63,121`] `_month_label` has no caller since S1-06 (S5 also notes it). Delete it and its two export lines. → S7
N-2 [`_dpd_journey/__init__.py:1-135`] 128 lines; `__all__` lists private names for tests; the module docstring (60 lines) repeats METHODOLOGY.md and `states.py`. Drop `__all__`, add one F401 ignore, cut the docstring to the contract, run command and module list. About -75 lines. → S4 (with S5 on the docstring)
N-3 [`a2_locatability/signals.py:236-247`] The `rank` window sorts every DCORE account-day per observation row; before, only call days were sorted (`calls` filter ran ahead of the window). If most DCORE days are notes without a call, the window input grows. Check row counts into the window on the PROD sample, and if material, keep only days with any flag set (`_attempt`/`_contact`/`_deceased`/`_skip_trace`) and derive `_dcore_record` from the unreduced events with a small separate count. The golden harness cannot show this. → S2
N-4 [`_common.py:107-133`, `scoped`] In `pit_latest` the inner join against `base.select(...)` already keeps only base keys, so `scoped` adds a distinct-and-broadcast stage with no new pruning. Keep `scoped` in `window_agg` and the A2 reads, drop it from `pit_latest`, or show a plan where it helps. Also confirm the broadcast hint holds for a CIF-level base of about a million keys on the PROD driver. → S2
N-5 [`_common.py:176-206`, `window_agg(start=)`] and [`_dpd_journey/anchor.py`] no caller. See S1-07, S1-08. → S1 (move to the A3 bundle, or add the caller)
N-6 [`a1_ability/signals.py:41,54`] `BUREAU_BOUNCE = "BUREAU"` and `BUREAU = "bur"` one screen apart; `INTERNAL`, `BUREAU` are labels used in a single function. Inline `"int"` / `"bur"` as before, or fold them into one `Source` constant set. → S4
N-7 [`a1_ability/classify.py` `INCOME_POINTS`, `LIQUIDITY_POINTS`] two dicts, one use each, tied to the spec cells. Fine for R-I; if R-O wants fewer concepts, inline back. Low. → S4
N-8 [`a1/a2/a4/a3 pipeline.py`] The five-item tag list is written per axis. After S3-04, `persona_tags(axis, name)` in `_common` leaves one definition. Low; only with S3-04. → S3
N-9 [`cc_a4_deterioration/nodes.py:47-62`] S2-06 revert leaves the self-join in place; re-submit wrapped (see above). → S2
N-10 [`rl_a4_deterioration/pipeline.py`, `cc_a4_deterioration/pipeline.py`, `obs_base/pipeline.py`] If R-O does not waive S3-01/02 blocking, the dict form can drop to `inputs={"x": "x"}` only where key and dataset differ and keep the list elsewhere; Kedro accepts a list when names equal the parameters. → S3
N-11 [`_common.py` `WINDOW_MONTHS`, `a2_locatability/signals.py` `GONE_DARK_DAYS`] Two per-segment dicts with the same keys and the same lookup (`dict[segment(model_id)]`). A `for_model(table, model_id)` helper is not worth it today; at the third table (A3) it is. Note for the A3 session. → S1
N-12 [tier L, metrics] Functions over 40 lines: 18 -> 22. The new ones are `pit_latest` (41, one line over), `build_cc_full_history` (43), `build_rl_full_history` (54), `build_cc_dpd_sequences` (42), all `require_columns` blocks. Not a defect under the rules; no action unless R-I raises it.

## Round 2 removals, in order of size (for the Master)

1. `_dpd_journey/__init__.py` `__all__` and docstring (N-2): about -75 lines.
2. Move `anchor.py` and `window_agg(start=)` to the A3 bundle (S1-07/08): -58 lines in tier L.
3. Re-submit S2-06 wrapped: -3 lines and a join.
4. Drop `scoped` from `pit_latest` (N-4): -3 lines and a stage.
5. Inline `_latest_evidence`, `_shift_cycle_bills` if R-O sides with efficiency: -15 lines.
6. Delete `_month_label` (N-1): -8 lines.

Together about -160 to -200 lines, which takes tier L to about baseline.
