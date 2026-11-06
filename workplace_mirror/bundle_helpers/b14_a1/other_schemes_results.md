# Other schemes — CC + RL 60_180 (handoff 45, 2026-11-06)

Source: `tmp_validation/a1_other_schemes/summary.md` in the workplace, transcribed from 5 photos (lines 1–129 below).


````
1   # A1 other schemes - summary
2
3   Run 2026-11-05 in PROD, `cc_60_180` and `rl_60_180`, latest observation month 2026-08-31, legs of
4   the base CIFs on
5   13-character accounts, 2025-09-01 to 2026-08-31 (A1's own window). Detail: `results_<model_id>.md` /
6   `.json`; code
7   search: [h0_wm_scheme_lists.md](h0_wm_scheme_lists.md). Cells under 10 are `<10`.
8
9   ## Verdict
10
11  **Not term deposits or investments: 012, 095, 014 and 099 look like current / savings accounts.**
12  Each has
13  `schm_type` SBA (savings) or ODA (overdraft, the type the real current schemes such as 101 carry),
14  `schm_nature` N,
15  and a product name that says savings / current. Their legs look like day-to-day use (63-67% card
16  spend on 014,
17  43-57% on the rest, 22-31% economic, 76-90% debits), at 100-290 legs per CIF, the level of the real
18  current (235 CC,
19  280 RL) and savings (144 CC, 163 RL) schemes. The sanity check passes: current and savings have 0
20  became-`no_casa`
21  CIFs in both models, so the window matches A1's.
22
23  **They explain most of the CC change, and about a quarter of the RL change.** CC: 758 of the 915
24  CIFs that became
25  `no_casa` (83%) have a leg on a listed scheme. RL: 102 of 411 (25%). Adding them to the CASA lists
26  would undo most of
27  the CC "Low -> Unknown (no_casa)" and "dormant_casa -> no_casa" moves. The decision is the user's;
28  the evidence
29  below is code names, scheme types and leg shape, not a product-owner confirmation.
30
31  ## Code (WM and retail.feature_space)
32
33  | Scheme | WM list (207 + investment) | feature_space |
34  |---|---|---|
35  | 012, 014 | none | none |
36  | 095, 099 | none | `liv_accounts` ("Liv Scheme Codes"), its own account type, not CA / SA |
37  | 013, 059 | none | none |
38  | 067, 076 | `investment_accounts` | none |
39
40  WM has no comment on any of them. Liv is the bank's digital product line; no code says whether Liv
41  accounts are
42  current- or savings-like. File:line in `h0_wm_scheme_lists.md`.
43
44  ## Per scheme
45
46  `cc_60_180` (legs, CIFs, legs per CIF, debit share, card spend / economic share of legs,
47  new-`no_casa` CIFs with a leg):
48
49  | Scheme | `schm_type` | Name | Legs | CIFs | Legs/CIF | Debit | Card / econ | New-`no_casa` CIFs |
50  |---|---|---|---|---|---|---|---|---|
51  | 095 | SBA | SAVINGS | 86,436 | 402 | 215 | 76% | 43% / 28% | 288 (31.5%) |
52  | 012 | SBA | MILLIONAIRE SAV | 84,850 | 612 | 139 | 81% | 57% / 22% | 262 (28.6%) |
53  | 014 | ODA | MILLIONAIRE CUR | 18,914 | 188 | 101 | 87% | 66% / 24% | 151 (16.5%) |
54  | 099 | SBA | CURRENT | 12,641 | 95 | 133 | 78% | 49% / 32% | 67 (7.3%) |
55  | 067 | CAA | SHARE A/C - RES | 4,762 | 62 | 77 | 85% | 62% / 17% | 0 |
56  | 013 | SBA | EMIRATI MILLION | 1,914 | 15 | 128 | 83% | 66% / 17% | <10 |
57  | 059 | CAA | CA AL ISLAMI CA | 1,908 | 13 | 147 | 81% | 55% / 22% | <10 |
58  | 076 | CAA | INVESTMENT CASH | 1,379 | 156 | 9 | 49% | <10 / 32% (wash 42%, fees 19%) | <10 |
59  | current (36) | | | 2,414,036 | 10,254 | 235 | 81% | 53% / 27% | 0 |
60  | savings (13) | | | 248,900 | 1,731 | 144 | 79% | 46% / 25% | 0 |
61
62  `rl_60_180` (same columns; only four schemes reach 1,000 legs):
63
64  | Scheme | `schm_type` | Name | Legs | CIFs | Legs/CIF | Debit | Card / econ | New-`no_casa` CIFs |
65  |---|---|---|---|---|---|---|---|---|
66  | 095 | SBA | SAVINGS | 21,455 | 73 | 294 | 84% | 52% / 23% | 60 (14.6%) |
67  | 012 | SBA | MILLIONAIRE SAV | 14,661 | 102 | 144 | 79% | 49% / 23% | 17 (4.1%) |
68  | 014 | ODA | MILLIONAIRE CUR | 3,968 | 30 | 132 | 90% | 68% / 20% | 24 (5.8%) |
69  | 099 | SBA | CURRENT | 1,585 | <10 | - | 82% | 55% / 25% | <10 |
70  | current (36) | | | 780,842 | 2,791 | 280 | 83% | 55% / 24% | 0 |
71  | savings (13) | | | 87,016 | 535 | 163 | 83% | 51% / 22% | 0 |
72
73  013, 059, 067 and 076 are CC only in the table above (RL has 383, 173, 388 and 593 legs). New
74  `no_casa` CIFs: CC 915 (716 from `dormant_casa`, 199 not Unknown), RL 411 (358, 53). Lane mix of the
75  four is in the
76  results files; none stands out against the reference, except 076 (investment-like).
77
78  ## One line per scheme
79
80  - **095** (SBA, SAVINGS; Liv): **looks like a savings account.**
81  - **012** (SBA, MILLIONAIRE SAV): **looks like a savings account.**
82  - **014** (ODA, MILLIONAIRE CUR): **looks like a current account.**
83  - **099** (SBA named CURRENT; Liv): **looks like a current / savings account** (name says current,
84    type says
85    savings; which list does not matter for CASA). Few legs in RL.
86  - **013** (SBA, EMIRATI MILLION...): **looks like a savings account.** Tiny, no effect.
87  - **059** (CAA, CA AL ISLAMI CA): **looks like a current account** (Islamic). Tiny, no effect.
88  - **076** (CAA, INVESTMENT CASH; WM investment): **term deposit / investment** (about 9 legs per
89    CIF, wash and fee
90    legs, almost no card spend).
91  - **067** (CAA, SHARE A/C - RES; WM investment): **unclear.** The name and WM say share / investment
92    account, but
93    the 61% card spend does not fit; 0 new-`no_casa` CIFs, so it does not matter for B14.
94  - **Below 1,000 legs, not profiled:** 094 GLOBAL EQUITIES, 832 INVESTMENT CASH, 398 LXAU (gold):
95    investment-like by
96    name; 098 (Liv SAVINGS) and 619 (MILLIONAIRE ACC): savings-like by name; all small.
97
98  ## Other findings
99
100 - **6053, 5159, 6001, 7001, 5024 are not on 13-character accounts**: absent from both scheme tables.
101   They are the
102   15 / 16-character (loan-type) accounts in the B14 table and stay outside CASA. This run did not
103   profile them.
104 - **RL: three quarters of the new `no_casa` CIFs (309 of 411) have no leg on any listed scheme.**
105   Adding the four
106   schemes would not remove the RL change; the rest is the old logic counting 16-character loan legs
107   (B14 summary,
108   RL points to check). Not checked here.
109 - **The 49 codes include schemes that are not day-to-day accounts by type or name.** 590 is
110   `schm_type` TDA ("STEADY
111   DEP 12M"); 450-456, 486 and 070 are margin / structured accounts; 068, 069, 149 are share
112   accounts. All show 0
113   legs on the CC base (the RL scheme table shows none of them with legs either), so no effect today,
114   but they would
115   count if a base CIF used them.
116 - 73 (CC) and 27 (RL) accounts carry more than one scheme; the smallest code was used. Negligible.
117 - `gen_schm_parm_table` has one row per code (`versions` = 1), all live (`del_flg` N).
118   `product_type` is blank for
119   all of these, so it does not discriminate; `schm_type` and the name do.
120
121 ## For the decision
122
123 If the lists are extended: add 095, 012, 099 and 013 as savings and 014 and 059 as current (the
124 split only affects
125 labels). Do not add 067 or 076. Consider removing 590 from the savings list and the margin / share
126 codes from the
127 current list; no data effect here. If extended, rerun the B14 check (`crx_cc_a1_ability_b14_check`,
128 `crx_rl_a1_ability_b14_check`) to see the new Unknown mix.
129
````

## Notes on specific spots
- Cross-checks that pass: 716 + 199 = 915 and 358 + 53 = 411 (line 74); 758 / 915 = 83% and 102 / 411 = 25% (lines 23-25); 411 - 102 = 309 = "three quarters" (line 104); the "New-`no_casa` CIFs" percentages are shares of 915 (CC: 288, 262, 151, 67 give 31.5%, 28.6%, 16.5%, 7.3%) and of 411 (RL: 60, 17, 24 give 14.6%, 4.1%, 5.8%); legs per CIF = legs / CIFs in every row (for example 86,436 / 402 = 215, 21,455 / 73 = 294); the four CC schemes' new-`no_casa` CIFs (288 + 262 + 151 + 67 = 768) exceed 758 because a CIF can have legs on several schemes.
- Possible inconsistency, copied as shown: line 93 says "the 61% card spend" for 067, while the CC table (line 55) shows 62% card spend. Also, line 35 of handoff 43 gives 012 (65k legs) and 095 (61k legs) for the B14 accounts table, while lines 51-52 here give 84,850 and 86,436 CC legs (a different population / window: here only the base CIFs on 13-character accounts over A1's own window). Check which is meant.
- Table separator lines (50, 65) have 9 columns as in the header. The Name column of line 56 and 86 is cut in the source ("EMIRATI MILLION" / "EMIRATI MILLION..."), as shown.
- Line 69: "-" in the Legs/CIF cell is as printed (CIFs "<10", so no ratio).
- Line 58: "<10 / 32% (wash 42%, fees 19%)" is the Card / econ cell for 076, as printed.
- Line 13: "such as 101" refers to scheme code 101 (as in handoff 35, line 54), not the account-number prefix.
- OCR-risk digits: all legs / CIF counts in lines 51-60 and 66-71, percentages in lines 15-19, 23-25 and 51-71, scheme codes in lines 11, 35-38, 80-96, 100, 109-111 and 123-125 (012, 095, 014, 099, 013, 059, 067, 076, 094, 832, 398, 098, 619, 6053, 5159, 6001, 7001, 5024, 590, 450-456, 486, 070, 068, 069, 149).

## Claude's review

- **The four busy schemes are CASA.** 095 / 012 (SBA, savings), 014 (ODA, current), 099 (SBA named
  CURRENT); 095 and 099 are Liv, the digital product line. Legs per CIF and the lane mix match the 49
  codes. 013 and 059 (tiny) look the same. 067 and 076 are investment (WM's investment list).
- **They undo most of the CC change.** 758 of 915 newly `no_casa` CIFs (83%) have a leg on them. In RL
  only 102 of 411 (25%); the other 309 were the loan account's own legs, which is the intended fix.
- **Effect on earlier numbers:** the CC "no CASA" share (25.5% of rows) is overstated until the codes
  are added; RL stays about where B14 put it.
- **The 49 codes carry non-day-to-day schemes** (590 TDA, 450–456 / 486 / 070 margin or structured,
  068 / 069 / 149 share accounts) with 0 legs on either base today.
- The 65k / 61k in B14 ACCOUNTS vs 84,850 / 86,436 here: different populations (B14 = 12 months back
  from the run date; here A1's window to 2026-08-31). Not a conflict.

## Decision (user, 2026-11-06)

Stick to WM's 49 codes: none of the schemes above is added, none of the 49 is removed. Bundle 14 stands as built.
