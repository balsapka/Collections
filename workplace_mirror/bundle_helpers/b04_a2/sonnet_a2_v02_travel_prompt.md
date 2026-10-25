# A2 v02: how often the travel rule fires, and how sensitive it is

Give this to the workplace Sonnet in UAT after it has finished A2 v01 (it reuses v01's column
findings). Same flow (Sonnet writes, you run in PROD, Sonnet analyses), folder
`tmp_validation/a2_v02/`. Run for `cc_60_180` and `rl_60_180`; add `cc_180_plus` and
`rl_180_plus` if the run time allows (switch `model_id` in `globals_dev.yml`). Paste back
`summary.md` (part C).

````text
Task: measure how often the proposed A2 travel rule fires in PROD, how sensitive it is to its two
thresholds, and how it compares with alternatives. You work in UAT with no data: you write a
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
   - whether the t6 profile looks like leavers (long silence, few answered calls).
````
