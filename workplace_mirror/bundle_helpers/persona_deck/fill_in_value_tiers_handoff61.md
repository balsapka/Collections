# Handoff 61: `fill_in_changes.md` (tiers on expected collections), lines 1-345

## Context for Claude Code

- Source: 7 phone photos of VS Code, file `tmp_validation/persona_deck/fill_in_changes.md` (untracked, `U`), dated 2026-11-11, in the dev container `retail.collections.risk_profiling`. Other tabs open: `pipeline_registry.py`, `fill_in.md`.
- This is the change-view companion to the `fill_in.md` in handoff 60. It compares the refresh run (`fill_in.md` at `636095fd`, tiers cut on paid %) with the follow-up run (`fill_in.md` at `abcb1c9a`, tiers cut on expected collections per account).
- Scope of the run: 61-180 only (`cc_60_180`, `rl_60_180`). 180+ was not rerun.
- Photos merged by editor line number. Lines 1-345 are all covered; line 345 is the last line and is empty.
- Format below: `NNN  text`, where NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Continuation lines are indented 2 spaces, as in the editor. Table rows are copied cell by cell.
- Arrows are the real character `→`. The dash before "AUC" and similar is as printed.

## Transcription

```
  1  # fill_in — what changed (tiers on expected collections), 2026-11-11
  2  
  3  This file shows what changed between the refresh run (`fill_in.md` at `636095fd`, tiers cut on paid
  4    %) and the follow-up run (tiers cut on expected collections per account, `fill_in.md` at
  5    `abcb1c9a`). Part 1 lists the changes, part 2 compares old and new numbers side by side, part 3
  6    holds the new sections in full, part 4 is what I reported in the thread (findings, caveats, next
  7    steps). The current `fill_in.md` is the full sheet; this file is the change view only. Scope:
  8    61-180 only (`cc_60_180`, `rl_60_180`); 180+ was not rerun.
  9  
 10  ## 1. What changed
 11  
 12  ### 1a. Definitions and method
 13  - **Tier metric**: was each combination's back-test **paid %** (meaningful payment); now **collected
 14    per account** (AED collected in the 3 months after the back-test month, May 2026, averaged over
 15    the combination's accounts). `recovery_pct` (collected / outstanding principal) and `paid_pct` sit
 16    beside it.
 17  - **Cut-offs** (`TIER_CUTS`): were cards (30, 5) and loans (60, 25) in paid %; now cards (1,250,
 18    175) and loans (6,000, 1,350) in AED per account. In-house from the first, early exit below the
 19    second, agency between. Combinations under 10 back-test accounts stay `unassigned`.
 20  - **How the new cut-offs were chosen** (from the previous run's `combos_ranked`, ranked by collected
 21    per account): in-house at the knee where extra combinations stop adding much money per account
 22    (cards: top 15% of ranked accounts hold 46.6% of the money; loans: top 11.9% hold 31.2%); early
 23    exit where the bottom combinations hold about 5% or less of the money (cards 4.9%, loans 4.7%).
 24    Each cut sits in a gap between two adjacent combinations (cards 1,250 between 1,227 and 1,270; 175
 25    between 172 and 181; loans 6,000 between 5,834 and 6,295; 1,350 between 1,284 and 1,416).
 26  - **Alternatives considered**: cards in-house at 2,000 if capacity is tight (5.0% of accounts, 20.7%
 27    of money; narrow gap 1,962 / 2,006); loans early exit at 1,000 for a smaller exit group (10% of
 28    accounts, 1.7% of money). Not used.
 29  - **Exposure wording**: both `prm_balance.bnp_principal` (cards) and
 30    `int_loan_master.outstanding_balance` (loans) are called **outstanding principal** (was
 31    "billed-not-paid (BNP) principal" and "ENR").
 32  - **Script**: `persona_deck_numbers.py` commits `99d5ddd8`, `b12f6358`. New helper `_values`;
 33    `_with_tier`, `_tier_of`, `_ranked` and the tree rewritten; `TIER_CUTS` refuses to run if unset;
 34    new columns `collected_per_account`, `recovery_pct` in `combos_ranked`, `tier_summary` and `tree`.
 35    Earlier fixes kept (paid_any, call-attempt days, suppression of thin back-test cells).
 36  - **Checked unchanged**: `action`, family outcomes, credibility mix, `uc1_contact` and every table
 37    outside the tier sections are identical to the previous run.
 38  
 39  ### 1b. Lines changed in fill_in.md
 40  - Exposure source section: wording as above plus a line that loan amounts come from `total_paid`.
 41  - Summary: "AED 39.7m BNP principal" → "AED 39.7m outstanding principal" (number unchanged).
 42  - 180+ section: wording only ("BNP principal" / "ENR" → outstanding principal); 180+ numbers
 43    unchanged.
 44  - Tiers, Tree, Risk score, UC1, Pilot: replaced (part 3).
 45  - Outcome check, "By tier" line: now on the new tiers (cards in_house 49.9 vs 51.3 paid-any, agency
 46    16.6 vs 17.7, early_exit 3.9 vs 4.0, unassigned 37.6 vs 37.8; loans 65.2 vs 73.4, 34.0 vs 43.7,
 47    9.7 vs 16.6, 52.7 vs 61.4).
 48  - Notes and Next steps rewritten (part 4).
 49  
 50  ## 2. Old vs new, side by side (61-180)
 51  
 52  ### 2a. Tier sizes (Aug accounts, % of all)
 53  | tier | cards old | cards new | loans old | loans new |
 54  |---|---|---|---|---|
 55  | in_house | 13.7 | 10.8 | 8.9 | 8.0 |
 56  | agency | 60.1 | 54.1 | 32.8 | 53.9 |
 57  | early_exit | 23.4 | 32.4 | 39.9 | 19.8 |
 58  | unassigned | 2.7 | 2.7 | 18.4 | 18.4 |
 59  
 60  ### 2b. What each tier delivers (May back-test)
 61  | tier | paid % old → new | % of payers old → new | % of money old → new |
 62  |---|---|---|---|
 63  | Cards in_house | 48.8 → 49.9 | 49.3 → 39.2 | 46.2 → 43.9 |
 64  | Cards agency | 13.1 → 16.6 | 42.0 → 49.1 | 45.1 → 45.8 |
 65  | Cards early_exit | 2.7 → 3.9 | 2.7 → 5.7 | 2.9 → 4.6 |
 66  | Cards unassigned | 37.6 → 37.6 | 5.9 → 5.9 | 5.7 → 5.7 |
 67  | Loans in_house | 73.1 → 65.2 | 22.3 → 17.6 | 22.3 → 24.4 |
 68  | Loans agency | 38.6 → 34.0 | 39.0 → 53.9 | 38.9 → 50.2 |
 69  | Loans early_exit | 14.9 → 9.7 | 14.1 → 4.0 | 17.0 → 3.6 |
 70  | Loans unassigned | 52.7 → 52.7 | 24.5 → 24.5 | 21.7 → 21.7 |
 71  
 72  The early-exit group now holds about the same small slice of money (cards 4.6%, loans 3.6%) but
 73    cards early exit is larger and loans early exit is much smaller: the loan accounts that rarely pay
 74    but collect real money per account moved up to agency.
 75  
 76  ### 2c. Who changed tier (ranked accounts only = combinations with ≥10 back-test accounts)
 77  Cards: 3,155 of 15,424 ranked accounts (20.5%), 48 combinations. Rows = old tier, columns = new
 78    tier.
 79  | old \ new | in_house | agency | early_exit |
 80  |---|---|---|---|
 81  | in_house | 2,070 | 907 | 0 |
 82  | agency | 250 | 7,507 | 1,681 |
 83  | early_exit | 0 | 317 | 2,692 |
 84  
 85  Loans: 829 of 2,568 ranked accounts (32.3%), 24 combinations.
 86  | old \ new | in_house | agency | early_exit |
 87  |---|---|---|---|
 88  | in_house | 212 | 134 | 0 |
 89  | agency | 82 | 1,063 | 0 |
 90  | early_exit | 11 | 602 | 464 |
 91  
 92  ### 2d. Capture curve (top 20% of ranked accounts)
 93  | | old (ranked by paid %) | new (ranked by collected per account) |
 94  |---|---|---|
 95  | cards: money | 50.4% | 55.2% |
 96  | cards: payers | 53.6% | 50.3% |
 97  | loans: money | 38.1% | 44.1% |
 98  | loans: payers | 39.8% | 32.5% |
 99  
100  Ranking on money captures more of the money (cards +4.8 pts, loans +6.0 pts) and slightly fewer
101    payers.
102  
103  ### 2e. Risk score and AUC (in-sample)
104  - Verdict: every tier "yes" overall before and after; the rule does not discriminate.
105  - Tier AUC (paid / rolled): cards 0.747 / 0.752 → 0.735 / 0.744; loans 0.721 / 0.700 → 0.670 /
106    0.659.
107  - Band + tier: cards 0.794 / 0.790 → 0.781 / 0.782; loans 0.754 / 0.736 → 0.707 / 0.699.
108  - Tree leaf, band and band + leaf unchanged (cards 0.770 / 0.650 / 0.809, loans 0.669 / 0.611 /
109    0.726 on paid). The new tiers rank outcomes (paid, rolled) a little less well because they are cut
110    on money.
111  
112  ### 2f. UC1 contact by tier (%)
113  | tier | cards old → new | loans old → new |
114  |---|---|---|
115  | in_house | 94.1 → 89.0 | 75.1 → 85.2 |
116  | agency | 38.3 → 45.3 | 59.3 → 49.7 |
117  | early_exit | 14.2 → 16.1 | 35.0 → 33.0 |
118  | unassigned | 62.4 → 62.4 | 63.1 → 63.1 |
119  
120  ### 2g. Pilot sizing
121  | item | old | new |
122  |---|---|---|
123  | cards n per arm +5 / +10 (agency) | 826 / 232 | 970 / 265 |
124  | cards n per arm +5 / +10 (early_exit) | 309 / 111 | 375 / 127 |
125  | cards n per arm +5 / +10 (in_house) | 1,568 / 389 | 1,565 / 388 |
126  | loans n per arm +5 / +10 (agency) | 1,519 / 385 | 1,455 / 373 |
127  | loans n per arm +5 / +10 (early_exit) | 902 / 250 | 672 / 196 |
128  | loans n per arm +5 / +10 (in_house) | 1,158 / 268 | 1,372 / 328 |
129  | cards 10% early-exit hold-out Jun / Jul / Aug | 318 / 388 / 452 | 470 / 551 / 625 |
130  | loans 10% early-exit hold-out Jun / Jul / Aug | 125 / 143 / 159 | 54 / 63 / 79 |
131  | tiers filling both arms, cards +10 | agency, early_exit, in_house | agency, early_exit, in_house |
132  | tiers filling both arms, loans +10 | early_exit, agency | agency, early_exit |
133  
134  ## 3. The new sections in full (as in fill_in.md)
135  
136  ## Tiers (61-180; cut on expected collections per account, in-sample)
137  Cut-offs (`TIER_CUTS`, AED collected per account in the 3 months after the back-test month; in-house
138    from the first, early exit below the second, agency between): **cards 1,250 / 175, loans 6,000 /
139    1,350.** Chosen from the previous run's `combos_ranked` (ranked by collected per account):
140    in-house where extra combinations stop adding much money per account (cards: top 15% of ranked
141    accounts hold 46.6% of the money; loans: top 11.9% hold 31.2%); early exit where the bottom
142    combinations together hold about 5% or less of the money (cards 4.9%, loans 4.7%); each cut sits
143    in a gap between two adjacent combinations. No cost per in-house account, agency commission or
144    sale price has come from GRR, so these are hypotheses from the data. Combinations under 10
145    back-test accounts are `unassigned`. Share / principal = Aug population; paid, rolled, cured,
146    collected = May back-test; recovery % = collected / outstanding principal; call days = distinct
147    outbound call days over the last 3 months (A2).
148  
149  | tier | share % | principal AED m | collected / account AED | recovery % | paid % | paid-any % |
150    rolled % | collected AED m | % of payers | % of money | call days |
151  |---|---|---|---|---|---|---|---|---|---|---|---|
152  | **Cards** in_house | 10.8 | 39.9 | 1,920 | 9.75 | 49.9 | 51.3 | 51.1 | 4.45 | 39.2 | 43.9 | 11.7 |
153  | agency | 54.1 | 213.2 | 532 | 2.59 | 16.6 | 17.7 | 86.1 | 4.65 | 49.1 | 45.8 | 11.8 |
154  | early_exit | 32.4 | 138.0 | 106 | 0.47 | 3.9 | 4.0 | 96.4 | 0.46 | 5.7 | 4.6 | 10.9 |
155  | unassigned | 2.7 | 9.7 | 1,243 | 6.32 | 37.6 | 37.8 | 64.8 | 0.58 | 5.9 | 5.7 | 10.0 |
156  | **Loans** in_house | 8.0 | 33.3 | 9,008 | 7.93 | 65.2 | 73.4 | 58.0 | 2.75 | 17.6 | 24.4 | 9.3 |
157  | agency | 53.9 | 243.6 | 3,144 | 2.87 | 34.0 | 43.7 | 80.3 | 5.66 | 53.9 | 50.2 | 9.5 |
158  | early_exit | 19.8 | 100.0 | 886 | 0.67 | 9.7 | 16.6 | 96.7 | 0.41 | 4.0 | 3.6 | 10.1 |
159  | unassigned | 18.4 | 72.5 | 4,636 | 4.86 | 52.7 | 61.4 | 68.9 | 2.45 | 24.5 | 21.7 | 8.2 |
160  
161  - Back-test tier sizes (accounts): cards in_house 2,320 / agency 8,731 / early_exit 4,373 /
162    unassigned 466 (of 15,890); loans 305 / 1,799 / 464 / 528 (of 3,096). The Aug mix has drifted
163    since May (cards in_house 14.6% → 10.8%, early_exit 27.5% → 32.4%).
164  - Against the previous paid-%-based tiers (Aug shares): cards in_house 13.7 → 10.8, agency 60.1 →
165    54.1, early_exit 23.4 → 32.4; loans in_house 8.9 → 8.0, agency 32.8 → 53.9, early_exit 39.9 →
166    19.8, unassigned unchanged. 20.5% of ranked card accounts and 32.3% of ranked loan accounts
167    changed tier; on loans, 602 accounts moved from early exit up to agency (low paid %, but real
168    money per account).
169  - Cards: in-house recovers 9.75% of outstanding principal in 3 months against 2.59% for agency and
170    0.47% for early exit; early exit is 32% of accounts, 5.7% of payers and 4.6% of the money.
171  - Loans: recovery 7.93% / 2.87% / 0.67% (in-house / agency / early exit), the same pattern as cards.
172  
173  Who is in each tier (largest family × nuance groups, % of the tier; `tier_composition`; tiers are
174    set per full combination, so one leaf can appear in several tiers):
175  - Cards in_house: curing_now with a credible-or-able customer (36%), cure_history credible-or-able
176    (16%), stopped_suddenly credible-or-able (12%).
177  - Cards agency: stopped_suddenly, not reachable (46%); cure_history, not reachable (32%),
178    stopped_suddenly, neither credible nor able (10%).
179  - Cards early_exit: stopped_suddenly, not reachable (79%); never_paid, not reachable (20%); nothing
180    else of size.
181  - Loans in_house: cure_history credible-or-able (27%), curing_now credible-or-able (22%),
182    cure_history not reachable (17%).
183  - Loans agency: stopped_suddenly not reachable (47%), cure_history not reachable (29%),
184    stopped_suddenly neither (9%).
185  - Loans early_exit: stopped_suddenly not reachable (58%), cure_history not reachable (18%),
186    never_paid not reachable (14%).
187  
188  Capture curve (combinations ranked by collected per account; ranked accounts only = combinations
189    with ≥10 back-test accounts: cards 15,424 of 15,890 accounts, loans 2,568 of 3,096; linear
190    interpolation) · `combos_ranked`
191  
192  | top % of ranked accounts | cards: money | cards: payers | cards: principal | loans: money | loans:
193    payers | loans: principal |
194  |---|---|---|---|---|---|---|
195  | 10% | 35.3 | 31.1 | 8.9 | 27.5 | 18.9 | 10.8 |
196  | 20% | 55.2 | 50.3 | 18.9 | 44.1 | 32.5 | 19.9 |
197  | 30% | 68.2 | 65.2 | 28.8 | 57.5 | 48.0 | 27.8 |
198  | 50% | 85.6 | 83.8 | 48.7 | 76.4 | 69.8 | 46.3 |
199  | 80% | 97.2 | 96.6 | 76.8 | 94.5 | 93.8 | 76.8 |
200  
201  - **Headline:** the top 20% of card accounts, ranked by expected collections, hold about 55% of the
202    money collected and 50% of the payers, with 19% of the outstanding principal (loans: 44% of the
203    money, 33% of the payers, 20% of the principal).
204  - Loan caveats: loan amounts come from `int_loan_master.total_paid` (monthly field that looks
205    inflated vs cards); the loan `unassigned` tier (17.1% of back-test accounts, 21.7% of the money)
206    has no tier, so about a fifth of loan money sits outside the allocation; loan in-house is only 305
207    back-test accounts on many combinations of under 20 accounts, so its membership is unstable.
208  - Noise: 41 of 159 card and 33 of 77 loan combinations have under 20 accounts; ranks at the top and
209    bottom of the curve rest on a handful of accounts (top card combination: 18 accounts at AED 5,624
210    per account).
211  
212  ## Tree (cards, family × nuance leaf: share % / back-test paid % / collected per account AED / tier
213    of the leaf average) · `tree`
214  - stopped_suddenly · not_reachable 50.8 / 7.8 / 269 / agency; neither 6.1 / 21.7 / 763 / agency;
215    credible_or_able 3.5 / 33.5 / 1,278 / in_house
216  - cure_history · not_reachable 19.0 / 16.3 / 607 / agency; credible_or_able 3.4 / 40.3 / 1,523 /
217    in_house; neither 2.7 / 29.9 / 1,065 / agency
218  - never_paid · not_reachable 6.8 / 2.9 / 72 / early_exit; neither 0.5 / 10.9 / 264 / agency;
219    credible_or_able 0.1 / 32.3 / 933 / agency (31 back-test accounts)
220  - curing_now · credible_or_able 4.1 / 68.2 / 2,035 / in_house; not_reachable 2.1 / 43.6 / 1,229 /
221    agency; neither 0.4 / 51.5 / 1,688 / in_house (101 accounts)
222  - unknown · not_reachable 0.3 / 13.4 / 975 / agency (67 accounts); neither and credible_or_able
223    under 10 accounts (suppressed)
224  - The leaf tier is the tier of the leaf's average, so it can differ from the combination-level
225    account tiers above (a leaf at AED 1,229 is agency although some of its combinations are
226    in-house). The largest leaf (stopped_suddenly, not reachable; half of all cards) collects AED 269
227    per account and is agency; its payers sit in agency and early_exit.
228  
229  ## Risk score (61-180; verdict: yes if spread ≥15 pts or AUC ≥0.65; no if spread <5 and AUC <0.58;
230    else maybe) · `score_tier`
231  
232  | tier | accounts (back-test) | paid % | paid spread / AUC (band-only) | rolled spread / AUC |
233    verdict (paid · rolled) |
234  |---|---|---|---|---|---|
235  | Cards in_house | 2,320 | 49.9 | 20.7 / 0.553 | 22.5 / 0.593 | yes · yes |
236  | Cards agency | 8,731 | 16.6 | 18.4 / 0.634 | 12.6 / 0.621 | yes · maybe |
237  | Cards early_exit | 4,373 | 3.9 | 9.6 / 0.754 | 4.9 / 0.637 | yes (AUC) · maybe |
238  | Cards unassigned | 466 | 37.6 | 21.9 / 0.555 | 22.3 / 0.587 | yes · yes |
239  | Loans in_house | 305 | 65.2 | 41.9 / 0.584 | 28.3 / 0.603 | yes · yes |
240  | Loans agency | 1,799 | 34.0 | 20.5 / 0.586 | 16.1 / 0.597 | yes · yes |
241  | Loans early_exit | 464 | 9.7 | 14.5 / 0.629 | 5.6 / 0.656 | maybe · yes (AUC) |
242  | Loans unassigned | 528 | 52.7 | 34.3 / 0.593 | 27.0 / 0.589 | yes · yes |
243  
244  - Verdict **yes overall in every tier** (overall = the stronger of paid and rolled): the rule does
245    not discriminate between tiers; read as "a score is not ruled out", not as proof. Cards
246    early_exit's paid yes rests on AUC 0.754 over a 3.9% base rate; loans in_house (305) is a small
247    cell.
248  
249  AUC comparison, in-sample back-test month (tiers are cut on collections, not on paid; finer
250    partitions inflate AUC) · `score_compare_auc`
251  
252  | ranking | cards paid | cards rolled | loans paid | loans rolled |
253  |---|---|---|---|---|
254  | DPD band alone | 0.650 | 0.647 | 0.611 | 0.609 |
255  | tree leaf | 0.770 | 0.787 | 0.669 | 0.641 |
256  | tier | 0.735 | 0.744 | 0.670 | 0.659 |
257  | band + leaf | 0.809 | 0.811 | 0.726 | 0.697 |
258  | band + tier | 0.781 | 0.782 | 0.707 | 0.699 |
259  
260  - Personas add about +0.08 to +0.14 AUC over DPD band on cards and +0.05 to +0.10 on loans; band +
261    leaf is highest in both. The four collections tiers get within 0.03-0.04 of the 15-leaf tree on
262    cards and match it on loans (paid 0.670 vs 0.669). Not out-of-sample.
263  
264  ## UC1 · right-party contact in the last 3 months · `uc1_contact`, `uc1_by_tier`
265  - UC1 · overall · cards 41.0% (7,910 of 19,292); loans 51.7% (2,060 of 3,985)
266  - UC1 · by tier · cards in_house 89.0% (1,849 / 2,077) / agency 45.3% (4,729 / 10,442) / early_exit
267    16.1% (1,004 / 6,247) / unassigned 62.4% (328 / 526); loans in_house 85.2% (270 / 317) / agency
268    49.7% (1,068 / 2,148) / early_exit 33.0% (260 / 788) / unassigned 63.1% (462 / 732)
269  - UC1 · reading: contact tracks tier because A3 credibility and the tier both use contact history;
270    the early-exit tier is where call-transcript features have least contact to work with (cards
271    16.1%, loans 33.0%).
272  
273  ## Pilot · `tier_volume`; sample size: two-sided α 0.05, 80% power, baseline = tier back-test paid %
274  - Accounts per tier Jun / Jul / Aug 2026 (membership from the May combination values; changes are
275    population changes):
276    - cards in_house 2,337 / 2,143 / 2,077; agency 9,418 / 10,217 / 10,442; early_exit 4,704 / 5,505 /
277      6,247; unassigned 523 / 532 / 526
278    - loans in_house 319 / 297 / 317; agency 2,095 / 2,137 / 2,148; early_exit 542 / 630 / 788;
279      unassigned 558 / 664 / 732
280  
281  | tier | baseline paid % | n per arm at +5 pts | n per arm at +10 pts |
282  |---|---|---|---|
283  | Cards in_house | 49.9 | 1,565 | 388 |
284  | Cards agency | 16.6 | 970 | 265 |
285  | Cards early_exit | 3.9 | 375 | 127 |
286  | Cards unassigned | 37.6 | 1,508 | 383 |
287  | Loans in_house | 65.2 | 1,372 | 328 |
288  | Loans agency | 34.0 | 1,455 | 373 |
289  | Loans early_exit | 9.7 | 672 | 196 |
290  | Loans unassigned | 52.7 | 1,552 | 382 |
291  
292  - Fill both arms in one month (2n ≤ Aug accounts, and ≤ the smallest of Jun/Jul/Aug): cards +5:
293    agency, early_exit; cards +10: agency, early_exit, in_house (776 of 2,077). Loans +5: none (agency
294    closest, 2,910 vs 2,148); loans +10: agency (746) and early_exit (392 of 788; 542 in Jun);
295    in_house (656 vs 317) and unassigned (764 vs 732) do not.
296  - 10% hold-out of early-exit candidates per month (Jun / Jul / Aug): cards 470 / 551 / 625 — above
297    the n per arm needed (375 at +5, 127 at +10); loans 54 / 63 / 79 — well below the 196 needed at
298    +10 pts (at most 0.40×).
299  - Early exit grows every month in both products, so hold-out sizes grow with it. A paid-% effect is
300    the pilot measure here; the tiers are cut on money, so also track collected per account.
301  
302  ## 4. What I reported in the thread
303  
304  ### Key findings
305  - The top 20% of card accounts, ranked by expected collections, hold about 55% of the money
306    collected, 50% of the payers and 19% of the outstanding principal; loans 44% of the money, 33% of
307    the payers.
308  - Recovery of outstanding principal in 3 months: cards in-house 9.75%, agency 2.59%, early exit
309    0.47%; loans 7.93%, 2.87%, 0.67%.
310  - Risk score: yes overall in every tier. The four collections tiers get within 0.03-0.04 AUC of the
311    15-leaf tree on cards and match it on loans (0.670 vs 0.669 on paid). In-sample.
312  - Pilot: card agency, early_exit and (at +10 pts) in_house fill two arms in one month; loans fill
313    agency and early_exit only at +10 pts; the loan 10% early-exit hold-out (54-79 accounts) is far
314    below the 196 per arm needed.
315  - Regression and consistency checks passed: payer and money shares add to 100 within rounding; the
316    tree's family totals match the family shares; nothing outside the tier sections changed (the only
317    difference seen was row order in `tree_x_band`, values identical).
318  
319  ### Caveats
320  - Loan unassigned: 17.1% of loan back-test accounts (18.4% of Aug) sit in combinations under 10
321    accounts and hold 21.7% of the loan money, so about a fifth of loan money has no tier.
322  - Loan amounts come from `int_loan_master.total_paid` (monthly field, looks inflated vs cards): loan
323    AED per account averages 3,432 against 620 for cards. Compare products on recovery %.
324  - Small cells: loan in-house is only 305 back-test accounts; 41 of 159 card and 33 of 77 loan
325    combinations have under 20 accounts, so ranks near the cuts are noisy (top card combination: 18
326    accounts at AED 5,624 per account). The card in-house gap is narrow (1,227 to 1,270).
327  - The tier mix drifts month to month (membership comes from the May combination values), so May
328    baselines are approximate for a pilot cohort.
329  - Tiers, verdicts and AUCs are in-sample. GRR has supplied no cost per in-house account, agency
330    commission or sale price: the cut-offs are data-driven hypotheses.
331  - 180+ results are from the earlier run (paid-%-based tiers; about 84% of card and 95% of loan 180+
332    accounts fell in early exit, so do not use them) and were not rerun; at 180+ the collected amount
333    spans 6-12 months, so these cuts do not apply there. Late-stage 180+ still uses a 7-month window.
334  
335  ### Next steps
336  1. Get cost per in-house account, agency commission and sale price from GRR; re-set the cut-offs so
337    the break-even is in AED per account (recovery % is the figure to compare with a sale price).
338  2. Make the loan money measure trustworthy before the GRR workshop: confirm `total_paid` with the
339    loan-data owners or rebuild loan payments from a transaction source.
340  3. Validate the tiers out-of-sample (fit on one month, score another) before the workshop.
341  4. Hold the 180+ tiers and the 12-month late-stage numbers until persona history reaches back to
342    2025-08 or the 7-month window is accepted; rerun 180+ with collections tiers only after that.
343  5. Pilot design: for loans, a hold-out of early exit much larger than today's 54-79 accounts a month
344    is needed, or accept the +10 pt effect with agency and early_exit only.
345  
```

## Notes on specific spots

Sum checks (all done on the transcribed numbers):
- Tier sizes (2a): cards old 13.7 + 60.1 + 23.4 + 2.7 = 99.9, new 10.8 + 54.1 + 32.4 + 2.7 = 100.0; loans old 100.0, new 100.1 (rounding).
- Back-test accounts: cards 2,320 + 8,731 + 4,373 + 466 = 15,890; loans 305 + 1,799 + 464 + 528 = 3,096. Both tie to lines 162 and 189.
- Tier changes (2c): card matrix sums to 15,424 ranked accounts, with 907 + 250 + 1,681 + 317 = 3,155 moved. Loan matrix sums to 2,568, with 134 + 82 + 11 + 602 = 829 moved. Both tie to the headers.
- Tier table (149-159): cards collected 4.45 + 4.65 + 0.46 + 0.58 = 10.14 (handoff 60 had 10.15). Loans collected 2.75 + 5.66 + 0.41 + 2.45 = 11.27, same as handoff 60. Payer and money shares sum to 99.9-100.0. Card principal sums to 400.8 (handoff 60: 400.7) and loan principal to 449.4 (handoff 60: 449.5), both rounding.
- Line 156-159 payer/money shares for loans agree with the 2b "new" columns, and the card rows agree as well.
- Tree shares: never_paid 6.8 + 0.5 + 0.1 = 7.4, curing_now 4.1 + 2.1 + 0.4 = 6.6, cure_history 19.0 + 3.4 + 2.7 = 25.1, stopped_suddenly 50.8 + 6.1 + 3.5 = 60.4, unknown 0.3. Total 99.8 plus suppressed cells, as in handoff 60.
- Pilot: `2 × n per arm` matches lines 292-295 (776, 2,910, 746, 392, 656, 764). 10% hold-out: 4,704 / 5,505 / 6,247 give 470 / 551 / 625, and 542 / 630 / 788 give 54 / 63 / 79. 79 / 196 = 0.40.
- Capture curve (195-199) matches 2d at 20% (cards 55.2 / 50.3, loans 44.1 / 32.5).

Flagged spots:
- Line 36: the editor font showed `ucl_contact`. I transcribed `uc1_contact` because that is the table name used on line 264. Check the source.
- Line 67: "Loans in_house" has 22.3 in both the old "% of payers" and the old "% of money" columns. Both columns sum to 99.9 across the four loan tiers, so I think this is real, not a duplicated read.
- Line 151: the divider has 12 groups, matching the 12 header columns (header is split over lines 149-150 in the editor).
- Lines 149-150, 192-193, 232-233: the table header is split over two editor lines, so it is not a valid single-line markdown header in the source.
- Line 105: "Tier AUC ... loans 0.721 / 0.700" is the old pair. New pair is `0.670 / 0.659`.
- Line 345: the last line, empty.
- Lines 1-8 name two commits for `fill_in.md`: `636095fd` (refresh run) and `abcb1c9a` (follow-up run). Line 32 names two for `persona_deck_numbers.py`: `99d5ddd8`, `b12f6358`. Handoff 60 had commit `d98510ba` and script `d20ef626`.
- Digits at OCR risk: 0.470 / 0.375 / 0.388 style three-digit counts in the pilot tables (lines 123-130), and the tier AUCs in lines 235-242. All were readable, and the pilot ones also tie to the `2 × n` checks above.
