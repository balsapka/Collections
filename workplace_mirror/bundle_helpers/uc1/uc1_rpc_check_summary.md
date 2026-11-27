# UC1 RPC check: is a right-party contact a real conversation? (cc_60_180, rl_60_180)

Source: `uc1_rpc_check_<model_id>.md` / `.json` (snippet 2026-11-27b), PROD run of 2026-11-27. Persona CIFs of
the 61-180 base; days March-August unless stated. Result-name classes are my reading of the vocabulary
(README), not a finding.

## a. Tie-outs

All match for both models (cc and rl: RPC since March, RPC 90 days, Genesys transcript 90 days, March-August
RPC / transcript / any UC1 evidence; cc: 1,934 accounts, 19.5% with no RPC). The 19.5% is the **CIF view** of
RPC (as `uc1_reach` Q0.store_without_rpc); the account view gives 20.7% (information row). Loans, not given in
the brief: 496 accounts with a transcript in 90 days, 31.0% with no RPC (CIF view), 31.5% (account view). All
R1-R4 tables ran; no errors.

## b. Verdict

**RPC is not a fair measure of "had a conversation": only 29% of card and 30% of loan RPC days hold a
conversation result.** By the best result of the day: not a conversation 39.7% (cards) / 52.1% (loans);
unclear 31.1% / 18.2%; conversation 29.2% / 29.7%. So 71% / 70% of RPC days are not a conversation or unclear.
The largest non-conversation results: payment postings (CUSTOMER MADE PAYMENT, ACCOUNT PAID, PARTIALLY PAID:
25% of card, 21% of loan RPC days, all "SUC" category) and E MAIL RECEIVED (14% of card, **31.5% of loan** RPC
days).

## c. Why so few RPC days have a transcript (Mar-Aug; cards 63,794 RPC days, loans 11,907; Genesys only, PCA
has no day before 10-01)

Same day / within +-1 / within +-3 days: cards 21.1% / 23.2% / 25.1%; loans 7.2% / 8.8% / 10.8% (the brief's
13% / 5% could not be reproduced; mine counts each CIF-day once over the days the store covers). Causes,
exclusive, ranked:

| # | cause | cards | loans |
|---|---|---|---|
| 1 | the day's results are all "not a conversation" (no call to record: e-mail, payment posting, label): no transcript | 36.1% | 50.3% |
| 2 | the CIF has no transcript at all in the period (not recorded, not linked, or a channel neither source records) | 22.7% | 21.0% |
| 3 | the CIF has transcripts, but on other days | 16.1% | 17.8% |
| 4 | transcript 2-3 days away (date drift) | 1.9% | 2.0% |
| - | matched within +-1 day (Genesys) | 23.2% | 8.8% |
| - | time zone (match only after the +4 h shift) | 0 | 0 |

- Evidence by class: of days with a conversation result 48.9% (cards) / 24.3% (loans) have a transcript within
  +-1 day; not-a-conversation days 9.2% / 3.0%; unclear 23.8% / 11.2%. E MAIL RECEIVED matches 1.9% / 2.1%,
  payment postings 6.8-7.8% / 3.0-3.3%, PROMISE TO PAY 73% (cards). Even real conversations are covered by
  about half of cards and a quarter of loans.
- **Month trend**: the +-1 match falls from 36% (March) to 8.5% (August) for cards, 15% to 5% for loans. The
  staged Genesys volume is flat (28-43k a month); the volume linked to persona CIFs falls (cards 7,730 in
  March, 2,101 July, 1,117 September; loans 1,418, 491, 297). Not explained by these tables.
- **Linking** (R3): 94,260 valid Genesys conversations (March-September, 19-40% of the valid ones each month)
  have no `contact_id` and never reach staging; in August 1,821 and in September 8,615 conversations have an
  agreement row with no customer id. Staging has no duplicates. I cannot split cause 2 into "not recorded" and
  "not linked" per CIF.
- **Time zone / date**: DCORE `action_ts` has no time of day (98.7% at 00:00), so only dates can match.
  Genesys hours peak at 05-08 (UTC, 09-12 Dubai); the +4 h date moves no matched day (identical counts). PCA
  hours 09-19 look local.
- **Source switch**: no effect in March-August. In August-October (to 10-14, cards 17,110 RPC days) 6.1% of
  days fall after Genesys' last day (09-29) with no PCA transcript; PCA matched 0.6% (cards) / <10 days
  (loans) of days.
- Reverse (cards, March-August, 31,237 transcripts): 50.9% have an RPC within +-1 day (60.9% within +-3);
  43.4% an outbound attempt without a right-party result; 0.3% an inbound call; 4.1% nothing in DCORE. Loans
  (6,079): 18.6% have an RPC; 23.4% an attempt; 16.2% only another DCORE record; **41.3% nothing in DCORE**.
  August-October: cards 53.3% (Genesys 54.1%, PCA 38.0%); loans 15.5%.

## d. Upper bound under (a)-(d)

Accounts "with a conversation", % of accounts (cards 18,397 / 19,292; loans 3,728 / 3,985). `_s` unclear
dropped, `_w` unclear kept.

| definition | cards 90 d to 07-31 | cards Mar-Aug | loans 90 d | loans Mar-Aug |
|---|---|---|---|---|
| (a) RPC as today | 36.1 | 50.8 | 42.7 | 57.2 |
| (b) conversation results, `_s` / `_w` | 16.0 / 23.1 | 29.9 / 38.5 | 18.3 / 25.3 | 31.6 / 40.1 |
| (c) (b) + inbound + SUC outside list, `_s` / `_w` | 24.5 / 30.0 | 38.4 / 44.7 | 23.3 / 29.3 | 37.9 / 44.5 |
| (d) (b) or any transcript, `_s` / `_w` | 20.6 / 26.2 | 41.0 / 45.9 | 25.9 / 30.6 | 45.8 / 50.9 |
| reference: transcript (Genesys; PCA 0) | 10.5 | 32.7 | 13.3 | 32.4 |
| reference: UC1 reading (90 d) / any UC1 evidence | 7.1 | 22.3 | 8.2 | 19.6 |

Of the accounts that had a conversation, the share with a transcript / with a UC1 reading (any-time evidence
for Mar-Aug):

| definition | cards 90 d | cards Mar-Aug | loans 90 d | loans Mar-Aug |
|---|---|---|---|---|
| (a) | 23.1 / 16.9 | 54.8 / 40.5 | 21.4 / 14.7 | 43.1 / 28.7 |
| (b) `_s` | 36.7 / 27.9 | 72.2 / 57.4 | 31.3 / 25.0 | 57.5 / 41.5 |
| (b) `_w` | 32.0 / 23.9 | 65.8 / 50.6 | 31.5 / 22.1 | 53.7 / 36.8 |
| (d) `_s` | 51.0 / 32.3 | 79.7 / 54.5 | 51.3 / 31.5 | 70.7 / 42.9 |

A2 observation (07-31, unchanged): of 4,046 reachable cards, 1,685 (41.6%) have a conversation-class contact
in W, 814 (20.1%) at best an unclear one, **1,547 (38.2%) rest only on not-a-conversation results or on
inbound / SUC calls outside the list** (1,336 + 211). Loans: 1,064 reachable; 40.0% conversation, 17.5%
unclear, 452 (42.5%) only non-conversation.

## e. R3 sources

| | Genesys (`stg_genesys_transcripts`) | PCA (`stg_pca_transcripts`) |
|---|---|---|
| dates found | 2026-03-06 .. 2026-09-29 (loaded to 11-08) | 2026-10-01 .. 2026-11-11 (loaded 11-11) |
| conversations (no duplicates) | 239,233, all with a CIF by construction | 51,109, 49,352 (96.6%) with a CIF |
| per month | Mar 32,493; Apr 43,358; May 31,238; Jun 39,782; Jul 27,752; Aug 33,402; Sep 31,208 | Oct 33,231; Nov 17,878 |
| persona base, cards / loans | 32,354 / 6,376 | 1,248 / 248 (Oct 765, Nov 483 for cards) |
| date field | `conversationstart` (string, UTC) | `conversationend` = PCA `call_date` (`conversationstart` empty) |
| CIF link | interaction `contact_id` -> agreement `szcustomerid` | `customer_id` used as CIF |
| direction field, raw values | 100% "outbound" | 100% "outbound" |

- **No overlap**: the sources do not share a month and no CIF-day is in both; the first PCA-only month is
  October. The correction note that Genesys and PCA overlap in August-September is **not seen**: raw PCA
  `conversations` has no row before 10-01. PCA staging keeps `financial_remediation` + `completed` = 51,109 of
  401,685 raw rows (12.7%).
- UC1: Genesys in UC1 metadata March-June 87-92%, July 51.8% (metadata ends 07-16); in the extraction ledger
  only 3.9-8.4% (non-legacy 3.1-7.6%, July 13.7%); **August-September 0 of 64,610; PCA 0 of 51,109**.
- Added up: 239,233 + 51,109 = 290,342 (288,585 with a CIF), more than the 150,000+ known; I cannot tie
  150,000 to a definition. For example August-November is 115,719 and June-November 183,253.
- PCA customer ids found in this model's DCORE agreements: cards 3.8% (Genesys 16.3%), loans 1.0% (3.3%); the
  agreements are model-scoped, so this does not show whether the id is a bank CIF.

## f. Deck lines (slide 5)

1. Right-party contact overstates real conversations: only 29-30% of RPC days hold a conversation result; 40%
   (cards) and 52% (loans) hold only payment postings, e-mails or labels.
2. With conversation results only, the March-August ceiling is 30% of card and 32% of loan accounts (38% / 40%
   if unclear results count), against 50.8% / 57.2% by RPC.
3. Adding any transcript, the ceiling is 41-46% of cards and 46-51% of loans; transcripts reach 32.7% / 32.4%
   and UC1 readings 22.3% / 19.6%.
4. Only 21% (cards) and 7% (loans) of RPC days have a transcript the same day; the match fell from about a
   third in March to under a tenth in August.
5. Genesys ends on 09-29 and PCA starts on 10-01; UC1 has read none of the 64,610 August-September Genesys or
   the 51,109 PCA transcripts.

## g. Not computed, or open

- Cause 2 (no transcript for the CIF) cannot be split into not recorded vs not linked; the 94k `contact_id`
  loss is by month, not by RPC CIF.
- The drop of persona-CIF transcripts after June is not explained (flat staged volume, falling persona share).
- Overlap of PCA with Genesys in August-September cannot be tested: no PCA row before 10-01. DCORE ends 10-14,
  so August-October is thin (PCA persona 1,248).
- **Classes**: the evidence suggests SETTLEMENT (14.8% of card RPC days) matches far less than real-call
  results (14.8% cards, PROMISE TO PAY 73%; loans 4.6%, like payments), so it may be a back-office step, while
  CLAIMS MADE PAYMENT (53%) and CUSTOMER_HUNG_UP (58%) match like real calls. Not changed here; moving
  SETTLEMENT would lower (b). Confirm unclear and KSA/ names with DCORE owners.
- The 13% / 5% same-day shares of the brief are not reproduced (21.1% / 7.2%). The "99% inbound" reading is
  not seen: both direction fields say "outbound".
