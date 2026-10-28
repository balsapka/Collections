# A1: why the bureau CIF bridge reaches under 4% of customers (O65), and the right link

Give this to the UAT Sonnet 5.5. Same flow as before: Sonnet writes the snippet in UAT, you run it in
PROD for `cc_60_180` and `rl_60_180` (switch `model_id` in `globals_dev.yml`), commit the JSONs,
Sonnet writes the summary. Paste back `tmp_validation/a1_bureau_link/summary.md` and the inventory
section of its `README.md`. While you are there, the same session can answer R13 and R14 (`REQUESTS.md`: how WM decodes
`week_number`; the v03b CASA transaction classification).

````text
Goal: find how an AECB bureau file is tied to one of our customers (cif_id), so that bureau salary
(stg_aecb_salary_history) reaches every customer it exists for. You work in UAT with no data: write
a validation snippet, the user runs it in PROD, then you analyse the results. Change no pipeline
code.

What is known (A1 v03b, tmp_validation/a1_v03/summary.md section 0; read it first):
- prm_bureau_cif_bridge (src/enbd_collections/nodes/primary/bureau/prm_bureau.py, about lines
  46-59) takes cif_id from the digits of PRVDR_SUBJ_NUM in the ALERT table (one arbitrary row per
  subject) and inner-joins contract_link. Structure is sound (1 CIF per file, 1 row per file x
  load date), but coverage is not: 93.8% (CC) / 96.2% (RL) of base CIFs have an alert row in
  prm_bureau_alert_enriched, while only 109 (0.58%) / 123 (3.4%) reach a bureau file. 99.4% of CC
  CIFs drop out at the bridge, before any date or salary filter.
- Where a file is reached, 62% / 78% have a salary row, so stg_aecb_salary_history is usable (its
  month is MMyyyy). Ignoring file and date, only 51 CC / 93 RL base CIFs have any salary row.
- The bureau pipeline was written by an earlier model and never validated: do not trust its
  docstrings or models, read the code and the data.
- RL already gets bureau salary from feature_retail_loans (aecb_last_salary_credit_amount); find
  out how that pipeline links a bureau report to the loan / customer, because it evidently works.

Hypotheses, each with a verdict and the numbers behind it:
  H1 contract_link is the bottleneck: how many alert subjects / base CIFs it holds, what its keys
     are, whether it covers only a subset (e.g. a product, a period, contract-level inquiries).
  H2 the subject number is not the CIF: PRVDR_SUBJ_NUM digits vs cif_id (length, leading zeros,
     prefixes, a different id such as Emirates ID or an account number); the match rate of each
     candidate transformation against our customer master.
  H3 a better link exists: every AECB table in the catalog (catalog_raw_aecb.yml and the staging /
     primary bureau outputs) with a column that could identify the subject (file id, header file id,
     subject id, Emirates ID, passport, provider subject number, CIF, account / contract number);
     for each, coverage of base CIFs and of salary-history file ids. Include the inquiry / request /
     header tables and whatever feature_retail_loans uses.
  H4 the salary table's file ids are a different id space: share of stg_aecb_salary_history
     hdr_file_id values found in each candidate link table; files per subject per month (one
     report per pull?).
  H5 the recommended link: base CIFs reached, salary-history files reached, CIFs with a salary
     month in 24 months (CC and RL), against today's 109 / 123 and 39 / 74; how many files map to
     more than one CIF and how to resolve it.

Hard rules:
- catalog.load only (no spark.read, no paths); model_id from catalog.load("params:model_id"), in
  the output file name; nothing hardcoded or overridden.
- Aggregates only: no ids, Emirates IDs, names or customer rows in the results. Id formats only as
  patterns (length, digit / letter mask, prefix counts).
- Base = the obs base for model_id (crx_cc_obs_base / crx_rl_obs_base), latest observation month;
  customer = cif_id.
- One JSON per model_id at context.project_path / "tmp_validation/a1_bureau_link/results_<model_id>.json";
  each table in its own try/except with the error recorded.
- Work only in tmp_validation/a1_bureau_link/ (tracked); commit and push only that folder.

Deliverables:
1. README.md: the inventory (H3: every candidate table and column, what it holds, file:line where
   the repo builds or reads it), the run steps.
2. a1_bureau_link_snippet.py, run in PROD for cc_60_180 and rl_60_180.
3. After the user commits the JSONs, summary.md (under 50 lines): per hypothesis a verdict line
   and the key numbers, CC and RL side by side; then the recommended link as exact join keys and
   transformations, the tables it reads, its coverage, and how to deduplicate. Check each number
   against the JSON; write NOT IN JSON when one is missing.
````
