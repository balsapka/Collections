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
  The exact scope (Dimension B qualifying and any-payment, Dimension C, the refusal follow-up) is
  being settled with the open items below.

## Open (asked 2026-11-03)

- 180+ windows: by `model_id`, as A1 / A2 do, or by the row's current bucket (O74)?
- DCORE link: A2's `prm_dcore_account_agreements` (all agreements of the account); account level or
  CIF level (O72)?
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
