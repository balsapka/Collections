# Handoff 20: `tmp_validation/a1_b08_cc_check_run_summary_2026-10-29.md` (photos 80-85), 2026-10-30

## Context for Claude Code
- Source: 6 phone photos of the VS Code editor (workspace `retail.collections.risk_profiling`, Dev Container: cdp-devcontainer:latest @ 10.119.132.99), taken 2026-10-30 ~09:41 Dubai. Tabs: `pipeline_registry.py`, `a1_b08_cc_check_run_summary_2026-10-29.md` (U = untracked, active). Branch `feature/persona_redesign_b01*`. Status bar: Ln 1, Col 1, Spaces: 2, Markdown.
- Title: "A1 Ability B08 Check, CC Pipeline (run of 2026-10-29)". The CC (`cc_60_180`) b08 check run of the new A1 ability engine: new state distribution, old vs new, step-by-step attribution, reasons and signals, source depth, takeaways. Follows handoffs 1-19; it is the new-engine counterpart of the older A1 summaries (handoffs 2, 4, 7, 12).
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file and the run JSON.
- Photos overlap and are merged into source lines 1-152. Photo-to-line map: photo 80 = lines 103-152; photo 81 = lines 101-132; photo 82 = lines 84-115; photo 83 = lines 51-93; photo 84 = lines 1, 11-64; photo 85 = lines 1-36. The chat order was 103-152, 101-132, 84-115, 51-93, 11-64, 1-36; here the file is merged by line number.
- Markdown tables are shown as in the editor.

---

## `a1_b08_cc_check_run_summary_2026-10-29.md` (lines 1-152)

````
1   # A1 Ability B08 Check, CC Pipeline (run of 2026-10-29)
2
3   ## Run
4
5   - 11 of 11 nodes completed, pipeline succeeded in 2690 sec (~45 min). The slow nodes were
6     `describe_a1_sources` (~4 min) and `explain_a1_changes` (~38 min).
7   - Nodes: obs_base, 5 signal builders (distress, eosb, income, liquidity anchor, liquidity),
8     `build_a1_ability`, and 4 checks (compare, report, sources, changes).
9   - Base: month 2026-08-31, 19292 accounts, 18731 CIFs. New and old keys are identical (0 new-only, 0 old-only).
10
11  ## 1. New a1_state (n = 19292)
12
13  | a1_state | n | % |
14  |---|---|---|
15  | high | 37 | 0.2 |
16  | moderate | 277 | 1.4 |
17  | low | 4670 | 24.2 |
18  | unknown | 14308 | 74.2 |
19
20  Share by month (%), Jan to Aug 2026. The mix is stable.
21
22  | month | n | high | moderate | low | unknown |
23  |---|---|---|---|---|---|
24  | 2026-01 | 14664 | 0.34 | 2.15 | 24.28 | 73.23 |
25  | 2026-02 | 14576 | 0.33 | 2.15 | 24.06 | 73.46 |
26  | 2026-03 | 14455 | 0.27 | 1.93 | 23.98 | 73.82 |
27  | 2026-04 | 14671 | 0.25 | 2.26 | 23.56 | 73.93 |
28  | 2026-05 | 15890 | 0.27 | 2.25 | 25.44 | 72.03 |
29  | 2026-06 | 16982 | 0.22 | 2.05 | 25.64 | 72.09 |
30  | 2026-07 | 18397 | 0.23 | 1.77 | 26.28 | 71.71 |
31  | 2026-08 | 19292 | 0.19 | 1.44 | 24.21 | 74.17 |
32
33  Range over the months: high 0.19 to 0.34, moderate 1.44 to 2.26, low 23.56 to 26.28, unknown 71.71 to 74.17.
34
35  ## 2. Old vs new (Aug 2026)
36
37  | old | new | n | % |
38  |---|---|---|---|
39  | high | high | 8 | 0.0 |
40  | low | high | 1 | 0.0 |
41  | low | low | 4532 | 23.5 |
42  | low | moderate | 101 | 0.5 |
43  | low | unknown | 2350 | 12.2 |
44  | moderate | high | 28 | 0.1 |
45  | moderate | moderate | 176 | 0.9 |
46  | unknown | low | 138 | 0.7 |
47  | unknown | unknown | 11958 | 62.0 |
48
49  Net: 2618 rows move (13.6%). 2350 of them are old low to new unknown (89.8% of the movers).
50
51  ## 3. Step-by-step attribution (rows per state)
52
53  | step | high | moderate | low | unknown |
54  |---|---|---|---|---|
55  | s0_old_rules | 8 | 204 | 6984 | 12096 |
56  | s1_salary_dating | 28 | 264 | 6904 | 12096 |
57  | s2_window_total | 36 | 277 | 6883 | 12096 |
58  | s3_activity_gate | 36 | 277 | 4822 | 14157 |
59  | s4_bureau_repeats | 37 | 277 | 4670 | 14308 |
60
61  | transition | rows moved | detail |
62  |---|---|---|
63  | s0 to s1 (salary dating) | 100 | low to moderate 80, moderate to high 20 |
64  | s1 to s2 (window total) | 29 | low to moderate 21, moderate to high 8 |
65  | s2 to s3 (activity gate) | 2337 | low to unknown 2199, unknown to low 138 |
66  | s3 to s4 (bureau repeats) | 153 | low to unknown 151, low to moderate 1, moderate to high 1 |
67
68  - The activity gate is the main driver. It accounts for 2337 of the 2619 step moves.
69  - Consistency checks: s0 vs the old output 0 differ, s4 vs the new output 0 differ, income series vs the signals 0 differ.
70
71  ## 4. Report: reasons and signals
72
73  - Income (M4): internal_only x stable 203 (1.1%), internal_only x weak 237 (1.2%), neither x none 18852 (97.7%).
74  - CASA relationship x a1_state (M5):
75
76  | CASA | high | moderate | low | unknown |
77  |---|---|---|---|---|
78  | active_casa | 37 | 214 | 3380 | 0 |
79  | dormant_casa | 0 | 63 | 1055 | 8007 |
80  | no_casa | 0 | 0 | 235 | 6301 |
81
82  - Liquidity level (M6): adequate 196 (1.0%), weak 342 (1.8%), none 18754 (97.2%).
83  - Max monthly CASA balance in W (M6): none 14021, <1000 4775, 1000-3000 254, >=3000 242. Only 230 (1.2%) cover max(3000, anchor).
84  - Unknown reason (M7): dormant_casa 8007 (56.0%), no_casa 6301 (44.0%).
85  - Low reason (M8): 0pt_active_casa 2605 (55.8%), 0pt_distress 1531 (32.8%), 1pt 470 (10.1%), 2-3pt_distress 64 (1.4%).
86  - Moderate and high (M9):
87
88  | state | income | liquidity | distress | n | % |
89  |---|---|---|---|---|---|
90  | high | stable | adequate | 0 | 37 | 11.8 |
91  | moderate | none | adequate | 0 | 103 | 32.8 |
92  | moderate | stable | none | 0 | 95 | 30.3 |
93  | moderate | stable | weak | 0 | 29 | 9.2 |
94  | moderate | weak | weak | 0 | 23 | 7.3 |
95  | moderate | weak | adequate | 0 | 16 | 5.1 |
96  | moderate | stable | adequate | 1 | 11 | 3.5 |
97
98  - Distress parts in W (M10): none 17616 (91.3%), dds 596 (3.1%), bureau 483 (2.5%), cheque 451 (2.3%), cheque+dds 109 (0.6%), dds+bureau 21, cheque+bureau 15, all three 1.
99  - Distress parts x a1_state: every distress combination lands in low, except 11 rows in moderate (cheque 3, dds 8).
100 - EOSB (M11): result 1 on 25 rows (low 15, moderate 1, unknown 9). Liquidity level on those: adequate 1, weak 1, none 23.
101 - Liquidity anchor (M11): present on 100% of rows, p10 / p50 / p90 = 128 / 837 / 2342. It raises the income x CASA x card-payment floor on 4555 rows (23.6%).
102
103 ## 5. Source depth (month_end)
104
105 | source | range | base CIFs from |
106 |---|---|---|
107 | feat_cif_internal_salary_monthly | 2024-09 to 2026-08 | 2024-09 |
108 | feat_cif_bureau_salary_monthly | 2020-08 to 2026-06 | 2020-11 |
109 | feat_cif_casa_balance_monthly | 2025-02 to 2026-09 | 2025-02 |
110 | feat_cif_casa_activity_monthly | 2025-02 to 2026-10 | 2025-02 |
111
112 - Internal salary (>= 1000) history:
113
114 | history | n | % |
115 |---|---|---|
116 | in W | 440 | 2.3 |
117 | last m4-6 | 3094 | 16.0 |
118 | last m7-12 | 3599 | 18.7 |
119 | last m13-24 | 1941 | 10.1 |
120 | never | 10218 | 53.0 |
121
122  Salary in W gives 37 high, 174 moderate and 229 low. "never" gives 8772 unknown (45.5% of base).
123 - Bureau (M3): record_not_linked 17962 (93.1%), no_record 1209 (6.3%), linked_never_salary 63 (0.3%), salary_ever_none_in_W 58 (0.3%). The bureau-to-CIF bridge is almost entirely unlinked.
124 - CASA legs in W (2026-06 to 2026-08) by lane (legs, CIFs):
125
126 | lane | legs | CIFs |
127 |---|---|---|
128 | signal | 101967 | 1150 |
129 | card_spend | 25724 | 1062 |
130 | economic | 18144 | 2708 |
131 | wash | 7107 | 2258 |
132 | ambiguous | 5223 | 2440 |
133 | fee_interest | 3893 | 1360 |
134 | own_loan | 2054 | 750 |
135 | card_payment | 1889 | 1374 |
136 | group_internal | 859 | 238 |
137 | refund | 387 | 198 |
138 | reversal | 293 | 129 |
139 | unclassified | 39 | 3 |
140
141  The ambiguous lane is almost all `MISCELLANEOUS` (5221 legs). The unclassified lane is `POS TRANSACTIONS` (39 legs).
142 - WM vs FTR, last 12 months: 56.2% of base CIFs have a WM row, a WM positive, an FTR leg and an FTR customer leg. 32.2% have a WM row only. 1.8% have neither WM nor FTR.
143
144 ## Takeaways
145
146 - The new rules cut low from 6984 to 4670 and raise unknown from 12096 to 14308. Unknown now covers 74.2% of the base, so most accounts carry no ability signal.
147 - Unknown is a data-coverage issue. 56% of it is a dormant CASA and 44% is no CASA.
148 - Salary dating and the window total add 129 rows to moderate and high. High is 37 accounts, all with active CASA and stable income plus adequate liquidity.
149 - Low is driven by CASA activity (55.8%) and distress (32.8%). A distress signal almost never leaves low.
150 - The Jan to Aug mix is stable, so there is no monthly drift to explain.
151 - Open points: 93% of base CIFs are not linked in the bureau bridge, and 5221 `MISCELLANEOUS` CASA legs are ambiguous.
152
````

## Notes on specific spots
- Line breaks: in the editor, long bullets soft-wrap; here each source line is kept as one line (lines 5-9 keep the two-line wrapping shown in the photo).
- Lines 49 and 68: the net movers are 2618 (line 49) while the step moves sum to 2619 (line 68: 100+29+2337+153). Both copied as shown; a net of 2618 vs gross 2619 is plausible, since one row moves in two steps (the 1 `low to moderate` in s3 to s4 and the 1 `moderate to high` in the same step can come from the same row), but this is my reading, not file text.
- Lines 55-59 and 78-80 check out: each column totals 19,292 and the CASA table sums match the state counts (high 37, moderate 277, low 4670, unknown 14308).
- Line 123: "Bureau (M3)" 17962 + 1209 + 63 + 58 = 19,292.
- Line 83 uses `<1000` and `>=3000` as shown; line 112 uses `>= 1000`.
- Line 122, 141 start with a leading space in the file (continuation lines without a dash), shown as in the photos.
- Lines 126-139: lane counts are dense; verify against the JSON.
- Terminal and taskbar are not in these photos.
