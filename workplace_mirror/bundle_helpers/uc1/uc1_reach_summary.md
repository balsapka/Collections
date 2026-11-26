# UC1 reach: coverage ceiling, unreachable but talking, tier effect (PROD run 2026-11-26)

Source: `uc1_reach_results_pack.md` (aggregates from the workplace `tmp_validation/uc1_reach/`, all four model_ids;
the full tables are in the workplace `uc1_reach_<model_id>.{md,json}`). Prompt removed after this run (last version
`d5121f9`). All 07-31 tie-outs match the latest results (§25). Groups (CIF view, 90 days): C1 = UC1 reading with a
positive signal, C2 = reading without one, C3 = conversation (right-party contact or Genesys store call) without a
reading, C4 = no conversation. Bar (user): ≥ 5 pp inside the state, interval excludes 0, and better than C3.

## Read before using

- Axes were read at `persona_end_date` 2026-09-30 after a persona rerun; a master rerun failed partway, so cross-month
  consistency is not verified. Tie-outs at 07-31 all match.
- The G3 tier mapping parameters equal the old run, but the shares do not (cards in-house 16.5% vs 14.0%), most likely
  because the persona inputs changed. Sonnet ran Q3 anyway (the prompt said stop). Read the tier results as indicative.
- P4 (money at equal in-house share with an override) is 0 by construction: the moved accounts rank below every
  original in-house account, so none enter. Only "accounts that move" and "money per mover" are usable.
- C1 vs C3 compares a read, recorded call with any right-party contact. Part of C1's edge may be "a real recorded
  conversation" rather than what UC1 read. The cleaner comparator (store call that UC1 did not read) is not in this run.
- Outcomes are next month (t = 04-30 .. 07-31); 3-month money only for 04-30 and 05-31. Account-months are pooled;
  intervals come from account resamples. The age-limit tables are in the full files, not in the pack.

## Verdicts

1. **Coverage ceiling (07-31, account view).** Half of 60-180 accounts had a right-party contact since March: cards
   49.3%, loans 54.7%. In the 90 days before the month end: 36.1% / 42.7%. The Genesys store holds a conversation for
   only 10.5% / 13.3% of accounts in those 90 days; UC1 has a reading under 90 days for 7.1% / 8.2%. Any age: 19.2% /
   18.2%. Over March-August per account: right-party contact 50.8% / 57.2%, store 32.7% / 32.4%, any UC1 evidence
   22.3% / 19.6%.
2. **UC1 stays inside the store.** Under 90 days, UC1 reads 58-69% of the store-call accounts (cards) but only 15-19% of
   the right-party-contact accounts. Remark-only readings almost all sit on an unread store call: 97.1% have a store
   call the same day or the day before that is in UC1's metadata, and 2.6% of those calls are extracted. So "remark
   only" = a call UC1 has not read yet, not a note with no call behind it. The ceiling that matters is the store: about
   a third of right-party customers ever reach it, and only ~13% of card right-party days have a transcript there.
3. **The store goes thin in July:** only 77 card accounts with a store call in the 30 days to 07-31, vs 1,934 in 90
   days (per-month flow is in the full file). Without new store calls UC1 cannot read anything new.
4. **180+: no role for UC1 on today's data.** Right-party contact since March 3.4% cards / 4.4% loans, store ≈ 0%, UC1
   reading 0.1%. Outside the 180+ positive-signal group, accounts with a positive UC1 reading pay 1.7% (n 60).
5. **A2 vs right-party contact (cards 07-31).** 3,835 reachable with a contact in W; 2,919 not reachable despite a contact
   in W (all gone dark afterwards); 211 reachable on contacts outside the right-party list. Among the 12,151
   non-reachable, 2,929 (24%) had a right-party contact on the CIF in the last 90 days; 5.4% have a recent UC1 reading.
6. **Going dark (Q1): no UC1 signal.** Cards: C1 29.4% vs C3 27.8% (+1.5 pp [-0.2, +3.6]); within the age of the last
   contact C1 - C3 is +0.6 / +0.3 / -1.1 pp. What predicts going dark is how recent the last contact was (26% at 0-30
   days, 35-39% at 31-90) and having no conversation (C4 60%). Recent positive and recent negative readings both go
   dark less, so it is recency, not content. P2 has no comparator (C2 without a negative: 3 accounts). Loans: C1 +3.7
   pp vs C3.
7. **Unreachable but talking (Q2), non_reachable + unknown, next month:**
   - Cards: C1 12.9% pay, C3 11.2%, C4 4.1%. The conversation is the signal (+7.1 pp vs none). UC1 adds +1.7 pp [0.0,
     +3.3] (strong positive +3.4 [+1.4, +5.9]; conversation A2 does not see +1.1 [-1.2, +3.6]): **watch**. P3 (non_reachable,
     (b), vs C3): +0.6 pp [-2.0, +3.1].
   - Cards C2 (read, no positive statement) pays 4.2%, like no conversation (n 120): the absence of any positive
     statement looks informative, but it is rare (5% of readers).
   - Loans: C1 25.5%, C3 17.0%, C4 13.6%. UC1 adds +8.5 pp [+4.5, +12.0] (strong positive +11.6 [+6.2, +18.8]; transcript
     +10.5, remark +5.9): **holds** on the bar. P3: +7.8 pp [+2.4, +13.9], mde 6.9 pp.
   - Size: about 590 card and 130 loan account-months a month in C1 non_reachable; 38% (cards) / 61% (loans) of C1 is a
     conversation A2 does not see. Cards: mostly DCORE logged an attempt that day, not a contact (72.5%); loans:
     mostly nothing in DCORE that day (71.9%). Observation only: A2 is signed off.
   - 180+: cards C1 4.6% vs C3 4.7%; loans C1 12.3% vs C3 6.6% (n 81, watch).
8. **Tier (Q3, 60-180).** Shares at the calibrated cuts: cards 15.4 / 55.1 / 29.5% of accounts, 46.6 / 47.9 / 5.5% of
   3-month money; loans 17.1 / 56.1 / 26.8%, 24.1 / 62.1 / 13.8%.
   - A positive UC1 reading does **not** lift an agency account to in-house level: cards C1 in agency collect 376 AED next
     month and 13.0% pay, vs ~530-560 AED and ~36% for in-house accounts. On 3-month money, C1 agency (1,010 AED, n
     718) sits at the in-house cut (1,031): borderline, not above. Loans C1 agency 4,220 vs the in-house cut 4,790.
   - In the **non-workable pool** it does mark accounts that pay like the agency tier. Cards: C1 in the pool pay 8.6%
     and 253 AED, vs 3.0% / 82 AED for conversation-only (C3) and 1.6% / 45 AED with no conversation; the agency tier's
     C4 pays 5.4% / 150 AED. Loans: 14.3% vs 6.7% (C3), n 147. That is about 115 card and 35 loan accounts a month:
     **holds on the bar, small**.
   - What-if movers (90 days): UC1 positive moves 2,315 card account-months at 352 AED each; conversation moves 12,090 at
     253. Loans 592 at 1,689 vs 2,717 at 1,169.
   - Reverse: reachable in-house accounts with a recent negative reading pay 5.5 pp less (cards, [-9.7, -1.1], n 548;
     money no different); loans -7.8 pp [-16.0, +1.2]: **watch**.

## Deck lines

1. About half of 60-180 customers had a right-party conversation since March (cards 49%, loans 55%); at the July month
   end 36% / 43% had one in the last 90 days. That is the most a conversation-based signal could reach.
2. UC1 can read only calls in the Genesys store, which holds a conversation for 11% / 13% of accounts in the last 90
   days. UC1 has a reading under 90 days old for 7% / 8%: about two thirds of what the store holds and a fifth of the
   conversation ceiling. Readings of any age: 19% / 18%.
3. At 180+ hardly any customer is reached (3-4% since March) and UC1 reads almost none: no UC1 role at 180+ for now.
4. Among customers we cannot reach, having had a conversation is what goes with payment (cards 11% pay vs 4% without).
   What UC1 read adds on top: cards +2 points (not enough), loans +8.5 points.
5. UC1 signals do not predict who goes dark; the age of the last contact does.
6. A positive UC1 reading does not move an agency account to in-house level. It does find accounts in the non-workable
   pool that pay like the agency tier (cards 8.6% vs 2% for the pool; loans 14%): about 150 accounts a month.

## Hypotheses for the full UC1 data and the pilot

| # | Hypothesis | Metric, bar | Today [interval], n | n at store / RPC ceiling | Confirm or drop |
|---|---|---|---|---|---|
| H1 | Loans: a recent positive reading among unreachable accounts adds to a conversation | paid_due vs C3, ≥ 5 pp | +8.5 pp [+4.5, +12.0], 659 | P3 506 / 1,128 | holds vs "store call not read" and on 3-month money |
| H2 | Non-workable pool: a recent positive reading marks agency-level payers | paid_due and money vs C3 in the pool, ≥ 5 pp | cards +5.6 pp (454), loans +7.6 pp (147) | grows with the store | holds on 3-month money once payments pass 08-31 |
| H3 | Cards: a positive reading adds to a conversation among unreachable accounts | paid_due vs C3, ≥ 5 pp | +1.7 pp [0.0, +3.3], 2,408; strong +3.4 | P3 1,282 / 3,841 (mde 3.3 pp today) | drop if still < 5 pp at the store ceiling |
| H4 | Cards: a read call with no positive statement, or a negative one, marks non-payers | paid_due vs C1 / vs segment | C2 4.2% vs C1 12.9% (120); in-house negative -5.5 pp (548) | - | holds with n ≥ 500 in C2 |
| H5 | UC1 predicts going dark | going-dark rate vs C3 within contact age | +0.3 to +0.6 pp | - | dropped |
| H6 | UC1 at 180+ | any | ceiling 3-4%, store ≈ 0 | - | parked until 180+ calls reach the store |
| H7 | Coverage: the store limits UC1 | store calls / right-party days | ~1/3 of right-party customers, thin in July | - | data question for the UC1 / Genesys team |

## Follow-ups

- Ask the UC1 team (or Genesys owners) which calls reach the store, and why July is thin. This sets every UC1 ceiling.
- Harness fixes before the next run: P4 (compare movers' money with the in-house accounts they would displace);
  split C3 into "store call not read" and "right-party contact only"; print the per-month flow and the age-limit tables in the pack.
- 3-month money for June / July once payments are refreshed past 08-31.
