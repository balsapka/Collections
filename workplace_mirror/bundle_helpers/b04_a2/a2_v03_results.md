# A2 v03 — PROD results (cc_60_180 + rl_60_180, 2026-10-28)

`tmp_validation/a2_v03/summary.md`, written by the workplace Sonnet from `results_{cc,rl}_60_180.json`.
Transcribed from photos by a chat session (`pics/claude_code_handoff_13.md`, photos 63-68), OCR quality;
line numbers are the editor's. Cells are CC | RL. The README inventory was not photographed. The
review and the decisions are at the end. FTR row-handling know-how the Sonnet cites:
`bundle_helpers/ftr_transaction_handling.md`.

## `tmp_validation/a2_v03/summary.md`

````
1   # A2 v03 — in-person debit-card rows of `comp_financial_tran_repos_dly` (PROD runs of 2026-10-28)
2
3   `cc_60_180`: 19,292 base rows / 18,731 CIFs; `rl_60_180`: 3,985 / 3,608; base 2026-08-31;
4   `errors` = {} in both.
5   Cells are CC | RL. H1–H4, H5 hygiene, H10: last 12 months; H5 keys, H6–H8: 36; **H2 read 3 months,
6   H9 12** (run arguments).
7   The rule below is **provisional**: ATM-only plausibility, the Offline era and 36-month reason values
8   were not measured.
9
10  ## Verdicts
11
12  - **H1 — R2 as drafted is wrong; Machine is the card-present value.**
13    - No `Offline` row in the last 12 months. POS debit rows: Machine 969,953 | 306,993, Online
14      449,889 | 162,120,
15      NULL 88,260 | 31,710. Every ATM row has NULL type (143,904 | 45,258).
16    - `Offline` shows only before ~2025-08-31: a rule needing POS=Offline finds 0 | 0 UAE base rows in
17      12m,
18      8,454 | 2,646 in 36m. Same meaning as Machine is consistent (login conflict 27% vs 26%) but
19      unproven.
20    - Online catches e-commerce (UAE Online top merchants: Smart Dubai Government 24,399, Talabat.com
21      22,273,
22      Noon Minutes 21,873, Tabby, E& app, Careem) but is not an MCC filter: 33.0% | 38.3% of Online
23      rows have
24      grocery / fuel / restaurant / pharmacy / transport MCCs.
25    - Leak into Machine is small: remote MCC 0.25% | 0.26%, strong e-com narration (ECOM, WWW, .COM)
26      0.32% | 0.34%,
27      vs Online 15.2% | 14.5% and 14.4% | 17.7%.
28    - NULL-type POS rows (5.3% | 5.8% of debit card rows): no merchant fields, 34% | 39% e-com
29      narration,
30      49,875 | 18,816 with a foreign narration country. Drop.
31    - Top foreign-Machine merchants: NOT IN JSON (the list was keyed on Offline).
32  - **H2 — best field is `merchant_type_desc`; none beats it.**
33    - Fill on card rows 87.3% | 84.7% (Machine and Online 100%, POS NULL and ATM 0%).
34    - `terminal_id` 99.4% | 98.6% incl. Online, `delivery_channel_id` = EFT on all POS: no signal.
35      `tran_channel_id` 0%.
36    - `module_id` = DCI on Machine 28.0% | 23%, ATM 88% | 75%, Online 0%: precise but covers a
37      minority.
38    - No card-number column found (13-19 digit shape: `counter_party_acct_num` 27.7% | 24.5%,
39      `merchant_id` 22.3% | 18.6%; not shown to be PANs).
40    - H2 counts are 3 months (28,668 | 8,386 card rows): use fill shares only.
41  - **H3 — ATM can be placed, by narration.**
42    - ATM debit rows 143,915 | 45,262. Withdrawals (`tran_particular_code_desc` DR ATM TRANSACTION +
43      UAE SWITCH WDL)
44      84,251 | 27,462 (58.5% | 60.7%); fees/enquiry/mePay 59,650 | 17,788.
45    - Country fill: narration code (`:XX#` or trailing ` XX`) 95.1% | 94.6%;
46      `counter_party_bank_cntry` 76.1% | 76.9%;
47      `terminal_cntry` 73.0% | 73.3% (UAE and GCC only: SA 462, OM 314, QA 42, BH 19, KW 3);
48      `merchant_country` 0.01%; currency AED on 100%.
49    - Withdrawals placed by narration 83,689 (99.3%) | 27,213 (99.1%); 100% with the
50      counter-party-bank fallback.
51    - Abroad by narration: 3,322 (3.9%) | 1,287 (4.7%). Narration says abroad while bank country does
52      not: 5 | 0.
53  - **H4 — one UAE spelling.**
54    - `UNITED ARAB EMIRATES` 1,339,363 | 437,505 rows; no other spelling, no ≤3-char code.
55    - NULL: Machine 19 of 969,953, Online 0, POS-NULL-type and ATM 100%. Currency cannot check country
56      (all AED).
57    - POS narration country vs `merchant_country` contradict on 197 of 1,419,823 | 79 of 469,094
58      (0.014% | 0.017%).
59  - **H5 — hygiene.**
60    - Card keys (tran_id, part_tran_srl_num, tran_date): 6,749,364 | 2,457,356, **0 copies**;
61      non-card 54 | 59 keys with copies. `edp_load_date` = `tran_date` on 100%.
62    - The same (tran_id, part_tran_srl_num) recurs on other dates (1,026,682 | 174,326): keep the date
63      in the key.
64    - Credits on card channels 12,468 | 4,554: `POS-REFUNDS/RET` (reason RETURNS) 10,943, `POS-PURCH
65      REV` (REVERSAL) 503,
66      POS SETTLEMENT 344, ATM reversal/deposit. `tran_dc = D` drops them.
67    - Debit card rows with a reason: 57,005 of 1,652,017 (3.4%) | 17,037 of 546,085 (3.1%), almost all
68      **CHARGES = ATM fees** (56,858 | 16,990). The 3 repo return values catch only 2 | 4.
69    - Debits with a later matching credit: 6,623 (0.40%) | 1,958 (0.36%).
70    - No declined authorisations (`channel_status` NULL on all; 53 | 15 decline-word rows). Amounts
71      all positive.
72  - **H6 — use `value_date`.**
73    - `value_date` = narration swipe date on 100% of parsed rows (POS all, ATM 80%).
74    - `tran_date` is later. Foreign POS: 2d 70.2% | 70.1%, 1d 14.0% | 14.6%, 3d 12.6% | 12.1%.
75      UAE POS: 0d 26% | 24%, 1d 32%, 2d 39% | 41%. Foreign ATM 2d 48% | 51%; UAE ATM 0d 92% | 93%.
76    - `pstd_date` ≈ `tran_date`; `edp_load_date` = `tran_date`; `etl_load_date` = +1d (99.6%).
77    - With `value_date` the draft's foreign-day UAE-login conflict drops 14.1% → 11.5% same day and
78      25.9% → 23.3% within ±1d (RL: 15.9 → 12.1 and 29.0 → 26.0).
79  - **H7 — R2 and R4 both earn their place.**
80    - Foreign CIF-days with a UAE login same day / ±1d (in brackets: UAE CIF-days with a foreign login
81      ±1d):
82      - draft 14.1% / 25.9% (6.6%) | 15.9% / 29.0% (6.6%)
83      - R2 dropped 23.0% / 39.5% (7.4%) | 24.2% / 42.0% (7.5%)
84      - R4 dropped 17.5% / 31.3% (6.6%) | 19.3% / 34.2% (6.7%)
85      - online-only control 30.9% / 52.7% (9.6%) | 30.8% / 53.1% (9.6%)
86      - R1+R3 only 27.0% / 46.5% | 27.5% / 47.7%
87    - The days R2 / R4 remove conflict at ±1d on 54% / 57% | 56% / 58%, like the control.
88    - On draft foreign days, 70% | 69% of same-day logins are foreign (control 22%).
89    - Draft conflict stays high; roaming and trip-boundary days are legitimate, so the floor is
90      unknown.
91  - **H8 — what it decides (draft = Machine POS).**
92    - Any in-person row in 3 / 12 / 36m, UAE: 693 (3.6%) / 8,915 (46.2%) / 11,453 (59.4%) |
93      195 (4.9%) / 2,449 (61.5%) / 3,133 (78.6%).
94    - Abroad: 87 (0.5%) / 1,955 (10.1%) / 5,016 (26.0%) | 47 (1.2%) / 671 (16.8%) / 1,739 (43.6%).
95    - Debit holds the latest foreign date on 667 (3.5%) | 241 (6.0%) rows (login 11,713 | 2,567,
96      credit card 2,081 | 219, DCORE note 498 | 20), and the latest UAE date on 2,578 (13.4%) | 800
97      (20.1%)
98      (login 10,226 | 2,133, credit card 6,654 | 586).
99    - It changes the state of 229 (1.2%) | 178 (4.5%) rows, mostly UNKNOWN→UAE (97 | 151).
100     The loose R1+R3 rule flips 320 | 45 UAE⇔FOREIGN vs 124 | 18.
101   - **RL 620 vs 411:** v02's t7c used 36 months of debit events, t7b 12. Replica: 317 vs 222, with
102     95 (30%) older
103     than 12m (v02: 34%); CC 303 vs 298. Level not reproduced (credit-card evidence is now present
104     for RL).
105 - **H9 — sizing, all CIFs, 12 months (2025-09 → 2026-08).**
106   - Rows per month 67.2-74.8M; card rows 37.2-43.5M; card debit 36.6-41.7M.
107   - Draft in-person 21.4-25.1M (UAE 20.5-23.9M, abroad 0.69-1.65M); R1+R3 only 31.8-36.6M.
108     Aug-2026: 73.6M / 41.3M / 23.8M.
109   - Earliest `tran_date` with card rows and the partition column: NOT IN JSON
110     (2025-08-31 is the window floor; the plan line is cut).
111   - Lookback 36 → 24 → 12m, UNKNOWN: 427 → 587 → 1,226 | 605 → 649 → 744.
112   - Rows changing state vs 36m: 24m 160 (0.8%), 12m 799 (4.1%) | 44 (1.1%), 139 (3.5%).
113 - **H10 — credit cards.**
114   - Purchase debits flagged international: 178,465 of 1,674,454 (10.7%) | 42,002 of 307,390 (13.7%).
115     Cash debits: 5,202 of 19,668 | 1,014 of 3,476.
116   - Rows with no `DOMESTIC=` key are fees, IPP and uncategorised: only 22 | 3 purchase debits and 4
117     | 2 C2 debits,
118     none the sole UAE evidence of a base row.
119   - Payment credits are flagged international (220,476 | 35,473): restrict to purchase/cash debits.
120   - Base rows In Country on card C2 alone (after foreign override):
121     3m 377 (2.0%) | 202 (5.1%); 6m 7,116 (36.9%) | 959 (24.1%); 12m 13,023 (67.5%) | 1,623 (40.7%).
122
123 ## Recommended rule (provisional)
124
125 - **POS:** `channel_desc` = 'Point of Sale'
126   - and `merchant_type_desc` in ('Machine','Offline')
127   - and `tran_dc` = 'D'
128   - and `reason_for_excluding` not in (CHARGES, FEES, REVERSAL, CANCELLED, RETURNS, CHEQUE RETURNS,
129     DDS Rejects/Reversal, Status Deleted in Finacle); NULL, '' and 'NA' = no reason
130   - and `cast(merchant_category as int)` not in 5815-5818, 4814, 4816, 4899, 5964-5969, 5734, 7372
131   - Where: `merchant_country` = 'UNITED ARAB EMIRATES' → UAE; other filled → ABROAD; NULL → unplaced
132     (19 rows).
133 - **ATM:** `channel_desc` = 'ATM Transactions'
134   - and `tran_dc` = 'D'
135   - and `tran_particular_code_desc` in ('DR ATM TRANSACTION','UAE SWITCH WDL')
136   - and the same reason list
137   - Where: country code of `tran_narration_1` (`:XX#` or trailing ` XX`; AE = UAE, else ABROAD),
138     then `counter_party_bank_cntry`.
139 - **Date:** `value_date` (fall back to `tran_date`).
140 - **Dedup:** key (tran_id, part_tran_srl_num, tran_date), latest `edp_load_date`; never
141   `distinct()`.
142 - **Drop:** CIF 13339117, credits, ATM fee/enquiry/mePay rows, Online and NULL-type rows.
143   Refund-matched debits stay (the purchase happened).
144 - **Keep:** cif_id, foracid, tran_id, part_tran_srl_num, tran_date, value_date, pstd_date,
145   edp_load_date,
146   channel_desc, merchant_type_desc, tran_dc, tran_type, tran_particular_code_desc,
147   reason_for_excluding,
148   merchant_category, merchant_country, merchant_name, terminal_cntry, counter_party_bank_cntry,
149   tran_amt_aed, actual_tran_amt_aed, derived country code, location class, location source;
150   partition `event_month` (month of `tran_date`).
151 - **Cannot be told:**
152   - NULL-type POS rows 88,260 | 31,710 (5.3% | 5.8% of debit card rows).
153   - Online rows 449,889 | 162,120 (27.2% | 29.7%), by design.
154   - ATM non-withdrawal rows 59,650 | 17,788.
155   - 19 Machine rows without a country.
156   - ATM place beyond country (the city is only in the narration).
157
158 ## What `ftr_transaction_handling.md` adds to these results
159
160 - **Reason handling (rules 2, 3; §2):** never test `IS NULL`. NULL / `NA` / '' mean none, and
161   `Status Deleted in Finacle` (Jan 2025) is a deleted row. My strict variant used `IS NULL`, so its
162   36m numbers
163   (the Offline era, before July 2025) may be understated. The 36-month card-row reason values are
164   NOT IN JSON.
165 - **Confirmed on card rows:** RETURNS = POS refunds (credit leg), REVERSAL = POS reversal credits,
166   CHARGES = fees (§2);
167   key uniqueness (§1, rule 5); amounts unsigned and positive; RL behaves like CC (§8 open item).
168 - **CIF 13339117** (non-customer NI POS sink, ~3.6M rows a month): base CIFs exclude it, so H1–H8
169   are unaffected.
170   H9 includes it, overstating card rows by up to ~9% (not quantifiable from the JSON).
171   Use `actual_tran_amt_aed` (§1) and keep both amount columns.
172 - **Country text (rule 11):** one spelling here, but the primary should normalise. My loose regex
173   would call a typo
174   such as UNITER ARAB EMIRATES abroad; none appears in the top 32 values.
175 - **Dictionary (§5):** add the card descriptions above (`SERVICE CHGS-ATM`, `UAE SWITCH ENQUIRY
176   CHRG`,
177   `MEPAY TRANSFER TO`, `POS SETTLEMENT`, `ATM TRAN-REVERSAL`).
178 - **Open before building:** one small re-run (Machine/Offline era split by month, ATM-only
179   plausibility,
180   36-month reason values, foreign Machine merchants, H9 on all 36 months excluding CIF 13339117).
181
````

## Review and decisions (2026-10-28)

**Decided (user, 2026-10-28):**
- **D-A2-19 debit evidence = the recommended rule, as is.** POS: `channel_desc` = Point of Sale,
  `merchant_type_desc` in (Machine, Offline), debit, reason not in the list (NULL / '' / NA = none),
  MCC not remote; place = `merchant_country`. ATM: `channel_desc` = ATM Transactions, debit,
  `tran_particular_code_desc` in (DR ATM TRANSACTION, UAE SWITCH WDL), same reasons; place = the
  narration country code (`:XX#` or a trailing ` XX`; AE = UAE), else `counter_party_bank_cntry`.
  Date `value_date` (else `tran_date`); dedup on the key, latest `edp_load_date`; CIF 13339117
  dropped. Online and NULL-type POS rows are not evidence (they still count as travel purchases).
- **No re-run.** The Sonnet's "open before building" items (Offline era by month, ATM-only
  plausibility, 36-month reason values, foreign Machine merchants, H9 over 36 months) change no
  code: Offline stays in the filter with Machine's meaning, the reason list is explicit (so the
  `IS NULL` caveat does not apply). The bundle's check logs in-person debit rows by month and type.
- **Primary scope (Claude, user delegated):** `prm_casa_card_transactions` keeps only rows that can
  be evidence — in-person candidates (POS Machine / Offline, ATM withdrawals) and travel purchases
  on any card channel — for all CIFs, 36 months, raw columns kept; the reason and remote-MCC lists
  apply in the location feature.
- **RL Way4 is wired** (user): RL reads `prm_transaction`, `prm_contract`, `prm_client` (credit-card
  evidence, Way4 deceased).

**Settled by the numbers:**
- H1: `Offline` is gone since ~2025-08; `Machine` is the card-present value now. Online is
  e-commerce but not an MCC filter, so the remote-MCC list stays as a second guard.
- H3: ATM withdrawals can be placed (99% by narration, 4–5% abroad) — the v02 caveat "debit ATM rows
  carry no country" is replaced.
- H4: one UAE spelling in `merchant_country`; the primary still normalises (FTR rule 11).
- H5: no key copies on card rows; credits are refunds / reversals (dropped by debit-only).
- H6: `value_date` = the swipe date; foreign POS posts 1–3 days later.
- H8: debit holds the latest foreign date on 3.5% | 6.0% of rows and the latest UAE date on
  13.4% | 20.1%; it moves 1.2% | 4.5% of states, mostly Unknown → In Country.
- H10: payment credits carry `is_international` → credit-card evidence uses purchase / cash debits
  only (`direction = -1`, `txn_category` in purchase, cash). Rows without a `DOMESTIC=` key are fees /
  IPP (22 | 3 purchase debits): negligible.
- RL 620 vs 411 (v02) explained: 36 vs 12 months of debit events.
