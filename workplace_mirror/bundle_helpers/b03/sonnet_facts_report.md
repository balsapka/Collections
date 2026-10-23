# Sonnet facts report for bundle 03 (UAT, 2026-10-24)

Transcribed from the photos of the workplace `tmp_validation/a1_v01/summary.md` (condensed).

1. **comp_financial_tran_repos_dly**
   - Key: `tran_id`, `part_tran_srl_num` (+ `tran_date` as the 3rd component). All found.
   - Debit/credit: `tran_dc` (2 distinct values).
   - Type/code: `main_tran_type`, `tran_type`, `tran_sub_type`, `channel_tran_type`,
     `tran_particular_code`.
   - Amounts: `tran_amt`, `tran_amt_aed`, `actual_tran_amt`, `actual_tran_amt_aed`.
     `tran_amt_aed` is the AED amount by the repo convention (cc/rl departure_signature);
     `actual_*` is read nowhere.
   - Account: `foracid` (0% null, 4.7M distinct). No product/category column: "REMITTANCE"
     sits in `main_tran_type`, `tran_type` and `channel_tran_type`.
   - Catalog: `conf/base/catalog/catalog_raw_dpl.yml:9-14`, `SparkHiveSQLDataset`,
     `SELECT * FROM ${globals:aacoe_prefix}dpl_uae_compliance.COMP_FINANCIAL_TRAN_REPOS_DLY`,
     write_mode overwrite, no load_args, no partition column.

2. **Primary conventions**: `pipelines/<domain>/primary.py` calls
   `nodes/primary/<domain>/prm_<domain>.py`. Examples: bureau (`bureau_primary`,
   `build_alert_enriched(stg_aecb_alert, params:product_mapping_aecb)`, params in
   `parameters_bureau.yml`), credit_card_way4 (`cc_way4_primary`, `build_balance`),
   demographics (`demographics_primary`). Catalog: `catalog_outputs.yml`, anchor `_spark_de`
   (SparkDataset, parquet, overwrite, no partitionBy), filepath
   `${_project.hdfs_path}/${globals:model_id}/${globals:folders.prm}/<domain>/<entity>`.
   prm tables are model_id-namespaced on disk. Suggested: domain `casa`, params file
   `parameters_casa.yml`. Bureau prm projects through `build_primary_dataframe(df, Model,
   renames)` (`src/data_engineering/primary/schema.py:24`, Pydantic models).

3. **prm_bureau_alert_enriched**: `build_alert_enriched`,
   `nodes/primary/bureau/prm_bureau.py:119`, input `stg_aecb_alert` (from raw
   `sa_ops_aecb_alert`). Date columns in `_ALERT_RENAMES` (line 74): `OPN_DT` → `open_date`
   (kept), `EXTRACT_DT` → `extract_date` (kept; also gives `alert_month`), `DT_OF_RETURN` →
   `return_date` and `CONTRACT_STATUS_DT` → `contract_status_date` — **both dropped** by the
   final projection (`BureauAlertEnriched` has no such fields). `DT_OF_RETURN` is real
   upstream (stg, fixtures, schema registry, raw profile). **The pull date is `EXTRACT_DT`
   = `extract_date`**; `bureau_pull_date` would only be an alias.

4. **Consumers**
   - comp_financial_tran_repos_dly: cc_departure_signature (`build_crx_departure_pass_b`),
     rl_departure_signature (`build_rl_depart_casa_signals`, `build_rl_depart_travel_mcc`),
     a1_ability `build_internal_returns` via cc_a1_ability_v2.
   - prm_bureau_alert_enriched: bureau `build_int_bureau_alert_monthly`; cc_a1_ability
     (`build_crx_a1_group_b_bureau`, `…_recent`); rl_a1_ability
     (`build_rl_a1_group_b_bureau_recent`); cc_a1_ability_v2 (`build_crx_cc_a1_distress_signals`,
     b01 `compare_crx_cc_a1_b01_distress`).
