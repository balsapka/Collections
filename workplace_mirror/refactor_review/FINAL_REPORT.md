# crx_persona council refactor: final report

Branch `refactor/persona_review`. Baseline `33fcc07` → code `aed15fd` (docs `5986193`). Three rounds.
**Outcome: signed off with recorded exceptions** (R-O, D-3-3). Outputs identical on all 14 tier-L pipelines
(golden, 79 datasets); all 32 questions answered by the user; nothing in this tree changes behaviour.

## 1. Metrics (`checks/refactor_metrics.py`)

| Tier L | Baseline | Round 1 | Round 2 | Final |
|---|---|---|---|---|
| Lines | 3,893 | 4,119 | 4,087 | **4,097** |
| Functions > 40 lines | 18 | 22 | 20 | **20** |
| Spark actions | 11 | 9 | 9 | **9** |
| Ruff findings | 178 | 134 | 69 | **69** |
| Pylint (line-weighted) | 9.98 | 9.98 | 9.98 | **9.99** |
| Docstring + comment share | 23% | 23% | 23% | **23%** |

| Other tiers | Baseline | Final | Note |
|---|---|---|---|
| D (dead) | 12 files, 7,028 lines, 47 actions, 135 ruff | **0** | deleted (S7) |
| K (kept, other owners) | 1,482 lines | 1,568 | `build_rl_depart_spine` moved into `rl_a4_spine` unchanged |
| A (A3, handoff only) | 4,192 | 4,192 | untouched |
| X (read only) | 723 | 723 | untouched |

Tier L is +204 lines (+5%): A3 design-in (`anchor.py`, `window_agg(start=)`, Scorecard modes), fail-loud
contracts and named rules. The longest functions shrank: `build_dpd_sequences` 122 → 83, `build_deterioration`
109 → 78, `build_dcore_signals` 94 → 69, `build_a1_ability` 76 → 61, `assign_state` 69 → 44, `build_history` 97 → 84.
The count over 40 rose by two: four functions crossed 40 (42–54 lines, mostly from `require_columns` contracts and `Scorecard.score`), two left the list.

Reviewer averages: **R-O** weighted 3.94 → 4.07 → **4.12** (final O1 3.94 · O2 4.03 · O3 4.14 · O4 4.36 · O5 4.08 ·
O6 4.77 · O7 3.69). **R-I** 3.86 → 3.95 → **3.99**. **R-E** ≈ 3.3 (round 2, R-O estimate) → **3.41**.

## 2. Change log by theme (R-O weighted score; R-E / R-I where they differed)

| Theme | What changed | Score |
|---|---|---|
| Dead code (S7) | 12 tier-D files deleted, 4 registry + 20 catalog entries, 3 dead tier-L symbols | accept (D-1-1) |
| Shared layer (S1) | `segment` / `SEG_*`, `string_key`, `window_start`, `window_agg(start=)`, `dcore_account_events`, one state logger (A4 on `log_latest_month`), `episode_start` + left-censored flag, `GONE_DARK_DAYS`; `_common` no longer imports the A4 engine | 4.0 – 4.7 |
| One scoring engine (S1-R2-01/02, R3-1/2) | `Scorecard` / `Dimension` / `Override` replace `StateLadder` for A1 and A3; A1 `FAMILIES`, `HIGH_FROM` / `MODERATE_FROM`; a bad override mode raises | 4.1 – 4.4 (R-E blocking waived, D-2-3) |
| Contracts and Kedro (S3) | dict `inputs` everywhere, `require_columns` on spines / sources / A4 history, `crx_persona` required, one tag set (Q-15), raw read documented (Q-16) | 4.0 – 4.5 |
| PROD cost (S2) | scoped `pit_latest` as one aggregate, one join per A1 source, A2 DCORE window removed (Exchange 7 → 7, Window 1 → 0), CC restructure flag as one aggregate, RL A4 without `collect`, distress floor pruning, liquidity floor from `crx_persona` (Q-14) | 3.9 – 4.6 |
| Readability (S4) | A1 thresholds and labels named with spec cells, A2 / A1 splits, `__all__` → `noqa` (`_dpd_journey/__init__` 85 → 61), A4 helper steps, `_reachable` | 3.5 – 4.4 (R3-4: R-E 3.0, R-I met) |
| Docstrings (S5) | ticket history removed; docstrings say what the code does now | accept |

## 3. Disputes and rulings (R-O)

- R-1: `episode_start` and `window_agg(start=)` stay in the shared layer now (R-E wanted them in the A3 bundle).
- R-2 / S4-02: `__all__` replaced by a file-level F401 ignore (R-E won).
- R-3 / S3-01: dict inputs kept; R-E's blocking 4 waived (rename-safe beats line count).
- R-4 / D-1-9, D-1-10: `spark.py` and A4 wrapper splits only in part (A4 parity code).
- R-5 / D-1-11: CC restructure flag back as `_restructure_blind_spot`, tie rule written once.
- R-10: A1 source labels named (R-I) over inline (R-E). R-12: `_RESTRUCTURE_DLQ_THRESHOLD` stays in CC A4.
- D-2-3: full `Scorecard` kept (CAP, FORCE, High gate) for the A1 redesign and A3; R-E's blocking 3 waived.
- D-2-4: `black -C` only in files a bundle changes anyway, never A1 before its redesign.
- D-2-5: `lookback_floor` → `crx_persona` floor moves to the A1 redesign bundle.
- D-2-6: `F.forall` kept; UAT step prints `pyspark.__version__`.
- D-2-7: round 3 limited to six small items; `score` split and `build_history` split dropped.
- D-3-1: `_reachable` kept although one line over its item budget (black blank line; R-I over R-E: rule line).

## 4. Dropped proposals (logged, not proposed again)

S4-08 (duplicate of S1-04) · S4-03 `_history_udf` / `_classify_udf` and type hints · S4-09 CC half (superseded by
S2-06) · R-E N-8 `persona_tags()`, N-10 name-match lists · R-E: move S1-07/08 to the A3 bundle · R-I N-9 threshold
move · R-I N-2 four-way `build_a1_ability` split · R-E inline `_latest_evidence` / `_shift_cycle_bills` · R-I R3-1
`score` split · R-I `_last_call_days`, bucket import, `_rows_before_chain` · R-I N-15 `build_history` split ·
R-I N-10 / N-11, R-E N-11 · R-E N-R2-2 (waived) · R-E N-R2-3 (recheck in the A3 bundle).

## 5. Questions (Q-01 … Q-32, all answered: recommendation accepted, user 2026-11-05)

| Goes to | Questions |
|---|---|
| A4 fix bundle | Q-01, Q-03, Q-04, Q-05 (with the persona master) |
| Shared fix bundle | Q-02 |
| A3 bundle | Q-11, Q-12, Q-13, Q-20, Q-22 / Q-27, Q-25, Q-28 … Q-32 |
| A1 redesign bundle | Q-26 rule column (designed with A3's) |
| Applied in this refactor (no behaviour change) | Q-14, Q-15, Q-16, Q-18, Q-21 (`string_key` sites checked in PROD) |
| Spec text or no action | Q-06, Q-07, Q-08, Q-09, Q-10, Q-17, Q-19, Q-24 |
| Workplace catalog check | Q-23 (`crx_cc_billing`, the smoke baseline failure) |

## 6. Bundle plan (`BUNDLE_PLAN.md`, accepted D-3-2)

- **R-A `refactor_dead_code`**: S7 deletions + the moved RL spine function; PROD: `kedro registry list`,
  `crx_rl_a4_spine` rerun with `exceptAll` = 0; HDFS cleanup of 17 datasets.
- **R-B `persona_refactor`** on R-A: all tier-L changes; one 0-diff RF check per axis (A4 → A2 → A1), plus DCORE
  spill (N-3), key / broadcast size (N-4) and `RF STRING KEYS`; step 8 only after all show 0 differing rows.
- Conditions (R-O): pin `98e0338` to a branch (C1); rollback = revert the whole R-B apply (C2); `RF KEYS` also on
  `cc_180_plus` (C3); whichever of R-B / A1 redesign / A3 lands second rebases and re-runs gates; confirm the bundle
  13 cleanup first (C4). Fix `a3_handoff.md` lines 11-12 (`StateLadder` → `Scorecard`).
- Later: A1 redesign bundle (D-2-5, D-2-3 check, Q-26); A4 and shared fix bundles; A3 bundle.

## 7. A3 and A1 design-in

- `a3_target_shape.md`: the `a3_credibility/` engine + CC / RL wrappers on the obs base, `episode_start`,
  shared DCORE window, `Scorecard` declaration with `COMMITMENT_POINTS`, `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS`,
  `HIGH_FROM` / `MODERATE_FROM`, `DISPLAY_NAMES` (O5 = 5).
- `a3_handoff.md`: diff-level items for the A3 session (A3 files unchanged since `d1ad38a`).
- `a1_design_in.md`: what the A1 redesign gets from `Scorecard` (High gate, CAP / negative points for distress).

## 8. Open items and exceptions

| # | Exception | Clears when |
|---|---|---|
| E1 | R-O O1 3.94: A4 per-row Python UDFs (parity engine) | A4 fix bundle scored with the frozen rubric; meanwhile R-B logs A4 stage run time |
| E2 | R-O O7 3.69: A1 builders frozen (D-2-2), A4 engine functions and `score` whole (R-4, D-2-7) | A1 redesign bundle, then the A4 fix bundle and the D-2-3 check |
| E3 | R-E 3.41 < 3.5: A3 design-in and Scorecard modes without callers yet | A3 bundle and A1 redesign bundle (D-2-3, D-2-5); R-E re-scores at the post-A3 pass |
| E4 | Smoke at its baseline failure (`crx_cc_billing`) | Q-23 workplace catalog check, CC A3 standalone run |

Open, not exceptions: bundle build conditions C1–C4; bundle 14 cleanup in the workplace; the `a3_handoff.md`
header fix; R-I's `MOD` / `MODERATE_FROM` spelling nit (A3 bundle may align it).
