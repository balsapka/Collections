# Bureau investigation v01: what a bureau row is, and when a bounce happened

Give this to the workplace Sonnet in UAT. Independent of bundle 03: it can run now. Same
flow as the A1 validations (Sonnet writes, you run in PROD, Sonnet analyses), with the folder
`tmp_validation/bureau_v01/`. Paste back `inventory.md` (part A) and `summary.md` (part C).

````text
Task: find out what the AECB bureau tables hold, and how to date a bounced cheque. You work in
UAT with no data: you read code / config / profiles and write a snippet; you never see PROD rows.

Context. CC A1 distress counts a bureau bounced cheque (prm_bureau_alert_enriched,
bounced_cheque_amount > 0) dated by extract_date. extract_date (raw EXTRACT_DT) is the date we
pulled the report, not the date of the bounce. In PROD (cc_60_180), 55% of bounced CIFs repeat
the same amount across extracts, so an old bounce may keep the flag on (11,477 obs rows flagged
by the bureau only). stg_aecb_alert has DT_OF_RETURN and CONTRACT_STATUS_DT, which
build_alert_enriched renames (return_date, contract_status_date) and then drops in the final
projection. feature_retail_loans has aecb_bureau_pull_date and aecb_direct_debit_returns_6m.
We know little about these tables; treat every assumption below as unproven.

A. Inventory (read only; no data). Save tmp_validation/bureau_v01/inventory.md, under 80 lines:
   1. Every AECB/bureau dataset in conf/base/catalog (raw, stg, int, prm, feat, and
      feature_retail_loans' bureau inputs): name, source table, grain if documented, its
      date columns, the node that builds it, and its consumers.
   2. Everything the repo says about the AECB alert feed: docstrings, READMEs, data
      dictionaries (00_dictionary, schema_intelligence profiles, schema_registry.py), test
      fixtures. In particular: is an alert row an event notification (one row per event) or
      a snapshot of a contract at each pull? What do ALERT_DESC / the alert type values mean?
      What do DT_OF_RETURN, CONTRACT_STATUS_DT, OPN_DT mean? Quote file:line for each claim.
   3. The full column list of stg_aecb_alert (raw names) with type, and the candidate row key
      (CIF, contract / alert id, EXTRACT_DT, ...).
   4. Where aecb_bureau_pull_date and aecb_direct_debit_returns_6m in feature_retail_loans
      come from (raw table, column, how the 6m window is computed).

B. PROD snippet: tmp_validation/bureau_v01/bureau_v01_snippet.py plus a README.md with the run
   steps. It runs in a Kedro notebook (catalog, context exist).
   Rules: catalog.load only (no spark.read, no paths); model_id from
   catalog.load("params:model_id") and in the output filename; aggregates only — no ids,
   card/account/contract numbers, names or free text; top 25 per categorical; one JSON at
   context.project_path / "tmp_validation/bureau_v01/results_<model_id>.json"; commit and push
   only tmp_validation/bureau_v01/.
   Datasets: stg_aecb_alert, prm_bureau_alert_enriched, crx_cc_obs_base, feature_retail_loans
   (and any other bureau dataset part A shows holds bounces or returns). "Bounced row" = a row
   with the bounced-cheque amount > 0. "Key" = the row key from A3 without EXTRACT_DT.

   Hypotheses:
   B0  An alert row is an event notification: each bounce appears in one extract only.
   B1  The opposite: a row is a snapshot of a contract, re-sent at every pull, so a bounce
       repeats until it ages out of a bureau lookback window.
   B2  DT_OF_RETURN is the bounce date: populated on bounced rows, on or before EXTRACT_DT,
       and constant while the same bounce repeats.
   B3  A new bounce shows as the key's first bounced extract, or as a rise in the amount; a
       repeated amount is the same bounce.
   B4  Pulls follow a regular cadence (e.g. a monthly batch for the whole book), not
       on-demand pulls.

   Tables (all rows, and again for obs-base CIFs only where it says so):
   w1_columns    every stg_aecb_alert column: type, null share, distinct count (capped at
                 1000); for date-like columns min, max, and the lag EXTRACT_DT - column in
                 days (p1/p10/p50/p90/p99, share negative).
   w2_grain      rows vs distinct counts for each candidate key from A3, with and without
                 EXTRACT_DT.
   w3_pulls      distinct EXTRACT_DT values (count, min, max); rows per EXTRACT_DT day of
                 month (histogram) and per month; per CIF: distinct extracts (p50/p90/max) and
                 the gap in days between consecutive extracts (0, 1-7, 8-27, 28-35, 36-92, 93+).
   w4_return_dt  bounced rows: DT_OF_RETURN null share; lag EXTRACT_DT - DT_OF_RETURN in bands
                 (<0, 0-30, 31-90, 91-180, 181-365, 366+); non-bounced rows: DT_OF_RETURN
                 null share; CONTRACT_STATUS_DT the same.
   w5_repeats    per key ordered by EXTRACT_DT: transitions between consecutive extracts
                 (zero->bounced, same amount, rise, fall, bounced->zero, key absent next
                 pull) as counts and shares; run length of one bounced amount in extracts and
                 in days (p50/p90/max); share of runs where DT_OF_RETURN stays constant; share
                 of rises where DT_OF_RETURN changes.
   w6_alert_type bounced rows by alert type / description (top 25), with the w5 "same amount"
                 share per type.
   w7_obs        cc obs base (latest 6 observation months): obs rows bureau-flagged in the
                 3-month window when the bounce is dated by (a) extract_date, (b) DT_OF_RETURN,
                 (c) the first extract of each run from w5. Counts and the overlap of a/b/c.
   w8_frl        feature_retail_loans: aecb_bureau_pull_date min/max/null share and the
                 distinct pull dates per account (p50/p90/max); aecb_direct_debit_returns_6m
                 null share, share > 0, and p50/p90 where > 0.

C. Analysis (only when I give you results_cc_60_180.json): for B0-B4 a verdict (CONFIRMED /
   REJECTED / INCONCLUSIVE), the 3-6 numbers that decide it, and one line on what it means
   for dating a bureau bounce. Then: the column (or derivation) that best dates a bounce, and
   how many w7 obs rows change against extract_date. Don't propose code changes. Plain text,
   under 50 lines. Save it as tmp_validation/bureau_v01/summary.md, then commit and push.
````
