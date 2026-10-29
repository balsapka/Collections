# A2 v04: the debit-row drop from 2026-05, foreign logins (VPN), and the Non-Reachable threshold, before GRR

Give this to the UAT Sonnet 5.5. Same flow as before: Sonnet writes the snippet in UAT. You run it in PROD
for `cc_60_180` and `rl_60_180` (switch `model_id` in `globals_dev.yml`) and commit the JSONs. Sonnet then
writes the summary. Paste back `tmp_validation/a2_v04/summary.md`.
Our review of the bundle 07 check is in `bundle_helpers/b07_a2/b07_check_results.md`.

````text
Goal: three checks on the new A2 locatability output (crx_cc_a2_locatability / crx_rl_a2_locatability,
latest observation month 2026-08) before it goes to GRR. You work in UAT with no data: write a
validation snippet, the user runs it in PROD, then you analyse the results. Change no pipeline code.

What is known (bundle 07 check, CC 2026-08, 19,292 accounts):
- Skip 44.0%. The deciding evidence (L1 = latest foreign evidence on or after the latest UAE
  evidence) is a foreign login for 5,772 accounts (29.9%); credit card 551, debit 143, DCORE note 403.
  In Country 24.0%, decided mostly by a UAE login (4,367).
- Skip share by month: about 36-37% from Jan to May 2026, then 38.4 / 41.6 / 44.0% in Jun / Jul / Aug.
  RL shows the same (38.6% in Jan, 43.4% in Aug).
- prm_casa_card_transactions rows for the latest month's base CIFs fall about 30-fold from 2026-05
  (2025-08: about 158k rows; 2026-08: about 5k). Rows still exist for 2026-09 and 2026-10.
- v01: 15.1% of login rows are foreign. Login country comes from the login record (countrylocation /
  countrycode in stg_digital_login, is_foreign_login: 0 UAE, 1 foreign, NULL no country).
- The engine output carries location_state, location_rule, last_uae_date, last_uae_source,
  last_foreign_source and the foreign date (read classify.py for the exact names).

Hypotheses, each with a verdict and the numbers behind it:
  D1 Lag or behaviour. Monthly rows of prm_casa_card_transactions (in-person and travel, UAE and abroad)
     for ALL CIFs, 2025-01 to 2026-10. Then the same for three groups: the latest base's CIFs;
     CIFs of a not-delinquent comparison group (customers outside every persona obs base who hold
     a debit card, or the closest available group, named); and the base's CIFs by the month they
     entered 60+ DPD. Also the same monthly counts in the source comp_financial_tran_repos_dly,
     with its load / partition columns. A lag shows in all groups and in the source. Behaviour
     shows only in the base, and starts around each customer's delinquency entry.
  D2 Effect on location. For the base CIFs whose latest UAE evidence is debit-card and older than
     W: how many have debit rows in the 3 months before their delinquency entry. Under D1 =
     behaviour, the drop is real, and Unknown / Skip from it are correct by the rule.
  V1 VPN or real departure. Among the latest-month base accounts with L1 decided by a login:
     - the foreign login countries (top 15, with share);
     - the share of CIFs whose foreign logins come with UAE logins within 1, 3 and 7 days;
     - the share switching country more than N times a month (choose N; give the distribution);
     - the share with any UAE in-person card use (credit or debit) after their latest foreign
       login, from prm_transaction / prm_casa_card_transactions.
     Compare with the In Country accounts decided by a UAE login. Typical VPN exits are countries
     like US, NL, DE, GB and SG; typical expat home countries are IN, PK, PH, EG, BD and LK.
     Say which pattern dominates.
  V2 Sensitivity. Skip / In Country / Unknown shares (CC and RL) in four cases:
     - as now;
     - (a) foreign logins ignored when a UAE login falls within 7 days of them;
     - (b) foreign logins from the top VPN-exit countries ignored;
     - (c) foreign logins ignored, keeping only card, DCORE and travel evidence.
     Re-derive these in the snippet from the same inputs as the engine (feat_cif_location_monthly
     and the login primary). First reproduce the engine's location_state for the "as now" case:
     0 mismatches, else report the count and stop V2.
  R1 Non-Reachable threshold (GONE_DARK_DAYS = 3 in a2_locatability/signals.py, build_dcore_signals).
     Today: Non-Reachable = the last 3 call days all failed, the oldest in W, no contact since;
     else Reachable = a contact in W; else Unknown. CC 2026-08: Non-Reachable 67.6%, Reachable 21.0%,
     Unknown 11.5%. 3,386 accounts (17.6%) had a contact in W and are Non-Reachable anyway; 85.9%
     have 6+ call days in W. Reuse the engine's own helpers and code lists (_dcore_events,
     codes.py) so call days, failures and contacts are defined exactly as in the engine.
     Per account, the failed run k = the number of consecutive failed call days counted back from
     the latest call day, stopping at a call day that did not fail, at the start of W, or at the
     last contact date. Non-Reachable at threshold N <=> k >= N. First check that N = 3 gives the
     engine's reachability_state: 0 mismatches, else report the count and stop R1. Then:
     - the distribution of k (0..15, 16+);
     - for N = 1..10: Non-Reachable / Reachable / Unknown counts and shares, and how many of the
       Non-Reachable had a contact in W;
     - span: for k >= 3, the calendar days from the run's oldest to its latest call day (buckets
       1-3, 4-7, 8-14, 15-30, 31+), crossed with k (3-5, 6-9, 10+), so a rule like "N failed call
       days spanning at least D days" can be read off;
     - the same N table by month, Jan-Aug 2026, Non-Reachable share only.

Hard rules:
- catalog.load only (no spark.read, no paths); model_id from catalog.load("params:model_id"), in
  the output file name; nothing hardcoded or overridden.
- Aggregates only: no CIFs, account ids, IPs, call notes or customer rows in the results. Countries by ISO code
  are fine; leave out any count under 10.
- Base = the obs base for model_id (crx_cc_obs_base / crx_rl_obs_base), latest observation month;
  customer = cif_id; dates never joined exactly to cc_spine / dcore_observation_spine / prm_contract
  (mid-month dates).
- One JSON per model_id at context.project_path / "tmp_validation/a2_v04/results_<model_id>.json";
  each part in its own try/except with the error recorded.
- Work only in tmp_validation/a2_v04/ (tracked); commit and push only that folder.

Deliverables:
1. README.md: run steps and, per hypothesis, the tables and columns read (file:line where the repo
   builds them).
2. a2_v04_snippet.py, run in PROD for cc_60_180 and rl_60_180.
3. After the user commits the JSONs, summary.md (under 60 lines):
   - per hypothesis, a verdict line and the key numbers, CC and RL side by side;
   - then a recommendation: does the debit drop need a data fix, and should foreign logins stay
     L1 evidence as they are, or be ignored when a UAE login falls within N days?
   - the R1 table for N = 1..10, CC and RL side by side, and where the curve flattens.
     Do not recommend a value; the user decides.
   Check each number against the JSON; write NOT IN JSON when one is missing.
````
