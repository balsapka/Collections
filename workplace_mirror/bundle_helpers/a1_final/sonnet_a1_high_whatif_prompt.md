# A1 ability — High what-if and ability signal inventory (UAT Sonnet prompt)

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
bureau-only Stable 14.4%). About 25% of CC rows and 13% of RL rows hold no CASA with us, so nothing
internal can lift them above Moderate.

Two parts, one snippet:
1. **Scenarios:** size three rule changes for GRR by rescoring the real A1 output (no pipeline change):
   how many rows move, and whether the rows that move to High pay and cure like High.
2. **Signal inventory:** for every other data point that could show ability, how many customers it
   reaches, how fresh it is, and whether it separates better from worse payers. We use this to design
   the alternatives, especially for the no-CASA and dormant customers.

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
- Axis boundaries: payment behaviour towards us (payments, promises, cures) is **A3 credibility**;
  contact and location are **A2**. A1 is about whether the customer has the money. In the inventory,
  report A3-adjacent signals but label them.

## Hard rules

- Kedro notebook snippet in a temporary **tracked** folder `tmp_validation/a1_high_whatif/`; commit
  and push it. Data via `catalog.load(...)` only; `model_id = catalog.load("params:model_id")` in every
  output filename, never hardcoded or overridden. No `spark.read`, no paths. A source that is not in
  the catalog is listed as "not in catalog", not read another way.
- Reuse the engine functions (`income_level`, `liquidity_level`, `build_a1_ability` or the pieces they
  call) and change only what a scenario names. If an input is not persisted, rebuild it with the
  pipeline's own node function from catalog inputs and say which.
- **Bureau link:** the AECB file-level tables (`subj_cntrct_hist`, `subj_cntrct_dtl`,
  `subj_con_tot_smry`, `subj_crdt_score`, `sub_sal_cr_hist`, …) have **no valid link to our customers**
  (only through `subj_cntrct_link`, which reaches under 1% and mixes co-parties; O65). Do not join them
  to customers. Use only sources that carry our customer id: the alert table and
  `alert_othprv_sub` (via `PRVDR_SUBJ_NUM` = `cif_id`, check it for `alert_othprv_sub`),
  `bo_rr_aecb_metric` (`cust_num`, loan applicants only), and for RL `feature_retail_loans`.
- Filter every large source to the base CIFs before any aggregation. Aggregates only: no customer rows
  or IDs; cells under 10 shown as `<10`.
- No pipeline, catalog or registry changes.

## Part 1 — scenarios

| Scenario | Change (everything else as today) |
|---|---|
| S0 | none; must reproduce `crx_<p>_a1_ability` (0 states differ) |
| A | Income Stable from **internal salary alone** (the same S12 rule with the bureau salary set to 0) and no distress → High, whatever the liquidity |
| B | Liquidity from **flows** instead of balances: Adequate = credits in the customer lanes ≥ max(AED 1,000, 1 × anchor) in `MIN_MONTHS[w]` months of W; Weak = any month ≥ AED 1,000. External card payment rule kept |
| B′ | B with salary credits left out of the credits (the legs WM flags as salary, if they can be matched; say how, or skip B′ and say why) |
| C | Balance rule kept, floor = max(AED 1,000, 1 × anchor) instead of max(AED 3,000, 1 × anchor) |
| A+B | both |

The bureau salary keeps its current carry in every scenario.

## Part 2 — ability signal inventory

Find the sources yourself (this repo's catalog, `wealth_management`, `retail.feature_space`). Below are
the candidates we can think of; add others you find, and say where each comes from (dataset + column).

**Internal, now (in W):**
- Credits by type in the customer lanes (inward remittance, internal transfer from others, cash
  deposit, clearing) and the debit side (POS spend, ATM cash, outward transfers, bill payments): monthly
  amounts relative to the anchor.
- Debit card spend (Way4 / POS on CASA), and for CC the card's own spend before it was blocked.
- Large one-off credits (≥ 3 × anchor or ≥ AED 10,000): EOSB, settlements, lump sums.
- Holdings outside the 49 CASA codes: term deposits, investment, WM balances on the 207 codes (are
  they swept or liened too?).
- Other products with us and how they run: mortgage, other loans, other cards (label A3-adjacent if it
  is payment behaviour).

**Internal, before delinquency (stale by design, but before any sweep):**
- CASA balance, credits and debit spend in the 3–6 months before collections entry (the entry month
  as the A4 engine dates it, point-in-time).
- Internal salary at entry: last amount, months since the last salary, amount ÷ anchor.
- CC: limit, utilisation and spend level before entry.

**Origination and customer data (often stale; report the age):**
- Declared income, DBR / DTI at application, salary-transfer loan flag (RL), employer category
  (government / private / self-employed), customer segment (priority / private / mass), tenure with
  the bank, age, residency / nationality type.

**Bureau (linkable sources only, often stale):**
- Every alert type on the alert table and `alert_othprv_sub`: list the types with their counts on the
  base CIFs (salary, new facility elsewhere, delinquency elsewhere, closure, enquiry, …), and which
  look like ability (new credit granted elsewhere, current elsewhere) or distress (delinquency, court).
- `bo_rr_aecb_metric`: which fields it carries besides the salary (exposure, other-bank obligations,
  score), their coverage and pull age.
- RL `feature_retail_loans`: fields beyond the salary.

**For each signal, measure on the latest month's base (all four model_ids):**
1. Coverage: share of base CIFs with any value; with a value within 3 / 6 / 12 / 24 months
   (freshness); median age in months.
2. Reach into the groups that matter: coverage within today's Unknown (`no_casa`, `dormant_casa`), Low
   and Moderate.
3. Overlap: how many of its customers are already Stable income or Adequate liquidity.
4. Lift (60_180 only, cohort Jan–May 2026, the outcomes of part 1): `cure_3`, `pay_any_3`, `roll_3`
   for the signal present vs absent (or by tercile for amounts), standardised for DPD band, with n
   and 95% intervals; and the same within today's Unknown.

Skip a signal and say why when it covers under 1% of the base or cannot be linked.

## Results to save (`results_<model_id>.md`, one per model_id)

1. **S0 check:** states that differ from `crx_<p>_a1_ability` (must be 0).
2. **Scenarios, latest month** (`persona_end_date`'s month): state distribution (n, %) per scenario;
   RL also by product (`rl_spine.loan_type`); liquidity level per scenario; moves S0 → each scenario
   (from × to, n).
3. **Scenario outcomes (60_180 only):** for Jan–May 2026, `cure_3`, `roll_3`, `pay_any_3` defined as in
   the payment / cure validation (`tmp_validation/a1_payment_cure/` if still there; otherwise define
   them from `crx_<p>_dpd_sequences` and the payments and state the definitions): rate by state per
   scenario, and for the rows that **move** (by from × to state), with n, standardised for DPD band.
4. **Sweep visibility (latest month's CIFs, W):** of the customer-lane credits, the share followed
   within 3 days by a debit on the same CIF in each lane (own_loan, card_payment, ambiguous, other);
   month-end balance as a share of that month's credits (p25 / p50 / p75).
5. **Signal inventory:** one row per signal: source (dataset.column), label (ability / A3-adjacent /
   distress), coverage, fresh within 3 / 6 / 12 / 24 m, median age, coverage in Unknown / Low /
   Moderate, overlap with Stable / Adequate, lift (60_180), and the skipped signals with the reason.
6. **Source freshness:** for every source read, the latest date overall and the share of base CIFs
   whose latest value is in W.

Run for `cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus` (switch `model_id` in
`conf/dev/globals_dev.yml`, switch back after). The user runs it in PROD and commits the result files.
If a full run is too slow, run part 1 for all four and part 2 for the two 60_180 first, and say so.

## Summary (back in UAT, after the results are committed)

Write `tmp_validation/a1_high_whatif/summary.md`, one section per model_id:
- S0 check: pass / fail.
- States per scenario (n, %) in one table, and liquidity Adequate share per scenario.
- The biggest moves per scenario, with n.
- 60_180: `cure_3` / `pay_any_3` of the new High rows in A, B and A+B against today's High and today's
  Moderate, with n and intervals.
- Sweep visibility in two lines.
- Signal inventory, ranked: the signals with coverage ≥ 10% and a lift whose interval excludes 0,
  each with coverage, freshness, reach into Unknown and lift; then the ones that reach the no-CASA
  group; then the rest in one line each.
- One-line verdict per scenario (does it fill High with customers who behave like High?) and per
  top signal (worth a rule, worth a data request, or not useful).
The user pastes the summary back here.
