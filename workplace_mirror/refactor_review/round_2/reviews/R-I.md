# R-I review, round 2 (Interpretability advocate)

Rubric: `rubrics/interpretability.md` (frozen). Tree: HEAD (`7ae2a08`), diff `2942237..HEAD` over
`src`, `conf`, `checks`, `specs`. Read: PLAN (incl. "Axis stability"), decisions (D-2-1, D-2-2), round 1
triage and my round 1 review, S1-S5 logs, gates, `a3_target_shape.md`, `a1_design_in.md`, and every
changed tier-L file. Not read: the other round 2 reviews. Behaviour is the gates' (and S6's), not mine.

**Result.** No blocking objection open on any round 2 item. Tier-L average of the 18 changed files
**3.95** (round 1: 3.86 over 25 files; target 3.5 met). Round 2 closed my five conditions; the large
gain is the `Scorecard` (one declaration per axis) and the Q ids on the A4 rules. What is left is
smaller: `Scorecard.score` is itself a 45-line function, A1's ladder thresholds are still bare `4` / `2`,
and A1 / A4 still do not print which rule fired.

## 1. Round 1 conditions: met?

| Round 1 item | Condition | Met? | Evidence |
|---|---|---|---|
| S2-02 (A1 liquidity union) | each rule a named builder | **Met** | `_casa_legs` (`a1_ability/signals.py:209`) with a contract per column (`balance`, `customer` = S11 lane, `held`); `casa_active` (S11) and `casa_held` are two named expressions before the join. Income signals (`SOURCE_INTERNAL` / `SOURCE_BUREAU` rows) keep their old shape; deferred by D-2-2, fine. |
| S2-03 (A2 DCORE) | a named place for D-A2-7 / D-A2-20 | **Mostly met** | `_gone_dark(streak, w_start)` (`a2_locatability/signals.py:198`) is the non-reachable rule, its docstring cites D-A2-7 and D-A2-20, and `_last_calls` removes the `_rank` trick. The reachable rule (`last_contact_date >= w_start`) is still inline in `reachability_state`, the `slice(sort_array(collect_list(...)))` is an unnamed local, and `build_dcore_signals` is 69 lines with a pylint disable. No output says which reachability rule fired. Non-blocking (R3-4). |
| S1-07 (anchor) | comment on the arithmetic; a test that reaches `episode_start` | **Met** | `anchor.py:41` comment; `checks/a4_chain_spec.py::check_anchor` runs it on the RL A4 output, on long-keyed billing-dated CC rows, the cropped / uncropped pair and a last-month row. The comment wording is clumsy ("... minus the episode's first month's"); say "months from the episode's first month to the row's month, counted back from the history end" (R3-6). |
| S4-06 (Q3 / Q4 predicates) | finish the job | **Met** | `_is_repeat_delinquent` (Q3), `_is_straight_roller` (Q4) beside Q1 / Q2; every `STATE_RULES` key and every `if` in `assign_state` carries its Q id. State names are still literals (S4 declined; I accept, `STATES[1]` reads worse). The seasoned / early-life split under Q4 stays inline with its own constant; fine. |
| S2-06 (CC restructure flag) | tie rule stated; fold into one helper | **Met** | `_restructure_blind_spot(history)` (`cc_a4_deterioration/nodes.py:29`): docstring names the rule, a two-line comment states the tie ("earliest dated row; same date: worst bucket, because the bucket is negated"). `-F.col("_first.neg_bucket") >= ...` still reads backwards, but the comment is the explanation I accepted. |
| S4-09 (A4 wrappers) | RL `_original_loan_months`; CC flag as a named function; `frame()` to `_chain_frames` | **Mostly met** | `_original_loan_months` is in (docstring: chain rule, closed months, worst bucket, own row wins); the CC flag is named. The nested `frame()` is gone, but replaced by a generator unpacked into two names (`chain_df, member_df = (... for rows, schema in ...)`), which is cleverer than the closure. `build_rl_a4_deterioration` still has two pylint disables and no `_rows_before_chain` (N-8, second half). Non-blocking (R3-5). |

## 2. Proposals

Round 2 items were applied on the branch (D-2-1), so each verdict is on the code as it now stands.

**S1 A3-1 / A1-1 `Scorecard`, `Dimension`, `Override`**: accept (blocking: no)  I1, I6, I7
  The central item. One engine for A1 and A3; the rule list is a declaration; `<prefix>_override` and
  `<prefix>_reason` give the auditor the reason column that `StateLadder` never had. Reservations in
  section 3. The NULL-override difference (no longer turns into Low) is documented and pinned by a
  spec row; it is a gate question, not mine.
**S1 A1-2 `**signals` + `FAMILIES`**: accept (no)  I6, I7
  A family is one builder, one node input, one row. `FAMILIES` pairs the level function with its
  `Dimension` in reading order. The loop `for level, dimension in FAMILIES` hides nothing: both rules
  keep their names (`income_level`, `liquidity_level`). Not a blocking objection 7 (the rule functions
  stay named).
**S1 A3-4 `GONE_DARK_DAYS` to `_common`**: accept (no)  I2, I6
  One definition per number, comment names both readers (D-A2-20, D-A3-19). Raises I2 on `_common` and
  `a2_locatability/signals`.
**S1 A3-3 `episode_left_censored` + revise S1-07 / S1-08**: accept (no)  I1, I5, I6
  The docstring now says which rows are censored and what the consumer does. Checked cases close N-12 /
  N-13.
**S1 Q-18 `require_columns` in `build_dpd_sequences`**: accept (no)  I1, I5. The error text change is
  listed.
**S1 Q-21 `string_key` in RL A4**: accept (no)  I2, I7. The "flagged, not changed" table of sites is
  exactly what an auditor needs; it should be carried into the shared bundle check (R3-7).
**S1 revise #5 (A3 target text)**: accept (no)  I6. `SEG_*` keys, inclusive `_in_episode`; N-11 closed
  in the text. See the A3 declaration in section 3 for what is still literal.
**S2 S2-06**: accept (no). **S2 N-3 window-free DCORE + `_gone_dark`**: accept (no)  I1, I3. **S2 S2-02**:
  accept (no)  I1, I3. **S2 Q-14 (b) partition floor**: accept (neutral). One comment explains why the
  floor cannot change a value; `first` is a weak name for "the persona start date" (`persona_start`).
  **S2 N-4**: no change, agree.
**S3 tags, Q-16 note**: accept (no)  I7. Every pipeline now writes `TAGS` once with the same five-name
  shape (I7 for the A4 pipelines 3 to 5). `rl_b1` is gone (D3 leak). `full_history` tags differ by
  design (no `persona_axis`); fine.
**S4 S4-02 (`__all__` to commented import groups)**: accept (no)  I4, I5. "Public" vs "Re-exported for
  the parity tests: H, N, P, R are the numpy reference's names" is the explanation I asked for.
**S4 S4-03 part (`_monthly_rows_per_account`, `_spine_rows_with_history`)**: accept (no)  I3, I5.
  Each helper has a column contract. The two `build_*` functions are still about 90 and 85 lines with the
  UDF closures inline, so `spark.py` stays my lowest file (R3-3).
**S4 S4-09 RL**: accept, see section 1. **S4 Q3 / Q4**: accept. **S4 A1 label constants, `pair`**:
  accept (no)  I2, I4. `SOURCE_INTERNAL` / `SOURCE_BUREAU` vs `REASON_BUREAU_BOUNCE` ends the N-5
  confusion; the values stay `"int"` / `"bur"` / `"BUREAU"`, which are still cryptic as data, but they
  are not output columns.
**S4 line target (`black -C`, docstring cuts)**: accept, neutral. The `__init__` docstring cut (-22)
  removes text that repeated `constants.py` / `states.py`; the rules pointer stays. No rule lost.
**S5**: accept (no)  I5. The `_log_sequence_stats` contract is a comment above the `def`, not a
  docstring (to stay under 40 lines). It reads fine; I score it as a boundary documented, not as a
  docstring. `INCOME_POINTS` / `LIQUIDITY_POINTS` now cite the spec table (N-17 closed).

## 3. The new `Scorecard`: is each axis's rule set readable and traceable?

### What works
- **The declaration is the rule list.** Dimensions, points per level, thresholds, overrides and labels
  sit in one expression; the override order is the priority and is stated in the docstring. An analyst
  reads `SCORECARD` and sees the ladder without reading Spark.
- **Reason and override columns exist in the engine** (`a1_override`, `a1_reason`, and `a3_*` the same).
  This is the traceability the rubric calls a 5 (I1) once the columns reach the output.
- **Same names on both axes** (`Dimension`, `Override`, `DEMOTE`, `high_from`, `moderate_from`,
  `unknown_also`), so A3 reads as A1 with more dimensions (I6, I7).
- **Spec cases**: 14 rows pin DEMOTE, CAP, FORCE, first-override-wins, NULL flag, the High gate, Unknown.

### What does not yet read well (none blocking)
1. **`Scorecard.score` is one 45-line method** doing points, High gate, rung, overrides, Unknown, reason
   and select, with a pylint disable (`too-many-locals`). The rubric's I3 = 5 order is "points,
   override, ladder, output" as separate small steps. Split into `_points`, `_rung`, `_unknown`,
   `_reason` (private methods, one-line contract each); the lines move, they do not grow much.
2. **Rung literals.** `F.when(high, 2).when(total >= moderate_from, 1).otherwise(0)` and `for i in
   (2, 1)` are the index of `RUNGS` written as digits. `HIGH, MODERATE, LOW = 2, 1, 0` (or `RUNGS.index`)
   makes the rung table visible.
3. **A mode typo silently becomes FORCE** (`moved.get(o.mode, to)`). Make the three modes explicit and
   reject others in `Override.__post_init__`; the auditor should not have to know the default.
4. **The rule id is only in a comment.** A1's `Override("distress", ...)` carries `# S9` and the points
   dicts carry "spec points table", but the engine emits the override *name* as the reason. Acceptable
   when the name equals the spec's word (distress, refusal); A3's `broken_commitments` / `refusal` also
   do. Do not add a spec-id field (would be a parameter for its own sake); keep names equal to the spec's
   words.
5. **Reason and points are computed and dropped in A1** (`select` omits `a1_override`, `a1_reason`).
   This is N-16 / Q-26: the largest remaining I1 gap for A1 and A4, barred for a refactor by PLAN §3, so
   it is a question for the user, not a refactor item (R3-1).

### A1 declaration (`a1_ability/classify.py:119-142`): I1 4, I2 4, I3 4, I4 4, I5 4, I6 5, I7 4 = **4.08**
Good: `FAMILIES` next to `SCORECARD`, S9 on the override, constants with S-ids above it.
Gaps: `high_from=4, moderate_from=2` are bare literals (the module docstring has the table: "4 high,
2-3 moderate"); `labels={s: s for s in (...)}` is an identity map whose purpose (state ids equal the
rung names, display names added separately by `DISPLAY_NAMES`) is not stated. Two lines fix it:
`HIGH_FROM_POINTS = 4  # S3: 2 income + 2 liquidity`, `MODERATE_FROM_POINTS = 2  # S3` and a comment on
`labels`. That is declaration naming, within D-2-2 (structure only for A1).

### A3 declaration (`a3_target_shape.md` §5, `triage.md` A3-1): I1 4, I2 3, I3 5, I4 4, I5 4, I6 5, I7 5 = **4.18** (sketch)
Good: the three dimensions map one-to-one to D-A3 A / B / C; the decision map (§3) points D-A3-5, -6, -16,
-17, -20 at one home each; `BROKEN_OVERRIDE` (P2) makes an open option a single line; `a3_override` is
today's `a3_strong_negative_reason`, so no provenance is lost. The `silent` levels per dimension state
the Unknown rule in the declaration instead of a boolean in a node.
Gaps (all in the bundle, not the refactor):
- The points maps are inline literals in the sketch (`{"kept": 2, "partly_kept": 1}`, `{"regular": 2,
  "some": 1}`, `{"clean": 1}`). Rubric I2 example 1 and A1's `INCOME_POINTS` say name them
  (`COMMITMENT_POINTS`, `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS`, each with the D-A3-16 sheet row).
  `HIGH_FROM` / `MODERATE_FROM` are already named in the sketch; A1 should adopt the same names (I7).
- Dimension names (`commitments`, `dlq_payments`, `pre_dlq_record`) are good; put "Dim A / B / C" in a
  comment so the spec's letters and the output columns meet in one place.
- Same word, same meaning: the label map is `STATE_LABELS` in the A3 sketch, `DISPLAY_NAMES` in A1 and
  A4. Pick one (R3-2).

## 4. Tier-L files that changed

Weighted = (22·I1 + 14·I2 + 16·I3 + 12·I4 + 12·I5 + 16·I6 + 8·I7) / 100. Tier K (`rl_a4_spine`) and
tier A not scored. Deltas are against my round 1 scores.

| File | I1 | I2 | I3 | I4 | I5 | I6 | I7 | Wtd | Delta | Lowest and fix |
|---|---|---|---|---|---|---|---|---|---|---|
| `_common.py` | 4 | 5 | 4 | 4 | 5 | 5 | 4 | **4.42** | +0.14 | `log_latest_month` `latest_per_account` switch now has its exit note; still a switch (I3). |
| `scoring_engine.py` | 4 | 3 | 3 | 4 | 4 | 5 | 5 | **3.94** | -0.22 | `score` 45 lines; rung digits; mode default. Scored against a bigger job than `StateLadder` (R3-1). |
| `_dpd_journey/anchor.py` | 5 | 4 | 4 | 5 | 5 | 5 | 4 | **4.62** | 0 | `:41` reword the arithmetic comment. |
| `_dpd_journey/__init__.py` | 3 | 3 | 4 | 4 | 5 | 4 | 4 | **3.76** | +0.12 | `# ruff: noqa: F401` file-wide hides which names are used; two groups are commented, acceptable. |
| `_dpd_journey/_dates.py` | 4 | 4 | 4 | 3 | 4 | 3 | 4 | **3.72** | 0 | `d`, `c` argument names remain. |
| `_dpd_journey/logging.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | +0.12 | contract is a comment, `_log_sequence_stats` still one 30-line dict. |
| `_dpd_journey/spark.py` | 3 | 3 | 3 | 3 | 4 | 3 | 3 | **3.12** | +0.16 | `build_dpd_sequences` ~90, `build_deterioration` ~85 lines, UDF closures inline (R3-3). |
| `_dpd_journey/states.py` | 5 | 4 | 4 | 4 | 4 | 4 | 3 | **4.14** | +0.22 | state names are literals; `assign_state` keeps a pylint disable. |
| `a1_ability/classify.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.08** | +0.32 | `:127` bare `4` / `2`; identity `labels` map; `build_a1_ability` ~65 lines + one disable. |
| `a1_ability/signals.py` | 4 | 4 | 3 | 4 | 5 | 4 | 4 | **3.96** | +0.12 | income builder still a source-tagged union; `first` in the liquidity floor. |
| `a1_ability/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | 0 | one input line added (`crx_persona`). |
| `a2_locatability/signals.py` | 4 | 4 | 3 | 4 | 5 | 5 | 4 | **4.12** | +0.16 | `build_dcore_signals` 69 lines; reachable rule inline (R3-4). |
| `cc_a4_deterioration/nodes.py` | 4 | 3 | 4 | 4 | 4 | 3 | 3 | **3.62** | +0.50 | `:26` `_RESTRUCTURE_DLQ_THRESHOLD = 4` still a copy of cc_spell's (N-9). |
| `rl_a4_deterioration/nodes.py` | 4 | 4 | 3 | 4 | 4 | 3 | 3 | **3.60** | +0.48 | `build_rl_a4_deterioration` 52 lines, two disables (N-8). |
| `cc_a4_deterioration/pipeline.py`, `rl_a4_deterioration/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 5 | **4.08** | +0.16 | `TAGS` once per file. |
| `cc_full_history/pipeline.py`, `rl_full_history/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | +0.16 | raw read documented as a layer exception (Q-16). |

Average of the 18 changed files: **3.95**. Lowest file: `_dpd_journey/spark.py` (3.12). Lowest criterion
overall is still I3 (long functions: `spark.py`, `build_dcore_signals`, `build_a1_ability`, `score`).
Highest: I5 and I6.

## 5. New issues for round 3 (consistency and convergence only)

R3-1 [`scoring_engine.py:62-103`] `Scorecard.score` 45 lines, pylint disable. Split into `_points`, `_rung`,
  `_unknown`, `_reason`; give the rung digits names (`HIGH, MODERATE, LOW = 2, 1, 0`); reject unknown
  `Override.mode` in `__post_init__`. Behaviour neutral, spec cases already pin it. Related, for the
  Master: N-16 (a1 / A4 `*_rule` column) is still a question for the user; the engine already computes
  `a1_override` / `a1_reason`, so the answer costs one `select` line in the redesign bundle.
R3-2 [`a1_ability/classify.py:119-142`, A3 sketch, A4 `states.py`] same idea, different spelling: name
  `HIGH_FROM` / `MODERATE_FROM` (with S3) in A1 as in the A3 sketch; one label-map name (`STATE_LABELS` or
  `DISPLAY_NAMES`) on all axes; comment the identity `labels` map; in the A3 bundle name the three
  points maps. Cheap, declaration only.
R3-3 [`_dpd_journey/spark.py`] one-line contract comments on the two `_udf` closures (columns in, struct
  out) and a docstring first line per `build_*` that says the stage order; no further split. If R-E / R-O
  keep the closures inline, this is the least I accept for the lowest file.
R3-4 [`a2_locatability/signals.py:240-275`] name the last two inline pieces: `_last_call_days(streak)` for
  the `slice(sort_array(collect_list(...)))` expression and `_reachable(w_start)` for the D-A2-7 contact
  rule, so `reachability_state` reads `when(_gone_dark(...), ...).when(_reachable(...), ...)`. Lines
  neutral.
R3-5 [`cc_a4_deterioration/nodes.py:26`, `rl_a4_deterioration/nodes.py`] import the restructure bucket
  from `_dpd_journey/constants.py` (N-9; cc_spell is tier K and stays); replace the generator unpack in
  `_original_loan_months` with two plain lines or a named `_chain_frames`; `_rows_before_chain` for the
  chain switch (N-8).
R3-6 [`_dpd_journey/anchor.py:41`] reword the arithmetic comment (section 1).
R3-7 [shared bundle check] carry the S1 "flagged, not changed" `string_key` site table as an explicit
  bundle check; until then the obs base (no trim) and A4 (trim) agree only for unpadded ids. A doc item, no
  code.

## Convergence check (R-I view)

- Blocking objections open: **none**. All five round 1 conditions are met or mostly met, with the
  remainders listed above as non-blocking R3 items.
- Tier-L average 3.95 (target 3.5; round 1 3.86). The three weakest changed files are `spark.py`
  (3.12), `rl_a4_deterioration/nodes.py` (3.60), `cc_a4_deterioration/nodes.py` (3.62); R3-3 and R3-5
  move them to about 3.4 / 3.9 / 3.9.
- A1 and A3 declarations both score above 4.0 on the sketch; they reach 4.3+ with R3-1 and R3-2.
- Axis stability respected: A1 got structure only (D-2-2); R3-2 is the one A1 item and is a declaration
  name, not a rule change. A4 and A2 carry the polish.
