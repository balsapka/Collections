# UAT Sonnet prompt: UC1 stated signals against the UC2 persona states (our own validation)

Paste everything below the line into the UAT Sonnet session.

---

Goal
We hold two views of each delinquent customer: the UC2 persona states the crx_persona pipelines
derive from observed data (A1 ability, A2 locatability, A3 credibility, A4 deterioration), and the
UC1 stated block (crx_<p>_uc1_stated, bundle 26): A5 stated ability and A6 stated intent, from the
UC1 team's call-transcript signals. Before deciding how the two combine into the final personas and
tiers, we need to know, on our own data and outcomes: how old the stated signals are, what reasons and
supporting signals come with them, how they line up with the UC2 states (above all among A2
Reachable customers, but also the Non-Reachable ones that do have UC1 conversations), and whether a
stated level tells us anything about payment that the UC2 state does not. Do not use the UC1 team's
own UC1 / UC2 corroboration; we validate the signals ourselves.

Decided, to follow
- model_ids: all four (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus). At 180+ the UC1 reach is
  tiny (a few hundred rows); run the same code and report n, no extra work there.
- Legacy-format extractions are out (user, 2026-11-18): a conversation whose only extraction rows
  have model_version = 'legacy' is dropped everywhere, as if it did not exist. Bundle 26's output
  still has uc1_evidence = 'legacy_only' rows (a later bundle removes them): recompute the evidence
  status from the UC1 tables with legacy conversations dropped, and say how many rows moved.
- The current-format extractions were drawn by stratified sampling on the 60-180 population, so at
  60-180 the distributions are taken as broadly representative until UC1 runs on all transcripts.
  Part C checks this; it does not change Parts A and B.
- UC1 inputs (catalog, read only): crx_uc1_metadata, crx_uc1_extracted_signals,
  crx_uc1_signal_level_conflicts (per conversation × slot; only the primary level is 'detected';
  slot = the part of value before ':'), crx_uc1_simple_signal_aggregation. Calls exist only
  2026-03-06..2026-07-16.
- UC2 inputs: the persisted outputs as they are now (crx_<p>_a1_ability, crx_<p>_a2_locatability,
  crx_<p>_a3_payment_credibility, the A4 output, crx_<p>_obs_base, crx_<p>_uc1_stated). Do not
  re-run or re-implement any engine. Record in the README which A1 / A3 logic version the persisted
  tables carry (e.g. the a3_commitments_level values present).
- Columns to use where they exist: a1_state, a1_income_level, a1_income_source, a1_salary_stopped,
  a1_distress_flag, a1_reason; a2 reachability_state, location_state; a3_state, a3_points_total,
  a3_commitments_level, a3_refusal_flag, a3_dispute_flag; the A4 family. Scored A1 / A3 rows as the
  axis defines them; keep Unknown as its own row in crosstabs.
- Outcomes, per (account, month end), from the same dues and payments the A3 results work uses
  (crx_<p>_a3_dues / crx_<p>_a3_payments if persisted, otherwise the payment inputs the A3 engine
  reads; say which): paid_due = payments in the window reach max(one month's due at the month end,
  100 AED); paid_any = payments reach 100 AED. Window: 3 months after the month end, except Part A
  (2026-08-31), which uses the 2 full months available (Sep, Oct 2026); label it.
- Splits: DPD band at the month end as the persona code defines it (61–90 / 91–120 / 121–150 /
  151–180; 181–360 / 361–720 / 720+); RL product from rl_spine.loan_type.

Part A — the stated block as shipped, 2026-08-31, all four model_ids
A1 Coverage: evidence status (legacy dropped) × A2 reachability; × A2 location; × A4 family; × DPD
   band.
A2 Age of the signal, extracted rows: days from the last extracted conversation to the observation
   date (0–30 / 31–60 / 61–90 / 91–180 / >180), per A5 state and per A6 state; and days since the
   last conversation that detected the published capacity / intent level.
A3 Ability: A5 state × a1_state; A5 × a1_income_level, × a1_salary_stopped, × a1_distress_flag;
   a5_reason × a1_state and × a1_salary_stopped / a1_income_source.
A4 Intent: A6 state × a3_state; × a3_commitments_level; × a3_refusal_flag; a6_period × A6 state;
   amount / date named flags × a3_commitments_level; stated_dispute × a3_dispute_flag;
   stated_request_flag × a3_state.
A5 Support: a5_conversations_n and a6_conversations_n bucketed (1 / 2 / 3–5 / 6+), agree share per
   bucket; A5 = A1 concordance (able~High, partly_able~Moderate, unable~Low) per support bucket.
A6 Reachability: the A5 / A6 states within each A2 reachability state. For Non-Reachable rows with
   an extracted conversation: was the last UC1 conversation before or after the start of the failed
   call days A2 counted (use whatever dates the A2 output or its DCORE input carries; say which).
A7 Outcomes (2 months): paid_due %, paid_any % with n, by A5 within each a1_state and by A6 within
   each a3_state, with not_stated and no_evidence as their own rows.

Part B — point in time, conversation level (our validation; month ends 2026-03-31 .. 2026-07-31)
For each (account, month end) of the obs base, the CIF's current-format extracted conversations
dated strictly before the month end, and per conversation the capacity and intent level it detected.
Two readings, for validation only (they are not a rule of ours and do not change UC1's):
L = the level of the latest conversation that detected the signal, with its age in days;
M = the most frequent level so far, ties to the latest (UC1's rule, applied point in time).
B1 Account-months with a reading, per month end; age distribution (0–30 / 31–60 / 61–90 / 91+).
B2 paid_due % (3 months) by L capacity, overall and within each a1_state; by L intent, overall and
   within each a3_state; the same for M. n in every cell.
B3 Decay: paid_due % by L × age bucket, for capacity and intent; the gap between the best and the
   worst level per bucket.
B4 Added value: AUC on paid_due of (i) a1_state alone and (ii) a1_state then L capacity inside it
   (fixed order: High > Moderate > Low > Unknown; inside each, able > partly_able > not stated or
   no reading > unable). Same for a3_state and L intent (pays_in_full > partly_or_later > not stated
   or no reading > refuses). Also paid_due % for "has a reading" vs "has no conversation" within
   each UC2 state (selection effect of being called and extracted).
B5 Agreement: L capacity × a1_state, L intent × a3_state (counts, concordance %), per month end
   pooled.
B6 Reachability: paid_due % by L within A2 Reachable and within Non-Reachable.

Part C — is the extracted sample representative (60_180 model_ids, month ends 2026-03 .. 07)
Among account-months whose CIF has any conversation before the month end (metadata, legacy
dropped): extracted vs not extracted, distributions of a1_state, A2 reachability, a3_state, A4
family, DPD band, RL product, a3_commitments_level and call month. Then paid_due % by L capacity and
L intent reweighted to the conversation holders on (a3_state × DPD band) vs unweighted.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name;
aggregates only, no account / agreement / CIF ids or conversation ids in any output; cells under 10
as "<10". A part that fails records its error and the rest still runs. Performance: literal date
filters right after catalog.load; scope the UC1 tables to the model's CIFs first; one pass per table
group over a localCheckpoint of the joined frame; broadcast the small tables; no row-level collect;
AUCs from (score, outcome) counts. Work in a new tracked folder tmp_validation/uc1_uc2/ and commit
only that. No pipeline, catalog or registry change.

Deliverables
1. Snippet + README_uc1_uc2.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_uc1_uc2_<model_id>.md.
3. Back in UAT: summary_uc1_uc2.md, which the user pastes back to Claude.
   - All four model_ids together, one markdown table per numbered table with a model_id column,
     numbers only inside tables.
   - Under 300 lines.
   - End with eight lines, one verdict each: how old the stated signals are at the latest month;
     does stated ability add to A1 on paid_due (B4); does stated intent add to A3 (B4); do L and M
     differ in value; does the signal decay with age (B3); why Non-Reachable customers have UC1
     conversations (A6); is the sample representative enough (C); anything that looks like a
     defect in the UC1 inputs or in bundle 26's output.
