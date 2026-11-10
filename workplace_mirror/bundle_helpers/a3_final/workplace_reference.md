# A3 workplace reference: catalog and registry excerpts (handoff 34, 2026-11-03)

Partial files, so not under `conf/` or `src/` (same convention as `a1_final/workplace_reference.md`).
Photos IMG_8734 (registry), IMG_8736–8741 (`catalog_crx.yml` 1–289), IMG_8742–8748
(`catalog_outputs.yml`), IMG_8749 (`catalog_raw_way4.yml`). IMG_8735 was not in the batch.

## `conf/base/catalog/catalog_crx.yml`, lines 14–78 (verbatim)

Lines 1–12 (file header) equal the mirror's. The mirror copy (634 lines) predates the DE's A3 work:
it has no `crx_cc_acct_windows` or `crx_cc_billing`, and its `crx_cc_balance` comment is the old one.

```yaml
# -- T04c: T0-scoped CC raw DDI intermediates ---------------------------------
# Grain: (contract_id, observation_date) — one row per account per date.
# Built by crx_cc_raw_extract pipeline (T04c). Consumed by T04b, T05, T06.
# Replaces prm_transaction / prm_limit / prm_balance primary-layer inputs,
# which are spine-scoped and lack history for cc_180_plus T0 windows.

# Grain: (account_id). Shared per-account [acct_start, acct_end] window,
# forward edge anchored to cc_spine — computed once and consumed by
# build_cc_transactions / build_cc_balance / build_cc_billing below instead of
# each recomputing the same crx_cc_spell_table/cc_spine aggregation.
crx_cc_acct_windows:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_acct_windows"
  save_args:
    mode: overwrite

crx_cc_transactions:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_transactions"
  save_args:
    mode: overwrite

crx_cc_limits:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_limits"
  save_args:
    mode: overwrite

# Carries minimum_due/stmt_balance/total_due plus overdue_bucket_01..08 (from
# prm_cc.derive_billing_amounts/derive_overdue_buckets) - the overdue buckets
# feed A3 Dimension B/C's due-amount resolution
# (cc_a3_payment_credibility._signals_common.resolve_due_amount_m) since
# minimum_due alone goes to an explicit 0 at deep DLQ.
crx_cc_balance:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_balance"
  save_args:
    mode: overwrite

# Grain: (contract_id, observation_date) - one row per billing cycle per account.
# Carries due_date and next_billing_date (F.lead(billing_date) per contract) - the
# cycle-attribution primitive A3 Dimension B/C's payment-attribution helper
# (cc_a3_payment_credibility._signals_common.attribute_payments_to_billing_cycles)
# is built on. billing_date < banking_date <= next_billing_date, NOT due_date.
crx_cc_billing:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_billing"
  save_args:
    mode: overwrite

# -- CC Full Billing History (ad hoc, no task card, mirrors RL-B1) -----------
# Grain: (account_id, billing_date) — one row per billing cycle.
# Full history, no date window — built straight from raw_stg_billing (dlq_bucket
# parsed from add_info), leftsemi-scoped to cc_spine.
crx_cc_full_history:
  type: spark.SparkDataset
  file_format: parquet
  filepath: "${_project.hdfs_path}/${globals:model_id}/${globals:folders.persona}/crx/crx_cc_full_history"
  save_args:
    mode: overwrite
```

Lines 80–289, keys only: `crx_cc_spell_table` (85), `crx_cc_dpd_sequences` (104),
`crx_cc_a4_deterioration` (115), `crx_cc_payment_trajectory` (127), `crx_cc_utilisation_features` (142),
`crx_cc_departure_spell_base` (168), `crx_cc_departure_contract_cif` (175), `crx_cc_departure_pass_a`
… `_h`, `_h2`, `_i`, `_j`, `_k` (182–264), `crx_cc_departure_signature` (266), then the CC A2 block
(273: shared `a2_locatability` engine; inputs `crx_cc_obs_base, feat_cif_location_monthly,
dcore_prm_followup_outcomes, prm_dcore_account_agreements, prm_contract, prm_client,
feat_demographics_cif`): `crx_cc_a2_location_signals` (281), `crx_cc_a2_dcore_signals` (288). The
departure passes are still in the workplace catalog. **The A3 entries lie after line 289 and were not
photographed** (`crx_cc_a3_*`, `crx_rl_a3_*`, `crx_rl_a4_spine`).

## `conf/base/catalog/catalog_outputs.yml` (excerpts)

Every entry is `<<: *spark_de` plus a `filepath`.

| Line | Key | Path after `${globals:model_id}/` |
|---|---|---|
| 383 | `int_bureau_pull_monthly` | `${globals:folders.int}/bureau/pull_monthly` |
| 389 | `dcore_int_contact` | `${globals:folders.int}/dcore/contact` |
| 393 | `dcore_int_ptp` | `${globals:folders.int}/dcore/ptp` |
| 397 | `dcore_int_resolution` | `…int}/dcore/resolution` |
| 401 | `dcore_int_settlement` | `…int}/dcore/settlement` |
| 405 / 409 | `dcore_int_legal_action`, `dcore_int_alloc_state` | `…int}/dcore/…` |
| 415 | `int_loan_master` | `${globals:folders.int}/retail_loans/loan_master` |
| 419 / 423 / 427 | `loan_account_cif_map`, `int_loan_restructure_link`, `cif_grid` | `…int}/retail_loans/…` |
| 433 | `int_customer_demographics` | `…int}/demographics/customer_demographics` |
| 438 | `# 04_PRM`, section `# — cc_way4` | |
| 443 | `prm_transaction` | `${globals:folders.prm}/cc_way4/transaction` |
| 447 | `prm_balance` | `…prm}/cc_way4/balance` |
| 451 | `prm_limit` | `…prm}/cc_way4/limit` |
| 455 | `prm_contract` | `…prm}/cc_way4/contract` |
| 459 | `prm_card` | `…prm}/cc_way4/card` |
| 463 | `prm_client` | `…prm}/cc_way4/client` |
| 467 | `prm_product_config` | `…prm}/cc_way4/product_config` |
| 471 | `prm_billing` | `…prm}/cc_way4/billing` |
| 475 / 479 / 483 / 487 | `prm_tariff`, `prm_last_operation`, `prm_turnovers`, `prm_instalment_summary` | `…prm}/cc_way4/…` |
| 531 | (`…prm}/dcore/mail_attempts`, `save_args: mode: overwrite`) | |
| 535–543 | commented out (DEFERRED): `dcore_prm_free_text`, `dcore_prm_system_actions` | |
| 545 | `dcore_prm_customer_responses` | `…prm}/dcore/customer_responses` |
| 549 | `dcore_prm_followup_outcomes` | `…prm}/dcore/followup_outcomes` |
| 553 / 557 / 561 | `dcore_prm_allocation_state`, `dcore_prm_allocation_tracking`, `dcore_prm_log_allocation_tracking` | `…prm}/dcore/…` |
| 565 | `dcore_prm_promise_summary` | `…prm}/dcore/promise_summary` |
| 569 | `dcore_prm_promise_instalments` | `…prm}/dcore/promise_instalments` |
| 573 | `dcore_prm_settlement_summary` | `…prm}/dcore/settlement_summary` |
| 577 | `dcore_prm_rps_waivers` | `…prm}/dcore/rps_waivers` |
| 581 | `dcore_prm_settlement_schedule_instalments` | `…prm}/dcore/settlement_schedule_instalments` |
| 585 | `dcore_prm_atd_call_attempts` | (cut off) |
| 784 / 788 / 792 / 796 | `feat_bureau_pull`, `feat_bureau`, `feat_bureau_snapshot`, `target_cifs_bureau` | `…feat}/bureau/…` |
| 802 | `dcore_feat_contact` | `${globals:folders.feat}/dcore/contact` |
| 806 | `dcore_feat_ptp` | `…feat}/dcore/ptp` |
| 810 / 814 | `dcore_feat_resolution`, `dcore_feat_legal_action` | `…feat}/dcore/…` |
| 818 | `dcore_feat_settlement` | `…feat}/dcore/settlement` |
| 822 | `dcore_feat_alloc_state` | `…feat}/dcore/alloc_state` |
| 826 / 830 / 834 | `dcore_features`, `dcore_agreement_features`, `dcore_cif_features` | `…feat}/dcore/…` |
| 1142 / 1146 / 1150 | `prm_customer_individual`, `prm_customer_address`, `prm_customer_employment` | `…prm}/demographics/…` |
| 1155 / 1159 | `feat_demographics`, `feat_demographics_cif` | `…feat}/demographics/…` |
| 1163 | `# 05_FEAT — data_engineering feature outputs`; `# -- CC observation spine + target variable --` | |
| 1168 | `cc_spine` | `${globals:folders.spine}/cc_way4/cc_spine` |
| 1172 | `cc_cif_obs_spine` | `…spine}/cc_way4/cc_cif_obs_spine` |
| 1176 | `cc_spine_with_target` | `…spine}/cc_way4/cc_spine_with_target` |
| 1182 | `rl_spine` | `…spine}/retail_loans/rl_spine` |
| 1186 / 1190 / 1194 | `rl_cif_obs_spine`, `rl_spine_dates`, `rl_spine_with_target` | `…spine}/retail_loans/…` |
| 1200 | `dcore_observation_spine` | `${globals:folders.spine}/dcore/observation_spine` |
| 1206–1216 | `dpl_cc_spine`, `dpl_cc_target`, `dpl_cc_spine_with_target` (`# — cc_dpl (legacy / inactive)`) | |
| 1222–1236 | `model_input_target`, `model_input_base`, `model_input` (`pandas.ParquetDataset`), `dpl_cc_model_input` (`# 08_MIP`) | |

Layer notes: `dcore_observation_spine` is a spine (not staging, as the A2 notes assumed);
`int_loan_master` and `dcore_int_*` are the intermediate layer (`folders.int`).

## `conf/base/catalog/catalog_raw_way4.yml`, lines 7–64 (excerpt)

`_way4_ddi: &way4_ddi` = `enbd_collections.datasets.spark_hive_sql_dataset.SparkHiveSQLDataset`,
database `${globals:aacoe_prefix}ddi_tdv_way4_standard_group_way4_standard`, `write_mode: "overwrite"`.
Comment: "Way4 CC raw tables (input to data_engineering pipeline). 6 of 9 tables migrated to DDI schema
(3-5 year history); 3 remain on TDV pending DDI ingestion (TBL024-026)." Each entry is
`SELECT * FROM ${globals:aacoe_prefix}ddi_tdv_way4_standard_group_way4_standard.<table>`:

| Key | Anchor | Table |
|---|---|---|
| `raw_stg_contract` | `*way4_ddi` | `contract` |
| `raw_stg_limit` | `*way4` | `limit` (`table: "stg_limit"`) |
| `raw_stg_card` | `*way4` | `card` (`table: "stg_card"`) |
| `raw_stg_client` | `*way4_ddi` | `client` |
| `raw_transaction` | `*way4` | `transaction` |
| `raw_stg_contract_attribute` | `*way4_ddi` | `contract_attribute` |
| `raw_stg_balance` | `*way4_ddi` | `balance` |
| `raw_stg_account_group` | `*way4_ddi` | `account_group` |
| `raw_stg_product_config` | `*way4_ddi` | `product_config` |
| `raw_stg_billing` | `*way4_ddi` (under "New Way4 CC DDI raw tables (10 tables from schema-to-model)") | `billing` |

## `src/enbd_collections/pipeline_registry.py`, lines 213–270 (photo)

Same as the mirror's lines 212–275 except:
- no `crx_rl_a4_deterioration_b13_check` entry (bundle 13 cleanup applied in the workplace);
- the two `*_b12_check` entries are one line each:
  `"crx_cc_a1_ability_b12_check": (crx_cc_a1_ability.create_b12_check_pipeline()),`;
- after `location_features`: `# -- Genesys / PCA interactions ---` and `"genesys": genesys.create_pipeline(),`
  (not in the mirror);
- the closing `}` sits on line 270.
A3 registry keys: `"crx_cc_a3_payment_credibility"` (245), `"crx_rl_a3_payment_credibility"` (255).
`"crx_cc_raw_extract"` (234), `"crx_cc_full_history"` (233), `"crx_rl_a4_spine"` (248) are still registered.

## Registry: workplace-only `casa_windows*` pipelines (handoff 57, 2026-11-10)

The workplace `pipeline_registry.py` has four `casa_windows*` imports and registry entries (modules and
catalog entries exist there; `TASKS.md` E4 refers to them) that the mirror lacks. The bundle 21 apply
dropped them silently (the same merge effect as the bundle 16 catalog loss); the UAT Sonnet restored
them. Until the registry is photographed, any bundle that edits the registry must have UAT check the
`casa_windows*` entries after the apply.
