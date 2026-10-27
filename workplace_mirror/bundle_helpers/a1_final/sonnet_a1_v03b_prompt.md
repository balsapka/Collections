# A1 v03b: the v03 parts the first run did not cover (CC and RL)

Give this to the UAT Sonnet 5.5. The first v03 run (`tmp_validation/a1_v03/`, CC only) was
written from an earlier version of the v03 prompt; its summary has no bureau-input check, no
salary timing, no EOS check, no activity-gate test and no RL. Same flow as before: Sonnet
extends the snippet, you run it in PROD for `cc_60_180` and then `rl_60_180` (`model_id` in
`conf/dev/globals_dev.yml`), push the JSONs, Sonnet writes the summary, and you paste back the
new summary sections. The full table definitions are in `sonnet_a1_v03_grr_prompt.md`
(copy it in too if the Sonnet does not have it).

````text
Goal: finish A1 v03 so the GRR results note can be written. The existing
tmp_validation/a1_v03/ (snippet, results_cc_60_180.json, summary.md) covers v1-v8 for
cc_60_180 and the recompute check (0 mismatches). Add what is missing and run it for both
model_ids. Change no pipeline code.

Already decided, do not revisit: the engine logic (crx_persona/a1_ability/README.md);
stg_aecb_salary_history.subj_salcr_hist_ref_mnth is MMYYYY (staging docstring, e.g. "072023"),
so the engine's parse is right and the DE model's "YYYYMM" is wrong; bureau distress repeats
(same amount in a later extract) will be treated as the same bounce; the WM salary feature is
a monthly sum of salary-flagged credits, first-of-month dated, forward-filled, EOS excluded.

What to add (definitions in the v03 prompt; keep the snippet's existing tables, rules and
JSON layout, and add the new keys):
1. v0_bureau — validate the three bureau inputs (bridge, salary history, alerts) with a
   verdict per input. Priority question: 88% of CC Unknown CIFs have a bureau pull in 12
   months but only 0.18% of CIFs have any bureau salary in 24 months. Is that the data (no
   salary reported for most pulls) or the join (bridge, file id, edp_load_date)? Show the
   funnel per model_id: base CIFs -> in the bridge -> with a bureau file in 24 months -> with
   any salary-history row for those files (any month) -> with a parsed month in the 24
   months -> with an amount > 0.
2. The missing piece of v2: rows by income reason (N1 / N2-N4) x bureau pull in 12 months
   without any bureau salary.
3. v2b_salary_timing and v2c_eos.
4. Part D: part A code reading first (how wm_fea_casa_cc_inflow_outflow's CASA columns are
   built, and which columns tell customer-initiated from administrative transactions, with
   file:line), then v9_activity (H-A for both model_ids, H-RL1 for RL) and v10_dds_emi (H-RL2).
   CC matters as much as RL here: 68% of CC Low is 0 points + a CASA flow.
5. RL: the snippet picks dataset names by model_id (crx_rl_* datasets; the RL anchor is the
   EMI, int_loan_master.installment_due_amount; RL income also reads feature_retail_loans).
   Run every table for rl_60_180 and keep the recompute check at 0 mismatches.

Hard rules: catalog.load only (no spark.read, no paths); model_id from
catalog.load("params:model_id") and in the output filename; aggregates only (no ids, account
or card numbers, names, free text); reuse the engine's own functions; each table in its own
try/except with the error recorded, so one failure does not hide the others; never join
cc_spine, the DCORE spine or prm_contract on the date (they are on mid-month dates in PROD).
Check yourself before handing over: the snippet compiles, every catalog name exists in conf/,
and table definitions match the v03 prompt.

Deliverables:
- the extended snippet and README run steps, committed and pushed (UAT);
- after the user pushes results_cc_60_180.json and results_rl_60_180.json: extend summary.md
  with section 0 (bureau inputs: funnel + verdict), section 3 (salary timing, the window-total
  rule's moves between levels and states, EOS), the pull-without-salary count in section 4,
  section 8 (hypotheses H-A, H-RL1, H-RL2: CONFIRMED / REJECTED / INCONCLUSIVE with the 3-5
  deciding numbers per model_id, and how many Low rows would become Unknown if only
  customer-initiated transactions counted, and for RL if EMI repayments did not count either),
  and an RL column or block for every section. Numbers only, no code proposals; under 140
  lines. Commit and push.
````
