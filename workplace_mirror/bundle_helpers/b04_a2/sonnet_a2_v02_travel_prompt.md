# A2 v02: the travel rule (firing rate, sensitivity) and how to tell in-person card use

Give this to the workplace Sonnet in UAT after it has finished A2 v01 (it reuses v01's column
findings). Same flow (Sonnet writes, you run in PROD, Sonnet analyses), folder
`tmp_validation/a2_v02/`. Run for `cc_60_180` and `rl_60_180`; add `cc_180_plus` and
`rl_180_plus` if the run time allows (switch `model_id` in `globals_dev.yml`). Paste back
`summary.md` (part C).

````text
Task: measure how often the proposed A2 travel rule fires in PROD, how sensitive it is to its two
thresholds, and how it compares with alternatives; and find out how to tell in-person credit-card
use from online use, comparing the options. You work in UAT with no data: you write a
validation snippet, the user runs it in PROD. Change no pipeline code.

The location rules (checked in order; dates on or before the observation date):
  L1 Skip        there is foreign evidence dated on or after the latest UAE evidence
  L2 Skip        travel rule: there is a travel purchase, the latest UAE evidence is at most
                 GAP after the last travel purchase (or there is no UAE evidence), and there has
                 been no UAE evidence for at least SILENCE before the observation date
  L3 In Country  the latest UAE evidence is within the window (3 months at 60-180, 6 at 180+,
                 the observation month included)
  L4 Unknown     otherwise
Baseline GAP = 1 month, SILENCE = 1 month.

Evidence, per CIF (all the customer's cards and accounts), dated by day:
  UAE evidence      a login from the UAE; an in-person card payment or ATM withdrawal in the UAE
                    (credit or debit card) that is not a travel purchase
  foreign evidence  a login from abroad; an in-person card payment or ATM withdrawal abroad;
                    a DCORE departure result (LEFT THE COUNTRY, OUT OF COUNTRY,
                    KSA/NATHEER-CROSSING FINAL EXIT VISA)
  travel purchase   MCC 3000-3299, 4411, 4511, 4722 (or the airline / travel keywords in
                    _TRAVEL_KEYWORDS_RE, cc_departure_signature/nodes.py), any channel
  Not evidence      online purchases, transfers / remittances; logins with no country (both
                    country columns NULL) — they are neither UAE nor foreign.
  Use the sources v01 identified: the login data per login (stg_digital_login is acceptable
  here because this is a validation, not a pipeline), the card transactions with the domestic
  flag, MCC and a card-present / channel field if one exists, and
  wm_pri_labelled_transactions_indicators_by_week for CASA (channel, mcc_code, country /
  home_country_flag). Say in README.md exactly which source, column and filter defines each
  evidence type, and where "in person" could not be told apart (then count all and say so).

A. Inventory first (read only; append to README.md, under 50 lines). Credit cards and debit cards
   come from different systems: answer for each separately.
   A1 Credit cards (Way4): prm_transaction (primary, catalog_outputs.yml:429-431, preferred)
      and raw_transaction (raw, catalog_raw_way4.yml:35-38): every column, name, type, what the
      code or docs say it holds; from which date prm_transaction holds transactions (it is model-scoped: CC models the
      spine cards, RL models all cards of the scoped CIFs via cc_scope — that scope is used as
      is); every key in add_info that the repo parses or documents (the DOMESTIC= flag comes
      from there, prm_cc.py:375-381) — look for POS entry mode, e-commerce / card-not-present,
      terminal type, ATM indicators; how cash advances (ATM) are marked (MCC 6011, txn type).
   A2 Debit cards / CASA — two candidate routes, answer for both:
      (a) comp_financial_tran_repos_dly, the raw CASA transaction table (would need a new
          reusable primary node): which rows are debit-card use at all (vs transfers, standing
          orders, cheques, bill payments, fees), which columns mark POS / ATM / e-commerce
          (channel_desc, tran_type, tran_sub_type, tran_particular_code, narration), and which
          say where the card was used (merchant_country, counter_party_bank_cntry, ...), with
          their fill rates from the profiles;
      (b) the sibling-repo feature datasets (wealth_management, retail.feature_space):
          wm_pri_labelled_transactions_indicators_by_week (channel_desc / channel_tran_type,
          mcc_country, home_country_flag, mcc_code), fea_casa_cc_international_spend_by_cif and
          fea_days_since_last_international_case_cc_txns (intl_flag_by_loc /
          transaction_location): grain, whether a date per transaction or only weekly
          aggregates survive, how "international" is defined, whether card-present can be told,
          and whether they cover our customers or only WM's population.
   Quote file:line. Name, per source, the field that marks "card present" and the field that
   marks "abroad", or say NONE FOUND.

B. PROD snippet: tmp_validation/a2_v02/a2_v02_snippet.py plus README.md with the run steps.
   Rules: catalog.load only (no spark.read, no paths); model_id from
   catalog.load("params:model_id") and in the output filename; aggregates only — no ids or
   customer rows; read at most 36 months of events before the observation date; base = the obs
   base for model_id, latest observation month only; per CIF compute last_uae_date,
   last_foreign_date, last_travel_date once and derive everything below from them. One JSON at
   context.project_path / "tmp_validation/a2_v02/results_<model_id>.json"; wrap each table in
   try/except and record the error; commit and push only tmp_validation/a2_v02/.

   Tables:
   t1_states       base rows by state under the baseline, with and without L2 (crosstab
                   "without L2" x "with L2"), and by the rule that decided it (L1..L4).
   t2_sensitivity  rows where L2 fires (and L1 does not), for GAP in {14 days, 1, 2, 3 months}
                   x SILENCE in {1, 2, 3, 6 months}: count, share of base, and of those how many
                   would otherwise be In Country vs Unknown.
   t3_travel       share of base CIFs with any travel purchase in the 36 months; age of the last
                   one at the observation date (0-1 / 1-3 / 3-6 / 6-12 / 12-24 / 24-36 months);
                   by source (credit card / CASA) and by channel (online / in person / unknown).
   t4_lag          calibration on known leavers = rows decided by L1 through a foreign login or
                   in-person use abroad (not the DCORE note): the gap from the last travel
                   purchase before the first foreign evidence to the last UAE evidence before it,
                   in days (ticket after the last UAE evidence / 0-7 / 8-14 / 15-30 / 31-60 /
                   61-90 / 91-180 / 180+ / no ticket). Same buckets for rows decided by L3
                   (active in the UAE) as a contrast.
   t5_alternatives rows that would be Skip from travel under: A) the old rule (a travel purchase
                   in the last 12 months competing by date as foreign evidence); B) any travel
                   purchase in the last 12 months and no UAE evidence in the window. For each, the
                   overlap with L2 (both / only the alternative / only L2).
   t7a_credit_card credit-card purchases and cash advances in the 12 months before the
                   observation date, base CIFs: value counts (top 50) of each candidate
                   card-present / channel field from A1, split domestic / international; ATM
                   share. Then for each option, the base rows whose latest foreign evidence
                   comes from credit-card use, and the rows decided Skip by L1 because of it:
                     C1 the card-present field from A1 (if found);
                     C2 ATM + in-person merchant categories only: grocery 5411/5422/5441/5451/
                        5462/5499, fuel 5541/5542, restaurants 5812/5813/5814, pharmacy 5912,
                        transport 4111/4121/4131, department / convenience 5311/5331;
                     C3 all purchases (no in-person filter);
                     C4 ATM only.
                   Overlap of C2 and C3 with C1 (if C1 exists): Skip under both / only one.
   t7b_debit_card  for each route from A2 separately — (a) the raw CASA table, (b) the sibling
                   datasets — debit-card / CASA debits in the same 12 months, base CIFs: rows by
                   the channel values (top 50), split home country / abroad by each candidate
                   country field (and how often those fields disagree); share of rows that are
                   card use at all; share of base CIFs covered. Then for each option, as in t7a:
                     D1 card-present channels from A2 (POS, ATM);
                     D2 ATM + the in-person merchant categories of C2;
                     D3 all debit-card rows (online included);
                     D4 ATM only.
                   Overlap of D2 and D3 with D1, and, per option, overlap of routes (a) and (b)
                   (Skip under both / only one).
   t7c_combined    with the chosen credit-card option and the chosen debit-card option, how
                   many base rows get their latest UAE / foreign evidence from credit cards, debit
                   cards, logins or the DCORE note; and how many have card evidence only from one
                   of the two card sources.
   t6_l2_profile   for rows where L2 fires at the baseline: months since the last UAE evidence
                   (1 / 2 / 3 / 4-6 / 7-12 / 12+), and the share with any outbound call answered
                   in the last 3 months in DCORE (a sanity check: a "left" customer answering
                   calls is suspicious, though roaming is possible).

C. After the user commits the results: save tmp_validation/a2_v02/summary.md, under 60 lines:
   per model_id the key numbers of t1-t6, then one verdict line each:
   - how many accounts L2 moves to Skip, and from which state;
   - which GAP / SILENCE pair the t4 lag distribution supports (e.g. the GAP that covers 80% of
     known leavers' lags), and how steeply t2 changes around the baseline;
   - whether alternative A or B catches a materially different set (t5);
   - whether the t6 profile looks like leavers (long silence, few answered calls);
   - per card source, which option to use: credit cards (t7a) C1 if the field exists and is
     filled, else C2; debit cards (t7b) D1 if the channel values are reliable, else D2; how many
     Skips the "all" option (C3 / D3) would add (likely online foreign shopping);
   - for debit cards, which route to build on — (a) a new primary from the raw CASA table, or
     (b) the sibling datasets — judged on coverage, card-present and country quality (t7b);
     which country field to trust; how much each card source adds to the logins (t7c).
````
