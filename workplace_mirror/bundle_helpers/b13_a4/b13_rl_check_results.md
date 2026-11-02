# Bundle 13 RL check results: review (rl_60_180, 2026-08, 3,985 accounts)

Reviewed 2026-11-02. Source: the UAT summary of the B13 blocks (handoff 30, below).

**Verdict: passes; step 7 can run.**

- The switch changes no result. New states match B11 count for count, and old x new is the same
  table cell for cell. Unknown stays 0.
- The baseline was not bundle 11's output: old still has 1,094 Unknown, so bundle 11's step 8 did
  not run. old x new is therefore against the pre-11 output. It does not matter, because the
  identical table shows 13 = 11 on these accounts. Step 7 replaces bundle 11's step 8.
- `has_restructured_loan_flag` = 67 accounts, the same count and split as the old
  `is_restructured` path: 65 stitched, 2 blind (both stabilized). Stitched without the flag: 0.

**Open, not blocking:** restructured Auto is still 0 of 1,364. The feature flag does not change
that, and matches the note in handoff 26 that it is built from `is_restructured`. A flag of 1
means restructured; a 0 on Auto is not evidence of no restructure. Question for the DE.

# Handoff 30: `data/input/mirror_bundles/rl_a4_b13_check_summary.md` (3 photos), 2026-11-02

## Context for Claude Code
- Source: 3 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-11-02 ~15:35 Dubai. Tabs: `pipeline_registry.py`, `staging.py`, `13_a4_rl_restructure_feature_flag.md`, `rl_a4_b13_check_summary.md` (active, saved). Path: `data > input > mirror_bundles > rl_a4_b13_check_summary.md`. Status bar: Spaces: 2 (Ln 1, Col 1 in one photo; Ln 55, Col 71 in the others).
- Title: "RL A4 deterioration B13 check - numbers summary". Numbers from the B13 check run of the RL A4 deterioration logic with the restructure feature flag (bundle `13_a4_rl_restructure_feature_flag.md`). It follows the B11 summary in handoff 29: the state mix is identical, and the new part is the old-blind vs new-blind table in section 4. Follows handoffs 1-29.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run output.
- Photos overlap and are merged into source lines 1-90. Photo-to-line map (in the order sent): P1 = 1, 38, 61-90; P2 = 1, 19, 34-67; P3 = 1-36. Line 90 is empty and is the last visible line; the photos show nothing after it, so it is probably the end of the file (not confirmed by you this time).

---

## `rl_a4_b13_check_summary.md` (lines 1-90)

````
1   # RL A4 deterioration B13 check - numbers summary
2
3   Run: `kedro run --env=dev --pipeline=crx_rl_a4_deterioration_b13_check`
4   Model: rl_60_180 | dlq_min=3 | dlq_max=6 | horizon=1 month | snapshot: 2026 August
5   Result: 5 of 5 tasks completed, 121.9 sec
6
7   ## 1. New det_state distribution (total accounts = 3,985)
8
9   | det_state                  |     n |     % |
10  |----------------------------|------:|------:|
11  | straight_roller_seasoned   | 1,349 | 33.9% |
12  | slow_roller                |   933 | 23.4% |
13  | straight_roller_early_life |   700 | 17.6% |
14  | stabilized                 |   411 | 10.3% |
15  | repeat_delinquent          |   363 |  9.1% |
16  | early_payment_default      |   229 |  5.7% |
17  | **Total**                  | 3,985 |  100% |
18
19  ## 2. Old x new state
20
21  | old                        | new                        |    n |     % |
22  |----------------------------|----------------------------|-----:|------:|
23  | early_payment_default      | early_payment_default      |  229 |  5.7% |
24  | repeat_delinquent          | repeat_delinquent          |  174 |  4.4% |
25  | slow_roller                | repeat_delinquent          |    2 |  0.1% |
26  | slow_roller                | slow_roller                |  612 | 15.4% |
27  | stabilized                 | stabilized                 |  411 | 10.3% |
28  | straight_roller_early_life | straight_roller_early_life |  552 | 13.9% |
29  | straight_roller_seasoned   | straight_roller_seasoned   |  911 | 22.9% |
30  | unknown                    | repeat_delinquent          |  187 |  4.7% |
31  | unknown                    | slow_roller                |  321 |  8.1% |
32  | unknown                    | straight_roller_early_life |  148 |  3.7% |
33  | unknown                    | straight_roller_seasoned   |  438 | 11.0% |
34
35  Derived: old "unknown" = 1,094 accounts (27.5%), all reassigned to a named state.
36  Only 2 accounts (0.1%) moved between named states (slow_roller -> repeat_delinquent).
37
38  ## 3. loan_type x new state (n)
39
40  | loan_type     | early_pay_def | repeat_delinq | slow_roller | stabilized |
41  |---------------|--------------:|--------------:|------------:|-----------:|
42  | Auto          |            48 |           187 |         331 |        162 |
43  | Personal      |           125 |           109 |         315 |         94 |
44  | Personal Cash |            56 |            67 |         287 |        155 |
45
46  | loan_type     | straight_early_life | straight_seasoned |
47  |---------------|--------------------:|------------------:|
48  | Auto          |                 200 |               436 |
49  | Personal      |                 284 |               470 |
50  | Personal Cash |                 216 |               443 |
51
52  Same table as % of all 3,985 accounts:
53
54  | loan_type     |  EPD | RepDel | Slow | Stab | EarlyLife | Seasoned |
55  |---------------|-----:|-------:|-----:|-----:|----------:|---------:|
56  | Auto          | 1.2% |   4.7% | 8.3% | 4.1% |      5.0% |    10.9% |
57  | Personal      | 3.1% |   2.7% | 7.9% | 2.4% |      7.1% |    11.8% |
58  | Personal Cash | 1.4% |   1.7% | 7.2% | 3.9% |      5.4% |    11.1% |
59
60  Loan type totals: Auto 1,364 | Personal 1,397 | Personal Cash 1,224.
61
62  ## 4. Restructure check
63
64  Restructure flag set: 67 accounts
65
66  | loan_type     | stitched | blind |  n |     % |
67  |---------------|---------:|------:|---:|------:|
68  | Personal      |        0 |     1 |  2 |  3.0% |
69  | Personal      |        1 |     0 | 17 | 25.4% |
70  | Personal Cash |        1 |     0 | 48 | 71.6% |
71
72  | old_blind | blind |     n |     % |
73  |----------:|------:|------:|------:|
74  |         0 |     0 | 3,918 | 98.3% |
75  |         1 |     0 |    65 |  1.6% |
76  |         1 |     1 |     2 |  0.1% |
77
78  - blind old x new: stabilized -> stabilized = 2 (100.0%)
79  - Stitched without the flag: 0
80
81  ## 5. Unknown check
82
83  - unknown count (new output): 0
84  - route x loan_type table: empty
85
86  ## Notes
87
88  - Spark/YARN WARN lines (native-hadoop, HiveConf, "User balzsv not found" on one
89    executor container) are environment noise; they carry no numbers and the run succeeded.
90
````

## Notes on specific spots
- Checks I ran on the transcription: section 1 sums to 3,985; old x new (lines 23-33) sums to 3,985, with 1,094 old-unknown rows (187 + 321 + 148 + 438, matches line 35); loan-type rows (lines 42-50) sum to 1,364 / 1,397 / 1,224 as stated on line 60; the restructure table (lines 68-70) sums to 67; the old_blind x blind table (lines 74-76) sums to 3,985 (3,918 + 65 + 2).
- Meaning (my reading, not file text): `old_blind` / `blind` are the restructure blind-spot flag before and after the B13 change; 65 accounts go from blind to not blind (the 65 stitched), 2 stay blind. This agrees with the 65 of 67 stitched in handoff 29.
- Lines 68-69: loan_type reads "Personal" twice (stitched 0 / blind 1, then stitched 1 / blind 0), as printed.
- Line 17 shows the total row as `**Total**` in bold markdown, as printed.
- Compared with handoff 29 (B11): the det_state mix and the old x new table are identical; the loan-type counts are the same (the % table here uses short headers EPD, RepDel, Slow, Stab, EarlyLife, Seasoned).
- Column padding in the code block is mine; the `|` bars and values are as shown.
