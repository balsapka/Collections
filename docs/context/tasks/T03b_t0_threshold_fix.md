# T03b — T0 threshold fix (CC spell table)

**Track A** · **Depends:** T03 (done) · **PROD round trip:** Yes — delta validation

**This is a rework card, not a rebuild.** T03 shipped with the wrong delinquency
threshold. Change the threshold, re-derive, prove the delta. Do **not** re-run the full
T03 validation battery.

**Load.** `reference/feature_specs.md §2` only (the corrected threshold table);
`reference/snippet_contract.md`.

## The defect

T03's spec said *"T0 is the 0 → non-zero transition, spell end the return to 0."* On CC
that is wrong: code `1` means **due but not overdue** — ordinary revolver behaviour —
and delinquency starts at code **`2`** (0–30 DPD). Confirmed with the user 2026-08-19.

| | Wrong (as shipped) | Correct |
|---|---|---|
| CC spell starts | code ≥ 1 | **code ≥ 2** |
| CC cure | code = 0 | **code ≤ 1** |
| Loans | code ≥ 1 / cure at 0 | **unchanged — loans were already correct** |

**Expected fingerprint in the T03 output.** A revolver never returns to `0`, so the
string reads as permanently non-zero → one enormous spell, T0 at the customer's
first-ever statement, and `t0_censored_flag` set spuriously. Check the returned T03
numbers before doing anything: if censoring came back spread across *all* cohorts
rather than concentrated in 180+ >2y, that confirms it. **Record what the old rate was
— it is the before-measurement for this card and cannot be recovered once re-run.**

## Do NOT redo

- String orientation, as-of reference month — already confirmed in T03. Do not re-ask.
- The module, catalog entries, output schema, and join-to-`obs` logic.
- Restructure / succession handling (R13) — independent of the threshold.
- **The loan path** — the original rule was correct for loans. Leave it alone.
- The invariant test *harness* — only its threshold constants change.

## Do this

1. Replace the hardcoded boundary with a per-unit `DELINQ_MIN` constant (CC = 2,
   loan = 1). One constant, referenced everywhere — not a literal repeated per call site.
2. Add `prior_spell_end` to the output schema (previous spell's cure date, NULL for a
   first spell). T04b needs it for window truncation (`§3.0b`).
3. Re-derive spells. Keep the old table alongside under a distinct name — the delta
   snippet needs both, and R18 says additive anyway.
4. Update the two threshold-dependent invariants: cure is `code < DELINQ_MIN`, and
   outside spells the code is `< DELINQ_MIN` (**≤ 1 on CC**, not `= 0`).
5. **Check any bucket-code filter elsewhere in what you built** — "60+ DPD" is code ≥ 4
   on CC but ≥ 3 on loans. A shared constant silently selects the wrong population (R20).

## Validation snippet — a delta, not a re-validation

Old and new table, one round trip. Report:

- `t0_censored_flag` rate, **old vs new, by cohort** — the headline. New should
  concentrate in 180+ >2y; old probably did not.
- Spells per account, old vs new distribution.
- `t0_new − t0_old` in months: distribution, plus the count where old T0 was absent
  (censored) and new T0 exists — those accounts were unusable and now are not.
- Count of observations that change spell membership (this sizes T04b's rework).
- Re-run **only** the two threshold-dependent invariants, with violation counts.
- ~20 rows where T0 moved: raw bucket string, old T0, new T0 — for eyeballing.

## Done when

Delta reported and sane, invariants pass, and `RESULTS.md` carries the old-vs-new
censoring rates plus the count of affected observations. **T04b is unblocked only by
this card** — T05/T06/T07 have not run yet and will pick up the corrected table
directly, so they need no rework.
