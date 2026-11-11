# Handoff 68: `a1_check_new/summary.md` (A1 ability check, new vs old, results summary), lines 1-301

## Context for Claude Code

- Source: 6 phone photos of VS Code (LG monitor), file `tmp_validation/a1_check_new/summary.md`, marked `U` (untracked). Other open tabs: `pipeline_registry.py`, `21_a1_evidence_family_rule.md`. Branch shown in the status bar ends in `…persona_refactor`.
- Content: summary of the A1 (ability) check run with the new bureau salary input (`feat_bureau_salary_unified`, see handoff 66) against the old input, for all four models at month 2026-08-31. Per model: output state, new reason, moves old to new, families, and (60_180 only) outcomes and gaps.
- Photos merged by editor line number: P1 = 1-59; P2 = 55-109; P3 = 102-157; P4 = 153-207; P5 = 202-258; P6 = 239-301. Lines 1-301 are covered. Line 301 is the last line I can see and is empty.
- Format: `NNN  text`, NNN is the editor line number. The source tables are padded to align columns; I copied each cell but normalised the padding to single spaces. Divider rows keep the alignment colons I could see (`---:` = right-aligned).
- Section order in the file: Overview, then `rl_60_180`, `cc_180_plus`, `cc_60_180`, `rl_180_plus`.

## Transcription

```
  1  # A1 ability check (new vs old) - results summary
  2  
  3  Source: `kedro run --env=dev --pipeline=crx_<cc|rl>_a1_check`, latest month 2026-08-31.
  4  Only the numeric blocks (OUTPUT, MOVES, FAMILIES, OUTCOMES) are summarised.
  5  
  6  ## Overview (all four models, month 2026-08-31)
  7  
  8  | model_id | rows | high new/old | low new/old | unknown new/old | moderate new/old |
  9  |---|---:|---:|---:|---:|---:|
 10  | rl_60_180 | 3,985 | 1.2% / 0.3% | 49.2% / 44.7% | 41.0% / 46.1% | 8.7% / 8.9% |
 11  | cc_60_180 | 19,292 | 1.6% / 0.2% | 25.6% / 28.9% | 58.0% / 56.6% | 14.8% / 14.4% |
 12  | rl_180_plus | 55,371 | 0.1% / 0.0% | 11.0% / 6.9% | 85.4% / 89.5% | 3.5% / 3.5% |
 13  | cc_180_plus | 318,663 | 0.3% / 0.0% | 8.4% / 6.4% | 85.2% / 87.4% | 6.2% / 6.2% |
 14  
 15  Outcomes exist for the 60_180 models only. Order of sections below: rl_60_180, cc_180_plus, cc_60_180,
 16  rl_180_plus.
 17  
 18  ## rl_60_180
 19  
 20  Rows: new 3,985, old 3,985.
 21  
 22  ### Output - state (new vs old)
 23  
 24  | state | new n | new % | old n | old % |
 25  |---|---:|---:|---:|---:|
 26  | high | 47 | 1.2% | 11 | 0.3% |
 27  | moderate | 345 | 8.7% | 354 | 8.9% |
 28  | low | 1,960 | 49.2% | 1,783 | 44.7% |
 29  | unknown | 1,633 | 41.0% | 1,837 | 46.1% |
 30  
 31  ### Output - new reason
 32  
 33  | reason | n | % |
 34  |---|---:|---:|
 35  | None | 2,845 | 71.4% |
 36  | distress | 760 | 19.1% |
 37  | income | 294 | 7.4% |
 38  | money_in | 43 | 1.1% |
 39  | cross_product | 39 | 1.0% |
 40  | money_out | 4 | 0.1% |
 41  
 42  Unknown rows by reason: dormant_casa 1,203 (30.2%), no_casa 430 (10.8%).
 43  
 44  ### Moves (old -> new)
 45  
 46  | old | new | n | % |
 47  |---|---|---:|---:|
 48  | high | high | 10 | 0.3% |
 49  | high | moderate | 1 | 0.0% |
 50  | moderate | high | 30 | 0.8% |
 51  | moderate | moderate | 284 | 7.1% |
 52  | moderate | low | 40 | 1.0% |
 53  | low | high | 7 | 0.2% |
 54  | low | moderate | 26 | 0.7% |
 55  | low | low | 1,510 | 37.9% |
 56  | low | unknown | 240 | 6.0% |
 57  | unknown | moderate | 34 | 0.9% |
 58  | unknown | low | 410 | 10.3% |
 59  | unknown | unknown | 1,393 | 35.0% |
 60  
 61  ### Families (level distributions, n of 3,985)
 62  
 63  | family | none/None | weak/some | stable/strong |
 64  |---|---:|---:|---:|
 65  | a1_income_level | none 3,234 (81.2%) | weak 380 (9.5%) | stable 371 (9.3%) |
 66  | a1_money_in_level | None 3,347 (84.0%), none 170 (4.3%) | some 380 (9.5%) | strong 88 (2.2%) |
 67  | a1_money_out_level | None 3,571 (89.6%), none 89 (2.2%) | some 275 (6.9%) | strong 50 (1.3%) |
 68  | a1_cross_product_level | none 2,971 (74.6%) | some 951 (23.9%) | strong 63 (1.6%) |
 69  
 70  Strong families per row: 0 = 3,494 (87.7%), 1 = 432 (10.8%), 2 = 38 (1.0%), 3 = 20 (0.5%), 4 = 1 (0.0%).
 71  
 72  Sweepable balance flag = 1: 48 (1.2%). Money-in strong only through the balance: 26 (0.7%).
 73  
 74  State without balance -> with it (rows the balance moves): low->moderate 7 (0.2%),
 75  moderate->high 5 (0.1%), unknown->moderate 8 (0.2%).
 76  
 77  ### Outcomes (cohort 2026-01..2026-05, bucket 4-7: 12,512 rows / 5,416 accounts)
 78  
 79  Raw rate [95% CI, clustered on CIF]:
 80  
 81  | state | rows / accts | cure_3 | pay_any_3 | roll_3 | n |
 82  |---|---:|---|---|---|---:|
 83  | high | 124 / 73 | 27.6% [14.6, 40.7] | 75.2% [65.1, 85.4] | 59.0% [44.6, 73.5] | 105 |
 84  | moderate | 1,423 / 819 | 15.4% [13.0, 17.9] | 64.8% [61.2, 68.5] | 68.9% [65.3, 72.5] | 1,322 |
 85  | low | 6,163 / 3,329 | 9.9% [8.8, 11.0] | 44.7% [42.6, 46.9] | 82.0% [80.4, 83.5] | 5,967 |
 86  | unknown | 4,802 / 2,347 | 8.6% [7.4, 9.8] | 36.4% [34.1, 38.6] | 85.3% [83.7, 86.9] | 4,683 |
 87  
 88  Gaps, standardised to the better state's DPD-band mix:
 89  
 90  | gap | cure_3 | pay_any_3 | roll_3 | n |
 91  |---|---|---|---|---:|
 92  | high - moderate | +10.9pp [-2.5, 24.3] | +9.1pp [-1.7, 19.8] | -8.6pp [-23.4, 6.1] | 105/1,322 |
 93  | moderate - low | +5.8pp [3.3, 8.3] | +20.4pp [16.4, 24.3] | -13.3pp [-16.9, -9.6] | 1,322/5,967 |
 94  
 95  ## cc_180_plus
 96  
 97  Rows: new 318,663, old 318,663.
 98  
 99  ### Output - state (new vs old)
100  
101  | state | new n | new % | old n | old % |
102  |---|---:|---:|---:|---:|
103  | high | 836 | 0.3% | 110 | 0.0% |
104  | moderate | 19,623 | 6.2% | 19,658 | 6.2% |
105  | low | 26,789 | 8.4% | 20,459 | 6.4% |
106  | unknown | 271,415 | 85.2% | 278,436 | 87.4% |
107  
108  ### Output - new reason
109  
110  | reason | n | % |
111  |---|---:|---:|
112  | None | 289,276 | 90.8% |
113  | distress | 9,094 | 2.9% |
114  | income | 19,215 | 6.0% |
115  | money_in | 732 | 0.2% |
116  | cross_product | 310 | 0.1% |
117  | money_out | 36 | 0.0% |
118  
119  Unknown rows by reason: no_casa 235,821 (74.0%), dormant_casa 35,594 (11.2%).
120  
121  ### Moves (old -> new)
122  
123  | old | new | n | % |
124  |---|---|---:|---:|
125  | high | high | 108 | 0.0% |
126  | high | moderate | 2 | 0.0% |
127  | moderate | high | 502 | 0.2% |
128  | moderate | moderate | 19,115 | 6.0% |
129  | moderate | low | 41 | 0.0% |
130  | low | high | 226 | 0.1% |
131  | low | moderate | 264 | 0.1% |
132  | low | low | 19,162 | 6.0% |
133  | low | unknown | 807 | 0.3% |
134  | unknown | moderate | 242 | 0.1% |
135  | unknown | low | 7,586 | 2.4% |
136  | unknown | unknown | 270,608 | 84.9% |
137  
138  ### Families (level distributions, n of 318,663)
139  
140  | family | none / None | weak / some | stable / strong |
141  |---|---:|---:|---:|
142  | a1_income_level | none 287,127 (90.1%) | weak 10,299 (3.2%) | stable 21,237 (6.7%) |
143  | a1_money_in_level | None 315,281 (98.9%), none 1,236 (0.4%) | some 925 (0.3%) | strong 1,221 (0.4%) |
144  | a1_money_out_level | None 316,558 (99.3%), none 578 (0.2%) | some 692 (0.2%) | strong 835 (0.3%) |
145  | a1_cross_product_level | none 308,970 (97.0%) | some 9,075 (2.8%) | strong 618 (0.2%) |
146  
147  Strong families per row: 0 = 296,173 (92.9%), 1 = 21,488 (6.7%), 2 = 619 (0.2%), 3 = 347 (0.1%),
148  4 = 36 (0.0%).
149  
150  Sweepable balance flag = 1: 588 (0.2%). Money-in strong only through the balance: 533 (0.2%).
151  
152  State without balance -> with it (rows the balance moves): low->moderate 76 (0.0%),
153  moderate->high 75 (0.0%), unknown->moderate 310 (0.1%).
154  
155  ### Outcomes
156  
157  None: 180+ has no outcomes (as in rounds 1-3).
158  
159  ## cc_60_180
160  
161  Rows: new 19,292, old 19,292.
162  
163  ### Output - state (new vs old)
164  
165  | state | new n | new % | old n | old % |
166  |---|---:|---:|---:|---:|
167  | high | 311 | 1.6% | 45 | 0.2% |
168  | moderate | 2,850 | 14.8% | 2,769 | 14.4% |
169  | low | 4,948 | 25.6% | 5,568 | 28.9% |
170  | unknown | 11,183 | 58.0% | 10,910 | 56.6% |
171  
172  ### Output - new reason
173  
174  | reason | n | % |
175  |---|---:|---:|
176  | None | 14,415 | 74.7% |
177  | income | 2,654 | 13.8% |
178  | distress | 1,795 | 9.3% |
179  | money_in | 213 | 1.1% |
180  | cross_product | 196 | 1.0% |
181  | money_out | 19 | 0.1% |
182  
183  Unknown rows by reason: dormant_casa 6,527 (33.8%), no_casa 4,656 (24.1%).
184  
185  ### Moves (old -> new)
186  
187  | old | new | n | % |
188  |---|---|---:|---:|
189  | high | high | 43 | 0.2% |
190  | high | moderate | 2 | 0.0% |
191  | moderate | high | 186 | 1.0% |
192  | moderate | moderate | 2,546 | 13.2% |
193  | moderate | low | 37 | 0.2% |
194  | low | high | 82 | 0.4% |
195  | low | moderate | 169 | 0.9% |
196  | low | low | 4,352 | 22.6% |
197  | low | unknown | 965 | 5.0% |
198  | unknown | moderate | 133 | 0.7% |
199  | unknown | low | 559 | 2.9% |
200  | unknown | unknown | 10,218 | 53.0% |
201  
202  ### Families (level distributions, n of 19,292)
203  
204  | family | none / None | weak / some | stable / strong |
205  |---|---:|---:|---:|
206  | a1_income_level | none 14,316 (74.2%) | weak 1,980 (10.3%) | stable 2,996 (15.5%) |
207  | a1_money_in_level | None 17,655 (91.5%), none 600 (3.1%) | some 659 (3.4%) | strong 378 (2.0%) |
208  | a1_money_out_level | None 17,981 (93.2%), none 402 (2.1%) | some 606 (3.1%) | strong 303 (1.6%) |
209  | a1_cross_product_level | none 17,853 (92.5%) | some 1,071 (5.6%) | strong 368 (1.9%) |
210  
211  Strong families per row: 0 = 15,786 (81.8%), 1 = 3,116 (16.2%), 2 = 255 (1.3%), 3 = 121 (0.6%),
212  4 = 14 (0.1%).
213  
214  Sweepable balance flag = 1: 146 (0.8%). Money-in strong only through the balance: 126 (0.7%).
215  
216  State without balance -> with it (rows the balance moves): low->moderate 28 (0.1%),
217  moderate->high 35 (0.2%), unknown->moderate 38 (0.2%).
218  
219  ### Outcomes (cohort 2026-01..2026-05, bucket 4-7: 74,256 rows / 29,629 accounts)
220  
221  Raw rate [95% CI, clustered on CIF]:
222  
223  | state | rows / accts | cure_3 | pay_any_3 | roll_3 | n |
224  |---|---:|---|---|---|---:|
225  | high | 2,045 / 1,045 | 31.3% [28.6, 34.0] | 58.5% [55.3, 61.7] | 52.8% [49.5, 56.1] | 2,045 |
226  | moderate | 13,945 / 7,376 | 15.9% [15.1, 16.7] | 41.3% [40.1, 42.5] | 73.2% [72.1, 74.3] | 13,945 |
227  | low | 18,670 / 10,794 | 10.9% [10.3, 11.5] | 29.1% [28.1, 30.0] | 82.3% [81.6, 83.1] | 18,670 |
228  | unknown | 39,596 / 17,529 | 7.8% [7.4, 8.1] | 19.9% [19.2, 20.5] | 87.5% [87.0, 88.0] | 39,596 |
229  
230  Gaps, standardised to the better state's DPD-band mix:
231  
232  | gap | cure_3 | pay_any_3 | roll_3 |
233  |---|---|---|---|
234  | high - moderate | +14.7pp [12.0, 17.3] | +16.3pp [13.0, 19.5] | -19.6pp [-22.9, -16.3] |
235  | moderate - low | +5.1pp [4.2, 6.0] | +12.4pp [11.1, 13.8] | -9.3pp [-10.5, -8.1] |
236  
237  Gap n: high/moderate = 2,045/13,945; moderate/low = 13,945/18,670.
238  
239  ## rl_180_plus
240  
241  Rows: new 55,371, old 55,371.
242  
243  ### Output - state (new vs old)
244  
245  | state | new n | new % | old n | old % |
246  |---|---:|---:|---:|---:|
247  | high | 66 | 0.1% | 17 | 0.0% |
248  | moderate | 1,919 | 3.5% | 1,962 | 3.5% |
249  | low | 6,077 | 11.0% | 3,822 | 6.9% |
250  | unknown | 47,309 | 85.4% | 49,570 | 89.5% |
251  
252  ### Output - new reason
253  
254  | reason | n | % |
255  |---|---:|---:|
256  | None | 51,326 | 92.7% |
257  | distress | 2,085 | 3.8% |
258  | income | 1,703 | 3.1% |
259  | money_in | 221 | 0.4% |
260  | cross_product | 31 | 0.1% |
261  | money_out | 5 | 0.0% |
262  
263  Unknown rows by reason: no_casa 36,853 (66.6%), dormant_casa 10,456 (18.9%).
264  
265  ### Moves (old -> new)
266  
267  | old | new | n | % |
268  |---|---|---:|---:|
269  | high | high | 17 | 0.0% |
270  | moderate | high | 37 | 0.1% |
271  | moderate | moderate | 1,865 | 3.4% |
272  | moderate | low | 60 | 0.1% |
273  | low | high | 12 | 0.0% |
274  | low | moderate | 27 | 0.0% |
275  | low | low | 3,516 | 6.3% |
276  | low | unknown | 267 | 0.5% |
277  | unknown | moderate | 27 | 0.0% |
278  | unknown | low | 2,501 | 4.5% |
279  | unknown | unknown | 47,042 | 85.0% |
280  
281  ### Families (level distributions, n of 55,371)
282  
283  | family | none / None | weak / some | stable / strong |
284  |---|---:|---:|---:|
285  | a1_income_level | none 52,078 (94.1%) | weak 1,299 (2.3%) | stable 1,994 (3.6%) |
286  | a1_money_in_level | None 54,361 (98.2%), none 324 (0.6%) | some 390 (0.7%) | strong 296 (0.5%) |
287  | a1_money_out_level | None 55,006 (99.3%), none 78 (0.1%) | some 211 (0.4%) | strong 76 (0.1%) |
288  | a1_cross_product_level | none 51,887 (93.7%) | some 3,437 (6.2%) | strong 47 (0.1%) |
289  
290  Strong families per row: 0 = 53,078 (95.9%), 1 = 2,202 (4.0%), 2 = 64 (0.1%), 3 = 25 (0.0%),
291  4 = 2 (0.0%).
292  
293  Sweepable balance flag = 1: 257 (0.5%). Money-in strong only through the balance: 245 (0.4%).
294  
295  State without balance -> with it (rows the balance moves): low->moderate 40 (0.1%),
296  moderate->high 7 (0.0%), unknown->moderate 161 (0.3%).
297  
298  ### Outcomes
299  
300  None: 180+ has no outcomes (as in rounds 1-3).
301  
```

## Notes on specific spots

Sum checks (all done on the transcribed numbers, every block ties to its model's row count):
- State tables, new and old: rl_60_180 3,985, cc_180_plus 318,663, cc_60_180 19,292, rl_180_plus 55,371.
- Reason tables sum to the same totals: rl_60_180 3,985, cc_180_plus 318,663, cc_60_180 19,292, rl_180_plus 55,371.
- "Unknown rows by reason" adds up to the new unknown count in each model: 1,203 + 430 = 1,633; 235,821 + 35,594 = 271,415; 6,527 + 4,656 = 11,183; 36,853 + 10,456 = 47,309.
- Moves: each old-state group sums to the old count, and each new-state group to the new count. For example, rl_60_180 old high 10 + 1 = 11, new high 10 + 30 + 7 = 47. cc_60_180 old low 82 + 169 + 4,352 + 965 = 5,568. rl_180_plus has no "high to moderate" row (zero moves).
- Families: for every family and model, the level counts sum to the model's row count. "Strong families per row" also sums to the row count: 3,494 + 432 + 38 + 20 + 1 = 3,985; 296,173 + 21,488 + 619 + 347 + 36 = 318,663; 15,786 + 3,116 + 255 + 121 + 14 = 19,292; 53,078 + 2,202 + 64 + 25 + 2 = 55,371.
- Outcomes rows for the two 60_180 models sum to the cohort row counts: loans 124 + 1,423 + 6,163 + 4,802 = 12,512; cards 2,045 + 13,945 + 18,670 + 39,596 = 74,256.
- Overview (lines 10-13) agrees with the new/old state shares in each model's block.
- Cross-handoff: the cohort sizes in lines 77 and 219 (12,512 rows / 5,416 accounts; 74,256 / 29,629) are the same as in handoff 65 (`oos_results.md`). Row counts 3,985, 19,292, 55,371 and 318,663 are the same as in handoffs 60 and 67.

Flagged spots:
- Tables are normalised to single-space cells. The source pads cells to align columns, so my spacing differs but the cell contents are as printed.
- Line 3: `<cc|rl>` is as printed.
- Line 176-178: in the cc_60_180 reason table `income` comes before `distress`; in the other three models `distress` comes first. That is as printed.
- Outcomes `accts` column (lines 83-86, 225-228) sums to more than the distinct account count (for example 73 + 819 + 3,329 + 2,347 = 6,568 vs 5,416), because an account can sit in several states across cohort months. Not a transcription error.
- Lines 55-59, 102-109, 153-157, 202-207 and 239-258 each appear in two photos and matched.
- Line 301 is empty and is the last line I can see.
