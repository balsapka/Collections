# Review: UC2 signal rows 56–95 (`uc2_signals_output_schema.md`)

Reviewed 2026-11-16 against the bundle 25 tree (`.worktrees/council_a1_a3`, head `1550e83`). Paths
below are relative to `workplace_mirror/src/enbd_collections/pipelines/crx_persona/` unless they
start with `nodes/`. The schema file and the code are unchanged.

Two questions per row:
- **Reader:** can an agent or collector who has never seen this project use the column from its
  name, type, example and Desc alone?
- **Code:** is every claim in the Desc true in the code?

Verdicts: **correct** · **correct, incomplete** (true, but a reader would misuse it without the
missing part) · **wrong** (a claim is false; evidence and fix given) · **unverifiable**.

**Result: 13 rows wrong, 21 correct but incomplete, 6 correct.** Every row gets a proposed name or
Desc; for the 6 correct rows the change is wording only. Rows 62 and 68 (built in the persona master) can both be built from the
columns they name, but row 62's `travelled_no_uae_since` describes the travel rule wrongly.

## (a) Per-row table

The proposed names follow the naming convention in (b). Where only the Desc changes, the name
column says "keep". The proposed Desc texts are written to stand alone.

| id | field | verdict | issue (evidence) | proposed name / Desc |
|---|---|---|---|---|
| 56 | `dpd_bucket` | correct, incomplete | Mapping is right: CC native = canonical, RL native + 1 (`_dpd_journey/constants.py:25-26`), and `current_bucket` is the native bucket at the row's month (`_dpd_journey/spark.py:310`). But (1) the loan top bucket is RL native 7 = **181+** (`rl_a4_deterioration/nodes.py:16`), so "180+" overlaps 151–180. (2) For cards the value is the bucket on the **statement** in the observation month, not at the month end: the gap to DCORE is the days since that statement, not "since the observation date". (3) Blank when A4 did not score the row (no usable history, or a non-delinquent month: `spark.py:290-296`) is not stated. | keep. *DPD range on the latest statement (cards) or month-end loan record (loans) in the observation month, in days: 61-90 / 91-120 / 121-150 / 151-180, then 181-210 / 211+ for cards and 181+ for loans. Our reference value; the collection system's live bucket can be higher by the days since that statement. Blank if the account has no usable payment history.* |
| 57 | `SF_1_months_before_spell` | **wrong** | "Months of clean history on book" is false. The value is `sp_start` (`_dpd_journey/core.py:121`): the number of **observed** months before the current delinquency started. Earlier delinquencies are included (they are not "clean"). It is also capped by the data: card history starts at the 2024-01-01 floor (`cc_a4_deterioration/nodes.py:7-9`), so it is not time on book. It is 0 when the delinquency started before the data begins. "Spell" is jargon. | `SF_1_months_before_delinquency`. *Months of payment history we can see before the current delinquency began (earlier delinquencies included). Short = early-life default; long = seasoned customer. Card history starts in Jan 2024, so cards top out at about 34; 0 = the delinquency began before our history does.* |
| 58 | `SF_1_prior_episodes` | **wrong** | The rule that skips blips is incomplete. A blip is 1–2 months that **never passed 1–30 DPD** (`core.py:105`: `e - s <= 2 and max(b) <= 2`), so a 2-month spell that reached 31–60 does count. The count only covers the visible history. "Episodes" is jargon and the name has no count suffix. | `SF_1_prior_delinquency_count`. *Earlier delinquencies on this account in the visible history, after it had come back to current. Not counted: 1–2 month slips that never went past 30 DPD.* |
| 59 | `SF_1_spell_pay_months` | **wrong** | "Paid something" is false. The code counts months in the current delinquency where the bucket **held or improved** (`core.py:143-147`: transitions that are not a roll). A partial payment that still lets the account roll is not counted. A hold at the top bucket (cards 211+, loans 181+) is not counted either. So 0 means "never paid enough to stop the roll", not "paid nothing". | `SF_1_months_paid_in_delinquency`. *Months since this delinquency began in which the account did not get worse, i.e. the customer paid about a month's due or more. 0 = never paid enough to stop the roll (small partial payments may still have come in). Months at the top bucket (cards 211+, loans 181+) are not counted.* |
| 60 | `SF_1_months_since_61_dpd` | correct, incomplete | `months_since_4` = months since the first month at canonical ≥ 4 in this delinquency (`core.py:122,128`), so "61+", not exactly "61–90" (an account can jump past). If the delinquency started before our history, it counts from the first month we can see. | keep. *Months since the account first reached 61+ DPD in this delinquency (0 = this month). If the delinquency began before our history starts, it counts from the first month we can see.* |
| 61 | `SF_1_history_gap_flag` | **wrong** | The 1-cases are right. Cards: the earliest billing row is at bucket ≥ 4 (`cc_a4_deterioration/nodes.py:22-45`). Loans: `has_restructured_loan_flag` ever set, minus the stitched chains (`rl_a4_deterioration/nodes.py:166-229`). But "1 = the start is not visible" claims too much, so 0 does not mean the start is visible. Cards whose history is **cut at the 2024 floor** are blind (`history_cropped`, `states.py:113`) but read 0. This is common at 180+. Also, a stitched loan reads 1 for observation months before its `chain_known_date` (`rl_a4_deterioration/nodes.py:262-276`). | Your decision (C1). Either (a) keep the narrow meaning: `SF_1_reopened_in_delinquency_flag`. *1 = this account was opened while already delinquent: a restructured loan we could not link to its original loans, or a card whose first statement was already 61+ DPD. Its earlier history is missing.* Or (b) widen the column to every blind case: `restructure_blind_spot_flag OR (left_censored AND history_cropped)`, which is A3's `episode_left_censored` plus the flag. Then the current Desc becomes true. |
| 62 | `SF_2_location_reason` (derived) | **wrong** (one value) | Can be built from `location_rule` + `location_unknown_reason` (`a2_locatability/signals.py:156-170`): L1 / L2 / L3 / L4 + `no_evidence` / `domestic_before_window`. But `travelled_no_uae_since` misstates L2 (`signals.py:116-127`). L2 allows UAE evidence up to **3 months after** the ticket, provided there has been none in the **last month**. `uae_in_window` and `uae_before_window` use the undefined "window". L1 and L2 have no age limit: an old foreign login with nothing since still means Skip. | Values `abroad_latest` / `travelled_then_quiet` / `uae_recent` / `uae_too_old` / `no_evidence`. *Why the location part of SF_2 is what it is. abroad_latest: the most recent evidence (any age) puts the customer abroad. travelled_then_quiet: a travel purchase, at most 3 months of UAE evidence after it, and none in the last month. uae_recent: UAE evidence in the last 3 months (6 at 180+), observation month included. uae_too_old: UAE evidence exists but is older than that. no_evidence: none at all.* |
| 63 | `SF_2_last_uae_date` | correct, incomplete | Latest UAE evidence over all of the customer's accounts (`signals.py:85-106`; `nodes/features/location/feat_cif_location_monthly.py:1-16`). It is in-person card use or a UAE login. Travel purchases made in the UAE are excluded (`feat_cif_location_monthly.py:137,177`). Blank-if-none is not stated. | keep. *Latest date we have evidence the customer was in the UAE: a login from the UAE, or a card used in person there (shop terminal or ATM), on any of their accounts. Blank if none.* |
| 64 | `SF_2_last_uae_source` | correct | Values match (`feat_cif_location_monthly.py:12-14`). | keep. *What that evidence was: login / debit_card / credit_card (card used in person). Blank if none.* |
| 65 | `SF_2_last_foreign_date` | correct | `_foreign` struct (`signals.py:93`); blank when none. | keep. Add "on any of their accounts". |
| 66 | `SF_2_last_foreign_source` | **wrong** | The code emits `dcore_note`, not `dcore` (`feat_cif_location_monthly.py:14,215`). Blank-if-none is not stated. | keep the name; map the value in the master. *What that evidence was: login / debit_card / credit_card (card used in person abroad) / collector_note (a collector recorded that the customer left the country). Blank if none.* |
| 67 | `SF_2_last_travel_date` | correct, incomplete | Debit travel purchases count only on the POS channel (`feat_cif_location_monthly.py:129`). Credit purchases count on any channel (`:174`). Travel = airline / travel agency / cruise MCC, or a travel keyword in the description (`nodes/utils/location.py:21-26`). Blank-if-none is not stated. | keep. *Latest travel purchase (airline, travel agency, cruise) on any of the customer's cards. Blank if none. It is a sign of a possible trip, not proof the customer left.* |
| 68 | `SF_2_travel_purchase_recent_flag` (derived) | correct, incomplete | Can be built: `last_travel_date >= window_start(W)` = the first day of the month 2 (5 at 180+) months before the observation month (`_common.py:75-79`). The master needs the segment, which it has from `model_id`. "Last 3 months" should say calendar months, observation month included. | `SF_2_recent_travel_purchase_flag`. *1 = a travel purchase in the observation month or the 2 months before (5 at 180+). An early warning of a possible departure, raised before the location state changes to Skip.* |
| 69 | `SF_2_last_contact_date` | correct, incomplete | Contact rule matches (`signals.py:195-202`): only call entries count, and ignored results are excluded. The Non-Reachable rule leaves out "the **oldest** of those failed call days is within the window" (`signals.py:217-228`). "Window" and "DCORE" are undefined. Reachability is read on the scored account's agreement, not the CIF. "Right-party" is jargon. | `SF_2_last_call_connected_date`. *Latest call on this account that got through: the customer called in, or a collector's call was answered by the customer. Decides reachability: a connected call in the observation month or the 2 before (5 at 180+) = Reachable. Non-Reachable = the last 3 call days (6 at 180+) all failed, all inside that period, with no connected call since. Blank if no call ever got through.* |
| 70 | `SF_2_last_attempt_date` | correct, incomplete | Outbound calls only (OC / CB), ignored results excluded (`signals.py:196-198,252`). | `SF_2_last_call_attempt_date`. *Latest day a collector called this account, whatever the outcome. Blank if never called.* |
| 71 | `SF_2_attempt_days_in_window` | correct, incomplete | Distinct outbound call days in W (`signals.py:253-255`); 0 when none (`:271`). W has to be spelled out. | `SF_2_call_attempt_days_recent`. *Number of days a collector called this account in the observation month and the 2 before (5 at 180+). 0 = no calls.* |
| 72 | `SF_2_last_skip_trace_date` | correct | `SKIP - UNDER TRACING`, `SKIP - TRACED` (`_dcore_codes.py:139`), any entry type. | keep. *Latest date the collection system recorded the customer as being traced or traced (skip trace = searching for a customer who cannot be reached). Blank if never.* |
| 73 | `SF_3_reason` | **wrong** | The value set is right (`scoring_engine.py:101`, dimension names `a3_credibility/constants.py:69-77`). "Blank = no evidence (Low on 0 points)" is false: blank means **no family scored a positive point**, which includes rows with only broken promises (−1). Commitments are scored on every row, episode or not (`signals.py:113`), so a credibility-Unknown row can carry a reason. "Refusal lowered it one level" does nothing at Low. `dlq` / `pre_dlq` are jargon. | `SF_3_main_reason`, values `promises` / `payments_while_overdue` / `record_before_delinquency` / `refusal`. *Which evidence lifted credibility most. refusal = the customer's latest contact was a refusal to pay, which lowers the state one level (no further than Low). Blank = no positive evidence (state Low or Unknown).* Master: blank it when SF_3 = Unknown (C5). |
| 74 | `SF_3_episode_start` | **wrong** | (1) The date is the **first day of a month** (`_dpd_journey/anchor.py:48-51`), so the example `2026-06-30` cannot occur; use `2026-06-01`. (2) It is the month the account first went **1+ DPD** in this delinquency, not "collections entry". (3) "All credibility windows are read inside it" is false. Promises use the last 12 months, earlier delinquencies included (`signals.py:93-99`). The prior record is read **before** it (`signals.py:228-232`). (4) It is blank when A4 did not score the row; credibility is then Unknown (`sources.py:36-38`). | `SF_3_delinquency_start_date`. *First day of the month the account first fell overdue (1+ DPD) in its current delinquency. Blank = no delinquency history available (credibility Unknown). If our history starts mid-delinquency, the true start is earlier.* |
| 75 | `SF_3_commitments_level` | correct, incomplete | Rule order and thresholds match (`signals.py:107-122`, `constants.py:7-11`). Missing: "promises" also covers payment plans (`promises.py:51-77`). "Kept" means the promised amount was paid by the deadline, and the deadline is a fixed rule (cards 61–180: next statement, at most 31 days; loans and all 180+: end of the promise month, `constants.py:15-21`). The 12 months are calendar months by promise date. Broken "under 40%" needs ≥ 2 concluded. | `SF_3_promise_level`. *Promises to pay and payment plans made in the observation month and the 11 before, judged once their deadline has passed. Deadline: cards at 61–180 DPD = next statement; loans and everything at 180+ = end of the month the promise was made. kept = 2+ judged and 80%+ paid in full. broken = the last 3 all not paid in full, or 2+ judged and under 40% paid. partly_kept = at least one paid in full otherwise. thin = none paid in full, or no promises.* |
| 76 | `SF_3_commitments_concluded` | correct, incomplete | Event date in the 12 months, cutoff ≤ observation date (`signals.py:66-71`). As written, "deadline passed in the last 12 months" reads as if the deadline were the window key. | `SF_3_promises_judged_count`. *Promises made in the observation month and the 11 before whose deadline has passed (see SF_3_promise_level).* |
| 77 | `SF_3_commitments_kept` | correct | Outcome `paid` = payments reach the promised amount by the deadline (`promises.py:241-248`). | `SF_3_promises_kept_count`. *Of those, promises paid in full by their deadline. Partial payments do not count.* |
| 78 | `SF_3_dlq_payment_level` | **wrong** | "3 at 180+" reads as 3 of 3. The code is 3 of the last **6** months (`constants.py:44`, window W = 6, `signals.py:157`). "Some" has no window in the Desc: the code uses the last 3 months, or 12 at 180+ (`constants.py:45`). Only months after the delinquency-start month count (`signals.py:156`). A qualifying month = paid ≥ max(due, AED 100). | `SF_3_payment_while_overdue_level`. *Payments since the account fell behind. regular = the full monthly due (at least AED 100) paid in 2 of the last 3 months (3 of the last 6 at 180+). some = a month with AED 100+ paid in the last 3 months (12 at 180+). none = neither.* |
| 79 | `SF_3_pre_dlq_payment_level` | correct, incomplete | 12 months before the start month, clean ≥ 80% of months with a due paid in full (`signals.py:207-260`). `no_record` = fewer than 3 months with a due, **or** the delinquency start is blank or not visible (`signals.py:219-222`). | `SF_3_record_before_delinquency_level`. *Payment record in the 12 months before this delinquency. clean = 80%+ of the statements / instalments in that year paid in full. not_clean = below that. no_record = fewer than 3 bills in that year, or the start of the delinquency is not visible.* |
| 80 | `SF_3_last_rpc_date` | correct, incomplete | Window = since the delinquency start, at most 24 months (`signals.py:301-307`, `constants.py:56`). Notes logged without a call count too. "RPC" and "DCORE" are jargon. Blank is not stated. | `SF_3_last_customer_contact_date`. *Latest date the collection system shows the customer was reached personally (by call or a logged note, e.g. a promise or payment report) during this delinquency, at most 24 months back. Blank if none. Differs from SF_2_last_call_connected_date: see header note.* |
| 81 | `SF_3_last_rpc_disposition` | correct, incomplete | Value set matches (`signals.py:265-272`). Same-day order: promise > paid > refusal > dispute > success > hung up (`:278`). `ptp` also covers retention-desk PTP notes. `success` is unclear to a reader. | `SF_3_last_customer_contact_outcome`, values `promise_to_pay` / `payment_reported` / `refusal` / `dispute` / `hung_up` / `reached`. *Outcome of that contact. reached = spoke to the customer, no specific outcome. Blank if no contact.* |
| 82 | `SF_3_refusal_flag` | **wrong** | The scope is missing. The flag fires only when the **latest** contact was a refusal (`signals.py:427-429`). An earlier refusal followed by any other contact gives 0. Lifted by a plan started on or after the refusal day, or AED 100+ paid on or after it (loans: in the refusal month) (`:313-338,366-381`). The code type is **boolean**, not 0/1 (`signals.py:448`). | keep. *1 = the customer's latest contact was a refusal to pay, and no plan or payment of AED 100+ has come since (a payment on the same day lifts it). Lowers credibility one level.* Master: cast to 0/1. |
| 83 | `SF_3_dispute_flag` | correct | `last_rpc_disposition == 'dispute'` (`signals.py:456`). Boolean in code. Fully redundant with row 81 (C6). | keep, or drop (C6). *1 = the latest contact was a dispute (the customer contests the debt). Rows 20–25 give the call-transcript view.* Master: cast to 0/1. |
| 84 | `SF_3_no_pickup_after_contact` | correct, incomplete | Needs a last contact, plus **3 days (6 at 180+)** with an unanswered outbound call (no answer / ringing / message left) after it, and no dead-line result since (`signals.py:464-468`, `constants.py:57`). Boolean in code. The name has no `_flag`. | `SF_3_no_answer_since_contact_flag`. *1 = since the latest contact, collector calls went unanswered on 3+ days (6+ at 180+) and the number is not recorded as wrong or dead. The customer may be avoiding calls.* Master: cast to 0/1. |
| 85 | `SF_4_reason` | correct, incomplete | `distress` if it fired, else the family with the most points, else **blank** (`scoring_engine.py:101`). Blank is not stated. "Family" is jargon. | `SF_4_main_reason`, values `income` / `money_in` / `spending` / `other_products` / `distress`. *Which evidence lifted ability most. distress = a returned cheque, rejected direct debit or bureau bounce in the period, which lowers the state one level. Blank = no strong evidence (state Low or Unknown).* |
| 86 | `SF_4_income_level` | **wrong** | The threshold is wrong. Stable = the period's **total** salary reaches **2 ×** (3 × at 180+) max(AED 3,000, 2 × amount due), **and** is at most 25% below the previous period (`a1_ability/classify.py:126-149`). Weak = any month with AED 1,000+ salary (`:148`). Salary = the larger of the internal and bureau amounts each month (`signals.py:11-12`). The window is undefined in the Desc. | keep. *Salary over the observation month and the 2 before (6 months at 180+), from our records or the credit bureau, whichever is larger each month. stable = the total reaches 2 × (3 × at 180+) the larger of AED 3,000 and twice SF_4_amount_due_aed, and is no more than 25% below the period before. weak = some month with AED 1,000+ salary. none = no salary seen.* |
| 87 | `SF_4_money_in_level` | **wrong** | Leaves out that salary is **excluded** (`signals.py:246-247`: "salary credits are income, not money in"). No thresholds are given. Strong = money in at the strong amount in 2 of 3 months (3 of 6), **or** a current/savings balance at that amount in 2 of 3 months and not halved (`classify.py:158-196`). Some = a month with AED 1,000+ in. **Blank** when there is no account flow data in the period (`:181`). | keep. *Money other than salary coming into the customer's current / savings accounts with us, or held there. strong = the larger of AED 3,000 and twice SF_4_amount_due_aed, in 2 of the last 3 months (3 of 6 at 180+), either as inflow or as balance held. some = a month with AED 1,000+ in. none = less. Blank = no account activity data in the period.* |
| 88 | `SF_4_money_out_level` | correct, incomplete | Same thresholds as 87 on the counted outflow classes (`classify.py:199-201`, `signals.py:211-214`). "Chooses to spend" is vague. Blank as in 87. | `SF_4_spending_level`. *Money the customer spends or moves out of their accounts with us by choice: card and account spending, transfers to their own accounts at other banks (the counted outflow classes of the account-flow feature). strong / some / none on the same amounts as SF_4_money_in_level. Blank = no data.* |
| 89 | `SF_4_cross_product_level` | correct, incomplete | At the observation month end, the scored account excluded. Strong = assets ≥ max(3,000, 2 × due) **or** another credit product flagged current (`is_current`) with instalment / minimum due ≥ max(1,000, due) (`classify.py:204-215`, `signals.py:298-340`). Some = any other current credit product or any asset > 0; an overdue other product does not count. Thresholds missing; "current" is ambiguous. | `SF_4_other_products_level`. *Other products the customer holds with us at month end. strong = deposits / investments of at least the larger of AED 3,000 and twice SF_4_amount_due_aed, or another loan / card that is up to date with an instalment of at least the larger of AED 1,000 and SF_4_amount_due_aed. some = any other up-to-date loan / card, or any deposit / investment. none = neither.* |
| 90 | `SF_4_distress_flag` | correct, incomplete | Cheque return, DDS return or bureau bounce dated in W (`signals.py:394-440`). W is undefined; DDS is jargon. | keep. *1 = a returned cheque, a rejected direct debit, or a bounce reported by the credit bureau in the observation month or the 2 before (5 at 180+). Lowers ability one level.* |
| 91 | `SF_4_income_source` | correct | `_income_source` (`classify.py:236-247`) on the monthly max ≥ AED 1,000 in W. | keep. *Where salary of AED 1,000+ was seen in the period: internal (credited to an account with us) / bureau (reported by the credit bureau) / both / none.* |
| 92 | `SF_4_salary_stopped_flag` | correct, incomplete | Internal salary only (bureau not read) (`classify.py:250-254`). The "previous window" needs defining. | keep. *1 = salary credited to an account with us in the 3 months before the period (6 at 180+) and none in the period. Possible job loss. Bureau salary is not considered.* |
| 93 | `SF_4_eosb_flag` | correct, incomplete | A DCORE result containing "EOSB" on any of the customer's agreements, in W (`signals.py:446-487`). "EOSB" is jargon. | `SF_4_end_of_service_flag`. *1 = a collector recorded an end-of-service benefit (gratuity) as expected or received in the period: a lump sum may be coming.* |
| 94 | `SF_4_unknown_reason` | **wrong** | `no_casa` is not "no current / savings account". It is **no account movement and no positive balance in the last 12 months** (`signals.py:249-251,281`), so a customer can hold a zero, unused account and still read `no_casa`. `dormant_casa` has no definition in the Desc: the code sets it when the customer held one in the 12 months but had no counted transaction in the period (`classify.py:276-279`). | keep, values `no_account_activity_12m` / `inactive_account`. *Why ability is Unknown. no_account_activity_12m = no current / savings account with movement or a positive balance with us in the last 12 months. inactive_account = such an account exists but had no counted transaction in the period. Blank when ability is not Unknown.* |
| 95 | `SF_4_amount_due_now` | correct, incomplete | Cards 61–180: amount in the oldest non-empty overdue bucket on the observation month's statement (`cc_a1_ability/nodes.py:25-61`). Loans: one instalment (`rl_a1_ability/nodes.py:44`). Blank at cards 180+ ✓. Also blank when there is no statement or loan record that month, or the buckets / instalment are empty or zero. This is also the yardstick for every ability threshold. | `SF_4_amount_due_aed`. *Reference amount the customer must find now, AED. Cards: the oldest overdue amount on the statement (what stops the roll). Loans: one instalment. Blank at cards 180+, or with no statement or loan record that month; ability then uses its AED floors alone. Not the total overdue.* |

### Code column → output field table

- `current_bucket` → `dpd_bucket` needs the explicit product mapping: cards native 4–9 →
  61-90 … 211+; loans native 3–7 → 61-90 … 181+.
- `a3_refusal_flag`, `a3_dispute_flag`, `a3_no_pickup_after_contact` are **booleans** in code
  (`signals.py:427-468`). The master must `cast("int")` them like the A1 flags
  (`classify.py:270-284`).
- `last_foreign_source` needs the value map `dcore_note` → (proposed) `collector_note`.
- `location_rule` + `location_unknown_reason` → `SF_2_location_reason`: L1 → abroad_latest,
  L2 → travelled_then_quiet, L3 → uae_recent, L4 + `domestic_before_window` → uae_too_old,
  L4 + `no_evidence` → no_evidence.
- "What changed" says the anchor amount was kept as drafted. Fine. "Kept as drafted … A3 levels"
  is also fine.

## (b) Cross-cutting recommendations

1. **One suffix rule** (today it is mixed: `no_pickup_after_contact` has no `_flag`,
   `episode_start` no `_date`, `prior_episodes` / `commitments_kept` are counts with no marker,
   `amount_due_now` has no unit):
   - `_flag`: 0/1 numeric, never boolean;
   - `_level`: ordered words;
   - `_date`: YYYY-MM-DD;
   - `_count`: counts of events;
   - `months_…`: durations;
   - `_aed`: amounts;
   - `_reason` / `_source` / `_outcome`: word codes.
   All value codes in lower_snake.
2. **No internal words in names or values.** Replace spell / episode → delinquency; rpc →
   customer contact; dlq / pre_dlq → while_overdue / before_delinquency; commitments → promises;
   cross_product → other_products; money_out → spending; casa → account; eosb → end_of_service;
   ptp → promise_to_pay; success → reached; dcore_note → collector_note. DCORE can stay in the
   header note as "the collection system", but not in the Descs.
3. **Header note for agents** (add above row 56; about 8 lines):
   - *Period:* "the period" = the observation month and the 2 months before it for accounts at
     61–180 DPD, and the 5 before at 180+. "The period before" = the same number of months just
     before it.
   - *Scope:* account-level for SF_1 and SF_3 and for the call columns of SF_2. Customer-level
     (all of the customer's accounts with us) for the SF_2 location columns and all of SF_4.
   - *Blanks:* a blank date means no such event in our data. A blank level means no data for that
     signal. If a whole feature's columns are blank, that feature could not be scored for this
     row.
   - *Two contact dates:* SF_2_last_call_connected_date = a call got through (decides
     reachability). SF_3_last_customer_contact_date = the customer was reached and an outcome
     was recorded (calls and logged notes; this delinquency only).
   - *Reference amounts:* SF_4_amount_due_aed is the yardstick. "Strong" = the larger of AED 3,000
     and twice that amount.
   - *Values are as of the observation date* (row 3), not today.
4. **Spell out every period in the Desc** ("observation month and the 2 before"), never
   "window", "in window" or "last 3 months". Calendar months are meant, observation month
   included, and a reader would otherwise count back 90 days.
5. **Keep the bank's 0/1 vs string split explicit.** Rows 12–51 use `detected` / `not-detected`.
   Our 0/1 numeric flags are fine but should be named in the header (C4).
6. **Drop candidate:** row 83 `SF_3_dispute_flag` is exactly `SF_3_last_rpc_disposition =
   'dispute'` (C6). It is not wrong, just a second copy.
7. **Add candidates** (each answers "what should I do now?" better than several rows kept; C7):
   - `SF_3_open_promise_flag` / `SF_3_open_promise_deadline_date`: a promise whose deadline has
     not passed yet, so don't chase it. Promise events with `promise_cutoff > observation_date`
     already exist (`promises.py`).
   - `SF_3_last_payment_date` / `SF_3_last_payment_aed`: from `crx_<p>_a3_payments` (bundle 25
     persists it).
8. **Value sets:** with the bank's "reference table will be provided" approach (rows 6–9), ship
   one reference table per code column (62, 64, 66, 73, 75, 78, 79, 81, 85–89, 91, 94) instead of
   relying on the Desc alone. The Descs above are written so they could be that table.

## (c) Decisions only you can make

- **C1 — `SF_1_history_gap_flag`:** narrow (restructured / reopened only, renamed, Desc made
  honest) or wide (also histories cut at the 2024 floor, so 1 = start not visible, as the Desc
  says now)? This ties into the open point "separate restructured flag". Under the narrow option
  the column *is* that flag for loans (`has_restructured_loan_flag` and not linked); a linked
  restructure would still need its own column if GRR wants every restructure flagged.
- **C2 — Renames:** adopt the column renames in (a) and the suffix rule in (b)1? They are
  master-only (the axis tables keep their names), but they change the field list GRR has seen.
- **C3 — Value renames in the master:** location_reason, sources (`dcore_note`), dispositions
  (`ptp`, `success`), unknown_reason (`no_casa`, `dormant_casa`), reason values. Map once in the
  master, or ship the code values with a reference table?
- **C4 — Flag encoding:** 0/1 numeric (and cast the three A3 booleans) or the bank's
  `detected` / `not-detected` strings?
- **C5 — `SF_3_reason` on credibility-Unknown rows:** blank it in the master? Promises are scored
  even with no delinquency start, so an Unknown row can show `commitments`.
- **C6 — Drop `SF_3_dispute_flag`** (redundant with the contact outcome) or keep it as a
  convenience for agents?
- **C7 — Add the open-promise and last-payment columns** (open promise / deadline; last payment
  date / amount)?
- **C8 — Loan top bucket label:** `181+` (proposed, no overlap with 151–180) or keep `180+`?
- **C9 — `SF_1_months_before_spell`:** keep it with the honest "visible history" Desc, or drop it?
  At cards 180+ it is mostly 0 (history before 2024 is cut), and A3 already uses the delinquency
  start.
