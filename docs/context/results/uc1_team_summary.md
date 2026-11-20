# UC1 transcript signals in the collections persona: what we found and how we propose to use them

DRAFT, 2026-11-20. Cards and retail loans at 61–180 DPD; 180+ follows.

## What we tested

We compared UC1's per-conversation signals with our observed-data persona (UC2: A1 ability, A2 locatability, A3
payment credibility, A4 deterioration) and with what customers paid in the 30–45 days after the call. Calls from
March to July 2026, current-format extractions only. We read every signal as what the customer *said*. Whether it
is true is a separate question, so we test only two things: does it line up with what the customer did next, and is
it consistent with what our data shows.

## What we found

- **The inputs are sound.** Counts, support and UC1's own aggregation match our recomputation from the
  per-conversation grid.
- **Transcripts capture promises our collections system does not.** 60% of card and 85% of loan promises made on a
  call have no promise logged on any of the customer's accounts within a week. On loans those customers pay more
  than customers with no promise at all (48% vs 30–34% within 30 days); on cards the gap is small. Stated disputes
  are likewise almost never in the collections record. As extra promise events in our credibility axis they are too
  few to change it today; we use them as a separate flag and will retest on the full run.
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
| Cross-check | promises and disputes stated on the call but not logged | strongest result: 60% of card and 85% of loan promises have no logged promise on any of the customer's accounts within a week; shown to collectors as a flag and raised with collections operations |
| Treat | reason, request, payment period, dispute | supported; feeds offer type, call timing, dispute routing and UC1's `collection_action` |
| Fill | stated ability where our ability axis has no evidence | promising, needs the full run to reach a usable sample |
| Context | the last stated stance and call date | collector view |

## What would help from UC1

1. The full-run date over all transcripts, including calls made at 1–60 DPD, and the refresh cadence after it
   (ideally before each month end).
2. Whether 180+ customers' calls are in the transcript store.
3. The sampling rule for the current extractions and transcripts: extraction rises from 6–11% of calls at 0–30 DPD to
   50–78% at 61+ DPD, and logged promises with a call in the store pay far less than those without (15% vs 41% on
   cards), so the stored calls look selected; we would like to weight them correctly until the full run.
4. Detection confidence and conversation date carried through to the customer-level delivery.
