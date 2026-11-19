# UC1 transcript signals in the collections persona: what we found and how we propose to use them

DRAFT, 2026-11-19. Sections marked [signals test] are filled once our second validation run is back.

## What we tested

We compared UC1's per-conversation signals with our observed-data persona (UC2: A1 ability, A2 locatability, A3
payment credibility, A4 deterioration) and with what customers paid afterwards. Scope: cards and retail loans at
61–180 DPD, month ends March to July 2026, current-format extractions only. We read every signal as what the customer
*said* on the call. Whether it is true is a separate question, so we only test two things: whether it lines up with
what the customer did next, and whether it is consistent with what our data shows.

## What we found

- **The inputs are sound.** Bundle counts, support counts and UC1's own aggregation match our recomputation from the
  per-conversation grid. Only a handful of intent customers differ.
- **Where UC1 adds most is where our data is blind.** Inside A1 Unknown (57% of cards at 61–180), paid rates follow
  the stated ability: able 21% / partly able 17% / not stated 16% / unable 12%, against 8% with no conversation.
  Inside A3 Low, customers who said they would pay partly or later paid 9.5% against 4.3% for those who did not say.
  Small cells for now, but this is the pattern a fill needs.
- **Where our data already sees the customer, UC1 mostly agrees with it.** Inside A1 High / Moderate / Low the stated
  level adds little ranking power (≤ +0.02 AUC on customers with a reading).
- **A real conversation is itself a strong signal.** Inside A3 Low, cards with an extracted conversation paid 7.0%
  against 3.2% with none (loans 22% vs 10%).
- **Freshness limits the shipped block today.** Calls in the store end on 2026-07-16, so at the August scoring date
  the newest reading is 1–6 months old.
- [signals test] Reasons, payment period, named amount / date, requests and disputes against payment.
- [signals test] Stated job and income claims against our observed income; whether consistent and inconsistent
  claims pay differently.
- [signals test] Promises made on the call that were never logged in DCORE.
- [signals test] Coverage a full run would reach: we estimate about a quarter of 61–180 accounts with an extracted
  conversation (now 5% of cards, 10% of loans); 180+ depends on whether those customers have calls at all.

## How we propose to use the signals

The persona key stays on observed data; UC1 adds what observed data cannot give. Four jobs:

| Job | What UC1 gives | Example |
|---|---|---|
| Fill | stated ability / intent where UC2 has no evidence | A1 Unknown split into stated able, stated unable, silent |
| Cross-check | statement vs observed data, as "verify" flags | says employed but salary stopped with us; promised on the call, nothing logged |
| Treat | reason, request, payment period, dispute | restructure / settlement / deferral demand; call on the salary cycle; route disputes |
| Context | the last stated stance and call date | for customers who talked and then went silent |

A fill or a flag goes into the persona only if it holds on the full run in both products; the treatment and context
jobs need no ranking bar. This fits the `collection_action` field in UC1's target schema: our persona sets priority,
UC1 helps set the action.

## What would help from UC1

1. The date of the full run over all transcripts, and the refresh cadence after it (ideally before each month end).
2. Whether 180+ customers' calls are in the transcript store.
3. How the current sample was drawn (which calls, which dates), so we can weight it correctly until the full run.
4. Detection confidence and conversation date carried through to the customer-level delivery.
