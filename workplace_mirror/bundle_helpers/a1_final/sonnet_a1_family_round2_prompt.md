# A1 ability: evidence-family redesign, round 2 (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session, on branch `feature/persona_redesign_b14`.
It builds on round 1 in `tmp_validation/a1_family_redesign/` (snippet, `results_cc_60_180.md`,
`results_rl_60_180.md`, `summary.md`). Read those first and extend the round-1 snippet; do not
rebuild what it already does.

---

## Goal

Round 1 showed that **V1** (families F1 income, F2 inflow, F3 spend, F4 cross-product; Liquidity
dropped) fills High with customers who behave like High. Its order High > Moderate > Low holds and
it adds no dependence on A2, A4 or old A3. Before it goes to GRR, we need four things:

1. **A cleaner V1.** Take out the parts round 1 found redundant or unsupported, and close the gaps
   it found.
2. **How the four families fire.** How often, how much, in which combinations, and how stable they
   are from month to month.
3. **An audit of the flows F2 and F3 count.** Which transaction types actually made a family fire,
   and whether customers whose firing rests on a given type behave like real evidence. We want to
   find types we included wrongly.
4. **Stretch: an estimate for Unknown.** Can ability for today's Unknown customers be estimated
   from the customers we can score?

This is an experiment. Nothing in the pipeline changes.

## Decided (do not re-open)

Everything in round 1's "Decided" section still holds:
- windows end at the observation date (no pre-delinquency data);
- the anchor as today;
- CIF-level signals;
- distress as today;
- the axis boundaries (own card / loan payments never count);
- AECB live tables are out.

New from round 1:
- **Liquidity is dropped.** It is not a family any more.
- **The "≥ 2 dimensions" High gate is removed.** It cannot bind: each family scores at most 2, so
  4 points already needs two families.
- **P (profile) is never scored.** In this prompt it may only be a predictor in part D.
- **V3, V4 and V5 are closed.** The capacity shock is not a distress signal.

## Part A: the cleaned variants

Use the same scoring function as round 1. Score four variants. Each one changes a single thing from
the one before it:

| Variant | Change | Why |
|---|---|---|
| **R0** | round-1 V1 without Liquidity's reach and without the gate | reproduce: states must equal round-1 V1. Stop and report if they don't |
| **R1** | R0 with "some" = 0 points for F2, F3 and F4 | "some" did not lift in RL (worse than none for F2b and F3). Report F1 "weak" against "none" too; if it does not lift either, add **R1b** with weak = 0 |
| **R2** | R1 with F2 **excluding salary credits** (true F2a) | stops one salary credit scoring in both F1 and F2. `wm_pri_labelled_transactions` carries `salary_txn_flag` and `tran_id`. Find the join to `prm_casa_transactions`, and report its match rate. If no reliable key exists, say so and keep F2b |
| **R3** | R2 with **F4 including the customer's other cards** | round 1 said cards are still missing from F4. Another card of the same CIF that is current at the observation month counts as "another credit product"; use its minimum due / instalment for the "≥ 1 × anchor" test. Cards of the same contract (supplementaries) are not another product |

With "some" = 0, the rule reads: one strong family → Moderate, two → High, evidence without points
→ Low, no data → Unknown. Say if any row breaks that reading.

For R0–R3, report what round 1 reported:
- the state mix;
- transitions from V0;
- the reason column;
- separation (60_180, cohort Jan–May 2026, DPD-standardised, 95% intervals): the order, gaps, new
  High rows against V0 High and V0 Moderate;
- V1 within A2 reachability and within old A3;
- Cramér's V against A2, A4 and old A3;
- sensitivity on R3 (the round-1 knobs, minus the gate).

Also report, for R0 and R2, **High rows by the pair of strong families behind them**. The share of
R0 High resting only on F1 + F2b measures the double counting R2 removes.

## Part B: how the families fire

For R3's families (F2 = true F2a if R2 found it):

- **Firing rate.**
  - By family and level (strong / some / none / no data): for the latest month and for each cohort
    month.
  - Split by DPD band; by `rl_spine.loan_type` for RL; and by CASA holder vs no-CASA.
- **Intensity.**
  - For F2 and F3: the number of qualifying months in W (1..3, or 1..6 at 180+), and the
    distribution of the monthly amount ÷ anchor among firing rows (p10, p25, p50, p75, p90).
  - The same for F4's balance ÷ anchor.
- **Concentration.** Among strong F2 / F3 rows, the share where a single transaction makes up
  ≥ 50% of a qualifying month's amount. A strong level resting on one large credit is weaker
  evidence than regular flows.
- **Combinations.**
  - The number of strong families per row (0–4).
  - All 16 strong-family patterns with n (latest month) and the cohort outcomes (`cure_3`,
    `pay_any_3`, `roll_3`).
- **Stability.**
  - Each family's level at month t against t − 1, for the same account (transition matrix, cohort
    months).
  - R3's state transitions month to month.

## Part C: flow audit (were the right rows counted?)

For every **F2 or F3 row at strong or some level** in the cohort:

1. **What was counted.** AED and legs counted, broken down by:
   - `tran_type`, `reason_for_excluding` and the lane from `transaction_lane`;
   - channel / transaction code, and counterparty type where available: own account at another
     bank, third party, merchant, cash.

   Rank the types by counted AED, with their share. Do the same for the debit and credit types that
   **were excluded**, so the boundary can be judged from both sides.
2. **Suspect types.** Size each of these explicitly (n rows where it is ≥ 50% of the counted amount;
   share of counted AED):
   - Inflow:
     - loan disbursements or credit-card cash / balance transfers landing in CASA;
     - transfers from the customer's own accounts at other banks or under another CIF of theirs;
     - cash deposits;
     - refunds or reversals that escaped the lane rules;
     - round trips (a credit followed by a debit of the same amount ±5% to the same counterparty
       within 3 days).
   - Spend:
     - payments to other banks' cards or loans (ability is present, but the money goes to another
       creditor);
     - transfers to own accounts elsewhere;
     - remittances;
     - the sweep-matched debits round 1 dropped, at whatever residue is left.
   - Name any other type that looks wrong.
3. **Outcomes by dominant type.**
   - Classify each firing row by the type that makes up the most of its counted amount.
   - Give `cure_3` / `pay_any_3` / `roll_3` per dominant type against the family's `none` rows
     (DPD-standardised, n, intervals).
   - A type whose firers behave like `none` is a candidate for exclusion.
   - Re-score R3 without each candidate and report the rows that change.
4. **Narrations.**
   - Normalise narrations: upper case, digits and punctuation removed, first three words.
   - Report the top 30 stems of counted rows and the top 30 of excluded rows, **only stems shared
     by ≥ 50 distinct CIFs**. No other narration text leaves the cluster.

End with a proposed inclusion / exclusion list for F2 and F3, each entry with its evidence.

## Part D (stretch): estimating ability for Unknown

Only if parts A–C are done.
- **Training set:** rows R3 scores (not Unknown), latest month plus cohort months, 60_180.
- **Target:** the R3 state, or the number of strong families. Pick one and say why.
- **Predictors:** only data available for Unknown rows that obeys the window rule (observation
  month or earlier within W, or static as of the observation date):
  - product and `loan_type`, DPD band, anchor and its ratio to limit / EMI, months on book;
  - employer category and segment (P), product holding;
  - `bo_rr_aecb_metric` where linked;
  - any bureau field the income family already uses.
- **Not allowed:**
  - nationality, gender or age (fairness; GRR has not approved them);
  - any A2, A3 or A4 state or input, which would break orthogonality;
  - any outcome variable.
- **Model:** something GRR can read. Use logistic / ordinal regression or a shallow tree (depth
  ≤ 4), and a gradient-boosted model only as a ceiling for comparison.
- **Report:**
  - holdout discrimination on scored rows (AUC or ordinal accuracy) for the readable model and for
    the ceiling;
  - the top predictors;
  - the imputed state mix inside Unknown.
- **Selection bias.** Unknown customers mostly have no CASA. Compare their predictor distributions
  with the training set's, and report the share of Unknown rows outside the training support.
- **The real test:** within today's Unknown, does imputed High > Moderate > Low hold for `cure_3`,
  `pay_any_3` and `roll_3` (DPD-standardised, intervals)? If it does not, say plainly that the
  estimate is not usable.
- **Orthogonality:** Cramér's V of the imputed state against A2 and A4, inside Unknown.
- **Labelling:** keep the estimate as a separate label (`estimated_<state>`). Never merge it into the
  evidence-based states.

## 180+

- If round 1's 180+ results exist but are not committed, commit them.
- Otherwise, run round 1's parts 1–3 for `cc_180_plus` and `rl_180_plus` together with this round.
- At 180+, run parts A and B, plus part C's step 1 (no outcomes at 180+).

## Hard rules

- **Where the code lives.** The same tracked folder `tmp_validation/a1_family_redesign/`. Extend the
  round-1 snippet, or add `round2_snippet.py` next to it. Commit and push.
- **Data access.** Only `catalog.load(...)`. Use `model_id = catalog.load("params:model_id")` and
  put it in every output filename; never hardcode or override it. A source that is not in the
  catalog is reported as "not in catalog".
- **Reuse.** Reuse the engine functions and the round-1 family builders. Change only what a variant
  names.
- **Performance.**
  - Filter large sources to the base CIFs and to W before aggregating.
  - Read each source once.
  - Cache only the base.
  - Use literal partition filters.
  - If the run is too slow, run the four model_ids for parts A–B and the 60_180 ones for parts C–D,
    and say so.
- **What may leave the cluster.** Aggregates only. No customer rows or IDs, no model coefficients
  tied to individuals; cells under 10 shown as `<10`. Narrations only as the stems above.
- **No pipeline, catalog or registry changes.**

## Results and summary

- **Results.** `results_r2_<model_id>.md`, one per model_id, with sections A–D in the order above.
  The user runs it in PROD (switching `model_id` in `conf/dev/globals_dev.yml` and back) and commits
  the results.
- **Summary.** Back in UAT, write `summary_r2.md`, one section per model_id. Keep it short:
  - **A.** R0 reproduces (yes / no). A table of the state mix for R0–R3. One line per variant on the
    order, the High–Moderate gaps and Unknown. The double-counting share. The F2a match rate.
  - **B.** Firing rates per family (latest month), the top five strong-family patterns with
    outcomes, and family stability in one line each.
  - **C.** The top counted types per family, the suspect types with their size and their outcome
    against `none`, and the proposed inclusion / exclusion list.
  - **D.** Discrimination, the imputed mix and the within-Unknown order. The verdict: usable, not
    usable, or needs data.
  - **Verdict.** The variant to take to GRR, the F2 / F3 flow rules, and what still needs data.

The user pastes the summary back here.
