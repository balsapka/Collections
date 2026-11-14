# Council run 2: questions for the user (U1, after round 1)

None of these is applied in the refactor: it keeps today's behaviour for every item. An answer that
asks for a change goes into a fix after the zero-difference refactor step (same bundle 25 only if
the user says so). Severity M first. Full evidence: `round_1/proposals/S6.md`, `S7.md`, `S2.md`, `S3.md`, `S1.md`.

## A. Behaviour and spec questions (S6 correctness)

```
Q-S6-01 [A3 · a3_credibility/sources.py:182-235 `_followup_promises`, :238-275 `_consolidate`, :333] (M, ambiguity; D-P-6 is a Master default, not a user answer) A run matched to a plan is judged from the plan's date and deadline, but it was split on its first row's own cutoff. Follow-ups after the plan's deadline are then never judged.
Now: the fold splits runs on each first row's `promise_cutoff`. `_consolidate` then gives a matched run the plan's `event_date`, and `_cutoff` is recomputed from that date (line 333). Example (month_end, RL 61-180 / all 180+): PTP plan 03-28, follow-ups 04-02, 04-08, 04-14 form one run (cutoff 04-30), and the plan takes it (|04-02 − 03-28| = 5 ≤ 7). The event is judged 03-28..03-31, so the April promises are never judged, though all three come after the event's deadline (03-31). With next_statement, the plan can also sit before a statement that the run's first row is after. | Spec: D-A3-29 "a follow-up starts a new event when it is … after the current event's `promise_cutoff`". For a matched run the current event is the plan event, so the literal reading splits on the plan's cutoff. D-A3-25 matches "nearest follow-up promise within 7 days", which says nothing about the run's later rows.
Options: (a) keep (D-P-6): a matched run takes the plan's date and deadline; its later rows ride with it. (b) match plans to follow-up rows first, then fold: a matched row gives the run the plan's date and cutoff, and a later row after that cutoff starts a new event. (c) keep the split as today, but drop the match when the run's first row is after the plan's cutoff (the run becomes followup_only).
Recommendation: ask the user. (b) is the literal D-A3-29 reading and the rule GRR would expect ("a new promise after a broken one is a new event"). (a) is simpler and what V1j Q0 sized, if Q0 ran on today's code. | Impact: matched events whose run crosses the plan's cutoff. Mostly month_end books, where a plan in the last days of a month meets an early-next-month run. Not visible in the oracle (no such case). Count in the bundle 25 check: matched events with a run row after the plan's cutoff, per model_id. Add a spec case: plan 03-28 + run 04-02..04-14 at month_end.
Answer:
```

```
Q-S6-02 [A3 · a3_credibility/sources.py:238-275 `_consolidate`; signals.py:57-75] (M, bug: look-ahead in history months) A plan that starts up to 7 days after the observation date removes a follow-up event that was already concluded at it.
Now: matching is done once over all history, not as of each observation. Follow-up run 03-25 (month_end: cutoff 03-31, concluded at obs 03-31), DCORE plan 04-01 (distance 7): the pair becomes one event dated 04-01. At obs 03-31 the event is outside the window (`event_date <= obs`), so the concluded 03-25 event disappears. The 04-01 plan was not known on 03-31. The scored latest month never sees future plans, so PROD latest-month output differs from the same month re-scored later, and back-tests on earlier persona months (V1h/V1i style) differ too. | Spec: D-A3-2/D6 point in time; D-A3-25 "concluded once the deadline is on or before the observation date".
Options: (a) accept (only history rows, small) and say so in the spec. (b) match only plans whose start is ≤ the observation date (an as-of match per observation row; a performance cost). (c) let a matched event keep the earlier of the two dates.
Recommendation: (a) for bundle 25, with one spec line. Size it before deciding on (b)/(c), because the persona outputs feed outcome validation. | Impact: month_end books only (RL 61-180, all 180+): follow-up runs in a month's last 7 days that a plan in the next month's first days claims. Next_statement CC is not affected (a run that late is never concluded at month end). Check: Sonnet aggregate per model_id over the persona months, counting matched events with `fu_date ≤ obs < plan_start` and the follow-up concluded at obs.
Answer:
```

```
Q-S6-03 [A1 · rl_a1_ability/nodes.py:15-44 `build_rl_liquidity_anchor`] (M, ambiguity: two spec texts disagree) The RL anchor is the EMI at 180+ as well; the family rule says 180+ uses flat floors.
Now: the RL anchor has no segment check: rl_180_plus scales every threshold with the EMI (income max(3000, 2×EMI), flows max(1000, EMI), assets max(10000, 3×EMI)). CC returns NULL at 180+ (`cc_a1_ability/nodes.py:28-31`). | Spec: `A1_ability_spec.md` S1 "CC 180+: no anchor …; RL: one EMI" (no segment). `A1_ability_family_rule.md` §1: "CC 60–180: oldest bucket; RL: one EMI; **180+ or missing: flat floors only**". CLAUDE.local "A1 essentials" follows S1.
Options: (a) keep: RL keeps the EMI at 180+ (S1); fix the family rule text. (b) NULL at 180+ for both products (family rule §1), in a fix bundle.
Recommendation: ask the user. A written-off loan's EMI is a contractual, not a current, amount (the same reason CC drops its anchor at 180+), which favours (b). | Impact: rl_180_plus rows with a positive `installment_due_amount` in the observation month. The A1 state moves only where an amount sits between the flat floor and the EMI-scaled floor. Check: rl_180_plus crosstab of `liquidity_anchor_amt IS NULL` × state, and old vs new with the anchor nulled (Sonnet what-if).
Answer:
```

```
Q-S6-04 [A1 tier A · nodes/features/casa/feat_cif_casa.py:392-441 `_net_mirrored`] (M, bug against the family rule; handoff, tier A is not edited here) Round trips between two counted legs are never netted.
Now: only a counted leg mirrored by a non-counted, non-salary leg is dropped (`mirrors = legs.filter(~counted & …)`). A debit to the customer's own account elsewhere (`own_out_external`, F3) that comes back within 3 days (`own_in_external`, F2) keeps both legs, so money moved out and back can make F2 **and** F3 strong (High). The same goes for an ATM withdrawal re-deposited as cash (`chosen_spend` + `cash_in`). | Spec: family rule §3 "dropped together with its mirror when the pair is a bounce, reversal, sweep or round trip"; §6.1 "A transfer that returns within 3 days is still netted as a round trip, so moving money out and back does not count twice."
Options: (a) keep and change the spec (only counted-vs-non-counted pairs are netted). (b) Sonnet prompt (`casa_handoff.md`): also net pairs of opposite counted legs (own_out_external ↔ own_in_external at least) within 0–3 days, same amount ±1%.
Recommendation: (b) as a `casa_handoff.md` item, after the workplace confirms its copy matches the mirror (lines 438–487 were not photographed; the workplace Sonnet rewrote this netting). | Impact: CIF-months with a same-amount own-external round trip. The family rule's §6.1 bundle-check line ("how many states these legs move") is the place to count it. Not visible in the oracle.
Answer:
```

```
Q-S6-05 [A3 · cc_a3_payment_credibility/nodes.py:21-66 `_balance_dues`] (M, ambiguity + data check) The bucket-08 fallback needs `minimum_due` = 0 as well; if Way4 sets the minimum due to the whole overdue amount, the fallback never fires.
Now: `_LADDER` is buckets 07..01 **and `minimum_due`**. `_stagnated` = none of them non-zero and bucket 08 non-zero. A statement with only bucket 08 plus a non-zero `minimum_due` takes `due_amount = minimum_due`. Deep in delinquency that may be the whole accumulated overdue amount, so a Dimension B cycle can only qualify by paying all of it. | Spec: D-A3-12 "once the ladder sits in bucket 08 … no bucket holds one month's due … before the first statement where **only bucket 08 holds money**". Whether `minimum_due` counts as "holding money" is not said.
Options: (a) keep (minimum_due is a slot of the ladder). (b) treat "only 08" as buckets 01–07 empty, whatever the minimum due (fallback = the 12-month baseline).
Recommendation: data check first (Sonnet aggregate, cc_60_180 and cc_180_plus, latest month): statements with buckets 01–07 = 0 and bucket 08 > 0, split by `minimum_due` = 0 / > 0, and the ratio `minimum_due / overdue_bucket_08`. If `minimum_due ≈ bucket 08` on most of them, ask the user (b). | Impact: CC Dimension B at 180+ (Regular / qualifying cycles); none if Way4 zeroes the minimum due in that state.
Answer:
```

```
Q-01 [A3 · rl_a3_payment_credibility/nodes.py:48-60 + a3_credibility/signals.py:290 `_paid_after_refusal`] (L, conforms to D-A3-14; asymmetric with D-A3-25)
Assessment: the code follows the spec. D-A3-14 says "`total_paid` ≥ 100 AED in **a month after the refusal month**". `pay_from` (the 1st) > the refusal day gives exactly that, including a refusal on the 1st (equal, so it does not count). D-A3-22 (Q-29) "a month with 100 AED or more paid after the refusal day" is looser, but it was meant as the unit (cycle / month), not as a change to D-A3-14. What is worth writing down: the promise rule handles the same month-level uncertainty the other way. D-A3-25 counts the event month's cash in full (`sources.py:343-346`), even cash that came before the promise. So on loans the month's cash favours the customer for a promise and counts against them for a refusal. Cards treat both by day.
Recommendation: (a) keep, and add one line to D-A3-14 / D-A3-22: "RL: the refusal month's cash never lifts a refusal (cash is dated only to the month, so it may predate the refusal); promise events count the event month in full." Revisit with the "RL exact payments" option (`prm_loan_payments`), which would remove both approximations. | Impact: RL refusal rows whose only cash after the refusal is in the refusal month. Bundle 25 check: per rl model_id, `a3_refusal_flag` rows whose refusal month has `total_paid` ≥ 100.
Answer:
```

```
Q-S6-06 [A1 · a1_ability/classify.py:250] (L, bug against the spec; diagnostic only) `a1_sweepable_balance_flag` is the whole balance-strong rule over W, not "balance strong in the observation month".
Now: `balance_strong(amt, w)`: ≥ max(3000, anchor) in 2 of 3 (3 of 6) months **and** not > 50% below the prior window. A customer whose balance was swept in the observation month (m1 = 100, m2 = m3 = 3500) is flagged. One who holds 9,000 in m1 only is not. | Spec: family rule §4 "`a1_sweepable_balance_flag` = balance strong in the observation month. It marks a delinquent customer holding money above the floor now."
Options: (a) keep and change the spec text ("the balance branch of F2 is strong"). (b) flag = `casa_m1 ≥ max(3000, anchor)`.
Recommendation: ask the user. (b) matches the stated purpose (an operational lead "now"). | Impact: diagnostic column only, no state moves. Crosstab old vs new flag per model_id.
Answer:
```

```
Q-S6-07 [A1 · a1_ability/classify.py:224-225; spec test `checks/a1_engine_spec.py:280-281`] (L, spec text) The Unknown gate still needs "no counted CASA leg in W" (S11), which the family rule's §4 table leaves out.
Now: `unknown_also = casa_active == 0`, so a row with counted legs below the "some" floors (money in < 1000, money out < 500 every month) and no family evidence is **Low**. The spec test encodes this ("0 points, a third-party credit -> Low"). | Spec: family rule §4 "Unknown: no evidence in any family"; §2 F2 and §6.5 imply the S11 gate is kept with the counted classes.
Options: (a) keep; add "and no counted CASA leg in the window (S11)" to §4. (b) drop the gate, so §4 is literal (rows move Low → Unknown).
Recommendation: (a). Code and spec test agree, and §6.5 sizes the gate. | Impact: none for (a). For (b), rows whose only evidence is a small counted leg.
Answer:
```

```
Q-S6-08 [A3 · a3_credibility/sources.py:205] (L, ambiguity; boundary) A follow-up dated exactly on the run's cutoff day joins the run, and its own promise is never judged.
Now: `row.event_date > run.cutoff` (strict). With next_statement, a promise made on the statement day S that ends the current run joins it. The run's payment window ends that day, so the new promise (its own cutoff is the next statement) gets no window. With month_end, a promise on the last day joins too; on cards its own window would be empty anyway (D-A3-29's V1j note), on loans it is the same month's cash. Exactly 7 days apart = same run, 8 = new run: conforms ("less than 8 days apart"). | Spec: D-A3-29 "after the current event's `promise_cutoff`" (the cutoff day itself is not "after"); D-A3-28 "paying on the deadline day counts".
Options: (a) keep (literal; the cutoff day belongs to the old event). (b) `>=`: a promise on the cutoff day starts a new event.
Recommendation: (a), with a spec case (next_statement, follow-up on the statement day) so the boundary is pinned. The spec test has no cutoff-day, 7-vs-8-day or same-day-two-names case today. | Impact: CC 61-180 follow-ups made on a statement day inside a run; small.
Answer:
```

```
Q-S6-09 [A3 · a3_credibility/classify.py:76-88; signals.py:321-323] (L, output coherence) Unknown (`no_episode`) rows still carry points, `a3_override = refusal` and `a3_reason`.
Now: with no anchor, every builder falls back to the observation lookback (contacts: the last 24 months), so a refusal, points and a reason are computed. Only `a3_state` is overwritten to Unknown. A row can read Unknown + `a3_override = refusal`. | Spec: D-A3-27 "Unknown stays only for rows with no episode anchor"; D-A3-17 wants every input carried, but says nothing about override / reason on Unknown rows.
Options: (a) keep (the signals are informative; the state says Unknown). (b) NULL `a3_override` / `a3_reason` (and points?) on Unknown rows, as A1 does for `a1_unknown_reason`.
Recommendation: (a) plus one line in the output doc; (b) only if GRR reads `a3_override` without the state. | Impact: no_episode rows with a refusal in the last 24 months; no state change.
Answer:
```

```
Q-S6-10 [A3 · a3_credibility/sources.py:335-342 (`_due`)] (L, ambiguity) "The due of the cycle open on the event day (the last known one)" takes the latest cycle even when its due is NULL; an RL promise on a month end reads the next month's EMI.
Now: `max(struct(cycle_start, due_amount))` over cycles with `cycle_start ≤ event_date`. (1) If the latest cycle's due is NULL (CC: no balance row, or nothing due), `promise_amount` = 100 AED instead of the last known due. (2) RL cycles start on the previous month end, so a promise on 03-31 picks the April cycle and April's EMI. That snapshot postdates an obs of 03-31 (look-ahead), and at the latest month it does not exist yet, so the same event reads March's EMI there. | Spec: D-A3-25 "the due of the cycle open on the event day (the last known one, at least 100 AED)".
Options: (a) keep. (b) skip NULL dues (`max` over non-NULL `due_amount`) and use `cycle_start < event_date` for RL.
Recommendation: (a); revisit with the promise-points work (bundle 25's undecided list). | Impact: EMI changes are rare and NULL dues mostly mean nothing due, so few outcomes move. Check: events whose chosen due is NULL; RL events on a month end.
Answer:
```

```
Q-S6-11 [A3 · rl_a3_payment_credibility/nodes.py:30-45] (L, data check) At rl_180_plus a written-off loan's EMI may be 0, so Dimension B "Regular" cannot be reached on loans; CC has the bucket-08 baseline for the same problem (D-A3-12).
Now: `due_amount` = the month's EMI, else the last non-NULL one. An EMI of 0 is kept (not NULL), and `qualifies` needs `due > 0`. D-A3-13 covers only a missing snapshot. | Spec: D-A3-13 (missing EMI only); D-A3-12 gives CC a fallback; RL has none.
Options: (a) keep. (b) treat 0 as missing (the last positive EMI).
Recommendation: data check first: rl_180_plus latest month, rows whose B-window months have `monthly_emi_due` = 0 / NULL / > 0. Ask the user only if 0 is common. | Impact: rl_180_plus Dimension B level (Regular vs Some).
Answer:
```

```
Q-S6-12 [A3 · a3_credibility/sources.py:123, 130-131 `build_instalments`] (L, look-ahead in history months) Cancellation is today's status, not the status as of the observation.
Now: `is_cancelled` and the cancelled instalment statuses are read as loaded. A plan cancelled after an observation date is missing from that observation's events and from the refusal "followed by a plan" test. | Spec: D-A3-25 "every non-cancelled PTP and settlement plan"; D-A3-2 point in time. Neither says "as of when".
Options: (a) accept (the latest month, which PROD scores, is right). (b) as-of cancellation, if DCORE keeps a cancel date.
Recommendation: (a), one spec line; note it for back-tests on earlier months. | Impact: history rows only.
Answer:
```

```
Q-S6-13 [A1 · nodes/features/bureau/feat_cif_bureau_salary_monthly.py:25-40; a1_ability/signals.py:115-176] (L, look-ahead in history months) The unified bureau salary is not as of the observation: bulk-pull months are back-filled 12 months from the load date, and salary_credit is an application-time look-back.
Now: a pull loaded 2026-09 gives rows for 2025-09..2026-08, which a 2026-03 observation already reads. | Spec: family rule §1 "every signal comes from W or the observation-month snapshot" (window, not knowledge time); the source description itself says the pull is inferred back.
Options: (a) accept and say so (~1% of 61–180 CIFs, `bulk_pull_results.md`). (b) cap each row at its load date (needs a load stamp on the unified table: DE ask).
Recommendation: (a) now; add the load stamp to the DE asks for when pulls repeat. | Impact: history rows of ~1% of CIFs (bulk) plus salary_credit rows (0.0–0.6%). Matters for outcome validation, not for latest-month scoring.
Answer:
```

```
Q-S6-14 [A1 · nodes/features/products/feat_cif_cross_product.py:136-139 `_cards`; nodes/primary/products/prm_products.py:54-74] (L, data check) `parent_contract_idt` is read as "the contract a newer one replaced". In Way4 it is often the card → account hierarchy link.
Now: every contract named as a parent is dropped as "replaced". If Way4 uses `parent_contract_idt` for card contracts under their account contract, account contracts with cards are dropped and card-level contracts stay. F4 could then count the scored account's own card contracts (≠ `account_id`) as "another card", or miss the CIF's other accounts. | Spec: family rule §2 F4 "the customer's other cards, not supplementaries of the same contract".
Options: (a) keep (B24 found products "as expected"; bundle 21's logic). (b) Sonnet aggregate: share of `prm_card_contracts` parents that are account-level contracts, and of `prm_card_month_end` rows whose contract has a parent.
Recommendation: (b), one aggregate before GRR reads F4 card results. | Impact: F4 card branch (`xp_current`, `xp_instalment_max`) on CC and RL.
Answer:
```

```
Q-S6-15 [A1 · cc_a1_ability/nodes.py:38, rl_a1_ability/nodes.py:29, a1_ability/signals.py:294-296, feat_cif_bureau_bounces_monthly.py:35, prm_products.py:173] (L, run 1 Q-21 accepted but not applied in A1) Keys are still normalised in different ways.
Now: A1 anchors and the cross-product feature use plain `cast("string")` on `contract_id` / `account_id` / `product_account_id` / `cust_num`. A3 uses `_common.string_key`, which casts doubles to long and trims. The bureau salary `cif_id` is trimmed, the bounces `cif_id` is not, and Way4 `ident_number` is trimmed. | Expected: run 1 Q-21 (b) "one key helper on every axis" (accepted 2026-11-05).
Options: (a) keep. (b) `string_key` everywhere in A1 (a refactor proposal for S1/S3; the oracle proves no value changes with today's types).
Recommendation: (b), with the golden check; flag any source whose type would change a value. | Impact: none with today's types; guards a double / padded source.
Answer:
```

```
Q-S6-16 [A3 · _dcore_codes.py:285-300 `PROMISE_EVENT`; a3_credibility/signals.py:247-254 `_DISPOSITIONS`] (L) `EOSB_PTP_DOCUMENTS` is a promise event but no contact disposition, so it never lifts a refusal; `HISTORICAL PROMISE TO PAY` is an event and a `ptp` disposition but not right-party.
Now: a refusal followed by `EOSB_PTP_DOCUMENTS` stays a refusal, though D-A3-25 counts it as a promise event (not a plan, so the `planned` test misses it too). | Spec: D-A3-20 "no PTP / settlement … followed it"; the `_dcore_codes` comment says both names are near-empty.
Options: (a) keep (near-empty). (b) add `EOSB_PTP_DOCUMENTS` to the `ptp` disposition.
Recommendation: (a). | Impact: near zero.
Answer:
```

## B. Refactor decisions that are the user's (held, not applied)

```
Q-R-01 [dead code · tier D?] Delete `_spine_utils.py`, `rl_a4_spine/`, `rl_spell_table/`, `cc_spell/` with `build_cc_limits` / `crx_cc_limits` (9 files, ~1,060 lines; S7 A-01, patch `round_1/proposals/S7_A_held.patch`).
Now: Cartographer and S7 both find no reader in the mirror. The mirror cannot rule out workplace-only readers.
Needs: the workplace grep (`00_baseline/inventory.md` §6) pasted back; then the user's approval of the list. The registry lines (imports 75, 98, 100; entries 238, 250, 251) and 4 catalog entries go as named edits by the UAT Sonnet.
Recommendation: delete once the grep is clean.
Answer:
```

```
Q-R-02 [scoring_engine.py · S7 B-04] Scorecard options nothing uses: override modes `CAP` / `FORCE`, `Override.mode` / `to`, `high_min_dimensions`, `high_current` (-18 lines; the A1 spec test changes with it).
Now: neither A1 nor A3 passes them. Run 1 (D-2-3) kept them for the A1 redesign and A3; both are built now without them.
Options: (a) remove; (b) keep until promise points / Broken +1 and the A1 High options are decided.
Recommendation: (b) for bundle 25: the undecided A3 points rules and A1's "internal Stable -> High" option are the cases they were kept for.
Answer:
```

```
Q-R-03 [a3_credibility `build_instalments` · S7 B-06] The persisted instalments table carries `due_amount` and `payment_amount`, which nothing reads since promises are judged by payment (D-A3-25).
Options: (a) drop the two columns (output columns of a persisted dataset: hard rule 5); (b) keep.
Recommendation: (b) until the promise-amount question (Q-S6-10) is settled; they are the DCORE promised amounts.
Answer:
```

```
Q-R-04 [catalog · S2-03] `crx_<p>_a3_dues` and `crx_<p>_a3_payments` are memory-only and read by three nodes each, so the CC dues plan is computed three times.
Options: (a) persist both (two catalog entries per product; needs the workplace catalog checked first); (b) keep.
Recommendation: (a), after a UAT look at the workplace catalog; the largest remaining A3 cost in PROD.
Answer:
```

```
Q-R-05 [`_common.require_columns` vs `frames.require_columns` · S3-01] Two helpers do the same check with different error text.
Options: (a) one helper (the error text of a failing run changes; workplace tests that assert the text need an update); (b) keep both.
Recommendation: left to R-O's ruling in the round 1 review; say so if you have a preference.
Answer:
```

```
Q-R-06 [cc_raw_extract · Q-S3-1] `cc_raw_extract` reads raw Way4 tables inside a persona pipeline (the known exception to "no raw_ / stg_ inputs").
Options: (a) keep the exception in bundle 25; (b) later: primary-layer `prm_cc_*` tables bounded by parameters, scoped in the CC A3 wrapper as RL does.
Recommendation: (a) now, (b) as its own bundle (D-A3-18 already lists it as a later option).
Answer:
```

```
Q-R-07 [casa features, tier A · S2-H1, S3-H1, S7 H-01] `feat_cif_casa_activity_monthly` and `feat_cif_ext_card_payment_monthly` have no reader in the mirror; the activity node scans the whole CASA transaction history.
Needs: a workplace reader grep. If none: stop building them (through the Sonnet handoff).
Recommendation: add both names to the workplace grep of Q-R-01.
Answer:
```

```
Q-R-08 [A1 source floors · S1-01, applied] The A1 income / distress / EOSB / RL anchor nodes now take `params:crx_persona` and floor their sources at the persona start minus the look-back, instead of four Spark actions on the obs base (run 1 D-2-5). Outputs are identical; one error path differs: the "returns history too short" guard can fire when the obs base has no row in the persona start month.
Options: (a) keep in bundle 25; (b) take it out.
Recommendation: (a).
Answer:
```

```
Q-R-09 [prm_products.py `_latest_in_month` · S2-10, applied] The latest row per card and month is now `max(struct(day, value))` instead of `row_number` ordered by day.
Now: identical when a card has one row on its latest day in the month. With two rows on that day the old pick was arbitrary (it could change between runs); the new one always takes the larger `level` / `minimum_due`.
Options: (a) keep (deterministic; the bundle check counts cards with two rows on the latest day); (b) revert to the window.
Recommendation: (a).
Answer:
```

```
Q-R-10 [a3_credibility/signals.py `_contact_summary` · R-I N-1] When an account's latest contact day has several dispositions, the one kept is decided last by the alphabetical order of the labels.
Now: unchanged from before the refactor in outcome (the oracle passes), but the order is not written anywhere as a rule. Round 2 names it as a constant with the same order.
Options: (a) keep today's order and write it into the spec (Q-28); (b) give the order you want (for example refusal > promise > contact > no pick-up).
Recommendation: (a) for bundle 25; say so if GRR has an order.
Answer:
```

```
Q-R-11 [A3 promise deadline · promises.py `_cutoff`, applied with the new event rule] The next-statement deadline is capped at 31 days after the promise.
Now: the deadline is the first statement after the promise day; when the next statement on record is more than 31 days later (statements missing from the history), the deadline is day + 31. Before, such an event waited for whatever statement came next, which under the new rule kept an old promise alive for months.
Options: (a) keep the cap; (b) no cap.
Recommendation: (a).
Answer:
```

```
Q-R-12 [A3 refusal · signals.py `_paid_after_refusal`, applied with D-A3-30] On cards a payment dated on the refusal day itself also lifts the refusal.
Now: "penalise only when certain" is applied to both products: loans by month, cards by day. A card payment on the same day as the refusal may have come before or after the call.
Options: (a) keep (same-day payment lifts); (b) cards need a payment on a later day.
Recommendation: (a), the same principle as on loans.
Answer:
```
