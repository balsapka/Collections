# A1 ability — High what-if: liquidity after the sweep (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session (branch `feature/persona_redesign_b14`,
bundle 14 applied and its step 8 run, so `crx_<p>_a1_ability` is the bundle 14 output).

---

## Goal

High is almost empty: CC 45 of 19,292 rows, RL 11 of 3,985 at 61–180 (2026-08-31). It needs income
Stable (2 points) **and** liquidity Adequate (2 points), and liquidity is Adequate for only 1.0% (CC) /
1.4% (RL). GRR confirmed that the bank can and does **sweep CASA balances against overdue amounts**, so
a delinquent customer cannot keep a balance with us: the balance rule measures whether a sweep has
happened, not the customer's ability. Money flowing through the account survives a sweep. Customers
with a Stable *internal* salary already behave like High (cure within 3 months 33.0% vs High 33.6%;
bureau-only Stable 14.4%).

Size three rule changes for GRR by rescoring the real A1 output, with no change to the pipeline: how
many rows move, and whether the rows that move to High pay and cure like High.

## How A1 scores today (decided; only the scenarios below change it)

- `a1_ability/classify.py`: points = income (stable 2 / weak 1) + liquidity (adequate 2 / weak 1);
  High = 4 points and no distress; Moderate 2–3, or 4 with distress; Low otherwise; Unknown = 0
  points, no distress, no customer CASA transaction (S11). Window W = 3 months at 60–180, 6 at 180+;
  `MIN_MONTHS[w]` months needed.
- `liquidity_level`: Adequate = CASA average balance ≥ max(AED 3,000, 1 × anchor) in `MIN_MONTHS[w]`
  months and not more than 50% below the prior window, **or** an external card payment
  ≥ max(AED 500, 1 × anchor); Weak = any month ≥ AED 1,000 or such a payment. Anchor: CC 60–180 the
  oldest overdue bucket, RL one EMI, 180+ none (flat floors).
- `income_level`: monthly income = the larger of internal salary and bureau salary (S12, level check).
- CASA legs: `feat_cif_casa_activity_monthly` (CASA accounts only since bundle 14), lanes from
  `feat_cif_casa.py::transaction_lane`; customer lanes = economic, card_spend, card_payment.

## Scenarios

| Scenario | Change (everything else as today) |
|---|---|
| S0 | none; must reproduce `crx_<p>_a1_ability` (0 states differ) |
| A | Income Stable from **internal salary alone** (the same S12 rule with the bureau salary set to 0) and no distress → High, whatever the liquidity |
| B | Liquidity from **flows** instead of balances: Adequate = credits in the customer lanes ≥ max(AED 1,000, 1 × anchor) in `MIN_MONTHS[w]` months of W; Weak = any month ≥ AED 1,000. External card payment rule kept |
| B′ | B with salary credits left out of the credits (the legs WM flags as salary, if they can be matched; say how, or skip B′ and say why) |
| C | Balance rule kept, floor = max(AED 1,000, 1 × anchor) instead of max(AED 3,000, 1 × anchor) |
| A+B | both |

The bureau salary keeps its current carry in every scenario.

## Hard rules

- Kedro notebook snippet in a temporary **tracked** folder `tmp_validation/a1_high_whatif/`; commit
  and push it. Data via `catalog.load(...)` only; `model_id = catalog.load("params:model_id")` in every
  output filename, never hardcoded or overridden. No `spark.read`, no paths.
- Reuse the engine functions (`income_level`, `liquidity_level`, `build_a1_ability` or the pieces they
  call) and change only what a scenario names. If an input is not persisted, rebuild it with the
  pipeline's own node function from catalog inputs and say which.
- Aggregates only: no customer rows or IDs; cells under 10 shown as `<10`.
- No pipeline, catalog or registry changes.

## Results to save (`results_<model_id>.md`, one per model_id)

1. **S0 check:** states that differ from `crx_<p>_a1_ability` (must be 0).
2. **Latest month** (`persona_end_date`'s month): state distribution (n, %) per scenario; RL also by
   product (`rl_spine.loan_type`); liquidity level (adequate / weak / none) per scenario; moves S0 →
   each scenario (from × to, n).
3. **Outcomes (60_180 only):** for the cohort months Jan–May 2026, use the 3-month outcomes `cure_3`,
   `roll_3`, `pay_any_3` defined as in the payment / cure validation (`tmp_validation/a1_payment_cure/`
   if it is still there; otherwise define them, from `crx_<p>_dpd_sequences` and the payments, and state
   the definitions). Report: rate by state per scenario, and separately for the rows that **move** in
   each scenario (by from × to state), with n. Standardise for DPD band as that validation did.
4. **Sweep visibility (latest month's CIFs, W):** of the customer-lane credits, the share followed
   within 3 days by a debit on the same CIF in each lane (own_loan, card_payment, ambiguous, other);
   and the month-end balance as a share of that month's credits (p25 / p50 / p75). This shows whether
   money passes through the account and then leaves.

Run for `cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus` (switch `model_id` in
`conf/dev/globals_dev.yml`, switch back after). The user runs it in PROD and commits the result files.

## Summary (back in UAT, after the results are committed)

Write `tmp_validation/a1_high_whatif/summary.md`, one section per model_id:
- S0 check: pass / fail.
- States per scenario (n, %) in one table, and liquidity Adequate share per scenario.
- The biggest moves per scenario, with n.
- 60_180: `cure_3` / `pay_any_3` of the new High rows in A, B and A+B against today's High and today's
  Moderate, with n and intervals.
- Sweep visibility in two lines.
- One-line verdict per scenario: does it fill High with customers who behave like High?
The user pastes the summary back here.
