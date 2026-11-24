# UC1 integration: workshop summary and proposals

24 November 2026

UC2 tells us who to call first; UC1 tells us what to say and what we are missing. UC1 (what customers say on calls, extracted from transcripts and agent notes) should sit beside the UC2 persona (A1 ability, A2 locatability, A3 credibility, A4 deterioration), not inside it: A1–A4 keep setting the persona and tier, and what customers say on calls adds a few narrow signals, treatment hints and an operations finding. All readings are provisional until UC1 finishes generating signals for every available transcript and remark.

## Where we are

The current UC1 delivery is a sample: 5,038 customers, with signals from calls dated March to 16 July 2026. It covers 2.6% of 61–180 DPD card account-months and 5.9% of loan account-months (April–July). UC1 is now generating signals for every available transcript and remark; the same analysis reruns on that data.

|  | Cards 61–180 | Loans 61–180 |
| --- | --- | --- |
| Book reachable (A2), share of account-months | 25% | 29% |
| Covered by UC1, average April–July | 2.6% | 5.9% |
| Covered by UC1 at the July month end | 4.8% | 9.0% |
| Had a call UC1 has not read yet (July) | 21.8% | 17.4% |
| Stored calls read by UC1 | 16% | 35% |
| Projected coverage if all stored calls are read | about 13% | about 16% |

- **The realistic ceiling is the reachable pool** (about a fifth to a quarter of the book): a transcript needs a conversation. Most customers will never have a UC1 reading, so every customer must get a persona and tier without one.
- **180+ DPD is barely covered.** UC1 reaches 107 card and 68 loan accounts at 180+ (0.1% or less), through the same customer's other products.
- **Results are read at month ends**, with payment measured in the following month.

## What the data says

Two findings hold in both readings, promises said on calls but never logged and the stated reason, and stated ability now orders the card customers our data cannot read. Payment = paid at least one due in the following month, among customers with a UC1 reading. "April–July" uses each customer's latest call reading over four month ends; "July" uses UC1's own final estimate at the July month end. One month with small groups: read the July figures as direction. AUC measures how well a signal ranks payers above non-payers (0.5 = no better than chance, 1.0 = perfect).

| Finding | Cards: April–July / July | Loans: April–July / July | Reading |
| --- | --- | --- | --- |
| Promise said on the call, not logged in DCORE, vs no promise | +3.5 pp / inside A3 "no promise" 8.7% vs 4.1% | +13 pp / inside "no promise" 25% vs 14%; inside "promised" 61% vs 29% | holds; strongest on loans |
| Promise said, not logged, vs promise logged | +8.9 pp / 18.0% vs 16.9% | too few logged / 36.5% vs 39.0% | unlogged promises pay as well as logged ones |
| Stated ability inside A1 Unknown: able / partly / not stated / unable | 24 / 18 / 24 / 12%, AUC 0.53 / 27 / 16 / 14 / 7%, AUC 0.61 | 32 / 27% / no order (AUC 0.47) | cards: now orders payers |
| Reason: has employment vs lost employment | 21% vs 10% / 17% vs 14% | 37% vs 19% / 44% vs 23% | holds; strongest on loans |
| Stated intent inside A3 "no promise": pays in full vs partly | no difference / no difference | 34% vs 18%, AUC 0.61 / 22% vs 24%, AUC 0.52 | not confirmed: recheck on the full data |
| Says able or pays in full while A1 is Low | about 25 pp lower / no difference (20% vs 19%) | too few / no difference (33% vs 33%) | did not hold |
| Transcript promises added to A3 as promise events | 0.2 state changes per 1,000 rows | 2.5 per 1,000 rows | no effect on A3 |
| Stated dispute or request | no payment difference | no payment difference | not a risk signal |

Four findings change how we use UC1:

- **Many promises made on calls have no DCORE promise record (being verified).** 60% of card and 81% of loan transcript promises have no DCORE promise on the customer within ±7 days; at July, 41% (cards) and 70% (loans) of promises with an amount or date have no promise record near the call. Logged amounts match what was said in 29% of cases and dates in 12%. We are verifying this against the raw call and DCORE records (time stamps, all agreements of the customer, all DCORE codes, who handled the call) before concluding whether it is a logging practice or a data-linking issue.
- **Having a call is not a good sign by itself.** Inside reachable card customers, those with a transcript pay 7 pp less: calls go to harder cases. Customers with a UC1 reading pay more than the whole book (cards 16% vs 9%) only because they are reachable, which A2 already captures.
- **Agent remarks come from DCORE notes.** 92% of card remark days have a DCORE follow-up the same day. They add what agents wrote but DCORE never records as structured data, such as promises noted but not logged.
- **At 180+, the few customers UC1 reaches stand out.** Card accounts with any UC1 conversation pay 4.7–7.2% vs 1.1% for the rest; loans 8.8–12.3% vs 1.3% (107 to 329 accounts). Small, but it is the kind of positive signal 180+ needs.

## Money behind the signals

UC1's signals sit on real balances, and the biggest blind spot it can help with is A1 Unknown: more than half of card outstanding. July month end, AED; "paid of due" = August payments as a share of the amount due.

| Group | Cards: accounts | Cards: outstanding | Cards: paid of due | Loans: accounts | Loans: outstanding | Loans: paid of due |
| --- | --- | --- | --- | --- | --- | --- |
| Whole book | 18,397 | 519M | 19% | 3,728 | 418M | 35% |
| With a UC1 reading | 891 | 30M | 31% | 334 | 37M | 44% |
| Promise said, not logged (being verified) | 239 | 8.1M | 28% | 137 | 14.4M | 57% |
| A1 Unknown (our data cannot read ability) | 10,001 | 283M | 13% | 1,493 | 148M | 30% |
| A1 Unknown, says able | 33 | 1.1M | 66% | 13 | 1.2M | 14% |
| A1 Unknown, says unable | 72 | 2.2M | 5% | 22 | 2.2M | 79% |

- **A1 Unknown holds 54% of card outstanding and about a third of loan outstanding;** UC1 reaches 4–6% of its amount due today. On cards, those who say they can pay paid 66% of their due in August; those who say they cannot, 5%. Loan groups are too small to read.
- **Why A1 Unknown customers are behind (cards):** lost employment is the most common reason (38%, against 27% in A1 Low and 16% in A1 Moderate); lost or reduced employment together make 46%, and they pay least (reduced 4%, lost 11%, no reason stated 17%). On loans, lost employment is 31–34%.
- **The call transcripts carry the signal.** Readings from transcripts order payers better than readings from agent remarks in 5 of 6 comparisons; remark readings are mostly empty. Each difference alone is within noise.

Card outstanding is the latest July balance, close to but not exactly the month end.

## How UC1 fits the persona

UC2 measures what customers do; UC1 records what they say. The persona key and the tier stay on A1 (ability), A2 (locatability), A3 (credibility) and A4 (deterioration); UC1 never changes an A1–A4 state. It adds a "stated layer" beside them with four jobs:

| Job | What UC1 adds | Where it lands | Candidates on today's data |
| --- | --- | --- | --- |
| Fill | a stated reading where UC2 has no evidence | priority order inside a tier | cards: stated ability inside A1 Unknown |
| Cross-check | what was said but never recorded | collector priority; operations finding | promise said on the call, not logged (strongest on loans) |
| Treat | the reason behind the delinquency | treatment hint next to the tier | lost vs has employment (strongest on loans) |
| Context | last stated stance and call date | collector view only | every customer with a UC1 record |

Rules that keep it safe:

- **UC1's final estimate is the state.** For each signal, the state value is UC1's own estimate, built from call transcripts and agent remarks; we do not re-judge it.
- **One month end for now.** UC1's estimate carries no date, so results use the July month end; a monthly dated estimate (see the asks below) would allow several.
- **Within a tier, not across.** UC1 can reorder customers inside a tier and attach hints and flags; moving a customer across tiers needs an explicit decision on the full data.
- **Confidence and bank check read with care.** UC1's confidence is LOW for every ability and intent estimate today, and its bank check uses our own income data, so neither is read as proof of a statement.

What the stated layer holds for each customer and month, all taken from UC1's estimates:

| Field | Values | Use |
| --- | --- | --- |
| Stated ability | able / partly able / unable / not stated / no reading | cards: order inside A1 Unknown |
| Stated intent | pays in full / partly or later / refuses / not stated / no reading | context; loans: recheck inside A3 "no promise" |
| Delinquency reason | lost / reduced / has employment, increased obligations | treatment hint |
| Promise said, not logged | yes / no | priority inside the tier; operations finding |
| Payment period, dispute, request | UC1's levels | context for the collector |
| UC1 record | no conversation / calls not yet read by UC1 / reading | tells a silent customer from one never heard |
| Last call date, UC1 confidence | as delivered | context |

## Proposals

Lead with what UC1 sees that nothing else does, keep three narrow signals, and judge UC1 by what it changes for the collector, not by how well it ranks payers on its own (A1–A4 already rank them). Each candidate is confirmed or dropped on the full data.

1. **Keep the persona key A1–A4 unchanged.** UC1 sits beside it as the stated layer; a customer with no call keeps exactly the persona and tier they have today.
2. **"Promise said, not logged" as a priority signal.** Strongest on loans: inside A3 "promised", customers whose promise was never logged paid 61% vs 29%; inside "no promise", 25% vs 14%. The collector follows up the promise the customer already made.
3. **Cards: stated ability orders customers inside A1 Unknown,** where our data has no reading: able 27%, partly 16%, not stated 14%, unable 7% (July). Use it to order calls inside the tier.
4. **The delinquency reason as a treatment hint.** Lost employment pays about half as often as has employment on loans (23% vs 44%): route to hardship or restructure options rather than a standard promise script.
5. **Context for the collector:** the last stated stance and call date, shown, not scored.
6. **Recheck on the full data:** stated intent inside A3 "no promise" on loans (strong over April–July, not seen in July alone).
7. **Drop:** the "says able while A1 is Low" flag (did not hold), transcript promises as A3 events, disputes and requests as risk signals, UC1's confidence as a filter (LOW throughout today).
8. **Operations / DCORE: the promise gap, once verified.** If the raw-data check confirms that most promises made on calls are not recorded, fixing the recording improves A3 for every customer, not only those with a call, and a one-page note goes to collections operations.

## Proving the value: a pilot

UC1's value is in what the collector does with it, and only a test can show that. Proposal for GRR:

- **Who:** reachable customers at 61–180 DPD with a UC1 reading, split at random in two halves; both halves keep the same persona and tier.
- **What changes:** collectors see the UC1 card (reason, promise said but not logged, stated ability, last stance and call date) for one half only.
- **Measured:** promises kept, cures, and payment within 30 and 60 days, compared between the halves.
- **Cost:** low; the UC1 fields are already produced per customer and month.

## Coverage roadmap

UC1's reach grows with extraction, up to the reachable pool:

| Share of 61–180 account-months | Cards | Loans |
| --- | --- | --- |
| Today (July month end) | 4.8% | 9.0% |
| All stored calls read | about 13% | about 16% |
| Ceiling: reachable customers | about 25% | about 29% |

## What we ask the UC1 team

1. **A monthly dated estimate,** back to March, so results can be measured over several month ends instead of one.
2. **All stored calls read, and calls after 16 July added,** which takes coverage to about two thirds (cards) and four fifths (loans) of the reachable pool.
3. **180+ calls:** are recoveries and vendor calls recorded? If yes, UC1 could be the only signal source at 180+, where our ability axis is about 85% Unknown.

## Example: what the collector sees

An illustrative customer, not a real one:

|  |  |
| --- | --- |
| Persona (UC2) | ability Unknown · reachable · credibility Moderate (promised) · slow roller |
| Stated ability (UC1) | partly able |
| Reason (UC1) | lost employment |
| Promise said, not logged | yes: amount named on the last call, no promise recorded |
| Last call | 10 July |
| Suggested action | follow up the promise made on the call; offer hardship options |

## Decisions for the workshop and next steps

The workshop is asked to agree the shape of the integration now, so the full-data run only has to confirm or drop each signal.

- [ ] UC1 sits beside the persona as a stated layer; the A1–A4 key and tiers stay as they are.
- [ ] UC1 may reorder customers inside a tier and add hints and flags, but not move them across tiers.
- [ ] A signal may be adopted for one product only (the strongest results are product-specific).
- [ ] UC1's final estimate per signal is the state value; it uses both call transcripts and agent remarks.
- [ ] GRR runs the pilot: the UC1 card for a random half of reachable 61–180 customers with a reading.
- [ ] Once the raw-data check confirms the promise gap, a note goes to collections operations / DCORE, with an owner on their side.
- [ ] The three asks go to the UC1 team (dated estimate, all calls read, 180+ calls).
- [ ] Bar on the full data, per product: at least 5 pp paid difference or +0.02 AUC inside the target state, with at least 100 account-months per cell.

Next steps:

1. UC1 finishes generating signals for all available transcripts and remarks.
2. We rerun the same measurements on it. If calls now go past 16 July, we first extend our data to a later month end so the newer calls have a payment outcome.
3. Each candidate in the proposals is confirmed or dropped against the bar; the result comes back to this group.
4. The confirmed signals are added to the persona output as the stated layer, and the pilot starts on them.
