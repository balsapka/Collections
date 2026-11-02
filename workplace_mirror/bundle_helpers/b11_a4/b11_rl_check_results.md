# Bundle 11 RL check results: review (rl_60_180, 2026-08, 3,985 accounts)

Reviewed 2026-11-02. Source: the UAT summary of the B11 blocks (handoff 29, below).

**Verdict: passes; step 8 can run.**

- ECL rule confirmed as the cause: 1,092 of the 1,094 old Unknown were flagged. New Unknown = 0.
- `2025_12_or_later` = 0: every flagged account's history starts before the seam, so no state
  comes from a truncated history. This shows the start is before 2025-12, not that it reaches
  disbursement.
- Known states: 2,889 of 2,891 unchanged; the 2 moves are stitched slow_roller -> repeat.
- 0 EPD among flagged Auto is expected: they were disbursed before 2025-12, and an EPD reaches
  180+ about 6 months after the spell starts, so few can still be in 60-180 by 2026-08.
  The 48 Auto EPD are all in the 113 Auto accounts disbursed later.
- Stitching: 65 of 67 known restructured, all one_to_one, none ambiguous; 4 state changes.

**Open, not blocking:**

- **0 restructured Auto** of 1,364, against 19 of 1,397 Personal and 48 of 1,224 Personal Cash.
  The check only counts flagged or linked accounts, so `is_restructured` may be unset for Auto
  in the new history (the DE reported Auto restructures since 2025-12).
- **Auto repeat_delinquent 14.9% of flagged** against 7.8% Personal, 5.5% Personal Cash. Older
  books explain part of it (7.8% is 11% without EPD and early life). A bucket break where the
  old and new sources meet would look like a cure and could explain the rest.

# Handoff 29: `data/input/rl_a4_b11_check_run_summary.md` (5 photos), 2026-11-02

## Context for Claude Code
- Source: 5 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-11-02 ~15:04 Dubai. Tabs: `pipeline_registry.py`, `11_a4_rl_restructure_chains.md`, `rl_a4_b11_check_run_summary.md` (active, saved). Path: `data > input > rl_a4_b11_check_run_summary.md`. Status bar: Ln 1, Col 1, Spaces: 2.
- Title: "RL A4 Deterioration - B11 Check Run Summary". Results of the B11 check run of the new RL A4 (deterioration) logic: the ECL-gap fix for old `unknown` accounts and the restructure-chain stitching specified in handoff 26 (README) and bundle `11_a4_rl_restructure_chains.md`. Follows handoffs 1-28.
- You said the last line ("reproduced here.", line 169) is the end of the file. This handoff therefore covers the file to its end.
- **Not visible in any photo: lines 2-20 (section 1) and lines 22-33 (body of section 2, "Node execution order")**. Only the line 1 title and the line 21 heading `## 2. Node execution order` are visible, from the sticky header. Those lines are NOT transcribed. If you need them, send one more photo of lines 1-34.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run output.
- Photos overlap and are merged by line number. Photo-to-line map (in the order sent): P1 = 112-169; P2 = 86-144; P3 = 48-116; P4 = 48-88 (partly 55-62); P5 = 1, 21, 34-67.
- Tables are shown as in the editor.

---

## `rl_a4_b11_check_run_summary.md` (lines 1, 21, 34-169)

````
1   # RL A4 Deterioration - B11 Check Run Summary
...     [lines 2-20 (section 1) not visible in the photos]
21  ## 2. Node execution order
...     [lines 22-33 not visible in the photos]
34
35  ## 3. New det_state distribution (build_rl_deterioration, 60_180)
36
37  Total accounts (2026 August) = 3,985.
38
39  | det_state                  |     n |     % |
40  |----------------------------|------:|------:|
41  | straight_roller_seasoned   | 1,349 | 33.9% |
42  | slow_roller                |   933 | 23.4% |
43  | straight_roller_early_life |   700 | 17.6% |
44  | stabilized                 |   411 | 10.3% |
45  | repeat_delinquent          |   363 |  9.1% |
46  | early_payment_default      |   229 |  5.7% |
47
48  ## 4. B11 OUTPUT - old x new state (accounts 3,985)
49
50  | old                        | new                        |     n |     % |
51  |----------------------------|----------------------------|------:|------:|
52  | early_payment_default      | early_payment_default      |   229 |  5.7% |
53  | repeat_delinquent          | repeat_delinquent          |   174 |  4.4% |
54  | slow_roller                | repeat_delinquent          |     2 |  0.1% |
55  | slow_roller                | slow_roller                |   612 | 15.4% |
56  | stabilized                 | stabilized                 |   411 | 10.3% |
57  | straight_roller_early_life | straight_roller_early_life |   552 | 13.9% |
58  | straight_roller_seasoned   | straight_roller_seasoned   |   911 | 22.9% |
59  | unknown                    | repeat_delinquent          |   187 |  4.7% |
60  | unknown                    | slow_roller                |   321 |  8.1% |
61  | unknown                    | straight_roller_early_life |   148 |  3.7% |
62  | unknown                    | straight_roller_seasoned   |   438 | 11.0% |
63
64  Key reading:
65  - 1,094 accounts (27.5%) were `unknown` in the old logic and now get a real state.
66  - 2,891 accounts (72.5%) keep a known old state; 2,889 of those keep the same state.
67  - Only change among known states: 2 slow_roller -> repeat_delinquent (0.1%).
68  - stabilized and early_payment_default are unchanged (411 and 229).
69
70  ### Loan type x new state
71
72  | loan_type      | early_pay_def | repeat_delinq | slow_roller | stabilized |
73  |----------------|--------------:|--------------:|------------:|-----------:|
74  | Auto           |    48 (1.2%)  |   187 (4.7%)  |  331 (8.3%) | 162 (4.1%) |
75  | Personal       |   125 (3.1%)  |   109 (2.7%)  |  315 (7.9%) |  94 (2.4%) |
76  | Personal Cash  |    56 (1.4%)  |    67 (1.7%)  |  287 (7.2%) | 155 (3.9%) |
77
78  | loan_type      | straight_roller_early_life | straight_roller_seasoned | Total |
79  |----------------|---------------------------:|-------------------------:|------:|
80  | Auto           |                200 (5.0%)  |              436 (10.9%) | 1,364 |
81  | Personal       |                284 (7.1%)  |              470 (11.8%) | 1,397 |
82  | Personal Cash  |                216 (5.4%)  |              443 (11.1%) | 1,224 |
83
84  Percentages are of all 3,985 accounts.
85
86  ## 5. B11 ECL - flagged accounts (old `unknown` driven by ECL gap)
87
88  Flagged accounts: 1,251 (31.4% of 3,985).
89
90  | loan_type | history_from   |     n |      % |
91  |-----------|----------------|------:|-------:|
92  | Auto      | before_2025_12 | 1,251 | 100.0% |
93
94  All flagged accounts are Auto and have history from before 2025-12.
95
96  | history_from   | old      | new                        |    n |     % |
97  |----------------|----------|----------------------------|-----:|------:|
98  | before_2025_12 | stabilized | stabilized               |  159 | 12.7% |
99  | before_2025_12 | unknown  | repeat_delinquent          |  187 | 14.9% |
100 | before_2025_12 | unknown  | slow_roller                |  321 | 25.7% |
101 | before_2025_12 | unknown  | straight_roller_early_life |  148 | 11.8% |
102 | before_2025_12 | unknown  | straight_roller_seasoned   |  436 | 34.9% |
103
104 History months (min / median / max) for before_2025_12: 10 / 25 / 67.
105
106 Key reading:
107 - 1,092 of 1,251 flagged accounts were `unknown` before and are now resolved.
108 - 159 were already `stabilized` and stay `stabilized`.
109 - Of the 438 `unknown -> straight_roller_seasoned` in section 4, 436 are ECL-flagged; the
110   other 2 are restructure-chain stitches (section 6).
111
112 ## 6. B11 CHAIN - restructure stitching
113
114 Restructured accounts: 67. Stitched: 65 (97.0%).
115
116 | loan_type     | stitched | still blind |  n |     % |
117 |---------------|---------:|------------:|---:|------:|
118 | Personal      |        0 |           1 |  2 |  3.0% |
119 | Personal      |        1 |           0 | 17 | 25.4% |
120 | Personal Cash |        1 |           0 | 48 | 71.6% |
121
122 (The "Personal, stitched 0, still blind 1" row is the 2 accounts that could not be stitched.)
123
124 | match_type |  n |      % |
125 |------------|---:|-------:|
126 | one_to_one | 65 | 100.0% |
127
128 - Ambiguous matches (candidate_count > 1): 0.
129 - Months of history added by stitching (min / median / max): 5 / 16 / 87.
130
131 ### Stitched accounts: old x new
132
133 | old                      | new                      |  n |     % |
134 |--------------------------|--------------------------|---:|------:|
135 | repeat_delinquent        | repeat_delinquent        |  7 | 10.8% |
136 | slow_roller              | repeat_delinquent        |  2 |  3.1% |
137 | slow_roller              | slow_roller              | 19 | 29.2% |
138 | stabilized               | stabilized               | 19 | 29.2% |
139 | straight_roller_seasoned | straight_roller_seasoned | 16 | 24.6% |
140 | unknown                  | straight_roller_seasoned |  2 |  3.1% |
141
142 Key reading:
143 - Stitching changes the state of only 4 of 65 accounts (6.2%): 2 slow_roller ->
144   repeat_delinquent and 2 unknown -> straight_roller_seasoned.
145 - The 2 slow_roller -> repeat_delinquent moves are the only known-to-known changes in the
146   whole population (section 4).
147 - Stitching is clean: all matches are one-to-one with zero ambiguity.
148
149 ## 7. B11 UNKNOWN
150
151 | Metric            | Value |
152 |-------------------|------:|
153 | unknown (new)     |     0 |
154 | route x loan_type | empty |
155
156 No account is `unknown` under the new logic, so the route x loan_type breakdown is empty.
157
158 ## 8. Takeaways
159
160 1. New logic leaves zero `unknown` accounts; all 1,094 old `unknown` are assigned a state.
161 2. The old `unknown` population is almost entirely an Auto ECL-gap effect (1,092 of 1,094,
162    all with history before 2025-12); the other 2 come from restructure stitching.
163 3. Known-state agreement is near-perfect: 2,889 of 2,891 unchanged; 2 moved because of
164    restructure stitching.
165 4. Restructure chain: 65 of 67 stitched, all one-to-one; 2 Personal accounts stay blind.
166 5. Resolved Auto `unknown` accounts split mostly into straight_roller_seasoned (34.9%) and
167    slow_roller (25.7%) of the flagged set.
168 6. `kedro run` was executed by the user in their own environment; results were not
169    reproduced here.
````

## Notes on specific spots
- Checks I ran on the transcription: section 3 (lines 41-46) sums to 3,985; old x new (lines 52-62) sums to 3,985, with 2,891 known-old-state rows (matches line 66) and 1,094 old-unknown rows (187 + 321 + 148 + 438, matches line 65); loan-type totals (lines 80-82) sum to 3,985; flagged table (lines 98-102) sums to 1,251; chain loan_type rows (lines 118-120) sum to 67; stitched old x new (lines 135-140) sums to 65; the unknown rows 187 / 321 / 148 are the same in section 4 and section 5, and 438 = 436 + 2 (line 109).
- Line 118-120: the loan_type column reads "Personal" twice (stitched 0 / still blind 1, then stitched 1 / still blind 0), as printed. The "stitched" and "still blind" columns are 0/1 flags, not counts.
- Line 98: this table's first row is `stabilized` to `stabilized` with 159 accounts (12.7% of the 1,251 flagged); it comes from P3.
- In the photos, the numbers in tables of lines 72-82 use the form `n (% of all 3,985)`. Line 84 states that.
- Column padding in the code block is mine for readability; the real file's padding may differ (the `|` bars and values are as shown).
- Line 168 mentions `kedro run` was executed by you in your own environment. Line 169 is the last line of the file (you confirmed).
