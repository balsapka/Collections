# Inventory (run 2 baseline)

Input commit `ec0c329` (base `4536d52` + D-A3-29), branch `refactor/council_a1_a3`.
Paths are under `workplace_mirror/src/enbd_collections/`. Tiers as in PLAN §2, with the
corrections in §6. Lines and symbols are generated from the tree (`checks/refactor_metrics.py`
holds the tier patterns); per-file quality numbers are in `metrics.md`.

## 1. Totals per tier

| Tier | Files | Lines | Plan says | Note |
|---|---|---|---|---|
| L | 34 (3 empty `__init__.py`) | 3,162 | 3,131 | plan counted at `4536d52`; D-A3-29 added 31 lines (`sources.py` +30, `constants.py` +1) |
| S | 3 | 677 | 677 | |
| A | 3 | 877 | 877 | `feat_cif_casa.py` lines 438–487 not photographed |
| D? | 9 | 923 | 923 | |
| K | 4 | 578 | 578 | does not import in the mirror (§6 C5) |
| X | 54 | 5,492 | — | measured only |

## 2. Files in tiers L, S, A, D?, K

Public symbols = module-level functions, classes and UPPER-case constants without a leading
underscore. Imports = intra-project imports (relative ones resolved). `nodes/primary/cc_way4/prm_cc`,
`nodes/features/dcore/_feat_dcore_utils` and `nodes/utils/config_dcore` are workplace modules the
mirror does not hold.

| File | Tier | Lines | Public symbols | Imports (project) |
|---|---|---|---|---|
| `nodes/features/bureau/feat_cif_bureau_bounces_monthly.py` | L | 43 | `build()` | — |
| `nodes/features/bureau/feat_cif_bureau_salary_monthly.py` | L | 40 | `build()` | nodes/utils/frames |
| `nodes/features/casa/feat_cif_casa.py` | A | 618 | `SIGNAL_REASONS`, `LANES`, `build_internal_salary()`, `build_casa_balance()`, `transaction_lane()`, `build_casa_activity()`, `build_ext_card_payments()`, `build_returns()`, `FLOW_CLASSES`, `MONEY_IN_CLASSES`, `MONEY_OUT_CLASSES`, `WM_SELF_COLUMN`, `WM_SELF_VALUE`, `WM_BANK_COLUMNS`, `WM_LABEL_FLAGS`, `NET_DAYS`, `NET_TOLERANCE`, `flow_class()`, `build_casa_flow_legs()`, `build_casa_flows()` | nodes/utils/frames |
| `nodes/features/casa/feat_cif_casa_flow.py` | A | 159 | `build_casa_scheme_flow()` | nodes/features/casa/feat_cif_casa, nodes/features/casa/feat_cif_windows |
| `nodes/features/products/__init__.py` | L | 0 | — | — |
| `nodes/features/products/feat_cif_cross_product.py` | L | 206 | `PRODUCT_TYPES`, `COLUMNS`, `ASSET_IDS`, `CARD_CURRENT_MAX_LEVEL`, `build()` | nodes/utils/frames |
| `nodes/primary/products/__init__.py` | L | 0 | — | — |
| `nodes/primary/products/prm_products.py` | L | 182 | `BALANCE_TAIL_DAYS`, `LOAD_LAG_DAYS`, `build_card_contracts()`, `build_card_month_end()`, `build_loan_month_end()` | nodes/primary/cc_way4/prm_cc, nodes/utils/frames |
| `nodes/utils/frames.py` | L | 32 | `months_back()`, `require_columns()`, `wm_month()`, `cif_column()` | — |
| `pipelines/bureau/salary_bounces.py` | L | 39 | `create_pipeline()` | nodes/features/bureau |
| `pipelines/casa/features.py` | A | 100 | `create_pipeline()` | nodes/features/casa |
| `pipelines/crx_persona/_common.py` | S | 307 | `LOG`, `GRAIN`, `MODEL_ID_SEGMENT`, `WINDOW_MONTHS`, `GONE_DARK_DAYS`, `segment()`, `window_months()`, `require_columns()`, `string_key()`, `window_start()`, `scoped()`, `pit_latest()`, `window_agg()`, `lookback_floor()`, `left_join_all()`, `log_latest_month()`, `build_cc_obs_base()`, `build_rl_obs_base()`, `dcore_account_events()` | — |
| `pipelines/crx_persona/_dcore_codes.py` | S | 312 | `OUTBOUND_CODES`, `INBOUND_CODES`, `CALL_CODES`, `SUCCESS_CATEGORY`, `RIGHT_PARTY_CONTACT`, `FAILED_CALL`, `SKIP_TRACE`, `IGNORED`, `IGNORED_PREFIX`, `DECEASED`, `REFUSAL`, `DISPUTE`, `HUNG_UP`, `RINGING`, `PROMISE_TO_PAY`, `NOT_REACHABLE`, `RETAIN_PTP`, `PAYMENT_CONFIRMED`, `PROMISE_EVENT`, `PAYMENT_REPORTED` | — |
| `pipelines/crx_persona/_dpd_journey/anchor.py` | S | 58 | `episode_start()` | pipelines/crx_persona/_common |
| `pipelines/crx_persona/_spine_utils.py` | D | 120 | `join_spine_to_spell()`, `rl_spine_as_cc_shim()` | — |
| `pipelines/crx_persona/a1_ability/__init__.py` | L | 19 | — | pipelines/crx_persona/a1_ability/classify, pipelines/crx_persona/a1_ability/signals |
| `pipelines/crx_persona/a1_ability/classify.py` | L | 261 | `MIN_MONTHS`, `STABLE_INCOME_FLOORS`, `INCOME_FLOOR`, `INCOME_ANCHOR_MULT`, `INCOME_MAX_FALL`, `FLOW_FLOOR`, `FLOW_ANCHOR_MULT`, `MONEY_IN_SOME`, `MONEY_OUT_SOME`, `BALANCE_FLOOR`, `BALANCE_ANCHOR_MULT`, `BALANCE_MAX_FALL`, `ASSET_FLOOR`, `ASSET_ANCHOR_MULT`, `INSTALMENT_FLOOR`, `INSTALMENT_ANCHOR_MULT`, `MIN_EVIDENCE_AMT`, `INCOME_POINTS`, `FAMILY_POINTS`, `DISPLAY_NAMES`, `income_level()`, `balance_strong()`, `money_in_level()`, `money_out_level()`, `cross_product_level()`, `FAMILIES`, `SCORECARD`, `build_a1_ability()` | pipelines/crx_persona/_common, pipelines/crx_persona/scoring_engine |
| `pipelines/crx_persona/a1_ability/pipeline.py` | L | 120 | `TAGS`, `create_a1_pipeline()` | pipelines/crx_persona/a1_ability/classify, pipelines/crx_persona/a1_ability/signals |
| `pipelines/crx_persona/a1_ability/signals.py` | L | 455 | `REASON_BUREAU_BOUNCE`, `CASA_HELD_MONTHS`, `EOSB`, `build_income_signals()`, `build_casa_signals()`, `build_cross_product_signals()`, `build_distress_signals()`, `build_eosb_signals()` | nodes/features/casa/feat_cif_casa, nodes/features/products/feat_cif_cross_product, pipelines/crx_persona/_common |
| `pipelines/crx_persona/a3_credibility/__init__.py` | L | 16 | — | pipelines/crx_persona/a3_credibility/classify, pipelines/crx_persona/a3_credibility/pipeline, pipelines/crx_persona/a3_credibility/signals, pipelines/crx_persona/a3_credibility/sources |
| `pipelines/crx_persona/a3_credibility/classify.py` | L | 89 | `OUTPUT_COLUMNS`, `build_a3_credibility()` | pipelines/crx_persona/_common, pipelines/crx_persona/a3_credibility/constants |
| `pipelines/crx_persona/a3_credibility/constants.py` | L | 87 | `COMMITMENT_MONTHS`, `MIN_CONCLUDED`, `KEPT_RATE`, `BROKEN_RATE`, `BROKEN_STREAK`, `FOLLOWUP_RUN_DAYS`, `MATCH_DAYS`, `DEADLINES`, `PROMISE_DEADLINE`, `STATEMENT_FALLBACK_D`, `promise_deadline()`, `QUALIFYING_SHARE`, `MIN_PAYMENT_AED`, `REGULAR_FROM`, `ANY_PAYMENT_MONTHS`, `PRE_DLQ_MONTHS`, `PRE_DLQ_MIN_MONTHS_DUE`, `CLEAN_SHARE`, `DCORE_MAX_MONTHS`, `NO_PICKUP_NAMES`, `CYCLE_MAX_DAYS`, `FLOOR_LOOKBACK_DAYS`, `BUCKET08_BASELINE_MONTHS`, `DISPLAY_NAMES`, `COMMITMENT_POINTS`, `DLQ_PAYMENT_POINTS`, `PRE_DLQ_POINTS`, `SCORECARD` | pipelines/crx_persona/_common, pipelines/crx_persona/scoring_engine |
| `pipelines/crx_persona/a3_credibility/pipeline.py` | L | 145 | `TAGS`, `LEDGER`, `create_a3_pipeline()` | pipelines/crx_persona/a3_credibility/classify, pipelines/crx_persona/a3_credibility/signals, pipelines/crx_persona/a3_credibility/sources |
| `pipelines/crx_persona/a3_credibility/signals.py` | L | 414 | `build_commitment_signals()`, `build_dlq_payment_signals()`, `build_pre_dlq_payment_signals()`, `build_contact_signals()` | pipelines/crx_persona/_common, pipelines/crx_persona/a3_credibility/constants, pipelines/crx_persona:_dcore_codes |
| `pipelines/crx_persona/a3_credibility/sources.py` | L | 372 | `DUES`, `PAYMENTS`, `build_a3_episode()`, `build_cycle_ledger()`, `build_instalments()`, `EVENTS`, `build_promise_events()` | nodes/features/dcore/_feat_dcore_utils, nodes/utils/config_dcore, pipelines/crx_persona/_common, pipelines/crx_persona/_dpd_journey/anchor, pipelines/crx_persona/a3_credibility/constants, pipelines/crx_persona:_dcore_codes |
| `pipelines/crx_persona/cc_a1_ability/__init__.py` | L | 5 | — | pipelines/crx_persona/cc_a1_ability/pipeline |
| `pipelines/crx_persona/cc_a1_ability/nodes.py` | L | 54 | `build_cc_liquidity_anchor()` | pipelines/crx_persona/_common |
| `pipelines/crx_persona/cc_a1_ability/pipeline.py` | L | 33 | `create_pipeline()` | pipelines/crx_persona/a1_ability/pipeline, pipelines/crx_persona/cc_a1_ability/nodes |
| `pipelines/crx_persona/cc_a3_payment_credibility/__init__.py` | L | 5 | — | pipelines/crx_persona/cc_a3_payment_credibility/pipeline |
| `pipelines/crx_persona/cc_a3_payment_credibility/nodes.py` | L | 130 | `build_cc_a3_dues()`, `build_cc_a3_payments()` | pipelines/crx_persona/_common, pipelines/crx_persona/a3_credibility/constants |
| `pipelines/crx_persona/cc_a3_payment_credibility/pipeline.py` | L | 40 | `DUES`, `PAYMENTS`, `create_pipeline()` | pipelines/crx_persona/a3_credibility/pipeline, pipelines/crx_persona/cc_a3_payment_credibility/nodes |
| `pipelines/crx_persona/cc_raw_extract/__init__.py` | K | 14 | — | pipelines/crx_persona/cc_raw_extract/pipeline |
| `pipelines/crx_persona/cc_raw_extract/_window_utils.py` | K | 56 | `prune_by_edp_load_date()`, `scope_to_acct_window()` | nodes/utils/config |
| `pipelines/crx_persona/cc_raw_extract/nodes.py` | K | 436 | `build_cc_acct_windows()`, `build_cc_transactions()`, `build_cc_limits()`, `build_cc_balance()`, `build_cc_billing()` | nodes/primary/cc_way4/prm_cc, nodes/utils/config, pipelines/crx_persona/_dpd_journey/anchor, pipelines/crx_persona/cc_raw_extract/_window_utils |
| `pipelines/crx_persona/cc_raw_extract/pipeline.py` | K | 72 | `create_pipeline()` | pipelines/crx_persona/cc_raw_extract/nodes |
| `pipelines/crx_persona/cc_spell/nodes.py` | D | 237 | `LOG`, `build_cc_spell_table()` | — |
| `pipelines/crx_persona/cc_spell/pipeline.py` | D | 30 | `create_pipeline()` | pipelines/crx_persona/cc_spell/nodes |
| `pipelines/crx_persona/rl_a1_ability/__init__.py` | L | 5 | — | pipelines/crx_persona/rl_a1_ability/pipeline |
| `pipelines/crx_persona/rl_a1_ability/nodes.py` | L | 44 | `build_rl_liquidity_anchor()` | pipelines/crx_persona/_common |
| `pipelines/crx_persona/rl_a1_ability/pipeline.py` | L | 29 | `create_pipeline()` | pipelines/crx_persona/a1_ability/pipeline, pipelines/crx_persona/rl_a1_ability/nodes |
| `pipelines/crx_persona/rl_a3_payment_credibility/__init__.py` | L | 5 | — | pipelines/crx_persona/rl_a3_payment_credibility/pipeline |
| `pipelines/crx_persona/rl_a3_payment_credibility/nodes.py` | L | 60 | `build_rl_a3_dues()`, `build_rl_a3_payments()` | pipelines/crx_persona/_common |
| `pipelines/crx_persona/rl_a3_payment_credibility/pipeline.py` | L | 36 | `DUES`, `PAYMENTS`, `create_pipeline()` | pipelines/crx_persona/a3_credibility/pipeline, pipelines/crx_persona/rl_a3_payment_credibility/nodes |
| `pipelines/crx_persona/rl_a4_spine/__init__.py` | D | 9 | — | pipelines/crx_persona/rl_a4_spine/pipeline |
| `pipelines/crx_persona/rl_a4_spine/nodes.py` | D | 89 | `LOG`, `build_rl_depart_spine()` | — |
| `pipelines/crx_persona/rl_a4_spine/pipeline.py` | D | 35 | `create_pipeline()` | pipelines/crx_persona/rl_a4_spine/nodes |
| `pipelines/crx_persona/rl_spell_table/__init__.py` | D | 5 | — | pipelines/crx_persona/rl_spell_table/pipeline |
| `pipelines/crx_persona/rl_spell_table/nodes.py` | D | 366 | `LOG`, `build_rl_spell_table()` | — |
| `pipelines/crx_persona/rl_spell_table/pipeline.py` | D | 32 | `create_pipeline()` | pipelines/crx_persona/rl_spell_table/nodes |
| `pipelines/crx_persona/scoring_engine.py` | L | 108 | `RUNGS`, `Dimension`, `Override`, `Scorecard`, `state_label()` | — |
| `pipelines/products/__init__.py` | L | 0 | — | — |
| `pipelines/products/features.py` | L | 36 | `create_pipeline()` | nodes/features/products |
| `pipelines/products/primary.py` | L | 52 | `create_pipeline()` | nodes/primary/products |

## 3. Import graph (who reads whom)

```
scoring_engine ◄── a1_ability/classify, a3_credibility/constants, a2_locatability/classify (state_label)
_common        ◄── a1_ability/{classify,signals}, a3_credibility/{classify,constants,signals,sources},
                   cc_a1_ability/nodes, rl_a1_ability/nodes, cc_a3_*/nodes, rl_a3_*/nodes,
                   _dpd_journey/{anchor,__init__,logging,params,spark}, a2_locatability/{classify,signals},
                   cc_a4_deterioration/nodes, rl_a4_deterioration/nodes, cc_full_history/nodes,
                   rl_full_history/nodes, cc_raw_extract/nodes, obs_base/pipeline
_dcore_codes   ◄── a3_credibility/{signals,sources}, a2_locatability/signals
_dpd_journey/anchor.episode_start ◄── a3_credibility/sources, cc_raw_extract/nodes, _dpd_journey/__init__
a1_ability/pipeline ◄── cc_a1_ability/pipeline, rl_a1_ability/pipeline (TAGS, create_a1_pipeline)
a3_credibility/pipeline ◄── cc_a3_*/pipeline, rl_a3_*/pipeline (TAGS, create_a3_pipeline)
a3_credibility/constants ◄── cc_a3_payment_credibility/nodes (BUCKET08_BASELINE_MONTHS, CYCLE_MAX_DAYS,
                             FLOOR_LOOKBACK_DAYS)
nodes/utils/frames ◄── feat_cif_cross_product, prm_products, feat_cif_bureau_salary_monthly,
                       feat_cif_casa (tier A)
nodes/features/casa/feat_cif_casa (A) ◄── a1_ability/signals (MONEY_IN_CLASSES, MONEY_OUT_CLASSES),
                       feat_cif_casa_flow (A: _cif, _require), feat_cif_windows (X, workplace: _cif,
                       _require, _wm_month), pipelines/casa/features (A)
nodes/features/products/feat_cif_cross_product ◄── a1_ability/signals (COLUMNS), pipelines/products/features
nodes/primary/products/prm_products ◄── pipelines/products/primary
nodes/features/bureau/feat_cif_bureau_{salary,bounces}_monthly ◄── pipelines/bureau/salary_bounces
cc_spell, rl_spell_table, rl_a4_spine ◄── pipeline_registry only
_spine_utils   ◄── nothing
```

The registry imports every crx package (§5). `cc_a4_deterioration`, `cc_full_history`,
`cc_spell` and `pipelines/digital_login` have no `__init__.py` in the mirror (namespace packages);
the smoke gate reads their `pipeline.py`.

## 4. Datasets per pipeline (node inputs → outputs)

From `python checks/refactor_smoke.py --io` (mirror registry). `crx_cc_raw_extract` is listed
from its `pipeline.py` because the package does not import in the mirror (§6 C5).

### crx_cc_raw_extract (from pipeline.py)
- `build_crx_cc_acct_windows`: crx_cc_obs_base, crx_cc_a4_deterioration, params:cc_a3_history_floor_date -> crx_cc_acct_windows
- `build_crx_cc_transactions`: raw_transaction, crx_cc_acct_windows -> crx_cc_transactions
- `build_crx_cc_limits`: raw_stg_limit, crx_cc_spell_table -> crx_cc_limits
- `build_crx_cc_balance`: raw_stg_balance, raw_stg_account_group, crx_cc_acct_windows -> crx_cc_balance
- `build_crx_cc_billing`: raw_stg_billing, crx_cc_acct_windows -> crx_cc_billing

### bureau_salary_bounces
- `build_feat_cif_bureau_bounces_monthly`: prm_bureau_alert_enriched -> feat_cif_bureau_bounces_monthly
- `build_feat_cif_bureau_salary_monthly`: feat_bureau_salary_unified -> feat_cif_bureau_salary_monthly

### casa_features
- `build_feat_cif_casa_activity_monthly`: prm_casa_transactions, prm_casa_accounts -> feat_cif_casa_activity_monthly
- `build_feat_cif_casa_balance_monthly`: wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow, params:crx_persona.persona_start_date, params:casa_features.history_months -> feat_cif_casa_balance_monthly
- `build_feat_cif_ext_card_payment_monthly`: wm_pri_labelled_transactions, prm_beneficiary_cards, params:crx_persona.persona_start_date, params:casa_features.history_months -> feat_cif_ext_card_payment_monthly
- `build_feat_cif_internal_salary_monthly`: wm_fea_salary_days_since_increment -> feat_cif_internal_salary_monthly
- `build_feat_cif_returns_monthly`: prm_casa_return_events, prm_casa_accounts -> feat_cif_returns_monthly
- `build_prm_casa_flow_legs`: prm_casa_transactions, prm_casa_accounts, wm_pri_labelled_transactions, params:crx_persona.persona_start_date, params:casa_features.history_months -> prm_casa_flow_legs
- `build_feat_cif_casa_flows_monthly`: prm_casa_flow_legs -> feat_cif_casa_flows_monthly

### casa_primary
- `build_prm_beneficiary_cards`: raw_beneficiary_cards -> prm_beneficiary_cards
- `build_prm_casa_accounts`: raw_casa_acid_to_cif, params:casa_primary.current_account_codes, params:casa_primary.saving_account_codes -> prm_casa_accounts
- `build_prm_casa_card_transactions`: comp_financial_tran_repos_dly, params:crx_persona.persona_start_date, params:casa_primary.card_history_months -> prm_casa_card_transactions
- `build_prm_casa_return_events`: comp_financial_tran_repos_dly, params:casa_primary.return_reasons, params:crx_persona.persona_start_date, params:casa_primary.history_months -> prm_casa_return_events
- `build_prm_casa_transactions`: comp_financial_tran_repos_dly, params:crx_persona.persona_start_date, params:casa_primary.transaction_history_months -> prm_casa_transactions

### crx_cc_a1_ability
- `build_crx_cc_a1_casa_signals`: crx_cc_obs_base, feat_cif_casa_balance_monthly, feat_cif_casa_flows_monthly, params:model_id, params:crx_persona -> crx_cc_a1_casa_signals
- `build_crx_cc_a1_cross_product_signals`: crx_cc_obs_base, feat_cif_cross_product_monthly -> crx_cc_a1_cross_product_signals
- `build_crx_cc_a1_distress_signals`: crx_cc_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_cc_a1_distress_signals
- `build_crx_cc_a1_eosb_signals`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_cc_a1_eosb_signals
- `build_crx_cc_a1_income_signals`: crx_cc_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id -> crx_cc_a1_income_signals
- `build_crx_cc_a1_liquidity_anchor`: crx_cc_obs_base, prm_balance, params:model_id -> crx_cc_a1_liquidity_anchor
- `build_crx_cc_a1_ability`: crx_cc_obs_base, crx_cc_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date, crx_cc_a1_income_signals, crx_cc_a1_casa_signals, crx_cc_a1_cross_product_signals, crx_cc_a1_distress_signals, crx_cc_a1_eosb_signals -> crx_cc_a1_ability

### crx_cc_a2_locatability
- `build_crx_cc_a2_dcore_signals`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_cc_a2_dcore_signals
- `build_crx_cc_a2_demographics_deceased`: crx_cc_obs_base, feat_demographics_cif -> crx_cc_a2_demographics_deceased
- `build_crx_cc_a2_location_signals`: crx_cc_obs_base, feat_cif_location_monthly, params:model_id -> crx_cc_a2_location_signals
- `build_crx_cc_a2_way4_deceased`: crx_cc_obs_base, prm_contract, prm_client -> crx_cc_a2_way4_deceased
- `build_crx_cc_a2_locatability`: crx_cc_obs_base, crx_cc_a2_location_signals, crx_cc_a2_dcore_signals, crx_cc_a2_way4_deceased, crx_cc_a2_demographics_deceased, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a2_locatability

### crx_cc_a3_payment_credibility
- `build_crx_cc_a3_dues`: crx_cc_billing, crx_cc_balance, params:cc_a3_history_floor_date -> crx_cc_a3_dues
- `build_crx_cc_a3_episode`: crx_cc_obs_base, crx_cc_a4_deterioration -> crx_cc_a3_episode
- `build_crx_cc_a3_instalments`: crx_cc_obs_base, prm_dcore_account_agreements, dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement, dcore_prm_settlement_schedule_instalments -> crx_cc_a3_instalments
- `build_crx_cc_a3_payments`: crx_cc_transactions -> crx_cc_a3_payments
- `build_crx_cc_a3_contact_signals`: crx_cc_a3_episode, dcore_prm_followup_outcomes, prm_dcore_account_agreements, crx_cc_a3_instalments, crx_cc_a3_payments, crx_cc_a3_dues, params:model_id -> crx_cc_a3_strong_negative_signals
- `build_crx_cc_a3_payment_cycles`: crx_cc_a3_dues, crx_cc_a3_payments -> crx_cc_a3_payment_cycles
- `build_crx_cc_a3_promise_events`: crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, crx_cc_a3_instalments, crx_cc_a3_dues, crx_cc_a3_payments, params:model_id -> crx_cc_a3_promise_events
- `build_crx_cc_a3_commitment_signals`: crx_cc_a3_episode, crx_cc_a3_promise_events -> crx_cc_a3_commitment_signals
- `build_crx_cc_a3_dlq_payment_signals`: crx_cc_a3_episode, crx_cc_a3_payment_cycles, params:model_id -> crx_cc_a3_dlq_payment_signals_single_payment_cycle_count
- `build_crx_cc_a3_pre_dlq_payment_signals`: crx_cc_a3_episode, crx_cc_a3_payment_cycles -> crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count
- `build_crx_cc_a3_payment_credibility`: crx_cc_a3_episode, crx_cc_a3_commitment_signals, crx_cc_a3_dlq_payment_signals_single_payment_cycle_count, crx_cc_a3_pre_dlq_payment_signals_single_payment_cycle_count, crx_cc_a3_strong_negative_signals, params:model_id, params:crx_persona.persona_end_date -> crx_cc_a3_payment_credibility

### crx_cc_a4_deterioration
- `build_crx_cc_dpd_sequences`: crx_cc_full_history, params:crx_persona, params:model_id -> crx_cc_dpd_sequences
- `build_crx_cc_a4_deterioration`: crx_cc_dpd_sequences, cc_spine, params:crx_persona, params:model_id -> crx_cc_a4_deterioration

### crx_cc_full_history
- `build_crx_cc_full_history`: raw_stg_billing, cc_spine -> crx_cc_full_history

### crx_cc_obs_base
- `build_crx_cc_obs_base`: cc_spine, params:crx_persona -> crx_cc_obs_base

### crx_cc_spell_table
- `build_crx_cc_spell_table`: raw_stg_billing, cc_spine -> crx_cc_spell_table

### crx_rl_a1_ability
- `build_crx_rl_a1_casa_signals`: crx_rl_obs_base, feat_cif_casa_balance_monthly, feat_cif_casa_flows_monthly, params:model_id, params:crx_persona -> crx_rl_a1_casa_signals
- `build_crx_rl_a1_cross_product_signals`: crx_rl_obs_base, feat_cif_cross_product_monthly -> crx_rl_a1_cross_product_signals
- `build_crx_rl_a1_distress_signals`: crx_rl_obs_base, feat_cif_returns_monthly, feat_cif_bureau_bounces_monthly, params:model_id -> crx_rl_a1_distress_signals
- `build_crx_rl_a1_eosb_signals`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_rl_a1_eosb_signals
- `build_crx_rl_a1_income_signals`: crx_rl_obs_base, feat_cif_internal_salary_monthly, feat_cif_bureau_salary_monthly, params:model_id -> crx_rl_a1_income_signals
- `build_crx_rl_a1_liquidity_anchor`: crx_rl_obs_base, int_loan_master -> crx_rl_a1_liquidity_anchor
- `build_crx_rl_a1_ability`: crx_rl_obs_base, crx_rl_a1_liquidity_anchor, params:model_id, params:crx_persona.persona_end_date, crx_rl_a1_income_signals, crx_rl_a1_casa_signals, crx_rl_a1_cross_product_signals, crx_rl_a1_distress_signals, crx_rl_a1_eosb_signals -> crx_rl_a1_ability

### crx_rl_a2_locatability
- `build_crx_rl_a2_dcore_signals`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:model_id -> crx_rl_a2_dcore_signals
- `build_crx_rl_a2_demographics_deceased`: crx_rl_obs_base, feat_demographics_cif -> crx_rl_a2_demographics_deceased
- `build_crx_rl_a2_location_signals`: crx_rl_obs_base, feat_cif_location_monthly, params:model_id -> crx_rl_a2_location_signals
- `build_crx_rl_a2_way4_deceased`: crx_rl_obs_base, prm_contract, prm_client -> crx_rl_a2_way4_deceased
- `build_crx_rl_a2_locatability`: crx_rl_obs_base, crx_rl_a2_location_signals, crx_rl_a2_dcore_signals, crx_rl_a2_way4_deceased, crx_rl_a2_demographics_deceased, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a2_locatability

### crx_rl_a3_payment_credibility
- `build_crx_rl_a3_dues`: int_loan_master, crx_rl_obs_base -> crx_rl_a3_dues
- `build_crx_rl_a3_episode`: crx_rl_obs_base, crx_rl_a4_deterioration -> crx_rl_a3_episode
- `build_crx_rl_a3_instalments`: crx_rl_obs_base, prm_dcore_account_agreements, dcore_int_ptp, dcore_prm_promise_instalments, dcore_int_settlement, dcore_prm_settlement_schedule_instalments -> crx_rl_a3_instalments
- `build_crx_rl_a3_payments`: int_loan_master, crx_rl_obs_base -> crx_rl_a3_payments
- `build_crx_rl_a3_contact_signals`: crx_rl_a3_episode, dcore_prm_followup_outcomes, prm_dcore_account_agreements, crx_rl_a3_instalments, crx_rl_a3_payments, crx_rl_a3_dues, params:model_id -> crx_rl_a3_strong_negative_signals
- `build_crx_rl_a3_dlq_cycles`: crx_rl_a3_dues, crx_rl_a3_payments -> crx_rl_a3_dlq_cycles
- `build_crx_rl_a3_promise_events`: crx_rl_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements, crx_rl_a3_instalments, crx_rl_a3_dues, crx_rl_a3_payments, params:model_id -> crx_rl_a3_promise_events
- `build_crx_rl_a3_commitment_signals`: crx_rl_a3_episode, crx_rl_a3_promise_events -> crx_rl_a3_commitment_signals
- `build_crx_rl_a3_dlq_payment_signals`: crx_rl_a3_episode, crx_rl_a3_dlq_cycles, params:model_id -> crx_rl_a3_dlq_payment_signals_single_payment_cycle_count
- `build_crx_rl_a3_pre_dlq_payment_signals`: crx_rl_a3_episode, crx_rl_a3_dlq_cycles -> crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count
- `build_crx_rl_a3_payment_credibility`: crx_rl_a3_episode, crx_rl_a3_commitment_signals, crx_rl_a3_dlq_payment_signals_single_payment_cycle_count, crx_rl_a3_pre_dlq_payment_signals_single_payment_cycle_count, crx_rl_a3_strong_negative_signals, params:model_id, params:crx_persona.persona_end_date -> crx_rl_a3_payment_credibility

### crx_rl_a4_deterioration
- `build_crx_rl_dpd_sequences`: crx_rl_full_history, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences
- `build_crx_rl_full_history_linked`: crx_rl_full_history, int_loan_master, int_loan_restructure_link -> crx_rl_full_history_linked, crx_rl_restructure_chains
- `build_crx_rl_dpd_sequences_linked`: crx_rl_full_history_linked, crx_rl_restructure_chains, feature_retail_loans, params:crx_persona, params:model_id -> crx_rl_dpd_sequences_linked
- `build_crx_rl_a4_deterioration`: crx_rl_dpd_sequences, crx_rl_dpd_sequences_linked, crx_rl_restructure_chains, rl_spine, params:crx_persona, params:model_id -> crx_rl_a4_deterioration

### crx_rl_a4_spine
- `build_crx_rl_a4_spine`: rl_spine, crx_rl_spell_table, params:crx_persona -> crx_rl_a4_spine

### crx_rl_full_history
- `build_crx_rl_full_history`: rl_spine, int_loan_master, params:crx_persona -> crx_rl_full_history

### crx_rl_obs_base
- `build_crx_rl_obs_base`: rl_spine, params:crx_persona -> crx_rl_obs_base

### crx_rl_spell_table
- `build_crx_rl_spell_table`: crx_rl_full_history, rl_spine -> crx_rl_spell_table

### digital_login
- `build_stg_digital_login`: raw_digital_login_data, raw_digital_login_data_history, raw_digital_user_data -> stg_digital_login
- `build_prm_digital_login_monthly`: stg_digital_login -> prm_digital_login_monthly

### location_features
- `build_prm_dcore_account_agreements`: dcore_observation_spine -> prm_dcore_account_agreements
- `build_feat_cif_location_monthly`: prm_digital_login_monthly, prm_casa_card_transactions, prm_transaction, prm_contract, prm_client, dcore_prm_followup_outcomes, prm_dcore_account_agreements, params:crx_persona.persona_start_date, params:location_features.history_months -> feat_cif_location_monthly

### product_features
- `build_feat_cif_cross_product_monthly`: prm_card_contracts, prm_card_month_end, prm_loan_month_end, wm_fea_casa_eod_avg_balance, wm_fea_wealth_holdings_by_cif, params:crx_persona.persona_start_date, params:products.history_months -> feat_cif_cross_product_monthly

### product_primary
- `build_prm_card_contracts`: raw_stg_client, raw_stg_contract -> prm_card_contracts
- `build_prm_card_month_end`: raw_stg_billing, raw_stg_balance, raw_stg_account_group, params:crx_persona.persona_start_date, params:products.history_months -> prm_card_month_end
- `build_prm_loan_month_end`: bo_rr_portf_actv_acct_mthly, params:crx_persona.persona_start_date, params:products.history_months -> prm_loan_month_end

Memory-only node outputs (not in the mirror's catalog; the workplace catalog after line 289 was
not photographed, so whether it persists them is unknown): `crx_<p>_a3_dues`, `crx_<p>_a3_payments`,
`crx_cc_a3_payment_cycles`, `crx_rl_a3_dlq_cycles`, `crx_<p>_a3_dlq_payment_signals_single_payment_cycle_count`,
`crx_<p>_a3_pre_dlq_payment_signals_single_payment_cycle_count`, `crx_<p>_a3_strong_negative_signals`
(the last four names are the workplace catalog's, `a3_credibility/pipeline.py` `LEDGER`), plus
`stg_digital_login` / `prm_digital_login_monthly` (digital_login, tier X).

### Run order for one model_id (A1 / A3)

```
casa_primary → casa_features ┐          product_primary → product_features ┐
bureau_staging/primary (DE) → bureau_salary_bounces ┐                       │
location_features (prm_dcore_account_agreements) ───┼───────────────────────┼─► crx_<p>_a1_ability
crx_<p>_obs_base ───────────────────────────────────┘                       │
crx_<p>_obs_base + crx_<p>_full_history → crx_<p>_a4_deterioration ─┬─► crx_cc_raw_extract (CC) ─┐
                                                                    └──────────────────────────────┴─► crx_<p>_a3_payment_credibility
```

## 5. Shared-code dependencies of tiers A and K

- **A `feat_cif_casa.py`** imports `nodes/utils/frames` (tier L: `cif_column`, `months_back`,
  `require_columns`, `wm_month`). It exports `MONEY_IN_CLASSES` / `MONEY_OUT_CLASSES` to A1
  (`a1_ability/signals.py`), and the private `_cif`, `_require`, `_wm_month` to
  `feat_cif_casa_flow.py` (A) and `feat_cif_windows.py` (X, workplace module). A rename of any of
  these breaks imports (hard rule 9 names `_cif` / `_require`; `_wm_month` is a third).
  Changing `frames.py` signatures touches tier A behaviour.
- **A `feat_cif_casa_flow.py`** imports `feat_cif_casa` and `feat_cif_windows` (X).
- **A `pipelines/casa/features.py`** builds `prm_casa_flow_legs`, `feat_cif_casa_flows_monthly`,
  `feat_cif_casa_balance_monthly`, `feat_cif_internal_salary_monthly`, `feat_cif_returns_monthly`
  (read by A1) and `feat_cif_casa_activity_monthly`, `feat_cif_ext_card_payment_monthly` (read by
  no persona node in the mirror; outputs of `casa_features`).
- **K `cc_raw_extract`** imports `_dpd_journey/anchor.episode_start` (S), `nodes/utils/config`
  (`POST_BLOCK_X_SENTINEL_DATE`, `TXN_CATEGORIES`, `EDP_LOAD_DATE_BUFFER_MONTHS` — the last is
  missing from the mirror's `config.py`), and the unmirrored `prm_cc.derive_billing_amounts` /
  `derive_overdue_buckets` (also used by `prm_products`, tier L). It reads `crx_cc_spell_table`
  (D?) in `build_cc_limits`.

## 6. Tier D? candidates: does anything live consume them?

Evidence collected on the mirror at `ec0c329`: `grep` over `src/` and `conf/` for the module
names, the dataset names and every public function; the node inputs of all 23 registered
pipelines the smoke gate builds (§4); `checks/` and `tools/`; and the workplace excerpts in
`bundle_helpers/a3_final/workplace_reference.md` / `a1_final/workplace_reference.md`.

| Candidate | Produces | Python importers | Node consumers of its output | Registry | Verdict |
|---|---|---|---|---|---|
| `_spine_utils.py` (120) | — (`join_spine_to_spell`, `rl_spine_as_cc_shim`, `_build_cif_bridge`) | **none** | — | — | **dead** |
| `rl_a4_spine/` (133) | `crx_rl_a4_spine` | registry only (line 100) | **none** in any pipeline | `crx_rl_a4_spine` (mirror 251, workplace 248) | **dead** (pipeline + registry entry + catalog entry `catalog_crx.yml:294`) |
| `rl_spell_table/` (403) | `crx_rl_spell_table` | registry only (line 98) | `crx_rl_a4_spine` pipeline only (dead) | `crx_rl_spell_table` (250) | **dead with `rl_a4_spine`** (catalog `:281`) |
| `cc_spell/` (267) | `crx_cc_spell_table` | registry only (line 75) | **`crx_cc_raw_extract.build_crx_cc_limits` (tier K)**, which writes `crx_cc_limits`; `crx_cc_limits` has **no** reader | `crx_cc_spell_table` (238) | **dead only together with `build_cc_limits`**, the `crx_cc_limits` node and catalog entry (`catalog_crx.yml:36`) in tier K. Deleting `cc_spell` alone leaves `crx_cc_raw_extract` reading a stale persisted `crx_cc_spell_table` (or failing once its HDFS folder is removed). |

Text-only references that a deletion should also clean: `cc_a4_deterioration/nodes.py:23`
(comment naming `cc_spell`'s threshold), `catalog_crx.yml:269` and `:280`, `:292` (comments),
`parameters_crx_persona.yml:6` (comment), `cc_raw_extract/nodes.py` and `__init__.py` docstrings
(spell / T0 window of `build_cc_limits`), DESIGN_REVIEW §6 D5 already lists them for removal.

**What the mirror cannot prove.** `pipeline_registry.py` lines 54–130 and 180+ were never
photographed (the workplace reference confirms lines 213–270 only, plus that
`crx_cc_raw_extract`, `crx_cc_full_history` and `crx_rl_a4_spine` are still registered). Those
regions hold imports of other domains and the model-variant entries; a workplace-only pipeline
reading `crx_cc_spell_table`, `crx_rl_spell_table`, `crx_rl_a4_spine` or `crx_cc_limits` there,
in the unmirrored domains (credit_card_way4, retail_loans, model_input, genesys, validation …),
in notebooks or in `src/tests/` cannot be excluded from the mirror. The earlier R4 grep
(2026-10-27) covered the departure / trajectory / utilisation pipelines only. **Closing step for
U0:** ask the UAT Sonnet for `grep -rn "spell_table\|a4_spine\|crx_cc_limits\|_spine_utils\|cc_spell\|rl_spell_table\|build_rl_depart_spine\|join_spine_to_spell" src conf notebooks`
in the workplace repo and paste the output, as R4 was done.

## 7. Corrections to the plan

- **C1 (§2 L lines)** 3,162 lines in 34 files at the input commit, not 3,131 (D-A3-29 added 31).
- **C2 (§2 L, scoring_engine)** "only A1 and A3 use it" is wrong: `a2_locatability/classify.py`
  imports `state_label`. A change to `state_label` touches A2 (the oracle covers A2).
- **C3 (§2 D?)** `cc_spell/` is not dead on its own: tier K `build_cc_limits` reads
  `crx_cc_spell_table`. The dead unit is `cc_spell` + `build_cc_limits` + `crx_cc_limits`, i.e.
  the deletion edits tier K (allowed under §10 Q2, but it must be on the U0 list). `rl_spell_table`
  is dead only with `rl_a4_spine`.
- **C4 (§2 L ↔ A)** tier L `a1_ability/signals.py` imports `MONEY_IN_CLASSES` /
  `MONEY_OUT_CLASSES` from tier A `feat_cif_casa.py`; moving or renaming them needs a CASA
  handoff. Hard rule 9 should also name `_wm_month` (imported by `feat_cif_windows.py`).
- **C5 (§2 K, §6 gate 5)** `cc_raw_extract` does not import in the mirror: the mirror's
  `nodes/utils/config.py` lacks `EDP_LOAD_DATE_BUFFER_MONTHS` (transcribed before the workplace
  added it). Smoke baseline failure; the oracle sets it to 12 (the value its docstrings state).
  Photograph the constant to close it.
- **C6 (§2 L)** `prm_products.py` (L) and `cc_raw_extract/nodes.py` (K) import the unmirrored
  `nodes/primary/cc_way4/prm_cc.derive_billing_amounts` (K also `derive_overdue_buckets`); the
  oracle uses a stand-in, so the minimum-due / bucket derivation itself is not under test.
  `a3_credibility/sources.py` imports two unmirrored DCORE helpers (stubbed as in the A3 spec test).
- **C7 (§2 L, catalog)** the A3 ledger and signal datasets named after the workplace catalog
  (§4, 12 names) are not in the mirror's `catalog_crx.yml`; "their entries in catalog_crx.yml"
  covers only the persisted five per product. Compare with the workplace catalog before any
  rename (hard rule 5).
- **C8 (§2 L)** `a1_ability/README.md` exists (not counted as code; the docstring pass should
  keep it in line).
- **C9 (§5 oracle)** `casa_features` is not run (unphotographed lines); A1 reads feature tables
  built by the A1 spec test's calls to the CASA builders (see `harness_coverage.md`).

## 8. Observations for S6 (seen while building the oracle; not changed)

- **RL refusal and same-month cash.** RL cash is dated `pay_from` = the 1st of the month,
  and `_paid_after_refusal` needs `pay_from > last_rpc_date`. A payment in the month of the
  refusal therefore never lifts it, even when it came after the refusal day (oracle case
  "refusal, then 150 AED in one cycle": CC not a refusal, RL still a refusal). Possibly
  intended (cash known only to the month); worth a line in the spec either way.
- **Promise deadline fallback.** A promise after the last statement with a successor (CC,
  next statement) is judged at day + 31 (`STATEMENT_FALLBACK_D`); in the oracle that promise
  is not concluded at the observation date, so it never counts. Matches the constant's
  comment.
