# R-O review, round 1 (Owner)

Frozen rubric `rubrics/owner.md`. Input `d1ad38a`, merged tree HEAD `5c24553` (S7 → S1 → S3 → S2 →
S4, S5 docstrings). Read: PLAN §2/§3/§8, scorecard, merge_log, gates, decisions, all proposals,
`a3_handoff.md`, `questions.md`, R-E and R-I (after scoring the files blind).

Criteria: O1 PROD operability 18 · O2 change risk / bundle-ability 18 · O3 auditability 16 · O4 one
engine, thin wrappers 14 · O5 fits A3 14 · O6 contracts / Kedro 10 · O7 clarity per line 10.

## Summary

- Gates green (gates.md), golden identical on 14 runs / 79 datasets. Nothing in the tree is a
  behaviour change; no gate is in dispute.
- The round pays where I score highest: one segment map, one string key, one window start, one
  state logger, one DCORE reader, `pit_latest` without a window, RL A4 without `collect`, tier D gone.
  Actions in tier L 11 → 9; no new one.
- What holds my scores below 4: two unmeasured PROD plan changes (N-3, N-4), a 38-line `__all__` of
  private names, the two 100+-line A4 engine functions, the A4 wrappers (S2-06 / S4-09 reverted), and
  shared A3 helpers (S1-07, S1-08) with no checked caller.
- **Change risk to note for the bundles:** `a1_ability/signals.py` (223 changed lines) and
  `a2_locatability/signals.py` (279) are the two files the workplace edits most; bundle 14 (A1) is
  still waiting UAT apply. PLAN §8 holds: rebase on bundle 14's workplace head before building, A1 and
  A2 refactor bundles after the shared one, each with a 0-diff crosstab.

## Proposals

Verdict, my weighted score, criteria that decided it. "Blocking" is my own objection only.

### S7
S7 patch + delete list: **accept** (blocking: no) 4.6  O2, O4
  Tier D gone, `build_rl_depart_spine` moved byte-identical into tier K before the CC delete (PLAN
  §2 order kept). The logger-name change of the moved function is listed. Ships in bundle 1.

### S1
S1-01 `segment()` / `MODEL_ID_SEGMENT` / `SEG_*` in `_common`: **accept** (no) 4.6  O4, O5, O3
  Dependency direction fixed (engines → shared layer); `ValueError` names the model_id. The A3 band
  lookup has one home.
S1-02 `string_key`: **accept** (no) 4.7  O4, O6
S1-03 `window_start(months, anchor=None)`: **accept** (no) 4.5  O5, O3
  Argument order changed on a renamed function: listed for the tests. Good.
S1-04 `state_label`: **accept** (no) 4.3  O4
  Rename `kv` → `pair` (R-I) in round 2, zero lines.
S1-05 `dcore_account_events`: **accept** (no) 4.3  O5, O4
  A3's D-A3-7 read is now A2's read. Kept in `_common` on the strength of the A3 caller (R-E's
  condition noted: if the A3 session does not use it, it moves back to A2).
S1-06 one state logger: **accept** (no) 4.4  O1, O4, O3
  My rubric example 1 met. The A4 log header and ordering change is a PROD log change; the A4 check
  pipelines do not parse it, and it is listed in merge_log for the A4 bundle notes (blocking 7
  satisfied). Add the exit note to `latest_per_account` ("remove when cc_spine is month-end"), S5.
S1-07 `episode_start` (`_dpd_journey/anchor.py`): **accept, keep in tree; revise (non-blocking) for
  a checked caller** 4.1  O5 5, O2 3
  PLAN §2 puts A3's shared helpers in this refactor, and the user asked for "fits A3 easily"; moving
  the file into the A3 bundle would make the A3 session re-derive the anchor in the bundle it is
  already busiest with (my blocking 4). R-E's real point stands: shared code with no test is a ship
  risk. Round 2: S1 turns its sanity run (S1.md "What I checked") into a checked spec case, and adds
  the one-line comment on `history_months - 1 - months_before_spell` and the censored-row sentence
  (R-I N-12, N-13).
S1-08 `window_agg(start=)`: **accept, keep; revise (non-blocking) for a checked caller** 4.0  O5
  Same ruling. The case must cover a row whose `start` is later than `window_start(months)` and one
  where it is earlier. The bound convention (inclusive at both ends) stays one convention; A3
  follows it unless the user answers Q-22 otherwise, and then A3 filters privately (no mode switch in
  the shared helper).

### S3
S3-01, S3-02 dict inputs (obs base, full histories, A4): **accept** (no) 4.2  O6, O4
  My tie-break says dict, rename-safe; it is already the A1/A2 form and it is what A3 will copy.
  R-E's blocking 4 is waived for these (ruling R-3 below).
S3-03 `require_columns` on spines / sources: **accept** (no) 4.5  O6, O1
  Line growth allowed by the scorecard; D2.
S3-04 tag normalisation: **held** for Q-15. Verdict when answered "yes": accept (4.0). Module
  constant `TAGS` per pipeline as A1/A2; no `persona_tags()` helper (R-E N-8 rejected: a function for
  a five-item list adds a concept and still needs an axis argument).
S3-05 `crx_persona` required: **accept** (no) 4.4  O6
S3-06 registry wrap, S3-07 catalog comments: **accept** (no) 4.0  O2, O3

### S2
S2-01 `scoped` + `pit_latest` as one aggregate: **accept** (no) 4.2  O1, O5
  Equivalence on ties and NULLs shown; golden agrees. N-4 below: keep `scoped` in `pit_latest`,
  measure the broadcast.
S2-02 A1 one join per source: **accept; R-I's naming as a round-2 follow-up** (no) 3.9  O1 5, O7 3
  Five reads to two is a real PROD gain. The S11 rules (`casa_active`, `casa_held`) sit in sentinel
  columns of a union: on rule lines R-I wins (ruling R-6). Round 2 names them, the plan stays.
S2-03 A2 DCORE account-days: **accept; follow-up on plan and naming** (no) 3.9  O1 4, O3 3
  Event rows no longer multiply by observation rows: the biggest plan win in A2. N-3 (sort of all
  account-days) and R-I's D-A2-7 / D-A2-20 naming go to S2 as one item (ruling R-6, R-9).
S2-04 A2 scoped sources, Way4 struct-max: **accept** (no) 4.2  O1
S2-05 distress floor pruning: **accept** (no) 4.3  O1
S2-07 RL A4 without `collect`: **accept** (no) 4.6  O1
  One action and a driver loop over all spine accounts gone.
S2-06 CC A4 restructure flag as one aggregate (reverted, E501): **bring back, revised** 4.2  O1, O3
  Ruling R-5 below.

### S4
S4-01 A1 threshold names, `INCOME_POINTS`, `_shows_evidence`: **accept** (no) 4.3  O3, O7
  Business numbers get a name and a spec cell; spec text updated in the same commit (good for audit).
S4-02 `__all__`, public `log_state_stats`: **revise** (blocking: no, but R-E blocks) 3.0  O7, O2
  Ruling R-2 below. Keep the rename.
S4-04 (part) A2 split: **accept** (no) 4.0  O3
  `_latest_evidence` stays: "latest evidence wins" is the A2 rule's own phrase, so the name is a spec
  concept (tie-break: keep when the name is a spec term). R-E's inline request declined.
S4-05 A1 distress split: **accept** (no) 4.0  O6, O3
  The fail-loud check (`_require_returns_from`) has a name and keeps S2-05's floor.
S4-06 `assign_state` predicates: **accept** (no) 4.0  O3
  Finish Q3 / Q4 in round 2 (R-I N-7) so the four rules read the same way.
S4-07 `_shift_cycle_bills`: **accept** (no) 3.6  O7
  Below my bar for a single-caller helper, but it is applied, local, removes two pylint disables and
  names a step the docstring numbers; re-inlining is churn. Keep.
S4-08: skipped (duplicate of S1-04). Agree.
S4-10 `SEG_60_180` / `SEG_180_PLUS` in `_common`: **accept** (no) 4.3  O4
S4-11 A2 `TAGS`: **accept** (no) 4.0  O4
S4-03 split `spark.py` (reverted, E501): **bring back in part** 3.6  O7, O2. Ruling R-4.
S4-09 A4 wrapper steps (reverted, E501): **bring back in part** 3.5  O3, O2. Ruling R-4, R-5.

### S5
S5 docstrings (28 files): **accept** (no) 4.2  O3
  History out, spec IDs and run commands in, net +11. Remaining: `_dpd_journey/__init__.py` module
  docstring (60 lines, repeats METHODOLOGY), `_log_sequence_stats`, `INCOME_POINTS` spec ref.

### S6
Findings only, all in `questions.md` (Q-01 … Q-25). None in the code. Correct handling.

## Rulings on R-E / R-I disagreements

Order applied: gates and behaviour → bundle risk → spec traceability (R-I) → brevity (R-E).

R-1 **S1-07 `episode_start`, S1-08 `window_agg(start=)`: keep both in the shared layer now.** R-E's
  "no caller, land with A3" is overruled by PLAN §2 (S1 "puts them in the shared layer in this
  refactor") and my blocking 4 (A3 would re-derive the anchor). R-E's test demand is upheld: a checked
  spec case for each in round 2. One line: scope is the plan's, and a tested helper is not dead code.
R-2 **S4-02 `__all__` vs F401 ignore: R-E wins.** Replace the 38-line `__all__` with a file-level
  `# ruff: noqa: F401` and two commented import groups ("public" / "re-exported for the parity
  tests", with one line saying `H, N, P, R` are the reference's names). An `__all__` that lists
  `_glitches` and `_mean` is not a public surface, and a re-export list is not a business rule; the
  grouping gives R-I's N-6 what it asked for at ~35 fewer lines.
R-3 **S3-01/02 dict inputs: R-E's blocking 4 waived.** My tie-break names dict inputs explicitly
  (rename-safe, the A1/A2 form A3 will copy). R-E N-10 (lists where names match) rejected: two styles
  is what O4 scores down.
R-4 **S4-03 and S4-09: neither R-I's "all back" nor R-E's "none back".**
  - S4-03: bring back only the two data stages, `_monthly_rows_per_account` and
    `_spine_rows_with_history` (R-E's own offer). No UDF-closure helpers, no type hints. The 122- and
    104-line engine functions are O7 = 1 for me; the two data helpers carry the joins an auditor has
    to follow, the closures are mechanism. One line: shorten the engine where the data flows, not
    where the plumbing is.
  - S4-09: bring back the RL half only, as one helper `_original_loan_months` that also absorbs the
    nested `frame()` closure (R-I N-8), net ≤ +8 lines. It names the user's restructure-chain rule
    (2026-11-02); R-I wins on rule lines. The CC half is replaced by R-5. One line: the RL step is a
    business rule with a name; the CC step is superseded.
R-5 **S2-06: comes back as the CC `_restructure_blind_spot(history)` helper, with the tie rule
  written down.** The helper's name is the conformance D2 rule (R-I wins on the rule's home); the
  body is S2-06's one aggregate (R-E wins on the plan). The comment states the rule in two lines ≤ 88
  characters: "earliest dated row; on a same-date tie the worst bucket wins" and "bucket negated so
  the smallest struct is that row". Name the struct field `neg_bucket` as proposed. One line: one
  place for the rule, one pass for the data.
R-6 **S2-02, S2-03: keep the code; R-I's naming is round-2 work, not a revert.** The plan gains are
  mine (O1); the rule lines are R-I's. A1: `casa_active` (S11) and `casa_held` become named column
  expressions beside the legs union (`_casa_legs` with a one-line contract). A2: `gone_dark` becomes a
  named expression or private function citing D-A2-7 / D-A2-20, and the rank line says it is the
  D-A2-20 streak. No new pass, no output change. One line: keep the passes, name the rules.
R-7 **R-E's tier-L line target (+237 against "no higher than baseline"): not adopted as a gate or
  convergence condition.** About 110 lines are A3 helpers the plan asked for and about 90 are
  `require_columns` and spec-named constants the scorecard allows; R-E's target is its own file-score
  input, not mine. Round 2 must still be **net negative in tier L (≤ −25 lines)**, with a line budget
  per item (triage). One line: growth that the plan and the scorecard allow is not debt; growth beyond
  it is.
R-8 **S4-04 `_latest_evidence`, S4-07 `_shift_cycle_bills`: keep** (R-E asked R-O). Spec term /
  applied and local. See above.
R-9 **N-3 vs R-I N-3 (`build_dcore_signals`): one owner, S2**, so the plan fix and the naming land in
  one edit of one function; S4 does not touch it in round 2.
R-10 **`INTERNAL` / `BUREAU` labels (R-E N-6 inline vs R-I N-5 rename): R-I wins.** They are source
  and reason labels; my tie-break gives labels a name. Rename to `SOURCE_INTERNAL`, `SOURCE_BUREAU`,
  `REASON_BUREAU_BOUNCE` (values unchanged, zero net lines).
R-11 **`INCOME_POINTS` / `LIQUIDITY_POINTS` (R-E N-7): keep**, add the GRR points-table reference
  (R-I N-17). Business numbers.
R-12 **`_RESTRUCTURE_DLQ_THRESHOLD` (R-I N-9): leave in `cc_a4_deterioration/nodes.py`.** Moving it to
  `_dpd_journey/constants.py` does not remove the copy: `cc_spell` is tier K and cannot import it.
  Revisit when `cc_spell` is deleted after A3. The comment cites conformance D2 (already does).
R-13 **R-I N-15 (`build_history` split), N-2's four-way split of `build_a1_ability`: not in round 2.**
  Take from N-2 only the ladder thresholds as named constants and the S11 Unknown gate as a named
  predicate (rule lines); the `_levels/_state/_diagnostics/_output` split is mechanism and A1 is a
  closed axis with a bundle in flight (bundle risk). `build_history` waits for round 3 if S4-03 lands
  cleanly.
R-14 **N-11 (`for_model` helper / key every table by segment): round 3 consistency pass**, and only
  the A3 design text (S1.md target shape: `SEG_*` keys, `_in_episode` bound) is fixed in round 2.
  A1's window-length keys stay until round 3; A1 has a bundle in flight.

## PROD cost items (R-E N-3, N-4): what must be measured or changed

**N-3, A2 DCORE `rank` sorts every account-day.** Before, only attempt days entered the window; now
all DCORE days dated on or before each observation do. Against that, the old plan ran three
aggregates over event × observation rows, which is larger than day × observation, so the round is
very likely still a net gain; but "likely" is not a PROD answer and the golden harness cannot show it.
- **Change (S2, round 2):** remove the window. The last `streak` attempt days can be read in the same
  aggregate: `slice(sort_array(collect_list(when(attempt, struct(day, failed))), asc=False), 1,
  streak)`, then `_n_last`, `_failed_last`, `_oldest_last` from that array (days are unique per
  `(GRAIN, day)`, so no tie question). That is one shuffle, no sort of non-attempt days, and gives
  R-I's `_last_call_days` a natural home. Accept only if golden and the A2 spec pass, the local
  `explain()` shows no more Exchange nodes than HEAD, and the function does not grow by more than 6
  lines. If S2 finds it less clear or longer, keep the window and do the measurement below instead.
- **Measure (A2 refactor bundle PROD check, aggregates only, per model_id):** rows entering the
  DCORE summary (day × observation, after the date filter) and the share with `_attempt = 1`; plus the
  stage's shuffle-read and spill from the Spark UI for old vs new. Rule: if non-attempt days are over
  half the rows or the stage spills, the window-free form is required before the A2 bundle ships.

**N-4, `scoped` broadcast in `pit_latest`.** R-E is wrong that it prunes nothing: the inner join is a
sort-merge join that shuffles the whole bank-wide source; `scoped` drops non-base keys map-side before
that shuffle. Keep it. R-E is right that the hint is forced: `F.broadcast` ignores
`autoBroadcastJoinThreshold`, so a large key set goes to the driver regardless.
- **Measure (A1 and A2 bundle PROD checks, per model_id):** distinct `cif_id` and `account_id` of the
  obs base over the persona months (two numbers in the check output), and in the Spark UI the size of
  the `BroadcastExchange` for one A1 node. Expected: hundreds of thousands of keys at 180+, tens of
  MB.
- **Rule:** if any model_id exceeds 2M keys, or a broadcast exceeds 256 MB, or a broadcast timeout
  appears, drop the hint inside `scoped` (plain `left_semi`, Spark decides). One-line, plan-only
  change in `_common`; no output change. No code change in round 2.

## A3 handoff verdicts

| Item | R-E | R-I | R-O | Reason |
|---|---|---|---|---|
| S1-H1 RL A3 `string_key` | accept | accept | **accept**, merge S4-H1 into it | one key rule |
| S1-H2 CC A3 ladder on `StateLadder` | accept | accept (Unknown gate named) | **accept with R-I's condition** | the gate is a rule (S11-style) and gets one named place, as in A1 |
| S1-H3 drop `_log_a3_stats` | accept | accept | **accept** | three full-lineage actions gone; list the removed `a3_path` log breakdown in the A3 bundle notes; also remove the `.count()` guards (`nodes.py:176-193,440`) when A3 moves to the obs base |
| S2-H-01 latest RPC as `max(struct)` | accept | accept with rename | **accept with rename** (`_not_refusal`, comment "same day: a refusal sorts first (D-A3-19)") | the tie on date and flag becomes deterministic (largest disposition): a behaviour choice, asked as Q-28 |
| S3-A3-H1 dict inputs + tags (18 nodes) | revise | accept | **revise: R-E's way** | reformatting 18 nodes of code the A3 rebuild replaces is churn (bundle risk); write dict inputs once in the new `a3_credibility` wrappers; tags follow Q-15 |
| S3-A3-H2 quiet-null guards | accept | accept (b) | **accept (b), after Q-20** | blocking 3 in my rubric: a guard that turns a source off quietly |
| S4-H1 | dup | dup | **merged into S1-H1** | |
| S6-H01 window start by `add_months` | accept | accept | **accept** | A3 uses `_common.window_start` / `window_agg(start=)`; calendar months, one definition |
| S6-H02 DCORE bound | inclusive | one named bound | **inclusive, pending Q-22** | `window_agg` and A2 are inclusive; if the user picks exclusive, A3 filters privately, no switch in the shared helper |
| S6-H03 anchor on cropped histories | accept | accept, carry censored reason | **accept** | `episode_left_censored` reaches the A3 output as a reason (Q-25) |
| S6-H04 "oldest open bucket" helper | defer | accept | **defer to the A3 build** | extract only if A3's `resolve_due_amount_m` shrinks by more than the helper adds; ranges as spec-named constants then. A1's anchor is not re-touched (bundle in flight) |

S1's target A3 shape: O5 **4** today (engine + thin wrappers, decision → helper map, one anchor, one
DCORE reader). It reaches 5 with the N-11 text fixes (segment constants, the `_in_episode` bound
matching `window_agg`) and the checked cases for `episode_start` / `start=`. `a3_handoff.md` is
diff-level for H1, H2, H3, S2-H-01, S3-A3-H1; the S6 items are text by nature.

## Files (merged tree)

Weighted = (18·O1 + 18·O2 + 16·O3 + 14·O4 + 14·O5 + 10·O6 + 10·O7) / 100.

| File | O1 | O2 | O3 | O4 | O5 | O6 | O7 | Wtd | Lowest and fix |
|---|---|---|---|---|---|---|---|---|---|
| `_common.py` | 4 | 4 | 4 | 5 | 5 | 5 | 4 | **4.38** | `scoped` broadcast unmeasured (N-4) |
| `scoring_engine.py` | 4 | 4 | 4 | 5 | 4 | 5 | 4 | **4.24** | `kv` |
| `obs_base/pipeline.py` | 4 | 5 | 4 | 4 | 4 | 5 | 4 | **4.28** | — |
| `_dpd_journey/__init__.py` | 4 | 3 | 3 | 3 | 4 | 4 | 2 | **3.32** | `__all__` of private names, 60-line docstring (R-2) |
| `_dpd_journey/anchor.py` | 4 | 3 | 4 | 4 | 5 | 5 | 4 | **4.06** | no checked case (R-1) |
| `_dpd_journey/_dates.py` | 4 | 4 | 4 | 4 | 3 | 4 | 3 | **3.76** | dead `_month_label` |
| `_dpd_journey/constants.py` | 4 | 5 | 4 | 4 | 4 | 4 | 4 | **4.18** | — |
| `_dpd_journey/history.py` | 4 | 4 | 3 | 4 | 3 | 4 | 3 | **3.60** | 84-line `build_history` (round 3) |
| `_dpd_journey/logging.py` | 4 | 4 | 3 | 5 | 4 | 4 | 4 | **3.98** | `_log_sequence_stats` contract |
| `_dpd_journey/params.py` | 4 | 4 | 4 | 5 | 4 | 4 | 4 | **4.14** | — |
| `_dpd_journey/spark.py` | 3 | 4 | 3 | 4 | 3 | 4 | 2 | **3.32** | 122 / 104-line functions (R-4) |
| `_dpd_journey/states.py` | 4 | 4 | 4 | 4 | 3 | 4 | 3 | **3.76** | Q3 / Q4 inline |
| `a1_ability/classify.py` | 4 | 4 | 4 | 4 | 4 | 4 | 3 | **3.90** | ladder `4` / `2`, S11 gate inline |
| `a1_ability/signals.py` | 4 | 3 | 4 | 4 | 4 | 5 | 3 | **3.82** | 223 changed lines in a file with a bundle in flight; S11 in sentinel columns |
| A1 `pipeline.py` + CC/RL A1 wrappers | 4 | 4 | 4 | 5 | 4 | 5 | 4 | **4.24** | model wrapper shape |
| `a2_locatability/signals.py` | 3 | 3 | 4 | 4 | 5 | 5 | 3 | **3.78** | N-3 unmeasured; `gone_dark` unnamed |
| `a2_locatability/classify.py` | 4 | 4 | 4 | 5 | 4 | 5 | 4 | **4.24** | no reachability rule column (Q-26 scope) |
| `a2_locatability/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | — |
| `cc_a4_deterioration/nodes.py` | 3 | 4 | 3 | 3 | 4 | 5 | 3 | **3.52** | self-join over full billing history (R-5) |
| `rl_a4_deterioration/nodes.py` | 4 | 4 | 3 | 3 | 4 | 5 | 3 | **3.70** | 76-line linked history with nested `frame()` (R-4) |
| A4 `pipeline.py` (CC, RL) | 4 | 4 | 4 | 3 | 4 | 5 | 4 | **3.96** | tag set differs (Q-15) |
| `cc_full_history/nodes.py`, `rl_full_history/nodes.py` | 4 | 4 | 4 | 4 | 4 | 5 | 3 | **4.00** | 43 / 54 lines from contracts (allowed) |
| `catalog_crx.yml`, `pipeline_registry.py` (crx part) | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | — |

Per criterion (line-weighted over tier L, approximate): O1 3.8 · O2 3.8 · O3 3.7 · O4 4.1 · O5 4.1 ·
O6 4.9 · O7 3.2. Average of files 3.94. No file below 3 on O1, O2 or O3. **Not yet sign-off grade:**
O1, O2, O3 and O7 are under 4; round 2 targets them (R-2, R-4, R-5, N-3, N-4, R-6).

## New issues (R-O)

N-O1 [`a1_ability/signals.py`, `a2_locatability/signals.py`] Bundle 14 (A1) is not yet applied in the
  workplace and touches `a1_ability/signals.py`. Before the A1 refactor bundle is built, rebase on the
  workplace head after bundle 14 and re-run all gates (PLAN §8); the three-way merge of 223 changed
  lines must be checked by hand, not trusted. → Master (bundle build)
N-O2 [bundle notes] The A1 and A2 refactor bundles' PROD checks carry the N-3 / N-4 aggregates in
  addition to the 0-diff crosstab (aggregates only, temporary node, catalog entry removed by the
  cleanup). → Master (bundle plan)
N-O3 [`round_1/proposals/S1.md` target A3 shape] `_in_episode` writes `< observation_date`; the shared
  helper is inclusive. Align the design text with `window_agg(start=)` pending Q-22. → S1
