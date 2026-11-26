# UC1 reach: coverage ceiling, unreachable but talking, tier effect (PROD runs 2026-11-26)

Sources: `uc1_reach_results_pack.md` (main run, all four model_ids) and `uc1_reach_details_summary.md` (details:
call dates, evidence age, C3 split; 60-180 only). Full tables are in the workplace
`tmp_validation/uc1_reach/uc1_reach[_details]_<model_id>.{md,json}`. Prompts removed after the runs (main: last `d5121f9`;
details: last version in git history). All 07-31 tie-outs match the latest results (§25).

Groups (CIF view, 90 days before the month end):
- C1: UC1 reading with a positive signal;
- C2: reading without one;
- C3: conversation without a reading, split into C3s (a Genesys store call UC1 did not read) and C3r (a right-party contact
  in DCORE only, no store call);
- C4: no conversation.

Bar (user): ≥ 5 pp inside the state, interval excludes 0, and better than the conversation groups.

## Read before using

- Axes were read at `persona_end_date` 2026-09-30 after a persona rerun; a master rerun failed partway, so cross-month
  consistency is not verified. Tie-outs at 07-31 all match.
- The G3 tier mapping parameters equal the old run, but the shares moved (cards in-house 16.5% vs 14.0%), most likely
  because the persona inputs changed. Q3 ran anyway (the prompt said stop). Read the tier results as indicative.
- P4 (money at equal in-house share with an override) is 0 by construction: moved accounts rank below every original
  in-house account, so none enter. Only "accounts that move" and "money per mover" are usable.
- Outcomes: next month for t = 04-30 .. 07-31, pooled account-months. 3-month money only for 04-30 and 05-31.
  Intervals come from account resamples. These are associations, not effects of UC1.

## Verdicts

1. **Coverage ceiling (07-31, account view).**
   - Right-party contact since March: cards 49.3%, loans 54.7%. In the last 90 days: 36.1% / 42.7%.
   - Genesys store call in those 90 days: 10.5% / 13.3%.
   - UC1 reading under 90 days: 7.1% / 8.2%. Any age: 19.2% / 18.2%.
   - Over March-August per account: right-party contact 50.8% / 57.2%, store 32.7% / 32.4%, any UC1 evidence 22.3% /
     19.6%.
2. **UC1 stays inside the store, and its intake stopped on 16 July.**
   - The store records calls up to 2026-08-29; UC1's metadata stops at 2026-07-16. So UC1 has not taken in six weeks
     of store calls, and readings at 08-31 are almost all old.
   - Under 90 days, UC1 covers 58-69% of the accounts with a store call (cards), but only 15-19% of the accounts with a
     right-party contact.
   - Remark-only readings almost all sit on an unread store call: 97.1% have a store call the same day or the day
     before that is in UC1's metadata, and 2.6% of those calls are extracted. "Remark only" means a call UC1 has not
     read yet.
   - Only about a third of customers with a right-party contact ever have a store call, and ~13% of card right-party
     days do. Which calls reach the store sets every UC1 ceiling.
3. **180+: no role for UC1 on today's data.** Right-party contact since March 3.4% cards / 4.4% loans; store ≈ 0%; UC1
   reading 0.1%. Outside the 180+ positive-signal group, accounts with a positive UC1 reading pay 1.7% (n 60).
4. **A2 vs right-party contact (cards 07-31).**
   - 3,835 accounts are reachable with a contact in W; 2,919 are non-reachable despite a contact in W (all gone dark
     afterwards); 211 are reachable on contacts outside the right-party list.
   - Among the 12,151 non-reachable, 2,929 (24%) had a right-party contact on the CIF in the last 90 days; 5.4% have a
     recent UC1 reading.
5. **Going dark (Q1): no UC1 signal.**
   - Cards: C1 29.4% vs C3 27.8%. Within the age of the last contact, C1 - C3 is +0.6 / +0.3 / -1.1 pp.
   - What predicts going dark is how recent the last contact was (26% at 0-30 days, 35-39% at 31-90) and having no
     conversation (C4 60%). Recent positive and recent negative readings both go dark less: it is recency, not content.
   - No evidence-age band separates from C3 in either product.
6. **Unreachable but talking (non_reachable + unknown, next month).**
   - **Cards:** C1 12.9% pay, C3r 11.9%, C3s 7.9%, C4 4.1%. UC1 readers pay about like customers with a logged contact
     (+1.0 pp vs C3r). Against unread store calls: +4.9 pp [+2.9, +7.1] on paid_due, money +109 AED [-21, +207]. Just
     under the bar: **watch**.
   - **Cards, other:**
     - strong positive pays 14.6%;
     - C2 (read, no positive statement) pays 4.2%, like no conversation (n 120). The absence of any positive statement
       looks informative, but it is rare (5% of readers).
   - **Loans:** C1 25.5% pay, C3s 19.2%, C3r 16.2%, C4 13.6%. Versus unread store calls: +6.3 pp [+2.6, +10.6], money
     +547 AED [+69, +966]; vs contact only +9.3 pp. Strong positive 28.6%: **holds** against both conversation groups.
   - **Size:** about 590 card and 130 loan account-months a month in C1 non_reachable. Of C1, 38% (cards) / 61% (loans)
     are conversations A2 does not see:
     - cards: DCORE mostly logged an attempt that day, not a contact (72.5%);
     - loans: mostly nothing in DCORE that day (71.9%).
     - Observation only: A2 is signed off.
   - **180+:** cards C1 4.6% vs C3 4.7%; loans C1 12.3% vs C3 6.6% (n 81, watch).
7. **Evidence age (C1 with the signal positive vs C3, unreachable, paid_due):**

   | signal | cards ≤ 90 d | cards 91-180 d | loans ≤ 90 d | loans 91-180 d |
   |---|---|---|---|---|
   | ability | +3.4 [+0.9, +6.4] (672) | +8.3 [+1.9, +13.7] (185) | +17.4 [+11.3, +23.4] (221) | +13.4 [-3.9, +32.4] (23) |
   | intent | +2.5 [+0.8, +4.2] (1,839) | +6.0 [-0.8, +15.6] (87) | +9.3 [+5.6, +13.2] (524) | -1.2 [-16.3, +16.4] (19) |
   | reason | +4.9 [+2.4, +7.6] (839) | +15.2 [+6.4, +22.7] (87) | +10.4 [+4.1, +15.8] (197) | +6.5 [-14.8, +27.1] (17) |

   - Over 180 days: every cell is under 10.
   - Cards: 91-180-day signals are not weaker (small n). The data does not support a strict 90-day cut on cards.
   - Loans: 91-180-day cells are too small to read.
   - Keep showing the call date with every signal; decide any limit on the full data.
8. **Tier (Q3, 60-180).**
   - Shares at the calibrated cuts: cards 15.4 / 55.1 / 29.5% of accounts and 46.6 / 47.9 / 5.5% of 3-month money;
     loans 17.1 / 56.1 / 26.8% and 24.1 / 62.1 / 13.8%.
   - A positive UC1 reading does **not** lift an agency account to in-house level:
     - cards C1 in agency collect 376 AED next month and 13.0% pay, vs ~530-560 AED and ~36% for in-house accounts;
     - on 3-month money, cards C1 agency (1,010 AED, n 718) is at the in-house cut (1,031), not above it;
     - loans C1 agency: 4,220 vs the in-house cut of 4,790.
   - **Non-workable pool, cards:** C1 pays 8.6% and 253 AED, vs C3s 2.2% / 52 AED and C3r 3.2% / 91 AED. C1 - C3s:
     +6.4 pp [+3.8, +9.8], money +200 AED [+49, +413]. The agency tier's C4 pays 5.4% / 150 AED. So these accounts pay
     like the agency tier: **holds**. About 115 card accounts a month.
   - **Non-workable pool, loans:** C1 14.3% vs C3s 10.0% and C3r 5.6%. C1 - C3s: +4.3 pp [-2.3, +11.6] (n 147):
     **watch**.
   - What-if movers (90 days): UC1 positive moves 2,315 card account-months at 352 AED each; conversation moves 12,090
     at 253. Loans: 592 at 1,689 vs 2,717 at 1,169.
   - Reverse: reachable in-house accounts with a recent negative reading pay 5.5 pp less on cards ([-9.7, -1.1], n 548;
     money no different) and 7.8 pp less on loans ([-16.0, +1.2]): **watch**.

## Deck lines

1. About half of 60-180 customers had a right-party conversation since March (cards 49%, loans 55%). At the July month
   end, 36% / 43% had one in the last 90 days: that is the most a conversation-based signal could reach.
2. UC1 can read only calls in the Genesys store, which holds a call for 11% / 13% of accounts in the last 90 days. UC1
   has a reading under 90 days old for 7% / 8%: about two thirds of what the store holds and a fifth of the
   conversation ceiling.
3. UC1 took in no calls after 16 July, while the store kept recording to 29 August. New readings depend on UC1 catching
   up.
4. At 180+ hardly any customer is reached (3-4% since March), and UC1 reads almost none: no UC1 role at 180+ for now.
5. Among customers we cannot reach, a conversation goes with payment (cards 12% pay vs 4% without). On loans, a positive
   UC1 reading adds on top (26% vs 16-19% for other conversations). On cards it adds little (13% vs 12%).
6. UC1 signals do not predict who goes dark; the age of the last contact does.
7. A positive UC1 reading does not move an agency account to in-house level. In the card non-workable pool, it finds
   about 115 accounts a month that pay like the agency tier (8.6% vs 2-3% for other conversations).

## Hypotheses for the full UC1 data and the pilot

| # | Hypothesis | Metric, bar | Today [interval], n | Confirm or drop |
|---|---|---|---|---|
| H1 | Loans: a recent positive reading among unreachable accounts adds to a conversation | paid_due vs C3s and C3r, ≥ 5 pp | +6.3 [+2.6, +10.6] vs C3s; +9.3 vs C3r; 659 | holds on the full data and on 3-month money |
| H2 | Card non-workable pool: a recent positive reading marks agency-level payers | paid_due and money vs C3s in the pool, ≥ 5 pp | +6.4 pp [+3.8, +9.8], +200 AED; 454 | holds on 3-month money once payments pass 08-31 |
| H2b | Loan non-workable pool: same | same | +4.3 pp [-2.3, +11.6]; 147 | n ≥ 400 |
| H3 | Cards: a positive reading adds to a conversation among unreachable accounts | paid_due vs C3s and C3r, ≥ 5 pp | +4.9 vs C3s, +1.0 vs C3r; 2,408 | drop if still under 5 pp on the full data |
| H4 | Cards: a read call with no positive statement, or a negative one, marks non-payers | paid_due vs C1 / vs segment | C2 4.2% vs C1 12.9% (120); in-house negative -5.5 pp (548) | holds with n ≥ 500 in C2 |
| H5 | UC1 predicts going dark | going-dark rate vs C3 within contact age | +0.3 to +0.6 pp | dropped |
| H6 | UC1 at 180+ | any | ceiling 3-4%, store ≈ 0 | parked until 180+ calls reach the store |
| H7 | Signals expire after 90 days (60-180) | C1 vs C3 by evidence age | cards 91-180 d not weaker (n 87-185) | decide on the full data |
| H8 | Coverage: the store and UC1's intake limit UC1 | store calls / right-party contacts; UC1 intake date | ~1/3 of contacted customers in the store; intake stopped 07-16 | questions for the UC1 team |

## Follow-ups

- **UC1 team:** take in the store calls after 16 July and keep reading monthly. Which calls reach the Genesys store, and
  why only about a third of contacted customers have one?
- **Harness, before the next run:**
  - fix P4 (compare movers' money with the in-house accounts they would displace);
  - keep the C3s / C3r split;
  - print the per-month flow in the pack.
- **Payments refreshed past 08-31:** 3-month money for June and July.
