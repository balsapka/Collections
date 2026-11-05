# R-O review, round 3 (Owner): final review and sign-off

Frozen rubric `rubrics/owner.md`, its sign-off criteria, and the round 3 conditions in `round_2/triage.md`.
Code tree `aed15fd`; docs HEAD `5986193`. Diff `git diff 7ae2a08 aed15fd -- src checks`: 7 files, +32 / −17.
Read: triage, my round 2 review, decisions D-1-* / D-2-*, S4 round 3 log, gates, R-E (3.41) and R-I (3.99)
round 3, `BUNDLE_PLAN.md`, `questions.md` (32 answered), baseline / round 1 metrics, and current metrics
(`refactor_metrics.py`; round 2 recomputed from `git archive 7ae2a08`).

Criteria: O1 PROD operability 18 · O2 change risk 18 · O3 auditability 16 · O4 one engine 14 · O5 fits A3 14 ·
O6 contracts 10 · O7 clarity per line 10.

## Summary

- Gates on `aed15fd`: golden identical (79 datasets), A1 69/69 (+ bad-mode row), A2 36/36, A4 chain pass,
  ruff tier L 69, pylint 9.99, no new Spark action (9). Smoke: the baseline failure only (`crx_cc_billing`, Q-23).
- Round 3: **6 keep, 0 revise, 0 revert.** No blocking objection from any reviewer.
- My final scores: **O1 3.94 · O2 4.03 · O3 4.14 · O4 4.36 · O5 4.08 · O6 4.77 · O7 3.69** (weighted 4.12).
- Bundle plan: **two bundles accepted** in place of my four-bundle sketch, with four build conditions.
- **Signed off with recorded exceptions** (E1 O1, E2 O7, E3 R-E 3.41, E4 smoke baseline failure). D-3-1 … D-3-7.

## 1. Round 3 items

| Item | Verdict | R-O wtd | Note |
|---|---|---|---|
| R3-1 `scoring_engine`: `LOW, MOD, HIGH`; `{**moved, FORCE: to}[o.mode]` | **keep** | 4.4 | The silent FORCE on a typo is gone: a bad mode raises `KeyError` while the node builds its plan, before any Spark job, pinned by a spec row. R-I's `MOD` / `MODERATE_FROM` spelling nit: no change (a shared-engine hunk for a cosmetic gain); the A3 bundle may align it if it touches the file. |
| R3-2 A1 `HIGH_FROM, MODERATE_FROM = 4, 2` + `labels` comment | **keep** | 4.3 | Closes round 1 triage #6. The constant line names the spec cells `s_high` / `s_mod`; same names in the A3 sketch. |
| R3-3 `**signals` join-order comment | **keep** | — | True (left joins on `GRAIN`, distinct columns). |
| R3-4 A2 `_reachable(w_start)` | **keep** | 4.4 | +4 against an item budget of ≤ +3. The extra line is a blank line that black requires between top-level functions; round 3 total is +10, at budget. Dropping it would leave the D-A2-7 rule inline beside the named `_gone_dark`. Ruling D-3-1. |
| R3-5 `spark.py` stage-order lines, `_udf` contracts | **keep** | 3.7 | `spark.py` O3 3 → 4. The functions stay 83 / 78 lines (R-4, A4 parity). |
| R3-6 RL generator unpack → plain lines; `anchor.py` comment | **keep** | 4.1 | −1 line. Five plain lines instead of the "two" the triage named: same net, clearer. |

**R-E vs R-I in round 3.** One difference: R3-4 (R-E 3.0 "single-caller predicate"; R-I "met"). Ruling: R-I,
because the line encodes a signed-off business rule (D-A2-7) and my tie-break puts spec traceability above
brevity; neither reviewer blocks. All other items: both accept.

## 2. Final criterion scores

Line-weighted over tier L (4,097 lines). Files not listed keep their round 2 row.

| File | Round 2 → 3 change | Wtd |
|---|---|---|
| `scoring_engine.py` | O3 4 → 5 (no silent default, named rungs, spec row); O7 3 (`score` 42 lines) | 4.44 |
| `a1_ability/classify.py` | O3 4 → 5 (thresholds named with spec cells) | 4.34 |
| `_dpd_journey/spark.py` | O3 3 → 4 (stage order, closure contracts); O1 3, O7 3 unchanged | 3.68 |
| `a2_locatability/signals.py` | O3 4 → 5 (both reachability rules named) | 4.40 |
| `rl_a4_deterioration/nodes.py`, `chains.py` | O7 3 → 4 (plain unpack) | 4.10 |
| `_dpd_journey/anchor.py` | O3 4 → 5 (arithmetic comment right) | 4.40 |

| | O1 | O2 | O3 | O4 | O5 | O6 | O7 | Wtd |
|---|---|---|---|---|---|---|---|---|
| Round 1 | 3.8 | 3.8 | 3.7 | 4.1 | 4.1 | 4.9 | 3.2 | 3.94 |
| Round 2 | 3.94 | 4.02 | 3.87 | 4.35 | 4.08 | 4.77 | 3.60 | 4.07 |
| **Final** | **3.94** | **4.03** | **4.14** | **4.36** | **4.08** | **4.77** | **3.69** | **4.12** |

No tier-L file below 3 on O1, O2 or O3 (lowest: `spark.py` O1 3, `history.py` O3 3).
What holds O1: `spark.py`'s per-row Python UDFs (A4 parity engine, signed off), the only O1 3 file; at 4 it
alone would lift O1 to 4.02. What holds O7: A1 builders (432 + 205 lines at 3, D-2-2), A4 engine functions
(`spark.py`, `history.py`, R-4 / D-2-7), `Scorecard.score` (42 lines, D-2-7).

## 3. Ruling on `BUNDLE_PLAN.md`: two bundles accepted

My sketch had four bundles so that each PROD check isolated one axis. The Master's couplings are real:
A1 `classify` is on `Scorecard` (no `StateLadder` left), `_common` no longer imports `_dpd_journey` (the
dependency is reversed), and A2 imports the shared window / DCORE helpers whose private copies are gone.
Four bundles would ship three trees the golden harness never ran, or need shims. My own tie-break ranks
"the tree that was tested" above "the smaller diff", and per-axis isolation survives as one 0-diff RF check
per axis, run A4 → A2 → A1. The plan lists base, slug, excludes, signatures, renamed / removed / new symbols
(R-I's request is in), log / error / tag changes, and the cleanup. That meets my criterion. **Accepted (D-3-2)**,
with four conditions for the build (none needs a code change):

- **C1 Pin the S7 commit.** `98e0338` is on no branch (reflog only). Before anything else, the Master points a
  named ref at it (e.g. branch `refactor/s7_dead_code`); reflog expiry would lose bundle R-A's source.
- **C2 Rollback is whole-bundle.** One RF check failing means `git revert` of the R-B apply commit in the
  workplace, not a per-axis patch; step 8 (real outputs) runs only after all three RF checks show 0 differing
  rows. Write that line into the bundle's run steps.
- **C3 Measure N-4 where it is largest.** The broadcast / key-count block (`RF KEYS`) also runs on
  `cc_180_plus` (the largest obs base); the 60–180 model_ids alone do not bound the broadcast risk. The 180+
  outputs are covered by the golden harness locally; in PROD they get step 8 directly, as planned.
- **C4 Order against the other sessions.** R-B and the A1 redesign bundle both edit `a1_ability/`; R-B and the
  A3 bundle both depend on `scoring_engine` / `_common`. Whichever lands second is rebased on the first and re-runs
  every gate (PLAN §8). Confirm the bundle 13 cleanup state with the user before building R-A (the plan asks).

Doc fix for the Master before the A3 handoff: `a3_handoff.md` lines 11-12 still list
`scoring_engine.StateLadder` as importable. The status table (line 26) is right; the header is not. A3 files
are unchanged since `d1ad38a`, so the diffs still apply.

## 4. Sign-off

| Criterion (rubric + round 2 triage) | Status |
|---|---|
| Gates green, golden identical on every tier-L pipeline | **met** (smoke: baseline failure only, E4) |
| No open blocking objection | **met** (R-E: none, S1-R2-01 waived by D-2-3; R-I: none) |
| R-O O3 ≥ 4; O2, O4, O5, O6 ≥ 4 | **met** (4.14; 4.03, 4.36, 4.08, 4.77) |
| R-O O1, O7 ≥ 4 | **not met**: recorded exceptions E1, E2 (anticipated in D-2-8) |
| No tier-L file below 3 on O1, O2, O3 | **met** |
| R-I average ≥ 3.5 | **met** (3.99) |
| R-E average ≥ 3.5 | **not met**: 3.41, recorded exception E3; R-E does not object |
| No new revise items | **met** |
| Behaviour findings only in `questions.md`, all answered | **met** (Q-01 … Q-32; none applied in code) |
| Bundle plan complete | **met** (two-bundle plan, D-3-2; build conditions C1–C4) |
| A3 target shape O5 ≥ 4; `a3_handoff.md` diff-level | **met** (O5 5; header fix above) |

**Decision: signed off with recorded exceptions** (D-3-3).

| # | Exception | Reason (one line) | Clears when |
|---|---|---|---|
| E1 | O1 3.94 < 4 | `spark.py` runs A4 as per-row Python UDFs, the parity engine signed off with A4; rewriting it is bundle risk on signed-off code. | The A4 fix bundle (Q-01, Q-05 touch Stage 2) is scored with the frozen rubric and `spark.py` reaches O1 4; until then the R-B A4 check logs the A4 stage run time per model_id as evidence the cost is unchanged. |
| E2 | O7 3.69 < 4 | A1 builders are frozen until the A1 redesign (D-2-2); A4 engine functions and `Scorecard.score` stay whole (R-4, D-2-7). | The A1 redesign bundle (A1 files to O7 4 lifts O7 to ~3.85), then the A4 fix bundle (`spark.py`, `history.py`) and the D-2-3 check (`score` shrinks if CAP / FORCE / the High gate go). |
| E3 | R-E 3.41 < 3.5 | Structural: tier L is +204 lines over baseline for A3 design-in (`anchor.py`, `window_agg(start=)`, Scorecard modes only A3 / the A1 redesign use) and fail-loud contracts; R-E does not object. | The A3 bundle (first callers of `episode_start`, `start=`, CAP) and the A1 redesign bundle (D-2-3: remove unused modes; D-2-5: delete `lookback_floor`); R-E re-scores at the post-A3 check pass (PLAN §8). |
| E4 | Smoke gate at its baseline failure | `crx_cc_billing` has no catalog entry (Q-23), present at baseline, not a regression. | The workplace catalog check for Q-23 and a CC A3 standalone run. |

What I answer for in audit: outputs identical on every tier-L pipeline (golden), every behaviour finding with
the user and answered, every rule named next to its spec cell, one shared layer A3 can build on, and a ship
plan whose PROD checks expect zero differing rows.
