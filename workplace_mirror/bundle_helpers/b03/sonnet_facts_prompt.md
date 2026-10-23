# Facts for bundle 03 (UAT, no data, no code changes)

Give this to the workplace Sonnet in UAT. Pull first, so it has
`tmp_validation/a1_v01/results_cc_60_180.json`. Paste its report back here.

````text
Task: collect facts for the next mirror bundle. Read only: change nothing, commit nothing.
Answer every item exactly (names copied verbatim from the code / config / results file).
Where you can't find something, write NOT FOUND and where you looked.

1. comp_financial_tran_repos_dly columns, from tmp_validation/a1_v01/results_cc_60_180.json
   ("columns_found") and from the snippet a1_v01_snippet.py: list every column the
   snippet looked for, and whether it was found. Give the exact names of:
   a) the transaction key columns (tran_id, part_tran_srl_num, ...);
   b) the debit/credit column;
   c) the 5 type/code columns (tran_type, tran_sub_type, tran_particular_code, ...);
   d) the 4 amount columns. Say which one is the transaction amount in AED, if the code or
      catalog tells you;
   e) the account column (foracid / acid / account number) if one exists, and the
      product/category column that held "REMITTANCE" in v01's H2.
   Also give the catalog entry for comp_financial_tran_repos_dly (type, filepath/table,
   load_args, partition column).

2. Primary-layer conventions in this repo. Find 2-3 existing pipelines that build a prm_
   dataset from a raw_/stg_/comp_ source, and for each give:
   - the package path under src/enbd_collections/pipelines/;
   - how it is registered in pipeline_registry.py (the line);
   - its catalog entry: file, type, filepath pattern (with model_id or not), save_args
     (mode, partitionBy), layer metadata;
   - where its parameters live (file and key).
   Then say where a new pipeline building prm_casa_return_events should go, by the same
   conventions (package path, catalog file, parameters file).

3. prm_bureau_alert_enriched:
   - the node and file that build it, and its raw/stg inputs (catalog names);
   - every column of those inputs that holds the bureau pull date, report date or event
     date (name, which input, how the code uses it today, or "unused");
   - whether extract_date in the output comes from one of them;
   - which column carries the bureau pull date, so that it can be exposed as
     bureau_pull_date in prm_bureau_alert_enriched.

4. Who else reads these datasets (grep the repo and the catalog):
   comp_financial_tran_repos_dly, prm_bureau_alert_enriched. List the pipeline and node of
   each consumer.

Format: numbered like the questions, plain text, under 80 lines.
````
