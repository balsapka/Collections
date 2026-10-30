# Handoff 24: `tmp_validation/a1_b09_rl_check_run_summary_2026-10-30.md` (10 photos), 2026-10-30

## Context for Claude Code
- Source: 10 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest), taken 2026-10-30 ~17:04 Dubai. Tabs: `pipeline_registry.py`, `a1_b09_rl_check_run_summary_2026-10-30.md` (U = untracked, active). Branch `.../persona_redesign_b01*`.
- Title: "A1 ability - bundle 09 check run summary (RL)". The RL (`rl_60_180`) counterpart of handoff 23 (CC b09). Same structure, source lines 1-493. Follows handoffs 1-23.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run log.
- The photos overlap and are merged into source lines 1-493. Photo-to-line map (in the order sent): P1 = 385-444; P2 = 427-493; P3 = 331-397; P4 = 288-346; P5 = 96, 243-299; P6 = 192-251; P7 = 144-204; P8 = 100-157; P9 = 42-106; P10 = 1-59.
- Where a table in one photo is cut off, the rows come from the overlapping photo. Tables are as in the editor.

---

## `a1_b09_rl_check_run_summary_2026-10-30.md` (lines 1-493)

````
1   # A1 ability - bundle 09 check run summary (RL)
2
3   - Command: `kedro run --env=dev --pipeline=crx_rl_a1_ability_b09_check`
4   - Run date: 2026-10-30, started 12:42, completed successfully in 605.9 sec (11 of 11 tasks)
5   - Model config: `model_id=rl_60_180`, `dlq_min=3`, `dlq_max=6`, `collateral_codes=['WO','SK']`,
6     `target_horizon_months=1` (source `globals_dev.yml`)
7   - Spark hook env: medium
8   - Warnings (non-blocking): native-hadoop library not loadable; SparkUI port 4040 busy (used 4041);
9     HiveConf unknown-name warnings; one YARN executor (executor 8) removed because of a bad node
10    (`User balzsv not found`, exit status -1000).
11  - Evaluation month: 2026-08-31, base = 3,985 accounts, 3,608 CIFs
12
13  ## Nodes run
14
15  | # | Node | Output |
16  |---|------|--------|
17  | 1 | build_crx_rl_obs_base | crx_rl_obs_base |
18  | 2 | build_crx_rl_a1_distress_signals | crx_rl_a1_distress_signals |
19  | 3 | build_crx_rl_a1_eosb_signals | crx_rl_a1_eosb_signals |
20  | 4 | build_crx_rl_a1_income_signals | crx_rl_a1_income_signals |
21  | 5 | build_crx_rl_a1_liquidity_anchor | crx_rl_a1_liquidity_anchor |
22  | 6 | build_crx_rl_a1_liquidity_signals | crx_rl_a1_liquidity_signals |
23  | 7 | build_crx_rl_a1_ability | crx_rl_a1_ability_b09_check |
24  | 8 | compare_crx_rl_a1_b09 | (log only) |
25  | 9 | describe_crx_rl_a1_b09_report | (log only) |
26  | 10 | describe_crx_rl_a1_b09_sources | (log only) |
27  | 11 | explain_crx_rl_a1_b09_aecb | (log only) |
28
29  ## 1. a1_state, month 2026-08-31 (n=3,985)
30
31  | a1_state | n | % |
32  |---|---:|---:|
33  | high | 11 | 0.3 |
34  | low | 1,837 | 46.1 |
35  | moderate | 358 | 9.0 |
36  | unknown | 1,779 | 44.6 |
37
38  ## 2. Compare new vs old (`compare_a1_outputs`)
39
40  Month 2026-08-31: new 3,985 rows, old 3,985, new only 0, old only 0.
41
42  ### By product x a1_state
43
44  | product | a1_state | n | % |
45  |---|---|---:|---:|
46  | Auto | high | 2 | 0.1 |
47  | Auto | low | 636 | 16.0 |
48  | Auto | moderate | 124 | 3.1 |
49  | Auto | unknown | 602 | 15.1 |
50  | Personal | high | 6 | 0.2 |
51  | Personal | low | 593 | 14.9 |
52  | Personal | moderate | 100 | 2.5 |
53  | Personal | unknown | 698 | 17.5 |
54  | Personal Cash | high | 3 | 0.1 |
55  | Personal Cash | low | 608 | 15.3 |
56  | Personal Cash | moderate | 134 | 3.4 |
57  | Personal Cash | unknown | 479 | 12.0 |
58
59  ### Old x new a1_state
60
61  | old | new | n | % |
62  |---|---|---:|---:|
63  | high | high | 1 | 0.0 |
64  | low | low | 1,766 | 44.3 |
65  | low | moderate | 297 | 7.5 |
66  | low | unknown | 1,503 | 37.7 |
67  | moderate | high | 10 | 0.3 |
68  | moderate | moderate | 45 | 1.1 |
69  | moderate | unknown | 1 | 0.0 |
70  | unknown | low | 71 | 1.8 |
71  | unknown | moderate | 16 | 0.4 |
72  | unknown | unknown | 275 | 6.9 |
73
74  ### New a1_state share by month (%)
75
76  | month | n | high | moderate | low | unknown |
77  |---|---:|---:|---:|---:|---:|
78  | 2026-01-01 | 2,324 | 0.04 | 12.56 | 46.17 | 41.22 |
79  | 2026-02-01 | 2,213 | 0.09 | 10.94 | 44.24 | 44.74 |
80  | 2026-03-01 | 2,218 | 0.14 | 11.23 | 45.90 | 42.74 |
81  | 2026-04-01 | 2,661 | 0.15 | 11.84 | 47.80 | 40.21 |
82  | 2026-05-01 | 3,096 | 0.10 | 11.53 | 49.10 | 39.28 |
83  | 2026-06-01 | 3,514 | 0.17 | 10.33 | 48.80 | 40.69 |
84  | 2026-07-01 | 3,728 | 0.08 | 9.63 | 47.42 | 42.86 |
85  | 2026-08-01 | 3,985 | 0.28 | 8.98 | 46.10 | 44.64 |
86
87  ### Range over the months (min-max %)
88
89  | state | min | max |
90  |---|---:|---:|
91  | high | 0.04 | 0.28 |
92  | moderate | 8.98 | 12.56 |
93  | low | 44.24 | 49.10 |
94  | unknown | 39.28 | 44.74 |
95
96  ## 3. Report (`describe_a1_report`)
97
98  Base: 3,985 accounts, 3,608 CIFs.
99
100 ### M4 income source in W x income level
101
102 | income source | level | n | % |
103 |---|---|---:|---:|
104 | both | stable | 13 | 0.3 |
105 | both | weak | 8 | 0.2 |
106 | bureau_only | stable | 307 | 7.7 |
107 | bureau_only | weak | 231 | 5.8 |
108 | internal_only | stable | 41 | 1.0 |
109 | internal_only | weak | 143 | 3.6 |
110 | neither | none | 3,242 | 81.4 |
111
112 ### M5 CASA relationship x a1_state
113
114 | CASA | a1_state | n | % |
115 |---|---|---:|---:|
116 | active_casa | high | 11 | 0.3 |
117 | active_casa | low | 1,154 | 29.0 |
118 | active_casa | moderate | 167 | 4.2 |
119 | dormant_casa | low | 683 | 17.1 |
120 | dormant_casa | moderate | 191 | 4.8 |
121 | dormant_casa | unknown | 1,779 | 44.6 |
122
123 ### M6 max monthly CASA balance in W x covers max(3000, anchor)
124
125 | max balance | covers | n | % |
126 |---|---|---:|---:|
127 | 1000-3000 | False | 193 | 4.8 |
128 | <1000 | False | 1,410 | 35.4 |
129 | >=3,000 | False | 53 | 1.3 |
130 | >=3,000 | True | 105 | 2.6 |
131 | none | False | 2,224 | 55.8 |
132
133 ### M6 external card payment in W x liquidity level
134
135 | ext card payment | liquidity | n | % |
136 |---|---|---:|---:|
137 | False | adequate | 46 | 1.2 |
138 | False | none | 3,609 | 90.6 |
139 | False | weak | 291 | 7.3 |
140 | True | adequate | 11 | 0.3 |
141 | True | none | 14 | 0.4 |
142 | True | weak | 14 | 0.4 |
143
144 ### M6 liquidity level
145
146 | level | n | % |
147 |---|---:|---:|
148 | adequate | 57 | 1.4 |
149 | none | 3,623 | 90.9 |
150 | weak | 305 | 7.7 |
151
152 ### M7 unknown reason
153
154 | reason | n | % |
155 |---|---:|---:|
156 | dormant_casa | 1,779 | 100.0 |
157
158 ### M8 low reason
159
160 | reason | n | % |
161 |---|---:|---:|
162 | 0pt_active_casa | 656 | 35.7 |
163 | 0pt_distress | 539 | 29.3 |
164 | 1pt | 559 | 30.4 |
165 | 2-3pt_distress | 83 | 4.5 |
166
167 ### M9 moderate / high: state x income x liquidity x distress
168
169 | state | income | liquidity | distress | n | % |
170 |---|---|---|---:|---:|---:|
171 | high | stable | adequate | 0 | 11 | 3.0 |
172 | moderate | none | adequate | 0 | 23 | 6.2 |
173 | moderate | stable | adequate | 1 | 3 | 0.8 |
174 | moderate | stable | none | 0 | 271 | 73.4 |
175 | moderate | stable | weak | 0 | 19 | 5.1 |
176 | moderate | weak | adequate | 0 | 3 | 0.8 |
177 | moderate | weak | weak | 0 | 39 | 10.6 |
178
179 ### M10 distress parts in W ('' = none)
180
181 | parts | n | % |
182 |---|---:|---:|
183 | (none) | 3,261 | 81.8 |
184 | bureau | 282 | 7.1 |
185 | cheque | 189 | 4.7 |
186 | cheque+bureau | 28 | 0.7 |
187 | cheque+dds | 36 | 0.9 |
188 | cheque+dds+bureau | 1 | 0.0 |
189 | dds | 184 | 4.6 |
190 | dds+bureau | 4 | 0.1 |
191
192 ### M10 distress parts x a1_state
193
194 | parts | a1_state | n | % |
195 |---|---|---:|---:|
196 | bureau | low | 282 | 39.0 |
197 | cheque | low | 189 | 26.1 |
198 | cheque+bureau | low | 28 | 3.9 |
199 | cheque+dds | low | 36 | 5.0 |
200 | cheque+dds+bureau | low | 1 | 0.1 |
201 | dds | low | 181 | 25.0 |
202 | dds | moderate | 3 | 0.4 |
203 | dds+bureau | low | 4 | 0.6 |
204
205 ### M11 EOSB result in W x a1_state
206
207 | EOSB result | a1_state | n | % |
208 |---|---|---:|---:|
209 | 0 | high | 11 | 0.3 |
210 | 0 | low | 1,832 | 46.0 |
211 | 0 | moderate | 356 | 8.9 |
212 | 0 | unknown | 1,774 | 44.5 |
213 | 1 | low | 5 | 0.1 |
214 | 1 | moderate | 2 | 0.1 |
215 | 1 | unknown | 5 | 0.1 |
216
217 ### M11 EOSB in W x liquidity level
218
219 | liquidity | n | % |
220 |---|---:|---:|
221 | none | 6 | 50.0 |
222 | weak | 6 | 50.0 |
223
224 ### M11 anchor
225
226 Anchor present / p10 p50 p90: [1193.0, 2389.0, 8018.0]
227
228 | anchor present | n | % |
229 |---|---:|---:|
230 | True | 3,985 | 100.0 |
231
232 ### M11 anchor raises the income x CASA x card-payment floor
233
234 | col 1 | col 2 | col 3 | n | % |
235 |---|---|---|---:|---:|
236 | False | False | False | 26 | 0.7 |
237 | False | False | True | 712 | 17.9 |
238 | True | False | True | 1,724 | 43.3 |
239 | True | True | True | 1,523 | 38.2 |
240
241 (The log does not label the three boolean columns.)
242
243 ### By product: loan_type x a1_state, x unknown reason, x low reason
244
245 | product | a1_state / reason | n | % |
246 |---|---|---:|---:|
247 | Auto | high | 2 | 0.1 |
248 | Auto | low | 636 | 16.0 |
249 | Auto | moderate | 124 | 3.1 |
250 | Auto | unknown | 602 | 15.1 |
251 | Personal | high | 6 | 0.2 |
252 | Personal | low | 593 | 14.9 |
253 | Personal | moderate | 100 | 2.5 |
254 | Personal | unknown | 698 | 17.5 |
255 | Personal Cash | high | 3 | 0.1 |
256 | Personal Cash | low | 608 | 15.3 |
257 | Personal Cash | moderate | 134 | 3.4 |
258 | Personal Cash | unknown | 479 | 12.0 |
259 | Auto | dormant_casa | 602 | 33.8 |
260 | Personal | dormant_casa | 698 | 39.2 |
261 | Personal Cash | dormant_casa | 479 | 26.9 |
262 | Auto | 0pt_active_casa | 150 | 8.2 |
263 | Auto | 0pt_distress | 335 | 18.2 |
264 | Auto | 1pt | 120 | 6.5 |
265 | Auto | 2-3pt_distress | 31 | 1.7 |
266 | Personal | 0pt_active_casa | 262 | 14.3 |
267 | Personal | 0pt_distress | 83 | 4.5 |
268 | Personal | 1pt | 235 | 12.8 |
269 | Personal | 2-3pt_distress | 13 | 0.7 |
270 | Personal Cash | 0pt_active_casa | 244 | 13.3 |
271 | Personal Cash | 0pt_distress | 121 | 6.6 |
272 | Personal Cash | 1pt | 204 | 11.1 |
273 | Personal Cash | 2-3pt_distress | 39 | 2.1 |
274
275 ## 4. Sources (`describe_a1_sources`)
276
277 Base (latest month): 3,985 accounts, 3,608 CIFs.
278
279 ### Source depth (month_end)
280
281 | source | all CIFs | base CIFs from |
282 |---|---|---|
283 | feat_cif_internal_salary_monthly | 2024-09-30 .. 2026-08-31 | 2024-09-30 |
284 | feat_cif_bureau_salary_monthly | 2022-10-31 .. 2026-08-31 | 2022-11-30 |
285 | feat_cif_casa_balance_monthly | 2025-02-28 .. 2026-09-30 | 2025-02-28 |
286 | feat_cif_casa_activity_monthly | 2025-02-28 .. 2026-10-31 | 2025-02-28 |
287
288 ### M2 internal salary (>= 1000) history
289
290 | history | n | % |
291 |---|---:|---:|
292 | in_W | 205 | 5.1 |
293 | last_m13-24 | 528 | 13.2 |
294 | last_m4-6 | 1,146 | 28.8 |
295 | last_m7-12 | 888 | 22.3 |
296 | never | 1,218 | 30.6 |
297
298 ### M2 internal salary history x a1_state
299
300 | history | a1_state | n | % |
301 |---|---|---:|---:|
302 | in_W | high | 10 | 0.3 |
303 | in_W | low | 124 | 3.1 |
304 | in_W | moderate | 71 | 1.8 |
305 | last_m13-24 | high | 1 | 0.0 |
306 | last_m13-24 | low | 250 | 6.3 |
307 | last_m13-24 | moderate | 62 | 1.6 |
308 | last_m13-24 | unknown | 215 | 5.4 |
309 | last_m4-6 | low | 504 | 12.6 |
310 | last_m4-6 | moderate | 43 | 1.1 |
311 | last_m4-6 | unknown | 599 | 15.0 |
312 | last_m7-12 | low | 399 | 10.0 |
313 | last_m7-12 | moderate | 70 | 1.8 |
314 | last_m7-12 | unknown | 419 | 10.5 |
315 | never | low | 560 | 14.1 |
316 | never | moderate | 112 | 2.8 |
317 | never | unknown | 546 | 13.7 |
318
319 ### M3 AECB salary (>= 1000) by last pull month, before the carry
320
321 | last pull | n | % |
322 |---|---:|---:|
323 | alert_never_salary | 2,310 | 58.0 |
324 | in_W | 461 | 11.6 |
325 | last_m13-24 | 274 | 6.9 |
326 | last_m25+ | 285 | 7.2 |
327 | last_m4-6 | 262 | 6.6 |
328 | last_m7-12 | 230 | 5.8 |
329 | no_alert_row | 163 | 4.1 |
330
331 ### M3 internal salary (rows) x AECB salary history (columns), n (%)
332
333 | internal \ AECB | alert_never_salary | in_W | last_m13-24 | last_m25+ |
334 |---|---|---|---|---|
335 | in_W | 142 (3.6) | 21 (0.5) | 10 (0.3) | 19 (0.5) |
336 | last_m13-24 | 258 (6.5) | 91 (2.3) | 36 (0.9) | 40 (1.0) |
337 | last_m4-6 | 737 (18.5) | 93 (2.3) | 81 (2.0) | 97 (2.4) |
338 | last_m7-12 | 498 (12.5) | 108 (2.7) | 59 (1.5) | 77 (1.9) |
339 | never | 675 (16.9) | 148 (3.7) | 88 (2.2) | 52 (1.3) |
340
341 | internal \ AECB | last_m4-6 | last_m7-12 | no_alert_row |
342 |---|---|---|---|
343 | in_W | 1 (0.0) | 4 (0.1) | 8 (0.2) |
344 | last_m13-24 | 49 (1.2) | 40 (1.0) | 14 (0.4) |
345 | last_m4-6 | 47 (1.2) | 42 (1.1) | 49 (1.2) |
346 | last_m7-12 | 62 (1.6) | 42 (1.1) | 42 (1.1) |
347 | never | 103 (2.6) | 102 (2.6) | 50 (1.3) |
348
349 ### CASA legs of base CIFs in W (2026-06-01 .. 2026-08-31) by lane
350
351 | lane | legs | CIFs |
352 |---|---:|---:|
353 | ambiguous | 3,789 | 1,390 |
354 | card_payment | 479 | 196 |
355 | card_spend | 7,359 | 294 |
356 | economic | 6,570 | 1,178 |
357 | fee_interest | 964 | 391 |
358 | group_internal | 386 | 91 |
359 | own_loan | 3,163 | 1,207 |
360 | refund | 136 | 73 |
361 | reversal | 112 | 44 |
362 | signal | 23,404 | 388 |
363 | unclassified | 2 | 2 |
364 | wash | 6,163 | 2,379 |
365
366 ### Top unclassified / ambiguous (lane, tran_type, reason)
367
368 | lane | tran_type | reason | n |
369 |---|---|---|---:|
370 | ambiguous | MISCELLANEOUS | None | 3,788 |
371 | unclassified | POS TRANSACTIONS | None | 2 |
372 | ambiguous | MC/DD-ISSUE | None | 1 |
373
374 ### WM vs FTR, base CIFs, last 12 months
375
376 | WM row | WM positive | FTR leg | FTR customer leg | n | % |
377 |---|---|---|---|---:|---:|
378 | False | False | True | False | 76 | 2.1 |
379 | False | False | True | True | 165 | 4.6 |
380 | True | False | True | False | 318 | 8.8 |
381 | True | False | True | True | 139 | 3.9 |
382 | True | True | True | False | 56 | 1.6 |
383 | True | True | True | True | 2,854 | 79.1 |
384
385 ## 5. AECB explain (`explain_a1_aecb`)
386
387 Rows 3,985; last step vs the output: 0 states, 0 income levels differ.
388
389 ### Rows per state at each step
390
391 | step | high | moderate | low | unknown |
392 |---|---:|---:|---:|---:|
393 | s0_no_aecb | 9 | 89 | 1,811 | 2,076 |
394 | s1_pull_months | 11 | 272 | 1,866 | 1,836 |
395 | s2_one_month_carry | 11 | 358 | 1,837 | 1,779 |
396
397 ### s0_no_aecb -> s1_pull_months: 310 rows move
398
399 | from | to | n | % |
400 |---|---|---:|---:|
401 | low | moderate | 68 | 21.9 |
402 | moderate | high | 2 | 0.6 |
403 | unknown | low | 123 | 39.7 |
404 | unknown | moderate | 117 | 37.7 |
405
406 ### s1_pull_months -> s2_one_month_carry: 136 rows move
407
408 | from | to | n | % |
409 |---|---|---:|---:|
410 | low | moderate | 77 | 56.6 |
411 | moderate | low | 2 | 1.5 |
412 | unknown | low | 46 | 33.8 |
413 | unknown | moderate | 11 | 8.1 |
414
415 ### Income source x income level
416
417 | source | level | n | % |
418 |---|---|---:|---:|
419 | both | stable | 13 | 0.3 |
420 | both | weak | 8 | 0.2 |
421 | bureau | stable | 307 | 7.7 |
422 | bureau | weak | 231 | 5.8 |
423 | internal | stable | 41 | 1.0 |
424 | internal | weak | 143 | 3.6 |
425 | none | none | 3,242 | 81.4 |
426
427 ### Income source x a1_state
428
429 | source | a1_state | n | % |
430 |---|---|---:|---:|
431 | both | high | 1 | 0.0 |
432 | both | low | 10 | 0.3 |
433 | both | moderate | 10 | 0.3 |
434 | bureau | high | 1 | 0.0 |
435 | bureau | low | 273 | 6.9 |
436 | bureau | moderate | 264 | 6.6 |
437 | internal | high | 9 | 0.2 |
438 | internal | low | 114 | 2.9 |
439 | internal | moderate | 61 | 1.5 |
440 | none | low | 1,440 | 36.1 |
441 | none | moderate | 23 | 0.6 |
442 | none | unknown | 1,779 | 44.6 |
443
444 ### AECB months in W (with the carry) x income level
445
446 | AECB months | level | n | % |
447 |---:|---|---:|---:|
448 | 0 | none | 3,242 | 81.4 |
449 | 0 | stable | 41 | 1.0 |
450 | 0 | weak | 143 | 3.6 |
451 | 1 | stable | 37 | 0.9 |
452 | 1 | weak | 146 | 3.7 |
453 | 2 | stable | 161 | 4.0 |
454 | 2 | weak | 75 | 1.9 |
455 | 3 | stable | 122 | 3.1 |
456 | 3 | weak | 18 | 0.5 |
457
458 AECB in W, window total passes, the 25% check fails: **86**
459
460 ### Salary stopped x income source x income level
461
462 | source | level | n | % |
463 |---|---|---:|---:|
464 | bureau | stable | 49 | 4.3 |
465 | bureau | weak | 72 | 6.3 |
466 | none | none | 1,025 | 89.4 |
467
468 (Percentages are within the salary-stopped = 1 group, 1,146 rows.)
469
470 ### Salary stopped x a1_state
471
472 | salary stopped | a1_state | n | % |
473 |---:|---|---:|---:|
474 | 0 | high | 11 | 0.3 |
475 | 0 | low | 1,333 | 33.5 |
476 | 0 | moderate | 315 | 7.9 |
477 | 0 | unknown | 1,180 | 29.6 |
478 | 1 | low | 504 | 12.6 |
479 | 1 | moderate | 43 | 1.1 |
480 | 1 | unknown | 599 | 15.0 |
481
482 ## Notes
483
484 - The new a1_state differs from the old (`crx_rl_a1_ability_v2`) output for 1,898 of 3,985 rows
485   (everything off the diagonal in the old x new table): low->unknown 1,503, low->moderate 297,
486   unknown->low 71, unknown->moderate 16, moderate->high 10, moderate->unknown 1.
487 - The "last step vs the output" check in the AECB explain shows the final step (s2_one_month_carry)
488   matches the output exactly.
489 - RL has no `no_casa` relationship: every unknown row is `dormant_casa` (M7 = 100%).
490 - The M3 internal x AECB matrix has seven AECB columns, so it is split into two tables to stay within
491   120 characters per line.
492 - The log was transcribed without any rerun; percentages are as printed by the pipeline.
493
````

## Notes on specific spots
- Checks I ran on the transcription: line 31-36 sums to 3,985 (11+1,837+358+1,779); old x new (lines 63-72) sums to 3,985 and off-diagonal = 1,898 (matches line 484); step rows (lines 393-395) each sum to 3,985; line 397 "310 rows move" = 68+2+123+117; line 406 "136 rows move" = 77+2+46+11; M3 AECB table (lines 323-329) sums to 3,985; salary stopped x a1_state sums to 3,985; WM vs FTR (lines 378-383) sums to 3,608 CIFs; M10 distress parts sum to 3,985 (3,261+282+189+28+36+1+184+4).
- Lines 246-273: the by-product table has 27 data rows in the editor, including the unknown-reason (dormant_casa) rows and the low-reason rows by product.
- Lines 333-347: the M3 matrix is split in two tables as stated in line 490; the first photo showed the first four columns, the second the last three.
- Line 458: `**86**` is bold in the source.
- Line 289-296: M2 history table rows come from P4 and P5; line 291 (header divider) is partly cut in the photos.
- Line 126-131: `<1000` and `>=3,000` as printed.
- Compare with handoff 23 (CC): RL b09 has unknown 44.6%, low 46.1%, moderate 9.0%, high 0.3%. For RL, the old-to-new change is mostly low -> unknown (1,503) and low -> moderate (297).
