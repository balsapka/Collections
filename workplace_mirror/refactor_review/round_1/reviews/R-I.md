# R-I review, round 1 (Interpretability advocate)

Rubric: `rubrics/interpretability.md` (frozen). Input `d1ad38a`, merged tree HEAD (`5c24553`).
Read: PLAN §2-§3, scorecard, merge_log, decisions, proposals S1-S5 and S7, `a3_handoff.md`, the
specs, and every changed tier-L file in the merged tree. Not read: the other reviews, S6 beyond its
handoff text. Behaviour is the gate's, not mine.

**Result.** No open blocking objection on any applied proposal. Tier-L file average **3.86**
(25 files; target 3.5 met). Round-1 net: shared layer and engines read better (named constants in
A1, one `segment`, one `state_label`, one `string_key`, `episode_start`, `window_start`). The
weak spots that remain are all inherited, not introduced: the two 100-line functions in
`_dpd_journey/spark.py` (the S4-03 revert), the A4 wrappers (S4-09/S2-06 reverts), `build_a1_ability`,
`build_dcore_signals`, and rule-fired columns that exist for A2 but not for A1 or A4.

## Proposals

Applied or re-based, as they stand in the merged tree.

**S7 patch + delete list**: accept (blocking: no)  criteria: I6, I7
  Tier D gone (7,028 lines), dead tier-L symbols removed. No spec rule lived in the removed code
  (A2 is in `a2_locatability/`). `build_rl_depart_spine` moved byte-identical into `rl_a4_spine/`.
  Neutral to positive for the analyst: one A2, no orphaned `nodes.py` that still looks live.

**S1-01 `segment()`, `MODEL_ID_SEGMENT` in `_common`**: accept (blocking: no)  criteria: I2, I6, I7
  One definition per segment name and an explicit `ValueError` (`_common.py:46-52`). A3 band rules
  (D-A3-6) point at exactly one helper. Good.

**S1-02 `string_key`**: accept (no)  I2, I7
  Three copies become one with a docstring that carries the reason (`1.23456789E8`).

**S1-03 `window_start(months, anchor=None)`**: accept (no)  I2, I6
  One definition of "the last N calendar months, the observation month included"; A1, A2, `pit_latest`,
  `window_agg`, `lookback_floor` and the future A3 share it. This is also the answer to S6-H01.

**S1-04 `state_label`**: accept (no)  I7
  Three label maps become one helper. Small readability debt: `[F.lit(x) for kv in labels.items() for x in kv]`
  (`scoring_engine.py:89`) needs a second look; rename `kv` to `pair` or flatten in a named line. Not a rule.

**S1-05 `dcore_account_events`**: accept (no)  I5, I6, I7
  Docstring cites D-A2-8 and D-A3-7, names the output columns and says "not dated by the observation".

**S1-06 one state logger (`log_latest_month(latest_per_account=)`)**: accept (no)  I7
  One log format on all axes. The boolean is a small switch (I3), but the docstring gives the reason
  (A4 on billing dates). Add "remove with the cc_spine month-end shift" so the switch has an exit.
  PROD log change is listed in the merge log; fine.

**S1-07 `episode_start`** (`_dpd_journey/anchor.py`): accept (no)  I1, I6
  Best addition of the round: D-A3-2 has one named place, the module docstring names the rule, the
  left-censored column is carried. Two gaps, see N-12 and N-13 (no test or golden case reaches it
  because no tier-L node calls it; the `history_months - 1 - months_before_spell` arithmetic is
  uncommented).

**S1-08 `window_agg(start=)`**: accept (no)  I6
  The A3 episode lower bound has a home. The contract "aggs may read `start`" is stated. Keep the
  parameter as a column name, not a method switch (D-A3-3), as it is.

**S3-01, S3-02 dict inputs** (obs base, full history, A4): accept (no)  I7
  `inputs={"obs_base": ..., "model_id": "params:model_id"}` reads as the node signature. Same shape as A1/A2.

**S3-03 `require_columns` on spines and sources**: accept (no)  I1, I5
  The input contract becomes visible at the top of each node. It pushes `build_cc_full_history`,
  `build_rl_full_history` over 40 lines; accepted, the lines carry a contract (PLAN scorecard
  "allowed for `require_columns`"). The RL list should be moved to a module constant if it grows.

**S3-05 `crx_persona` required on RL full history, S3-06 registry wrap, S3-07 catalog comments**:
  accept (no)  I5, I7
  Optionality that hid a contract is gone.

**S2-01 `scoped` + `pit_latest` aggregate**: accept (no)  I3, I5
  `scoped` is named for its contract. `pit_latest` is 41 lines but is a straight build: anchor,
  condition, aggregate, select. Docstring says how ties are broken, which an auditor needs.

**S2-02 A1 one join per source**: revise (blocking: no)  criteria: I1, I3
  `build_liquidity_signals` (`a1_ability/signals.py:208-280`) stacks the activity legs and the balance
  rows into one table with sentinel columns (`lit(None)` balance, `lit(1)` held, `lit(0)` customer),
  then reads `casa_active` and `casa_held` out of it with `max(when(...))`. S11 "customer-initiated
  movement" and "holds a CASA" are each split over a union column and an aggregate; the docstring
  helps, the code does not. Acceptable as is for the gate, but make each rule a named builder
  (`_casa_legs` with a one-line contract per column, `casa_active` and `casa_held` as two named
  expressions) in round 2. Income signals (`build_income_signals`) have the same shape with `INTERNAL`/`BUREAU`.

**S2-03 A2 DCORE account-days** (re-based on S1-05): revise (blocking: no)  criteria: I1, I3
  `_dcore_days` is a good named step, but `build_dcore_signals` is 78 lines and one aggregate that
  produces nine outputs for three rules (D-A2-7 non-reachable, reachable, deceased/skip-trace dates).
  `gone_dark` stays an inline boolean (`signals.py:269-274`) and no output says which reachability
  rule fired. The "attempt days, newest first; other days sort last and are never read" ordering
  trick (`F.when(attempt, day).desc_nulls_last()`) is clever but is the D-A2-20 streak, and its name is
  `_rank`. Round 2: the S4-04 DCORE split was skipped by D-1-7 because S2-03 rewrote the function;
  re-brief S4 for the new shape: `_last_call_days(days, streak)` (n, failed, oldest) and
  `_reachability(...)`, so D-A2-7 and D-A2-20 have named places. This is not a regression (the
  baseline was a larger function with the same inline boolean), so non-blocking.

**S2-04 A2 scoped location / demographics / Way4**: accept (no)  I3
  `_latest_evidence`, `_location_rule` (S4-04) make L1-L4 readable top to bottom: evidence, then rule,
  then state, then unknown reason. Model shape for A3.

**S2-05 distress floor pruning, S2-07 RL A4 no `collect`**: accept (no)  neutral
  S2-07 adds a nested `frame()` inside the node (`rl_a4_deterioration/nodes.py:111-115`); fine, but see N-8.

**S4-01 A1 threshold names**: accept (no)  I2, I4
  Exactly the rubric's example 2: `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`, `CASA_MAX_FALL`... each with an S-number
  and unit. Spec cells S2, S4, S10, S12 updated in the same commit, which keeps the trace honest.
  Remaining: the ladder thresholds `4` and `2`, the level strings and the window-number dict keys, see N-2.

**S4-02 `__all__`, `log_state_stats` public**: accept (no)  I5
  `__all__` lists underscore names (`_glitches`, `_mean`, `_month_idx`...) and the single letters `H, N, P, R`.
  Needed for tests today, but the public surface is no longer a surface. See N-6.

**S4-04 (part) A2 split**: accept (no)  I1, I3 (see S2-03 for the dropped DCORE half).

**S4-05 A1 distress split**: accept (no)  I1, I3
  `_flag`, `_require_returns_from`, `_distress_events` each do one thing and the S9/S15 trace is
  `distress_cheque` / `distress_dds` / `distress_bureau`. Keeps S2-05's floor.

**S4-06 `assign_state` predicates**: accept (no)  I1, I3
  `_is_early_payment_default` (Q1) and `_is_stabilized` (Q2) carry the rule id and the threshold names.
  Q3 and Q4 are still inline; finish the job in round 2 (N-7).

**S4-07 `_shift_cycle_bills`**: accept (no)  I3, I4  (the name says the step; "Step 1 of build_history" is in the docstring).

**S4-10 `SEG_60_180` / `SEG_180_PLUS`**: accept (no)  I2
  Agree with D-1-8 (`_common`, not `_dpd_journey`). The A3 target text still writes `"60_180"` as a literal (N-11).

**S4-11 A2 `TAGS`**: accept (no)  I7.  **S4-08 skipped**: agree (duplicate of S1-04).

**S5 docstrings (28 files)**: accept (no)  I5, I1
  History and tickets are gone (T43, R13, R20, "mirror bundle 14"), spec IDs and run commands were
  added where the code had none (`signals.py` D-A2-n, `classify.py` S-n). Two boundaries still lack
  one: `_dpd_journey/logging.py::_log_sequence_stats` and the `_mean`/`_count_at_least`/`_months`
  helpers in A1 classify (private, acceptable; the first is called by two modules).

**Held, S3-04 tag normalisation**: accept in principle, hold for Q-15 (blocking: no)  criterion I7.
  See "Held proposal" below.

## The three proposals reverted only for E501

Question: should each come back in round 2 with the line wrapped? **Yes, all three**, with the
conditions below.

- **S4-03 (split `build_dpd_sequences` / `build_deterioration`)**: yes, accept as the round-2 item
  with highest R-I value. These two are the longest functions in tier L (122 and 104 lines, `spark.py:119`, `:244`),
  and a stage-by-stage name (`_monthly_rows_per_account`, `_spine_rows_with_history`, `_classify_udf`) is
  what makes the sequence "history, classify, select" readable. Conditions: wrap the new `_month_col`
  docstring line to 88; every new helper gets a one-line contract (columns in/out); re-base on the
  merged `string_key` and `state_label`; keep type hints as a separate, optional commit (neutral).
  Size: functions over 40 lines in `spark.py` should fall from 2 to 0 (the `ship_by_value` and
  schema code are small).
- **S4-09 (A4 wrapper steps)**: yes, accept. `_original_loan_months` and `_restructure_blind_spot`
  give the wrappers the same top-to-bottom shape (history, flag, engine call), and the CC flag becomes
  a named function with the "opened mid-delinquency" rule in its docstring. Condition: wrap the 90-character
  docstring line; the RL `frame()` closure added by S2-07 should become `_chain_frames` in the same edit (N-8).
- **S2-06 (CC restructure flag as one aggregate)**: yes, but fold it into the S4-09 helper
  `_restructure_blind_spot` so there is one place for the rule. The `min(struct(obs_date, -dlq_bucket))`
  negation hides the tie-break (earliest date, then the worst bucket) in a sign flip, and `-F.col("_first.neg_bucket") >= threshold` reads backwards.
  Acceptable only with the rule in the docstring and a name for the struct field (`worst_bucket_neg` is a
  mechanism name; prefer a comment line "negated so the smallest struct is the worst bucket"). If R-E and R-O
  want it without that, I yield on the efficiency (no rule is lost: the rule stays in the docstring), I do not
  yield on a bare negation with no explanation. Wrap the 89-character comment.

## Held proposal S3-04 (tag normalisation)

Accept once Q-15 is answered "yes". Today A1 and A2 use `TAGS = [crx_persona, crx, <axis>, <name>,
persona_axis]`, the A3 handoff proposes the same, and the A4 and full-history nodes still use
`[crx, cc, cc_a4_deterioration]` / `rl_b1`. That is "same shape, different spelling" (I7 = 3 for the A4
pipelines). `rl_b1` is a ticket id and a D3 history leak. Also drop the pipeline-level `tags=["crx_persona"]` as proposed.
No R-I objection to the tag renames; the cost is the user's (selection by tag in PROD), not interpretability.
Related: A1/A2 call the constant `TAGS`, the A3 handoff `_TAGS` (N-10).

## A3 handoff verdicts (recorded for the A3 session)

| Id | R-I verdict | Why |
|---|---|---|
| S1-H1 RL A3 uses `string_key` | **accept** | one definition of a business-neutral rule (I2/I7); removes the third copy and a comment about a private helper. |
| S1-H2 CC A3 ladder on `StateLadder` | **accept** | the ladder is the same cell-for-cell as A1 (I7, I6). Condition: keep the Unknown gate as its own named function (`_a3_unknown(level_a, level_b, level_c, has_refusal)`), so S11-style gate has one place, as in A1 (N-2). |
| S1-H3 drop `_log_a3_stats` | **accept** | one logger per axis; the `a3_path` column stays in the data, only the log breakdown goes. List the removed log in the A3 bundle notes. |
| S2-H-01 latest right-party contact as an aggregate | **accept with rename** | `max(struct(date, non-refusal flag, disposition))` must name its tie rule: `_later` is a mechanism name; use `_not_refusal` and a comment "same day: a refusal sorts first (D-A3-19)". The note that tied rows now pick the largest disposition string is a behaviour question for the gate. |
| S3-A3-H1 dict inputs and one tag set | **accept** | dict inputs yes now (I7, matches A1/A2); tag set waits for Q-15 as S3-04 does. |
| S3-A3-H2 schema guards turn a source off quietly | **accept, option (b)** | an auditor cannot trace an `unknown` state to "column missing, signal nulled"; D2 `require_columns` or an explicit optional input makes the cause visible. Needs Q-S3-7 first. |
| S4-H1 third `_string_key` copy | **accept** | same change as S1-H1; merge the two entries. |
| S6-H01 window start by `add_months` on month-end | **accept** | A3 takes `_common.window_start` and `greatest(anchor, ...)`; "calendar months, observation month included" stays one definition (I2). Write it in D-A3-2 so the spec and the helper say the same words. |
| S6-H02 DCORE bound exclusive at the observation date | **accept the finding; one named bound** | whichever the user picks, A2 and A3 should share one convention, defined in one place (`_common` helper or the S1 `_in_episode`, which today writes `<` while A2 reads `<=`, N-11). R-I has no preference between the two bounds. |
| S6-H03 A4 anchor on cropped or blind histories | **accept** | the `episode_left_censored` column from `episode_start` should reach the A3 output (a `censored` reason on Dimension C `no_record`), so the auditor sees why a row is `no_record`. |
| S6-H04 "oldest open overdue bucket" with two ranges | **accept** | a shared `oldest_open_amount(buckets)` with named ranges (A1: `OVD_01..06`, S1; A3: `OVD_01..07` + `minimum_due`, D-A3-12) beats two functions that must be read side by side. The ranges are constants with spec IDs, not parameters hidden in a call. |

The target A3 shape in `S1.md` scores **5 on I6** for engine layout and the decision-to-helper map, and
**4** overall: fix the literal segment keys and the `_in_episode` bound (N-11) and it is a 5.

## Files (merged tree)

Weighted = (22·I1 + 14·I2 + 16·I3 + 12·I4 + 12·I5 + 16·I6 + 8·I7) / 100. Tier L only; tier K
(`rl_a4_spine/nodes.py`, moved byte-identical) and deleted files not scored.

| File | I1 | I2 | I3 | I4 | I5 | I6 | I7 | Wtd | Lowest and fix |
|---|---|---|---|---|---|---|---|---|---|
| `_common.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.28** | `log_latest_month` `latest_per_account` switch: give it an exit note. |
| `scoring_engine.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.16** | `:89` flatten comprehension, rename `kv`. |
| `_dpd_journey/anchor.py` | 5 | 4 | 4 | 5 | 5 | 5 | 4 | **4.62** | `:38` explain `history_months - 1 - months_before_spell`. |
| `_dpd_journey/__init__.py` | 3 | 3 | 4 | 3 | 5 | 4 | 4 | **3.64** | `__all__` exports private names and `H,N,P,R`; group under a "for tests" comment. |
| `_dpd_journey/_dates.py` | 4 | 4 | 4 | 3 | 4 | 3 | 4 | **3.72** | `d`, `c` argument names; three near-identical month helpers. |
| `_dpd_journey/constants.py` | 4 | 4 | 5 | 4 | 4 | 4 | 4 | **4.16** | fine. |
| `_dpd_journey/history.py` | 3 | 3 | 3 | 3 | 4 | 3 | 3 | **3.12** | `build_history:90` 84 lines; `by_month`, `best`, `ms`, steps numbered, not rule-named. |
| `_dpd_journey/logging.py` | 4 | 4 | 3 | 4 | 3 | 4 | 4 | **3.72** | `_log_sequence_stats:16` no docstring, one 30-line dict. |
| `_dpd_journey/params.py` | 3 | 4 | 4 | 4 | 4 | 4 | 4 | **3.78** | `("truncate","drop")` repeated as literals (`:14`, `:62`); name `GAP_POLICIES`. |
| `_dpd_journey/spark.py` | 3 | 3 | 2 | 3 | 4 | 3 | 3 | **2.96** | `build_dpd_sequences:119` 122 lines, `build_deterioration:244` 104 lines. Fix: S4-03 in round 2. |
| `_dpd_journey/states.py` | 4 | 4 | 4 | 4 | 4 | 4 | 3 | **3.92** | Q3/Q4 inline; `STATE_RULES` keys carry no Q id; state names are literals in `assign_state` while `STATES` exists. |
| `a1_ability/classify.py` | 4 | 4 | 3 | 4 | 4 | 4 | 3 | **3.76** | `build_a1_ability:136` 76 lines and 3 pylint disables; S11 gate inline (`:163-167`), ladder `4`/`2` literals (`:41-42`). |
| `a1_ability/signals.py` | 4 | 4 | 3 | 3 | 5 | 4 | 4 | **3.84** | `INTERNAL="int"`/`BUREAU="bur"` vs `BUREAU_BOUNCE="BUREAU"` (`:41,:49`); the CASA union in `build_liquidity_signals`. |
| `a1_ability/pipeline.py`, `cc_a1_ability/pipeline.py`, `rl_a1_ability/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | `if product == "rl"` input switch (`:49`) is the one product branch; keep. |
| `cc_a1_ability/nodes.py` | 5 | 5 | 4 | 4 | 5 | 4 | 4 | **4.48** | model for a thin wrapper. |
| `rl_a1_ability/nodes.py` | 5 | 5 | 4 | 4 | 4 | 4 | 4 | **4.40** | docstring should say "S1: one EMI" first line (it does) - fine. |
| `a2_locatability/classify.py` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.16** | no `reachability_rule` beside `location_rule`. |
| `a2_locatability/signals.py` | 4 | 4 | 3 | 4 | 5 | 4 | 4 | **3.96** | `build_dcore_signals:203` 78 lines, inline `gone_dark`. |
| `a2_locatability/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 5 | **4.08** | fine. |
| `cc_a4_deterioration/nodes.py` | 3 | 3 | 3 | 3 | 4 | 3 | 3 | **3.12** | inline restructure query `:41-58`; `_RESTRUCTURE_DLQ_THRESHOLD=4` copies cc_spell's. S4-09/S2-06. |
| `rl_a4_deterioration/nodes.py` | 3 | 3 | 3 | 3 | 4 | 3 | 3 | **3.12** | `build_rl_full_history_linked:83` 76 lines with a nested `frame()`; `build_rl_a4_deterioration:233` 52 lines + 2 pylint disables. |
| `cc_a4_deterioration/pipeline.py`, `rl_a4_deterioration/pipeline.py` | 4 | 4 | 4 | 4 | 4 | 4 | 3 | **3.92** | old tag spelling, `rl_b1` (S3-04). |
| `cc_full_history/nodes.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | `build_cc_full_history` 43 lines with the contract block; acceptable. |
| `rl_full_history/nodes.py` | 4 | 4 | 3 | 4 | 4 | 4 | 4 | **3.84** | 54 lines; the required-columns list could be a constant. |

Tier L average **3.86**. Lowest criterion overall: **I3** (functions over 40 lines: 22 in the metrics,
the sub-3 ones are `spark.py`, `history.py`, `build_a1_ability`, `build_dcore_signals`, A4 wrappers).
Highest: I5 (S5 pass) and I6 (anchor, segment, window helpers).

## New issues

N-1 [`_dpd_journey/spark.py:119,244`] 122- and 104-line functions; resubmit S4-03 wrapped, split into named stages, each with a column contract → S4.

N-2 [`a1_ability/classify.py:41-42,136-170`] `_LADDER` thresholds `4` and `2` are literals; level strings (`"stable"`, `"weak"`, `"adequate"`) repeat in three places; the S11 Unknown gate is an inline boolean inside a 76-line function with three pylint disables. Proposed: `A1_HIGH_FROM_POINTS = 4  # S3 points: 2 income + 2 liquidity`, `A1_MODERATE_FROM_POINTS = 2`, `a1_unknown(points, distress, casa_active) -> Column` (S11, three inputs, one rule), `a1_points(income, liquidity)`, and split `build_a1_ability` into `_levels`, `_state`, `_diagnostics`, `_output` → S4.

N-3 [`a2_locatability/signals.py:203-282`] `build_dcore_signals` is one aggregate with nine outputs; `gone_dark` inline; add `_last_call_days` and `_reachability_state` so D-A2-7 and D-A2-20 each have a named place; `_rank` ordering trick gets a docstring line → S4 (re-brief after D-1-7).

N-4 [`a1_ability/signals.py:208-280`, `:135-205`] stacked union with sentinel columns hides S11 (`casa_active`, `casa_held`) and S3/S14 (internal vs bureau rows); name the legs builder and each flag expression → S4.

N-5 [`a1_ability/signals.py:41,49`] `BUREAU = "bur"` (income source tag) and `BUREAU_BOUNCE = "BUREAU"` (distress reason) are two constants with one meaning of "bureau"; rename to `SOURCE_INTERNAL`/`SOURCE_BUREAU` and `REASON_BUREAU_BOUNCE`, with units in the comment → S4.

N-6 [`_dpd_journey/__init__.py:63-128`] `__all__` carries underscore names and `H, N, P, R, NO_PRIOR`; split it into "public" and "re-exported for the parity tests" blocks with a comment, and give `H/N/P/R` a one-line meaning (they are the reference's names, `core.py` says so) → S4/S5.

N-7 [`_dpd_journey/states.py:66-130`] Q3 (repeat delinquent) and Q4 (straight roller) are inline in `assign_state` while Q1 and Q2 are named predicates; `STATE_RULES` keys have no Q id; state names are string literals though `STATES` exists. Add `_is_repeat_delinquent`, `_is_straight_roller`, and tag each key `# Q2`... → S4.

N-8 [`rl_a4_deterioration/nodes.py:83-160,233`] split `build_rl_full_history_linked` (`_original_loan_months` from S4-09, nested `frame()` to `_chain_frames`); `build_rl_a4_deterioration` has two pylint disables, move the chain-switch to `_rows_before_chain` → S4 (with the S4-09 resubmit).

N-9 [`cc_a4_deterioration/nodes.py:25-29`] `_RESTRUCTURE_DLQ_THRESHOLD = 4` is a copy of cc_spell's constant (comment says "same value as"); one definition for the number: move it to `_dpd_journey/constants.py` as `RESTRUCTURE_OPENING_BUCKET` (conformance D2, native CC bucket 4 = 61-90 DPD) and import it; cc_spell is tier K and stays frozen → S4/S1.

N-10 [A1/A2 `TAGS`, A3 handoff `_TAGS`; A1 `DISPLAY_NAMES`, A2 `LOCATION_LABELS`, A4 `DISPLAY_NAMES`; A1 `_LADDER`, A3 `_LADDER` in H2] same idea, different spelling. Round 3 consistency pass: `TAGS`, `STATE_LABELS` (or `DISPLAY_NAMES`) everywhere, one ladder name → S1/S4.

N-11 [`proposals/S1.md` "Engine-private" block] `ANY_PAYMENT_MONTHS = {"60_180": 3, ...}` and `REGULAR_FROM_MONTHS` use string keys instead of `SEG_60_180`/`SEG_180_PLUS`; `_in_episode` writes `< observation_date` while A2 reads `<= observation_date` (S6-H02); A1's `STABLE_INCOME_FLOORS = {3: 2, 6: 3}` and `CASA_MIN_MONTHS` key by window length, A2's `GONE_DARK_DAYS` by segment: two key systems for one segment idea. Key all by segment → S1 (design text), S4 (A1 dicts).

N-12 [`_dpd_journey/anchor.py:36`] one-line comment for `months_back = history_months - 1 - months_before_spell` (index of the spell start counted from the history end); `episode_start` has no caller, spec test or golden case, so D-A3-2 is not exercised by any run → S4 (comment), Cartographer (add a case to `refactor_golden.py` or the A4 spec test).

N-13 [`_dpd_journey/anchor.py`, S6-H03] the anchor on cropped histories: document in the docstring which rows come back with `episode_left_censored = true` and what the consumer must do → S5 with S6.

N-14 [`_dpd_journey/logging.py:19`] `_log_sequence_stats` has no docstring and is imported by `spark.py` and `__init__`; add a two-line contract → S5.

N-15 [`_dpd_journey/history.py:90-190`] `build_history` is still 84 lines with numbered steps in comments; extract `_pick_latest_per_month` and `_apply_floor_and_gaps` the way `_shift_cycle_bills` was done; names of locals (`best`, `ms`) → S4.

N-16 [output columns, A1 and A4] A2 carries `location_rule`; A1 (`a1_unknown_reason` only) and A4 (state only) have no column that says which rule fired. This is the largest remaining I1 gap for an auditor. Adding a column is barred by PLAN §3 rule 5 and rule 1, so it is **not** a refactor item: it needs a user question and a fix bundle (`a1_rule`: S-id of the points/ distress/ unknown path; `det_rule`: Q0-Q4). Ask now, so the A3 `*_rule` idiom is the same on all four axes → Master (question to the user, not S-owned).

N-17 [`a1_ability/classify.py:38-39`] `INCOME_POINTS` and `LIQUIDITY_POINTS` carry no spec ID (the points table lives in the GRR MECE header); add `# GRR MECE points` and fold into N-2 → S5.

## Convergence check (R-I view)

- Blocking objections open: none. Four "revise" items (S2-02, S2-03, and the S2-06 / S4-03 / S4-09 resubmits) are non-blocking.
- Average of tier-L files 3.86, above the 3.5 target; the lowest file is `_dpd_journey/spark.py` at 2.96 and rises to about 3.6 with S4-03 alone.
- To reach 4.0 in round 3: N-1, N-2, N-3, N-7, N-8, N-9, N-10 and the user's answer on N-16.
