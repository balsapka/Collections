# `docs/context/reference/ftr_transaction_handling.md` (workplace, 2026-10-28)

The workplace reference for reading raw `comp_financial_tran_repos_dly` (FTR), from the T46 / T46b
PROD EDA. Transcribed from photos (`pics/claude_code_handoff_11.md`, photos 42-52), OCR quality:
re-check counts, code lists and regexes (rules 11, 12) against the real file before relying on them.
Line numbers are the editor's. Used by A1 (distress, activity gate) and A2 (debit evidence).

````
1   # `comp_financial_tran_repos_dly` (FTR) — row handling reference
2
3   Reference for any pipeline or snippet that reads raw FTR (CASA transactions). The table
4   holds many bookkeeping rows that are not customer money movement, and some of those rows
5   are exactly the distress signals we want (DDS rejects, cheque bounces). Handle them as
6   **separate lanes**. Final version of the FTR EDA (T46, T46b).
7
8   **Evidence tags used below**
9   - **[T46]** PROD run, `results/T46_ftr_row_taxonomy_cc_60_180_20261028.json`: `cc_60_180`
10    spine CIFs, 20% seeded CIF sample, `edp_load_date` 2025-11-01 to 2025-12-31, 233,970
11    rows.
12  - **[T46b]** PROD run, `results/T46b_ftr_open_items_cc_60_180_20261028.json`: same sample
13    for checks A-C; check E is a 5% CIF sample over 2025-01 to 2026-10.
14  - **[profile]** schema profile of 2026-05-04: null % and distinct counts are full-table;
15    value counts come from a 100k block-clustered sample (vocabulary only).
16  - **[code]** verified by running the regexes or reading the code (this repo, WM, Feature
17    Store).
18  - **[inferred]** read from narration text, not from a data dictionary.
19
20  Counts describe those samples and periods; rely on the patterns. The type vocabulary
21  originates from the bank's ODS transaction-type mapping (Feature Store,
22  `services.feature_store.core`, `workflow/ftr`).
23
24  ---
25
26  ## At a glance
27
28  1. A plain credit or debit total is **not** income or spend: only ~55% of credit AED is
29     genuine movement (section 4).
30  2. Classify every row into one **lane**: signal, card, noise, group-internal, economic,
31     ambiguous. Select per use (rule 1).
32  3. **DDS rejects** are insufficient-funds returns of direct debits originated by other
33     institutions. Find them by `reason_for_excluding`, count one event per
34     `(cif_id, tran_id, tran_date)` (section 3).
35  4. **`reason_for_excluding` is not a noise filter.** It flags own-card payments (75% of
36     card-payment rows) and POS refunds; use explicit value lists (section 2).
37  5. **Salary** follows the WM rule: credit, code list or narration regex (rule 12).
38  6. **Exclude CIF `13339117`** (NI POS sink) and **`tran_type = INTERNAL TRANSFER - SELF`**
39     (wash) from economic measures (rules 7, 8).
40  7. Activity features must **exclude DDS reject rows** (rule 9).
41
42  ---
43
44  ## 1. Table facts
45
46  - 2.42B rows, 124 columns, daily snapshot (`edp_load_date`, 1,081 distinct) [profile].
47  - **Rows are legs, not transactions.** `(tran_id, part_tran_srl_num, tran_date)` was
48    unique on all 233,970 rows [T46]: no reload duplicates in that window. Keep the key
49    dedup (latest `edp_load_date`) as a safeguard for other periods.
50  - **`tran_id` is not an event id.** 123 DDS `tran_id`s span two CIFs and two dates
51    (4 rows) [T46b]. An event key is `(cif_id, tran_id, tran_date)`.
52  - `tran_dc` is `C`/`D` only. Amounts are **unsigned**, with no nulls, zeros, negatives
53    or outliers (max 4.5M AED) in 2025-11/12; the 22-month check found no month with an
54    amount above 1e9 or a negative [T46, T46b]. Direction comes from `tran_dc`. The 1e14
55    maximum in the profile was not reproduced; keep a cheap outlier guard anyway.
56  - **Use `actual_tran_amt_aed`.** It equals `tran_amt_aed` on 99.96% of rows; the 91 that
57    differ are mostly foreign-currency rows plus ~55 AED rows [T46].
58  - **`foracid` is the own-account id** (0% null) [profile] and works for pairing legs
59    [T46]. RL-A1-18's "no account-number column" statement is wrong.
60  - **`tran_time` is populated** on DDS rows (0% null) [T46b], so legs can be ordered
61    within a day.
62  - **Row mix is dominated by POS**: 52% of rows but 4% of AED [T46].
63  - **`tran_particular_code_desc`** is the bank's own description of the code (233
64    distinct, 4.4% null) [profile], e.g. `SALARY CREDIT`, `SB-SALARY PAYMENTS`,
65    `POS-PURCHASE`, `POS-REFUNDS/RET`, `IPP Customer Credit`, `BULK PAYMENT-`,
66    `CREDIT CARD PAYMENT`. The section 5 dictionary was built from type and narration
67    rather than from this column; prefer the column where they differ.
68
69  ## 2. The bank's flag: `reason_for_excluding`
70
71  17.6% of rows carry a value in 2025-11/12 [T46] (13.7% over the full table [profile]).
72  Ten values are current:
73
74  - `DDS Rejects/Reversal` (16,008 rows): **matched pairs** of `OUTWARD REMITTANCE` (D) +
75    `INWARD REMITTANCE` (C) with the same amount, plus the `- SUBSIDIARIES` variants,
76    `INTERNAL TRANSFER - SELF` and `- OTHERS`. See section 3.
77  - `INTERNAL TRANSFER - SELF` (15,040): `INTERNAL TRANSFER - SELF` (8,780) **and
78    `CREDIT CARD PAYMENTS` debits (6,260)**.
79  - `CHARGES` (6,584): `CHARGES` (plus 11 POS debits).
80  - `SUBSIDIARIES EXCLUSION` (1,250): `- SUBSIDIARIES` remittances (502), card payments
81    (747).
82  - `RETURNS` (802): **POS refunds** (801 POS credits, code `948`) and 1 cash withdrawal.
83  - `INTERNAL TRANSFER - LIV` (539): `INTERNAL TRANSFER - OTHERS` (492), card payments (47   [cut off at the right edge]
84  - `CHEQUE RETURNS` (376): `CHEQUE RETURNS`, 188 D + 188 C legs.
85  - `CANCELLED` (291): cancelled remittance pairs (150 D + 141 C).
86  - `REVERSAL` (168): reversal credits on POS (122), cash deposit (30), inward remittance
87    (9) and `tran_type` `REVERSAL` (7).
88  - `FEES` (40): `FEES`.
89
90  **The vocabulary is stable since mid-2025.** Over 22 months [T46b] the legacy values
91  `Status Deleted in Finacle` (January 2025 only), `NA` (January-May 2025) and an empty
92  string (February-June 2025) disappear. They matter only for windows before July 2025.
93  Map NULL, `NA` and the empty string to "no reason". The profile's 18 distinct values
94  against the 13 seen here are probably case variants and rare values.
95
96  What this means:
97  - **`RETURNS` is not a bounce.** It is POS refunds. `signals.py` already keeps it out of
98    `DISTRESS_RETURN_REASONS`; `prm_casa_return_events` carries it but does not use it.
99  - **The reason flag is a superset of the noise types, not a clean noise filter.** 75% of
100   `CREDIT CARD PAYMENTS` rows (7,054 of 9,441) carry `SELF`/`SUBSIDIARIES`/`LIV`: own-CASA
101   payments to the customer's own card. Filtering on reason deletes the card-repayment
102   signal (A3).
103 - 31% of `INWARD REMITTANCE` credit rows and 29% of its AED (27.0M of 94.3M) are DDS
104   reversal credits [T46]. Unfiltered, they read as remittance inflow.
105
106 ## 3. The DDS reject signal
107
108 `DDS Rejects/Reversal` is found by reason, never by `tran_type` or by code alone.
109
110 - **What it is [inferred]:** the credit leg's narration is `DDR- RETURN - INSUFFICIENT
111   FUNDS` (7,421 of 8,004 credit legs, code `004`). The debit leg reads
112   `DDR-<ref>; OIC NAME-<bank>` (code `445`): a direct debit **originated by another
113   institution** that was returned for insufficient funds. The named originator is
114   `DUBAI ISLAMIC BANK` on 7,095 debit legs and `EMIRATES ISLAMIC BANK` (a group entity)
115   on 76 [T46b]. The originator is a potential "external creditor" field.
116 - **Event grain:** one event = two legs (D + C), same CIF, account and date, same amount,
117   net zero. 7,746 of 7,874 `tran_id` events are such clean pairs [T46b]. About 8,000
118   events in the sample.
119 - **Concentrated, repeated, small population.** 250 CIFs (2.9% of 8,529 sampled spine
120   CIFs) hold all events. Among them the median is 19 events in the two months, 135 CIFs
121   have 11 or more, and the maximum is 167 [T46b]. Event amount: median 1.8k AED, 90th
122   percentile 6.6k, 99th 26.5k. Read it as a chronic failing direct debit, not a one-off.
123 - **It swamps FTR activity once customers go delinquent.** In the spine cohort, DDS rows
124   rise from ~1% of all FTR rows (early 2025) to ~50% (mid-2026) while total monthly rows
125   fall about 8x (5% CIF sample, calendar months, not months since delinquency) [T46b].
126   The account is largely dry apart from failing debits [inferred].
127 - **Code `445`/`004` is shared:** about 7% of those codes' rows are `INTERNAL
128   TRANSFER - SELF` rows. Identify DDS by reason (or narration), not by code.
129 - **Related fees [inferred]:** `CHARGES` rows with `DDS` (208) or `RETURN`/`REJECT`
130   (475) in the narration are likely returned-item fees. A candidate companion signal.
131 - **Cheque returns:** 188 events over 153 CIFs (1.8%), mostly one event per CIF (132);
132   narration `RET.CHQ. NO: # :CA INSUFFICIENT FU...` (code `126`, also `040`, `127`).
133   23 CIFs have both a DDS reject and a cheque return [T46b].
134
135 ## 4. Row classes (lane per observed value)
136
137 - **Signal — DDS rejects, cheque returns.** See section 3.
138 - **Not a signal — `RETURNS`** (POS refunds, single credit leg, code `948`).
139 - **Noise — fees, interest.** `CHARGES`, `FEES`, `INTEREST PAID` (credit),
140   `INTEREST COLLECTION` (debit).
141 - **Noise — wash.** `INTERNAL TRANSFER - SELF` (see rule 8).
142 - **Noise — reversal / cancel.** Reason `REVERSAL`, `CANCELLED`; `tran_type` `REVERSAL`.
143 - **Group-internal.** `- SUBSIDIARIES` types, reason `SUBSIDIARIES EXCLUSION`, reason
144   `INTERNAL TRANSFER - LIV`. Exclude by default; decide per use.
145 - **Genuine movement.** `INWARD/OUTWARD REMITTANCE`, `INTERNAL TRANSFER - OTHERS`,
146   `CASH DEPOSIT` / `CASH WITHDRAWALS`, `INWARD CLEARING` (debit), `OUTWARD CLEARING`
147   (credit), `BILL PAYMENTS` (debit only).
148 - **Card.** `POS TRANSACTIONS` (spend), `CREDIT CARD PAYMENTS` (repayment, debit; A3).
149   Classify **before** any reason-based noise rule.
150 - **Own-loan repayment.** `MISCELLANEOUS` rows whose narration starts
151   `INSTL_RECOVERY-PL-AC` (personal loan) or `-AL-AC` (auto loan) are installment
152   recovery debits: 1,344 PL + 282 AL debits [T46b, inferred]. Treat as repayment
153   behaviour, not income. The matching credits (945 PL, 231 AL) are unexplained.
154 - **Ambiguous — rest of `MISCELLANEOUS`.** 6,357 rows but 15.6% of AED. The remainder:
155   `LOAN RECOVERY FROM : #` credits (419), `TO - #; AUTHCODE-VPAUTHCODE=#` credits (434),
156   `DEFERMENT FEE-PL` + VAT debits (85 each), numeric-only narrations (1,490 debits), and
157   84 large credits on code `945` (AED 11.6M, median 45k). No counterparty on any row,
158   and only 8.6% of credits pair same-day [T46b]. `MC/DD`, `MC/DD-ISSUE`,
159   `STANDING INSTRUCTIONS` are tiny. Keep out of economic measures.
160
161 Lane sizes, 2025-11/12 sample, with noise assigned before card [T46]:
162
163 | Lane | Row share | AED share | Credit AED share |
164 |---|---:|---:|---:|
165 | card | 52.4% | 4.6% | 0.0% |
166 | economic | 26.8% | 46.0% | 54.6% |
167 | noise | 9.9% | 18.1% | 15.3% |
168 | signal (incl. POS refunds) | 7.3% | 14.5% | 15.2% |
169 | ambiguous | 2.7% | 15.6% | 14.1% |
170 | group-internal | 0.9% | 1.0% | 0.7% |
171
172 **A plain credit total overstates economic inflow by up to ~1.8x.** Assigning card
173 payments before the reason rules (rule 3) shifts ~7,054 rows (AED 15.7M) from noise /
174 group-internal into card.
175
176 ## 5. `tran_particular_code` dictionary (type + narration evidence) [T46b]
177
178 - **POS:** `447`, `433` spend (debit); `948` refund (credit, reason `RETURNS`); `434`
179   POS reversal (credit, reason `REVERSAL`).
180 - **Salary: a code list, not one code** (rule 12). Two codes on WM's list appear here:
181   `507` (2,198 rows, 100% credit, `INWARD REMITTANCE`, 95% narrate `SALARY FROM
182   <employer> FOR THE MONTH <m>`, median 6.5k AED) and `506` (407 rows, median 7.0k AED,
183   but only 44 narrate salary). `586` / `587` are a few small `MISCELLANEOUS` credits.
184   Salary-worded narrations also sit on `TP2` (208 rows, `INTERNAL TRANSFER - OTHERS`),
185   which is not on WM's list. Of 2,462 salary-narration rows, 89% are `507`. The other
186   WM codes (`505`, `503`, `585`, `588`, `085`-`088`, `328`, `828`) are not among the 60
187   most frequent codes in the window.
188 - **DDS pair:** `445` (debit) / `004` (credit). Not salary.
189 - **Inward credits:** `101` (instant payments), `605` (money-transfer app TT refs; has
190   the `CANCELLED` rows), `945`, `506`, `963`. **Outward debits:** `120` (the bulk),
191   `121`, `102`, `621`, `993`.
192 - **Mobile banking:** `958` credit / `458` debit, including own-account transfers.
193 - **Card payments:** `405` (debit; 6,260 flagged `SELF`), `905`.
194 - **Cash:** `508` deposit (smart deposit machine); `426`, `012` withdrawals; `927`
195   deposit reversal.
196 - **Cheque:** `126`, `040`, `127` returns; `125` outward clearing (credit); `055` inward
197   clearing (debit); `050` in-house cheque transfer.
198 - **Charges / fees:** `418`, `918`, `620`, `011`, `170`, `VAT`, `420` (charges; `418`
199   is VAT at ~1 AED median); `866`, `361` (fees).
200 - **Utilities:** `291` (telecom), `292` (DEWA), `475` (Salik), `486`, `471`.
201 - **Auto-save micro transfers:** `LV95` credit / `LV3` debit, `SET AND FORGET RULE`,
202   median 20 AED, reason `SELF`. Pure noise for income and spend.
203 - **No code (3.6% of rows, AED 88M):** loan installment recovery, charges and some
204   self-transfers.
205
206 ## 6. Rules for our pipelines
207
208 1. **Two lanes, one scan.** Classify each row once, then select per use:
209    - *Signal lane*: DDS rejects by reason; cheque returns by reason / type. **Count
210      events, not rows or amounts**: one event per `(cif_id, tran_id, tran_date)`, and
211      use one leg's amount. Keep POS refunds out.
212    - *Economic lane* (inflow, salary, ability, outflow): allow-list of genuine types, with
213      signal, noise, group-internal and ambiguous rows removed. Otherwise a bounced
214      item's reversal credit reads as income.
215 2. **Use explicit value lists.** Never test `reason_for_excluding` with `IS NULL`; map
216    NULL, `NA` and the empty string to "no reason". Do not drop a whole group wholesale.
217 3. **Precedence: signal, then card, then reason-based noise, then type-based noise, then
218    economic.** Card payments must survive the reason flag (section 2).
219 4. **Match `tran_type` by exact value, not regex.** A regex that strips spaces only and
220    tests `INTERNAL TRANSFER(?!SELF)` misclassifies the hyphenated SELF and SUBSIDIARIES
221    variants as ordinary internal transfers [code]. If a regex is unavoidable, normalise
222    whitespace **and** hyphens first, in one helper, with hyphenated unit tests.
223 5. **Dedup on `(tran_id, part_tran_srl_num, tran_date)`**, latest `edp_load_date`. Never
224    a whole-row `distinct()`: it removes real same-day, same-amount transactions [code].
225 6. **Window on `tran_date`**, with a bounded `edp_load_date` range (both ends) for
226    partition pruning, and scope to the spine / CIFs first (R20).
227 7. **Exclude CIF `13339117` explicitly.** It is the non-customer NI POS sink: 7.27M rows
228    and AED 193B in the 2-month window, roughly 6x the whole sampled CC 60-180 population
229    extrapolated to 100% (~1.2M) [T46].
230 8. **Self-transfer wash (RL-A1-18).** `tran_type = 'INTERNAL TRANSFER - SELF'` is a clean
231    wash flag [T46]: 99.7% of its credit rows (4,144 of 4,158) have a same-CIF, same-day,
232    same-amount debit; `counter_party_cif_id` equals the own CIF on 100% of them (0%
233    null). By `foracid`, 76% of pairs run between different accounts of the CIF and 24%
234    within one. Control, `INTERNAL TRANSFER - OTHERS`: 3.2% paired, 0% own-CIF
235    counterparty, so the flag is specific. **Do not use reason `INTERNAL TRANSFER -
236    SELF` as the wash flag**: it also covers card payments.
237 9. **Activity features must exclude DDS reject rows.** Otherwise a dry, delinquent
238    customer looks active (section 3). Use them as a separate signal.
239 10. **Calendar:** UAE weekend is Friday-Saturday before 2022-01-01 and Saturday-Sunday
240     from that date.
241 11. **Country text is free text** with typos (`UAE`, `U.A.E`, `United Arab Emirates`,
242     `AE`, `UNITER ARAB EMIRATES`). Normalise before any domestic / international or
243     travel logic. The Feature Store pattern:
244     `(?i)\b(?:U\.?\s*-?\s*)A\.?\s*-?\s*E\.?\b|\b(?:U\w*\s+)?A\w*\s+E\w*\b`.
245     A NULL country is neither domestic nor international under it.
246 12. **Salary: use the WM ENBD rule, not one code and not `channel_tran_type`.** WM
247     (`wealth_management`, `conf/enbd/parameters/parameters.yml: salary_from_casa_txns`,
248     `income.py`) flags a row as salary when it is a **credit**, the code is **not** in
249     `947`, `LV3`, `LV4`, and **either**
250     (a) the code is in `505, 506, 507, 503, 585, 586, 587, 588, 085, 086, 087, 088, 328,
251     828`, **or** (b) the narration, upper-cased with spaces removed, matches
252     `SALARY|PAYROLL|SALAR|B/O|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK|
253     SALERY|SALRY` or a month-name + `SAL` form (`JANSAL` ... `DECSAL`) [code]. It then
254     sums per CIF and month after FX conversion, with a 500 AED minimum per month
255     (1,000 to 3,000,000 is the valid range used downstream). The spaced regex variants
256     (`JAN SAL`) can never match because spaces are removed first. `B/O`, `SALAR`,
257     `BONUS` and `COMMISSION` are broad.
258     WM runs it on raw Finacle `hist_tran_dtl_table` (narration from `tran_particular`,
259     `tran_particular_2`, `remarks`, `tran_rmks`), not on FTR. FTR shares the code space
260     (`507` and `506` are on the list and carry salary narrations), but has different
261     narration columns: use `tran_narration_1/2`, `sender_to_recvr_info`,
262     `tran_particular_code_desc` (WM's own FTR job concatenates these). Do not treat
263     `004`, `101`, `958` or `508` as salary: DDS returns, instant payments, mobile
264     banking and cash deposits. `channel_tran_type` mirrors `tran_type` and shows no
265     `SALARY` in 22 months [T46b].
266     Our `cc_departure_signature` and `rl_departure_signature` nodes already apply this
267     rule (same code lists). Differences: the narration regex omits `B/O` and the
268     month-name forms, and only `tran_narration_1` is searched [code]. Both narrow it.
269 13. **Report the unclassified share** whenever a new FTR-derived feature is added. Only 8
270     of 233,970 rows were unclassified [T46], but new types would silently become income
271     or vanish. The `tran_type` list is stable over 22 months (25 values) [T46b].
272
273 ## 7. Gotchas when reading old FTR-derived numbers
274
275 - Totals built from `tran_dc` alone include fees, interest, reversals, DDS reversal
276   credits, wash pairs and card payments. They are not income or spend.
277 - Per-type amount columns that default to 0 instead of NULL change what count and
278   null-rate metrics mean.
279 - Round-amount features (`amount % 100 = 0`) include zero amounts unless guarded.
280 - Transaction counts for delinquent customers are inflated by failing direct debits.
281
282 ## 8. Known limitations of this EDA
283
284 Nothing here blocks use of the rules above; these are the edges of the evidence.
285
286 - **One variant and sample.** All findings come from `cc_60_180` spine CIFs. The table is
287   shared, so table-level patterns (vocabulary, amounts, keys, codes) should hold for the
288   other models; lane sizes and DDS frequency will differ by population.
289 - **Narration-based readings are inferred.** The DDS meaning (other institutions' direct
290   debits returned for insufficient funds), the `INSTL_RECOVERY` loan repayments and the
291   code dictionary come from narration patterns, not from a data dictionary. The
292   `tran_particular_code_desc` column was not examined.
293 - **Salary rule not run on FTR.** WM's rule is documented from its code; its FTR narration
294   mapping is unvalidated.
295 - **DDS frequency is not cut by delinquency.** The spine (`account_id`, `cif_id`,
296   `observation_date`) carries no DPD, so the DDS trend is by calendar month, not months
297   since delinquency.
298 - **Unexplained items.** `INSTL_RECOVERY` credit legs (945 PL / 231 AL), `VPAUTHCODE`
299   credits, numeric-only `MISCELLANEOUS` narrations, and the 84 large credits on code
300   `945`. All sit in the ambiguous lane and are excluded from economic measures.
301 - **Originator names** were seen only as 40-character masked patterns; distinct
302   originating institutions per CIF were not extracted.
303 - **Free-text fields** (narration, country) vary; patterns above are a sample.
304
````

## Transcriber's notes
- Line 54 (`1e14`) and line 53 (`1e9`): read as written; the photos show `1e9` and `1e14`.
- Line 244 (Feature Store country regex): transcribed from photo 50; check it against the original character by character, since a single missed backslash changes the pattern.
- Lines 252-253 (salary narration regex): the alternation list `SALARY|PAYROLL|SALAR|B/O|INCENTIVE|BONUS|OVERTIME|COMMISSION|COMISS|SALBNK|SALABNK|SALERY|SALRY` wraps across two source lines after `SALABNK|`; the join is as shown.
- Line 250: the code list `505, 506, 507, 503, 585, 586, 587, 588, 085, 086, 087, 088, 328, 828` wraps after `328,`.
- Section 4 table: the column alignment row is `|---|---:|---:|---:|`, as shown.
