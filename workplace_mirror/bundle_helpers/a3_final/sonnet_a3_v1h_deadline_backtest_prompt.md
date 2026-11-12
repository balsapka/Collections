# A3: V1h, a back-test of the promise deadline (bundle 20 vs GRR vs 30 days) and the Unknown -> Low rule (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for all four model_ids
and pastes `summary_v1h.md` back here.

Why (user, 2026-11-12): the bundle 23 check (`bundle_helpers/b23_a3/b23_check_review.md`) showed what
GRR's month-end deadline changes: RL 61–180 paid promises 70.5 -> 46.8%, 7.2% of states move down;
CC 61–180 untouched; 180+ small. It also showed that the Unknown rule (D-A3-27) moves every former
Unknown row to Low (CC 180+ 81%). It carries no outcomes. V1h asks which deadline ranks customers
best on later cure / payment / roll, and whether the former Unknown rows behave like Low.

Bundle 23 is applied in the workplace (its check ran); step 8 is not run yet, so the real A3 output
is still bundle 20's.

````text
Goal
Back-test three deadlines for judging A3 promise events, and the Unknown -> Low rule, on later
outcomes, for all four model_ids. Exploration only: aggregates, no pipeline change, no real output
written.

Decided, to follow
- Engine: the applied code in src/enbd_collections/pipelines/crx_persona/a3_credibility/ and the
  product wrappers (cc_/rl_a3_payment_credibility). Run the A3 node functions in pipeline order on
  catalog loads (episode, dues, payments, ledger, instalments, promise events, the three signal
  builders, build_a3_credibility); do not re-implement any rule. build_promise_events and
  build_a3_credibility take a deadline override: pass it for each variant.
- Deadlines (one full engine run each; everything else identical):
  B20 = bundle 20: CC "next_statement", RL "next_month_end" (both segments);
  GRR = as shipped (no override): 61-180 CC "next_statement", RL "month_end"; 180+ "month_end";
  LEN = lenient: CC "30_days", RL "30_days_month_end".
  At 61-180 CC, B20 and GRR are the same rule: say so and show it once.
- Unknown rule: NEW = as shipped (an episode row is never Unknown). OLD = bundle 20's: an episode
  row is Unknown when a3_commitments_level = thin, a3_dlq_payment_level = none,
  a3_pre_dlq_payment_level = no_record and the refusal flag is off. Derive OLD from the same run
  (flag ex_unknown); rows with no episode stay Unknown in both.
- Observation dates: the engine scores every persona month; use the month ends that leave 3 full
  months of outcome before persona_end_date (expected 2026-03-31, 2026-04-30, 2026-05-31; take what
  the data allows), pooled, with per-month results for stability. Each row is point in time: events
  conclude only when their deadline is on or before the observation date.
- Outcomes over the 3 months after the observation date, per (account, observation date). Reuse
  V1g's outcome code if tmp_validation/a3_v1g/ still exists, else build it from the A4 / spine DPD
  and the A3 payments:
  cured = back to current (no overdue) at any month end in the 3 months;
  paid_due = payments in the 3 months reach at least one month's due (the A3 dues);
  paid_any = payments >= 100 AED in the 3 months;
  rolled = a worse DPD bucket at month 3 than at the observation date (61-180 only);
  exited = not in the base / closed / written off / sold at month 3. Exited rows are their own
  category, never dropped. At 180+ cure and roll are near zero by construction: lead with paid_due
  and paid_any there.

Questions (each a short answer with the key numbers, per model_id)
Q1 States: High / Moderate / Low / Unknown for each deadline x Unknown rule (pooled), with n.
Q2 Outcome rates by state for each variant, and by Dimension A level (Kept / Partly / Thin / Broken)
   for each deadline.
Q3 Ranking. AUC with a 95% interval (bootstrap over accounts, 200 resamples) per outcome (cured,
   paid_due, paid_any, not rolled), for: the A3 state (High > Moderate > Low) under each deadline,
   with ex_unknown rows (a) as Low (NEW) and (b) left out (OLD); a3_points_total; the Dimension A
   level alone in two orders (Kept > Partly > Thin > Broken; Kept > Partly > Broken > Thin), on all
   rows and on rows with >= 1 concluded event. Name the best deadline per outcome and segment, and
   say when the intervals overlap.
Q4 Who moves. Rows whose state differs between GRR and B20, and between GRR and LEN: their outcome
   rates next to the rows that stayed in the upper state and those that stayed in the lower state
   (do demoted rows behave like the upper or the lower state?). At event level for RL: promises
   paid by the month end, paid only in the following month (B20 counts them, GRR does not), and not
   paid: the account's later outcome rates for each.
Q5 Unknown -> Low. Size of ex_unknown per model_id; its outcome rates next to the other Low rows,
   Moderate and High; and whether any outcome makes it look better than the other Low rows (then it
   would belong in its own state). What it is made of: ex_unknown requires Dimension C = no_record,
   and the user's EPD share at cc_60_180 is ~7%, not the 11.5% ex_unknown, so split ex_unknown by
   why C is no_record, from the Dimension C signals (pre_dlq_reason, pre_dlq_months_due_n):
   (a) censored episode (A4 cropped the history: the episode start is unknown, C is no_record by
   rule); (b) 0 / 1 / 2 months with a billed amount > 0 in the 12 months before the episode, crossed
   with months on book at the episode start (< 6, 6-12, 12-24, 24+, from the card / loan open date)
   so young accounts (EPD-like) separate from old accounts with idle months (dormant card, no bill);
   (c) months missing from the ledger in that window (no statement, or cycles over 62 days dropped).
   Also months since the episode start, and at 180+ charge-off age < 24 vs >= 24 months. Report each
   group's outcome rates too.
Q6 Stability: Q3's state AUC for paid_due per observation month and deadline.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / agreement / CIF ids; cells under 10 as "<10". A part that fails records its error
and the rest still runs. Performance: one engine run per deadline over all months at once;
localCheckpoint the event tables and the scored output before counting; literal date filters right
after catalog.load; broadcast the small tables; no row-level collect; at 180+ (300k+ rows a month)
check the driver memory before the bootstrap and sample accounts if needed (say so). Work in a new
tracked folder tmp_validation/a3_v1h/ and commit only that.

Deliverables
1. Snippet + README_v1h.md, pushed from UAT.
2. The user runs it in PROD per model_id and commits results_v1h_<model_id>.md.
3. Back in UAT: summary_v1h.md, under 90 lines: one line per question per model_id with the key
   numbers; then a verdict in one paragraph per segment (61-180, 180+): which deadline ranks best
   (first on paid_due and cure at 61-180, paid_due and paid_any at 180+), whether GRR's month end
   costs ranking for loans, and whether ex_unknown belongs in Low or deserves its own state.
````
