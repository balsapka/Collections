# Handoff 69: `a1_bureau_unified/summary.md` (A1 unified bureau salary, DE table check), lines 1-265

> **Correction (user, 2026-11-12):** `salary_credit` is not our own bank's salary credits. It is a
> bureau table of salary history across providers, captured as a look-back when the customer applies
> for a new product with us (hence thin and thinning; it matches internal salary where the salary is
> paid to us). `bureau_salary` is the ad-hoc bulk bureau pull (cross-bank aggregates `_1m`, `_3m`, ...,
> months inferred back by the DE). All three sources are bureau. Section 4's verdict and decision 5
> below are superseded; see spec `specs/A1_ability_family_rule.md`.

## Context for Claude Code

- Source: 5 phone photos of VS Code (LG monitor), file `tmp_validation/a1_bureau_unified/summary.md`, marked `U` (untracked). Other open tab: `pipeline_registry.py`. Dev container `retail.collections.risk_profiling` (cdp-devcontainer:latest).
- Content: results summary of checking the DE's unified bureau salary table (`feat_bureau_salary_unified`, see handoff 66) against today's series (`feat_cif_bureau_salary_monthly`) for all four models. Run on PROD 2026-11-11 with `a1_bureau_unified_snippet.py`. Sections: Headlines, 1 Shape and population, 2 Keys, 3 Cadence, 4 What `salary_credit` is, 5 Coverage against today, 6 Effect on the income family (F1), 7 Quality signal (60_180), What to expect from the swap, Decisions before the bundle, For the DE, Caveats.
- It records the user's decision of 2026-11-11 to KEEP the one-month carry (`signals._with_next_month`, S14) until bureau salary sourcing is fixed. This replaces the recommendation in handoff 66 (carry only `bureau_salary` rows or no carry).
- Photos merged by editor line number: P1 = 1-59; P2 = 57-112; P3 = 107-163; P4 = 161-217; P5 = 212-265. Lines 1-265 are covered. Line 265 is the last line I can see and is empty.
- Format: `NNN  text`, NNN is the editor line number. The file is hard-wrapped, so each editor line is one row. Continuation lines of list items are indented 3 spaces (numbered) or 2 spaces (bullets), as in the editor. Tables are copied as printed (the source cells already have single spaces).

## Transcription

```
  1  # A1 unified bureau salary: summary (cc_60_180, rl_60_180, cc_180_plus, rl_180_plus)
  2  
  3  Source: `results_<model_id>.md` of this folder (PROD run 2026-11-11, snippet `a1_bureau_unified_snippet.py`). No part
  4  failed in any model_id. **Check 0 PASSES in all four** (the rebuilt "today" income level equals
  5  `crx_<p>_a1_ability.a1_income_level` on every row: 0 differ of 93,548 / 16,497 / 318,663 / 55,371), so the old-vs-new
  6  comparison in questions 5-7 is like for like. Latest persona month 2026-08, W = 3 (60_180) / 6 (180+). Base rows are
  7  account x observation month; a cell under 10 is `<10`.
  8  
  9  ## Headlines
 10  
 11  1. **The unified `alert` source is our current bureau series.** In the same month 95-96% of unified alert CIF-months are
 12     in `feat_cif_bureau_salary_monthly` with an amount within 5% in 100% of them, and 99.5-99.7% of our positive months
 13     are in unified alert. So the swap is today's series plus two small additions (`salary_credit`, `bureau_salary`),
 14     minus the carry and the RL loan source.
 15  2. **Coverage goes down, not up.** Salary evidence on the obs base falls in all four models (below), because the unified
 16     side has no carry and the alert series is event-like. What the new sources add is small (0.1-0.9% of rows at the
 17     latest month, 1.1-1.8% in the 60_180 cohorts).
 18  3. **Carry kept (decided).** Removing it would have moved Stable to Weak/None: Stable falls 15.5% -> 11.9% (cc_60_180),
 19     9.3% -> 7.5% (rl_60_180), 6.7% -> 5.4% (cc_180_plus), 3.6% -> 2.8% (rl_180_plus). The cause is the carry, not the 0
 20     rows (see question 6), so it stays for now.
 21  4. **`salary_credit` looks like salary credits at our own bank**, but a partial, thinning feed (question 4).
 22  5. **Join cast: cast the unified long to string.** No leading zeros; both casts match the same CIFs.
 23  6. **Data issues to raise with the DE** (end of file): `salary_credit` rows thin out toward recent months, a jump in
 24     alert 0 rows from 2026-07, `bureau_salary` only exists 2025-09 .. 2026-08, and the table runs to 2026-11 with the
 25     last month partial.
 26  
 27  ## 1. Shape and population  - verdict: clean structure; a fresh-looking table with three source-level anomalies
 28  
 29  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
 30  |---|---|---|---|---|
 31  | rows | 1,191,425 | 756,853 | 1,517,783 | 500,428 |
 32  | distinct CIFs | 58,648 | 21,955 | 102,684 | 16,392 |
 33  | month range | 2020-07 .. 2026-11 (77 months), all four | | | |
 34  | rows/month (min/med/max) | 84 / 15,196 / 30,677 | 87 / 9,967 / 17,527 | 84 / 18,208 / 56,118 | 63 / 6,332 / 12,401 |
 35  | duplicate (cif, month) rows | 0 | 0 | 0 | 0 |
 36  | not a month end | 0 | 0 | 0 | 0 |
 37  | NULL amount | 332,741 | 280,268 | see file | see file |
 38  | amount = 0 | 9.5% | 5.7% | 20.7% | 6.8% |
 39  | rows by source (alert / credit / pull) | 40 / 59 / 0.6% | 18 / 82 / 0.3% | 66 / 34 / 0.1% | 22 / 78 / 0.1% |
 40  | CIFs by source | 51.7k / 16.9k / 817 | 15.2k / 14.5k / 242 | 97.6k / 12.9k / 103 | 11.8k / 9.5k / 51 |
 41  | 0 rows % (alert/credit/pull) | 21.8/1.0/29.3 | 25.6/1.2/30.4 | 30.6/1.0/28.2 | 26.9/0.9/32.9 |
 42  
 43  - Amounts are never negative and cif/month/source are never NULL; **NULL amounts exist** (the DE note said 0 is kept
 44    over NULL; NULL still appears: 332,741 cc_60_180 rows). The engine treats NULL as no evidence, so harmless, but not
 45    what the handover said.
 46  - Quantiles of positive amounts (cc_60_180, all months, AED, p5 / p50 / p95): alert 2,133 / 6,853 / 31,490;
 47    salary_credit 3,000 / 8,330 / 40,000; bureau_salary 1,250 / 7,260 / 30,155. The other models are alike (rl_60_180
 48    alert p50 11,613).
 49  - **Freshness**: the table runs to 2026-11, three months past the persona month. Months up to 2026-10 look complete;
 50    **2026-11 is partial** (cc_60_180 7,281 rows = 54% of the mean of the 3 months before; all four 52-60%).
 51    `salary_credit` is much thinner. The bureau node must cap the series at the persona months.
 52  - Anomalies, same in all four models (cc_60_180 numbers):
 53    - `salary_credit` rows fall every month: 5,557 (2025-06) -> 4,818 (2025-08) -> 2,831 (2026-01) -> 781 (2026-08) -> 76
 54      (2026-11), while alert stays flat at ~10-13k. The newest months, which A1 reads, are the thinnest.
 55    - Alert 0 rows jump from 4.8-17% of alert rows (2026-01 .. 2026-06) to 32-35% from 2026-07 (cc_60_180; rl_60_180
 56      27-32%).
 57    - `bureau_salary` has ~600 rows a month from 2025-09 to 2026-08 and **none before or after** (cc_60_180).
 58  
 59  ## 2. Keys  - verdict: cast the unified long to string
 60  
 61  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
 62  |---|---|---|---|---|
 63  | distinct obs-base CIFs | 42,508 | 7,832 | 305,260 | 53,591 |
 64  | matched, `cast(long as string)` (A) | 71.9% | 89.5% | 31.2% | 25.1% |
 65  | matched, ours cast to long (B) | 71.9% | 89.5% | 31.2% | 25.1% |
 66  | A only / B only | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
 67  | leading-zero strings | 0 | 0 | <10 | 0 |
 68  | non-digit strings | 39 | 0 | 145 | 0 |
 69  | 19+ digit strings | 0 | 0 | <10 | 0 |
 70  
 71  A and B match the identical CIFs in all four, there is no whitespace, and the few non-digit CIFs match under neither.
 72  **Join on the string: `cast(cif_id as string)` on the unified side** (keeps A1's string types, no guard needed). The
 73  unmatched CIFs are CIFs with no unified row (the table is scoped to spine CIFs and A1 reads salary only for the base),
 74  not a key problem: the 180+ obs bases are 3x larger than the unified CIF set.
 75  
 76  ## 3. Cadence  - verdict: event-like, not a monthly series (except a minority); 0 rows mark a stopped salary
 77  
 78  Last 12 months to 2026-08, CIFs with a positive value:
 79  
 80  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
 81  |---|---|---|---|---|
 82  | CIFs with any positive (any source) | 34,239 | 10,370 | 47,447 | 6,781 |
 83  | 1 positive month | 20.2% | 18.3% | 20.0% | 20.5% |
 84  | 10-12 positive months: any | 6.2% | 10.1% | 4.2% | 7.7% |
 85  | ... alert | 2.4% | 2.8% | 3.0% | 3.2% |
 86  | ... salary_credit | 10.6% | 9.0% | 13.0% | 9.7% |
 87  | ... bureau_salary | 28.4% | 23.9% | 25.8% | 31.0% |
 88  | longest gap 0 (single month or none): any | 41.1% | 46.6% | 35.5% | 40.9% |
 89  | longest gap 3+ months: any | 26.9% | 22.4% | 30.4% | 25.9% |
 90  
 91  - Alert is the least monthly (57% of its CIFs have 1-3 positive months in 12; alerts fire on a change). `salary_credit`
 92    and the `bureau_salary` pulls are more regular but still mostly well short of 10-12 months, and a third of
 93    `bureau_salary` CIFs have a gap of 2+ months. No source is a monthly series for most CIFs.
 94  - **0 rows** (cc_60_180, last 12 months: 24,464): 69% sit after the CIF's last positive month (salary stopped), 17%
 95    between positive months in a longer hole, 6% isolated (positive before and after), 6% CIFs that were never positive,
 96    1% at the start. Alert: 72% after the last positive. The other models are within a few points (rl_60_180 alert 70%,
 97    cc_180_plus 69%, rl_180_plus 68%). Only 22% of cc_60_180 0 rows follow a positive previous month. So a 0 is mostly
 98    "this salary has stopped", with a minority of holes.
 99  
100  ## 4. What `salary_credit` is  - verdict: our own bank's salary credits (same amounts), but a different and thinner feed
101  
102  `salary_credit` against our internal salary, positive CIF-months in the last 12 months:
103  
104  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
105  |---|---|---|---|---|
106  | positive salary_credit CIF-months | 17,751 | 16,393 | 7,377 | 5,171 |
107  | internal also positive, same month | 61.6% | 65.0% | 40.8% | 51.0% |
108  | ... amount within 5% | 94.9% | 95.1% | 95.6% | 95.9% |
109  | ... 5-25% | 1.5% | 1.4% | 1.1% | 0.8% |
110  | ... > 25% | 3.5% | 3.6% | 3.3% | 3.3% |
111  | internal positive months that are in salary_credit | 27.5% | 38.6% | 23.9% | 32.9% |
112  | internal positive months in any unified source | 32.8% | 42.8% | 28.6% | 36.8% |
113  
114  The same test for the other sources: **alert vs internal** agrees in the same month in only 0.2-1.7% of alert months and
115  within 5% in 9-12% of those (it is not our salary credit); **bureau_salary vs internal** overlaps 24-46% of months with
116  within-5% in 33-40% (a rough match, like a different employer record or a lagged pull). **Alert vs our current bureau
117  series**: 95-96% / 100% (above). `salary_credit` and `bureau_salary` overlap our current series in <10 CIF-months.
118  
119  Reading: where `salary_credit` and our internal salary both exist, they are the same number in 95% of months, which no
120  bureau view of salary at any bank would give; so it is our own salary credits. But it is not a copy: only a quarter to a
121  third of our internal salary months appear in it, and 35-60% of its own CIF-months have no positive internal salary (a
122  different CIF-level definition or look-back, or a feed that only covers part of the base; the thinning in question 1
123  points at the second). For A1 this means it adds internal-like evidence without an internal row only where the feed has
124  it, and mostly in older months.
125  
126  ## 5. Coverage against today  - verdict: a small loss everywhere; the gain from the new sources is 0.1-0.9% of rows
127  
128  Latest persona month, rows with salary evidence (a month >= AED 1,000 in W):
129  
130  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
131  |---|---|---|---|---|
132  | base rows | 19,292 | 3,985 | 318,663 | 55,371 |
133  | today: internal or current bureau | 25.8% | 18.8% | 9.9% | 5.9% |
134  | after the swap: internal or unified | 22.6% | 17.5% | 9.4% | 5.7% |
135  | no internal salary evidence | 97.7% | 94.9% | 99.8% | 99.7% |
136  | ... **gain** a salary (unified yes, current no) | 164 (0.9%) | 35 (0.9%) | 356 (0.1%) | 71 (0.1%) |
137  | ... **lose** a salary (current yes, unified no) | 780 (4.1%) | 89 (2.4%) | 1,799 (0.6%) | 181 (0.3%) |
138  | of rows with no evidence today, gain | 1.1% | 1.1% | 0.1% | 0.1% |
139  | unified evidence from alert only | 94.8% | 83.3% | 98.6% | 94.1% |
140  | ... salary_credit only | 2.5% | 8.5% | 0.5% | 1.7% |
141  | ... bureau_salary only | 1.2% | 2.2% | 0.1% | <10 |
142  
143  2x2, cc_60_180 latest month: current yes / unified yes 3,793; current yes / unified no 784; current no / unified yes
144  240; neither 14,475. rl_60_180: 478 / 89 / 62 / 3,356. Jan-May 2026 cohort (60_180): cc_60_180 evidence 30.1% -> 27.6%
145  (gain 781, lose 2,652 of 72,137 rows without internal); rl_60_180 22.5% -> 22.2% (gain 226, lose 262 of 11,978). RL is
146  nearly neutral in the cohort, CC loses 2.5pp. A "lost" row has evidence today only through the carry (or, for RL, the
147  loan source); the numbers do not separate the two.
148  
149  ## 6. Effect on the income family (F1)  - verdict: Stable shrinks 0.8-3.6pp, almost all to Weak; the cause is the carry
150  
151  `a1_income_level`, latest month, old -> new:
152  
153  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
154  |---|---|---|---|---|
155  | Stable | 15.5% -> 11.9% | 9.3% -> 7.5% | 6.7% -> 5.4% | 3.6% -> 2.8% |
156  | Weak | 10.3% -> 10.7% | 9.5% -> 10.0% | 3.2% -> 4.0% | 2.3% -> 2.9% |
157  | None | 74.2% -> 77.4% | 81.2% -> 82.5% | 90.1% -> 90.6% | 94.1% -> 94.3% |
158  | Stable -> Weak | 630 (3.3%) | 85 (2.1%) | 4,842 (1.5%) | 534 (1.0%) |
159  | Stable -> None | 265 (1.4%) | 25 (0.6%) | 351 (0.1%) | 37 (0.1%) |
160  | Weak -> None | 515 (2.7%) | 64 (1.6%) | 1,448 (0.5%) | 144 (0.3%) |
161  | Weak -> Stable | 125 (0.6%) | 19 (0.5%) | 1,070 (0.3%) | 112 (0.2%) |
162  | None -> Weak or Stable | 164 (0.9%) | 35 (0.9%) | 356 (0.1%) | 71 (0.1%) |
163  
164  Bureau-only windows (no internal salary in either window, bureau evidence under either series):
165  
166  | | cc_60_180 | rl_60_180 | cc_180_plus | rl_180_plus |
167  |---|---|---|---|---|
168  | windows | 4,271 | 452 | 30,573 | 2,994 |
169  | stable-floor total reached, today -> unified | 77.1% -> 58.5% | 70.6% -> 57.7% | 81.6% -> 66.6% | 73.9% -> 58.9% |
170  | with a 0 month in 2W, today -> unified | 24.2% -> 32.5% | 25.4% -> 28.1% | 36.6% -> 31.2% | 39.5% -> 31.5% |
171  | S12 `hold` true -> false (unified weakens) | 453 (10.6%) | 45 (10.0%) | 2,518 (8.2%) | 254 (8.5%) |
172  | S12 `hold` false -> true (unified holds) | 311 (7.3%) | 28 (6.2%) | 1,766 (5.8%) | 190 (6.3%) |
173  | total passes but S12 blocks Stable, today -> unified | 729 -> 549 | 53 -> 55 | 4,471 -> 3,764 | 380 -> 329 |
174  | of the flips, S12 decides Stable (weakens / holds) | 175 / 121 | 23 / 11 | 1,382 / 1,051 | 126 / 101 |
175  
176  - **Two corrections to the working assumption**: (a) today's series already has real 0 months (24-40% of bureau-only
177    windows), and the unified series has about as many (28-33%); it does not add 0s where there were none. (b) The S12
178    test flips both ways with a small net (cc_60_180 453 weaker vs 311 holding; S12 blocks fewer Stable windows under the
179    unified series than today). **S12 is not the problem.**
180  - The drop is in the first test: the share of bureau-only windows whose W total reaches the stable floor falls 15-19pp
181    in every model. That is the carry: without it, an alert that fires in one month of W counts once, not in two months.
182  
183  ## 7. Quality signal (60_180)  - verdict: unified-only Stable cures like Moderate
184  
185  `cure_3` / `pay_any_3` over the Jan-May 2026 cohort (bucket 4-7), with the new income level:
186  
187  | income source x new level | cc_60_180 rows | cure_3 | pay_any_3 | rl_60_180 rows | cure_3 | pay_any_3 |
188  |---|---|---|---|---|---|---|
189  | internal Stable | 1,268 | 32.8% | 60.6% | 122 | 29.9% (n=107, CI 19-41) | 65.4% |
190  | internal Weak | 851 | 20.6% | 41.2% | 412 | 10.3% | 48.4% |
191  | **unified-only Stable** | 11,544 | **17.0%** | **43.7%** | 1,162 | **15.7%** | **69.0%** |
192  | unified-only Weak | 6,817 | 10.8% | 34.6% | 1,083 | 9.8% | 55.8% |
193  | none | 53,776 | 8.7% | 21.8% | 9,733 | 9.3% | 39.3% |
194  | *today: bureau-only Stable* | 13,717 | 14.8% | 41.1% | 1,336 | 13.4% | 65.8% |
195  | *persisted High / Moderate* | | 34.1 / 16.6 | 54.1 / 42.6 | | n/a / 14.8 | n/a / 63.3 |
196  | *persisted Low / Unknown* | | 11.6 / 8.1 | 32.0 / 19.2 | | 10.3 / 8.8 | 47.3 / 35.3 |
197  
198  - cc_60_180: internal Stable - unified-only Stable = +14.5pp cure [11.1, 17.8], +15.2pp pay_any [11.1, 19.3].
199    Unified-only Stable sits on top of Moderate (16.6%) and far below internal Stable / High (32.8% / 34.1%), as in round
200    3. Unified-only Stable - Weak = +6.3pp cure [5.2, 7.5]; Stable - none = +7.4pp [6.5, 8.4]: the ordering is kept.
201  - rl_60_180: unified-only Stable cures 15.7% against internal Stable 29.9% (+7.9pp, CI -2.8 to 18.7, n=107, not
202    separable) and against Moderate 14.8%; pay_any is high for every bureau group (65-69%), so it adds little there.
203    Unified-only Stable - Weak = +5.8pp cure [2.7, 8.9], +12.7pp pay_any.
204  - The unified-only group is a little better than today's bureau-only (17.0 vs 14.8% cure in CC), which fits a window
205    where only months with an actual alert count.
206  - Not answered: the unified-only group is not split by source, so I cannot say whether `salary_credit`-only Stable cures
207    like internal Stable. It is only 2.5% / 8.5% of unified-evidence rows (cc / rl), so it would need a larger cohort or a
208    source split.
209  
210  ## What to expect from the swap
211  
212  - **Coverage**: a small fall in rows with salary evidence (cc_60_180 25.8% -> 22.6%, rl_60_180 18.8% -> 17.5%,
213    cc_180_plus 9.9% -> 9.4%, rl_180_plus 5.9% -> 5.7%). The new sources add 0.1-0.9% of rows (1.1-1.8% in the 60_180
214    cohorts).
215  - **Income level**: Stable down 0.8-3.6pp (cc_60_180 3.6pp), nearly all to Weak, plus a few Weak -> None; very little
216    moves up. So A1 High/Moderate counts will go down a little in the same direction. The Stable that stays still cures
217    like Moderate (unified-only) or High (internal).
218  - **A1 states**: the bundle's own state change is not measured here (income level only). Expect fewer income-driven
219    Moderates; the rebuild of the whole state with a check-run would give it.
220  
221  ## Decisions before the bundle
222  
223  1. **Carry: DECIDED (user, 2026-11-11) - keep the one-month carry (`signals._with_next_month`, S14) until bureau salary
224     sourcing is fixed.** This replaces the earlier decision to remove it with the swap. Why the data back it: the unified
225     alert source *is* today's series (question 1/4) and is event-like (question 3), and removing the carry is what costs
226     the Stable rows (question 6), not the 0 rows or S12. Consequences: the A1 engine stays as it is, and the swap is only
227     the rebuilt `feat_cif_bureau_salary_monthly` (from the unified table) feeding the same carry. The carry then also
228     applies to `salary_credit` rows (the handover's double-counting concern for monthly sources; those rows are 2.5-8.5%
229     of unified-evidence rows, so small). **Not measured**: coverage and income levels with the carry kept on the unified
230     series; expect about today's figures plus the gains in question 5 (0.1-0.9% of rows), minus nothing from the RL loan
231     source if that stays too. Revisit when the DE fixes the sourcing (the `salary_credit` thinning, the alert 0-row jump,
232     `bureau_salary` gap below).
233  2. **Join cast**: `cast(unified.cif_id as string)`; no `F.last_day` needed (every value is a month end), but harmless.
234  3. **Series cap**: the rebuilt `feat_cif_bureau_salary_monthly` must stop at the persona months: the table has 2026-09
235     .. 2026-11 rows and 2026-11 is partial.
236  4. **RL loan source**: dropping it costs RL 60_180 89 rows (2.4% of rows without internal) at the latest month and is
237     nearly neutral in the cohort (22.5% -> 22.2% with the carry gone too). Acceptable under your decision.
238  5. **`salary_credit` overlap**: it equals our internal salary where both exist, so with income = max(internal, bureau)
239     it does not double count. But it gives "internal-like" evidence under the bureau label; A1's `a1_income_source` will
240     call it `bureau` where there is no internal row. Decide whether to keep that label or map `salary_credit` to
241     `internal` (the data support it, on 2.5-8.5% of unified-evidence rows).
242  6. **NULL amounts**: the table has NULL `monthly_salary` (cc_60_180 332,741 rows) although the DE note says 0 is kept;
243     the engine treats NULL as no evidence, but ask the DE.
244  
245  ## For the DE
246  
247  - `salary_credit` rows fall steadily over the last 14 months (cc_60_180 5.6k -> 0.8k, 76 in 2026-11): lag, back-fill or
248    a changed source?
249  - Alert 0 rows rise from ~10% of alert rows to 32-35% from 2026-07 on (all models): a change in the alert feed or in the
250    0 rule?
251  - `bureau_salary` has rows only for 2025-09 .. 2026-08: was the AECB pull stopped or not loaded?
252  - NULL `monthly_salary` rows although 0 is meant to be kept.
253  - The table runs to 2026-11 with the latest month partial: is a rerun planned, and is the persona cap enough on our
254    side?
255  
256  ## Caveats
257  
258  - Every number is the latest persona month (2026-08) or the Jan-May 2026 cohort of the 60_180 models; 180+ has no
259    outcomes.
260  - "Gain" and "lose" are evidence in W at a month >= AED 1,000, not state changes; the state effect is the F1 table.
261  - The unmatched share in question 2 is rows with no unified row, which is not shown separately from a key problem; A = B
262    and the zero counts say it is not the key.
263  - Question 7 CIs are clustered on the CIF; rl_60_180 internal Stable has n=107, too small to separate from unified-only
264    Stable.
265  
```

## Notes on specific spots

Sum and ratio checks on the transcribed numbers:
- Line 143: cc_60_180 2x2 = 3,793 + 784 + 240 + 14,475 = 19,292 (matches base rows, line 132). rl_60_180: 478 + 89 + 62 + 3,356 = 3,985.
- Line 189-193 (quality table): cc_60_180 rows 1,268 + 851 + 11,544 + 6,817 + 53,776 = 74,256 and rl_60_180 rows 122 + 412 + 1,162 + 1,083 + 9,733 = 12,512. Both equal the Jan-May cohort sizes in handoffs 65 and 68.
- Base rows on line 132 (19,292 / 3,985 / 318,663 / 55,371) match handoffs 60, 67, 68. Line 5's "93,548 / 16,497" are not base rows of the latest month; I copied them as printed.
- Lines 108-110 add to about 100% in each column (94.9 + 1.5 + 3.5 = 99.9; 95.1 + 1.4 + 3.6 = 100.1; 95.6 + 1.1 + 3.3 = 100.0; 95.9 + 0.8 + 3.3 = 100.0).
- Lines 94-95: 69 + 17 + 6 + 6 + 1 = 99.
- Line 171-172 percentages equal count / windows (453 / 4,271 = 10.6%; 311 / 4,271 = 7.3%; 45 / 452 = 10.0%; 28 / 452 = 6.2%; 2,518 / 30,573 = 8.2%; 1,766 / 30,573 = 5.8%; 254 / 2,994 = 8.5%; 190 / 2,994 = 6.3%).
- Lines 158-162 percentages equal count / base rows (630 / 19,292 = 3.3%; 4,842 / 318,663 = 1.5%; 534 / 55,371 = 1.0%).
- Line 5-7 to line 189: the cohort tables and persisted-state rows (lines 195-196) agree with handoff 68 only in cohort size; the persisted High / Moderate / Low / Unknown cure rates were not checked against handoff 68.

Flagged spots (as printed, not corrected):
- Line 66: the row has FIVE `0 / 0` cells against four model columns (the divider on line 62 has five column groups including the label). I copied what I read; check the source, it may be a stray extra cell.
- Lines 136-137 vs 143-144: the table says gain 164 / lose 780 (cc_60_180) and gain 35 (rl_60_180), the 2x2 sentence says current no / unified yes 240 and current yes / unified no 784 (cc), 62 (rl gain) and 89 (rl lose, same as the table). The gain/lose definitions probably differ (the table is restricted to rows with no internal salary evidence); not a transcription slip as far as I can tell.
- Lines 180-181 say the stable-floor share "falls 15-19pp in every model". From line 169: cc 77.1 -> 58.5 = 18.6pp, rl 70.6 -> 57.7 = 12.9pp, cc_180_plus 81.6 -> 66.6 = 15.0pp, rl_180_plus 73.9 -> 58.9 = 15.0pp. The rl_60_180 drop is 12.9pp, outside the quoted range.
- Line 17 / 213: "1.1-1.8% in the 60_180 cohorts". From line 145: 226 / 11,978 = 1.9% for rl_60_180 (cc: 781 / 72,137 = 1.1%).
- Line 189: rl_60_180 internal Stable shows 122 rows but the text says n=107 (lines 189, 201, 263). Presumably 107 is the CIF-clustered or distinct count; not explained in the file.
- Line 239: the editor font rendered `a1_income_source` as `al_income_source` (digit one vs lowercase L). I typed `a1_`, consistent with `a1_income_level` elsewhere.
- Line 233: `F.last_day` as printed.
- Line 27, 59, 76, 100, 126, 149, 183: headings have two spaces before the dash (`## 2. Keys  - verdict`), as printed.
- Line 46-47: `p5 / p50 / p95` quantiles as printed (alert 2,133 / 6,853 / 31,490; salary_credit 3,000 / 8,330 / 40,000; bureau_salary 1,250 / 7,260 / 30,155).
- Line 195-196: `*persisted ...*` rows have empty cells for the row-count columns and `n/a` for rl internal High. Copied as printed.
- Line 223: this is the decision of 2026-11-11 (today), made by the user. It replaces the recommendation in handoff 66, lines 38-43 there (carry only `bureau_salary` rows).
- Line 265 is empty and is the last line I can see. I can't tell whether the file continues.
- Lines 57-59, 107-112, 161-162 and 212-217 each appear in two photos and matched.
