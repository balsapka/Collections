# UC2 persona signals — draft for sign-off

Proposed rows to append to `output_schema.md` (continue field ids from 56). Same columns: field id,
field, type, example value, desc. Examples are illustrative. One row per (cif_id, account_id,
observation date), as in the existing schema.

### A1 Ability (feeds SF_4_Ability) — source: a1_ability/classify.py

```
id  field                      type     example   desc
---------------------------------------------------------------------------------------------------
56  a1_state                   string   moderate  A1 state: high / moderate / low / unknown (SF_4
                                                  value)
57  a1_reason                  string   income    Strongest evidence family behind the state, or
                                                  distress
58  a1_provenance              string   observed  observed, or no_signal when the state is unknown
59  a1_unknown_reason          string   no_casa   Why unknown: no_casa (no CASA leg/balance in 12m)
                                                  or dormant_casa; blank otherwise
60  a1_income_level            string   stable    F1 income: stable / weak / none (salary in window
                                                  vs max(3,000 AED, 2x anchor))
61  a1_money_in_level          string   strong    F2 money in or held (inflows or CASA balance):
                                                  strong / some / none
62  a1_money_out_level         string   some      F3 money out (chosen spend, transfers to own
                                                  accounts elsewhere): strong / some / none
63  a1_cross_product_level     string   none      F4 other products with us (assets, current credit
                                                  products): strong / some / none
64  a1_points_total            numeric  2         Points over the four families (2 per strong
                                                  family); 4+ = high, 2+ = moderate
65  a1_distress_flag           numeric  0         1 = returned cheque, DDS reject or bureau bounce
                                                  in window; lowers state one level
66  liquidity_anchor_amt       numeric  2000      Amount the customer must pay now (CC: oldest
                                                  overdue bucket; RL: one instalment); AED
67  a1_sweepable_balance_flag  numeric  1         1 = CASA balance is strong, i.e. money the bank
                                                  could still sweep (diagnostic)
68  a1_eosb_flag               numeric  0         1 = DCORE end-of-service result in window
                                                  (diagnostic)
69  a1_income_source           string   internal  Who shows >= AED 1,000 income in window: internal
                                                  / bureau / both / none
70  a1_salary_stopped          numeric  0         1 = internal salary in the prior window, none in
                                                  the current one
```

### A2 Locatability (feeds SF_2_Locatability) — source: a2_locatability/classify.py, signals.py

```
id  field                         type        example                desc
----------------------------------------------------------------------------------------------------
71  a2_state                      string      in_country__reachable  Combined state:
                                                                     <location>_<reachability> (9
                                                                     values) or deceased
72  location_state                string      in_country             skip / in_country / unknown
73  reachability_state            string      reachable              reachable / non_reachable /

<!-- lines 53-69 not in the photos (rest of A2 table, ends with desc text 'abroad') -->

81  last_foreign_source           string      TBD                    Source of that evidence
82  last_travel_date              YYYY-MM-DD  2026-06-01             Latest travel event
83  reachability_unknown_reason   string      TBD                    Why reachability is unknown
84  last_contact_date             YYYY-MM-DD  2026-10-02             Latest successful contact
                                                                     (DCORE) -- NAME CLASH, see open
                                                                     points
85  last_attempt_date             YYYY-MM-DD  2026-10-20             Latest contact attempt
86  attempt_days_in_window        numeric     6                      Distinct days with a contact
                                                                     attempt in the window
87  last_skip_trace_date          YYYY-MM-DD  2026-09-10             Latest skip-trace event
```

### A3 Payment credibility (feeds SF_3_Payment_credibility) — source: a3_credibility/classify.py

```
id   field                             type        example         desc
----------------------------------------------------------------------------------------------------
88   a3_state                          string      Moderate        A3 state: high / moderate / low /
                                                                   unknown (SF_3 value)
89   a3_reason                         string      TBD             Main reason for the state
90   a3_unknown_reason                 string      no_episode      no_episode when no delinquency
                                                                   episode anchor; blank otherwise
91   a3_override                       string      refusal         Override applied (refusal lowers
                                                                   state one level)
92   a3_points_total                   numeric     3               Sum of the three dimension
                                                                   points; 4+ = high, 2+ = moderate
93   episode_start                     YYYY-MM-DD  2026-06-30      Start of the current delinquency
                                                                   episode
94   episode_left_censored             numeric     0               1 = episode start predates the
                                                                   available history
95   a3_promise_deadline               string      next_statement  Rule used to judge when a promise
                                                                   is due (next_statement /
                                                                   month_end / ...)
96   a3_commitments_level              string      kept            Dim A promises: kept /
                                                                   partly_kept / broken / thin
97   a3_commitments_points             numeric     2               Points: kept 2, partly kept 1,
                                                                   broken -1
98   commitments_window_start          YYYY-MM-DD  2025-11-30      Start of the 12-month promise
                                                                   window
99   commitments_concluded             numeric     4               Promises whose deadline has
                                                                   passed in the window
100  commitments_kept                  numeric     3               Concluded promises kept
101  commitments_partial               numeric     0               Concluded promises partly kept
102  commitments_kept_rate             numeric     0.75            Kept share of concluded promises
                                                                   (kept >= 0.80, broken < 0.40)
103  commitments_last_broken_n         numeric     0               Broken promises among the most
                                                                   recent concluded (3 in a row =
                                                                   broken)
104  a3_dlq_payment_level              string      some            Dim B payments while delinquent:

<!-- lines 119+ not in the photos -->
