# Handoff 59: `tmp_validation/persona_deck/fill_in.md` lines 1-212 (Persona deck - fill-in sheet: summary, A1-A4 mixes, Part 2 combos / tree / action / score / UC1 / pilot, notes, changes to the snippet) (4 photos), 2026-11-10

## Context for Claude Code
- Source: 4 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest`, workspace `retail.collections.risk_profiling`; menu bar shows "Help"). Tabs: `pipeline_registry.py`, `fill_in.md` (active, `U` = untracked, not in git yet). Breadcrumb `tmp_validation > persona_deck > fill_in.md > # Persona deck - fill-in sheet > ## Changes made to the snippet`.
- These are the `tmp_validation/persona_deck/` files that handoff 58 mentions as "not ours" (they appeared in `git status` during the wash-lane session). They hold the persona-deck numbers (cards `cc_60_180`, loans `rl_60_180`, 180+ runs `cc_180_plus`, `rl_180_plus`), produced by `persona_deck_numbers.py` (committed 5fc0e8f3), as a fill-in sheet in the format `slide · item · value · source table`. Follows handoffs 1-58.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photo-to-line map (in the order sent): photo 1 = lines 1, 155-212; photo 2 = lines 1, 92, 111-166; photo 3 = lines 1, 56-113; photo 4 = lines 1-59. Overlaps merged. Lines 1-212 are all covered; line 212 is the last (blank), I cannot tell whether the file continues.
- Lines 1 and 92 (in photo 2) and line 1 (photos 1, 3) are sticky-scroll headers of the editor, not extra lines.
- Source lines are hard-numbered in the editor. Bullets and paragraphs wrapped by the editor are shown as continuation lines with their own source number where the editor numbers them (the editor numbers every wrapped line here, so each line below is one source line).
- The segment name `rl_60_180` (loans) is printed in the editor font where `l` looks like `1`; I read it as `rl_..` (same as in handoffs 50-57). Check the real file.
- Written in the cloud workspace; saved to `~/Python/Collections/pics/claude_code_handoff_59.md` through the Mac link if it is up (see the chat reply); otherwise copy it there.

---

## `fill_in.md` (lines 1-212)

````
1   # Persona deck - fill-in sheet
2
3   Format: `slide · item · value · source table`. Source files: `deck_<model_id>.md`. Latest month = Aug 2026
4   (persona_end_date 2026-08-31); back-test = May 2026 states against Jun-Aug outcomes. Units are **accounts**
5   (the axis grain), not CIFs. "paid" = any payment of AED 100+ in the next 3 months. Deck axis names:
6   A1 Deterioration, A2 Locatability, A3 Payment credibility, A4 Ability.
7
8   ## Summary
9   - Summary · % of reachable 61-180 who are credible or able (A3 or A4 High/Moderate), cards · 53.2%
10    (AED 60.5m) · `summary` cc_60_180
11  - Summary · same, loans · 57.2% (AED 55.1m) · `summary` rl_60_180
12  - Summary · paid % range across tree leaves at 91-120, cards · 4.1% - 62.6% (leaves with ≥10 accounts;
13    low = never_paid/not_reachable, high = can_cure/credible_or_able) · `summary`, `tree_x_band` cc_60_180
14  - Summary · % of 180+ accounts with a positive signal, cards · 12.2% · `positive_signal` cc_180_plus
15  - Summary · % of 180+ accounts with a positive signal, loans · 12.2% · `positive_signal` rl_180_plus
16  - Summary · each signal at 180+ (cards / loans) · payment AED 100+ 5.9% / 8.2%; kept or part-kept promise
17    1.4% / 2.4%; reachable 3.7% / 4.8%; ability High or Moderate 6.2% / 3.6% · `positive_signal`
18
19  ## A1 Deterioration
20  - A1 · family shares, cards 61-180 · can_cure 31.8% / stopped_suddenly 60.4% / never_paid 7.5% /
21    unknown 0.3% · `mix_a1_family` cc_60_180
22  - A1 · family shares, loans 61-180 · can_cure 42.8% / stopped_suddenly 51.4% / never_paid 5.7%
23    (reference 43 / 51 / 6: matches) · `mix_a1_family` rl_60_180
24  - A1 · paid within 3m, can_cure vs rest, overall, cards · 33.1% vs 11.3% (rest = stopped_suddenly +
25    never_paid + unknown; 11.1% without unknown) · `a1_family_outcome` cc_60_180
26  - A1 · paid within 3m, can_cure vs rest, overall, loans · 56.0% vs 35.8% · `a1_family_outcome` rl_60_180
27  - A1 · same within DPD band, cards (can_cure vs rest) · 61-90: 43.5% vs 19.0% · 91-120: 35.3% vs 11.6% ·
28    121-150: 28.3% vs 7.6% · 151-180: 10.9% vs 3.0% · `a1_family_x_band` cc_60_180
29  - A1 · same within DPD band, loans (can_cure vs rest) · 61-90: 66.3% vs 45.7% · 91-120: 61.6% vs 33.7% ·
30    121-150: 39.6% vs 22.4% · 151-180: 37.2% vs 17.9% · `a1_family_x_band` rl_60_180
31
32  ## A2 Locatability
33  - A2 · 180+ reachable / in country / both, cards · 3.7% (11,716) / 3.2% (10,099) / 0.7% (2,377) ·
34    `a2_positive` cc_180_plus
35  - A2 · 180+ reachable / in country / both, loans · 4.8% (2,653) / 3.6% (1,966) / 1.3% (704) ·
36    `a2_positive` rl_180_plus
37  - A2 · 61-180 matrix, cards (location × reachability, % of accounts) · `mix_a2_matrix` cc_60_180
38    - Skip: Non-Reachable 31.7 / Reachable 6.2 / Unknown 6.1
39    - In Country: Non-Reachable 13.6 / Reachable 8.5 / Unknown 1.9
40    - Unknown location: Non-Reachable 22.3 / Reachable 6.3 / Unknown 3.4
41  - A2 · 61-180 matrix, loans · `mix_a2_matrix` rl_60_180
42    - Skip: Non-Reachable 28.5 / Reachable 8.1 / Unknown 6.8
43    - In Country: Non-Reachable 14.2 / Reachable 10.2 / Unknown 2.7
44    - Unknown location: Non-Reachable 14.9 / Reachable 7.9 / Unknown 6.8
45  - A2 · cells more than 1 pt from the reference · none. Cards In Country × Reachable 8.5 (ref 8.5),
46    Skip × Non-Reachable 31.7 (ref 31.7); loans 10.2 (ref 10.2), 28.5 (ref 28.5)
47
48  ## A3 Payment credibility
49  - A3 · High / Moderate / Low, cards 61-180 · 2.5% / 19.4% / 66.5%; Unknown 11.5% (above 1%) ·
50    `mix_a3_band` cc_60_180
51  - A3 · High / Moderate / Low, loans 61-180 · 4.9% / 27.9% / 60.6%; Unknown 6.6% (above 1%) ·
52    `mix_a3_band` rl_60_180
53  - A3 · roll % at 91-120, High vs Low, cards · 42.4% vs 89.9% (High n=144, Low n=2,419; paid 75.0% vs
54    14.7%) · `a3_band_x_band` cc_60_180
55  - A3 · untested share, cards (no concluded promise) · 59.0% (loans 67.1%) · `a3_untested` cc_60_180
56
57  ## A4 Ability
58  - A4 · High / Moderate / Low / Unknown, cards 61-180 · 0.2 / 14.4 / 28.9 / 56.6 % · `mix_a4_band` cc_60_180
59  - A4 · loans 61-180 · 0.3 / 8.9 / 44.7 / 46.1 % · `mix_a4_band` rl_60_180
60  - A4 · cards 180+ · 0.0 / 6.2 / 6.4 / 87.4 % · `mix_a4_band` cc_180_plus
61  - A4 · loans 180+ · 0.0 / 3.5 / 6.9 / 89.5 % · `mix_a4_band` rl_180_plus
62  - A4 · % of card accounts at 61-180 that are Unknown · 56.6% · `mix_a4_band` cc_60_180
63  - A4 · % of loan accounts at 180+ that are High or Moderate · 3.6% (1,979 of 55,371) ·
64    `mix_a4_band` rl_180_plus
65
66  ## Part 2 — combinations (family | location | reachability | credibility | ability)
67  - Combos · possible / non-empty / covering 80% / under 0.5%, cards 61-180 · 432 / 297 / 57 / 242 ·
68    `combos` cc_60_180
69  - Combos · same, loans 61-180 · 432 / 199 / 55 / 136 · `combos` rl_60_180
70  - Combos · top 8, cards 61-180 (share % · paid %) · `combos_top` cc_60_180
71    1. stopped_suddenly | skip | non_reachable | low | unknown · 13.8 · 3.5
72    2. stopped_suddenly | unknown | non_reachable | low | unknown · 6.1 · 5.5
73    3. stopped_suddenly | skip | non_reachable | low | low · 5.1 · 6.6
74    4. never_paid | unknown | non_reachable | unknown | unknown · 2.8 · 0.4
75    5. can_cure | skip | non_reachable | low | unknown · 2.5 · 7.7
76    6. stopped_suddenly | in_country | non_reachable | low | unknown · 2.4 · 10.4
77    7. stopped_suddenly | skip | unknown | low | unknown · 2.4 · 4.5
78    8. stopped_suddenly | in_country | non_reachable | low | low · 2.4 · 18.2
79
80  ## Part 2 — tree (family × nuance leaf, cards 61-180; share % · paid %) · `tree` cc_60_180
81  - stopped_suddenly · not_reachable · 50.8 · 8.4
82  - stopped_suddenly · neither · 6.1 · 23.0
83  - stopped_suddenly · credible_or_able · 3.5 · 34.0
84  - can_cure · not_reachable · 21.2 · 20.8
85  - can_cure · neither · 3.1 · 35.0
86  - can_cure · credible_or_able · 7.5 · 58.0
87  - never_paid · not_reachable · 6.8 · 3.0
88  - never_paid · neither · 0.5 · 12.0
89  - never_paid · credible_or_able · 0.1 · 38.7 (n=23 at latest, 31 in back-test; thin)
90  - unknown family · not_reachable 0.3 · 13.4; the other two unknown leaves are under 10 accounts (suppressed)
91
92  ## Part 2 — action segments · `action`
93  Share % of Aug accounts, AED m of Aug exposure, paid % from the May back-test.
94
95  Cards 61-180 (`cc_60_180`):
96
97  | segment | share % | AED m | paid % |
98  |---|---|---|---|
99  | never_paid | 7.5 | 60.1 | 4.6 |
100 | not_reachable | 72.2 | 372.8 | 12.6 |
101 | cure_reach_cred | 6.3 | 35.9 | 61.1 |
102 | stopped_reach_means | 1.5 | 7.3 | 27.9 |
103 | reach_notcred_means | 1.1 | 5.6 | 39.8 |
104 | other | 11.3 | 62.3 | 29.9 |
105
106 Loans 61-180 (`rl_60_180`):
107
108 | segment | share % | AED m | paid % |
109 |---|---|---|---|
110 | never_paid | 5.7 | 38.1 | 24.2 |
111 | not_reachable | 68.5 | 294.6 | 41.0 |
112 | cure_reach_cred | 10.8 | 38.4 | 76.1 |
113 | stopped_reach_means | 0.9 | 3.9 | 57.9 |
114 | reach_notcred_means | 0.6 | 1.3 | 69.0 |
115 | other | 13.5 | 73.2 | 48.1 |
116
117 - 180+ segment (any positive signal) · cards 12.2% of accounts (38,763); loans 12.2% (6,780) ·
118   `positive_signal` 180+ runs. AED and paid % for this group are not in the output (see notes).
119 - 180+ action split (for reference) · cards: not_reachable 92.1% / never_paid 4.4% / other 2.6% / the three
120   reachable segments 0.9% together; loans: 91.1% / 4.2% / 3.2% / 1.5% · `action` 180+ runs
121
122 ## Part 2 — risk score · `score_action`
123 Spread across DPD bands (pts) and band-only AUC. Verdict rule: "yes" if paid or rolled spread ≥ 15 pts or
124 either AUC ≥ 0.65; "no" if both spreads < 5 and both AUCs < 0.58; else "maybe".
125
126 Cards 61-180 (`cc_60_180`):
127
128 | segment | n | paid spread | rolled spread | AUC paid | AUC rolled | verdict |
129 |---|---|---|---|---|---|---|
130 | never_paid | 1,247 | 8.7 | 5.8 | 0.726 | 0.698 | yes |
131 | not_reachable | 10,559 | 18.1 | 9.6 | 0.675 | 0.627 | yes |
132 | cure_reach_cred | 1,479 | 18.8 | 15.7 | 0.555 | 0.565 | yes |
133 | stopped_reach_means | 340 | 11.3 | 20.5 | 0.552 | 0.597 | yes |
134 | reach_notcred_means | 249 | 25.1 | 39.6 | 0.597 | 0.666 | yes |
135 | other | 2,016 | 22.4 | 18.0 | 0.598 | 0.607 | yes |
136
137 Loans 61-180 (`rl_60_180`):
138
139 | segment | n | paid spread | rolled spread | AUC paid | AUC rolled | verdict |
140 |---|---|---|---|---|---|---|
141 | never_paid | 186 | 36.8 | 13.7 | 0.730 | 0.684 | yes |
142 | not_reachable | 1,995 | 24.8 | 15.2 | 0.610 | 0.605 | yes |
143 | cure_reach_cred | 351 | 24.5 | 12.2 | 0.576 | 0.559 | yes |
144 | stopped_reach_means | 38 | n/a (cells <10) | n/a | 0.643 | 0.604 | maybe (n=38) |
145 | reach_notcred_means | 29 | n/a (cells <10) | n/a | 0.733 | 0.718 | yes by rule; n=29, unreliable |
146 | other | 497 | 15.6 | 25.0 | 0.556 | 0.637 | yes |
147
148 - On the 180+ runs the score test cannot be read: all accounts sit in the one 181+ band, spreads are empty
149   and AUC is 0.5.
150
151 ## Part 2 — UC1
152 - UC1 · % of accounts at 61-180 with a right-party contact in the last 3 months · cards 41.0% (7,910);
153   loans 51.7% (2,060) · `uc1_contact`. (At 180+: cards 4.2%, loans 6.3%.)
154
155 ## Part 2 — pilot
156 Monthly accounts per segment (Jun / Jul / Aug 2026) · `volume`. Arm n = accounts per arm for a 2-arm test,
157 two-sided α = 0.05, 80% power, +5 pts on the segment's paid %.
158
159 Cards 61-180 (`cc_60_180`):
160
161 | segment | Jun | Jul | Aug | paid base | arm n |
162 |---|---|---|---|---|---|
163 | never_paid | 1,239 | 1,349 | 1,440 | 4.6% | 411 |
164 | not_reachable | 11,612 | 13,117 | 13,936 | 12.6% | 802 |
165 | cure_reach_cred | 1,391 | 1,293 | 1,224 | 61.1% | 1,450 |
166 | stopped_reach_means | 339 | 337 | 299 | 27.9% | 1,325 |
167 | reach_notcred_means | 252 | 220 | 217 | 39.8% | 1,529 |
168 | other | 2,149 | 2,081 | 2,176 | 29.9% | 1,372 |
169
170 Loans 61-180 (`rl_60_180`):
171
172 | segment | Jun | Jul | Aug | paid base | arm n |
173 |---|---|---|---|---|---|
174 | never_paid | 210 | 226 | 229 | 24.2% | 1,225 |
175 | not_reachable | 2,333 | 2,474 | 2,731 | 41.0% | 1,540 |
176 | cure_reach_cred | 362 | 394 | 430 | 76.1% | 1,053 |
177 | stopped_reach_means | 34 | 33 | 35 | 57.9% | 1,498 |
178 | reach_notcred_means | 21 | 34 | 23 | 69.0% | 1,276 |
179 | other | 554 | 567 | 537 | 48.1% | 1,566 |
180
181 Both arms fit in one month of Aug volume (2 × arm n ≤ Aug accounts): cards never_paid (822 ≤ 1,440) and
182 not_reachable (1,604 ≤ 13,936) only. Everything else needs several months pooled, and repeat accounts across
183 months do not add independent samples:
184 - Cards: cure_reach_cred (2,900 vs 1,224 a month), other (2,744 vs 2,176), stopped_reach_means (2,650 vs 299),
185   reach_notcred_means (3,058 vs 217).
186 - Loans: not_reachable (3,080 vs 2,731), never_paid (2,450 vs 229), cure_reach_cred (2,106 vs 430),
187   other (3,132 vs 537), stopped_reach_means and reach_notcred_means (about 3,000 vs about 30).
188
189 ## Notes: what looks wrong (≤5 lines)
190 1. **180+ exposure is implausible on cards:** AED 109 bn on 293k not_reachable accounts (about AED 370k each)
191    versus AED 544 m on 19k cards at 61-180. Do not quote 180+ card AED from `crx_cc_balance.stmt_balance`
192    until checked. Loans (AED 4.6 bn, about 90k each) look plausible.
193 2. **180+ axes are mostly empty:** deterioration family Unknown 78% (cards) / 59% (loans), locatability
194    Unknown × Unknown 78.5% / 77.7%, credibility Unknown 81% / 64%, ability Unknown 87% / 90%. So 92% / 91%
195    of 180+ land in `not_reachable` and the cure/stopped/credible segments hold under 1%.
196 3. **61-180 ability is thin:** 56.6% Unknown on cards, 46% on loans; High is 0.2-0.3%, so High rarely
197    contributes.
198 4. **Loan paid % looks inflated against cards** (not_reachable loans 41% vs cards 13%; can_cure 56% vs 33%).
199    Loan cash is read by month (`int_loan_master.total_paid` ≥ AED 100, dated month end) while card payments
200    are by day from transactions; the two "paid" measures may not be like for like (cause not checked).
201 5. **Deceased accounts are counted** (cards 0.5%, loans 0.7%) in the mixes and segments; no 180+
202    positive-signal paid % or AED exists in the output, only the share.
203
204 ## Changes made to the snippet
205 See `persona_deck_numbers.py` (committed 5fc0e8f3):
206 - payments rebuilt from `crx_cc_transactions` / `int_loan_master` (`crx_<p>_a3_payments` is not a catalog
207   dataset);
208 - loans read `crx_rl_dpd_sequences_linked`;
209 - NULL bucket → `no_bucket` / `no_history`; missing A2 row → not reachable; `element_at` guarded for idx ≥ 1;
210 - back-test outcomes blanked where the back-test cell has fewer than 10 accounts (`bt_accounts`);
211 - output folder from `__file__`.
212
````

## Notes on specific spots
- Sum checks that pass: A2 cards matrix 44.0 + 24.0 + 32.0 = 100.0 (lines 38-40); loans 43.4 + 27.1 + 29.6 = 100.1 (rounding). A3 cards 2.5 + 19.4 + 66.5 + 11.5 = 99.9, loans 4.9 + 27.9 + 60.6 + 6.6 = 100.0. A4 rows 100.1 / 100.0 / 100.0 / 99.9 (rounding). A1 cards 31.8 + 60.4 + 7.5 + 0.3 = 100.0; loans 42.8 + 51.4 + 5.7 = 99.9. Tree leaves (lines 81-90): stopped 50.8 + 6.1 + 3.5 = 60.4 (= line 20), can_cure 21.2 + 3.1 + 7.5 = 31.8 (= line 20), never_paid 6.8 + 0.5 + 0.1 = 7.4 (line 20 says 7.5, rounding).
- Action tables: card shares 7.5 + 72.2 + 6.3 + 1.5 + 1.1 + 11.3 = 99.9; card AED 60.1 + 372.8 + 35.9 + 7.3 + 5.6 + 62.3 = 544.0 (= "AED 544 m" in note 1, line 191); loan shares sum to 100.0; loan AED 38.1 + 294.6 + 38.4 + 3.9 + 1.3 + 73.2 = 449.5 (no stated total). Segment shares equal the family shares for never_paid (7.5 cards / 5.7 loans, lines 20-22).
- 180+ split (lines 119-120): cards 92.1 + 4.4 + 2.6 + 0.9 = 100.0, loans 91.1 + 4.2 + 3.2 + 1.5 = 100.0.
- Pilot (lines 163-187): arm n check on the first card row: 4.6% base, +5 pts, alpha 0.05, 80% power gives about 410 (printed 411); "2 × arm n" values in lines 181-187 match the arm n column (822, 1,604, 2,900, 2,744, 2,650, 3,058; loans 3,080, 2,450, 2,106, 3,132). Loans stopped_reach_means 2 × 1,498 = 2,996 ("about 3,000", as printed) and reach_notcred_means 2 × 1,276 = 2,552 (also grouped under "about 3,000 vs about 30", as printed). Aug loan volumes sum to 3,985 (= 2,060 / 51.7% on line 153); Aug card volumes sum to 19,292 (about the "19k cards" in line 191).
- Verdict rule (lines 123-124) holds for every printed row (e.g. line 144: no spread, AUC 0.643 < 0.65 gives "maybe"; line 145: AUC 0.733 gives "yes by rule").
- Line 53: roll 42.4% vs 89.9% with "paid 75.0% vs 14.7%" as printed (High n=144, Low n=2,419).
- Line 63: 1,979 / 55,371 = 3.57%, printed 3.6%. Line 17 lists loans ability High or Moderate 6.2% / 3.6% (cards / loans); line 60-61 give 6.2 (0.0 + 6.2) for cards and 3.5 for loans (0.0 + 3.5, line 17 says 3.6; rounding).
- Line 12-13: "4.1% - 62.6%" range as printed; the tree shows 58.0 for the best can_cure leaf at the latest month, the 62.6% is for the 91-120 band (a different cut), so the numbers are not expected to match.
- Lines 148-149, 193-195: "Unknown × Unknown" (line 194) is printed with a multiplication-like sign between the two words; I read it as ×.
- Arrows in lines 209 are real `→` characters in the photo.
- Photo caveats: photo 2 shows the editor scrolled so that line 92 is sticky at the top and line 110 is partly cut, then 111-166; line 113 is read from photo 3 (partly cut) and photo 2 (`stopped_reach_means | 0.9 | 3.9 | 57.9`). Line 144 and 145 text in the verdict column is as printed ("maybe (n=38)", "yes by rule; n=29, unreliable").
- Status bar and status elements: file untracked (`U`), 0 errors 0 warnings, branch tag cut off at the left (`...actor*`, i.e. `feature/persona_refactor*`).
- OCR-risk digits: nearly all tables are digits; especially lines 9-17 (53.2%, 60.5m, 57.2%, 55.1m, 4.1% - 62.6%, 5.9% / 8.2%, 1.4% / 2.4%), 33 / 35 (11,716, 10,099, 2,377, 2,653, 1,966, 704), line 53 (144, 2,419), line 63 (1,979, 55,371), lines 67-69 (432 / 297 / 57 / 242; 432 / 199 / 55 / 136), line 117 (38,763, 6,780), lines 130-146 (n and AUC columns), lines 163-179 (monthly counts), lines 181-187, line 190 (109 bn, 293k, 370k), line 192 (4.6 bn), 5fc0e8f3 on line 205.
