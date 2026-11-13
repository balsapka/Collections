# A3 payment credibility: spec (draft, decisions as they are taken)

Code reviewed: O66–O81 in `REVIEW_OBSERVATIONS.md`. The DE spec (`A3_credibility_shared.xlsx`,
"A3 framework") is not in the mirror yet; until it is, the rules below plus the code's `[CONFIRM]`
thresholds are the reference.

## What A3 measures (working framing, 2026-11-03)

(User, 2026-11-03: this framing opens the updated model spec, with the strong-negative test and the
overlap notes below.)

GRR reframed the axis from payment intent to **payment credibility**: how far we can believe this
customer will pay on this debt. Two kinds of evidence:
- **Trust: does what they say happen?** Promises and arrangements made and honoured (Dimension A), and
  explicit statements of non-intent (refusal). Depends on DCORE, whose promise records and the actual
  payments do not always line up.
- **Flow: is money coming in, and did it before?** Payments while delinquent (Dimension B) and the
  record before delinquency (Dimension C). Flow reads intent only together with capacity: a customer
  can mean to pay and be unable to for a while (lost salary, between jobs), and shows None / Some here.
  So a weak flow is not proof of low intent, and A3 must not be read without A1. The persona combines
  them; A3 itself stays about this customer's track record on this debt.

Not A3: capacity to pay (A1), reachability / location (A2), the DPD path itself (A4).

Dimension A and Dimension B differ in time as well as in kind (user, 2026-11-09): A characterises the
customer's trustworthiness over the last 12 months, earlier episodes included (D-A3-26), B establishes recency (the last 3
months, 6 at 180+). A payment rule for A that only re-reads recent payments repeats B.

A **strong negative** earns its place only when all four hold:
1. it adds evidence the points do not already carry;
2. the data behind it is reliable;
3. it does not re-derive another axis;
4. it moves states in a way that makes sense on PROD.

Measured, not assumed (V2, V3).

## Decided

- **D-A3-1: no spells, no T0 (D5).** Grain = the month-end observation base
  `crx_{cc|rl}_obs_base` `(account_id, observation_date, cif_id)`. A3 stops reading
  `crx_cc_spell_table`, `crx_rl_a4_spine` and `join_spine_to_spell` (user, 2026-11-03).
- **D-A3-2: anchor = the latest spell start, as of the observation date.** This is the start of the
  current delinquency episode, taken point-in-time from the A4 engine (`months_before_spell`: the last
  maximal run at or above delinquency, so a cure back to current ends an episode). It is not the first
  entry into collections and not a DCORE agreement start: an agreement id can stay the same across
  episodes, and the first entry would make the record look clean. One anchor serves all three:
  - Dimension C, record before delinquency: the 12 months before the anchor. A repeat delinquent's
    earlier missed payments fall inside it on purpose.
  - The Dimension B window start: `greatest(anchor, observation_date − N months)`.
  - The DCORE contact and plans-on-record windows: `[anchor, observation_date)` (D6).
- **D-A3-3: one method per dimension, no switches.** Dimension B and Dimension C ship
  `single_payment_cycle_count` (CC: one cycle's payments ≥ 100% of that cycle's due; RL: the month's
  cash ≥ 100% of the EMI). Removed: `payment_sum_waterfall`, `dpd_bucket_movement`, their nodes,
  helpers, catalog entries and per-method columns, and the params `a3_dlq_payment_evidence_method`,
  `a3_pre_dlq_payment_evidence_method` and the two `rl_a3_*` keys (user, 2026-11-03).
- **D-A3-4: output.** `a3_state_v1` → `a3_state`; `a3_confidence`, `a3_provenance`, `computed_at` and the
  per-method columns are dropped (user, 2026-11-03).

- **D-A3-5: 100 AED minimum payment guardrail in every band, not only 180+** (user, 2026-11-03).
  Scope (user, 2026-11-03): payments while delinquent only. A Dimension B cycle qualifies when its
  payments reach `max(100% of one month's due, 100 AED)`; "any payment" (Some, and the payment tests of
  the refusal and no-response strong negatives) needs a cycle with at least 100 AED. Dimension C is
  unchanged: paying the billed minimum counts, even below 100 AED (spec row 31).

- **D-A3-6: band rules by `model_id`** (user, 2026-11-03). `*_60_180` runs use the 61–180 rules
  (Regular 2 of 3 months, any-payment window 3 months); `*_180_plus` runs use the 180+ rules (Regular
  3 of 6, any-payment window 12 months), as A1 and A2 do (`_common.window_months`). The row's bucket no
  longer picks the band, so the `dlq_bucket_from_hist` / month-end bucket lookups go.

- **D-A3-7: DCORE evidence at account level** (user, 2026-11-03). Commitments and strong negatives
  read only the scored account's agreement(s), linked date-free through A2's
  `prm_dcore_account_agreements` (one agreement per account in PROD, A2 v01); `dcore_observation_spine`
  and its billing-date equality join go (O71, O72). Payments are the account's own. An exception to the
  CIF-level rule for customer signals: credibility is about this debt.

- **D-A3-8: "paid as billed" = paid before the next statement, not by the due date** (user,
  2026-11-03; departs from the DE sheet row 31, O82). CC: the cycle's payments with
  `billing_date < banking_date <= next_billing_date` reach the billed amount; RL: the month's cash
  reaches the EMI. `on_time_payment_sum_in_cycle` and the TEMPORARY note go.

- **D-A3-9: commitments counted once, from the instalments** (user, 2026-11-03, provisional on V1).
  Kept / concluded counts and the broken streak come from one rule over the PTP and settlement
  instalments: concluded = due on or before the observation date and paid or overdue (pending ones
  do not count), window = `[max(latest spell start, obs − 12 m), obs]` (spec rows 19, 76; O75, O83;
  the window is the last 12 months since D-A3-26).
  `dcore_feat_ptp` / `dcore_feat_settlement` are no longer read.

- **D-A3-10: keep `cc_a3_history_floor_date` (2024-01-01) and measure it** (user, 2026-11-03, O77).
  The bundle check reports, per model_id, the latest-month rows whose Dimension C reads `no_record`
  because the floor cut the 12 months before the latest spell start (rows that would have ≥ 3 months
  due without the floor). Revisit with those numbers or when the billing backfill lands.

- **D-A3-11: kept / broken is judged by the payments, unless DCORE's status proves reliable**
  (user, 2026-11-03: payment data is the truth, DCORE status is simpler if reliable). V1 extension
  decides: if DCORE's paid / overdue status agrees with the ledger closely enough (the user judges
  from the numbers), A3 uses DCORE's status. Otherwise an instalment counts as kept when payments of at
  least its amount arrive between the promise date and its due date. CC matches Way4 payment
  transactions by date. RL can only match by month (`total_paid` is a monthly total).

- **D-A3-12: CC due once the ladder sits in bucket 08** (user, 2026-11-03). Deep in delinquency Way4
  accumulates the whole overdue amount in `overdue_bucket_08`, so no bucket holds one month's due.
  What is reasonable to ask is estimated from before: the average `minimum_due` of the last 12 months
  with a positive minimum due, before the first statement where only bucket 08 holds money
  (`resolve_bucket08_fallback_due`, kept). The waterfall's bucket-08 slicing goes with the waterfall
  method (D-A3-3).
- **D-A3-13: RL record before delinquency falls back to the last known EMI** (user, 2026-11-03, O81):
  a month without its own EMI snapshot is judged against `monthly_emi_asof`, as Dimension B does.
- **D-A3-14: RL refusal payment test reads the loan's own cash after the refusal** (user,
  2026-11-03, provisional on the strong-negative redesign, V2): `total_paid` ≥ 100 AED in a month
  after the refusal month, instead of Dimension B's any-payment flag.
- **D-A3-15: CC cycles are one month, statement to statement** (user, 2026-11-03: about a month,
  ~99% on the same day of the month). When a statement is missing (the 2021–2023 gap, the 2024-11/12
  run), the span to the next existing statement is several months long; such a span is dropped, not
  read as one month (`_PAYMENT_CYCLE_MAX_LENGTH_D` = 62 days, kept). The 35-day lookback before the
  history floor keeps the statement just before the floor.
- **D-A3-16: thresholds ship as the DE sheet proposes** (user, 2026-11-03): points cut-offs 4 / 1,
  commitments 12 months / 2 concluded / 80% / 40% / streak 3, payments 3 / 6 months, 2 of 3 / 3 of 6,
  100% of one month's due, record 12 months / 3 months due / 80%, 3 / 6 contact days. Sensitivity in V4.
- **D-A3-17: the output carries every signal that fed the decision** (user, 2026-11-03): the anchor
  (latest spell start), windows, dimension levels, points and their inputs (concluded / kept / rate /
  streak, qualifying-month count, any-payment flag, months due / paid), the strong-negative reason and
  its evidence. Not carried: per-method columns, confidence, provenance, `computed_at` (D-A3-4).

- **D-A3-18: A3 builds the source outputs it needs itself, for now** (user, 2026-11-03). No refactor of
  the core CC pipelines in this bundle; merging them into the CC primaries / features is a later
  option. The builders still lose their T0 windows (D-A3-1): rescoping them needs the current
  `cc_raw_extract/nodes.py` (`build_cc_acct_windows`, `build_cc_billing`) at bundle time.

- **D-A3-19: no contact-based negative in the state** (user, 2026-11-04, from V2). Today's no-response
  rule goes: it fires on 36% CC / 26% RL and is 84% / 78% A2 Non-Reachable (dead-line outcomes), so
  it re-derives A2. The avoidance variants overlap A2 too (66–76%). Two diagnostic columns stay in the
  output, outside the state, for analysis and the persona master:
  - no pickup after an earlier right-party contact: 3 days at 61–180, 6 at 180+ of ringing / no answer /
    left message, no dead-line outcome in between;
  - hang-up as the latest right-party contact.
  O85 goes with the rule.

- **D-A3-20: explicit refusal is A3's stated-intent negative; dispute is a column** (user, 2026-11-04,
  from V2). Refusal = the latest right-party contact in the delinquency is `REFUSE TO PAY`,
  `REFUSED TO PAY`, `KSA/REFUSE TO PAY` or `REWRITE NOT AGREED`, and no PTP / settlement and no payment
  ≥ 100 AED followed it up to the observation date. It takes the state one level down (4.4% CC and RL).
  `DISPUTE` / `KSA/DISPUTE` is a diagnostic column, not a negative (0.3% CC, 0 RL): a contested debt is
  not unwillingness. `CUSTOMER HUNG UP` moves to the avoidance diagnostics (D-A3-19);
  `CUSTOMER MISBEHAVED` is dropped. The `_dcore_codes.REFUSING` set is split accordingly (A3 only).

- **D-A3-21: both flow dimensions stay as they are; the overlap with A4 is reported** (user,
  2026-11-04, from V3). Payments drive the DPD path, so overlap is expected (V 0.53–0.62). Both
  dimensions still split A4's large states. `no_record` is A4's early payment default almost exactly.
  The axis report shows the crosstabs.
- **V4 read (2026-11-04):** the thresholds ship as decided (D-A3-16). Only the Moderate cut-off really
  matters: Moderate from 2 points instead of 1 moves 19% CC / 29% RL. High from 3 / 5 moves 2–6%;
  every other threshold moves ≤ 4%. High from 3 is the lever if High (today reachable only with DCORE
  commitments) should open to regular payments plus a clean record. Both are for the GRR calibration,
  not this bundle.

- **D-A3-24: Moderate from 2 points, High from 4** (user, 2026-11-09, from the threshold what-if,
  `bundle_helpers/a3_final/threshold_whatif_summary_60_180.md`; replaces D-A3-16's Moderate cut-off).
  A clean pre-delinquency record alone (1 point) no longer makes a customer Moderate: 85% of the CC
  rows it moves made no promise and paid nothing while delinquent, the group that rolls most (V1f Q8).
  60–180 states: CC 1.3 / 14.5 / 71.8 / 12.4 (High / Moderate / Low / Unknown), RL 1.6 / 24.0 / 67.6 /
  6.9. Ships in the next A3 bundle (`MODERATE_FROM = 2`).

- **D-A3-25: Dimension A = promise events judged by a sufficient payment, on GRR's deadline**
  (user, 2026-11-09, from V1f / V1g, `bundle_helpers/a3_final/thresholds_v1f_review.md`;
  replaces D-A3-11's instalment rule, ships in bundle 20).
  - Events: every non-cancelled PTP and settlement plan (dated at its start), plus every
    follow-up promise (`_dcore_codes.PROMISE_EVENT`: promise to pay, scheduled, digital collect,
    pay at salary; any action code) that no plan claims. Follow-up promises less than 8 days
    apart are one event, dated at the first; a plan takes its nearest follow-up promise within
    7 days, each at most once. SOFTPTP, RETAIN PTP, arrangement names without a plan and payment
    reports are not events. Account level.
  - Judged once: payments after the event day up to the deadline against the due of the cycle
    open on the event day (the last known one, at least 100 AED). Paid: they reach it; partial:
    100 AED or more (counts as not kept); else none. Concluded once the deadline is on or before
    the observation date.
  - Deadline (GRR; replaced by D-A3-28): CC the next statement after the event day, however close (no statement yet:
    31 days); RL the end of the next month (cash is month-level; the event month's cash counts
    in full). The 30-day alternative (V1g: higher AUC, CC 0.740 vs 0.714) is built in
    (`PROMISE_DEADLINE`) and logged by the bundle check, pending GRR.
  - The ladder and points are unchanged (Kept 2 / Partly kept 1 / Thin 0 / Broken −1).
  - Contact disposition: payment reports (`_dcore_codes.PAYMENT_REPORTED`) read `paid`.

- **D-A3-26: Dimension A's window = the last 12 months, regardless of the episode start** (user,
  2026-11-09; ships in bundle 20). A characterises trustworthiness, so promises from an earlier
  episode within 12 months count (`[obs − 12 m, obs]`, calendar months). This departs from D6 for
  Dimension A only: contacts and the refusal flag stay on the current episode, B on recency. Accepted
  overlaps: with C (a repeat delinquent's earlier episode can cost in both) and a little with B. The
  bundle 20 check measures it (state / level with the episode window vs 12 months, events before the
  episode start) before the logic is final.

- **D-A3-27: Unknown = no episode only** (user, 2026-11-10; ships in bundle 23, which absorbed
  bundle 22). No payment while delinquent (Dimension B `none`) is evidence that scores 0 points, not a
  silent level, so a row with an observed episode and no points in any dimension (mostly early
  payment defaults) is Low. Unknown stays only for rows with no episode anchor
  (`a3_unknown_reason = no_episode`); `no_evidence` no longer occurs.

- **D-A3-28: promise deadline = GRR's threshold, whatever date was promised** (GRR Teams answer,
  handoff 64, `bundle_helpers/a3_final/grr_broken_ptp_thresholds_handoff64.md`; user 2026-11-11:
  the promised date is ignored; ships in bundle 23 with D-A3-27, pending its check). Replaces D-A3-25's deadline:
  61–180 cards by the next statement after the promise day (unchanged); 61–180 loans by the end of
  the promise month (was the end of the next month); 180+ cards and loans by the end of the promise
  month. Paying on the deadline day counts. `PROMISE_DEADLINE` is keyed by segment (from
  `params:model_id`) and product; the 30-day and next-month-end options stay.

- **V1h back 2026-11-13** (`bundle_helpers/a3_final/v1h_review.md`): GRR's month end ranks worst for loans and at 180+ (RL 61–180 AUC 0.643 vs 0.666), 30 days best or equal in every book; the no-evidence rows are the weakest part of Low (D-A3-27 holds); Thin pays less than Broken (V1i running). Deadline open with GRR; bundle 23 step 8 on hold. Model document: `docs/credibility/build_a3_workbook.py` (updated 2026-11-13; detailed results from `sonnet_a3_detailed_results_prompt.md`).
- **V1i + detailed results back 2026-11-13** (`a3_final/v1i_summary.md`, `a3_detail_summary.md`): never promising (T0) is what separates, not breaking: Broken pays like one failed promise (T2) and well above T0, also inside reachable / contacted accounts. Broken +1 ranks best in every book, deadline and month (state AUC cc61 +.045, rl61 +.030, 180+ +.02/+.03), moves 12% / 8% of 61–180 rows Low → Moderate (they pay like Moderate); Thin −1 hurts the state. Open for the user / GRR: Broken +1 (or 0); next test: Broken and T2 raised together, Partly +2. Detail: High > Moderate > Low on payment in every split and month; states 88–90% stable at 61–180, 99% at 180+; Cramér's V with other axes ≤ 0.41 (A4 highest); the payment step is at 2 points in every book. To check: rl_60_180 shows no dispute (58 at 180+): the RL dispute code mapping.
- **D-A3-11 decided: payments judge** (user, 2026-11-09, from the bundle 17 check,
  `bundle_helpers/b17_a3/a3_check_review.md`). An instalment is kept when the payments since the plan
  start reach the plan's cumulative due by the first statement on or after the due date (CC) / the end
  of the next month (RL). The two judges agree on 96.2% (CC) / 97.2% (RL) of states; DCORE credited
  twice the kept instalments on CC (427 Highs rest only on it). The cumulative rule's cascade adds 1.8%
  Broken on CC (accepted for now). The `dcore` option and `params:a3_kept_by` go in the next A3
  bundle.
- **D-A3-22: council answers taken into the engine** (user, 2026-11-05, refactor review
  `questions.md`): anchor = the first day of the episode month (Q-11); rows A4 does not score are
  Unknown, `a3_unknown_reason = no_episode` (Q-12); calendar-month windows (Q-13); DCORE windows
  inclusive at the observation date (Q-22 / Q-27); a censored anchor (A4 cropped the history and the
  episode ran from its first kept month) counts as unknown: windows from the observation lookback,
  Dimension C No record, `pre_dlq_reason = censored` (Q-25); same-day ties on the latest right-party
  contact: a non-refusal counts as later, then the largest disposition (Q-28); "a payment of 100 AED
  after the refusal" = one cycle (CC) / month (RL) with 100 AED or more paid after the refusal day
  (Q-29); DCORE read at most 24 months back, both products, the bundle check reports the refusals the
  cap removes (Q-30); the onset cycle is in neither B nor C (Q-31); the instalments are an A3 source
  node (Q-32 (a), until the DE adds a DCORE primary).
- **D-A3-23: Broken scores −1 and is not a strong negative; refusal is the only one** (proposal
  2026-11-05, in bundle 17). The weight (today's override / 0 / −1 / −2) is reported by the bundle
  check's `A3 BROKEN` block; V1e part 2 (outcome) can still confirm it.

## Bundle 17 (built 2026-11-06)

`bundles/17_a3_credibility_engine.md`, on `611b23c..bf3b141` (branch `refactor/a3_stage`), after the
refactor bundles 15 (dead code) and 16 (shared layer, A4, A2, A1). Engine `a3_credibility/`
(constants, sources, signals, classify, pipeline) with CC / RL wrappers that build only the dues and
payments; spec test `checks/a3_engine_spec.py` (72-cell map, both judges, grace, windows, contacts,
instalments, Kedro runs of both products, the check). **Both D-A3-11 options ship**
(`params:a3_kept_by`: `payments` with grace to the first statement on or after the due date (CC) /
the end of the next month (RL), or `dcore`); the check `crx_<p>_a3_check` scores the latest month
both ways against today's output. The user picks the judge from the check blocks; the losing option
and the parameter then go in a small follow-up bundle.

## Validations before the bundle

Prompt for V1–V4: `bundle_helpers/a3_final/sonnet_a3_v1_v4_prompt.md`. Results (60_180):
`v1_v4_summary_60_180.md`, review `v1_v4_review.md`. V1c rerun with the corrected allocation:
`v1c_summary_60_180.md` (review: `v1_v4_review.md`, V1c). DCORE 'paid' is often not backed by card
payments (CC settlement 22%). Before deciding D-A3-11, the user wants to know where that money is (user,
2026-11-04): V1d, `sonnet_a3_v1d_missing_payments_prompt.md` (other card credits, Way4 last-payment
fields, balance movement, FTR legs of the CIF's other accounts, lateness, partials, DCORE fields, and
whether the delinquency behaves as if paid). The user also questions how strict the due date should be.


- **V1 (DCORE instalments, Sonnet, no photos unless needed):** confirm the columns and meaning of
  `dcore_prm_promise_instalments`, `dcore_prm_settlement_schedule_instalments`, `dcore_int_ptp`,
  `dcore_int_settlement` (agreement link, due / paid amounts, instalment and cancel statuses, what
  dcore's `instalment_amount_flags` calls paid / overdue); decide the layer the A3 node reads (the
  link sits in `dcore_int_*`, the instalments in `dcore_prm_*`; a feature table per agreement × month
  if the one-layer rule needs it); and compare the new 12-month counts with the `dcore_feat_*_12m`
  counts on PROD (aggregates) so a difference is explained before shipping.

- **V2 (strong-negative candidates, Sonnet, PROD aggregates):** direction (user, 2026-11-03):
  hard negatives only where they add to the picture; keep the axes orthogonal (A3 must not re-derive
  A2's Non-Reachable). Three candidates to explore (user, 2026-11-03), each measured on its own, at the
  latest month per model_id, CC and RL:
  - **Explicit refusal:** the latest right-party contact in the delinquency is a clear refusal
    (`REFUSE TO PAY`, `REFUSED TO PAY`, `KSA/REFUSE TO PAY`, `REWRITE NOT AGREED`), with no promise,
    arrangement or payment ≥ 100 AED after it.
  - **Dispute:** the same rule with `DISPUTE` / `KSA/DISPUTE`; it contests the debt, so it may be a
    flag rather than a negative.
  - **Avoidance:** the customer does not take calls on a working line. Variants:
    - N0, today's no-response rule (3 contact days in every band, as the code has it);
    - N1, ringing / no-answer / left-message outcomes on 3+ days (61–180) or 6+ days (180+, as A2's
      `GONE_DARK_DAYS`; user, 2026-11-03) in the delinquency, no dead-line outcome (`NOT_REACHABLE`)
      in between, no plan, no payment ≥ 100 AED;
    - N2, N1 but only after a right-party contact earlier in the delinquency;
    - N4, hang-ups (`CUSTOMER HUNG UP`, `CUSTOMER_HUNG_UP`) as the latest right-party contact, nothing
      after;
    - N3, none.
    Facts: A2 `FAILED_CALL` holds all 18 `NOT_REACHABLE` names and the ringing / no-answer /
    left-message ones, so any unanswered-calls rule overlaps Non-Reachable by construction. The old A2
    `avoiding` state was 24% of CC and split about evenly between the new reachable and non-reachable
    (b07 check).
  For every candidate, report:
  - the firing rate;
  - the crosstab with A2 reachability;
  - the A3 state distribution with and without it;
  - the result names that drive it, including how often each `REFUSING` name and `CUSTOMER MISBEHAVED`
    is the latest right-party contact;
  - the overlap between the candidates;
  - the rows each candidate moves against a run with no negative.

  The right-party definition is checked here too: today `rpc_confirmed` uses `RIGHT_PARTY_CONTACT`
  only, while the classifier also counts `HISTORICAL PROMISE TO PAY` / `RETAIN PTP` (O80).
- **V4 (threshold sensitivity, PROD aggregates):** latest-month A3 state distribution per model_id
  when each D-A3-16 threshold moves one step either way (e.g. High from 3 / 5, kept 70% / 90%, broken
  30% / 50%, streak 2 / 4, Regular 1 / 3 of 3, record clean 70% / 90%, months due 2 / 4), one at a
  time; report the rows that change state.

- **Later option, RL exact payments (user, 2026-11-04):** `comp_financial_tran_repos_dly` could give
  dated payments into the loan account instead of the monthly `int_loan_master.total_paid`. That would
  sharpen Dimension B / C, the promise-vs-ledger match (D-A3-11, today month-level for RL) and the RL
  refusal test (D-A3-14). A delinquent loan account carries many administrative / internal postings
  that are not customer payments, so it needs an EDA first to find the filter. Per the layer rule, it
  would come in as a primary (`prm_loan_payments`, customer payments only), not a raw read in A3. Not
  in this bundle unless decided.

## Open (asked 2026-11-03)

- **GRR's alternative Dimension A (user, 2026-11-09): promise events judged by a sufficient payment.**
  A promise comes from the PTP / settlement tables and the DCORE follow-up result names; it is paid
  when payments by the next statement (CC) / next month end (RL) cover the minimum payable due (oldest
  bucket / EMI), partial when some but not enough; DPD bucket movement as the indirect reading (also at
  180+). Exploration V1f, `bundle_helpers/a3_final/sonnet_a3_v1f_promise_events_prompt.md`: the
  follow-up promise set, coverage gain, outcome by payment vs bucket movement, overlap with Dimension
  B, levels, and which ranks next-3-month outcomes better. Bundle 17's instalment rule is the baseline.
  V1f back 2026-11-09 for 60_180 (`bundle_helpers/a3_final/v1f_summary_60_180.md`, review
  `thresholds_v1f_review.md`): follow-up promises raise coverage (33.5% vs 23.3% CC accounts) and are
  paid as often as table plans, but the payment reading depends on the grace window's length (a fixed
  window is needed), bucket movement adds nothing independent at 60–180, and A overlaps B in the
  recent months (A's own information is in older events). 180+ not run.


- Required inputs: settled by D2 (all A3 sources exist in PROD, so all are required; O73).
- D-A3-11: V1d back (2026-11-06, `v1d_summary_60_180.md`): the ledger is complete, DCORE 'paid' is premature (PTP) or late (settlement). Both options ship in bundle 17 for the comparison; proposal: payments, grace to the next statement. Open with it: the payments judge's cumulative rule breaks a settlement instalment that sits behind an earlier miss (V1d cascade addendum, `v1d_cascade_cc_60_180.md`: 65% of CC settlement G1 is behind an earlier miss, 72% pays its own amount by the cut-off); the user applies bundle 17 as is (2026-11-06) and reads the effect from the check (`A3 COMMITMENTS`, `A3 BROKEN`) before choosing.
- **Broken commitments, proposal (user, 2026-11-05): Broken scores negative points and leaves the
  strong-negative list; refusal stays the only strong negative.** Today Broken scores 0 and fires a
  negative; without A the maximum is 3 points (< High's 4), so it always means Low, even for a regular
  payer ("cap at Low" = keep). Dropping the negative alone would make Broken score like Thin. Promise
  points become Kept 2 / Partly kept 1 / Thin 0 / Broken −1 (or −2). Once Broken is in the points it
  fails strong-negative test 1 (adds nothing the points do not carry). The weight is picked by V1e
  (`sonnet_a3_v1e_broken_weight_prompt.md`: today / drop / −1 / −2, under both judges; next-3-month
  outcome of Broken vs Thin at the same B + C points). Broken with −1:

  | B + C points | Today | Drop | −1 | −2 |
  |---|---|---|---|---|
  | 0 | Low | Low | Low | Low |
  | 1 (Some, or Clean only) | Low | Moderate | Low | Low |
  | 2 (Regular, or Some + Clean) | Low | Moderate | Moderate | Low |
  | 3 (Regular + Clean) | Low | Moderate | Moderate | Moderate |

  Fallback if GRR finds the points opaque: grade from a trust (Kept / Partly / Thin / Broken) × flow
  (strong / some / none) table instead of summed points.
- **CC sources (superseded by D-A3-18 for this bundle; kept as the later option).** Today `crx_cc_billing` / `crx_cc_balance` / `crx_cc_transactions` (`cc_raw_extract`)
  read `raw_*` inside crx_persona, re-implement the `prm_cc` derivations and are scoped by T0 windows,
  which breaks D5 and the §7 layer rule. Proposal pending photos: the CC primary pipeline owns the raw
  reads (`prm_balance` / `prm_transaction` / a billing primary, extended with the columns A3 needs),
  the per-cycle ledger (`build_a3_payment_cycles`) becomes a CC feature, and A3 signals read obs base +
  that feature. Open: whether the CC primaries stay model-scoped or cover all contracts from a date floor.
