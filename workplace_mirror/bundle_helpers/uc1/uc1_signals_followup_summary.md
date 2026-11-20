# UC1 signals follow-up: CIF-level matching and transcript promises as A3 events

Source: `results_uc1_signals_followup_cc_60_180.md`, `results_uc1_signals_followup_rl_60_180.md`
(snippet 2026-11-20a, PROD, full run). Rates are `pay30_due` / `pay45_any` after the call (E tables)
or `paid_due` / `paid_any` after the month end (W tables). `<10` = masked cell.

**Scope note: item 1 of the prompt (Part A / B-F for `cc_180_plus`, `rl_180_plus`) was NOT run.**
The 180+ CIFs are not in the UC1 sample so far (user, 2026-11-20), so there is nothing to measure
and no 180+ verdict in this file.

## Check W0: rebuild without transcripts vs persisted (exact counts)

The engine's own merge, deadline and Dimension A / scorecard functions were run on the persisted
inputs without the transcript days. Every difference is 0, so the what-if tables below are trusted.

| model_id | events persisted | rebuilt | in both | event diffs | level diff | state diff |
|---|---|---|---|---|---|---|
| cc_60_180 | 466 | 466 | 466 | 0 / 0 / 0 | 0 of 338 | 0 of 338 |
| rl_60_180 | 93 | 93 | 93 | 0 / 0 / 0 | 0 of 192 | 0 of 192 |

## E5c.1 Transcript promises vs DCORE promises, CIF level (any account of the CIF)

| model_id | group | n_conv | pay30_due | pay45_any |
|---|---|---|---|---|
| cc_60_180 | transcript promise (all) | 240 | 16.9% | 27.5% |
| cc_60_180 | matched at CIF +-3 | 60 | <10 | 24.6% |
| cc_60_180 | matched at CIF +-7 | 96 | 11.1% | 21.2% |
| cc_60_180 | still unmatched at CIF +-3 | 180 | 17.5% | 28.4% |
| cc_60_180 | still unmatched at CIF +-7 | 144 | 20.5% | 31.4% |
| cc_60_180 | no promise at all, CIF +-3 | 287 | 17.3% | 25.4% |
| cc_60_180 | no promise at all, CIF +-7 | 258 | 18.2% | 26.3% |
| cc_60_180 | DCORE promise on the CIF +-3 | 130 | 15.5% | 23.9% |
| cc_60_180 | DCORE promise on the CIF +-7 | 195 | 12.7% | 21.6% |
| rl_60_180 | transcript promise (all) | 109 | 49.5% | 63.1% |
| rl_60_180 | matched at CIF +-3 | 13 | <10 | <10 |
| rl_60_180 | matched at CIF +-7 | 16 | <10 | <10 |
| rl_60_180 | still unmatched at CIF +-3 | 96 | 48.0% | 63.3% |
| rl_60_180 | still unmatched at CIF +-7 | 93 | 48.4% | 64.2% |
| rl_60_180 | no promise at all, CIF +-3 | 211 | 33.5% | 50.0% |
| rl_60_180 | no promise at all, CIF +-7 | 197 | 30.4% | 48.3% |
| rl_60_180 | DCORE promise on the CIF +-3 | 28 | 41.7% | 41.7% |
| rl_60_180 | DCORE promise on the CIF +-7 | 45 | 50.0% | 50.0% |

## E5c.2 Shares: unmatched transcript promises that become matched, and the reverse flag

| model_id | share | num | den | % |
|---|---|---|---|---|
| cc_60_180 | account +-3 unmatched, matched at CIF +-3 | <10 | 187 | <10 |
| cc_60_180 | account +-3 unmatched, matched at CIF +-7 | 43 | 187 | 23.0% |
| cc_60_180 | transcript promises unmatched at CIF +-3 | 180 | 240 | 75.0% |
| cc_60_180 | transcript promises unmatched at CIF +-7 | 144 | 240 | 60.0% |
| cc_60_180 | DCORE promises (CIF +-3) with intent not stated / no_payment | 45 | 130 | 34.6% |
| cc_60_180 | DCORE promises (CIF +-7) with intent not stated / no_payment | 65 | 195 | 33.3% |
| rl_60_180 | account +-3 unmatched, matched at CIF +-3 | <10 | 99 | <10 |
| rl_60_180 | account +-3 unmatched, matched at CIF +-7 | <10 | 99 | <10 |
| rl_60_180 | transcript promises unmatched at CIF +-3 | 96 | 109 | 88.1% |
| rl_60_180 | transcript promises unmatched at CIF +-7 | 93 | 109 | 85.3% |
| rl_60_180 | DCORE promises (CIF +-3) with intent not stated / no_payment | <10 | 28 | <10 |
| rl_60_180 | DCORE promises (CIF +-7) with intent not stated / no_payment | 19 | 45 | 42.2% |

Stated intent `no_payment` never occurs next to a DCORE promise (0 conversations in both models,
both windows): the reverse flag is entirely "intent not stated".

## E6c Stated dispute vs `a3_dispute_flag` at the next month end, account and CIF level

| model_id | group | n_conv | pay30_due | pay45_any |
|---|---|---|---|---|
| cc_60_180 | stated dispute, account flag false | 65 | 19.4% | 37.5% |
| cc_60_180 | stated dispute, CIF flag false | 66 | 17.9% | 34.6% |
| cc_60_180 | stated dispute, CIF flag true | <10 | <10 | <10 |
| cc_60_180 | stated dispute, account flag false but CIF flag true | 0 | - | - |
| cc_60_180 | stated dispute, no A3 row at the next month end | 90 | <10 | 14.1% |
| cc_60_180 | no stated dispute, CIF flag true | <10 | <10 | <10 |
| cc_60_180 | no stated dispute, CIF flag false | 226 | 28.7% | 40.1% |
| rl_60_180 | stated dispute, CIF flag false | 36 | 45.9% | 56.8% |
| rl_60_180 | stated dispute, CIF flag true | 0 | - | - |
| rl_60_180 | stated dispute, no A3 row at the next month end | 10 | <10 | <10 |
| rl_60_180 | no stated dispute, CIF flag true | 0 | - | - |
| rl_60_180 | no stated dispute, CIF flag false | 227 | 35.1% | 51.2% |

## E5.3c DCORE promise events by whether a conversation of the CIF lies within +-3 / +-7 days

| model_id | window | conversation | n events | pay30_due | pay45_any |
|---|---|---|---|---|---|
| cc_60_180 | +-3 | no conversation | 3,978 | 41.2% | 52.4% |
| cc_60_180 | +-3 | with a conversation | 246 | 14.6% | 17.5% |
| cc_60_180 | +-7 | no conversation | 3,909 | 41.2% | 52.5% |
| cc_60_180 | +-7 | with a conversation | 315 | 19.7% | 22.9% |
| rl_60_180 | +-3 | no conversation | 592 | 45.8% | 66.6% |
| rl_60_180 | +-3 | with a conversation | 25 | 44.0% | 48.0% |
| rl_60_180 | +-7 | no conversation | 588 | 45.6% | 66.3% |
| rl_60_180 | +-7 | with a conversation | 29 | 48.3% | 55.2% |

## E5.3d The same by event kind and source (window +-3; `matched` = plan and follow-up promise)

| model_id | conversation | kind / source | n events | pay30_due | pay45_any |
|---|---|---|---|---|---|
| cc_60_180 | none | followup_only / followup | 1,252 | 50.7% | 64.4% |
| cc_60_180 | none | matched / ptp | 419 | 32.7% | 48.0% |
| cc_60_180 | none | matched / settlement | 245 | 36.3% | 45.7% |
| cc_60_180 | none | table_only / ptp | 88 | 43.2% | 61.4% |
| cc_60_180 | none | table_only / settlement | 1,974 | 37.4% | 46.1% |
| cc_60_180 | with | followup_only / followup | 81 | 18.5% | 25.9% |
| cc_60_180 | with | matched / ptp | 78 | <10 | <10 |
| cc_60_180 | with | matched / settlement | 25 | <10 | <10 |
| cc_60_180 | with | table_only / settlement | 60 | 16.7% | 18.3% |
| rl_60_180 | none | followup_only / followup | 295 | 41.7% | 59.3% |
| rl_60_180 | none | matched / ptp | 151 | 51.7% | 66.9% |
| rl_60_180 | none | matched / settlement | 14 | <10 | 85.7% |
| rl_60_180 | none | table_only / settlement | 130 | 47.7% | 81.5% |
| rl_60_180 | with | followup_only / followup | 15 | <10 | <10 |

## E5.3e The same by the first follow-up code (window +-3); due = pay30_due, any45 = pay45_any

| model_id | code | n none | due none | any45 none | n with | due with | any45 with |
|---|---|---|---|---|---|---|---|
| cc_60_180 | (no follow-up code) | 2,062 | 37.6% | 46.8% | 62 | 17.7% | 19.4% |
| cc_60_180 | PROMISE TO PAY SCHEDULED | 1,139 | 47.5% | 61.5% | 81 | 19.8% | 22.2% |
| cc_60_180 | CODE25 WILL PAY AT SALARY | 311 | 45.0% | 56.3% | 43 | <10 | 23.3% |
| cc_60_180 | PROMISE TO PAY | 269 | 44.6% | 56.9% | 60 | <10 | <10 |
| cc_60_180 | DIGITAL COLLECT PTP SUBSCRIBED | 190 | 30.5% | 46.3% | 0 | - | - |
| rl_60_180 | (no follow-up code) | 132 | 47.0% | 80.3% | <10 | <10 | <10 |
| rl_60_180 | PROMISE TO PAY SCHEDULED | 202 | 33.7% | 51.5% | 13 | <10 | <10 |
| rl_60_180 | CODE25 WILL PAY AT SALARY | 110 | 59.1% | 77.3% | <10 | <10 | <10 |
| rl_60_180 | PROMISE TO PAY | 89 | 57.3% | 70.8% | <10 | <10 | <10 |
| rl_60_180 | DIGITAL COLLECT PTP SUBSCRIBED | 56 | 42.9% | 58.9% | 0 | - | - |

## W1 What-if inputs and reach (extra promise day = call date, on every paired account of the CIF)

| model_id | item | n |
|---|---|---|
| cc_60_180 | transcript promises (conversations) / still unmatched at CIF +-7 | 240 / 144 |
| cc_60_180 | extra promise days / accounts with one | 156 / 118 |
| cc_60_180 | scored account-months of the model, 2026-03 .. 07 / accounts | 80,395 / 32,630 |
| cc_60_180 | account-months of the accounts with an extra day | 338 |
| cc_60_180 | account-months whose Dimension A level changes / whose state changes | 42 / 15 |
| rl_60_180 | transcript promises (conversations) / still unmatched at CIF +-7 | 109 / 93 |
| rl_60_180 | extra promise days / accounts with one | 95 / 56 |
| rl_60_180 | scored account-months of the model, 2026-03 .. 07 / accounts | 15,217 / 6,456 |
| rl_60_180 | account-months of the accounts with an extra day | 192 |
| rl_60_180 | account-months whose Dimension A level changes / whose state changes | 64 / 36 |

## W2 Dimension A level changes: moved rows beside the unmoved rows at the level they leave / join

Each outcome cell: moved / leaves / joins. The 3-month outcome exists for month ends 2026-03 .. 05
only (payments end 2026-08-31); the 1-month outcome for 03 .. 07. Moved rows at `cc_60_180` are
masked in every transition except one.

| model_id | transition | n | paid_due 1m | paid_any 1m |
|---|---|---|---|---|
| cc_60_180 | no_promise -> promised | 21 | <10 / 4.8% / 14.7% | <10 / 5.6% / 16.5% |
| cc_60_180 | the four other transitions | each <10 | <10 | <10 |
| rl_60_180 | promised -> partly_kept | 17 | 64.7% / 24.6% / 30.6% | 70.6% / 34.3% / 40.2% |
| rl_60_180 | no_promise -> partly_kept | 18 | <10 / 13.7% / 30.6% | 72.2% / 19.3% / 40.2% |
| rl_60_180 | no_promise -> promised | 26 | 38.5% / 13.7% / 24.6% | 50.0% / 19.3% / 34.3% |
| rl_60_180 | the two other transitions | each <10 | <10 | <10 |

*(continued: paid_due 3m)*

| model_id | transition | paid_due 3m |
|---|---|---|
| cc_60_180 | no_promise -> promised | <10 / 8.1% / 22.6% |
| cc_60_180 | the four other transitions | <10 |
| rl_60_180 | promised -> partly_kept | <10 / 42.9% / 54.8% |
| rl_60_180 | no_promise -> partly_kept | <10 / 25.1% / 54.8% |
| rl_60_180 | no_promise -> promised | <10 / 25.1% / 42.9% |
| rl_60_180 | the two other transitions | <10 |

## W3 A3 state changes (Dimension A moved; B, C, refusal as persisted)

| model_id | transition | n | paid_due 1m | paid_any 1m |
|---|---|---|---|---|
| cc_60_180 | low -> moderate, moderate -> high, high -> moderate | each <10 | <10 | <10 |
| rl_60_180 | low -> moderate | 17 | <10 / 10.6% / 27.3% | <10 / 15.4% / 37.3% |
| rl_60_180 | moderate -> high | 18 | 72.2% / 27.3% / 44.6% | 77.8% / 37.3% / 54.6% |
| rl_60_180 | high -> moderate | <10 | <10 | <10 |

## W4 All scored account-months by persisted Dimension A level (scale for W2)

| model_id | level | n account-months | paid_due 3m | paid_due 1m |
|---|---|---|---|---|
| cc_60_180 | kept | 2,988 | 40.7% | 28.4% |
| cc_60_180 | partly_kept | 21,263 | 32.3% | 21.2% |
| cc_60_180 | promised | 13,698 | 22.6% | 14.7% |
| cc_60_180 | no_promise | 42,446 | 8.2% | 4.8% |
| rl_60_180 | kept | 548 | 55.6% | 38.7% |
| rl_60_180 | partly_kept | 2,899 | 54.8% | 30.6% |
| rl_60_180 | promised | 2,377 | 43.2% | 24.9% |
| rl_60_180 | no_promise | 9,393 | 25.3% | 13.8% |

## W5 Share of A3 promise events that would come from transcripts (event day 2026-03-06 .. 07-16)

| model_id | item | value |
|---|---|---|
| cc_60_180 | persisted promise events of the model | 13,405 |
| cc_60_180 | events of the model with transcripts added | 13,503 |
| cc_60_180 | events started by a transcript promise / containing a transcript day | 112 / 131 |
| cc_60_180 | share started by a transcript, extracted conversations only | 0.8% |
| cc_60_180 | extraction coverage (extracted / all conversations in range) | 39.8% |
| cc_60_180 | share if every call were extracted | 2.1% |
| rl_60_180 | persisted promise events of the model | 2,211 |
| rl_60_180 | events of the model with transcripts added | 2,278 |
| rl_60_180 | events started by a transcript promise / containing a transcript day | 68 / 69 |
| rl_60_180 | share started by a transcript, extracted conversations only | 3.0% |
| rl_60_180 | extraction coverage (extracted / all conversations in range) | 70.1% |
| rl_60_180 | share if every call were extracted | 4.2% |

## W6 State AUC on paid_due: persisted A3 vs transcripts added (account bootstrap, 200 draws)

| model_id | window | n | state changes | AUC base | AUC what-if | diff | 95% interval |
|---|---|---|---|---|---|---|---|
| cc_60_180 | 3m | 45,016 | <10 | 0.760 | 0.760 | +0.0001 | [-0.0000, +0.0002] |
| cc_60_180 | 1m | 80,395 | 15 | 0.769 | 0.769 | -0.0000 | [-0.0000, +0.0001] |
| rl_60_180 | 3m | 7,975 | 14 | 0.691 | 0.692 | +0.0009 | [+0.0000, +0.0019] |
| rl_60_180 | 1m | 15,217 | 36 | 0.680 | 0.681 | +0.0005 | [-0.0002, +0.0013] |

## Reading notes

- Groups in E5c.1 are not adjusted for A1 / A3 state or DPD band; "no promise at all" now includes
  promise intents with neither amount nor date (the first run dropped them through a NULL, see the
  README).
- W2 / W3 moved rows are customers who made a recorded promise on a call, so they are a selected
  group; paying above both the level they leave and the one they join describes promise-makers, not
  proof that the new level is right. Their n is small (17-26).

## Verdicts

- **Full-run coverage at 180+ (A):** not run. The 180+ CIFs are not in the UC1 sample, so there is
  no 180+ verdict.
- **Do transcript promises carry evidence DCORE misses (E5):** yes at `rl_60_180`, weakly at
  `cc_60_180`. Widening to the CIF makes only the cards' +-7 window move a visible share, and most
  transcript promises stay without a DCORE promise within a week on the CIF in both models (E5c.2).
  The unmatched ones pay clearly more than "no promise at all" at RL and slightly more at CC, while
  the matched ones pay no better (E5c.1); not adjusted for state.
- **Does the CIF level change E6:** no. A stated dispute is not matched by the flag at account or
  CIF level (matched cells are `<10` or 0), and RL has no dispute flags at all; a stated dispute
  goes with lower `pay30_due` at CC and higher at RL, both on small n.
- **Why DCORE promise events without a conversation pay much more than those with one (E5.3):** not
  promise source or code. The gap at CC is present inside every source (follow-up only, table only,
  matched) and inside each follow-up code with enough n; the source mix differs a little between the
  groups but does not carry it. The data here cannot say what does (which events get a recorded call
  is a selection we have not measured); at RL the gap is small on `pay30_due` and the with-call n is
  25.
- **Do transcript promises help as A3 events (W):** no for the state. They change Dimension A for a
  tiny share of account-months (about 5 per 10,000 at CC, about 4 per 1,000 at RL) and the state AUC
  does not move (differences inside the interval, RL 3m at most +0.001). The moved RL rows pay above
  both neighbouring levels, but at n 17-26 and as a selected group.
- **Share of A3 promise events from transcripts:** small today and small if every call were
  extracted (W5), larger at RL than at CC. The transcript value is as a separate stated-intent
  signal (E5c.1), not as extra A3 events.

