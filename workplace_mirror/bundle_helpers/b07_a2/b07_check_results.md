# Bundle 07 check: PROD results (2026-10-29)

CC (`cc_60_180`): OUTPUT, RULES and REACH completed (3 of 3 nodes, 308 s); handoff 17.
RL (`rl_60_180`): OUTPUT only. The log summary stops when node 2 (DEBIT) starts; RULES, REACH and PRODUCT
have no output yet (handoff 16). Both transcriptions are below the review.

## Review

**1. The reachable drop is fully explained (CC, latest month, 19,292 accounts).** REACH rebuilds
the old rule and then applies each change in turn. Its last step reproduces the engine (0 mismatches).

| Step | Change | Reachable | Non-reachable | Unknown |
|---|---|---|---|---|
| R0 | old rule: contact ever, gone dark on ringing-only days, admin entries count | 62.7% | 7.0% | 30.3% |
| R1 | D-A2-17 failure set (dead lines, LEFT_MSG, …) | 47.6% (−15.1 pt) | 35.3% | 17.1% |
| R2 | admin / IGNORED entries no longer break a failed run | 26.5% (−21.1 pt) | 67.6% | 5.9% |
| R3 | contact must fall in W | 21.0% (−5.5 pt) | 67.6% | 11.5% |

- The largest single move is R2: admin entries such as "Result Not Found", "Follow up" and "E mail Sent" sat between failed call days and reset the run.
- R3 only moves reachable to unknown: 1,065 accounts whose last contact is before W.
- Non-reachable (13,038) splits by last contact:
  - never: 4,961 (25.7%);
  - before W: 4,691 (24.3%);
  - in W, then 3 failed call days: 3,386 (17.6%).
- 85.9% of accounts have 6 or more call days in W, so 3 failed days in a row is a low bar. This is the signed-off rule (`GONE_DARK_DAYS = 3`, checked first). It is the point to put to GRR.

**2. Location (CC).**
- Skip is 8,489 (44.0%):
  - L1, latest evidence foreign: 6,869. Foreign **login** decides 5,772 (29.9% of all accounts).
  - L2, travel rule: 1,620, mostly 3–7 months after the latest UAE evidence.
- In Country 4,638 (24.0%), mostly by UAE login (4,367).
- Unknown 6,165 (32.0%): 94% have UAE evidence, but older than W.
- Card evidence decides little:
  - L1 credit 551, debit 143;
  - L3 credit 123, debit 148.
  - The cards are blocked at 60+ DPD, and the debit rows of these customers almost vanish from 2026-05.
- So Skip rests on foreign logins. v01 found 15.1% of login rows foreign: "mostly real (or VPN)". VPN use is common in the UAE, so it is the open risk for L1.

**3. The debit drop from 2026-05 may not be a data lag.**
- The DEBIT block counts only the latest month's base CIFs, so it cannot tell a lag from behaviour. These customers were current a year ago and are 60–180 DPD now: they missed a payment from about March to June 2026.
- Rows still exist for 2026-09 and 2026-10, which argues against a loading lag.
- The decisive count is `prm_casa_card_transactions` rows by month for **all** CIFs, 2026-01..10.

**4. Trends (Jan → Aug 2026).**

| | CC | RL |
|---|---|---|
| Base | 14,664 → 19,292 | 2,324 → 3,985 |
| Skip | 35.4% → 44.0% | 38.6% → 43.4% |
| Non-reachable | 58.7% → 67.6% | 47.3% → 57.5% |

- Skip is flat at about 36–37% to May, then rises. That matches the debit drop (UAE evidence ages, a later foreign login wins).
- Reachable counts are flat (CC about 4.0–4.4k), so the growth goes to non-reachable.

**5. Old vs new.**
- Old "gone" (6,048) → skip 5,158, non-reachable 5,019: consistent.
- Old "skip" (3,855) → location unknown 2,172, skip only 913. The old rule placed on older or wider evidence (the O59 foreign flag).
- Old "reachable" (682, single-state priority) → reachable only 365.
- Deceased 89 vs 44: Way4 and demographics are new sources. Way4 alone gives 17, Way4 with demographics 13.

**6. RL.**
- Old-only 111 rows: the old output was spell-based and the new one is keyed on the obs base (D5; 3,985 = the A1 base). Expected.
- New: reachable 26.0%, non-reachable 57.5%, skip 43.0%, deceased 29 (old 26).
- RULES, REACH and PRODUCT are still to come.

**Open before GRR:**
- (a) the RL RULES / REACH / PRODUCT blocks;
- (b) the debit count for all CIFs (lag or behaviour);
- (c) whether foreign logins are VPN (foreign-login countries, and UAE logins interleaved within days).

Bundle 06 step 8 and the cleanup are not blocked: the engine is the signed-off rule.

---

# Handoff 17: `tmp_validation/a2_b06_cc_check_run_summary_2026-10-29.md` (photos 71-76), 2026-10-29

## Context for Claude Code
- Source: 6 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-29 ~09:10 Dubai. Tabs: `pipeline_registry.py`, `A3_Payment_Credibility_Stats.txt`, `a2_b06_cc_check_run_summary_2026-10-29.md` (U, active). Terminal panel shows "Brewed for 26s · done 5:06 AM" (not transcribed).
- Title: "A2 Locatability B06 Check, CC Pipeline (run of 2026-10-29)". The CC (`cc_60_180`) b06 check run of the new A2 locatability engine, now successful (compare to handoff 15, where node 10 failed). Companion to handoff 16 (RL). Follows handoffs 1-16.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photos overlap and are merged into source lines 1-283. Photo-to-line map: photo 71 = lines 240-283; photo 72 = lines 199-250; photo 73 = lines 152-203; photo 74 = lines 101-152; photo 75 = lines 51-102; photo 76 = lines 1-54 (the chat order was 240-283 first, then 199-250, 152-203, 101-152, 51-102, 1-54; here the file is merged by line number).
- Markdown tables are shown as in the editor.

---

## `a2_b06_cc_check_run_summary_2026-10-29.md` (lines 1-283)

````
1   # A2 Locatability B06 Check, CC Pipeline (run of 2026-10-29)
2
3   ## Run
4
5   - Command: `kedro run --env=dev --pipeline=crx_cc_a2_locatability_b06_check
6     --nodes compare_crx_cc_a2_b06,describe_crx_cc_a2_b06_rules,explain_crx_cc_a2_b06_reach`
7   - ModelConfigHook: model_id=cc_60_180, dlq_min=4, dlq_max=7, collateral_codes=[WO, SK],
8     target_horizon_months=1 (source=globals_dev.yml)
9   - Datasets loaded: crx_cc_a2_locatability (new), crx_cc_a2_locatability_b06_check (old),
10    crx_cc_obs_base, dcore_prm_followup_outcomes, prm_dcore_account_agreements
11  - Result: 3 of 3 nodes completed, pipeline succeeded in 308.3 sec
12  - Log noise, not a failure: Hadoop/Hive WARNs, and one YARN executor (17) removed from a bad
13    node (lvencdpdta059b) because user "balzsv" was not found there. Spark carried on.
14  - This log has the CC blocks OUTPUT, RULES and REACH. The RL blocks (OUTPUT, RULES, REACH,
15    DEBIT, PRODUCT) are NOT in it. The CC DEBIT block was received earlier.
16  - Next, per the task text: bundle 06 step 8 and its cleanup, only after the review.
17
18  ## Block 1: B06 OUTPUT (compare_a2_outputs), month 2026-08-01
19
20  Row match: new 19292, old 19292, new-only 0, old-only 0. The key sets are identical.
21
22  New a2_state (location__reachability), n and % of 19292:
23
24  | a2_state | n | % |
25  |---|---|---|
26  | deceased | 89 | 0.5 |
27  | in_country__non_reachable | 2613 | 13.5 |
28  | in_country__reachable | 1648 | 8.5 |
29  | in_country__unknown | 369 | 1.9 |
30  | skip__non_reachable | 6114 | 31.7 |
31  | skip__reachable | 1186 | 6.1 |
32  | skip__unknown | 1155 | 6.0 |
33  | unknown__non_reachable | 4290 | 22.2 |
34  | unknown__reachable | 1203 | 6.2 |
35  | unknown__unknown | 625 | 3.2 |
36
37  Old a2_state_v1:
38
39  | state | n | % |
40  |---|---|---|
41  | avoiding | 4678 | 24.2 |
42  | deceased | 44 | 0.2 |
43  | gone | 6048 | 31.3 |
44  | non_cooperative | 2541 | 13.2 |
45  | reachable | 682 | 3.5 |
46  | skip | 3855 | 20.0 |
47  | unknown | 1444 | 7.5 |
48
49  Old state x new location:
50
51  | old state | in_country | skip | unknown |
52  |---|---|---|---|
53  | avoiding | 2135 | 773 | 1770 |
54  | deceased | 5 | 15 | 24 |
55  | gone | 219 | 5158 | 671 |
56  | non_cooperative | 1119 | 482 | 940 |
57  | reachable | 194 | 346 | 142 |
58  | skip | 770 | 913 | 2172 |
59  | unknown | 196 | 802 | 446 |
60
61  Notable: gone -> skip is 5158 (26.7%). skip -> unknown is 2172 (11.3%).
62  avoiding -> in_country is 2135 (11.1%).
63
64  Old state x new reachability:
65
66  | old state | non_reachable | reachable | unknown |
67  |---|---|---|---|
68  | avoiding | 2804 | 1514 | 360 |
69  | deceased | 13 | 6 | 25 |
70  | gone | 5019 | 535 | 494 |
71  | non_cooperative | 1251 | 1186 | 104 |
72  | reachable | 203 | 365 | 114 |
73  | skip | 3270 | 337 | 248 |
74  | unknown | 478 | 100 | 866 |
75
76  Notable: gone -> non_reachable is 5019 (26.0%). The old "reachable" class mostly maps to
77  non_reachable (203) or unknown (114) in the new scheme, and only 365 stay reachable.
78
79  New location_state by month. Percentages in the log are of all 8 months pooled
80  (about 128.9k rows):
81
82  | month | in_country | skip | unknown |
83  |---|---|---|---|
84  | 2026-01 | 4753 | 5186 | 4725 |
85  | 2026-02 | 4531 | 5187 | 4858 |
86  | 2026-03 | 4339 | 5246 | 4870 |
87  | 2026-04 | 4316 | 5396 | 4959 |
88  | 2026-05 | 4830 | 5861 | 5199 |
89  | 2026-06 | 4967 | 6520 | 5495 |
90  | 2026-07 | 4824 | 7652 | 5921 |
91  | 2026-08 | 4638 | 8489 | 6165 |
92
93  Trend: skip rises from 5186 to 8489 (4.0% to 6.6%). Unknown rises from 4725 to 6165.
94  in_country is roughly flat at 4.3k to 5.0k.
95
96  New reachability_state by month:
97
98  | month | non_reachable | reachable | unknown |
99  |---|---|---|---|
100 | 2026-01 | 8605 | 4447 | 1612 |
101 | 2026-02 | 8494 | 4440 | 1642 |
102 | 2026-03 | 9000 | 4039 | 1416 |
103 | 2026-04 | 9386 | 3873 | 1412 |
104 | 2026-05 | 10142 | 4207 | 1541 |
105 | 2026-06 | 10745 | 4260 | 1977 |
106 | 2026-07 | 12151 | 4046 | 2200 |
107 | 2026-08 | 13038 | 4043 | 2211 |
108
109 Trend: non_reachable grows steadily from 8605 to 13038. reachable is flat at about 4.0k to
110 4.4k. unknown is up modestly.
111
112 ## Block 2: B06 RULES (describe_a2_rules)
113
114 location_rule x deciding source (L1: latest foreign, else latest UAE). n and % of 19292:
115
116 | rule | source | n | % |
117 |---|---|---|---|
118 | L1 | credit_card | 551 | 2.9 |
119 | L1 | dcore_note | 403 | 2.1 |
120 | L1 | debit_card | 143 | 0.7 |
121 | L1 | login | 5772 | 29.9 |
122 | L2 | None | 26 | 0.1 |
123 | L2 | credit_card | 966 | 5.0 |
124 | L2 | debit_card | 279 | 1.4 |
125 | L2 | login | 349 | 1.8 |
126 | L3 | credit_card | 123 | 0.6 |
127 | L3 | debit_card | 148 | 0.8 |
128 | L3 | login | 4367 | 22.6 |
129 | L4 | None | 344 | 1.8 |
130 | L4 | credit_card | 2703 | 14.0 |
131 | L4 | debit_card | 688 | 3.6 |
132 | L4 | login | 2430 | 12.6 |
133
134 Totals: L1 6869, L2 1620, L3 4638, L4 6165. L3 total (4638) matches in_country (4638) and
135 L4 total (6165) matches unknown (6165) in the Aug location count. L1 + L2 = 8489, which
136 matches skip (8489).
137
138 location_unknown_reason (6165 rows):
139
140 | reason | n | % |
141 |---|---|---|
142 | domestic_before_window | 5821 | 94.4 |
143 | no_evidence | 344 | 5.6 |
144
145 L2 rows by months since latest UAE evidence (1620 rows, % of L2):
146
147 | months | n | % |
148 |---|---|---|
149 | None | 26 | 1.6 |
150 | 1 | 31 | 1.9 |
151 | 2 | 102 | 6.3 |
152 | 3 | 244 | 15.1 |
153 | 4 | 370 | 22.8 |
154 | 5 | 333 | 20.6 |
155 | 6 | 194 | 12.0 |
156 | 7 | 102 | 6.3 |
157 | 8 | 62 | 3.8 |
158 | 9 | 34 | 2.1 |
159 | 10 | 26 | 1.6 |
160 | 11 | 12 | 0.7 |
161 | 12 | 11 | 0.7 |
162 | 13 | 6 | 0.4 |
163 | 14 | 9 | 0.6 |
164 | 15 | 11 | 0.7 |
165 | 16 | 5 | 0.3 |
166 | 17 | 3 | 0.2 |
167 | 18 | 4 | 0.2 |
168 | 19 | 2 | 0.1 |
169 | 20 | 3 | 0.2 |
170 | 21 | 3 | 0.2 |
171 | 22 | 2 | 0.1 |
172 | 23 | 3 | 0.2 |
173 | 24 | 2 | 0.1 |
174 | 25 | 1 | 0.1 |
175 | 26 | 2 | 0.1 |
176 | 27 | 5 | 0.3 |
177 | 28 | 2 | 0.1 |
178 | 29 | 2 | 0.1 |
179 | 30 | 1 | 0.1 |
180 | 31 | 1 | 0.1 |
181 | 34 | 1 | 0.1 |
182 | 36 | 3 | 0.2 |
183 | 39 | 1 | 0.1 |
184 | 41 | 1 | 0.1 |
185
186 Peak is at 4 to 5 months; about 78% is within 3 to 7 months. There is a thin tail to
187 41 months.
188
189 reachability_state x reason:
190
191 | state | reason | n | % |
192 |---|---|---|---|
193 | non_reachable | None | 13038 | 67.6 |
194 | reachable | None | 4043 | 21.0 |
195 | unknown | no_contact_in_window | 1938 | 10.0 |
196 | unknown | no_dcore_record | 273 | 1.4 |
197
198 reachability_state x last contact (in W / before W / never):
199
200 | state | last contact | n | % |
201 |---|---|---|---|
202 | non_reachable | before_W | 4691 | 24.3 |
203 | non_reachable | in_W | 3386 | 17.6 |
204 | non_reachable | never | 4961 | 25.7 |
205 | reachable | in_W | 4043 | 21.0 |
206 | unknown | before_W | 1065 | 5.5 |
207 | unknown | never | 1146 | 5.9 |
208
209 Call days in the window:
210
211 | call days | n | % |
212 |---|---|---|
213 | 0 | 743 | 3.9 |
214 | 1-2 | 446 | 2.3 |
215 | 3-5 | 1539 | 8.0 |
216 | 6+ | 16564 | 85.9 |
217
218 Skip-trace status ever (diagnostic) x location_state:
219
220 | skip-trace ever | in_country | skip | unknown |
221 |---|---|---|---|
222 | False | 2910 (15.1%) | 4881 (25.3%) | 3252 (16.9%) |
223 | True | 1728 (9.0%) | 3608 (18.7%) | 2913 (15.1%) |
224
225 Skip-trace history does not separate the location states cleanly. Among accounts with
226 skip-trace True, in_country is 1728 and skip is 3608.
227
228 deceased_source (89 deceased):
229
230 | source | n | % |
231 |---|---|---|
232 | dcore | 37 | 41.6 |
233 | dcore,demographics | 2 | 2.2 |
234 | dcore,way4 | 8 | 9.0 |
235 | dcore,way4,demographics | 9 | 10.1 |
236 | demographics | 3 | 3.4 |
237 | way4 | 17 | 19.1 |
238 | way4,demographics | 13 | 14.6 |
239
240 ## Block 3: B06 REACH (explain_reachability), rungs R0 to R3
241
242 | rung | non_reachable | reachable | unknown |
243 |---|---|---|---|
244 | R0 | 1344 (7.0%) | 12097 (62.7%) | 5851 (30.3%) |
245 | R1 | 6807 (35.3%) | 9182 (47.6%) | 3303 (17.1%) |
246 | R2 | 13038 (67.6%) | 5108 (26.5%) | 1146 (5.9%) |
247 | R3 | 13038 (67.6%) | 4043 (21.0%) | 2211 (11.5%) |
248
249 Moves between rungs (n and % of the moved rows):
250
251 | move | from -> to | n | % |
252 |---|---|---|---|
253 | R0 -> R1 | reachable -> non_reachable | 2915 | 53.4 |
254 | R0 -> R1 | unknown -> non_reachable | 2548 | 46.6 |
255 | R1 -> R2 | reachable -> non_reachable | 4074 | 65.4 |
256 | R1 -> R2 | unknown -> non_reachable | 2157 | 34.6 |
257 | R2 -> R3 | reachable -> unknown | 1065 | 100.0 |
258
259 R0 -> R3 (all changes):
260
261 | R0 | R3 | n | % |
262 |---|---|---|---|
263 | non_reachable | non_reachable | 1344 | 7.0 |
264 | reachable | non_reachable | 6989 | 36.2 |
265 | reachable | reachable | 4043 | 21.0 |
266 | reachable | unknown | 1065 | 5.5 |
267 | unknown | non_reachable | 4705 | 24.4 |
268 | unknown | unknown | 1146 | 5.9 |
269
270 Check: R3 vs the engine's reachability_state gives 0 mismatches. R3 is the final rung and
271 reproduces the engine.
272
273 Reading: R0 to R1 and R1 to R2 only push rows toward non_reachable; R2 to R3 only moves
274 1065 rows from reachable to unknown (no contact in the window, but a contact before it).
275 The rungs add up to the 1065 "unknown / before_W" rows in Block 2.
276
277 ## Cross-block checks (consistent)
278
279 - Reachability totals agree across blocks: 13038 non_reachable, 4043 reachable, 2211 unknown.
280 - Location totals agree across blocks: in_country 4638, skip 8489, unknown 6165.
281 - Deceased: 89 new, against 44 in the old schema.
282 - Not in this log: the RL blocks, and any step-8 or cleanup output.
283
````

## Notes on specific spots
- Photo boundaries were merged by line number; every line 1-283 is covered. Lines 55-56 and 118-132 came from two overlapping photos each and agree.
- Consistency checks I ran on the transcription: new a2_state counts sum to 19,292; old a2_state_v1 sums to 19,292; location totals per month match L1-L4 in line 134; R2 non_reachable+reachable+unknown = 13,038+5,108+1,146 = 19,292; R3 = 13,038+4,043+2,211 = 19,292; deceased sources sum to 89.
- Line 197 area: line 189-196 the reason table sums to 13,038+4,043+1,938+273 = 19,292.
- Line 246: R2 values read as 13038 / 5108 / 1146 (the top of photo 71 cuts line 246 partly; the same line is fully visible in photo 72).
- Line 134: "L1 6869" is L1 total (551+403+143+5772 = 6,869). L2 1620 includes the 26 None row.
- Lines 145-184 (L2 months table) sums to 1,620 rows.

---

# Handoff 16: `tmp_validation/a2_b06_rl_log_summary_20261029.md` (photos 69-70), 2026-10-29

## Context for Claude Code
- Source: 2 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-29 ~09:10 Dubai. Tabs: `pipeline_registry.py`, `A3_Payment_Credibility_Stats.txt`, `a2_b06_cc_check_run_summary_2026-10-29.md` (U), `a2_b06_rl_log_summary_20261029.md` (U, active). Both summary files are untracked.
- Title: "SUMMARY OF KEDRO LOG: RL A2 LOCATABILITY B06 CHECK (run on 29 Oct 2026)". It is a summary of the RL (`rl_60_180`) b06 check run of the new A2 locatability engine. Companion to handoff 17 (the CC run summary of the same date) and follows handoffs 1-15.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify the numbers against the real file.
- Photos overlap and are merged into source lines 1-104. Photo-to-line map: photo 69 = lines 1-54; photo 70 = lines 53-104 (the photo order in chat was lines 53-104 first, then 1-54).
- The whole body sits inside a fenced block (opening ``` on line 3, closing ``` on line 103), shown as in the editor. The terminal panel under the editor shows only "Brewed for 26s · done 5:06 AM" and is not transcribed.
- Many columns are aligned with spaces in the file. Alignment below is approximate.

---

## `a2_b06_rl_log_summary_20261029.md` (lines 1-104)

````
1   # SUMMARY OF KEDRO LOG: RL A2 LOCATABILITY B06 CHECK (run on 29 Oct 2026)
2
3   ```
4   1. RUN SETUP
5   ------------------------------------------------------------------------------------------
6   Command : kedro run --env=dev --pipeline=crx_rl_a2_locatability_b06_check
7             --nodes compare_crx_rl_a2_b06, describe_crx_rl_a2_b06_rules,
8                     explain_crx_rl_a2_b06_reach, describe_crx_rl_a2_b06_debit,
9                     split_crx_rl_a2_b06_product
10  Host    : lvenaacaai402b (repo retail.collections.risk_profiling)
11  Config  : model_id=rl_60_180, dlq_min=3, dlq_max=6, collateral_codes=[WO, SK],
12            target_horizon_months=1 (source: globals_dev.yml)
13  Spark   : "medium" env. Log started 04:59:05 and the Spark hook was up at 05:00:01.
14  Runner  : sequential, synchronous load/save.
15  Warnings: SparkUI moved from port 4040 to 4041. libhadoop not loadable. Several HiveConf keys
16            unknown. spark.yarn.jars/archive not set. All are routine environment noise.
17
18  2. EXECUTION PROGRESS
19  ------------------------------------------------------------------------------------------
20  Inputs loaded for node 1: crx_rl_a2_locatability (new schema), then
21                            crx_rl_a2_locatability_b06_check (old single-state schema).
22  Node 1 compare_crx_rl_a2_b06 (compare_a2_outputs): COMPLETED at about 05:01:13. This is 1 of 5.
23  Node 2 describe_crx_rl_a2_b06_debit (describe_debit_evidence): STARTED.
24    Inputs loaded: crx_rl_obs_base and prm_casa_card_transactions.
25  The log stops here. Nodes 2 to 5 have no results yet.
26  Nodes 3 to 5 have not started: rules, reach, product split.
27  The log never shows node 2 finishing, so I can't tell whether it succeeded.
28
29  3. B06 COMPARISON OUTPUT, SNAPSHOT MONTH 2026-08-01
30  ------------------------------------------------------------------------------------------
31  Row counts : new 3,985, old 4,096, new-only 0, old-only 111.
32               The new output is a strict subset of old, and 111 old rows have no new counterpart.
33               The old-vs-new crosstabs below cover only the 3,985 matched rows.
34
35  New a2_state (location x reachability, plus deceased):
36    skip__non_reachable       1,135  28.5%    unknown__non_reachable   592  14.9%
37    in_country__non_reach.      564  14.2%    in_country__reachable    407  10.2%
38    skip__reachable             320   8.0%    unknown__reachable       308   7.7%
39    unknown__unknown            263   6.6%    skip__unknown            260   6.5%
40    in_country__unknown         107   2.7%    deceased                  29   0.7%
41
42  Old a2_state_v1:
43    avoiding 1,376 (33.6%)    skip 816 (19.9%)          gone 760 (18.6%)
44    non_cooperative 454 (11.1%)   reachable 381 (9.3%)   unknown 283 (6.9%)
45    deceased 26 (0.6%)
46
47  4. OLD STATE vs NEW DIMENSIONS (matched rows)
48  ------------------------------------------------------------------------------------------
49  Old state       New location (in_country / skip / unknown)   New reach. (non_r / reach / unk)
50  avoiding         588 / 311 / 433                              664 / 494 / 174
51  deceased           2 /  10 /  11                                1 /   8 /  14
52  gone              48 / 574 / 119                              581 /  69 /  91
53  non_cooperative  187 / 126 / 130                              176 / 232 /  35
54  reachable         62 / 188 / 120                              101 / 159 / 110
55  skip             163 / 346 / 289                              646 /  65 /  87
56  unknown           30 / 173 /  75                              123 /  16 / 139
57
58  Readings from the crosstabs:
59  - "gone" lines up well with the new dimensions. About 77% are location=skip and about 78% are
60    non_reachable.
61  - Old "skip" mostly agrees on reachability (about 81% non_reachable) but only 43% are
62    location=skip. Only 346 of the 798 matched rows agree.
63  - "avoiding" is the broadest bucket and spreads across all new values. It is split roughly
64    evenly between non_reachable and reachable and is mostly in_country or unknown on location.
65  - Old "reachable" is only partly confirmed. 159 of 370 are reachable in the new schema,
66    101 are non_reachable and 110 are unknown.
67  - Old "non_cooperative" is 52% reachable in the new schema.
68  - Old "deceased" (26) maps to 29 new deceased. The 1 and 8 in the deceased row's reachability
69    cells show the deceased flag does not force a reachability value.
70
71  5. NEW LOCATION AND REACHABILITY BY MONTH (Jan to Aug 2026)
72  ------------------------------------------------------------------------------------------
73  The percentages printed in the log are shares of all months pooled (about 23.7k rows).
74  The table below uses counts and per-month shares, which I computed from the log's counts.
75
76  Month    Rows   in_country   skip   unknown | non_reach   reach   unknown
77  Jan-26   2,324      805       898      621  |   1,099      791      434
78  Feb-26   2,213      717       882      614  |   1,043      755      415
79  Mar-26   2,218      709       888      621  |   1,161      729      328
80  Apr-26   2,661      889     1,034      738  |   1,477      793      391
81  May-26   3,096      962     1,159      975  |   1,697      945      454
82  Jun-26   3,514    1,059     1,344    1,111  |   1,939    1,000      575
83  Jul-26   3,728    1,014     1,577    1,137  |   2,031    1,064      633
84  Aug-26   3,985    1,080     1,728    1,177  |   2,292    1,043      650
85
86  Trends, Jan to Aug:
87  - The population grew from 2,324 to 3,985 rows, up about 71%.
88  - location=skip rose from 38.6% to 43.4% of rows. in_country fell from 34.6% to 27.1%.
89    unknown rose from 26.7% to 29.5%.
90  - non_reachable rose from 47.3% to 57.5% of rows. reachable fell from 34.0% to 26.2%.
91    unknown reachability fell from 18.7% to 16.3%.
92  - Reachable counts stayed roughly flat at 730 to 1,060. The growth is almost entirely
93    non_reachable and skip.
94
95  6. POINTS TO FOLLOW UP
96  ------------------------------------------------------------------------------------------
97  - Find out why 111 old-schema rows have no new row in 2026-08. The new schema has no new-only
98    rows, so the old table may carry extra customers.
99  - The reachability trend (non_reachable up about 10 points) may be real portfolio ageing or a
100   feature artefact. Compare it with the REACH explanation node when that output arrives.
101 - Wait for nodes 2 to 5 (debit evidence, rules, reach explanation, product split) and check
102   that node 2 finishes without error. The log was cut off at its start.
103 ```
104
````

## Notes on specific spots
- Lines 36-40: the two-column layout is as shown (left column then right column per line); spacing is approximate.
- Lines 43-45: the old state line layout is approximate.
- Line 62: "Only 346 of the 798 matched rows agree" is read as written. Row 55 above gives skip total 163+346+289 = 798, so the figures are consistent.
- Line 65: "159 of 370" (reachable row sums to 62+188+120 = 370). Consistent.
- Line 68-69: the 1 and 8 refer to the deceased row's reach cells (1 / 8 / 14).
- Lines 77-84: the month table is as shown. Sums per row: Jan 805+898+621 = 2,324 and Aug 1,080+1,728+1,177 = 3,985, matching Rows.
- Line 100: "REACH explanation node" refers to `explain_crx_rl_a2_b06_reach`.
- Line 102: "The log was cut off at its start" is read as written (probably "at its end"; the file text says "start").
