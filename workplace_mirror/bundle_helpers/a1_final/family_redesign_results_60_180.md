# Handoff 50: `tmp_validation/a1_family_redesign/summary.md` UPDATED with Round 2 (lines 1-444) (16 photos), 2026-11-09

## Context for Claude Code
- Source: 16 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`, branch `feature/persona_refactor*`). Tabs: `pipeline_registry.py`, `17_a3_credibility_engine.md`, `results_summary_cc_rl_60_180.md` (U), `summary.md` (M, active). Path `tmp_validation > a1_family_redesign > summary.md`. Blame on line 1: "You, 3 days ago - Summarise the A1 family redesign results for cc...". Photo 1 also shows "You, 9 minutes ago | 1 author (You)".
- This is the SAME file as handoff 47 (lines 1-186), now longer: **Round 1 (lines 1-185) is unchanged except one resolved reading, and a new "Round 2" section was added (lines 189-443, green change bar in the editor = uncommitted additions)**. Round 2 is the cleaned variants R0-R3, firing, flow audit, estimate for Unknown, and a combined verdict. Line 444 is empty (last line, cursor at Ln 1 in the last photo).
- Resolved from handoff 47: line 147 reads `roll_3 -21.3pp` (clearly legible now; the possible `-22.3pp` in handoff 47 was a misread).
- Segments: `cc_60_180` and `rl_60_180` only; 180+ is NOT IN RESULTS (lines 3-4, 185, 193, 432).
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged by the editor's line numbers into lines 1-444. Photo-to-line map (in the order sent): 1 = 1-35; 2 = 32-65; 3 = 61-94; 4 = 92-125; 5 = 118-151; 6 = 146-179; 7 = 176-209; 8 = 206-239; 9 = 232-265; 10 = 259-291; 11 = 288-321; 12 = 315-348; 13 = 346-379; 14 = 376-408; 15 = 404-437; 16 = 421-444.
- Long paragraph lines are hard-numbered as the editor shows them; several lines (e.g. 220-221, 232-241, 249-266, 270-301) are numbered short lines because of a source-file wrap that the editor keeps as separate lines. They are kept exactly as numbered. Table rows that wrap in the editor (verdict tables) are kept as one source line per row where the editor shows a single number, and as continuation lines where it shows separate numbers (lines 87-95, 174-176, 410-429).
- Saved to `~/Python/Collections/pics/claude_code_handoff_50.md` through the Mac link (if it is missing there, copy it from chat).

---

## `summary.md` (lines 1-444)

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
55  Moderate-Low +6.1 / +13.1 / -10.7pp. V0 High-Moderate: +16.6 / +10.5 / -19.6pp (only 270 rows).
56  V3 (+18.2 / +18.3 / -22.5pp, 1,272 High rows) and V5 (+17.0 / +20.3 / -23.3pp, 1,977 High rows) have the widest High-Moderate gaps.
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
87  | V1
88    | fills High with High-like customers: yes. Shrinks Unknown: barely (2.3 pp). Stays orthogonal: A2 yes; A4 / A3 not
89    measurable |
90  | V4
91    | no better than V1; cap keeps ~400 more rows in Moderate; order holds, High-Moderate gaps +15.1 / +18.0 / -20.8pp,
92    about V1's |
93  | V5
94    | shock sharpens the High-Moderate gap (pay_any_3 +20.3pp) at the cost of 85 fewer High rows in the latest month
95    (1,977 vs 2,435 cohort rows) |
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
174 | V1
175   | fills High with High-like customers: yes for pay and roll, cure only directionally. Shrinks Unknown: slightly (2.6
176   pp). Orthogonal: yes |
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
187 ---
188
189 # Round 2 - cleaned variants R0-R3, firing, flow audit, estimate for Unknown
190
191 **Status: `cc_60_180` and `rl_60_180`.** Sources: `results_r2_cc_60_180.md` (latest month 2026-08, 19,292 rows; scored
192 months 2026-01..05 + 2026-08, 93,548 rows; cohort 74,256 rows) and `results_r2_rl_60_180.md` (3,985 latest rows; 16,497
193 scored; cohort 12,512). Run 2026-11-06, W = 3. 180+ round 2 is NOT IN RESULTS.
194
195 **Variants.** R0 = round-1 V1 without the (non-binding) 2-dimensions gate. R1 = R0 with "some" worth 0 points for F2,
196 F3, F4.
197 R1b = R1 with F1 weak = 0 too. R2 = R1 with true F2a (salary-flagged legs left out). R3 = R2 with F4 counting the
198 customer's other current cards. R3b = R3 with F1 weak = 0.
199
200 **Checks (both products).** V0 reproduces `crx_<p>_a1_ability`: PASS, 0 states differ (CC 93,548 rows, RL 16,497). R0 =
201 round-1 V1:
202 YES, 0 differ. Salary-flag join on `cif_id, tran_id, tran_date` is reliable: CC 93.5% of flagged keys find a leg, RL
203 96.5%,
204 1.00 legs per key in both, so R2 uses true F2a. "One strong family -> Moderate, two -> High" holds with 0 breaking rows
205 for R1-R3 in both products.
206
207 ## cc_60_180
208
209 **States (latest month).**
210
211 | variant | high | moderate | low | unknown |
212 |---|---|---|---|---|
213 | V0 | 45 (0.2%) | 2,769 (14.4%) | 5,568 (28.9%) | 10,910 (56.6%) |
214 | R0 | 394 (2.0%) | 3,246 (16.8%) | 5,175 (26.8%) | 10,477 (54.3%) |
215 | R1 (= R1b) | 319 (1.7%) | 2,909 (15.1%) | 5,587 (29.0%) | 10,477 (54.3%) |
216 | R2 | 286 (1.5%) | 2,915 (15.1%) | 5,614 (29.1%) | 10,477 (54.3%) |
217 | R3 (= R3b) | 292 (1.5%) | 2,926 (15.2%) | 6,019 (31.2%) | 10,055 (52.1%) |
218
219 **Separation (cohort Jan-May, DPD-standardised gaps).** Order High > Moderate > Low > Unknown holds for cure_3,
220 pay_any_3 and
221 roll_3 in every variant.
222
223 | variant | H-M cure_3 | H-M pay_any_3 | H-M roll_3 | M-L cure_3 | M-L pay_any_3 | M-L roll_3 |
224 |---|---|---|---|---|---|---|
225 | V0 | +16.6 | +10.5 | -19.6 | +5.7 | +11.4 | -9.6 |
226 | R0 | +14.6 | +17.5 | -20.1 | +6.1 | +13.1 | -10.7 |
227 | R1 | +15.8 | +18.3 | -21.7 | +6.4 | +13.8 | -11.1 |
228 | R2 | +15.7 | +19.0 | -22.1 | +6.4 | +13.7 | -11.1 |
229 | R3 | +16.1 | +18.9 | -22.3 | +5.9 | +14.3 | -10.8 |
230
231 R3 outcomes by state (cure_3 / pay_any_3 / roll_3): High 33.2 / 62.2 / 49.3 (1,916 rows), Moderate 16.3 / 42.2 / 72.6,
232 Low
233 10.7 / 28.3 / 83.1, Unknown 7.5 / 19.0 / 87.9. Within A2 reachability the R3 gaps hold in all three states (e.g.
234 non_reachable
235 cure_3 H-M +11.0, pay_any_3 +22.0). Within old A3 the High cells hold 17-18 rows, so inconclusive.
236 Moved rows V0 -> R3: moderate -> high (1,269) cure_3 36.2%, +1.9pp [-5.6, 9.3] vs V0 High, i.e. indistinguishable. New
237 High rows
238 (1,707) vs V0 Moderate: +15.2 / +18.8 / -21.3pp; vs V0 High: -1.5 [-8.9, 5.8] / +8.0 [-0.5, 16.5] / -1.4. Exception: the
239 438
240 rows that jump low -> high have cure_3 23.7%, -11.5pp [-20.0, -2.9] vs V0 High (pay_any_3 and roll_3 not significantly
241 different).
242 Demoted rows behave as demoted: moderate -> low (310) pay_any_3 -8.8pp [-15.8, -1.8] vs stayers.
243
244 **Does "some" lift (cohort, vs none)?** F2b some: cure +1.4 [-0.3, 3.2], pay -1.2 [-3.9, 1.4] (no). F3 some: +3.5 / +5.3
245 (small).
246 F4 some: +6.5 / +2.5 (pay not significant). F1 weak: +1.4 / +9.8. Strong levels: F1 +6.3 / +19.3, F2b +16.5 / +22.7, F3
247 +18.3 / +25.8, F4 +20.2 / +16.9. Zeroing "some" (R0 -> R1) sharpened every gap, so keep it at 0.
248
249 **F1 weak is redundant.** R1b and R3b give identical states and identical outcomes to R1 and R3 (1 point alone cannot
250 reach
251 Moderate once "some" is 0). Weak stays as evidence (Low), not as a point.
252
253 **Firing (R3 families, latest month).** Strong / some / none / no data: F1 15.5 / 10.3 / 74.2 / 0%; F2 2.2 / 6.5 / 5.9 /
254 85.5%;
255 F3 1.3 / 2.9 / 2.8 / 93.0%; F4 2.1 / 5.5 / 92.4 / <0.1%. No-CASA customers: F2 and F3 are 100% no data; F4 strong 1.1%.
256 F1
257 strong falls from 21.5% (2026-01) to 15.5% (2026-08); the file gives no reason. Strong F2 rows qualify in 2 of 3 months
258 54.6%, all 3 months 45.4%; median month / anchor 7.5. Number of strong families (latest rows 81.5% / 16.6% / 1.3% / 0.5%
259 /
260 0.1% for 0..4): cure_3 8.5 / 15.7 / 30.2 / 33.3 / 49.7%, pay_any_3 22.1 / 41.4 / 60.2 / 63.1 / 66.7%. Monotone, and 2+
261 strong is
262 where High-like outcomes begin. Single families differ in profile: F4 alone cure_3 26.9% but pay_any_3 34.6%; F2 alone
263 24.0% / 64.9%.
264 Stability: R3 state unchanged month to month 79.7%; Low -> Unknown 3,457 of 13,247 Low rows (26%), because Unknown
265 depends on a CASA
266 leg appearing in W. F4 level 98.2% unchanged, F3 94.5%, F2 91.3%, F1 86.4%.
267
268 **Flow audit.**
269 - F2 counted: economic credits 96.7% of legs / 60.1% of AED; ambiguous `MISCELLANEOUS` credits 3.3% of legs / **39.9% of
270   AED**. Excluded
271   correctly: `DDS Rejects/Reversal` 29,187 legs, self transfers, cheque returns, subsidiaries.
272 - Counted narration stems with the largest AED are `CHQ RTN INSUFFICIENT` (124.8M AED, 474 legs) and `CHQ NO
273   INSUFFICIENT` (108.4M AED, 636
274   legs). Whether these are the ambiguous `MISCELLANEOUS` legs is NOT IN RESULTS (no stem x placement table). By name
275   they look like
276   returned-cheque entries, so check at leg level.
277 - Firers whose counted AED is mostly ambiguous `MISCELLANEOUS` do **worse than none**: cure_3 -2.3pp [-5.2, 0.7],
278   pay_any_3 -16.3pp
279   [-21.0, -11.6], roll_3 +6.5pp (818 rows). Other dominant types lift: inward remittance +5.6 / +11.7, cash deposit +4.2
280   / +8.0, internal transfer
281   others +9.0 / +6.2, own-account transfer +7.8 / +9.1 (so the keyword class does not mark it as bad). loan_disbursement
282   -2.5 / +4.8 (139 rows, not
283   significant).
284 - Round trips (credit mirrored by a debit within 3 days / 5%, any counterparty) are 45.5% of counted F2 AED; rows where
285   they are >= 50%:
286   cure_3 +1.7pp [-0.3, 3.7], pay_any_3 +3.4pp [0.4, 6.4] vs none, weaker than other dominant types (+4 to +9 / +6 to
287   +12).
288   Leaving `rt = 1` out changes 1,529 rows (1.6%): high -> moderate 293, moderate -> low 623, low -> unknown 610. Whether
289   the outcome
290   separation improves is NOT IN RESULTS (C6 reports state changes only).
291 - Rests on one leg (after taking single-leg dominated months out fewer than MIN_MONTHS qualify): F2 77.9% of strong
292   rows, F3 48.2%. This is a size,
293   not a verdict (a monthly rent transfer also looks like this).
294 - F3 counted: outward 62.3% of AED, POS 20.5%, cash 16.8%. Sweep-matched debits dropped: 11,661 legs, 17.5% of F3 AED.
295   All dominant F3
296   types lift similarly (remittance +9.6 / +13.0, POS +8.1 / +13.2, cash +12.2 / +15.1; "other" +9.2 / +13.7), so the
297   mechanical candidate
298   `sus = remittance` has no outcome support (12 rows would change in RL, none material).
299 - Leaving out the smaller F2 candidates changes few rows: cash_deposit 345 (0.4%), own_account_transfer 98,
300   loan_disbursement 76,
301   refund_reversal <10.
302
303 **Orthogonality (Cramér's V, latest month).** R3 vs V0: A2 0.199 vs 0.190. A4 0.328 vs 0.287 and old A3 0.214 vs 0.200
304 rest on 78 rows, not reliable.
305
306 **Sensitivity (R3).** Only `minmonths_less1` exceeds 5% (1,111 rows, 5.8%; low -> moderate 798, low -> high 128,
307 moderate -> high 185). Others:
308 high5 1.1%, floor2000 0.6%, k2 0.5%, high3 0.4%, floor500 0.3%, k0_5 0.2%, F3 keeping sweep-matched 0.2%, F2 without
309 ambiguous credits 0.1%.
310
311 **Estimate for Unknown (Part D).** Holdout 14,121 rows. AUC High vs rest: logistic 0.752, tree 0.750, boosting 0.766;
312 Moderate+ vs Low 0.558 / 0.543 / 0.602.
313 Exact accuracy 0.453 / 0.428 / 0.500 is below the majority class (0.590). The top tree split is employer / segment
314 unknown, and the Unknown rows
315 differ from the scored rows (employer unknown 82.5% vs 71.2%). The real test inside Unknown (cohort 36,430 rows):
316 estimated_high cure_3 10.8%, estimated_moderate
317 5.8%, estimated_low 8.7%; pay_any_3 19.7 / 19.2 / 18.3 pooled, but the standardised High-Moderate gap is **-4.3pp**
318 [-5.9, -2.7]; cure_3 and roll_3 order does not hold.
319 **The estimate does not order outcomes. Do not impute a state for Unknown.**
320
321 ## rl_60_180
322
323 **States (latest month).**
324
325 | variant | high | moderate | low | unknown |
326 |---|---|---|---|---|
327 | V0 | 11 (0.3%) | 354 (8.9%) | 1,783 (44.7%) | 1,837 (46.1%) |
328 | R0 | 87 (2.2%) | 617 (15.5%) | 1,547 (38.8%) | 1,734 (43.5%) |
329 | R1 (= R1b) | 56 (1.4%) | 411 (10.3%) | 1,784 (44.8%) | 1,734 (43.5%) |
330 | R2 | 45 (1.1%) | 408 (10.2%) | 1,798 (45.1%) | 1,734 (43.5%) |
331 | R3 (= R3b) | 48 (1.2%) | 408 (10.2%) | 2,159 (54.2%) | 1,370 (34.4%) |
332
333 By loan type, R3 High: Auto 14 (1.0%), Personal 14 (1.0%), Personal Cash 20 (1.6%).
334
335 **Separation (cohort, 12,512 rows; High has only 147-157 rows with outcomes in R1-R3).** Order holds on all three
336 outcomes for R0-R3.
337
338 | variant | H-M cure_3 | H-M pay_any_3 | H-M roll_3 | M-L cure_3 | M-L pay_any_3 | M-L roll_3 |
339 |---|---|---|---|---|---|---|
340 | R0 | +8.6 [-0.1, 17.3] | +15.3 | -19.2 | +1.6 [-0.5, 3.7] | +14.3 | -6.6 |
341 | R1 | +6.2 [-4.8, 17.1] | +15.6 | -20.6 | +5.9 | +23.3 | -14.9 |
342 | R2 | +2.3 [-9.3, 13.9] | +15.0 | -18.5 | +6.2 | +23.5 | -15.0 |
343 | R3 | +2.1 [-9.1, 13.3] | +13.8 | -17.4 | +6.6 | +25.2 | -15.7 |
344
345 Zeroing "some" (R0 -> R1) is the clearest gain in RL: Moderate-Low cure_3 goes from not significant to +5.9pp and
346 pay_any_3 from +14.3 to +23.3pp.
347 The High-Moderate cure_3 gap shrinks as the variants are cleaned (+8.6 -> +2.1) and is never significant. pay_any_3 and
348 roll_3 High-Moderate gaps are
349 significant in every variant. R3 outcomes (cure_3 / pay_any_3 / roll_3): High 19.7 / 83.7 / 48.3, Moderate 16.2 / 68.3 /
350 67.2, Low 9.6 / 43.0 / 83.0,
351 Unknown 8.6 / 35.2 / 85.8. Within A2 reachability the H-M pay_any_3 gap is significant in non_reachable (+22.2pp) and
352 unknown (+22.7pp) but
353 not in reachable (+5.5pp [-4.2, 15.3]); the H-M roll_3 and cure_3 gaps are not significant in any of the three (cure_3
354 -3.4 / -3.5 / +11.0). Within old A3 only
355 "moderate" has High rows (106-116) and shows cure_3 +1.3pp ns, pay_any_3 +8.0pp [-0.5, 16.5], roll_3 -13.7pp; the rest
356 are too small.
357 Moved rows V0 -> R3: moderate -> high (133) pay_any_3 87.5%, +21.2pp vs stayers, roll_3 -24.6pp; cure_3 +4.6pp ns. New
358 High rows (154) vs V0
359 Moderate: cure_3 +3.4 [-7.0, 13.8], pay_any_3 +18.7, roll_3 -20.3. Demoted moderate -> low (209): cure_3 -8.7pp,
360 pay_any_3 -24.5pp vs stayers.
361
362 **Does "some" lift (cohort, vs none)?** F2b some: cure -4.4pp [-9.6, 0.9], pay -9.2pp [-16.6, -1.8] (worse than none).
363 F3 some -2.1 / -2.0. F4 some +2.7 / +3.5
364 (not significant). F1 weak: -1.2 / +9.1. Strong levels: F1 +4.2 / +24.8, F2b +5.6 [-1.2, 12.4] / +21.8, F3 +14.5 [-1.9,
365 30.9] / +27.0, F4 +14.4 / +12.8 [-1.4, 27.1]. As in CC,
366 zeroing "some" is supported, and in RL more strongly. F1 weak is again redundant (R1b = R1, R3b = R3).
367
368 **Firing (latest month).** Strong / some / none / no data: F1 9.3 / 9.5 / 81.2 / 0%; F2 4.1 / 19.2 / 8.3 / 68.4%; F3 1.0
369 / 6.4 / 3.2 / 89.4%; F4 1.6 / 23.9 / 74.5 / 0%.
370 No-CASA customers: F2 and F3 100% no data; F4 strong 4.7%. Strong families (latest rows 86.1 / 12.3 / 1.2 / 0.4%):
371 cure_3 8.9 / 16.2 / 19.7 / 13.0% (3 strong = 29 cohort rows),
372 pay_any_3 39.4 / 65.8 / 82.6 / 78.3%, roll_3 84.5 / 68.4 / 51.1 / 69.6%. Monotone to 2 strong; the 3-strong cell is too
373 small. R3 state unchanged month to
374 month 80.6%; Low -> Unknown 607 against 2,919 Low rows staying Low. F2 strong rests on one leg for 84.3% of rows, F3
375 43.4%.
376
377 **Flow audit.**
378 - F2 counted: ambiguous `MISCELLANEOUS` credits are 7.1% of legs but **84.2% of counted AED**. The largest counted stems
379   are `CHQ RTN INSUFFICIENT` (171.3M AED) and `CHQ NO INSUFFICIENT`
380   (164.1M AED); same open question as CC.
381 - Firers dominated by ambiguous `MISCELLANEOUS` credits: cure_3 -5.7pp [-9.3, -2.0], pay_any_3 -20.5pp [-28.9, -12.1],
382   roll_3 +8.7pp vs none (609 rows). No other dominant type lifts
383   over none (inward remittance -1.5 / +5.0, cash deposit -4.5 / -0.2, internal transfer others -5.2 / -0.8).
384   loan_disbursement cure_3 -9.3pp [-15.3, -3.4]. In RL, F2 firing only lifts at the strong level (see above).
385 - Round trips are 88.6% of counted F2 AED. Rows with >= 50%: cure_3 -3.0pp, pay_any_3 +0.3pp vs none (no lift). Leaving
386   `rt = 1` out changes 760 rows (4.6%): high -> moderate 89, moderate -> low 366,
387   low -> unknown 302. Outcome effect NOT IN RESULTS.
388 - F3: no dominant type separates from none (all intervals include 0, 362 none rows). Sweep-matched debits dropped: 2,261
389   legs, 12.5% of F3 AED.
390 - Unplaced ambiguous debits (`MISCELLANEOUS`) are 25.0% of excluded F3 AED, consistent with round 1.
391
392 **Orthogonality (Cramér's V, latest month, all rows).** R3 vs V0: A2 0.175 vs 0.180; A4 0.148 vs 0.114; old A3 0.088 vs
393 0.111. The A4 dependence rises slightly; A2 and old A3 fall.
394
395 **Sensitivity (R3).** `minmonths_less1` 542 rows (13.6%; low -> moderate 442, low -> high 45, moderate -> high 55).
396 Others: k2 2.5%, k0_5 1.7%, high5 1.0%, high3 0.6%, floor2000 0.4%,
397 F2 without ambiguous credits 0.3%, floor500 and F3 keeping sweep-matched <10 rows.
398
399 **Estimate for Unknown (Part D).** Holdout 3,274 rows. AUC High vs rest: logistic 0.518, tree 0.475, boosting 0.472 (no
400 discrimination); Moderate+ vs Low 0.623 / 0.581 / 0.597.
401 Exact accuracy 0.479 / 0.432 / 0.624 vs majority class 0.798. Inside Unknown (4,116 cohort rows): estimated_high cure_3
402 6.7%, estimated_moderate 10.5%, estimated_low 7.7%; High-Moderate cure_3 gap
403 **-6.6pp** [-10.0, -3.2], pay_any_3 -4.2pp [-11.1, 2.7]. **Same verdict as CC: do not impute.** No RL months-on-book or
404 EMI source was read.
405
406 ## Verdict (60-180, CC and RL)
407
408 | item | verdict |
409 |---|---|
410 | "some" worth 0 points for F2 / F3 / F4 (R1) | **adopt.** Sharpens every gap in CC; in RL it removes the Moderate-Low
411   noise (pay_any_3 +14.3 -> +23.3pp). "Some" is not better than none for F2b and F3 in RL |
412 | F1 weak = 0 points (R1b) | **adopt.** Changes no state or outcome in either product, so it is a simpler rule. Weak
413   still counts as evidence (Low) |
414 | True F2a (R2, salary-flagged legs left out) | **adopt.** The salary-flag join is reliable (93.5% / 96.5%); separation
415   is unchanged in CC, High falls 319 -> 286 (CC) and 56 -> 45 (RL), and F2 no longer repeats F1's salary |
416 | Other cards in F4 (R3) | **adopt for the strong level only; decision for GRR on the rest.** High is unchanged; Unknown
417   falls to 52.1% (CC) and 34.4% (RL). But the Unknown -> Low rows behave like Unknown (RL 1,377 rows: cure_3 -0.7pp,
418   pay_any_3 -0.5pp vs stayers; CC pay_any_3 +0.1pp), and about 10-11pp below V0 Low on pay_any_3 (CC -10.1pp, RL
419   -11.1pp). The Unknown reduction is mostly relabelling |
420 | Rule behind R3 | **High = 2+ strong families, Moderate = 1, Low = evidence but none strong, Unknown = no evidence;
421   distress demotes one rung.** 0 breaks in A7. The High count is 6.5x today's in CC (45 -> 292) and 4.4x in RL (11 ->
422   48), smaller than round 1's V1 because "some" no longer scores |
423 | Ambiguous `MISCELLANEOUS` credits in F2 | **exclude from F2 strength** (candidate to confirm at leg level). Their
424   firers do worse than none in both products (pay_any_3 -16.3 / -20.5pp), and states barely change (CC 19 rows, RL 13)
425   |
426 | loan_disbursement credits | exclude (low impact: CC 76 rows, RL 69; RL cure_3 -9.3pp) |
427 | Cash-deposit, own-account, internal-transfer credits | keep (they lift in CC; no evidence against in RL) |
428 | Round-trip credits | **needs data:** rescore with `rt = 1` out and read the cohort separation. Sizes: CC 1,529 rows
429   (1.6%), RL 760 (4.6%, 89 Highs) |
430 | F3 exclusions | none. The mechanical `remittance` candidate has the same outcomes as other types |
431 | Estimate for Unknown (Part D) | **no.** It does not order outcomes in either product |
432 | 180+ | NOT IN RESULTS |
433
434 **Take to GRR: R3, with ambiguous `MISCELLANEOUS` credits out of F2.** Open points:
435 1. RL High is 45-48 latest rows and about 150 cohort rows. pay_any_3 and roll_3 separate, but the cure_3 High-Moderate
436    gap is not significant (+2.1pp [-9.1, 13.3]).
437 2. Whether Unknown -> Low should require more than other-card holding or ambiguous credits (see the R3 row). Options:
438    keep those rows Unknown, or accept the Low label.
439 3. `MIN_MONTHS` (2 of 3 months) is the one knob that moves more than 5% of rows (CC 5.8%, RL 13.6%). GRR should confirm
440    it.
441 4. The `CHQ RTN INSUFFICIENT` / `CHQ NO INSUFFICIENT` stems carry 233M AED (CC) and 335M AED (RL) of counted F2 inflow.
442    Confirm at leg level whether they are real inflows.
443 5. A4 and old A3 orthogonality in CC rests on 78 rows and cannot be read.
444
````

## Notes on specific spots
- Sum checks that pass (all latest-month state tables): CC rows sum to 19,292 in every variant (V0, V1, V1a, V2, V3, V4, V5; R0, R1, R2, R3); RL rows sum to 3,985 in every variant (same set). Strong-family and firing splits add to ~100% (CC F2 line 253 adds to 100.1% by rounding). Ratios: 292 / 45 = 6.5x and 48 / 11 = 4.4x (line 421-422); 394 / 45 = 8.8x and 87 / 11 = 7.9x (lines 51, 135).
- Handoff 47 flag resolved: line 147 `roll_3 -21.3pp` (not -22.3).
- Photo 6 / lines 168-173 (RL verdict table): the F1 and F2 verdict texts are read as F1 = `keep (strong: pay_any_3 +24.8pp)` and F2 = `keep the strong level; the "some" level does not lift (needs data: rescore with some = 0)`; the photo is at an angle and the F1/F2 text split is my best reading. F3's text (`10.6% coverage`) matches the F3 coverage in line 115.
- Lines 27 and 112: the separator rows were read as 5 and 4 dashes cells to match the headers; they are small and slanted in the photos.
- Lines 87-95 and 174-176: V1 / V4 / V5 verdict rows are ragged in the source (the `|` starts a new line, text continues on the next), copied as shown. Same for the verdict rows in lines 410-429 (continuation lines are indented as shown).
- Lines 232-241 etc.: odd one-word lines (`Low`, `non_reachable`, `High rows`, `438`) are separate numbered lines in the source, as shown. Line 239 is the lone `438` (a number inside the sentence "Exception: the 438 rows that jump low -> high").
- The Round 2 section is new vs handoff 47; Round 1 (lines 1-185) looks identical to what handoff 47 transcribed (same numbers in the same lines).
- RL R3 `Unknown -> Low` row count: line 417 says RL 1,377 rows; line 374 says "Low -> Unknown 607 against 2,919" (different direction), as printed.
- Cut/partially visible in the photos: the bottoms of photos 6 and 8-10 cut lines 179, 239-240, 265, 291; those lines are completed from the next photo. No line is missing.
- OCR-risk digits: all percentages and counts in the state tables (lines 43-49, 127-133, 213-217, 327-331), separation tables (lines 225-229, 340-343, with confidence intervals), firing lines 253-266 and 368-375, flow audit AED figures (124.8M, 108.4M, 171.3M, 164.1M, 233M, 335M), and the Part D AUC / accuracy numbers (lines 311-318, 399-404).
