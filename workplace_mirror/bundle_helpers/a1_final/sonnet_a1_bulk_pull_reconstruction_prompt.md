# A1: the bureau bulk pull in the DE's unified salary table — code read, coverage, alert-shaped months (UAT → PROD → UAT)

## Goal

The bank's ad-hoc bulk bureau pull (`salary_source = "bureau_salary"` in the DE's
`feat_bureau_salary_unified`) will become our primary bureau salary source: GRR is pushing for a
pull of every 61–180 customer, and with a pull every ~2 months its cross-bank aggregates (`_1m`,
`_3m`, ...) pin each month's salary. Until then the monthly amounts the DE infers from one pull's
aggregates must be shaped by the alert table (an alert marks the month the salary changes) instead
of a flat spread. Answer three questions so we can brief the DE:

1. **Coverage.** How many customers does the raw pull cover, before the unified precedence
   (`alert > salary_credit > bureau_salary`) hides pull months behind alert / salary_credit months?
   The user expects ~5%. In the unified output the pull shows for only 0.1–1.4% of CIFs.
2. **Today's spreading rule.** Exactly how the DE's code turns the pull's aggregates into monthly
   rows.
3. **An alert-shaped rebuild.** Propose one and measure it against the flat spread.

Exploration only: no change to the DE's code, our pipelines, catalog or A1 code.

## Context and decisions already made (user, 2026-11-12)

All three unified sources are **bureau** data:
- `alert`: fires on a salary change (new level, stop); a fill-until-change what-if is running separately
  (`tmp_validation/a1_bureau_fill/`; don't redo it, reuse its helpers if useful).
- `salary_credit`: bureau salary history across providers, captured as a look-back when a customer
  applies for a new product with us (so most delinquent customers have none, and it thins in recent
  months). Your earlier exploration called it "our own salary credits": that reading was wrong.
- `bureau_salary`: the ad-hoc bulk pull; aggregates across all banks, months inferred back by the DE.
  In the unified output: ~600 rows a month, 2025-09 .. 2026-08 only (cc_60_180), a third of its CIFs
  with 2+ month gaps.

Our internal salary (`feat_cif_internal_salary_monthly`, WM's monthly sum of salary-flagged credits)
is the ground truth for customers paid into our bank: a cross-bank pull should match it or exceed it
(salary at other banks), never be clearly below it for long.

## What to do

**UAT (code).** Read the DE's branch `bureau-pipeline-analysis` without merging it (`git fetch`,
`git show origin/bureau-pipeline-analysis:<path>`), starting at
`src/enbd_collections/nodes/features/bureau/feat_bureau_salary_unified.py` and following every input
back to its raw/staging tables and catalog entries. Write down for each source: table, the columns
used, the date that becomes `salary_month_end`, and for `bureau_salary`:
- which aggregate columns are read (`_1m`, `_3m`, `_6m`, `_12m`, others), and the pull date column;
- the formula that gives each month's amount (even split of a total? differences between nested
  windows, e.g. `(_3m − _1m) / 2` for months 2–3? something else?), how far back it goes, and what
  happens with NULL / 0 aggregates, negative differences, and two pulls whose windows overlap;
- how the precedence step drops pull months.

**PROD (snippet).** Write a Kedro-notebook snippet in a temporary tracked folder
`tmp_validation/a1_bulk_pull/`, commit and push; the user runs it in PROD for all four model_ids
(switching `model_id` in `globals_dev.yml`) and commits the results. Measure, per model_id:
- **Coverage before precedence:** CIFs with at least one raw pull row, as a share of (a) the latest
  persona month's obs base and (b) the Jan–May 2026 cohort used in the bundle 21 check; number of
  distinct pull dates and CIFs per pull date; CIFs pulled more than once and the gap between pulls.
  Then the share of raw pull CIF-months that the unified output replaces with alert / salary_credit.
- **Spreading check:** the share of pull CIFs whose inferred months are flat (one value across the
  window) versus varying.
- **Truth test (pull vs internal):** for pull CIFs that also have internal salary in the pull window:
  per month, inferred pull amount vs internal (within 5%, pull higher, pull lower by >25%); a month
  where internal salary changes level or stops but the inferred pull stays flat.
- **Alert-shaped rebuild:** for pull CIFs with alerts inside the pull window, rebuild the months as
  piecewise-constant levels that change only in alert months (new level or stop) and still add up to
  each pulled aggregate (state your exact fitting rule; where the aggregates and alerts can't both be
  met, say how you resolve it and count those CIFs). Compare flat spread vs rebuild on the truth test
  above. Also report how many pull CIFs have no alert in the window (the rebuild is flat for them).
- **Effect on A1 income:** for the latest persona month, how many rows' income level (S12 Stable /
  Weak / none) would change between the flat spread and the rebuild (count only; no A1 rerun needed
  if you can apply `income_level` to the rebuilt series; if not, say so).

**UAT (summary).** Write `tmp_validation/a1_bulk_pull/summary.md` for the user to paste back.

## Hard rules

- Data only through `catalog.load(...)`; `model_id` from `catalog.load("params:model_id")`, in every
  output filename; never hardcoded or overridden. If a raw pull table the DE reads has no catalog entry
  on our branch, add a temporary entry in a new file `conf/base/catalog/tmp_a1_bulk_pull.yml` (copy
  the DE's definition), name it in the summary, and leave it for the cleanup.
- Aggregates only in the results files: no customer rows, no CIF ids.
- Cap every series at the persona end month. Join keys: `cast(cif_id as string)`.
- No edits to the DE branch, to pipelines, A1 code or permanent catalog files.

## Deliverable: `summary.md`

1. **DE code, per source** (table, columns, date, precedence) and the **exact `bureau_salary` monthly
   formula**, quoting the lines (file:line on the DE branch). Flag anything that looks wrong.
2. **Coverage** table (four model_ids): raw pull CIFs and share of obs base / cohort, pull dates, repeat
   pulls, share hidden by precedence. Verdict on the user's ~5%.
3. **Spreading and truth test:** flat vs varying; pull vs internal agreement; missed changes / stops.
4. **Rebuild:** the fitting rule in plain words, CIFs it applies to, conflicts, flat vs rebuild on the
   truth test, A1 income rows that change.
5. **Questions for the DE** that the code and data leave open (e.g. pull schedule, why rows stop after
   2026-08), and anything you would change in the unified node, as a short design note (not code).

Keep it short: verdict + key numbers per section. Then tell the user the folder and catalog file can
be deleted after the results are pasted back.
