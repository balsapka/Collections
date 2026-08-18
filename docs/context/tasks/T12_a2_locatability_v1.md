# T12 — A2 locatability v1 (rules)

**Track A** · **Depends:** T03, T01, T06 · **PROD round trip:** Yes — validation snippet

**Goal.** Assign each delinquent account a contact state — `gone`, `skip`, `avoiding`,
`reachable` — using core-banking signals plus the sourced retail departure features.

**Why.** This is the axis with the cleanest action mapping: `gone` means field visits
are wasted, `skip` means tracing works, `avoiding` means the customer is reachable and
choosing not to pay (an escalation case, not a locating one). It also survives if DCORE
proves untrustworthy, because the core signals come from banking data.

**Load.** `reference/snippet_contract.md`; `reference/feature_specs.md §4` (signals and v1 rules). T01 reuse map; T06's
departure features.

## Steps

1. **Reuse first (R14):** the departure signals overlap heavily with T06's output and
   the sourced retail features. Reuse rather than recompute.
2. Build the [CORE] signals in `§4.1`: per-channel activity gaps, channel-death
   simultaneity, post-T0 domestic activity, travel/foreign flags, other-product
   activity.
3. Apply the `§4.3` v1 rules. Include DCORE delivery/disposition signals **only** if
   T11 cleared them.
4. Emit state + confidence + `observed|inferred` (R6).

## Important limitation to respect

Without trustworthy DCORE, `reachable` cannot be distinguished honestly — it needs
right-party-contact evidence. In that case emit **three** states
(`gone` / `active-but-not-paying` / `unknown`) and say so in the output schema and
documentation. Do not fabricate a fourth state to make the grid look complete.

## Done when

State assigned across the CC delinquent book with confidence and provenance flags;
state distribution per segment logged in `RESULTS.md`; face-validity table produced
(do the states differ in observable behaviour in the expected direction?); the
DCORE-dependent portion clearly marked as included or excluded.
