# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`a1_state` = `high`, `moderate`, `low` or `unknown`, shown as `a1_state_label` = High,
Moderate, Low, Unknown.

This page explains the logic in plain terms. The rule table is the GRR workbook
`A1_ability_20261022` and the spec `specs/A1_ability_spec.md` (S1–S13); the code is
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
  | `feat_cif_casa_activity_monthly` | `prm_casa_transactions` ← FTR (`casa_primary`, `casa_features`) |
  | `feat_cif_ext_card_payment_monthly` | `wm_pri_labelled_transactions` + `prm_beneficiary_cards` |
  | `feat_cif_returns_monthly` | `prm_casa_return_events` ← FTR |
  | `feat_cif_bureau_salary_monthly` | `prm_bureau_salary_history` + `prm_bureau_cif_bridge` (`bureau_salary_bounces`) |
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

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — WM's monthly total of salary-flagged credits (bonuses and
  commissions included). WM's weekly snapshots carry the latest salary month's total and the
  days from the first of that month; `week_number` is `yyyyMM0W` (week 1–4 of the month), so
  the salary month is the snapshot week minus those days, rounded to the nearest first of a
  month.
- **Bureau salary** — the AECB salary history, the largest total any provider reported for
  the month, linked to the CIF through `prm_bureau_cif_bridge`. RL also reads
  `feature_retail_loans`: the salary of each loan's latest bureau pull, dated by the pull
  month.

The result is `income_m1 … income_m6` (`… m12` at 180+; NULL = no salary that month), and
the window's largest month per source (`internal_salary_w`, `bureau_salary_w`).

**Step 2: the level** (`income_level`, spec S12).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **Stable** = the salary received in m1–m3 adds up to **2 × the threshold** (3 × at 180+),
  **and** it is at least 75% of what m4–m6 received (`D_INC = 0.25`; nothing in m4–m6 →
  nothing to compare). The window total, not a count of months: an employer paying early
  puts two salaries in one month and none in the next.
- **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000, Stable needs 8,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | NULL | 9,000 | 4,500 | 5,000 each |

The window holds 13,500 ≥ 8,000, and 13,500 ≥ 75% of 15,000 → **Stable** (June's double
salary covers July).

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`) — current + savings average balance, the
  4-week average on the month's last weekly WM snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA payment in
  m1–m3 to a card registered as a payment beneficiary (money paid to another bank's card).

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3 (3 of 6 at 180+), **and** the
    m1–m3 average not more than 50% below the m4–m6 average (months without data skipped); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`; the parts are `distress_cheque`, `distress_dds`,
`distress_bureau`):

- **Internal:** a returned cheque or a DDS (direct debit) reject on any of their CASA
  accounts (`CHEQUE RETURNS`, `DDS Rejects/Reversal`). POS refunds (`RETURNS`) do not count;
  the two legs of one return count once.
- **Bureau:** a **new** bounced cheque in a bureau pull — per alert key (CIF, contract type,
  alert), a pull whose bounced amount differs from the key's previous pull, or follows a
  pull without one. A bounce repeated unchanged in later pulls counts once. Dated by the
  pull (the bureau gives no bounce date).

## 4. Activity — is there a CASA we can read? (spec S11)

The CASA legs of the transaction table (FTR) are sorted into lanes
(`feat_cif_casa.transaction_lane`, after the FTR row-handling reference). **Customer-initiated
movement** = a leg in the `economic` lane (remittances in and out, transfers to others, cash,
clearing, bill payments), `card_spend` (POS) or `card_payment` (paying their own credit
card). It does **not** count: transfers between the customer's own accounts and auto-save
(`wash`), the bank recovering the customer's loan instalment (`own_loan`), fees and interest,
reversals, returns, group-internal transfers and the ambiguous rest of `MISCELLANEOUS`.

- `casa_active` = a customer-initiated leg in m1–m3.
- `casa_held` = any CASA leg, or a positive balance, in the last 12 months. WM may fill a
  missing balance with 0, so a zero balance alone does not show a CASA.

## 5. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `unknown` | 0 points, no distress **and** no customer-initiated movement in m1–m3 — we cannot see the customer's money, which is not evidence of no ability. `a1_unknown_reason`: `no_casa` (no CASA with us in 12 months) or `dormant_casa` |
| `high` | 4 points, no distress |
| `moderate` | 2–3 points without distress, or 4 points with distress |
| `low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down.
`a1_eosb_flag` (a DCORE end-of-service result in the window) is a diagnostic column and
changes nothing.

## Known limits

- **The salary total is not a clean basic salary.** WM's flag counts bonuses, incentives,
  overtime and commissions, so a month with a large bonus can pass on its own.
- **Only what WM labels as salary counts.** Regular non-salary income is invisible; about a
  third of customers ever show an internal salary, and about a third hold no CASA with us.
- **Bureau salary reaches few customers** because `prm_bureau_cif_bridge` links only the
  bureau files with a contract link (O65). The GRR bureau salary feed and the link fix enter
  through the same "larger of the two per month" rule.
- **Missing salary months count as 0** in the window total and the weakening check.
- **Inputs follow the persona start.** `prm_casa_return_events`, `prm_casa_transactions` and
  the WM-based features keep a fixed number of months before
  `crx_persona.persona_start_date`; after moving that date, rerun `casa_primary` and
  `casa_features` first, or the A1 run stops (`build_distress_signals`).
