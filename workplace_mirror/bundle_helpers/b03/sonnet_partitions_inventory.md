# A1 sources v01: partition inventory (Sonnet part A, transcribed)

Source: workplace `tmp_validation/a1_sources_v01/inventory.md`, 59 lines (photos IMG_8393–8395,
2026-10-26). Parts B and C (PROD snippet, summary) are not back yet. Condensed; file:line
references are the workplace's.

| Dataset | Catalog | Owner | Partitioning | What A1 filters on | Prunes? |
|---|---|---|---|---|---|
| `wm_fea_salary_days_since_increment` | `catalog_casa_plus_ftr.yml:38`, parquet, `.../04_feature/.../adv_load_date=${globals:snapshot_adv_load_date}` | WM | **pinned** to one leaf dir = one full-history snapshot; `adv_load_date` not even a column once pinned; `week_number` is a plain column (`reference/sibling_repo_partitions.md:6`) | — | n/a (single snapshot) |
| `wm_fea_casa_eod_avg_balance` | `catalog_casa_plus_ftr.yml:103`, parquet, `.../04_feature/fea_casa_eod_avg_bal_by_cif` | WM | **unpinned**, no `load_args` filter; carries `adv_load_date` (load-time constant, not a partition) and `week_number` (plain per-row column) — PROD-probed 2026-10-05 | — | no |
| `wm_fea_casa_cc_inflow_outflow` | `catalog_casa_plus_ftr.yml:33`, parquet | WM | pinned `adv_load_date`, as salary | — | n/a |
| `wm_pri_labelled_transactions` | `catalog_casa_plus_ftr.yml:28`, parquet, `.../03_primary/pri_labelled_transactions_indicators_by_week` | WM | Hive partition **`week_number`** (one dir per week) | **`tran_date`** (`signals.py:212 tran_date >= since`) | **unconfirmed — P2**: filter column ≠ partition column |
| `stg_aecb_salary_history` | `catalog_outputs.yml:140`, `_spark_de` parquet, no `partitionBy` | ours (`pipelines/bureau/staging.py:48-51`) | `.repartition("subj_salcr_hist_hdr_file_id")` (`stg_aecb_salary_history.py:64`) is an in-memory shuffle, not on-disk | `subj_salcr_hist_ref_mnth` (`'MMyyyy'` string) after the join to `prm_bureau_cif_bridge` (`signals.py:121-123`) | row-group stats only |
| `prm_bureau_alert_enriched` | `catalog_outputs.yml:483`, `_spark_de`, no `partitionBy` | ours (`prm_bureau.py:119`, grain `alert_process_id × edp_load_date`) | none | `extract_date` (`signals.py:306-308`) — a different column from the write grain's `edp_load_date` | row-group stats only |
| `comp_financial_tran_repos_dly` | `catalog_raw_dpl.yml:9`, `SparkHiveSQLDataset`, `SELECT * FROM ${aacoe_prefix}dpl_uae_compliance.COMP_FINANCIAL_TRAN_REPOS_DLY` | DPL (external Hive) | on-disk partitioning not visible from our code; `_load()` runs `spark.sql(query)` (`spark_hive_sql_dataset.py:51-57`), so `casa_primary`'s later `.filter(edp_load_date >= F, tran_date >= F)` (`prm_casa.py:56-58`) composes into one Catalyst plan on the Hive scan | — | **unconfirmed — P3**: prunes only if the Hive table is partitioned on either column |
| `prm_casa_return_events` | `catalog_casa.yml:4`, parquet, `save_args: {mode: overwrite, partitionBy: ["event_month"]}` | ours (`prm_casa.py:35`, `pipelines/casa/primary.py:9-23`) | **genuine Hive partition** `event_month = date_format(trunc(tran_date,'month'),'yyyy-MM-dd')` (`prm_casa.py:65-67`) | `event_month >= F` (`signals.py:350-361`) | **yes — P4** |

No date filter (reported only), all `_spark_de` with no `partitionBy` unless noted:
`prm_bureau_cif_bridge` (`catalog_outputs.yml:479`, ours), `raw_beneficiary_cards`
(`catalog_raw_digital.yml:73`, Hive query filters `edp_activeind='Y' AND
instrument_type='CARD_NUMBER'` server-side, not ours), `prm_balance` (`catalog_outputs.yml:433`),
`cc_spine` (`catalog_outputs.yml:1136`), `crx_cc_obs_base` (`catalog_crx.yml:385`, parquet,
overwrite).

**Pattern:** of our own primary / staging outputs only `prm_casa_return_events` declares a
`partitionBy`; every other one writes a flat parquet directory, so pruning can only come from
parquet row-group statistics (`PushedFilters`), never `PartitionFilters`.

## What it means for A1 (Claude, 2026-10-26)

- `event_month` is a real Hive partition. On read Spark infers its folder values as **dates**
  (`2024-07-01` → `DateType`) — the cause of the bundle 03 check failure; fixed in bundle 04.
- P2 (`wm_pri_labelled_transactions` filtered on `tran_date`, partitioned on `week_number`) is
  a run-time question, not a logic one. Once part B shows the `PartitionFilters`, add a
  `week_number >=` floor next to the `tran_date` filter if it doesn't prune.
- P3 sits in `casa_primary` (DPL table), already isolated in one primary node that runs once a
  month; nothing to change in A1.
