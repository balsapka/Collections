# UAT Sonnet prompt: make the UC1 refresh check a reusable rerun

Paste everything below the line into the UAT Sonnet session.

---

Goal
Turn the UC1 refresh check in `tmp_validation/uc1_refresh/` into a check we rerun unchanged every time the UC1 team
adds data, and fix what the first run (`summary_uc1_refresh.md`, 2026-11-26) got wrong or left out. Update the
existing snippet in place; do not start a new one. Coverage and data understanding only: no payment-by-signal analysis
(that is a separate rerun of the bundle 31 measurements).

Decisions already made (do not reopen)
- Agreed inputs: `customer_signal_export` (state = UC1's `estimated_value`, as is) and `crx_uc1_metadata`; remarks
  are UC1 data and stay in. `signal_level_posteriors` is being assessed as UC1's dated estimate, not adopted.
- Axis numbers: A1 deterioration, A2 locatability, A3 credibility, A4 ability. Dataset names unchanged
  (`crx_<p>_a1_ability` is the A4 axis). Use the new numbers in text.
- No coverage target, no minimum n: n beside every share; whole population and A2 reachable side by side.

What to change
1. Snapshot handling. Detect the latest `snapshot_date` partition of every UC1 table at run time (the evidence root
   does not load: list the folders and read them one by one), and record it. Results file:
   `results_<model_id>_<export snapshot>.md`, so reruns never overwrite earlier ones.
2. Model ids. Run for all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus); for 180+ the coverage and
   conversation waterfall are enough, skip any section that is empty and say so.
3. Call waterfall. Step 1 = DCORE call days (OC / CB / IC) with a right-party contact (`RIGHT_PARTY_CONTACT` in
   `_dcore_codes.py`), not every attempt; keep all-attempt days as a context line only. Then: transcript in the store
   that day → conversation in UC1 metadata → read by UC1 (extraction ledger, and separately an observation in the
   proposer evidence; say which table you treat as "read" and why). By call month. Keep the conversation-level
   waterfall (store → metadata → read), including conversations after the last metadata call date.
4. Coverage at every month end from 2026-04-30 to the latest persona month end, three measures side by side:
   M1 export row on the CIF (bundle 31's measure; it uses evidence up to the export snapshot, so for past month ends
   it looks ahead — label it); M2 UC1 evidence in the 90 days strictly before the month end, split transcript only /
   remark only / both; M3 a posterior row dated on the month end. Whole population and A2 reachable; by DPD band,
   A4 state, A3 level.
5. What the readings say. For M2 and M3, per signal, the share of not-stated / not-detected levels, split by
   transcript vs remark-only evidence. We expect remark readings to be mostly empty; show whether they are.
6. Posteriors. Per month end: age of the latest evidence behind each CIF × signal (0-30 / 31-90 / 91-180 / >180
   days, from the evidence dated on or before the month end). Why the grid starts in 2022: earliest evidence date by
   source / proposer type, and whether any proposer is UC2 or bank data (list the proposer / source values with
   counts). Repeat the reproduction check (posterior top level vs rebuild from the evidence with `parameters.json`) at
   each month end; keep the export reproduction at the snapshot.
7. Outcome readiness. Last payment date in the persona inputs and which month ends have a one-month outcome.

Rules
`catalog.load` only; UC1 entries in `conf/base/catalog/catalog_tmp_uc1_full.yml` and `catalog_crx.yml`; add any
missing temporary entry to `catalog_tmp_uc1_full.yml` only, explicit, no dataset factories. model_id =
`catalog.load("params:model_id")`, never hardcoded. Join persona rows to UC1 on `cif_id`. Committed outputs: aggregates
only, no account, CIF, agreement, conversation or agent ids, no transcript or remark text; cells under 10 as "<10".
Commit only `tmp_validation/uc1_refresh/`. No pipeline, catalog (beyond the temp file) or registry change.

Deliverables
1. Updated snippet + README with one run command per model_id (the user switches `model_id` in `globals_dev.yml`
   and reruns it on every UC1 refresh).
2. After the user commits the PROD results: `summary_uc1_refresh_<export snapshot>.md` (under 150 lines): what
   arrived; what changed since the previous results files in the folder (new CIFs, new calls read, coverage by month
   end); the waterfall verdict "UC1 has / has not read everything it could, and where the gap is"; the M1 / M2 / M3
   coverage table; the empty-reading shares; whether posteriors give a usable dated value (evidence age, 2022 start,
   UC2 inputs). Mark every number you could not compute and why.
