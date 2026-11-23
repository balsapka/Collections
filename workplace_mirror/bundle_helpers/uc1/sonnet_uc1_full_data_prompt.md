# UAT Sonnet prompt: UC1 signal export: exploration and validation against the persona

Paste everything below the line into the UAT Sonnet session. Context for Sonnet: the dataset description the UC1
team published (`uc1_signal_export_datasets.md`, pasted after the prompt).

---

Goal
The UC1 team has populated six tables in the shared file store (`.../05_feat/file_store/current/outputs/timelines/`):
`customer_signal_export` (official, primary), `proposer_level_observations` (official, the evidence behind it),
and `signal_level_posteriors`, `time_weighted_signal_aggregation`, `simple_signal_aggregation`,
`signal_level_conflicts`. Their description is pasted below. Until now, bundle 26 (the UC1 stated block,
`uc1_stated` + `cc_` / `rl_uc1_stated`) and three earlier validations (`tmp_validation/uc1_uc2/`,
`tmp_validation/uc1_signals/`) worked on a small extracted sample (60-180 only, transcripts only, no date, no
confidence). Nothing about UC1 is decided yet: every decision waits for this data. We want five things:
1. what exactly was delivered, whether it is the full transcript run, and whether bundle 26 still runs on it;
2. who it covers, and whether the covered customers are a selected group;
3. how trustworthy the new fields are (confidence, agent remarks, estimate vs latest vs average, bank
   corroboration, repayment text), and whether past month ends can be read point in time;
4. whether each integration candidate (D1–D8 below) meets the bar, and whether each sample finding (S1–S11 below)
   holds, changes or fails;
5. the gaps between what customers say on calls and what DCORE records (promises, disputes, requests), where they
   sit, and whether they come from agents' logging or from the data.

Decided, to follow
- UC1 signals are what the customer said (transcripts) or what the agent wrote (remarks), as extracted. We never
  treat them as true. We test only (a) whether they line up with what the customer does next and (b) whether they
  are consistent with our observed data.
- `supporting_data` is built from UC2 features, i.e. partly from our own data (income, payment capacity). It is
  never used as evidence that a signal is right, and never as a predictor next to A1. Describe it, and measure how
  much of `estimated_value` depends on it (Part 3).
- UC1 outputs are taken as they are for the pipeline. For validation only, you may recompute values from
  `proposer_level_observations` (Part 3); nothing recomputed goes into a pipeline.
- Persona key stays A1–A4 (rules and states fixed). UC1 can only fill (inside A1 Unknown / A3 no_promise),
  cross-check (discrepancy flags), treat (reason, request, period, dispute) or give context. A3 is signed off: a
  transcript-promise effect on A3 is measured (D1), not proposed as a rule change.
- Bar for any fill or flag: ≥ 5 pp paid difference or ≥ +0.02 AUC inside the target state, in both products,
  n ≥ 100 per cell. Treatment hints and context are descriptive, no bar.
- model_ids: all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus) for every Part; where n is too small, say
  so and give n.
- Point in time: a UC1 reading counts at a month end only if its evidence is dated strictly before it
  (`observed_at` < month end for `proposer_level_observations`). The export is one snapshot: it is point in time
  only at its own `snapshot_date`.
- Two units:
  - Month-end view (decisions): account-months of crx_<p>_obs_base, UC1 reading per CIF from evidence before the
    month end, UC2 states (A1–A4, DPD band) at that month end. Outcomes paid_due / paid_any over the next 1 and
    3 months, as in the A3 results run. Month ends: from the first month with evidence to the last with 3 months of
    outcome; months with only 1 month of outcome reported apart. Say the last payment date available.
  - Call-anchored view (logging gaps, requests): each customer-day observation of a CIF, joined to every account
    of that CIF in crx_<p>_obs_base at the last month end strictly before the day. Outcomes after the day:
    pay30_due = payments in days 1–30 ≥ max(one month's due at the prior month end, 100 AED); pay30_any ≥ 100 AED;
    pay45_due / pay45_any over 45 days; days_to_pay to the first payment ≥ 100 AED within 45 days. Only days with a
    full 45-day window. with_delay / partial / weeks may pay late or below the due: always show the 45-day and
    _any versions beside pay30_due.
- Every result table: n accounts and n account-months (or customer-days), Unknown / not-detected / no evidence as
  their own rows, and a HIGH-confidence-only version where confidence exists.
- Observed data (catalog, read only, as in `tmp_validation/uc1_signals/`): income per CIF month = larger of
  feat_cif_internal_salary_monthly.salary and feat_cif_bureau_salary_monthly.bureau_salary;
  feat_cif_casa_balance_monthly; feat_cif_casa_inflow_outflow_salary_monthly; DCORE promises and follow-ups as A3
  reads them (prm_dcore_account_agreements and A3's promise events); a3_dispute_flag on
  crx_<p>_a3_payment_credibility; RL dispute codes in DCORE (find them; say which); restructures (A4 restructure
  flag or crx_rl_restructure_chains; say which and how far the data reaches). Persisted outputs as they are; do
  not re-run any engine.

Part 0 — What was delivered (intake)
0.1 For each of the six tables (and the `parameters.json` companion of `proposer_level_observations`: find it with
    `hdfs dfs -ls`, paste its contents; it holds settings only): schema, row count, distinct cif_id,
    snapshot_date values / partitions, date range of `observed_at` (or of the call dates it holds), write time
    (`hdfs dfs -ls`). How the tables relate: is the export built from posteriors / time-weighted? Same snapshot
    in all?
0.2 Signals and levels in the export vs bundle 26's schema (payment_capacity none / partial / full; payment_intent
    no_payment / with_delay / partial / payback_full; delinquency_reason lost_employment / reduced_employment /
    has_employment / increased_obligations; payment_period weeks / salary_cycle_dependent / months_or_longer;
    dispute system_problem / customer_scammed / other; request detected; fraudulent_customer detected;
    repayment_specifics amount / date / plan). List every level new, renamed or gone; whether request now carries
    a type; fraudulent_customer detections.
0.3 Grain checks: one row per cif × signal × snapshot in the export; 10 rows per customer; placeholder counts
    (`not-detected`, `N/A`, null) per column; tied `estimated_value` ("a|b") per signal; proposer rows per
    customer-day; multi-level statements (`named_level_count` > 1) per signal and source, and how many
    transcript picks the alphabetical `is_pick` changes vs the first named level (if the order is recoverable).
0.4 Is this the full transcript run? Calls in `crx_uc1_metadata` per month vs customer-days with a transcript
    observation per month; share of called CIFs (per month, per DPD band at the call) with any transcript
    observation. Remarks: customer-days with a remark and no transcript.
0.5 Bundle 26 compatibility. Two of its inputs (`crx_uc1_simple_signal_aggregation`,
    `crx_uc1_signal_level_conflicts`) sit at paths that were overwritten. Check that every column bundle 26
    requires still exists (metadata: conversationid, cif_id, conversationstart; extracted_signals:
    conversationid, model_version; signal_level_conflicts: conversationid, signal, value, observation;
    simple_signal_aggregation: cif_id, signals_json) and that every level it reads is still in the old value set.
    Do not run the pipeline. Agreement of the export's `estimated_value` with the persisted crx_<p>_uc1_stated
    (A5 / A6, latest month) for the CIFs in both: crosstab, and the share now `not-detected` / newly covered.

Part 1 — Coverage and selection
1.1 Month-end view, per month end: account-months whose CIF has any observation in the prior 90 days and ever
    before: by source (transcript only / remark only / both), split by a1_state, a3 level, a2 state, DPD band.
    At the snapshot: share of the latest month with an export row, and with a non-`not-detected` estimate per
    signal, by confidence.
1.2 Selection: within each A3 level and each A1 state, paid_due of covered vs not covered account-months. Repeat
    the sample check: DCORE promise events with a transcript observation on the CIF within ±7 days vs without
    (sample cards 15% vs 41% paid). If the gap holds, Parts 4–5 are read within comparable groups and you say so.
1.3 Extraction by DPD at the call (sample: calls at 61+ DPD mostly extracted, the gap was 1–60 DPD).
1.4 180+: observations per month end, both products; if n allows, Parts 2, 4 and 5 run there too.

Part 2 — Quality of the new fields (month-end view unless stated)
2.1 Confidence: level × confidence per signal; paid_due by level within confidence. Does HIGH separate payers more
    than MEDIUM / LOW? (It measures a margin, not accuracy.)
2.2 Transcript vs remark: on customer-days where both name a level for the same signal, agreement per signal;
    payment when they agree vs disagree; remark-only vs transcript-only readings, payment by level. Where do
    remarks come from? Share of remark days with a DCORE follow-up / promise record on the CIF the same day; if
    remarks are DCORE notes, a remark-named promise may already be an A3 event (measure the overlap).
2.3 Which field to read: `estimated_value` vs `latest_value` vs `average_value` (and `average_count`). Share
    differing per signal; for capacity and intent, paid_due ordering and AUC inside A1 Unknown and inside A3
    no_promise for each field, at the snapshot (or the last month end that has outcomes, Part 3).
2.4 `historic_consistency`: share Agree / Disagree / N/A; paid_due by level within each.
2.5 `supporting_data`: distribution for the levels where it exists; crosstab with a1_state and with the A1 income
    signals (circularity, not validity).
2.6 Repayment text: share of `latest_value` / `agent_remark_value` per slot that is a clean amount, a clean date,
    a percentage, a range, words, a redaction token (count per token type; never print the free text). Clean
    amounts: ratio to one month's due at the prior month end (bins); clean dates: days after the observation
    (bins); payment by bin.

Part 3 — Point in time and backtest
3.1 List the export snapshots and proposer partitions available. For each month end, share of the snapshot's
    export rows whose evidence includes observations on or after it.
3.2 Reproduce `estimated_value` and `confidence` at the snapshot from `proposer_level_observations` (+
    `signal_level_posteriors` for the bank component, `parameters.json` for the settings; read UC1's code if it is
    available): match rate per signal. Also the estimate without the bank component: how often does
    `supporting_data` change the published level?
3.3 If 3.2 matches ≥ 99% (without the bank component, or with a point-in-time bank component), recompute the
    estimate at each earlier month end from evidence before it, for validation only, and run Parts 2 and 4 on
    every month end. Otherwise use the latest transcript level strictly before the month end (and its
    age) as the point-in-time reading, and the export only at its snapshot. Say which one Parts 2 and 4 use.
3.4 Stability: month to month, share of CIFs whose capacity / intent reading changes.

Part 4 — Decisions (bar above; month-end view; outcome paid_due / paid_any at 1 and 3 months)
D1 Transcript promises as A3 events (what-if, no pipeline change). Transcript promise = intent payback_full /
   partial / with_delay with an amount or a date named, on a customer-day with no DCORE promise on any account of
   the CIF within ±7 days. Add each one as a promise event (event day = the observation day; deadline and
   kept / not kept exactly as A3 judges a DCORE event, a payment on the day counts), recompute Dimension A and the
   state (B, C, refusal unchanged). Report level and state moves, moved rows' paid_due vs the level left and
   joined, state AUC vs persisted A3 (account bootstrap, 200 draws), and transcript promises as a share of all
   A3 promise events. Sample: 4 per 1,000 rows moved, AUC +0.001. Run it with remark-named promises too, apart.
D2 Flag: promise on the call, none logged on the CIF within ±7 days: paid vs no promise and vs a matched promise,
   within A3 level.
D3 Flag: dispute stated, A3 dispute flag false at the next month end: paid vs no stated dispute, within A3 level
   (loans: against the RL dispute codes, as A3 has no loan dispute flag).
D4 Fill: stated capacity inside A1 Unknown: able > partly > not stated > unable ordering, paid_due per level,
   AUC inside Unknown.
D5 Fill: stated intent, and an amount / date named, inside A3 no_promise: the same.
D6 Discrepancy flags vs their concordant group: says able / payback_full while A1 Low; says capacity none while
   A1 High / Moderate or CASA balance ≥ one month's due; says has_employment while income stopped; says
   lost_employment while income continues (income classes as in `tmp_validation/uc1_signals/` Part C).
D7 Treatment: reason, request (by type if delivered), payment period by A1 × A3 (counts = demand); pay45_any
   after each request type (call-anchored).
D8 180+: Part 1, then D2–D5 if n allows.

Part 5 — Logging gaps (call-anchored)
5.1 Unlogged promises: share of transcript promises with no DCORE promise on the account / the CIF within ±3 and
    ±7 days (sample: 60% cards / 85% loans on the CIF within ±7). The reverse: DCORE promises within ±3 days of an
    observation where no paying intent was stated.
5.2 Where the gap sits: the same share by month, product, DPD band, call direction, campaign / queue, agent team
    (aggregated, no agent ids), call length, promise type (payback_full / partial / with_delay; amount vs date
    named), confidence and source (transcript / remark). Use whatever metadata exists; say which fields. A gap
    spread evenly points to the feed; one concentrated in teams or queues points to logging practice.
5.3 Timing and accuracy of logged promises: days from the call to the DCORE entry; does the logged amount / date
    match the stated one (clean values only, ±10% / ±3 days)?
5.4 Disputes: share of stated disputes with no A3 dispute flag (account and CIF) at the next month end, by dispute
    type; loans against the RL dispute codes.
5.5 Requests: restructure, settlement, waiver, deferral (or `detected` if untyped) vs any matching DCORE record or
    restructure within 90 days.
5.6 Does it matter: pay30_due / pay45_any of unlogged vs logged promises vs no promise, within A3 level.

Part 6 — Sample statements re-checked (one line each: holds / changes / fails, with the new numbers)
S1 UC1's levels match our recomputation (0.5, 3.2). S2 Coverage 10–13% cards / 12–19% loans with any call in
90 days, 3% / 5–8% extracted, no 180+ (1.1, 1.4). S3 Covered customers are a selected group, 15% vs 41% (1.2).
S4 60% / 85% of transcript promises unlogged on the CIF; unlogged pay more than no promise on loans (5.1, 5.6).
S5 Stated disputes are almost never in A3's flag (5.4). S6 Specific statements go with payment: employed,
salary-cycle period, amount or date named, restructure / settlement / waiver requests; card settlement requests the
exception (D7, plus each level vs not detected within A1 / A3 states). S7 Inside A1 Unknown a stated reading pays
about twice no reading; able > unable on cards (D4). S8 Able vs partly able and the intent levels barely separate
(D4, D5). S9 Job and income claims loosely match our income data and the match does not change payment (D6). S10
Transcript promises as A3 events move almost nothing (D1). S11 Calls at 61+ DPD are mostly extracted (1.3).

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name. The four tables not in
the catalog yet (`customer_signal_export`, `proposer_level_observations`, `signal_level_posteriors`,
`time_weighted_signal_aggregation`) get explicit entries in a temporary `conf/base/catalog/catalog_tmp_uc1_full.yml`
(same path pattern as the existing `crx_uc1_*` entries; no dataset factories: the workplace Kedro does not resolve
them). Never add rows across `proposer_level_observations` partitions: filter to one partition first. Aggregates
only: no account / agreement / CIF / conversation / agent ids and no free text in any output; cells under 10 as
"<10". A part that fails records its error and the rest still runs. Reuse the loaders and point-in-time joins of
`tmp_validation/uc1_signals/` and `tmp_validation/uc1_uc2/` where they still exist. Performance: literal date
filters right after catalog.load; scope UC1 tables to the model's CIFs first; one pass per table group over a
localCheckpoint of the joined frame; broadcast small tables; no row-level collect; AUCs from (score, outcome)
counts. New tracked folder `tmp_validation/uc1_full/`; commit only that folder and the temporary catalog file. No
pipeline, other catalog or registry change.

Deliverables
1. Snippet + README_uc1_full.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_uc1_full_<model_id>.md.
3. Back in UAT, two files the user pastes back to Claude:
   - summary_uc1_full.md: all model_ids together, one markdown table per numbered item with a model_id column,
     numbers only inside tables, under 450 lines. Ends with verdict lines: what was delivered and whether it is
     the full transcript run (0.1, 0.4); does bundle 26 still run on it, and what breaks (0.5); coverage at 60-180
     and 180+, and is it selected (1); which field to read and is HIGH confidence worth requiring (2); can past
     month ends be read point in time, and how (3); per D1–D8: meets the bar / does not / n too small, with the
     deciding number; per S1–S11: holds / changes / fails.
   - logging_gap_note.md: one page for collections operations / DCORE: unlogged promise, dispute and request
     rates, where they concentrate, the likely cause (agents' logging or the feed), and whether it matters for
     payment. Aggregates only.

---

Interim run on the current export (2026-11-23, after the quick coverage check)
Paste below the line into the same UAT Sonnet session, after the prompt above (it changes the uc1_full build; build
it once, run it now on the current data, rerun it unchanged on the refresh).

---

Changes to the uc1_full build. The quick coverage check (`tmp_validation/uc1_cov/`) showed: 5,038 CIFs, transcript
observations dated 2026-03 .. 07 only, every capacity / intent estimate LOW confidence, no repayment rows in the
evidence and none usable in the export, covered customers selected (reachable, early DPD, fewer no_promise, pay
more). We make the best of it with our own point-in-time readings; everything stays provisional until the refresh.

1. Evidence partition. List the `proposer_level_observations` partitions (08-31, 09-30, 10-31) with row counts, CIFs
   and max `observed_at`; check whether the observations dated up to 2026-07-31 are identical across them. Use the
   latest non-empty partition, chosen by a single parameter so the refresh needs no code change. The export is used
   only in 0.5 and for one comparison (point 4); it is timeless, all LOW, and carries no repayment data.
2. Months. Month-end view on month ends 2026-04 .. 07 pooled (account bootstrap, 200 draws, for every AUC and
   every paid difference that decides something), with 2026-07-31 as the headline single month (freshest readings
   with an outcome). 2026-08-31 is not used for validation (no new transcripts, no outcome window). March and
   earlier: report n only. Say the last payment date; use 3-month outcomes only where the window is complete.
3. Our reading (validation only, nothing goes into a pipeline). Per CIF × signal at each month end, from evidence
   with `observed_at` < month end:
   - `latest`: the level(s) of the latest transcript customer-day within 90 days; several levels that day =
     `mixed`; no transcript day but a remark day = the remark level, kept as its own source category;
   - `modal90`: the most frequent transcript level over the 90 days, ties to the latest;
   - `support`: number of customer-days naming the reading's level, and whether any day named another level.
   Every Part 4 table: readings by `latest` (main) and the `modal90` AUC beside it; `support` ≥ 2 replaces the
   HIGH-confidence-only versions (HIGH does not exist). Also by age of the reading (0–30 / 31–60 / 61–90 days):
   does separation fade? And 90 vs 180-day windows for capacity and intent. This decides the reading rule the
   pipeline would use.
4. Agreement of `latest` at 2026-07-31 with the export's `estimated_value` (CIFs in both), per signal.
5. Selection. Read every fill / flag inside the covered group (that is where a rule applies), always within A3
   level × DPD band as well as overall, and say whether the direction holds in each stratum. Covered vs not covered
   is used only for the contact effect: paid_due with a transcript day in the 90 days vs none, within A1 × A3 ×
   DPD band cells (weighted to the book), so the effect of having a call is separated from what was said.
6. Transcript promise. The evidence has no repayment rows. First check whether the new `signal_level_conflicts`
   (per conversation, joined to `crx_uc1_metadata` for the date, legacy dropped) still has repayment slots
   (amount / date named); if yes, a promise = paying intent + amount or date named, as before; if not, intent only
   (payback_full / partial / with_delay), labelled an upper bound. Say which.
7. Remarks. Where do remarks come from? Share of remark days with a DCORE follow-up / promise / agreement record on
   any account of the CIF the same day or the day before; agreement of remark and transcript levels on days with
   both; whether remark-only readings order payers like transcript readings.
8. Calls in the store. `crx_uc1_metadata` conversations by month 2026-01 .. latest, for the model CIFs and in total,
   vs extracted customer-days by month: does the store hold calls after July that UC1 has not extracted, or did it
   stop? (Tells us what the refresh can add.)
9. Scope and priority. 180+ is out (not in UC1's sample): report n only. Run in this order and keep each part
   independent: Part 0 (0.3–0.5), points 1, 8; Part 1; points 3–5; D4 (A1 Unknown fill), D2 and Part 5.1–5.3
   (unlogged promises, with point 6), point 7; then D1, D3, D5, D6, D7, Part 2.4–2.6, Part 3.4, Part 6. Part 2.1
   (confidence) and Part 3.2–3.3 (reproducing the estimate) are dropped: the confidence is flat and we use our own
   reading. Cells below n 100 are shown and marked "thin"; the bar stays as stated (both products, n ≥ 100).
10. Summary verdicts as in the prompt, plus: which reading rule (latest / modal90, window, support) separates best;
    the contact effect within cells; for D4 and D2 whether the direction holds in every A3 level × DPD stratum;
    what the refresh must add for each D that is thin now.
