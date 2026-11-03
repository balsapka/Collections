# A1 AECB what-if — CC results (handoff 32, 2026-11-03)

Source: `tmp_validation/a1_aecb_whatif/summary.md` in the workplace (prompt
`sonnet_a1_aecb_whatif_prompt.md`), transcribed from 2 photos. Latest month 2026-08. RL not run yet.
S0 = today (pull counts in its month + 1), S6 = + 5 months, S12 = + 11 months; never backwards,
the next pull or a closure stops it.

## States

| Book | Scenario | High | Moderate | Low | Unknown | Unknown % |
|---|---|---:|---:|---:|---:|---:|
| cc_60_180 (19,292) | S0 | 46 | 2,798 | 5,688 | 10,760 | 55.8 |
| | S6 | 47 | 3,855 | 5,934 | 9,456 | 49.0 |
| | S12 | 49 | 4,216 | 5,980 | 9,047 | 46.9 |
| cc_180_plus (318,663) | S0 | 111 | 19,907 | 19,991 | 278,654 | 87.4 |
| | S6 | 115 | 23,868 | 19,307 | 275,373 | 86.4 |
| | S12 | 118 | 25,706 | 18,978 | 273,861 | 85.9 |

S0 check passes on both (0 states and 0 income levels differ). Every column sums to the book.

## Today's Unknown by the latest AECB salary alert (>= AED 1,000)

| Book | In W | Older (4–24 m; 7–24 at 180+) | 25+ m | Alert rows, never a salary | No alert row |
|---|---:|---:|---:|---:|---:|
| cc_60_180 | 101 | 4,017 | 607 | 5,090 | 945 |
| cc_180_plus | 306 | 18,065 | 25,869 | 145,558 | 88,856 |

- 61–180: 43% of Unknown is "AECB too old", 56% "no AECB salary ever". Pulls resolve at most
  1,304 (S6) to 1,713 (S12) Unknowns, 12–16%.
- 180+: 16% too old, 84% never. At most 3,281 to 4,793 (1.2–1.7%): a coverage problem, not a
  freshness one.
- Never-alerted group at 61–180: 7,569 accounts, 5,276 (70%) with an internal salary in 24 months;
  of its 5,090 Unknowns none has internal salary in W, 3,239 (64%) had one 4–24 months ago (a
  stopped salary). At 180+: 150,553, only 8,143 (5.4%) with an internal salary in 24 months.
- Feed coverage of base CIFs, any alert / a salary alert in 12 months: 88.3 / 43.1% (61–180),
  32.4 / 12.7% (180+).

## Claude's review

- Reconciles. The handoff flagged 1,290 vs 1,304 (S6) and 1,697 vs 1,713 (S12) at 61–180: the gap
  (14, 16) is the in-W group (101), whose pull in month 3 now also reaches the later months. Same at
  180+ (3,208 vs 3,281). The S12 count is above S6 + the m13–24 addition because the longer carry
  also reaches more m4–12 rows. No transcription error found.
- 426 of the 1,280 Unknowns with a salary alert 4–6 months ago stay Unknown in S6, though a 5-month
  carry reaches W. Likely cause: a later alert (closure, type 43 = 0, or an amount change below
  AED 1,000) stops the carry. Not diagnosed; only matters if GRR asks.
- The base differs slightly from the workbook's coverage-gap block (never-alerted 7,569 here vs
  7,693 all accounts there): that block counts all accounts, this group is defined over the 24-month
  lookback. Not material.
- Message for GRR: at 61–180 the thin feed costs up to 7–9 points of Unknown on cards; at 180+ 1–1.5.
  The bigger lever is the never-alerted salaried group (70% of it at 61–180), which only a real
  2-monthly pull can show.

## RL

Not run (user, 2026-11-03): the loan cells of the workbook's what-if blocks stay blank. The prompt
is retired; it is in git history (`sonnet_a1_aecb_whatif_prompt.md`) if RL is wanted later.
