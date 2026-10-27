# A2 v02: summary of the PROD results (part C, standalone)

Part C of `sonnet_a2_v02_travel_prompt.md`, written so a new Sonnet session can work from the
committed results alone. Give it to the UAT Sonnet 5.5 once `results_cc_60_180.json` and
`results_rl_60_180.json` (and any 180+ files) are pushed to `tmp_validation/a2_v02/`. Paste
back `tmp_validation/a2_v02/summary.md` and the part A inventory section of its `README.md`.

````text
Goal: turn the A2 v02 PROD results into a short summary the A2 refactor bundle is built from:
the travel rule's thresholds, how to tell in-person card use, and the debit-card / CASA route.
Read tmp_validation/a2_v02/ (README.md with the part A inventory, a2_v02_snippet.py, every
results_<model_id>.json). Change no code; numbers from the JSONs only.

Rule under test (A2 location, latest evidence wins, CIF level):
  L1 foreign evidence on/after the latest UAE evidence -> Skip;
  L2 travel rule: a travel purchase (MCC 3000-3299, 4411, 4511, 4722 + keywords), the latest
     UAE evidence <= GAP after the last ticket (or none), and >= SILENCE without UAE evidence
     -> Skip; baseline GAP = 1 month, SILENCE = 1 month;
  L3 latest UAE evidence within W (3 months at 60-180, 6 at 180+) -> In Country; L4 Unknown.
  Evidence: logins with a country, in-person card use (POS / ATM, credit + debit), the DCORE
  departure note. Online use, transfers, incoming money and salary are not evidence.
Tables in the JSONs: t1_states, t2_sensitivity (GAP x SILENCE grid), t3_travel, t4_lag (known
leavers), t5_alternatives, t6_l2_profile, t7a_credit_card (options C1-C4 and the DOMESTIC= check),
t7b_debit_card (options D1-D4, routes (a) raw comp_financial_tran_repos_dly vs (b) the sibling
WM datasets), t7c_combined.

Known before this run (v01): "foreign" is suspect in both card sources. Way4 is_international
(add_info DOMESTIC=N, also in prm_transaction) is 1 for 96% of CC customers' transactions, and
comp_financial_tran_repos_dly's foreign share is 51% CC / 70% RL of customers. Say first, per
source, which field and value really mean "used abroad", from t7a / t7b, before judging any
option. If the JSON cannot settle it, say so and name the one extra aggregate that would.

Deliverable: tmp_validation/a2_v02/summary.md, under 70 lines, CC and RL side by side
(180+ if present):
- the "abroad" definition per card source (verdict + the 2-3 numbers behind it);
- the key numbers of t1-t6 per model_id;
- one verdict line each:
  - how many accounts L2 moves to Skip, and from which state;
  - which GAP / SILENCE pair the t4 lag distribution supports (e.g. the GAP that covers 80% of
    known leavers' lags), and how steeply t2 changes around the baseline;
  - whether alternative A or B catches a materially different set (t5);
  - whether the t6 profile looks like leavers (long silence, few answered calls);
  - per card source, which option to use: credit cards C1 if the field exists and is filled,
    else C2; debit cards D1 if the channel values are reliable, else D2; how many Skips the
    "all" option (C3 / D3) would add;
  - for debit cards, which route to build on, (a) or (b), judged on coverage, card-present and
    country quality; which country field to trust; how much each card source adds to the
    logins (t7c);
- any table that failed or is missing (its recorded error), without guessing its numbers.
Commit and push.
````
