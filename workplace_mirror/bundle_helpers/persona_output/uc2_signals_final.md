# UC2 persona signals: final columns (rows 56–87)

The signals that ship next to the four persona states (rows 6–9 of the bank's output table), one row per customer, account and observation date. Only what our models compute: anything the collection system (DCORE) already shows is left out. Source of truth: `uc2_signals_output_schema_v2.md` (same content in the bank's tab format, with the change list and the mapping to the code columns). Decisions: user, 2026-11-16.

## How to read the columns

- **Period:** "the period" means the observation month and the 2 months before it for accounts at
  61–180 DPD, or the observation month and the 5 before it at 180+. "The period before" means the
  same number of months just before that. These are calendar months.
- **Scope:** SF_1, SF_3 and SF_2 reachability describe this account. SF_2 location and SF_4
  describe the customer: every account they hold with us.
- **Blanks:**
  - a blank date means no such event in our data;
  - a blank level means there is no data for that signal;
  - when a state is Unknown, its levels still show what was seen (mostly none / 0).
- **Flags:** 1 = yes, 0 = no.
- **Not repeated here:** what the collection system (DCORE) already shows: DPD bucket, amounts
  owed, calls and their outcomes, live promises to pay, payments, skip trace. These columns add
  what our models compute on top of it.
- **Amounts:** in AED. Ability thresholds scale with the amount due (as in DCORE: cards at
  61–180 DPD, the oldest overdue amount; loans, one instalment; cards at 180+, none). "The strong
  amount" is the larger of AED 3,000 and twice the amount due (AED 3,000 alone when there is none).
- **As of:** every value is as of the observation date (row 3), not today. "The collection
  system" is DCORE.

## SF_1 Deterioration: how the account fell behind

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 56 | `SF_1_months_before_delinquency` | numeric | `18` | Months of our history before this delinquency began. 0 = it began before our history (cards: from Jan 2024) |
| 57 | `SF_1_prior_delinquency_count` | numeric | `1` | Earlier delinquencies that ended with the account up to date. Counted if 31+ DPD or 3+ months overdue; depth not shown |
| 58 | `SF_1_months_paid_in_delinquency` | numeric | `2` | Months in this delinquency in which the account did not get worse (about a month's due or more paid; months at the top bucket not counted) |
| 59 | `SF_1_months_since_61_dpd` | numeric | `5` | Months since the account first reached 61+ DPD in this delinquency |

## SF_2 Locatability: where the customer is and whether we reach them

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 60 | `SF_2_location_reason` | string | `uae_recent` | abroad_latest (latest evidence is abroad) / travelled_then_quiet (travel purchase, no UAE evidence later than 3 months after it, none in the last month) / uae_recent (UAE evidence in the period) / uae_too_old / no_evidence |
| 61 | `SF_2_reachability_reason` | string | `call_connected` | call_connected (a call got through in the period) / calls_failing (last 3 call days, 6 at 180+, all failed in the period, none connected since) / no_recent_connection (no connected call in the period) / no_calls (no collection-system activity) |
| 62 | `SF_2_last_uae_date` | YYYY-MM-DD | `2026-11-12` | Latest evidence of being in the UAE: a UAE login or a card used in person there. Blank = none |
| 63 | `SF_2_last_uae_source` | string | `login` | login / debit_card / credit_card |
| 64 | `SF_2_last_foreign_date` | YYYY-MM-DD | `2026-03-04` | Latest evidence of being abroad. Blank = none |
| 65 | `SF_2_last_foreign_source` | string | `credit_card` | login / debit_card / credit_card / collector_note (departure noted by a collector) |
| 66 | `SF_2_last_travel_date` | YYYY-MM-DD | `2026-10-20` | Latest travel purchase (airline, travel agency, cruise). Blank = none |
| 67 | `SF_2_recent_travel_purchase_flag` | numeric | `1` | 1 = travel purchase in the period (early warning of a departure) |

## SF_3 Payment credibility: promises and payments

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 68 | `SF_3_main_reason` | string | `promises` | What set the state most: promises / payments_while_overdue / record_before_delinquency / refusal. Blank = no positive evidence |
| 69 | `SF_3_promise_level` | string | `kept` | kept / partly_kept / broken / thin (0–1 judged, none kept), from the promise counts below |
| 70 | `SF_3_promises_judged_count` | numeric | `4` | Promises and plans of the last 12 months whose deadline has passed; repeats before the deadline count once (deadline: cards 61–180 next statement, else month end) |
| 71 | `SF_3_promises_kept_count` | numeric | `3` | Of those, the monthly due (min AED 100) paid by the deadline |
| 72 | `SF_3_promises_partly_paid_count` | numeric | `1` | Of those, AED 100+ paid but less than the monthly due |
| 73 | `SF_3_promises_broken_count` | numeric | `0` | Of those, not paid |
| 74 | `SF_3_last_3_promises_not_kept_flag` | numeric | `0` | 1 = none of the last 3 judged promises was kept |
| 75 | `SF_3_full_due_paid_months` | numeric | `1` | Months in the period, since falling behind, with the full monthly due (min AED 100) paid |
| 76 | `SF_3_payment_while_overdue_level` | string | `some` | regular (full due paid in 2 months of the period, 3 at 180+) / some (AED 100+ paid in a month of the period; at 180+, of the last 12 months) / none |
| 77 | `SF_3_record_before_delinquency_level` | string | `clean` | clean (monthly due, for cards the minimum, paid in 80%+ of billed months in the 12 months before this delinquency) / not_clean / no_record (under 3 bills, or start not visible) |
| 78 | `SF_3_refusal_flag` | numeric | `0` | 1 = latest contact was a refusal, with no plan or AED 100+ payment since |

## SF_4 Ability: income, money and other products

| # | Column | Type | Example | Meaning |
|---:|---|---|---|---|
| 79 | `SF_4_main_reason` | string | `income` | What set the state most: income / money_in / spending / other_products / distress. Blank = nothing strong |
| 80 | `SF_4_income_level` | string | `stable` | stable (period salary ≥ 2 × the strong amount, 3 × at 180+, and not more than 25% below the period before) / weak (a month with AED 1,000+) / none |
| 81 | `SF_4_money_in_level` | string | `strong` | Non-salary money into or held in accounts with us: strong (the strong amount in 2 of 3 months, 3 of 6 at 180+, as inflow or balance held) / some (a month with AED 1,000+) / none. Blank = no data |
| 82 | `SF_4_spending_level` | string | `some` | Money spent or moved out by choice, same scale as money in. Blank = no data |
| 83 | `SF_4_other_products_level` | string | `none` | strong (deposits / investments ≥ the strong amount, or an up-to-date loan / card with instalment ≥ max(AED 1,000, amount due)) / some (any deposit / investment, or any up-to-date loan / card) / none |
| 84 | `SF_4_distress_flag` | numeric | `0` | 1 = returned cheque, rejected direct debit or a bounced payment reported by the credit bureau in the period |
| 85 | `SF_4_income_source` | string | `internal` | Where salary of AED 1,000+ was seen in the period: internal / bureau / both / none |
| 86 | `SF_4_salary_stopped_flag` | numeric | `0` | 1 = salary with us in the period before, none in the period |
| 87 | `SF_4_unknown_reason` | string | `no_account_activity_12m` | no_account_activity_12m / inactive_account (account with us, no transaction in the period). Blank unless Ability is Unknown |

## Deriving the states

- **SF_1** is not derivable from these columns: the journey tree reads about eight history
  features (`docs/deterioration_states/METHODOLOGY.md`).
- **SF_2:** Deceased overrides everything (shown in SF_2 itself). Otherwise location × reachability.
  Location: abroad_latest or travelled_then_quiet = Skip, uae_recent = In Country, else Unknown.
  Reachability: call_connected = Reachable, calls_failing = Non-Reachable, else Unknown.
- **SF_3:** Unknown when SF_1 was not scored for the row. Otherwise points:
  - promise level: kept 2, partly_kept 1, broken −1, thin 0;
  - payment while overdue: regular 2, some 1, none 0;
  - record before delinquency: clean 1, else 0.

  High from 4, Moderate from 2, else Low. `SF_3_refusal_flag` = 1 moves the state one level down
  (not below Low). Promise level from the counts, first match: broken if the last-3 flag is 1, or 2+ judged and
  under 40% kept; kept if 2+ judged and 80%+ kept; partly_kept if 1+ kept; else thin. Partly paid
  counts as not kept.
- **SF_4:** stable income or a strong family = 2 points each. High from 4, Moderate from 2, else
  Low; `SF_4_distress_flag` = 1 moves it one level down (not below Low). Unknown when
  `SF_4_unknown_reason` is filled: every level none or blank, no distress, no account activity in
  the period.

32 columns: 4 SF_1, 8 SF_2, 11 SF_3, 9 SF_4.
