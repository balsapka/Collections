# UC2 persona signals: final columns (rows 56–98)

The signals that ship next to the four persona states (rows 6–9 of the bank's output table), one row per customer, account and observation date. Source of truth: `uc2_signals_output_schema_v2.md` (same content in the bank's tab format, with the change list and the mapping to the code columns). Decisions behind it: user, 2026-11-16.

## How to read the columns

- **Period:** "the period" means the observation month and the 2 months before it for accounts at
  61–180 DPD, or the observation month and the 5 before it at 180+. "The period before" means the
  same number of months just before that. These are calendar months.
- **Scope:** SF_1, SF_3 and the call columns of SF_2 describe this account. The SF_2 location
  columns and all of SF_4 describe the customer: every account they hold with us.
- **Blanks:**
  - a blank date means no such event in our data;
  - a blank level means there is no data for that signal;
  - if every column of one feature is blank, that feature could not be scored for this row.
- **Flags:** 1 = yes, 0 = no.
- **Two contact dates:**
  - `SF_2_last_call_connected_date`: a call got through. It decides reachability.
  - `SF_3_last_customer_contact_date`: the customer was reached and an outcome was recorded. It
    covers calls and logged notes, in this delinquency only.
- **Amounts:** in AED. `SF_4_amount_due_aed` is the yardstick for ability. "The strong amount"
  is the larger of AED 3,000 and twice `SF_4_amount_due_aed` (AED 3,000 alone when that column
  is blank).
- **As of:** every value is as of the observation date (row 3), not today. "The collection
  system" is DCORE.

## Context

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 56 | `dpd_bucket` | string | `91-120` | DPD range on the latest statement (cards) or month-end loan record (loans) in the observation month, in days: 61-90 / 91-120 / 121-150 / 151-180, then 181-210 / 211+ for cards and 181+ for loans. Our reference value; the collection system's live bucket can be higher by the days since that statement. Blank if the account has no usable payment history |

## SF_1 Deterioration: how the account fell behind

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 57 | `SF_1_months_before_delinquency` | numeric | `18` | Months of payment history we can see before the current delinquency began (earlier delinquencies included). Short = early-life default; long = seasoned customer. Card history starts in Jan 2024, so cards top out at about 34; 0 = the delinquency began before our history does |
| 58 | `SF_1_prior_delinquency_count` | numeric | `1` | Earlier delinquencies on this account in the visible history, after it had come back to current. Not counted: 1–2 month slips that never went past 30 DPD |
| 59 | `SF_1_months_paid_in_delinquency` | numeric | `2` | Months since this delinquency began in which the account did not get worse, i.e. the customer paid about a month's due or more. 0 = never paid enough to stop the roll (small partial payments may still have come in). Months at the top bucket (cards 211+, loans 181+) are not counted |
| 60 | `SF_1_months_since_61_dpd` | numeric | `5` | Months since the account first reached 61+ DPD in this delinquency (0 = this month). If the delinquency began before our history starts, it counts from the first month we can see |
| 61 | `SF_1_reopened_in_delinquency_flag` | numeric | `0` | 1 = this account was opened while already delinquent: a restructured loan we could not link to its original loans, or a card whose first statement was already 61+ DPD. Its earlier history is missing, so SF_1 is less certain. A restructured loan linked to its originals is 0 |

## SF_2 Locatability: where the customer is and whether we can reach them

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 62 | `SF_2_location_reason` | string | `uae_recent` | Why the location part of SF_2 is what it is. abroad_latest: the most recent evidence (any age) puts the customer abroad. travelled_then_quiet: a travel purchase, at most 3 months of UAE evidence after it, and none in the last month. uae_recent: UAE evidence in the period. uae_too_old: UAE evidence exists but is older than the period. no_evidence: none at all |
| 63 | `SF_2_last_uae_date` | YYYY-MM-DD | `2026-11-12` | Latest date we have evidence the customer was in the UAE: a login from the UAE, or a card used in person there (shop terminal or ATM), on any of their accounts. Blank if none |
| 64 | `SF_2_last_uae_source` | string | `login` | What that evidence was: login / debit_card / credit_card (card used in person). Blank if none |
| 65 | `SF_2_last_foreign_date` | YYYY-MM-DD | `2026-03-04` | Latest date we have evidence the customer was abroad, on any of their accounts. Blank if none |
| 66 | `SF_2_last_foreign_source` | string | `credit_card` | What that evidence was: login / debit_card / credit_card (card used in person abroad) / collector_note (a collector recorded that the customer left the country). Blank if none |
| 67 | `SF_2_last_travel_date` | YYYY-MM-DD | `2026-10-20` | Latest travel purchase (airline, travel agency, cruise) on any of the customer's cards. A sign of a possible trip, not proof the customer left. Blank if none |
| 68 | `SF_2_recent_travel_purchase_flag` | numeric | `1` | 1 = a travel purchase in the period. An early warning of a possible departure, raised before the location state changes to Skip |
| 69 | `SF_2_last_call_connected_date` | YYYY-MM-DD | `2026-11-02` | Latest call on this account that got through: the customer called in, or a collector's call was answered by the customer. Decides reachability: a connected call in the period = Reachable. Non-Reachable = the last 3 call days (6 at 180+) all failed, all inside the period, with no connected call since. Blank if no call ever got through |
| 70 | `SF_2_last_call_attempt_date` | YYYY-MM-DD | `2026-11-25` | Latest day a collector called this account, whatever the outcome. Blank if never called |
| 71 | `SF_2_call_attempt_days_recent` | numeric | `6` | Number of days a collector called this account in the period. 0 = no calls |
| 72 | `SF_2_last_skip_trace_date` | YYYY-MM-DD | `2026-09-10` | Latest date the collection system recorded the customer as being traced or traced (skip trace = searching for a customer who cannot be reached). Blank if never |

## SF_3 Payment credibility: promises, payments and contacts

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 73 | `SF_3_main_reason` | string | `promises` | Which evidence lifted payment credibility most: promises / payments_while_overdue / record_before_delinquency, or refusal (the latest contact was a refusal to pay, which lowers the state one level, no further than Low). Blank = no positive evidence (state Low or Unknown) |
| 74 | `SF_3_delinquency_start_date` | YYYY-MM-DD | `2026-06-01` | First day of the month the account first fell overdue (1+ DPD) in its current delinquency. Blank = no delinquency history available (credibility Unknown). If our history starts mid-delinquency, the true start is earlier |
| 75 | `SF_3_promise_level` | string | `kept` | Promises to pay and payment plans made in the observation month and the 11 before, judged once their deadline has passed. Deadline: cards at 61–180 DPD = next statement; loans and everything at 180+ = end of the month the promise was made. kept = 2+ judged and 80%+ paid in full / broken = the last 3 all not paid in full, or 2+ judged and under 40% paid / partly_kept = at least one paid in full otherwise / thin = none paid in full, or no promises |
| 76 | `SF_3_promises_judged_count` | numeric | `4` | Promises made in the observation month and the 11 before whose deadline has passed (see SF_3_promise_level) |
| 77 | `SF_3_promises_kept_count` | numeric | `3` | Of those, promises paid in full by their deadline. Partial payments do not count |
| 78 | `SF_3_open_promise_flag` | numeric | `0` | 1 = a promise to pay or payment plan is still running at the observation date: made on or before it, deadline after it, not yet paid in full. Chasing it before the deadline can break a working promise |
| 79 | `SF_3_open_promise_deadline_date` | YYYY-MM-DD | `2026-12-15` | Deadline of that running promise (cards at 61–180 DPD: next statement; loans and everything at 180+: end of the month the promise was made). Blank if none is running |
| 80 | `SF_3_payment_while_overdue_level` | string | `some` | Payments since the account fell behind. regular = the full monthly due (at least AED 100) paid in 2 of the last 3 months (3 of the last 6 at 180+) / some = a month with AED 100+ paid in the last 3 months (12 at 180+) / none = neither |
| 81 | `SF_3_record_before_delinquency_level` | string | `clean` | Payment record in the 12 months before this delinquency. clean = 80%+ of the statements / instalments in that year paid in full / not_clean = below that / no_record = fewer than 3 bills in that year, or the start of the delinquency is not visible |
| 82 | `SF_3_last_payment_date` | YYYY-MM-DD | `2026-11-10` | Latest payment to this account on or before the observation date, any amount (loans: the month end of the month the cash came in). Blank if none in our payment data |
| 83 | `SF_3_last_payment_aed` | numeric | `1500` | Total paid on that date (loans: in that month), AED. Blank if none |
| 84 | `SF_3_last_customer_contact_date` | YYYY-MM-DD | `2026-11-02` | Latest date the collection system shows the customer was reached personally (by call or a logged note, e.g. a promise or payment report) during this delinquency, at most 24 months back. Blank if none |
| 85 | `SF_3_last_customer_contact_outcome` | string | `promise_to_pay` | Outcome of that contact: promise_to_pay / payment_reported / refusal / dispute / hung_up / reached (spoke to the customer, no specific outcome). Blank if no contact |
| 86 | `SF_3_refusal_flag` | numeric | `0` | 1 = the customer's latest contact was a refusal to pay, and no plan or payment of AED 100+ has come since (a payment on the same day lifts it). Lowers payment credibility one level |
| 87 | `SF_3_no_answer_since_contact_flag` | numeric | `1` | 1 = since the latest contact, collector calls went unanswered on 3+ days (6+ at 180+) and the number is not recorded as wrong or dead. The customer may be avoiding calls |

## SF_4 Ability: income, money and other products

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 88 | `SF_4_main_reason` | string | `income` | Which evidence lifted ability most: income / money_in / spending / other_products, or distress (a returned cheque, rejected direct debit or bureau bounce in the period, which lowers the state one level). Blank = no strong evidence (state Low or Unknown) |
| 89 | `SF_4_income_level` | string | `stable` | Salary over the period, from our records or the credit bureau, whichever is larger each month. stable = the total reaches 2 × the strong amount (3 × at 180+) and is no more than 25% below the period before / weak = some month with AED 1,000+ salary / none = no salary seen |
| 90 | `SF_4_money_in_level` | string | `strong` | Money other than salary coming into the customer's current / savings accounts with us, or held there. strong = the strong amount in 2 of the period's 3 months (3 of 6 at 180+), either as inflow or as balance held (balance not halved against the period before) / some = a month with AED 1,000+ in / none = less. Blank = no account activity data in the period |
| 91 | `SF_4_spending_level` | string | `some` | Money the customer spends or moves out of their accounts with us by choice: card and account spending, transfers to their own accounts at other banks. strong / some / none on the same amounts as SF_4_money_in_level. Blank = no account activity data in the period |
| 92 | `SF_4_other_products_level` | string | `none` | Other products the customer holds with us at the observation month end. strong = deposits / investments of at least the strong amount, or another loan / card that is up to date with an instalment of at least the larger of AED 1,000 and SF_4_amount_due_aed / some = any other up-to-date loan / card, or any deposit / investment / none = neither |
| 93 | `SF_4_distress_flag` | numeric | `0` | 1 = a returned cheque, a rejected direct debit, or a bounce reported by the credit bureau in the period. Lowers ability one level |
| 94 | `SF_4_income_source` | string | `internal` | Where salary of AED 1,000+ was seen in the period: internal (credited to an account with us) / bureau (reported by the credit bureau) / both / none |
| 95 | `SF_4_salary_stopped_flag` | numeric | `0` | 1 = salary credited to an account with us in the period before and none in the period. Possible job loss. Bureau salary is not considered |
| 96 | `SF_4_end_of_service_flag` | numeric | `0` | 1 = a collector recorded an end-of-service benefit (gratuity) as expected or received in the period: a lump sum may be coming |
| 97 | `SF_4_unknown_reason` | string | `no_account_activity_12m` | Why ability is Unknown. no_account_activity_12m = no current / savings account with movement or a positive balance with us in the last 12 months / inactive_account = such an account exists but had no counted transaction in the period. Blank when ability is not Unknown |
| 98 | `SF_4_amount_due_aed` | numeric | `2000` | Reference amount the customer must find now, AED. Cards: the oldest overdue amount on the statement (what stops the roll). Loans: one instalment. Not the total overdue. Blank at cards 180+, or with no statement / loan record that month; ability then uses its AED floors alone |

43 columns: the DPD range, 5 SF_1, 11 SF_2, 15 SF_3, 11 SF_4.
