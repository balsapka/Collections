# A1 v03 (rerun, v03b) — PROD results (cc_60_180 + rl_60_180, 2026-10-28)

`tmp_validation/a1_v03/summary.md`, the later full version (sections 0-9, "rerun 2026-10-28, all tables
ran, 0 errors"); supersedes the first 84 lines filed in `a1_v03_results.md`. Transcribed from photos
(`pics/claude_code_handoff_12.md`, photos 53-62), OCR quality; line numbers are the editor's. Filed by
the A2 session; reviewed 2026-10-28 (end of file).

````
1   # A1 Ability — why the states fire at these rates
2
3   60-180 DPD, 31 Aug 2026. CC `cc_60_180`: 19,292 accounts / 18,731 CIFs. RL `rl_60_180`: 3,985
4   accounts / 3,608 CIFs.
5   Source: `results_cc_60_180.json`, `results_rl_60_180.json` (rerun 2026-10-28, all tables ran, 0
6   errors). "-" = not computed.
7
8   ## 0. Bureau inputs (base CIFs)
9   **Is the missing bureau salary the data or the join? The join.** 88% of CC CIFs have a bureau
10  alert
11  row in 12 months, but only 0.58% reach a bureau file.
12
13  | Funnel (CIFs) | CC | RL |
14  |---|---|---|
15  | base | 18,731 | 3,608 |
16  | in `prm_bureau_cif_bridge` | 109 (0.58%) | 123 (3.4%) |
17  | bureau file in 24 months | 63 | 95 |
18  | any `stg_aecb_salary_history` row (any month) | 39 | 74 |
19  | parsed month in 24 months | 39 | 74 |
20  | amount > 0 | 34 | 63 |
21  | same, base CIFs with alert row in 12m (16,536 / 3,220) | 106→61→38→38→33 | 114→90→72→72→61 |
22
23  - The 88% "pull" is the alert table (`prm_bureau_alert_enriched`: 93.8% of CC / 96.2% of RL
24    base
25    CIFs have a row). Salary needs the bridge. 99.4% of CC CIFs drop out there, before any date
26  or
27    salary filter.
28  - Date is not the cause: ignoring file and date, 51 CC / 93 RL CIFs have any salary row. Salary
29    is
30    present for 62% (CC 39/63) and 78% (RL 74/95) of CIFs that have a file in 24 months.
31  - Not measured: how many files in `stg_aecb_salary_history` the bridge cannot reach (the run
32    only
33    reads the bridge's files).
34  - RL's bureau salary comes mostly from `feature_retail_loans`, not the AECB table: 53% of RL
35    CIFs
36    have a bureau salary month (both 45.5%, bureau-only 7.9%); only 63 through the AECB table.
37
38  - `prm_bureau_cif_bridge`: Structure is sound: 1 CIF per file (219/219, 371/371), 1 row per
39    (file, load date). A CIF has 1 / 2 / 3+ files: 60/24/25 (CC), 40/33/50 (RL), max 8 / 15.
40    `cif_id` = digits of `PRVDR_SUBJ_NUM` from the **alert** table, one arbitrary row per
41    subject, inner-joined to `contract_link` (`prm_bureau.py:46-59`). **Verdict:** **Not usable
42    at 0.6% / 3.4% coverage.** Named fix: the link; why 99% (CC) / 96% (RL) of CIFs with an alert
43    row have no `contract_link` file.
44  - `stg_aecb_salary_history`: MMyyyy: 0% NULL, 100% plausible 2015→obs+2m. yyyyMM: **100% NULL**
45    (so the engine's MMyyyy is right; the DE `YYYYMM` is wrong). Raw codes all 6 digits
46    (`012021`, `012022`, `022021` …). Amount NULL 61% / 65%, zero 0% / 5.6%. One load date per
47    (file, month). 2+ providers per (file, month): 46% / 36%; sum would pass the floor where max
48    does not in 0 / 2 CIF-months (of 489 / 919). Columns (CC): file id, ref_mnth, provider no,
49    EDP_LOAD_DATE, tot_sal_amt, trnsfr_cnt, lst_upd_dt, dp_acct_no (RL: no dp_acct_no).
50    **Verdict:** **Usable as is.** Value limited by the bridge.
51  - `prm_bureau_alert_enriched`: Base CIFs with a row 93.8% / 96.2%. Null: alert_process_id 0,
52    extract_date 0, alert_description 0, contract_type 27.6% / 24.5%, bounced_cheque_amount 99.1%
53    / 96.9% (every non-null > 0). `extract_date` = `edp_load_date` (0 days at p10/p50/p90): the
54    pull date. Rows per (alert_process_id, load date): all 3+ (p50 232 / 50). **Verdict:**
55    **Usable as is** for pull and bounce; repeats (35% / 43% of bureau-only flags) treated as the
56    same bounce.
57
58  ## 1. The distribution
59  | | CC | RL |
60  |---|---|---|
61  | Unknown | 62.7% (12,096) | 9.1% (362) |
62  | Low | 36.2% (6,984) | 89.5% (3,566) |
63  | Moderate | 1.1% (204) | 1.4% (56) |
64  | High | 8 (0.04%) | 1 (0.03%) |
65
66  ## 2. Per state
67  - **High.** CC 8, RL 1: stable income and adequate liquidity, no distress. Stable income alone:
68    42
69    CC / 6 RL accounts.
70  - **Moderate.** CC 109 of 204 (53%) and RL 26 of 56 (46%) are adequate liquidity with no income
71    evidence. Stable income alone: 18 CC / 3 RL.
72  - **Low.** CC: 0 points + CASA flow, no distress 4,752 (68%); 0 points + distress 1,712
73    (24.5%); 1
74    point 466; 2-3 points + distress 54. RL: 2,521 (71%); 672 (19%); 1 point 349; 24.
75  - **Unknown.** CC: no CASA with us 52.7%, dormant CASA 47.3%; salary none 68%, internal-only
76    (too
77    old) 32%; alert row in 12m 88%. RL: no CASA 83%, dormant 17%; salary none 63%, bureau 27%,
78    internal 10%; alert row 77%.
79
80  ## 3. What's missing
81  | | CC | RL |
82  |---|---|---|
83  | Income none | 98.5% (18,994) | 97.4% (3,883) |
84  | - N1 no salary in 24m | 53.6% (10,177) | 20.2% (807) |
85  | - N2-N4 latest older than m3 | 45.8% (8,719) | 75.8% (3,022) |
86  | Median age of latest salary (internal / bureau) | 8 / 12 months | 7 / 15 months |
87  | CIFs: internal/bureau/both/neither | 46.9/0.06/0.12/53.0% | 28.8/7.9/45.5/17.8% |
88  | Liquidity none | 97.2% (18,754) | 90.9% (3,623) |
89  | - CASA rows but m1-m3 < AED 1,000 / no CASA | 11,721 / 7,033 | 2,841 / 782 |
90  | `casa_active` / external card payment | 34.3% / 0.6% (median 830) | 83.6% / 1.0% (median 1,000) |
91
92  **Pull gap (income none, alert row in 12m, no bureau salary month in 24m):**
93
94  | | CC | RL |
95  |---|---|---|
96  | N1 | 9,163 of 10,177 (90.0%) | 655 of 807 (81.2%) |
97  | N2-N4 | 7,489 of 8,719 (85.9%) | 907 of 3,022 (30.0%); 1,835 more (60.7%) have a stale one |
98  | Total | 16,652 (86.3% of rows) | 1,562 (39.2% of rows) |
99  | Alert row and a bureau salary month (stale) | 32 | 1,835 |
100
101 The upper bound of what a bureau salary feed could reach is this table. The bridge (section 0)
102 caps
103 what the current feed delivers.
104
105 **Salary dating (new finding).** `week_number` is `yyyyMM0W` (suffix 01-04 only, 695,244 /
106 233,708
107 snapshot rows), not a date. The engine parses it as `yyyyMMdd` (`signals.py:95-99`). WM's
108 `ft_days_since_salary_transaction` counts from the 1st of the salary month: WM's decode lands
109 on day
110 1 in 100% of rows, the engine's in 0%.
111 - The engine dates **every** salary one month early (month difference -1 in 100% of rows).
112 - Latest salary month is m1 for 0.0% of CIFs under the engine, 3.2% CC / 2.8% RL under WM's
113   decode.
114   `income_m1` fills for 0.0% of CC rows (RL 0.03%), and 86% / 85% of rows with any income month
115 have
116   it at m6.
117 - If dated as WM does, with the engine's own rule: CC income none→weak 142, weak→stable 113;
118   state
119   Low→Moderate 80, Moderate→High 20. RL: none→weak 106, weak→stable 17; Low→Moderate 32,
120   Moderate→High 6. No Unknown row moves.
121
122 **Salary timing (24 months, base CIFs).**
123 - History: salary months per CIF p10/p50/p90 = 1/9/17 (CC), 3/13/19 (RL). 53% / 55% have a gap
124   between earliest and latest. Months ≥4 before the snapshot are present: 27.7% CC / 22.4% RL
125 of
126   snapshot rows (the feature is forward-filled, no 3-month look-back).
127 - Double months (≥1.8x the CIF's median, interior, CIFs with ≥4 months): CC 7,651 of 79,879
128   CIF-months (9.6%); RL 2,628 of 31,267 (8.4%). Median ratio 2.07x / 2.11x. Of interior doubles
129   (7,246 / 2,497): next month missing, previous present (early-pay) 23.6% / 22.7%; either
130 neighbour
131   missing 56.6% / 52.6%; both present (bonus) 43.4% / 47.4%. Windows holding a double: 39 CC /
132 3 RL
133   rows.
134 - `pri_salary_from_casa_txns` (month_sum, salary_count): **NOT FOUND** in our catalog (searched
135   `conf/**/*.yml` and `src/**`). It exists in `wealth_management` `conf/base/catalog.yml:1394`,
136   built by `income_pipeline.py:59` via `income.py:17`.
137 - Window-total rule (Stable = window salary ≥ 2x threshold, not >25% below prior window), on
138   the
139   engine's series: CC weak→stable 46 rows (14 with a double); Low→Moderate 21 (5),
140 Moderate→High 8
141   (4); nothing moves down. RL: weak→stable 2 (1), Low→Moderate 2 (1). On the WM-dated series
142 with
143   this rule: CC none→weak 126, none→stable 16, weak→stable 145; Low→Moderate 101, Moderate→High
144 28.
145   RL: none→weak 90, none→stable 16, weak→stable 21; Low→Moderate 41, Moderate→High 8.
146
147 **EOS (bureau).** Bureau month > 3x the median of the prior 12 months (3+ prior months needed):
148 CC
149 39 CIFs with a bureau month, 3 EOS-like, 0 of 4 followed by no salary; no row has one in the
150 window.
151 RL: 1,935 CIFs, 74 eligible, 10 EOS-like, 0 of 16 followed by no salary, 1 row in the window
152 (Stable, Moderate). Bureau history is too thin to detect EOS today.
153 **EOS (DCORE results).** CC 378 events, 276 CIFs, 292 base rows with an EOSB result in 24m
154 (EOSB
155 358, AWAITING 12, RECEIVED 4, EXPECTING 3). By state: Unknown 102, Low 181, Moderate 9. By
156 liquidity: none 273, weak 14, adequate 5. RL: 299 events, 171 CIFs, 175 rows: Unknown 4, Low
157 169,
158 Moderate 2; liquidity none 147, weak 27, adequate 1.
159
160 ## 4. Distress
161 | | CC | RL |
162 |---|---|---|
163 | CIFs with a bounce/return in window | 1,764 (9.4%) | 570 (15.8%) |
164 | DDS-only / bureau-only / cheque-only | 3.0 / 3.2 / 2.2% | 4.7 / 5.0 / 4.8% |
165 | Overlaps | cheque+DDS 107, DDS+bureau 25, cheque+bureau 16, all 1 | 31, 5, 8, 2 |
166 | Low rows with distress | 26.4% | 21.5% |
167 | Bureau-only flags repeating an earlier amount | 35.2% | 43.4% |
168
169 Moderate 0.5% (CC) / 0% (RL) carry distress; High and Unknown 0%.
170 ## 5. Anchor and stability
171 | | CC | RL |
172 |---|---|---|
173 | Anchor p10 / p50 / p90 (AED) | 128 / 837 / 2,342 | 1,193 / 2,389 / 8,018 |
174 | Anchor raises income bar / liquidity floor | 23.6% / 5.5% | 81.5% / 38.2% |
175 | Unknown across 8 months | 61.2-64.7% | 6.0-12.2% |
176 | Low / Moderate / High | 33.0-37.0 / 1.1-2.1 / 0.04-0.33% | 85.8-91.8 / 1.4-2.2 / 0.03-0.11% |
177
178 ## 6. Recompute check
179 All persona-month rows re-run through the engine's functions and compared on state, income
180 level,
181 liquidity level, points, distress: CC 128,927 rows, RL 23,731 rows, **0 mismatches** on every
182 column.
183
184 ## 7. What would move (rows, 31 Aug)
185 | Change | CC | RL |
186 |---|---|---|
187 | Salary dated as WM does (engine rule) | Low→Mod 80, Mod→High 20 | Low→Mod 32, Mod→High 6 |
188 | + window-total rule | Low→Mod 101, Mod→High 28 | Low→Mod 41, Mod→High 8 |
189 | Only customer-initiated open `casa_active` | Low→Unknown 1,058 (15.2%) | 400 (11.2%) |
190 | - and not self-transfers either | 2,171 (31.1% of Low) | 1,723 (48.3%) |
191 | - RL: EMI repayments, top-ups do not open it (self-transfers do) | - | 1,196-1,791 (33.5-50.2%) |
192
193 ## 8. Activity gate (`casa_active`)
194 **Part A.** `casa_active` = any week in the window with CASA inflow > 0 or outflow > 0
195 (`signals.py:267-290`). The columns sum `tran_amt` of `wm_pri_labelled_transactions` rows with
196 `product_category == 'CASA'` by `in_out_flow`, per CIF and week, **no filter on type or
197 reason**
198 (`casa_cc_transaction.py:98-104`); `tran_dc` D/C only (`casa_cc_merge.py:146-199`). Separating
199 fields: `tran_type`, `tran_sub_type`, `main_tran_type`, `channel_tran_type`,
200 `tran_particular_code(_desc)`, `reason_for_excluding` (comp rows for base CIFs, CC: DDS
201 Rejects/Reversal 100,418 of 167,579, INTERNAL TRANSFER - SELF 7,786, CHARGES 2,635, CHEQUE
202 RETURNS
203 1,549). `EPH-DDS` rejects are 40% of base-CIF CASA transactions in the labelled table (CC
204 95,998 of
205 239,974; RL 21,423 of 76,871, 27.9%).
206
207 Rows with Low, 0 points, no distress, `casa_active` (regex on the type columns):
208
209 | Rows | CC (4,752) | RL (2,521) |
210 |---|---|---|
211 | no transaction found in comp | 129 (2.7%) | 0 |
212 | all administrative | 240 (5.1%) | 5 (0.2%) |
213 | only unclassified | 689 (14.5%) | 395 (15.7%) |
214 | ≥1 customer-initiated | 3,694 (77.7%) | 2,121 (84.1%) |
215 | - only self-transfers | 1,113 (23.4%) | 1,323 (52.5%) |
216 | - ≥1 other than a self-transfer | 2,581 (54.3%) | 798 (31.7%) |
217
218 - **H-A: REJECTED** (CC and RL). Administrative-only rows are 5.1% (CC) and 0.2% (RL). CC:
219   interest
220   249 transactions on ≤169 CIFs (INTEREST PAID 178, INTEREST COLLECTION 71); charges and
221 reversals
222   134 on ≤63 CIFs; RL 8 transactions in all.
223 - Weeks with flow > 0 and no customer-initiated transaction that week: CC 4,940 of 11,228
224   (44.0%),
225   3,071 (27.4%) if unclassified counted; RL 2,586 of 5,819 (44.4%), 1,001 (17.2%).
226 - Control (Unknown rows, WM flag 0): CC 11,900 of 12,096 (98.4%) have no transaction, 173
227   (1.4%)
228   have a customer-initiated one, 145 (1.2%) other than self-transfers. RL: 79 of 362 (21.8%)
229 none,
230   230 (63.5%) customer-initiated, 62 (17.1%) other than self-transfers; the RL mismatch is not
231   explained. What is open is self-transfers (section 9), not fees.
232 - **H-RL1: CONFIRMED** (RL). Of 2,521 rows: a debit to the loan account (counterparty = the
233   account)
234   1,669 (66.2%); a debit within 5% of the EMI 255 (10.1%); of the 2,121 with a
235 customer-initiated
236   transaction, 1,391 (65.6%) have only EMI repayments and same-week top-ups (1,191 if
237 unclassified
238   counts). Without servicing, 1,791 rows (71.0%) would be inactive: 1,196 if unclassified
239 counts.
240   Low 3,566→1,775 to 2,370; Unknown 9.1%→39.1-54.0%.
241 - **H-RL2: REJECTED** (RL). DDS rejects: 225 rows with an event; debit legs all within 5% of
242   the EMI
243   in 2 (0.9%); any non-EMI leg 223 (99.1%); any EMI-like leg 8 (3.6%); leg ÷ EMI p10/p50/p90 =
244 0.22
245   / 0.85 / 5.5 over 22,720 legs. Cheque returns: 254 rows, all EMI-like 3 (1.2%), non-EMI 251;
246 0.99
247   / 4.8 / 23.2 over 684 legs. Legs are at CIF level, EMI is the scored account's; the ratios
248 are
249   leg-weighted.
250 ## 9. Know-how from `ftr_transaction_handling.md` that bears on this
251 - **Self-transfer is a wash, but the run's flag is not the wash flag.** `tran_type` SELF
252   credits are
253   paired same-day, same-amount on 99.7% [T46]; `reason_for_excluding` SELF also holds
254 card-payment
255   debits (6,260 of 15,040 [T46]). `is_self` here uses the reason, so CC's 1,113 includes
256 own-card
257   repayments (comp base CIFs: SELF type 7,107 vs card payments 1,889; RL 6,163 vs 479). CC
258   Low→Unknown is between 1,058 and 2,171; RL's 1,323 is mostly wash.
259 - **DDS rejects are third-party direct debits** (originator mostly another bank: 7,095 of 7,171
260   named debit legs [T46b]), which fits H-RL2. They are distress by construction, so they cannot
261 be
262   in the 0-point, no-distress rows above; for the 1,712 CC / 672 RL Low rows with distress,
263 whether
264   `casa_active` would survive without DDS pairs is not measured. DDS legs are a chronic pattern
265   (median 19 events per CIF in 2 months), so leg-weighted ratios lean on few CIFs.
266 - **Own-loan repayments sit in `MISCELLANEOUS`** (`INSTL_RECOVERY-PL/AL` debits) and match no
267   type
268   pattern; RL comp is 12.2% unclassified (6,419 of 52,527). Part of the 395 RL
269 unclassified-only
270   rows is probably servicing, so 1,196 is a floor and 1,791 a ceiling for H-RL1.
271 - **WM's salary flag counts bonus, incentive, overtime and commission narrations**, applies a
272   500
273   AED monthly floor, and misses salary on code `TP2`. This matches the interior doubles with
274 both
275   neighbours present (43.4% CC / 47.4% RL) and says 14 of the 46 CC weak→stable moves under the
276   window-total rule hold a double month.
277 - A1 liquidity reads balances, so FTR's ~1.8x inflow overstatement (DDS reversal credits, wash,
278   card
279   payments) touches only the gate. No EOS code or narration is documented.
280
281
````

## Transcriber's notes
- Line 21: the arrow chains `106→61→38→38→33` and `114→90→72→72→61` are read as written; they look like a CIF count after each successive filter step. Worth a second look.
- Lines 114-115: the code span `income_m1` starts a continuation line (line 114) and the word `have` sits alone on line 115, as shown in the photos.
- Line 168-170: `## 5. Anchor and stability` follows directly after line 169 with no blank line in between, as shown.
- Lines 193-205 and 233-240: `tran_dc`, `tran_particular_code(_desc)` and the counts for the comp rows (DDS Rejects/Reversal 100,418 of 167,579, etc.) are dense; check them against the source.
- Lines 250-280 (section 9) cross-reference `ftr_transaction_handling.md` (handoff 11); the FTR numbers there (6,260 of 15,040; 7,095 of 7,171; 99.7%) match handoff 11's text.

## Review (A1, 2026-10-28)

**Settled**

- **The engine is right; the inputs are not.** There were 0 recompute mismatches on CC (128,927 rows)
  and RL (23,731 rows), and the mix is stable over 8 months. Every open item below is about an input.
- **S12 (window-total rule) is small and safe:** CC Low→Moderate 21, Moderate→High 8; RL 2. Nothing
  moves down. It ships as decided.
- **S13, bureau EOS: dropped.** Bureau history is too thin to find spikes (CC 3 EOS-like months, RL 10;
  1 row in the window). No rule is needed today; it comes back only if GRR's bureau feed is dense
  enough.
- **H-A (fees as activity): rejected.** Administrative-only rows are 5.1% of the CC 0-point Low rows and
  0.2% of RL. Fees are not what keeps the gate open.
- **H-RL2 (DDS = EMI collections): rejected.** 99% of DDS reject legs are not EMI-sized; they are
  third-party direct debits. DDS stays distress.
- **Bureau salary months parse as MMyyyy** (O62 confirmed). The salary table is usable as is: one
  load per (file, month), and max vs sum across providers changes 0 / 2 CIF-months.
- **Bureau bounce repeats** are 35% (CC) / 43% (RL) of bureau-only flags. This confirms the decided
  "identical repeats are the same bounce" rule.

**Defects (fixed in the CC finish bundle)**

1. **O64: internal salary is dated one month early** for every customer, because `week_number`
   (`yyyyMM0W`) is parsed as a date. Today `income_m1` is never filled. Fixing it moves CC Low→Moderate
   80 and Moderate→High 20 (with S12: 101 / 28); RL 32 / 6 (41 / 8). No Unknown row moves. WM's exact
   decode is needed (R13).
2. **O65: the bureau CIF bridge reaches 0.6% (CC) / 3.4% (RL) of customers.** Bureau salary is cut
   off by the join, not by scarcity. It caps any bureau salary feed GRR delivers, so it must be fixed
   before that feed can help. The upper bound on what bureau salary could reach is the "pull gap":
   86% of CC rows and 39% of RL rows have no income, an alert row and no bureau salary.

**Decisions for the user**

- **D-A1-a, the activity gate (S11 `casa_active`).** The gate today is any CASA inflow or outflow in
  the WM weekly flows, with no filter on type. H-RL1 is confirmed: on RL, 66% of the 0-point Low rows
  have a debit to the loan account, and 1,391 of 2,121 (65.6%) have only EMI repayments and same-week
  top-ups. On CC, 23.4% have only self-transfers (and the "SELF" reason also holds own-card
  repayments). If the gate counted only customer-initiated money movement — no own-loan instalment
  recovery (`INSTL_RECOVERY-PL/AL`, debits to the customer's loan account), no self-transfer wash
  (`tran_type` SELF pairs), no fees or interest:
  - CC Low→Unknown between 1,058 and 2,171 (15–31% of Low);
  - RL Low 89.5% → about 45–60% (1,196–1,791 rows to Unknown).
  This needs a CASA activity feature from the raw CASA table (a primary beside
  `prm_casa_return_events`), because the WM flows cannot separate the types.
- **D-A1-b, the bureau bridge (O65).** Either fix the link now (a Sonnet investigation: which field
  ties an AECB file to a CIF — Emirates ID, the inquiry / request table, `contract_link` keys), or ship
  the finish bundle on the current bridge and fix it with GRR's bureau feed. Either way the engine is
  ready.
- **D-A1-c, DCORE EOSB results** (EOS expected or received: 292 CC rows, 175 RL; mostly Low with no
  liquidity). Ignore, keep as a diagnostic column, or treat as a liquidity signal.

**Open, not blocking:** the RL Unknown control (63.5% of RL Unknown rows have a customer-initiated
CASA transaction although the WM flag is 0) is unexplained. It is moot if D-A1-a moves the gate to
the raw table. Neither the effect of DDS pairs on the 1,712 CC / 672 RL Low rows with distress, nor
the count of salary files the bridge cannot reach, was measured.
