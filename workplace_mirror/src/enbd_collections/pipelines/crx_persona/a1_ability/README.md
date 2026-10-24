# A1 Ability — how the engine decides

A1 asks: **can this customer pay?** It looks at what we can see of their money — income,
liquid balances, failed payments — and gives one state per observation:
`ability_high`, `ability_moderate`, `ability_low` or `ability_unknown`.

This page explains the logic in plain terms. The detailed rule table (thresholds, decision
log) is the GRR workbook `A1_ability_20261022`; the code is `signals.py` (evidence) and
`classify.py` (levels and state). CC wraps it in `cc_a1_ability_v2` (the anchor).

## Ground rules

- **Grain:** one row per `(account_id, observation_date)` from the observation base.
  Observation dates are **month ends** (CC: until `cc_spine` itself is month-end, the
  observation base moves each billing-date row to its month end).
- **Windows are calendar months, by segment** (`_common.window_months`), the observation
  month included (m1 = the observation month, m2 the one before, …):
  - **60–180: 3 months** (m1–m3); the prior window m4–m6 (used to spot a decline).
  - **180+: 6 months** (m1–m6); the prior window m7–m12.
  - Every count scales with it: **"2 of 3" at 60–180 is "3 of 6" at 180+**
    (`MIN_MONTHS`), and every "in the window" rule (card payment, distress, CASA activity)
    reads 6 months at 180+.
  - The sections below are written for 60–180; read m1–m6 / m7–m12 and 3 of 6 for 180+.
- **Customer level.** Salary, CASA, card payments, bounces and returns are read across
  **all accounts of the customer's CIF**, never the scored account alone.
- **Anchor** (the workbook's "minimum due"): what the customer must pay now.
  - CC 60–180: the amount in the oldest overdue bucket (`overdue_bucket_01..06`) on the
    latest balance snapshot in the observation month.
  - CC 180+: none. RL: one EMI.
  - No anchor → the flat floors below apply on their own.

## 1. Income — Stable (2 points) / Weak (1) / None (0)

**Step 1: one income amount per month** (`build_income_signals`). Two sources; for each
month **the larger one wins**.

- **Internal salary** — `wm_fea_salary_days_since_increment`, a weekly WM snapshot per CIF:
  - `week_number` = the snapshot date;
  - `ft_last_salary_amount` = the last salary credit WM detected;
  - `ft_days_since_salary_transaction` = how many days before the snapshot it came.
  - Credit date = snapshot date − days since; its month is the salary month. Several
    weekly snapshots see the same credit; they collapse to one value per month (a credit on
    30 July, seen by the 2, 9 and 16 August snapshots, lands in July).
- **Bureau salary** — `stg_aecb_salary_history`: `subj_salcr_hist_ref_mnth` (MMyyyy) and
  `subj_salcr_hist_tot_sal_amt`, linked to the CIF through `prm_bureau_cif_bridge`.

The result is `income_m1 … income_m6` (`… m12` at 180+); NULL = no salary that month from either source.

**Step 2: the level** (`income_level`).

- **Threshold** = max(AED 3,000, 2 × anchor).
- **2 of 3:** each of `income_m1..m3` scores 1 if it is at or above the threshold (NULL
  scores 0); Stable needs a count ≥ 2 (`MIN_MONTHS`; 3 of 6 at 180+). Any two months — not necessarily
  consecutive.
- **Not weakening:** the m1–m3 average must be ≥ 75% of the m4–m6 average
  (`D_INC = 0.25`); months without salary count as 0 here. No salary in m4–m6 → nothing to
  compare, the check passes.
- **Stable** = 2 of 3 at or above the threshold **and** not weakening.
  **Weak** = otherwise, any month in m1–m3 ≥ AED 1,000. **None** = neither.

Example — observation 31 July, anchor AED 2,000 → threshold 4,000:

| | Jul (m1) | Jun (m2) | May (m3) | Apr–Feb (m4–m6) |
|---|---|---|---|---|
| income | 5,000 | NULL | 4,500 | 5,000 each |

July and May qualify (count 2), but the 3-month average (5,000 + 0 + 4,500) / 3 = 3,167 is
below 75% of 5,000 = 3,750 → **Weak**, not Stable. The missing June pulls the average down.

## 2. Liquidity — Adequate (2 points) / Weak (1) / None (0)

**Evidence** (`build_liquidity_signals`):

- **CASA balance per month** (`casa_m1 … casa_m6`, `… m12` at 180+) — `wm_fea_casa_eod_avg_balance`:
  current + savings average balance, taken as the 4-week average on the month's last weekly
  snapshot.
- **External card payment** (`ext_card_payment_max`) — the largest single CASA outflow
  in m1–m3 (`wm_pri_labelled_transactions`) to a credit card the customer registered as a
  beneficiary (`raw_beneficiary_cards`, card numbers). It shows money paid to other banks'
  cards.

**Level** (`liquidity_level`):

- **Adequate** = either
  - CASA ≥ max(AED 3,000, 1 × anchor) in at least 2 of m1–m3, **and** the m1–m3 average not
    more than 50% below the m4–m6 average (months without data are skipped here, not 0); or
  - one external card payment ≥ max(AED 500, 1 × anchor).
- **Weak** = otherwise, CASA ≥ AED 1,000 in any of m1–m3, or a card payment ≥ AED 1,000.
- **None** = neither.

## 3. Distress — a failed payment lowers the state one level

`distress_flag = 1` when the customer has **at least one** of these in m1–m3
(`build_distress_signals`):

- **Internal:** a returned cheque or a DDS (direct debit) reject/reversal on any of their
  CASA accounts — `prm_casa_return_events`, `reason_for_excluding` in
  `CHEQUE RETURNS`, `DDS Rejects/Reversal`. POS reversals (`RETURNS`) do not count. The
  debit and credit legs of one return count once.
- **Bureau:** `prm_bureau_alert_enriched` with `bounced_cheque_amount > 0`, dated by
  `extract_date` — the date the report was pulled, not the date of the bounce.

## 4. The state

Points = income points + liquidity points (0–4).

| State | Rule |
|---|---|
| `ability_unknown` | 0 points, no distress **and** no CASA transaction in m1–m3 (`casa_active`, from `wm_fea_casa_cc_inflow_outflow`) — we see nothing, which is not evidence of no ability |
| `ability_high` | 4 points, no distress |
| `ability_moderate` | 2–3 points without distress, or 4 points with distress |
| `ability_low` | everything else: 0–1 points, or 2–3 points with distress |

Unknown is checked first. Distress moves a customer exactly one rung down (High →
Moderate, Moderate → Low).

## Known limits

- **Two salary credits in one month count once.** Each snapshot carries only the *last*
  salary and the month keeps the largest amount, not the sum: two credits a month (salary
  plus allowance, split payments) show as the larger one; two credits in the same week can
  hide the earlier.
- **Only what WM labels as salary counts.** Regular non-salary income (own business,
  rent, transfers from family) is invisible — about a third of customers ever show an
  internal salary, and about a third hold no CASA with us at all.
- **Bureau salary is sparse for now.** The GRR bureau salary feed is the planned fix; it
  enters through the same "larger of the two per month" rule.
- **Missing salary months count as 0 in the weakening check**, so one late or missed
  salary can turn Stable into Weak (see the example).
- **Bureau bounces are dated by the pull date.** A bounce repeated in later reports keeps
  the flag on; when the bounce really happened is under investigation.
