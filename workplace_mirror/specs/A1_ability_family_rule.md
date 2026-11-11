# A1 ability: the evidence-family rule

This is the rule that replaces today's income + liquidity ladder (`A1_ability_spec.md`, S1–S16) once
GRR agrees. It comes from the family-redesign rounds 1–3 (`bundle_helpers/a1_final/
family_redesign_results_60_180.md`, `family_redesign_results_r3_60_180.md`; rule R4 there), plus the
CASA balance folded into Money in (user, 2026-11-10; not run as a separate check).

Built as **bundle 21** (`bundles/21_a1_evidence_family_rule.md`, stage branch
`refactor/a1_family`, `8f9d69e..b159b5b`; spec test `checks/a1_engine_spec.py` 92/92). Its check
(`crx_<p>_a1_check`) is the first PROD run of the full rule, including the balance. Filled in UAT
from the round-3 code: the cross-product feature body, the WM "self" column, the class table
against the flow dictionary, the check's outcome block.

## 1. What stays from today

- **Grain and dates.** One state per `(account_id, observation_date)`; observation dates are month
  ends.
- **Window W.** The observation month plus the months before it: 3 at 60–180, 6 at 180+
  (`_common.window_months`). `MIN_MONTHS = {3: 2, 6: 3}`.
- **No pre-delinquency data** (GRR): every signal comes from W or from the observation-month
  snapshot.
- **Anchor**, which is what the customer must find now:
  - CC 60–180: the oldest non-zero overdue bucket on the observation-month snapshot;
  - RL: one EMI;
  - 180+ or missing: flat floors only.
- **CIF level.** All customer signals cover every account of the `cif_id`.
- **Income (F1).** Computed exactly as today's `income_level` (S12, S14).
- **The bureau salary source is swappable** (user, 2026-11-10). **Next source:** the DE's
  `feat_bureau_salary_unified` (handoff 66, `bundle_helpers/a1_final/bureau_salary_unified_handover.md`;
  `cif_id long`, `salary_month_end`, `monthly_salary`, `salary_source` alert > salary_credit >
  bureau_salary). Swapped in its own bundle after bundle 21 (user, 2026-11-11), once the exploration
  (`sonnet_a1_bureau_unified_exploration_prompt.md`) shows its coverage. GRR is building a bureau salary
  feature layer (`cif_id` / `month_end` / salary amount), to be followed by a bulk salary load. The
  engine therefore reads bureau salary through one contract only:
  - **Contract:** `feat_cif_bureau_salary_monthly`, one row per `(cif_id, month_end)` with
    `bureau_salary` (AED; 0 = salary account closed, which ends the series).
  - **To swap the source,** rebuild that dataset from the new layer: map its amount column to
    `bureau_salary` in the feature node. The engine, catalog name and persona pipelines stay as
    they are.
  - **Two alert-specific pieces stay in `a1_ability/signals.py` until then:**
    - the **one-month carry** (S14, `_with_next_month`) is removed together with the switch to the
      new bureau logic (user, 2026-11-10). The rule bundle leaves it alone;
    - **RL `feature_retail_loans`** (`_loan_bureau_salary`) is dropped with the swap: its salary is
      the loan application's, not a monthly series (user, 2026-11-11). The swap also drops the RL
      `loan_features` input and the `product == "rl"` branch.
  - The S12 level check for windows where only the bureau shows salary stays in the engine, because
    it is about how much a bureau amount is trusted, not where it comes from. Review it when the
    bulk load arrives.
- **Distress.** Cheque returns, DDS and bureau bounces (S15).

## 2. Families

Each family is **strong**, **some** or **none** (NULL = no data). Only strong scores, with 2 points.
"Some" scores 0 but still counts as evidence: it makes a row Low rather than Unknown.

| Family | Strong (2 points) | Some (evidence, 0 points) |
|---|---|---|
| **F1 Income** | today's `income_level` = stable | weak |
| **F2 Money in or held** | either inflow or balance (below) is strong | inflow some |
| **F3 Money out** | chosen spend + transfers out to the customer's own accounts at other banks (§3) ≥ max(AED 1,000, 1 × anchor) in ≥ `MIN_MONTHS` months of W | any month ≥ AED 500 |
| **F4 Cross-product** | deposits / investments / WM assets (AUM; kept, user 2026-11-10) ≥ max(AED 10,000, 3 × anchor) at the observation month end; **or** another credit product with us (incl. the customer's other cards, not supplementaries of the same contract) current at the observation month with instalment / minimum due ≥ max(AED 1,000, 1 × anchor) | any other product current, or any holding > 0 |

### F2 Money in or held

- **Inflow strong:** credits in the counted classes (§3) ≥ max(AED 1,000, 1 × anchor) in
  ≥ `MIN_MONTHS` months of W. Salary-flagged credits are left out, since salary is F1.
- **Inflow some:** any month of W with ≥ AED 1,000 of counted credits.
- **Balance strong:** the CASA average balance (`feat_cif_casa_balance_monthly`, WM's 49 CASA scheme
  codes, CIF level) ≥ max(AED 3,000, 1 × anchor) in ≥ `MIN_MONTHS` months of W, and the window
  average is no more than 50% below the prior window's. This is today's liquidity "adequate"
  condition on balances (`F_CASA`, `K_CASA`, `D_CASA`).
- **Balance below strong does nothing.** It scores no points and is not evidence. A small balance
  alone does not take a row out of Unknown (S11 as today: dormant accounts keep residual balances,
  and WM may fill missing months with 0).
- **Why the balance is back.** GRR said balances are swept against the overdue amount, so R3 dropped
  liquidity. The sweep is operational and manual (user, 2026-11-10), so a balance that survives it
  is real money held. It is rare (old liquidity "adequate" fired for 1.0% of CC and 1.4% of RL), and
  it belongs with money in rather than in a fifth family that would almost never be strong.
- **Dropped from old liquidity:** the external card payment branch (`ext_card_payment_max`). Payments
  to other lenders are invisible in our data (round 3: 3–4% of WM's external payments show as CASA
  debits) and made no difference to any state.
- **Kept apart from F4:** F4 balances are term deposits, investments and WM assets. They never
  include the CASA balance counted here.

## 3. Which transactions count (inclusion list)

A leg counts only if its class is positively identified; everything else is out. The classes come
from the round-3 flow dictionary: `tran_dc` × `tran_type` × `reason_for_excluding` ×
`tran_particular_code` × WM label × lane, plus two narration-stem rules.

| Class | F2 | F3 | Evidence (round 3) |
|---|---|---|---|
| `third_party_in` (transfers in, remittances, non-flagged salary-like credits) | yes | | positive lift in CC |
| `cash_in` (cash deposits) | yes | | CC cure +5.6pp, pay +19.8pp; dropping it demotes rows that perform at or above their state |
| `chosen_spend` (POS, ATM, bills, transfers to others) | | yes | every dominant type lifts alike |
| `reversal_return` (reversals, returned cheques / DDS, refunds, and the presentment they undo) | no | no | `CHQ RTN` / `CHQ NO` credits are 100% mirrored the same day; round 2 counted AED 186M (CC) / 264M (RL) of them as income |
| `own_out_external` (debits to the customer's own account at another bank: WM label `self`, or the own-account remittance types such as `OUTWARD REMITTANCE 120`) | | yes | money leaving our bank that the customer controls (user, 2026-11-10). Largest such type: CC 33,785 legs / AED 76.8M, RL 9,688 / AED 30.2M |
| `own_in_external` (credits from the customer's own account at another bank: WM label `self` on credits, or the own-account inward types) | yes | | money brought into our bank from elsewhere (user, 2026-11-10); round 2: own-account credits lift in CC (cure +7.8pp, pay +9.1pp) |
| `own_transfer` (between the customer's own accounts with us, auto-save) | no | no | the money never leaves our bank; no new evidence |
| `bank_initiated` (sweeps, fees, interest, disbursements, recoveries) | no | no | |
| `debt_elsewhere` | no | no | AED 0.2–1.0M; no state changes |
| `debt_to_us` (own card / own loan) | no | no | A3 |
| `unplaced` | no | no | meaning not established |

- **Lane before the self label on the wash lane** (user, 2026-11-10, handoff 57). A wash-lane leg
  (direct-debit returns, DDS legs) stays `own_transfer` / `reversal_return` even when WM labels it
  `self`, as the flow dictionary orders it: these are returns, not money moved to another bank
  (CC ~AED 19M, RL ~5M, almost all mirrored). The self label decides only outside that lane.
- **Fees and possible own-loan payments** (dictionary, step 4): a debit WM labels `fees_charges` is
  `bank_initiated`; a debit with WM's loan-payment flag and no bank counterparty is `unplaced`.
- **Pairs that cancel are netted.** A leg mirrored by an opposite leg of the same amount (±1%) within
  0–3 days on any account of the CIF is dropped together with its mirror when the pair is a bounce,
  reversal, sweep or round trip. Sweep-matched debits stay out of F3.
- **Salary flag:** `wm_pri_labelled_transactions.salary_txn_flag`, joined on
  `cif_id, tran_id, tran_date` (94–97% of keys match, 1.00 legs per key).
- **The class table lives in code** as a constant next to `feat_cif_casa.transaction_lane`, built
  from `flow_dictionary_<model_id>.md`. An allow-list replaces today's
  `economic` / `ambiguous` split for A1.

## 4. State

| State | Rule |
|---|---|
| High | 2 or more strong families (4+ points) |
| Moderate | exactly 1 strong family |
| Low | no strong family, but some evidence (any "some", F1 weak, or F4 some) |
| Unknown | no evidence in any family |

- **Distress** lowers the state one rung (High → Moderate → Low). Low stays Low.
- **Reason column:** the strongest family, or `distress` when the demotion fired. Unknown keeps
  `a1_unknown_reason` (`no_casa` / `dormant_casa`) as a description only, because it does not
  separate outcomes (round 3 B0).
- **Diagnostic flag, not part of the state:** `a1_sweepable_balance_flag` = balance strong in the
  observation month. It marks a delinquent customer holding money above the floor now, an
  operational lead for GRR.

## 5. Evidence for the rule (60–180, cohort Jan–May 2026, without the balance)

- **CC (R4):** High 1.4% / Moderate 15.1% / Low 30.1% / Unknown 53.4%. Cure / pay / roll:
  High 33.1 / 61.9 / 49.1, Moderate 16.4 / 42.3 / 72.5, Low 10.8 / 28.7 / 82.8, Unknown
  7.4 / 18.9 / 87.9. Every gap excludes 0.
- **RL (R4):** High 1.0 / 9.9 / 52.4 / 36.7%. Pay and roll order. High (117 cohort rows) cures
  below Moderate (−4.6pp, interval includes 0), so no cure claim at High.
- **Orthogonality:** R3 against A2 has Cramér's V 0.18–0.20, the same as today's rule.
- **Balance, expected effect:** small. Round 1's V2 (liquidity added while "some" still scored)
  added 72 High rows in CC and 37 in RL. With "some" at 0 and only the balance branch, fewer rows
  move. The bundle check reports the rows the balance moves and their outcomes.

## 6. Open (decisions for the user / GRR)

1. **Own-account transfers with another bank count both ways** (user, 2026-11-10): out in F3, in in
   F2. WM `self` and our wash lane disagree on CC 224,903 legs / AED 861M and RL 62,523 / AED 240M.
   The bundle check reports how many states these legs move. A transfer that returns within 3 days
   is still netted as a round trip, so moving money out and back does not count twice.
2. **The `MIN_MONTHS` knob** (2 of 3, 3 of 6) is the only one that moves more than 5% of rows (CC
   5.8%, RL 13.6%). GRR to confirm.
3. **The Unknown estimate** (round 3 B2) is a separate `a1_estimate` column, never part of the
   state.
   - CC passes all five criteria (FamGBM, pay gap +8–10pp, coverage 75–100%).
   - RL did not run (singular matrix).
   - It uses risk-model-style features, so GRR decides.
   - Before any use: absolute rates per group, and the F4 model's AUC of 0.93 checked for leakage
     from the holdings features.
4. **180+ has not run in any round.** At 180+ there is no anchor and Unknown is 87–90%.
5. **Today's A1 gate** (A6): 0.2% CC / 0.7% RL of rows leave Unknown only on legs round 3 called
   non-evidence. The largest of those, `OUTWARD REMITTANCE 120` to own accounts elsewhere, is now
   evidence (`own_out_external`), so the remaining gap is smaller still. The allow-list in §3 settles
   the rest when this rule ships.
