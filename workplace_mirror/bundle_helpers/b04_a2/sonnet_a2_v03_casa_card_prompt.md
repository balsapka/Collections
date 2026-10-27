# A2 v03: in-person debit-card use in `comp_financial_tran_repos_dly`

Give this to the UAT Sonnet 5.5. Same flow as v01 / v02: Sonnet writes the snippet in UAT, you run it in
PROD for `cc_60_180` and `rl_60_180` (switch `model_id` in `globals_dev.yml`), commit the JSONs,
Sonnet writes the summary. Paste back `tmp_validation/a2_v03/summary.md` and the inventory section
of its `README.md`.

````text
Goal: decide exactly which rows of the raw CASA table comp_financial_tran_repos_dly are a
customer's in-person debit-card use (a shop payment or an ATM withdrawal), and where it
happened (UAE or abroad), so that a new primary table can be built from it. The A2 locatability
axis will use those rows as location evidence. A wrong "in person" makes an online purchase
from a foreign shop look like the customer is abroad, so precision matters more than coverage.
You work in UAT with no data: write a validation snippet, the user runs it in PROD, then you
analyse the results. Change no pipeline code.

Context (decided; do not re-open):
- A2 location = latest evidence wins, per cif_id (all the customer's accounts): UAE logins and
  in-person card use in the UAE are UAE evidence; logins abroad, in-person card use abroad and a
  DCORE departure note are foreign evidence. Online purchases, transfers, remittances, salary
  and incoming money are not evidence. Travel purchases (MCC 3000-3299, 4411, 4511, 4722 +
  _TRAVEL_KEYWORDS_RE) feed a separate travel rule, any channel.
- A2 v02 (tmp_validation/a2_v02/, read README.md and summary.md first) chose this table over
  the WM datasets. It found: channel_desc is never NULL (Point of Sale / ATM Transactions /
  Online or Mobile Banking / Branch / Cheque / remittance); merchant_type_desc has three values
  Offline / Machine / Online and is NULL on 49.3% of rows; merchant_country is a full country
  name ("UNITED ARAB EMIRATES"), NULL on ~40%, and never filled on ATM rows; "all debit-card
  rows" (D3) gave exactly the same rows as POS + ATM (D1), so channel_desc alone probably labels
  online card purchases Point of Sale too. RL debit: 620 rows in t7c vs 411 in t7b, unexplained.
- A primary from this table already exists: prm_casa_return_events
  (src/enbd_collections/nodes/primary/casa/prm_casa.py, build_return_events, pipeline
  casa_primary): all CIFs, dedup on (tran_id, part_tran_srl_num, tran_date) keeping the latest
  edp_load_date, partitioned by event_month. The new table will follow the same pattern.

Draft rule under test (in-person debit-card row):
  R1 channel_desc in (Point of Sale, ATM Transactions)
  R2 merchant_type_desc in (Offline, Machine)          -- Offline = in shop? Machine = ATM?
  R3 tran_dc = 'D', not a returned / reversed / refunded transaction
  R4 MCC not remote: 5815-5818, 4814, 4816, 4899, 5964-5969, 5734, 7372
  R5 merchant_country filled: UNITED ARAB EMIRATES (or its other spellings) = UAE, else abroad
Your job is to test each condition, find better fields if they exist, and recommend the exact
filter.

Questions (hypotheses) to answer, each with a verdict and the numbers behind it:
  H1 merchant_type_desc: does Offline mean card-present in a shop, or "authorised offline"?
     Does Online catch all e-commerce? Evidence: crosstab with channel_desc, MCC groups
     (remote MCCs of R4, grocery / fuel / restaurant / pharmacy / transport, travel, ATM 6011,
     other), merchant_country filled, narration patterns (e.g. "ECOM", "INTERNET", "WWW",
     ".COM", "APPLE.COM", "NETFLIX"); the top 30 merchant names / narrations of foreign Offline
     rows and of UAE Online rows.
  H2 Other card-present fields: list every column of the table (all ~124) that could mark
     card-present / POS entry mode / terminal / ATM id / merchant city / card number, with fill
     rate on card rows and top values. Name the best card-present field, or say none beats
     merchant_type_desc.
  H3 ATM location: where does an ATM row say where it was (terminal id or ATM id prefix, our own
     ATM network, narration text with a city or country, currency)? Can domestic vs foreign
     ATM be told at all? Share of ATM rows you can place.
  H4 merchant_country: all spellings that mean the UAE (UAE, AE, ARE, DUBAI, ...), top 30
     values, NULL share by channel_desc x merchant_type_desc; agreement with the transaction
     currency (foreign merchant vs foreign currency) where a currency column exists.
  H5 Transaction hygiene: key uniqueness and reloads across edp_load_date (as in
     prm_casa_return_events); how reversals, refunds, chargebacks and failed / declined
     authorisations appear (reason_for_excluding, tran_sub_type, tran_dc = C on card channels,
     narration); which rows to drop.
  H6 Dates: tran_date vs value / posting dates on foreign card rows (settlement lag in days);
     which date is closest to the day the card was used.
  H7 Plausibility against logins: for base CIFs, foreign in-person rows (draft rule) on a day
     with a UAE login on the same day or the day before / after, against UAE in-person rows on a
     day with a foreign login. Report both rates under the draft rule, with R2 dropped, and with
     R4 dropped. A good rule keeps the "impossible" rate low.
  H8 What the rule decides, per model_id, latest observation month: base CIFs with any
     in-person row in 3 / 12 / 36 months (UAE, abroad); base rows whose latest foreign evidence
     and latest UAE evidence comes from debit cards (compared with logins, credit cards C2 on
     prm_transaction, and the DCORE note); explain the RL 620 vs 411 gap from v02.
  H9 Sizing the primary: rows per month for all CIFs (all rows, card rows, in-person rows under
     the recommended rule), the earliest tran_date with card rows, the partition column of the
     raw table, and how much the states change if the evidence lookback is 12, 24 or 36 months.
  H10 Credit cards, while you are in the data (prm_transaction, base CIFs, 12 months):
     is_international by txn_category and direction, to size the rows whose Way4 DOMESTIC= key
     is absent (the parse sets them to domestic); how many base rows would be In Country on
     credit-card UAE evidence alone (C2 categories, is_international = 0).

Hard rules:
- catalog.load only (no spark.read, no paths); model_id from catalog.load("params:model_id"),
  in the output file name; no model_id hardcoded or overridden.
- Aggregates only: no ids, card numbers, names or customer rows in the results. Merchant names
  and narrations only as top-N value counts, truncated to 40 characters.
- Base = the obs base for model_id (crx_cc_obs_base / crx_rl_obs_base), latest observation
  month; customer = cif_id, all of its accounts. Read at most 36 months before the observation
  date; filter the raw table on its partition column first.
- One JSON per model_id at context.project_path / "tmp_validation/a2_v03/results_<model_id>.json";
  each table in its own try/except with the error recorded.
- Work only in tmp_validation/a2_v03/ (tracked); commit and push only that folder.

Deliverables:
1. README.md: the inventory (H2 column list with what each field holds, file:line where the repo
   reads it), the run steps, and exactly which column / filter defines each rule.
2. a2_v03_snippet.py, run in PROD for cc_60_180 and rl_60_180.
3. After the user commits the JSONs, summary.md (under 70 lines): per hypothesis a verdict line
   and the key numbers, CC and RL side by side; then the recommended in-person rule as exact
   column = value conditions, the UAE spellings, the date to use, the dedup / drop rules, and the
   columns the new primary should keep; a separate line on what cannot be told (e.g. ATM
   location) and how many rows that leaves out. Check each number against the JSON before you
   write it; write NOT IN JSON when a number is missing.
````
