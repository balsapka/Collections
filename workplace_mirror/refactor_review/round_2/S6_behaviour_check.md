# S6 behaviour check: the bundle 25 behaviour steps at `e3bb65e`

Scope: the code at `e3bb65e`, checked against D-U1-1..7, D-B-1/2,
`specs/A3_credibility_spec.md` D-A3-29 (rewritten) / D-A3-30, and `specs/A1_ability_family_rule.md`
§1–2. These are findings only: nothing was edited, nothing committed, no Spark run. Paths are under
`src/enbd_collections/pipelines/crx_persona/` unless they say otherwise. Severity is H / M / L.
"Bug" means the code differs from a decision; "ambiguity" means the decision leaves the case open.

There are no H findings: the decided rules are coded as written. One M is a numeric fault in the new
fold. The rest are small questions.

## 1. Findings

```
Q-S6-17 [A3 · a3_credibility/promises.py:121-150 `_with_payments`, :158-162 `_event_step`] (M, bug: double arithmetic) "Paid since the event day" is a difference of two double sums. When the customer pays exactly the promised amount, it often comes out a hair below it, so the event does not end.
Now: paid_since_start = `_paid_before(day)` − `_paid_by(start)`. Each is a separate `F.sum` over a `double`, the first over a superset of the second's payments. In exact arithmetic the difference is the sum of the payments after the start, before the day. In floating point it is not. A Python simulation of payments with 2 decimals (1–6 earlier payments, then one exact payment of the amount): (Σa + x) − Σa < x in 35% of cases. The event then stays alive and absorbs the next promise before the deadline, although the payments reached the amount. The outcome itself (`_judged`, a direct sum) can still read `paid`, so the event is "paid" and yet swallowed a later promise. Spark's sum order is not fixed, so reruns can also disagree on such a row. | Decision: D-U1-1 / D-A3-29 "the event ends when … the payments since the event day and before a later promise reach the promised amount".
Options: (a) keep. (b) compare with a cent tolerance: `paid_since_start >= amount - 0.005`, or round both sums to 2 decimals before subtracting. (c) sum `decimal(18,2)` amounts in `_with_payments`.
Recommendation: (b) inside bundle 25's A3 behaviour step. The rule is new and not yet in PROD, so the old-vs-new check absorbs it. The same tolerance could later cover the older `>=` money comparisons (B's qualifying cycle, C's paid-as-billed, `_judged`), where a sum of several payments equal to the due reads below it in about 10% of simulated cases. Those predate this bundle, so they are a separate L. | Impact: events with earlier payments on the account, an exact payment of the promised amount, and a later promise before the deadline. Mostly CC 61–180 (next_statement) and the 30-day options. RL month_end never ends mid-month, so it is not affected. Which check shows it: a new spec case (earlier payments 1000.10 + 234.46, then exactly the promised amount, then a promise before the deadline: expect a new event). PROD: count `promise_outcome = paid` events that hold a promise day after their last payment (bundle 25 A3 check).
Answer:
```

```
Q-S6-18 [A3 · a3_credibility/signals.py:100-125 `build_commitment_signals`] (L, ambiguity raised by D-U1-1) An event that ended early because it was paid in full still counts as concluded only once its deadline has passed.
Now: `_concluded = promise_cutoff <= observation_date`. A card promise on 08-10, paid in full on 08-12, has its cutoff at the 09-05 statement. At obs 08-31 it is not concluded, so it adds neither kept nor broken, though it is settled and its outcome is known. | Decision: D-A3-25 "concluded once the deadline is on or before the observation date" (unchanged). D-U1-1 now lets payment end an event early, but says nothing about when it counts.
Options: (a) keep (an event counts after its deadline). (b) also concluded when the payments after the event day up to the observation date reach the amount (kept at once). That needs a paid-by-obs sum per row and event, not the cutoff sum.
Recommendation: ask the user with the promise-points work; (a) for bundle 25. | Impact: the latest month's kept counts on CC 61–180 and the 30-day options (cutoff after the month end). None on month_end books. Check: events with `promise_cutoff > obs` and payments by obs ≥ amount, per model_id.
Answer:
```

```
Q-S6-19 [A3 · a3_credibility/promises.py:107-109 `_with_terms`] (L, ambiguity: spec text vs code) The 100 AED floor also lifts a known due below 100. The spec says 100 AED only when no due exists.
Now: `promise_amount = greatest(coalesce(_due, 0), 100)`, so a known due of 60 becomes 100. | Decision: D-U1-6 / D-A3-29 "100 AED only when no due exists (rare)". D-A3-25's older text says "at least 100 AED".
Options: (a) keep the floor on every due (D-A3-25) and change D-A3-29's wording. (b) floor only a missing due.
Recommendation: (a). A promise below 100 AED would be "paid" by a payment that is not even a "partial" (which needs 100 AED), and the partial / none split would no longer line up with the amount. Fix the spec sentence. | Impact: dues below 100 AED (small residual buckets on cards; RL EMIs almost never). Check: events with `_due < 100`.
Answer:
```

```
Q-S6-20 [A3 · a3_credibility/signals.py:391-404 `_plan_after_refusal`] (L, consistency with D-B-2 (2)) A payment on the refusal day lifts the refusal (order within the day unknown), but a plan that starts on the refusal day does not.
Now: payments use `pay_date >= last_rpc_date` (D-A3-30, D-B-2). Plans use `plan_start > last_rpc_date`. A same-day follow-up promise already lifts it through `_SAME_DAY_ORDER`, so only a plan with no follow-up record on that day is left out. | Decision: D-A3-30 "counted only when it is certain"; D-B-2 (2) applies "order unknown" to payments only.
Options: (a) keep. (b) `>=` for plans too, under the same "penalise only when certain" reading.
Recommendation: put it to the user together with D-B-2 (2), which is open anyway; (b) if they confirm D-B-2 (2). | Impact: refusal rows with a DCORE plan starting on the refusal day and no same-day promise call; likely very few.
Answer:
```

```
Q-S6-21 [A3 · a3_credibility/promises.py:208-234 `_events`, :121-150] (L, reporting) `promise_paid_amount` of an event that ended early also includes payments made after the next event started, so one payment can be reported on two events.
Now: the paid amount is the start day's sum of payments after the event day up to its cutoff. A payment after a later event's day counts in both. Outcomes cannot change: the early end needs payments ≥ the amount before the later promise, and adding more keeps `paid`. Only the reported amount and any sum of `promise_paid_amount` across events are inflated. | Decision: D-U1-1 "a new event … counts only its own payments" (met for the new event). Nothing is said about what the old event reports.
Options: (a) keep and document the column ("payments up to the cutoff"). (b) cap the old event's sum at the next event's day.
Recommendation: (a), with one line in the column doc; nobody should sum the column across events. | Impact: none on state.
Answer:
```

```
Q-S6-22 [docs · `docs/ability/build_a1_workbook.py` on `feature/persona_redesign`, lines 369-377, 432-456, 580] (L, out of the bundle) The A1 model workbook still states the old thresholds: flows max(1,000, 1×), Some 500 out, balance max(3,000, 1×), assets max(10,000, 3×).
Now: the worktree's copy is the older four-book workbook. The authoritative builder (main checkout) has the family layout with the pre-D-U1-3 numbers. | Decision: D-U1-3 / D-U1-4, family rule §2.
Options: (a) update the builder's Logic / Examples text when bundle 25's threshold step is back (its results cells need the new run anyway).
Recommendation: (a); not refactor work. | Impact: GRR document only.
Answer:
```

## 2. Item by item

### 2.1 Promise events (`a3_credibility/promises.py`)

| Rule (D-U1-1 / D-A3-29) | Code | Verdict |
|---|---|---|
| One stream of plans and follow-up promises | `_promise_rows`: plans (start day) ∪ calls (`PROMISE_EVENT`, call day); `days` = distinct `(account_id, event_date)` | conforms |
| Event starts with the first promise; its terms are that day's | `_event_step` keeps `start`, `cutoff`, `amount`, `paid_at_start` of the start day; `_events` takes the start day's `_TERMS` | conforms |
| Alive until the deadline passes | `day.event_date <= live.cutoff` | conforms. **A promise on the deadline day belongs to the old event** (`<=`). |
| …or the payments since the event day, before a later promise, reach the amount | `_paid_before(day)` (dated < day) − `_paid_by(start)` (not after the start) `< amount` | conforms in exact arithmetic (Q-S6-17). It is exact as a set: `_paid_by(start)` ⊂ `_paid_before(day)`, and both stay inside the `pay_date ≤ cutoff` join, because every cutoff is ≥ its day. |
| Partial payment keeps it alive | the same test, strictly `<` | conforms |
| New event counts only its own payments | `promise_paid_amount` = `_after(start)`, up to the start's cutoff | conforms (Q-S6-21 is reporting only) |
| Same-day promise + payment | CC: a payment on a new event's day is not counted (`pay_from = pay_date`, not `_after`). For a live event, a payment on a later promise's day does not end it first (`pay_date < day`), so that promise joins the event, which can then read paid. | conforms; order unknown, so it reads in the customer's favour |
| Several promises on one day (plan + follow-up) | one fold step (distinct days); `_events` keeps the first plan (by day, `plan_id`) and the first call → `matched` | conforms |
| Loans never end mid-month | RL cash `pay_date` = month end, `pay_from` = 1st: inside month M, `pay_date < day` never holds for M's cash (also not on the month-end day itself); M's cash counts for an event starting in M (`_after`: same-day with `pay_from < pay_date`) | conforms. At month_end every promise of a month is one event. |
| Promised amount = latest non-empty due ≤ day, floor 100 | `max(when(due not null & cycle_start ≤ day, struct))`; `greatest(coalesce(_due,0),100)` | conforms on NULL skipping and the no-due fallback; floor wording is Q-S6-19 |
| Next statement capped at 31 days | `least(coalesce(next_cycle_end, day+31), day+31)` | conforms (D-B-2 (1), open for the user). It also settles round 1's "cutoff jumps past a dropped cycle" note. |
| Null handling | no dues → amount 100, cutoff day + 31; no payments → sums 0, `promise_paid_amount` NULL → 0 in `_judged`; a NULL `pay_from` on the event day is counted in neither sum (as before); a NULL `plan_start` day gets cutoff NULL and an event dated NULL, which never joins or blocks others and is dropped by the commitments window | conforms, harmless |
| Ordering | `array_sort` of structs led by `event_date`, which is unique per account (distinct days) | deterministic |
| No look-ahead | a day's event depends only on earlier days and on payments before it; dates, terms and outcome come from the start day. Later rows only fill `event_kind` / `event_name` / `plan_id` (no effect on the state). | conforms |

**Round 2's one-pass rewrite keeps 8b3d969's per-day semantics exactly:**
- `_with_terms` = old `_cutoff` + `_with_due`: same `min(cycle_end > day)`, same latest-non-NULL-due struct max. The left join only adds NULL rows, which change no aggregate.
- `_with_payments` = old `_with_paid_by` + `_with_paid`. The join bound moved from `pay_date ≤ day` to `pay_date ≤ cutoff`. Since cutoff ≥ day, `_paid_before` and `_paid_by` are unchanged, and `promise_paid_amount` is the old `_after(day) ∧ pay_date ≤ cutoff` sum, now computed for every day and read for the start day only.
- `_event_step` is unchanged apart from the variable name. The oracle being identical across 9fbc5d1..e3bb65e agrees.

### 2.2 Refusal (`signals.py` `_paid_after_refusal`, D-A3-30)

- Filter `pay_date >= last_rpc_date`, applied **before** the per-cycle grouping, so `_cycle` only regroups payments that may have come after the refusal. Conforms.
- Cards: payments dated the refusal day or later (the same day is D-B-2 (2), open).
- Loans: the refusal month's cash (`pay_date` = that month end ≥ refusal day) and later months'.
- **No payment certainly before the refusal can lift it.** An earlier month's RL cash is dated at that month end, which is before any refusal in a later month. The only equality case is a refusal on a month-end day, and then that month is the refusal month. `pay_from` is no longer read. Spec cases R6 (lifted) and R7 (paid before → refusal) cover it.
- Plans stay strict `>` (Q-S6-20).
- `_SAME_DAY_ORDER` (refusal, dispute, hung_up, paid, ptp, success) is the old alphabetical tie order with refusal first, so no value change (answers Q-R-10's concern).

### 2.3 A1 thresholds (`a1_ability/classify.py`)

- `_strong_amount` = max(`STRONG_FLOOR` 3,000, `STRONG_ANCHOR_MULT` 2 × anchor) is used for:
  - income: the window total ≥ 2 / 3 × the strong amount, unchanged S12;
  - money in and money out: `MIN_MONTHS` months;
  - the balance, with the 50% fall test;
  - assets.
- `FLOW_SOME` = 1,000 for both flows. `_instalment_amount` stays max(1,000, 1 × anchor).
- RL anchor = EMI at both segments: `rl_a1_ability/nodes.py` has no segment branch, and CC still returns NULL at 180+. Conforms to D-U1-2..4 and family rule §1–2.
- Leftovers: none in `src/` (no `FLOW_FLOOR` / `ASSET_FLOOR` / `BALANCE_FLOOR` / `MONEY_OUT_SOME`). The A1 README, the family rule §1–2 and `checks/a1_engine_spec.py` use the new numbers. The 10,000 / 500 hits in `A1_ability_spec.md` are the old workbook and S8 history rows, which the family rule supersedes; no action needed. The only stale text is the GRR workbook builder (Q-S6-22).

## 3. Status of round 1 questions (for cleaning `questions.md`)

| Question | Status |
|---|---|
| Q-S6-01 (matched run vs plan deadline) | **closed by decision** D-U1-1: matching and 7-day chaining are gone |
| Q-S6-02 (plan after obs removes a concluded follow-up) | **moot**: no matching. Under the new fold no later row can remove or re-date an earlier event. |
| Q-S6-03 (RL anchor at 180+) | **closed by decision** D-U1-2 (EMI at both; spec fixed) |
| Q-S6-04 (round trips not netted, tier A) | still open (handoff) |
| Q-S6-05 (bucket-08 fallback needs minimum_due = 0) | still open (data check) |
| Q-01 (RL refusal-month cash) | **closed by decision** D-U1-7 / D-A3-30, coded; R6 / R7 |
| Q-S6-06 (sweepable flag) | still open |
| Q-S6-07 (family rule §4 Unknown text) | still open (spec text) |
| Q-S6-08 (promise on the cutoff day) | **closed by decision** D-U1-1 (belongs to the old event); coded `<=` |
| Q-S6-09 (Unknown rows carry override / points) | still open |
| Q-S6-10 (promised amount: NULL due, RL month end) | **closed by decision** D-U1-6 (NULL dues skipped, coded; the RL month-end part stays). Its floor wording carries on as Q-S6-19. |
| Q-S6-11 (RL zero EMI at 180+) | still open (data check) |
| Q-S6-12 (cancellation not as of obs) | still open; still applies, since plans enter the one stream |
| Q-S6-13 (bureau back-fill not as of obs) | still open |
| Q-S6-14 (`parent_contract_idt` meaning) | still open (data check) |
| Q-S6-15 (`string_key` not applied in A1) | still open |
| Q-S6-16 (`EOSB_PTP_DOCUMENTS`) | still open. Still an event, still no disposition; refusal side unchanged. |
| Q-R-11 / Q-R-12 (D-B-2) | open for the user, as decisions.md says; Q-S6-20 belongs with Q-R-12 |
