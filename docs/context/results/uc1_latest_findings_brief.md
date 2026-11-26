# UC1 findings and deck review context (GRR deck for 27 Nov; updated 2026-11-26 evening)

For the session that reviews the GRR deck "UC1 integration + pilot selection". This file is the single source for UC1
numbers and framing in the deck.
- Deck: https://claude.ai/artifact/DY5FLA436G3EqPKUXFmVLE. Sources: `docs/presentation/grr_uc1_pilot_deck/` (slides in
  `project/slides/*.html`, plus pdf and pptx; not committed).
- Detail behind every number:
  - `workplace_mirror/bundle_helpers/uc1/uc1_latest_results_summary.md` (latest results, logic doc §25);
  - `workplace_mirror/bundle_helpers/uc1/uc1_reach_summary.md` (coverage ceiling, unreachable customers, tier; logic doc
    §26);
  - `docs/context/results/uc1_stated_block.md`.

## Rules for the review

- **Collect changes, then the user decides.** List suggested changes per slide; apply only what the user approves.
- **Never take UC1 numbers from the workshop doc** (`uc1_workshop_summary.md`, Claude Doc). It still shows old figures:
  891 / 334 readings, and cards stated ability 27% vs 7%.
- **User rules:**
  - An AUC around 0.6 is not good enough to rank on: call such signals watch items, not candidates.
  - Every UC1 signal is read with its call date (a customer's situation changes).
  - The deck describes and never suggests collection actions; the in-house / agency tier is the one proposal.
  - GRR-facing text uses plain labels, not code field names.
- **Axis numbers:** A1 deterioration, A2 locatability, A3 credibility, A4 ability.
- **Outcome:** "pays" = pays at least the amount due in the next month. Figures are at the July month end (31 July
  2026) unless a line says otherwise.
- **Everything about UC1 is provisional.** UC1 took in no calls after 16 July 2026 and has read only part of the calls
  before that.

## Numbers at a glance (60-180, July month end, share of accounts)

| | cards | loans |
|---|---|---|
| Accounts | 18,397 | 3,728 |
| A2 reachable | 22.0% | 28.5% |
| Right-party contact since March (March-August, per account) | 50.8% | 57.2% |
| Right-party contact in the last 90 days | 36.1% | 42.7% |
| Genesys store call in the last 90 days (what UC1 can read) | 10.5% | 13.3% |
| UC1 reading under 90 days old | 7.1% | 8.2% |
| UC1 reading, any age | 19.2% (3,528) | 18.2% (680) |
| Reachable accounts with a UC1 reading (any age / under 90 days) | 31.5% / 14.8% | 24.9% / 12.2% |
| 180+: right-party contact since March / UC1 reading | 3.3% / 0.1% | 4.5% / 0.3% |

The 19% is not "near full coverage". Most readers are not reachable (cards 1,275 of 3,528 are). Against the
conversation ceiling (36%), UC1's recent readings (7%) cover about a fifth.

## Messages

1. **Coverage: reach grew about four times, mostly through agent remarks, but it is far from full.**
   - Readings: 19% / 18% of accounts (was 891 / 334 accounts); recent ones only 7% / 8%.
   - About half of customers had a right-party contact since March; 36% / 43% had one in the last 90 days. That is the
     most a conversation-based signal could reach.
2. **The Genesys store and UC1's intake are the limits.**
   - UC1 reads only store calls. The store holds a call for about a third of contacted customers (11% / 13% of
     accounts in 90 days).
   - UC1's intake stopped on 16 July, while the store kept recording to 29 August.
   - Remark-only readings almost all sit on a store call UC1 has not read yet.
3. **No UC1 signal ranks customers.** The best in-state AUCs are 0.55-0.66; A3 alone reaches 0.70-0.79. UC1 changes
   neither the persona nor the tier.
4. **What holds: the delinquency reason, as context.**
   - Customers who still have a job pay more than those who lost it: cards 17% vs 11% (+6.2 points, +11 over three
     months), loans 27% vs 20% (+7.6).
   - The gap is larger with a recent call (cards +8.8).
   - Size: lost or reduced employment = 1,202 card accounts (AED 1.76m due) and 273 loan accounts (AED 1.17m due).
5. **What no longer holds: stated ability on cards** (the earlier lead idea). Where ability is Unknown it no longer orders
   payers (AUC 0.51-0.53, 3,014 accounts). The earlier 27% vs 7% was a small sample.
6. **A call and payment: two findings that must not be mixed up.**
   - Among reachable card customers, those with a UC1 reading pay 7-9 points less: calls go to harder cases.
   - Among customers we cannot reach, any conversation goes with payment: cards 12% pay vs 4% without.
   - What UC1 read adds on top of a conversation:
     - loans: yes, 26% vs 16-19% after other conversations (holds);
     - cards: little, 13% vs 12% after a logged contact (not enough).
7. **180+: no UC1 role for now.** Only 3-4% of 180+ customers were reached since March, and UC1 reads almost none.
   Customers with a recorded call pay 5-14% vs about 1%, but calls UC1 never read pay as well: it is the contact, not
   UC1.
8. **Recency.**
   - Show the call date with every signal. At the August month end most UC1 values rest on calls 3-6 months old.
   - The data does not support a strict 90-day cut on cards: 91-180-day signals did not separate payers less, on small
     samples. Loans have too few accounts to tell.
   - Who goes dark depends on how recent the last contact was, not on what UC1 read.
9. **Tier.**
   - A positive UC1 reading does not move an agency account to in-house level (cards 13% pay vs about 36% in-house).
   - In the card non-workable pool, a recent positive reading finds about 115 accounts a month that pay like the agency
     tier: 8.6% vs 2-3% after other conversations.
   - Loans point the same way, but there are too few accounts to confirm.
   - Tier figures are indicative: the tier shares moved after a persona rerun.
10. **Where UC1's value sits:**
    - the reason, as a hint for the collector;
    - a context card (last stance and call date);
    - the loan finding among unreachable customers;
    - the card non-workable-pool finding;
    - a pilot that measures the card.
    - Watch items, not candidates: agent-remark intent on cards where no promise is on record (AUC 0.61); loan intent
      there over three months (AUC 0.66); cards "no positive statement" (4% pay, 120 accounts).
11. **Still no signal:** disputes, requests, UC1 confidence (almost never HIGH), "says able while A4 Low", "says unable
    while A4 High / Moderate", and going dark.

## Slide-by-slide check (current deck text → suggested change; the user decides)

- **Slide 2 (combining the states):** "UC1 sits beside it and adds no new personas". Fine.
- **Slide 3 (where the value sits):** no UC1 content.
- **Slide 4 (collector card):** "Empty until UC1 has read a call or remark: about 1 in 5 accounts today. Each shows its
  call date." Suggest: "about 1 in 5 accounts today, 1 in 14 from a call in the last 90 days". The notes say the same
  and need the same change.
- **Slide 5 (UC1 early results):**
  - Title "UC1 now reaches 1 in 5 accounts; one signal holds". Suggest: "UC1 has a reading for 1 in 5 accounts, a recent
    one for 1 in 14; one signal holds". Optionally add the ceiling: 36% / 43% had a conversation in the last 90 days.
  - "UC1 has read no call after 16 July": correct. Add "while calls kept being recorded to 29 August".
  - Reason figures (17 vs 11, 27 vs 20, +9 recent): correct.
  - "A call as a good sign: card customers with a reading pay 7-9 points less". Add "among reachable customers", so it
    doesn't clash with message 6 (among customers we cannot reach, a conversation goes with payment).
  - Possible addition (user decides): "Loans: among customers we cannot reach, a positive reading goes with 26% paying,
    vs 16-19% after other conversations."
  - "180+: the call matters, not the reading": correct. Could add "UC1 reads almost no 180+ calls (0.1%)".
- **Slide 6 (how UC1 joins):**
  - The proposal A wording and the B / C figures are consistent with today's data (B: four in five without a reading,
    over nine in ten without a recent one).
  - "What we need from the UC1 team: new calls read every month · each reading dated · 180+ calls, if they are
    recorded". Suggest:
    - "take in the calls recorded since 16 July, then read new calls every month";
    - "each reading dated";
    - "which calls reach the call store: only about a third of contacted customers have a recorded call".
    - The 180+ ask can go: few 180+ customers are reached at all (3-4%).
- **Slide 7 (pilot options):**
  - 180+ option: "positive signal (12%; about 1 in 5 pays)" and "under 3% of the other accounts pay". In the reach run
    the same group pays 8% next month and the rest 0.1%. "1 in 5" is likely a 3-month figure: check which measure the
    slide uses and label it.
  - Not UC1-related otherwise. UC1 adds nothing outside that group (positive readers outside it pay 1.7%, 60
    account-months).
- **Slide 8 (card test):** "1,400 card accounts per group with a UC1 reading: about 6 points would show". The 1,400 is
  19% of 7,500, so it counts readings of any age. With recent readings only (7%), it is about 530 per group and about 10
  points. Both depend on UC1 reading new calls: without that, by January every reading would be over five months old.
  Suggest: "if UC1 reads new calls; at today's recent coverage about 530 per group, about 10 points".
- **Slide 9 (tier):**
  - The deck's 17 / 54 / 29% of accounts and 48 / 46 / 6% of money come from the earlier tier run. The reach run's
    recalibrated cut gives 15 / 55 / 30% and 47 / 48 / 6%: close, no change needed.
  - Possible addition (user decides): "A recent positive UC1 reading finds about 115 card accounts a month in the
    non-workable pool that pay like the agency tier."
- **Slide 10 (next steps):**
  - Data need 4, "UC1 readings on new calls, at least monthly": add "UC1 has taken in no call since 16 July".
  - Timeline, "By 11 Dec: 30 Nov month end scored, with UC1's reason and last call": without a catch-up, the newest UC1
    call at 30 Nov is from 16 July (4.5 months old). Name it as a dependency.

The older GRR persona deck (slides 22 / 23, the persona count slide, the "UC1 join 20 Nov - 11 Dec" timeline) only
matters if it is reused. If so, apply the same points: only the reason carries a payment signal; UC1 adds no persona
dimensions; the join waits for UC1's catch-up.

## Recent readings only (April and May month ends, all evidence under 90 days old)

| Signal | April end | May end | April + May, three months |
|---|---|---|---|
| Stated ability where A4 is Unknown, cards (AUC) | 0.508 (125) | 0.554 (518) | 0.501 (643) |
| Stated ability where A4 is Unknown, loans (AUC) | 0.652 (45) | 0.545 (100) | 0.561 (145) |
| Reason, has minus lost job, cards (points) | +6.4 | +9.2 | +11.0 [5.4, 16.5] |
| Reason, loans (points) | +14.2 | +3.1 | +9.2 [-4.0, 20.4] |
| Intent where no promise is on record, cards (AUC) | 0.469 | 0.499 | 0.492 |
| Intent where no promise is on record, loans (AUC) | 0.544 | 0.578 | 0.661 [0.587, 0.753] |

Recency does not rescue the weak signals; the reason holds best on the cleanest month end (May).

## Caveats to keep in mind

- **Associations, not effects of UC1.** Calls go to selected customers.
- **Tier results are indicative:** the tier shares moved after a persona rerun, and the tier what-if test did not work
  as built.
- **Outcomes are mostly next month.** Three-month money exists only for the April and May month ends until payments are
  refreshed past 31 August.
- **Sample sizes:** loans and the non-workable-pool results rest on 147-659 account-months.
