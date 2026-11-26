# UAT Sonnet prompt: UC1 refresh — has everything been extracted, and what does it cover?

Paste everything below the line into the UAT Sonnet session.

---

Goal
The UC1 team refreshed their outputs for the August month end and say `signal_level_posteriors` now holds the signal
history over time, for every date up to its `snapshot_date`. The persona pipelines have been rerun to 2026-09-30. Find
out, with numbers, (1) whether UC1 has now read all the calls it could, (2) what the refresh covers in our persona
population at the August and September month ends, and (3) whether the posteriors table could give us a dated state per
month end. Exploration only: no integration decision here.

Context and decisions already made (do not reopen)
- Agreed inputs: `customer_signal_export` (state value = UC1's `estimated_value`, as is) and `crx_uc1_metadata`. Agent
  remarks are UC1 data and stay in. The posteriors table is NOT an agreed input; here we only assess it.
- Axis numbers changed: A1 = deterioration, A4 = ability (A2 locatability, A3 credibility unchanged). Dataset names
  have not changed: `crx_<p>_a1_ability` is the A4 ability axis, `_dpd_journey` outputs are A1. Use the new numbers in
  your text.
- Coverage is read against the whole model population and against the A2 reachable pool, side by side; there is no
  coverage target. No minimum n: report n beside every share.
- Earlier delivery for comparison (snapshot 2026-10-31, built 2026-11-23): 5,040 CIFs in the export, calls 2026-03-06 ..
  07-16 in the metadata, 16% (cards) / 35% (loans) of the model CIFs' calls extracted; at 2026-07-31, 891 card and
  334 loan accounts with a reading (4.8% / 9.0%).

Questions
Q1 What arrived. Every UC1 table in the shared store (`current/outputs/timelines/*`, `current/outputs/extracted_signals`,
   `metadata`): partitions / `snapshot_date` values, row and CIF counts, last write time, date range of the calls and
   observations. What changed since the 2026-10-31 delivery (new CIFs, new calls, calls after 2026-07-16).
Q2 Has UC1 read everything it could? For calls of the persona CIFs, 2026-01 .. 2026-09:
   - calls in `crx_uc1_metadata` vs calls with any extracted observation (transcript source) — share by call month,
     product, model_id, DPD band;
   - calls in the raw transcript store (`stg_genesys_transcripts` or whatever the catalog holds; say which) that are
     not in `crx_uc1_metadata` at all;
   - DCORE call-type follow-ups (outbound / callback / inbound: OC / CB / IC, `_dcore_codes.py`) with no conversation in
     the metadata that day, by month — the calls UC1 cannot see;
   - agent remarks: DCORE follow-ups with remark text vs remark observations UC1 extracted, by month.
   Give one waterfall per product: collections calls (DCORE) → calls with a transcript → in UC1 metadata → extracted.
Q3 Coverage at 2026-08-31 and 2026-09-30, for cc_60_180, rl_60_180, cc_180_plus, rl_180_plus: accounts in
   `crx_<p>_obs_base`; with a UC1 export row on the CIF; by evidence (transcript / remark / both), A2 reachable vs not,
   DPD band, A4 ability state, A3 credibility level; with a call in the last 90 days but no reading. Same table at
   2026-07-31 to show what the refresh added.
Q4 Posteriors over time. Structure (grain, columns, date column, levels per signal, how far back). For each CIF ×
   signal: does the posterior on the export's `snapshot_date` reproduce `estimated_value` (share equal, by signal)? Can
   a month-end value be read for 2026-07-31 / 08-31 / 09-30 (rows with a date on or before each, n CIFs per month end)?
   Compare with rebuilding the month-end value from `proposer_level_observations` using UC1's `parameters.json`.
Q5 Readiness. For each month end 07 / 08 / 09: accounts with a reading, and whether a payment outcome exists for the
   following month in our data (last payment date in the persona inputs). Which month end gives the most readings with
   an outcome.

Rules
`catalog.load` only; UC1 tables are in `conf/base/catalog/catalog_tmp_uc1_full.yml` (`crx_uc1_full_export`,
`_evidence`, `_posteriors`, `_time_weighted`; the evidence root fails to load, so list the `snapshot_date=` folders and
read them one by one) and `catalog_crx.yml` (`crx_uc1_customer_signal_export`, `crx_uc1_metadata`,
`crx_uc1_extracted_signals`). Add an explicit temporary entry to `catalog_tmp_uc1_full.yml` for anything missing (no
dataset factories); say which. Raw tables that are not catalogued may be read read-only in the same session; say how.
model_id = `catalog.load("params:model_id")`, never hardcoded. Join persona rows to UC1 on `cif_id`. Committed outputs:
aggregates only, no account, CIF, agreement, conversation or agent ids, no transcript or remark text; cells under 10 as
"<10". New tracked folder `tmp_validation/uc1_refresh/`; commit only that folder. No pipeline, catalog (beyond the temp
file) or registry change.

Deliverables
1. Snippet + README; the user runs it in PROD once per model_id and commits `results_<model_id>.md`.
2. Back in UAT: `summary_uc1_refresh.md` (under 150 lines): what arrived (Q1), the waterfall per product with the
   verdict "UC1 has / has not read everything it could, and where the gap is" (Q2), the coverage tables (Q3), whether
   posteriors give a usable dated value per month end (Q4), and the recommended month end for the next analysis (Q5).
   Mark every number you could not compute and why.
