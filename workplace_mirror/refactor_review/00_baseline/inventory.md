# crx_persona inventory (Phase 0 baseline)

Baseline: branch `refactor/persona_review` at `088580b` (code = bundle 14 head `33fcc07`).
Paths are relative to `workplace_mirror/src/enbd_collections/pipelines/crx_persona/`.
Tables below are generated (file list and public functions from the AST, the import graph
from the import statements, node I/O from `checks/refactor_smoke.py --io`); the tier D
confirmation and the A3 section are hand-checked.

## 1. Tiers

| Tier | Files | Lines | Meaning (PLAN §2) |
|---|---|---|---|
| L | 42 | 3,893 | live: review and refactor |
| D | 12 | 7,028 | dead: delete |
| K | 12 | 1,482 | kept for A3, frozen |
| A | 10 | 4,192 | A3, design-in (edits go to `a3_handoff.md`) |
| X | 3 | 723 | read only (`_dcore_codes.py`, `b13_check.py`, `b14_check.py`) |

Tier L also covers the crx part of `catalog_crx.yml`, `parameters_crx_persona.yml` and
`pipeline_registry.py` (not counted above).

### Corrections to the plan

1. **`rl_departure_signature/` is missing from the tier D row.** PLAN §2 says in prose that it
   is deleted except `build_rl_depart_spine`, but the D table lists only `cc_departure_signature/`.
   It is tiered D here (1,124 lines: `__init__.py`, `pipeline.py`, `nodes.py`), with
   `build_rl_depart_spine` (lines 85–159 of `nodes.py`) as K.
2. **Deletion order: `cc_departure_signature/` cannot go first.** `rl_departure_signature/nodes.py:42`
   imports `_TRAVEL_KEYWORDS_RE` and `_TRAVEL_MCCS` from `cc_departure_signature.nodes` at module
   level, and `rl_a4_spine/pipeline.py:17` (K) imports `build_rl_depart_spine` from that module.
   Deleting `cc_departure_signature/` before moving `build_rl_depart_spine` breaks
   `crx_rl_a4_spine` and with it `crx_rl_a3_payment_credibility` (reads `crx_rl_a4_spine`).
   `build_rl_depart_spine` itself does not use the travel constants, so the move in §2 works;
   it must happen in the same bundle as the deletion, or before it.
3. **`crx_cc_limits` becomes dead after the deletion.** Its only reader is
   `crx_cc_utilisation_features` (D). `build_cc_limits` / the `crx_cc_limits` catalog entry stay
   in tier K (cc_raw_extract, frozen) but have no consumer once D is gone. Likewise
   `crx_cc_payment_trajectory` and `crx_cc_spell_table`'s D readers disappear.
4. **Tier L outputs read by A3:** `crx_cc_full_history` (CC A3 `dpd_bucket_movement` nodes) and
   `crx_rl_full_history` (RL A3 `build_rl_a3_dlq_cycles`, and `rl_spell_table` (K)). Their schema
   and grain are a contract with A3 and K: the golden harness pins them.
5. **No tier-D output is read by A3 or a live axis.** Confirmed below; the only cross-tier link
   is the import chain in item 2.
6. The plan's L estimate (~3,900) matches: 3,893 lines in 42 files.

### Mirror gaps found (not code findings)

- 7 crx packages have no `__init__.py` in the mirror: `crx_persona/` itself, `cc_spell/`,
  `cc_full_history/`, `cc_payment_trajectory/`, `cc_utilisation/`, `cc_departure_signature/`,
  `cc_a4_deterioration/`. The registry calls `crx_cc_spell.create_pipeline()` etc., so the
  workplace copies must export `create_pipeline`; the smoke test reads `pipeline.py` instead.
- `catalog_crx.yml` has no `crx_cc_billing` entry, yet `crx_cc_a3_payment_credibility` reads it
  as a pipeline input (written by `crx_cc_raw_extract`). Either the mirror's catalog is
  incomplete or the A3 run reads an in-memory dataset that does not exist (smoke FAIL, §8 of
  `gates_baseline.md`). 18 other crx node outputs (A3 intermediates, `crx_cc_acct_windows`,
  `crx_rl_depart_*`) are memory-only within their own pipeline, which is fine.
- Unmirrored workplace modules the crx code imports: `nodes.primary.cc_way4.prm_cc`,
  `nodes.utils.config.EDP_LOAD_DATE_BUFFER_MONTHS` (`cc_raw_extract`),
  `nodes.features.dcore._feat_dcore_utils`, `nodes.utils.config_dcore` (CC A3). `kedro
  registry list` cannot run here (no `pyproject.toml`).

## 2. Files, lines, public functions

| File | Tier | Lines | Public functions / classes |
|---|---|---|---|
| `_common.py` | L | 215 | window_months(), require_columns(), parse_yyyymmdd(), pit_latest(), window_agg(), lookback_floor(), left_join_all(), log_latest_month(), build_cc_obs_base(), build_rl_obs_base() |
| `_dpd_journey/__init__.py` | L | 85 | — |
| `_dpd_journey/_dates.py` | L | 31 | — |
| `_dpd_journey/constants.py` | L | 40 | BucketScheme |
| `_dpd_journey/core.py` | L | 172 | encode(), journey_features() |
| `_dpd_journey/history.py` | L | 165 | build_history() |
| `_dpd_journey/logging.py` | L | 100 | — |
| `_dpd_journey/params.py` | L | 79 | JourneyParams, journey_params() |
| `_dpd_journey/spark.py` | L | 362 | build_dpd_sequences(), build_deterioration() |
| `_dpd_journey/states.py` | L | 126 | assign_state(), classify() |
| `a1_ability/__init__.py` | L | 17 | — |
| `a1_ability/classify.py` | L | 198 | income_level(), liquidity_level(), build_a1_ability() |
| `a1_ability/pipeline.py` | L | 176 | create_a1_pipeline(), create_b14_check_pipeline() |
| `a1_ability/signals.py` | L | 381 | build_income_signals(), build_liquidity_signals(), build_distress_signals(), build_eosb_signals() |
| `a2_locatability/__init__.py` | L | 19 | — |
| `a2_locatability/classify.py` | L | 94 | build_a2_locatability() |
| `a2_locatability/pipeline.py` | L | 89 | create_a2_pipeline() |
| `a2_locatability/signals.py` | L | 346 | build_location_signals(), gone_dark_days(), build_dcore_signals(), build_way4_deceased(), build_demographics_deceased() |
| `cc_a1_ability/__init__.py` | L | 5 | — |
| `cc_a1_ability/nodes.py` | L | 55 | build_cc_liquidity_anchor() |
| `cc_a1_ability/pipeline.py` | L | 41 | create_pipeline(), create_b14_check_pipeline() |
| `cc_a2_locatability/__init__.py` | L | 6 | — |
| `cc_a2_locatability/pipeline.py` | L | 18 | create_pipeline() |
| `cc_a4_deterioration/nodes.py` | L | 81 | build_cc_dpd_sequences(), build_cc_a4_deterioration() |
| `cc_a4_deterioration/pipeline.py` | L | 47 | create_pipeline() |
| `cc_full_history/nodes.py` | L | 60 | build_cc_full_history() |
| `cc_full_history/pipeline.py` | L | 30 | create_pipeline() |
| `obs_base/__init__.py` | L | 5 | — |
| `obs_base/pipeline.py` | L | 40 | create_cc_pipeline(), create_rl_pipeline() |
| `rl_a1_ability/__init__.py` | L | 5 | — |
| `rl_a1_ability/nodes.py` | L | 43 | build_rl_liquidity_anchor() |
| `rl_a1_ability/pipeline.py` | L | 37 | create_pipeline(), create_b14_check_pipeline() |
| `rl_a2_locatability/__init__.py` | L | 6 | — |
| `rl_a2_locatability/pipeline.py` | L | 18 | create_pipeline() |
| `rl_a4_deterioration/__init__.py` | L | 5 | — |
| `rl_a4_deterioration/chains.py` | L | 76 | Edge, Chain, Member, resolve_chains() |
| `rl_a4_deterioration/nodes.py` | L | 260 | build_rl_full_history_linked(), build_rl_dpd_sequences(), build_rl_linked_dpd_sequences(), build_rl_a4_deterioration() |
| `rl_a4_deterioration/pipeline.py` | L | 130 | create_pipeline(), create_b13_check_pipeline() |
| `rl_full_history/__init__.py` | L | 5 | — |
| `rl_full_history/nodes.py` | L | 92 | build_rl_full_history() |
| `rl_full_history/pipeline.py` | L | 33 | create_pipeline() |
| `scoring_engine.py` | L | 100 | points_from_level(), priority_reason(), StateLadder |
| `cc_a2_locatability/constants.py` | D | 299 | — |
| `cc_a2_locatability/nodes.py` | D | 1320 | build_a2_base(), build_a2_login_presence(), build_a2_contact_signals(), build_a2_locatability() |
| `cc_departure_signature/nodes.py` | D | 2375 | build_departure_spell_base(), build_departure_contract_cif(), build_departure_pass_a(), build_departure_pass_b(), build_departure_pass_c(), build_departure_pass_d(), build_departure_pass_e(), build_departure_pass_f(), build_departure_pass_g(), build_departure_pass_h(), build_departure_pass_h2(), build_departure_pass_i(), build_departure_pass_j(), build_departure_pass_k(), build_departure_final() |
| `cc_departure_signature/pipeline.py` | D | 267 | create_pipeline() |
| `cc_payment_trajectory/nodes.py` | D | 781 | build_cc_payment_trajectory() |
| `cc_payment_trajectory/pipeline.py` | D | 38 | create_pipeline() |
| `cc_utilisation/nodes.py` | D | 569 | build_cc_utilisation_features() |
| `cc_utilisation/pipeline.py` | D | 41 | create_pipeline() |
| `rl_a2_locatability/nodes.py` | D | 214 | build_rl_a2_base(), build_rl_a2_login_presence(), build_rl_a2_contact_signals() |
| `rl_departure_signature/__init__.py` | D | 10 | — |
| `rl_departure_signature/nodes.py` | D | 998 | build_rl_depart_spine(), build_rl_depart_casa_signals(), build_rl_depart_travel_mcc(), build_rl_depart_foreign_signals(), build_rl_departure_final() |
| `rl_departure_signature/pipeline.py` | D | 116 | create_pipeline() |
| `_spine_utils.py` | K | 120 | join_spine_to_spell(), rl_spine_as_cc_shim() |
| `cc_raw_extract/__init__.py` | K | 14 | — |
| `cc_raw_extract/_window_utils.py` | K | 56 | prune_by_edp_load_date(), scope_to_acct_window() |
| `cc_raw_extract/nodes.py` | K | 487 | build_cc_acct_windows(), build_cc_transactions(), build_cc_limits(), build_cc_balance(), build_cc_billing() |
| `cc_raw_extract/pipeline.py` | K | 87 | create_pipeline() |
| `cc_spell/nodes.py` | K | 237 | build_cc_spell_table() |
| `cc_spell/pipeline.py` | K | 30 | create_pipeline() |
| `rl_a4_spine/__init__.py` | K | 9 | — |
| `rl_a4_spine/pipeline.py` | K | 39 | create_pipeline() |
| `rl_spell_table/__init__.py` | K | 5 | — |
| `rl_spell_table/nodes.py` | K | 366 | build_rl_spell_table() |
| `rl_spell_table/pipeline.py` | K | 32 | create_pipeline() |
| `cc_a3_payment_credibility/__init__.py` | A | 5 | — |
| `cc_a3_payment_credibility/_signals_common.py` | A | 1153 | resolve_dlq_payment_window(), payment_meets_floor(), resolve_dpd_bucket_movement_history(), resolve_pre_dlq_spell_window(), attribute_payments_to_billing_cycles(), resolve_dlq_waterfall_qualifying_months_cleared(), filter_payment_cycles(), resolve_due_amount_m(), resolve_bucket08_fallback_due(), aggregate_dlq_window(), aggregate_pre_dlq_window(), pooled_trailing_broken_streak(), flag_plans_on_record(), flag_followups_after_refusal() |
| `cc_a3_payment_credibility/constants.py` | A | 93 | — |
| `cc_a3_payment_credibility/nodes.py` | A | 1570 | derive_commitments_level(), build_a3_commitment_signals(), build_a3_strong_negative_signals(), build_a3_payment_cycles(), build_a3_dlq_payment_signals_payment_sum_waterfall(), build_a3_dlq_payment_signals_single_payment_cycle_count(), build_a3_dlq_payment_signals_dpd_bucket_movement(), build_a3_pre_dlq_payment_signals_single_payment_cycle_count(), build_a3_pre_dlq_payment_signals_dpd_bucket_movement(), build_a3_payment_credibility() |
| `cc_a3_payment_credibility/pipeline.py` | A | 238 | create_pipeline() |
| `rl_a3_payment_credibility/__init__.py` | A | 5 | — |
| `rl_a3_payment_credibility/_signals_common.py` | A | 105 | resolve_rl_dlq_payment_window() |
| `rl_a3_payment_credibility/constants.py` | A | 58 | — |
| `rl_a3_payment_credibility/nodes.py` | A | 797 | build_rl_a3_commitment_signals(), build_rl_a3_strong_negative_signals(), build_rl_a3_dlq_cycles(), build_rl_a3_dlq_payment_signals_payment_sum_waterfall(), build_rl_a3_dlq_payment_signals_single_payment_cycle_count(), build_rl_a3_dlq_payment_signals_dpd_bucket_movement(), build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count(), build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement(), build_rl_a3_payment_credibility() |
| `rl_a3_payment_credibility/pipeline.py` | A | 168 | create_pipeline() |
| `_dcore_codes.py` | X | 281 | — |
| `a1_ability/b14_check.py` | X | 297 | compare_a1_outputs(), describe_a1_accounts(), describe_a1_bounces() |
| `rl_a4_deterioration/b13_check.py` | X | 145 | compare_rl_a4_outputs() |

Notes: `rl_departure_signature/nodes.py` is D except `build_rl_depart_spine` (K). Unused public
helpers in tier L (no caller anywhere in crx_persona or the checks): `_common.parse_yyyymmdd`,
`scoring_engine.priority_reason`, `_dpd_journey.SEGMENTS` (re-exported only). For S7.

## 3. Import graph (crx_persona modules; `EXT:` = workplace module outside crx_persona)

Arrows read "imports from". Third-party imports (pyspark, kedro, dateutil, stdlib) omitted.

- `_common.py` → `_dpd_journey.constants` (MODEL_ID_SEGMENT)
- `_dpd_journey/__init__.py` → `_dpd_journey._dates` (_month_idx, _month_label); `_dpd_journey.constants` (CC, MODEL_ID_SEGMENT, RL, SEGMENTS, BucketScheme); `_dpd_journey.core` (H, N, NO_PRIOR, P, R, _glitches, _mean, _repair, _runs, encode, journey_features); `_dpd_journey.history` (_legacy_drop, build_history); `_dpd_journey.logging` (LOG, _log_sequence_stats, _log_state_stats); `_dpd_journey.params` (PARAM_DEFAULTS, JourneyParams, journey_params); `_dpd_journey.spark` (_CLASSIFY_SCHEMA, _FEATURES, _HISTORY_SCHEMA, _idx_to_month_end, _month_col, _ship_by_value, _string_key, build_deterioration, build_dpd_sequences); `_dpd_journey.states` (DISPLAY_NAMES, STATE_RULES, STATES, assign_state, classify)
- `_dpd_journey/logging.py` → `_dpd_journey._dates` (_month_col, _month_idx, _month_label); `_dpd_journey.constants` (BucketScheme); `_dpd_journey.params` (JourneyParams)
- `_dpd_journey/params.py` → `_dpd_journey.constants` (BucketScheme, MODEL_ID_SEGMENT)
- `_dpd_journey/spark.py` → `_dpd_journey._dates` (_month_col, _month_idx); `_dpd_journey.constants` (BucketScheme); `_dpd_journey.history` (build_history); `_dpd_journey.logging` (_log_sequence_stats, _log_state_stats); `_dpd_journey.params` (JourneyParams); `_dpd_journey.states` (DISPLAY_NAMES, classify)
- `_dpd_journey/states.py` → `_dpd_journey.core` (journey_features)
- `a1_ability/__init__.py` → `a1_ability.classify` (build_a1_ability); `a1_ability.signals` (build_distress_signals, build_eosb_signals, build_income_signals, build_liquidity_signals)
- `a1_ability/b14_check.py` → `_common` (GRAIN, window_agg, window_months)
- `a1_ability/classify.py` → `_common` (GRAIN, left_join_all, log_latest_month, window_months); `scoring_engine` (StateLadder, points_from_level)
- `a1_ability/pipeline.py` → `obs_base` (create_cc_pipeline, create_rl_pipeline); `a1_ability.b14_check` (compare_a1_outputs, describe_a1_accounts, describe_a1_bounces); `a1_ability.classify` (build_a1_ability); `a1_ability.signals` (build_distress_signals, build_eosb_signals, build_income_signals, build_liquidity_signals)
- `a1_ability/signals.py` → `_common` (GRAIN, left_join_all, lookback_floor, require_columns, window_agg, window_months)
- `a2_locatability/__init__.py` → `a2_locatability.classify` (build_a2_locatability); `a2_locatability.pipeline` (create_a2_pipeline); `a2_locatability.signals` (build_dcore_signals, build_demographics_deceased, build_location_signals, build_way4_deceased)
- `a2_locatability/classify.py` → `_common` (GRAIN, left_join_all, log_latest_month); `a2_locatability.signals` (LOCATION_EVIDENCE)
- `a2_locatability/pipeline.py` → `a2_locatability.classify` (build_a2_locatability); `a2_locatability.signals` (build_dcore_signals, build_demographics_deceased, build_location_signals, build_way4_deceased)
- `a2_locatability/signals.py` → `_common` (GRAIN, left_join_all, require_columns, window_months); `_dcore_codes` (CALL_CODES, DECEASED, FAILED_CALL, IGNORED, IGNORED_PREFIX, INBOUND_CODES, OUTBOUND_CODES, RIGHT_PARTY_CONTACT, SKIP_TRACE, SUCCESS_CATEGORY); `_dpd_journey.constants` (MODEL_ID_SEGMENT)
- `cc_a1_ability/__init__.py` → `cc_a1_ability.pipeline` (create_b14_check_pipeline, create_pipeline)
- `cc_a1_ability/nodes.py` → `_common` (GRAIN, pit_latest, require_columns); `_dpd_journey` (MODEL_ID_SEGMENT)
- `cc_a1_ability/pipeline.py` → `a1_ability.pipeline` (TAGS, create_a1_pipeline, create_b14_check_pipeline); `cc_a1_ability.nodes` (build_cc_liquidity_anchor)
- `cc_a2_locatability/__init__.py` → `cc_a2_locatability.pipeline` (create_pipeline)
- `cc_a2_locatability/nodes.py` → `cc_a2_locatability.constants` (_DECEASED_RESULT_NAMES, _DEPARTURE_RESULT_NAMES, _FIELD_VISIT_RESULT_NAMES, _HARDSHIP_RESULT_NAMES, _NOT_REACHABLE_RESULT_NAMES, _PROMISE_TO_PAY_RESULT_NAMES, _REFUSING_RESULT_NAMES, _RIGHT_PARTY_CONTACT_RESULT_NAMES, _RINGING_RESULT_NAMES); `_spine_utils` (_build_cif_bridge, join_spine_to_spell)
- `cc_a2_locatability/pipeline.py` → `a2_locatability.pipeline` (create_a2_pipeline)
- `cc_a3_payment_credibility/__init__.py` → `cc_a3_payment_credibility.pipeline` (create_pipeline)
- `cc_a3_payment_credibility/_signals_common.py` → `EXT:enbd_collections.nodes.features.dcore._feat_dcore_utils` (instalment_amount_flags, null_cancelled_instalment_fields); `EXT:enbd_collections.nodes.utils.config_dcore` (PTP_INSTALMENT_STATUS_CANCELLED, SETTLEMENT_INSTALMENT_STATUS_CANCELLED); `_spine_utils` (join_spine_to_spell); `cc_a3_payment_credibility.constants` (_PAYMENT_CYCLE_FLOOR_LOOKBACK_D, _PAYMENT_CYCLE_MAX_LENGTH_D, _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N, _TAU_A3V2_COMMITMENTS_WINDOW_M, _TAU_A3V2_DLQ_PAYMENT_DUE_BASELINE_MONTHS, _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS, _TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS, _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_61_180, _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS, _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, _TAU_A3V2_PRE_DLQ_WINDOW_M)
- `cc_a3_payment_credibility/nodes.py` → `_common` (log_latest_month); `_spine_utils` (join_spine_to_spell); `cc_a3_payment_credibility._signals_common` (attribute_payments_to_billing_cycles, filter_payment_cycles, resolve_dpd_bucket_movement_history, resolve_dlq_payment_window, resolve_bucket08_fallback_due, resolve_due_amount_m, resolve_pre_dlq_spell_window, resolve_dlq_waterfall_qualifying_months_cleared, aggregate_dlq_window, aggregate_pre_dlq_window, payment_meets_floor, flag_followups_after_refusal, flag_plans_on_record, pooled_trailing_broken_streak); `_dcore_codes` (CALL_CODES, PAYMENT_CONFIRMED, PROMISE_TO_PAY, REFUSING, RETAIN_PTP, RIGHT_PARTY_CONTACT); `cc_a3_payment_credibility.constants` (_CONF_HIGH, _CONF_LOW, _CONF_MODERATE, _CONF_UNKNOWN, _DLQ_LEVEL_SATURATED, _METHOD_DPD_BUCKET_MOVEMENT, _METHOD_PAYMENT_SUM_WATERFALL, _METHOD_SINGLE_PAYMENT_CYCLE_COUNT, _SB_PRIORITY, _TAU_A3V2_DLQ_PAYMENT_BUCKET08_BASELINE_LOOKBACK_M, _TAU_A3V2_DLQ_PAYMENT_BUCKET08_SPLIT_CAP, _TAU_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE, _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_61_180, _TAU_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_180_PLUS, _TAU_A3V2_DLQ_PAYMENT_WINDOW_M_180_PLUS, _TAU_A3V2_PRE_DLQ_AMOUNT_TOLERANCE, _TAU_A3V2_PRE_DLQ_CLEAN_SHARE, _TAU_A3V2_PRE_DLQ_MIN_MONTHS_DUE, _TAU_A3V2_COMMITMENTS_BROKEN_RATE, _TAU_A3V2_COMMITMENTS_BROKEN_STREAK_N, _TAU_A3V2_COMMITMENTS_KEPT_RATE, _TAU_A3V2_COMMITMENTS_MIN_CONCLUDED, _TAU_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_180_PLUS, _TAU_A3V2_HIGH_FROM_POINTS, _TAU_A3V2_MODERATE_FROM_POINTS, _TAU_MIN_CONTACT_DATES)
- `cc_a3_payment_credibility/pipeline.py` → `cc_a3_payment_credibility.nodes` (build_a3_commitment_signals, build_a3_strong_negative_signals, build_a3_dlq_payment_signals_payment_sum_waterfall, build_a3_dlq_payment_signals_single_payment_cycle_count, build_a3_dlq_payment_signals_dpd_bucket_movement, build_a3_payment_credibility, build_a3_payment_cycles, build_a3_pre_dlq_payment_signals_single_payment_cycle_count, build_a3_pre_dlq_payment_signals_dpd_bucket_movement)
- `cc_a4_deterioration/nodes.py` → `_dpd_journey` (CC, build_deterioration, build_dpd_sequences, journey_params)
- `cc_a4_deterioration/pipeline.py` → `cc_a4_deterioration.nodes` (build_cc_a4_deterioration, build_cc_dpd_sequences)
- `cc_departure_signature/pipeline.py` → `cc_departure_signature.nodes` (build_departure_contract_cif, build_departure_final, build_departure_pass_a, build_departure_pass_b, build_departure_pass_c, build_departure_pass_d, build_departure_pass_e, build_departure_pass_f, build_departure_pass_g, build_departure_pass_h, build_departure_pass_h2, build_departure_pass_i, build_departure_pass_j, build_departure_pass_k, build_departure_spell_base)
- `cc_full_history/pipeline.py` → `cc_full_history.nodes` (build_cc_full_history)
- `cc_payment_trajectory/pipeline.py` → `cc_payment_trajectory.nodes` (build_cc_payment_trajectory)
- `cc_raw_extract/__init__.py` → `cc_raw_extract.pipeline` (create_pipeline)
- `cc_raw_extract/_window_utils.py` → `EXT:enbd_collections.nodes.utils.config` (EDP_LOAD_DATE_BUFFER_MONTHS)
- `cc_raw_extract/nodes.py` → `EXT:enbd_collections.nodes.primary.cc_way4.prm_cc` (derive_billing_amounts, derive_overdue_buckets); `EXT:enbd_collections.nodes.utils.config` (POST_BLOCK_X_SENTINEL_DATE, TXN_CATEGORIES); `cc_raw_extract._window_utils` (prune_by_edp_load_date, scope_to_acct_window)
- `cc_raw_extract/pipeline.py` → `cc_raw_extract.nodes` (build_cc_acct_windows, build_cc_balance, build_cc_billing, build_cc_limits, build_cc_transactions)
- `cc_spell/pipeline.py` → `cc_spell.nodes` (build_cc_spell_table)
- `cc_utilisation/pipeline.py` → `cc_utilisation.nodes` (build_cc_utilisation_features)
- `obs_base/__init__.py` → `obs_base.pipeline` (create_cc_pipeline, create_rl_pipeline)
- `obs_base/pipeline.py` → `_common` (build_cc_obs_base, build_rl_obs_base)
- `rl_a1_ability/__init__.py` → `rl_a1_ability.pipeline` (create_b14_check_pipeline, create_pipeline)
- `rl_a1_ability/nodes.py` → `_common` (GRAIN, lookback_floor, pit_latest, require_columns)
- `rl_a1_ability/pipeline.py` → `a1_ability.pipeline` (TAGS, create_a1_pipeline, create_b14_check_pipeline); `rl_a1_ability.nodes` (build_rl_liquidity_anchor)
- `rl_a2_locatability/__init__.py` → `rl_a2_locatability.pipeline` (create_pipeline)
- `rl_a2_locatability/nodes.py` → `cc_a2_locatability.nodes` (build_a2_contact_signals, build_a2_locatability, build_a2_login_presence)
- `rl_a2_locatability/pipeline.py` → `a2_locatability.pipeline` (create_a2_pipeline)
- `rl_a3_payment_credibility/__init__.py` → `rl_a3_payment_credibility.pipeline` (create_pipeline)
- `rl_a3_payment_credibility/_signals_common.py` → `_spine_utils` (join_spine_to_spell, rl_spine_as_cc_shim); `rl_a3_payment_credibility.constants` (_DLQ_WINDOW_SPLIT_THRESHOLD_RL, _TAU_RL_A3V2_DLQ_PAYMENT_ANY_WINDOW_M_DEEP, _TAU_RL_A3V2_DLQ_PAYMENT_MIN_AMOUNT_DEEP, _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP, _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_MID)
- `rl_a3_payment_credibility/constants.py` → `cc_a3_payment_credibility.constants` (_METHOD_SINGLE_PAYMENT_CYCLE_COUNT)
- `rl_a3_payment_credibility/nodes.py` → `_spine_utils` (rl_spine_as_cc_shim); `cc_a3_payment_credibility.nodes` (build_a3_commitment_signals, build_a3_payment_credibility, build_a3_strong_negative_signals); `cc_a3_payment_credibility._signals_common` (aggregate_dlq_window, aggregate_pre_dlq_window, payment_meets_floor, resolve_pre_dlq_spell_window); `rl_a3_payment_credibility._signals_common` (resolve_rl_dlq_payment_window); `rl_a3_payment_credibility.constants` (_DLQ_LEVEL_SATURATED_RL, _DLQ_PAYMENT_EVIDENCE_METHOD_RL, _PRE_DLQ_NOT_DELINQUENT_MAX_RL, _PRE_DLQ_PAYMENT_EVIDENCE_METHOD_RL, _TAU_RL_A3V2_DLQ_PAYMENT_QUALIFYING_SHARE, _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_DEEP, _TAU_RL_A3V2_DLQ_PAYMENT_REGULAR_FROM_MONTHS_MID, _TAU_RL_A3V2_DLQ_PAYMENT_WINDOW_M_DEEP, _TAU_RL_A3V2_PRE_DLQ_AMOUNT_TOLERANCE, _TAU_RL_A3V2_PRE_DLQ_MIN_MONTHS_DUE)
- `rl_a3_payment_credibility/pipeline.py` → `rl_a3_payment_credibility.nodes` (build_rl_a3_commitment_signals, build_rl_a3_dlq_cycles, build_rl_a3_dlq_payment_signals_dpd_bucket_movement, build_rl_a3_dlq_payment_signals_payment_sum_waterfall, build_rl_a3_dlq_payment_signals_single_payment_cycle_count, build_rl_a3_payment_credibility, build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement, build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count, build_rl_a3_strong_negative_signals)
- `rl_a4_deterioration/__init__.py` → `rl_a4_deterioration.pipeline` (create_b13_check_pipeline, create_pipeline)
- `rl_a4_deterioration/nodes.py` → `_common` (require_columns); `_dpd_journey` (RL, _log_state_stats, build_deterioration, build_dpd_sequences, journey_params); `rl_a4_deterioration.chains` (Edge, resolve_chains)
- `rl_a4_deterioration/pipeline.py` → `rl_a4_deterioration.b13_check` (compare_rl_a4_outputs); `rl_a4_deterioration.nodes` (build_rl_a4_deterioration, build_rl_dpd_sequences, build_rl_full_history_linked, build_rl_linked_dpd_sequences)
- `rl_a4_spine/__init__.py` → `rl_a4_spine.pipeline` (create_pipeline)
- `rl_a4_spine/pipeline.py` → `rl_departure_signature.nodes` (build_rl_depart_spine)
- `rl_departure_signature/__init__.py` → `rl_departure_signature.pipeline` (create_pipeline)
- `rl_departure_signature/nodes.py` → `cc_departure_signature.nodes` (_TRAVEL_KEYWORDS_RE, _TRAVEL_MCCS)
- `rl_departure_signature/pipeline.py` → `rl_departure_signature.nodes` (build_rl_depart_casa_signals, build_rl_depart_foreign_signals, build_rl_depart_spine, build_rl_depart_travel_mcc, build_rl_departure_final)
- `rl_full_history/__init__.py` → `rl_full_history.pipeline` (create_pipeline)
- `rl_full_history/pipeline.py` → `rl_full_history.nodes` (build_rl_full_history)
- `rl_spell_table/__init__.py` → `rl_spell_table.pipeline` (create_pipeline)
- `rl_spell_table/pipeline.py` → `rl_spell_table.nodes` (build_rl_spell_table)

Shape, in short:
- `_dpd_journey` (A4 engine) ← `_common` (only `MODEL_ID_SEGMENT`), `cc_a1_ability/nodes`,
  `a2_locatability/signals` (`MODEL_ID_SEGMENT`), `cc_a4_deterioration`, `rl_a4_deterioration`.
- `_common` ← A1 engine, A2 engine, CC/RL A1 anchors, `obs_base`, `rl_a4_deterioration`, CC A3
  (`log_latest_month`).
- `scoring_engine` ← `a1_ability/classify` only.
- `a1_ability/pipeline.py` imports `b14_check` (X) and `obs_base` at module level: the bundle 14
  cleanup must edit it.
- `rl_a4_deterioration/pipeline.py` imports `b13_check` (X) at module level, same.
- Dead chain: `rl_a2_locatability/nodes` (D) → `cc_a2_locatability/nodes` (D) → `_spine_utils` (K)
  and `cc_a2_locatability/constants` (D); `rl_a4_spine` (K) → `rl_departure_signature/nodes` (D)
  → `cc_departure_signature/nodes` (D).

## 4. Pipelines: node inputs → outputs (all registry `crx_*` entries)

### crx_cc_a1_ability
- `build_crx_cc_a1_distress_signals`: crx_cc_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_cc_a1_distress_signals
- `build_crx_cc_a1_eosb_signals`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_cc_a1_eosb_signals
- `build_crx_cc_a1_income_signals`: crx_cc_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id -> crx_cc_a1_income_signals
- `build_crx_cc_a1_liquidity_anchor`: crx_cc_obs_base, prm_balance, params:model_id -> crx_cc_a1_liquidity_anchor
- `build_crx_cc_a1_liquidity_signals`: crx_cc_obs_base, feat_cif_casa_balance_monthly, feat_cif_ext_card_payment_monthly, feat_cif_casa_activity_monthly, params:model_id -> crx_cc_a1_liquidity_signals
- `build_crx_cc_a1_ability`: crx_cc_obs_base, crx_cc_a1_income_signals, crx_cc_a1_liquidity_signals, crx_cc_a1_distress_signals, crx_cc_a1_eosb_signals, crx_cc_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a1_ability

### crx_cc_a1_ability_b14_check
- `build_crx_cc_obs_base`: cc_spine, params:crx_persona -> crx_cc_obs_base
- `build_crx_cc_a1_distress_signals`: crx_cc_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_cc_a1_distress_signals
- `build_crx_cc_a1_eosb_signals`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_cc_a1_eosb_signals
- `build_crx_cc_a1_income_signals`: crx_cc_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id -> crx_cc_a1_income_signals
- `build_crx_cc_a1_liquidity_anchor`: crx_cc_obs_base, prm_balance, params:model_id -> crx_cc_a1_liquidity_anchor
- `build_crx_cc_a1_liquidity_signals`: crx_cc_obs_base, feat_cif_casa_balance_monthly, feat_cif_ext_card_payment_monthly, feat_cif_casa_activity_monthly, params:model_id -> crx_cc_a1_liquidity_signals
- `describe_crx_cc_a1_b14_accounts`: crx_cc_obs_base, prm_casa_transactions, raw_casa_acid_to_cif, params:casa_primary.current_account_codes, params:casa_primary.saving_account_codes, feat_cif_casa_activity_monthly, params:model_id -> (log only)
- `describe_crx_cc_a1_b14_bounces`: crx_cc_obs_base, prm_bureau_alert_enriched, feat_cif_bureau_bounces_monthly, params:model_id -> (log only)
- `build_crx_cc_a1_ability`: crx_cc_obs_base, crx_cc_a1_income_signals, crx_cc_a1_liquidity_signals, crx_cc_a1_distress_signals, crx_cc_a1_eosb_signals, crx_cc_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a1_ability_b14_check
- `compare_crx_cc_a1_b14`: crx_cc_a1_ability, crx_cc_a1_ability_b14_check, crx_cc_obs_base, params:model_id -> (log only)

### crx_cc_a2_locatability
- `build_crx_cc_a2_dcore_signals`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_cc_a2_dcore_signals
- `build_crx_cc_a2_demographics_deceased`: crx_cc_obs_base, feat_demographics_cif -> crx_cc_a2_demographics_deceased
- `build_crx_cc_a2_location_signals`: crx_cc_obs_base, feat_cif_location_monthly, params:model_id -> crx_cc_a2_location_signals
- `build_crx_cc_a2_way4_deceased`: crx_cc_obs_base, prm_contract, prm_client -> crx_cc_a2_way4_deceased
- `build_crx_cc_a2_locatability`: crx_cc_obs_base, crx_cc_a2_location_signals, crx_cc_a2_dcore_signals, crx_cc_a2_way4_deceased, crx_cc_a2_demographics_deceased, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a2_locatability

### crx_cc_a3_payment_credibility
- `build_a3_commitment_signals`: cc_spine, crx_cc_spell_table, dcore_observation_spine, dcore_feat_ptp, dcore_feat_settlement, dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement, dcore_prm_settlement_schedule_instalments -> crx_cc_a3_commitment_signals
- `build_a3_payment_cycles`: crx_cc_billing, crx_cc_balance, crx_cc_transactions, params:cc_a3_history_floor_date -> crx_cc_a3_payment_cycles
- `build_a3_strong_negative_signals`: cc_spine, crx_cc_spell_table, dcore_observation_spine, dcore_prm_followup_outcomes, dcore_int_ptp, dcore_int_settlement, crx_cc_transactions -> crx_cc_a3_strong_negative_signals
- `build_a3_dlq_payment_signals_dpd_bucket_movement`: crx_cc_a3_payment_cycles, crx_cc_full_history, crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_a3_dlq_payment_signals_dpd_bucket_movement
- `build_a3_dlq_payment_signals_payment_sum_waterfall`: crx_cc_a3_payment_cycles, crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_a3_dlq_payment_signals_payment_sum_waterfall
- `build_a3_dlq_payment_signals_single_payment_cycle_count`: crx_cc_a3_payment_cycles, crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_a3_dlq_payment_signals_single_payment_cycle_count
- `build_a3_pre_dlq_payment_signals_dpd_bucket_movement`: crx_cc_a3_payment_cycles, crx_cc_full_history, crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement
- `build_a3_pre_dlq_payment_signals_single_payment_cycle_count`: crx_cc_a3_payment_cycles, crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count
- `build_a3_payment_credibility`: crx_cc_a3_commitment_signals, crx_cc_a3_strong_negative_signals, crx_cc_a3_dlq_payment_signals_payment_sum_waterfall, crx_cc_a3_dlq_payment_signals_single_payment_cycle_count, crx_cc_a3_dlq_payment_signals_dpd_bucket_movement, crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count, crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement, params:a3_dlq_payment_evidence_method, params:a3_pre_dlq_payment_evidence_method, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a3_payment_credibility

### crx_cc_a4_deterioration
- `build_crx_cc_dpd_sequences`: crx_cc_full_history, params:crx_persona, params:model_id -> crx_cc_dpd_sequences
- `build_crx_cc_a4_deterioration`: crx_cc_dpd_sequences, cc_spine, params:crx_persona, params:model_id -> crx_cc_a4_deterioration

### crx_cc_departure_signature
- `build_crx_departure_contract_cif`: prm_contract, prm_client -> crx_cc_departure_contract_cif
- `build_crx_departure_spell_base`: crx_cc_spell_table, crx_cc_payment_trajectory, cc_spine -> crx_cc_departure_spell_base
- `build_crx_departure_pass_a`: crx_cc_transactions, crx_cc_departure_spell_base -> crx_cc_departure_pass_a
- `build_crx_departure_pass_b`: comp_financial_tran_repos_dly, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_b
- `build_crx_departure_pass_c`: crx_cc_spell_table, crx_cc_departure_spell_base -> crx_cc_departure_pass_c
- `build_crx_departure_pass_e`: int_bureau_pull_monthly, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_e
- `build_crx_departure_pass_f`: feat_product_holding, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_f
- `build_crx_departure_pass_g`: fea_monthly_aecb_alerts, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_g
- `build_crx_departure_pass_h`: feat_fx_leakage, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_h
- `build_crx_departure_pass_h2`: feat_cc_txns_rfs, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_h2
- `build_crx_departure_pass_i`: feat_payroll_indicator, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_i
- `build_crx_departure_pass_j`: prm_digital_login_monthly, crx_cc_departure_contract_cif, crx_cc_departure_spell_base -> crx_cc_departure_pass_j
- `build_crx_departure_pass_k`: crx_cc_transactions, prm_contract, crx_cc_departure_spell_base -> crx_cc_departure_pass_k
- `build_crx_departure_pass_d`: prm_contract, prm_turnovers, crx_cc_departure_spell_base, crx_cc_departure_pass_a -> crx_cc_departure_pass_d
- `build_crx_departure_final`: crx_cc_departure_spell_base, crx_cc_departure_pass_a, crx_cc_departure_pass_b, crx_cc_departure_pass_c, crx_cc_departure_pass_d, crx_cc_departure_pass_e, crx_cc_departure_pass_f, crx_cc_departure_pass_g, crx_cc_departure_pass_h, crx_cc_departure_pass_h2, crx_cc_departure_pass_i, crx_cc_departure_pass_j, crx_cc_departure_pass_k -> crx_cc_departure_signature

### crx_cc_full_history
- `build_crx_cc_full_history`: raw_stg_billing, cc_spine -> crx_cc_full_history

### crx_cc_obs_base
- `build_crx_cc_obs_base`: cc_spine, params:crx_persona -> crx_cc_obs_base

### crx_cc_payment_trajectory
- `build_crx_cc_payment_trajectory`: crx_cc_transactions, crx_cc_balance, crx_cc_spell_table, prm_contract -> crx_cc_payment_trajectory

### crx_cc_raw_extract
- `build_crx_cc_acct_windows`: crx_cc_spell_table, cc_spine, params:cc_a3_history_floor_date -> crx_cc_acct_windows
- `build_crx_cc_limits`: raw_stg_limit, crx_cc_spell_table -> crx_cc_limits
- `build_crx_cc_balance`: raw_stg_balance, raw_stg_account_group, crx_cc_acct_windows -> crx_cc_balance
- `build_crx_cc_billing`: raw_stg_billing, crx_cc_acct_windows -> crx_cc_billing
- `build_crx_cc_transactions`: raw_transaction, crx_cc_acct_windows -> crx_cc_transactions

### crx_cc_spell_table
- `build_crx_cc_spell_table`: raw_stg_billing, cc_spine -> crx_cc_spell_table

### crx_cc_utilisation_features
- `build_crx_cc_utilisation_features`: crx_cc_limits, crx_cc_transactions, crx_cc_spell_table, crx_cc_payment_trajectory -> crx_cc_utilisation_features

### crx_rl_a1_ability
- `build_crx_rl_a1_distress_signals`: crx_rl_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_rl_a1_distress_signals
- `build_crx_rl_a1_eosb_signals`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_rl_a1_eosb_signals
- `build_crx_rl_a1_income_signals`: crx_rl_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id, feature_retail_loans -> crx_rl_a1_income_signals
- `build_crx_rl_a1_liquidity_anchor`: crx_rl_obs_base, int_loan_master -> crx_rl_a1_liquidity_anchor
- `build_crx_rl_a1_liquidity_signals`: crx_rl_obs_base, feat_cif_casa_balance_monthly, feat_cif_ext_card_payment_monthly, feat_cif_casa_activity_monthly, params:model_id -> crx_rl_a1_liquidity_signals
- `build_crx_rl_a1_ability`: crx_rl_obs_base, crx_rl_a1_income_signals, crx_rl_a1_liquidity_signals, crx_rl_a1_distress_signals, crx_rl_a1_eosb_signals, crx_rl_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a1_ability

### crx_rl_a1_ability_b14_check
- `build_crx_rl_obs_base`: rl_spine, params:crx_persona -> crx_rl_obs_base
- `build_crx_rl_a1_distress_signals`: crx_rl_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_rl_a1_distress_signals
- `build_crx_rl_a1_eosb_signals`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_rl_a1_eosb_signals
- `build_crx_rl_a1_income_signals`: crx_rl_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id, feature_retail_loans -> crx_rl_a1_income_signals
- `build_crx_rl_a1_liquidity_anchor`: crx_rl_obs_base, int_loan_master -> crx_rl_a1_liquidity_anchor
- `build_crx_rl_a1_liquidity_signals`: crx_rl_obs_base, feat_cif_casa_balance_monthly, feat_cif_ext_card_payment_monthly, feat_cif_casa_activity_monthly, params:model_id -> crx_rl_a1_liquidity_signals
- `describe_crx_rl_a1_b14_accounts`: crx_rl_obs_base, prm_casa_transactions, raw_casa_acid_to_cif, params:casa_primary.current_account_codes, params:casa_primary.saving_account_codes, feat_cif_casa_activity_monthly, params:model_id -> (log only)
- `describe_crx_rl_a1_b14_bounces`: crx_rl_obs_base, prm_bureau_alert_enriched, feat_cif_bureau_bounces_monthly, params:model_id -> (log only)
- `build_crx_rl_a1_ability`: crx_rl_obs_base, crx_rl_a1_income_signals, crx_rl_a1_liquidity_signals, crx_rl_a1_distress_signals, crx_rl_a1_eosb_signals, crx_rl_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a1_ability_b14_check
- `compare_crx_rl_a1_b14`: crx_rl_a1_ability, crx_rl_a1_ability_b14_check, rl_spine, params:model_id -> (log only)

### crx_rl_a2_locatability
- `build_crx_rl_a2_dcore_signals`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_rl_a2_dcore_signals
- `build_crx_rl_a2_demographics_deceased`: crx_rl_obs_base, feat_demographics_cif -> crx_rl_a2_demographics_deceased
- `build_crx_rl_a2_location_signals`: crx_rl_obs_base, feat_cif_location_monthly, params:model_id -> crx_rl_a2_location_signals
- `build_crx_rl_a2_way4_deceased`: crx_rl_obs_base, prm_contract, prm_client -> crx_rl_a2_way4_deceased
- `build_crx_rl_a2_locatability`: crx_rl_obs_base, crx_rl_a2_location_signals, crx_rl_a2_dcore_signals, crx_rl_a2_way4_deceased, crx_rl_a2_demographics_deceased, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a2_locatability

### crx_rl_a3_payment_credibility
- `build_rl_a3_commitment_signals`: crx_rl_a4_spine, dcore_observation_spine, dcore_feat_ptp, dcore_feat_settlement, dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement, dcore_prm_settlement_schedule_instalments -> crx_rl_a3_commitment_signals
- `build_rl_a3_dlq_cycles`: crx_rl_full_history, int_loan_master, rl_spine -> crx_rl_a3_dlq_cycles
- `build_rl_a3_strong_negative_signals`: crx_rl_a4_spine, dcore_observation_spine, dcore_prm_followup_outcomes, params:crx_persona, dcore_int_ptp, dcore_int_settlement -> crx_rl_a3_strong_negative_signals
- `build_rl_a3_dlq_payment_signals_dpd_bucket_movement`: crx_rl_a3_dlq_cycles, crx_rl_a4_spine -> crx_rl_a3_dlq_payment_signals_dpd_bucket_movement
- `build_rl_a3_dlq_payment_signals_payment_sum_waterfall`: crx_rl_a3_dlq_cycles, crx_rl_a4_spine -> crx_rl_a3_dlq_payment_signals_payment_sum_waterfall
- `build_rl_a3_dlq_payment_signals_single_payment_cycle_count`: crx_rl_a3_dlq_cycles, crx_rl_a4_spine -> crx_rl_a3_dlq_payment_signals_single_payment_cycle_count
- `build_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement`: crx_rl_a3_dlq_cycles, crx_rl_a4_spine -> crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement
- `build_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count`: crx_rl_a3_dlq_cycles, crx_rl_a4_spine -> crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count
- `build_rl_a3_payment_credibility`: crx_rl_a3_commitment_signals, crx_rl_a3_strong_negative_signals, crx_rl_a3_dlq_payment_signals_payment_sum_waterfall, crx_rl_a3_dlq_payment_signals_single_payment_cycle_count, crx_rl_a3_dlq_payment_signals_dpd_bucket_movement, crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count, crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement, params:rl_a3_dlq_payment_evidence_method, params:rl_a3_pre_dlq_payment_evidence_method, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a3_payment_credibility

### crx_rl_a4_deterioration
- `build_crx_rl_dpd_sequences`: crx_rl_full_history, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences
- `build_crx_rl_full_history_linked`: crx_rl_full_history, int_loan_master, int_loan_restructure_link -> crx_rl_full_history_linked, crx_rl_restructure_chains
- `build_crx_rl_dpd_sequences_linked`: crx_rl_full_history_linked, crx_rl_restructure_chains, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences_linked
- `build_crx_rl_a4_deterioration`: crx_rl_dpd_sequences, crx_rl_dpd_sequences_linked, crx_rl_restructure_chains, rl_spine, params:crx_persona, params:model_id -> crx_rl_a4_deterioration

### crx_rl_a4_deterioration_b13_check
- `build_crx_rl_dpd_sequences_b13_check`: crx_rl_full_history, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences_b13_check
- `build_crx_rl_full_history_linked`: crx_rl_full_history, int_loan_master, int_loan_restructure_link -> crx_rl_full_history_linked, crx_rl_restructure_chains
- `build_crx_rl_dpd_sequences_linked`: crx_rl_full_history_linked, crx_rl_restructure_chains, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences_linked
- `build_crx_rl_a4_deterioration_b13_check`: crx_rl_dpd_sequences_b13_check, crx_rl_dpd_sequences_linked, crx_rl_restructure_chains, rl_spine, params:crx_persona, params:model_id -> crx_rl_a4_deterioration_b13_check
- `compare_rl_a4_outputs`: crx_rl_a4_deterioration, crx_rl_a4_deterioration_b13_check, feature_retail_loans, rl_spine, params:model_id -> (log only)

### crx_rl_a4_spine
- `build_crx_rl_a4_spine`: rl_spine, crx_rl_spell_table, params:crx_persona -> crx_rl_a4_spine

### crx_rl_departure_signature
- `build_rl_depart_spine`: rl_spine, crx_rl_spell_table, params:crx_persona -> crx_rl_depart_spine
- `build_rl_depart_casa_signals`: crx_rl_depart_spine, comp_financial_tran_repos_dly, feat_payroll_indicator, params:crx_persona -> crx_rl_depart_casa_signals
- `build_rl_depart_foreign_signals`: crx_rl_depart_spine, feat_fx_leakage, prm_digital_login_monthly -> crx_rl_depart_foreign_signals
- `build_rl_depart_travel_mcc`: crx_rl_depart_spine, comp_financial_tran_repos_dly -> crx_rl_depart_travel_mcc
- `build_rl_departure_final`: crx_rl_depart_spine, crx_rl_depart_travel_mcc, crx_rl_depart_foreign_signals, crx_rl_depart_casa_signals -> crx_rl_departure_signature

### crx_rl_full_history
- `build_crx_rl_full_history`: rl_spine, int_loan_master, params:crx_persona -> crx_rl_full_history

### crx_rl_obs_base
- `build_crx_rl_obs_base`: rl_spine, params:crx_persona -> crx_rl_obs_base

### crx_rl_spell_table
- `build_crx_rl_spell_table`: crx_rl_full_history, rl_spine -> crx_rl_spell_table


### crx datasets: writer pipelines and readers in other pipelines

| Dataset | Written by | Read by (other pipelines) |
|---|---|---|
| `crx_cc_a1_ability` | crx_cc_a1_ability | crx_cc_a1_ability_b14_check |
| `crx_cc_a1_ability_b14_check` | crx_cc_a1_ability_b14_check | — |
| `crx_cc_a1_distress_signals` | crx_cc_a1_ability, crx_cc_a1_ability_b14_check | — |
| `crx_cc_a1_eosb_signals` | crx_cc_a1_ability, crx_cc_a1_ability_b14_check | — |
| `crx_cc_a1_income_signals` | crx_cc_a1_ability, crx_cc_a1_ability_b14_check | — |
| `crx_cc_a1_liquidity_anchor` | crx_cc_a1_ability, crx_cc_a1_ability_b14_check | — |
| `crx_cc_a1_liquidity_signals` | crx_cc_a1_ability, crx_cc_a1_ability_b14_check | — |
| `crx_cc_a2_dcore_signals` | crx_cc_a2_locatability | — |
| `crx_cc_a2_demographics_deceased` | crx_cc_a2_locatability | — |
| `crx_cc_a2_locatability` | crx_cc_a2_locatability | — |
| `crx_cc_a2_location_signals` | crx_cc_a2_locatability | — |
| `crx_cc_a2_way4_deceased` | crx_cc_a2_locatability | — |
| `crx_cc_a3_commitment_signals` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_dlq_payment_signals_dpd_bucket_movement` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_dlq_payment_signals_payment_sum_waterfall` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_dlq_payment_signals_single_payment_cycle_count` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_payment_credibility` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_payment_cycles` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_pre_dlq_payment_signals_dpd_bucket_movement` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a3_strong_negative_signals` | crx_cc_a3_payment_credibility | — |
| `crx_cc_a4_deterioration` | crx_cc_a4_deterioration | — |
| `crx_cc_acct_windows` | crx_cc_raw_extract | — |
| `crx_cc_balance` | crx_cc_raw_extract | crx_cc_a3_payment_credibility, crx_cc_payment_trajectory |
| `crx_cc_billing` | crx_cc_raw_extract | crx_cc_a3_payment_credibility |
| `crx_cc_departure_contract_cif` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_a` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_b` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_c` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_d` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_e` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_f` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_g` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_h` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_h2` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_i` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_j` | crx_cc_departure_signature | — |
| `crx_cc_departure_pass_k` | crx_cc_departure_signature | — |
| `crx_cc_departure_signature` | crx_cc_departure_signature | — |
| `crx_cc_departure_spell_base` | crx_cc_departure_signature | — |
| `crx_cc_dpd_sequences` | crx_cc_a4_deterioration | — |
| `crx_cc_full_history` | crx_cc_full_history | crx_cc_a3_payment_credibility, crx_cc_a4_deterioration |
| `crx_cc_limits` | crx_cc_raw_extract | crx_cc_utilisation_features |
| `crx_cc_obs_base` | crx_cc_a1_ability_b14_check, crx_cc_obs_base | crx_cc_a1_ability, crx_cc_a2_locatability |
| `crx_cc_payment_trajectory` | crx_cc_payment_trajectory | crx_cc_departure_signature, crx_cc_utilisation_features |
| `crx_cc_spell_table` | crx_cc_spell_table | crx_cc_a3_payment_credibility, crx_cc_departure_signature, crx_cc_payment_trajectory, crx_cc_raw_extract, crx_cc_utilisation_features |
| `crx_cc_transactions` | crx_cc_raw_extract | crx_cc_a3_payment_credibility, crx_cc_departure_signature, crx_cc_payment_trajectory, crx_cc_utilisation_features |
| `crx_cc_utilisation_features` | crx_cc_utilisation_features | — |
| `crx_rl_a1_ability` | crx_rl_a1_ability | crx_rl_a1_ability_b14_check |
| `crx_rl_a1_ability_b14_check` | crx_rl_a1_ability_b14_check | — |
| `crx_rl_a1_distress_signals` | crx_rl_a1_ability, crx_rl_a1_ability_b14_check | — |
| `crx_rl_a1_eosb_signals` | crx_rl_a1_ability, crx_rl_a1_ability_b14_check | — |
| `crx_rl_a1_income_signals` | crx_rl_a1_ability, crx_rl_a1_ability_b14_check | — |
| `crx_rl_a1_liquidity_anchor` | crx_rl_a1_ability, crx_rl_a1_ability_b14_check | — |
| `crx_rl_a1_liquidity_signals` | crx_rl_a1_ability, crx_rl_a1_ability_b14_check | — |
| `crx_rl_a2_dcore_signals` | crx_rl_a2_locatability | — |
| `crx_rl_a2_demographics_deceased` | crx_rl_a2_locatability | — |
| `crx_rl_a2_locatability` | crx_rl_a2_locatability | — |
| `crx_rl_a2_location_signals` | crx_rl_a2_locatability | — |
| `crx_rl_a2_way4_deceased` | crx_rl_a2_locatability | — |
| `crx_rl_a3_commitment_signals` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_dlq_cycles` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_dlq_payment_signals_dpd_bucket_movement` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_dlq_payment_signals_payment_sum_waterfall` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_dlq_payment_signals_single_payment_cycle_count` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_payment_credibility` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_pre_dlq_payment_signals_dpd_bucket_movement` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a3_strong_negative_signals` | crx_rl_a3_payment_credibility | — |
| `crx_rl_a4_deterioration` | crx_rl_a4_deterioration | crx_rl_a4_deterioration_b13_check |
| `crx_rl_a4_deterioration_b13_check` | crx_rl_a4_deterioration_b13_check | — |
| `crx_rl_a4_spine` | crx_rl_a4_spine | crx_rl_a3_payment_credibility |
| `crx_rl_depart_casa_signals` | crx_rl_departure_signature | — |
| `crx_rl_depart_foreign_signals` | crx_rl_departure_signature | — |
| `crx_rl_depart_spine` | crx_rl_departure_signature | — |
| `crx_rl_depart_travel_mcc` | crx_rl_departure_signature | — |
| `crx_rl_departure_signature` | crx_rl_departure_signature | — |
| `crx_rl_dpd_sequences` | crx_rl_a4_deterioration | — |
| `crx_rl_dpd_sequences_b13_check` | crx_rl_a4_deterioration_b13_check | — |
| `crx_rl_dpd_sequences_linked` | crx_rl_a4_deterioration, crx_rl_a4_deterioration_b13_check | — |
| `crx_rl_full_history` | crx_rl_full_history | crx_rl_a3_payment_credibility, crx_rl_a4_deterioration, crx_rl_a4_deterioration_b13_check, crx_rl_spell_table |
| `crx_rl_full_history_linked` | crx_rl_a4_deterioration, crx_rl_a4_deterioration_b13_check | — |
| `crx_rl_obs_base` | crx_rl_a1_ability_b14_check, crx_rl_obs_base | crx_rl_a1_ability, crx_rl_a2_locatability |
| `crx_rl_restructure_chains` | crx_rl_a4_deterioration, crx_rl_a4_deterioration_b13_check | — |
| `crx_rl_spell_table` | crx_rl_spell_table | crx_rl_a4_spine, crx_rl_departure_signature |

## 5. Tier D confirmation

Checked: Python imports in `src/`, `checks/` and `tools/` (grep and the import graph), every
pipeline's inputs (§4), and the registry. "Registry" = registered as a pipeline, which only
runs it; it is not a consumer.

| Tier-D file | Imported by | Its outputs read by | Registry | Verdict |
|---|---|---|---|---|
| `cc_a2_locatability/nodes.py` (1,320) | `rl_a2_locatability/nodes.py` (D) only; the wrappers import `a2_locatability.pipeline` | not wired in any pipeline (`cc_a2_locatability/pipeline.py` calls the engine) | — | dead |
| `cc_a2_locatability/constants.py` (299) | `cc_a2_locatability/nodes.py` (D) only | — | — | dead |
| `rl_a2_locatability/nodes.py` (214) | nothing | not wired | — | dead |
| `cc_departure_signature/` (2,642) | **`rl_departure_signature/nodes.py:42`** (D, module level: `_TRAVEL_KEYWORDS_RE`, `_TRAVEL_MCCS`) | `crx_cc_departure_signature` and its 14 intermediate tables: no reader outside the pipeline | `crx_cc_departure_signature` | dead, but see correction 2 (import chain to K / A3) |
| `cc_payment_trajectory/` (819) | nothing | `crx_cc_payment_trajectory` → `crx_cc_departure_signature`, `crx_cc_utilisation_features` (both D) | `crx_cc_payment_trajectory` | dead |
| `cc_utilisation/` (610) | nothing | `crx_cc_utilisation_features`: no reader | `crx_cc_utilisation_features` | dead |
| `rl_departure_signature/` (1,124; correction 1) | `rl_a4_spine/pipeline.py:17` (K) imports `build_rl_depart_spine` | `crx_rl_departure_signature` and `crx_rl_depart_*`: no reader outside the pipeline | `crx_rl_departure_signature` | dead except `build_rl_depart_spine` (K, moves to `rl_a4_spine/`) |

Text-only mentions (docstrings, no import): `cc_spell/nodes.py:11-12` names the D packages
among its readers; `cc_a2_locatability/nodes.py` docstrings name `crx_cc_departure_signature`.
No test module is mirrored (`src/tests/` absent), so test imports of D code cannot be checked
here; the workplace Sonnet owns them.

Registry lines to remove with tier D (`pipeline_registry.py`): the imports of
`cc_payment_trajectory`, `cc_utilisation`, `cc_departure_signature`, `rl_departure_signature`
and the entries `crx_cc_payment_trajectory`, `crx_cc_utilisation_features`,
`crx_cc_departure_signature`, `crx_rl_departure_signature`. Catalog entries to remove:
`crx_cc_payment_trajectory`, `crx_cc_utilisation_features`, `crx_cc_departure_*` (15),
`crx_rl_depart_travel_mcc`, `crx_rl_depart_foreign_signals`, `crx_rl_departure_signature`.

## 6. A3 (tier A) dependencies on shared code

| Shared piece | Used by A3 | What exactly |
|---|---|---|
| `_common.py` (L) | `cc_a3_payment_credibility/nodes.py` | `log_latest_month` only |
| `_spine_utils.py` (K) | CC `nodes.py`, CC `_signals_common.py`, RL `_signals_common.py`, RL `nodes.py` | `join_spine_to_spell` (CC + RL), `rl_spine_as_cc_shim` (RL) |
| `_dcore_codes.py` (X) | CC `nodes.py` | `CALL_CODES`, `PAYMENT_CONFIRMED`, `PROMISE_TO_PAY`, `REFUSING`, `RETAIN_PTP`, `RIGHT_PARTY_CONTACT` |
| `_dpd_journey/` (L) | — | no import today; D-A3 plan wants the episode anchor (`months_before_spell`) from it |
| `scoring_engine.py` (L) | — | no import (A3 has its own ladder in `nodes.py`) |
| spell tables (K) | CC pipeline reads `crx_cc_spell_table`; RL reads `crx_rl_a4_spine` (= `build_rl_depart_spine` over `crx_rl_spell_table`) | spell grain `(account_id, spell_id)`, T0 |
| `cc_raw_extract` (K) | CC pipeline reads `crx_cc_billing`, `crx_cc_balance`, `crx_cc_transactions` | `crx_cc_billing` has no catalog entry in the mirror (§1) |
| full histories (L) | CC reads `crx_cc_full_history`; RL reads `crx_rl_full_history` | schema is a contract (golden harness pins it) |
| params | `cc_a3_history_floor_date`, `a3_*_payment_evidence_method`, `rl_a3_*_payment_evidence_method`, `model_id`, `crx_persona` (RL strong negatives), `crx_persona.persona_end_date` | — |
| workplace modules (not mirrored) | CC `_signals_common.py` | `nodes.features.dcore._feat_dcore_utils` (`instalment_amount_flags`, `null_cancelled_instalment_fields`), `nodes.utils.config_dcore` (`PTP_INSTALMENT_STATUS_CANCELLED`, `SETTLEMENT_INSTALMENT_STATUS_CANCELLED`) |
| CC A3 from RL A3 | RL `nodes.py`, `constants.py` | `build_a3_commitment_signals`, `build_a3_strong_negative_signals`, `build_a3_payment_credibility`, four `_signals_common` helpers, `_METHOD_SINGLE_PAYMENT_CYCLE_COUNT` |

A refactor of tier L must keep `_common.log_latest_month` (name and signature) and the
schemas of `crx_cc_full_history` / `crx_rl_full_history`, or hand the change to the A3 session.

## 7. Observations for the specialists (behaviour questions, not fixed)

- `cc_a4_deterioration/nodes.py:44-60`: the CC restructure flag reads the earliest row with a
  non-NULL bucket, including out-of-range buckets (`> 9`) that `build_dpd_sequences` rejects
  as invalid. An out-of-range first row marks the account a restructure blind spot (seen in the
  harness: account 12). For S6.
- `computed_at` (`current_timestamp` / `current_date`) in `crx_*_a1_ability`,
  `crx_*_a4_deterioration`, `crx_rl_full_history`: the only non-deterministic columns; the
  harness drops them.
- `_obs_base` drops duplicate grain rows with `dropDuplicates`, so an RL spine row repeated
  with two different `cif_id`s keeps an arbitrary one (CC collapses to the largest first).
  The harness avoids that input. For S6.
