# T04b — Re-anchor A4 payment/balance features + window truncation

**Track A** · **Depends:** T03b · **PROD round trip:** Yes — delta validation

**This is a rework card, not a rebuild.** The feature *formulas* from T04 are unchanged
and stay unchanged. What moved underneath them is the anchor (T03b) and the window
definition (`§3.0b`). Recompute, add four columns, prove the delta.

**Load.** `reference/feature_specs.md §3.0b` and `§3.1` only; `reference/snippet_contract.md`.

## What actually changed

1. **T0 moved** (T03b) — so every `W12 / H1 / H2` window moves with it. There is no
   partial recompute here: the anchor changed, so the features recompute. The *code*
   barely changes — it repoints at the corrected spell table.
2. **`W_pre` is now truncated** at the latest of `M0−12`, the month after
   `prior_spell_end`, `month(account_open_date)`, and the retention floor (`§3.0b`).
   New logic, user-ratified 2026-08-19 (truncate **and** flag).
3. **Windows are month-based, not day-based** (`§0`). `[T0−365d, T0)` becomes
   `[M0−12, M0)` with `F.add_months` / `F.months_between`, matching the existing
   pipelines. T0 is month-resolved anyway, so day offsets were false precision — and a
   mid-month boundary leaves the first and last monthly buckets partial, biasing every
   mean and slope. The onset month `M0` is excluded.

## Do NOT redo

- **Every feature definition in `§3.1`.** Formulas are correct and were already
  validated — `pay_dom_std`, `pay_dom_drift`, `pay_ratio_*`, `min_pay_share_w12`, the
  lot. Do not re-derive or re-justify them.
- The module structure, catalog entries, and the join to `obs` via `current_spell`.
- The full T04 validation battery — correctness of the formulas is settled. Validate
  only what moved (below).
- T02 (retention) — unaffected. Reuse its answer as the `retention_floor`; do not
  re-measure it.

## Do this

1. Repoint at T03b's corrected spell table.
2. **Switch the window boundaries to month arithmetic** (`§0`) — `F.add_months` on
   month-truncated dates. Keep day arithmetic for what genuinely measures days
   (`pay_dom_*`, `pay_gap_*_d`). Watch the `F.months_between` fractional-return footgun:
   truncate both sides to month start and floor, or diff a `yyyyMM` key.
3. Implement the `§3.0b` truncation:
   `w_pre_start = max(M0−12, month_after(prior_spell_end), month(account_open_date),
   retention_floor_month)`.
4. Emit four new columns on every row — `w_pre_start`, `w_pre_clean_m`,
   `w_pre_contaminated_flag`, `w_pre_truncation_reason`
   (`none | prior_spell | tenure | retention`).
5. **Make the ≥ 4-non-null-month slope rule count clean months**, not nominal ones. A
   slope fitted across a prior-spell boundary measures the boundary, not the
   deterioration — this is the single change most likely to alter feature *meaning*
   rather than just feature values.
6. Recompute the `§3.1` set. Keep the old output alongside (R18) so the delta is
   measurable.

## Validation snippet — a delta, not a re-validation

- **Truncation profile:** share of rows by `w_pre_truncation_reason`, and the
  distribution of `w_pre_clean_m`. If `prior_spell` dominates, repeat delinquency is
  common in this book and the old features were substantially mixed-regime — say so
  explicitly, it changes how T07 should read them.
- **NULL-rate shift per feature, old vs new.** Expect slopes to go NULL more often
  (clean-month rule). A feature whose NULL rate jumps past ~50% on a segment is no
  longer a feature there — flag it for T21 rather than shipping it quietly.
- **Distribution shift on the headline features** (`pay_dom_drift`, `pay_ratio_slope`,
  `pay_gap_last_d`): old vs new mean/median/decile. A large shift is expected and is
  evidence the old anchor was wrong; a *zero* shift means the repoint did not take —
  check before believing it.
- **T0-boundary leakage test (R2) re-run** — the window moved, so re-assert it. This is
  the one test worth repeating in full.
- ~20 rows with old vs new feature values side by side, for eyeballing.

## Done when

Features recomputed on the corrected anchor, the four truncation columns present, the
delta reported, and the leakage test passing. Log to `RESULTS.md`: the truncation
profile, the NULL-rate shifts, and any feature the clean-month rule effectively killed.
