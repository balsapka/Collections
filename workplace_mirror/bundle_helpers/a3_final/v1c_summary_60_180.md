# A3 V1c summary (cc_60_180, rl_60_180): `tmp_validation/a3_v1_v4/summary_v1c.md`

Transcribed from handoff 41 (4 photos, merged into source lines 1–104, chat transcription). Tables
ragged in the source at lines 70–71 and 82–85, kept as shown. Review: `v1_v4_review.md`, section V1c.

````
1   # A3 V1c summary - corrected cumulative ledger, 60/180 models (cc_60_180, rl_60_180)
2
3   Evidence: `results_v1c_cc_60_180.md` (19,292 accounts, 19,277 agreements) and
4   `results_v1c_rl_60_180.md` (3,985 accounts and agreements), latest month 2026-08-31, anchor = A4
5   spell start (same month as the A3 `t0` on 19,290 / 19,292 CC and 3,965 / 3,985 RL). Ledger rule as
6   `README_v1c.md`. The 180+ models were not run. **Gap: section 4 (Dimension A level, DCORE vs ledger)
7   failed with a Java heap error in both models** and is not in this summary. It failed again on RL
8   (3,985 accounts) after the cache-release fix, so the cause is not data size (see Open items).
9
10  ## What changed against the first V1 ledger (`summary.md`)
11
12  The old ledger compared one instalment's due amount with all money paid since plan start.
13  Plan-length results show why that mattered only for some plans.
14
15  - **All PTP plans in both models have a single instalment** (plan-length rows 2-3 and 4+ are empty).
16    The new cumulative rule changes nothing for PTP: CC 93.2% / 92.0% (was 93.2% / 92.0%), RL 78.4% /
17    86.5% (unchanged).
18  - **Settlement plans are multi-instalment** (CC 92% of instalments sit in plans of 4+; RL 84%), and
19    this is where the numbers move. CC settlement agreement to the due date: 52.0% -> 62.5% (all),
20    48.7% -> 70.5% (last 3m); to due date + 5 days: 55.0% -> 68.6%, 51.0% -> 74.8%. Cramer's V 0.06 ->
21    0.36 / 0.37 (due date), 0.46 / 0.48 (+5d). RL settlement is slightly lower: 80.5% -> 78.4% (all),
22    87.7% -> 85.6% (last 3m).
23  - Coverage is complete: no instalment is unscored in either model, and no RL instalment spans a
24    missing loan-master month.
25
26  ## DCORE status vs ledger (concluded instalments)
27
28  | model | plan | cut-off | scope | instalments | agreement | V |
29  |---|---|---|---|---|---|---|
30  | cc | PTP | due date | all / last 3m | 4,701 / 1,396 | 93.2% / 92.0% | 0.69 / 0.61 |
31  | cc | PTP | due date + 5d | all / last 3m | 4,701 / 1,396 | 88.7% / 91.6% | 0.57 / 0.63 |
32  | cc | settlement | due date | all / last 3m | 12,151 / 5,962 | 62.5% / 70.5% | 0.36 / 0.37 |
33  | cc | settlement | due date + 5d | all / last 3m | 12,151 / 5,962 | 68.6% / 74.8% | 0.46 / 0.48 |
34  | rl | PTP | due month | all / last 3m | 877 / 355 | 78.4% / 86.5% | 0.53 / 0.65 |
35  | rl | settlement | due month | all / last 3m | 333 / 187 | 78.4% / 85.6% | 0.61 / 0.70 |
36
37  **CC.**
38  - DCORE `overdue` is almost never ledger-kept: PTP 0% to the due date, 8.0% with +5 days; settlement
39    <10 of 6,311. When DCORE says overdue, the ledger agrees.
40  - DCORE `paid` is only partly confirmed: PTP 52.0% kept to the due date, 69.0% with +5 days;
41    settlement 22.1% and 34.7%. So the disagreement is one-sided: DCORE calls instalments `paid` that
42    the customer's card payments do not cover, and the gap shrinks when 5 days of grace are allowed.
43  - Agreement on PTP is mostly the base rate: 85.8% of PTP instalments are overdue and not kept, so
44    always guessing that cell gives 85.8% against 93.2% agreement.
45  - Settlement 4+ plans disagree most (60.9% / 67.2% agreement); 1- and 2-3-instalment plans sit at
46    80-88%.
47
48  **RL.**
49  - DCORE `paid` is ledger-kept 94.3% (PTP) and 53.0% (settlement); last 3m 98.0% and 63.4%.
50  - DCORE `overdue` is ledger-kept 24.6% (PTP, 181 of 737) and <10 (settlement). The PTP
51    overdue-but-kept group is the opposite pattern to CC: the loan master shows enough paid in the due
52    month while DCORE has the instalment overdue. Month-level `total_paid` cannot separate a payment
53    before the due date from one after it, so some of this is the cut-off, not a DCORE error.
54  - Agreement on all-concluded RL PTP (78.4%) is below always guessing the modal row level (84.0%);
55    the V of 0.53 is real association, but the status adds no accuracy over the base rate in that
56    cell. The last-3m cell is 86.5% against 85.9%.
57  - RL settlement is the cleanest relation: V 0.61 / 0.70, 78-86% agreement against a 55-62% baseline.
58
59  ## PTP names in `dcore_prm_followup_outcomes` (latest 12 months, model agreements)
60
61  **CC** (rows / agreements / rows in delinquency)
62
63  | result name | model set | rows / agreements / in delinquency |
64  |---|---|---|
65  | PROMISE TO PAY | PROMISE_TO_PAY | 9,180 / 4,445 / 4,418 |
66  | PROMISE TO PAY SCHEDULED | PROMISE_TO_PAY | 9,867 / 3,613 / 7,023 |
67  | DIGITAL COLLECT  PTP SUBSCRIBED | PROMISE_TO_PAY | 750 / 583 / 422 |
68  | RETAIN PTP | RETAIN_PTP | 68 / 26 / 58 |
69  | SOFTPTP | PROMISE_TO_PAY | 35 / 32 / 34 |
70  | HISTORICAL PROMISE TO PAY | PROMISE_TO_PAY | 0 |
71  | PROMISE TO PAY PARTIALLY | PROMISE_TO_PAY | <10 |
72  | EOSB_PTP_DOCUMENTS | not in either set | <10 / <10 / 0 |
73
74  **RL** (rows / agreements / rows in delinquency)
75
76  | result name | model set | rows / agreements / in delinquency |
77  |---|---|---|
78  | PROMISE TO PAY | PROMISE_TO_PAY | 1,087 / 632 / 694 |
79  | PROMISE TO PAY SCHEDULED | PROMISE_TO_PAY | 1,758 / 780 / 1,189 |
80  | DIGITAL COLLECT  PTP SUBSCRIBED | PROMISE_TO_PAY | 187 / 116 / 172 |
81  | RETAIN PTP | RETAIN_PTP | 90 / 26 / 70 |
82  | SOFTPTP | PROMISE_TO_PAY | <10 |
83  | HISTORICAL PROMISE TO PAY | PROMISE_TO_PAY | 0 |
84  | PROMISE TO PAY PARTIALLY | PROMISE_TO_PAY | <10 |
85  | EOSB_PTP_DOCUMENTS | not in either set | not present |
86
87  - `HISTORICAL PROMISE TO PAY` has no rows in the latest 12 months in either model; it is in the set
88    but does not fire for these populations. `RETAIN PTP` fires on 26 agreements in each model.
89  - The only PTP-like name outside both sets is `EOSB_PTP_DOCUMENTS` (CC, <10 rows, none in
90    delinquency): immaterial.
91
92  ## Open items
93
94  1. **Section 4 level crosstab still fails (CC and RL).** The per-call cache release did not help,
95     and RL has only 3,985 accounts, so the failure is driver-side plan growth (the chained window /
96     join / streak plan across 12 iterations in one session), not data volume. The section-4-only
97     snippet `a3_v1c_level_snippet.py` has the same plan, so it will likely fail the same way. A
98     different fix is needed before it is rerun: for example, write the per-iteration frames to a
99     temporary table or checkpoint them (truncating lineage), or run one (variant, source, scope)
100    combination per call.
101 2. Cut-off sensitivity: RL has a single month-level cut-off, so the 24.6% of PTP `overdue`
102    instalments that are ledger-kept cannot be split into late-but-paid and DCORE error.
103 3. 180+ models not run.
104
````
