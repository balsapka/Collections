# A1: fix the bureau-link snippet for the tables the sandpit has now (+ the CASA part)

Give the block below to the UAT Sonnet 5.5 that wrote `tmp_validation/a1_bureau_link/` (the
bureau-link snippet and its CASA addendum C1–C3). A fresh session works too: the block is
self-contained. Then run the fixed snippet in PROD for `cc_60_180` and `rl_60_180`, commit the JSONs,
let Sonnet write the summary, and paste back `summary.md` and the README inventory. The separate
alert-table prompt (`tmp_validation/a1_alert_salary/`) can run in the same PROD session.

````text
Goal
The snippet in tmp_validation/a1_bureau_link/ (bureau CIF link H1-H5 + the CASA part C1-C3) could
not run: some raw AECB tables are temporarily missing from the sandpit. Make it run on what exists
today, skip cleanly what does not, and keep the CASA part independent of the bureau part. Change no
pipeline code.

What is now known
- The AECB tables that exist (your inventory, tmp_validation/a1_bureau_link/bureau.md), all in
  dpl_uae_operations: ref_ops_aecb (1 snapshot, 2026-01-22), sa_ops_aecb_subj_crdt_score,
  sa_ops_aecb_subj_con_tot_smry, sa_ops_aecb_subj_cntrct_hist (995M rows), sa_ops_aecb_subj_cntrct_dtl,
  sa_ops_aecb_sub_sal_cr_hist (148M, edp_load_date from 2023-06-23), sa_ops_aecb_subj_cntrct_link
  (1.3M), sa_ops_aecb_subj_court_case, sa_ops_aecb_subj_pymnt_order, sa_ops_aecb_alert (90M),
  sa_ops_aecb_alert_othprv_sub. Any other AECB table the snippet reads (subject / header / inquiry /
  request tables, anything else in catalog_raw_aecb.yml) is NOT AVAILABLE for now.
- Likely cause of the bridge's <4% coverage: among these, only subj_cntrct_link ties a bureau file
  to a subject, and it is small (1.3M rows against 148M salary-history rows). Test this as H1.
- Persisted staging / primary datasets (stg_aecb_salary_history, prm_bureau_cif_bridge,
  prm_bureau_alert_enriched, other prm_bureau_*) may still load even where their raw source is gone;
  use them, and record which loaded.
- R13 (WM week_number decode) and R14 (the v03b CASA classification) are no longer needed: drop
  them from the snippet and the README.
- The alert table itself (salary_credit_amount, cb_subject_id as a hub, "is it the master bureau
  table?") is covered by the separate a1_alert_salary snippet: do not compute the same tables here.
  Here, H3 / H4 cover the link candidates among the other tables; mention the alert table only as
  the source of today's cif_id.

Changes to make
1. Availability first: before any part runs, try each table the snippet needs (catalog.load + a
   1-row read) and save an availability list (dataset, loaded yes / no, error class). A part whose
   inputs are missing records "NOT AVAILABLE: <dataset>" and the run continues.
2. Bureau part: restrict H3 / H4 to the available tables above; add the history depth of each
   (min / max edp_load_date, and for salary history the min / max salary month). Keep H2 (is
   PRVDR_SUBJ_NUM the CIF?) and H5 (the recommended link) on what loads; if no link beyond
   subj_cntrct_link can be tested, say so as H5's verdict.
3. CASA part C1-C3 (WM segment filter; who holds a CASA account; history depth of each source): its
   own try/except blocks, no dependency on any bureau table, so it completes even when every bureau
   input fails. C3: add sa_ops_aecb_sub_sal_cr_hist's depth (loads from 2023-06-23) next to the
   internal sources, so "ever had bureau salary" is quoted against it.
4. Keep everything else as it was: the same hypotheses, outputs and summary format.

Hard rules
- catalog.load only (no spark.read, no paths); model_id = catalog.load("params:model_id"), in every
  output file name; nothing hardcoded or overridden.
- Aggregates only: no ids, Emirates IDs, names or customer rows; id formats only as patterns
  (length, digit / letter mask, prefix counts); suppress any cell under 10 customers.
- Base = the latest observation month of crx_cc_obs_base / crx_rl_obs_base; customer = cif_id.
- Work only in tmp_validation/a1_bureau_link/ (tracked); commit and push only that folder.

Deliverables
1. The fixed snippet and README.md: an "Availability" section (what loads, what does not), the
   inventory updated to the tables above, R13 / R14 removed, run steps. Commit and push from UAT.
2. After the user commits results_cc_60_180.json and results_rl_60_180.json: summary.md (under 60
   lines) — first the availability list, then per hypothesis (H1-H5, C1-C3) a verdict and the key
   numbers, CC and RL side by side, NOT AVAILABLE where an input was missing; then the recommended
   link (or why none can be tested yet) and which source defines "has a CASA with us". Check every
   number against the JSON; write NOT IN JSON when one is missing.
````
