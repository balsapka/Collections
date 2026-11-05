# A1 ability: evidence-family redesign experiment (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session, on branch `feature/persona_redesign_b14`.
Bundle 14 is applied, so `crx_<p>_a1_ability` is the bundle 14 output. If the High what-if
(`tmp_validation/a1_high_whatif/`) results are committed, read them first: they already list the
sources, their coverage and the outcome definitions. Reuse them; do not measure anything twice.

---

## Goal

A1 does not work well on dry data today:
- The state is driven almost entirely by salary.
- Liquidity is dry. The bank sweeps CASA balances against overdue amounts, so a balance measures
  whether a sweep happened, not ability.
- High is nearly empty.
- The High what-if (internal Stable → High, liquidity from flows, a lower balance floor) barely moved
  the states.

We are testing a different design, one that keeps the points → High / Moderate / Low / Unknown
ladder. **Ability = evidence that the customer has money relative to what they owe, from independent
evidence families.** Each family scores 0 / 1 / 2 against the anchor. High needs agreement between
families, so it no longer depends on salary alone. Your job: build the families and score the
variants below on the real base, then measure coverage, separation and orthogonality. GRR can then
choose a design from evidence.

This is an experiment. Nothing in the pipeline changes.

## Decided (do not re-open)

- **Windows end at the observation date.** GRR wants signals derived only around the scoring date.
  - Use **no pre-delinquency windows** and no pre-T0 data for A1.
  - W = the observation month plus the months before it: 3 months at 60–180, 6 at 180+
    (`_common.window_months`). `MIN_MONTHS[w]` as in `a1_ability/classify.py`.
  - Observation dates are month ends.
- **Anchor as today.**
  - CC 60–180: the oldest non-zero overdue bucket on the observation-month snapshot.
  - RL: one EMI (`int_loan_master.installment_due_amount`).
  - 180+: no anchor, so flat floors.
  - `max(AED floor, k × anchor)` everywhere, so CC and RL stay comparable.
- **Customer signals at CIF level**: across all accounts of the `cif_id`.
- **Income stays a family**, computed exactly as `income_level` does today. Larger of internal salary
  and bureau salary, S12 level check, S14 alert carry.
- **Distress as today**: cheque returns, DDS and bureau bounces (S15).
- **Axis boundaries.** A1 is "has the money".
  - Payments, promises and cures towards *this* debt are A3.
  - Contact and location are A2.
  - Payments to our own card or loan (`card_payment` / `own_loan` lanes) are A3-adjacent. They never
    count as A1 evidence.
- **AECB live signals are out (X9).** The AECB file-level tables have no valid customer link (O65).
  - Only sources carrying our customer id may be used: the alert table and `alert_othprv_sub`,
    `bo_rr_aecb_metric` (`cust_num`, loan applicants only), and `feature_retail_loans` (RL).
  - Bureau data enters only through the income family (as today) and the distress set.

## The families to build

Each family gives a level per obs-base row: `strong` (2), `some` (1), `none` (0), or NULL if there
is no data for the customer.
- Every threshold is a named constant at the top of the snippet. Part 3 varies them.
- For every family, record which source and column you used.

**Step 0, before you build anything.**
- Confirm, for each source below:
  - its grain;
  - its date column and latest date;
  - that it reaches the base CIFs.
- `feat_cif_casa_activity_monthly` carries, per `(cif_id, month_end, lane)`: `legs`, `credit_aed`
  and `debit_aed`. Lanes are from `feat_cif_casa.py::transaction_lane`.
- Where a family needs a finer split than the lanes give (ATM vs other economic debits, salary
  credits inside `economic`), go back to `prm_casa_transactions`.
  - It is a primary, so it is allowed.
  - Filter it to the base CIFs and to W first.
  - Then group by `tran_type` / `reason_for_excluding` with the same rules as `transaction_lane`.
  - Say which types you put where.
- For `wm_*` tables: salary there is a monthly sum of salary-flagged credits, dated the 1st of the
  month and forward-filled (`bundle_helpers/a1_final/wm_salary_feature_logic.md` on the mirror side,
  summarised here). Salary credits can be told apart from other credits only if `prm_casa_transactions`
  carries the flag. Find out and say.

**F1 Income.** Today's `income_level`: stable 2, weak 1, none 0. Rebuild it with the engine function;
do not re-implement it.

**F2 Inflow capacity.** Money arriving in the customer's accounts in W that does not come from
themselves or from the bank.
- **Counts:** `economic` and `ambiguous` credits. Report both with and without `ambiguous`.
- **Does not count:** `wash` (own transfers), `group_internal`, `reversal`, `refund`, `fee_interest`,
  `card_payment`, `own_loan`.
- **Two variants:**
  - **F2a** excludes salary credits. It is independent of F1. Use it only if Step 0 finds the
    salary flag.
  - **F2b** includes salary credits.
- **Strong:** months in W with credits ≥ `max(AED 1,000, 1 × anchor)` ≥ `MIN_MONTHS[w]`.
- **Some:** any month in W with credits ≥ AED 1,000.

**F3 Spend capacity.** Money the customer chooses to spend in W.
- **Counts:**
  - `card_spend` (POS);
  - ATM cash withdrawals;
  - bill payments and outward transfers to third parties.
- **Does not count:** payments to our own card or loan, fees, sweeps and other bank-initiated debits,
  and reversals. **Report the debit types you could not place.**
- **Strong:** months with spend ≥ `max(AED 1,000, 1 × anchor)` ≥ `MIN_MONTHS[w]`.
- **Some:** any month ≥ AED 500.
- **Also report the sweep share.** Of the W debits, how many happen within 3 days of a credit and
  match its amount ±5%? Leave those out of F3 if Step 0 shows they are bank sweeps rather than
  customer spend. Say which you did and why.

**F4 Cross-product conduct (S12).** Live evidence of money from the customer's other relationships
with us at the observation month.
- **Find the sources:** product holding (`feat_product_holding`), the other card and loan spines and
  balances, term deposits, investments and WM balances. Read the catalog and the `wealth_management`
  repo to find them.
- **Strong**, either of:
  - deposits, investments or WM balances ≥ `max(AED 10,000, 3 × anchor)` at the month end of the
    observation month;
  - another credit product with us that is **current** (0 DPD) at the observation month and has a
    regular instalment of at least 1 × anchor.
- **Some:** any other product current at the observation month, or any deposit or investment holding
  > 0.
- **Same-account rule:** a sweepable balance on the same CASA as today's liquidity is not F4. Say how
  you kept the two apart.

**L Liquidity (today's).** Today's `liquidity_level`, kept only to compare against. V2 tests whether
it adds anything once F2 and F3 exist.

**P Profile (static, optional).** Employer category, customer segment and tenure, as static
attributes as of the observation date (latest known value, its age reported).
- It is **not** a window.
- It is reported for coverage and lift only, and is never scored in the main variants. GRR has not
  asked for it.

**Capacity shock (a candidate distress signal).** Inflow (F2b) in the observation month < 25% of the
average of the other months of W, given that the W average ≥ AED 1,000. It stays inside W, so it is
consistent with GRR's rule.

## The variants to score

Use one small scoring function in the snippet that mirrors the planned shared `Scorecard`:
- named dimensions with points by level;
- a total;
- an override with a mode: `demote` drops one rung, `cap` caps at Moderate;
- an Unknown gate: no dimension has data or evidence, and no override;
- an optional High gate: at least N dimensions with points > 0;
- a reason column: the dimension contributing the most points, or the override that fired.

**V0** (no gate). Today's rule: F1 + L, High 4, Moderate 2–3, distress = demote, Unknown as S11.
It must reproduce `crx_<p>_a1_ability` with 0 differing states. Stop and report if it doesn't.

| Variant | Dimensions | High rule | Distress | Notes |
|---|---|---|---|---|
| **V1 (main)** | F1, F2a, F3, F4 | ≥ 4 points from ≥ 2 dimensions | demote | Moderate 2–3, Low 1 or any evidence, Unknown none. Use F2b if Step 0 finds no salary flag, and say so. |
| V2 | V1 + L | same | demote | does balance add anything? |
| V3 | F1, F2a, F4 (no F3) | same | demote | in case spend is A3-adjacent or mostly sweeps |
| V4 | as V1 | same | cap at Moderate | |
| V5 | as V1 | same | demote | capacity shock added to distress |
| V6 | F1, F2b, F3, F4 | same | demote | F2 with salary inside, to show the double counting |

**Sensitivity on V1**, one change at a time:
- High from 3 and from 5;
- the "≥ 2 dimensions" gate off;
- strong multiple 0.5× and 2× anchor;
- floors AED 500 and AED 2,000;
- `MIN_MONTHS` one less.

Report the rows that change state in each.

## Outcomes and checks

**Outcomes, 60_180 only.** Cohort: observation months Jan–May 2026. Use `cure_3`, `pay_any_3` and
`roll_3` as defined in `tmp_validation/a1_payment_cure/`. If that folder is gone, define them from
`crx_<p>_dpd_sequences` and the payments, and state the definitions.

**Orthogonality.** Join on `(account_id, observation_date)`, using the latest month only:
- A2: `crx_<p>_a2_locatability`;
- A4: `crx_<p>_a4_deterioration`;
- A3: `crx_<p>_a3_payment_credibility`. This is the **old DE A3** and is being rebuilt, so label it
  "old A3, indicative".

## Hard rules

- **Where the code lives.** A Kedro notebook snippet in the temporary **tracked** folder
  `tmp_validation/a1_family_redesign/`. Commit and push it.
- **Data access.**
  - Data only via `catalog.load(...)`. No `spark.read`, no paths.
  - `model_id = catalog.load("params:model_id")`, and put it in every output filename. Never hardcode
    or override it.
  - A source not in the catalog is reported as "not in catalog", not read another way.
- **Reuse the engine.** Reuse `income_level`, `liquidity_level`, the distress builder,
  `_common.window_agg` / `pit_latest` and the obs base. Change only what a family or variant names.
  - If an input is not persisted, rebuild it with the pipeline's own node function from catalog
    inputs, and say which.
- **Performance.**
  - Filter every large source to the base CIFs and to W before any aggregation.
  - Read each source once and derive every family from that one read.
  - Cache only the base.
  - Use literal partition filters, so partitions are pruned.
  - If the four model_ids are too slow, run all four for parts 1–2 and the two 60_180 ones for
    part 3, and say so.
- **What may leave the cluster.** Aggregates only: no customer rows or IDs, and cells under 10 shown
  as `<10`.
- **No pipeline, catalog or registry changes.**

## Results to save (`results_<model_id>.md`, one per model_id)

**0. Step 0 table.** One row per source: dataset, the columns used, grain, latest date, the share of
base CIFs reached, and the family it feeds. Also the type mapping for F2 and F3, the unplaced debit
types with their volume, and whether the salary flag exists.

**1. V0 check.** States that differ from `crx_<p>_a1_ability`. Must be 0.

**2. Families, latest month** (`persona_end_date`'s month). For each family:
- level distribution: strong, some, none, no data (n, %);
- the same split within today's Unknown (by its reason), Low and Moderate;
- the same split for **no-CASA** customers (no CASA account with us).

Also:
- a **family overlap matrix**: the share of rows with ≥ 1 point in both families, for every pair
  (F1, F2a, F2b, F3, F4, L, P);
- the **sweep share** from F3;
- the **capacity-shock firing rate**.

**3. Variants, latest month.**
- The state distribution (n, %) per variant, with RL also split by product (`rl_spine.loan_type`).
- Transitions V0 → each variant (from × to, n).
- The reason-column distribution per variant.
- The Unknown share and its composition.
- Sensitivity on V1: the rows that change state for each knob.

**4. Separation (60_180).** For each variant:
- `cure_3`, `pay_any_3` and `roll_3` by state, with n and 95% intervals, standardised for DPD band;
- whether the order High > Moderate > Low holds for each outcome, and the gaps between states;
- for V1, the same **within each old-A3 state** and **within each A2 reachability state**, to check
  ability is not standing in for credibility or contact;
- the moved rows (V0 → V1, by from × to): their outcomes against the rows that stayed;
- the new High rows against today's High and today's Moderate.

**5. Family lift (60_180).** For each family and each level: outcomes against `none`, standardised
for DPD band, with n and intervals. Also within today's Unknown, and within no-CASA customers.

**6. Orthogonality, latest month.**
- Crosstabs of V1 against A2 and against A4.
- V1 against old A3, labelled indicative.
- Cramér's V for each, next to V0's.

**Run.** Run for `cc_60_180`, `rl_60_180`, `cc_180_plus` and `rl_180_plus`: switch `model_id` in
`conf/dev/globals_dev.yml`, and switch it back after. The user runs it in PROD and commits the result
files.

## Summary (back in UAT, after the results are committed)

Write `tmp_validation/a1_family_redesign/summary.md`, one section per model_id. Keep it short:
- **Step 0.** The sources used, the salary-flag answer, the unplaced debit volume, and the sweep share,
  one line each.
- **V0 check.** Pass or fail.
- **Families.** One table with coverage, reach into today's Unknown and into no-CASA, and the strongest
  overlaps.
- **Variants.** One table of states (n, %) per variant. The Unknown share against V0, and the size of
  High against V0.
- **Separation (60_180).** Per variant: whether the High > Moderate > Low order holds, and the gaps in
  `cure_3` / `pay_any_3`. Then V1 within old-A3 and A2 states, in one line each.
- **Sensitivity.** The knobs that move more than 5% of rows.
- **Verdict.** One line per family (keep, drop, or needs data) and one per variant (fills High with
  customers who behave like High, shrinks Unknown, stays orthogonal: yes or no). Finish with the
  variant you would take to GRR, and why.

The user pastes the summary back here.
