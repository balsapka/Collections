# UAT Sonnet prompt: UC1 on the collector card, gates G1 + G2 and E6 (what collectors can and do change)

Paste everything below the line into the UAT Sonnet session. Run cc_60_180 first, then rl_60_180. At 180+
(cc_180_plus, rl_180_plus) run part `g1` only (UC1 reads almost no 180+ customers).

---

Goal
We plan to show what the customer said on a call (UC1) on the collector card, beside the persona. Before that we
need three facts from today's data:
- G1 Room to act: how much do collectors' own choices vary today (promise amount and date, follow-up gap, plan,
  settlement, waiver, escalation)? If rules set everything, a card cannot change anything.
- G2 Is it new: after a call UC1 read, is the next person who handles the customer someone who did not hear it?
- E6 Do collectors already act on what the customer said, and does that reaction survive a handover?
Exploration only: no change to the pipeline, the persona, another catalog file or the registry. The job must rerun
unchanged when UC1 has read more calls (derive every date range from the data; nothing hardcoded to July).

Decisions already made (do not reopen)
- A conversation in DCORE = a follow-up row whose result is in the class "conversation" of the RPC check README
  (`tmp_validation/uc1_rpc_check/`). Right-party contact is not used as "conversation" (only ~29-30% of
  right-party days hold one). A Genesys or PCA transcript is always a conversation.
- UC1 values in this job are the per-call values (`crx_uc1_extracted_signals`), not the customer-level
  `estimated_value`: we look at what was said on that call and what happened next.
- Base: accounts in the model's persona base (`crx_persona.master` output of `<model_id>.persona_e2e`; name the
  dataset you load). Code axis names differ from the display names: in code A1 = ability, A4 = deterioration.
  Use the display names (Deterioration, Locatability, Credibility, Ability) in the summary.
- Windows (config block): next actions 14 days; next contact looked for up to 90 days; a collector enters a spread
  table only with at least 30 conversations in the cell.
- No collector, agent, account, CIF, agreement or conversation id leaves PROD. Collectors appear only as counts
  and as quantiles of collector-level figures.

Part s0: sources (run first; every later part depends on it; "not available" is a valid answer)
1. Handler. Which field holds the user who made a DCORE follow-up action (`dcore_prm_followup_outcomes`, else raw
   `col_his_followup`)? Name it, give its fill rate and the number of distinct handlers per month. Does
   `stg_genesys_transcripts` / `stg_pca_transcripts` carry an agent field? The UC1 index has `agent_id` (agent
   e-mail). Is there a map between a DCORE user and a Genesys agent? If not, take the handler of a call as the DCORE
   user on the same CIF's conversation row that day, and report the match rate.
2. Levers. For each lever say which dataset and field holds it, its date range, whether an amount is held and who
   chose it (collector, approval, campaign) as far as the data shows: promise (`dcore_int_ptp`,
   `ptp_trn_promiseheader` / `ptp_trn_promisedetail`: amount, promise date, instalments), reschedule
   (`rps_cur_header` / `rps_cur_schedule`), settlement (`dcore_int_settlement`), waiver or discount, escalation,
   dispute routing, agency placement, follow-up date set by the collector.
3. Owner or dialer. Per customer and month: number of distinct handlers across its conversations, and the share of
   conversations held by the most frequent handler (distribution: p25 / p50 / p75 / p90). One line: do accounts
   have an owner, or does the dialer hand each call to whoever is free?

Part g1: room to act (DCORE only; months from 2026-03 to the latest full month)
Within product x DPD bucket x month, for conversations on accounts in the base:
- promise amount as % of the amount overdue that day (name the field), days from the call to the promise date,
  number of instalments, days to the next attempt after a conversation;
- share of conversations followed within 14 days by a promise, a reschedule, a settlement, a waiver, an escalation.
For each: the overall distribution (p10 / p25 / p50 / p75 / p90) and the spread across collectors (collector-level
mean or share: p10 / p25 / p50 / p75 / p90, number of collectors, share of the variance that lies between
collectors). Also bunching: share of promise amounts equal to the full overdue amount, to the minimum due, or to a
round value; share of promise dates on a salary day (25th to 1st).
Reading per lever, cut-offs are our judgement (show the numbers so they can move): "varies by collector" when the
collector-level interquartile range is at least 10 points for a share, or 25% of the median for an amount or a gap;
"set by rule" when amounts or dates bunch on one value for 70% or more; else "little spread"; "not visible".

Part g2: is the next handler someone new?
Anchor = every call UC1 read (`crx_uc1_metadata` joined to the UC1 index for `agent_id`) for a customer in the base.
We have seen conflicting counts of such calls, so print the anchor count under both definitions and explain the gap
in one line: (a) the customer has an account in the base at the month end of the call's month; (b) at any month end
within 90 days after the call. Use (b) and say so.
- Next conversation on the customer (transcript or DCORE conversation row) and next DCORE action of any kind: days
  to it (0-3, 4-7, 8-14, 15-30, 31-90, none in 90) and the share handled by a different handler than the call's.
- Split by the call's queue and by the product of the call (its `contact_id` agreement, method of the source map
  run). Share of next contacts that sit on another product of the same customer.
- The same figures anchored on every staged Genesys call, read by UC1 or not, to show whether read calls are special.
- Manual check, PROD only, off by default (`--manual-sample`): print to the console, never to a file, 50 random
  anchors with the UC1 values of the call and the customer's next 3 DCORE remarks. The user tallies by hand how
  often the remarks already carry the UC1 values (all / part / none). Put only an empty tally table in the README.

Part e6: do collectors act on what was said?
For each read call and each signal (`delinquency_reason`, `payment_capacity`, `payment_intent`, `request`,
`dispute`; calls where the signal was not detected are the reference row): the levers of part g1 in the 14 days
after the call, split by who acted:
- the call's handler on the day of the call (the call itself: report it apart, the reading and the action can be
  one event);
- the call's handler on days 1-14;
- another handler on days 1-14.
Per signal value: share with each action, promise amount % and days to promise date, follow-up gap, with n and a
95% interval for the difference against the signal's most common level; raw and standardised over product x DPD
bucket. Reading per signal and lever: "lost at handover" (the call's handler differs by value, another handler does
not), "travels" (both differ), "no reaction seen" (both intervals inside +-5 points), "too thin" (a cell under 100
or an interval wider than +-10 points). A difference counts when it is at least 5 points and its interval excludes 0.

Tie-outs (print first; a mismatch goes to the top of the summary; never adjust numbers to match)
Month end 2026-07-31, 61-180, cards / loans, valid while UC1's read calls end 2026-07-16 (after a UC1 refresh print
the new values and mark them "moved"): accounts 18,397 / 3,728; UC1 reading of any age 19.2% / 18.2% (3,528 / 680);
reading under 90 days 7.1% / 8.2%; right-party contact in the last 90 days 36.1% / 42.7%; Genesys transcript in the
last 90 days 10.5% / 13.3%; share of right-party days that hold a conversation result 29% / 30%.

Rules
- Loading: `catalog.load` only; never `spark.read` or a path. Reuse `tmp_validation/uc1_reach/` (frame
  `uc1_reach_frame`, right-party and transcript loaders), `tmp_validation/uc1_refresh/` (Genesys call to CIF) and
  `tmp_validation/uc1_rpc_check/` (result classes) where they give what is needed; do not edit them.
- Catalog: temporary, explicit entries only, in `conf/base/catalog/catalog_tmp_uc1_full.yml` (no dataset-factory
  patterns: the workplace Kedro does not resolve them). No other catalog, pipeline or registry change. None is better.
- `model_id` = `catalog.load("params:model_id")`: never hardcoded, no override argument, in every output file name.
  The user switches model in `globals_dev.yml`.
- Dates: `cc_spine`, `dcore_observation_spine` and `prm_contract` carry mid-month billing dates in PROD: never join
  them on the date (on-or-before, or `last_day` first). DCORE timestamps: the Spark session is GMT; say which
  timestamp you use (`action_ts`, `result_ts`, `updated_at`).
- Aggregates only in results files and summaries: no ids, e-mails or names; no transcript, remark or note text;
  cells under 10 as "<10". Result names and queue names are vocabulary and may appear.
- A part that fails records its error; the rest still runs. Parts: `s0,g1,g2,e6`.
- New tracked folder `tmp_validation/uc1_card_gates/`; commit only that folder.

Deliverables
1. The snippet in `tmp_validation/uc1_card_gates/`: config block at the top (windows, cut-offs, minimum counts,
   parts, level maps); one results pair per model_id (`uc1_card_gates_<model_id>.json` + `.md`), tie-outs first;
   a README with one command per model_id, the fields found in part s0 and the empty tally table.
2. After the user commits the PROD results: `summary_uc1_card_gates.md`, under 150 lines:
   - a. Tie-outs per model_id, or "all match".
   - b. Verdict in four lines: G1 which levers collectors really set; G2 how often the next handler is new, and
     whether accounts have an owner; E6 which signals collectors react to and whether it survives a handover;
     what the data cannot show.
   - c. Part s0: the handler field, the lever table (dataset, field, range, amount yes / no, who chose).
   - d. G1: one table per product, lever x reading, with the collector spread.
   - e. G2: days to next contact and share by a different handler, read calls against all staged calls.
   - f. E6: one table per signal, value x actor, with the reading.
   - g. What could not be computed, and what each missing source would unlock.
