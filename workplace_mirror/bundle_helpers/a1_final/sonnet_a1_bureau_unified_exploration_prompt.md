# A1: explore `feat_bureau_salary_unified` before it replaces our bureau salary (UAT → PROD → UAT)

## Goal

The DE delivered `feat_bureau_salary_unified` (already built for all four model_ids; catalog entry in
`catalog_bureau.yml`; your handover `tasks/bureau_salary_unified_handover.md`). It will replace A1's
bureau salary input in a bundle after bundle 21. Before that we need to know what the table holds,
how it is populated, and how its coverage compares with what A1 reads today, so the swap has no
surprises. **Exploration only: no pipeline, catalog or A1 code changes.**

## Decisions already made (user, 2026-11-11)

- The swap goes through our contract: the bureau feature node rebuilds `feat_cif_bureau_salary_monthly`
  (`cif_id`, `month_end`, `bureau_salary`) from the unified table; the A1 engine stays as it is.
- The one-month carry (`signals._with_next_month`, S14) is removed with the swap.
- RL's `feature_retail_loans` salary (`_loan_bureau_salary`) is dropped: it is the loan application's
  salary, not a monthly series.
- Income per month stays the larger of internal salary (`feat_cif_internal_salary_monthly`) and
  bureau salary.

## Questions to answer (per model_id)

1. **Shape and population.** Rows, distinct CIFs, `salary_month_end` range and rows per month,
   `salary_source` mix (rows and CIFs, overall and per month for the last 18 months), share of 0
   rows by source, amount quantiles by source (p5 / p25 / p50 / p75 / p95), whether every
   `salary_month_end` is a month end. Is the latest month populated as fully as earlier months
   (freshness)?
2. **Keys.** `cif_id` is `long` in the unified table; ours is a string. Share of obs-base CIFs that
   match by `cast(long as string)`, by casting ours to long, and how many of our CIF strings have
   leading zeros or non-digits. Recommend the join cast.
3. **Cadence.** Per CIF with any salary in the last 12 months: months with a positive value, longest
   gap, by `salary_source`. Is it a monthly series (most CIFs 10–12 months) or event-like? Where do
   0 rows sit (after a positive month, isolated, at the start)?
4. **What `salary_credit` is.** Overlap of `salary_credit` cif-months with our internal salary
   (`feat_cif_internal_salary_monthly`, positive months): share of cif-months in both, and amount
   agreement where both exist (ratio buckets: within 5%, 5–25%, > 25%). Same for `alert` rows against
   our current bureau series (`feat_cif_bureau_salary_monthly`). Verdict: is `salary_credit` our own
   salary credits or the bureau's view of salary at any bank?
5. **Coverage against today.** On the obs base, for the latest persona month and for the Jan–May 2026
   cohort (60_180 only): share of rows with salary evidence (a month ≥ AED 1,000 in the window W)
   from: internal only / current bureau only (with the carry, plus the RL loan source as the engine
   does today) / unified only (no carry) / both / none. A 2×2 of current bureau vs unified evidence.
   How many of today's no-internal-salary rows gain a salary from the unified table?
6. **Effect on the income family (F1).** Recompute `a1_income_level` (stable / weak / none) with the
   unified series in place of the current bureau series (no carry, no RL loan source), using the
   engine's own `income_level` logic, and crosstab old × new for the latest month. Count separately
   the bureau-only windows whose S12 "not weakening" test changes because the unified series has
   real 0 months where the alert series had none.
7. **Quality signal (60_180 only).** For the Jan–May cohort, `cure_3` / `pay_any_3` (the definitions
   in `a1_ability/check.py`, `cohort_outcome_lines`) by income source (internal / unified-only /
   none) × new income level. Does a unified-only Stable cure like an internal Stable (round 3:
   internal Stable ≈ High, bureau-only Stable ≈ Moderate)?

## Hard rules

- A Kedro-notebook snippet in a temporary tracked folder `tmp_validation/a1_bureau_unified/`;
  data through `catalog.load(...)` only; `model_id` from `catalog.load("params:model_id")`, in the
  results file name; never hardcoded.
- Aggregates only: no CIF ids, no customer rows; cells under 10 show `<10`.
- No changes to pipelines, catalog or A1 code; no `kedro run`.

## Steps

1. UAT: write the snippet, commit, push. Tell the user the run order: all four model_ids
   (switch `model_id` in `globals_dev.yml`), 60_180 first.
2. PROD (user): run it per model_id; it writes `results_<model_id>.md` to the folder; the user
   commits and pushes.
3. UAT: analyse and write `summary.md` in the folder: per question a verdict and the key numbers per
   model_id, then a "What to expect from the swap" section (coverage change, income-level moves,
   anything that needs a decision before the bundle: the join cast, the 0 rows, the S12 test, the
   `salary_credit` overlap). The user pastes `summary.md` back to Claude Code.
