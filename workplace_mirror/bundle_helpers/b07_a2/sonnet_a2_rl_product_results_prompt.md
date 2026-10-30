# A2: retail-loan results by product (and by charge-off vintage at 180+) for the model workbook

Give this to the UAT Sonnet 5.5. Sonnet writes the snippet in UAT. You run it in PROD once per RL
model_id (`rl_60_180`, and `rl_180_plus` once its A2 output exists; switch `model_id` in
`globals_dev.yml` and reload the kernel), then commit and push the results. Pull in UAT in the same
Sonnet session: it checks the numbers and writes the workbook tables. Paste back
`tmp_validation/a2_rl_product/summary.md`. The workbook is generated from
`docs/locatability/build_a2_workbook.py` in the mirror repo, so the pasted summary is what fills it.

````text
Goal: the A2 model workbook needs the retail-loan results split by product (Personal Loans,
Personal Cash Loans, Auto) and, at 180+, by charge-off vintage. The final A2 output
(crx_rl_a2_locatability) does not carry the product, so join it in a validation snippet. You work in
UAT with no data: write the snippet, the user runs it in PROD per model_id and commits the results,
then you turn them into the workbook tables. Change no pipeline code.

What is known:
- crx_rl_a2_locatability: one row per (account_id, observation_date), month-end dates. Columns in
  a2_locatability/classify.py (_OUTPUT): a2_state, location_state, reachability_state,
  deceased_flag, deceased_source, location_rule (L1-L4), location_unknown_reason,
  reachability_unknown_reason, last_contact_date, attempt_days_in_window, last_uae_source,
  last_foreign_source, …
- rl_spine is month-end too and has loan_type and chargeoff_age_months. The temporary check node
  split_by_product (a2_locatability/b06_check.py) joins it the same way: on account_id (string) and
  observation_date, spine deduplicated on that key.
- The window W is 3 months at 60-180 and 6 at 180+ (_common.window_months). The b06 check's
  describe_a2_rules builds the same detail tables for the whole book; reuse its derivations
  (deciding source = last_foreign_source for L1, else last_uae_source; last contact in W / before W
  / never; call-day buckets) so the numbers match it.
- Latest month RL 60-180 (2026-08): 3,985 accounts; Skip 1,728, In Country 1,080, Unknown 1,177;
  Reachable 1,043, Non-Reachable 2,292, Unknown 650; deceased 29. The product totals must add up
  to these.

Deliverables per model_id, latest observation month, each count broken down by product (every raw
loan_type value, mapped to the three products; any other value and NULL kept as its own column and
named), plus a total column:
  T1 combined state: deceased, then the 9 location x reachability pairs (in_country, skip,
     unknown x reachable, non_reachable, unknown), and the account total;
  T2 location_state; T3 reachability_state (both on all rows, deceased included);
  T4 why Unknown: location no_evidence, location domestic_before_window, reachability
     no_dcore_record, reachability no_contact_in_window;
  T5 location rule x deciding source: L1 by source (login, credit_card, debit_card, dcore_note),
     L2 total, L3 by source (login, credit_card, debit_card), L4 by unknown reason;
  T6 reachability state x last contact (in W / before W / never), and Unknown-never split into
     no_dcore_record and the rest;
  T7 call days in W: 0, 1-2, 3-5, 6+;
  T8 deceased_source grouped: DCORE only, Way4 only, demographics only, more than one;
  T9 180+ model_ids only: T1 by vintage (chargeoff_age_months < 24 = early-stage charge-off,
     else late-stage; NULL its own column), products pooled.
Also: the join match rate (output rows with no spine row), and T1 by product for every month in
the output (rows only, for a trend check).

Hard rules:
- catalog.load only (no spark.read, no paths); model_id from catalog.load("params:model_id"), in
  the output file name; nothing hardcoded or overridden.
- Aggregates only: counts, no account ids, CIFs or customer rows. Exact counts (small ones too);
  the workbook computes the shares.
- Write context.project_path / "tmp_validation/a2_rl_product/results_<model_id>.json"; each table in
  its own try/except with the error recorded.
- Work only in tmp_validation/a2_rl_product/ (tracked); commit and push only that folder.

Deliverables:
1. a2_rl_product_snippet.py and a README.md with the run steps (one run per model_id, kernel reloaded).
2. After the user commits the JSONs, summary.md (no commentary beyond one line per check):
   - checks: each product split adds up to its total; the totals match the numbers above for
     rl_60_180; the join match rate. Write FAIL with the difference if one does not hold.
   - per model_id, T1-T8 (and T9) as markdown tables, rows in the order listed, one column per
     product then total, counts only. Check every number against the JSON; write NOT IN JSON when
     one is missing.
````
