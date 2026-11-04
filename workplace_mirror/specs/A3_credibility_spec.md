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
  do not count), window = `[max(latest spell start, obs − 12 m), obs]` (spec rows 19, 76; O75, O83).
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

## Validations before the bundle

Prompt for V1–V4: `bundle_helpers/a3_final/sonnet_a3_v1_v4_prompt.md`.


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

- Required inputs: settled by D2 (all A3 sources exist in PROD, so all are required; O73).
- Strong negatives (broken commitments, refusal, dispute, avoidance): pending V1 and V2; O85's extra condition goes with the redesign.
- **CC sources (superseded by D-A3-18 for this bundle; kept as the later option).** Today `crx_cc_billing` / `crx_cc_balance` / `crx_cc_transactions` (`cc_raw_extract`)
  read `raw_*` inside crx_persona, re-implement the `prm_cc` derivations and are scoped by T0 windows,
  which breaks D5 and the §7 layer rule. Proposal pending photos: the CC primary pipeline owns the raw
  reads (`prm_balance` / `prm_transaction` / a billing primary, extended with the columns A3 needs),
  the per-cycle ledger (`build_a3_payment_cycles`) becomes a CC feature, and A3 signals read obs base +
  that feature. Open: whether the CC primaries stay model-scoped or cover all contracts from a date floor.
