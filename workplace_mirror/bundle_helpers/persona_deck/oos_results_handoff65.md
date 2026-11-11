# Handoff 65: `oos_results.md` (persona out-of-sample test, cc_60_180 and rl_60_180), lines 1-303

## Context for Claude Code

- Source: 11 phone photos of VS Code (Dell laptop), file `tmp_validation/persona_deck/oos_results.md`, marked `M` (modified), "Not Committed Yet", Ln 22 Col 101. Other open tabs: `pipeline_registry.py`, `21_a1_evidence_family_rule.md`. Dev container `retail.collections.risk_profiling`.
- Content: results of the persona out-of-sample test on cards (`cc_60_180`) and loans (`rl_60_180`): verdict, AUC tables, capture tables, fallback-level shares, tier tables and stability, caveats.
- Photos merged by editor line number. Lines 1-303 are covered. Line 303 is the last line and is empty. Photo-to-line map: P1 = 1-35; P2 = 32-65; P3 = 63-94; P4 = 92-123; P5 = 121-153; P6 = 148-180; P7 = 173-205; P8 = 203-235; P9 = 229-261; P10 = 260-292; P11 = 278-303.
- Format: `NNN  text`, NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Continuation lines of a bullet are indented 2 spaces as in the editor. Table rows are copied cell by cell.
- Line 1 shows blame ghost text in the editor ("You, 8 minutes ago • Persona out-of-sample res…"). It is not file content.
- This file is delivered through the chat. If the Mac write did not happen for this batch, copy it to `~/Python/Collections/pics/`.

## Transcription

```
  1  # Persona out-of-sample test — results (cc_60_180, rl_60_180)
  2  
  3  Source: `oos_cc_60_180.json`, `oos_rl_60_180.json` (PROD run, personas Jan-May 2026 cohorts, 3-month
  4  outcomes). Views: A bucket · B persona · C 3 tiers · D persona x bucket · E tiers x bucket · F
  5  logistic (axes + bucket) · F_int (F + deterioration x locatability). Schemes: strict = 2 folds (Apr,
  6  May), adjacent = 4 folds (Feb-May), k-fold = 5 folds grouped by account. Fallback below 30 training
  7  accounts. Cells under 10 accounts suppressed.
  8  
  9  ## Verdict
 10  
 11  1. **Personas beat the bucket out-of-sample, in every fold:** AUC paid cards .81-.83 vs .65
 12     (+.16-.17), loans .73-.77 vs .62 (+.11-.14); the top 10 % holds ~31 % of cards money (bucket
 13     15 %, near random) and 17-20 % of loans money (bucket 12 %).
 14  2. **The bucket adds little within personas** (D vs B: cards +.010-.014 AUC paid, loans +.001-.002,
 15     no capture gain); within the 3 tiers it adds +.04 (E vs C) but E stays below B, so tiers lose
 16     ranking power the bucket only partly restores.
 17  3. **A simple logistic model beats the persona rate table modestly, every fold:** F vs B AUC paid
 18     cards +.016-.020, loans +.019-.031 (largest where loan personas fall back); the interaction
 19     version F_int = F, so a risk score has room of about +.02-.03 AUC.
 20  4. **Tiers are only partly stable:** order holds in 22/22 folds and cards cut-offs hold in 32/33
 21     checks (one tie at 175), but loans in_house >= 6,000 and early_exit < 1,350 each hold in only 6
 22     of 11 folds (regression to the middle); ~25 % of accounts change tier each month although 53-60 %
 23     change persona.
 24  
 25  ## Cards (cc_60_180)
 26  
 27  Cohorts (accounts in 61-180 DPD, 74,256 account-months, 29,629 distinct accounts):
 28  
 29  | cohort | accounts | paid % | rolled % | collected/acct | recovery % | personas | personas 30+ |
 30  |---|---|---|---|---|---|---|---|
 31  | 2026-01 | 14,664 | 21.4 | 80.4 | 683 | 3.5 | 306 | 103 |
 32  | 2026-02 | 14,576 | 19.7 | 82.2 | 610 | 3.11 | 296 | 98 |
 33  | 2026-03 | 14,455 | 18.8 | 83.3 | 588 | 2.91 | 301 | 99 |
 34  | 2026-04 | 14,671 | 19.1 | 83.7 | 630 | 3.04 | 300 | 99 |
 35  | 2026-05 | 15,890 | 18.6 | 83.2 | 639 | 3.05 | 309 | 101 |
 36  
 37  ### Table 1a — AUC, out-of-sample vs in-sample
 38  
 39  Mean [min-max] over folds. In-sample = the training data scored on itself. Views: A bucket, B
 40  persona, C 3 tiers, D persona x bucket, E tiers x bucket, F logistic, F_int logistic + family x
 41  locatability. Folds: strict 2, adjacent 4, k-fold 5.
 42  
 43  | scheme | view | AUC paid OOS | paid in-sample | AUC rolled OOS | rolled in-sample |
 44  |---|---|---|---|---|---|
 45  | strict | A | 0.651 [0.650-0.652] | 0.659 | 0.647 [0.647-0.647] | 0.654 |
 46  | strict | B | 0.806 [0.793-0.818] | 0.842 | 0.811 [0.805-0.817] | 0.847 |
 47  | strict | C | 0.751 [0.742-0.761] | 0.781 | 0.755 [0.752-0.758] | 0.774 |
 48  | strict | D | 0.816 [0.808-0.824] | 0.856 | 0.813 [0.810-0.815] | 0.856 |
 49  | strict | E | 0.792 [0.788-0.796] | 0.820 | 0.788 [0.786-0.790] | 0.807 |
 50  | strict | F | 0.826 [0.817-0.836] | 0.853 | 0.823 [0.817-0.829] | 0.850 |
 51  | strict | F_int | 0.826 [0.816-0.836] | 0.854 | 0.822 [0.817-0.827] | 0.852 |
 52  | adjacent | A | 0.654 [0.649-0.663] | 0.658 | 0.650 [0.647-0.655] | 0.654 |
 53  | adjacent | B | 0.821 [0.797-0.838] | 0.839 | 0.824 [0.809-0.834] | 0.843 |
 54  | adjacent | C | 0.765 [0.741-0.780] | 0.780 | 0.763 [0.754-0.781] | 0.773 |
 55  | adjacent | D | 0.833 [0.815-0.848] | 0.855 | 0.828 [0.819-0.839] | 0.854 |
 56  | adjacent | E | 0.806 [0.791-0.820] | 0.820 | 0.798 [0.788-0.814] | 0.807 |
 57  | adjacent | F | 0.839 [0.817-0.858] | 0.851 | 0.833 [0.819-0.845] | 0.848 |
 58  | adjacent | F_int | 0.838 [0.817-0.857] | 0.852 | 0.833 [0.820-0.845] | 0.849 |
 59  | k-fold | A | 0.654 [0.640-0.665] | 0.654 | 0.651 [0.637-0.660] | 0.651 |
 60  | k-fold | B | 0.825 [0.820-0.833] | 0.829 | 0.829 [0.821-0.843] | 0.833 |
 61  | k-fold | C | 0.764 [0.758-0.769] | 0.769 | 0.761 [0.755-0.764] | 0.765 |
 62  | k-fold | D | 0.839 [0.835-0.843] | 0.847 | 0.835 [0.830-0.845] | 0.846 |
 63  | k-fold | E | 0.806 [0.800-0.815] | 0.811 | 0.796 [0.793-0.799] | 0.801 |
 64  | k-fold | F | 0.841 [0.838-0.845] | 0.842 | 0.838 [0.833-0.846] | 0.838 |
 65  | k-fold | F_int | 0.841 [0.837-0.845] | 0.842 | 0.838 [0.833-0.847] | 0.839 |
 66  
 67  ### Table 1b — capture in the top 10 / 20 / 30 % of test accounts
 68  
 69  Mean % of AED collected (money) and of payers captured by the top 10 / 20 / 30 % of test accounts
 70  ranked by each view (random = 10 / 20 / 30).
 71  
 72  | scheme | view | money top 10 / 20 / 30 | payers top 10 / 20 / 30 |
 73  |---|---|---|---|
 74  | strict | A | 15.2 / 30.6 / 45.8 | 15.1 / 30.1 / 45.3 |
 75  | strict | B | 30.4 / 50.3 / 64.5 | 32.8 / 52.5 / 66.5 |
 76  | strict | C | 26.8 / 47.2 / 56.8 | 28.2 / 49.2 / 58.4 |
 77  | strict | D | 30.1 / 49.3 / 64.5 | 31.2 / 51.6 / 66.3 |
 78  | strict | E | 27.6 / 48.8 / 62.9 | 29.2 / 50.8 / 63.9 |
 79  | strict | F | 31.1 / 52.1 / 66.6 | 34.1 / 54.9 / 69.5 |
 80  | strict | F_int | 30.9 / 51.5 / 66.2 | 34.2 / 54.7 / 69.0 |
 81  | adjacent | A | 15.1 / 30.3 / 45.4 | 15.1 / 30.2 / 45.3 |
 82  | adjacent | B | 32.0 / 54.1 / 67.6 | 33.8 / 55.0 / 68.5 |
 83  | adjacent | C | 28.6 / 51.0 / 59.8 | 29.1 / 51.6 / 60.3 |
 84  | adjacent | D | 32.1 / 53.8 / 68.5 | 32.6 / 54.6 / 69.0 |
 85  | adjacent | E | 29.0 / 52.4 / 65.5 | 30.2 / 53.0 / 65.8 |
 86  | adjacent | F | 32.7 / 54.9 / 68.8 | 35.1 / 57.1 / 71.0 |
 87  | adjacent | F_int | 32.6 / 54.7 / 68.8 | 35.3 / 57.0 / 71.0 |
 88  | k-fold | A | 15.0 / 30.1 / 45.1 | 15.1 / 30.2 / 45.3 |
 89  | k-fold | B | 31.5 / 54.0 / 68.2 | 33.4 / 55.4 / 68.9 |
 90  | k-fold | C | 28.1 / 50.5 / 59.1 | 28.9 / 51.8 / 60.2 |
 91  | k-fold | D | 31.4 / 53.3 / 68.0 | 32.0 / 54.6 / 69.3 |
 92  | k-fold | E | 28.5 / 51.8 / 64.6 | 30.0 / 53.0 / 65.4 |
 93  | k-fold | F | 32.6 / 54.8 / 69.5 | 35.0 / 57.0 / 71.4 |
 94  | k-fold | F_int | 32.4 / 54.3 / 69.4 | 35.2 / 56.9 / 71.2 |
 95  
 96  Test accounts per fallback level, %. B: persona / family x locatability / family. D: persona x
 97  bucket / persona / family x locatability / family. The overall level is never used.
 98  
 99  | scheme | B | D |
100  |---|---|---|
101  | strict | 92.5 / 6.8 / 0.8 | 71.2 / 21.2 / 6.8 / 0.8 |
102  | adjacent | 94.2 / 5.2 / 0.6 | 79.4 / 14.9 / 5.2 / 0.6 |
103  | k-fold | 96.6 / 3.0 / 0.4 | 89.1 / 7.4 / 3.0 / 0.4 |
104  
105  ### Table 2 — tiers, out-of-sample
106  
107  Fixed cut-offs: in_house >= 1,250, early_exit < 175 AED collected per account over 3 months. Mean
108  [min-max] over folds.
109  
110  **Table 2a — size and outcome**
111  
112  | scheme | tier | share of accounts % | paid % | collected/acct | recovery % |
113  |---|---|---|---|---|---|
114  | strict | in_house | 16.2 [14.2-18.2] | 53.0 [52.6-53.5] | 1695 [1692-1698] | 9.43 [9.41-9.44] |
115  | strict | agency | 50.5 [49.3-51.8] | 17.2 [16.0-18.5] | 610 [549-671] | 2.92 [2.60-3.24] |
116  | strict | early_exit | 33.2 [32.5-34.0] | 4.5 [4.5-4.6] | 151 [149-153] | 0.68 [0.66-0.70] |
117  | adjacent | in_house | 16.8 [15.1-19.8] | 55.4 [52.7-57.2] | 1762 [1748-1793] | 9.96 [9.79-10.27] |
118  | adjacent | agency | 51.5 [48.8-55.5] | 16.5 [15.5-17.1] | 547 [476-596] | 2.68 [2.40-2.87] |
119  | adjacent | early_exit | 31.8 [29.4-34.6] | 3.9 [3.8-4.0] | 122 [104-143] | 0.55 [0.50-0.63] |
120  | k-fold | in_house | 17.1 [16.2-17.5] | 56.5 [55.5-57.4] | 1772 [1724-1806] | 9.97 [9.67-10.13] |
121  | k-fold | agency | 54.4 [51.2-57.4] | 16.3 [15.6-17.2] | 537 [516-576] | 2.66 [2.53-2.81] |
122  | k-fold | early_exit | 28.6 [25.2-32.7] | 3.5 [3.1-4.3] | 123 [80-175] | 0.56 [0.36-0.80] |
123  
124  **Table 2b — share of payers and of money**
125  
126  | scheme | tier | payers % | money % |
127  |---|---|---|---|
128  | strict | in_house | 45.6 [40.3-50.9] | 43.4 [37.6-49.1] |
129  | strict | agency | 46.4 [41.2-51.5] | 48.7 [43.0-54.4] |
130  | strict | early_exit | 8.0 [7.8-8.2] | 7.9 [7.9-7.9] |
131  | adjacent | in_house | 48.7 [42.7-55.5] | 48.0 [42.3-56.6] |
132  | adjacent | agency | 44.8 [38.4-51.0] | 45.7 [38.0-51.8] |
133  | adjacent | early_exit | 6.4 [6.1-6.9] | 6.2 [5.4-7.1] |
134  | k-fold | in_house | 49.4 [48.6-49.8] | 48.0 [46.7-49.1] |
135  | k-fold | agency | 45.4 [43.8-46.3] | 46.4 [42.8-48.3] |
136  | k-fold | early_exit | 5.2 [4.2-6.7] | 5.6 [3.4-8.1] |
137  
138  Fixed cut-offs on unseen data (all 11 test folds): order in_house > agency > early_exit holds in 11;
139  in_house >= 1,250 holds in 11; agency in band holds in 11; early_exit < 175 holds in 10.
140  
141  Tier stability, month m to m+1, adjacent scheme (3 pairs, mean [min-max], % of accounts present in
142  both months):
143  
144  | measure | % (mean [min-max]) |
145  |---|---|
146  | persona changed | 52.9 [52.4-53.4] |
147  | tier changed | 24.6 [22.8-28.1] |
148  | tier changed, persona same | 5.7 [3.2-9.3] |
149  | tier changed, persona changed | 41.5 [39.1-44.5] |
150  | tier changes with persona same (table moved) | 10.4 [6.7-15.4] |
151  
152  ## Loans (rl_60_180)
153  
154  Cohorts (accounts in 61-180 DPD, 12,512 account-months, 5,416 distinct accounts):
155  
156  | cohort | accounts | paid % | rolled % | collected/acct | recovery % | personas | personas 30+ |
157  |---|---|---|---|---|---|---|---|
158  | 2026-01 | 2,324 | 33.0 | 80.5 | 3,117 | 2.75 | 213 | 17 |
159  | 2026-02 | 2,213 | 29.2 | 84.6 | 2,997 | 2.63 | 202 | 18 |
160  | 2026-03 | 2,218 | 31.9 | 83.9 | 3,340 | 2.89 | 212 | 16 |
161  | 2026-04 | 2,661 | 34.1 | 81.7 | 3,746 | 3.3 | 222 | 21 |
162  | 2026-05 | 3,096 | 36.6 | 78.7 | 3,637 | 3.28 | 215 | 28 |
163  
164  ### Table 1a — AUC, out-of-sample vs in-sample
165  
166  Mean [min-max] over folds. In-sample = the training data scored on itself. Views: A bucket, B
167  persona, C 3 tiers, D persona x bucket, E tiers x bucket, F logistic, F_int logistic + family x
168  locatability. Folds: strict 2, adjacent 4, k-fold 5.
169  
170  | scheme | view | AUC paid OOS | paid in-sample | AUC rolled OOS | rolled in-sample |
171  |---|---|---|---|---|---|
172  | strict | A | 0.617 [0.611-0.624] | 0.635 | 0.620 [0.609-0.632] | 0.634 |
173  | strict | B | 0.730 [0.712-0.747] | 0.805 | 0.712 [0.697-0.728] | 0.795 |
174  | strict | C | 0.667 [0.665-0.669] | 0.726 | 0.654 [0.652-0.655] | 0.706 |
175  | strict | D | 0.731 [0.715-0.747] | 0.807 | 0.712 [0.697-0.727] | 0.796 |
176  | strict | E | 0.705 [0.702-0.707] | 0.769 | 0.695 [0.693-0.696] | 0.753 |
177  | strict | F | 0.761 [0.741-0.780] | 0.816 | 0.746 [0.730-0.762] | 0.805 |
178  | strict | F_int | 0.759 [0.739-0.778] | 0.824 | 0.746 [0.732-0.759] | 0.815 |
179  | adjacent | A | 0.619 [0.611-0.624] | 0.631 | 0.625 [0.609-0.632] | 0.633 |
180  | adjacent | B | 0.755 [0.717-0.779] | 0.800 | 0.736 [0.702-0.770] | 0.788 |
181  | adjacent | C | 0.677 [0.635-0.707] | 0.713 | 0.659 [0.617-0.684] | 0.695 |
182  | adjacent | D | 0.756 [0.720-0.780] | 0.802 | 0.737 [0.707-0.768] | 0.792 |
183  | adjacent | E | 0.720 [0.675-0.741] | 0.759 | 0.706 [0.663-0.730] | 0.745 |
184  | adjacent | F | 0.780 [0.745-0.797] | 0.809 | 0.765 [0.734-0.793] | 0.798 |
185  | adjacent | F_int | 0.779 [0.745-0.797] | 0.815 | 0.766 [0.736-0.793] | 0.805 |
186  | k-fold | A | 0.624 [0.602-0.636] | 0.624 | 0.627 [0.610-0.648] | 0.627 |
187  | k-fold | B | 0.765 [0.746-0.779] | 0.775 | 0.748 [0.730-0.765] | 0.763 |
188  | k-fold | C | 0.670 [0.644-0.683] | 0.674 | 0.652 [0.635-0.667] | 0.660 |
189  | k-fold | D | 0.767 [0.748-0.781] | 0.782 | 0.748 [0.732-0.761] | 0.770 |
190  | k-fold | E | 0.715 [0.699-0.725] | 0.719 | 0.700 [0.686-0.719] | 0.709 |
191  | k-fold | F | 0.784 [0.775-0.791] | 0.787 | 0.770 [0.762-0.779] | 0.773 |
192  | k-fold | F_int | 0.785 [0.777-0.792] | 0.790 | 0.771 [0.766-0.781] | 0.779 |
193  
194  ### Table 1b — capture in the top 10 / 20 / 30 % of test accounts
195  
196  Mean % of AED collected (money) and of payers captured by the top 10 / 20 / 30 % of test accounts
197  ranked by each view (random = 10 / 20 / 30).
198  
199  | scheme | view | money top 10 / 20 / 30 | payers top 10 / 20 / 30 |
200  |---|---|---|---|
201  | strict | A | 11.7 / 23.4 / 35.0 | 12.8 / 25.5 / 38.2 |
202  | strict | B | 16.8 / 28.9 / 44.5 | 20.2 / 33.6 / 46.8 |
203  | strict | C | 14.9 / 27.4 / 39.2 | 17.4 / 30.2 / 41.6 |
204  | strict | D | 16.8 / 29.3 / 44.1 | 20.2 / 33.8 / 46.5 |
205  | strict | E | 14.8 / 27.5 / 40.1 | 17.9 / 31.6 / 44.9 |
206  | strict | F | 17.4 / 32.0 / 48.7 | 21.8 / 38.0 / 53.5 |
207  | strict | F_int | 16.7 / 32.0 / 45.7 | 21.6 / 38.2 / 52.5 |
208  | adjacent | A | 12.4 / 24.9 / 37.4 | 13.2 / 26.5 / 39.7 |
209  | adjacent | B | 20.1 / 34.9 / 47.1 | 21.6 / 37.0 / 50.0 |
210  | adjacent | C | 19.1 / 31.3 / 42.0 | 20.0 / 32.5 / 43.5 |
211  | adjacent | D | 20.1 / 34.6 / 47.3 | 21.6 / 37.7 / 50.3 |
212  | adjacent | E | 19.5 / 32.6 / 45.2 | 20.3 / 34.5 / 48.2 |
213  | adjacent | F | 18.8 / 36.4 / 49.8 | 23.1 / 40.9 / 56.0 |
214  | adjacent | F_int | 19.0 / 36.8 / 49.0 | 22.9 / 41.4 / 55.8 |
215  | k-fold | A | 12.5 / 25.0 / 37.5 | 13.3 / 26.6 / 39.9 |
216  | k-fold | B | 19.2 / 36.6 / 50.5 | 19.1 / 36.7 / 51.4 |
217  | k-fold | C | 18.3 / 31.0 / 41.6 | 19.0 / 31.8 / 42.5 |
218  | k-fold | D | 18.4 / 35.1 / 49.6 | 18.7 / 35.5 / 50.7 |
219  | k-fold | E | 18.3 / 32.5 / 44.9 | 19.1 / 33.6 / 46.6 |
220  | k-fold | F | 19.1 / 36.4 / 50.4 | 23.0 / 41.0 / 56.5 |
221  | k-fold | F_int | 19.5 / 36.8 / 49.7 | 23.2 / 41.3 / 56.2 |
222  
223  Test accounts per fallback level, %. B: persona / family x locatability / family. D: persona x
224  bucket / persona / family x locatability / family. The overall level is never used.
225  
226  | scheme | B | D |
227  |---|---|---|
228  | strict | 48.0 / 47.5 / 4.5 | 16.6 / 31.4 / 47.5 / 4.5 |
229  | adjacent | 62.2 / 34.4 / 3.4 | 28.0 / 34.1 / 34.4 / 3.4 |
230  | k-fold | 78.1 / 20.2 / 1.7 | 45.8 / 32.3 / 20.2 / 1.7 |
231  
232  ### Table 2 — tiers, out-of-sample
233  
234  Fixed cut-offs: in_house >= 6,000, early_exit < 1,350 AED collected per account over 3 months. Mean
235  [min-max] over folds.
236  
237  **Table 2a — size and outcome**
238  
239  | scheme | tier | share of accounts % | paid % | collected/acct | recovery % |
240  |---|---|---|---|---|---|
241  | strict | in_house | 11.6 [7.8-15.4] | 65.0 [56.5-73.6] | 5689 [5248-6130] | 6.56 [5.14-7.98] |
242  | strict | agency | 59.5 [59.1-60.0] | 40.2 [38.0-42.4] | 4367 [4364-4370] | 4.13 [4.05-4.22] |
243  | strict | early_exit | 28.9 [25.6-32.1] | 14.2 [11.6-16.8] | 1538 [1414-1662] | 1.16 [1.06-1.25] |
244  | adjacent | in_house | 11.8 [10.1-15.5] | 65.7 [56.7-74.1] | 6521 [5736-7345] | 7.41 [5.92-8.65] |
245  | adjacent | agency | 61.0 [56.7-67.5] | 36.0 [31.4-38.6] | 3665 [3165-4031] | 3.38 [2.98-3.69] |
246  | adjacent | early_exit | 27.2 [21.7-33.2] | 12.1 [8.7-16.4] | 1561 [1071-1901] | 1.16 [0.77-1.38] |
247  | k-fold | in_house | 12.5 [10.3-15.1] | 63.1 [57.0-68.5] | 6239 [5273-7574] | 6.67 [5.59-7.80] |
248  | k-fold | agency | 65.7 [62.0-69.2] | 35.6 [31.9-37.7] | 3592 [3456-3883] | 3.30 [2.95-3.63] |
249  | k-fold | early_exit | 21.8 [20.1-23.8] | 9.1 [6.6-10.4] | 1146 [840-1316] | 0.84 [0.58-0.99] |
250  
251  **Table 2b — share of payers and of money**
252  
253  | scheme | tier | payers % | money % |
254  |---|---|---|---|
255  | strict | in_house | 20.6 [15.7-25.5] | 17.4 [13.2-21.5] |
256  | strict | agency | 67.7 [65.8-69.5] | 70.5 [68.8-72.1] |
257  | strict | early_exit | 11.7 [8.7-14.7] | 12.2 [9.6-14.7] |
258  | adjacent | in_house | 23.6 [19.1-30.2] | 22.6 [19.0-29.8] |
259  | adjacent | agency | 66.6 [61.8-71.2] | 65.1 [60.6-71.2] |
260  | adjacent | early_exit | 9.7 [8.0-11.7] | 12.3 [9.7-16.2] |
261  | k-fold | in_house | 23.7 [17.3-27.0] | 23.0 [17.7-32.0] |
262  | k-fold | agency | 70.4 [66.2-77.1] | 69.7 [60.3-74.7] |
263  | k-fold | early_exit | 5.9 [4.4-7.3] | 7.3 [5.6-8.6] |
264  
265  Fixed cut-offs on unseen data (all 11 test folds): order in_house > agency > early_exit holds in 11;
266  in_house >= 6,000 holds in 6; agency in band holds in 11; early_exit < 1,350 holds in 6.
267  
268  Tier stability, month m to m+1, adjacent scheme (3 pairs, mean [min-max], % of accounts present in
269  both months):
270  
271  | measure | % (mean [min-max]) |
272  |---|---|
273  | persona changed | 59.9 [58.0-61.5] |
274  | tier changed | 25.1 [23.2-26.6] |
275  | tier changed, persona same | 16.8 [14.9-20.3] |
276  | tier changed, persona changed | 30.7 [28.4-34.9] |
277  | tier changes with persona same (table moved) | 26.8 [23.9-31.8] |
278  
279  ## Caveats
280  
281  - **Cohort overlap:** an account sits in up to 5 cohort months (cards 74,256 account-months for
282    29,629 accounts; loans 12,512 for 5,416). Rolling folds share accounts across train and test
283    (production-like, not independent), k-fold groups by account but trains on later months than it
284    tests; fold spreads understate uncertainty. Adjacent trains on cohorts whose 3-month outcome is
285    not yet known when the test month is scored (optimistic vs strict).
286  - **Few folds:** strict has 2 folds; 'consistent in every fold' there is weak evidence. Adjacent B
287    AUC falls from Feb to May (cards .838 to .797, loans .780 to .717); with 4 points we cannot say
288    whether it is drift.
289  - **Small personas, mainly loans:** only 16-28 of ~210 loan personas per month have 30+ accounts; in
290    strict only 48 % of loan test accounts use their own persona rate (47.5 % use family x
291    locatability), cards 92 %. The loan persona-table results are largely coarse-cell results, and
292    loan tier counts are small (in_house 224-409 accounts per fold).
293  - **Loan amounts** come from `int_loan_master.total_paid` (month-end snapshots, dated at month end;
294    stabilising amount = one EMI), so `paid` and `collected` carry month-grain noise; cards use daily
295    transactions.
296  - **Cards rolled** has a base rate of 80-84 %, so the rolled AUC is on a very imbalanced outcome;
297    accounts without a bucket at m+3 are excluded from rolled metrics.
298  - Tier cut-offs were set from an earlier in-sample run and are untouched; loan outer tiers fail them
299    out of sample in the direction expected from selecting on training noise. Logistic C = 1.0, not
300    tuned.
301  - Money capture at top 10 % for loans is noisy (kfold B 17-25 %); read differences within the fold
302    spread as ties.
303  
```

## Notes on specific spots

Checks done on the transcribed numbers:
- Cohort accounts sum to the totals: cards 14,664 + 14,576 + 14,455 + 14,671 + 15,890 = 74,256; loans 2,324 + 2,213 + 2,218 + 2,661 + 3,096 = 12,512.
- Fallback-level shares (lines 101-103, 228-230) sum to 100 within 0.1 in every row.
- Tier shares of accounts (2a) sum to 99.9-100.1 in every scheme, for cards and loans. Payer and money shares (2b) sum to 99.9-100.1 in every scheme.
- Verdict vs tables:
  - Cards B vs A paid AUC: .806 / .821 / .825 against .651 / .654 / .654, so +.155 to +.171, matches "+.16-.17" (rounded).
  - D vs B (cards): .816 - .806 = .010, .833 - .821 = .012, .839 - .825 = .014, matches.
  - F vs B (cards): +.020, +.018, +.016. F vs B (loans): .761 - .730 = .031, .780 - .755 = .025, .784 - .765 = .019. Matches "+.019-.031".
  - Cards cut-off checks: three cut-off checks times 11 folds = 33. Order holds 11 + 11 (in_house, agency) and early_exit < 175 holds in 10, so 32 of 33. Matches line 20.
  - Loans cut-offs hold in 6 of 11 folds (lines 265-266), as in the verdict.

Flagged spots:
- Line 1 uses an em dash "—" and line 37 etc. use "—" too; the editor font showed them as long dashes. Kept as em dashes.
- Line 207 (loans, strict F_int money top 30) reads `45.7`, while F on line 206 reads `48.7`. The two other F_int cells in that row are within 0.3 of F, so `45.7` may be a misread. It was legible on the photo, so I kept it.
- Line 161: the loans cohort recovery for 2026-04 is `3.3` (no trailing zero), as printed.
- Cohort table `personas 30+` for loans is 16-28 on lines 158-162, which agrees with the caveat on line 289.
- Digit-heavy tables (AUC rows 45-65 and 172-192, capture rows 74-94 and 201-221, tier rows 114-122 and 241-249) were read cell by cell. The most OCR-risk digits are the single-digit AUC differences in the min-max brackets.
- Line 303 is empty and is the last line I can see.
