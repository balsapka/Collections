# A1 Ability — initial results

> **On hold (user, 2026-10-28): not for GRR.** Pre-fix numbers. The report to GRR is written from the
> final pipeline (CC finish bundle) with the metrics in `workplace_mirror/DESIGN_REVIEW.md`,
> "A1 final report: metrics". Kept as a working draft.

**Scope:** collections customers at 60–180 days past due, credit cards (`cc_60_180`, 19,292 accounts)
and retail loans (`rl_60_180`, 3,985 accounts), as of 31 August 2026. The numbers come from the
production run, recomputed independently: 0 differences on 152,658 account-months.
**Status:** initial results, before the fixes in section 5. The final report follows the next release.

---

## 1. What A1 measures

**Does the customer have the means to pay?** This is separate from whether we can reach them (A2)
or whether they will pay (A3). The answer comes only from money we can see: salary, bank-account
balances and payments, and failed payments.

| Signal | Points | Rule (window = the observation month and the 2 before it) |
|---|---|---|
| Income | Stable 2 · Weak 1 · None 0 | Stable: salary ≥ max(AED 3,000, 2 × the amount due) in 2 of 3 months and not falling more than 25%. Weak: any month ≥ AED 1,000 |
| Liquidity | Adequate 2 · Weak 1 · None 0 | Adequate: account balance ≥ max(AED 3,000, the amount due) in 2 of 3 months and not falling more than 50%, or a payment of the amount due from another bank's card. Weak: any month ≥ AED 1,000 |
| Distress | one level down | a returned cheque or a failed direct debit, at the bank or in the credit bureau |

**State:** High = 4 points, no distress · Moderate = 2–3 points, or 4 with distress · Low =
everything else · Unknown = we cannot see the customer's money (0 points, no distress, no
active current / savings account).

"The amount due" is the oldest overdue instalment for cards and one monthly instalment for loans.
Salary and account activity are read across all of the customer's accounts, not only the
delinquent one.

---

## 2. Results

| State | Credit cards | Retail loans |
|---|---|---|
| High | 8 (0.04%) | 1 (0.03%) |
| Moderate | 204 (1.1%) | 56 (1.4%) |
| Low | 6,984 (36.2%) | 3,566 (89.5%) |
| Unknown | 12,096 (62.7%) | 362 (9.1%) |

The mix is stable over the 8 months from January to August 2026: card Unknown 61–65% and Low 33–37%;
loan Low 86–92%.

---

## 3. Why each state fires

- **High (9 accounts):** a stable salary and an adequate balance together, with no failed payment.
  Stable salary alone: 42 card and 6 loan accounts.
- **Moderate:** most have an adequate balance but no income we can see (cards 109 of 204, loans 26 of
  56). Few have a stable salary without a balance (18 / 3).
- **Low** — mostly accounts where we see a bank account but no salary and no balance:

  | Low accounts | Cards | Loans |
  |---|---|---|
  | 0 points, account active, no distress | 4,752 (68%) | 2,521 (71%) |
  | 0 points, with distress | 1,712 (24.5%) | 672 (19%) |
  | 1 point | 466 | 349 |
  | 2–3 points pulled down by distress | 54 | 24 |

- **Unknown:** cards — 53% hold no current / savings account with us, 47% hold a dormant one;
  loans — 83% / 17%.

---

## 4. What information is missing

**Income is missing for almost everyone:** 98.5% of card accounts and 97.4% of loan accounts.

| Reason | Cards | Loans |
|---|---|---|
| No salary seen in 24 months | 53.6% | 20.2% |
| A salary, but older than the window (stopped) | 45.8% | 75.8% |
| Median age of the last salary, bank / bureau | 8 / 12 months | 7 / 15 months |
| Customers with salary from: bank only · bureau only · both · neither | 46.9 · 0.06 · 0.12 · 53.0% | 28.8 · 7.9 · 45.5 · 17.8% |

"Older than the window" means no salary in the observation month and the 2 months before it (3 at
60–180 days past due, 6 at 180+); it says nothing about when the customer became delinquent.

**Liquidity is missing because balances are low, not for lack of a relationship:** 97.2% of card
accounts and 90.9% of loan accounts have no liquidity points. Of these, 11,721 card / 2,841 loan
accounts hold an account that stays under AED 1,000, and 7,033 / 782 hold none.

**Bureau salary does not reach us yet.** 94% of card customers and 96% of loan customers have a
credit-bureau record, but our link from a bureau file to the customer works for only 0.6% / 3.4% of
them. Where the link works, 62–78% have a reported salary. Up to 86% of card accounts and 39% of loan
accounts have no income, a bureau record and no bureau salary: this is the most a working bureau
salary feed could fill. Loans already get bureau salary from the loan-application bureau pull.

**Distress:** 9.4% of card and 15.8% of loan customers had a returned cheque or failed direct debit
in the window, split about evenly between bank direct debits, bank cheques and the bureau. A third
of the bureau flags (35% / 43%) repeat a bounce already reported in an earlier pull; these will be
counted once.

---

## 5. What changes next (decided, in the next release)

| Change | Why | Effect (31 Aug, accounts) |
|---|---|---|
| **Salary dating fix** | Bank salary was dated one month early, so the latest month never counted | cards Low→Moderate 80, Moderate→High 20; loans 32 / 6 |
| **Window-total salary rule** | Early salary payments put two salaries in one month and none in the next; Stable now uses the window's total (≥ 2 × the threshold) | with the fix above: cards 101 / 28, loans 41 / 8 |
| **Activity gate on customer-initiated movement** | An account counted as "active" when the only movement was the bank collecting the loan instalment, a transfer between the customer's own accounts, or a fee. A dormant account says nothing about ability, so it becomes Unknown | cards Low→Unknown 1,058–2,171 (15–31% of Low); loans Low 89.5% → about 45–60% |
| **Bureau link** | Under investigation; the fix lets bureau salary reach the customer | not sized yet |
| **Repeated bureau bounces counted once** | The same bounce reappears in later pulls | fewer bureau distress flags |
| **End-of-service notes** (DCORE: benefit expected / received) | Shown beside the state, no effect on it; the money counts once it reaches the account | 292 card / 175 loan accounts |

Expected outcome: cards about 68–74% Unknown and 24–30% Low; loans about 40–55% Unknown and
45–60% Low, with High and Moderate a little larger in both. Moving Low to Unknown is deliberate:
**Low should mean "we see an account the customer uses, and money never stays in it"**, not "we
see no money at all".

---

## 6. What we need from GRR

1. **A frequent, CIF-linked bureau salary feed.** It is the only way to fill the income gap: about a
   third of card customers have no account with us, and half never had a salary with us.
2. **The bureau bounced-cheque amount:** is it one cheque, or the total of open bounces? This decides
   how a repeat is recognised.
3. **Agreement on the activity rule** in section 5: which account movements count as the customer
   using the account.
