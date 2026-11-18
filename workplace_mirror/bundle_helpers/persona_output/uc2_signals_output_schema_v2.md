# UC2 persona signals: rows 56–85, revised for review

This draft applies the review in `uc2_schema_review.md` and sits beside
`uc2_signals_output_schema.md` (unchanged). The user accepted the review's recommendation for every
open question (C1–C9, 2026-11-16); they are listed under "Decided" at the end. Then cut to what our models compute: anything a collector already sees in DCORE (DPD bucket,
amounts owed, calls and their outcomes, live promises, payments, skip trace, end-of-service notes)
is left out (user, 2026-11-16). 30 columns: 3 SF_1, 8 SF_2, 10 SF_3, 9 SF_4 (the last-3 flag went with the Broken level, D-A3-34, 2026-11-18).

## Header note (goes above row 56)

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

## Rows

```
field id	field	type	Example value	Desc
56	SF_1_months_before_delinquency	numeric	18	Months of our history before this delinquency began. 0 = it began before our history (cards: from Jan 2024)
57	SF_1_prior_delinquency_count	numeric	1	Earlier delinquencies that ended with the account up to date. Counted if 31+ DPD or 3+ months overdue; depth not shown
58	SF_1_months_since_61_dpd	numeric	5	Months since the account first reached 61+ DPD in this delinquency
59	SF_2_location_reason	string	uae_recent	abroad_latest (latest evidence is abroad) / travelled_then_quiet (travel purchase, no UAE evidence later than 3 months after it, none in the last month) / uae_recent (UAE evidence in the period) / uae_too_old / no_evidence
60	SF_2_reachability_reason	string	call_connected	call_connected (a call got through in the period) / calls_failing (last 3 call days, 6 at 180+, all failed in the period, none connected since) / no_recent_connection (no connected call in the period) / no_calls (no collection-system activity)
61	SF_2_last_uae_date	YYYY-MM-DD	2026-11-12	Latest evidence of being in the UAE: a UAE login or a card used in person there. Blank = none
62	SF_2_last_uae_source	string	login	login / debit_card / credit_card
63	SF_2_last_foreign_date	YYYY-MM-DD	2026-03-04	Latest evidence of being abroad. Blank = none
64	SF_2_last_foreign_source	string	credit_card	login / debit_card / credit_card / collector_note (departure noted by a collector)
65	SF_2_last_travel_date	YYYY-MM-DD	2026-10-20	Latest travel purchase (airline, travel agency, cruise). Blank = none
66	SF_2_recent_travel_purchase_flag	numeric	1	1 = travel purchase in the period (early warning of a departure)
67	SF_3_main_reason	string	promises	What set the state most: promises / payments_while_overdue / record_before_delinquency / refusal. Blank = no positive evidence
68	SF_3_promise_level	string	kept	kept / partly_kept / promised (a promise in the last 12 months, none kept) / no_promise (no promise in the last 12 months)
69	SF_3_promises_judged_count	numeric	4	Promises and plans of the last 12 months whose deadline has passed; repeats before the deadline count once (deadline: cards 61–180 next statement, else month end)
70	SF_3_promises_kept_count	numeric	3	Of those, the monthly due (min AED 100) paid by the deadline
71	SF_3_promises_partly_paid_count	numeric	1	Of those, AED 100+ paid but less than the monthly due
72	SF_3_promises_broken_count	numeric	0	Of those, not paid
73	SF_3_full_due_paid_months	numeric	1	Months in the period, since falling behind, with the full monthly due (min AED 100) paid
74	SF_3_payment_while_overdue_level	string	some	regular (full due paid in 2 months of the period, 3 at 180+) / some (AED 100+ paid in a month of the period; at 180+, of the last 12 months) / none
75	SF_3_record_before_delinquency_level	string	clean	clean (monthly due, for cards the minimum, paid in 80%+ of billed months in the 12 months before this delinquency) / not_clean / no_record (under 3 bills, or start not visible)
76	SF_3_refusal_flag	numeric	0	1 = latest contact was a refusal, with no plan or AED 100+ payment since
77	SF_4_main_reason	string	income	What set the state most: income / money_in / spending / other_products / distress. Blank = nothing strong
78	SF_4_income_level	string	stable	stable (period salary ≥ 2 × the strong amount, 3 × at 180+, and not more than 25% below the period before) / weak (a month with AED 1,000+) / none
79	SF_4_money_in_level	string	strong	Non-salary money into or held in accounts with us: strong (the strong amount in 2 of 3 months, 3 of 6 at 180+, as inflow or balance held) / some (a month with AED 1,000+) / none. Blank = no data
80	SF_4_spending_level	string	some	Money spent or moved out by choice, same scale as money in. Blank = no data
81	SF_4_other_products_level	string	none	strong (deposits / investments ≥ the strong amount, or an up-to-date loan / card with instalment ≥ max(AED 1,000, amount due)) / some (any deposit / investment, or any up-to-date loan / card) / none
82	SF_4_distress_flag	numeric	0	1 = returned cheque, rejected direct debit or a bounced payment reported by the credit bureau in the period
83	SF_4_income_source	string	internal	Where salary of AED 1,000+ was seen in the period: internal / bureau / both / none
84	SF_4_salary_stopped_flag	numeric	0	1 = salary with us in the period before, none in the period
85	SF_4_unknown_reason	string	no_account_activity_12m	no_account_activity_12m / inactive_account (account with us, no transaction in the period). Blank unless Ability is Unknown
```

## Deriving the states

- **SF_1** is not derivable from these columns: the journey tree reads about eight history
  features (`docs/deterioration_states/METHODOLOGY.md`).
- **SF_2:** Deceased overrides everything (shown in SF_2 itself). Otherwise location × reachability.
  Location: abroad_latest or travelled_then_quiet = Skip, uae_recent = In Country, else Unknown.
  Reachability: call_connected = Reachable, calls_failing = Non-Reachable, else Unknown.
- **SF_3:** Unknown when SF_1 was not scored for the row. Otherwise points:
  - promise level: kept 3, partly_kept 2, promised 1, no_promise 0 (D-A3-33, -34);
  - payment while overdue: regular 2, some 1, none 0;
  - record before delinquency: clean 1, else 0.

  High from 4, Moderate from 2, else Low. `SF_3_refusal_flag` = 1 moves the state one level down
  (not below Low). Promise level from the counts, first match: kept if 2+ judged and 80%+ kept; partly_kept if 1+ kept; promised if any promise in the last 12 months (judged or
  not yet); else no_promise. Partly paid
  counts as not kept.
- **SF_4:** stable income or a strong family = 2 points each. High from 4, Moderate from 2, else
  Low; `SF_4_distress_flag` = 1 moves it one level down (not below Low). Unknown when
  `SF_4_unknown_reason` is filled: every level none or blank, no distress, no account activity in
  the period.

## Changes against `uc2_signals_output_schema.md`

| old id | old field | new field | change | decision |
|---|---|---|---|---|
| 56 | `dpd_bucket` | **dropped** | DCORE holds the live bucket | cut |
| 57 | `SF_1_months_before_spell` | `SF_1_months_before_delinquency` | Desc was wrong (not clean history, not time on book) | C2, C9 |
| 58 | `SF_1_prior_episodes` | `SF_1_prior_delinquency_count` | blip rule completed | C2 |
| 59 | `SF_1_spell_pay_months` | **dropped** | overlaps `SF_3_full_due_paid_months` | — |
| 60 | `SF_1_months_since_61_dpd` | same | 61+, visible-history caveat | — |
| 61 | `SF_1_history_gap_flag` | **dropped** | user, 2026-11-16 | — |
| 62 | `SF_2_location_reason` | same | new value names; travel rule corrected | C3 |
| 63–65 | — | same | blank cases, all accounts | — |
| 66 | `SF_2_last_foreign_source` | same | `dcore` → `collector_note` (code: `dcore_note`) | C3 |
| 67 | — | same | blank case | — |
| 68 | `SF_2_travel_purchase_recent_flag` | `SF_2_recent_travel_purchase_flag` | period defined | C2 |
| 69 | `SF_2_last_contact_date` | **dropped** | DCORE call log (the SF_2 value already says Reachable / Non-Reachable) | cut |
| 70 | `SF_2_last_attempt_date` | **dropped** | DCORE call log | cut |
| 71 | `SF_2_attempt_days_in_window` | **dropped** | DCORE call log | cut |
| 72 | `SF_2_last_skip_trace_date` | **dropped** | DCORE result | cut |
| 73 | `SF_3_reason` | `SF_3_main_reason` | new values; blank meaning corrected | C2, C3, C5 |
| 74 | `SF_3_episode_start` | **dropped** | DCORE shows the delinquency date | cut |
| 75–77 | `SF_3_commitments_*` | `SF_3_promise_level`, `SF_3_promises_judged_count`, `SF_3_promises_kept_count` | deadline rule and window spelled out | C2 |
| 78 | `SF_3_dlq_payment_level` | `SF_3_payment_while_overdue_level` | 180+ rule and "some" window were wrong / missing | C2 |
| 79 | `SF_3_pre_dlq_payment_level` | `SF_3_record_before_delinquency_level` | no_record cases | C2 |
| 80–81 | `SF_3_last_rpc_date`, `_disposition` | **dropped** | in DCORE already | cut |
| 82 | `SF_3_refusal_flag` | same | "latest contact" scope added; cast to 0/1 | C4 |
| 83 | `SF_3_dispute_flag` | **dropped** | the DCORE disposition | C6, cut |
| 84 | `SF_3_no_pickup_after_contact` | **dropped** | read straight off the DCORE call log | cut |
| new | — | `SF_2_reachability_reason` | the SF_2 reachability part from the columns (state + `reachability_unknown_reason`) | derivable |
| new | — | `SF_3_promises_partly_paid_count`, `SF_3_promises_broken_count`, `SF_3_full_due_paid_months` | the promise level and payment level can be re-derived | derivable |
| 85 | `SF_4_reason` | `SF_4_main_reason` | new values; blank meaning | C2, C3 |
| 86 | `SF_4_income_level` | same | threshold was wrong | — |
| 87 | `SF_4_money_in_level` | same | salary excluded; thresholds; blank | — |
| 88 | `SF_4_money_out_level` | `SF_4_spending_level` | thresholds; blank | C2 |
| 89 | `SF_4_cross_product_level` | `SF_4_other_products_level` | thresholds | C2 |
| 90–92 | — | same | period defined | — |
| 93 | `SF_4_eosb_flag` | **dropped** | DCORE result | cut |
| 94 | `SF_4_unknown_reason` | same | values `no_account_activity_12m` / `inactive_account`; Desc was wrong | C3 |
| 95 | `SF_4_amount_due_now` | **dropped** | amount owed is in DCORE; the header note says how thresholds use it | cut |

New ids: in the order of the Rows block; the ids in this table are the old ones.

## Code column → output field (for the persona master)

| Axis column | Output field | Transform |
|---|---|---|
| `months_before_spell` | `SF_1_months_before_delinquency` | — |
| `n_prior_episodes` | `SF_1_prior_delinquency_count` | — |
| `months_since_4` | `SF_1_months_since_61_dpd` | — |
| `location_rule` + `location_unknown_reason` | `SF_2_location_reason` | L1 → abroad_latest, L2 → travelled_then_quiet, L3 → uae_recent, L4 + domestic_before_window → uae_too_old, L4 + no_evidence → no_evidence |
| `last_uae_date`, `last_uae_source`, `last_foreign_date` | `SF_2_last_uae_date`, `SF_2_last_uae_source`, `SF_2_last_foreign_date` | — |
| `last_foreign_source` | `SF_2_last_foreign_source` | dcore_note → collector_note |
| `last_travel_date` | `SF_2_last_travel_date` | — |
| `reachability_state` + `reachability_unknown_reason` | `SF_2_reachability_reason` | reachable → call_connected, non_reachable → calls_failing, unknown + no_contact_in_window → no_recent_connection, unknown + no_dcore_record → no_calls |
| `last_travel_date` | `SF_2_recent_travel_purchase_flag` | 1 if ≥ first day of the month 2 (5 at 180+) months before the observation month |
| `a3_reason` | `SF_3_main_reason` | commitments → promises, dlq_payments → payments_while_overdue, pre_dlq_record → record_before_delinquency; blank when SF_3 = Unknown |
| `a3_commitments_level`, `commitments_concluded`, `commitments_kept` | `SF_3_promise_level`, `SF_3_promises_judged_count`, `SF_3_promises_kept_count` | — |
| `a3_dlq_payment_level` | `SF_3_payment_while_overdue_level` | — |
| `commitments_partial` | `SF_3_promises_partly_paid_count` | — |
| `commitments_concluded − commitments_kept − commitments_partial` | `SF_3_promises_broken_count` | — |
| `dlq_payment_qualifying_month_cnt` | `SF_3_full_due_paid_months` | — |
| `a3_pre_dlq_payment_level` | `SF_3_record_before_delinquency_level` | — |
| `a3_refusal_flag` | `SF_3_refusal_flag` | boolean → 0/1 |
| `a1_reason` | `SF_4_main_reason` | money_out → spending, cross_product → other_products |
| `a1_income_level`, `a1_money_in_level` | `SF_4_income_level`, `SF_4_money_in_level` | — |
| `a1_money_out_level` | `SF_4_spending_level` | — |
| `a1_cross_product_level` | `SF_4_other_products_level` | — |
| `a1_distress_flag`, `a1_income_source`, `a1_salary_stopped` | `SF_4_distress_flag`, `SF_4_income_source`, `SF_4_salary_stopped_flag` | — |
| `a1_unknown_reason` | `SF_4_unknown_reason` | no_casa → no_account_activity_12m, dormant_casa → inactive_account |

## Decided (user, 2026-11-16: the review's recommendations)

- C1: `SF_1_reopened_in_delinquency_flag`, the narrow meaning (restructured loan not linked to its
  originals, or card opened at 61+ DPD). Linked restructures are 0; no separate restructured flag.
- C2: the column renames and the suffix rule (`_flag` 0/1, `_level`, `_date`, `_count`, `months_…`,
  `_aed`, `_reason` / `_source` / `_outcome`).
- C3: value codes renamed once in the persona master (mapping table above).
- C4: flags are 0/1 numeric; the A3 booleans are cast.
- C5: `SF_3_main_reason` is blank when SF_3 is Unknown.
- C6: `SF_3_dispute_flag` dropped.
- C7: superseded: open promise and last payment are in DCORE, so not added.
- C8: moot (`dpd_bucket` dropped).
- C9: `SF_1_months_before_delinquency` kept, with the visible-history Desc.
- SF_3 cut (user, 2026-11-16): no columns that repeat DCORE. Dropped: last customer contact date
  and outcome, the no-answer flag, and the proposed open-promise and last-payment columns. Kept: the
  engine's own signals (main reason, promise level with the judged / kept
  counts, payment while overdue, record before delinquency, refusal flag after the payment / plan
  lift).
- Same cut on every axis (user, 2026-11-16: amounts owed etc. are in DCORE): dropped `dpd_bucket`,
  the SF_2 call columns (last connected call, last attempt, attempt days, skip trace),
  `SF_4_end_of_service_flag` and `SF_4_amount_due_aed`.
- `SF_3_delinquency_start_date` dropped too (user, 2026-11-16: DCORE shows it).
- `SF_1_reopened_in_delinquency_flag` dropped (user, 2026-11-16); C1 moot.
- Descriptions cut to the minimum; columns added so SF_2–SF_4 can be re-derived from the table (user, 2026-11-16): `SF_2_reachability_reason`, the partly paid / broken promise counts, the last-3 flag, full-due months. SF_1 is not derivable (open).
- `SF_1_months_paid_in_delinquency` dropped (user, 2026-11-16: overlaps `SF_3_full_due_paid_months`); the other three SF_1 columns stay as context.
