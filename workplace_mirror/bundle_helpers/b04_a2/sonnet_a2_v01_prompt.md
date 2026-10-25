# A2 v01: the facts the locatability engine needs

Give this to the workplace Sonnet in UAT. Independent of bundle 03: it only reads sources.
Same flow as the A1 validations (Sonnet writes, you run in PROD, Sonnet analyses), with the
folder `tmp_validation/a2_v01/`. Run the snippet for `cc_60_180` and `rl_60_180` (switch
`model_id` in `globals_dev.yml`). Paste back `inventory.md` (part A) and `summary.md` (part C).

````text
Task: collect the facts needed to build the A2 locatability axis. You work in UAT with no data:
you read code / config / profiles and write a snippet; you never see PROD rows. Change no
pipeline code.

Context. A2 has two independent dimensions plus a deceased override:
- Location: the latest dated evidence of where the customer is wins. Evidence is read at CIF
  level across all the customer's cards and CASA accounts: logins (UAE / abroad), card and
  CASA spending (UAE / abroad), travel purchases (airline / cruise / travel-agency MCC) in the
  last 12 months, and a DCORE "left the country" result. Foreign latest -> Skip at any age;
  UAE latest -> In Country if within the window (3 months at 60-180, 6 at 180+).
- Reachability: from DCORE call outcomes up to the observation date (no T0).
- Deceased: DCORE deceased results, Way4 block code D (CC), feat_demographics_cif.
Observation dates are month ends (crx_cc_obs_base / crx_rl_obs_base, after bundle 03).
Persona code reads prm_/feat_/wm_ datasets only; a raw pass goes into a reusable primary node.

A. Inventory (read only). Save tmp_validation/a2_v01/inventory.md, under 100 lines. Quote
   file:line for every claim; write NOT FOUND and where you looked when you can't find one.
   1. Location features that already exist, in this repo AND in the sibling clones
      wealth_management and retail.feature_space: every dataset with travel, foreign /
      cross-border / international spend, merchant or login country (including
      feat_cc_txns_rfs = fea_cc_inflow_outflow_txns_monthly and feat_fx_leakage =
      fea_monthly_agg_fx_leakage). For each: grain, date column, the column names, how
      "foreign" is defined (merchant country, currency, or something else), its source
      tables. Then: an earlier review found these unfit for our purpose; find what was
      written about that (tmp_validation, docs, RESULTS*.md, comments) and quote it.
   2. Transaction sources a location data layer could be built from:
      a) card transactions: the prm_/stg_/raw_ dataset (prm_transaction, raw_transaction,
         crx_cc_transactions, ...), its catalog entry, and the exact columns for contract /
         card id, transaction date, merchant country, is_international / currency,
         merchant_category_code, description, debit/credit;
      b) CASA transactions: wm_pri_labelled_transactions and comp_financial_tran_repos_dly:
         the exact columns for cif_id, account, date, channel (ATM / POS / transfer),
         country or foreign indicator, MCC, debit/credit;
      c) which of them already holds supplementary / add-on cards under the main CIF.
   3. DCORE: the nodes and catalog entries of dcore_observation_spine,
      dcore_stg_scope_agreements and dcore_prm_followup_outcomes; their columns (exact
      names: account_id or contract_id, observation_date, agreement_id, cif_id, action_ts,
      action_code, result_category, result_name); how dcore_observation_spine is built and
      whose observation dates it carries (cc_spine billing dates or month ends).
   4. Deceased sources: prm_contract (columns, how often a contract gets a row, the date
      column) and feat_demographics_cif (grain, date column, ft_deceased_flag source).
   5. prm_digital_login_monthly: the node that builds it, its raw source, how month_number,
      last_login_date, last_login_foreign_flag and last_login_country are derived, and
      whether the raw source has one row per login.
   6. Results splits: the column that gives the RL product type (Personal Loans, Personal
      Cash Loans, Auto) on rl_spine or its sources, with its value -> product mapping; and
      how the charge-off-age vintage (early-stage < 2 years / late-stage 2+ years) is
      computed in this repo (search gt2y, lt2y, chargeoff), for CC and RL.

B. PROD snippet: tmp_validation/a2_v01/a2_v01_snippet.py plus README.md with the run steps.
   It runs in a Kedro notebook (catalog, context exist).
   Rules: catalog.load only (no spark.read, no paths); model_id from
   catalog.load("params:model_id") and in the output filename; aggregates only — no ids,
   account / card numbers, names or customer free text (DCORE result_name values are fixed
   codes and may be listed); top 50 per categorical; read only the last 24 months of any event
   table; one JSON at context.project_path / "tmp_validation/a2_v01/results_<model_id>.json";
   commit and push only tmp_validation/a2_v01/. Base = the obs base for model_id, latest
   observation month only. Wrap each table in try/except and record the error, so one
   failure does not lose the rest.

   Tables:
   t1_dcore_keys   dcore_observation_spine: column list; day-of-month distribution of
                   observation_date; join rate of the base on (account, observation_date)
                   exact, on (account, same month), on account only; agreements per account
                   (1 / 2 / 3+), and how many of those agreements have events in the last
                   24 months.
   t2_dcore_events for base accounts, events in the last 24 months: counts by action_code;
                   by (action_code, result_category); top 50 result_name with action_code
                   and the share of each on the ringing / dead-line / right-party / departure /
                   deceased lists in cc_a2_locatability/constants.py (and the top 50 names on
                   none of the lists).
   t3_reach_preview for base accounts: distinct outbound (OC/CB) call dates in the last 3 and
                   6 months (0 / 1-2 / 3-5 / 6+); share with an inbound call (IC) in the last
                   3 / 6 months; share whose last 3 call dates were all ringing or dead
                   (every OC/CB event that day on those lists, none confirmed).
   t4_login        raw_digital_login_data and raw_digital_login_data_history (last 24
                   months of createdon): whether each has sessionid / countrycode /
                   countrylocation; NULL share of each; share with both country columns
                   NULL; rows vs distinct non-NULL sessionid; status value counts.
                   stg_digital_login: rows by is_foreign_login and by whether both country
                   columns are NULL (those are flagged foreign today).
                   prm_digital_login_monthly: month_number format and day-of-month; lag
                   month_number - last_login_date in days (p1/p50/p99, share negative);
                   foreign flag share; country null share. For base CIFs: age of the latest
                   login at the observation date (0-3 m / 3-6 m / 6-12 m / 12+ m / none),
                   split by foreign flag.
   t5_location_sources for base CIFs, each candidate from A1 / A2 (feature tables, card and
                   CASA transactions): share with any row in the last 12 months; share with a
                   foreign / international row; share with a travel MCC or travel category
                   row; age of the latest row and of the latest foreign row (0-3 m / 3-6 m /
                   6-12 m / 12+ m / none).
   t6_deceased     prm_contract: day-of-month of its date column, join rate to the base on
                   exact date / same month / latest row on or before; block_code_1/2 value
                   counts (top 50). feat_demographics_cif: rows per cif_id (1 / 2 / 3+), its
                   date columns, ft_deceased_flag counts for base CIFs.
   t7_splits       RL only: base accounts by product type (the column from A6); CC and RL:
                   base accounts by charge-off-age vintage, as computed in A6.

C. After the user commits the results: read results_cc_60_180.json and results_rl_60_180.json
   and save tmp_validation/a2_v01/summary.md, under 80 lines: per table t1-t7 the key
   numbers for both model_ids and one verdict line each:
   - t1: which join key works for month-end observation dates; whether accounts carry more
     than one live agreement;
   - t2: whether the result_name lists cover the outcomes (share unmatched, top unmatched);
   - t3: expected Reachable / Non-Reachable / Unknown shares under the rules in Context;
   - t4: whether month_number is a month start or end, whether last_login_date is the real
     login day, and login coverage;
   - t5: which source gives the best location coverage, and whether a new primary
     (prm_customer_location_events) is needed;
   - t6: which date join Way4 needs; whether demographics needs a point-in-time pick;
   - t7: product and vintage counts.
````
