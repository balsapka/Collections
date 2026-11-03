# A1 ability — AECB what-if: what frequent bureau pulls would change (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session (branch `feature/persona_redesign`,
bundle 12 applied).

---

## Goal

GRR will deliver AECB salary pulls every 2 months. Today A1's bureau salary comes from the AECB
**alert** table, which only fires on a change, so most customers have no recent AECB value. We
need two numbers for GRR: how much of today's A1 result is caused by the thin AECB data, and a
range of what to expect once pulls are frequent. Do this by rescoring the latest month of the
**real A1 output** with a longer AECB validity, no code change to the pipeline.

## How A1 uses AECB today (decided, do not change)

- `feat_cif_bureau_salary_monthly` (from `prm_bureau_alert_enriched`): one row per
  `(cif_id, month_end)` with a pull; types 31 / 32 give the amount, type 43 (salary account
  closed) gives 0. RL also adds the salary on `feature_retail_loans`' latest pull.
- `a1_ability/signals.py::build_income_signals` carries each pull to its month and the next one
  only (`_with_next_month`); never backwards. Income per month = the larger of internal and AECB.
- `a1_ability/classify.py`: S12 window total + 25% rule (level check when no internal salary).
  Window W = 3 months at 60–180, 6 at 180+.

## Scenarios

A pull counts in its month and the next `K` months, stopping at the next pull (a closure, 0,
stops it); never backwards. Everything else stays exactly as in the pipeline.

| Scenario | K | Reads as |
|---|---|---|
| S0 | 1 | today; must reproduce `crx_<p>_a1_ability` (0 states and 0 income levels differ) |
| S6 | 5 | the last AECB salary in 6 months still holds (≈ what a 2-month pull would confirm) |
| S12 | 11 | the last AECB salary in 12 months still holds (upper bound) |

S6 / S12 are ceilings for customers who already had an AECB salary; they cannot show customers
who never had a salary alert (a steady salary never alerts). Report that group separately (below).

## Hard rules

- Kedro notebook snippet in a temporary **tracked** folder `tmp_validation/a1_aecb_whatif/`;
  commit and push it. All data via `catalog.load(...)`; `model_id = catalog.load("params:model_id")`,
  in every output filename; never hardcoded or overridden. No `spark.read`, no paths.
- Reuse the engine functions (`build_income_signals`, `income_level` / `build_a1_ability` or the
  pieces they call); only the AECB carry changes. If an input the engine needs is not persisted,
  rebuild it with the pipeline's own node function from catalog inputs; say which.
- Latest observation month only (`persona_end_date`'s month). Aggregates only: no customer rows,
  no IDs, counts and shares. Cells under 10 shown as `<10`.
- No pipeline, catalog or registry changes.

## Results to save (`results_<model_id>.md`, one per model_id)

1. S0 check: rows, states and income levels that differ from `crx_<p>_a1_ability` (must be 0).
2. State distribution (high / moderate / low / unknown, n and %) for S0, S6, S12; RL also by product
   (`rl_spine.loan_type`: Personal / Personal Cash / Auto).
3. Moves S0 → S6 and S0 → S12 (from state × to state, n).
4. Income level (stable / weak / none) × income source (internal / bureau / both / none) per scenario.
5. S0 Unknown and S0 Low split by the latest AECB salary alert ≥ AED 1,000 before the carry:
   in W / 4–6 m / 7–12 m / 13–24 m / 25+ m / alert rows, never a salary / no alert row (at 180+,
   W covers 1–6). For each cell: n, and the S6 and S12 state they end in.
6. The never-alerted group: customers with alert rows but no salary alert ever, × internal salary
   history (in W / 4–6 / 7–12 / 13–24 m / none in 24 m), and their S0 state. Internal salary here
   shows how many of them are salaried yet never produced a salary alert.
7. Alert-feed coverage of the base CIFs: any alert row in the last 6 / 12 / 24 months; share with
   a salary alert in those periods.

Run for `cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus` (switch `model_id` in
`conf/dev/globals_dev.yml`, switch back after). The user runs it in PROD and commits the result
files.

## Summary (back in UAT, after the results are committed)

Write `tmp_validation/a1_aecb_whatif/summary.md`, one section per model_id:
- S0 check: pass / fail.
- A table of states S0 / S6 / S12 (n, %).
- The 3 biggest moves S0 → S12, with n.
- Unknown and Low: what share has an older AECB salary (4–24 m), and where it lands in S6 / S12.
- Never-alerted group: n, and how many have an internal salary in 24 months.
- One-line verdict: how much of Unknown is "AECB too old" vs "no AECB salary ever".
The user pastes the summary back here.
