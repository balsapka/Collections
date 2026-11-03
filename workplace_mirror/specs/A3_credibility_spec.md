# A3 payment credibility: spec (draft, decisions as they are taken)

Code reviewed: O66–O81 in `REVIEW_OBSERVATIONS.md`. The DE spec (`A3_credibility_shared.xlsx`,
"A3 framework") is not in the mirror yet; until it is, the rules below plus the code's `[CONFIRM]`
thresholds are the reference.

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

## Validations before the bundle

- **V1 (DCORE instalments, Sonnet, no photos unless needed):** confirm the columns and meaning of
  `dcore_prm_promise_instalments`, `dcore_prm_settlement_schedule_instalments`, `dcore_int_ptp`,
  `dcore_int_settlement` (agreement link, due / paid amounts, instalment and cancel statuses, what
  dcore's `instalment_amount_flags` calls paid / overdue); decide the layer the A3 node reads (the
  link sits in `dcore_int_*`, the instalments in `dcore_prm_*`; a feature table per agreement × month
  if the one-layer rule needs it); and compare the new 12-month counts with the `dcore_feat_*_12m`
  counts on PROD (aggregates) so a difference is explained before shipping.

## Open (asked 2026-11-03)

- Required inputs (D2) for all DCORE tables and `crx_cc_transactions` (O73)?
- `cc_a3_history_floor_date`: keep and measure, or drop (O77)?
- Ladder: a clean record alone (1 point) gives Moderate; Unknown plus a strong negative gives Low; the
  `[CONFIRM]` thresholds stand until GRR says otherwise.
- **CC sources (user, 2026-11-03: review whether the builders are needed or belong in the CC
  pipelines).** Today `crx_cc_billing` / `crx_cc_balance` / `crx_cc_transactions` (`cc_raw_extract`)
  read `raw_*` inside crx_persona, re-implement the `prm_cc` derivations and are scoped by T0 windows,
  which breaks D5 and the §7 layer rule. Proposal pending photos: the CC primary pipeline owns the raw
  reads (`prm_balance` / `prm_transaction` / a billing primary, extended with the columns A3 needs),
  the per-cycle ledger (`build_a3_payment_cycles`) becomes a CC feature, and A3 signals read obs base +
  that feature. Open: whether the CC primaries stay model-scoped or cover all contracts from a date floor.
