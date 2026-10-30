# A1 — Ability: spec and code conformance

Source: `A1_ability_20261022.xlsx` (sheets *A1 rules*, *Thresholds*), photographed 2026-10-23.
Section 1–3 transcribe the workbook; section 4 compares it with the code.

## 1. Inputs

Internal salary credit, bureau salary, CASA average balance, external card payments,
cheque bounces, DDS (direct debit) returns, customer-initiated CASA transactions (the
activity gate, S11). One added input: the card's
outstanding balance, to work out the **minimum due = max(5% × outstanding, AED 100)**.
Setting the three multiples (`k_inc`, `k_casa`, `k_pay`) to 0 runs on flat amounts only.

## 2. Rules

State = income points + liquidity points, then distress.

| State | Rule | In plain words |
|---|---|---|
| High | 4 points and no distress | Regular income and a buffer, both confirmed |
| Moderate | ≥ 2 but < 4 points and no distress, or 4 points with distress | One side confirmed, or both partly; or everything in place but a payment has just failed |
| Limited | < 2 points with any signal, or < 4 points with distress | What we can see shows little or nothing to pay with |
| Unknown | 0 points, no distress, and no CASA with us or a dormant one (no customer-initiated money movement in the window, S11) | We cannot see the customer's money: absence of data, not evidence of no ability |

| Consideration | Level | Points | Rule |
|---|---|---|---|
| Income (internal salary credit, bureau salary) | Stable | 2 | A *salary month* has an internal salary credit ≥ max(AED 3,000, 2 × minimum due) or a bureau salary ≥ max(AED 3,000, 2 × minimum due). Stable = a salary month in at least 2 of the last 3, **and** the 3-month average income not more than 25% below the prior 3 months |
| | Weak | 1 | Some income in the last 3 months (AED 1,000 or more in any month) but not Stable: below threshold, irregular or weakening |
| | None | 0 | No internal salary credit and no bureau salary of AED 1,000 or more in any of the last 3 months |
| Liquidity (CASA average balance, external card payments) | Adequate | 2 | CASA average balance ≥ max(AED 3,000, 1 × minimum due) in at least 2 of the last 3 months **and** the 3-month average not more than 50% below the prior 3 months. Or at least one external card payment ≥ max(AED 500, 1 × minimum due) in the last 3 months |
| | Weak | 1 | Not Adequate, but a CASA average balance of AED 1,000 or more in any of the last 3 months, or any external card payment of that size |
| | None | 0 | No CASA average balance and no external card payment of AED 1,000 or more in the last 3 months |
| Distress (cheque bounce, DDS return) | Yes | −1 level | 1 or more cheque bounces or DDS returns in the last 3 months |
| Activity gate (CASA transactions) | Dormant | Unknown | Income None, Liquidity None, no distress, and no customer-initiated CASA transaction in the last 3 months (no CASA at all included) — S11 |

Map (every combination has one state):

| | Liquidity Adequate | Liquidity Weak | Liquidity None |
|---|---|---|---|
| **No distress** — Income Stable | High | Moderate | Moderate |
| Income Weak | Moderate | Moderate | Limited |
| Income None | Moderate | Limited | Limited (Unknown if the CASA is dormant or absent) |
| **With distress** — Income Stable | Moderate | Limited | Limited |
| Income Weak | Limited | Limited | Limited |
| Income None | Limited | Limited | Limited |

## 3. Thresholds (starting values; no PROD calibration yet)

| Key | Threshold | Business table | Value |
|---|---|---|---|
| `n3` | Months out of the last 3 that must qualify | 2 of 3 | 2 |
| ~~`n6`~~ | ~~Months out of the last 6 (regular income)~~ | — | removed after the 10-07 meeting |
| `f_int` | Internal salary credit floor | AED 1,000 | AED 3,000 |
| `f_bur` | Bureau salary floor | AED 2,000 | AED 3,000 (adjusted after 10-07) |
| `k_inc` | Income: multiple of the card's minimum due | none | 2.0 |
| `d_inc` | Income weakening: fall of the 3-month average vs the prior 3 months | not defined | 25% |
| `f_casa` | CASA average balance floor | AED 2,000 | AED 3,000 (adjusted after 10-07) |
| `k_casa` | CASA: multiple of the minimum due | none | 1.0 |
| `d_casa` | CASA weakening: fall of the 3-month average vs the prior 3 months | not defined | 50% |
| `f_pay` | External card payment floor | AED 500 | AED 500 |
| `k_pay` | External card payment: multiple of the minimum due | none | 1.0 |
| `demin` | Smallest amount that counts as evidence | not defined | AED 1,000 (adjusted after 10-07) |
| `n_bnc` | Cheque bounces + DDS returns in the last 3 months that count as distress | at least 1 | 1 |
| `s_high` / `s_mod` | Points needed for High / Moderate | n/a | 4 / 2 |
| `mpd_rate` / `mpd_floor` | Minimum due: share of outstanding / floor | n/a | 5% / AED 100 |

Every customer-level signal (salary, CASA, external payments, cheque bounces, DDS returns)
is read across **all accounts of the customer's CIF**, not the scored account — an RL
`account_id` is never the customer's CASA account (user, 2026-10-23).

## 4. Decisions (2026-10-23) and how the engine implements them

The shared engine (`crx_persona/a1_ability`, bundle 01) follows sections 1–3, with these
decisions by the user where the workbook and the earlier code disagreed:

| # | Topic | Decision | Implementation |
|---|---|---|---|
| S1 | Anchor (the workbook's "minimum due") | **CC 60–180: the amount in the oldest overdue bucket**, excluding the 181–210 bucket and the 211+ catch-all; **CC 180+: no anchor** (absolute thresholds only); **RL: one EMI**. Missing → flat floors | `build_cc_liquidity_anchor`: oldest non-zero of `overdue_bucket_01..06` on the latest snapshot in the observation month; NULL at 180+ |
| S2 | Income multiple | Income ≥ max(AED 3,000, **2 × anchor**) | `K_INC = 2` |
| S3 | Salary month | per-month amount ≥ threshold, Stable = 2 of the last 3 | `feat_cif_internal_salary_monthly`: WM's monthly salary total, the month = the snapshot week (`week_number` = `yyyyMM0W`) minus the days since, rounded to the nearest first of a month (O64 fixed in bundle 08); `feat_cif_bureau_salary_monthly` (S14); the larger counts |
| S4 | Income weakening | last-3-month average ≥ 75% of the prior 3 | `D_INC = 0.25`, months without salary count as 0 |
| S5/S6 | Weak income, bureau window | any month ≥ AED 1,000 in the last 3 months (bureau included) | the observation month (a month end) and the 2 months before it (6-month window at 180+, S10) |
| S7 | CASA | ≥ floor in 2 of the last 3 months and not > 50% below the prior 3 | monthly CASA (CA+SA) average from `wm_fea_casa_eod_avg_balance` (4-week average at the month's last weekly snapshot) |
| S8 | External card payment | one payment ≥ max(AED 500, anchor) / ≥ AED 1,000 for Weak | largest single payment in the last 3 months |
| S9 | Distress | cheque bounces and DDS returns, bureau **and internal**, across all the customer's accounts | `feat_cif_returns_monthly` (internal cheque / DDS returns) + `feat_cif_bureau_bounces_monthly` (a new bureau bounce: amount changed vs the key's previous pull; repeats count once); `payment_order` slot ready |
| S10 | Window by segment (user, 2026-10-24) | the workbook's 3-month windows | **60–180: 3 months, 180+: 6 months**, the observation month included, as on every other axis; "2 of 3" becomes **3 of 6** at 180+; the prior window is the 6 months before; card payments, distress and CASA activity read the 6 months | `_common.window_months(model_id)`; `classify.MIN_MONTHS = {3: 2, 6: 3}` |
| S11 | Activity gate (user, 2026-10-27; revised 2026-10-28 after A1 v03b) | the *Signal* row (no CASA transaction) and the *Unknown* text disagree; and any WM CASA flow kept the gate open, mostly the bank's own EMI recovery on RL | Within 0 points and no distress (balance < AED 1,000 in every month, no qualifying income or card payment): **Unknown** when the customer has no CASA with us or a **dormant** one — no customer-initiated money movement on any of the CIF's CASA accounts in the window; otherwise **Limited** (an account they use, where money never stays). Counts: credits from third parties (salary, transfers in, cash deposits), card and ATM spend, transfers out, bill payments, paying their own credit card. Does not count: the bank recovering the customer's own loan instalment (`INSTL_RECOVERY-PL/AL`, debits to their loan account), transfers between their own CASA accounts (net zero at CIF level), fees, charges, interest, reversals. Distress always means Limited. Sized by v03b: CC Limited→Unknown 1,058–2,171 (15–31%), RL Limited 89.5% → ~45–60% | bundle 08: `prm_casa_transactions` (all CASA legs) → `feat_cif_casa_activity_monthly` (legs per lane, FTR row-handling reference); customer-initiated = lanes `economic`, `card_spend`, `card_payment` (user, 2026-10-29); `a1_unknown_reason` = `no_casa` (no CASA leg and no positive balance in 12 months; WM may zero-fill balances, user 2026-10-29) or `dormant_casa` |
| S12 | Salary timing (user, 2026-10-27; sized by A1 v03) | a salary month = a calendar month with salary ≥ the threshold, 2 of 3 months | an employer may pay early, so one month holds two salaries and the next none; the WM table gives only monthly totals (`bundle_helpers/a1_final/wm_salary_feature_logic.md`). **Window-total rule:** Stable = salary received in the window (sum of the monthly incomes, each the larger of internal and bureau) ≥ 2 × the threshold (3 × at 180+) **and** the window total not more than 25% below the prior window's total. Known limit: a month with salary plus a large bonus can pass | bundle 08: `INC_FLOORS = {3: 2, 6: 3}`, `D_INC = 0.25` on the window totals |
| S13 | End-of-service payment (user, 2026-10-27) | — (the workbook has no EOS rule) | EOS is not salary; it counts only through the CASA balance. The WM salary table already excludes EOS (user), so internal income needs no rule. Bureau: no rule — v03b found bureau history too thin to show spikes (CC 3, RL 10 EOS-like months); revisit with GRR's bureau feed. DCORE EOSB results (EOS expected / received; v03b: 292 CC, 175 RL rows) are a **diagnostic column only**, no effect on points or state (user, 2026-10-28) | internal: as is; bureau: none; EOSB diagnostic `a1_eosb_flag` (a DCORE result naming EOSB in W): bundle 08 |
| S14 | AECB salary from the alert table (user, 2026-10-30) | the workbook names bureau salary, no source | `salary_credit_amount` (category 5, types 31 and 32) is a reported salary, accurate on the pull date (`extract_date`). It counts in the extract month and is filled forward by at most 1 month, so pulls every 2 months give a continuous series. Never filled backwards, never across all of W. Income, S12 and the 25% check then apply unchanged (larger of internal and bureau per month) | bundle 09: `feat_cif_bureau_salary_monthly` reads `prm_bureau_alert_enriched` (the month's latest pull; type 43, salary account closed, gives 0 and ends the carry); `build_income_signals` carries it (RL's `feature_retail_loans` salary too). Replaces the salary-history path (its bridge can give a co-party's salary, R19). A stopped salary is seen only as a closure, a lower amount (the 25% check) or the end of an internal salary: an internal salary of 10,000 followed by one pull at 10,000 gives 20,000 against 30,000, so Weak. Diagnostics `a1_income_source`, `a1_salary_stopped` change nothing |

Every customer-level signal is read across **all accounts of the CIF**. Local check:
`workplace_mirror/checks/a1_engine_spec.py` — 60 cases built from source-shaped rows through the
primaries and features, all passing (2026-10-30).
