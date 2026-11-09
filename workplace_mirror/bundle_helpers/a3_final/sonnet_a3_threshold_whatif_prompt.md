# A3: grade thresholds what-if on the bundle 17 check output (prompt for the UAT Sonnet)

Send the block below to the UAT Sonnet. The user runs the snippet in PROD for cc_60_180 and rl_60_180 and
pastes `summary.md` back here. It reads only the check outputs that still exist (bundle 17's cleanup
has not run), so nothing is rebuilt.

Why: with no-response out of the grade, Moderate is 66% of both 60–180 models (Moderate from 1 point).
The user wants the distribution with Moderate from 2 points. High from 3 is the other calibration lever
(V4), so the grid covers both.

````text
Goal
Recompute the A3 state for four threshold settings from the bundle 17 check output, and show who moves.
Aggregates only. Change no pipeline code.

Input
crx_<p>_a3_check_payments (catalog entry from bundle 17; <p> = cc for cc_60_180, rl for rl_60_180):
one row per account for the latest month, the new A3 on the payments judge (the chosen one). Columns
used: a3_points_total, a3_refusal_flag, a3_state, a3_commitments_level, a3_dlq_payment_level,
a3_pre_dlq_payment_level.

The rule (as in a3_credibility/constants.py SCORECARD; reproduce it, do not import it)
- Unknown rows stay Unknown: keep every row with a3_state = 'payment_credibility_unknown' as it is.
- Otherwise the rung comes from a3_points_total: High if >= HIGH_FROM, Moderate if >= MODERATE_FROM,
  else Low.
- A refusal (a3_refusal_flag true) takes one rung off: High -> Moderate, Moderate -> Low, Low stays Low.
- Settings: M1H4 (today: Moderate from 1, High from 4), M2H4, M1H3, M2H3.
- Sanity check first: M1H4 must reproduce a3_state on every row; if it does not, stop and report the
  rows that differ.

Report, per model
1. a3_points_total distribution (value, n, %), split by a3_refusal_flag.
2. The state distribution under each of the four settings (n, %).
3. Crosstab M1H4 x M2H4 and M1H4 x M1H3 (n, %).
4. The rows that move Moderate -> Low under M2H4: n by (a3_commitments_level, a3_dlq_payment_level,
   a3_pre_dlq_payment_level), largest first. Same for the rows that move Moderate -> High under M1H3.

Rules
catalog.load only; model_id = catalog.load("params:model_id"), in every output file name; aggregates
only, no account / CIF ids; cells under 10 shown as "<10". Work in a new tracked folder
tmp_validation/a3_thresholds/ and commit only that.

Deliverables
1. Snippet + README in tmp_validation/a3_thresholds/, pushed from UAT.
2. The user runs it in PROD for cc_60_180 and rl_60_180 and commits results_<model_id>.md.
3. Back in UAT: summary.md, under 60 lines: the sanity check; the four distributions side by side for
   both models; the crosstabs; the top level combinations that move under M2H4 and M1H3, in plain
   words (e.g. "thin promises, some payment, no record: only one cycle of 100 AED or more").
````
