# UC1 reach: results pack (numbers only, compact)

Source: the four `uc1_reach_<model_id>.{md,json}` of the 2026-11-26 PROD run (definitions: `README.md`). Month
ends 03-31..08-31; next-month outcomes for t <= 07-31, 3-month for t <= 05-31. Per-month tables are cut to
2026-07-31, signal tables to the key rows, and some tables are left out here (age-limit tables, Q1 context /
last conversation, A3/A4 splits, 180+ side tables); all are in the per-model files. Cells under 10 print
`<10`. Intervals: 200 account resamples.

Notes on how the numbers were made:
1. Axes read at `persona_end_date` 2026-09-30; the persona pipeline was rerun after the old tier results and a
master rerun failed partway, so A1-A4 / spine consistency across months is unverified. All 07-31 tie-outs
match.
2. G3 tier (60-180): the 2026-05 mapping parameters equal the old run (cap 20,080, cuts 1,248.9 / 174.8, 4
months, 58,366 rows) but the tier shares do not (cards in-house 16.5% vs 14.0% old). Q3 ran anyway; cuts
calibrated to 17% in-house / 29% non-workable of accounts.
3. Q3.whatif "money captured at equal in-house share" (left out) is identical with and without every override,
with 0 accounts entering in-house places: moved accounts rank below all original in-house accounts at a fixed
number of places. P4 = 0.0 pp by construction; "accounts that change tier" and "money per mover" are the
usable columns.
4. P2 comparator (C2 without a negative, < 90 d) has under 10 accounts for cards 60-180: no interval.
5. Store starts 2026-03-06; UC1 metadata ends 2026-07-16 (transcript readings stop; remark evidence
continues).
6. Groups (CIF view, 90 d): C1 reading with a positive signal, C2 reading without, C3 conversation (RPC or
store call) without a reading, C4 no conversation. Reading = posterior row on the month end; "under 90 d" =
latest evidence of any signal within 90 days.
7. Ceilings: store = CIF had a store conversation in 90 d; RPC = CIF had an RPC in 90 d; "n at ceiling" =
today's n scaled by those counts per account with a reading under 90 d. `left_top_band` is inferred. 180+ Q3 =
positive-signal group.

# cc_60_180
Tie-outs 07-31: all match (accounts=18397, reachable=4046, reading_post=3525, reading_post_90=1299,
reach_reading_90=600)
P1 CIF/account view 07-31: rpc_since_march 49.7/49.3%; rpc_90d 36.5/36.1%; store_conv_90d 10.5/10.5%;
any_uc1_reading 19.0/19.2%; uc1_reading_under_90d 7.0/7.1%
P2: n 1293/3; rates 0.2931 vs 0; diff +28.6 pp [-,-]; watch (too few to interval); mde 73.6 pp; n at store/RPC
ceiling 1724/8215
P3: n 787/10403; rates 0.1194 vs 0.1133; diff +0.6 pp [-2.0,+3.1]; watch; mde 3.3 pp; n at store/RPC
ceiling 1282/3841
P4: n 2408/13244; rates 42.52 vs 42.52; diff +0.0 pp [+0.0,+0.0]; no signal; mde - pp; n at store/RPC ceiling
4077/11069
**Q0.chain_cif** CIF view
| month end | base | 1 RPC since store start | 2 RPC 90d | 3 store conv 90d | 4 UC1 metadata 90d | 5
transcript reading | 6 remark reading | 7 any reading |
| 2026-07-31 | 17,854 | 49.7%(17,854) | 36.5%(17,854) | 10.5%(17,854) | 9.7%(17,854) | 2.2%(17,854) |
6.5%(17,854) | 7.0%(17,854) |
**Q0.ever** fixed window
| unit | base | RPC | store conv | UC1 metadata | any UC1 evidence | transcript evidence | remark evidence |
| CIF | 18,731 | 51.2%(18,731) | 32.5%(18,731) | 30.4%(18,731) | 22.2%(18,731) | 12.9%(18,731) | 18.3%(18,731)
|
| account | 19,292 | 50.8%(19,292) | 32.7%(19,292) | 30.6%(19,292) | 22.3%(19,292) | 13.0%(19,292) |
18.4%(19,292) |
**Q0.nr_unknown_rpc**
| month end | A2 state | accounts | RPC since March (CIF) | RPC since March (account) | age of latest CIF RPC
(accounts) |
| 2026-07-31 | non_reachable | 12,151 | 40.1%(12,151) | 39.5%(12,151) | 0-30: 431; 31-60: 1,255; 61-90: 1,243;
91-180: 1,946 |
| 2026-07-31 | unknown | 2,200 | 17.6%(2,200) | 16.6%(2,200) | 0-30: <10; 31-60: <10; 61-90: 10; 91-180: 369 |
**Q0.store_without_rpc**
| month end | store conv 90d (accounts) | no RPC 90d | of those: any DCORE call ever (attempts / inbound
without an RPC result) | of those: no DCORE call at all |
| 2026-07-31 | 1,934 | 19.5%(1,934) | 99.7%(377) | 0.3%(377) |
**Q0.reconcile_A2**
| month end | accounts | reachable and RPC in W | reachable, no RPC in W | not reachable, RPC in W | neither |
reachable-only: A2 contact date in W (contact outside the RPC list: inbound or SUC) | RPC-only: of which
non_reachable (gone-dark override) | RPC-only: of which A2 last_contact in W |
| 2026-07-31 | 18,397 | 3,835 | 211 | 2,919 | 11,432 | 100.0%(211) | 100.0%(2,919) | 100.0%(2,919) |
**Q0.flow**
| month end | accounts | new RPC (30d, own agreements) | new store conv (30d) | new UC1 reading (30d) | store
ceiling: reading < 30 d if UC1 read every store conv | store ceiling: reading < 90 d | RPC ceiling: reading <
30 d if every RPC had a transcript | RPC ceiling: reading < 90 d | CIFs with a UC1 reading < 30 d (today) |
CIFs with a UC1 reading < 90 d (today) |
| 2026-07-31 | 18,397 | 3,063 | 77 | 72 | 77 | 1,934 | 3,097 | 6,723 | 69 | 1,249 |
**Q0.remark_only**
| month end | CIFs (remark only) | store conv same day or day before | in UC1 metadata (same day / day before)
| metadata and extracted | DCORE RPC that day | DCORE call, no RPC (attempts only) | no DCORE call that day |
| 2026-07-31 | 1,203 | 97.1%(1,203) | 97.1%(1,203) | 2.6%(1,203) | 51.0%(1,203) | 41.4%(1,203) | 7.6%(1,203) |
**Q0.coverage_by** 07-31
| dimension | level | accounts | reading any age | reading under 90 d | under 90 d as % of store-conv accounts
(store ceiling) | under 90 d as % of RPC-90d accounts (RPC ceiling) | store conv 90d | RPC 90d (CIF) |
| A2 state | non_reachable | 12,151 | 16.6%(12,151) | 5.4%(12,151) | 57.9%(1,033) | 18.6%(2,893) |
8.5%(12,151) | 23.8%(12,151) |
| A2 state | reachable | 4,046 | 31.5%(4,046) | 14.8%(4,046) | 68.9%(800) | 15.5%(3,812) | 19.8%(4,046) |
94.2%(4,046) |
| A2 state | unknown | 2,200 | 10.4%(2,200) | 2.1%(2,200) | 40.6%(101) | 33.3%(18) | 4.6%(2,200) | 0.8%(2,200)
|
| DPD band | 121-150 | 4,091 | 20.9%(4,091) | 2.4%(4,091) | 76.0%(75) | 5.5%(1,292) | 1.8%(4,091) |
31.6%(4,091) |
| DPD band | 151-180 | 3,154 | 6.2%(3,154) | 1.0%(3,154) | 71.0%(31) | 2.7%(777) | 1.0%(3,154) | 24.6%(3,154)
|
| DPD band | 61-90 | 6,240 | 22.6%(6,240) | 13.4%(6,240) | 60.1%(1,347) | 27.7%(2,766) | 21.6%(6,240) |
44.3%(6,240) |
| DPD band | 91-120 | 4,912 | 21.6%(4,912) | 6.7%(4,912) | 62.8%(481) | 14.7%(1,888) | 9.8%(4,912) |
38.4%(4,912) |
**Q0.recency_x_reach** 07-31, >=100 accounts
| latest RPC age | A2 state | accounts | store conv (90d) | any UC1 reading (any age) | UC1 reading under 90
days |
| none since March | reachable | 140 | 2.1%(140) | 7.1%(140) | 1.4%(140) |
| none since March | non_reachable | 7,276 | 2.4%(7,276) | 2.8%(7,276) | 0.6%(7,276) |
| 0-30 | reachable | 2,728 | 18.3%(2,728) | 30.6%(2,728) | 13.9%(2,728) |
| 0-30 | non_reachable | 431 | 23.0%(431) | 36.7%(431) | 18.8%(431) |
| 31-60 | reachable | 710 | 24.5%(710) | 34.8%(710) | 18.5%(710) |
| 31-60 | non_reachable | 1,255 | 25.3%(1,255) | 36.4%(1,255) | 19.0%(1,255) |
| 61-90 | reachable | 388 | 30.4%(388) | 35.6%(388) | 21.4%(388) |
| 61-90 | non_reachable | 1,243 | 27.8%(1,243) | 33.7%(1,243) | 18.4%(1,243) |
| 91-180 | non_reachable | 1,946 | 5.0%(1,946) | 40.1%(1,946) | 3.2%(1,946) |
**Q1.outcome** pooled
| month end | accounts | reachable | non_reachable | unknown | deceased | left_top_band | left_other |
| pooled | 16,386 | 47.7%(16,386) | 30.2%(16,386) | 2.3%(16,386) | 0.1%(16,386) | 6.2%(16,386) | 13.6%(16,386)
|
**Q1.dark_by_group**
| group | accounts | going-dark rate [95%] | vs C2 | vs C3 | vs C4 |
| C1 | 2,337 | 29.4%[27.5, 31.3](2,337) | -4.0 pp[-12.5, +4.6] | +1.5 pp[-0.2, +3.6] | -30.6 pp[-34.0, -27.0]
|
| C2 | 90 | 33.3%[24.7, 42.3](90) | - | +5.5 pp[-3.2, +14.7] | -26.6 pp[-35.7, -16.2] |
| C3 | 12,890 | 27.8%[26.9, 28.7](12,890) | -5.5 pp[-14.7, +3.2] | - | -32.2 pp[-35.3, -29.2] |
| C4 | 1,069 | 60.0%[56.9, 62.8](1,069) | +26.6 pp[+16.2, +35.7] | +32.2 pp[+29.2, +35.3] | - |
**Q1.dark_by_contact_age**
| last-contact age | accounts | C1 | C2 | C3 | C4 | C1 - C2 | C1 - C3 | C1 - C4 |
| 0-30 | 12,418 | 26.0%[23.6, 28.0](1,558) | 31.3%[20.8, 43.1](67) | 25.4%[24.4, 26.3](9,996) | 68.4%[64.9,
71.5](797) | -5.3 pp[-16.6, +4.5] | +0.6 pp[-1.8, +2.7] | -42.4 pp[-46.5, -38.4] |
| 31-60 | 2,624 | 34.9%[30.1, 38.1](493) | 40.0%[13.3, 69.2](15) | 34.6%[32.7, 36.7](1,955) | 32.9%[27.1,
40.0](161) | -5.1 pp[-35.5, +22.0] | +0.3 pp[-4.9, +4.0] | +2.0 pp[-6.2, +8.7] |
| 61-90 | 1,337 | 38.1%[32.7, 44.4](286) | <10(<10) | 39.2%[36.4, 42.0](939) | 39.4%[29.7, 46.8](104) | <10 |
-1.1 pp[-7.1, +5.5] | -1.3 pp[-11.7, +10.0] |
**Q1.dark_by_signal_age**
| signal | age band | accounts | going-dark rate [95%] | vs C2 | vs C3 | vs C4 |
| any positive | 0-30 | 354 | 19.2%[15.3, 23.0](354) | -13.9 pp[-24.4, -4.4] | -8.6 pp[-12.6, -4.6] | -41.8
pp[-47.3, -36.2] |
| any positive | 31-60 | 939 | 29.4%[26.5, 32.4](939) | -4.9 pp[-15.9, +4.8] | +0.4 pp[-2.4, +3.2] | -26.8
pp[-30.8, -22.9] |
| any positive | 61-90 | 1,044 | 32.8%[30.0, 36.0](1,044) | -1.1 pp[-12.8, +9.4] | +3.3 pp[+0.6, +6.7] | -24.5
pp[-28.3, -20.6] |
| any positive | 91-180 | 964 | 32.9%[30.2, 36.0](964) | -0.5 pp[-9.7, +9.0] | +4.7 pp[+2.4, +7.5] | -26.8
pp[-30.2, -22.9] |
| any negative | 0-30 | 171 | 17.0%[10.1, 22.6](171) | -15.9 pp[-28.4, -6.4] | -10.4 pp[-16.9, -4.5] | -45.2
pp[-52.1, -37.7] |
| any negative | 31-60 | 520 | 29.0%[25.6, 32.9](520) | -5.2 pp[-16.2, +3.8] | +0.2 pp[-3.4, +3.7] | -27.2
pp[-31.8, -23.1] |
| any negative | 61-90 | 602 | 33.1%[29.4, 36.8](602) | -1.0 pp[-12.4, +8.9] | +3.4 pp[-0.3, +7.1] | -23.6
pp[-28.3, -18.0] |
| any negative | 91-180 | 614 | 33.4%[29.4, 36.9](614) | -0.1 pp[-9.3, +10.7] | +4.9 pp[+0.9, +8.6] | -25.5
pp[-29.6, -20.9] |
**Q2.groups**
| A2 state | group | account-months | mean due (AED) | mean outstanding (AED) | location_state | paid_due next
month [95%] | money collected next month (mean AED) |
| non_reachable | C1 | 2,964 | 1,461 | 30,686 | in_country 52%; unknown 26%; skip 22% | 12.8%[11.3,
14.3](2,260) | 314 |
| non_reachable | C2 | 147 | 1,434 | 28,102 | in_country 44%; skip 29%; unknown 27% | 4.6%[1.0, 7.9](109) |
142 |
| non_reachable | C3 | 12,754 | 1,302 | 31,380 | in_country 35%; unknown 33%; skip 31% | 11.3%[10.6,
11.9](10,403) | 263 |
| non_reachable | C4 | 39,597 | 1,172 | 27,548 | skip 49%; unknown 34%; in_country 17% | 3.7%[3.5,
3.9](29,652) | 90 |
| unknown / no_contact_in_window | C1 | 194 | 1,367 | 30,669 | in_country 60%; skip 20%; unknown 20% |
14.2%[8.1, 20.0](148) | 984 |
| unknown / no_contact_in_window | C2 | 12 | 1,228 | 24,088 | in_country 42%; skip 33%; unknown 25% |
0.0%[0.0, 0.0](11) | 0 |
| unknown / no_contact_in_window | C3 | 375 | 1,294 | 29,518 | skip 37%; in_country 33%; unknown 30% |
6.7%[3.7, 9.9](313) | 280 |
| unknown / no_contact_in_window | C4 | 7,640 | 1,079 | 25,794 | skip 51%; unknown 31%; in_country 18% |
6.6%[6.0, 7.5](5,811) | 176 |
| unknown / no_dcore_record | C4 | 1,120 | 244 | 4,304 | skip 54%; unknown 37%; in_country 9% | 2.0%[1.1,
3.2](847) | 305 |
**Q2.timing**
| group | when the latest evidence falls | account-months | evidence on or after last_attempt_date | days from
evidence to last_attempt_date (evidence before it) | paid_due next month [95%] |
| C1 | (a) on or before last_contact_date | 1,946 | 0.0%(1,946) | 0-30: 76; 31-60: 777; 61-90: 1,093; 91+: 0 |
13.2%[11.4, 15.0](1,473) |
| C1 | (b) after it / no contact ever (A2 does not see it) | 1,212 | 5.0%(1,211) | 0-30: 218; 31-60: 486;
61-90: 462; 91+: 0 | 12.3%[9.9, 14.7](935) |
| C2 | (a) on or before last_contact_date | 82 | 0.0%(82) | 0-30: <10; 31-60: 31; 61-90: 49; 91+: 0 |
5.1%[0.0, 10.0](59) |
| C2 | (b) after it / no contact ever (A2 does not see it) | 77 | 5.2%(77) | 0-30: 10; 31-60: 27; 61-90: 36;
91+: 0 | 3.3%[0.0, 7.7](61) |
**Q2.why_b**
| group | reason | account-months | % of (b) | DCORE direction (IC = inbound, OC / CB = outbound) | store
direction (field in facts) |
| C1 | DCORE call on the CIF, no RPC | 879 | 72.5%(1,212) | outbound: 878; both: <10 | outbound: 824; nan: 55
|
| C1 | nothing in DCORE that day (Genesys / remark only) | 285 | 23.5%(1,212) | nan: 285 | outbound: 169; nan:
116 |
| C1 | RPC on another account of the CIF (in the persona base) | 47 | 3.9%(1,212) | outbound: 47 | outbound:
45; nan: <10 |
| C1 | RPC on another account of the CIF (outside the persona base) | <10 | 0.1%(1,212) | outbound: <10 |
outbound: <10 |
| C2 | DCORE call on the CIF, no RPC | 64 | 83.1%(77) | outbound: 64 | outbound: 58; nan: <10 |
| C2 | nothing in DCORE that day (Genesys / remark only) | 13 | 16.9%(77) | nan: 13 | outbound: 11; nan: <10 |
**Q2.outcome_contrasts**
| group | account-months | paid_due [95%] | paid_due vs C3 | paid_due vs C4 | money vs C3 | money vs C4 |
| C1 all | 3,158 | 12.9%[11.5, 14.3](2,408) | +1.7 pp[+0.0, +3.3] | +8.7 pp[+7.4, +10.3] | +92 AED[+22, +174]
| +247 AED[+170, +326] |
| C1 (a) | 1,946 | 13.2%[11.4, 15.0](1,473) | +2.0 pp[+0.1, +4.1] | +9.1 pp[+7.3, +10.9] | +64 AED[-14, +159]
| +219 AED[+140, +307] |
| C1 (b) | 1,212 | 12.3%[9.9, 14.7](935) | +1.1 pp[-1.2, +3.6] | +8.2 pp[+5.8, +10.7] | +136 AED[+0, +281] |
+291 AED[+163, +437] |
| C1 strong positive < 90 d | 1,055 | 14.6%[12.5, 17.0](841) | +3.4 pp[+1.4, +5.9] | +10.5 pp[+8.4, +12.9] |
+70 AED[-26, +174] | +225 AED[+134, +341] |
| C1 (b) any positive < 90 d | 1,212 | 12.3%[9.9, 14.7](935) | +1.1 pp[-1.2, +3.6] | +8.2 pp[+5.8, +10.7] |
+136 AED[+0, +281] | +291 AED[+163, +437] |
| C2 all | 159 | 4.2%[0.9, 7.2](120) | -7.0 pp[-10.2, -4.2] | +0.0 pp[-3.2, +3.0] | -135 AED[-244, -28] | +20
AED[-78, +119] |
| C2 (b) | 77 | 3.3%[0.0, 7.7](61) | -7.9 pp[-11.3, -3.6] | -0.9 pp[-4.1, +3.7] | -148 AED[-259, +2] | +7
AED[-101, +155] |
| C3 | 13,129 | 11.2%[10.5, 11.8](10,716) | - | +7.1 pp[+6.3, +7.7] | - | +155 AED[+119, +206] |
| C4 | 48,357 | 4.1%[3.9, 4.4](36,310) | -7.1 pp[-7.7, -6.3] | - | -155 AED[-206, -119] | - |
**Q3.setup**
| item | value |
| cuts used (AED per account in 3 months, before the relative scaling): in-house / non-workable | 1030.6 /
115.5 |
| account share in-house / agency / non-workable, month ends 04-30 .. 07-31 | 15.4% / 55.1% / 29.5%(65,940) |
| money share (3-month collections, 04-30 and 05-31) in-house / agency / non-workable | 46.6% / 47.9% / 5.5% |
**Q3.groups_tier**
| group | tier | account-months | money next month (AED / account) | paid_due next month | money next 3 months
(04-30, 05-31) | money vs C4, same segment (diff) | paid_due vs C4, same segment |
| C1 | in_house | 93 | 449[232, 706](93) | 31.2%[21.8, 41.1](93) | 1.44e+03[583, 2.69e+03](49) | -40 AED[-259,
+249] | -3.2 pp[-14.0, +8.6] |
| C1 | agency | 1,861 | 376[285, 479](1,861) | 13.0%[11.5, 14.3](1,861) | 1.01e+03[801, 1.28e+03](718) | +226
AED[+133, +324] | +6.8 pp[+5.3, +8.2] |
| C1 | early_exit | 454 | 253[124, 452](454) | 8.6%[6.0, 11.4](454) | 718[352, 1.22e+03](196) | +211 AED[+84,
+424] | +7.1 pp[+4.6, +9.9] |
| C2 | in_house | <10 | <10(<10) | <10(<10) | <10(<10) | <10 | <10 |
| C2 | agency | 74 | 142[10.4, 316](74) | 4.1%[0.0, 8.1](74) | 1.11e+03[0, 2.92e+03](27) | -13 AED[-147, +153]
| -2.1 pp[-6.2, +1.9] |
| C2 | early_exit | 44 | 113[0, 297](44) | 4.5%[0.0, 11.9](44) | 156[0, 581](13) | +71 AED[-47, +245] | +2.9
pp[-1.7, +9.9] |
| C3 | in_house | 1,059 | 562[469, 657](1,059) | 35.7%[32.9, 38.7](1,059) | 1.52e+03[1.25e+03, 1.79e+03](617)
| +61 AED[-70, +211] | +0.3 pp[-5.5, +6.1] |
| C3 | agency | 7,116 | 284[235, 342](7,116) | 10.5%[9.7, 11.3](7,116) | 618[526, 710](3,664) | +135 AED[+81,
+197] | +4.4 pp[+3.4, +5.2] |
| C3 | early_exit | 2,541 | 81.8[57.9, 110](2,541) | 3.0%[2.5, 3.6](2,541) | 199[133, 263](1,251) | +39
AED[+11, +72] | +1.4 pp[+0.9, +2.1] |
| C4 | in_house | 573 | 528[429, 646](573) | 35.6%[30.6, 41.0](573) | 1.11e+03[816, 1.43e+03](243) | - | - |
| C4 | agency | 19,298 | 150[124, 182](19,298) | 5.4%[5.1, 5.7](19,298) | 362[303, 428](8,274) | - | - |
| C4 | early_exit | 16,439 | 45.4[35, 57](16,439) | 1.6%[1.4, 1.8](16,439) | 91.6[69.1, 115](7,428) | - | - |
**Q3.c1_variants**
| variant | account-months | tier mix in-house / agency / non-workable | money next month | paid_due next
month | money vs C4 | money vs C3 | paid_due vs C4 | paid_due vs C3 |
| C1 all | 2,408 | 3.9% / 77.3% / 18.9% | 355[282, 438](2,408) | 12.9%[11.4, 14.2](2,408) | +213 AED[+136,
+302] | +90 AED[-0, +185] | +6.4 pp[+5.1, +7.8] | +2.7 pp[+1.2, +4.2] |
| C1 strong positive < 90 d | 841 | 3.8% / 83.1% / 13.1% | 334[250, 440](841) | 14.6%[12.5, 17.0](841) | +186
AED[+106, +282] | +63 AED[-27, +163] | +7.9 pp[+5.7, +10.4] | +4.0 pp[+1.8, +6.6] |
| C1 any positive < 30 d | 163 | 6.7% / 84.0% / 9.2% | 408[254, 611](163) | 15.3%[10.6, 21.9](163) | +233
AED[+82, +444] | +114 AED[-40, +351] | +7.4 pp[+2.1, +13.2] | +3.7 pp[-1.8, +9.5] |
| C1 any positive 31-60 d | 836 | 5.4% / 78.6% / 16.0% | 340[230, 502](836) | 14.6%[12.4, 16.5](836) | +188
AED[+79, +367] | +59 AED[-57, +220] | +7.5 pp[+5.1, +9.3] | +3.8 pp[+1.3, +5.8] |
| C1 any positive 61-90 d | 1,409 | 2.6% / 75.7% / 21.6% | 358[251, 467](1,409) | 11.6%[10.0, 13.3](1,409) |
+225 AED[+120, +333] | +105 AED[-7, +240] | +5.7 pp[+4.3, +7.4] | +2.0 pp[+0.3, +4.2] |
| C1 latest evidence transcript | 1,039 | 4.9% / 76.0% / 19.1% | 353[252, 496](1,039) | 12.1%[10.0,
14.3](1,039) | +207 AED[+111, +340] | +81 AED[-38, +224] | +5.5 pp[+3.3, +7.6] | +1.7 pp[-0.5, +4.2] |
| C1 latest evidence remark | 1,369 | 3.1% / 78.2% / 18.7% | 357[270, 482](1,369) | 13.4%[11.7, 15.1](1,369) |
+217 AED[+131, +338] | +96 AED[-2, +230] | +7.2 pp[+5.5, +9.1] | +3.5 pp[+1.8, +5.4] |
| C1 (a) evidence on or before last contact | 1,473 | 3.8% / 77.2% / 19.0% | 327[244, 427](1,473) |
13.2%[11.5, 14.8](1,473) | +190 AED[+105, +293] | +66 AED[-24, +183] | +6.9 pp[+5.2, +8.6] | +2.9 pp[+1.0,
+4.6] |
| C1 (b) conversation A2 does not see | 935 | 4.0% / 77.4% / 18.6% | 400[269, 588](935) | 12.3%[10.4,
14.5](935) | +248 AED[+117, +414] | +127 AED[-35, +314] | +5.8 pp[+3.9, +7.9] | +2.4 pp[+0.4, +4.9] |
**Q3.whatif** 90-day rows
| override | accounts the rule applies to | accounts that change tier | money per mover (AED) |
| i_pos_90 | 2,408 | 2,315 | 352 |
| i_strong_90 | 841 | 809 | 338 |
| ii_conv_90 | 13,244 | 12,090 | 253 |
| iii_neg_90 | 1,214 | 912 | 234 |
**Q3.nonworkable**
| subset | account-months | money next month (AED / account) | paid_due next month |
| pool, all | 19,478 | 55.1[44.9, 66.6](19,478) | 1.9%[1.8, 2.1](19,478) |
| conversation < 90 d (C1 U C2 U C3) | 3,039 | 108[73.9, 145](3,039) | 3.8%[3.3, 4.5](3,039) |
| UC1 positive < 90 d (C1) | 454 | 253[114, 456](454) | 8.6%[6.3, 11.5](454) |
| UC1 positive < 30 d | 15 | 242[0, 679](15) | 6.7%[0.0, 20.0](15) |
| no conversation (C4) | 16,439 | 45.4[35.7, 54.9](16,439) | 1.6%[1.4, 1.7](16,439) |
**Q3.reverse**
| group | account-months | money next month (AED / account) | money vs the rest (same segment) | paid_due vs
the rest (same segment) |
| reachable in-house with a UC1 negative < 90 d | 548 | 727[542, 898](548) | +68 AED[-109, +236] | -5.5
pp[-9.7, -1.1] |

# rl_60_180
Tie-outs 07-31: all match (accounts=3728, reachable=1064, reading_post=679, reading_post_90=307,
reach_reading_90=130)
P1 CIF/account view 07-31: rpc_since_march 55.0/54.7%; rpc_90d 43.6/42.7%; store_conv_90d 12.9/13.3%;
any_uc1_reading 18.8/18.2%; uc1_reading_under_90d 8.5/8.2%
P2: n 429/0; rates - vs -; diff - pp [-,-]; no signal (empty); mde - pp; n at store/RPC ceiling 703/3442
P3: n 271/2169; rates 0.2472 vs 0.1697; diff +7.8 pp [+2.4,+13.9]; holds; mde 6.9 pp; n at store/RPC ceiling
506/1128
P4: n 659/3028; rates 30.55 vs 30.55; diff +0.0 pp [+0.0,+0.0]; no signal; mde - pp; n at store/RPC ceiling
1267/2252
**Q0.chain_cif** CIF view
| month end | base | 1 RPC since store start | 2 RPC 90d | 3 store conv 90d | 4 UC1 metadata 90d | 5
transcript reading | 6 remark reading | 7 any reading |
| 2026-07-31 | 3,338 | 55.0%(3,338) | 43.6%(3,338) | 12.9%(3,338) | 11.9%(3,338) | 4.6%(3,338) | 7.3%(3,338) |
8.5%(3,338) |
**Q0.ever** fixed window
| unit | base | RPC | store conv | UC1 metadata | any UC1 evidence | transcript evidence | remark evidence |
| CIF | 3,608 | 57.5%(3,608) | 32.2%(3,608) | 29.1%(3,608) | 20.1%(3,608) | 13.0%(3,608) | 15.7%(3,608) |
| account | 3,985 | 57.2%(3,985) | 32.4%(3,985) | 28.7%(3,985) | 19.6%(3,985) | 12.5%(3,985) | 15.6%(3,985) |
**Q0.nr_unknown_rpc**
| month end | A2 state | accounts | RPC since March (CIF) | RPC since March (account) | age of latest CIF RPC
(accounts) |
| 2026-07-31 | non_reachable | 2,031 | 44.5%(2,031) | 43.0%(2,031) | 0-30: 85; 31-60: 245; 61-90: 239; 91-180:
335 |
| 2026-07-31 | unknown | 633 | 21.6%(633) | 18.3%(633) | 0-30: <10; 31-60: <10; 61-90: <10; 91-180: 131 |
**Q0.coverage_by** 07-31
| dimension | level | accounts | reading any age | reading under 90 d | under 90 d as % of store-conv accounts
(store ceiling) | under 90 d as % of RPC-90d accounts (RPC ceiling) | store conv 90d | RPC 90d (CIF) |
| A2 state | non_reachable | 2,031 | 17.1%(2,031) | 7.7%(2,031) | 63.7%(237) | 18.8%(568) | 11.7%(2,031) |
28.0%(2,031) |
| A2 state | reachable | 1,064 | 24.9%(1,064) | 12.2%(1,064) | 60.6%(213) | 12.4%(1,043) | 20.0%(1,064) |
98.0%(1,064) |
| A2 state | unknown | 633 | 10.6%(633) | 3.2%(633) | 43.5%(46) | <10(<10) | 7.3%(633) | 0.9%(633) |
**Q1.outcome** pooled
| month end | accounts | reachable | non_reachable | unknown | deceased | left_top_band | left_other |
| pooled | 3,802 | 47.9%(3,802) | 26.4%(3,802) | 3.5%(3,802) | 0.4%(3,802) | 5.2%(3,802) | 16.6%(3,802) |
**Q1.dark_by_group**
| group | accounts | going-dark rate [95%] | vs C2 | vs C3 | vs C4 |
| C1 | 685 | 29.1%[25.9, 32.8](685) | -2.2 pp[-23.2, +16.8] | +3.7 pp[+0.4, +8.2] | -11.6 pp[-22.8, -3.7] |
| C2 | 16 | 31.2%[12.5, 50.1](16) | - | +5.9 pp[-13.0, +25.8] | -9.4 pp[-33.4, +10.6] |
| C3 | 3,015 | 25.3%[23.6, 26.9](3,015) | -5.9 pp[-25.8, +13.0] | - | -15.4 pp[-26.1, -6.2] |
| C4 | 86 | 40.7%[31.7, 51.5](86) | +9.4 pp[-10.6, +33.4] | +15.4 pp[+6.2, +26.1] | - |
**Q2.groups**
| A2 state | group | account-months | mean due (AED) | mean outstanding (AED) | location_state | paid_due next
month [95%] | money collected next month (mean AED) |
| non_reachable | C1 | 642 | 4,454 | 118,597 | in_country 61%; skip 22%; unknown 17% | 25.1%[21.3, 28.7](526)
| 1,716 |
| non_reachable | C2 | 28 | 2,931 | 88,383 | in_country 57%; skip 25%; unknown 18% | 18.2%[4.0, 35.8](22) |
684 |
| non_reachable | C3 | 2,755 | 4,277 | 131,303 | in_country 36%; skip 35%; unknown 28% | 17.0%[15.3,
18.4](2,169) | 1,075 |
| non_reachable | C4 | 6,012 | 3,668 | 107,796 | skip 55%; unknown 26%; in_country 19% | 11.1%[10.0,
12.3](4,428) | 755 |
| unknown / no_contact_in_window | C1 | 146 | 3,408 | 93,392 | in_country 47%; unknown 42%; skip 10% |
27.1%[18.9, 33.3](133) | 1,577 |
| unknown / no_contact_in_window | C2 | <10 | 3,992 | 148,716 | <10 | <10(<10) | - |
| unknown / no_contact_in_window | C3 | 217 | 2,874 | 80,539 | unknown 47%; skip 27%; in_country 26% |
17.2%[12.5, 22.7](174) | 1,190 |
| unknown / no_contact_in_window | C4 | 2,318 | 3,613 | 95,116 | skip 44%; unknown 42%; in_country 14% |
19.7%[17.7, 21.4](1,729) | 1,263 |
| unknown / no_dcore_record | C4 | 16 | 5,914 | 52,836 | unknown 69%; in_country 25%; skip 6% | 33.3%[14.3,
50.0](12) | 2,374 |
**Q2.why_b**
| group | reason | account-months | % of (b) | DCORE direction (IC = inbound, OC / CB = outbound) | store
direction (field in facts) |
| C1 | nothing in DCORE that day (Genesys / remark only) | 345 | 71.9%(480) | nan: 345 | outbound: 317; nan:
28 |
| C1 | DCORE call on the CIF, no RPC | 124 | 25.8%(480) | outbound: 124 | outbound: 119; nan: <10 |
| C1 | RPC on another account of the CIF (in the persona base) | <10 | 1.9%(480) | outbound: <10 | outbound:
<10 |
| C1 | RPC on another account of the CIF (outside the persona base) | <10 | 0.4%(480) | outbound: <10 |
outbound: <10 |
| C2 | nothing in DCORE that day (Genesys / remark only) | 15 | 60.0%(25) | nan: 15 | outbound: 13; nan: <10 |
| C2 | DCORE call on the CIF, no RPC | 10 | 40.0%(25) | outbound: 10 | outbound: 10 |
**Q2.outcome_contrasts**
| group | account-months | paid_due [95%] | paid_due vs C3 | paid_due vs C4 | money vs C3 | money vs C4 |
| C1 all | 788 | 25.5%[21.9, 28.4](659) | +8.5 pp[+4.5, +12.0] | +11.9 pp[+8.3, +15.5] | +604 AED[+214, +1011]
| +787 AED[+427, +1173] |
| C1 (a) | 308 | 25.5%[20.4, 31.4](255) | +8.5 pp[+3.2, +14.6] | +11.9 pp[+6.6, +18.4] | +770 AED[+200, +1381]
| +953 AED[+454, +1604] |
| C1 (b) | 480 | 25.5%[20.8, 30.2](404) | +8.5 pp[+3.7, +13.6] | +11.9 pp[+7.3, +16.4] | +499 AED[+103, +1076]
| +682 AED[+301, +1216] |
| C1 strong positive < 90 d | 281 | 28.6%[23.0, 34.5](245) | +11.6 pp[+6.2, +18.8] | +15.0 pp[+9.5, +20.8] |
+433 AED[-27, +910] | +616 AED[+151, +1108] |
| C1 (b) any positive < 90 d | 480 | 25.5%[20.8, 30.2](404) | +8.5 pp[+3.7, +13.6] | +11.9 pp[+7.3, +16.4] |
+499 AED[+103, +1076] | +682 AED[+301, +1216] |
| C2 all | 33 | 15.4%[3.0, 30.4](26) | -1.6 pp[-13.8, +13.3] | +1.8 pp[-10.5, +17.0] | -502 AED[-1037, +126] |
-319 AED[-783, +325] |
| C2 (b) | 25 | 14.3%[0.0, 31.8](21) | -2.7 pp[-16.6, +14.4] | +0.7 pp[-13.6, +17.8] | -497 AED[-1044, +288] |
-315 AED[-849, +420] |
| C3 | 2,972 | 17.0%[15.3, 18.3](2,343) | - | +3.4 pp[+1.5, +5.1] | - | +183 AED[+22, +374] |
| C4 | 8,346 | 13.6%[12.6, 14.6](6,169) | -3.4 pp[-5.1, -1.5] | - | -183 AED[-374, -22] | - |
**Q3.setup**
| item | value |
| cuts used (AED per account in 3 months, before the relative scaling): in-house / non-workable | 4789.9 /
1647.5 |
| account share in-house / agency / non-workable, month ends 04-30 .. 07-31 | 17.1% / 56.1% / 26.8%(12,999) |
| money share (3-month collections, 04-30 and 05-31) in-house / agency / non-workable | 24.1% / 62.1% / 13.8%
|
**Q3.groups_tier**
| group | tier | account-months | money next month (AED / account) | paid_due next month | money next 3 months
(04-30, 05-31) | money vs C4, same segment (diff) | paid_due vs C4, same segment |
| C1 | in_house | 67 | 1.68e+03[1.19e+03, 2.15e+03](67) | 44.8%[32.1, 58.7](67) | 4.61e+03[3.1e+03,
6.06e+03](26) | -982 AED[-1645, -324] | -5.3 pp[-19.4, +7.6] |
| C1 | agency | 445 | 1.71e+03[1.37e+03, 2.15e+03](445) | 26.3%[22.2, 30.0](445) | 4.22e+03[2.92e+03,
6.08e+03](188) | +629 AED[+213, +1070] | +9.6 pp[+5.0, +13.4] |
| C1 | early_exit | 147 | 1.62e+03[727, 2.85e+03](147) | 14.3%[9.4, 19.7](147) | 5.11e+03[2.26e+03,
8.44e+03](68) | +1151 AED[+266, +2414] | +8.2 pp[+3.8, +14.1] |
| C2 | in_house | <10 | <10(<10) | <10(<10) | <10(<10) | <10 | <10 |
| C2 | agency | <10 | <10(<10) | <10(<10) | <10(<10) | <10 | <10 |
| C2 | early_exit | 14 | 174[0, 533](14) | 7.1%[0.0, 22.3](14) | <10(<10) | -330 AED[-599, +33] | +0.8
pp[-7.0, +16.3] |
| C3 | in_house | 241 | 1.57e+03[1.21e+03, 2.01e+03](241) | 34.4%[28.5, 40.6](241) | 4.54e+03[3.61e+03,
5.6e+03](136) | -1181 AED[-2152, -461] | -21.6 pp[-30.3, -11.0] |
| C3 | agency | 1,435 | 1.26e+03[1.07e+03, 1.47e+03](1,435) | 18.8%[16.9, 20.6](1,435) | 3.76e+03[3.12e+03,
4.39e+03](719) | +172 AED[-83, +439] | +2.1 pp[-0.8, +4.4] |
| C3 | early_exit | 667 | 525[379, 659](667) | 6.7%[5.0, 8.8](667) | 2.19e+03[1.57e+03, 2.74e+03](325) | +46
AED[-125, +226] | +0.6 pp[-1.5, +2.7] |
| C4 | in_house | 446 | 2.7e+03[2.25e+03, 3.09e+03](446) | 48.4%[43.1, 52.9](446) | 6.53e+03[5.26e+03,
8.03e+03](187) | - | - |
| C4 | agency | 3,077 | 1.02e+03[877, 1.17e+03](3,077) | 14.7%[13.5, 16.0](3,077) | 3.08e+03[2.53e+03,
3.84e+03](1,178) | - | - |
| C4 | early_exit | 2,646 | 462[361, 557](2,646) | 6.4%[5.4, 7.4](2,646) | 1.55e+03[1.19e+03, 1.94e+03](1,180)
| - | - |
**Q3.c1_variants**
| variant | account-months | tier mix in-house / agency / non-workable | money next month | paid_due next
month | money vs C4 | money vs C3 | paid_due vs C4 | paid_due vs C3 |
| C1 all | 659 | 10.2% / 67.5% / 22.3% | 1.69e+03[1.35e+03, 2.01e+03](659) | 25.5%[22.4, 28.5](659) | +582
AED[+217, +975] | +583 AED[+234, +970] | +7.8 pp[+4.0, +11.0] | +8.5 pp[+5.1, +12.0] |
| C1 strong positive < 90 d | 245 | 11.8% / 71.0% / 17.1% | 1.52e+03[1.05e+03, 2.06e+03](245) | 28.6%[23.2,
34.0](245) | +347 AED[-117, +871] | +409 AED[-86, +983] | +9.8 pp[+4.3, +15.2] | +11.1 pp[+5.2, +15.9] |
| C1 any positive < 30 d | 127 | 14.2% / 70.9% / 15.0% | 2.47e+03[1.34e+03, 3.98e+03](127) | 23.6%[16.5,
30.1](127) | +1237 AED[+88, +2291] | +1257 AED[+66, +2289] | +2.9 pp[-4.8, +9.5] | +5.2 pp[-2.7, +12.1] |
| C1 any positive 31-60 d | 277 | 10.1% / 66.8% / 23.1% | 1.54e+03[1.18e+03, 1.99e+03](277) | 24.9%[19.5,
29.7](277) | +429 AED[+45, +909] | +437 AED[+38, +896] | +7.3 pp[+1.9, +11.9] | +7.8 pp[+2.2, +12.5] |
| C1 any positive 61-90 d | 255 | 8.2% / 66.7% / 25.1% | 1.46e+03[974, 1.92e+03](255) | 27.1%[21.4, 32.5](255)
| +421 AED[-33, +919] | +407 AED[-29, +944] | +10.8 pp[+4.8, +16.5] | +10.9 pp[+5.3, +16.7] |
| C1 latest evidence transcript | 372 | 9.9% / 68.8% / 21.2% | 1.91e+03[1.44e+03, 2.53e+03](372) | 27.7%[23.3,
32.1](372) | +784 AED[+307, +1405] | +784 AED[+275, +1459] | +9.5 pp[+4.9, +13.7] | +10.5 pp[+5.8, +14.7] |
| C1 latest evidence remark | 287 | 10.5% / 65.9% / 23.7% | 1.4e+03[989, 1.77e+03](287) | 22.6%[17.2,
28.1](287) | +320 AED[-113, +740] | +324 AED[-50, +743] | +5.6 pp[+1.3, +10.8] | +5.9 pp[+1.1, +10.9] |
| C1 (a) evidence on or before last contact | 255 | 7.1% / 71.8% / 21.2% | 1.85e+03[1.32e+03, 2.48e+03](255) |
25.5%[20.2, 31.3](255) | +777 AED[+245, +1453] | +704 AED[+211, +1366] | +8.1 pp[+3.7, +13.8] | +7.7 pp[+3.0,
+13.4] |
| C1 (b) conversation A2 does not see | 404 | 12.1% / 64.9% / 23.0% | 1.58e+03[1.23e+03, 2.02e+03](404) |
25.5%[21.4, 29.3](404) | +458 AED[+67, +1120] | +508 AED[+36, +1175] | +7.6 pp[+3.2, +11.6] | +9.0 pp[+4.1,
+13.0] |
**Q3.whatif** 90-day rows
| override | accounts the rule applies to | accounts that change tier | money per mover (AED) |
| i_pos_90 | 659 | 592 | 1,689 |
| i_strong_90 | 245 | 216 | 1,506 |
| ii_conv_90 | 3,028 | 2,717 | 1,169 |
| iii_neg_90 | 336 | 254 | 1,658 |
**Q3.reverse**
| group | account-months | money next month (AED / account) | money vs the rest (same segment) | paid_due vs
the rest (same segment) |
| reachable in-house with a UC1 negative < 90 d | 122 | 2.13e+03[1.55e+03, 2.79e+03](122) | -33 AED[-690,
+684] | -7.8 pp[-16.0, +1.2] |

# cc_180_plus
Tie-outs 07-31: all match (accounts=316738)
P1 CIF/account view 07-31: rpc_since_march 3.4/3.3%; rpc_90d 2.3/2.2%; store_conv_90d 0.0/0.0%;
any_uc1_reading 0.1/0.1%; uc1_reading_under_90d 0.0/0.0%
P2: n 164/0; rates - vs -; diff - pp [-,-]; no signal (empty); mde - pp; n at store/RPC ceiling 223/18597
P3: n 89/1794; rates 0.03371 vs 0.04013; diff -0.6 pp [-3.9,+3.3]; no signal; mde 5.9 pp; n at store/RPC
ceiling 130/1567
**Q0.chain_cif** CIF view
| month end | base | 1 RPC since store start | 2 RPC 90d | 3 store conv 90d | 4 UC1 metadata 90d | 5
transcript reading | 6 remark reading | 7 any reading |
| 2026-07-31 | 297,178 | 3.4%(297,178) | 2.3%(297,178) | 0.0%(297,178) | 0.0%(297,178) | 0.0%(297,178) |
0.0%(297,178) | 0.0%(297,178) |
**Q0.ever** fixed window
| unit | base | RPC | store conv | UC1 metadata | any UC1 evidence | transcript evidence | remark evidence |
| CIF | 299,026 | 4.1%(299,026) | 0.2%(299,026) | 0.2%(299,026) | 0.1%(299,026) | 0.1%(299,026) |
0.1%(299,026) |
| account | 318,663 | 3.9%(318,663) | 0.2%(318,663) | 0.2%(318,663) | 0.1%(318,663) | 0.1%(318,663) |
0.1%(318,663) |
**Q0.coverage_by** 07-31
| dimension | level | accounts | reading any age | reading under 90 d | under 90 d as % of store-conv accounts
(store ceiling) | under 90 d as % of RPC-90d accounts (RPC ceiling) | store conv 90d | RPC 90d (CIF) |
| A2 state | non_reachable | 21,014 | 0.3%(21,014) | 0.1%(21,014) | 77.8%(27) | 1.0%(414) | 0.1%(21,014) |
2.0%(21,014) |
| A2 state | reachable | 12,062 | 1.0%(12,062) | 0.5%(12,062) | 70.9%(79) | 0.6%(6,577) | 0.7%(12,062) |
54.5%(12,062) |
| A2 state | unknown | 283,662 | 0.0%(283,662) | 0.0%(283,662) | 56.8%(37) | 0.0%(42) | 0.0%(283,662) |
0.0%(283,662) |
**Q1.dark_by_group**
| group | accounts | going-dark rate [95%] | vs C2 | vs C3 | vs C4 |
| C1 | 340 | 5.6%[3.4, 7.8](340) | <10 | +3.1 pp[+1.0, +5.4] | +2.3 pp[+0.0, +4.8] |
| C2 | <10 | <10(<10) | - | <10 | <10 |
| C3 | 26,636 | 2.5%[2.3, 2.7](26,636) | <10 | - | -0.8 pp[-1.1, -0.5] |
| C4 | 22,418 | 3.3%[3.0, 3.5](22,418) | <10 | +0.8 pp[+0.5, +1.1] | - |
**Q2.groups**
| A2 state | group | account-months | mean due (AED) | mean outstanding (AED) | location_state | paid_due next
month [95%] | money collected next month (mean AED) |
| non_reachable | C1 | 121 | 1,527 | 49,737 | in_country 69%; unknown 21%; skip 9% | 3.0%[0.0, 6.3](100) | 403
|
| non_reachable | C2 | <10 | 1,361 | 26,328 | <10 | <10(<10) | - |
| non_reachable | C3 | 2,210 | 1,404 | 46,233 | unknown 42%; in_country 36%; skip 22% | 4.0%[3.0, 5.1](1,794)
| 249 |
| non_reachable | C4 | 98,563 | 1,177 | 76,209 | unknown 63%; skip 25%; in_country 12% | 1.5%[1.4,
1.6](79,164) | 76 |
| unknown / no_contact_in_window | C1 | 126 | 1,357 | 53,033 | in_country 63%; unknown 24%; skip 13% |
6.1%[0.9, 15.8](115) | 143 |
| unknown / no_contact_in_window | C2 | <10 | 1,370 | 56,648 | <10 | <10(<10) | - |
| unknown / no_contact_in_window | C3 | 356 | 1,215 | 60,968 | unknown 56%; in_country 30%; skip 14% |
9.2%[6.0, 12.8](283) | 426 |
| unknown / no_contact_in_window | C4 | 1,405,702 | 1,116 | 384,376 | unknown 88%; skip 11%; in_country 2% |
0.6%[0.6, 0.6](1,119,753) | 20 |
| unknown / no_dcore_record | C1 | <10 | 896 | 38,468 | <10 | <10(<10) | - |
| unknown / no_dcore_record | C3 | <10 | 896 | 38,468 | <10 | <10(<10) | - |
| unknown / no_dcore_record | C4 | 5,356 | 625 | 76,839 | unknown 92%; skip 6%; in_country 2% | 0.3%[0.1,
0.5](4,281) | 35 |
**Q2.outcome_contrasts**
| group | account-months | paid_due [95%] | paid_due vs C3 | paid_due vs C4 | money vs C3 | money vs C4 |
| C1 all | 249 | 4.6%[1.1, 9.4](217) | -0.1 pp[-4.0, +5.2] | +4.0 pp[+0.5, +8.8] | -11 AED[-234, +243] | +238
AED[+60, +483] |
| C1 (a) | 17 | 0.0%[0.0, 0.0](11) | -4.7 pp[-5.7, -3.6] | -0.6 pp[-0.7, -0.6] | -272 AED[-398, -173] | -24
AED[-25, -23] |
| C1 (b) | 232 | 4.9%[1.1, 9.9](206) | +0.1 pp[-3.9, +5.8] | +4.2 pp[+0.5, +9.3] | +3 AED[-228, +264] | +252
AED[+68, +515] |
| C1 strong positive < 90 d | 99 | 3.3%[0.0, 10.6](91) | -1.4 pp[-5.3, +5.7] | +2.7 pp[-0.7, +10.0] | -141
AED[-328, +65] | +108 AED[-13, +304] |
| C1 (b) any positive < 90 d | 232 | 4.9%[1.1, 9.9](206) | +0.1 pp[-3.9, +5.8] | +4.2 pp[+0.5, +9.3] | +3
AED[-228, +264] | +252 AED[+68, +515] |
| C2 all | <10 | <10(<10) | <10 | <10 | <10 | <10 |
| C2 (b) | <10 | <10(<10) | <10 | <10 | <10 | <10 |
| C3 | 2,569 | 4.7%[3.6, 5.7](2,079) | - | +4.1 pp[+3.0, +5.1] | - | +248 AED[+150, +373] |
| C4 | 1,509,621 | 0.6%[0.6, 0.7](1,203,198) | -4.1 pp[-5.1, -3.0] | - | -248 AED[-373, -150] | - |
**Q3.positive_signal**
| group | account-months | share of account-months | paid_due next month [95%] |
| all accounts: positive_signal | 157,693 | 12.6%(1,254,900) | 8.1%[7.9, 8.3](157,693) |
| all accounts: the rest | 1,097,207 | 87.4%(1,254,900) | 0.1%[0.1, 0.2](1,097,207) |
**Q3.outside_group**
| subset | account-months | paid_due next month [95%] | money next month (AED / account) |
| non_reachable / unknown, inside the group (payment, promise or A4 able) | 108,292 | 5.7%[5.5, 5.9](108,292)
| 169[159, 180](108,292) |
| non_reachable / unknown, outside the group | 1,097,207 | 0.1%[0.1, 0.2](1,097,207) | 10.2[9.1,
11](1,097,207) |
| ... outside, UC1 positive < 90 d (C1) | 60 | 1.7%[0.0, 4.8](60) | 91.8[0, 259](60) |
| ... outside, UC1 positive < 30 d | 20 | 5.0%[0.0, 13.1](20) | 276[0, 705](20) |
| ... outside, strong positive < 90 d | 22 | 0.0%[0.0, 0.0](22) | 0[0, 0](22) |
| ... outside, C2 (reading, no positive) | <10 | <10(<10) | <10(<10) |
| ... outside, C3 (conversation, no reading) | 611 | 2.5%[1.3, 3.6](611) | 297[61.4, 587](611) |
| ... outside, C4 (no conversation) | 1,096,534 | 0.1%[0.1, 0.2](1,096,534) | 10[8.97, 10.9](1,096,534) |

# rl_180_plus
Tie-outs 07-31: all match (accounts=54819)
P1 CIF/account view 07-31: rpc_since_march 4.4/4.5%; rpc_90d 3.0/3.1%; store_conv_90d 0.1/0.2%;
any_uc1_reading 0.2/0.3%; uc1_reading_under_90d 0.1/0.1%
P2: n 63/0; rates - vs -; diff - pp [-,-]; no signal (empty); mde - pp; n at store/RPC ceiling 89/2660
P3: n 56/465; rates 0.1071 vs 0.06237; diff +4.5 pp [-2.4,+13.2]; watch; mde 9.9 pp; n at store/RPC ceiling
75/443
**Q0.chain_cif** CIF view
| month end | base | 1 RPC since store start | 2 RPC 90d | 3 store conv 90d | 4 UC1 metadata 90d | 5
transcript reading | 6 remark reading | 7 any reading |
| 2026-07-31 | 52,374 | 4.4%(52,374) | 3.0%(52,374) | 0.1%(52,374) | 0.1%(52,374) | 0.1%(52,374) |
0.1%(52,374) | 0.1%(52,374) |
**Q0.ever** fixed window
| unit | base | RPC | store conv | UC1 metadata | any UC1 evidence | transcript evidence | remark evidence |
| CIF | 52,904 | 5.4%(52,904) | 0.7%(52,904) | 0.6%(52,904) | 0.4%(52,904) | 0.3%(52,904) | 0.3%(52,904) |
| account | 55,371 | 5.4%(55,371) | 0.7%(55,371) | 0.6%(55,371) | 0.4%(55,371) | 0.3%(55,371) | 0.3%(55,371) |
**Q0.coverage_by** 07-31
| dimension | level | accounts | reading any age | reading under 90 d | under 90 d as % of store-conv accounts
(store ceiling) | under 90 d as % of RPC-90d accounts (RPC ceiling) | store conv 90d | RPC 90d (CIF) |
| A2 state | non_reachable | 2,948 | 1.7%(2,948) | 0.7%(2,948) | 90.9%(22) | 11.5%(131) | 0.7%(2,948) |
4.4%(2,948) |
| A2 state | reachable | 2,701 | 2.8%(2,701) | 1.4%(2,701) | 67.3%(52) | 1.7%(1,562) | 1.9%(2,701) |
57.8%(2,701) |
| A2 state | unknown | 49,170 | 0.0%(49,170) | 0.0%(49,170) | 45.5%(11) | - | 0.0%(49,170) | 0.0%(49,170) |
**Q1.dark_by_group**
| group | accounts | going-dark rate [95%] | vs C2 | vs C3 | vs C4 |
| C1 | 114 | 0.9%[0.0, 3.0](114) | <10 | -2.0 pp[-3.2, +0.2] | -2.5 pp[-3.8, -0.3] |
| C2 | <10 | <10(<10) | - | <10 | <10 |
| C3 | 5,891 | 2.8%[2.4, 3.3](5,891) | <10 | - | -0.6 pp[-1.2, +0.1] |
| C4 | 4,654 | 3.4%[2.9, 3.9](4,654) | <10 | +0.6 pp[-0.1, +1.2] | - |
**Q2.groups**
| A2 state | group | account-months | mean due (AED) | mean outstanding (AED) | location_state | paid_due next
month [95%] | money collected next month (mean AED) |
| non_reachable | C1 | 67 | 3,801 | 96,930 | unknown 66%; in_country 22%; skip 12% | 10.0%[3.2, 18.2](60) |
1,623 |
| non_reachable | C2 | <10 | 2,451 | 21,533 | <10 | <10(<10) | - |
| non_reachable | C3 | 589 | 4,850 | 148,161 | in_country 41%; unknown 31%; skip 28% | 6.2%[4.0, 8.4](465) |
694 |
| non_reachable | C4 | 13,803 | 4,190 | 129,415 | unknown 51%; skip 35%; in_country 14% | 1.9%[1.5,
2.2](10,807) | 244 |
| unknown / no_contact_in_window | C1 | 25 | 2,040 | 44,599 | in_country 92%; unknown 8% | 19.0%[0.0,
48.3](21) | 560 |
| unknown / no_contact_in_window | C2 | <10 | 2,580 | 85,736 | <10 | <10(<10) | - |
| unknown / no_contact_in_window | C3 | 81 | 2,831 | 66,810 | unknown 70%; in_country 20%; skip 10% |
9.1%[3.1, 15.7](77) | 2,552 |
| unknown / no_contact_in_window | C4 | 244,129 | 2,879 | 92,237 | unknown 86%; skip 12%; in_country 2% |
0.6%[0.5, 0.6](194,691) | 80 |
| unknown / no_dcore_record | C4 | 41 | 1,204 | 21,587 | unknown 88%; in_country 10%; skip 2% | 0.0%[0.0,
0.0](33) | 0 |
**Q2.outcome_contrasts**
| group | account-months | paid_due [95%] | paid_due vs C3 | paid_due vs C4 | money vs C3 | money vs C4 |
| C1 all | 92 | 12.3%[3.7, 21.5](81) | +5.7 pp[-2.5, +15.1] | +11.7 pp[+3.1, +20.8] | +390 AED[-929, +1424] |
+1259 AED[+302, +2281] |
| C1 (a) | <10 | <10(<10) | <10 | <10 | <10 | <10 |
| C1 (b) | 87 | 13.0%[4.0, 22.9](77) | +6.3 pp[-2.4, +15.9] | +12.3 pp[+3.3, +22.2] | +342 AED[-921, +1405] |
+1212 AED[+307, +2298] |
| C1 strong positive < 90 d | 18 | 0.0%[0.0, 0.0](13) | -6.6 pp[-9.0, -4.3] | -0.7 pp[-0.7, -0.6] | -260
AED[-1509, +1524] | +609 AED[-94, +2180] |
| C1 (b) any positive < 90 d | 87 | 13.0%[4.0, 22.9](77) | +6.3 pp[-2.4, +15.9] | +12.3 pp[+3.3, +22.2] | +342
AED[-921, +1405] | +1212 AED[+307, +2298] |
| C2 all | <10 | <10(<10) | <10 | <10 | <10 | <10 |
| C2 (b) | <10 | <10(<10) | <10 | <10 | <10 | <10 |
| C3 | 670 | 6.6%[4.3, 9.0](542) | - | +6.0 pp[+3.6, +8.3] | - | +869 AED[+326, +1810] |
| C4 | 257,973 | 0.7%[0.6, 0.7](205,531) | -6.0 pp[-8.3, -3.6] | - | -869 AED[-1810, -326] | - |
**Q3.positive_signal**
| group | account-months | share of account-months | paid_due next month [95%] |
| all accounts: positive_signal | 25,534 | 11.8%(216,823) | 10.0%[9.4, 10.6](25,534) |
| all accounts: the rest | 191,289 | 88.2%(216,823) | 0.1%[0.1, 0.1](191,289) |
**Q3.outside_group**
| subset | account-months | paid_due next month [95%] | money next month (AED / account) |
| non_reachable / unknown, inside the group (payment, promise or A4 able) | 14,869 | 7.8%[7.1, 8.4](14,869) |
821[747, 905](14,869) |
| non_reachable / unknown, outside the group | 191,289 | 0.1%[0.1, 0.1](191,289) | 34.3[27.7, 43.3](191,289) |
| ... outside, UC1 positive < 90 d (C1) | <10 | <10(<10) | <10(<10) |
| ... outside, UC1 positive < 30 d | <10 | <10(<10) | <10(<10) |
| ... outside, strong positive < 90 d | 0 | - | - |
| ... outside, C2 (reading, no positive) | 0 | - | - |
| ... outside, C3 (conversation, no reading) | 166 | 0.6%[0.0, 2.0](166) | 1e+03[0, 3.25e+03](166) |
| ... outside, C4 (no conversation) | 191,114 | 0.1%[0.1, 0.2](191,114) | 33.3[26.7, 41.3](191,114) |

# Where to find the full results (copy from here when a segment needs more)
All files are in `tmp_validation/uc1_reach/` (repo root: `/workspaces/retail.collections.risk_profiling`).
- `uc1_reach_<model_id>.md`: every table of the run for `cc_60_180`, `rl_60_180`, `cc_180_plus`,
`rl_180_plus`, same table names as here (`Q0.*` coverage ceiling, `Q1.*` going dark, `Q2.*` unreachable but
talking, `Q3.*` tier / positive-signal group), plus the full G3 tier tie-out.
- `uc1_reach_<model_id>.json`: the same tables as data: `tables["Q2.signals"] = {title, header, rows}`; also
`primary` (P1-P4), `tie_outs`, `tier_tie_out`, `facts`.
- Left out here but in those files: all per-month rows (Q0 tables), `Q0.recency_x_reach` (all months),
`Q0.coverage_by` A3 / A4 levels, `Q1.dark_by_signal_age` (every signal level x age band), `Q1.dark_within_*`,
`Q1.last_conversation`, `Q1.context`, `Q1.agelimit`, `Q2.signals` (every level x band, C1 and C2),
`Q2.agelimit`, `Q3.whatif` money columns, and for rl / 180+ models the tables dropped above.
- `README.md`: definitions (RPC, groups, signal ages, tier, outcomes) and the frame's column list.
`_facts_<model_id>.json`: run facts (store dates, outcome months, tier mapping).
- Row-level data (the frame `uc1_reach_frame`) lives on PROD HDFS only, never in the repo. A new cut needs
`main(catalog, rebuild=False)` on PROD or a pandas load of the frame.
