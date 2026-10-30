# Handoff 23: `tmp_validation/a1_b09_cc_check_run_summary_2026-10-30.md` (12 photos), 2026-10-30

## Context for Claude Code
- Source: 12 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest), taken 2026-10-30 ~16:33 Dubai. Tabs: `pipeline_registry.py`, `09_a1_alert_salary.md`, `10_a2_180_streak.md`, `a1_b09_cc_check_run_summary_2026-10-30.md` (U = untracked, active). Branch `.../persona_redesign_b01*`. Terminal panel shows "Worked for 16s - done 12:29 PM" (not transcribed).
- Title: "A1 ability - bundle 09 check run summary (CC)". The CC b09 check run of the A1 ability engine with the **alert-salary route** (bureau salary from the AECB alert table, see handoff 19 and bundle `09_a1_alert_salary.md`). Follows handoffs 1-22; it is the b09 successor of the b08 summary in handoff 20. Compare: b08 had unknown 74.2% / low 24.2%; b09 has unknown 56.1% / low 29.7% / moderate 13.9%.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run log.
- The photos overlap and are merged into source lines 1-467. Photo-to-line map (in the order sent): P1 = 1-55; P2 = 122-181; P3 = 81-133; P4 = 37-89; P5 = 169-225; P6 = 275-326; P7 = 257-307; P8 = 209-266; P9 = 311-364; P10 = 421-467; P11 = 381-437; P12 = 346-408.
- Lines 40-55 and 163-181 appear in two photos each and agree. Where a table in the photos is cut off, the missing rows come from the overlapping photo.
- Line 31-35 uses right-aligned markers (`---:`) as printed. Markdown tables are shown as in the editor.
- The Mac link was disconnected at the start of this turn if the write below fails; if the write succeeded, the file is already in the folder.

---

## `a1_b09_cc_check_run_summary_2026-10-30.md` (lines 1-467)

````
1   # A1 ability - bundle 09 check run summary (CC)
2
3   - Command: `kedro run --env=dev --pipeline=crx_cc_a1_ability_b09_check`
4   - Run date: 2026-10-30, started 12:14, completed successfully in 495.5 sec (11 of 11 tasks)
5   - Model config: `model_id=cc_60_180`, `dlq_min=4`, `dlq_max=7`, `collateral_codes=['WO','SK']`,
6     `target_horizon_months=1` (source `globals_dev.yml`)
7   - Spark hook env: medium
8   - Warnings (non-blocking): native-hadoop library not loadable; SparkUI port 4040 busy (used 4041);
9     HiveConf unknown-name warnings; one YARN executor (executor 2) removed because of a bad node
10    (`User balzsv not found`, exit status -1000).
11  - Evaluation month: 2026-08-31, base = 19,292 accounts, 18,731 CIFs
12
13  ## Nodes run
14
15  | # | Node | Output |
16  |---|------|--------|
17  | 1 | build_crx_cc_obs_base | crx_cc_obs_base |
18  | 2 | build_crx_cc_a1_distress_signals | crx_cc_a1_distress_signals |
19  | 3 | build_crx_cc_a1_eosb_signals | crx_cc_a1_eosb_signals |
20  | 4 | build_crx_cc_a1_income_signals | crx_cc_a1_income_signals |
21  | 5 | build_crx_cc_a1_liquidity_anchor | crx_cc_a1_liquidity_anchor |
22  | 6 | build_crx_cc_a1_liquidity_signals | crx_cc_a1_liquidity_signals |
23  | 7 | build_crx_cc_a1_ability | crx_cc_a1_ability_b09_check |
24  | 8 | compare_crx_cc_a1_b09 | (log only) |
25  | 9 | describe_crx_cc_a1_b09_report | (log only) |
26  | 10 | describe_crx_cc_a1_b09_sources | (log only) |
27  | 11 | explain_crx_cc_a1_b09_aecb | (log only) |
28
29  ## 1. a1_state, month 2026-08-31 (n=19,292)
30
31  | a1_state | n | % |
32  |---|---:|---:|
33  | high | 47 | 0.2 |
34  | low | 5,737 | 29.7 |
35  | moderate | 2,689 | 13.9 |
36  | unknown | 10,819 | 56.1 |
37
38  ## 2. Compare new vs old (`compare_a1_outputs`)
39
40  Month 2026-08-31: new 19,292 rows, old 19,292, new only 0, old only 0.
41
42  By product x a1_state: only `all` (same as the table above).
43
44  ### Old x new a1_state
45
46  | old | new | n | % |
47  |---|---|---:|---:|
48  | high | high | 8 | 0.0 |
49  | low | high | 1 | 0.0 |
50  | low | low | 4,371 | 22.7 |
51  | low | moderate | 668 | 3.5 |
52  | low | unknown | 1,944 | 10.1 |
53  | moderate | high | 38 | 0.2 |
54  | moderate | moderate | 166 | 0.9 |
55  | unknown | low | 1,366 | 7.1 |
56  | unknown | moderate | 1,855 | 9.6 |
57  | unknown | unknown | 8,875 | 46.0 |
58
59  ### New a1_state share by month (%)
60
61  | month | n | high | moderate | low | unknown |
62  |---|---:|---:|---:|---:|---:|
63  | 2026-01-01 | 14,664 | 0.43 | 19.19 | 28.48 | 51.90 |
64  | 2026-02-01 | 14,576 | 0.41 | 19.40 | 27.41 | 52.77 |
65  | 2026-03-01 | 14,455 | 0.33 | 18.27 | 28.19 | 53.21 |
66  | 2026-04-01 | 14,671 | 0.31 | 17.84 | 28.23 | 53.62 |
67  | 2026-05-01 | 15,890 | 0.35 | 17.26 | 30.96 | 51.44 |
68  | 2026-06-01 | 16,982 | 0.29 | 16.93 | 31.39 | 51.39 |
69  | 2026-07-01 | 18,397 | 0.29 | 15.08 | 32.44 | 52.19 |
70  | 2026-08-01 | 19,292 | 0.24 | 13.94 | 29.74 | 56.08 |
71
72  ### Range over the months (min-max %)
73
74  | state | min | max |
75  |---|---:|---:|
76  | high | 0.24 | 0.43 |
77  | moderate | 13.94 | 19.40 |
78  | low | 27.41 | 32.44 |
79  | unknown | 51.39 | 56.08 |
80
81  ## 3. Report (`describe_a1_report`)
82
83  Base: 19,292 accounts, 18,731 CIFs.
84
85  ### M4 income source in W x income level
86
87  | income source | level | n | % |
88  |---|---|---:|---:|
89  | both | stable | 26 | 0.1 |
90  | both | weak | 12 | 0.1 |
91  | bureau_only | stable | 2,656 | 13.8 |
92  | bureau_only | weak | 1,807 | 9.4 |
93  | internal_only | stable | 190 | 1.0 |
94  | internal_only | weak | 212 | 1.1 |
95  | neither | none | 14,389 | 74.6 |
96
97  ### M5 CASA relationship x a1_state
98
99  | CASA | a1_state | n | % |
100 |---|---|---:|---:|
101 | active_casa | high | 45 | 0.2 |
102 | active_casa | low | 3,044 | 15.8 |
103 | active_casa | moderate | 542 | 2.8 |
104 | dormant_casa | high | 2 | 0.0 |
105 | dormant_casa | low | 1,577 | 8.2 |
106 | dormant_casa | moderate | 802 | 4.2 |
107 | dormant_casa | unknown | 6,744 | 35.0 |
108 | no_casa | low | 1,116 | 5.8 |
109 | no_casa | moderate | 1,345 | 7.0 |
110 | no_casa | unknown | 4,075 | 21.1 |
111
112 ### M6 max monthly CASA balance in W x covers max(3000, anchor)
113
114 | max balance | covers | n | % |
115 |---|---|---:|---:|
116 | 1000-3000 | False | 254 | 1.3 |
117 | <1000 | False | 4,775 | 24.8 |
118 | >=3,000 | False | 12 | 0.1 |
119 | >=3,000 | True | 230 | 1.2 |
120 | none | False | 14,021 | 72.7 |
121
122 ### M6 external card payment in W x liquidity level
123
124 | ext card payment | liquidity | n | % |
125 |---|---|---:|---:|
126 | False | adequate | 142 | 0.7 |
127 | False | none | 18,705 | 97.0 |
128 | False | weak | 327 | 1.7 |
129 | True | adequate | 54 | 0.3 |
130 | True | none | 49 | 0.3 |
131 | True | weak | 15 | 0.1 |
132
133 ### M6 liquidity level
134
135 | level | n | % |
136 |---|---:|---:|
137 | adequate | 196 | 1.0 |
138 | none | 18,754 | 97.2 |
139 | weak | 342 | 1.8 |
140
141 ### M7 unknown reason
142
143 | reason | n | % |
144 |---|---:|---:|
145 | dormant_casa | 6,744 | 62.3 |
146 | no_casa | 4,075 | 37.7 |
147
148 ### M8 low reason
149
150 | reason | n | % |
151 |---|---:|---:|
152 | 0pt_active_casa | 2,065 | 36.0 |
153 | 0pt_distress | 1,151 | 20.1 |
154 | 1pt | 2,211 | 38.5 |
155 | 2-3pt_distress | 310 | 5.4 |
156
157 ### M9 moderate / high: state x income x liquidity x distress
158
159 | state | income | liquidity | distress | n | % |
160 |---|---|---|---:|---:|---:|
161 | high | stable | adequate | 0 | 47 | 1.7 |
162 | moderate | none | adequate | 0 | 89 | 3.3 |
163 | moderate | stable | adequate | 1 | 13 | 0.5 |
164 | moderate | stable | none | 0 | 2,492 | 91.1 |
165 | moderate | stable | weak | 0 | 47 | 1.7 |
166 | moderate | weak | adequate | 0 | 20 | 0.7 |
167 | moderate | weak | weak | 0 | 28 | 1.0 |
168
169 ### M10 distress parts in W ('' = none)
170
171 | parts | n | % |
172 |---|---:|---:|
173 | (none) | 17,616 | 91.3 |
174 | bureau | 483 | 2.5 |
175 | cheque | 451 | 2.3 |
176 | cheque+bureau | 15 | 0.1 |
177 | cheque+dds | 109 | 0.6 |
178 | cheque+dds+bureau | 1 | 0.0 |
179 | dds | 596 | 3.1 |
180 | dds+bureau | 21 | 0.1 |
181
182 ### M10 distress parts x a1_state
183
184 | parts | a1_state | n | % |
185 |---|---|---:|---:|
186 | bureau | low | 483 | 28.8 |
187 | cheque | low | 448 | 26.7 |
188 | cheque | moderate | 3 | 0.2 |
189 | cheque+bureau | low | 15 | 0.9 |
190 | cheque+dds | low | 108 | 6.4 |
191 | cheque+dds | moderate | 1 | 0.1 |
192 | cheque+dds+bureau | low | 1 | 0.1 |
193 | dds | low | 587 | 35.0 |
194 | dds | moderate | 9 | 0.5 |
195 | dds+bureau | low | 21 | 1.3 |
196
197 ### M11 EOSB result in W x a1_state
198
199 | EOSB result | a1_state | n | % |
200 |---|---|---:|---:|
201 | 0 | high | 47 | 0.2 |
202 | 0 | low | 5,721 | 29.7 |
203 | 0 | moderate | 2,686 | 13.9 |
204 | 0 | unknown | 10,813 | 56.0 |
205 | 1 | low | 16 | 0.1 |
206 | 1 | moderate | 3 | 0.0 |
207 | 1 | unknown | 6 | 0.0 |
208
209 ### M11 EOSB in W x liquidity level
210
211 | liquidity | n | % |
212 |---|---:|---:|
213 | adequate | 1 | 4.0 |
214 | none | 23 | 92.0 |
215 | weak | 1 | 4.0 |
216
217 ### M11 anchor
218
219 Anchor present / p10 p50 p90: [128.34, 837.14, 2342.33]
220
221 | anchor present | n | % |
222 |---|---:|---:|
223 | True | 19,292 | 100.0 |
224
225 ### M11 anchor raises the income x CASA x card-payment floor
226
227 | col 1 | col 2 | col 3 | n | % |
228 |---|---|---|---:|---:|
229 | False | False | False | 5,300 | 27.5 |
230 | False | False | True | 9,437 | 48.9 |
231 | True | False | True | 3,490 | 18.1 |
232 | True | True | True | 1,065 | 5.5 |
233
234 (The log does not label the three boolean columns.)
235
236 ### By product: loan_type x a1_state, x unknown reason, x low reason
237
238 All rows are product `all`:
239
240 | a1_state / reason | n | % |
241 |---|---:|---:|
242 | high | 47 | 0.2 |
243 | low | 5,737 | 29.7 |
244 | moderate | 2,689 | 13.9 |
245 | unknown | 10,819 | 56.1 |
246 | dormant_casa | 6,744 | 62.3 |
247 | no_casa | 4,075 | 37.7 |
248 | 0pt_active_casa | 2,065 | 36.0 |
249 | 0pt_distress | 1,151 | 20.1 |
250 | 1pt | 2,211 | 38.5 |
251 | 2-3pt_distress | 310 | 5.4 |
252
253 ## 4. Sources (`describe_a1_sources`)
254
255 Base (latest month): 19,292 accounts, 18,731 CIFs.
256
257 ### Source depth (month_end)
258
259 | source | all CIFs | base CIFs from |
260 |---|---|---|
261 | feat_cif_internal_salary_monthly | 2024-09-30 .. 2026-08-31 | 2024-09-30 |
262 | feat_cif_bureau_salary_monthly | 2022-10-31 .. 2026-08-31 | 2022-10-31 |
263 | feat_cif_casa_balance_monthly | 2025-02-28 .. 2026-09-30 | 2025-02-28 |
264 | feat_cif_casa_activity_monthly | 2025-02-28 .. 2026-10-31 | 2025-02-28 |
265
266 ### M2 internal salary (>= 1000) history
267
268 | history | n | % |
269 |---|---:|---:|
270 | in_W | 440 | 2.3 |
271 | last_m13-24 | 1,941 | 10.1 |
272 | last_m4-6 | 3,094 | 16.0 |
273 | last_m7-12 | 3,599 | 18.7 |
274 | never | 10,218 | 53.0 |
275
276 ### M2 internal salary history x a1_state
277
278 | history | a1_state | n | % |
279 |---|---|---:|---:|
280 | in_W | high | 38 | 0.2 |
281 | in_W | low | 220 | 1.1 |
282 | in_W | moderate | 182 | 0.9 |
283 | last_m13-24 | high | 1 | 0.0 |
284 | last_m13-24 | low | 669 | 3.5 |
285 | last_m13-24 | moderate | 192 | 1.0 |
286 | last_m13-24 | unknown | 1,079 | 5.6 |
287 | last_m4-6 | low | 1,268 | 6.6 |
288 | last_m4-6 | moderate | 183 | 0.9 |
289 | last_m4-6 | unknown | 1,643 | 8.5 |
290 | last_m7-12 | high | 3 | 0.0 |
291 | last_m7-12 | low | 1,194 | 6.2 |
292 | last_m7-12 | moderate | 278 | 1.4 |
293 | last_m7-12 | unknown | 2,124 | 11.0 |
294 | never | high | 5 | 0.0 |
295 | never | low | 2,386 | 12.4 |
296 | never | moderate | 1,854 | 9.6 |
297 | never | unknown | 5,973 | 31.0 |
298
299 ### M3 AECB salary (>= 1000) by last pull month, before the carry
300
301 | last pull | n | % |
302 |---|---:|---:|
303 | alert_never_salary | 7,644 | 39.6 |
304 | in_W | 3,729 | 19.3 |
305 | last_m13-24 | 1,349 | 7.0 |
306 | last_m25+ | 902 | 4.7 |
307 | last_m4-6 | 2,362 | 12.2 |
308 | last_m7-12 | 2,097 | 10.9 |
309 | no_alert_row | 1,209 | 6.3 |
310
311 ### M3 internal salary (rows) x AECB salary history (columns), n (%)
312
313 | internal \ AECB | alert_never_salary | in_W | last_m13-24 | last_m25+ | last_m4-6 | last_m7-12 | no_alert_row |
314 |---|---|---|---|---|---|---|---|
315 | in_W | 285 (1.5) | 34 (0.2) | 31 (0.2) | 48 (0.2) | 15 (0.1) | 14 (0.1) | 13 (0.1) |
316 | last_m13-24 | 960 (5.0) | 268 (1.4) | 121 (0.6) | 92 (0.5) | 167 (0.9) | 189 (1.0) | 144 (0.7) |
317 | last_m4-6 | 1,982 (10.3) | 349 (1.8) | 130 (0.7) | 169 (0.9) | 121 (0.6) | 88 (0.5) | 255 (1.3) |
318 | last_m7-12 | 2,082 (10.8) | 438 (2.3) | 155 (0.8) | 155 (0.8) | 265 (1.4) | 197 (1.0) | 307 (1.6) |
319 | never | 2,335 (12.1) | 2,640 (13.7) | 912 (4.7) | 438 (2.3) | 1,794 (9.3) | 1,609 (8.3) | 490 (2.5) |
320
321 ### CASA legs of base CIFs in W (2026-06-01 .. 2026-08-31) by lane
322
323 | lane | legs | CIFs |
324 |---|---:|---:|
325 | ambiguous | 5,223 | 2,440 |
326 | card_payment | 1,889 | 1,374 |
327 | card_spend | 25,724 | 1,062 |
328 | economic | 18,144 | 2,708 |
329 | fee_interest | 3,893 | 1,360 |
330 | group_internal | 859 | 238 |
331 | own_loan | 2,054 | 750 |
332 | refund | 387 | 198 |
333 | reversal | 293 | 129 |
334 | signal | 101,967 | 1,150 |
335 | unclassified | 39 | 3 |
336 | wash | 7,107 | 2,258 |
337
338 ### Top unclassified / ambiguous (lane, tran_type, reason)
339
340 | lane | tran_type | reason | n |
341 |---|---|---|---:|
342 | ambiguous | MISCELLANEOUS | None | 5,221 |
343 | unclassified | POS TRANSACTIONS | None | 39 |
344 | ambiguous | MC/DD-ISSUE | None | 2 |
345
346 ### WM vs FTR, base CIFs, last 12 months
347
348 | WM row | WM positive | FTR leg | FTR customer leg | n | % |
349 |---|---|---|---|---:|---:|
350 | False | False | False | False | 338 | 1.8 |
351 | False | False | True | False | 15 | 0.1 |
352 | False | False | True | True | 504 | 2.7 |
353 | True | False | False | False | 6,031 | 32.2 |
354 | True | False | True | False | 258 | 1.4 |
355 | True | False | True | True | 844 | 4.5 |
356 | True | True | False | False | 103 | 0.5 |
357 | True | True | True | False | 110 | 0.6 |
358 | True | True | True | True | 10,528 | 56.2 |
359
360 ## 5. AECB explain (`explain_a1_aecb`)
361
362 Rows 19,292; last step vs the output: 0 states, 0 income levels differ.
363
364 ### Rows per state at each step
365
366 | step | high | moderate | low | unknown |
367 |---|---:|---:|---:|---:|
368 | s0_no_aecb | 37 | 277 | 4,670 | 14,308 |
369 | s1_pull_months | 47 | 2,078 | 5,719 | 11,448 |
370 | s2_one_month_carry | 47 | 2,689 | 5,737 | 10,819 |
371
372 ### s0_no_aecb -> s1_pull_months: 3,132 rows move
373
374 | from | to | n | % |
375 |---|---|---:|---:|
376 | low | moderate | 262 | 8.4 |
377 | moderate | high | 10 | 0.3 |
378 | unknown | low | 1,311 | 41.9 |
379 | unknown | moderate | 1,549 | 49.5 |
380
381 ### s1_pull_months -> s2_one_month_carry: 1,328 rows move
382
383 | from | to | n | % |
384 |---|---|---:|---:|
385 | high | moderate | 1 | 0.1 |
386 | low | moderate | 609 | 45.9 |
387 | moderate | high | 1 | 0.1 |
388 | moderate | low | 88 | 6.6 |
389 | unknown | low | 539 | 40.6 |
390 | unknown | moderate | 90 | 6.8 |
391
392 ### Income source x income level
393
394 | source | level | n | % |
395 |---|---|---:|---:|
396 | both | stable | 26 | 0.1 |
397 | both | weak | 12 | 0.1 |
398 | bureau | stable | 2,656 | 13.8 |
399 | bureau | weak | 1,807 | 9.4 |
400 | internal | stable | 190 | 1.0 |
401 | internal | weak | 212 | 1.1 |
402 | none | none | 14,389 | 74.6 |
403
404 ### Income source x a1_state
405
406 | source | a1_state | n | % |
407 |---|---|---:|---:|
408 | both | high | 1 | 0.0 |
409 | both | low | 18 | 0.1 |
410 | both | moderate | 19 | 0.1 |
411 | bureau | high | 9 | 0.0 |
412 | bureau | low | 2,036 | 10.6 |
413 | bureau | moderate | 2,418 | 12.5 |
414 | internal | high | 37 | 0.2 |
415 | internal | low | 202 | 1.0 |
416 | internal | moderate | 163 | 0.8 |
417 | none | low | 3,481 | 18.0 |
418 | none | moderate | 89 | 0.5 |
419 | none | unknown | 10,819 | 56.1 |
420
421 ### AECB months in W (with the carry) x income level
422
423 | AECB months | level | n | % |
424 |---:|---|---:|---:|
425 | 0 | none | 14,389 | 74.6 |
426 | 0 | stable | 190 | 1.0 |
427 | 0 | weak | 212 | 1.1 |
428 | 1 | stable | 292 | 1.5 |
429 | 1 | weak | 1,053 | 5.5 |
430 | 2 | stable | 1,225 | 6.3 |
431 | 2 | weak | 603 | 3.1 |
432 | 3 | stable | 1,165 | 6.0 |
433 | 3 | weak | 163 | 0.8 |
434
435 AECB in W, window total passes, the 25% check fails: **912**
436
437 ### Salary stopped x income source x income level
438
439 | source | level | n | % |
440 |---|---|---:|---:|
441 | bureau | stable | 207 | 6.7 |
442 | bureau | weak | 208 | 6.7 |
443 | none | none | 2,679 | 86.6 |
444
445 (Percentages are within the salary-stopped = 1 group, 3,094 rows.)
446
447 ### Salary stopped x a1_state
448
449 | salary stopped | a1_state | n | % |
450 |---:|---|---:|---:|
451 | 0 | high | 47 | 0.2 |
452 | 0 | low | 4,469 | 23.2 |
453 | 0 | moderate | 2,506 | 13.0 |
454 | 0 | unknown | 9,176 | 47.6 |
455 | 1 | low | 1,268 | 6.6 |
456 | 1 | moderate | 183 | 0.9 |
457 | 1 | unknown | 1,643 | 8.5 |
458
459 ## Notes
460
461 - The new a1_state differs from the old (`crx_cc_a1_ability_v2`) output for 5,872 of 19,292 rows
462   (everything off the diagonal in the old x new table): low->unknown 1,944, unknown->moderate 1,855,
463   unknown->low 1,366, low->moderate 668, moderate->high 38, low->high 1.
464 - The "last step vs the output" check in the AECB explain shows the final step (s2_one_month_carry)
465   matches the output exactly.
466 - The log was transcribed without any rerun; percentages are as printed by the pipeline.
467
````

## Notes on specific spots
- Lines 63-70 use `2026-01-01` style month keys (b08, handoff 20, used `2026-01`).
- Lines 63-70: the `moderate` column holds the values 19.19 ... 13.94 and `low` 28.48 ... 29.74. The range table (lines 76-79) confirms: moderate 13.94-19.40, low 27.41-32.44.
- Checks I ran on the transcription: line 31-36 sums to 19,292 (47+5,737+2,689+10,819); old x new (lines 48-57) sums to 19,292 and off-diagonal = 5,872 (matches line 461); s0/s1/s2 rows (lines 368-370) each sum to 19,292; line 372 "3,132 rows move" = 262+10+1,311+1,549; line 381 "1,328 rows move" = 1+609+1+88+539+90; M3 AECB table (lines 303-309) sums to 19,292; salary-stopped x a1_state (lines 451-457) sums to 19,292; WM vs FTR (lines 350-358) sums to 18,731 CIFs.
- Line 117 `<1000` and line 118-119 `>=3,000`: written exactly as in the photo.
- Lines 227-232: the three boolean columns are unlabeled in the log ("col 1 | col 2 | col 3"); only 4 of the 8 combinations appear.
- Line 264: `casa_activity_monthly` ends 2026-10-31 and `casa_balance_monthly` 2026-09-30, as printed.
- Line 435: `**912**` is bold in the source.
- Line 39 in the editor (the cursor line) is empty.
- Dense numerics most at risk of misreading: the M3 cross table (lines 315-319) and the M2/M3 tables (lines 280-309).
