# T05 — A4 CC: utilisation, spend & liquidity features

**Track A** · **Depends:** T03, T02, T01 · **PROD round trip:** Yes — validation snippet

**Goal.** Build the spend/liquidity half of the deterioration axis, anchored to T0.

**Why.** This is the group that separates a gradual over-indebtedness spiral from an
abrupt shock: a spiral shows rising utilisation, a cash-advance ramp and a slow spend
taper; a shock shows a cliff. Both look identical once the account is dry — the
difference is only visible before T0.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §3.2`. T01 reuse map. T02's window decision.

## Steps

1. **Reuse check (R14)** per feature — utilisation trends in particular are likely to
   exist already in some form. Record REUSE/ADAPT/BUILD.
2. Build against the T03 spell table using CC balance, utilisation and transaction
   sources (R15 — CC has dedicated tables for these, not just transaction history).
3. Implement the `§3.2` set: utilisation level/slope/acceleration across half-windows,
   cash-advance ramp and amount share, spend taper ratio, spend cliff flag, active-days
   share, transaction-count slope.
4. Respect null rules (≥ 4 non-null months for any slope).

## Done when

- Feature table built, keyed `(account_id, spell_id)`, joinable with T04's output.
- Null-rate and coverage report per segment.
- **T0-boundary leakage test passes** (R2).
- Reuse classification counts logged in `RESULTS.md`.
