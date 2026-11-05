# R-E review, round 3 (efficiency engineer, delta only)

Frozen rubric `rubrics/efficiency.md`. Diff `d79a5be..aed15fd` (src, checks): 7 files, +32/-17, tier L net +10 (4,097).
Read: triage, R-O round 2, D-2-3..8, S4 round 3, gates, BUNDLE_PLAN, my round 2 review. Other round 3 reviews not read.

## 1. Items

R3-1 named rungs `LOW, MOD, HIGH`, mode lookup raises on a mistyped mode: **accept** (blocking: no)  E3, E6
  `{**moved, FORCE: to}[o.mode]` is the right size: +0 lines, replaces `.get(..., to)` (which hid a typo as FORCE),
  and the spec row proves it. One line of constants, zero new concepts. Score 4.0.
R3-2 `HIGH_FROM`, `MODERATE_FROM` + identity-labels comment: **accept**  E6
  +2 lines for two named literals the spec calls `s_high` / `s_mod`; the comment on the identity `labels` map is
  a real "why". Score 3.5 (named constants used once each; E3 stays 3).
R3-3 / N-R2-4 join-order comment: **accept**  E6
  One line that saves a reader a check. Score 3.5.
R3-4 `_reachable(w_start)`: **accept**  E3
  Single-caller one-line predicate, +4 lines: E3 2. It names a signed-off rule and sits beside `_gone_dark`; same
  reasoning as the R-O ruling D-2-7. Score 3.0 (not blocking).
R3-5 stage-order docstring lines, UDF contract comments: **accept**  E6
  +3 lines of interface text that the closures lacked; no code. Score 3.3.
R3-6 `_original_loan_months` plain lines; anchor comment reworded: **accept**  E1, E3
  -1 line, a generator-over-tuple unpack replaced by four statements: fewer concepts for the same count. The
  anchor comment is now shorter and clearer. Score 4.0.

No new Spark action, no extra pass, no shuffle change (gates: golden 79/79 identical, specs green, smoke baseline).

## 2. Tier-L average (final tree)

Per-file weighted scores (rubric weights), round 2 values for untouched files:
`_common` 4.0 · `scoring_engine` 3.3 (was 3.25; rung names, raising lookup) · `_dpd_journey/__init__` 3.7 ·
`_dates` 3.3 · `anchor` 3.15 · `constants` 3.4 · `history` 3.1 · `logging` 4.1 · `params` 3.5 ·
`spark` 3.4 · `states` 2.9 · `a1 signals` 3.0 · `a1 classify` 3.8 · `a1` pipelines 3.4 / wrappers 3.2 ·
`a2 signals` 4.1 (was 4.15; single-caller predicate) · `a2 classify` 3.65 · `a2 pipeline` 3.0 ·
`cc_a4 nodes` 3.6 / pipeline 3.4 · `rl_a4 nodes` 3.6 (was 3.55) / pipeline 3.4 / `__init__` 2.95 ·
full-history modules 3.4 x2 · `obs_base/pipeline` 3.0.

**Tier-L average: 3.41** (25 scored units, simple mean). Changed files this round average 3.57; only seven files
moved and by at most 0.05 each, so the average is about 3.4 and **does not reach 3.5**.
I will not round it up. The gap is structural, not a round 3 defect: tier L is still +204 lines over baseline
(4,097 vs 3,893) for code the A3 bundle consumes (`anchor.py`, the `Scorecard` unused modes, shared layer).
That gap closes at the A3 bundle, as recorded under Axis stability. If R-O needs 3.5 from me, the honest
route is the recorded exception, not a rescore. For R-O's decision: I do not object to sign-off at 3.41 given
the cause.

## 3. Blocking objections

None. S1-R2-01 was waived by D-2-3 and I record my objection without asking for a revert. No round 3 item
adds a blocking issue.

## 4. BUNDLE_PLAN.md

Two bundles (deletions first, then one refactor bundle) is the leanest ship I can see: it avoids a
compatibility shim between a Scorecard A1 and a StateLadder engine. Fine from my angle.

Note: the Round 3 line cost (+10) is at budget; the lines I would still remove first, in the A1 redesign or A3
bundle, are `lookback_floor` (D-2-5), unused CAP/FORCE/High-gate modes (D-2-3), and `anchor.py` if no A3 caller lands.
