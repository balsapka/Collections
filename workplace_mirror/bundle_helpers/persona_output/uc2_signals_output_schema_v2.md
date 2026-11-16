# UC2 persona signals: rows 56–95, revised for review

This draft applies the review in `uc2_schema_review.md`. It sits beside
`uc2_signals_output_schema.md` and does not replace it. Where a decision is still open, the row
uses the option the review recommends and the right-hand column says so (C1–C9 = the decisions
in the review).

## Header note (goes above row 56)

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

## Rows

```
field id	field	type	Example value	Desc
56	dpd_bucket	string	91-120	DPD range on the latest statement (cards) or month-end loan record (loans) in the observation month, in days: 61-90 / 91-120 / 121-150 / 151-180, then 181-210 / 211+ for cards and 181+ for loans. Our reference value; the collection system's live bucket can be higher by the days since that statement. Blank if the account has no usable payment history
57	SF_1_months_before_delinquency	numeric	18	months of payment history we can see before the current delinquency began (earlier delinquencies included). Short = early-life default; long = seasoned customer. Card history starts in Jan 2024, so cards top out at about 34; 0 = the delinquency began before our history does
58	SF_1_prior_delinquency_count	numeric	1	earlier delinquencies on this account in the visible history, after it had come back to current. Not counted: 1–2 month slips that never went past 30 DPD
59	SF_1_months_paid_in_delinquency	numeric	2	months since this delinquency began in which the account did not get worse, i.e. the customer paid about a month's due or more. 0 = never paid enough to stop the roll (small partial payments may still have come in). Months at the top bucket (cards 211+, loans 181+) are not counted
60	SF_1_months_since_61_dpd	numeric	5	months since the account first reached 61+ DPD in this delinquency (0 = this month). If the delinquency began before our history starts, it counts from the first month we can see
61	SF_1_reopened_in_delinquency_flag	numeric	0	1 = this account was opened while already delinquent: a restructured loan we could not link to its original loans, or a card whose first statement was already 61+ DPD. Its earlier history is missing, so SF_1 is less certain. A restructured loan linked to its originals is 0
62	SF_2_location_reason	string	uae_recent	why the location part of SF_2 is what it is. abroad_latest: the most recent evidence (any age) puts the customer abroad. travelled_then_quiet: a travel purchase, at most 3 months of UAE evidence after it, and none in the last month. uae_recent: UAE evidence in the period. uae_too_old: UAE evidence exists but is older than the period. no_evidence: none at all
63	SF_2_last_uae_date	YYYY-MM-DD	2026-11-12	latest date we have evidence the customer was in the UAE: a login from the UAE, or a card used in person there (shop terminal or ATM), on any of their accounts. Blank if none
64	SF_2_last_uae_source	string	login	what that evidence was: login / debit_card / credit_card (card used in person). Blank if none
65	SF_2_last_foreign_date	YYYY-MM-DD	2026-03-04	latest date we have evidence the customer was abroad, on any of their accounts. Blank if none
66	SF_2_last_foreign_source	string	credit_card	what that evidence was: login / debit_card / credit_card (card used in person abroad) / collector_note (a collector recorded that the customer left the country). Blank if none
67	SF_2_last_travel_date	YYYY-MM-DD	2026-10-20	latest travel purchase (airline, travel agency, cruise) on any of the customer's cards. A sign of a possible trip, not proof the customer left. Blank if none
68	SF_2_recent_travel_purchase_flag	numeric	1	1 = a travel purchase in the period. An early warning of a possible departure, raised before the location state changes to Skip
69	SF_2_last_call_connected_date	YYYY-MM-DD	2026-11-02	latest call on this account that got through: the customer called in, or a collector's call was answered by the customer. Decides reachability: a connected call in the period = Reachable. Non-Reachable = the last 3 call days (6 at 180+) all failed, all inside the period, with no connected call since. Blank if no call ever got through
70	SF_2_last_call_attempt_date	YYYY-MM-DD	2026-11-25	latest day a collector called this account, whatever the outcome. Blank if never called
71	SF_2_call_attempt_days_recent	numeric	6	number of days a collector called this account in the period. 0 = no calls
72	SF_2_last_skip_trace_date	YYYY-MM-DD	2026-09-10	latest date the collection system recorded the customer as being traced or traced (skip trace = searching for a customer who cannot be reached). Blank if never
73	SF_3_main_reason	string	promises	which evidence lifted payment credibility most: promises / payments_while_overdue / record_before_delinquency, or refusal (the latest contact was a refusal to pay, which lowers the state one level, no further than Low). Blank = no positive evidence (state Low or Unknown)
74	SF_3_delinquency_start_date	YYYY-MM-DD	2026-06-01	first day of the month the account first fell overdue (1+ DPD) in its current delinquency. Blank = no delinquency history available (credibility Unknown). If our history starts mid-delinquency, the true start is earlier
75	SF_3_promise_level	string	kept	promises to pay and payment plans made in the observation month and the 11 before, judged once their deadline has passed. Deadline: cards at 61–180 DPD = next statement; loans and everything at 180+ = end of the month the promise was made. kept = 2+ judged and 80%+ paid in full / broken = the last 3 all not paid in full, or 2+ judged and under 40% paid / partly_kept = at least one paid in full otherwise / thin = none paid in full, or no promises
76	SF_3_promises_judged_count	numeric	4	promises made in the observation month and the 11 before whose deadline has passed (see SF_3_promise_level)
77	SF_3_promises_kept_count	numeric	3	of those, promises paid in full by their deadline. Partial payments do not count
78	SF_3_payment_while_overdue_level	string	some	payments since the account fell behind. regular = the full monthly due (at least AED 100) paid in 2 of the last 3 months (3 of the last 6 at 180+) / some = a month with AED 100+ paid in the last 3 months (12 at 180+) / none = neither
79	SF_3_record_before_delinquency_level	string	clean	payment record in the 12 months before this delinquency. clean = 80%+ of the statements / instalments in that year paid in full / not_clean = below that / no_record = fewer than 3 bills in that year, or the start of the delinquency is not visible
80	SF_3_last_customer_contact_date	YYYY-MM-DD	2026-11-02	latest date the collection system shows the customer was reached personally (by call or a logged note, e.g. a promise or payment report) during this delinquency, at most 24 months back. Blank if none
81	SF_3_last_customer_contact_outcome	string	promise_to_pay	outcome of that contact: promise_to_pay / payment_reported / refusal / dispute / hung_up / reached (spoke to the customer, no specific outcome). Blank if no contact
82	SF_3_refusal_flag	numeric	0	1 = the customer's latest contact was a refusal to pay, and no plan or payment of AED 100+ has come since (a payment on the same day lifts it). Lowers payment credibility one level
83	SF_3_dispute_flag	numeric	0	1 = the latest contact was a dispute (the customer contests the debt). Rows 20–25 give the call-transcript view
84	SF_3_no_answer_since_contact_flag	numeric	1	1 = since the latest contact, collector calls went unanswered on 3+ days (6+ at 180+) and the number is not recorded as wrong or dead. The customer may be avoiding calls
85	SF_4_main_reason	string	income	which evidence lifted ability most: income / money_in / spending / other_products, or distress (a returned cheque, rejected direct debit or bureau bounce in the period, which lowers the state one level). Blank = no strong evidence (state Low or Unknown)
86	SF_4_income_level	string	stable	salary over the period, from our records or the credit bureau, whichever is larger each month. stable = the total reaches 2 × the strong amount (3 × at 180+) and is no more than 25% below the period before / weak = some month with AED 1,000+ salary / none = no salary seen
87	SF_4_money_in_level	string	strong	money other than salary coming into the customer's current / savings accounts with us, or held there. strong = the strong amount in 2 of the period's 3 months (3 of 6 at 180+), either as inflow or as balance held (balance not halved against the period before) / some = a month with AED 1,000+ in / none = less. Blank = no account activity data in the period
88	SF_4_spending_level	string	some	money the customer spends or moves out of their accounts with us by choice: card and account spending, transfers to their own accounts at other banks. strong / some / none on the same amounts as SF_4_money_in_level. Blank = no account activity data in the period
89	SF_4_other_products_level	string	none	other products the customer holds with us at the observation month end. strong = deposits / investments of at least the strong amount, or another loan / card that is up to date with an instalment of at least the larger of AED 1,000 and SF_4_amount_due_aed / some = any other up-to-date loan / card, or any deposit / investment / none = neither
90	SF_4_distress_flag	numeric	0	1 = a returned cheque, a rejected direct debit, or a bounce reported by the credit bureau in the period. Lowers ability one level
91	SF_4_income_source	string	internal	where salary of AED 1,000+ was seen in the period: internal (credited to an account with us) / bureau (reported by the credit bureau) / both / none
92	SF_4_salary_stopped_flag	numeric	0	1 = salary credited to an account with us in the period before and none in the period. Possible job loss. Bureau salary is not considered
93	SF_4_end_of_service_flag	numeric	0	1 = a collector recorded an end-of-service benefit (gratuity) as expected or received in the period: a lump sum may be coming
94	SF_4_unknown_reason	string	no_account_activity_12m	why ability is Unknown. no_account_activity_12m = no current / savings account with movement or a positive balance with us in the last 12 months / inactive_account = such an account exists but had no counted transaction in the period. Blank when ability is not Unknown
95	SF_4_amount_due_aed	numeric	2000	reference amount the customer must find now, AED. Cards: the oldest overdue amount on the statement (what stops the roll). Loans: one instalment. Not the total overdue. Blank at cards 180+, or with no statement / loan record that month; ability then uses its AED floors alone
```

## Changes against `uc2_signals_output_schema.md`

| id | old field | new field | change | depends on |
|---|---|---|---|---|
| 56 | `dpd_bucket` | same | loan top bucket `181+`; statement date; blank case | C8 |
| 57 | `SF_1_months_before_spell` | `SF_1_months_before_delinquency` | Desc was wrong (not clean history, not time on book) | C2, C9 |
| 58 | `SF_1_prior_episodes` | `SF_1_prior_delinquency_count` | blip rule completed | C2 |
| 59 | `SF_1_spell_pay_months` | `SF_1_months_paid_in_delinquency` | Desc was wrong (held or improved, not "paid something") | C2 |
| 60 | `SF_1_months_since_61_dpd` | same | 61+, visible-history caveat | — |
| 61 | `SF_1_history_gap_flag` | `SF_1_reopened_in_delinquency_flag` | narrow option: says what the flag really covers | **C1** |
| 62 | `SF_2_location_reason` | same | new value names; travel rule corrected | C3 |
| 63–65 | — | same | blank cases, all accounts | — |
| 66 | `SF_2_last_foreign_source` | same | `dcore` → `collector_note` (code: `dcore_note`) | C3 |
| 67 | — | same | blank case | — |
| 68 | `SF_2_travel_purchase_recent_flag` | `SF_2_recent_travel_purchase_flag` | period defined | C2 |
| 69 | `SF_2_last_contact_date` | `SF_2_last_call_connected_date` | Non-Reachable rule completed | C2 |
| 70 | `SF_2_last_attempt_date` | `SF_2_last_call_attempt_date` | — | C2 |
| 71 | `SF_2_attempt_days_in_window` | `SF_2_call_attempt_days_recent` | — | C2 |
| 73 | `SF_3_reason` | `SF_3_main_reason` | new values; blank meaning corrected | C2, C3, C5 |
| 74 | `SF_3_episode_start` | `SF_3_delinquency_start_date` | example and Desc were wrong | C2 |
| 75–77 | `SF_3_commitments_*` | `SF_3_promise_level`, `SF_3_promises_judged_count`, `SF_3_promises_kept_count` | deadline rule and window spelled out | C2 |
| 78 | `SF_3_dlq_payment_level` | `SF_3_payment_while_overdue_level` | 180+ rule and "some" window were wrong / missing | C2 |
| 79 | `SF_3_pre_dlq_payment_level` | `SF_3_record_before_delinquency_level` | no_record cases | C2 |
| 80–81 | `SF_3_last_rpc_date`, `_disposition` | `SF_3_last_customer_contact_date`, `_outcome` | window; values `promise_to_pay` / `payment_reported` / `reached` | C2, C3 |
| 82 | `SF_3_refusal_flag` | same | "latest contact" scope added; cast to 0/1 | C4 |
| 83 | `SF_3_dispute_flag` | same | kept for now; cast to 0/1 | C4, **C6** |
| 84 | `SF_3_no_pickup_after_contact` | `SF_3_no_answer_since_contact_flag` | threshold added; cast to 0/1 | C2, C4 |
| 85 | `SF_4_reason` | `SF_4_main_reason` | new values; blank meaning | C2, C3 |
| 86 | `SF_4_income_level` | same | threshold was wrong | — |
| 87 | `SF_4_money_in_level` | same | salary excluded; thresholds; blank | — |
| 88 | `SF_4_money_out_level` | `SF_4_spending_level` | thresholds; blank | C2 |
| 89 | `SF_4_cross_product_level` | `SF_4_other_products_level` | thresholds | C2 |
| 90–92 | — | same | period defined | — |
| 93 | `SF_4_eosb_flag` | `SF_4_end_of_service_flag` | — | C2 |
| 94 | `SF_4_unknown_reason` | same | values `no_account_activity_12m` / `inactive_account`; Desc was wrong | C3 |
| 95 | `SF_4_amount_due_now` | `SF_4_amount_due_aed` | blank cases; "not the total overdue" | C2 |

Not in this draft (open, C7): `SF_3_open_promise_flag` / `SF_3_open_promise_deadline_date`,
`SF_3_last_payment_date` / `SF_3_last_payment_aed`.

## Code column → output field (for the persona master)

| Axis column | Output field | Transform |
|---|---|---|
| `current_bucket` | `dpd_bucket` | cards: 4 → 61-90, 5 → 91-120, 6 → 121-150, 7 → 151-180, 8 → 181-210, 9 → 211+; loans (native): 3 → 61-90 … 6 → 151-180, 7 → 181+ |
| `months_before_spell` | `SF_1_months_before_delinquency` | — |
| `n_prior_episodes` | `SF_1_prior_delinquency_count` | — |
| `spell_pay_events` | `SF_1_months_paid_in_delinquency` | — |
| `months_since_4` | `SF_1_months_since_61_dpd` | — |
| `restructure_blind_spot_flag` | `SF_1_reopened_in_delinquency_flag` | — |
| `location_rule` + `location_unknown_reason` | `SF_2_location_reason` | L1 → abroad_latest, L2 → travelled_then_quiet, L3 → uae_recent, L4 + domestic_before_window → uae_too_old, L4 + no_evidence → no_evidence |
| `last_uae_date`, `last_uae_source`, `last_foreign_date` | rows 63–65 | — |
| `last_foreign_source` | `SF_2_last_foreign_source` | dcore_note → collector_note |
| `last_travel_date` | `SF_2_last_travel_date` | — |
| `last_travel_date` | `SF_2_recent_travel_purchase_flag` | 1 if ≥ first day of the month 2 (5 at 180+) months before the observation month |
| `last_contact_date` | `SF_2_last_call_connected_date` | — |
| `last_attempt_date` | `SF_2_last_call_attempt_date` | — |
| `attempt_days_in_window` | `SF_2_call_attempt_days_recent` | — |
| `last_skip_trace_date` | `SF_2_last_skip_trace_date` | — |
| `a3_reason` | `SF_3_main_reason` | commitments → promises, dlq_payments → payments_while_overdue, pre_dlq_record → record_before_delinquency; blank when SF_3 = Unknown |
| `episode_start` | `SF_3_delinquency_start_date` | — |
| `a3_commitments_level`, `commitments_concluded`, `commitments_kept` | rows 75–77 | — |
| `a3_dlq_payment_level` | `SF_3_payment_while_overdue_level` | — |
| `a3_pre_dlq_payment_level` | `SF_3_record_before_delinquency_level` | — |
| `last_rpc_date` | `SF_3_last_customer_contact_date` | — |
| `last_rpc_disposition` | `SF_3_last_customer_contact_outcome` | ptp → promise_to_pay, paid → payment_reported, success → reached |
| `a3_refusal_flag`, `a3_dispute_flag`, `a3_no_pickup_after_contact` | rows 82–84 | boolean → 0/1 |
| `a1_reason` | `SF_4_main_reason` | money_out → spending, cross_product → other_products |
| `a1_income_level`, `a1_money_in_level` | rows 86–87 | — |
| `a1_money_out_level` | `SF_4_spending_level` | — |
| `a1_cross_product_level` | `SF_4_other_products_level` | — |
| `a1_distress_flag`, `a1_income_source`, `a1_salary_stopped` | rows 90–92 | — |
| `a1_eosb_flag` | `SF_4_end_of_service_flag` | — |
| `a1_unknown_reason` | `SF_4_unknown_reason` | no_casa → no_account_activity_12m, dormant_casa → inactive_account |
| `liquidity_anchor_amt` | `SF_4_amount_due_aed` | — |
