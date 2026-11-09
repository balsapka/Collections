# A3: V1g, promise events under two deadlines: GRR's next statement vs a fixed 30 days (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
(60_180 first) and pastes `summary_v1g.md` back here.

Why (user, 2026-11-09): V1f (`v1f_summary_60_180.md`) showed that follow-up promises add coverage and
are paid as often as table plans. But the CC paid rate follows the time left to the next statement (15%
paid at ≤ 7 days, 43% at 15–30). That deadline is GRR's rule on purpose: a promise belongs to the
current statement cycle, so the next statement is the hard deadline however close it is. The
alternative is a fixed 30 days from the promise. V1g runs both on the same events and asks which one
ranks customers better, and covers 180+.

Bundle 17 is applied, its real A3 output is written for all four model_ids, and the check is cleaned up.
Since then (D-A3-24): Moderate from 2 points, High from 4.

````text
Goal
Compare two deadlines for judging A3 promise events, GRR's next statement (G) and a fixed 30 days (F),
on the same events, against bundle 17's Dimension A, for all four model_ids. Exploration only:
aggregates, no pipeline change. It follows V1f (tmp_validation/a3_v1f/: reuse its event builder and
README, fix what its caveats name).

Decided, to follow
- Code: src/enbd_collections/pipelines/crx_persona/a3_credibility/ and the product wrappers (dues,
  payments, ledger, instalments, commitment signals). Baseline = the real output
  crx_<p>_a3_payment_credibility (bundle 17, payments judge, every dimension and the refusal flag);
  recompute its state with Moderate from 2 / High from 4 (a3_credibility/constants.py SCORECARD with
  MODERATE_FROM = 2; refusal takes one rung off) so baseline and variants use the same thresholds.
- Events (V1f's consolidation, unchanged): follow-up P1 and P2 names (P3 SOFTPTP reported apart);
  table PTPs and settlement plans; on one agreement, follow-up rows within 7 days are one event dated
  at the first; follow-up matched to a table event within +/- 7 days (nearest, once each). Change: A1
  names (SETTLEMENT, BALCON, REWRITE AGREED) count only when matched to a settlement record. Window
  as Dimension A: [max(episode start, last 12 months), observation date], latest month.
- Amount: the minimum payable due of the current cycle at the promise. CC: the due_amount of the
  latest statement on or before the event day (oldest open bucket, else minimum due; bucket 08
  fallback), at least 100 AED. RL: the EMI of the event month. Report how often this differs from
  V1f's amount (the cycle the cutoff closes).
- Deadline G (GRR): CC: payments in (event day, the first statement after the event day], however
  close. RL: RL cash is month-level, so G = the event month's cash; say how much of it can predate
  the event day and check whether any day-level RL repayment source exists in the catalog (report
  it, do not use it).
- Deadline F: payments in (event day, event day + 30 days]. RL: the cash of the months the 30 days
  touch.
- Outcome per event: paid (>= the amount), partial (>= 100 AED, below it), none. Settlement plans: per
  instalment due date, the same two deadlines from the due date.
- Levels: bundle 17's ladder on events (Kept: >= 2 concluded and >= 80 % paid; Broken: the last 3 all
  broken, or >= 2 concluded and < 40 % paid; Partly kept: >= 1 paid; else Thin), partial = broken.
  An event is concluded once its deadline is on or before the observation date.
- 180+: CC accounts may have no statement after the event (charged off); then G falls back to the end
  of the next month. Report how often.

Questions (each gets a short answer with the key numbers, per model_id)
Q1 Events: count by kind (matched / table-only / follow-up only) and class, accounts with >= 1
   concluded event vs bundle 17's accounts with >= 1 concluded instalment, accounts leaving Thin. 180+
   first sight: do the promise names and tables carry events at all?
Q2 Outcomes: paid / partial / none under G and under F, by kind and class; the paid rate by days to
   the deadline (G: 1-7, 8-14, 15-21, 22-31 days to the next statement); the crosstab G x F (paid
   under one, not the other); for CC events made <= 7 days before a statement, the share paid by
   the statement vs paid within 30 days (does the customer pay the next cycle instead?).
Q3 Overlap with Dimension B: the share of paid events whose payment falls in a B qualifying cycle,
   split by event age (deadline inside B's window: last 3 months at 60_180, 6 at 180+, vs older);
   accounts Kept with B none and Broken with B regular, under G and F.
Q4 Levels and state: level distribution under G, F and bundle 17; crosstabs of each with bundle 17;
   the A3 state distribution (Moderate from 2, High from 4, refusal on) with each level in place of
   bundle 17's.
Q5 Does it predict? For persona_end_date - 3 months (rebuild the events and levels as of that date),
   the share that cure / improve / hold / roll over the next 3 months by level, under G, F and bundle
   17, with the accounts that exit or have no level at the later date shown as their own row (do not
   drop them). AUC of non-roll vs roll for the ladder in two orders (Kept > Partly > Thin > Broken, and
   Kept > Partly > Broken > Thin) and for the A3 state (High > Moderate > Low). Also the same outcome
   by a3_points_total (0 / 1 / 2 / 3 / 4+) on the baseline, split by refusal.
Q6 Settlement plans: per instalment and per plan paid shares under G and F.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance as V1f (build the event list once and persist it, literal date
filters right after catalog.load, broadcast joins to the population, no row-level collect). Work in a
new tracked folder tmp_validation/a3_v1g/ and commit only that.

Deliverables
1. Snippet + README_v1g.md (what changed from V1f and why), pushed from UAT.
2. The user runs it in PROD per model_id and commits results_v1g_<model_id>.md.
3. Back in UAT: summary_v1g.md, under 80 lines: one line per question per model with the key numbers;
   then a verdict in one paragraph: G or F (or neither), at 60_180 and 180+, judged first on Q5
   (ranking) and then on coverage and overlap with B; and whether either beats bundle 17's
   Dimension A.
````
