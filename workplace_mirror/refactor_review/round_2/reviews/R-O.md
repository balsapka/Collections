# R-O review, round 2 (Owner)

Frozen rubric `rubrics/owner.md`. Tree HEAD `7ae2a08`; diff `git diff 2942237 HEAD -- workplace_mirror/src
workplace_mirror/conf workplace_mirror/checks` (20 files, +542 / −497). Read: PLAN (incl. Axis stability),
decisions D-1-*, D-2-1, D-2-2, questions (all answered; Q-26 = (b), so R-I N-16 is settled), round 1
R-O and triage, S1–S5 logs, gates (all green), R-E and R-I round 2 reviews (read after scoring files).

Criteria: O1 PROD operability 18 · O2 change risk / bundle-ability 18 · O3 auditability 16 · O4 one
engine, thin wrappers 14 · O5 fits A3 14 · O6 contracts / Kedro 10 · O7 clarity per line 10.

## Summary

- Gates green; golden identical (79 datasets); no new Spark action (9); tier L 4,119 → 4,087.
- Round 2 closed both PROD cost items I raised: the A2 DCORE window is gone (N-3, Exchange 7 → 7,
  Window 1 → 0) and the CC A4 restructure flag is one aggregate over the largest A4 input. N-4 stays a
  bundle measurement, as ruled.
- Every round 1 revise item landed within budget, except triage #6 (A1 ladder thresholds `4` / `2`
  as named constants): not done by S4. It carries to round 3.
- **21 accept, 0 revise, 0 reject.** One blocking objection (R-E on S1-R2-01) is waived below; R-E
  offered that path itself.
- My line-weighted scores: O1 3.94 · O2 4.02 · O3 3.87 · O4 4.35 · O5 4.08 · O6 4.77 · O7 3.60
  (weighted 4.07). Not yet sign-off grade on O1, O3, O7; see "Convergence".

## Proposals

Verdict, my weighted score, deciding criteria. "Blocking" is my own objection.

### S1
S1-R2-01 `Scorecard` / `Dimension` / `Override` replace `StateLadder`: **accept** (blocking: no) 4.3  O4, O5
  One scoring engine for A1 and A3 (user's wish), reason and override columns back, A1's ladder one
  declaration, 14 spec rows. R-E's blocking 3 on the unused modes is waived (ruling D-2-3). One defect
  to fix in round 3: `moved.get(o.mode, to)` turns a typo in `mode` into a silent FORCE; index the dict
  instead so a bad mode raises (`scoring_engine.py:80-81`, 0 lines).
S1-R2-02 `build_a1_ability(..., **signals)` + `FAMILIES`: **accept** (no) 4.1  O5, O4
  Node input keys unchanged, so the pipeline and catalog are untouched; positional callers are listed
  for the tests. Join order follows the node's dict order and cannot change an output (left joins on
  `GRAIN`, distinct columns): one comment line (R-E N-R2-4), round 3.
S1-R2-03 `GONE_DARK_DAYS` → `_common`: **accept** (no) 4.4  O5, O4
  Still importable from A2; A3 never imports A2. Net 0.
S1-R2-04 `episode_left_censored` + checked cases: **accept** (no) 4.3  O5, O3
  R-1's condition met: `check_anchor` reaches `episode_start` and both `window_agg(start=)` bounds.
S1-R2-05 `build_dpd_sequences` → `require_columns`: **accept** (no) 4.4  O6, O1
  The `ValueError` text changes: list it in the A4 bundle notes with S1-06's log change.
S1-R2-06 `string_key` in RL A4: **accept** (no) 4.2  O4, O3
  The "flagged, not changed" site table is a shared-bundle check (R-I R3-7), not code: the Master puts
  the trim / type aggregate into the shared bundle's PROD check.
S1-R2-07 A3 target-shape text: **accept** (no) —  O5

### S3
S3-04 tag normalisation: **accept** (no) 4.2  O4, O2
  `TAGS` once per file, same five-name shape on A1 / A2 / A4. Removed tag values (`cc`, `rl`,
  `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`) go in the A4 bundle notes, with the line that
  `--tags full_history` now selects both histories.
Q-16 note (`cc_full_history` raw read documented): **accept** (no) 4.0  O3, O6

### S2
S2-06 `_restructure_blind_spot`: **accept** (no) 4.6  O1, O3
  Self-join and second `groupBy` over the full CC billing history gone; the tie rule is written once,
  in my R-5 words. +3 against +2 (one wrap of an 89-char line): accepted.
N-3 window-free DCORE + `_gone_dark`: **accept** (no) 4.5  O1, O3
  All four conditions of R-9 met (golden, A2 spec, Exchange count, function size). `F.forall` kept
  (ruling D-2-6). The A2 bundle check keeps the `_attempt` share and spill measurement as a safety net.
S2-02 naming (`_casa_legs`, `casa_active`, `casa_held`): **accept** (no) 4.0  O3
  R-6 met: the S11 rules are named expressions before the join; the plan is unchanged.
Q-14 (b) liquidity floor from `crx_persona`: **accept** (no) 4.2  O1, O6
  The user's answer, applied without an action; S2's proof that the floor reads nothing a window could
  use is sound (the obs base starts at the persona start month). Test-churn line listed.
N-4: no change, measurement in the A1 / A2 bundle checks: **accept** (as ruled).

### S4
S4-02 `__all__` → `# ruff: noqa: F401`, `_month_label`, `__init__` docstring: **accept** (no) 4.3  O7, O2
  R-2 met exactly; `__init__.py` 134 → 61 lines.
S4-03 part (`_monthly_rows_per_account`, `_spine_rows_with_history`): **accept** (no) 3.9  O7, O3
  R-4 met. The two engine functions are still ~90 / ~85 lines; I accept that as the A4 parity design
  (UDF closures stay inline, R-4). One-line closure contracts are the round 3 minimum (R-I R3-3).
S4-09 RL half (`_original_loan_months`): **accept** (no) 4.0  O3, O7
  Closure gone, net −2. The generator unpack that replaced it is clever where two plain lines would do
  (R-I R3-5, round 3, 0–1 line).
Q3 / Q4 predicates, Q ids on `STATE_RULES` and `assign_state`: **accept** (no) 4.1  O3
  The four A4 rules now read the same way. State names stay literals (agree with S4, R-E and R-I).
A1 label constants, `kv` → `pair`: **accept** (no) 4.0  O3
  R-10 met; values byte-identical.
Line target, incl. `black -C` compaction: **accept** (no) 3.8  O2, O7
  Ruling D-2-4.
Triage #6 (A1 ladder thresholds named, S11 gate named): **not done**, carried to round 3. The S11 gate
  is met in substance (`no_casa_activity`, commented S11); `high_from=4, moderate_from=2`
  (`a1_ability/classify.py:140-141`) are still bare. A declaration name, inside D-2-2.

### S5
S5 docstrings: **accept** (no) 4.1  O3
  #10, #11, #12 done; −5 net; AST identical. The `_log_sequence_stats` contract as a comment is fine.

## Rulings on disputes

Order applied: gates and behaviour → bundle risk → spec traceability (R-I) → brevity (R-E).

**D-2-3 S1-R2-01 unused `Scorecard` features (CAP, FORCE, High gate, `silent`, `to`): keep; R-E's
blocking 3 waived.** Three reasons, in my order. (1) Bundle risk: `scoring_engine.py` is shared; taking
the modes out now and putting them back in the A3 bundle is two edits of the same shared file across two
bundles, with the A3 session (another writer) owning the second; one edit now is the smaller risk.
(2) The callers are planned and named, not speculative: the user asked for one scoring utility for A1 and
A3; `a1_design_in.md` needs the High gate (two families, one current) and CAP / negative points for
distress; the A3 declaration needs CAP for `BROKEN_OVERRIDE` (V1d) and `silent` per dimension (`thin`,
`no_record`). (3) They are not untested code: 14 spec rows pin every mode. A1 already uses `silent` (its
default). The same test R-1 applied to `episode_start`. One line: one edit of the shared engine, tested,
for two named callers, beats two edits across two bundles. If neither the A1 redesign nor the A3 bundle
uses CAP / FORCE / the gate by the time both ship, the follow-up dead-code pass removes them.

**D-2-4 `black -C` compaction: allowed, with limits.** It is the repo's own formatter: once a call has no
magic trailing comma, plain `black` (which the workplace runs per bundle) keeps it joined, so the
three-way merge sees no reflow churn from the workplace lint. The hunks landed in A4 files (`spark.py`,
`states.py`, CC / RL A4 nodes), which are signed off and not edited in the workplace, so their merge risk
is nil. Limits: (a) only in files a bundle already changes for another reason; (b) not in A1 files
until the A1 redesign bundle (D-2-2), and not in files with workplace edits pending; (c) never run
repo-wide. Line counts use the Master's number (compaction included); R-E's "−14 without it" is recorded
in its review and in the final report. One line: same formatter, no merge churn where it was used, so it
stays; it is not a licence to reflow files the bundles do not otherwise touch.

**D-2-5 R-E N-R2-1 replace `lookback_floor` with the param floor: not in this refactor; it moves with
the A1 redesign bundle.** `lookback_floor` is one of the decided actions in my O1 anchor and PLAN §3.6
forbids only *new* actions, so keeping it breaks no rule. Its callers are all A1 (`a1_ability/signals.py`
three sites, `rl_a1_ability/nodes.py` one); replacing them adds a `crx_persona` node input to three more
A1 nodes and the RL anchor node (pipeline, signature and test churn in the axis that is still moving,
D-2-2). The A1 redesign bundle rewires those nodes anyway; there it costs nothing extra. Then
`lookback_floor` is deleted from `_common` (no A2, A4 or A3 caller today). R-E's equivalence argument is
right and is carried into that bundle's brief. One line: the gain is real but belongs where the A1 nodes
are rewired, not in a pure refactor of a moving axis.

**D-2-6 pyspark ≥ 3.1 for `F.forall`: keep `F.forall`.** The workplace already runs PySpark ≥ 3.3 in
PROD: `unionByName(..., allowMissingColumns=True)` (3.1) in `stg_rr_portf.py:192-194` and
`rl_spell_table/nodes.py:184`, and `DataFrame.withColumns` (3.3) in
`cc_a3_payment_credibility/_signals_common.py:548,580`, all transcribed from code that runs there. The
`array_contains` form is a double negative for no gain. The A2 bundle's UAT step still prints
`pyspark.__version__` (one line in the apply command, no code).

**D-2-7 Round 3 items from R-I R3-1…R3-7 and R-E N-R2-2…N-R2-4:**

| Item | Verdict | Reason (one line) |
|---|---|---|
| R-I R3-1 split `Scorecard.score` into `_points` / `_rung` / `_unknown` / `_reason` | **partly**: no split; take the mode lookup that raises on an unknown mode (0 lines) and name the rung indices from `RUNGS` (≤ +1) | the split is mechanism (R-E wins on brevity); the silent-FORCE default is an audit risk (R-I wins on a rule line) |
| R-I R3-2 `HIGH_FROM` / `MODERATE_FROM` in A1, one label-map name, comment the identity `labels` | **in**: A1 `HIGH_FROM = 4`, `MODERATE_FROM = 2` with the S3 cite (was triage #6) and a one-line comment on `labels`; label map: `DISPLAY_NAMES` is the house name (A1, A4), the A3 sketch text uses it; A2's `LOCATION_LABELS` stays (two state dimensions, A2 signed off, public name) | thresholds are business numbers (my tie-break); renaming a signed-off public constant is churn |
| R-I R3-2 (A3 part) name the three A3 points maps | **handoff text only** (`a3_target_shape.md` §5) | A3 code is the A3 session's |
| R-I R3-3 one-line contracts on the two `_udf` closures + stage order line per `build_*` | **in**, ≤ +4 | `spark.py` is my lowest O3 file; text, no logic |
| R-I R3-4 `_reachable(w_start)` and `_last_call_days(streak)` | **`_reachable` in** (D-A2-7 rule, ≤ +3); `_last_call_days` out | a rule gets a name (R-I); the slice expression is mechanism (R-E) |
| R-I R3-5 restructure bucket import; generator unpack; `_rows_before_chain` | **generator → two plain lines in** (≤ +1); bucket import **out** (R-12 stands, cc_spell tier K); `_rows_before_chain` **out** | clarity at no cost vs a single-caller helper |
| R-I R3-6 reword `anchor.py:41` comment | **in**, 0 lines | text |
| R-I R3-7 `string_key` site check | **Master, bundle plan** (shared bundle PROD check), no code | |
| R-E N-R2-1 `lookback_floor` | **A1 redesign bundle** (D-2-5) | |
| R-E N-R2-2 unused Scorecard modes | **waived** (D-2-3) | |
| R-E N-R2-3 `WINDOW_MONTHS` / `GONE_DARK_DAYS` | **no action**, recheck in the A3 bundle | not a third table |
| R-E N-R2-4 `**signals` order comment | **in**, +1 | stops a reader checking the join order |
| Round 1 deferrals: R-I N-15 `build_history` split; R-I N-10 / N-11 / R-E N-11 | **dropped** (logged). `build_history` stays (A4 parity code, signed off, the split adds lines for no audit gain); N-10 is covered by R3-2; N-11 = N-R2-3 | keep round 3 small (user) |

## Files (merged tree; unchanged files keep their round 1 row)

Weighted = (18·O1 + 18·O2 + 16·O3 + 14·O4 + 14·O5 + 10·O6 + 10·O7) / 100.

| File | O1 | O2 | O3 | O4 | O5 | O6 | O7 | Wtd | Lowest and fix |
|---|---|---|---|---|---|---|---|---|---|
| `_common.py` | 4 | 4 | 4 | 5 | 5 | 5 | 4 | **4.38** | `scoped` broadcast measured in the bundles |
| `scoring_engine.py` | 4 | 4 | 4 | 5 | 5 | 5 | 3 | **4.28** | silent FORCE on a bad mode; 45-line `score` (R3-1 part) |
| `obs_base/` | 4 | 5 | 4 | 4 | 4 | 5 | 4 | **4.28** | — |
| `_dpd_journey/__init__.py` | 4 | 4 | 4 | 4 | 4 | 4 | 4 | **4.00** | — |
| `_dpd_journey/_dates.py` | 4 | 4 | 4 | 4 | 3 | 4 | 4 | **3.86** | — |
| `_dpd_journey/anchor.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.24** | comment wording (R3-6) |
| `_dpd_journey/constants.py`, `params.py`, `core.py` | 4 | 4–5 | 4 | 4–5 | 4 | 4 | 4 | **4.0–4.18** | — |
| `_dpd_journey/history.py` | 4 | 4 | 3 | 4 | 3 | 4 | 3 | **3.60** | 84-line `build_history` (kept, D-2-7) |
| `_dpd_journey/logging.py` | 4 | 4 | 4 | 5 | 4 | 4 | 4 | **4.14** | — |
| `_dpd_journey/spark.py` | 3 | 4 | 3 | 4 | 3 | 5 | 3 | **3.52** | UDF closures without contracts (R3-3); Python UDFs are the parity design |
| `_dpd_journey/states.py` | 4 | 4 | 4 | 4 | 3 | 4 | 4 | **3.86** | — |
| `a1_ability/classify.py` | 4 | 4 | 4 | 5 | 5 | 4 | 3 | **4.18** | bare `4` / `2` (R3-2); `build_a1_ability` ~65 lines (A1, D-2-2) |
| `a1_ability/signals.py` | 4 | 4 | 4 | 4 | 4 | 5 | 3 | **4.00** | long builders (A1, D-2-2); `lookback_floor` (D-2-5) |
| A1 `pipeline.py` + CC / RL A1 wrappers | 4 | 4 | 4 | 5 | 4 | 5 | 4 | **4.24** | — |
| `a2_locatability/signals.py` | 4 | 4 | 4 | 4 | 5 | 5 | 4 | **4.24** | reachable rule inline (R3-4) |
| `a2_locatability/classify.py`, `pipeline.py`, A2 wrappers | 4 | 4 | 4 | 4–5 | 4 | 5 | 4 | **4.10–4.24** | — |
| `cc_a4_deterioration/nodes.py` | 5 | 4 | 4 | 4 | 4 | 5 | 4 | **4.28** | — |
| `rl_a4_deterioration/nodes.py`, `chains.py` | 4 | 4 | 4 | 4 | 4 | 5 | 3 | **4.00** | generator unpack, two disables (R3-5 part) |
| A4 `pipeline.py` (CC, RL) | 4 | 4 | 4 | 5 | 4 | 5 | 4 | **4.24** | — |
| `cc_full_history`, `rl_full_history` | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | — |
| `catalog_crx.yml`, `pipeline_registry.py` (crx part) | 4 | 4 | 4 | 4 | 4 | 5 | 4 | **4.10** | — |

Changes since round 1: O2 on `a1_ability/signals.py` and `a2_locatability/signals.py` 3 → 4 (bundle 14 is
applied and is the branch base; A2 is signed off, so no workplace edits are pending on either file);
`a2 signals` O1 3 → 4 (N-3); `cc_a4` O1 3 → 5 (S2-06); `spark.py` O6 4 → 5, O7 2 → 3; `__init__` O7 2 → 4.

Per criterion, line-weighted over tier L (4,058 lines scored): **O1 3.94 · O2 4.02 · O3 3.87 · O4 4.35 ·
O5 4.08 · O6 4.77 · O7 3.60.** Weighted 4.07. No file below 3 on O1, O2 or O3.

## Convergence (PLAN §5 + my sign-off criteria)

| Criterion | Status |
|---|---|
| Gates green, golden identical | **met** |
| No open blocking objection | **met after D-2-3** (R-E's only blocking item waived; R-I none) |
| R-O ≥ 4 on every criterion | **not met**: O1 3.94, O3 3.87, O7 3.60 |
| R-E and R-I average ≥ 3.5 | R-I 3.95 **met**; R-E: changed files ≈ 3.5 (its 14 rows average 3.52), unchanged files keep its round 1 scores (file average ≈ 3.3), so the tier average is below 3.5: **not met** |
| No new revise items | **met** (0 revise; triage #6 is an unfinished round 1 item, not a new revise) |
| Questions all in `questions.md`, none in code | **met** |
| Bundle plan (§8) complete for bundles 2–4 | **not yet** (Master, round 3) |

**What round 3 can and cannot lift.** O3 reaches 4 with R3-3 and R3-2 (`spark.py`, A1 thresholds). O1
and O7 cannot reach 4 inside the rules we set: O1 is held by `spark.py`'s Python UDFs (the A4 parity
engine, signed off) and O7 by the A1 builders (D-2-2, no polish of a moving axis) and the A4 engine
functions (R-4). Splitting them would buy my score at the cost of bundle risk on signed-off or moving
code, which my own tie-break ranks higher. I will therefore sign off in round 3 with these two recorded
exceptions, provided O3 ≥ 4, R-E's tier average ≥ 3.5 after its round 3 rescoring of the touched files,
and the bundle plan is complete. Round 3 is **not** cut to sign-off only: the R3 items are small, but
two of them (the silent FORCE default, the bare A1 thresholds) are audit defects in shared or
scored code, and the bundle plan is a sign-off condition.

## A3 handoff

No new handoff item this round. `a3_target_shape.md` §5: name the three points maps
(`COMMITMENT_POINTS`, `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS`) and use `DISPLAY_NAMES` for the label
map (R3-2, text). S1's target shape: O5 **5** now (checked anchor and `start=`, `SEG_*` keys, inclusive
`_in_episode`, `Scorecard` in place).
