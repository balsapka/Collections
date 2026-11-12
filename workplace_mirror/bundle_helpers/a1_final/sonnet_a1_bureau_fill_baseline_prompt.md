# A1: does a silent salary alert mean "no change"? — baseline rerun (UAT → PROD → UAT)

## Goal

Decide **on the data** whether a bureau salary alert level can be filled forward until the next alert
or a stop, and up to which age. Your first run (`tmp_validation/a1_bureau_fill/summary.md`) showed the
feed is live for silent CIFs and that missed stops are rare up to ~6 months and common after a year.
It could not settle three things, and this run is for those only:

1. **No baseline for disagreement.** While a level was filled, the other sources were > 25% off in
   37–67% of cases. We don't know how often they disagree when the alert is fresh (same month). The
   sources differ by definition (alert = one salary-credit amount; `salary_credit` = sum across
   providers; the pull = spread from 1 / 3 / 6 / 12-month totals; internal includes bonuses), so some
   disagreement is expected even with no staleness. Disagreement counts against the fill only where it
   is higher than at age 0.
2. **Hidden stops.** The unified table shows a `salary_credit` row instead of a 0 alert in the same
   month, so the fill could not see every stop, and some "missed stops" may not be missed.
3. **The pull may be one month late.** The pull's codes 232–235 are "salaries reported for the last
   month / 3 / 6 / 12 months", and the user suspects month 1 is booked to the pull month instead of the
   month before.

**Cure / pay rates are not part of this run** (user): the question is whether the data support the
assumption, not what a filled level is worth.

## Decisions and facts already settled

- Every unified source is bureau data (user, 2026-11-12). `alert`: change events from the AECB alert
  feed; `salary_credit`: cross-provider salary history captured as a look-back at a new-product
  application (thin for delinquent customers); `bureau_salary`: the ad-hoc bulk pull.
- The alert feed loads daily in PROD (`edp_load_date`) and is complete from **2024-01**; levels dated
  earlier are out of scope. Series end at the persona end month (2026-08) for the age bands; for
  "did an alert eventually come" you may look up to the latest load, and say so.
- Internal salary = `feat_cif_internal_salary_monthly` (our bank only). A stop there can be a move
  of the salary to another bank, which is not a stop of the salary itself.

## What to measure (all four model_ids)

Build the **raw alert level series**, not the unified one: the salary alert types the DE's
`int_bureau_alert_salary_monthly` uses (read the logic on `origin/bureau-pipeline-analysis`; rebuild it
from the alert dataset our catalog has, e.g. `prm_bureau_alert_enriched`, or load the DE's dataset if
our catalog has it), latest alert per CIF-month, positive amount = a level, 0 / closed-account type =
a stop. **Alert age** at month m = months since the CIF's latest salary alert at or before m (age 0 =
an alert in m).

1. **Disagreement by alert age, against age 0.** For each comparator (internal; `salary_credit`; the
   pull at lag 0 **and** at lag −1, i.e. pull month m compared at m and at m−1): CIF-months with a
   positive alert level and the comparator present that month, by alert age 0 / 1 / 2–3 / 4–6 / 7–12 /
   13–24 / 25+. Report n, share within 10%, share > 25% higher, share > 25% lower, and the median
   comparator / alert ratio, with 95% CIs clustered on CIF. Then the same **within CIF**: only CIFs
   that have a comparison at age 0 and at the later age, so composition doesn't drive the gap. For the
   pull, say which lag agrees better at age 0 (that is the booking month).
2. **Comparator movement while the alert is silent.** For CIF-months at age ≥ 1: did the comparator
   move > 25% between the alert month and m (internal: use the median of the 3 months ending at each
   point, to damp bonuses)? Share by age band; and of those, the share where an alert arrived within 3
   months, later, never. As a reference, the same movement share over the same horizon for CIFs whose
   alert did change (a new level) in that span.
3. **Stops on the raw series.** Fill months where the internal salary stopped (positive before, none
   for 2+ months) and no raw 0 / closed alert came: by age band, as a share of fill months with
   internal history. Split each case by what else happened: a "salary account added" alert within ±2
   months (likely a bank move), `salary_credit` or the pull still positive after the stop (salary goes
   on elsewhere), or nothing. Then: how many of your first run's missed stops had a raw 0 alert that the
   unified precedence hid.
4. **How late stops arrive.** Where an internal stop and a later raw 0 / closed alert both exist: the
   lag in months (distribution). And for the 0 alerts of the 2026-07 bulk month: how long the level had
   been silent before (distribution), against 0 alerts in normal months.

## Hard rules

- Data only through `catalog.load(...)`; `model_id` from `catalog.load("params:model_id")`, in every
  output filename; never hardcoded or overridden. If you need a DE dataset our catalog lacks, add a
  temporary entry in a new `conf/base/catalog/tmp_a1_bureau_fill.yml`, name it in the summary, and leave
  it for the cleanup.
- Aggregates only in the results files (no customer rows, no CIF ids); a cell under 10 is `<10`.
- Reuse the folder `tmp_validation/a1_bureau_fill/` (new snippet file, new results files); commit and
  push; the user runs it in PROD for all four model_ids and commits the results.
- No change to the DE branch, pipelines, A1 code or permanent catalog files.

## Deliverable: `tmp_validation/a1_bureau_fill/summary_baseline.md`

1. **Verdict per age band** (1, 2–3, 4–6, 7–12, 13–24, 25+): does the data support "no alert = no
   change"? Yes / no / unclear, with the two or three numbers that decide it (disagreement vs age 0
   within CIF, comparator movement without an alert, stops on the raw series net of bank moves).
2. Tables for tests 1–4, four model_ids side by side where they fit.
3. The pull booking month (lag 0 vs −1) and what it changes.
4. How many first-run missed stops were hidden 0 alerts.
5. Anything the DE should fix for a fill to be safe (e.g. an alert-0 flag in the unified table).

Keep it short: verdict + key numbers per test. Then tell the user what can be deleted after the
results are pasted back.
