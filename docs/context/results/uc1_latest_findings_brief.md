# UC1 latest findings: brief for the GRR deck (2026-11-26)

For the session updating the GRR persona deck. Results on UC1's August refresh. Sources:
`workplace_mirror/bundle_helpers/uc1/uc1_latest_results_summary.md` (full tables) and
`docs/context/results/uc1_stated_block.md` §24–25. The workshop doc (`uc1_workshop_summary.md`, Claude Doc) still
shows the older figures (891 / 334 readings, cards stated ability 27% vs 7%): do not copy numbers from it.

Axis numbers: A1 deterioration, A2 locatability, A3 credibility, A4 ability. Outcome = share of accounts paying at
least the amount due in the next month (`paid_due`). All UC1 results are provisional: UC1 has read no call after
16 July 2026 and only about 1 in 7 card calls from April to June.

## Messages for the slides

1. **UC1 reach grew about four times, mostly through agent remarks.** Accounts with a UC1 reading at the July month
   end: cards 3,528 (19.2% of 18,397), loans 680 (18.2% of 3,728); before: 891 / 334. With a call in the last 90 days
   only 7.1% / 8.2%, because UC1's calls stop on 16 July.
2. **No UC1 signal is strong enough to rank customers.** The best in-state AUCs are about 0.55–0.66; A3 alone reaches
   0.70–0.79. User's view: an AUC around 0.6 is not good enough. UC1 does not change the persona or tier.
3. **What holds: the delinquency reason, as a treatment hint.** Customers who still have a job pay more than those who
   lost it: cards +6.2 pp (every month end; +11 pp over three months), loans +7.6 pp. Size at the July month end:
   lost or reduced employment = 1,202 card accounts (AED 1.76m due) and 273 loan accounts (AED 1.17m due).
4. **What no longer holds: stated ability on cards** (the earlier lead idea). Inside A4 Unknown the stated level does
   not order payers (AUC 0.51–0.53, n 3,014). The earlier "27% vs 7%" was a small-sample result. Use as context only.
5. **Having a call is not a good sign by itself.** Card customers with a UC1 reading pay 7–9 pp less than other
   reachable customers, at every month end (calls go to harder cases). Loans: no difference.
6. **180+: customers with a recorded call pay 5–14% vs about 1%.** But calls UC1 never read pay as well, so the
   signal is the conversation, not UC1's reading. Not yet compared within A2 reachable.
7. **Recency matters.** Signals from recent calls separate payers better (cards reason +8.8 pp with evidence in the
   last 90 days vs +6.2 pp at any age). At the August month end most UC1 values rest on calls 3–6 months old. Any
   stated signal shown to a collector comes with its call date.
8. **UC1's value is in what the collector does with it:** the reason as a treatment hint, a context card (last stance
   and call date), and a pilot that measures the card's effect. Watch items to recheck on the full data, not
   candidates: agent-remark intent on cards in A3 no promise (AUC 0.61, n 367); loan intent in A3 no promise over
   three months (AUC 0.66, n 258).
9. **Still no signal:** disputes, requests, UC1 confidence (almost never HIGH), "says able while A4 Low", "says unable
   while A4 High / Moderate".

## Recent readings only (April and May month ends, all evidence under 90 days old)

| Signal | April end | May end | April + May, three months |
|---|---|---|---|
| Stated ability in A4 Unknown, cards (AUC) | 0.508 (125) | 0.554 (518) | 0.501 (643) |
| Stated ability in A4 Unknown, loans (AUC) | 0.652 (45) | 0.545 (100) | 0.561 (145) |
| Reason, has minus lost job, cards (pp) | +6.4 | +9.2 | +11.0 [5.4, 16.5] |
| Reason, loans (pp) | +14.2 | +3.1 | +9.2 [−4.0, 20.4] |
| Intent in A3 no promise, cards (AUC) | 0.469 | 0.499 | 0.492 |
| Intent in A3 no promise, loans (AUC) | 0.544 | 0.578 | 0.661 [0.587, 0.753] |

Recency does not rescue the weak signals; the reason holds best on the cleanest month end (May).

## Deck text that may need a change (check each; the user decides)

- **Slide 22** ("In-house is where we talk to customers, so that is where UC1 adds its signals"): the list of signals
  ("intent to pay, a change in income or job, a hardship reason, a dispute, a promise made on the call") reads as
  if all are useful; on today's data only the reason carries a payment signal, disputes do not, and intent is weak.
- **Slide 23** last paragraph ("UC1 refines it with what customers tell us"): fine as a direction; UC1 refines
  treatment and context, not the ranking.
- **Persona count slide** ("each UC1 signal multiplies the count again"): the agreed shape is a stated layer beside
  the A1–A4 key; UC1 does not add persona dimensions.
- **Timeline** ("UC1 transcript signals join 20 Nov – 11 Dec"): the join waits for UC1 to read the remaining calls;
  only the reason and the context card are ready to show.
- Framework tiles with the dashed UC1 box: unchanged.

## Still running (may land before the deck)

`summary_uc1_reach.md`: which UC1 signals come before Reachable → Non-Reachable, and Non-Reachable accounts with a
recent conversation (about 700 card and 180 loan accounts at the July month end), by signal age.
