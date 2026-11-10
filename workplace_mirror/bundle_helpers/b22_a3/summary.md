**What this bundle does.** Narrows A3 payment credibility's Unknown state to rows with no delinquency episode. Apply after bundle 20 (and its cleanup); it touches only A3 files, so its order against bundle 21 doesn't matter.

**What changes in the logic** (spec `specs/A3_credibility_spec.md`, D-A3-27):
- No payment while delinquent (Dimension B `none`) is evidence that scores 0 points. It is no longer a "silent" level.
- So a row with an observed episode and no points in any dimension (thin promises, no payment, no record before delinquency) is **Low**, not Unknown. These are mostly early payment defaults.
- Unknown stays only for rows with no episode anchor (`a3_unknown_reason = 'no_episode'`); the `no_evidence` reason no longer occurs.
- High and Moderate don't move; nothing else in the scoring changes.

**Code:** `a3_credibility/constants.py` (Dimension B has no silent level) and `a3_credibility/classify.py` (the `no_evidence` branch and docstring). No new datasets, no catalog or registry change, no temporary check.
