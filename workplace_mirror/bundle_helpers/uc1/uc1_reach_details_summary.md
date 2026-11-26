# UC1 reach: three details (cc_60_180, rl_60_180)

Source: `uc1_reach_details_<model_id>.md` (PROD run of `uc1_reach_details.py` on the saved frame). Aggregates
only; cells under 10 are "<10".
Part A flow and chain tables are unchanged and stay in `uc1_reach_<model_id>.md`. Both models ran with no
errors.

## A. Last call date per month end (same for cc and rl)

| month end | last store call | last UC1 metadata call |
|---|---|---|
| 03-31 | 03-31 | 03-31 |
| 04-30 | 04-30 | 04-30 |
| 05-31 | 05-30 | 05-30 |
| 06-30 | 06-30 | 06-30 |
| 07-31 | 07-30 | 07-16 |
| 08-31 | 08-29 | 07-16 |

- UC1 metadata stops at 07-16, so UC1 reads nothing new after that. That is why 08-31 has under 10 new
  readings.
- The store runs to 08-29, so there are store calls UC1 never read.

## B. Evidence age: C1 with the signal positive, paid_due next month, difference vs C3 (non_reachable +
unknown)

| signal | age | cc | rl |
|---|---|---|---|
| ability | <=90 d | +3.4 pp [+0.9, +6.4] (n=672) | +17.4 [+11.3, +23.4] (n=221) |
| ability | 91-180 d | +8.3 [+1.9, +13.7] (n=185) | +13.4 [-3.9, +32.4] (n=23) |
| ability | >180 d | <10 | <10 |
| intent | <=90 d | +2.5 [+0.8, +4.2] (n=1,839) | +9.3 [+5.6, +13.2] (n=524) |
| intent | 91-180 d | +6.0 [-0.8, +15.6] (n=87) | -1.2 [-16.3, +16.4] (n=19) |
| intent | >180 d | <10 | <10 |
| reason | <=90 d | +4.9 [+2.4, +7.6] (n=839) | +10.4 [+4.1, +15.8] (n=197) |
| reason | 91-180 d | +15.2 [+6.4, +22.7] (n=87) | +6.5 [-14.8, +27.1] (n=17) |
| reason | >180 d | <10 | <10 |

- Cards: signals 91-180 d old are not weaker than <=90 d ones (ability and reason beat C3 by more, on small
  samples). This argues against a 90-day limit for cards.
- Loans: the 91-180 d cells have n of 17-23 and intervals too wide to read.
- Over 180 days: every cell is under 10.
- Going dark (Q1, reachable accounts): no age band separates from C3 in either model.

## C. C3 split (non_reachable + unknown, t = 04-30 .. 07-31)

| group | cc paid_due | cc money (AED) | rl paid_due | rl money (AED) |
|---|---|---|---|---|
| C1 | 12.9% (n=2,408) | 355 | 25.5% (n=659) | 1,688 |
| C1 strong positive | 14.6% (n=841) | 334 | 28.6% (n=245) | 1,517 |
| C3s (store call UC1 did not read) | 7.9% (n=1,851) | 246 | 19.2% (n=642) | 1,141 |
| C3r (right-party contact only) | 11.9% (n=8,865) | 267 | 16.2% (n=1,701) | 1,062 |
| C4 | 4.1% (n=36,310) | 109 | 13.6% (n=6,169) | 901 |
| C1 - C3s | +4.9 pp [+2.9, +7.1] | +109 [-21, +207] | +6.3 [+2.6, +10.6] | +547 [+69, +966] |

- C1 beats C3s on paid_due in both models. On money it does so only for loans; for cards the interval includes
  zero.
- Cards: C3s pays less than C3r (7.9% vs 11.9%), so the unread store calls are not the stronger contact group.
- Loans: C3s is slightly above C3r (19.2% vs 16.2%); neither pays much more than C4.

## C. Non-workable pool (tier early_exit)

| group | cc paid_due | cc money (AED) | rl paid_due | rl money (AED) |
|---|---|---|---|---|
| C1 | 8.6% (n=454) | 253 | 14.3% (n=147) | 1,621 |
| C3s | 2.2% (n=595) | 52 | 10.0% (n=170) | 704 |
| C3r | 3.2% (n=1,946) | 91 | 5.6% (n=497) | 463 |
| C1 - C3s | +6.4 pp [+3.8, +9.8] | +200 [+49, +413] | +4.3 [-2.3, +11.6] | +917 [-113, +2,265] |

- Cards: C1 beats C3s on both paid_due and money inside the pool, the cleanest sign that UC1 reading adds
  value for accounts the tier rule would write off. The C1 money interval is wide (124 to 452).
- Loans: point estimates favour C1, but the intervals include zero (small pool, C1 n=147).

## Caveats

- `tier` comes from the frame; the G3 tie-out mismatch noted in the earlier run still applies.
- The results are associations from observed payments, not causal effects of UC1.
