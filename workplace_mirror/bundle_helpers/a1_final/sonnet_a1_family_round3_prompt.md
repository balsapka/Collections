# A1 ability: evidence-family redesign, round 3 (UAT Sonnet prompt)

Paste everything below the line into the UAT Sonnet session, on branch `feature/persona_redesign_b14`.
It builds on rounds 1–2 in `tmp_validation/a1_family_redesign/` (snippets, `results_*`,
`results_r2_*`, `summary.md`). Read them first and reuse their family builders, outcomes and scoring
function.

---

## Goal

Rounds 1–2 settled the rule (**R3**):
- High = 2+ strong families;
- Moderate = 1 strong family;
- Low = evidence but none strong;
- Unknown = no evidence;
- distress demotes one rung.

Families: F1 income, F2 inflow without salary credits, F3 spend, F4 cross-product including the
customer's other cards. R3 separates outcomes well.

Two things are still open, and this round is about them:

1. **Which raw transactions may count as inflow (F2) and spend (F3).** Filtering
   `prm_casa_transactions` is hard, and round 2 shows we are getting it wrong:
   - The largest counted F2 narration stems are `CHQ RTN INSUFFICIENT` and `CHQ NO INSUFFICIENT`
     (CC 233M AED, RL 335M AED). They look like the credits that reverse bounced cheques: distress,
     not money arriving.
   - Ambiguous `MISCELLANEOUS` credits are 40% (CC) and 84% (RL) of counted F2 AED. Rows whose
     inflow is mostly these credits do worse than rows with no inflow.
   - Mirrored credits (a debit of the same amount within 3 days) are 46% / 89% of counted F2 AED.
   - 78% / 84% of strong F2 rows rest on one leg.
   - Yet leaving the ambiguous credits out changes only 19 / 13 states. That does not add up.

   This round is **a careful assessment of every flow type, not another filter.** The deliverable is
   an evidence-backed flow dictionary and the F2 / F3 definitions built from it.
2. **Saying something about Unknown** (CC 52–54%, RL 34–44% of rows). Round 2's estimate learned the
   R3 state from static features on scored rows. It did not order outcomes inside Unknown, and in RL
   it did not discriminate at all. This round tries harder, in a principled way:
   - first, direct evidence that reaches Unknown customers;
   - then a better-designed inference, with acceptance criteria fixed before any model is fit.

   A clear "the available data cannot place these customers" is an acceptable answer, as long as it
   is demonstrated.

This is an experiment. Nothing in the pipeline changes.

## Decided (do not re-open)

- Everything in rounds 1–2's "Decided" sections still holds:
  - windows end at the observation date;
  - the anchor as today;
  - CIF-level signals;
  - distress as today;
  - own card / own loan payments never count (A3);
  - AECB file-level tables are out (no customer link, O65).
- **Rule R3 stands**: "some" = 0 points, F1 weak = 0 points (still evidence for Low), true F2a,
  Liquidity dropped.
- **The flow principle (new): an inclusion list, not an exclusion list.** A flow type counts for F2
  or F3 only when its meaning is **positively established** with evidence. Everything else is
  "unplaced" and does not count. When in doubt, leave it out: round 2 showed that dropping doubtful
  credits costs almost no states.
- **Context from the code** (`nodes/features/casa/feat_cif_casa.py::transaction_lane`):
  - The `signal` lane catches only `tran_type = CHEQUE RETURNS` or reason
    `DDS Rejects/Reversal` / `CHEQUE RETURNS`. The `CHQ RTN …` narrations sit under `MISCELLANEOUS`,
    so they land in `ambiguous`.
  - `economic` includes `INWARD CLEARING` / `OUTWARD CLEARING`. A presented cheque that later
    bounces may therefore be counted as spend (F3) or inflow (F2), with its reversal in `ambiguous`.
  - Today's A1 `casa_active` (`CUSTOMER_LANES`) does not use `ambiguous`, so the live Unknown gate is
    probably unaffected. Verify it in part A.
- **An estimate for Unknown is never merged into the evidence-based states.** If anything is usable,
  it is a separate column (`a1_estimate` + confidence), and GRR decides whether to use it.

## Part A: flow assessment (careful, leg level)

### A1. Reuse existing classifications before inventing rules

Inventory the transaction labels others already maintain, and compare them with our lanes on the same
legs:
- `wm_pri_labelled_transactions`: all its label / category columns, not only `salary_txn_flag`. The
  join on `cif_id, tran_id, tran_date` is reliable (93.5% / 96.5%).
- The `retail.feature_space` and `wealth_management` repos (cloned beside the branch). Look for
  income, spend, transfer and cheque classifications.
- The WM monthly inflow / outflow features. Known: they carry admin records such as fees.

For each labelled source, report:
- its coverage of our legs;
- the crosstab of its labels against our lane;
- where they disagree, by AED.

Prefer a curated label to our own rule wherever it is reliable, and say where you did.

### A2. The flow dictionary

Build one table of every distinct combination of:
- direction (`tran_dc`);
- `tran_type`;
- `reason_for_excluding`;
- `tran_particular_code`;
- the WM label (if any);
- today's lane.

Cover all legs of base CIFs in the cohort windows. Keep every combination with ≥ 50 distinct CIFs;
fold the rest into "other" and report its size. For each combination report:
- legs, distinct CIFs and AED;
- the amount distribution (p50, p90, p99), and the share of round amounts (multiples of 1,000);
- the top normalised narration stems (upper case, digits and punctuation removed, first three words,
  only stems shared by ≥ 50 CIFs);
- **pairing behaviour**: the share of legs mirrored by an opposite leg of the same amount ±1% within
  0–3 days on any account of the CIF, broken down by the mirror's own type. This tells a bounce, a
  reversal, a sweep and an own transfer apart;
- **event alignment**: the share of legs on the same day as, or within 3 days of:
  - an internal cheque return or DDS event in the distress sources (match on `cif_id`, date,
    amount);
  - a card or loan due date / overdue sweep;
  - a loan disbursement;
- **regularity**: the share of CIFs where the combination recurs in 3+ consecutive months at a
  similar amount (±20%), the pattern of salary, rent and support payments;
- **outcome lift** (60_180 cohort, DPD-standardised): `cure_3`, `pay_any_3` and `roll_3` for rows
  where the combination is ≥ 50% of the row's W credits (or debits), against rows with no credits
  (or debits).

### A3. Classify each combination

Classify each combination into one of the following, with the evidence for it:

| Class | Meaning | F2 / F3 |
|---|---|---|
| `third_party_in` | money from another person or employer (incl. non-flagged salary-like credits) | F2 |
| `cash_in` | cash the customer deposits | F2 candidate: decide from the evidence |
| `own_transfer` | between the customer's own accounts, here or elsewhere | neither |
| `bank_initiated` | sweeps, fees, interest, disbursements, recoveries | neither |
| `reversal_return` | reversals, returned cheques / DDS, refunds, and the presentment they undo | neither (distress if it is a bounce) |
| `chosen_spend` | POS, ATM, bills, transfers to others | F3 |
| `debt_elsewhere` | payments to other banks' cards / loans | F3 candidate: decide and say why |
| `debt_to_us` | own card / own loan | neither (A3) |
| `unplaced` | meaning not established | neither |

**The cheque question first.** At leg level, trace a sample of CIFs (aggregates only) through
presentment → return:
- Are the `CHQ RTN …` / `CHQ NO …` legs credits or debits?
- What do they mirror?
- Do they match the internal cheque-return events?
- Which lanes do both legs fall in?

Answer this and size it before anything else, in both products.

### A4. Pairs that cancel

Where a leg and its mirror are both meaningless as evidence (a bounce, a reversal, a sweep and its
credit, a round trip through the same counterparty), **net the pair out**: drop both legs. Do not
drop a whole type.

Report how much of round 2's counted F2 / F3 AED this removes, per class.

### A5. Rebuild F2 and F3 from the dictionary, then score

| Variant | Change from R3 |
|---|---|
| **R4** | F2 / F3 count only their inclusion classes, after netting the pairs (A4) |
| R4-cash | R4 with `cash_in` out of F2 |
| R4-debt | R4 with `debt_elsewhere` out of F3 |
| R4-reg | R4 where F2 strong also needs ≥ 2 legs in each qualifying month, or a regular credit (A2's regularity test). This is for the "rests on one leg" problem; report it even if it cuts F2 sharply |
| R4-F4 | R4 where holding another product / card without the strong condition is **not** evidence. Round 2 showed those Unknown → Low rows behave like Unknown |

For each variant, report:
- the state mix (latest month), and RL by `loan_type`;
- transitions from R3;
- separation as in round 2 (order, gaps with intervals, new / moved rows);
- the share of strong F2 / F3 rows resting on one leg.

### A6. Effect on today's A1

Using the dictionary, check whether any class that is not evidence (bounce, reversal, bank-initiated,
`unplaced`) is inside today's `CUSTOMER_LANES`:
- How many `crx_<p>_a1_ability` rows leave Unknown only because of such legs (latest month)?
- Which lane rules in `transaction_lane` would you change? Give each one with its evidence and the
  rows it moves.

This is a proposal only; no code change.

## Part B: saying something about Unknown

### B0. Describe Unknown before modelling it

Split today's R3 Unknown into data situations, all observable at the observation date:
- no CASA account with us;
- CASA held but no leg in W;
- CASA legs only in unplaced / bank-initiated classes;
- other.

Split each further by product, DPD band and `loan_type`. Give the outcomes for each sub-group.

If the sub-groups already order outcomes, that is the cheapest thing we can say about Unknown: a
**reason code**, not a state.

### B1. Direct evidence that reaches Unknown

Look for evidence from sources that carry our customer id and that Unknown customers have, and size
each one inside Unknown:
- **External conduct**: whether the customer is current with other lenders at the observation month,
  from `alert_othprv_sub`, the alert table and `bo_rr_aecb_metric` (`cust_num`, loan applicants).
  Check each source's grain, freshness and link rate first, as round 1's step 0 did.
- **Our other relationships** missed so far: term deposits, investments, WM balances on other CIF
  links, joint accounts.
- **Card-side evidence for CC** (no CASA needed): spending on *other* cards of the CIF in W. This is
  not the scored card, and not payments.

For each candidate, report:
- its reach into Unknown (n, % with data, % at a strong-like level);
- outcome lift inside Unknown, against Unknown without it;
- Cramér's V against A2 and A4.

A candidate that reaches Unknown and lifts there is a family proposal (**F5**), to be scored as
**R5** = R4 + F5.

### B2. Inference, if direct evidence leaves a large Unknown

Round 2 failed for identifiable reasons, and the design must answer each:
- **Covariate shift**: Unknown differs from scored rows; employer unknown is 82.5% against 71.2%.
- **A target that exists only where data exists**: the R3 state is defined by data availability.
- **Thin features**: RL months on book, EMI and loan amount were never read.

**Fix the acceptance criteria before fitting anything, and keep them.** An estimate is usable only if
**all** of these hold:
1. Inside today's Unknown (60_180 cohort, DPD-standardised), the estimated groups order `pay_any_3`
   and `roll_3`, with the top–bottom gap significant (95% interval excluding 0). `cure_3` must not
   reverse.
2. It adds separation beyond DPD band + product + `loan_type`: a likelihood-ratio test, or ΔAUC with
   a bootstrap interval, on `pay_any_3` inside Unknown.
3. Cramér's V against A4 and A2 inside Unknown is no higher than R3's on scored rows.
4. It holds on the latest month **and** on at least two separate cohort months (temporal holdout:
   train on Jan–Mar, test on Apr–May).
5. It covers ≥ 30% of Unknown after abstention.

Explore these approaches. Pick the features and models; justify the choices.

- **Features (allowed).** Only data at or before the observation date, within W or static as of that
  date:
  - product, `loan_type`, DPD band, anchor, limit / original loan amount, EMI;
  - anchor ÷ limit and EMI ÷ loan amount; months on book;
  - employer category, segment, product holding;
  - B1's sources; B0's data situation.

  Static **application-time affordability** (declared income, debt-burden ratio at origination) is
  pre-delinquency data. GRR's window rule may exclude it, so **report every model with and without
  it**, and label the "with" results "needs GRR approval".
- **Features (not allowed):**
  - nationality, gender, age;
  - any A2, A3 or A4 state or input;
  - payments to this debt;
  - any outcome.
- **Shift diagnosis first.** Fit a classifier for Unknown vs scored ("adversarial validation"). Report
  its AUC and top features, and the share of Unknown rows inside the scored rows' support (propensity
  overlap).
- **Shift-aware learning.** Retrain the round-2 target with importance weights from that
  classifier's density ratio. Report whether the within-Unknown order improves.
- **A better target.** Instead of the R3 state, predict each **strong family separately** (F1, F2,
  F3, F4 strong: four binary models), each trained where that family has data. Combine them into an
  expected number of strong families. This avoids learning "has data" as the target.
- **Models.** Use regularised logistic / ordinal regression as the readable baseline. Then use
  monotone-constrained gradient boosting (LightGBM / XGBoost, or sklearn `HistGradientBoosting`,
  whichever is installed), and an explainable boosting machine (`interpret`) if available. Use
  nearest-neighbour / similarity estimates (state mix of the k nearest scored rows, abstaining when
  the neighbours are far) as a non-parametric check.
- **Uncertainty and abstention.** Use **weighted conformal prediction** (weights from the shift
  classifier) for prediction sets at 80% / 90% coverage. A row gets an estimate only when its set is a
  single state, or a pair of adjacent states collapsed to "not Low" / "not High". Otherwise it stays
  Unknown. Report the coverage achieved.
- **Semi-supervised check (optional).** Self-training or label propagation over scored + Unknown rows.
  Report it only if it beats the supervised route on criterion 1.
- **Ceiling diagnostic, never shipped.** Fit the best model that predicts `pay_any_3` directly inside
  Unknown from the allowed features, cross-validated. If even this barely beats DPD band + product
  (ΔAUC < 0.03), the available data carries no ability signal for these customers. Say so as the
  conclusion: the gap needs new data (GRR's bureau salary feed), not a cleverer model. This model is a
  risk model, so it must never become the A1 estimate.

**Report for B2**, per approach and per product:
- discrimination on scored holdout and on the temporal holdout;
- the five acceptance criteria (pass / fail, with numbers);
- coverage after abstention;
- the top features;
- the estimated mix inside Unknown.

Finish with one verdict line: **usable** (which approach), **not usable**, or **needs data** (which
data).

## 180+

- If round 1 or 2's 180+ results exist uncommitted, commit them.
- Run part A (dictionary, R4 variants without outcomes), B0 and B1's reach for `cc_180_plus` and
  `rl_180_plus`. At 180+, A1 has no anchor and Unknown is about 87–90%, so B1 matters most there.
- B2 only if B1 leaves 180+ unresolved and 60_180 found a usable approach.

## Hard rules

- **Where the code lives.** The tracked folder `tmp_validation/a1_family_redesign/`. Add
  `round3_snippet.py` (and helpers) next to the round-1/2 snippets. Commit and push.
- **Data access.**
  - Only `catalog.load(...)`.
  - `model_id = catalog.load("params:model_id")`, in every output filename. Never hardcode or
    override it.
  - A source that is not in the catalog is reported as "not in catalog".
- **Reuse** the engine functions and the round-1/2 builders. Change only what a variant names.
- **Performance.**
  - Filter large sources to the base CIFs and W before aggregating; read each source once; cache only
    the base; use literal partition filters.
  - Pairing within 3 days: use a self-join on `(cif_id, amount bucket)` with a date range, not a
    cross join.
  - Model training may use pandas on the obs-base rows (about 100k CC, 20k RL).
- **What may leave the cluster.** Aggregates only:
  - no customer rows, IDs, account numbers or per-customer predictions;
  - cells under 10 shown as `<10`;
  - narrations only as stems shared by ≥ 50 CIFs;
  - model outputs as metrics, coefficients or feature importances only.
- **No pipeline, catalog or registry changes.**

## Results and summary

- **Results.**
  - `results_r3_<model_id>.md`, one per model_id, sections A1–A6 and B0–B2.
  - Also `flow_dictionary_<model_id>.md`: the A2 table with each combination's class and the evidence
    behind it.
  - The user runs it in PROD, switching `model_id` in `conf/dev/globals_dev.yml` and back, and
    commits the results.
- **Summary.** Back in UAT, write a **new file** `summary_r3.md`, one section per model_id. Leave
  `summary.md` (rounds 1–2) unchanged. Keep it short:
  - **Cheques.** What `CHQ RTN` / `CHQ NO` legs are, how much was counted in round 2, and in which
    family.
  - **Labels.** Which existing classifications were reusable.
  - **Dictionary.** The F2 and F3 inclusion classes, each with its main evidence in one line, and what
    is unplaced (AED share).
  - **Variants.** A table of the R4 variants' states, then the order and gaps, and the one-leg share.
  - **Today's A1.** Rows wrongly out of Unknown, and the proposed lane changes.
  - **Unknown.** B0's sub-groups and outcomes, and B1's candidates with their reach and lift.
  - **Inference.** B2's acceptance table per approach; the ceiling diagnostic; the verdict.
  - **Verdict.** The F2 / F3 definitions and the variant to take to GRR. What we can say about
    Unknown (reason code, F5, estimate, or nothing without new data). The decisions GRR must make.

The user pastes the summary back here.
