# R-I review, round 3 (delta, Interpretability advocate)

Rubric `rubrics/interpretability.md` (frozen). Read: round 3 diff `d79a5be..aed15fd` (src, checks),
the `a3_target_shape.md` diff, triage, R-O round 2, decisions (D-2-7), S4 log, gates, BUNDLE_PLAN, my
round 2 review. Not read: other round 3 reviews.

## 1. Round 3 items

| Item | Verdict | Note |
|---|---|---|
| R3-1 mode lookup + rung names (`scoring_engine.py:16,74-88`) | **Met** (the `score` split was dropped by R-O, D-2-7) | `{**moved, FORCE: to}[o.mode]` raises `KeyError` on a typo, pinned by a spec row. `LOW, MOD, HIGH = range(len(RUNGS))` replaces the digits. Nit, non-blocking: `MOD` vs `MODERATE_FROM` spell the same word two ways. |
| R3-2 `HIGH_FROM, MODERATE_FROM` + `labels` comment (`a1_ability/classify.py:40,138-141`) | **Met** | Thresholds are named, SCORECARD uses them, same names as the A3 sketch (I7). The spec cites `s_high` / `s_mod` on the constant line. |
| R3-2 A3 text (points maps, `DISPLAY_NAMES`, Dim A/B/C) | **Met** | `COMMITMENT_POINTS`, `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS` carry their D-A3-16 rows; `labels=DISPLAY_NAMES`. |
| R3-3 `spark.py` stage-order lines + `_udf` contracts | **Met (minimum)** | Both `build_*` first lines give the stage; both closures say columns in / struct out. The functions stay ~90 lines (R-4, A4 parity design); I accept that. |
| R3-4 `_reachable(w_start)` (`a2_locatability/signals.py:211`) | **Met**; `_last_call_days` dropped by R-O | D-A2-7 rule now has a name beside `_gone_dark`; `reachability_state` reads as two named rules. |
| R3-5 generator unpack | **Met**; bucket import and `_rows_before_chain` dropped by R-O | Plain lines in `_original_loan_months`. |
| R3-6 `anchor.py:41` comment | **Met** | Reads correctly now. |
| R3-7 `string_key` site check | **Met** in `BUNDLE_PLAN.md` (check 4, `RF STRING KEYS`). |
| N-R2-4 (R-E) join-order comment | Seen, accurate. |

No stale docstring, no literal introduced, no output column lost or renamed.

## 2. Tier-L average on the final tree

Files touched in round 3 rescored; the rest keep their round 2 (changed) or round 1 (unchanged) scores.

| File | Wtd | Change |
|---|---|---|
| `scoring_engine.py` | 4.08 | was 3.94; I2 3 -> 4 (rung names, no silent default); `score` still 45 lines (I3 3) |
| `_dpd_journey/spark.py` | 3.24 | was 3.12; contracts raise I4; still my lowest file (I3 3) |
| `a1_ability/classify.py` | 4.30 | was 4.08; I2 4 -> 5 |
| `a2_locatability/signals.py` | 4.12 | unchanged in score; `build_dcore_signals` still ~70 lines (I3 3), `_reachable` fixes the I1 gap |
| `rl_a4_deterioration/nodes.py` | 3.76 | was 3.60; I3 3 -> 4 |
| `_dpd_journey/anchor.py` | 4.62 | unchanged score, comment fixed |

18 files changed since round 1 average 3.99; 11 unchanged files (round 1 scores) average 3.99.
**Tier-L average over all 29 scored files: 3.99** (round 2: 3.95 on 18; round 1: 3.86 on 25). Target
3.5 met. Lowest: `spark.py` 3.24, `history.py` 3.12 (unchanged since round 1, tier-A parity code, signed off).

## 3. Open blocking objections

**None.** Items of mine still open are non-blocking and recorded: A1 / A4 print no rule column
(Q-26, answered (b), goes in the A1 redesign bundle), `score` and `build_*` length (mechanism, R-E won),
`MOD` spelling.

## 4. BUNDLE_PLAN.md

Traceable enough: one bundle, per-axis zero-difference checks, renamed and removed symbols listed with
pointers to the per-round logs, tags, log and error-text changes called out, and the `string_key` site
check is a PROD block. One request for the bundle notes: list `LOW`, `MOD`, `HIGH`, `HIGH_FROM`,
`MODERATE_FROM` and `_reachable` as new symbols (round 3 log has them), so the auditor sees them.
