# A1 — Ability: spec and code conformance

Source: `A1_ability_20261022.xlsx` (sheets *A1 rules*, *Thresholds*), photographed 2026-10-23.
Section 1–3 transcribe the workbook; section 4 compares it with the code.

## 1. Inputs

Internal salary credit, bureau salary, CASA average balance, external card payments,
cheque bounces, DDS (direct debit) returns, CASA transactions. One added input: the card's
outstanding balance, to work out the **minimum due = max(5% × outstanding, AED 100)**.
Setting the three multiples (`k_inc`, `k_casa`, `k_pay`) to 0 runs on flat amounts only.

## 2. Rules

State = income points + liquidity points, then distress.

| State | Rule | In plain words |
|---|---|---|
| High | 4 points and no distress | Regular income and a buffer, both confirmed |
| Moderate | ≥ 2 but < 4 points and no distress, or 4 points with distress | One side confirmed, or both partly; or everything in place but a payment has just failed |
| Limited | < 2 points with any signal, or < 4 points with distress | What we can see shows little or nothing to pay with |
| Unknown | No signal: no income, no CASA balance or transaction, no external card payment, no bounce or return | Absence of data, not evidence of no ability |

| Consideration | Level | Points | Rule |
|---|---|---|---|
| Income (internal salary credit, bureau salary) | Stable | 2 | A *salary month* has an internal salary credit ≥ max(AED 3,000, 2 × minimum due) or a bureau salary ≥ max(AED 3,000, 2 × minimum due). Stable = a salary month in at least 2 of the last 3, **and** the 3-month average income not more than 25% below the prior 3 months |
| | Weak | 1 | Some income in the last 3 months (AED 1,000 or more in any month) but not Stable: below threshold, irregular or weakening |
| | None | 0 | No internal salary credit and no bureau salary of AED 1,000 or more in any of the last 3 months |
| Liquidity (CASA average balance, external card payments) | Adequate | 2 | CASA average balance ≥ max(AED 3,000, 1 × minimum due) in at least 2 of the last 3 months **and** the 3-month average not more than 50% below the prior 3 months. Or at least one external card payment ≥ max(AED 500, 1 × minimum due) in the last 3 months |
| | Weak | 1 | Not Adequate, but a CASA average balance of AED 1,000 or more in any of the last 3 months, or any external card payment of that size |
| | None | 0 | No CASA average balance and no external card payment of AED 1,000 or more in the last 3 months |
| Distress (cheque bounce, DDS return) | Yes | −1 level | 1 or more cheque bounces or DDS returns in the last 3 months |
| Signal (CASA transactions) | No | Unknown | Income None, Liquidity None, no distress and no CASA transaction in the last 3 months |

Map (every combination has one state):

| | Liquidity Adequate | Liquidity Weak | Liquidity None |
|---|---|---|---|
| **No distress** — Income Stable | High | Moderate | Moderate |
| Income Weak | Moderate | Moderate | Limited |
| Income None | Moderate | Limited | Limited (Unknown if no CASA transactions) |
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
| S3 | Salary month | per-month amount ≥ threshold, Stable = 2 of the last 3 | internal credits recovered per month from the WM salary snapshots (credit date = snapshot − days since credit); bureau salary per month; the larger counts. TODO(sonnet): validate against `feat_payroll_indicator` |
| S4 | Income weakening | last-3-month average ≥ 75% of the prior 3 | `D_INC = 0.25`, months without salary count as 0 |
| S5/S6 | Weak income, bureau window | any month ≥ AED 1,000 in the last 3 months (bureau included) | the observation month (a month end) and the 2 months before it |
| S7 | CASA | ≥ floor in 2 of the last 3 months and not > 50% below the prior 3 | monthly CASA (CA+SA) average from `wm_fea_casa_eod_avg_balance` (4-week average at the month's last weekly snapshot) |
| S8 | External card payment | one payment ≥ max(AED 500, anchor) / ≥ AED 1,000 for Weak | largest single payment in the last 3 months |
| S9 | Distress | cheque bounces and DDS returns, bureau **and internal**, across all the customer's accounts | bureau bounced cheques wired; `payment_order` and `internal_returns` slots ready. TODO(sonnet): find the internal returned-cheque / DDS-return source |

Every customer-level signal is read across **all accounts of the CIF**. Local check:
`workplace_mirror/checks/a1_engine_spec.py` — 25 cases built from the workbook rows, all
passing.
