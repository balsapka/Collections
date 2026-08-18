# T03 — Spell / T0 table (CC)

**Track A** · **Depends:** T01 · **PROD round trip:** Yes — validation snippet

**Goal.** Build the delinquency-spell table that anchors every A4 feature: one row per
account × spell, with `T0` (spell start).

**Why.** A4 characterises *how* a customer deteriorated, which only means anything
relative to when the trouble started — not relative to the calendar or the observation
date. Anchoring wrong silently destroys the signal, so this is built once, tested, and
reused.

**Load.** `reference/feature_specs.md §2` (full spec). Reuse map from T01 (R14) —
spell/window helpers may already exist.

## Steps

1. **Check T01's reuse map first.** If an equivalent spell or delinquency-episode table
   exists, adapt it rather than building new.
2. **Use the existing 24-month DPD bucket history feature** (the `33321000…` string) —
   T0 is the 0 → non-zero transition, spell end the return to 0. This makes CC
   derivation nearly free. First confirm: string orientation, as-of reference month,
   bucket encoding.
   - **Set `t0_censored_flag = 1`** where the string is entirely non-zero — the spell
     began beyond the 24-month horizon and T0 is unknowable from it. Do not guess.
     Expect this to hit the 180+ >2y cohort hardest.
   - T0 lands at **month** resolution. Optionally refine to a day using CC
     payment/balance tables; record which resolution was used.
   - Loans have no such feature and need bucket reconstruction from the full data
     model — out of scope here (separate pipeline, R3).
3. **Restructures (R13):** the old account's spell ends at closure with
   `spell_end_reason = 'restructure_closure'`. Do **not** bridge DPD resets within an
   account — that mechanic does not exist here.
4. Where T18/T19 supplied a succession link, set `predecessor_account_id` and
   `inherited_history_flag = 1` on the successor (strict confidence only — wrong
   history is worse than none).
5. Emit the schema in `§2`, built for CC only (loans are a separate pipeline, R3).

## Done when

Code is written blind in UAT, so it ships with a **validation snippet** (R17,
`reference/snippet_contract.md`) that the user runs in PROD. Not done until that
output comes back clean.

The validation snippet must report:
- **Invariants:** spells per account non-overlapping; `t0 <= obs <= spell_end` for
  every joined observation; `DPD = 0` outside spells; no spell bridges a closure;
  `inherited_history_flag = 1` resolves to exactly one predecessor. Print a
  pass/fail plus a violation count per invariant — counts make the fix obvious.
- **Distributions:** spell count, mean spells per account, `t0_censored_flag` rate by
  cohort (expect it concentrated in 180+ >2y), inherited-history coverage.
- **A ~20-row sample** of accounts with their derived spells, for eyeballing against
  the raw DPD string.

Log the returned output in `RESULTS.md`. Expect at least one fix round — write the
snippet to surface *what* broke, not just that something did.
