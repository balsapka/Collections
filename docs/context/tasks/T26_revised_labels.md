# T26 — Revised labels

**Goal.** Add the new target labels beside the existing ones: futility and expected
recovery at 60–180, hurdle components at 180+.

**Why.** The current targets do not match the decisions they support. The 60–180 roll
label treats an account paying half its installment the same as one that vanished —
opposite cases for an exclusion decision. The 180+ dual threshold (5% or 1000 AED)
means different things at different balances, and a binary at a low bar erases the
differentiation being asked for.

**Precondition.** T02 — succession postings must be identifiable, or a restructure
reads as recovery and every new label inherits the error.

**Load.** `reference/feature_specs.md §1` (definitions and parameters).

## Steps

1. Implement `payments(a, t1, t2]` per `§1`, **excluding succession/restructure
   postings** (R13). Emit `succession_excluded_flag` on every row so contamination
   stays measurable.
2. Build: `futility_60_180`, `recovery_aed_60_180`, `any_recovery_180p`,
   `recovery_amount_180p`.
3. Parameters from config with the `§1` defaults, each marked CONFIRM: horizon `N`,
   negligible threshold `ε`, the 180+ noise floor.
4. Add `restructured_in_horizon`; default = exclude from futility *training*, keep in
   reporting, never score a restructure as recovery.
5. **Keep the roll and 5%/1000 labels running unchanged** (R11) — they remain the
   reported metrics and provide continuity.

## Done when

- Label tables build for all segments; prevalence per segment logged in `RESULTS.md`
  (expect futility prevalence to differ substantially from the roll-negative rate —
  if it does not, check the ε threshold).
- Unit tests cover: horizon boundary conditions, `ε` edge cases, succession-posting
  exclusion, and re-run of the existing leakage tests (R2).
- The CONFIRM parameters are listed for the user to ratify.
