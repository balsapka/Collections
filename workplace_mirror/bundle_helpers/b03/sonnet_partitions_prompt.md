# A1 sources v01: how each table is partitioned, and what our date filters save

Give this to the workplace Sonnet in UAT. Independent of bundle 03: it can run before or
after it (the snippet only reads the sources). Same flow as the other validations (Sonnet
writes, you run in PROD, Sonnet analyses), with the folder `tmp_validation/a1_sources_v01/`.
Paste back `inventory.md` (part A) and `summary.md` (part C).

````text
Task: find out how every source of the CC A1 ability axis is stored and loaded, and whether the
date filters in the A1 code prune partitions, skip row groups, or only drop rows after the
scan. You work in UAT with no data: you read code / config and write a snippet; you never see
PROD rows.

Context. Bundle 03 filters each A1 source from a floor date before any join or aggregation
(src/enbd_collections/pipelines/crx_persona/a1_ability/signals.py; casa_primary in
src/enbd_collections/nodes/primary/casa/prm_casa.py). We do not know the partition columns.
We believe the WM feature tables are pinned to one adv_load_date partition in the catalog
(globals snapshot_adv_load_date) and carry the full weekly history in week_number, so a
week_number filter cannot prune — it only cuts rows before the shuffle. Treat every belief here
as unproven.

Datasets and the filter A1 applies (floor F = first day of the month 5 months before the
month of params:crx_persona.persona_start_date — the start of the 6-month income / CASA
lookback at cc_60_180):
  wm_fea_salary_days_since_increment   to_date(cast(week_number as string), 'yyyyMMdd') >= F
  wm_fea_casa_eod_avg_balance          same on week_number
  wm_fea_casa_cc_inflow_outflow        same on week_number
  wm_pri_labelled_transactions         tran_date >= F
  stg_aecb_salary_history              to_date(subj_salcr_hist_ref_mnth, 'MMyyyy') >= F
                                       (applied after the join with prm_bureau_cif_bridge)
  prm_bureau_alert_enriched            to_date(extract_date) >= F
  comp_financial_tran_repos_dly        edp_load_date >= F and tran_date >= F (casa_primary)
  prm_casa_return_events               event_month >= F (string yyyy-MM-dd; written by
                                       casa_primary with partitionBy event_month)
  no date filter (report only):        prm_bureau_cif_bridge, raw_beneficiary_cards,
                                       prm_balance, cc_spine, crx_cc_obs_base

A. Inventory (read only; no data). Save tmp_validation/a1_sources_v01/inventory.md, under 60
   lines. Per dataset: the catalog entry (type, file_format, filepath or Hive table, load_args
   including filters / partition pins and the globals they read, save_args partitionBy), the
   node that writes it if it is ours, and anything the repo says about its partitioning
   (file:line).

B. PROD snippet: tmp_validation/a1_sources_v01/a1_sources_v01_snippet.py plus a README.md with
   the run steps. It runs in a Kedro notebook (catalog, context exist).
   Rules: catalog.load only (no spark.read, no paths); model_id from
   catalog.load("params:model_id") and in the output filename; F from
   catalog.load("params:crx_persona")["persona_start_date"]; aggregates only — no ids, card /
   account / contract numbers, names or free text; no partition values except dates; one JSON
   at context.project_path / "tmp_validation/a1_sources_v01/results_<model_id>.json"; commit
   and push only tmp_validation/a1_sources_v01/. Never collect() rows, only aggregates.

   Hypotheses:
   P1  The three WM feature tables load one adv_load_date partition; week_number is a plain
       column; the A1 filter neither prunes nor skips row groups.
   P2  wm_pri_labelled_transactions is partitioned by a date the tran_date filter prunes.
   P3  comp_financial_tran_repos_dly is partitioned by edp_load_date, and casa_primary's
       edp_load_date filter prunes it.
   P4  prm_casa_return_events prunes on event_month.
   P5  The bureau tables (stg_aecb_salary_history, prm_bureau_alert_enriched) are small enough
       that the filters do not matter.

   Per dataset (one entry each):
   s1_storage    the dtype of every column the A1 code reads (from df.schema); partition
                 column names, parsed from the "name=value" segments of df.inputFiles(); for
                 each date-like partition column its distinct count, min and max.
   s2_size       df.inputFiles() count and total bytes if available; row count; for the A1
                 date column (after the same parsing the A1 code does): min, max, null share,
                 and the share of rows at or after F.
   s3_filter     the A1 filter from the list above applied to df: the PartitionFilters,
                 PushedFilters and DataFilters lines of the executed plan
                 (df._jdf.queryExecution().executedPlan().toString(), those lines only), and
                 inputFiles() count after the filter.

C. Analysis (only when I give you results_cc_60_180.json): for P1-P5 a verdict (CONFIRMED /
   REJECTED / INCONCLUSIVE) with the 2-4 numbers that decide it. Then one line per dataset:
   prunes / skips row groups / only cuts rows / no filter, the share of rows the filter keeps,
   and — only where a filter misses an available partition column, or could prune if written
   on the raw column (e.g. comparing week_number as yyyyMMdd instead of parsing it) — the
   exact expression that would. Don't propose other code changes. Plain text, under 40 lines.
   Save it as tmp_validation/a1_sources_v01/summary.md, then commit and push.
````
