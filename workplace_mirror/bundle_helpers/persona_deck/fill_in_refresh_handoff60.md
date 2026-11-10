# Handoff 60: `tmp_validation/persona_deck/fill_in.md` "refresh run, 2026-11-10", lines 1-329 (exposure source, A1-A4, combinations, tiers, tree, risk score, UC1, pilot, 180+, regression, outcome check, notes, next steps) (11 photos), 2026-11-11

## Context for Claude Code
- Source: 11 phone photos of the VS Code editor (Dev Container `cdp-devcontainer:latest @ 10.119.132.99`, workspace `retail.collections.risk_profiling`). Tabs: `pipeline_registry.py`, `fill_in.md` (active; saved, no `U` mark this time). Breadcrumb `tmp_validation > persona_deck > fill_in.md > # Persona deck - fill-in sheet (refresh run, 2026-11-10) > ## Next steps`. A git-blame line "You, 3 seconds ago | 1 author (You)" shows above line 1 in photo 1. Status bar: Ln 329, Col 1, Spaces: 2, UTF-8, LF.
- This is the **refreshed version** of the file in handoff 59 (that one was the 212-line first version, titled "fill-in sheet"). New in this run: meaningful-payment target (`paid`) next to `paid_any`, exposure source (BNP principal for cards, ENR for loans), curing_now / cure_history split of A1 can_cure, det_state outcomes, A3 with no Unknown row (D-A3-27), tiers (in_house / agency / early_exit / unassigned) with capture curve, tree with tiers, score-by-tier, AUC comparison, tier pilot, 180+ vintage split and positive-signal outcomes, regression against the previous run, outcome check, notes, next steps. Segments: `cc_60_180`, `rl_60_180`, `cc_180_plus`, `rl_180_plus`. Follows handoffs 1-59.
- Transcribed by Claude (chat) from the images, not copied from the file. Verify numbers against the real file.
- Photo-to-line map (in the order sent): photo 1 = lines 1-35; photo 2 = lines 1, 91, 95-128; photo 3 = lines 1, 107, 124-157; photo 4 = lines 1, 107, 155-188; photo 5 = lines 1, 34, 35-67; photo 6 = lines 1, 34, 65-98; photo 7 = lines 1, 175, 184-217; photo 8 = lines 1, 208, 214-247; photo 9 = lines 1, 241, 243-276; photo 10 = lines 1, 241, 272-305; photo 11 = lines 1, 289, 301-329. The overlaps are merged; every line 1-329 is covered. Lines headed 1 and the `##` line right under it in each photo are the editor's sticky-scroll headers, not extra lines. Line 329 is the last line (empty, cursor on it).
- Source lines are hard-numbered in the editor and the editor numbers every wrapped line here, so each line below is one source line.
- The Mac link is down for this batch (the computer is not reachable from the cloud workspace), so I could not write the file into `~/Python/Collections/pics/`. Written in the cloud workspace and sent as a file; copy it to `~/Python/Collections/pics/claude_code_handoff_60.md`.

---

## `fill_in.md` (lines 1-329)

````
1   # Persona deck - fill-in sheet (refresh run, 2026-11-10)
2
3   Format: `section · item · value · source table`. Source: `deck_<model_id>.json/.md` (commit
4     `d98510ba`, script `d20ef626`).
5   Latest month = Aug 2026; 61-180 back-test = May 2026 states vs Jun-Aug outcomes (3 months). Units
6     are **accounts**.
7   `paid` = **meaningful payment** (the risk score's target; 61-180: in ≥1 of the 3 months the customer
8     paid ≥ the
9   stabilising amount [cards: oldest overdue bucket; loans: one EMI]); `paid_any` = old "any payment
10    AED 100+".
11  Labels: A1 Deterioration, A2 Locatability, A3 Payment credibility, A4 Ability. Cells under 10
12    accounts are marked.
13
14  ## Exposure source
15  - Exposure · cards · `prm_balance.bnp_principal` = **billed-not-paid (BNP) principal** (excludes
16    unbilled; NOT total outstanding principal — no true outstanding-principal column exists for cards;
17    use agreed 2026-11-10) · `exposure_source` cc
18  - Exposure · loans · `int_loan_master.outstanding_balance` (`ra_enr_amt`, expected net receivable;
19    not confirmed principal-only) · `exposure_source` rl
20  - Exposure · card AED and loan AED are on different bases: do not compare per-account amounts across
21    products.
22  - Exposure · back-test rows with no exposure · cards 388 (61-180), 1,103 (180+); loans 10 (61-180),
23    167 (180+) · `bt_no_exposure`
24
25  ## Summary
26  - Summary · % of reachable (61-180) who are credible or able · cards 53.2% (AED 39.7m BNP
27    principal); loans 57.2% (AED 55.1m) · `summary`
28  - Summary · reachable share of all accounts · cards 21.0% (4,043 / 19,292); loans 26.2% (1,043 /
29    3,985) · `summary`
30  - Summary · % of 180+ accounts with a positive signal · cards 12.2% (38,763 / 318,663); loans 12.2%
31    (6,780 / 55,371) (same % by coincidence, counts differ) · `positive_signal`
32  - Summary · paid % range across leaves at 91-120 · cards 4.1-73.2%; loans 9.1-76.4% · `summary`
33
34  ## A1 Deterioration
35  - A1 · family shares, cards 61-180 · stopped_suddenly 60.4 / cure_history 25.2 / never_paid 7.5 /
36    curing_now 6.6 / unknown 0.3 (60 accounts) · `mix_a1_family`
37  - A1 · family shares, loans 61-180 · stopped_suddenly 51.4 / cure_history 32.5 / curing_now 10.3 /
38    never_paid 5.7 · `mix_a1_family`
39  - A1 · paid in 3 months by family, overall, cards · curing_now 60.3 / cure_history 21.9 /
40    stopped_suddenly 11.4 / never_paid 4.3 / unknown 24.2 (91 accounts) · `a1_family_outcome`
41  - A1 · paid in 3 months by family, overall, loans · curing_now 74.1 / cure_history 38.1 /
42    stopped_suddenly 28.6 / never_paid 21.5 · `a1_family_outcome`
43  - A1 · paid by family per DPD band (61-90 / 91-120 / 121-150 / 151-180), cards · curing_now 59.3 /
44    64.3 / 65.8 / 42.7 (131 accounts in last band); cure_history 33.3 / 22.0 / 17.1 / 5.6;
45    stopped_suddenly 18.8 / 11.3 / 8.2 / 3.2; never_paid 8.5 / 5.2 / 1.4 / 0.6 · `a1_family_x_band`
46  - A1 · same, loans · curing_now 77.8 / 73.1 / 68.9 / 53.8 (162 / 108 / 45 / 13 accounts);
47    cure_history 47.6 / 44.2 / 26.0 / 20.3; stopped_suddenly 36.4 / 27.7 / 16.1 / 13.7; never_paid
48    40.0 / 15.6 / 5.9 / 3.1 (75 / 45 / 34 / 32 accounts) · `a1_family_x_band`
49  - A1 · paid by det_state, overall, cards · stabilized 60.3 / slow_roller 22.1 / repeat_delinquent
50    21.4 / straight_roller_seasoned 11.4 / straight_roller_early_life 11.3 / early_payment_default 4.3
51    / unknown 24.2 · `a1_state_outcome`
52  - A1 · paid by det_state, overall, loans · stabilized 74.1 / repeat_delinquent 41.2 / slow_roller
53    36.6 / straight_roller_seasoned 31.2 / straight_roller_early_life 23.8 / early_payment_default
54    21.5 · `a1_state_outcome`
55  - A1 · paid by det_state per band (61-90 / 91-120 / 121-150 / 151-180), cards · stabilized 59.3 /
56    64.3 / 65.8 / 42.7; slow_roller 35.0 / 21.5 / 18.2 / 6.2; repeat_delinquent 30.5 / 23.3 / 14.2 /
57    4.3; seasoned 18.9 / 11.5 / 7.5 / 3.2; early_life 18.6 / 10.8 / 10.0 / 3.3; early_payment_default
58    8.5 / 5.2 / 1.4 / 0.6 · `a1_state_x_band`
59  - A1 · same, loans · stabilized 77.8 / 73.1 / 68.9 / 53.8; slow_roller 48.1 / 43.7 / 23.0 / 20.2;
60    repeat_delinquent 46.7 / 45.0 / 34.8 / 20.5; seasoned 39.8 / 28.3 / 16.5 / 20.3; early_life 30.0 /
61    26.5 / 15.5 / 4.0; early_payment_default 40.0 / 15.6 / 5.9 / 3.1 · `a1_state_x_band`
62  - A1 · **verdict** curing_now ≥ 5 pts above cure_history · cards **yes, 4 of 4 bands** (+26.0 /
63    +42.3 / +48.7 / +37.1); loans **yes, 4 of 4** (+30.2 / +28.9 / +42.9 / +33.5; last-band curing_now
64    cell has 13 accounts) · `a1_family_x_band`
65
66  ## A2 Locatability
67  - A2 · 61-180 matrix, % of accounts (location / reachability), cards | loans · `mix_a2_matrix`
68
69  | location \ reach | reachable | non_reachable | unknown |
70  |---|---|---|---|
71  | in_country | 8.5 \| 10.2 | 13.6 \| 14.2 | 1.9 \| 2.7 |
72  | skip | 6.2 \| 8.1 | 31.7 \| 28.5 | 6.1 \| 6.8 |
73  | unknown | 6.3 \| 7.9 | 22.3 \| 14.9 | 3.4 \| 6.8 |
74
75  - A2 · 180+ reachable / in country / both · cards 3.7% (11,716) / 3.2% (10,099) / 0.7% (2,377);
76    loans 4.8% (2,653) / 3.6% (1,966) / 1.3% (704) · `a2_positive`
77  - A2 · 61-180 reachable / in country / both · cards 21.0 / 24.0 / 8.5; loans 26.2 / 27.1 / 10.2 ·
78    `a2_positive`
79  - A2 · 180+ matrix · unknown/unknown cards 78.5%, loans 77.7% (by design for gt2y) · `mix_a2_matrix`
80
81  ## A3 Payment credibility
82  - A3 · High / Moderate / Low, 61-180 · cards 2.5 / 19.4 / 78.0; loans 4.9 / 27.9 / 67.2. **No
83    Unknown row** in any model (D-A3-27: `no_evidence` now counts as Low) · `mix_a3_band`
84  - A3 · High / Moderate / Low, 180+ · cards 0.1 / 2.7 / 97.2; loans 0.3 / 4.3 / 95.4 · `mix_a3_band`
85  - A3 · `no_evidence` share (now inside Low), 61-180 · cards 11.5% (2,228); loans 6.6% (263); 180+
86    cards 81.4%, loans 63.5% · `mix_a3_unknown_reason`
87  - A3 · rolled % at 91-120, High vs Low · cards 42.4% (144 accounts) vs 90.4% (2,821); loans 65.5%
88    (59) vs 85.8% (639) · `a3_band_x_band`
89  - A3 · untested share · cards 59.0% at 61-180, 95.3% at 180+; loans 67.1% / 96.1% · `a3_untested`
90
91  ## A4 Ability
92  - A4 · High / Moderate / Low / Unknown · cc_60_180 0.2 / 14.4 / 28.9 / 56.6; rl_60_180 0.3 / 8.9 /
93    44.7 / 46.1; cc_180_plus 0.0 / 6.2 / 6.4 / 87.4; rl_180_plus 0.0 / 3.5 / 6.9 / 89.5 ·
94    `mix_a4_band`
95
96  ## Combinations (61-180, 576 possible = 4 families × 3 × 3 × 4 × 4)
97
98  | item | cards | loans |
99  |---|---|---|
100 | non-empty | 298 | 221 |
101 | non-empty, known family | 272 | 221 |
102 | empty (= 576 - non-empty known) | 304 | 355 |
103 | covering 80% of accounts | 54 | 64 |
104 | under 0.5% of accounts | 251 | 163 |
105 | with ≥10 back-test accounts (rankable) | 159 | 77 |
106
107 ## Tiers (61-180; cuts used: cards (30, 5), loans (60, 25) paid % — in-sample)
108 Share / principal = Aug population; paid, rolled, cured, collected = May back-test; call-attempt
109   days = distinct outbound call days over the last 3 months (A2). Cards principal = BNP.
110
111 | tier | share % | principal AED m | paid % | paid-any % | rolled % | cured % | collected AED m | %
112   of payers | % of money | call days |
113 |---|---|---|---|---|---|---|---|---|---|
114 | **Cards** in_house | 13.7 | 50.4 | 48.8 | 50.2 | 53.6 | 13.8 | 4.69 | 49.3 | 46.2 | 12.4 |
115 | agency | 60.1 | 238.2 | 13.1 | 14.1 | 89.0 | 5.0 | 4.58 | 42.0 | 45.1 | 11.7 |
116 | early_exit | 23.4 | 102.4 | 2.7 | 2.9 | 97.1 | 1.9 | 0.30 | 2.7 | 2.9 | 10.6 |
117 | unassigned | 2.7 | 9.7 | 37.6 | 37.8 | 64.8 | 13.9 | 0.58 | 5.9 | 5.7 | 10.0 |
118 | **Loans** in_house | 8.9 | 29.1 | 73.1 | 79.5 | 54.7 | 8.2 | 2.51 | 22.3 | 22.3 | 8.5 |
119 | agency | 32.8 | 144.9 | 38.6 | 47.9 | 76.1 | 9.8 | 4.39 | 39.0 | 38.9 | 9.6 |
120 | early_exit | 39.9 | 203.0 | 14.9 | 24.5 | 93.3 | 2.6 | 1.92 | 14.1 | 17.0 | 9.9 |
121 | unassigned | 18.4 | 72.5 | 52.7 | 61.4 | 68.9 | 7.4 | 2.45 | 24.5 | 21.7 | 8.2 |
122
123 Who is in each tier (largest family × nuance groups, % of the tier):
124 - Cards in_house: curing_now with a credible-or-able customer (~29%), cure_history credible-or-able
125   (~18%), stopped_suddenly neither able nor reachable (~16%).
126 - Cards agency: stopped_suddenly, not reachable (~53%); cure_history, not reachable (~31%);
127   stopped_suddenly, neither (~7%).
128 - Cards early_exit: stopped_suddenly, not reachable (~77%); never_paid, not reachable (~23%);
129   nothing else.
130 - Loans in_house: curing_now credible-or-able (3.3% of all accounts, the largest), stopped_suddenly
131   not reachable (1.6%), cure_history not reachable (1.5%).
132 - Loans agency: stopped_suddenly not reachable (10.2% of all), cure_history not reachable (9.7%),
133   stopped_suddenly neither (4.6%).
134 - Loans early_exit: stopped_suddenly not reachable (~63%), cure_history not reachable (~23%),
135   never_paid not reachable (~9%).
136 - Call attempts are highest where payment is already likely (cards in_house 12.4 days) but cards
137   early_exit still gets 10.6 days for a 14.2% right-party contact rate.
138
139 Capture curve (combinations ranked by paid %, ranked accounts only = combos with ≥10 back-test
140   accounts: 97% of card, ~83% of loan accounts; linear interpolation) · `combos_ranked`
141
142 | top % of accounts | cards: payers | cards: money | loans: payers | loans: money |
143 |---|---|---|---|---|
144 | 10% | 34.4 | 29.5 | 22.8 | 22.6 |
145 | 20% | 53.6 | 50.4 | 39.8 | 38.1 |
146 | 30% | 67.1 | 63.7 | 53.7 | 50.0 |
147 | 50% | 84.5 | 84.7 | 75.0 | 70.6 |
148 | 80% | 96.9 | 96.8 | 94.1 | 92.2 |
149
150 - **Headline:** the top 20% of card accounts hold about 54% of payers and 50% of the money collected
151   (loans: about 40% of payers).
152 - Cut-offs used: cards (30, 5), loans (60, 25). **Proposed (not applied, see Next steps):** cards
153   (30, 8), loans (40, 15). Evaluated offline on ranked accounts: cards in_house 19.3% unchanged,
154   agency 61.2% → 40.6% (-20.6 pts), early_exit 19.5% → 40.1% (+20.6; holds 9.8% of payers, 10.3% of
155   money; the 5% cut keeps 97% of payers in agency and the curve flattens near 8%). Loans in_house
156   13.5% → 35.0% (+21.5; 59.8% of payers), agency 44.6% → 44.1%, early_exit 41.9% → 20.9% (-21.0;
157   6.3% of payers). Both move tiers by more than 5 pts.
158 - Loan money caveat: loan amounts come from `int_loan_master.total_paid`, a monthly field that looks
159   inflated against cards; treat loan money shares as indicative.
160
161 ## Tree (cards, family × nuance leaf: share % / paid % / tier at the leaf level) · `tree`
162 - stopped_suddenly · not_reachable 50.8 / 7.8 / agency; neither 6.1 / 21.7 / agency;
163   credible_or_able 3.5 / 33.5 / in_house
164 - cure_history · not_reachable 19.0 / 16.3 / agency; credible_or_able 3.4 / 40.3 / in_house; neither
165   2.7 / 29.9 / agency
166 - never_paid · not_reachable 6.8 / 2.9 / early_exit; neither 0.5 / 10.9 / agency; credible_or_able
167   0.1 / 32.3 / in_house
168 - curing_now · credible_or_able 4.1 / 68.2 / in_house; not_reachable 2.1 / 43.6 / in_house; neither
169   0.4 / 51.5 / in_house
170 - unknown · not_reachable 0.3 / 13.4 / agency; neither and credible_or_able under 10 accounts
171   (suppressed)
172 - The largest leaf (stopped_suddenly, not reachable; half of all cards) pays 7.8%: leaf-level tier
173   is agency, but at combination level its payers sit in both agency and early_exit.
174
175 ## Risk score (61-180; verdict: yes if spread ≥15 pts or AUC ≥0.65; no if spread <5 and AUC <0.58;
176   else maybe) · `score_tier`
177
178 | tier | accounts (back-test) | paid % | paid spread / AUC (band-only) | rolled spread / AUC |
179   verdict (paid · rolled) |
180 |---|---|---|---|---|---|
181 | Cards in_house | 2,977 | 48.8 | 17.9 / 0.545 | 18.9 / 0.578 | yes · yes |
182 | Cards agency | 9,438 | 13.1 | 17.1 / 0.655 | 11.0 / 0.627 | yes · maybe |
183 | Cards early_exit | 3,009 | 2.7 | 6.9 / 0.756 | 2.6 / 0.603 | yes (AUC only) · maybe |
184 | Cards unassigned | 466 | 37.6 | 21.9 / 0.555 | 22.3 / 0.587 | yes · yes |
185 | Loans in_house | 346 | 73.1 | 44.2 / 0.597 | 30.9 / 0.574 | yes · yes |
186 | Loans agency | 1,145 | 38.6 | 24.8 / 0.602 | 22.8 / 0.618 | yes · yes |
187 | Loans early_exit | 1,077 | 14.9 | 17.4 / 0.641 | 7.1 / 0.621 | yes · maybe |
188 | Loans unassigned | 528 | 52.7 | 34.3 / 0.593 | 27.0 / 0.589 | yes · yes |
189
190 - Verdict **yes in every tier** (none "no"): the rule is lenient, read as "a score is not ruled
191   out", not as proof. Cards early_exit's yes rests on AUC 0.756 over ~80 payers (fragile); loans
192   in_house (346) and cards unassigned (466) are small cells.
193
194 AUC comparison, in-sample back-test month (tiers cut from the same paid %, finer partitions inflate
195   AUC) · `score_compare_auc`
196
197 | ranking | cards paid | cards rolled | loans paid | loans rolled |
198 |---|---|---|---|---|
199 | DPD band alone | 0.650 | 0.647 | 0.611 | 0.609 |
200 | tree leaf | 0.770 | 0.787 | 0.669 | 0.641 |
201 | tier | 0.747 | 0.752 | 0.721 | 0.700 |
202 | band + leaf | 0.809 | 0.811 | 0.726 | 0.697 |
203 | band + tier | 0.794 | 0.790 | 0.754 | 0.736 |
204
205 - Personas add about +0.10 to +0.14 AUC over DPD band on cards, +0.03 to +0.06 (leaf) and +0.09 to
206   +0.11 (tier) on loans; adding band to personas adds a little more. Not out-of-sample.
207
208 ## UC1 · right-party contact in the last 3 months · `uc1_contact`, `uc1_by_tier`
209 - UC1 · overall · cards 41.0% (7,910); loans 51.7% (2,060)
210 - UC1 · by tier · cards in_house 94.1% / agency 38.3% / early_exit 14.2% / unassigned 62.4%; loans
211   in_house 75.1% / agency 59.3% / early_exit 35.0% / unassigned 63.1%
212 - UC1 · reading: contact tracks tier because A3 credibility and the tier both use contact history;
213   the early-exit tier is where call-transcript features have least contact to work with (cards
214   14.2%).
215
216 ## Pilot · `tier_volume`, sample size: two-sided α 0.05, 80% power, baseline = tier back-test paid %
217 - Accounts per tier Jun / Jul / Aug · cards agency 10,400 / 11,247 / 11,596; early_exit 3,177 /
218   3,882 / 4,518; in_house 2,882 / 2,736 / 2,652; unassigned 523 / 532 / 526 · loans agency 1,341 /
219   1,330 / 1,309; early_exit 1,245 / 1,432 / 1,590; in_house 370 / 302 / 354; unassigned 558 / 664 /
220   732
221
222 | tier | baseline paid % | n per arm at +5 pts | n per arm at +10 pts |
223 |---|---|---|---|
224 | Cards agency | 13.1 | 826 | 232 |
225 | Cards early_exit | 2.7 | 309 | 111 |
226 | Cards in_house | 48.8 | 1,568 | 389 |
227 | Cards unassigned | 37.6 | 1,508 | 383 |
228 | Loans early_exit | 14.9 | 902 | 250 |
229 | Loans agency | 38.6 | 1,519 | 385 |
230 | Loans unassigned | 52.7 | 1,552 | 382 |
231 | Loans in_house | 73.1 | 1,158 | 268 |
232
233 - Fill both arms in one month: cards +5: agency, early_exit; cards +10: agency, early_exit, in_house
234   (778 of 2,652). Loans +5: none; loans +10: early_exit (500 of 1,590; 1,245 in Jun) and agency (770
235   of 1,309); in_house (536 vs 354) and unassigned (764 vs 732; 558 in Jun) do not.
236 - 10% hold-out of early-exit candidates per month · cards 318 (Jun) / 388 (Jul) / 452 (Aug) — above
237   the 111 per arm needed at +10 pts; loans 125 / 143 / 159 — below the 250 needed at +10 pts.
238 - Tier membership drifts month to month (cards in_house falls 2,882 → 2,652 while early_exit rises
239   3,177 → 4,518), so baselines from the May cohort are approximate for a pilot cohort.
240
241 ## 180+ (cards `cc_180_plus`, loans `rl_180_plus`)
242 - Windows: early-stage (<24 months in 180+) base Feb 2026, 6 months; late-stage base Jan 2026, **7
243   months, not the 12 intended** (persona data starts Jan 2026) · `backtest`
244 - Positive signal · any 12.2% / 12.2%; payment 5.9 / 8.2; promise 1.4 / 2.4; reachable 3.7 / 4.8;
245   ability 6.2 / 3.6 (cards / loans) · `positive_signal`
246 - Vintage split · cards early 19.2% (61,112) / late 80.8% (257,551); loans early 17.5% (9,679) /
247   late 82.5% (45,692); no unknown bucket · `vintage_split`
248 - Meaningful payment with signal vs without (5% of principal / AED 1,000 / AED 2,000 / any 100+),
249   overall positive signal · `positive_signal_outcome`
250
251 | | vintage | without signal | with signal | lift (5% / 1,000 / 2,000) |
252 |---|---|---|---|---|
253 | Cards | early | 2.7 / 2.6 / 2.0 / 3.6 | 20.7 / 20.0 / 15.3 / 25.8 | +18.0 / +17.4 / +13.3 |
254 | Cards | late | 0.6 / 0.6 / 0.5 / 0.7 | 18.6 / 17.9 / 13.8 / 23.1 | +18.0 / +17.3 / +13.3 |
255 | Loans | early | 3.3 / 4.6 / 3.9 / 5.5 | 20.1 / 24.7 / 22.4 / 27.3 | +16.8 / +20.1 / +18.5 |
256 | Loans | late | 0.6 / 0.7 / 0.6 / 0.7 | 27.2 / 30.2 / 28.8 / 31.4 | +26.6 / +29.5 / +28.2 |
257
258 - By signal (5% variant, with vs without, early | late): cards payment 28.1 vs 4.0 | 43.9 vs 0.9;
259   promise 32.0 vs 7.6 | 53.8 vs 1.6; reachable 29.1 vs 6.0 | 24.3 vs 1.2; ability 19.7 vs 6.9 | 13.9
260   vs 1.3. Loans payment 23.7 vs 4.5 | 51.5 vs 0.8; promise 33.9 vs 7.9 | 65.5 vs 1.6; reachable 26.4
261   vs 6.9 | 29.8 vs 1.3; ability 26.7 vs 8.5 | 24.3 vs 1.6. Promise (894 cards / 313 loans with
262   signal, late) and payment have the biggest lift; ability the smallest. Late-stage without a signal
263   is essentially dead (<2% on every variant).
264 - Score by vintage (`score_vintage`, vintage-only): cards no-signal 264,691 accts, paid 0.9%, spread
265   2.1, AUC 0.661 → yes (AUC rule only, base-rate gap early 2.7% vs late 0.6%); cards with signal
266   38,664, 19.8%, spread 2.1, AUC 0.516 → no; loans no-signal 46,461, 0.9%, spread 2.7, AUC 0.658 →
267   yes (AUC only); loans with signal 6,145, 22.9%, spread 7.1, AUC 0.547 → maybe. Vintage ranks the
268   no-signal group only through the base-rate gap, not a real score effect.
269 - **Recommended threshold: 5% of outstanding principal** as the headline, with AED 1,000 reported
270   beside it: lifts are nearly identical across variants, so the choice moves the base rate, not the
271   separation. On cards 5% ≈ AED 1,000 (late-stage mean ~AED 19k BNP principal). On loans mean ENR
272   ~AED 89k makes 5% ≈ AED 4.4k, stricter than the AED 2,000 variant, which counts small payments
273   against large balances.
274
275 ## Regression (61-180, `action` vs previous run `d20ef626`)
276 - `never_paid`, `not_reachable`, `cure_reach_cred`, `stopped_reach_means`: **account counts and
277   shares identical to the decimal** in all four models; `paid_any_pct` equals the old `paid_pct` for
278   them. Cards 61-180 paid-any: cure_reach_cred 61.1, never_paid 4.6, not_reachable 12.6,
279   stopped_reach_means 27.9; loans 76.1 / 24.2 / 41.0 / 57.9.
280 - Moved (allowed): `other` cards 2,176 → 2,175, loans 537 → 536; `reach_notcred_means` cards 217 →
281   218 (paid-any 39.8 → 40.1, rolled 61.0 → 61.1), loans 23 → 24 (paid-any unchanged 69.0).
282   Consistent with D-A3-27 moving accounts to Low (not separately verified).
283 - 180+: the four fixed segments keep their shares (cards cure_reach_cred 0.3, never_paid 4.4,
284   not_reachable 92.1, stopped 0.3); `other` 2.6 → 2.5, `reach_notcred_means` 0.3 → 0.4 (cards, 920 →
285   1,301 accounts). Their `paid_any` / rolled differ from the old run because the window is now 6-7
286   months, not 3 — not comparable.
287 - No other differences.
288
289 ## Outcome check (meaningful payment vs any payment)
290 - Overall back-test, 61-180 · cards paid 18.6% vs paid-any 19.4%; loans 36.6% vs 45.6%
291 - By tier · cards in_house 48.8 vs 50.2; agency 13.1 vs 14.1; early_exit 2.7 vs 2.9; unassigned 37.6
292   vs 37.8 · loans in_house 73.1 vs 79.5; agency 38.6 vs 47.9; early_exit 14.9 vs 24.5; unassigned
293   52.7 vs 61.4 · `tier_summary`
294 - Overall 180+ (5% / 1,000 / 2,000 / any) · cards 3.3 / 3.2 / 2.5 / 4.1; loans 3.4 / 4.1 / 3.8 / 4.5
295 - Reading: the new target barely changes cards (any-payment overstates by ~1 pt) but removes about 9
296   pts of loan "paid" (payments below one EMI), most in loan early_exit (24.5 → 14.9).
297 - Consistency: axis shares sum to 99.9-100.1 (rounding); tier shares sum to 99.9-100.0; tree family
298   totals match the family shares within 0.1 (cards tree total 99.8 because two unknown-family leaves
299   are suppressed); cards curing_now 6.6 + cure_history 25.2 = 31.8 and loans 10.3 + 32.5 = 42.8,
300   equal to the old "can cure" shares.
301
302 ## Notes
303 - Cards exposure is BNP principal, loans is ENR, so AED figures and "AED per account" are not
304   comparable across products; 388 card back-test rows have no exposure.
305 - Late-stage 180+ uses a 7-month window instead of 12; early and late are not like-for-like and
306   late-stage rates are understated.
307 - At 180+ the tiers (cuts built for 61-180) put about 84% of card and 95% of loan accounts in
308   early_exit (Aug: cards 268,023 of 318,663; loans 52,881 of 55,371): not meaningful, do not use
309   180+ tiers.
310 - Loan "unassigned" (18.4% of accounts, 52.7% paid) is combinations under 10 back-test accounts, not
311   a weak tier; loan collected AED comes from `total_paid` and looks inflated.
312 - Tier tables, verdicts and AUCs are in-sample; the risk-score verdict rule passes every cell, so it
313   does not discriminate.
314
315 ## Next steps
316 1. **Recalibrate the tier cut-offs (optional second pass).** Proposed `TIER_CUTS = {"cc": (30.0,
317    8.0), "rl": (40.0, 15.0)}`: moves cards agency/early_exit by ±20.6 pts and loans
318    in_house/early_exit by +21.5 / -21.0 pts of ranked accounts. Kept at the current cuts for this
319    sheet (user decision); to apply, change the constant, rerun `cc_60_180` and `rl_60_180`, and redo
320    the tier, risk-score and pilot sections.
321 2. Hold the 180+ tier and the 12-month late-stage numbers until persona history reaches back to
322    2025-08 (widen `persona_start_date`, rerun the axes) or the user accepts the 7-month window.
323 3. Get the Way4 owners' answer on a true outstanding-principal field for cards, and on whether ENR
324    excludes interest and fees for loans.
325 4. Validate the tiers out-of-sample (fit on one month, score another) before they go to the GRR
326    workshop.
327 5. Pilot: cards agency and early_exit fill two arms at +5 pts in one month; loans need the +10 pt
328    effect or two months of data.
329
````

## Notes on specific spots
- Sum checks that pass: tier shares cards 13.7 + 60.1 + 23.4 + 2.7 = 99.9, loans 8.9 + 32.8 + 39.9 + 18.4 = 100.0; loan principal 29.1 + 144.9 + 203.0 + 72.5 = 449.5 (= the loan action AED total in handoff 59, lines 110-115); card principal 50.4 + 238.2 + 102.4 + 9.7 = 400.7. Collected AED: cards 4.69 + 4.58 + 0.30 + 0.58 = 10.15 and in_house is 46.2% of it (matches the "% of money" column); loans 2.51 + 4.39 + 1.92 + 2.45 = 11.27, in_house 22.3% (matches). % of payers cards 99.9, loans 99.9; % of money cards 99.9, loans 99.9.
- Tree shares (lines 162-170): stopped_suddenly 50.8 + 6.1 + 3.5 = 60.4 (= line 35), curing_now 4.1 + 2.1 + 0.4 = 6.6 (= line 35), cure_history 19.0 + 3.4 + 2.7 = 25.1 (line 35 says 25.2), never_paid 6.8 + 0.5 + 0.1 = 7.4 (line 35 says 7.5), unknown 0.3: total 99.8, as line 298 says. Line 299: 6.6 + 25.2 = 31.8 and 10.3 + 32.5 = 42.8 hold.
- A1 verdict (lines 62-63): curing_now minus cure_history per band, cards 59.3 - 33.3 = 26.0, 64.3 - 22.0 = 42.3, 65.8 - 17.1 = 48.7, 42.7 - 5.6 = 37.1; loans 77.8 - 47.6 = 30.2, 73.1 - 44.2 = 28.9, 68.9 - 26.0 = 42.9, 53.8 - 20.3 = 33.5. All hold. The curing_now rows in the per-band det_state lists (lines 55 and 59: `stabilized`) repeat the family numbers, as printed.
- Pilot counts: Aug cards 11,596 + 4,518 + 2,652 + 526 = 19,292 (= line 28); Aug loans 1,309 + 1,590 + 354 + 732 = 3,985 (= line 29). "2 × n per arm" at +10 pts in lines 233-235 matches the table (778, 500, 770, 536, 764). Hold-out numbers are 10% of early_exit: 3,177 / 3,882 / 4,518 gives 318 / 388 / 452.
- Vintage split (lines 246-247): 61,112 + 257,551 = 318,663 and 9,679 + 45,692 = 55,371 (= lines 30-31). Lift columns in lines 253-256 are the differences of the first three values of each group (e.g. 20.7 - 2.7 = 18.0); each "without / with" group has four values (5% / 1,000 / 2,000 / any 100+), the lift three, as printed. Lines 264-266: the no-signal and with-signal counts (264,691 + 38,664 = 303,355; 46,461 + 6,145 = 52,606) do not add up to 318,663 / 55,371; I copied them as shown (likely back-test populations, not checked).
- AUC comparison (lines 199-203): card gains over DPD band (0.650 / 0.647) for the tier are 0.097 / 0.105, for leaf 0.120 / 0.140, consistent with line 205 ("+0.10 to +0.14"); loan gains for leaf 0.058 / 0.032 and tier 0.110 / 0.091 match "+0.03 to +0.06" and "+0.09 to +0.11".
- Line 307-308: 268,023 / 318,663 = 84.1%, 52,881 / 55,371 = 95.5% (printed "about 84% / 95%").
- Line 4: `d98510ba` is the commit and `d20ef626` the script; line 275 calls `d20ef626` the "previous run". As printed (could be the same short hash used both ways, or a transcription slip of mine; check the file).
- Line 111-113: the tier table header wraps to a second source line (line 112) and the divider on line 113 is 10 or 11 columns; I could not count it reliably in the photo and typed 10 `---` groups (the table has 11 columns: tier + 10 values per row).
- Lines 124-135: percentages and "~" signs as printed (the in_house card shares ~29 / ~18 / ~16, agency ~53 / ~31 / ~7).
- Line 79 text "gt2y" is as printed. Line 12 "Cells under 10 accounts are marked."
- Arrows (→) are real characters in the editor (lines 154-156, 238-239, 280-285, 296).
- Compared with handoff 59 (older version of this file): A3 Low is now 78.0 (cards) / 67.2 (loans) = old Low + Unknown (66.5 + 11.5, 60.6 + 6.6); A1 `can_cure` 31.8 / 42.8 is now split into curing_now + cure_history; the `Summary` AED 60.5m for cards credible-or-able is now 39.7m BNP principal.
- OCR-risk digits: almost everything in tables; especially lines 28-31 (4,043, 19,292, 1,043, 3,985, 38,763, 318,663, 6,780, 55,371), 43-48 (band counts 131; 162 / 108 / 45 / 13; 75 / 45 / 34 / 32), 85-88 (2,228, 263, 144, 2,821, 59, 639), 100-105, 111-121 (all tier columns), 144-148 (capture curve), 181-188 (back-test counts and AUCs), 199-203, 217-231 (monthly counts, n per arm), 246-247, 253-256, 258-268, 284-285 (920, 1,301), 307-308 (268,023, 52,881).
