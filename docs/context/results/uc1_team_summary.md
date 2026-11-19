# UC1 transcript signals in the collections persona: what we found and how we propose to use them

DRAFT, 2026-11-19. Cards and retail loans at 61–180 DPD; 180+ follows.

## What we tested

We compared UC1's per-conversation signals with our observed-data persona (UC2: A1 ability, A2 locatability, A3
payment credibility, A4 deterioration) and with what customers paid in the 30–45 days after the call. Calls from
March to July 2026, current-format extractions only. We read every signal as what the customer *said*. Whether it
is true is a separate question, so we test only two things: does it line up with what the customer did next, and is
it consistent with what our data shows.

## What we found

- **The inputs are sound.** Counts, support and UC1's own aggregation match our recomputation from the
  per-conversation grid.
- **Transcripts capture promises our collections system does not.** 79% of card and 91% of loan promises made on a
  call have no promise logged on the account within ±3 days, and those customers pay more than customers with no
  promise at all (loans 48% vs 29%, cards 18% vs 14% paid within 30 days). Stated disputes are likewise almost never
  in the collections record. This is evidence our credibility axis does not see today.
- **Specific statements go with payment.** Customers who say they are employed, tie payment to their salary date,
  name an amount or date, or ask for a restructure, settlement or waiver pay more than those who say none of it
  (loans: 52–65% against 34%). Card settlement requests are the exception.
- **Where our data is blind, a reading helps.** Among customers our ability axis cannot score, those with a stated
  ability pay about twice as often as those without one, and on cards "able" pays more than "unable" (22% vs 13%).
- **The level detail adds little yet.** Able vs partly able, and the intent levels, look alike once we know the
  customer said something; job and income claims are only loosely consistent with our income data, often because
  we cannot see the income at all.
- **Coverage is the limit.** About 10–13% of card and 12–19% of loan accounts at 61–180 had a conversation in the 90
  days before a month end; 3% and 5–8% had an extracted one. Most calls at 61+ DPD are already extracted; the gap is
  calls made earlier in the delinquency. Our call-anchored sample was 333 card and 148 loan accounts, so most results
  are directional.

## How we propose to use the signals

The persona key stays on observed data; UC1 adds what observed data cannot give.

| Job | What UC1 gives | Status |
|---|---|---|
| Cross-check | promises and disputes stated on the call but not logged | strongest result; next we check promises logged on the customer's other accounts |
| Treat | reason, request, payment period, dispute | supported; feeds offer type, call timing, dispute routing and UC1's `collection_action` |
| Fill | stated ability where our ability axis has no evidence | promising, needs the full run to reach a usable sample |
| Context | the last stated stance and call date | collector view |

## What would help from UC1

1. The full-run date over all transcripts, including calls made at 1–60 DPD, and the refresh cadence after it
   (ideally before each month end).
2. Whether 180+ customers' calls are in the transcript store.
3. The sampling rule for the current extractions: extraction rises from 6–11% of calls at 0–30 DPD to 50–78% at
   61+ DPD, and we would like to weight it correctly until the full run.
4. Detection confidence and conversation date carried through to the customer-level delivery.
