# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks for independent evidence that the customer has
money — income, money coming in or held, money going out by choice, other products with us —
and failed payments, and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule is `specs/A1_ability_family_rule.md`
(income: `specs/A1_ability_spec.md` S1–S16); the code is
`signals.py` (evidence), `classify.py` (levels and state) and `pipeline.py` (nodes). CC wraps
it in `cc_a1_ability`, RL in `rl_a1_ability`; each wrapper adds its anchor.

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends**. Only the persona months are scored,
  `crx_persona.persona_start_date` to `persona_end_date`.
- **Layers:** the signal nodes read the observation base and monthly feature tables, one
  row per `(cif_id, month_end)` — never raw or staging tables:

  | Feature | Built from (pipeline) |
  |---|---|
  | `feat_cif_internal_salary_monthly` | `wm_fea_salary_days_since_increment` (`casa_features`) |
  | `feat_cif_casa_balance_monthly` | WM CASA balance and flow tables (`casa_features`) |
  | `feat_cif_casa_flows_monthly` | `prm_casa_transactions` ← FTR + `wm_pri_labelled_transactions` (`casa_features`) |
  | `feat_cif_cross_product_monthly` | product holding, loan portfolio, card balances, WM assets (`product_features`) |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | the DE's `feat_bureau_salary_unified` (`bureau_salary_bounces`) |
  | `feat_cif_bureau_bounces_monthly` | `prm_bureau_alert_enriched` (`bureau_salary_bounces`) |

- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month. CC 180+: none.
  - RL: one EMI — `installment_due_amount` on the observation month's `int_loan_master`
    snapshot.
  - No anchor → the flat floors below apply on their own.

## 1. F1 Income — Stable (2 points) / Weak (evidence) / None

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — one monthly AECB salary per CIF from the DE's unified table (alert
  change events first, then application-time salary history, then the bulk pull's
  aggregates spread back over 12 months). A row counts in its month and the next, never
  before it and no further (S14); a 0 row ends the carry.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`) and the prior window's internal salary (`internal_salary_prior`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`D_INC = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000 (no points, but evidence: Low rather
  than Unknown). **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Which transactions count (`feat_cif_casa_flows_monthly`)

Every CASA leg gets one class (`feat_cif_casa.flow_class`, on top of `transaction_lane`).
Only these count:

- **Money in:** transfers and remittances from others and clearing credits
  (`third_party_in`), cash deposits (`cash_in`), credits from the customer's own account at
  another bank (`own_in_external`, WM label).
- **Money out:** card spend, ATM, bills, transfers to others (`chosen_spend`), debits to the
  customer's own account at another bank (`own_out_external`, WM label).

Nothing else counts: salary-flagged credits (they are income), reversals, returned cheques /
DDS and the cheque presentments they undo (narrations `CHQ RTN` / `CHQ NO`), refunds,
transfers between the customer's accounts with us, fees and interest, paying their own card
or loan, and anything whose meaning is not established (the rest of `MISCELLANEOUS`). A
counted leg mirrored by a leg that does not count — the same amount (±1%) within 3 days —
is dropped (a bounce, a reversal, a sweep).

## 3. F2 Money in or held, F3 Money out — Strong (2) / Some (evidence) / None

- **F2 strong** = money in ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3 (3 of 6 at 180+),
  **or** the CASA balance ≥ max(AED 3,000, 1 × anchor) in 2 of m1–m3 and not more than 50%
  below the m4–m6 average (money held: the bank's sweep is manual, so a balance can survive
  it). **Some** = any month with ≥ AED 1,000 of money in. A balance below strong is not
  evidence.
- **F3 strong** = money out ≥ max(AED 1,000, 1 × anchor) in 2 of m1–m3. **Some** = any month
  ≥ AED 500.
- `a1_sweepable_balance_flag` = the balance is strong: money above the floor the bank could
  still sweep (a lead for collections; it changes nothing).

## 4. F4 Cross-product — Strong (2) / Some (evidence) / None

At the observation month end, the customer's other products with us (the scored account
left out): **strong** = deposits + investments + WM assets ≥ max(AED 10,000, 3 × anchor), or
another credit product (incl. other cards) that is current with an instalment / minimum due
≥ max(AED 1,000, 1 × anchor); **some** = any other current credit product or any asset.

## 5. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a bounced cheque reported by the bureau, one per CIF and return date
  (`DT_OF_RETURN`, S15).

## 6. The state

Only strong levels score (2 points each); weak / some are evidence.

| State | Rule |
|---|---|
| `high` | two or more strong families (4+ points) |
| `moderate` | one strong family |
| `low` | no strong family, but some evidence (income weak, money in / out some, cross-product some), or distress alone |
| `unknown` | no evidence in any family, no distress **and** no counted CASA leg in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA leg or positive balance in 12 months) or `dormant_casa` |

Distress moves a customer exactly one rung down (High → Moderate → Low). `a1_reason` names
the strongest family (or `distress`). `a1_eosb_flag` (a DCORE end-of-service result in the
window) is a diagnostic column and changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts as income.** Other regular credits count as money in;
  about a third of customers hold no CASA with us, so F2 / F3 cannot see them.
- **Money in / out rest on the class table.** A flow type counts only once its meaning is
  established; new transaction types land in `unplaced` until they are classified.
- **Bureau salary is mostly an event feed for now.** Most rows are alerts, which appear only
  when something changes, so no row means nothing is known, not that the salary stopped; the
  bulk pull covers about 1% of customers. GRR's feed of pulls every 2 months enters through
  the same table. A stop shows only
  as a closure, a lower amount or the end of an internal salary (`a1_salary_stopped`).
- **Missing salary months count as 0** in the window total and the weakening check, except that
  with no internal salary in either window the weakening check compares the months with a value.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions`,
  the flows and the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
