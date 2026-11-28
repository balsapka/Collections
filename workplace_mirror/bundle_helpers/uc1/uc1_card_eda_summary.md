# UC1 card EDA: summary (E28)

Source: `uc1_card_eda_cc_60_180.{md,json}` and `uc1_card_eda_rl_60_180.{md,json}`, run 2026-11-28 (version
2026-11-28a). 60-180 only. Persona = `crx_persona.master`
output of `<model_id>.persona_e2e`, read through the saved `uc1_reach_frame`. Display names: Deterioration,
Locatability, Credibility, Ability. Unit: customers (CIF);
a customer's persona is that of its worst-DPD account in the base. Verdicts are my reading of the numbers, for
the card workshop to confirm.

## a. Tie-outs, snapshot, month ends

**Two mismatches (reported, not adjusted):** UC1 reading of any age, accounts at 2026-07-31: cards 3,525 found
against 3,528 expected, loans 679 against 680. Every
percentage (19.2% / 18.2%) and all other lines match (accounts 18,397 / 3,728; reading under 90 days 7.1% /
8.2%; Genesys transcript 90 days 10.5% / 13.3%). The
expected counts come from the earlier `uc1_latest` run (export-based reading); the frame counts the posterior
reading (`has_post`): a difference of definition (3 and 1 accounts) is the likely
cause, not checked.

- Card view: export snapshot **2026-08-31**, persona at month end 2026-08-31. Call view: persona at the month
  end of each call's month.
- Month ends with persona output: 2026-01-31 and 2026-03-31 to 2026-08-31 (February has none). UC1's last read
  call is **2026-07-16** (not moved).
- Card view customers in the base at 2026-08-31: cards 4,161 (of 5,496 persona customers in the export), loans
  728 (of 1,111).
- Call view: cards 4,207 calls / 1,409 customers, of which **only 502 calls are in the base** at the month end
  of the call; loans 1,658 calls, **524 in the base**.
  Most UC1-read customers were not in 61-180 at the time of the call. Everything that needs the persona at
call time (E4 call view, E5) rests on these ~500 calls.
- UC1 `confidence` (printed once, used nowhere): intent LOW 43% / 40%, capacity LOW 23% / 23%; reason, period,
  request, dispute carry no LOW; repayment slots carry none.

## b. Verdict per card field (cards / loans)

| Field | Verdict | The number behind it |
|---|---|---|
| Delinquency reason | show its month | stays the same in 58% / 63% of consecutive calls up to 30 days; highest overlap V 0.23 (with period); too few calls to say whether it matters on outcomes (lost job: cards 41 customers) |
| Payment capacity | keep (watch overlap with intent) | same-call V with intent 0.45 / **0.54** (loans, call view: "say the same thing", capacity adds least); 65% / 67% stable; stated-vs-Ability cells reach 100 customers on cards (below) |
| Payment intent | keep, show its month | moves most: 48% / 48% same up to 30 days (UC1 reference 64%); V with capacity 0.38-0.54; V with repayment amount 0.26-0.36 |
| Payment period | show its month | 54% / 61% same up to 30 days; V at most 0.23 |
| Repayment: amount named | keep | 72% / 72% same; V 0.28-0.40 with capacity, intent, plan: related, not the same thing |
| Repayment: date named | keep, too thin on loans | 79% / 80% same (loans just reach "stable"); V up to 0.34 |
| Repayment: plan structure named | too thin to say | 90% / 93% same but named for only 449 customers on cards, 66 on loans |
| Request | keep (cards only evidence) | cards: after a request, cure -9.0 pp [-17.6, -0.5] and waiver in 90 days +8.5 pp [+0.2, +16.9] (155 customers); loans: no difference; 67% / 65% same call to call |
| Dispute | keep (rare, stable) | 85% / 87% same (245 / 68 pairs); never a merge candidate by rule; named for 870 / 144 customers |

No pair of fields reaches V 0.5 on cards in either view. **Nothing is a drop or a merge on this evidence**:
the one overlap (capacity and intent) is at 0.54 on loans only and
at 0.38-0.45 on cards. The three repayment slots are not interchangeable (V 0.09-0.34).

## c. E1 overlap and E3 stability

**E1/E2: V per pair (largest; call view / card view), cards:** capacity x intent 0.45 / 0.38; capacity x
amount named 0.33 / 0.40; intent x amount 0.33 / 0.32; intent x date
0.17 / 0.32; amount x plan 0.31 / 0.31. Loans: capacity x intent **0.54** / 0.45; intent x dispute 0.00 / 0.46
(123 customers); amount x date 0.18 / 0.34. All other pairs below 0.30.
Unexpected level pairs (lift 2 or more, 100 or more): cards 9, loans 1.

| View | Pair | n | Lift |
|---|---|---|---|
| cards, card | capacity full with intent payback_full | 182 | 3.3 |
| cards, card | capacity none with intent no_payment | 169 | 3.2 |
| cards, call | capacity full with payback_full | 416 | 3.1 |
| cards, call | amount named with plan named | 226 | 2.8 |
| cards, call | intent partial with plan named | 167 | 2.4 |
| cards, card | intent no_payment with date absent | 210 | 2.2 |
| cards, call | reason has_employment with capacity full | 151 | 2.1 |
| loans, call | capacity full with payback_full | 144 | 3.5 |

Reading: the one expected link (can pay in full goes with will pay in full; cannot pay with did not offer) is
the overlap. Nothing else is unexpected.

**E3 share staying the same (consecutive calls, gap up to 30 days; cards / loans):** reason 58 / 63%, capacity
65 / 67%, intent 48 / 48%, period 54 / 61%, amount 72 / 72%, date 79 / 80%,
plan 90 / 93%, request 67 / 65%, dispute 85 / 87%. "Stable" (80% or more): plan, dispute, and date on loans.
By gap (reason, cards): 0-7 days 61%, 8-30 days 52%, 31-90 days 40%.
**Same agent against different agent:** not readable. Same-agent pairs are rare (21 pairs on cards for
reason): every "moves" field has "agent split too thin", so the question
whether a field moves less with the same agent is **unanswered**. Capacity: UC1 reference 1,703 pairs / 61.5%
same against 998 / 63.1% (cards) and 421 / 64.8% (loans);
intent 2,628 / 63.6% against 1,413 / 47.1% and 579 / 45.9% (lower than UC1: here a tie such as
`partial|payback_full` is its own level and counts as a change). Median gap 5-6 days (UC1: 4).
Calls carrying both capacity and intent: 1,900 cards / 773 loans (UC1 sample: 5,789).

## d. E4 said against data (card view; call view is thin)

**Ability** (stated capacity against Ability; customers; cells at 100 or more marked *):

| Cell | Cards, card view | Loans, card view | Cards, call view | Loans, call view |
|---|---|---|---|---|
| Matches (full-High, partial-Moderate, none-Low) | 436 * | 92 | 54 | 47 |
| Says more than data shows (full-Low) | 121 * | 29 | 16 | 23 |
| Says less than data shows (none-High / Moderate) | 108 * | 14 | <10 | <10 |
| Data can't see income (Ability Unknown) | 817 * | 113 * | 36 | 36 |
| Other mismatch | 442 * | 110 * | 71 | 62 |
| No single stated level (tie / not detected) | 2,237 * | 370 * | 176 * | 162 * |

Of 4,161 cards customers only 436 (10.5%) match; 2.9% say more than the data shows and 2.6% say less. Ability
is mostly Low or Unknown (stated full: High 10, Moderate 84, Low 121, Unknown 171).
By product (loans): "Matches" Personal Cash 18%, Personal 12%, Auto 5%. By reading age (cards): 3,511 of 4,161
customers have **no call date** in the call table (value comes from remarks or
calls outside the extract); of the dated ones 268 are 31-90 days old and 382 are 91-180; none is under 31 days
(calls end 07-16, snapshot 08-31).

**Promises** (stated intent against promise record): cards High or Moderate 2,819 *, Low with promises 681 *,
no promise on record 661 * (Unknown with promises: 0 everywhere). Loans: 387 *, 87, 254 *.
Of customers stating "will pay" on cards: 2,236 High or Moderate, 478 Low, 338 with no promise on record.
Stating "did not offer to pay": 104 / 72 / 87. Call view (promises strictly before the call):
cards High or Moderate 222 customers *, Low 35, none 33; loans 144 *, 31, 75: only the first cell reaches 100.

## e. E5 outcomes other than payment (call view, cards 502 / loans 524 calls in the base)

Comparisons made: cards 291, loans 693. Reaching the counting rule: cards 2, loans 0 (chance alone would give
about 14 and 34). The two on cards are the same value, request (cure -9.0 pp, waiver within 90 days +8.5 pp,
same sign in both halves). **Every other value is "too thin"** (fewer than 100 customers in a cell); no value
is "same everywhere", so **there is no merge candidate**. Outcomes not available: dispute closed / days to
close
(no case table), agency placement (agency code empty). Reschedule and settlement are one outcome (plan
proposed within 60 days). Lost job (cards, 41 customers, below the rule): rolled +15.6 pp [+1.5, +29.7],
stayed -15.0 pp, plan within 60 days -10.6 pp; cannot pay (28 customers): conversation within 30 days +9.9 pp
[-1.2, +21.0]. These are indications only. Segment used: DPD bucket x Deterioration state.

## f. E9 does a customer-level reading fit the account?

| Reading | Cards: 2+ products / other + unknown | Loans: 2+ products / other + unknown |
|---|---|---|
| any field, last read call | 7.0% of 4,161 / 19.1% (330 accounts) | 29.5% of 728 / **66.5%** (236 accounts) |
| capacity | 10.8% / 21.8% | 43.4% / 73.5% |
| intent | 6.6% / 20.3% | 29.8% / 68.7% |
| reason | 6.5% / 19.5% | 29.2% / 73.9% |

Reading: loans, other + unknown is far above 20% (the call's product is usually another family): **the card
should name the product of the call**. Cards: 19% on the last read call, 20-26% on several fields: borderline;
only 7% of cards customers are multi-product, so naming the product is low value there. "Unknown" is 0
everywhere, and a customer with a reading but no call in the extract cannot be counted as multi-product,
so the shares (denominator all readings) are probably understated.

## g. What could not be computed and what would unlock it

- **Agent effect on stability (E3):** same-agent pairs are too few. A longer call history per customer would
  unlock it.
- **Outcomes on the call view (E5):** only ~500 calls per model are in the 61-180 base at call time. More
  UC1-read calls on customers who are in 61-180 at call time (a longer run after the refresh) would unlock it.
- **Dispute closure and agency placement:** no DCORE case table for disputes, `szagencycode` empty and no list
  of agency collector groups. A placement table or the agency group list would unlock agency; a dispute case
  table the closure.
- **Reschedule against settlement:** `settlement_type` is in the plan table but was not split. Say if the
  split is wanted.
- **Reading age:** 84% of card-view customers have a value but no call date in the call table (remark-based or
  outside the extract); the age tables are therefore mostly "no call date". The reason was not checked.
- **E9 denominator:** customers with a remark-only reading have no call, so are never counted as
  multi-product.
- **180+:** not run (outside UC1's read set).
