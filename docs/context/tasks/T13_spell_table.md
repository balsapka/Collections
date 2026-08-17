# T13 — Spell / T0 table (CC)

**Goal.** Build the delinquency-spell table that anchors every A4 feature: one row per
account × spell, with `T0` (spell start).

**Why.** A4 characterises *how* a customer deteriorated, which only means anything
relative to when the trouble started — not relative to the calendar or the observation
date. Anchoring wrong silently destroys the signal, so this is built once, tested, and
reused.

**Load.** `reference/feature_specs.md §2` (full spec). Reuse map from T11 (R14) —
spell/window helpers may already exist.

## Steps

1. **Check T11's reuse map first.** If an equivalent spell or delinquency-episode table
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
4. Where T03/T04 supplied a succession link, set `predecessor_account_id` and
   `inherited_history_flag = 1` on the successor (strict confidence only — wrong
   history is worse than none).
5. Emit the schema in `§2`, built for CC only (loans are a separate pipeline, R3).

## Done when

- Invariants tested: spells per account non-overlapping; `t0 <= obs <= spell_end` for
  every joined observation; `DPD = 0` outside spells; no spell bridges a closure;
  `inherited_history_flag = 1` resolves to exactly one predecessor.
- A sample is spot-checked against raw DPD history by hand.
- Spell count, mean spells per account, and inherited-history coverage logged in
  `RESULTS.md`.
