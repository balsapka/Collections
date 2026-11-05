# Round 1 merge log

Input `d1ad38a` (worktree `refactor/persona_review`, HEAD before merge `43bd75b`). Merged in the
PLAN order S7 → S1 → S3 → S2 → S4, one local commit per stage, then two revert commits after
gate 2, squashed into the round commit (pre-squash stage commits, local only: S7 `98e0338`, S1 `420d366`, S3 `fdb130a`, S2 `f5276c2`, S4 `f6fc230`, reverts `9f1aeca`, `3d0c4a5`). S5 (docstrings) has not run yet. Master decisions:
`../decisions.md` D-1-1 … D-1-5; merge-time skips and reverts D-1-6 … D-1-12.

Re-basing method: each proposal's diff was replayed on a scratch worktree at `d1ad38a` (in the
specialist's order) to get exact per-proposal diffs, then applied to the merged tree with
`git apply -3`. Conflicts were resolved keeping the earlier stage and carrying the later
proposal's intent onto it, with no new content beyond what the two proposals already wrote.

## Counts

| | Applied as written | Re-based | Held | Skipped | Reverted |
|---|---|---|---|---|---|
| S7 (1 patch + delete list) | 1 | – | – | – | – |
| S1 (8) | 4 (02, 04, 05, 06 via the combined diff) | 4 (01, 03, 07, 08: conflicts with S7) | – | – | – |
| S3 (7) | 4 (01, 02, 05, 07) | 2 (03, 06) | 1 (04) | – | – |
| S2 (7) | 2 (05, 07) | 4 (01, 02, 03, 04) | – | – | 1 (06) |
| S4 (11) | 4 (06, 07, 11, 02*) | 4 (01, 04 part, 05, 10) | – | 1 (08) | 2 (03, 09) |
| **Total (34)** | **15** | **14** | **1** | **1** | **3** |

Applied in the tree: 29 proposals (15 + 14). *S4-02 needed only conflict resolution in import
and comment lines (S1-01 import line, S1-06 comment kept).

## Per proposal

### S7 dead code
| Id | Status | Note |
|---|---|---|
| S7 patch | applied | `S7.patch` (8 files) + the 12-file delete list (7,028 lines of tier D). `build_rl_depart_spine` moved byte-identical into the new `rl_a4_spine/nodes.py` (checked with `diff`); `rl_a4_spine/pipeline.py` repointed. Dead tier-L symbols removed: `_common.parse_yyyymmdd`, `scoring_engine.priority_reason`, `_dpd_journey.SEGMENTS`. 20 catalog entries and 4 registry imports/entries removed. |

### S1 architecture (S1's combined diff, order 01, 03, 02, 04, 05, 06, 07, 08)
| Id | Status | Note |
|---|---|---|
| S1-01 segment map in `_common` | re-based | S7 had already deleted `SEGMENTS`; `constants.py` keeps only `BucketScheme`, `CC`, `RL`. |
| S1-03 `window_start` public | re-based | `_common` conflict with S7's `parse_yyyymmdd` removal; resolved without `parse_yyyymmdd`. |
| S1-02 `string_key` in `_common` | applied | |
| S1-04 `state_label` | applied | |
| S1-05 `dcore_account_events` | applied | |
| S1-06 one state logger | applied | PROD log text changes (below). |
| S1-07 `episode_start` | re-based | Master D-1-2. `__init__` import/layout lines re-based onto S7's `SEGMENTS` removal. |
| S1-08 `window_agg(start=)` | applied | Master D-1-2. |

### S3 conventions
| Id | Status | Note |
|---|---|---|
| S3-01 dict inputs obs base / full history | applied | |
| S3-02 dict inputs A4 | applied | |
| S3-03 `require_columns` on spine / sources | re-based | `rl_full_history/nodes.py` import block: S1-02 had removed the local `_string_key` and `types` import; now `from .._common import require_columns, string_key`. |
| S3-04 tag normalisation | **held** | Master D-1-3: waits for Q-15 [Q-S3-1]. |
| S3-05 `crx_persona` required on RL full history | applied | |
| S3-06 registry wrap | re-based | Same two wraps; the context line `crx_rl_departure_signature` was gone (S7). |
| S3-07 catalog comments | applied | |

### S2 performance
| Id | Status | Note |
|---|---|---|
| S2-01 `scoped` + `pit_latest` aggregate | re-based | Onto S1-03 (`window_start(months, anchor)`) and S1-08 (`window_agg(start=)`): `scoped()` wraps the source in both helpers; the `Window` import stays (S1-06's `log_latest_month` uses it). |
| S2-02 A1 one join per source | re-based | Diff hunk counts were off (`git apply --recount`). Output column order kept: `build_liquidity_signals` ends with a `.select(GRAIN, casa_m1…casa_m2W, ext_card_payment_max, casa_active, casa_held)` (Master D-1-4); `GRAIN` import restored for it. Income column order unchanged. |
| S2-03 A2 DCORE account-days | re-based | Onto S1-05: `_dcore_days(events)` now aggregates the rows of `_common.dcore_account_events` (already upper-cased and trimmed) instead of reading followup / agreements itself; `build_dcore_signals` keeps S1-01's `segment`. The single summary aggregate lists `dcore_deceased_date`, `last_skip_trace_date` first so the output column order matches the baseline (D-1-4). |
| S2-04 A2 scoped location / demographics / Way4 | re-based | Import block merged with S1's. |
| S2-05 distress floor pruning | applied | |
| S2-06 CC A4 restructure aggregate | **reverted** | Gate 2: its new comment line is 89 characters, `cc_a4_deterioration/nodes.py` ruff 9 → 10 (E501 at line 47 of the S2 stage). D-1-11. |
| S2-07 RL A4 no `collect` | applied | |

### S4 readability
| Id | Status | Note |
|---|---|---|
| S4-01 A1 threshold names | re-based | `label_column` → `scoring_engine.state_label` (Master D-1-5). Spec cells S2, S4, S10, S12 of `specs/A1_ability_spec.md` updated to the new names in the same commit (text only). |
| S4-02 `__all__`, `log_state_stats` public | applied | Conflicts in import and comment lines only: kept S1-01's `from .._common import MODEL_ID_SEGMENT` (minus the now-unneeded `pylint: disable=unused-import`) and S1-06's shorter comment; `__all__` drops `SEGMENTS` (S7) and `_string_key` (S1-02), adds `episode_start` (S1-07). |
| S4-03 split `spark.py` functions | **reverted** | Gate 2: the type-hint docstring added to `_dpd_journey/_dates.py::_month_col` is 89 characters, ruff 3 → 4. D-1-9. The re-based version (string_key, state_label) is in the pre-squash S4 stage commit `f6fc230` (local reflog only). |
| S4-04 A2 split | re-based (part) | Kept: `_latest_evidence`, `_location_rule`, `_cif_rows` (on S2-04's `scoped` join and S1-03's `window_start`). Dropped: the window-start part (Master D-1-5, S1-03 did it) and the DCORE split `_call_days` / `_last_call_days` (S2-03, an earlier stage, rewrote `build_dcore_signals` as one aggregate; the split's intent does not survive; D-1-7). |
| S4-05 A1 distress split | re-based | `_distress_events` takes `since` so S2-05's floor on bounces and returns is kept; `since = lookback_floor(...)` computed once, same action order. |
| S4-06 `assign_state` predicates | applied | |
| S4-07 `_shift_cycle_bills` | applied | |
| S4-08 `label_column` | **skipped** | Master D-1-5: duplicate of S1-04. |
| S4-09 A4 wrapper steps | **reverted** | Gate 2: `_original_loan_months` docstring line is 90 characters, `rl_a4_deterioration/nodes.py` ruff 5 → 6. D-1-10. (Its CC part had been re-based onto S2-06.) |
| S4-10 segment constants | re-based | `SEG_60_180` / `SEG_180_PLUS` live in `_common` (S1-01 made `_common` own the segment map; putting them in `_dpd_journey/constants.py` would bring back the import cycle). `params.py`, A2 `GONE_DARK_DAYS`, CC A1 anchor import them from `_common`. D-1-8. |
| S4-11 A2 `TAGS` | applied | |

## PROD log changes (list in the bundle notes)

- **S1-06, A4 state log** (`_dpd_journey/logging.py::log_state_stats`, called by CC and RL A4):
  the block is now written by `_common.log_latest_month(..., latest_per_account=True)`.
  - header `build_cc_deterioration [60_180]: total accounts (2026 August) = n` becomes the A1/A2
    format `a4_deterioration [cc_60_180] — det_state, month of 2026-08-31 (n=…)`;
  - rows are ordered by state name, not by count;
  - the logger name is `…crx_persona._common`, not `…_dpd_journey.logging`.
  The A4 check pipelines' own blocks do not change. Still one Spark action per call.
- **S1-06 / S4-02**: the function is now public `log_state_stats` (was `_log_state_stats`); no
  log text change from the rename.
- S7: the four tier-D pipelines (`crx_cc_payment_trajectory`, `crx_cc_utilisation_features`,
  `crx_cc_departure_signature`, `crx_rl_departure_signature`) no longer exist, so their logs go.
  The moved `build_rl_depart_spine` logs under the logger `…rl_a4_spine.nodes` instead of
  `…rl_departure_signature.nodes`; the message text is unchanged.

## Renamed and removed public symbols (for the workplace tests)

Paths under `crx_persona/`.

| Old | New / status | From |
|---|---|---|
| packages `cc_departure_signature`, `rl_departure_signature`, `cc_payment_trajectory`, `cc_utilisation`; modules `cc_a2_locatability.nodes`, `cc_a2_locatability.constants`, `rl_a2_locatability.nodes` | removed (tier D). Tests importing them are deleted | S7 |
| `rl_departure_signature.nodes.build_rl_depart_spine` | `rl_a4_spine.nodes.build_rl_depart_spine` (same name and signature) | S7 |
| `_common.parse_yyyymmdd`, `scoring_engine.priority_reason`, `_dpd_journey.SEGMENTS` (and `_dpd_journey.constants.SEGMENTS`) | removed | S7 |
| `_dpd_journey.constants.MODEL_ID_SEGMENT` | `_common.MODEL_ID_SEGMENT` (still importable as `_dpd_journey.MODEL_ID_SEGMENT`) | S1-01 |
| — | new `_common.segment(model_id)`; raises `ValueError` for an unknown model_id (was a bare `KeyError` in `window_months`, `gone_dark_days`, the CC A1 anchor) | S1-01 |
| — | new `_common.SEG_60_180`, `_common.SEG_180_PLUS` | S4-10 |
| `_common._window_start(anchor, months)` | `_common.window_start(months, anchor=None)` (argument order changed; anchor defaults to `observation_date`) | S1-03 |
| `a2_locatability.signals._window_start` | removed (use `_common.window_start`) | S1-03 |
| `_dpd_journey._string_key`, `_dpd_journey.spark._string_key`, `rl_full_history.nodes._string_key` | removed; `_common.string_key(df, col="account_id")` | S1-02 |
| `a2_locatability.signals._dcore_events` | removed; `_common.dcore_account_events(obs_base, followup, agreements)`; A2 adds private `_dcore_days(events)` (S2-03) | S1-05 |
| `a2_locatability.classify._label` | removed; `scoring_engine.state_label(col, labels)` (also used by A1 and A4) | S1-04 |
| `_common.log_latest_month(df, col, name, persona_end_date)` | new keyword-only `latest_per_account=False` | S1-06 |
| `_dpd_journey._log_state_stats` (also `_dpd_journey.logging._log_state_stats`) | `log_state_stats` (same signature); `_dpd_journey` now has `__all__` | S1-06, S4-02 |
| — | new `_dpd_journey.episode_start(obs_base, deterioration)` (`_dpd_journey/anchor.py`) | S1-07 |
| `_common.window_agg(...)` | new keyword `start=` (a base date column bounding the window from below) | S1-08 |
| `rl_full_history.nodes.build_rl_full_history(rl_spine, int_loan_master, crx_persona=None)` | `crx_persona` required (no default) | S3-05 |
| `a1_ability.classify`: `F_INC`, `K_INC`, `D_INC`, `F_CASA`, `K_CASA`, `D_CASA`, `F_PAY`, `K_PAY`, `DEMIN`, `MIN_MONTHS`, `INC_FLOORS` | `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`, `INCOME_MAX_FALL`, `CASA_FLOOR`, `CASA_ANCHOR_MULT`, `CASA_MAX_FALL`, `CARD_PAYMENT_FLOOR`, `CARD_PAYMENT_ANCHOR_MULT`, `MIN_EVIDENCE_AMT`, `CASA_MIN_MONTHS`, `STABLE_INCOME_FLOORS`; new `INCOME_POINTS`, `LIQUIDITY_POINTS`, `_shows_evidence`; `_not_weakening` flags now keyword-only (`missing_is_zero=`, `w=`) | S4-01 |
| `a1_ability.signals.build_distress_signals` nested `flag` | module-level `_flag`; new `_require_returns_from`, `_distress_events`, constants `BUREAU_BOUNCE`, `INTERNAL`, `BUREAU` | S4-05 |
| `a1_ability.signals._by_month(obs, series, value, prefix, months)` | `_by_month(value, prefix, months)` returns aggregate columns (private) | S2-02 |
| — | new `_common.scoped(src, base, key)` | S2-01 |
| — | new private A2 `_latest_evidence`, `_location_rule`, `_cif_rows`; `_dpd_journey.states._is_stabilized`, `_is_early_payment_default`; `_dpd_journey.history._shift_cycle_bills`; `a2_locatability.pipeline.TAGS` | S4-04, 06, 07, 11 |

No catalog dataset, HDFS path, pipeline name, parameter key or output column was renamed. Output
column order is as at baseline (golden harness).

## Net lines per file

From `python workplace_mirror/checks/refactor_metrics.py round_1/metrics` (`round_1/metrics/`),
against `00_baseline/metrics.json`. Files whose lines and scores did not change are left out
(e.g. the A4 and obs-base `pipeline.py` files, where S3-01/02 changed the input style in place).

| File | Tier | Lines before | Lines after | Net | pylint before → after | ruff before → after |
|---|---|---|---|---|---|---|
| `_common.py` | L | 215 | 303 | +88 | 10.0 → 10.0 | 4 → 4 |
| `_dpd_journey/__init__.py` | L | 85 | 128 | +43 | 10.0 → 10.0 | 58 → 17 |
| `_dpd_journey/anchor.py` | L | 0 | 52 | +52 | – → 10.0 | – → 0 |
| `_dpd_journey/constants.py` | L | 40 | 26 | -14 | 10.0 → 10.0 | 0 → 0 |
| `_dpd_journey/history.py` | L | 165 | 173 | +8 | 9.86 → 9.87 | 12 → 12 |
| `_dpd_journey/logging.py` | L | 100 | 71 | -29 | 10.0 → 10.0 | 1 → 0 |
| `_dpd_journey/params.py` | L | 79 | 77 | -2 | 10.0 → 10.0 | 11 → 10 |
| `_dpd_journey/spark.py` | L | 362 | 347 | -15 | 10.0 → 10.0 | 9 → 9 |
| `_dpd_journey/states.py` | L | 126 | 142 | +16 | 9.62 → 9.7 | 14 → 13 |
| `a1_ability/classify.py` | L | 198 | 210 | +12 | 10.0 → 10.0 | 2 → 2 |
| `a1_ability/signals.py` | L | 381 | 419 | +38 | 10.0 → 10.0 | 6 → 6 |
| `a2_locatability/classify.py` | L | 94 | 89 | -5 | 10.0 → 10.0 | 0 → 0 |
| `a2_locatability/pipeline.py` | L | 89 | 90 | +1 | 10.0 → 10.0 | 1 → 1 |
| `a2_locatability/signals.py` | L | 346 | 348 | +2 | 10.0 → 10.0 | 3 → 3 |
| `cc_a1_ability/nodes.py` | L | 55 | 54 | -1 | 10.0 → 10.0 | 1 → 1 |
| `cc_a2_locatability/constants.py` | D | 299 | 0 | -299 | 10.0 → – | 1 → – |
| `cc_a2_locatability/nodes.py` | D | 1320 | 0 | -1320 | 9.77 → – | 50 → – |
| `cc_a4_deterioration/nodes.py` | L | 81 | 88 | +7 | 10.0 → 10.0 | 9 → 9 |
| `cc_departure_signature/nodes.py` | D | 2375 | 0 | -2375 | 9.75 → – | 59 → – |
| `cc_departure_signature/pipeline.py` | D | 267 | 0 | -267 | 10.0 → – | 2 → – |
| `cc_full_history/nodes.py` | L | 60 | 66 | +6 | 10.0 → 10.0 | 12 → 12 |
| `cc_payment_trajectory/nodes.py` | D | 781 | 0 | -781 | 10.0 → – | 7 → – |
| `cc_payment_trajectory/pipeline.py` | D | 38 | 0 | -38 | 10.0 → – | 1 → – |
| `cc_utilisation/nodes.py` | D | 569 | 0 | -569 | 10.0 → – | 6 → – |
| `cc_utilisation/pipeline.py` | D | 41 | 0 | -41 | 10.0 → – | 0 → – |
| `rl_a2_locatability/nodes.py` | D | 214 | 0 | -214 | 10.0 → – | 2 → – |
| `rl_a4_deterioration/nodes.py` | L | 260 | 278 | +18 | 10.0 → 10.0 | 5 → 5 |
| `rl_a4_spine/nodes.py` | K | 0 | 89 | +89 | – → 10.0 | – → 1 |
| `rl_a4_spine/pipeline.py` | K | 39 | 36 | -3 | 10.0 → 10.0 | 0 → 0 |
| `rl_departure_signature/__init__.py` | D | 10 | 0 | -10 | 10.0 → – | 0 → – |
| `rl_departure_signature/nodes.py` | D | 998 | 0 | -998 | 9.81 → – | 7 → – |
| `rl_departure_signature/pipeline.py` | D | 116 | 0 | -116 | 10.0 → – | 0 → – |
| `rl_full_history/nodes.py` | L | 92 | 100 | +8 | 10.0 → 10.0 | 7 → 7 |
| `rl_full_history/pipeline.py` | L | 33 | 37 | +4 | 10.0 → 10.0 | 0 → 0 |
| `scoring_engine.py` | L | 100 | 89 | -11 | 10.0 → 10.0 | 2 → 2 |

Tier L: 3893 → 4119 lines (+226); ruff 178 → 134; pylint (line-weighted) 9.98 → 9.98; functions over 40 lines 18 → 22; Spark actions 11 → 9
Tier D: 7028 → 0 lines (-7028); ruff 135 → 0; pylint (line-weighted) 9.85 → 0.0; functions over 40 lines 36 → 0; Spark actions 47 → 0
Tier K: 1482 → 1568 lines (+86); ruff 13 → 14; pylint (line-weighted) 9.16 → 9.2; functions over 40 lines 9 → 10; Spark actions 6 → 8

Outside the Python files: `catalog_crx.yml` +13 / −201, `pipeline_registry.py` +6 / −18,
`specs/A1_ability_spec.md` 4 lines changed.

Where tier L grows (+226): the shared helpers S1 put in for A3 (`anchor.py` 52, `dcore_account_events`,
`string_key`, `segment`, `window_agg(start=)`, `log_latest_month(latest_per_account=)`) and the S4
splits and `__all__`. Functions over 40 lines rose 18 → 22 (metrics script): `_common.pit_latest` 41 (S1 + S2-01 docstring
and `scoped` join), `cc_a4_deterioration.build_cc_dpd_sequences` 42, `cc_full_history.build_cc_full_history`
43 and `rl_full_history.build_rl_full_history` 54 (the `require_columns` blocks of S3-03). For the
reviewers.
