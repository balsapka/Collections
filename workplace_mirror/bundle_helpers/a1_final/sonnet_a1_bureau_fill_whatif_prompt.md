# A1: fill bureau salary alerts until a change or stop — what-if + source disagreement (UAT → PROD → UAT)

## Goal

The bureau salary alert feed fires on a change (new level, account added, stop), not every month.
The user's argument: a positive alert level should hold until the next alert (a new level) or a 0
(a stop), with no cap, because silence means "no change". Today A1 carries a level one month
(S14). Test the argument on the data before it goes into the bureau swap bundle:

1. Does a filled level still predict ability as it ages?
2. Is silence really "no change"? Check it against the other salary sources: while a fill is active
   and no new alert arrives, does another source report a different salary, or a stopped one, that
   the alert table never turned into a change alert?

Exploration only: no pipeline, catalog or A1 code changes.

## Context and decisions already made

- Source: the DE's `feat_bureau_salary_unified` (your exploration `tmp_validation/a1_bureau_unified/
  summary.md`): `alert` is today's bureau series and event-like; `salary_credit` is our own bank's
  salary credits (a thin, thinning feed); `bureau_salary` is AECB pulls, 2025-09 .. 2026-08 only.
  Join: `cast(cif_id as string)`. Cap every series at the persona end month.
- The A1 rule is bundle 21's evidence-family rule (`a1_ability/classify.py`); income per month =
  the larger of internal (`feat_cif_internal_salary_monthly`) and bureau salary. RL's loan
  application salary is out of A1.
- **The user expects few disagreements for now:** the other sources are mostly application-time
  levels and the occasional bulk upload. Internal salary is the one monthly comparator. Report what
  the data show; low counts are not a failure.

## Feed facts (user, 2026-11-12)

- The alert table is loaded **daily in PROD** (`edp_load_date`); the sandpit copy was last refreshed a
  few weeks ago. Run the snippet in PROD and report the latest `edp_load_date` it sees; a thin
  latest month in another environment is a load lag, not a feed gap.
- **Alerts are complete from 2024-01 on.** Before that, a missing alert does not mean "no change".
  So: fills (C12 / CU / CU-W) start only from alert levels dated 2024-01 or later (an older level
  gets C1 only); feed health, the monitoring proxy and missed changes / stops are measured from
  2024-01 on. Report how many CIFs' latest positive level predates 2024 (they lose nothing against
  today, but cannot be filled).

## Fill variants (bureau series only; `salary_credit` is never filled, it is a monthly credit)

- **C1** (today): an alert or pull level counts in its month and the next; a 0 ends it.
- **C12**: filled forward until the next alert / pull row (new level) or a 0, at most 12 months.
- **CU**: as C12 with no cap (the user's argument).
- **CU-W**: as CU, but a level older than the window W counts as Weak only (never Stable): a
  reported level, not fresh evidence.

Check 0: rebuild today's `a1_income_level` and `a1_state` from today's inputs and confirm 0 rows
differ from `crx_<p>_a1_ability` (bundle 21 output). Then run C1 on the unified table as the
baseline for the variants.

## Questions (per model_id; 60_180 first)

1. **Feed health.** Salary alert rows per month (any month with < 50% of the 3-month mean is a
   gap); for CIFs with a positive alert in the last 24 months, months since the last salary alert at
   the persona end month (quantiles). **Monitoring proxy:** share of those CIFs that received any
   other alert type (any category, `prm_bureau_alert_enriched`) after their last salary alert —
   silence on salary is credible only while the customer still gets other alerts. Split by fill age
   (0–3, 4–6, 7–12, 13–24, 25+ months).
2. **Disagreement while a fill is active** (CU, last 24 months, cif-months with an active fill and no
   new alert that month):
   - share with another source present that month: internal salary, unified `salary_credit`, unified
     `bureau_salary`; and `feature_retail_loans` application salary for RL as a reference only;
   - where present: other / filled level within 10%, 10–25% higher, 10–25% lower, > 25% higher,
     > 25% lower; by source and fill age;
   - **missed changes:** of the > 25% disagreements, how many are followed by a new alert within
     1–3 months (the feed caught up) vs never (no change alert came);
   - **missed stops:** fills still active 2+ months after the CIF's internal salary stopped (positive
     in the 3 months before, then 0 / NULL for 2+ months) with no 0 alert: count, share of active
     fills with internal history, by fill age.
3. **States.** `a1_state` and `a1_income_level` for C1 (unified), C12, CU and CU-W against today:
   distribution and old × new moves for the latest persona month. At 180+, how many filled levels
   (CU) are older than the charge-off date (find the charge-off age on the spine / obs base).
4. **Quality (60_180, Jan–May 2026 cohort).** `cure_3` / `pay_any_3` with 95% CIs clustered on CIF
   (definitions as in bundle 21's check, `cohort_outcome_lines`; ask the user if the code is gone,
   or port it from `tmp_validation/a1_family_redesign/round3_snippet.py`) for rows whose income
   evidence is a filled bureau level only, by fill age (0–1 = today's carry, 2–3, 4–6, 7–12, 13+) and
   level (Stable / Weak); with internal Stable, today's bureau-only Stable and the persisted
   High / Moderate / Low / Unknown as reference. **The key test:** does a 7–12 or 13+ month old level
   still cure above none and near a fresh one? Also split by whether a disagreement or missed stop
   (question 2) occurred in the fill.

## Hard rules

- A Kedro-notebook snippet in a temporary tracked folder `tmp_validation/a1_bureau_fill/`; data
  through `catalog.load(...)` only; `model_id` from `catalog.load("params:model_id")`, in the results
  file name.
- Aggregates only: no CIF ids or customer rows; cells under 10 show `<10`.
- Reuse the engine's own functions for the levels and states where you can, so check 0 can pass.
- No pipeline, catalog or A1 code changes; no `kedro run`.

## Steps

1. UAT: write the snippet, commit, push; tell the user the run order (all four model_ids, 60_180
   first; switch `model_id` in `globals_dev.yml`).
2. PROD (user): run it per model_id; it writes `results_<model_id>.md`; the user commits and pushes.
3. UAT: write `summary.md` in the folder: check 0; per question a verdict and the key numbers per
   model_id; then **"Recommendation for the fill"**: C1 / C12 / CU / CU-W or a cap where the cure
   rate drops, with the evidence (fill-age outcomes, missed stops, monitoring proxy), and a short
   "For the DE" list of feed issues found. The user pastes `summary.md` back to Claude Code.
