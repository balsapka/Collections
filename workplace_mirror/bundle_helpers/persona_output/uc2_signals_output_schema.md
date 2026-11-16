# UC2 persona signals: rows to append to `output_schema.md`

Rows 56–93 continue the bank's output schema (rows 1–55: keys, persona, collection action, the four
synthetic features SF_1–SF_4, UC1 transcript signals). One row per (`cif_id`, `account_id`,
`observation_date`). Examples are illustrative. Every signal is prefixed with the synthetic feature it belongs to
(`SF_1_` … `SF_4_`, as rows 6–9); the internal axis prefixes (`a1_` = SF_4 Ability, `a3_` = SF_3
Credibility, A4 = SF_1, A2 = SF_2) are not used here. The persona master renames the axis columns once
(mapping below); `SF_2_location_reason` and `SF_2_travel_purchase_recent_flag` are derived there, one
line each.

Selection rule: a signal goes to the handover only if a collector, GRR or the agent can **read it
on its own and act on it**: it says why the state is what it is, or gives a fact the state hides
(a date, an amount, an event). Rule mechanics (points, window starts, deadline-rule names,
counts that only build a rate), engine diagnostics and anything that repeats a column already in
the schema stay in the axis tables. Those are persisted and available on request.

## Rows to append

```
field id	field	type	Example value	Desc
56	SF_1_months_before_spell	numeric	18	months of clean history on book before the current delinquency spell started (short = early-life default, long = seasoned customer)
57	SF_1_prior_episodes	numeric	1	earlier delinquency spells on this account (1–2 month blips not counted)
58	SF_1_spell_pay_months	numeric	2	months in the current spell in which the customer paid something (0 = has not paid since falling behind)
59	SF_1_months_since_91_dpd	numeric	5	months since the account first reached 91–120 DPD in this spell
60	SF_1_restructured_flag	numeric	0	1 = restructured account; the journey before the restructure is not visible, so the state is less certain
61	SF_2_location_reason	string	uae_in_window	SF_2 location: why. foreign_after_uae (latest evidence is abroad) / travelled_no_uae_since (travel purchase, no UAE evidence since) / uae_in_window / no_evidence / uae_before_window (all evidence too old)
62	SF_2_last_uae_date	YYYY-MM-DD	2026-11-12	latest evidence the customer was in the UAE
63	SF_2_last_uae_source	string	login	source of that evidence: login / debit_card / credit_card (in-person use only)
64	SF_2_last_foreign_date	YYYY-MM-DD	2026-03-04	latest evidence the customer was abroad; blank if none
65	SF_2_last_foreign_source	string	credit_card	source of that evidence: login / debit_card / credit_card / dcore (collector departure note)
66	SF_2_last_travel_date	YYYY-MM-DD	2026-10-20	latest travel purchase (airline, travel agency, cruise; debit or credit card, any channel)
67	SF_2_travel_purchase_recent_flag	numeric	1	1 = a travel purchase in the last 3 months (6 at 180+), whether or not it has moved location to Skip yet. An early-warning signal for possible departure
68	SF_2_last_attempt_date	YYYY-MM-DD	2026-11-25	SF_2 reachability: latest collector call attempt (DCORE)
69	SF_2_attempt_days_in_window	numeric	6	distinct days with a call attempt in the window (3 months at 61–180, 6 at 180+)
70	SF_2_last_skip_trace_date	YYYY-MM-DD	2026-09-10	latest skip-trace / under-tracing result in DCORE; blank if never
71	SF_3_reason	string	commitments	what decided the state: commitments / dlq_payments / pre_dlq_record / refusal (refusal lowered it one level); blank = no evidence (Low on 0 points)
72	SF_3_episode_start	YYYY-MM-DD	2026-06-30	start of the current collections episode (all credibility windows are read inside it)
73	SF_3_commitments_level	string	kept	promises to pay in the last 12 months: kept (80%+ of 2 or more concluded promises kept) / broken (under 40%, or the last 3 all broken) / partly_kept (at least one kept otherwise) / thin (none kept, or no promises)
74	SF_3_commitments_concluded	numeric	4	promises whose deadline has passed in the last 12 months
75	SF_3_commitments_kept	numeric	3	of those, promises kept in full
76	SF_3_dlq_payment_level	string	some	payments while delinquent: regular (the monthly due paid in full in 2 of the last 3 cycles; 3 at 180+) / some (any payment of AED 100 or more) / none
77	SF_3_pre_dlq_payment_level	string	clean	record in the 12 months before the episode: clean (80%+ of bills paid as billed) / not_clean / no_record
78	SF_3_last_rpc_date	YYYY-MM-DD	2026-11-02	latest right-party contact (DCORE)
79	SF_3_last_rpc_disposition	string	ptp	outcome of that contact: ptp / paid (payment reported) / refusal / dispute / hung_up / success
80	SF_3_refusal_flag	numeric	0	1 = explicit refusal to pay, not lifted by a later payment or plan
81	SF_3_dispute_flag	numeric	0	1 = the latest contact was a dispute (DCORE disposition; UC1 rows 20–25 give the transcript view)
82	SF_3_no_pickup_after_contact	numeric	1	1 = has stopped answering since the last right-party contact
83	SF_4_reason	string	income	the strongest family behind the state: income / money_in / money_out / cross_product, or distress (lowered one level)
84	SF_4_income_level	string	stable	salary in the window: stable (reaches max(AED 3,000, 2 × amount due), not falling) / weak / none
85	SF_4_money_in_level	string	strong	money coming in or held in CASA: strong / some / none
86	SF_4_money_out_level	string	some	money the customer chooses to spend or move to own accounts elsewhere: strong / some / none
87	SF_4_cross_product_level	string	none	other products with us (deposits / investments, current credit products): strong / some / none
88	SF_4_distress_flag	numeric	0	1 = returned cheque, direct-debit reject or bureau bounce in the window
89	SF_4_income_source	string	internal	who sees an income of AED 1,000+ in the window: internal / bureau / both / none
90	SF_4_salary_stopped_flag	numeric	0	1 = salary credited with us in the previous window, none in the current one (possible job loss)
91	SF_4_eosb_flag	numeric	0	1 = DCORE end-of-service result in the window (gratuity payout may be due)
92	SF_4_unknown_reason	string	no_casa	why Ability is Unknown: no_casa (no current / savings account with us) / dormant_casa; blank otherwise
93	SF_4_amount_due_now	numeric	2000	amount the customer must find now (cards: oldest overdue bucket; loans: one instalment), AED; blank at cards 180+
```

38 signal columns: 5 SF_1, 10 SF_2, 12 SF_3, 11 SF_4. With the four states and the keys, the UC2 part of
the table is 42 columns. The deck's "50+ signals" refers to what the engines compute, not to this
table, and it holds: the four axis tables carry about 95 signal columns (A1 17, A2 17, A3 42,
A4 ~20).

## What changed against the workplace draft (rows 56–119+)

Kept as drafted (Desc rewritten for a collector): the four A1 family levels, distress, income source,
salary stopped, EOSB, unknown reason, anchor amount; A2 evidence dates and sources, attempts,
skip trace; A3 levels, promise counts, refusal, episode start.

Added:
- `SF_2_travel_purchase_recent_flag` (GRR asked for it). `last_travel_date` alone only says when. The
  flag fires on the purchase itself, before the travel rule (no UAE evidence for a month afterwards)
  moves the customer to Skip, so GRR can act before the customer leaves.
- `SF_2_location_reason`: replaces `location_rule` (L1–L4 codes) and `location_unknown_reason`.
- SF_1 had no rows in the draft: five journey facts from the A4 engine.
- `SF_3_last_rpc_disposition`, `SF_3_no_pickup_after_contact`, `SF_3_dispute_flag`.

Dropped, with the reason:

| Draft field(s) | Why it is not in the handover |
|---|---|
| `a1_state`, `a2_state`, `location_state`, `reachability_state`, `a3_state` | Repeat SF_2–SF_4 (rows 6–9). The location and reachability split of SF_2 is the open point below |
| `a1_provenance`, `a3_unknown_reason` | Follow from the state (Unknown ⇔ no_signal; A3 Unknown is only ever no_episode) |
| `a1_points_total`, `a3_points_total`, `a3_commitments_points` (and the other points) | Scoring mechanics: the levels say the same in words |
| `a3_override` | Same information as `a3_reason` = refusal and `a3_refusal_flag` |
| `commitments_window_start`, `dlq_payment_window_start`, `pre_dlq_window_start` | Fixed offsets from the observation date or the episode start |
| `a3_promise_deadline` | Constant per product and segment (a rule name, not a customer fact) |
| `commitments_partial`, `commitments_kept_rate`, `commitments_last_broken_n`, `dlq_payment_qualifying_month_cnt`, `pre_dlq_months_due_n`, `pre_dlq_paid_as_billed_share` | Inputs to the level, which is already shipped; concluded + kept give the rate |
| `episode_left_censored`, `pre_dlq_reason` | Data-coverage diagnostics; `no_record` already shows in the level |
| `refusal_followed_by_plan`, `refusal_followed_by_payment`, `a3_hung_up_last`, `contact_dates_n`, `no_pickup_days_n` | Inputs to the refusal / no-pickup flags, or already in `SF_3_last_rpc_disposition` |
| `a1_sweepable_balance_flag` | Diagnostic: measures the sweep, not ability (GRR: CASA balances are swept against the overdue) |
| `deceased_flag`, `deceased_source` | SF_2 = Deceased already; which system said so is an audit question |
| `last_contact_date` (A2; the name clash) | See open point 1 |
| A4 engine fields (`runup_len`, `last6_in_band`, `chg_6m`, `gap_prior_peak3`, `n_blips`, glitch / gap counters, `history_cropped`) | Tree mechanics and data-quality counters |

## Code column → output field

| Axis column | Output field |
|---|---|
| `months_before_spell` | `SF_1_months_before_spell` |
| `n_prior_episodes` | `SF_1_prior_episodes` |
| `spell_pay_events` | `SF_1_spell_pay_months` |
| `months_since_4` | `SF_1_months_since_91_dpd` |
| `restructure_blind_spot_flag` | `SF_1_restructured_flag` |
| `location_rule` + `location_unknown_reason` | `SF_2_location_reason` |
| `last_uae_date` | `SF_2_last_uae_date` |
| `last_uae_source` | `SF_2_last_uae_source` |
| `last_foreign_date` | `SF_2_last_foreign_date` |
| `last_foreign_source` | `SF_2_last_foreign_source` |
| `last_travel_date` | `SF_2_last_travel_date` |
| `last_travel_date` within W | `SF_2_travel_purchase_recent_flag` |
| `last_attempt_date` | `SF_2_last_attempt_date` |
| `attempt_days_in_window` | `SF_2_attempt_days_in_window` |
| `last_skip_trace_date` | `SF_2_last_skip_trace_date` |
| `a3_reason` | `SF_3_reason` |
| `episode_start` | `SF_3_episode_start` |
| `a3_commitments_level` | `SF_3_commitments_level` |
| `commitments_concluded` | `SF_3_commitments_concluded` |
| `commitments_kept` | `SF_3_commitments_kept` |
| `a3_dlq_payment_level` | `SF_3_dlq_payment_level` |
| `a3_pre_dlq_payment_level` | `SF_3_pre_dlq_payment_level` |
| `last_rpc_date` | `SF_3_last_rpc_date` |
| `last_rpc_disposition` | `SF_3_last_rpc_disposition` |
| `a3_refusal_flag` | `SF_3_refusal_flag` |
| `a3_dispute_flag` | `SF_3_dispute_flag` |
| `a3_no_pickup_after_contact` | `SF_3_no_pickup_after_contact` |
| `a1_reason` | `SF_4_reason` |
| `a1_income_level` | `SF_4_income_level` |
| `a1_money_in_level` | `SF_4_money_in_level` |
| `a1_money_out_level` | `SF_4_money_out_level` |
| `a1_cross_product_level` | `SF_4_cross_product_level` |
| `a1_distress_flag` | `SF_4_distress_flag` |
| `a1_income_source` | `SF_4_income_source` |
| `a1_salary_stopped` | `SF_4_salary_stopped_flag` |
| `a1_eosb_flag` | `SF_4_eosb_flag` |
| `a1_unknown_reason` | `SF_4_unknown_reason` |
| `liquidity_anchor_amt` | `SF_4_amount_due_now` |

## Open points (your call)

1. **One contact date or two.** A2's `last_contact_date` = any answered call (inbound, or an
   outbound call in the success category). This date decides reachability. A3's `last_rpc_date` = a
   confirmed right-party contact, and it comes with its outcome. Proposed: ship only the A3 pair.
   Alternative: also ship the A2 date as `SF_2_last_answered_date`, so a Non-Reachable row can show
   when the phone was last answered.
2. **SF_2 as one value or two.** If SF_2 carries the combined value (e.g. "In Country – Reachable",
   9 values + Deceased), the agent has to split it. Two extra columns (`SF_2_location_state`,
   `SF_2_reachability_state`) would make filtering easier, at the cost of repeating SF_2.
3. **DPD / bucket.** Not repeated: it comes from DCORE. If the output table must stand alone,
   add `SF_1_current_bucket` with an explicit DPD-range label (CC and RL bucket numbers differ natively).
