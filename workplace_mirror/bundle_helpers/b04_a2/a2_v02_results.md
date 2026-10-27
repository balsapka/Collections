# A2 v02 — PROD results (cc_60_180 + rl_60_180, 2026-10-27)

`tmp_validation/a2_v02/summary.md` and the part A inventory of its `README.md`, written by the
workplace Sonnet from `results_{cc,rl}_60_180.json`. Transcribed from photos by a chat session
(`pics/claude_code_handoff_10.md`, photos 38–41), OCR quality; line numbers are the transcriber's,
not the editor's. 180+ not run. The review is at the end.

## `tmp_validation/a2_v02/summary.md` (lines 1-44)

````
1   # A2 v02 — travel rule, in-person card use, debit route (results of 2026-10-27)
2
3   `cc_60_180`: 19,292 rows / 18,731 CIFs; `rl_60_180`: 3,985 / 3,608; base 2026-08-31, W = 3 months. 180+ not run.
4   Both JSONs: `errors` = {} (no table failed). Not in a JSON: t7a for RL ("not applicable to RL (no card)"), t7c RL credit card
5   and `cifs_with_card_evidence_from_only_one_source` (null), the (a)-vs-(b) "Skip under both" overlap (only each route's n), the
6   disagreement between country fields (only `merchant_country` was tested), and the `candidate_field_value_counts` fill rate of TRANS_LOCATION.
7
8   ## 1. What "abroad" means per card source
9   - **Way4 credit card — verdict: `DOMESTIC=N` = merchant outside the UAE (online included); NOT proven "customer abroad".** The JSON cannot settle presence.
10    - `DOMESTIC=N` 425,507 rows; `Y` 1,550,780; absent/blank 2,734,294 (817,049 of them with NULL currency). N = 21.5% of flagged rows, 9.0% of all.
11    - N share by MCC: 6011 (ATM) 5,568 of 28,245 = 19.7%; travel MCC 6,180 of 16,302 = 37.9%. The currency cross-check is void: `trans_currency == "AED"` matched 0 rows (no
12      AED anywhere, so the column is not coded as the string AED).
13    - `FF=PHYSICAL_CARD` sits on all 1,976,287 flagged rows (N included): not card-present. `DT_ENTMODE` is blank on all 425,507 N rows. 65.4% of base rows (12,613) have an
14      N row in 12 months (C3).
15    - Extra aggregate that would settle it: `DOMESTIC` x `trans_currency` value counts (top 10) for the 12 months, plus N rows by `source_channel`.
16  - **Debit card / CASA — verdict: `merchant_country` != "UNITED ARAB EMIRATES" (country name) is a usable "abroad", where populated.**
17    - Route (a) populated 1,439,358 of 2,395,539 rows (60.1%) CC, 472,460 of 782,764 (60.4%) RL; abroad = 81,525 (5.7% of populated) CC, 31,879 (6.7%) RL.
18    - 39.9% of rows have no country. D4 (ATM only) found 0 abroad rows in every route, so ATM rows probably carry no country — `merchant_country` null share by
19      `channel_desc` would confirm.
20
21  ## 2. Key numbers (t1-t6)
22  | | CC | RL |
23  |---|---|---|
24  | t1 baseline (GAP=SILENCE=1m): L1 Skip / L3 In Country / L4 Unknown / L2 Skip | 12,245 (63.5%) / 3,920 / 2,800 / 327 (1.7%) | 1,556 (39.0%) / 1,086 / 1,288 / 55 (1.4%) |
25  | L2 comes from | Unknown 298, In Country 29 | Unknown 53, In Country 2 |
26  | t2 L2 rows, GAP 14d / 1m / 2m / 3m at SILENCE 1m | 206 / 327 / 531 / 724 | 40 / 55 / 85 / 114 |
27  | t2 SILENCE 1m / 2m / 3m / 6m at GAP 1m | 327 / 326 / 303 / 53 | 55 / 55 / 54 / 18 |
28  | t3 CIFs with a travel purchase in 36m; last one 0-3 months old | 66.3%; 138 | 59.5%; 30 |
29  | t4 known leavers (L1); with a ticket / no ticket | 4,765; 761 / 3,825 (179 in no bucket) | 1,537; 160 / 1,336 (41 in no bucket) |
30  | t5 alt A / alt B (share of base) | 720 (3.7%) / 5,119 (26.5%) | 91 (2.3%) / 666 (16.7%) |
31  | t6 L2 rows by months since last UAE evidence: 2 / 3 / 4-6 / 7-12 / 12+ | 23 / 72 / 218 / 12 / 0 (1 "never", 1 at 1m) | 1 / 8 / 34 / 6 / 6 |
32  | t6 answered outbound call in last 3m | 22.0% | 54.5% |
33  - t1 is run with every foreign card event as evidence (README: channel not filtered), so the 63.5% CC L1 is inflated by C3-type rows; with the chosen options t7c
34    attributes the latest foreign date to only 6,493 CC rows.
35  - t3 "in_person" is just "not online": 100,008 vs 257 online events (CC), 16,446 vs 101 (RL) — it separates nothing.
36
37  ## 3. Verdicts
38  - **L2 volume:** moves 327 CC rows (1.7%; 298 from Unknown, 29 from In Country) and 55 RL rows (1.4%; 53 / 2) to Skip. Small either way.
39  - **GAP / SILENCE (t4):** share of ticketed known leavers' lags within GAP — CC: ≤30d 61%, ≤60d 75%, ≤90d 82%, ≤180d 91%; RL: 64% / 79% / 84% / 91%. L3 stayers: ≤30d 0.6% / 0.7%, ≤90d 5.4% / 4.3%. **GAP = 3 months** reaches the 80% mark; the baseline 1 month covers ~62%. Only 16% (CC) / 10% (RL) of known leavers have a ticket at all, so L2 can only reach a minority.
40  - **t2 steepness:** GAP is steep: 327 → 531 → 724 CC (+62%, +121%), 55 → 85 → 114 RL. SILENCE is flat to 3m (CC -7%, RL -2%) and collapses at 6m (-84%, -67%). The In Country rows L2 overrides: GAP 3m/SILENCE 1m 128 CC, 17 RL; at SILENCE 3m only 11 / 2. Pair that the data supports: GAP 3m + SILENCE 3m = 607 CC (3.1%), 99 RL (2.5%), without overriding L3. (t4 gives no SILENCE calibration; the 3m SILENCE choice rests on t2 and the L3 window.)
41  - **t5:** A (old rule) and L2 are different sets: overlap 39 of 720 CC, 15 of 91 RL. B contains most of L2 (298 of 327 CC, 47 of 55 RL) but is 16x / 12x larger (4,821 / 619 rows only in B) — materially broader than L2.
42  - **t6:** CC looks like leavers (302 of 327 L2 rows, 92%, have ≥ 3 months since the last UAE evidence, 70% ≥ 4; only 22% answered a call). RL does not clearly (54.5% answered), although roaming is possible; 55 rows is a thin base.
43  - **Credit-card option: C2.** C1 (TRANS_LOCATION not ONLINE) attributes 587 rows against 12,613 for C3, and "ONLINE" occurs on 9 N rows, so the field is empty on most N rows: not usable. C2 = 243 rows (193 L1 Skips); C1 and C2 overlap in 113 (C2 adds 130, misses 474). C4 (ATM) 47 (38 Skips). C3 adds 12,370 rows over C2 (7,495 more L1 Skips) — online foreign shopping.
44  - **Debit-card option: D1** (POS + ATM channels, `channel_desc` 0% null in route (a)): 292 CC rows (108 L1 Skips) / 411 RL (68). D3 (all rows) = D1 exactly, adds 0; D2 is a strict subset (51 / 73); D4 = 0 (see section 1).
45  - **Debit route: (a), the raw CASA table.** Coverage of base CIFs: CC 57.5% (a) vs 55.2% (b); RL 75.6% vs 73.3%. Card use identified in 79.0% / 78.5% of rows vs 32.6% / 45.1% for (b), whose `channel_desc` is NULL on 3,081,182 of 5,576,373 CC rows (55%) and 487,534 RL rows (37%). Country populated in 25.6% / 36.0% of (b) rows vs 60.1% / 60.4% of (a). D1 rows: 292 vs 289 CC, 411 vs 373 RL. (b) also covers only WM segments PRB/PSB/PB. Trust `merchant_country`; `counter_party_bank_cntry` was not tested (a wire-bank country per the inventory).
46  - **t7c, what each source adds to the logins (rows whose latest foreign date comes from it):** CC — login 5,270 (27.3%), DCORE note 338 (1.8%), credit card 588 (3.0%), debit 297 (1.5%); card-only: 587 credit-only, 296 debit-only. RL — login 2,370 (59.5%), debit 620 (15.6%), DCORE note 19 (0.5%).
47  - **Open:** RL debit is 620 in t7c but 411 for D1 route (a) in t7b — not explained by the JSON.
````

## `tmp_validation/a2_v02/README.md` (lines 1-92)

````
1   # A2 v02 — travel rule / card-present inventory + run steps
2
3   ## A. Inventory (read-only; under 50 lines)
4
5   **A1 Credit cards (Way4).** `prm_transaction` (`catalog_outputs.yml:429-431`, builder
6   `prm_cc.py:350-386`): `txn_id` (=`primary_entry_idt`), `contract_id`, `observation_date`(←
7   `banking_date`), `card_id`, `txn_category`, `txn_amount[_aed]`, `is_international`, `direction`,
8   `txn_code`, `merchant_category_code`, `merchant`/`txn_city`/`txn_country`/`txn_description`,
9   `source_channel` (`flows.py:42-129`) — **no `add_info`, no currency column survive**. Scoping
10  confirmed: CC scopes via `data_spine_contracts_way4` (DLQ-filtered, `spine_builders.py:350-375`);
11  RL via `*.cc_scope`→`build_rl_scoped_cc_billing_spine` (`spine_builders.py:448-473`, "no DLQ
12  filter, scoped to RL CIFs" — **all** of the CIF's cards). Both write the same templated path,
13  so `catalog.load("prm_transaction")` is correct for either. `raw_transaction`
14  (`catalog_raw_way4.yml:35-38`, full schema `data/08_reporting/schema_intelligence/credit_card/
15  tables/raw_transaction.md`). `add_info` keys parsed anywhere in `src/`: only `DOMESTIC=(.)`
16  (`prm_cc.py:375-381`, byte-identical in `cc_raw_extract/nodes.py:104-112` — "N"→int(1),
17  else→domestic(0); **not** country-code-based despite `flows.py:54,97-99`'s docstring — R19
18  doc/code mismatch). Cash advances: `txn_code` in `TXN_CATEGORIES["cash"]` (`config.py:95-96`),
19  **not** MCC 6011 — no MCC-based cash logic exists. **Card-present: NONE decoded in-code** —
20  raw `add_info`/`oper_type_add_info` carry unparsed candidates: `FF=PHYSICAL_CARD`,
21  `DT_ENTMODE=07` (POS entry mode), `TRANS_LOCATION=...` (free text, online vs. physical),
22  `MTH_ATM_POS_REPORT`/`MTH_PROFILE=POS`/`ATM`. `source_channel` survives but is an unmapped raw
23  code with no decode anywhere — its "ATM/POS/Online" docstring is aspirational. **Abroad: only
24  `DOMESTIC=`** — verdict pending t7a's crosstab (96% flagged vs. 28% travel-MCC, implausible).
25
26  **A2(a) Raw CASA `comp_financial_tran_repos_dly`** (`catalog_raw_dpl.yml:9-14`, 124-col
27  schema). Current nodes (`cc_departure_signature/nodes.py:791-873`;
28  `rl_departure_signature/nodes.py:257-304,522-601`) select only `cif_id`/`tran_date`/
29  `tran_amt_aed`/`tran_dc`/`tran_particular_code`/`tran_narration_1` (+`merchant_category` in
30  RL's travel node) — **unused**: `channel_desc`, `merchant_country`, `merchant_type_desc`,
31  `counter_party_bank_cntry`. Debit-use-at-all: `channel_desc` (0% null — `Point of Sale`/`ATM
32  Transactions`/`Online or Mobile Banking`/`Branch`/`Cheque`/remittance) cleanly separates card
33  use from transfers/cheques/fees. **Card-present: `merchant_type_desc`** — exactly 3 values
34  `Offline`/`Machine`/`Online` (POS/ATM/e-commerce), 49.3% null (populated only on card rows);
35  never read anywhere — `channel_desc` (0% null, same POS/ATM values) used for D1 instead, fully
36  populated. **Abroad: `merchant_country`** — full country NAME (`UNITED ARAB EMIRATES`, not
37  ISO), 49.3% null, never referenced in `src/`. `counter_party_bank_cntry` is a *bank* country on
38  wire rows, not card rows — wrong field for card location.
39
40  **A2(b) Sibling datasets.** `wm_pri_labelled_transactions` (`catalog_casa_plus_ftr.yml:28-31`,
41  `week_number`-partitioned, per-txn `tran_date` survives). Renamed on ingest
42  (`casa_cc_merge.py:148-195`): `merchant_category→mcc_code`, `merchant_country→mcc_country`,
43  `merchant_type_desc→mcc_type`, `channel_desc` kept verbatim — same card-present/abroad
44  semantics as A2(a). **Coverage caveat:** filtered upstream to `segment_desc.isin(["PRB","PSB",
45  "PB"])` — Private/Priority/Premium Banking only, **not** general retail (`parameters.yml:1304`).
46  `fea_casa_cc_international_spend_by_cif`/`fea_days_since_last_international_case_cc_txns`
47  (`casa_cc_transaction.py:182-266`): `cif_id×week_number` weekly aggregate, no per-txn date;
48  "international" = IBAN/counterparty-bank-based, **not** `mcc_country`; `mcc_type` never
49  consumed — **card-present: NONE FOUND**. `product_category:"CASA"` excludes CC txns. Neither
50  exists in `retail.feature_space` under these names (its own `casa_cc_transactions.py` selects
51  `merchant_type_desc`/`channel_desc` but never consumes them either).
52
53  ## Dates
54
55  Per the task spec: never move `dcore_observation_spine`/`prm_contract` dates to month-end,
56  and never join them to the base on an exact/truncated date. This snippet always compares
57  "event/snapshot date **on or before** the observation date" (`F.col("event_date") <=
58  F.col("observation_date")`, then take the latest such row per `(cif_id, observation_date)` —
59  see `_latest_on_or_before`). No `last_day()`/`trunc()` is applied to DCORE or `prm_contract`
60  dates anywhere in this snippet.
61
62  ## Evidence definitions (exactly which source/column/filter)
63
64  - **UAE evidence**: login from UAE (`stg_digital_login.is_foreign_login==0` AND not both
65    `countrylocation`/`countrycode` null) OR in-person card/CASA use in UAE that is not a
66    travel purchase (`add_info.DOMESTIC==Y` for CC / `merchant_country=="UNITED ARAB EMIRATES"`
67    for CASA, both AND NOT travel).
68  - **Foreign evidence**: login abroad (`is_foreign_login==1`) OR in-person card/CASA use
69    abroad (`DOMESTIC==N` / `merchant_country!="UNITED ARAB EMIRATES"`, any in-person/online —
70    channel is NOT filtered here, only for the C/D "in-person" options) OR a DCORE departure
71    note (`result_name` in `{LEFT THE COUNTRY, OUT OF COUNTRY, KSA/NATHEER-CROSSING FINAL EXIT
72    VISA}`, `cc_a2_locatability/constants.py::_DEPARTURE_RESULT_NAMES`).
73  - **Travel purchase**: `merchant_category_code`/`merchant_category` in MCC 3000-3299, 4411,
74    4511, 4722, OR `txn_description`/`tran_narration_1` matches `_TRAVEL_KEYWORDS_RE` (duplicated
75    from `cc_departure_signature/nodes.py:77,83-86`), any channel, any CIF card or CASA account.
76  - **"In person" could not be cleanly told apart for credit cards** — no decoded field exists
77    (A1 above). C1 operationalizes it via the raw `add_info.TRANS_LOCATION` free-text field
78    (NOT containing "ONLINE" → in-person); this is the snippet's own best-effort read, not an
79    existing pipeline definition, and `candidate_field_value_counts` in `t7a_credit_card` reports
80    `FF`, `DT_ENTMODE`, `source_channel` too so the user can override C1 if the data disagrees.
81    For CASA, `channel_desc` (`Point of Sale`/`ATM Transactions`) is used for D1 and is a real,
82    0%-null field — "in person" is NOT ambiguous there.
83  - **Not evidence**: online purchases/transfers (no in-person filter applied), remittances,
84    logins with both country columns NULL.
85
86  ## PROD run steps
87
88  1. Pull this branch, open a Kedro notebook (`kedro jupyter notebook`).
89  2. Run (works from any notebook location — walks up from CWD to find the repo root):
90     ```python
91     import sys, pathlib
92     _c = pathlib.Path.cwd()
    (continues below the visible area)
````


## Review (2026-10-27)

**Settled**

- **O59: what `DOMESTIC=N` means.** The flag is not inverted. `N` marks a merchant outside the UAE,
  online included. It is 9% of all Way4 rows and 21.5% of the rows that carry the key. The 96%
  in v01 was the share of customers with *any* `N` row in the T0 extract. No card-present field
  is decoded anywhere (`FF=PHYSICAL_CARD` is on every row; `DT_ENTMODE` is blank on `N` rows), and
  `TRANS_LOCATION` is too sparse to use (C1 finds 587 rows against C3's 12,613). C2 (ATM plus the
  in-person merchant categories) needs only `is_international`, `merchant_category_code` and
  `txn_category`, and `prm_transaction` keeps all three, so no new card primary is needed.
- **Debit cards / CASA: route (a).** The raw `comp_financial_tran_repos_dly` beats the WM
  datasets on coverage (CC 57.5% vs 55.2%, RL 75.6% vs 73.3%), on card identification and on
  country fill. The WM datasets also cover only the PRB / PSB / PB segments. Columns:
  `channel_desc` (0% null; `Point of Sale` / `ATM Transactions`) marks card use and
  `merchant_country` (the country name) marks location. `prm_casa.py` already builds a primary
  from this raw table (`build_return_events`), so the new card-location primary sits beside it,
  same pattern. **R12 is not needed.**
- **The travel rule is small.** At the baseline it moves 1.7% (CC) and 1.4% (RL) of rows to
  Skip, almost all from Unknown. Only 16% (CC) and 10% (RL) of known leavers bought a ticket,
  so L2 can only add to L1, never replace it.
- **SILENCE = W stops L2 from ever overriding In Country.** When there has been no UAE evidence
  for W, L3 cannot fire. At GAP 3 m / SILENCE 3 m, L2 takes 607 CC rows (3.1%) and 99 RL rows
  (2.5%), and only 11 and 2 of them came from In Country (a month-vs-day edge). GAP 3 months
  covers 82% (CC) and 84% (RL) of the ticket → last-UAE lags of known leavers, against about 5%
  for stayers.

**Caveats (no new snippet; the bundle's check pipeline measures them)**

1. **t1 overstates CC L1 (63.5%).** It counted every `N` row, online included. The real CC Skip
   share will be lower. The old A2 reads the same unfiltered flag (`last_txn_foreign_flag` →
   `departure_trail_flag`), so the old CC Skip is inflated in the same way. Expect a large
   old-vs-new move on CC: a correction, not a regression.
2. **t7c's credit-card row (588) matches C1 (587), not the recommended C2 (243).** The source
   split in t7c is therefore not the chosen configuration.
3. **`DOMESTIC=` is missing on 2.73M Way4 rows (58%).** The parse treats a missing key as
   domestic, and `prm_transaction` cannot tell `Y` from a missing key. Credit-card UAE evidence
   is therefore limited to purchases and cash in the C2 categories with `is_international = 0`.
   The check pipeline reports how many In Country rows rest on credit-card evidence alone.
4. **Debit ATM rows carry no `merchant_country`** (D4 = 0 abroad on every route). A UAE ATM
   withdrawal on a debit card is therefore no evidence, the same rule as a login with no country.
5. **RL L2 rows do not look like leavers:** 54.5% answered an outbound call in the last
   3 months, against 22% on CC. It is a thin base (55 rows); roaming is possible.
6. **RL debit counts disagree:** 620 in t7c against 411 for D1 route (a) in t7b, with no
   explanation in the JSON.
7. **t7a skipped RL ("no card").** But on RL, `prm_transaction` holds every card of the scoped
   CIFs (D-A2-16), and about 10–15% of RL customers have one, so the engine reads it on RL too.
