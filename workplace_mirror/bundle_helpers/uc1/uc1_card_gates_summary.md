# UC1 card gates (G1, G2, E6): summary

Sources: `uc1_card_gates_cc_60_180.{md,json}` and `uc1_card_gates_rl_60_180.{md,json}` (PROD, snippet
2026-11-28a, persona_end_date 2026-09-30,
UC1 read calls 2026-03-06 .. 2026-07-16, DCORE to 2026-11-25, Genesys / PCA to 2026-11-11). The 180+ models
were not run. No part
reported an error. Aggregates only. Exploration: no pipeline, persona or UC1 rule changed. Cards =
`cc_60_180`, loans = `rl_60_180`.

## a. Tie-outs

**Two mismatches, both a few accounts: accounts with a UC1 reading of any age (n) = 3,525 vs 3,528 expected
(cards) and 679 vs 680 (loans).**
The percentages match (19.2% / 18.2%), so the difference is 3 and 1 accounts; not adjusted, cause not looked
into. Everything else matches
(accounts 18,397 / 3,728; reading under 90 days 7.1% / 8.2%; right-party contact 36.1% / 42.7%; transcript
10.5% / 13.3%; right-party days
holding a conversation result 29% / 30%). UC1 read calls still end 2026-07-16, so nothing is "moved".

## b. Verdict

- **G1 (room to act): cannot be answered for collectors at your cut-offs.** Only 7,293 conversation units and
  578 promise units (cards; 1,544 and
  235 loans) spread over 160-200 handlers a month, so almost no collector reaches 30 rows in a DPD x month
  cell: the collector spread is "not visible"
  for nearly every lever. What the pooled numbers do show: promises are single-payment for every promise (100%
  on 1 instalment, set by rule); the
  promise is a small slice of the outstanding (median 4-5%, p10-p90 2-11%, almost never the full amount); the
  date is the same day for 19-48% and
  on a salary day for 39-52% of promises. Reschedule and settlement could not be measured (plan map below).
  Who chooses is visible for
  promises only (creator `szuserid`).
- **G2 (is the next handler new): yes.** After a read call the next conversation comes within 14 days for 67%
  of cards / 61% of loans (20% none in
  90 days); where the handler is known, 98% of the time it is a different person. Read calls are not special
  (same figures as all staged calls).
  Cards behave like a dialer (median top-handler share 50% of a customer-month's conversations); loans have an
  owner (median 100%).
- **E6 (do collectors react): on the call, yes; afterwards, not shown.** The call's own handler enters a
  promise the same day in 56% of
  "pays in full" calls against 0% of "no payment" calls, and 63% against 3% for capacity full against none
  (cards): the reading and the action
  are one event. In days 1-14 the same handler almost never promises (0-1%), and another handler's promise
  differs for 3 of 16 comparisons
  ("another handler only", read as the customer, not a reaction). Nothing reads "travels" or "lost at
  handover"; the rest is "too thin" or
  "no difference that counts". Loans: all "too thin".
- **What the data cannot show:** actor on reschedule / settlement / waiver / escalation; the minimum due; the
  collector follow-up date (0.1% filled);
  agency placement; anything for 180+ (not run); the call's handler for 72% (cards) and 89% (loans) of
  extracted calls.

## c. Part s0

**Handler field:** `dcore_prm_followup_outcomes.agent_id` (= `szuserid`). Fill: all rows 83.3% cards / 84.9%
loans; call rows 99.9%;
conversation rows 99.1% / 99.6%. `DIALER` never appears (0.0%): the blank rows (about 16%) are the system's.
Distinct human handlers on
conversation rows per month: cards 291, 313, 298, 305, 287, 292 (Mar-Aug); loans 83-104. Genesys:
`agentemailid` in staging (both sources); UC1
index `agent_id` filled for 100% of read calls (196 / 191 distinct agents); the collector master has a name
but no login or e-mail.

**Map between a DCORE user and a Genesys agent:** none in the catalog. Same-day DCORE conversation row on the
CIF gives a unique handler for only
30.5% (cards) / 12.5% (loans) of read calls in the base. Where it exists, the e-mail local part equals the
DCORE user id for 91.6% (n=5,423) /
84.4% (n=403), and 170 of 188 (cards) / 85 of 183 (loans) agent local parts are a DCORE conversation user: a
name map would work.

| lever | dataset, field | range | amount held | who chose |
|---|---|---|---|---|
| promise | `dcore_stg_promiseheader` (`ftotpromiseamt`, `ftotosamt`, `iinstallmentcnt`, dates) + `dcore_prm_promise_instalments` | 2026-03-01 .. 2026-11-26 (5,998 cards / 1,471 loans) | yes, 100% filled | creator `szuserid` 100% (a DCORE user: 100% / 99.7%) |
| reschedule, settlement | `dcore_prm_settlement_summary` (`settlement_type`, `proposed_ts`) | plans from 2023-07 (14,575 / 1,103) | yes (compromise, total due) | not carried; raw `rps_cur_header` has `szproposedby`, `szuserid`, `szauthrizedby`; `authorised_ts` 0% filled |
| waiver | `waiver_pct`, `total_waived`, `rps_cur_waivers.waive_amount` | as plans | yes | flag true for 97% / 86% of plans: not usable |
| escalation | `dcore_prm_allocation_state.is_escalated`, snapshots every 4 days | 2025-01 .. 2026-11 | no | not visible who; 1,798 / 169 N-to-Y events |
| follow-up date | raw `col_his_followup.dtnextaction` | - | no | 0.1% filled: collectors do not set it |
| agency, dispute routing | `szagencycode`; `workflow_state_code` | - | no | not available / vocabulary not decoded |

**Owner or dialer** (customer-months with 2+ conversations, top-handler share p25 / p50 / p75): cards 50 / 50
/ 100% (4,699), distinct handlers p50 2;
loans 67 / 100 / 100% (1,000), distinct handlers p50 1. Cards: dialer (cut-off 60%); loans: owner (cut-off
80%).

## d. G1: room to act (months pooled; DPD bucket 61-90 carries most rows)

| cards, 61-90 | n | overall p10 / p25 / p50 / p75 / p90 | collectors | reading |
|---|---|---|---|---|
| promise amount % of outstanding | 452 | 2 / 3 / 5 / 8 / 11 (0.2% = full amount) | none with 30 rows | not visible |
| days conversation to promise date | 452 | 0 / 1 / 5 / 11 / 16 (19% same day) | none | not visible |
| instalments | 452 | 1 / 1 / 1 / 1 / 1 | - | set by rule (100%) |
| days to next outbound attempt | 3,674 | 1 / 2 / 4 / 9 / 17 | under 10, 5 months | little spread (IQR 0.9 days) |
| followed within 14 d by a promise | 3,705 | 0 / 0 / 0 / 0 / 100 | under 10, 5 months | varies by collector (IQR 16 points; 17% of variance between collectors) |
| followed by a waiver plan / escalation | 3,705 | 0 | under 10, 5 months | little spread (IQR 6 / 0 points) |
| followed by reschedule / settlement | 3,705 | 0 | - | **not measured: type map matched nothing** |

Other cards buckets (91-120, 121-150, 151-180): same pattern, fewer rows, "not visible". Promise bunching
(cards 61-90): round multiple of AED 100 44.5%,
promise date on a salary day (25th to 1st) 38.9%; 91-120: 46.4% / 40.5%; amount = minimum due not available.
Loans (Auto 113, Personal Cash 27,
Personal Loans 23 promises in 61-90): median 3-4% of outstanding, 0% equal to the full amount, round amount
13-41%, salary day 42-52%; every collector
reading "not visible"; only instalments read "set by rule".

## e. G2: next contact after a UC1-read call (b: base within 90 days; all anchors have a full 90-day look-ahead)

Anchors (b): 17,781 cards / 3,217 loans read calls, against (a) 1,013 / 936 and 26,058 / 4,784 calls of
base-family customers. (b) is wider because callers are
early-delinquent and reach 61+ later (16,768 / 2,281 read calls in (b) only).

| next conversation | anchors | 0-3 d | 4-7 d | 8-14 d | 15-30 d | 31-90 d | none in 90 | another handler (of known) | handler unknown | other product |
|---|---|---|---|---|---|---|---|---|---|---|
| cards, read | 17,781 | 39.7% | 18.5% | 9.0% | 6.5% | 6.2% | 20.1% | 98.3% (n=10,692) | 24.7% | 2.5% |
| cards, every staged call | 20,610 | 39.3% | 18.0% | 9.0% | 6.4% | 6.2% | 21.0% | 98.3% | 29.2% | 2.4% |
| loans, read | 3,217 | 35.2% | 16.5% | 9.5% | 9.9% | 8.4% | 20.5% | 97.9% (n=1,992) | 22.1% | 17.6% |
| loans, every staged call | 4,006 | 34.9% | 16.0% | 9.4% | 9.9% | 8.3% | 21.5% | 97.9% | 25.8% | 17.2% |

Next DCORE action of any kind: 0-3 days for 68.0% (cards) / 44.8% (loans), 14 days for 96% / 85%; another
handler 97.7% (n=3,655) / 86.5% (n=289), but the
handler is unknown for 79% / 91% (system rows, and no same-day DCORE user for the call), so this is the
weakest figure. The next conversation is a
transcript in 8,855 of 17,781 (cards) and a DCORE conversation row in 5,350. By queue, cards queues
(FRESHFLOW, XCARDS, CARDS, PREDUE) all sit at 31-46%
within 3 days and 97.9-99.1% another handler. Calls in the loan queues (XLOANS) of card customers: next
contact within 3 days only 8%, none in 90 days
42%, next on another product 52-68%. 98% another handler is about what random assignment among ~200 agents
would give (my arithmetic, not measured).

## f. E6: do collectors act on what was said (cards; 3,367 extracted calls, handler known for 28.1% = about 950 calls; loans 1,274 and 11.1%)

| signal value (cards) | calls | call's handler promises on the day of the call | difference vs the most common level, standardised |
|---|---|---|---|
| capacity: full / partial (ref) / none / not detected | 133 / 373 / 151 / 291 | 63.2% / 38.6% / 2.6% / 31.3% | +25.2 [+15.6, +34.8] / ref / -35.9 [-42.3, -29.5] |
| intent: payback_full / with_delay (ref) / partial / no_payment | 236 / 364 / 159 / 41 | 56.4% / 23.1% / 44.7% / 0.0% | +33.8 / ref / +21.7 / -23.5 |
| reason: has_employment / lost_employment (ref) / increased_obligations / reduced | 246 / 272 / 96 / 102 | 36.6% / 15.1% / 39.6% / 22.5% | +21.8 / ref / +24.9 / +8.1 [-0.9, +15.8] |
| request: restructure / information (ref) / deferral / waiver | 133 / 81 / 59 / 48 | 18.8% / 38.3% / 15.3% / 18.8% | -18.5 / ref / -22.8 / -19.7 |
| dispute: other / system_problem (ref) / scammed | 19 / 88 / 13 | 26.3% / 35.2% / 23.1% | no difference (intervals span 0) |

Raw and standardised differences agree to about a point. These are the call itself (reading and action one
event). **Days 1-14:** the same handler
promises in 0.0-0.8% of calls whatever was said; another handler promises in 8-22% (reason: +13.2 [+5.8,
+19.3] for has_employment vs lost_employment;
no difference for increased or reduced employment). Outbound attempts in days 1-14 and later the same day show
no difference that counts. Readings (promise
and attempt, per value): no "travels", no "lost at handover"; "another handler only" 3 (reason has_employment,
capacity none, intent payback_full);
"no difference that counts" 8; "too thin" the rest, all 18 request and dispute readings. Loans: every reading
"too thin" (for example capacity full 50%
vs partial 15% on the day, n=18 and 46). Escalation within 14 days: 0.4-2.2% of calls, capacity none -1.3
[-2.4, -0.1] points vs partial; waiver plans
under 2%. Reschedule and settlement: all zero (map).

## g. What could not be computed, and what unlocks it

- **Reschedule and settlement (G1, E6): the type map matched nothing.** `settlement_type` codes are PRA
  10,984, PR 1,826, DPS 529, RGLA 527, RGL 515,
  ND 120, HXBL 45, LOJ 16 (cards); PRA 610, PR 204, RGL 184, DPS 69, RGLA 24 (loans). I did not guess their
  meaning: DCORE ops decodes them, then
  `SETTLEMENT_LEVELS` is corrected and the run repeated.
- **Waiver:** the flag is true for 97% / 86% of plans (a waiver row on almost every plan, probably fee lines);
  needs a threshold or a fee-code filter.
- **Plan date and actor:** `proposed_ts` is 35% / 30% filled and `authorised_ts` 0%; raw `rps_cur_header` has
  `dtproposedon`, `szproposedby`, `szuserid`,
  `szauthrizedby`. Staging them would give the plan's date and actor for E6.
- **Collector spread (G1):** a cell of 30 rows per collector is out of reach (about 6 conversations per
  handler per month). Options: pool months per
  collector (a collector's mean over March-August), a minimum of 10, or DPD buckets pooled. Your call; it
  changes the cut-offs.
- **Call's handler for E6 / G2:** the same-day DCORE conversation row exists for 28% (cards) / 11% (loans) of
  extracted calls (a call with no logged row is
  the E20 "unlogged" case). A name map (e-mail local part = DCORE user, 92% / 84% where testable) would lift
  this; it is untested beyond that.
- **Manual check (G2):** `--manual-sample` was not run; the tally table in the README is empty.
- **180+:** not run. UC1 reads almost no 180+ customers (source map), so G1 would be thin too.
- Selection caveat for G2 handler figures: "another handler (of known)" is measured on calls that have a
  handler on both sides (for DCORE next rows, a
  same-day DCORE row), a minority.
