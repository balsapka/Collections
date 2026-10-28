# A1 addendum: CASA holding, segment coverage and history depth (for the final-report metrics)

Give this to the same UAT Sonnet 5.5 session that runs `sonnet_a1_bureau_link_prompt.md`, as one more
part of that snippet (same folder `tmp_validation/a1_bureau_link/`, same JSON per model_id, same
hard rules). Paste back its summary section with the bureau one.

````text
Extra part for the same snippet and summary (same hard rules: catalog.load only, model_id from
params, aggregates only, base = the obs base's latest month, cif_id level, try/except per table).

Goal: the A1 final report must say exactly how many customers have no CASA account with us
(Unknown by design), how many have a dormant one, and how many never had a salary with us. Check
that the sources can say this.

  C1 WM segment filter. A2 v02 found wm_pri_labelled_transactions filtered upstream to
     segment_desc in (PRB, PSB, PB) (parameters.yml:1304 of wealth_management). For each WM table
     A1 reads — wm_fea_casa_eod_avg_balance, wm_fea_casa_cc_inflow_outflow,
     wm_fea_salary_days_since_increment, wm_pri_labelled_transactions — say from the code whether
     the same (or any) segment / population filter applies, and measure: share of base CIFs with a
     row in 12 months, against the share with any CASA transaction in comp_financial_tran_repos_dly
     in 12 months, by segment_desc if available. Explain v03b's open point: 63.5% of RL Unknown rows
     had a customer-initiated CASA transaction in comp while the WM flow flag was 0.
  C2 Who holds a CASA account. Find the source that lists a customer's current / savings accounts
     with open / close dates (account master, e.g. general_acct_mast_table or its primary; file:line
     in our repo or wealth_management). Base CIFs: CASA open at the observation date / closed in
     the last 12 months / never; against "no balance row in 12 months" (the v03 proxy) — crosstab.
  C3 History depth. Earliest month each source holds for base CIFs: wm_fea_salary_days_since_increment
     (and the earliest recoverable salary month), comp_financial_tran_repos_dly, the WM CASA tables,
     stg_aecb_salary_history, feature_retail_loans pulls. Share of base CIFs whose earliest CASA
     account or customer record is younger than that depth (so "never had salary" is not just
     "joined recently").

Summary lines: per table a verdict; then which source should define "has a CASA with us", whether
the WM balance / salary tables cover our whole base, and the history depth to quote as "ever".
````
