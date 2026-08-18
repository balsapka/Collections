# T23 — Within-cohort discrimination at 180+

**Goal.** Test whether the 180+ model's discrimination survives *inside* the
time-in-bucket cohorts, or whether it comes from separating <2y from >2y accounts.

**Why.** Positive rates differ sharply by time in bucket (~5% under two years, 1–2%
beyond). Time in bucket is trivially known, so a model spanning both cohorts can earn
apparent skill by learning "how long has this been sitting" — which tells collections
nothing they don't already know. The equivalent test across DPD buckets was run and
came back negative; this finer version has not been tested.

**Load.** `reference/domain_and_decisions.md §3`.

## Steps

1. Score the existing 180+ population with the current model.
2. Compute AUC, PR-AUC (against each cohort's own base rate) and capture@10%
   (accounts and AED) **within** the <2y cohort and **within** the >2y cohort
   separately.
3. Compare each against the pooled figures.

## Decision rule

- Within-cohort performance materially below pooled → the apparent skill was largely
  cohort membership. **Re-baseline every 180+ result within cohort**, and treat cohort
  as a segmentation boundary rather than a feature.
- Within-cohort ≈ pooled → the model genuinely discriminates inside each cohort; close
  this question as the DPD-bucket version was closed, and record it so it is not
  re-opened.

## Done when

Pooled vs within-cohort metrics are logged in `RESULTS.md` with an explicit
conclusion, and if re-baselining is required, that is flagged for the later retrain
work.
