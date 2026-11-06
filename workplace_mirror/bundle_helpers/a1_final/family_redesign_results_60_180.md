# Handoff 47: `tmp_validation/a1_family_redesign/summary.md` (4 photos), 2026-11-06

## Context for Claude Code
- Source: 4 phone photos of the VS Code editor on a second (LG) monitor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99). Tabs: `pipeline_registry.py` (M), `15_refactor_dead_code.md`, `summary.md` (active, no U). Path: `tmp_validation > a1_family_redesign > summary.md`. Blame header (photo 4): "You, 33 seconds ago | 1 author (You)"; blame on line 1: "You, 51 minutes ago • Summarise the A1 family redesign results for cc…" (cut off).
- Title: "A1 family redesign - summary". Compares today's A1 (V0) with redesigned rule variants V1-V6 built from "families" of evidence (F1 income, F2a/F2b inflow, F3 spend, F4 cross-product, L liquidity, P profile), for `cc_60_180` and `rl_60_180`, and gives a verdict and a recommendation "to GRR". It follows the CASA / bounce work in handoffs 43-45 (V0 here equals the new B14 state mix of handoff 43 for CC: 45 / 2,769 / 5,568 / 10,910). Source files named: `results_cc_60_180.md`, `results_rl_60_180.md` (the 180+ results are not committed yet). Follows handoffs 1-46.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the results files.
- Photos overlap and are merged into source lines 1-186. Photo-to-line map (in the order sent): photo 1 = lines 1, 97, 148-186 (lines 147-148 cut at the top edge); photo 2 = lines 1, 96-153; photo 3 = lines 1, 8, 50-105; photo 4 = lines 1-58. Line 186 is blank and is the last line shown.
- Source lines are hard-numbered in the editor. Long paragraphs are one source line that the editor soft-wraps over several visual lines; they are kept as one numbered line, or as the continuation lines the editor numbers separately (for example lines 4-6, 12-14).
- The Mac link was available when this was written; it is saved to `~/Python/Collections/pics/claude_code_handoff_47.md` (if it is missing there, copy it from chat).

---

## `summary.md` (lines 1-186)

````
1   # A1 family redesign - summary
2
3   **Status: `cc_60_180` and `rl_60_180`.** `cc_180_plus` and `rl_180_plus` results are not committed yet; their sections
4   are NOT IN RESULTS. Sources: `results_cc_60_180.md` (latest month 2026-08, 19,292 rows / 18,731 CIFs) and
5   `results_rl_60_180.md`
6   (3,985 rows / 3,608 CIFs); W = 3, run 2026-11-06.
7
8   ## cc_60_180
9
10  **Step 0.**
11  - Sources: `prm_casa_transactions` (legs reach 26.5% of base CIFs in W; 65.7% have a CASA account),
12    `feat_cif_internal_salary_monthly` (3.0%), `wm_fea_casa_eod_avg_balance` (63.3%), `bo_rr_portf_actv_acct_mthly` (13.6%
13    of rows have another loan; 1.6% have one that is current), `feat_product_holding` (99.9%). Tie-out to
14    `feat_cif_casa_activity_monthly` = 1.0000.
15  - Salary flag: none in `prm_casa_transactions`; `wm_pri_labelled_transactions` has `salary_txn_flag` and `tran_id` (not
16    used). V1 therefore uses F2b, so V6 = V1; V1a / V3 use the month-level F2a approximation.
17  - Unplaced debits: 20.1% of debit AED, all `MISCELLANEOUS` (2.6% of legs); 60.6% of its legs / 92.0% of its AED mirror a
18    credit, i.e. mostly bank sweeps, correctly outside F3.
19  - Sweep share of F3: 26.7% of non-POS legs / 22.3% of their AED matched (18.9% of all F3 AED), mostly outward
20    remittances; they were dropped from F3.
21
22  **V0 check.** PASS (93,548 rows, 0 states differ).
23
24  **Families (latest month).**
25
26  | family | has data | >=1 point | reach into today's Unknown (>=1 point) | into no-CASA |
27  |---|---|---|---|---|
28  | F1 income | 100% | 25.8% | 0% (by construction) | 34.0% |
29  | F2b inflow | 14.5% | 9.8% | 2.3% | 0% |
30  | F2a (approx.) | 14.5% | 8.6% | 2.2% | 0% |
31  | F3 spend | 7.0% | 4.2% | 0% | 0% |
32  | F4 cross-product | ~100% | 3.6% | 2.5% | 1.2% |
33  | L liquidity | 100% | 2.8% | 0% | ~0% |
34
35  Strongest overlaps (>=1 point in both): F2a/F2b 8.6%, F1/F2b 3.8%, F2b/F3 3.4%; F4 and L overlap everything under 2%.
36  Capacity shock fires on 4.3% of rows (29.6% of rows with credits in W; 9.5% of today's Low).
37  "Holds another card" (99.9%) includes the scored card itself: ignore.
38
39  **Variants (latest month).**
40
41  | variant | high | moderate | low | unknown |
42  |---|---|---|---|---|
43  | V0 | 45 (0.2%) | 2,769 (14.4%) | 5,568 (28.9%) | 10,910 (56.6%) |
44  | V1 (= V6) | 394 (2.0%) | 3,246 (16.8%) | 5,175 (26.8%) | 10,477 (54.3%) |
45  | V1a | 346 (1.8%) | 3,219 (16.7%) | 5,250 (27.2%) | 10,477 (54.3%) |
46  | V2 | 466 (2.4%) | 3,343 (17.3%) | 5,092 (26.4%) | 10,391 (53.9%) |
47  | V3 | 202 (1.0%) | 3,102 (16.1%) | 5,511 (28.6%) | 10,477 (54.3%) |
48  | V4 (cap) | 394 (2.0%) | 3,645 (18.9%) | 4,776 (24.8%) | 10,477 (54.3%) |
49  | V5 (+shock) | 309 (1.6%) | 3,018 (15.6%) | 5,488 (28.4%) | 10,477 (54.3%) |
50
51  Unknown falls only 2.3 pp (56.6% -> 54.3%); High grows about 9x (45 -> 394) but stays 2%.
52
53  **Separation (cohort Jan-May 2026, 74,256 rows).** High > Moderate > Low holds for cure_3, pay_any_3 and roll_3 in every
54  variant (V0 too). V1 gaps (DPD-standardised): High-Moderate cure_3 +14.6pp, pay_any_3 +17.5pp, roll_3 -20.1pp;
55  Moderate-Low +6.1 / +13.1 / -10.7pp. V0 High-Moderate: +16.6 / +10.5 / -19.6pp (only 270 rows). V3 (+18.2 / +18.3 /
56  -22.5pp, 1,272 High rows) and V5 (+17.0 / +20.3 / -23.3pp, 1,977 High rows) have the widest High-Moderate gaps.
57  - V1 within A2 reachability: gaps hold in all three states (e.g. reachable cure_3 H-M +10.3pp, pay_any_3 +9.0pp).
58  - V1 within old A3 (indicative): only ~1,090 cohort rows carry an A3 state (High 22-25 per state), gaps are within noise
59    (e.g. low-A3 cure_3 H-M +1.4pp [-17.9, 20.7]); inconclusive, not evidence of either.
60  - Moved rows: moderate -> high (1,599) cure_3 32.6%, pay_any_3 61.5%, roll_3 51.0%, indistinguishable from today's High
61    (cure -2.2pp [-9.6, 5.1]). New High rows (2,190) vs V0 Moderate: cure_3 +12.6pp, pay_any_3 +16.0pp, roll_3 -17.8pp; vs
62    V0 High: cure -4.4pp [-11.7, 2.8], no significant difference.
63
64  **Family lift (cohort, strong vs none, standardised).** F1 +6.3pp cure / +19.3pp pay; F2b +16.5 / +22.7; F3 +18.3 /
65  +25.8; F4 +20.2 / +16.9; L +16.6 / +14.2. Inside today's Unknown only F4 has rows: strong (549) cure_3 22.2% vs 7.8%
66  (+12.9pp), pay_any_3 +10.4pp. F2b inside Unknown has 412 "some" rows against only 48 "none" rows, so no usable
67  comparison. Within no-CASA customers F2/F3/L are empty; F4 has little data. P: tenure >= 36 months +4.3pp cure / +4.3pp
68  pay vs shorter; employer category is almost all "SALARIED" and does not separate.
69
70  **Orthogonality (latest month).** Cramér's V V1 vs V0: A2 0.202 vs 0.190; A4 0.282 vs 0.287; old A3 0.176 vs 0.200. A4
71  and old A3 are present on only ~75 latest-month rows, so those two V values are not reliable.
72
73  **Sensitivity (V1).** No knob moves more than 5% of rows. Largest: `MIN_MONTHS` one less 4.9% (low->moderate 640,
74  moderate->high 298), High from 3: 1.8% (+284 High), High from 5: 1.2%, floor 2,000: 1.1%. The "2 dimensions" gate: 0
75  (cannot bind). F3 keeping sweep-matched debits: 0.4%; F2 without ambiguous credits: 0.2%.
76
77  **Verdict.**
78
79  | item | verdict |
80  |---|---|
81  | F1 | keep (reaches 26% of rows, still the base) |
82  | F2 | keep (clear lift, but only 14.5% of rows have credits in W; salary-inside vs approximate-off differ little) |
83  | F3 | keep as a supplement (strong lift, 7% coverage; sweep exclusion was right: it changes only 0.4%) |
84  | F4 | keep (the only family that reaches today's Unknown; 3.6% coverage; cards still missing) |
85  | L | drop (V2 adds 72 High rows, 0.4%; lift real but overlaps nothing new) |
86  | P | drop from scoring (tenure only; employer category uninformative) |
87  | V1 |
88    | fills High with High-like customers: yes. Shrinks Unknown: barely (2.3 pp). Stays orthogonal: A2 yes; A4 / A3 not
89      measurable |
90  | V4 |
91    | no better than V1: cap keeps ~400 more rows in Moderate; order holds, High-Moderate gaps +15.1 / +18.0 / -20.8pp,
92      about V1's |
93  | V5 |
94    | shock sharpens the High-Moderate gap (pay_any_3 +20.3pp) at the cost of 85 fewer High rows in the latest month
95      (1,977 vs 2,435 cohort rows) |
96
97  ## rl_60_180
98
99  **Step 0.**
100 - Reach: `prm_casa_transactions` legs 52.3% of base CIFs (CASA account 85.1%), salary 6.9%, WM balances 84.8%, another
101   loan on 17.4% of rows (2.3% current), `feat_product_holding` 99.9%. Same sources as CC; no source missing.
102 - Salary flag: none in `prm_casa_transactions` (same as CC), so V1 = V6 and V1a / V3 use the approximate F2a.
103 - Unplaced debits: 50.5% of debit AED (3.2% of legs), all `MISCELLANEOUS`; 97.5% of its AED mirrors a credit, so it is
104   bank sweeping and correctly outside F3.
105 - Sweep share inside F3 is in the results file (section 0b); F3 drops matched debits as in CC.
106
107 **V0 check.** PASS (16,497 rows, 0 states differ).
108
109 **Families (latest month).**
110
111 | family | has data | >=1 point | reach into today's Unknown (>=1 point) |
112 |---|---|---|---|
113 | F1 income | 100% | 18.8% | 0% (by construction) |
114 | F2b / F2a (approx.) | 31.6% (F2a) | 26.0% / 23.2% | 5.4% (F2a) |
115 | F3 spend | 10.6% | 7.4% | 0% |
116 | F4 cross-product | ~100% | 4.7% | 4.4% |
117 | L liquidity | 100% | 9.2% | 0% |
118
119 Strongest overlaps: F2a/F2b 23.2%, F1/F2b 8.5%, F2b/F3 5.9%; F4 overlaps everything under 1.3%. Capacity shock fires on
120 13.8% of rows (43.5% of rows with credits in W; 22.9% of today's Low, 19.8% of Moderate) - three times the CC rate.
121 Employer category and segment are known for 100% of RL rows (23% in CC).
122
123 **Variants (latest month).**
124
125 | variant | high | moderate | low | unknown |
126 |---|---|---|---|---|
127 | V0 | 11 (0.3%) | 354 (8.9%) | 1,783 (44.7%) | 1,837 (46.1%) |
128 | V1 (= V6) | 87 (2.2%) | 617 (15.5%) | 1,547 (38.8%) | 1,734 (43.5%) |
129 | V1a | 70 (1.8%) | 584 (14.7%) | 1,597 (40.1%) | 1,734 (43.5%) |
130 | V2 | 124 (3.1%) | 672 (16.9%) | 1,541 (38.7%) | 1,648 (41.4%) |
131 | V3 | 37 (0.9%) | 505 (12.7%) | 1,709 (42.9%) | 1,734 (43.5%) |
132 | V4 (cap) | 87 (2.2%) | 760 (19.1%) | 1,404 (35.2%) | 1,734 (43.5%) |
133 | V5 (+shock) | 61 (1.5%) | 446 (11.2%) | 1,744 (43.8%) | 1,734 (43.5%) |
134
135 Unknown falls 2.6 pp (46.1% -> 43.5%); High grows about 8x (11 -> 87). V1 High by product: Auto 23 (1.7%), Personal 27
136 (1.9%), Personal Cash 37 (3.0%).
137
138 **Separation (cohort Jan-May 2026, 12,512 rows).** V0 has only 13 High cohort rows, so its order cannot be read. V1:
139 High > Moderate > Low holds for all three outcomes, but the cure gaps are not significant (High-Moderate +8.6pp [-0.1,
140 17.3]; Moderate-Low +1.6pp [-0.5, 3.7]). pay_any_3 and roll_3 separate well: High-Moderate +15.3pp / -19.2pp,
141 Moderate-Low +14.3pp / -6.6pp. V3 and V5 break the cure_3 order (High-Moderate -2.2pp and -1.9pp); V2 weakens pay_any_3
142 (High-Moderate +5.3pp, not significant); V4 and V6 behave as V1.
143 - V1 within A2 reachability: pay_any_3 and roll_3 gaps hold in all three states; cure_3 High-Moderate is not significant
144   in any (+2.0 / +8.4 / +14.9pp, intervals include 0).
145 - V1 within old A3 (indicative, full coverage here): only "moderate" has enough High rows (145) and the gaps hold there
146   (cure_3 +9.6pp, pay_any_3 +12.0pp, roll_3 -19.1pp); in "low" (42 High) they are inconclusive.
147 - Moved rows: moderate -> high (192) pay_any_3 79.2%, +15.2pp vs stayers, roll_3 -21.3pp; cure_3 +8.0pp not significant.
148   New High rows (228) vs V0 Moderate: pay_any_3 +9.8pp [3.3, 16.3], roll_3 -13.7pp [-21.9, -5.5], cure_3 +5.0pp [-2.7,
149   12.7].
150
151 **Family lift (cohort, standardised to `none`).** Only the "strong" level carries lift. Strong vs none: F1 cure +4.2pp /
152 pay +24.8pp; F2b +5.6 / +21.8; F3 +14.5 / +27.0; F4 +14.4 / +12.8; L +15.8 / +7.2. The "some" level is **not** better
153 than none for F2b (cure -4.4pp, pay -9.2pp), F3 (-2.1 / -2.0) and L (-7.0 / -12.2): one point for "some" in those
154 families is not supported. Inside today's Unknown only F4 has usable rows: strong (81) cure_3 +16.6pp, pay_any_3
155 +15.7pp. P: employer = COMPANY (1,199 rows) cure_3 +10.6pp and roll_3 -11.2pp vs other employers, SALARIED -8.9pp cure;
156 tenure >= 36 months: not read here (see results section 5).
157
158 **Orthogonality (latest month, all rows present).** Cramér's V V1 vs V0: A2 0.186 vs 0.180; A4 0.119 vs 0.114; old A3
159 0.101 vs 0.111. V1 adds no dependence on any axis.
160
161 **Sensitivity (V1).** One knob moves more than 5%: `MIN_MONTHS` one less, 11.7% (low->moderate 349, moderate->high 117).
162 Next: High from 3 4.2%, k2 2.1%. The "2 dimensions" gate: 0 (cannot bind).
163
164 **Verdict.**
165
166 | item | verdict |
167 |---|---|
168 | F1 | keep (strong: pay_any_3 +24.8pp) |
169 | F2 | keep the strong level; the "some" level does not lift (needs data: rescore with some = 0) |
170 | F3 | keep the strong level only; 10.6% coverage; sweep exclusion right |
171 | F4 | keep (only family reaching Unknown; strong +16.6pp cure inside it) |
172 | L | drop (V2 adds 37 High, weakens pay_any_3 order gaps, "some" worse than none) |
173 | P | needs data: employer category is informative for cure in RL (COMPANY +10.6pp); not scored |
174 | V1 |
175   | fills High with High-like customers: yes for pay and roll, cure only directionally. Shrinks Unknown: slightly (2.6
176     pp). Orthogonal: yes |
177 | V3 / V5 | no (break the cure_3 order) |
178 | V4 | same as V1 on outcomes |
179
180 **Take to GRR (60-180, CC and RL): V1.** It is the simplest rule that gives a 8-9x larger High whose outcomes match or
181 beat today's High, keeps the High > Moderate > Low order on both products and adds no dependence on A2, A4 or old A3. CC
182 supports V5 as a refinement; RL does not (V5 breaks the cure_3 order), so V1 is the common choice. Two caveats for GRR:
183 Unknown barely moves (54% CC, 44% RL) because most delinquent customers have no inflow or spend data, which no scoring
184 change fixes; and in RL the "some" level of F2, F3 and L does not lift, so a V1 with "some" worth 0 should be tested
185 before sign-off. 180+ results are still needed.
186
````

## Notes on specific spots
- Sum checks that pass: every row of both variants tables adds up to the row count (CC 19,292 on lines 43-49; RL 3,985 on lines 127-133); RL V1 High by product 23 + 27 + 37 = 87 (line 135, same as line 128); CC V2 adds 466 - 394 = 72 High rows (line 85) and RL V2 adds 124 - 87 = 37 (line 172); V1 vs V5 latest-month High: 394 - 309 = 85 (line 94); Unknown falls 10,910 -> 10,477 (-2.3 pp on 19,292) and 1,837 -> 1,734 (-2.6 pp on 3,985); V0 in the CC table is the same as the new B14 state mix of handoff 43 (45 / 2,769 / 5,568 / 10,910) and V0 in the RL table is the same as the new B14 RL mix (11 / 354 / 1,783 / 1,837). The moved-rows counts (lines 60-61 and 147-148) stand alone and could not be cross-checked.
- Line 147: the part "roll_3 -21.3pp" is clear in the second photo, but the first photo (where the line is cut at the top edge) may read "-22.3pp". Copied as -21.3pp; check.
- Line 97: the heading reads `## rl_60_180` (the photos render the `l` like a `1`).
- Lines 87-95 (V1 / V4 / V5 verdict rows) are formatted in the source as a table row that is split over several lines: `| V1 |` on one line, then an indented `| fills ... |` continuation line, as shown. Same for lines 174-176. These are a ragged table in the source.
- Line 12: `bo_rr_portf_actv_acct_mthly` and line 11: `prm_casa_transactions` are as printed.
- Line 35: "F4 and L overlap everything under 2%." and line 119 "under 1.3%" are as printed.
- Line 180: "a 8-9x larger High" is as printed ("a" before a vowel-sounding number).
- OCR-risk digits: all numbers in lines 11-20, 28-33, 43-49, 54-62, 64-71, 73-75, 100-105, 113-120, 127-133, 138-149, 151-162, and the counts 93,548 and 16,497 (lines 22 and 107). Intervals in square brackets (lines 59, 61, 62, 139-140, 148-149) are especially OCR-risk.
