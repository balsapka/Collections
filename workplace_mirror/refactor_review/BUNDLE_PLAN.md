# Bundle plan: council refactor → workplace (PLAN §8)

Master, round 3. This plan replaces the four-bundle sketch in PLAN §8 and in the round 2 triage
(shared, A4, A2, A1). The reason is below.

## Why two bundles, not four

The shared layer and the axes can no longer ship apart. Each of these couplings would leave the
workplace with a tree the golden harness never ran:
- `scoring_engine.StateLadder` and `points_from_level` are gone. A1 `classify.py` is now on `Scorecard`,
  so the shared bundle cannot ship without A1.
- `_common` no longer imports `_dpd_journey`; the direction is reversed (S1-01, `MODEL_ID_SEGMENT`,
  `segment`). So `_common` cannot ship without A4.
- A2 imports `window_start`, `dcore_account_events` and `GONE_DARK_DAYS` from `_common`, and its
  private copies are gone.

The golden harness, the spec tests and the reviews all cover one tree: the final commit. So the
refactor ships as **one bundle**, and each axis gets its own zero-difference check, which keeps the
isolation per axis that four bundles were meant to give.

The deletions are independent of all this. They go first, as a small bundle of their own.

## Workplace state this plan assumes (confirm before building)

- Bundles 01–14 are applied. **Bundle 14's cleanup is still pending** (user, 2026-11-05).
- **Bundle 13's cleanup: unknown.** Ask the user.
- Before building, mirror each cleanup that has been applied in the workplace onto both
  `feature/persona_redesign` and `refactor/persona_review`:
  - bundle 14: remove `a1_ability/b14_check.py`, `create_b14_check_pipeline`, the `rl_a1_ability`
    import, two registry entries and two catalog entries;
  - bundle 13: remove `rl_a4_deterioration/b13_check.py` and its pipeline, registry and catalog
    entries;
  - also update the spec tests that import the check pipelines (`a4_chain_spec.py` imports
    `create_b13_check_pipeline`).

  Then rebase `refactor/persona_review` onto the result and re-run every gate. The base of each bundle
  is the workplace-equivalent head after the cleanups.
- `make_bundle.py` numbers bundles by file count, so take the next free number and check the name
  after building. Shared numbering with the A3 session: `git pull` first.

## Bundle R-A: dead-code deletion

- **Slug:** `refactor_dead_code`.
- **Content:** the round 1 S7 stage, which is commit `98e0338` in the worktree reflog: "R1 merge S7".
  - Delete the 12 tier-D files: the old A2 `nodes.py` / `constants.py`, `cc_departure_signature/`,
    `rl_departure_signature/` except the moved function, `cc_payment_trajectory/` and
    `cc_utilisation/`.
  - Move `build_rl_depart_spine` into `rl_a4_spine/nodes.py`, unchanged.
  - Remove their 4 registry entries and imports, and the 20 catalog entries.
  - Remove three unused tier-L symbols: `parse_yyyymmdd`, `priority_reason` and `SEGMENTS`.
- **Build:** a branch from the base, then `git checkout 98e0338 -- <S7 paths>`. Re-run py_compile,
  smoke and golden on that tree before building. This exact state passed golden only as part of the
  stage sequence.
- **Exclude:** `_dcore_codes.py`, the A3 modules, and anything the A3 session has in flight.
- **PROD check:** none on data.
  - UAT: `kedro registry list` resolves.
  - PROD: run `crx_rl_a4_spine` for `rl_60_180`, because A3 reads it. Its output must match the
    previous run (row count + `exceptAll` = 0, one temporary check node).
- **Cleanup:** `hdfs dfs -rm -r` the folders of the 17 deleted persisted datasets, per model_id. The
  list is in `round_1/proposals/S7.md`.
- **Workplace tests:** any test that imports a deleted module is deleted or re-pointed (Sonnet). The
  list is in S7.md.

## Bundle R-B: the refactor (shared layer + A4 + A2 + A1 structure)

- **Slug:** `persona_refactor`.
- **Content:** every tier-L change from rounds 1–3, plus the spec-cell renames in
  `specs/A1_ability_spec.md`, the A1 / A4 spec-test updates, and the catalog comment edits.
- **Base:** R-A's head.
- **Exclude:** `_dcore_codes.py`, A3 modules, tier K/X files, `refactor_review/`, `checks/refactor_*.py`
  (mirror-only tools).
- **A3 is untouched.** This bundle must not break its imports. Smoke checks that: A3 imports
  `_common.log_latest_month`, `_spine_utils` and six `_dcore_codes` names, and none of them changed.

### PROD checks

One temporary check pipeline per axis. Each re-runs the axis into a temporary catalog entry
`crx_<p>_<axis>_rf_check` and compares it with the existing persisted output from the run before the
bundle. It logs `=== RF <AXIS> OUTPUT START/END ===`. Run order and blocks:

| Order | Pipeline (model_id) | Blocks | Expected |
|---|---|---|---|
| 1 | `crx_rl_a4_rf_check` (rl_60_180), then cc_60_180 | `RF A4 OUTPUT`: old × new `a4_state`, n differing; schema diff | **0 differing rows**, same schema |
| 2 | `crx_<p>_a2_rf_check` (rl, cc 60_180) | `RF A2 OUTPUT` as above; `RF A2 DCORE`: rows into the DCORE aggregate, share of non-attempt days, stage spill (N-3); `RF KEYS`: distinct `cif_id` / `account_id` of the obs base, BroadcastExchange size (N-4) | 0 differing rows; N-3 fallback (window form before `41d4662`) if non-attempt days > 50% or spill; drop the broadcast hint inside `scoped` if keys > 2M, broadcast > 256 MB, or timeout |
| 3 | `crx_<p>_a1_rf_check` (rl, cc 60_180) | `RF A1 OUTPUT` as above | 0 differing rows |
| 4 | shared | `RF STRING KEYS`: per key column, `sum(cast(k as string) != trim(cast(k as string)))` and the source type, at the flagged `string_key` sites (`round_2/proposals/S1.md`, Q-21; R-I R3-7) | 0 at every site, before any later `string_key` change |

After the checks pass, run the 180+ model_ids with step 8 (the real output). Cleanup prompt: remove the
check pipelines, the catalog entries, `rf_check.py`, the registry lines, the HDFS folders per
model_id, and `data/input/mirror_bundles`.

### UAT apply step

Print `pyspark.__version__` (D-2-6). The A2 DCORE rewrite needs ≥ 3.1 (`F.forall`).

### Changes the workplace sees, which go into the bundle notes

- **Tags** (S3-04, Q-15):
  - A4 → `crx_persona, crx, a4, deterioration, persona_axis`;
  - full histories → `crx_persona, crx, full_history`;
  - removed: `cc`, `rl`, `cc_a4_deterioration`, `rl_a4_deterioration`, `rl_b1`;
  - `--tags full_history` now selects both histories.
- **Logs:** the A4 state-log block now uses the A1 / A2 `log_latest_month` format (S1-06).
- **Errors:**
  - `build_dpd_sequences` now says `A4 history is missing required columns [...]` (Q-18; still
    `ValueError`);
  - the new `require_columns` guards on the obs bases, the full histories and the A4 entries (S3-03)
    raise where the code used to continue.
- **Signatures** (the workplace Sonnet updates the tests): `build_a1_ability(obs_base, anchor,
  model_id, persona_end_date, **signals)`; `build_liquidity_signals(..., *, crx_persona)`;
  `build_rl_full_history` now requires `crx_persona` (S3-05); `episode_start` needs `history_cropped`.
- **Renamed and removed public symbols.** The full tables are in `round_1/merge_log.md`,
  `round_2/proposals/S1.md`, `S4.md` and `round_3/proposals/S4.md`. The main ones:
  - `StateLadder` → `Scorecard` / `Dimension` / `Override`;
  - `points_from_level` and `priority_reason` removed;
  - `_window_start` → `window_start`;
  - `_string_key` → `_common.string_key`;
  - `MODEL_ID_SEGMENT` moved to `_common` (still re-exported);
  - `_log_state_stats` → `log_state_stats`;
  - `_dpd_journey.__all__` and `_month_label` removed;
  - the A1 label constants are now `SOURCE_INTERNAL`, `SOURCE_BUREAU`, `REASON_BUREAU_BOUNCE`.
  - new: `scoring_engine.LOW` / `MOD` / `HIGH`; A1 `HIGH_FROM` / `MODERATE_FROM`; A2 `_reachable`;
    `_common.segment`, `string_key`, `dcore_account_events`, `GONE_DARK_DAYS`; `_dpd_journey.anchor.episode_start`.

## Later, not in these bundles

- **The A1 redesign bundle** carries:
  - D-2-5: give the remaining `lookback_floor` callers the `crx_persona` floor, then delete
    `lookback_floor`;
  - the D-2-3 check: remove CAP, FORCE and the High gate if neither A1 nor A3 uses them by then;
  - the Q-26 rule column, designed together with A3's.
- **Fix bundles** from the answered questions, each with a D4 distribution and crosstab check:
  - **A4:** Q-01, Q-03, Q-04, Q-05 (decided later with the persona master);
  - **shared:** Q-02.
- **The A3 bundle** (A3 session): `a3_target_shape.md` + `a3_handoff.md`, built on R-B.
