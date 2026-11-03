# DE spec: `A3_credibility_shared_Nov3.xlsx`, sheet "A3 framework" (transcribed 2026-11-03)

Photos IMG_8727–8733 (handoff 34). Cell text verbatim; row numbers are the sheet's. Blue cells
(points, values) are inputs. A second sheet, "Tester", exists and was not photographed.

**Row 1:** A3 Payment Credibility: framework

**Row 2:** Accounts at 60+ DPD under active collection, credit card and retail loan. Built from "A3
Payment Credibility Business Summary (Waterfall) + Redesign Ask": the 25 waterfall arms become 3 scored
dimensions, 1 override and 1 gate.

| Row | | |
|---|---|---|
| 4 | MECE check | 72 of 72 level combinations are claimed by exactly one state (block 4). 12 of 12 test accounts give the expected state; 5 of them get a different state from the current waterfall (Tester). |
| 5 | How to read | Score the three dimensions (block 2) and add the points. A strong negative (block 3) takes one level off. Read the state in block 1. |
| 6 | Boundary | Payments in delinquency and the record before delinquency are separate dimensions with separate windows, split at onset. No feature spans both. |
| 7 | Basis | Nothing here is measured on PROD. The 80% / 40% cuts, 2 concluded, 3 in a row and 3 contact dates are the waterfall's own. Points, state cut-offs and the payment windows are proposals to calibrate (block 5). |

## 1. State: add the points, take one level off for a strong negative (rows 9–14)

| State | Rule (total points) | In plain words |
|---|---|---|
| High | Total of 4 or more, and no strong negative. | Keeps commitments and money is coming in. |
| Moderate | Total from 1 to below 4, and no strong negative. Or 4 or more with a strong negative. | Some evidence to rely on, not yet consistent. Or a strong record with a fresh refusal. |
| Low | Total below 1. Or below 4 with a strong negative. | Nothing positive on record, or what there is has been outweighed by broken commitments, a refusal or no response. |
| Unknown | No evidence in any dimension: commitments Thin, payments None, no record before, and no strong negative. | Nothing observed either way. Not the same as Low. |

## 2. Dimensions: three questions, scored separately (blue points are inputs) (rows 16–33)

| Level | Points | Rule | In plain words |
|---|---|---|---|
| **A. Commitments kept.** Does the customer do what they commit to? A 4-way read of promises and arrangement instalments due in the window below, checked in this order: Broken first (a strong negative overrides a better average) → Kept → Partly kept → Thin, the no-evidence fallback. | | | |
| Window | | Promises and arrangement instalments that fell due in the last 12 months of this delinquency. Pending ones do not count. | |
| Kept | 2 | Not Broken, at least 2 concluded, and 80% or more of them kept. | A proven track record: enough commitments have concluded, and the large majority were honoured. |
| Partly kept | 1 | Not Broken, not Kept, and at least one kept. | Not reliable enough to call Kept, not bad enough to call Broken — some proof it isn't a blank slate. E.g. one commitment ever, and it was kept, or a mixed record, some kept, some broken. |
| Thin | 0 | None concluded, or one concluded and broken. No evidence either way. | Nothing has concluded yet, or the one thing that did was broken — there's no track record to judge, good or bad. |
| Broken | 0 | The last 3 concluded were all broken, or at least 2 concluded and fewer than 40% kept. Checked first: a recent streak overrides a better average. Also a strong negative (block 3). | A clear negative pattern on record: either a recent run of broken commitments, or most of what's concluded was missed. |
| **B. Payments in delinquency.** Is money coming in now? | | | |
| Window | | All payments in the last 3 months (61-180 DPD) or 6 months (180+ DPD), after onset only. Promised or not. | |
| Regular | 2 | A qualifying payment in 2 or more months of the window (61-180 DPD), or 3 or more months of the window (180+ DPD). Qualifying: at least 100% of one month's due amount. | Money came in during at least two of the three months (61-180 DPD), or three of the six months (180+ DPD) — a genuine, repeated payment, not a one-off. |
| Some | 1 | Not Regular, and any payment in the window. (180+ 12 months window ) | Not enough months of payment to call Regular, but something came in during the window — not completely silent. |
| None | 0 | No payment in the window. | Nothing came in during the window — fully silent since onset. |
| **C. Record before delinquency.** Did they pay as billed before it started? | | | |
| Window | | The 12 months before onset. Never mixed with months after onset. | |
| Clean | 1 | Paid as billed in 80% or more of the months with an amount due. As billed: at least the amount due, by the due date. Paying the minimum counts. | Paid at least the amount due, on time, in the large majority of months before the account went delinquent — including customers who only ever paid the minimum. |
| Not clean | 0 | Below 80%. Partial and missed months both count against. | Fell short of that bar — partial payments and missed months both count against, regardless of how far short. |
| No record | 0 | Fewer than 3 months with an amount due before onset. No evidence either way. | Too few months with anything due before onset to say anything either way — not evidence of good or bad behaviour. |

## 3. Strong negatives: any one takes the state down one level; they do not stack (rows 35–39)

| Strong negative | Rule | Replaces waterfall arms |
|---|---|---|
| Broken commitments | (A) Commitments kept dimension is at level Broken. | Low 1 to 5: break streaks, under 40% kept or paid. |
| Refusal | The latest right-party contact ended in a refusal to pay, and no promise, arrangement or payment has followed it. | Low 6 to 8: flat refusal, consistently refusing, promised then refused. |
| No response | Contact attempted on 3 or more separate dates without reaching the customer, no promise or arrangement on record, and no payment in the window. | Low 9: contacted enough times, nothing to show for it. |

## 4. The map: every combination of levels, and the one state it gets (rows 41–70)

Columns: refusal or no response / C. record before delinquency (points C).

| A. Commitments | B. Payments | Points A + B | No / Clean (1) | No / Not clean (0) | No / No record (0) | Yes / Clean (1) | Yes / Not clean (0) | Yes / No record (0) |
|---|---|---|---|---|---|---|---|---|
| Kept | Regular | 4 | High | High | High | Moderate | Moderate | Moderate |
| Kept | Some | 3 | High | Moderate | Moderate | Moderate | Low | Low |
| Kept | None | 2 | Moderate | Moderate | Moderate | Low | Low | Low |
| Partly kept | Regular | 3 | High | Moderate | Moderate | Moderate | Low | Low |
| Partly kept | Some | 2 | Moderate | Moderate | Moderate | Low | Low | Low |
| Partly kept | None | 1 | Moderate | Moderate | Moderate | Low | Low | Low |
| Thin | Regular | 2 | Moderate | Moderate | Moderate | Low | Low | Low |
| Thin | Some | 1 | Moderate | Moderate | Moderate | Low | Low | Low |
| Thin | None | 0 | Moderate | Low | Unknown | Low | Low | Low |
| Broken | Regular | 2 | Low | Low | Low | Low | Low | Low |
| Broken | Some | 1 | Low | Low | Low | Low | Low | Low |
| Broken | None | 0 | Low | Low | Low | Low | Low | Low |

Rows 58–70: "Number of state rules that claim each cell (the proof: it must be 1 everywhere)" — 1 in
every cell.

## 5. Cut-offs and windows (blue = input; both sheets recalculate) (rows 72–89)

| Parameter | Value | Source | Why this value |
|---|---|---|---|
| State: High from (total points) | 4 | Proposed | The top level on commitments or payments, backed by the other two. A kept arrangement with regular payments is High on its own, as in the waterfall. |
| State: Moderate from (total points) | 1 | Proposed | Any one piece of positive evidence. Below it there is nothing to rely on. |
| Commitments: window in months, inside this delinquency | 12 | Proposed | The waterfall has no window; its recency-weighted rate did that job. One window and the streak rule replace it. Defines the input. |
| Commitments: concluded needed before a rate counts | 2 | Waterfall (High 3, Low 4) | Fewer than 2 is not a pattern. |
| Commitments: Kept from (share kept) | 80% | Waterfall (High 1, 2, 5) | The waterfall's cut. |
| Commitments: Broken below (share kept) | 40% | Waterfall (Moderate 1, 7, Low 4, 5) | The waterfall's cut. |
| Commitments: Broken when the last N concluded were all broken | 3 | Waterfall (Low 1, 2) | Covers Low 3 as well: 4 missed instalments in a row contain 3. |
| Payments in delinquency: window in months (61-180 DPD) | 3 | Proposed | The waterfall uses 30, 60 and 90 days in different arms. Month grain so the retail loan snapshot can feed it. Defines the input. |
| Payments in delinquency: qualifying payment, share of one month's due | 100% | Proposed | Requires the full month's due amount, not a token payment, to count as qualifying. Defines the input. |
| Payments in delinquency: Regular from (qualifying months) (61-180 DPD) | 2 | Proposed | Two months of three. |
| Record before: window in months before onset | 12 | Redesign ask | The window the card payment ratio already covers. Defines the input. |
| Record before: months with an amount due needed | 3 | Proposed | Below this the record says nothing and the level is No record. |
| Record before: Clean from (share of months paid as billed) | 80% | Proposed | Same cut as commitments: 10 of 12 months. |
| No response: separate contact dates from | 3 | Waterfall (Low 9) | The waterfall's count. |
| Payments in delinquency: window in months (180+ DPD) | 6 | Proposed | Longer bucket, slower cadence: a 6-month window instead of 3, so there is enough time to see a payment land as transactions thin out further into delinquency. Defines the input. |
| Payments in delinquency: Regular from (qualifying months) (180+ DPD) | 3 | Proposed | Three qualifying months out of the 6-month window. |

Not in the sheet (code only): the 100 AED floor at 180+ (`_TAU_A3V2_DLQ_PAYMENT_MIN_AMOUNT_180_PLUS`),
the 12-month any-payment window at 180+ beyond the "Some" cell's note, the bucket-08 baseline due, the
cycle sanity limits (35 / 62 days), and `cc_a3_history_floor_date`.
