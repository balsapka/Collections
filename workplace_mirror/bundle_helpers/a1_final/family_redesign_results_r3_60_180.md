# Handoff 55: `tmp_validation/a1_family_redesign/summary_r3.md` lines 1-346 (A1 family redesign, round 3 - summary) (7 photos), 2026-11-10

## Context for Claude Code
- Source: 7 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`; photographed on an LG monitor, menu bar shows "Help"). Tabs: `pipeline_registry.py`, `20_a3_promise_events_grr_deadline.md`, `summary_r3.md` (U = untracked, active). Path `tmp_validation > a1_family_redesign > summary_r3.md`, breadcrumb `# A1 family redesign, round 3 - summary`.
- It is the round-3 follow-up to `summary.md` (handoffs 47 and 50; rounds 1-2 unchanged, line 6). Round 3 tests R4 = "only positively identified flow classes, pairs netted" for F2/F3 (variants R4, R4cash, R4debt, R4reg, R4F4, as listed in the tables), the returned-cheque question, the flow dictionary, A6 (effect on today's A1 gate), and the Unknown analysis B0 (reason code), B1 (direct evidence candidates `x_*`, "F5"), B2 (inference). Products `cc_60_180` and `rl_60_180` only; 180+ NOT IN RESULTS. Sources named in lines 4-5: `results_r3_cc_60_180.md`, `results_r3_rl_60_180.md`, `flow_dictionary_<model_id>.md`. Run 2026-11-09. Follows handoffs 1-54.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- In the editor font `rl` looks like `r1` (lines 3, 5, 196, 340-341). I read it as `rl` (`rl_60_180`, `rl_180_plus`, `results_r3_rl_60_180.md`), consistent with the earlier handoffs; not verified character by character.
- Photos overlap and are merged into source lines 1-346. Photo-to-line map (in the order sent): photo 1 = lines 1-59; photo 2 = 55-109; photo 3 = 102-157; photo 4 = 156-210; photo 5 = 206-261; photo 6 = 257-311; photo 7 = 293-346. Line 346 is the last line shown (blank).
- Source lines are hard-numbered in the editor. Long paragraphs and bullets are one source line each, wrapped by the editor; the wrapped visual lines carry the next number only where the editor shows one (as numbered below).
- Written in the cloud workspace; saved to `~/Python/Collections/pics/claude_code_handoff_55.md` through the Mac link if it is up (see the chat reply); otherwise copy it there.

---

## `summary_r3.md` (lines 1-346)

````
1   # A1 family redesign, round 3 - summary
2
3   **Status: `cc_60_180` and `rl_60_180` only.** `cc_180_plus` and `rl_180_plus` are not committed: NOT IN RESULTS.
4   Sources: `results_r3_cc_60_180.md` (latest month 2026-08, 19,292 rows; cohort Jan-May 74,256 rows),
5   `results_r3_rl_60_180.md` (3,985 rows; cohort 12,512 rows), `flow_dictionary_<model_id>.md` (table only, see
6   below). W = 3 months, run 2026-11-09. `summary.md` (rounds 1-2) is unchanged. In every table "cure", "pay" and
7   "roll" are `cure_3`, `pay_any_3`, `roll_3` in %; gaps are DPD-band standardised percentage points (pp).
8
9   ## Headline
10
11  - **Checks pass in both:** V0 reproduces `crx_<p>_a1_ability` (0 states differ; 93,548 CC rows, 16,497 RL rows) and
12    R0 reproduces round-1 V1.
13  - **Cheques were counted as income.** Every returned-cheque credit that round 2 counted in F2 has an opposite leg
14    the same day (100% mirrored). Round 2 counted AED 186.1M (CC) and AED 264.0M (RL) of them in F2.
15  - **R4 (only positively identified classes, pairs netted) keeps CC separation and moves few rows.** F2 AED kept:
16    CC 60.7%, RL 37.9%. CC gaps stay within 0.4pp of R3. In RL, High shrinks to 117 cohort rows and the High vs
17    Moderate cure_3 gap turns negative (-4.6pp, interval includes 0); pay_any_3 and roll_3 still order.
18  - **Single-change variants:** keep `cash_in` (R4cash and R4reg demote rows that perform at Moderate level or
19    better); `debt_elsewhere` is irrelevant (R4debt = R4 state for state); R4F4 is not supported.
20  - **Unknown:** the reason code (B0) does not separate CC and in RL mostly reflects product mix. No direct evidence
21    source qualifies as F5 (B1). An inference (B2) passes all five criteria in CC; B2 crashed in RL.
22  - **Today's A1 gate is nearly fine:** only 17 CC rows (0.2%) and 14 RL rows (0.7%) leave Unknown solely on
23    non-evidence legs (A6).
24
25  ## cc_60_180
26
27  ### Cheque question
28
29  | stem (credit side) | legs | AED | class | mirrored in 3 days |
30  |---|---|---|---|---|
31  | CHQ NO INSUFFICIENT | 959 | 107.6M | reversal_return | 100.0% |
32  | CHQ RTN INSUFFICIENT | 474 | 77.8M | reversal_return | 100.0% |
33
34  - Round 2 counted F2 AED 186.1M and F3 AED 0.0M from cheque-narration stems. None of these legs is an internal
35    return event (0.0%), so `prm_casa_return_events` does not see them.
36  - Trace of every cheque leg (10 days, 0.5%): the debit `CHQ NO` (1,000 legs, AED 113.4M) is 100% paired, 95.9% of
37    its AED to a same-day `MISCELLANEOUS` credit classed reversal_return. `CHQ` (476 legs, AED 79.2M) is 100% paired.
38    Cheque-return and cheque-book charges are about AED 0.0M and not income either way.
39
40  ### Labels and the flow dictionary
41
42  - `wm_pri_labelled_transactions` joins to the legs on `cif_id, tran_id, tran_date`: 94.2% of flagged salary keys
43    find a leg (37,934 keys, 35,746 found), 1.00 legs per key. Verdict reliable, so true F2a is used.
44  - Dictionary: 142 combinations with >= 50 CIFs (2,820,933 legs, AED 5,697M) plus 2 stem rules; 304 smaller
45    combinations (20,342 legs, AED 584M) folded into `unplaced`. The table is in `flow_dictionary_cc_60_180.md`; I
46    did not check it line by line.
47  - Where the WM label and our lanes disagree: WM `self` (own account at another bank) on legs we do not call wash,
48    224,903 legs / AED 860.7M; our wash lane without a WM `self` label, 81,369 legs / AED 551.1M.
49  - Debt to other lenders is nearly invisible in the CASA legs: WM `wm_fea_external_loan_payments` has 9,427
50    CIF-months with a payment, of which we also see a `debt_elsewhere` debit in 354 (3.8%).
51
52  Round-2 counted AED by the class it now has:
53
54  | class | F2 AED (share) | F3 AED (share) |
55  |---|---|---|
56  | third_party_in | 643.0M (46.6%) | - |
57  | cash_in | 202.4M (14.7%) | - |
58  | reversal_return | 185.4M (13.4%) | 0.2M |
59  | unplaced | 350.0M (25.3%) | 14.1M (1.5%) |
60  | chosen_spend | - | 794.1M (87.4%) |
61  | own_transfer | - | 66.8M (7.3%) |
62  | bank_initiated | - | 32.6M (3.6%) |
63  | debt_elsewhere | - | 1.0M (0.1%) |
64  | total | 1,380.9M | 908.6M |
65
66  R4 keeps F2 AED 837.9M (60.7%) and F3 AED 790.1M (87.0%). Netting removes little beyond the class filter (F2: 7.5M
67  from rules A and B; F3: 5.0M).
68
69  Outcome lift of single combinations (60-180 cohort, vs rows with no credits): salary `INWARD REMITTANCE 507`
70  cure +13.0pp, pay +23.1pp, roll -18.8pp; `CASH DEPOSIT` cure +5.6pp, pay +19.8pp, roll -12.0pp (a real signal, so
71  cash_in stays); `CHEQUE RETURNS 126` credits cure -4.4pp, pay -6.3pp, roll +6.5pp (the opposite sign, as
72  expected); `DDS Rejects/Reversal 004` credits cure -2.0pp, roll +3.3pp.
73
74  ### R4 variants - state mix, latest month (19,292 rows)
75
76  | variant | high | moderate | low | unknown |
77  |---|---|---|---|---|
78  | R3 | 292 (1.5%) | 2,926 (15.2%) | 6,019 (31.2%) | 10,055 (52.1%) |
79  | R4 | 279 (1.4%) | 2,913 (15.1%) | 5,800 (30.1%) | 10,300 (53.4%) |
80  | R4cash | 259 (1.3%) | 2,909 (15.1%) | 5,824 (30.2%) | 10,300 (53.4%) |
81  | R4debt | 279 (1.4%) | 2,913 (15.1%) | 5,800 (30.1%) | 10,300 (53.4%) |
82  | R4reg | 237 (1.2%) | 2,859 (14.8%) | 5,896 (30.6%) | 10,300 (53.4%) |
83  | R4F4 | 279 (1.4%) | 2,913 (15.1%) | 5,230 (27.1%) | 10,870 (56.3%) |
84
85  R3 -> R4: 12 High -> Moderate, 22 Moderate -> Low, 242 Low -> Unknown (rows with only non-evidence legs); nothing
86  leaves Unknown. Strong rows resting on one leg (R3 -> R4): F2 68.2% -> 67.3%, F3 38.7% -> 39.5%; R4reg brings F2
87  down to 46.5%.
88
89  ### Separation (cohort Jan-May 2026, 74,256 rows)
90
91  Order High > Moderate > Low > Unknown holds for cure, pay and roll in all six variants.
92
93  | state | R3 rows | R3 cure / pay / roll | R4 rows | R4 cure / pay / roll |
94  |---|---|---|---|---|
95  | high | 1,916 | 33.2 / 62.2 / 49.3 | 1,844 | 33.1 / 61.9 / 49.1 |
96  | moderate | 14,191 | 16.3 / 42.2 / 72.6 | 14,210 | 16.4 / 42.3 / 72.5 |
97  | low | 21,719 | 10.7 / 28.3 / 83.1 | 21,341 | 10.8 / 28.7 / 82.8 |
98  | unknown | 36,430 | 7.5 / 19.0 / 87.9 | 36,861 | 7.4 / 18.9 / 87.9 |
99
100 | variant | High-Mod cure / pay / roll | Mod-Low cure / pay / roll |
101 |---|---|---|
102 | R3 | +16.1 / +18.9 / -22.3 | +5.9 / +14.3 / -10.8 |
103 | R4 | +15.9 / +18.5 / -22.5 | +5.9 / +14.1 / -10.7 |
104 | R4cash | +16.4 / +18.6 / -23.2 | +5.9 / +13.8 / -10.4 |
105 | R4debt | +15.9 / +18.5 / -22.5 | +5.9 / +14.1 / -10.7 |
106 | R4reg | +16.4 / +18.4 / -22.6 | +5.5 / +13.2 / -10.1 |
107 | R4F4 | +15.9 / +18.5 / -22.5 | +6.6 / +13.3 / -10.9 |
108
109 All High-Mod intervals are about +/-2.8pp wide and exclude 0. The variants are not separable on these gaps.
110
111 ### Moved rows (what the rows that change state look like)
112
113 Reference, R3 states: high 33.2 / 62.2 / 49.3; moderate 16.3 / 42.2 / 72.6; low 10.7 / 28.3 / 83.1; unknown
114 7.5 / 19.0 / 87.9 (cure / pay / roll, %).
115
116 | variant: move | rows | cure / pay / roll | reading |
117 |---|---|---|---|
118 | R4: high -> moderate | 70 | 37.1 / 71.4 / 54.3 | still High-like |
119 | R4: moderate -> low | 49 | 20.4 / 46.9 / 65.3 | Moderate-like |
120 | R4: low -> unknown | 429 | 4.4 / 11.4 / 93.2 | worse than Low |
121 | R4cash: high -> moderate | 190 | 29.5 / 64.2 / 57.9 | High-like |
122 | R4cash: moderate -> low | 219 | 20.5 / 59.8 / 59.4 | better than Moderate |
123 | R4reg: high -> moderate | 280 | 33.2 / 67.5 / 49.3 | High-like |
124 | R4reg: moderate -> low | 486 | 27.6 / 61.9 / 57.2 | better than Moderate |
125 | R4F4: low -> unknown | 2,847 | 13.1 / 19.8 / 83.2 | in between |
126
127 - R4's only clean move is Low -> Unknown (429 rows behave like Unknown: pay -11.7pp vs Low stayers).
128 - R4reg moderate -> low (486 rows) beats the Moderate stayers by +9.4pp cure and +17.4pp pay: the regularity
129   requirement demotes good rows. R4cash does the same for cash (219 rows, pay +15.5pp vs Moderate stayers).
130 - R4F4 sends 2,847 rows to Unknown with cure 13.1%, above Low (10.7%) and +5.4pp above R3 Unknown.
131
132 ### A6 - effect on today's A1 (latest month)
133
134 17 of 8,382 rows that are not Unknown today (0.2%) leave Unknown only because their CASA activity is non-evidence.
135 Largest lane combination: `OUTWARD REMITTANCE 120` to the customer's own account elsewhere (WM `self`), 33,785
136 legs / 3,736 CIFs / AED 76.8M, fewer than 10 rows moved. Proposal only, no code change: route these to a
137 non-customer lane or give `casa_active` an allow-list of evidence classes.
138
139 ### Unknown - B0 (reason code)
140
141 Unknown rows, latest month: 10,055 (R3), 10,300 (R4).
142
143 | data situation | rows (share) | cure | pay | roll |
144 |---|---|---|---|---|
145 | CASA held, no leg in W | 5,615 (55.8%) | 6.8 | 17.2 | 89.0 |
146 | CASA legs only in non-evidence classes | 533 (5.3%) | 7.7 | 18.7 | 89.4 |
147 | no CASA account with us | 3,907 (38.9%) | 8.4 | 21.8 | 86.0 |
148
149 Against "no CASA account" (standardised): CASA held, no leg: cure -0.3pp [-1.0, 0.5], pay -2.6pp [-3.9, -1.2],
150 roll +1.5pp [0.4, 2.6]; non-evidence only: pay -3.5pp [-6.3, -0.7], roll +3.7pp [1.5, 5.9]. The gaps are small and
151 inside a 4.6pp range of pay_any_3; a reason code would be descriptive only, not an ability signal.
152
153 ### Unknown - B1 (direct evidence)
154
155 | candidate | reach in Unknown | strong | strong vs none (cure / pay / roll, pp) |
156 |---|---|---|---|
157 | x_aecb | 1,471 (14.6%) | 228 (2.3%) | -3.7 / -12.9 / +6.5 |
158 | x_alert | 6,789 (67.5%) | 2,699 (26.8%) | +0.1 / -0.5 / +0.1 (not significant) |
159 | x_aum | 9,443 (93.9%) | 0 | <10 rows |
160 | x_cardspend | 586 (5.8%) | 0 | <10 rows |
161 | x_joint | <10 | 0 | <10 rows |
162
163 **No F5 proposals.** `x_aecb` strong (clean conduct, pull <= 12 months old) is the opposite of the intended sign:
164 those rows pay less. My guess, not tested: a recent pull marks a recent borrower who defaulted early. The AECB pull
165 is application-time, so it describes the past. `x_alert` "some" is better than none (cure +2.9pp, pay +5.6pp, roll
166 -5.0pp) but "strong" is not, so it is not a monotone signal.
167
168 ### Unknown - B2 (inference), 60-180
169
170 Shift diagnosis, Unknown vs scored rows: AUC 0.733; 88.2% of Unknown rows lie inside the scored rows' propensity
171 support. Family AUCs on holdout: F1 0.70, F2 0.68, F3 0.72, F4 0.93. The F4 value is probably driven by holdings
172 features (`ph_td`, `ph_cc`, `ph_loans`) that also define the family; not checked.
173
174 Approaches that pass all five criteria (temporal test pool; pay gap = upper group minus lower group):
175
176 | approach | abstention | pay gap [95% CI] | coverage |
177 |---|---|---|---|
178 | FamLR | 90% conformal | +5.5 [3.2, 7.7] | 71% |
179 | FamGBM | 80% conformal | +8.4 [6.6, 10.3] | 99% |
180 | FamGBM | 90% conformal | +9.1 [6.6, 11.6] | 75% |
181 | FamGBM | none | +9.9 [6.7, 13.2] | 100% |
182 | FamGBM+IW | 80% conformal | +8.2 [6.3, 10.1] | 100% |
183 | FamGBM+IW | none | +9.5 [6.4, 12.6] | 100% |
184
185 - Not usable: LR-ordinal (every setting; groups under 10 rows), kNN, FamLR at 80% and none, FamGBM+IW at 90%.
186   For the last three, C1 fails although the listed gaps look significant; the file does not say which part of C1
187   failed.
188 - Estimated mix of latest-month Unknown, FamGBM: no abstention moderate 56%, low 37%, high 7%; 90% conformal
189   not_high 57%, abstain 26%, not_low 12%, low 4%, high 0%. Most sets are "not high", which carries little.
190 - Ceiling diagnostic (gradient boosting for pay_any_3 inside Unknown cohort rows, 36,430): AUC 0.651 for DPD band
191   + product, 0.758 full, gain +0.107 [0.099, 0.116] - signal present.
192 - Absolute pay_any_3 per estimated group is NOT IN RESULTS. Observed Unknown pay is 19.0% against 42.2% for real
193   Moderate, so "moderate" for 56% of Unknown should not be read as a level: only the ordering is validated.
194 - Feature set B (application-time affordability): none available at this model_id.
195
196 ## rl_60_180
197
198 ### Cheque question
199
200 | stem (credit side) | legs | AED | class | mirrored in 3 days |
201 |---|---|---|---|---|
202 | CHQ NO INSUFFICIENT | 470 + 14 | 160.5M + 4.9M | reversal_return / unplaced | 100.0% |
203 | CHQ RTN INSUFFICIENT | 263 + 10 | 95.6M + 3.0M | reversal_return / unplaced | 100.0% |
204
205 Round 2 counted F2 AED 264.0M and F3 AED 0.0M from cheque stems. As in CC, every cheque leg has an opposite
206 same-day partner (debit `CHQ NO` 501 legs, AED 174.6M, 100% paired).
207
208 ### Labels and the flow dictionary
209
210 - Salary-flag join 96.7% (13,583 keys, 13,134 found), 1.00 legs per key: reliable.
211 - Dictionary: 102 combinations with >= 50 CIFs (873,657 legs, AED 2,251M) plus 2 stem rules; 309 smaller
212   combinations (25,409 legs, AED 316M) folded into `unplaced`.
213 - WM `self` on non-wash legs: 62,523 legs / AED 239.7M; our wash lane without a WM `self` label: 28,999 legs /
214   AED 121.2M. WM external-loan payments: 2,722 CIF-months, we see a `debt_elsewhere` debit in 81 (3.0%).
215
216 | class | F2 AED (share) | F3 AED (share) |
217 |---|---|---|
218 | third_party_in | 192.7M (29.6%) | - |
219 | cash_in | 61.2M (9.4%) | - |
220 | reversal_return | 256.1M (39.4%) | 0.2M |
221 | unplaced | 140.6M (21.6%) | 59.6M (16.0%) |
222 | chosen_spend | - | 280.0M (75.4%) |
223 | own_transfer | - | 23.7M (6.4%) |
224 | bank_initiated | - | 7.6M (2.0%) |
225 | debt_elsewhere | - | 0.3M (0.1%) |
226 | total | 650.5M | 371.2M |
227
228 R4 keeps F2 AED 246.8M (37.9%) and F3 AED 278.5M (75.0%). In RL, round 2's F2 was 39.4% reversal / return flows.
229 Outcome lift in RL is weaker and mixed: `CASH DEPOSIT` pay +14.2pp but cure -3.0pp (interval includes 0); salary
230 `INWARD REMITTANCE 507` shows no significant lift (cure -3.1pp, pay +2.3pp).
231
232 ### R4 variants - state mix, latest month (3,985 rows)
233
234 | variant | high | moderate | low | unknown |
235 |---|---|---|---|---|
236 | R3 | 48 (1.2%) | 408 (10.2%) | 2,159 (54.2%) | 1,370 (34.4%) |
237 | R4 | 39 (1.0%) | 394 (9.9%) | 2,088 (52.4%) | 1,464 (36.7%) |
238 | R4cash | 37 (0.9%) | 382 (9.6%) | 2,102 (52.7%) | 1,464 (36.7%) |
239 | R4debt | 39 (1.0%) | 394 (9.9%) | 2,088 (52.4%) | 1,464 (36.7%) |
240 | R4reg | 28 (0.7%) | 357 (9.0%) | 2,136 (53.6%) | 1,464 (36.7%) |
241 | R4F4 | 39 (1.0%) | 394 (9.9%) | 1,645 (41.3%) | 1,907 (47.9%) |
242
243 R3 -> R4: 22 Moderate -> Low, 94 Low -> Unknown, 9 High rows move down (cells under 10). Strong F2 rows resting on
244 one leg: 75.9% (R3), 83.3% (R4), 68.4% (R4reg). R4 Unknown by loan type: Auto 39.2%, Personal 39.5%, Personal
245 Cash 30.8% (R3: 38.5%, 35.9%, 28.1%).
246
247 ### Separation (cohort Jan-May 2026, 12,512 rows)
248
249 | state | R3 rows | R3 cure / pay / roll | R4 rows | R4 cure / pay / roll |
250 |---|---|---|---|---|
251 | high | 163 | 19.7 / 83.7 / 48.3 | 117 | 14.2 / 83.0 / 51.9 |
252 | moderate | 1,564 | 16.2 / 68.3 / 67.2 | 1,507 | 16.3 / 68.6 / 66.7 |
253 | low | 6,669 | 9.6 / 43.0 / 83.0 | 6,538 | 10.0 / 44.0 / 82.3 |
254 | unknown | 4,116 | 8.6 / 35.2 / 85.8 | 4,350 | 8.3 / 34.8 / 86.2 |
255
256 R3 orders all three outcomes. Every R4 variant fails the cure_3 order at High (14.2% against 16.3% at Moderate).
257
258 | variant | High-Mod cure | High-Mod pay | High-Mod roll |
259 |---|---|---|---|
260 | R3 | +2.1 [-9.1, 13.3] | +13.8 [6.9, 20.8] | -17.4 [-28.2, -6.5] |
261 | R4 | -4.6 [-12.0, 2.8] | +12.0 [4.3, 19.7] | -12.3 [-23.5, -1.1] |
262 | R4cash | -3.3 [-11.4, 4.8] | +13.1 [4.9, 21.4] | -12.7 [-24.8, -0.5] |
263 | R4reg | -3.1 [-13.0, 6.9] | +14.1 [4.5, 23.7] | -6.7 [-19.6, 6.2] |
264 | R4F4 | -4.6 [-12.0, 2.8] | +12.0 [4.3, 19.7] | -12.3 [-23.5, -1.1] |
265
266 Moderate-Low is stable across variants (cure +5.9 to +6.6pp, pay +22.5 to +25.2pp, roll -15.2 to -15.7pp). High
267 holds only 63-147 rows with outcomes, so no High-vs-Moderate claim on cure_3 is supportable either way. R4reg's
268 roll gap (-6.7pp) is no longer significant.
269
270 ### Moved rows
271
272 Reference, R3 states: high 19.7 / 83.7 / 48.3; moderate 16.2 / 68.3 / 67.2; low 9.6 / 43.0 / 83.0; unknown
273 8.6 / 35.2 / 85.8 (cure / pay / roll, %).
274
275 | variant: move | rows | cure / pay / roll | reading |
276 |---|---|---|---|
277 | R4: moderate -> low | 76 | 13.4 / 70.1 / 70.1 | Moderate-like |
278 | R4: low -> unknown | 231 | 2.7 / 28.3 / 93.4 | Unknown-like |
279 | R4cash: moderate -> low | 143 | 18.9 / 75.6 / 63.8 | better than Moderate |
280 | R4reg: high -> moderate | 67 | 12.5 / 81.2 / 45.3 | High-like |
281 | R4reg: moderate -> low | 235 | 15.2 / 79.6 / 64.0 | better than Moderate |
282 | R4F4: low -> unknown | 1,478 | 7.3 / 33.6 / 87.3 | Unknown-like |
283
284 R4 high -> low (24 rows, 20 with outcome) shows an interval of exactly [55.0, 55.0]: it is a handful of accounts and
285 is not interpretable. R4reg moderate -> low beats Moderate stayers by +11.6pp pay [3.7, 19.5]. In RL the R4F4 move
286 looks Unknown-like (pay -0.8pp vs R3 Unknown [-4.9, 3.2]), unlike CC.
287
288 ### A6 - effect on today's A1
289
290 14 of 2,148 rows that are not Unknown today (0.7%) leave Unknown only because of non-evidence legs. Largest
291 combination: `OUTWARD REMITTANCE 120` own account elsewhere, 9,688 legs / 1,073 CIFs / AED 30.2M, under 10 rows.
292
293 ### Unknown - B0 (reason code)
294
295 Unknown rows: 1,370 (R3), 1,464 (R4).
296
297 | data situation | rows (share) | cure | pay | roll |
298 |---|---|---|---|---|
299 | CASA held, no leg in W | 744 (54.3%) | 4.9 | 30.4 | 90.5 |
300 | CASA legs only in non-evidence classes | 250 (18.2%) | 4.7 | 28.0 | 90.6 |
301 | no CASA account with us | 376 (27.4%) | 21.1 | 52.5 | 70.4 |
302
303 Against "no CASA account" (standardised): CASA held -13.1pp cure, -14.4pp pay, +15.5pp roll; non-evidence only
304 -16.8pp, -25.4pp, +20.8pp (all intervals exclude 0). But 302 of the 376 no-CASA rows are Auto. Within Auto the
305 pay values are 59.6% [51.6, 67.5] (no CASA), 52.2% [46.3, 58.2] (CASA, no leg), 42.9% [27.7, 58.0] (non-evidence
306 only): intervals overlap. Within Personal they are 23.9% (n=155), 23.3%, 22.6%. The gaps are standardised for DPD
307 band only, not product, so the reason code mostly restates product mix.
308
309 ### Unknown - B1 and B2
310
311 | candidate | reach in Unknown | strong | strong vs none (cure / pay / roll, pp) |
312 |---|---|---|---|
313 | x_aecb | 997 (72.8%) | 143 (10.4%) | -2.2 / -22.5 / +7.5 |
314 | x_alert | 860 (62.8%) | 290 (21.2%) | -2.5 / -4.7 / +2.1 (not significant) |
315 | x_aum, x_joint | 82.0%, <10 | 0 | <10 rows |
316
317 **No F5 proposals.** `x_aecb` strong again carries the wrong sign (pay -22.5pp [-28.0, -16.9]) and overlaps A4
318 (Cramér's V 0.42). **B2 did not run** (`LinAlgError('Singular matrix')`): no RL inference result, NOT IN RESULTS.
319 No RL months-on-book / EMI-ratio source was read.
320
321 ## Verdict
322
323 | item | verdict |
324 |---|---|
325 | V0 / R0 checks | PASS in both |
326 | Cheques as income | confirmed: AED 186.1M (CC), 264.0M (RL) in F2, each leg mirrored |
327 | R4 (classes + netting) | CC: no loss of separation. RL: High too small to judge |
328 | R4cash | not supported: demotes CC 190 + 219 and RL 143 rows that perform at or above their state |
329 | R4debt | irrelevant: states identical to R4 (AED 0.7M / 0.2M) |
330 | R4reg | not supported: demotes 486 CC / 235 RL rows that beat Moderate |
331 | R4F4 | not supported: CC rows are in between, 2,847 moved |
332 | Flow dictionary | usable as a classification table; WM `self` vs wash needs a decision |
333 | A6 gate change | marginal (0.2% CC, 0.7% RL); low priority |
334 | B0 reason code | CC: no. RL: product mix, not ability |
335 | B1 F5 | none qualify |
336 | B2 inference | CC: passes; RL: not run. Needs GRR decision (M1) |
337
338 ## Not in results / open
339
340 - `cc_180_plus` and `rl_180_plus` (all sections); RL B2; absolute per-group rates for B2; the A3 breakdown
341   (`crx_cc_a3_payment_credibility`, `crx_rl_a3_payment_credibility` lack `a3_state_v1`, so it was skipped).
342 - B2 is a risk-model-style predictor (it uses `log_anchor`, bureau and holdings features), so it should be a
343   separate column and not merged into the evidence states. It is not for the A1 rule unless GRR agrees.
344 - Re-run RL B2 after fixing the singular matrix (likely collinear or constant columns in the RL feature set; not
345   investigated).
346
````

## Notes on specific spots
- **Does not tie out, as printed:** CC R3 -> R4 move counts (line 85) vs the state tables (lines 78-79). High 292 - 12 = 280 but R4 shows 279; Moderate 2,926 + 12 - 22 = 2,916 but R4 shows 2,913; Low 6,019 + 22 - 242 = 5,799 but R4 shows 5,800; Unknown 10,055 + 242 = 10,297 but R4 shows 10,300 (the table implies 245 Low -> Unknown). So about 3 rows of movement are not in the line-85 list (probably small cells). RL line 243 (22 + 94 + 9) vs lines 236-237: Unknown 1,370 + 94 = 1,464 matches; High 48 - 9 = 39 matches. Copied as shown; check against the real file.
- Total rows printed as `1,380.9M` (line 64) vs the sum of the F2 cells 1,380.8M (643.0 + 202.4 + 185.4 + 350.0), and `908.6M` vs the F3 cells 908.8M (0.2 + 14.1 + 794.1 + 66.8 + 32.6 + 1.0); `371.2M` (line 226) vs the RL F3 cells 371.4M. Rounding, as printed. RL F2 cells 192.7 + 61.2 + 256.1 + 140.6 = 650.6M vs 650.5M.
- Sum checks that pass: all six CC state-mix rows add to 19,292 and all six RL rows to 3,985 (lines 78-83, 236-241); cohort tables add to 74,256 (CC R3 and R4) and 12,512 (RL R3 and R4) (lines 95-98, 251-254); Unknown B0 splits add to 10,055 (CC), 1,370 (RL) (lines 145-147, 299-301); 8,382 = 19,292 - 10,910 and 2,148 = 3,985 - 1,837 (V0 Unknown counts in handoff 50); line 202-203 AED 160.5 + 4.9 + 95.6 + 3.0 = 264.0M (= line 205); line 31-32 107.6 + 77.8 = 185.4M (vs 186.1M counted in lines 14, 34: the 0.7M difference is not explained, as printed); percentages: 94.2% = 35,746 / 37,934, 96.7% = 13,134 / 13,583, 3.8% = 354 / 9,427, 3.0% = 81 / 2,722, 60.7% = 837.9 / 1,380.9, 87.0% = 790.1 / 908.6, 37.9% = 246.8 / 650.5, 75.0% = 278.5 / 371.2.
- Line 16 vs 102-103: "CC gaps stay within 0.4pp of R3" holds for R4 (0.2 / 0.4 / 0.2 pp) but not for R4cash roll (-23.2 vs -22.3, 0.9pp); the line refers to R4, as I read it.
- Line 22 vs 134 and 290: the headline gives 17 CC rows (0.2%) and 14 RL rows (0.7%), matching the A6 sections.
- Line 44-45: "2,820,933 legs, AED 5,697M" and "20,342 legs, AED 584M" are as shown; the flow-dictionary table itself is not in this file ("I did not check it line by line", line 45-46, is the file's wording).
- Lines 203-204 and 202: the `+` cells (`470 + 14`, `160.5M + 4.9M`, `reversal_return / unplaced`) are as printed.
- Line 284: "interval of exactly [55.0, 55.0]" is as printed; the move `R4 high -> low` has no row in the table at lines 275-282.
- Line 315: `82.0%, <10` in the "reach in Unknown" cell is as printed (two values for two candidates).
- Line 336: "M1" is the file's own label ("Needs GRR decision (M1)"); it is not explained in the visible lines.
- Lines 3 / 196 / 340-341 and the file names with `rl`: see the context note about `r1` vs `rl` in this font.
- Photo notes: photo 1 is slanted and slightly blurred; photos 3-7 are blurry at the right edge, so long lines (e.g. 165-166, 303-307) are read from the wrapped text.
- OCR-risk digits: all counts and percentages in the tables (lines 29-32, 54-64, 76-83, 93-107, 116-125, 143-147, 155-161, 176-183, 200-203, 216-226, 234-264, 275-282, 297-301, 311-315), the AED figures, the interval brackets, and the AUC values in lines 170-172 and 190-191.
