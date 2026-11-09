# A3: V1f, promises judged by a sufficient payment (GRR's Dimension A) (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
(60_180 first) and pastes `summary.md` back here.

Why (user, 2026-11-09, from GRR): what counts is whether the customer paid enough to stabilise the
account (the oldest overdue bucket amount / one EMI) after making a commitment, not whether a promised
amount was paid. GRR proposes:
- a promise event comes from the PTP / settlement tables and from the DCORE follow-up result names
  (which bundle 17 does not use for Dimension A);
- the promise is paid when payments by the next statement (CC) / the next month end (RL) cover the
  minimum payable due, partial when there is some payment but not enough, else broken;
- DPD bucket movement is the indirect reading of the same thing, usable at 180+ as well. The DE's
  bucket-movement approach came close to the payment approach.

Bundle 17's Dimension A (instalments, cumulative due by the grace cutoff) is the baseline.

````text
Goal
Find out whether A3 Dimension A can reliably be built as "promise events judged by a sufficient
payment", as GRR proposes, and how it compares with bundle 17's instalment rule. Exploration only:
aggregates, no pipeline change.

Decided, to follow
- A3 code: src/enbd_collections/pipelines/crx_persona/a3_credibility/ (bundle 17). Reuse its functions
  instead of re-deriving: _dpd_journey.anchor.episode_start (episode anchor from the A4 output),
  cc_a3_payment_credibility.nodes.build_cc_a3_dues / build_cc_a3_payments, rl_a3_payment_credibility
  .nodes.build_rl_a3_dues / build_rl_a3_payments, a3_credibility.sources.build_cycle_ledger and
  build_instalments, a3_credibility.signals.build_commitment_signals (kept_by="payments") for the
  baseline. The DCORE code sets are in crx_persona/_dcore_codes.py; events through
  _common.dcore_account_events.
- Window: as Dimension A, events in [max(episode start, last 12 months), observation date], account
  level (prm_dcore_account_agreements), the latest month of each model_id.
- Minimum payable due = one month's due as Dimension B uses it: CC due_amount of the cycle (oldest open
  bucket 07..01, else minimum due; bucket 08 fallback), RL the EMI (last known). Grace = the first
  statement on or after the reference date (CC) / the end of the next month (RL). A "payment" needs at
  least 100 AED (D-A3-5).

Questions (each gets a short answer with the key numbers)
Q1 Every result name, classified. List every result_name that occurs in dcore_prm_followup_outcomes
   for the model's agreements (and in stg_dcore_mst_result / the result master, if it has a catalog
   entry) with counts in the Dimension A window and overall: rows, agreements, accounts, by action_code.
   Classify each name with the proposed classes P1 / P2 / P3 / A1 / A2 / R / K / I / D / N / not about
   paying (the table is in workplace_mirror/bundle_helpers/a3_final/dcore_promise_names_assessment.md,
   section 2; copy it into the README). List every name that occurs but is not in that table, with
   counts and your proposed class. Flag any class assignment the data contradicts (e.g. a "promise"
   name logged mostly after a payment).
Q2 Consolidated promise events (the rules are in the same file, section 3):
   - follow-up events: P1, P2, P3, A2 names, any action code; rows on one agreement within 7 days of
     each other are one event, dated at the first;
   - table events: non-cancelled PTPs (promise start, else event date) and settlement plans (event
     date);
   - match a follow-up event to a table event on the same agreement within +/- 7 days (nearest, each
     at most once); A1 names are matched to settlement records the same way.
   Report: the match-distance distribution (0, 1-3, 4-7, 8-30, > 30 days, none); matched / table-only /
   follow-up-only counts by class and name; events per account (0 / 1 / 2 / 3+); the share of accounts
   with at least one event vs at least one concluded instalment today (bundle 17); how many accounts
   move out of Thin. Repeat the collapse and the match with 30 days and say what changes.
Q3 Reference date. A table PTP has a due date, a follow-up promise only its day. Judge each event
   against (a) the event day and (b) the due date where one exists; report how often the two give a
   different outcome.
Q4 Outcome by payment. Per event: paid (payments in (reference date, cutoff] >= the minimum payable due
   of the cycle the cutoff closes), partial (>= 100 AED but below it), none. Shares by event kind
   (matched / table-only / follow-up only), class and plan type; settlement plans: per instalment and
   per plan. Are follow-up-only events paid at a rate close to matched ones (then they are real
   promises the tables miss)? Also DCORE's own reading: the share of events with a K name (kept /
   payment confirmation) in their grace window, crosstabbed with the payment outcome.
Q5 Outcome by DPD movement. Per event: the bucket at the statement / month end before the reference
   date against the one at the cutoff: improved / held / rolled (CC 08 accumulates; say how you treat
   it). Crosstab with Q4. How close is "held or improved" to "paid", by segment (60_180 vs 180+)?
Q6 Does it carry its own information? The risk: a sufficient payment after a promise is often the same
   cycle Dimension B already counts. For the latest month, crosstab the new Dimension A level (ladder
   below) with Dimension B (regular / some / none) and Dimension C; report the share of paid events
   whose payment cycle is also a Dimension B qualifying cycle; and the rows where the new A disagrees
   with B (A kept & B none, A broken & B regular). Split all of Q6 by event age: cutoff inside
   Dimension B's regular window (the last 3 months at 60_180, 6 at 180+) vs older. The user's framing:
   A measures trustworthiness over the episode (up to 12 months), B recency, so overlap is expected
   in the recent events and A's own information in the older ones; say whether the data agree.
Q7 Levels. Apply bundle 17's ladder to events (Kept: >= 2 concluded and >= 80% paid; Broken: the last 3
   all broken, or >= 2 concluded and < 40% paid; Partly kept: >= 1 paid; else Thin) in two readings:
   partial = broken, and partial = half a paid event. Crosstab each with bundle 17's payments level and
   give the A3 state distribution (the Scorecard in a3_credibility/constants.py, Broken -1) with the new
   level in place of the old.
Q8 Does it predict? For an earlier month (persona_end_date - 3 months), the share of accounts that cure,
   improve, hold or roll over the next 3 months, by new level and by bundle 17's level. Which ranks
   better (Kept best, Broken worst, monotone)?

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance (V1d rules): build the event list once and persist it, literal
date filters right after catalog.load (min / max of the windows as scalars), broadcast joins to the
population, no looped plan chains, no row-level collect, check PartitionFilters on partitioned sources.
Work in a new tracked folder tmp_validation/a3_v1f/ and commit only that.

Deliverables
1. Snippet + README_v1f.md (tables, columns, the classification table with every added name and your
   reasons), pushed from UAT.
2. The user runs it in PROD per model_id and commits results_v1f_<model_id>.md.
3. Back in UAT: summary_v1f.md, under 80 lines: one line per question per model with the key numbers;
   the final promise set (names and classes, with their counts); then a verdict in one paragraph: can Dimension A be built this way reliably,
   is the payment reading or the bucket-movement reading better (and at 180+), and what it adds over
   Dimension B.
````
