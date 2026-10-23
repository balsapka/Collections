# Validation v01 — A1 distress sources and CASA liquidity coverage

Give the block below to the workplace Sonnet in UAT (branch `feature/persona_redesign_b01`, bundle 02
applied). Then:

1. **UAT:** Sonnet writes the snippet, then commits and pushes `tmp_validation/a1_v01/`.
2. **PROD:** pull and open a Kedro notebook (`kedro jupyter notebook`). Paste the snippet
   and run it. It writes `results_<model_id>.json` into the same folder.
   Run it for `cc_60_180` only (the `model_id` already in `globals_dev.yml`; cc_180_plus is
   skipped for now).
   Then commit and push only `tmp_validation/a1_v01/`.
3. **UAT:** pull and ask Sonnet for the analysis (step B of the prompt). Paste the summary
   back here.

````text
Task: a PROD validation snippet for the CC A1 ability engine. You work in UAT with no data:
you write code and analyse a results file, you never see PROD rows.

Context. src/enbd_collections/pipelines/crx_persona/a1_ability/ (signals.py,
classify.py) and cc_a1_ability_v2/ (pipeline.py, b01_check.py) build A1 per
(account_id, observation_date). The PROD check run for model_id=cc_60_180 (311,277 rows)
showed:
- Distress: 36,235 rows flagged. Bureau-only 11,477, internal-only 23,724, both 1,034.
  Internal events in the 3-month window / rows flagged, by reason_for_excluding:
  CHEQUE RETURNS 30,425 / 10,911; DDS Rejects/Reversal 1,357,274 / 11,438; RETURNS
  9,630 / 5,065. DDS has ~119 events per flagged row; the other reasons have ~2-3.
- Liquidity level: none 93% (288,486 + 2,594 + 3,335 of 311,277), weak 4%, adequate 1.5%.
  Income level: none 97%.

Hypotheses:
H1  The DDS event volume is duplication, not real events: comp_financial_tran_repos_dly
    repeats the same transaction across edp_load_date partitions, and/or one DDS
    instruction is retried many times, and/or a few CIFs dominate.
H2  "DDS Rejects/Reversal" and "RETURNS" are not all customer distress. They include
    reversals or returns that are corrections, refunds or bank-side events.
H3  The generic RETURNS reason adds few rows that no other source flags. Dropping it changes
    few A1 states.
H4  Liquidity "none" means mostly "no CASA data at the bank" (the customer is CC-only),
    not "has CASA but the balance is below 1,000 AED".
H6  The unknown state matches data coverage. About 66% of this population hold a CASA account
    at the bank (business figure). Rows with no CASA data should be ability_unknown unless the
    bureau flags distress. If they land in ability_low instead, CASA-less customers are being
    read as "no ability".
H7  Salary has stopped, not gone missing. About 50% of the population had a salary credit at
    some point, but only ~3% of rows have one in the last 3 months. Expect most former
    salary customers' last credit to fall before the 3-month window (salary stopped or moved
    before or during delinquency).
H8  Bureau bounces are dated by the extract, not by the bounce. The engine flags a row when
    prm_bureau_alert_enriched has bounced_cheque_amount > 0 with extract_date in the window.
    If the same bounce repeats in every monthly extract, old bounces keep the flag on
    (bureau-only rows: 11,477). Look for a real bounce/event date column in the table.
H5  feat_payroll_indicator.month_number is stamped one month after the salary month
    (in PROD, a payroll flag in month M+1 matched a recovered salary credit in month M
    98% of the time).

A. Write the snippet: tmp_validation/a1_v01/a1_v01_snippet.py, plus a README.md with
   the two run steps. The snippet runs in a Kedro notebook, where `catalog` and `context`
   exist.
   Rules:
   - Load data only with catalog.load(<dataset name>). No spark.read, no paths, no
     hardcoded tables. model_id = catalog.load("params:model_id"). Never set or override it.
   - Use the dataset names that the crx_persona pipelines use:
     crx_cc_obs_base, crx_cc_a1_internal_returns, crx_cc_a1_liquidity_signals,
     crx_cc_a1_ability_b01_check, prm_bureau_alert_enriched, comp_financial_tran_repos_dly,
     wm_fea_casa_eod_avg_balance, feat_payroll_indicator.
     Import lookback_floor, parse_yyyymmdd and RETURN_REASONS from the package. Don't
     copy them.
   - Scope comp_financial_tran_repos_dly exactly as build_internal_returns does: leftsemi
     to the obs base's CIFs first, then edp_load_date and tran_date >= lookback_floor(obs, 100),
     reason_for_excluding in RETURN_REASONS. It has 2.4B rows, so never scan it unscoped.
   - Aggregates only. The file is committed to git. No cif_id, account_id, card/account
     numbers, names or free-text narration. Distributions, counts and code values only.
     For any group-by on a code column, keep the top 25 values and fold the rest into
     "(other)".
   - Find the transaction-identity and type columns of comp_financial_tran_repos_dly in this
     repo and the sibling repos (retail.feature_space, wealth_management): a transaction id,
     a part/serial number, amount, debit/credit indicator, transaction type/sub-type/code.
     The snippet checks which of them exist (df.columns) and records the missing ones in
     the results, instead of failing.
   - Write one JSON file with pandas/json on the driver:
     context.project_path / "tmp_validation/a1_v01/results_<model_id>.json".
     Use one key per table below, each a list of records. Also record "model_id",
     "run_at" and "columns_found".
   - Don't touch src/ or conf/. Commit only tmp_validation/a1_v01/, then push.

   Tables (window = the 3 complete calendar months before each observation month, as in
   b01_check._in_last_3_months, unless stated otherwise):
   t1_dup (H1)       per reason, on the scoped raw rows: rows; distinct
                     (cif_id, tran_date); distinct (cif_id, tran_date, amount); distinct
                     transaction key (id + part serial + tran_date, if present); p50/p90/max
                     of distinct edp_load_date per transaction key; number of CIFs; p50/p90/
                     p99/max of rows per CIF; share of rows from the top 1% of CIFs.
   t2_types (H2)     per reason x each type/code column found x debit/credit: rows, distinct
                     transaction keys, p10/p50/p90 amount (top 25 per reason).
   t3_overlap (H3)   per obs row, flags for bureau / CHEQUE RETURNS / DDS / RETURNS in the
                     window: count of rows for every combination of the 4 flags (16 rows).
   t4_impact (H3)    rows flagged ONLY by RETURNS, and rows flagged ONLY by DDS: crosstab of
                     a1_state x a1_points_total x casa_active_3m (from
                     crx_cc_a1_ability_b01_check joined with crx_cc_a1_liquidity_signals).
   t5_casa (H4)      per obs row: has_casa_data (any casa_m1..m3 not null),
                     ever_in_casa_table (the CIF appears in wm_fea_casa_eod_avg_balance at
                     any week), casa_active_3m, ext_card_payment_max_3m not null, the max
                     casa_m1..m3 band (null, <=0, 0-1000, 1000-3000, 3000+),
                     a1_liquidity_level, a1_state and bureau_distress (bureau flag in the
                     window, as in t3). Count rows for each combination.
   t7_salary (H7)    per obs row, from wm_fea_salary_days_since_increment (all weeks up to the
                     observation date; credit date = snapshot date - days since salary, as in
                     signals._internal_salary): salary_ever (any credit before the
                     observation date), months from the last credit to the observation month
                     (bands: 1-3, 4-6, 7-12, 13-24, 25+, never), and last-credit amount band
                     (<1000, 1000-3000, 3000+), crossed with a1_income_level and
                     ever_in_casa_table. Count rows for each combination.
   t8_bureau (H8)    prm_bureau_alert_enriched for the obs base's CIFs: extracts per CIF (p50/
                     p90/max); for CIFs with bounced_cheque_amount > 0, the number of
                     consecutive extracts with the same amount (p50/p90/max) and the share
                     whose amount never changes; every date-like column found, with its
                     null share and the lag to extract_date in days (p10/p50/p90).
   t6_payroll (H5)   feat_payroll_indicator: count of rows by day-of-month of the parsed
                     month_number, and min/max month_number vs min/max observation_date of the
                     obs base.

B. Analysis (only when I give you the committed results file): read
   results_cc_60_180.json. For each hypothesis H1-H8, give:
   - a verdict: CONFIRMED / REJECTED / INCONCLUSIVE;
   - the 3-6 numbers that decide it;
   - one line on what it means for the engine.
   Then add:
   - H1: the distinct-event count per reason, if duplicates are dropped by the best key
     found;
   - H2: the code values that look like non-distress, with their row share;
   - H3: how many A1 states would change if RETURNS were dropped. The rule: distress lowers
     the state one level; with 0 points, no distress and casa_active_3m = 0, the state is
     unknown, otherwise low.
   - H6: the share of rows with no CASA data that end up ability_low, and why (bureau
     distress or something else);
   - H7: the share of salary_ever rows whose last credit was 4+ months before observation,
     with the months-since bands;
   - H8: whether a bounce date exists, and the share of bureau-flagged rows whose bounce is
     really older than the window (if that can be told);
   - List columns_found and any table that came back empty.
   Don't propose code changes. Plain text, under 50 lines. Save it as
   tmp_validation/a1_v01/summary.md, then commit and push.
````
